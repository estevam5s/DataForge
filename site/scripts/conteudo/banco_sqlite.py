# -*- coding: utf-8 -*-
"""Arcane.Database — SQLite, e os projetos que se fazem com ele."""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/tecnicas/banco-de-dados",
"title": "Banco de dados",
"description": "SQLite com CRUD, transações que desfazem, upsert, paginação, relatório agrupado, busca textual e plano de consulta — 63 símbolos, sem dependência.",
"blocos": [
 {"p": "`Arcane.Database` é o SQLite, que vem com o Python. Um arquivo, transação real, chave estrangeira, índice, busca textual — e nada a instalar."},
 {"code": """adopt Arcane.Database as Banco

db := Banco.connect("loja.db")      // ou Banco.memory(), para teste

Banco.create_table(db, "produtos", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "sku": "TEXT NOT NULL UNIQUE",
    "nome": "TEXT NOT NULL",
    "preco": "REAL NOT NULL CHECK (preco >= 0)",
    "estoque": "INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0)"
})

Banco.upsert(db, "produtos", {"sku": "CAF-500", "nome": "Café 500g",
                              "preco": 32.9, "estoque": 20}, "sku")

out Banco.count(db, "produtos")""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Forge, para os outros cinco motores", "texto": "Este módulo é só SQLite. Para PostgreSQL, MySQL, MariaDB, MongoDB e Redis pela mesma interface, [`Arcane.Forge`](/docs/banco-de-dados) — também sem dependência, com um driver por protocolo."}},

 {"h2": "Projetos completos"},
 {"p": "As rotas abaixo não explicam funções: elas constroem um sistema, do schema ao relatório."},
 {"cards": [
   {"href": "/docs/tecnicas/banco-de-dados/crud", "title": "CRUD completo", "meta": "livraria, biblioteca, PDV, estoque", "desc": "Cinco sistemas com o mesmo esqueleto, e o que muda entre eles."},
   {"href": "/docs/tecnicas/banco-de-dados/relatorios", "title": "Relatórios e busca", "meta": "agregação, FTS5, plano", "desc": "O que toda tela de gestão pede, e a versão que aguenta cem mil linhas."},
   {"href": "/docs/tecnicas/banco-de-dados/migracoes", "title": "Migrações", "meta": "ida, volta e histórico", "desc": "Mudar o schema de um banco que tem dado dentro."}]},

 {"h2": "Parâmetros, sempre"},
 {"code": """// certo
Banco.query(db, "SELECT * FROM produtos WHERE sku = ?", [sku])

// errado, e é assim que um banco é apagado
Banco.query(db, $"SELECT * FROM produtos WHERE sku = '{sku}'")""", "lang": "df"},
 {"p": "Toda função deste módulo que aceita valor o passa por `?`. Nome de **coluna**, de tabela e de índice não pode ir por parâmetro — o SQLite não aceita — e por isso vai concatenado; para esses, o módulo **recusa** o que não parece um nome:"},
 {"code": """Banco.aggregate(db, "vendas", {"n": ["count", "*"]},
                order_by := "valor; DROP TABLE vendas")
// erro: 'valor; DROP TABLE vendas' nao e um nome valido de tabela ou coluna""", "lang": "df"},
 {"p": "Isso importa porque o `order_by` de uma listagem vem de fora — `?ordenar=nome`."},

 {"h2": "CRUD"},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`Banco.insert(db, tabela, vault)`", "insere; devolve o `id`"],
   ["`Banco.insert_many(db, tabela, cluster)`", "insere muitos"],
   ["`Banco.insert_or_ignore(db, tabela, vault)`", "não reclama se a chave existe; devolve `0`"],
   ["`Banco.upsert(db, tabela, vault, chaves)`", "insere **ou** atualiza; devolve `\"inserido\"`/`\"atualizado\"`"],
   ["`Banco.upsert_many(db, tabela, cluster, chaves)`", "o mesmo, numa transação só"],
   ["`Banco.select(db, tabela, where, order_by, limit)`", "lê"],
   ["`Banco.query(db, sql, params)`", "SQL livre, como cluster de vaults"],
   ["`Banco.query_one(db, sql, params)`", "a primeira linha, ou `void`"],
   ["`Banco.update(db, tabela, vault, where)`", "altera; devolve quantas linhas"],
   ["`Banco.increment(db, tabela, coluna, delta, where)`", "`coluna = coluna + ?`, no banco"],
   ["`Banco.delete(db, tabela, where)`", "apaga"],
   ["`Banco.count(db, tabela, where)`", "conta"],
   ["`Banco.exists(db, tabela, where)`", "`yes`/`no`"],
   ["`Banco.paginate(db, tabela, pagina, por_pagina, …)`", "uma fatia, com o total e o número de páginas"]]}},

 {"h3": "A condição"},
 {"code": """{"id": 7}                       // id = 7
{"id": [1, 2, 3]}               // id IN (1, 2, 3)
{"preco": {"gte": 10}}          // preco >= 10
{"nome": {"like": "caf%"}}      // nome LIKE 'caf%'
{"nota": void}                  // nota IS NULL""", "lang": "text"},
 {"p": "Operadores: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `like`. Um cluster **vazio** não casa com nada — `IN ()` é erro de sintaxe no SQLite, e a resposta certa para \"nenhum dos valores\" é não casar com nada."},
 {"callout": {"tipo": "nota", "titulo": "`void` vira `IS NULL`", "texto": "`coluna = NULL` nunca é verdadeiro em SQL, nem quando a coluna é nula. Quem escreve `void` quer dizer \"está vazio\", e é isso que o módulo gera."}},

 {"h2": "Escrita que não duplica"},
 {"p": "O catálogo que chega por CSV toda noite, o cliente que se cadastra duas vezes, o produto que dois caixas lançam ao mesmo tempo:"},
 {"code": """Banco.upsert(db, "produtos", dados, "sku")      // "inserido" ou "atualizado"

r := Banco.upsert_many(db, "produtos", lote, "sku")
out $"{r["inseridos"]} novos, {r["atualizados"]} atualizados\"""", "lang": "df"},
 {"p": "As chaves de conflito precisam ter índice **UNIQUE** — é o SQLite que decide, não um `SELECT` antes do `INSERT`. A diferença importa: entre o `SELECT` e o `INSERT`, outra thread pode inserir a mesma chave, e o código \"confere e depois grava\" **perde a corrida** sem nada denunciando."},

 {"h2": "Transações"},
 {"code": """action vender(sku, quantos):
    action corpo():
        p := Banco.query_one(db, "SELECT * FROM produtos WHERE sku = ?", [sku])
        given p["estoque"] smaller quantos:
            trigger $"estoque insuficiente de {p["nome"]}"
        Banco.insert(db, "vendas", {"produto_id": p["id"],
                                    "quantidade": quantos,
                                    "valor": p["preco"] * quantos})
        Banco.increment(db, "produtos", "estoque", -quantos, {"id": p["id"]})
        yield p["preco"] * quantos

    yield Banco.transacao(db, corpo)""", "lang": "df"},
 {"p": "Erro **desfaz tudo**. É a peça que falta num PDV: gravar a venda, baixar o estoque e lançar o pagamento são três escritas que precisam valer juntas."},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`Banco.transacao(db, acao)`", "roda a ação; erro desfaz; devolve o que ela devolveu"],
   ["`Banco.savepoint(db, nome, acao)`", "uma transação **dentro** de outra"],
   ["`Banco.in_transaction(db)`", "estamos dentro de uma agora?"],
   ["`Banco.begin` · `commit` · `rollback`", "à mão — prefira `transacao`"]]}},
 {"p": "Uma `transacao` dentro de outra vira savepoint sozinha: o SQLite não aninha `BEGIN`, mas aninha savepoint. O savepoint desfaz **só a parte dele** — um item sem estoque não precisa derrubar a venda inteira."},
 {"callout": {"tipo": "atencao", "titulo": "Por que não `begin` à mão", "texto": "`begin` obriga a não esquecer o `rollback` em **nenhum** caminho de saída, inclusive no que dispara. Esquecer deixa a conexão travada para as outras threads — e o sintoma é um servidor que fica lento sem motivo aparente."}},

 {"h3": "`increment`, e não ler-somar-escrever"},
 {"code": """// errado, e o erro é silencioso
p := Banco.query_one(db, "SELECT estoque FROM produtos WHERE id = ?", [7])
Banco.update(db, "produtos", {"estoque": p["estoque"] - 1}, {"id": 7})

// certo: a soma é do banco, sob a trava da linha
Banco.increment(db, "produtos", "estoque", -1, {"id": 7})""", "lang": "df"},
 {"p": "Dois caixas vendendo o mesmo item ao mesmo tempo leem 10, os dois escrevem 9, e uma unidade desaparece do controle **sem nenhum erro aparecer**. Foi medido: quatro threads fazendo 200 incrementos cada perdem cerca de um terço na forma ingênua."},

 {"h2": "Schema"},
 {"code": """Banco.create_table(db, nome, esquema)
Banco.drop_table(db, nome)
Banco.table_exists(db, nome)      Banco.tables(db)
Banco.columns(db, tabela)         Banco.table_info(db, tabela)
Banco.add_column(db, tabela, nome, tipo)
Banco.create_index(db, tabela, colunas, unique := yes, name := "idx_x")
Banco.drop_index(db, nome)
Banco.schema_sql(db)              // o CREATE como o SQLite o guarda
Banco.foreign_keys(db, tabela)    // as chaves, legíveis
Banco.check_foreign_keys(db)      // as linhas que apontam para o nada""", "lang": "df"},
 {"p": "`PRAGMA foreign_keys=ON` já vem ligado na conexão. Ele impede **novas** violações, mas não conserta as que entraram antes — um banco importado de CSV costuma ter várias, e `check_foreign_keys` é o que as encontra."},

 {"h2": "Construtor de consultas"},
 {"code": """Banco.builder(db, "vendas")
    .select("vendedor", "valor")
    .where("valor", ">", 100)
    .and_where("mes", "=", "2026-03")
    .order_by("valor", "DESC")
    .limit(20)
    .get()""", "lang": "df"},
 {"p": "E `where_in`, `where_null`, `where_between`, `where_like`, `join`, `left_join`, `group_by`, `having`, `offset`. Os terminais: `get`, `first`, `count`, `sum`, `avg`, `max`, `min`, `insert`, `update`, `delete` — e `to_sql`, que mostra o SQL sem executar."},

 {"h2": "Diagnóstico"},
 {"code": """Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
// {"varre_tabela": yes, "aviso": "le a tabela inteira: SCAN vendas", …}

Banco.indexes(db, "vendas")     // com as colunas de cada um
Banco.stats(db)                 // tabelas, linhas, índices, bytes
Banco.integrity(db)             // o 'integrity_check' do SQLite""", "lang": "df"},
 {"p": "A linha que importa no `explain` é a que diz **SCAN** em vez de SEARCH: SCAN lê a tabela inteira, e num cadastro de 200 mil linhas é a diferença entre 2 ms e 2 s. A resposta quase sempre é um índice."},

 {"h2": "Entrada e saída"},
 {"code": """Banco.export_csv(db, "vendas", "vendas.csv")
Banco.export_json(db, "vendas", "vendas.json")
Banco.import_csv(db, "vendas", "vendas.csv")
Banco.import_json(db, "vendas", "vendas.json")
Banco.backup(db, "copia.db")      // cópia consistente, com o banco em uso
Banco.vacuum(db)                  // devolve o espaço das linhas apagadas""", "lang": "df"},

 {"h2": "Concorrência"},
 {"p": "A conexão é utilizável de **várias threads** — o acesso é serializado por uma trava, e o modo `WAL` fica ligado. Sem isso, a primeira consulta de qualquer servidor estoura com `SQLite objects created in a thread can only be used in that same thread`."},
 {"p": "O que a trava **não** protege é a lógica de quem lê-e-depois-escreve. Para isso, `increment`, `upsert` e `transacao`."},

 {"h2": "Testar"},
 {"code": """db := Banco.memory()     // em memória, some ao terminar""", "lang": "df"},
 {"p": "E, para que um teste que grava não seja visto pelo seguinte, [`Crucible.banco(db)`](/docs/tecnicas/instantaneos) abre uma transação e a desfaz no fim de cada trial."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/tecnicas/banco-de-dados/crud",
"title": "Um CRUD completo",
"description": "Livraria, biblioteca, comércio, estoque e PDV — o mesmo esqueleto, e o que muda entre eles.",
"blocos": [
 {"p": "Os cinco sistemas que as pessoas pedem — livraria, biblioteca, loja, controle de estoque, PDV — têm o **mesmo esqueleto**. Esta página o constrói inteiro, e depois mostra o que muda em cada um."},
 {"p": "O código roda: ele é o [exercício 219](/docs/exercicios/29-banco-e-crud) mais o [220](/docs/exercicios/29-banco-e-crud), que se verificam a cada execução da suíte."},

 {"h2": "1. O schema, onde a regra mora"},
 {"code": """adopt Arcane.Database as Banco

db := Banco.connect("livraria.db")

Banco.create_table(db, "autores", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "nome": "TEXT NOT NULL UNIQUE"
})

Banco.create_table(db, "livros", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "isbn": "TEXT NOT NULL UNIQUE",
    "titulo": "TEXT NOT NULL",
    "autor_id": "INTEGER NOT NULL REFERENCES autores(id)",
    "preco": "REAL NOT NULL CHECK (preco >= 0)",
    "estoque": "INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0)"
})

Banco.create_index(db, "livros", ["autor_id"])
Banco.create_index(db, "livros", ["titulo"])""", "lang": "df"},
 {"table": {"head": ["Na memória", "No banco"], "rows": [
   ["`SELECT` e depois `INSERT`", "`UNIQUE` + `upsert`"],
   ["conferir estoque e subtrair", "`estoque = estoque - ?`"],
   ["verificar se o autor tem livro", "`REFERENCES autores(id)`"],
   ["validar preço ≥ 0 no código", "`CHECK (preco >= 0)`"]]}},
 {"p": "A coluna da esquerda funciona até dois processos rodarem ao mesmo tempo. A da direita é o banco decidindo, sob a trava dele — e ele decide igual em todos os caminhos do código, inclusive nos que ninguém lembrou de validar."},
 {"callout": {"tipo": "dica", "titulo": "Índice em toda chave estrangeira", "texto": "O SQLite cria índice para `UNIQUE` e `PRIMARY KEY`, mas **não** para `REFERENCES`. Sem ele, cada `JOIN` e cada `DELETE` na tabela-mãe varre a tabela-filha inteira."}},

 {"h2": "2. Create"},
 {"code": """action autor(nome):
    // Cadastrar o mesmo autor duas vezes não é erro do usuário,
    // e ele não precisa ver um.
    Banco.insert_or_ignore(db, "autores", {"nome": nome})
    yield Banco.query_one(db, "SELECT id FROM autores WHERE nome = ?",
                          [nome])["id"]

action cadastrar(isbn, titulo, nome_autor, preco, estoque):
    yield Banco.upsert(db, "livros", {
        "isbn": isbn, "titulo": titulo, "autor_id": autor(nome_autor),
        "preco": preco, "estoque": estoque
    }, "isbn")

cadastrar("978-1", "Duna", "Frank Herbert", 79.9, 4)     // "inserido"
cadastrar("978-1", "Duna (ed. especial)", "Frank Herbert", 99.9, 6)
// "atualizado" — e o autor não duplicou""", "lang": "df"},

 {"h2": "3. Read, com paginação e junção"},
 {"code": """action pagina_de_livros(numero, tamanho, busca):
    given busca is not "":
        yield {"itens": Banco.search(db, "livros", busca, limit := tamanho),
               "pagina": 1, "paginas": 1, "total": 0,
               "tem_anterior": no, "tem_proxima": no}
    yield Banco.paginate(db, "livros", numero, tamanho,
                         order_by := "titulo")

action catalogo():
    yield Banco.query(db, \"\"\"
        SELECT l.isbn, l.titulo, a.nome AS autor, l.preco, l.estoque
        FROM livros l
        JOIN autores a ON a.id = l.autor_id
        ORDER BY l.titulo
    \"\"\")""", "lang": "df"},
 {"p": "`Banco.paginate` devolve o que a tela precisa, e não só a fatia:"},
 {"code": """{
    "itens": [...],       "pagina": 2,      "por_pagina": 20,
    "total": 143,         "paginas": 8,
    "tem_anterior": yes,  "tem_proxima": yes
}""", "lang": "text"},
 {"p": "Sem `total` e `paginas` a tela não sabe desenhar a paginação, e calcular isso à mão é a mesma consulta escrita duas vezes. `por_pagina` tem teto de 500: o número vem de fora numa rota, e `?por_pagina=1000000` é como se derruba um servidor sem exploit."},

 {"h2": "4. Update e Delete"},
 {"code": """Banco.update(db, "livros", {"preco": 89.9}, {"isbn": "978-1"})   // uma linha
Banco.delete(db, "livros", {"isbn": "978-3"})                    // uma linha

// e o banco recusa apagar um autor que tem livro
monitor:
    Banco.delete(db, "autores", {"nome": "Frank Herbert"})
handle Error as e:
    out "recusado pela chave estrangeira"      // FOREIGN KEY constraint""", "lang": "df"},

 {"h2": "5. A venda, como uma unidade"},
 {"p": "É aqui que um exemplo se separa de um sistema. Gravar a venda, gravar os itens e baixar o estoque de cada um precisam valer **juntos**:"},
 {"code": """action registrar_venda(carrinho, caixa):
    action corpo():
        total := 0.0
        linhas := []
        cycle item in carrinho:
            p := Banco.query_one(db, "SELECT * FROM livros WHERE isbn = ?",
                                 [item["isbn"]])
            given p is void:
                trigger $"ISBN {item["isbn"]} nao existe"
            given p["estoque"] smaller item["quantidade"]:
                trigger $"estoque insuficiente de {p["titulo"]}"
            total += p["preco"] * item["quantidade"]
            linhas.append({"livro": p, "quantidade": item["quantidade"]})

        venda_id := Banco.insert(db, "vendas", {
            "total": round(total, 2), "caixa": caixa,
            "quando": Time.now().iso()})

        cycle linha in linhas:
            Banco.insert(db, "itens", {
                "venda_id": venda_id, "livro_id": linha["livro"]["id"],
                "quantidade": linha["quantidade"],
                "preco_unitario": linha["livro"]["preco"]})
            Banco.increment(db, "livros", "estoque",
                            -linha["quantidade"],
                            {"id": linha["livro"]["id"]})
        yield {"id": venda_id, "total": round(total, 2)}

    yield Banco.transacao(db, corpo)""", "lang": "df"},
 {"code": """       grava a venda   ✓
       grava o item 1  ✓
       baixa estoque 1 ✓
       grava o item 2  ✗  ← sem estoque
       ────────────────────
       sem transação:   a venda existe, com um item, e o estoque do
                        primeiro item foi baixado
       com transação:   nada aconteceu""", "lang": "text"},
 {"p": "Ninguém descobre o primeiro caso até o inventário — e aí não há como saber quais vendas foram afetadas."},

 {"h3": "Quando a regra é \"vende o que tem\""},
 {"code": """action tentar_item():
    p := Banco.query_one(db, "SELECT * FROM livros WHERE isbn = ?", [isbn])
    given p is void or p["estoque"] smaller pedido:
        trigger "sem estoque"
    Banco.insert(db, "itens", { … })
    Banco.increment(db, "livros", "estoque", -pedido, {"id": p["id"]})
    yield p["preco"] * pedido

monitor:
    total += Banco.savepoint(db, "item", tentar_item)
handle Error as e:
    recusados.append(isbn)""", "lang": "df"},
 {"p": "O savepoint desfaz só a parte dele: o item recusado não sai do estoque, e a venda continua."},

 {"h2": "O mesmo esqueleto, cinco sistemas"},
 {"table": {"head": ["Sistema", "A tabela do meio é", "O que muda"], "rows": [
   ["**Livraria**", "`vendas` + `itens`", "o que foi escrito acima"],
   ["**Biblioteca**", "`emprestimos`", "não há preço; há `devolver_em` e o estoque é *exemplares disponíveis*. Um empréstimo é `increment(-1)`; a devolução, `increment(+1)`"],
   ["**Comércio**", "`pedidos` + `itens`", "acrescenta `clientes`, `enderecos` e um `status` que caminha (`aberto → pago → enviado`)"],
   ["**Estoque**", "`movimentos`", "toda alteração é uma **linha**, nunca um `update`: entrada, saída, ajuste, perda. O saldo é a soma — e aí ele é auditável"],
   ["**PDV**", "`vendas` + `itens` + `pagamentos`", "uma venda tem N formas de pagamento, e a soma delas precisa fechar com o total"]]}},

 {"h3": "Estoque: por que movimento e não saldo"},
 {"code": """Banco.create_table(db, "movimentos", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "produto_id": "INTEGER NOT NULL REFERENCES produtos(id)",
    "tipo": "TEXT NOT NULL CHECK (tipo IN ('entrada','saida','ajuste','perda'))",
    "quantidade": "INTEGER NOT NULL",
    "motivo": "TEXT NOT NULL DEFAULT ''",
    "quem": "TEXT NOT NULL",
    "quando": "TEXT NOT NULL"
})

action saldo(produto_id):
    linha := Banco.query_one(db, \"\"\"
        SELECT COALESCE(SUM(CASE WHEN tipo IN ('entrada','ajuste')
                                 THEN quantidade ELSE -quantidade END), 0)
               AS saldo
        FROM movimentos WHERE produto_id = ?
    \"\"\", [produto_id])
    yield linha["saldo"]""", "lang": "df"},
 {"p": "Um `UPDATE produtos SET estoque = ?` é mais rápido e não responde à pergunta que sempre aparece: *por que o saldo está assim?* Com movimento, a resposta é um `SELECT`. A coluna `estoque` continua existindo como **cache** do saldo, mantida por `increment` na mesma transação do movimento."},

 {"h3": "PDV: o pagamento precisa fechar"},
 {"code": """action fechar_venda(venda_id, pagamentos):
    action corpo():
        v := Banco.query_one(db, "SELECT total FROM vendas WHERE id = ?",
                             [venda_id])
        somado := pagamentos >> morph p: p["valor"] >> distill a, x: a + x 0.0
        given round(somado, 2) is not round(v["total"], 2):
            trigger $"pagamento de {somado} nao fecha com o total {v["total"]}"
        cycle p in pagamentos:
            Banco.insert(db, "pagamentos", {
                "venda_id": venda_id, "forma": p["forma"],
                "valor": p["valor"]})
        Banco.update(db, "vendas", {"status": "paga"}, {"id": venda_id})
        yield somado

    yield Banco.transacao(db, corpo)""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Dinheiro não é `Float`", "texto": "`0.1 + 0.2` dá `0.30000000000000004`, e um centavo que soma errado numa linha soma errado num milhão. Para valor conferido por pessoa, [`Arcane.Decimal`](/docs/tecnicas/decimal) — e guarde no banco como **inteiro de centavos** ou como `TEXT`, nunca como `REAL`."}},

 {"h2": "Ligando na tela"},
 {"p": "O mesmo banco serve os três: uma API REST, um painel e uma CLI."},
 {"code": """adopt Kiln
adopt Arcane.Vitrine as V

// API REST — sete rotas de uma vez
Kiln.resource(app, "livros", {
    "index":   lambda req: Banco.paginate(db, "livros",
                                          int(req["query"]["pagina"] ?? "1"),
                                          20, order_by := "titulo"),
    "show":    lambda req: Banco.query_one(
                   db, "SELECT * FROM livros WHERE id = ?",
                   [req["params"]["id"]]) ?? Kiln.status(404),
    "create":  lambda req: Banco.insert(db, "livros", req["body"]),
    "update":  lambda req: Banco.update(db, "livros", req["body"],
                                        {"id": req["params"]["id"]}),
    "destroy": lambda req: Banco.delete(db, "livros",
                                        {"id": req["params"]["id"]})
})""", "lang": "df"},
 {"p": "Para o painel, [um projeto de análise completo](/docs/vitrine/projeto) lê deste mesmo banco."},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/tecnicas/banco-de-dados/relatorios", "title": "Relatórios e busca", "desc": "Agregação, FTS5 e o plano de consulta."},
   {"href": "/docs/tecnicas/banco-de-dados/migracoes", "title": "Migrações", "desc": "Mudar o schema de um banco que tem dado dentro."},
   {"href": "/docs/vitrine/projeto", "title": "Um painel sobre este banco", "desc": "Análise de dados completa, do SQL ao gráfico."},
   {"href": "/docs/exercicios/29-banco-e-crud", "title": "Os exercícios", "desc": "Os quatro que se verificam a cada execução."}]},
]},
]

PAGINAS += [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/tecnicas/banco-de-dados/relatorios",
"title": "Relatórios e busca",
"description": "Agregação sem escrever SQL, busca textual com FTS5 e o plano de consulta que mostra o índice que falta.",
"blocos": [
 {"p": "Três coisas que toda tela de gestão pede. As três têm uma versão ingênua que funciona com cem linhas e morre com cem mil."},

 {"h2": "Relatório agrupado"},
 {"code": """adopt Arcane.Database as Banco

por_vendedor := Banco.aggregate(db, "vendas", {
    "receita": ["sum", "valor"],
    "vendas":  ["count", "*"],
    "ticket":  ["avg", "valor"]
}, group_by := "vendedor", order_by := "receita DESC")""", "lang": "df"},
 {"code": """[{"vendedor": "ana",   "receita": 4820.0, "vendas": 30, "ticket": 160.6},
 {"vendedor": "bruno", "receita": 3910.0, "vendas": 27, "ticket": 144.8}]""", "lang": "text"},
 {"p": "As colunas do `group_by` saem **junto** com os agregados — que é o que um gráfico precisa. Dois grupos ao mesmo tempo também:"},
 {"code": """Banco.aggregate(db, "vendas", {"receita": ["sum", "valor"]},
                group_by := ["categoria", "vendedor"])

// com filtro
Banco.aggregate(db, "vendas", {"total": ["sum", "valor"]},
                where := {"mes": "2026-03", "valor": {"gte": 50}})

// o atalho que mais se pede
Banco.group_count(db, "vendas", "categoria")
// [{"categoria": "bebida", "quantidade": 30}, …]""", "lang": "df"},
 {"p": "Aceita `count`, `sum`, `avg`, `min`, `max` e `total`. A lista é fechada **de propósito**: o nome da função vai cru para o SQL, e aceitar qualquer texto ali seria injeção pela porta da frente. Para outra agregação, escreva o SQL com `Banco.query` — e aí a responsabilidade é de quem escreveu."},
 {"callout": {"tipo": "atencao", "titulo": "O `order_by` vem de fora", "texto": "Numa listagem, `?ordenar=nome` chega do cliente, e nome de coluna não pode ir por parâmetro. `Banco.aggregate` confere pedaço por pedaço e recusa `\"valor; DROP TABLE vendas\"`; a direção também — só `ASC` e `DESC`."}},

 {"h2": "Busca textual"},
 {"code": """-- o que quase todo mundo escreve
SELECT * FROM produtos WHERE nome LIKE '%cafe%'""", "lang": "sql"},
 {"p": "`LIKE` com `%` na frente **não usa índice nenhum**: ele lê a tabela inteira, sempre. O FTS5 do SQLite usa índice invertido e ordena por relevância."},
 {"code": """Banco.create_search(db, "produtos", ["nome", "categoria"])

Banco.search(db, "produtos", "merce")        // acha "mercearia"
Banco.search(db, "produtos", "cafe 500", limit := 10)""", "lang": "df"},
 {"table": {"head": ["Detalhe", "Por quê"], "rows": [
   ["prefixo na **última** palavra", "quem digita `livr` espera achar `livro` antes de terminar de escrever"],
   ["o índice se mantém em dia, por gatilhos", "sem eles ele envelhece em silêncio e a busca deixa de achar o que foi cadastrado depois — o pior defeito possível numa busca"],
   ["devolve a linha da tabela **original**", "quem busca quer o produto, não o índice"],
   ["o termo é escapado", "`MATCH` tem sintaxe própria: um termo com aspas ou `AND` quebraria a consulta ou mudaria o que ela procura"],
   ["o `LIMIT` é aplicado antes do `JOIN`", "com um milhão de linhas, junta-se vinte e não um milhão"]]}},
 {"callout": {"tipo": "nota", "titulo": "Um bug que valeu a lição", "texto": "A primeira versão montava a consulta como `\"livr*\"` — com o `*` **dentro** das aspas, onde ele é um caractere literal. A sintaxe de prefixo do FTS5 é `\"livr\"*`. A busca devolvia lista vazia, calada, e nenhum erro apareceu em lugar nenhum."}},
 {"p": "As quatro tabelas-sombra que o FTS5 cria para si (`_data`, `_idx`, `_docsize`, `_config`) não aparecem em `Banco.stats` — contá-las faria um banco de duas tabelas parecer ter dez."},

 {"h2": "O plano da consulta"},
 {"code": """sem := Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
// {"varre_tabela": yes,
//  "aviso": "le a tabela inteira: SCAN vendas",
//  "passos": ["SCAN vendas"]}

Banco.create_index(db, "vendas", ["vendedor"])

com := Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
// {"varre_tabela": no, "aviso": "", "passos": ["SEARCH vendas USING INDEX …"]}""", "lang": "df"},
 {"p": "A linha que importa é a que diz **SCAN** em vez de SEARCH. SCAN lê a tabela inteira; num cadastro de 200 mil linhas é a diferença entre 2 ms e 2 s, e a resposta quase sempre é um índice."},
 {"code": """indices := Banco.indexes(db, "vendas")
// [{"nome": "idx_vendas_vendedor", "tabela": "vendas",
//   "colunas": ["vendedor"], "automatico": no}, …]""", "lang": "df"},
 {"p": "`automatico: yes` é o índice que o SQLite criou sozinho para um `UNIQUE` ou `PRIMARY KEY` — ele existe, e não foi você que pediu."},

 {"h3": "Onde pôr índice"},
 {"table": {"head": ["Situação", "Índice"], "rows": [
   ["toda chave estrangeira", "sempre — o SQLite **não** cria"],
   ["a coluna do `WHERE` de uma tela de listagem", "sim"],
   ["a coluna do `ORDER BY` de uma listagem grande", "sim; ele evita a ordenação"],
   ["as duas juntas, na mesma consulta", "um índice **composto**, na ordem `WHERE` → `ORDER BY`"],
   ["uma coluna com três valores possíveis", "não — o índice não separa nada"],
   ["uma tabela de cem linhas", "não — varrer é mais rápido"]]}},
 {"callout": {"tipo": "dica", "titulo": "Índice custa escrita", "texto": "Cada índice é uma árvore a atualizar em todo `INSERT` e `UPDATE`. Numa tabela de log com dez índices, gravar fica mais lento que ler. Meça com `explain` antes de acrescentar, e apague o que não aparece em nenhum plano."}},

 {"h2": "Um retrato do banco"},
 {"code": """e := Banco.stats(db)
// {"caminho": "loja.db", "bytes": 4915200, "total_de_linhas": 182044,
//  "tabelas": [{"tabela": "vendas", "linhas": 180000,
//               "colunas": 7, "indices": 3}, …]}

Banco.integrity(db)          // {"ok": yes, "problemas": []}
Banco.check_foreign_keys(db) // as linhas que apontam para o nada""", "lang": "df"},
 {"p": "`check_foreign_keys` importa num banco que recebeu importação: `PRAGMA foreign_keys=ON` impede novas violações, mas não conserta as que entraram antes — e elas só aparecem quando alguém tenta usar o dado."},

 {"h2": "Ligando num painel"},
 {"code": """adopt Arcane.Vitrine as V

mark @V.cache(validade := 60)
action receita_por_mes():
    yield Banco.aggregate(db, "vendas", {"receita": ["sum", "valor"]},
                          group_by := "mes", order_by := "mes")

action painel():
    V.titulo("Vendas")
    V.grafico_barras(receita_por_mes(), x := "mes", y := "receita")
    V.frame(Banco.group_count(db, "vendas", "vendedor"))""", "lang": "df"},
 {"p": "O `mark @V.cache` não é opcional aqui: o programa de um painel roda inteiro a cada clique, e sem cache mover um deslizante refaz a agregação. Ver [o projeto completo](/docs/vitrine/projeto)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/tecnicas/banco-de-dados/migracoes",
"title": "Migrações",
"description": "Mudar o schema de um banco que tem dado dentro — com ida, volta e histórico.",
"blocos": [
 {"p": "Num sistema em produção o banco tem dado dentro. Trocar o `create_table` no código não muda a tabela que já existe, e apagar e recriar perde tudo."},

 {"h2": "A lista, com ida e volta"},
 {"code": """steady MIGRACOES := [
    {
        "version": 1,
        "description": "clientes",
        "up": \"\"\"
            CREATE TABLE clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL
            );
        \"\"\",
        "down": "DROP TABLE clientes;"
    },
    {
        "version": 2,
        "description": "e-mail do cliente",
        "up":   "ALTER TABLE clientes ADD COLUMN email TEXT;",
        "down": "ALTER TABLE clientes DROP COLUMN email;"
    }
]

Banco.migrate(db, MIGRACOES)      // aplica o que falta; devolve quantas""", "lang": "df"},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`Banco.migrate(db, lista)`", "aplica as que faltam, em ordem de versão"],
   ["`Banco.migrations_applied(db)`", "versão, descrição e quando"],
   ["`Banco.rollback_migration(db, lista)`", "desfaz **uma**"],
   ["`Banco.rollback_migration(db, lista, ate := 3)`", "desfaz até a 3, que **fica**"],
   ["`Banco.schema_sql(db)`", "o schema como o SQLite o guarda"]]}},

 {"h2": "É idempotente, e isso é o ponto"},
 {"p": "`migrate` grava numa tabela `_migrations` o que já aplicou, e pula essas. Rodar de novo devolve `0`. É o que permite chamá-lo no começo de **todo** processo:"},
 {"code": """db := Banco.connect("dados.db")
Banco.migrate(db, MIGRACOES)
V.subir(porta := 8501)""", "lang": "df"},
 {"p": "Sem isso, subir o servidor duas vezes quebraria na segunda — e alguém acabaria escrevendo um script de migração que se roda à mão, que é o mesmo problema com mais passos."},

 {"h2": "Toda migração deveria ter `down`"},
 {"p": "Desfazer acontece no meio de um incidente — que é quando ninguém tem paciência para editar o banco à mão. Duas escolhas deliberadas:"},
 {"callout": {"tipo": "atencao", "titulo": "Por padrão desfaz uma", "texto": "Desfazer em cascata por acidente é perda de dado, e é a diferença entre \"corrigi a última\" e \"apaguei o banco\". Para ir mais fundo, diga explicitamente até onde: `ate := 3`."}},
 {"callout": {"tipo": "atencao", "titulo": "Sem `down`, o rollback para com erro", "texto": "Pular em silêncio deixaria o banco num estado que **nenhuma versão descreve** — nem a anterior, nem a nova. Descobrir isso depois é pior que o erro agora."}},

 {"h2": "O dado sobrevive"},
 {"code": """Banco.insert(db, "clientes", {"nome": "Ana", "email": "ana@exemplo.br"})

steady MAIS := [...MIGRACOES, {
    "version": 3, "description": "telefone",
    "up":   "ALTER TABLE clientes ADD COLUMN telefone TEXT DEFAULT '';",
    "down": "ALTER TABLE clientes DROP COLUMN telefone;"
}]

Banco.migrate(db, MAIS)                  // uma aplicada
Banco.count(db, "clientes")              // o dado continua lá""", "lang": "df"},

 {"h2": "As migrações que exigem cuidado"},
 {"table": {"head": ["Mudança", "Como fazer"], "rows": [
   ["acrescentar coluna", "`ALTER TABLE … ADD COLUMN` — barato, e com `DEFAULT` não trava"],
   ["renomear coluna", "`ALTER TABLE … RENAME COLUMN` (SQLite 3.25+)"],
   ["mudar tipo de coluna", "tabela nova, `INSERT … SELECT`, `DROP`, `RENAME` — o SQLite não altera tipo"],
   ["acrescentar `NOT NULL` sem `DEFAULT`", "impossível com dado existente: preencha antes, em duas migrações"],
   ["acrescentar índice numa tabela grande", "trava a escrita enquanto constrói; faça na janela de manutenção"],
   ["apagar coluna", "`DROP COLUMN` (3.35+), e é **irreversível** — o `down` não recupera o dado"]]}},
 {"callout": {"tipo": "dica", "titulo": "Duas migrações, não uma", "texto": "Para tornar uma coluna obrigatória: primeiro acrescente nula e preencha o que falta; depois, numa segunda migração, imponha o `NOT NULL`. Uma migração que precisa que o dado já esteja certo falha na primeira máquina onde ele não está."}},

 {"h2": "Antes de migrar em produção"},
 {"code": """Banco.backup(db, $"antes-da-v{proxima}.db")
Banco.migrate(db, MIGRACOES)
Banco.integrity(db)""", "lang": "df"},
 {"p": "`backup` faz uma cópia consistente **com o banco em uso** — é a API de backup do SQLite, não um `cp`. Um `cp` de um banco sendo escrito copia um arquivo pela metade."},
 {"p": "E o SQLite não desfaz DDL dentro de transação de forma confiável em todas as versões: o backup é a rede de segurança real, não o `rollback`."},

 {"h2": "Comparar dois ambientes"},
 {"code": """// em produção
IO.write("schema-prod.sql", Banco.schema_sql(prod))
// no seu
IO.write("schema-dev.sql", Banco.schema_sql(dev))""", "lang": "df"},
 {"p": "Um `diff` entre os dois mostra o que falta migrar. É o jeito mais direto de descobrir que alguém alterou o banco à mão."},
]},
]
