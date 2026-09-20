"""A superfície pública — o que sai de `adopt Arcane.Vitrine as V`.

Uma aplicação implícita
-----------------------
Um app de uma página não deveria precisar declarar aplicação nenhuma:

    adopt Arcane.Vitrine as V

    action pagina():
        V.titulo("Olá")

    V.rodar(pagina)

A aplicação existe — `V.app()` a devolve — mas quem não precisa dela
não a vê. Quando o app cresce para várias páginas, ela aparece:

    app := V.app("Painel", tema := "escuro")
    V.pagina("/", inicio)
    V.pagina("/vendas", vendas)
    V.subir(porta := 8501)
"""

import threading
import time

from . import componentes as C
from . import conteudo as CT
from . import conexoes as CX
from . import dados as D
from . import entradas as E
from . import graficos as G
from . import graficos_avancados as GA
from . import layout as L
from . import render as R
from . import extras as X
from . import tema as TM
from . import teste as T
from .estado import Cache, Estado, Geral, Recurso
from .nucleo import Contexto
from .runtime import Aplicacao, _Navegar, _Parar, _Reexecutar
from . import sessoes as _sessoes

#: Os componentes dos módulos novos também viram métodos de área —
#: sem esta chamada, `coluna.indicador(…)` não existiria e o painel
#: pararia no primeiro nível de aninhamento.
L.ligar_componentes(CT, [
    "escrever", "legenda", "citacao", "selo", "selos", "formula", "ajuda",
    "fluxo", "icone", "pdf", "iframe", "galeria", "toast", "esqueleto",
    "comemorar", "excecao", "status", "chat", "chat_mensagem",
    "chat_entrada"])
L.ligar_componentes(E, [
    "hora", "periodo", "faixa", "deslizante_opcoes", "pilulas", "segmentado",
    "avaliacao", "tags", "autocompletar", "senha", "busca", "email",
    "camera"])
L.ligar_componentes(D, [
    "grade", "editor", "indicador", "indicadores", "estatisticas"])
L.ligar_componentes(GA, [
    "grafico_combo", "grafico_barras_100", "grafico_area_empilhada",
    "grafico_funil", "grafico_treemap", "grafico_cascata", "grafico_pareto",
    "medidor", "grafico_bala", "mapa_de_calor", "grafico_calendario",
    "grafico_radar", "grafico_caixa", "grafico_bolhas",
    "grafico_dispersao_xy", "grafico_velas", "grafico_sankey",
    "grafico_gantt", "grafico_mapa", "grafico_rede", "mini_grafico"])

_TRAVA = threading.RLock()
_ATUAL = {"app": None}


def _app():
    """A aplicação de agora — a do contexto, ou a implícita."""
    ctx = Contexto.atual()
    if ctx is not None and ctx.app is not None:
        return ctx.app
    with _TRAVA:
        if _ATUAL["app"] is None:
            _ATUAL["app"] = _ligar(Aplicacao())
        return _ATUAL["app"]


def _ligar(aplicacao):
    """Liga a aplicação ao cache e ao estado global do módulo.

    Eles são do módulo e não da aplicação porque um `mark @V.cache` no
    topo do arquivo é avaliado ANTES de qualquer `V.app(...)`. Sem esta
    ligação, `V.metricas()` relataria as estatísticas de um cache vazio
    que ninguém usa.
    """
    aplicacao.cache = _CACHE
    aplicacao.geral = _GERAL
    return aplicacao


def _ctx():
    return C._ctx()


# ═══════════════════════════════════════════════════════════
#  Aplicação, páginas, servidor
# ═══════════════════════════════════════════════════════════

def app(titulo="Vitrine", **config):
    """Cria a aplicação e passa a ser a atual."""
    with _TRAVA:
        _ATUAL["app"] = _ligar(Aplicacao(titulo, **config))
        return _ATUAL["app"]


def configurar(chave=None, valor=None, **pares):
    return _app().configurar(chave, valor, **pares)


def configurar_pagina(titulo="", icone="", **pares):
    """Muda título e ícone **só desta página**, sem tocar nas outras."""
    ctx = _ctx()
    if titulo:
        ctx.config_local["titulo"] = C._str(titulo)
    if icone:
        ctx.config_local["icone"] = C._str(icone)
    ctx.config_local.update(pares)
    return ctx.config_local


def pagina(caminho, acao=None, titulo="", icone="", oculta=False):
    """Registra uma página. Também serve de decorador.

        mark @V.pagina("/vendas")
        action vendas():
            V.titulo("Vendas")
    """
    if acao is None:
        def registrar(alvo):
            _app().pagina(caminho, alvo, titulo, icone, oculta)
            return alvo
        return registrar
    return _app().pagina(caminho, acao, titulo, icone, oculta)


def paginas():
    return _app().menu()


def rodar(acao=None, porta=8501, host="127.0.0.1", recarregar=False,
          silencioso=False):
    """Sobe a aplicação. Com uma ação, ela vira a página de `/`."""
    aplicacao = _app()
    if acao is not None and not aplicacao.paginas:
        aplicacao.pagina("/", acao)
    return aplicacao.subir(porta, host, silencioso, recarregar)


def subir(porta=8501, host="127.0.0.1", recarregar=False, silencioso=False):
    return _app().subir(porta, host, silencioso, recarregar)


def servir(porta=0, host="127.0.0.1"):
    """Sobe em segundo plano e devolve a porta. Para teste e para script."""
    return _app().servir(porta, host)


def parar_servidor():
    return _app().parar()


def montar():
    """O app Kiln por baixo — para acrescentar rota, REST ou middleware."""
    return _app().montar()


# ═══════════════════════════════════════════════════════════
#  Navegação e fluxo
# ═══════════════════════════════════════════════════════════

def navegar(destino):
    """Vai para outra página. Interrompe o programa aqui."""
    raise _Navegar(str(destino))


def parar():
    """Acaba a página neste ponto, sem erro.

    É o que se usa depois de uma barreira de login: mostrar a tela de
    entrada e não deixar o resto do programa rodar.
    """
    raise _Parar()


def recarregar():
    """Roda a página de novo, do começo, jogando fora o que foi montado.

    Serve para quando o estado mudou no meio e o que já está na tela
    ficou errado. Há um teto de reexecuções: um `V.recarregar()` sem
    `given` em volta vira uma mensagem, e não um servidor travado.
    """
    raise _Reexecutar()


def caminho_atual():
    return _ctx().caminho


def parametros():
    """Os parâmetros da URL: os da rota e os da query, juntos."""
    return dict(_ctx().params)


def parametro(nome, padrao=""):
    return _ctx().params.get(str(nome), padrao)


def menu(rotulo="Páginas"):
    """Desenha o menu das páginas registradas na barra lateral."""
    ctx = _ctx()
    lado = L.lateral()
    if rotulo:
        lado.cabecalho(rotulo, 4)
    for item in ctx.menu:
        marca = f'{item["icone"]} ' if item["icone"] else ""
        lado.link(f'{marca}{item["titulo"]}', item["caminho"])
    return ctx.menu


# ═══════════════════════════════════════════════════════════
#  Autenticação, autorização
# ═══════════════════════════════════════════════════════════

def autenticacao(verificador, papeis=None):
    return _app().autenticacao(verificador, papeis)


def entrar(usuario, senha):
    return _app().entrar(_ctx().sessao, usuario, senha)


def sair():
    return _app().sair(_ctx().sessao)


def usuario():
    """Quem está logado, ou `void`."""
    return _ctx().sessao.obter("__usuario__")


def autenticado():
    return _ctx().sessao.obter("__usuario__") is not None


def pode(permissao):
    return _app().pode(_ctx().sessao, permissao)


def exigir_login(mensagem="Entre para continuar."):
    """A barreira: mostra o formulário de entrada e para a página.

    Devolve o usuário quando já está logado, e nesse caso não desenha
    nada — o que permite chamá-la na primeira linha de toda página.
    """
    quem = usuario()
    if quem is not None:
        return quem

    ctx = _ctx()
    C.titulo("Entrar")
    C.texto(mensagem)
    forma = L.formulario("__login__")
    nome = forma.entrada("Usuário", chave="__login_usuario")
    senha = forma.entrada("Senha", tipo="senha", chave="__login_senha")
    if forma.enviar("Entrar"):
        achado = entrar(nome, senha)
        if achado is not None:
            ctx.sessao.remover("__campo____login_senha")
            # A página roda **de novo, do começo**, agora como a de quem
            # já entrou. Continuar daqui parece mais barato e não
            # funciona: quem escreveu 'given V.autenticado(): …' já
            # passou por esse teste com a resposta antiga, e a tela
            # sairia vazia no instante em que a pessoa acertou a senha.
            raise _Reexecutar()
        C.erro("Usuário ou senha inválidos.")
    parar()


def exigir_permissao(permissao, mensagem=""):
    """Barra quem não tem a permissão. Devolve o usuário quando tem."""
    quem = exigir_login()
    if not pode(permissao):
        C.erro(C._str(mensagem) or
               f"Você não tem permissão para isto ({permissao}).")
        parar()
    return quem


# ═══════════════════════════════════════════════════════════
#  Observabilidade
# ═══════════════════════════════════════════════════════════

def registrar(mensagem, nivel="info", extra=None):
    return _app().registrar(nivel, mensagem, extra)


def logs(quantos=100, nivel=""):
    return _app().logs(quantos, nivel)


def metricas():
    return _app().metricas()


def saude():
    return _app().saude()


def plugin(nome, instalar):
    return _app().plugin(nome, instalar)


def antes(funcao):
    """Middleware: roda antes de toda página. `no` interrompe."""
    _app().antes.append(funcao)
    return funcao


def depois(funcao):
    """Middleware de saída: recebe o contexto já montado."""
    _app().depois.append(funcao)
    return funcao


def sessoes():
    return _app().armazem_de_sessao().contar()


def encerrar_sessao():
    sessao = _ctx().sessao
    # marcada, para o fim do pedido nao grava-la de volta
    sessao.encerrada = True
    _app().encerrar_sessao(sessao.id)


def sessoes_em_banco(caminho):
    """As sessoes num SQLite que todo processo abre. Aceita a conexao do Database."""
    return _sessoes.EmBanco(caminho)


def sessoes_em_arquivos(pasta):
    """As sessoes num JSON por sessao, numa pasta que os processos dividem."""
    return _sessoes.EmArquivos(C._str(pasta))


# ═══════════════════════════════════════════════════════════
#  Trabalho fora do pedido
# ═══════════════════════════════════════════════════════════

def tarefa(acao, *args):
    """Roda numa thread e devolve na hora.

    A página **não espera**. Use quando o resultado não é o que se vai
    mostrar agora — mandar um e-mail, gravar um log remoto. Para um
    resultado que a página precisa, `Arcane.Async`, que tem `await`.
    """
    linha = threading.Thread(target=acao, args=args, daemon=True)
    linha.start()
    return linha


def agendar(acao, a_cada, *args):
    """Roda de tempos em tempos, enquanto o processo viver.

    O primeiro disparo é depois do primeiro intervalo, e não na hora:
    agendar algo para "a cada hora" não deveria fazê-lo agora e de novo
    em uma hora.
    """
    intervalo = max(1.0, float(a_cada))
    parar_sinal = threading.Event()

    def laco():
        while not parar_sinal.wait(intervalo):
            try:
                acao(*args)
            except Exception as erro:      # noqa: BLE001
                _app().registrar("erro", f"tarefa agendada falhou: {erro}")

    threading.Thread(target=laco, daemon=True).start()
    return parar_sinal


def atualizar_a_cada(segundos):
    """A página se recarrega sozinha nesse intervalo.

    É o "tempo real" do framework, e ele é por pergunta, não por
    empurrão: o Kiln roda sobre o `http.server`, que não tem WebSocket.
    Para um painel que muda a cada segundos, perguntar é suficiente e
    não quebra atrás de proxy nenhum.
    """
    _ctx().config_local["atualizar_a_cada"] = max(0, int(segundos))
    return segundos


# ═══════════════════════════════════════════════════════════
#  Exportar
# ═══════════════════════════════════════════════════════════

def exportar_csv(dados, nome="dados.csv", rotulo="Baixar CSV",
                 separador=","):
    """Um botão que entrega os dados como CSV."""
    linhas, colunas = C._normalizar_tabela(dados)
    saida = [separador.join(_celula_csv(c, separador) for c in colunas)]
    saida.extend(separador.join(_celula_csv(v, separador) for v in linha)
                 for linha in linhas)
    C.baixar(rotulo, "\n".join(saida), nome, "text/csv; charset=utf-8")
    return dados


def exportar_json(dados, nome="dados.json", rotulo="Baixar JSON"):
    import json
    texto = json.dumps(R._serializavel(dados), ensure_ascii=False, indent=2)
    C.baixar(rotulo, texto, nome, "application/json")
    return dados


def _celula_csv(valor, separador):
    texto = C._str(valor)
    if any(c in texto for c in (separador, '"', "\n", "\r")):
        return '"' + texto.replace('"', '""') + '"'
    return texto


def html_da_pagina():
    """A página atual como HTML — para gravar em disco ou mandar por e-mail."""
    ctx = _ctx()
    return R.pagina(ctx, {**_app().config, **ctx.config_local})


def markdown_para_html(texto):
    return R.markdown(str(texto))


def tema(qual=None, densidade=None):
    """Lê ou troca o tema da aplicação.

        V.tema("meia-noite")
        V.tema({"primaria": "#0F62FE", "raio": "4px"})

    Sem argumento, devolve o que está valendo. A troca vale para a
    aplicação inteira — um tema por sessão exigiria recarregar o CSS a
    cada pedido, e o CSS é o que menos muda numa página.
    """
    aplicacao = _app()
    if qual is None and densidade is None:
        return {"tema": aplicacao.config.get("tema"),
                "modo": aplicacao.config.get("modo_tema", "automatico"),
                "densidade": aplicacao.config.get("densidade", "normal"),
                "prontos": TM.nomes()}
    if qual is not None:
        # Um nome errado precisa falhar AQUI, e não na hora de desenhar:
        # lá dentro o erro viraria uma página em branco sem dizer qual
        # tema foi pedido.
        TM.resolver(qual)
        aplicacao.config["tema"] = qual
    if densidade is not None:
        if str(densidade) not in TM.DENSIDADES:
            from ...errors import RuntimeError_
            raise RuntimeError_(
                f"densidade '{densidade}' nao existe.", 0, 0,
                nota="as densidades: " + ", ".join(TM.DENSIDADES),
                doc="vitrine/referencia")
        aplicacao.config["densidade"] = str(densidade)
    return aplicacao.config.get("tema")


def temas():
    """Os nomes dos temas prontos."""
    return TM.nomes()


def seletor_de_tema(rotulo="Tema"):
    """Desenha a troca de tema e devolve o escolhido.

    A troca reexecuta a página, pelo mesmo motivo do seletor de idioma:
    o CSS é escrito no cabeçalho, e metade da tela ficaria com as cores
    anteriores.
    """
    disponiveis = TM.nomes()
    atual = _app().config.get("tema")
    nome_atual = atual if isinstance(atual, str) else "claro"
    indice = (disponiveis.index(nome_atual)
              if nome_atual in disponiveis else 0)
    escolhido = C.escolha(rotulo, disponiveis, indice, chave="__tema__")
    if escolhido != nome_atual:
        tema(escolhido)
        raise _Reexecutar()
    return escolhido


def exportar_svg(grafico, nome="grafico.svg", rotulo="Baixar SVG"):
    """O gráfico como arquivo SVG, com um botão para baixá-lo.

    O SVG que sai daqui é **o mesmo** que a página desenha: ele vem do
    mesmo renderizador. Uma segunda rota para gerar imagem divergiria
    da primeira, e o arquivo baixado deixaria de ser o que se viu.
    """
    from .nucleo import No
    if not isinstance(grafico, G.Grafico):
        from ...errors import TypeError_
        raise TypeError_(
            "V.exportar_svg espera um grafico de V.grafico(...).", 0, 0,
            doc="vitrine/referencia")
    series, categorias = G._extrair(grafico.dados, grafico.props)
    no = No("grafico", {**grafico.props, "grafico": grafico.tipo,
                        "series": series, "categorias": categorias})
    desenho = R._SVG.get(grafico.tipo, R._svg_linha)(no.props, series,
                                                     categorias)
    completo = desenho.replace(
        "<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    C.baixar(rotulo, completo, nome, "image/svg+xml")
    return completo


def exportar_excel(dados, nome="dados.xlsx", rotulo="Baixar Excel",
                   aba="Dados"):
    """Uma planilha .xlsx de verdade, sem dependência externa.

    Ela sai do `Arcane.Excel`, que já escreve o formato à mão. Gerar um
    CSV com a extensão trocada — o atalho comum — faz o Excel abrir com
    aviso e estragar o separador decimal em pt-BR.
    """
    import os
    import random
    import tempfile

    from ..arcane_excel import ArcaneExcel

    linhas, colunas = C._normalizar_tabela(dados)
    modulo = ArcaneExcel()
    livro = modulo["new"]()
    modulo["sheet"](livro, C._str(aba), [list(l) for l in linhas],
                    list(colunas))

    # O `Arcane.Excel` escreve num CAMINHO, e o botão precisa de bytes.
    # A pasta é própria e sorteada: escrever direto no temporário do
    # sistema deixa lixo com nome previsível, e dois pedidos ao mesmo
    # tempo sobrescreveriam o arquivo um do outro.
    pasta = os.path.join(tempfile.gettempdir(),
                         f"vitrine-xlsx-{random.randint(100000, 999999)}")
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, "planilha.xlsx")
    try:
        modulo["save"](livro, caminho)
        with open(caminho, "rb") as arquivo:
            conteudo = arquivo.read()
    finally:
        for alvo in (caminho, pasta):
            try:
                os.remove(alvo) if os.path.isfile(alvo) else os.rmdir(alvo)
            except OSError:
                pass
    C.baixar(rotulo, conteudo, nome,
             "application/vnd.openxmlformats-officedocument."
             "spreadsheetml.sheet")
    return dados


def modo_servidor():
    """`yes` quando quem chamou quer o servidor **no ar**.

    Um arquivo de painel tem dois destinos, e eles se contradizem:

    - `dataforge vitrine run` e `dataforge vitrine dev` esperam que ele
      termine chamando `V.subir`, e **fiquem servindo**;
    - a suíte de testes roda o mesmo arquivo com `dataforge run`, e um
      arquivo que sobe um servidor ali nunca termina.

    Sem uma pergunta que separe os dois, o autor escolhe uma flag
    própria (`-- --servir`) e o arquivo deixa de funcionar com o
    comando que o framework oferece — que foi exatamente o que
    aconteceu. `V.modo_servidor()` é essa pergunta:

        given V.modo_servidor():
            V.rodar(painel)
        otherwise:
            conferir()

    Ela responde `yes` quando o `dataforge vitrine` anunciou a porta no
    ambiente, e quando `--servir` está nos argumentos — a segunda forma
    continua valendo para quem chama `dataforge run` direto.
    """
    import os
    import sys

    if os.environ.get("VITRINE_PORTA") or os.environ.get("VITRINE_RECARREGAR"):
        return True
    return any(arg in ("--servir", "--serve") for arg in sys.argv[1:])


def fragmentos():
    """As chaves dos fragmentos montados nesta execução."""
    return sorted(_ctx().nos_de_fragmento)


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

class ArcaneVitrine:
    """Arcane.Vitrine — dashboards e aplicações de dados."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Vitrine",

            # ── Aplicação e servidor ──
            "app": app,
            "configurar": configurar,
            "configurar_pagina": configurar_pagina,
            "pagina": pagina,
            "paginas": paginas,
            "rodar": rodar,
            "subir": subir,
            "modo_servidor": modo_servidor,
            "servir": servir,
            "parar_servidor": parar_servidor,
            "montar": montar,

            # ── Texto ──
            "escrever": CT.escrever,
            "legenda": CT.legenda,
            "citacao": CT.citacao,
            "selo": CT.selo,
            "selos": CT.selos,
            "formula": CT.formula,
            "ajuda": CT.ajuda,
            "fluxo": CT.fluxo,
            "icone": CT.icone,
            "icones": CT.icones,
            "texto": C.texto,
            "titulo": C.titulo,
            "subtitulo": C.subtitulo,
            "cabecalho": C.cabecalho,
            "markdown": C.markdown,
            "codigo": C.codigo,
            "html": C.html,
            "divisor": C.divisor,
            "espaco": C.espaco,

            # ── Entrada ──
            "botao": C.botao,
            "entrada": C.entrada,
            "area_de_texto": C.area_de_texto,
            "numero": C.numero,
            "deslizante": C.deslizante,
            "caixa": C.caixa,
            "interruptor": C.interruptor,
            "opcao": C.opcao,
            "escolha": C.escolha,
            "escolhas": C.escolhas,
            "data": C.data,
            "cor": C.cor,
            "arquivo": C.arquivo,
            "hora": E.hora,
            "periodo": E.periodo,
            "faixa": E.faixa,
            "deslizante_opcoes": E.deslizante_opcoes,
            "pilulas": E.pilulas,
            "segmentado": E.segmentado,
            "avaliacao": E.avaliacao,
            "tags": E.tags,
            "autocompletar": E.autocompletar,
            "senha": E.senha,
            "busca": E.busca,
            "email": E.email,
            "camera": E.camera,
            "mudou": E.mudou,
            "mudancas": E.mudancas,

            # ── Dados ──
            "tabela": C.tabela,
            "frame": C.frame,
            "metrica": C.metrica,
            "json": C.json_,
            "vault": C.vault,
            "grade": D.grade,
            "editor": D.editor,
            "coluna": D.coluna,
            "regra": D.regra,
            "indicador": D.indicador,
            "indicadores": D.indicadores,
            "estatisticas": D.estatisticas,
            "formatar": D.formatar,
            "moeda": D.moeda,
            "numero_br": D.numero,
            "percentual": D.percentual,
            "compacto": D.compacto,
            "data_br": D.data_br,

            # ── Retorno ──
            "sucesso": C.sucesso,
            "erro": C.erro,
            "aviso": C.aviso,
            "informacao": C.informacao,
            "progresso": C.progresso,
            "carregando": C.carregando,
            "imagem": C.imagem,
            "audio": C.audio,
            "video": C.video,
            "link": C.link,
            "baixar": C.baixar,
            "pdf": CT.pdf,
            "iframe": CT.iframe,
            "logo": CT.logo,
            "galeria": CT.galeria,
            "toast": CT.toast,
            "esqueleto": CT.esqueleto,
            "comemorar": CT.comemorar,
            "excecao": CT.excecao,
            "status": CT.status,
            "chat": CT.chat,
            "chat_mensagem": CT.chat_mensagem,
            "chat_entrada": CT.chat_entrada,
            "historico_de_chat": CT.historico_de_chat,
            "guardar_no_chat": CT.guardar_no_chat,

            # ── Layout ──
            "colunas": L.colunas,
            "container": L.container,
            "linha": L.linha,
            "cartao": L.cartao,
            "expandir": L.expandir,
            "abas": L.abas,
            "formulario": L.formulario,
            "vazio": L.vazio,
            "lateral": L.lateral,
            "espacador": L.espacador,
            "malha": L.malha,
            "painel": L.painel,
            "barra_superior": L.barra_superior,
            "dialogo": L.dialogo,
            "popover": L.popover,
            "passos": L.passos,
            "separador": L.separador,
            "rolagem": L.rolagem,
            "fragmento": L.fragmento,
            "fragmentos": fragmentos,

            # ── Gráficos ──
            "grafico": G.grafico,
            "desenhar": G.desenhar,
            "grafico_linha": G.grafico_linha,
            "grafico_barras": G.grafico_barras,
            "grafico_barras_h": G.grafico_barras_h,
            "grafico_area": G.grafico_area,
            "grafico_dispersao": G.grafico_dispersao,
            "grafico_pizza": G.grafico_pizza,
            "grafico_rosca": G.grafico_rosca,
            "histograma": G.histograma,
            "paleta": list(G.PALETA),
            "tipos_de_grafico": list(G.TIPOS),
            "grafico_combo": GA.grafico_combo,
            "grafico_barras_100": GA.grafico_barras_100,
            "grafico_area_empilhada": GA.grafico_area_empilhada,
            "grafico_funil": GA.grafico_funil,
            "grafico_treemap": GA.grafico_treemap,
            "grafico_cascata": GA.grafico_cascata,
            "grafico_pareto": GA.grafico_pareto,
            "grafico_radar": GA.grafico_radar,
            "grafico_caixa": GA.grafico_caixa,
            "grafico_bolhas": GA.grafico_bolhas,
            "grafico_dispersao_xy": GA.grafico_dispersao_xy,
            "grafico_velas": GA.grafico_velas,
            "grafico_sankey": GA.grafico_sankey,
            "grafico_gantt": GA.grafico_gantt,
            "grafico_mapa": GA.grafico_mapa,
            "grafico_rede": GA.grafico_rede,
            "grafico_calendario": GA.grafico_calendario,
            "mapa_de_calor": GA.mapa_de_calor,
            "medidor": GA.medidor,
            "grafico_bala": GA.grafico_bala,
            "mini_grafico": GA.mini_grafico,

            # ── Estado ──
            "estado": Estado(),
            "geral": _GERAL,
            "cache": _CACHE,
            "recurso": _RECURSO,
            "conexao": CX.conexao,
            "conexao_de": CX.conexao_de,
            "conexoes": CX.conexoes,
            "fechar_conexoes": CX.fechar_conexoes,
            "segredos": CX.segredos,
            "segredo": CX.segredo,
            "segredos_mascarados": CX.segredos_mascarados,

            # ── Navegação ──
            "navegar": navegar,
            "parar": parar,
            "recarregar": recarregar,
            "caminho": caminho_atual,
            "parametros": parametros,
            "parametro": parametro,
            "menu": menu,

            # ── Segurança ──
            "autenticacao": autenticacao,
            "entrar": entrar,
            "sair": sair,
            "usuario": usuario,
            "autenticado": autenticado,
            "pode": pode,
            "exigir_login": exigir_login,
            "exigir_permissao": exigir_permissao,

            # ── Operação ──
            "registrar": registrar,
            "logs": logs,
            "metricas": metricas,
            "saude": saude,
            "plugin": plugin,
            "antes": antes,
            "depois": depois,
            "sessoes": sessoes,
            "encerrar_sessao": encerrar_sessao,
            "sessoes_em_banco": sessoes_em_banco,
            "sessoes_em_arquivos": sessoes_em_arquivos,
            "tarefa": tarefa,
            "agendar": agendar,
            "atualizar_a_cada": atualizar_a_cada,

            # ── Exportar ──
            "exportar_csv": exportar_csv,
            "exportar_json": exportar_json,
            "exportar_svg": exportar_svg,
            "exportar_excel": exportar_excel,
            "tema": tema,
            "temas": temas,
            "seletor_de_tema": seletor_de_tema,
            "html_da_pagina": html_da_pagina,
            "markdown_para_html": markdown_para_html,

            # ── Validação ──
            "validar": X.validar,
            "campo_validado": X.campo_validado,

            # ── Idioma ──
            "i18n": _I18N,
            "t": _I18N.traduzir,
            "traduzir": _I18N.traduzir,

            # ── Componentes próprios ──
            "componente": X.componente,
            "usar": X.usar,
            "componentes": X.componentes_registrados,

            # ── Testes ──
            "testar": T.testar,
            "pedir": T.pedir,
        }


#: O estado global e o cache vivem no módulo, e não na aplicação, de
#: propósito: um `mark @V.cache` no topo do arquivo é avaliado antes de
#: qualquer `V.app(...)`, e prendê-los à aplicação faria o decorador
#: falhar exatamente no uso mais comum.
_GERAL = Geral()
_CACHE = Cache()

#: O depósito de objetos vive no módulo pela mesma razão do cache: um
#: `mark @V.recurso` no topo do arquivo roda antes de qualquer
#: `V.app(...)`.
_RECURSO = Recurso()

#: A tradução também: as chaves são carregadas no topo do arquivo, antes
#: de qualquer 'V.app(...)'.
_I18N = X.Traducao()
