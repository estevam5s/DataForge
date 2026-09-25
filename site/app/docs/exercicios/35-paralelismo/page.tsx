// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "35 · Paralelismo",
  description: "3 exercícios: vários núcleos de verdade, o que atravessa para outro processo.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Aplicações** · vários núcleos de verdade, o que atravessa para outro processo · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 35`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[238](#238-varios-nucleos-de-verdade)", "**Varios nucleos, de verdade**", "meca a diferenca entre thread e processo em trabalho de CPU."], ["[239](#239-o-que-atravessa-para-o-outro-processo)", "**O que atravessa para o outro processo**", "descubra o que viaja junto com a acao, e o que fica."], ["[240](#240-um-pipeline-que-usa-a-maquina-inteira)", "**Um pipeline que usa a maquina inteira**", "divida, calcule em paralelo, junte — e prove que bate."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "238 · Varios nucleos, de verdade"},
  {"p": "**Enunciado.** meca a diferenca entre thread e processo em trabalho de CPU."},
  { code: `adopt Arcane.Concurrent as P
adopt Arcane.Time as Time

// ── O problema ──────────────────────────────────────────────
//
// 'async', 'thread' e 'parallel' usam threads do Python, e duas
// threads do Python nunca executam bytecode ao mesmo tempo — e o GIL.
//
//     trabalho que ESPERA (rede, disco, banco)  ->  thread
//     trabalho que CALCULA (numeros, imagem)    ->  processo
//
// Para o primeiro caso a thread e perfeita: ela solta o GIL enquanto
// espera, e dez downloads acontecem juntos. Para o segundo, oito
// threads levam o mesmo tempo que uma.

out $"nucleos disponiveis: {P.nucleos()}"

action cpu(n):
    soma := 0
    cycle i from 1 to n:
        soma += i * i
    yield soma

steady BLOCOS := [150000, 150000, 150000, 150000]

action cronometrar(f):
    inicio := Time.monotonic()
    valor := f()
    yield {"ms": (Time.monotonic() - inicio) * 1000, "valor": valor}

serie := cronometrar(lambda => [cpu(b) cycle b in BLOCOS])
threads := cronometrar(lambda => P.map(cpu, BLOCOS))
processos := cronometrar(lambda => P.map_processos(cpu, BLOCOS))

// ── O resultado tem de ser o mesmo pelos tres caminhos ──────

assert serie["valor"] is threads["valor"], "as threads mudaram o resultado"
assert serie["valor"] is processos["valor"], "os processos mudaram o resultado"

out $"serie:     {round(serie['ms'])} ms"
out $"threads:   {round(threads['ms'])} ms"
out $"processos: {round(processos['ms'])} ms"

ganho_threads := serie["ms"] / threads["ms"]
ganho_processos := serie["ms"] / processos["ms"]

out $"threads   x{round(ganho_threads, 2)}"
out $"processos x{round(ganho_processos, 2)}"

// ── O que os numeros provam ─────────────────────────────────
//
// A comparacao e sempre com a SERIE medida na mesma maquina. Um
// limite absoluto ("menos de 200 ms") mediria a maquina, e nao o
// paralelismo — e reprovaria num runner ocupado que esta certissimo.

given P.nucleos() >= 4:
    assert ganho_processos bigger 1.2,
    "os processos nao ganharam da serie: a travessia voltou a rodar num nucleo so"
    assert ganho_threads < 1.5,
    "as threads ganharam em trabalho de CPU — se o GIL sumiu, este exercicio e que mudou"

out "ok"`, lang: 'df', title: `exercicios/35-paralelismo/238_varios_nucleos.df` },
  {"h3": "A pergunta que decide tudo"},
  {"p": "O trabalho **espera** ou **calcula**?"},
  {"table": {"head": ["O trabalho", "Use", "Por quê"], "rows": [["espera (rede, disco, banco, `sleep`)", "`P.map` — threads", "a thread solta o GIL enquanto espera, e dez downloads acontecem juntos"], ["calcula (números, imagem, parsing)", "`P.map_processos` — processos", "duas threads do Python nunca executam bytecode ao mesmo tempo"]]}},
  {"p": "O GIL — *Global Interpreter Lock* — é a razão. Ele é do CPython, não do DataForge: `async`, `thread` e `parallel` são threads do Python, e por isso nenhum dos três usa mais de um núcleo para contas."},
  {"h3": "O que este exercício mede"},
  {"p": "Quatro blocos de 150 mil multiplicações, pelos três caminhos:"},
  { code: `serie := cronometrar(lambda => [cpu(b) cycle b in BLOCOS])
threads := cronometrar(lambda => P.map(cpu, BLOCOS))
processos := cronometrar(lambda => P.map_processos(cpu, BLOCOS))`, lang: 'df' },
  {"p": "Numa máquina de 10 núcleos:"},
  {"table": {"head": ["Como", "Tempo", "Ganho"], "rows": [["em série", "598 ms", "—"], ["`P.map` — threads", "610 ms", "**0,97x**"], ["`P.map_processos` — processos", "302 ms", "**1,98x**"]]}},
  {"p": "As threads não só deixaram de ganhar: ficaram um pouco **mais lentas** que a série. É o custo de trocar de contexto sem nada a ganhar em troca — e é o resultado esperado, não um defeito."},
  {"h3": "Por que a comparação é com a série, e não com um número"},
  { code: `assert ganho_processos bigger 1.2      // certo
assert processos["ms"] < 200           // errado`, lang: 'df' },
  {"p": "Um limite absoluto mede a **máquina**, e não o paralelismo: num runner de CI ocupado, quatro processos perfeitamente paralelos levam mais de 200 ms. A razão contra a série medida na mesma máquina, no mesmo instante, é o que significa alguma coisa."},
  {"p": "E a razão é cobrada **com fator** (`bigger 1.2`), não com `bigger 1`: o segundo passa por acidente metade das vezes."},
  {"h3": "O que o exercício não afirma"},
  {"p": "O `assert` só roda quando há **quatro núcleos ou mais**:"},
  { code: `given P.nucleos() >= 4:
    assert ganho_processos bigger 1.2, …`, lang: 'df' },
  {"p": "Numa máquina de um núcleo, `map_processos` é mais lento que a série — e está certo. Cobrar ganho ali seria cobrar o impossível."},
  {"h3": "Onde isso continua"},
  {"list": ["[`239_o_que_atravessa.df`](239_o_que_atravessa.df) — o que viaja junto com a"]},
  {"p": "ação, e o que fica para trás"},
  {"list": ["[`240_pipeline_em_blocos.df`](240_pipeline_em_blocos.df) — dividir, calcular"]},
  {"p": "em paralelo, juntar, e conferir contra a resposta fechada"},
  {"h2": "239 · O que atravessa para o outro processo"},
  {"p": "**Enunciado.** descubra o que viaja junto com a acao, e o que fica."},
  { code: `adopt Arcane.Concurrent as P
adopt Arcane.Math as M
adopt Arcane.Database as DB

// ── O que viaja ─────────────────────────────────────────────
//
// Um processo recebe o trabalho por COPIA. O que atravessa nao e a
// acao — e a DECLARACAO dela, mais os nomes que ela le e nao cria, e
// tudo o que esses nomes alcancam. Nada disso precisa ser dito.

steady TAXA := 0.08

record Pedido:
    cliente: String
    valor: Float

enum Faixa:
    Comum
    Alta

record Nota:
    cliente: String
    total: Float
    faixa: Faixa

action imposto(v):
    yield v * TAXA

action faixa_de(v):
    yield Faixa.Alta given v bigger 200 otherwise Faixa.Comum

action emitir(p: Pedido) -> Nota:
    total := M.round(p.valor + imposto(p.valor), 2)
    yield Nota(p.cliente, total, faixa_de(total))

pedidos := [Pedido("ana", 100.0), Pedido("bia", 250.0), Pedido("caio", 30.0)]
notas := P.map_processos(emitir, pedidos)

cycle n in notas:
    out n

assert len(notas) is 3, "um item se perdeu na travessia"
assert notas[0].total is 108.0, "a steady TAXA nao atravessou"
assert notas[1].faixa is Faixa.Alta, "o enum nao atravessou"
assert notas[2].faixa is Faixa.Comum, "o enum nao atravessou"

// O tipo que VOLTA e o mesmo declarado aqui — e por isso 'with',
// que confere os campos contra o record, aceita o resultado.
copia := notas[0] with {"cliente": "outro"}
assert copia.cliente is "outro", "o record voltou como outro tipo"
assert copia.total is notas[0].total, "'with' nao preservou o resto"

// ── O que NAO viaja ─────────────────────────────────────────
//
// Uma conexao de banco, um arquivo aberto, um socket, um mutex, um
// canal e uma tarefa existem no processo que os abriu. Copia-los nao
// faria sentido: o outro lado ganharia um descritor que la nao aponta
// para nada.

banco := DB.connect(":memory:")

action usa_o_banco_de_fora(n):
    yield len(DB.query(banco, "select 1")) + n

monitor:
    P.map_processos(usa_o_banco_de_fora, [1, 2])
    assert no, "devia ter recusado"
handle Error as e:
    out e.message
    assert "banco" in e.message, "a mensagem tem de citar a VARIAVEL pelo nome"

// ── E o que fazer a respeito ────────────────────────────────
//
// Abrir o recurso DENTRO da acao: cada processo abre o seu.

action abre_o_proprio(n):
    meu := DB.connect(":memory:")
    DB.execute(meu, "create table t (n integer)")
    DB.execute(meu, "insert into t values (?)", [n])
    yield DB.count(meu, "t") * n

assert P.map_processos(abre_o_proprio, [2, 3, 4]) is [2, 3, 4]

// Um recurso que a acao NAO usa nao atrapalha: a analise so cobra o
// nome quando ele faz falta de verdade.
_trava := P.mutex()
_canal := P.canal()

action nao_usa_nada_de_fora(n):
    yield n * 10

assert P.map_processos(nao_usa_nada_de_fora, [1, 2, 3]) is [10, 20, 30]

out "ok"`, lang: 'df', title: `exercicios/35-paralelismo/239_o_que_atravessa.df` },
  {"h3": "A regra"},
  {"p": "Um processo recebe o trabalho por **cópia**. O que atravessa não é a ação — é a **declaração** dela, mais os nomes que ela lê e não cria, mais tudo o que esses nomes alcançam."},
  { code: `steady TAXA := 0.08

record Pedido:
    cliente: String
    valor: Float

action imposto(v):
    yield v * TAXA

action emitir(p):
    yield Nota(p.cliente, p.valor + imposto(p.valor))

P.map_processos(emitir, pedidos)`, lang: 'df' },
  {"p": "Atravessam junto, sem que nada disso precise ser dito:"},
  {"list": ["a `steady TAXA`, porque `imposto` a lê", "a ação `imposto`, porque `emitir` a chama", "os `record` e o `enum`, porque são construídos lá dentro", "o módulo `Arcane.Math` — **pelo nome**: o outro lado o carrega de novo, em vez"]},
  {"p": "de recebê-lo copiado"},
  {"h3": "O record que volta é o mesmo tipo"},
  { code: `copia := notas[0] with {"cliente": "outro"}`, lang: 'df' },
  {"p": "`with` confere os campos contra o record. Se o processo filho devolvesse uma **cópia** do tipo, essa linha recusaria o próprio resultado — e o erro falaria de um `Nota` que não é o `Nota`, o que é impossível de entender."},
  {"h3": "O que não atravessa"},
  {"p": "Uma conexão de banco, um arquivo aberto, um socket, um mutex, um canal e uma tarefa existem no processo que os abriu. Copiá-los não faria sentido: o outro lado ganharia um número de descritor que lá não aponta para nada."},
  { code: `erro[DF1001]: 'banco' cannot cross into another process
  = nota: it holds a connection to a database, which exists only in
          the process that opened it
  = dica: open it INSIDE the action — each process opens its own — or
          use 'map', which uses threads and shares memory`, lang: 'text' },
  {"p": "A mensagem chama a **variável pelo nome**. Isso importa mais do que parece: a mensagem antiga citava um objeto interno da biblioteca (`<locals>.<lambda>`) e mandava \"declarar a ação no topo do arquivo\" — que era onde ela já estava."},
  {"h3": "A saída: abrir dentro da ação"},
  { code: `action abre_o_proprio(n):
    meu := DB.connect(":memory:")
    …`, lang: 'df' },
  {"p": "Cada processo abre o seu. É também o desenho certo para um banco de verdade: uma conexão compartilhada entre processos seria um gargalo, mesmo se pudesse ser copiada."},
  {"h3": "O que a análise NÃO faz"},
  {"p": "Um recurso que a ação não usa não atrapalha:"},
  { code: `_trava := P.mutex()
_canal := P.canal()

action nao_usa_nada_de_fora(n):
    yield n * 10           // atravessa sem problema`, lang: 'df' },
  {"p": "A varredura de nomes livres é **generosa de propósito** — na dúvida, captura — e por isso um nome que não pôde atravessar só vira erro **quando a ação realmente o usa**. Reclamar na hora seria falso alarme, e falso alarme ensina a desligar a verificação."},
  {"h3": "Onde isso continua"},
  {"list": ["[`238_varios_nucleos.df`](238_varios_nucleos.df) — a medida que prova o ganho", "[`240_pipeline_em_blocos.df`](240_pipeline_em_blocos.df) — o desenho completo"]},
  {"h2": "240 · Um pipeline que usa a maquina inteira"},
  {"p": "**Enunciado.** divida, calcule em paralelo, junte — e prove que bate."},
  { code: `adopt Arcane.Concurrent as P
adopt Arcane.Time as Time

// ── O desenho ───────────────────────────────────────────────
//
//     dividir  ->  map_processos  ->  juntar
//
// Cada bloco tem de ser autossuficiente: ele atravessa para outro
// processo, faz a conta la, e volta com um resumo pequeno. O que
// atravessa custa — mandar o bloco e receber UM numero e barato;
// mandar o bloco e receber outro bloco nao e.

steady TOTAL := 60000
steady BLOCOS := 6

action dividir(quantos, em):
    tamanho := quantos ~/ em
    yield [{"de":i * tamanho + 1, "ate":(i + 1) * tamanho}
        cycle i in range(0, em)]

// O bloco vira um RESUMO, e nao uma lista: e o resumo que volta.
action resumir(bloco):
    soma_do_bloco := 0
    primos_do_bloco := 0
    cycle n from bloco["de"] to bloco["ate"]:
        soma_do_bloco += n
        given e_primo(n):
            primos_do_bloco += 1
    yield {"soma": soma_do_bloco, "primos": primos_do_bloco}

action e_primo(n):
    given n < 2:
        yield no
    given n % 2 is 0:
        yield n is 2
    d := 3
    persist d * d <= n:
        given n % d is 0:
            yield no
        d += 2
    yield yes

blocos := dividir(TOTAL, BLOCOS)
assert len(blocos) is BLOCOS, "a divisao errou a contagem"
assert blocos[0]["de"] is 1
assert blocos[BLOCOS - 1]["ate"] is TOTAL, "o ultimo bloco nao fecha o total"

inicio := Time.monotonic()
resumos := P.map_processos(resumir, blocos)
ms := (Time.monotonic() - inicio) * 1000

soma := sum([r["soma"] cycle r in resumos])
primos := sum([r["primos"] cycle r in resumos])

out $"{BLOCOS} blocos de {TOTAL ~/ BLOCOS} em {round(ms)} ms"
out $"soma:   {soma}"
out $"primos: {primos}"

// ── A conferencia ───────────────────────────────────────────
//
// Um pipeline paralelo que nao e conferido contra a resposta fechada
// e um gerador de numeros plausiveis. A soma de 1 a n tem formula:

esperado := TOTAL * (TOTAL + 1) ~/ 2
assert soma is esperado, $"a soma deu {soma}, e devia ser {esperado}"
assert primos is 6057, "a contagem de primos ate 60000 e conhecida"

// A ordem da entrada e a da saida — sem isso, quem chama teria de
// reassociar bloco e resumo, e e ai que se erra.
assert resumos[0]["soma"] < resumos[BLOCOS - 1]["soma"],
"os resumos voltaram fora de ordem"

out "ok"`, lang: 'df', title: `exercicios/35-paralelismo/240_pipeline_em_blocos.df` },
  {"h3": "O desenho"},
  { code: `dividir  ->  map_processos  ->  juntar`, lang: 'text' },
  {"p": "Cada bloco tem de ser **autossuficiente**: ele atravessa para outro processo, faz a conta lá, e volta."},
  {"h3": "A decisão que mais importa: o que volta"},
  { code: `action resumir(bloco):
    soma := 0
    primos := 0
    cycle n from bloco["de"] to bloco["ate"]:
        …
    yield {"soma": soma, "primos": primos}`, lang: 'df' },
  {"p": "O bloco vira um **resumo**, e não uma lista. Mandar dez mil números e receber dois de volta é barato; mandar dez mil e receber dez mil paga a travessia duas vezes, e aí os processos perdem para a série."},
  {"p": "É a mesma conta do `map_processos` em geral: ele vale a partir de **alguns milissegundos de trabalho por item**."},
  {"h3": "A conferência"},
  {"p": "Um pipeline paralelo que não é conferido contra uma resposta fechada é um gerador de números plausíveis. Aqui há duas âncoras:"},
  { code: `esperado := TOTAL * (TOTAL + 1) ~/ 2
assert soma is esperado
assert primos is 6057        // π(60000), que é uma constante conhecida`, lang: 'df' },
  {"p": "A primeira é uma fórmula; a segunda, um valor tabelado. Nenhuma das duas vem do próprio programa — que é o ponto."},
  {"h3": "A ordem"},
  { code: `assert resumos[0]["soma"] < resumos[BLOCOS - 1]["soma"]`, lang: 'df' },
  {"p": "`map_processos` devolve **na ordem da entrada**, e não na ordem em que os processos terminaram. Sem essa garantia, quem chama teria de reassociar bloco e resumo — e é aí que se erra."},
  {"h3": "Medido"},
  {"p": "Seis blocos de dez mil, numa máquina de 10 núcleos: **426% de CPU**. O programa usou quatro núcleos e um pouco, que é o que seis blocos permitem quando cada um custa o mesmo."},
  {"h3": "Onde isso continua"},
  {"list": ["[`238_varios_nucleos.df`](238_varios_nucleos.df) — a medida do ganho", "[`239_o_que_atravessa.df`](239_o_que_atravessa.df) — o que viaja e o que fica"]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/35-paralelismo/238_varios_nucleos.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '238-varios-nucleos-de-verdade', text: "238 · Varios nucleos, de verdade", level: 2 as const }, { id: 'a-pergunta-que-decide-tudo', text: "A pergunta que decide tudo", level: 3 as const }, { id: 'o-que-este-exercicio-mede', text: "O que este exercício mede", level: 3 as const }, { id: 'por-que-a-comparacao-e-com-a-serie-e-nao-com-um-numero', text: "Por que a comparação é com a série, e não com um número", level: 3 as const }, { id: 'o-que-o-exercicio-nao-afirma', text: "O que o exercício não afirma", level: 3 as const }, { id: 'onde-isso-continua', text: "Onde isso continua", level: 3 as const }, { id: '239-o-que-atravessa-para-o-outro-processo', text: "239 · O que atravessa para o outro processo", level: 2 as const }, { id: 'a-regra', text: "A regra", level: 3 as const }, { id: 'o-record-que-volta-e-o-mesmo-tipo', text: "O record que volta é o mesmo tipo", level: 3 as const }, { id: 'o-que-nao-atravessa', text: "O que não atravessa", level: 3 as const }, { id: 'a-saida-abrir-dentro-da-acao', text: "A saída: abrir dentro da ação", level: 3 as const }, { id: 'o-que-a-analise-nao-faz', text: "O que a análise NÃO faz", level: 3 as const }, { id: 'onde-isso-continua', text: "Onde isso continua", level: 3 as const }, { id: '240-um-pipeline-que-usa-a-maquina-inteira', text: "240 · Um pipeline que usa a maquina inteira", level: 2 as const }, { id: 'o-desenho', text: "O desenho", level: 3 as const }, { id: 'a-decisao-que-mais-importa-o-que-volta', text: "A decisão que mais importa: o que volta", level: 3 as const }, { id: 'a-conferencia', text: "A conferência", level: 3 as const }, { id: 'a-ordem', text: "A ordem", level: 3 as const }, { id: 'medido', text: "Medido", level: 3 as const }, { id: 'onde-isso-continua', text: "Onde isso continua", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"35 · Paralelismo"}
      description={"3 exercícios: vários núcleos de verdade, o que atravessa para outro processo."}
      href={"/docs/exercicios/35-paralelismo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
