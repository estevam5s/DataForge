# Dataforge Stream & DevOps

Framework oficial da Dataforge para construção, execução, testes, empacotamento,
implantação e monitoramento de aplicações web, dashboards, Data Apps, APIs e
sistemas de dados.

---

## 1. Visão geral

O Dataforge Stream deverá permitir construir:

- aplicações web
- dashboards
- Data Apps
- APIs REST
- APIs WebSocket
- aplicações de dados
- Machine Learning
- Big Data
- ferramentas administrativas
- sistemas internos
- monitoramento
- pipelines de dados

O ecossistema também deverá integrar:

- Docker
- Docker Compose
- Git
- GitHub
- GitLab
- CI/CD
- GitHub Actions
- Kubernetes
- Helm
- Terraform
- Ansible
- Nginx
- PostgreSQL
- Redis
- RabbitMQ
- Kafka
- Prometheus
- Grafana
- OpenTelemetry
- AWS
- Azure
- Google Cloud
- Linux
- Windows
- macOS

---

# 2. Filosofia

A cadeia de desenvolvimento deverá seguir:

```text
Código
  ↓
Dataforge Compiler
  ↓
Format
  ↓
Lint
  ↓
Testes
  ↓
Build
  ↓
Docker
  ↓
CI/CD
  ↓
Container Registry
  ↓
Deploy
  ↓
Kubernetes / Cloud
  ↓
Monitoramento
  ↓
Logs + Metrics + Traces
```

---

# 3. Estrutura do projeto

```text
my-app/
│
├── src/
│   ├── main.df
│   ├── app.df
│   ├── api/
│   ├── pages/
│   ├── components/
│   └── services/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── assets/
├── config/
├── scripts/
├── migrations/
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── dataforge.toml
├── dataforge.lock
└── .github/
    └── workflows/
        ├── ci.yml
        ├── cd.yml
        └── release.yml
```

---

# 4. CLI

A CLI deverá centralizar o desenvolvimento e o DevOps.

```bash
dataforge create
dataforge init
dataforge run
dataforge dev
dataforge build
dataforge test
dataforge lint
dataforge format
dataforge check
dataforge package
dataforge publish
dataforge deploy
dataforge doctor
```

---

# 5. Desenvolvimento

```bash
dataforge run
dataforge dev
dataforge dev --reload
dataforge dev --debug
```

O modo `dev` deverá oferecer:

- hot reload
- logs detalhados
- diagnóstico de erros
- recompilação automática
- atualização da aplicação

---

# 6. Gerenciamento de dependências

```bash
dataforge add stream
dataforge add database
dataforge add postgres
dataforge add redis

dataforge remove redis

dataforge update

dataforge install

dataforge list
```

O projeto deverá possuir:

```text
dataforge.toml
dataforge.lock
```

O lockfile deverá permitir builds reproduzíveis.

---

# 7. Configuração

Exemplo de `dataforge.toml`:

```toml
[project]
name = "analytics"
version = "1.0.0"
entry = "src/main.df"

[server]
host = "0.0.0.0"
port = 8501

[development]
reload = true
debug = true

[production]
workers = 4

[security]
csrf = true
secure_headers = true

[logging]
level = "info"
```

---

# 8. Variáveis de ambiente

`.env`:

```env
APP_ENV=production
APP_PORT=8501
DATABASE_URL=postgresql://user:password@db/app
REDIS_URL=redis://redis:6379
SECRET_KEY=change-me
```

Na aplicação:

```text
database_url = env.get("DATABASE_URL")
redis_url = env.get("REDIS_URL")
```

Secrets nunca deverão ser armazenados diretamente no código-fonte.

---

# 9. Docker

A CLI poderá gerar um Dockerfile:

```bash
dataforge docker init
```

Exemplo:

```dockerfile
FROM dataforge/runtime:latest

WORKDIR /app

COPY . .

RUN dataforge install
RUN dataforge build

EXPOSE 8501

CMD ["dataforge", "run", "--production"]
```

Build:

```bash
dataforge docker build --tag my-app:1.0.0
```

Execução:

```bash
dataforge docker run
```

Ou diretamente:

```bash
docker build -t my-app:1.0.0 .
docker run -p 8501:8501 my-app:1.0.0
```

---

# 10. Docker Compose

O Compose deverá permitir criar ambientes completos.

```yaml
services:

  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      DATABASE_URL: postgresql://postgres:password@db/app
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7

volumes:
  postgres_data:
```

Comandos:

```bash
dataforge compose init
dataforge compose up
dataforge compose down
dataforge compose logs
dataforge compose restart
```

---

# 11. Stack de desenvolvimento

Um comando poderá iniciar toda a infraestrutura:

```bash
dataforge dev stack
```

Exemplo:

```text
Dataforge Application
        │
        ├── PostgreSQL
        ├── Redis
        ├── Kafka
        ├── RabbitMQ
        ├── Prometheus
        └── Grafana
```

---

# 12. Git

A Dataforge deverá funcionar nativamente com Git.

```bash
dataforge git init
dataforge git status
dataforge git commit
dataforge git branch
dataforge git log
```

Também deverá ser possível utilizar diretamente:

```bash
git init
git add .
git commit -m "Initial commit"
git push
```

---

# 13. GitHub

A CLI poderá auxiliar na criação e configuração de repositórios:

```bash
dataforge github init
```

Funcionalidades possíveis:

- criar repositório
- configurar branches
- configurar Actions
- criar releases
- publicar pacotes
- configurar secrets
- configurar environments

---

# 14. GitHub Actions

Gerar pipeline:

```bash
dataforge ci init github
```

Arquivo:

```text
.github/workflows/ci.yml
```

Exemplo:

```yaml
name: Dataforge CI

on:
  push:
  pull_request:

jobs:

  test:

    runs-on: ubuntu-latest

    steps:

      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Dataforge
        uses: dataforge/setup-dataforge@v1

      - name: Install
        run: dataforge install

      - name: Format
        run: dataforge format --check

      - name: Lint
        run: dataforge lint

      - name: Type Check
        run: dataforge check

      - name: Test
        run: dataforge test

      - name: Build
        run: dataforge build
```

---

# 15. CI

Pipeline padrão:

```text
Push
 ↓
Checkout
 ↓
Install Dependencies
 ↓
Format Check
 ↓
Lint
 ↓
Type Check
 ↓
Unit Tests
 ↓
Integration Tests
 ↓
Security Scan
 ↓
Build
 ↓
Docker Build
 ↓
Container Scan
```

---

# 16. CD

Pipeline:

```text
Build
 ↓
Docker Image
 ↓
Container Registry
 ↓
Staging
 ↓
Integration Tests
 ↓
Production
```

---

# 17. CI/CD completo

```text
Developer
    ↓
Git Push
    ↓
GitHub
    ↓
GitHub Actions
    ↓
+---------------------+
| Format              |
| Lint                |
| Type Check          |
| Unit Test           |
| Integration Test    |
| Security Scan       |
+---------------------+
    ↓
Dataforge Build
    ↓
Docker Build
    ↓
Container Security
    ↓
Container Registry
    ↓
Staging
    ↓
Smoke Tests
    ↓
Production
```

---

# 18. Container Registry

Integrações:

- Docker Hub
- GitHub Container Registry
- GitLab Container Registry
- Amazon ECR
- Google Artifact Registry
- Azure Container Registry

Comandos:

```bash
dataforge registry login
dataforge registry push
dataforge registry pull
```

---

# 19. Versionamento

Utilizar Semantic Versioning:

```text
MAJOR.MINOR.PATCH
```

Exemplos:

```text
1.0.0
1.1.0
1.1.1
2.0.0
```

Release:

```bash
dataforge release 1.0.0
```

---

# 20. Testes

O ecossistema deverá oferecer:

- Unit Tests
- Integration Tests
- End-to-End Tests
- API Tests
- Component Tests
- Performance Tests
- Security Tests

Comandos:

```bash
dataforge test
dataforge test unit
dataforge test integration
dataforge test e2e
```

---

# 21. Linter

```bash
dataforge lint
```

Deverá detectar:

- variáveis não utilizadas
- imports não utilizados
- erros de tipos
- código inacessível
- más práticas
- problemas de segurança
- complexidade excessiva
- APIs obsoletas

---

# 22. Formatter

```bash
dataforge format
```

Verificação:

```bash
dataforge format --check
```

---

# 23. Type Checking

```bash
dataforge check
```

O sistema deverá validar os tipos durante o desenvolvimento e CI.

Exemplo:

```text
String
Int
Float
Bool
List<T>
Map<K,V>
DataFrame
Future<T>
Result<T,E>
```

---

# 24. Segurança

Comando:

```bash
dataforge security scan
```

Categorias:

```text
Dependency Security
SAST
Secret Detection
Container Security
Configuration Security
SBOM
```

---

# 25. SAST

```bash
dataforge security sast
```

Detectar:

- SQL Injection
- Command Injection
- Path Traversal
- XSS
- unsafe deserialization
- hardcoded secrets
- criptografia fraca

---

# 26. Secrets

```bash
dataforge secrets scan
```

Detectar:

- API Keys
- tokens
- passwords
- private keys
- cloud credentials
- JWT secrets

---

# 27. Dependências

```bash
dataforge security dependencies
```

O sistema deverá verificar vulnerabilidades conhecidas nas dependências.

---

# 28. SBOM

```bash
dataforge security sbom
```

Formatos:

```text
CycloneDX
SPDX
```

---

# 29. Container Security

```bash
dataforge docker scan
```

Verificações:

- vulnerabilidades da imagem
- pacotes vulneráveis
- secrets
- permissões
- usuário root
- configurações inseguras
- imagem base

---

# 30. Kubernetes

Inicializar:

```bash
dataforge kubernetes init
```

Estrutura:

```text
k8s/
├── deployment.yml
├── service.yml
├── ingress.yml
├── configmap.yml
└── secret.yml
```

Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: dataforge-app

spec:
  replicas: 3

  selector:
    matchLabels:
      app: dataforge

  template:
    metadata:
      labels:
        app: dataforge

    spec:
      containers:

        - name: app
          image: registry.example.com/dataforge-app:1.0.0

          ports:
            - containerPort: 8501
```

---

# 31. Kubernetes Service

```yaml
apiVersion: v1
kind: Service

metadata:
  name: dataforge-service

spec:
  selector:
    app: dataforge

  ports:
    - port: 80
      targetPort: 8501
```

---

# 32. Helm

Inicialização:

```bash
dataforge helm init
```

Estrutura:

```text
helm/
└── dataforge-app/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── deployment.yaml
        ├── service.yaml
        └── ingress.yaml
```

Deploy:

```bash
helm install dataforge-app ./helm/dataforge-app
```

---

# 33. Terraform

Estrutura:

```text
infrastructure/
├── main.tf
├── variables.tf
├── outputs.tf
└── providers.tf
```

Comandos:

```bash
dataforge infra init
dataforge infra plan
dataforge infra apply
dataforge infra destroy
```

---

# 34. Ansible

Estrutura:

```text
ansible/
├── inventory
├── playbook.yml
└── roles/
```

Uso:

```bash
ansible-playbook playbook.yml
```

---

# 35. Nginx

Arquitetura:

```text
Internet
    ↓
Nginx
    ↓
Dataforge Stream
    ↓
PostgreSQL
    ↓
Redis
```

Funções:

- reverse proxy
- TLS termination
- load balancing
- arquivos estáticos
- compressão
- rate limiting

---

# 36. HTTPS

Produção deverá utilizar:

- HTTPS
- TLS moderno
- secure cookies
- HSTS
- security headers

Integrações possíveis:

- Let's Encrypt
- cert-manager
- Cloudflare
- AWS Certificate Manager

---

# 37. PostgreSQL

```text
db = database.connect(
    env.get("DATABASE_URL")
)
```

Consulta:

```text
users = db.query("""
    SELECT id, name, email
    FROM users
""")
```

---

# 38. Redis

```text
redis = cache.redis(
    env.get("REDIS_URL")
)
```

Utilizações:

- cache
- sessões
- filas
- rate limiting
- locks distribuídos

---

# 39. RabbitMQ

```text
queue.publish(
    "data.processing",
    payload
)
```

Worker:

```text
queue.consume(
    "data.processing",
    process
)
```

---

# 40. Kafka

```text
kafka.subscribe("events")

for event in kafka.events():

    process(event)
```

Casos de uso:

- streaming
- eventos
- telemetria
- IoT
- Big Data
- processamento distribuído

---

# 41. Background Tasks

```text
@task
function process_dataset(data):

    return process(data)
```

Executar:

```text
task.dispatch(
    process_dataset,
    data
)
```

---

# 42. Cron Jobs

```text
@schedule("0 * * * *")
function update_data():

    process_data()
```

---

# 43. Cloud

Integrações planejadas:

```text
AWS
Azure
Google Cloud
DigitalOcean
Cloudflare
```

---

# 44. AWS

Possíveis integrações:

```text
EC2
ECS
EKS
Lambda
S3
RDS
ElastiCache
CloudWatch
ECR
```

---

# 45. Azure

Possíveis integrações:

```text
Azure Container Apps
AKS
Azure Functions
Blob Storage
Azure Database
ACR
Application Insights
```

---

# 46. Google Cloud

Possíveis integrações:

```text
Cloud Run
GKE
Cloud Functions
Cloud Storage
Cloud SQL
Artifact Registry
Cloud Monitoring
```

---

# 47. Storage

API:

```text
storage.put(
    "reports/result.csv",
    data
)
```

Backends:

```text
local
S3
Azure Blob
Google Cloud Storage
MinIO
```

---

# 48. Observabilidade

O runtime deverá possuir:

```text
Logs
Metrics
Traces
Health Checks
Audit Logs
```

---

# 49. Prometheus

Endpoint:

```text
/metrics
```

Exemplo:

```text
stream.metrics.counter(
    "requests_total"
)
```

---

# 50. Grafana

Arquitetura:

```text
Dataforge
    ↓
Prometheus
    ↓
Grafana
```

Monitoramento:

- CPU
- memória
- requests
- latência
- erros
- sessões
- banco
- Redis
- workers
- containers

---

# 51. OpenTelemetry

Suporte a:

- traces
- metrics
- logs

Exemplo:

```text
with telemetry.span("process_data"):

    process_data()
```

---

# 52. Health Checks

Endpoints:

```text
/health
/ready
/live
```

Resposta:

```json
{
    "status": "healthy",
    "database": "healthy",
    "redis": "healthy"
}
```

---

# 53. Logs estruturados

```text
logger.info(
    "User authenticated",
    user_id = user.id
)
```

Formato:

```json
{
    "level": "info",
    "message": "User authenticated",
    "service": "dataforge-app"
}
```

---

# 54. Blue/Green Deployment

```text
Production A
     |
     | deploy
     v
Production B
     |
     | health check
     v
Traffic Switch
```

---

# 55. Canary Deployment

```text
Production
    |
    +---- 95% → Version 1
    |
    +---- 5%  → Version 2
```

Depois:

```text
5%
 ↓
25%
 ↓
50%
 ↓
100%
```

---

# 56. Rollback

```bash
dataforge deploy rollback
```

Kubernetes:

```bash
dataforge kubernetes rollback
```

---

# 57. Zero Downtime

O runtime deverá suportar:

- health checks
- graceful shutdown
- connection draining
- rolling updates
- múltiplos workers
- readiness probes

---

# 58. Graceful Shutdown

```text
SIGTERM
   ↓
Stop accepting requests
   ↓
Finish active requests
   ↓
Close database
   ↓
Close Redis
   ↓
Close workers
   ↓
Shutdown
```

---

# 59. Dataforge Stream + DevOps

O framework web e dashboard deverá funcionar junto com toda a
infraestrutura:

```text
                 Dataforge
                     |
        +------------+------------+
        |            |            |
      Stream       HTTP         Data
        |            |            |
    Dashboard       REST      DataFrame
        |         WebSocket       |
        +------------+------------+
                     |
                   Runtime
                     |
              +------+------+
              |             |
            Docker       Testing
              |             |
            Compose        CI
              |             |
              +------+------+
                     |
                   CD/CD
                     |
                 Registry
                     |
              Kubernetes/Cloud
                     |
        +------------+------------+
        |            |            |
       Logs        Metrics       Traces
        |            |            |
        +------------+------------+
                     |
                  Grafana
```

---

# 60. Ecossistema inspirado no Python

A Dataforge poderá fornecer equivalentes nativos para categorias
importantes do ecossistema Python:

```text
Python Ecosystem
       ↓
Dataforge Ecosystem

Web
 ├── Streamlit
 ├── FastAPI
 ├── Flask
 └── Django
       ↓
Dataforge Stream
Dataforge HTTP
Dataforge Web

Data
 ├── Pandas
 ├── NumPy
 ├── Polars
 └── PyArrow
       ↓
Dataforge Data
Dataforge Array
Dataforge Arrow

Machine Learning
 ├── Scikit-learn
 ├── PyTorch
 ├── TensorFlow
 └── XGBoost
       ↓
Dataforge ML

Async
 ├── asyncio
 └── aiohttp
       ↓
Dataforge Async

Database
 ├── SQLAlchemy
 ├── Psycopg
 ├── Redis
 └── MongoDB
       ↓
Dataforge Database

Testing
 ├── pytest
 └── unittest
       ↓
Dataforge Test

DevOps
 ├── Docker
 ├── Docker Compose
 ├── Kubernetes
 ├── Git
 ├── GitHub Actions
 └── Terraform
       ↓
Dataforge DevOps
```

---

# 61. Ecossistema final

A visão de longo prazo é:

```text
Dataforge
│
├── Language
├── Compiler
├── Runtime
├── Package Manager
│
├── Stream
│   ├── Web
│   ├── Dashboard
│   └── Data Apps
│
├── HTTP
│   ├── REST
│   └── WebSocket
│
├── Data
│   ├── DataFrame
│   ├── SQL
│   ├── Arrow
│   └── Big Data
│
├── ML
│
├── Database
│
├── Testing
│
├── Security
│
├── DevOps
│   ├── Docker
│   ├── Docker Compose
│   ├── Git
│   ├── GitHub
│   ├── CI/CD
│   ├── Kubernetes
│   ├── Helm
│   ├── Terraform
│   └── Ansible
│
├── Observability
│   ├── Prometheus
│   ├── Grafana
│   └── OpenTelemetry
│
└── Cloud
    ├── AWS
    ├── Azure
    └── GCP
```

---

# 62. Objetivo

O objetivo não é transformar a Dataforge em uma cópia do Python.

O objetivo é construir um ecossistema no qual uma única linguagem
possa participar de todo o ciclo de desenvolvimento:

```text
Programar
   ↓
Testar
   ↓
Analisar
   ↓
Construir
   ↓
Empacotar
   ↓
Containerizar
   ↓
Integrar
   ↓
Publicar
   ↓
Implantar
   ↓
Monitorar
   ↓
Escalar
```

A Dataforge deverá, portanto, oferecer uma experiência integrada para:

```text
Development
Data Engineering
Web Development
Backend
Dashboards
Machine Learning
Big Data
Testing
Security
DevOps
Cloud
Observability
```

---

# 63. Princípios do ecossistema

O ecossistema deverá seguir:

```text
Simple
Type-safe
Reactive
Secure
Performant
Extensible
Testable
Observable
Cloud-ready
Container-ready
Developer-friendly
Production-ready
```

A proposta final é que o desenvolvedor consiga iniciar com:

```bash
dataforge create analytics
```

desenvolver a aplicação:

```bash
dataforge dev
```

testar:

```bash
dataforge test
```

validar:

```bash
dataforge lint
dataforge check
dataforge security scan
```

criar a imagem:

```bash
dataforge docker build
```

publicar:

```bash
dataforge registry push
```

e implantar:

```bash
dataforge deploy
```

sem precisar abandonar o ecossistema da Dataforge durante o ciclo
de desenvolvimento.
