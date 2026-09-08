# Exercício 213 — Medir o crescimento, não o relógio

## Enunciado

Escreva duas versões do mesmo problema e compare as ordens.

## Conceitos

Um algoritmo que funciona com dez itens pode não terminar com um milhão.
`dataforge big-o` lê a árvore e diz a classe de cada ação, sem rodar nada — e
diz **também o porquê**.

```
▲ comuns_lento    O(n^2)  tempo   O(n) espaco
    · 'in' na linha 14 percorre a colecao (use um vault para O(1))
    ⚠ O(n^2): dobrar a entrada quadruplica o tempo.
● comuns          O(n)    tempo   O(n) espaco
```

## O que observar

**A razão cresce com n.** Com n=500 o O(n) *perde* — montar o vault custa, e
esse custo não depende de n. Com n=5000 ele já ganha, e a vantagem só aumenta.

**Big-O é sobre crescimento, não sobre velocidade.** O(n) com constante grande
perde de O(n²) com constante pequena até um certo n. Achar esse ponto é trabalho
de medição; saber que ele existe é trabalho da notação.

**Medir uma vez só é ruído.** `Crucible.timed(acao, 200)` repete, porque uma
operação de microssegundos é dominada pelo custo de medir.

## Armadilhas

- Otimizar sem medir é adivinhar. Otimizar sem saber a ordem é adivinhar duas
  vezes.
- `dataforge profile` diz quanto custa **hoje**; `big-o` diz como o custo
  **cresce**. As duas coisas respondem perguntas diferentes.

## Relacionados

- [214 — Memoização](214_memoizacao.md)
- [215 — A estrutura certa](215_estrutura_certa.md)
