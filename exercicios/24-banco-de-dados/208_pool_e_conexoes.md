# Exercício 208 — Pool de conexões

## Enunciado

Reaproveite conexões, e garanta que elas voltem.

## Conceitos

Abrir conexão custa: TCP, autenticação, negociação. Numa rota web isso acontece
por requisição e passa a dominar o tempo de resposta.

```dataforge
pool := Forge.pool("postgres://localhost/app", 5)

with Forge.conexao(pool) as db:
    Forge.de(db, "usuarios").contar()
```

## O que observar

**`with` devolve a conexão sozinho** — inclusive quando o corpo falha, que é
onde mais importa. Uma conexão pegada e não devolvida some do pool para sempre.

**O pool não é só cache — é limite.** Sem teto, um pico de tráfego abre mil
conexões e o servidor recusa **todas**, inclusive as de quem já estava
funcionando. Melhor a milésima requisição esperar do que as mil falharem.

**O `with` roda no escopo de fora**, como o `monitor`: o que o corpo calcula
continua visível depois. Só o nome do recurso é local — ele deixa de valer
quando o recurso fecha.

## Armadilhas

- Uma conexão devolvida no meio de uma transação contaminaria a próxima. O pool
  desfaz antes de devolver.
- O tamanho do pool tem um teto natural: o `max_connections` do servidor. Cinco
  processos com pool de 20 pedem 100 conexões.

## Relacionados

- [204 — Transações](204_transacoes.md)
