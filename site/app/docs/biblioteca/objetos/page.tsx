// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/objetos.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Objetos",
  description: "Cópia rasa e funda, congelamento, igualdade estrutural, hash coerente, ordenação por campos e serialização polimórfica que só reconstrói os tipos autorizados e resolve ciclos.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (13)"},
  {"table": {"head": ["Assinatura"], "rows": [["`clonar(obj)`"], ["`clonar_fundo(obj)`"], ["`comparar_por(campos)`"], ["`congelado(obj)`"], ["`congelar(obj, fundo=False)`"], ["`de_json(texto, tipos)`"], ["`de_vault(dado, tipos, opcoes=None)`"], ["`hash(obj)`"], ["`identico(a, b)`"], ["`igual(a, b)`"], ["`ordenar(itens, campos)`"], ["`para_json(obj, opcoes=None, indent=None)`"], ["`para_vault(obj, opcoes=None)`"]]}},
];

const headings = [{ id: 'funcoes-13', text: "Funções (13)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Objetos"}
      description={"Cópia rasa e funda, congelamento, igualdade estrutural, hash coerente, ordenação por campos e serialização polimórfica que só reconstrói os tipos autorizados e resolve ciclos."}
      href={"/docs/biblioteca/objetos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
