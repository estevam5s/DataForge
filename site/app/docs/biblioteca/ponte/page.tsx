// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/ponte.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Ponte",
  description: "A ponte para o Python: perguntar se um pacote existe, explorar o que ele oferece e converter o que ele devolve.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (12)"},
  {"table": {"head": ["Assinatura"], "rows": [["`assinatura(valor)`"], ["`atributos(valor)`"], ["`chamavel(x)`"], ["`cluster(valor)`"], ["`doc(valor)`"], ["`empacotado() -> bool`"], ["`importar(nome)`"], ["`onde() -> str`"], ["`tem(nome)`"], ["`tipo(valor) -> str`"], ["`vault(valor)`"], ["`versao(nome)`"]]}},
];

const headings = [{ id: 'funcoes-12', text: "Funções (12)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Ponte"}
      description={"A ponte para o Python: perguntar se um pacote existe, explorar o que ele oferece e converter o que ele devolve."}
      href={"/docs/biblioteca/ponte"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
