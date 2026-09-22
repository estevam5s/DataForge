// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/integridade.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Integridade",
  description: "Provar que o que está aqui é o que foi posto aqui: o valor SRI de um script de CDN, o manifesto SHA-256 de uma pasta com o que foi acrescentado, removido e alterado, e o manifesto assinado com uma chave que mora fora dali.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (6)"},
  {"table": {"head": ["Assinatura"], "rows": [["`assinar_manifesto(m, chave)`"], ["`conferir_manifesto(pasta, esperado, ignorar=None)`"], ["`conferir_sri(conteudo, integridade)`"], ["`manifesto(pasta, ignorar=None)`"], ["`sri(conteudo, algoritmo='sha384')`"], ["`verificar_manifesto(assinado, chave)`"]]}},
];

const headings = [{ id: 'funcoes-6', text: "Funções (6)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Integridade"}
      description={"Provar que o que está aqui é o que foi posto aqui: o valor SRI de um script de CDN, o manifesto SHA-256 de uma pasta com o que foi acrescentado, removido e alterado, e o manifesto assinado com uma chave que mora fora dali."}
      href={"/docs/biblioteca/integridade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
