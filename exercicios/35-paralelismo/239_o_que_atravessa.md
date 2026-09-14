# Exercicio 239 — O que atravessa para o outro processo

## Enunciado

Descubra o que viaja junto com a ação para outro processo, e o que fica.

## A regra

Um processo recebe o trabalho por **cópia**. O que atravessa não é a ação — é a
**declaração** dela, mais os nomes que ela lê e não cria, mais tudo o que esses
nomes alcançam.

```dataforge
steady TAXA := 0.08

record Pedido:
    cliente: String
    valor: Float

action imposto(v):
    yield v * TAXA

action emitir(p):
    yield Nota(p.cliente, p.valor + imposto(p.valor))

P.map_processos(emitir, pedidos)
```

Atravessam junto, sem que nada disso precise ser dito:

- a `steady TAXA`, porque `imposto` a lê
- a ação `imposto`, porque `emitir` a chama
- os `record` e o `enum`, porque são construídos lá dentro
- o módulo `Arcane.Math` — **pelo nome**: o outro lado o carrega de novo, em vez
  de recebê-lo copiado

## O record que volta é o mesmo tipo

```dataforge
copia := notas[0] with {"cliente": "outro"}
```

`with` confere os campos contra o record. Se o processo filho devolvesse uma
**cópia** do tipo, essa linha recusaria o próprio resultado — e o erro falaria
de um `Nota` que não é o `Nota`, o que é impossível de entender.

## O que não atravessa

Uma conexão de banco, um arquivo aberto, um socket, um mutex, um canal e uma
tarefa existem no processo que os abriu. Copiá-los não faria sentido: o outro
lado ganharia um número de descritor que lá não aponta para nada.

```
erro[DF1001]: 'banco' cannot cross into another process
  = nota: it holds a connection to a database, which exists only in
          the process that opened it
  = dica: open it INSIDE the action — each process opens its own — or
          use 'map', which uses threads and shares memory
```

A mensagem chama a **variável pelo nome**. Isso importa mais do que parece: a
mensagem antiga citava um objeto interno da biblioteca (`<locals>.<lambda>`) e
mandava "declarar a ação no topo do arquivo" — que era onde ela já estava.

## A saída: abrir dentro da ação

```dataforge
action abre_o_proprio(n):
    meu := DB.connect(":memory:")
    …
```

Cada processo abre o seu. É também o desenho certo para um banco de verdade:
uma conexão compartilhada entre processos seria um gargalo, mesmo se pudesse
ser copiada.

## O que a análise NÃO faz

Um recurso que a ação não usa não atrapalha:

```dataforge
_trava := P.mutex()
_canal := P.canal()

action nao_usa_nada_de_fora(n):
    yield n * 10           // atravessa sem problema
```

A varredura de nomes livres é **generosa de propósito** — na dúvida, captura —
e por isso um nome que não pôde atravessar só vira erro **quando a ação
realmente o usa**. Reclamar na hora seria falso alarme, e falso alarme ensina a
desligar a verificação.

## Onde isso continua

- [`238_varios_nucleos.df`](238_varios_nucleos.df) — a medida que prova o ganho
- [`240_pipeline_em_blocos.df`](240_pipeline_em_blocos.df) — o desenho completo
