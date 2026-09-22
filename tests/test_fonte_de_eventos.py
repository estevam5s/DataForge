"""Fonte de eventos: o armazém, reconstituir e a projeção.

O que importa conferir é o que cada peça RECUSA: o comando decidido
sobre um estado velho, o evento que o agregado não sabe aplicar, e o
registro que a projeção já contou.
"""
import os
import sys
import threading

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import erro_por_nome  # noqa: E402
from dataforge.stdlib import get_module  # noqa: E402
from tests._df import rodar  # noqa: E402

D = get_module("Arcane.Dominio")
Conflito = erro_por_nome("AggregateVersionError")

APLICAR = {
    "Aberta": lambda e, d: {"saldo": 0},
    "Depositado": lambda e, d: {**e, "saldo": e["saldo"] + d["valor"]},
    "Sacado": lambda e, d: {**e, "saldo": e["saldo"] - d["valor"]},
}


def test_a_versao_conta_os_eventos_do_fluxo():
    a = D["armazem"]()
    assert a.versao("x") == 0
    assert a.anexar("x", [{"nome": "Aberta"}, D["evento"]("Depositado", {"valor": 5})]) == 2
    assert [r["versao"] for r in a.ler("x")] == [1, 2]
    assert [r["versao"] for r in a.ler("x", 1)] == [2]


def test_versao_esperada_recusa_quem_decidiu_sobre_estado_velho():
    a = D["armazem"]()
    a.anexar("x", [{"nome": "Aberta"}])
    lido = a.versao("x")
    a.anexar("x", [{"nome": "Depositado", "dados": {"valor": 1}}], lido)
    with pytest.raises(Conflito, match="versao 2.*versao 1"):
        a.anexar("x", [{"nome": "Depositado", "dados": {"valor": 1}}], lido)
    assert a.versao("x") == 2          # nada entrou pela metade


def test_o_conflito_e_da_familia_do_dominio():
    assert issubclass(Conflito, erro_por_nome("DomainError"))


def test_duas_threads_com_a_mesma_leitura_so_uma_grava():
    a = D["armazem"]()
    a.anexar("x", [{"nome": "Aberta"}])
    lido = a.versao("x")
    resultados = []
    barreira = threading.Barrier(8)

    def tentar():
        barreira.wait()
        try:
            a.anexar("x", [{"nome": "Depositado", "dados": {"valor": 1}}], lido)
            resultados.append("ok")
        except Conflito:
            resultados.append("conflito")

    ts = [threading.Thread(target=tentar) for _ in range(8)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert resultados.count("ok") == 1 and a.versao("x") == 2


def test_a_posicao_global_e_a_ordem_de_todos():
    a = D["armazem"]()
    a.anexar("a", [{"nome": "Aberta"}])
    a.anexar("b", [{"nome": "Aberta"}])
    a.anexar("a", [{"nome": "Depositado", "dados": {"valor": 1}}])
    assert [(r["fluxo"], r["posicao"]) for r in a.todos()] == [("a", 1), ("b", 2), ("a", 3)]
    assert len(a.todos(2)) == 1 and a.fluxos() == ["a", "b"]


def test_reconstituir_e_estrito():
    eventos = [{"nome": "Aberta"}, {"nome": "Depositado", "dados": {"valor": 10}},
               {"nome": "Sacado", "dados": {"valor": 3}}]
    assert D["reconstituir"](eventos, APLICAR) == {"saldo": 7}
    with pytest.raises(erro_por_nome("EventError"), match="Estornado"):
        D["reconstituir"](eventos + [{"nome": "Estornado"}], APLICAR)


def test_aplicador_que_muda_no_lugar_pode_devolver_void():
    def depositar(e, d):
        e["saldo"] = e.get("saldo", 0) + d["valor"]
    assert D["reconstituir"]([{"nome": "D", "dados": {"valor": 4}}], {"D": depositar}) == {"saldo": 4}


def test_projecao_ignora_o_que_nao_lhe_interessa_e_nao_conta_duas_vezes():
    a = D["armazem"]()
    p = D["projecao"]({"Depositado": lambda e, d: {"total": e["total"] + d["valor"]}}, {"total": 0})
    a.assinar(p.aplicar)
    a.anexar("x", [{"nome": "Aberta"}, {"nome": "Depositado", "dados": {"valor": 5}}])
    assert p.estado() == {"total": 5} and p.posicao() == 2
    for r in a.todos():            # reentrega
        assert p.aplicar(r) is False
    assert p.estado() == {"total": 5}
    assert p.reconstruir(a.todos() + a.todos()) == {"total": 5}


def test_assinatura_cancelada_para_de_receber():
    a = D["armazem"]()
    vistos = []
    chave = a.assinar(vistos.append)
    a.anexar("x", [{"nome": "A"}])
    assert a.cancelar(chave) is True
    a.anexar("x", [{"nome": "B"}])
    assert [r["nome"] for r in vistos] == ["A"]


def test_na_linguagem_o_handle_pega_o_conflito(tmp_path):
    r = rodar(tmp_path, '''adopt Arcane.Dominio as D
a := D.armazem()
a.anexar("c", [{"nome": "Aberta"}])
v := a.versao("c")
a.anexar("c", [{"nome": "X"}], v)
monitor:
    a.anexar("c", [{"nome": "Y"}], v)
handle AggregateVersionError as e:
    out "recusado"
''')
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "recusado"


def test_o_campo_de_um_valor_vence_o_metodo_de_mesmo_nome():
    """`cliente.nome` devolvia o MÉTODO `nome()` da classe, e não "Ana"."""
    Cliente = D["valor"]("Cliente", ["nome", "campos", "com"])
    c = Cliente("Ana", "x", "y")
    assert c.nome == "Ana" and c.campos == "x" and c.com == "y"
    Dinheiro = D["valor"]("Dinheiro", ["quantia"])
    d = Dinheiro(10)
    assert d.nome() == "Dinheiro"          # sem campo 'nome', o método segue
    assert d.com(quantia=20).quantia == 20
