# Exercicio 230 — Lavra: o N+1, os limites e a paginação

## Enunciado

Conte as idas ao banco e prove que o lote as junta numa só.

## O N+1, em uma frase

Uma consulta que pede 20 pedidos e, de cada um, o cliente, faz **21** consultas
ao banco: uma para os pedidos e uma por cliente.

```lavra
busca:
    pedidos:
        numero
        cliente:
            nome
```

O servidor parece rápido — cada consulta é de milissegundos — e o banco morre.
É o problema mais conhecido de qualquer camada de consulta, e o mais fácil de
introduzir sem perceber: a consulta acima tem cinco linhas.

## O lote, em uma frase

O resolvedor não **busca** — ele **pede**. Os pedidos feitos na mesma volta são
juntados num só:

```dataforge
action cliente_do_pedido(p, _args, ctx):
    yield Lavra.pedir(ctx, "clientes", p.cliente_id)
```

E o lote é declarado no contexto da consulta:

```dataforge
ctx := Lavra.contexto({})
_ := Lavra.lote(ctx, "clientes", buscar_clientes)
```

## Por que o teste conta a IDA, e não o resultado

Este é o ponto do exercício. Um lote que devolve o valor certo e mesmo assim
consulta vinte vezes **passa em qualquer teste que só olhe os dados**:

```dataforge
idas := []

action buscar_clientes(ids):
    idas.append(len(ids))
    yield [clientes[i] cycle i in ids]

...
assert len(idas) is 1, "UMA ida — sem o lote seriam 20"
```

O `r["extensoes"]["lotes"]` traz o mesmo número para se olhar em produção:

```
{clientes: {chamadas: 1, chaves: 20, economia: 19}}
```

## Duas decisões do lote

**O lote vive no contexto, e não no módulo.** Um lote de processo guardaria o
cliente depois que ele mudou, e serviria o valor velho para outra pessoa. O
contexto morre com a consulta, que é exatamente a vida útil que um cache de
leitura pode ter aqui.

**A ordem da resposta é a ordem do pedido.** A função recebe as chaves e devolve
os valores na MESMA ordem — ou um vault de chave para valor, que não depende de
ordem nenhuma. Uma lista fora de ordem é o bug clássico da técnica: cada pedido
recebe o cliente de outro, e **nada falha**.

## Os limites

Um grafo com ciclo deixa pedir `pedido.cliente.pedidos.cliente…` para sempre:

```dataforge
Lavra.limites(esq, profundidade := 8, complexidade := 1000, itens := 500)
```

| Limite | O que impede |
|--------|--------------|
| `profundidade` | a consulta funda num grafo com ciclo |
| `complexidade` | uma consulta curta que pede um milhão de itens |
| `itens` | um resolvedor que devolve a tabela inteira num dia de pico |

Os três são conferidos **antes** de resolver qualquer coisa. A consulta funda é
a forma mais barata de derrubar um servidor de consulta: cabe num tuíte, e o
servidor gasta tudo o que tem antes de responder.

## Paginação por cursor

Paginar por posição (`pule 3, traga 3`) quebra do jeito mais difícil de ver: se
alguém insere uma linha entre a página 1 e a 2, um item **desaparece** — ele
desceu para a posição que já foi lida.

```dataforge
p1 := Lavra.pagina(pedidos, primeiros := 3)
p2 := Lavra.pagina(pedidos, primeiros := 3, depois := p1["info"]["cursor_fim"])
```

Com cursor, a página seguinte começa exatamente onde a anterior parou.

## O erro parcial

```
[pedidos, 0, cliente, risco] | o servico de risco caiu
```

Quem pediu dois campos e teve problema em um recebe **um** — não zero. É a
diferença entre uma tela com um aviso e uma tela vazia. O `caminho` diz
exatamente qual campo quebrou.

## Saída esperada

```
20 pedidos, 1 ida(s) ao banco
{clientes: {chamadas: 1, chaves: 20, economia: 19}}
a consulta tem profundidade 3, e o limite é 2
[4, 5, 6]
[pedidos, 0, cliente, risco] | o servico de risco caiu
230 ok
```

## Para experimentar

- Tire o `Lavra.pedir` e busque direto no resolvedor. Veja `idas` ir para 20.
- Devolva `[clientes[i] cycle i in reversed(ids)]` no lote. O Lavra recusa, e
  diz por quê — porque esse é o único sintoma que a falha tem.
- Baixe `itens` para 5 e peça os 20 pedidos.
