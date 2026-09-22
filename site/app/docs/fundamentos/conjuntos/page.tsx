// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fundamentos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Conjuntos",
  description: "O tipo Set: o literal {1, 2}, set(xs), a compreensão, as operações — e por que um Cluster não entra nele.",
};

const blocos: Bloco[] = [
  {"p": "Um **conjunto** guarda valores sem repetição e sem ordem, e responde uma pergunta em tempo constante: *este valor está aqui?*. É o tipo certo para uma lista de permissões, para tirar duplicatas, e para comparar dois grupos."},
  { code: `cores := {"azul", "verde", "azul"}      // a repeticao some
assert len(cores) is 2
assert "verde" in cores
assert typeof(cores) is "Set"

vazio := set()                           // '{}' e o vault vazio
assert typeof(vazio) is "Set" and typeof({}) is "Vault"

assert set([3, 1, 3, 2]) is {1, 2, 3}   // de uma lista
assert {n % 3 cycle n in range(0, 10)} is {0, 1, 2}   // compreensao

xs := [1, 2]
assert {...xs, 9} is {1, 2, 9}           // espalhando
out cores                                // sai em ordem: {azul, verde}`, lang: 'df' },
  {"h2": "As operações"},
  { code: `dev := {"ana", "bia", "caio"}
ops := {"bia", "davi"}

assert dev.union(ops) is {"ana", "bia", "caio", "davi"}        // em qualquer um
assert dev.intersection(ops) is {"bia"}                        // nos dois
assert dev.difference(ops) is {"ana", "caio"}                  // so no primeiro
assert dev.symmetric_difference(ops) is {"ana", "caio", "davi"}
assert {"bia"}.issubset(dev)

dev.add("eva")
dev.discard("ninguem")      // 'discard' nao reclama do que nao existe
assert len(dev) is 4`, lang: 'df' },
  {"h2": "Anotar o tipo"},
  { code: `permitidos: Set<String> := {"admin", "editor"}
assert "admin" in permitidos
// permitidos: Set<String> := {1} — recusado em execucao
// e o 'check' conhece 'Set' e 'Set<T>'`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Um Cluster não entra num Set", "texto": "Um conjunto só guarda o que não muda: um Cluster dentro dele poderia mudar depois de entrar e ficar no lugar errado. `{[1, 2]}` é acusado pelo `check` (`set-item-mutavel`) e recusado em execução com a dica — congele com `freeze(x)`, ou use uma tupla `(1, 2)`."}},
  {"h2": "Quando usar"},
  {"table": {"head": ["Pergunta", "Tipo", "Custo de `x in …`"], "rows": [["*este valor está aqui?*, muitas vezes", "Set", "O(1)"], ["*qual é o terceiro?*, *em que ordem?*", "Cluster", "O(n)"], ["*quanto vale esta chave?*", "Vault", "O(1)"]]}},
  {"p": "A diferença do `in` aparece com volume: ver [Estruturas](/docs/big-o/estruturas)."},
];

const headings = [{ id: 'as-operacoes', text: "As operações", level: 2 as const }, { id: 'anotar-o-tipo', text: "Anotar o tipo", level: 2 as const }, { id: 'quando-usar', text: "Quando usar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Conjuntos"}
      description={"O tipo Set: o literal {1, 2}, set(xs), a compreensão, as operações — e por que um Cluster não entra nele."}
      href={"/docs/fundamentos/conjuntos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
