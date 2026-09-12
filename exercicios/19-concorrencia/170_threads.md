# Exercicio 170 — Threads e paralelismo

## Enunciado

Execute trabalho em segundo plano — e conheça o problema que isso cria.

## `thread`

```dataforge
thread:
    cycle i from 1 to 3:
        resultados.append($"A{i}")
```

O bloco roda numa thread daemon: o programa **não espera** por ela. Se o programa
principal terminar antes, a thread é interrompida no meio.

Por isso o `wait 200` — sem ele, o programa acabaria antes das threads
produzirem qualquer coisa.

## `parallel`

```dataforge
parallel:
    saidas.append(tarefa_a())
    saidas.append(tarefa_b())
    saidas.append(tarefa_c())
```

**Cada instrução** do bloco vai para uma thread, e há um join de 30 segundos no
fim.

Note a semântica: é uma thread por *instrução*, não uma thread para o bloco
inteiro. Isso é uma limitação conhecida — o roadmap prevê mudar para blocos.
Enquanto isso, mantenha cada linha do `parallel` autossuficiente.

## A condição de corrida

O último trecho do exercício é o mais importante:

```dataforge
contador := {"valor": 0}

thread:
    cycle _ in range(0, 1000):
        contador["valor"] := contador["valor"] + 1

thread:
    cycle _ in range(0, 1000):
        contador["valor"] := contador["valor"] + 1
```

O resultado **deveria** ser 2000. Frequentemente é menos.

O motivo: `contador["valor"] + 1` são três passos — ler, somar, escrever. Se as
duas threads leem 5 ao mesmo tempo, ambas escrevem 6. Um incremento se perdeu.

Rode várias vezes: o número muda. Esse é o tipo de bug que passa em teste e
quebra em produção sob carga.

### O `check` avisa

```
aviso: 'contador' e escrito dentro de 'thread' e vem de fora:
       duas threads podem perder atualizacoes
   sugestao: a linguagem nao sincroniza sozinha — use
             'Arcane.Concurrent': 'contador()' para somar,
             'mutex()' para um bloco, ou 'canal()' para passar
             o valor adiante
```

Aqui a corrida é o assunto, então o exercício usa
`// df: permitir escrita-concorrente` nas duas linhas. Num código de
verdade, o aviso é para ser atendido.

### E a saída, no mesmo arquivo

```dataforge
adopt Arcane.Concurrent as Conc

atomico := Conc.contador()

thread:
    cycle _ in range(0, 1000):
        atomico.somar(1)

thread:
    cycle _ in range(0, 1000):
        atomico.somar(1)

assert atomico.valor() is 2000      // sempre
```

O incremento acontece dentro de uma trava. Não há o que torcer.

### Por que o número não é impresso

A primeira versão deste exercício imprimia `contador["valor"]`, e **isso
reprovou a CI**: `test_a_compilacao_nao_muda_o_resultado_de_nenhum_exercicio`
roda cada arquivo duas vezes e exige saída idêntica. Deu 2000 numa
execução e 1847 na outra — a corrida acontecendo, que é o ponto.

Imprimir a instabilidade era a forma errada de ensiná-la. A forma certa
é afirmar o que se **sabe**:

```dataforge
assert valor smaller_eq 2000, "nunca passa: so se perde, nao se inventa"
assert valor bigger 0, "algo foi contado"
```

Duas threads só podem **perder** incrementos, nunca inventar — então o
limite superior é garantido. O texto diz qual dos dois casos aconteceu
nesta execução, sem imprimir o número.

## Como evitar

**DataForge 4.0 não tem mutex nem lock.** A ferramenta segura é `channel`:

```dataforge
channel resultados
thread:
    resultados.send(calcular())
```

Cada thread envia o que produziu; a thread principal recebe e agrega. Ninguém
escreve na mesma variável.

O próximo exercício mostra esse padrão.

## Regra prática

| Situação | Seguro? |
|----------|---------|
| threads só leem dados compartilhados | sim |
| cada thread escreve numa variável própria | sim |
| threads enviam por `channel` | sim |
| duas threads escrevem na mesma variável | **não** |
| `lista.append` de duas threads | **não** |

## Saída esperada

```
itens produzidos: 6

  fatorial: 479001600
  fibonacci: 75025
  primo: yes

sequencial: 24.3 ms

o contador fechou em 2000 NESTA execucao — e sorte, nao
garantia. Na proxima, ou em outra maquina, pode nao fechar.

com Conc.contador(): 2000 — e sempre 2000
```

## Experimente

- Rode cinco vezes e veja a mensagem mudar entre "fechou" e "veio menor"
  — na sua máquina, num dos dois, mais cedo ou mais tarde.
- Ponha carga na máquina (`yes > /dev/null &` algumas vezes) e rode de
  novo: a corrida aparece mais.
- Troque o `Conc.contador()` pelo vault e veja o `assert` do fim falhar.
