// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "26 · Complexidade",
  description: "4 exercícios: Big-O, memoização e custo de estrutura.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 26`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[213](#213-medir-o-crescimento-nao-o-relogio)", "**Medir o crescimento, nao o relogio**", "escreva duas versoes do mesmo problema e compare as ordens."], ["[214](#214-trocar-tempo-exponencial-por-memoria-linear)", "**Trocar tempo exponencial por memoria linear**", "faca fib(35) responder, sem esperar."], ["[215](#215-a-estrutura-certa)", "**A estrutura certa**", "escolha entre cluster e vault pela operacao que voce faz."], ["[216](#216-complexidade-de-espaco)", "**Complexidade de espaco**", "processe mais dados do que cabem na memoria."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "213 · Medir o crescimento, nao o relogio"},
  {"p": "**Enunciado.** escreva duas versoes do mesmo problema e compare as ordens."},
  { code: `// Um algoritmo que funciona com dez itens pode nao terminar com um
// milhao. 'dataforge big-o' le a arvore e diz a classe de cada acao,
// sem rodar nada — e diz TAMBEM o porque.

adopt Crucible

// ── O(n^2): para cada item de xs, percorre ys inteiro ──
action comuns_lento(xs, ys):
    saida := []
    cycle x in xs:
        given x in ys:
            saida.append(x)
    yield saida

// ── O(n): o vault responde em O(1) ──
action comuns(xs, ys):
    indice := {}
    cycle y in ys:
        indice[str(y)] := yes

    saida := []
    cycle x in xs:
        given indice.has(str(x)):
            saida.append(x)
    yield saida

// As duas respondem a mesma coisa
a := [1, 2, 3, 4, 5]
b := [4, 5, 6, 7]
assert comuns_lento(a, b) is comuns(a, b), "mesmo resultado"
assert comuns(a, b) is [4, 5], "e o resultado certo"

// A diferenca so aparece quando a entrada cresce. E aqui ha uma licao
// que a notacao sozinha nao ensina: com entrada PEQUENA, o O(n) pode
// perder — montar o vault custa, e esse custo nao depende de n.

action comparar(n):
    xs := [i cycle i in range(n)]
    ys := [i + n ~/ 2 cycle i in range(n)]

    lento := Crucible.timed(lambda => comuns_lento(xs, ys))
    rapido := Crucible.timed(lambda => comuns(xs, ys))

    assert comuns_lento(xs, ys) is comuns(xs, ys), "as duas concordam"
    yield {"n": n, "lento": lento["total_ms"], "rapido": rapido["total_ms"]}

cycle n in [500, 2000, 5000]:
    r := comparar(n)
    razao := round(r["lento"] / r["rapido"], 2)
    out "n =", r["n"], " O(n^2):", round(r["lento"], 1),
    "ms   O(n):", round(r["rapido"], 1), "ms   razao:", razao

// O que a saida mostra:
//
//   n=500    razao ~0.5   o O(n) PERDE — montar o vault custa
//   n=2000   razao ~0.9   quase empatam
//   n=5000   razao ~1.6   o O(n) ganha, e a vantagem so cresce
//
// Big-O e sobre CRESCIMENTO, nao sobre velocidade. O(n) com constante
// grande perde de O(n^2) com constante pequena ate um certo n —
// depois disso, nunca mais. Achar esse ponto e trabalho de medicao;
// saber que ele existe e trabalho da notacao.

pequeno := comparar(500)
grande := comparar(5000)
razao_pequeno := pequeno["lento"] / pequeno["rapido"]
razao_grande := grande["lento"] / grande["rapido"]

out "razao com n=500: ", round(razao_pequeno, 2)
out "razao com n=5000:", round(razao_grande, 2)
assert razao_grande bigger razao_pequeno,
"a vantagem do O(n) cresce com a entrada"
assert razao_grande bigger 1.0,
"e a partir de certo tamanho, ele ja e mais rapido"

// A analise estatica concorda, e diz o porque:
//
//   $ dataforge big-o 213_medir_o_crescimento.df -v
//
//   ▲ comuns_lento    O(n^2)  tempo   O(n) espaco
//       · 'in' na linha 14 percorre a colecao (use um vault para O(1))
//       ⚠ O(n^2): dobrar a entrada quadruplica o tempo.
//   ● comuns          O(n)    tempo   O(n) espaco

out "ok"`, lang: 'df', title: `exercicios/26-complexidade/213_medir_o_crescimento.df` },
  {"h3": "Conceitos"},
  {"p": "Um algoritmo que funciona com dez itens pode não terminar com um milhão. `dataforge big-o` lê a árvore e diz a classe de cada ação, sem rodar nada — e diz **também o porquê**."},
  { code: `▲ comuns_lento    O(n^2)  tempo   O(n) espaco
    · 'in' na linha 14 percorre a colecao (use um vault para O(1))
    ⚠ O(n^2): dobrar a entrada quadruplica o tempo.
● comuns          O(n)    tempo   O(n) espaco`, lang: 'text' },
  {"h3": "O que observar"},
  {"p": "**A razão cresce com n.** Com n=500 o O(n) *perde* — montar o vault custa, e esse custo não depende de n. Com n=5000 ele já ganha, e a vantagem só aumenta."},
  {"p": "**Big-O é sobre crescimento, não sobre velocidade.** O(n) com constante grande perde de O(n²) com constante pequena até um certo n. Achar esse ponto é trabalho de medição; saber que ele existe é trabalho da notação."},
  {"p": "**Medir uma vez só é ruído.** `Crucible.timed(acao, 200)` repete, porque uma operação de microssegundos é dominada pelo custo de medir."},
  {"h3": "Armadilhas"},
  {"list": ["Otimizar sem medir é adivinhar. Otimizar sem saber a ordem é adivinhar duas"]},
  {"p": "vezes."},
  {"list": ["`dataforge profile` diz quanto custa **hoje**; `big-o` diz como o custo"]},
  {"p": "**cresce**. As duas coisas respondem perguntas diferentes."},
  {"h3": "Relacionados"},
  {"list": ["[214 — Memoização](214_memoizacao.md)", "[215 — A estrutura certa](215_estrutura_certa.md)"]},
  {"h2": "214 · Trocar tempo exponencial por memoria linear"},
  {"p": "**Enunciado.** faca fib(35) responder, sem esperar."},
  { code: `// Fibonacci ingenuo e O(2^n): cada chamada gera duas, e quase todas
// recalculam o que ja foi calculado. Guardar o resultado derruba para
// O(n) — e e a troca mais lucrativa que existe.

adopt Crucible

action fib_lento(n):
    given n smaller 2:
        yield n
    yield fib_lento(n - 1) + fib_lento(n - 2)

cache := {}

action fib(n):
    given n smaller 2:
        yield n
    chave := str(n)
    given cache.has(chave):
        yield cache[chave]
    resultado := fib(n - 1) + fib(n - 2)
    cache[chave] := resultado
    yield resultado

// As duas concordam
cycle i from 0 to 15:
    assert fib_lento(i) is fib(i), "mesmo resultado"

assert fib(10) is 55, "o decimo"
assert fib(20) is 6765, "o vigesimo"

// A diferenca de custo, medida
lento := Crucible.timed(lambda => fib_lento(22))
cache := {}
rapido := Crucible.timed(lambda => fib(22))

out "fib(22) ingenuo:  ", round(lento["total_ms"], 2), "ms"
out "fib(22) memoizado:", round(rapido["total_ms"], 3), "ms"
// A razao nao e IMPRESSA: ela varia a cada execucao (687x, 441x…), e o
// teste que compara a saida com a compilacao ligada e desligada roda o
// arquivo DUAS vezes e exige saida identica. Ele normaliza numeros com
// unidade de tempo — '12.3ms' — e um numero solto seguido de 'x' passa
// por fora.
//
// O 'assert' abaixo cobre o que importa, e sem imprimir nada instavel.
out "razao:             duas ordens de grandeza"
// Margem, e nao 'bigger': medido, a razao fica em ~440x. Comparar
// dois tempos com 'bigger' passa por acidente quando a medicao
// quebra — e foi o que aconteceu no 215, que tinha margem de 2x e
// reprovou a CI num macOS carregado.
assert lento["total_ms"] / rapido["total_ms"] bigger 20,
"o memoizado ganha por duas ordens de grandeza"

// E o que so o memoizado consegue: fib(90) tem 19 digitos, e o
// ingenuo levaria mais tempo que a idade do universo.
cache := {}
assert fib(90) is 2880067194370816120, "instantaneo"

// O custo: memoria. Cada valor calculado fica guardado.
out "valores guardados:", len(cache)
assert len(cache) is 89, "um por chamada, de 2 a 90"

// A conta que decide a troca:
//
//   fib(50) ingenuo   ~2^50  = 10^15 chamadas    (semanas)
//   fib(50) memoizado ~50    = 50 chamadas       (microssegundos)
//   custo em memoria  ~50 valores                (nada)
//
// Trocar O(2^n) de tempo por O(n) de memoria quase sempre vale. A
// excecao e quando a memoria e o gargalo — ver o exercicio 216.

out "ok"`, lang: 'df', title: `exercicios/26-complexidade/214_memoizacao.df` },
  {"h3": "Conceitos"},
  {"p": "Fibonacci ingênuo é O(2ⁿ): cada chamada gera duas, e quase todas recalculam o que já foi calculado. `fib(40)` faz mais de um bilhão de chamadas."},
  {"p": "Guardar o resultado derruba para O(n):"},
  { code: `cache := {}

action fib(n):
    given n smaller 2:
        yield n
    chave := str(n)
    given cache.has(chave):
        yield cache[chave]
    resultado := fib(n - 1) + fib(n - 2)
    cache[chave] := resultado
    yield resultado`, lang: 'df' },
  {"h3": "O que observar"},
  {"p": "**A conta que decide a troca:**"},
  {"table": {"head": ["", "tempo", "memória"], "rows": [["`fib(50)` ingênuo", "~10¹⁵ chamadas (semanas)", "O(n) de pilha"], ["`fib(50)` memoizado", "~50 chamadas (µs)", "50 valores"]]}},
  {"p": "**O snippet `memo`** no VS Code escreve esse padrão."},
  {"p": "**O analisador reconhece os dois.** Ele distingue divisão e conquista (O(n log n)) de recursão exponencial (O(2ⁿ)) olhando o argumento da chamada recursiva — metade contra n−1."},
  {"h3": "Armadilhas"},
  {"list": ["O cache cresce sem limite. Para entrada ilimitada, use um cache com teto (LRU)"]},
  {"p": "— ou o programa troca tempo por vazamento de memória."},
  {"list": ["A chave precisa ser única. `str(n)` serve para um argumento; com dois, junte"]},
  {"p": "os dois."},
  {"h3": "Relacionados"},
  {"list": ["[213 — Medir o crescimento](213_medir_o_crescimento.md)", "[216 — Complexidade de espaço](216_espaco.md)"]},
  {"h2": "215 · A estrutura certa"},
  {"p": "**Enunciado.** escolha entre cluster e vault pela operacao que voce faz."},
  { code: `// Escolher a estrutura costuma render mais que otimizar o algoritmo. A
// tabela que decide cabe em tres linhas:
//
//   procurar por posicao  -> Cluster, O(1)
//   procurar por chave    -> Vault,   O(1)
//   procurar por valor    -> Cluster, O(n)   <- e aqui que se perde

adopt Crucible

// 100 mil, e nao 3 mil.
//
// Com n = 3000 a razao entre as duas buscas ficava em ~2x, e uma volta
// em cinco dava 1,3x — o 'assert' abaixo virava sorteio, e a CI
// reprovou nisso num macOS carregado. A causa nao e a medicao: e que o
// 'in' de um cluster e um laco em C, rapido o bastante para o CUSTO DE
// DESPACHO do interpretador dominar os dois lados e mascarar a
// diferenca assintotica.
//
// Medido aqui: 2,7x com 3 mil, 9x com 20 mil, 43x com 100 mil, 127x
// com 300 mil. So a partir de 100 mil a conta que este exercicio
// ensina fica visivel acima do ruido.
n := 100000
lista := [i cycle i in range(n)]
mapa := {}
cycle i in range(n):
    mapa[str(i)] := i

// Ler por posicao: os dois sao O(1)
assert lista[500] is 500, "cluster indexa direto"
assert mapa["500"] is 500, "vault tambem"

// Procurar por VALOR: o cluster percorre.
//
// A medicao repete 200 vezes: uma busca sozinha leva microssegundos, e
// o custo de medir dominaria o resultado. Medir uma vez so e o erro
// mais comum de quem compara desempenho.
por_valor := Crucible.timed(lambda => -1 in lista, 50)
por_chave := Crucible.timed(lambda => mapa.has("nao-existe"), 50)

razao := por_valor["media_ms"] / por_chave["media_ms"]

out "procurar num cluster de", n, ":", round(por_valor["media_ms"], 4), "ms"
out "procurar num vault  de", n, ":", round(por_chave["media_ms"], 5), "ms"

// A margem e 5x, e nao "maior que": medido, o valor fica em ~43x.
// Cobrar so 'bigger' passaria por acidente numa medicao quebrada, e
// cobrar 40x reprovaria numa maquina lenta. 5x e o intervalo onde a
// afirmacao e verdadeira e a medicao nao e sorteio.
assert razao bigger 5,
"o vault ganha por uma ordem de grandeza, e a vantagem cresce com n"

// Contar ocorrencias: uma passada, nao um laco aninhado
palavras := ["a", "b", "a", "c", "b", "a"]

// O(n^2) — para cada palavra, conta percorrendo tudo
action contar_lento(xs):
    saida := {}
    cycle x in xs:
        saida[x] := xs.count(x)
    yield saida

// O(n) — uma passada
action contar(xs):
    yield xs.tally()

assert contar_lento(palavras) is contar(palavras), "mesmo resultado"
assert contar(palavras)["a"] is 3, "tres 'a'"

// Agrupar: o vault ja e o agrupamento
pessoas := [
    {"nome": "Ana", "cidade": "Floripa"},
    {"nome": "Bia", "cidade": "Recife"},
    {"nome": "Cid", "cidade": "Floripa"}
]
por_cidade := pessoas.group_by(lambda p: p["cidade"])
assert len(por_cidade["Floripa"]) is 2, "duas em Floripa"
assert len(por_cidade) is 2, "duas cidades"

// Remover do INICIO de um cluster e O(n): desloca todos os outros.
// Num laco, isso vira O(n^2).
fila := [i cycle i in range(500)]
inverso := fila.reversed()  // O(n), uma vez
assert inverso.pop() is 0, "tirar do fim e O(1)"
assert len(inverso) is 499, "e a fila continua"

out "ok"`, lang: 'df', title: `exercicios/26-complexidade/215_estrutura_certa.df` },
  {"h3": "A tabela que decide"},
  {"table": {"head": ["Você faz", "Use", "Custo"], "rows": [["procurar por posição", "`Cluster`", "O(1)"], ["procurar por chave", "`Vault`", "O(1)"], ["procurar por **valor**", "`Cluster`", "**O(n)**"]]}},
  {"p": "A terceira linha é onde se perde. `999999 in lista` percorre a lista inteira; `mapa.has(\"999999\")` calcula um hash e vai direto."},
  {"p": "Escolher a estrutura costuma render mais que otimizar o algoritmo: um `O(n)` dentro de um laço `O(n)` dá `O(n²)`, e nenhuma micro-otimização salva isso."},
  {"h3": "Por que 100 mil, e não 3 mil"},
  {"p": "Este exercício media com `n = 3000`, e a razão entre as duas buscas ficava em **~2x** — com uma volta em cinco dando 1,3x. O `assert` virava sorteio, e reprovou a CI num macOS carregado."},
  {"p": "A causa não era a medição. O `in` de um cluster é um **laço em C**, rápido o bastante para o custo de despacho do interpretador dominar os dois lados e mascarar a diferença assintótica:"},
  {"table": {"head": ["n", "cluster", "vault", "razão"], "rows": [["3.000", "0,015 ms", "0,006 ms", "2,7x"], ["20.000", "0,057 ms", "0,006 ms", "9,2x"], ["100.000", "0,259 ms", "0,006 ms", "**43x**"], ["300.000", "0,815 ms", "0,006 ms", "127x"]]}},
  {"p": "Note a coluna do vault: **constante**. É isso que O(1) significa, e é por isso que a vantagem cresce com n — não porque o vault fique mais rápido, mas porque o cluster fica mais lento."},
  {"p": "Só a partir de 100 mil a conta que este exercício ensina fica visível acima do ruído."},
  {"h3": "A margem, e por que ela importa"},
  { code: `razao := por_valor["media_ms"] / por_chave["media_ms"]
assert razao bigger 5,
"o vault ganha por uma ordem de grandeza, e a vantagem cresce com n"`, lang: 'df' },
  {"p": "Não `assert a_ms bigger b_ms`. Comparar dois tempos medidos sem margem passa **por acidente** quando a medição está quebrada, e falha por acidente quando a máquina está carregada. Um teste que falha por máquina lenta ensina a ignorar a suíte, que é o pior que pode acontecer com ela."},
  {"p": "`5x` é o intervalo honesto: o valor medido é ~43x, então a afirmação é verdadeira com folga; e se algum dia a busca no vault virar O(n) por acidente, 5x reprova alto."},
  {"p": "Há um teste no repositório (`test_nenhum_exercicio_compara_dois_tempos_sem_margem`) que proíbe o padrão sem margem voltar."},
  {"h3": "Medir uma vez é o erro mais comum"},
  { code: `por_valor := Crucible.timed(lambda => -1 in lista, 50)`, lang: 'df' },
  {"p": "O segundo argumento é o número de repetições. Uma busca sozinha leva microssegundos, e o custo de **medir** dominaria o resultado — o que se mede então é o relógio, não o código."},
  {"p": "E procure por algo que **não existe** (`-1`, `\"nao-existe\"`): procurar um valor que está no meio mede meia lista, e o número depende de onde ele caiu."},
  {"h2": "216 · Complexidade de espaco"},
  {"p": "**Enunciado.** processe mais dados do que cabem na memoria."},
  { code: `// Tempo nao e o unico recurso. Um algoritmo O(n log n) que aloca uma
// copia pode perder para um O(n^2) que trabalha no lugar, quando a
// memoria e o gargalo.

adopt Crucible

// ── O(1) de espaco: uma variavel, nao importa o tamanho ──
action somar(xs):
    total := 0
    cycle x in xs:
        total += x
    yield total

// ── O(n) de espaco: a saida cresce com a entrada ──
action dobrar(xs):
    saida := []
    cycle x in xs:
        saida.append(x * 2)
    yield saida

assert somar([1, 2, 3]) is 6, "somou"
assert dobrar([1, 2]) is [2, 4], "dobrou"

// A pilha tambem e memoria: cada chamada recursiva ocupa um quadro
action soma_recursiva(n):
    given n smaller_eq 0:
        yield 0
    yield n + soma_recursiva(n - 1)

action soma_iterativa(n):
    total := 0
    cycle i from 1 to n:
        total += i
    yield total

assert soma_recursiva(100) is soma_iterativa(100), "mesmo resultado"

// Recursao profunda estoura a pilha; o laco nao
monitor:
    soma_recursiva(100000)
    assert no, "devia ter estourado"
handle e:
    out "recursao profunda:", e.type
    assert soma_iterativa(100000) is 5000050000, "o laco vai fundo sem estourar"

// ── Preguica: processar sem materializar ──

// Um generator produz um item por vez. Este 'range' de um milhao nunca
// existe inteiro na memoria — so os tres primeiros pares sao calculados.
stream action pares(xs):
    cycle x in xs:
        given x % 2 is 0:
            emit x

primeiros := pares(range(1000000)).take(3)
out "os tres primeiros pares de um milhao:", primeiros
assert primeiros is [0, 2, 4], "so tres foram calculados"

// A compreensao equivalente alocaria 500 mil itens
poucos := [x cycle x in range(20) given x % 2 is 0]
assert len(poucos) is 10, "aqui cabe, com 20 itens"

// Medindo a diferenca com uma entrada media
com_preguica := Crucible.timed(lambda => pares(range(100000)).take(5))
com_lista := Crucible.timed(lambda => [x cycle x in range(100000) given x % 2 is 0])

out "preguicoso (5 itens):", round(com_preguica["total_ms"], 3), "ms"
out "lista inteira:       ", round(com_lista["total_ms"], 1), "ms"
// Margem: medido, a razao fica em ~130x. Ver a nota do 214.
assert com_lista["total_ms"] / com_preguica["total_ms"] bigger 10,
"a preguica so paga pelo que voce pede"

// A regra:
//
//   'stream action' + 'take(n)' processa mais dados do que cabem na
//   RAM. A compreensao e mais legivel e materializa tudo. Use a
//   segunda ate ela nao caber, e entao troque.

out "ok"`, lang: 'df', title: `exercicios/26-complexidade/216_espaco.df` },
  {"h3": "Conceitos"},
  {"p": "Tempo não é o único recurso. Um algoritmo O(n log n) que aloca uma cópia pode perder para um O(n²) que trabalha no lugar, quando a memória é o gargalo."},
  { code: `stream action pares(xs):
    cycle x in xs:
        given x % 2 is 0:
            emit x

out pares(range(1000000)).take(3)     // O(1) de espaço`, lang: 'df' },
  {"p": "O `range` de um milhão nunca existe inteiro na memória — só os três primeiros pares são calculados."},
  {"h3": "O que observar"},
  {"p": "**A pilha também é memória.** Cada chamada recursiva ocupa um quadro. Uma recursão de profundidade n custa O(n) de espaço mesmo sem alocar nada — e estoura por volta de mil níveis."},
  {"p": "**Preguiça é uma estratégia de memória.** `stream action` + `take(n)` processa mais dados do que cabem na RAM. A compreensão é mais legível e materializa tudo: use a segunda até ela não caber, e então troque."},
  {"p": "**Só a memória adicional conta.** A entrada não entra na conta — ela já existia."},
  {"h3": "Armadilhas"},
  {"list": ["Um generator infinito materializado (`to_cluster()`) trava. Use `take(n)`.", "Trocar tempo por memória quase sempre vale — exceto quando a memória é o"]},
  {"p": "gargalo. Num contêiner com limite apertado, estourar derruba o processo, enquanto ser lento só irrita."},
  {"h3": "Relacionados"},
  {"list": ["[214 — Memoização](214_memoizacao.md)", "[Complexidade de espaço](https://dataforge-lang.vercel.app/docs/big-o/espaco)"]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/26-complexidade/213_medir_o_crescimento.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '213-medir-o-crescimento-nao-o-relogio', text: "213 · Medir o crescimento, nao o relogio", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '214-trocar-tempo-exponencial-por-memoria-linear', text: "214 · Trocar tempo exponencial por memoria linear", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '215-a-estrutura-certa', text: "215 · A estrutura certa", level: 2 as const }, { id: 'a-tabela-que-decide', text: "A tabela que decide", level: 3 as const }, { id: 'por-que-100-mil-e-nao-3-mil', text: "Por que 100 mil, e não 3 mil", level: 3 as const }, { id: 'a-margem-e-por-que-ela-importa', text: "A margem, e por que ela importa", level: 3 as const }, { id: 'medir-uma-vez-e-o-erro-mais-comum', text: "Medir uma vez é o erro mais comum", level: 3 as const }, { id: '216-complexidade-de-espaco', text: "216 · Complexidade de espaco", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"26 · Complexidade"}
      description={"4 exercícios: Big-O, memoização e custo de estrutura."}
      href={"/docs/exercicios/26-complexidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
