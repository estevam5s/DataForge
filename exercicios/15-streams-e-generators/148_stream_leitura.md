# Exercicio 148 — Processamento incremental

## Enunciado

Use streams para tratar um volume grande de dados sem carregar tudo na memória.

## O problema

Um arquivo de log com um milhão de linhas. Você quer os erros. A forma ansiosa:

```dataforge
linhas := IO.read("app.log").lines()      // 1 milhão de strings na memória
registros := linhas >> morph interpretar   // mais 1 milhão de vaults
erros := registros >> sift e: e["nivel"] is "ERROR"
```

Três cópias completas dos dados, e você talvez só queira ver o primeiro erro.

## A forma incremental

Cada estágio é um `stream action` que consome o anterior:

```dataforge
stream action interpretar(fonte):
    cycle linha in fonte:
        emit {...}

stream action apenas(fonte, nivel):
    cycle registro in fonte:
        given registro["nivel"] is nivel:
            emit registro

erros := apenas(interpretar(linhas_do_log()), "ERROR")
```

Montar a cadeia **não lê nada**. Uma linha entra, atravessa os três estágios,
sai — e só então a próxima começa. A memória usada é a de uma linha, não a de um
milhão.

## O ganho fica óbvio em `first()`

```dataforge
primeiro_erro := apenas(interpretar(linhas_do_log()), "ERROR").first()
```

Isso lê até o primeiro erro e **para**. Se ele estiver na linha 3, as outras
999.997 nunca são tocadas.

## O padrão de três estágios

Vale para praticamente todo processamento de dados:

1. **Origem** — produz os itens brutos (`linhas_do_log`)
2. **Transformação** — dá estrutura a cada item (`interpretar`)
3. **Filtro** — descarta o que não interessa (`apenas`)

Separados assim, cada estágio é testável e reutilizável isoladamente.

## Contando sem materializar

```dataforge
contagem := {}
cycle registro in interpretar(linhas_do_log()):
    nivel := registro["nivel"]
    contagem[nivel] := contagem.get(nivel, 0) + 1
```

O acumulador cresce com o número de **níveis distintos** (3), não com o número de
linhas. Essa é a diferença entre um agregado e uma cópia.

## Saída esperada

```
── erros encontrados ──
  2026-01-10: falha ao conectar
  2026-01-11: timeout no banco

{INFO: 3, WARN: 1, ERROR: 2}

primeiro erro: falha ao conectar
```

## Experimente

- Troque `linhas_do_log` por `IO.read("arquivo.log").lines()` e mantenha o resto.
- Acrescente um estágio que só passa registros de uma data.
- Escreva `ultimo(stream)` — por que ele precisa consumir tudo?
