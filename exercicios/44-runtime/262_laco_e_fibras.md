# 262 — o laço de eventos, o escalonador e as fibras

`async/await` nesta linguagem é **uma thread por tarefa**. Serve para o
que foi feito — sobrepor entrada e saída — e não escala: mil conexões
simultâneas são mil threads do sistema, e a conta aparece na memória e no
escalonador do SO antes de aparecer no programa. O Kiln atende **um
pedido por thread** pelo mesmo motivo.

O outro modelo é o **reator**: uma thread que dorme num seletor do
sistema — `epoll` no Linux, `kqueue` no macOS e no BSD, `select` no
Windows — e acorda quando algum descritor tem trabalho.

## O número

Um servidor de linha, uma requisição por conexão, medido contra o mesmo
servidor com uma thread por conexão:

| Conexões | Laço de eventos | Thread por conexão |
|---|---|---|
| 400 | 33 ms · **1 thread** · +0 MB | 43 ms · 400 threads · +14 MB |
| 1000 | 73 ms · **1 thread** · +1 MB | 83 ms · 1000 threads · +36 MB |
| 2000 | 151 ms · **1 thread** · +0 MB | 161 ms · 2000 threads · +36 MB |

**O tempo quase empata, e a memória é que conta a história.** Nesta
máquina duas mil threads ainda funcionam, e a diferença de tempo fica em
~1,1×. O que muda é a **forma da conta**: o custo do laço é plano, o do
modelo de threads é linear (~36 KB por thread). Num contêiner com limite
de threads, ou com trabalho de verdade por conexão, um falha onde o outro
nem percebe.

Publicar o 1,1× é mais honesto que publicar só o caso em que o outro
modelo já quebrou.

## Ele não gira em vão

É a diferença entre um reator e uma espera ocupada, e é **testada**: com
um único temporizador, o número de voltas tem de ser pequeno. Um laço de
espera ocupada daria milhões e queimaria um núcleo sem fazer nada.

## As três filas

| Fila | O que resolve |
|---|---|
| **poller** (`selectors`) | dormir até haver E/S, em vez de girar |
| **prazos** (heap) | `apos` e `a_cada` sem uma thread por relógio |
| **prontas** | a ordem de execução, e onde a contrapressão mora |

E uma quarta que quase sempre falta num reator escrito à mão: o
**executor**. Um trabalho que bloqueia dentro do laço trava tudo — não só
aquela tarefa, mas toda conexão aberta. `L.executar` manda para um pool e
devolve o resultado pela fila, que é a única forma de o laço continuar
girando.

Para isso funcionar, `agendar` chamado de outra thread precisa **acordar
o laço**. É o truque clássico do autocano (*socketpair*): um seletor
acorda por **descritor**, e uma fila em memória não é um descritor.

## Contrapressão, e o erro que não derruba

Uma fila sem teto troca **falha visível** por **morte por memória** — que
é muito pior de diagnosticar, porque acontece longe da causa. Com teto,
`agendar` devolve `no` e quem chama decide.

E um reator que morre no primeiro erro derruba o servidor inteiro, sendo
que o erro costuma ser de **uma** conexão. Aqui ele é contado, guardado
com o tipo e o texto, e o laço segue.

## Fibras — e elas são reais

Um `stream action` da linguagem **já é** um gerador do Python, e o
interpretador suspende o corpo dele em cada `emit`. O escalonador dirige
esse gerador: o valor emitido diz **o que a fibra está esperando**, e a
troca de contexto é o quadro do gerador.

Duas fibras cedendo o controle produzem `A1 B1 A2 B2 A3 B3`. Se fossem
sequenciais seria `A1 A2 A3 B1 B2 B3` — é isso que prova o escalonamento
cooperativo.

`emit` é **instrução**, não expressão: não devolve valor para a fibra. O
laço entrega por um vault que ela passou — a **caixa**. Ser explícito
aqui é melhor que fingir o contrário.

E cancelar uma fibra fecha o gerador, o que roda os `defer` do corpo. Uma
thread do sistema não se cancela assim: é a vantagem concreta de a fibra
ser um objeto, e não um recurso do SO.

## Sem pilha — e isso tem nome

**Um `emit` dentro de uma ação chamada NÃO suspende a fibra.** Só o
`emit` do corpo da própria fibra suspende.

É a limitação de toda corrotina **sem pilha** (*stackless*) — a mesma dos
iteradores do C# e do `yield` do Python. Suspender dentro de uma chamada
exige pilha própria, e isso quer dizer troca de contexto em assembly ou
uma extensão em C: as duas fora de uma linguagem sem dependência externa.

É por isso que a documentação diz **fibra** e não *green thread*.

## O que NÃO existe

- **work stealing** entre laços: cada laço é uma thread, e com o GIL o
  ganho some antes de aparecer.
- **`io_uring`**: só Linux, e pelo CPython exigiria extensão em C.
- **IOCP no Windows**: ali o `selectors` usa `select`, com teto de 512
  descritores. É o limite desta forma, e está dito em vez de escondido.
- **prioridade por tarefa**: a fila é FIFO. Prioridade sem inversão de
  prioridade é mais difícil do que parece.
- **mais de um núcleo**: o laço é uma thread só, e o GIL continua no
  caminho. Para CPU, `P.map_processos`.

## Quando usar qual

| Precisa de | Use |
|---|---|
| sobrepor duas ou três chamadas de rede | `async`/`await` — mais simples, e o custo não aparece |
| milhares de conexões abertas ao mesmo tempo | **este módulo** |
| usar mais de um núcleo | `P.map_processos` |
| servir HTTP com rota e template | Kiln — thread por pedido, e para a maioria isso basta |
