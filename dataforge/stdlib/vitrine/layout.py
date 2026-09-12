"""Layout — colunas, abas, cartões, barra lateral, formulários.

O problema e a escolha
----------------------
Em Python isto seria um `with`:

    with stream.columns(3) as cols:
        with cols[0]:
            stream.metric(…)

A DataForge não tem bloco de contexto, e inventar um só para o layout
seria acrescentar uma palavra reservada à linguagem inteira para
resolver um problema de um módulo.

A saída é o idioma que a linguagem já tem: **a área é um objeto, e os
componentes são métodos dele**.

    colunas := V.colunas(3)
    colunas[0].metrica("Vendas", "R$ 100K")
    colunas[1].metrica("Clientes", "2.500")

Lê-se melhor, aninha sem indentação extra, e a área pode ser guardada
numa variável e passada adiante — o que um `with` não permite.
"""

from . import componentes as C
from . import graficos as G
from .nucleo import Contexto, No


def _ctx():
    return C._ctx()


#: Os componentes que toda área oferece. A lista é a fonte: os métodos
#: de 'Area' saem daqui, e o catálogo da documentação também — assim um
#: componente novo aparece nos dois sem ser escrito duas vezes.
COMPONENTES = {}


def _registrar(modulo, nomes):
    for nome in nomes:
        alvo = nome[:-1] if nome.endswith("_") else nome
        COMPONENTES[alvo] = getattr(modulo, nome)


_registrar(C, [
    "texto", "titulo", "subtitulo", "cabecalho", "markdown", "codigo",
    "html", "divisor", "espaco",
    "botao", "entrada", "area_de_texto", "numero", "deslizante", "caixa",
    "interruptor", "opcao", "escolha", "escolhas", "data", "cor", "arquivo",
    "tabela", "frame", "metrica", "json_", "vault",
    "sucesso", "erro", "aviso", "informacao", "progresso", "carregando",
    "imagem", "audio", "video", "link", "baixar",
])
_registrar(G, [
    "grafico_linha", "grafico_barras", "grafico_area", "grafico_dispersao",
    "grafico_pizza", "histograma", "grafico", "desenhar",
])


class Area:
    """Um pedaço da página em que se pode escrever.

    Uma coluna, uma aba, um cartão, a barra lateral, um formulário — a
    diferença entre eles é só o nó que carregam e como o renderizador o
    desenha. Os métodos são os mesmos, e é por isso que aprender um
    layout ensina todos.
    """

    __slots__ = ("_no",)

    def __init__(self, no):
        self._no = no

    # ── O que faz um componente cair aqui dentro ─────────────

    def _dentro(self, funcao, args, kwargs):
        ctx = _ctx()
        ctx.pilha.append(self._no)
        try:
            return funcao(*args, **kwargs)
        finally:
            # O 'finally' não é zelo excessivo: se o componente
            # disparar, a pilha ficaria apontando para dentro desta
            # área e todo o resto da página entraria nela.
            if ctx.pilha and ctx.pilha[-1] is self._no:
                ctx.pilha.pop()

    def __repr__(self):
        return f"<area {self._no.tipo}>"

    # ── Layouts aninhados ────────────────────────────────────

    def colunas(self, quantidade, larguras=None, espacamento="medio"):
        return self._dentro(colunas, (quantidade, larguras, espacamento), {})

    def abas(self, rotulos):
        return self._dentro(abas, (rotulos,), {})

    def cartao(self, titulo="", subtitulo=""):
        return self._dentro(cartao, (titulo, subtitulo), {})

    def expandir(self, rotulo, aberto=False):
        return self._dentro(expandir, (rotulo, aberto), {})

    def container(self, borda=False, altura=None):
        return self._dentro(container, (borda, altura), {})

    def linha(self, alinhar="inicio", espacamento="medio"):
        return self._dentro(linha, (alinhar, espacamento), {})

    def formulario(self, nome, limpar=False):
        return self._dentro(formulario, (nome, limpar), {})

    def vazio(self):
        return self._dentro(vazio, (), {})


def _metodo_de(funcao):
    def metodo(self, *args, **kwargs):
        return self._dentro(funcao, args, kwargs)
    metodo.__name__ = funcao.__name__
    metodo.__doc__ = funcao.__doc__
    return metodo


for _nome, _funcao in COMPONENTES.items():
    if not hasattr(Area, _nome):
        setattr(Area, _nome, _metodo_de(_funcao))
del _nome, _funcao


class Formulario(Area):
    """Uma área que só entrega os valores quando alguém confirma.

    A diferença importa: sem formulário, **cada tecla** digitada roda o
    programa inteiro. Num campo ligado a uma consulta pesada, isso é a
    diferença entre um app usável e um que trava a cada letra.
    """

    __slots__ = ("_nome", "_limpar")

    def __init__(self, no, nome, limpar=False):
        super().__init__(no)
        self._nome = nome
        self._limpar = limpar

    def enviar(self, rotulo="Enviar", tipo="primario"):
        """O botão que confirma. Devolve `yes` no ciclo do envio."""
        ctx = _ctx()
        chave = f"__form__{self._nome}"
        self._no.acrescentar(No("enviar", {
            "rotulo": C._str(rotulo), "variante": tipo, "chave": chave,
        }, chave=chave))
        enviado = ctx.foi_acionado(chave)
        if enviado and self._limpar:
            # Limpa DEPOIS de a página ser montada; limpar agora
            # apagaria os valores antes de quem escreveu o formulário
            # poder lê-los.
            ctx.limpar_depois.append(self._no)
        return enviado


# ═══════════════════════════════════════════════════════════
#  Os layouts
# ═══════════════════════════════════════════════════════════

def colunas(quantidade, larguras=None, espacamento="medio"):
    """Divide em colunas. Devolve um cluster de áreas.

    `quantidade` pode ser um número (colunas iguais) ou um cluster de
    pesos — `V.colunas([2, 1])` dá uma coluna com o dobro da outra.
    """
    ctx = _ctx()
    if isinstance(quantidade, (list, tuple)):
        pesos = [float(p) for p in quantidade]
    else:
        n = max(1, int(quantidade))
        pesos = [float(p) for p in (larguras or [1] * n)][:n]
        while len(pesos) < n:
            pesos.append(1.0)

    total = sum(pesos) or 1.0
    raiz = ctx.por(No("colunas", {"espacamento": espacamento}))
    areas = []
    for peso in pesos:
        filho = raiz.acrescentar(
            No("coluna", {"proporcao": round(peso / total * 100, 4)}))
        areas.append(Area(filho))
    return areas


def container(borda=False, altura=None):
    no = _ctx().por(No("container", {"borda": bool(borda), "altura": altura}))
    return Area(no)


def linha(alinhar="inicio", espacamento="medio"):
    """Um container horizontal — os filhos ficam lado a lado."""
    no = _ctx().por(No("linha", {"alinhar": alinhar,
                                 "espacamento": espacamento}))
    return Area(no)


def cartao(titulo="", subtitulo=""):
    no = _ctx().por(No("cartao", {"titulo": C._str(titulo),
                                  "subtitulo": C._str(subtitulo)}))
    return Area(no)


def expandir(rotulo, aberto=False):
    """Uma seção que abre e fecha. O estado sobrevive à execução."""
    ctx = _ctx()
    chave = ctx.chave_para("expandir", rotulo)
    estado = ctx.valor_de(chave, bool(aberto))
    ctx.guardar_valor(chave, estado)
    no = ctx.por(No("expandir", {"rotulo": C._str(rotulo),
                                 "aberto": bool(estado), "chave": chave},
                    chave=chave))
    return Area(no)


def abas(rotulos):
    """Abas. Devolve um cluster de áreas, uma por rótulo.

    Todas as abas são **montadas**, e só a escolhida aparece. É uma
    decisão consciente: montar só a visível deixaria o programa com um
    caminho diferente por aba, e um erro escondido atrás de um clique.
    """
    ctx = _ctx()
    nomes = [C._str(r) for r in (rotulos or [])] or ["Aba"]
    chave = ctx.chave_para("abas", "|".join(nomes))
    ativa = ctx.valor_de(chave, nomes[0])
    if ativa not in nomes:
        ativa = nomes[0]
    ctx.guardar_valor(chave, ativa)
    raiz = ctx.por(No("abas", {"rotulos": nomes, "ativa": ativa,
                               "chave": chave}, chave=chave))
    return [Area(raiz.acrescentar(No("aba", {"rotulo": nome,
                                             "visivel": nome == ativa})))
            for nome in nomes]


def formulario(nome, limpar=False):
    """Agrupa campos que só valem quando o botão de envio é apertado."""
    no = _ctx().por(No("formulario", {"nome": C._str(nome),
                                      "chave": f"__form__{nome}"}))
    return Formulario(no, C._str(nome), limpar)


def vazio():
    """Um espaço reservado para ser preenchido depois.

    Serve para escrever "Calculando…" e substituir pelo resultado sem
    que a página salte — o espaço já estava lá.
    """
    return Area(_ctx().por(No("vazio")))


def lateral():
    """A barra lateral. Sempre a mesma, chamada de onde for."""
    return Area(_ctx().barra_lateral)


def espacador():
    """Empurra o que vem depois para a outra ponta de uma `linha`."""
    _ctx().por(No("espacador"))
