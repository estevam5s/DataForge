// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "15 · Streams",
  description: "6 exercícios: stream action, emit, take e sequências infinitas.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **A linguagem a fundo** · stream action, emit, take e sequências infinitas · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 15`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[145](#145-generators-com-stream-action)", "**Generators com stream action**", "produza valores um a um com emit, em vez de montar a lista inteira."], ["[146](#146-sequencias-infinitas)", "**Sequencias infinitas**", "escreva um generator sem fim e consuma so o que precisa."], ["[147](#147-streams-com-pipelines)", "**Streams com pipelines**", "combine generators com sift, morph e distill."], ["[148](#148-processamento-incremental)", "**Processamento incremental**", "use streams para tratar dados grandes sem carregar tudo na memoria."], ["[149](#149-observe-e-eventos)", "**observe e eventos**", "reaja a valores conforme eles chegam."], ["[150](#150-projeto-etl-com-streams)", "**Projeto: ETL com streams**", "monte um pipeline de extracao, transformacao e carga usando generators."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "145 · Generators com stream action"},
  {"p": "**Enunciado.** produza valores um a um com emit, em vez de montar a lista inteira."},
  { code: `// Um stream action produz valores com 'emit'
stream action contar(ate):
    cycle i from 1 to ate:
        emit i

// A chamada devolve um Stream, nao uma lista
s := contar(5)
out typeof(s)
assert typeof(s) is "Stream", "a chamada devolve um Stream"

// to_cluster materializa tudo
out s.to_cluster()
assert contar(5).to_cluster() is [1, 2, 3, 4, 5], "todos os valores"

// take pega so o comeco
out contar(1000).take(3)
assert contar(1000).take(3) is [1, 2, 3], "so os tres primeiros"

// cycle consome o stream direto
cycle v in contar(3):
    out $"recebi {v}"

// Um generator pode emitir qualquer coisa
stream action palavras():
    emit "data"
    emit "forge"
    emit "lang"

out palavras().to_cluster().join(" ")
assert palavras().to_cluster() is ["data", "forge", "lang"], "textos"

// emit fora de um stream action e um alias historico de 'out'
emit "isso imprime, nao produz"

// Contar sem materializar
stream action pares_ate(n):
    cycle i from 0 to n:
        given i % 2 is 0:
            emit i

out $"pares ate 10: {pares_ate(10).to_cluster()}"
assert pares_ate(10).count() is 6, "0, 2, 4, 6, 8, 10"`, lang: 'df', title: `exercicios/15-streams-e-generators/145_generator_basico.df` },
  {"h3": "Conceitos"},
  {"p": "Um `stream action` é uma ação que **produz uma sequência**:"},
  { code: `stream action contar(ate):
    cycle i from 1 to ate:
        emit i`, lang: 'df' },
  {"p": "Duas palavras fazem a diferença:"},
  {"table": {"head": ["Palavra", "Efeito"], "rows": [["`stream action`", "a chamada devolve um `Stream`, não um valor"], ["`emit`", "produz um item e **continua** de onde parou"]]}},
  {"h3": "`emit` e `yield` são coisas diferentes"},
  {"p": "Esta é a distinção central, e ela é deliberada:"},
  { code: `action f():
    yield 1        // devolve 1 e ENCERRA a ação

stream action g():
    emit 1         // produz 1 e CONTINUA
    emit 2`, lang: 'df' },
  {"p": "Em Python as duas ideias dividem a mesma palavra (`yield`), o que é uma fonte conhecida de confusão — uma função vira geradora só por conter um `yield`, sem nada no cabeçalho anunciando isso. DataForge separa: `stream action` no cabeçalho diz o que a ação é, `emit` diz o que ela faz."},
  {"p": "Dentro de um `stream action`, `yield` continua servindo para encerrar a produção antes do fim."},
  {"h3": "Consumindo um stream"},
  {"table": {"head": ["Chamada", "Devolve"], "rows": [["`s.to_cluster()`", "tudo, como lista"], ["`s.take(n)`", "os `n` primeiros"], ["`s.next()`", "o próximo item (ou `void`)"], ["`s.count()`", "quantos itens ao todo"], ["`s.first()`", "o primeiro (ou `void`)"], ["`cycle v in s:`", "percorre item a item"]]}},
  {"h3": "Saída esperada"},
  { code: `Stream
[1, 2, 3, 4, 5]
[1, 2, 3]
recebi 1
recebi 2
recebi 3
data forge lang
isso imprime, nao produz
pares ate 10: [0, 2, 4, 6, 8, 10]`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Troque `emit i` por `yield i` e veja o stream terminar no primeiro item.", "Escreva um generator que emite os quadrados perfeitos até um limite."]},
  {"h2": "146 · Sequencias infinitas"},
  {"p": "**Enunciado.** escreva um generator sem fim e consuma so o que precisa."},
  { code: `// Um laco infinito num generator e legitimo: nada roda ate alguem pedir
stream action naturais():
    n := 0
    persist yes:
        emit n
        n += 1

out naturais().take(6)
assert naturais().take(6) is [0, 1, 2, 3, 4, 5], "seis primeiros"

// Fibonacci infinito
stream action fibonacci():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b

out fibonacci().take(10)
assert fibonacci().take(10) is [0, 1, 1, 2, 3, 5, 8, 13, 21, 34], "fib"

// Potencias de dois
stream action potencias(base):
    valor := 1
    persist yes:
        emit valor
        valor *= base

out potencias(2).take(8)
assert potencias(2).take(8) is [1, 2, 4, 8, 16, 32, 64, 128], "potencias de 2"

// Ciclo eterno sobre uma lista
stream action repetir(itens):
    persist yes:
        cycle i in itens:
            emit i

out repetir(["a", "b", "c"]).take(7)
assert repetir(["a", "b"]).take(5) is ["a", "b", "a", "b", "a"], "alterna"

// Parar de dentro, com halt
stream action ate_passar(limite):
    n := 1
    persist yes:
        given n bigger limite:
            halt
        emit n
        n *= 3

out ate_passar(100).to_cluster()
assert ate_passar(100).to_cluster() is [1, 3, 9, 27, 81], "para em 81"

// next() avanca um por vez
g := naturais()
out g.next(), g.next(), g.next()
assert g.next() is 3, "a quarta chamada devolve 3"`, lang: 'df', title: `exercicios/15-streams-e-generators/146_generator_infinito.df` },
  {"h3": "Conceitos"},
  {"p": "Um `persist yes:` dentro de um `stream action` não trava o programa:"},
  { code: `stream action naturais():
    n := 0
    persist yes:
        emit n
        n += 1

out naturais().take(6)     // [0, 1, 2, 3, 4, 5]`, lang: 'df' },
  {"h3": "Por que isso funciona"},
  {"p": "O corpo de um `stream action` **não roda na chamada**. `naturais()` devolve um `Stream` sem executar nada. A execução acontece sob demanda: cada `emit` roda quando alguém pede o próximo item, e **pausa** logo depois."},
  {"p": "`take(6)` pede seis itens, recebe seis, e para de pedir. O laço infinito simplesmente nunca chega à sétima volta."},
  {"p": "É a mesma ideia de `itertools.count()` em Python ou de listas preguiçosas em Haskell — a sequência é uma *receita*, não um dado."},
  {"h3": "O que isso permite"},
  {"p": "Descrever a sequência pelo que ela **é**, não por quantos itens você vai querer:"},
  { code: `stream action fibonacci():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b`, lang: 'df' },
  {"p": "Essa definição é completa e não menciona limite algum. Quem chama decide: `take(10)`, `take(1000)`, ou um `cycle` com `halt` na condição que importar."},
  {"p": "Repare no `a, b := b, a + b` — a desestruturação faz a troca simultânea que em outras linguagens exigiria uma variável temporária."},
  {"h3": "Parando por dentro"},
  {"p": "Quando o próprio generator sabe onde parar, use `halt`:"},
  { code: `stream action ate_passar(limite):
    n := 1
    persist yes:
        given n bigger limite:
            halt
        emit n
        n *= 3`, lang: 'df' },
  {"p": "Agora `to_cluster()` é seguro: a sequência termina sozinha."},
  {"h3": "Cuidado"},
  {"p": "`to_cluster()` num generator **realmente** infinito trava o programa — ele tenta materializar itens para sempre. Use `take(n)` ou garanta um `halt`."},
  {"h3": "Saída esperada"},
  { code: `[0, 1, 2, 3, 4, 5]
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
[1, 2, 4, 8, 16, 32, 64, 128]
[a, b, c, a, b, c, a]
[1, 3, 9, 27, 81]
0 1 2`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Escreva um generator de números primos e pegue os 20 primeiros.", "Faça `repetir` aceitar um limite opcional de voltas."]},
  {"h2": "147 · Streams com pipelines"},
  {"p": "**Enunciado.** combine generators com sift, morph e distill."},
  { code: `stream action naturais():
    n := 1
    persist yes:
        emit n
        n += 1

// Materialize antes de usar o pipeline
primeiros := naturais().take(20)
out primeiros >> sift n: n % 3 is 0
assert(primeiros >> sift n: n % 3 is 0) is [3, 6, 9, 12, 15, 18], "multiplos de 3"

// Compreensao sobre stream
stream action letras():
    cycle c in "dataforge":
        emit c

maiusculas := [c.upper() cycle c in letras() given c isnt "a"]
out maiusculas.join("")
assert maiusculas.join("") is "DTFORGE", "sem os a"

// map e filter direto no stream: os dois devolvem um STREAM, e nao
// uma lista — por isso encadeiam, e por isso valem num infinito.
stream action ate(n):
    cycle i from 1 to n:
        emit i

out ate(10).filter(lambda n: n % 2 is 0).to_cluster()
out ate(5).map(lambda n: n * n).to_cluster()
assert ate(10).filter(lambda n: n % 2 is 0).to_cluster() is [2, 4, 6, 8, 10], "filter"
assert ate(5).map(lambda n: n * n).to_cluster() is [1, 4, 9, 16, 25], "map"

// Num stream INFINITO, que e onde a preguica deixa de ser detalhe:
// isto volta na hora, e materializar antes nao voltaria nunca.
assert naturais().map(lambda n: n * n).take(4) is [1, 4, 9, 16], "infinito"
assert naturais().filter(lambda n: n % 7 is 0).take(3) is [7, 14, 21], "infinito"

// E os outros tres que um stream sabe fazer:
assert ate(10).skip(7).to_cluster() is [8, 9, 10], "skip"
assert ate(4).enumerate().to_cluster() is [[0, 1], [1, 2], [2, 3], [3, 4]], "enumerate"
assert ate(4).reduce(lambda a, b => a + b, 0) is 10, "reduce"

// Encadear geradores: um consome o outro
stream action dobrar(fonte):
    cycle v in fonte:
        emit v * 2

out dobrar(ate(5)).to_cluster()
assert dobrar(ate(5)).to_cluster() is [2, 4, 6, 8, 10], "generator sobre generator"

stream action so_pares(fonte):
    cycle v in fonte:
        given v % 2 is 0:
            emit v

// Uma cadeia inteira, ainda preguicosa ate o take
cadeia := dobrar(so_pares(naturais()))
out cadeia.take(5)
assert cadeia.take(5) is [4, 8, 12, 16, 20], "pares dobrados"

// Reduzir um stream
total := ate(100).to_cluster() >> distill acc, v: acc + v 0
out $"soma de 1 a 100: {total}"
assert total is 5050, "soma de Gauss"`, lang: 'df', title: `exercicios/15-streams-e-generators/147_stream_em_pipeline.df` },
  {"h3": "Conceitos"},
  {"p": "Streams e pipelines resolvem o mesmo problema por caminhos diferentes:"},
  {"table": {"head": ["", "Streams", "Pipelines"], "rows": [["Avaliação", "preguiçosa, item a item", "ansiosa, lista inteira"], ["Fonte infinita", "sim", "não"], ["Sintaxe", "`stream action` + `emit`", "`>> sift` / `>> morph`"]]}},
  {"p": "Os pipelines operam sobre listas. Para usá-los com um stream, materialize antes:"},
  { code: `primeiros := naturais().take(20)
out primeiros >> sift n: n % 3 is 0`, lang: 'df' },
  {"h3": "Métodos diretos no stream"},
  {"p": "Para filtrar e transformar sem escrever a materialização:"},
  { code: `ate(10).filter(lambda n: n % 2 is 0).to_cluster()
ate(5).map(lambda n: n * n).to_cluster()`, lang: 'df' },
  {"p": "Ambos devolvem outro **stream**, e não uma lista: nada é produzido enquanto ninguém pede. É o que faz `naturais().map(…).take(4)` voltar na hora — um `map` que consumisse o stream inteiro nunca voltaria de um infinito, e essa é a única razão de o stream existir."},
  {"p": "Quem pede o resultado é `to_cluster()` (tudo) ou `take(n)` (os `n` primeiros, e nem um item a mais produzido)."},
  {"table": {"head": ["Método", "Devolve", "Preguiçoso"], "rows": [["`map(f)` · `filter(f)` · `skip(n)` · `enumerate()`", "um stream", "sim"], ["`take(n)` · `to_cluster()`", "uma lista", "não"], ["`reduce(f, inicial)` · `count()` · `first()` · `next()`", "um valor", "não"]]}},
  {"h3": "Compreensões consomem streams"},
  { code: `[c.upper() cycle c in letras() given c isnt "a"]`, lang: 'df' },
  {"p": "O `cycle in` de uma compreensão aceita um stream como fonte, igual ao `cycle` de laço."},
  {"h3": "Encadear generators"},
  {"p": "Aqui está o padrão que dá poder à ideia: um generator que consome outro."},
  { code: `stream action dobrar(fonte):
    cycle v in fonte:
        emit v * 2

cadeia := dobrar(so_pares(naturais()))
out cadeia.take(5)          // [4, 8, 12, 16, 20]`, lang: 'df' },
  {"p": "`naturais()` é infinito. `so_pares` filtra, `dobrar` transforma — e **nada roda** até o `take(5)`. Cada item atravessa a cadeia inteira sob demanda; a memória usada não depende do tamanho da fonte."},
  {"p": "É o mesmo desenho dos pipes do Unix: `yes | grep ... | sed ...` não trava porque cada estágio consome o anterior aos poucos."},
  {"h3": "Quando escolher cada um"},
  {"list": ["**Pipeline** para dados que já estão na memória e cabem nela.", "**Stream** para fonte infinita, arquivo grande, ou quando você só precisa dos"]},
  {"p": "primeiros resultados."},
  {"h3": "Saída esperada"},
  { code: `[3, 6, 9, 12, 15, 18]
DTFORGE
[2, 4, 6, 8, 10]
[1, 4, 9, 16, 25]
[2, 4, 6, 8, 10]
[4, 8, 12, 16, 20]
soma de 1 a 100: 5050`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente um terceiro estágio à cadeia e confirme que continua preguiçoso.", "Meça com `Arcane.Time.stopwatch` a diferença entre filtrar 1 milhão de itens"]},
  {"p": "materializados e pegar os 5 primeiros de um stream."},
  {"h2": "148 · Processamento incremental"},
  {"p": "**Enunciado.** use streams para tratar dados grandes sem carregar tudo na memoria."},
  { code: `adopt Arcane.Serialization as Serde

// Simula linhas chegando de um arquivo grande
stream action linhas_do_log():
    dados := [
        "2026-01-10 INFO servidor iniciado",
        "2026-01-10 WARN memoria em 80%",
        "2026-01-10 ERROR falha ao conectar",
        "2026-01-11 INFO requisicao ok",
        "2026-01-11 ERROR timeout no banco",
        "2026-01-11 INFO requisicao ok"
    ]
    cycle l in dados:
        emit l

// Um estagio que interpreta cada linha
stream action interpretar(fonte):
    cycle linha in fonte:
        partes := linha.split(" ")
        emit {
            "data": partes[0],
            "nivel": partes[1],
            "mensagem": partes.slice(2).join(" ")
        }

// Um estagio que filtra
stream action apenas(fonte, nivel):
    cycle registro in fonte:
        given registro["nivel"] is nivel:
            emit registro

// A cadeia inteira, montada sem executar nada
erros := apenas(interpretar(linhas_do_log()), "ERROR")

out "── erros encontrados ──"
cycle e in erros:
    out $"  {e["data"]}: {e["mensagem"]}"

assert erros.count() is 2, "dois erros no log"

// Contar por nivel sem materializar o log inteiro
contagem := {}
cycle registro in interpretar(linhas_do_log()):
    nivel := registro["nivel"]
    contagem[nivel] := contagem.get(nivel, 0) + 1

out ""
out contagem
assert contagem["INFO"] is 3, "tres INFO"
assert contagem["ERROR"] is 2, "dois ERROR"

// Primeiro que satisfaz, sem ler o resto
primeiro_erro := apenas(interpretar(linhas_do_log()), "ERROR").first()
out ""
out $"primeiro erro: {primeiro_erro["mensagem"]}"
assert primeiro_erro["mensagem"] is "falha ao conectar", "para no primeiro"`, lang: 'df', title: `exercicios/15-streams-e-generators/148_stream_leitura.df` },
  {"h3": "O problema"},
  {"p": "Um arquivo de log com um milhão de linhas. Você quer os erros. A forma ansiosa:"},
  { code: `linhas := IO.read("app.log").lines()      // 1 milhão de strings na memória
registros := linhas >> morph interpretar   // mais 1 milhão de vaults
erros := registros >> sift e: e["nivel"] is "ERROR"`, lang: 'df' },
  {"p": "Três cópias completas dos dados, e você talvez só queira ver o primeiro erro."},
  {"h3": "A forma incremental"},
  {"p": "Cada estágio é um `stream action` que consome o anterior:"},
  { code: `stream action interpretar(fonte):
    cycle linha in fonte:
        emit {...}

stream action apenas(fonte, nivel):
    cycle registro in fonte:
        given registro["nivel"] is nivel:
            emit registro

erros := apenas(interpretar(linhas_do_log()), "ERROR")`, lang: 'df' },
  {"p": "Montar a cadeia **não lê nada**. Uma linha entra, atravessa os três estágios, sai — e só então a próxima começa. A memória usada é a de uma linha, não a de um milhão."},
  {"h3": "O ganho fica óbvio em `first()`"},
  { code: `primeiro_erro := apenas(interpretar(linhas_do_log()), "ERROR").first()`, lang: 'df' },
  {"p": "Isso lê até o primeiro erro e **para**. Se ele estiver na linha 3, as outras 999.997 nunca são tocadas."},
  {"h3": "O padrão de três estágios"},
  {"p": "Vale para praticamente todo processamento de dados:"},
  {"p": "1. **Origem** — produz os itens brutos (`linhas_do_log`) 2. **Transformação** — dá estrutura a cada item (`interpretar`) 3. **Filtro** — descarta o que não interessa (`apenas`)"},
  {"p": "Separados assim, cada estágio é testável e reutilizável isoladamente."},
  {"h3": "Contando sem materializar"},
  { code: `contagem := {}
cycle registro in interpretar(linhas_do_log()):
    nivel := registro["nivel"]
    contagem[nivel] := contagem.get(nivel, 0) + 1`, lang: 'df' },
  {"p": "O acumulador cresce com o número de **níveis distintos** (3), não com o número de linhas. Essa é a diferença entre um agregado e uma cópia."},
  {"h3": "Saída esperada"},
  { code: `── erros encontrados ──
  2026-01-10: falha ao conectar
  2026-01-11: timeout no banco

{INFO: 3, WARN: 1, ERROR: 2}

primeiro erro: falha ao conectar`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Troque `linhas_do_log` por `IO.read(\"arquivo.log\").lines()` e mantenha o resto.", "Acrescente um estágio que só passa registros de uma data.", "Escreva `ultimo(stream)` — por que ele precisa consumir tudo?"]},
  {"h2": "149 · observe e eventos"},
  {"p": "**Enunciado.** reaja a valores conforme eles chegam."},
  { code: `// observe percorre uma fonte reagindo a cada item
recebidos := []
observe valor in [10, 20, 30]:
    recebidos.append(valor * 2)

out recebidos
assert recebidos is [20, 40, 60], "reagiu a cada item"

// halt e skip funcionam dentro do observe
selecionados := []
observe n in [1, 2, 3, 4, 5, 6, 7]:
    given n % 2 is 0:
        skip
    given n bigger 5:
        halt
    selecionados.append(n)

out selecionados
assert selecionados is [1, 3, 5], "impares ate 5"

// stream() cria uma fonte a partir de uma colecao
fonte := stream([1, 2, 3])
soma := 0
observe v in fonte:
    soma += v
assert soma is 6, "somou o stream"

// Observando um generator
stream action temperaturas():
    emit 18
    emit 25
    emit 31
    emit 28

alertas := []
observe t in temperaturas():
    given t bigger 30:
        alertas.append($"alerta: {t} graus")

out alertas
assert len(alertas) is 1, "um alerta"

// Um padrao de assinantes
assinantes := []

action inscrever(fn):
    assinantes.append(fn)
    yield len(assinantes)

action publicar(evento):
    cycle fn in assinantes:
        fn(evento)
    yield len(assinantes)

log := []
inscrever(lambda e: log.append($"A viu {e}"))
inscrever(lambda e: log.append($"B viu {e}"))
publicar("inicio")
publicar("fim")

out log
assert len(log) is 4, "dois assinantes, dois eventos"
assert log[0] is "A viu inicio", "ordem preservada"`, lang: 'df', title: `exercicios/15-streams-e-generators/149_observe_reativo.df` },
  {"h3": "Conceitos"},
  {"p": "`observe` percorre uma fonte executando um bloco a cada item:"},
  { code: `observe valor in [10, 20, 30]:
    recebidos.append(valor * 2)`, lang: 'df' },
  {"p": "A forma é a mesma de `cycle`, mas a intenção é diferente:"},
  {"table": {"head": ["", "`cycle`", "`observe`"], "rows": [["Intenção", "percorrer uma coleção", "reagir a itens que chegam"], ["Fonte típica", "lista pronta", "stream, eventos, sensores"], ["Leitura", "\"para cada item\"", "\"sempre que chegar um item\""]]}},
  {"p": "Tecnicamente ambos funcionam sobre listas e streams. Usar `observe` sinaliza ao leitor que a fonte é um fluxo, não uma coleção parada."},
  {"h3": "`halt` e `skip`"},
  {"p": "Funcionam igual ao laço:"},
  { code: `observe n in [1, 2, 3, 4, 5, 6, 7]:
    given n % 2 is 0:
        skip          // ignora este e vai ao próximo
    given n bigger 5:
        halt          // para de observar
    selecionados.append(n)`, lang: 'df' },
  {"h3": "`stream(colecao)`"},
  {"p": "Converte uma coleção pronta numa fonte:"},
  { code: `fonte := stream([1, 2, 3])
observe v in fonte:
    soma += v`, lang: 'df' },
  {"p": "Útil para testar código que espera um fluxo, sem precisar escrever um `stream action`."},
  {"h3": "O padrão de assinantes"},
  {"p": "Quando os eventos não vêm de uma sequência, mas de chamadas espalhadas pelo código, o desenho é outro — uma lista de funções e uma ação que as chama:"},
  { code: `assinantes := []

action inscrever(fn):
    assinantes.append(fn)

action publicar(evento):
    cycle fn in assinantes:
        fn(evento)`, lang: 'df' },
  {"p": "Quem publica não sabe quem escuta, e quem escuta não sabe quem publica. É o padrão Observer, e é a base de quase todo sistema de eventos."},
  {"p": "Note que `inscrever(lambda e: log.append(...))` funciona porque a lambda é um valor como qualquer outro — pode ser guardada numa lista e chamada depois."},
  {"h3": "Saída esperada"},
  { code: `[20, 40, 60]
[1, 3, 5]
[alerta: 31 graus]
[A viu inicio, B viu inicio, A viu fim, B viu fim]`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Faça `inscrever` devolver uma ação que cancela a inscrição.", "Acrescente um filtro: `inscrever_se(condicao, fn)`.", "Combine `observe` com um generator infinito e um `halt` na condição de parada."]},
  {"h2": "150 · Projeto: ETL com streams"},
  {"p": "**Enunciado.** monte um pipeline de extracao, transformacao e carga usando generators."},
  { code: `adopt Arcane.Serialization as Serde
adopt Arcane.Collections as Col

// ── EXTRACAO: a origem dos dados brutos ──
stream action extrair():
    linhas := [
        "  ANA SILVA,ana@Exemplo.COM, 30, vendas, 5500",
        "bruno costa,bruno@teste.org,25,ti,7200",
        "linha malformada",
        "CARLA DIAS, carla@x.com,41, vendas,9100",
        "diego alves,invalido,29,ti,6300",
        "elena rocha,elena@y.com,abc,rh,4800"
    ]
    cycle l in linhas:
        emit l

// ── TRANSFORMACAO: um estagio por responsabilidade ──
stream action separar(fonte):
    cycle linha in fonte:
        campos := linha.split(",")
        given len(campos) is 5:
            emit campos
        otherwise:
            emit {"__erro__": $"campos de menos: '{linha.trim()}'"}

stream action limpar(fonte):
    cycle item in fonte:
        match item:
            point {"__erro__": e}:
                emit item
            point [nome, email, idade, setor, salario]:
                emit {
                    "nome": nome.trim().title(),
                    "email": email.trim().lower(),
                    "idade": idade.trim(),
                    "setor": setor.trim().lower(),
                    "salario": salario.trim()
                }
            default:
                emit {"__erro__": "formato inesperado"}

stream action validar(fonte):
    cycle registro in fonte:
        given "__erro__" in registro:
            emit registro
        otherwise:
            problemas := []
            given "@" not in registro["email"]:
                problemas.append("email invalido")
            given not registro["idade"].isdigit():
                problemas.append("idade nao numerica")
            given len(problemas) bigger 0:
                emit {"__erro__": $"{registro["nome"]}: {problemas.join(", ")}"}
            otherwise:
                emit {
                    "nome": registro["nome"],
                    "email": registro["email"],
                    "idade": cast registro["idade"] as Integer,
                    "setor": registro["setor"],
                    "salario": cast registro["salario"] as Integer
                }

// ── CARGA: separa o que passou do que falhou ──
validos := []
rejeitados := []

observe registro in validar(limpar(separar(extrair()))):
    given "__erro__" in registro:
        rejeitados.append(registro["__erro__"])
    otherwise:
        validos.append(registro)

out "── carregados ──"
cycle v in validos:
    out $"  {v["nome"].pad_end(12)} {v["setor"].pad_end(8)} R$ {v["salario"]}"

out ""
out "── rejeitados ──"
cycle r in rejeitados:
    out $"  {r}"

// ── RELATORIO ──
out ""
out "── por setor ──"
por_setor := Col.group_by(validos, "setor")
cycle setor in por_setor.keys():
    salarios := por_setor[setor] >> morph p: p["salario"]
    out $"  {setor.pad_end(8)} n={len(salarios)}  media=R$ {round(mean(salarios), 2)}"

folha := validos >> morph v: v["salario"] >> distill acc, s: acc + s 0
out ""
out $"folha total: R$ {folha}"
out $"aproveitamento: {len(validos)}/{len(validos) + len(rejeitados)}"

assert len(validos) is 3, "tres registros validos"
assert len(rejeitados) is 3, "tres rejeitados"
assert folha is 21800, "5500 + 9100 + 7200"
assert por_setor["vendas"].length() is 2, "duas pessoas em vendas"`, lang: 'df', title: `exercicios/15-streams-e-generators/150_projeto_etl.df` },
  {"h3": "A arquitetura"},
  { code: `extrair()  →  separar()  →  limpar()  →  validar()  →  observe
   ↓             ↓            ↓            ↓             ↓
 origem      estrutura    normaliza     verifica     carrega`, lang: 'text' },
  {"p": "Cada estágio é um `stream action` que consome o anterior. A linha que monta tudo:"},
  { code: `observe registro in validar(limpar(separar(extrair()))):`, lang: 'df' },
  {"p": "Nada roda até o `observe` pedir o primeiro item. Depois, cada linha atravessa os quatro estágios individualmente."},
  {"h3": "Um estágio, uma responsabilidade"},
  {"table": {"head": ["Estágio", "Faz", "Não faz"], "rows": [["`extrair`", "produz linhas brutas", "não interpreta"], ["`separar`", "quebra em campos", "não limpa"], ["`limpar`", "normaliza caixa e espaços", "não valida"], ["`validar`", "verifica e converte tipos", "não decide o destino"]]}},
  {"p": "Essa separação não é preciosismo. Quando o formato de entrada mudar de CSV para JSON, só `separar` muda. Quando a regra de e-mail mudar, só `validar` muda."},
  {"h3": "Erros que atravessam o pipeline"},
  {"p": "O ponto mais delicado de um ETL: **uma linha ruim não pode derrubar as outras**."},
  {"p": "A solução aqui é fazer o erro viajar como um dado:"},
  { code: `emit {"__erro__": $"campos de menos: '{linha.trim()}'"}`, lang: 'df' },
  {"p": "Cada estágio seguinte reconhece o marcador e o repassa intacto:"},
  { code: `match item:
    point {"__erro__": e}:
        emit item              // passa adiante sem tocar
    point [nome, email, ...]:
        emit {...}             // processa normalmente`, lang: 'df' },
  {"p": "No fim, o consumidor separa os dois fluxos. Ninguém perde dado e ninguém para o processamento por causa de uma linha torta."},
  {"p": "Um `monitor` em volta de tudo não resolveria: ele abortaria o pipeline inteiro na primeira linha ruim."},
  {"h3": "Normalizar na entrada"},
  { code: `"nome": nome.trim().title(),        // "  ANA SILVA " → "Ana Silva"
"email": email.trim().lower(),      // " ana@Exemplo.COM " → "ana@exemplo.com"`, lang: 'df' },
  {"p": "Dados de fora chegam sujos. Limpar **uma vez**, na fronteira, evita ter que lembrar disso em cada consulta depois."},
  {"h3": "Converter só depois de validar"},
  { code: `given not registro["idade"].isdigit():
    problemas.append("idade nao numerica")
...
"idade": cast registro["idade"] as Integer`, lang: 'df' },
  {"p": "A ordem importa: `cast \"abc\" as Integer` dispara erro. Verificar primeiro transforma uma exceção num registro rejeitado com mensagem clara."},
  {"h3": "Saída esperada"},
  { code: `── carregados ──
  Ana Silva    vendas   R$ 5500
  Bruno Costa  ti       R$ 7200
  Carla Dias   vendas   R$ 9100

── rejeitados ──
  campos de menos: 'linha malformada'
  Diego Alves: email invalido
  Elena Rocha: idade nao numerica

── por setor ──
  vendas   n=2  media=R$ 7300.0
  ti       n=1  media=R$ 7200.0

folha total: R$ 21800
aproveitamento: 3/6`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente um estágio `deduplicar` que descarta e-mails repetidos.", "Grave os rejeitados num CSV com `Serde.records_to_csv`.", "Faça `extrair` ler de um arquivo real com `IO.read(...).lines()`."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/15-streams-e-generators/145_generator_basico.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '145-generators-com-stream-action', text: "145 · Generators com stream action", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'emit-e-yield-sao-coisas-diferentes', text: "`emit` e `yield` são coisas diferentes", level: 3 as const }, { id: 'consumindo-um-stream', text: "Consumindo um stream", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '146-sequencias-infinitas', text: "146 · Sequencias infinitas", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'por-que-isso-funciona', text: "Por que isso funciona", level: 3 as const }, { id: 'o-que-isso-permite', text: "O que isso permite", level: 3 as const }, { id: 'parando-por-dentro', text: "Parando por dentro", level: 3 as const }, { id: 'cuidado', text: "Cuidado", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '147-streams-com-pipelines', text: "147 · Streams com pipelines", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'metodos-diretos-no-stream', text: "Métodos diretos no stream", level: 3 as const }, { id: 'compreensoes-consomem-streams', text: "Compreensões consomem streams", level: 3 as const }, { id: 'encadear-generators', text: "Encadear generators", level: 3 as const }, { id: 'quando-escolher-cada-um', text: "Quando escolher cada um", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '148-processamento-incremental', text: "148 · Processamento incremental", level: 2 as const }, { id: 'o-problema', text: "O problema", level: 3 as const }, { id: 'a-forma-incremental', text: "A forma incremental", level: 3 as const }, { id: 'o-ganho-fica-obvio-em-first', text: "O ganho fica óbvio em `first()`", level: 3 as const }, { id: 'o-padrao-de-tres-estagios', text: "O padrão de três estágios", level: 3 as const }, { id: 'contando-sem-materializar', text: "Contando sem materializar", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '149-observe-e-eventos', text: "149 · observe e eventos", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'halt-e-skip', text: "`halt` e `skip`", level: 3 as const }, { id: 'streamcolecao', text: "`stream(colecao)`", level: 3 as const }, { id: 'o-padrao-de-assinantes', text: "O padrão de assinantes", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '150-projeto-etl-com-streams', text: "150 · Projeto: ETL com streams", level: 2 as const }, { id: 'a-arquitetura', text: "A arquitetura", level: 3 as const }, { id: 'um-estagio-uma-responsabilidade', text: "Um estágio, uma responsabilidade", level: 3 as const }, { id: 'erros-que-atravessam-o-pipeline', text: "Erros que atravessam o pipeline", level: 3 as const }, { id: 'normalizar-na-entrada', text: "Normalizar na entrada", level: 3 as const }, { id: 'converter-so-depois-de-validar', text: "Converter só depois de validar", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"15 · Streams"}
      description={"6 exercícios: stream action, emit, take e sequências infinitas."}
      href={"/docs/exercicios/15-streams-e-generators"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
