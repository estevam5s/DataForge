# Exercicio 169 — Ações assíncronas

## Enunciado

Declare ações `async` e aguarde o resultado com `await`.

## Conceitos

```dataforge
async action buscar_usuario(id):
    yield {"id": id, "nome": $"Usuario {id}"}

usuario := await buscar_usuario(7)
```

Chamar uma ação `async` **começa o trabalho** numa thread e devolve a *tarefa*.
`await` espera ela terminar e entrega o valor.

## Para que serve

Representar trabalho que **espera** por algo externo — rede, disco, banco.
Enquanto uma operação espera, o programa faz outra.

Só que escrito assim, uma de cada vez, `async` não compra nada: o `await` na
linha seguinte cancela qualquer sobreposição. O ganho está em **chamar todas
antes de aguardar qualquer uma**:

```dataforge
// as quatro comecam aqui
tarefas := [demorada(n) cycle n in [1, 2, 3, 4]]

// e aqui so se espera a mais lenta
valores := await tarefas
```

| Como está escrito | Quatro esperas de 0,1 s custam |
|---|---|
| `tarefas := [...]` e depois `await tarefas` | **0,1 s** |
| `cycle` com `await` dentro | **0,4 s** |

O exercício mede as duas formas e compara. Rode e veja.

## O que acelera e o que não

As tarefas são threads. Elas se sobrepõem enquanto uma está **esperando algo de
fora**. Para contas, não — o GIL do Python deixa uma thread por vez executar
código, e vinte tarefas somando números levam o mesmo tempo que uma.

- entrada e saída (rede, disco, banco, `sleep`) → `async`
- trabalho de CPU → `Arcane.Concurrent`, que usa processos

## A tarefa não é o valor

O engano mais comum de quem escreve código assíncrono, em qualquer linguagem:

```dataforge
u := buscar_usuario(1)
out u["nome"]          // erro: 'u' e a tarefa, nao o vault
```

A linguagem aponta a linha e diz a palavra que faltou.

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

- cancelamento de tarefa em andamento
- `await` com prazo — hoje ele espera o tempo que for
- `Mutex`, `Semaphore`, `Atomic`

Aguardar várias ao mesmo tempo **já existe**: `await` sobre um cluster de
tarefas espera todas. Para dividir trabalho de CPU, veja `thread`, `channel` e
`Arcane.Concurrent` (próximos exercícios).

## Saída esperada

```
usuario: Usuario 7
pedidos: 2

{nome: Usuario 7, pedidos: 2, total_gasto: 330.0}

erro capturado: a busca falhou

[Usuario 1, Usuario 2, Usuario 3]

juntas:    0.1s
uma a uma: 0.4s
```

Os dois tempos variam com a máquina; o que não varia é a diferença entre eles.

## Experimente

- Escreva uma cadeia de três ações async que dependem uma da outra.
- Combine `await` com `retry` para uma busca que pode falhar temporariamente.
- Troque `T.sleep(0.1)` por uma conta pesada e meça de novo: o ganho some, e
  esse é o limite do GIL aparecendo.
