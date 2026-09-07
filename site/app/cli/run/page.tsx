import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge run",
  description: "Executar um programa",
};

const blocos: Bloco[] = [
  {"h2": "Uso"},
  { code: `dataforge run programa.df
dataforge run programa.df --time      # com tempo de execução
dataforge run programa.df --debug     # tokens, AST e traceback
dataforge run                         # usa a entrada do forge.toml`, lang: 'bash' },
  {"h2": "A entrada do manifesto"},
  {"p": "Sem argumento, o `run` usa o `entry` declarado no [`forge.toml`](/cli/forge-toml):"},
  { code: `[project]
entry = "src/main.df"`, lang: 'toml' },
  {"p": "Isso funciona de qualquer subpasta do projeto — o comando sobe procurando o manifesto."},
  {"h2": "--debug"},
  {"p": "Imprime o fluxo de tokens, um resumo da AST e, se houver erro, o traceback completo do interpretador. Útil para investigar um comportamento que parece impossível."},
  {"h2": "--time"},
  { code: `⚡ Execution time: 42.31ms`, lang: 'text' },
];

const headings = [{ id: 'uso', text: "Uso", level: 2 as const }, { id: 'a-entrada-do-manifesto', text: "A entrada do manifesto", level: 2 as const }, { id: '--debug', text: "--debug", level: 2 as const }, { id: '--time', text: "--time", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge run"}
      description={"Executar um programa"}
      href={"/cli/run"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
