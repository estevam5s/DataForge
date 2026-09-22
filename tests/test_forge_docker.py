# -*- coding: utf-8 -*-
"""O banco em contêiner, e os três recursos de ORM que faltavam.

─── Por que metade destes testes sobe um contêiner ─────────────

Os drivers deste repositório falam o protocolo do banco **por
socket** — `postgres.py`, `mysql.py`, `redis.py` e `mongo.py` são
implementações próprias, sem psycopg nem PyMySQL. Um driver assim,
testado só contra um dublê, prova que os métodos existem: o que
quebra na prática é o aperto de mão, a autenticação e o
enquadramento, e nada disso aparece sem o outro lado de verdade.

É a mesma decisão de `tests/test_malha.py`, que sobe um servidor
HTTP que se comporta mal de propósito.

─── E por que a outra metade não sobe ──────────────────────────

`compose()` e `de_ambiente()` são lógica pura: URL entra, dicionário
sai. Exigir Docker para exercitá-las tornaria caro um teste barato, e
um teste caro é um teste que alguém pula.

Sem Docker, os que precisam dele são **pulados** — e o que sobra
ainda cobre a maior parte.
"""

import os
import shutil
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib import get_module  # noqa: E402

F = get_module("Arcane.Forge")


def erro_de(nome):
    from dataforge import errors
    return errors.erro_por_nome(nome)


# ═══════════════════════════════════════════════════════════
#  Sem Docker: a lógica pura
# ═══════════════════════════════════════════════════════════

def test_compose_sai_da_MESMA_url_que_a_aplicacao_usa():
    """Escrever os dois à mão é como eles divergem: o compose sobe
    `POSTGRES_DB=loja` e a aplicação procura `loja_dev`, e o erro só
    aparece na primeira consulta."""
    c = F["compose"]("postgres://ana:segredo@localhost:55432/loja")
    servico = c["definicao"]["banco"]

    assert servico["environment"]["POSTGRES_USER"] == "ana"
    assert servico["environment"]["POSTGRES_PASSWORD"] == "segredo"
    assert servico["environment"]["POSTGRES_DB"] == "loja"
    assert servico["ports"] == ["55432:5432"], (
        "a porta PUBLICADA e a da URL; a interna e a do motor")


def test_o_compose_traz_sonda_de_saude():
    """Sem ela, `depends_on` espera o contêiner COMEÇAR, e não ficar
    pronto — e a aplicação falha na primeira consulta, de forma
    intermitente."""
    for url in ("postgres://a:b@h/x", "mysql://a:b@h/x", "redis://h:6379"):
        c = F["compose"](url)
        sonda = c["definicao"]["banco"]["healthcheck"]
        assert sonda["test"], f"{url} sem sonda"
        assert sonda["start_period"], (
            "sem periodo de partida, as falhas normais da inicializacao "
            "contam como 'nao saudavel' e derrubam o servico")


def test_a_url_interna_troca_host_E_porta():
    """Trocar só o host é o erro clássico de quem publica numa porta
    diferente: por dentro da rede do compose a porta é sempre a do
    motor, e não a publicada."""
    c = F["compose"]("postgres://ana:s@localhost:55432/loja", servico="pg")
    assert c["url_interna"] == "postgres://ana:s@pg:5432/loja"


def test_o_sqlite_nao_vira_conteiner():
    with pytest.raises(erro_de("DatabaseError")) as e:
        F["compose"]("dados.db")
    assert "volume" in e.value.dica.lower()


def test_um_motor_sem_receita_diz_quais_existem():
    with pytest.raises(erro_de("DatabaseError")) as e:
        F["compose"]("oracle://a:b@h/x")
    assert "postgres" in str(e.value) + e.value.nota


def test_de_ambiente_le_a_variavel(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", ":memory:")
    db = F["de_ambiente"]()
    assert F["ping"](db) is True
    F["fechar"](db)


def test_de_ambiente_sem_variavel_e_ERRO_e_nao_um_sqlite_calado(monkeypatch):
    """Cair num SQLite silencioso quando falta a variável é o defeito
    que faz alguém rodar uma semana contra o banco errado."""
    for nome in F["__name__"] and ("DATABASE_URL", "DB_URL", "FORGE_DATABASE_URL"):
        monkeypatch.delenv(nome, raising=False)

    with pytest.raises(erro_de("DatabaseError")) as e:
        F["de_ambiente"]()
    assert "DATABASE_URL" in e.value.nota
    assert "padrao" in e.value.dica


def test_de_ambiente_aceita_um_padrao(monkeypatch):
    for nome in ("DATABASE_URL", "DB_URL", "FORGE_DATABASE_URL"):
        monkeypatch.delenv(nome, raising=False)
    db = F["de_ambiente"](padrao=":memory:")
    assert F["ping"](db) is True
    F["fechar"](db)


def test_esperar_desiste_no_prazo_e_diz_o_ULTIMO_erro():
    """Um "tempo esgotado" genérico manda procurar no lugar errado
    quando a causa era outra."""
    inicio = time.monotonic()
    with pytest.raises(erro_de("DatabaseError")) as e:
        # Porta fechada: a recusa é transitória, então ele insiste.
        F["esperar"]("postgres://a:b@127.0.0.1:1/x", prazo=1.0, intervalo=0.1)
    gasto = time.monotonic() - inicio

    assert 0.9 <= gasto < 6.0, f"desistiu em {gasto:.1f}s"
    assert "ultimo erro" in e.value.nota
    assert "tentativas" in str(e.value)


# ═══════════════════════════════════════════════════════════
#  O ORM, em SQLite — o que não precisa de rede
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def blog():
    F["limpar_modelos"]()
    db = F["memoria"]()
    Autor = F["modelo"]("Autor", {"id": "Serial", "nome": "Texto"})
    Post = F["modelo"]("Post", {"id": "Serial", "autor_id": "Inteiro",
                                "titulo": "Texto", "status": "Texto"})
    Comentario = F["modelo"]("Comentario", {"id": "Serial",
                                            "post_id": "Inteiro",
                                            "texto": "Texto"})
    for m in (Autor, Post, Comentario):
        F["ligar"](m, db)
        m.migrar()
    yield db, Autor, Post, Comentario
    F["fechar"](db)
    F["limpar_modelos"]()


def test_tem_muitos_atraves(blog):
    """O autor não tem comentários: ele tem **posts**, e os posts têm
    comentários. Sem isto, a saída é carregar os posts, tirar os ids e
    consultar de novo — e quem escreve isso tende a fazer uma consulta
    por post, que é o N+1 com um passo a mais."""
    _, Autor, Post, Comentario = blog
    Autor.tem_muitos_atraves("comentarios", "Comentario", "Post")

    ana = Autor.criar({"nome": "Ana"})
    bob = Autor.criar({"nome": "Bob"})
    p1 = Post.criar({"autor_id": ana["id"], "titulo": "Um", "status": "publicado"})
    p2 = Post.criar({"autor_id": bob["id"], "titulo": "Dois", "status": "publicado"})
    for t in ("a", "b", "c"):
        Comentario.criar({"post_id": p1["id"], "texto": t})
    Comentario.criar({"post_id": p2["id"], "texto": "d"})

    autores = Autor.com(Autor.todos(), "comentarios")
    por_nome = {a["nome"]: a for a in autores}
    assert len(por_nome["Ana"]["comentarios"]) == 3
    assert len(por_nome["Bob"]["comentarios"]) == 1


def test_atraves_sem_ninguem_no_meio_devolve_lista_vazia(blog):
    _, Autor, _, _ = blog
    Autor.tem_muitos_atraves("comentarios", "Comentario", "Post")
    Autor.criar({"nome": "Sozinha"})
    assert Autor.com(Autor.todos(), "comentarios")[0]["comentarios"] == []


def test_atraves_com_modelo_do_meio_nao_registrado(blog):
    _, Autor, _, _ = blog
    Autor.tem_muitos_atraves("x", "Comentario", "NaoExiste")
    Autor.criar({"nome": "A"})
    with pytest.raises(erro_de("SchemaError")) as e:
        Autor.com(Autor.todos(), "x")
    assert "NaoExiste" in str(e.value)


def test_o_escopo_e_reaproveitavel_e_encadeavel(blog):
    """Encadear é o que separa um escopo de um atalho."""
    _, _, Post, _ = blog
    Post.escopo("publicados", lambda q: q.onde("status", "publicado"))
    Post.escopo("do_autor_1", lambda q: q.onde("autor_id", 1))

    Post.criar({"autor_id": 1, "titulo": "a", "status": "publicado"})
    Post.criar({"autor_id": 1, "titulo": "b", "status": "rascunho"})
    Post.criar({"autor_id": 2, "titulo": "c", "status": "publicado"})

    assert len(Post.usar("publicados").buscar()) == 2
    assert len(Post.usar("do_autor_1", Post.usar("publicados")).buscar()) == 1


def test_um_escopo_desconhecido_diz_quais_existem(blog):
    _, _, Post, _ = blog
    Post.escopo("publicados", lambda q: q)
    with pytest.raises(erro_de("SchemaError")) as e:
        Post.usar("publicadoss")
    assert "publicados" in e.value.nota


def test_paginar_traz_o_total_e_as_paginas(blog):
    """Sem eles a tela não sabe quantos botões desenhar — e a saída
    comum é buscar tudo para contar, que é o que a paginação existe
    para evitar."""
    _, _, Post, _ = blog
    for i in range(25):
        Post.criar({"autor_id": 1, "titulo": f"P{i}", "status": "publicado"})

    p = Post.paginar(pagina=2, tamanho=10)
    assert len(p["linhas"]) == 10
    assert p["total"] == 25 and p["paginas"] == 3
    assert p["tem_anterior"] is True and p["tem_proxima"] is True

    ultima = Post.paginar(pagina=3, tamanho=10)
    assert len(ultima["linhas"]) == 5
    assert ultima["tem_proxima"] is False


def test_pagina_fora_da_faixa_e_vazia_e_nao_erro(blog):
    """`?pagina=999` é um link antigo, não um ataque — e uma listagem
    que quebra com isso quebra com um favorito de seis meses atrás."""
    _, _, Post, _ = blog
    Post.criar({"autor_id": 1, "titulo": "a", "status": "x"})
    fora = Post.paginar(pagina=999, tamanho=10)
    assert fora["linhas"] == []
    assert fora["tem_proxima"] is False
    assert fora["total"] == 1, "o total continua sendo o de verdade"


def test_paginar_tem_teto_de_tamanho(blog):
    """`?tamanho=999999` é a forma mais barata de derrubar a listagem."""
    _, _, Post, _ = blog
    for i in range(3):
        Post.criar({"autor_id": 1, "titulo": str(i), "status": "x"})
    assert Post.paginar(pagina=1, tamanho=10 ** 9)["tamanho"] <= 500


def test_paginar_sobre_um_escopo(blog):
    _, _, Post, _ = blog
    Post.escopo("publicados", lambda q: q.onde("status", "publicado"))
    for i in range(12):
        Post.criar({"autor_id": 1, "titulo": str(i),
                    "status": "publicado" if i % 2 else "rascunho"})
    p = Post.paginar(pagina=1, tamanho=5, consulta=Post.usar("publicados"))
    assert p["total"] == 6
    assert len(p["linhas"]) == 5


# ═══════════════════════════════════════════════════════════
#  Com Docker: o protocolo de verdade
# ═══════════════════════════════════════════════════════════

def _tem_docker():
    if shutil.which("docker") is None:
        return False
    try:
        return subprocess.run(["docker", "info"], capture_output=True,
                              timeout=20).returncode == 0
    except Exception:                                      # noqa: BLE001
        return False


precisa_docker = pytest.mark.skipif(
    not _tem_docker(),
    reason="Docker nao esta disponivel; os testes de protocolo sao pulados")


@pytest.fixture(scope="module")
def postgres_em_conteiner():
    """Um Postgres de verdade, derrubado no fim.

    O nome tem sufixo do processo: duas execuções em paralelo — o que
    o pytest-xdist faz — colidiriam no nome e na porta, e a segunda
    derrubaria o banco da primeira no meio de um teste.
    """
    if not _tem_docker():
        pytest.skip("sem Docker")

    nome = f"df-teste-pg-{os.getpid()}"
    porta = 55400 + (os.getpid() % 90)
    subprocess.run(["docker", "rm", "-f", nome], capture_output=True)
    criado = subprocess.run(
        ["docker", "run", "-d", "--name", nome,
         "-e", "POSTGRES_PASSWORD=segredo", "-e", "POSTGRES_USER=forge",
         "-e", "POSTGRES_DB=teste", "-p", f"{porta}:5432",
         "postgres:16-alpine"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    if criado.returncode != 0:
        pytest.skip(f"nao consegui subir o conteiner: {criado.stderr[-200:]}")

    url = f"postgres://forge:segredo@localhost:{porta}/teste"
    try:
        yield url
    finally:
        subprocess.run(["docker", "rm", "-f", nome], capture_output=True)


@precisa_docker
@pytest.mark.slow
def test_esperar_conecta_num_conteiner_RECEM_criado(postgres_em_conteiner):
    """"Up" não quer dizer "pronto".

    O contêiner do Postgres sobe, cria o cluster, **reinicia o
    servidor uma vez** durante a inicialização, e só então passa a
    escutar. Quem chama `conectar` direto pega "connection refused" —
    é o defeito de boot mais comum de todo compose.
    """
    db = F["esperar"](postgres_em_conteiner, prazo=60.0)
    assert F["ping"](db) is True
    assert F["versao"](db)
    F["fechar"](db)


@precisa_docker
@pytest.mark.slow
def test_a_credencial_errada_NAO_espera_o_prazo(postgres_em_conteiner):
    """Insistir trinta segundos numa senha inválida é esconder a causa
    atrás de um prazo: ela não melhora com o tempo."""
    F["esperar"](postgres_em_conteiner, prazo=60.0)   # garante que subiu
    ruim = postgres_em_conteiner.replace(":segredo@", ":ERRADA@")

    inicio = time.monotonic()
    with pytest.raises(Exception) as e:
        F["esperar"](ruim, prazo=30.0)
    gasto = time.monotonic() - inicio

    assert gasto < 10.0, f"insistiu {gasto:.1f}s numa senha invalida"
    assert "senha" in str(e.value).lower() or "password" in str(e.value).lower()


@precisa_docker
@pytest.mark.slow
def test_o_driver_de_postgres_fala_o_protocolo(postgres_em_conteiner):
    """O que quebra num driver caseiro é o aperto de mão, a
    autenticação e o enquadramento — e nada disso aparece contra um
    dublê."""
    db = F["esperar"](postgres_em_conteiner, prazo=60.0)
    try:
        F["executar"](db, "drop table if exists prova")
        F["executar"](db, """create table prova (
            id serial primary key, nome text not null,
            preco numeric(10,2), quando timestamp default now())""")
        F["executar"](db, "insert into prova (nome, preco) values ($1, $2)",
                      ["Café", 32.5])
        F["executar"](db, "insert into prova (nome, preco) values ($1, $2)",
                      ["Chá", 18.0])

        linhas = F["consultar"](db, "select nome, preco from prova order by id")
        assert [l["nome"] for l in linhas] == ["Café", "Chá"], (
            "o acento prova que a codificacao atravessa o protocolo")
        assert "prova" in F["tabelas"](db)
        assert F["colunas"](db, "prova")
    finally:
        F["fechar"](db)


@precisa_docker
@pytest.mark.slow
def test_o_ORM_com_relacoes_contra_postgres(postgres_em_conteiner):
    """As relações e a carga antecipada contra o banco de verdade: o
    SQLite perdoa tipos e aspas que o Postgres não perdoa."""
    db = F["esperar"](postgres_em_conteiner, prazo=60.0)
    F["limpar_modelos"]()
    try:
        F["executar"](db, "drop table if exists pedido")
        F["executar"](db, "drop table if exists cliente")

        Cliente = F["modelo"]("Cliente", {"id": "Serial", "nome": "Texto"})
        Pedido = F["modelo"]("Pedido", {"id": "Serial",
                                        "cliente_id": "Inteiro",
                                        "total": "Decimal"})
        for m in (Cliente, Pedido):
            F["ligar"](m, db)
            m.migrar()

        Cliente.tem_muitos("pedidos", "Pedido", chave_externa="cliente_id")
        Pedido.pertence_a("cliente", "Cliente", chave_local="cliente_id")

        ana = Cliente.criar({"nome": "Ana"})
        bob = Cliente.criar({"nome": "Bob"})
        Pedido.criar({"cliente_id": ana["id"], "total": 99.9})
        Pedido.criar({"cliente_id": ana["id"], "total": 45.0})
        Pedido.criar({"cliente_id": bob["id"], "total": 12.0})

        # Duas consultas, e nao N+1.
        clientes = {c["nome"]: c for c in Cliente.com(Cliente.todos(), "pedidos")}
        assert len(clientes["Ana"]["pedidos"]) == 2
        assert len(clientes["Bob"]["pedidos"]) == 1

        pedidos = Pedido.com(Pedido.todos(), "cliente")
        assert all(p["cliente"]["nome"] in ("Ana", "Bob") for p in pedidos)

        pagina = Pedido.paginar(pagina=1, tamanho=2)
        assert pagina["total"] == 3 and pagina["paginas"] == 2
    finally:
        F["limpar_modelos"]()
        F["fechar"](db)


@precisa_docker
@pytest.mark.slow
def test_a_transacao_desfaz_de_verdade_no_postgres(postgres_em_conteiner):
    db = F["esperar"](postgres_em_conteiner, prazo=60.0)
    try:
        F["executar"](db, "drop table if exists conta")
        F["executar"](db, "create table conta (id serial primary key, saldo int)")
        F["executar"](db, "insert into conta (saldo) values (100)")

        # `transacao(conexao, corpo)` — e nao um bloco `with`. E a
        # unica forma que nao deixa transacao aberta por engano: um
        # `comecar()` com o `confirmar()` esquecido segura locks ate a
        # conexao cair.
        # O corpo recebe a conexao: assim ele nao depende de um nome
        # de fora, e a mesma acao serve a duas conexoes.
        def zerar(c):
            F["executar"](c, "update conta set saldo = 0")
            raise RuntimeError("algo deu errado no meio")

        try:
            F["transacao"](db, zerar)
        except RuntimeError:
            pass

        assert F["consultar"](db, "select saldo from conta")[0]["saldo"] == 100, (
            "o rollback nao desfez")
    finally:
        F["fechar"](db)
