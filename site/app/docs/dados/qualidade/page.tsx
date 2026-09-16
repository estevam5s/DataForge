// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_etl.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Qualidade de dados",
  description: "As regras que impedem o relatório errado — e por que elas rodam junto do pipeline, não depois.",
};

const blocos: Bloco[] = [
  {"p": "Um pipeline que termina sem erro **não** prova que os dados estão certos. Ele prova que nada estourou — e a diferença entre as duas coisas é onde vive o relatório errado que ninguém contesta."},
  {"h2": "As seis perguntas"},
  {"table": {"head": ["Dimensão", "A pergunta", "Como se mede"], "rows": [["**completude**", "falta alguma coisa?", "quantos vazios por coluna"], ["**unicidade**", "há repetido?", "contagem de chaves distintas × total"], ["**validade**", "o valor faz sentido?", "faixa, formato, lista de valores aceitos"], ["**consistência**", "as partes concordam?", "o total bate com a soma das partes?"], ["**pontualidade**", "o dado é de hoje?", "a data mais recente × agora"], ["**volume**", "veio a quantidade esperada?", "linhas de hoje × a média dos últimos dias"]]}},
  {"callout": {"tipo": "dica", "titulo": "A última é a que mais pega", "texto": "Um arquivo que chegou com 3 linhas quando sempre tem 30 mil passa por todas as outras verificações — cada uma das 3 linhas está perfeita. Comparar o **volume** com o histórico é a regra mais barata e a que mais evita relatório errado."}},
  {"h2": "Escrever uma regra"},
  { code: `record Regra:
    nome: String
    grave: Boolean := yes

action conferir(dados, regra, teste):
    falhas := [l cycle l in dados given not teste(l)]
    yield {"regra": regra.nome,
           "grave": regra.grave,
           "falhas": len(falhas),
           "total": len(dados),
           "exemplos": falhas[0:3]}
`, lang: 'df' },
  { code: `resultados := [
    conferir(vendas, Regra("valor positivo"), lambda l: l["valor"] > 0.0),
    conferir(vendas, Regra("regiao conhecida"),
             lambda l: l["regiao"] in ["sul", "norte"]),
    conferir(vendas, Regra("qtd inteira", no), lambda l: l["qtd"] >= 1)
]

cycle r in resultados:
    marca := "x" given r["falhas"] > 0 otherwise " "
    out $"[{marca}] {r['regra']}: {r['falhas']} de {r['total']}"
`, lang: 'df' },
  {"h2": "Grave interrompe; aviso não"},
  {"p": "Toda regra precisa de uma resposta declarada para \"e se falhar?\". Sem isso, ou o pipeline para por qualquer coisa, ou nunca para por nada:"},
  { code: `action decidir(resultados):
    graves := [r cycle r in resultados
               given r["grave"] and r["falhas"] > 0]
    given len(graves) > 0:
        trigger $"{len(graves)} regra(s) grave(s) falharam; o carregamento nao aconteceu"

    avisos := [r cycle r in resultados given r["falhas"] > 0]
    cycle a in avisos:
        out $"aviso: {a['regra']} — {a['falhas']} linha(s)"
    yield yes
`, lang: 'df' },
  {"table": {"head": ["Gravidade", "O que fazer"], "rows": [["**grave**", "não carregar. Um dado errado publicado é pior que um relatório atrasado"], ["**aviso**", "carregar, registrar, e olhar amanhã"], ["**informativo**", "só o número, para acompanhar a tendência"]]}},
  {"h2": "Onde as regras rodam"},
  {"p": "**Junto do pipeline, entre transformar e carregar** — não num relatório separado que alguém abre na sexta."},
  { code: `action rodar(caminho, db):
    brutas := extrair(caminho)
    limpas := transformar(brutas)

    resultados := conferir_tudo(limpas)
    decidir(resultados)               // para aqui se houver grave

    yield carregar(db, limpas)
`, lang: 'df' },
  {"p": "A razão é simples: a única hora em que alguém consegue agir sobre um dado ruim é **antes** de ele virar a fonte de um painel."},
  {"h2": "Guardar o resultado das regras"},
  {"p": "Gravar a saída das verificações a cada execução transforma \"os números pareciam estranhos\" em uma série temporal:"},
  { code: `IO.write_json($"qualidade/{data}.json", {
    "data": data,
    "linhas": len(limpas),
    "regras": resultados
})
`, lang: 'df' },
  {"p": "Com um histórico, a regra de **volume** deixa de precisar de número mágico: ela compara com a média dos últimos dias."},
  {"h2": "Testar as regras"},
  {"p": "Uma regra de qualidade é código, e código sem teste dá falso negativo em silêncio — a regra que nunca acusa nada parece estar tudo bem:"},
  { code: `adopt Arcane.Crucible as C

crucible "regras":
    trial "valor negativo e pego":
        r := conferir([{"valor": -1.0}], Regra("positivo"),
                      lambda l: l["valor"] > 0.0)
        expect r["falhas"] is 1

    trial "valor positivo passa":
        r := conferir([{"valor": 5.0}], Regra("positivo"),
                      lambda l: l["valor"] > 0.0)
        expect r["falhas"] is 0

C.run()
`, lang: 'df' },
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/tecnicas/qualidade", "title": "Arcane.Qualidade", "desc": "o módulo com as regras prontas"}, {"href": "/docs/tecnicas/observar", "title": "Observabilidade e linhagem", "desc": "de onde veio cada número"}, {"href": "/docs/crucible", "title": "Crucible", "desc": "testar as regras"}]},
];

const headings = [{ id: 'as-seis-perguntas', text: "As seis perguntas", level: 2 as const }, { id: 'escrever-uma-regra', text: "Escrever uma regra", level: 2 as const }, { id: 'grave-interrompe-aviso-nao', text: "Grave interrompe; aviso não", level: 2 as const }, { id: 'onde-as-regras-rodam', text: "Onde as regras rodam", level: 2 as const }, { id: 'guardar-o-resultado-das-regras', text: "Guardar o resultado das regras", level: 2 as const }, { id: 'testar-as-regras', text: "Testar as regras", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Qualidade de dados"}
      description={"As regras que impedem o relatório errado — e por que elas rodam junto do pipeline, não depois."}
      href={"/docs/dados/qualidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
