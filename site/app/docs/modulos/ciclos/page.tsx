// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ciclos de import",
  description: "Por que A → B → A não sobe, como o check mostra a cadeia, e as três formas de quebrá-la.",
};

const blocos: Bloco[] = [
  {"p": "Um ciclo de import é `a.df` adotando `b.df`, que adota `a.df`. Para carregar `a`, é preciso `b`; para carregar `b`, é preciso `a`. O `check` acusa antes de rodar, e mostra a cadeia **mais curta** — a mais fácil de quebrar."},
  { code: `$ dataforge check src/
src/pedidos.df:1:1: erro: import cycle: pedidos.df → clientes.df → pedidos.df
    sugestao: move what both need into a third module`, lang: 'text' },
  {"h2": "As três saídas"},
  {"table": {"head": ["Saída", "Quando"], "rows": [["**um terceiro módulo** com o que os dois precisam", "quase sempre: o ciclo é um tipo compartilhado morando no lugar errado"], ["**passar como argumento** em vez de adotar", "quando só uma ação de `b` precisa de algo de `a`"], ["**juntar os dois**", "quando eles são, na verdade, um módulo só"]]}},
  { code: `// ANTES: pedidos.df adota clientes.df, e clientes.df adota pedidos.df
//         porque os dois usam o record Endereco.
//
// DEPOIS:
//   endereco.df   record Endereco            (nao adota ninguem)
//   clientes.df   adopt ./endereco
//   pedidos.df    adopt ./endereco, adopt ./clientes
//
// O grafo virou uma arvore: endereco <- clientes <- pedidos.

record Endereco:
    rua: String
    cidade: String

e := Endereco("Rua A", "Recife")
assert e.cidade is "Recife"`, lang: 'df' },
  { code: `dataforge deps              # o grafo de imports
dataforge check src/        # o ciclo, com a cadeia`, lang: 'bash' },
];

const headings = [{ id: 'as-tres-saidas', text: "As três saídas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ciclos de import"}
      description={"Por que A → B → A não sobe, como o check mostra a cadeia, e as três formas de quebrá-la."}
      href={"/docs/modulos/ciclos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
