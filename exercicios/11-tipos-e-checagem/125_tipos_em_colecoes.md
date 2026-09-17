# Exercicio 125 — Tipos dentro de coleções

## Enunciado

Combine anotações com listas e dicionários, e escreva validação para o que a
anotação não cobre.

## Conceitos

Uma anotação de coleção descreve **o recipiente**, não o conteúdo:

```dataforge
notas: Cluster := [7.5, 8.0]      // "é uma lista" — nada diz sobre os itens
```

Quando o conteúdo é uma regra de **tipo**, a anotação resolve:
`notas: Cluster<Float> := [7.5, 8.0]` confere cada item e recusa um `append`
fora do tipo. Este exercício é sobre o que a anotação **não** alcança — uma
regra de valor (nota entre 0 e 10), ou dados que chegam de fora como texto —,
e escrever essa validação é útil por si só.

## Duas estratégias

**Verificar tudo antes de usar:**

```dataforge
action todos_numeros(valores: Cluster) -> Boolean:
    cycle v in valores:
        given typeof(v) isnt "Integer" and typeof(v) isnt "Float":
            yield no
    yield yes
```

**Coletar todos os problemas e reportar juntos:**

```dataforge
action validar_aluno(dados: Vault) -> Cluster:
    problemas := []
    given "nome" not in dados:
        problemas.append("falta o nome")
    ...
    yield problemas
```

A segunda é quase sempre melhor para entrada de usuário: quem preencheu um
formulário quer ver os cinco erros de uma vez, não um por vez.

## O detalhe do `orif`

Repare:

```dataforge
given "nome" not in dados:
    problemas.append("falta o nome")
orif typeof(dados["nome"]) isnt "String":
    problemas.append("nome deve ser String")
```

O `orif` é essencial: sem ele, o segundo teste rodaria mesmo quando a chave não
existe, e `dados["nome"]` estouraria. `orif` só é avaliado se o `given` foi
falso — ou seja, se a chave existe.

## Saída esperada

```
media das notas: 8.33
so numeros? yes
e com texto? no
[]
[falta o nome, nota deve ser numero]
```

## Experimente

- Escreva `validar_aluno` devolvendo um `Vault` com `{"ok": …, "erros": …}`.
- Use `Arcane.Collections.partition` para separar válidos de inválidos numa lista.
