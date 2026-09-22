// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O lexer",
  description: "Texto em tokens: indentação vira INDENT e DEDENT, a interpolação vira partes, e // decide entre comentário e divisão.",
};

const blocos: Bloco[] = [
  {"p": "O lexer lê o texto caractere por caractere e entrega **tokens**: cada um com tipo, valor, linha e coluna. É a linha e a coluna que fazem todo erro posterior apontar o lugar certo — um token sem posição produziria um erro sem seta."},
  { code: `adopt Arcane.Compilador as Comp

tipos := [t["tipo"] cycle t in Comp.tokens("given x bigger 1:\\n    out x\\n")]
assert tipos.contains("INDENT") and tipos.contains("DEDENT")
assert Comp.tokens("total := 7")[2] is {"tipo": "INTEGER", "valor": 7, "linha": 1, "coluna": 10}`, lang: 'df' },
  {"h2": "A indentação vira token"},
  {"p": "A linguagem marca bloco por recuo, e o parser não conta espaços: o lexer mantém uma pilha de recuos e emite `INDENT` quando o recuo cresce e um `DEDENT` para **cada nível** que fecha. Tabulação é recusada (`SyncError`) — dois editores mostram um tab com larguras diferentes, e um bloco pareceria certo em um e errado no outro."},
  {"h2": "`//`: comentário ou divisão?"},
  {"p": "`//` é **comentário** por padrão, e vira divisão inteira só quando o que vem depois é um número, `(`, ou uma chamada/índice/membro. É por isso que `total // 2` divide e `total // nota` comenta — e é a regra que exige cuidado com comentário que começa com número:"},
  { code: `adopt Arcane.Compilador as Comp

divide := [t["tipo"] cycle t in Comp.tokens("x := a // 2")]
comenta := [t["tipo"] cycle t in Comp.tokens("x := a // metade")]
assert divide.contains("FLOOR_DIV")
assert not comenta.contains("FLOOR_DIV")`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Comentário que começa com número", "texto": "`total := 12   // 3 parcelas` divide 12 por 3, e `parcelas` vira uma segunda instrução na mesma linha. Desde esta versão o parser recusa isso com uma dica sobre o `//`. Comece o comentário com uma palavra, ou use `#`. A forma recomendada para dividir é `~/`, que nunca é comentário."}},
];

const headings = [{ id: 'a-indentacao-vira-token', text: "A indentação vira token", level: 2 as const }, { id: 'comentario-ou-divisao', text: "`//`: comentário ou divisão?", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O lexer"}
      description={"Texto em tokens: indentação vira INDENT e DEDENT, a interpolação vira partes, e // decide entre comentário e divisão."}
      href={"/docs/compilador/lexer"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
