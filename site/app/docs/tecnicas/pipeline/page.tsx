import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Pipelines e orquestração",
  description: "DAG, dependências, retry e carga incremental — sem servidor, sem agendador, sem banco de metadados.",
};

const blocos: Bloco[] = [
  {"p": "Airflow, Prefect e Dagster resolvem orquestração com um servidor, um banco de metadados e um agendador. `Arcane.Pipeline` resolve com **uma estrutura de dados e um laço** — o que cabe num processo só, que é onde a maioria dos pipelines de verdade vive."},
  { code: `adopt Arcane.Pipeline as P

fluxo := P.fluxo("vendas")

P.etapa(fluxo, "extrair", extrair)
P.etapa(fluxo, "limpar",   limpar,   ["extrair"])
P.etapa(fluxo, "conferir", conferir, ["limpar"])
P.etapa(fluxo, "carregar", carregar, ["conferir"])

relatorio := P.rodar(fluxo)`, lang: 'df' },
  {"p": "A ordem sai das **dependências**, não da ordem em que você declarou — é a ordenação topológica que todo DAG faz. `P.grafico(fluxo)` mostra o resultado antes de rodar."},
  {"h2": "As três garantias"},
  {"h3": "1. Um ciclo é erro, não aviso"},
  { code: `P.etapa(fluxo, "x", acao_x, ["y"])
P.etapa(fluxo, "y", acao_y, ["x"])

erro: as etapas x, y dependem umas das outras.
  nota: um ciclo não tem ordem possível
  dica: quebre o ciclo, ou junte as etapas numa só`, lang: 'text' },
  {"p": "Não há ordem que satisfaça as duas. Escolher uma arbitrariamente produziria um resultado que ninguém consegue explicar — e que muda entre execuções."},
  {"h3": "2. Falhou? quem depende é PULADO"},
  { code: `ok      extrair
falhou  limpar     banco fora do ar
pulada  conferir   depende de limpar
pulada  carregar   depende de conferir
ok      notificar`, lang: 'text' },
  {"callout": {"tipo": "atencao", "titulo": "Rodar mesmo assim produz dado corrompido", "texto": "E dado corrompido é **pior** que dado ausente: o ausente alguém percebe. Uma etapa que não depende da que falhou continua rodando — `notificar`, acima, é justamente a que você quer que rode."}},
  {"h3": "3. Retry para a falha passageira"},
  { code: `// 3 tentativas, esperando 2s, 4s entre elas
P.etapa(fluxo, "carregar", carregar, ["limpar"], 3, 2)`, lang: 'df' },
  {"p": "A espera **cresce** a cada tentativa. Se o banco está ocupado, insistir no mesmo ritmo mantém ele ocupado. E o relatório diz em qual tentativa passou — uma etapa que sempre precisa de três é um problema que a média esconde."},
  {"h2": "Carga incremental"},
  {"p": "Reprocessar tudo a cada execução é o que faz um pipeline de 10 minutos virar um de 6 horas em dois anos."},
  { code: `fluxo := P.fluxo("vendas", "estado/vendas.json")

action extrair(ctx):
    desde := P.marca(fluxo, "ate") ?? "1970-01-01"
    novas := Banco.consultar(db,
        "SELECT * FROM vendas WHERE atualizado_em > ?", [desde])
    given len(novas) bigger 0:
        P.marcar(fluxo, "ate", maior(novas, "atualizado_em"))
    yield novas`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "A marca só avança quando a execução INTEIRA termina bem", "texto": "É a garantia que evita perda silenciosa. Avançar por etapa deixaria o checkpoint à frente do que foi realmente carregado — e o que ficou no meio some para sempre, sem ninguém notar. O arquivo é gravado num temporário e renomeado: um checkpoint pela metade é pior que nenhum."}},
  {"h2": "Rodar só um pedaço"},
  { code: `P.rodar_ate(fluxo, "limpar")   // roda 'extrair' e 'limpar', e para`, lang: 'df' },
  {"p": "Ele resolve as dependências sozinho — roda o que `limpar` precisa, e nada além. É como se depura um pipeline longo sem esperar a carga."},
  {"h2": "O relatório"},
  { code: `{
  "fluxo": "vendas",
  "ok": yes,
  "duracao": 12.4,
  "resumo": {"total": 4, "ok": 4, "falhou": 0, "pulada": 0, "saltada": 0},
  "etapas": [
    {"etapa": "extrair", "estado": "ok", "duracao": 8.1, "tentativas": 1},
    …
  ],
  "resultados": {"extrair": [ … ], "limpar": [ … ]}
}`, lang: 'json' },
  {"p": "O relatório é o produto. Sem ele, saber o que aconteceu exige ler log — e log de pipeline é o que ninguém lê até quebrar."},
  {"h2": "Condição: o mesmo fluxo em modos diferentes"},
  { code: `P.etapa(fluxo, "carga_completa", completa, ["limpar"],
        1, 0, lambda ctx: MODO is "cheio")`, lang: 'df' },
  {"p": "A etapa é **saltada** quando a condição dá falso — e saltar não é falhar: o fluxo segue verde. É como se roda o mesmo pipeline em modo cheio e incremental sem duplicá-lo."},
];

const headings = [{ id: 'as-tres-garantias', text: "As três garantias", level: 2 as const }, { id: '1-um-ciclo-e-erro-nao-aviso', text: "1. Um ciclo é erro, não aviso", level: 3 as const }, { id: '2-falhou-quem-depende-e-pulado', text: "2. Falhou? quem depende é PULADO", level: 3 as const }, { id: '3-retry-para-a-falha-passageira', text: "3. Retry para a falha passageira", level: 3 as const }, { id: 'carga-incremental', text: "Carga incremental", level: 2 as const }, { id: 'rodar-so-um-pedaco', text: "Rodar só um pedaço", level: 2 as const }, { id: 'o-relatorio', text: "O relatório", level: 2 as const }, { id: 'condicao-o-mesmo-fluxo-em-modos-diferentes', text: "Condição: o mesmo fluxo em modos diferentes", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Pipelines e orquestração"}
      description={"DAG, dependências, retry e carga incremental — sem servidor, sem agendador, sem banco de metadados."}
      href={"/docs/tecnicas/pipeline"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
