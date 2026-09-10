# -*- coding: utf-8 -*-
"""Parquet e Data Lake."""

PAGINAS = [
{
"href": "/docs/tecnicas/parquet",
"title": "Parquet",
"description": "O formato colunar, escrito e lido em DataForge — sem pyarrow, e interoperável com ele.",
"blocos": [
 {"p": "**Parquet** é o formato em que os dados de verdade vivem. `Arcane.Lago` o escreve e o lê em Python puro: um arquivo gerado aqui é lido pelo pandas, pelo DuckDB e pelo Spark, e um arquivo gerado por eles é lido aqui."},
 {"code": """adopt Arcane.Lago as L

L.gravar_parquet("vendas.parquet", linhas)
L.ler_parquet("vendas.parquet")
L.ler_parquet("vendas.parquet", ["id", "valor"])   // só duas colunas
L.esquema_parquet("vendas.parquet")                // sem ler os dados""", "lang": "df"},

 {"h2": "Por que colunar"},
 {"p": "Um CSV guarda linha a linha. Para somar uma coluna de 40 milhões de linhas, o disco entrega as outras trinta junto — e elas são jogadas fora. O Parquet guarda **coluna a coluna**: ler uma coluna lê só ela."},
 {"code": """// 50.000 linhas, 4 colunas
L.ler_parquet("grande.parquet")            // 0,05 s
L.ler_parquet("grande.parquet", ["id"])    // 0,02 s — 2,9× mais rápido""", "lang": "df"},
 {"p": "E valores do mesmo tipo, lado a lado, comprimem muito melhor. Uma coluna de datas repetidas ou de categorias encolhe uma ordem de grandeza; a mesma informação espalhada por linhas, não."},

 {"h2": "O formato, por dentro"},
 {"code": """PAR1                       ← marca de abertura
[dados da coluna 1]        ← páginas, uma por bloco de valores
[dados da coluna 2]
…
[metadados em Thrift]      ← esquema, onde cada coluna começa
<4 bytes: tamanho deles>
PAR1                       ← marca de fechamento""", "lang": "text"},
 {"p": "Os metadados ficam no **fim**, e não no começo. É o que permite escrever um arquivo sem saber de antemão quantas linhas ele terá — e é por isso que o leitor busca o fim primeiro."},
 {"callout": {"tipo": "nota", "titulo": "Thrift compact, escrito à mão", "texto": "Os metadados usam o protocolo Thrift compact: inteiros em zigzag varint, campos por delta de id, estruturas aninhadas. Não há biblioteca — é a parte que mais parece arbitrária e a que menos pode errar por um byte. Um deslocamento de um único byte no rodapé faz o pyarrow recusar o arquivo inteiro sem dizer onde."}},

 {"h2": "Tipos"},
 {"table": {"head": ["DataForge", "Parquet", "Lido como"], "rows": [
   ["`Integer`", "INT64", "`int64`"],
   ["`Number`", "DOUBLE", "`double`"],
   ["`String`", "BYTE_ARRAY (UTF8)", "`string`"],
   ["`Boolean`", "BOOLEAN", "`bool`"],
   ["`void`", "nível de definição", "`null`"]]}},
 {"p": "O tipo sai dos **valores**, e um inteiro grande demais para 64 bits sobe para `DOUBLE`. Misturar tipos numa coluna é o que mais quebra na leitura — o Parquet é tipado, e o CSV que o originou não era."},

 {"h2": "Nulos custam quando existem"},
 {"p": "Uma coluna sem nulo nenhum é declarada **REQUIRED**, e não carrega níveis de definição. A que tem nulo é **OPTIONAL**, e paga por isso. Declarar tudo como opcional custaria os níveis à toa em toda coluna."},

 {"h2": "Dicionário"},
 {"p": "A maioria dos Parquet do mundo é escrita com codificação por **dicionário**: a página guarda índices, e os valores distintos ficam numa página à parte. Uma coluna de cinco categorias vira 3 bits por linha."},
 {"p": "Nós escrevemos PLAIN e lemos os dois — ler só PLAIN leria quase nada do que existe por aí."},

 {"h2": "O que ainda não lemos"},
 {"table": {"head": ["Compressão", "Estado"], "rows": [
   ["sem compressão", "**lê e escreve**"],
   ["gzip", "**lê e escreve** (o padrão)"],
   ["snappy, zstd, brotli, lz4", "recusado, com o nome da compressão na mensagem"]]}},
 {"p": "Gzip está na biblioteca padrão do Python; as outras exigiriam dependência, e a linguagem não tem nenhuma. Quando o arquivo vem comprimido de outro jeito, a mensagem diz qual e como regravar."},
]},

{
"href": "/docs/tecnicas/lago",
"title": "Data Lake",
"description": "Partições Hive, camadas bronze/prata/ouro e compactação — em disco, sem servidor.",
"blocos": [
 {"code": """adopt Arcane.Lago as L

lago := L.lago("dados/")

L.gravar(lago, "vendas", linhas, ["ano", "mes"])
L.ler(lago, "vendas", {"ano": 2026})""", "lang": "df"},

 {"h2": "O caminho carrega o filtro"},
 {"code": """dados/vendas/ano=2026/mes=03/parte-20260910-084726-0000.parquet""", "lang": "text"},
 {"p": "Uma consulta por `ano=2026` não abre um arquivo sequer de 2025 — ela nem os lista. Com dois anos de dados isso é conveniência; com dez, é a diferença entre segundos e minutos."},
 {"callout": {"tipo": "dica", "titulo": "É o layout do Hive", "texto": "`chave=valor` na pasta não é invenção nossa: é o que Spark, DuckDB e pandas já sabem ler. Um lago escrito aqui é lido por eles sem conversão — `pd.read_parquet(\"dados/vendas\")` traz as partições como colunas."}},
 {"p": "O campo de partição **sai** das linhas antes de gravar: ele já está no caminho, e guardá-lo duas vezes é desperdício. Na leitura ele volta, vindo da pasta."},

 {"h2": "Gravar sempre acrescenta"},
 {"p": "Cada gravação cria um arquivo com instante e contador no nome. Sobrescrever exigiria saber que a gravação anterior terminou, e num lago ninguém garante isso — quem quer trocar um período remove a partição antes:"},
 {"code": """L.remover_particao(lago, "vendas", {"ano": 2026, "mes": 3})
L.gravar(lago, "vendas", linhas_de_marco, ["ano", "mes"])""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Sem filtro, ele recusa", "texto": "`remover_particao` sem filtro apagaria a tabela inteira. Ele levanta em vez de fazer — apagar dado por engano não tem desfazer."}},

 {"h2": "Compactar"},
 {"p": "Um lago que recebe carga de hora em hora acumula 24 arquivos por dia por partição. Ler mil arquivos de 4 KB é muito mais lento que ler um de 4 MB — **o custo está em abrir, não em ler**."},
 {"code": """L.compactar(lago, "vendas")
// {"particoes_compactadas": 12, "arquivos_removidos": 276}""", "lang": "df"},
 {"p": "Ele grava o arquivo novo **inteiro** antes de apagar os antigos. Apagar primeiro e falhar no meio perderia os dados."},

 {"h2": "As três camadas"},
 {"table": {"head": ["Camada", "O que guarda"], "rows": [
   ["**bronze**", "o dado como chegou, sem tocar"],
   ["**prata**", "limpo, tipado, sem duplicata"],
   ["**ouro**", "agregado, pronto para consumo"]]}},
 {"code": """action limpar(linhas):
    yield Q.so_validas(Q.sem_duplicadas(linhas, ["id"]), REGRAS)

L.gravar(L.camada(lago, "bronze"), "vendas", bruto, ["ano"])
L.promover(lago, "vendas", "bronze", "prata", limpar, ["ano"])
L.promover(lago, "vendas", "prata", "ouro", agregar, ["ano"])""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Bronze existe para poder reprocessar", "texto": "Quando a regra de limpeza estava errada — e vai estar — sem o bruto guardado a única saída é pedir os dados de novo à origem, que nem sempre os tem. `promover` **nunca** altera a camada de origem."}},

 {"h2": "Inspecionar"},
 {"code": """L.tabelas(lago)                    // as tabelas que existem
L.particoes(lago, "vendas")        // as partições de uma delas
L.arquivos(lago, "vendas", {"ano": 2026})
L.esquema(lago, "vendas")          // colunas, tipos, e quais são de partição
L.tamanho(lago)                    // bytes e arquivos, legível
L.eventos(lago)                    // o que aconteceu com o lago
L.vacuo(lago)                      // tira pasta vazia e gravação interrompida""", "lang": "df"},

 {"h2": "O que este módulo não é"},
 {"p": "Não é Delta Lake nem Iceberg. **Não há transação ACID entre escritores concorrentes**, nem viagem no tempo por versão, nem evolução de esquema automática."},
 {"p": "Dois processos gravando na mesma partição ao mesmo tempo é o caso que ele não protege. Cada gravação cria um arquivo com nome próprio, então eles não se sobrescrevem — mas nada garante que os dois apareçam juntos para quem lê no meio."},
 {"callout": {"tipo": "atencao", "titulo": "O valor da partição vem do dado", "texto": "E dado vem de fora. Um campo com `../..` escreveria fora do lago — é o mesmo Zip Slip, por outra porta. Todo valor é higienizado antes de virar pasta, e há teste conferindo que nada escapa da raiz."}},
]},
]
