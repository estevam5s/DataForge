# -*- coding: utf-8 -*-
"""Arcane.Dominio — as pecas de DDD, cobradas.

O que se testa aqui nao e que as pecas existem: e que elas RECUSAM.
Um agregado que aceita estado invalido, um valor que muda, um evento
publicado antes da confirmacao — os tres sao o modelo nao valendo nada,
e nenhum deles levanta erro por conta propria.
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib import get_module                       # noqa: E402
from dataforge.errors import erro_por_nome                    # noqa: E402

#: A familia inteira. Todo teste captura por ela, e os que se
#: importam com a distincao conferem a classe exata — que e o
#: que faz um 'handle' especifico valer alguma coisa.
DominioError = erro_por_nome("DomainError")


@pytest.fixture
def D():
    return get_module("Arcane.Dominio")


# ═══════════════════════════════════════════════════════════
#  Valor
# ═══════════════════════════════════════════════════════════

def test_dois_valores_iguais_sao_o_mesmo_valor(D):
    Dinheiro = D["valor"]("Dinheiro", ["quantia", "moeda"])
    assert Dinheiro(10, "BRL") == Dinheiro(10, "BRL")
    assert Dinheiro(10, "BRL") != Dinheiro(11, "BRL")
    assert Dinheiro(10, "BRL") != Dinheiro(10, "USD")


def test_o_valor_serve_de_chave_porque_tem_hash(D):
    Dinheiro = D["valor"]("Dinheiro", ["quantia", "moeda"])
    contagem = {Dinheiro(10, "BRL"): "dez"}
    assert contagem[Dinheiro(10, "BRL")] == "dez"


def test_o_valor_nao_muda(D):
    Dinheiro = D["valor"]("Dinheiro", ["quantia", "moeda"])
    dez = Dinheiro(10, "BRL")
    with pytest.raises(DominioError) as erro:
        dez.quantia = 99
    assert "objeto de valor" in str(erro.value)


def test_com_devolve_outro_e_nao_mexe_no_original(D):
    Dinheiro = D["valor"]("Dinheiro", ["quantia", "moeda"])
    dez = Dinheiro(10, "BRL")
    vinte = dez.com(quantia=20)
    assert vinte.quantia == 20
    assert dez.quantia == 10


def test_com_recusa_campo_que_nao_existe(D):
    """Um campo a mais e um erro de digitacao passando calado."""
    Dinheiro = D["valor"]("Dinheiro", ["quantia", "moeda"])
    with pytest.raises(DominioError) as erro:
        Dinheiro(10, "BRL").com(quantiaa=20)
    assert "quantiaa" in str(erro.value)


def test_a_regra_e_cobrada_na_criacao(D):
    Dinheiro = D["valor"](
        "Dinheiro", ["quantia", "moeda"],
        regra=lambda v: v["quantia"] >= 0,
        motivo="dinheiro nao e negativo")
    assert Dinheiro(0, "BRL").quantia == 0
    with pytest.raises(DominioError) as erro:
        Dinheiro(-5, "BRL")
    assert "nao e negativo" in str(erro.value)


def test_a_regra_tambem_vale_no_com(D):
    """Um refinamento que so valesse na criacao e uma sugestao."""
    Positivo = D["valor"]("Positivo", ["n"], regra=lambda v: v["n"] > 0)
    with pytest.raises(DominioError):
        Positivo(5).com(n=-1)


def test_uma_regra_quebrada_e_um_bug_da_regra(D):
    """E nao um valor invalido — dizer 'invalido' esconderia o defeito."""
    Ruim = D["valor"]("Ruim", ["n"], regra=lambda v: v["naoexiste"] > 0)
    with pytest.raises(DominioError) as erro:
        Ruim(1)
    assert "estourou" in str(erro.value)


def test_o_valor_nasce_completo(D):
    Dinheiro = D["valor"]("Dinheiro", ["quantia", "moeda"])
    with pytest.raises(DominioError) as erro:
        Dinheiro(10)
    assert "moeda" in str(erro.value)


# ═══════════════════════════════════════════════════════════
#  Entidade
# ═══════════════════════════════════════════════════════════

def test_a_entidade_e_igual_por_identidade_e_nao_por_conteudo(D):
    a = D["entidade"]("Pessoa", "1", nome="Ana")
    b = D["entidade"]("Pessoa", "1", nome="Beatriz")
    c = D["entidade"]("Pessoa", "2", nome="Ana")
    assert a == b          # a MESMA pessoa, com outro nome
    assert a != c          # duas pessoas com o mesmo nome


def test_a_entidade_de_tipos_diferentes_nao_colide(D):
    assert D["entidade"]("Pessoa", "1") != D["entidade"]("Pedido", "1")


def test_a_entidade_muda(D):
    p = D["entidade"]("Pessoa", "1", nome="Ana")
    p.mudar(nome="Ana Maria")
    assert p.ler("nome") == "Ana Maria"


def test_novo_id_nao_repete(D):
    assert len({D["novo_id"]() for _ in range(500)}) == 500


# ═══════════════════════════════════════════════════════════
#  Agregado
# ═══════════════════════════════════════════════════════════

def _pedido(D, total=0):
    p = D["agregado"]("Pedido", "p-1", total=total, itens=0)
    p.invariante("o total nunca e negativo", lambda a: a.ler("total", 0) >= 0)
    return p


def test_o_estado_so_muda_por_comando(D):
    p = _pedido(D)
    with pytest.raises(DominioError) as erro:
        p.mudar(total=-999)
    assert "comando" in str(erro.value)


def test_o_comando_muda_e_avanca_a_versao(D):
    p = _pedido(D)
    p.comando("acrescentar", lambda a, preco: a.mudar(total=a.ler("total", 0) + preco))
    assert p.versao() == 0
    p.acrescentar(50)
    assert p.ler("total") == 50
    assert p.versao() == 1


def test_a_invariante_e_cobrada_na_saida_do_comando(D):
    p = _pedido(D, total=10)
    p.comando("descontar", lambda a, v: a.mudar(total=a.ler("total", 0) - v))
    with pytest.raises(DominioError) as erro:
        p.descontar(999)
    assert "o total nunca e negativo" in str(erro.value)


def test_o_comando_que_falha_no_meio_nao_deixa_metade(D):
    """Sem o desfazer, a proxima leitura ve um estado que nunca deveria existir."""
    p = _pedido(D, total=10)

    def quebrado(a):
        a.mudar(total=999)
        a.mudar(itens=7)
        raise ValueError("caiu aqui")

    p.comando("quebrado", quebrado)
    with pytest.raises(Exception):
        p.quebrado()
    assert p.ler("total") == 10
    assert p.ler("itens") == 0
    assert p.versao() == 0


def test_o_comando_recusado_pela_invariante_tambem_desfaz(D):
    p = _pedido(D, total=10)
    p.comando("zerar_errado", lambda a: a.mudar(total=-1, itens=99))
    with pytest.raises(DominioError):
        p.zerar_errado()
    assert p.ler("total") == 10
    assert p.ler("itens") == 0


def test_o_evento_do_comando_desfeito_tambem_some(D):
    """Um fato de um comando que nao aconteceu e a pior classe de evento."""
    p = _pedido(D, total=10)

    def quebrado(a):
        a.aconteceu("TotalMudado", {"de": 10, "para": 0})
        a.mudar(total=-1)

    p.comando("quebrado", quebrado)
    with pytest.raises(DominioError):
        p.quebrado()
    assert p.eventos() == []


def test_uma_invariante_quebrada_e_um_bug_dela(D):
    p = D["agregado"]("Pedido", "p-1")
    p.invariante("impossivel", lambda a: a.naoExiste())
    p.comando("mexer", lambda a: a.mudar(x=1))
    with pytest.raises(DominioError) as erro:
        p.mexer()
    assert "estourou" in str(erro.value)


def test_o_comando_serve_de_decorador(D):
    p = _pedido(D)

    @p.comando("somar")
    def somar(a, v):
        a.mudar(total=a.ler("total", 0) + v)

    p.somar(7)
    assert p.ler("total") == 7


def test_conferir_pode_ser_chamado_a_mao(D):
    assert _pedido(D, total=5).conferir() is True


# ═══════════════════════════════════════════════════════════
#  Evento
# ═══════════════════════════════════════════════════════════

def test_o_evento_nao_muda(D):
    e = D["evento"]("PedidoPago", {"valor": 10})
    with pytest.raises(DominioError) as erro:
        e.valor = 20
    assert "ja aconteceu" in str(erro.value)


def test_o_evento_sabe_de_onde_veio(D):
    p = _pedido(D)
    p.comando("marcar", lambda a: a.aconteceu("PedidoCriado", {"x": 1}))
    p.marcar()
    fato = p.eventos()[0]
    assert fato.nome == "PedidoCriado"
    assert fato.origem == "p-1"
    assert fato.tipo == "Pedido"
    assert fato.dados["x"] == 1


def test_limpar_eventos_devolve_e_esvazia(D):
    p = _pedido(D)
    p.comando("marcar", lambda a: a.aconteceu("A"))
    p.marcar()
    assert len(p.limpar_eventos()) == 1
    assert p.eventos() == []


def test_o_evento_sem_nome_e_recusado(D):
    with pytest.raises(DominioError):
        D["evento"]("")


# ═══════════════════════════════════════════════════════════
#  Regra
# ═══════════════════════════════════════════════════════════

class _P:
    def __init__(self, idade, pais):
        self.idade, self.pais = idade, pais


def test_a_regra_combina(D):
    maior = D["regra"]("maior de idade", lambda p: p.idade >= 18)
    brasil = D["regra"]("mora no Brasil", lambda p: p.pais == "BR")
    pode = maior.e(brasil)

    assert pode.vale(_P(20, "BR"))
    assert not pode.vale(_P(15, "BR"))
    assert not pode.vale(_P(20, "US"))


def test_o_por_que_nao_aponta_A_PARTE_que_falhou(D):
    """A frase inteira nao diz o que o usuario precisa resolver."""
    maior = D["regra"]("maior de idade", lambda p: p.idade >= 18)
    brasil = D["regra"]("mora no Brasil", lambda p: p.pais == "BR")
    pode = maior.e(brasil)

    assert pode.por_que_nao(_P(15, "BR")) == "maior de idade"
    assert pode.por_que_nao(_P(20, "US")) == "mora no Brasil"
    assert pode.por_que_nao(_P(20, "BR")) == ""


def test_ou_e_nao(D):
    maior = D["regra"]("maior", lambda p: p.idade >= 18)
    brasil = D["regra"]("brasil", lambda p: p.pais == "BR")
    assert maior.ou(brasil).vale(_P(15, "BR"))
    assert not maior.ou(brasil).vale(_P(15, "US"))
    assert maior.nao().vale(_P(15, "BR"))


def test_a_regra_da_decisao_e_a_mesma_da_consulta(D):
    maior = D["regra"]("maior", lambda p: p.idade >= 18)
    pessoas = [_P(10, "BR"), _P(20, "BR"), _P(30, "US")]
    assert len(maior.filtrar(pessoas)) == 2


def test_uma_regra_quebrada_nao_devolve_nao_vale(D):
    r = D["regra"]("ruim", lambda p: p.naoExiste)
    with pytest.raises(DominioError) as erro:
        r.vale(_P(1, "BR"))
    assert "estourou" in str(erro.value)


# ═══════════════════════════════════════════════════════════
#  Repositorio
# ═══════════════════════════════════════════════════════════

def test_guarda_e_recupera_por_id(D):
    repo = D["repositorio"]("Pedido")
    p = _pedido(D)
    repo.guardar(p)
    assert repo.por_id("p-1") is p
    assert repo.quantos() == 1


def test_por_id_devolve_void_e_exigir_levanta(D):
    repo = D["repositorio"]("Pedido")
    assert repo.por_id("nao-existe") is None
    with pytest.raises(DominioError) as erro:
        repo.exigir("nao-existe")
    assert "nao-existe" in str(erro.value)


def test_um_objeto_de_valor_nao_entra_num_repositorio(D):
    """Ele nao tem identidade — e nao tem porque dois iguais sao o mesmo."""
    Dinheiro = D["valor"]("Dinheiro", ["quantia"])
    with pytest.raises(DominioError) as erro:
        D["repositorio"]("Dinheiro").guardar(Dinheiro(10))
    assert "identidade" in str(erro.value)


def test_apagar(D):
    repo = D["repositorio"]("Pedido")
    repo.guardar(_pedido(D))
    assert repo.apagar("p-1") is True
    assert repo.apagar("p-1") is False


def test_que_usa_a_regra(D):
    repo = D["repositorio"]("Pedido")
    for i, total in enumerate([10, 200, 3000]):
        a = D["agregado"]("Pedido", "p-%d" % i, total=total)
        repo.guardar(a)
    grandes = D["regra"]("grande", lambda p: p.ler("total", 0) >= 200)
    assert len(repo.que(grandes)) == 2


def test_repositorio_de_usa_o_armazem_de_fora(D):
    banco = {}
    repo = D["repositorio_de"](
        "Pedido",
        ler=lambda i: banco.get(i),
        gravar=lambda i, v: banco.__setitem__(i, v),
        apagar=lambda i: banco.pop(i, None) is not None,
        listar=lambda: list(banco.values()))
    repo.guardar(_pedido(D))
    assert "p-1" in banco
    assert repo.por_id("p-1") is not None
    assert repo.quantos() == 1
    assert repo.apagar("p-1") is True
    assert banco == {}


# ═══════════════════════════════════════════════════════════
#  Unidade de trabalho
# ═══════════════════════════════════════════════════════════

def test_o_evento_so_sai_na_confirmacao(D):
    publicados = []
    p = _pedido(D)
    p.comando("marcar", lambda a: a.aconteceu("PedidoPago"))
    p.marcar()

    u = D["unidade"](publicar=publicados.append)
    u.registrar(p)
    assert publicados == []          # o mundo ainda nao sabe
    saindo = u.confirmar()
    assert len(saindo) == 1
    assert [e.nome for e in publicados] == ["PedidoPago"]


def test_desfazer_descarta_os_eventos(D):
    publicados = []
    p = _pedido(D)
    p.comando("marcar", lambda a: a.aconteceu("PedidoPago"))
    p.marcar()

    u = D["unidade"](publicar=publicados.append)
    u.registrar(p)
    u.desfazer()
    assert publicados == []
    assert p.eventos() == []


def test_a_unidade_grava_nos_repositorios(D):
    repo = D["repositorio"]("Pedido")
    u = D["unidade"]()
    u.registrar(_pedido(D), repo)
    assert repo.quantos() == 0
    u.confirmar()
    assert repo.quantos() == 1


def test_a_invariante_de_TODOS_e_conferida_antes_de_gravar_QUALQUER(D):
    """Senao a transacao de dominio vaza pela metade."""
    repo = D["repositorio"]("Pedido")
    bom = _pedido(D, total=10)

    ruim = D["agregado"]("Pedido", "p-2", total=10)
    ruim.invariante("sempre falha", lambda a: False)

    u = D["unidade"]()
    u.registrar(bom, repo)
    u.registrar(ruim, repo)
    with pytest.raises(DominioError):
        u.confirmar()
    assert repo.quantos() == 0


def test_nao_da_para_desfazer_o_confirmado(D):
    u = D["unidade"]()
    u.confirmar()
    with pytest.raises(DominioError) as erro:
        u.desfazer()
    assert "ja foi confirmado" in str(erro.value)
    # A saida esta na dica, e nao no texto: publicar um evento de compensacao.
    assert "compensacao" in erro.value.dica


def test_a_unidade_terminada_nao_recebe_mais(D):
    u = D["unidade"]()
    u.confirmar()
    with pytest.raises(DominioError):
        u.registrar(_pedido(D))


def test_eventos_pendentes_mostra_sem_publicar(D):
    p = _pedido(D)
    p.comando("marcar", lambda a: a.aconteceu("A"))
    p.marcar()
    u = D["unidade"]()
    u.registrar(p)
    assert [e.nome for e in u.eventos_pendentes()] == ["A"]
    assert p.eventos() != []


# ═══════════════════════════════════════════════════════════
#  Contexto delimitado
# ═══════════════════════════════════════════════════════════

def test_o_ouvinte_reage_ao_fato(D):
    vistos = []
    c = D["contexto"]("Vendas")
    c.ao_acontecer("PedidoPago", lambda e: vistos.append(e.dados["valor"]))
    c.publicar(D["evento"]("PedidoPago", {"valor": 42}))
    assert vistos == [42]


def test_um_ouvinte_que_estoura_nao_impede_os_outros(D):
    vistos = []
    c = D["contexto"]("Vendas")

    def explode(_e):
        raise ValueError("caiu")

    c.ao_acontecer("A", explode)
    c.ao_acontecer("A", lambda e: vistos.append(1))
    falhas = c.publicar(D["evento"]("A"))
    assert vistos == [1]
    assert len(falhas) == 1


def test_o_ao_acontecer_serve_de_decorador(D):
    vistos = []
    c = D["contexto"]("Vendas")

    @c.ao_acontecer("A")
    def anotar(e):
        vistos.append(e.nome)

    c.publicar(D["evento"]("A"))
    assert vistos == ["A"]


def test_atravessar_a_fronteira_exige_traducao(D):
    suporte = D["contexto"]("Suporte")
    with pytest.raises(DominioError) as erro:
        suporte.receber("Vendas", "Cliente", {"nome": "Ana", "credito": 500})
    assert "traduzir" in str(erro.value)


def test_a_traducao_deixa_so_o_que_este_lado_usa(D):
    suporte = D["contexto"]("Suporte")
    suporte.traduzir_de("Vendas", "Cliente",
                        lambda v: {"nome": v["nome"], "plano": "basico"})
    aqui = suporte.receber("Vendas", "Cliente",
                           {"nome": "Ana", "credito": 500})
    assert aqui == {"nome": "Ana", "plano": "basico"}
    assert "credito" not in aqui


def test_o_repositorio_do_contexto_e_o_mesmo_entre_chamadas(D):
    c = D["contexto"]("Vendas")
    assert c.repositorio("Pedido") is c.repositorio("Pedido")
    assert c.repositorios() == ["Pedido"]


# ═══════════════════════════════════════════════════════════
#  A classe do erro E o contrato
# ═══════════════════════════════════════════════════════════
#
# Levantar `RuntimeError` em tudo faria a distincao morrer na
# fronteira: para quem escreve o `handle`, violar uma invariante e
# dividir por zero viram a mesma coisa. Estes testes cobram que cada
# peca levante a sua — e que a base continue pegando todas.

def _classe(nome):
    return erro_por_nome(nome)


@pytest.mark.parametrize("classe,fazer", [
    ("ValueObjectError",
     lambda D: D["valor"]("Dinheiro", ["q"], regra=lambda v: False)(1)),
    ("ValueObjectError",
     lambda D: D["valor"]("Dinheiro", ["q", "m"])(1)),
    ("IdentityError",
     lambda D: D["repositorio"]("X").guardar(
         D["valor"]("Dinheiro", ["q"])(1))),
    ("RepositoryError",
     lambda D: D["repositorio"]("X").exigir("nao-existe")),
    ("EventError", lambda D: D["evento"]("")),
    ("SpecificationError",
     lambda D: D["regra"]("ruim", lambda p: p.naoExiste).vale(object())),
    ("BoundedContextError",
     lambda D: D["contexto"]("A").receber("B", "C", {})),
])
def test_cada_peca_levanta_a_sua_classe(D, classe, fazer):
    alvo = _classe(classe)
    assert alvo is not None, classe
    with pytest.raises(alvo):
        fazer(D)


def test_o_agregado_levanta_AggregateError_nas_duas_recusas(D):
    alvo = _classe("AggregateError")
    p = _pedido(D, total=10)
    p.comando("descontar", lambda a, v: a.mudar(total=a.ler("total", 0) - v))

    with pytest.raises(alvo):
        p.mudar(total=-1)          # escrita fora de comando
    with pytest.raises(alvo):
        p.descontar(999)           # invariante violada


def test_a_unidade_levanta_UnitOfWorkError(D):
    alvo = _classe("UnitOfWorkError")
    u = D["unidade"]()
    u.confirmar()
    with pytest.raises(alvo):
        u.desfazer()
    with pytest.raises(alvo):
        u.confirmar()


def test_o_evento_alterado_levanta_EventError(D):
    with pytest.raises(_classe("EventError")):
        D["evento"]("PedidoPago").dados = {}


def test_a_base_pega_todas(D):
    """`handle DomainError` sem listar os nove casos."""
    base = _classe("DomainError")
    for nome in ["ValueObjectError", "IdentityError", "AggregateError",
                 "EventError", "SpecificationError", "RepositoryError",
                 "UnitOfWorkError", "BoundedContextError"]:
        assert issubclass(_classe(nome), base), nome


def test_a_familia_do_dominio_nao_pega_um_erro_de_fora(D):
    """Senao `handle DomainError` viraria um `handle` sem tipo."""
    base = _classe("DomainError")
    assert not issubclass(_classe("DivisionByZeroError"), base)
    assert not issubclass(_classe("FileNotFoundError_"), base)
