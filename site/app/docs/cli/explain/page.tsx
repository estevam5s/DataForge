import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge explain",
  description: "O que significa um código de erro.",
};

const blocos: Bloco[] = [
  { code: `dataforge explain DF0601
dataforge explain 0401        # o prefixo é opcional`, lang: 'bash' },
  {"p": "Todo erro do DataForge carrega um código estável. O comando diz o que ele significa, com exemplo e solução:"},
  { code: `  DF0601  Indice ou chave invalida

  Leitura fora da faixa de um cluster, ou de uma chave que o vault nao tem.

  Em cluster de n itens, os indices validos vao de 0 a n-1 — ou de -1 a -n
  contando do fim. O erro classico e usar len(x) como indice, quando o
  ultimo e len(x) - 1.

  EXEMPLO
      itens := [10, 20, 30]
      out itens[3]        // DF0601: so ha 0, 1 e 2
      out itens[-1]       // 30, o ultimo

  COMO RESOLVER
      Confira o tamanho antes:   given len(itens) bigger i:
      Use valor de reserva:      v["idade"] ?? 0`, lang: 'bash' },
  {"h2": "Sem argumento, lista tudo"},
  { code: `dataforge explain`, lang: 'bash' },
  {"p": "A referência completa está em [códigos de erro](/docs/referencia/erros)."},
];

const headings = [{ id: 'sem-argumento-lista-tudo', text: "Sem argumento, lista tudo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge explain"}
      description={"O que significa um código de erro."}
      href={"/docs/cli/explain"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
