// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/decimal.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Decimal",
  description: "Número decimal exato, para quando 0,1 + 0,2 precisa dar 0,3 — dinheiro, imposto, e todo número que alguém confere na mão.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (16)"},
  {"table": {"head": ["Assinatura"], "rows": [["`abs(d)`"], ["`arredondar(valor, casas=0, modo='MEIO_PARA_CIMA')`"], ["`casas(valor)`"], ["`centavos(valor)`"], ["`de(valor)`"], ["`de_centavos(centavos)`"], ["`e_decimal(x)`"], ["`float(valor)`"], ["`inteiro(valor)`"], ["`media(valores)`"], ["`modos()`"], ["`repartir(valor, partes, casas=2)`"], ["`sinal(d)`"], ["`soma(valores)`"], ["`texto(valor, casas=None)`"], ["`zero()`"]]}},
];

const headings = [{ id: 'funcoes-16', text: "Funções (16)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Decimal"}
      description={"Número decimal exato, para quando 0,1 + 0,2 precisa dar 0,3 — dinheiro, imposto, e todo número que alguém confere na mão."}
      href={"/docs/biblioteca/decimal"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
