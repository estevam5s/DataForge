# -*- coding: utf-8 -*-
"""Arcane.Rede — TCP, UDP, DNS e TLS.

O que faltava
-------------
O Kiln fala HTTP, e a Malha fala com outro servico. Abaixo disso nao
havia nada: um protocolo proprio, um agente que manda uma linha por
UDP, ou descobrir para onde um nome aponta pediam sair da linguagem.

E o TLS estava na lista do que NAO existe, na propria documentacao.
Ele existe agora, dos dois lados.

Tres decisoes
-------------
1. **`receber` tem prazo, e o prazo tem padrao.** Uma leitura sem prazo
   e a forma mais comum de um servico travar para sempre: o outro lado
   caiu sem fechar o socket, e o `recv` fica esperando um byte que
   nunca vem. O padrao aqui e 30 segundos, e quem quiser esperar para
   sempre escreve isso.

2. **`receber_exato` insiste ate completar.** O `recv` devolve MENOS do
   que se pediu com frequencia — e tratar o retorno curto como a
   mensagem inteira corrompe a proxima. E a mesma licao que o WebSocket
   do Kiln aprendeu.

3. **O servidor atende uma conexao por thread, e diz isso.** Nao ha
   laco de eventos por baixo; o modelo e o mesmo do Kiln, e o aviso
   sobre estado compartilhado vale igual.
"""

import socket
import ssl
import threading


class ErroDeRede(Exception):
    pass


PRAZO_PADRAO = 30.0


def _erro(acao, erro, alvo=""):
    onde = f" ({alvo})" if alvo else ""
    if isinstance(erro, socket.timeout):
        return ErroDeRede(
            f"{acao}{onde}: o prazo acabou.\n"
            f"  O outro lado nao respondeu a tempo. Aumente o prazo, ou\n"
            f"  trate a espera — uma rede lenta nao e a mesma coisa que\n"
            f"  um servico fora do ar.")
    if isinstance(erro, ConnectionRefusedError):
        return ErroDeRede(
            f"{acao}{onde}: a conexao foi RECUSADA.\n"
            f"  Ha alguem escutando nessa porta? Recusa e resposta: o\n"
            f"  host esta de pe e nada atende ali.")
    if isinstance(erro, socket.gaierror):
        return ErroDeRede(
            f"{acao}{onde}: o nome nao resolve.\n"
            f"  O DNS nao sabe quem e esse host.")
    return ErroDeRede(f"{acao}{onde}: {erro}")


# ══════════════════════════════════════════════════════════════
#  Conexao
# ══════════════════════════════════════════════════════════════

class Conexao:
    """Um canal TCP aberto, dos dois lados iguais."""

    def __init__(self, bruto, endereco=None):
        self._s = bruto
        self.endereco = endereco or bruto.getpeername()
        self.aberta = True
        self.enviados = 0
        self.recebidos = 0

    # ── escrever ──

    def enviar(self, dados):
        """Manda tudo. Ao contrario do `send`, nao devolve pela metade."""
        bruto = _bytes(dados)
        try:
            self._s.sendall(bruto)
        except OSError as erro:
            self.aberta = False
            raise _erro("enviar", erro, self._nome()) from None
        self.enviados += len(bruto)
        return len(bruto)

    def enviar_linha(self, texto, fim="\n"):
        return self.enviar(str(texto) + fim)

    # ── ler ──

    def receber(self, quantos=4096, prazo=PRAZO_PADRAO):
        """O que chegou, ate `quantos` bytes. Vazio quando o outro fechou."""
        self._s.settimeout(prazo)
        try:
            pedaco = self._s.recv(quantos)
        except OSError as erro:
            raise _erro("receber", erro, self._nome()) from None
        if not pedaco:
            self.aberta = False
        self.recebidos += len(pedaco)
        return pedaco

    def receber_exato(self, quantos, prazo=PRAZO_PADRAO):
        """Insiste ate completar `quantos` bytes.

        O `recv` devolve menos do que se pediu com frequencia num
        pedaco que atravessa pacotes, e tratar o retorno curto como a
        mensagem inteira corrompe a proxima — o sintoma e uma conexao
        que funciona e de repente para.
        """
        partes, falta = [], quantos
        while falta > 0:
            pedaco = self.receber(falta, prazo)
            if not pedaco:
                raise ErroDeRede(
                    f"a conexao fechou faltando {falta} de {quantos} byte(s)")
            partes.append(pedaco)
            falta -= len(pedaco)
        return b"".join(partes)

    def receber_linha(self, prazo=PRAZO_PADRAO, limite=65536):
        """Ate a quebra de linha. Com teto, porque o outro lado pode mentir.

        Sem o limite, um cliente que manda bytes sem nunca mandar `\\n`
        enche a memoria do servidor — e e um ataque de uma linha.
        """
        partes, total = [], 0
        while True:
            byte = self.receber(1, prazo)
            if not byte:
                break
            if byte == b"\n":
                break
            if byte != b"\r":
                partes.append(byte)
                total += 1
            if total > limite:
                raise ErroDeRede(
                    f"a linha passou de {limite} bytes sem terminar.\n"
                    f"  Um cliente que nunca manda a quebra enche a memoria "
                    f"do servidor.")
        return b"".join(partes).decode("utf-8", "replace")

    def receber_tudo(self, prazo=PRAZO_PADRAO, limite=10 * 1024 * 1024):
        partes, total = [], 0
        while True:
            pedaco = self.receber(65536, prazo)
            if not pedaco:
                break
            partes.append(pedaco)
            total += len(pedaco)
            if total > limite:
                raise ErroDeRede(f"passou de {limite} bytes")
        return b"".join(partes)

    def fechar(self):
        self.aberta = False
        try:
            self._s.close()
        except OSError:
            pass
        return self

    def _nome(self):
        try:
            return f"{self.endereco[0]}:{self.endereco[1]}"
        except (TypeError, IndexError):
            return str(self.endereco)

    def __repr__(self):
        estado = "aberta" if self.aberta else "fechada"
        return f"<conexao {self._nome()} {estado}>"


def _bytes(valor):
    if isinstance(valor, (bytes, bytearray, memoryview)):
        return bytes(valor)
    return str(valor).encode("utf-8")


# ══════════════════════════════════════════════════════════════
#  TCP
# ══════════════════════════════════════════════════════════════

def conectar(host, porta, prazo=PRAZO_PADRAO, tls=False, conferir=True):
    """Abre uma conexao TCP. Com `tls := yes`, cifrada."""
    try:
        bruto = socket.create_connection((host, int(porta)), timeout=prazo)
    except OSError as erro:
        raise _erro("conectar", erro, f"{host}:{porta}") from None

    if tls:
        contexto = ssl.create_default_context()
        if not conferir:
            # Recusar sem avisar seria pior; aceitar calado tambem. Quem
            # desliga a conferencia esta dizendo "sei o que faco" — em
            # rede interna com certificado proprio, por exemplo.
            contexto.check_hostname = False
            contexto.verify_mode = ssl.CERT_NONE
        try:
            bruto = contexto.wrap_socket(bruto, server_hostname=host)
        except ssl.SSLError as erro:
            bruto.close()
            raise ErroDeRede(
                f"o TLS falhou com {host}:{porta}: {erro}\n"
                f"  Certificado invalido, expirado, ou de outro nome.\n"
                f"  Em rede interna com certificado proprio, passe "
                f"'conferir := no'.") from None
    return Conexao(bruto, (host, int(porta)))


class Servidor:
    """Escuta TCP e atende uma conexao por thread."""

    def __init__(self, atender, host="127.0.0.1", porta=0, fila=128,
                 tls=None):
        self.atender = atender
        self.host = host
        self.porta = porta
        self.fila = fila
        self.tls = tls
        self._s = None
        self._thread = None
        self.rodando = False
        self.atendidas = 0

    def subir(self, bloquear=True):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._s.bind((self.host, int(self.porta)))
        except OSError as erro:
            raise _erro("escutar", erro,
                        f"{self.host}:{self.porta}") from None
        self._s.listen(self.fila)
        self.porta = self._s.getsockname()[1]
        self.rodando = True

        if self.tls:
            contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            contexto.load_cert_chain(self.tls["certificado"],
                                     self.tls["chave"])
            self._contexto = contexto
        else:
            self._contexto = None

        if bloquear:
            self._laco()
            return self
        self._thread = threading.Thread(target=self._laco, daemon=True)
        self._thread.start()
        return self

    def _laco(self):
        while self.rodando:
            try:
                bruto, endereco = self._s.accept()
            except OSError:
                break
            if self._contexto is not None:
                try:
                    bruto = self._contexto.wrap_socket(bruto, server_side=True)
                except ssl.SSLError:
                    bruto.close()
                    continue
            self.atendidas += 1
            # Uma thread por conexao. O modelo e o do Kiln, e o aviso
            # sobre estado compartilhado vale igual: duas conexoes
            # escrevendo no mesmo nome perdem atualizacoes.
            threading.Thread(
                target=self._uma, args=(Conexao(bruto, endereco),),
                daemon=True).start()

    def _uma(self, conexao):
        try:
            self.atender(conexao)
        except Exception:                            # noqa: BLE001
            pass          # um cliente nao pode derrubar o servidor
        finally:
            conexao.fechar()

    def parar(self):
        self.rodando = False
        if self._s is not None:
            try:
                self._s.close()
            except OSError:
                pass
        return self

    def __repr__(self):
        return f"<servidor tcp {self.host}:{self.porta}>"


def servir(atender, host="127.0.0.1", porta=0, tls=None):
    """Sobe e BLOQUEIA."""
    return Servidor(atender, host, porta, tls=tls).subir(bloquear=True)


def servir_em_segundo_plano(atender, host="127.0.0.1", porta=0, tls=None):
    """Sobe em outra thread e devolve o servidor, com a porta real."""
    return Servidor(atender, host, porta, tls=tls).subir(bloquear=False)


# ══════════════════════════════════════════════════════════════
#  UDP
# ══════════════════════════════════════════════════════════════

class Datagrama:
    """UDP: manda e esquece. Sem conexao, sem ordem, sem garantia.

    E o certo para metrica, descoberta e log — onde perder um pacote
    custa menos que a espera de confirmar cada um.
    """

    def __init__(self, host="0.0.0.0", porta=0, escutar=False):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if escutar:
            self._s.bind((host, int(porta)))
        self.porta = self._porta_do_sistema()

    def _porta_do_sistema(self):
        """A porta, ou 0 enquanto o socket nao estiver ligado a uma.

        `getsockname` num socket UDP que ainda nao foi ligado devolve
        `('0.0.0.0', 0)` no Unix e levanta **WSAEINVAL (10022)** no
        Windows — e o construtor de um emissor (`udp()`, sem
        `escutar`) morria ali antes de mandar o primeiro byte.

        Um socket de saida ganha a porta quando envia; por isso o
        numero e reconsultado em `enviar`, e nao so aqui.
        """
        try:
            return self._s.getsockname()[1]
        except OSError:
            return 0

    def enviar(self, dados, host, porta):
        enviados = self._s.sendto(_bytes(dados), (host, int(porta)))
        if not self.porta:
            self.porta = self._porta_do_sistema()
        return enviados

    def receber(self, quantos=65535, prazo=PRAZO_PADRAO):
        """Devolve `{dados, host, porta}` — de quem veio importa."""
        self._s.settimeout(prazo)
        try:
            dados, origem = self._s.recvfrom(quantos)
        except OSError as erro:
            raise _erro("receber (udp)", erro) from None
        return {"dados": dados, "host": origem[0], "porta": origem[1]}

    def transmitir(self, dados, porta):
        """Para todo mundo da rede local."""
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        return self._s.sendto(_bytes(dados), ("<broadcast>", int(porta)))

    def fechar(self):
        self._s.close()
        return self

    def __repr__(self):
        return f"<udp :{self.porta}>"


def udp(host="0.0.0.0", porta=0, escutar=False):
    return Datagrama(host, porta, escutar)


# ══════════════════════════════════════════════════════════════
#  DNS
# ══════════════════════════════════════════════════════════════

def resolver(nome):
    """Os IPs de um nome. Lista, porque quase sempre e mais de um."""
    try:
        info = socket.getaddrinfo(nome, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as erro:
        raise _erro("resolver", erro, nome) from None
    vistos, saida = set(), []
    for familia, _, _, _, endereco in info:
        ip = endereco[0]
        if ip not in vistos:
            vistos.add(ip)
            saida.append({"ip": ip,
                          "versao": 6 if familia == socket.AF_INET6 else 4})
    return saida


def nome_de(ip):
    """O caminho contrario: de quem e este IP."""
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except OSError as erro:
        raise _erro("nome_de", erro, str(ip)) from None


def meu_nome():
    return socket.gethostname()


def meu_ip():
    """O IP com que esta maquina sai para a rede.

    Nao e `gethostbyname(gethostname())`, que numa maquina com
    /etc/hosts comum devolve 127.0.0.1 e nao serve para nada. Abrir um
    socket UDP para fora (sem mandar nada) faz o sistema escolher a
    interface de verdade.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def porta_livre():
    """Uma porta que o sistema garante estar livre AGORA."""
    s = socket.socket()
    s.bind(("", 0))
    porta = s.getsockname()[1]
    s.close()
    return porta


def porta_aberta(host, porta, prazo=2.0):
    """Ha alguem escutando? Para health check e espera de subida.

    Ela ABRE uma conexao de verdade e fecha em seguida — nao ha como
    perguntar sem bater na porta. Um servidor que conta conexoes vai
    ver esta tambem, e um que le uma linha logo de cara vai receber
    o fim da conexao. E o preco de um teste honesto: responder sem
    conectar seria adivinhar.
    """
    try:
        with socket.create_connection((host, int(porta)), timeout=prazo):
            return True
    except OSError:
        return False


def esperar_porta(host, porta, prazo=30.0, intervalo=0.2):
    """Espera alguem subir naquela porta. Devolve quanto demorou.

    E o que falta em todo script de integracao: subir o servico e
    dormir dois segundos torcendo para dar tempo.
    """
    import time
    inicio = time.perf_counter()
    while time.perf_counter() - inicio < prazo:
        if porta_aberta(host, porta, min(1.0, intervalo * 5)):
            return round(time.perf_counter() - inicio, 3)
        time.sleep(intervalo)
    raise ErroDeRede(
        f"{host}:{porta} nao abriu em {prazo}s.\n"
        f"  O servico nao subiu, subiu em outra porta, ou subiu em\n"
        f"  127.0.0.1 quando deveria ser 0.0.0.0.")


# ══════════════════════════════════════════════════════════════
#  TLS
# ══════════════════════════════════════════════════════════════

def certificado_de(host, porta=443, prazo=PRAZO_PADRAO):
    """O certificado que o servidor apresenta — quem o emitiu e ate quando.

    Um certificado vencido derruba o site inteiro, e o aviso chega pelo
    cliente reclamando. Isto e o que um monitor pergunta.
    """
    contexto = ssl.create_default_context()
    try:
        with socket.create_connection((host, int(porta)), timeout=prazo) as cru:
            with contexto.wrap_socket(cru, server_hostname=host) as seguro:
                bruto = seguro.getpeercert()
                cifra = seguro.cipher()
    except OSError as erro:
        raise _erro("certificado_de", erro, f"{host}:{porta}") from None

    def _plano(campos):
        return {c[0][0]: c[0][1] for c in (campos or ()) if c}

    return {
        "assunto": _plano(bruto.get("subject")),
        "emissor": _plano(bruto.get("issuer")),
        "valido_de": bruto.get("notBefore"),
        "valido_ate": bruto.get("notAfter"),
        "nomes": [v for k, v in bruto.get("subjectAltName", ()) if k == "DNS"],
        "cifra": cifra[0] if cifra else "",
        "protocolo": cifra[1] if cifra else "",
    }


def dias_ate_vencer(host, porta=443):
    """Quantos dias faltam. Negativo se ja venceu."""
    import datetime
    ficha = certificado_de(host, porta)
    vence = datetime.datetime.strptime(ficha["valido_ate"],
                                       "%b %d %H:%M:%S %Y %Z")
    return (vence - datetime.datetime.utcnow()).days


class ArcaneRede:
    """O dicionario que `adopt Arcane.Rede` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Rede",

            # ── TCP ──
            "conectar": conectar,
            "servir": servir,
            "servir_em_segundo_plano": servir_em_segundo_plano,
            "Servidor": Servidor,
            "Conexao": Conexao,

            # ── UDP ──
            "udp": udp,

            # ── DNS ──
            "resolver": resolver,
            "nome_de": nome_de,
            "meu_nome": meu_nome,
            "meu_ip": meu_ip,

            # ── Portas ──
            "porta_livre": porta_livre,
            "porta_aberta": porta_aberta,
            "esperar_porta": esperar_porta,

            # ── TLS ──
            "certificado_de": certificado_de,
            "dias_ate_vencer": dias_ate_vencer,

            "prazo_padrao": PRAZO_PADRAO,
        }
