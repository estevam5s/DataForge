# Exercicio 198 — A API vista de fora

## Enunciado

Exporte as rotas de um servidor Kiln para as ferramentas que quem
consome a API de fato usa: OpenAPI, Insomnia, Postman e `curl`.

## Conceitos

```dataforge
adopt Arcane.API as API

out API.openapi(servidor, {"titulo": "Minha API"})
out API.insomnia(servidor)
out API.curl(servidor)
```

E na linha de comando, que é como se usa na prática:

```bash
dataforge api src/app.df --openapi  -o=openapi.json
dataforge api src/app.df --insomnia -o=insomnia.json
dataforge api src/app.df --curl
```

## Por que não escrever a documentação à mão

Ela resolve por uma semana. Depois alguém acrescenta uma rota e esquece
de atualizar, e a documentação passa a mentir — o que é **pior que não
ter**, porque quem a lê não tem como saber.

Aqui ela é derivada das rotas registradas. O servidor é a fonte da
verdade, e isto é uma projeção dele: acrescentar uma rota e reexportar
são a mesma ação.

## Aponte para o `app.df`, não para o `main.df`

O arquivo é **executado** para que as rotas se registrem — é assim que
um servidor Kiln se declara. O `main.df` chama `ignite` e nunca
voltaria.

É a mesma separação que `projetos/loja-web` já usava para poder testar
rotas sem abrir socket. Agora ela tem uma segunda razão de existir.

## As traduções que importam

| No Kiln | No formato | Por quê |
|---|---|---|
| `/produtos/:id` | OpenAPI: `/produtos/{id}` | o Swagger trataria `:id` como parte literal, e o cliente gerado bateria numa URL que não existe |
| `/produtos/:id` | Insomnia: `{{ id }}` | `{{ }}` é o que o Insomnia reconhece como variável |
| a porta do `server` | ambiente `base` | trocar de máquina passa a ser editar um campo |
| `POST`/`PUT`/`PATCH` | corpo JSON vazio | pronto para preencher; `GET` não ganha corpo |

## O que ele **não** infere

O Kiln não declara tipos de corpo nem de resposta: `respond json {…}`
monta o vault na hora. Então o **esquema** de entrada e saída não
aparece — só a rota, o método e os parâmetros de caminho.

Inventar um esquema a partir de um exemplo daria uma documentação com
*aparência* de completa e conteúdo adivinhado. Isso é especialmente
perigoso aqui: alguém vai gerar um cliente a partir desse arquivo.

Uma documentação menor e verdadeira é mais útil que uma grande e
inventada.

## Saída esperada

```
rotas: 5
metodos: {GET: 2, POST: 1, PATCH: 1, DELETE: 1}
com parametro: 3

openapi: 3.1.0
titulo:  API da Loja
caminhos: [/produtos, /produtos/{id}]
parametro: id em path

requisicoes: 5
primeira: GET {{ base }}/produtos

# Lista produtos
curl https://api.loja.com/produtos

ok
```

## Experimente

- Acrescente uma rota `PUT` e reexporte: repare que não há um segundo
  lugar para atualizar.
- Importe o `insomnia.json` no Insomnia e dispare as cinco requisições.
- Rode `dataforge api` num dos projetos de `projetos/` e compare o que
  sai com o que o código faz.
- Gere o OpenAPI e cole em `editor.swagger.io`.
