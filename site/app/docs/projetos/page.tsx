import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Projetos",
  description: "Três programas completos que juntam as bibliotecas.",
};

const blocos: Bloco[] = [
  {"p": "Não são exercícios: cada um tem `forge.toml` com dependências reais, estrutura em camadas e testes próprios. Ficam em `projetos/` no repositório."},
  { code: `cd projetos/gestor-tarefas
dataforge install
dataforge test tests/
dataforge run src/main.df -- listar`, lang: 'bash' },
  {"table": {"head": ["Projeto", "O que faz", "Bibliotecas"], "rows": [["[Gestor de tarefas](/docs/projetos/gestor-tarefas)", "CLI com prazos e persistência", "6"], ["[Análise de vendas](/docs/projetos/analise-vendas)", "CSV → relatório estatístico", "6"], ["[API de links](/docs/projetos/api-links)", "Encurtador com servidor HTTP", "6"]]}},
  {"h2": "O que cada um mostra"},
  {"p": "**gestor-tarefas** — a estrutura de uma CLI: `argumentos` gera a ajuda da mesma declaração que faz a leitura, `cofre` monta a configuração em camadas, e o repositório fica isolado atrás de uma interface para que trocar JSON por SQLite seja mexer num arquivo só."},
  {"p": "**analise-vendas** — o pipeline de dados: converter na entrada e falhar cedo, calcular, apresentar. O relatório avisa quando o desvio passa de metade da média, porque aí o ticket médio não descreve as vendas."},
  {"p": "**api-links** — separar regra de negócio de transporte. Toda a lógica está em um arquivo testável em milissegundos; o servidor é uma casca de trinta linhas."},
];

const headings = [{ id: 'o-que-cada-um-mostra', text: "O que cada um mostra", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Projetos"}
      description={"Três programas completos que juntam as bibliotecas."}
      href={"/docs/projetos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
