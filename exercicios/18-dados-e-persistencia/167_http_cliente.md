# Exercicio 167 — Cliente HTTP e URLs

## Enunciado

Monte URLs com parâmetros, interprete respostas e trate os erros que a rede
inevitavelmente traz.

## Codificação de URL

```dataforge
Web.encode_url("busca com espacos")     // "busca%20com%20espacos"
Web.decode_url(texto)
```

Espaços, acentos e `&` precisam ser codificados. Sem isso, um `&` no valor de um
parâmetro quebra a query string inteira — o servidor lê como início de outro
parâmetro.

## Montar a query string

```dataforge
partes := [$"{Web.encode_url(k)}={Web.encode_url(str(parametros[k]))}"
           cycle k in parametros.keys()]
yield $"{base}?{partes.join("&")}"
```

Repare: **chave e valor** são codificados, e `str()` converte números antes.
Concatenar valores crus é a origem de metade dos bugs de integração.

## Classificar respostas com `match`

```dataforge
match codigo:
    point c when c bigger_eq 200 and c smaller 300:
        yield "sucesso"
    point c when c bigger_eq 400 and c smaller 500:
        yield "erro do cliente"
```

As guardas expressam faixas diretamente. A distinção 4xx/5xx importa na prática:

- **4xx** é culpa do cliente — repetir a mesma requisição dá o mesmo erro
- **5xx** é do servidor — vale tentar de novo, com espera crescente

## Tratar a resposta em camadas

```dataforge
action processar(resposta):
    given resposta["status"] bigger_eq 400:
        yield {"ok": no, "erro": $"HTTP {resposta["status"]}"}
    dados := Serde.from_json_safe(resposta["body"])
    given dados.ok is no:
        yield {"ok": no, "erro": "resposta nao e JSON valido"}
    yield {"ok": yes, "dados": dados.value}
```

Três coisas podem dar errado, e cada uma tem seu tratamento:

1. o servidor recusou (código ≥ 400)
2. respondeu, mas o corpo não é JSON
3. deu tudo certo

Note o `from_json_safe`: um servidor que devolve HTML de erro com status 200 é
comum o bastante para valer o cuidado.

## O padrão de resultado

```dataforge
{"ok": yes, "dados": ...}
{"ok": no, "erro": "..."}
```

Sempre a mesma forma, sucesso ou falha. Quem chama testa `ok` uma vez, sem
precisar de `monitor` em volta de cada chamada.

## Chamadas de verdade

```dataforge
resposta := Web.get("https://api.exemplo.com/dados")
resposta := Web.post(url, corpo)
resposta := Web.request(metodo, url, cabecalhos, corpo)
```

Este exercício não chama a rede para poder rodar em qualquer ambiente.

## Saída esperada

```
── codificacao ──
espacos:  busca%20com%20espacos
acentos:  cafe%20%26%20pao

https://api.exemplo.com/busca?q=linguagem%20de%20programacao&pagina=2&ordem=recente

query lida: {nome: Ana Silva, idade: 30}

corpo: {"acao": "criar", "dados": {"nome": "Ana"}}

── codigos ──
  200: sucesso
  404: erro do cliente
  503: erro do servidor

{ok: yes, dados: {nome: Ana}}
{ok: no, erro: HTTP 404}
{ok: no, erro: resposta nao e JSON valido}
```

## Experimente

- Escreva `com_retentativa(url, tentativas)` usando `retry`, só para 5xx.
- Acrescente cabeçalhos de autenticação ao montador de requisição.
