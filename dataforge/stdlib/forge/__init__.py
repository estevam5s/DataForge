"""
Forge — o banco de dados do DataForge.

Um nome, cinco motores, a mesma interface:

    adopt Forge

    db := Forge.conectar("postgres://usuario:senha@localhost/app")
    db := Forge.conectar("mysql://root@localhost/app")
    db := Forge.conectar("mongodb://localhost/app")
    db := Forge.conectar("redis://localhost")
    db := Forge.conectar("dados.db")               // SQLite

Trocar o motor troca a URL, e mais nada. As consultas, o construtor e
os modelos continuam iguais — o que muda por baixo (dialeto de SQL,
marca de parametro, forma do erro) fica escondido.

─── Como isto e possivel sem dependencia nenhuma ───────────

Cada driver fala o protocolo do seu banco, por socket. Nao ha
psycopg2, PyMySQL, redis-py nem pymongo aqui: ha 'postgres.py',
'mysql.py', 'redis.py' e 'mongo.py', cada um implementando o protocolo
publicado do seu servidor.

O custo foi escreve-los. O que se ganha e que 'pip install dataforge'
funciona numa maquina sem compilador, e que a versao do driver nunca
briga com a de outro pacote.

─── O que NAO se finge aqui ────────────────────────────────

Redis nao tem SQL, e Mongo nao tem junção. A interface comum cobre o
que faz sentido em todos — conectar, consultar, fechar — e cada motor
expoe o resto pelo que ele e. Um ORM que finge que Redis e uma tabela
produz codigo que parece portavel e nao e.
"""

from .protocolo import analisar_url, MOTORES, PORTAS
from .consulta import Consulta, DIALETOS
from .orm import (Campo, Migracoes, Modelo, REGISTRO, RegistroDeModelos,
                  Relacao, TIPOS_SQL, sql_do_tipo)
from ...errors import ConnectionError_, DatabaseError, PoolExhaustedError


# ═════════════════════════════════════════════════════════════
#  Abertura
# ═════════════════════════════════════════════════════════════

def conectar(url, **opcoes):
    """Abre uma conexao. O motor sai da URL.

    Aceita tambem um caminho solto, que e SQLite:

        Forge.conectar("dados.db")
        Forge.conectar(":memory:")
    """
    dados = analisar_url(str(url))
    motor = dados["motor"]
    prazo = float(opcoes.get("prazo", 10.0))
    tls = _verdade(opcoes.get("tls", dados["opcoes"].get("tls")))

    if motor == "sqlite":
        from .sqlite import SQLite
        return SQLite(dados["caminho"] or ":memory:", prazo=prazo)

    if motor == "postgres":
        from .postgres import Postgres
        return Postgres(
            dados["host"], dados["porta"], dados["usuario"] or "postgres",
            dados["senha"], dados["banco"] or "postgres", tls=tls, prazo=prazo,
            opcoes={k: v for k, v in dados["opcoes"].items() if k != "tls"})

    if motor in ("mysql", "mariadb"):
        from .mysql import MySQL
        return MySQL(
            dados["host"], dados["porta"], dados["usuario"] or "root",
            dados["senha"], dados["banco"], tls=tls, prazo=prazo, sabor=motor)

    if motor == "redis":
        from .redis import Redis
        return Redis(
            dados["host"], dados["porta"], dados["senha"], dados["usuario"],
            banco=dados["banco"] or 0, tls=tls, prazo=prazo)

    if motor == "mongo":
        from .mongo import Mongo
        return Mongo(
            dados["host"], dados["porta"], dados["usuario"], dados["senha"],
            dados["banco"] or "admin", tls=tls, prazo=prazo,
            autenticar_em=dados["opcoes"].get("authSource", ""))

    raise DatabaseError(f"no driver for '{motor}'.", doc="banco-de-dados")


def _verdade(valor):
    if isinstance(valor, bool):
        return valor
    return str(valor or "").lower() in ("1", "yes", "sim", "true", "on")


def memoria():
    """Um SQLite em memoria — o banco de teste que nao deixa rastro."""
    from .sqlite import SQLite
    return SQLite(":memory:")


# ═════════════════════════════════════════════════════════════
#  Pool
# ═════════════════════════════════════════════════════════════

class Pool:
    """Um punhado de conexoes reaproveitadas.

    Abrir conexao custa: TCP, autenticacao, negociacao. Numa rota web
    isso acontece por requisicao, e passa a dominar o tempo de resposta.

    O pool nao e so cache: e tambem limite. Sem teto, um pico de
    trafego abre mil conexoes e o servidor de banco recusa TODAS —
    inclusive as do que ja estava funcionando. Melhor a milesima
    requisicao esperar do que as mil falharem.
    """

    def __init__(self, url, tamanho=5, prazo_espera=10.0, **opcoes):
        import queue
        import threading

        self.url = url
        self.tamanho = max(1, int(tamanho))
        self.prazo_espera = prazo_espera
        self.opcoes = opcoes
        self.disponiveis = queue.LifoQueue()
        self.trava = threading.Lock()
        self.abertas = 0
        self._fechado = False

    def pegar(self):
        """Uma conexao do pool; abre uma nova se ainda couber."""
        import queue

        if self._fechado:
            from ...errors import StateError
            raise StateError("this pool is closed.", doc="banco-de-dados")

        try:
            return self.disponiveis.get_nowait()
        except queue.Empty:
            pass

        with self.trava:
            if self.abertas < self.tamanho:
                self.abertas += 1
                try:
                    return conectar(self.url, **self.opcoes)
                except Exception:
                    self.abertas -= 1
                    raise

        try:
            return self.disponiveis.get(timeout=self.prazo_espera)
        except queue.Empty:
            raise PoolExhaustedError(
                f"all {self.tamanho} connections are busy, and none freed "
                f"up in {self.prazo_espera:.0f}s.",
                nota="a connection taken and never returned looks like this",
                dica=("use  with Forge.conexao(pool) as db:  so it goes back "
                      "on its own, or raise the pool size"),
                doc="banco-de-dados") from None

    def devolver(self, conexao):
        if self._fechado:
            conexao.fechar()
            return
        # Uma conexao devolvida no meio de uma transacao contamina o
        # proximo que a pegar. Desfazer antes e o unico jeito seguro.
        if getattr(conexao, "em_transacao", False):
            try:
                conexao.desfazer()
            except Exception:                        # noqa: BLE001
                conexao.fechar()
                with self.trava:
                    self.abertas -= 1
                return
        self.disponiveis.put(conexao)

    def fechar(self):
        import queue
        self._fechado = True
        while True:
            try:
                self.disponiveis.get_nowait().fechar()
            except queue.Empty:
                break
        self.abertas = 0

    def estado(self):
        return {"tamanho": self.tamanho, "abertas": self.abertas,
                "livres": self.disponiveis.qsize()}


class _ConexaoEmprestada:
    """O 'with' que devolve a conexao ao pool sozinho."""

    def __init__(self, pool):
        self.pool = pool
        self.conexao = None

    def __enter__(self):
        self.conexao = self.pool.pegar()
        return self.conexao

    def __exit__(self, *_):
        if self.conexao is not None:
            self.pool.devolver(self.conexao)
        return False


# ═════════════════════════════════════════════════════════════
#  Transacao com bloco
# ═════════════════════════════════════════════════════════════

def transacao(conexao, corpo):
    """Roda o corpo numa transacao: confirma no fim, desfaz se falhar.

    E a unica forma que nao deixa transacao aberta por engano. Um
    'comecar()' com um 'confirmar()' esquecido segura locks ate a
    conexao cair — e o motivo mais comum de um banco travar em
    producao.
    """
    conexao.comecar()
    try:
        resultado = corpo(conexao)
    except BaseException:
        conexao.desfazer()
        raise
    conexao.confirmar()
    return resultado


# ═════════════════════════════════════════════════════════════
#  A fachada que o DataForge ve
# ═════════════════════════════════════════════════════════════

class ArcaneForge(dict):
    """Forge — bancos de dados, construtor de consultas e ORM."""

    def __new__(cls):
        return {
            # ── conexao ──
            "conectar": conectar,
            "memoria": memoria,
            "url": analisar_url,
            "motores": lambda: sorted(set(MOTORES.values())),
            "pool": lambda url, tamanho=5, **o: Pool(url, tamanho, **o),
            "conexao": lambda pool: _ConexaoEmprestada(pool),

            # ── consultas ──
            "de": cls._de,
            "tabela": cls._de,
            "consultar": cls._consultar,
            "executar": cls._executar,
            "primeiro": cls._primeiro,
            "transacao": transacao,

            # ── modelos ──
            "modelo": cls._modelo,
            "ligar": cls._ligar,
            "migrar_tudo": cls._migrar_tudo,
            "modelos": lambda: [m.nome for m in REGISTRO.todos()],
            "buscar_modelo": REGISTRO.modelo,
            "limpar_modelos": REGISTRO.limpar,

            # ── migracoes ──
            "migracoes": lambda conexao: Migracoes(conexao),

            # ── esquema ──
            "tabelas": lambda db: db.tabelas(),
            "colunas": lambda db, t: db.colunas(t),
            "tipos": lambda: sorted(TIPOS_SQL),
            "dialetos": lambda: sorted(DIALETOS),

            # ── utilidades ──
            "ping": lambda db: db.ping(),
            "versao": lambda db: db.versao(),
            "fechar": lambda db: db.fechar(),
            "para_csv": cls._para_csv,
            "de_csv": cls._de_csv,
        }

    # ── consultas ──

    @staticmethod
    def _de(conexao, tabela):
        return Consulta(conexao, tabela)

    @staticmethod
    def _consultar(conexao, sql, parametros=None):
        return conexao.consultar(sql, parametros)

    @staticmethod
    def _executar(conexao, sql, parametros=None):
        return conexao.executar(sql, parametros)

    @staticmethod
    def _primeiro(conexao, sql, parametros=None):
        linhas = conexao.consultar(sql, parametros)
        return linhas[0] if linhas else None

    # ── modelos ──

    @staticmethod
    def _modelo(nome, campos=None, opcoes=None):
        """Declara um modelo pela forma de biblioteca.

            Forge.modelo("Usuario", {
                "id": {"tipo": "Serial"},
                "email": {"tipo": "Texto", "unico": yes, "obrigatorio": yes,
                          "validacoes": ["email"]},
            })
        """
        o = opcoes or {}
        modelo = Modelo(nome, o.get("tabela", ""), o.get("conexao"))
        for campo, definicao in (campos or {}).items():
            if isinstance(definicao, str):
                definicao = {"tipo": definicao}
            modelo.campo(campo, definicao.get("tipo", "Texto"),
                         obrigatorio=bool(definicao.get("obrigatorio")),
                         unico=bool(definicao.get("unico")),
                         padrao=definicao.get("padrao"),
                         indice=bool(definicao.get("indice")),
                         chave=bool(definicao.get("chave")),
                         referencia=definicao.get("referencia", ""),
                         validacoes=definicao.get("validacoes", []),
                         tamanho=int(definicao.get("tamanho", 0) or 0))
        if o.get("marcas_de_tempo"):
            modelo.com_marcas_de_tempo()
        if o.get("remocao_suave"):
            modelo.com_remocao_suave()
        return REGISTRO.registrar(modelo)

    @staticmethod
    def _ligar(modelo, conexao):
        """Liga um modelo — ou todos — a uma conexao."""
        if isinstance(modelo, str):
            modelo = REGISTRO.modelo(modelo)
        if modelo is None:
            raise DatabaseError("no such model.", doc="orm")
        modelo.conexao = conexao
        return modelo

    @staticmethod
    def _migrar_tudo(conexao):
        return REGISTRO.migrar_tudo(conexao)

    # ── importar e exportar ──

    @staticmethod
    def _para_csv(linhas, caminho=""):
        import csv
        import io
        if not linhas:
            return ""
        saida = io.StringIO()
        escritor = csv.DictWriter(saida, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)
        texto = saida.getvalue()
        if caminho:
            with open(caminho, "w", encoding="utf-8", newline="") as f:
                f.write(texto)
        return texto

    @staticmethod
    def _de_csv(caminho_ou_texto):
        import csv
        import io
        import os
        if os.path.isfile(str(caminho_ou_texto)):
            with open(caminho_ou_texto, encoding="utf-8") as f:
                return list(csv.DictReader(f))
        return list(csv.DictReader(io.StringIO(str(caminho_ou_texto))))
