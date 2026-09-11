// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "20 · Projetos finais",
  description: "6 exercícios: programas completos, de ponta a ponta.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 20`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["175", "**Projeto: ferramenta de linha de comando**", "escreva um utilitario que analisa arquivos e imprime um relatorio."], ["176", "**Projeto: analise de dados**", "carregue, limpe, agregue e visualize um conjunto de dados."], ["177", "**Projeto: mini linguagem**", "escreva um interpretador de expressoes dentro do DataForge."], ["178", "**Projeto: sistema de biblioteca**", "integre records, enums, banco, validacao e relatorios."], ["179", "**Revisao: todos os conceitos**", "um programa que exercita cada recurso da linguagem."], ["180", "**Encerramento e proximos passos**", "o que voce aprendeu, o que a linguagem ainda nao faz e para onde ir."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/20-projetos-finais/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/20-projetos-finais/175_cli_arquivos.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"20 · Projetos finais"}
      description={"6 exercícios: programas completos, de ponta a ponta."}
      href={"/docs/exercicios/20-projetos-finais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
