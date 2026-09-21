# -*- coding: utf-8 -*-
"""Arcane.Politica.

Um motor de autorizacao erra de um jeito so: PERMITINDO. Um bug que
nega aparece no primeiro minuto — alguem reclama que nao consegue. Um
bug que permite nao aparece nunca, ate o incidente.

Por isso quase todo teste aqui cobra a RECUSA, e os tres que mais
importam sao:

  - o padrao e negar (uma acao nova nao nasce permitida);
  - a negacao explicita vence o papel (a excecao nao e apagada);
  - uma regra que FALHA nega (um bug na regra nao vira autorizacao).
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib import get_module  # noqa: E402

P = get_module("Arcane.Politica")


def erro_de(nome):
    from dataforge import errors
    return errors.erro_por_nome(nome)


@pytest.fixture
def loja():
    pol = P["motor"]("loja")
    pol.papel("leitor", ["pedido:ler"])
    pol.papel("editor", ["pedido:escrever"], herda=["leitor"])
    pol.papel("admin", ["pedido:apagar", "usuario:*"], herda=["editor"])
    return pol


ANA = {"id": "ana", "papel": "admin"}
BOB = {"id": "bob", "papel": "leitor"}


# ═══════════════════════════════════════════════════════════
#  O padrao, e a explicacao
# ═══════════════════════════════════════════════════════════

def test_o_padrao_e_negar(loja):
    """Uma acao que ninguem declarou nao nasce permitida."""
    d = loja.pode(ANA, "acao:inventada:agora")
    assert d["permitido"] is False
    assert d["regra"] == "padrao"


def test_sujeito_sem_papel_nao_pode_nada(loja):
    assert loja.pode({"id": "x"}, "pedido:ler")["permitido"] is False
    assert loja.pode({"id": "x", "papel": "inexistente"},
                     "pedido:ler")["permitido"] is False


def test_a_decisao_traz_o_motivo_e_nao_so_o_veredito(loja):
    """Um motor que responde so yes/no e impossivel de auditar: o
    incidente pergunta *por que ele conseguiu*."""
    d = loja.pode(ANA, "pedido:apagar")
    assert d["permitido"] is True
    assert d["motivo"] and d["regra"]
    assert d["sujeito"] == "ana" and d["acao"] == "pedido:apagar"


def test_o_motivo_nomeia_o_papel_que_REALMENTE_tem_a_permissao(loja):
    """Com `admin → editor → leitor`, dizer "o papel 'admin' permite
    'pedido:ler'" manda quem audita procurar num papel onde ela nao
    esta."""
    d = loja.pode(ANA, "pedido:ler")
    assert d["permitido"] is True
    assert "'leitor'" in d["motivo"], d["motivo"]
    assert "admin" in d["motivo"], "e por onde se chegou nele"
    assert d["regra"] == "papel:leitor"


# ═══════════════════════════════════════════════════════════
#  RBAC e heranca
# ═══════════════════════════════════════════════════════════

def test_a_heranca_atravessa_dois_niveis(loja):
    assert loja.pode(ANA, "pedido:ler")["permitido"] is True
    assert loja.pode(ANA, "pedido:escrever")["permitido"] is True


def test_a_heranca_nao_anda_para_tras(loja):
    """O leitor nao ganha o que o editor tem."""
    assert loja.pode(BOB, "pedido:escrever")["permitido"] is False
    assert loja.pode(BOB, "pedido:apagar")["permitido"] is False


def test_o_ciclo_de_heranca_nao_trava():
    """`a herda b herda a` e erro de configuracao; sem o corte seria
    recursao infinita na primeira decisao — em producao."""
    pol = P["motor"]("ciclo")
    pol.papel("a", ["x"], herda=["b"])
    pol.papel("b", ["y"], herda=["a"])
    assert pol.pode({"papel": "a"}, "y")["permitido"] is True
    assert pol.pode({"papel": "a"}, "z")["permitido"] is False


def test_o_curinga_precisa_ser_escrito(loja):
    """`usuario:*` cobre o que ainda nao existe — porque alguem
    escreveu o `*`. Uma permissao que crescesse sozinha e como uma
    acao nova nasce permitida."""
    assert loja.pode(ANA, "usuario:gerir")["permitido"] is True
    assert loja.pode(ANA, "usuario:qualquer:coisa")["permitido"] is True
    # 'pedido' nao tem curinga: so o que esta escrito.
    assert loja.pode(ANA, "pedido:exportar")["permitido"] is False


def test_o_grupo_traz_papeis(loja):
    loja.grupo("financeiro", papeis=["editor"], membros=["carla"])
    assert loja.pode({"id": "carla"}, "pedido:escrever")["permitido"] is True
    assert loja.pode({"id": "outro"}, "pedido:escrever")["permitido"] is False


def test_papeis_multiplos_somam(loja):
    quem = {"id": "z", "papeis": ["leitor", "editor"]}
    assert loja.pode(quem, "pedido:escrever")["permitido"] is True


# ═══════════════════════════════════════════════════════════
#  A negacao vence
# ═══════════════════════════════════════════════════════════

def test_a_negacao_explicita_vence_o_papel(loja):
    """E o que torna possivel a excecao. Sem prioridade sobre o
    permitir, ela seria apagada pelo papel e ninguem notaria."""
    assert loja.pode(ANA, "pedido:apagar")["permitido"] is True
    loja.negar(ANA, "pedido:apagar", motivo="congelado por auditoria")
    d = loja.pode(ANA, "pedido:apagar")
    assert d["permitido"] is False
    assert d["regra"] == "negacao"
    assert "auditoria" in d["motivo"]


def test_a_negacao_vence_ate_a_acl(loja):
    pedido = {"id": 7}
    loja.acl(pedido, ANA, ["pedido:apagar"])
    loja.negar(ANA, "pedido:apagar")
    assert loja.pode(ANA, "pedido:apagar", pedido)["permitido"] is False


def test_a_negacao_com_curinga_de_sujeito(loja):
    loja.negar("*", "pedido:apagar", motivo="desligado para todos")
    assert loja.pode(ANA, "pedido:apagar")["permitido"] is False


def test_a_negacao_de_um_recurso_nao_alcanca_outro(loja):
    a, b = {"id": 1}, {"id": 2}
    loja.negar(ANA, "pedido:apagar", a)
    assert loja.pode(ANA, "pedido:apagar", a)["permitido"] is False
    assert loja.pode(ANA, "pedido:apagar", b)["permitido"] is True


# ═══════════════════════════════════════════════════════════
#  ABAC
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def docs():
    pol = P["motor"]("docs")
    pol.papel("usuario", ["doc:ler"])
    pol.regra(
        "somente-dono",
        lambda s, a, r: None if r is None else r.get("dono") == s.get("id"),
        acoes=["doc:escrever"],
    )
    return pol


CARLOS = {"id": "carlos", "papel": "usuario"}


def test_a_regra_decide_pelos_valores(docs):
    assert docs.pode(CARLOS, "doc:escrever", {"id": 1, "dono": "carlos"})["permitido"]
    assert docs.pode(CARLOS, "doc:escrever", {"id": 2, "dono": "dani"})["permitido"] is False


def test_void_da_regra_e_NAO_OPINO(docs):
    """Uma regra que so soubesse dizer nao bloquearia tudo que ela nao
    entende. Aqui ela se cala, e a decisao cai no papel."""
    assert docs.pode(CARLOS, "doc:ler", {"id": 2, "dono": "dani"})["permitido"]


def test_uma_regra_que_FALHA_nega():
    """Tratar a excecao como "nao opino" faria um bug virar
    autorizacao — o pior defeito possivel num motor de politica."""
    pol = P["motor"]("x")
    pol.papel("todos", ["a:b"])

    def quebrada(s, a, r):
        raise ValueError("bug meu")

    pol.regra("quebrada", quebrada, acoes=["a:b"])
    d = pol.pode({"papel": "todos"}, "a:b")
    assert d["permitido"] is False
    assert "falhou" in d["motivo"]


def test_a_regra_recebe_a_aridade_que_declara():
    """A primeira versao chamava com quatro e recuava no `TypeError`.
    Uma `DFAction` levanta `TypeError_` da LINGUAGEM, que nao e o do
    Python: o erro virava "a regra falhou" e, com ele, uma negacao —
    uma regra correta recusada porque o motor errou a chamada."""
    pol = P["motor"]("aridade")
    pol.papel("p", [])
    vistos = []

    pol.regra("um", lambda s: (vistos.append(1), True)[1], acoes=["so-sujeito"])
    assert pol.pode({"papel": "p", "id": "i"}, "so-sujeito")["permitido"]
    assert vistos == [1]

    pol2 = P["motor"]("aridade4")
    pol2.papel("p", [])
    pol2.regra("quatro", lambda s, a, r, c: c is not None, acoes=["com-contexto"])
    assert pol2.pode({"papel": "p"}, "com-contexto",
                     contexto={"ip": "1.2.3.4"})["permitido"]


def test_a_regra_so_vale_para_as_acoes_declaradas(docs):
    """`acoes` e o recorte: sem ele toda regra opinaria sobre tudo."""
    d = docs.pode(CARLOS, "doc:ler", {"id": 9, "dono": "outro"})
    assert d["regra"].startswith("papel:")


# ═══════════════════════════════════════════════════════════
#  ACL
# ═══════════════════════════════════════════════════════════

def test_a_acl_do_objeto_vence_o_papel(loja):
    """Ela existe para decidir NAQUELE item; se o papel viesse antes,
    ela nunca seria alcancada."""
    pedido = {"id": 42}
    loja.acl(pedido, BOB, ["pedido:escrever"])
    assert loja.pode(BOB, "pedido:escrever", pedido)["permitido"] is True
    # E em outro objeto o papel volta a mandar.
    assert loja.pode(BOB, "pedido:escrever", {"id": 43})["permitido"] is False


def test_a_acl_tambem_RECUSA(loja):
    """Estar na lista e nao ter a acao e um nao — e nao um 'siga para
    o papel'. Senao a lista so poderia dar permissao, nunca limitar."""
    pedido = {"id": 50}
    loja.acl(pedido, ANA, ["pedido:ler"])
    d = loja.pode(ANA, "pedido:apagar", pedido)
    assert d["permitido"] is False
    assert d["regra"] == "acl"


# ═══════════════════════════════════════════════════════════
#  Delegacao
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def fin():
    pol = P["motor"]("fin")
    pol.papel("gerente", ["pagamento:aprovar"])
    pol.papel("analista", ["pagamento:ler"])
    return pol


CHEFE = {"id": "chefe", "papel": "gerente"}
SUB = {"id": "sub", "papel": "analista"}


def test_a_delegacao_empresta_e_vence(fin):
    assert fin.pode(SUB, "pagamento:aprovar")["permitido"] is False
    fin.delegar(CHEFE, SUB, ["pagamento:aprovar"], prazo=3600)
    assert fin.pode(SUB, "pagamento:aprovar")["permitido"] is True

    # Duas horas depois: a delegacao caducou.
    daqui_a_2h = time.time() + 7200
    assert fin.pode(SUB, "pagamento:aprovar",
                    quando=daqui_a_2h)["permitido"] is False


def test_ninguem_delega_o_que_nao_tem(fin):
    """Sem isto, A delega a B algo que A nao pode, B delega a C, e C
    passa a poder — autoridade criada do nada."""
    with pytest.raises(erro_de("DelegationError")) as e:
        fin.delegar(SUB, CHEFE, ["pagamento:apagar"])
    assert "pagamento:apagar" in e.value.nota


def test_a_delegacao_e_revogavel(fin):
    fin.delegar(CHEFE, SUB, ["pagamento:aprovar"], prazo=3600)
    assert fin.revogar(SUB) == 1
    assert fin.pode(SUB, "pagamento:aprovar")["permitido"] is False


def test_a_delegacao_nao_vence_uma_negacao(fin):
    fin.delegar(CHEFE, SUB, ["pagamento:aprovar"], prazo=3600)
    fin.negar(SUB, "pagamento:aprovar")
    assert fin.pode(SUB, "pagamento:aprovar")["permitido"] is False


# ═══════════════════════════════════════════════════════════
#  Inquilino
# ═══════════════════════════════════════════════════════════

def test_o_inquilino_e_conferido_ANTES_das_permissoes():
    """Conferir depois faria um papel 'admin' atravessar a fronteira
    entre clientes — o vazamento mais caro de um SaaS."""
    pol = P["motor"]("saas", "acme")
    pol.papel("admin", ["*"])
    assert pol.pode({"id": "y", "papel": "admin", "tenant": "acme"},
                    "qualquer")["permitido"] is True
    d = pol.pode({"id": "x", "papel": "admin", "tenant": "outra"}, "qualquer")
    assert d["permitido"] is False
    assert d["regra"] == "tenant"


def test_sem_inquilino_declarado_a_politica_nao_filtra():
    pol = P["motor"]("aberta")
    pol.papel("admin", ["*"])
    assert pol.pode({"papel": "admin", "tenant": "x"}, "q")["permitido"] is True


# ═══════════════════════════════════════════════════════════
#  Ferramentas
# ═══════════════════════════════════════════════════════════

def test_exigir_levanta_com_o_motivo(loja):
    with pytest.raises(erro_de("AuthorizationError")) as e:
        loja.exigir(BOB, "pedido:apagar")
    assert e.value.nota
    assert loja.exigir(ANA, "pedido:apagar") is True


def test_explicar_mostra_as_outras_camadas(loja):
    """`pode()` para na primeira que decide; quando a resposta
    surpreende, o que se quer saber e o que as OUTRAS diriam."""
    loja.negar(BOB, "pedido:ler")
    e = loja.explicar(BOB, "pedido:ler")
    assert e["decisao"]["permitido"] is False
    assert "leitor" in e["papeis"]
    assert "pedido:ler" in e["permissoes"], "o papel TEM — e a negacao venceu"
    assert len(e["negacoes"]) == 1


def test_permissoes_de_soma_papel_e_delegacao(fin):
    assert P["motor"] is not None
    fin.delegar(CHEFE, SUB, ["pagamento:aprovar"], prazo=3600)
    assert set(fin.permissoes_de(SUB)) == {"pagamento:ler", "pagamento:aprovar"}


def test_separacao_de_funcoes(fin):
    """Escrita a mao em cada fluxo, ela e esquecida em um deles — e o
    um e o que vira a fraude."""
    with pytest.raises(erro_de("AuthorizationError")) as e:
        P["separacao_de_funcoes"](fin, "pagamento:aprovar", CHEFE, CHEFE)
    assert "nao aprova" in str(e.value)
    assert P["separacao_de_funcoes"](fin, "pagamento:aprovar",
                                     SUB, CHEFE) is True


def test_a_politica_sai_de_um_vault():
    """Em producao a politica e CARREGADA, nao escrita em codigo:
    mudar quem pode o que nao pode exigir deploy."""
    pol = P["de_vault"]("do-banco", {
        "papeis": {
            "leitor": {"permissoes": ["a:ler"]},
            "editor": {"permissoes": ["a:escrever"], "herda": ["leitor"]},
        },
        "negacoes": [{"sujeito": "banido", "acao": "*"}],
    })
    assert pol.pode({"papel": "editor"}, "a:ler")["permitido"] is True
    assert pol.pode({"id": "banido", "papel": "editor"},
                    "a:ler")["permitido"] is False


def test_de_vault_recusa_chave_desconhecida():
    from dataforge.stdlib.opcoes import OpcaoDesconhecida
    with pytest.raises(OpcaoDesconhecida):
        P["de_vault"]("x", {"papeeis": {}})


def test_auditar_lista_o_que_a_politica_tem(loja):
    """Uma politica que ninguem consegue LER envelhece com permissoes
    que ninguem lembra por que existem."""
    a = loja.auditar()
    assert a["politica"] == "loja"
    assert set(a["papeis"]) == {"leitor", "editor", "admin"}
    assert a["papeis"]["admin"]["herda"] == ["editor"]


def test_a_ordem_das_camadas_e_contrato():
    """Ela nao e detalhe de implementacao: a ACL existe para dizer
    "neste objeto, nao", e se o papel viesse antes ela nunca seria
    alcancada."""
    assert P["camadas"]() == ["tenant", "negacao", "acl", "regra",
                              "papel", "delegacao", "padrao"]


def test_a_identidade_sai_de_vault_record_ou_texto():
    assert P["identidade"]({"id": 7}) == "7"
    assert P["identidade"]({"email": "a@b.c"}) == "a@b.c"
    assert P["identidade"]("ana") == "ana"
    assert P["identidade"](None) == ""


def test_pode_nunca_levanta(loja):
    """Um motor que levanta obriga um `monitor` em toda decisao, e o
    `monitor` mal colocado vira um 'permitido'."""
    for entrada in (None, {}, {"papel": None}, {"papeis": []}):
        assert loja.pode(entrada, "pedido:ler")["permitido"] is False


def test_o_modulo_nao_reimplementa_o_que_seguranca_ja_faz():
    """Duas respostas para a mesma pergunta divergem."""
    seg = set(get_module("Arcane.Seguranca")) - {"__name__"}
    pol = set(P) - {"__name__"}
    assert pol & seg == set(), f"repetido: {sorted(pol & seg)}"
