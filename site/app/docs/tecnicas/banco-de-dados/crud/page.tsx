// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_sqlite.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Um CRUD completo",
  description: "Livraria, biblioteca, comércio, estoque e PDV — o mesmo esqueleto, e o que muda entre eles.",
};

const blocos: Bloco[] = [
  {"p": "Os cinco sistemas que as pessoas pedem — livraria, biblioteca, loja, controle de estoque, PDV — têm o **mesmo esqueleto**. Esta página o constrói inteiro, e depois mostra o que muda em cada um."},
  {"p": "O código roda: ele é o [exercício 219](/docs/exercicios/29-banco-e-crud) mais o [220](/docs/exercicios/29-banco-e-crud), que se verificam a cada execução da suíte."},
  {"h2": "1. O schema, onde a regra mora"},
  { code: `adopt Arcane.Database as Banco

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
Banco.create_index(db, "livros", ["titulo"])`, lang: 'df' },
  {"table": {"head": ["Na memória", "No banco"], "rows": [["`SELECT` e depois `INSERT`", "`UNIQUE` + `upsert`"], ["conferir estoque e subtrair", "`estoque = estoque - ?`"], ["verificar se o autor tem livro", "`REFERENCES autores(id)`"], ["validar preço ≥ 0 no código", "`CHECK (preco >= 0)`"]]}},
  {"p": "A coluna da esquerda funciona até dois processos rodarem ao mesmo tempo. A da direita é o banco decidindo, sob a trava dele — e ele decide igual em todos os caminhos do código, inclusive nos que ninguém lembrou de validar."},
  {"callout": {"tipo": "dica", "titulo": "Índice em toda chave estrangeira", "texto": "O SQLite cria índice para `UNIQUE` e `PRIMARY KEY`, mas **não** para `REFERENCES`. Sem ele, cada `JOIN` e cada `DELETE` na tabela-mãe varre a tabela-filha inteira."}},
  {"h2": "2. Create"},
  { code: `action autor(nome):
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
// "atualizado" — e o autor não duplicou`, lang: 'df' },
  {"h2": "3. Read, com paginação e junção"},
  { code: `action pagina_de_livros(numero, tamanho, busca):
    given busca is not "":
        yield {"itens": Banco.search(db, "livros", busca, limit := tamanho),
               "pagina": 1, "paginas": 1, "total": 0,
               "tem_anterior": no, "tem_proxima": no}
    yield Banco.paginate(db, "livros", numero, tamanho,
                         order_by := "titulo")

action catalogo():
    yield Banco.query(db, """
        SELECT l.isbn, l.titulo, a.nome AS autor, l.preco, l.estoque
        FROM livros l
        JOIN autores a ON a.id = l.autor_id
        ORDER BY l.titulo
    """)`, lang: 'df' },
  {"p": "`Banco.paginate` devolve o que a tela precisa, e não só a fatia:"},
  { code: `{
    "itens": [...],       "pagina": 2,      "por_pagina": 20,
    "total": 143,         "paginas": 8,
    "tem_anterior": yes,  "tem_proxima": yes
}`, lang: 'text' },
  {"p": "Sem `total` e `paginas` a tela não sabe desenhar a paginação, e calcular isso à mão é a mesma consulta escrita duas vezes. `por_pagina` tem teto de 500: o número vem de fora numa rota, e `?por_pagina=1000000` é como se derruba um servidor sem exploit."},
  {"h2": "4. Update e Delete"},
  { code: `Banco.update(db, "livros", {"preco": 89.9}, {"isbn": "978-1"})   // uma linha
Banco.delete(db, "livros", {"isbn": "978-3"})                    // uma linha

// e o banco recusa apagar um autor que tem livro
monitor:
    Banco.delete(db, "autores", {"nome": "Frank Herbert"})
handle Error as e:
    out "recusado pela chave estrangeira"      // FOREIGN KEY constraint`, lang: 'df' },
  {"h2": "5. A venda, como uma unidade"},
  {"p": "É aqui que um exemplo se separa de um sistema. Gravar a venda, gravar os itens e baixar o estoque de cada um precisam valer **juntos**:"},
  { code: `action registrar_venda(carrinho, caixa):
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

    yield Banco.transacao(db, corpo)`, lang: 'df' },
  { code: `       grava a venda   ✓
       grava o item 1  ✓
       baixa estoque 1 ✓
       grava o item 2  ✗  ← sem estoque
       ────────────────────
       sem transação:   a venda existe, com um item, e o estoque do
                        primeiro item foi baixado
       com transação:   nada aconteceu`, lang: 'text' },
  {"p": "Ninguém descobre o primeiro caso até o inventário — e aí não há como saber quais vendas foram afetadas."},
  {"h3": "Quando a regra é \"vende o que tem\""},
  { code: `action tentar_item():
    p := Banco.query_one(db, "SELECT * FROM livros WHERE isbn = ?", [isbn])
    given p is void or p["estoque"] smaller pedido:
        trigger "sem estoque"
    Banco.insert(db, "itens", { … })
    Banco.increment(db, "livros", "estoque", -pedido, {"id": p["id"]})
    yield p["preco"] * pedido

monitor:
    total += Banco.savepoint(db, "item", tentar_item)
handle Error as e:
    recusados.append(isbn)`, lang: 'df' },
  {"p": "O savepoint desfaz só a parte dele: o item recusado não sai do estoque, e a venda continua."},
  {"h2": "O mesmo esqueleto, cinco sistemas"},
  {"table": {"head": ["Sistema", "A tabela do meio é", "O que muda"], "rows": [["**Livraria**", "`vendas` + `itens`", "o que foi escrito acima"], ["**Biblioteca**", "`emprestimos`", "não há preço; há `devolver_em` e o estoque é *exemplares disponíveis*. Um empréstimo é `increment(-1)`; a devolução, `increment(+1)`"], ["**Comércio**", "`pedidos` + `itens`", "acrescenta `clientes`, `enderecos` e um `status` que caminha (`aberto → pago → enviado`)"], ["**Estoque**", "`movimentos`", "toda alteração é uma **linha**, nunca um `update`: entrada, saída, ajuste, perda. O saldo é a soma — e aí ele é auditável"], ["**PDV**", "`vendas` + `itens` + `pagamentos`", "uma venda tem N formas de pagamento, e a soma delas precisa fechar com o total"]]}},
  {"h3": "Estoque: por que movimento e não saldo"},
  { code: `Banco.create_table(db, "movimentos", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "produto_id": "INTEGER NOT NULL REFERENCES produtos(id)",
    "tipo": "TEXT NOT NULL CHECK (tipo IN ('entrada','saida','ajuste','perda'))",
    "quantidade": "INTEGER NOT NULL",
    "motivo": "TEXT NOT NULL DEFAULT ''",
    "quem": "TEXT NOT NULL",
    "quando": "TEXT NOT NULL"
})

action saldo(produto_id):
    linha := Banco.query_one(db, """
        SELECT COALESCE(SUM(CASE WHEN tipo IN ('entrada','ajuste')
                                 THEN quantidade ELSE -quantidade END), 0)
               AS saldo
        FROM movimentos WHERE produto_id = ?
    """, [produto_id])
    yield linha["saldo"]`, lang: 'df' },
  {"p": "Um `UPDATE produtos SET estoque = ?` é mais rápido e não responde à pergunta que sempre aparece: *por que o saldo está assim?* Com movimento, a resposta é um `SELECT`. A coluna `estoque` continua existindo como **cache** do saldo, mantida por `increment` na mesma transação do movimento."},
  {"h3": "PDV: o pagamento precisa fechar"},
  { code: `action fechar_venda(venda_id, pagamentos):
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

    yield Banco.transacao(db, corpo)`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Dinheiro não é `Float`", "texto": "`0.1 + 0.2` dá `0.30000000000000004`, e um centavo que soma errado numa linha soma errado num milhão. Para valor conferido por pessoa, [`Arcane.Decimal`](/docs/tecnicas/decimal) — e guarde no banco como **inteiro de centavos** ou como `TEXT`, nunca como `REAL`."}},
  {"h2": "Ligando na tela"},
  {"p": "O mesmo banco serve os três: uma API REST, um painel e uma CLI."},
  { code: `adopt Kiln
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
})`, lang: 'df' },
  {"p": "Para o painel, [um projeto de análise completo](/docs/vitrine/projeto) lê deste mesmo banco."},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/tecnicas/banco-de-dados/relatorios", "title": "Relatórios e busca", "desc": "Agregação, FTS5 e o plano de consulta."}, {"href": "/docs/tecnicas/banco-de-dados/migracoes", "title": "Migrações", "desc": "Mudar o schema de um banco que tem dado dentro."}, {"href": "/docs/vitrine/projeto", "title": "Um painel sobre este banco", "desc": "Análise de dados completa, do SQL ao gráfico."}, {"href": "/docs/exercicios/29-banco-e-crud", "title": "Os exercícios", "desc": "Os quatro que se verificam a cada execução."}]},
];

const headings = [{ id: '1-o-schema-onde-a-regra-mora', text: "1. O schema, onde a regra mora", level: 2 as const }, { id: '2-create', text: "2. Create", level: 2 as const }, { id: '3-read-com-paginacao-e-juncao', text: "3. Read, com paginação e junção", level: 2 as const }, { id: '4-update-e-delete', text: "4. Update e Delete", level: 2 as const }, { id: '5-a-venda-como-uma-unidade', text: "5. A venda, como uma unidade", level: 2 as const }, { id: 'quando-a-regra-e-vende-o-que-tem', text: "Quando a regra é \"vende o que tem\"", level: 3 as const }, { id: 'o-mesmo-esqueleto-cinco-sistemas', text: "O mesmo esqueleto, cinco sistemas", level: 2 as const }, { id: 'estoque-por-que-movimento-e-nao-saldo', text: "Estoque: por que movimento e não saldo", level: 3 as const }, { id: 'pdv-o-pagamento-precisa-fechar', text: "PDV: o pagamento precisa fechar", level: 3 as const }, { id: 'ligando-na-tela', text: "Ligando na tela", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Um CRUD completo"}
      description={"Livraria, biblioteca, comércio, estoque e PDV — o mesmo esqueleto, e o que muda entre eles."}
      href={"/docs/tecnicas/banco-de-dados/crud"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
