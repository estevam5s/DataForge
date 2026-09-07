# Exercicio 166 — Servidor HTTP

## Enunciado

Monte uma API REST com rotas, parâmetros de caminho, JSON e validação.

> Este exercício **configura** a aplicação sem abrir a porta, para poder rodar na
> suíte de testes. Acrescente `Http.listen(app, 3000)` no fim para subir de
> verdade.

## Montar a aplicação

```dataforge
app := Http.create("API de Tarefas")
Http.cors(app)         // libera chamadas de outra origem
Http.logger(app)       // registra cada requisição
```

## Rotas

```dataforge
Http.get(app, "/api/tarefas", listar)
Http.get(app, "/api/tarefas/:id", buscar)
Http.post(app, "/api/tarefas", criar)
Http.put(app, "/api/tarefas/:id", concluir)
Http.delete(app, "/api/tarefas/:id", remover)
```

O `:id` é um **parâmetro de caminho**, disponível em `req["params"]["id"]` — como
texto, sempre. Converta antes de comparar:

```dataforge
id := cast req["params"]["id"] as Integer
```

## O par requisição/resposta

| Leitura | Contém |
|---------|--------|
| `req["params"]` | parâmetros do caminho (`:id`) |
| `req["query"]` | da query string (`?pagina=2`) |
| `req["json"]` | o corpo, já interpretado |
| `req["headers"]` | os cabeçalhos |

| Escrita | Faz |
|---------|-----|
| `res.json(dados)` | responde JSON com 200 |
| `res.json(dados, 404)` | com o código que você escolher |
| `res.html(texto)` | responde HTML |
| `res.send(texto, 200)` | texto puro |

## Códigos que importam

| Código | Quando |
|--------|--------|
| 200 | deu certo |
| 201 | criou algo novo |
| 400 | o cliente mandou dado inválido |
| 404 | não existe |
| 500 | o servidor quebrou |

Devolver 200 com `{"erro": ...}` no corpo obriga todo cliente a inspecionar o
JSON para saber se deu certo. O código HTTP existe justamente para isso.

## Validação fora da rota

```dataforge
action validar_tarefa(corpo):
    problemas := []
    given "titulo" not in corpo:
        problemas.append("titulo e obrigatorio")
    orif len(corpo["titulo"].trim()) smaller 3:
        problemas.append("titulo precisa de ao menos 3 letras")
    yield problemas
```

Duas vantagens de separar:

1. **Testável sem servidor** — como este exercício demonstra.
2. **Reutilizável** — a mesma validação serve para POST e PUT.

E devolver **todos** os problemas de uma vez poupa o cliente de descobrir um erro
por requisição.

## Saída esperada

```
── rotas registradas ──
  GET    /api/tarefas
  ...

── validacao ──
  sem corpo:      [corpo ausente]
  sem titulo:     [titulo e obrigatorio]
  titulo curto:   [titulo precisa de ao menos 3 letras]
  valido:         []

tarefas iniciais: 2
```

## Experimente

- Acrescente `Http.listen(app, 3000)` e teste com `curl`:
  ```bash
  curl localhost:3000/api/tarefas
  curl -X POST localhost:3000/api/tarefas -H 'Content-Type: application/json' -d '{"titulo":"Nova"}'
  ```
- Troque a lista em memória por `Arcane.Database`.
- Acrescente paginação com `req["query"]["pagina"]`.
