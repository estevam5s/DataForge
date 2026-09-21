// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/capacidade.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Capacidade",
  description: "A fronteira de CAPACIDADE: roda uma acao com a lista de poderes que ela pode alcancar, e recusa o resto pelo NOME da capacidade que falta. A ponte para o Python e capacidade propria, e nunca vem junto. NAO e caixa contra programa hostil, e o modulo diz isso em 'limites()': ele bloqueia a autoridade ambiente (o 'adopt'), e nao tira o que foi ENTREGUE — o que e o modelo de capacidade, nao um defeito.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (6)"},
  {"table": {"head": ["Assinatura"], "rows": [["`capacidades()`"], ["`executar(acao, permissoes=None, argumentos=None)`"], ["`exige(nome_modulo)`"], ["`limites()`"], ["`modulos_de(capacidade)`"], ["`observar(acao, permissoes=None, argumentos=None)`"]]}},
];

const headings = [{ id: 'funcoes-6', text: "Funções (6)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Capacidade"}
      description={"A fronteira de CAPACIDADE: roda uma acao com a lista de poderes que ela pode alcancar, e recusa o resto pelo NOME da capacidade que falta. A ponte para o Python e capacidade propria, e nunca vem junto. NAO e caixa contra programa hostil, e o modulo diz isso em 'limites()': ele bloqueia a autoridade ambiente (o 'adopt'), e nao tira o que foi ENTREGUE — o que e o modelo de capacidade, nao um defeito."}
      href={"/docs/biblioteca/capacidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
