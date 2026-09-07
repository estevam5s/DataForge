"""
Testes do Kiln — o framework web do DataForge (4.2).

Cobre o roteamento, a sintaxe propria da linguagem ('server', 'route',
'respond', 'render', …), os templates, a seguranca dos arquivos
estaticos e a garantia de que as palavras novas continuam servindo como
nomes comuns fora de um bloco 'server'.
"""

import io
import os
import socket
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.interpreter import Interpreter  # noqa: E402
from dataforge.lexer import tokenize  # noqa: E402
from dataforge.parser import parse  # noqa: E402
from dataforge.stdlib import get_module  # noqa: E402
from dataforge.stdlib.kiln import App, ArcaneKiln, Rota, _preencher  # noqa: E402
from dataforge.typechecker import check_program  # noqa: E402


def run(source: str) -> str:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(source)))
    return buffer.getvalue().strip()


def env_of(source: str) -> dict:
    interp = Interpreter()
    with redirect_stdout(io.StringIO()):
        interp.run(parse(tokenize(source)))
    return interp.global_env.variables


def errors(source: str):
    return [d for d in check_program(parse(tokenize(source)), "t.df")
            if d.severity == "error"]


# ── Modulo ───────────────────────────────────────────────────

def test_kiln_esta_registrado_na_stdlib():
    assert get_module("Kiln") is not None
    assert get_module("Arcane.Kiln") is not None


def test_kiln_expoe_a_superficie_documentada():
    mod = get_module("Kiln")
    for nome in ("forge", "get", "post", "put", "patch", "delete", "route",
                 "resource", "mount", "group", "use", "cors", "logger",
                 "rate_limit", "auth", "json", "html", "text", "redirect",
                 "file", "cookie", "render", "templates", "static",
                 "listen", "serve", "stop", "test", "routes", "stats"):
        assert nome in mod, f"Kiln.{nome} sumiu"


# ── Roteamento ───────────────────────────────────────────────

@pytest.mark.parametrize("padrao,caminho,esperado", [
    ("/users/:id", "/users/42", {"id": "42"}),
    ("/users/:id", "/users", None),
    ("/users/:id/posts/:post", "/users/7/posts/3", {"id": "7", "post": "3"}),
    ("/files/*caminho", "/files/a/b/c.txt", {"caminho": "a/b/c.txt"}),
    ("/", "/", {}),
    ("/produtos", "/produtos/", {}),          # barra final e tolerada
    ("/produtos", "/produtosX", None),
])
def test_padroes_de_rota(padrao, caminho, esperado):
    assert Rota("GET", padrao, None).casa(caminho) == esperado


def test_parametro_chega_decodificado():
    assert Rota("GET", "/b/:nome").casa("/b/ma%C3%A7%C3%A3") == {"nome": "maçã"}


def test_405_distingue_verbo_errado_de_rota_ausente():
    app = App("t")
    app.rota("GET", "/x", lambda req: "ok")
    assert ArcaneKiln._test(app, "GET", "/x")["status"] == 200
    recusa = ArcaneKiln._test(app, "POST", "/x")
    assert recusa["status"] == 405
    assert recusa["headers"]["Allow"] == "GET"
    assert ArcaneKiln._test(app, "GET", "/y")["status"] == 404


def test_query_com_um_valor_e_string_com_varios_e_lista():
    app = App("t")
    app.rota("GET", "/b", lambda req: ArcaneKiln._json(req["query"]))
    corpo = ArcaneKiln._test(app, "GET", "/b?a=1&t=x&t=y")["body"]
    assert corpo == {"a": "1", "t": ["x", "y"]}


def test_middleware_que_responde_interrompe_a_cadeia():
    app = App("t")
    chamou = []
    app.usar(lambda req: ArcaneKiln._json({"barrado": True}, 401))
    app.rota("GET", "/x", lambda req: chamou.append(1))
    assert ArcaneKiln._test(app, "GET", "/x")["status"] == 401
    assert chamou == []


def test_rate_limit_barra_depois_do_teto():
    app = App("t")
    app.usar(ArcaneKiln._rate_limit(maximo=2, janela=60))
    app.rota("GET", "/x", lambda req: "ok")
    assert [ArcaneKiln._test(app, "GET", "/x")["status"] for _ in range(3)] \
        == [200, 200, 429]


def test_erro_no_handler_vira_500_e_nao_derruba_o_servidor():
    app = App("t")
    app.rota("GET", "/boom", lambda req: 1 / 0)
    app.rota("GET", "/ok", lambda req: "vivo")
    assert ArcaneKiln._test(app, "GET", "/boom")["status"] == 500
    assert ArcaneKiln._test(app, "GET", "/ok")["status"] == 200


def test_corpo_json_invalido_nao_estoura():
    """JSON quebrado e problema do cliente: 400 se a rota quiser, nunca 500."""
    app = App("t")
    app.rota("POST", "/x", lambda req: ArcaneKiln._json({"tipo": str(type(req["body"]).__name__)}))
    resp = ArcaneKiln._test(app, "POST", "/x", "{isso nao e json",
                            {"content-type": "application/json"})
    assert resp["status"] == 200
    assert resp["body"]["tipo"] == "str"


def test_resource_gera_as_rotas_restful():
    app = App("t")
    ArcaneKiln._resource(app, "posts", {
        "index": lambda req: ArcaneKiln._json([]),
        "show": lambda req: ArcaneKiln._json({"id": req["params"]["id"]}),
        "create": lambda req: ArcaneKiln._json({}, 201),
    })
    caminhos = {(r["method"], r["path"]) for r in ArcaneKiln._routes(app)}
    assert ("GET", "/posts") in caminhos
    assert ("GET", "/posts/:id") in caminhos
    assert ("POST", "/posts") in caminhos
    # os que o controlador nao tem simplesmente nao existem
    assert ("DELETE", "/posts/:id") not in caminhos


# ── Templates ────────────────────────────────────────────────

def test_template_escapa_por_padrao_e_solta_com_e_comercial():
    assert _preencher("{{x}}", {"x": "<b>"}) == "&lt;b&gt;"
    assert _preencher("{{&x}}", {"x": "<b>"}) == "<b>"


def test_template_repete_lista_e_trata_vazio():
    modelo = "{{#itens}}[{{n}}]{{/itens}}{{^itens}}vazio{{/itens}}"
    assert _preencher(modelo, {"itens": [{"n": 1}, {"n": 2}]}) == "[1][2]"
    assert _preencher(modelo, {"itens": []}) == "vazio"


def test_template_com_bloco_aberto_avisa_em_vez_de_calar():
    with pytest.raises(ValueError, match="aberto e nunca fechado"):
        _preencher("{{#a}}sem fim", {"a": [1]})


# ── Seguranca ────────────────────────────────────────────────

def test_estatico_recusa_sair_da_pasta(tmp_path):
    (tmp_path / "ok.txt").write_text("conteudo")
    app = App("t")
    app.estaticos.append(("/s", str(tmp_path)))
    assert ArcaneKiln._test(app, "GET", "/s/ok.txt")["status"] == 200
    fuga = ArcaneKiln._test(app, "GET", "/s/../../../etc/passwd")
    assert fuga["status"] == 403


def test_sessao_assinada_recusa_token_adulterado():
    token = ArcaneKiln._sign({"user": "ana"}, "segredo")
    assert ArcaneKiln._unsign(token, "segredo") == {"user": "ana"}
    assert ArcaneKiln._unsign(token[:-1] + "0", "segredo") is None
    assert ArcaneKiln._unsign(token, "outro") is None


def test_corpo_grande_demais_e_recusado_antes_de_ser_lido():
    app = App("t")
    app.config["limite_corpo"] = 10
    app.rota("POST", "/x", lambda req: "ok")
    porta = ArcaneKiln._serve(app, 0)
    try:
        conexao = socket.create_connection(("127.0.0.1", porta), timeout=5)
        corpo = b"x" * 5000
        conexao.sendall(
            b"POST /x HTTP/1.1\r\nHost: t\r\nConnection: close\r\n"
            b"Content-Length: " + str(len(corpo)).encode() + b"\r\n\r\n" + corpo)
        resposta = b""
        while True:
            pedaco = conexao.recv(4096)
            if not pedaco:
                break
            resposta += pedaco
        conexao.close()
        assert b"413" in resposta.split(b"\r\n")[0]
    finally:
        ArcaneKiln._stop(app)


# ── Servidor de verdade ──────────────────────────────────────

def test_servidor_real_responde_pelo_socket():
    app = App("t")
    app.rota("GET", "/oi/:nome",
             lambda req: ArcaneKiln._html(f"<h1>{req['params']['nome']}</h1>"))
    porta = ArcaneKiln._serve(app, 0)
    try:
        conexao = socket.create_connection(("127.0.0.1", porta), timeout=5)
        conexao.sendall(b"GET /oi/Ana HTTP/1.1\r\nHost: t\r\n"
                        b"Connection: close\r\n\r\n")
        resposta = b""
        while True:
            pedaco = conexao.recv(4096)
            if not pedaco:
                break
            resposta += pedaco
        conexao.close()
        assert b"200" in resposta.split(b"\r\n")[0]
        assert b"<h1>Ana</h1>" in resposta
        assert b"text/html" in resposta
    finally:
        ArcaneKiln._stop(app)


# ── Sintaxe da linguagem ─────────────────────────────────────

FONTE = '''
adopt Kiln

itens := [{"id": 1, "nome": "Martelo"}]

server loja on 8080:
    middleware Kiln.cors()

    route GET "/":
        respond html "<h1>Forja</h1>"

    route GET "/itens":
        respond json itens

    route GET "/itens/:id":
        given int(params["id"]) bigger len(itens):
            respond 404 json {"erro": "não achei"}
        respond json itens[int(params["id"]) - 1]

    route POST "/itens":
        respond 201 json {"criado": body["nome"]}

    route DELETE "/itens/:id":
        respond 204

    route GET "/velho":
        redirect "/itens"
'''


def test_bloco_server_liga_o_nome_a_uma_aplicacao():
    app = env_of(FONTE)["loja"]
    assert isinstance(app, App)
    assert app.nome == "loja"
    assert app.config["porta"] == 8080
    assert len(app.rotas) == 6


def test_respond_devolve_o_tipo_certo_para_cada_forma():
    app = env_of(FONTE)["loja"]

    home = ArcaneKiln._test(app, "GET", "/")
    assert home["status"] == 200 and home["body"] == "<h1>Forja</h1>"

    lista = ArcaneKiln._test(app, "GET", "/itens")
    assert lista["body"] == [{"id": 1, "nome": "Martelo"}]

    assert ArcaneKiln._test(app, "GET", "/itens/1")["body"]["nome"] == "Martelo"
    assert ArcaneKiln._test(app, "GET", "/itens/9")["status"] == 404

    criado = ArcaneKiln._test(app, "POST", "/itens", {"nome": "Bigorna"})
    assert criado["status"] == 201 and criado["body"] == {"criado": "Bigorna"}

    assert ArcaneKiln._test(app, "DELETE", "/itens/1")["status"] == 204


def test_redirect_manda_location():
    app = env_of(FONTE)["loja"]
    saida = ArcaneKiln._test(app, "GET", "/velho")
    assert saida["status"] == 302
    assert saida["headers"]["Location"] == "/itens"


def test_respond_encerra_a_rota_como_yield():
    """O que vem depois de 'respond' nao roda."""
    app = env_of('''
adopt Kiln
marcas := []
server s on 0:
    route GET "/":
        respond json {"ok": yes}
        marcas.append("nao devia rodar")
''')["s"]
    assert ArcaneKiln._test(app, "GET", "/")["body"] == {"ok": True}


def test_rota_enxerga_acoes_e_dados_declarados_antes():
    saida = run('''
adopt Kiln
taxa := 2
action dobrar(n):
    yield n * taxa
server s on 0:
    route GET "/d/:n":
        respond json {"r": dobrar(int(params["n"]))}
''' + '''
out Kiln.test(s, "GET", "/d/21")["body"]["r"]''')
    assert saida == "42"


def test_render_com_with_nao_vira_expressao_de_record(tmp_path):
    """'render "x" with {…}' e um comando, nao 'record with {…}'."""
    (tmp_path / "p.html").write_text("<p>{{nome}}</p>")
    saida = run(f'''
adopt Kiln
server s on 0:
    views "{tmp_path}"
    route GET "/":
        render "p.html" with {{"nome": "Ana"}}
out Kiln.test(s, "GET", "/")["body"]''')
    assert saida == "<p>Ana</p>"


def test_record_with_continua_funcionando():
    """A guarda do render nao pode ter matado o operador 'with'."""
    saida = run('''
record Ponto:
    x: Integer
    y: Integer
p := Ponto(1, 2) with {"y": 9}
out p.x, p.y''')
    assert saida == "1 9"


def test_os_atalhos_da_rota_existem():
    saida = run('''
adopt Kiln
server s on 0:
    route POST "/x/:id":
        respond json {
            "p": params["id"],
            "q": query["f"],
            "b": body["n"],
            "tem_req": req["method"]
        }
out Kiln.test(s, "POST", "/x/7?f=abc", {"n": 5})["body"]''')
    assert "p: 7" in saida and "q: abc" in saida
    assert "b: 5" in saida and "tem_req: POST" in saida


# ── As palavras novas continuam livres ───────────────────────

@pytest.mark.parametrize("palavra", [
    "server", "route", "respond", "render", "redirect",
    "middleware", "mount", "assets", "views", "ignite",
])
def test_palavra_do_kiln_ainda_serve_de_nome(palavra):
    """Foram feitas contextuais justamente para isto."""
    assert run(f"{palavra} := 7\nout {palavra} * 6") == "42"


def test_palavra_do_kiln_ainda_serve_de_acao():
    assert run("action route(x):\n    yield x + 1\nout route(41)") == "42"


def test_server_seguido_de_atribuicao_nao_abre_bloco():
    assert run('server := "10.0.0.1"\nout server') == "10.0.0.1"


# ── Analisador estatico ──────────────────────────────────────

def test_checker_conhece_o_bloco_server():
    assert errors(FONTE + '\nout Kiln.routes(loja)') == []


def test_checker_declara_os_atalhos_da_rota():
    assert errors('''
adopt Kiln
server s on 0:
    route GET "/:id":
        respond json {"a": params["id"], "b": query, "c": body, "d": req}
''') == []


def test_ignite_recusa_quem_nao_e_server():
    from dataforge.errors import RuntimeError_
    with pytest.raises(RuntimeError_, match="expects a server"):
        run('x := 7\nignite x')


def test_ignite_aceita_um_server_vindo_de_modulo():
    """'ignite App.loja' — um projeto separa quem monta de quem acende.

    O parser so aceitava um nome simples, e um projeto de verdade
    quebrava na ultima linha do main.
    """
    from dataforge.parser import parse
    from dataforge.lexer import tokenize
    from dataforge import ast_nodes as ast

    no = parse(tokenize("ignite App.loja on porta")).body[0]
    assert isinstance(no, ast.IgniteStatement)
    assert isinstance(no.target, ast.MemberAccess)
    assert isinstance(no.port, ast.Identifier)


def test_kiln_test_devolve_texto_para_arquivo_textual(tmp_path):
    """Um .css servido do disco chega em bytes; num teste, isso obriga
    a decodificar a mao toda vez."""
    (tmp_path / "e.css").write_text("body { color: red }")
    app = App("t")
    app.estaticos.append(("/s", str(tmp_path)))
    corpo = ArcaneKiln._test(app, "GET", "/s/e.css")["body"]
    assert isinstance(corpo, str)
    assert "color: red" in corpo
