"""Gráficos — linha, barras, área, dispersão, pizza, histograma.

Sem biblioteca
--------------
O gráfico vira **SVG escrito à mão**, no renderizador. Não é
teimosia: uma dependência de JavaScript obrigaria a página a buscar
centenas de kilobytes de uma CDN, o que quebra qualquer aplicação que
rode numa rede fechada — que é exatamente onde dashboard de dados
costuma rodar.

SVG também imprime, escala e é legível por leitor de tela. E o arquivo
que sai daqui é o mesmo que `V.exportar_svg` grava em disco.

Duas formas de pedir
--------------------
A curta, para o caso comum:

    V.grafico_linha(vendas, x := "mes", y := "total")

E a construída, quando há mais a dizer:

    g := V.grafico("barras")
    g.eixo_x("mes")
    g.eixo_y("total")
    g.titulo("Vendas por período")
    g.cores(["#FED403", "#0F62FE"])
    V.desenhar(g)
"""

from .nucleo import Contexto, No

#: A paleta padrão. A primeira é o amarelo da marca; as demais foram
#: escolhidas para continuarem distinguíveis em escala de cinza e para
#: quem não separa vermelho de verde — que é 8% dos homens.
PALETA = ["#FED403", "#0F62FE", "#24A148", "#FA4D56", "#8A3FFC",
          "#FF832B", "#009D9A", "#D12771", "#B28600", "#4589FF"]

#: Os tipos que o renderizador sabe desenhar. Pedir outro é erro na
#: hora da chamada, e não uma página em branco.
#:
#: A lista cresceu, e a regra de entrada continua a mesma: um tipo só
#: entra aqui quando há um desenho para ele em `_SVG`. Um nome nesta
#: tupla sem desenho do outro lado seria um gráfico que some calado —
#: `_svg_linha` assumiria, e a pessoa veria uma linha onde pediu um
#: funil. `tests/test_vitrine.py` confere os dois lados.
TIPOS = ("linha", "barras", "area", "dispersao", "pizza", "histograma",
         "barras_horizontais", "rosca",
         # os que vieram com o painel profissional
         "combo", "radar", "medidor", "funil", "mapa_de_calor", "treemap",
         "cascata", "velas", "caixa", "bolhas", "pareto", "calendario",
         "sankey", "gantt", "barras_100", "bala", "dispersao_xy", "mapa",
         "rede")


def _ctx():
    from .componentes import _ctx as obter
    return obter()


class Grafico:
    """Um gráfico sendo montado. Só vira nó quando `V.desenhar` o recebe."""

    __slots__ = ("tipo", "dados", "props")

    def __init__(self, tipo, dados=None):
        tipo = str(tipo)
        if tipo not in TIPOS:
            from ...errors import RuntimeError_
            raise RuntimeError_(
                f"grafico de tipo '{tipo}' nao existe.", 0, 0,
                nota=f"os tipos sao: {', '.join(TIPOS)}",
                doc="tecnicas/vitrine")
        self.tipo = tipo
        self.dados = dados
        self.props = {"cores": list(PALETA), "legenda": True,
                      "grade": True, "altura": 280, "empilhado": False,
                      "rotulos": False, "suave": False, "dica": True,
                      "formato": "", "legenda_em": "baixo"}

    # Cada método devolve o próprio gráfico, então dá para encadear:
    #   V.grafico("linha").eixo_x("mes").eixo_y("total")
    def com(self, dados):
        self.dados = dados
        return self

    def eixo_x(self, campo, rotulo=""):
        self.props["x"] = str(campo)
        self.props["rotulo_x"] = str(rotulo or campo)
        return self

    def eixo_y(self, campo, rotulo=""):
        campos = campo if isinstance(campo, (list, tuple)) else [campo]
        self.props["y"] = [str(c) for c in campos]
        self.props["rotulo_y"] = str(rotulo or campos[0])
        return self

    def serie(self, campo):
        """Acrescenta uma linha/barra ao mesmo gráfico."""
        self.props.setdefault("y", []).append(str(campo))
        return self

    def titulo(self, texto):
        self.props["titulo"] = str(texto)
        return self

    def cores(self, lista):
        self.props["cores"] = [str(c) for c in lista] or list(PALETA)
        return self

    def altura(self, pixels):
        self.props["altura"] = max(80, int(pixels))
        return self

    def empilhar(self, ligado=True):
        self.props["empilhado"] = bool(ligado)
        return self

    def suavizar(self, ligado=True):
        self.props["suave"] = bool(ligado)
        return self

    def legenda(self, ligada=True):
        self.props["legenda"] = bool(ligada)
        return self

    def grade(self, ligada=True):
        self.props["grade"] = bool(ligada)
        return self

    def rotular(self, ligado=True):
        """Escreve o valor em cima de cada ponto ou barra."""
        self.props["rotulos"] = bool(ligado)
        return self

    def limite_y(self, minimo=None, maximo=None):
        self.props["min_y"] = minimo
        self.props["max_y"] = maximo
        return self

    # ── O que um painel de verdade pede ──────────────────────

    def formato(self, nome, casas=None):
        """Como os números do eixo e das dicas são escritos.

        `moeda`, `numero`, `percentual`, `compacto` — os mesmos nomes
        que a grade usa. Um eixo em reais e uma tabela em reais não
        podem discordar sobre o que é um real.
        """
        self.props["formato"] = str(nome)
        if casas is not None:
            self.props["casas"] = int(casas)
        return self

    def tracejar(self, *nomes):
        """Deixa tracejadas as séries nomeadas — a linha do *planejado*.

        Tracejado, e não outra cor: a comparação entre o realizado e o
        previsto é entre a mesma grandeza, e trocar a cor faria parecer
        que são duas coisas diferentes.
        """
        # Sem nome nenhum, todas: `"*"` diz isso sem precisar conhecer
        # as séries, que só existem depois de o dado ser lido.
        alvos = [str(n) for n in nomes] or ["*"]
        self.props.setdefault("tracejadas", []).extend(alvos)
        return self

    def referencia(self, valor, rotulo="", cor=""):
        """Uma linha horizontal fixa — a meta, o limite, a média."""
        self.props.setdefault("referencias", []).append(
            {"valor": float(valor), "rotulo": str(rotulo), "cor": str(cor)})
        return self

    def anotar(self, categoria, texto, cor=""):
        """Um marcador sobre uma categoria do eixo x."""
        self.props.setdefault("anotacoes", []).append(
            {"categoria": str(categoria), "texto": str(texto), "cor": str(cor)})
        return self

    def faixa_de_meta(self, de, ate, cor=""):
        """Uma faixa sombreada entre dois valores do eixo y."""
        self.props.setdefault("faixas", []).append(
            {"de": float(de), "ate": float(ate), "cor": str(cor)})
        return self

    def como(self, **tipos):
        """O tipo de cada série, num gráfico combinado.

            g.como(receita := "barra", margem := "linha")
        """
        self.props.setdefault("tipos_de_serie", {}).update(
            {str(k): str(v) for k, v in tipos.items()})
        return self

    def eixo_direito(self, *nomes):
        """As séries que usam a escala da direita.

        Sem isso, uma margem de 0 a 100 desenhada ao lado de uma receita
        de milhões vira uma linha colada no zero — o gráfico existe e
        não mostra nada.
        """
        self.props.setdefault("direita", []).extend(str(n) for n in nomes)
        return self

    def empilhar_100(self, ligado=True):
        """Cada categoria soma 100%: a composição, e não o tamanho."""
        self.props["cem_por_cento"] = bool(ligado)
        if ligado:
            self.props["empilhado"] = True
        return self

    def legenda_em(self, onde="baixo"):
        """`baixo`, `direita` ou `nenhuma`."""
        self.props["legenda_em"] = str(onde)
        self.props["legenda"] = str(onde) != "nenhuma"
        return self

    def total_no_centro(self, texto="", rotulo=""):
        """O total no buraco da rosca — o que a imagem de referência faz."""
        self.props["centro"] = {"valor": str(texto), "rotulo": str(rotulo)}
        return self

    def vertical(self, ligado=True):
        """Gira as barras: categoria com nome longo se lê deitada."""
        self.props["deitado"] = bool(ligado)
        return self

    def marcadores(self, ligados=True):
        self.props["marcadores"] = bool(ligados)
        return self

    def dica(self, ligada=True):
        """A caixinha que segue o cursor. Ligada por padrão."""
        self.props["dica"] = bool(ligada)
        return self

    def para_vault(self):
        return {"tipo": self.tipo, "props": dict(self.props)}

    def __repr__(self):
        return f"<grafico {self.tipo}>"


def grafico(tipo="linha", dados=None):
    """Começa a montar um gráfico. Nada aparece até `V.desenhar`."""
    return Grafico(tipo, dados)


def desenhar(g):
    """Põe o gráfico montado na página."""
    if not isinstance(g, Grafico):
        from ...errors import TypeError_
        raise TypeError_(
            "V.desenhar espera um grafico de V.grafico(...).", 0, 0,
            doc="tecnicas/vitrine")
    series, categorias = _extrair(g.dados, g.props)
    ctx = _ctx()
    # A largura é gravada AQUI, e não na hora de desenhar: quando o
    # renderizador roda, a montagem já acabou e a pilha de larguras do
    # contexto não existe mais.
    ctx.por(No("grafico", {**g.props, "grafico": g.tipo,
                           "series": series, "categorias": categorias,
                           "largura_css": ctx.largura}))
    return g


def _atalho(tipo, dados, x, y, titulo, altura, kwargs):
    g = Grafico(tipo, dados)
    if x:
        g.eixo_x(x)
    if y:
        g.eixo_y(y)
    if titulo:
        g.titulo(titulo)
    if altura:
        g.altura(altura)
    for chave, valor in (kwargs or {}).items():
        g.props[chave] = valor
    desenhar(g)
    return dados


def grafico_linha(dados, x="", y="", titulo="", altura=None, **kw):
    return _atalho("linha", dados, x, y, titulo, altura, kw)


def grafico_barras(dados, x="", y="", titulo="", altura=None, **kw):
    return _atalho("barras", dados, x, y, titulo, altura, kw)


def grafico_area(dados, x="", y="", titulo="", altura=None, **kw):
    return _atalho("area", dados, x, y, titulo, altura, kw)


def grafico_dispersao(dados, x="", y="", titulo="", altura=None, **kw):
    return _atalho("dispersao", dados, x, y, titulo, altura, kw)


def grafico_pizza(dados, x="", y="", titulo="", altura=None, **kw):
    return _atalho("pizza", dados, x, y, titulo, altura, kw)


def grafico_rosca(dados, x="", y="", titulo="", altura=None, **kw):
    return _atalho("rosca", dados, x, y, titulo, altura, kw)


def grafico_barras_h(dados, x="", y="", titulo="", altura=None, **kw):
    return _atalho("barras_horizontais", dados, x, y, titulo, altura, kw)


def histograma(dados, campo="", faixas=10, titulo="", altura=None):
    """Distribuição. Conta quantos valores caem em cada faixa."""
    valores = _coluna_numerica(dados, campo)
    faixas = max(1, int(faixas))
    if not valores:
        ctx = _ctx()
        ctx.por(No("grafico", {"grafico": "barras", "series": [],
                               "categorias": [], "titulo": titulo,
                               "cores": list(PALETA), "altura": altura or 280,
                               "grade": True, "legenda": False,
                               "largura_css": ctx.largura}))
        return dados

    menor, maior = min(valores), max(valores)
    largura = (maior - menor) / faixas or 1.0
    contagem = [0] * faixas
    for v in valores:
        # O último valor cairia na faixa faixas+1 sem este min().
        indice = min(faixas - 1, int((v - menor) / largura))
        contagem[indice] += 1

    categorias = [_curto(menor + i * largura) for i in range(faixas)]
    ctx = _ctx()
    ctx.por(No("grafico", {
        "grafico": "barras", "categorias": categorias,
        "series": [{"nome": str(campo or "frequência"), "valores": contagem}],
        "titulo": str(titulo), "cores": list(PALETA), "grade": True,
        "legenda": False, "altura": altura or 280, "rotulos": False,
        "empilhado": False, "suave": False,
        "largura_css": ctx.largura}))
    return dados


# ═══════════════════════════════════════════════════════════
#  Dos dados às séries
# ═══════════════════════════════════════════════════════════

def _extrair(dados, props):
    """Descobre categorias e séries a partir do que veio.

    Aceita as mesmas formas que `V.tabela`, e mais uma: um vault de
    rótulo para número — `{"Sul": 120, "Norte": 90}` — que é a forma em
    que um `group_by` costuma sair e seria absurdo obrigar a converter.
    """
    registros = _registros(dados)
    if not registros:
        return [], []

    campo_x = props.get("x") or ""
    campos_y = list(props.get("y") or [])

    disponiveis = []
    for reg in registros:
        for c in reg:
            if c not in disponiveis:
                disponiveis.append(c)

    if not campo_x:
        # A primeira coluna não numérica é quase sempre o eixo. Quando
        # todas são numéricas, o eixo é a posição da linha.
        campo_x = next((c for c in disponiveis
                        if not _e_numero(registros[0].get(c))), "")
    if not campos_y:
        campos_y = [c for c in disponiveis
                    if c != campo_x and _e_numero(registros[0].get(c))]
    if not campos_y:
        campos_y = [c for c in disponiveis if c != campo_x][:1]

    categorias = ([_texto(r.get(campo_x, "")) for r in registros]
                  if campo_x else [str(i + 1) for i in range(len(registros))])
    series = [{"nome": str(c),
               "valores": [_numero_ou_ausente(r.get(c)) for r in registros]}
              for c in campos_y]
    return series, categorias


def _registros(dados):
    if dados is None:
        return []
    if hasattr(dados, "to_dict") and hasattr(dados, "columns"):
        return list(dados.to_dict())
    if isinstance(dados, dict):
        if dados and all(isinstance(v, list) for v in dados.values()):
            altura = max((len(v) for v in dados.values()), default=0)
            return [{c: (v[i] if i < len(v) else None)
                     for c, v in dados.items()} for i in range(altura)]
        # {"Sul": 120, "Norte": 90}
        return [{"rotulo": k, "valor": v} for k, v in dados.items()]
    if isinstance(dados, (list, tuple)):
        itens = list(dados)
        if not itens:
            return []
        if isinstance(itens[0], dict):
            return itens
        if isinstance(itens[0], (list, tuple)):
            return [{f"col{i + 1}": v for i, v in enumerate(linha)}
                    for linha in itens]
        # Um cluster de números puro.
        return [{"indice": i + 1, "valor": v} for i, v in enumerate(itens)]
    return []


def _coluna_numerica(dados, campo=""):
    registros = _registros(dados)
    if not registros:
        return []
    if not campo:
        campo = next((c for c, v in registros[0].items() if _e_numero(v)),
                     next(iter(registros[0]), ""))
    return [_numero(r.get(campo)) for r in registros
            if _e_numero(r.get(campo))]


def _e_numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _numero_ou_ausente(v):
    """`void` continua `void`. É o que separa um vão de um zero.

    O caminho antigo devolvia `0.0`, e a linha de um acumulado
    despencava ao chegar no mês que ainda não aconteceu — um gráfico
    que mostra uma queda de um milhão onde só falta o dado. Um vão diz
    "não sei"; um zero afirma um número.
    """
    if v is None:
        return None
    if isinstance(v, str) and not v.strip():
        return None
    return _numero(v)


def _numero(v):
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def _texto(v):
    from .componentes import _str
    return _str(v)


def _curto(v):
    if isinstance(v, float) and not v.is_integer():
        return f"{v:.1f}"
    return str(int(v))
