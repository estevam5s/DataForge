"""Os geradores de GitHub, GitLab, devcontainer, pre-commit e systemd —
e o `dataforge check --formato=github` que põe o erro na linha do PR.

Como em `test_devops.py`, o artefato é conferido como **dado** (YAML
lido, JSON lido), e não como texto: um workflow com a indentação errada
passa num teste de `in` e é recusado pelo GitHub.
"""
import json
import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import devops as g  # noqa: E402


def _yaml(texto):
    yaml = pytest.importorskip("yaml", reason="pyyaml ausente")
    return yaml.safe_load(texto)


@pytest.fixture
def servidor(tmp_path):
    (tmp_path / "forge.toml").write_text(
        '[project]\nname = "loja"\nversion = "1.0.0"\nentry = "src/main.df"\n')
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.df").write_text(
        'adopt Kiln\n\nserver api on 8080:\n    route GET "/":\n'
        '        respond json {"ok": yes}\n\nignite api\n', encoding="utf-8")
    p = g.Projeto(str(tmp_path))
    assert p.e_servidor, "a fixture precisa ser um servidor"
    return p


@pytest.fixture
def biblioteca():
    return g.Projeto(os.path.join(RAIZ, "packages", "validador"))


def _rodar(args, pasta):
    return subprocess.run([sys.executable, "-m", "dataforge", *args], cwd=pasta,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=dict(os.environ, PYTHONPATH=RAIZ,
                                                     NO_COLOR="1"))


# ── o release ───────────────────────────────────────────────────

def test_o_release_e_yaml_valido_com_a_permissao_minima(servidor):
    w = _yaml(g.github_release(servidor))
    assert w["permissions"] == {"contents": "write"}
    gatilho = w.get("on") or w.get(True)
    assert gatilho["push"]["tags"] == ["v*"]


def test_o_release_confere_a_tag_contra_o_manifesto_e_testa_de_novo(servidor):
    texto = g.github_release(servidor)
    assert "forge.toml" in texto and "github.ref_name" in texto
    assert texto.index("dataforge test") < texto.index("gh release create")


def test_a_biblioteca_publica_o_pacote_e_nao_um_tar_da_pasta(biblioteca):
    assert "dataforge pack" in g.github_release(biblioteca)


# ── dependabot e modelos ────────────────────────────────────────

def test_o_dependabot_nao_promete_o_que_nao_le(servidor):
    d = _yaml(g.dependabot(servidor))
    ecossistemas = {u["package-ecosystem"] for u in d["updates"]}
    assert "github-actions" in ecossistemas
    assert not any("dataforge" in e or "forge" in e for e in ecossistemas)
    assert "NAO le o forge.toml" in g.dependabot(servidor)


def test_codeowners_protege_o_pipeline(servidor):
    t = g.codeowners(servidor, "@ana")
    assert "/.github/            @ana" in t and "forge.lock" in t


def test_o_formulario_de_bug_e_yaml_e_exige_a_versao(servidor):
    f = _yaml(g.issue_bug(servidor))
    versao = [c for c in f["body"] if c["id"] == "versao"][0]
    assert versao["validations"]["required"] is True


# ── outros ecossistemas ─────────────────────────────────────────

def test_o_gitlab_publica_o_junit_no_merge_request(servidor):
    c = _yaml(g.gitlab_ci(servidor))
    assert c["verificar"]["artifacts"]["reports"]["junit"] == "relatorio.xml"
    assert "dataforge check . --strict" in c["verificar"]["script"]


def test_o_devcontainer_e_json_e_abre_a_porta_do_servidor(servidor, biblioteca):
    d = json.loads(g.devcontainer(servidor))
    assert d["forwardPorts"] == [servidor.porta]
    assert "dataforge editor" in d["postCreateCommand"]
    assert json.loads(g.devcontainer(biblioteca))["forwardPorts"] == []


def test_o_pre_commit_usa_o_dataforge_instalado(servidor):
    c = _yaml(g.pre_commit(servidor))
    ganchos = c["repos"][0]["hooks"]
    assert {h["id"] for h in ganchos} >= {"dataforge-fmt", "dataforge-check"}
    assert all(h["language"] == "system" for h in ganchos)


def test_o_systemd_e_endurecido_e_o_comando_e_texto(servidor):
    t = g.systemd(servidor)
    for diretiva in ("NoNewPrivileges=true", "ProtectSystem=strict",
                     "ProtectHome=true", "User=dataforge"):
        assert diretiva in t
    execstart = [l for l in t.splitlines() if l.startswith("ExecStart=")][0]
    assert "[" not in execstart and execstart.endswith("dataforge run src/main.df")


def test_o_ci_do_github_pede_as_anotacoes(servidor):
    assert "dataforge check . --strict --formato=github" in g.ci_github(servidor)


# ── a CLI ───────────────────────────────────────────────────────

def test_devops_github_escreve_os_cinco_e_nao_sobrescreve(tmp_path):
    (tmp_path / "forge.toml").write_text('[project]\nname = "x"\nversion = "1.0.0"\n')
    r = _rodar(["devops", "github", "--dono=@ana"], tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    for arq in ("workflows/release.yml", "dependabot.yml", "CODEOWNERS",
                "pull_request_template.md", "ISSUE_TEMPLATE/bug.yml"):
        assert (tmp_path / ".github" / arq).is_file(), arq
    (tmp_path / ".github" / "CODEOWNERS").write_text("ajustado a mao\n")
    _rodar(["devops", "github"], tmp_path)
    assert (tmp_path / ".github" / "CODEOWNERS").read_text() == "ajustado a mao\n"


def test_devops_ci_gitlab_e_devcontainer(tmp_path):
    (tmp_path / "forge.toml").write_text('[project]\nname = "x"\n')
    assert _rodar(["devops", "ci", "gitlab"], tmp_path).returncode == 0
    assert _rodar(["devops", "devcontainer"], tmp_path).returncode == 0
    assert (tmp_path / ".gitlab-ci.yml").is_file()
    assert (tmp_path / ".devcontainer" / "devcontainer.json").is_file()


# ── check --formato=github ──────────────────────────────────────

def test_check_formato_github_anota_a_linha_e_sai_com_erro(tmp_path):
    f = tmp_path / "ruim.df"
    f.write_text("action f(a):\n    yield a\n\nf(1, 2)\n", encoding="utf-8")
    r = _rodar(["check", "ruim.df", "--formato=github"], tmp_path)
    assert r.returncode == 1
    anotacoes = [l for l in r.stdout.splitlines() if l.startswith("::error ")]
    assert len(anotacoes) == 1
    assert anotacoes[0].startswith("::error file=ruim.df,line=4,col=1,title=arity::")


def test_check_formato_github_numa_pasta_e_no_erro_de_sintaxe(tmp_path):
    (tmp_path / "a.df").write_text("x := naoExiste\n", encoding="utf-8")
    (tmp_path / "b.df").write_text("y := (1 +\n", encoding="utf-8")
    r = _rodar(["check", ".", "--formato=github"], tmp_path)
    linhas = r.stdout.splitlines()
    assert any(l.startswith("::error file=") and "a.df" in l for l in linhas)
    assert any("title=sintaxe" in l and "b.df" in l for l in linhas)


def test_sem_o_formato_a_saida_de_sempre_nao_muda(tmp_path):
    (tmp_path / "a.df").write_text("x := naoExiste\n", encoding="utf-8")
    r = _rodar(["check", "a.df"], tmp_path)
    assert "::error" not in r.stdout and "a.df:1:" in r.stdout
