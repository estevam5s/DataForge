# Exercicio 175 — Projeto: ferramenta de linha de comando

## Enunciado

Escreva um utilitário que analisa uma pasta e imprime um relatório — o tipo de
ferramenta que se usa todo dia.

## O que ele faz

1. Lê cada arquivo da pasta
2. Extrai nome, extensão, tamanho e contagem de linhas
3. Agrupa por extensão com um histograma
4. Encontra o maior e o menor
5. Busca um termo em todos os arquivos

## Modelo primeiro

```dataforge
record Arquivo:
    nome: String
    extensao: String
    bytes: Integer
    linhas: Integer
```

Converter os dados brutos num record logo na entrada faz o resto do programa
trabalhar com `a.bytes` em vez de chamar `IO.size` repetidamente. Uma leitura, um
tipo, muitos usos.

## Formatação legível

```dataforge
action formatar_bytes(n: Number) -> String:
    given n smaller 1024:
        yield $"{n} B"
    orif n smaller 1048576:
        yield $"{round(n / 1024, 1)} KB"
    yield $"{round(n / 1048576, 2)} MB"
```

"1.4 KB" comunica; "1433" não. Numa ferramenta de terminal, esse detalhe é a
diferença entre útil e irritante.

## Colunas alinhadas

```dataforge
out $"  {a.nome.pad_end(14)}{a.extensao.pad_end(8)}{formatar_bytes(a.bytes).pad_start(10)}"
```

`pad_end` para texto (alinha à esquerda), `pad_start` para número (alinha à
direita). É como toda tabela de terminal se lê melhor.

## Histograma proporcional

```dataforge
barra := "#".repeat(max(1, soma * 20 ~/ max(total_bytes, 1)))
```

Dois `max` protegem contra os casos de borda: barra de comprimento zero, e
divisão por zero se a pasta estiver vazia. Vale escrever mesmo quando "não vai
acontecer" — é uma linha, e evita um crash na única vez em que acontece.

## Busca com número de linha

```dataforge
numero := 0
cycle l in conteudo.lines():
    numero += 1
    given "linha" in l.lower():
        achados.append($"{nome}:{numero}: {l.trim()}")
```

O formato `arquivo:linha: texto` é o do `grep` — e o que editores reconhecem para
saltar direto ao ponto.

## Limpeza

A ferramenta apaga o que criou. Num programa real, isso iria num `defer` logo
após o `mkdir`.

## Saída esperada

```
┌─────────────────────┐
│ Analise de Arquivos │
└─────────────────────┘

  ARQUIVO       EXT        TAMANHO  LINHAS
  ----------------------------------------
  dados.csv     .csv         26 B       5
  script.df     .df          34 B       3
  ...

  total: 5 arquivos, 145 B, 15 linhas

  ── por extensao ──
  .csv       1  ### 26 B
  ...

  ── procurando por 'linha' ──
    notas.txt:1: linha 1
    notas.txt:2: linha 2
    notas.txt:3: linha 3
```

## Experimente

- Aceite o caminho e o termo de busca como argumentos.
- Percorra subpastas recursivamente.
- Acrescente `--json` para saída legível por máquina.
