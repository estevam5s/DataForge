// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/tipos.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Tipos",
  description: "Reflexao sobre tipos: os metadados de um 'type' declarado (especie, base, regra, opaco), 'satisfaz' para conferir sem levantar, a forma ESTRUTURAL de um valor ('Cluster<Integer>', 'Tuple<Integer, String>') e os campos de um record ou instancia com o tipo de cada um.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (10)"},
  {"table": {"head": ["Assinatura"], "rows": [["`campos(valor)`"], ["`conferir(valor, nome)`"], ["`de(nome)`"], ["`declarados()`"], ["`e_colecao(valor)`"], ["`e_imutavel(valor)`"], ["`existe(nome)`"], ["`forma(valor, profundidade=3)`"], ["`nome_de(valor)`"], ["`satisfaz(valor, nome)`"]]}},
];

const headings = [{ id: 'funcoes-10', text: "Funções (10)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Tipos"}
      description={"Reflexao sobre tipos: os metadados de um 'type' declarado (especie, base, regra, opaco), 'satisfaz' para conferir sem levantar, a forma ESTRUTURAL de um valor ('Cluster<Integer>', 'Tuple<Integer, String>') e os campos de um record ou instancia com o tipo de cada um."}
      href={"/docs/biblioteca/tipos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
