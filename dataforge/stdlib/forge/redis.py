"""
Driver Redis — protocolo RESP, falado direto.

RESP e o protocolo mais simples que um banco de dados serio tem: cinco
tipos, cada resposta comeca com um byte que diz qual e, e strings
carregam o proprio tamanho. Da para ler a especificacao inteira numa
tarde — e por isso que este arquivo cabe em 300 linhas sem atalhos.

    +OK\\r\\n              texto simples
    -ERR algo\\r\\n        erro
    :42\\r\\n              inteiro
    $5\\r\\nvalor\\r\\n      texto com tamanho
    *2\\r\\n...            arranjo

O RESP3 acrescenta mapas, conjuntos e booleanos. O driver os entende
quando o servidor os manda, mas nao pede RESP3: a diferenca nao muda o
que o DataForge ve, e HELLO 3 falha em Redis antigo.
"""

from .protocolo import Canal, analisar_url
from ...errors import (AuthenticationError, ConnectionError_, DatabaseError,
                       QueryError)


class Redis:
    """Uma conexao Redis.

    Os comandos nao sao metodos nomeados um a um: sao mais de 240, e
    uma lista escrita a mao envelheceria a cada versao do Redis. O
    driver monta o comando a partir do nome, e o servidor recusa o que
    nao existir — dizendo qual.
    """

    def __init__(self, host="localhost", porta=6379, senha="", usuario="",
                 banco=0, tls=False, prazo=10.0):
        self.host = host
        self.porta = porta
        self.banco = int(banco or 0)
        self.canal = Canal(host, porta, prazo, tls=tls)
        self._fechado = False

        if senha:
            # O Redis 6+ tem usuarios; antes disso, so senha.
            if usuario:
                self.comando("AUTH", usuario, senha)
            else:
                self.comando("AUTH", senha)
        if self.banco:
            self.comando("SELECT", self.banco)

    # ── protocolo ───────────────────────────────────────────

    @staticmethod
    def _codificar(partes):
        """O comando no formato de arranjo, que e o unico que o Redis aceita."""
        saida = [f"*{len(partes)}\r\n".encode()]
        for parte in partes:
            if isinstance(parte, bool):
                bruto = b"1" if parte else b"0"
            elif isinstance(parte, bytes):
                bruto = parte
            elif parte is None:
                bruto = b""
            else:
                bruto = str(parte).encode("utf-8")
            saida.append(b"$" + str(len(bruto)).encode() + b"\r\n" + bruto + b"\r\n")
        return b"".join(saida)

    def _ler_resposta(self):
        tipo = self.canal.ler_byte()

        if tipo == b"+":                            # texto simples
            return self.canal.ler_ate().decode("utf-8", "replace")
        if tipo == b"-":                            # erro
            texto = self.canal.ler_ate().decode("utf-8", "replace")
            raise self._erro(texto)
        if tipo == b":":                            # inteiro
            return int(self.canal.ler_ate())
        if tipo == b"$":                            # texto com tamanho
            n = int(self.canal.ler_ate())
            if n == -1:
                return None
            dados = self.canal.ler(n)
            self.canal.ler(2)                       # o \r\n final
            return dados.decode("utf-8", "replace")
        if tipo == b"*":                            # arranjo
            n = int(self.canal.ler_ate())
            if n == -1:
                return None
            return [self._ler_resposta() for _ in range(n)]

        # ── RESP3 ──
        if tipo == b"%":                            # mapa
            n = int(self.canal.ler_ate())
            return {self._ler_resposta(): self._ler_resposta()
                    for _ in range(n)}
        if tipo in (b"~", b">"):                    # conjunto, notificacao
            n = int(self.canal.ler_ate())
            return [self._ler_resposta() for _ in range(n)]
        if tipo == b"#":                            # booleano
            return self.canal.ler_ate() == b"t"
        if tipo == b",":                            # ponto flutuante
            return float(self.canal.ler_ate())
        if tipo == b"_":                            # nulo
            self.canal.ler_ate()
            return None
        if tipo == b"=":                            # texto verbatim
            n = int(self.canal.ler_ate())
            dados = self.canal.ler(n)
            self.canal.ler(2)
            return dados.decode("utf-8", "replace")[4:]

        raise DatabaseError(
            f"unknown RESP type: {tipo!r}",
            nota="the server may not be Redis, or speaks a newer protocol",
            doc="banco-de-dados")

    @staticmethod
    def _erro(texto):
        """O erro do Redis, no vocabulario da linguagem."""
        codigo = texto.split(" ", 1)[0]
        if codigo in ("NOAUTH", "WRONGPASS", "NOPERM"):
            return AuthenticationError(
                texto,
                dica="pass the password in the URL:  redis://:senha@host",
                doc="banco-de-dados")
        if codigo == "LOADING":
            return ConnectionError_(
                texto, nota="Redis is still loading the dataset from disk",
                doc="banco-de-dados")
        return QueryError(texto, doc="banco-de-dados")

    def comando(self, *partes):
        """Manda um comando e devolve a resposta."""
        if self._fechado:
            from ...errors import StateError
            raise StateError("this Redis connection is closed.",
                             dica="open a new one with Forge.conectar(...)",
                             doc="banco-de-dados")
        self.canal.escrever(self._codificar(partes))
        return self._ler_resposta()

    def pipeline(self, comandos):
        """Varios comandos numa ida so.

        Cem SETs em cem idas custam cem vezes a latencia da rede; numa
        ida so, custam uma. E a otimizacao mais eficaz que existe com
        Redis, e a razao de o driver expor isto e nao so 'comando'.
        """
        if not comandos:
            return []
        self.canal.escrever(b"".join(self._codificar(c) for c in comandos))
        saida = []
        for _ in comandos:
            try:
                saida.append(self._ler_resposta())
            except DatabaseError as e:
                # Numa pipeline, o erro de um comando nao invalida os
                # outros: cada resposta vale por si.
                saida.append({"erro": str(getattr(e, "message", e))})
        return saida

    def transacao(self, comandos):
        """MULTI/EXEC — todos aplicam, ou nenhum."""
        pacote = [("MULTI",)] + list(comandos) + [("EXEC",)]
        respostas = self.pipeline(pacote)
        return respostas[-1] if respostas else []

    # ── ciclo de vida ───────────────────────────────────────

    def ping(self):
        return self.comando("PING") == "PONG"

    def info(self):
        """O INFO do servidor como vault, e nao como texto de 200 linhas."""
        bruto = self.comando("INFO") or ""
        dados = {}
        secao = "geral"
        for linha in bruto.splitlines():
            linha = linha.strip()
            if not linha:
                continue
            if linha.startswith("#"):
                secao = linha[1:].strip().lower()
                continue
            if ":" in linha:
                chave, valor = linha.split(":", 1)
                dados[f"{secao}.{chave}"] = valor
        return dados

    def fechar(self):
        if not self._fechado:
            self._fechado = True
            try:
                self.canal.escrever(self._codificar(("QUIT",)))
            except Exception:                       # noqa: BLE001
                pass
            self.canal.fechar()

    # ── a interface comum dos drivers do Forge ──────────────
    #
    # Redis nao tem SQL, e fingir que tem seria mentir. O que ele tem e
    # chave-valor, e e isso que estes metodos expoem. 'consultar' existe
    # so para o codigo que troca de motor nao quebrar: manda o comando
    # cru e devolve o que vier.

    def consultar(self, comando, parametros=None):
        partes = comando.split() if isinstance(comando, str) else list(comando)
        partes.extend(parametros or [])
        resposta = self.comando(*partes)
        if isinstance(resposta, list):
            return [{"valor": v} for v in resposta]
        return [{"valor": resposta}]

    def executar(self, comando, parametros=None):
        return self.consultar(comando, parametros)

    @property
    def dialeto(self):
        return "redis"
