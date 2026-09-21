// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/ecossistema.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Ecossistema",
  description: "O inventario da implementacao, CONFERIDO contra ela. Cada componente do desenho do ecossistema aponta arquivos de verdade e carrega um de tres estados: 'existe', 'equivale' (ha outra peca que responde a mesma pergunta, nomeada) ou 'nao-existe' (com o porque escrito). 'conferir()' cobra as duas direcoes — todo caminho citado existe no disco, e todo modulo do nucleo aparece em algum componente —, e e isso que impede o mapa de mentir quando uma peca muda de nome. 'o_que_nao_existe()' e a resposta honesta a 'o DataForge tem backend LLVM?'.",
};

const blocos: Bloco[] = [
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`ESTADOS`", "`[\"existe\", \"equivale\", \"nao-existe\"]`"]]}},
  {"h2": "Funções (8)"},
  {"table": {"head": ["Assinatura"], "rows": [["`arvore()`"], ["`componentes()`"], ["`conferir()`"], ["`equivalencias()`"], ["`grupos()`"], ["`numeros()`"], ["`o_que_nao_existe()`"], ["`relatorio()`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-8', text: "Funções (8)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Ecossistema"}
      description={"O inventario da implementacao, CONFERIDO contra ela. Cada componente do desenho do ecossistema aponta arquivos de verdade e carrega um de tres estados: 'existe', 'equivale' (ha outra peca que responde a mesma pergunta, nomeada) ou 'nao-existe' (com o porque escrito). 'conferir()' cobra as duas direcoes — todo caminho citado existe no disco, e todo modulo do nucleo aparece em algum componente —, e e isso que impede o mapa de mentir quando uma peca muda de nome. 'o_que_nao_existe()' e a resposta honesta a 'o DataForge tem backend LLVM?'."}
      href={"/docs/biblioteca/ecossistema"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
