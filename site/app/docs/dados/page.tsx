// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_etl.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Análise de dados",
  description: "Carregar, limpar, agregar e descrever — o caminho de um conjunto de dados até a resposta.",
};

const blocos: Bloco[] = [
  {"p": "Analisar dados é sempre a mesma sequência: **carregar**, **conferir**, **limpar**, **agregar**, **responder**. A linguagem traz as cinco etapas, e esta página é o caminho inteiro com um conjunto pequeno o bastante para caber na tela."},
  {"h2": "O quadro de dados"},
  {"p": "`Arcane.Analytics` trabalha com um **frame**: um cluster de vaults, que é o que `IO.read_csv(caminho, yes)` devolve e o que `Database.query` devolve."},
  { code: `adopt Arcane.Analytics as An

vendas := [
    {"produto": "cafe",   "regiao": "sul",   "valor": 120.0, "qtd": 4},
    {"produto": "cafe",   "regiao": "norte", "valor": 90.0,  "qtd": 3},
    {"produto": "cha",    "regiao": "sul",   "valor": 60.0,  "qtd": 2},
    {"produto": "cha",    "regiao": "norte", "valor": 45.0,  "qtd": 1},
    {"produto": "acucar", "regiao": "sul",   "valor": 30.0,  "qtd": 5}
]

out len(vendas), "registros"
`, lang: 'df' },
  {"h2": "1. Conferir antes de confiar"},
  {"p": "A primeira coisa a fazer com um conjunto novo não é calcular — é **olhar**. Quantas linhas, quais colunas, o que está faltando:"},
  { code: `adopt Arcane.Analytics as An

action colunas_de(dados):
    yield keys(dados[0])

action faltando(dados, coluna):
    yield len([l cycle l in dados given (l[coluna] ?? void) is void])

out colunas_de(vendas)
out faltando(vendas, "valor"), "sem valor"
`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A média que mente", "texto": "Uma média calculada sobre dados com buraco não avisa que tinha buraco — ela só sai menor. Conferir a contagem de ausentes **antes** de agregar é o passo que separa um relatório de um chute."}},
  {"h2": "2. Limpar"},
  { code: `action limpo(dados):
    yield [linha cycle linha in dados
           given (linha["valor"] ?? 0.0) > 0.0]

action com_total(dados):
    yield [linha with {"total": linha["valor"] * linha["qtd"]}
           cycle linha in dados]
`, lang: 'df' },
  {"p": "Note que nada é mutado: cada etapa devolve um frame **novo**. É o que permite comparar o antes e o depois, e é o que faz um pipeline ser reexecutável."},
  {"h2": "3. Agregar"},
  { code: `action somar_por(dados, chave, campo):
    totais := {}
    cycle linha in dados:
        grupo := linha[chave]
        totais[grupo] := (totais[grupo] ?? 0.0) + linha[campo]
    yield totais

out somar_por(vendas, "produto", "valor")
out somar_por(vendas, "regiao", "valor")
`, lang: 'df' },
  { code: `{cafe: 210.0, cha: 105.0, acucar: 30.0}
{sul: 210.0, norte: 135.0}
`, lang: 'text', title: `saída` },
  {"p": "O vault como acumulador é `O(n)`: uma passada, e cada escrita é constante. A versão \"óbvia\" — para cada grupo, percorrer tudo filtrando — é `O(n × grupos)`, e o [`dataforge big-o`](/docs/big-o/padroes) acusa."},
  {"h2": "4. Descrever"},
  { code: `adopt Arcane.Analytics as An

valores := [v["valor"] cycle v in vendas]

out An.media(valores)
out An.mediana(valores)
out An.desvio_padrao(valores)
out min(valores), max(valores)
`, lang: 'df' },
  {"p": "**Média e mediana juntas dizem mais que qualquer uma sozinha.** Quando as duas se afastam, há assimetria — um valor muito alto puxando a média —, e é o sinal de que a média não representa o conjunto."},
  {"h2": "5. Responder, e mostrar"},
  {"p": "O resultado de uma análise termina de três formas, e cada uma tem o seu lugar:"},
  {"table": {"head": ["Onde termina", "Com o quê"], "rows": [["no terminal", "`out`, ou o pacote [`tabela`](/docs/pacotes/tabela)"], ["num arquivo", "`IO.write_csv`, `IO.write_json`, [`Arcane.Excel`](/docs/tecnicas/planilhas)"], ["numa página", "[Vitrine](/docs/vitrine) — o mesmo `.df` vira painel com gráfico"]]}},
  {"h2": "Quando os dados não cabem na memória"},
  {"p": "A regra prática: até alguns milhões de linhas, um cluster de vaults resolve. Acima disso, há três caminhos, e o primeiro costuma bastar:"},
  {"list": ["**Processar por partes**, com `stream action` — `O(1)` de espaço, ver [complexidade de espaço](/docs/big-o/espaco).", "**Deixar o banco agregar** — `SUM` e `GROUP BY` acontecem onde o dado já está, e volta só o resultado. Ver [SQLite](/docs/sqlite).", "**A ponte para o Python** — `adopt Python.pandas as pd` quando a conta é vetorizada e o volume justifica."]},
  { code: `adopt Python.numpy as np

a := np.array([1.0, 2.0, 3.0])
out (a * 2).tolist()        // a conta é do numpy, sem cópia na fronteira
`, lang: 'df' },
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/dados/etl", "title": "ETL", "desc": "extrair, transformar e carregar — com o que fazer quando falha"}, {"href": "/docs/dados/qualidade", "title": "Qualidade de dados", "desc": "as regras que impedem o relatório errado"}, {"href": "/docs/biblioteca/analytics", "title": "Arcane.Analytics", "desc": "a referência do módulo"}, {"href": "/docs/vitrine", "title": "Vitrine", "desc": "o resultado como página"}]},
];

const headings = [{ id: 'o-quadro-de-dados', text: "O quadro de dados", level: 2 as const }, { id: '1-conferir-antes-de-confiar', text: "1. Conferir antes de confiar", level: 2 as const }, { id: '2-limpar', text: "2. Limpar", level: 2 as const }, { id: '3-agregar', text: "3. Agregar", level: 2 as const }, { id: '4-descrever', text: "4. Descrever", level: 2 as const }, { id: '5-responder-e-mostrar', text: "5. Responder, e mostrar", level: 2 as const }, { id: 'quando-os-dados-nao-cabem-na-memoria', text: "Quando os dados não cabem na memória", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Análise de dados"}
      description={"Carregar, limpar, agregar e descrever — o caminho de um conjunto de dados até a resposta."}
      href={"/docs/dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
