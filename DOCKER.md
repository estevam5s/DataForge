<div align="center">

<img src="https://dataforge-lang.vercel.app/marca-256.png" alt="DataForge" width="120" height="120">

# DataForge

**Uma linguagem de programação interpretada, de propósito geral, com vocabulário próprio.**

<sub>

`Python 3.12` · `sem dependências no runtime` · `multi-estágio` · `usuário sem privilégio` · `~120 MB`

</sub>

[![Docker Pulls](https://img.shields.io/docker/pulls/estevan5s/dataforge)](https://hub.docker.com/r/estevan5s/dataforge)
[![Image Size](https://img.shields.io/docker/image-size/estevan5s/dataforge/latest)](https://hub.docker.com/r/estevan5s/dataforge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Documentação](https://dataforge-lang.vercel.app/docs) ·
[Tutorial](https://dataforge-lang.vercel.app/docs/primeiros-passos) ·
[GitHub](https://github.com/estevam5s/DataForge)

</div>

---

## Começar em 10 segundos

```bash
docker run --rm -it estevan5s/dataforge repl
```

```text
forge> nums := [1, 2, 3, 4, 5, 6]
forge> out nums >> sift n: n % 2 is 0 >> morph n: n * 10
[20, 40, 60]
```

## Rodar o seu arquivo

```bash
docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df
```

O `-v "$PWD:/app"` monta a pasta atual em `/app`, que é o diretório de
trabalho da imagem. Sem ele, o container não enxerga arquivo nenhum seu.

## O que há dentro

| | |
|---|---|
| Base | `python:3.12-slim` |
| Usuário | `forge` — **não é root** |
| Diretório | `/app` |
| Entrypoint | `dataforge` |
| Comando padrão | `repl` |
| Dependências | **nenhuma** além da stdlib do Python |

A imagem é **multi-estágio**: as ferramentas de build ficam no primeiro
estágio e não chegam à imagem final. O que se baixa é o interpretador, a
biblioteca padrão e nada mais.

## Todos os comandos

O entrypoint é o `dataforge`, então qualquer subcomando funciona:

```bash
# executar
docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df
docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df --time

# qualidade
docker run --rm -v "$PWD:/app" estevan5s/dataforge check src/
docker run --rm -v "$PWD:/app" estevan5s/dataforge fmt . --check
docker run --rm -v "$PWD:/app" estevan5s/dataforge lint src/
docker run --rm -v "$PWD:/app" estevan5s/dataforge test tests/

# complexidade
docker run --rm -v "$PWD:/app" estevan5s/dataforge big-o src/

# projeto
docker run --rm -v "$PWD:/app" estevan5s/dataforge init meu-app
docker run --rm -v "$PWD:/app" estevan5s/dataforge new api minha-api

# interativo
docker run --rm -it estevan5s/dataforge repl
```

### Um apelido que poupa digitação

```bash
alias df-docker='docker run --rm -it -v "$PWD:/app" estevan5s/dataforge'

df-docker run main.df
df-docker check src/
df-docker repl
```

## Servidor web (Kiln)

O Kiln escuta em `0.0.0.0` dentro do container — em `127.0.0.1` ele
ficaria inalcançável de fora, que é o erro mais comum ao conteinerizar
um servidor.

```dataforge
// app.df
adopt Kiln

server api on 8080:
    route GET "/":
        respond {"linguagem": "DataForge", "versao": "1.0.0"}

    route GET "/saude":
        respond {"ok": yes}

ignite api
```

```bash
docker run --rm -p 8080:8080 -v "$PWD:/app" estevan5s/dataforge run app.df
curl localhost:8080
```

## Como imagem base

```dockerfile
FROM estevan5s/dataforge:1.0.0

WORKDIR /app
COPY forge.toml .
RUN dataforge install          # resolve as dependências primeiro

COPY src/ ./src/
RUN dataforge check src/ --strict    # o build falha se o código não passar

EXPOSE 8080
CMD ["run", "src/main.df"]
```

> **Copie o `forge.toml` antes do código.** As dependências mudam menos
> que o código; nessa ordem, o Docker reaproveita a camada do `install`
> em toda build que só mexeu em `src/`.

## docker compose

```yaml
services:
  api:
    image: estevan5s/dataforge:1.0.0
    command: run src/main.df
    ports: ["8080:8080"]
    volumes: [".:/app"]
    environment:
      DATAFORGE_ENV: producao

  testes:
    image: estevan5s/dataforge:1.0.0
    command: test tests/
    volumes: [".:/app"]
    profiles: ["ci"]
```

```bash
docker compose up api
docker compose --profile ci run --rm testes
```

## No CI

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  verificar:
    runs-on: ubuntu-latest
    container: estevan5s/dataforge:1.0.0
    steps:
      - uses: actions/checkout@v4
      - run: dataforge check src/ --strict
      - run: dataforge fmt . --check
      - run: dataforge lint src/
      - run: dataforge test tests/
```

Como o container **já é** o ambiente, não há passo de instalação — e a
versão do interpretador fica presa na tag da imagem, então o CI de hoje
roda igual daqui a um ano.

## Etiquetas

| Tag | O que é |
|---|---|
| `latest` | a última versão estável |
| `1.0.0` | uma versão fixa — **use esta em produção** |
| `1.0` | a última correção da 1.0 |

`latest` muda sem avisar. Num Dockerfile ou num CI, fixe a versão: é a
diferença entre um build reproduzível e um que quebra numa terça-feira
sem ninguém ter mexido em nada.

## Permissões de arquivo

O container não roda como root. Se os arquivos que ele cria aparecerem
com dono errado na sua máquina, force o seu próprio usuário:

```bash
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD:/app" \
  estevan5s/dataforge run main.df
```

## Construir a sua

```bash
git clone https://github.com/estevam5s/DataForge
cd DataForge
docker build -t dataforge .
docker run --rm -it dataforge repl
```

## A linguagem, em 20 linhas

```dataforge
// atribuição, constante, interpolação
x := 10
steady PI := 3.14159
out $"x vale {x}, o dobro é {x * 2}"

// condicional e laço
given x bigger 5:
    out "grande"
otherwise:
    out "pequeno"

cycle i from 1 to 3:
    out i

// ação, record, pipeline
action somar(a: Integer, b: Integer) -> Integer:
    yield a + b

record Ponto:
    x: Integer
    y: Integer

out [1, 2, 3, 4, 5, 6]
    >> sift n: n % 2 is 0
    >> morph n: n * 10
    >> distill acc, v: acc + v 0
```

| Conceito | DataForge |
|---|---|
| `=` | `:=` |
| `print` | `out` |
| `if/elif/else` | `given/orif/otherwise` |
| `for` / `while` | `cycle` / `persist` |
| `def` / `return` | `action` / `yield` |
| `class` / `new` | `blueprint` / `spawn` |
| `try/catch/finally` | `monitor/handle/ensure` |
| `true/false/null` | `yes/no/void` |
| `//` (div. inteira) | **`~/`** |

## O que vem junto

**32 módulos de biblioteca padrão**, todos sem dependência externa:

- **Kiln** — framework web: rotas, middleware, templates, sessão, CSRF
- **Crucible** — framework de testes: matchers, fixtures, dublês
- **Forge** — SQLite, Postgres, MySQL, Redis e MongoDB por protocolo próprio
- **Arcane.Lago** — Parquet nativo e Data Lake com partições Hive
- **Arcane.Pipeline** — ETL com DAG, retry e carga incremental
- **Arcane.Cortex** — regressão, floresta, k-NN, Naive Bayes, PCA
- **Arcane.Stream** — tópicos, partições e offsets
- e mais 25.

## Links

- **Documentação:** https://dataforge-lang.vercel.app/docs
- **Primeiros passos:** https://dataforge-lang.vercel.app/docs/primeiros-passos
- **216 exercícios:** https://dataforge-lang.vercel.app/docs/exercicios
- **GitHub:** https://github.com/estevam5s/DataForge

## Licença

MIT.
