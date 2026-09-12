"""Chamada de cauda — quando `yield f(…)` é um salto, não uma chamada.

O problema
----------
`MAX_CALL_DEPTH` é mil. Qualquer travessia de árvore ou grafo sobre dado
real bate nisso, e o programa morre com `StackOverflowError` — não
porque há recursão infinita, mas porque a linguagem contava quadros que
não precisava ter empilhado.

A observação
------------
Em DataForge, `yield` **devolve e encerra**. Então numa ação assim:

    action somar_ate(n, acumulado):
        given n is 0:
            yield acumulado
        yield somar_ate(n - 1, acumulado + n)

o último `yield` não tem nada depois dele. O quadro atual existe só para
repassar o resultado de volta — e repassar um resultado não precisa de
quadro. Reaproveitá-lo transforma a recursão num laço, e o limite
desaparece.

Isso é o que qualquer linguagem funcional faz, e é possível aqui
justamente porque `yield` já é `return`: não há "e depois" implícito.

Quando NÃO vale
---------------
Três casos, e os três são recusados por análise, antes de rodar:

1. **`defer` na ação.** O bloco adiado roda na saída do quadro. Reusar o
    quadro mudaria quando ele roda, e `defer` existe exatamente para
    garantir *quando*.

2. **Dentro de `monitor`.** Um `handle` acima pode querer capturar o que
    vier da chamada. Saltar em vez de chamar tiraria a chamada de dentro
    do `monitor`, e o `handle` deixaria de ver o que via.

3. **Recursão indireta.** `f` chama `g` que chama `f` continua
    empilhando. Detectar isso exigiria olhar o programa inteiro, e a
    análise aqui olha uma ação de cada vez — o caso direto é a
    esmagadora maioria, e uma análise que às vezes acerta seria pior que
    uma que sempre diz a mesma coisa.

O preço, e ele é real
---------------------
Uma ação que salta não aparece repetida no stack trace: são mil saltos e
um quadro só. É o mesmo preço que toda linguagem com esta otimização
paga, e ele está documentado na página de ações.

E recursão de cauda infinita vira **laço** infinito: não há mais
`StackOverflowError` para interrompê-la, do mesmo jeito que não há para
`persist yes:`. Um laço é um laço.
"""

from . import ast_nodes as ast

#: O campo que marca um 'yield' elegível, posto no próprio nó.
#:
#: Fica no nó, e não numa tabela ao lado, porque é onde
#: 'exec_YieldStatement' vai perguntar — e ele passa por ali milhões de
#: vezes num programa de porte médio. Um 'getattr' com padrão é a
#: pergunta mais barata que existe.
MARCA = "_cauda_de"


def _sem_surpresa(chamada):
    """Sem argumento nomeado e sem espalhamento.

    Os dois passam pelo `_eval_args`, que tem regras próprias; duplicá-las
    aqui é onde a divergência entraria. São raros em recursão.
    """
    return (not chamada.kwargs
            and not any(isinstance(a, ast.SpreadElement)
                        for a in chamada.args))


def _chamada_a_si_mesma(valor, nome):
    """`yield f(a, b)` — ou `yield self.f(a, b)` — onde `f` é esta ação.

    A forma com `self.` importa: um método recursivo é escrito assim, e
    deixá-lo de fora faria a otimização valer para ação solta e não para
    método, sem nada que explicasse a diferença.
    """
    if isinstance(valor, ast.FunctionCall):
        return (isinstance(valor.callee, ast.Identifier)
                and valor.callee.name == nome
                and _sem_surpresa(valor))

    if isinstance(valor, ast.MethodCall):
        return (isinstance(valor.object, ast.Identifier)
                and valor.object.name in ("self", "this")
                and valor.method == nome
                and _sem_surpresa(valor))

    return False


#: Onde um `yield` pertence a OUTRA ação, e não a esta.
#:
#: Uma ação declarada dentro de outra tem os próprios `yield`, e eles
#: encerram ELA. Descer aqui marcaria o `yield` do filho como salto do
#: pai — o salto reusaria o quadro errado, e o erro apareceria longe
#: da causa.
_OUTRO_DONO = (ast.ActionDeclaration, ast.LambdaExpression,
               ast.BlueprintDeclaration, ast.RecordDeclaration)


def _percorrer(no, nome, bloqueado, achados, todos):
    """Varre em busca de `yield` elegível, sabendo onde não vale.

    `todos` recolhe **todo** `yield` desta ação, e não só os elegíveis.
    A diferença entre as duas contas é o que prova que a ação não
    termina — ver `analisar`.
    """
    if isinstance(no, ast.YieldStatement):
        todos.append(no)
        if not bloqueado and _chamada_a_si_mesma(no.value, nome):
            try:
                setattr(no, MARCA, nome)
            except AttributeError:
                return                      # nó sem espaço para a marca
            achados.append(no)
        return

    if isinstance(no, _OUTRO_DONO):
        return

    if isinstance(no, (ast.MonitorBlock, ast.DeferStatement)):
        # Dentro destes, nenhum 'yield' salta — mas segue-se varrendo,
        # porque um 'defer' aninhado ainda bloqueia o resto da ação.
        bloqueado = True

    if isinstance(no, ast.ASTNode):
        for campo, valor in vars(no).items():
            if campo.startswith("_"):
                continue
            _percorrer(valor, nome, bloqueado, achados, todos)
    elif isinstance(no, (list, tuple)):
        for item in no:
            _percorrer(item, nome, bloqueado, achados, todos)
    elif isinstance(no, dict):
        for item in no.values():
            _percorrer(item, nome, bloqueado, achados, todos)


def _tem_defer(no):
    """Um `defer` em qualquer lugar da ação desliga o salto.

    Ele roda na saída do quadro, e o salto reusa o quadro. Em vez de
    tentar acertar a ordem, recusa-se: `defer` existe para garantir
    *quando*, e uma garantia com exceção não é garantia.
    """
    if isinstance(no, ast.DeferStatement):
        return True
    if isinstance(no, ast.ASTNode):
        return any(_tem_defer(v) for c, v in vars(no).items()
                   if not c.startswith("_"))
    if isinstance(no, (list, tuple)):
        return any(_tem_defer(i) for i in no)
    if isinstance(no, dict):
        return any(_tem_defer(i) for i in no.values())
    return False


def analisar(acao) -> bool:
    """Marca os `yield` que podem saltar. Devolve se achou algum.

    Roda uma vez por ação, na primeira chamada — percorrer a árvore a
    cada chamada custaria muito mais do que a recursão que se quer
    evitar.
    """
    nome = acao.name
    if not nome or acao.is_generator:
        return False

    corpo = acao.body
    if _tem_defer(corpo):
        return False

    achados, todos = [], []
    _percorrer(corpo, nome, False, achados, todos)
    if not achados:
        return False

    # ── A ação que NUNCA devolve não ganha o salto ──
    #
    # Se todo 'yield' dela é uma chamada a si mesma, não existe caminho
    # que produza um valor: ela é infinita por construção. Com o salto,
    # isso deixaria de ser 'StackOverflowError' e viraria um laço mudo —
    # e trocar uma mensagem clara por um travamento é uma piora, não uma
    # otimização.
    #
    # Recusar o salto é sempre seguro: a ação volta a empilhar, e o
    # guarda de recursão a interrompe como sempre interrompeu.
    #
    # Isto não pega toda recursão infinita — 'given no: yield 1' é um
    # caminho morto que a análise não sabe que é morto. Essas viram
    # laço, como 'persist yes:' vira, e a documentação diz isso.
    if len(achados) == len(todos):
        for no in achados:
            try:
                delattr(no, MARCA)
            except AttributeError:
                pass
        return False

    return True
