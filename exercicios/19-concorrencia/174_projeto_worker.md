# Exercicio 174 — Projeto: fila de trabalho

## Enunciado

Monte um sistema de tarefas com fila de prioridade, execução com retentativa e
relatório.

## A arquitetura

```
MODELO       enum Estado, record Tarefa
FILA         Col.priority_queue
EXECUCAO     retry + registro de estado
RELATORIO    agregação por estado e prioridade
```

## Fila de prioridade

```dataforge
fila := Col.priority_queue()
fila.push(tarefa, tarefa.prioridade)
t := fila.pop()      // sempre a de MENOR número
```

Menor número = mais urgente. A convenção pode parecer invertida, mas é a
tradicional: "prioridade 1" é o topo da lista.

Isso permite inserir em qualquer ordem e sempre tirar a certa. No exercício,
`alerta de seguranca` (p1) sai antes de `backup` (p9), mesmo tendo entrado
depois.

## Estado como enum

```dataforge
enum Estado:
    Pendente
    Executando
    Concluida
    Falhou
```

Comparado a guardar `"concluida"` como texto: um erro de digitação vira erro na
hora, e `Estado.names()` dá a lista completa para o relatório sem repetição.

## Retentativa por tarefa

```dataforge
retry 2:
    saida := executar(t)
    resultado["estado"] := Estado.Concluida
handle e:
    resultado["estado"] := Estado.Falhou
    resultado["detalhe"] := e
```

O `retry` fica em volta de **uma** tarefa. Uma falha não interrompe a fila — ela
é registrada e o laço segue para a próxima. Um `monitor` em volta do laço inteiro
abortaria tudo na primeira falha.

## Registrar o resultado, não só o sucesso

```dataforge
historico.append({"tarefa": t, "estado": ..., "detalhe": ...})
```

Guardar o histórico completo é o que torna o relatório possível. Sem ele, você
saberia que "algo falhou", mas não o quê nem por quê.

## Reenfileirar com prioridade máxima

```dataforge
cycle h in falhadas:
    fila.push(h["tarefa"], 0)
```

Tarefas que falharam voltam com prioridade 0 — à frente de tudo. Numa fila real,
isso precisaria de um contador de tentativas para não gerar um laço infinito com
tarefas que sempre falham.

## Histograma em texto

```dataforge
out $"  {nome_estado.pad_end(12)} {"#".repeat(quantos)} ({quantos})"
```

## Saída esperada

```
┌──────────────────┐
│ Fila de Trabalho │
└──────────────────┘
tarefas na fila: 6

── processando por prioridade ──
  [p1] ERR processar pagamento    gateway indisponivel
  [p1] ok  alerta de seguranca    alerta de seguranca concluida
  [p5] ok  enviar email           enviar email concluida
  [p7] ok  limpar cache           limpar cache concluida
  [p8] ok  gerar relatorio        gerar relatorio concluida
  [p9] ok  backup                 backup concluida

┌───────────┐
│ Relatorio │
└───────────┘
total:      6
concluidas: 5
falhadas:   1

ordem de execucao (prioridade): [1, 1, 5, 7, 8, 9]

── por estado ──
  Concluida    ##### (5)
  Falhou       # (1)

── reenfileirando falhas ──
  processar pagamento volta com prioridade maxima
```

## Experimente

- Acrescente um contador de tentativas e descarte após 3 falhas.
- Use `thread` + `channel` para processar várias tarefas em paralelo.
- Persista o histórico com `Arcane.Database`.
