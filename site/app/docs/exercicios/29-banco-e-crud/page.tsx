// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "29 · Banco e CRUD",
  description: "4 exercícios: transações, upsert, busca textual e paginação.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 29`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[219](#219-um-crud-completo-com-o-banco-fazendo-o-trabalho)", "**Um CRUD completo, com o banco fazendo o trabalho**", ""], ["[220](#220-um-pdv-a-venda-inteira-ou-nenhuma)", "**Um PDV: a venda inteira, ou nenhuma**", ""], ["[221](#221-relatorio-busca-e-o-indice-que-falta)", "**Relatorio, busca e o indice que falta**", ""], ["[222](#222-migracoes-mudar-o-schema-sem-perder-dado)", "**Migracoes: mudar o schema sem perder dado**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "219 · Um CRUD completo, com o banco fazendo o trabalho"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 219 — Um CRUD completo, com o banco fazendo o trabalho
//
//  Uma livraria: cadastro, listagem paginada, busca, edicao e
//  exclusao. O que separa um exemplo de um sistema e onde a regra
//  mora — e aqui ela mora no BANCO, nao na memoria do processo.
// ════════════════════════════════════════════════════════════

adopt Arcane.Database as Banco

db := Banco.memory()

// ── 1. O schema, com as restricoes que protegem o dado ──────
//
// 'UNIQUE' no ISBN nao e enfeite: e o que permite 'upsert' e o que
// impede o mesmo livro entrar duas vezes quando dois caixas cadastram
// ao mesmo tempo. Conferir com um SELECT antes do INSERT perde essa
// corrida.

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

// ── 2. Create ───────────────────────────────────────────────

action autor(nome):
    // 'insert_or_ignore' + busca: cadastrar o mesmo autor duas vezes
    // nao e erro do usuario, e ele nao precisa ver um.
    Banco.insert_or_ignore(db, "autores", {"nome": nome})
    yield Banco.query_one(db, "SELECT id FROM autores WHERE nome = ?", [nome])["id"]

action cadastrar(isbn, titulo, nome_autor, preco, estoque):
    yield Banco.upsert(db, "livros", {
            "isbn": isbn, "titulo": titulo, "autor_id": autor(nome_autor),
            "preco": preco, "estoque": estoque
        }, "isbn")

assert cadastrar("978-1", "Duna", "Frank Herbert", 79.9, 4) is "inserido"
assert cadastrar("978-2", "O Messias de Duna", "Frank Herbert", 69.9, 2) is "inserido"
assert cadastrar("978-3", "Neuromancer", "William Gibson", 64.9, 3) is "inserido"

// o mesmo ISBN ATUALIZA, e o autor nao duplicou
assert cadastrar("978-1", "Duna (ed. especial)", "Frank Herbert", 99.9, 6) is "atualizado"
assert Banco.count(db, "livros") is 3
assert Banco.count(db, "autores") is 2

// ── 3. Read, com juncao e paginacao ─────────────────────────

action pagina_de_livros(numero, tamanho):
    yield Banco.paginate(db, "livros", numero, tamanho, order_by := "titulo")

p := pagina_de_livros(1, 2)
assert p["total"] is 3
assert p["paginas"] is 2
assert len(p["itens"]) is 2
assert p["tem_proxima"]
assert not p["tem_anterior"]

segunda := pagina_de_livros(2, 2)
assert len(segunda["itens"]) is 1
assert not segunda["tem_proxima"]
// a segunda pagina nao repete a primeira
assert segunda["itens"][0]["titulo"] is not p["itens"][0]["titulo"]

// com o nome do autor, que esta em outra tabela
action com_autor():
    yield Banco.query(db, """
        SELECT l.titulo, a.nome AS autor, l.preco
        FROM livros l JOIN autores a ON a.id = l.autor_id
        ORDER BY l.titulo
    """)

catalogo := com_autor()
assert len(catalogo) is 3
assert catalogo[0]["autor"] is "Frank Herbert"

// ── 4. Update ───────────────────────────────────────────────

assert Banco.update(db, "livros", {"preco": 89.9}, {"isbn": "978-1"}) is 1
assert Banco.query_one(db, "SELECT preco FROM livros WHERE isbn = '978-1'")["preco"] is 89.9

// ── 5. Delete, e o que a chave estrangeira impede ───────────

assert Banco.delete(db, "livros", {"isbn": "978-3"}) is 1
assert Banco.count(db, "livros") is 2

// apagar um autor que tem livro e recusado pelo BANCO
monitor:
    Banco.delete(db, "autores", {"nome": "Frank Herbert"})
    assert no  // nao deveria chegar aqui
handle Error as e:
    assert "FOREIGN KEY" in e.message or "constraint" in e.message

// ── 6. O que o CHECK protege ────────────────────────────────

monitor:
    Banco.insert(db, "livros", {
            "isbn": "978-9", "titulo": "Impossivel",
            "autor_id": 1, "preco": -10.0, "estoque": 0})
    assert no
handle Error as e:
    assert "CHECK" in e.message or "constraint" in e.message

out "219 ok — crud completo"`, lang: 'df', title: `exercicios/29-banco-e-crud/219_crud_completo.df` },
  {"h3": "Conceitos"},
  { code: `adopt Arcane.Database as Banco

Banco.upsert(db, "livros", dados, "isbn")     // insere ou atualiza
Banco.insert_or_ignore(db, "autores", dados)  // não reclama se já existe
Banco.paginate(db, "livros", 2, 20, order_by := "titulo")
Banco.update(db, "livros", {"preco": 89.9}, {"isbn": "978-1"})
Banco.delete(db, "livros", {"isbn": "978-3"})`, lang: 'df' },
  {"h3": "Por que a regra vai no banco"},
  {"table": {"head": ["Na memória", "No banco"], "rows": [["`SELECT` e depois `INSERT`", "`UNIQUE` + `upsert`"], ["conferir estoque e subtrair", "`estoque = estoque - ?`"], ["verificar se o autor tem livro", "`REFERENCES autores(id)`"], ["validar preço ≥ 0 no código", "`CHECK (preco >= 0)`"]]}},
  {"p": "A coluna da esquerda funciona até dois processos rodarem ao mesmo tempo. Entre o `SELECT` e o `INSERT` outra thread pode inserir a mesma chave, e o código \"confere e depois grava\" **perde a corrida** sem nada denunciando — o resultado é uma linha duplicada que ninguém sabe explicar."},
  {"p": "A da direita é o banco decidindo, sob a trava dele."},
  {"h3": "`UNIQUE` não é enfeite"},
  {"p": "É o que permite o `upsert`: sem um índice único no ISBN, o `ON CONFLICT` não tem em que se apoiar. Toda escrita idempotente começa por declarar qual é a identidade da linha."},
  {"h3": "Paginação"},
  {"p": "`Banco.paginate` devolve o que a tela precisa, e não só a fatia:"},
  { code: `{
    "itens": [...],       "pagina": 2,      "por_pagina": 20,
    "total": 143,         "paginas": 8,
    "tem_anterior": yes,  "tem_proxima": yes
}`, lang: 'df' },
  {"p": "Sem `total` e `paginas` a tela não sabe desenhar a paginação, e calcular isso à mão é a mesma consulta escrita duas vezes."},
  {"p": "`por_pagina` tem teto de 500: o número vem de fora numa rota, e `?por_pagina=1000000` é como se derruba um servidor sem exploit."},
  {"h3": "O que este exercício mostra"},
  {"table": {"head": ["Parte", "Ideia"], "rows": [["1", "o schema com `UNIQUE`, `REFERENCES` e `CHECK`"], ["2", "`upsert` — cadastrar duas vezes atualiza, não duplica"], ["3", "leitura paginada, e a junção que traz o nome do autor"], ["4", "`update` com condição"], ["5", "`delete`, e a chave estrangeira recusando apagar um autor com livro"], ["6", "o `CHECK` recusando preço negativo"]]}},
  {"h3": "Continua em"},
  {"p": "[220 — PDV e transações](220_pdv_e_transacoes.df), onde três escritas precisam valer juntas."},
  {"h2": "220 · Um PDV: a venda inteira, ou nenhuma"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 220 — Um PDV: a venda inteira, ou nenhuma
//
//  Gravar a venda, baixar o estoque e lancar o pagamento sao tres
//  escritas que precisam valer JUNTAS. Sem transacao, um erro no meio
//  deixa a venda registrada com o estoque intacto — e ninguem descobre
//  ate o inventario.
// ════════════════════════════════════════════════════════════

adopt Arcane.Database as Banco

db := Banco.memory()

Banco.create_table(db, "produtos", {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "sku": "TEXT NOT NULL UNIQUE",
        "nome": "TEXT NOT NULL",
        "preco": "REAL NOT NULL",
        "estoque": "INTEGER NOT NULL CHECK (estoque >= 0)"
    })
Banco.create_table(db, "vendas", {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "total": "REAL NOT NULL",
        "caixa": "TEXT NOT NULL",
        "quando": "TEXT NOT NULL"
    })
Banco.create_table(db, "itens", {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "venda_id": "INTEGER NOT NULL REFERENCES vendas(id)",
        "produto_id": "INTEGER NOT NULL REFERENCES produtos(id)",
        "quantidade": "INTEGER NOT NULL",
        "preco_unitario": "REAL NOT NULL"
    })

Banco.upsert_many(db, "produtos", [
        {"sku": "CAF-500", "nome": "Cafe 500g", "preco": 32.9, "estoque": 20},
        {"sku": "ACU-1KG", "nome": "Acucar 1kg", "preco": 5.49, "estoque": 50},
        {"sku": "LEI-1L", "nome": "Leite 1L", "preco": 6.9, "estoque": 2}
    ], "sku")

// ── 1. A venda, como uma unidade ────────────────────────────

action registrar_venda(carrinho, caixa):
    // O corpo roda DENTRO de uma transacao. Qualquer 'trigger' aqui
    // desfaz tudo o que ja foi escrito — inclusive a baixa de estoque
    // dos itens anteriores do mesmo carrinho.
    action corpo():
        total := 0.0
        linhas := []
        cycle item in carrinho:
            p := Banco.query_one(db, "SELECT * FROM produtos WHERE sku = ?", [item["sku"]])
            given p is void:
                trigger $"produto {item["sku"]} nao existe"
            given p["estoque"] smaller item["quantidade"]:
                trigger $"estoque insuficiente de {p["nome"]}: tem {p["estoque"]}, pediu {item["quantidade"]}"
            total += p["preco"] * item["quantidade"]
            linhas.append({"produto": p, "quantidade": item["quantidade"]})

        venda_id := Banco.insert(db, "vendas", {
                "total": round(total, 2), "caixa": caixa, "quando": "2026-09-12"})

        cycle linha in linhas:
            Banco.insert(db, "itens", {
                    "venda_id": venda_id,
                    "produto_id": linha["produto"]["id"],
                    "quantidade": linha["quantidade"],
                    "preco_unitario": linha["produto"]["preco"]})
            // A baixa e no BANCO: 'estoque = estoque - ?'. Ler, subtrair
            // e escrever de volta perde atualizacoes quando dois caixas
            // vendem o mesmo item ao mesmo tempo.
            Banco.increment(db, "produtos", "estoque",
                -linha["quantidade"], {"id": linha["produto"]["id"]})
        yield {"id": venda_id, "total": round(total, 2)}

    yield Banco.transacao(db, corpo)

// ── 2. Uma venda que da certo ───────────────────────────────

v := registrar_venda([
        {"sku": "CAF-500", "quantidade": 2},
        {"sku": "ACU-1KG", "quantidade": 3}
    ], "ana")

assert v["total"] is 82.27
assert Banco.count(db, "vendas") is 1
assert Banco.count(db, "itens") is 2
assert Banco.query_one(db, "SELECT estoque FROM produtos WHERE sku='CAF-500'")["estoque"] is 18
assert Banco.query_one(db, "SELECT estoque FROM produtos WHERE sku='ACU-1KG'")["estoque"] is 47

// ── 3. Uma venda que falha NO MEIO ──────────────────────────
//
// O primeiro item tem estoque e o segundo nao. Sem transacao, o cafe
// sairia do estoque e a venda nao existiria.

antes_vendas := Banco.count(db, "vendas")
antes_itens := Banco.count(db, "itens")
antes_cafe := Banco.query_one(db, "SELECT estoque FROM produtos WHERE sku='CAF-500'")["estoque"]

monitor:
    registrar_venda([
            {"sku": "CAF-500", "quantidade": 1},
            {"sku": "LEI-1L", "quantidade": 99}
        ], "bruno")
    assert no
handle Error as e:
    assert "estoque insuficiente" in e.message

assert Banco.count(db, "vendas") is antes_vendas
assert Banco.count(db, "itens") is antes_itens
assert Banco.query_one(db, "SELECT estoque FROM produtos WHERE sku='CAF-500'")["estoque"] is antes_cafe

// ── 4. O savepoint: desfazer so uma parte ───────────────────
//
// Um item sem estoque nao precisa derrubar a venda inteira quando a
// regra do negocio e "vende o que tem".

action venda_tolerante(carrinho, caixa):
    action corpo():
        venda_id := Banco.insert(db, "vendas", {
                "total": 0.0, "caixa": caixa, "quando": "2026-09-12"})
        total := 0.0
        recusados := []

        cycle item in carrinho:
            action tentar_item():
                p := Banco.query_one(db, "SELECT * FROM produtos WHERE sku = ?", [item["sku"]])
                given p is void or p["estoque"] smaller item["quantidade"]:
                    trigger "sem estoque"
                Banco.insert(db, "itens", {
                        "venda_id": venda_id, "produto_id": p["id"],
                        "quantidade": item["quantidade"],
                        "preco_unitario": p["preco"]})
                Banco.increment(db, "produtos", "estoque",
                    -item["quantidade"], {"id": p["id"]})
                yield p["preco"] * item["quantidade"]

            monitor:
                total += Banco.savepoint(db, "item", tentar_item)
            handle Error as e:
                recusados.append(item["sku"])

        Banco.update(db, "vendas", {"total": round(total, 2)}, {"id": venda_id})
        yield {"id": venda_id, "total": round(total, 2), "recusados": recusados}

    yield Banco.transacao(db, corpo)

r := venda_tolerante([
        {"sku": "ACU-1KG", "quantidade": 1},
        {"sku": "LEI-1L", "quantidade": 99},
        {"sku": "CAF-500", "quantidade": 1}
    ], "carla")

assert r["recusados"] is ["LEI-1L"]
assert r["total"] is 38.39
assert Banco.count(db, "vendas") is 2
// o leite nao saiu do estoque
assert Banco.query_one(db, "SELECT estoque FROM produtos WHERE sku='LEI-1L'")["estoque"] is 2

out "220 ok — pdv e transacoes"`, lang: 'df', title: `exercicios/29-banco-e-crud/220_pdv_e_transacoes.df` },
  {"h3": "O problema"},
  {"p": "Sem transação, um erro no meio deixa a venda registrada com o estoque intacto — ou o estoque baixado sem venda nenhuma. Ninguém descobre até o inventário, e aí não há como saber quais vendas foram afetadas."},
  { code: `       grava a venda   ✓
       grava o item 1  ✓
       baixa estoque 1 ✓
       grava o item 2  ✗  ← sem estoque
       ────────────────────
       sem transação:   a venda existe, com um item, e o estoque do
                        primeiro item foi baixado
       com transação:   nada aconteceu`, lang: 'text' },
  {"h3": "Conceitos"},
  { code: `Banco.transacao(db, corpo)        // erro DESFAZ tudo
Banco.savepoint(db, "item", acao) // desfaz só uma parte
Banco.increment(db, "produtos", "estoque", -2, {"id": 7})`, lang: 'df' },
  {"p": "`Banco.transacao` devolve o que o corpo devolveu, e desfaz em **qualquer** saída que não seja normal — inclusive num `halt` ou num `yield` que atravesse o bloco. Deixar commitado o que já foi escrito seria a pior das duas opções."},
  {"h3": "Por que `increment` e não ler-somar-escrever"},
  { code: `// errado, e o erro é silencioso
p := Banco.query_one(db, "SELECT estoque FROM produtos WHERE id = ?", [7])
Banco.update(db, "produtos", {"estoque": p["estoque"] - 1}, {"id": 7})

// certo: a soma é do banco, sob a trava da linha
Banco.increment(db, "produtos", "estoque", -1, {"id": 7})`, lang: 'df' },
  {"p": "Dois caixas vendendo o mesmo item ao mesmo tempo leem 10, ambos escrevem 9, e uma unidade desaparece do controle sem nenhum erro aparecer. Foi medido: em quatro threads fazendo 200 incrementos cada, a forma ingênua perde cerca de um terço."},
  {"h3": "`savepoint`: quando a regra é \"vende o que tem\""},
  {"p": "Um item sem estoque não precisa derrubar a venda inteira. O savepoint é uma transação **dentro** da transação: ele desfaz só a parte dele."},
  { code: `monitor:
    total += Banco.savepoint(db, "item", tentar_item)
handle Error as e:
    recusados.append(item["sku"])`, lang: 'df' },
  {"p": "O SQLite não aninha `BEGIN`, mas aninha savepoint — `Banco.transacao` dentro de outra vira savepoint sozinho."},
  {"h3": "O que este exercício mostra"},
  {"table": {"head": ["Parte", "Ideia"], "rows": [["1", "a venda como uma unidade, dentro de `transacao`"], ["2", "uma venda que dá certo"], ["3", "uma que falha **no meio**, e não deixa rastro"], ["4", "`savepoint` para recusar um item sem perder a venda"]]}},
  {"h3": "Armadilha"},
  {"p": "Todo `insert` e `update` deste módulo confirma sozinho — **exceto** dentro de uma transação. Foi um bug real: o primeiro `insert` de dentro confirmava a transação inteira, e o `rollback` depois não tinha o que desfazer. A venda ficava gravada com o estoque intacto, que é exatamente o que a transação existe para evitar."},
  {"h2": "221 · Relatorio, busca e o indice que falta"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 221 — Relatorio, busca e o indice que falta
//
//  Tres coisas que toda tela de gestao pede, e as tres tem uma versao
//  ingenua que funciona com cem linhas e morre com cem mil.
// ════════════════════════════════════════════════════════════

adopt Arcane.Database as Banco

db := Banco.memory()

Banco.create_table(db, "vendas", {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "produto": "TEXT NOT NULL",
        "categoria": "TEXT NOT NULL",
        "vendedor": "TEXT NOT NULL",
        "valor": "REAL NOT NULL",
        "mes": "TEXT NOT NULL"
    })

dados := []
categorias := ["bebida", "mercearia", "limpeza"]
vendedores := ["ana", "bruno", "carla"]
cycle i from 1 to 90:
    dados.append({
            "produto": $"Produto {i}",
            "categoria": categorias[i % 3],
            // Um passo diferente: se os dois vierem de 'i % 3', categoria e
            // vendedor ficam presos um ao outro e o cruzamento de dois
            // grupos da 3 linhas em vez de 9.
            "vendedor": vendedores[(i ~/ 3) % 3],
            "valor": 10.0 + (i % 17) * 5.0,
            "mes": $"2026-{(i % 6) + 1}"
        })
Banco.insert_many(db, "vendas", dados)

// ── 1. Relatorio agrupado, sem escrever SQL ─────────────────

por_vendedor := Banco.aggregate(db, "vendas", {
        "receita":["sum", "valor"],
        "vendas":["count", "*"],
        "ticket":["avg", "valor"]
    }, group_by := "vendedor", order_by := "receita DESC")

assert len(por_vendedor) is 3
// a primeira linha e a de maior receita
assert por_vendedor[0]["receita"] bigger_eq por_vendedor[1]["receita"]
// as colunas do group_by vem junto — e o que um grafico precisa
assert "vendedor" in por_vendedor[0]
assert por_vendedor[0]["vendas"] is 30

// dois grupos ao mesmo tempo
cruzado := Banco.aggregate(db, "vendas", {"receita":["sum", "valor"]},
    group_by := ["categoria", "vendedor"])
assert len(cruzado) is 9  // 3 x 3

// com filtro
so_bebida := Banco.aggregate(db, "vendas", {"total":["sum", "valor"]},
    where := {"categoria": "bebida"})
assert so_bebida[0]["total"] smaller_eq por_vendedor[0]["receita"] * 3

// ── 2. O atalho que mais se pede ────────────────────────────

quantas := Banco.group_count(db, "vendas", "categoria")
assert len(quantas) is 3
assert quantas[0]["quantidade"] is 30

// ── 3. O que o analisador NAO deixa passar ──────────────────
//
// O nome da coluna vai CRU para o SQL — o SQLite nao aceita nome por
// parametro. Um '?ordenar=' vindo de uma rota e injecao pela porta da
// frente, e por isso ele e conferido.

monitor:
    Banco.aggregate(db, "vendas", {"n":["count", "*"]},
        order_by := "valor; DROP TABLE vendas")
    assert no
handle Error as e:
    assert "nao e um nome valido" in e.message
assert Banco.table_exists(db, "vendas")

monitor:
    Banco.aggregate(db, "vendas", {"x":["mediana", "valor"]})
    assert no
handle Error as e:
    assert "agregacao conhecida" in e.message

// ── 4. Busca textual, com indice ────────────────────────────
//
// 'WHERE produto LIKE "%termo%"' nao usa indice nenhum: ele le a
// tabela inteira, sempre. O FTS5 usa indice invertido e ordena por
// relevancia.

Banco.create_search(db, "vendas", ["produto", "categoria"])

achados := Banco.search(db, "vendas", "produto 4")
assert len(achados) bigger 0
// devolve a linha da tabela ORIGINAL, com todas as colunas
assert "valor" in achados[0]
assert "vendedor" in achados[0]

// busca por prefixo: quem digita "merce" acha "mercearia"
assert len(Banco.search(db, "vendas", "merce")) bigger 0

// e o indice se mantem em dia — sem isso ele envelhece em silencio
Banco.insert(db, "vendas", {
        "produto": "Cafezinho Especial", "categoria": "bebida",
        "vendedor": "ana", "valor": 12.0, "mes": "2026-6"})
assert len(Banco.search(db, "vendas", "cafezinho")) is 1

// ── 5. O plano da consulta: onde esta o indice que falta ────

sem := Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
assert sem["varre_tabela"]
assert "le a tabela inteira" in sem["aviso"]

Banco.create_index(db, "vendas", ["vendedor"])
com := Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
assert not com["varre_tabela"]
assert com["aviso"] is ""

// os indices, com as colunas de cada um
indices := Banco.indexes(db, "vendas") >> sift i: not i["automatico"]
assert len(indices) is 1
assert indices[0]["colunas"] is ["vendedor"]

// ── 6. Um retrato do banco ──────────────────────────────────

e := Banco.stats(db)
// as tabelas-sombra do FTS nao contam: um banco de uma tabela nao
// pode parecer ter cinco
assert len(e["tabelas"]) is 1
assert e["tabelas"][0]["tabela"] is "vendas"
assert e["tabelas"][0]["linhas"] is 91
assert Banco.integrity(db)["ok"]

out "221 ok — relatorios e busca"`, lang: 'df', title: `exercicios/29-banco-e-crud/221_relatorios_e_busca.df` },
  {"h3": "Conceitos"},
  { code: `Banco.aggregate(db, "vendas",
                {"receita": ["sum", "valor"], "vendas": ["count", "*"]},
                group_by := "vendedor", order_by := "receita DESC")

Banco.group_count(db, "vendas", "categoria")

Banco.create_search(db, "produtos", ["nome", "sku"])
Banco.search(db, "produtos", "cafe")

Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
Banco.indexes(db, "vendas")
Banco.stats(db)`, lang: 'df' },
  {"h3": "Relatório sem escrever SQL"},
  {"p": "As colunas do `group_by` saem junto com os agregados — que é o que um gráfico precisa:"},
  { code: `[{"vendedor": "ana", "receita": 4820.0, "vendas": 30, "ticket": 160.6},
 {"vendedor": "bruno", "receita": 3910.0, ...}]`, lang: 'text' },
  {"p": "Aceita `count`, `sum`, `avg`, `min`, `max` e `total`. A lista é fechada **de propósito**: o nome da função vai cru para o SQL, e aceitar qualquer texto ali seria injeção pela porta da frente. Para outra agregação, escreva o SQL com `Banco.query` — e aí a responsabilidade é de quem escreveu."},
  {"h3": "O nome de coluna é conferido"},
  {"p": "Valor vai por `?`, sempre. Mas nome de coluna, de tabela e de índice **não pode ir por parâmetro** — o SQLite não aceita — e portanto vai concatenado. É a porta de injeção, e a única defesa é recusar o que não parece um nome:"},
  { code: `Banco.aggregate(db, "vendas", {"n": ["count", "*"]},
                order_by := "valor; DROP TABLE vendas")
// erro: 'valor; DROP TABLE vendas' nao e um nome valido`, lang: 'df' },
  {"p": "Isso importa porque o `order_by` de uma listagem vem de fora (`?ordenar=nome`)."},
  {"h3": "Busca textual contra `LIKE`"},
  { code: `WHERE produto LIKE '%cafe%'     -- lê a tabela inteira, sempre`, lang: 'sql' },
  {"p": "`LIKE` com `%` na frente não usa índice nenhum. O FTS5 usa índice invertido e ordena por relevância:"},
  { code: `Banco.create_search(db, "produtos", ["nome", "categoria"])
Banco.search(db, "produtos", "merce")     // acha "mercearia"`, lang: 'df' },
  {"p": "Três detalhes que fazem a diferença:"},
  {"list": ["**Prefixo na última palavra.** Quem digita `livr` espera achar"]},
  {"p": "`livro` antes de terminar de escrever."},
  {"list": ["**O índice se mantém em dia**, por gatilhos. Sem eles ele envelhece"]},
  {"p": "em silêncio e a busca deixa de achar o que foi cadastrado depois — o pior defeito possível numa busca."},
  {"list": ["**Devolve a linha da tabela original.** Quem busca quer o produto,"]},
  {"p": "não o índice."},
  {"h3": "O plano da consulta"},
  {"p": "A linha que importa é a que diz `SCAN` em vez de `SEARCH`:"},
  { code: `Banco.explain(db, "SELECT * FROM vendas WHERE vendedor = ?", ["ana"])
// {"varre_tabela": yes, "aviso": "le a tabela inteira: SCAN vendas"}

Banco.create_index(db, "vendas", ["vendedor"])
// {"varre_tabela": no, "aviso": ""}`, lang: 'df' },
  {"p": "`SCAN` lê a tabela inteira. Num cadastro de 200 mil linhas é a diferença entre 2 ms e 2 s, e a resposta quase sempre é um índice."},
  {"h3": "Armadilha"},
  {"p": "`Banco.stats` **não** conta as tabelas-sombra do FTS5 (`_data`, `_idx`, `_docsize`, `_config`). Contá-las faria um banco de duas tabelas parecer ter dez — e foi o que acontecia."},
  {"h2": "222 · Migracoes: mudar o schema sem perder dado"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 222 — Migracoes: mudar o schema sem perder dado
//
//  Num sistema em producao o banco tem dado dentro. Trocar o
//  'create_table' no codigo nao muda a tabela que ja existe, e apagar
//  e recriar perde tudo. Migracao e o registro do que ja foi aplicado.
// ════════════════════════════════════════════════════════════

adopt Arcane.Database as Banco

db := Banco.memory()

// ── 1. A lista, com ida E volta ─────────────────────────────
//
// Toda migracao tem 'up' e deveria ter 'down'. Sem o 'down', desfazer
// exige editar o banco a mao — no meio de um incidente, que e quando
// se desfaz.

steady MIGRACOES := [
    {
        "version": 1,
        "description": "clientes",
        "up": """
            CREATE TABLE clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL
            );
        """,
        "down": "DROP TABLE clientes;"
    },
    {
        "version": 2,
        "description": "e-mail do cliente",
        "up": "ALTER TABLE clientes ADD COLUMN email TEXT;",
        "down": "ALTER TABLE clientes DROP COLUMN email;"
    },
    {
        "version": 3,
        "description": "indice de e-mail",
        "up": "CREATE INDEX idx_cliente_email ON clientes(email);",
        "down": "DROP INDEX idx_cliente_email;"
    }
]

// ── 2. Aplicar ──────────────────────────────────────────────

assert Banco.migrate(db, MIGRACOES) is 3
assert Banco.table_exists(db, "clientes")
assert "email" in(Banco.columns(db, "clientes") >> morph c: c["name"])

// ── 3. E idempotente: rodar de novo nao faz nada ────────────
//
// E o que permite chamar 'migrate' no comeco de todo processo. Sem
// isso, subir o servidor duas vezes quebraria na segunda.

assert Banco.migrate(db, MIGRACOES) is 0

aplicadas := Banco.migrations_applied(db)
assert len(aplicadas) is 3
assert aplicadas[0]["version"] is 1
assert aplicadas[2]["description"] is "indice de e-mail"

// ── 4. O dado sobrevive a uma migracao ──────────────────────

Banco.insert(db, "clientes", {"nome": "Ana", "email": "ana@exemplo.br"})
assert Banco.count(db, "clientes") is 1

// uma migracao nova, com a tabela ja povoada
steady MAIS := [...MIGRACOES, {
        "version": 4,
        "description": "telefone",
        "up": "ALTER TABLE clientes ADD COLUMN telefone TEXT DEFAULT '';",
        "down": "ALTER TABLE clientes DROP COLUMN telefone;"
    }]

assert Banco.migrate(db, MAIS) is 1
assert Banco.count(db, "clientes") is 1  // o dado continua la
assert Banco.query_one(db, "SELECT nome FROM clientes")["nome"] is "Ana"

// ── 5. Desfazer uma ─────────────────────────────────────────
//
// Por padrao desfaz UMA: desfazer em cascata por acidente e perda de
// dado, e a diferenca entre "corrigi a ultima" e "apaguei o banco".

assert Banco.rollback_migration(db, MAIS) is 1
assert "telefone" not in(Banco.columns(db, "clientes") >> morph c: c["name"])
assert len(Banco.migrations_applied(db)) is 3

// ── 6. Desfazer ate uma versao ──────────────────────────────

assert Banco.rollback_migration(db, MAIS, ate := 1) is 2
assert len(Banco.migrations_applied(db)) is 1
assert Banco.table_exists(db, "clientes")  // a versao 1 ficou

// ── 7. Uma migracao sem 'down' nao e pulada em silencio ─────
//
// Pular deixaria o banco num estado que NENHUMA versao descreve, e
// descobrir isso depois e pior que o erro agora.

steady SEM_VOLTA := [{
        "version": 1, "description": "sem volta",
        "up": "CREATE TABLE x (id INTEGER);"
    }]

outro := Banco.memory()
Banco.migrate(outro, SEM_VOLTA)
monitor:
    Banco.rollback_migration(outro, SEM_VOLTA)
    assert no
handle Error as e:
    assert "nao tem 'down'" in e.message

// ── 8. O schema como o banco o guarda ───────────────────────
//
// Para versionar, comparar dois ambientes e escrever a migracao que
// falta.

sql := Banco.schema_sql(db, "clientes")
assert "CREATE TABLE" in sql
assert "nome" in sql

out "222 ok — migracoes"`, lang: 'df', title: `exercicios/29-banco-e-crud/222_migracoes.df` },
  {"h3": "Conceitos"},
  { code: `steady MIGRACOES := [
    {"version": 1, "description": "clientes",
     "up":   "CREATE TABLE clientes (id INTEGER PRIMARY KEY, nome TEXT);",
     "down": "DROP TABLE clientes;"},
    {"version": 2, "description": "e-mail",
     "up":   "ALTER TABLE clientes ADD COLUMN email TEXT;",
     "down": "ALTER TABLE clientes DROP COLUMN email;"}
]

Banco.migrate(db, MIGRACOES)                 // aplica o que falta
Banco.migrations_applied(db)                 // o que já foi
Banco.rollback_migration(db, MIGRACOES)      // desfaz UMA
Banco.rollback_migration(db, MIGRACOES, ate := 1)
Banco.schema_sql(db, "clientes")             // o CREATE como está`, lang: 'df' },
  {"h3": "É idempotente, e isso é o ponto"},
  {"p": "`Banco.migrate` grava numa tabela `_migrations` o que já aplicou, e pula essas. Rodar de novo devolve `0`."},
  {"p": "É o que permite chamá-lo no começo de **todo** processo:"},
  { code: `db := Banco.connect("dados.db")
Banco.migrate(db, MIGRACOES)
V.subir(porta := 8501)`, lang: 'df' },
  {"p": "Sem isso, subir o servidor duas vezes quebraria na segunda."},
  {"h3": "Toda migração deveria ter `down`"},
  {"p": "Desfazer acontece no meio de um incidente — que é quando ninguém tem paciência para editar o banco à mão. Duas escolhas:"},
  {"p": "**Por padrão desfaz uma.** Desfazer em cascata por acidente é perda de dado, e é a diferença entre \"corrigi a última\" e \"apaguei o banco\". `ate := n` desfaz até a versão `n`, que **fica** aplicada."},
  {"p": "**Uma migração sem `down` interrompe o rollback com erro**, em vez de ser pulada em silêncio. Pular deixaria o banco num estado que **nenhuma versão descreve**, e descobrir isso depois é pior que o erro agora."},
  {"h3": "O que este exercício mostra"},
  {"table": {"head": ["Parte", "Ideia"], "rows": [["1", "a lista, com `up` **e** `down`"], ["2–3", "aplicar, e a idempotência"], ["4", "o dado sobrevive a uma migração sobre tabela povoada"], ["5–6", "desfazer uma, e desfazer até uma versão"], ["7", "a migração sem `down` não é pulada em silêncio"], ["8", "`schema_sql` para versionar e comparar ambientes"]]}},
  {"h3": "Para produção"},
  {"p": "O SQLite não desfaz DDL dentro de transação de forma confiável em todas as versões. Faça backup antes de migrar em produção — `Banco.backup(db, \"antes-da-v7.db\")` é uma chamada."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/29-banco-e-crud/219_crud_completo.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '219-um-crud-completo-com-o-banco-fazendo-o-trabalho', text: "219 · Um CRUD completo, com o banco fazendo o trabalho", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'por-que-a-regra-vai-no-banco', text: "Por que a regra vai no banco", level: 3 as const }, { id: 'unique-nao-e-enfeite', text: "`UNIQUE` não é enfeite", level: 3 as const }, { id: 'paginacao', text: "Paginação", level: 3 as const }, { id: 'o-que-este-exercicio-mostra', text: "O que este exercício mostra", level: 3 as const }, { id: 'continua-em', text: "Continua em", level: 3 as const }, { id: '220-um-pdv-a-venda-inteira-ou-nenhuma', text: "220 · Um PDV: a venda inteira, ou nenhuma", level: 2 as const }, { id: 'o-problema', text: "O problema", level: 3 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'por-que-increment-e-nao-ler-somar-escrever', text: "Por que `increment` e não ler-somar-escrever", level: 3 as const }, { id: 'savepoint-quando-a-regra-e-vende-o-que-tem', text: "`savepoint`: quando a regra é \"vende o que tem\"", level: 3 as const }, { id: 'o-que-este-exercicio-mostra', text: "O que este exercício mostra", level: 3 as const }, { id: 'armadilha', text: "Armadilha", level: 3 as const }, { id: '221-relatorio-busca-e-o-indice-que-falta', text: "221 · Relatorio, busca e o indice que falta", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'relatorio-sem-escrever-sql', text: "Relatório sem escrever SQL", level: 3 as const }, { id: 'o-nome-de-coluna-e-conferido', text: "O nome de coluna é conferido", level: 3 as const }, { id: 'busca-textual-contra-like', text: "Busca textual contra `LIKE`", level: 3 as const }, { id: 'o-plano-da-consulta', text: "O plano da consulta", level: 3 as const }, { id: 'armadilha', text: "Armadilha", level: 3 as const }, { id: '222-migracoes-mudar-o-schema-sem-perder-dado', text: "222 · Migracoes: mudar o schema sem perder dado", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'e-idempotente-e-isso-e-o-ponto', text: "É idempotente, e isso é o ponto", level: 3 as const }, { id: 'toda-migracao-deveria-ter-down', text: "Toda migração deveria ter `down`", level: 3 as const }, { id: 'o-que-este-exercicio-mostra', text: "O que este exercício mostra", level: 3 as const }, { id: 'para-producao', text: "Para produção", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"29 · Banco e CRUD"}
      description={"4 exercícios: transações, upsert, busca textual e paginação."}
      href={"/docs/exercicios/29-banco-e-crud"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
