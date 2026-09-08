"""
A camada de transporte dos drivers do Forge.

Todos os bancos falam por socket, e todos precisam das mesmas quatro
coisas: abrir com prazo, ler exatamente N bytes, empacotar inteiros na
ordem certa e nao deixar a conexao pendurada quando algo da errado.
Escrever isso quatro vezes garantiria quatro comportamentos diferentes
sob falha — que e justamente quando o comportamento importa.

─── Por que protocolo proprio, e nao um driver ─────────────

O DataForge nao tem dependencia de runtime. Nao e purismo: e o que
permite 'pip install dataforge' funcionar em qualquer maquina, e o
instalador nao precisar de compilador para o psycopg2.

O custo e este arquivo e os quatro ao lado. O que se ganha e que
'conectar("postgres://...")' funciona numa instalacao limpa.
"""

import hashlib
import hmac
import os
import socket
import ssl
import struct
import time

from ...errors import (
    AuthenticationError, ConnectionError_, DatabaseError, QueryError,
    TimeoutError_,
)


#: Quanto esperar para abrir a conexao, em segundos.
PRAZO_CONEXAO = 10.0

#: Quanto esperar por uma resposta.
PRAZO_LEITURA = 30.0


class Canal:
    """Um socket com leitura exata e erros da linguagem.

    'recv' pode devolver menos bytes do que se pediu — o TCP nao
    promete que uma escrita vira uma leitura. Todo driver que ignora
    isso funciona no localhost e falha em producao, sob carga, de forma
    irreproduzivel. 'ler' aqui insiste ate completar.
    """

    __slots__ = ("sock", "host", "porta", "_buffer", "_fechado")

    def __init__(self, host, porta, prazo=PRAZO_CONEXAO, tls=False,
                 verificar_tls=True):
        self.host = host
        self.porta = porta
        self._buffer = b""
        self._fechado = False
        try:
            self.sock = socket.create_connection((host, porta), timeout=prazo)
        except socket.timeout:
            raise TimeoutError_(
                f"{host}:{porta} did not answer within {prazo:.0f}s.",
                dica="check the host and port, and whether the service is up",
                doc="banco-de-dados") from None
        except OSError as e:
            raise ConnectionError_(
                f"could not connect to {host}:{porta}: {e}",
                nota="the server refused the connection or is unreachable",
                dica=("check the address and port, and that the container "
                      "is running:  docker ps"),
                doc="banco-de-dados") from None

        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(PRAZO_LEITURA)
        if tls:
            self.envolver_tls(verificar_tls)

    def envolver_tls(self, verificar=True):
        contexto = ssl.create_default_context()
        if not verificar:
            contexto.check_hostname = False
            contexto.verify_mode = ssl.CERT_NONE
        self.sock = contexto.wrap_socket(
            self.sock, server_hostname=self.host if verificar else None)

    # ── leitura ─────────────────────────────────────────────

    def ler(self, n):
        """Exatamente n bytes, ou erro. Nunca menos."""
        while len(self._buffer) < n:
            try:
                pedaco = self.sock.recv(max(4096, n - len(self._buffer)))
            except socket.timeout:
                raise TimeoutError_(
                    f"{self.host}:{self.porta} stopped answering mid-message.",
                    dica="the query may be too slow; raise the timeout",
                    doc="banco-de-dados") from None
            except OSError as e:
                raise ConnectionError_(
                    f"connection to {self.host}:{self.porta} broke: {e}",
                    doc="banco-de-dados") from None
            if not pedaco:
                raise ConnectionError_(
                    f"{self.host}:{self.porta} closed the connection.",
                    nota=("the server usually does this after an "
                          "authentication failure or a protocol error"),
                    doc="banco-de-dados")
            self._buffer += pedaco
        dados, self._buffer = self._buffer[:n], self._buffer[n:]
        return dados

    def ler_ate(self, marca=b"\r\n"):
        """Le ate encontrar a marca; devolve sem ela."""
        while marca not in self._buffer:
            try:
                pedaco = self.sock.recv(4096)
            except OSError as e:
                raise ConnectionError_(f"read failed: {e}",
                                       doc="banco-de-dados") from None
            if not pedaco:
                raise ConnectionError_("the server closed the connection.",
                                       doc="banco-de-dados")
            self._buffer += pedaco
        i = self._buffer.index(marca)
        dados, self._buffer = self._buffer[:i], self._buffer[i + len(marca):]
        return dados

    def ler_byte(self):
        return self.ler(1)

    def espiar(self, n=1):
        """Ve os proximos bytes sem consumi-los."""
        while len(self._buffer) < n:
            pedaco = self.sock.recv(4096)
            if not pedaco:
                return self._buffer
            self._buffer += pedaco
        return self._buffer[:n]

    # ── escrita ─────────────────────────────────────────────

    def escrever(self, dados):
        try:
            self.sock.sendall(dados)
        except OSError as e:
            raise ConnectionError_(f"write failed: {e}",
                                   doc="banco-de-dados") from None

    def prazo(self, segundos):
        self.sock.settimeout(segundos)

    def fechar(self):
        if self._fechado:
            return
        self._fechado = True
        try:
            self.sock.close()
        except OSError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.fechar()


# ─────────────────────────────────────────────────────────────
#  Empacotamento
# ─────────────────────────────────────────────────────────────

def i32(n):
    """Inteiro de 32 bits, big-endian — a ordem do PostgreSQL."""
    return struct.pack("!i", n)


def i16(n):
    return struct.pack("!h", n)


def le32(n):
    """32 bits little-endian — a ordem do MySQL e do MongoDB."""
    return struct.pack("<i", n)


def le64(n):
    return struct.pack("<q", n)


def des_i32(b, i=0):
    return struct.unpack_from("!i", b, i)[0]


def des_i16(b, i=0):
    return struct.unpack_from("!h", b, i)[0]


def des_le32(b, i=0):
    return struct.unpack_from("<i", b, i)[0]


def cstr(texto):
    """Texto terminado em zero, como o C — PostgreSQL e MySQL usam."""
    if isinstance(texto, bytes):
        return texto + b"\x00"
    return texto.encode("utf-8") + b"\x00"


def ler_cstr(dados, i=0):
    """Le um texto terminado em zero; devolve (texto, proximo indice)."""
    fim = dados.index(b"\x00", i)
    return dados[i:fim].decode("utf-8", "replace"), fim + 1


# ─────────────────────────────────────────────────────────────
#  SCRAM-SHA-256 — a autenticacao padrao do PostgreSQL e do Mongo
# ─────────────────────────────────────────────────────────────
#
# O 'md5' do PostgreSQL esta desativado por padrao desde a versao 14, e
# o Mongo nunca teve outra coisa. Sem SCRAM, o driver so conecta em
# servidor mal configurado — que e o unico tipo em que nao se deveria
# conectar.
#
# O algoritmo (RFC 5802) em quatro passos:
#   1. cliente manda um nonce
#   2. servidor responde com sal, contagem de iteracoes e o nonce dele
#   3. cliente prova que sabe a senha sem envia-la
#   4. servidor prova que tambem sabe, o que impede um impostor

class Scram:
    """Cliente SCRAM-SHA-1 ou SCRAM-SHA-256."""

    def __init__(self, usuario, senha, mecanismo="SCRAM-SHA-256"):
        self.usuario = usuario
        self.senha = senha
        self.mecanismo = mecanismo
        self.hash = hashlib.sha256 if "256" in mecanismo else hashlib.sha1
        self.nonce = os.urandom(18).hex()
        self.primeira_mensagem = ""
        self.chave_servidor = b""
        self.assinatura_esperada = b""

    def primeiro(self):
        """A mensagem que abre a negociacao."""
        # O nome vai vazio: o PostgreSQL ja o recebeu no startup, e o
        # RFC manda usar 'n=' vazio quando o canal ja o carrega.
        self.primeira_mensagem = f"n={self._escapar(self.usuario)},r={self.nonce}"
        return "n,," + self.primeira_mensagem

    def final(self, desafio):
        """A prova de que sabemos a senha, sem envia-la."""
        campos = dict(
            parte.split("=", 1) for parte in desafio.split(",") if "=" in parte)
        nonce = campos["r"]
        sal = _b64d(campos["s"])
        iteracoes = int(campos["i"])

        if not nonce.startswith(self.nonce):
            raise AuthenticationError(
                "the server's nonce does not extend ours.",
                nota="this is what SCRAM checks to detect an impostor server",
                doc="banco-de-dados")

        senha = self.senha.encode("utf-8")
        chave_salgada = hashlib.pbkdf2_hmac(
            self.hash().name, senha, sal, iteracoes)
        chave_cliente = hmac.new(chave_salgada, b"Client Key", self.hash).digest()
        chave_guardada = self.hash(chave_cliente).digest()
        self.chave_servidor = hmac.new(
            chave_salgada, b"Server Key", self.hash).digest()

        sem_prova = f"c=biws,r={nonce}"
        assinatura_texto = (f"{self.primeira_mensagem},{desafio},{sem_prova}")
        assinatura = hmac.new(
            chave_guardada, assinatura_texto.encode("utf-8"), self.hash).digest()
        prova = bytes(a ^ b for a, b in zip(chave_cliente, assinatura))

        self.assinatura_esperada = hmac.new(
            self.chave_servidor, assinatura_texto.encode("utf-8"),
            self.hash).digest()
        return f"{sem_prova},p={_b64e(prova)}"

    def conferir(self, resposta):
        """O servidor tambem provou que sabe? Senao, e um impostor."""
        campos = dict(
            parte.split("=", 1) for parte in resposta.split(",") if "=" in parte)
        if "e" in campos:
            raise AuthenticationError(
                f"the server rejected the credentials: {campos['e']}",
                doc="banco-de-dados")
        if _b64d(campos.get("v", "")) != self.assinatura_esperada:
            raise AuthenticationError(
                "the server failed to prove it knows the password.",
                nota="someone may be impersonating the database server",
                doc="banco-de-dados")
        return True

    @staticmethod
    def _escapar(nome):
        return nome.replace("=", "=3D").replace(",", "=2C")


def _b64e(dados):
    import base64
    return base64.b64encode(dados).decode("ascii")


def _b64d(texto):
    import base64
    return base64.b64decode(texto) if texto else b""


# ─────────────────────────────────────────────────────────────
#  Endereco
# ─────────────────────────────────────────────────────────────

#: A porta padrao de cada motor.
PORTAS = {
    "postgres": 5432, "postgresql": 5432, "pg": 5432,
    "mysql": 3306, "mariadb": 3306,
    "redis": 6379,
    "mongodb": 27017, "mongo": 27017,
    "sqlite": 0,
}

#: Apelidos aceitos, para o nome que o usuario escreveu.
MOTORES = {
    "postgres": "postgres", "postgresql": "postgres", "pg": "postgres",
    "mysql": "mysql",
    "mariadb": "mariadb",
    "redis": "redis",
    "mongodb": "mongo", "mongo": "mongo",
    "sqlite": "sqlite", "sqlite3": "sqlite", "file": "sqlite",
}


def analisar_url(url):
    """'postgres://usuario:senha@host:5432/banco?opcao=x' → vault.

    Uma URL e melhor que seis parametros soltos: cabe numa variavel de
    ambiente, e e o formato que todo servico de nuvem ja entrega
    pronto.
    """
    from urllib.parse import urlparse, parse_qs, unquote

    if "://" not in url:
        # Um caminho solto e SQLite: 'conectar("dados.db")'.
        return {"motor": "sqlite", "caminho": url, "host": "", "porta": 0,
                "usuario": "", "senha": "", "banco": url, "opcoes": {}}

    partes = urlparse(url)
    esquema = (partes.scheme or "").lower()
    motor = MOTORES.get(esquema)
    if motor is None:
        conhecidos = ", ".join(sorted(set(MOTORES)))
        raise DatabaseError(
            f"'{esquema}' is not a database the Forge knows.",
            nota=f"it understands: {conhecidos}",
            dica="the URL looks like  postgres://user:pass@host:5432/db",
            doc="banco-de-dados")

    if motor == "sqlite":
        caminho = (partes.netloc + partes.path) or ":memory:"
        return {"motor": "sqlite", "caminho": caminho, "host": "", "porta": 0,
                "usuario": "", "senha": "", "banco": caminho, "opcoes": {}}

    opcoes = {k: v[0] for k, v in parse_qs(partes.query).items()}
    return {
        "motor": motor,
        "host": partes.hostname or "localhost",
        "porta": partes.port or PORTAS.get(esquema, 0),
        "usuario": unquote(partes.username or ""),
        "senha": unquote(partes.password or ""),
        "banco": (partes.path or "/").lstrip("/"),
        "caminho": "",
        "opcoes": opcoes,
    }
