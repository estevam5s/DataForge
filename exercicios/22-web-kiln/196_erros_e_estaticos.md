# Exercicio 196 — Páginas de erro, redirecionamento e arquivos estáticos

## Enunciado

Personalize o 404, redirecione uma rota antiga e sirva CSS do disco.

## Conceitos

```dataforge
server site on 8080:
    assets "/static" from "./www"

    route GET "/antigo":
        redirect "/"

Kiln.on_error(site, 404, minha_pagina_404)
```

| Palavra | Faz |
|---------|-----|
| `assets "/prefixo" from "pasta"` | serve arquivos do disco |
| `redirect "/destino"` | 302 com `Location` (use `status 301` para permanente) |
| `Kiln.on_error(app, status, handler)` | troca a resposta de um status |

## O que observar

**404 em JSON serve para uma API; um site merece uma página.** `on_error`
troca o corpo mantendo o status — o status é o que os buscadores e os clientes
leem, e ele não muda.

**`../` não escapa da pasta servida.** Um pedido a
`/static/../../../etc/passwd` recebe **403**, e a checagem acontece antes de
qualquer arquivo ser aberto. Essa é a falha clássica de servidor de arquivos,
e vale saber que ela está fechada.

**302 é temporário, 301 é permanente.** O 301 fica no cache do navegador
praticamente para sempre; use só quando o endereço mudou de verdade.

## Erros comuns

- Trocar o status junto com o corpo no `on_error`. Se você responde 200 numa
  página de erro, buscadores indexam a página de erro.
- Servir a pasta do projeto inteiro em `assets`. Sirva só o que é público —
  o `.git` e o `.env` moram no mesmo disco.
