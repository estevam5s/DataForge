<p align="center">
  <img src="https://dataforge-lang.vercel.app/marca-256.png" alt="DataForge" width="120">
</p>

<h1 align="center">DataForge</h1>

<p align="center">
  Uma linguagem de programação interpretada, de propósito geral,
  <br>com <strong>zero dependências</strong> no runtime.
</p>

<p align="center">
  <a href="https://dataforge-lang.vercel.app">Site</a> ·
  <a href="https://dataforge-lang.vercel.app/docs">Documentação</a> ·
  <a href="https://github.com/estevam5s/DataForge">Código</a> ·
  <a href="https://github.com/dataforge-df/docs">Docs em Markdown</a>
</p>

---

## Começar

```bash
docker run --rm -it estevan5s/dataforge repl
```

O console interativo, sem instalar nada. Para rodar um arquivo seu:

```bash
docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df
```

O `-v "$PWD:/app"` monta a pasta atual em `/app`, que é o diretório de
trabalho da imagem. Sem isso, o container não vê os seus arquivos.

---

## A linguagem em trinta segundos

```dataforge
// atribuição, constante, interpolação
x := 10
steady PI := 3.14159
out $"x vale {x}, o dobro é {x * 2}"

// condicional e laços
given x bigger 5:
    out "grande"
otherwise:
    out "pequeno"

cycle i from 1 to 5:
    out i

// ação com tipos
action somar(a: Integer, b: Integer) -> Integer:
    yield a + b

// record imutável, com igualdade estrutural
record Ponto:
    x: Integer
    y: Integer

p := Ponto(3, 4)

// pipeline
out [1, 2, 3, 4, 5, 6]
    >> sift n: n % 2 is 0
    >> morph n: n * 10
    >> distill acc, v: acc + v 0
```

| Conceito | DataForge |
|---|---|
| `=` · `const` · `print` | `:=` · `steady` · `out` |
| `if/elif/else` | `given/orif/otherwise` |
| `for` · `while` | `cycle` · `persist` |
| `def`/`return` | `action`/`yield` |
| `class`/`new` | `blueprint`/`spawn` |
| `try/catch/finally` | `monitor/handle/ensure` |
| `true/false/null` | `yes/no/void` |
| `import`/`export` | `adopt`/`relay` |
| `filter/map/reduce` | `>> sift` / `>> morph` / `>> distill` |
| `//` (divisão inteira) | **`~/`** |

A tabela completa está em
[/docs/referencia](https://dataforge-lang.vercel.app/docs/referencia).

---

## O que vem dentro

| | |
|---|---|
| **Tamanho** | 51 MB comprimida, 259 MB no disco |
| **Base** | `python:3.12-slim` |
| **Usuário** | `forge` (UID 1000) — **não** roda como root |
| **Diretório** | `/app` |
| **Entrypoint** | `dataforge` |
| **CMD padrão** | `repl` |
| **Biblioteca** | 39 módulos, 1348 símbolos |
| **Comandos** | 45, de `run` a `devops` |

### Zero dependência, de verdade

Nada no runtime importa fora da biblioteca padrão do Python — e isso
inclui os drivers de PostgreSQL, MySQL, MariaDB, MongoDB e Redis (um
arquivo por protocolo, sobre socket), o Parquet com metadados em Thrift,
o `.xlsx`, o ChaCha20-Poly1305 (RFC 8439), o WebSocket (RFC 6455) e os
gráficos em SVG.

É por isso que o build não precisa de compilador, e a imagem sai de
`python:3.12-slim` sem uma única camada de `apt-get`.

Dos 259 MB, cerca de 130 são o Python base. O resto é a linguagem
inteira — interpretador, 39 módulos de biblioteca, as ferramentas, e a
extensão do editor, que viaja junto para `dataforge editor` funcionar
sem internet.

---

## Receitas

### Um REPL descartável

```bash
docker run --rm -it estevan5s/dataforge repl
```

### Rodar um arquivo

```bash
docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df
```

### As ferramentas, sobre o seu código

```bash
docker run --rm -v "$PWD:/app" estevan5s/dataforge check src/ --strict
docker run --rm -v "$PWD:/app" estevan5s/dataforge test --cobertura
docker run --rm -v "$PWD:/app" estevan5s/dataforge fmt . --check
docker run --rm -v "$PWD:/app" estevan5s/dataforge lint src/
```

### Um painel de dados

A **Vitrine** transforma um programa de cima para baixo numa página web:

```bash
docker run --rm -v "$PWD:/app" -p 8501:8501 \
  estevan5s/dataforge vitrine run --host=0.0.0.0
```

```dataforge
adopt Arcane.Vitrine as V

action painel():
    V.titulo("Vendas", icone := "📊")
    regiao := V.escolha("Região", ["Sul", "Sudeste", "Norte"])
    V.metrica("Receita", "R$ 850.000", variacao := 18.0)
    V.grafico_barras(vendas_de(regiao), x := "mes")

V.rodar(painel, porta := 8501)
```

O `--host=0.0.0.0` é obrigatório dentro de um container: o padrão é
`127.0.0.1`, que de dentro significa *o próprio container* — e a porta
publicada responderia vazio. **É o erro mais comum ao pôr um servidor
DataForge em Docker**, e o sintoma é enganoso: o log diz "no ar" e o
`curl` de fora não recebe nada.

### Um site ou uma API

```bash
docker run --rm -v "$PWD:/app" -p 8080:8080 estevan5s/dataforge run main.df
```

```dataforge
adopt Kiln

server loja on 8080:
    middleware Kiln.logger()
    middleware Kiln.cors()

    route GET "/api/produtos":
        respond json {"itens": produtos}

    route POST "/api/produtos":
        respond 201 json criar(req["body"])

// 'at "0.0.0.0"' é obrigatório dentro de um container: o padrão do
// 'ignite' é 127.0.0.1, que de dentro significa o próprio container —
// e a porta publicada responderia vazio.
ignite loja on 8080 at "0.0.0.0"
```

O Kiln tem upload `multipart`, SSE e WebSocket — ver
[/docs/kiln](https://dataforge-lang.vercel.app/docs/kiln).

### Numa pipeline de CI

```yaml
- name: verificar
  run: |
    docker run --rm -v "$PWD:/app" estevan5s/dataforge check . --strict
    docker run --rm -v "$PWD:/app" estevan5s/dataforge test --minimo=80
```

---

## Como imagem base

Para empacotar a **sua** aplicação:

```dockerfile
FROM estevan5s/dataforge:1.0.0

# O manifesto ANTES do código: a camada de dependência só é refeita
# quando ele muda. Sem isso, um commit numa linha reinstala tudo.
COPY --chown=forge:forge forge.toml forge.lock* ./
RUN dataforge install

COPY --chown=forge:forge . .

EXPOSE 8501
CMD ["vitrine", "run", "--host=0.0.0.0"]
```

O `ENTRYPOINT` já é `dataforge`, então o `CMD` leva apenas o subcomando.

O próprio DataForge gera esse Dockerfile, com sonda de saúde, usuário
sem privilégio e `.dockerignore`:

```bash
dataforge devops docker        # Dockerfile, .dockerignore, compose
dataforge devops k8s           # deployment, service, ingress, hpa
dataforge devops doctor        # o que falta para subir
```

---

## Docker Compose

Um ambiente completo, com banco:

```yaml
services:
  app:
    image: estevan5s/dataforge
    command: ["vitrine", "run", "--host=0.0.0.0"]
    volumes: ["./:/app"]
    ports: ["8501:8501"]
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: forge
      POSTGRES_PASSWORD: desenvolvimento    # DESENVOLVIMENTO
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U forge"]
      interval: 5s
      retries: 10
```

`service_healthy`, e não `service_started`: o Postgres aceita conexão
segundos depois de o container subir, e sem esperar a sonda a aplicação
falha na primeira consulta — de forma intermitente, que é a pior.

`dataforge devops docker` gera esse compose, com os serviços que o
**seu** código realmente adota.

---

## Tags

| Tag | O quê |
|---|---|
| `latest` | a última publicada |
| `1.0.0` | fixa — use esta em produção |

**Em produção, sempre uma tag fixa.** `latest` muda sob os seus pés, e
um `docker pull` num redeploy pode trazer uma versão que você não
testou.

As tags `4.1.0` e `4.2.0` são da numeração anterior do projeto e
continuam disponíveis, mas a linguagem que elas contêm é mais antiga.

---

## Em produção

Três coisas que valem saber antes:

**Ponha um proxy reverso na frente.** O Kiln e a Vitrine rodam sobre o
`http.server` do Python: não há TLS, HTTP/2 nem compressão. Quem faz
isso é o nginx ou o Caddy — `dataforge devops nginx` gera a
configuração, com as linhas de `Upgrade` que o WebSocket exige e o
`proxy_buffering off` que o SSE exige.

**A sessão da Vitrine vive na memória do processo.** Um processo por
aplicação; com dois, dois pedidos da mesma pessoa caem em memórias
diferentes. No Kubernetes, `sessionAffinity: ClientIP` no Service.

**Não rode como root.** A imagem já não roda — e se você a estender,
mantenha o `USER forge`. Um processo root num container tem capacidades
que não precisa, e um escape de container vira root no host.

Os manifestos de Kubernetes com `resources`, `readinessProbe`,
`livenessProbe` e `securityContext` saem de
`dataforge devops k8s`.

---

## Verificado

| | |
|---|---|
| Testes | 2093 |
| Exercícios | 227, cada um com `assert` |
| Exemplos | 44 programas |
| Documentação | 636 blocos de código que compilam |

A imagem é construída e **executada** na CI a cada push, e há um teste
que confirma que ela não roda como root.

---

## Licença

MIT.
