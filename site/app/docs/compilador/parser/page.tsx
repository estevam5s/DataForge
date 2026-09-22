// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O parser",
  description: "Descida recursiva: uma função por nível de precedência, a recuperação que junta vários erros, e o fim de linha exigido.",
};

const blocos: Bloco[] = [
  {"p": "O parser é **descendente recursivo**: uma função por construção da gramática, e uma por nível de precedência. `1 + 2 * 3` vira `+` na raiz porque a função da soma chama a da multiplicação para ler cada lado — a precedência está na **ordem das chamadas**, e não numa tabela."},
  { code: `adopt Arcane.Compilador as Comp

raiz := Comp.arvore("x := 1 + 2 * 3")["corpo"][0]["valor"]
assert raiz["op"] is "+"
assert raiz["direita"]["op"] is "*"               // o * ficou mais fundo: liga mais forte`, lang: 'df' },
  {"table": {"head": ["Do mais fraco", "ao mais forte"], "rows": [["`>>` (pipeline)", "a mais fraca de todas"], ["`a given c otherwise b`", "o ternário"], ["`??`", "abaixo de `or` — `x ?? 0 is 0` é `x ?? (0 is 0)`: o `check` avisa"], ["`or` · `and` · `not`", ""], ["`is`, `bigger`, `smaller`…", "encadeiam: `1 smaller x smaller 9`"], ["`+ -` · `* / ~/ %` · `**`", "`**` associa à direita"], ["unário, chamada, índice, membro", "o mais forte"]]}},
  {"h2": "Vários erros de uma vez"},
  {"p": "Um parser que para no primeiro erro obriga a corrigir, compilar e corrigir uma vez por erro. Este registra o erro, **ressincroniza** no começo da próxima instrução e continua: quem lê recebe os quatro erros do arquivo de uma vez. O erro que viaja continua sendo um só, e os demais vão em `outros`."},
  {"h2": "Uma instrução por linha"},
  {"p": "Depois de uma instrução completa, a linha tem de acabar. `x := 1 vazios` era aceito como duas instruções — `x := 1` e `vazios` —, e o caso que custou caro foi o comentário começando com número, que virava uma divisão seguida de uma instrução solta. Dezessete blocos desta documentação só \"compilavam\" por isso; hoje todos compilam de verdade."},
  { code: `adopt Arcane.Compilador as Comp

recusado := no
monitor:
    Comp.arvore("x := 1 vazios")
handle Error as e:
    recusado := e.message.contains("same line")
assert recusado`, lang: 'df' },
];

const headings = [{ id: 'varios-erros-de-uma-vez', text: "Vários erros de uma vez", level: 2 as const }, { id: 'uma-instrucao-por-linha', text: "Uma instrução por linha", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O parser"}
      description={"Descida recursiva: uma função por nível de precedência, a recuperação que junta vários erros, e o fim de linha exigido."}
      href={"/docs/compilador/parser"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
