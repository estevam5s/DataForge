# 228 — Saga: não existe transação que atravesse a rede

## O problema, em uma frase

`BEGIN` no serviço de estoque não alcança o de cobrança.

```
  serviço de estoque          serviço de cobrança
  ┌──────────────────┐        ┌──────────────────┐
  │ BEGIN            │        │                  │
  │   reserva -2     │        │                  │
  │ COMMIT           │        │                  │
  └──────────────────┘        └──────────────────┘
          │                            │
          └──────── e agora? ──────────┘
```

Se a reserva passou e a cobrança falhou, o produto fica preso. Não há
`rollback` que chegue ao outro banco — e nem deveria: um `BEGIN` distribuído
pediria que cada serviço segurasse uma transação aberta esperando os outros, o
que transforma a queda de um na queda de todos.

A resposta correta é **compensar**: cada passo declara como se desfaz.

## O desenho

```dataforge
s := Malha.saga("checkout")
s.passo("reservar", reservar, liberar)
s.passo("cobrar",   cobrar,   estornar)
s.passo("despachar", despachar, cancelar_despacho)

r := s.executar({"sku": "CAF-500", "quantidade": 2, "limite": 100.0})
```

```
reservar ──▶ cobrar ──▶ despachar
                            │
                          falhou
                            │
            ◀─── estornar ◀─┘
   liberar ◀───
```

Cada passo recebe **dois** argumentos: o estado acumulado da saga e a chave de
idempotência daquele passo.

```dataforge
action reservar(estado, chave):
    estoque[estado["sku"]] := estoque[estado["sku"]] - estado["quantidade"]
    reservas[chave] := estado["quantidade"]
    yield {"reserva": chave}        // o vault entra no estado
```

Um passo que devolve vault **funde** o resultado no estado — é assim que
`cobrar` lê o que `reservar` produziu. Um passo que não precisa de um dos
argumentos escreve `_estado` ou `_chave`; o linter cobra isso, e com razão: a
assinatura é fixa, e o `_` é a declaração de que a omissão é deliberada.

## Três coisas que a diferenciam de um `monitor` com `ensure`

### 1. A compensação roda em ordem inversa

```dataforge
assert r2["desfeitos"] is ["cobrar", "reservar"]
```

Não é detalhe estético. Estornar a cobrança **antes** de liberar o estoque
deixa uma janela em que o cliente não tem dinheiro nem produto. A ordem inversa
é a única que mantém o sistema num estado defensável em cada instante do
desfazimento.

**O passo que falhou não é compensado.** Ele não concluiu, e desfazer o que não
aconteceu é o outro lado do mesmo bug — um estorno de cobrança que nunca
existiu devolve dinheiro que nunca foi cobrado.

### 2. Uma compensação que falha não é engolida

```dataforge
assert len(r3["orfas"]) is 1
assert r3["orfas"][0]["passo"] is "cobrar"
```

Um estorno que não passa deixa o sistema inconsistente, e isso precisa chegar a
um humano. `ok` continua `no` mesmo que o resto tenha desfeito.

E as compensações **seguintes ainda rodam**: o estoque preso por um estorno que
não passou seria um segundo problema criado pelo primeiro.

### 3. Cada passo tem chave de idempotência estável

```dataforge
s4 := Malha.saga("checkout", "pedido-4711")
assert s4.chave_de("cobrar") is "pedido-4711:cobrar"
```

Derivada do id da saga mais o nome do passo — **estável entre execuções**. É o
que permite reprocessar uma fila: a saga roda de novo, `cobrar` reconhece a
chave e não cobra duas vezes.

```dataforge
action cobrar(estado, chave):
    given chave in chaves_vistas:
        yield {"cobranca": chaves_vistas[chave], "repetida": yes}
    …
```

**A saga dá a chave; quem honra é o outro lado.** No exercício, `cobrar` honra e
`reservar` não — e o resultado é visível:

```dataforge
assert len(cobrancas) is 1       // cobrou uma vez
assert estoque["CAF-500"] is 6   // mas debitou DUAS
```

Idempotência é uma promessa que cada serviço faz por si. A saga não pode
fabricá-la.

## `conferir()` — antes de executar

```dataforge
s6 := Malha.saga("risco")
s6.passo("consultar", lambda e, c: {"score": 700}, escreve := no)
s6.passo("marcar", lambda e, c: void)
assert s6.conferir() is ["marcar"]
```

Um passo que escreve e não declara compensação não falha em teste feliz. Ele
aparece no dia em que o passo seguinte falha — e aí já escreveu. `conferir()`
devolve a lista antes de rodar.

`escreve := no` é a declaração de que o passo não precisa de compensação: uma
leitura, um log, uma consulta de score.

## O diário, e por que a cada passo

```dataforge
s7 := Malha.saga("checkout", "p-1", lambda linha: linhas.append(linha))
…
assert situacoes is ["feito", "feito", "falhou", "desfeito", "desfeito"]
```

O terceiro argumento é onde escrever cada linha — um arquivo, uma tabela, o
`Arcane.Logging`. Gravado a **cada passo**, e não no fim: uma queda do processo
no meio da saga perderia o que já foi feito, e ninguém saberia o que compensar.
Cada linha leva o `rastro` do contexto (exercício 227), o que liga o diário da
saga ao log dos serviços que ela chamou.

Um diário que não grava **não derruba a saga** — ela está no meio de escritas
reais em serviços reais, e falhar por causa do log seria trocar um problema
pequeno por um grande.

## O que a saga não faz

**Não há isolamento.** Entre `reservar` e `cobrar`, outro pedido vê o estoque já
reservado. Uma saga troca atomicidade por disponibilidade, e essa troca é o
ponto, não um defeito: quem precisa de isolamento precisa de um banco (módulo
29), não de microserviços.
