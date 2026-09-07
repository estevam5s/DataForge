# Exercicio 178 — Projeto: sistema de biblioteca

## Enunciado

Integre records, enums, banco de dados, validação e relatórios num sistema
completo.

## A arquitetura

```
MODELO         record Livro, record Emprestimo, enum Situacao
REGRAS         situacao_do, multa_de, validar_livro   ← puras
PERSISTENCIA   cadastrar, emprestar, livros           ← tocam o banco
APLICACAO      cadastro, relatório, estatísticas
```

O que distingue as camadas: **as regras não sabem que existe banco**.

## Regras puras

```dataforge
action situacao_do(emprestimo) -> Situacao:
    given emprestimo is void:
        yield Situacao.Disponivel
    given emprestimo.dias bigger PRAZO_DIAS:
        yield Situacao.Atrasado
    yield Situacao.Emprestado
```

Sem banco, sem `out`, sem data do sistema. Consequência prática: o teste é uma
linha, e roda em microssegundos.

```dataforge
assert situacao_do(Emprestimo(1, 1, "Ana", 20)) is Situacao.Atrasado
```

Se ela consultasse o banco, cada teste precisaria montar um esquema.

## Constantes com nome

```dataforge
steady PRAZO_DIAS := 14
steady MULTA_POR_DIA := 2.5
```

Compare com `given emprestimo.dias bigger 14` espalhado por três lugares. Quando
a biblioteca mudar o prazo, há uma linha para mudar — e o nome documenta o que o
número significa.

## Validar e converter na fronteira

```dataforge
action livros():
    yield DB.query(conn, "SELECT ...")
        >> morph l: Livro(l["id"], l["titulo"], l["autor"], l["ano"])
```

Linhas do banco entram; records tipados saem. A partir dali, `l.titulo` com
verificação, não `l["titulo"]` com risco de digitar errado.

## Regra de negócio no banco

```dataforge
action emprestar(livro_id, leitor, dias):
    ja := DB.query_one(conn, "SELECT id FROM emprestimos WHERE livro_id = ?", [livro_id])
    given ja isnt void:
        yield {"ok": no, "erros": ["livro ja emprestado"]}
```

"Um livro só pode estar emprestado uma vez" depende do estado atual — não dá para
validar sem consultar. Por isso essa checagem fica na camada de persistência, não
em `validar_livro`.

## Agrupar por expressão

```dataforge
Col.group_by(todos, lambda l: $"seculo {l.ano ~/ 100 + 1}")
```

`group_by` aceita o nome de um campo **ou** uma função. Aqui a chave é calculada:
1899 → século 19, 1956 → século 20.

## Saída esperada

```
┌────────────┐
│ Biblioteca │
└────────────┘

── cadastro ──
  ok   Dom Casmurro
  ok   Grande Sertao Veredas
  ...
  nao  X: titulo muito curto
  nao  Livro do Futuro: ano improvavel: 3000

── emprestimos ──
  ok   livro 1 para Ana ha 5 dias
  ok   livro 2 para Bruno ha 20 dias
  nao  livro 1 para Carla: livro ja emprestado

┌────────┐
│ Acervo │
└────────┘

  TITULO                     ANO  SITUACAO    MULTA
  --------------------------------------------------------
  A Hora da Estrela         1977  Disponivel  -
  Dom Casmurro              1899  Emprestado  -
  Grande Sertao Veredas     1956  Atrasado    R$ 15.0
  Vidas Secas               1938  Disponivel  -

  multas acumuladas: R$ 15.0
```

## Experimente

- Acrescente devolução, com registro da data.
- Use `Arcane.Time` para calcular os dias a partir de datas reais.
- Exponha como API HTTP reaproveitando as regras.
- Escreva `tests/regras_test.df` cobrindo prazo, atraso e multa.
