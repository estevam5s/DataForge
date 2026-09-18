# 254 — Tuplas

`Cluster` é uma **lista**: itens do mesmo tipo, quantidade livre, e ela
muda. `Tuple` é uma **forma**: uma casa por tipo, quantidade fixa, e ela
não muda.

| | Muda? | Conteúdo | Serve para |
|---|---|---|---|
| `Cluster` | sim | mesmo tipo, quantidade livre | uma lista de coisas |
| `Frozen` | não | mesmo tipo (`freeze([1, 2])`) | um cluster que não muda mais |
| `Tuple` | não | **um tipo por casa** | par, coordenada, retorno duplo |

## A única ambiguidade: `(1)` não é tupla

`(1)` é o número 1 entre parênteses — sem isso, `(2 + 3) * 2` deixaria de
ser 10. A tupla de um item se escreve `(7,)`, e a vazia, `()`.

## O tamanho faz parte do tipo

Em `Tuple<Integer, String>`, a **quantidade de argumentos é o tamanho**.
Uma tupla de três casas não é "uma tupla com um item errado": é outra
forma, e a mensagem diz isso. Quando a posição é que está errada, o erro
nomeia a casa (`place 0`).

É o tipo natural do retorno duplo:

```dataforge
action dividir(a: Integer, b: Integer) -> Tuple<Integer, Integer>:
    yield (a ~/ b, a % b)

inteiro, resto := dividir(17, 5)
```

Antes, isso obrigava a devolver um cluster (que não promete duas casas) ou
um vault (que obriga a nomear o que já tem ordem).

## Por que ela é hasheável

Porque é imutável. É isso que permite usá-la como **chave de vault** e
dentro de um `Set` — e é a razão prática de a tupla existir ao lado do
cluster. Um cluster não pode ser chave: ele mudaria, e a chave mudaria
com ele.

## Na fronteira do JSON

JSON não tem tupla: `to_json((1, "a"))` produz `[1, "a"]`, e o caminho de
volta traz um `Cluster`. A forma não sobrevive ao formato — quando ela
importa, declare `Tuple<…>` na entrada e converta ali.
