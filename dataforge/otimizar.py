"""O pipeline de otimização que esta linguagem tem — e o que ele rende.

Onde ele NÃO é
--------------
Uma referência de linguagem compilada descreve o pipeline do LLVM:
inlining, vetorização, análise de alias, otimização de programa inteiro.
Nada disso existe aqui, e escrever uma função chamada `vetorizar` que não
vetoriza seria pior que não ter nenhuma.

O pipeline desta linguagem é `compilador.py`: a árvore vira fechamentos,
uma vez. Este módulo é a camada de **cima** dele — três passes sobre o
HIR, que tiram trabalho antes de o fechamento ser construído:

| Passe | O que faz |
|---|---|
| `dobra-de-constante` | `2 + 3 * 4` vira `14`, na carga e não por volta |
| `ramo-morto` | o ramo cuja condição se **prova** falsa sai da árvore |
| `inalcancavel` | o que vem depois de um `yield`/`halt`/`trigger` sai |

O resultado, medido
-------------------
Esta é a parte que interessa, e ela é **desconfortável**: numa carga
feita dos nós que o inventário do LIR apontou, a diferença é de 1,33×;
em 59 exercícios **reais** do repositório, é de **1,01× — nada**.

E o motivo é instrutivo. O que recua do compilador de fechamentos é
dominado por nós que rodam **uma vez** (declaração, `adopt`, `assert` de
topo). Os que rodam dentro de laço são poucos por volta, e o trabalho da
volta já estava compilado: leitura de nome, conta binária, chamada,
leitura por índice. Otimizar o que sobra é otimizar 3% de 3%.

Por isso os passes ficam **desligados por padrão**. Eles existem para
serem medidos, para `dataforge ir --fase=otimizado` mostrar o que dá para
tirar, e porque a conta honesta é a informação — não a promessa de
velocidade.

Duas regras ao mexer aqui
-------------------------
1. **A prova é a saída.** Um passe errado não levanta erro: ele muda o
   resultado. `tests/test_ssa_e_otimizacao.py` roda exercícios do
   repositório nas duas formas e compara caractere por caractere. É a
   mesma trava do HIR, pelo mesmo motivo.

2. **Nada que possa falhar é dobrado.** `1 / 0` dobrado moveria o erro
   para a **carga**, longe da linha que o causa; `"a" + 1` mudaria a
   mensagem. Diante de qualquer dúvida o passe **não** mexe.
"""

import dataclasses

from . import ast_nodes as ast
from . import hir as _hir
from . import mir as _mir
from . import ssa as _ssa

__all__ = ["PASSES", "otimizar", "relatorio_de", "texto"]


#: nome do passe -> o que ele faz. É esta tabela que a CLI mostra.
PASSES = {
    "dobra-de-constante":
        "'2 + 3 * 4' vira '14' na carga, em vez de uma conta por volta",
    "ramo-morto":
        "o ramo cuja condicao se PROVA falsa sai da arvore, com o corpo",
    "inalcancavel":
        "o que vem depois de um 'yield', 'halt' ou 'trigger' sai do corpo",
}

#: As contas que dobram. Divisão fica **fora**: `1 / 0` dobrado moveria o
#: erro para a carga, e a divisão inteira tem o mesmo problema.
_CONTAS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "%": lambda a, b: a % b,
    "**": lambda a, b: a ** b,
}

_NUMERO = (ast.IntegerLiteral, ast.FloatLiteral)
_LITERAL = (ast.IntegerLiteral, ast.FloatLiteral, ast.StringLiteral)

#: Um expoente grande dobrado trava a carga montando o número.
#: `2 ** 1000000` é literal de um lado e meio milhão de dígitos do outro.
_TETO_DO_EXPOENTE = 64

#: O que ENCERRA o fluxo: o que vem depois, no mesmo bloco, não roda.
_ENCERRAM = (ast.YieldStatement, ast.HaltStatement, ast.SkipStatement,
             ast.TriggerStatement, ast.RespondStatement, ast.RenderStatement,
             ast.RedirectStatement)


class _Contagem(dict):
    def somar(self, passe, quantos=1):
        self[passe] = self.get(passe, 0) + quantos


def otimizar(programa, passes=None):
    """`(árvore otimizada, {passe: quantas vezes})`. A original fica.

    A normalização do HIR roda primeiro, porque os passes olham o núcleo:
    sem ela, `orif` seria um caso a mais em cada um — e é exatamente
    assim que um passe fica certo num caminho e errado no outro.
    """
    escolhidos = set(PASSES if passes is None else passes)
    desconhecidos = escolhidos - set(PASSES)
    if desconhecidos:
        from .errors import RuntimeError_
        raise RuntimeError_(
            f"unknown pass(es): {', '.join(sorted(desconhecidos))}. "
            f"The passes are: {', '.join(sorted(PASSES))}.",
            doc="compilador/otimizacao")

    contagem = _Contagem()
    arvore = _hir.normalizar(programa)

    if "dobra-de-constante" in escolhidos:
        arvore = _dobrar(arvore, contagem)
    if "ramo-morto" in escolhidos:
        arvore = _cortar_ramos(arvore, contagem)
    if "inalcancavel" in escolhidos:
        arvore = _cortar_inalcancavel(arvore, contagem)
    return arvore, dict(contagem)


def relatorio_de(programa, passes=None):
    """Só a contagem — para quem quer saber sem trocar a árvore."""
    return otimizar(programa, passes)[1]


# ── passe 1: dobra de constante ───────────────────────────────

def _dobrar(no, contagem):
    """De baixo para cima: `1 + 2 + 3` dobra nas duas contas."""
    novo = _mapear(no, lambda filho: _dobrar(filho, contagem))
    pronto = _dobra_deste(novo)
    if pronto is not None:
        contagem.somar("dobra-de-constante")
        return pronto
    return novo


def _dobra_deste(no):
    if not isinstance(no, ast.BinaryOp) or no.op not in _CONTAS:
        return None
    if not isinstance(no.left, _LITERAL) or not isinstance(no.right, _LITERAL):
        return None
    esquerda, direita = no.left.value, no.right.value
    # texto com número muda a mensagem de erro; e 'a' * 3 é legítimo mas o
    # resultado pode ser enorme. Só número com número dobra.
    if not isinstance(no.left, _NUMERO) or not isinstance(no.right, _NUMERO):
        return None
    if isinstance(esquerda, bool) or isinstance(direita, bool):
        return None
    if no.op == "**" and (abs(direita) > _TETO_DO_EXPOENTE or
                          not isinstance(direita, int)):
        return None
    try:
        valor = _CONTAS[no.op](esquerda, direita)
    except Exception:
        return None                 # o erro continua acontecendo na linha dele
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return None
    classe = ast.IntegerLiteral if isinstance(valor, int) else ast.FloatLiteral
    return classe(line=no.line, column=no.column, value=valor)


# ── passe 2: ramo morto ───────────────────────────────────────

def _cortar_ramos(raiz, contagem):
    """Tira o ramo cuja condição a propagação condicional prova falsa.

    A prova vem do SSA, e não de olhar o literal: `limite := 5` seguido
    de `given limite bigger 10` é provável, e é a forma que aparece em
    código de verdade — número mágico virando constante nomeada.
    """
    provas = _provas_por_corpo(raiz)
    if not provas:
        return raiz

    def andar(no):
        novo = _mapear(no, andar)
        if isinstance(novo, ast.GivenBlock) and novo.condition is not None:
            decidido = provas.get(id(no.condition))
            if decidido is True:
                contagem.somar("ramo-morto")
                return _um_so(novo.body, novo)
            if decidido is False:
                contagem.somar("ramo-morto")
                return _um_so(novo.otherwise_body, novo)
        return novo

    return andar(raiz)


def _um_so(corpo, original):
    """O ramo que sobra, no lugar do `given`.

    Um `given` que vira um bloco de instruções não pode virar uma lista
    solta: o corpo de quem o continha espera uma instrução. Um `given`
    com condição sempre verdadeira serve de casca.
    """
    if not corpo:
        return ast.GivenBlock(line=original.line, column=original.column,
                              condition=ast.BooleanLiteral(
                                  line=original.line, column=original.column,
                                  value=False),
                              body=[], orif_blocks=[], otherwise_body=[])
    return ast.GivenBlock(line=original.line, column=original.column,
                          condition=ast.BooleanLiteral(
                              line=original.line, column=original.column,
                              value=True),
                          body=list(corpo), orif_blocks=[], otherwise_body=[])


def _provas_por_corpo(raiz):
    """`{id do nó da condição: True | False}` — só o que se prova."""
    provas = {}
    for corpo in _mir.construir(raiz, normalizar=False):
        try:
            forma = _ssa.construir(corpo)
            _fixas, mortos = _ssa.constantes_condicionais(forma)
        except Exception:
            continue
        if not mortos:
            continue
        for bloco in forma.blocos:
            if bloco.terminador != "ramo" or not bloco.instrucoes:
                continue
            condicao = bloco.instrucoes[-1]
            vivos = {d for d, _r in bloco.saidas if d not in mortos}
            morre = {r for d, r in bloco.saidas if d in mortos}
            if len(morre) != 1 or not vivos:
                continue
            # 'sim' morto => a condição é falsa; 'nao' morto => verdadeira
            rotulo = next(iter(morre))
            if rotulo == "sim":
                provas[id(condicao.no)] = False
            elif rotulo == "nao":
                provas[id(condicao.no)] = True
    return provas


# ── passe 3: inalcançável ─────────────────────────────────────

def _cortar_inalcancavel(no, contagem):
    """Tira o que vem depois de uma instrução que encerra o fluxo."""
    def andar(alvo):
        novo = _mapear(alvo, andar)
        for campo in dataclasses.fields(novo) if isinstance(
                novo, ast.ASTNode) else ():
            valor = getattr(novo, campo.name)
            if not isinstance(valor, list) or not valor:
                continue
            if not all(isinstance(i, ast.ASTNode) for i in valor):
                continue
            corte = _onde_encerra(valor)
            if corte is not None and corte + 1 < len(valor):
                contagem.somar("inalcancavel", len(valor) - corte - 1)
                setattr(novo, campo.name, valor[:corte + 1])
        return novo
    return andar(no)


def _onde_encerra(instrucoes):
    for indice, instrucao in enumerate(instrucoes):
        if isinstance(instrucao, _ENCERRAM):
            return indice
    return None


# ── a travessia ───────────────────────────────────────────────

def _mapear(no, f):
    """Um nó novo, com `f` aplicada em cada filho. O original não muda."""
    if not isinstance(no, ast.ASTNode) or isinstance(no, ast.ValorPronto):
        return no
    trocas = {}
    for campo in dataclasses.fields(no):
        antes = getattr(no, campo.name)
        depois = _mapear_valor(antes, f)
        if depois is not antes:
            trocas[campo.name] = depois
    campos = {c.name: trocas.get(c.name, getattr(no, c.name))
              for c in dataclasses.fields(no)}
    return no.__class__(**campos)


def _mapear_valor(valor, f):
    if isinstance(valor, ast.ASTNode):
        return f(valor)
    if isinstance(valor, list):
        return [_mapear_valor(i, f) for i in valor]
    if isinstance(valor, tuple):
        return tuple(_mapear_valor(i, f) for i in valor)
    if isinstance(valor, dict):
        return {k: _mapear_valor(v, f) for k, v in valor.items()}
    return valor


# ── o desenho ─────────────────────────────────────────────────

def texto(programa, passes=None):
    """O relatório escrito, com o que cada passe rendeu."""
    from . import lir as _lir

    antes = _lir.inventario(programa)
    arvore, contagem = otimizar(programa, passes)
    depois = _lir.inventario(arvore)

    linhas = ["  passe                   vezes   o que faz"]
    for nome in sorted(PASSES):
        linhas.append(f"   {nome:<22} {contagem.get(nome, 0):>5}   "
                      f"{PASSES[nome]}")
    linhas.append("")
    linhas.append(f"  nos antes: {antes.total}   depois: {depois.total}   "
                  f"({antes.total - depois.total} a menos)")
    linhas.append(f"  compilado: {antes.proporcao():.0f}% → "
                  f"{depois.proporcao():.0f}%")
    linhas.append("")
    linhas.append("  MEDIDO: numa carga feita dos nos que o inventario aponta,")
    linhas.append("  1,33x. Em 59 exercicios reais do repositorio, 1,01x — o")
    linhas.append("  trabalho da volta ja estava compilado. Os passes ficam")
    linhas.append("  desligados por padrao, e o numero e a informacao.")
    return "\n".join(linhas)
