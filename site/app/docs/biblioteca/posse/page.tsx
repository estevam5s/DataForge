// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/posse.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Posse",
  description: "Quem e o dono, quem tomou emprestado, e quando solta: posse exclusiva com liberacao deterministica ('dono' e 'com', o RAII), emprestimo com escopo (muitos leem OU um escreve, cobrado quando roda), contagem de referencia deterministica ('compartilhado' e 'atomico') e referencia fraca que quebra o ciclo.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (16)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Celula(valor)`"], ["`Compartilhado(valor=None, ao_soltar=None, _nucleo=None, atomico=False)`"], ["`Dono(valor, ao_soltar=None, nome='valor')`"], ["`Emprestimo(valor, exclusivo=False)`"], ["`Escopo()`"], ["`Fraco(compartilhado)`"], ["`atomico(valor=None, ao_soltar=None)`"], ["`celula(valor=None)`"], ["`com(alvo, acao)`"], ["`com_escopo(acao)`"], ["`compartilhado(valor=None, ao_soltar=None)`"], ["`dono(valor=None, ao_soltar=None, nome='valor')`"], ["`e_dono(valor)`"], ["`escopo()`"], ["`estado(alvo)`"], ["`fraco(alvo)`"]]}},
];

const headings = [{ id: 'funcoes-16', text: "Funções (16)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Posse"}
      description={"Quem e o dono, quem tomou emprestado, e quando solta: posse exclusiva com liberacao deterministica ('dono' e 'com', o RAII), emprestimo com escopo (muitos leem OU um escreve, cobrado quando roda), contagem de referencia deterministica ('compartilhado' e 'atomico') e referencia fraca que quebra o ciclo."}
      href={"/docs/biblioteca/posse"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
