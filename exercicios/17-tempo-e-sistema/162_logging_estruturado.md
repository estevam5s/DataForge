# Exercicio 162 — Registro de eventos

## Enunciado

Registre o que acontece no programa com níveis, campos estruturados e saída em
arquivo.

## Por que não usar `out`

`out` serve para falar com quem está olhando o terminal agora. Log serve para
responder perguntas depois: *o que aconteceu às 3h da manhã?*

A diferença prática está em três coisas que `out` não tem: **nível**, **campos
estruturados** e **destino configurável**.

## Os seis níveis

| Nível | Quando |
|-------|--------|
| `TRACE` | detalhe fino, normalmente desligado |
| `DEBUG` | o que ajuda a investigar |
| `INFO` | eventos normais que valem registrar |
| `WARN` | algo estranho, mas o programa segue |
| `ERROR` | uma operação falhou |
| `FATAL` | o programa não continua |

O nível do logger é um **piso**: com `WARN`, tudo abaixo é descartado sem custo.

```dataforge
registro := Log.logger("pedidos", "DEBUG")     // durante o desenvolvimento
registro := Log.logger("pedidos", "WARN")      // em produção
```

Uma linha muda a verbosidade do sistema inteiro.

## Campos estruturados

```dataforge
registro.info("pedido recebido", {"id": 1042, "cliente": "Ana"})
```

Sai como `pedido recebido id=1042 cliente=Ana`.

Compare com `out $"pedido {id} do cliente {nome}"`. A diferença aparece na hora
de procurar: com campos, `grep 'id=1042'` acha tudo daquele pedido. Com texto
interpolado, a estrutura se perdeu na formatação.

## Contexto fixo

```dataforge
servico.with_context({"servico": "checkout", "versao": "1.2"})
```

Esses campos passam a aparecer em **toda** linha daquele logger. Você escreve uma
vez o que é constante e não repete em cada chamada.

## JSON para máquina

```dataforge
maquina.as_json(yes)
```

Cada linha vira um objeto JSON completo — o formato que ferramentas de agregação
(Elasticsearch, Loki, CloudWatch) esperam. Uma linha de configuração troca o
público-alvo do log de humano para máquina.

## Guardar em memória

```dataforge
auditoria.keep(yes)
...
erros := auditoria.records() >> sift r: r["level"] is "ERROR"
```

Útil em teste: você verifica **que o log certo foi emitido**, sem ler stdout.

## Arquivo

```dataforge
arquivo.to_file("app.log", yes)     // yes = anexar
...
arquivo.close()
```

O `close` garante que o buffer foi para o disco. Em programa que roda continuamente,
combine com `defer`.

## Saída esperada

```
23:59:01 DEBUG [pedidos] iniciando o processamento
23:59:01 INFO  [pedidos] pedido recebido id=1042 cliente=Ana
23:59:01 WARN  [pedidos] estoque baixo produto=P02 restam=3
23:59:01 ERROR [pedidos] pagamento recusado id=1042 codigo=402

contagem: {DEBUG: 1, INFO: 1, WARN: 1, ERROR: 1}
...
{"time": "...", "level": "INFO", "logger": "json", "message": "evento estruturado", "usuario": 7, "acao": "login"}
```

## Experimente

- Ligue `as_json` e mande para arquivo; leia de volta com `Serde.from_json_lines`.
- Escreva um logger que também conta erros por código.
- Use `keep(yes)` num teste para verificar que um aviso foi emitido.
