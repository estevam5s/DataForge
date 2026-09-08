# Exercício 209 — A primeira suíte

## Enunciado

Escreva testes que dizem **o que** quebrou, e não só que quebrou.

## Conceitos

`assert` responde "passou?" e nada mais. Quando falha, ele diz que uma expressão
deu falso — não o que se esperava, o que veio, nem qual dos quarenta casos era.

```dataforge
crucible "Calculadora":
    setup:
        base := 10

    trial "soma dois números":
        expect somar(2, 2) is 4
```

| Palavra | Abre |
|---------|------|
| `crucible` | uma suíte; suítes aninham |
| `trial` | um caso de teste |
| `expect` | uma cobrança |
| `setup` / `teardown` | o que roda em volta de cada trial |
| `fixture` / `provide` | preparo e limpeza no mesmo lugar |
| `tagged` / `pending` / `bench` | marcar, adiar, medir |

Nenhuma delas é reservada: `setup` é o nome do construtor de blueprint, e
`expect` e `trial` são nomes bons demais para tirar de quem escreve. Elas só
valem dentro de um bloco `crucible`.

## O que observar

**`pending` não roda, e o relatório diz por quê.** É melhor que comentar o
teste: um teste comentado some do relatório e é esquecido.

**A forma curta cobre igualdade e comparação.** Quatro de cada cinco cobranças
são igualdade, e `.to_be(...)` em volta delas só acrescenta ruído.

## Armadilhas

- `expect(1 / 0)` já estourou antes de chegar ao matcher. Para testar erro, é
  `expect(lambda => 1 / 0).to_raise()`.
- Um `only` esquecido faz o CI rodar um teste e reportar verde.

## Relacionados

- [210 — Isolamento](210_isolamento.md)
- [211 — Os matchers](211_matchers.md)
