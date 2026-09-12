# Exercicio 222 — Migrações: mudar o schema sem perder dado

## Enunciado

Num sistema em produção o banco tem dado dentro. Trocar o
`create_table` no código não muda a tabela que já existe, e apagar e
recriar perde tudo.

## Conceitos

```dataforge
steady MIGRACOES := [
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
Banco.schema_sql(db, "clientes")             // o CREATE como está
```

## É idempotente, e isso é o ponto

`Banco.migrate` grava numa tabela `_migrations` o que já aplicou, e
pula essas. Rodar de novo devolve `0`.

É o que permite chamá-lo no começo de **todo** processo:

```dataforge
db := Banco.connect("dados.db")
Banco.migrate(db, MIGRACOES)
V.subir(porta := 8501)
```

Sem isso, subir o servidor duas vezes quebraria na segunda.

## Toda migração deveria ter `down`

Desfazer acontece no meio de um incidente — que é quando ninguém tem
paciência para editar o banco à mão. Duas escolhas:

**Por padrão desfaz uma.** Desfazer em cascata por acidente é perda de
dado, e é a diferença entre "corrigi a última" e "apaguei o banco".
`ate := n` desfaz até a versão `n`, que **fica** aplicada.

**Uma migração sem `down` interrompe o rollback com erro**, em vez de
ser pulada em silêncio. Pular deixaria o banco num estado que
**nenhuma versão descreve**, e descobrir isso depois é pior que o erro
agora.

## O que este exercício mostra

| Parte | Ideia |
|---|---|
| 1 | a lista, com `up` **e** `down` |
| 2–3 | aplicar, e a idempotência |
| 4 | o dado sobrevive a uma migração sobre tabela povoada |
| 5–6 | desfazer uma, e desfazer até uma versão |
| 7 | a migração sem `down` não é pulada em silêncio |
| 8 | `schema_sql` para versionar e comparar ambientes |

## Para produção

O SQLite não desfaz DDL dentro de transação de forma confiável em todas
as versões. Faça backup antes de migrar em produção —
`Banco.backup(db, "antes-da-v7.db")` é uma chamada.
