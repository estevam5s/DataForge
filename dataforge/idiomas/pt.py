# -*- coding: utf-8 -*-
"""O catalogo em portugues do Brasil.

Ele nasceu dentro de 'idioma.py', que so sabia pt e en. Mora aqui desde
que a camada passou a aceitar N idiomas: um catalogo por arquivo e o
que permite alguem contribuir uma traducao sem tocar no nucleo — e o
que torna possivel carregar uma de fora, por 'DF_IDIOMA_CAMINHO'.

Duas formas, porque as mensagens tem duas formas.

INTEIRAS casa a mensagem TODA ('fullmatch'), que e o caso da grande
maioria e o mais seguro: nao ha como uma traducao escapar para dentro de
um texto que por acaso contenha a frase.

PEDACOS troca um trecho, para as mensagens compostas — a do modulo nao
encontrado carrega a lista da biblioteca inteira no fim, e a nota de um
erro de comparacao carrega a frase do CPython.

Os grupos sao NOMEADOS, e o molde os usa por nome. Numerado, inverter
dois campos numa traducao passaria calado.
"""

INTEIRAS = (
    # ── Nomes ──
    (r"'(?P<n>.+)' is not defined\.",
     "'{n}' não está definido."),
    (r"'(?P<n>.+)' is a reserved keyword and cannot be assigned to\. "
     r"Pick another name\.",
     "'{n}' é palavra reservada e não pode receber valor. Escolha outro nome."),
    (r"'(?P<n>.+)' is steady and cannot be reassigned\.",
     "'{n}' é steady e não pode ser reatribuído."),
    (r"'(?P<n>.+)' was read before it was assigned\.",
     "'{n}' foi lido antes de receber valor."),

    # ── Colecoes ──
    (r"Key \"(?P<k>.*)\" is not in this vault\.",
     'A chave "{k}" não está neste vault.'),
    (r"Index (?P<i>-?\d+) is out of range for a cluster of (?P<n>\d+) items?\.",
     "O índice {i} está fora do alcance de um cluster de {n} item(ns)."),
    (r"A (?P<t>\w+) cannot be indexed\.",
     "Um {t} não aceita índice."),
    (r"An (?P<t>\w+) cannot be indexed\.",
     "Um {t} não aceita índice."),
    (r"Cannot cycle over (?P<t>\w+): expected a Cluster, Vault or String",
     "Não se pode percorrer um {t}: era esperado Cluster, Vault ou String"),
    (r"The (?P<t>\w+) is empty\.",
     "O {t} está vazio."),

    # ── Contas e operadores ──
    (r"Division by zero\.",
     "Divisão por zero."),
    (r"Cannot add Void to text\.",
     "Não se soma Void a texto."),
    (r"'(?P<op>.+)' between an? (?P<a>\w+) and an? (?P<b>\w+) "
     r"is not defined\.",
     "'{op}' entre {a} e {b} não está definido."),
    (r"'(?P<op>.+)' between an? (?P<a>\w+) and an? (?P<b>\w+) "
     r"has no answer\.",
     "'{op}' entre {a} e {b} não tem resposta."),
    (r"'(?P<op>.+)' between a Decimal and a Float is refused",
     "'{op}' entre um Decimal e um Float é recusado"),
    (r"Cannot add (?P<a>\w+) and (?P<b>\w+)",
     "Não se soma {a} com {b}"),
    (r"Cannot multiply (?P<a>\w+) by (?P<b>\w+)",
     "Não se multiplica {a} por {b}"),

    # ── Acoes ──
    (r"action '(?P<n>.+)' is missing argument\(s\): (?P<q>.+)",
     "a ação '{n}' está sem o(s) argumento(s): {q}"),
    (r"action '(?P<n>.+)' takes (?P<e>\d+) argument\(s\) but "
     r"(?P<d>\d+) (?:was|were) given",
     "a ação '{n}' recebe {e} argumento(s), e foram passados {d}"),
    (r"action '(?P<n>.+)' got an unexpected argument '(?P<a>.+)'",
     "a ação '{n}' recebeu um argumento que não conhece: '{a}'"),
    (r"Call stack exceeded (?P<n>\d+) frames in '(?P<f>.+)'\.",
     "A pilha de chamadas passou de {n} quadros em '{f}'."),

    # ── Membros ──
    (r"Record '(?P<r>.+)' has no field or method '(?P<m>.+)'\. "
     r"It has: (?P<tem>.*)",
     "O record '{r}' não tem campo nem método '{m}'. Tem: {tem}"),
    (r"Record '(?P<r>.+)' has no field '(?P<m>.+)'",
     "O record '{r}' não tem o campo '{m}'"),
    (r"Record '(?P<r>.+)' has no field\(s\): (?P<q>.+)",
     "O record '{r}' não tem o(s) campo(s): {q}"),
    (r"Record '(?P<r>.+)' is immutable: cannot assign to '(?P<m>.+)'\. "
     r"Build a changed copy with \"(?P<forma>.+)\"\.",
     "O record '{r}' é imutável: não se atribui a '{m}'. "
     'Faça uma cópia alterada com "{forma}".'),
    (r"Record '(?P<r>.+)' is missing field\(s\): (?P<q>.+)",
     "O record '{r}' está sem o(s) campo(s): {q}"),
    (r"'(?P<b>.+)' has no member '(?P<m>.+)'",
     "'{b}' não tem o membro '{m}'"),
    (r"Enum '(?P<e>.+)' has no member '(?P<m>.+)'\. Members: (?P<tem>.*)",
     "O enum '{e}' não tem o membro '{m}'. Membros: {tem}"),
    (r"Cannot access member '(?P<m>.+)' on (?:an? )?(?P<t>.+?)\.",
     "Não se acessa o membro '{m}' em {t}."),
    (r"Cannot read '(?P<m>.+)': the value is Void\.",
     "Não se lê '{m}': o valor é void."),
    (r"module '(?P<mod>.+)' has no '(?P<m>.+)'\.?",
     "o módulo '{mod}' não tem '{m}'"),

    # ── Chamada ──
    (r"Cannot call '(?P<n>.+)': the value is Void\.",
     "Não se chama '{n}': o valor é void."),
    (r"Cannot call method '(?P<n>.+)' on (?P<t>.+)\.",
     "Não se chama o método '{n}' em {t}."),
    (r"(?P<t>\w+) is not callable\.",
     "{t} não é chamável."),

    # ── Sintaxe ──
    (r"Unexpected token: (?P<t>\w+) \((?P<v>.*)\)",
     "Token inesperado: {t} ({v})"),
    (r"Expected (?P<q>.+) after (?P<onde>.+)",
     "Era esperado {q} depois de {onde}"),
    (r"Expected (?P<q>.+)",
     "Era esperado {q}"),
    (r"Tabs are not allowed for indentation\.",
     "Tabulação não é aceita no recuo."),

    # ── Modulos ──
    (r"Circular import detected: (?P<cadeia>.+)",
     "Import circular: {cadeia}"),

    # ── O conteudo das colecoes: Cluster<T>, Vault<K, V>, Set<T> ──
    # O tipo tem '<', ',' e espaco dentro, e por isso nao casa com o '\w+'
    # dos moldes de baixo — cada forma com conteudo tem o seu.
    (r"(?P<w>.+) declared as (?P<d>(?:Cluster|Vault|Set)<.+>), but "
     r"(?P<onde>.+) is (?P<o>\w+)(?P<resto>(?: — .*)?)",
     "{w} tem o tipo {d}, mas {onde} é {o}{resto}"),
    (r"(?P<w>.+) declared as (?P<d>(?:Cluster|Vault|Set)<.+>) but got (?P<o>\w+)",
     "{w} tem o tipo {d}, e recebeu {o}"),
    (r"(?P<c>(?:Cluster|Vault|Set)<.+>) only holds (?P<t>.+), and (?P<op>.+) "
     r"got (?P<o>\w+)\.",
     "{c} só guarda {t}, e {op} recebeu {o}."),
    (r"(?P<c>(?:Cluster|Vault|Set)<.+>) cannot hold (?P<o>\w+): (?P<r>.+) is (?P<o2>\w+)",
     "{c} não guarda {o}: {r} é {o2}"),
    (r"'(?P<b>\w+)<…>' is not a collection type: only Cluster<T>, Vault<K, V> "
     r"and Set<T> declare the type of what is inside\. Annotate as '(?P<b2>\w+)'\.",
     "'{b}<…>' não é uma coleção: só Cluster<T>, Vault<K, V> e Set<T> declaram "
     "o tipo do que está dentro. Anote como '{b2}'."),
    (r"(?P<f>(?:Cluster|Vault|Set)<[^>]+>) takes one type — got (?P<n>\d+) in '(?P<t>.+)'\.",
     "{f} leva um tipo — e '{t}' tem {n}."),
    (r"(?P<f>Vault<K, V>) takes two types: the key and the value — got (?P<n>\d+) "
     r"in '(?P<t>.+)'\.",
     "{f} leva dois tipos, a chave e o valor — e '{t}' tem {n}."),

    # ── Tipos declarados ──
    (r"Declared as (?P<d>\w+) but the value is (?P<o>\w+)",
     "Declarado como {d}, e o valor é {o}"),
    (r"Parameter '(?P<p>.+)' of '(?P<f>.+)' expects (?P<d>\w+) "
     r"but got (?P<o>\w+)",
     "O parâmetro '{p}' de '{f}' espera {d}, e recebeu {o}"),
    (r"Unreachable code: the block already ended above",
     "Código inalcançável: o bloco já terminou acima"),
    (r"Variable '(?P<n>.+)' is assigned but never read",
     "A variável '{n}' recebe valor e nunca é lida"),
    # A anotação vale depois da declaração (tests/test_tipo_declarado.py).
    (r"'(?P<n>.+)' was declared as (?P<d>.+), and this assigns (?P<o>.+)",
     "'{n}' foi declarado como {d}, e esta atribuição é {o}"),
    (r"Field '(?P<c>.+)' of '(?P<b>.+)' is declared as (?P<d>.+), and this "
     r"assigns (?P<o>.+)",
     "O campo '{c}' de '{b}' foi declarado como {d}, e esta atribuição é {o}"),
    (r"Assign a (?P<d>[\w.<>, |]+)", "Atribua um {d}"),

    # ── Concorrencia ──
    (r"'(?P<p>\w+)' cannot leave a '(?P<b>parallel|thread)' block\.",
     "'{p}' não pode sair de um bloco '{b}'."),
    (r"(?P<n>\d+) thread\(s\) failed\. The errors? (?:is|are) shown above\.",
     "{n} thread(s) falharam. O erro está desenhado acima."),

    # ── O que atravessa a fronteira de modulo ──
    # Estas sao variantes proprias, e nao as mesmas do arquivo unico: a
    # aridade entre modulos diz "takes N, got M" onde a local diz "takes
    # N but M were given". Traduzir uma e esquecer a outra deixa metade
    # do 'check' de um projeto modular em ingles — que e a metade que
    # mais aparece num sistema de verdade.
    (r"'(?P<n>.+)' takes (?P<e>\d+) argument\(s\), got (?P<d>\d+)",
     "'{n}' recebe {e} argumento(s), e recebeu {d}"),
)

#: Trechos, para as mensagens compostas e para nota/dica.
PEDACOS = (
    (r"^Module '(?P<m>[^']+)' not found\.",
     "Módulo '{m}' não encontrado."),
    (r"Looked in the standard library, next to (?P<a>\S+), and in "
     r"forge_modules/\.",
     "Procurei na biblioteca padrão, ao lado de {a} e em forge_modules/."),
    (r"No packages installed — try 'dataforge add <package>'\.",
     "Nenhum pacote instalado — tente 'dataforge add <pacote>'."),
    (r"Standard library:", "Biblioteca padrão:"),
    (r"Did you mean '(?P<n>[^']+)'\?", "Você quis dizer '{n}'?"),
    (r"^Fields: ", "Campos: "),
    (r"^it offers: ", "ele oferece: "),
    (r"^declared in (?P<a>.+) line (?P<l>\d+)$",
     "declarada em {a}, linha {l}"),
    (r"^It has: ", "Tem: "),
    (r"^Members: ", "Membros: "),
    (r"Pick another name\.?", "Escolha outro nome."),
    (r"^variable '(?P<n>[^']+)'", "a variável '{n}'"),
    (r"^parameter '(?P<p>[^']+)' of action '(?P<f>[^']+)'",
     "o parâmetro '{p}' da ação '{f}'"),
    (r"^return value of action '(?P<f>[^']+)'", "o valor devolvido pela ação '{f}'"),
    (r"^field '(?P<c>[^']+)' of '(?P<b>[^']+)'", "o campo '{c}' de '{b}'"),
    # O resto da frase de "<quem> declared as X but got Y". O começo tem
    # pedaço próprio (variável, parâmetro, campo, valor devolvido), e sem
    # este o relatório saía "a variável 'x' declared as Integer but got
    # String" — meio em cada idioma. Neutro de gênero ("tem o tipo"), porque
    # o sujeito pode ser a variável, o parâmetro ou o campo.
    (r" declared as (?P<d>[\w.|<>, ]+?) but got (?P<o>\w+)$",
     " tem o tipo {d}, e recebeu {o}"),
    # Pedaço, e não mensagem inteira: dentro de um 'monitor' a dica ganha
    # o sufixo "(dentro de um 'monitor' …)", e o molde inteiro não casaria.
    (r"^Assign a (?P<d>[\w.<>, |]+), or declare a new name — an annotation "
     r"holds for every assignment after it, not just the first",
     "Atribua um {d}, ou use um nome novo — a anotação vale para toda "
     "atribuição depois dela, e não só para a primeira"),
    (r"the value at key (?P<k>\S+)", "o valor na chave {k}"),
    (r"the value of the key (?P<k>\S+)", "o valor da chave {k}"),
    (r"the key (?P<k>\S+)", "a chave {k}"),
    (r"the item of (?P<m>\w+)", "o item de {m}"),
    (r"the assigned (?P<o>item|value)", "o valor atribuído"),
    (r"(?<!\w)an item(?!\w)", "um item"),
    (r"every item has to be a (?P<t>.+?)(?:;| —) (?:widen the annotation \(Any accepts "
     r"everything\) or fix the value|fix the value, or widen the annotation \(Any "
     r"accepts everything\))",
     "todo item precisa ser {t} — corrija o valor, ou alargue a anotação (Any aceita tudo)"),
    (r"every key has to be a (?P<t>.+)", "toda chave precisa ser {t}"),
    (r"insert a (?P<t>.+), or widen the annotation \(Any accepts everything\)",
     "insira um {t}, ou alargue a anotação (Any aceita tudo)"),

    # ── O que o CPython escreve, e que sobrevive a '_traduzir_tipos' ──
    # Ela troca o NOME do tipo; a frase em volta continua inglesa.
    (r"object of type '(?P<t>\w+)' has no len\(\)",
     "{t} não tem tamanho"),
    (r"must be real number, not (?P<t>\w+)",
     "precisa de um número real, e recebeu {t}"),
    (r"bad operand type for abs\(\): '(?P<t>\w+)'",
     "abs() não se aplica a {t}"),
    (r"can't multiply sequence by non-(?P<t>\w+)",
     "não se repete uma sequência por algo que não é {t}"),
    (r"unsupported operand type\(s\) for (?P<op>\S+): '(?P<a>\w+)' and "
     r"'(?P<b>\w+)'",
     "'{op}' não se aplica entre {a} e {b}"),
    (r"'(?P<op>\S+)' not supported between instances of '(?P<a>\w+)' and "
     r"'(?P<b>\w+)'",
     "'{op}' não se aplica entre {a} e {b}"),

    (r"^first: ", "o primeiro: "),
    (r"\ba caught error \((?P<t>\w+)\)", "um erro capturado ({t})"),
    (r"\bcaught error \((?P<t>\w+)\)", "erro capturado ({t})"),
    (r"to catch the error with 'handle', use 'parallel', which waits for "
     r"its statements",
     "para pegar o erro com 'handle', use 'parallel', que espera as "
     "instruções"),
    (r"each statement of 'parallel' runs in its own thread, so there is no "
     r"loop or action around it to end",
     "cada instrução de 'parallel' roda na própria thread, e não há laço "
     "nem ação em volta para encerrar"),
    (r"decide inside the statement, or move the loop out of 'parallel'",
     "decida dentro da instrução, ou tire o laço de dentro do 'parallel'"),

    # ── Os rotulos da seta, sob o trecho de codigo ──
    (r"^key read here$", "a chave foi lida aqui"),
    (r"^nothing to read$", "não há o que ler"),
    (r"^out of range$", "fora do alcance"),
    (r"^used here$", "usado aqui"),

    # ── Notas ──
    (r"this name was never assigned in any enclosing scope",
     "este nome nunca recebeu valor em nenhum escopo ao redor"),
    (r"the vault has (?P<n>\d+) keys?:",
     "o vault tem {n} chave(s):"),
    (r"valid indexes go from (?P<a>-?\d+) to (?P<b>-?\d+), or "
     r"(?P<c>-?\d+) to (?P<d>-?\d+) from the end",
     "os índices válidos vão de {a} a {b}, ou de {c} a {d} a partir do fim"),
    (r"the right side evaluated to 0",
     "o lado direito resultou em 0"),
    (r"the (?P<lado>left|right) side evaluated to 'void'",
     "o lado {lado} resultou em 'void'"),
    (r"something before this returned 'void'",
     "algo antes disto devolveu 'void'"),
    (r"Only Cluster, Vault, String and record accept \[ \]\.",
     "Só Cluster, Vault, String e record aceitam [ ]."),
    (r"'steady' declares a value that never changes",
     "'steady' declara um valor que nunca muda"),

    # ── Dicas ──
    (r"use  valor \?\? padrao  for a fallback, or check first with  "
     r"vault\.has\(chave\)",
     "use  valor ?? padrao  para um padrão, ou confira antes com  "
     "vault.has(chave)"),
    (r"use  x\[-1\]  for the last item",
     "use  x[-1]  para o último item"),
    (r"guard the divisor first:",
     "proteja o divisor antes:"),
    (r"assign it before using:",
     "atribua antes de usar:"),
    (r"remember DataForge assigns with ':=', not '='",
     "lembre que DataForge atribui com ':=', não com '='"),
    (r"Pass a (?P<t>\w+)", "Passe {t}"),
    (r"Build it as ", "Construa como "),
    (r"Call it as ", "Chame como "),
    (r"use  \?\.  to stop safely:", "use  ?.  para parar em segurança:"),
    (r"or a default:", "ou um padrão:"),
    (r"Remove this line or move it before the "
     r"'yield'/'halt'/'skip'",
     "Remova esta linha, ou mova-a para antes do 'yield'/'halt'/'skip'"),
    (r"Remove it, or rename it to '(?P<n>[^']+)' to say it is on purpose",
     "Remova-a, ou renomeie para '{n}' para dizer que é de propósito"),
    (r"Check the divisor before dividing",
     "Confira o divisor antes de dividir"),
    (r"\(inside a 'monitor' or 'expect', so this is only a warning\)",
     "(dentro de um 'monitor' ou 'expect', por isso é só um aviso)"),
)
