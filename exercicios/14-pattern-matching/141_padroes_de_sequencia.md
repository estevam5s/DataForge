# Exercicio 141 — Padrões de sequência

## Enunciado

Desmonte listas por posição, com tamanho fixo ou separando cabeça e cauda.

## Conceitos

Colchetes num `point` formam um **padrão de sequência**:

```dataforge
point []:                    // exatamente vazia
point [unico]:               // exatamente um item
point [a, b]:                // exatamente dois
point [primeiro, ...resto]:  // um ou mais
```

O padrão casa pelo **comprimento** e liga cada posição a um nome.

## Só sequências de verdade

Um vault é iterável, mas **não** casa com `[…]`:

```dataforge
descrever({"a": 1})     // "nao e lista"
```

Isso é deliberado: um vault casa com `{…}`, uma lista com `[…]`. Sem essa
separação, `point [a, b]` capturaria dicionários de duas chaves por acidente — um
bug difícil de enxergar.

## Literais dentro do padrão

Você pode misturar literais e capturas:

```dataforge
point ["mover", direcao, passos]:
    yield $"mover {passos} para {direcao}"
```

Casa só se o primeiro elemento for exatamente `"mover"` **e** houver três
elementos. É a forma natural de interpretar comandos.

## Padrões aninhados

```dataforge
point [nome, [x, y]]:
    yield $"{nome} em ({x}, {y})"
```

Um padrão dentro do outro, na profundidade que precisar.

## Cabeça e cauda: o padrão recursivo

```dataforge
action somar(lista):
    match lista:
        point []:
            yield 0
        point [cabeca, ...cauda]:
            yield cabeca + somar(cauda)
```

Dois casos e a função está completa: a lista vazia (caso base) e "um elemento
mais o resto" (caso recursivo). É como se escreve sobre listas em Haskell, Elixir
e Erlang.

Para listas grandes, prefira `>> distill` — a recursão consome pilha e o limite é
1000 quadros.

## Saída esperada

```
vazia
um item: 7
par: 1 e 2
comeca com 1, mais 3
nao e lista
origem em (0, 0)
mover 3 para norte
parando
dizendo: ola mundo
comando desconhecido
soma recursiva: 15
```

## Experimente

- Adicione `point [a, b, c]` e veja onde colocá-lo para ser alcançado.
- Escreva `inverter(lista)` usando cabeça e cauda.
- Reescreva `somar` com `>> distill` e compare em `[1..2000]`.
