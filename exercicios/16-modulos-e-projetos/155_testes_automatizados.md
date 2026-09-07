# Exercicio 155 — Testes automatizados

## Enunciado

Escreva testes que o `dataforge test` descobre e executa sozinho.

## Descoberta automática

O runner encontra testes por convenção:

| Padrão | Exemplo |
|--------|---------|
| `*_test.df` | `matematica_test.df` |
| `test_*.df` | `test_matematica.df` |
| qualquer `.df` em `tests/` | `tests/regras.df` |

Dentro do arquivo, **toda ação `test_*` é um caso**:

```dataforge
action test_fatorial_casos_base():
    assert fatorial(0) is 1, "fatorial de 0"
```

```bash
dataforge test              # tudo
dataforge test tests/ -v    # mostra cada caso
dataforge test --filter=primo
dataforge test --fail-fast
```

## Ganchos opcionais

| Ação | Roda |
|------|------|
| `setup_all` | uma vez, antes de tudo |
| `setup` | antes de cada caso |
| `teardown` | depois de cada caso |
| `teardown_all` | uma vez, no fim |

## Anatomia de um bom teste

**Nome que descreve o comportamento**, não a implementação:

```dataforge
action test_saque_acima_do_saldo():        // bom
action test_sacar_2():                     // ruim
```

**Mensagem em cada assert.** Quando falha, é ela que você lê:

```dataforge
assert depois.saldo is 700, "saldo apos saque"
```

**Um comportamento por caso.** Se um `test_tudo` falha, você não sabe qual das
oito verificações quebrou.

## Testando erros

O erro esperado é parte do contrato, e merece teste:

```dataforge
action test_saque_acima_do_saldo():
    erro := ""
    monitor:
        sacar(Conta("Ana", 100), 500)
    handle e:
        erro := e.message
    assert erro is "saldo insuficiente", "mensagem do guard"
```

Note que o `assert` verifica a **mensagem**, não só que algo falhou. Isso pega o
caso em que a ação falha pelo motivo errado.

## Testando imutabilidade

```dataforge
action test_saque_reduz_saldo():
    c := Conta("Ana", 1000)
    depois := sacar(c, 300)
    assert depois.saldo is 700, "saldo apos saque"
    assert c.saldo is 1000, "o original nao muda"
```

O segundo `assert` é o que garante que `sacar` não tem efeito colateral. Sem ele,
uma implementação que mutasse o original passaria.

## Cobrindo faixas

```dataforge
action test_primos_conhecidos():
    cycle n in [2, 3, 5, 7, 11, 13]:
        assert eh_primo(n) is yes, $"{n} e primo"
```

Um laço dentro do teste cobre vários valores. A mensagem interpolada diz **qual**
falhou.

## Saída esperada

```
  ok    fatorial_casos_base
  ok    fatorial_cresce
  ok    fatorial_recusa_negativo
  ok    primos_conhecidos
  ok    nao_primos
  ok    saque_reduz_saldo
  ok    saque_acima_do_saldo

7 passaram, 0 falharam
```

## Experimente

- Copie os casos para `tests/matematica_test.df` e rode `dataforge test`.
- Quebre `eh_primo` de propósito e veja o relatório com a linha da falha.
- Acrescente `setup` que prepara uma conta reaproveitada pelos casos.
