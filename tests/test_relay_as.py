"""'relay novo as antigo' — renomear sem quebrar quem usa o nome velho.

Uma biblioteca que renomeia uma ação quebra todo programa que chama o
nome antigo. Com 'relay novo, novo as antigo' os dois nomes saem, e o
objeto é o MESMO — e o 'dataforge abi' concorda que a versão nova não
quebra a anterior, que é a prova de que o recurso serve ao que existe.
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LIB_V1 = "action total(v):\n    yield v * 2\n\nrelay total\n"
LIB_V2 = ("action total_com_imposto(v):\n    yield v * 2\n\n"
          "relay total_com_imposto, total_com_imposto as total\n")


def _df(*args, cwd):
    return subprocess.run([sys.executable, "-m", "dataforge", *args], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=dict(os.environ, NO_COLOR="1"))


def test_os_dois_nomes_saem_e_sao_o_mesmo_objeto(tmp_path):
    (tmp_path / "lib.df").write_text(LIB_V2)
    (tmp_path / "m.df").write_text(
        "adopt ./lib as L\nassert L.total is L.total_com_imposto\n"
        "assert L.total(21) is 42\n")
    r = _df("run", "m.df", cwd=tmp_path)
    assert r.returncode == 0, r.stdout


def test_so_o_apelido_esconde_o_nome_local(tmp_path):
    (tmp_path / "lib.df").write_text("action interno(x):\n    yield x\nrelay interno as publico\n")
    (tmp_path / "m.df").write_text("adopt ./lib as L\nassert L.publico(3) is 3\nL.interno(1)\n")
    r = _df("run", "m.df", cwd=tmp_path)
    assert r.returncode == 1 and "interno" in r.stdout
    c = _df("check", "m.df", cwd=tmp_path)
    assert "interno" in c.stdout and "erro" in c.stdout


def test_o_check_confere_o_apelido_como_confere_o_nome(tmp_path):
    (tmp_path / "lib.df").write_text(LIB_V2)
    (tmp_path / "m.df").write_text("adopt ./lib as L\nL.totl(1)\nL.total(1, 2)\n")
    c = _df("check", "m.df", cwd=tmp_path)
    assert "'total'" in c.stdout            # a sugestao
    assert "recebe 1" in c.stdout or "takes 1" in c.stdout


def test_nome_exportado_duas_vezes_e_recusado(tmp_path):
    (tmp_path / "d.df").write_text("action a():\n    yield 1\nrelay a as b, a as b\n")
    c = _df("check", "d.df", cwd=tmp_path)
    assert "exported twice" in c.stdout


def test_renomear_com_apelido_nao_quebra_a_abi(tmp_path):
    (tmp_path / "v1.df").write_text(LIB_V1)
    (tmp_path / "v2.df").write_text(LIB_V2)
    r = _df("abi", "v1.df", "v2.df", "--json", cwd=tmp_path)
    assert r.returncode == 0, r.stdout
    dados = json.loads(r.stdout)
    assert dados["veredito"] == "menor" and dados["quebras"] == []


def test_renomear_sem_apelido_quebra(tmp_path):
    (tmp_path / "v1.df").write_text(LIB_V1)
    (tmp_path / "v2.df").write_text("action total_com_imposto(v):\n    yield v * 2\nrelay total_com_imposto\n")
    r = _df("abi", "v1.df", "v2.df", cwd=tmp_path)
    assert r.returncode != 0 and "MAIOR" in r.stdout
