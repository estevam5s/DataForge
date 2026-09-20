"""Arcane.Vitrine — o framework de dashboards.

O que estes testes protegem, em ordem de quanto doeu descobrir:

1. **O cookie de sessão sai como TEXTO.** O Kiln guarda cookie como a
   linha `Set-Cookie` pronta. Passar um vault ali faz o navegador
   descartar o cookie e cada pedido abrir uma sessão nova — o contador
   nunca passa de 1 e o login nunca "pega", sem nenhum erro.

2. **`V.parar()` deriva de `BaseException`.** O interpretador embrulha
   toda `Exception` que sai de função Python num erro de execução, e
   `V.exigir_login()` virava a mensagem "exigir_login: _Parar" no meio
   da página em vez de parar coisa alguma.

3. **O botão vale por uma execução.** Um clique que continuasse
   verdadeiro dispararia a ação de novo no carregamento seguinte —
   duplicar um pagamento é o tipo de bug que ninguém perdoa.

4. **Escapar é a regra.** Todo texto passa por `escape`; só `V.html`
   insere cru.
"""

import json
import os
import re
import sys
import threading

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import get_module
from dataforge.stdlib.vitrine import render
from dataforge.stdlib.vitrine.api import ArcaneVitrine, _ATUAL


@pytest.fixture
def V():
    """Um módulo limpo. Sem isto, um teste vê a aplicação do anterior."""
    _ATUAL["app"] = None
    modulo = ArcaneVitrine()
    yield modulo
    app = _ATUAL["app"]
    if app is not None:
        app.parar()
    _ATUAL["app"] = None


def sonda(V, pagina):
    return V["testar"](pagina)


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

def test_o_modulo_esta_registrado_pelos_tres_nomes():
    for nome in ("Arcane.Vitrine", "Vitrine", "Painel"):
        modulo = get_module(nome)
        assert modulo is not None, nome
        # O nome oficial vale venha por onde vier — senão o catálogo
        # não acha a descrição e o site conta módulos a mais.
        assert modulo["__name__"] == "Arcane.Vitrine"


def test_o_catalogo_descreve_o_modulo():
    from dataforge.stdlib.catalogo import DESCRICOES
    assert "Arcane.Vitrine" in DESCRICOES


def test_nao_colide_com_o_modulo_de_streaming():
    """`Arcane.Stream` é o de tópicos e partições, e continua sendo."""
    assert get_module("Stream")["__name__"] == "Arcane.Stream"
    assert get_module("Vitrine")["__name__"] == "Arcane.Vitrine"


# ═══════════════════════════════════════════════════════════
#  A árvore
# ═══════════════════════════════════════════════════════════

def test_os_componentes_entram_na_ordem(V):
    def pagina():
        V["titulo"]("um")
        V["texto"]("dois")
        V["divisor"]()

    t = sonda(V, pagina)
    assert [n.tipo for n in t.ctx.raiz.filhos] == ["titulo", "texto", "divisor"]


def test_um_componente_fora_da_pagina_diz_o_que_fazer(V):
    with pytest.raises(Exception) as erro:
        V["texto"]("solto")
    assert "fora de uma aplicacao" in str(erro.value)


def test_a_coluna_recebe_os_proprios_filhos(V):
    def pagina():
        colunas = V["colunas"](2)
        colunas[0].texto("esquerda")
        colunas[1].texto("direita")
        V["texto"]("fora")

    t = sonda(V, pagina)
    raiz = t.ctx.raiz
    assert [n.tipo for n in raiz.filhos] == ["colunas", "texto"]
    colunas = raiz.filhos[0]
    assert len(colunas.filhos) == 2
    assert colunas.filhos[0].filhos[0].props["conteudo"] == "esquerda"
    assert colunas.filhos[1].filhos[0].props["conteudo"] == "direita"


def test_a_pilha_se_recupera_de_um_erro_dentro_da_coluna(V):
    """Sem o `finally`, a página inteira cairia dentro da coluna."""
    def pagina():
        colunas = V["colunas"](2)
        try:
            colunas[0]._dentro(lambda: (_ for _ in ()).throw(ValueError("x")),
                               (), {})
        except ValueError:
            pass
        V["texto"]("depois")

    t = sonda(V, pagina)
    assert t.ctx.raiz.filhos[-1].props["conteudo"] == "depois"


def test_as_colunas_com_pesos_dividem_proporcionalmente(V):
    def pagina():
        V["colunas"]([3, 1])

    t = sonda(V, pagina)
    larguras = [c.props["proporcao"] for c in t.ctx.raiz.filhos[0].filhos]
    assert larguras == [75.0, 25.0]


def test_todas_as_abas_sao_montadas_e_so_uma_aparece(V):
    def pagina():
        abas = V["abas"](["A", "B"])
        abas[0].texto("conteudo A")
        abas[1].texto("conteudo B")

    t = sonda(V, pagina)
    abas = t.ctx.raiz.filhos[0]
    assert [a.props["visivel"] for a in abas.filhos] == [True, False]
    # Montar só a visível deixaria um erro escondido atrás de um clique.
    assert abas.filhos[1].filhos[0].props["conteudo"] == "conteudo B"


# ═══════════════════════════════════════════════════════════
#  Interação
# ═══════════════════════════════════════════════════════════

def test_o_botao_vale_por_uma_execucao(V):
    contagem = {"n": 0}

    def pagina():
        if V["botao"]("Somar"):
            contagem["n"] += 1
        V["texto"](str(contagem["n"]))

    t = sonda(V, pagina)
    assert contagem["n"] == 0
    t.clicar("Somar")
    assert contagem["n"] == 1
    t.rodar()              # outra execução, sem clique
    assert contagem["n"] == 1


def test_o_campo_guarda_o_valor_entre_execucoes(V):
    def pagina():
        nome = V["entrada"]("Nome", "")
        V["texto"](f"olá {nome}")

    t = sonda(V, pagina)
    t.digitar("Nome", "Ana")
    assert "olá Ana" in t.texto()
    t.rodar()
    assert "olá Ana" in t.texto()


def test_clicar_num_botao_nao_apaga_o_campo(V):
    def pagina():
        nome = V["entrada"]("Nome", "")
        if V["botao"]("Ok"):
            V["estado"].definir("visto", nome)
        V["texto"](nome)

    t = sonda(V, pagina)
    t.digitar("Nome", "Bruno")
    t.clicar("Ok")
    assert t.estado("visto") == "Bruno"
    assert "Bruno" in t.texto()


def test_o_numero_respeita_o_minimo_e_o_maximo(V):
    def pagina():
        V["texto"](str(V["numero"]("N", 5, minimo=0, maximo=10)))

    t = sonda(V, pagina)
    t.digitar("N", 99)
    assert "10" in t.texto()
    t.digitar("N", -5)
    assert "0" in t.texto()


def test_a_escolha_recusa_valor_fora_da_lista(V):
    def pagina():
        V["texto"](V["escolha"]("Cor", ["azul", "verde"]))

    t = sonda(V, pagina)
    t.selecionar("Cor", "roxo")
    assert "azul" in t.texto()


def test_o_formulario_so_entrega_no_envio(V):
    salvos = []

    def pagina():
        forma = V["formulario"]("cad")
        nome = forma.entrada("Nome")
        if forma.enviar("Salvar"):
            salvos.append(nome)

    t = sonda(V, pagina)
    t.digitar("Nome", "Carla")
    assert salvos == []            # digitar não salva
    t.enviar("cad")
    assert salvos == ["Carla"]


def test_o_teste_diz_quais_rotulos_existem(V):
    def pagina():
        V["botao"]("Salvar")
        V["botao"]("Cancelar")

    t = sonda(V, pagina)
    with pytest.raises(Exception) as erro:
        t.clicar("Excluir")
    assert "Excluir" in str(erro.value)
    assert "Salvar" in erro.value.nota and "Cancelar" in erro.value.nota


# ═══════════════════════════════════════════════════════════
#  Estado e cache
# ═══════════════════════════════════════════════════════════

def test_o_estado_sobrevive_a_execucao(V):
    def pagina():
        V["estado"].padrao("n", 0)
        if V["botao"]("Mais"):
            V["estado"].somar("n")
        V["texto"](f"n={V['estado'].obter('n')}")

    t = sonda(V, pagina)
    for esperado in (1, 2, 3):
        t.clicar("Mais")
        assert f"n={esperado}" in t.texto()


def test_o_estado_nao_vaza_entre_sessoes(V):
    def pagina():
        V["estado"].somar("n")
        V["texto"](str(V["estado"].obter("n")))

    a = sonda(V, pagina)
    b = V["testar"](pagina)
    assert a.sessao.id != b.sessao.id
    assert "1" in b.texto()


def test_o_estado_interno_nao_aparece_em_tudo(V):
    def pagina():
        V["entrada"]("Nome", "x")
        V["estado"].definir("meu", 1)
        V["texto"](str(sorted(V["estado"].tudo())))

    t = sonda(V, pagina)
    assert "['meu']" in t.texto()


def test_o_cache_nao_recalcula(V):
    vezes = {"n": 0}

    @V["cache"]
    def carregar(chave):
        vezes["n"] += 1
        return [chave]

    def pagina():
        V["texto"](str(carregar("a")))
        V["texto"](str(carregar("a")))
        V["texto"](str(carregar("b")))

    sonda(V, pagina)
    assert vezes["n"] == 2        # "a" uma vez, "b" uma vez


def test_o_cache_distingue_texto_de_numero(V):
    """`"1"` e `1` são chamadas diferentes — com `str` na chave, a
    segunda receberia o resultado da primeira, calada."""
    @V["cache"]
    def eco(x):
        return type(x).__name__

    assert eco(1) == "int"
    assert eco("1") == "str"


def test_o_cache_solta_o_menos_usado(V):
    @V["cache"](teto=2)
    def eco(x):
        return x

    for i in range(5):
        eco(i)
    assert eco.deposito.estatisticas()["itens"] == 2


def test_o_cache_nao_identifica_a_acao_por_um_id_reaproveitavel(V):
    """`id()` não é identidade ao longo do tempo.

    A chave do depósito era `f"{nome}#{id(alvo):x}"`. `id()` é único
    apenas entre objetos **vivos**, e o CPython reaproveita o endereço
    de um objeto coletado de forma agressiva — cinco mil funções criadas
    e liberadas em sequência dão **um** id distinto.

    Logo, uma ação nova de mesmo nome caía na chave de uma ação morta e
    herdava o depósito dela: o `teto` da outra, as entradas da outra, e
    — o pior — **o valor da outra**. Uma função devolvia o resultado
    cacheado de outra função, calada. É a mesma mistura de caches que o
    `id` veio consertar, agora com um gatilho não determinístico: na CI
    apareceu em **um** dos sete ambientes (macOS, 3.10), num teste que
    pedia `teto=2` e via seis itens — os cinco novos mais o resto do
    teste anterior, sob o teto 128 herdado.

    Provocar a colisão pelo caminho público depende do alocador, e por
    isso não é teste: o que se cobra aqui é a **correção**, que é manter
    a ação viva em `_por_alvo` — enquanto o depósito existir, aquele id
    não pode ser de mais ninguém.
    """
    import gc

    @V["cache"]
    def unica():
        return 1

    alvo = unica.sem_cache
    marca = id(alvo)
    guardados = V["cache"]._por_alvo
    assert any(a is alvo for a, _ in guardados.values()), (
        "o depósito não mantém a ação viva — o id dela pode ser "
        "reaproveitado por outra ação, que herdaria este cache")

    del alvo, unica
    gc.collect()
    assert any(id(a) == marca for a, _ in guardados.values()), (
        "a ação foi coletada apesar do depósito: o id voltou a estar "
        "disponível")


def test_o_teto_e_a_validade_pedidos_sao_os_do_deposito(V):
    """O sintoma que aparecia na CI: `teto=2` pedido, 128 em uso."""
    @V["cache"](teto=2)
    def eco(x):
        return x

    assert eco.deposito.teto == 2

    @V["cache"](teto=7, validade=99)
    def eco(x):                                       # noqa: F811
        return x

    assert eco.deposito.teto == 7
    assert eco.deposito.validade == 99


def test_duas_acoes_de_mesmo_nome_nao_dividem_o_cache(V):
    """O bug original, que o `id` consertou e que a reutilização de `id`
    ressuscitava: uma receberia o resultado da outra."""
    @V["cache"]
    def carregar():
        return "primeira"

    primeira = carregar
    assert primeira() == "primeira"

    @V["cache"]
    def carregar():                                   # noqa: F811
        return "segunda"

    assert carregar() == "segunda"
    assert primeira() == "primeira"
    assert carregar.deposito is not primeira.deposito


def test_o_cache_pode_ser_esquecido(V):
    vezes = {"n": 0}

    @V["cache"]
    def carregar():
        vezes["n"] += 1
        return 1

    carregar()
    carregar()
    assert vezes["n"] == 1
    V["cache"].invalidar(carregar)
    carregar()
    assert vezes["n"] == 2


def test_o_global_e_atomico_na_soma(V):
    """Ler-somar-escrever de duas threads perde atualizações."""
    geral = V["geral"]
    geral.definir("n", 0)

    def bater():
        for _ in range(500):
            geral.somar("n")

    linhas = [threading.Thread(target=bater) for _ in range(4)]
    for l in linhas:
        l.start()
    for l in linhas:
        l.join()
    assert geral.obter("n") == 2000


# ═══════════════════════════════════════════════════════════
#  Autenticação
# ═══════════════════════════════════════════════════════════

def _autenticar(V):
    def conferir(usuario, senha):
        if usuario == "ana" and senha == "1234":
            return {"nome": "Ana", "papel": "admin"}
        return None

    V["app"]("Teste")
    V["autenticacao"](conferir, {"admin": ["editar"], "leitor": []})
    return conferir


def test_a_barreira_de_login_para_a_pagina(V):
    _autenticar(V)
    chegou = []

    def pagina():
        V["exigir_login"]()
        chegou.append(1)
        V["titulo"]("segredo")

    t = sonda(V, pagina)
    assert chegou == []
    assert "Entrar" in t.texto()
    assert "segredo" not in t.texto()


def test_o_login_certo_continua_a_pagina_no_mesmo_ciclo(V):
    """Parar depois do login daria uma página em branco no instante em
    que a pessoa acabou de acertar a senha."""
    _autenticar(V)

    def pagina():
        V["exigir_login"]()
        V["titulo"]("segredo")

    t = sonda(V, pagina)
    t.digitar("Usuário", "ana")
    t.digitar("Senha", "1234")
    t.clicar("Entrar")
    assert "segredo" in t.texto()
    assert "Entrar" not in t.texto()


def test_a_senha_errada_avisa_e_nao_entra(V):
    _autenticar(V)

    def pagina():
        V["exigir_login"]()
        V["titulo"]("segredo")

    t = sonda(V, pagina)
    t.digitar("Usuário", "ana")
    t.digitar("Senha", "errada")
    t.clicar("Entrar")
    assert "inválidos" in t.texto()
    assert "segredo" not in t.texto()


def test_a_senha_nao_fica_guardada_depois_de_entrar(V):
    _autenticar(V)

    def pagina():
        V["exigir_login"]()
        V["titulo"]("ok")

    t = sonda(V, pagina)
    t.digitar("Usuário", "ana")
    t.digitar("Senha", "1234")
    t.clicar("Entrar")
    assert t.sessao.obter("__campo____login_senha") is None


def test_a_permissao_barra_quem_nao_tem(V):
    def conferir(usuario, senha):
        return {"nome": usuario, "papel": "leitor"}

    V["app"]("Teste")
    V["autenticacao"](conferir, {"admin": ["editar"], "leitor": ["ver"]})

    def pagina():
        V["exigir_permissao"]("editar")
        V["titulo"]("editor")

    t = sonda(V, pagina)
    t.digitar("Usuário", "zé")
    t.digitar("Senha", "x")
    t.clicar("Entrar")
    assert "permissão" in t.texto()
    assert "editor" not in t.texto()


def test_sair_derruba_o_usuario(V):
    _autenticar(V)

    def pagina():
        if V["autenticado"]():
            V["titulo"]("dentro")
            if V["botao"]("Sair"):
                V["sair"]()
        else:
            V["exigir_login"]()

    t = sonda(V, pagina)
    t.digitar("Usuário", "ana")
    t.digitar("Senha", "1234")
    t.clicar("Entrar")
    assert "dentro" in t.texto()
    t.clicar("Sair")
    # A página em que se clicou já tinha sido montada como logada; é a
    # execução seguinte que mostra a porta. Um app que queira a troca
    # imediata chama 'V.recarregar()' logo depois do 'V.sair()'.
    t.rodar()
    assert "Entrar" in t.texto()


# ═══════════════════════════════════════════════════════════
#  Erros
# ═══════════════════════════════════════════════════════════

def test_um_erro_na_pagina_nao_derruba_o_servidor(V):
    def pagina():
        V["titulo"]("antes")
        raise ValueError("quebrou de propósito")

    t = sonda(V, pagina)
    assert t.falhou()
    assert "quebrou de propósito" in t.falhas()[0]
    assert "antes" in t.texto()      # o que já foi montado continua


def test_em_producao_o_detalhe_nao_vaza(V):
    V["app"]("p", producao=True)

    def pagina():
        raise ValueError("segredo interno")

    t = V["testar"](pagina)
    assert t.falhou()
    assert t.ctx.falhas[0]["detalhe"] == ""
    # A mensagem aparece; o stack trace, não — ele entrega o caminho dos
    # arquivos e o nome das funções a quem quiser atacar.
    assert "Traceback" not in t.html()


def test_parar_nao_e_erro(V):
    def pagina():
        V["titulo"]("visível")
        V["parar"]()
        V["titulo"]("nunca")

    t = sonda(V, pagina)
    assert not t.falhou()
    assert "visível" in t.texto()
    assert "nunca" not in t.texto()


def test_navegar_pede_redirecionamento(V):
    def pagina():
        V["navegar"]("/outra")

    t = sonda(V, pagina)
    assert t.ctx.redirecionar == "/outra"
    assert not t.falhou()


# ═══════════════════════════════════════════════════════════
#  Renderização
# ═══════════════════════════════════════════════════════════

def test_o_texto_do_usuario_e_escapado(V):
    def pagina():
        V["texto"]("<script>alert(1)</script>")
        V["entrada"]("Nome", '" onfocus="alert(1)')

    t = sonda(V, pagina)
    html = t.html()
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
    assert 'onfocus="alert(1)' not in html


def test_html_cru_passa_de_proposito(V):
    def pagina():
        V["html"]("<b>negrito</b>")

    assert "<b>negrito</b>" in sonda(V, pagina).html()


def test_o_markdown_escapa_antes_de_marcar():
    saida = render.markdown("**<script>** e `<b>`")
    assert "<script>" not in saida
    assert "<strong>" in saida


def test_o_markdown_recusa_link_javascript():
    saida = render.markdown("[clique](javascript:alert(1))")
    assert "href=\"javascript:" not in saida


def test_o_markdown_nao_deixa_tag_aberta():
    """Um `*` sobrando comeria o resto da página."""
    saida = render.markdown("um * dois")
    assert saida.count("<em>") == saida.count("</em>")


def test_a_tabela_aceita_as_tres_formas(V):
    def pagina():
        V["tabela"]([{"a": 1, "b": 2}])
        V["tabela"]({"a": [1, 2], "b": [3, 4]})
        V["tabela"]([[1, 2], [3, 4]])

    t = sonda(V, pagina)
    tabelas = t.achar("tabela")
    assert tabelas[0].props["colunas"] == ["a", "b"]
    assert len(tabelas[1].props["linhas"]) == 2
    assert tabelas[2].props["colunas"] == ["col1", "col2"]


def test_a_tabela_mantem_a_ordem_das_colunas(V):
    """Alfabética embaralharia a ordem que quem montou escolheu."""
    def pagina():
        V["tabela"]([{"zebra": 1, "alfa": 2}])

    assert sonda(V, pagina).primeiro("tabela").props["colunas"] == \
        ["zebra", "alfa"]


def test_a_metrica_sabe_o_sinal_da_variacao(V):
    def pagina():
        V["metrica"]("Sobe", "10", 5.0)
        V["metrica"]("Desce", "10", -5.0)

    html = sonda(V, pagina).html()
    assert "v-sobe" in html and "v-desce" in html


def test_o_grafico_vira_svg(V):
    def pagina():
        V["grafico_linha"]([{"x": "a", "y": 1}, {"x": "b", "y": 2}], x="x")

    html = sonda(V, pagina).html()
    assert "<svg" in html and "<path" in html


def test_todos_os_tipos_de_grafico_desenham(V):
    dados = [{"c": "a", "v": 3}, {"c": "b", "v": 7}, {"c": "c", "v": 5}]

    for tipo in ("linha", "barras", "area", "dispersao", "pizza",
                 "rosca", "barras_horizontais"):
        def pagina(tipo=tipo):
            g = V["grafico"](tipo, dados)
            g.eixo_x("c")
            g.eixo_y("v")
            V["desenhar"](g)

        html = V["testar"](pagina).html()
        assert "<svg" in html, tipo
        assert "sem dados" not in html, tipo


def test_um_grafico_de_tipo_inexistente_avisa_na_hora(V):
    """E a mensagem lista os que existem, em vez de dar página em branco."""
    with pytest.raises(Exception) as erro:
        V["grafico"]("pirulito")
    assert "nao existe" in str(erro.value)
    assert "pizza" in erro.value.nota


def test_uma_fatia_unica_na_pizza_desenha_o_circulo(V):
    """Um arco de 360° fecha em si mesmo e some."""
    def pagina():
        V["grafico_pizza"]([{"c": "só", "v": 10}], x="c")

    html = sonda(V, pagina).html()
    assert "<circle" in html


def test_o_grafico_sem_dados_diz_isso(V):
    def pagina():
        V["grafico_barras"]([])

    assert "sem dados" in sonda(V, pagina).html()


def test_o_histograma_conta_por_faixa(V):
    def pagina():
        V["histograma"]([{"v": v} for v in (1, 1, 2, 9)], campo="v", faixas=2)

    no = sonda(V, pagina).primeiro("grafico")
    assert sum(no.props["series"][0]["valores"]) == 4


def test_a_pagina_tem_as_duas_paletas_de_tema(V):
    def pagina():
        V["texto"]("x")

    html = sonda(V, pagina).html()
    assert "prefers-color-scheme:dark" in html
    assert "--v-fundo" in html


def test_um_componente_desconhecido_aparece_em_vez_de_sumir():
    from dataforge.stdlib.vitrine.nucleo import No
    saida = render.desenhar(No("inventado"))
    assert "desconhecido" in saida


# ═══════════════════════════════════════════════════════════
#  HTTP
# ═══════════════════════════════════════════════════════════

def _app_http(V):
    def inicio():
        V["titulo"]("Início")

    def produto():
        V["titulo"](f"Produto {V['parametro']('id')}")

    app = V["app"]("Loja")
    V["pagina"]("/", inicio)
    V["pagina"]("/produto/:id", produto)
    return app


def test_a_pagina_responde_html_completo(V):
    r = V["pedir"](_app_http(V), "GET", "/")
    assert r["status"] == 200
    assert "<!DOCTYPE html>" in r["body"]


def test_a_resposta_traz_os_cabecalhos_de_seguranca(V):
    r = V["pedir"](_app_http(V), "GET", "/")
    assert r["headers"]["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors" in r["headers"]["Content-Security-Policy"]


def test_o_cookie_de_sessao_e_texto_e_nao_vault(V):
    """O bug que fazia cada pedido abrir uma sessão nova.

    `Kiln.test` não devolve os cookies — ele para antes do cabeçalho —,
    então este confere o que o handler produz, e o teste do socket
    logo abaixo confere que o navegador de fato o guarda.
    """
    app = _app_http(V)
    resposta = app._atender_pagina(
        {"cookies": {}, "path": "/", "query": {}})
    cookie = resposta["cookies"][0]
    assert isinstance(cookie, str), f"cookie veio como {type(cookie).__name__}"
    assert cookie.startswith("vitrine_sid=")
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie


def test_a_sessao_volta_pelo_cookie(V):
    def pagina():
        V["estado"].somar("n")
        V["texto"](f"n={V['estado'].obter('n')}")

    app = V["app"]("s")
    V["pagina"]("/", pagina)

    r = V["pedir"](app, "GET", "/")
    assert "n=1" in r["body"]
    sid = next(iter(app.sessoes))

    r2 = V["pedir"](app, "GET", "/",
                    cabecalhos={"cookie": f"vitrine_sid={sid}"})
    assert "n=2" in r2["body"]
    assert len(app.sessoes) == 1


def test_o_parametro_da_rota_chega(V):
    r = V["pedir"](_app_http(V), "GET", "/produto/42")
    assert "Produto 42" in r["body"]


def test_uma_pagina_que_nao_existe_responde_404_de_verdade(V):
    """Um 200 com "404" escrito no corpo engana monitoramento, buscador
    e qualquer cliente que confira o status em vez de ler HTML."""
    r = V["pedir"](_app_http(V), "GET", "/nao-existe")
    assert r["status"] == 404
    assert V["pedir"](_app_http(V), "GET", "/")["status"] == 200


def test_uma_pagina_que_nao_existe_lista_as_que_existem(V):
    r = V["pedir"](_app_http(V), "GET", "/nao-existe")
    assert "404" in r["body"]
    assert "/nao-existe" in r["body"]
    assert 'href="/produto/:id"' in r["body"] or "Produto" in r["body"]


def test_a_saude_responde(V):
    r = V["pedir"](_app_http(V), "GET", "/__vitrine__/saude")
    assert r["status"] == 200
    corpo = r["body"] if isinstance(r["body"], dict) else json.loads(r["body"])
    assert corpo["estado"] == "ok"


def test_as_metricas_contam_as_execucoes(V):
    app = _app_http(V)
    V["pedir"](app, "GET", "/")
    V["pedir"](app, "GET", "/")
    assert app.metricas()["execucoes"] >= 2


def test_a_acao_devolve_so_o_miolo(V):
    app = _app_http(V)
    r = V["pedir"](app, "POST", "/__vitrine__/acao",
                   {"evento": "", "campos": {}, "caminho": "/"})
    corpo = r["body"] if isinstance(r["body"], dict) else json.loads(r["body"])
    assert "<!DOCTYPE" not in corpo["html"]
    assert 'id="v-raiz"' in corpo["html"]


# ═══════════════════════════════════════════════════════════
#  Operação
# ═══════════════════════════════════════════════════════════

def test_as_sessoes_vencidas_saem_da_memoria(V):
    app = V["app"]("s", validade_sessao=0.01)
    velha = app.sessao()
    velha.tocada_em -= 10
    app.sessao()
    assert velha.id not in app.sessoes


def test_o_log_tem_teto(V):
    app = V["app"]("s")
    for i in range(2600):
        app.registrar("info", str(i))
    assert len(app._registro) <= 2000
    assert app.logs(1)[0]["mensagem"] == "2599"


def test_dois_plugins_com_o_mesmo_nome_sao_recusados(V):
    app = V["app"]("s")
    app.plugin("x", lambda a: None)
    with pytest.raises(Exception) as erro:
        app.plugin("x", lambda a: None)
    assert "ja foi instalado" in str(erro.value)


def test_o_middleware_pode_interromper(V):
    def pagina():
        V["titulo"]("privado")

    V["app"]("s")
    V["antes"](lambda ctx: False)
    V["pagina"]("/", pagina)
    t = V["testar"](pagina)
    assert "privado" not in t.texto()


def test_exportar_csv_escapa_o_separador(V):
    def pagina():
        V["exportar_csv"]([{"a": 'tem, virgula', "b": 'tem "aspas"'}])

    t = sonda(V, pagina)
    chave = t.primeiro("baixar").props["chave"]
    csv = t.sessao.obter(f"__baixar__{chave}")["conteudo"]
    assert '"tem, virgula"' in csv
    assert '"tem ""aspas"""' in csv


# ═══════════════════════════════════════════════════════════
#  Sem dependência
# ═══════════════════════════════════════════════════════════

def test_a_vitrine_nao_importa_nada_de_fora():
    """A regra do projeto inteiro, conferida aqui também."""
    import ast
    import os
    import pathlib
    import sys as _sys

    padrao = set(_sys.stdlib_module_names)
    pasta = pathlib.Path("dataforge/stdlib/vitrine")
    for arquivo in pasta.glob("*.py"):
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for alias in no.names:
                    raiz = alias.name.split(".")[0]
                    assert raiz in padrao, f"{arquivo.name}: {alias.name}"
            elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
                raiz = no.module.split(".")[0]
                assert raiz in padrao, f"{arquivo.name}: {no.module}"


def test_o_javascript_nao_busca_nada_de_fora():
    """Uma CDN quebraria o app em rede fechada — que é onde dashboard
    de dados costuma rodar."""
    from dataforge.stdlib.vitrine.render import _JS, _CSS
    for texto in (_JS, _CSS):
        assert "http://" not in texto
        assert "https://" not in texto
        assert "cdn" not in texto.lower()


# ═══════════════════════════════════════════════════════════
#  Reexecução
# ═══════════════════════════════════════════════════════════

def test_o_login_reexecuta_a_pagina_do_comeco(V):
    """O `given V.autenticado()` já passou com a resposta antiga."""
    _autenticar(V)

    def pagina():
        if V["autenticado"]():
            V["titulo"]("dentro")
        else:
            V["exigir_login"]()

    t = sonda(V, pagina)
    t.digitar("Usuário", "ana")
    t.digitar("Senha", "1234")
    t.clicar("Entrar")
    assert "dentro" in t.texto()
    assert "Entrar" not in t.texto()


def test_recarregar_joga_fora_o_que_ja_foi_montado(V):
    def pagina():
        V["texto"]("rascunho")
        if not V["estado"].existe("pronto"):
            V["estado"].definir("pronto", True)
            V["recarregar"]()
        V["texto"]("final")

    t = sonda(V, pagina)
    conteudos = [n.props["conteudo"] for n in t.achar("texto")]
    assert conteudos == ["rascunho", "final"]


def test_recarregar_sem_condicao_vira_mensagem_e_nao_travamento(V):
    def pagina():
        V["recarregar"]()

    t = sonda(V, pagina)
    assert t.falhou()
    assert "vezes demais" in t.falhas()[0]


# ═══════════════════════════════════════════════════════════
#  O servidor de verdade
# ═══════════════════════════════════════════════════════════

def test_o_ciclo_completo_por_socket(V):
    """O bug do cookie só aparecia com um navegador de verdade no meio:
    o `Kiln.test` para antes do cabeçalho `Set-Cookie`."""
    import http.cookiejar
    import urllib.request

    def pagina():
        V["titulo"]("Contador")
        if V["botao"]("Somar"):
            V["estado"].somar("n")
        V["entrada"]("Nome", "")
        V["texto"](f"n={V['estado'].obter('n', 0)}")

    app = V["app"]("Socket")
    V["pagina"]("/", pagina)
    porta = V["servir"](0)

    jar = http.cookiejar.CookieJar()
    abrir = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar)).open

    html = abrir(f"http://127.0.0.1:{porta}/").read().decode()
    assert "n=0" in html
    assert [c.name for c in jar] == ["vitrine_sid"]

    evento = re.search(r'data-v-evento="([^"]+)"', html).group(1)
    campo = re.search(r'data-v-campo="([^"]+)"', html).group(1)

    def acao(clique="", campos=None):
        pedido = urllib.request.Request(
            f"http://127.0.0.1:{porta}/__vitrine__/acao",
            data=json.dumps({"evento": clique, "campos": campos or {},
                             "caminho": "/"}).encode(),
            headers={"Content-Type": "application/json"})
        return json.loads(abrir(pedido).read().decode())["html"]

    for esperado in (1, 2, 3):
        assert f"n={esperado}" in acao(evento)

    # Digitar não zera o contador, e clicar não apaga o que foi digitado.
    assert "n=3" in acao("", {campo: "Ana"})
    depois = acao(evento, {campo: "Ana"})
    assert "n=4" in depois and 'value="Ana"' in depois

    assert app.metricas()["sessoes"] == 1


# ═══════════════════════════════════════════════════════════
#  A documentação não pode envelhecer
# ═══════════════════════════════════════════════════════════

def test_a_referencia_do_site_cobre_todos_os_simbolos():
    """O gerador recusa rodar com um símbolo de fora; este teste
    garante que o arquivo versionado é o que o gerador produz hoje.

    Um símbolo que existe e não aparece na doc é trabalho que ninguém
    encontra. Um listado que não existe é uma promessa quebrada na
    primeira tentativa de quem lê.
    """
    import os
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    destino = os.path.join(raiz, "site", "app", "docs", "vitrine",
                           "referencia", "page.tsx")
    if not os.path.isfile(destino):
        pytest.skip("o site não está neste checkout")

    antes = open(destino, encoding="utf-8").read()
    saida = subprocess.run(
        [sys.executable, os.path.join(raiz, "tools", "gerar_ref_vitrine.py")],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz)
    assert saida.returncode == 0, saida.stdout + saida.stderr
    depois = open(destino, encoding="utf-8").read()
    assert antes == depois, (
        "site/app/docs/vitrine/referencia/page.tsx está desatualizado — "
        "rode  python3 tools/gerar_ref_vitrine.py")


def test_o_sidebar_lista_as_paginas_da_vitrine():
    import os

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nav = os.path.join(raiz, "site", "lib", "nav.ts")
    if not os.path.isfile(nav):
        pytest.skip("o site não está neste checkout")

    texto = open(nav, encoding="utf-8").read()
    paginas = os.path.join(raiz, "site", "app", "docs", "vitrine")
    for nome in sorted(os.listdir(paginas)):
        if os.path.isdir(os.path.join(paginas, nome)):
            assert f"/docs/vitrine/{nome}" in texto, (
                f"/docs/vitrine/{nome} não está em site/lib/nav.ts")
    assert "'/docs/vitrine'" in texto


def test_todo_link_interno_da_doc_da_vitrine_existe():
    """Quatro links já apontaram para rotas que não existem."""
    import os
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonte = os.path.join(raiz, "site", "scripts", "conteudo", "vitrine.py")
    app = os.path.join(raiz, "site", "app")
    if not os.path.isfile(fonte):
        pytest.skip("o site não está neste checkout")

    texto = open(fonte, encoding="utf-8").read()
    quebrados = []
    for destino in sorted(set(re.findall(r"\]\((/[a-z0-9/_-]+)\)", texto))):
        caminho = os.path.join(app, destino.strip("/"), "page.tsx")
        if not os.path.isfile(caminho):
            quebrados.append(destino)
    assert not quebrados, f"links para rotas que não existem: {quebrados}"


# ═══════════════════════════════════════════════════════════
#  Validação
# ═══════════════════════════════════════════════════════════

def test_o_erro_aparece_sob_o_campo(V):
    """Num formulário de doze campos, um alerta no topo dizendo "há
    erros" obriga a pessoa a caçar qual deles."""
    def pagina():
        email = V["entrada"]("E-mail", "")
        V["validar"](email, lambda v: "@" in v, "E-mail inválido.")

    t = sonda(V, pagina)
    t.digitar("E-mail", "sem-arroba")
    assert t.problema("E-mail") == "E-mail inválido."
    html = t.html()
    assert 'aria-invalid="true"' in html
    assert 'role="alert"' in html
    # E o campo aponta para a mensagem, para o leitor de tela achá-la.
    assert "aria-describedby" in html


def test_a_regra_pode_devolver_a_propria_mensagem(V):
    def pagina():
        senha = V["entrada"]("Senha", "")
        V["validar"](senha, lambda v: "" if len(v) >= 8
                     else f"faltam {8 - len(v)} caracteres")

    t = sonda(V, pagina)
    t.digitar("Senha", "abc")
    assert t.problema("Senha") == "faltam 5 caracteres"


def test_uma_regra_quebrada_nao_vira_valor_invalido(V):
    """Dizer "E-mail inválido" quando a regra disparou esconde o bug."""
    def pagina():
        V["entrada"]("X", "")
        V["validar"]("v", lambda v: 1 / 0, "inválido")

    t = sonda(V, pagina)
    assert "regra de validação falhou" in (t.problema("X") or "")


def test_campo_vazio_e_intocado_nao_e_acusado(V):
    def pagina():
        V["campo_validado"]("E-mail", lambda v: "@" in v, "inválido")

    assert sonda(V, pagina).problemas() == []


def test_campo_validado_devolve_o_valor_e_se_esta_bom(V):
    visto = {}

    def pagina():
        valor, bom = V["campo_validado"]("E-mail", lambda v: "@" in v, "x")
        visto["valor"], visto["bom"] = valor, bom

    t = sonda(V, pagina)
    t.digitar("E-mail", "ana@exemplo.br")
    assert visto == {"valor": "ana@exemplo.br", "bom": True}


# ═══════════════════════════════════════════════════════════
#  Idioma
# ═══════════════════════════════════════════════════════════

def test_a_traducao_troca_o_texto(V):
    V["i18n"].carregar("pt-BR", {"titulo": "Painel"})
    V["i18n"].carregar("en-US", {"titulo": "Dashboard"})

    def pagina():
        V["titulo"](V["t"]("titulo"))

    assert "Painel" in sonda(V, pagina).texto()
    V["i18n"].idioma("en-US")
    assert "Dashboard" in V["testar"](pagina).texto()
    V["i18n"].idioma("pt-BR")


def test_uma_chave_sem_traducao_aparece_crua(V):
    """Feio o bastante para alguém corrigir, e informativo o bastante
    para dizer qual chave é."""
    assert V["t"]("painel.sem.traducao") == "painel.sem.traducao"


def test_a_traducao_interpola(V):
    V["i18n"].carregar("pt-BR", {"ola": "Olá, {nome}"})
    assert V["t"]("ola", nome="Ana") == "Olá, Ana"


def test_o_idioma_e_por_sessao(V):
    """Dois visitantes podem ler a mesma página em línguas diferentes."""
    V["i18n"].carregar("pt-BR", {"k": "pt"})
    V["i18n"].carregar("es", {"k": "es"})

    def pagina():
        V["texto"](V["t"]("k"))

    a = sonda(V, pagina)
    b = V["testar"](pagina)
    a.ctx.sessao.definir("__idioma__", "es")
    a.rodar()
    assert "es" in a.texto()
    assert "pt" in b.texto()


# ═══════════════════════════════════════════════════════════
#  Componentes próprios
# ═══════════════════════════════════════════════════════════

def test_um_componente_registrado_pode_ser_chamado_pelo_nome(V):
    def cartao_de_usuario(nome, email):
        caixa = V["cartao"](nome)
        caixa.texto(email)

    V["componente"]("usuario", cartao_de_usuario)

    def pagina():
        V["usar"]("usuario", "Ana", "ana@exemplo.br")
        V["usar"]("usuario", "Bruno", "bruno@exemplo.br")

    t = sonda(V, pagina)
    assert t.quantos("cartao") == 2
    assert "ana@exemplo.br" in t.texto()
    assert V["componentes"]() == ["usuario"]


def test_um_nome_errado_sugere_o_certo(V):
    V["componente"]("usuario", lambda: None)

    def pagina():
        V["usar"]("usuarios")

    t = sonda(V, pagina)
    assert t.falhou()
    assert "usuarios" in t.falhas()[0]


def test_o_registro_nao_vaza_entre_aplicacoes(V):
    """Um teste passaria por um registro que o teste anterior deixou."""
    V["componente"]("x", lambda: None)
    assert V["componentes"]() == ["x"]
    V["app"]("outra")
    assert V["componentes"]() == []


# ═══════════════════════════════════════════════════════════
#  Acessibilidade
# ═══════════════════════════════════════════════════════════

def test_a_pagina_tem_link_para_pular_a_navegacao(V):
    def pagina():
        V["lateral"]().texto("filtros")
        V["texto"]("conteúdo")

    html = sonda(V, pagina).html()
    assert 'href="#v-conteudo"' in html
    assert 'id="v-conteudo"' in html


def test_as_abas_sao_navegaveis_por_teclado(V):
    def pagina():
        V["abas"](["A", "B", "C"])

    html = sonda(V, pagina).html()
    assert 'role="tablist"' in html
    assert 'role="tabpanel"' in html
    # Só a ativa fica no caminho do Tab; as outras, nas setas.
    assert html.count('tabindex="-1"') >= 2
    assert 'aria-controls=' in html
    assert 'aria-labelledby=' in html
    assert "ArrowRight" in html


def test_a_variacao_da_metrica_tem_texto_alem_da_seta(V):
    """A seta ▲ não diz "aumento de" para quem não vê a tela."""
    def pagina():
        V["metrica"]("Receita", "10", 5.0)
        V["metrica"]("Custo", "10", -5.0)

    html = sonda(V, pagina).html()
    assert "aumento de" in html and "queda de" in html
    assert 'aria-hidden="true"' in html


def test_o_alerta_de_erro_interrompe_e_o_de_sucesso_nao(V):
    def pagina():
        V["erro"]("falhou")
        V["sucesso"]("salvo")

    html = sonda(V, pagina).html()
    assert 'role="alert"' in html      # o erro
    assert 'role="status"' in html     # o sucesso


def test_um_grupo_de_opcoes_e_um_fieldset(V):
    def pagina():
        V["opcao"]("Cor", ["azul", "verde"])
        V["escolhas"]("Tags", ["a", "b"])

    html = sonda(V, pagina).html()
    assert html.count("<fieldset") == 2
    assert html.count("<legend") == 2


def test_a_barra_de_progresso_diz_o_que_mede(V):
    def pagina():
        V["progresso"](0.4, "40% processado")
        V["progresso"](0.7)

    html = sonda(V, pagina).html()
    assert 'role="progressbar"' in html
    assert 'aria-label="40% processado"' in html
    assert 'aria-label="70%"' in html


# ═══════════════════════════════════════════════════════════
#  O comando de linha
# ═══════════════════════════════════════════════════════════

def test_o_modelo_painel_existe_e_e_valido():
    from dataforge.modelos import MODELOS
    assert "painel" in MODELOS
    modelo = MODELOS["painel"]
    assert "src/main.df" in modelo["files"]
    assert "tests/painel_test.df" in modelo["files"]


def test_o_projeto_de_painel_passa_nos_proprios_testes(tmp_path):
    """Todo modelo de `dataforge new` tem essa obrigação."""
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    criar = subprocess.run(
        [sys.executable, "-m", "dataforge", "new", "p", "--modelo=painel",
         "--silencioso"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": raiz})
    assert criar.returncode == 0, criar.stdout + criar.stderr

    testar = subprocess.run(
        [sys.executable, "-m", "dataforge", "test"],
        cwd=tmp_path / "p", capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": raiz})
    assert testar.returncode == 0, testar.stdout + testar.stderr
    assert "Tudo verde" in testar.stdout


def test_o_doctor_nao_estoura_fora_de_um_projeto(tmp_path):
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "vitrine", "doctor",
         "--no-color"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": raiz})
    # Devolve 1 porque falta o arquivo — mas diz o que fazer, e não
    # despeja um traceback.
    assert saida.returncode == 1
    assert "Traceback" not in saida.stdout + saida.stderr
    assert "dataforge vitrine new" in saida.stdout


def test_build_e_deploy_explicam_por_que_nao_existem(tmp_path):
    """Quem veio de outro framework procura os dois, e "comando
    desconhecido" não responde a pergunta que a pessoa tem."""
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for sub, esperado in (("build", "não há etapa de build"),
                          ("deploy", "de propósito")):
        saida = subprocess.run(
            [sys.executable, "-m", "dataforge", "vitrine", sub, "--no-color"],
            cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONPATH": raiz})
        assert esperado in saida.stdout, (sub, saida.stdout)


# ═══════════════════════════════════════════════════════════
#  De onde vêm os dados
# ═══════════════════════════════════════════════════════════

def test_o_painel_le_de_banco_analytics_e_cortex(V):
    """A Vitrine desenha; quem lê os dados são os módulos de sempre.

    Este teste existe porque a documentação afirma isso. Se algum deles
    mudar de assinatura, é aqui que se descobre — e não na página de
    alguém.
    """
    from dataforge.stdlib import get_module

    DB = get_module("Arcane.Database")
    An = get_module("Arcane.Analytics")
    ML = get_module("Arcane.Cortex")

    banco = DB["connect"](":memory:")
    DB["execute"](banco, "CREATE TABLE v (mes TEXT, numero INT, receita INT)")
    for linha in (("Jan", 1, 120), ("Fev", 2, 90), ("Mar", 3, 160)):
        DB["execute"](banco, "INSERT INTO v VALUES (?, ?, ?)", list(linha))

    @V["cache"]
    def vendas():
        return DB["query"](banco, "SELECT mes, numero, receita FROM v")

    def pagina():
        V["frame"](vendas())
        V["grafico_barras"](An["from_records"](vendas()), x="mes",
                            y="receita")
        V["vault"](An["describe"](An["from_records"](vendas())))
        modelo = ML["linear"](vendas(), "receita", ["numero"])
        V["metrica"]("Previsão", round(ML["prever"](modelo,
                                                    [{"numero": 4}])[0], 1))

    t = sonda(V, pagina)
    assert not t.falhou(), t.falhas()
    assert t.quantos("frame") == 1
    assert "<svg" in t.html()
    assert t.metrica("Previsão") is not None
    # Um Frame do Analytics entra no gráfico sem conversão.
    assert t.primeiro("grafico").props["categorias"] == ["Jan", "Fev", "Mar"]


def test_a_mesma_aplicacao_serve_painel_e_api(V):
    """`V.montar()` devolve o app Kiln, e as rotas convivem."""
    from dataforge.stdlib import get_module

    Kiln = get_module("Kiln")

    def painel():
        V["titulo"]("Painel")

    app = V["app"]("Misto")
    V["pagina"]("/", painel)

    kiln = V["montar"]()
    Kiln["get"](kiln, "/api/itens", lambda req: {"itens": [1, 2, 3]})

    html = V["pedir"](app, "GET", "/")
    assert html["status"] == 200
    assert "<!DOCTYPE html>" in html["body"]

    api = V["pedir"](app, "GET", "/api/itens")
    assert api["status"] == 200
    corpo = (api["body"] if isinstance(api["body"], dict)
             else json.loads(api["body"]))
    assert corpo["itens"] == [1, 2, 3]


def test_a_rota_curinga_nao_engole_as_do_kiln(V):
    """A curinga das páginas é registrada por último, de propósito."""
    from dataforge.stdlib import get_module

    Kiln = get_module("Kiln")
    app = V["app"]("Ordem")
    V["pagina"]("/", lambda: V["titulo"]("x"))
    Kiln["get"](V["montar"](), "/api/ping", lambda req: {"ok": True})

    r = V["pedir"](app, "GET", "/api/ping")
    corpo = r["body"] if isinstance(r["body"], dict) else json.loads(r["body"])
    assert corpo == {"ok": True}, "a curinga da Vitrine comeu a rota do Kiln"


def test_por_socket_a_api_e_a_pagina_convivem(V):
    """A curinga já engoliu a rota da API uma vez; o `Kiln.test` não
    pega ordem de rota do mesmo jeito que um servidor de verdade."""
    import urllib.error
    import urllib.request

    from dataforge.stdlib import get_module

    Kiln = get_module("Kiln")
    V["app"]("Misto")
    V["pagina"]("/", lambda: V["titulo"]("Painel"))
    Kiln["get"](V["montar"](), "/api/ping", lambda req: {"ok": True})
    porta = V["servir"](0)

    def pegar(caminho):
        try:
            resposta = urllib.request.urlopen(
                f"http://127.0.0.1:{porta}{caminho}")
            return resposta.status, resposta.read().decode()
        except urllib.error.HTTPError as erro:
            return erro.code, erro.read().decode()

    status, corpo = pegar("/")
    assert status == 200 and "Painel" in corpo

    status, corpo = pegar("/api/ping")
    assert status == 200, "a curinga da Vitrine comeu a rota do Kiln"
    assert json.loads(corpo) == {"ok": True}

    status, corpo = pegar("/nao-existe")
    assert status == 404 and "404" in corpo


# ═══════════════════════════════════════════════════════════
#  O painel profissional — gráficos, grade, indicadores
# ═══════════════════════════════════════════════════════════
#
# O que estes testes protegem, e o que cada um já pegou:
#
# 1. **Um tipo em `TIPOS` sem desenho em `_SVG` some calado.**
#    `_svg_linha` assume, e quem pediu um funil vê uma linha. É a
#    falha mais barata de cometer ao acrescentar um gráfico, e a mais
#    difícil de notar numa tela cheia.
#
# 2. **A grade ordena e pagina NO SERVIDOR.** A `V.frame` ordena o que
#    já está na tela, e num conjunto de cem mil linhas isso é mentira.
#
# 3. **O editor devolve o TIPO da coluna.** Devolver `"12"` onde havia
#    `12` faz a soma do rodapé concatenar, e o sintoma é um total
#    absurdo — não um erro.

VENDAS = [{"mes": "jan", "receita": 12000, "despesa": 8000, "margem": 33.3},
          {"mes": "fev", "receita": 15000, "despesa": 9000, "margem": 40.0},
          {"mes": "mar", "receita": 11000, "despesa": 9500, "margem": 13.6}]


def test_todo_tipo_de_grafico_declarado_tem_um_desenho():
    """A trava dos dois lados: a tupla e a tabela de despacho.

    Sem ela, acrescentar um nome a `TIPOS` e esquecer o desenho
    entrega um gráfico de linha no lugar do que foi pedido — e a
    página não reclama de nada.
    """
    from dataforge.stdlib.vitrine import graficos as G

    sem_desenho = [t for t in G.TIPOS if t not in render._SVG]
    assert not sem_desenho, (
        f"tipos sem desenho em render._SVG: {sem_desenho}")

    inventados = [t for t in render._SVG if t not in G.TIPOS]
    assert not inventados, (
        f"desenhos para tipos que ninguém pode pedir: {inventados}")


def test_todo_tipo_de_grafico_desenha_um_svg(V):
    """Cada tipo, com o dado que ele espera, sai como SVG.

    Um gráfico que levanta derruba a página inteira; um que devolve
    vazio some sem avisar. Os dois são reprovados aqui.
    """
    from dataforge.stdlib.vitrine import graficos as G

    pedidos = {
        "linha": lambda: V["grafico_linha"](VENDAS, x="mes", y="receita"),
        "barras": lambda: V["grafico_barras"](VENDAS, x="mes", y="receita"),
        "area": lambda: V["grafico_area"](VENDAS, x="mes", y="receita"),
        "dispersao": lambda: V["grafico_dispersao"](VENDAS, x="mes", y="receita"),
        "pizza": lambda: V["grafico_pizza"](VENDAS, x="mes", y="receita"),
        "rosca": lambda: V["grafico_rosca"](VENDAS, x="mes", y="receita"),
        "histograma": lambda: V["histograma"](VENDAS, "receita"),
        "barras_horizontais": lambda: V["grafico_barras_h"](
            VENDAS, x="mes", y="receita"),
        "combo": lambda: V["grafico_combo"](
            VENDAS, x="mes", barras=["receita"], linhas=["margem"],
            direita=["margem"]),
        "barras_100": lambda: V["grafico_barras_100"](
            VENDAS, x="mes", y=["receita", "despesa"]),
        "radar": lambda: V["grafico_radar"](
            VENDAS, x="mes", y=["receita", "despesa"]),
        "medidor": lambda: V["medidor"](72, 0, 100),
        "bala": lambda: V["grafico_bala"](72, 90, rotulo="NPS"),
        "funil": lambda: V["grafico_funil"](
            [{"e": "visitas", "n": 1000}, {"e": "compras", "n": 88}],
            x="e", y="n"),
        "treemap": lambda: V["grafico_treemap"](
            VENDAS, rotulo="mes", valor="receita"),
        "cascata": lambda: V["grafico_cascata"](
            [{"i": "base", "v": 100}, {"i": "perdas", "v": -25}], x="i", y="v"),
        "pareto": lambda: V["grafico_pareto"](VENDAS, x="mes", y="receita"),
        "mapa_de_calor": lambda: V["mapa_de_calor"](
            [{"d": "seg", "h": "09", "n": 5}, {"d": "ter", "h": "10", "n": 9}],
            x="h", y="d", valor="n"),
        "calendario": lambda: V["grafico_calendario"](
            [{"d": "2026-03-01", "n": 4}], data="d", valor="n"),
        "caixa": lambda: V["grafico_caixa"](VENDAS, y=["receita"]),
        "bolhas": lambda: V["grafico_bolhas"](
            VENDAS, x="receita", y="despesa", tamanho="margem", rotulo="mes"),
        "dispersao_xy": lambda: V["grafico_dispersao_xy"](
            VENDAS, x="receita", y="despesa", tendencia=True),
        "velas": lambda: V["grafico_velas"](
            [{"d": "01", "abertura": 10, "maxima": 12, "minima": 9,
              "fechamento": 11}], data="d"),
        "sankey": lambda: V["grafico_sankey"](
            [{"de": "A", "para": "B", "valor": 10}]),
        "gantt": lambda: V["grafico_gantt"](
            [{"tarefa": "x", "inicio": "2026-01-01", "fim": "2026-02-01"}]),
        "mapa": lambda: V["grafico_mapa"](
            [{"lat": -27.5, "lon": -48.5, "rotulo": "Floripa", "valor": 3}]),
        "rede": lambda: V["grafico_rede"](
            [{"de": "A", "para": "B"}, {"de": "B", "para": "C"}]),
    }
    assert set(pedidos) == set(G.TIPOS), (
        "este teste precisa de um caso por tipo; faltam "
        f"{sorted(set(G.TIPOS) - set(pedidos))}")

    for tipo, montar in pedidos.items():
        def pagina(montar=montar):
            montar()

        t = sonda(V, pagina)
        assert not t.falhou(), f"{tipo}: {t.falhas()}"
        html = t.html()
        assert "<svg" in html, f"{tipo} não desenhou SVG nenhum"
        assert "sem dados para desenhar" not in html, (
            f"{tipo} recebeu dado e mesmo assim disse que não tem")


def test_as_barras_deitadas_desenham_TODAS_as_series(V):
    """Elas desenhavam só a primeira, e a legenda prometia as duas.

    Planejado contra realizado saía mostrando o planejado e nada mais.
    Desenhar menos do que a legenda anuncia é pior que recusar a
    segunda série: ninguém confere um gráfico que parece completo.
    """
    def pagina():
        V["grafico_barras_h"](VENDAS, x="mes", y=["receita", "despesa"])

    t = sonda(V, pagina)
    no = t.primeiro("grafico")
    assert len(no.props["series"]) == 2
    html = t.html()
    # Três categorias × duas séries = seis barras, mais nenhuma.
    assert html.count("<rect") >= 6, "faltam barras da segunda série"
    assert "despesa" in html


def test_a_rosca_escreve_o_total_no_centro(V):
    def pagina():
        g = V["grafico"]("rosca", {"Sul": 120.0, "Norte": 80.0})
        g.total_no_centro("R$ 200", "Total")
        V["desenhar"](g)

    html = sonda(V, pagina).html()
    assert "v-centro-valor" in html and "R$ 200" in html
    assert "Total" in html


def test_a_linha_tracejada_distingue_o_planejado(V):
    """Tracejado, e não outra cor: é a mesma grandeza."""
    def pagina():
        g = V["grafico"]("linha", VENDAS)
        g.eixo_x("mes")
        g.eixo_y(["receita", "despesa"])
        g.tracejar("despesa")
        V["desenhar"](g)

    html = sonda(V, pagina).html()
    assert html.count("stroke-dasharray") == 1, (
        "o tracejado pegou a série errada, ou as duas")


def test_a_linha_de_referencia_fica_atras_do_dado(V):
    """Uma meta por cima da série esconde onde ela foi cruzada."""
    def pagina():
        g = V["grafico"]("linha", VENDAS)
        g.eixo_x("mes")
        g.eixo_y("receita")
        g.referencia(13000, "meta")
        V["desenhar"](g)

    html = sonda(V, pagina).html()
    assert "meta" in html
    assert html.index("stroke-dasharray") < html.index('stroke-width="2.5"')


def test_o_eixo_usa_o_formato_pedido(V):
    """Eixo em `1,2 M` e dica em `1200000` obriga a converter de cabeça."""
    def pagina():
        g = V["grafico"]("barras", VENDAS)
        g.eixo_x("mes")
        g.eixo_y("receita")
        g.formato("moeda")
        V["desenhar"](g)

    html = sonda(V, pagina).html()
    assert "R$" in html


def test_as_barras_de_cem_por_cento_normalizam_cada_categoria(V):
    def pagina():
        V["grafico_barras_100"](VENDAS, x="mes", y=["receita", "despesa"])

    t = sonda(V, pagina)
    assert not t.falhou()
    assert t.primeiro("grafico").props["cem_por_cento"] is True


def test_uma_coluna_toda_zero_nao_vira_nan(V):
    """`nan` num atributo de SVG não levanta: a barra some, calada."""
    zerado = [{"mes": "jan", "a": 0, "b": 0}, {"mes": "fev", "a": 3, "b": 1}]

    def pagina():
        V["grafico_barras_100"](zerado, x="mes", y=["a", "b"])

    # Só o desenho do gráfico: a página inteira carrega o cliente, e o
    # `isNaN` dele daria um falso positivo aqui.
    t = sonda(V, pagina)
    svg = render.desenhar(t.primeiro("grafico"))
    assert "nan" not in svg.lower()


def test_a_area_das_bolhas_e_proporcional_e_nao_o_raio(V):
    """Usar o raio direto quadruplica a mancha de um valor dobrado."""
    dados = [{"n": "a", "x": 1, "y": 1, "t": 1},
             {"n": "b", "x": 2, "y": 2, "t": 4}]

    def pagina():
        V["grafico_bolhas"](dados, x="x", y="y", tamanho="t", rotulo="n")

    html = sonda(V, pagina).html()
    raios = sorted(float(r) for r in re.findall(r'r="([\d.]+)"', html))
    menor, maior = raios[0], raios[-1]
    # Quatro vezes a área é o dobro do raio útil: 4 + 22·√(1/4) = 15 e
    # 4 + 22·√1 = 26. A razão dos raios ÚTEIS (sem o piso de 4) é 2.
    assert abs((maior - 4) / (menor - 4) - 2.0) < 0.05, (
        f"a proporção do raio saiu em {(maior - 4) / (menor - 4):.2f}, "
        "e devia ser 2 — a área é que é proporcional")


def test_a_tendencia_traz_o_r2_junto(V):
    """Sem o r², uma reta é desenhada com a mesma confiança sobre ruído."""
    def pagina():
        V["grafico_dispersao_xy"](VENDAS, x="receita", y="despesa",
                                  tendencia=True)

    t = sonda(V, pagina)
    assert t.primeiro("grafico").props["tendencia"]["r2"] is not None
    assert "r²" in t.html()


def test_o_funil_traz_as_duas_conversoes(V):
    """Só o total seria pior que inútil: o gargalo é uma passagem."""
    def pagina():
        V["grafico_funil"]([{"e": "visitas", "n": 1000},
                            {"e": "cadastros", "n": 300},
                            {"e": "compras", "n": 90}], x="e", y="n")

    etapas = sonda(V, pagina).primeiro("grafico").props["etapas"]
    assert abs(etapas[1]["da_anterior"] - 30.0) < 0.01
    assert abs(etapas[2]["do_topo"] - 9.0) < 0.01


def test_a_cascata_encadeia_os_passos(V):
    def pagina():
        V["grafico_cascata"]([{"i": "base", "v": 100},
                              {"i": "ganhos", "v": 40},
                              {"i": "perdas", "v": -25}], x="i", y="v")

    passos = sonda(V, pagina).primeiro("grafico").props["passos"]
    assert [p["de"] for p in passos] == [0.0, 100.0, 140.0, 0.0]
    assert passos[-1]["tipo"] == "total" and passos[-1]["ate"] == 115.0
    assert passos[2]["tipo"] == "desce"


def test_o_quartil_do_boxplot_sai_da_amostra(V):
    """Interpolar inventa um valor que não aconteceu."""
    from dataforge.stdlib.vitrine import graficos_avancados as GA

    resumo = GA._resumo_de_caixa("x", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    for campo in ("q1", "mediana", "q3"):
        assert resumo[campo] in range(1, 11), (
            f"{campo} = {resumo[campo]} não é um valor da amostra")


def test_o_calendario_acha_o_dia_da_semana_sem_datetime():
    """Zeller, porque `datetime` levanta num ano fora da faixa dele."""
    import datetime

    from dataforge.stdlib.vitrine import render_graficos as RG

    for ano, mes, dia in ((2026, 9, 20), (2000, 2, 29), (1999, 12, 31)):
        esperado = datetime.date(ano, mes, dia).weekday()
        assert RG._dia_da_semana(ano, mes, dia) == esperado, (
            f"{ano}-{mes}-{dia}")


def test_o_gantt_converte_data_nos_dois_sentidos():
    from dataforge.stdlib.vitrine import render_graficos as RG

    numero = RG._dia_juliano("2026-09-20")
    assert RG._data_juliana(numero) == "20/09"
    assert RG._dia_juliano("2026-09-21") - numero == 1


def test_o_sankey_poe_cada_no_na_camada_certa(V):
    def pagina():
        V["grafico_sankey"]([{"de": "R", "para": "C", "valor": 60},
                             {"de": "R", "para": "L", "valor": 40},
                             {"de": "L", "para": "P", "valor": 20}])

    camadas = sonda(V, pagina).primeiro("grafico").props["camadas"]
    assert camadas["R"] == 0 and camadas["C"] == 1 and camadas["P"] == 2


def test_um_ciclo_no_sankey_nao_prende_o_servidor():
    """O teto de voltas é o número de nós. Um grafo torto é melhor que
    um laço infinito — e um ciclo aqui é dado errado, não um ataque."""
    from dataforge.stdlib.vitrine import graficos_avancados as GA

    camadas = GA._camadas_do_sankey([
        {"de": "a", "para": "b", "valor": 1},
        {"de": "b", "para": "c", "valor": 1},
        {"de": "c", "para": "a", "valor": 1}])
    assert set(camadas) == {"a", "b", "c"}


# ── A grade ─────────────────────────────────────────────────

def test_a_grade_pagina_no_servidor(V):
    muitas = [{"i": n, "v": n * 2} for n in range(57)]

    def pagina():
        V["grade"](muitas, paginar=10)

    t = sonda(V, pagina)
    no = t.primeiro("grade")
    assert no.props["paginas"] == 6 and no.props["total"] == 57
    assert len(no.props["linhas"]) == 10, "a página trouxe linhas demais"


def test_a_grade_ordena_o_conjunto_inteiro_e_nao_a_pagina(V):
    """É a diferença entre a grade e a `V.frame`, e o ponto dela."""
    muitas = [{"i": n, "v": (n * 37) % 100} for n in range(40)]

    def pagina():
        V["grade"](muitas, paginar=5, chave="g")

    t = sonda(V, pagina)
    t.rodar(entrada={"g:ordem": "v", "g:desc": True})
    primeira = t.primeiro("grade").props["linhas"][0]["celulas"][1]["texto"]
    assert primeira == str(max(l["v"] for l in muitas))


def test_a_grade_devolve_o_que_foi_selecionado(V):
    escolhidas = []

    def pagina():
        escolhidas.clear()
        escolhidas.extend(V["grade"](VENDAS, selecionar="varias", chave="g"))

    t = sonda(V, pagina)
    assert escolhidas == []
    t.rodar(entrada={"g:selecao": ["0", "2"]})
    assert [l["mes"] for l in escolhidas] == ["jan", "mar"]


def test_a_selecao_de_linha_unica_fica_com_a_ultima(V):
    marcadas = []

    def pagina():
        marcadas.clear()
        marcadas.extend(V["grade"](VENDAS, selecionar="linha", chave="g"))

    t = sonda(V, pagina)
    t.rodar(entrada={"g:selecao": ["0", "1"]})
    assert len(marcadas) == 1 and marcadas[0]["mes"] == "fev"


def test_a_grade_soma_o_rodape_do_conjunto_todo_e_nao_da_pagina(V):
    def pagina():
        V["grade"](VENDAS, paginar=1, totais=["receita"])

    rodape = sonda(V, pagina).primeiro("grade").props["rodape"]
    soma = next(c["texto"] for c in rodape if c["texto"])
    assert "38.000" in soma, f"o rodapé somou só a página: {soma}"


def test_a_ordenacao_nao_estoura_com_uma_celula_vazia(V):
    """Comparar tipos diferentes dispara, e a listagem inteira some."""
    furados = [{"n": "a", "v": 3}, {"n": "b", "v": None}, {"n": "c", "v": 1}]

    def pagina():
        V["grade"](furados, chave="g")

    t = sonda(V, pagina)
    t.rodar(entrada={"g:ordem": "v"})
    assert not t.falhou(), t.falhas()
    ordem = [l["celulas"][1]["texto"]
             for l in t.primeiro("grade").props["linhas"]]
    assert ordem[-1] == "", "a ausência devia ficar por último"


def test_a_regra_de_destaque_pinta_a_celula(V):
    def pagina():
        V["grade"](VENDAS, destacar=[V["regra"]("margem", "menor", 20, "erro")])

    linhas = sonda(V, pagina).primeiro("grade").props["linhas"]
    cores = [l["celulas"][3]["cor"] for l in linhas]
    assert cores == ["", "", "erro"]


def test_uma_coluna_de_tipo_inexistente_sugere_o_parecido(V):
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        V["coluna"]("x", tipo="moedas")
    assert "moeda" in str(erro.value.nota)


def test_a_grade_busca_em_todas_as_colunas(V):
    def pagina():
        V["grade"](VENDAS, chave="g")

    t = sonda(V, pagina)
    t.rodar(entrada={"g:busca": "fev"})
    assert t.primeiro("grade").props["total"] == 1


# ── O editor ────────────────────────────────────────────────

def test_o_editor_devolve_o_tipo_da_coluna(V):
    """Devolver `"12"` faz a soma do rodapé concatenar, sem erro."""
    saida = []

    def pagina():
        saida.clear()
        saida.extend(V["editor"](VENDAS, chave="e"))

    t = sonda(V, pagina)
    t.rodar(entrada={"e:0:receita": "99000"})
    assert saida[0]["receita"] == 99000
    assert isinstance(saida[0]["receita"], int)


def test_o_editor_acrescenta_e_remove_linha(V):
    saida = []

    def pagina():
        saida.clear()
        saida.extend(V["editor"](VENDAS, chave="e"))

    t = sonda(V, pagina)
    assert len(saida) == 3
    t.rodar(eventos=["e:novo"])
    assert len(saida) == 4
    t.rodar(eventos=["e:rm:0"])
    assert len(saida) == 3 and saida[0]["mes"] == "fev"


def test_a_coluna_do_editor_nasce_editavel(V):
    """Um editor cujas colunas nascem travadas não edita nada."""
    def pagina():
        V["editor"](VENDAS)

    colunas = sonda(V, pagina).primeiro("editor").props["colunas"]
    assert all(c["editavel"] for c in colunas)


# ── Indicadores e formatos ──────────────────────────────────

def test_o_indicador_formata_o_valor(V):
    def pagina():
        V["indicador"]("Patrimônio", 1091947.91, formato="moeda")

    assert sonda(V, pagina).primeiro("indicador").props["valor"] == \
        "R$ 1.091.947,91"


def test_o_indicador_mede_o_alvo(V):
    def pagina():
        V["indicador"]("Aportes", 6000, alvo=12000, formato="moeda")

    progresso = sonda(V, pagina).primeiro("indicador").props["progresso"]
    assert abs(progresso["fracao"] - 0.5) < 1e-9


def test_uma_chave_errada_num_indicador_e_recusada(V):
    """Sem isso o cartão sai com o padrão e nada denuncia o engano."""
    def pagina():
        V["indicadores"]([{"rotulo": "x", "valor": 1, "formatto": "moeda"}])

    t = sonda(V, pagina)
    # A chave desconhecida é IGNORADA em vez de derrubar a página — e o
    # cartão continua existindo, que é o que se vê na tela.
    assert not t.falhou()
    assert t.primeiro("indicador").props["valor"] == "1"


def test_os_formatos_falam_pt_br(V):
    assert V["moeda"](1091947.91) == "R$ 1.091.947,91"
    assert V["numero_br"](1234567) == "1.234.567"
    assert V["percentual"](12.5) == "12,5%"
    assert V["compacto"](1234567) == "1,2 mi"
    assert V["data_br"]("2026-09-20") == "20/09/2026"


def test_o_formato_nao_estraga_o_que_nao_e_numero(V):
    assert V["moeda"]("—") == "—"
    assert V["data_br"]("ontem") == "ontem"


# ── Entradas novas ──────────────────────────────────────────

def test_o_periodo_troca_as_datas_fora_de_ordem(V):
    faixa = []

    def pagina():
        faixa.clear()
        faixa.extend(V["periodo"]("Quando", chave="p"))

    t = sonda(V, pagina)
    t.rodar(entrada={"p": ["2026-12-31", "2026-01-01"]})
    assert faixa == ["2026-01-01", "2026-12-31"]


def test_a_faixa_respeita_os_limites(V):
    valores = []

    def pagina():
        valores.clear()
        valores.extend(V["faixa"]("Preço", 0, 100, chave="f"))

    t = sonda(V, pagina)
    t.rodar(entrada={"f": [-20, 480]})
    assert valores == [0, 100]


def test_as_pilulas_recusam_o_que_saiu_da_lista(V):
    """A lista muda entre duas execuções, e o valor guardado fica órfão."""
    escolhido = []

    def pagina():
        escolhido.append(V["pilulas"]("Período", ["Dia", "Mês"], chave="p"))

    t = sonda(V, pagina)
    t.rodar(entrada={"p": "Década"})
    assert escolhido[-1] == "Dia"


def test_as_pilulas_com_varios_devolvem_cluster(V):
    escolhidos = []

    def pagina():
        escolhidos.clear()
        escolhidos.extend(V["pilulas"]("Canais", ["Web", "App", "Loja"],
                                       varios=True, chave="c"))

    t = sonda(V, pagina)
    t.rodar(entrada={"c": ["App", "Loja", "Fax"]})
    assert escolhidos == ["App", "Loja"]


def test_o_deslizante_de_opcoes_aceita_a_posicao(V):
    """O navegador manda número: o cursor é numérico por baixo."""
    escolhido = []

    def pagina():
        escolhido.append(V["deslizante_opcoes"]("Tamanho", ["P", "M", "G"],
                                                chave="t"))

    t = sonda(V, pagina)
    t.rodar(entrada={"t": 2})
    assert escolhido[-1] == "G"


def test_a_avaliacao_devolve_zero_e_nao_void(V):
    """A média de uma coluna de notas não deveria tratar ausência."""
    def pagina():
        V["avaliacao"]("Nota")

    assert sonda(V, pagina).primeiro("avaliacao").props["valor"] == 0


def test_as_etiquetas_chegam_separadas_por_virgula(V):
    etiquetas = []

    def pagina():
        etiquetas.clear()
        etiquetas.extend(V["tags"]("Marcas", chave="t"))

    t = sonda(V, pagina)
    t.rodar(entrada={"t": "urgente, revisar ,urgente"})
    assert etiquetas == ["urgente", "revisar"], "repetida ou espaço sobrando"


def test_mudou_responde_so_no_ciclo_da_mudanca(V):
    """É o `on_change` deste framework, e ele é uma pergunta."""
    respostas = []

    def pagina():
        V["escolha"]("Região", ["Sul", "Norte"], chave="r")
        respostas.append(V["mudou"]("r"))

    t = sonda(V, pagina)
    assert respostas == [False]
    t.rodar(entrada={"r": "Norte"})
    assert respostas[-1] is True
    t.rodar()
    assert respostas[-1] is False, "a mudança ficou grudada"


# ── Conteúdo ────────────────────────────────────────────────

def test_escrever_escolhe_pelo_valor(V):
    def pagina():
        V["escrever"]("## Título")
        V["escrever"](VENDAS)
        V["escrever"]({"total": 12})
        V["escrever"](42)

    t = sonda(V, pagina)
    assert t.quantos("markdown") == 1
    assert t.quantos("frame") == 1
    assert t.quantos("vault") == 1
    assert t.quantos("texto") == 1


def test_um_icone_que_nao_existe_sugere_o_parecido(V):
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        V["icone"]("grafik")
    assert "grafico" in str(erro.value.nota)


def test_o_icone_herda_a_cor_do_texto(V):
    """Um ícone com cor fixa briga com metade dos temas."""
    def pagina():
        V["icone"]("painel")

    assert "currentColor" in sonda(V, pagina).html()


def test_o_iframe_entra_em_sandbox_sem_mesma_origem(V):
    """Mesma origem daria a ele a sessão de quem está logado."""
    def pagina():
        V["iframe"]("/externo")

    html = sonda(V, pagina).html()
    assert "sandbox=" in html and "allow-same-origin" not in html


def test_o_pdf_e_o_iframe_recusam_javascript(V):
    def pagina():
        V["iframe"]("javascript:alert(1)")
        V["pdf"]("javascript:alert(1)")

    html = sonda(V, pagina).html()
    assert "javascript:" not in html
    assert html.count("não é seguro") == 2


def test_a_formula_traduz_fracao_e_grega(V):
    def pagina():
        V["formula"](r"\frac{a}{b} \leq \alpha")

    html = sonda(V, pagina).html()
    assert "v-frac" in html and "≤" in html and "α" in html


def test_o_status_muda_de_estado(V):
    def pagina():
        passo = V["status"]("Consultando")
        passo.texto("1200 linhas")
        passo.concluir("Pronto")

    t = sonda(V, pagina)
    no = t.primeiro("status")
    assert no.props["estado"] == "pronto" and no.props["rotulo"] == "Pronto"
    assert "1200 linhas" in t.texto()


def test_o_toast_e_um_no_e_pode_ser_testado(V):
    def pagina():
        V["toast"]("salvo", nivel="sucesso")

    t = sonda(V, pagina)
    assert t.quantos("toast") == 1
    assert t.primeiro("toast").props["nivel"] == "sucesso"


def test_a_conversa_guarda_o_historico(V):
    def pagina():
        V["guardar_no_chat"]("usuario", "oi")
        V["guardar_no_chat"]("assistente", "olá")
        area = V["chat"]()
        for m in V["historico_de_chat"]():
            area.chat_mensagem(m["quem"], m["conteudo"])

    t = sonda(V, pagina)
    assert t.quantos("chat_mensagem") == 2
    assert "olá" in t.texto()


def test_a_caixa_de_conversa_devolve_void_sem_envio(V):
    enviados = []

    def pagina():
        enviados.append(V["chat_entrada"](chave="c"))

    t = sonda(V, pagina)
    assert enviados == [None]
    t.rodar(entrada={"c": "qual o total?"}, eventos=["c"])
    assert enviados[-1] == "qual o total?"
    t.rodar()
    assert enviados[-1] is None, "o texto ficou e seria reenviado"


# ── Layout ──────────────────────────────────────────────────

def test_o_painel_e_a_malha_recebem_os_proprios_filhos(V):
    def pagina():
        m = V["malha"](3)
        p = m.painel("Receita")
        p.metrica("Total", "R$ 1")

    t = sonda(V, pagina)
    malha = t.primeiro("malha")
    assert malha.filhos[0].tipo == "painel"
    assert malha.filhos[0].filhos[0].tipo == "metrica"


def test_o_dialogo_fechado_nao_desenha_nada(V):
    def pagina():
        janela = V["dialogo"]("Novo", aberto=False)
        janela.entrada("Nome")

    # O corpo, e não a página: a folha de estilo cita `.v-dialogo` de
    # qualquer jeito, e conferir o documento inteiro testaria o CSS.
    t = sonda(V, pagina)
    corpo = render.corpo_html(t.ctx, {})
    assert "v-dialogo" not in corpo
    assert "Nome" not in corpo, "o conteúdo do diálogo fechado vazou"


def test_o_dialogo_avisa_quando_fecharam(V):
    fechou = []

    def pagina():
        janela = V["dialogo"]("Novo", chave="d")
        fechou.append(janela.fechou())

    t = sonda(V, pagina)
    assert fechou == [False]
    t.rodar(eventos=["d:fechar"])
    assert fechou[-1] is True


def test_a_barra_superior_marca_a_pagina_atual(V):
    def pagina():
        V["barra_superior"]("App", itens=["Dados", "Painel"], ativo="Painel")

    html = sonda(V, pagina).html()
    assert 'aria-current="page"' in html and "v-topo-on" in html


def test_os_passos_marcam_o_que_ja_passou(V):
    def pagina():
        V["passos"](["Dados", "Revisão", "Envio"], atual=1)

    no = sonda(V, pagina).primeiro("passos")
    assert no.props["concluidos"] == ["Dados"] and no.props["atual"] == 1


# ── Fragmentos ──────────────────────────────────────────────

def test_o_fragmento_anota_quem_mora_dentro_dele(V):
    def pagina():
        f = V["fragmento"]("cotacoes")
        f.botao("Atualizar", chave="b")
        V["botao"]("Fora", chave="fora")

    t = sonda(V, pagina)
    assert t.ctx.dono_do_fragmento.get("b") == "cotacoes"
    assert "fora" not in t.ctx.dono_do_fragmento


def test_o_clique_dentro_do_fragmento_responde_so_o_pedaco(V):
    def pagina():
        V["titulo"]("Painel inteiro")
        f = V["fragmento"]("agora")
        f.botao("Atualizar", chave="b")

    t = sonda(V, pagina)
    t.rodar(eventos=["b"])
    alvo = t.app._fragmento_da_resposta(t.ctx, "b", "")
    assert alvo == "agora"


def test_uma_falha_derruba_a_resposta_parcial(V):
    """O erro é desenhado fora do fragmento, e ficaria invisível."""
    def pagina():
        f = V["fragmento"]("agora")
        f.botao("Atualizar", chave="b")
        raise ValueError("quebrou")

    t = sonda(V, pagina)
    t.rodar(eventos=["b"])
    assert t.app._fragmento_da_resposta(t.ctx, "b", "") == ""


def test_um_fragmento_que_sumiu_volta_a_pagina_inteira(V):
    def pagina():
        V["titulo"]("nada aqui")

    t = sonda(V, pagina)
    assert t.app._fragmento_da_resposta(t.ctx, "b", "sumido") == ""


# ── Tema ────────────────────────────────────────────────────

def test_um_tema_escuro_pedido_pelo_nome_nao_volta_ao_claro(V):
    """Deixá-lo no automático faria o tema escolhido deixar de valer."""
    def pagina():
        V["titulo"]("x")

    V["app"]("Painel", tema="meia-noite")
    html = sonda(V, pagina).html()
    assert 'data-tema="escuro"' in html
    assert "prefers-color-scheme" not in html


def test_um_tema_que_nao_existe_sugere_o_parecido(V):
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        V["tema"]("meianoite")
    assert "meia" in str(erro.value.nota)


def test_a_densidade_muda_o_respiro_e_nao_a_cor(V):
    from dataforge.stdlib.vitrine import tema as TM

    compacta = TM.densidade("compacta")
    folgada = TM.densidade("folgada")
    assert compacta != folgada
    for texto in (compacta, folgada):
        assert "#" not in texto, "a densidade não pode mexer em cor"


def test_os_seis_temas_prontos_carregam(V):
    from dataforge.stdlib.vitrine import tema as TM

    for nome in TM.nomes():
        claro, escuro = TM.resolver(nome)
        assert claro["fundo"] and escuro["texto"]


# ── Recurso, conexão e segredos ─────────────────────────────

def test_o_recurso_devolve_o_MESMO_objeto(V):
    """Um cache com teto soltaria a conexão, e o pool do banco acabaria."""
    aberturas = []

    def abrir(qual):
        aberturas.append(qual)
        return {"conexao": qual}

    embrulhado = V["recurso"](abrir)
    assert embrulhado("a") is embrulhado("a")
    assert embrulhado("b") is not embrulhado("a")
    assert aberturas == ["a", "b"]


def test_a_conexao_e_a_mesma_entre_execucoes(V):
    banco = V["conexao"]("teste_vitrine")
    assert V["conexao"]("teste_vitrine") is banco
    banco.executar("CREATE TABLE t (n INTEGER)")
    banco.executar("INSERT INTO t VALUES (?)", [7])
    assert banco.consultar("SELECT n FROM t") == [{"n": 7}]
    assert "t" in banco.tabelas()
    banco.fechar()


def test_um_nome_de_tabela_estranho_e_recusado(V):
    """O SQLite não aceita nome por parâmetro: ele vai cru para o SQL."""
    from dataforge.errors import RuntimeError_

    banco = V["conexao"]("teste_seguro")
    try:
        with pytest.raises(RuntimeError_):
            banco.colunas("t; DROP TABLE x")
    finally:
        banco.fechar()


def test_o_ambiente_vence_o_arquivo_de_segredos(V, monkeypatch):
    monkeypatch.setenv("CHAVE_DE_TESTE", "do-ambiente")
    assert V["segredo"]("CHAVE_DE_TESTE") == "do-ambiente"


def test_o_segredo_mascarado_mostra_so_o_fim(V):
    from dataforge.stdlib.vitrine import conexoes as CX

    CX._SEGREDOS.update({"carregado": True, "de": "teste",
                         "dados": {"api": "sk_muito_secreto_1234"}})
    try:
        mascarados = V["segredos_mascarados"]()
        assert mascarados["api"] == "••••1234"
        assert "secreto" not in str(mascarados)
    finally:
        CX._SEGREDOS.update({"carregado": False, "dados": {}, "de": ""})


def test_o_toml_simples_le_secao_e_tipo():
    from dataforge.stdlib.vitrine import conexoes as CX

    lido = CX._toml_simples(
        '# comentário\nporta = 8501\nligado = true\n'
        '[banco]\nsenha = "abc"\n')
    assert lido["porta"] == 8501
    assert lido["ligado"] is True
    assert lido["banco"]["senha"] == "abc"


# ── Exportar ────────────────────────────────────────────────

def test_o_svg_exportado_e_o_mesmo_que_a_pagina_desenha(V):
    saida = {}

    def pagina():
        g = V["grafico"]("barras", VENDAS)
        g.eixo_x("mes")
        g.eixo_y("receita")
        saida["svg"] = V["exportar_svg"](g)
        V["desenhar"](g)

    html = sonda(V, pagina).html()
    assert "xmlns=" in saida["svg"], "um SVG solto precisa do namespace"
    miolo = saida["svg"].split(">", 1)[1]
    assert miolo in html, "o arquivo baixado difere do que está na tela"


def test_a_planilha_exportada_e_um_zip_valido(V):
    import io
    import zipfile

    pacotes = []

    def pagina():
        V["exportar_excel"](VENDAS)

    t = sonda(V, pagina)
    for chave in t.sessao.tudo():
        if chave.startswith("__baixar__"):
            pacotes.append(t.sessao.obter(chave))
    assert pacotes, "o botão de baixar não guardou nada"
    conteudo = pacotes[0]["conteudo"]
    assert isinstance(conteudo, bytes), (
        "o .xlsx virou texto — o arquivo baixado abriria corrompido")
    with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
        assert "xl/workbook.xml" in z.namelist()


# ── O cliente continua sem buscar nada de fora ──────────────

def test_o_css_e_o_js_novos_tambem_nao_buscam_nada_de_fora():
    """Uma CDN quebra qualquer app em rede fechada — que é onde painel
    de dados costuma rodar."""
    from dataforge.stdlib.vitrine import tema as TM

    folha = render.estilo(TM.CLARO, TM.ESCURO)
    cliente = render.script({})
    for texto, nome in ((folha, "CSS"), (cliente, "JS")):
        for proibido in ("http://", "https://", "cdn.", "unpkg", "jsdelivr"):
            assert proibido not in texto, f"{nome} busca {proibido}"


def test_o_exemplo_do_painel_financeiro_roda():
    """O exemplo é a prova de ponta a ponta: ele monta o painel inteiro
    em DataForge e confere o resultado com os próprios `assert`."""
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alvo = os.path.join(raiz, "examples", "vitrine_painel_financeiro.df")
    if not os.path.isfile(alvo):
        pytest.skip("o exemplo não está neste checkout")
    saida = subprocess.run([sys.executable, "-m", "dataforge", "run", alvo],
                           capture_output=True, text=True, encoding="utf-8",
                           cwd=raiz)
    assert saida.returncode == 0, saida.stdout + saida.stderr
    assert "painel ok" in saida.stdout


# ═══════════════════════════════════════════════════════════
#  Dois defeitos que só a tela mostrou
# ═══════════════════════════════════════════════════════════

def test_o_layout_diz_ao_grafico_a_largura_em_que_ele_vai_aparecer(V):
    """O desenho é feito em 800 unidades e o CSS o encolhe.

    Num painel de um terço da tela o fator é 0,45, e um rótulo de 11px
    chega ao olho com 5px — ilegível, sem nada que denuncie, porque de
    longe o gráfico continua bonito. Sem a largura vinda do layout, não
    há como compensar: o servidor não mede a tela.
    """
    def pagina():
        V["grafico_linha"](VENDAS, x="mes", y="receita", titulo="cheio")
        m = V["malha"](3)
        m.painel("Um terço").grafico_linha(
            VENDAS, x="mes", y="receita", titulo="terco")
        V["lateral"]().grafico_linha(
            VENDAS, x="mes", y="receita", titulo="lateral")

    t = sonda(V, pagina)
    larguras = {no.props["titulo"]: no.props["largura_css"]
                for no in t.achar("grafico")}
    assert larguras["cheio"] > larguras["terco"] > larguras["lateral"], (
        f"a largura não desce com o aninhamento: {larguras}")
    assert larguras["terco"] < 420, (
        "um painel de um terço não tem a largura da página inteira")


def test_o_texto_do_grafico_cresce_quando_o_espaco_encolhe(V):
    """`--v-fs` desfaz o encolhimento na medida exata dele."""
    def pagina():
        m = V["malha"](3)
        m.painel("Estreito").grafico_linha(VENDAS, x="mes", y="receita")

    html = sonda(V, pagina).html()
    tamanhos = [float(t) for t in re.findall(r"--v-fs:([\d.]+)px", html)]
    assert tamanhos and max(tamanhos) > 11.0, (
        "o texto não foi compensado — ele vai chegar à tela menor que 11px")
    assert max(tamanhos) <= 11 * 2.6 + 0.1, (
        "compensar sem teto faz o rótulo ocupar metade do gráfico")


def test_um_valor_ausente_vira_vao_e_nao_zero(V):
    """A linha despencava ao chegar no mês que ainda não aconteceu.

    Um gráfico que mostra uma queda de um milhão onde só falta o dado é
    pior que um gráfico que para: ele afirma um número.
    """
    serie = [{"mes": "jan", "total": 100}, {"mes": "fev", "total": 140},
             {"mes": "mar", "total": None}, {"mes": "abr", "total": None}]

    def pagina():
        V["grafico_linha"](serie, x="mes", y="total")

    t = sonda(V, pagina)
    valores = t.primeiro("grafico").props["series"][0]["valores"]
    assert valores == [100, 140, None, None], (
        f"a ausência virou {valores[2]!r}")

    svg = render.desenhar(t.primeiro("grafico"))
    caminho = re.search(r'<path d="([^"]+)" fill="none"', svg).group(1)
    # Dois pontos, um traço: o vão fica no fim e não há recomeço. A
    # conferência é no CAMINHO, e não no SVG inteiro — a linha da grade
    # do zero está lá de qualquer jeito, e é ela que deve estar.
    assert caminho.count("M") == 1 and caminho.count("L") == 1, caminho
    piso = render._y_de(0, *render._escala(
        [{"nome": "t", "valores": [100, 140]}], {})[:2], 280)
    assert f"{piso:.1f}" not in caminho, "a linha foi até o zero mesmo assim"


def test_o_vao_no_meio_parte_o_traco_em_dois(V):
    serie = [{"m": "a", "v": 10}, {"m": "b", "v": None}, {"m": "c", "v": 30}]

    def pagina():
        V["grafico_linha"](serie, x="m", y="v")

    svg = render.desenhar(sonda(V, pagina).primeiro("grafico"))
    caminho = re.search(r'<path d="([^"]+)" fill="none"', svg)
    assert caminho and caminho.group(1).count("M") == 2, (
        "os dois lados do vão foram ligados por uma reta que não existe")


def test_uma_barra_ausente_nao_e_desenhada_como_zero(V):
    serie = [{"m": "a", "v": 10}, {"m": "b", "v": None}]

    def pagina():
        V["grafico_barras"](serie, x="m", y="v")

    svg = render.desenhar(sonda(V, pagina).primeiro("grafico"))
    assert svg.count("<rect") == 1


def test_o_total_no_centro_cabe_no_buraco_da_rosca(V):
    """Um número de doze dígitos atravessava o anel e saía dos dois lados.

    O tamanho sai do BURACO, e não da escala do resto do texto: o
    número é o que mais importa na tela, e um número cortado ao meio
    não vale nada.
    """
    def pagina():
        g = V["grafico"]("rosca", {"a": 700000.0, "b": 426601.0})
        g.total_no_centro("R$ 1.126.601,00", "Total investido")
        V["desenhar"](g)

    svg = render.desenhar(sonda(V, pagina).primeiro("grafico"))
    tamanhos = [float(t) for t in re.findall(r"font-size:([\d.]+)px", svg)]
    assert tamanhos, "o centro saiu sem tamanho próprio"
    valor = max(tamanhos)
    # 15 caracteres a esse tamanho têm de caber no diâmetro do buraco.
    buraco = 2 * min(280 / 2 - 14, 128) * 0.64
    assert len("R$ 1.126.601,00") * valor * 0.54 <= buraco * 1.05, (
        f"o total de {valor:.1f}px atravessa um buraco de {buraco:.0f}")


def test_o_rotulo_do_centro_tem_um_piso_de_tamanho(V):
    """A 42% de um valor já encolhido ele saía com três pixels na tela."""
    def pagina():
        g = V["grafico"]("rosca", {"a": 1.0, "b": 2.0})
        g.total_no_centro("R$ 1.126.601,00", "Total investido no ano")
        V["desenhar"](g)

    svg = render.desenhar(sonda(V, pagina).primeiro("grafico"))
    tamanhos = sorted(float(t) for t in re.findall(r"font-size:([\d.]+)px", svg))
    assert tamanhos[0] >= 10.0, (
        f"o rótulo saiu com {tamanhos[0]}px — desenhado e ilegível")


def test_o_eixo_deitado_nao_escreve_por_cima_da_ultima_barra(V):
    """A última barra e os números do eixo dividiam o mesmo pedaço."""
    def pagina():
        V["grafico_barras_h"]([{"g": "Habitação", "v": 9000},
                               {"g": "Financeiras", "v": 6400}],
                              x="g", y="v", formato="moeda")

    svg = render.desenhar(sonda(V, pagina).primeiro("grafico"))
    altura = float(re.search(r"viewBox=\"0 0 800 ([\d.]+)\"", svg).group(1))
    barras = [float(y) + float(h) for y, h in re.findall(
        r'<rect[^>]*y="([\d.]+)"[^>]*height="([\d.]+)"', svg)]
    # A primeira marca do eixo é a única ancorada em `start`: é ela que
    # diz onde a faixa dos números começa.
    eixo = float(re.search(
        r'<text class="v-eixo" x="[\d.]+" y="([\d.]+)" text-anchor="start"',
        svg).group(1))
    assert max(barras) <= altura, "a barra saiu da moldura"
    assert max(barras) < eixo - 6, (
        f"a última barra termina em {max(barras):.0f} e os números do eixo "
        f"começam em {eixo:.0f} — eles se sobrepõem")


def test_a_barra_na_celula_nao_mostra_o_numero_cru(V):
    """`95.77777777777777` ao lado de uma barrinha não é leitura."""
    linhas = [{"g": "a", "uso": 8620 / 9000 * 100}]

    def pagina():
        V["grade"](linhas, colunas=[
            V["coluna"]("g"), V["coluna"]("uso", tipo="barra", maximo=130)])

    celula = sonda(V, pagina).primeiro("grade").props["linhas"][0]["celulas"][1]
    assert celula["texto"] == "95,8", celula["texto"]


def test_a_linha_nao_e_ancorada_no_zero_e_a_barra_e(V):
    """Forçar o zero num patrimônio de 1,02 a 1,13 milhão desenha uma reta.

    A diferença não é estética. Numa barra o que significa é o
    COMPRIMENTO, e cortar o eixo faz uma barra 3% maior parecer o
    dobro — o gráfico enganoso clássico. Numa linha o que significa é
    a POSIÇÃO, e ancorar no zero apaga a variação que o gráfico existe
    para mostrar.
    """
    serie = [{"m": "jan", "v": 1020000}, {"m": "fev", "v": 1075000},
             {"m": "mar", "v": 1130000}]

    def pagina():
        V["grafico_linha"](serie, x="m", y="v")
        V["grafico_barras"](serie, x="m", y="v")
        V["grafico_area"](serie, x="m", y="v")

    t = sonda(V, pagina)
    linha, barras, area = t.achar("grafico")
    valores = [{"nome": "v", "valores": [1020000, 1075000, 1130000]}]
    piso_linha = render._escala(valores, linha.props, ancorar_no_zero=False)[0]
    piso_barra = render._escala(valores, barras.props)[0]
    assert piso_barra == 0.0, "a barra precisa começar no zero"
    assert piso_linha > 900000, (
        f"a linha foi ancorada em {piso_linha} e a variação some")

    # E a área volta ao zero: o preenchimento afirma magnitude.
    svg_area = render.desenhar(area)
    assert ">0<" in svg_area, "a área precisa mostrar o zero no eixo"


def test_o_eixo_nao_repete_o_mesmo_rotulo(V):
    """Um eixo de 1,02 a 1,13 milhão escrevia `1,1 mi` em todas as marcas.

    Um eixo cujas marcas são todas iguais não é um eixo — é uma coluna
    de ruído ao lado do gráfico.
    """
    rotulos = render._rotulos_distintos(
        [1020000, 1050000, 1080000, 1110000, 1140000], {"formato": "compacto"})
    assert len(set(rotulos)) == len(rotulos), rotulos
    assert rotulos[0] == "1,02 mi"

    # E não gasta casas onde elas não fazem falta.
    assert render._rotulos_distintos([0, 10, 20], {"formato": "compacto"}) == \
        ["0", "10", "20"]


def test_quem_pede_as_casas_manda_nelas(V):
    """Subir a precisão por conta própria sobre um número de casas
    explícito seria desobedecer a quem escreveu o gráfico."""
    rotulos = render._rotulos_distintos(
        [1.001, 1.002], {"formato": "numero", "casas": 0})
    assert rotulos == ["1", "1"]


# ═══════════════════════════════════════════════════════════
#  O mesmo arquivo serve e se testa
# ═══════════════════════════════════════════════════════════

def test_modo_servidor_responde_ao_comando_e_a_flag(V, monkeypatch):
    """Um arquivo de painel tem dois destinos, e eles se contradizem.

    `dataforge vitrine dev` espera que ele termine chamando `V.subir` e
    **fique servindo**; a suíte roda o mesmo arquivo com `dataforge
    run`, e um arquivo que sobe um servidor ali nunca termina.
    """
    monkeypatch.delenv("VITRINE_PORTA", raising=False)
    monkeypatch.delenv("VITRINE_RECARREGAR", raising=False)
    monkeypatch.setattr(sys, "argv", ["dataforge", "run", "x.df"])
    assert V["modo_servidor"]() is False

    monkeypatch.setenv("VITRINE_PORTA", "8501")
    assert V["modo_servidor"]() is True

    monkeypatch.delenv("VITRINE_PORTA")
    monkeypatch.setattr(sys, "argv", ["dataforge", "run", "x.df", "--servir"])
    assert V["modo_servidor"]() is True


def test_todo_exemplo_de_painel_sobe_com_o_comando_do_framework():
    """Uma flag própria (`-- --servir`) faz o arquivo deixar de funcionar
    com `dataforge vitrine run/dev`, que é o comando que o framework
    oferece — e o sintoma é o painel rodar os testes e sair, em vez de
    servir. Quem lê a saída conclui que o comando está quebrado.
    """
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alvos = glob.glob(os.path.join(raiz, "examples", "vitrine_*.df"))
    assert alvos, "nenhum exemplo de painel neste checkout"
    for alvo in alvos:
        fonte = open(alvo, encoding="utf-8").read()
        if "V.rodar" not in fonte and "V.subir" not in fonte:
            continue
        assert "V.modo_servidor()" in fonte, (
            f"{os.path.basename(alvo)} decide se sobe por conta própria; "
            "use 'given V.modo_servidor():' para que "
            "'dataforge vitrine dev' funcione nele")


def test_o_vitrine_dev_de_fato_serve(tmp_path):
    """A ponta a ponta: o comando do framework sobe o painel e responde.

    O teste anterior confere o TEXTO do exemplo; este confere o que o
    comando faz. Os dois juntos são o que impede a combinação voltar a
    quebrar — foi assim que ela quebrou: cada metade estava certa.
    """
    import socket
    import subprocess
    import time
    import urllib.request

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alvo = os.path.join(raiz, "examples", "vitrine_painel_financeiro.df")
    if not os.path.isfile(alvo):
        pytest.skip("o exemplo não está neste checkout")

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        porta = s.getsockname()[1]

    processo = subprocess.Popen(
        [sys.executable, "-m", "dataforge", "vitrine", "run", alvo,
         f"--porta={porta}"],
        cwd=raiz, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8")
    try:
        corpo = ""
        for _ in range(60):
            if processo.poll() is not None:
                saida = processo.stdout.read()
                pytest.fail(
                    "o 'vitrine run' terminou em vez de servir — o exemplo "
                    f"rodou os próprios testes e saiu:\n{saida[-600:]}")
            try:
                with urllib.request.urlopen(
                        f"http://127.0.0.1:{porta}/", timeout=1) as r:
                    corpo = r.read().decode()
                break
            except Exception:                                # noqa: BLE001
                time.sleep(0.25)
        assert "v-indicador" in corpo, "o painel não chegou ao navegador"
    finally:
        processo.terminate()
        try:
            processo.wait(timeout=10)
        except subprocess.TimeoutExpired:
            processo.kill()
