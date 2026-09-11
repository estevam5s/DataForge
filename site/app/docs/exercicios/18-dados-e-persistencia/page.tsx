// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "18 · Dados e persistencia",
  description: "6 exercícios: JSON, CSV, SQLite e serialização.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 18`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["163", "**Serializacao de dados**", "converta estruturas para JSON, CSV, TOML e de volta."], ["164", "**Arquivos e diretorios**", "leia, escreva e organize arquivos com Arcane.IO."], ["165", "**Banco de dados**", "crie tabelas, insira e consulte com Arcane.Database."], ["166", "**Servidor HTTP**", "monte uma API REST com rotas e JSON."], ["167", "**Cliente HTTP e URLs**", "monte URLs, trate respostas e prepare requisicoes."], ["168", "**Projeto: CRUD com persistencia**", "junte banco, validacao e relatorio num sistema completo."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/18-dados-e-persistencia/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/18-dados-e-persistencia/163_serializacao.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"18 · Dados e persistencia"}
      description={"6 exercícios: JSON, CSV, SQLite e serialização."}
      href={"/docs/exercicios/18-dados-e-persistencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
