# -*- coding: utf-8 -*-
"""MQTT 3.1.1 — o protocolo que liga sensor, painel e automação.

Falado à mão sobre TCP, como o WebSocket do Kiln: são dezesseis tipos de
pacote, e os cinco que importam cabem num arquivo — CONNECT, PUBLISH,
SUBSCRIBE, PINGREQ e DISCONNECT.

| Decisão | Porque |
|---|---|
| QoS **0 e 1** | o 2 exige guardar estado de quatro mensagens por publicação, e quase nenhum projeto de sensor usa |
| o `keepalive` tem uma thread própria | sem PINGREQ, o broker fecha a conexão no silêncio — e o sintoma é um painel que para de atualizar de madrugada |
| `assinar` recebe uma ação | um laço de leitura que devolve mensagem obrigaria quem chama a girar |
| **sem TLS** | `ssl` da biblioteca padrão resolveria, e a decisão fica para quando houver um teste com certificado de verdade |

O testamento (*last will*) está aqui de propósito: é como o painel
descobre que o sensor caiu. Sem ele, um sensor sem energia fica
"online" para sempre, com o último valor congelado na tela.
"""

import socket
import struct
import threading
import time

from ..errors import RuntimeError_

_DOC = "iot/mqtt"

CONNECT, CONNACK = 1, 2
PUBLISH, PUBACK = 3, 4
SUBSCRIBE, SUBACK = 8, 9
UNSUBSCRIBE, UNSUBACK = 10, 11
PINGREQ, PINGRESP = 12, 13
DISCONNECT = 14

#: O que o byte de retorno do CONNACK quer dizer. Sem esta tabela, a
#: falha chega como "codigo 5" — e 5 é justamente o mais comum de todos.
RECUSAS = {
    1: "o broker nao fala MQTT 3.1.1",
    2: "o identificador do cliente foi recusado",
    3: "o broker esta fora do ar",
    4: "usuario ou senha errados",
    5: "nao autorizado — confira o usuario, a senha e a ACL do topico",
}


def _erro(mensagem, nota="", dica=""):
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


def _tamanho(valor):
    """O comprimento restante, em bytes de sete bits — o do MQTT."""
    saida = bytearray()
    while True:
        byte = valor % 128
        valor //= 128
        if valor:
            byte |= 0x80
        saida.append(byte)
        if not valor:
            return bytes(saida)


def _texto(valor):
    crus = str(valor).encode("utf-8")
    if len(crus) > 65535:
        raise _erro("um texto do MQTT vai ate 65535 bytes.")
    return struct.pack(">H", len(crus)) + crus


class Mqtt:
    """Um cliente MQTT. Publica, assina e responde ao broker."""

    def __init__(self, host="localhost", porta=1883, cliente="", usuario="",
                 senha="", keepalive=60, testamento=None, prazo=10.0):
        self.host = str(host)
        self.porta = int(porta)
        self.cliente = str(cliente) or f"dataforge-{int(time.time() * 1000) % 100000}"
        self.keepalive = int(keepalive)
        self.prazo = float(prazo)
        self._usuario = str(usuario)
        self._senha = str(senha)
        self._testamento = testamento
        self._soquete = None
        self._trava = threading.RLock()
        self._assinaturas = {}      # filtro -> acao
        self._recebidas = []
        self._id = 0
        self._vivo = False
        self._leitor = None
        self._batida = None
        self._conectado = threading.Event()
        self._falha = None

    # ── conectar ─────────────────────────────────────────────

    def conectar(self):
        try:
            self._soquete = socket.create_connection((self.host, self.porta),
                                                     timeout=self.prazo)
        except OSError as erro:
            raise _erro(
                f"nao consegui falar com o broker {self.host}:{self.porta}: {erro}",
                nota="um broker local costuma ser o mosquitto na porta 1883",
                dica="docker run -p 1883:1883 eclipse-mosquitto") from None
        self._soquete.settimeout(0.2)
        self._vivo = True

        bandeiras = 0x02                       # sessao limpa
        corpo = _texto("MQTT") + bytes([4, 0]) + struct.pack(">H", self.keepalive)
        carga = _texto(self.cliente)
        if self._testamento:
            bandeiras |= 0x04
            qos = int(self._testamento.get("qos", 0)) & 0x03
            bandeiras |= qos << 3
            if self._testamento.get("reter"):
                bandeiras |= 0x20
            carga += _texto(self._testamento["topico"])
            carga += _texto(self._testamento.get("mensagem", ""))
        if self._usuario:
            bandeiras |= 0x80
            carga += _texto(self._usuario)
            if self._senha:
                bandeiras |= 0x40
                carga += _texto(self._senha)
        corpo = corpo[:-3] + bytes([4, bandeiras]) + struct.pack(">H", self.keepalive)
        self._mandar(CONNECT, 0, corpo + carga)

        self._leitor = threading.Thread(target=self._ler_sempre, daemon=True,
                                        name="mqtt-leitor")
        self._leitor.start()
        if not self._conectado.wait(self.prazo):
            self.fechar()
            raise _erro(f"o broker {self.host} nao respondeu ao CONNECT.",
                        nota=self._falha or "nenhuma resposta em "
                                            f"{self.prazo:g} s")
        if self._falha:
            motivo = self._falha
            self.fechar()
            raise _erro(f"o broker recusou a conexao: {motivo}")
        self._batida = threading.Thread(target=self._bater, daemon=True,
                                        name="mqtt-keepalive")
        self._batida.start()
        return True

    # ── mandar e receber ─────────────────────────────────────

    def _mandar(self, tipo, bandeiras, corpo):
        cabeca = bytes([(tipo << 4) | bandeiras]) + _tamanho(len(corpo))
        with self._trava:
            if not self._soquete:
                raise _erro("este cliente MQTT ja foi fechado.")
            self._soquete.sendall(cabeca + corpo)

    def _proximo_id(self):
        with self._trava:
            self._id = (self._id % 65535) + 1
            return self._id

    def publicar(self, topico, mensagem, qos=0, reter=False):
        """Publica num tópico. Com `qos := 1`, espera o PUBACK."""
        if not str(topico) or "+" in str(topico) or "#" in str(topico):
            raise _erro(f"'{topico}' nao serve para publicar.",
                        nota="'+' e '#' sao curingas de ASSINATURA",
                        dica='publicar("casa/sala/temperatura", 21.5)')
        corpo = _texto(topico)
        identificador = None
        bandeiras = (int(qos) & 0x03) << 1
        if reter:
            bandeiras |= 0x01
        if int(qos) > 0:
            identificador = self._proximo_id()
            corpo += struct.pack(">H", identificador)
        crus = (mensagem if isinstance(mensagem, (bytes, bytearray))
                else str(mensagem).encode("utf-8"))
        self._mandar(PUBLISH, bandeiras, corpo + crus)
        return identificador or True

    def assinar(self, filtro, acao, qos=0):
        """Chama `acao({topico, mensagem})` a cada mensagem que casar.

        `+` casa um nível (`casa/+/temperatura`), `#` casa o resto
        (`casa/#`) — e só no fim do filtro.
        """
        identificador = self._proximo_id()
        corpo = struct.pack(">H", identificador) + _texto(filtro) + bytes([int(qos) & 3])
        self._mandar(SUBSCRIBE, 0x02, corpo)
        with self._trava:
            self._assinaturas[str(filtro)] = acao
        return identificador

    def cancelar(self, filtro):
        identificador = self._proximo_id()
        self._mandar(UNSUBSCRIBE, 0x02,
                     struct.pack(">H", identificador) + _texto(filtro))
        with self._trava:
            self._assinaturas.pop(str(filtro), None)
        return True

    def recebidas(self):
        """As mensagens que chegaram, na ordem."""
        with self._trava:
            return list(self._recebidas)

    def esperar(self, quantas=1, prazo=5.0):
        """Espera N mensagens chegarem. Devolve as que chegaram."""
        limite = time.monotonic() + float(prazo)
        while time.monotonic() < limite:
            with self._trava:
                if len(self._recebidas) >= int(quantas):
                    return list(self._recebidas)
            time.sleep(0.005)
        return self.recebidas()

    # ── o laço ───────────────────────────────────────────────

    def _ler_sempre(self):
        buffer = bytearray()
        while self._vivo:
            try:
                pedaco = self._soquete.recv(4096)
                if not pedaco:
                    self._vivo = False
                    return
                buffer.extend(pedaco)
            except socket.timeout:
                continue
            except OSError:
                self._vivo = False
                return
            while True:
                quadro = self._extrair(buffer)
                if quadro is None:
                    break
                self._tratar(*quadro)

    @staticmethod
    def _extrair(buffer):
        if len(buffer) < 2:
            return None
        tamanho, deslocamento, multiplicador = 0, 1, 1
        while True:
            if deslocamento >= len(buffer):
                return None
            byte = buffer[deslocamento]
            tamanho += (byte & 0x7F) * multiplicador
            deslocamento += 1
            if not byte & 0x80:
                break
            multiplicador *= 128
        if len(buffer) < deslocamento + tamanho:
            return None
        cabeca = buffer[0]
        corpo = bytes(buffer[deslocamento:deslocamento + tamanho])
        del buffer[:deslocamento + tamanho]
        return cabeca >> 4, cabeca & 0x0F, corpo

    def _tratar(self, tipo, bandeiras, corpo):
        if tipo == CONNACK:
            codigo = corpo[1] if len(corpo) > 1 else 0
            if codigo:
                self._falha = RECUSAS.get(codigo, f"codigo {codigo}")
            self._conectado.set()
        elif tipo == PUBLISH:
            tamanho = struct.unpack(">H", corpo[:2])[0]
            topico = corpo[2:2 + tamanho].decode("utf-8", "replace")
            resto = corpo[2 + tamanho:]
            qos = (bandeiras >> 1) & 0x03
            if qos > 0:
                identificador = struct.unpack(">H", resto[:2])[0]
                resto = resto[2:]
                self._mandar(PUBACK, 0, struct.pack(">H", identificador))
            mensagem = {"topico": topico,
                        "mensagem": resto.decode("utf-8", "replace"),
                        "bytes": resto, "qos": qos,
                        "retida": bool(bandeiras & 0x01)}
            with self._trava:
                self._recebidas.append(mensagem)
                acoes = [a for f, a in self._assinaturas.items()
                         if _casa(f, topico)]
            for acao in acoes:
                try:
                    acao(mensagem)
                except Exception:                        # noqa: BLE001
                    pass    # um assinante que falha não derruba o cliente

    def _bater(self):
        """O PINGREQ: sem ele, o broker fecha a conexão no silêncio."""
        while self._vivo:
            time.sleep(max(1, self.keepalive // 2))
            if not self._vivo:
                return
            try:
                self._mandar(PINGREQ, 0, b"")
            except Exception:                            # noqa: BLE001
                return

    def fechar(self):
        """DISCONNECT e fecha. Idempotente."""
        if not self._vivo and self._soquete is None:
            return False
        self._vivo = False
        try:
            if self._soquete:
                self._mandar(DISCONNECT, 0, b"")
        except Exception:                                # noqa: BLE001
            pass
        finally:
            if self._soquete:
                try:
                    self._soquete.close()
                except OSError:                          # pragma: no cover
                    pass
                self._soquete = None
        return True

    def conectado(self):
        return bool(self._vivo)

    def __repr__(self):
        estado = "conectado" if self._vivo else "fechado"
        return f"<mqtt {self.cliente}@{self.host}:{self.porta} {estado}>"


def _casa(filtro, topico):
    """A regra de curinga do MQTT: `+` um nível, `#` o resto."""
    partes_f = str(filtro).split("/")
    partes_t = str(topico).split("/")
    for i, parte in enumerate(partes_f):
        if parte == "#":
            return True
        if i >= len(partes_t):
            return False
        if parte != "+" and parte != partes_t[i]:
            return False
    return len(partes_f) == len(partes_t)


def mqtt(host="localhost", porta=1883, cliente="", usuario="", senha="",
         keepalive=60, testamento=None, prazo=10.0):
    """Cria o cliente e **conecta**."""
    c = Mqtt(host, porta, cliente, usuario, senha, keepalive, testamento, prazo)
    c.conectar()
    return c
