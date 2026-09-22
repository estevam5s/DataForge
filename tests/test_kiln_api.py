"""As peças de API do Kiln: problema, negociação, pré-condição, cursor, links.

Cada teste confere o que a norma exige, e não o que a implementação faz —
é a única defesa contra um teste que concorda com o código errado.
"""
import json
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402
from tests._df import rodar  # noqa: E402

K = get_module("Arcane.Kiln")


def _req(**cabecalhos):
    return {"headers": {k.replace("_", "-"): v for k, v in cabecalhos.items()}}


# ── RFC 9457 ──────────────────────────────────────────────────

def test_problema_tem_o_tipo_de_midia_e_os_campos_da_rfc():
    r = K["problema"](404, "Pedido não encontrado", "não há pedido 9",
                      "https://exemplo.dev/erros/sem-pedido")
    assert r["status"] == 404
    assert r["content_type"].startswith("application/problem+json")
    assert r["body"] == {"type": "https://exemplo.dev/erros/sem-pedido",
                         "title": "Pedido não encontrado", "status": 404,
                         "detail": "não há pedido 9"}


def test_problema_sem_tipo_e_about_blank():
    assert K["problema"](500, "Falhou")["body"]["type"] == "about:blank"


def test_problema_de_sucesso_e_recusado():
    with pytest.raises(Exception, match="não é status de erro"):
        K["problema"](200, "Tudo certo")


def test_extras_nao_sobrescrevem_campo_da_rfc():
    with pytest.raises(Exception, match="própria RFC 9457"):
        K["problema"](400, "x", extras={"status": 200})
    ok = K["problema"](422, "Inválido", extras={"campos": {"email": "vazio"}})
    assert ok["body"]["campos"] == {"email": "vazio"}


# ── negociação ────────────────────────────────────────────────

@pytest.mark.parametrize("aceite,esperado", [
    (None, "application/json"),
    ("text/csv", "text/csv"),
    ("text/csv;q=0.5, application/json", "application/json"),
    ("*/*", "application/json"),
    ("text/*", "text/csv"),
    ("*/*, application/json;q=0", "text/csv"),
    ("image/png", None),
])
def test_negociar(aceite, esperado):
    req = _req(accept=aceite) if aceite else {"headers": {}}
    assert K["negociar"](req, ["application/json", "text/csv"]) == esperado


def test_a_faixa_mais_especifica_decide_o_q():
    """`text/csv;q=0` vence `text/*;q=1` — a específica manda."""
    req = _req(accept="text/*, text/csv;q=0")
    assert K["negociar"](req, ["text/csv", "text/plain"]) == "text/plain"


# ── pré-condição ──────────────────────────────────────────────

def test_etiqueta_e_forte_e_estavel():
    a = K["etiqueta"](3)
    assert a == K["etiqueta"](3) and not a.startswith("W/")
    assert a != K["etiqueta"](4)


def test_if_match_certo_passa_e_errado_da_412():
    atual = K["etiqueta"](3)
    assert K["precondicao"](_req(if_match=atual), atual) is None
    r = K["precondicao"](_req(if_match=K["etiqueta"](2)), atual)
    assert r["status"] == 412 and r["body"]["atual"] == atual


def test_etiqueta_fraca_nunca_casa_em_if_match():
    """RFC 9110 §13.1.1: If-Match usa comparação forte."""
    atual = 'W/"abc"'
    assert K["precondicao"](_req(if_match='W/"abc"'), atual)["status"] == 412


def test_if_match_asterisco_exige_que_exista():
    assert K["precondicao"](_req(if_match="*"), None)["status"] == 412
    assert K["precondicao"](_req(if_match="*"), '"x"') is None


def test_if_none_match_asterisco_cria_sem_sobrescrever():
    assert K["precondicao"](_req(if_none_match="*"), None) is None
    assert K["precondicao"](_req(if_none_match="*"), '"x"')["status"] == 412


def test_exigir_sem_cabecalho_da_428():
    assert K["precondicao"]({"headers": {}}, '"x"') is None
    assert K["precondicao"]({"headers": {}}, '"x"', True)["status"] == 428


# ── cursor e links ────────────────────────────────────────────

def test_cursor_vai_e_volta():
    assert K["ler_cursor"](K["cursor"]({"depois_de": 42})) == {"depois_de": 42}


def test_cursor_assinado_recusa_adulteracao_e_o_nao_assinado():
    c = K["cursor"]({"depois_de": 42}, "segredo")
    assert K["ler_cursor"](c, "segredo") == {"depois_de": 42}
    marca = c.rsplit(".", 1)[1]
    trocada = ("1" if marca[0] != "1" else "2") + marca[1:]
    assert K["ler_cursor"](c.rsplit(".", 1)[0] + "." + trocada, "segredo") is None
    corpo = K["cursor"]({"depois_de": 43}).rstrip("=")
    assert K["ler_cursor"](corpo + "." + marca, "segredo") is None
    assert K["ler_cursor"](c, "outro") is None
    assert K["ler_cursor"](K["cursor"]({"depois_de": 1}), "segredo") is None


@pytest.mark.parametrize("lixo", ["", "!!!", "e30", "WzFd"])
def test_cursor_invalido_e_void_e_nao_erro(lixo):
    # e30 = {} (vault vazio é válido); WzFd = [1] (não é vault)
    esperado = {} if lixo == "e30" else None
    assert K["ler_cursor"](lixo) == esperado


def test_links_nas_pontas():
    assert K["links"]("/p", 1, 3) == ('</p?pagina=1>; rel="first", '
                                      '</p?pagina=2>; rel="next", '
                                      '</p?pagina=3>; rel="last"')
    meio = K["links"]("/p?ordem=nome", 2, 3)
    assert '</p?ordem=nome&pagina=1>; rel="prev"' in meio


def test_de_ponta_a_ponta_na_linguagem(tmp_path):
    fonte = '''adopt Arcane.Kiln as Kiln
pedidos := {"1": {"id": 1, "total": 50, "versao": 1}}
app := Kiln.app()
action trocar(req):
    p := pedidos[req["params"]["id"]] ?? void
    given p is void:
        yield Kiln.problema(404, "Pedido não encontrado")
    falha := Kiln.precondicao(req, Kiln.etiqueta(p["versao"]), yes)
    given falha is not void:
        yield falha
    p["versao"] += 1
    yield Kiln.json(p, 200, {"ETag": Kiln.etiqueta(p["versao"])})
Kiln.put(app, "/pedidos/:id", trocar)
et := Kiln.etiqueta(1)
out Kiln.test(app, "PUT", "/pedidos/1", {})["status"]
out Kiln.test(app, "PUT", "/pedidos/1", {}, {"If-Match": et})["status"]
out Kiln.test(app, "PUT", "/pedidos/1", {}, {"If-Match": et})["status"]
out Kiln.test(app, "PUT", "/pedidos/7", {}, {"If-Match": et})["status"]
'''
    r = rodar(tmp_path, fonte)
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == ["428", "200", "412", "404"]


# ── duas correções achadas escrevendo estas páginas ───────────

def test_use_registra_as_duas_metades_do_idempotente(tmp_path):
    """`Kiln.use(app, Kiln.idempotente())` guardava nada: a cobrança repetia."""
    r = rodar(tmp_path, '''adopt Arcane.Kiln as Kiln
cobrancas := []
app := Kiln.app()
Kiln.use(app, Kiln.idempotente())
action cobrar(req):
    cobrancas.append(1)
    yield Kiln.json({"n": len(cobrancas)}, 201)
Kiln.post(app, "/c", cobrar)
k := {"Idempotency-Key": "k1"}
Kiln.test(app, "POST", "/c", {}, k)
r := Kiln.test(app, "POST", "/c", {}, k)
out len(cobrancas), r["headers"]["Idempotent-Replay"]
''')
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == ["1", "true"]


def test_registrar_a_metade_de_saida_duas_vezes_nao_a_duplica():
    from dataforge.stdlib.kiln import App, ArcaneKiln
    app = App("s")
    meio = ArcaneKiln._idempotente()
    app.usar(meio)
    app.apos(meio.depois)
    assert app.depois.count(meio.depois) == 1


def test_check_avisa_quando_o_coalesce_engole_a_comparacao(tmp_path):
    import subprocess
    arquivo = tmp_path / "c.df"
    arquivo.write_text('v := {}\nx := v["b"] ?? void is void\n'
                       'y := (v["b"] ?? void) is void\nz := v["b"] ?? (1 is 1)\n'
                       'w := v["b"] ?? 0 + 1\n', encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "check", str(arquivo)],
                       capture_output=True, text=True, encoding="utf-8",
                       cwd=RAIZ, env=dict(os.environ, NO_COLOR="1"))
    avisos = [l for l in r.stdout.splitlines() if "binds looser" in l
              or "liga mais fraco" in l]
    assert len(avisos) == 1 and ":2:" in avisos[0]
