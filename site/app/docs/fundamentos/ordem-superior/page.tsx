// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fundamentos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ações como valores",
  description: "Passar uma ação para outra, devolver uma ação, lambda — e o pipeline como a forma idiomática.",
};

const blocos: Bloco[] = [
  {"p": "Uma ação é um valor como outro qualquer: pode ser guardada numa variável, passada como argumento e devolvida por outra ação. É o que permite escrever `ordenar(pessoas, pela_idade)` em vez de uma ordenação nova para cada campo."},
  { code: `action aplicar_duas_vezes(f, x):
    yield f(f(x))

dobro := lambda n: n * 2
assert aplicar_duas_vezes(dobro, 3) is 12

// Uma acao que DEVOLVE uma acao.
action multiplicador(k):
    yield lambda n: n * k

triplo := multiplicador(3)
assert triplo(5) is 15

pessoas := [{"nome": "Bia", "idade": 30}, {"nome": "Ana", "idade": 25}]
assert sorted(pessoas, lambda p: p["idade"])[0]["nome"] is "Ana"`, lang: 'df' },
  {"h2": "O pipeline"},
  { code: `vendas := [120, 45, 300, 80, 15]

// filtrar, transformar, reduzir — lido de cima para baixo
total := vendas
    >> sift v: v bigger_eq 50
    >> morph v: v * 0.9
    >> distill acc, v: acc + v 0

assert total is 450.0`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Um pipeline dentro de um lambda precisa de parênteses", "texto": "`lambda => xs >> morph x: x * 2` canaliza o **lambda**, e não `xs`. A forma certa é `lambda => (xs >> morph x: x * 2)`. E um ternário no corpo de `morph` também: `morph n: (n given n bigger 0 otherwise 0)`."}},
  {"p": "Continue em [Closures](/docs/fundamentos/closures) e [Pipelines](/docs/pipelines)."},
];

const headings = [{ id: 'o-pipeline', text: "O pipeline", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ações como valores"}
      description={"Passar uma ação para outra, devolver uma ação, lambda — e o pipeline como a forma idiomática."}
      href={"/docs/fundamentos/ordem-superior"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
