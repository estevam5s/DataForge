import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "02 · Controle fluxo",
  description: "12 exercícios: given/orif/otherwise, ternário, match e guardas.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 02`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["013", "**Condicional given**", "classifique um numero como positivo, negativo ou zero."], ["014", "**Condicionais aninhadas**", "converta uma nota de 0 a 10 em conceito A/B/C/D."], ["015", "**match / point / default**", "traduza o codigo de um dia da semana para o nome."], ["016", "**Laco cycle from/to**", "some os numeros de 1 a 100."], ["017", "**Laco com step**", "liste os pares de 0 a 10 e faca uma contagem regressiva."], ["018", "**Laco cycle in**", "percorra uma lista e um vault."], ["019", "**Laco persist (while)**", "calcule quantas vezes um numero pode ser dividido por 2."], ["020", "**Laco perform (do-while)**", "garanta que o corpo execute ao menos uma vez."], ["021", "**halt e skip**", "pule os multiplos de 3 e pare ao encontrar o primeiro maior que 10."], ["022", "**Lacos aninhados**", "imprima a tabuada de 1 a 3 e monte a matriz de produtos."], ["023", "**FizzBuzz**", "para 1..15, diga Fizz, Buzz, FizzBuzz ou o proprio numero."], ["024", "**guard como pre-condicao**", "use guard para sair cedo de uma acao com entrada invalida."]]}},
  {"p": "Rode um isolado com `dataforge run exercicios/02-controle-fluxo/013_given_simples.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"02 · Controle fluxo"}
      description={"12 exercícios: given/orif/otherwise, ternário, match e guardas."}
      href={"/docs/exercicios/02-controle-fluxo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
