// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Flame graph, pausas e contenção",
  description: "Onde o tempo foi — por ação da linguagem, não por quadro do Python. Mais as pausas do coletor e a contenção que nenhum perfil de CPU mostra.",
};

const blocos: Bloco[] = [
  {"p": "Um *benchmark* diz que está lento; um **perfil** diz onde. `P.comecar_perfil` sombreia o mesmo gancho que o [`dataforge profile`](/docs/cli) usa, e conta o tempo **próprio** de cada ação — o total menos o que as chamadas internas gastaram."},
  {"callout": {"tipo": "nota", "titulo": "Por que tempo próprio, e não acumulado", "texto": "Somar o acumulado daria mais de 100%: numa recursão, o tempo das chamadas internas está dentro do próprio. Um flame graph que soma 207% não é um flame graph. O tempo próprio é o que responde **onde mexer**, que é a pergunta."}},
  { code: `dataforge profile src/main.df      # o resumo, por acao`, lang: 'bash' },
  {"p": "E de dentro da linguagem, com o gráfico:"},
  { code: `// perfil := P.perfilar(minha_acao)
// IO.write("perfil.svg", P.chama_svg(perfil["perfil"]))
// IO.write("perfil.folded", P.chama_texto(perfil["perfil"]))`, lang: 'df', title: `O flame graph, gravado` },
  {"table": {"head": ["Saída", "Para que serve"], "rows": [["`P.chama_svg(perfil)`", "o gráfico, **sem nada de fora**: sem CDN, sem script e sem fonte remota — a mesma regra da [Vitrine](/docs/vitrine), porque perfil costuma ser aberto em rede fechada"], ["`P.chama_texto(perfil)`", "o formato **dobrado** (`a;b;c 1234`), que o `flamegraph.pl` e os visualizadores de navegador consomem"]]}},
  {"p": "O formato dobrado foi escolhido por isso: um formato próprio obrigaria a escrever o visualizador junto."},
  {"h2": "Pausas do coletor"},
  {"p": "A pausa do coletor é o que transforma um P50 bom num P99 ruim, e ela **não aparece** em medida nenhuma que olhe só o tempo total. `gc.callbacks` entrega o começo e o fim de cada coleta — é a medida na fonte."},
  { code: `adopt Arcane.Perfil as P

action trabalho():
    total := 0
    cycle i from 1 to 50:
        total += i
    yield total

r := P.gc_pausas(trabalho)

assert r["resultado"] is 1275
assert "p95" in r and "por_geracao" in r
assert r["total_ms"] smaller 50`, lang: 'df' },
  {"h2": "Contenção de trava"},
  {"p": "Contenção **não aparece num perfil de CPU**: a thread bloqueada não gasta CPU nenhuma. Ela aparece como latência que ninguém explica — e a única forma de vê-la é medir na própria trava."},
  { code: `adopt Arcane.Perfil as P

trava := P.trava()
P.com_trava(trava, lambda => 1 + 1)
P.com_trava(trava, lambda => 2 + 2)

e := P.estatisticas_da_trava(trava)
assert e["aquisicoes"] is 2
assert e["esperas"] is 0          // sem disputa, ninguem esperou`, lang: 'df' },
  {"p": "A distinção é feita por uma tentativa **sem bloqueio** antes da aquisição real: sem ela, toda aquisição contaria como espera, e a métrica diria que há contenção em programa de uma thread só."},
];

const headings = [{ id: 'pausas-do-coletor', text: "Pausas do coletor", level: 2 as const }, { id: 'contencao-de-trava', text: "Contenção de trava", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Flame graph, pausas e contenção"}
      description={"Onde o tempo foi — por ação da linguagem, não por quadro do Python. Mais as pausas do coletor e a contenção que nenhum perfil de CPU mostra."}
      href={"/docs/observabilidade/chamadas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
