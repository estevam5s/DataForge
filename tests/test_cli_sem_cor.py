"""NO_COLOR vale para a CLI inteira, e não só para o depurador.

`NO_COLOR` é o padrão de fato (no-color.org). O depurador e a marca já o
respeitavam; a CLI e os diagnósticos do `check`, não — um log de CI com
NO_COLOR=1 saía cheio de `\\x1b[1;31m`, e um script que procurava
"erro:" na saída não achava.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _check(tmp_path, env_extra, *flags):
    (tmp_path / "a.df").write_text("x := naoExiste\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "NO_COLOR"}
    env.update(env_extra, PYTHONPATH=RAIZ)
    return subprocess.run([sys.executable, "-m", "dataforge", "check", "a.df", *flags],
                          cwd=tmp_path, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env).stdout


def test_no_color_tira_a_cor_do_diagnostico_e_do_resumo(tmp_path):
    saida = _check(tmp_path, {"NO_COLOR": "1"})
    assert "\x1b[" not in saida
    # O que um script procura e o LUGAR — 'arquivo:linha:coluna' —, e ele
    # nao muda de idioma. A palavra ao lado e a moldura do relatorio, e
    # ela fala o idioma em vigor: afirma-la aqui era afirmar o idioma
    # sem querer, e a suite roda em ingles.
    assert "a.df:1:6: " in saida


def test_a_moldura_do_diagnostico_fala_o_idioma_em_vigor(tmp_path):
    """'erro:' em pt, 'error:' em en — e o lugar, igual nos dois.

    A camada de idioma traduzia as 530 mensagens e deixava de fora as
    quatro palavras que mais aparecem: `DF_IDIOMA=en` produzia
    `erro[DF0602]: Key "b" is not in this vault.` — um rotulo em
    portugues em cima de uma mensagem em ingles, na primeira linha.
    """
    from dataforge.idioma import palavra

    for codigo in ("pt", "en", "es"):
        saida = _check(tmp_path, {"NO_COLOR": "1", "DF_IDIOMA": codigo})
        assert f"a.df:1:6: {palavra('erro', para=codigo)}:" in saida, \
            f"{codigo}: {saida[:160]}"
        assert f"{palavra('aviso', para=codigo)}(s)" in saida


def test_a_flag_continua_valendo(tmp_path):
    assert "\x1b[" not in _check(tmp_path, {}, "--no-color")


def test_sem_nada_a_cor_continua(tmp_path):
    assert "\x1b[" in _check(tmp_path, {})
