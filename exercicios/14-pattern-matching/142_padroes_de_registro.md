# Exercicio 142 — Padrões de record e vault

## Enunciado

Extraia campos direto no padrão, por posição ou por nome, e roteie requisições
com padrões de vault.

## Conceitos

### Record por posição

```dataforge
point Usuario(n, i, p):
```

Casa pelo tipo e liga os campos **na ordem em que foram declarados**.

### Record por nome

```dataforge
point Usuario(nome := n, idade := i):
```

Casa pelo tipo e liga só os campos citados, **pelo nome**. Preferível quando o
record tem muitos campos ou quando você só precisa de dois deles.

### Testar um valor específico

```dataforge
point Usuario(papel := "admin"):
```

Aqui `"admin"` é um literal, não uma captura: casa apenas quando o campo `papel`
vale exatamente isso. Um teste de tipo e um teste de valor na mesma linha.

## Padrões de vault

```dataforge
point {"metodo": "GET", "rota": r}:
    yield $"lendo {r}"
```

O casamento é **parcial**: o vault precisa ter as chaves citadas, mas pode ter
outras. Por isso `{"metodo": "GET", "rota": "/x", "extra": 1}` casa normalmente.

Essa é a escolha certa para dados que vêm de fora — um JSON de API sempre traz
campos que você não usa, e exigir correspondência exata quebraria a cada mudança
do fornecedor.

## O roteador em oito linhas

```dataforge
match req:
    point {"metodo": "GET", "rota": r}:
    point {"metodo": "POST", "rota": r, "corpo": c}:
    point {"metodo": m}:
    default:
```

Cada linha diz simultaneamente **o formato esperado** e **como extrair os
dados**. Sem pattern matching, isso seria uma escada de `given req["metodo"] is
…` com verificações de chave espalhadas.

## Saída esperada

```
acesso total
Kid e menor: acesso limitado
Ana: acesso padrao
lendo /usuarios
criando em /usuarios com 1 campos
metodo DELETE nao suportado
requisicao invalida
```

## Experimente

- Acrescente `point {"metodo": "PUT", "rota": r, "id": i}`.
- Use `...resto` no padrão de vault para capturar as chaves não citadas.
