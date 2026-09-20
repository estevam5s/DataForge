// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "18 · Persistência",
  description: "6 exercícios: JSON, CSV, SQLite e serialização.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 18`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[164](#164-serializacao-de-dados)", "**Serializacao de dados**", "converta estruturas para JSON, CSV, TOML e de volta."], ["[165](#165-arquivos-e-diretorios)", "**Arquivos e diretorios**", "leia, escreva e organize arquivos com Arcane.IO."], ["[166](#166-banco-de-dados)", "**Banco de dados**", "crie tabelas, insira e consulte com Arcane.Database."], ["[167](#167-servidor-http)", "**Servidor HTTP**", "monte uma API REST com rotas e JSON."], ["[168](#168-cliente-http-e-urls)", "**Cliente HTTP e URLs**", "monte URLs, trate respostas e prepare requisicoes."], ["[169](#169-projeto-crud-com-persistencia)", "**Projeto: CRUD com persistencia**", "junte banco, validacao e relatorio num sistema completo."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "164 · Serializacao de dados"},
  {"p": "**Enunciado.** converta estruturas para JSON, CSV, TOML e de volta."},
  { code: `adopt Arcane.Serialization as Serde

dados := {
    "app": "DataForge",
    "versao": 4,
    "ativo": yes,
    "tags": ["linguagem", "dados"],
    "autor": {"nome": "Ana", "email": "ana@x.com"}
}

// JSON
texto := Serde.to_json(dados)
out $"json: {texto[0:50]}..."
volta := Serde.from_json(texto)
assert volta["versao"] is 4, "roundtrip json"
assert volta["autor"]["nome"] is "Ana", "aninhado preservado"

// JSON legivel
out ""
out Serde.json_pretty(dados["autor"])

// Leitura tolerante: nunca dispara
out ""
bom := Serde.from_json_safe(texto)
ruim := Serde.from_json_safe("{isso nao e json")
out $"valido: ok={bom.ok}"
out $"invalido: ok={ruim.ok}, erro='{ruim.error[0:30]}...'"
assert bom.ok is yes, "json valido"
assert ruim.ok is no, "json invalido nao dispara"
assert ruim.value is void, "valor padrao"

// Caminho pontuado
out ""
out $"autor.nome: {Serde.json_path(dados, "autor.nome")}"
out $"tags.0:     {Serde.json_path(dados, "tags.0")}"
out $"ausente:    {Serde.json_path(dados, "autor.telefone", "nao informado")}"
assert Serde.json_path(dados, "autor.email") is "ana@x.com", "caminho aninhado"
assert Serde.json_path(dados, "tags.1") is "dados", "indice de lista"

// CSV a partir de registros
registros := [
    {"nome": "Ana", "idade": 30, "setor": "vendas"},
    {"nome": "Bruno", "idade": 25, "setor": "ti"}
]
csv := Serde.records_to_csv(registros)
out ""
out csv
lidos := Serde.csv_to_records(csv)
assert len(lidos) is 2, "dois registros"
assert lidos[0]["nome"] is "Ana", "primeiro registro"

// TOML
config := {"servidor": {"host": "localhost", "porta": 8080}, "debug": yes}
out Serde.to_toml(config)
assert Serde.from_toml(Serde.to_toml(config))["servidor"]["porta"] is 8080, "roundtrip toml"

// Achatar e desachatar
plano := Serde.flatten(dados["autor"])
out $"achatado: {plano}"
assert plano["nome"] is "Ana", "achatado"
assert Serde.unflatten({"a.b.c": 1})["a"]["b"]["c"] is 1, "desachatado"

// JSON Lines: um objeto por linha
linhas := Serde.json_lines(registros)
out ""
out $"json lines tem {len(linhas.lines())} linhas"
assert len(Serde.from_json_lines(linhas)) is 2, "roundtrip jsonl"

// Formatos disponiveis
out ""
out $"formatos: {Serde.formats()}"`, lang: 'df', title: `exercicios/18-dados-e-persistencia/164_serializacao.df` },
  {"h3": "Por que isso importa"},
  {"p": "Todo programa que não é um exercício conversa com o mundo: lê um arquivo, chama uma API, grava um relatório. Serialização é essa fronteira, e o módulo `Arcane.Serialization` cobre os formatos que aparecem na prática."},
  {"h3": "JSON"},
  { code: `Serde.to_json(dados)                  // compacto
Serde.json_pretty(dados, 2)           // indentado
Serde.from_json(texto)                // pode disparar
Serde.from_json_safe(texto, padrao)   // nunca dispara`, lang: 'df' },
  {"p": "**A variante `_safe`**"},
  { code: `r := Serde.from_json_safe("{isso nao e json")
// {ok: no, value: void, error: "Expecting property name..."}`, lang: 'df' },
  {"p": "Dado que veio de fora **vai** estar malformado alguma hora. `from_json_safe` transforma isso num valor que você examina, em vez de uma exceção que precisa envolver em `monitor`:"},
  { code: `r := Serde.from_json_safe(corpo)
given r.ok:
    processar(r.value)
otherwise:
    responder_erro(r.error)`, lang: 'df' },
  {"h3": "`json_path` — navegar sem quebrar"},
  { code: `Serde.json_path(dados, "autor.nome")
Serde.json_path(dados, "tags.0")                       // índice de lista
Serde.json_path(dados, "autor.telefone", "ausente")    // com padrão`, lang: 'df' },
  {"p": "Sem isso, chegar num campo aninhado exige verificar cada nível:"},
  { code: `given "autor" in dados and "nome" in dados["autor"]:`, lang: 'df' },
  {"p": "`json_path` faz o mesmo em uma expressão, devolvendo o padrão se qualquer nível faltar."},
  {"h3": "CSV"},
  { code: `Serde.records_to_csv(registros)     // lista de vaults → CSV com cabeçalho
Serde.csv_to_records(csv)           // CSV com cabeçalho → lista de vaults
Serde.to_csv(linhas, ",", cabecalho)
Serde.from_csv(texto, ",", yes)`, lang: 'df' },
  {"p": "As duas primeiras assumem que a primeira linha é cabeçalho e que cada linha vira um vault — o formato natural para dados tabulares."},
  {"h3": "TOML"},
  {"p": "Legível para humanos, ideal para configuração:"},
  { code: `config := {"servidor": {"host": "localhost", "porta": 8080}}
Serde.to_toml(config)`, lang: 'df' },
  { code: `[servidor]
host = "localhost"
porta = 8080`, lang: 'toml' },
  {"h3": "Achatar e desachatar"},
  { code: `Serde.flatten({"a": {"b": 1}})      // {"a.b": 1}
Serde.unflatten({"a.b": 1})         // {"a": {"b": 1}}`, lang: 'df' },
  {"p": "`flatten` é o que transforma um JSON aninhado em colunas de CSV. `unflatten` reconstrói."},
  {"h3": "JSON Lines"},
  { code: `Serde.json_lines(registros)         // um objeto JSON por linha
Serde.from_json_lines(texto)`, lang: 'df' },
  {"p": "O formato de log e de exportação em lote: cada linha é independente, então dá para processar em stream sem carregar o arquivo inteiro."},
  {"h3": "Saída esperada"},
  { code: `json: {"app": "DataForge", "versao": 4, "ativo": true, "t...
{
  "nome": "Ana",
  "email": "ana@x.com"
}
valido: ok=yes
invalido: ok=no, erro='Expecting property name enclos...'
autor.nome: Ana
tags.0:     linguagem
ausente:    nao informado
nome,idade,setor
Ana,30,vendas
Bruno,25,ti`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Leia um CSV, transforme com pipeline e grave como JSON.", "Escreva `carregar_config(caminho)` com TOML e valores padrão."]},
  {"h2": "165 · Arquivos e diretorios"},
  {"p": "**Enunciado.** leia, escreva e organize arquivos com Arcane.IO."},
  { code: `adopt Arcane.IO as IO
adopt Arcane.Serialization as Serde

pasta := "_exercicio_164"
IO.mkdir(pasta)
assert IO.exists(pasta) is yes, "pasta criada"

// Escrever e ler texto
alvo := IO.join(pasta, "notas.txt")
IO.write(alvo, "primeira linha\\nsegunda linha\\nterceira linha")

conteudo := IO.read(alvo)
out $"lidas {len(conteudo.lines())} linhas"
assert len(conteudo.lines()) is 3, "tres linhas"
assert conteudo.lines()[0] is "primeira linha", "primeira linha"

// Anexar
IO.append(alvo, "\\nquarta linha")
assert len(IO.read(alvo).lines()) is 4, "quatro apos anexar"

// Tamanho e existencia
out $"tamanho: {IO.size(alvo)} bytes"
assert IO.size(alvo) bigger 0, "arquivo tem conteudo"
assert IO.file_exists(alvo) is yes, "existe"
assert IO.exists(IO.join(pasta, "inexistente.txt")) is no, "nao existe"

// Caminhos
out ""
out $"nome:      {IO.basename(alvo)}"
out $"pasta:     {IO.dirname(alvo)}"
out $"extensao:  {IO.ext(alvo)}"
assert IO.basename(alvo) is "notas.txt", "basename"
assert IO.ext(alvo) is ".txt", "extensao"

// JSON direto em arquivo
config := {"tema": "escuro", "fonte": 14, "plugins": ["a", "b"]}
json_alvo := IO.join(pasta, "config.json")
IO.write_json(json_alvo, config)
lido := IO.read_json(json_alvo)
out ""
out $"config lida: {lido}"
assert lido["fonte"] is 14, "json roundtrip"
assert lido["plugins"] is ["a", "b"], "lista preservada"

// CSV direto em arquivo
csv_alvo := IO.join(pasta, "dados.csv")
IO.write_csv(csv_alvo, [["nome", "nota"], ["Ana", "9.5"], ["Bruno", "7.0"]])
linhas := IO.read_csv(csv_alvo)
out $"csv tem {len(linhas)} linhas"
assert len(linhas) is 3, "cabecalho + dois"
assert linhas[1][0] is "Ana", "primeira linha de dados"

// Listar o diretorio
out ""
arquivos := IO.list_dir(pasta)
out $"na pasta: {sorted(arquivos)}"
assert len(arquivos) is 3, "tres arquivos"

// Copiar e renomear
copia := IO.join(pasta, "notas_copia.txt")
IO.copy(alvo, copia)
assert IO.exists(copia) is yes, "copiado"
assert IO.read(copia) is IO.read(alvo), "conteudo identico"

renomeado := IO.join(pasta, "notas_final.txt")
IO.rename(copia, renomeado)
assert IO.exists(renomeado) is yes, "renomeado"
assert IO.exists(copia) is no, "o antigo sumiu"

// Processar so os .txt
out ""
textos := IO.list_dir(pasta) >> sift nome: nome.endswith(".txt")
out $"arquivos .txt: {len(textos)}"
assert len(textos) is 2, "dois .txt"

// Limpar
cycle nome in IO.list_dir(pasta):
    IO.delete(IO.join(pasta, nome))
IO.delete(pasta)
assert IO.exists(pasta) is no, "pasta removida"
out ""
out "tudo limpo"`, lang: 'df', title: `exercicios/18-dados-e-persistencia/165_arquivos.df` },
  {"h3": "Texto"},
  { code: `IO.write(caminho, texto)      // cria ou substitui
IO.append(caminho, texto)     // acrescenta ao fim
IO.read(caminho)              // devolve o conteúdo`, lang: 'df' },
  {"p": "Para trabalhar linha a linha, `.lines()` da própria string:"},
  { code: `cycle linha in IO.read("dados.txt").lines():
    processar(linha)`, lang: 'df' },
  {"p": "Para arquivos grandes, prefira um `stream action` que emite linha por linha — `IO.read` carrega tudo na memória."},
  {"h3": "Formatos estruturados"},
  { code: `IO.write_json(caminho, vault)     IO.read_json(caminho)
IO.write_csv(caminho, linhas)     IO.read_csv(caminho)`, lang: 'df' },
  {"p": "Fazem a serialização e a escrita numa chamada só, e é o que você quer na maioria dos casos."},
  {"h3": "Caminhos"},
  { code: `IO.join(pasta, "arquivo.txt")     // monta com o separador certo
IO.basename(caminho)              // "notas.txt"
IO.dirname(caminho)               // a pasta
IO.ext(caminho)                   // ".txt"
IO.abs(caminho)                   // caminho absoluto`, lang: 'df' },
  {"p": "**Sempre use `IO.join`** em vez de concatenar com `\"/\"`. O separador muda entre sistemas, e concatenar à mão é a forma mais rápida de escrever código que só funciona na sua máquina."},
  {"h3": "Diretórios"},
  { code: `IO.mkdir(pasta)          // cria, inclusive os níveis intermediários
IO.list_dir(pasta)       // os nomes dentro dela
IO.exists(caminho)       // arquivo ou pasta
IO.file_exists(caminho)  // só arquivo`, lang: 'df' },
  {"h3": "Copiar, renomear, apagar"},
  { code: `IO.copy(origem, destino)
IO.rename(antigo, novo)
IO.delete(caminho)`, lang: 'df' },
  {"p": "`rename` também **move** entre pastas — é a mesma operação no sistema de arquivos."},
  {"h3": "Filtrar por extensão"},
  { code: `textos := IO.list_dir(pasta) >> sift nome: nome.endswith(".txt")`, lang: 'df' },
  {"p": "`list_dir` devolve uma lista comum, então todo o pipeline funciona sobre ela."},
  {"h3": "Limpeza garantida"},
  {"p": "Este exercício apaga o que criou. Num programa real, use `defer` para garantir isso mesmo se algo falhar no meio:"},
  { code: `action processar():
    IO.mkdir(temp)
    defer:
        limpar(temp)
    // ... o defer roda mesmo se isto disparar`, lang: 'df' },
  {"h3": "Saída esperada"},
  { code: `lidas 3 linhas
tamanho: 47 bytes

nome:      notas.txt
pasta:     _exercicio_164
extensao:  .txt

config lida: {tema: escuro, fonte: 14, plugins: [a, b]}
csv tem 3 linhas

na pasta: [config.json, dados.csv, notas.txt]

arquivos .txt: 2

tudo limpo`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Escreva `action tamanho_da_pasta(p)` somando o tamanho de todos os arquivos.", "Faça um backup que copia só os arquivos alterados."]},
  {"h2": "166 · Banco de dados"},
  {"p": "**Enunciado.** crie tabelas, insira e consulte com Arcane.Database."},
  { code: `adopt Arcane.Database as DB

// Um banco em memoria: nada toca o disco
conn := DB.memory()

DB.execute(conn, """CREATE TABLE produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    estoque INTEGER DEFAULT 0
)""")

assert DB.table_exists(conn, "produtos") is yes, "tabela criada"

// Inserir um por vez
DB.execute(conn, "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
    ["Mouse", 80.0, 15])

// Ou varios de uma vez
DB.execute_many(conn, "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", [
        ["Teclado", 200.0, 3],
        ["Monitor", 1200.0, 0],
        ["Cabo", 25.0, 60]
    ])

assert DB.count(conn, "produtos") is 4, "quatro produtos"

// Consultar
todos := DB.query(conn, "SELECT nome, preco, estoque FROM produtos ORDER BY preco DESC")
out "── catalogo ──"
cycle p in todos:
    out $"  {str(p["nome"]).pad_end(10)} R$ {str(p["preco"]).pad_start(8)}  ({p["estoque"]} un)"

assert len(todos) is 4, "quatro linhas"
assert todos[0]["nome"] is "Monitor", "o mais caro primeiro"

// Parametros evitam injecao de SQL
baratos := DB.query(conn, "SELECT nome FROM produtos WHERE preco < ?", [100])
out ""
out $"abaixo de 100: {baratos >> morph p: p["nome"]}"
assert len(baratos) is 2, "mouse e cabo"

// Uma linha so
caro := DB.query_one(conn, "SELECT nome, preco FROM produtos ORDER BY preco DESC LIMIT 1")
out $"mais caro: {caro["nome"]} a R$ {caro["preco"]}"
assert caro["nome"] is "Monitor", "query_one"

// Agregacoes
resumo := DB.query_one(conn, "SELECT COUNT(*) AS total, SUM(preco * estoque) AS patrimonio FROM produtos")
out ""
out $"{resumo["total"]} produtos, patrimonio R$ {resumo["patrimonio"]}"
assert resumo["total"] is 4, "contagem"
assert resumo["patrimonio"] is 3300.0, "1200 + 600 + 0 + 1500"

// Atualizar e remover
DB.execute(conn, "UPDATE produtos SET estoque = estoque + 10 WHERE nome = ?", ["Monitor"])
novo := DB.query_one(conn, "SELECT estoque FROM produtos WHERE nome = ?", ["Monitor"])
assert novo["estoque"] is 10, "estoque reposto"

DB.execute(conn, "DELETE FROM produtos WHERE estoque = 0")
assert DB.count(conn, "produtos") is 4, "nenhum zerado agora"

// Transacao: tudo ou nada
out ""
DB.begin(conn)
DB.execute(conn, "INSERT INTO produtos (nome, preco) VALUES (?, ?)", ["Temporario", 1.0])
assert DB.count(conn, "produtos") is 5, "dentro da transacao"
DB.rollback(conn)
assert DB.count(conn, "produtos") is 4, "rollback desfez"
out "rollback funcionou"

DB.begin(conn)
DB.execute(conn, "INSERT INTO produtos (nome, preco) VALUES (?, ?)", ["Definitivo", 50.0])
DB.commit(conn)
assert DB.count(conn, "produtos") is 5, "commit manteve"
out "commit funcionou"

// Estrutura da tabela
out ""
out $"tabelas: {DB.tables(conn)}"
out $"colunas: {DB.columns(conn, "produtos")}"

DB.close(conn)
out ""
out "conexao fechada"`, lang: 'df', title: `exercicios/18-dados-e-persistencia/166_banco_sqlite.df` },
  {"h3": "Conectar"},
  { code: `conn := DB.memory()                  // em memória: some ao terminar
conn := DB.connect("dados.db")       // arquivo SQLite`, lang: 'df' },
  {"p": "`memory()` é ideal para teste: cada execução começa limpa, e nada fica no disco."},
  {"h3": "Parâmetros, sempre"},
  { code: `DB.query(conn, "SELECT nome FROM produtos WHERE preco < ?", [100])`, lang: 'df' },
  {"p": "Nunca monte SQL com interpolação:"},
  { code: `DB.query(conn, $"SELECT * FROM users WHERE nome = '{entrada}'")   // NÃO`, lang: 'df' },
  {"p": "Se `entrada` for `'; DROP TABLE users; --`, você acabou de perder a tabela. Com `?`, o valor é enviado separado do comando e nunca é interpretado como SQL. Essa é a defesa contra injeção, e ela é completa."},
  {"h3": "As operações"},
  {"table": {"head": ["Chamada", "Para"], "rows": [["`execute(conn, sql, params)`", "INSERT, UPDATE, DELETE, CREATE"], ["`execute_many(conn, sql, lista)`", "vários INSERT de uma vez"], ["`query(conn, sql, params)`", "várias linhas, como lista de vaults"], ["`query_one(conn, sql, params)`", "uma linha, ou `void`"], ["`count(conn, tabela)`", "atalho para `COUNT(*)`"]]}},
  {"p": "`query` devolve vaults com os nomes das colunas como chaves — dá para usar `p[\"nome\"]` direto, sem índices."},
  {"h3": "`execute_many`"},
  { code: `DB.execute_many(conn, "INSERT INTO produtos VALUES (?, ?, ?)", [
    ["Teclado", 200.0, 3],
    ["Monitor", 1200.0, 0]
])`, lang: 'df' },
  {"p": "Uma ida ao banco em vez de N. Para inserção em lote, a diferença de desempenho é grande."},
  {"h3": "Transações"},
  { code: `DB.begin(conn)
DB.execute(conn, "UPDATE contas SET saldo = saldo - 100 WHERE id = 1")
DB.execute(conn, "UPDATE contas SET saldo = saldo + 100 WHERE id = 2")
DB.commit(conn)         // ou DB.rollback(conn)`, lang: 'df' },
  {"p": "As duas operações acontecem **juntas ou nenhuma**. Sem transação, uma falha entre elas deixaria dinheiro sumido."},
  {"p": "O padrão seguro combina com `monitor`:"},
  { code: `DB.begin(conn)
monitor:
    // ... operações
    DB.commit(conn)
handle e:
    DB.rollback(conn)
    propagate e.message`, lang: 'df' },
  {"h3": "Introspecção"},
  { code: `DB.tables(conn)                  // as tabelas
DB.columns(conn, "produtos")     // as colunas
DB.table_exists(conn, "x")
DB.table_info(conn, "produtos")  // tipos e restrições`, lang: 'df' },
  {"h3": "Saída esperada"},
  { code: `── catalogo ──
  Monitor    R$   1200.0  (0 un)
  Teclado    R$    200.0  (3 un)
  Mouse      R$     80.0  (15 un)
  Cabo       R$     25.0  (60 un)

abaixo de 100: [Mouse, Cabo]
mais caro: Monitor a R$ 1200.0

4 produtos, patrimonio R$ 3300.0

rollback funcionou
commit funcionou

tabelas: [produtos]
colunas: [id, nome, preco, estoque]

conexao fechada`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Crie uma tabela de vendas com chave estrangeira e faça um JOIN.", "Envolva uma transferência entre contas numa transação com `monitor`.", "Compare `execute` num laço com `execute_many` para 1000 registros."]},
  {"h2": "167 · Servidor HTTP"},
  {"p": "**Enunciado.** monte uma API REST com rotas e JSON."},
  { code: `adopt Arcane.Http as Http
adopt Arcane.Serialization as Serde

// Este exercicio monta a aplicacao e verifica a configuracao sem
// abrir a porta — assim ele roda na suite de testes.

app := Http.create("API de Tarefas")
Http.cors(app)
Http.logger(app)

// ── dados em memoria ──
tarefas := [
    {"id": 1, "titulo": "Estudar DataForge", "feita": yes},
    {"id": 2, "titulo": "Escrever testes", "feita": no}
]
proximo_id := 3

// ── validacao, separada da rota ──
action validar_tarefa(corpo):
    problemas := []
    given corpo is void:
        problemas.append("corpo ausente")
        yield problemas
    given "titulo" not in corpo:
        problemas.append("titulo e obrigatorio")
    orif len(corpo["titulo"].trim()) smaller 3:
        problemas.append("titulo precisa de ao menos 3 letras")
    yield problemas

// ── as rotas ──
action listar(req, res):
    res.json(tarefas)

action buscar(req, res):
    id := cast req["params"]["id"] as Integer
    achadas := tarefas >> sift t: t["id"] is id
    given len(achadas) is 0:
        res.json({"erro": "tarefa nao encontrada"}, 404)
    otherwise:
        res.json(achadas[0])

action criar(req, res):
    problemas := validar_tarefa(req["json"])
    given len(problemas) bigger 0:
        res.json({"erros": problemas}, 400)
        yield void
    nova := {
        "id": proximo_id,
        "titulo": req["json"]["titulo"].trim(),
        "feita": no
    }
    proximo_id += 1
    tarefas.append(nova)
    res.json(nova, 201)

action concluir(req, res):
    id := cast req["params"]["id"] as Integer
    cycle i from 0 to len(tarefas) - 1:
        given tarefas[i]["id"] is id:
            tarefas[i]["feita"] := yes
            res.json(tarefas[i])
            yield void
    res.json({"erro": "tarefa nao encontrada"}, 404)

action remover(req, res):
    id := cast req["params"]["id"] as Integer
    tarefas := tarefas >> sift t: t["id"] isnt id
    res.json({"removida": id})

Http.get(app, "/api/tarefas", listar)
Http.get(app, "/api/tarefas/:id", buscar)
Http.post(app, "/api/tarefas", criar)
Http.put(app, "/api/tarefas/:id", concluir)
Http.delete(app, "/api/tarefas/:id", remover)

// ── verificando a configuracao ──
out "── rotas registradas ──"
out "  GET    /api/tarefas"
out "  GET    /api/tarefas/:id"
out "  POST   /api/tarefas"
out "  PUT    /api/tarefas/:id"
out "  DELETE /api/tarefas/:id"

// A validacao e testavel sem subir servidor
out ""
out "── validacao ──"
out $"  sem corpo:      {validar_tarefa(void)}"
out $"  sem titulo:     {validar_tarefa({"outro": 1})}"
out $"  titulo curto:   {validar_tarefa({"titulo": "ab"})}"
out $"  valido:         {validar_tarefa({"titulo": "Uma tarefa"})}"

assert len(validar_tarefa(void)) is 1, "corpo ausente"
assert len(validar_tarefa({"titulo": "ab"})) is 1, "titulo curto"
assert len(validar_tarefa({"titulo": "Uma tarefa"})) is 0, "valido"

out ""
out $"tarefas iniciais: {len(tarefas)}"
out ""
out "Para subir de verdade, acrescente ao final:"
out "    Http.listen(app, 3000)"`, lang: 'df', title: `exercicios/18-dados-e-persistencia/167_http_servidor.df` },
  {"h3": "Montar a aplicação"},
  { code: `app := Http.create("API de Tarefas")
Http.cors(app)         // libera chamadas de outra origem
Http.logger(app)       // registra cada requisição`, lang: 'df' },
  {"h3": "Rotas"},
  { code: `Http.get(app, "/api/tarefas", listar)
Http.get(app, "/api/tarefas/:id", buscar)
Http.post(app, "/api/tarefas", criar)
Http.put(app, "/api/tarefas/:id", concluir)
Http.delete(app, "/api/tarefas/:id", remover)`, lang: 'df' },
  {"p": "O `:id` é um **parâmetro de caminho**, disponível em `req[\"params\"][\"id\"]` — como texto, sempre. Converta antes de comparar:"},
  { code: `id := cast req["params"]["id"] as Integer`, lang: 'df' },
  {"h3": "O par requisição/resposta"},
  {"table": {"head": ["Leitura", "Contém"], "rows": [["`req[\"params\"]`", "parâmetros do caminho (`:id`)"], ["`req[\"query\"]`", "da query string (`?pagina=2`)"], ["`req[\"json\"]`", "o corpo, já interpretado"], ["`req[\"headers\"]`", "os cabeçalhos"]]}},
  {"table": {"head": ["Escrita", "Faz"], "rows": [["`res.json(dados)`", "responde JSON com 200"], ["`res.json(dados, 404)`", "com o código que você escolher"], ["`res.html(texto)`", "responde HTML"], ["`res.send(texto, 200)`", "texto puro"]]}},
  {"h3": "Códigos que importam"},
  {"table": {"head": ["Código", "Quando"], "rows": [["200", "deu certo"], ["201", "criou algo novo"], ["400", "o cliente mandou dado inválido"], ["404", "não existe"], ["500", "o servidor quebrou"]]}},
  {"p": "Devolver 200 com `{\"erro\": ...}` no corpo obriga todo cliente a inspecionar o JSON para saber se deu certo. O código HTTP existe justamente para isso."},
  {"h3": "Validação fora da rota"},
  { code: `action validar_tarefa(corpo):
    problemas := []
    given "titulo" not in corpo:
        problemas.append("titulo e obrigatorio")
    orif len(corpo["titulo"].trim()) smaller 3:
        problemas.append("titulo precisa de ao menos 3 letras")
    yield problemas`, lang: 'df' },
  {"p": "Duas vantagens de separar:"},
  {"p": "1. **Testável sem servidor** — como este exercício demonstra. 2. **Reutilizável** — a mesma validação serve para POST e PUT."},
  {"p": "E devolver **todos** os problemas de uma vez poupa o cliente de descobrir um erro por requisição."},
  {"h3": "Saída esperada"},
  { code: `── rotas registradas ──
  GET    /api/tarefas
  ...

── validacao ──
  sem corpo:      [corpo ausente]
  sem titulo:     [titulo e obrigatorio]
  titulo curto:   [titulo precisa de ao menos 3 letras]
  valido:         []

tarefas iniciais: 2`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente `Http.listen(app, 3000)` e teste com `curl`:"]},
  { code: `  curl localhost:3000/api/tarefas
  curl -X POST localhost:3000/api/tarefas -H 'Content-Type: application/json' -d '{"titulo":"Nova"}'`, lang: 'bash' },
  {"list": ["Troque a lista em memória por `Arcane.Database`.", "Acrescente paginação com `req[\"query\"][\"pagina\"]`."]},
  {"h2": "168 · Cliente HTTP e URLs"},
  {"p": "**Enunciado.** monte URLs, trate respostas e prepare requisicoes."},
  { code: `adopt Arcane.Web as Web
adopt Arcane.Serialization as Serde

// Codificar valores para URL
out "── codificacao ──"
out $"espacos:  {Web.encode_url("busca com espacos")}"
out $"acentos:  {Web.encode_url("cafe & pao")}"
assert Web.decode_url(Web.encode_url("a b&c")) is "a b&c", "roundtrip"

// Montar uma query string
action montar_url(base, parametros):
    given len(parametros.keys()) is 0:
        yield base
    partes := [$"{Web.encode_url(k)}={Web.encode_url(str(parametros[k]))}"
        cycle k in parametros.keys()]
    yield $"{base}?{partes.join("&")}"

url := montar_url("https://api.exemplo.com/busca", {
        "q": "linguagem de programacao",
        "pagina": 2,
        "ordem": "recente"
    })
out ""
out url
assert "q=linguagem" in url, "parametro codificado"
assert "pagina=2" in url, "numero convertido"

// Interpretar uma query string de volta
action ler_query(texto):
    resultado := {}
    given len(texto) is 0:
        yield resultado
    cycle par in texto.split("&"):
        given "=" in par:
            partes := par.split("=")
            resultado[Web.decode_url(partes[0])] := Web.decode_url(partes[1])
    yield resultado

lidos := ler_query("nome=Ana%20Silva&idade=30")
out ""
out $"query lida: {lidos}"
assert lidos["nome"] is "Ana Silva", "decodificado"
assert lidos["idade"] is "30", "valores sao texto"

// JSON no corpo
corpo := Web.json_stringify({"acao": "criar", "dados": {"nome": "Ana"}})
out ""
out $"corpo: {corpo}"
assert Web.json_parse(corpo)["acao"] is "criar", "roundtrip json"

// Classificar o codigo de resposta
action classificar(codigo):
    match codigo:
        point c when c bigger_eq 200 and c smaller 300:
            yield "sucesso"
        point c when c bigger_eq 300 and c smaller 400:
            yield "redirecionamento"
        point c when c bigger_eq 400 and c smaller 500:
            yield "erro do cliente"
        point c when c bigger_eq 500:
            yield "erro do servidor"
        default:
            yield "desconhecido"

out ""
out "── codigos ──"
cycle c in [200, 201, 301, 400, 404, 500, 503]:
    out $"  {c}: {classificar(c)}"

assert classificar(200) is "sucesso", "2xx"
assert classificar(404) is "erro do cliente", "4xx"
assert classificar(503) is "erro do servidor", "5xx"

// Tratar uma resposta simulada
action processar(resposta):
    given resposta["status"] bigger_eq 400:
        yield {"ok": no, "erro": $"HTTP {resposta["status"]}"}
    dados := Serde.from_json_safe(resposta["body"])
    given dados.ok is no:
        yield {"ok": no, "erro": "resposta nao e JSON valido"}
    yield {"ok": yes, "dados": dados.value}

out ""
out processar({"status": 200, "body": '{"nome": "Ana"}'})
out processar({"status": 404, "body": ""})
out processar({"status": 200, "body": "isso nao e json"})

assert processar({"status": 200, "body": '{"a": 1}'}).ok is yes, "sucesso"
assert processar({"status": 500, "body": ""}).ok is no, "erro http"
assert processar({"status": 200, "body": "quebrado"}).ok is no, "json invalido"`, lang: 'df', title: `exercicios/18-dados-e-persistencia/168_http_cliente.df` },
  {"h3": "Codificação de URL"},
  { code: `Web.encode_url("busca com espacos")     // "busca%20com%20espacos"
Web.decode_url(texto)`, lang: 'df' },
  {"p": "Espaços, acentos e `&` precisam ser codificados. Sem isso, um `&` no valor de um parâmetro quebra a query string inteira — o servidor lê como início de outro parâmetro."},
  {"h3": "Montar a query string"},
  { code: `partes := [$"{Web.encode_url(k)}={Web.encode_url(str(parametros[k]))}"
           cycle k in parametros.keys()]
yield $"{base}?{partes.join("&")}"`, lang: 'df' },
  {"p": "Repare: **chave e valor** são codificados, e `str()` converte números antes. Concatenar valores crus é a origem de metade dos bugs de integração."},
  {"h3": "Classificar respostas com `match`"},
  { code: `match codigo:
    point c when c bigger_eq 200 and c smaller 300:
        yield "sucesso"
    point c when c bigger_eq 400 and c smaller 500:
        yield "erro do cliente"`, lang: 'df' },
  {"p": "As guardas expressam faixas diretamente. A distinção 4xx/5xx importa na prática:"},
  {"list": ["**4xx** é culpa do cliente — repetir a mesma requisição dá o mesmo erro", "**5xx** é do servidor — vale tentar de novo, com espera crescente"]},
  {"h3": "Tratar a resposta em camadas"},
  { code: `action processar(resposta):
    given resposta["status"] bigger_eq 400:
        yield {"ok": no, "erro": $"HTTP {resposta["status"]}"}
    dados := Serde.from_json_safe(resposta["body"])
    given dados.ok is no:
        yield {"ok": no, "erro": "resposta nao e JSON valido"}
    yield {"ok": yes, "dados": dados.value}`, lang: 'df' },
  {"p": "Três coisas podem dar errado, e cada uma tem seu tratamento:"},
  {"p": "1. o servidor recusou (código ≥ 400) 2. respondeu, mas o corpo não é JSON 3. deu tudo certo"},
  {"p": "Note o `from_json_safe`: um servidor que devolve HTML de erro com status 200 é comum o bastante para valer o cuidado."},
  {"h3": "O padrão de resultado"},
  { code: `{"ok": yes, "dados": ...}
{"ok": no, "erro": "..."}`, lang: 'df' },
  {"p": "Sempre a mesma forma, sucesso ou falha. Quem chama testa `ok` uma vez, sem precisar de `monitor` em volta de cada chamada."},
  {"h3": "Chamadas de verdade"},
  { code: `resposta := Web.get("https://api.exemplo.com/dados")
resposta := Web.post(url, corpo)
resposta := Web.request(metodo, url, cabecalhos, corpo)`, lang: 'df' },
  {"p": "Este exercício não chama a rede para poder rodar em qualquer ambiente."},
  {"h3": "Saída esperada"},
  { code: `── codificacao ──
espacos:  busca%20com%20espacos
acentos:  cafe%20%26%20pao

https://api.exemplo.com/busca?q=linguagem%20de%20programacao&pagina=2&ordem=recente

query lida: {nome: Ana Silva, idade: 30}

corpo: {"acao": "criar", "dados": {"nome": "Ana"}}

── codigos ──
  200: sucesso
  404: erro do cliente
  503: erro do servidor

{ok: yes, dados: {nome: Ana}}
{ok: no, erro: HTTP 404}
{ok: no, erro: resposta nao e JSON valido}`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Escreva `com_retentativa(url, tentativas)` usando `retry`, só para 5xx.", "Acrescente cabeçalhos de autenticação ao montador de requisição."]},
  {"h2": "169 · Projeto: CRUD com persistencia"},
  {"p": "**Enunciado.** junte banco, validacao e relatorio num sistema completo."},
  { code: `adopt Arcane.Database as DB
adopt Arcane.Text as Text
adopt Arcane.Time as Time

// ═══ MODELO ═══

record Aluno:
    id: Integer
    nome: String
    email: String
    nota: Number

enum Conceito:
    A := 9
    B := 7
    C := 5
    D := 0

action conceito_de(nota: Number) -> Conceito:
    given nota bigger_eq 9:
        yield Conceito.A
    orif nota bigger_eq 7:
        yield Conceito.B
    orif nota bigger_eq 5:
        yield Conceito.C
    yield Conceito.D

// ═══ VALIDACAO ═══

action validar(nome, email, nota):
    problemas := []
    given len(nome.trim()) smaller 3:
        problemas.append("nome precisa de ao menos 3 letras")
    given "@" not in email:
        problemas.append("email invalido")
    given nota smaller 0 or nota bigger 10:
        problemas.append("nota deve estar entre 0 e 10")
    yield problemas

// ═══ PERSISTENCIA ═══

conn := DB.memory()
DB.execute(conn, """CREATE TABLE alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    nota REAL NOT NULL
)""")

action inserir(nome, email, nota):
    problemas := validar(nome, email, nota)
    given len(problemas) bigger 0:
        yield {"ok": no, "erros": problemas}
    monitor:
        DB.execute(conn, "INSERT INTO alunos (nome, email, nota) VALUES (?, ?, ?)",
            [nome.trim(), email.trim().lower(), nota])
        yield {"ok": yes}
    handle e:
        yield {"ok": no, "erros": ["email ja cadastrado"]}

action buscar_todos():
    linhas := DB.query(conn, "SELECT id, nome, email, nota FROM alunos ORDER BY nota DESC")
    yield linhas >> morph l: Aluno(l["id"], l["nome"], l["email"], l["nota"])

action atualizar_nota(id, nova):
    given nova smaller 0 or nova bigger 10:
        yield {"ok": no, "erros": ["nota fora da faixa"]}
    DB.execute(conn, "UPDATE alunos SET nota = ? WHERE id = ?", [nova, id])
    yield {"ok": yes}

action remover(id):
    antes := DB.count(conn, "alunos")
    DB.execute(conn, "DELETE FROM alunos WHERE id = ?", [id])
    yield {"ok": DB.count(conn, "alunos") smaller antes}

// ═══ APLICACAO ═══

out Text.box("Cadastro de Alunos")

entradas := [
    ["Ana Silva", "ana@escola.br", 9.5],
    ["Bruno Costa", "bruno@escola.br", 7.0],
    ["Carla Dias", "carla@escola.br", 4.5],
    ["Ze", "ze@escola.br", 8.0],
    ["Diego Alves", "sem-arroba", 6.0],
    ["Elena Rocha", "elena@escola.br", 15.0],
    ["Repetido", "ana@escola.br", 5.0]
]

out ""
out "── cadastrando ──"
aceitos := 0
cycle e in entradas:
    nome, email, nota := e
    r := inserir(nome, email, nota)
    given r.ok:
        aceitos += 1
        out $"  ok   {nome}"
    otherwise:
        out $"  nao  {nome}: {r["erros"].join("; ")}"

assert aceitos is 3, "tres aceitos"
assert DB.count(conn, "alunos") is 3, "tres no banco"

// ── relatorio ──
alunos := buscar_todos()
out ""
out Text.box("Boletim")
cycle a in alunos:
    c := conceito_de(a.nota)
    out $"  {a.nome.pad_end(14)} {str(a.nota).pad_start(5)}  {c.name}"

media := alunos >> morph a: a.nota >> distill acc, n: acc + n 0
out ""
out $"media da turma: {round(media / len(alunos), 2)}"
assert round(media / len(alunos), 2) is 7.0, "media (9.5 + 7.0 + 4.5) / 3"

// ── distribuicao por conceito ──
out ""
out "── por conceito ──"
cycle nome_conceito in Conceito.names():
    quantos := len(alunos >> sift a: conceito_de(a.nota).name is nome_conceito)
    given quantos bigger 0:
        out $"  {nome_conceito}: {"#".repeat(quantos)} ({quantos})"

// ── atualizar e remover ──
out ""
primeiro := alunos[0]
atualizar_nota(primeiro.id, 10.0)
depois := DB.query_one(conn, "SELECT nota FROM alunos WHERE id = ?", [primeiro.id])
out $"nota de {primeiro.nome} atualizada para {depois["nota"]}"
assert depois["nota"] is 10.0, "nota atualizada"

assert atualizar_nota(primeiro.id, 99).ok is no, "nota fora da faixa recusada"

ultimo := alunos[len(alunos) - 1]
remover(ultimo.id)
out $"{ultimo.nome} removido"
assert DB.count(conn, "alunos") is 2, "dois restantes"

DB.close(conn)
out ""
out "conexao fechada"`, lang: 'df', title: `exercicios/18-dados-e-persistencia/169_projeto_crud.df` },
  {"h3": "A arquitetura"},
  { code: `MODELO         record Aluno, enum Conceito, conceito_de
VALIDACAO      validar — pura, sem banco
PERSISTENCIA   inserir, buscar_todos, atualizar_nota, remover
APLICACAO      cadastro, relatório, distribuição`, lang: 'text' },
  {"p": "Cada camada depende só das de cima. `validar` não sabe que existe banco; `conceito_de` não sabe que existe relatório."},
  {"h3": "Modelo e armazenamento são coisas diferentes"},
  {"p": "O banco guarda linhas; o programa trabalha com records:"},
  { code: `action buscar_todos():
    linhas := DB.query(conn, "SELECT id, nome, email, nota FROM alunos ...")
    yield linhas >> morph l: Aluno(l["id"], l["nome"], l["email"], l["nota"])`, lang: 'df' },
  {"p": "Essa conversão na fronteira paga por si: a partir dali o código usa `a.nome` com verificação de tipo, em vez de `l[\"nome\"]` com risco de digitar errado. E se a coluna do banco mudar de nome, só esta linha muda."},
  {"h3": "Validar antes de tocar no banco"},
  { code: `action inserir(nome, email, nota):
    problemas := validar(nome, email, nota)
    given len(problemas) bigger 0:
        yield {"ok": no, "erros": problemas}
    ...`, lang: 'df' },
  {"p": "Duas linhas de defesa, e as duas são necessárias:"},
  {"p": "1. **A validação** pega o que dá para prever (nome curto, e-mail sem `@`). 2. **A restrição do banco** (`UNIQUE`) pega o que só ele sabe (e-mail repetido)."},
  {"p": "A segunda vem envolvida em `monitor`, porque a violação chega como erro do SQLite:"},
  { code: `monitor:
    DB.execute(conn, "INSERT ...")
    yield {"ok": yes}
handle e:
    yield {"ok": no, "erros": ["email ja cadastrado"]}`, lang: 'df' },
  {"p": "Repare que a mensagem técnica do banco é traduzida para algo que o usuário entende."},
  {"h3": "O padrão de resultado"},
  {"p": "Toda operação devolve a mesma forma:"},
  { code: `{"ok": yes}
{"ok": no, "erros": ["...", "..."]}`, lang: 'df' },
  {"p": "Quem chama testa `ok` e, se falhou, tem a lista pronta para mostrar. Sem exceções, sem código de erro para decorar."},
  {"h3": "Enum com valor numérico"},
  { code: `enum Conceito:
    A := 9
    B := 7
    C := 5
    D := 0`, lang: 'df' },
  {"p": "O valor é a **nota mínima** daquele conceito. Isso guarda a regra no próprio enum, em vez de espalhá-la em números soltos pelo código."},
  {"h3": "Gráfico em texto"},
  { code: `out $"  {nome_conceito}: {"#".repeat(quantos)} ({quantos})"`, lang: 'df' },
  {"p": "Um histograma com uma linha. Em ferramenta de terminal, isso comunica a distribuição melhor que uma tabela de números."},
  {"h3": "Saída esperada"},
  { code: `┌────────────────────┐
│ Cadastro de Alunos │
└────────────────────┘

── cadastrando ──
  ok   Ana Silva
  ok   Bruno Costa
  ok   Carla Dias
  nao  Ze: nome precisa de ao menos 3 letras
  nao  Diego Alves: email invalido
  nao  Elena Rocha: nota deve estar entre 0 e 10
  nao  Repetido: email ja cadastrado

┌─────────┐
│ Boletim │
└─────────┘
  Ana Silva       9.5  A
  Bruno Costa     7.0  B
  Carla Dias      4.5  D

media da turma: 7.0

── por conceito ──
  A: # (1)
  B: # (1)
  D: # (1)`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente busca por nome com `LIKE` e parâmetro.", "Exponha o CRUD como API HTTP reaproveitando `validar`.", "Escreva `tests/validacao_test.df` cobrindo cada regra."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/18-dados-e-persistencia/164_serializacao.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '164-serializacao-de-dados', text: "164 · Serializacao de dados", level: 2 as const }, { id: 'por-que-isso-importa', text: "Por que isso importa", level: 3 as const }, { id: 'json', text: "JSON", level: 3 as const }, { id: 'jsonpath-navegar-sem-quebrar', text: "`json_path` — navegar sem quebrar", level: 3 as const }, { id: 'csv', text: "CSV", level: 3 as const }, { id: 'toml', text: "TOML", level: 3 as const }, { id: 'achatar-e-desachatar', text: "Achatar e desachatar", level: 3 as const }, { id: 'json-lines', text: "JSON Lines", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '165-arquivos-e-diretorios', text: "165 · Arquivos e diretorios", level: 2 as const }, { id: 'texto', text: "Texto", level: 3 as const }, { id: 'formatos-estruturados', text: "Formatos estruturados", level: 3 as const }, { id: 'caminhos', text: "Caminhos", level: 3 as const }, { id: 'diretorios', text: "Diretórios", level: 3 as const }, { id: 'copiar-renomear-apagar', text: "Copiar, renomear, apagar", level: 3 as const }, { id: 'filtrar-por-extensao', text: "Filtrar por extensão", level: 3 as const }, { id: 'limpeza-garantida', text: "Limpeza garantida", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '166-banco-de-dados', text: "166 · Banco de dados", level: 2 as const }, { id: 'conectar', text: "Conectar", level: 3 as const }, { id: 'parametros-sempre', text: "Parâmetros, sempre", level: 3 as const }, { id: 'as-operacoes', text: "As operações", level: 3 as const }, { id: 'executemany', text: "`execute_many`", level: 3 as const }, { id: 'transacoes', text: "Transações", level: 3 as const }, { id: 'introspeccao', text: "Introspecção", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '167-servidor-http', text: "167 · Servidor HTTP", level: 2 as const }, { id: 'montar-a-aplicacao', text: "Montar a aplicação", level: 3 as const }, { id: 'rotas', text: "Rotas", level: 3 as const }, { id: 'o-par-requisicaoresposta', text: "O par requisição/resposta", level: 3 as const }, { id: 'codigos-que-importam', text: "Códigos que importam", level: 3 as const }, { id: 'validacao-fora-da-rota', text: "Validação fora da rota", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '168-cliente-http-e-urls', text: "168 · Cliente HTTP e URLs", level: 2 as const }, { id: 'codificacao-de-url', text: "Codificação de URL", level: 3 as const }, { id: 'montar-a-query-string', text: "Montar a query string", level: 3 as const }, { id: 'classificar-respostas-com-match', text: "Classificar respostas com `match`", level: 3 as const }, { id: 'tratar-a-resposta-em-camadas', text: "Tratar a resposta em camadas", level: 3 as const }, { id: 'o-padrao-de-resultado', text: "O padrão de resultado", level: 3 as const }, { id: 'chamadas-de-verdade', text: "Chamadas de verdade", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '169-projeto-crud-com-persistencia', text: "169 · Projeto: CRUD com persistencia", level: 2 as const }, { id: 'a-arquitetura', text: "A arquitetura", level: 3 as const }, { id: 'modelo-e-armazenamento-sao-coisas-diferentes', text: "Modelo e armazenamento são coisas diferentes", level: 3 as const }, { id: 'validar-antes-de-tocar-no-banco', text: "Validar antes de tocar no banco", level: 3 as const }, { id: 'o-padrao-de-resultado', text: "O padrão de resultado", level: 3 as const }, { id: 'enum-com-valor-numerico', text: "Enum com valor numérico", level: 3 as const }, { id: 'grafico-em-texto', text: "Gráfico em texto", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"18 · Persistência"}
      description={"6 exercícios: JSON, CSV, SQLite e serialização."}
      href={"/docs/exercicios/18-dados-e-persistencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
