"""A promessa de estabilidade, verificada em vez de escrita.

`doc/ESTABILIDADE.md` diz que acrescentar é livre e que tirar exige uma
versão maior. Prosa não impede ninguém de renomear um símbolo no meio de
um refactor — este teste impede.

`doc/superficie.json` é a foto do que é público: palavras reservadas,
funções embutidas, módulos e seus símbolos, apelidos, comandos da CLI e
códigos de erro. Se algo sumir dela, a suíte fica vermelha com o nome do
que sumiu.

**Como atualizar quando a remoção for mesmo o certo:** rode
`python3 scripts/gerar_superficie.py` no mesmo commit. Aí a mudança
aparece no diff, com nome e motivo, em vez de escapar sem ninguém ver.
"""

import json
import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

FOTO = os.path.join(RAIZ, "doc", "superficie.json")
GERADOR = os.path.join(RAIZ, "scripts", "gerar_superficie.py")


@pytest.fixture(scope="module")
def foto():
    assert os.path.exists(FOTO), \
        "a foto da superficie sumiu — rode scripts/gerar_superficie.py"
    with open(FOTO, encoding="utf-8") as f:
        return json.load(f)


def test_nada_sumiu_da_superficie_publica():
    """O teste que faz a promessa valer alguma coisa."""
    r = subprocess.run([sys.executable, GERADOR, "--check"],
                       capture_output=True, text=True, encoding="utf-8",
                       cwd=RAIZ, timeout=120)
    assert r.returncode == 0, (
        "algo publico foi removido ou renomeado.\n\n"
        + (r.stdout or "") + (r.stderr or "")
        + "\n  Se a remocao e deliberada, ela precisa de uma versao MAIOR "
          "(ver doc/ESTABILIDADE.md).\n"
          "  Atualize a foto no mesmo commit:\n"
          "      python3 scripts/gerar_superficie.py")


def test_a_foto_cobre_o_que_a_politica_promete(foto):
    """Se a foto parar de cobrir um campo, a promessa vira metade."""
    for campo in ("palavras", "embutidas", "modulos", "apelidos",
                  "comandos", "codigos_de_erro"):
        assert foto.get(campo), f"a foto nao tem '{campo}'"


def test_a_foto_e_da_versao_atual(foto):
    from dataforge import __version__
    assert foto["versao"] == __version__, (
        f"a foto e da {foto['versao']} e a linguagem esta na "
        f"{__version__} — rode scripts/gerar_superficie.py")


def test_a_politica_existe_e_cita_a_foto():
    """Um documento que não aponta para o mecanismo não é verificável."""
    caminho = os.path.join(RAIZ, "doc", "ESTABILIDADE.md")
    assert os.path.exists(caminho), "doc/ESTABILIDADE.md sumiu"
    texto = open(caminho, encoding="utf-8").read()
    assert "superficie.json" in texto
    assert "2.0.0" in texto, "a politica precisa dizer o que muda numa maior"


def test_os_numeros_da_politica_batem_com_a_realidade(foto):
    """A tabela de cobertura envelheceria em silêncio.

    Ela cita quantidades — 81 palavras, 36 módulos — e números escritos
    à mão foram, nesta sessão, a fonte de quinze mentiras no site.
    """
    import re

    texto = open(os.path.join(RAIZ, "doc", "ESTABILIDADE.md"),
                 encoding="utf-8").read()

    reais = {
        "palavras reservadas": len(foto["palavras"]),
        "funções embutidas": len(foto["embutidas"]),
        "módulos": len(foto["modulos"]),
        "comandos": len(foto["comandos"]),
        "códigos de erro": len(foto["codigos_de_erro"]),
    }
    for rotulo, quantos in reais.items():
        achado = re.search(r"\*\*(\d+) " + re.escape(rotulo), texto)
        assert achado, f"a politica nao cita mais '{rotulo}'"
        assert int(achado.group(1)) == quantos, (
            f"a politica diz {achado.group(1)} {rotulo}, sao {quantos}")


def test_todo_codigo_de_erro_da_foto_ainda_existe(foto):
    """O código é o que a política promete — a mensagem, não."""
    from dataforge.catalogo_erros import ERROS

    atuais = {ficha["codigo"] for ficha in ERROS}
    sumiram = sorted(set(foto["codigos_de_erro"]) - atuais)
    assert not sumiram, (
        f"codigo de erro removido: {sumiram}. Quem casa por codigo "
        f"— e a politica manda casar por codigo — para de funcionar.")
