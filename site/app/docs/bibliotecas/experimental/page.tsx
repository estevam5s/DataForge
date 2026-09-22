// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "API experimental",
  description: "Marcar o que ainda pode mudar sem aviso de versão — e por que isso protege os dois lados.",
};

const blocos: Bloco[] = [
  {"p": "Semver promete que uma versão menor não quebra nada. Isso é ótimo para quem usa e é uma prisão para quem escreve: a primeira versão de uma API raramente é a certa. `experimental` separa o que já é promessa do que ainda é rascunho."},
  { code: `adopt Arcane.Evolucao as Ev

mark @Ev.experimental("a assinatura ainda vai mudar")
action prever_demanda(historico):
    yield sum(historico) / len(historico)

assert prever_demanda([10, 20, 30]) is 20.0
assert Ev.avisos()[0]["tipo"] is "experimental"`, lang: 'df' },
  {"table": {"head": ["", "Obsoleta", "Experimental"], "rows": [["diz", "*vai sumir*", "*pode mudar*"], ["`DF_OBSOLETOS=erro`", "reprova", "**não** reprova — usar o experimental é escolha legítima"], ["entra no `dataforge abi`", "sim, até sair", "declare no README que não entra na promessa"]]}},
  {"callout": {"tipo": "dica", "titulo": "Experimental tem prazo", "texto": "Uma API experimental há três versões não é experimental: é uma API que você não teve coragem de prometer. Ou ela vira estável, ou sai."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"API experimental"}
      description={"Marcar o que ainda pode mudar sem aviso de versão — e por que isso protege os dois lados."}
      href={"/docs/bibliotecas/experimental"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
