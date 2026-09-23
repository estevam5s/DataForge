# 399 — O método que não existe

## A medida que motivou isto

Quinze erros que **falham em execução**, conferidos contra o que o
`dataforge check` pegava antes de rodar. Ele pegava oito. Dos sete
silêncios, quatro eram o mesmo caso em tipos diferentes:

```dataforge
nome := "ana"
out nome.naoExiste()      // passava limpo, e estourava em execução
```

O mesmo erro num `record` era acusado desde sempre, **com sugestão**. A
forma mais comum de erro de digitação que existe numa linguagem era a
que escapava.

## A lista vem do interpretador

As tabelas de método de texto e de cluster moram em
`dataforge/interpreter.py`, e o analisador as **lê de lá**. Uma segunda
lista divergiria no primeiro método novo — e a divergência não daria
erro: ela faria o analisador acusar um método que *funciona*, que é o
falso alarme que ensina a desligar a verificação inteira.

## Onde ele cala

| Cala sobre | Porque |
|---|---|
| um **Vault** | `v.cidade` cai na chave quando ela existe |
| um objeto de `adopt Python.x` | ali o membro é resolvido pelo Python |
| um nome começando com `_` | é combinado, não um engano |
| um tipo que ele não inferiu | a regra de sempre: sem prova, silêncio |

## A calibragem

Zero falso alarme nas cinco pastas do repositório — `examples`,
`exercicios`, `projetos`, `packages` e `trilha`, 532 arquivos. Um
analisador que acusa código que funciona é desligado no mesmo dia, e
junto com ele vão os achados de verdade.

## `length` é chamado

`nome.length` devolve a *ação*, não o número: ele está na tabela de
métodos como qualquer outro. A forma é `nome.length()`.
