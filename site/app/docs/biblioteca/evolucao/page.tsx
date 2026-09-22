// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/evolucao.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Evolucao",
  description: "Como uma API muda sem pegar ninguém de surpresa: marcar uma ação como obsoleta (desde quando, por quê, o que usar) ou experimental, e manter um nome antigo que avisa. O aviso sai uma vez por ação, na saída de erro, e DF_OBSOLETOS=erro o transforma em erro no CI.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (5)"},
  {"table": {"head": ["Assinatura"], "rows": [["`avisos()`"], ["`esquecer()`"], ["`experimental(motivo='')`"], ["`obsoleta(motivo='', desde='', use='')`"], ["`renomeada(acao, nome_antigo, desde='')`"]]}},
];

const headings = [{ id: 'funcoes-5', text: "Funções (5)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Evolucao"}
      description={"Como uma API muda sem pegar ninguém de surpresa: marcar uma ação como obsoleta (desde quando, por quê, o que usar) ou experimental, e manter um nome antigo que avisa. O aviso sai uma vez por ação, na saída de erro, e DF_OBSOLETOS=erro o transforma em erro no CI."}
      href={"/docs/biblioteca/evolucao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
