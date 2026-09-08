# Exercício 201 — Conectar e consultar

## Enunciado

Abra um banco, crie uma tabela e leia de volta.

## Conceitos

O **Forge** fala com cinco motores pela mesma interface: PostgreSQL, MySQL,
MariaDB, MongoDB, Redis e SQLite. Trocar o motor troca a URL, e mais nada.

```dataforge
db := Forge.conectar("postgres://usuario:senha@localhost/app")
db := Forge.conectar("mysql://root@localhost/app")
db := Forge.conectar("dados.db")          // SQLite
db := Forge.conectar(":memory:")          // SQLite, sem arquivo
```

O exercício usa `:memory:` porque ele não precisa de servidor nenhum — e é
também o banco de teste ideal: cada execução começa limpa.

| Função | Devolve |
|--------|---------|
| `Forge.consultar` | uma lista de vaults, um por linha |
| `Forge.executar` | quantas linhas mudaram |
| `Forge.primeiro` | a primeira linha, ou `void` |

## O que observar

**As linhas voltam como vault, não como tupla.** `linha["nome"]` continua
funcionando quando alguém acrescenta uma coluna; `linha[0]` não.

**Os tipos sobrevivem à ida e volta.** `preco` volta como `Float`, não como
texto. Sem isso, `preco * 2` concatenaria em vez de multiplicar.

**Sem resultado devolve `void`, não erro.** `Forge.primeiro` de uma busca que
não achou nada é uma resposta legítima, não uma falha.

## Armadilhas

- `Forge.executar` devolve **quantas linhas mudaram**, não as linhas. Para
  receber as linhas de volta num INSERT, use `RETURNING` (PostgreSQL) ou o
  ORM.
- Uma conexão aberta e não fechada segura um recurso. Em programa curto isso
  não importa; num servidor, importa muito — ver o exercício 208.

## Relacionados

- [202 — Construtor de consultas](202_construtor_de_consultas.md)
- [205 — Modelos e validação](205_modelos_e_validacao.md)
- [208 — Pool de conexões](208_pool_e_conexoes.md)
