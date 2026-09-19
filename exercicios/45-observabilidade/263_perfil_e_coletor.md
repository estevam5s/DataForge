# 263 — medir com rigor, e o coletor sob controle

`Arcane.Bench` responde "quanto tempo leva" com uma **média**. É o que
quase toda ferramenta de benchmark faz, e é onde quase toda decisão de
performance erra:

- **a média esconde a cauda**, e é a cauda que o usuário sente. Cem
  requisições de 10 ms e uma de 1000 ms dão média 20 ms — e quem pegou a
  última esperou um segundo;
- **duas médias diferentes podem ser a mesma coisa com ruído**, e sem
  teste estatístico não há como saber;
- **um número sozinho não responde "piorou desde a semana passada?"**.

## Percentis, e por que sem interpolar

`P.medir` devolve a distribuição: `p50`, `p90`, `p95`, `p99`, `p999`,
`min`, `max`, `media`, `desvio` e `vazao`.

O **aquecimento é separado e declarado**. As primeiras execuções medem
cache frio, import preguiçoso e alocação inicial: misturá-las com o resto
não é medir o programa, é medir a **partida**.

E o percentil sai da amostra **por posto**, não de uma interpolação.
Interpolar inventa um valor que não aconteceu — num P99 de latência o que
se quer é uma medida que **existiu**.

## O teste que importa

**Comparar uma ação com ela mesma não pode dar "3% mais rápida".** É o
que separa medição de superstição.

```dataforge
igual := P.comparar(consulta, consulta, {"amostras": 40})
assert igual["mais_rapido"] is "empate"
```

A conta é o **Mann-Whitney U**, e não o teste t. Tempo de execução não é
normal: tem cauda longa à direita, piso duro à esquerda (nada roda em
tempo negativo) e picos de escalonamento. Um teste t supõe normalidade e
responde com confiança sobre uma suposição falsa. O U não supõe nada
sobre a forma — ele compara **ordens** —, e a correção de empates importa
quando o relógio tem resolução grossa.

E as duas medições são **intercaladas**: medir A inteiro e depois B
inteiro faz uma queda de clock no meio virar "B é mais lenta". Alternar
espalha a deriva da máquina pelos dois lados.

`p_valor` diz **se** há diferença; `sobreposicao` diz **quanto** — é o
tamanho do efeito, e é o que o `p` não diz.

## Regressão, e duas escolhas que mantêm o CI utilizável

- **A primeira medida nunca reprova.** Sem base guardada não há
  regressão, só um começo. Reprovar ali faria todo CI novo nascer
  vermelho, e a primeira coisa que se faz com um CI vermelho por desenho
  é desligá-lo.
- **A tolerância é obrigatória.** Sem ela, todo CI fica vermelho por
  ruído de máquina — o que dá no mesmo.

## O que nenhum perfil de CPU mostra

**Pausa do coletor**: é o que transforma um P50 bom num P99 ruim, e não
aparece em medida que olhe só o tempo total. `gc.callbacks` entrega o
começo e o fim de cada coleta — é a medida na fonte.

**Contenção de trava**: a thread bloqueada **não gasta CPU nenhuma**.
Ela aparece como latência que ninguém explica, e a única forma de vê-la é
medir na própria trava. A distinção entre "peguei na hora" e "esperei" é
feita por uma tentativa sem bloqueio antes da aquisição real — sem ela,
toda aquisição contaria como espera.

## O coletor, e a distinção que quase todo mundo erra

No CPython quem libera é a **contagem de referência**, e ela roda na
hora. O **coletor** existe só para o **ciclo**: `a` apontando para `b`
que aponta para `a`.

**Desligar o coletor não vaza memória em geral** — só deixa o ciclo para
trás. É por isso que desligá-lo num trecho curto e sensível a latência é
técnica segura, e não gambiarra.

`Mem.sem_gc` religa **mesmo se o corpo falhar**. Não é detalhe: deixar o
coletor desligado por causa de um erro é muito pior que a pausa que se
queria evitar, e o programa seguiria assim até terminar sem nada
denunciando.

`Mem.gc_congelar` tira o que **já vive** das varreduras para sempre — o
que um servidor faz depois da carga e antes do primeiro pedido.

## Arena

**Não é um allocator**: quem aloca continua sendo o Python, e não há como
trocá-lo por dentro. O que a arena troca é o **padrão de uso** — em vez
de criar e descartar por volta, um lote é preparado, emprestado e
devolvido.

| Decisão | Por quê |
|---|---|
| ela **cresce** quando acaba, e **conta** | travar seria pior; crescer calado esconderia que foi dimensionada errada |
| devolver o que não veio dela é **recusado** | o lote cresceria com estranhos, e o próximo `pegar` entregaria um deles |
| `limpar` solta o lote inteiro numa chamada | é o tempo de vida de arena da literatura |

**O ganho aparece quando o objeto é caro de montar**, não quando é um
vault de três chaves. Meça antes com `P.comparar`, e só mantenha se a
diferença for **significativa**.

## O que NÃO se aplica

- **allocator global, bump, slab, `#[no_std]`**: quem aloca é o CPython.
  Um "allocator" em Python puro seria uma camada *sobre* o alocador real
  — mais lenta, e chamada de allocator por engano.
- **contadores de hardware, cache miss, branch miss**: o CPython não os
  expõe, e a conta num interpretador de árvore diria pouco.
- **mark-and-sweep, GC concorrente ou paralelo**: o coletor é o do
  CPython, e trocá-lo não é decisão desta linguagem.
- **PGO e LTO**: a parte 8 já mediu que compilar mais nós rende **1,01×**
  em código real. Um PGO otimizaria a constante errada.
