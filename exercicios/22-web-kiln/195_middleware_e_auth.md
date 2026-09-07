# Exercicio 195 — Middleware, autenticação e limite de taxa

## Enunciado

Proteja rotas com autenticação e limite os pedidos por IP.

## Conceitos

Middleware roda **antes** de toda rota do servidor:

```dataforge
server privado on 8080:
    middleware Kiln.rate_limit(3, 60)
    middleware Kiln.auth(conferir)
```

A regra é uma só: **se o middleware devolve uma resposta, a cadeia para ali.**
Se devolve `void`, o pedido segue, e o que ele guardou em `req["state"]` chega
na rota.

| Pronto | Faz |
|--------|-----|
| `Kiln.cors(origens)` | responde o preflight e libera origens |
| `Kiln.logger()` | uma linha por pedido no terminal |
| `Kiln.rate_limit(max, janela)` | 429 + `Retry-After` ao estourar |
| `Kiln.auth(verificador)` | 401 sem credencial; põe o usuário em `state` |
| `Kiln.guard(condicao, status)` | middleware a partir de qualquer condição |

## O que observar

**A ordem importa, e não é detalhe.** No exercício, `rate_limit` vem antes de
`auth`. Se fosse o contrário, um pedido barrado pelo `auth` nunca seria
contado — e quem está martelando a porta com credenciais inválidas é justamente
quem você quer limitar.

**Autenticação é uma função sua.** `Kiln.auth` cuida do protocolo (ler o
cabeçalho, devolver 401 com `WWW-Authenticate`); quem decide se o token vale é
a ação que você passa. O Kiln não escolhe seu banco nem seu formato de token.

**O 429 diz quando voltar.** `Retry-After` no cabeçalho é a diferença entre um
cliente que espera e um que fica tentando.

## Erros comuns

- Pôr autenticação antes do limite de taxa.
- Middleware que devolve algo sem querer. Só devolva quando for para **cortar**
  o pedido.
- Confiar no `rate_limit` em produção com vários processos: a contagem é por
  processo, em memória.
