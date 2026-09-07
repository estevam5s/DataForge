# Exercicio 184 — Visibilidade: private e protected

## Enunciado

Proteja o estado interno de um objeto, deixando público apenas o que você
pretende manter.

## Conceitos

```dataforge
blueprint Conta:
    private saldo: Float := 0.0      // só dentro de Conta
    protected titular: String := ""  // Conta e seus herdeiros
    numero: String := ""             // público
```

O que fica público é **a promessa que você mantém**. O resto você pode mudar sem
avisar ninguém — e é essa liberdade que a visibilidade compra.

| Linguagem | Equivalente |
|-----------|-------------|
| Python | `_nome` por convenção (não impede nada) |
| TypeScript | `private` / `protected` |
| Java | `private` / `protected` |
| Rust | privado por padrão, `pub` para expor |

## O que observar

**Em DataForge, `private` impede de verdade.** Não é convenção: o acesso de fora
é recusado em tempo de execução, com mensagem que diz de onde partiu:

```
erro[DF0301]: 'Conta.saldo' is private and was accessed outside any blueprint.
              Only 'Conta' can read it.
```

**`protected` alcança o herdeiro**, `private` não. Um campo que o filho precisa
ler é `protected`; um que só o pai usa é `private`.

**A verificação vale para leitura e escrita.** Não dá para forjar o saldo de
fora.

## Armadilhas

- `private` de um pai **não** vaza para o filho. Se o filho precisa, é
  `protected`.
- Tornar tudo privado e criar um `get`/`set` para cada campo devolve o problema
  ao ponto de partida. Exponha comportamento (`depositar`), não estado (`saldo`).

## Relacionados

- [183 — Propriedades](183_propriedades.md)
- [187 — Herança e root](187_heranca_e_root.md)
