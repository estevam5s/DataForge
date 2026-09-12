// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "29 · Banco e crud",
  description: "4 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 29`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["219", "**Um CRUD completo, com o banco fazendo o trabalho**", ""], ["220", "**Um PDV: a venda inteira, ou nenhuma**", ""], ["221", "**Relatorio, busca e o indice que falta**", ""], ["222", "**Migracoes: mudar o schema sem perder dado**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/29-banco-e-crud/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/29-banco-e-crud/219_crud_completo.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"29 · Banco e crud"}
      description={"4 exercícios: ."}
      href={"/docs/exercicios/29-banco-e-crud"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
