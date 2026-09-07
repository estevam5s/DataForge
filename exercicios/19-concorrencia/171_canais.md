# Exercicio 171 — Canais entre threads

## Enunciado

Passe valores entre threads com segurança, sem condição de corrida.

## O que é um canal

```dataforge
channel fila
fila.send(valor)
fila.receive()      // o próximo, ou void se estiver vazio
```

Uma fila FIFO **com trava interna**. `send` e `receive` são seguros de chamar de
qualquer thread — a implementação garante que dois envios simultâneos não se
atropelam.

## O padrão que resolve a corrida

O exercício anterior mostrou o problema: duas threads incrementando a mesma
variável perdem atualizações. A solução não é sincronizar o acesso — é **não
compartilhar**:

```dataforge
channel parciais

thread:
    soma := 0                  // variável local desta thread
    cycle _ in range(0, 1000):
        soma += 1
    parciais.send(soma)        // reporta uma vez, no fim
```

Cada thread trabalha no próprio escopo. Ninguém escreve onde outro lê. No fim, a
thread principal soma os parciais — e o resultado é 2000, sempre.

Essa ideia tem nome: *"não comunique compartilhando memória; compartilhe memória
comunicando"* — é o lema de Go, e vale igual aqui.

## Recolher tudo

Como `receive` devolve `void` quando a fila esvazia:

```dataforge
persist yes:
    item := canal.receive()
    given item is void:
        halt
    colhidos.append(item)
```

## Fila de trabalho

O mesmo canal serve para distribuir tarefas:

```dataforge
channel tarefas
cycle t in ["compilar", "testar", "empacotar"]:
    tarefas.send(t)

// vários trabalhadores podem consumir daqui
persist yes:
    t := tarefas.receive()
    given t is void:
        halt
    executar(t)
```

Cada tarefa vai para exatamente um consumidor — a trava garante isso.

## Limitação a conhecer

`receive` **não bloqueia**: devolve `void` na hora se a fila estiver vazia. Isso
significa que você precisa de um `wait` para dar tempo às threads produzirem,
como neste exercício.

Um `receive` bloqueante (que espera até chegar algo) está no roadmap. Hoje, para
sincronização precisa, prefira estruturar o programa de forma que o `wait` seja
suficiente — ou processe em lote.

## Saída esperada

```
primeiro
segundo

colhidos: 3
  tarefa A
  tarefa B
  tarefa C

total pelo canal: 2000
cada thread trabalhou no proprio escopo e reportou pelo canal

── processando a fila ──
  executando: compilar
  executando: testar
  executando: empacotar
  executando: publicar
```

## Experimente

- Monte um pool: N threads consumindo da mesma fila de tarefas.
- Use dois canais — um de entrada, um de saída — para um pipeline concorrente.
