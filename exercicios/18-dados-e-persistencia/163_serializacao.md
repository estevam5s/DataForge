# Exercicio 163 — Serialização de dados

## Enunciado

Converta estruturas do DataForge para JSON, CSV, TOML e de volta.

## Por que isso importa

Todo programa que não é um exercício conversa com o mundo: lê um arquivo, chama
uma API, grava um relatório. Serialização é essa fronteira, e o módulo
`Arcane.Serialization` cobre os formatos que aparecem na prática.

## JSON

```dataforge
Serde.to_json(dados)                  // compacto
Serde.json_pretty(dados, 2)           // indentado
Serde.from_json(texto)                // pode disparar
Serde.from_json_safe(texto, padrao)   // nunca dispara
```

### A variante `_safe`

```dataforge
r := Serde.from_json_safe("{isso nao e json")
// {ok: no, value: void, error: "Expecting property name..."}
```

Dado que veio de fora **vai** estar malformado alguma hora. `from_json_safe`
transforma isso num valor que você examina, em vez de uma exceção que precisa
envolver em `monitor`:

```dataforge
r := Serde.from_json_safe(corpo)
given r.ok:
    processar(r.value)
otherwise:
    responder_erro(r.error)
```

## `json_path` — navegar sem quebrar

```dataforge
Serde.json_path(dados, "autor.nome")
Serde.json_path(dados, "tags.0")                       // índice de lista
Serde.json_path(dados, "autor.telefone", "ausente")    // com padrão
```

Sem isso, chegar num campo aninhado exige verificar cada nível:

```dataforge
given "autor" in dados and "nome" in dados["autor"]:
```

`json_path` faz o mesmo em uma expressão, devolvendo o padrão se qualquer nível
faltar.

## CSV

```dataforge
Serde.records_to_csv(registros)     // lista de vaults → CSV com cabeçalho
Serde.csv_to_records(csv)           // CSV com cabeçalho → lista de vaults
Serde.to_csv(linhas, ",", cabecalho)
Serde.from_csv(texto, ",", yes)
```

As duas primeiras assumem que a primeira linha é cabeçalho e que cada linha vira
um vault — o formato natural para dados tabulares.

## TOML

Legível para humanos, ideal para configuração:

```dataforge
config := {"servidor": {"host": "localhost", "porta": 8080}}
Serde.to_toml(config)
```

```toml
[servidor]
host = "localhost"
porta = 8080
```

## Achatar e desachatar

```dataforge
Serde.flatten({"a": {"b": 1}})      // {"a.b": 1}
Serde.unflatten({"a.b": 1})         // {"a": {"b": 1}}
```

`flatten` é o que transforma um JSON aninhado em colunas de CSV. `unflatten`
reconstrói.

## JSON Lines

```dataforge
Serde.json_lines(registros)         // um objeto JSON por linha
Serde.from_json_lines(texto)
```

O formato de log e de exportação em lote: cada linha é independente, então dá
para processar em stream sem carregar o arquivo inteiro.

## Saída esperada

```
json: {"app": "DataForge", "versao": 4, "ativo": true, "t...
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
Bruno,25,ti
```

## Experimente

- Leia um CSV, transforme com pipeline e grave como JSON.
- Escreva `carregar_config(caminho)` com TOML e valores padrão.
