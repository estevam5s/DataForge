# Exercicio 172 — Canais entre threads

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

## Perguntar ou esperar

`receive()` **não espera**: devolve `void` na hora se a fila estiver vazia. É por
isso que a primeira parte do exercício precisa de um `wait` — ele dá tempo às
threads, e é um chute de quanto tempo basta.

Para esperar pelo item, passe o prazo:

```dataforge
fila.receive()          // void na hora, se vazio
fila.receive(2000)      // espera até 2 segundos; depois, void
fila.receive(void)      // espera o que for preciso
```

A última parte do exercício usa `receive(5000)`: o consumidor dorme até cada
pedido chegar, sem gastar CPU num laço e sem adivinhar quanto tempo basta.
O prazo é em **milissegundos**, a mesma unidade de `sleep`.

O padrão sem argumento continua não esperando **de propósito**: mudá-lo não
daria erro em programa nenhum, daria **travamento** — o pior tipo de falha,
porque não deixa mensagem nem pilha para investigar.

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
