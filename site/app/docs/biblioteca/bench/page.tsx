// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/bench.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Bench",
  description: "Medir, comparar e descobrir a classe de custo: tempo de uma ação, implementações lado a lado sem a ordem decidir quem ganha, e a curva medida em tamanhos crescentes dizendo qual O() descreve o que aconteceu.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (7)"},
  {"table": {"head": ["Assinatura"], "rows": [["`classe(acao, tamanhos=None, preparar=None, repeticoes=3)`"], ["`comparar(implementacoes, argumento=None, repeticoes=5, aquecer=1)`"], ["`curva(acao, tamanhos, preparar=None, repeticoes=3, aquecer=1)`"], ["`medir(acao, argumento=None, repeticoes=5, aquecer=1)`"], ["`relatorio(resultado)`"], ["`repetir(acao, vezes, argumento=None)`"], ["`tabela(resultado)`"]]}},
];

const headings = [{ id: 'funcoes-7', text: "Funções (7)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Bench"}
      description={"Medir, comparar e descobrir a classe de custo: tempo de uma ação, implementações lado a lado sem a ordem decidir quem ganha, e a curva medida em tamanhos crescentes dizendo qual O() descreve o que aconteceu."}
      href={"/docs/biblioteca/bench"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
