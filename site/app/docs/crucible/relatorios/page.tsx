// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/crucible_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Relatórios, benchmark e CI",
  description: "Quatro formatos, e a medição que mostra o p95 em vez de só a média.",
};

const blocos: Bloco[] = [
  {"h2": "Os formatos"},
  { code: `dataforge crucible                        # texto, colorido
dataforge crucible --formato=junit --out=r.xml
dataforge crucible --formato=json --out=r.json
dataforge crucible --formato=tap`, lang: 'bash' },
  {"table": {"head": ["Formato", "Para"], "rows": [["texto", "ler no terminal"], ["JUnit XML", "GitHub Actions, GitLab, Jenkins — todos leem"], ["JSON", "processar por programa"], ["TAP 13", "o formato mais simples e portável que existe"]]}},
  {"p": "O JUnit existe porque integrar com cada CI exigiria que cada um aprendesse o formato do Crucible — e nenhum vai aprender."},
  {"h2": "A ordem do relatório"},
  {"p": "Primeiro o mapa, uma linha por suíte. Depois cada falha com espaço para respirar. Quem roda a suíte quer saber se está verde; quando não está, quer o detalhe de cada uma — e não rolar a tela procurando o vermelho no meio do verde."},
  {"h2": "Benchmark"},
  { code: `crucible "Desempenho":
    bench "soma de mil" times 100:
        total := 0
        cycle i from 1 to 1000:
            total += i`, lang: 'df' },
  { code: `    ⏱  soma de mil: 0.0821ms media, 0.0798ms mediana,
       p95 0.0954ms, 12180 ops/s`, lang: 'text' },
  {"callout": {"tipo": "dica", "titulo": "Média sozinha engana", "texto": "Uma pausa do coletor de lixo no meio de mil voltas move a média e não aparece nela. A mediana e o p95 contam a história inteira — e o p95 é o que o usuário de um serviço web sente."}},
  {"p": "Pela biblioteca, com mais controle:"},
  { code: `adopt Crucible

m := Crucible.benchmark("soma", lambda => sum(range(1000)), 500)
out m["media_ms"], m["mediana_ms"], m["p95_ms"], m["ops_por_s"]`, lang: 'df' },
  {"h2": "Ordem aleatória"},
  {"p": "Um teste que só passa porque outro rodou antes é uma bomba-relógio. `--aleatorio` a detona cedo:"},
  { code: `dataforge crucible --aleatorio
# ordem aleatoria, semente 1738 (--semente=1738 repete)

dataforge crucible --aleatorio --semente=1738   # reproduz exatamente`, lang: 'bash' },
  {"p": "A semente aparece no relatório justamente para a falha ser reproduzível — uma ordem aleatória que não se repete é impossível de depurar."},
  {"h2": "Instabilidade"},
  { code: `dataforge crucible --repetir=20`, lang: 'bash' },
  {"p": "Roda cada trial vinte vezes. Um teste que passa às vezes depende de tempo, de ordem, ou de estado que sobrou — e é melhor descobrir isso agora que numa madrugada de plantão."},
  {"h2": "No CI"},
  { code: `name: testes
on: [push, pull_request]

jobs:
  crucible:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh
      - run: dataforge check src/ --strict
      - run: dataforge big-o src/ --strict
      - run: dataforge crucible --formato=junit --out=resultados.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: resultados
          path: resultados.xml`, lang: 'text' },
  {"p": "`dataforge crucible` sai com código 1 quando algo falha, então o passo reprova sozinho."},
  {"h2": "Lendo o resultado por programa"},
  { code: `adopt Crucible

Crucible.suite("Exemplo", lambda => [
    Crucible.trial("passa", lambda => Crucible.expect(1).to_be(1))
])

resumo := Crucible.run()
out resumo["passou"], resumo["falhou"], resumo["verde"]

cycle r in Crucible.results():
    out r["nome"], r["estado"], r["duracao"]`, lang: 'df' },
];

const headings = [{ id: 'os-formatos', text: "Os formatos", level: 2 as const }, { id: 'a-ordem-do-relatorio', text: "A ordem do relatório", level: 2 as const }, { id: 'benchmark', text: "Benchmark", level: 2 as const }, { id: 'ordem-aleatoria', text: "Ordem aleatória", level: 2 as const }, { id: 'instabilidade', text: "Instabilidade", level: 2 as const }, { id: 'no-ci', text: "No CI", level: 2 as const }, { id: 'lendo-o-resultado-por-programa', text: "Lendo o resultado por programa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Relatórios, benchmark e CI"}
      description={"Quatro formatos, e a medição que mostra o p95 em vez de só a média."}
      href={"/docs/crucible/relatorios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
