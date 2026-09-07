import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "02 · Controle de fluxo",
  description: "12 exercícios: condicionais, os quatro laços, `halt`/`skip` e `guard`.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 02`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["013", "**Condicional given**", "classifique um numero como positivo, negativo ou zero."], ["014", "**Condicionais aninhadas**", "converta uma nota de 0 a 10 em conceito A/B/C/D."], ["015", "**match / point / default**", "traduza o codigo de um dia da semana para o nome."], ["016", "**Laco cycle from/to**", "some os numeros de 1 a 100."], ["017", "**Laco com step**", "liste os pares de 0 a 10 e faca uma contagem regressiva."], ["018", "**Laco cycle in**", "percorra uma lista e um vault."], ["019", "**Laco persist (while)**", "calcule quantas vezes um numero pode ser dividido por 2."], ["020", "**Laco perform (do-while)**", "garanta que o corpo execute ao menos uma vez."], ["021", "**halt e skip**", "pule os multiplos de 3 e pare ao encontrar o primeiro maior que 10."], ["022", "**Lacos aninhados**", "imprima a tabuada de 1 a 3 e monte a matriz de produtos."], ["023", "**FizzBuzz**", "para 1..15, diga Fizz, Buzz, FizzBuzz ou o proprio numero."], ["024", "**guard como pre-condicao**", "use guard para sair cedo de uma acao com entrada invalida."]]}},
  {"h2": "013 · Condicional given"},
  {"p": "Classifique um numero como positivo, negativo ou zero."},
  { code: `// Exercicio 013 — Condicional given
// Enunciado: classifique um numero como positivo, negativo ou zero.

action classificar(n):
    given n bigger 0:
        yield "positivo"
    orif n smaller 0:
        yield "negativo"
    otherwise:
        yield "zero"

cycle n in [5, -3, 0]:
    out n, "->", classificar(n)

assert classificar(5) is "positivo", "positivo"
assert classificar(-3) is "negativo", "negativo"
assert classificar(0) is "zero", "zero"
`, title: `013_given_simples.df` },
  {"h2": "014 · Condicionais aninhadas"},
  {"p": "Converta uma nota de 0 a 10 em conceito A/B/C/D."},
  { code: `// Exercicio 014 — Condicionais aninhadas
// Enunciado: converta uma nota de 0 a 10 em conceito A/B/C/D.

action conceito(nota):
    given nota bigger_eq 9:
        yield "A"
    orif nota bigger_eq 7:
        yield "B"
    orif nota bigger_eq 5:
        yield "C"
    otherwise:
        yield "D"

cycle n in [10, 8, 6, 2]:
    out n, "->", conceito(n)

assert conceito(10) is "A", "A"
assert conceito(8) is "B", "B"
assert conceito(6) is "C", "C"
assert conceito(2) is "D", "D"
`, title: `014_given_aninhado.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 10 exercícios deste módulo estão em `exercicios/02-controle-fluxo/`. Rode-os com o comando acima."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '013--condicional-given', text: "013 · Condicional given", level: 2 as const }, { id: '014--condicionais-aninhadas', text: "014 · Condicionais aninhadas", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"02 · Controle de fluxo"}
      description={"12 exercícios: condicionais, os quatro laços, `halt`/`skip` e `guard`."}
      href={"/docs/exercicios/02-controle-fluxo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
