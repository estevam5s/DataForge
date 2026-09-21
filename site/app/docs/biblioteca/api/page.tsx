// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/api.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.API",
  description: "A API do Kiln vista de fora: OpenAPI, coleção do Insomnia e do Postman, curl e a tabela em Markdown — tudo derivado das rotas registradas.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (7)"},
  {"table": {"head": ["Assinatura"], "rows": [["`curl(app, config=None)`"], ["`insomnia(app, config=None)`"], ["`markdown(app, config=None)`"], ["`openapi(app, config=None)`"], ["`postman(app, config=None)`"], ["`resumo(app)`"], ["`rotas(app)`"]]}},
];

const headings = [{ id: 'funcoes-7', text: "Funções (7)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.API"}
      description={"A API do Kiln vista de fora: OpenAPI, coleção do Insomnia e do Postman, curl e a tabela em Markdown — tudo derivado das rotas registradas."}
      href={"/docs/biblioteca/api"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
