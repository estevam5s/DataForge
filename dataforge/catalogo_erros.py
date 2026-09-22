"""
Catalogo mestre dos erros do DataForge.

Este arquivo e a **unica** fonte de verdade sobre erros. Dele saem duas
coisas que antes viviam separadas e divergiam:

    errors.py         as classes de excecao ('handle DivisionByZeroError')
    diagnosticos.py   o texto de 'dataforge explain DF0212'

Manter as duas listas a mao garantia divergencia: um erro novo ganhava
classe e ficava sem explicacao, ou ganhava explicacao com o codigo
errado. Aqui os dois nascem da mesma linha.

Nao importe nada do pacote aqui. Este modulo e a base da pilha: quem
importa 'errors' importa isto, e um ciclo derruba o interpretador
inteiro.

─── Como ler um codigo ─────────────────────────────────────

    DF  0 6  01
    │    │   └── o erro dentro da familia
    │    └────── a familia
    └─────────── o prefixo, sempre

Familias:

    01xx  sintaxe          o texto nao vira programa
    02xx  execucao         o programa roda e falha
    03xx  tipos            o valor nao serve para a operacao
    04xx  nomes            o nome nao existe, ou nao ali
    05xx  modulos          adopt/relay
    06xx  colecoes         indice, chave, fatia
    07xx  do usuario       trigger, assert
    08xx  limites          recursao, memoria, tempo
    09xx  objetos          blueprint, record, trait, enum
    10xx  concorrencia     thread, canal, async
    11xx  sistema          arquivo, processo, ambiente
    12xx  dados            banco de dados, ORM, serializacao
    13xx  rede             HTTP, Kiln, socket
    14xx  testes           Crucible
    15xx  validacao        conversao, formato, contrato
    16xx  dominio          DDD: valor, agregado, evento, regra
    17xx  reativo          sinal, derivado, efeito, observavel
    18xx  memoria estruturada  layout binario, ponteiro, janela

─── Como adicionar um erro ─────────────────────────────────

Acrescente uma entrada em ERROS. Os campos:

    codigo      DFnnnn, unico
    classe      nome da classe Python gerada; '' para nao gerar classe
                (util quando um codigo so refina uma classe existente)
    pai         nome da classe-mae; define o que 'handle' captura
    titulo      uma linha, sem ponto final
    doc         ancora na documentacao do site
    explicacao  o porque; varias linhas
    exemplo     codigo que provoca, e a versao certa
    solucao     o que fazer

A classe vira exportacao de 'errors.py' automaticamente, e
'dataforge explain <codigo>' passa a responder.
"""

# A raiz de tudo. 'pai' aponta para nomes desta tabela ou para
# 'DataForgeError', que e definida em errors.py.
RAIZ = "DataForgeError"


def _e(codigo, classe, pai, titulo, doc, explicacao, exemplo="", solucao=""):
    return {
        "codigo": codigo,
        "classe": classe,
        "pai": pai,
        "titulo": titulo,
        "doc": doc,
        "explicacao": explicacao.strip("\n"),
        "exemplo": exemplo.strip("\n"),
        "solucao": solucao.strip("\n"),
    }


ERROS = [

    # ═══ 01xx — sintaxe ═══════════════════════════════════

    _e("DF0101", "SyncError", RAIZ,
       "Indentacao inconsistente", "primeiros-passos",
       """
DataForge usa indentacao para delimitar blocos, e aceita apenas espacos.
Um caractere de tabulacao no meio de linhas indentadas com espaco produz
um bloco que o leitor ve de um jeito e o parser ve de outro.
""",
       """
given x bigger 0:
    out "com espacos"
\tout "com tab"      // <- SyncError
""",
       """
Configure o editor para inserir espacos no lugar de tab.
No VS Code:  "editor.insertSpaces": true, "editor.tabSize": 4
Depois:      dataforge fmt arquivo.df
"""),

    _e("DF0102", "LexError", RAIZ,
       "Caractere inesperado", "referencia/gramatica",
       """
O lexer encontrou um simbolo que nao faz parte da linguagem.

A causa mais comum e usar '=' para atribuir. Em DataForge a atribuicao e
':=' — o '=' sozinho nao existe.
""",
       """
x = 10        // errado
x := 10       // certo
""",
       "Troque '=' por ':=', ou remova o simbolo desconhecido."),

    _e("DF0103", "ParseError", RAIZ,
       "Erro de sintaxe", "referencia/gramatica",
       """
O parser encontrou um token onde esperava outro. A mensagem diz o que
esperava; a coluna marca onde.

Causas frequentes:
  - falta ':' no fim de um cabecalho (given, cycle, action, blueprint)
  - parentese ou colchete sem fechar
  - 'otherwise' sem o 'given' correspondente
""",
       """
given x bigger 0        // falta ':'
    out "positivo"

given x bigger 0:       // certo
    out "positivo"
""",
       "Confira o ':' e o pareamento de parenteses e colchetes."),

    _e("DF0104", "UnterminatedStringError", "LexError",
       "String sem fechamento", "referencia/tipos",
       """
Uma aspa foi aberta e a linha terminou sem a aspa que fecha. String
simples nao atravessa linhas em DataForge — a quebra vira o fim do
literal, e o lexer avisa ali.
""",
       """
s := "texto que nao fecha
                          // <- LexError aqui

s := \"\"\"
texto que atravessa
varias linhas
\"\"\"                        // certo, para multilinha
""",
       "Feche a aspa, ou use aspas triplas para texto multilinha."),

    _e("DF0105", "UnterminatedCommentError", "LexError",
       "Comentario de bloco sem fechamento", "referencia/gramatica",
       """
Um '/*' foi aberto e o arquivo terminou sem o '*/' correspondente. Tudo
depois do '/*' virou comentario, inclusive o codigo que deveria rodar.
""",
       """
/* explicacao
out "isto nunca roda"
""",
       "Feche com '*/', ou use '//' para comentario de uma linha."),

    _e("DF0106", "UnbalancedDelimiterError", "ParseError",
       "Parentese, colchete ou chave sem par", "referencia/gramatica",
       """
Um delimitador foi aberto e nao fechado, ou fechado com o simbolo
errado. Dentro de parenteses a indentacao e ignorada, entao um '('
esquecido faz o parser engolir as linhas seguintes e reclamar longe
da causa.
""",
       """
out soma(1, 2          // falta ')'
out [1, 2}             // fecha com o simbolo errado
""",
       "Confira o pareamento. 'dataforge fmt --check' aponta o bloco."),

    _e("DF0107", "ReservedWordError", "ParseError",
       "Palavra reservada usada como nome", "referencia/palavras-reservadas",
       """
As 81 palavras reservadas nao podem ser nome de variavel, de acao nem de
campo. As que mais pegam quem escreve em portugues: 'no', 'in', 'is',
'to', 'from', 'as', 'step', 'point', 'default', 'when'.
""",
       """
no := 5               // 'no' e o literal falso
nota := 5             // certo
""",
       "Escolha outro nome. A lista completa esta em 'dataforge palavras'."),

    _e("DF0108", "InvalidAssignmentTargetError", "ParseError",
       "Alvo de atribuicao invalido", "referencia/atribuicao",
       """
O lado esquerdo de ':=' precisa ser algo que possa guardar um valor: um
nome, um indice, um membro, ou um padrao de desestruturacao. Uma chamada
ou um literal nao servem.
""",
       """
soma(1, 2) := 3       // errado: chamada nao guarda valor
x[0] := 3             // certo
obj.campo := 3        // certo
a, b := 1, 2          // certo
""",
       "Atribua a um nome, indice, membro ou padrao."),

    _e("DF0109", "InvalidNumberError", "LexError",
       "Numero mal formado", "referencia/tipos",
       """
O literal numerico nao forma um numero valido: dois pontos decimais, um
expoente vazio, ou um separador '_' no lugar errado.
""",
       """
x := 1.2.3            // errado
x := 1e               // errado
x := 1_000_000        // certo
x := 0xFF             // certo, hexadecimal
""",
       "Escreva um numero por literal; '_' so entre digitos."),

    _e("DF0110", "InterpolationError", "LexError",
       "Interpolacao mal formada", "referencia/strings",
       """
Dentro de $"..." cada '{' precisa de um '}'. Uma chave sozinha, ou uma
expressao vazia entre elas, nao produz nada que possa ser avaliado.
""",
       """
out $"total: {x"      // falta '}'
out $"total: {}"      // expressao vazia
out $"total: {x}"     // certo
out $"chave literal: {{"   // '{{' escreve uma chave
""",
       "Feche a chave, ou dobre-a ('{{') para escrever uma chave literal."),

    _e("DF0111", "UnexpectedIndentError", "SyncError",
       "Indentacao inesperada", "primeiros-passos",
       """
Uma linha esta mais indentada que a anterior sem que a anterior tenha
aberto um bloco. Um bloco so abre depois de um cabecalho terminado
em ':'.
""",
       """
x := 1
    out x             // indentado sem motivo

given x bigger 0:
    out x             // certo: o ':' abriu o bloco
""",
       "Alinhe a linha com a anterior, ou termine a anterior com ':'."),

    _e("DF0112", "EmptyBlockError", "ParseError",
       "Bloco vazio", "referencia/gramatica",
       """
Um cabecalho terminou em ':' e nenhuma linha indentada veio depois. Todo
bloco precisa de pelo menos uma instrucao.
""",
       """
action nada():
                      // sem corpo

action nada():
    yield void        // certo
""",
       "Escreva o corpo, ou 'yield void' se a acao ainda nao faz nada."),

    _e("DF0113", "DuplicateParameterError", "ParseError",
       "Parametro repetido", "referencia/acoes",
       """
Dois parametros da mesma acao tem o mesmo nome. O segundo apagaria o
primeiro em silencio, entao o parser recusa.
""",
       """
action f(x, y, x):    // 'x' duas vezes
    yield x

action f(x, y, z):    // certo
    yield x
""",
       "Renomeie o parametro repetido."),

    _e("DF0114", "DefaultBeforeRequiredError", "ParseError",
       "Parametro com padrao antes de um sem padrao", "referencia/acoes",
       """
Depois do primeiro parametro com valor padrao, todos precisam ter
padrao. Senao nao ha como saber a qual parametro um argumento posicional
pertence.
""",
       """
action f(a := 1, b):  // errado
    yield a + b

action f(b, a := 1):  // certo
    yield a + b
""",
       "Mova os parametros com padrao para o fim da lista."),

    _e("DF0115", "MultipleRestError", "ParseError",
       "Mais de um '...' no padrao", "referencia/desestruturacao",
       """
Um padrao de desestruturacao aceita um unico '...'. Com dois, nao ha
como dividir o que sobra entre eles.
""",
       """
a, ...meio, ...fim := xs    // errado
a, ...resto := xs           // certo
primeiro, ...meio, ultimo := xs   // certo: '...' so um
""",
       "Deixe um unico '...' no padrao."),

    _e("DF0116", "OrphanClauseError", "ParseError",
       "Clausula sem o bloco a que pertence", "referencia/controle",
       """
'orif', 'otherwise', 'handle' e 'ensure' so existem ligados ao bloco que
os abre. Sozinhos, ou separados por uma linha em branco com indentacao
diferente, o parser nao consegue liga-los.
""",
       """
otherwise:            // sem 'given' antes
    out "nada"

given x bigger 0:
    out "sim"
otherwise:            // certo
    out "nao"
""",
       "Ponha a clausula logo apos o bloco correspondente, no mesmo nivel."),

    _e("DF0117", "InvalidPatternError", "ParseError",
       "Padrao invalido em 'point'", "referencia/pattern-matching",
       """
O que segue 'point' precisa ser um padrao: literal, nome, sequencia
'[a, b]', vault '{"k": v}', chamada de record, membro de enum, ou tipo
com 'as'. Uma expressao qualquer nao serve.
""",
       """
match v:
    point x + 1:      // errado: expressao, nao padrao
        yield 1
    point Integer as n when n bigger 1:   // certo
        yield 2
""",
       "Use um dos formatos de padrao; a guarda vai depois de 'when'."),

    _e("DF0118", "UnreachablePatternError", "ParseError",
       "Padrao inalcancavel", "referencia/pattern-matching",
       """
Um padrao de captura ('point n', sem guarda) ou um 'default' apareceu
antes de outros padroes. Tudo abaixo dele nunca sera testado.
""",
       """
match v:
    point n:          // captura tudo
        yield "qualquer"
    point 0:          // nunca alcancado
        yield "zero"
""",
       "Ordene do especifico ao geral; deixe a captura e 'default' por ultimo."),

    _e("DF0119", "ReturnOutsideActionError", "ParseError",
       "'yield' fora de uma acao", "referencia/acoes",
       """
'yield' encerra a acao em que esta. No topo do arquivo nao ha acao para
encerrar.

Se o que voce quer e imprimir, o comando e 'out'.
""",
       """
yield 42              // errado, no topo do arquivo
out 42                // certo

action f():
    yield 42          // certo
""",
       "Use 'out' para imprimir; 'yield' so dentro de 'action'."),

    _e("DF0120", "EmitOutsideStreamError", "ParseError",
       "'emit' fora de 'stream action'", "referencia/generators",
       """
'emit' produz um valor e continua de onde parou — isso so faz sentido
num generator. Numa acao comum, use 'yield'.
""",
       """
action f():
    emit 1            // errado

stream action f():
    emit 1            // certo
    emit 2
""",
       "Declare a acao como 'stream action', ou troque 'emit' por 'yield'."),

    # ═══ 02xx — execucao ══════════════════════════════════

    _e("DF0201", "RuntimeError_", RAIZ,
       "Erro em tempo de execucao", "referencia/erros",
       """
O programa foi aceito pelo parser e falhou ao rodar. E a categoria mais
larga: dentro dela ficam divisao por zero, conversao impossivel,
operacao sobre um valor que nao a suporta.
""",
       """
monitor:
    arriscado()
handle RuntimeError as e:
    out e.type, e.message
""",
       "Envolva em 'monitor'/'handle', ou corrija a causa apontada."),

    _e("DF0202", "DivisionByZeroError", "RuntimeError_",
       "Divisao por zero", "referencia/operadores",
       """
Dividir por zero nao tem resultado. Vale para '/', '~/' e '%'.

Em ponto flutuante alguns sistemas devolvem infinito; DataForge nao — um
infinito silencioso contamina o calculo e aparece muito depois, longe da
causa.
""",
       """
out a / b                        // erro se b for 0
out a / b given b isnt 0 otherwise 0    // certo
""",
       "Guarde a divisao com 'given', ou use '??' sobre um calculo anterior."),

    _e("DF0203", "ConversionError", "RuntimeError_",
       "Conversao impossivel", "referencia/tipos",
       """
'int("abc")' nao tem resposta. As conversoes de DataForge falham em vez
de devolver zero: um zero inventado por engano e um bug que so aparece
no relatorio do fim do mes.
""",
       """
n := int(entrada)                     // erro se nao for numero
n := int_ou(entrada, 0)               // devolve 0 se falhar
monitor:
    n := int(entrada)
handle ConversionError:
    n := 0
""",
       "Use 'int_ou'/'float_ou' com padrao, ou trate com 'monitor'."),

    _e("DF0204", "ArithmeticOverflowError", "RuntimeError_",
       "Numero grande demais", "referencia/tipos",
       """
O resultado passou do que a representacao suporta. Inteiros em DataForge
crescem sem limite, entao isto vem de operacoes em ponto flutuante:
'1e308 * 10', ou uma potencia que estoura.
""",
       """
out 1e308 * 10        // erro
out 10 ** 1000        // ok: inteiro cresce sem limite
""",
       "Reveja a escala do calculo, ou trabalhe com inteiros."),

    _e("DF0205", "ValueError_", "RuntimeError_",
       "Valor fora do que a operacao aceita", "referencia/erros",
       """
O tipo esta certo e o valor nao serve: raiz de negativo, log de zero,
uma fatia com passo zero, um formato de data que nao existe.
""",
       """
out sqrt(-1)          // erro
out sqrt(abs(x))      // certo
""",
       "Verifique a faixa antes de chamar, ou trate com 'monitor'."),

    _e("DF0206", "NullReferenceError", "RuntimeError_",
       "Uso de 'void'", "referencia/operadores",
       """
Uma operacao recebeu 'void' onde precisava de um valor. Costuma vir de
uma acao sem 'yield', de uma chave ausente, ou de uma busca que nao
achou nada.
""",
       """
out usuario.nome              // erro se 'usuario' for void
out usuario?.nome             // devolve void em vez de falhar
out usuario?.nome ?? "anonimo"  // e um padrao no lugar
""",
       "Use '?.' para navegar com seguranca e '??' para o padrao."),

    _e("DF0207", "ImmutableError", "RuntimeError_",
       "Tentativa de alterar algo imutavel", "referencia/records",
       """
Records e valores 'steady' nao mudam depois de criados. A alteracao
produz um valor novo, e o original segue intacto — e o que permite
compara-los por conteudo e passa-los sem medo.
""",
       """
p := Ponto(1, 2)
p.x := 9                      // erro
p2 := p with {"x": 9}         // certo: um Ponto novo
""",
       "Use 'with' para derivar um valor novo."),

    _e("DF0208", "ConstantReassignmentError", "RuntimeError_",
       "Reatribuicao de 'steady'", "referencia/variaveis",
       """
Um nome declarado com 'steady' recebe valor uma vez. A segunda
atribuicao e recusada no ponto em que acontece.
""",
       """
steady PI := 3.14159
PI := 3                       // erro

PI_APROX := 3                 // certo: outro nome
""",
       "Escolha outro nome, ou declare com ':=' se o valor muda mesmo."),

    _e("DF0209", "UnpackError", "RuntimeError_",
       "Desestruturacao com tamanhos diferentes", "referencia/desestruturacao",
       """
O padrao a esquerda espera um numero de itens que a sequencia a direita
nao tem. Sem '...' os dois lados precisam bater exatamente.
""",
       """
a, b, c := [1, 2]             // erro: 3 nomes, 2 itens
a, b := [1, 2]                // certo
a, ...resto := [1, 2, 3]      // certo: '...' absorve o que sobra
""",
       "Iguale os tamanhos, ou use '...' para o resto."),

    _e("DF0210", "AssertionError_", "RuntimeError_",
       "Assercao falhou", "referencia/testes",
       """
Um 'assert' recebeu algo falso. A mensagem mostra a expressao e os
valores dos dois lados, para nao ser preciso reexecutar para descobrir o
que veio.
""",
       """
assert total is 10
assert total is 10, $"total veio {total}"
""",
       "Corrija o calculo, ou o valor esperado, conforme o caso."),

    _e("DF0211", "NotImplementedError_", "RuntimeError_",
       "Metodo abstrato nao implementado", "referencia/oop",
       """
O metodo existe na hierarquia so como declaracao. Chamar o que ninguem
implementou nao tem o que executar.
""",
       """
blueprint Forma:
    abstract action area()

blueprint Circulo extends Forma:
    action area():                 // certo: implementou
        yield 3.14159 * self.r ** 2
""",
       "Implemente o metodo no blueprint concreto."),

    _e("DF0212", "InfiniteLoopError", "RuntimeError_",
       "Laco sem fim detectado", "referencia/controle",
       """
Um 'persist' passou do limite de iteracoes sem que a condicao mudasse,
ou um generator infinito foi materializado inteiro.

O limite existe para transformar um travamento silencioso — que so o
Ctrl-C resolve — num erro com linha e coluna.
""",
       """
out fib().to_cluster()        // generator infinito: nunca termina
out fib().take(10)            // certo
""",
       "Garanta que a condicao muda, ou limite com 'take(n)' e 'halt'."),

    _e("DF0213", "OperatorError", "RuntimeError_",
       "Operador nao definido para estes valores", "referencia/operadores",
       """
O operador nao sabe o que fazer com a combinacao de tipos recebida. Para
blueprints, isso se resolve declarando o operador.
""",
       """
out spawn Vetor(1,2) + spawn Vetor(3,4)   // erro sem 'operator +'

blueprint Vetor(x, y):
    operator +(outro):                     // certo
        yield spawn Vetor(self.x + outro.x, self.y + outro.y)
""",
       "Declare 'operator <simbolo>(outro)' no blueprint, ou converta antes."),

    _e("DF0214", "ComparisonError", "RuntimeError_",
       "Valores nao comparaveis", "referencia/operadores",
       """
'bigger' e 'smaller' precisam de uma ordem. Numeros e strings tem;
vaults e instancias sem 'operator <' nao tem.
""",
       """
out {"a":1} bigger {"b":2}    // erro
out xs.sort()                 // erro se a lista mistura tipos
""",
       "Compare campos concretos, ou de a ordem com 'operator <'."),

    _e("DF0215", "RangeError", "RuntimeError_",
       "Faixa invalida", "referencia/controle",
       """
Um 'cycle ... from ... to ... step' com passo zero nunca avanca; com
passo negativo e limite crescente, nunca entra.
""",
       """
cycle i from 1 to 10 step 0:  // erro: passo zero
cycle i from 10 to 1 step -1: // certo: desce
""",
       "Use passo diferente de zero, no sentido do inicio para o fim."),

    _e("DF0216", "FormatError", "RuntimeError_",
       "Formato invalido", "referencia/strings",
       """
Um especificador de formato nao existe, ou nao serve para o valor:
'{x:d}' com um texto, '{x:%Y}' com um numero.
""",
       """
out format(nome, "{:d}")      // erro: nome e texto
out format(idade, "{:d}")     // certo
""",
       "Confira o especificador contra o tipo do valor."),

    _e("DF0217", "EncodingError", "RuntimeError_",
       "Problema de codificacao", "referencia/strings",
       """
Um texto nao pode ser representado na codificacao pedida, ou uma
sequencia de bytes nao forma texto valido nela.

Arquivos '.df' precisam ser UTF-8.
""",
       """
conteudo := ler_arquivo("dados.txt")                 // assume UTF-8
conteudo := ler_arquivo("dados.txt", "latin-1")      // outra codificacao
""",
       "Informe a codificacao certa, ou converta o arquivo para UTF-8."),

    _e("DF0218", "TimeoutError_", "RuntimeError_",
       "Tempo esgotado", "referencia/concorrencia",
       """
Uma operacao com limite de tempo nao terminou dentro dele: uma chamada
de rede, uma espera em canal, um teste com prazo.
""",
       """
resposta := Http.get(url, tempo_limite := 5)
""",
       "Aumente o limite, ou trate a demora como um caso previsto."),

    _e("DF0219", "CancelledError", "RuntimeError_",
       "Operacao cancelada", "referencia/concorrencia",
       """
A operacao foi interrompida antes de terminar — por um cancelamento
explicito, ou porque o escopo que a criou terminou primeiro.
""",
       """
monitor:
    esperar(tarefa)
handle CancelledError:
    out "cancelada"
""",
       "Trate o cancelamento como saida legitima, nao como falha."),

    _e("DF0220", "StateError", "RuntimeError_",
       "Operacao invalida no estado atual", "referencia/erros",
       """
O objeto existe mas nao esta pronto para o que foi pedido: ler de um
arquivo fechado, confirmar uma transacao ja desfeita, avancar um
generator esgotado.
""",
       """
monitor:
    conexao.consultar("select 1")
handle StateError:
    conexao.abrir()
""",
       "Verifique o estado antes, ou reabra o recurso."),

    # ═══ 03xx — tipos ═════════════════════════════════════

    _e("DF0301", "TypeError_", RAIZ,
       "Tipo incompativel", "referencia/tipos",
       """
O valor recebido nao serve para a operacao. A mensagem diz o tipo que
chegou e o que era esperado.
""",
       """
out "3" + 4                   // erro: texto e numero
out int("3") + 4              // certo
out "3" .. 4                  // certo: '..' concatena como texto
""",
       "Converta antes com int(), float() ou str()."),

    _e("DF0302", "ArityError", "TypeError_",
       "Numero errado de argumentos", "referencia/acoes",
       """
A acao foi chamada com mais ou menos argumentos do que declara. A
mensagem mostra a assinatura.
""",
       """
action somar(a, b):
    yield a + b

out somar(1)                  // erro: falta 'b'
out somar(1, 2)               // certo
""",
       "Confira a assinatura; parametros opcionais precisam de padrao."),

    _e("DF0303", "UnknownArgumentError", "TypeError_",
       "Argumento nomeado desconhecido", "referencia/acoes",
       """
Um argumento foi passado por nome e a acao nao tem parametro com esse
nome. Costuma ser erro de digitacao.
""",
       """
action f(nome, idade := 0):
    yield nome

f(nome := "Ana", idadde := 3)  // erro: 'idadde'
f(nome := "Ana", idade := 3)   // certo
""",
       "Confira o nome do parametro contra a assinatura."),

    _e("DF0304", "DuplicateArgumentError", "TypeError_",
       "Argumento passado duas vezes", "referencia/acoes",
       """
O mesmo parametro recebeu valor por posicao e por nome. Nao ha como
saber qual dos dois vale.
""",
       """
action f(a, b):
    yield a

f(1, a := 2)                  // erro: 'a' duas vezes
f(1, b := 2)                  // certo
""",
       "Passe cada parametro uma vez so."),

    _e("DF0305", "NotCallableError", "TypeError_",
       "O valor nao e chamavel", "referencia/acoes",
       """
Os parenteses foram aplicados a algo que nao e acao: um numero, um
texto, um vault. Costuma vir de um nome sobrescrito.
""",
       """
soma := 10
out soma(1, 2)                // erro: 'soma' virou numero
""",
       "Confira se o nome foi reatribuido antes da chamada."),

    _e("DF0306", "NotIterableError", "TypeError_",
       "O valor nao pode ser percorrido", "referencia/colecoes",
       """
'cycle ... in' e as compreensoes precisam de algo percorrivel: cluster,
vault, string, range, generator, ou um objeto com 'iterar()'.
""",
       """
cycle x in 42:                // erro
cycle x in range(42):         // certo
""",
       "Envolva num cluster, ou use 'range' para numeros."),

    _e("DF0307", "NotIndexableError", "TypeError_",
       "O valor nao aceita [ ]", "referencia/colecoes",
       """
So cluster, vault, string e record aceitam indexacao. Numeros e acoes
nao.
""",
       """
x := 42
out x[0]                      // erro
""",
       "Confira o tipo do valor; talvez falte uma chamada antes."),

    _e("DF0308", "NotHashableError", "TypeError_",
       "Chave invalida para vault", "referencia/colecoes",
       """
Chave de vault precisa ser imutavel: texto, numero, booleano, ou record.
Um cluster ou outro vault nao servem, porque mudam depois de guardados e
a busca deixa de encontra-los.
""",
       """
v := {}
v[[1, 2]] := "x"              // erro: cluster como chave
v[Ponto(1, 2)] := "x"         // certo: record e imutavel
""",
       "Use texto, numero ou record como chave."),

    _e("DF0309", "TypeAnnotationError", "TypeError_",
       "Anotacao de tipo desconhecida", "referencia/tipos",
       """
O tipo escrito na anotacao nao existe. Os tipos da linguagem sao
Integer, Float, String, Boolean, Cluster, Vault, Action, Any, alem dos
records, blueprints, enums e traits declarados.
""",
       """
x: Inteiro := 1               // erro: nome em portugues
x: Integer := 1               // certo
""",
       "Use um dos tipos da linguagem, ou um nome declarado no arquivo."),

    _e("DF0310", "GenericArityError", "TypeError_",
       "Numero errado de parametros de tipo", "referencia/generics",
       """
O blueprint ou a acao declara N parametros de tipo e recebeu outra
quantidade entre '<' e '>'.
""",
       """
blueprint Par<A, B>:
    ...

p: Par<Integer> := ...        // erro: falta um
p: Par<Integer, String> := ...  // certo
""",
       "Informe um argumento de tipo para cada parametro declarado."),

    _e("DF0311", "CoercionError", "TypeError_",
       "Conversao implicita recusada", "referencia/tipos",
       """
DataForge nao converte tipos por conta propria numa operacao. Somar
texto com numero e quase sempre um engano, e o erro aparece onde o
engano esta, nao no relatorio.
""",
       """
total := "10" + 5             // erro
total := int("10") + 5        // certo
rotulo := "10" .. 5           // certo: concatena como texto
""",
       "Converta explicitamente, ou use '..' para concatenar."),

    _e("DF0312", "SignatureMismatchError", "TypeError_",
       "Assinatura incompativel na sobrescrita", "referencia/oop",
       """
O metodo do herdeiro tem aridade diferente da do metodo que sobrescreve.
Quem chama pela classe-mae passaria argumentos que o herdeiro nao
aceita.
""",
       """
blueprint Base:
    action f(a, b):
        yield a

blueprint Filho extends Base:
    action f(a):              // erro: perdeu um parametro
        yield a
""",
       "Mantenha a assinatura da mae, ou de padrao ao que falta."),

    _e("DF0313", "ReadOnlyPropertyError", "TypeError_",
       "Propriedade sem 'set'", "referencia/oop",
       """
A propriedade declara 'get' e nao 'set'. Ela e derivada: existe para ser
lida, e escreve-la nao teria onde guardar.
""",
       """
blueprint Circulo(r):
    get area():
        yield 3.14159 * self.r ** 2

c.area := 10                  // erro
c.r := 10                     // certo: mude a origem
""",
       "Altere o campo de origem, ou declare um 'set'."),

    _e("DF0314", "AbstractInstantiationError", "TypeError_",
       "'spawn' de blueprint abstrato", "referencia/oop",
       """
Um blueprint abstrato descreve um contrato e deixa metodos sem corpo.
Instanciar produziria um objeto com buracos.
""",
       """
abstract blueprint Forma:
    abstract action area()

f := spawn Forma()            // erro
f := spawn Circulo(2)         // certo
""",
       "Instancie um herdeiro concreto."),

    _e("DF0315", "PrivateAccessError", "TypeError_",
       "Acesso a membro 'private'", "referencia/oop",
       """
'private' limita o acesso ao blueprint que declarou o membro — nem o
herdeiro entra. Para abrir ao herdeiro, o modificador e 'protected'.
""",
       """
blueprint Conta:
    private saldo: Float := 0.0
    get extrato():            // certo: expoe sob controle
        yield self.saldo

out c.saldo                   // erro
out c.extrato                 // certo
""",
       "Exponha por um 'get', ou troque para 'protected'."),

    _e("DF0316", "ProtectedAccessError", "TypeError_",
       "Acesso a membro 'protected'", "referencia/oop",
       """
'protected' alcanca o blueprint que declarou e seus herdeiros. De fora
da linhagem, o acesso e recusado.
""",
       """
blueprint Base:
    protected estado: Integer := 0

out (spawn Base()).estado     // erro: de fora
""",
       "Acesse de dentro da linhagem, ou exponha por um 'get'."),

    _e("DF0317", "FinalOverrideError", "TypeError_",
       "Sobrescrita de metodo 'final'", "referencia/oop",
       """
'final' marca um metodo que a linhagem nao deve mudar — normalmente
porque outra coisa depende do comportamento exato dele.
""",
       """
blueprint Base:
    final action id():
        yield self.__id

blueprint Filho extends Base:
    action id():              // erro
        yield 0
""",
       "Escolha outro nome, ou remova o 'final' da mae se ele nao se justifica."),

    _e("DF0319", "InternalAccessError", "TypeError_",
       "Acesso a membro 'internal' de outro arquivo", "oop/modificadores",
       """
'internal' abre o membro para o arquivo em que o blueprint foi
declarado, e so para ele. E a visibilidade de um modulo: as pecas de
dentro conversam, e quem adota o arquivo ve so o que e publico.
""",
       """
// banco.df
blueprint Conexao:
    internal action bruta():
        yield "sql"

// app.df
adopt ./banco as B
(spawn B.Conexao()).bruta()       // erro
""",
       "Exponha uma acao publica que faca o que o outro arquivo precisa."),

    _e("DF0318", "TraitContractError", "TypeError_",
       "Contrato de trait nao cumprido", "referencia/traits",
       """
O blueprint declara 'with <Trait>' e nao implementou todos os metodos
que o trait exige. A checagem acontece na declaracao, nao no primeiro
uso.
""",
       """
trait Forma:
    action area()

blueprint Caixa with Forma:   // erro: falta 'area'
    action perimetro():
        yield 0
""",
       "Implemente os metodos que faltam, listados na mensagem."),

    # ═══ 04xx — nomes ═════════════════════════════════════

    _e("DF0401", "NameError_", RAIZ,
       "Nome nao definido", "referencia/variaveis",
       """
O nome nao existe no escopo onde foi usado. Quando ha um parecido, a
mensagem sugere.

Causas frequentes: erro de digitacao, uso antes da atribuicao, ou uma
variavel criada dentro de um bloco e lida fora dele.
""",
       """
contador := 0
out contadr                   // erro: sugere 'contador'
""",
       "Confira a grafia, e se o nome foi atribuido antes deste ponto."),

    _e("DF0402", "UndefinedMemberError", "NameError_",
       "Membro inexistente", "referencia/oop",
       """
O objeto nao tem esse campo, metodo ou propriedade. A mensagem lista o
que ele tem, e sugere o parecido.
""",
       """
p := Ponto(1, 2)
out p.z                       // erro: Ponto tem x e y
""",
       "Confira o nome do membro contra a declaracao."),

    _e("DF0403", "UseBeforeAssignmentError", "NameError_",
       "Uso antes da atribuicao", "referencia/variaveis",
       """
O nome existe no escopo — ha uma atribuicao a ele mais abaixo — mas foi
lido antes de receber valor.
""",
       """
out total                     // erro
total := 10

total := 10                   // certo
out total
""",
       "Mova a atribuicao para antes do uso."),

    _e("DF0404", "SelfOutsideMethodError", "NameError_",
       "'self' fora de um metodo", "referencia/oop",
       """
'self' aponta para o objeto em que o metodo roda. No topo do arquivo, ou
numa acao solta, nao ha objeto.
""",
       """
action f():
    yield self.x              // erro

blueprint B:
    action f():
        yield self.x          // certo
""",
       "Mova a acao para dentro do blueprint, ou receba o objeto por parametro."),

    _e("DF0405", "RootOutsideChildError", "NameError_",
       "'root' sem classe-mae", "referencia/oop",
       """
'root' chama a versao da mae. Num blueprint sem 'extends' nao ha mae
para chamar.
""",
       """
blueprint Filho extends Base:
    action f():
        root.f()              // certo
""",
       "Declare 'extends', ou remova o 'root'."),

    _e("DF0406", "ShadowedBuiltinError", "NameError_",
       "Nome global sobrescrito", "referencia/variaveis",
       """
Um nome da biblioteca padrao foi reatribuido, e o codigo abaixo esperava
o original. Nao e proibido — mas quando a chamada falha, e quase sempre
isto.
""",
       """
len := 5
out len("abc")                // erro: 'len' virou numero
""",
       "Renomeie a variavel; a lista de globais esta em 'dataforge globais'."),

    _e("DF0407", "ScopeError", "NameError_",
       "Nome fora de alcance", "referencia/variaveis",
       """
O nome existe, mas nao neste escopo: foi criado dentro de uma acao, de
um bloco 'handle', ou de uma compreensao, e lido fora.
""",
       """
action f():
    interno := 1
out interno                   // erro: 'interno' morreu com a acao
""",
       "Devolva o valor com 'yield', ou declare o nome no escopo de fora."),

    _e("DF0408", "DuplicateDeclarationError", "NameError_",
       "Declaracao repetida", "referencia/variaveis",
       """
Dois blueprints, records, enums ou traits com o mesmo nome no mesmo
arquivo. O segundo apagaria o primeiro sem aviso.
""",
       """
record Ponto:
    x: Integer

record Ponto:                 // erro
    y: Integer
""",
       "Renomeie um dos dois, ou junte as declaracoes."),

    _e("DF0409", "LabelError", "NameError_",
       "Rotulo de laco desconhecido", "referencia/controle",
       """
'halt <rotulo>' ou 'skip <rotulo>' apontou para um rotulo que nao existe
entre os lacos abertos.
""",
       """
cycle externo i in xs:
    cycle j in ys:
        halt externo          // certo
""",
       "Confira o nome do rotulo, e se o laco ainda esta aberto aqui."),

    _e("DF0410", "ReservedNameError", "NameError_",
       "Nome reservado pelo runtime", "referencia/variaveis",
       """
Nomes que comecam e terminam com '__' pertencem ao runtime
('__metadados__', '__tipo__'). Redefini-los quebra reflexao e
decoradores.
""",
       """
__metadados__ := {}           // erro
meus_metadados := {}          // certo
""",
       "Escolha um nome sem o prefixo '__'."),

    # ═══ 05xx — modulos ═══════════════════════════════════

    _e("DF0501", "ImportError_", RAIZ,
       "Falha ao importar", "referencia/modulos",
       """
'adopt' nao encontrou o modulo. Ele procura, nesta ordem: os modulos
Arcane.*, os arquivos '.df' vizinhos, e 'forge_modules/' subindo ate o
'forge.toml'.
""",
       """
adopt Arcane.Math as Math
adopt "./utilitarios.df" as Util
""",
       "Confira o nome, e rode 'dataforge install' se for dependencia."),

    _e("DF0502", "ModuleNotFoundError_", "ImportError_",
       "Modulo inexistente", "referencia/modulos",
       """
Nenhum arquivo nem modulo com esse nome foi encontrado nos lugares onde
'adopt' procura. A mensagem lista os caminhos tentados.
""",
       """
adopt Arcane.Mat as M         // erro: e 'Arcane.Math'
""",
       "Veja 'dataforge modulos' para a lista, ou instale o pacote."),

    _e("DF0503", "SymbolNotExportedError", "ImportError_",
       "Simbolo nao exportado", "referencia/modulos",
       """
O modulo existe e nao expoe esse nome. Um arquivo '.df' so expoe o que
lista em 'relay'.
""",
       """
adopt {calcular} from "./util.df"   // erro se util.df nao faz 'relay calcular'
""",
       "Acrescente o nome ao 'relay' do modulo de origem."),

    _e("DF0504", "CircularImportError", "ImportError_",
       "Ciclo de importacao", "referencia/modulos",
       """
Dois ou mais modulos se importam em circulo. A mensagem mostra o
caminho completo do ciclo.
""",
       """
// a.df faz 'adopt "./b.df"'
// b.df faz 'adopt "./a.df"'   <- ciclo
""",
       "Extraia o que os dois usam para um terceiro modulo."),

    _e("DF0505", "PackageNotInstalledError", "ImportError_",
       "Pacote declarado e nao instalado", "referencia/pacotes",
       """
O 'forge.toml' lista a dependencia e ela nao esta em 'forge_modules/'.
""",
       """
dataforge install
""",
       "Rode 'dataforge install' para resolver o forge.toml."),

    _e("DF0506", "VersionConflictError", "ImportError_",
       "Conflito de versao", "referencia/pacotes",
       """
Dois pacotes pedem faixas incompativeis do mesmo terceiro. Instalar duas
copias em versoes diferentes gera bug irreproduzivel, entao o resolvedor
falha dizendo quem pediu o que.
""",
       """
dataforge install --explicar    // mostra a arvore de pedidos
""",
       "Afrouxe uma das faixas no forge.toml, ou atualize o pacote."),

    _e("DF0507", "IntegrityError", "ImportError_",
       "Pacote corrompido", "referencia/pacotes",
       """
O sha256 do tarball baixado nao bate com o do 'forge.lock'. O conteudo
mudou entre o registro e voce.
""",
       """
dataforge install --limpar-cache
""",
       "Limpe o cache e reinstale. Se persistir, o registro esta inconsistente."),

    _e("DF0508", "UnsafeArchiveError", "ImportError_",
       "Pacote com caminho inseguro", "referencia/pacotes",
       """
O tarball contem uma entrada com '../' ou um link simbolico, que
escreveria fora da pasta do pacote. A extracao e recusada inteira.
""",
       """
dataforge pack --verificar
""",
       "Reporte ao autor do pacote; nao extraia manualmente."),

    _e("DF0509", "ManifestError", "ImportError_",
       "forge.toml invalido", "referencia/pacotes",
       """
O manifesto tem sintaxe TOML invalida, ou falta um campo obrigatorio
('nome', 'versao').
""",
       """
dataforge info                 // mostra o manifesto lido
""",
       "Corrija o TOML; 'dataforge init' gera um exemplo valido."),

    _e("DF0510", "RelayError", "ImportError_",
       "'relay' de nome inexistente", "referencia/modulos",
       """
O modulo tenta exportar um nome que nao declara.
""",
       """
relay somar                   // erro se 'somar' nao existe no arquivo
""",
       "Declare o nome, ou remova-o do 'relay'."),

    # ═══ 06xx — colecoes ══════════════════════════════════

    _e("DF0601", "IndexError_", RAIZ,
       "Indice fora da faixa", "referencia/colecoes",
       """
O indice pedido nao existe. A mensagem diz o tamanho da colecao e a
faixa valida, inclusive os negativos.
""",
       """
xs := [1, 2, 3]
out xs[5]                     // erro: vai de -3 a 2
out xs[-1]                    // certo: o ultimo
""",
       "Confira o tamanho com 'len(xs)' antes, ou use '?[i]'."),

    _e("DF0602", "KeyError_", "IndexError_",
       "Chave inexistente", "referencia/colecoes",
       """
O vault nao tem essa chave. A mensagem lista as que existem e sugere a
parecida.
""",
       """
v := {"nome": "Ana"}
out v["nom"]                  // erro: sugere "nome"
out v["nom"] ?? "sem nome"    // certo: padrao
out v.get("nom", "sem nome")  // certo
""",
       "Use '??' ou '.get(chave, padrao)' quando a ausencia e prevista."),

    _e("DF0603", "EmptyCollectionError", "IndexError_",
       "Operacao sobre colecao vazia", "referencia/colecoes",
       """
'first', 'last', 'min', 'max', 'mean' e 'pop' precisam de pelo menos um
item. Numa colecao vazia nao ha resposta certa — e devolver zero
esconderia o caso.
""",
       """
out xs.min()                       // erro se xs esta vazia
out xs.min() given len(xs) bigger 0 otherwise 0    // certo
""",
       "Verifique 'len(xs)' antes, ou use a variante com padrao."),

    _e("DF0604", "SliceError", "IndexError_",
       "Fatia invalida", "referencia/colecoes",
       """
Passo zero nao avanca, e os limites precisam ser inteiros. Limites fora
da faixa nao sao erro: a fatia so devolve menos itens.
""",
       """
out xs[::0]                   // erro: passo zero
out xs[1.5:]                  // erro: limite nao inteiro
out xs[10:20]                 // ok: devolve []
""",
       "Use passo diferente de zero e limites inteiros."),

    _e("DF0605", "MutationDuringIterationError", "IndexError_",
       "Colecao alterada durante o percurso", "referencia/colecoes",
       """
Inserir ou remover itens de uma colecao enquanto ela e percorrida pula
itens ou repete outros, dependendo de onde a mudanca cai.
""",
       """
cycle x in xs:
    xs.remove(x)              // erro

cycle x in xs.copy():         // certo: percorre uma copia
    xs.remove(x)
""",
       "Percorra uma copia, ou monte uma lista nova com compreensao."),

    _e("DF0606", "ValueNotFoundError", "IndexError_",
       "Valor nao encontrado", "referencia/colecoes",
       """
'index_of' e 'remove' precisam que o item exista. Quando a ausencia e
prevista, 'contains' responde sem falhar.
""",
       """
out xs.index_of(9)            // erro se 9 nao esta
out xs.contains(9)            // certo: devolve yes/no
""",
       "Teste com 'contains' antes, ou trate com 'monitor'."),

    _e("DF0607", "DuplicateKeyError", "IndexError_",
       "Chave repetida no literal", "referencia/colecoes",
       """
O mesmo texto aparece duas vezes como chave no mesmo literal de vault. A
segunda apagaria a primeira em silencio.
""",
       """
v := {"a": 1, "a": 2}         // erro
""",
       "Deixe uma chave so, ou atribua depois se a sobrescrita e intencional."),

    _e("DF0608", "LengthMismatchError", "IndexError_",
       "Tamanhos diferentes", "referencia/colecoes",
       """
'zip_estrito', 'juntar_colunas' e operacoes elemento a elemento exigem o
mesmo tamanho. A versao nao estrita corta no menor.
""",
       """
out zip_estrito([1,2,3], [4,5])   // erro
out zip([1,2,3], [4,5])           // certo: corta em 2
""",
       "Iguale os tamanhos, ou use a variante que corta."),

    _e("DF0609", "NegativeSizeError", "IndexError_",
       "Tamanho negativo", "referencia/colecoes",
       """
'chunk', 'take', 'repeat' e 'range' com tamanho negativo nao tem
significado.
""",
       """
out xs.chunk(-1)              // erro
out xs.chunk(2)               // certo
""",
       "Use um tamanho positivo."),

    _e("DF0610", "NestedDepthError", "IndexError_",
       "Aninhamento profundo demais", "referencia/colecoes",
       """
'flatten' e a serializacao param num limite de profundidade. Passar dele
costuma significar uma estrutura que se contem — um cluster que aponta
para si mesmo.
""",
       """
out xs.flatten(3)             // limita a profundidade
""",
       "Limite a profundidade, ou quebre o ciclo na estrutura."),

    _e("DF0611", "SortKeyError", "IndexError_",
       "Chave de ordenacao invalida", "referencia/colecoes",
       """
A acao passada em 'chave' falhou para algum item, ou devolveu valores
que nao se comparam entre si.
""",
       """
out sorted(pessoas, chave := lambda p: p.idade)    // certo
""",
       "Garanta que a chave existe em todos os itens e devolve o mesmo tipo."),

    _e("DF0612", "FrozenCollectionError", "IndexError_",
       "Colecao congelada", "referencia/colecoes",
       """
A colecao veio de um record ou de um valor 'steady' e nao aceita
alteracao no lugar.
""",
       """
novos := [...antigos, item]   // certo: monta uma nova
""",
       "Monte uma colecao nova com spread em vez de alterar."),

    # ═══ 07xx — do usuario ════════════════════════════════

    _e("DF0701", "TriggerError", RAIZ,
       "Erro disparado por 'trigger'", "referencia/erros",
       """
O proprio programa disparou o erro. 'handle RuntimeError' nao captura
isto — o tipo e 'TriggerError'.
""",
       """
trigger "saldo insuficiente"

monitor:
    sacar(1000)
handle TriggerError as e:
    out e.message
""",
       "Capture com 'handle TriggerError', ou nomeie o erro no 'trigger'."),

    _e("DF0702", "CustomError", "TriggerError",
       "Erro definido pelo programa", "referencia/erros",
       """
Um 'trigger' com tipo nomeado. O nome vira o tipo capturavel, o que
permite tratar cada falha do dominio separadamente.
""",
       """
trigger SaldoInsuficiente("faltam 20 reais")

monitor:
    sacar(1000)
handle SaldoInsuficiente as e:
    out e.message
""",
       "Nomeie o erro no 'trigger' e capture pelo mesmo nome."),

    _e("DF0703", "RethrowError", "TriggerError",
       "Reenvio sem erro em curso", "referencia/erros",
       """
'trigger' sem argumento reenvia o erro que esta sendo tratado. Fora de
um 'handle' nao ha erro para reenviar.
""",
       """
monitor:
    arriscado()
handle e:
    registrar(e)
    trigger                   // certo: reenvia
""",
       "Use 'trigger' sozinho apenas dentro de um 'handle'."),

    _e("DF0704", "UnhandledError", RAIZ,
       "Erro nao tratado", "referencia/erros",
       """
O erro subiu ate o topo do programa sem encontrar 'handle'. A pilha
mostra o caminho da chamada, do topo ate onde falhou.
""",
       """
monitor:
    principal()
handle e:
    out "falhou:", e.message
""",
       "Trate onde da para decidir o que fazer, nao onde acontece."),

    _e("DF0705", "PanicError", RAIZ,
       "Falha irrecuperavel", "referencia/erros",
       """
Uma falha que 'handle' nao captura de proposito: invariante do runtime
quebrada, ou 'panic' explicito. Existe para nao deixar um programa
continuar em estado inconsistente.
""",
       """
panic("indice negativo apos validacao — impossivel")
""",
       "Corrija a invariante; nao tente capturar."),

    # ═══ 08xx — limites ═══════════════════════════════════

    _e("DF0801", "StackOverflowError_", RAIZ,
       "Recursao profunda demais", "referencia/acoes",
       """
A pilha passou do limite. Quase sempre e recursao sem caso base, ou com
um caso base que nunca e alcancado.
""",
       """
action fat(n):
    given n smaller 2:        // caso base
        yield 1
    yield n * fat(n - 1)
""",
       "Confira o caso base, ou reescreva como laco."),

    _e("DF0802", "MemoryLimitError", RAIZ,
       "Memoria esgotada", "referencia/desempenho",
       """
A alocacao nao coube. Costuma vir de materializar um generator infinito,
ou de uma compreensao sobre um produto cartesiano grande.
""",
       """
out fib().take(1000)          // certo: limita
""",
       "Trabalhe preguicosamente com 'stream' e 'take'."),

    _e("DF0803", "TimeLimitError", RAIZ,
       "Tempo limite do programa", "referencia/desempenho",
       """
A execucao passou do limite configurado. No playground e no runner de
testes existe um teto para nao travar a sessao.
""",
       """
dataforge run programa.df --tempo-limite=30
""",
       "Aumente o limite, ou reduza o trabalho por execucao."),

    _e("DF0804", "OutputLimitError", RAIZ,
       "Saida grande demais", "referencia/desempenho",
       """
O programa escreveu mais do que o destino aceita guardar. Normalmente e
um 'out' dentro de um laco que nao para.
""",
       """
cycle i from 1 to 10:
    out i                     // certo: quantidade previsivel
""",
       "Reduza o que e impresso, ou escreva num arquivo."),

    _e("DF0805", "ComplexityLimitError", RAIZ,
       "Estrutura complexa demais", "referencia/desempenho",
       """
Aninhamento ou tamanho de expressao passou do que o parser aceita. Um
literal com dezenas de milhares de itens costuma vir de geracao
automatica.
""",
       """
xs := [i cycle i in range(100000)]   // certo: gera em vez de literalizar
""",
       "Gere os dados em tempo de execucao em vez de escreve-los."),

    _e("DF0806", "ResourceExhaustedError", RAIZ,
       "Recurso do sistema esgotado", "referencia/sistema",
       """
Descritores de arquivo, threads ou conexoes acabaram. Normalmente e um
recurso aberto dentro de um laco e nunca fechado.
""",
       """
with abrir(caminho) as f:     // certo: fecha sozinho
    out f.ler()
""",
       "Feche o que abre, ou use 'with' para fechar automaticamente."),

    # ═══ 09xx — objetos ═══════════════════════════════════

    _e("DF0901", "ObjectError", RAIZ,
       "Erro de objeto", "referencia/oop",
       """
Familia dos erros de blueprint, record, trait e enum: construcao,
heranca, contrato e ciclo de vida.
""",
       """
monitor:
    obj := spawn Coisa()
handle ObjectError as e:
    out e.message
""",
       "A mensagem especifica diz qual regra de objeto foi violada."),

    _e("DF0902", "ConstructorError", "ObjectError",
       "Falha na construcao", "referencia/oop",
       """
O 'setup' falhou, ou os argumentos nao batem com os parametros do
construtor inline.
""",
       """
blueprint Ponto(x, y):
    action setup(x, y):
        given x smaller 0:
            trigger "x negativo"
""",
       "Confira os argumentos do 'spawn' e o corpo do 'setup'."),

    _e("DF0903", "InheritanceCycleError", "ObjectError",
       "Ciclo de heranca", "referencia/oop",
       """
Um blueprint herda, direta ou indiretamente, de si mesmo.
""",
       """
blueprint A extends B: ...
blueprint B extends A: ...    // erro
""",
       "Quebre o ciclo; extraia o comum para uma terceira classe ou trait."),

    _e("DF0904", "UnknownParentError", "ObjectError",
       "Classe-mae inexistente", "referencia/oop",
       """
O nome apos 'extends' nao e um blueprint declarado nem importado.
""",
       """
adopt {Base} from "./base.df"
blueprint Filho extends Base: ...    // certo
""",
       "Importe a classe-mae, ou confira a grafia."),

    _e("DF0905", "UnknownTraitError", "ObjectError",
       "Trait inexistente", "referencia/traits",
       """
O nome apos 'with' nao e um trait declarado nem importado.
""",
       """
trait Forma:
    action area()

blueprint Caixa with Forma: ...      // certo
""",
       "Declare ou importe o trait antes do blueprint."),

    _e("DF0906", "ConflictingTraitError", "ObjectError",
       "Traits em conflito", "referencia/traits",
       """
Dois traits trazem uma implementacao padrao para o mesmo metodo, e o
blueprint nao escolheu qual vale.
""",
       """
blueprint C with A, B:
    action f():               // certo: decide explicitamente
        yield A.f(self)
""",
       "Implemente o metodo no blueprint para desempatar."),

    _e("DF0907", "RecordMutationError", "ObjectError",
       "Alteracao de record", "referencia/records",
       """
Records sao imutaveis: e o que permite compara-los por conteudo e usa-los
como chave de vault.
""",
       """
p2 := p with {"x": 9}         // certo
""",
       "Derive um valor novo com 'with'."),

    _e("DF0908", "RecordArityError", "ObjectError",
       "Campos do record nao batem", "referencia/records",
       """
A construcao passou mais ou menos valores do que o record declara. Sem
padrao, todos os campos sao obrigatorios.
""",
       """
record Ponto:
    x: Integer
    y: Integer := 0

Ponto(1)                      // certo: y usa o padrao
""",
       "Passe todos os campos sem padrao, na ordem declarada."),

    _e("DF0909", "UnknownFieldError", "ObjectError",
       "Campo desconhecido em 'with'", "referencia/records",
       """
'with' so altera campos que o record declara. Uma chave nova viraria um
campo fantasma que nada le.
""",
       """
p with {"z": 1}               // erro: Ponto nao tem 'z'
p with {"x": 1}               // certo
""",
       "Confira o nome do campo contra a declaracao do record."),

    _e("DF0910", "EnumMemberError", "ObjectError",
       "Membro de enum inexistente", "referencia/enums",
       """
O enum nao tem esse membro. A mensagem lista os que tem.
""",
       """
enum Status:
    Ativo
    Inativo

out Status.Pendente           // erro
""",
       "Use um dos membros listados, ou acrescente-o ao enum."),

    _e("DF0911", "EnumValueError", "ObjectError",
       "Valor sem membro correspondente", "referencia/enums",
       """
'Status(valor)' procura o membro com aquele valor e nao achou.
""",
       """
out Status("off")             // certo se algum membro vale "off"
""",
       "Confira o valor, ou trate a ausencia com 'monitor'."),

    _e("DF0912", "NonExhaustiveMatchError", "ObjectError",
       "'match' sem caso para o valor", "referencia/pattern-matching",
       """
Nenhum 'point' casou e nao ha 'default'. Um 'match' sem saida devolveria
'void' em silencio, que aparece muito depois como NullReferenceError.
""",
       """
match s:
    point Status.Ativo:
        yield 1
    default:                  // certo: fecha o match
        yield 0
""",
       "Acrescente 'default', ou cubra todos os membros do enum."),

    _e("DF0913", "OperatorOverloadError", "ObjectError",
       "Operador sobrecarregado invalido", "referencia/oop",
       """
'operator' aceita um conjunto fixo de simbolos, e cada um tem aridade
propria: binarios recebem um parametro, unarios nenhum.
""",
       """
blueprint V(x):
    operator +(outro):        // certo: binario, 1 parametro
        yield spawn V(self.x + outro.x)
""",
       "Confira o simbolo e o numero de parametros."),

    _e("DF0914", "PropertyRecursionError", "ObjectError",
       "Propriedade que chama a si mesma", "referencia/oop",
       """
O 'get' le a propria propriedade em vez do campo de apoio, e a leitura
se repete ate estourar a pilha.
""",
       """
blueprint C:
    private _raio: Float := 0.0
    get raio():
        yield self._raio      // certo: le o campo, nao a propriedade
""",
       "Leia o campo de apoio dentro do 'get'."),

    _e("DF0915", "StaticContextError", "ObjectError",
       "'self' em metodo estatico", "referencia/oop",
       """
Um metodo estatico roda sem objeto. Se ele precisa de 'self', nao e
estatico.
""",
       """
blueprint Mat:
    static action dobro(x):   // certo: nao usa self
        yield x * 2
""",
       "Remova o 'static', ou pare de usar 'self' no metodo."),

    _e("DF0916", "DecoratorError", "ObjectError",
       "Decorador invalido", "referencia/decoradores",
       """
O nome apos '@' nao existe, nao e chamavel, ou devolveu algo que nao
substitui o alvo.
""",
       """
@Http.Get("/usuarios")
action listar():
    yield []
""",
       "Confira o nome do decorador e o que ele devolve."),

    _e("DF0917", "FinalBlueprintError", "ObjectError",
       "Heranca de blueprint final", "oop/modificadores",
       """
'final blueprint' fecha a hierarquia: ninguem herda dele. E a forma de
dizer que o comportamento esta completo e que uma filha so poderia
quebrar o que ele promete.
""",
       """
final blueprint Dinheiro(centavos):
    action somar(o):
        yield spawn Dinheiro(self.centavos + o.centavos)

blueprint Moeda extends Dinheiro:     // erro
    x := 1
""",
       "Use composicao: guarde um Dinheiro num campo em vez de herdar dele."),

    _e("DF0918", "SealedBlueprintError", "ObjectError",
       "Heranca de blueprint selado fora do arquivo", "oop/modificadores",
       """
'sealed blueprint' so aceita filhas declaradas no MESMO arquivo. A
familia fica fechada e conhecida — e o que deixa um 'match' saber que
cobriu todos os casos.
""",
       """
// formas.df
sealed blueprint Forma:
    abstract action area()

// outro.df
adopt ./formas as F
blueprint Hexagono extends F.Forma:     // erro
    action area():
        yield 0
""",
       "Declare a filha no arquivo da mae, ou tire o 'sealed' se a familia e aberta."),

    _e("DF0919", "OverrideTargetError", "ObjectError",
       "'override' sem nada para sobrescrever", "oop/modificadores",
       """
'override' e uma promessa: este membro substitui um da mae, de um trait
ou de um contrato. Quando nao ha o que substituir — o nome foi digitado
errado, ou a mae mudou — a promessa e falsa, e o metodo nunca seria
chamado por quem conhece a mae.
""",
       """
blueprint Animal:
    action falar():
        yield "..."

blueprint Gato extends Animal:
    override action fala():      // erro: a mae tem 'falar'
        yield "miau"
""",
       "Corrija o nome para o da mae, ou tire o 'override'."),

    _e("DF0920", "OverloadResolutionError", "ObjectError",
       "Nenhuma sobrecarga aceita os argumentos", "oop/sobrecarga",
       """
Uma acao 'overload' tem variantes, e a chamada escolhe pela quantidade
e pelo tipo dos argumentos. Nenhuma variante aceitou os que vieram.
""",
       """
overload action area(r: Float):
    yield 3.14 * r * r
overload action area(l: Float, a: Float):
    yield l * a

area("dez")     // erro
""",
       "Passe argumentos que uma das variantes aceite, ou acrescente a variante que falta."),

    _e("DF0921", "AmbiguousOverloadError", "OverloadResolutionError",
       "Mais de uma sobrecarga serve igualmente bem", "oop/sobrecarga",
       """
Duas variantes aceitam os argumentos com a mesma precisao. Escolher uma
em silencio faria o resultado depender da ordem em que foram escritas.
""",
       """
overload action f(x: Integer, y):
    yield 1
overload action f(x, y: Integer):
    yield 2

f(1, 2)     // erro: as duas servem
""",
       "Declare os tipos que desempatam, ou junte as variantes numa so."),

    _e("DF0922", "ReadOnlyFieldError", "ObjectError",
       "Campo 'readonly' alterado depois da construcao", "oop/modificadores",
       """
Um campo 'readonly' recebe valor enquanto o objeto nasce — no padrao, no
cabecalho, no 'setup' — e depois disso nao muda. E a identidade de uma
entidade, a data de criacao, o que nao pode mudar sem virar outra coisa.
""",
       """
blueprint Pedido:
    readonly id := 0
    action setup(id):
        self.id := id         // ok: construindo

p := spawn Pedido(7)
p.id := 8                     // erro
""",
       "Crie outro objeto, ou tire o 'readonly' se o campo pode mudar de verdade."),

    _e("DF0923", "FrozenObjectError", "ObjectError",
       "Objeto congelado", "oop/objetos",
       """
'Objetos.congelar(obj)' torna a instancia imutavel: nenhum campo aceita
escrita depois disso. E o jeito de passar um objeto a outra thread, ou a
codigo que nao se controla, com a garantia de que ele volta igual.
""",
       """
adopt Arcane.Objetos as Objetos
c := spawn Config()
Objetos.congelar(c)
c.porta := 81          // erro
""",
       "Trabalhe numa copia: Objetos.clonar(c) devolve uma instancia nao congelada."),

    _e("DF0924", "MetaclassError", "ObjectError",
       "Metaclasse invalida", "oop/metaclasses",
       """
A metaclasse nomeada em 'using' nao e um 'meta blueprint', declara um
gancho que nao existe, ou conflita com a metaclasse herdada da mae.
""",
       """
meta blueprint Registro:
    action on_forje(molde):     // erro: o gancho e 'on_forge'
        out molde
""",
       "Use um dos ganchos: on_forge, on_extend, on_spawn, on_ready, on_read, "
       "on_missing, on_write, on_call, on_serialize, on_deserialize."),

    _e("DF0925", "AugmentError", "ObjectError",
       "'augment' recusado", "oop/augment",
       """
'augment' acrescenta membros a um blueprint que ja existe. Ele nao
substitui um membro existente, nao mexe num blueprint 'final', e nao
atravessa o arquivo de um 'sealed' — cada um desses quebraria uma
promessa que o blueprint original fez.
""",
       """
final blueprint Id(valor):
    action texto():
        yield str(self.valor)

augment Id:              // erro: final
    action dobro():
        yield self.valor * 2
""",
       "Escreva uma acao que recebe o objeto, ou tire o 'final' do original."),

    _e("DF0926", "DependencyResolutionError", "ObjectError",
       "Dependencia sem registro no conteiner", "oop/injecao",
       """
O conteiner precisou construir um objeto e um parametro do construtor
pede um tipo que ninguem registrou.
""",
       """
adopt Arcane.Injecao as DI
c := DI.conteiner()
c.unico(Servico)          // Servico pede um Repositorio
c.resolver(Servico)       // erro: Repositorio nao esta registrado
""",
       "Registre o tipo que falta, ou de um padrao ao parametro para torna-lo opcional."),

    _e("DF0927", "CircularDependencyError", "DependencyResolutionError",
       "Dependencia circular", "oop/injecao",
       """
A construcao de A precisa de B, e a de B precisa de A. Nao ha ordem que
construa os dois, e a mensagem mostra a cadeia inteira para saber por
onde quebra-la.
""",
       """
blueprint A(b: B):
    x := 1
blueprint B(a: A):
    x := 1
""",
       "Quebre o ciclo com c.preguicoso(Tipo), ou extraia o que os dois dividem."),

    _e("DF0928", "UnsafeDeserializationError", "ObjectError",
       "Tipo nao autorizado na desserializacao", "oop/objetos",
       """
'Objetos.de_vault' so reconstroi os tipos que voce listou. Um dado que
vem de fora com '$tipo' apontando para outro blueprint e recusado: e
assim que uma desserializacao vira execucao de codigo alheio.
""",
       """
Objetos.de_vault(json_de_fora, [Pedido])   // o dado pede 'Admin': erro
""",
       "Liste o tipo, se ele e esperado; se nao e, o dado nao e confiavel."),

    # ═══ 10xx — concorrencia ══════════════════════════════

    _e("DF1001", "ConcurrencyError", RAIZ,
       "Erro de concorrencia", "referencia/concorrencia",
       """
Familia dos erros de thread, canal e execucao assincrona.
""",
       """
monitor:
    esperar(tarefas)
handle ConcurrencyError as e:
    out e.message
""",
       "A mensagem especifica diz qual foi o problema."),

    _e("DF1002", "ChannelClosedError", "ConcurrencyError",
       "Canal fechado", "referencia/concorrencia",
       """
Enviar para um canal fechado nao entrega a ninguem. Receber de um canal
fechado e vazio devolve 'void'.
""",
       """
given canal.aberto():         // certo: verifica antes
    canal.enviar(x)
""",
       "Verifique 'aberto()' antes de enviar."),

    _e("DF1003", "ChannelFullError", "ConcurrencyError",
       "Canal cheio", "referencia/concorrencia",
       """
O canal tem capacidade limitada e o envio nao bloqueante nao coube.
""",
       """
canal.enviar(x, esperar := yes)   // bloqueia ate caber
""",
       "Aumente a capacidade, ou envie bloqueando."),

    _e("DF1004", "ThreadError", "ConcurrencyError",
       "Falha ao criar ou juntar thread", "referencia/concorrencia",
       """
A thread nao pode ser criada, ou 'juntar' foi chamado sobre uma que
nunca comecou.
""",
       """
t := thread(trabalhar)
t.juntar()
""",
       "Inicie a thread antes de juntar; reduza a quantidade simultanea."),

    _e("DF1005", "DataRaceError", "ConcurrencyError",
       "Acesso concorrente detectado", "referencia/concorrencia",
       """
Duas threads escreveram na mesma estrutura sem coordenacao. DataForge
nao tem mutex: a coordenacao e feita por canal.
""",
       """
canal.enviar(resultado)       // certo: cada thread envia
""",
       "Passe valores por canal em vez de compartilhar estrutura."),

    _e("DF1006", "DeadlockError", "ConcurrencyError",
       "Espera circular", "referencia/concorrencia",
       """
Duas ou mais threads esperam umas pelas outras e nenhuma avanca.
""",
       """
canal.receber(tempo_limite := 5)   // certo: prazo para desistir
""",
       "Estabeleca uma ordem unica de espera, ou use tempo limite."),

    _e("DF1007", "AwaitError", "ConcurrencyError",
       "'await' sobre valor nao aguardavel", "referencia/concorrencia",
       """
'await' precisa de uma tarefa. Sobre um valor comum, nao ha o que
esperar.
""",
       """
t := async buscar()
r := await t                  // certo
""",
       "Crie a tarefa com 'async' antes de aguardar."),

    # ═══ 11xx — sistema ═══════════════════════════════════

    _e("DF1101", "IOError_", RAIZ,
       "Falha de entrada e saida", "referencia/sistema",
       """
Familia dos erros de arquivo, diretorio, processo e ambiente.
""",
       """
monitor:
    conteudo := ler_arquivo(caminho)
handle IOError as e:
    out "nao deu para ler:", e.message
""",
       "A mensagem especifica diz qual operacao falhou."),

    _e("DF1102", "FileNotFoundError_", "IOError_",
       "Arquivo nao encontrado", "referencia/sistema",
       """
O caminho nao existe. Caminhos relativos partem do diretorio de onde o
programa foi executado, nao de onde o arquivo '.df' esta.
""",
       """
out caminho_absoluto("dados.csv")   // mostra onde ele procura
""",
       "Confira o caminho, e de onde o programa foi executado."),

    _e("DF1103", "PermissionError_", "IOError_",
       "Permissao negada", "referencia/sistema",
       """
O sistema recusou a leitura, a escrita ou a execucao.
""",
       """
given pode_escrever(caminho):
    escrever_arquivo(caminho, dados)
""",
       "Ajuste as permissoes, ou escolha outro caminho."),

    _e("DF1104", "IsADirectoryError_", "IOError_",
       "Esperava arquivo, veio diretorio", "referencia/sistema",
       """
A operacao e de arquivo e o caminho aponta para uma pasta.
""",
       """
cycle f in listar(pasta):     // certo: percorre a pasta
    out ler_arquivo(f)
""",
       "Aponte para um arquivo, ou percorra a pasta com 'listar'."),

    _e("DF1105", "FileExistsError_", "IOError_",
       "Arquivo ja existe", "referencia/sistema",
       """
A criacao exclusiva encontrou o caminho ocupado.
""",
       """
escrever_arquivo(caminho, dados, sobrescrever := yes)
""",
       "Escolha outro nome, ou permita a sobrescrita."),

    _e("DF1106", "DiskFullError", "IOError_",
       "Sem espaco em disco", "referencia/sistema",
       """
A escrita nao coube. O arquivo pode ter ficado pela metade.
""",
       """
out espaco_livre(".")
""",
       "Libere espaco e reescreva o arquivo inteiro."),

    _e("DF1107", "ProcessError", "IOError_",
       "Falha ao executar processo", "referencia/sistema",
       """
O comando nao existe, nao pode ser executado, ou saiu com codigo
diferente de zero.
""",
       """
r := executar("ls", ["-la"])
out r.codigo, r.saida
""",
       "Confira o comando e o codigo de saida antes de usar o resultado."),

    _e("DF1108", "EnvironmentError_", "IOError_",
       "Variavel de ambiente ausente", "referencia/sistema",
       """
Uma variavel obrigatoria nao esta definida. Costuma ser configuracao que
falta no ambiente de execucao, nao erro de codigo.
""",
       """
chave := ambiente("API_KEY") ?? trigger "defina API_KEY"
""",
       "Defina a variavel, ou de um padrao com '??'."),

    _e("DF1109", "PathError", "IOError_",
       "Caminho invalido", "referencia/sistema",
       """
O caminho tem caracteres que o sistema nao aceita, e longo demais, ou
tenta sair de uma raiz permitida.
""",
       """
caminho := juntar_caminho(base, nome)   // certo: monta com seguranca
""",
       "Monte caminhos com 'juntar_caminho' em vez de concatenar texto."),

    _e("DF1110", "SerializationError", "IOError_",
       "Falha ao serializar", "referencia/sistema",
       """
O valor tem algo que nao vira JSON, ou tem um ciclo: uma estrutura que
aponta para si mesma nao termina de escrever.
""",
       """
out para_json(dados)          // erro se 'dados' tem ciclo ou acao
""",
       "Remova acoes e ciclos antes de serializar."),

    _e("DF1111", "ParseDataError", "IOError_",
       "Dados mal formados", "referencia/sistema",
       """
O texto nao e JSON, CSV, TOML ou YAML valido. A mensagem diz a linha e a
coluna dentro do dado.
""",
       """
monitor:
    dados := de_json(texto)
handle ParseDataError as e:
    out "JSON invalido:", e.message
""",
       "Valide a origem do dado; a posicao esta na mensagem."),

    # ═══ 12xx — dados ═════════════════════════════════════

    _e("DF1201", "DatabaseError", RAIZ,
       "Erro de banco de dados", "referencia/banco-de-dados",
       """
Familia dos erros de conexao, consulta, transacao e mapeamento. Vale
para todos os bancos que o Forge suporta.
""",
       """
monitor:
    usuarios := db.consultar("select * from usuarios")
handle DatabaseError as e:
    out e.type, e.message
""",
       "A mensagem especifica diz qual camada falhou."),

    _e("DF1202", "ConnectionError_", "DatabaseError",
       "Falha ao conectar", "referencia/banco-de-dados",
       """
O servidor nao respondeu, recusou, ou o endereco esta errado.
""",
       """
db := Forge.conectar("postgres://usuario@localhost/app")
""",
       "Confira endereco, porta e se o servico esta no ar."),

    _e("DF1203", "AuthenticationError", "DatabaseError",
       "Credenciais recusadas", "referencia/banco-de-dados",
       """
Usuario ou senha invalidos, ou o metodo de autenticacao do servidor e
outro.
""",
       """
db := Forge.conectar(ambiente("DATABASE_URL"))
""",
       "Confira as credenciais; guarde-as em variavel de ambiente."),

    _e("DF1204", "QueryError", "DatabaseError",
       "Consulta invalida", "referencia/banco-de-dados",
       """
O SQL tem erro de sintaxe, ou cita tabela ou coluna que nao existe. A
mensagem traz o retorno do servidor.
""",
       """
db.consultar("select nome from usuarios where id = ?", [id])
""",
       "Teste a consulta no cliente do banco; confira nomes de coluna."),

    _e("DF1205", "TransactionError", "DatabaseError",
       "Falha de transacao", "referencia/banco-de-dados",
       """
Confirmar ou desfazer fora de uma transacao aberta, ou aninhar
transacoes onde o banco nao suporta.
""",
       """
db.transacao(lambda t => t.executar("update ..."))
""",
       "Use 'transacao' com bloco: ela confirma e desfaz sozinha."),

    _e("DF1206", "ConstraintError", "DatabaseError",
       "Restricao violada", "referencia/banco-de-dados",
       """
Chave unica repetida, chave estrangeira sem destino, ou 'not null' com
nulo. A mensagem nomeia a restricao.
""",
       """
monitor:
    Usuario.criar({"email": email})
handle ConstraintError:
    out "e-mail ja cadastrado"
""",
       "Verifique antes de inserir, ou trate a violacao como caso previsto."),

    _e("DF1207", "MigrationError", "DatabaseError",
       "Falha de migracao", "referencia/orm",
       """
Uma migracao falhou no meio, ou o historico do banco nao bate com o dos
arquivos.
""",
       """
dataforge db migrar --estado
""",
       "Veja o estado, corrija a migracao e rode de novo."),

    _e("DF1208", "SchemaError", "DatabaseError",
       "Esquema incompativel", "referencia/orm",
       """
O modelo declara colunas que a tabela nao tem, ou de tipo diferente.
""",
       """
dataforge db verificar        // compara modelo e tabela
""",
       "Gere e aplique a migracao que falta."),

    _e("DF1209", "RecordNotFoundError", "DatabaseError",
       "Registro nao encontrado", "referencia/orm",
       """
'buscar!' exige que o registro exista. A versao sem '!' devolve 'void'.
""",
       """
u := Usuario.buscar(id)       // void se nao existe
u := Usuario.buscar!(id)      // erro se nao existe
""",
       "Use a versao sem '!' quando a ausencia e prevista."),

    _e("DF1210", "PoolExhaustedError", "DatabaseError",
       "Pool de conexoes esgotado", "referencia/banco-de-dados",
       """
Todas as conexoes estao em uso e a espera passou do limite. Costuma ser
conexao aberta e nao devolvida.
""",
       """
with db.conexao() as c:       // certo: devolve sozinha
    c.consultar("select 1")
""",
       "Use 'with' para devolver a conexao, ou aumente o pool."),

    _e("DF1211", "ValidationError", "DatabaseError",
       "Validacao do modelo falhou", "referencia/orm",
       """
Um campo nao passou nas regras declaradas no modelo. A mensagem lista
todos os campos com problema, nao so o primeiro.
""",
       """
monitor:
    Usuario.criar(dados)
handle ValidationError as e:
    cycle f in e.campos:
        out f.campo, f.motivo
""",
       "Corrija os campos listados em 'e.campos'."),

    _e("DF1212", "SerializationMismatchError", "DatabaseError",
       "Tipo do banco nao mapeia", "referencia/orm",
       """
A coluna tem um tipo que o modelo nao sabe converter, ou o valor
gravado nao cabe no tipo declarado.
""",
       """
campo criado_em: DataHora     // certo: tipo do Forge
""",
       "Declare o tipo do Forge correspondente, ou converta na consulta."),

    # ═══ 13xx — rede ══════════════════════════════════════

    _e("DF1301", "NetworkError", RAIZ,
       "Erro de rede", "referencia/kiln",
       """
Familia dos erros de HTTP, socket e servidor Kiln.
""",
       """
monitor:
    r := Http.get(url)
handle NetworkError as e:
    out e.type, e.message
""",
       "A mensagem especifica diz qual camada falhou."),

    _e("DF1302", "HttpError", "NetworkError",
       "Resposta HTTP de erro", "referencia/kiln",
       """
O servidor respondeu com codigo 4xx ou 5xx. O corpo e o codigo ficam no
erro.
""",
       """
monitor:
    r := Http.get(url)
handle HttpError as e:
    out e.codigo, e.corpo
""",
       "Trate por codigo; 4xx e o pedido, 5xx e o servidor."),

    _e("DF1303", "DnsError", "NetworkError",
       "Nome nao resolvido", "referencia/kiln",
       """
O nome do host nao virou endereco: dominio errado, ou sem DNS.
""",
       """
out resolver("exemplo.com")
""",
       "Confira o dominio e a conectividade."),

    _e("DF1304", "TlsError", "NetworkError",
       "Falha de TLS", "referencia/kiln",
       """
Certificado invalido, expirado, ou de um nome diferente do pedido.
""",
       """
Http.get(url, verificar_tls := yes)   // padrao, e o certo
""",
       "Corrija o certificado do servidor; nao desligue a verificacao."),

    _e("DF1305", "RouteNotFoundError", "NetworkError",
       "Rota nao registrada", "referencia/kiln",
       """
Nenhuma rota do servidor casa com o caminho e o metodo pedidos.
""",
       """
route GET "/usuarios/:id":
    respond usuario(params.id)
""",
       "Registre a rota, ou confira o metodo HTTP."),

    _e("DF1306", "MiddlewareError", "NetworkError",
       "Falha no middleware", "referencia/kiln",
       """
Um middleware falhou, ou nao chamou o proximo nem respondeu — a
requisicao ficaria pendurada.
""",
       """
middleware registrar(req, proximo):
    out req.caminho
    yield proximo(req)        // certo: passa adiante
""",
       "Chame 'proximo(req)' ou responda; nunca os dois, nunca nenhum."),

    _e("DF1307", "TemplateError", "NetworkError",
       "Falha ao renderizar", "referencia/kiln",
       """
O template nao existe, tem sintaxe invalida, ou usa uma variavel que o
contexto nao tem.
""",
       """
render "usuarios/lista.html" with {"usuarios": us}
""",
       "Confira o caminho do template e as chaves do contexto."),

    _e("DF1308", "SessionError", "NetworkError",
       "Sessao invalida", "referencia/kiln",
       """
O cookie de sessao esta ausente, expirado, ou nao passa na verificacao
de assinatura.
""",
       """
given req.sessao.valida():
    out req.sessao["usuario"]
""",
       "Verifique a sessao antes de ler; renove quando expirar."),

    _e("DF1309", "PortInUseError", "NetworkError",
       "Porta ocupada", "referencia/kiln",
       """
Outro processo ja escuta nessa porta. Costuma ser uma execucao
anterior do proprio servidor que nao encerrou, ou outro servico
usando a mesma porta.
""",
       """
server porta := 8080
ignite porta := 8081          // certo: outra porta
""",
       "Escolha outra porta, ou encerre o processo que a ocupa."),

    _e("DF1310", "PayloadError", "NetworkError",
       "Corpo da requisicao invalido", "referencia/kiln",
       """
O corpo nao e do tipo declarado, esta mal formado, ou passa do tamanho
maximo.
""",
       """
route POST "/usuarios":
    dados := req.json()       // erro se o corpo nao e JSON
""",
       "Valide 'content-type' e o tamanho antes de interpretar."),

    _e("DF1311", "CorsError", "NetworkError",
       "Origem nao permitida", "referencia/kiln",
       """
A origem da requisicao nao esta na lista de origens aceitas.
""",
       """
server cors := ["https://meusite.com"]
""",
       "Acrescente a origem a lista, com o protocolo completo."),

    _e("DF1312", "RateLimitError", "NetworkError",
       "Limite de requisicoes", "referencia/kiln",
       """
O cliente passou do numero de requisicoes permitido na janela.
""",
       """
middleware limite(req, proximo):
    given contagem(req.ip) bigger 100:
        respond 429, "devagar"
    yield proximo(req)
""",
       "Espere a janela reabrir, ou ajuste o limite."),

    # ═══ 14xx — testes (Crucible) ═════════════════════════

    _e("DF1401", "TestError", RAIZ,
       "Erro do framework de testes", "referencia/crucible",
       """
Familia dos erros do Crucible: assercoes, fixtures, mocks e execucao da
suite.
""",
       """
monitor:
    rodar_suite()
handle TestError as e:
    out e.message
""",
       "A mensagem especifica diz qual parte do teste falhou."),

    _e("DF1402", "ExpectationError", "TestError",
       "Expectativa nao satisfeita", "referencia/crucible",
       """
Um 'expect' falhou. A mensagem mostra o esperado e o obtido, com a
diferenca destacada quando sao estruturas.
""",
       """
expect(total).to_be(10)
expect(lista).to_contain("a")
""",
       "Corrija o codigo, ou a expectativa, conforme o caso."),

    _e("DF1403", "FixtureError", "TestError",
       "Falha na fixture", "referencia/crucible",
       """
Uma fixture falhou ao preparar ou ao limpar. Falha na preparacao pula os
testes que dependem dela; na limpeza, contamina os proximos.
""",
       """
fixture banco():
    d := abrir_temporario()
    provide d
    d.fechar()                // certo: limpeza depois do 'provide'
""",
       "Garanta que preparacao e limpeza rodam mesmo com erro no teste."),

    _e("DF1404", "MockError", "TestError",
       "Uso invalido de mock", "referencia/crucible",
       """
Um mock recebeu chamada que nao foi programada, ou uma expectativa de
chamada nao se cumpriu.
""",
       """
m := mock(Servico)
m.quando("buscar").devolve([])
expect(m).chamado("buscar", vezes := 1)
""",
       "Programe a chamada, ou ajuste a expectativa."),

    _e("DF1405", "SuiteError", "TestError",
       "Falha na suite", "referencia/crucible",
       """
A suite nao pode ser montada: arquivo sem testes, nome repetido, ou
'describe' aninhado sem corpo.
""",
       """
dataforge test --listar       // mostra o que foi descoberto
""",
       "Confira os nomes e a descoberta com '--listar'."),

    _e("DF1406", "SnapshotError", "TestError",
       "Snapshot divergente", "referencia/crucible",
       """
A saida mudou em relacao ao snapshot gravado. A diferenca vem no
relatorio.
""",
       """
dataforge test --atualizar-snapshots
""",
       "Revise a diferenca; atualize o snapshot se a mudanca e desejada."),

    _e("DF1407", "FlakyTestError", "TestError",
       "Teste instavel", "referencia/crucible",
       """
O teste passou e falhou entre repeticoes com a mesma entrada. Costuma
depender de tempo, de ordem, ou de estado que sobrou de outro teste.
""",
       """
dataforge test --repetir=10
""",
       "Isole o estado; nao dependa de ordem nem de relogio."),

    _e("DF1408", "CoverageError", "TestError",
       "Cobertura abaixo do minimo", "referencia/crucible",
       """
A cobertura ficou abaixo do piso configurado. O relatorio lista as
linhas nao alcancadas.
""",
       """
dataforge test --cobertura --minimo=80
""",
       "Cubra as linhas listadas, ou ajuste o piso conscientemente."),

    # ═══ 15xx — validacao ═════════════════════════════════

    _e("DF1501", "ContractError", RAIZ,
       "Contrato violado", "referencia/contratos",
       """
Familia das pre-condicoes, pos-condicoes e invariantes declaradas.
""",
       """
action sacar(v):
    requires v bigger 0
    ensures self.saldo bigger_eq 0
""",
       "A mensagem diz qual clausula falhou e com que valores."),

    _e("DF1502", "PreconditionError", "ContractError",
       "Pre-condicao violada", "referencia/contratos",
       """
Um 'requires' recebeu falso na entrada da acao. A culpa e de quem
chamou.
""",
       """
action raiz(x):
    requires x bigger_eq 0
    yield sqrt(x)
""",
       "Valide o argumento antes de chamar."),

    _e("DF1503", "PostconditionError", "ContractError",
       "Pos-condicao violada", "referencia/contratos",
       """
Um 'ensures' recebeu falso na saida. A culpa e da acao, nao de quem
chamou.
""",
       """
action normalizar(xs):
    ensures len(resultado) is len(xs)
""",
       "Corrija a implementacao: ela nao cumpre o que promete."),

    _e("DF1504", "InvariantError", "ContractError",
       "Invariante quebrada", "referencia/contratos",
       """
Uma condicao que deveria valer sempre deixou de valer depois de um
metodo.
""",
       """
blueprint Conta:
    invariant self.saldo bigger_eq 0
""",
       "Reveja os metodos que alteram o estado citado."),

    _e("DF1505", "SchemaValidationError", "ContractError",
       "Dado fora do esquema", "referencia/validacao",
       """
O valor nao casa com o esquema declarado. O relatorio aponta o caminho
ate o campo com problema.
""",
       """
monitor:
    validar(dados, EsquemaUsuario)
handle SchemaValidationError as e:
    out e.caminho, e.motivo
""",
       "Corrija o dado, ou afrouxe o esquema se a regra e restritiva demais."),

    _e("DF1506", "RegexError", "ContractError",
       "Expressao regular invalida", "referencia/strings",
       """
O padrao nao compila: grupo sem fechar, quantificador sem alvo, classe
mal formada.
""",
       """
out casa(texto, "[a-z")       // erro: classe sem fechar
out casa(texto, "[a-z]")      // certo
""",
       "Confira o padrao; a posicao do problema vem na mensagem."),

    _e("DF1507", "DateTimeError", "ContractError",
       "Data ou hora invalida", "referencia/datas",
       """
A data nao existe (31 de fevereiro), o formato nao bate, ou o fuso e
desconhecido.
""",
       """
d := data("2026-02-30")       // erro: nao existe
d := data("2026-02-28")       // certo
""",
       "Confira o valor e o formato de entrada."),

    _e("DF1508", "UnitError", "ContractError",
       "Unidades incompativeis", "referencia/validacao",
       """
Operacao entre grandezas de unidades diferentes sem conversao.
""",
       """
out 10.metros + 5.segundos    // erro
out 10.metros + 5.metros      // certo
""",
       "Converta para a mesma unidade antes de operar."),

    _e("DF1509", "CurrencyError", "ContractError",
       "Moedas diferentes", "referencia/validacao",
       """
Somar valores em moedas diferentes sem taxa de conversao produziria um
numero sem significado.
""",
       """
out dinheiro(10, "BRL") + dinheiro(5, "USD")   // erro
""",
       "Converta com uma taxa explicita antes de somar."),

    _e("DF1510", "PrecisionError", "ContractError",
       "Perda de precisao recusada", "referencia/validacao",
       """
A conversao perderia digitos significativos, e o contexto pediu
precisao exata — tipico de dinheiro.
""",
       """
out decimal("0.1") + decimal("0.2")   // certo: exato
out 0.1 + 0.2                          // 0.30000000000000004
""",
       "Use 'decimal' para dinheiro, nao ponto flutuante."),
    # ═══ 16xx — dominio ═══════════════════════════════════
    #
    # DDD e um conjunto de distincoes, e o valor delas esta em serem
    # cobradas. Um agregado que levanta 'RuntimeError' e uma distincao
    # que nao chega a quem escreve o 'handle': para o programa acima,
    # violar uma invariante e dividir por zero viram a mesma coisa.

    _e("DF1601", "DomainError", "RuntimeError_",
       "Regra do dominio recusou a operacao", "dominio",
       """
A base da familia. 'handle DomainError' pega tudo que o modelo de
dominio recusa — valor invalido, escrita fora de comando, unidade ja
confirmada — sem listar os nove casos.
""",
       """
monitor:
    pedido.acrescentar("cafe", -1)
handle DomainError as e:
    out $"o dominio recusou: {e.message}"
""",
       "Capture o especifico quando precisar distinguir; a base quando nao."),

    _e("DF1602", "ValueObjectError", "DomainError",
       "Objeto de valor recusado ou alterado", "dominio/valores",
       """
Um objeto de valor e imutavel e nasce completo: dois valores iguais sao
o MESMO valor, e mudar um deles mudaria o outro para quem os comparou.
A regra dele e cobrada na criacao — o unico ponto em que ela pode
impedir o valor errado de existir.
""",
       """
dez := Dinheiro(10, "BRL")
dez.quantia := 99        // erro: objeto de valor nao muda
Dinheiro(-5, "BRL")      // erro: a regra recusou
""",
       "Crie outro com '.com(campo := valor)'; ou corrija o valor."),

    _e("DF1603", "IdentityError", "DomainError",
       "Falta identidade", "dominio/valores",
       """
Um repositorio guarda agregados e entidades, que tem id. Um objeto de
VALOR nao tem — e nao tem porque dois iguais sao o mesmo.
""",
       """
D.repositorio("Dinheiro").guardar(Dinheiro(10, "BRL"))   // erro
""",
       "Se voce precisa distinguir duas instancias iguais, e uma entidade."),

    _e("DF1604", "AggregateError", "DomainError",
       "Escrita fora de comando, ou invariante violada", "dominio/agregados",
       """
O agregado e a unica porta de escrita. Se qualquer um escreve, a
invariante nao vale nada — nao ha onde cobra-la. E ela e conferida na
SAIDA de cada comando: cobrar na entrada deixaria o objeto quebrado
quando o comando falha no meio.

Um comando recusado e desfeito por inteiro, e a versao nao avanca.
""",
       """
pedido.mudar(total := -1)        // erro: so muda dentro de um comando
pedido.descontar(999)            // erro: violou 'o total nunca e negativo'
""",
       "Declare o comando: mark @agregado.comando(\"nome\")."),

    _e("DF1605", "EventError", "DomainError",
       "Fato do passado alterado", "dominio/eventos",
       """
Um evento ja aconteceu. Muda-lo e reescrever a historia — quem ja
reagiu a ele reagiu ao que estava escrito antes.
""",
       """
e := D.evento("PedidoPago", {"valor": 120})
e.valor := 0        // erro
""",
       "Publique um evento novo, que corrige o efeito do anterior."),

    _e("DF1606", "SpecificationError", "DomainError",
       "A regra de negocio estourou", "dominio/contextos",
       """
A condicao quebrou ao ser avaliada. Isso e um bug DELA, e nao um alvo
que nao a satisfaz: devolver 'nao vale' recusaria o usuario por um
defeito do codigo, calado.
""",
       """
r := D.regra("maior", lambda p => p.idadee bigger_eq 18)   // typo
r.vale(pessoa)      // erro: a regra 'maior' estourou
""",
       "Corrija a condicao; 'por_que_nao' so responde sobre regra sadia."),

    _e("DF1607", "RepositoryError", "DomainError",
       "O agregado pedido nao existe", "dominio/valores",
       """
'exigir' afirma que ele existe, e levanta quando nao acha. 'por_id'
devolve void — as duas perguntas existem, e uma so obrigaria metade das
chamadas a tratar um void que nunca acontece.
""",
       """
pedidos.exigir("PED-404")     // erro
pedidos.por_id("PED-404")     // void
""",
       "Use 'por_id' quando a ausencia for um desfecho normal."),

    _e("DF1608", "UnitOfWorkError", "DomainError",
       "A unidade de trabalho ja terminou", "dominio/eventos",
       """
Uma unidade confirmada ja publicou os eventos, e quem reagiu a eles nao
tem como voltar atras. Uma desfeita descartou tudo.
""",
       """
u.confirmar()
u.desfazer()        // erro: nao da para desfazer o confirmado
""",
       "Abra outra com D.unidade(); para reverter, publique compensacao."),

    _e("DF1609", "BoundedContextError", "DomainError",
       "Falta a traducao para atravessar a fronteira", "dominio/contextos",
       """
O 'Cliente' de Vendas tem limite de credito; o de Suporte tem plano e
chamados. Sem traducao, o modelo de fora entra inteiro — e o de dentro
passa a ter campos que so existem porque o outro time os tem.
""",
       """
suporte.receber("Vendas", "Cliente", cliente)   // erro
""",
       "suporte.traduzir_de(\"Vendas\", \"Cliente\", acao)"),

    _e("DF1610", "AggregateVersionError", "DomainError",
       "Outro escreveu no fluxo antes de voce", "dominio/fonte-de-eventos",
       """
O fluxo de eventos estava na versao que voce leu quando a decisao foi
tomada, e nao esta mais. Gravar assim mesmo aplicaria um comando sobre
um estado que ja nao existe — o controle de concorrencia OTIMISTA recusa
em vez de sobrescrever.
""",
       """
lido := armazem.versao("pedido-1")            // 3
armazem.anexar("pedido-1", [e1])              // outro processo: 4
armazem.anexar("pedido-1", [e2], lido)        // erro: esperava 3, esta 4
""",
       "Leia de novo, reconstitua o agregado e reaplique o comando."),

    # ═══ 17xx — reativo ═══════════════════════════════════

    _e("DF1701", "ReactiveError", "RuntimeError_",
       "Falha num grafo reativo", "reativo",
       """
A base da familia: sinal, derivado, efeito e observavel.
""",
       """
monitor:
    total.ler()
handle ReactiveError as e:
    out e.message
""",
       "Capture o especifico quando precisar distinguir."),

    _e("DF1702", "ReactiveCycleError", "ReactiveError",
       "Um derivado depende de si mesmo", "reativo/sinais",
       """
A cadeia estouraria a pilha. A mensagem traz o caminho inteiro porque
dizer so 'ha um ciclo' manda procurar em toda a formula — e o ciclo mais
curto e o mais facil de quebrar.
""",
       """
// erro: o derivado 'a' depende de si mesmo.
//   nota: a cadeia: a -> b -> a
""",
       "Quebre o ciclo: um dos dois precisa ser um sinal."),

    _e("DF1703", "ReactiveWriteError", "ReactiveError",
       "Escrita durante o calculo de um derivado", "reativo/sinais",
       """
A formula de um derivado e lida para descobrir de QUE ela depende.
Escrever de dentro dela faz a propagacao correr no meio da propria
descoberta: o grafo muda enquanto esta sendo percorrido, e o resultado
depende da ordem em que as dependencias foram visitadas.
""",
       """
steady total := R.derivado(lambda => (contador.escrever(1) ?? 0))
total.ler()    // erro
""",
       "Um derivado so LE. Para reagir a uma mudanca, use um efeito."),

    _e("DF1704", "StreamClosedError", "ReactiveError",
       "Emissao num fluxo ja encerrado", "reativo/observaveis",
       """
'encerrar' e definitivo: quem estava inscrito ja foi avisado do fim e
cancelou a inscricao. Emitir depois disso entregaria um valor a ninguem,
em silencio.
""",
       """
cliques.encerrar()
cliques.emitir(x)    // erro
""",
       "Abra outro observavel; um fluxo encerrado nao reabre."),

    # ═══ 18xx — memoria estruturada ═══════════════════════

    _e("DF1801", "LayoutError", "RuntimeError_",
       "O layout binario nao fecha", "estruturas",
       """
A base da familia: estruturas de layout fixo, campos, ponteiros e
janelas sobre bytes.
""",
       """
monitor:
    Cabecalho.ler(dados)
handle LayoutError as e:
    out e.message
""",
       "Capture o especifico quando precisar distinguir."),

    _e("DF1802", "BufferOverflowError", "LayoutError",
       "A leitura ou escrita passa do fim do bloco", "estruturas",
       """
Um registro de 16 bytes lido a partir do byte 10 de um bloco de 20
leria 6 bytes que nao sao dele. Numa linguagem sem essa conferencia, o
resultado e lixo com cara de dado — e o erro aparece tres camadas
adiante, num campo que nao tem nada a ver.
""",
       """
Registro.ler(bloco, offset := 10)   // erro: precisa de 16, ha 10
""",
       "Confira 'len(bloco) - offset' antes, ou leia menos campos."),

    _e("DF1803", "AlignmentError", "LayoutError",
       "Campo desalinhado para o tipo", "estruturas",
       """
Um inteiro de 4 bytes comeca num multiplo de 4; um de 8, num multiplo
de 8. O desalinhamento nao e teoria: e o que faz o mesmo arquivo ser
lido de um jeito aqui e de outro no C que o escreveu.
""",
       """
E := Est.definir("Pacote", [["a", "u8"], ["b", "u32"]], empacotado := no)
// 'b' comeca em 4, e nao em 1 — ha 3 bytes de enchimento
""",
       "Declare 'empacotado := yes' para o layout sem enchimento."),

    _e("DF1804", "NullPointerError", "LayoutError",
       "Ponteiro nulo desreferenciado", "estruturas",
       """
Diferente de 'NullReferenceError', que fala de um 'void' da linguagem:
aqui o endereco existe e vale zero. Desreferencia-lo num ambiente sem
protecao seria a falha de segmentacao classica.
""",
       """
p := Est.nulo()
p.ler()     // erro
""",
       "Confira 'p.e_nulo()' antes de ler."),

    _e("DF1805", "DanglingPointerError", "LayoutError",
       "Ponteiro para um bloco que ja foi liberado", "estruturas",
       """
O bloco morreu e o endereco continua na mao de alguem. E a classe de
defeito que mais custa a achar, porque o programa segue rodando e le o
que ocupou aquele espaco depois.
""",
       """
b := Est.bloco(64)
b.liberar()
p.ler()     // erro: o bloco de 'p' foi liberado
""",
       "Use 'Arcane.Posse' quando o dono precisa ser um so."),
    _e("DF1901", "SecurityError", "RuntimeError_",
       "A base da familia de seguranca", "seguranca",
       """
Entrada hostil recusada, assinatura que nao confere, prazo vencido,
segredo achado onde nao podia, politica que disse nao, cadeia de
auditoria que nao fecha. Capture esta para tratar 'o pedido foi
recusado por seguranca' sem distinguir o motivo.
""",
       """
monitor:
    Seg.url_segura(vinda_de_fora)
handle SecurityError as e:
    out e.message
""",
       "Capture o especifico quando a resposta ao usuario for diferente."),

    _e("DF1902", "UnsafeInputError", "SecurityError",
       "A entrada pede o que nao pode ser servido", "seguranca/entrada",
       """
Um caminho que sai da pasta base, uma URL que aponta para a rede
interna, um redirecionamento para fora do site, um JSON fundo demais.
O nome do erro diz que a recusa foi DELIBERADA: o valor chegou de
fora e nao passou na conferencia.
""",
       """
Seg.caminho_seguro("uploads/", "../../etc/passwd")   // erro
""",
       "Nao conserte a entrada: recuse o pedido e registre a tentativa."),

    _e("DF1903", "SignatureError", "SecurityError",
       "A assinatura nao confere com o conteudo", "seguranca/tokens",
       """
O valor foi alterado depois de assinado, ou foi assinado com outra
chave. Sao a mesma resposta de proposito: dizer qual dos dois foi
entrega informacao a quem esta tentando.
""",
       """
Seg.ler_assinado(token_mexido, chave)    // erro
""",
       "Trate como pedido invalido. Nao leia o conteudo mesmo assim."),

    _e("DF1904", "ExpiredTokenError", "SecurityError",
       "A assinatura confere, e o prazo venceu", "seguranca/tokens",
       """
Separado de 'SignatureError' porque a resposta ao usuario e outra:
aqui o link era legitimo e caducou, e a acao certa e oferecer outro.
Num token adulterado, oferecer outro seria ajudar quem tenta.
""",
       """
Seg.ler_assinado(link_de_ontem, chave, prazo := 3600)    // erro
""",
       "Ofereca gerar um novo link; nao estenda o prazo do antigo."),

    _e("DF1905", "SecretLeakError", "SecurityError",
       "Um segredo aparece onde ele nao pode estar", "seguranca/segredos",
       """
Chave de API, token, senha ou bloco de chave privada num texto que vai
ser gravado, commitado, enviado ou mostrado. A varredura acha pelo
FORMATO, entao ela acha o que voce esqueceu — e nao so o que voce
lembra de procurar.
""",
       """
Seg.exigir_sem_segredo(fonte)     // erro: chave da Stripe na linha 12
""",
       "Tire o valor do arquivo, ponha num '.env' ignorado, e ROTACIONE."),

    _e("DF1906", "PolicyError", "SecurityError",
       "A politica recusou", "seguranca/senha",
       """
Senha curta demais, sem variedade, igual a uma conhecida, ou entropia
abaixo do minimo. A mensagem diz o que falta, e nao apenas que faltou:
uma recusa sem o motivo faz a pessoa tentar de novo no escuro.
""",
       """
Seg.exigir_politica("123456")     // erro: curta, e esta na lista
""",
       "Mostre 'e.nota', que traz a lista do que falta."),

    _e("DF1907", "AuditChainError", "SecurityError",
       "A cadeia de auditoria nao fecha", "seguranca/auditoria",
       """
Cada registro carrega o resumo do anterior. Se um deles foi alterado
ou removido, o proximo deixa de bater — e o erro diz em qual linha a
cadeia quebrou. Um registro de auditoria que pode ser editado sem
deixar marca nao e registro de auditoria.
""",
       """
livro.conferir()     // erro: a cadeia quebra no registro 41
""",
       "Guarde a trilha fora da maquina que a escreve."),

    _e("DF1908", "AuthorizationError", "SecurityError",
       "A politica recusou o acesso", "seguranca/autorizacao",
       """
Diferente de 'PolicyError', que fala de uma politica de SENHA: aqui a
pergunta era "este sujeito pode esta acao neste recurso?", e a
resposta foi nao. O motivo vem em 'e.nota', e ele diz QUAL regra
decidiu — uma recusa sem o motivo e impossivel de auditar e quase
impossivel de depurar.
""",
       """
monitor:
    P.exigir(usuario, "pedido:apagar", pedido)
handle AuthorizationError as e:
    out e.nota      // "negacao explicita da regra 'somente-dono'"
""",
       "Responda 404 quando a existencia do recurso ja e informacao."),

    _e("DF1909", "DelegationError", "SecurityError",
       "A delegacao nao vale", "seguranca/autorizacao",
       """
Vencida, revogada, ou de quem nao tinha a permissao para delegar.
Ninguem delega o que nao tem: sem essa conferencia, uma cadeia de
delegacoes cria autoridade do nada.
""",
       """
P.delegar(ana, bruno, ["pedido:aprovar"], prazo := 3600)
// ... 2 horas depois
P.pode(bruno, "pedido:aprovar", p)     // no: a delegacao venceu
""",
       "Delegacao sem prazo e concessao de permissao com passos a mais."),

    _e("DF1910", "CryptoKeyError", "SecurityError",
       "A chave criptografica nao pode ser usada", "seguranca/chaves",
       """
Vencida, revogada, ou de um proposito diferente do pedido. Uma chave
que assina token nao decifra arquivo: separar os propositos e o que
impede um comprometimento virar todos os comprometimentos.
""",
       """
Ch.usar(chave, "assinar")    // erro: esta chave e de 'cifrar'
""",
       "Gere uma chave por proposito, e rotacione por prazo."),
]


#: Indice por codigo, para busca direta.
POR_CODIGO = {e["codigo"]: e for e in ERROS}

#: Indice por nome de classe.
POR_CLASSE = {e["classe"]: e for e in ERROS if e["classe"]}


def familia(codigo):
    """O nome da familia a que um codigo pertence."""
    FAMILIAS = {
        "01": "sintaxe", "02": "execucao", "03": "tipos", "04": "nomes",
        "05": "modulos", "06": "colecoes", "07": "do usuario",
        "08": "limites", "09": "objetos", "10": "concorrencia",
        "11": "sistema", "12": "dados", "13": "rede", "14": "testes",
        "15": "validacao", "16": "dominio", "17": "reativo",
        "18": "memoria estruturada", "19": "seguranca",
    }
    return FAMILIAS.get(codigo[2:4], "desconhecida")
