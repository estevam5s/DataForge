# 215 — A estrutura certa

## A tabela que decide

| Você faz | Use | Custo |
|---|---|---|
| procurar por posição | `Cluster` | O(1) |
| procurar por chave | `Vault` | O(1) |
| procurar por **valor** | `Cluster` | **O(n)** |

A terceira linha é onde se perde. `999999 in lista` percorre a lista
inteira; `mapa.has("999999")` calcula um hash e vai direto.

Escolher a estrutura costuma render mais que otimizar o algoritmo: um
`O(n)` dentro de um laço `O(n)` dá `O(n²)`, e nenhuma micro-otimização
salva isso.

## Por que 100 mil, e não 3 mil

Este exercício media com `n = 3000`, e a razão entre as duas buscas
ficava em **~2x** — com uma volta em cinco dando 1,3x. O `assert` virava
sorteio, e reprovou a CI num macOS carregado.

A causa não era a medição. O `in` de um cluster é um **laço em C**,
rápido o bastante para o custo de despacho do interpretador dominar os
dois lados e mascarar a diferença assintótica:

| n | cluster | vault | razão |
|---|---|---|---|
| 3.000 | 0,015 ms | 0,006 ms | 2,7x |
| 20.000 | 0,057 ms | 0,006 ms | 9,2x |
| 100.000 | 0,259 ms | 0,006 ms | **43x** |
| 300.000 | 0,815 ms | 0,006 ms | 127x |

Note a coluna do vault: **constante**. É isso que O(1) significa, e é
por isso que a vantagem cresce com n — não porque o vault fique mais
rápido, mas porque o cluster fica mais lento.

Só a partir de 100 mil a conta que este exercício ensina fica visível
acima do ruído.

## A margem, e por que ela importa

```dataforge
razao := por_valor["media_ms"] / por_chave["media_ms"]
assert razao bigger 5,
"o vault ganha por uma ordem de grandeza, e a vantagem cresce com n"
```

Não `assert a_ms bigger b_ms`. Comparar dois tempos medidos sem margem
passa **por acidente** quando a medição está quebrada, e falha por
acidente quando a máquina está carregada. Um teste que falha por máquina
lenta ensina a ignorar a suíte, que é o pior que pode acontecer com ela.

`5x` é o intervalo honesto: o valor medido é ~43x, então a afirmação é
verdadeira com folga; e se algum dia a busca no vault virar O(n) por
acidente, 5x reprova alto.

Há um teste no repositório (`test_nenhum_exercicio_compara_dois_tempos_sem_margem`)
que proíbe o padrão sem margem voltar.

## Medir uma vez é o erro mais comum

```dataforge
por_valor := Crucible.timed(lambda => -1 in lista, 50)
```

O segundo argumento é o número de repetições. Uma busca sozinha leva
microssegundos, e o custo de **medir** dominaria o resultado — o que se
mede então é o relógio, não o código.

E procure por algo que **não existe** (`-1`, `"nao-existe"`): procurar
um valor que está no meio mede meia lista, e o número depende de onde
ele caiu.
