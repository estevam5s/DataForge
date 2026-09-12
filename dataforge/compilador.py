"""Compilação para closures — a árvore vira funções, uma vez.

O problema
----------
Um interpretador de árvore paga, em CADA passagem por um nó, o que só
precisaria pagar uma vez: descobrir de que tipo o nó é, achar o método
que o trata, e ler os campos dele. Num `fib(24)` são 318 mil idas ao
`evaluate` para 35 mil chamadas da linguagem — e o perfil mostra o custo
espalhado pelo despacho, sem gargalo único para atacar.

A ideia
-------
Percorrer a árvore **uma vez** e produzir, para cada nó, um fechamento
Python que faz o que aquele nó faz. Executar passa a ser chamar
fechamentos: sem tabela, sem `isinstance`, sem `node.campo`.

Medido antes de escrever uma linha — um protótipo à mão, preservando a
semântica inteira (escopo encadeado, quadro na pilha, guarda de
profundidade, `yield` como sinal), roda o mesmo `fib` **6,5× mais
rápido**. É o mesmo teto de uma VM de bytecode escrita em Python, por
uma fração do risco.

Por que o risco é menor que o de uma VM
---------------------------------------
Cada construtor aqui espelha **um** método `eval_`/`exec_` do
interpretador, e delega aos mesmos auxiliares (`_operar`, `_comparar`,
`_call`) — a semântica não é reimplementada, é reusada. E o que este
módulo não conhece **recua** para `interp.evaluate`/`interp.execute`,
que é o comportamento de hoje, byte por byte. Um nó novo na linguagem
continua funcionando sem tocar aqui; só não fica mais rápido.
"""

from . import ast_nodes as ast
from .errors import (ControlSignal, DataForgeError, HaltSignal, SkipSignal,
                     TypeError_, YieldSignal)


# ── Expressões ───────────────────────────────────────────────

def _constante(interp, no):
    valor = no.value
    return lambda env: valor


def _void(interp, no):
    return lambda env: None


def _identificador(interp, no):
    """`x` — o caso mais comum da linguagem inteira.

    `root` tem tratamento próprio em `eval_Identifier` e é raro; ele
    recua. O caminho do nome comum é uma leitura no escopo, e o `except`
    só existe para a mensagem: um nome que não existe pode ainda ser um
    TIPO de erro (`KeyError` como valor), e a posição vem do nó.
    """
    if no.name == "root":
        avaliar = interp.eval_Identifier
        return lambda env: avaliar(no, env)

    nome = no.name
    avaliar = interp.eval_Identifier

    def ler(env):
        try:
            return env.get(nome)
        except Exception:
            # Deixa o caminho completo montar a mensagem e procurar o
            # tipo de erro. Acontece uma vez, no erro; nunca no sucesso.
            return avaliar(no, env)
    return ler


def _binario(interp, no):
    esquerda = compilar_expressao(interp, no.left)
    direita = compilar_expressao(interp, no.right)
    op = no.op
    operar = interp._operar
    return lambda env: operar(esquerda(env), op, direita(env), no, env)


def _comparacao(interp, no):
    esquerda = compilar_expressao(interp, no.left)
    direita = compilar_expressao(interp, no.right)
    op = no.op
    comparar = interp._comparar
    return lambda env: comparar(esquerda(env), op, direita(env), no, env)


def _logico(interp, no):
    """`and` e `or` continuam curto-circuitando, e devolvendo o VALOR.

    `a and b` não devolve `yes`/`no`: devolve `a` quando `a` é falso e
    `b` caso contrário, como em Python. Trocar isso por um `bool`
    quebraria `nome := entrada or "sem nome"`.
    """
    esquerda = compilar_expressao(interp, no.left)
    direita = compilar_expressao(interp, no.right)
    if no.op == "and":
        def avaliar(env):
            valor = esquerda(env)
            return direita(env) if valor else valor
    elif no.op == "or":
        def avaliar(env):
            valor = esquerda(env)
            return valor if valor else direita(env)
    else:
        return None
    return avaliar


def _nao(interp, no):
    operando = compilar_expressao(interp, no.operand)
    verdade = interp._verdade
    return lambda env: not verdade(operando(env), no)


def _lista(interp, no):
    """`[a, b, c]` — sem espalhamento, que tem regra própria."""
    if any(isinstance(e, ast.SpreadElement) for e in no.elements):
        return None
    itens = [compilar_expressao(interp, e) for e in no.elements]
    return lambda env: [item(env) for item in itens]


def _vault(interp, no):
    """`{"a": 1}` — sem espalhamento."""
    if any(isinstance(k, ast.SpreadElement) for k, _ in no.pairs):
        return None
    pares = [(compilar_expressao(interp, k), compilar_expressao(interp, v))
             for k, v in no.pairs]
    return lambda env: {k(env): v(env) for k, v in pares}


def _indice(interp, no):
    """`xs[i]` e `v["k"]` — o segundo nó mais comum da linguagem."""
    objeto = compilar_expressao(interp, no.object)
    indice = compilar_expressao(interp, no.index)
    # Método mágico, '__missing__' e a mensagem de chave ausente
    # continuam onde estavam: só os dois valores chegam prontos.
    ler = interp._ler_indice
    return lambda env: ler(objeto(env), indice(env), no, env)


def _texto_interpolado(interp, no):
    """`$"ola {nome}"` — texto e expressão já separados na compilação."""
    formatar = interp._formatar
    para_texto = interp._to_str

    pedacos = []
    for tipo, conteudo in no.parts:
        if tipo == "text":
            pedacos.append(("t", conteudo))
        elif tipo == "fmt":
            expressao, formato = conteudo
            pedacos.append(("f", (compilar_expressao(interp, expressao),
                                  formato)))
        else:
            pedacos.append(("e", compilar_expressao(interp, conteudo)))

    # Texto puro entre chaves e o caso comum; resolver o 'tipo' aqui
    # evita compara-lo a cada montagem da string.
    def montar(env):
        partes = []
        for marca, dado in pedacos:
            if marca == "t":
                partes.append(dado)
            elif marca == "e":
                partes.append(para_texto(dado(env)))
            else:
                fecho, formato = dado
                partes.append(formatar(fecho(env), formato, no))
        return "".join(partes)
    return montar


def _chamada(interp, no):
    """`f(a, b)`.

    Só o caso sem espalhamento e sem argumento nomeado: `f(...xs)` e
    `f(n := 1)` recuam. São raros no caminho quente e o `_eval_args`
    trata os dois com cuidado que não vale duplicar.
    """
    if no.kwargs or any(isinstance(a, ast.SpreadElement) for a in no.args):
        return None

    alvo = compilar_expressao(interp, no.callee)
    argumentos = [compilar_expressao(interp, a) for a in no.args]
    chamar = interp._call

    if not argumentos:
        return lambda env: chamar(alvo(env), [], {}, no, env)
    if len(argumentos) == 1:
        um = argumentos[0]
        return lambda env: chamar(alvo(env), [um(env)], {}, no, env)
    return lambda env: chamar(alvo(env), [a(env) for a in argumentos],
                              {}, no, env)


def _membro(interp, no):
    """`obj.campo` — e, dentro de um método, `self.campo`."""
    objeto = compilar_expressao(interp, no.object)
    ler = interp._ler_membro
    return lambda env: ler(objeto(env), no, env)


def _chamada_de_metodo(interp, no):
    """`obj.metodo(a)` — o mais comum depois da chamada simples.

    Como em `_chamada`: espalhamento e argumento nomeado recuam.
    """
    if no.kwargs or any(isinstance(a, ast.SpreadElement) for a in no.args):
        return None

    objeto = compilar_expressao(interp, no.object)
    argumentos = [compilar_expressao(interp, a) for a in no.args]
    chamar = interp._chamar_metodo

    if not argumentos:
        return lambda env: chamar(objeto(env), [], {}, no, env)
    if len(argumentos) == 1:
        um = argumentos[0]
        return lambda env: chamar(objeto(env), [um(env)], {}, no, env)
    return lambda env: chamar(objeto(env), [a(env) for a in argumentos],
                              {}, no, env)


# ── Instruções ───────────────────────────────────────────────

def _composta_em_nome(interp, no, op):
    """`x += v` num nome simples.

    Le, aplica e escreve — a mesma coisa que '_atribuicao_composta'
    faz para o caso 'Identifier'. As outras formas do alvo (indice,
    membro) recuam: cada uma tem regra propria, inclusive metodo
    magico, e duplica-las e onde a divergencia entraria.
    """
    if not isinstance(no.target, ast.Identifier):
        return None

    nome = no.target.name
    direita = compilar_expressao(interp, no.value)
    operar = interp._operar

    def executar(env):
        novo = operar(env.get(nome), op, direita(env), no, env)
        env.set(nome, novo)
        return novo
    return executar


def _composta_em_membro(interp, no, op):
    """`self.n += 1` — o corpo de quase todo método que acumula."""
    alvo = no.target
    objeto = compilar_expressao(interp, alvo.object)
    direita = compilar_expressao(interp, no.value)
    membro = alvo.member
    operar = interp._operar
    ler = interp._ler_membro
    escrever = interp._escrever_membro

    def executar(env):
        obj = objeto(env)
        novo = operar(ler(obj, alvo, env), op, direita(env), no, env)
        escrever(obj, membro, novo, no, env, alvo)
        return novo
    return executar


def _atribuicao_em_membro(interp, no):
    """`self.x := v`."""
    alvo = no.target
    objeto = compilar_expressao(interp, alvo.object)
    valor = compilar_expressao(interp, no.value)
    membro = alvo.member
    escrever = interp._escrever_membro

    def executar(env):
        escrever(objeto(env), membro, valor(env), no, env, alvo)
    return executar


def _imprimir(interp, no):
    """`out a, b` — a instrução mais escrita da linguagem."""
    partes = [compilar_expressao(interp, e) for e in no.expressions]
    para_texto = interp._to_str

    if len(partes) == 1:
        unica = partes[0]

        def executar(env):
            print(para_texto(unica(env)))
        return executar

    def executar(env):
        print(" ".join(para_texto(p(env)) for p in partes))
    return executar


def _atribuicao(interp, no):
    """`x := v` — só a forma simples, num nome, sem tipo declarado.

    `v["k"] := 1`, `p.x := 1`, `a, b := par` e `x += 1` recuam: cada uma
    tem regras próprias (avaliar o alvo uma vez só, recusar record
    imutável, desestruturar) que não se duplicam sem arriscar divergir.
    """
    op = getattr(no, "compound_op", "")
    if op:
        if isinstance(no.target, ast.MemberAccess):
            return _composta_em_membro(interp, no, op)
        return _composta_em_nome(interp, no, op)
    if getattr(no, "declared_type", ""):
        return None
    if isinstance(no.target, ast.MemberAccess):
        return _atribuicao_em_membro(interp, no)
    if not isinstance(no.target, ast.Identifier):
        return None

    nome = no.target.name
    valor = compilar_expressao(interp, no.value)

    def executar(env):
        env.set(nome, valor(env))
    return executar


def _devolver(interp, no):
    """`yield` — encerra a ação levantando o sinal, como hoje.

    Salvo quando ele é uma chamada de cauda: aí quem decide é
    `exec_YieldStatement`, que confere a identidade da ação antes de
    saltar. Recuar para ele é mais barato que duplicar a conferência —
    e um `yield` marcado é raro, então o recuo quase nunca acontece.
    """
    from .cauda import MARCA

    if getattr(no, MARCA, None) is not None:
        devolver = interp.exec_YieldStatement
        return lambda env: devolver(no, env)

    if no.value is None:
        def executar(env):
            raise YieldSignal(None)
        return executar

    valor = compilar_expressao(interp, no.value)

    def executar(env):
        raise YieldSignal(valor(env))
    return executar


def _condicional(interp, no):
    """`given` / `orif` / `otherwise`.

    Cada ramo ganha o próprio escopo filho, como em `exec_GivenBlock`:
    uma variável declarada dentro do `given` não vaza para fora.
    """
    condicao = compilar_expressao(interp, no.condition)
    corpo = compilar_bloco(interp, no.body)
    verdade = interp._verdade

    ramos = [(compilar_expressao(interp, c), compilar_bloco(interp, b))
             for c, b in no.orif_blocks]
    senao = compilar_bloco(interp, no.otherwise_body) \
        if no.otherwise_body else None

    def executar(env):
        if verdade(condicao(env), no):
            return corpo(env.child("<given>"))
        for cond, ramo in ramos:
            if verdade(cond(env), no):
                return ramo(env.child("<orif>"))
        if senao is not None:
            return senao(env.child("<otherwise>"))
        return None
    return executar


# ── Laços ────────────────────────────────────────────────────
#
# Os três abaixo mudam UMA coisa em relação ao interpretador: o corpo
# vem compilado. Tudo o mais — o escopo reaproveitado, os sinais 'halt'
# e 'skip', a ordem de avaliação — é copiado linha por linha de
# 'exec_CycleFromTo', 'exec_CycleIn' e 'exec_PersistBlock'.
#
# O escopo reaproveitado é a otimização mais delicada do interpretador:
# se o corpo captura o escopo — uma ação, um 'lambda', um 'blueprint',
# um 'thread', um 'defer' — cada volta precisa do seu, senão todas as
# closures veem o último valor. A decisão continua vindo de
# '_escopo_de_laco', que já a memoriza por nó; aqui ela não é
# reimplementada.

def _cycle_de_ate(interp, no):
    inicio = compilar_expressao(interp, no.start)
    fim = compilar_expressao(interp, no.end)
    passo = compilar_expressao(interp, no.step) if no.step else None
    corpo = compilar_bloco(interp, no.body)
    var = no.var
    escopo_de_laco = interp._escopo_de_laco

    def executar(env):
        i = inicio(env)
        limite = fim(env)
        salto = passo(env) if passo is not None else 1

        reusavel = escopo_de_laco(no, env, "<cycle>")
        while (salto > 0 and i <= limite) or (salto < 0 and i >= limite):
            if reusavel is None:
                loop_env = env.child("<cycle>")
            else:
                loop_env = reusavel
                loop_env.limpar()
            loop_env.set_local(var, i)
            try:
                corpo(loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                pass
            i += salto
    return executar


def _cycle_em(interp, no):
    # Importado aqui, e nao no topo: 'interpreter' importa este modulo,
    # e no topo daria ciclo. Acontece uma vez por no de laco, na
    # compilacao — nunca por volta.
    from .interpreter import DFInstance

    fonte = compilar_expressao(interp, no.collection)
    corpo = compilar_bloco(interp, no.body)
    var = no.var
    nomes = getattr(no, "vars", None) or []
    escopo_de_laco = interp._escopo_de_laco
    espalhar = interp._espalhar_no_laco
    percorrer = interp._percorrer
    tipo_de = interp._type_of

    def executar(env):
        colecao = fonte(env)
        if isinstance(colecao, DFInstance):
            colecao = percorrer(colecao, no)
        if not hasattr(colecao, "__iter__"):
            raise TypeError_(
                f"Cannot cycle over {tipo_de(colecao)}: "
                f"expected a Cluster, Vault or String",
                no.line, no.column)

        reusavel = escopo_de_laco(no, env, "<cycle>")
        for item in colecao:
            if reusavel is None:
                loop_env = env.child("<cycle>")
            else:
                loop_env = reusavel
                loop_env.limpar()
            if nomes:
                espalhar(nomes, item, loop_env, no)
            else:
                loop_env.set_local(var, item)
            try:
                corpo(loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                continue
    return executar


def _persist(interp, no):
    condicao = compilar_expressao(interp, no.condition)
    corpo = compilar_bloco(interp, no.body)
    escopo_de_laco = interp._escopo_de_laco
    verdade = interp._verdade

    def executar(env):
        reusavel = escopo_de_laco(no, env, "<persist>")
        while verdade(condicao(env), no):
            if reusavel is None:
                loop_env = env.child("<persist>")
            else:
                loop_env = reusavel
                loop_env.limpar()
            try:
                corpo(loop_env)
            except HaltSignal:
                break
            except SkipSignal:
                continue
    return executar


# ── Montagem ─────────────────────────────────────────────────

_EXPRESSOES = {
    ast.IntegerLiteral: _constante,
    ast.FloatLiteral: _constante,
    ast.StringLiteral: _constante,
    ast.BooleanLiteral: _constante,
    ast.VoidLiteral: _void,
    ast.Identifier: _identificador,
    ast.BinaryOp: _binario,
    ast.ComparisonOp: _comparacao,
    ast.LogicalOp: _logico,
    ast.NotOp: _nao,
    ast.FunctionCall: _chamada,
    ast.MethodCall: _chamada_de_metodo,
    ast.MemberAccess: _membro,
    ast.IndexAccess: _indice,
    ast.ListLiteral: _lista,
    ast.DictLiteral: _vault,
    ast.InterpolatedString: _texto_interpolado,
}

#: Uma expressao SOLTA e instrucao: nao ha no proprio para ela, o nó da
#: expressao aparece direto no corpo. Por isso as duas tabelas se
#: cruzam — 'compilar_instrucao' tenta a de instrucao e, nao achando,
#: a de expressao, exatamente como '_resolver_exec' faz hoje.
_INSTRUCOES = {
    ast.Assignment: _atribuicao,
    ast.YieldStatement: _devolver,
    ast.GivenBlock: _condicional,
    ast.CycleFromTo: _cycle_de_ate,
    ast.CycleIn: _cycle_em,
    ast.PersistBlock: _persist,
    ast.OutStatement: _imprimir,
}


def compilar_expressao(interp, no):
    """Um fechamento `f(env)` equivalente a `interp.evaluate(no, env)`."""
    construtor = _EXPRESSOES.get(no.__class__)
    if construtor is not None:
        pronto = construtor(interp, no)
        if pronto is not None:
            return pronto

    # Recuo: exatamente o interpretador de hoje.
    avaliar = interp.evaluate
    return lambda env: avaliar(no, env)


def compilar_instrucao(interp, no):
    """Um fechamento `f(env)` equivalente a `interp.execute(no, env)`.

    A tradução de exceção do Python para erro da linguagem fica aqui, e
    não em `compilar_expressao`, pelo mesmo motivo que fica em `execute`
    e não em `evaluate`: a instrução é a menor unidade que `monitor`
    delimita, e são muito menos por segundo que expressões.
    """
    classe = no.__class__
    construtor = _INSTRUCOES.get(classe) or _EXPRESSOES.get(classe)
    if construtor is None:
        executar = interp.execute
        return lambda env: executar(no, env)

    pronto = construtor(interp, no)
    if pronto is None:
        executar = interp.execute
        return lambda env: executar(no, env)

    traduzir = interp._traduzir_excecao

    def protegido(env):
        try:
            return pronto(env)
        except (DataForgeError, ControlSignal):
            raise
        except Exception as erro:
            raise traduzir(erro, no) from None
    return protegido


def compilar_bloco(interp, instrucoes):
    """Um fechamento `f(env)` equivalente a `interp.exec_block(...)`."""
    compiladas = [compilar_instrucao(interp, i) for i in instrucoes]

    if len(compiladas) == 1:
        unica = compiladas[0]
        return unica

    def executar(env):
        resultado = None
        for instrucao in compiladas:
            resultado = instrucao(env)
        return resultado
    return executar
