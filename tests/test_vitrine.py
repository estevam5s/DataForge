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
