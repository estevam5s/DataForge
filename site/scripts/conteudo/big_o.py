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
 {"p": "A [extensão do VS Code](/docs/tecnicas/editor) mostra a classe acima de cada ação, enquanto se escreve. O motivo aparece no hover, e o comando *Analisar complexidade* abre o relatório completo."},
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
 {"callout": {"tipo": "nota", "titulo": "O(?) não é erro", "texto": "Significa que a análise não conseguiu provar a ordem, não que o código esteja errado. Nos 200 exercícios da linguagem, zero ficam indeterminados."}},

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
]
