// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "23 · Dados e planilhas",
  description: "3 exercícios: frames, agregação e .xlsx.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 23`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["198", "**Gravar e ler uma planilha**", "transforme uma lista de vaults num .xlsx e leia de volta."], ["199", "**Relatorio com varias abas e formulas**", "monte um relatorio com formulas que o Excel calcula ao abrir."], ["200", "**Do banco para a planilha, passando pela analise**", "consulte o banco, analise os numeros e exporte a planilha."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/23-dados-e-planilhas/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/23-dados-e-planilhas/198_primeira_planilha.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"23 · Dados e planilhas"}
      description={"3 exercícios: frames, agregação e .xlsx."}
      href={"/docs/exercicios/23-dados-e-planilhas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
