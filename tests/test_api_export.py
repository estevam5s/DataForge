"""`Arcane.API` — a API do Kiln vista de fora.

O Kiln já era um framework REST completo. Faltava o outro lado: quem vai
**consumir** a API precisava ler o código-fonte do servidor.

Escrever a documentação à mão resolve por uma semana; depois ela diverge,
e uma documentação de API errada é pior que nenhuma. Por isso ela é
derivada das **rotas registradas** — o servidor é a fonte da verdade.
"""

import io
import json
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.interpreter import Interpreter    # noqa: E402
from dataforge.lexer import tokenize             # noqa: E402
from dataforge.parser import parse               # noqa: E402
from dataforge.stdlib import get_module          # noqa: E402

SERVIDOR = '''adopt Kiln

server Loja on 8080:
    route GET "/produtos":
        respond json {}
    route POST "/produtos":
        respond json {}
    route GET "/produtos/:id":
        respond json {}
    route PATCH "/produtos/:id":
        respond json {}
    route DELETE "/produtos/:id":
        respond json {}
'''


@pytest.fixture(scope="module")
def app():
    interp = Interpreter()
    with redirect_stdout(io.StringIO()):
        interp.run(parse(tokenize(SERVIDOR, "s.df"), "s.df"), "s.df")
    return interp.global_env.get("Loja")


@pytest.fixture(scope="module")
def API():
    return get_module("Arcane.API")


# ── A base: as rotas ─────────────────────────────────────────

def test_as_rotas_vem_do_servidor(app, API):
    rotas = API["rotas"](app)
    assert len(rotas) == 5
    assert {"method": "GET", "path": "/produtos", "params": []} in rotas


def test_resumo_conta_por_metodo(app, API):
    r = API["resumo"](app)
    assert r["rotas"] == 5
    assert r["metodos"]["GET"] == 2
    assert r["com_parametro"] == 3


# ── OpenAPI ──────────────────────────────────────────────────

def test_openapi_e_json_valido_e_versionado(app, API):
    doc = json.loads(API["openapi"](app))
    assert doc["openapi"] == "3.1.0"
    assert "/produtos" in doc["paths"]


def test_openapi_usa_chaves_no_parametro(app, API):
    """`/produtos/:id` é a sintaxe do Kiln; o OpenAPI usa `{id}`.

    Sem traduzir, o Swagger trata `:id` como parte literal do caminho e
    o cliente gerado bate numa URL que não existe.
    """
    doc = json.loads(API["openapi"](app))
    assert "/produtos/{id}" in doc["paths"]
    assert ":id" not in json.dumps(doc["paths"])

    parametros = doc["paths"]["/produtos/{id}"]["get"]["parameters"]
    assert parametros[0]["name"] == "id"
    assert parametros[0]["in"] == "path"
    assert parametros[0]["required"] is True


def test_openapi_pede_corpo_onde_faz_sentido(app, API):
    doc = json.loads(API["openapi"](app))
    assert "requestBody" in doc["paths"]["/produtos"]["post"]
    assert "requestBody" not in doc["paths"]["/produtos"]["get"]


def test_openapi_respeita_a_configuracao(app, API):
    doc = json.loads(API["openapi"](app, {
        "titulo": "Minha Loja", "versao": "2.1.0",
        "base": "https://api.loja.com"}))
    assert doc["info"]["title"] == "Minha Loja"
    assert doc["info"]["version"] == "2.1.0"
    assert doc["servers"][0]["url"] == "https://api.loja.com"


# ── Insomnia ─────────────────────────────────────────────────

def test_insomnia_e_importavel(app, API):
    """O formato 4 é o que o Insomnia lê em Import → From File."""
    col = json.loads(API["insomnia"](app))
    assert col["_type"] == "export"
    assert col["__export_format"] == 4

    pedidos = [r for r in col["resources"] if r.get("_type") == "request"]
    assert len(pedidos) == 5, "devia haver uma requisicao por rota"


def test_insomnia_usa_variavel_de_ambiente_no_parametro(app, API):
    """`{{ id }}` é o que o Insomnia reconhece como variável.

    Deixar `:id` cru daria uma requisição que bate literalmente em
    `/produtos/:id` — e ninguém entende por que dá 404.
    """
    col = json.loads(API["insomnia"](app))
    urls = [r["url"] for r in col["resources"] if r.get("_type") == "request"]
    assert any("{{ id }}" in u for u in urls)
    assert not any(":id" in u for u in urls)
    assert all(u.startswith("{{ base }}") for u in urls)


def test_insomnia_traz_o_ambiente_com_a_base(app, API):
    col = json.loads(API["insomnia"](app, {"base": "https://x.com"}))
    ambiente = next(r for r in col["resources"]
                    if r.get("_type") == "environment")
    assert ambiente["data"]["base"] == "https://x.com"


def test_insomnia_poe_corpo_so_onde_faz_sentido(app, API):
    col = json.loads(API["insomnia"](app))
    pedidos = {(r["method"], r["url"]): r
               for r in col["resources"] if r.get("_type") == "request"}
    post = next(r for (m, _), r in pedidos.items() if m == "POST")
    get = next(r for (m, _), r in pedidos.items() if m == "GET")
    assert "body" in post
    assert "body" not in get


# ── Postman ──────────────────────────────────────────────────

def test_postman_e_colecao_v2_1(app, API):
    col = json.loads(API["postman"](app))
    assert "collection/v2.1.0" in col["info"]["schema"]
    assert len(col["item"]) == 5


# ── curl e markdown ──────────────────────────────────────────

def test_curl_tem_um_comando_por_rota(app, API):
    texto = API["curl"](app, {"base": "https://api.loja.com"})
    assert texto.count("curl ") == 5
    assert "curl -X POST https://api.loja.com/produtos" in texto
    assert "-H 'Content-Type: application/json'" in texto


def test_markdown_tem_a_tabela(app, API):
    texto = API["markdown"](app, {"titulo": "Loja"})
    assert "# Loja" in texto
    assert "| `GET` | `/produtos` |" in texto


# ── Recusas ──────────────────────────────────────────────────

def test_o_que_nao_e_servidor_explica(API):
    from dataforge.errors import DataForgeError

    with pytest.raises(DataForgeError) as capturado:
        API["openapi"]({"nao": "sou"})
    assert "servidor" in str(capturado.value).lower()


def test_aceita_a_lista_que_routes_devolve(app, API):
    """Quem chama não deveria precisar saber qual das duas tem em mãos."""
    kiln = get_module("Kiln")
    rotas = kiln["routes"](app)
    doc = json.loads(API["openapi"](rotas))
    assert "/produtos" in doc["paths"]


# ── O comando da CLI ─────────────────────────────────────────

def test_o_comando_api_exporta_de_um_arquivo(tmp_path):
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivo = tmp_path / "app.df"
    arquivo.write_text(SERVIDOR, encoding="utf-8")
    destino = tmp_path / "openapi.json"

    r = subprocess.run(
        [sys.executable, "-m", "dataforge", "api", str(arquivo),
         "--openapi", f"-o={destino}"],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz,
        env={**os.environ, "PYTHONPATH": raiz, "NO_COLOR": "1"}, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    assert destino.exists()

    doc = json.loads(destino.read_text(encoding="utf-8"))
    assert len(doc["paths"]) == 2


def test_o_comando_explica_quando_nao_acha_servidor(tmp_path):
    """A causa mais comum é apontar para o `main.df`, que chama `ignite`."""
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivo = tmp_path / "vazio.df"
    arquivo.write_text('out "nada aqui"\n', encoding="utf-8")

    r = subprocess.run(
        [sys.executable, "-m", "dataforge", "api", str(arquivo)],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz,
        env={**os.environ, "PYTHONPATH": raiz, "NO_COLOR": "1"}, timeout=120)
    assert r.returncode != 0
    assert "main.df" in r.stdout, \
        "a mensagem precisa apontar a causa mais comum"


def test_funciona_num_projeto_de_verdade_do_repositorio():
    """O teste que pega o que um servidor inventado não pegaria."""
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alvo = os.path.join(raiz, "projetos", "loja-web", "src", "app.df")
    if not os.path.exists(alvo):
        pytest.skip("projetos/loja-web nao existe")

    r = subprocess.run(
        [sys.executable, "-m", "dataforge", "api", alvo, "--openapi"],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz,
        env={**os.environ, "PYTHONPATH": raiz, "NO_COLOR": "1"}, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr

    inicio = r.stdout.index("{")
    doc = json.loads(r.stdout[inicio:])
    assert doc["paths"], "nenhuma rota saiu de um projeto que tem rotas"
