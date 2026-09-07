# Exercicio 144 — Projeto: validador de dados

## Enunciado

Junte padrões de tipo, sequência e vault num validador que compara dados contra
um esquema declarado.

## O problema

Dados que vêm de fora — JSON de uma API, CSV, formulário — não têm garantia de
formato. Validar campo a campo com `given` espalhado pelo código não escala: a
regra fica misturada com a lógica de negócio, e cada campo novo exige mexer em
vários lugares.

A saída é **declarar o formato como dado** e escrever um interpretador para ele.

## O esquema

```dataforge
esquema_usuario := {
    "tipo": "Vault",
    "campos": {
        "nome": {"tipo": "String"},
        "idade": {"tipo": "Integer"},
        "tags": {"tipo": "Cluster", "de": {"tipo": "String"}}
    }
}
```

Três formas, recursivamente compostas:

| Forma | Significa |
|-------|-----------|
| `{"tipo": "String"}` | um valor daquele tipo |
| `{"tipo": "Cluster", "de": E}` | uma lista cujos itens seguem `E` |
| `{"tipo": "Vault", "campos": {…}}` | um objeto com aqueles campos |

## O validador

O `match` sobre o **esquema** escolhe a estratégia:

```dataforge
match esquema:
    point {"tipo": "Cluster", "de": interno}:
        // valida cada item contra 'interno'
    point {"tipo": "Vault", "campos": campos}:
        // valida cada campo declarado
    default:
        // tipo simples: compara com typeof
```

Repare que os dois primeiros padrões extraem exatamente o que precisam (`interno`,
`campos`) ao mesmo tempo em que identificam a forma.

## Caminhos nas mensagens

O parâmetro `caminho` acumula a posição:

```
raiz.nome: esperava String, veio Integer
raiz.tags[1]: esperava String, veio Integer
```

Isso transforma um relatório inútil ("dados inválidos") em algo acionável. Custa
um parâmetro a mais e paga por si na primeira vez que alguém precisa depurar um
JSON aninhado.

## Coletar em vez de parar no primeiro

O validador devolve **todos** os problemas, não só o primeiro. Quem preencheu um
formulário quer ver os três erros de uma vez.

## Saída esperada

```
── dados validos ──
[]

── dados invalidos ──
  raiz.nome: esperava String, veio Integer
  raiz.idade: campo obrigatorio ausente
  raiz.tags[1]: esperava String, veio Integer

3 problema(s) encontrados
```

## Experimente

- Acrescente `{"tipo": "String", "opcional": yes}` e trate campos opcionais.
- Adicione validação de faixa: `{"tipo": "Integer", "min": 0, "max": 150}`.
- Faça o validador aceitar `{"tipo": "Enum", "valores": [...]}`.
