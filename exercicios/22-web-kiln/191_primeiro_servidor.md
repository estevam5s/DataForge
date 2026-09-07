# Exercicio 191 — O primeiro servidor

## Enunciado

Declare um servidor com duas rotas: uma devolvendo HTML, outra devolvendo texto.

## Conceitos

O **Kiln** é o framework web do DataForge. O nome vem do forno onde a peça ganha
a forma final: a requisição entra crua e sai como resposta.

Três palavras novas, todas contextuais — fora de um bloco `server` elas
continuam sendo nomes livres:

```dataforge
server ola on 8080:
    route GET "/":
        respond html "<h1>Ola do Kiln</h1>"
```

| Palavra | Faz |
|---------|-----|
| `server nome on porta:` | declara a aplicação e liga ao nome |
| `route VERBO "caminho":` | registra uma rota |
| `respond [status] [tipo] valor` | envia a resposta e **encerra a rota** |
| `ignite nome` | acende o forno: sobe o servidor e bloqueia |

| Framework | Equivalente |
|-----------|-------------|
| Flask | `@app.route("/")` + `return` |
| Express | `app.get("/", (req, res) => res.send(...))` |
| FastAPI | `@app.get("/")` |
| Fastify | `fastify.get("/", handler)` |

## O que observar

**`server` não sobe nada.** Ele monta a aplicação e liga ao nome. Quem acende o
forno é `ignite` — ou `Kiln.serve`, que sobe em segundo plano. Essa separação é
o que permite testar uma rota sem abrir socket nenhum:

```dataforge
Kiln.test(ola, "GET", "/")   // executa a rota, sem rede
```

Testar uma rota fica tão barato quanto testar uma função — que é o que faz
alguém realmente escrever esses testes.

**`respond` encerra a rota**, exatamente como `yield` encerra uma ação. O que
vier depois não roda.

**O 404 é de graça.** Um caminho não registrado responde 404 sem você escrever
nada. E se o caminho existe mas o verbo não, a resposta é **405** com o
cabeçalho `Allow` — distinguir os dois poupa depuração.

## Erros comuns

- Escrever `route` fora de um bloco `server`. Fora dali, `route` é só um nome
  de variável — o parser não vai reconhecer a rota.
- Esquecer o `ignite`. O programa monta o servidor, não sobe nada e termina.
- Usar `yield` no corpo de uma rota. Funciona, mas `respond` já monta a
  resposta com o status e o tipo certos.
