// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/primeiros_passos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "9. Ler uma mensagem de erro",
  description: "Onde olhar numa mensagem de erro, e os seis erros que quem começa mais encontra.",
};

const blocos: Bloco[] = [
  {"p": "Errar é o normal; o que muda com a prática é quanto tempo se leva para achar o erro. Uma mensagem de erro do DataForge tem sempre quatro partes, e lê-las em ordem resolve a maioria dos casos."},
  { code: `erro[DF0401]: 'totl' nao esta definido.
  ┌─ conta.df:3:5
  │
3 │ out totl * 2
  │     ^^^^ usado aqui
  = nota: este nome nunca recebeu valor em nenhum escopo ao redor
  = dica: voce quis dizer 'total'?`, lang: 'text' },
  {"table": {"head": ["Parte", "O que diz"], "rows": [["`erro[DF0401]`", "o **código** — `dataforge explain DF0401` explica em detalhe"], ["`conta.df:3:5`", "o **arquivo**, a **linha** e a **coluna**"], ["a linha com `^^^^`", "o **ponto exato**"], ["`nota` / `dica`", "o **porquê** e o **que fazer**"]]}},
  {"h2": "Os seis mais comuns"},
  {"table": {"head": ["A mensagem fala de", "O que costuma ser"], "rows": [["nome não definido", "um erro de digitação — a dica sugere o nome parecido"], ["indentação / `SyncError`", "um **tab** no lugar de espaços: use 4 espaços"], ["`Expected ':'`", "faltou o `:` no fim do `given`, do `cycle` ou da `action`"], ["não se soma texto com número", "o que veio do `input` ainda é texto — `int(...)`"], ["índice fora do alcance", "a lista começa no zero; o último é `[-1]`"], ["`'no'` é palavra reservada", "`no`, `in`, `is`, `to`, `from` não podem ser nomes"]]}},
  { code: `// Conferir ANTES de rodar acha a maioria deles:
//   dataforge check conta.df
monitor:
    x := "10" + 1
handle Error as e:
    out "o erro:", e.message
assert int("10") + 1 is 11`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "`dataforge check` antes de `run`", "texto": "Ele lê o arquivo sem executar e acusa nome errado, número errado de argumentos e tipo errado — em menos de um segundo, e com a mesma cara de mensagem. É o hábito que mais poupa tempo no começo."}},
  {"p": "Próximo: [10. Para onde ir](/docs/primeiros-passos/proximos-passos)."},
];

const headings = [{ id: 'os-seis-mais-comuns', text: "Os seis mais comuns", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"9. Ler uma mensagem de erro"}
      description={"Onde olhar numa mensagem de erro, e os seis erros que quem começa mais encontra."}
      href={"/docs/primeiros-passos/erros-comuns"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
