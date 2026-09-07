# Exercicio 156 — Projeto: biblioteca completa

## Enunciado

Escreva um módulo publicável: interface pública clara, implementação escondida,
testes e documentação.

## A anatomia de uma biblioteca

Quatro partes, nesta ordem:

1. **Cabeçalho** — o que é e o que expõe
2. **Tipos** — os dados que atravessam a interface
3. **Implementação** — o interno (`_`) e o público
4. **`relay`** — a fronteira

```dataforge
relay Resultado, validar_cpf, formatar_cpf, validar_email, validar_telefone
```

Tudo que não está nessa linha — `_so_digitos`, `_digito_cpf` — é detalhe de
implementação. Você pode reescrevê-los amanhã sem quebrar ninguém.

## Devolver o motivo, não só `no`

Esta é a decisão de desenho mais importante do exercício:

```dataforge
record Resultado:
    valido: Boolean
    motivo: String := ""
```

Compare as duas interfaces:

```dataforge
validar_cpf("123")           // no
validar_cpf("123")           // Resultado(no, "esperava 11 digitos, veio 3")
```

A primeira obriga quem chama a adivinhar o que está errado. A segunda pode ser
mostrada ao usuário direto. O custo é um record; o ganho é toda a mensagem de
erro que você não precisa escrever de novo em cada tela.

O campo `motivo` tem valor padrão `""`, então o caso de sucesso continua sendo
`Resultado(yes)`.

## Validar antes de formatar

```dataforge
action formatar_cpf(cpf: String) -> String:
    limpo := _so_digitos(cpf)
    guard len(limpo) is 11, "CPF precisa de 11 digitos"
    yield $"{limpo.slice(0, 3)}.{...}"
```

O `guard` na entrada garante que a formatação nunca produz lixo. Uma função que
formata dado inválido espalha o problema em vez de contê-lo.

## Testes que cobrem os dois lados

```dataforge
action test_cpf_valido():        // o que deve passar
action test_cpf_invalido():      // o que deve falhar
action test_cpf_explica_o_motivo():   // e por quê
```

O terceiro é o que muita suíte esquece: testar a **mensagem**. Sem ele, uma
mudança que faz o validador rejeitar pelo motivo errado passa despercebida.

## Publicando

```bash
dataforge check validadores.df     # nomes e tipos
dataforge lint validadores.df      # estilo
dataforge test tests/              # suíte
dataforge doc validadores.df --out=doc/API.md
```

O `doc` extrai os comentários acima de cada declaração — por isso vale escrevê-los
como frases completas.

## Saída esperada

```
┌────────────────┐
│ Validadores BR │
└────────────────┘

── CPF ──
  ok  529.982.247-25   529.982.247-25
  ok  52998224725      529.982.247-25
  nao 111.111.111-11   todos os digitos iguais
  nao 123              esperava 11 digitos, veio 3
  nao 529.982.247-26   primeiro digito verificador nao confere
...
6/6 testes passaram
```

## Experimente

- Acrescente `validar_cnpj` seguindo o mesmo desenho.
- Separe em `validadores.df` e `tests/validadores_test.df` de verdade.
- Rode `dataforge doc` e veja a documentação que os comentários geraram.
