// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/principios.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Principios",
  description: "Os dez principios de design, cada um com uma prova que RODA e o numero que ela deu — duas delas rodam o analisador e uma roda o interpretador, porque 'verificacao antes de rodar' e 'custo zero quando desligado' sao coisas que se demonstram. O veredito nao e dez de dez de proposito: 5 cumpridos, 4 parciais e 1 que nao se aplica. E as nove TENSOES: onde dois principios se contradizem, qual venceu, o custo aceito e o arquivo onde a decisao mora.",
};

const blocos: Bloco[] = [
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`VEREDITOS`", "`[\"cumprido\", \"parcial\", \"nao-se-aplica\"]`"]]}},
  {"h2": "Funções (5)"},
  {"table": {"head": ["Assinatura"], "rows": [["`conferir(nome=None)`"], ["`principios()`"], ["`relatorio()`"], ["`tensoes()`"], ["`veredito()`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-5', text: "Funções (5)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Principios"}
      description={"Os dez principios de design, cada um com uma prova que RODA e o numero que ela deu — duas delas rodam o analisador e uma roda o interpretador, porque 'verificacao antes de rodar' e 'custo zero quando desligado' sao coisas que se demonstram. O veredito nao e dez de dez de proposito: 5 cumpridos, 4 parciais e 1 que nao se aplica. E as nove TENSOES: onde dois principios se contradizem, qual venceu, o custo aceito e o arquivo onde a decisao mora."}
      href={"/docs/biblioteca/principios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
