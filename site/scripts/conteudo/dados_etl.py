# -*- coding: utf-8 -*-
"""Análise de dados, ETL e SQLite."""

PAGINAS = [
{
"href": "/docs/dados",
"title": "Análise de dados",
"description": "Carregar, limpar, agregar e descrever — o caminho de um conjunto de dados até a resposta.",
"blocos": [
 {"p": "Analisar dados é sempre a mesma sequência: **carregar**, **conferir**, **limpar**, **agregar**, **responder**. A linguagem traz as cinco etapas, e esta página é o caminho inteiro com um conjunto pequeno o bastante para caber na tela."},

 {"h2": "O quadro de dados"},
 {"p": "`Arcane.Analytics` trabalha com um **frame**: um cluster de vaults, que é o que `IO.read_csv(caminho, yes)` devolve e o que `Database.query` devolve."},
 {"code": """adopt Arcane.Analytics as An

vendas := [
    {"produto": "cafe",   "regiao": "sul",   "valor": 120.0, "qtd": 4},
    {"produto": "cafe",   "regiao": "norte", "valor": 90.0,  "qtd": 3},
    {"produto": "cha",    "regiao": "sul",   "valor": 60.0,  "qtd": 2},
    {"produto": "cha",    "regiao": "norte", "valor": 45.0,  "qtd": 1},
    {"produto": "acucar", "regiao": "sul",   "valor": 30.0,  "qtd": 5}
]

out len(vendas), "registros"
""", "lang": "df"},

 {"h2": "1. Conferir antes de confiar"},
 {"p": "A primeira coisa a fazer com um conjunto novo não é calcular — é **olhar**. Quantas linhas, quais colunas, o que está faltando:"},
 {"code": """adopt Arcane.Analytics as An

action colunas_de(dados):
    yield keys(dados[0])

action faltando(dados, coluna):
    yield len([l cycle l in dados given (l[coluna] ?? void) is void])

out colunas_de(vendas)
out faltando(vendas, "valor"), "sem valor"
""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "A média que mente", "texto": "Uma média calculada sobre dados com buraco não avisa que tinha buraco — ela só sai menor. Conferir a contagem de ausentes **antes** de agregar é o passo que separa um relatório de um chute."}},

 {"h2": "2. Limpar"},
 {"code": """action limpo(dados):
    yield [linha cycle linha in dados
           given (linha["valor"] ?? 0.0) > 0.0]

action com_total(dados):
    yield [linha with {"total": linha["valor"] * linha["qtd"]}
           cycle linha in dados]
""", "lang": "df"},
 {"p": "Note que nada é mutado: cada etapa devolve um frame **novo**. É o que permite comparar o antes e o depois, e é o que faz um pipeline ser reexecutável."},

 {"h2": "3. Agregar"},
 {"code": """action somar_por(dados, chave, campo):
    totais := {}
    cycle linha in dados:
        grupo := linha[chave]
        totais[grupo] := (totais[grupo] ?? 0.0) + linha[campo]
    yield totais

out somar_por(vendas, "produto", "valor")
out somar_por(vendas, "regiao", "valor")
""", "lang": "df"},
 {"code": """{cafe: 210.0, cha: 105.0, acucar: 30.0}
{sul: 210.0, norte: 135.0}
""", "lang": "text", "title": "saída"},
 {"p": "O vault como acumulador é `O(n)`: uma passada, e cada escrita é constante. A versão \"óbvia\" — para cada grupo, percorrer tudo filtrando — é `O(n × grupos)`, e o [`dataforge big-o`](/docs/big-o/padroes) acusa."},

 {"h2": "4. Descrever"},
 {"code": """adopt Arcane.Analytics as An

valores := [v["valor"] cycle v in vendas]

out An.media(valores)
out An.mediana(valores)
out An.desvio_padrao(valores)
out min(valores), max(valores)
""", "lang": "df"},
 {"p": "**Média e mediana juntas dizem mais que qualquer uma sozinha.** Quando as duas se afastam, há assimetria — um valor muito alto puxando a média —, e é o sinal de que a média não representa o conjunto."},

 {"h2": "5. Responder, e mostrar"},
 {"p": "O resultado de uma análise termina de três formas, e cada uma tem o seu lugar:"},
 {"table": {"head": ["Onde termina", "Com o quê"], "rows": [
   ["no terminal", "`out`, ou o pacote [`tabela`](/docs/pacotes/tabela)"],
   ["num arquivo", "`IO.write_csv`, `IO.write_json`, [`Arcane.Excel`](/docs/tecnicas/planilhas)"],
   ["numa página", "[Vitrine](/docs/vitrine) — o mesmo `.df` vira painel com gráfico"]]}},

 {"h2": "Quando os dados não cabem na memória"},
 {"p": "A regra prática: até alguns milhões de linhas, um cluster de vaults resolve. Acima disso, há três caminhos, e o primeiro costuma bastar:"},
 {"list": [
   "**Processar por partes**, com `stream action` — `O(1)` de espaço, ver [complexidade de espaço](/docs/big-o/espaco).",
   "**Deixar o banco agregar** — `SUM` e `GROUP BY` acontecem onde o dado já está, e volta só o resultado. Ver [SQLite](/docs/sqlite).",
   "**A ponte para o Python** — `adopt Python.pandas as pd` quando a conta é vetorizada e o volume justifica."]},
 {"code": """adopt Python.numpy as np

a := np.array([1.0, 2.0, 3.0])
out (a * 2).tolist()        // a conta é do numpy, sem cópia na fronteira
""", "lang": "df"},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/dados/etl", "title": "ETL", "desc": "extrair, transformar e carregar — com o que fazer quando falha"},
   {"href": "/docs/dados/qualidade", "title": "Qualidade de dados", "desc": "as regras que impedem o relatório errado"},
   {"href": "/docs/biblioteca/analytics", "title": "Arcane.Analytics", "desc": "a referência do módulo"},
   {"href": "/docs/vitrine", "title": "Vitrine", "desc": "o resultado como página"}]},
]},

{
"href": "/docs/dados/etl",
"title": "ETL: extrair, transformar, carregar",
"description": "O formato de um pipeline que roda todo dia — idempotência, falha parcial, reprocessamento e linhagem.",
"blocos": [
 {"p": "Um ETL é um programa que roda **de novo**, todo dia, sobre dados que mudam. Isso é tudo o que o distingue de um script de análise, e é o que cria os problemas dele: o que acontece quando roda duas vezes? E quando falha no meio?"},

 {"h2": "As três etapas, separadas de propósito"},
 {"code": """adopt Arcane.IO as IO

// EXTRAIR — só lê. Nenhuma regra de negócio aqui.
action extrair(caminho):
    yield IO.read_csv(caminho, yes)

// TRANSFORMAR — só calcula. Nada de arquivo, nada de banco.
action transformar(linhas):
    limpas := [l cycle l in linhas given (l["valor"] ?? "") isnt ""]
    yield [l with {"valor": float(l["valor"])} cycle l in limpas]

// CARREGAR — só escreve.
action carregar(linhas, destino):
    IO.write_csv(destino, linhas)
    yield len(linhas)
""", "lang": "df"},
 {"p": "A separação não é estética. `transformar` **não toca em disco**, e por isso ela é a única das três que se testa sem preparar ambiente — e é onde mora toda a regra que pode estar errada."},

 {"h2": "Rodar duas vezes tem de dar o mesmo resultado"},
 {"p": "É a propriedade que mais falta num ETL: **idempotência**. Sem ela, reprocessar um dia que falhou duplica tudo o que já tinha entrado."},
 {"table": {"head": ["Forma de carregar", "Rodar duas vezes"], "rows": [
   ["`insert`", "**duplica**"],
   ["`insert_or_ignore`", "ignora o repetido — seguro"],
   ["`upsert` por chave", "atualiza — seguro, e corrige o que mudou"],
   ["apagar a partição e reinserir", "seguro, e o mais simples de entender"]]}},
 {"code": """adopt Arcane.Database as DB

action carregar(db, linhas, dia):
    DB.transacao(db, lambda:
        [DB.upsert(db, "vendas", l, ["id"]) cycle l in linhas])
    yield len(linhas)
""", "lang": "df"},
 {"p": "A transação é o que torna \"carregou tudo\" e \"não carregou nada\" as duas únicas saídas possíveis. Sem ela, uma falha no meio deixa metade dentro — e a segunda execução não tem como saber qual metade."},

 {"h2": "Falhar bem"},
 {"p": "Um ETL que quebra às três da manhã precisa dizer **onde** parou e **o que** já tinha feito:"},
 {"code": """adopt Arcane.Logging as Log

action rodar(caminho, destino):
    Log.info($"etl: comecando {caminho}")
    monitor:
        brutas := extrair(caminho)
        Log.info($"etl: {len(brutas)} linhas lidas")

        limpas := transformar(brutas)
        Log.info($"etl: {len(limpas)} linhas apos limpeza")

        gravadas := carregar(limpas, destino)
        Log.info($"etl: {gravadas} gravadas em {destino}")
        yield gravadas
    handle Error as e:
        Log.erro($"etl falhou em {caminho}: {e.message}")
        trigger $"o ETL de {caminho} nao terminou"
""", "lang": "df"},
 {"p": "O `trigger` de fora preserva o erro original em `.causa` — o relatório mostra as duas camadas, e quem lê o log de manhã vê tanto o que o pipeline tentava fazer quanto o que o impediu."},

 {"h2": "A linha que não entra"},
 {"p": "Descartar silenciosamente uma linha ruim é a forma mais comum de um relatório ficar errado sem ninguém notar. Separe, conte e **guarde**:"},
 {"code": """action separar(linhas):
    boas := []
    ruins := []
    cycle l in linhas:
        given (l["valor"] ?? "") is "":
            ruins.append(l with {"motivo": "valor vazio"})
        otherwise:
            boas.append(l)
    yield {"boas": boas, "ruins": ruins}

resultado := separar(brutas)
given len(resultado["ruins"]) > 0:
    IO.write_csv("rejeitadas.csv", resultado["ruins"])
    out $"atencao: {len(resultado['ruins'])} linha(s) rejeitadas"
""", "lang": "df"},
 {"p": "O arquivo de rejeitadas é o que transforma \"os números não batem\" numa investigação de cinco minutos."},

 {"h2": "Ordem, dependência e paralelismo"},
 {"p": "Quando um pipeline tem etapas independentes, elas não precisam esperar umas às outras. Mas o ganho depende de onde está o custo:"},
 {"table": {"head": ["O gargalo é", "Use", "Ganho"], "rows": [
   ["**rede ou disco** (baixar, consultar API)", "`parallel:` ou `async`", "real — o GIL é solto na espera"],
   ["**CPU** (transformar milhões de linhas)", "`P.map_processos`", "real — medido 4,71× em 10 núcleos"],
   ["**o banco**", "nenhum dos dois", "agregue **no** banco em vez de trazer"]]}},
 {"code": """adopt Arcane.Concurrent as P

// as três fontes são independentes: baixam juntas
parallel:
    vendas := baixar("vendas")
    clientes := baixar("clientes")
    produtos := baixar("produtos")

// a transformação é CPU: processos de verdade
limpas := P.map_processos(transformar_lote, em_lotes(vendas, 10000))
""", "lang": "df"},

 {"h2": "Agendar"},
 {"p": "O pipeline em si não deveria saber a que horas roda. Quem agenda é de fora — `cron`, um orquestrador, ou `Arcane.Concurrent.repetir_a_cada` num processo que fica de pé:"},
 {"code": """dataforge run etl/diario.df --data=2026-09-16
""", "lang": "bash"},
 {"p": "Receber a data como **argumento** é o que torna o reprocessamento possível: rodar o dia 3 de novo é trocar um número, e não mexer no código."},

 {"h2": "A lista de conferência de um ETL"},
 {"list": [
   "Rodar duas vezes dá o mesmo resultado?",
   "A carga está dentro de uma transação?",
   "As linhas rejeitadas são contadas **e** gravadas?",
   "O log diz quantas linhas entraram em cada etapa?",
   "A data é argumento, e não `hoje()` no meio do código?",
   "A transformação é testável sem disco e sem banco?"]},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/dados/qualidade", "title": "Qualidade de dados", "desc": "as regras que rodam junto do pipeline"},
   {"href": "/docs/tecnicas/pipeline", "title": "Pipelines e orquestração", "desc": "o módulo Arcane.Pipeline"},
   {"href": "/docs/tecnicas/lago", "title": "Data Lake", "desc": "quando o volume passa do arquivo"},
   {"href": "/docs/big-o/dados", "title": "Custo em dados", "desc": "N+1, índice e paginação"}]},
]},

{
"href": "/docs/dados/qualidade",
"title": "Qualidade de dados",
"description": "As regras que impedem o relatório errado — e por que elas rodam junto do pipeline, não depois.",
"blocos": [
 {"p": "Um pipeline que termina sem erro **não** prova que os dados estão certos. Ele prova que nada estourou — e a diferença entre as duas coisas é onde vive o relatório errado que ninguém contesta."},

 {"h2": "As seis perguntas"},
 {"table": {"head": ["Dimensão", "A pergunta", "Como se mede"], "rows": [
   ["**completude**", "falta alguma coisa?", "quantos vazios por coluna"],
   ["**unicidade**", "há repetido?", "contagem de chaves distintas × total"],
   ["**validade**", "o valor faz sentido?", "faixa, formato, lista de valores aceitos"],
   ["**consistência**", "as partes concordam?", "o total bate com a soma das partes?"],
   ["**pontualidade**", "o dado é de hoje?", "a data mais recente × agora"],
   ["**volume**", "veio a quantidade esperada?", "linhas de hoje × a média dos últimos dias"]]}},
 {"callout": {"tipo": "dica", "titulo": "A última é a que mais pega", "texto": "Um arquivo que chegou com 3 linhas quando sempre tem 30 mil passa por todas as outras verificações — cada uma das 3 linhas está perfeita. Comparar o **volume** com o histórico é a regra mais barata e a que mais evita relatório errado."}},

 {"h2": "Escrever uma regra"},
 {"code": """record Regra:
    nome: String
    grave: Boolean := yes

action conferir(dados, regra, teste):
    falhas := [l cycle l in dados given not teste(l)]
    yield {"regra": regra.nome,
           "grave": regra.grave,
           "falhas": len(falhas),
           "total": len(dados),
           "exemplos": falhas[0:3]}
""", "lang": "df"},
 {"code": """resultados := [
    conferir(vendas, Regra("valor positivo"), lambda l: l["valor"] > 0.0),
    conferir(vendas, Regra("regiao conhecida"),
             lambda l: l["regiao"] in ["sul", "norte"]),
    conferir(vendas, Regra("qtd inteira", no), lambda l: l["qtd"] >= 1)
]

cycle r in resultados:
    marca := "x" given r["falhas"] > 0 otherwise " "
    out $"[{marca}] {r['regra']}: {r['falhas']} de {r['total']}"
""", "lang": "df"},

 {"h2": "Grave interrompe; aviso não"},
 {"p": "Toda regra precisa de uma resposta declarada para \"e se falhar?\". Sem isso, ou o pipeline para por qualquer coisa, ou nunca para por nada:"},
 {"code": """action decidir(resultados):
    graves := [r cycle r in resultados
               given r["grave"] and r["falhas"] > 0]
    given len(graves) > 0:
        trigger $"{len(graves)} regra(s) grave(s) falharam; o carregamento nao aconteceu"

    avisos := [r cycle r in resultados given r["falhas"] > 0]
    cycle a in avisos:
        out $"aviso: {a['regra']} — {a['falhas']} linha(s)"
    yield yes
""", "lang": "df"},
 {"table": {"head": ["Gravidade", "O que fazer"], "rows": [
   ["**grave**", "não carregar. Um dado errado publicado é pior que um relatório atrasado"],
   ["**aviso**", "carregar, registrar, e olhar amanhã"],
   ["**informativo**", "só o número, para acompanhar a tendência"]]}},

 {"h2": "Onde as regras rodam"},
 {"p": "**Junto do pipeline, entre transformar e carregar** — não num relatório separado que alguém abre na sexta."},
 {"code": """action rodar(caminho, db):
    brutas := extrair(caminho)
    limpas := transformar(brutas)

    resultados := conferir_tudo(limpas)
    decidir(resultados)               // para aqui se houver grave

    yield carregar(db, limpas)
""", "lang": "df"},
 {"p": "A razão é simples: a única hora em que alguém consegue agir sobre um dado ruim é **antes** de ele virar a fonte de um painel."},

 {"h2": "Guardar o resultado das regras"},
 {"p": "Gravar a saída das verificações a cada execução transforma \"os números pareciam estranhos\" em uma série temporal:"},
 {"code": """IO.write_json($"qualidade/{data}.json", {
    "data": data,
    "linhas": len(limpas),
    "regras": resultados
})
""", "lang": "df"},
 {"p": "Com um histórico, a regra de **volume** deixa de precisar de número mágico: ela compara com a média dos últimos dias."},

 {"h2": "Testar as regras"},
 {"p": "Uma regra de qualidade é código, e código sem teste dá falso negativo em silêncio — a regra que nunca acusa nada parece estar tudo bem:"},
 {"code": """adopt Arcane.Crucible as C

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
""", "lang": "df"},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/tecnicas/qualidade", "title": "Arcane.Qualidade", "desc": "o módulo com as regras prontas"},
   {"href": "/docs/tecnicas/observar", "title": "Observabilidade e linhagem", "desc": "de onde veio cada número"},
   {"href": "/docs/crucible", "title": "Crucible", "desc": "testar as regras"}]},
]},

{
"href": "/docs/sqlite",
"title": "SQLite",
"description": "O banco que vem junto: tabelas, transações, índices, busca textual e migrações — sem instalar nada.",
"blocos": [
 {"p": "SQLite é um banco **dentro do processo**: um arquivo, sem servidor, sem porta, sem senha. Ele vem com o Python e portanto com a DataForge — `adopt Arcane.Database` e já existe banco."},
 {"p": "É a escolha certa para muito mais coisa do que costuma parecer: ferramenta de linha de comando, aplicação de uma máquina, cache local, teste automatizado, e sites de leitura pesada com escrita moderada."},

 {"h2": "Abrir, criar, inserir, consultar"},
 {"code": """adopt Arcane.Database as DB

db := DB.memory()                   // some ao fim do programa
// db := DB.connect("dados.db")     // um arquivo

DB.create_table(db, "pedidos", {
    "id": "INTEGER PRIMARY KEY",
    "cliente": "TEXT",
    "total": "REAL"
})

DB.insert(db, "pedidos", {"cliente": "Ana", "total": 99.9})
DB.insert_many(db, "pedidos", [
    {"cliente": "Bruno", "total": 45.0},
    {"cliente": "Carla", "total": 12.5}
])

out DB.count(db, "pedidos")
out DB.query(db, "SELECT cliente, total FROM pedidos ORDER BY total DESC", [])
DB.close(db)
""", "lang": "df"},
 {"p": "A consulta devolve um **cluster de vaults** — a mesma forma que o resto da linguagem usa, e a mesma que a [análise de dados](/docs/dados) espera."},

 {"h2": "Parâmetro, sempre"},
 {"code": """// NÃO: um nome com aspas quebra a consulta, e um nome malicioso a reescreve
DB.query(db, $"SELECT * FROM pedidos WHERE cliente = '{nome}'", [])

// SIM: o valor vai por fora do SQL
DB.query(db, "SELECT * FROM pedidos WHERE cliente = ?", [nome])
""", "lang": "df"},
 {"callout": {"tipo": "perigo", "titulo": "O nome da coluna é a exceção", "texto": "O SQLite não aceita **nome de coluna** por parâmetro, então ele vai cru para o SQL. É por isso que `order_by` e amigos passam por uma validação que recusa o que não parece um identificador — e isso importa porque um `?ordenar=` de uma listagem chega de fora."}},

 {"h2": "Transação: tudo ou nada"},
 {"code": """DB.transacao(db, lambda:
    [DB.insert(db, "itens", i) cycle i in itens])
""", "lang": "df"},
 {"p": "Sem transação, cada escrita confirma sozinha — e uma falha no meio deixa metade dentro. Com ela, as duas únicas saídas são \"tudo\" e \"nada\"."},
 {"p": "**E a transação também é desempenho.** Mil `insert` soltos são mil confirmações em disco; dentro de uma transação, é uma — a diferença costuma ser de duas ordens de grandeza."},

 {"h2": "Índice: de varrer para buscar"},
 {"code": """DB.create_index(db, "pedidos", ["cliente"])
out DB.explain(db, "SELECT * FROM pedidos WHERE cliente = ?", ["Ana"])
""", "lang": "df"},
 {"code": """{passos: [SEARCH pedidos USING INDEX idx_pedidos_cliente (cliente=?)],
 varre_tabela: no, aviso: }
""", "lang": "text"},
 {"p": "Antes do índice, o mesmo `explain` responde `varre_tabela: yes`. Medido com 20 mil linhas e 200 consultas: **73,6 ms → 4,4 ms**, 16,6×. Ver [complexidade em dados](/docs/big-o/dados)."},

 {"h2": "Busca textual"},
 {"code": """DB.create_search(db, "pedidos", ["cliente"])
out DB.search(db, "pedidos", "ana")
""", "lang": "df"},
 {"p": "Duas armadilhas que a implementação já pagou, as duas silenciosas: o `*` de prefixo vai **fora** das aspas (`\"livr\"*`, e não `\"livr*\"`), e o nome da tabela junto de um apelido devolvia vazio — as duas devolviam lista vazia sem erro."},

 {"h2": "Migrações"},
 {"code": """DB.migrate(db, [
    {"nome": "001_pedidos",
     "up": "CREATE TABLE pedidos (id INTEGER PRIMARY KEY, cliente TEXT)",
     "down": "DROP TABLE pedidos"},
    {"nome": "002_total",
     "up": "ALTER TABLE pedidos ADD COLUMN total REAL DEFAULT 0",
     "down": "ALTER TABLE pedidos DROP COLUMN total"}
])

out DB.migrations_applied(db)
""", "lang": "df"},
 {"p": "O `down` não é opcional por preguiça: sem ele, desfazer exige editar o banco à mão — e a hora de precisar disso é sempre a pior possível."},

 {"h2": "Concorrência: o que o SQLite faz e o que não faz"},
 {"table": {"head": ["", "SQLite"], "rows": [
   ["muitos leitores ao mesmo tempo", "sim"],
   ["um escritor por vez", "sim — o banco inteiro trava na escrita"],
   ["muitos escritores ao mesmo tempo", "**não**"],
   ["acesso pela rede", "**não** — é um arquivo local"]]}},
 {"p": "O `Arcane.Database` serializa o acesso à conexão: sem isso, a primeira consulta de qualquer servidor estoura, porque a conexão do SQLite não atravessa thread. Num Kiln com carga de escrita alta, essa serialização vira o gargalo — e é o momento de trocar por um banco cliente-servidor."},

 {"h2": "Quando trocar de banco"},
 {"list": [
   "**Vários processos escrevendo** — não é o caso de uso do SQLite.",
   "**Acesso pela rede** — ele não tem; um arquivo em disco compartilhado corrompe.",
   "**Escrita concorrente alta** — o travamento no nível do banco passa a doer.",
   "**Dados maiores que o disco de uma máquina** — a resposta aí não é banco, é [lago](/docs/tecnicas/lago)."]},
 {"p": "Fora esses quatro casos, trocar SQLite por um servidor costuma acrescentar operação sem acrescentar capacidade."},

 {"h2": "Testar com banco"},
 {"code": """adopt Arcane.Crucible as C
adopt Arcane.Database as DB

crucible "pedidos":
    trial "insere e conta":
        db := DB.memory()
        DB.create_table(db, "p", {"id": "INTEGER PRIMARY KEY", "v": "REAL"})
        DB.insert(db, "p", {"v": 1.0})
        expect DB.count(db, "p") is 1
        DB.close(db)

C.run()
""", "lang": "df"},
 {"p": "`DB.memory()` é o que torna teste com banco barato: nada em disco, nada para limpar, e cada `trial` começa do zero. Para testar sobre um banco **real** sem sujá-lo, `Crucible.banco(db)` abre transação e a desfaz no fim."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/biblioteca/database", "title": "Arcane.Database", "desc": "os 64 símbolos, um por um"},
   {"href": "/docs/tecnicas/banco-de-dados/crud", "title": "CRUD completo", "desc": "um exemplo ponta a ponta"},
   {"href": "/docs/orm", "title": "ORM", "desc": "quando o SQL à mão deixa de compensar"},
   {"href": "/docs/big-o/dados", "title": "Custo em dados", "desc": "N+1, índice e paginação por cursor"}]},
]},
]
