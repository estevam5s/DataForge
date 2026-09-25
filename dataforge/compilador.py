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
from .errors import (ControlSignal, DataForgeError, HaltSignal, IndexError_,
                     RuntimeError_, SkipSignal, TypeError_, YieldSignal)


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
    if isinstance(no.target, ast.IndexAccess):
        return _atribuicao_em_indice(interp, no)
    if not isinstance(no.target, ast.Identifier):
        return None

    nome = no.target.name
    valor = compilar_expressao(interp, no.value)

    # O mesmo sinal que 'exec_Assignment' passa: um literal e um valor
    # NOVO, e so ele pode virar colecao tipada numa reatribuicao
    # ('xs := [2]' num 'xs: Cluster<Integer>'). Decidido aqui, uma vez,
    # pela forma da expressao — o caminho quente nao paga nada.
    from .interpreter import _NASCE_AQUI
    if isinstance(no.value, _NASCE_AQUI):
        def executar(env):
            env.set(nome, valor(env), True)
        return executar

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

    Os ramos rodam no MESMO escopo, como em `exec_GivenBlock` — um nome
    atribuído dentro do `given` existe depois dele, que é como se decide
    um valor em dois caminhos.

    Este construtor espelha `exec_GivenBlock`, e divergir dele faz a
    linguagem responder duas coisas diferentes conforme a compilação de
    fechamentos esteja ligada ou não. Foi o que aconteceu: o
    interpretador passou a compartilhar o escopo e aqui continuou
    criando filho, então o `check` aprovava e a execução falhava.
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
            return corpo(env)
        for cond, ramo in ramos:
            if verdade(cond(env), no):
                return ramo(env)
        if senao is not None:
            return senao(env)
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

def _pipeline(interp, no):
    """`xs >> sift x: … >> morph x: … >> distill a, v: … 0`.

    Espelha `eval_PipelineExpression`, e o custo que ele pagava estava em
    cada ELEMENTO: um escopo filho novo e a expressão reavaliada pela
    árvore. Num `distill` sobre 200 mil itens, 600 mil idas ao `evaluate`
    dentro de um corpo que já estava compilado.

    O escopo por elemento só é reaproveitado quando a expressão não
    captura escopo — um `lambda` criado dentro de um `morph` precisa do
    seu, senão todos veriam o último item. É a mesma regra, e a mesma
    função, que o `cycle` usa.

    A ação nomeada (`morph dobrar`) continua indo por `_call_func`, que
    passa pela chamada normal da linguagem.
    """
    from .environment import Environment

    fonte = compilar_expressao(interp, no.source)
    percorrer = interp._percorrer
    conferir = interp._conferir_fonte_do_pipeline
    chamar = interp._call_func
    captura = interp._corpo_captura_escopo
    etapas = []

    for op in no.operations:
        if isinstance(op, ast.QuadroOperation):
            # Um verbo de quadro RECUA para o interpretador: devolver
            # None aqui e como os casos dificeis ficam de fora sem
            # duplicar regra. O ganho da compilacao esta no custo POR
            # ELEMENTO, e um verbo de quadro e uma chamada so por
            # estagio — nao ha laco para tirar do caminho quente.
            return None
        if isinstance(op, ast.SiftOperation):
            if op.func_ref:
                nome, alvo = op.func_ref, op

                def etapa(dados, env, nome=nome, alvo=alvo):
                    funcao = env.get(nome)
                    return [x for x in dados if chamar(funcao, [x], alvo, env)]
            else:
                corpo = compilar_expressao(interp, op.condition)
                etapa = _por_elemento(op.param, corpo, captura([op.condition]),
                                      "<lambda>", filtrar=True)
        elif isinstance(op, ast.MorphOperation):
            if op.func_ref:
                nome, alvo = op.func_ref, op

                def etapa(dados, env, nome=nome, alvo=alvo):
                    funcao = env.get(nome)
                    return [chamar(funcao, [x], alvo, env) for x in dados]
            else:
                corpo = compilar_expressao(interp, op.expression)
                etapa = _por_elemento(op.param, corpo, captura([op.expression]),
                                      "<lambda>", filtrar=False)
        elif isinstance(op, ast.DistillOperation):
            inicial = (compilar_expressao(interp, op.initial)
                       if op.initial is not None else None)
            if op.func_ref:
                nome, alvo = op.func_ref, op

                def etapa(dados, env, nome=nome, alvo=alvo, inicial=inicial):
                    funcao = env.get(nome)
                    acc = inicial(env) if inicial is not None else dados[0]
                    for x in dados[0 if inicial is not None else 1:]:
                        acc = chamar(funcao, [acc, x], alvo, env)
                    return acc
            else:
                corpo = compilar_expressao(interp, op.expression)
                acumulador, valor = op.acc_param, op.val_param
                reusa = not captura([op.expression])

                def etapa(dados, env, corpo=corpo, acumulador=acumulador,
                          valor=valor, inicial=inicial, reusa=reusa):
                    acc = inicial(env) if inicial is not None else dados[0]
                    local = Environment(parent=env, name="<distill>")
                    for x in dados[0 if inicial is not None else 1:]:
                        if not reusa:
                            local = Environment(parent=env, name="<distill>")
                        variaveis = local.variables
                        variaveis[acumulador] = acc
                        variaveis[valor] = x
                        acc = corpo(local)
                    return acc
        else:
            return None                     # algo novo: recua inteiro
        etapas.append(etapa)

    def avaliar(env):
        dados = percorrer(fonte(env), no)
        conferir(dados, no)
        for etapa in etapas:
            dados = etapa(dados, env)
        return dados
    return avaliar


def _por_elemento(param, corpo, captura, nome_do_escopo, filtrar):
    """Uma etapa `sift`/`morph` escrita como expressão sobre `param`."""
    from .environment import Environment

    if filtrar:
        def etapa(dados, env):
            local = Environment(parent=env, name=nome_do_escopo)
            saida = []
            for x in dados:
                if captura:
                    local = Environment(parent=env, name=nome_do_escopo)
                local.variables[param] = x
                if corpo(local):
                    saida.append(x)
            return saida
    else:
        def etapa(dados, env):
            local = Environment(parent=env, name=nome_do_escopo)
            saida = []
            for x in dados:
                if captura:
                    local = Environment(parent=env, name=nome_do_escopo)
                local.variables[param] = x
                saida.append(corpo(local))
            return saida
    return etapa


# ── O que o inventario do LIR apontou ────────────────────────
#
# 'dataforge ir --fase=lir' conta, por classe de no, o que recuou para o
# interpretador de arvore — e separa os recuos DENTRO de laco, os unicos
# que aparecem num perfil. Medido nos 388 arquivos do repositorio, a
# lista de quem mais recuava em laco era esta, e nenhum destes nos tinha
# construtor. Nao foi intuicao: foi o relatorio.
#
# Cada um delega ao MESMO auxiliar que o `eval_`/`exec_` usa. Tres deles
# (`_aplicar_unario`, `_pertence`, `_escrever_indice`) foram extraidos
# no interpretador para isso, em vez de copiados para ca.

def _unario(interp, no):
    """`-x` — com a sobrecarga de operador de instancia intacta."""
    if no.op not in ('-', '+', '~'):
        return None
    operando = compilar_expressao(interp, no.operand)
    aplicar = interp._aplicar_unario
    op = no.op
    return lambda env: aplicar(operando(env), op, no)


def _pertence(interp, no):
    """`x in xs` — sempre dentro de laco ou de condicao de laco."""
    elemento = compilar_expressao(interp, no.element)
    recipiente = compilar_expressao(interp, no.container)
    dentro = interp._pertence
    negado = no.negated
    return lambda env: dentro(elemento(env), recipiente(env), negado, no)


def _ternario(interp, no):
    """`a given c otherwise b` — o unico jeito de decidir numa expressao."""
    condicao = compilar_expressao(interp, no.condition)
    entao = compilar_expressao(interp, no.then_value)
    senao = compilar_expressao(interp, no.else_value)
    return lambda env: entao(env) if condicao(env) else senao(env)


def _coalesce(interp, no):
    """`a ?? b` — com a indulgencia do lado esquerdo preservada.

    A leniencia e ESTREITA de proposito, e a estreiteza e decidida aqui,
    uma vez, em vez de num `isinstance` por avaliacao: so leitura por
    indice ou membro imediatamente a esquerda, e so `IndexError_`.
    """
    esquerda = compilar_expressao(interp, no.left)
    direita = compilar_expressao(interp, no.right)
    indulgente = isinstance(no.left, (ast.IndexAccess, ast.MemberAccess))

    def avaliar(env):
        try:
            valor = esquerda(env)
        except IndexError_:
            if indulgente:
                return direita(env)
            raise
        return direita(env) if valor is None else valor
    return avaliar


def _typeof(interp, no):
    tipo_de = interp._type_of
    operando = compilar_expressao(interp, no.operand)
    return lambda env: tipo_de(operando(env))


def _fatia(interp, no):
    """`xs[1:3]` e `xs[::-1]`."""
    objeto = compilar_expressao(interp, no.object)
    inicio = compilar_expressao(interp, no.start) if no.start is not None else None
    fim = compilar_expressao(interp, no.stop) if no.stop is not None else None
    passo = compilar_expressao(interp, no.step) if no.step is not None else None
    fatiar = interp.eval_SliceAccess

    def avaliar(env):
        alvo = objeto(env)
        try:
            return alvo[inicio(env) if inicio else None:
                        fim(env) if fim else None:
                        passo(env) if passo else None]
        except TypeError:
            # a mensagem inteira — nota, dica e doc — mora no interpretador
            return fatiar(no, env)
    return avaliar


def _atribuicao_em_indice(interp, no):
    """`v["k"] := x` — o alvo que mais recuava em laco, e de longe."""
    alvo = no.target
    objeto = compilar_expressao(interp, alvo.object)
    indice = compilar_expressao(interp, alvo.index)
    valor = compilar_expressao(interp, no.value)
    escrever = interp._escrever_indice

    def executar(env):
        pronto = valor(env)
        escrever(objeto(env), indice(env), pronto, no)
        return pronto
    return executar


def _constante_nomeada(interp, no):
    """`steady PI := 3.14`."""
    valor = compilar_expressao(interp, no.value)
    nome = no.name

    def executar(env):
        pronto = valor(env)
        env.define_steady(nome, pronto)
        return pronto
    return executar


def _afirmar(interp, no):
    """`assert c` — 2402 recuos no repositorio, o maior numero absoluto."""
    condicao = compilar_expressao(interp, no.condition)
    mensagem = compilar_expressao(interp, no.message) if no.message else None
    para_texto = interp._to_str

    def executar(env):
        if not condicao(env):
            texto = para_texto(mensagem(env)) if mensagem else "Assertion failed"
            raise RuntimeError_(texto, no.line, no.column)
    return executar


def _parar(interp, no):
    """`halt` — o sinal, sem passar pelo despacho."""
    def executar(env):
        raise HaltSignal()
    return executar


def _pular(interp, no):
    """`skip`."""
    def executar(env):
        raise SkipSignal()
    return executar


_EXPRESSOES = {
    ast.IntegerLiteral: _constante,
    ast.FloatLiteral: _constante,
    ast.DecimalLiteral: _constante,
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
    ast.PipelineExpression: _pipeline,
    ast.UnaryOp: _unario,
    ast.MembershipOp: _pertence,
    ast.TernaryExpression: _ternario,
    ast.CoalesceOp: _coalesce,
    ast.TypeofExpression: _typeof,
    ast.SliceAccess: _fatia,
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
    ast.SteadyDeclaration: _constante_nomeada,
    ast.AssertStatement: _afirmar,
    ast.HaltStatement: _parar,
    ast.SkipStatement: _pular,
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
        except DataForgeError as erro:
            # a mesma posicao que 'execute' da — os dois caminhos concordam
            if not erro.line:
                erro.line, erro.column = no.line, no.column
                erro.args = (erro.format(),)
            raise
        except ControlSignal:
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
