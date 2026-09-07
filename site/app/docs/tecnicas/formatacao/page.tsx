import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Formatação",
  description: "dataforge fmt: regras determinísticas, idempotência e uso em CI.",
};

const blocos: Bloco[] = [
  {"h2": "Usar"},
  { code: `dataforge fmt arquivo.df       # reescreve
dataforge fmt src/             # a pasta inteira
dataforge fmt . --check        # só verifica, não escreve`, lang: 'bash' },
  {"p": "O `--check` sai com código diferente de zero se algo estiver fora do formato — é a forma de usar em integração contínua."},
  {"h2": "As regras"},
  {"list": ["**4 espaços** por nível de indentação; tabs viram espaços", "Um espaço em volta de operadores binários e de `:=`", "Nenhum espaço depois de `(`, antes de `)`, ou antes de `,` e `:`", "Sem espaço entre um nome e o `(` da chamada", "Nenhum espaço em branco no fim da linha", "No máximo uma linha em branco dentro de um bloco, duas no topo do arquivo", "O arquivo termina com exatamente uma quebra de linha"]},
  { code: `action   somar( a,b ):
      yield a+b
x:=somar( 1,2 )
v := { "a":1,"b":2 }`, title: `antes` },
  { code: `action somar(a, b):
    yield a + b

x := somar(1, 2)
v := {"a": 1, "b": 2}`, title: `depois` },
  {"h2": "Idempotência"},
  {"p": "Formatar duas vezes dá o mesmo resultado que formatar uma. Há teste para isso, e ele roda sobre os 225 arquivos do repositório."},
  { code: `format_source(format_source(x)) == format_source(x)`, lang: 'text' },
  {"h2": "Dois detalhes que importam"},
  {"h3": "~/ em vez de //"},
  {"p": "O formatador reimprime a divisão inteira sempre como `~/`. Reimprimir `//` faria a linha virar **comentário** na próxima passagem — o operador some e o código muda de sentido."},
  {"h3": "Comentários e strings interpoladas"},
  {"p": "O extrator de comentário percorre o fluxo de tokens, não os caracteres. Só assim `#` dentro de `$\"…\"` não é confundido com um comentário:"},
  { code: `out $"{"#".repeat(n)} ({n})"     # o '#' de dentro é texto, não comentário` },
  {"h2": "Estrutura, não espaços"},
  {"p": "A profundidade de cada linha vem do `INDENT`/`DEDENT` do lexer, não da contagem de espaços do original. Isso significa que um arquivo com indentação inconsistente é **recusado** em vez de ser adivinhado:"},
  { code: `SyncError [line 10]: Indentation mismatch: expected 8 spaces, got 9`, lang: 'text' },
  {"p": "Um formatador que adivinha a estrutura de um código ambíguo pode mudar o que ele faz. Melhor falhar."},
  {"h2": "Em CI"},
  { code: `dataforge fmt . --check && dataforge check . && dataforge test`, lang: 'bash' },
];

const headings = [{ id: 'usar', text: "Usar", level: 2 as const }, { id: 'as-regras', text: "As regras", level: 2 as const }, { id: 'idempotencia', text: "Idempotência", level: 2 as const }, { id: 'dois-detalhes-que-importam', text: "Dois detalhes que importam", level: 2 as const }, { id: 'estrutura-nao-espacos', text: "Estrutura, não espaços", level: 2 as const }, { id: 'em-ci', text: "Em CI", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Formatação"}
      description={"dataforge fmt: regras determinísticas, idempotência e uso em CI."}
      href={"/docs/tecnicas/formatacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
