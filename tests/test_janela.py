# -*- coding: utf-8 -*-
"""Arcane.Janela — a aplicação de mesa, testada sem display nenhum.

Uma biblioteca de interface que só funciona com display é uma
biblioteca **sem teste**: o runner do CI não tem display. Por isso a
árvore é separada do desenho, e a `Sonda` monta a mesma árvore que o Tk
desenharia — ela não simula nada.

O que está aqui e o que fica de fora, dito sem rodeio:

| Camada | Coberta |
|---|---|
| a árvore, o estado, os eventos | **sim**, e é a maior parte |
| a Sonda: digitar, clicar, escolher | sim |
| o desenho com Tk | só com display — `test_a_janela_abre_de_verdade` |
| a aparência (fonte, espaçamento, cor) | **não**, e nenhum teste finge isso |
"""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module                        # noqa: E402

J = get_module("Arcane.Janela")


def tela_simples(t):
    t.titulo("Cadastro")
    nome = t.entrada("Nome", "")
    if t.botao("Salvar"):
        if not nome:
            t.erro("o nome é obrigatório")
        else:
            t.aviso(f"salvo: {nome}")
    return nome


# ═══════════════════════════════════════════════════════════
#  A árvore
# ═══════════════════════════════════════════════════════════

def test_a_tela_e_um_programa_de_cima_para_baixo():
    """Cada chamada devolve o VALOR daquele campo — é o que dispensa o
    grafo de callbacks."""
    s = J["testar"](tela_simples)
    assert s.tem("Cadastro")
    assert s.campos() == ["Nome"]
    assert s.botoes() == ["Salvar"]


def test_o_valor_digitado_volta_para_o_programa():
    s = J["testar"](tela_simples)
    s.digitar("Nome", "café")
    assert s.valor("Nome") == "café"


def test_o_clique_vale_para_UMA_execucao():
    """Se ele ficasse guardado, a próxima reexecução salvaria o
    formulário de novo — o defeito clássico de quem monta isto à mão."""
    salvos = []

    def tela(t):
        t.entrada("Nome", "")
        if t.botao("Salvar"):
            salvos.append(1)

    s = J["testar"](tela)
    s.clicar("Salvar")
    assert len(salvos) == 1

    s.digitar("Nome", "x")       # reexecuta
    assert len(salvos) == 1


def test_dois_campos_com_o_MESMO_rotulo_nao_dividem_estado():
    """Sem o contador na chave, digitar num mudaria o outro."""
    def tela(t):
        a = t.entrada("Valor", "a")
        b = t.entrada("Valor", "b")
        t.texto(f"{a}|{b}")

    s = J["testar"](tela)
    assert s.tem("a|b")


def test_o_estado_sobrevive_entre_as_execucoes():
    def tela(t):
        n = t.numero("Quantidade", 1)
        t.texto(f"vale {n}")

    s = J["testar"](tela)
    s.digitar("Quantidade", 7)
    assert s.tem("vale 7")
    s.clicar  # nenhuma ação: o estado continua
    assert s.valor("Quantidade") == 7


# ═══════════════════════════════════════════════════════════
#  Os componentes
# ═══════════════════════════════════════════════════════════

def test_a_tabela_aceita_vault_e_lista():
    def tela(t):
        t.tabela(["nome", "qtd"], [{"nome": "café", "qtd": 2}])
        t.tabela(["a", "b"], [["x", "y"]])

    s = J["testar"](tela)
    tabelas = s.tabelas()
    assert tabelas[0]["linhas"] == [["café", "2"]]
    assert tabelas[1]["linhas"] == [["x", "y"]]


def test_a_escolha_sem_opcao_nenhuma_e_recusada():
    with pytest.raises(Exception) as info:
        J["testar"](lambda t: t.escolha("Cor", []))
    assert "nao tem opcao nenhuma" in str(info.value)


def test_escolher_o_que_nao_esta_na_lista_e_recusado():
    s = J["testar"](lambda t: t.escolha("Cor", ["azul", "verde"]))
    with pytest.raises(Exception) as info:
        s.escolher("Cor", "roxo")
    assert "roxo" in str(info.value)
    assert "azul, verde" in info.value.nota


def test_o_grupo_precisa_ser_fechado():
    def tela(t):
        t.grupo("Dados")
        t.entrada("Nome")
        t.fim()
        t.texto("fora do grupo")

    s = J["testar"](tela)
    assert s.tem("Dados") and s.tem("fora do grupo")


def test_fechar_grupo_que_nao_foi_aberto_e_erro():
    with pytest.raises(Exception) as info:
        J["testar"](lambda t: t.fim())
    assert "nao ha grupo aberto" in str(info.value)


def test_o_progresso_e_limitado_entre_0_e_1():
    def tela(t):
        t.texto(str(t.progresso(2.5)))
        t.texto(str(t.progresso(-1)))

    s = J["testar"](tela)
    assert s.tem("1.0") and s.tem("0.0")


def test_o_numero_volta_como_NUMERO():
    """Digitado, ele chega como texto — e `n + 1` daria concatenação."""
    s = J["testar"](lambda t: t.numero("Qtd", 0))
    s.digitar("Qtd", "42")
    assert J["montar"](lambda t: t.numero("Qtd", 0),
                       {"numero:Qtd": "42"}).arvore.filhos[0].valor == "42"
    # e o que a AÇÃO recebe é um inteiro
    vistos = []
    J["montar"](lambda t: vistos.append(t.numero("Qtd", 0)), {"numero:Qtd": "42"})
    assert vistos == [42]


# ═══════════════════════════════════════════════════════════
#  A Sonda
# ═══════════════════════════════════════════════════════════

def test_um_campo_que_nao_existe_lista_os_que_existem():
    s = J["testar"](tela_simples)
    with pytest.raises(Exception) as info:
        s.digitar("Nomee", "x")
    assert "Nome" in str(info.value)


def test_um_botao_que_nao_existe_lista_os_que_existem():
    s = J["testar"](tela_simples)
    with pytest.raises(Exception) as info:
        s.clicar("Salvarr")
    assert "Salvar" in str(info.value)


def test_o_fluxo_inteiro():
    s = J["testar"](tela_simples)
    s.clicar("Salvar")
    assert s.tem("o nome é obrigatório")

    s.digitar("Nome", "café")
    s.clicar("Salvar")
    assert s.tem("salvo: café")


def test_a_arvore_e_dado():
    """Ela vira vault — é o que permite conferi-la num instantâneo."""
    s = J["testar"](tela_simples)
    arvore = s.arvore()
    assert arvore["especie"] == "raiz"
    especies = [f["especie"] for f in arvore["filhos"]]
    assert especies == ["titulo", "entrada", "botao"]


# ═══════════════════════════════════════════════════════════
#  O display
# ═══════════════════════════════════════════════════════════

def test_tem_display_NAO_abre_janela_para_descobrir():
    """A primeira versão criava um `Tk()` de sondagem, e isso derrubou
    o processo inteiro no macOS — com um **crash**, e não com uma
    exceção, porque o Tk exige a thread principal e o programa roda
    numa thread própria. Uma pergunta que mata o processo é pior que
    nenhuma pergunta."""
    import inspect

    from dataforge.stdlib import arcane_janela

    corpo = inspect.getsource(arcane_janela.tem_display)
    # A docstring CITA o defeito, e procurar no texto inteiro acusaria a
    # frase que explica a correcao — o mesmo falso alarme que a
    # varredura de segredo teve de aprender a calar. Por isso o corte e
    # no fecha-aspas, e nao por comparacao com `__doc__`: o recuo dos
    # dois e diferente, e a comparacao nunca casa.
    sem_doc = corpo.split('"""', 2)[-1]
    assert "Tk()" not in sem_doc, "ele voltou a abrir uma janela para sondar"
    assert "tkinter" in sem_doc, "ele precisa ao menos conferir que o Tk existe"


def test_a_resposta_do_display_e_coerente_com_o_sistema():
    resposta = J["tem_display"]()
    assert resposta in (True, False)
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY") \
            and not os.environ.get("WAYLAND_DISPLAY"):
        assert resposta is False


@pytest.mark.skipif(not J["tem_display"](),
                    reason="sem display — e é assim no CI")
def test_a_janela_abre_de_verdade():
    """O que a Sonda não prova: o desenho.

    Ela fecha sozinha com `fechar_em`. Uma janela que só fecha no
    clique não tem como ser exercitada num teste, e o que não se
    exercita quebra calado.
    """
    def tela(t):
        t.titulo("Teste")
        t.texto("uma linha")
        t.entrada("Nome", "café")
        t.tabela(["a"], [["1"]])
        t.progresso(0.5)
        t.botao("Ok")

    estado = J["abrir"](J["app"]("Teste", 320, 240), tela, None, 400)
    assert isinstance(estado, dict)


def test_abrir_com_algo_que_nao_e_app_e_recusado():
    with pytest.raises(Exception) as info:
        J["abrir"]("não é um app", tela_simples)
    assert "espera um app" in str(info.value)


# ═══════════════════════════════════════════════════════════
#  Pela linguagem
# ═══════════════════════════════════════════════════════════

def test_pela_linguagem(tmp_path):
    from tests._df import rodar

    r = rodar(tmp_path, '''adopt Arcane.Janela as J

itens := []

action tela(t):
    t.titulo("Lista")
    nome := t.entrada("Nome", "")
    given t.botao("Adicionar"):
        given nome is not "":
            itens.append(nome)
    t.texto($"{len(itens)} item(ns)")
    t.tabela(["nome"], [[i] cycle i in itens])

s := J.testar(tela)
s.digitar("Nome", "café")
s.clicar("Adicionar")
assert s.tem("1 item(ns)")
assert itens is ["café"]
out "ok"
''')
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip().endswith("ok")
