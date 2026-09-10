# Servidor HTTP / Framework Web

## Visão geral

Servidor completo para aplicações web, APIs REST/RESTful, microsserviços e aplicações HTTP.

Principais recursos:

- HTTP/HTTPS
- Roteamento
- Middleware
- APIs REST e RESTful
- CRUD
- Autenticação e autorização
- Sessões e cookies
- CORS e CSRF
- Rate limiting
- Validação e sanitização
- Compressão e cache
- Upload/download
- WebSocket e SSE
- Streaming
- Logs, métricas e tracing
- OpenAPI
- HTTP/2 e HTTP/3
- Proxy reverso
- Health checks
- Graceful shutdown
- Testes
- CLI
- Plugins

---

## 1. Servidor

```js
const app = server()

app.listen(3000)
```

Configuração:

```js
app.listen({
    port: 3000,
    host: "0.0.0.0"
})
```

---

## 2. Métodos HTTP

Suporte a:

```text
GET
POST
PUT
PATCH
DELETE
HEAD
OPTIONS
CONNECT
TRACE
```

```js
app.get("/users", handler)
app.post("/users", handler)
app.put("/users/:id", handler)
app.patch("/users/:id", handler)
app.delete("/users/:id", handler)
```

---

## 3. Request

```js
request.method
request.url
request.path
request.query
request.params
request.headers
request.body
request.cookies
request.ip
request.protocol
request.hostname
request.originalUrl
request.user
request.files
request.id
request.session
request.signal
```

---

## 4. Response

```js
res.status()
res.json()
res.send()
res.text()
res.html()
res.redirect()
res.download()
res.file()
res.cookie()
res.clearCookie()
res.header()
res.setHeader()
res.type()
res.end()
res.stream()
res.etag()
```

Exemplo:

```js
app.get("/hello", (req, res) => {
    res.status(200).json({
        message: "Hello World"
    })
})
```

---

## 5. Roteamento

```js
app.get("/", handler)
app.get("/users", handler)
app.post("/users", handler)
app.delete("/users/:id", handler)
```

Parâmetros:

```js
app.get("/users/:id", (req, res) => {
    const id = req.params.id
})
```

Múltiplos parâmetros:

```js
app.get("/users/:userId/posts/:postId", handler)
```

Wildcard:

```js
app.get("/files/*", handler)
```

---

## 6. Router

```js
const router = Router()

router.get("/", getUsers)
router.post("/", createUser)
router.get("/:id", getUser)
router.put("/:id", updateUser)
router.delete("/:id", deleteUser)

app.use("/users", router)
```

---

## 7. Middleware

```js
app.use((req, res, next) => {
    console.log(req.method, req.url)
    next()
})
```

Middleware pode:

- modificar request
- modificar response
- autenticar usuários
- validar dados
- registrar logs
- bloquear requisições
- adicionar headers
- tratar erros

Middleware por rota:

```js
app.get(
    "/admin",
    auth(),
    role("admin"),
    controller
)
```

---

## 8. Body Parser

Suporte a:

```text
application/json
application/x-www-form-urlencoded
multipart/form-data
text/plain
application/octet-stream
```

```js
app.use(json())
```

Dados:

```js
req.body
```

---

## 9. Query Parameters

```text
GET /users?page=1&limit=20
```

```js
const page = req.query.page
const limit = req.query.limit
```

---

## 10. Cookies e sessões

```js
res.cookie("session", token, {
    httpOnly: true,
    secure: true,
    sameSite: "lax"
})
```

```js
req.cookies.session
```

Sessões:

```js
app.use(session({
    secret: env.SESSION_SECRET,
    expiration: "7d"
}))
```

---

## 11. Autenticação

Suporte a:

```text
Basic Auth
Bearer Token
JWT
Session
API Key
OAuth 2.0
OpenID Connect
WebAuthn
```

Exemplo:

```js
app.use(jwt({
    secret: env.JWT_SECRET
}))
```

---

## 12. Autorização

RBAC:

```js
app.get(
    "/admin",
    auth(),
    role("admin"),
    adminController
)
```

Permissões:

```text
users:read
users:create
users:update
users:delete
```

ABAC:

```js
authorize(user, resource, action)
```

---

## 13. API REST

Modelo:

```text
GET    /users
POST   /users
GET    /users/:id
PUT    /users/:id
PATCH  /users/:id
DELETE /users/:id
```

O framework deve oferecer:

- Resources
- Nested Resources
- Paginação
- Filtros
- Ordenação
- Busca
- Seleção de campos
- Relacionamentos
- ETag
- Cache
- Content Negotiation
- Idempotência
- Versionamento

---

## 14. CRUD automático

```js
resource("users", UserController)
```

Gera:

```text
GET    /users
POST   /users
GET    /users/:id
PUT    /users/:id
PATCH  /users/:id
DELETE /users/:id
```

---

## 15. Paginação

```text
GET /products?page=1&limit=50
```

Resposta:

```json
{
    "data": [],
    "pagination": {
        "page": 1,
        "limit": 50,
        "total": 100,
        "pages": 2
    }
}
```

Cursor:

```text
GET /products?cursor=abc123
```

---

## 16. Filtering, Sorting e Search

```text
GET /products?status=active
GET /products?price[gte]=100
GET /products?sort=-price
GET /products?search=iphone
GET /products?fields=id,name,price
```

---

## 17. CORS

```js
app.use(cors({
    origin: "https://example.com",
    methods: ["GET", "POST", "PUT", "DELETE"],
    credentials: true
}))
```

---

## 18. Segurança HTTP

Proteções:

```text
XSS
CSRF
SQL Injection
NoSQL Injection
Command Injection
Path Traversal
HTTP Parameter Pollution
Request Smuggling
Header Injection
Host Header Injection
Open Redirect
Prototype Pollution
Mass Assignment
Brute Force
DoS
SSRF
```

---

## 19. Security Headers

Suporte a:

```text
Content-Security-Policy
Strict-Transport-Security
X-Content-Type-Options
X-Frame-Options
Referrer-Policy
Permissions-Policy
Cross-Origin-Opener-Policy
Cross-Origin-Resource-Policy
Cross-Origin-Embedder-Policy
```

```js
app.use(helmet())
```

---

## 20. Rate Limiting

```js
app.use(rateLimit({
    window: "1m",
    max: 100
}))
```

Resposta:

```http
429 Too Many Requests
```

---

## 21. CSRF

```js
app.use(csrf())
```

Suporte a:

- Synchronizer Token
- Double Submit Cookie
- SameSite Cookies
- Origin Validation
- Referer Validation

---

## 22. Validação

```js
app.post(
    "/users",
    validate({
        name: string().min(3),
        email: email(),
        age: number().min(18)
    }),
    createUser
)
```

Schema:

```js
const UserSchema = schema({
    name: string().required(),
    email: string().email().required(),
    age: number().integer().min(18)
})
```

---

## 23. Sanitização

```js
sanitize(req.body)
```

Deve ajudar a proteger contra:

```text
XSS
HTML Injection
SQL Injection
NoSQL Injection
Command Injection
Path Traversal
```

---

## 24. Tratamento de erros

```js
throw new HttpError(404, "User not found")
```

Middleware:

```js
app.use((err, req, res, next) => {
    res.status(500).json({
        error: {
            message: "Internal Server Error"
        }
    })
})
```

Em produção, stack traces não devem ser expostos ao cliente.

---

## 25. Resposta de erro padronizada

```json
{
    "success": false,
    "error": {
        "status": 404,
        "code": "USER_NOT_FOUND",
        "message": "User not found",
        "requestId": "abc123"
    }
}
```

---

## 26. Logging

```js
app.use(logger())
```

Registrar:

```text
timestamp
method
url
status
duration
ip
user-agent
request-id
```

Exemplo:

```text
2026-09-09T22:00:00Z GET /users 200 15ms
```

---

## 27. Request ID

```http
X-Request-ID: abc123
```

```js
req.id
```

---

## 28. Static Files

```js
app.static("./public")
```

Estrutura:

```text
public/
├── index.html
├── style.css
└── app.js
```

---

## 29. Templates

Suporte opcional a:

```text
HTML
EJS
Handlebars
Pug
Mustache
```

```js
res.render("home", {
    title: "Home"
})
```

---

## 30. Upload de arquivos

```js
app.post("/upload", upload(), (req, res) => {
    const file = req.files.avatar
})
```

Recursos:

```text
multipart/form-data
multiple files
streaming upload
size limits
MIME validation
extension validation
filename sanitization
magic bytes validation
```

---

## 31. Download

```js
res.download("./files/report.pdf")
```

---

## 32. Streaming

```js
app.get("/video", (req, res) => {
    res.stream(file)
})
```

Suporte a:

```text
Range Requests
Partial Content
206
Backpressure
Abort
```

---

## 33. Server-Sent Events

```js
app.sse("/events", (client) => {
    client.send({
        event: "message",
        data: "Hello"
    })
})
```

---

## 34. WebSocket

```js
app.ws("/chat", (socket) => {
    socket.on("message", message => {
        socket.send(message)
    })
})
```

Segurança:

```text
Origin validation
Authentication
Authorization
Rate limiting
Message size limits
Connection limits
Timeouts
Heartbeat
```

---

## 35. Cache

```js
app.use(cache({
    maxAge: "5m"
}))
```

Suporte a:

```text
Cache-Control
ETag
Last-Modified
Expires
Vary
If-None-Match
If-Modified-Since
```

---

## 36. Compressão

Suporte a:

```text
gzip
deflate
brotli
```

```js
app.use(compression())
```

---

## 37. Proxy

```js
app.proxy({
    trust: true
})
```

Suporte a:

```text
X-Forwarded-For
X-Forwarded-Proto
X-Forwarded-Host
Forwarded
```

---

## 38. HTTPS / TLS

```js
app.https({
    cert: "./cert.pem",
    key: "./key.pem"
})
```

Suporte a:

```text
TLS 1.2
TLS 1.3
Certificate
Private Key
SNI
ALPN
```

---

## 39. HTTP/2 e HTTP/3

```js
app.http2({
    cert: "./cert.pem",
    key: "./key.pem"
})
```

HTTP/3 pode ser disponibilizado quando suportado pela implementação de transporte.

---

## 40. Limites e timeouts

```js
app.bodyLimit("10mb")

app.timeout({
    request: 30000,
    headers: 10000,
    idle: 60000
})
```

Limitar:

```text
Header size
URL size
Query size
Parameter size
Body size
JSON depth
Array size
File size
Multipart size
```

---

## 41. Health Checks

```js
app.get("/health", (req, res) => {
    res.json({
        status: "ok"
    })
})
```

Endpoints:

```text
/health
/live
/ready
```

Readiness:

```json
{
    "status": "ready",
    "database": "connected",
    "cache": "connected"
}
```

---

## 42. Graceful Shutdown

```js
process.on("SIGTERM", async () => {
    await app.close()
})
```

O servidor deve:

1. Parar novas conexões.
2. Finalizar requisições existentes.
3. Fechar WebSockets.
4. Fechar banco de dados.
5. Fechar cache.
6. Liberar recursos.
7. Encerrar o processo.

---

## 43. Controllers

Arquitetura:

```text
Request
   ↓
Middleware
   ↓
Router
   ↓
Controller
   ↓
Service
   ↓
Repository
   ↓
Database
```

Exemplo:

```js
class UserController {
    async list(req, res) {
        const users = await UserService.list()

        return res.json(users)
    }
}
```

---

## 44. Services

```js
class UserService {
    static async create(data) {
        return UserRepository.create(data)
    }
}
```

---

## 45. Repository

```js
class UserRepository {
    static async findAll() {
        return database.users.findMany()
    }
}
```

---

## 46. Dependency Injection

```js
app.provide("database", database)
app.provide("logger", logger)
```

Uso:

```js
const database = inject("database")
```

---

## 47. Lifecycle

Hooks:

```text
beforeStart
afterStart

beforeRequest
afterRequest

beforeResponse
afterResponse

beforeShutdown
afterShutdown
```

---

## 48. Plugins

```js
app.plugin(cors())
app.plugin(auth())
app.plugin(database())
app.plugin(openapi())
```

Plugins podem registrar:

```text
routes
middleware
services
hooks
configuration
commands
```

---

## 49. Configuração

```js
const config = {
    server: {
        host: "0.0.0.0",
        port: 3000
    },

    security: {
        cors: true,
        csrf: true,
        rateLimit: true
    },

    database: {
        url: env.DATABASE_URL
    }
}
```

---

## 50. Environment e Secrets

Suporte:

```text
.env
.env.local
.env.development
.env.production
```

Secrets:

```text
Environment Variables
Secret Managers
Key Rotation
Encryption
```

Secrets nunca devem ser enviados ao cliente.

---

## 51. Observabilidade

Fornecer:

```text
Logs
Metrics
Tracing
Health Checks
Request IDs
Error Tracking
Performance Monitoring
```

Métricas:

```text
http_requests_total
http_request_duration
http_request_errors
active_connections
memory_usage
cpu_usage
```

Tracing:

```text
Trace ID
Span ID
Parent Span
Context Propagation
```

Compatibilidade recomendada com OpenTelemetry.

---

## 52. Performance

O servidor deve utilizar:

```text
Event Loop
Async I/O
Connection Pooling
Keep-Alive
Streaming
Backpressure
Caching
Compression
Efficient Routing
Minimal Allocations
```

---

## 53. Concorrência

Suporte a:

```text
Concurrent Requests
Async Handlers
Promise
Streams
Workers
Worker Threads
```

---

## 54. Cluster

```js
app.cluster({
    workers: "auto"
})
```

Arquitetura:

```text
             Load Balancer
                   |
       +-----------+-----------+
       |           |           |
    Worker 1    Worker 2    Worker 3
       |           |           |
       +-----------+-----------+
                   |
               Database
```

---

## 55. API Versioning

```text
/api/v1/users
/api/v2/users
```

Ou por media type:

```http
Accept: application/vnd.api.v2+json
```

---

## 56. OpenAPI

```js
app.openapi({
    title: "My API",
    version: "1.0.0"
})
```

Endpoints:

```text
/openapi.json
/docs
```

---

## 57. Contract Validation

Validar:

```text
Request
Headers
Query
Params
Body
Response
```

Exemplo:

```js
route.get("/users", {
    response: array(UserSchema)
})
```

---

## 58. Webhooks

```js
app.post("/webhooks/payment", webhook({
    signature: env.WEBHOOK_SECRET
}))
```

Recursos:

```text
Signature Validation
Replay Protection
Idempotency
Retries
Timeout
Raw Body
```

---

## 59. Idempotency

```http
Idempotency-Key: abc123
```

Exemplo:

```text
POST /payments
```

A mesma chave não deve executar uma operação não idempotente duas vezes.

---

## 60. Background Jobs

```js
queue.process("email", async job => {
    await sendEmail(job.data)
})
```

---

## 61. Scheduled Jobs

```js
schedule("0 * * * *", async () => {
    await cleanup()
})
```

---

## 62. Event System

```js
app.on("user.created", user => {
    console.log(user)
})

app.emit("user.created", user)
```

---

## 63. API Gateway

```text
Client
  ↓
API Gateway
  ↓
Authentication
  ↓
Rate Limit
  ↓
Router
  ↓
Microservice
```

---

## 64. Reverse Proxy

```js
proxy("/api", {
    target: "http://localhost:4000"
})
```

---

## 65. Load Balancing

Estratégias:

```text
Round Robin
Least Connections
Weighted
Random
```

---

## 66. Microservices

Transportes:

```text
HTTP
HTTPS
WebSocket
TCP
Message Queue
Events
```

---

## 67. RPC

```js
rpc("users.get", {
    id: 10
})
```

---

## 68. GraphQL

Opcional:

```js
app.graphql("/graphql", schema)
```

---

## 69. Arquitetura modular

```text
src/
├── controllers/
├── services/
├── repositories/
├── models/
├── schemas/
├── middleware/
├── routes/
├── modules/
├── plugins/
├── config/
├── utils/
└── main.js
```

Ou por domínio:

```text
User/
├── controller
├── service
├── repository
├── schema
├── routes
└── tests
```

---

## 70. CLI

```bash
framework create app
framework dev
framework start
framework build
framework test
framework routes
framework doctor
framework security
framework audit
```

Geradores:

```bash
framework generate controller User
framework generate service User
framework generate middleware Auth
framework generate resource User
```

---

## 71. Testes

Suporte a:

```text
Unit Tests
Integration Tests
HTTP Tests
End-to-End Tests
Security Tests
Load Tests
```

Exemplo:

```js
test("GET /users", async () => {
    const response = await request(app)
        .get("/users")

    expect(response.status).toBe(200)
})
```

---

## 72. Mock

```js
mock("database", fakeDatabase)
```

---

## 73. Test Server

```js
const server = app.test()

await server.get("/users")
```

---

## 74. Segurança de senhas

Nunca armazenar senhas em texto puro.

Suporte recomendado:

```text
Argon2id
bcrypt
scrypt
PBKDF2
```

---

## 75. Audit Log

Registrar eventos:

```text
LOGIN
LOGOUT
LOGIN_FAILED
PASSWORD_CHANGED
USER_CREATED
USER_UPDATED
USER_DELETED
PERMISSION_CHANGED
API_KEY_CREATED
API_KEY_REVOKED
```

---

## 76. SSRF Protection

Para requisições externas:

```text
Bloquear localhost
Bloquear redes privadas
Bloquear endpoints de metadata
Validar redirects
Restringir protocolos
```

---

## 77. Segurança de arquivos

Validar:

```text
File Size
MIME Type
Extension
Filename
Magic Bytes
Path Traversal
Executable Files
Archive Bombs
```

Nunca confiar somente na extensão.

---

## 78. Segurança por padrão

Princípios:

```text
Secure by Default
Fail Closed
Least Privilege
Defense in Depth
Input Validation
Output Encoding
Secret Protection
Secure Headers
Safe Error Handling
```

---

## 79. Produção

```js
app.production()
```

Deve:

```text
desativar debug
ocultar stack traces
ativar security headers
ativar compression
ativar request limits
ativar logging
ativar graceful shutdown
ativar health checks
```

---

## 80. Desenvolvimento

```js
app.development()
```

Recursos:

```text
Hot Reload
Detailed Errors
Debug Logs
Source Maps
Development Server
```

---

## 81. Pipeline completo

```text
                    REQUEST
                       │
                       ▼
                ┌─────────────┐
                │ HTTP Server │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │   Security  │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │ Rate Limit  │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │ Middleware  │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │   Router    │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │ Validation  │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │ Controller  │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │   Service   │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │ Repository  │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │  Database   │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │  Response   │
                └──────┬──────┘
                       │
                       ▼
                    CLIENT
```

---

## 82. Exemplo completo

```js
import {
    server,
    Router,
    json,
    cors,
    helmet,
    rateLimit,
    auth,
    role,
    validate
} from "web"

const app = server()

app.use(helmet())
app.use(cors())
app.use(json())

app.use(rateLimit({
    window: "1m",
    max: 100
}))

const users = Router()

users.get("/", async (req, res) => {
    const data = await UserService.list()

    return res.json({
        success: true,
        data
    })
})

users.post(
    "/",
    auth(),
    validate({
        name: string().required(),
        email: email().required()
    }),
    async (req, res) => {

        const user = await UserService.create(req.body)

        return res.status(201).json({
            success: true,
            data: user
        })
    }
)

users.get("/:id", async (req, res) => {
    const user = await UserService.find(req.params.id)

    if (!user) {
        return res.notFound("User not found")
    }

    return res.json({
        success: true,
        data: user
    })
})

users.delete(
    "/:id",
    auth(),
    role("admin"),
    async (req, res) => {

        await UserService.delete(req.params.id)

        return res.status(204).end()
    }
)

app.use("/api/v1/users", users)

app.get("/health", (req, res) => {
    res.json({
        status: "ok"
    })
})

app.listen(3000, () => {
    console.log("Server running on http://localhost:3000")
})
```

---

# 83. API principal

## Application

```text
app.use()
app.get()
app.post()
app.put()
app.patch()
app.delete()
app.head()
app.options()

app.listen()
app.close()

app.static()
app.plugin()
app.middleware()

app.ws()
app.sse()

app.openapi()

app.health()
app.ready()

app.config()
app.provide()
app.inject()

app.on()
app.emit()

app.production()
app.development()
app.cluster()
app.https()
app.http2()
```

## Router

```text
router.use()
router.get()
router.post()
router.put()
router.patch()
router.delete()
router.head()
router.options()

router.resource()
router.group()
router.param()
```

## Request

```text
req.method
req.url
req.originalUrl
req.path
req.params
req.query
req.headers
req.body
req.cookies
req.files

req.ip
req.ips
req.protocol
req.hostname
req.host

req.user
req.session
req.id

req.is()
req.accepts()
req.get()

req.abort()
req.signal
```

## Response

```text
res.status()
res.send()
res.json()
res.text()
res.html()

res.redirect()

res.header()
res.setHeader()
res.getHeader()

res.cookie()
res.clearCookie()

res.type()

res.file()
res.download()
res.stream()

res.etag()
res.cache()

res.end()
```

---

# 84. Objetivo

O servidor deve ser:

```text
Rápido
Seguro
Modular
Extensível
Tipável
Testável
Observável
Escalável
Compatível com REST
Compatível com APIs modernas
Adequado para produção
```

A API básica deve continuar simples:

```js
const app = server()

app.get("/", (req, res) => {
    res.send("Hello World")
})

app.listen(3000)
```

Mas a mesma base deve permitir:

```text
Enterprise
Microservices
REST API
Real-time Applications
Distributed Systems
Cloud Applications
```

sem obrigar o desenvolvedor a utilizar todos os recursos.
