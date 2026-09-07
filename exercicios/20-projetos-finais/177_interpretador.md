# Exercicio 177 — Projeto: mini linguagem

## Enunciado

Escreva um interpretador de expressões completo — lexer, parser e avaliador —
dentro do DataForge.

## Por que este exercício

Uma linguagem capaz de implementar outra linguagem é uma linguagem completa. Este
é o mesmo desenho do interpretador do próprio DataForge, em escala reduzida.

## As três fases

```
"2 + 3 * 4"
     ↓  tokenizar
[num:2] [sim:+] [num:3] [sim:*] [num:4]
     ↓  parsear
        (+)
       /   \
      2    (*)
          /   \
         3     4
     ↓  avaliar
        14.0
```

## Fase 1 — Lexer

Percorre o texto agrupando caracteres em tokens:

```dataforge
given c.isdigit():
    numero := ""
    persist i smaller len(fonte) and (fonte[i].isdigit() or fonte[i] is "."):
        numero += fonte[i]
        i += 1
    tokens.append(Token("numero", numero))
```

Cada tipo de token tem seu laço interno que consome enquanto o caractere
pertencer àquele token. Um caractere desconhecido dispara erro com a posição — a
informação que o usuário precisa.

## Fase 2 — Parser de descida recursiva

A gramática vira funções, uma por nível de precedência:

```
expressao := termo (('+' | '-') termo)*
termo     := fator (('*' | '/') fator)*
fator     := numero | nome | '(' expressao ')' | '-' fator
```

```dataforge
action expressao():
    no_ := termo()
    persist e_simbolo("+") or e_simbolo("-"):
        op := consumir().valor
        no_ := {"tipo": "bin", "op": op, "esq": no_, "dir": termo()}
    yield no_
```

**A precedência está na estrutura, não em tabelas.** `expressao` chama `termo`,
que chama `fator`. Como `termo` é chamado mais fundo, a multiplicação fica mais
fundo na árvore — e o avaliador, que desce recursivamente, a calcula primeiro.

O teste no fim do exercício confirma exatamente isso.

Repare também que `fator` chama `expressao` de volta ao encontrar `(`. Essa
recursão mútua é o que faz parênteses funcionarem em qualquer profundidade, sem
código especial.

## Fase 3 — Avaliador

```dataforge
action avaliar(no_, ambiente):
    match no_["tipo"]:
        point "num":
            yield no_["valor"]
        point "bin":
            e := avaliar(no_["esq"], ambiente)
            d := avaliar(no_["dir"], ambiente)
            ...
```

Um `match` sobre o tipo do nó, com recursão nos filhos. É todo o interpretador.

## Erros em cada fase

| Entrada | Fase | Mensagem |
|---------|------|----------|
| `2 @ 3` | lexer | caractere inesperado |
| `2 +` | parser | expressão incompleta |
| `(1 + 2` | parser | esperava `)` |
| `1 2` | parser | sobrou entrada |
| `z + 1` | avaliador | variável indefinida |
| `1 / 0` | avaliador | divisão por zero |

Cada fase valida o que é da sua competência. Isso é o que produz mensagens
específicas em vez de "erro de sintaxe".

## Ambiente de variáveis

```dataforge
ambiente := {"x": 10.0, "y": 4.0}
calcular("x + y", ambiente)     // 14.0
```

O ambiente é passado ao avaliador, não guardado globalmente. Essa é a base de
escopo em qualquer interpretador.

## Saída esperada

```
┌────────────────────┐
│ Mini Interpretador │
└────────────────────┘

── expressoes ──
  2 + 3                = 5.0
  2 + 3 * 4            = 14.0
  (2 + 3) * 4          = 20.0
  ...

── erros tratados ──
  2 +          -> expressao incompleta
  (1 + 2       -> esperava ')'
  1 / 0        -> divisao por zero
  z + 1        -> variavel indefinida: z
  2 @ 3        -> caractere inesperado: '@' na posicao 2

  a multiplicacao ficou mais funda na arvore — precedencia respeitada
```

## Experimente

- Acrescente `^` para potência (associando à **direita**).
- Adicione chamadas de função: `sqrt(16)`, `max(1, 2)`.
- Implemente atribuição: `x = 5` e depois `x + 1`.
- Escreva um "compilador" que gera notação polonesa reversa a partir da árvore.
