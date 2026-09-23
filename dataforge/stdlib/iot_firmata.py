# -*- coding: utf-8 -*-
"""Firmata 2.x — falar com uma placa que já está ligada.

O Firmata é o protocolo que o sketch `firmata` do `Arcane.IoT` fala, e que a IDE
do Arduino: a placa vira um periférico, e quem decide é o computador.
Isso muda o ciclo de trabalho por inteiro.

| Sem Firmata | Com Firmata |
|---|---|
| escrever C++, compilar, gravar, testar | chamar `placa.escrever(13, yes)` e ver o LED |
| 20 s a cada tentativa | milissegundos |
| depurar por `Serial.println` | depurar com o depurador da linguagem |

O preço, dito sem rodeio: **cada ordem atravessa o cabo**. Um laço que
pisca o LED mil vezes por segundo não cabe aqui — isso é sketch. O
Firmata serve para prototipar, para ler sensor, para automação de mesa
e para um painel que controla a placa. Ver `/docs/iot/quando-usar`.

O parser é uma máquina de estados sobre um fluxo de bytes: mensagem de
status (bit alto ligado) abre um quadro, e os bytes de dados vêm em
**sete bits** — o oitavo é reservado para marcar comando. É por isso que
todo valor viaja partido em LSB e MSB.
"""

import threading
import time

from ..errors import RuntimeError_

_DOC = "iot/firmata"

# ── comandos ────────────────────────────────────────────────
DIGITAL_MESSAGE = 0x90
ANALOG_MESSAGE = 0xE0
REPORT_ANALOG = 0xC0
REPORT_DIGITAL = 0xD0
SET_PIN_MODE = 0xF4
SET_DIGITAL_PIN = 0xF5
PROTOCOL_VERSION = 0xF9
SYSTEM_RESET = 0xFF
START_SYSEX = 0xF0
END_SYSEX = 0xF7

# ── sysex ───────────────────────────────────────────────────
REPORT_FIRMWARE = 0x79
CAPABILITY_QUERY = 0x6B
CAPABILITY_RESPONSE = 0x6C
ANALOG_MAPPING_QUERY = 0x69
ANALOG_MAPPING_RESPONSE = 0x6A
PIN_STATE_QUERY = 0x6D
PIN_STATE_RESPONSE = 0x6E
SERVO_CONFIG = 0x70
STRING_DATA = 0x71
I2C_REQUEST = 0x76
I2C_REPLY = 0x77
I2C_CONFIG = 0x78
SAMPLING_INTERVAL = 0x7A

#: Os modos de pino, com o nome em português. O número é do protocolo.
MODOS = {
    "entrada": 0x00,
    "saida": 0x01,
    "analogico": 0x02,
    "pwm": 0x03,
    "servo": 0x04,
    "shift": 0x05,
    "i2c": 0x06,
    "onewire": 0x07,
    "stepper": 0x08,
    "encoder": 0x09,
    "serial": 0x0A,
    "entrada_pullup": 0x0B,
}
NOME_DO_MODO = {v: k for k, v in MODOS.items()}


def _erro(mensagem, nota="", dica="", classe=None):
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


def _de_sete_bits(corpo):
    """Os pares (baixo, alto) de volta em bytes inteiros.

    Ler so os pares de indice par devolve a METADE BAIXA de cada byte:
    em ASCII ninguem nota, porque o bit 7 e zero; num acento, "ola" vira
    "olC!". O erro fica escondido ate a primeira mensagem em portugues.
    """
    return bytes(((corpo[i] | (corpo[i + 1] << 7)) & 0xFF)
                 for i in range(0, len(corpo) - 1, 2))


def _sete_bits(valor):
    """Um valor em dois bytes de sete bits — LSB primeiro, como o protocolo."""
    valor = int(valor)
    return bytes([valor & 0x7F, (valor >> 7) & 0x7F])


# ═══════════════════════════════════════════════════════════
#  A placa
# ═══════════════════════════════════════════════════════════

class Placa:
    """Uma placa falando Firmata, do outro lado de um transporte.

    O transporte é qualquer coisa com `escrever`, `ler` e `fechar`: a
    porta serial de verdade, ou o `Simulador`. É essa fronteira que
    torna todo exemplo desta documentação executável sem hardware — e a
    mesma que deixa o teste rodar no CI.
    """

    def __init__(self, transporte, nome="placa", prazo=5.0):
        self.transporte = transporte
        self.nome = str(nome)
        self.prazo = float(prazo)
        self._trava = threading.RLock()
        self._digital = {}          # pino -> 0/1 lido
        self._analogico = {}        # canal -> 0..1023
        self._modos = {}            # pino -> nome do modo
        self._versao = None         # (maior, menor) do protocolo
        self._firmware = None       # {"nome", "versao"}
        self._capacidades = None    # pino -> [modos]
        self._mapa_analogico = None
        self._i2c = {}              # (endereco, registro) -> [bytes]
        self._textos = []
        self._vivo = True
        self._parcial = bytearray()
        self._sysex = None
        self._ouvintes = []
        self._leitor = threading.Thread(target=self._ler_sempre, daemon=True,
                                        name=f"firmata-{self.nome}")
        self._leitor.start()

    # ── o laço de leitura ────────────────────────────────────

    def _ler_sempre(self):
        while self._vivo:
            try:
                dados = self.transporte.ler(64, prazo=0.05)
            except Exception:                            # noqa: BLE001
                return
            if dados:
                self._consumir(dados)
            else:
                time.sleep(0.001)

    def _consumir(self, dados):
        for byte in dados:
            if self._sysex is not None:
                if byte == END_SYSEX:
                    self._tratar_sysex(bytes(self._sysex))
                    self._sysex = None
                else:
                    self._sysex.append(byte)
                continue
            if byte == START_SYSEX:
                self._sysex = bytearray()
                continue
            if byte & 0x80:
                self._parcial = bytearray([byte])
                continue
            if self._parcial:
                self._parcial.append(byte)
                self._tratar_mensagem()

    def _tratar_mensagem(self):
        cabeca = self._parcial[0]
        comando = cabeca & 0xF0
        canal = cabeca & 0x0F
        if comando == ANALOG_MESSAGE and len(self._parcial) == 3:
            valor = self._parcial[1] | (self._parcial[2] << 7)
            with self._trava:
                self._analogico[canal] = valor
            self._avisar("analogico", canal, valor)
            self._parcial = bytearray()
        elif comando == DIGITAL_MESSAGE and len(self._parcial) == 3:
            mascara = self._parcial[1] | (self._parcial[2] << 7)
            with self._trava:
                for i in range(8):
                    pino = canal * 8 + i
                    novo = (mascara >> i) & 1
                    antigo = self._digital.get(pino)
                    self._digital[pino] = novo
                    if antigo is not None and antigo != novo:
                        self._avisar("digital", pino, novo)
            self._parcial = bytearray()
        elif cabeca == PROTOCOL_VERSION and len(self._parcial) == 3:
            self._versao = (self._parcial[1], self._parcial[2])
            self._parcial = bytearray()

    def _tratar_sysex(self, corpo):
        if not corpo:
            return
        tipo = corpo[0]
        if tipo == REPORT_FIRMWARE and len(corpo) >= 3:
            nome = _de_sete_bits(corpo[3:]).decode("ascii", "replace").rstrip("\x00")
            self._firmware = {"nome": nome, "versao": f"{corpo[1]}.{corpo[2]}"}
            self._versao = self._versao or (corpo[1], corpo[2])
        elif tipo == CAPABILITY_RESPONSE:
            capacidades, atual, pino = {}, [], 0
            for byte in corpo[1:]:
                if byte == 0x7F:
                    capacidades[pino] = atual
                    atual, pino = [], pino + 1
                    continue
                atual.append(byte)
            # os modos vêm em pares (modo, resolução): só o modo importa
            self._capacidades = {
                p: [NOME_DO_MODO.get(v, str(v)) for v in vs[0::2]]
                for p, vs in capacidades.items()}
        elif tipo == ANALOG_MAPPING_RESPONSE:
            self._mapa_analogico = {i: canal
                                    for i, canal in enumerate(corpo[1:])
                                    if canal != 0x7F}
        elif tipo == STRING_DATA:
            texto = _de_sete_bits(corpo[1:]).decode("utf-8", "replace").rstrip("\x00")
            self._textos.append(texto)
            self._avisar("texto", -1, texto)
        elif tipo == I2C_REPLY and len(corpo) >= 5:
            endereco = corpo[1] | (corpo[2] << 7)
            registro = corpo[3] | (corpo[4] << 7)
            dados = [corpo[i] | (corpo[i + 1] << 7)
                     for i in range(5, len(corpo) - 1, 2)]
            with self._trava:
                self._i2c[(endereco, registro)] = dados

    def _avisar(self, tipo, pino, valor):
        for acao in list(self._ouvintes):
            try:
                acao({"tipo": tipo, "pino": pino, "valor": valor})
            except Exception:                            # noqa: BLE001
                pass    # um ouvinte que falha não derruba a leitura

    # ── escrever ─────────────────────────────────────────────

    def _mandar(self, dados):
        if not self._vivo:
            raise _erro("esta placa ja foi fechada.",
                        dica="IoT.conectar(porta) abre outra")
        self.transporte.escrever(bytes(dados))

    def _esperar(self, condicao, o_que, prazo=None):
        limite = time.monotonic() + (self.prazo if prazo is None else float(prazo))
        while time.monotonic() < limite:
            if condicao():
                return True
            time.sleep(0.002)
        raise _erro(
            f"a placa nao respondeu {o_que} em {self.prazo:g} s.",
            nota="ela responde quando o firmware do Firmata esta gravado; "
                 "sem ele, a porta abre e nada chega",
            dica="dataforge iot carregar firmata --porta=... grava o firmware; "
                 "'dataforge iot doctor' confere porta, sketch e velocidade")

    def apresentar(self):
        """Pergunta versão, firmware, capacidades e o mapa analógico.

        Chamado por `conectar`. Sem isto, `modo(pino, "servo")` num pino
        que não faz servo seria aceito aqui e ignorado lá — o pior
        silêncio possível num programa que controla hardware.
        """
        self._mandar([PROTOCOL_VERSION])
        self._mandar([START_SYSEX, REPORT_FIRMWARE, END_SYSEX])
        self._esperar(lambda: self._firmware is not None, "quem e")
        self._mandar([START_SYSEX, CAPABILITY_QUERY, END_SYSEX])
        self._esperar(lambda: self._capacidades is not None, "as capacidades")
        self._mandar([START_SYSEX, ANALOG_MAPPING_QUERY, END_SYSEX])
        self._esperar(lambda: self._mapa_analogico is not None,
                      "o mapa analogico")
        return self.info()

    def info(self):
        return {
            "nome": self.nome,
            "firmware": self._firmware or {},
            "protocolo": (f"{self._versao[0]}.{self._versao[1]}"
                          if self._versao else ""),
            "pinos": len(self._capacidades or {}),
            "analogicos": len(self._mapa_analogico or {}),
        }

    def capacidades(self, pino=None):
        """O que cada pino aceita — lido da PLACA, e não de uma tabela.

        Uma tabela escrita aqui envelheceria na primeira placa nova, e
        uma UNO, uma Mega e um ESP32 têm mapas diferentes.
        """
        if self._capacidades is None:
            return {}
        if pino is None:
            return {str(p): list(m) for p, m in sorted(self._capacidades.items())}
        return list(self._capacidades.get(int(pino), []))

    def _conferir_modo(self, pino, modo):
        if self._capacidades is None:
            return
        aceita = self._capacidades.get(int(pino))
        if aceita is None:
            raise _erro(
                f"esta placa nao tem o pino {pino}.",
                nota=f"ela tem de 0 a {max(self._capacidades) if self._capacidades else 0}",
                dica="placa.capacidades() mostra o que cada pino aceita")
        if modo not in aceita:
            raise _erro(
                f"o pino {pino} nao faz '{modo}'.",
                nota=f"ele aceita: {', '.join(aceita) or 'nada'}",
                dica="num Arduino UNO, PWM so nos pinos 3, 5, 6, 9, 10 e 11")

    def modo(self, pino, modo):
        """Declara o que o pino faz: entrada, saida, pwm, servo, analogico…"""
        nome = str(modo)
        if nome not in MODOS:
            raise _erro(f"'{modo}' nao e um modo de pino.",
                        nota=f"os modos: {', '.join(sorted(MODOS))}")
        self._conferir_modo(pino, nome)
        self._mandar([SET_PIN_MODE, int(pino), MODOS[nome]])
        with self._trava:
            self._modos[int(pino)] = nome
        if nome in ("entrada", "entrada_pullup"):
            self.relatar_digital(int(pino) // 8, True)
        return nome

    def escrever(self, pino, valor):
        """Liga ou desliga um pino digital."""
        alto = 1 if valor in (True, 1, "1", "alto") else 0
        self._mandar([SET_DIGITAL_PIN, int(pino), alto])
        with self._trava:
            self._digital[int(pino)] = alto
        return alto == 1

    def ler(self, pino):
        """O último valor lido de um pino digital, como `yes`/`no`.

        É o ÚLTIMO relatado, e não uma pergunta ao vivo: a placa envia
        quando muda. `placa.esperar_mudanca` espera a próxima.
        """
        with self._trava:
            return bool(self._digital.get(int(pino), 0))

    def analogico(self, canal):
        """O valor de 0 a 1023 do canal analógico (o A0 é o canal 0)."""
        with self._trava:
            return self._analogico.get(int(canal), 0)

    def relatar_analogico(self, canal, ligado=True):
        """Liga o envio periódico daquele canal. Sem isto, nada chega."""
        self._mandar([REPORT_ANALOG | (int(canal) & 0x0F), 1 if ligado else 0])
        return bool(ligado)

    def relatar_digital(self, porta, ligado=True):
        self._mandar([REPORT_DIGITAL | (int(porta) & 0x0F), 1 if ligado else 0])
        return bool(ligado)

    def pwm(self, pino, valor):
        """0 a 255 num pino PWM — o brilho de um LED, a velocidade de um motor."""
        v = int(valor)
        if not 0 <= v <= 255:
            raise _erro(f"o PWM vai de 0 a 255, e veio {v}.",
                        dica="para 0..1 multiplique por 255")
        self._exigir_modo(pino, "pwm")
        self._mandar(bytes([ANALOG_MESSAGE | (int(pino) & 0x0F)]) + _sete_bits(v))
        return v

    def servo(self, pino, graus):
        """A posição de um servo, de 0 a 180 graus."""
        g = int(graus)
        if not 0 <= g <= 180:
            raise _erro(f"um servo vai de 0 a 180 graus, e veio {g}.")
        self._exigir_modo(pino, "servo")
        self._mandar(bytes([ANALOG_MESSAGE | (int(pino) & 0x0F)]) + _sete_bits(g))
        return g

    def configurar_servo(self, pino, minimo=544, maximo=2400):
        """Os microssegundos das duas pontas — cada servo tem os seus."""
        self._mandar(bytes([START_SYSEX, SERVO_CONFIG, int(pino)])
                     + _sete_bits(minimo) + _sete_bits(maximo)
                     + bytes([END_SYSEX]))
        return self.modo(pino, "servo")

    def _exigir_modo(self, pino, esperado):
        atual = self._modos.get(int(pino))
        if atual != esperado:
            # Declarar por conta própria seria conveniente e errado: um
            # pino em 'saida' recebendo PWM acende no talo, e quem lê o
            # programa não veria onde o modo mudou.
            raise _erro(
                f"o pino {pino} esta em '{atual or 'indefinido'}', e "
                f"'{esperado}' precisa do modo declarado.",
                dica=f'placa.modo({pino}, "{esperado}") antes')

    def amostragem(self, ms):
        """De quanto em quanto tempo a placa envia os analógicos.

        O padrão do Firmata é 19 ms. Um valor muito baixo enche a serial
        de mensagens e atrasa as ordens que você manda; um alto faz o
        gráfico perder detalhe.
        """
        valor = int(ms)
        if not 10 <= valor <= 10000:
            raise _erro(f"a amostragem vai de 10 a 10000 ms, e veio {valor}.")
        self._mandar(bytes([START_SYSEX, SAMPLING_INTERVAL])
                     + _sete_bits(valor) + bytes([END_SYSEX]))
        return valor

    # ── I2C ──────────────────────────────────────────────────

    def i2c_configurar(self, atraso=0):
        self._mandar(bytes([START_SYSEX, I2C_CONFIG]) + _sete_bits(atraso)
                     + bytes([END_SYSEX]))
        return True

    def i2c_escrever(self, endereco, dados):
        corpo = bytearray([START_SYSEX, I2C_REQUEST, int(endereco) & 0x7F, 0x00])
        for byte in dados:
            corpo += _sete_bits(int(byte))
        corpo.append(END_SYSEX)
        self._mandar(corpo)
        return len(list(dados))

    def i2c_ler(self, endereco, registro, quantos, prazo=None):
        """Pede N bytes e ESPERA a resposta. `void` se ela não vier."""
        with self._trava:
            self._i2c.pop((int(endereco), int(registro)), None)
        corpo = bytearray([START_SYSEX, I2C_REQUEST, int(endereco) & 0x7F, 0x08])
        corpo += _sete_bits(int(registro))
        corpo += _sete_bits(int(quantos))
        corpo.append(END_SYSEX)
        self._mandar(corpo)
        chave = (int(endereco), int(registro))
        limite = time.monotonic() + (self.prazo if prazo is None else float(prazo))
        while time.monotonic() < limite:
            with self._trava:
                if chave in self._i2c:
                    return list(self._i2c[chave])
            time.sleep(0.002)
        return None

    # ── esperar e observar ───────────────────────────────────

    def esperar_mudanca(self, pino, prazo=5.0):
        """Espera o pino mudar de estado. `void` quando o prazo acaba."""
        inicial = self.ler(pino)
        limite = time.monotonic() + float(prazo)
        while time.monotonic() < limite:
            atual = self.ler(pino)
            if atual != inicial:
                return atual
            time.sleep(0.002)
        return None

    def observar(self, acao):
        """Chama `acao(evento)` a cada leitura que chega da placa."""
        self._ouvintes.append(acao)
        return lambda: self._ouvintes.remove(acao) if acao in self._ouvintes else False

    def textos(self):
        """As mensagens que o sketch mandou com `Firmata.sendString`."""
        return list(self._textos)

    # ── fim ──────────────────────────────────────────────────

    def reiniciar(self):
        """Devolve todo pino ao estado de entrada, como no boot."""
        self._mandar([SYSTEM_RESET])
        with self._trava:
            self._modos.clear()
            self._digital.clear()
            self._analogico.clear()
        return True

    def fechar(self):
        """Desliga as saídas antes de sair — e é idempotente.

        Um programa que termina deixando um relé ligado é o defeito mais
        caro desta área: o resto do sistema continua sem ninguém olhando.
        """
        if not self._vivo:
            return False
        try:
            for pino, modo in list(self._modos.items()):
                if modo in ("saida", "pwm"):
                    try:
                        self._mandar([SET_DIGITAL_PIN, pino, 0])
                    except Exception:                    # noqa: BLE001
                        break
        finally:
            self._vivo = False
            self.transporte.fechar()
        return True

    def viva(self):
        return self._vivo

    def __repr__(self):
        fw = (self._firmware or {}).get("nome", "?")
        return f"<placa {self.nome}: {fw} {len(self._modos)} pino(s) em uso>"
