import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "15 · Streams e generators",
  description: "6 exercícios: `stream action`, `emit`, infinitos e ETL.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 15`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["145", "**Generators com stream action**", "produza valores um a um com emit, em vez de montar a lista inteira."], ["146", "**Sequencias infinitas**", "escreva um generator sem fim e consuma so o que precisa."], ["147", "**Streams com pipelines**", "combine generators com sift, morph e distill."], ["148", "**Processamento incremental**", "use streams para tratar dados grandes sem carregar tudo na memoria."], ["149", "**observe e eventos**", "reaja a valores conforme eles chegam."], ["150", "**Projeto: ETL com streams**", "monte um pipeline de extracao, transformacao e carga usando generators."]]}},
  {"h2": "145 · Generators com stream action"},
  {"p": "Produza valores um a um com emit, em vez de montar a lista inteira."},
  { code: `// Exercicio 145 — Generators com stream action
// Enunciado: produza valores um a um com emit, em vez de montar a lista inteira.

// Um stream action produz valores com 'emit'
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
assert pares_ate(10).count() is 6, "0, 2, 4, 6, 8, 10"
`, title: `145_generator_basico.df` },
  {"h2": "146 · Sequencias infinitas"},
  {"p": "Escreva um generator sem fim e consuma so o que precisa."},
  { code: `// Exercicio 146 — Sequencias infinitas
// Enunciado: escreva um generator sem fim e consuma so o que precisa.

// Um laco infinito num generator e legitimo: nada roda ate alguem pedir
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
assert g.next() is 3, "a quarta chamada devolve 3"
`, title: `146_generator_infinito.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 4 exercícios deste módulo estão em `exercicios/15-streams-e-generators/`. Cada um tem um `.md` ao lado com a explicação completa."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '145--generators-com-stream-action', text: "145 · Generators com stream action", level: 2 as const }, { id: '146--sequencias-infinitas', text: "146 · Sequencias infinitas", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"15 · Streams e generators"}
      description={"6 exercícios: `stream action`, `emit`, infinitos e ETL."}
      href={"/exercicios/15-streams-e-generators"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
