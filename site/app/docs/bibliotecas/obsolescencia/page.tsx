// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Marcar o que vai sumir",
  description: "Arcane.Evolucao.obsoleta — a ação continua funcionando, e quem a chama é avisado uma vez.",
};

const blocos: Bloco[] = [
  {"p": "Remover uma ação de uma versão para a outra quebra quem a usa no dia da atualização. O caminho é avisar **antes**: numa versão menor, a ação continua funcionando e avisa; numa versão maior, ela sai. Quem prestou atenção ao aviso já migrou."},
  { code: `adopt Arcane.Evolucao as Ev

action calcular_total(itens):
    yield sum(itens)

mark @Ev.obsoleta("o nome dizia menos do que faz", desde := "1.4", use := "calcular_total")
action total(itens):
    yield calcular_total(itens)

cycle i in range(0, 3):
    assert total([1, 2]) is 3       // funciona — e avisa UMA vez

a := Ev.avisos()
assert len(a) is 1 and a[0]["acao"] is "total"
out a[0]["mensagem"]`, lang: 'df' },
  { code: `$ dataforge run app.df
aviso: 'total' esta obsoleta desde a 1.4: o nome dizia menos do que faz. Use 'calcular_total'.`, lang: 'text' },
  {"h2": "Três decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["o aviso sai **uma vez por ação**", "uma ação obsoleta num laço de um milhão imprimiria um milhão de linhas — e o aviso que se repete é o aviso que se aprende a filtrar"], ["o aviso vai para a **saída de erro**", "um programa cuja saída é lida por outro (CSV, JSON) teria um aviso no meio dos dados"], ["`DF_OBSOLETOS=erro` reprova", "o aviso impresso não para nada; no CI, ele precisa reprovar"]]}},
  { code: `DF_OBSOLETOS=erro dataforge test        # no CI: o uso obsoleto reprova
DF_OBSOLETOS=silencio dataforge run app.df   # quando nao da para mudar agora`, lang: 'bash' },
  {"h2": "O calendário"},
  {"table": {"head": ["Versão", "O que acontece com `total`"], "rows": [["1.4 (menor)", "`calcular_total` nasce; `total` passa a avisar"], ["1.5, 1.6 (menores)", "continua avisando — tempo para migrar"], ["2.0 (maior)", "`total` sai; o CHANGELOG diz o que usar"]]}},
];

const headings = [{ id: 'tres-decisoes', text: "Três decisões", level: 2 as const }, { id: 'o-calendario', text: "O calendário", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Marcar o que vai sumir"}
      description={"Arcane.Evolucao.obsoleta — a ação continua funcionando, e quem a chama é avisado uma vez."}
      href={"/docs/bibliotecas/obsolescencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
