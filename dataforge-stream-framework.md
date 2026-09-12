# Dataforge Stream Framework

## Framework Web, Dashboard e Data Apps para Dataforge

O **Dataforge Stream Framework** é o framework oficial da linguagem Dataforge
para criação de aplicações web, dashboards interativos, aplicações de dados,
visualizações, ferramentas analíticas e interfaces administrativas.

A proposta é fornecer uma experiência inspirada em frameworks como Streamlit,
porém utilizando a sintaxe, runtime, tipos, módulos e convenções da linguagem
Dataforge.

---

# 1. Objetivos

O framework deve permitir:

- Criar páginas web utilizando código Dataforge.
- Criar dashboards interativos.
- Criar aplicações de análise de dados.
- Exibir tabelas e DataFrames.
- Criar gráficos.
- Criar formulários.
- Criar componentes interativos.
- Receber entradas do usuário.
- Criar layouts responsivos.
- Criar múltiplas páginas.
- Criar menus e navegação.
- Executar código no servidor.
- Trabalhar com bancos de dados.
- Trabalhar com APIs.
- Trabalhar com arquivos.
- Trabalhar com DataFrames.
- Trabalhar com Machine Learning.
- Trabalhar com Big Data.
- Criar aplicações administrativas.
- Criar aplicações de monitoramento.
- Criar aplicações de BI.
- Criar aplicações internas.
- Criar aplicações em tempo real.

---

# 2. Arquitetura

```text
Aplicação Dataforge
       |
       v
Dataforge Stream API
       |
       v
Component System
       |
       +---- Layout Engine
       |
       +---- State Manager
       |
       +---- Event System
       |
       +---- Data Engine
       |
       +---- Chart Engine
       |
       +---- Session Manager
       |
       v
Web Runtime
       |
       +---- HTTP Server
       +---- WebSocket Server
       +---- Static Files
       +---- REST API
       |
       v
Frontend
```

---

# 3. Modelo de execução

A aplicação Dataforge será executada por um runtime próprio.

```text
dataforge stream run main.df
```

O runtime deverá:

1. Carregar o arquivo principal.
2. Inicializar o ambiente.
3. Inicializar o servidor HTTP.
4. Criar uma sessão para cada usuário.
5. Executar a aplicação.
6. Construir a árvore de componentes.
7. Enviar a interface ao navegador.
8. Escutar eventos.
9. Atualizar o estado da aplicação.
10. Re-renderizar os componentes necessários.

---

# 4. Estrutura de projeto

```text
my-dashboard/
│
├── dataforge.toml
├── main.df
│
├── pages/
│   ├── home.df
│   ├── analytics.df
│   └── users.df
│
├── components/
│   ├── header.df
│   ├── sidebar.df
│   └── cards.df
│
├── assets/
│   ├── logo.svg
│   ├── style.css
│   └── images/
│
├── data/
│   └── dataset.csv
│
└── config/
    └── app.df
```

---

# 5. Arquivo dataforge.toml

```toml
[app]
name = "Analytics Dashboard"
version = "1.0.0"
entry = "main.df"

[server]
host = "127.0.0.1"
port = 8501

[server.development]
reload = true
debug = true

[security]
cors = false
csrf = true
secure_headers = true

[session]
enabled = true
timeout = 3600

[assets]
directory = "assets"

[logging]
level = "info"
```

---

# 6. Aplicação mínima

```text
import stream

app = stream.app("Minha aplicação")

app.title("Olá Dataforge")

app.text("Minha primeira aplicação web.")

app.run()
```

---

# 7. Configuração da aplicação

```text
stream.configure(
    title = "Dataforge Dashboard",
    icon = "📊",
    layout = "wide",
    theme = "dark"
)
```

Configurações possíveis:

```text
title
icon
layout
theme
language
timezone
page_width
sidebar
footer
debug
```

---

# 8. Texto

## Texto simples

```text
stream.text("Olá mundo!")
```

## Título

```text
stream.title("Dashboard")
```

## Subtítulo

```text
stream.subtitle("Análise de dados")
```

## Cabeçalho

```text
stream.header("Vendas")
```

## Markdown

```text
stream.markdown("""
# Dashboard

Este é um dashboard criado com Dataforge.
""")
```

## Código

```text
stream.code("""
for user in users:
    print(user)
""")
```

---

# 9. HTML

```text
stream.html("""
<div class="card">
    <h2>Vendas</h2>
    <p>R$ 120.000</p>
</div>
""")
```

HTML arbitrário deverá ser desativado por padrão em ambientes
de produção quando representar risco de XSS.

---

# 10. Componentes

Todos os elementos da interface deverão ser tratados como componentes.

```text
stream.text("Nome")
stream.input("name")
stream.button("Salvar")
stream.table(data)
```

Modelo:

```text
Component
    |
    +-- Text
    +-- Button
    +-- Input
    +-- Select
    +-- Table
    +-- Chart
    +-- Image
    +-- Form
    +-- Container
```

---

# 11. Botões

```text
if stream.button("Clique aqui"):
    stream.success("Botão pressionado!")
```

Tipos:

```text
stream.button()
stream.primary_button()
stream.secondary_button()
stream.danger_button()
```

---

# 12. Entrada de texto

```text
name = stream.input(
    "Nome",
    placeholder = "Digite seu nome"
)
```

Uso:

```text
stream.text("Olá " + name)
```

---

# 13. Número

```text
age = stream.number_input(
    "Idade",
    min = 0,
    max = 120,
    value = 18
)
```

---

# 14. Slider

```text
value = stream.slider(
    "Valor",
    min = 0,
    max = 100,
    value = 50
)
```

---

# 15. Checkbox

```text
enabled = stream.checkbox(
    "Ativar processamento"
)
```

---

# 16. Radio

```text
option = stream.radio(
    "Escolha",
    ["A", "B", "C"]
)
```

---

# 17. Select

```text
country = stream.select(
    "País",
    ["Brasil", "Portugal", "Estados Unidos"]
)
```

---

# 18. Multi Select

```text
languages = stream.multiselect(
    "Linguagens",
    ["Dataforge", "Python", "Java", "Rust"]
)
```

---

# 19. Upload

```text
file = stream.file_upload(
    "Selecione um arquivo"
)

if file:
    stream.text(file.name)
```

Formatos:

```text
CSV
JSON
TXT
PDF
XLSX
PARQUET
IMAGEM
```

---

# 20. Imagens

```text
stream.image("assets/logo.png")
```

Configuração:

```text
stream.image(
    "assets/chart.png",
    width = 500,
    caption = "Gráfico"
)
```

---

# 21. Áudio

```text
stream.audio("audio.mp3")
```

---

# 22. Vídeo

```text
stream.video("video.mp4")
```

---

# 23. Tabelas

```text
stream.table(data)
```

Tabela interativa:

```text
stream.data_table(
    data,
    sortable = true,
    searchable = true,
    pagination = true
)
```

Funcionalidades:

```text
sorting
filtering
pagination
selection
editing
column formatting
export
search
```

---

# 24. DataFrame

O framework deverá possuir integração nativa com o sistema de dados da
linguagem Dataforge.

```text
df = data.read_csv("sales.csv")

stream.dataframe(df)
```

---

# 25. Gráficos

## Linha

```text
stream.line_chart(df)
```

## Barras

```text
stream.bar_chart(df)
```

## Área

```text
stream.area_chart(df)
```

## Dispersão

```text
stream.scatter_chart(df)
```

## Pizza

```text
stream.pie_chart(df)
```

## Histograma

```text
stream.histogram(df)
```

---

# 26. API de gráficos

```text
chart = stream.chart("line")

chart.x("date")
chart.y("sales")

chart.title("Vendas por período")

stream.render(chart)
```

---

# 27. Sistema de layout

```text
with stream.container():

    stream.title("Dashboard")

    stream.text("Conteúdo")
```

---

# 28. Colunas

```text
with stream.columns(3) as cols:

    with cols[0]:
        stream.metric("Vendas", "R$ 100K")

    with cols[1]:
        stream.metric("Clientes", "2.500")

    with cols[2]:
        stream.metric("Pedidos", "8.400")
```

---

# 29. Sidebar

```text
with stream.sidebar():

    stream.title("Menu")

    page = stream.select(
        "Página",
        ["Home", "Analytics", "Configurações"]
    )
```

---

# 30. Tabs

```text
with stream.tabs(["Visão geral", "Dados", "Configurações"]) as tabs:

    with tabs[0]:
        stream.text("Visão geral")

    with tabs[1]:
        stream.dataframe(df)

    with tabs[2]:
        stream.text("Configurações")
```

---

# 31. Expander

```text
with stream.expander("Detalhes"):

    stream.text("Informações adicionais")
```

---

# 32. Container horizontal

```text
with stream.row():

    stream.button("Salvar")
    stream.button("Cancelar")
```

---

# 33. Cards

```text
stream.card(
    title = "Receita",
    value = "R$ 150.000",
    description = "+15%"
)
```

---

# 34. Métricas

```text
stream.metric(
    "Receita",
    "R$ 150.000",
    delta = "+12%"
)
```

---

# 35. Alertas

```text
stream.success("Operação realizada!")

stream.info("Informação")

stream.warning("Atenção!")

stream.error("Erro!")
```

---

# 36. Loading

```text
with stream.spinner("Processando..."):

    data = process_data()
```

---

# 37. Progress

```text
progress = stream.progress(0)

for i in range(100):

    process(i)

    progress.update(i)
```

---

# 38. Formulários

```text
with stream.form("user_form"):

    name = stream.input("Nome")
    email = stream.input("Email")

    submitted = stream.submit("Cadastrar")

    if submitted:

        create_user(name, email)

        stream.success("Usuário cadastrado!")
```

---

# 39. Estado da sessão

```text
if not stream.state.exists("counter"):

    stream.state.set("counter", 0)
```

Incremento:

```text
if stream.button("Incrementar"):

    value = stream.state.get("counter")

    stream.state.set(
        "counter",
        value + 1
    )
```

Exibição:

```text
stream.text(
    stream.state.get("counter")
)
```

---

# 40. Estado global

```text
stream.global_state.set(
    "application_version",
    "1.0.0"
)
```

O estado global deverá ser utilizado com cuidado.

---

# 41. Cache

```text
@stream.cache
function load_data():

    return database.query(
        "SELECT * FROM sales"
    )
```

Cache por parâmetros:

```text
@stream.cache
function calculate(value):

    return expensive_operation(value)
```

O sistema deverá possuir:

```text
TTL
LRU
memory cache
disk cache
distributed cache
cache invalidation
```

---

# 42. Banco de dados

```text
db = database.connect(
    "postgresql://localhost/analytics"
)
```

Consulta:

```text
df = db.query("""
    SELECT
        date,
        sales
    FROM sales
""")
```

Exibição:

```text
stream.dataframe(df)
```

Bancos suportados poderão incluir:

```text
PostgreSQL
MySQL
MariaDB
SQLite
SQL Server
Oracle
MongoDB
Redis
DuckDB
```

---

# 43. APIs

```text
response = http.get(
    "https://api.example.com/users"
)

data = response.json()

stream.json(data)
```

O framework também poderá disponibilizar APIs:

```text
@stream.api.get("/users")
function users():

    return database.users()
```

---

# 44. REST API

Suporte para:

```text
GET
POST
PUT
PATCH
DELETE
OPTIONS
HEAD
```

Exemplo:

```text
@stream.api.get("/api/users")
function get_users():

    return users.all()
```

---

# 45. WebSocket

```text
@stream.websocket("/events")
function events(socket):

    while socket.connected():

        message = socket.receive()

        socket.send(message)
```

Aplicações:

```text
chat
monitoramento
dashboards
telemetria
logs
IoT
```

---

# 46. Atualização em tempo real

```text
stream.autorefresh(
    interval = 5
)
```

O dashboard poderá atualizar automaticamente.

---

# 47. Multipáginas

Estrutura:

```text
pages/
├── home.df
├── analytics.df
├── customers.df
└── settings.df
```

Registro de páginas:

```text
stream.page(
    "/analytics",
    "Analytics",
    analytics
)
```

---

# 48. Roteamento

```text
@stream.route("/")
function home():

    stream.title("Home")
```

Outra rota:

```text
@stream.route("/analytics")
function analytics():

    stream.title("Analytics")
```

---

# 49. Parâmetros de URL

```text
@stream.route("/users/{id}")
function user(id):

    user = database.find_user(id)

    stream.json(user)
```

---

# 50. Autenticação

O framework deverá suportar:

```text
session authentication
JWT
OAuth2
OpenID Connect
API Keys
Basic Authentication
```

Exemplo:

```text
if not stream.authenticated():

    stream.redirect("/login")
```

---

# 51. Autorização

```text
if stream.user.has_role("admin"):

    stream.admin_panel()
```

Permissões:

```text
admin
manager
analyst
user
guest
```

---

# 52. Segurança

O framework deverá possuir proteção nativa contra:

```text
XSS
CSRF
SQL Injection
Command Injection
Path Traversal
Session Fixation
Clickjacking
Open Redirect
HTTP Header Injection
```

Também deverá oferecer:

```text
secure cookies
security headers
CORS
CSRF tokens
rate limiting
input validation
output encoding
authentication
authorization
audit logs
```

---

# 53. CORS

```text
stream.security.cors(
    enabled = true,
    origins = [
        "https://example.com"
    ]
)
```

---

# 54. Rate Limiting

```text
stream.security.rate_limit(
    requests = 100,
    window = 60
)
```

---

# 55. Logs

```text
logger.info("Servidor iniciado")

logger.warning("Operação suspeita")

logger.error("Falha no banco")
```

Níveis:

```text
TRACE
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

---

# 56. Tratamento de erros

```text
try:

    result = process()

except Error as error:

    stream.error(
        error.message
    )
```

O servidor não deverá expor stack traces ao usuário em produção.

---

# 57. Tema

```text
stream.theme(
    mode = "dark"
)
```

Modos:

```text
light
dark
system
```

---

# 58. Tema personalizado

```text
stream.theme.configure(

    primary_color = "#FFD43B",

    background = "#111111",

    text_color = "#FFFFFF",

    font = "Inter"
)
```

---

# 59. CSS

```text
stream.css("""
.card {
    border-radius: 12px;
    padding: 20px;
}
""")
```

O CSS deverá ser opcional.

---

# 60. JavaScript

```text
stream.javascript("""
console.log("Dataforge");
""")
```

O JavaScript deverá ser tratado como recurso avançado e possuir
mecanismos de segurança.

---

# 61. Componentes personalizados

```text
component UserCard:

    property name
    property email

    render:

        stream.card(
            title = name,
            description = email
        )
```

Uso:

```text
UserCard(
    name = "João",
    email = "joao@example.com"
)
```

---

# 62. Sistema de componentes

```text
Component
│
├── Layout
│   ├── Container
│   ├── Row
│   ├── Column
│   ├── Tabs
│   └── Sidebar
│
├── Input
│   ├── TextInput
│   ├── NumberInput
│   ├── Slider
│   ├── Checkbox
│   ├── Select
│   └── FileUpload
│
├── Data
│   ├── Table
│   ├── DataFrame
│   └── JSON
│
├── Visualization
│   ├── LineChart
│   ├── BarChart
│   ├── PieChart
│   └── ScatterChart
│
└── Feedback
    ├── Alert
    ├── Spinner
    ├── Progress
    └── Toast
```

---

# 63. Eventos

```text
button.on_click(
    handle_click
)
```

Exemplo:

```text
function handle_click():

    stream.success("Executado!")
```

---

# 64. Eventos disponíveis

```text
on_click
on_change
on_submit
on_select
on_upload
on_load
on_mount
on_unmount
on_focus
on_blur
```

---

# 65. Programação reativa

Exemplo:

```text
name = stream.input("Nome")

stream.text(
    "Olá " + name
)
```

Quando o valor de `name` mudar, o framework deverá atualizar
automaticamente o componente dependente.

---

# 66. Árvore de componentes

```text
Application
│
└── Page
    │
    ├── Header
    ├── Sidebar
    │
    └── Container
        │
        ├── Metric
        ├── Chart
        └── DataTable
```

---

# 67. Virtual DOM / Component Tree

O runtime poderá utilizar uma árvore virtual:

```text
Application
      |
      v
Component Tree
      |
      v
Diff Engine
      |
      v
DOM Updates
```

O objetivo é evitar a reconstrução completa da página quando somente
um componente foi alterado.

---

# 68. Comunicação Frontend ↔ Backend

```text
Browser
   |
   | HTTP
   v
Dataforge Server
   |
   | WebSocket
   v
Session Runtime
   |
   v
Dataforge Application
```

Eventos:

```text
USER_INPUT
BUTTON_CLICK
FORM_SUBMIT
SELECT_CHANGE
FILE_UPLOAD
PAGE_CHANGE
```

---

# 69. Sessões

Cada usuário deverá possuir uma sessão independente.

```text
Session
│
├── session_id
├── user
├── state
├── components
├── permissions
└── metadata
```

Gerenciamento:

```text
session.id()
session.user()
session.state()
session.destroy()
```

---

# 70. Arquivos estáticos

```text
stream.static(
    directory = "assets"
)
```

Arquivos:

```text
CSS
JavaScript
SVG
PNG
JPG
fonts
```

---

# 71. Download de arquivos

```text
stream.download(
    label = "Baixar CSV",
    data = csv_data,
    filename = "result.csv"
)
```

---

# 72. Upload de múltiplos arquivos

```text
files = stream.file_upload(
    "Arquivos",
    multiple = true
)
```

---

# 73. Exportação de dados

O framework deverá permitir:

```text
CSV
JSON
Excel
Parquet
PDF
```

Exemplo:

```text
stream.download(
    "Exportar CSV",
    df.to_csv(),
    "data.csv"
)
```

---

# 74. Machine Learning

Integração com modelos:

```text
model = ml.load("model.dfml")

prediction = model.predict(data)

stream.metric(
    "Predição",
    prediction
)
```

---

# 75. Big Data

O framework deverá trabalhar com grandes volumes de dados.

Integrações possíveis:

```text
Dataforge DataFrame
Apache Arrow
Parquet
DuckDB
Spark
Distributed DataFrames
Streaming Data
```

---

# 76. Streaming de dados

```text
stream_data = data.stream(
    "events"
)

for event in stream_data:

    stream.update(
        event
    )
```

Aplicações:

```text
IoT
logs
telemetria
mercado financeiro
monitoramento
Big Data
```

---

# 77. Dashboard completo

```text
import stream
import data

stream.configure(
    title = "Business Intelligence",
    layout = "wide",
    theme = "dark"
)

df = data.read_csv("sales.csv")

stream.title("Dashboard de Vendas")

with stream.columns(4) as cols:

    with cols[0]:

        stream.metric(
            "Receita",
            "R$ 850.000",
            "+18%"
        )

    with cols[1]:

        stream.metric(
            "Clientes",
            "12.450",
            "+8%"
        )

    with cols[2]:

        stream.metric(
            "Pedidos",
            "32.500",
            "+14%"
        )

    with cols[3]:

        stream.metric(
            "Conversão",
            "8.4%",
            "+1.2%"
        )

stream.header("Evolução das vendas")

stream.line_chart(df)

stream.header("Dados")

stream.data_table(
    df,
    searchable = true,
    pagination = true
)
```

---

# 78. Estrutura interna do framework

```text
dataforge-stream/
│
├── runtime/
│   ├── application
│   ├── session
│   ├── state
│   ├── scheduler
│   └── events
│
├── server/
│   ├── http
│   ├── websocket
│   ├── routing
│   ├── middleware
│   └── static
│
├── components/
│   ├── core
│   ├── layout
│   ├── input
│   ├── data
│   ├── charts
│   └── feedback
│
├── frontend/
│   ├── runtime
│   ├── renderer
│   ├── events
│   └── components
│
├── security/
│   ├── csrf
│   ├── cors
│   ├── headers
│   ├── auth
│   └── rate_limit
│
├── data/
│   ├── dataframe
│   ├── csv
│   ├── json
│   └── parquet
│
└── cli/
    └── commands
```

---

# 79. CLI

Criar projeto:

```text
dataforge stream create my-dashboard
```

Executar:

```text
dataforge stream run
```

Executar com arquivo:

```text
dataforge stream run main.df
```

Modo desenvolvimento:

```text
dataforge stream dev
```

Build:

```text
dataforge stream build
```

Deploy:

```text
dataforge stream deploy
```

Diagnóstico:

```text
dataforge stream doctor
```

---

# 80. Hot Reload

Durante o desenvolvimento:

```text
dataforge stream dev
```

Fluxo:

```text
main.df changed
     |
     v
Recompile
     |
     v
Reload application
```

---

# 81. Desenvolvimento e produção

Desenvolvimento:

```text
dataforge stream dev
```

Características:

```text
hot reload
debug
logs detalhados
source maps
development errors
```

Produção:

```text
dataforge stream run --production
```

Características:

```text
optimized runtime
compression
secure headers
logging
caching
worker processes
health checks
```

---

# 82. Workers

```text
dataforge stream run \
    --workers 4 \
    --host 0.0.0.0 \
    --port 8501
```

---

# 83. Health Check

Endpoint:

```text
/health
```

Resposta:

```json
{
    "status": "healthy"
}
```

---

# 84. Métricas

Endpoint:

```text
/metrics
```

Possíveis métricas:

```text
requests_total
request_duration
active_sessions
memory_usage
cpu_usage
errors_total
websocket_connections
```

---

# 85. Observabilidade

O framework deverá oferecer integração com:

```text
logs
metrics
traces
health checks
audit logs
```

Arquitetura:

```text
Application
    |
    +---- Logs
    |
    +---- Metrics
    |
    +---- Traces
    |
    +---- Audit
```

---

# 86. Middleware

```text
middleware logger
middleware cors
middleware auth
middleware csrf
middleware rate_limit
```

Exemplo:

```text
app.use(
    middleware.authentication()
)
```

---

# 87. Plugins

O framework deverá possuir arquitetura extensível.

```text
plugin charts
plugin database
plugin authentication
plugin maps
plugin machine_learning
plugin big_data
```

Instalação:

```text
dataforge add stream-charts
```

---

# 88. API pública

```text
stream.app
stream.text
stream.title
stream.header

stream.button
stream.input
stream.select
stream.checkbox

stream.table
stream.dataframe

stream.line_chart
stream.bar_chart

stream.container
stream.columns
stream.tabs
stream.sidebar

stream.state
stream.cache

stream.auth
stream.security

stream.api
stream.route
```

---

# 89. Princípios da API

A API deverá seguir:

```text
simple
declarative
reactive
type-safe
secure
extensible
testable
performant
```

---

# 90. Tipagem

Os componentes deverão utilizar tipos nativos da Dataforge.

```text
name: String = stream.input("Nome")

age: Int = stream.number_input("Idade")

enabled: Bool = stream.checkbox("Ativo")
```

---

# 91. Validação

```text
email = stream.input("Email")

if not validation.email(email):

    stream.error(
        "Email inválido"
    )
```

Idealmente:

```text
email = stream.input(
    "Email",
    validator = validation.email
)
```

---

# 92. Acessibilidade

Todos os componentes deverão considerar:

```text
ARIA
keyboard navigation
screen readers
focus management
contrast
semantic HTML
```

---

# 93. Internacionalização

```text
stream.i18n.language("pt-BR")
```

Exemplo:

```text
stream.translate("dashboard.title")
```

Idiomas:

```text
pt-BR
en-US
es
fr
de
```

---

# 94. Responsividade

Os componentes deverão funcionar em:

```text
desktop
tablet
mobile
```

O layout deverá se adaptar automaticamente.

---

# 95. PWA

Opcionalmente:

```text
stream.pwa(
    enabled = true
)
```

Possibilitando:

```text
installable application
offline cache
service worker
mobile experience
```

---

# 96. Testes

O framework deverá possuir suporte para testes.

```text
test "dashboard renders":

    app = stream.test_app(
        main
    )

    response = app.render()

    assert response.contains(
        "Dashboard"
    )
```

---

# 97. Teste de componentes

```text
test "button":

    component = stream.test(
        stream.button("Salvar")
    )

    assert component.exists()
```

---

# 98. Teste de eventos

```text
test "counter":

    app = stream.test_app(counter)

    app.click("Incrementar")

    assert app.text("1")
```

---

# 99. Testes HTTP

```text
test "users endpoint":

    response = http.test.get(
        "/api/users"
    )

    assert response.status == 200
```

---

# 100. Performance

O framework deverá possuir:

```text
component caching
lazy rendering
async execution
connection pooling
compression
static asset caching
incremental rendering
WebSocket optimization
```

---

# 101. Execução assíncrona

```text
async function load_data():

    return await database.query(...)
```

Uso:

```text
data = await load_data()

stream.dataframe(data)
```

---

# 102. Jobs em background

```text
job = stream.background(
    process_large_dataset
)
```

Consulta:

```text
job.status()
job.progress()
job.result()
```

---

# 103. Agendamento

```text
stream.schedule(
    process_data,
    every = "1h"
)
```

---

# 104. Arquitetura final

```text
                 Dataforge Stream
                       |
       +---------------+---------------+
       |               |               |
    UI Layer       Data Layer      Server Layer
       |               |               |
 Components        DataFrame         HTTP
 Layout             SQL              REST
 Forms              Files            WebSocket
 Charts             APIs             Routing
       |               |               |
       +---------------+---------------+
                       |
                    Runtime
                       |
                Session Manager
                       |
                  State Engine
                       |
                 Event System
                       |
                Reactive Engine
                       |
                 Security Layer
                       |
                Dataforge Runtime
```

---

# 105. Objetivo do Dataforge Stream

O objetivo não é simplesmente criar um clone do Streamlit.

O objetivo é criar um **framework web nativo do ecossistema Dataforge**,
integrado diretamente com:

```text
Dataforge Language
        |
        +-- Type System
        +-- OOP
        +-- Modules
        +-- Async
        +-- Testing
        +-- DataFrames
        +-- Big Data
        +-- Database
        +-- Machine Learning
        +-- Security
        +-- HTTP
        +-- REST
        +-- WebSocket
        |
        v
Dataforge Stream
        |
        +-- Web Applications
        +-- Dashboards
        +-- Data Apps
        +-- BI
        +-- Analytics
        +-- Monitoring
        +-- Admin Panels
        +-- Internal Tools
```

Assim, o desenvolvedor poderá utilizar uma única linguagem para
programação, dados, backend e construção da interface web.

---

# 106. Roadmap recomendado

## Fase 1 — Core

Implementar primeiro:

```text
Application
Page
Component
Container
Text
Title
Button
Input
Select
Checkbox
```

## Fase 2 — Layout

```text
Columns
Rows
Sidebar
Tabs
Expander
Cards
Forms
```

## Fase 3 — Data

```text
DataFrame
Table
CSV
JSON
Parquet
Database
```

## Fase 4 — Visualização

```text
Line Chart
Bar Chart
Area Chart
Pie Chart
Scatter Chart
Histogram
```

## Fase 5 — Runtime

```text
HTTP Server
WebSocket
Sessions
State
Reactive Engine
Component Tree
```

## Fase 6 — Segurança

```text
Authentication
Authorization
CSRF
CORS
Rate Limiting
Security Headers
Input Validation
```

## Fase 7 — Produção

```text
Workers
Caching
Compression
Observability
Health Checks
Metrics
Logging
```

## Fase 8 — Ecossistema

```text
Plugins
CLI
Package Manager
Themes
PWA
Machine Learning
Big Data
Cloud Deployment
```

---

# 107. Resultado esperado

Ao final, a Dataforge deverá permitir criar aplicações como:

```text
                    Dataforge
                        |
             +----------+----------+
             |          |          |
          Backend     Data       Frontend
             |          |          |
           REST       SQL       Dashboard
           HTTP     DataFrame     Forms
        WebSocket   Big Data      Charts
           Auth       ML          Tables
             |          |          |
             +----------+----------+
                        |
                 Dataforge Stream
```

O desenvolvedor poderá criar um dashboard inteiro sem precisar
utilizar Python, JavaScript ou outro framework externo como requisito
da API pública.

O frontend continuará sendo executado no navegador, mas toda a
experiência de desenvolvimento será exposta através da linguagem
Dataforge.
