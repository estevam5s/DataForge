# Exercicio 124 — Análise estática

## Enunciado

Entenda o que `dataforge check` encontra **antes** de executar, e o que só
aparece em tempo de execução.

## Conceitos

`dataforge check` roda três etapas sem executar uma linha do seu programa:

1. **Léxica** — o arquivo é um DataForge válido?
2. **Sintática** — a estrutura faz sentido?
3. **Semântica** — os nomes existem? as chamadas batem? os tipos combinam?

```bash
dataforge check meu_programa.df
dataforge check src/ --strict     # avisos também falham
```

## O que ele encontra

| Categoria | Exemplo |
|-----------|---------|
| nome indefinido | `sommar(1, 2)` → *sugere `somar`* |
| aridade | `somar(1)` → falta `b` |
| tipo de argumento | `somar("x", 2)` |
| tipo de variável | `x: Integer := "texto"` |
| tipo inexistente | `x: Intger := 1` → *sugere `Integer`* |
| constante reatribuída | `LIMITE := 200` |
| operador incompatível | `1 + [2]` |
| campo de record | `p.emial` |
| membro de enum | `Status.Cancelado` |
| código inalcançável | linha após `yield` |
| retorno ausente | `-> Integer` sem `yield` |

## O que ele NÃO encontra

O analisador é **deliberadamente otimista**: quando não consegue provar que algo
está errado, fica calado. Um falso alarme atrapalha mais do que um alerta
perdido, porque ensina a ignorar as mensagens.

Por isso, isto passa no `check` e falha ao rodar:

```dataforge
divisor := 0
out 10 / divisor      // o valor só é conhecido em tempo de execução
```

## Erros dentro de `monitor`

Código dentro de um `monitor:` existe justamente para conter falhas. Por isso o
analisador **rebaixa erros a avisos** ali dentro — provocar uma falha de
propósito é legítimo.

## Experimente

1. Descomente uma das linhas listadas no arquivo.
2. Rode `dataforge check 124_checagem_estatica.df`.
3. Repare que a mensagem traz linha, coluna e uma sugestão.
