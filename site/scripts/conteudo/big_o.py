"""As páginas de complexidade (Big-O)."""

PAGINAS = [
{
"href": "/docs/big-o",
"title": "Complexidade e Big-O",
"description": "Quanto o seu código cresce — e como o DataForge mede isso sem rodar nada.",
"blocos": [
 {"p": "Um algoritmo que funciona com dez itens pode não terminar com um milhão. **Big-O é a linguagem para falar disso antes de descobrir na produção.**"},
 {"p": "O DataForge analisa complexidade de dentro: `dataforge big-o` lê a árvore do seu programa e diz a classe de cada ação — e o motivo. Não é uma calculadora à parte; é o mesmo compilador que roda o código."},
 {"code": """action comuns(xs, ys):
    saida := []
    cycle x in xs:
        given x in ys:
            saida.append(x)
    yield saida""", "lang": "df"},
 {"code": """$ dataforge big-o exemplo.df -v

  ▲ comuns                     O(n^2)      tempo   O(n) espaco
      · 'cycle … in 'xs'' na linha 3 anda uma vez por item
      · 'in' na linha 4 percorre a colecao (use um vault para O(1))
      ⚠ O(n^2): dobrar a entrada quadruplica o tempo.
        se um dos lacos so procura um item, um vault faz isso em O(1)""", "lang": "bash"},
 {"callout": {"tipo": "dica", "titulo": "O porquê vem junto", "texto": "`O(n²)` sozinho não ajuda a melhorar nada. O relatório sempre diz **onde** e **o que fazer** — é a diferença entre um número e uma ferramenta."}},

 {"h2": "As curvas"},
 {"p": "A tabela diz que O(n²) é pior que O(n log n). O gráfico mostra *quanto* — e é isso que decide projeto. Clique nas classes para comparar; arraste para mudar o tamanho da entrada."},
 {"componente": "curvas-big-o"},

 {"h2": "O que cada classe custa"},
 {"p": "Os números não são decorativos. É a diferença entre \"isso é lento\" e \"isso não termina antes do almoço\":"},
 {"componente": "escala-big-o"},
 {"p": "Um O(n²) com um milhão de itens são 10¹² operações — cerca de **onze dias** a um milhão de operações por segundo. O mesmo problema em O(n log n) são 20 milhões: **vinte segundos**."},

 {"h2": "Linear contra logarítmica, vendo"},
 {"p": "A busca linear olha caixa por caixa. A binária descarta metade a cada passo. Com 32 itens a diferença já aparece; com um milhão, é 1.000.000 contra 20."},
 {"componente": "corrida-busca"},

 {"h2": "O que Big-O não diz"},
 {"p": "Três coisas que a notação deliberadamente ignora, e que às vezes decidem a escolha:"},
 {"list": [
   "**A constante.** O(n) com constante 1000 perde de O(n²) com constante 1 até n=1000. Big-O é sobre crescimento, não sobre velocidade.",
   "**A memória.** Um algoritmo O(n log n) que aloca uma cópia pode perder para um O(n²) que trabalha no lugar, quando a memória é o gargalo.",
   "**O caso médio.** O(n²) é o pior caso do quicksort; o médio é O(n log n), e é ele que se observa. Ver [melhor, médio e pior caso](/docs/big-o/casos)."]},
 {"callout": {"tipo": "nota", "titulo": "Meça também", "texto": "A análise diz como o custo cresce. `dataforge profile` diz quanto ele é hoje, no seu computador, com os seus dados. As duas coisas respondem perguntas diferentes, e você precisa das duas."}},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/big-o/classes", "title": "As classes", "desc": "de O(1) a O(n!), com exemplo em DataForge de cada uma"},
   {"href": "/docs/big-o/analisar", "title": "Analisar o seu código", "desc": "o comando, as opções, e o que ele consegue e não consegue provar"},
   {"href": "/docs/big-o/padroes", "title": "Padrões e como melhorar", "desc": "os cinco jeitos mais comuns de escrever um O(n²) sem querer"},
   {"href": "/docs/big-o/estruturas", "title": "Custo das estruturas", "desc": "cluster, vault, string — o que cada operação custa"},
   {"href": "/docs/big-o/casos", "title": "Melhor, médio e pior", "desc": "e a análise amortizada, que explica por que 'append' é O(1)"},
   {"href": "/docs/big-o/espaco", "title": "Complexidade de espaço", "desc": "trocar tempo por memória, e quando vale"}]},

 {"h2": "Indo mais fundo"},
 {"p": "As seis acima cobrem o que se usa todo dia. Estas vão ao método, e aos casos que decidem arquitetura:"},
 {"cards": [
   {"href": "/docs/big-o/recorrencias", "title": "Recorrências e Teorema Mestre", "desc": "como se resolve o custo de uma função que chama a si mesma"},
   {"href": "/docs/big-o/amortizada", "title": "Análise amortizada", "desc": "por que 'append' é O(1) mesmo copiando a lista de vez em quando"},
   {"href": "/docs/big-o/limites", "title": "Ω, Θ e limites inferiores", "desc": "o que algoritmo nenhum pode fazer melhor — e como escapar disso"},
   {"href": "/docs/big-o/estruturas-avancadas", "title": "Estruturas avançadas", "desc": "heap, união-busca, deque e contador, com o custo de cada uma"},
   {"href": "/docs/big-o/paralelo", "title": "Complexidade em paralelo", "desc": "trabalho, profundidade e o teto de Amdahl — medido"},
   {"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "quando o melhor no papel perde na máquina, com medição"},
   {"href": "/docs/big-o/dados", "title": "Complexidade em dados e I/O", "desc": "banco, disco e rede: quando a unidade de custo deixa de ser a operação"}]},
]},

{
"href": "/docs/big-o/classes",
"title": "As classes de complexidade",
"description": "De O(1) a O(n!) — cada uma com um exemplo que roda.",
"blocos": [
 {"p": "Cada classe abaixo tem um exemplo em DataForge que você pode rodar, e o comando que confirma a análise."},

 {"h2": "O(1) — constante"},
 {"p": "O tamanho da entrada não muda o tempo. Ler um índice, ler uma chave de vault, somar dois números."},
 {"code": """action primeiro(xs):
    yield xs[0]

action tem_chave(v, chave):
    yield v.has(chave)

assert primeiro([9, 8, 7]) is 9
assert tem_chave({"a": 1}, "a") is yes""", "lang": "df"},
 {"p": "Um vault com um milhão de chaves responde tão rápido quanto um com três. É por isso que trocar `in cluster` por `in vault` derruba um O(n²) para O(n)."},

 {"h2": "O(log n) — logarítmica"},
 {"p": "Cada passo descarta metade do que sobrou. Vinte passos bastam para um milhão de itens."},
 {"code": """action busca_binaria(ordenada, alvo):
    baixo := 0
    alto := len(ordenada) - 1
    persist baixo smaller_eq alto:
        meio := (baixo + alto) ~/ 2
        given ordenada[meio] is alvo:
            yield meio
        orif ordenada[meio] smaller alvo:
            baixo := meio + 1
        otherwise:
            alto := meio - 1
    yield -1

assert busca_binaria([1, 3, 5, 7, 9, 11], 9) is 4
assert busca_binaria([1, 3, 5], 4) is -1""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "A entrada precisa estar ordenada", "texto": "Ordenar custa O(n log n). Buscar uma vez numa lista desordenada é O(n) — mais barato que ordenar para depois buscar. A busca binária compensa a partir da segunda busca."}},

 {"h2": "O(n) — linear"},
 {"p": "Dobrar a entrada dobra o tempo. Percorrer, somar, procurar sem índice."},
 {"code": """action maior(xs):
    given len(xs) is 0:
        trigger "cluster vazio"
    m := xs[0]
    cycle x in xs:
        given x bigger m:
            m := x
    yield m

assert maior([3, 9, 2]) is 9""", "lang": "df"},
 {"p": "Dois laços em **sequência** também são O(n): O(n) + O(n) = O(2n) = O(n). É o aninhamento que multiplica, não a repetição."},

 {"h2": "O(n log n) — linearítmica"},
 {"p": "O melhor possível para ordenar comparando elementos — há prova matemática disso. `sorted()` é O(n log n)."},
 {"code": """action ordenar_por_idade(pessoas):
    yield sorted(pessoas, chave := lambda p: p["idade"])

gente := [{"nome": "Ana", "idade": 30}, {"nome": "Bia", "idade": 25}]
assert ordenar_por_idade(gente)[0]["nome"] is "Bia\"""", "lang": "df"},
 {"p": "Merge sort e quicksort são O(n log n) por dividirem ao meio e fazerem trabalho linear em cada nível: log n níveis × n de trabalho."},
 {"code": """action merge_sort(xs):
    given len(xs) smaller_eq 1:
        yield xs
    meio := len(xs) ~/ 2
    esquerda := merge_sort(xs[:meio])
    direita := merge_sort(xs[meio:])
    yield intercalar(esquerda, direita)

action intercalar(a, b):
    saida := []
    i := 0
    j := 0
    persist i smaller len(a) and j smaller len(b):
        given a[i] smaller_eq b[j]:
            saida.append(a[i])
            i += 1
        otherwise:
            saida.append(b[j])
            j += 1
    yield [...saida, ...a[i:], ...b[j:]]

assert merge_sort([5, 2, 9, 1]) is [1, 2, 5, 9]""", "lang": "df"},

 {"h2": "O(n²) — quadrática"},
 {"p": "Dobrar a entrada quadruplica o tempo. Dois laços aninhados, comparar todos com todos."},
 {"code": """action pares_iguais(xs):
    achados := []
    cycle i from 0 to len(xs) - 1:
        cycle j from i + 1 to len(xs) - 1:
            given xs[i] is xs[j]:
                achados.append(xs[i])
    yield achados

assert pares_iguais([1, 2, 1, 3]) is [1]""", "lang": "df"},
 {"p": "Quase sempre há uma versão O(n) usando um vault. Ver [padrões e como melhorar](/docs/big-o/padroes)."},

 {"h2": "O(n³) — cúbica"},
 {"p": "Três laços aninhados. Multiplicação de matriz pelo método direto."},
 {"code": """action multiplicar(a, b, n):
    saida := [[0 cycle _ in range(n)] cycle _ in range(n)]
    cycle i from 0 to n - 1:
        cycle j from 0 to n - 1:
            cycle k from 0 to n - 1:
                saida[i][j] := saida[i][j] + a[i][k] * b[k][j]
    yield saida

m := [[1, 2], [3, 4]]
assert multiplicar(m, m, 2) is [[7, 10], [15, 22]]""", "lang": "df"},
 {"p": "Com n=1.000, são 10⁹ operações — minutos. Com n=10.000, 10¹² — dias."},

 {"h2": "O(2ⁿ) — exponencial"},
 {"p": "Cada item a mais **dobra** o custo. Recursão que se ramifica sem guardar resultado."},
 {"code": """action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)

assert fib(10) is 55""", "lang": "df"},
 {"p": "`fib(40)` faz mais de um bilhão de chamadas, quase todas repetindo cálculo já feito. Guardar o que já foi calculado derruba para O(n):"},
 {"code": """cache := {}

action fib_rapido(n):
    given n smaller 2:
        yield n
    chave := str(n)
    given cache.has(chave):
        yield cache[chave]
    resultado := fib_rapido(n - 1) + fib_rapido(n - 2)
    cache[chave] := resultado
    yield resultado

assert fib_rapido(40) is 102334155""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Memoização", "texto": "Trocar tempo exponencial por memória linear é quase sempre um bom negócio. O snippet `memo` no VS Code escreve esse padrão."}},

 {"h2": "O(n!) — fatorial"},
 {"p": "Todas as permutações. Inviável acima de uma dúzia de itens: 12! já são 479 milhões."},
 {"code": """action permutacoes(xs):
    given len(xs) smaller_eq 1:
        yield [xs]
    saida := []
    cycle i from 0 to len(xs) - 1:
        resto := [...xs[:i], ...xs[i + 1:]]
        cycle p in permutacoes(resto):
            saida.append([xs[i], ...p])
    yield saida

assert len(permutacoes([1, 2, 3])) is 6""", "lang": "df"},
 {"p": "O caixeiro-viajante por força bruta é O(n!). Para valores reais, usa-se programação dinâmica (O(2ⁿ·n²)) ou heurísticas."},

 {"h2": "Comparando"},
 {"componente": "escala-big-o"},
]},

{
"href": "/docs/big-o/analisar",
"title": "Analisar o seu código",
"description": "O comando, o que ele prova, e o que ele honestamente não prova.",
"blocos": [
 {"p": "`dataforge big-o` lê a árvore do programa e conta estrutura: quantos laços aninhados, se o contador dobra ou soma, quantas vezes uma ação chama a si mesma, e quanto custa cada função embutida que aparece."},
 {"code": """dataforge big-o programa.df           # a classe de cada ação
dataforge big-o src/ -v              # com o porquê e a sugestão
dataforge big-o src/ --strict        # sai com erro acima de O(n log n)
dataforge big-o --escala             # a tabela de referência
dataforge big-o programa.df --json   # para o editor e o CI""", "lang": "bash"},

 {"h2": "No editor"},
 {"p": "A [extensão do VS Code](/docs/editor) mostra a classe acima de cada ação, enquanto se escreve. O motivo aparece no hover, e o comando *Analisar complexidade* abre o relatório completo."},
 {"p": "É a mesma análise: a extensão chama a CLI. O que o editor mostra é exatamente o que o CI vai reprovar."},

 {"h2": "O que ele detecta"},
 {"table": {"head": ["Padrão", "Classe", "Como reconhece"], "rows": [
   ["`cycle x in xs`", "O(n)", "uma volta por item"],
   ["dois `cycle` aninhados", "O(n²)", "multiplica as ordens"],
   ["`persist` com `n ~/ 2`", "O(log n)", "a variável se divide a cada volta"],
   ["`persist` com `n -= 1`", "O(n)", "avança de um em um"],
   ["`cycle i from 1 to 10`", "O(1)", "limites constantes"],
   ["`sorted(xs)`", "O(n log n)", "custo conhecido da embutida"],
   ["`x in xs`", "O(n)", "percorre o cluster"],
   ["`v.has(k)`", "O(1)", "vault indexa"],
   ["uma chamada recursiva, `n - 1`", "O(n)", "profundidade linear"],
   ["uma chamada recursiva, `n ~/ 2`", "O(log n)", "profundidade logarítmica"],
   ["duas chamadas, `n - 1`", "O(2ⁿ)", "ramifica sem dividir"],
   ["duas chamadas, metade cada", "O(n log n)", "divisão e conquista"],
   ["compreensão aninhada", "O(n²)", "cabe numa linha e é um laço duplo"]]}},

 {"h2": "A distinção que mais importa"},
 {"p": "Merge sort e fibonacci ingênuo têm a **mesma forma**: uma ação que chama a si mesma duas vezes. O que os separa é a entrada — metade contra n−1:"},
 {"code": """// duas chamadas sobre METADE  →  O(n log n)
action merge_sort(xs):
    given len(xs) smaller_eq 1:
        yield xs
    meio := len(xs) ~/ 2
    yield intercalar(merge_sort(xs[:meio]), merge_sort(xs[meio:]))

// duas chamadas sobre n-1  →  O(2^n)
action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)""", "lang": "df"},
 {"p": "Confundir os dois condenaria todo algoritmo de divisão e conquista. A análise olha o argumento da chamada recursiva para separá-los."},

 {"h2": "Generators têm custo por item"},
 {"p": "Um `stream action` com `persist yes` não é um laço infinito por engano — é uma sequência preguiçosa, e quem consome decide quantos itens quer. A análise reporta o custo **por item emitido**:"},
 {"code": """stream action naturais():
    n := 0
    persist yes:
        emit n
        n += 1

out naturais().take(5)""", "lang": "df"},
 {"p": "`naturais` é O(1) por item. Analisar o corpo inteiro daria O(?) para todo generator correto da linguagem."},

 {"h2": "O que ele não faz"},
 {"p": "Três limites, declarados de propósito:"},
 {"list": [
   "**Não decide o indecidível.** Saber se um laço termina é o problema da parada. Quando a análise não consegue provar, ela diz `O(?)` em vez de inventar um número.",
   "**Não segue valor.** `cycle i from 1 to k` é O(k). Se `k` vier de fora, ela usa `k` como símbolo em vez de fingir que é constante.",
   "**Não mede constante.** O(n) com constante grande pode ser mais lento que O(n²) para entrada pequena."]},
 {"callout": {"tipo": "nota", "titulo": "O(?) não é erro", "texto": "Significa que a análise não conseguiu provar a ordem, não que o código esteja errado. Nos 251 exercícios da linguagem, zero ficam indeterminados."}},

 {"h2": "No CI"},
 {"p": "`--strict` faz o comando sair com código 1 se alguma ação passar de O(n log n). É o suficiente para uma regra de projeto:"},
 {"code": """# .github/workflows/ci.yml
- name: complexidade
  run: dataforge big-o src/ --strict""", "lang": "text"},
 {"p": "Use com julgamento: há problemas cuja melhor solução conhecida é quadrática. A regra serve para o quadrático **acidental**, que é a maioria."},
]},

{
"href": "/docs/big-o/padroes",
"title": "Padrões e como melhorar",
"description": "Os cinco jeitos mais comuns de escrever um O(n²) sem querer — e a versão linear de cada um.",
"blocos": [
 {"p": "Quase todo O(n²) acidental cai num destes cinco padrões. Os cinco têm versão linear, e as cinco usam a mesma ideia: **trocar busca por indexação**."},

 {"h2": "1. `in` sobre cluster dentro de laço"},
 {"p": "O mais comum de todos. O laço está à vista; o custo do `in` não."},
 {"code": """// O(n²) — 'in' percorre 'ys' a cada item de 'xs'
action comuns_lento(xs, ys):
    saida := []
    cycle x in xs:
        given x in ys:
            saida.append(x)
    yield saida""", "lang": "df"},
 {"code": """// O(n) — o vault responde em O(1)
action comuns(xs, ys):
    indice := {}
    cycle y in ys:
        indice[str(y)] := yes

    saida := []
    cycle x in xs:
        given indice.has(str(x)):
            saida.append(x)
    yield saida

assert comuns([1, 2, 3], [2, 3, 4]) is [2, 3]""", "lang": "df"},

 {"h2": "2. Procurar dentro do laço"},
 {"code": """// O(n²) — 'index_of' percorre a cada volta
action posicoes_lento(xs, alvos):
    yield [xs.index_of(a) cycle a in alvos]""", "lang": "df"},
 {"code": """// O(n) — um índice, construído uma vez
action posicoes(xs, alvos):
    onde := {}
    cycle i, x in enumerate(xs):
        given not onde.has(str(x)):
            onde[str(x)] := i
    yield [onde[str(a)] ?? -1 cycle a in alvos]

assert posicoes(["a", "b", "c"], ["c", "a"]) is [2, 0]""", "lang": "df"},

 {"h2": "3. Ordenar dentro do laço"},
 {"code": """// O(n² log n) — ordena a cada volta
action maiores_lento(grupos):
    yield [sorted(g)[-1] cycle g in grupos]""", "lang": "df"},
 {"code": """// O(n) — 'max' não precisa ordenar
action maiores(grupos):
    yield [max(g) cycle g in grupos]

assert maiores([[3, 1], [5, 9]]) is [3, 9]""", "lang": "df"},
 {"p": "Ordenar para pegar o maior é pagar O(n log n) por uma resposta que custa O(n). Vale só quando se quer os *k* maiores, com k grande."},

 {"h2": "4. Concatenar dentro do laço"},
 {"code": """// O(n²) — cada '+' copia a string inteira
action juntar_lento(partes):
    saida := ""
    cycle p in partes:
        saida := saida + p
    yield saida""", "lang": "df"},
 {"code": """// O(n) — 'join' aloca uma vez
action juntar(partes):
    yield "".join(partes)

assert juntar(["a", "b", "c"]) is "abc\"""", "lang": "df"},
 {"p": "Vale para clusters também: `saida := [...saida, x]` dentro de um laço copia tudo a cada volta. Use `saida.append(x)`, que é O(1) amortizado."},

 {"h2": "5. Agrupar comparando todos com todos"},
 {"code": """// O(n²) — compara cada um com cada um
action agrupar_lento(itens):
    grupos := []
    cycle item in itens:
        achou := no
        cycle g in grupos:
            given g[0]["tipo"] is item["tipo"]:
                g.append(item)
                achou := yes
        given not achou:
            grupos.append([item])
    yield grupos""", "lang": "df"},
 {"code": """// O(n) — o vault agrupa direto
action agrupar(itens):
    yield itens.group_by(lambda i: i["tipo"])

dados := [{"tipo": "a", "n": 1}, {"tipo": "a", "n": 2}, {"tipo": "b", "n": 3}]
assert len(agrupar(dados)["a"]) is 2""", "lang": "df"},

 {"h2": "A ideia por trás dos cinco"},
 {"callout": {"tipo": "dica", "titulo": "Troque busca por indexação", "texto": "Um vault responde \"você tem isto?\" em O(1). Construir o índice custa O(n) uma vez; consultá-lo n vezes custa O(n). Buscar linearmente n vezes custa O(n²). A troca é sempre a mesma, e quase sempre vale."}},
 {"p": "O custo é memória: o índice ocupa O(n). Ver [complexidade de espaço](/docs/big-o/espaco) para quando essa troca **não** vale."},

 {"h2": "Encontrando os seus"},
 {"code": """dataforge big-o src/ -v | grep -A3 'O(n^2)'""", "lang": "bash"},
 {"p": "Ou deixe o editor mostrar: a extensão marca com `⟵ acima do limite` tudo o que passa de O(n log n)."},
]},

{
"href": "/docs/big-o/estruturas",
"title": "Custo das estruturas",
"description": "O que cada operação de cluster, vault e string realmente custa.",
"blocos": [
 {"p": "Escolher a estrutura certa costuma render mais que otimizar o algoritmo. Esta é a tabela que decide."},

 {"h2": "Cluster"},
 {"table": {"head": ["Operação", "Custo", "Por quê"], "rows": [
   ["`xs[i]`", "O(1)", "acesso direto pelo índice"],
   ["`xs.append(x)`", "O(1)*", "amortizado — ver [casos](/docs/big-o/casos)"],
   ["`xs.pop()`", "O(1)", "remove do fim"],
   ["`xs.pop(0)`", "O(n)", "desloca todos os outros"],
   ["`xs.insert(0, x)`", "O(n)", "idem"],
   ["`x in xs`", "O(n)", "percorre até achar"],
   ["`xs.index_of(x)`", "O(n)", "idem"],
   ["`xs.remove(x)`", "O(n)", "procura e desloca"],
   ["`len(xs)`", "O(1)", "o tamanho é guardado"],
   ["`xs[a:b]`", "O(b−a)", "copia a fatia"],
   ["`xs.sort()`", "O(n log n)", "ordenação por comparação"],
   ["`xs.reverse()`", "O(n)", "troca aos pares"],
   ["`sum(xs)`, `max(xs)`", "O(n)", "percorre uma vez"],
   ["`[...a, ...b]`", "O(n+m)", "copia os dois"]]}},
 {"callout": {"tipo": "atencao", "titulo": "`pop(0)` num laço é O(n²)", "texto": "Remover do início desloca todos os outros. Para uma fila, percorra com índice ou inverta a lista e use `pop()`."}},

 {"h2": "Vault"},
 {"table": {"head": ["Operação", "Custo", "Por quê"], "rows": [
   ["`v[chave]`", "O(1)", "tabela de espalhamento"],
   ["`v[chave] := x`", "O(1)", "idem"],
   ["`v.has(chave)`", "O(1)", "idem"],
   ["`chave in v`", "O(1)", "idem"],
   ["`v.get(chave, padrao)`", "O(1)", "idem"],
   ["`delete v[chave]`", "O(1)", "idem"],
   ["`v.keys()`", "O(n)", "monta o cluster"],
   ["`v.values()`", "O(n)", "idem"],
   ["`v.items()`", "O(n)", "idem"],
   ["`len(v)`", "O(1)", "guardado"]]}},
 {"p": "**O vault é a estrutura mais subutilizada da linguagem.** Quase todo O(n²) acidental some ao trocar uma busca linear por uma consulta de vault."},

 {"h2": "String"},
 {"table": {"head": ["Operação", "Custo", "Por quê"], "rows": [
   ["`s[i]`", "O(1)", "acesso direto"],
   ["`len(s)`", "O(1)", "guardado"],
   ["`a + b`", "O(n+m)", "cria uma string nova"],
   ["`s.contains(t)`", "O(n·m)", "compara em cada posição"],
   ["`s.split(sep)`", "O(n)", "uma passada"],
   ["`sep.join(xs)`", "O(n)", "aloca uma vez"],
   ["`s.replace(a, b)`", "O(n)", "uma passada"],
   ["`s.upper()`", "O(n)", "cria uma nova"],
   ["`s[a:b]`", "O(b−a)", "copia"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Strings são imutáveis", "texto": "Toda operação que \"muda\" uma string cria outra. `s := s + x` num laço é O(n²). Acumule num cluster e use `join` no fim."}},

 {"h2": "Record e blueprint"},
 {"table": {"head": ["Operação", "Custo"], "rows": [
   ["`p.campo`", "O(1)"],
   ["`p with {...}`", "O(k) — k campos"],
   ["`spawn X(...)`", "O(k) — k campos"],
   ["`p1 is p2` (record)", "O(k) — compara campo a campo"],
   ["chamar um método", "O(1) + o corpo"],
   ["`root.metodo()`", "O(d) — d = profundidade da herança"]]}},

 {"h2": "Escolhendo"},
 {"table": {"head": ["Você precisa de…", "Use", "Por quê"], "rows": [
   ["ordem e índice", "`Cluster`", "acesso O(1) por posição"],
   ["procurar por chave", "`Vault`", "O(1) contra O(n)"],
   ["itens únicos", "`Vault` com valor `yes`", "a chave já garante unicidade"],
   ["contar ocorrências", "`xs.tally()`", "uma passada, O(n)"],
   ["agrupar", "`xs.group_by(f)`", "uma passada, O(n)"],
   ["valor imutável", "`record`", "igualdade estrutural, serve de chave"],
   ["entidade com estado", "`blueprint`", "identidade própria"]]}},
]},

{
"href": "/docs/big-o/casos",
"title": "Melhor, médio e pior caso",
"description": "E a análise amortizada, que explica por que 'append' é O(1).",
"blocos": [
 {"p": "Big-O sozinho é ambíguo: o quicksort é O(n²) e O(n log n) ao mesmo tempo, dependendo de qual caso se fala."},

 {"h2": "Os três casos"},
 {"code": """action procurar(xs, alvo):
    cycle i, x in enumerate(xs):
        given x is alvo:
            yield i
    yield -1""", "lang": "df"},
 {"table": {"head": ["Caso", "Quando", "Custo"], "rows": [
   ["melhor", "o alvo é o primeiro item", "O(1)"],
   ["médio", "o alvo está em posição qualquer", "O(n/2) = O(n)"],
   ["pior", "o alvo não existe", "O(n)"]]}},
 {"p": "Por convenção, **Big-O sem qualificação significa pior caso**. É o que dá garantia: o programa nunca vai custar mais que isso."},

 {"h2": "Quando o médio é o que importa"},
 {"table": {"head": ["Algoritmo", "Melhor", "Médio", "Pior"], "rows": [
   ["busca linear", "O(1)", "O(n)", "O(n)"],
   ["busca binária", "O(1)", "O(log n)", "O(log n)"],
   ["quicksort", "O(n log n)", "O(n log n)", "**O(n²)**"],
   ["merge sort", "O(n log n)", "O(n log n)", "O(n log n)"],
   ["busca em vault", "O(1)", "O(1)", "**O(n)**"],
   ["bubble sort", "O(n)", "O(n²)", "O(n²)"]]}},
 {"p": "O quicksort é usado na prática apesar do pior caso O(n²), porque o médio é O(n log n) e a constante é menor que a do merge sort. O pior caso só aparece com entrada já ordenada e pivô mal escolhido."},
 {"p": "O vault é O(n) no pior caso — quando todas as chaves colidem. Na prática nunca acontece com uma função de espalhamento decente, e por isso se fala em O(1)."},

 {"h2": "Análise amortizada"},
 {"p": "`xs.append(x)` é O(1), mas nem sempre: quando o cluster enche, ele realoca e copia tudo, o que é O(n). Por que dizemos O(1)?"},
 {"p": "Porque a realocação **dobra** a capacidade. Partindo de 1, para chegar a n itens houve realocações em 1, 2, 4, 8, …, n — que somam menos de 2n cópias. Espalhando esse custo pelas n inserções, dá menos de 2 por inserção: **O(1) amortizado**."},
 {"code": """// n appends custam O(n) no total, não O(n²)
action montar(n):
    saida := []
    cycle i from 1 to n:
        saida.append(i)
    yield saida

assert len(montar(1000)) is 1000""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Amortizado ≠ médio", "texto": "Médio é sobre a distribuição das entradas. Amortizado é uma garantia sobre uma *sequência* de operações, e vale mesmo no pior caso — não depende de sorte."}},

 {"h2": "Onde isso muda a decisão"},
 {"list": [
   "**Sistema de tempo real**: o pior caso é o que conta. Um O(1) amortizado com picos O(n) pode estourar o prazo.",
   "**Serviço web**: o percentil 95 é o que o usuário sente. Por isso `Crucible.benchmark` reporta p95, não só a média.",
   "**Processamento em lote**: o médio domina; picos ocasionais se diluem."]},
 {"p": "Ver [Crucible: benchmark](/docs/crucible/relatorios) para medir isso no seu código."},
]},

{
"href": "/docs/big-o/espaco",
"title": "Complexidade de espaço",
"description": "Trocar tempo por memória, e quando isso não vale.",
"blocos": [
 {"p": "Tempo não é o único recurso. `dataforge big-o` reporta os dois:"},
 {"code": """  ● dobrar                   O(n)        tempo   O(n) espaco
  ● somar                    O(n)        tempo   O(1) espaco""", "lang": "text"},

 {"h2": "O que conta como espaço"},
 {"p": "Só a memória **adicional** que o algoritmo pede — a entrada não conta, porque ela já existia."},
 {"code": """// O(1) de espaço: uma variável, não importa o tamanho de xs
action somar(xs):
    total := 0
    cycle x in xs:
        total += x
    yield total

// O(n) de espaço: a saída cresce com a entrada
action dobrar(xs):
    saida := []
    cycle x in xs:
        saida.append(x * 2)
    yield saida

assert somar([1, 2, 3]) is 6
assert dobrar([1, 2]) is [2, 4]""", "lang": "df"},

 {"h2": "A pilha também é memória"},
 {"p": "Cada chamada recursiva ocupa um quadro. Uma recursão de profundidade n custa O(n) de espaço mesmo sem alocar nada:"},
 {"code": """// O(n) de espaço — n quadros de pilha
action soma_recursiva(n):
    given n smaller_eq 0:
        yield 0
    yield n + soma_recursiva(n - 1)

// O(1) de espaço — um laço não empilha
action soma_iterativa(n):
    total := 0
    cycle i from 1 to n:
        total += i
    yield total

assert soma_recursiva(100) is soma_iterativa(100)""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Recursão profunda estoura", "texto": "`StackOverflowError` (DF0801) aparece por volta de mil níveis. Para profundidade grande, reescreva como laço."}},

 {"h2": "A troca"},
 {"p": "O padrão que mais aparece: gastar O(n) de memória para derrubar O(n²) para O(n)."},
 {"table": {"head": ["", "Tempo", "Espaço"], "rows": [
   ["busca linear em laço", "O(n²)", "O(1)"],
   ["índice em vault", "**O(n)**", "**O(n)**"],
   ["fibonacci ingênuo", "O(2ⁿ)", "O(n)"],
   ["fibonacci com memoização", "**O(n)**", "**O(n)**"]]}},
 {"p": "Quase sempre vale. As exceções:"},
 {"list": [
   "**A entrada não cabe na memória.** Aí o algoritmo O(1) de espaço é o único possível, e processa-se em fluxo.",
   "**A memória é o gargalo.** Num contêiner com limite apertado, estourar a memória derruba o processo — enquanto ser lento só irrita.",
   "**O índice é usado uma vez só.** Construir um vault para uma consulta única custa mais que a busca linear."]},

 {"h2": "Trabalhar em fluxo"},
 {"p": "Generators processam sem materializar. Um arquivo de dez milhões de linhas cabe em O(1) de memória:"},
 {"code": """stream action pares(xs):
    cycle x in xs:
        given x % 2 is 0:
            emit x

// O(1) de espaço: um item por vez, e só os 3 primeiros são calculados
out pares(range(1000000)).take(3)""", "lang": "df"},
 {"p": "Comparado à compreensão, que aloca a lista inteira:"},
 {"code": """// O(n) de espaço — materializa um milhão de itens
todos := [x cycle x in range(1000000) given x % 2 is 0]
out len(todos)""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Preguiça é uma estratégia de memória", "texto": "`stream action` + `take(n)` é como processar mais dados do que cabem na RAM. Ver [generators](/docs/fundamentos/generators)."}},
]},

{
"href": "/docs/big-o/recorrencias",
"title": "Recorrências e o Teorema Mestre",
"description": "Como se resolve o custo de um algoritmo que chama a si mesmo — e por que o merge sort e o fibonacci ingênuo têm a mesma forma e custos opostos.",
"blocos": [
 {"p": "Um laço se conta olhando. Uma **recursão**, não: o custo dela é definido em termos de si mesmo, e resolver isso é a única parte da análise de complexidade que tem método próprio."},
 {"p": "O método cabe numa linha. Escreva quanto custa uma chamada em função do que ela delega:"},
 {"code": "T(n) = a · T(n/b) + f(n)", "lang": "text"},
 {"list": ["**a** — quantas chamadas a função faz a si mesma", "**b** — por quanto a entrada é dividida em cada uma", "**f(n)** — o trabalho que ela faz **fora** das chamadas"]},
 {"p": "Os três números estão à vista no código, e é essa leitura que o `dataforge big-o` faz por você."},
 {"h2": "Os três casos do Teorema Mestre"},
 {"p": "Compare o que a recursão multiplica (`n^log_b(a)`) com o que ela faz por nível (`f(n)`). Vence o maior dos dois; empate acrescenta um `log n`."},
 {"table": {"head": ["Caso", "Quando", "Resultado"], "rows": [["**1 — a folha domina**", "`f(n)` cresce menos que `n^log_b(a)`", "`T(n) = Θ(n^log_b(a))`"], ["**2 — empate**", "`f(n) = Θ(n^log_b(a))`", "`T(n) = Θ(n^log_b(a) · log n)`"], ["**3 — a raiz domina**", "`f(n)` cresce mais que `n^log_b(a)`", "`T(n) = Θ(f(n))`"]]}},
 {"callout": {"tipo": "nota", "titulo": "Por que `log n` aparece do nada", "texto": "Dividir por `b` até chegar a 1 leva `log_b(n)` passos. Todo `log` numa análise de complexidade vem daí — de uma quantidade que se divide, nunca de uma que se subtrai."}},
 {"h2": "As quatro formas que aparecem no código real"},
 {"p": "Quase tudo o que se escreve cai numa destas quatro. A coluna da direita é o que o `dataforge big-o` responde:"},
 {"table": {"head": ["Forma", "a, b", "Recorrência", "Classe"], "rows": [["busca binária", "1, 2", "`T(n) = T(n/2) + O(1)`", "`O(log n)`"], ["merge sort", "2, 2", "`T(n) = 2T(n/2) + O(n)`", "`O(n log n)`"], ["percorrer uma árvore", "2, 2", "`T(n) = 2T(n/2) + O(1)`", "`O(n)`"], ["fibonacci ingênuo", "2, —", "`T(n) = T(n-1) + T(n-2) + O(1)`", "`O(2^n)`"]]}},
 {"p": "A última linha é a que não tem `b`: a entrada **diminui de um em um** em vez de se dividir. É a diferença inteira entre um algoritmo que serve e um que não termina."},
 {"h2": "Uma chamada, entrada pela metade — `O(log n)`"},
 {"code": """action busca(xs, alvo, baixo, alto):
    given baixo bigger alto:
        yield -1
    meio := (baixo + alto) ~/ 2
    given xs[meio] is alvo:
        yield meio
    given xs[meio] smaller alvo:
        yield busca(xs, alvo, meio + 1, alto)
    yield busca(xs, alvo, baixo, meio - 1)

out busca([1, 3, 5, 7, 9], 9, 0, 4)     // 4""", "lang": "df"},
 {"p": "Há **duas** chamadas escritas, e só **uma** roda: elas estão em ramos mutuamente exclusivos. Contá-las como duas é o erro que transforma uma busca binária em `O(2^n)` — a análise tem de olhar o caminho, e não a árvore."},
 {"code": """$ dataforge big-o busca.df -v

  ● busca                      O(log n)    tempo   O(n) espaco""", "lang": "bash"},
 {"h2": "Duas chamadas sobre metades — `O(n log n)`"},
 {"p": "O merge sort é o caso 2 do teorema: `n^log₂(2) = n`, e a intercalação também é `O(n)`. Empate, e o resultado ganha o `log n`."},
 {"code": """action intercalar(a, b):
    saida := []
    i := 0
    j := 0
    persist i smaller len(a) and j smaller len(b):
        given a[i] smaller_eq b[j]:
            saida.append(a[i])
            i += 1
        otherwise:
            saida.append(b[j])
            j += 1
    yield [...saida, ...a[i:], ...b[j:]]

action ordenar(xs):
    given len(xs) smaller_eq 1:
        yield xs
    meio := len(xs) ~/ 2
    yield intercalar(ordenar(xs[0:meio]), ordenar(xs[meio:]))

out ordenar([5, 2, 9, 1, 7])     // [1, 2, 5, 7, 9]""", "lang": "df"},
 {"p": "A conta por níveis deixa isso visível: no topo, um trabalho de `n`; no nível seguinte, dois de `n/2` — que somam `n` de novo; e assim por `log n` níveis. **Cada nível custa `n`**, e são `log n` deles."},
 {"code": """nivel 0:                    n            = n
nivel 1:        n/2   +   n/2            = n
nivel 2:   n/4 + n/4 + n/4 + n/4         = n
   …                                       …
             log n niveis  ×  n  =  n log n""", "lang": "text"},
 {"h2": "Duas chamadas, entrada quase inteira — `O(2^n)`"},
 {"code": """action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)

out fib(12)     // 144""", "lang": "df"},
 {"p": "A forma é **idêntica** à do merge sort: duas chamadas por nível. O que muda é o `b`: aqui a entrada perde **um**, e não metade. A árvore de chamadas tem profundidade `n` em vez de `log n`, e cada nível dobra."},
 {"callout": {"tipo": "atencao", "titulo": "A diferença cabe num caractere", "texto": "`fib(n - 1)` e `ordenar(xs[0:meio])` são a mesma linha com um argumento diferente, e separam `O(2^n)` de `O(n log n)`. Com n = 50: um termina antes de você soltar a tecla, o outro leva mais de dez dias."}},
 {"h2": "Memoizar muda a recorrência, não o código"},
 {"p": "O fibonacci ingênuo recalcula `fib(30)` milhões de vezes. Guardando o que já foi calculado, cada argumento distinto roda **uma vez** — e a recorrência deixa de ser exponencial:"},
 {"code": """cache := {}

action fib_memo(n):
    given n smaller 2:
        yield n
    given cache.has(str(n)):
        yield cache[str(n)]
    valor := fib_memo(n - 1) + fib_memo(n - 2)
    cache[str(n)] := valor
    yield valor

out fib_memo(30)     // 832040""", "lang": "df"},
 {"p": "São `n` argumentos possíveis e trabalho constante em cada um: `O(n)` de tempo, `O(n)` de espaço. O `dataforge big-o` reconhece o par que caracteriza o cache — a consulta que devolve cedo, e a escrita na mesma coleção — e para de acusar exponencial."},
 {"p": "`Arcane.Functional.memoize` faz o mesmo sem o cache à mão, e `Arcane.Iter.cache_info` diz quantas vezes ele acertou."},
 {"h2": "Quando o Teorema Mestre não se aplica"},
 {"list": ["**As partes são desiguais** — `T(n) = T(n/3) + T(2n/3) + O(n)` não tem um `b` único. (O resultado ainda é `O(n log n)`, por outro caminho.)", "**`a` ou `b` mudam com `n`** — o teorema pressupõe os dois constantes.", "**A diferença entre `f(n)` e `n^log_b(a)` não é polinomial** — é a lacuna entre os casos 2 e 3, e ela existe de verdade.", "**A recursão é indireta** — `f` chama `g`, que chama `f`. Aqui a análise do DataForge cala, porque olha uma ação por vez."]},
 {"h2": "Por onde seguir"},
 {"cards": [{"href": "/docs/big-o/classes", "title": "As classes", "desc": "de O(1) a O(n!), com um exemplo que roda de cada uma"}, {"href": "/docs/big-o/amortizada", "title": "Análise amortizada", "desc": "por que 'append' é O(1) mesmo custando O(n) de vez em quando"}, {"href": "/docs/big-o/limites", "title": "Limites inferiores", "desc": "Ω, Θ, e por que nenhuma ordenação por comparação vence n log n"}]},
]},

{
"href": "/docs/big-o/amortizada",
"title": "Análise amortizada",
"description": "Por que 'append' é O(1) mesmo custando O(n) de vez em quando — e as três formas de provar isso.",
"blocos": [
 {"p": "`xs.append(x)` é `O(1)`. Só que de vez em quando ele **copia a lista inteira**, o que é `O(n)`. As duas frases são verdadeiras, e a análise amortizada é o que as concilia."},
 {"p": "A pergunta certa não é *quanto custa esta operação*, e sim **quanto custam n operações, divididas por n**. É a diferença entre a conta do mês e a conta do café."},
 {"h2": "O que acontece por dentro"},
 {"p": "Um cluster guarda um bloco de memória com espaço sobrando. Quando o espaço acaba, ele aloca um bloco **maior** — tipicamente o dobro — e copia o que havia. Essa cópia é a operação cara."},
 {"code": """capacidade:  4        8              16                      32
append:      ····     ····****       ····****········        …
                 ↑            ↑                     ↑
              copia 4      copia 8              copia 16""", "lang": "text"},
 {"p": "A cópia acontece cada vez mais raramente, e é exatamente por isso que ela some na média."},
 {"h2": "A prova pela agregação"},
 {"p": "Some o custo de `n` appends. As cópias acontecem em 1, 2, 4, 8, …, até `n` — uma série geométrica:"},
 {"code": "1 + 2 + 4 + 8 + … + n  <  2n", "lang": "text"},
 {"p": "O total das cópias é **menor que `2n`**, e somado aos `n` appends dá menos de `3n`. Dividido por `n`: uma constante. Cada `append` custa `O(1)` **amortizado**."},
 {"h2": "A prova pela medição"},
 {"p": "A conta acima é verificável sem confiar em ninguém: se o total de `n` appends é linear, dobrar `n` tem de dobrar o tempo. Dobre quatro vezes e olhe a razão."},
 {"code": """adopt Arcane.Time as T

action tempo_de_n_appends(n):
    inicio := T.monotonic()
    xs := []
    cycle i from 1 to n:
        xs.append(i)
    yield (T.monotonic() - inicio) * 1000

anterior := 0.0
cycle n in [100000, 200000, 400000, 800000]:
    ms := tempo_de_n_appends(n)
    razao := "—" given anterior is 0.0 otherwise $"{round(ms / anterior, 2)}x"
    out $"{str(n).pad_start(7)} appends  {str(round(ms, 1)).pad_start(7)} ms   {razao}"
    anterior := ms""", "lang": "df"},
 {"code": """ 100000 appends     88.2 ms   —
 200000 appends    178.2 ms   2.02x
 400000 appends    360.1 ms   2.02x
 800000 appends    724.4 ms   2.01x""", "lang": "text", "title": "saída (macOS, 10 núcleos)"},
 {"p": "**2,02x** três vezes seguidas. Se cada `append` fosse `O(n)`, dobrar `n` daria 4x; se as cópias não amortizassem, a razão subiria a cada linha. Ela não sobe."},
 {"callout": {"tipo": "dica", "titulo": "A razão, e não o tempo", "texto": "O número absoluto mede a sua máquina; a **razão entre dois tamanhos** mede o algoritmo. É por isso que os testes de complexidade deste repositório cobram fator, nunca milissegundos."}},
 {"h2": "As outras duas provas"},
 {"p": "A agregação responde \"quanto custa o total\". As outras duas respondem \"por que nunca falta\", e são o que se usa quando a estrutura é mais complicada que uma lista:"},
 {"table": {"head": ["Método", "A ideia", "Aplicado ao `append`"], "rows": [["**agregação**", "some tudo e divida por n", "menos de 3n para n appends"], ["**contábil**", "cobre a mais em cada operação barata e guarde o crédito", "cada append paga 3: um por si, dois guardados para a cópia futura"], ["**potencial**", "defina uma função Φ do estado; o custo amortizado é o real mais a variação de Φ", "Φ = 2 × (itens além da metade da capacidade)"]]}},
 {"p": "As três dão o mesmo resultado. A contábil é a mais fácil de explicar: quando o bloco de capacidade `k` enche, os `k` itens copiados já pagaram, cada um, os dois créditos que a cópia consome."},
 {"h2": "Amortizado não é o mesmo que médio"},
 {"table": {"head": ["", "Sobre o quê", "Quem garante"], "rows": [["**caso médio**", "uma distribuição de **entradas**", "a estatística — pode dar azar"], ["**amortizado**", "uma **sequência** de operações", "a álgebra — não tem azar"]]}},
 {"p": "O quicksort é `O(n log n)` no caso **médio** e `O(n²)` no pior: uma entrada infeliz custa caro. O `append` é `O(1)` **amortizado**: não existe sequência de appends que fuja disso. Ver [melhor, médio e pior](/docs/big-o/casos)."},
 {"h2": "Onde isso muda a decisão"},
 {"list": ["**Construir uma lista com `append` num laço é linear**, e não quadrático. A alternativa \"esperta\" — `saida := [...saida, x]` — **é** quadrática, porque copia a cada volta.", "**Num sistema de tempo real, o amortizado não basta.** A cópia acontece de verdade, e naquela volta o prazo estoura. Ali se pré-aloca.", "**Um vault tem a mesma história**, com um detalhe a mais: ele também cresce por realocação, e uma colisão ruim de chaves degrada a busca."]},
 {"code": """// linear: cada append é O(1) amortizado
saida := []
cycle x in fonte:
    saida.append(x)

// quadrático: cada volta copia a lista inteira
saida := []
cycle x in fonte:
    saida := [...saida, x]""", "lang": "df"},
 {"p": "O `dataforge big-o` acusa o segundo — é o [padrão 4](/docs/big-o/padroes) da lista de armadilhas."},
 {"h2": "Por onde seguir"},
 {"cards": [{"href": "/docs/big-o/estruturas", "title": "Custo das estruturas", "desc": "o que cada operação de cluster, vault e string custa"}, {"href": "/docs/big-o/casos", "title": "Melhor, médio e pior", "desc": "e por que o médio é o que se observa"}, {"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "quando o algoritmo pior no papel ganha na máquina"}]},
]},

{
"href": "/docs/big-o/limites",
"title": "Ω, Θ e limites inferiores",
"description": "O que O, Ω e Θ dizem de diferente — e por que nenhuma ordenação por comparação pode ser melhor que n log n.",
"blocos": [
 {"p": "`O` é um limite **de cima**: \"não custa mais que isto\". Ele sozinho não diz que um algoritmo é bom — dizer que a busca linear é `O(n²)` é verdade, e inútil."},
 {"p": "A família inteira tem cinco membros, e três deles aparecem em conversa de projeto:"},
 {"table": {"head": ["Notação", "Lê-se", "Significa"], "rows": [["`O(f)`", "\"ó grande\"", "cresce **no máximo** como f — limite superior"], ["`Ω(f)`", "\"ômega\"", "cresce **no mínimo** como f — limite inferior"], ["`Θ(f)`", "\"teta\"", "cresce **exatamente** como f — os dois ao mesmo tempo"], ["`o(f)`", "\"ó pequeno\"", "cresce **estritamente menos** que f"], ["`ω(f)`", "\"ômega pequeno\"", "cresce **estritamente mais** que f"]]}},
 {"callout": {"tipo": "nota", "titulo": "O que se diz na prática", "texto": "Quando alguém diz \"o merge sort é O(n log n)\", quase sempre quer dizer `Θ(n log n)` — o limite justo. `O` sozinho é o costume, e não erro: todo `Θ(f)` também é `O(f)`."}},
 {"h2": "Do algoritmo para o problema"},
 {"p": "A mudança de perspectiva que importa: `O` e `Θ` descrevem um **algoritmo**; `Ω` pode descrever o **problema**. Provar que um problema é `Ω(g)` é provar que **nenhum** algoritmo pode fazer melhor — inclusive os que ainda não foram inventados."},
 {"p": "Quando o limite inferior do problema encontra o limite superior de um algoritmo, o assunto está encerrado: ele é **ótimo**, e procurar um melhor é perda de tempo."},
 {"h2": "Nenhuma ordenação por comparação vence `n log n`"},
 {"p": "É o limite inferior mais conhecido, e a prova cabe em três linhas."},
 {"list": ["Ordenar `n` itens é escolher uma entre **n!** permutações possíveis.", "Cada comparação tem **dois** desfechos, então `k` comparações distinguem no máximo `2^k` casos.", "Para `2^k ≥ n!` é preciso `k ≥ log₂(n!)`, e `log₂(n!) ≈ n log n`.", "Logo, **toda** ordenação baseada em comparar é `Ω(n log n)`."], "ordered": True},
 {"p": "O merge sort é `O(n log n)`. Limite inferior e superior coincidem: ele é ótimo na sua classe, e nenhum truque de implementação vai derrubá-lo para `O(n)`."},
 {"h2": "Escapar do limite: não comparar"},
 {"p": "O limite vale para quem **compara**. Um algoritmo que usa o valor como **endereço** não está nessa classe, e por isso pode ser linear:"},
 {"code": """// ordenação por contagem: O(n + k), sem comparar nada.
// O preço: só serve para inteiros numa faixa conhecida.
action ordenar_contando(xs, maior):
    contagem := [0] * (maior + 1)
    cycle x in xs:
        contagem[x] += 1
    saida := []
    cycle valor, vezes in enumerate(contagem):
        cycle k from 1 to vezes:
            saida.append(valor)
    yield saida

out ordenar_contando([3, 1, 2, 3, 1], 3)     // [1, 1, 2, 3, 3]""", "lang": "df"},
 {"p": "Não há contradição: a contagem não é uma ordenação por comparação. Ela paga com a **faixa** — `k` entra no custo, e ordenar mil números entre 0 e um bilhão aloca um bilhão de posições."},
 {"callout": {"tipo": "atencao", "titulo": "E ela perde na prática, aqui", "texto": "Medido com 200 mil inteiros de 0 a 999: `sorted` levou **13,5 ms** e a contagem escrita em DataForge, **381 ms** — 28x mais lenta, sendo assintoticamente melhor. O `sorted` roda em C; a contagem roda no interpretador. É o assunto da página [A constante que decide](/docs/big-o/constantes)."}},
 {"h2": "Outros limites inferiores que decidem projeto"},
 {"table": {"head": ["Problema", "Limite", "Consequência"], "rows": [["achar o máximo de uma lista sem ordem", "`Ω(n)`", "não existe atalho: é preciso ver todos"], ["buscar num conjunto **ordenado**, por comparação", "`Ω(log n)`", "a busca binária é ótima"], ["buscar por **igualdade** com tabela de espalhamento", "`Θ(1)` médio", "por isso um vault vence um cluster"], ["ler `n` itens de disco", "`Ω(n/B)` blocos", "o custo é o **bloco**, não o item — ver [complexidade de dados](/docs/big-o/dados)"]]}},
 {"h2": "Quando não se conhece nenhum algoritmo bom"},
 {"p": "Há problemas para os quais ninguém achou solução polinomial **e** ninguém provou que ela não existe. Reconhecê-los é prático: significa parar de procurar o algoritmo esperto e começar a procurar uma aproximação."},
 {"code": """// subconjunto que soma exatamente ao alvo: O(2^n) por força bruta
action soma_exata(valores, alvo, i, atual):
    given atual is alvo:
        yield yes
    given i bigger_eq len(valores) or atual bigger alvo:
        yield no
    given soma_exata(valores, alvo, i + 1, atual + valores[i]):
        yield yes
    yield soma_exata(valores, alvo, i + 1, atual)

out soma_exata([3, 34, 4, 12, 5, 2], 9, 0, 0)     // yes""", "lang": "df"},
 {"p": "Três saídas honestas, quando o problema é desses:"},
 {"list": ["**Aproximar** — aceitar 95% da resposta em tempo polinomial.", "**Restringir** — resolver só o caso que o seu sistema realmente tem (valores pequenos, grafo esparso, n abaixo de 30).", "**Podar** — força bruta com corte, como o `atual bigger alvo` acima. Não muda a classe, muda o dia."]},
 {"h2": "Por onde seguir"},
 {"cards": [{"href": "/docs/big-o/recorrencias", "title": "Recorrências", "desc": "como se resolve o custo de uma função que chama a si mesma"}, {"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "por que o melhor no papel perde na máquina"}, {"href": "/docs/big-o/estruturas-avancadas", "title": "Estruturas avançadas", "desc": "heap, união-busca e o custo de cada escolha"}]},
]},

{
"href": "/docs/big-o/estruturas-avancadas",
"title": "Estruturas avançadas",
"description": "Heap, união-busca, deque e contador — o que cada uma custa, e o problema que só ela resolve bem.",
"blocos": [
 {"p": "Cluster e vault resolvem quase tudo. As quatro estruturas desta página existem para os casos em que eles obrigam a pagar `O(n)` por algo que podia ser `O(log n)` ou `O(1)` — e todas já vêm em [`Arcane.Collections`](/docs/biblioteca/collections)."},
 {"h2": "Heap — o menor primeiro, em `O(log n)`"},
 {"p": "Uma fila de prioridade. O que ela dá, e o cluster não: inserir e tirar o menor mantendo a ordem **sem ordenar a lista inteira**."},
 {"code": """adopt Arcane.Collections as C

h := C.heap([5, 1, 9, 3])
C.heap_push(h, 2)
out C.heap_peek(h)     // 1  — o menor, sem remover
out C.heap_pop(h)      // 1
out C.heap_pop(h)      // 2""", "lang": "df"},
 {"table": {"head": ["Operação", "Heap", "Cluster ordenado", "Cluster solto"], "rows": [["ver o menor", "`O(1)`", "`O(1)`", "`O(n)`"], ["tirar o menor", "`O(log n)`", "`O(n)` (desloca)", "`O(n)`"], ["inserir", "`O(log n)`", "`O(n)` (desloca)", "`O(1)`"], ["montar de uma lista", "`O(n)`", "`O(n log n)`", "`O(1)`"]]}},
 {"h3": "Onde isso decide: os k maiores"},
 {"p": "Ordenar tudo para pegar 10 é `O(n log n)`. Um heap de tamanho 10 é `O(n log k)` — e com k pequeno, `log k` é praticamente uma constante:"},
 {"code": """adopt Arcane.Collections as C
adopt Arcane.Time as T

dados := [randint(1, 1000000) cycle i in range(0, 300000)]

inicio := T.monotonic()
maiores_a := sorted(dados)[len(dados) - 10:]
ms_sort := (T.monotonic() - inicio) * 1000

inicio := T.monotonic()
maiores_b := C.top_n(dados, 10)
ms_heap := (T.monotonic() - inicio) * 1000

out $"ordenar tudo e cortar 10:  {round(ms_sort, 1)} ms"
out $"top_n com heap de 10:      {round(ms_heap, 1)} ms"
""", "lang": "df"},
 {"code": """ordenar tudo e cortar 10:  25.7 ms
top_n com heap de 10:      1.7 ms""", "lang": "text", "title": "saída (300 mil itens)"},
 {"p": "**15x**, e a distância cresce com `n`. `C.top_n` e `C.bottom_n` fazem isso; `C.priority_queue` é o mesmo mecanismo com prioridade explícita, que é como se escreve um Dijkstra ou um escalonador."},
 {"h2": "União-busca — \"estes dois estão no mesmo grupo?\""},
 {"p": "O problema: juntar elementos em grupos e perguntar se dois estão juntos. Com listas, cada pergunta varre tudo; a união-busca responde em tempo **quase constante**."},
 {"code": """adopt Arcane.Collections as C

uf := C.union_find(["a", "b", "c", "d"])
uf.union("a", "b")
uf.union("c", "d")
out uf.connected("a", "b")     // yes
out uf.connected("a", "c")     // no
out uf.count()                 // 2 grupos""", "lang": "df"},
 {"table": {"head": ["Operação", "Custo"], "rows": [["`union(a, b)`", "`O(log n)` amortizado"], ["`connected(a, b)`", "`O(log n)` amortizado"], ["`count()`", "`O(n)`"], ["`groups()`", "`O(n)`"]]}},
 {"p": "A compressão de caminho é o que dá o amortizado: cada busca **achata** a árvore que percorreu, e a próxima passa direto. É o mesmo raciocínio da [análise amortizada](/docs/big-o/amortizada) do `append` — a operação cara paga pelas baratas que vêm depois."},
 {"p": "Serve para componentes conexos de um grafo, para detectar ciclo ao montar uma árvore geradora mínima, e para agrupar duplicatas — \"este e-mail e este telefone são da mesma pessoa\"."},
 {"h2": "Deque — as duas pontas em `O(1)`"},
 {"p": "Um cluster é `O(1)` no fim e `O(n)` no começo: inserir na posição 0 empurra todo o resto. O deque é `O(1)` nas duas pontas."},
 {"code": """adopt Arcane.Collections as C

d := C.deque([1, 2, 3])
C.push_left(d, 0)
out C.pop_left(d)     // 0
out C.pop(d)          // 3
out len(d)            // 2""", "lang": "df"},
 {"table": {"head": ["Operação", "Deque", "Cluster"], "rows": [["no fim (push/pop)", "`O(1)`", "`O(1)`"], ["no começo (push/pop)", "`O(1)`", "**`O(n)`**"], ["por índice, no meio", "`O(n)`", "`O(1)`"]]}},
 {"p": "A troca é clara: o deque ganha nas pontas e perde no acesso indexado. Use-o para fila (BFS, produtor-consumidor) e janela deslizante; para acesso aleatório, cluster."},
 {"h2": "Contador — contar sem laço aninhado"},
 {"p": "Contar ocorrências percorrendo e comparando é `O(n²)`. Com um vault de contagem é `O(n)`, e o `counter` é isso pronto:"},
 {"code": """adopt Arcane.Collections as C

palavras := ["a", "b", "a", "c", "a"]
out C.counter(palavras)                  // {a: 3, b: 1, c: 1}
out C.most_common(palavras, 2)           // [[a, 3], [b, 1]]""", "lang": "df"},
 {"p": "`most_common(n)` usa heap por dentro: `O(n log k)`, não `O(n log n)`. As duas ideias desta página juntas."},
 {"h2": "Escolhendo em trinta segundos"},
 {"table": {"head": ["A pergunta que você faz muitas vezes", "A estrutura"], "rows": [["\"este item está aqui?\"", "**vault** — `O(1)`"], ["\"qual é o menor/maior agora?\"", "**heap** — `O(log n)`"], ["\"os k maiores de muitos\"", "**heap** (`top_n`) — `O(n log k)`"], ["\"estes dois estão no mesmo grupo?\"", "**união-busca** — quase `O(1)`"], ["\"o primeiro da fila\"", "**deque** — `O(1)`"], ["\"quantas vezes cada um aparece?\"", "**counter** — `O(n)`"], ["\"o item da posição i\"", "**cluster** — `O(1)`"], ["\"está ordenado? onde entra este?\"", "**cluster ordenado** + `binary_search` — `O(log n)`"]]}},
 {"callout": {"tipo": "dica", "titulo": "A troca é sempre a mesma", "texto": "Toda estrutura desta página acelera **uma** pergunta e desacelera outra. Escolher bem é saber qual pergunta o seu código faz num laço — e essa é a que o `dataforge big-o` aponta."}},
 {"h2": "Por onde seguir"},
 {"cards": [{"href": "/docs/big-o/estruturas", "title": "Custo das estruturas", "desc": "cluster, vault e string, operação por operação"}, {"href": "/docs/big-o/amortizada", "title": "Análise amortizada", "desc": "de onde vem o 'amortizado' da união-busca"}, {"href": "/docs/biblioteca/collections", "title": "Arcane.Collections", "desc": "a referência completa do módulo"}]},
]},

{
"href": "/docs/big-o/constantes",
"title": "A constante que decide",
"description": "Big-O ignora a constante de propósito — e é ela que decide qual código é mais rápido no tamanho que você realmente tem.",
"blocos": [
 {"p": "`O(n)` e `O(n²)` dizem como o custo **cresce**. Nenhum dos dois diz quanto o custo **é**. Entre um `O(n)` com constante mil e um `O(n²)` com constante um, o segundo ganha até n = 1000 — e muito sistema nunca passa de mil."},
 {"p": "Essa página é o contrapeso das outras: ela existe para que a análise não vire superstição."},
 {"h2": "Uma medição que prova o ponto"},
 {"p": "A ordenação por contagem é `O(n + k)`; a ordenação por comparação é `O(n log n)`. A primeira é assintoticamente melhor. Com 200 mil inteiros de 0 a 999:"},
 {"code": """comparacao (n log n): 13.5 ms
contagem   (n + k):   381.3 ms
""", "lang": "text", "title": "medido"},
 {"p": "A melhor no papel perdeu por **28x**. O motivo não é o algoritmo: `sorted` é um Timsort escrito em C, e a contagem está escrita em DataForge, interpretada. A constante de \"uma volta de laço no interpretador\" é centenas de vezes maior que a de \"uma comparação em C\"."},
 {"callout": {"tipo": "atencao", "titulo": "A regra prática", "texto": "Quando um lado roda em C e o outro no interpretador, a diferença de constante costuma engolir uma classe inteira de complexidade. Antes de reimplementar um embutido \"com um algoritmo melhor\", meça."}},
 {"h2": "E uma em que a classe ganha, com folga"},
 {"p": "O mesmo par de forças, invertido: aqui os dois lados pagam a mesma constante, e só a classe separa."},
 {"code": """adopt Arcane.Time as T

N := 50000
BUSCAS := 2000

xs := [i cycle i in range(0, N)]
v := {}
cycle i in xs:
    v[i] := yes

// procura itens AUSENTES: o pior caso da busca linear, e o caso
// honesto — um item no começo da lista sai rápido por sorte.
inicio := T.monotonic()
cycle k from 1 to BUSCAS:
    given (N + k) in xs:
        out "achou"
cluster_ms := (T.monotonic() - inicio) * 1000

inicio := T.monotonic()
cycle k from 1 to BUSCAS:
    given (N + k) in v:
        out "achou"
vault_ms := (T.monotonic() - inicio) * 1000

out $"cluster: {round(cluster_ms, 1)} ms"
out $"vault:   {round(vault_ms, 1)} ms"
out $"razao:   {round(cluster_ms / vault_ms, 1)}x"
""", "lang": "df"},
 {"code": """cluster: 255.8 ms
vault:   2.2 ms
razao:   118.5x
""", "lang": "text", "title": "saída (50 mil itens)"},
 {"p": "**118x**, e essa distância cresce com `n` — é a diferença entre `O(n)` e `O(1)`. Nenhuma constante salva a busca linear aqui, porque não há constante: há uma classe."},
 {"h2": "Como um benchmark mente"},
 {"p": "A primeira versão da medição acima dizia o **contrário** — que o cluster era 3x mais rápido que o vault. Dois erros, os dois comuns:"},
 {"table": {"head": ["O erro", "O que ele fez", "A correção"], "rows": [["procurar itens que estão no **começo**", "`in` de cluster achava na posição 1, 2, 3… e nunca percorria nada", "procurar itens **ausentes**, ou sorteados"], ["medir a **montagem** junto da busca", "construir o vault de 50 mil dominou o tempo", "montar antes, cronometrar só a busca"]]}},
 {"p": "Um benchmark que confirma o que você esperava é o mais perigoso de todos — é o que ninguém revisa. Quando o número contrariar a teoria, desconfie do número **e** da teoria, nessa ordem."},
 {"h2": "Os quatro custos que o Big-O não conta"},
 {"table": {"head": ["Custo", "Por que ele some na notação", "Quando ele decide"], "rows": [["**a constante**", "some na definição de O", "sempre que `n` é pequeno"], ["**localidade de memória**", "não é uma operação", "percorrer um cluster contíguo é muito mais rápido que seguir ponteiros, com a mesma classe"], ["**alocação**", "conta como O(1)", "um algoritmo que aloca por item perde de um que trabalha no lugar"], ["**partida**", "não depende de `n`", "criar 5 threads custa mais que 60 ms de trabalho — [ver paralelismo](/docs/big-o/paralelo)"]]}},
 {"h2": "Medir: as três ferramentas"},
 {"table": {"head": ["Ferramenta", "Responde", "Quando usar"], "rows": [["[`dataforge big-o`](/docs/big-o/analisar)", "como o custo **cresce**", "antes de escrever, e no CI"], ["[`dataforge profile`](/docs/cli/bench)", "onde o tempo **está indo** hoje", "quando já está lento e você não sabe onde"], ["[`Arcane.Bench`](/docs/tecnicas/bench)", "quanto custa **este trecho**", "para comparar duas implementações"]]}},
 {"p": "As três respondem perguntas diferentes, e nenhuma substitui as outras. O `big-o` não sabe que você só tem 200 itens; o `profile` não sabe que amanhã serão 200 mil."},
 {"h2": "A ordem em que vale a pena mexer"},
 {"list": ["**Meça.** O gargalo quase nunca está onde a intuição aponta — este interpretador já teve sete otimizações feitas assim, e nenhuma delas no lugar esperado.", "**Troque a classe primeiro.** `O(n²)` para `O(n)` ganha de qualquer ajuste de constante, se `n` crescer.", "**Depois ataque a constante**, e só no trecho que o profile apontou.", "**Meça de novo.** Uma otimização que não foi medida depois é uma hipótese, não um ganho."], "ordered": True},
 {"h2": "Por onde seguir"},
 {"cards": [{"href": "/docs/big-o/paralelo", "title": "Complexidade em paralelo", "desc": "trabalho, profundidade e o teto de Amdahl"}, {"href": "/docs/big-o/analisar", "title": "Analisar o seu código", "desc": "o comando, e o que ele consegue provar"}, {"href": "/docs/cli/bench", "title": "Medir de verdade", "desc": "profile e bench: o tempo próprio de cada ação"}]},
]},

{
"href": "/docs/big-o/paralelo",
"title": "Complexidade em paralelo",
"description": "Trabalho e profundidade, o teto de Amdahl, e por que dez núcleos não dividem o tempo por dez.",
"blocos": [
 {"p": "Com mais de um núcleo, um número só não descreve o custo. São **dois**, e a distância entre eles é o quanto o problema aceita ser dividido."},
 {"table": {"head": ["Medida", "Símbolo", "O que é"], "rows": [["**trabalho**", "`T₁`", "o total de operações — o custo com **um** processador"], ["**profundidade**", "`T∞`", "a cadeia mais longa de dependências — o custo com **infinitos** processadores"]]}},
 {"p": "O tempo com `p` processadores fica entre os dois, e nunca abaixo da profundidade: `T_p ≥ max(T₁/p, T∞)`. O **paralelismo** do algoritmo é `T₁/T∞` — quantos processadores adiantam antes de sobrar."},
 {"h2": "Somar um milhão de números"},
 {"table": {"head": ["Forma", "Trabalho `T₁`", "Profundidade `T∞`", "Paralelismo"], "rows": [["laço sequencial", "`O(n)`", "`O(n)`", "**1** — não divide"], ["soma em árvore", "`O(n)`", "`O(log n)`", "`n / log n`"]]}},
 {"p": "O mesmo trabalho, profundidades diferentes. O laço obriga cada soma a esperar a anterior; a árvore soma pares independentes e depois pares de pares. É por isso que `>> distill` é sequencial por definição e uma redução por partes não é."},
 {"h2": "O teto de Amdahl"},
 {"p": "Se uma fração `s` do programa é **inerentemente** sequencial, o ganho máximo é `1 / s`, não importa quantos núcleos existam:"},
 {"table": {"head": ["Parte sequencial", "Ganho máximo", "Com 10 núcleos"], "rows": [["0%", "∞", "10,0x"], ["5%", "20x", "6,9x"], ["10%", "10x", "5,3x"], ["25%", "4x", "3,1x"], ["50%", "2x", "1,8x"]]}},
 {"p": "Dez por cento de código sequencial já corta o ganho de dez núcleos quase pela metade. Ler o arquivo, montar a lista e imprimir o resultado contam nesses dez por cento."},
 {"h2": "O que se mede de verdade"},
 {"p": "Oito blocos de CPU numa máquina de 10 núcleos, comparando a série com processos de verdade:"},
 {"code": """adopt Arcane.Concurrent as P
adopt Arcane.Time as T

action pesado(semente):
    total := 0
    cycle i from 1 to 400000:
        total += (i * semente) % 7
    yield total

lotes := [1, 2, 3, 4, 5, 6, 7, 8]

inicio := T.monotonic()
serie := [pesado(s) cycle s in lotes]
ms_serie := (T.monotonic() - inicio) * 1000

inicio := T.monotonic()
processos := P.map_processos(pesado, lotes)
ms_proc := (T.monotonic() - inicio) * 1000

out $"serie:     {round(ms_serie, 0)} ms"
out $"processos: {round(ms_proc, 0)} ms   ({round(ms_serie / ms_proc, 2)}x)"
out $"igual: {serie is processos}"
""", "lang": "df"},
 {"code": """serie:     4069 ms
processos: 864 ms   (4.71x)
igual: yes
""", "lang": "text", "title": "saída (macOS, 10 núcleos)"},
 {"p": "**4,71x** com 8 tarefas em 10 núcleos — e não 8x. O que falta foi para a partida dos processos, a cópia dos dados e a coleta dos resultados. É a diferença entre o modelo e a máquina, e ela é sempre nessa direção."},
 {"h2": "Threads não dividem trabalho de CPU"},
 {"p": "O mesmo teste com `thread` em vez de processos dá **0,97x** — ligeiramente pior que a série. O GIL do Python deixa uma thread por vez executar bytecode: para CPU, thread não é paralelismo."},
 {"table": {"head": ["Ferramenta", "Serve para", "Ganho em CPU"], "rows": [["`thread:` / `parallel:`", "rede, disco, banco, espera", "**nenhum** — o GIL serializa"], ["`async` / `await`", "entrada e saída sobreposta", "**nenhum** em CPU, muito em I/O"], ["`P.map_processos`", "trabalho de CPU", "medido: **4,71x** em 10 núcleos"], ["`P.pool_processos()`", "CPU, muitas vezes seguidas", "evita os ~100 ms de partida por chamada"]]}},
 {"callout": {"tipo": "atencao", "titulo": "A partida também tem custo", "texto": "Iniciar um processo custa mais de cem milissegundos. Medido: 180 ms na primeira chamada de um pool, 82 ms na segunda. Se o trabalho dura menos que isso, a versão paralela perde — e é por isso que um teste de paralelismo precisa de carga suficiente para o tempo de partida sumir na conta."}},
 {"h2": "Complexidade de comunicação"},
 {"p": "Num processo separado, o dado precisa **atravessar**. Isso é custo que a versão sequencial não tem, e ele entra na conta:"},
 {"list": ["**O que atravessa é copiado.** Mandar um record de trinta campos junto de cada lote copia trinta campos por lote.", "**Por isso o pacote vai uma vez por processo**, no início, e o que cada lote leva é um índice.", "**Lote grande demais** desequilibra: um processo termina e fica ocioso enquanto o outro ainda trabalha.", "**Lote pequeno demais** paga comunicação mais vezes do que trabalha."]},
 {"p": "A regra prática: divida em algumas vezes mais lotes do que núcleos — o suficiente para equilibrar, longe o bastante de comunicar a cada item."},
 {"h2": "Por onde seguir"},
 {"cards": [{"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "por que o modelo e a máquina discordam"}, {"href": "/docs/tecnicas/concorrencia", "title": "Concorrência", "desc": "thread, parallel, canais e o que não é protegido sozinho"}, {"href": "/docs/big-o/espaco", "title": "Complexidade de espaço", "desc": "trocar tempo por memória, e quando vale"}]},
]},

{
"href": "/docs/big-o/dados",
"title": "Complexidade em dados e I/O",
"description": "Onde a unidade de custo deixa de ser a operação e passa a ser o acesso — banco, disco e rede, com medição.",
"blocos": [
 {"p": "Toda a análise das outras páginas conta **operações**, e supõe que todas custam igual. Quando o dado sai da memória, essa suposição quebra: um acesso a disco vale cem mil operações, e uma ida à rede vale dez milhões."},
 {"p": "A conta muda de unidade. O que se conta aqui não é instrução — é **ida e volta**."},
 {"table": {"head": ["Onde está o dado", "Ordem de grandeza do acesso", "Equivale a"], "rows": [["cache L1", "~1 ns", "1 operação"], ["memória principal", "~100 ns", "~100 operações"], ["SSD", "~100 µs", "~100 mil operações"], ["rede, no mesmo datacentro", "~500 µs", "~500 mil operações"], ["rede, entre continentes", "~150 ms", "~150 milhões"]]}},
 {"callout": {"tipo": "dica", "titulo": "A regra que decorre disso", "texto": "Um algoritmo `O(n^2)` que roda **na memória** costuma ganhar de um `O(n)` que vai ao banco a cada item. Antes de otimizar o laço, conte as idas."}},

 {"h2": "O N+1: o O(n) que ninguém vê"},
 {"p": "Buscar uma lista e depois, para cada item, buscar o relacionado. O código parece linear e **é** linear — em consultas, que é a unidade cara:"},
 {"code": """// N+1: uma consulta pela lista, e mais uma por cliente
soma := 0.0
cycle c in DB.select(db, "clientes"):
    linhas := DB.query(db, "SELECT total FROM pedidos WHERE cliente_id = ?", [c["id"]])
    cycle l in linhas:
        soma += l["total"]
""", "lang": "df"},
 {"code": """// uma consulta so: o banco agrupa, e volta uma vez
soma := 0.0
cycle l in DB.query(db, "SELECT cliente_id, SUM(total) AS t FROM pedidos GROUP BY cliente_id", []):
    soma += l["t"]
""", "lang": "df"},
 {"code": """N+1 (501 consultas): 6.5 ms
uma consulta:        1.0 ms
razao: 6.4x
""", "lang": "text", "title": "medido — 500 clientes, 5 mil pedidos, SQLite em memória"},
 {"p": "**6,4x** com o banco na mesma memória do processo, onde uma consulta é barata. Com o banco em outra máquina, cada uma das 501 paga uma ida à rede, e a mesma diferença vira **centenas de vezes**."},
 {"p": "É o problema de desempenho mais comum em sistema com banco, e ele não aparece em teste: com dez linhas de exemplo, as 11 consultas são instantâneas."},

 {"h2": "Índice: de O(n) para O(log n), medido"},
 {"p": "Sem índice, o banco lê a tabela inteira a cada consulta. Com índice, ele desce uma árvore. O `explain` mostra a diferença **antes** de você medir:"},
 {"code": """adopt Arcane.Database as DB
adopt Arcane.Time as T

db := DB.memory()
DB.create_table(db, "pedidos", {"id": "INTEGER PRIMARY KEY", "cliente": "TEXT", "total": "REAL"})
DB.insert_many(db, "pedidos",
    [{"cliente": $"c{i % 500}", "total": i * 1.0} cycle i in range(0, 20000)])

inicio := T.monotonic()
cycle k from 1 to 200:
    DB.query(db, "SELECT * FROM pedidos WHERE cliente = ?", [$"c{k}"])
sem_indice := (T.monotonic() - inicio) * 1000

DB.create_index(db, "pedidos", ["cliente"])

inicio := T.monotonic()
cycle k from 1 to 200:
    DB.query(db, "SELECT * FROM pedidos WHERE cliente = ?", [$"c{k}"])
com_indice := (T.monotonic() - inicio) * 1000

out $"sem indice: {round(sem_indice, 1)} ms"
out $"com indice: {round(com_indice, 1)} ms"
out $"razao: {round(sem_indice / com_indice, 1)}x"
out DB.explain(db, "SELECT * FROM pedidos WHERE cliente = ?", ["c1"])
""", "lang": "df"},
 {"code": """sem indice: 73.6 ms
com indice: 4.4 ms
razao: 16.6x
{passos: [SEARCH pedidos USING INDEX idx_pedidos_cliente (cliente=?)], varre_tabela: no, aviso: }
""", "lang": "text", "title": "saída (20 mil linhas)"},
 {"p": "Antes do índice, o mesmo `explain` responde `varre_tabela: yes` e o aviso `le a tabela inteira: SCAN pedidos`. Esse campo é o que vale procurar num CI: uma consulta que varre a tabela inteira é aceitável com mil linhas e derruba o sistema com um milhão."},

 {"h2": "O que um índice custa"},
 {"p": "Ele não é grátis, e por isso não se indexa tudo:"},
 {"table": {"head": ["Operação", "Sem índice", "Com índice"], "rows": [["buscar por aquela coluna", "`O(n)`", "`O(log n)`"], ["inserir uma linha", "`O(1)`", "`O(log n)` — **por índice**"], ["atualizar aquela coluna", "`O(1)`", "`O(log n)`"], ["espaço em disco", "—", "mais uma estrutura por índice"]]}},
 {"p": "Indexe o que aparece em `WHERE`, `JOIN` e `ORDER BY` de consulta frequente. Uma tabela de escrita pesada com seis índices paga seis árvores a cada linha inserida."},

 {"h2": "Paginar por deslocamento é quadrático"},
 {"p": "`LIMIT 20 OFFSET 100000` parece constante e não é: o banco **produz e descarta** as cem mil primeiras linhas para chegar na página. Percorrer todas as páginas assim é `O(n^2)`."},
 {"code": """// O(offset) por pagina — a ultima pagina e a mais cara
DB.query(db, "SELECT * FROM pedidos ORDER BY id LIMIT 20 OFFSET 100000", [])

// O(log n) por pagina: continua de onde parou
DB.query(db, "SELECT * FROM pedidos WHERE id > ? ORDER BY id LIMIT 20", [ultimo_id])
""", "lang": "sql"},
 {"p": "A segunda forma — paginação por cursor — exige um campo ordenado e único, e em troca cada página custa o mesmo. `DB.paginate` faz a primeira; para listas grandes e rolagem infinita, escreva a segunda."},

 {"h2": "Ler arquivo: o custo é o bloco"},
 {"p": "Disco não entrega byte, entrega **bloco**. Ler um arquivo de `n` bytes em blocos de `B` custa `O(n/B)` acessos — e é por isso que ler de mil em mil linhas ganha de ler de uma em uma, com a mesma classe assintótica."},
 {"code": """// carrega o arquivo inteiro na memoria: O(n) de espaco
linhas := IO.read_lines("grande.csv")

// um item por vez: O(1) de espaco, e o mesmo O(n) de tempo
stream action registros(caminho):
    cycle linha in IO.read_lines(caminho):
        emit split(linha, ",")
""", "lang": "df"},
 {"p": "A segunda forma processa arquivo maior que a memória quando a fonte é preguiçosa. Ver [complexidade de espaço](/docs/big-o/espaco) e [generators](/docs/fundamentos/generators)."},

 {"h2": "A lista de conferência"},
 {"list": ["**Conte as idas ao banco**, não as linhas de código. Um laço com uma consulta dentro é um N+1 até prova em contrário.", "**Rode `DB.explain` nas consultas quentes** e procure `varre_tabela: yes`.", "**`DB.watch_slow` e `DB.slow_log`** registram o que passou do prazo, em produção.", "**Agregue no banco** (`SUM`, `GROUP BY`, `DB.aggregate`): trazer mil linhas para somar em memória paga transporte por nada.", "**Use transação para escrita em lote.** Sem ela, cada `insert` confirma sozinho, e o custo é por linha.", "**Pagine por cursor** quando a lista for grande."]},

 {"h2": "Por onde seguir"},
 {"cards": [{"href": "/docs/biblioteca/database", "title": "Arcane.Database", "desc": "transação, índice, explain, paginação e busca textual"}, {"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "por que contar operações não basta"}, {"href": "/docs/big-o/espaco", "title": "Complexidade de espaço", "desc": "processar mais dados do que cabem na memória"}]},
]},
]
