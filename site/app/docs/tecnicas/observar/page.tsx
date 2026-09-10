import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Observabilidade e linhagem",
  description: "As sete perguntas, métricas com percentil, tracing aninhado e de onde veio cada número.",
};

const blocos: Bloco[] = [
  {"p": "Observabilidade é conseguir responder, **sem abrir o código**:"},
  {"list": ["executou?", "quanto tempo demorou?", "quantos registros processou?", "quantos falharam?", "qual etapa falhou?", "quando?", "qual versão estava rodando?"]},
  {"p": "Log sozinho responde a primeira e a sexta. As outras cinco exigem **número** — e é isso que separa observabilidade de logging."},
  {"h2": "O painel"},
  { code: `adopt Arcane.Observar as O

p := O.painel("etl-vendas", "2.1.0")

O.contar(p, "linhas_lidas", 40000)      // só sobe
O.medir(p, "latencia_ms", 12.4)         // guarda a distribuição
O.marcar(p, "versao_do_esquema", 7)     // o último vale

out O.relatorio(p)`, lang: 'df' },
  {"h2": "A média esconde"},
  { code: `  medida                         p50       p95       p99       máx
  latencia_ms                  2.000     2.000    40.000    40.000`, lang: 'text' },
  {"p": "Um pipeline com média de 3,9s e **p99 de 40s** tem um problema que a média nunca mostra — e é o p99 que o usuário sente. `medir` guarda a distribuição e devolve p50, p95 e p99."},
  {"callout": {"tipo": "nota", "titulo": "Amostragem por reservatório", "texto": "O percentil exato exige a lista inteira, e uma lista sem teto vira vazamento de memória num processo longo. Dez mil amostras dão p99 com erro menor que 1% — e o reservatório garante que cada valor tenha a **mesma** chance de ficar, independente de quando chegou. Guardar só os primeiros mil daria o percentil do começo da execução."}},
  {"p": "O cálculo é interpolação linear — a mesma de `numpy.percentile`. Não é detalhe: um p99 calculado de outro jeito daria um número diferente do painel que a equipe já olha, e ninguém saberia qual acreditar."},
  {"h2": "Tracing: onde o tempo foi"},
  { code: `extrair := O.abrir(p, "extrair")
// …
O.fechar(p, extrair)

transformar := O.abrir(p, "transformar")
limpar := O.abrir(p, "limpar", transformar)      // aninhado
O.fechar(p, limpar)
O.fechar(p, transformar)`, lang: 'df' },
  { code: `    transformar                 0.048s  60.3% ██████████████
      enriquecer                  0.035s  44.4% ██████████
      limpar                      0.013s  15.9% ███
    extrair                     0.025s  31.7% ███████
  ✗ carregar                    0.006s   8.0% █`, lang: 'text' },
  {"p": "*carregar levou 40s* não ajuda. *Dos 40s, 38 foram no INSERT* resolve — e é o aninhamento que mostra isso."},
  {"h3": "A forma que não deixa trecho aberto"},
  { code: `O.cronometrar(p, "carregar", lambda => carregar(dados))`, lang: 'df' },
  {"p": "Mesmo quando a ação estoura, o trecho é fechado — marcado como falha, e com a mensagem. E `resumo` **avisa** se sobrou trecho aberto no fim, que é quase sempre um `ensure` que faltou."},
  {"h2": "Linhagem: de onde veio esse número"},
  { code: `O.derivar(p, "vendas_bruto",  ["api_erp"], "extração diária")
O.derivar(p, "vendas_prata",  ["vendas_bruto"], "limpeza e deduplicação")
O.derivar(p, "painel_diario", ["vendas_prata", "metas"], "agregação por dia")`, lang: 'df' },
  {"p": "Quando um número no painel está errado, a pergunta não é *onde está o bug*: é **de onde veio esse número**. Sem linhagem registrada, a resposta sai de ler o código de trás para a frente — e o código mudou desde que aquele número foi calculado."},
  { code: `O.origem(p, "painel_diario")
//   vendas_prata → painel_diario   (agregação por dia)
//   metas        → painel_diario   (agregação por dia)
//   vendas_bruto → vendas_prata    (limpeza e deduplicação)
//   api_erp      → vendas_bruto    (extração diária)`, lang: 'df' },
  {"h3": "E a pergunta inversa, que é a mais cara"},
  { code: `O.impacto(p, "vendas_bruto")
// ["vendas_prata", "painel_diario"]`, lang: 'df' },
  {"p": "*Se eu mexer aqui, o que quebra?* — a pergunta que trava refatoração em pipeline grande."},
  {"h2": "Sair"},
  { code: `O.relatorio(p)         // tudo em texto, para o log
O.prometheus(p)        // o formato de exposição, para o coletor
O.salvar(p, "obs/execucao.json")
O.alertar(p, regras)`, lang: 'df' },
  {"h3": "Alertas"},
  { code: `regras := {
    "latencia_ms": {"acima": 10, "estatistica": "p99", "texto": "a cauda está longa"},
    "erros":       {"acima": 0, "texto": "houve falha"},
}`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Alerta é sobre o que exige ação", "texto": "Uma regra que dispara todo dia deixa de ser lida em uma semana — e aí a que importa passa despercebida junto. Alerte sobre o p99, não sobre a média: é a cauda que dói."}},
  {"h3": "Expor no Kiln"},
  { code: `route GET "/metricas":
    respond text O.prometheus(painel)`, lang: 'df' },
];

const headings = [{ id: 'o-painel', text: "O painel", level: 2 as const }, { id: 'a-media-esconde', text: "A média esconde", level: 2 as const }, { id: 'tracing-onde-o-tempo-foi', text: "Tracing: onde o tempo foi", level: 2 as const }, { id: 'linhagem-de-onde-veio-esse-numero', text: "Linhagem: de onde veio esse número", level: 2 as const }, { id: 'sair', text: "Sair", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Observabilidade e linhagem"}
      description={"As sete perguntas, métricas com percentil, tracing aninhado e de onde veio cada número."}
      href={"/docs/tecnicas/observar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
