# Exercicio 149 — `observe` e eventos

## Enunciado

Reaja a valores conforme eles chegam, em vez de coletá-los primeiro.

## Conceitos

`observe` percorre uma fonte executando um bloco a cada item:

```dataforge
observe valor in [10, 20, 30]:
    recebidos.append(valor * 2)
```

A forma é a mesma de `cycle`, mas a intenção é diferente:

| | `cycle` | `observe` |
|---|---------|-----------|
| Intenção | percorrer uma coleção | reagir a itens que chegam |
| Fonte típica | lista pronta | stream, eventos, sensores |
| Leitura | "para cada item" | "sempre que chegar um item" |

Tecnicamente ambos funcionam sobre listas e streams. Usar `observe` sinaliza ao
leitor que a fonte é um fluxo, não uma coleção parada.

## `halt` e `skip`

Funcionam igual ao laço:

```dataforge
observe n in [1, 2, 3, 4, 5, 6, 7]:
    given n % 2 is 0:
        skip          // ignora este e vai ao próximo
    given n bigger 5:
        halt          // para de observar
    selecionados.append(n)
```

## `stream(colecao)`

Converte uma coleção pronta numa fonte:

```dataforge
fonte := stream([1, 2, 3])
observe v in fonte:
    soma += v
```

Útil para testar código que espera um fluxo, sem precisar escrever um
`stream action`.

## O padrão de assinantes

Quando os eventos não vêm de uma sequência, mas de chamadas espalhadas pelo
código, o desenho é outro — uma lista de funções e uma ação que as chama:

```dataforge
assinantes := []

action inscrever(fn):
    assinantes.append(fn)

action publicar(evento):
    cycle fn in assinantes:
        fn(evento)
```

Quem publica não sabe quem escuta, e quem escuta não sabe quem publica. É o
padrão Observer, e é a base de quase todo sistema de eventos.

Note que `inscrever(lambda e: log.append(...))` funciona porque a lambda é um
valor como qualquer outro — pode ser guardada numa lista e chamada depois.

## Saída esperada

```
[20, 40, 60]
[1, 3, 5]
[alerta: 31 graus]
[A viu inicio, B viu inicio, A viu fim, B viu fim]
```

## Experimente

- Faça `inscrever` devolver uma ação que cancela a inscrição.
- Acrescente um filtro: `inscrever_se(condicao, fn)`.
- Combine `observe` com um generator infinito e um `halt` na condição de parada.
