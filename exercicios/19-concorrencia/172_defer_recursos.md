# Exercicio 172 — Liberação garantida

## Enunciado

Garanta que a limpeza aconteça, inclusive quando algo falha no meio.

## O problema

```dataforge
action processar():
    arquivo := abrir("dados.txt")
    // ... se algo aqui disparar, o arquivo nunca fecha
    fechar(arquivo)
```

Todo caminho de saída precisaria repetir o `fechar` — e é sempre o caminho de
erro que alguém esquece.

## `defer`

```dataforge
action com_recurso():
    abrir()
    defer:
        fechar()
    // ... o defer roda aconteça o que acontecer
```

O bloco `defer` roda ao sair da ação, em **todos** os caminhos:

| Saída | `defer` roda? |
|-------|---------------|
| chegou ao fim | sim |
| `yield` no meio | sim |
| `trigger` / erro | sim |
| erro vindo de uma ação chamada | sim |

> Este comportamento no caminho de erro foi corrigido no 4.0 — antes, o `defer`
> só rodava no sucesso, deixando arquivos temporários para trás.

## Declare junto de quem adquire

```dataforge
IO.write(caminho, "dados")
defer:
    IO.delete(caminho)
```

O `defer` fica **imediatamente após** a aquisição. Assim, ler o código é ver o
par completo — não há como esquecer a limpeza porque ela está uma linha abaixo.

## LIFO: o último declarado roda primeiro

```dataforge
defer:
    fechar_arquivo()      // roda por último
defer:
    fechar_conexao()      // roda primeiro
```

A ordem inversa é a correta para recursos que dependem uns dos outros: você
desmonta na ordem oposta à que montou.

## Em cadeia

```dataforge
action interna():
    defer:
        trilha.append("interna limpou")
    trigger "falha"

action externa():
    defer:
        trilha.append("externa limpou")
    interna()
```

O erro sobe pela pilha, e cada `defer` roda no caminho — **de dentro para fora**.
Cada ação limpa o que ela própria adquiriu, sem precisar saber do resto.

## `defer` ou `ensure`?

| | `defer` | `ensure` |
|---|---------|----------|
| Escopo | a ação inteira | um bloco `monitor` |
| Declaração | junto da aquisição | no fim do bloco |
| Vários | sim, em LIFO | um por `monitor` |

Use `defer` para recursos; `ensure` quando a limpeza pertence a um trecho
específico que você já estava envolvendo em `monitor`.

## Saída esperada

```
concluido
[abriu, usou, fechou]

[abriu, fechou, tratou: falhou no meio]

[terceiro declarado, segundo declarado, primeiro declarado]

DADOS DE TRABALHO
erro: erro durante o processamento
o arquivo temporario nao sobreviveu a nenhum dos caminhos

[interna limpou, externa limpou, topo tratou]
```

## Experimente

- Combine `defer` com `DB.close` numa ação que abre banco.
- Escreva `com_arquivo(caminho, acao)` que abre, chama e fecha com `defer`.
