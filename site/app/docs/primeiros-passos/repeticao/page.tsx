// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/primeiros_passos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "5. Repetir",
  description: "cycle para contar e percorrer, persist para repetir enquanto for verdade.",
};

const blocos: Bloco[] = [
  {"p": "Repetir é a razão de existir do computador: ele faz a mesma coisa mil vezes sem cansar e sem errar. Há duas formas, e a escolha é a pergunta que você está fazendo."},
  {"table": {"head": ["Pergunta", "Use"], "rows": [["*“faça isto para cada número de 1 a 10”*", "`cycle i from 1 to 10`"], ["*“faça isto para cada item da lista”*", "`cycle item in lista`"], ["*“faça isto enquanto for verdade”*", "`persist condicao`"]]}},
  { code: `// A tabuada do 7 — 'from ... to' inclui as DUAS pontas.
cycle i from 1 to 10:
    out $"7 x {i} = {7 * i}"

// Somar uma lista, item por item.
total := 0
cycle preco in [10, 25, 7]:
    total += preco
assert total is 42

// Dobrar ate passar de 1000.
n := 1
passos := 0
persist n smaller 1000:
    n := n * 2
    passos += 1
out $"{passos} dobras: {n}"
assert n is 1024`, lang: 'df' },
  {"h2": "Parar antes, ou pular"},
  { code: `// 'halt' sai do laco; 'skip' pula para a proxima volta.
primeiro_par := void
cycle n in [7, 3, 8, 5, 10]:
    given n % 2 isnt 0:
        skip
    primeiro_par := n
    halt
assert primeiro_par is 8`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O laço que nunca termina", "texto": "Um `persist` cuja condição nunca fica falsa roda para sempre — o programa parece travado. Confira que alguma coisa **dentro** do laço muda a condição. Ctrl+C interrompe."}},
  {"p": "Próximo: [6. Listas e vaults](/docs/primeiros-passos/colecoes)."},
];

const headings = [{ id: 'parar-antes-ou-pular', text: "Parar antes, ou pular", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"5. Repetir"}
      description={"cycle para contar e percorrer, persist para repetir enquanto for verdade."}
      href={"/docs/primeiros-passos/repeticao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
