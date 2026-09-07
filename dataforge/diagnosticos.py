"""
Catalogo de codigos de erro do DataForge.

Todo erro carrega um codigo estavel (DF0601). Este arquivo diz o que cada
um significa, e e o que 'dataforge explain DF0601' imprime.

A separacao importa: a mensagem do erro cabe em uma linha e aponta o
lugar; a explicacao aqui tem espaco para o porque e para o exemplo.
"""

CATALOGO = {
    # ── 01xx: sintaxe ──
    "DF0101": {
        "titulo": "Indentacao inconsistente",
        "doc": "primeiros-passos",
        "explicacao": """
DataForge usa indentacao para delimitar blocos, e aceita apenas espacos.
Um caractere de tabulacao no meio de linhas indentadas com espaco produz
um bloco que o leitor ve de um jeito e o parser ve de outro.
""",
        "exemplo": """
given x bigger 0:
    out "com espacos"
\tout "com tab"      // <- SyncError
""",
        "solucao": """
Configure o editor para inserir espacos no lugar de tab.
No VS Code:  "editor.insertSpaces": true, "editor.tabSize": 4
Depois:      dataforge fmt arquivo.df
""",
    },
    "DF0102": {
        "titulo": "Caractere inesperado",
        "doc": "referencia/gramatica",
        "explicacao": """
O lexer encontrou um simbolo que nao faz parte da linguagem.

A causa mais comum e usar '=' para atribuir. Em DataForge a atribuicao e
':=' — o '=' sozinho nao existe.
""",
        "exemplo": """
x = 10        // errado
x := 10       // certo
""",
        "solucao": "Troque '=' por ':=', ou remova o simbolo desconhecido.",
    },
    "DF0103": {
        "titulo": "Erro de sintaxe",
        "doc": "referencia/gramatica",
        "explicacao": """
O parser encontrou um token onde esperava outro. A mensagem diz o que
esperava; a coluna marca onde.

Causas frequentes:
  - falta ':' no fim de um cabecalho (given, cycle, action, blueprint)
  - parentese ou colchete sem fechar
  - 'otherwise' sem o 'given' correspondente
""",
        "exemplo": """
given x bigger 0        // falta ':'
    out "positivo"

given x bigger 0:       // certo
    out "positivo"
""",
        "solucao": "Confira o ':' e o pareamento de parenteses e colchetes.",
    },

    # ── 02xx: execucao ──
    "DF0201": {
        "titulo": "Erro em tempo de execucao",
        "doc": "erros",
        "explicacao": """
O programa foi analisado sem problema, mas falhou ao rodar. Divisao por
zero, conversao impossivel e reatribuicao de 'steady' caem aqui.
""",
        "exemplo": """
out 10 / divisor          // se divisor for 0, estoura aqui

given divisor isnt 0:     // a guarda evita
    out 10 / divisor
""",
        "solucao": """
Guarde a condicao antes, ou envolva em 'monitor':

    monitor:
        out 10 / divisor
    handle e:
        out "nao deu:", e.message
""",
    },

    # ── 03xx: tipos ──
    "DF0301": {
        "titulo": "Tipo incompativel",
        "doc": "tipos",
        "explicacao": """
Uma operacao recebeu um tipo que nao aceita, ou uma anotacao foi
contrariada.

Tambem aparece em OOP: metodo de instancia chamado no blueprint, spawn de
blueprint abstrato, escrita em propriedade so-leitura, e blueprint que
nao implementou o que o trait exige.
""",
        "exemplo": """
action dobro(n: Integer) -> Integer:
    yield n * 2

out dobro("texto")        // String onde se esperava Integer
""",
        "solucao": """
Converta antes (int, float, str), ou ajuste a anotacao.
'dataforge check .' aponta a maioria destes antes de rodar.
""",
    },

    # ── 04xx: nomes ──
    "DF0401": {
        "titulo": "Nome nao definido",
        "doc": "variaveis",
        "explicacao": """
O nome nao existe em nenhum escopo visivel deste ponto.

Quando ha algo parecido, a mensagem sugere — o caso mais comum e erro de
digitacao. Quando nao ha, geralmente o nome foi usado antes de receber
valor, ou esta em outro escopo.
""",
        "exemplo": """
contador := 0
out contadr        // DF0401: voce quis dizer 'contador'?
""",
        "solucao": """
Confira a grafia, e lembre que a atribuicao e ':=' — 'x = 1' nao cria x.
Variavel criada dentro de um bloco nao existe fora dele.
""",
    },

    # ── 05xx: modulos ──
    "DF0501": {
        "titulo": "Modulo nao encontrado",
        "doc": "pacotes",
        "explicacao": """
O 'adopt' procurou em tres lugares e nao achou:

  1. biblioteca padrao (Arcane.*)
  2. arquivos ao lado do que faz o import
  3. forge_modules/, subindo ate achar um forge.toml
""",
        "exemplo": """
adopt validador as V      // se nao instalado, DF0501
""",
        "solucao": """
Se e um pacote:            dataforge add validador
Se e um arquivo seu:       confira o caminho e o nome
Se e da stdlib:            confira a grafia (Arcane.Math, nao Arcane.math)
""",
    },

    # ── 06xx: indice e chave ──
    "DF0601": {
        "titulo": "Indice ou chave invalida",
        "doc": "colecoes",
        "explicacao": """
Leitura fora da faixa de um cluster, ou de uma chave que o vault nao tem.

Em cluster de n itens, os indices validos vao de 0 a n-1 — ou de -1 a -n
contando do fim. O erro classico e usar len(x) como indice, quando o
ultimo e len(x) - 1.
""",
        "exemplo": """
itens := [10, 20, 30]
out itens[3]        // DF0601: so ha 0, 1 e 2
out itens[-1]       // 30, o ultimo

v := {"nome": "ana"}
out v["idade"]      // DF0601: a chave nao existe
""",
        "solucao": """
Confira o tamanho antes:   given len(itens) bigger i:
Use valor de reserva:      v["idade"] ?? 0
Ou confirme a chave:       given v.has("idade"):
""",
    },

    # ── 07xx: trigger ──
    "DF0701": {
        "titulo": "Erro lancado pelo programa",
        "doc": "erros",
        "explicacao": """
Alguem chamou 'trigger'. Nao e uma falha da linguagem: e o programa
sinalizando uma condicao que ele mesmo considera invalida.
""",
        "exemplo": """
action sacar(saldo, valor):
    given valor bigger saldo:
        trigger "saldo insuficiente"
    yield saldo - valor
""",
        "solucao": """
Trate com monitor/handle:

    monitor:
        novo := sacar(100, 500)
    handle e:
        out "recusado:", e.message
""",
    },

    # ── 08xx: recursao ──
    "DF0801": {
        "titulo": "Recursao profunda demais",
        "doc": "acoes",
        "explicacao": """
A pilha passou de mil quadros. Quase sempre e recursao sem caso base, ou
com um caso base que nunca e alcancado.
""",
        "exemplo": """
action contar(n):
    yield contar(n - 1)     // nunca para

action contar(n):
    given n smaller_eq 0:   // caso base
        yield 0
    yield contar(n - 1)
""",
        "solucao": """
Confirme que o caso base existe e que cada chamada se aproxima dele.
Para profundidade grande de verdade, troque a recursao por um laco.
""",
    },
}


def buscar(codigo):
    """Aceita 'DF0601', 'df0601' ou '0601'. Devolve (codigo, dados) ou None."""
    if not codigo:
        return None
    chave = str(codigo).strip().upper()
    if not chave.startswith("DF"):
        chave = "DF" + chave.zfill(4)
    dados = CATALOGO.get(chave)
    return (chave, dados) if dados else None
