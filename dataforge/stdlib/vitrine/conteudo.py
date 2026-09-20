"""Conteúdo — texto rico, mídia, status, conversa.

O que um painel precisa mostrar além de número e tabela: uma legenda
sob o gráfico, um selo de situação, um aviso que aparece e some, o
esqueleto enquanto o dado não chegou, e a conversa de um assistente.

Três decisões valem lembrar:

1. **`V.escrever` decide pelo valor, e não pelo tipo declarado.** Um
   vault de listas vira tabela; um vault simples vira lista de chave e
   valor; um gráfico montado é desenhado; um texto com marcação vira
   markdown. É o `st.write` do Streamlit, e a razão de existir é a
   mesma: no rascunho de uma análise, escolher o componente certo é
   atrito antes de haver o que mostrar.

2. **O ícone é desenhado aqui, e não buscado.** São 48 caminhos SVG no
   arquivo. Uma fonte de ícones de CDN quebraria a regra de rede
   fechada, e um emoji não tem a mesma cor do texto nem o mesmo peso.

3. **`V.fluxo` consome o gerador inteiro antes de desenhar.** A página
   é montada no servidor e vai pronta; não há como pintar palavra por
   palavra sem um canal aberto. A animação de digitação é do CSS, e a
   documentação diz isso — prometer streaming aqui seria mentir sobre
   o que acontece.
"""

import time

from . import componentes as C
from .nucleo import No

_str = C._str
_por = C._por
_ctx = C._ctx


# ═══════════════════════════════════════════════════════════
#  Texto
# ═══════════════════════════════════════════════════════════

def escrever(*valores):
    """Mostra o que vier, escolhendo o componente pelo valor.

        V.escrever("## Vendas")            // markdown
        V.escrever(vendas)                 // tabela
        V.escrever({"total": 12})          // vault
        V.escrever(V.grafico("linha")…)    // gráfico

    Devolve o último valor, para encadear.
    """
    ultimo = None
    for valor in valores:
        ultimo = _escrever_um(valor)
    return ultimo


def _escrever_um(valor):
    from . import graficos as G
    if isinstance(valor, G.Grafico):
        G.desenhar(valor)
        return valor
    if valor is None or isinstance(valor, bool):
        C.texto(_str(valor))
        return valor
    if isinstance(valor, (int, float)):
        C.texto(_str(valor))
        return valor
    if isinstance(valor, str):
        if _tem_marcacao(valor):
            C.markdown(valor)
        else:
            C.texto(valor)
        return valor
    if hasattr(valor, "to_dict") and hasattr(valor, "columns"):
        C.frame(valor)
        return valor
    if isinstance(valor, dict):
        # Vault de colunas é tabela; vault comum é chave e valor. A
        # diferença é o que a pessoa vê, e adivinhar errado aqui
        # transforma um relatório de dez colunas em dez linhas.
        if valor and all(isinstance(v, (list, tuple)) for v in valor.values()):
            C.frame(valor)
        else:
            C.vault(valor)
        return valor
    if isinstance(valor, (list, tuple, set)):
        itens = list(valor)
        if itens and isinstance(itens[0], dict):
            C.frame(itens)
        else:
            C.markdown("\n".join(f"- {_str(v)}" for v in itens))
        return valor
    if callable(valor):
        ajuda(valor)
        return valor
    C.texto(_str(valor))
    return valor


def _tem_marcacao(texto):
    marcas = ("#", "- ", "* ", "1. ", "> ", "```", "**", "__", "|")
    return any(linha.strip().startswith(marcas) or "**" in linha
               for linha in texto.split("\n"))


def legenda(conteudo):
    """Texto pequeno e discreto — a nota sob um gráfico ou uma tabela."""
    _por("legenda", {"conteudo": _str(conteudo)})
    return conteudo


def citacao(conteudo, autor=""):
    _por("citacao", {"conteudo": _str(conteudo), "autor": _str(autor)})
    return conteudo


def selo(texto, cor="neutro", icone=""):
    """Uma etiqueta curta: situação, categoria, contagem.

    As cores são as do tema — `neutro`, `sucesso`, `erro`, `aviso`,
    `info`, `primaria` —, e não um hexadecimal, para que um selo
    continue legível quando alguém troca o tema.
    """
    _por("selo", {"texto": _str(texto), "cor": _str(cor), "icone": _str(icone)})
    return texto


def selos(itens, cor="neutro"):
    """Vários selos numa linha só."""
    _por("selos", {"itens": [_str(i) for i in (itens or [])],
                   "cor": _str(cor)})
    return itens


def formula(expressao, bloco=True):
    """Uma fórmula matemática.

    Entende o subconjunto que aparece num painel: fração, potência,
    índice, raiz, somatório e as letras gregas. **Não** é um LaTeX
    completo, e o que ele não conhece sai como veio — ilegível é pior
    que errado, mas inventar uma renderização errada é pior que os dois.
    """
    _por("formula", {"tex": str(expressao), "bloco": bool(bloco)})
    return expressao


def ajuda(alvo):
    """A assinatura e a documentação de uma ação, na página.

    Serve ao mesmo que o `st.help`: explorar uma biblioteca sem sair da
    tela em que se está trabalhando.
    """
    nome = (getattr(alvo, "name", None) or getattr(alvo, "__name__", None)
            or _str(alvo))
    doc = (getattr(alvo, "doc", None) or getattr(alvo, "__doc__", None) or "")
    parametros = []
    for atributo in ("params", "parameters", "parametros"):
        lista = getattr(alvo, atributo, None)
        if lista:
            parametros = [getattr(p, "name", None) or _str(p) for p in lista]
            break
    _por("ajuda", {"nome": _str(nome), "doc": _str(doc).strip(),
                   "parametros": parametros})
    return alvo


def fluxo(gerador, velocidade=18):
    """Consome um gerador de texto e mostra o resultado.

    A animação de digitação é do CSS: a página é montada no servidor e
    chega pronta, então o texto inteiro já está aqui quando a primeira
    letra aparece. Devolve o texto completo, que é o que se guarda no
    histórico de uma conversa.
    """
    pedacos = []
    for pedaco in (gerador or []):
        if isinstance(pedaco, dict):
            pedacos.append(_str(pedaco.get("texto", pedaco.get("conteudo", ""))))
        else:
            pedacos.append(_str(pedaco))
    texto = "".join(pedacos)
    _por("fluxo", {"conteudo": texto, "velocidade": max(0, int(velocidade))})
    return texto


# ═══════════════════════════════════════════════════════════
#  Ícones
# ═══════════════════════════════════════════════════════════

#: Traçado de 24×24, com `currentColor`: o ícone é da cor do texto ao
#: lado dele, em qualquer tema, sem ninguém configurar nada.
ICONES = {
    "casa": "M3 10.5 12 3l9 7.5M5 9.5V21h14V9.5",
    "painel": "M3 3h8v8H3zM13 3h8v5h-8zM13 10h8v11h-8zM3 13h8v8H3z",
    "grafico": "M3 3v18h18M7 15l4-5 3 3 5-7",
    "barras": "M4 20V10M10 20V4M16 20v-8M22 20h-20",
    "pizza": "M12 3a9 9 0 1 0 9 9h-9z",
    "tabela": "M3 5h18v14H3zM3 10h18M9 10v9M15 10v9",
    "usuario": "M4 21v-2a5 5 0 0 1 5-5h6a5 5 0 0 1 5 5v2M12 3a4 4 0 1 0 0 8"
               " 4 4 0 0 0 0-8z",
    "usuarios": "M2 21v-2a4 4 0 0 1 4-4h5a4 4 0 0 1 4 4v2M9 3a3.5 3.5 0 1 0 0 7"
                " 3.5 3.5 0 0 0 0-7M17 11a3 3 0 1 0 0-6M18 21v-2a4 4 0 0 0-2-3.4",
    "carrinho": "M2 3h3l2.6 12h11L21 7H6M9 20a1 1 0 1 0 0-2 1 1 0 0 0 0 2"
                "M18 20a1 1 0 1 0 0-2 1 1 0 0 0 0 2",
    "dinheiro": "M3 6h18v12H3zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6",
    "moeda": "M12 2v20M17 6.5C17 4.6 14.8 3.5 12 3.5S7 4.6 7 6.5s2 2.8 5 3.5"
             "s5 1.6 5 3.5-2.2 3-5 3-5-1.1-5-3",
    "cartao": "M2 6h20v12H2zM2 10h20",
    "alvo": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8"
            "M12 11.5a.5.5 0 1 0 0 1 .5.5 0 0 0 0-1",
    "relogio": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18M12 7v5l3.5 2",
    "calendario": "M3 5h18v16H3zM3 10h18M8 3v4M16 3v4",
    "busca": "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14M20 20l-4-4",
    "filtro": "M3 4h18l-7 8v7l-4 2v-9z",
    "engrenagem": "M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6M19.4 15a1.6 1.6 0 0 0 .3 1.8"
                  "l.1.1-2 2-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21h-3v-.2a1.6 1.6 0 0 0-2.7-1.1"
                  "l-.1.1-2-2 .1-.1A1.6 1.6 0 0 0 4.6 15H3v-3h1.6a1.6 1.6 0 0 0 1.1-2.7"
                  "L5.6 9l2-2 .1.1A1.6 1.6 0 0 0 10.4 6V4h3v2a1.6 1.6 0 0 0 2.7 1.1"
                  "l.1-.1 2 2-.1.1A1.6 1.6 0 0 0 19.4 12H21v3z",
    "sino": "M18 9a6 6 0 1 0-12 0c0 6-2 7-2 7h16s-2-1-2-7M10.5 20a2 2 0 0 0 3 0",
    "estrela": "M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.9-5.2-2.8-5.2 2.8 1-5.9"
               "-4.3-4.1 5.9-.8z",
    "coracao": "M12 20s-7.5-4.6-7.5-9.4A4.1 4.1 0 0 1 12 8a4.1 4.1 0 0 1 7.5 2.6"
               "C19.5 15.4 12 20 12 20z",
    "raio": "M13 2 4 14h7l-1 8 9-12h-7z",
    "fogo": "M12 22a6 6 0 0 0 6-6c0-4-3-6-3-9 0 0-3 1.5-3 5 0-2-2-3-2-3"
            "s-4 3-4 7a6 6 0 0 0 6 6z",
    "escudo": "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z",
    "cadeado": "M5 11h14v10H5zM8 11V7a4 4 0 0 1 8 0v4",
    "chave": "M14 7a4 4 0 1 1-3.5 5.9L4 19.5V22H2v-2l8-8A4 4 0 0 1 14 7z",
    "arquivo": "M6 2h8l4 4v16H6zM14 2v5h5",
    "pasta": "M3 6h6l2 2h10v12H3z",
    "baixar": "M12 3v12M7 11l5 5 5-5M4 20h16",
    "enviar": "M3 11l18-8-8 18-2-7z",
    "nuvem": "M7 18a4 4 0 0 1 0-8 5.5 5.5 0 0 1 10.6 1.5A3.5 3.5 0 0 1 17 18z",
    "banco": "M3 10h18L12 4zM5 10v8M9 10v8M15 10v8M19 10v8M3 20h18",
    "servidor": "M3 4h18v6H3zM3 14h18v6H3zM7 7h.01M7 17h.01",
    "atualizar": "M20 11a8 8 0 1 0-1.5 5M20 5v6h-6",
    "mais": "M12 5v14M5 12h14",
    "menos": "M5 12h14",
    "conferir": "M4 12.5 9 18l11-12",
    "fechar": "M6 6l12 12M18 6 6 18",
    "sobe": "M5 15l7-7 7 7",
    "desce": "M5 9l7 7 7-7",
    "esquerda": "M15 5l-7 7 7 7",
    "direita": "M9 5l7 7-7 7",
    "info": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18M12 11v6M12 7.5h.01",
    "aviso": "M12 3 1.5 21h21zM12 10v5M12 18h.01",
    "erro": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18M9 9l6 6M15 9l-6 6",
    "olho": "M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6M12 9a3 3 0 1 0 0 6"
            " 3 3 0 0 0 0-6",
    "lixeira": "M4 7h16M10 7V5h4v2M6 7l1 14h10l1-14M10 11v6M14 11v6",
    "lapis": "M4 20h4L20 8l-4-4L4 16z",
    "link": "M10 13a4 4 0 0 0 5.7 0l3-3a4 4 0 1 0-5.7-5.7l-1 1M14 11a4 4 0 0 0-5.7 0"
            "l-3 3a4 4 0 1 0 5.7 5.7l1-1",
    "mapa": "M9 3 3 5v16l6-2 6 2 6-2V3l-6 2zM9 3v16M15 5v16",
    "robo": "M7 8h10v9H7zM12 4v4M9 12h.01M15 12h.01M4 12v3M20 12v3",
    "faisca": "M12 3l1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7z",
    "menu": "M4 7h16M4 12h16M4 17h16",
}


def icone(nome, tamanho=18, cor=""):
    """Um dos 48 ícones desenhados no módulo.

    Um nome que não existe vira um aviso com os parecidos — um ícone
    que some calado é a peça mais difícil de achar numa tela cheia.
    """
    chave = _str(nome).strip().lower()
    if chave not in ICONES:
        import difflib
        from ...errors import RuntimeError_
        perto = difflib.get_close_matches(chave, sorted(ICONES), n=3)
        raise RuntimeError_(
            f"nao ha um icone chamado '{nome}'.", 0, 0,
            nota=("voce quis dizer: " + ", ".join(perto) if perto else
                  f"sao {len(ICONES)} icones"),
            dica="V.icones() devolve a lista inteira",
            doc="vitrine/referencia")
    _por("icone", {"nome": chave, "tamanho": max(8, int(tamanho)),
                   "cor": _str(cor)})
    return chave


def icones():
    """Os nomes de todos os ícones."""
    return sorted(ICONES)


# ═══════════════════════════════════════════════════════════
#  Mídia
# ═══════════════════════════════════════════════════════════

def pdf(origem, altura=640, pagina=1):
    """Mostra um PDF na própria página."""
    _por("pdf", {"origem": _str(origem), "altura": max(120, int(altura)),
                 "pagina": max(1, int(pagina))})
    return origem


def iframe(origem, altura=420, titulo="Conteúdo incorporado"):
    """Incorpora outra página.

    O `sandbox` é ligado por padrão: o que entra aqui não é código
    desta aplicação, e deixá-lo rodar com os mesmos poderes da página
    é dar a ele a sessão de quem está logado.
    """
    _por("iframe", {"origem": _str(origem), "altura": max(80, int(altura)),
                    "titulo": _str(titulo)})
    return origem


def logo(origem, destino="/", largura=132):
    """A marca, no alto da barra lateral."""
    _ctx().config_local["logo"] = {
        "origem": _str(origem), "destino": _str(destino),
        "largura": max(24, int(largura))}
    return origem


def galeria(imagens, colunas=3, legendas=None):
    """Várias imagens numa grade."""
    lista = []
    rotulos = list(legendas or [])
    for i, img in enumerate(imagens or []):
        if isinstance(img, dict):
            lista.append({"origem": _str(img.get("origem", img.get("url", ""))),
                          "legenda": _str(img.get("legenda", ""))})
        else:
            lista.append({"origem": _str(img),
                          "legenda": _str(rotulos[i]) if i < len(rotulos) else ""})
    _por("galeria", {"imagens": lista, "colunas": max(1, int(colunas))})
    return imagens


# ═══════════════════════════════════════════════════════════
#  Situação
# ═══════════════════════════════════════════════════════════

def toast(mensagem, icone="", nivel="info", segundos=4):
    """Um aviso flutuante, que aparece e some sozinho.

    Diferente de `V.sucesso`, ele **não ocupa espaço** no fluxo da
    página: é para confirmar o que acabou de acontecer sem empurrar o
    resto da tela para baixo.
    """
    aviso = {"mensagem": _str(mensagem), "icone": _str(icone),
             "nivel": _str(nivel), "segundos": max(1, int(segundos))}
    # O nó entra na árvore, e não só numa lista à parte: é o que faz um
    # teste poder perguntar `t.achar("toast")`. Ele não ocupa espaço no
    # fluxo — quem o tira da página é o CSS, não a ausência do nó.
    _ctx().avisos.append(aviso)
    _por("toast", dict(aviso))
    return mensagem


def esqueleto(linhas=3, altura=14, largura="100%"):
    """O contorno cinza do que ainda não chegou.

    Mostrar o esqueleto em vez de um espaço vazio é o que impede a
    página de saltar quando o dado chega — e diz que algo vem vindo.
    """
    _por("esqueleto", {"linhas": max(1, int(linhas)),
                       "altura": max(4, int(altura)),
                       "largura": _str(largura)})


def comemorar(tipo="balao"):
    """Balões ou neve, por alguns segundos. `tipo`: balao, neve, confete."""
    permitidos = ("balao", "neve", "confete")
    escolhido = _str(tipo)
    if escolhido not in permitidos:
        escolhido = "balao"
    _por("comemorar", {"tipo": escolhido})


def excecao(erro, detalhe=""):
    """Um erro, desenhado como erro — com o tipo, a mensagem e o rastro."""
    tipo = (getattr(erro, "type", None) or getattr(erro, "tipo", None)
            or type(erro).__name__)
    mensagem = (getattr(erro, "message", None) or getattr(erro, "mensagem", None)
                or _str(erro))
    _por("excecao", {"tipo": _str(tipo), "mensagem": _str(mensagem),
                     "detalhe": _str(detalhe)})
    return erro


def status(rotulo, estado="rodando", aberto=True):
    """Uma caixa com estado, que se escreve por dentro.

        passo := V.status("Consultando o banco…")
        passo.texto("1.200 linhas")
        passo.concluir("Pronto")

    `estado` é `rodando`, `pronto` ou `falhou` — e o desenho muda, para
    que a diferença entre "ainda rodando" e "deu erro" não dependa de
    alguém ler o texto.
    """
    from .layout import Area
    ctx = _ctx()
    chave = ctx.chave_para("status", rotulo)
    no = ctx.por(No("status", {"rotulo": _str(rotulo), "estado": _str(estado),
                               "aberto": bool(aberto), "chave": chave},
                    chave=chave))
    return _Status(no)


class _Status:
    """A área de um `V.status`, com os três desfechos."""

    __slots__ = ("_area",)

    def __init__(self, no):
        from .layout import Area
        self._area = Area(no)

    def __getattr__(self, nome):
        return getattr(self._area, nome)

    def __repr__(self):
        return f"<status {self._area._no.props.get('estado')}>"

    def atualizar(self, rotulo="", estado=""):
        if rotulo:
            self._area._no.props["rotulo"] = _str(rotulo)
        if estado:
            self._area._no.props["estado"] = _str(estado)
        return self

    def concluir(self, rotulo=""):
        return self.atualizar(rotulo, "pronto")

    def falhar(self, rotulo=""):
        return self.atualizar(rotulo, "falhou")


# ═══════════════════════════════════════════════════════════
#  Conversa
# ═══════════════════════════════════════════════════════════

def chat(altura=None):
    """A área de uma conversa. As mensagens entram nela."""
    from .layout import Area
    no = _ctx().por(No("chat", {"altura": altura}))
    return Area(no)


def chat_mensagem(quem="assistente", conteudo="", avatar="", hora=""):
    """Uma bolha de conversa. Devolve a área, para escrever dentro dela.

        bolha := V.chat_mensagem("assistente")
        bolha.markdown(resposta)
        bolha.grafico_linha(serie)

    `quem` é `usuario`, `assistente` ou `sistema` — e é o que decide de
    que lado a bolha fica.
    """
    from .layout import Area
    papel = _str(quem).lower()
    if papel not in ("usuario", "assistente", "sistema"):
        papel = "assistente"
    no = _ctx().por(No("chat_mensagem", {
        "quem": papel, "avatar": _str(avatar), "hora": _str(hora)}))
    area = Area(no)
    if conteudo:
        area.markdown(_str(conteudo))
    return area


def chat_entrada(dica="Escreva uma mensagem…", chave=None, desabilitado=False):
    """A caixa de escrever, fixa embaixo. Devolve o texto enviado, ou `void`.

    Devolver `void` quando nada foi enviado é o que permite escrever o
    laço da conversa de cima para baixo:

        pergunta := V.chat_entrada()
        given pergunta is not void:
            responder(pergunta)
    """
    ctx = _ctx()
    k = ctx.chave_para("chat_entrada", dica, chave)
    _por("chat_entrada", {"dica": _str(dica), "chave": k,
                          "desabilitado": bool(desabilitado)}, chave=k)
    if ctx.foi_acionado(k):
        texto = _str(ctx.sessao.entrada.get(k, "")).strip()
        # A caixa esvazia sozinha: um texto que continuasse ali seria
        # mandado de novo no próximo clique de qualquer outro botão.
        ctx.sessao.remover(f"__campo__{k}")
        return texto or None
    return None


def historico_de_chat(chave="__chat__"):
    """A lista de mensagens guardada na sessão. Cria vazia na primeira vez."""
    from .estado import Estado
    return Estado().padrao(str(chave), [])


def guardar_no_chat(quem, conteudo, chave="__chat__"):
    """Acrescenta ao histórico e devolve a lista inteira."""
    from .estado import Estado
    estado = Estado()
    lista = list(estado.padrao(str(chave), []))
    lista.append({"quem": _str(quem), "conteudo": _str(conteudo),
                  "em": time.strftime("%H:%M")})
    estado.definir(str(chave), lista)
    return lista
