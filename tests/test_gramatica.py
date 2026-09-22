"""A gramática como dado, conferida contra o parser de verdade.

A EBNF da documentação era texto, e texto não é conferido: uma produção
podia descrever uma sintaxe que o parser já não aceita. Aqui cada
produção é passada pelo lexer e pelo parser, e precisa produzir os nós
que promete; cada afirmação de precedência e de associatividade é
conferida pela FORMA da árvore; e toda palavra reservada precisa
aparecer em alguma produção — uma palavra fora da gramática é uma parte
da linguagem que a documentação não descreve.
"""
import dataclasses
import os
import re
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import ast_nodes, gramatica as g  # noqa: E402
from dataforge.tokens import KEYWORDS  # noqa: E402


@pytest.mark.parametrize("p", g.PRODUCOES, ids=[p["nome"] for p in g.PRODUCOES])
def test_o_exemplo_de_cada_producao_produz_o_que_ela_promete(p):
    assert g.conferir_producao(p) is None, g.conferir_producao(p)


def test_os_nos_prometidos_existem_na_arvore_da_linguagem():
    for p in g.PRODUCOES:
        for classe in p["contem"]:
            assert dataclasses.is_dataclass(getattr(ast_nodes, classe, None)), \
                f"{p['nome']}: '{classe}' não é um nó de ast_nodes"


def test_toda_palavra_reservada_esta_em_alguma_producao():
    texto = " ".join(p["ebnf"] + " " + p["exemplo"] for p in g.PRODUCOES)
    presentes = set(re.findall(r"[a-z_]+", texto))
    fora = sorted(k for k in KEYWORDS if k not in presentes)
    assert not fora, f"palavras reservadas fora da gramática: {fora}"


def test_todo_grupo_tem_producao_e_toda_producao_tem_grupo():
    ids = [gid for gid, _n, _r in g.GRUPOS]
    assert all(g.do_grupo(gid) for gid in ids)
    assert all(p["grupo"] in ids for p in g.PRODUCOES)
    nomes = [p["nome"] for p in g.PRODUCOES]
    assert len(nomes) == len(set(nomes)), "duas produções com o mesmo nome"


@pytest.mark.parametrize("expr,raiz", g.CONFERENCIAS_DE_PRECEDENCIA)
def test_a_precedencia_decide_a_raiz(expr, raiz):
    assert g.raiz_da_expressao(expr) == raiz


@pytest.mark.parametrize("expr,lado,classe", g.CONFERENCIAS_DE_ASSOCIACAO)
def test_a_associatividade_decide_a_forma(expr, lado, classe):
    v = g._arvore(f"__x := {expr}").body[0].value
    assert type(getattr(v, lado)).__name__ == classe


def test_a_tabela_de_precedencia_e_uma_escada():
    niveis = [n["nivel"] for n in g.PRECEDENCIA]
    assert niveis == list(range(1, len(niveis) + 1))


def test_o_comentario_nao_vira_divisao():
    """'x := 7 // nota' é comentário; '7 // 2' seria divisão."""
    linha1 = [t for t in g.tokens("x := 7 // um comentario") if t["linha"] == 1]
    assert "FLOOR_DIV" not in {t["tipo"] for t in linha1}
    assert "FLOOR_DIV" in {t["tipo"] for t in g.tokens("x := 7 // 2")}


def test_o_separador_de_milhar_e_ignorado():
    assert g._arvore("x := 1_000_000").body[0].value.value == 1000000


def test_validar_nao_executa_e_aponta_a_linha(tmp_path):
    alvo = tmp_path / "nao-devia-existir"
    r = g.validar(f'adopt Arcane.IO as IO\nIO.write("{alvo}", "x")')
    assert r["ok"] and r["instrucoes"] == 2 and not alvo.exists()
    ruim = g.validar("x := (1 +")
    assert not ruim["ok"] and ruim["erros"][0]["linha"] == 2


def test_palavras_separa_reservadas_de_contextuais():
    p = g.palavras()
    assert set(p["reservadas"]) == set(KEYWORDS)
    assert "route" in p["contextuais"] and "route" not in p["reservadas"]


def _rodar(*args):
    return subprocess.run([sys.executable, "-m", "dataforge", *args], cwd=RAIZ,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=dict(os.environ, NO_COLOR="1"))


def test_a_cli_lista_mostra_e_recusa():
    assert f"{len(g.PRODUCOES)} producoes" in _rodar("gramatica").stdout
    assert "ternario      =" in _rodar("gramatica", "ternario").stdout
    assert _rodar("gramatica", "--ebnf").stdout.count(" = ") >= len(g.PRODUCOES)
    r = _rodar("gramatica", "ternaro")
    assert r.returncode == 1 and "ternario" in r.stdout


def test_do_dataforge(tmp_path):
    f = tmp_path / "g.df"
    f.write_text(
        'adopt Arcane.Gramatica as G\n'
        'assert G.raiz("1 + 2 * 3")[1] is "+"\n'
        'assert G.instrucoes("x := 1\\nout x") is ["Assignment", "OutStatement"]\n'
        'assert not G.validar("x := (1 +")["ok"]\n'
        'assert len(G.producoes("expressoes")) bigger 5\n', encoding="utf-8")
    r = _rodar("run", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
