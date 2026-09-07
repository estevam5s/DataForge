# Exercicio 193 — Uma API RESTful completa

## Enunciado

Implemente os cinco verbos sobre um mesmo recurso, cada situação com o status
certo.

## Conceitos

REST não é só usar `POST` e `GET`. Cada situação tem seu status, e usar o certo
é o que faz a API ser previsível para quem a consome:

| Situação | Status | Quem decide |
|----------|--------|-------------|
| leitura com sucesso | 200 | você |
| criado | **201** | você |
| apagado, sem corpo | **204** | você |
| recurso inexistente | 404 | o Kiln, se a rota não casar |
| caminho existe, verbo não | **405** + `Allow` | o Kiln |

```dataforge
route POST "/itens":
    novo := {"id": len(itens) + 1, "nome": body["nome"]}
    itens.append(novo)
    respond 201 json novo

route DELETE "/itens/:id":
    respond 204
```

`respond 204` sozinho é válido: status sem corpo.

## O que observar

**404 e 405 são coisas diferentes.** Se o caminho `/itens/1` existe mas só
aceita `GET`, `PUT` e `DELETE`, um `PATCH` recebe **405** com
`Allow: DELETE, GET, PUT`. Devolver 404 ali mandaria o cliente procurar um bug
que não existe.

**O corpo chega interpretado.** Com `Content-Type: application/json`, `body` já
é um vault. JSON quebrado **não** vira erro 500: chega como texto, e a rota
decide se responde 400 — porque JSON inválido é problema do cliente, não falha
do servidor.

**Um erro na rota não derruba o servidor.** Vira 500, o detalhe sai no terminal,
e o próximo pedido é atendido normalmente.

## Erros comuns

- Devolver 200 em tudo. O cliente não tem como distinguir "criei" de "já
  existia".
- Devolver corpo no 204. Por definição, 204 é "sem conteúdo".
- Confiar em `body` sem conferir. Se o cliente mandou texto onde você esperava
  um vault, `body["nome"]` falha — e vira 500.
