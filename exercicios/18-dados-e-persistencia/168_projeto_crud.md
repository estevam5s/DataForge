# Exercicio 168 — Projeto: CRUD com persistência

## Enunciado

Junte modelo, validação, banco de dados e relatório num sistema completo.

## A arquitetura

```
MODELO         record Aluno, enum Conceito, conceito_de
VALIDACAO      validar — pura, sem banco
PERSISTENCIA   inserir, buscar_todos, atualizar_nota, remover
APLICACAO      cadastro, relatório, distribuição
```

Cada camada depende só das de cima. `validar` não sabe que existe banco;
`conceito_de` não sabe que existe relatório.

## Modelo e armazenamento são coisas diferentes

O banco guarda linhas; o programa trabalha com records:

```dataforge
action buscar_todos():
    linhas := DB.query(conn, "SELECT id, nome, email, nota FROM alunos ...")
    yield linhas >> morph l: Aluno(l["id"], l["nome"], l["email"], l["nota"])
```

Essa conversão na fronteira paga por si: a partir dali o código usa `a.nome` com
verificação de tipo, em vez de `l["nome"]` com risco de digitar errado. E se a
coluna do banco mudar de nome, só esta linha muda.

## Validar antes de tocar no banco

```dataforge
action inserir(nome, email, nota):
    problemas := validar(nome, email, nota)
    given len(problemas) bigger 0:
        yield {"ok": no, "erros": problemas}
    ...
```

Duas linhas de defesa, e as duas são necessárias:

1. **A validação** pega o que dá para prever (nome curto, e-mail sem `@`).
2. **A restrição do banco** (`UNIQUE`) pega o que só ele sabe (e-mail repetido).

A segunda vem envolvida em `monitor`, porque a violação chega como erro do
SQLite:

```dataforge
monitor:
    DB.execute(conn, "INSERT ...")
    yield {"ok": yes}
handle e:
    yield {"ok": no, "erros": ["email ja cadastrado"]}
```

Repare que a mensagem técnica do banco é traduzida para algo que o usuário
entende.

## O padrão de resultado

Toda operação devolve a mesma forma:

```dataforge
{"ok": yes}
{"ok": no, "erros": ["...", "..."]}
```

Quem chama testa `ok` e, se falhou, tem a lista pronta para mostrar. Sem
exceções, sem código de erro para decorar.

## Enum com valor numérico

```dataforge
enum Conceito:
    A := 9
    B := 7
    C := 5
    D := 0
```

O valor é a **nota mínima** daquele conceito. Isso guarda a regra no próprio enum,
em vez de espalhá-la em números soltos pelo código.

## Gráfico em texto

```dataforge
out $"  {nome_conceito}: {"#".repeat(quantos)} ({quantos})"
```

Um histograma com uma linha. Em ferramenta de terminal, isso comunica a
distribuição melhor que uma tabela de números.

## Saída esperada

```
┌────────────────────┐
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
  D: # (1)
```

## Experimente

- Acrescente busca por nome com `LIKE` e parâmetro.
- Exponha o CRUD como API HTTP reaproveitando `validar`.
- Escreva `tests/validacao_test.df` cobrindo cada regra.
