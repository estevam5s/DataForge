# -*- coding: utf-8 -*-
"""Lavra — a consulta tipada.

O que estes testes cobrem, e por quê
------------------------------------
O valor de um servidor de consulta não está no caminho feliz: está no
que ele faz quando o cliente pede algo que não existe, quando um campo
falha no meio, quando uma consulta é funda demais, e quando cinquenta
itens pedem o mesmo relacionamento.

Cada um desses tem um teste aqui, e o do N+1 **conta as idas ao banco**
— porque um lote que devolve o valor certo e mesmo assim consulta vinte
vezes passaria em qualquer teste que só olhe o resultado.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib import get_module                      # noqa: E402

L = get_module("Arcane.Lavra")


# ══════════════════════════════════════════════════════════════
#  Um esquema de brinquedo, mas com as formas que importam
# ══════════════════════════════════════════════════════════════

def montar(idas=None):
    esq = L["esquema"]("loja")
    idas = idas if idas is not None else []

    clientes = {1: {"id": 1, "nome": "Ana", "email": "ana@x.co"},
                2: {"id": 2, "nome": "Bia", "email": None}}
    pedidos = [{"id": n, "numero": f"P-{n}", "total": n * 10.0,
                "cliente_id": 1 if n % 2 else 2} for n in range(1, 21)]

    L["tipo"](esq, {"id": "Integer", "nome": "String", "email": "String"},
              nome="Cliente")
    L["campo"](esq, "Cliente", "id", "Integer!")
    L["campo"](esq, "Cliente", "nome", "String!")

    L["tipo"](esq, {"id": "Integer", "numero": "String", "total": "Float"},
              nome="Pedido")
    L["campo"](esq, "Pedido", "id", "Integer!")
    L["campo"](esq, "Pedido", "total", "Float!")
    L["campo"](esq, "Pedido", "cliente", "Cliente!",
               resolve=lambda p, a, ctx: L["pedir"](ctx, "clientes",
                                                    p["cliente_id"]))

    L["busca"](esq, "cliente", "Cliente", args={"id": "Integer!"},
               resolve=lambda r, a, c: clientes.get(a["id"]))
    L["busca"](esq, "pedidos", "[Pedido!]!",
               args={"limite": {"tipo": "Integer", "padrao": 20}},
               resolve=lambda r, a, c: pedidos[:a["limite"]])
    L["busca"](esq, "quebra", "String",
               resolve=lambda r, a, c: L["erro"]("falhei de propósito"))
    L["busca"](esq, "obrigatorio", "String!", resolve=lambda r, a, c: None)
    L["conferir"](esq)

    def buscar(ids):
        idas.append(list(ids))
        return [clientes[i] for i in ids]

    return esq, buscar


def ctx_com_lote(esq, idas):
    _, buscar = montar(idas)
    ctx = L["contexto"]({})
    L["lote"](ctx, "clientes", buscar)
    return ctx


# ══════════════════════════════════════════════════════════════
#  O básico
# ══════════════════════════════════════════════════════════════

def test_a_consulta_devolve_exatamente_o_que_foi_pedido():
    """A razão de o módulo existir, num teste.

    Uma rota REST devolve o que o servidor decidiu devolver. Aqui, quem
    pediu `nome` recebe `nome` — e não `id`, nem `email`.
    """
    esq, _ = montar()
    r = L["executar"](esq, "busca:\n    cliente(id: 1):\n        nome\n")
    assert r["erros"] == []
    assert r["dados"] == {"cliente": {"nome": "Ana"}}


def test_a_ordem_da_resposta_e_a_ordem_do_pedido():
    """Não é estética: quem consome costuma exibir na ordem.

    Um vault que embaralha faz a tela mudar de consulta para consulta
    sem ninguém ter mexido nela.
    """
    esq, _ = montar()
    r = L["executar"](esq, "busca:\n    cliente(id: 1):\n        email\n        nome\n        id\n")
    assert list(r["dados"]["cliente"]) == ["email", "nome", "id"]


def test_o_campo_que_nao_existe_e_recusado_com_sugestao():
    esq, _ = montar()
    r = L["executar"](esq, "busca:\n    cliente(id: 1):\n        nomee\n")
    assert r["dados"] is None
    assert "nomee" in r["erros"][0]["mensagem"]
    assert "nome" in r["erros"][0]["extra"]["dica"]


def test_um_erro_num_campo_nao_derruba_o_resto():
    """Quem pediu dez campos e teve um problema num recebe NOVE.

    É a diferença entre uma tela com um aviso e uma tela vazia.
    """
    esq, _ = montar()
    r = L["executar"](esq, "busca:\n    cliente(id: 1):\n        nome\n    quebra\n")
    assert r["dados"]["cliente"]["nome"] == "Ana"
    assert r["dados"]["quebra"] is None
    assert len(r["erros"]) == 1
    assert r["erros"][0]["caminho"] == ["quebra"]
    assert r["erros"][0]["mensagem"] == "falhei de propósito"


def test_o_campo_obrigatorio_que_volta_void_sobe_para_o_pai():
    """É a única forma de a promessa do `!` valer alguma coisa.

    Se um `String!` pudesse ser void, o cliente teria de conferir cada
    campo mesmo assim — e aí o `!` não diria nada.
    """
    esq, _ = montar()
    r = L["executar"](esq, "busca:\n    obrigatorio\n")
    assert r["dados"] is None
    assert r["erros"][0]["codigo"] == "nulo"


def test_a_mensagem_do_resolvedor_nao_cita_o_interpretador():
    """`Lavra.erro("faltou saldo")` saía como

        RuntimeError_ [line 52, col 36]: erro: faltou saldo

    O nome de uma classe interna e uma linha de um arquivo do módulo,
    numa mensagem que vai para quem CONSULTA.
    """
    esq, _ = montar()
    r = L["executar"](esq, "busca:\n    quebra\n")
    texto = r["erros"][0]["mensagem"]
    assert "RuntimeError" not in texto and "line" not in texto
    assert texto == "falhei de propósito"


# ══════════════════════════════════════════════════════════════
#  Variáveis, apelidos, trechos, diretivas
# ══════════════════════════════════════════════════════════════

def test_variaveis_com_padrao_e_apelidos():
    esq, _ = montar()
    r = L["executar"](esq, """
busca Dois($a: Integer!, $b: Integer := 2):
    primeiro: cliente(id: $a):
        nome
    segundo: cliente(id: $b):
        nome
""", {"a": 1})
    assert r["dados"] == {"primeiro": {"nome": "Ana"},
                          "segundo": {"nome": "Bia"}}


def test_a_variavel_obrigatoria_que_nao_veio_e_recusada():
    esq, _ = montar()
    r = L["executar"](esq, "busca X($a: Integer!):\n    cliente(id: $a):\n        nome\n")
    assert r["dados"] is None
    assert "$a" in r["erros"][0]["mensagem"]


def test_trecho_e_trecho_condicional():
    esq, _ = montar()
    r = L["executar"](esq, """
trecho Basico em Cliente:
    id
    nome

busca:
    cliente(id: 1):
        ...Basico
        email
""")
    assert r["dados"]["cliente"] == {"id": 1, "nome": "Ana",
                                     "email": "ana@x.co"}


def test_o_mesmo_campo_pedido_duas_vezes_vira_um():
    """`...Basico` mais `nome` à mão pedem `nome` duas vezes.

    Sem juntar, a segunda apaga a primeira num vault — e a ORDEM da
    consulta passaria a mudar o resultado.
    """
    esq, _ = montar()
    r = L["executar"](esq, """
trecho Basico em Cliente:
    nome

busca:
    cliente(id: 1):
        ...Basico
        nome
""")
    assert r["dados"]["cliente"] == {"nome": "Ana"}


def test_o_trecho_que_usa_a_si_mesmo_e_recusado():
    esq, _ = montar()
    r = L["executar"](esq, """
trecho A em Cliente:
    nome
    ...A

busca:
    cliente(id: 1):
        ...A
""")
    assert r["dados"] is None
    assert "si mesmo" in r["erros"][0]["mensagem"]


@pytest.mark.parametrize("diretiva,valor,esperado", [
    ("@incluir(se: $v)", True, True),
    ("@incluir(se: $v)", False, False),
    ("@pular(se: $v)", True, False),
    ("@pular(se: $v)", False, True),
])
def test_incluir_e_pular(diretiva, valor, esperado):
    esq, _ = montar()
    r = L["executar"](esq, f"""
busca X($v: Boolean!):
    cliente(id: 1):
        nome
        id {diretiva}
""", {"v": valor})
    assert ("id" in r["dados"]["cliente"]) is esperado


def test_a_diretiva_que_nao_existe_e_recusada():
    esq, _ = montar()
    r = L["executar"](esq, "busca:\n    cliente(id: 1):\n        nome @inventada\n")
    assert r["dados"] is None
    assert "@inventada" in r["erros"][0]["mensagem"]


# ══════════════════════════════════════════════════════════════
#  O N+1 — medido, não prometido
# ══════════════════════════════════════════════════════════════

def test_o_lote_faz_uma_ida_ao_banco_para_vinte_pedidos():
    """O teste que separa um DataLoader de um cache com outro nome.

    Sem o lote são 21 consultas: uma para os pedidos e uma por cliente.
    Um lote que devolvesse o valor certo e mesmo assim fosse ao banco
    vinte vezes passaria em qualquer teste que só olhasse o resultado —
    por isso aqui se conta a IDA.
    """
    idas = []
    esq, buscar = montar(idas)
    ctx = L["contexto"]({})
    L["lote"](ctx, "clientes", buscar)

    r = L["executar"](esq, """
busca:
    pedidos:
        id
        cliente:
            nome
""", contexto=ctx)

    assert r["erros"] == []
    assert len(r["dados"]["pedidos"]) == 20
    assert len(idas) == 1, f"foram {len(idas)} idas ao banco, e basta uma"
    assert sorted(idas[0]) == [1, 2], "as duas chaves distintas, de uma vez"
    assert r["extensoes"]["lotes"]["clientes"]["economia"] == 19, (
        "vinte pedidos pediram o cliente, e o banco foi consultado uma vez")


def test_o_lote_recusa_uma_resposta_fora_de_ordem():
    """O bug clássico da técnica, e o mais difícil de ver.

    Uma lista com o tamanho errado é o sintoma de uma busca que
    devolveu na ordem do banco, e não na das chaves. Cada pedido
    receberia o cliente de outro — e nada falharia.
    """
    from dataforge.stdlib.lavra.lote import ErroDeLote, Registro

    r = Registro()
    r.lote("x", lambda ids: ["so um"])
    r.pedir("x", 1)
    r.pedir("x", 2)
    with pytest.raises(ErroDeLote) as erro:
        r.lotes["x"].resolver()
    assert "MESMA ORDEM" in str(erro.value)


def test_o_lote_aceita_vault_de_chave_para_valor():
    """A forma que não depende de ordem nenhuma."""
    from dataforge.stdlib.lavra.lote import Registro

    r = Registro()
    r.lote("x", lambda ids: {i: f"v{i}" for i in reversed(ids)})
    a, b = r.pedir("x", 1), r.pedir("x", 2)
    assert (a.cobrar(), b.cobrar()) == ("v1", "v2")


# ══════════════════════════════════════════════════════════════
#  Limites
# ══════════════════════════════════════════════════════════════

def test_a_consulta_funda_demais_e_recusada_antes_de_resolver():
    """Um grafo com ciclo deixa pedir `cliente.pedidos.cliente…` sem fim.

    É a forma mais barata de derrubar um servidor de consulta, e
    descobrir isso RESOLVENDO já é tarde.
    """
    esq, _ = montar()
    L["limites"](esq, profundidade=2)
    r = L["executar"](esq, """
busca:
    pedidos:
        cliente:
            nome
""")
    assert r["dados"] is None
    assert "profundidade" in r["erros"][0]["mensagem"]
    L["limites"](esq, profundidade=12)


def test_o_custo_da_consulta_tem_teto():
    esq, _ = montar()
    L["limites"](esq, complexidade=5)
    r = L["executar"](esq, "busca:\n    pedidos:\n        id\n        total\n")
    assert r["dados"] is None
    assert "custa" in r["erros"][0]["mensagem"]
    L["limites"](esq, complexidade=1000)


# ══════════════════════════════════════════════════════════════
#  Validação antes de executar
# ══════════════════════════════════════════════════════════════

def test_a_validacao_devolve_todos_os_problemas_de_uma_vez():
    """Um validador que para no primeiro erro faz corrigir uma linha
    por tentativa. Com dez numa resposta, corrigem-se as dez."""
    esq, _ = montar()
    problemas = L["validar"](esq, """
busca:
    cliente(id: 1):
        nomee
        emaill
    naoExiste
""")
    assert len(problemas) == 3
    assert all(p["linha"] for p in problemas)


def test_a_validacao_nao_chama_resolvedor_nenhum():
    """Executar e descobrir no meio que o campo não existe já custou o
    que veio antes — inclusive escritas, numa mudança."""
    chamadas = []
    esq = L["esquema"]("t")
    L["busca"](esq, "x", "String",
               resolve=lambda r, a, c: chamadas.append(1) or "x")
    L["conferir"](esq)
    L["validar"](esq, "busca:\n    x\n    naoExiste\n")
    assert chamadas == []


def test_a_variavel_declarada_e_nao_usada_e_apontada():
    esq, _ = montar()
    problemas = L["validar"](esq, """
busca X($sobrando: Integer):
    cliente(id: 1):
        nome
""")
    assert any("sobrando" in p["mensagem"] for p in problemas)


def test_pedir_um_objeto_sem_dizer_os_campos_e_recusado():
    esq, _ = montar()
    problemas = L["validar"](esq, "busca:\n    cliente(id: 1)\n")
    assert any("quais campos" in p["mensagem"] for p in problemas)


def test_pedir_campos_de_um_escalar_e_recusado():
    esq, _ = montar()
    problemas = L["validar"](esq, "busca:\n    quebra:\n        x\n")
    assert any("não tem campos dentro" in p["mensagem"] for p in problemas)


# ══════════════════════════════════════════════════════════════
#  Contratos, uniões, enums, entradas
# ══════════════════════════════════════════════════════════════

def montar_conteudo():
    esq = L["esquema"]("cms")
    L["tipo"](esq, {"id": "Integer", "titulo": "String"}, nome="Artigo",
              cumpre=["Conteudo"])
    L["tipo"](esq, {"id": "Integer", "titulo": "String", "minutos": "Integer"},
              nome="Video", cumpre=["Conteudo"])
    L["campo"](esq, "Artigo", "id", "Integer!")
    L["campo"](esq, "Artigo", "titulo", "String!")
    L["campo"](esq, "Video", "id", "Integer!")
    L["campo"](esq, "Video", "titulo", "String!")
    L["campo"](esq, "Video", "minutos", "Integer!")
    L["contrato"](esq, "Conteudo", {"id": "Integer", "titulo": "String"},
                  resolve_tipo=lambda v, c: "Video" if "minutos" in v
                  else "Artigo")
    L["busca"](esq, "conteudos", "[Conteudo!]!",
               resolve=lambda r, a, c: [
                   {"id": 1, "titulo": "Sobre a forja"},
                   {"id": 2, "titulo": "Como fundir", "minutos": 12}])
    L["conferir"](esq)
    return esq


def test_o_contrato_devolve_o_tipo_concreto():
    esq = montar_conteudo()
    r = L["executar"](esq, """
busca:
    conteudos:
        titulo
        ... em Video:
            minutos
""")
    assert r["erros"] == []
    assert r["dados"]["conteudos"] == [
        {"titulo": "Sobre a forja"},
        {"titulo": "Como fundir", "minutos": 12}]


def test_o_contrato_sem_todos_os_campos_e_recusado_na_montagem():
    """Na MONTAGEM, e não na primeira consulta que pedir aquele campo."""
    from dataforge.stdlib.lavra.esquema import ErroDeEsquema

    esq = L["esquema"]("t")
    L["contrato"](esq, "C", {"a": "String", "b": "String"})
    L["tipo"](esq, {"a": "String"}, nome="X", cumpre=["C"])
    L["busca"](esq, "x", "X", resolve=lambda r, a, c: {"a": "1"})
    with pytest.raises(ErroDeEsquema) as erro:
        L["conferir"](esq)
    assert "não tem o campo 'b'" in str(erro.value)


def test_o_enum_sai_pelo_nome_e_entra_pelo_nome():
    esq = L["esquema"]("t")
    L["enum"](esq, "Estado", {"Rascunho": "rasc", "Publicado": "pub"})
    L["busca"](esq, "estado", "Estado!", args={"qual": "Estado!"},
               resolve=lambda r, a, c: a["qual"])
    L["conferir"](esq)
    r = L["executar"](esq, "busca:\n    estado(qual: Publicado)\n")
    assert r["dados"] == {"estado": "Publicado"}


def test_a_entrada_recusa_o_campo_com_nome_quase_certo():
    """Ignorar seria pior: o dado não chegaria, e nada denunciaria."""
    esq = L["esquema"]("t")
    L["entrada"](esq, {"titulo": "String"}, nome="Novo")
    L["campo"](esq, "Novo", "titulo", "String!")
    L["busca"](esq, "eco", "String", args={"dados": "Novo!"},
               resolve=lambda r, a, c: a["dados"]["titulo"])
    L["conferir"](esq)
    r = L["executar"](esq, 'busca:\n    eco(dados: {titulo: "x", tituloo: "y"})\n')
    # 'eco' e String (admite void), entao o erro anula o CAMPO e a
    # resposta continua — que e a regra do erro parcial.
    assert r["dados"] == {"eco": None}
    assert "tituloo" in r["erros"][0]["mensagem"]


# ══════════════════════════════════════════════════════════════
#  Paginação
# ══════════════════════════════════════════════════════════════

def test_a_pagina_por_cursor_nao_pula_item():
    """Paginar por offset quebra do jeito mais difícil de ver.

    Se alguém insere uma linha entre a página 1 e a 2, um item
    DESAPARECE da listagem — ele desceu para a posição já lida.
    """
    itens = [{"id": i, "nome": f"n{i}"} for i in range(1, 8)]
    p1 = L["pagina"](itens, primeiros=3)
    assert [i["id"] for i in p1["itens"]] == [1, 2, 3]
    assert p1["info"]["tem_proxima"] is True

    # alguem insere no comeco entre uma pagina e outra
    itens.insert(0, {"id": 99, "nome": "novo"})

    p2 = L["pagina"](itens, primeiros=3, depois=p1["info"]["cursor_fim"])
    assert [i["id"] for i in p2["itens"]] == [4, 5, 6], \
        "com cursor, a pagina 2 continua de onde a 1 parou"


def test_o_cursor_de_outra_listagem_e_recusado():
    itens = [{"id": i} for i in range(1, 4)]
    from dataforge.stdlib.lavra.execucao import ErroDeExecucao
    with pytest.raises(ErroDeExecucao):
        L["pagina"](itens, primeiros=2, depois="nao-existe")


# ══════════════════════════════════════════════════════════════
#  Introspecção
# ══════════════════════════════════════════════════════════════

def test_o_esquema_se_descreve():
    esq, _ = montar()
    L["introspeccao"](esq)
    r = L["executar"](esq, 'busca:\n    __tipo(nome: "Pedido")\n')
    descricao = r["dados"]["__tipo"]
    assert descricao["nome"] == "Pedido"
    assert {c["nome"] for c in descricao["campos"]} >= {"id", "total", "cliente"}


def test_a_introspeccao_pode_ser_desligada():
    """Em produção, um esquema exposto é um mapa para quem for procurar."""
    esq, _ = montar()
    L["introspeccao"](esq)
    L["introspeccao"](esq, False)
    r = L["executar"](esq, "busca:\n    __esquema\n")
    assert r["dados"] is None


def test_o_esquema_em_texto_versiona():
    esq, _ = montar()
    texto = L["texto_do_esquema"](esq)
    assert "tipo Pedido:" in texto
    assert "cliente: Cliente!" in texto
    assert "busca:" in texto


# ══════════════════════════════════════════════════════════════
#  Erros de sintaxe da consulta
# ══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("texto,pedaco", [
    ("cliente:\n    nome\n", "busca"),
    ("busca:\n", "não pede nada"),
    ("busca:\n    cliente(id: 1:\n        nome\n", "fechar"),
    ("busca:\n    cliente(id: 1):\n", "nada dentro"),
    ("busca:\n\tcliente\n", "tab"),
])
def test_a_sintaxe_errada_diz_o_que_fazer(texto, pedaco):
    esq, _ = montar()
    r = L["executar"](esq, texto)
    assert r["dados"] is None
    tudo = json.dumps(r["erros"], ensure_ascii=False)
    assert pedaco in tudo, tudo


def test_o_erro_de_sintaxe_traz_a_linha():
    esq, _ = montar()
    r = L["executar"](esq, "busca:\n    cliente(id: 1):\n        nome\n    ???\n")
    assert r["erros"][0]["extra"]["linha"] == 4


# ══════════════════════════════════════════════════════════════
#  Federação
# ══════════════════════════════════════════════════════════════

def test_o_portao_junta_dois_servicos():
    contas = L["esquema"]("contas")
    L["tipo"](contas, {"id": "Integer", "nome": "String"}, nome="Usuario")
    L["campo"](contas, "Usuario", "id", "Integer!")
    L["busca"](contas, "usuario", "Usuario", args={"id": "Integer!"},
               resolve=lambda r, a, c: {"id": a["id"], "nome": "Ana"})

    vendas = L["esquema"]("vendas")
    L["tipo"](vendas, {"id": "Integer", "total": "Float"}, nome="Pedido")
    L["campo"](vendas, "Pedido", "id", "Integer!")
    L["busca"](vendas, "pedido", "Pedido", args={"id": "Integer!"},
               resolve=lambda r, a, c: {"id": a["id"], "total": 9.9})

    p = L["portao"]()
    L["juntar"](p, "contas", contas)
    L["juntar"](p, "vendas", vendas)
    L["estender"](p, "Usuario", "pedidos", "[Pedido!]!",
                  resolve=lambda u, a, c: [{"id": 1, "total": 9.9}])
    p.conferir()

    r = L["executar"](p.esquema, """
busca:
    usuario(id: 1):
        nome
        pedidos:
            total
""")
    assert r["erros"] == []
    assert r["dados"]["usuario"]["pedidos"] == [{"total": 9.9}]
    assert L["mapa"](p)["tipos"]["Usuario"] == "contas"


def test_dois_servicos_com_o_mesmo_tipo_param_a_composicao():
    """Fundir em silêncio faria a consulta devolver campos de um ou de
    outro conforme a ORDEM do juntar — o pior jeito de falhar."""
    from dataforge.stdlib.lavra.esquema import ErroDeEsquema

    a = L["esquema"]("a")
    L["tipo"](a, {"id": "Integer"}, nome="Usuario")
    b = L["esquema"]("b")
    L["tipo"](b, {"id": "Integer", "outro": "String"}, nome="Usuario")

    p = L["portao"]()
    L["juntar"](p, "a", a)
    with pytest.raises(ErroDeEsquema) as erro:
        L["juntar"](p, "b", b)
    assert "declarado por 'a' e por 'b'" in str(erro.value)


# ══════════════════════════════════════════════════════════════
#  O servidor, por socket de verdade
# ══════════════════════════════════════════════════════════════

def test_o_ciclo_completo_por_http():
    """`Kiln.test` não abre socket, e o que quebra na prática é o
    caminho que passa por ele: corpo, cabeçalho, status."""
    import urllib.error
    import urllib.request

    from dataforge.stdlib.lavra import servidor

    esq, _ = montar()
    app, porta = servidor.em_segundo_plano(
        esq, contexto_de=lambda req: {"quem": req["headers"].get("x-quem")})
    try:
        base = f"http://127.0.0.1:{porta}/lavra"

        corpo = json.dumps({"consulta": "busca:\n    cliente(id: 1):\n        nome"})
        pedido = urllib.request.Request(
            base, data=corpo.encode(), method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(pedido, timeout=10) as resposta:
            assert resposta.status == 200
            dados = json.loads(resposta.read())
        assert dados["dados"] == {"cliente": {"nome": "Ana"}}

        # O GET devolve o esquema em texto.
        with urllib.request.urlopen(base, timeout=10) as resposta:
            texto = resposta.read().decode()
        assert "tipo Pedido:" in texto

        # Corpo sem 'consulta' e 400 — nao e consulta nenhuma.
        vazio = urllib.request.Request(
            base, data=b'{"x":1}', method="POST",
            headers={"Content-Type": "application/json"})
        with pytest.raises(urllib.error.HTTPError) as erro:
            urllib.request.urlopen(vazio, timeout=10)
        assert erro.value.code == 400
    finally:
        servidor.parar(app)


def test_a_consulta_com_erro_responde_200():
    """Parece errado e não é: o HTTP falou, e a resposta tem `dados` e
    `erros`. Um 400 obrigaria o cliente a ter dois caminhos de leitura
    para o mesmo corpo, e esconderia o caso normal — dados parciais."""
    import urllib.request

    from dataforge.stdlib.lavra import servidor

    esq, _ = montar()
    app, porta = servidor.em_segundo_plano(esq)
    try:
        corpo = json.dumps({"consulta": "busca:\n    naoExiste"})
        pedido = urllib.request.Request(
            f"http://127.0.0.1:{porta}/lavra", data=corpo.encode(),
            method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(pedido, timeout=10) as resposta:
            assert resposta.status == 200
            dados = json.loads(resposta.read())
        assert dados["dados"] is None
        assert dados["erros"]
    finally:
        servidor.parar(app)


def test_o_cliente_local_tem_o_mesmo_contrato_do_remoto():
    """É o que torna teste de quem CONSOME barato: a mesma chamada,
    sem socket."""
    esq, _ = montar()
    c = L["local"](esq)
    assert c.dados("busca:\n    cliente(id: 1):\n        nome") == \
        {"cliente": {"nome": "Ana"}}



# ═══════════════════════════════════════════════════════════
#  Obsoleto é AVISO, e não recusa
# ═══════════════════════════════════════════════════════════

def _esquema_com_obsoleto():
    esq = L["esquema"]("loja")
    L["escalar"](esq, "Texto", lambda v: str(v), lambda t: t)
    L["busca"](esq, "produto", "Texto",
               resolve=lambda r, a, c: "café")
    L["campo"](esq, "Busca", "antigo", "Texto",
               resolve=lambda r, a, c: "café",
               obsoleto="use 'produto'; 'antigo' sai na 3.0")
    L["conferir"](esq)
    return esq


def test_o_campo_obsoleto_continua_respondendo():
    """Ele era **recusado**, e isso tornava `obsoleto` inútil.

    Uma depreciação que quebra no dia do aviso é uma quebra com aviso
    prévio de zero — e o efeito prático era ninguém marcar campo
    nenhum, porque marcar derrubava o cliente. Aí o campo some um dia
    sem que ninguém tenha sido avisado, que é exatamente o que a marca
    existe para evitar.
    """
    r = L["executar"](_esquema_com_obsoleto(), "busca:\n    antigo")

    # responde…
    assert r["dados"]["antigo"] == "café"
    assert r["erros"] == []

    # …e avisa, em 'extensoes.avisos', que é onde o cliente procura o
    # que vai quebrar depois.
    avisos = r["extensoes"]["avisos"]
    assert len(avisos) == 1
    assert "obsoleto" in avisos[0]["mensagem"]
    assert avisos[0]["aviso"] is True


def test_o_aviso_nao_esconde_um_erro_de_verdade():
    """Um campo que **não existe** continua sendo recusado — e o aviso
    do obsoleto viaja junto, para não sumir com a resposta."""
    r = L["executar"](_esquema_com_obsoleto(), "busca:\n    antigo\n    naoExiste")

    assert r["dados"] is None
    assert len(r["erros"]) == 1
    assert "naoExiste" in r["erros"][0]["mensagem"]
    assert len(r["extensoes"]["avisos"]) == 1


def test_validar_relata_o_obsoleto_sem_reprovar():
    """`validar` continua listando o aviso — é o que permite a um teste
    do cliente saber o que vai sair, sem que a consulta falhe hoje."""
    problemas = L["validar"](_esquema_com_obsoleto(), "busca:\n    antigo")
    assert len(problemas) == 1
    assert problemas[0]["aviso"] is True
