# Exercicio 122 — Ações com tipos

## Enunciado

Anote parâmetros e retorno de uma ação e observe que a mensagem de erro nomeia
exatamente o parâmetro que recebeu o tipo errado.

## Conceitos

A forma completa de uma ação tipada:

```dataforge
action nome(param: Tipo, outro: Tipo := padrao) -> TipoDeRetorno:
    yield valor
```

Três coisas passam a ser verificadas:

1. **Cada parâmetro** é checado no momento da chamada.
2. **O valor devolvido** é checado no `yield`.
3. **O analisador estático** avisa se a ação declara um retorno mas pode
   terminar sem `yield`.

## Por que a mensagem importa

Compare as duas formas de errar:

```
TypeError_: unsupported operand type(s) for *: 'str' and 'int'
```

contra o que o DataForge diz:

```
parameter 'largura' of action 'area_retangulo' declared as Number but got String
```

A segunda diz **onde** e **o quê**. É por isso que a checagem acontece na
fronteira da ação, e não lá dentro quando a conta explode.

## O tipo `Any`

`primeiro_item(itens: Cluster) -> Any` declara honestamente que o retorno
depende do conteúdo da lista. Usar `Any` é melhor que mentir um tipo específico.

## Saída esperada

```
12.0
oi oi oi
10 void
parameter 'largura' of action 'area_retangulo' declared as Number but got String
```

## Experimente

- Mude o retorno para `-> Integer` e veja o erro no `yield`.
- Remova o `yield void` do caminho da lista vazia e rode `dataforge check`.
