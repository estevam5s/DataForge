# -*- coding: utf-8 -*-
"""O Quadro, os verbos de pipeline, e o mapa do documento de origem."""

PAGINAS = [
{
"href": "/docs/dados/quadro",
"title": "Quadro — a tabela de dados",
"description": "Colunas nomeadas e linhas como vault: filtrar, agrupar, resumir, juntar, pivotar, limpar e descrever.",
"blocos": [
 {"p": "`Quadro` é a tabela da linguagem. Ele existe porque a forma natural de dado aqui — um cluster de vaults — responde bem a \"percorra\" e mal a \"agrupe por cidade e some o valor\"."},
 {"code": """adopt Arcane.Quadro as Q

vendas := Q.de_vaults([
    {"produto": "cafe",   "regiao": "sul",   "valor": 120.0, "qtd": 4},
    {"produto": "cafe",   "regiao": "norte", "valor": 90.0,  "qtd": 3},
    {"produto": "cha",    "regiao": "sul",   "valor": 60.0,  "qtd": 2},
    {"produto": "cha",    "regiao": "norte", "valor": void,  "qtd": 1},
    {"produto": "acucar", "regiao": "sul",   "valor": 30.0,  "qtd": 5}
])

out typeof(vendas)          // Quadro
out vendas.forma()          // [5, 4]
out vendas.texto()
""", "lang": "df"},
 {"code": """produto  regiao  valor  qtd
-------  ------  -----  ---
cafe     sul     120    4
cafe     norte   90     3
cha      sul     60     2
cha      norte   void   1
acucar   sul     30     5
[5 linha(s) × 4 coluna(s)]
""", "lang": "text", "title": "saída"},

 {"h2": "As cinco decisões"},
 {"table": {"head": ["Decisão", "Porque"], "rows": [
   ["**A linha é um vault**", "é a forma que o resto da linguagem já usa: `IO.read_csv(c, yes)` devolve vaults, `Database.query` devolve vaults, e o `>>` já sabe percorrê-los"],
   ["**Por dentro é colunar**", "`descrever`, `normalizar` e `correlacao` viram uma passada por coluna em vez de uma por célula"],
   ["**Todo verbo devolve um quadro NOVO**", "como `record` e `with`: o original nunca muda, e o pipeline fica reexecutável"],
   ["**A ausência tem um nome só**", "`void`, texto vazio e NaN são três jeitos de dizer a mesma coisa; tratá-los como coisas diferentes é de onde vem metade do bug de limpeza"],
   ["**Coluna que não existe é ERRO**", "com sugestão. Devolver uma coluna vazia calada é o jeito mais rápido de um relatório sair errado sem ninguém notar"]]}},
 {"code": """out vendas.pegar("prodto")
""", "lang": "df"},
 {"code": """erro: a coluna 'prodto' não existe neste quadro
  = nota: as colunas são: produto, regiao, valor, qtd
  = dica: você quis dizer 'produto'?
""", "lang": "text"},

 {"h2": "Nascer"},
 {"table": {"head": ["Forma", "De onde vem o dado"], "rows": [
   ["`Q.de_vaults(linhas)`", "um cluster de vaults — o que `read_csv` e `query` devolvem"],
   ["`Q.de_colunas(vault)`", "um vault de clusters — a forma colunar"],
   ["`Q.de_csv(caminho)`", "um arquivo; a primeira linha é o cabeçalho"],
   ["`Q.de_json(caminho)`", "cluster de vaults ou vault de clusters"],
   ["`Q.vazio(colunas)`", "um quadro sem linhas, com as colunas declaradas"]]}},
 {"callout": {"tipo": "dica", "titulo": "O CSV traz tudo como texto", "texto": "Somar uma coluna de texto é o primeiro engano de quem chega. `Q.de_csv` infere o tipo por padrão — e só converte a coluna **inteira**: uma coluna com `[\"1\", \"2\", \"n/a\"]` fica como está, porque converter metade produziria uma coluna de dois tipos."}},

 {"h2": "Olhar antes de calcular"},
 {"p": "`perfil()` é o primeiro comando a rodar num conjunto que você não conhece:"},
 {"code": """out vendas.perfil().texto()
""", "lang": "df"},
 {"code": """coluna   tipo     linhas  ausentes  ausentes_pct  distintos  minimo  maximo  exemplo
-------  -------  ------  --------  ------------  ---------  ------  ------  -------
produto  String   5       0         0             3          void    void    cafe
regiao   String   5       0         0             2          void    void    sul
valor    Float    5       1         20            4          30      120     120
qtd      Integer  5       0         0             5          1       5       4
""", "lang": "text", "title": "saída"},
 {"p": "E `descrever()` dá contagem, média, desvio, mínimo, quartis e máximo das colunas numéricas — **com a contagem de ausentes ao lado da média**, porque uma média sobre dados com buraco não avisa que tinha buraco."},

 {"h2": "Os verbos, por família"},
 {"table": {"head": ["Família", "Verbos"], "rows": [
   ["**olhar**", "`colunas`, `forma`, `altura`, `largura`, `coluna`, `linha`, `topo`, `fim`, `fatiar`, `amostra`, `texto`"],
   ["**escolher**", "`pegar`, `sem`, `renomear`, `onde`, `ordenar`, `distintas`, `duplicadas`"],
   ["**mudar**", "`com`, `mapear`, `converter`, `inferir_tipos`"],
   ["**ausência**", "`nulos`, `sem_nulos`, `preencher`"],
   ["**agrupar**", "`agrupar`, `resumir`, `contar_valores`, `tabela_cruzada`, `pivotar`, `despivotar`"],
   ["**juntar**", "`juntar` (dentro, esquerda, direita, fora), `empilhar`"],
   ["**escala**", "`normalizar`, `padronizar`, `codificar`, `discretizar`"],
   ["**estatística**", "`descrever`, `correlacao`, `perfil`, `fora_da_curva`"],
   ["**sair**", "`para_vaults`, `para_colunas`, `para_csv`, `para_json`"]]}},

 {"h2": "Agrupar e resumir"},
 {"code": """r := vendas.agrupar("produto").resumir({"valor": "soma", "qtd": "media"})
out r.texto()
""", "lang": "df"},
 {"code": """produto  valor_soma  qtd_media
-------  ----------  ---------
cafe     210         3.5
cha      60          1.5
acucar   30          5
""", "lang": "text", "title": "saída"},
 {"p": "As agregações são: `soma`, `media`, `mediana`, `minimo`, `maximo`, `contagem`, `contagem_valida`, `distintos`, `desvio`, `variancia`, `primeiro`, `ultimo`, `juntar` e `lista`."},
 {"callout": {"tipo": "atencao", "titulo": "A tabela é fechada de propósito", "texto": "O nome da agregação vem como **texto**, e um nome desconhecido é recusado com a lista do que existe. Aceitar qualquer ação abriria a porta para um nome vindo de fora — de um `?agregar=` de uma tela, por exemplo."}},
 {"p": "**`contagem` e `contagem_valida` respondem perguntas diferentes**: quantas linhas há, e quantas têm valor. Num conjunto com ausência, confundir as duas troca a média."},

 {"h2": "Juntar"},
 {"p": "Os quatro `JOIN` do SQL, com os nomes da linguagem:"},
 {"code": """regioes := Q.de_vaults([{"regiao": "sul", "gerente": "Ana"}])

out vendas.juntar(regioes, "regiao").altura()               // 3  — dentro
out vendas.juntar(regioes, "regiao", "esquerda").altura()   // 5
out vendas.juntar(regioes, "regiao", "fora").altura()       // 5
""", "lang": "df"},

 {"h2": "Limpar"},
 {"code": """limpo := vendas
    .preencher({"valor": "media"})     // ou um valor, "mediana", "anterior", "seguinte"
    .sem_duplicadas()
    .converter({"qtd": "Integer"})

out limpo.nulos()
""", "lang": "df"},
 {"p": "`converter` devolve `void` no que não converte, em vez de levantar: parar na primeira célula ruim de um CSV de um milhão de linhas não ajuda ninguém. Quantas não converteram aparece em `perfil()`, e é ali que a decisão se toma."},

 {"h2": "O quadro fala o protocolo da linguagem"},
 {"p": "Nada no `cycle`, no `len` ou no `>>` sabe o que é um quadro. Eles funcionam porque iterar um quadro dá **linhas como vault** — é o mesmo protocolo que faz a ponte para o Python funcionar sem conversão."},
 {"code": """cycle linha in vendas:
    out linha["produto"]

out len(vendas)                    // 5 linhas
out vendas["valor"]                // a coluna
out vendas[0]                      // a linha, como vault
out vendas[0:2].altura()           // uma fatia, como quadro
""", "lang": "df"},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/dados/verbos", "title": "Os verbos do pipeline", "desc": "a sintaxe: `>> onde valor bigger 50 >> agrupar produto`"},
   {"href": "/docs/dados", "title": "Análise de dados", "desc": "o caminho de um conjunto até a resposta"},
   {"href": "/docs/dados/mapa", "title": "O mapa do ecossistema", "desc": "o que é nativo, o que é ponte, e o que está fora"},
   {"href": "/docs/biblioteca", "title": "A biblioteca", "desc": "os 63 módulos, e onde cada um entra"}]},
]},

{
"href": "/docs/dados/verbos",
"title": "Os verbos do pipeline",
"description": "Seis palavras contextuais que fazem um quadro fluir pelo operador >> — com as colunas escritas nuas.",
"blocos": [
 {"p": "O operador `>>` já existia, com `sift`, `morph` e `distill`. Para dado tabular faltava o vocabulário: **seis verbos** que operam sobre o quadro inteiro, e não sobre um item por vez."},
 {"code": """resumo := vendas
    >> onde valor bigger 50
    >> agrupar produto
    >> resumir {"valor": "soma"}
    >> ordenar valor desc

out resumo.texto()
""", "lang": "df"},
 {"code": """produto  valor
-------  -----
cafe     210
cha      60
""", "lang": "text", "title": "saída"},

 {"h2": "Os seis"},
 {"table": {"head": ["Verbo", "Faz", "Devolve"], "rows": [
   ["`onde <expressão>`", "filtra, com as colunas escritas nuas", "quadro"],
   ["`pegar a, b`", "escolhe colunas, nessa ordem", "quadro"],
   ["`sem a`", "descarta colunas", "quadro"],
   ["`ordenar col [desc]`", "ordena", "quadro"],
   ["`agrupar col[, col2]`", "agrupa", "**agrupamento**"],
   ["`resumir {…}`", "agrega", "quadro"]]}},
 {"p": "`agrupar` é o único que não devolve quadro: um agrupamento não tem forma retangular até alguém dizer \"média de quê\". Depois dele vem `resumir` — e qualquer outro verbo ali diz isso."},

 {"h2": "A coluna se escreve nua"},
 {"p": "É o que faz o verbo valer a pena. `onde valor bigger 50` lê como se lê, sem `lambda l: l[\"valor\"]`:"},
 {"code": """out (vendas >> onde qtd bigger 3).altura()
""", "lang": "df"},
 {"p": "Nem todo cabeçalho de CSV é um identificador válido — `Valor Total` e `preco/kg` são nomes comuns de coluna. Por isso as duas formas convivem:"},
 {"code": """q := Q.de_vaults([{"Valor Total": 10}, {"Valor Total": 30}])
out (q >> pegar "Valor Total").colunas()
""", "lang": "df"},

 {"h2": "Duas regras de escopo, e elas são previsíveis"},
 {"table": {"head": ["Dentro de um `onde`", "Vale"], "rows": [
   ["um nome que é coluna", "**a coluna vence**, sempre"],
   ["um nome que não é coluna", "o escopo de fora, como em qualquer expressão"]]}},
 {"code": """limite := 100.0
out (vendas >> onde valor bigger limite).altura()    // 1 — 'limite' vem de fora
""", "lang": "df"},
 {"p": "A primeira regra é o contrato do verbo: dentro de um `onde`, um nome nu é uma coluna. Sem ela, o mesmo código leria de dois jeitos conforme o que houvesse no escopo."},

 {"h2": "A ausência não passa no filtro"},
 {"p": "Comparar com o **desconhecido** não dá nem sim nem não, e a linha não passa. É a lógica de três valores do SQL, e a de toda ferramenta de dados que existe:"},
 {"code": """out (vendas >> onde valor bigger 0).altura()     // 4 — a linha sem valor fica fora
out (vendas >> onde valor is void).altura()      // 1 — e quem quer a ausência pergunta
""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "A outra escolha era defensável, e inútil", "texto": "Levantar erro na comparação com `void` é o que a linguagem faz em toda expressão comum, e está certo lá. Aqui tornaria o verbo inutilizável: todo conjunto real tem ausência, e o primeiro `onde` de todo programa morreria na primeira linha vazia. **Só essa falha é engolida** — uma coluna que não existe, uma ação que quebra ou uma divisão por zero continuam subindo."}},

 {"h2": "Os verbos convivem com `sift` e `morph`"},
 {"p": "A conversão é preguiçosa: cada estágio pede a forma de que precisa, na hora em que precisa."},
 {"code": """out vendas >> onde regiao is "sul" >> morph l: l["produto"]
""", "lang": "df"},
 {"p": "E a fonte pode ser um **cluster de vaults**, que é o que sai de `IO.read_csv(caminho, yes)` e de `Database.query` — obrigar a converter na mão faria o verbo valer menos justamente onde o dado entra."},
 {"code": """linhas := [{"a": 1}, {"a": 5}]
out (linhas >> onde a bigger 2).altura()
""", "lang": "df"},

 {"h2": "Por que contextuais, e não reservadas"},
 {"p": "As seis palavras **não** entram em `KEYWORDS`. Elas valem só logo depois de um `>>`, e continuam livres como nome em todo o resto:"},
 {"code": """onde := 1
pegar := 2
agrupar := 3
out onde + pegar + agrupar
""", "lang": "df"},
 {"p": "É o mesmo tratamento das onze palavras do [Kiln](/docs/kiln). `agrupar`, `ordenar` e `pegar` são nomes bons demais para tirar de quem escreve — e este repositório já removeu sete palavras reservadas por serem caras sem entregar nada."},

 {"h2": "O que o analisador confere, e o que ele não pode"},
 {"p": "A expressão de um `onde` **não** é inferida no escopo de fora: os nomes dela são colunas, e o analisador não sabe quais colunas um quadro tem em tempo de análise. Inferir ali acusaria `onde valor bigger 50` com *\"'valor' is not defined\"* — um falso alarme no caminho mais comum do verbo, que é exatamente o que ensina a desligar a verificação inteira."},
 {"p": "O que ele confere é o que consegue provar: que o verbo existe, que `agrupar` é seguido de `resumir`, e o tipo que o pipeline produz."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/dados/quadro", "title": "O Quadro", "desc": "a estrutura por baixo dos verbos"},
   {"href": "/docs/pipelines", "title": "Pipelines", "desc": "sift, morph e distill — o operador de origem"},
   {"href": "/docs/dados/mapa", "title": "O mapa do ecossistema", "desc": "onde cada peça de dado mora"}]},
]},
{
"href": "/docs/dados/mapa",
"title": "O mapa do ecossistema de dados",
"description": "As 32 áreas de dados, cruzadas com o que a linguagem tem: o que é nativo, o que atravessa a ponte, e o que não existe por decisão.",
"blocos": [
 {"p": "Este documento é o **mapa**, e não a lista. Cada área do ciclo de vida do dado — ingestão, limpeza, transformação, validação, armazenamento, análise, visualização, aprendizado, governança — cruzada com o que existe, medido pelos símbolos dos módulos e não pela memória de quem escreveu."},
 {"p": "Três estados, e a diferença entre eles importa mais que a lista:"},
 {"table": {"head": ["Estado", "Significa"], "rows": [
   ["**nativo**", "está na linguagem ou na biblioteca padrão, sem dependência nenhuma"],
   ["**ponte**", "existe através de `adopt Python.x` — a biblioteca é do Python, o código é seu"],
   ["**fora**", "não existe, e a decisão está tomada: o motivo está escrito"]]}},

 {"h2": "1 — Fundamentos e estatística descritiva"},
 {"table": {"head": ["O que se pede", "Onde está"], "rows": [
   ["média, mediana, moda, variância, desvio", "**nativo** — `Quadro.descrever`, `Arcane.Analytics`"],
   ["mínimo, máximo, amplitude, percentis, quartis", "**nativo** — `descrever` traz q1, mediana e q3"],
   ["assimetria, curtose", "**nativo** — `Analytics.skewness`, `kurtosis`"],
   ["correlação e covariância", "**nativo** — `Quadro.correlacao`, `Analytics.covariance`"],
   ["outliers", "**nativo** — `Quadro.fora_da_curva` (1,5 × IQR)"],
   ["amostragem, amostra estratificada", "**nativo** — `Quadro.amostra`, `Analytics.stratified_sample`"],
   ["regressão, séries temporais", "**nativo** — `Analytics.linear_regression`, `moving_average`, `seasonality`, `trend`"],
   ["testes de hipótese, p-value, intervalo de confiança", "**ponte** — `adopt Python.scipy`; implementar a família inteira de testes sem dependência seria meio caminho"]]}},

 {"h2": "2 — Manipulação de dados"},
 {"p": "É a área que o [`Quadro`](/docs/dados/quadro) cobre por inteiro, e a razão de ele existir:"},
 {"table": {"head": ["O que se pede", "O verbo"], "rows": [
   ["DataFrame, Series, indexação", "`Quadro`, `coluna`, `linha`, `q[\"col\"]`, `q[0]`, `q[0:10]`"],
   ["seleção de colunas e linhas, filtros, ordenação", "`pegar`, `sem`, `onde`, `ordenar`"],
   ["agrupamento e agregação, `group_by`", "`agrupar` + `resumir`, com 14 agregações"],
   ["`join`, `merge`, `concat`", "`juntar` (dentro/esquerda/direita/fora), `empilhar`"],
   ["pivot tables", "`pivotar`, `despivotar`, `tabela_cruzada`"],
   ["transformação de colunas, aplicar função", "`com`, `mapear`"],
   ["dados ausentes, duplicatas", "`nulos`, `sem_nulos`, `preencher`, `distintas`, `duplicadas`"],
   ["conversão de tipos", "`converter`, `inferir_tipos`"],
   ["normalização, padronização, encoding", "`normalizar`, `padronizar`, `codificar`, `discretizar`"],
   ["operações vetorizadas", "**parcial** — colunar por dentro; o laço ainda é do interpretador. Para vetorização de verdade, a ponte para o `numpy`"]]}},

 {"h2": "3 e 4 — ETL e ELT"},
 {"table": {"head": ["Extrair de", "Estado"], "rows": [
   ["CSV, JSON, Excel, Parquet", "**nativo** — `Quadro.de_csv`, `de_json`, `Arcane.Excel`, `Arcane.Lago`"],
   ["SQLite", "**nativo** — `Arcane.Database`, 64 símbolos"],
   ["API REST, GraphQL", "**nativo** — `Arcane.Http`, `Arcane.Malha`, `Arcane.Lavra`"],
   ["arquivos locais, logs, streams", "**nativo** — `Arcane.IO`, `Arcane.Stream`"],
   ["XML, Avro, ORC", "**fora** — formatos de um ecossistema que a linguagem não fala; via ponte quando preciso"],
   ["PostgreSQL, MySQL, Oracle, MongoDB, Redis", "**ponte** — exigem driver de rede próprio, e a promessa aqui é zero dependência"],
   ["FTP, SFTP, Cloud Storage", "**ponte** — mesma razão"]]}},
 {"p": "Do lado da transformação, tudo é nativo: limpeza, deduplicação, normalização, conversão de tipo, tratamento de nulo, enriquecimento por `juntar`, agregação, filtro, ordenação, validação e regra de negócio — ver [ETL](/docs/dados/etl) e [qualidade](/docs/dados/qualidade)."},
 {"callout": {"tipo": "atencao", "titulo": "A parte que mais importa num ETL não é a conexão", "texto": "É a **idempotência**: rodar duas vezes tem de dar o mesmo resultado. `upsert`, `insert_or_ignore` e transação são nativos, e é deles que depende reprocessar um dia que falhou sem duplicar tudo."}},

 {"h2": "5 — Engenharia de dados"},
 {"table": {"head": ["O que se pede", "Onde está"], "rows": [
   ["data pipelines, orquestração, DAG", "**nativo** — `Arcane.Pipeline`: etapa, ordem, retry, incremental, histórico"],
   ["batch e stream processing", "**nativo** — `parallel`, `map_processos`, `Arcane.Stream`"],
   ["validação e qualidade", "**nativo** — `Arcane.Qualidade`"],
   ["linhagem, catálogo, observabilidade", "**nativo** — `Arcane.Observar`: origem, derivar, impacto, árvore, grafo"],
   ["contratos de dados, evolução de esquema", "**parcial** — `Arcane.Lago.esquema` e `Arcane.Qualidade.conferir`; o registro de esquema versionado não existe"],
   ["event-driven pipelines", "**nativo** — `Arcane.Eventos` (em memória); a fila **com persistência** é o item aberto do roadmap"]]}},

 {"h2": "6, 7 e 19 — SQL, Data Warehouse, Data Lake e Lakehouse"},
 {"table": {"head": ["O que se pede", "Onde está"], "rows": [
   ["SELECT, INSERT, UPDATE, DELETE, JOIN, índice", "**nativo** — [`Arcane.Database`](/docs/sqlite)"],
   ["transação, savepoint, upsert, migração", "**nativo**"],
   ["busca textual, `explain`, estatística de tabela", "**nativo** — FTS5, `DB.explain`, `DB.stats`"],
   ["ORM, modelos, relações", "**nativo** — `Arcane.Forge`"],
   ["Parquet, partições, camadas bronze/prata/ouro", "**nativo** — [`Arcane.Lago`](/docs/tecnicas/lago)"],
   ["compactação, vácuo, promoção entre camadas", "**nativo** — `Lago.compactar`, `vacuo`, `promover`"],
   ["modelagem dimensional, SCD, data marts", "**padrão, não módulo** — são formas de modelar, e a linguagem tem o que elas exigem (junção, upsert, versão por data)"],
   ["Snowflake, BigQuery, Redshift", "**fora** — são serviços; o caminho é a API deles por `Arcane.Http`"]]}},

 {"h2": "8 e 9 — Big Data e tempo real"},
 {"table": {"head": ["O que se pede", "Onde está"], "rows": [
   ["processamento paralelo de verdade", "**nativo** — `P.map_processos`, medido **4,71×** em 10 núcleos"],
   ["processamento por partes, streaming de arquivo", "**nativo** — `stream action` + `emit`, `O(1)` de espaço"],
   ["particionamento, poda de partição", "**nativo** — `Arcane.Lago.particoes`"],
   ["filas, tópicos, offset, janelas", "**nativo** — `Arcane.Stream`: topico, publicar, consumir, offset, janela, confirmar"],
   ["Spark, Hadoop, Flink, Kafka", "**fora** — são sistemas distribuídos, não bibliotecas. O que a linguagem oferece é o modelo deles numa máquina"],
   ["dados maiores que a memória", "**parcial** — por partes, sim; o motor distribuído, não"]]}},
 {"callout": {"tipo": "nota", "titulo": "O teto, dito com número", "texto": "Uma VM de bytecode **escrita em Python** tem teto de ~6,5×. Para trabalho pesado de CPU a resposta é `map_processos` (processos de verdade) ou a ponte para o `numpy`, onde a conta acontece fora do interpretador. Isso está medido em [complexidade em paralelo](/docs/big-o/paralelo)."}},

 {"h2": "10 e 25 — Visualização e BI"},
 {"table": {"head": ["O que se pede", "Onde está"], "rows": [
   ["gráfico de barras, linhas, dispersão, histograma", "**nativo** — `Arcane.Analytics` em ASCII, `Arcane.Vitrine` em SVG"],
   ["painel interativo, filtros, abas, métricas", "**nativo** — [Vitrine](/docs/vitrine): 40 componentes, sete gráficos, ~4 KB de cliente"],
   ["mapa de calor, sparkline, box plot", "**nativo** — `Analytics.heatmap`, `sparkline`, `box_plot`"],
   ["relatório e exportação", "**nativo** — `para_csv`, `para_json`, `Arcane.Excel`"],
   ["KPI, drill-down, self-service BI", "**padrão** — a Vitrine tem as peças; o produto é seu"],
   ["Power BI, Tableau, Looker", "**fora** — são produtos"]]}},

 {"h2": "11, 12 e 21 — Data Science, IA e séries temporais"},
 {"table": {"head": ["O que se pede", "Onde está"], "rows": [
   ["regressão linear e logística, árvore, floresta", "**nativo** — `Arcane.Cortex`"],
   ["k-médias, k-vizinhos, PCA, Bayes", "**nativo** — `Cortex.kmedias`, `vizinhos`, `pca`, `bayes_texto`"],
   ["treino, teste, validação cruzada, matriz de confusão", "**nativo** — `dividir`, `validacao_cruzada`, `matriz`"],
   ["escalonamento, categórico, importância de feição", "**nativo** — `escalonar`, `categorico`, `importancia`"],
   ["média móvel, defasagem, sazonalidade, tendência", "**nativo** — `Analytics.moving_average`, `lag`, `seasonality`, `trend`"],
   ["rede neural, aprendizado profundo, LLM", "**ponte** — `adopt Python.torch`. Uma rede neural sem BLAS é um brinquedo, e prometê-la seria mentir"]]}},

 {"h2": "15, 23, 24, 26 e 27 — Qualidade, perfil, limpeza, observabilidade e governança"},
 {"table": {"head": ["O que se pede", "Onde está"], "rows": [
   ["perfil de dados, tipos, distribuição, cardinalidade", "**nativo** — `Quadro.perfil`, `Arcane.Qualidade.perfil`"],
   ["completude, unicidade, validade, atualidade", "**nativo** — `Qualidade.completude`, `unicidade`, `so_validas`, `atualidade`"],
   ["duplicatas, valores fora da faixa, formato", "**nativo** — `duplicadas`, `fora_da_faixa`, `formatos`"],
   ["limpeza: nulo, tipo, texto, data", "**nativo** — `preencher`, `converter`, `Arcane.Text`, `Arcane.Time`"],
   ["linhagem, impacto, catálogo", "**nativo** — `Observar.origem`, `derivar`, `impacto`, `arvore`, `grafo`"],
   ["métricas, alerta, painel, Prometheus", "**nativo** — `Observar.medir`, `alertar`, `painel`, `prometheus`"],
   ["contrato de dados, política, auditoria", "**parcial** — `Qualidade.conferir` e `esperar` dão o contrato; a política e a auditoria são processo, não biblioteca"],
   ["mascaramento, anonimização, LGPD", "**parcial** — `Arcane.Crypto` tem o hash e a cifra; a classificação de dado pessoal é decisão de quem modela"]]}},

 {"h2": "28 e 29 — Testes e desempenho"},
 {"table": {"head": ["O que se pede", "Onde está"], "rows": [
   ["teste unitário, de integração, de dados", "**nativo** — [Crucible](/docs/testes), com banco isolado por teste"],
   ["instantâneo de saída grande", "**nativo** — `expect … matches snapshot`"],
   ["teste por propriedade", "**nativo** — `Crucible`"],
   ["análise de complexidade antes de rodar", "**nativo** — `dataforge big-o`, único entre linguagens"],
   ["lazy evaluation, processamento por partes", "**nativo** — `stream action` + `emit`"],
   ["cache, memoização", "**nativo** — `Arcane.Functional.memoize`, `Vitrine.cache`"],
   ["armazenamento colunar", "**nativo** — o `Quadro` é colunar por dentro; o Parquet, no `Lago`"],
   ["predicate pushdown, otimização de consulta", "**parcial** — o SQLite otimiza a consulta; o `Quadro` não reordena o pipeline"]]}},

 {"h2": "30 — A sintaxe que o documento esboçou"},
 {"p": "O esboço propunha um operador `|>` e blocos `pipeline { }`. A linguagem já tinha o `>>`, e o que faltava era o **vocabulário** — não um segundo operador:"},
 {"code": """// o esboço                          // em DataForge
// dados |> filtrar(idade > 18)       >> onde idade bigger 18
// |> agrupar.por("cidade")           >> agrupar cidade
// |> agregar.media("salario")        >> resumir {"salario": "media"}
// |> ordenar.desc("valor")           >> ordenar valor desc
""", "lang": "df"},
 {"code": """resumo := vendas
    >> onde valor bigger 50
    >> agrupar produto
    >> resumir {"valor": "soma"}
    >> ordenar valor desc
""", "lang": "df"},
 {"p": "Inventar `|>` ao lado de `>>` daria dois operadores para a mesma ideia — e a primeira pergunta de quem chega seria qual usar. Os [seis verbos](/docs/dados/verbos) são **contextuais**, como as onze palavras do Kiln: valem depois de um `>>` e continuam livres como nome em todo o resto."},

 {"h2": "31 — Os módulos propostos, e onde eles foram parar"},
 {"table": {"head": ["Proposto", "Onde está"], "rows": [
   ["`DataFrame`", "**`Arcane.Quadro`**"],
   ["`Data`, `Statistics`", "`Arcane.Analytics`, `Arcane.Data`"],
   ["`ETL`, `ELT`, `Pipelines`", "`Arcane.Pipeline` + os verbos do quadro"],
   ["`SQL`, `Warehouse`", "`Arcane.Database`, `Arcane.Forge`"],
   ["`Lake`, `Lakehouse`", "`Arcane.Lago`"],
   ["`Streaming`, `BigData`", "`Arcane.Stream`, `Arcane.Concurrent`"],
   ["`Visualization`, `BI`", "`Arcane.Vitrine`, `Arcane.Analytics`"],
   ["`MachineLearning`, `AI`", "`Arcane.Cortex` + a ponte"],
   ["`Quality`, `Governance`, `Observability`", "`Arcane.Qualidade`, `Arcane.Observar`"],
   ["`TimeSeries`", "`Arcane.Analytics` + `Arcane.Time`"],
   ["`Cloud`", "**fora** — serviços, alcançáveis por `Arcane.Http`"]]}},
 {"p": "Vinte e um módulos propostos couberam em doze que já existiam mais um novo. Criar um módulo por tópico daria vinte e uma portas para o que é um assunto só — e a regra aqui é que a tabela de módulos não divirja da realidade."},

 {"h2": "O que este mapa recusa a prometer"},
 {"list": [
   "**Driver de banco em rede** — PostgreSQL, MySQL, Oracle, MongoDB, Redis. Cada um é um protocolo de rede, e a promessa da linguagem é zero dependência no runtime.",
   "**Motor distribuído** — Spark, Flink, Hadoop. São sistemas, não bibliotecas; reimplementá-los em Python daria um subconjunto pior amarrado à linguagem.",
   "**Aprendizado profundo** — uma rede neural sem BLAS é um brinquedo. A ponte para o `torch` é honesta; uma implementação própria não seria.",
   "**Conectores de nuvem** — S3, GCS, Azure. São APIs HTTP, e `Arcane.Http` fala com elas; um cliente oficial de cada uma é manutenção sem fim.",
   "**Avro e ORC** — formatos de um ecossistema que a linguagem não fala. Parquet existe porque ele é a fronteira que um lago de dados realmente usa."]},
 {"callout": {"tipo": "dica", "titulo": "Como este mapa não envelhece", "texto": "As linhas marcadas **nativo** citam símbolos, e símbolo que sai da biblioteca quebra `tests/test_estabilidade.py`. As linhas **fora** citam o motivo, e não a falta — é o motivo que envelhece devagar."}},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/dados/quadro", "title": "O Quadro", "desc": "a tabela, verbo por verbo"},
   {"href": "/docs/dados/verbos", "title": "Os verbos do pipeline", "desc": "a sintaxe nativa"},
   {"href": "/docs/dados", "title": "Análise de dados", "desc": "o caminho de um conjunto até a resposta"},
   {"href": "/docs/dados/etl", "title": "ETL", "desc": "idempotência, falha parcial e reprocessamento"}]},
]},
]
