// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/primeiros_passos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Olá, mundo — de verdade",
  description: "O que acontece quando você roda um arquivo: a linha, a ordem, e o que 'out' faz.",
};

const blocos: Bloco[] = [
  {"p": "Um programa é uma lista de instruções que o computador executa **de cima para baixo**, uma de cada vez. O primeiro programa de toda linguagem mostra um texto na tela — e aqui isso se escreve com `out`."},
  { code: `out "Ola, mundo!"
out "Esta e a segunda linha."
out 2 + 3
out "o dobro de", 21, "e", 21 * 2`, lang: 'df', title: `ola.df` },
  { code: `dataforge run ola.df`, lang: 'bash' },
  {"table": {"head": ["Você escreveu", "Sai na tela", "Porque"], "rows": [["`out \"Ola, mundo!\"`", "`Ola, mundo!`", "o texto entre aspas sai como está"], ["`out 2 + 3`", "`5`", "sem aspas, é uma **conta**, e o resultado sai"], ["`out \"a\", 1`", "`a 1`", "a vírgula separa várias coisas, com um espaço entre elas"]]}},
  {"callout": {"tipo": "dica", "titulo": "Aspas mudam tudo", "texto": "`out \"2 + 3\"` mostra `2 + 3`; `out 2 + 3` mostra `5`. Entre aspas é **texto**, e o texto não é calculado. É a primeira distinção de toda linguagem, e a que mais confunde no começo."}},
  {"h2": "Comentários"},
  { code: `// Tudo depois de // e comentario: o computador ignora.
// Serve para quem LE o codigo — inclusive voce, daqui a um mes.
out "so esta linha roda"   // e aqui tambem pode`, lang: 'df' },
  {"p": "Próximo: [Variáveis e contas](/docs/primeiros-passos/variaveis-e-contas)."},
];

const headings = [{ id: 'comentarios', text: "Comentários", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Olá, mundo — de verdade"}
      description={"O que acontece quando você roda um arquivo: a linha, a ordem, e o que 'out' faz."}
      href={"/docs/primeiros-passos/ola-mundo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
