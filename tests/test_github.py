"""Arcane.GitHub — Actions, webhooks e a API REST, contra o que é de verdade.

A assinatura de webhook é conferida contra o **vetor publicado na
documentação do GitHub**: comparar a implementação com ela mesma não
prova nada. A API é testada contra um servidor HTTP local que responde
como a do GitHub — paginação por `Link`, limite de taxa, 404 com
`message` — porque um cliente testado só com dublê não prova nada sobre
o que acontece quando o outro lado pagina.
"""
import http.server
import json
import os
import sys
import threading

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402

G = get_module("Arcane.GitHub")


# ── Actions ─────────────────────────────────────────────────────

def test_a_anotacao_escapa_a_mensagem_e_as_propriedades():
    a = G["anotacao"]("erro", "linha 1\nlinha 2 com 100%", "src/a,b.df", 3, 5,
                      "DF0401: nome")
    assert a == ("::error file=src/a%2Cb.df,line=3,col=5,title=DF0401%3A nome"
                 "::linha 1%0Alinha 2 com 100%25")


def test_os_niveis_em_portugues_e_o_desconhecido_recusado():
    assert G["anotacao"]("aviso", "x").startswith("::warning::")
    assert G["anotacao"]("nota", "x").startswith("::notice::")
    with pytest.raises(Exception) as e:
        G["anotacao"]("fatal", "x")
    assert "nivel" in str(e.value)


def test_saida_multilinha_nao_vira_duas_saidas(tmp_path, monkeypatch):
    arq = tmp_path / "out"
    monkeypatch.setenv("GITHUB_OUTPUT", str(arq))
    G["saida"]("relatorio", "a=1\nb=2\n")
    texto = arq.read_text(encoding="utf-8")
    cabeca, resto = texto.split("\n", 1)
    nome, delim = cabeca.split("<<")
    assert nome == "relatorio" and delim.startswith("ghadelimiter_")
    assert resto == f"a=1\nb=2\n\n{delim}\n"


def test_o_delimitador_muda_a_cada_escrita(tmp_path, monkeypatch):
    arq = tmp_path / "out"
    monkeypatch.setenv("GITHUB_OUTPUT", str(arq))
    G["saida"]("a", "1")
    G["saida"]("b", "2")
    delims = [l.split("<<")[1] for l in arq.read_text().splitlines() if "<<" in l]
    assert len(set(delims)) == 2


def test_nome_com_igual_ou_quebra_e_recusado(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ENV", str(tmp_path / "env"))
    for ruim in ("A=B", "A\nB", ""):
        with pytest.raises(Exception):
            G["exportar"](ruim, "x")


def test_fora_do_actions_o_erro_diz_o_porque(monkeypatch):
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    with pytest.raises(Exception) as e:
        G["saida"]("x", "1")
    assert "GITHUB_OUTPUT" in str(e.value)


def test_contexto_fora_do_actions_vem_vazio_e_nao_levanta(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    c = G["contexto"]()
    assert c["em_actions"] is False and c["url_da_execucao"] == ""


def test_contexto_monta_a_url_da_execucao(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_REPOSITORY", "dono/repo")
    monkeypatch.setenv("GITHUB_RUN_ID", "42")
    c = G["contexto"]()
    assert c["em_actions"] and c["url_da_execucao"].endswith("/dono/repo/actions/runs/42")


def test_resumo_e_tabela_escapam_a_barra(tmp_path, monkeypatch):
    arq = tmp_path / "resumo.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(arq))
    t = G["tabela_markdown"]([{"teste": "a|b", "ok": "sim"}])
    G["resumo"](t)
    assert "a\\|b" in arq.read_text()
    assert arq.read_text().count("\n") == 3


def test_mascarar_multilinha_mascara_cada_linha(capsys):
    G["mascarar_no_log"]("linha-um\nlinha-dois")
    saida = capsys.readouterr().out.splitlines()
    assert saida == ["::add-mask::linha-um", "::add-mask::linha-dois"]


def test_grupo_fecha_mesmo_com_erro(capsys):
    with pytest.raises(ZeroDivisionError):
        G["grupo"]("passo", lambda: 1 / 0)
    assert capsys.readouterr().out.splitlines()[-1] == "::endgroup::"


def test_evento_le_o_arquivo_do_executor(tmp_path, monkeypatch):
    arq = tmp_path / "evento.json"
    arq.write_text(json.dumps({"pull_request": {"number": 7}}))
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(arq))
    assert G["evento"]()["pull_request"]["number"] == 7


# ── Webhooks ────────────────────────────────────────────────────

# O vetor da documentação do GitHub ("Validating webhook deliveries").
SEGREDO_DOC = "It's a Secret to Everybody"
CORPO_DOC = "Hello, World!"
ASSINATURA_DOC = ("sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46"
                  "f4379c8b043e17")


def test_a_assinatura_bate_com_o_vetor_da_documentacao():
    assert G["assinatura"](SEGREDO_DOC, CORPO_DOC) == ASSINATURA_DOC
    assert G["conferir_webhook"](SEGREDO_DOC, CORPO_DOC.encode(), ASSINATURA_DOC)


def test_corpo_alterado_ou_sem_cabecalho_nao_confere():
    assert not G["conferir_webhook"](SEGREDO_DOC, "Hello, World?", ASSINATURA_DOC)
    assert not G["conferir_webhook"](SEGREDO_DOC, CORPO_DOC, "")


def test_segredo_vazio_e_recusado():
    with pytest.raises(Exception) as e:
        G["assinatura"]("", "x")
    assert "segredo" in str(e.value)


def test_um_vault_no_lugar_do_corpo_e_recusado_com_o_motivo():
    with pytest.raises(Exception) as e:
        G["conferir_webhook"]("s", {"a": 1}, "sha256=x")
    assert "BYTES" in str(e.value)


def test_evento_de_webhook_devolve_tipo_entrega_e_acao():
    corpo = json.dumps({"action": "opened", "number": 3})
    cab = {"x-github-event": "pull_request", "X-GitHub-Delivery": "abc-123",
           "X-Hub-Signature-256": G["assinatura"]("s3", corpo)}
    e = G["evento_de_webhook"](cab, corpo, "s3")
    assert (e["tipo"], e["entrega"], e["acao"]) == ("pull_request", "abc-123", "opened")
    assert e["carga"]["number"] == 3


def test_evento_de_webhook_forjado_e_recusado():
    corpo = json.dumps({"action": "opened"})
    cab = {"X-Hub-Signature-256": G["assinatura"]("outro", corpo)}
    with pytest.raises(Exception) as e:
        G["evento_de_webhook"](cab, corpo, "s3")
    assert "nao confere" in str(e.value)


# ── A API, contra um servidor que responde como a do GitHub ─────

class _ApiFalsa(http.server.BaseHTTPRequestHandler):
    recebidos = []

    def log_message(self, *a):
        pass

    def _responder(self, status, corpo, extra=None):
        dados = json.dumps(corpo).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-RateLimit-Remaining", "4999")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        _ApiFalsa.recebidos.append(("GET", self.path, dict(self.headers)))
        base = f"http://127.0.0.1:{self.server.server_port}"
        if self.path.startswith("/repos/dono/repo/issues"):
            if "page=2" in self.path:
                return self._responder(200, [{"number": 3}, {"number": 4, "pull_request": {}}])
            return self._responder(200, [{"number": 1}, {"number": 2}], {
                "Link": f'<{base}/repos/dono/repo/issues?state=open&per_page=100&page=2>; rel="next", '
                        f'<{base}/repos/dono/repo/issues?page=2>; rel="last"'})
        if self.path == "/repos/dono/repo":
            return self._responder(200, {"full_name": "dono/repo"})
        return self._responder(404, {"message": "Not Found"})

    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        corpo = json.loads(self.rfile.read(tamanho) or b"{}")
        _ApiFalsa.recebidos.append(("POST", self.path, corpo))
        if self.path.endswith("/dispatches"):
            self.send_response(204)
            self.end_headers()
            return
        if self.path.endswith("/issues") and not corpo.get("title"):
            return self._responder(422, {"message": "Validation Failed"})
        return self._responder(201, {"ok": True, "recebido": corpo})


@pytest.fixture
def api():
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _ApiFalsa)
    t = threading.Thread(target=servidor.serve_forever, daemon=True)
    t.start()
    _ApiFalsa.recebidos = []
    yield G["cliente"]("tok-de-teste", f"http://127.0.0.1:{servidor.server_port}", 5)
    servidor.shutdown()


def test_manda_os_cabecalhos_que_a_api_pede(api):
    api.repositorio("dono/repo")
    cab = {k.lower(): v for k, v in _ApiFalsa.recebidos[0][2].items()}
    assert cab["authorization"] == "Bearer tok-de-teste"
    assert cab["accept"] == "application/vnd.github+json"
    assert cab["x-github-api-version"] == "2022-11-28"


def test_pagina_pelo_link_e_tira_os_prs_das_issues(api):
    issues = api.issues("dono/repo")
    assert [i["number"] for i in issues] == [1, 2, 3]
    assert api.limite == 4999


def test_404_vira_erro_com_a_mensagem_e_a_dica(api):
    with pytest.raises(Exception) as e:
        api.repositorio("dono/nao-existe")
    assert "404" in str(e.value) and "Not Found" in str(e.value)


def test_criar_issue_comentar_release_e_disparar(api):
    api.criar_issue("dono/repo", "Falhou", "o CI", ["bug"])
    api.comentar("dono/repo", 7, "olhando")
    api.criar_release("dono/repo", "v1.2.0", notas="notas")
    assert api.disparar_workflow("dono/repo", "ci.yml", "main", {"alvo": "prod"})
    caminhos = [r[1] for r in _ApiFalsa.recebidos]
    assert "/repos/dono/repo/issues" in caminhos
    assert "/repos/dono/repo/issues/7/comments" in caminhos
    assert _ApiFalsa.recebidos[0][2]["labels"] == ["bug"]
    assert _ApiFalsa.recebidos[2][2]["name"] == "v1.2.0"
    assert _ApiFalsa.recebidos[3][2] == {"ref": "main", "inputs": {"alvo": "prod"}}


def test_o_que_se_recusa_antes_de_ir_a_rede(api):
    with pytest.raises(Exception):
        api.criar_issue("dono/repo", "   ")
    with pytest.raises(Exception):
        api.repositorio("sem-barra")
    with pytest.raises(Exception) as e:
        api.status("dono/repo", "abc", "ok")
    assert "success" in str(e.value)
    assert _ApiFalsa.recebidos == []


def test_o_token_nunca_aparece_em_texto(api):
    assert "tok-de-teste" not in repr(api) and "tok-de-teste" not in str(api)


def test_do_dataforge(tmp_path):
    import subprocess
    f = tmp_path / "g.df"
    f.write_text(
        'adopt Arcane.GitHub as GH\n'
        'a := GH.anotacao("erro", "quebrou", "src/x.df", 3)\n'
        'assert a is "::error file=src/x.df,line=3::quebrou"\n'
        'assert GH.conferir_webhook("It\'s a Secret to Everybody", "Hello, World!",\n'
        '    "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17")\n',
        encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "run", str(f)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=RAIZ)
    assert r.returncode == 0, r.stdout + r.stderr
