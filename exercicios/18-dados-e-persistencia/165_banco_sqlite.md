# Exercicio 165 — Banco de dados

## Enunciado

Crie tabelas, insira, consulte e use transações com `Arcane.Database`.

## Conectar

```dataforge
conn := DB.memory()                  // em memória: some ao terminar
conn := DB.connect("dados.db")       // arquivo SQLite
```

`memory()` é ideal para teste: cada execução começa limpa, e nada fica no disco.

## Parâmetros, sempre

```dataforge
DB.query(conn, "SELECT nome FROM produtos WHERE preco < ?", [100])
```

Nunca monte SQL com interpolação:

```dataforge
DB.query(conn, $"SELECT * FROM users WHERE nome = '{entrada}'")   // NÃO
```

Se `entrada` for `'; DROP TABLE users; --`, você acabou de perder a tabela. Com
`?`, o valor é enviado separado do comando e nunca é interpretado como SQL. Essa
é a defesa contra injeção, e ela é completa.

## As operações

| Chamada | Para |
|---------|------|
| `execute(conn, sql, params)` | INSERT, UPDATE, DELETE, CREATE |
| `execute_many(conn, sql, lista)` | vários INSERT de uma vez |
| `query(conn, sql, params)` | várias linhas, como lista de vaults |
| `query_one(conn, sql, params)` | uma linha, ou `void` |
| `count(conn, tabela)` | atalho para `COUNT(*)` |

`query` devolve vaults com os nomes das colunas como chaves — dá para usar
`p["nome"]` direto, sem índices.

## `execute_many`

```dataforge
DB.execute_many(conn, "INSERT INTO produtos VALUES (?, ?, ?)", [
    ["Teclado", 200.0, 3],
    ["Monitor", 1200.0, 0]
])
```

Uma ida ao banco em vez de N. Para inserção em lote, a diferença de desempenho é
grande.

## Transações

```dataforge
DB.begin(conn)
DB.execute(conn, "UPDATE contas SET saldo = saldo - 100 WHERE id = 1")
DB.execute(conn, "UPDATE contas SET saldo = saldo + 100 WHERE id = 2")
DB.commit(conn)         // ou DB.rollback(conn)
```

As duas operações acontecem **juntas ou nenhuma**. Sem transação, uma falha entre
elas deixaria dinheiro sumido.

O padrão seguro combina com `monitor`:

```dataforge
DB.begin(conn)
monitor:
    // ... operações
    DB.commit(conn)
handle e:
    DB.rollback(conn)
    propagate e.message
```

## Introspecção

```dataforge
DB.tables(conn)                  // as tabelas
DB.columns(conn, "produtos")     // as colunas
DB.table_exists(conn, "x")
DB.table_info(conn, "produtos")  // tipos e restrições
```

## Saída esperada

```
── catalogo ──
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

conexao fechada
```

## Experimente

- Crie uma tabela de vendas com chave estrangeira e faça um JOIN.
- Envolva uma transferência entre contas numa transação com `monitor`.
- Compare `execute` num laço com `execute_many` para 1000 registros.
