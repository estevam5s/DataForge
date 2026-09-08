"""Forge — bancos de dados, construtor de consultas e ORM.

Os testes que precisam de servidor pulam quando ele nao esta no ar:
uma suite que exige Docker para rodar deixa de ser rodada. Os que
valem para todos os motores rodam sobre SQLite, que nao precisa de
nada — e o mesmo codigo, porque a interface e a mesma.

Para rodar tambem contra os servidores reais:

    docker run -d -p 15432:5432 -e POSTGRES_PASSWORD=forge \\
        -e POSTGRES_USER=forge -e POSTGRES_DB=forge postgres:16
    docker run -d -p 16379:6379 redis:7-alpine
    docker run -d -p 17017:27017 mongo:7
"""

import os
import socket
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import (ConstraintError, DatabaseError, QueryError,  # noqa: E402
                              RecordNotFoundError, SchemaError,
                              TransactionError, ValidationError)
from dataforge.stdlib.forge import (ArcaneForge, Consulta, Migracoes,  # noqa: E402
                                    Modelo, Pool, REGISTRO, conectar,
                                    memoria, transacao)
from dataforge.stdlib.forge.protocolo import analisar_url  # noqa: E402


def no_ar(host, porta):
    """O servidor esta respondendo? Sem isso, o teste pula."""
    try:
        with socket.create_connection((host, porta), timeout=0.4):
            return True
    except OSError:
        return False


PG = "postgres://forge:forge@localhost:15432/forge"
REDIS = ("localhost", 16379)
MONGO = ("localhost", 17017)

precisa_pg = pytest.mark.skipif(
    not no_ar("localhost", 15432), reason="PostgreSQL de teste nao esta no ar")
precisa_redis = pytest.mark.skipif(
    not no_ar(*REDIS), reason="Redis de teste nao esta no ar")
precisa_mongo = pytest.mark.skipif(
    not no_ar(*MONGO), reason="MongoDB de teste nao esta no ar")


@pytest.fixture
def db():
    conexao = memoria()
    yield conexao
    conexao.fechar()


@pytest.fixture(autouse=True)
def registro_limpo():
    REGISTRO.limpar()
    yield
    REGISTRO.limpar()


# ═══ URL ═══════════════════════════════════════════════════

@pytest.mark.parametrize("url, motor, porta", [
    ("postgres://u:s@h:5432/b", "postgres", 5432),
    ("postgresql://u@h/b", "postgres", 5432),
    ("pg://u@h/b", "postgres", 5432),
    ("mysql://u@h/b", "mysql", 3306),
    ("mariadb://u@h/b", "mariadb", 3306),
    ("redis://h", "redis", 6379),
    ("mongodb://h/b", "mongo", 27017),
])
def test_url_reconhece_o_motor_e_a_porta_padrao(url, motor, porta):
    dados = analisar_url(url)
    assert dados["motor"] == motor
    assert dados["porta"] == porta


def test_caminho_solto_e_sqlite():
    """'conectar("dados.db")' nao deveria exigir um esquema."""
    assert analisar_url("dados.db")["motor"] == "sqlite"
    assert analisar_url(":memory:")["motor"] == "sqlite"


def test_url_com_senha_escapada():
    dados = analisar_url("postgres://u:se%40nha@h/b")
    assert dados["senha"] == "se@nha"


def test_motor_desconhecido_lista_os_conhecidos():
    with pytest.raises(DatabaseError) as exc:
        analisar_url("oracle://h/b")
    assert "postgres" in exc.value.nota


# ═══ SQLite: a interface comum ═════════════════════════════

def test_consultar_devolve_vaults(db):
    db.executar("create table t (id integer primary key, nome text)")
    db.executar("insert into t (nome) values (?)", ["Ana"])
    assert db.consultar("select * from t") == [{"id": 1, "nome": "Ana"}]


def test_executar_devolve_quantas_mudaram(db):
    db.executar("create table t (id integer primary key, n int)")
    db.executar("insert into t (n) values (1), (2), (3)")
    assert db.executar("update t set n = n + 1") == 3


def test_erro_de_restricao_e_tipado(db):
    db.executar("create table t (id integer primary key, e text unique)")
    db.executar("insert into t (e) values (?)", ["a@b.c"])
    with pytest.raises(ConstraintError):
        db.executar("insert into t (e) values (?)", ["a@b.c"])


def test_tabela_inexistente_ensina_a_migrar(db):
    with pytest.raises(QueryError) as exc:
        db.consultar("select * from naoexiste")
    assert "migrar" in exc.value.dica


def test_transacao_desfaz_no_erro(db):
    db.executar("create table t (id integer primary key, n int)")

    def falha(conexao):
        conexao.executar("insert into t (n) values (1)")
        raise ValueError("proposital")

    with pytest.raises(ValueError):
        transacao(db, falha)
    assert db.consultar("select * from t") == []


def test_transacao_confirma_no_sucesso(db):
    db.executar("create table t (id integer primary key, n int)")
    transacao(db, lambda c: c.executar("insert into t (n) values (1)"))
    assert len(db.consultar("select * from t")) == 1


def test_confirmar_sem_transacao_explica(db):
    with pytest.raises(TransactionError) as exc:
        db.confirmar()
    assert "comecar" in exc.value.dica


# ═══ O construtor de consultas ═════════════════════════════

class ConexaoFalsa:
    """Registra o SQL sem ir a banco nenhum."""

    def __init__(self, dialeto="postgres"):
        self.dialeto = dialeto
        self.ultimo = None

    def consultar(self, sql, valores=None):
        self.ultimo = (sql, valores)
        return []

    def executar(self, sql, valores=None):
        self.ultimo = (sql, valores)
        return 0


def montar(tabela="t", dialeto="postgres"):
    return Consulta(ConexaoFalsa(dialeto), tabela, dialeto)


def test_valores_nunca_entram_no_texto():
    """A garantia central: e o que torna injecao impossivel."""
    sql, valores = montar().onde("nome", "'; drop table t; --").montar()
    assert "drop table" not in sql
    assert valores == ["'; drop table t; --"]


def test_marca_de_parametro_segue_o_dialeto():
    assert "$1" in montar(dialeto="postgres").onde("a", 1).montar()[0]
    assert "?" in montar(dialeto="mysql").onde("a", 1).montar()[0]
    assert "?" in montar(dialeto="sqlite").onde("a", 1).montar()[0]


def test_identificador_e_citado():
    """Uma coluna chamada 'order' quebraria a consulta."""
    sql, _ = montar().selecionar("order").montar()
    assert '"order"' in sql


def test_operador_vindo_de_texto_e_recusado():
    """A lista fechada e o que fecha esse caminho de injecao."""
    with pytest.raises(QueryError) as exc:
        montar().onde("a", "; drop table t--", 1)
    assert "operator" in str(exc.value)


def test_igual_a_void_vira_is_null():
    """'x = NULL' nunca e verdadeiro em SQL, nem quando x e nulo."""
    sql, valores = montar().onde("a", "=", None).montar()
    assert "IS NULL" in sql
    assert valores == []


def test_in_com_lista_vazia_nao_gera_sintaxe_invalida():
    """'in ()' e erro de sintaxe em quase todo banco."""
    sql, _ = montar().onde_em("a", []).montar()
    assert "1 = 0" in sql


def test_quando_aplica_so_se_a_condicao_valer():
    com = montar().quando(True, lambda c: c.onde("a", 1)).montar()[1]
    sem = montar().quando(False, lambda c: c.onde("a", 1)).montar()[1]
    assert com == [1] and sem == []


def test_pagina_um_e_a_primeira():
    """Off-by-one em paginacao e classico."""
    sql, _ = montar().pagina(1, 20).montar()
    assert "OFFSET 0" in sql
    sql, _ = montar().pagina(2, 20).montar()
    assert "OFFSET 20" in sql


def test_update_sem_where_e_recusado():
    with pytest.raises(QueryError) as exc:
        montar().atualizar({"a": 1})
    assert "every row" in str(exc.value)


def test_delete_sem_where_e_recusado():
    with pytest.raises(QueryError) as exc:
        montar().remover()
    assert "empty the table" in str(exc.value)


def test_apagar_tudo_de_proposito_e_permitido():
    """A recusa acima protege do engano, nao da intencao."""
    conexao = ConexaoFalsa()
    Consulta(conexao, "t").remover_tudo()
    assert "DELETE FROM" in conexao.ultimo[0]


def test_construtor_roda_de_verdade(db):
    db.executar("create table p (id integer primary key, nome text, preco real)")
    Consulta(db, "p").inserir([
        {"nome": "a", "preco": 10.0},
        {"nome": "b", "preco": 20.0},
        {"nome": "c", "preco": 30.0}])
    assert Consulta(db, "p").onde("preco", ">=", 20).contar() == 2
    assert Consulta(db, "p").somar("preco") == 60.0
    assert Consulta(db, "p").ordenar("preco", "desc").primeiro()["nome"] == "c"
    assert Consulta(db, "p").valores("nome") == ["a", "b", "c"]


def test_paginar_devolve_os_numeros_da_interface(db):
    db.executar("create table p (id integer primary key, n int)")
    Consulta(db, "p").inserir([{"n": i} for i in range(25)])
    pagina = Consulta(db, "p").paginar(2, 10)
    assert pagina["total"] == 25
    assert pagina["paginas"] == 3
    assert len(pagina["linhas"]) == 10
    assert pagina["tem_proxima"] and pagina["tem_anterior"]


def test_incrementar_soma_no_banco(db):
    """Ler-somar-gravar perde atualizacoes concorrentes; isto nao."""
    db.executar("create table c (id integer primary key, n int)")
    Consulta(db, "c").inserir({"n": 5})
    Consulta(db, "c").onde("id", 1).incrementar("n", 3)
    assert Consulta(db, "c").onde("id", 1).primeiro()["n"] == 8


# ═══ O ORM ═════════════════════════════════════════════════

def modelo_usuario(db):
    m = REGISTRO.registrar(Modelo("Usuario", conexao=db))
    m.campo("id", "Serial")
    m.campo("email", "Texto", obrigatorio=True, unico=True,
            validacoes=["email"])
    m.campo("nome", "Texto", obrigatorio=True, validacoes=[("minimo", 2)])
    m.campo("idade", "Inteiro", padrao=0,
            validacoes=[("minimo", 0), ("maximo", 130)])
    m.campo("ativo", "Booleano", padrao=True)
    m.campo("perfil", "Json")
    return m


def test_plural_da_tabela():
    assert Modelo("Usuario").tabela == "usuarios"
    assert Modelo("Pedido").tabela == "pedidos"
    assert Modelo("Animal").tabela == "animais"
    assert Modelo("Coracao").tabela == "coracoes"
    assert Modelo("Item", "coisas").tabela == "coisas"


def test_migrar_cria_a_tabela(db):
    modelo_usuario(db).migrar()
    assert "usuarios" in db.tabelas()


def test_criar_valida_e_devolve_a_linha(db):
    m = modelo_usuario(db)
    m.migrar()
    criado = m.criar({"email": "ana@x.com", "nome": "Ana", "idade": 30})
    assert criado["id"] == 1
    assert criado["email"] == "ana@x.com"


def test_validacao_junta_todos_os_problemas(db):
    """Um formulario que aponta um erro por vez custa cinco tentativas."""
    m = modelo_usuario(db)
    m.migrar()
    with pytest.raises(ValidationError) as exc:
        m.criar({"email": "nao-e-email", "nome": "X", "idade": 999})
    campos = {p["campo"] for p in exc.value.campos}
    assert campos == {"email", "nome", "idade"}


def test_campo_desconhecido_e_recusado(db):
    m = modelo_usuario(db)
    m.migrar()
    with pytest.raises(ValidationError) as exc:
        m.criar({"email": "a@b.co", "nome": "Ana", "inventado": 1})
    assert any(p["campo"] == "inventado" for p in exc.value.campos)


def test_tipos_voltam_convertidos(db):
    """SQLite guarda booleano como 0 e 1; sem converter, tudo e verdadeiro."""
    m = modelo_usuario(db)
    m.migrar()
    m.criar({"email": "a@b.co", "nome": "Ana", "ativo": False,
             "perfil": {"tema": "escuro"}})
    lido = m.buscar(1)
    assert lido["ativo"] is False
    assert lido["perfil"] == {"tema": "escuro"}
    assert isinstance(lido["idade"], int)


def test_buscar_ou_erro(db):
    m = modelo_usuario(db)
    m.migrar()
    assert m.buscar(999) is None
    with pytest.raises(RecordNotFoundError):
        m.buscar_ou_erro(999)


def test_atualizar_valida_parcialmente(db):
    m = modelo_usuario(db)
    m.migrar()
    m.criar({"email": "a@b.co", "nome": "Ana"})
    atualizado = m.atualizar(1, {"idade": 31})
    assert atualizado["idade"] == 31
    with pytest.raises(ValidationError):
        m.atualizar(1, {"idade": 999})


def test_criar_ou_atualizar(db):
    m = modelo_usuario(db)
    m.migrar()
    m.criar_ou_atualizar({"email": "a@b.co"}, {"nome": "Ana"})
    m.criar_ou_atualizar({"email": "a@b.co"}, {"nome": "Ana Maria"})
    assert m.contar() == 1
    assert m.primeiro(email="a@b.co")["nome"] == "Ana Maria"


def test_marcas_de_tempo(db):
    m = modelo_usuario(db).com_marcas_de_tempo()
    m.migrar()
    criado = m.criar({"email": "a@b.co", "nome": "Ana"})
    assert criado["criado_em"] and criado["atualizado_em"]


def test_remocao_suave_esconde_sem_apagar(db):
    m = modelo_usuario(db).com_remocao_suave()
    m.migrar()
    m.criar({"email": "a@b.co", "nome": "Ana"})
    m.remover(1)
    assert m.contar() == 0
    assert len(db.consultar("select * from usuarios")) == 1


def test_ganchos_rodam(db):
    m = modelo_usuario(db)
    m.migrar()
    vistos = []
    m.antes_de_salvar(lambda d: {**d, "nome": d["nome"].upper()})
    m.depois_de_salvar(lambda linha: vistos.append(linha["id"]))
    criado = m.criar({"email": "a@b.co", "nome": "Ana"})
    assert criado["nome"] == "ANA"
    assert vistos == [1]


# ═══ Relacoes ══════════════════════════════════════════════

def montar_relacionados(db):
    u = modelo_usuario(db)
    u.tem_muitos("pedidos", "Pedido")
    p = REGISTRO.registrar(Modelo("Pedido", conexao=db))
    p.campo("id", "Serial").campo("usuario_id", "Inteiro")
    p.campo("total", "Real", padrao=0)
    p.pertence_a("usuario", "Usuario")
    REGISTRO.migrar_tudo(db)

    ana = u.criar({"email": "ana@x.com", "nome": "Ana"})
    bia = u.criar({"email": "bia@x.com", "nome": "Bia"})
    p.criar({"usuario_id": ana["id"], "total": 10.0})
    p.criar({"usuario_id": ana["id"], "total": 20.0})
    p.criar({"usuario_id": bia["id"], "total": 5.0})
    return u, p


def test_tem_muitos_carrega_de_uma_vez(db):
    u, _ = montar_relacionados(db)
    usuarios = u.com(u.todos(), "pedidos")
    assert [len(x["pedidos"]) for x in usuarios] == [2, 1]


def test_carregar_relacao_nao_faz_n_mais_um(db):
    """Cem usuarios com 'pedidos' devem custar DUAS consultas, nao 101."""
    u, p = montar_relacionados(db)

    consultas = []
    original = db.consultar

    def contando(sql, valores=None):
        consultas.append(sql)
        return original(sql, valores)

    db.consultar = contando
    u.com(u.todos(), "pedidos")
    db.consultar = original
    assert len(consultas) == 2, f"fez {len(consultas)} consultas: {consultas}"


def test_pertence_a(db):
    _, p = montar_relacionados(db)
    pedidos = p.com(p.todos(), "usuario")
    assert pedidos[0]["usuario"]["nome"] == "Ana"


def test_relacao_desconhecida_lista_as_que_existem(db):
    u, _ = montar_relacionados(db)
    with pytest.raises(SchemaError) as exc:
        u.com(u.todos(), "inventada")
    assert "pedidos" in exc.value.nota


def test_relacao_sem_pais_devolve_lista_vazia(db):
    u, _ = montar_relacionados(db)
    db.executar("delete from pedidos")
    usuarios = u.com(u.todos(), "pedidos")
    assert all(x["pedidos"] == [] for x in usuarios)


# ═══ Esquema e migracoes ═══════════════════════════════════

def test_diferenca_ve_a_coluna_que_falta(db):
    m = modelo_usuario(db)
    m.migrar()
    m.campo("telefone", "Texto")
    assert m.diferenca()["colunas_faltando"] == ["telefone"]


def test_aplicar_diferenca_cria_a_coluna(db):
    m = modelo_usuario(db)
    m.migrar()
    m.campo("telefone", "Texto")
    m.aplicar_diferenca()
    assert m.diferenca()["colunas_faltando"] == []


def test_aplicar_diferenca_nunca_apaga(db):
    """Perda de dado nao se automatiza."""
    m = modelo_usuario(db)
    m.migrar()
    del m.campos["perfil"]
    resultado = m.aplicar_diferenca()
    assert "perfil" in resultado["colunas_a_mais"]
    assert "perfil" in {c["nome"] for c in db.colunas("usuarios")}


def test_migracoes_guardam_o_historico_no_banco(db):
    m = Migracoes(db)
    m.passo("001", lambda c: c.executar("create table a (id int)"),
            lambda c: c.executar("drop table a"))
    m.passo("002", lambda c: c.executar("create table b (id int)"))
    assert m.subir() == ["001", "002"]
    assert m.aplicadas() == ["001", "002"]
    assert m.pendentes() == []
    assert m.subir() == []                    # rodar de novo nao repete


def test_migracao_que_falha_para_e_diz_onde(db):
    m = Migracoes(db)
    m.passo("001", lambda c: c.executar("create table a (id int)"))
    m.passo("002", lambda c: c.executar("isto nao e sql"))
    m.passo("003", lambda c: c.executar("create table c (id int)"))
    from dataforge.errors import MigrationError
    with pytest.raises(MigrationError) as exc:
        m.subir()
    assert "002" in str(exc.value)
    assert "c" not in db.tabelas()             # a 003 nao rodou


def test_descer_desfaz(db):
    m = Migracoes(db)
    m.passo("001", lambda c: c.executar("create table a (id int)"),
            lambda c: c.executar("drop table a"))
    m.subir()
    assert m.descer(1) == ["001"]
    assert "a" not in db.tabelas()


def test_descer_sem_caminho_de_volta_explica(db):
    from dataforge.errors import MigrationError
    m = Migracoes(db)
    m.passo("001", lambda c: c.executar("create table a (id int)"))
    m.subir()
    with pytest.raises(MigrationError) as exc:
        m.descer(1)
    assert "descer" in exc.value.dica


def test_sql_criar_muda_com_o_dialeto():
    m = Modelo("Usuario")
    m.campo("id", "Serial").campo("nome", "Texto")
    assert "SERIAL PRIMARY KEY" in m.sql_criar("postgres")
    assert "AUTO_INCREMENT" in m.sql_criar("mysql")
    assert "AUTOINCREMENT" in m.sql_criar("sqlite")


def test_tipo_desconhecido_lista_os_validos():
    m = Modelo("X")
    m.campo("a", "Inventado")
    with pytest.raises(SchemaError) as exc:
        m.sql_criar("sqlite")
    assert "Texto" in exc.value.nota


# ═══ Pool ══════════════════════════════════════════════════

def test_pool_reaproveita():
    pool = Pool(":memory:", tamanho=2)
    a = pool.pegar()
    pool.devolver(a)
    assert pool.pegar() is a
    pool.fechar()


def test_pool_respeita_o_teto():
    from dataforge.errors import PoolExhaustedError
    pool = Pool(":memory:", tamanho=1, prazo_espera=0.2)
    pool.pegar()
    with pytest.raises(PoolExhaustedError) as exc:
        pool.pegar()
    assert "with Forge.conexao" in exc.value.dica
    pool.fechar()


def test_conexao_com_bloco_devolve_sozinha():
    from dataforge.stdlib.forge import _ConexaoEmprestada
    pool = Pool(":memory:", tamanho=1)
    with _ConexaoEmprestada(pool) as conexao:
        assert conexao.ping()
    assert pool.estado()["livres"] == 1
    pool.fechar()


# ═══ A fachada ═════════════════════════════════════════════

def test_a_fachada_expoe_o_que_a_doc_promete():
    forge = ArcaneForge()
    for nome in ("conectar", "memoria", "de", "modelo", "migrar_tudo",
                 "transacao", "pool", "migracoes", "tipos", "motores"):
        assert nome in forge, nome


def test_motores_listados():
    assert set(ArcaneForge()["motores"]()) == {
        "sqlite", "postgres", "mysql", "mariadb", "redis", "mongo"}


# ═══ Servidores reais ══════════════════════════════════════

@precisa_pg
def test_postgres_ponta_a_ponta():
    db = conectar(PG)
    try:
        assert db.ping()
        db.executar("drop table if exists t_forge")
        db.executar("create table t_forge (id serial primary key, "
                    "nome text, dados jsonb, tags text[], ativo boolean)")
        db.executar("insert into t_forge (nome, dados, tags, ativo) "
                    "values (?, ?, ?, ?)",
                    ["Ana", {"a": 1}, ["x", "y"], True])
        linha = db.consultar("select * from t_forge")[0]
        # A conversao de tipo e o que faz 'linha["dados"]["a"]' funcionar.
        assert linha["dados"] == {"a": 1}
        assert linha["tags"] == ["x", "y"]
        assert linha["ativo"] is True
        assert isinstance(linha["id"], int)
        db.executar("drop table t_forge")
    finally:
        db.fechar()


@precisa_pg
def test_postgres_parametriza_de_verdade():
    """A prova de que o valor nao vira texto de consulta."""
    db = conectar(PG)
    try:
        db.executar("drop table if exists t_inj")
        db.executar("create table t_inj (id serial primary key, nome text)")
        db.executar("insert into t_inj (nome) values (?)",
                    ["'; drop table t_inj; --"])
        assert "t_inj" in db.tabelas()
        assert db.consultar("select * from t_inj")[0]["nome"].startswith("';")
        db.executar("drop table t_inj")
    finally:
        db.fechar()


@precisa_pg
def test_postgres_erros_tipados():
    db = conectar(PG)
    try:
        db.executar("drop table if exists t_err")
        db.executar("create table t_err (id serial primary key, e text unique)")
        db.executar("insert into t_err (e) values (?)", ["a"])
        with pytest.raises(ConstraintError):
            db.executar("insert into t_err (e) values (?)", ["a"])
        with pytest.raises(QueryError):
            db.consultar("select * from nao_existe_mesmo")
        db.executar("drop table t_err")
    finally:
        db.fechar()


@precisa_redis
def test_redis_ponta_a_ponta():
    db = conectar(f"redis://{REDIS[0]}:{REDIS[1]}")
    try:
        assert db.ping()
        db.comando("SET", "forge:teste", "valor")
        assert db.comando("GET", "forge:teste") == "valor"
        assert db.comando("INCR", "forge:contador") == 1
        db.comando("RPUSH", "forge:lista", 1, 2, 3)
        assert db.comando("LRANGE", "forge:lista", 0, -1) == ["1", "2", "3"]
        db.comando("DEL", "forge:teste", "forge:contador", "forge:lista")
    finally:
        db.fechar()


@precisa_redis
def test_redis_pipeline_e_uma_ida_so():
    db = conectar(f"redis://{REDIS[0]}:{REDIS[1]}")
    try:
        respostas = db.pipeline([("SET", "a", "1"), ("SET", "b", "2"),
                                 ("MGET", "a", "b")])
        assert respostas[-1] == ["1", "2"]
        db.comando("DEL", "a", "b")
    finally:
        db.fechar()


@precisa_mongo
def test_mongo_ponta_a_ponta():
    db = conectar(f"mongodb://{MONGO[0]}:{MONGO[1]}/forge_teste")
    try:
        assert db.ping()
        db.apagar_colecao("t")
        r = db.inserir("t", [{"nome": "Ana", "idade": 30},
                             {"nome": "Bia", "idade": 25}])
        assert r["inseridos"] == 2
        assert db.contar("t") == 2
        assert db.achar_um("t", {"nome": "Ana"})["idade"] == 30
        # A busca por _id como texto tem de funcionar: e assim que ele sai.
        assert db.achar_um("t", {"_id": r["ids"][0]})["nome"] == "Ana"
        db.atualizar("t", {"nome": "Bia"}, {"idade": 26})
        assert db.achar_um("t", {"nome": "Bia"})["idade"] == 26
        assert db.agregar("t", [{"$group": {"_id": None,
                                            "m": {"$avg": "$idade"}}}])[0]["m"] == 28.0
        db.apagar_colecao("t")
    finally:
        db.fechar()


@precisa_mongo
def test_bson_ida_e_volta():
    """Um documento que sai e volta diferente corrompe dados em silencio."""
    import datetime
    from dataforge.stdlib.forge.bson import codificar, decodificar, ObjectId

    original = {"_id": ObjectId(), "texto": "acentuação", "n": 42,
                "grande": 2 ** 40, "real": 1.5, "sim": True, "nada": None,
                "lista": [1, "dois", {"tres": 3}], "vault": {"a": [1, 2]},
                "bytes": b"\x00\x01\xff"}
    volta = decodificar(codificar(original))
    assert volta == original
