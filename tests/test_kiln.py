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

import json
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
    (tmp_path / "p.html").write_text("<p>{{nome}}</p>", encoding="utf-8")
    # 'as_posix': no Windows o caminho vem com contrabarra, e dentro de
    # um literal de texto ela e ESCAPE — 'C:\\Users\\...' vira outra coisa
    # e o template nao e encontrado. A barra normal funciona nos tres
    # sistemas.
    pasta = tmp_path.as_posix()
    saida = run(f'''
adopt Kiln
server s on 0:
    views "{pasta}"
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


# ═══════════════════════════════════════════════════════════
#  Seguranca de aplicacao
# ═══════════════════════════════════════════════════════════

class TestCabecalhosSeguros:
    """Os cabecalhos que o navegador so respeita se voce mandar."""

    def _app(self, **kw):
        app = App("s")
        app.apos(ArcaneKiln._secure_headers(**kw))
        app.rota("GET", "/", lambda req: {"ok": 1})
        return app

    def _cabs(self, app):
        r = ArcaneKiln._test(app, "GET", "/")
        return {k.lower(): v for k, v in r["headers"].items()}

    def test_manda_os_cabecalhos_basicos(self):
        h = self._cabs(self._app())
        assert h["x-content-type-options"] == "nosniff"
        assert h["x-frame-options"] == "DENY"
        assert "referrer-policy" in h
        assert "content-security-policy" in h
        assert "permissions-policy" in h

    def test_hsts_so_com_https_ligado(self):
        """Mandar HSTS em http tranca o site num https que nao existe."""
        assert "strict-transport-security" not in self._cabs(self._app())
        assert "strict-transport-security" in self._cabs(self._app(hsts=True))

    def test_a_csp_pode_ser_trocada(self):
        h = self._cabs(self._app(csp="default-src 'none'"))
        assert h["content-security-policy"] == "default-src 'none'"

    def test_nao_apaga_cabecalho_que_a_rota_ja_pos(self):
        app = App("s")
        app.apos(ArcaneKiln._secure_headers())
        app.rota("GET", "/", lambda req: ArcaneKiln._header(
            ArcaneKiln._json({"ok": 1}), "X-Frame-Options", "SAMEORIGIN"))
        h = {k.lower(): v for k, v in
             ArcaneKiln._test(app, "GET", "/")["headers"].items()}
        assert h["x-frame-options"] == "SAMEORIGIN"


class TestCsrf:
    """O token que separa um pedido do seu site de um de outro."""

    SEGREDO = "segredo-de-teste"

    def _app(self, segredo=None):
        chave = segredo or self.SEGREDO
        app = App("s")
        app.usar(ArcaneKiln._csrf(chave))
        app.rota("GET", "/form",
                 lambda req: {"token": ArcaneKiln._csrf_token(req, chave)})
        app.rota("POST", "/enviar", lambda req: {"ok": 1})
        return app

    def _token(self, app=None, segredo=None):
        alvo = app or self._app(segredo)
        return ArcaneKiln._test(alvo, "GET", "/form")["body"]["token"]

    def test_get_passa_sem_token(self):
        """Metodo seguro nao muda estado; cobrar token ali so atrapalha."""
        assert ArcaneKiln._test(self._app(), "GET", "/form")["status"] == 200

    def test_post_sem_token_e_recusado(self):
        assert ArcaneKiln._test(self._app(), "POST", "/enviar")["status"] == 403

    def test_post_com_o_token_certo_passa(self):
        app = self._app()
        r = ArcaneKiln._test(app, "POST", "/enviar",
                             cabecalhos={"X-CSRF-Token": self._token(app)})
        assert r["status"] == 200

    def test_token_de_outro_segredo_e_recusado(self):
        """E o ponto do CSRF: um token forjado fora nao serve."""
        forjado = self._token(segredo="outro-segredo")
        r = ArcaneKiln._test(self._app(), "POST", "/enviar",
                             cabecalhos={"X-CSRF-Token": forjado})
        assert r["status"] == 403

    def test_token_adulterado_e_recusado(self):
        app = self._app()
        t = self._token(app)
        r = ArcaneKiln._test(app, "POST", "/enviar",
                             cabecalhos={"X-CSRF-Token": t[:-3] + "aaa"})
        assert r["status"] == 403

    def test_o_token_tambem_vem_do_corpo(self):
        """Um <form> comum nao manda cabecalho: manda campo."""
        app = self._app()
        r = ArcaneKiln._test(app, "POST", "/enviar",
                             corpo={"_csrf": self._token(app)})
        assert r["status"] == 200


# ═══════════════════════════════════════════════════════════
#  Validacao, listagem, cache e limites
# ═══════════════════════════════════════════════════════════

ESQUEMA = {
    "nome": {"tipo": "texto", "obrigatorio": True, "min": 2, "max": 40},
    "idade": {"tipo": "inteiro", "min": 0, "max": 130},
    "email": {"tipo": "email"},
    "papel": {"tipo": "texto", "em": ["admin", "leitor"]},
}


class TestValidar:
    def _app(self):
        app = App("s")
        app.usar(ArcaneKiln._validar(ESQUEMA))
        app.rota("POST", "/u", lambda req: {"ok": 1})
        return app

    def test_corpo_certo_passa(self):
        r = ArcaneKiln._test(self._app(), "POST", "/u", corpo={
            "nome": "Ana", "idade": 30, "email": "a@b.co", "papel": "admin"})
        assert r["status"] == 200

    def test_422_e_nao_400(self):
        """O corpo foi entendido; o que falhou foi o conteudo."""
        r = ArcaneKiln._test(self._app(), "POST", "/u", corpo={})
        assert r["status"] == 422

    def test_relata_todos_os_campos_de_uma_vez(self):
        """Um erro por envio faz a pessoa desistir no terceiro."""
        r = ArcaneKiln._test(self._app(), "POST", "/u", corpo={
            "nome": "A", "idade": 999, "email": "nao-e-email", "papel": "x"})
        campos = r["body"]["campos"]
        assert set(campos) == {"nome", "idade", "email", "papel"}

    def test_campo_opcional_ausente_nao_e_erro(self):
        r = ArcaneKiln._test(self._app(), "POST", "/u", corpo={"nome": "Ana"})
        assert r["status"] == 200

    def test_booleano_nao_passa_por_inteiro(self):
        """Em Python 'yes' é 1; aqui não pode valer como idade."""
        r = ArcaneKiln._test(self._app(), "POST", "/u",
                             corpo={"nome": "Ana", "idade": True})
        assert r["status"] == 422


class TestPaginarOrdenarBuscar:
    ITENS = [{"id": i, "nome": f"item {i:02d}", "preco": (100 - i)}
             for i in range(1, 31)]

    def _req(self, consulta):
        return {"query": consulta, "method": "GET"}

    def test_primeira_pagina_e_a_meta(self):
        p = ArcaneKiln._paginar(self.ITENS, self._req({}))
        assert len(p["itens"]) == 20
        assert (p["pagina"], p["total"], p["paginas"]) == (1, 30, 2)
        assert p["tem_proxima"] and not p["tem_anterior"]

    def test_segunda_pagina(self):
        p = ArcaneKiln._paginar(self.ITENS, self._req({"pagina": "2"}))
        assert len(p["itens"]) == 10
        assert p["tem_anterior"] and not p["tem_proxima"]

    def test_por_pagina_tem_teto(self):
        """'?por_pagina=1000000' derrubaria o servidor sem ferramenta."""
        p = ArcaneKiln._paginar(self.ITENS, self._req({"por_pagina": "1000000"}))
        assert p["por_pagina"] == 100

    def test_pagina_invalida_nao_estoura(self):
        for ruim in ("abc", "-5", "0", ""):
            p = ArcaneKiln._paginar(self.ITENS, self._req({"pagina": ruim}))
            assert p["pagina"] == 1

    def test_ordenar_crescente_e_descendente(self):
        campos = ["preco"]
        asc = ArcaneKiln._ordenar(self.ITENS, self._req({"ordenar": "preco"}), campos)
        des = ArcaneKiln._ordenar(self.ITENS, self._req({"ordenar": "-preco"}), campos)
        assert asc[0]["preco"] < asc[-1]["preco"]
        assert des[0]["preco"] > des[-1]["preco"]

    def test_ordenar_so_pelos_campos_permitidos(self):
        """Ordenar por um campo nao exposto revela a ordem dele."""
        fora = ArcaneKiln._ordenar(self.ITENS, self._req({"ordenar": "id"}),
                                   ["preco"])
        assert fora == list(self.ITENS)

    def test_ordenar_com_tipos_misturados_nao_estoura(self):
        bagunca = [{"v": 3}, {"v": None}, {"v": "a"}, {"v": True}]
        r = ArcaneKiln._ordenar(bagunca, self._req({"ordenar": "v"}), ["v"])
        assert len(r) == 4

    def test_buscar(self):
        r = ArcaneKiln._buscar(self.ITENS, self._req({"q": "item 07"}), ["nome"])
        assert len(r) == 1 and r[0]["id"] == 7

    def test_buscar_sem_termo_devolve_tudo(self):
        assert len(ArcaneKiln._buscar(self.ITENS, self._req({}), ["nome"])) == 30


class TestCacheEtag:
    def _app(self):
        app = App("s")
        app.apos(ArcaneKiln._cache(120))
        app.rota("GET", "/", lambda req: {"v": 1})
        return app

    def test_poe_cache_control_e_etag(self):
        h = ArcaneKiln._test(self._app(), "GET", "/")["headers"]
        assert "max-age=120" in h["Cache-Control"]
        assert h["ETag"].startswith('W/"')

    def test_304_quando_nada_mudou(self):
        app = self._app()
        etag = ArcaneKiln._test(app, "GET", "/")["headers"]["ETag"]
        r = ArcaneKiln._test(app, "GET", "/",
                             cabecalhos={"If-None-Match": etag})
        assert r["status"] == 304

    def test_etag_diferente_devolve_200(self):
        r = ArcaneKiln._test(self._app(), "GET", "/",
                             cabecalhos={"If-None-Match": 'W/"outra"'})
        assert r["status"] == 200


class TestComprimir:
    def _app(self, tamanho=5000):
        app = App("s")
        app.apos(ArcaneKiln._comprimir())
        app.rota("GET", "/", lambda req: ArcaneKiln._text("x" * tamanho))
        return app

    def test_comprime_quando_o_cliente_aceita(self):
        r = ArcaneKiln._test(self._app(), "GET", "/",
                             cabecalhos={"Accept-Encoding": "gzip, deflate"})
        assert r["headers"]["Content-Encoding"] == "gzip"
        assert r["headers"]["Vary"] == "Accept-Encoding"

    def test_nao_comprime_sem_accept_encoding(self):
        r = ArcaneKiln._test(self._app(), "GET", "/")
        assert "Content-Encoding" not in r["headers"]

    def test_corpo_pequeno_nao_compensa(self):
        r = ArcaneKiln._test(self._app(10), "GET", "/",
                             cabecalhos={"Accept-Encoding": "gzip"})
        assert "Content-Encoding" not in r["headers"]


class TestLimiteDeCorpo:
    def _app(self, teto=100):
        app = App("s")
        app.usar(ArcaneKiln._limite_de_corpo(teto))
        app.rota("POST", "/", lambda req: {"ok": 1})
        return app

    def test_corpo_pequeno_passa(self):
        assert ArcaneKiln._test(self._app(), "POST", "/",
                                corpo={"a": 1})["status"] == 200

    def test_corpo_grande_e_413(self):
        r = ArcaneKiln._test(self._app(), "POST", "/", corpo={"a": "x" * 500})
        assert r["status"] == 413


class TestIdempotencia:
    def _app(self):
        contador = {"n": 0}
        app = App("s")
        meio = ArcaneKiln._idempotente()
        app.usar(meio)
        app.apos(meio.depois)

        def cobrar(req):
            contador["n"] += 1
            return {"cobranca": contador["n"]}

        app.rota("POST", "/cobrar", cobrar)
        return app, contador

    def test_sem_chave_cobra_de_novo(self):
        app, c = self._app()
        ArcaneKiln._test(app, "POST", "/cobrar")
        ArcaneKiln._test(app, "POST", "/cobrar")
        assert c["n"] == 2

    def test_a_mesma_chave_nao_cobra_duas_vezes(self):
        """O caso real: a resposta se perde e o cliente reenvia."""
        app, c = self._app()
        cabs = {"Idempotency-Key": "abc-123"}
        um = ArcaneKiln._test(app, "POST", "/cobrar", cabecalhos=cabs)
        dois = ArcaneKiln._test(app, "POST", "/cobrar", cabecalhos=cabs)
        assert c["n"] == 1
        assert um["body"] == dois["body"]
        assert dois["headers"]["Idempotent-Replay"] == "true"

    def test_chaves_diferentes_cobram_separado(self):
        app, c = self._app()
        ArcaneKiln._test(app, "POST", "/cobrar", cabecalhos={"Idempotency-Key": "a"})
        ArcaneKiln._test(app, "POST", "/cobrar", cabecalhos={"Idempotency-Key": "b"})
        assert c["n"] == 2


class TestRequestIdEAudit:
    def test_gera_e_devolve_o_id(self):
        app = App("s")
        meio = ArcaneKiln._request_id()
        app.usar(meio)
        app.apos(meio.depois)
        app.rota("GET", "/", lambda req: {"id": req["state"]["request_id"]})
        r = ArcaneKiln._test(app, "GET", "/")
        assert r["headers"]["X-Request-Id"] == r["body"]["id"]

    def test_mantem_o_id_que_veio_de_fora(self):
        """O proxy na frente ja gerou; trocar quebra a corrente."""
        app = App("s")
        meio = ArcaneKiln._request_id()
        app.usar(meio)
        app.rota("GET", "/", lambda req: {"id": req["state"]["request_id"]})
        r = ArcaneKiln._test(app, "GET", "/",
                             cabecalhos={"X-Request-Id": "do-proxy"})
        assert r["body"]["id"] == "do-proxy"

    def test_audit_so_registra_o_que_muda_estado(self):
        app = App("s")
        registro = ArcaneKiln._audit()
        app.apos(registro)
        app.rota("GET", "/x", lambda req: {"ok": 1})
        app.rota("POST", "/x", lambda req: {"ok": 1})
        ArcaneKiln._test(app, "GET", "/x")
        ArcaneKiln._test(app, "POST", "/x")
        assert [l["metodo"] for l in registro.registro] == ["POST"]

    def test_audit_nao_guarda_o_corpo(self):
        """Ele carrega senha, cartao e token."""
        app = App("s")
        registro = ArcaneKiln._audit()
        app.apos(registro)
        app.rota("POST", "/login", lambda req: {"ok": 1})
        ArcaneKiln._test(app, "POST", "/login", corpo={"senha": "hunter2"})
        assert "hunter2" not in json.dumps(registro.registro)
