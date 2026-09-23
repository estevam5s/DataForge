# 398 — Tipos literais

## O que ele resolve

Uma lista fechada de valores é a coisa mais comum que existe num
programa: o estado de um pedido, o método HTTP, o nível de um log. Antes
do tipo literal ela era escrita assim:

```dataforge
action mudar(e):
    given e is not "ativo" and e is not "inativo":
        trigger $"estado invalido: {e}"
    ...
```

Em toda fronteira. E esquecida numa delas — que é onde o dado errado
entra.

## A forma

```dataforge
type Estado := "ativo" | "inativo" | "suspenso"
```

Texto, inteiro, decimal e booleano podem ser literais. `void` fica de
fora de propósito: `Void` já é o tipo dele, e `type T := void` seria uma
segunda forma de dizer a mesma coisa.

## Onde ele é cobrado

| Momento | O que acontece |
|---|---|
| `dataforge check`, com o **literal** na mão | acusa, e lista os valores que valem |
| `dataforge check`, com uma variável | **cala** — não há o que provar |
| execução, em toda fronteira | recusa, nomeando o tipo e o que chegou |

O silêncio do meio é o recurso. Um `String` que veio de `input()` não
prova nada, e acusá-lo recusaria justamente o código para o qual o tipo
existe: ler a entrada e passá-la adiante, deixando a fronteira decidir.

## Duas armadilhas

**`yes` e `1` não se confundem.** Em Python `True == 1` é verdadeiro.
Sem conferir o *tipo* junto com a igualdade, um `type Ligado := yes`
aceitaria o número 1 calado.

**As aspas fazem parte do tipo.** Sem elas, `type T := "Integer"` e
`type T := Integer` virariam a mesma string — e o primeiro, que só
aceita a palavra `"Integer"`, passaria a aceitar qualquer número.

## Quando usar `enum` em vez disto

Quando o valor é um conceito do domínio com nome próprio, quando você
quer método, `.name`, `.value`, ou exaustividade no `match`. O tipo
literal é para quando o valor **é** o dado — vem de um JSON, de uma
coluna, de um `?estado=`.
