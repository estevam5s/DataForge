// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A promessa de estabilidade",
  description: "O que cada número de versão promete, escrito — e conferido pelo abi a cada release.",
};

const blocos: Bloco[] = [
  {"p": "Semver é uma promessa, e uma promessa só vale se estiver escrita. Declare no README o que a sua biblioteca promete, e confira a cada release com `dataforge abi` — que diz qual número a mudança **exige**."},
  {"table": {"head": ["Sobe", "Quando", "Quem usa precisa…"], "rows": [["**correção** (1.4.0 → 1.4.1)", "a superfície não mudou", "nada"], ["**menor** (1.4 → 1.5)", "só acréscimos: nome novo, parâmetro com padrão", "nada — e ganha o novo"], ["**maior** (1.x → 2.0)", "algo saiu, mudou de nome ou de assinatura", "ler a seção *Quebra* do CHANGELOG"]]}},
  { code: `dataforge abi v1.4/src/main.df src/main.df
# veredito: menor
# e sai com codigo diferente de zero quando algo QUEBRA — no CI, antes da tag`, lang: 'bash' },
  {"table": {"head": ["Muda a superfície (é quebra)", "Não muda"], "rows": [["remover ou renomear uma ação exportada", "renomear com `relay novo, novo as antigo`"], ["renomear um **parâmetro** — a chamada com nome existe", "renomear uma variável interna"], ["acrescentar parâmetro **sem** padrão", "acrescentar parâmetro **com** padrão"], ["mudar o tipo declarado de retorno", "mudar a implementação"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Antes da 1.0 não há promessa", "texto": "Em `0.x`, qualquer versão pode quebrar — é o que o número diz. Fique lá enquanto a API muda, e suba para a 1.0 quando puder prometer. Uma 1.0 que quebra a cada menor ensina a não confiar no número."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"A promessa de estabilidade"}
      description={"O que cada número de versão promete, escrito — e conferido pelo abi a cada release."}
      href={"/docs/bibliotecas/estabilidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
