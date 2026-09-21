// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/injecao.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Injecao",
  description: "Contêiner de injeção de dependência: único, transitório e por escopo, fábrica, valor pronto, dependência preguiçosa e opcional, injeção por construtor, campo e método, e detecção de ciclo com a cadeia inteira.",
};

const blocos: Bloco[] = [
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`ESCOPOS`", "`[\"unico\", \"transitorio\", \"por_escopo\"]`"]]}},
  {"h2": "Funções (4)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Fornece(contrato)`"], ["`Injetar(alvo=None)`"], ["`Servico(escopo='transitorio')`"], ["`conteiner(nome='raiz')`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-4', text: "Funções (4)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Injecao"}
      description={"Contêiner de injeção de dependência: único, transitório e por escopo, fábrica, valor pronto, dependência preguiçosa e opcional, injeção por construtor, campo e método, e detecção de ciclo com a cadeia inteira."}
      href={"/docs/biblioteca/injecao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
