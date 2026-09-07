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

contador (esperado 2000): 1847
se o numero veio menor, voce acabou de ver uma condicao de corrida
```

## Experimente

- Rode o contador cinco vezes e veja o resultado variar.
- Reescreva com `channel` e confirme que dá 2000 sempre.
