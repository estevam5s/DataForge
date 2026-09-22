# -*- coding: utf-8 -*-
"""Big-O na prática — os algoritmos clássicos, e medir em vez de supor.

As treze páginas de complexidade ensinam a TEORIA (classes, casos,
recorrências, amortização). Estas usam `Arcane.Algoritmos`, que traz os
clássicos prontos com a complexidade como dado, e `Arcane.Bench`, que
mede a curva. Nenhum bloco afirma um tempo absoluto — isso mede a
máquina, e não o algoritmo; os que medem só imprimem.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/big-o/algoritmos",
"title": "Os clássicos, prontos",
"description": "Arcane.Algoritmos — catorze algoritmos com a complexidade declarada, e conferidos contra a versão ingênua.",
"blocos": [
 {"p": "Entender por que um Dijkstra é O((V + E) log V) é uma coisa; escrevê-lo certo às três da manhã é outra. `Arcane.Algoritmos` traz os clássicos prontos, e cada um responde a sua complexidade **como dado** — e é testado contra a versão óbvia e lenta, em centenas de entradas sorteadas."},
 {"code": """adopt Arcane.Algoritmos as Alg

cycle a in Alg.catalogo():
    out $"{a['nome'].pad_end(18)} {a['tempo'].pad_end(16)} {a['nota']}"

assert Alg.complexidade("dijkstra")["tempo"] is "O((V + E) log V)"
assert len(Alg.catalogo()) is 14""", "lang": "df"},
 {"table": {"head": ["Família", "Algoritmos", "Página"], "rows": [
   ["busca", "`busca_binaria`, `limite_inferior`", "[Busca](/docs/big-o/busca)"],
   ["ordenação", "`ordenar_mesclando`, `ordenar_contando`", "[Ordenação](/docs/big-o/ordenacao)"],
   ["grafos", "`bfs`, `dfs`, `ordem_topologica`, `dijkstra`, `caminho`", "[Grafos](/docs/big-o/grafos)"],
   ["programação dinâmica", "`lcs`, `levenshtein`, `mochila`", "[Programação dinâmica](/docs/big-o/programacao-dinamica)"],
   ["texto e números", "`kmp`, `crivo`", "[Texto](/docs/big-o/texto)"]]}},
 {"callout": {"tipo": "dica", "titulo": "Por que conferido contra a versão ingênua", "texto": "Testar um algoritmo com os exemplos que o autor escolheu prova pouco: são os casos em que ele pensou. Cada um aqui é comparado com a forma óbvia (Floyd-Warshall para o Dijkstra, força bruta para a mochila, recursão para o Levenshtein) sobre entradas sorteadas com semente fixa — ver `tests/test_algoritmos.py`."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/big-o/busca",
"title": "Busca",
"description": "Linear, binária e por hash — as três respostas para 'está aqui?', e o que cada uma exige.",
"blocos": [
 {"p": "Procurar é a operação mais comum que existe, e há três formas com custos muito diferentes. A escolha depende de uma pergunta: **o que você sabe sobre os dados antes de procurar?**"},
 {"table": {"head": ["Forma", "Custo", "Exige"], "rows": [
   ["percorrer (`x in lista`)", "O(n)", "nada"],
   ["binária (`busca_binaria`)", "O(log n)", "a lista **ordenada**"],
   ["hash (`x in set` / vault)", "O(1)", "valores imutáveis; memória extra"]]}},
 {"code": """adopt Arcane.Algoritmos as Alg

ordenada := [2, 3, 5, 7, 11, 13, 17, 19, 23]
assert Alg.busca_binaria(ordenada, 13) is 5
assert Alg.busca_binaria(ordenada, 4) is -1
assert Alg.limite_inferior(ordenada, 4) is 2      // onde o 4 entraria

// Um milhao de itens: a binaria olha no maximo ~20.
xs := range(0, 1000000)
assert Alg.busca_binaria(xs, 765432) is 765432
out $"log2(1.000.000) = {round(log2(1000000), 1)} passos, no pior caso\"""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Binária numa lista desordenada responde errado — calada", "texto": "A busca binária não confere se a lista está ordenada: conferir custaria O(n), e ela existe para não gastar isso. Numa lista fora de ordem ela devolve `-1` para um valor que está lá. Ordene uma vez; procure muitas."}},
 {"h2": "Quando ordenar vale a pena"},
 {"p": "Ordenar custa O(n log n). Se você vai procurar **uma** vez, percorrer (O(n)) é mais barato. Se vai procurar **k** vezes, ordenar e usar binária custa O(n log n + k log n) contra O(k·n) — e para k grande, a diferença é de horas. E se não precisa de ordem, um `set` responde em O(1) sem ordenar nada."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/big-o/ordenacao",
"title": "Ordenação",
"description": "Por comparação é O(n log n) no melhor caso; por contagem, O(n + k) — e o que é estabilidade.",
"blocos": [
 {"p": "Todo algoritmo que ordena **comparando** pares precisa de Ω(n log n) comparações no pior caso — é um limite matemático, não uma falta de esperteza. A única forma de ir abaixo é **não comparar**: contar."},
 {"code": """adopt Arcane.Algoritmos as Alg

// Merge sort: O(n log n), estavel.
pedidos := [
    {"cliente": "bia", "valor": 50},
    {"cliente": "ana", "valor": 30},
    {"cliente": "bia", "valor": 10},
    {"cliente": "ana", "valor": 20}]
por_cliente := Alg.ordenar_mesclando(pedidos, lambda p: p["cliente"])
// Estavel: dentro de 'ana', a ordem original (30 antes de 20) ficou.
assert (por_cliente >> morph p: p["valor"]) is [30, 20, 50, 10]

// Counting sort: O(n + k), so inteiros, e so quando a faixa k e pequena.
notas := [7, 3, 9, 3, 10, 0, 7]
assert Alg.ordenar_contando(notas) is [0, 3, 3, 7, 7, 9, 10]""", "lang": "df"},
 {"table": {"head": ["Algoritmo", "Tempo", "Espaço", "Estável", "Quando"], "rows": [
   ["`sorted` (Timsort)", "O(n log n)", "O(n)", "sim", "o padrão — e rápido em dados quase ordenados"],
   ["`ordenar_mesclando`", "O(n log n)", "O(n)", "sim", "quando se quer ver o algoritmo"],
   ["`ordenar_contando`", "O(n + k)", "O(k)", "sim", "inteiros numa faixa pequena (notas, idades)"]]}},
 {"callout": {"tipo": "dica", "titulo": "Estabilidade é o que permite ordenar por dois critérios", "texto": "Ordene primeiro pelo critério **secundário** e depois pelo principal, com um algoritmo estável: os empates do principal mantêm a ordem do secundário. Sem estabilidade, a segunda ordenação embaralha a primeira."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/big-o/grafos",
"title": "Grafos",
"description": "BFS, DFS, ordem topológica e Dijkstra — O(V + E) e O((V + E) log V), e o que cada um responde.",
"blocos": [
 {"p": "Um grafo é qualquer coisa que se conecta: ruas, dependências, amizades, tarefas. Quatro algoritmos respondem quase toda pergunta sobre eles, e o formato é o que um JSON já traz — um vault de listas."},
 {"code": """adopt Arcane.Algoritmos as Alg

// Sem peso: quem depende de quem.
tarefas := {
    "cafe": ["xicara", "agua"],
    "agua": ["ferver"],
    "xicara": [],
    "ferver": []}
ordem := Alg.ordem_topologica(tarefas)
assert ordem[0] is "cafe"

amigos := {"ana": ["bia"], "bia": ["caio"], "caio": ["davi"], "eva": []}
assert Alg.bfs(amigos, "ana")["davi"] is 3       // tres apertos de mao
assert Alg.dfs(amigos, "ana") is ["ana", "bia", "caio", "davi"]

// Com peso: o menor caminho.
mapa := {"centro": [["norte", 4], ["sul", 2]], "sul": [["norte", 1]], "norte": []}
r := Alg.dijkstra(mapa, "centro")
assert r["distancia"]["norte"] is 3
assert Alg.caminho(r, "norte") is ["centro", "sul", "norte"]
assert Alg.caminho(r, "lugar-nenhum") is void""", "lang": "df"},
 {"table": {"head": ["Pergunta", "Algoritmo", "Custo"], "rows": [
   ["a menor distância em **passos**", "`bfs`", "O(V + E)"],
   ["tudo que se alcança", "`dfs`", "O(V + E)"],
   ["uma ordem que respeite as dependências", "`ordem_topologica`", "O(V + E)"],
   ["o menor caminho com **peso**", "`dijkstra` + `caminho`", "O((V + E) log V)"]]}},
 {"h2": "Os dois erros que ele recusa"},
 {"code": """adopt Arcane.Algoritmos as Alg

monitor:
    Alg.ordem_topologica({"a": ["b"], "b": ["c"], "c": ["a"]})
    assert no
handle Error as e:
    out e.message                 // mostra o ciclo: a → b → c → a

monitor:
    Alg.dijkstra({"a": [["b", -2]]}, "a")
    assert no
handle Error as e:
    out e.message                 // Dijkstra nao aceita peso negativo""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Peso negativo não dá erro no Dijkstra ingênuo — dá resposta errada", "texto": "O algoritmo assume que um caminho nunca fica mais barato ao ficar mais longo. Com peso negativo isso é falso, e ele devolve um caminho que não é o menor, com toda a confiança. Aqui ele recusa antes; para peso negativo, o algoritmo é Bellman-Ford."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/big-o/programacao-dinamica",
"title": "Programação dinâmica",
"description": "Trocar exponencial por polinomial guardando subproblemas — LCS, Levenshtein e a mochila.",
"blocos": [
 {"p": "Programação dinâmica é o que se faz quando uma recursão ingênua recalcula os mesmos subproblemas milhares de vezes. Guarda-se cada resposta numa tabela, e o custo cai de exponencial para o tamanho da tabela."},
 {"code": """adopt Arcane.Algoritmos as Alg

// A maior subsequencia comum: O(n·m). Pode haver mais de uma do mesmo
// tamanho (BCBA, BDAB, BCAB) — o que e garantido e o TAMANHO.
s := Alg.lcs("ABCBDAB", "BDCABA")
assert len(s) is 4

// Quantas edicoes separam duas palavras: O(n·m), e sugere o que foi quase digitado.
assert Alg.levenshtein("gato", "rato") is 1
palavras := ["arvore", "arroz", "ervilha"]
digitado := "arvroe"
mais_perto := sorted(palavras, lambda p: Alg.levenshtein(p, digitado))[0]
assert mais_perto is "arvore"

// A mochila 0/1: o que levar para o maior valor sem passar do peso. O(n·W).
itens := [
    {"nome": "notebook", "peso": 3, "valor": 2000},
    {"nome": "camera", "peso": 2, "valor": 1500},
    {"nome": "livro", "peso": 1, "valor": 300},
    {"nome": "tripe", "peso": 2, "valor": 400}]
r := Alg.mochila(itens, 5)
assert r["valor"] is 3500
assert (r["escolhidos"] >> morph i: i["nome"]) is ["notebook", "camera"]""", "lang": "df"},
 {"h2": "O mesmo problema, sem a tabela"},
 {"code": """// Levenshtein recursivo: cada chamada abre tres — O(3^n).
action lev(a, b):
    given len(a) is 0:
        yield len(b)
    given len(b) is 0:
        yield len(a)
    custo := 0 given a[0] is b[0] otherwise 1
    yield min(lev(a[1:], b) + 1, lev(a, b[1:]) + 1, lev(a[1:], b[1:]) + custo)

assert lev("gato", "rato") is 1     // ok com 4 letras; com 12, nao termina hoje""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O(n·W) não é polinomial de verdade", "texto": "O custo da mochila depende de **W**, a capacidade — e não do tamanho da entrada, que é o número de dígitos de W. Com W de um milhão, a tabela tem um milhão de colunas. Por isso se diz *pseudo-polinomial*, e por isso o peso precisa ser inteiro."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/big-o/texto",
"title": "Texto e números",
"description": "KMP acha um padrão em O(n + m); o crivo acha os primos em O(n log log n).",
"blocos": [
 {"p": "Procurar um padrão num texto parece O(n·m) — para cada posição, comparar o padrão inteiro. O KMP não volta atrás no texto: ele pré-calcula, a partir do padrão, onde recomeçar quando a comparação falha."},
 {"code": """adopt Arcane.Algoritmos as Alg

dna := "ACGTACGTTACGTACGA"
assert Alg.kmp(dna, "ACGTA") is [0, 9]          // todas as posicoes
assert Alg.kmp("aaaa", "aa") is [0, 1, 2]       // sobrepostas tambem

// O crivo de Eratostenes: riscar os multiplos em vez de testar cada numero.
primos := Alg.crivo(50)
assert primos is [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
assert len(Alg.crivo(100000)) is 9592""", "lang": "df"},
 {"table": {"head": ["Tarefa", "Ingênuo", "Com o algoritmo"], "rows": [
   ["achar um padrão de m letras num texto de n", "O(n·m)", "O(n + m) — `kmp`"],
   ["os primos até n", "O(n·√n) testando cada um", "O(n log log n) — `crivo`"]]}},
 {"callout": {"tipo": "dica", "titulo": "E o `in` do texto?", "texto": "`\"ACGTA\" in dna` usa o algoritmo do próprio Python, rápido na prática. O KMP vale quando se quer **todas** as posições, ou quando o padrão é longo e repetitivo — o pior caso do ingênuo."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/big-o/escolher",
"title": "Escolher a estrutura",
"description": "Uma tabela de decisão: a pergunta que o código faz mais vezes decide a estrutura.",
"blocos": [
 {"p": "A estrutura certa não é a *“mais rápida”*: é a que responde barato **a pergunta que o código faz mais vezes**. Um vault é ótimo para *“quanto vale esta chave?”* e péssimo para *“qual é o menor?”*."},
 {"table": {"head": ["A pergunta frequente", "Estrutura", "Custo"], "rows": [
   ["*está aqui?*", "`Set`", "O(1)"],
   ["*quanto vale esta chave?*", "`Vault`", "O(1)"],
   ["*qual é o i-ésimo?*", "`Cluster`", "O(1)"],
   ["*qual é o menor agora?* (e tirar)", "heap — `Collections.heap_*`", "O(log n)"],
   ["*o primeiro que chegou?*", "fila — `Collections.deque`", "O(1) nas duas pontas"],
   ["*em que posição entraria?* (ordenado)", "`Cluster` ordenado + `limite_inferior`", "O(log n)"],
   ["*estes dois estão no mesmo grupo?*", "`Collections.union_find`", "≈ O(1)"],
   ["*qual o caminho entre dois pontos?*", "grafo (vault de listas)", "O((V + E) log V)"]]}},
 {"code": """adopt Arcane.Collections as C

// O menor, repetidas vezes: heap.
fila := C.heap([5, 1, 9, 3])       // devolve a fila; nao muda a lista
assert C.heap_pop(fila) is 1
assert C.heap_pop(fila) is 3

// Duplicatas: set.
vistos := set()
duplicados := []
cycle email in ["a@x", "b@x", "a@x"]:
    given email in vistos:
        duplicados.append(email)
    vistos.add(email)
assert duplicados is ["a@x"]""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`in` numa lista dentro de um laço", "texto": "É o O(n²) mais comum que existe: `cycle x in a: given x in b:` com `b` lista percorre `b` inteira a cada volta. Trocar `b` por `set(b)` — uma linha — muda a classe para O(n)."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/big-o/medir",
"title": "Medir a curva",
"description": "Bench.curva e Bench.classe — a classe MEDIDA, com a honestidade de dizer quando a medida não separa duas.",
"blocos": [
 {"p": "A análise diz a classe **esperada**; a medida diz a **real**. Dobrar o `n` e ver quanto o tempo cresce responde qual curva descreve o código — um fator ~2 é linear, ~4 é quadrático, pouco mais que 2 é n log n."},
 {"code": """adopt Arcane.Bench as B

r := B.curva(lambda n: sum(range(0, n)), [20000, 40000, 80000])
cycle p in r["pontos"]:
    out $"n = {p['n']}: {p['ms']} ms"
out $"fator ao dobrar: {r['fator']}"

c := B.classe(lambda xs: sorted(xs), [4000, 8000, 16000],
    lambda n: range(n, 0, -1))
out $"classe medida: {c['classe']} ({c['certeza']}, candidatas {c['classes']})"
assert c["classe"] in ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"]""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "A medida pode não separar duas classes — e diz isso", "texto": "O(n) e O(n log n) dão fatores parecidos ao dobrar o n (2,0 contra ~2,1). Quando a amostra cabe nas duas, `classe` devolve as duas em `classes` e `certeza` *“entre duas”*: dizer `O(n)` sobre uma medida que também cabe em `O(n log n)` seria inventar precisão."}},
 {"table": {"head": ["Regra da medida", "Porque"], "rows": [
   ["compare **fatores**, nunca milissegundos", "o número absoluto mede a máquina"],
   ["use tamanhos grandes o bastante", "com n pequeno, o custo fixo do interpretador domina tudo"],
   ["prepare a entrada fora do cronômetro", "`preparar` gera os dados; senão mede-se a geração"],
   ["repita e fique com o menor", "o `Bench` já faz: o menor tempo é o menos perturbado"]]}},
 {"code": """dataforge big-o src/ -v          # a classe estimada, sem rodar
dataforge big-o src/ --medir     # e a medida, lado a lado""", "lang": "bash"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/big-o/exercicios",
"title": "Exercícios de complexidade",
"description": "Oito trechos para classificar — e a resposta, com o porquê, conferida pelo próprio analisador.",
"blocos": [
 {"p": "Classifique cada trecho antes de olhar a resposta. Depois, confira com `dataforge big-o` — a ferramenta diz a classe **e o porquê**."},
 {"code": """// 1
action a(xs):
    yield xs[0]

// 2
action b(xs):
    total := 0
    cycle x in xs:
        total += x
    yield total

// 3
action c(xs):
    pares := 0
    cycle x in xs:
        cycle y in xs:
            given x + y is 0:
                pares += 1
    yield pares

// 4
action d(n):
    passos := 0
    persist n bigger 1:
        n := n ~/ 2
        passos += 1
    yield passos

// 5
action e(xs, ys):
    alvo := set(ys)
    yield [x cycle x in xs given x in alvo]

// 6
action f(n):
    given n smaller 2:
        yield n
    yield f(n - 1) + f(n - 2)

assert a([7]) is 7 and b([1, 2]) is 3 and c([1, -1]) is 2
assert d(1024) is 10 and e([1, 2, 3], [2, 3]) is [2, 3] and f(10) is 55""", "lang": "df"},
 {"table": {"head": ["#", "Classe", "Porque"], "rows": [
   ["1", "O(1)", "um acesso por índice, sem laço"],
   ["2", "O(n)", "um laço sobre a entrada"],
   ["3", "O(n²)", "dois laços aninhados sobre a mesma entrada"],
   ["4", "O(log n)", "o contador **divide** a cada volta"],
   ["5", "O(n + m)", "o `set(ys)` custa m, e cada `in` num set é O(1)"],
   ["6", "O(2ⁿ)", "duas chamadas a si mesma, repetindo o mesmo trabalho — memoize"]]}},
 {"code": """dataforge big-o exercicios.df -v""", "lang": "bash"},
 {"callout": {"tipo": "dica", "titulo": "O 5 é o mais importante", "texto": "Com `ys` como lista, o `in` dentro da compreensão seria O(m) e o todo O(n·m). Uma única linha — `set(ys)` — é a diferença entre segundos e horas num arquivo grande. É a otimização com a maior razão entre esforço e ganho que existe."}},
]},
]
