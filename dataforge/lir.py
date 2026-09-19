"""LIR — o que o compilador de fechamentos realmente compilou.

Uma referência de linguagem compilada chama esta fase de *lowering*: a
representação do meio desce para operações primitivas, convenção de
chamada e ABI, e o backend gera código de máquina. **O DataForge não
gera código de máquina** — e escrever um LIR que finge isso seria mentir
sobre a linguagem.

O que ele tem de verdade é um backend: `compilador.py` percorre a árvore
uma vez e devolve, para cada nó, um fechamento Python que faz o que
aquele nó faz. É a descida que existe aqui, e ela tem a propriedade que
importa: **é parcial**. O que não está nas tabelas `_EXPRESSOES` e
`_INSTRUCOES` **recua** para o interpretador de árvore, e continua
correto — só não fica mais rápido.

E essa informação não existia em lugar nenhum. Perguntas como "o meu laço
quente compilou?" ou "qual nó está me custando o despacho?" só podiam ser
respondidas lendo `compilador.py` e comparando com a árvore à mão.
`inventario(arvore)` responde:

* quantos nós compilaram e quantos recuaram;
* por classe de nó, quais;
* e os **quentes**: os que recuaram estando dentro de um laço, que são os
  únicos em que a diferença aparece num perfil.

A conta sai das tabelas do próprio compilador, e não de uma lista à parte
— há teste cobrando isso. Uma segunda lista divergiria no primeiro nó
novo, e o relatório passaria a mentir com confiança.
"""

import dataclasses
from dataclasses import dataclass, field

from . import ast_nodes as ast

__all__ = ["Inventario", "inventario", "texto", "classes_compilaveis"]


#: O que roda o corpo mais de uma vez. A COMPREENSAO e o PIPELINE contam:
#: o corpo deles roda uma vez por item, e a primeira versao desta lista
#: olhava so as palavras de laco — o que escondia o recuo que mais custa.
_LACOS = (ast.CycleIn, ast.CycleFromTo, ast.PersistBlock, ast.PerformBlock,
          ast.ListComprehension, ast.VaultComprehension, ast.PipelineExpression)

#: Nós que o compilador nunca vê como instrução nem como expressão: eles
#: são o CORPO de outra coisa (um `handle`, um `point`, um parâmetro), e
#: contá-los como "recuo" inflaria o denominador com o que não é código.
_NAO_CONTA = (ast.HandleClause, ast.MatchCase, ast.Pattern,
              ast.ComprehensionClause, ast.ValorPronto)


@dataclass
class Inventario:
    compiladas: int = 0
    recuadas: int = 0
    #: {classe: {'compiladas': n, 'recuadas': n}}
    por_no: dict = field(default_factory=dict)
    #: [(classe, linha)] — recuou DENTRO de um laço
    quentes: list = field(default_factory=list)

    @property
    def total(self):
        return self.compiladas + self.recuadas

    def proporcao(self):
        """Quanto por cento dos nós viraram fechamento."""
        return 100.0 * self.compiladas / self.total if self.total else 0.0


def _tabelas():
    from . import compilador
    return compilador._EXPRESSOES, compilador._INSTRUCOES


def classes_compilaveis():
    """Os nomes de classe que as tabelas do compilador conhecem."""
    expressoes, instrucoes = _tabelas()
    return {classe.__name__ for classe in set(expressoes) | set(instrucoes)}


def _interprete():
    from .interpreter import Interpreter
    return Interpreter()


def _compila(interp, no, expressoes, instrucoes):
    """O compilador construiria um fechamento para este nó?

    A pergunta é respondida **chamando o construtor**, e não olhando a
    tabela: metade deles devolve `None` nos casos difíceis (`f(...xs)`,
    `v["k"] += 1`), e é assim que o recuo acontece sem duplicar regra.
    Perguntar só à tabela contaria esses como compilados.
    """
    construtor = instrucoes.get(no.__class__) or expressoes.get(no.__class__)
    if construtor is None:
        return False
    try:
        return construtor(interp, no) is not None
    except Exception:
        return False


def inventario(programa):
    """Quanto da árvore desce para fechamento, e o que fica na árvore."""
    expressoes, instrucoes = _tabelas()
    interp = _interprete()
    inv = Inventario()

    def contar(no, em_laco):
        classe = no.__class__.__name__
        registro = inv.por_no.setdefault(classe, {"compiladas": 0,
                                                  "recuadas": 0})
        if _compila(interp, no, expressoes, instrucoes):
            inv.compiladas += 1
            registro["compiladas"] += 1
        else:
            inv.recuadas += 1
            registro["recuadas"] += 1
            if em_laco:
                inv.quentes.append((classe, getattr(no, "line", 0)))

    def andar(valor, em_laco):
        if isinstance(valor, ast.ASTNode):
            if isinstance(valor, _NAO_CONTA):
                if isinstance(valor, ast.ValorPronto):
                    return
            else:
                contar(valor, em_laco)
            # A COMPREENSAO e um laco, e esquecer isso escondia o maior
            # recuo de todos: o corpo dela roda uma vez por item, e a
            # primeira versao desta conta olhava so as palavras de laco.
            dentro = em_laco or isinstance(valor, _LACOS)
            for campo in dataclasses.fields(valor):
                andar(getattr(valor, campo.name), dentro)
        elif isinstance(valor, (list, tuple)):
            for item in valor:
                andar(item, em_laco)
        elif isinstance(valor, dict):
            for item in valor.values():
                andar(item, em_laco)

    for instrucao in getattr(programa, "body", []) or []:
        andar(instrucao, False)
    return inv


def texto(inv):
    """O inventário escrito, do que mais recuou para o que menos."""
    linhas = [f"  {inv.compiladas} de {inv.total} nos viraram fechamento "
              f"({inv.proporcao():.0f}%)",
              f"  {inv.recuadas} recuaram para o interpretador de arvore",
              ""]
    if inv.por_no:
        piores = sorted(inv.por_no.items(),
                        key=lambda par: (-par[1]["recuadas"], par[0]))
        linhas.append("  no                          compila   recua")
        for classe, contas in piores[:20]:
            linhas.append(f"   {classe:<26} {contas['compiladas']:>7}"
                          f" {contas['recuadas']:>7}")
        linhas.append("")
    if inv.quentes:
        linhas.append(f"  {len(inv.quentes)} recuo(s) DENTRO de laco — e onde "
                      f"a diferenca aparece num perfil:")
        vistos = {}
        for classe, linha in inv.quentes:
            vistos.setdefault(classe, []).append(linha)
        for classe, ondes in sorted(vistos.items()):
            amostra = ", ".join(str(x) for x in sorted(set(ondes))[:6])
            linhas.append(f"   {classe} — linha(s) {amostra}")
        linhas.append("")
    linhas.append("  o backend e compilador.py; nao ha codigo de maquina, e")
    linhas.append("  'dataforge ir --fase=lir' e onde isso fica visivel.")
    return "\n".join(linhas)
