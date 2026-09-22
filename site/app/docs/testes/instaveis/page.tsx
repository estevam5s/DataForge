// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testes instáveis",
  description: "O teste que passa e falha sem mudar nada — as cinco causas, e por que repetir não é a correção.",
};

const blocos: Bloco[] = [
  {"p": "Um teste instável é pior que nenhum: ele ensina o time a rodar o CI de novo em vez de ler a falha. E no dia em que a falha é real, ela é tratada como ruído. Toda instabilidade tem uma causa, e a causa quase sempre é uma destas cinco."},
  {"table": {"head": ["Causa", "Sintoma", "Correção"], "rows": [["**tempo**", "falha perto da meia-noite, ou numa máquina lenta", "relógio falso: `Crucible.com_relogio` / `freeze_time`"], ["**ordem**", "passa sozinho, falha na suíte", "estado compartilhado — um banco novo por teste"], ["**aleatoriedade**", "falha uma vez em vinte", "semente fixa, ou teste por propriedade com a semente no relatório"], ["**concorrência**", "falha só no CI, que tem outro número de núcleos", "sincronizar de verdade; medir com `Crucible.corrida`"], ["**medida absoluta**", "*“devia levar menos de 50 ms”*", "comparar uma **razão** contra a mesma máquina"]]}},
  {"h2": "Tempo: o relógio que você controla"},
  { code: `adopt Arcane.Crucible

action vencido(prazo, agora):
    yield agora bigger prazo

crucible "prazo":
    trial "vence depois do prazo, e nao antes":
        expect vencido(1000, 999) is no
        expect vencido(1000, 1000) is no
        expect vencido(1000, 1001) is yes

r := Crucible.run()
assert r["falhou"] is 0

// A regra recebe 'agora' como argumento. Uma acao que chama time()
// por dentro so e testavel na hora certa do dia.`, lang: 'df' },
  {"h2": "Repetir não é corrigir"},
  {"p": "`Crucible.flaky(acao, tentativas)` existe, e devolve **quantas tentativas** foram precisas — um teste que precisa de três toda vez não é instável, está quebrado. Use-o como diagnóstico, nunca como correção permanente."},
  {"callout": {"tipo": "atencao", "titulo": "Medida absoluta mede a máquina", "texto": "`assert tempo smaller 50` passa no seu notebook e falha num runner do CI carregado. Este repositório já reprovou três vezes assim. A saída é cobrar um **fator** contra uma referência medida no mesmo instante — ver [Prometer desempenho](/docs/bibliotecas/desempenho)."}},
  {"p": "Continue em [Cenários de concorrência e relógio](/docs/crucible/cenarios)."},
];

const headings = [{ id: 'tempo-o-relogio-que-voce-controla', text: "Tempo: o relógio que você controla", level: 2 as const }, { id: 'repetir-nao-e-corrigir', text: "Repetir não é corrigir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testes instáveis"}
      description={"O teste que passa e falha sem mudar nada — as cinco causas, e por que repetir não é a correção."}
      href={"/docs/testes/instaveis"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
