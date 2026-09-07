# Exercicio 169 — Ações assíncronas

## Enunciado

Declare ações `async` e aguarde o resultado com `await`.

## Conceitos

```dataforge
async action buscar_usuario(id):
    yield {"id": id, "nome": $"Usuario {id}"}

usuario := await buscar_usuario(7)
```

`async` marca a ação como assíncrona; `await` resolve o resultado.

## Para que serve

A ideia é representar trabalho que **espera** por algo externo — rede, disco,
banco. Enquanto uma operação espera, o programa poderia fazer outra coisa.

Em DataForge 4.0 o modelo é simples: `await` resolve a corrotina de forma
síncrona. Isso significa que a estrutura do código já está correta para quando o
agendamento paralelo chegar (está no roadmap), mas hoje não há ganho de
desempenho real em `await` sequenciais.

Seja honesto sobre isso ao escrever código: use `async` onde a semântica é de
espera, não esperando aceleração automática.

## Compor

```dataforge
async action perfil_completo(id):
    u := await buscar_usuario(id)
    p := await buscar_pedidos(id)
    yield {...}
```

Uma ação `async` pode aguardar outras. O resultado se lê de cima para baixo, como
código síncrono — que é justamente a razão de `async/await` existir em vez de
callbacks aninhados.

## Erros

`await` propaga o erro normalmente:

```dataforge
monitor:
    await pode_falhar(yes)
handle e:
    out $"erro capturado: {e.message}"
```

Nada de especial: o `monitor` funciona igual ao redor de código síncrono.

## O que ainda não existe

O roadmap prevê, e vale saber que **ainda não está aqui**:

- `TaskGroup` para aguardar várias tarefas em paralelo
- cancelamento de tarefa em andamento
- `Mutex`, `Semaphore`, `Atomic`

Para paralelismo real hoje, use `thread` e `channel` (próximos exercícios).

## Saída esperada

```
usuario: Usuario 7
pedidos: 2

{nome: Usuario 7, pedidos: 2, total_gasto: 330.0}

erro capturado: a busca falhou

[Usuario 1, Usuario 2, Usuario 3]
```

## Experimente

- Escreva uma cadeia de três ações async que dependem uma da outra.
- Combine `await` com `retry` para uma busca que pode falhar temporariamente.
