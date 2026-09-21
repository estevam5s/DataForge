// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/iter.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Iter",
  description: "Iteradores preguiçosos e composição de ações: janelas, combinatória, memoize.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (44)"},
  {"table": {"head": ["Assinatura"], "rows": [["`accumulate(fonte, funcao=None, inicial=None)`"], ["`attr(nome)`"], ["`batched(fonte, tamanho)`"], ["`cache_info(memoizada)`"], ["`chain(*fontes)`"], ["`chunk(fonte, tamanho)`"], ["`combinations(fonte, tamanho)`"], ["`combinations_with_repetition(fonte, tamanho)`"], ["`compose(*acoes)`"], ["`compress(fonte, marcas)`"], ["`constant(valor)`"], ["`count(inicio=0, passo=1)`"], ["`curry(funcao, aridade=2)`"], ["`cycle_forever(itens)`"], ["`drop(fonte, n)`"], ["`drop_while(fonte, condicao)`"], ["`filter_false(fonte, condicao)`"], ["`flat_map(fonte, funcao)`"], ["`flatten(fonte, profundidade=1)`"], ["`flip(funcao)`"], ["`group_runs(fonte, chave=None)`"], ["`identity(x)`"], ["`item(indice)`"], ["`memoize(funcao, tamanho=128)`"], ["`once(funcao)`"], ["`op(simbolo)`"], ["`pairwise(fonte)`"], ["`partial(funcao, *fixos, **nomeados)`"], ["`permutations(fonte, tamanho=0)`"], ["`pipe(*acoes)`"], ["`powerset(fonte)`"], ["`product(*fontes, repetir=1)`"], ["`reduce(fonte, funcao, inicial=None)`"], ["`repeat(valor, vezes=0)`"], ["`running_max(fonte)`"], ["`running_sum(fonte)`"], ["`slice(fonte, inicio, fim=None, passo=1)`"], ["`take(fonte, n)`"], ["`take_while(fonte, condicao)`"], ["`to_cluster(fonte)`"], ["`unique(fonte)`"], ["`unique_by(fonte, chave)`"], ["`window(fonte, tamanho)`"], ["`zip_longest(a, b, preencher=None)`"]]}},
];

const headings = [{ id: 'funcoes-44', text: "Funções (44)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Iter"}
      description={"Iteradores preguiçosos e composição de ações: janelas, combinatória, memoize."}
      href={"/docs/biblioteca/iter"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
