"""Onde mora o módulo que um `adopt` pede.

A regra estava escrita em **dois** lugares — o interpretador, que precisa
carregar o arquivo, e o analisador, que precisa saber se ele existe — e
os dois divergiram do pior jeito possível.

Dois defeitos vinham disso, e os dois eram invisíveis:

1. O analisador fazia `nome.replace('.', os.sep)`, o que transforma
   `'./mod'` em `'//mod'`. **Todo `adopt` relativo de todo projeto**
   gerava um aviso "Module not found" falso: 62 no repositório, e 795 de
   795 num projeto de 21 mil linhas — cada aviso que o `check` emitia
   ali era mentira. O projeto tem um princípio explícito sobre isso: um
   falso alarme ensina o usuário a ignorar mensagens.

2. Um pacote não sabia se importar pelo **próprio nome**. O teste de uma
   biblioteca escreve `adopt validador`, e não `adopt ../src/main`,
   porque precisa exercitá-la pelo mesmo caminho que um usuário usaria.
   As suítes dos **vinte** pacotes deste repositório falhavam por isso,
   e a CI não apanhava — ela não rodava `dataforge test` em `packages/`.
"""

import os
import subprocess
import sys

import pytest

sys.path.insert(0, ".")

from dataforge import resolucao

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ═══════════════════════════════════════════════════════════
#  O bug do replace
# ═══════════════════════════════════════════════════════════

def test_um_caminho_relativo_nao_e_mutilado(tmp_path):
    """`'./mod'.replace('.', '/')` dá `'//mod'`."""
    (tmp_path / "mod.df").write_text("action f():\n    yield 1\n",
                                     encoding="utf-8")
    origem = str(tmp_path / "usa.df")
    assert resolucao.achar("./mod", origem) == str(tmp_path / "mod.df")


def test_o_relativo_resolve_contra_o_ARQUIVO_e_nao_o_cwd(tmp_path):
    """Mover a pasta inteira não pode quebrar nada, e ler o código deve
    bastar para saber o que ele importa."""
    pasta = tmp_path / "src"
    pasta.mkdir()
    (pasta / "vizinho.df").write_text("action f():\n    yield 1\n",
                                      encoding="utf-8")
    achado = resolucao.achar("./vizinho", str(pasta / "principal.df"))
    assert achado == str(pasta / "vizinho.df")


def test_sobe_uma_pasta(tmp_path):
    (tmp_path / "util.df").write_text("action f():\n    yield 1\n",
                                      encoding="utf-8")
    fundo = tmp_path / "a" / "b"
    fundo.mkdir(parents=True)
    assert resolucao.achar("../../util", str(fundo / "x.df")) == \
        str(tmp_path / "util.df")


def test_um_ponto_no_meio_continua_sendo_pasta(tmp_path):
    """`sub.modulo` é `sub/modulo` — o replace só estava errado para o
    caso relativo."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "modulo.df").write_text("action f():\n    yield 1\n",
                                   encoding="utf-8")
    assert resolucao.achar("sub.modulo", str(tmp_path / "x.df")) == \
        str(sub / "modulo.df")


def test_o_que_nao_existe_devolve_none(tmp_path):
    assert resolucao.achar("./nao-existe", str(tmp_path / "x.df")) is None


def test_o_analisador_nao_inventa_modulo_ausente(tmp_path):
    """O teste que mais importa: `check` sobre um projeto com imports
    relativos não emite um único aviso de módulo."""
    pasta = tmp_path / "src"
    pasta.mkdir()
    (pasta / "util.df").write_text(
        "action dobro(n):\n    yield n * 2\n\nrelay dobro\n", encoding="utf-8")
    (pasta / "main.df").write_text(
        "adopt ./util as U\n\nout U.dobro(4)\n", encoding="utf-8")

    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "check", "src/", "--no-color"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": RAIZ})
    assert "was not found" not in saida.stdout, saida.stdout
    assert saida.returncode == 0, saida.stdout


def test_o_repositorio_nao_tem_aviso_falso_de_modulo():
    """Eram 62. Os que sobram são os dois exercícios que demonstram um
    `adopt` que falha de propósito."""
    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "check", ".", "--no-color"],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": RAIZ})
    linhas = [l for l in saida.stdout.splitlines() if "was not found" in l]
    inesperados = [l for l in linhas if "NaoExiste" not in l]
    assert not inesperados, "avisos falsos de módulo:\n" + "\n".join(
        inesperados[:10])


# ═══════════════════════════════════════════════════════════
#  O pacote que se importa
# ═══════════════════════════════════════════════════════════

def test_um_pacote_se_importa_pelo_proprio_nome(tmp_path):
    (tmp_path / "forge.toml").write_text(
        '[package]\nname = "meupacote"\nversion = "1.0.0"\n'
        'entry = "src/main.df"\n', encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.df").write_text("action f():\n    yield 1\n\nrelay f\n",
                                 encoding="utf-8")
    testes = tmp_path / "tests"
    testes.mkdir()

    achado = resolucao.achar_no_proprio_pacote(
        "meupacote", str(testes / "meu_test.df"))
    assert achado == str(src / "main.df")


def test_o_nome_de_outro_pacote_nao_resolve(tmp_path):
    (tmp_path / "forge.toml").write_text(
        '[package]\nname = "meu"\nversion = "1.0.0"\n', encoding="utf-8")
    assert resolucao.achar_no_proprio_pacote(
        "outro", str(tmp_path / "x.df")) is None


def test_a_raiz_do_projeto_e_achada_de_qualquer_profundidade(tmp_path):
    (tmp_path / "forge.toml").write_text("[project]\nname = \"x\"\n",
                                         encoding="utf-8")
    fundo = tmp_path / "src" / "a" / "b"
    fundo.mkdir(parents=True)
    assert resolucao.raiz_do_projeto(str(fundo / "x.df")) == str(tmp_path)


def test_sem_forge_toml_nao_ha_raiz(tmp_path):
    assert resolucao.raiz_do_projeto(str(tmp_path / "solto.df")) is None


@pytest.mark.parametrize("pacote", sorted(
    nome for nome in os.listdir(os.path.join(RAIZ, "packages"))
    if os.path.isdir(os.path.join(RAIZ, "packages", nome))
    and os.path.isdir(os.path.join(RAIZ, "packages", nome, "tests"))))
def test_a_suite_de_cada_pacote_roda(pacote):
    """As vinte falhavam, e nada apanhava: a CI não roda `dataforge test`
    dentro de `packages/`.

    Um pacote com dependência declarada precisa de `dataforge install`
    antes; esse é pulado com a razão dita, em vez de falhar.
    """
    pasta = os.path.join(RAIZ, "packages", pacote)
    manifesto = open(os.path.join(pasta, "forge.toml"),
                     encoding="utf-8").read()
    bloco = manifesto.split("[dependencies]")[1].split("[")[0] \
        if "[dependencies]" in manifesto else ""
    tem_dependencia = any(
        "=" in linha and not linha.strip().startswith("#")
        for linha in bloco.splitlines())
    if tem_dependencia and not os.path.isdir(
            os.path.join(pasta, "forge_modules")):
        pytest.skip(f"'{pacote}' precisa de 'dataforge install' primeiro")

    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "test", "--no-color"],
        cwd=pasta, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": RAIZ})
    assert saida.returncode == 0, saida.stdout + saida.stderr
    assert "Tudo verde" in saida.stdout


# ═══════════════════════════════════════════════════════════
#  Os dois não podem divergir de novo
# ═══════════════════════════════════════════════════════════

def test_o_interpretador_e_o_analisador_usam_o_mesmo_resolvedor():
    """A divergência foi a causa dos dois bugs. Este teste proíbe a
    cópia voltar."""
    for arquivo in ("dataforge/typechecker.py", "dataforge/superficie.py"):
        fonte = open(os.path.join(RAIZ, arquivo), encoding="utf-8").read()
        # Só as linhas de código: o comentário que explica o bug cita a
        # expressão de propósito, e proibir a explicação seria proibir
        # justamente o que impede alguém de reintroduzi-lo.
        codigo = [l for l in fonte.splitlines()
                  if l.strip() and not l.strip().startswith("#")]
        culpadas = [l for l in codigo if "replace('.', os.sep)" in l]
        assert not culpadas, (
            f"{arquivo} voltou a resolver caminho à mão — use "
            f"resolucao.py:\n" + "\n".join(culpadas))

    interp = open(os.path.join(RAIZ, "dataforge/interpreter.py"),
                  encoding="utf-8").read()
    assert "from . import resolucao" in interp
