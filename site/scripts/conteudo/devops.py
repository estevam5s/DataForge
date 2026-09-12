# -*- coding: utf-8 -*-
"""DevOps — os artefatos que levam o projeto ao ar.

A rota `/docs/devops` era um link **quebrado**: a página de
microserviços apontava para ela e ela não existia. O comando existe há
tempo, com 11 subcomandos e 65 testes, e não tinha uma linha no site.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops",
"title": "DevOps",
"description": "Dockerfile, compose, CI, Kubernetes, Helm, Terraform, nginx, Prometheus e SBOM — gerados do que o projeto realmente usa, e não de um modelo.",
"blocos": [
 {"p": "`dataforge devops` gera os arquivos que põem um projeto no ar — e **sai da frente**. Não há `deploy` que fale com Docker e Kubernetes por dentro: no dia em que alguém precisa mudar uma camada, tem de haver onde mexer."},
 {"code": """dataforge devops              # tudo o que faz sentido para este projeto
dataforge devops doctor       # o que falta para subir
dataforge devops --seco       # mostra o que faria, sem escrever""", "lang": "bash"},

 {"h2": "Os onze subcomandos"},
 {"table": {"head": ["Comando", "Gera"], "rows": [
   ["`devops init`", "tudo o que faz sentido para este projeto (o padrão)"],
   ["`devops docker`", "`Dockerfile`, `.dockerignore`, `docker-compose.yml`"],
   ["`devops ci github`", "`.github/workflows/ci.yml`"],
   ["`devops k8s`", "`deployment`, `service`, `ingress`, `configmap`, `hpa`"],
   ["`devops helm`", "um chart com `values.yaml`"],
   ["`devops terraform`", "o esqueleto"],
   ["`devops nginx`", "proxy reverso com TLS, WebSocket e SSE"],
   ["`devops observar`", "Prometheus, Grafana e OpenTelemetry"],
   ["`devops sbom`", "o inventário, em CycloneDX"],
   ["`devops secrets`", "`.env.example` e o `.gitignore`"],
   ["`devops doctor`", "o que falta para este projeto subir"]]}},

 {"h2": "Os artefatos saem do que o projeto ADOTA"},
 {"p": "Não é um modelo com buracos para preencher. O gerador lê o `forge.toml` e varre os `.df` procurando o que o código realmente usa:"},
 {"code": """$ dataforge devops --seco

  ◆ loja 2.1.0  (Kiln, banco)

  + .dockerignore              43 linha(s)
  + .env.example               15 linha(s)
  + .github/workflows/ci.yml   75 linha(s)
  + Dockerfile                 40 linha(s)
  + deploy/nginx.conf          67 linha(s)
  + docker-compose.yml         41 linha(s)
  + k8s/configmap.yml          13 linha(s)
  + k8s/deployment.yml         89 linha(s)
  + k8s/hpa.yml                30 linha(s)
  + k8s/ingress.yml            31 linha(s)
  + k8s/service.yml            16 linha(s)""", "lang": "bash"},
 {"p": "O `(Kiln, banco)` ali é o que ele detectou — e é o que decide o resultado. **Quem não usa banco não ganha um Postgres no compose**; quem não usa Kiln não ganha `EXPOSE` nem sonda de saúde."},

 {"callout": {"tipo": "nota", "titulo": "Arquivo que já existe é pulado, não sobrescrito", "texto": "Rodar de novo é seguro. O que você editou à mão fica, e a saída diz o que preservou. `--forcar` sobrescreve, e guarda o anterior em `.anterior` antes — um Dockerfile ajustado ao longo de meses não pode ser perdido por um comando distraído."}},

 {"h2": "O que o Dockerfile carrega, e por quê"},
 {"p": "O que ele gera não é esboço: é o que se poria em produção. Cinco decisões, e o problema de cada uma:"},
 {"table": {"head": ["No artefato", "Sem ele"], "rows": [
   ["`USER forge`", "um escape de container vira **root no host**"],
   ["o manifesto copiado antes do código", "um commit numa linha reinstala tudo — o build vai de 8 s para 2 min"],
   ["`.env` no `.dockerignore`", "o segredo fica na camada, e `docker history` o mostra — **mesmo apagado numa camada seguinte**"],
   ["`resources` + as duas sondas no Deployment", "um pod come o nó inteiro; e o Service manda tráfego antes da hora"],
   ["`depends_on: service_healthy`", "a aplicação falha na primeira consulta, de forma intermitente"]]}},

 {"code": """# A sonda usa o proprio Python: 'curl' nao esta na imagem
# slim, e instalar 30 MB para uma sonda de 200 bytes seria
# trocar tamanho por conveniencia.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \\
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/saude', timeout=2).status == 200 else 1)\"""", "lang": "bash"},

 {"h2": "`doctor` — e ele funciona num projeto que não compila"},
 {"code": """$ dataforge devops doctor

  ◆ loja 2.1.0  (Kiln, banco)

  ✓ há um forge.toml
  ✓ a entrada existe (src/main.df)
  ✓ o código passa no 'check'
  ✗ há Dockerfile
  ✗ há .dockerignore
  ✓ nenhum segredo versionado
  ! não há .env.example    cada pessoa nova descobre as variáveis por tentativa
  ✗ há pipeline de CI
  ✗ há testes

  Para produção:
    · há um proxy reverso na frente (TLS, compressão, HTTP/2)
    · a sessão vive na memória do processo: UM processo por aplicação
    · 'Kiln.secure_headers()' como middleware de saída

  4 coisa(s) a resolver:
    1. gere com 'dataforge devops docker'
    2. sem ele, o '.env' entra na imagem — e continua nela depois de
       apagado numa camada seguinte
    3. gere com 'dataforge devops ci github'""", "lang": "bash"},
 {"p": "Cada linha vermelha vem com **o comando que a resolve**. Um diagnóstico que diz \"falta X\" e não diz como obter X transfere o trabalho de volta."},
 {"callout": {"tipo": "dica", "titulo": "Ele lê o código por varredura de texto, e não pelo parser", "texto": "É deliberado: o `doctor` precisa funcionar num projeto que **não compila** — e é aí que ele é mais útil. Um diagnóstico que exige o código compilando não serve para quem está tentando descobrir por que nada sobe."}},

 {"h3": "Segredo versionado: a conferência é no git"},
 {"p": "Não no disco. Um `.env` que existe e está no `.gitignore` é normal; um `.env` que o `git` **rastreia** já vazou — e apagá-lo agora não o tira do histórico."},

 {"h2": "`--host=0.0.0.0` é obrigatório dentro de um container"},
 {"p": "Vale para o `ignite` do Kiln (`at \"0.0.0.0\"`) e para a Vitrine (`--host=0.0.0.0`). O padrão é `127.0.0.1`, que **de dentro do container significa o próprio container**."},
 {"p": "O sintoma é enganoso: o log diz \"no ar\", a porta está publicada, e o `curl` de fora não recebe nada. Os artefatos gerados já trazem a forma certa."},
 {"code": """// 'at "0.0.0.0"' e obrigatorio dentro de um container.
ignite loja on 8080 at "0.0.0.0\"""", "lang": "df"},

 {"h2": "Kubernetes: o que os manifestos trazem"},
 {"code": """spec:
  replicas: 3
  # 'maxUnavailable: 0' faz a atualizacao nao derrubar capacidade: o
  # pod novo entra em servico antes de o velho sair.
  strategy:
    rollingUpdate:
      maxUnavailable: 0
  …
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000""", "lang": "yaml"},
 {"p": "Mais `resources` (requests e limits), `readinessProbe`, `livenessProbe`, e um `hpa` que escala por CPU. O `ingress` usa o domínio que você passar em `--dominio=`."},

 {"h2": "O YAML é escrito à mão"},
 {"callout": {"tipo": "atencao", "titulo": "`yes`, `no` e `null` vão entre aspas", "texto": "Em **YAML 1.1** eles são booleanos. Um valor `no` sem aspas — o código de um país, a resposta de um campo — muda de tipo sozinho, e o manifesto aplica algo diferente do que está escrito. O gerador cita esses três sempre, e há teste para isso."}},
 {"p": "Escrever o YAML à mão, em vez de depender de uma biblioteca, é a mesma política de zero dependências do resto da linguagem — e aqui ela cobra o preço de conhecer essas armadilhas em vez de herdá-las resolvidas."},

 {"h2": "Duas metades separadas de propósito"},
 {"table": {"head": ["Arquivo", "Faz"], "rows": [
   ["`dataforge/devops.py`", "produz **texto**"],
   ["`dataforge/devops_cli.py`", "escreve **arquivo**"]]}},
 {"p": "A separação deixa os geradores testáveis sem tocar em disco — os 65 testes validam o compose com `docker compose config`, conferem os manifestos como dado e **executam a sonda do HEALTHCHECK** — e põe a política de \"o que fazer quando o arquivo já existe\" num lugar só."},

 {"h2": "O que ele não é"},
 {"p": "Não é um orquestrador. Não sobe nada, não fala com nenhuma nuvem, não guarda estado. Um `deploy` mágico esconderia o que a imagem é, e a primeira vez que algo desse errado em produção não haveria onde olhar."},
 {"p": "O que ele é: a diferença entre saber que você precisa de um `readinessProbe` e ter um."},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/instalacao/docker", "title": "A imagem oficial", "desc": "Rodar DataForge em container, sem instalar nada."},
   {"href": "/docs/tecnicas/observar", "title": "Observabilidade", "desc": "Métrica, traço e linhagem — o que o 'devops observar' instrumenta."},
   {"href": "/docs/tecnicas/microservicos", "title": "Microserviços", "desc": "O que muda quando a chamada atravessa a rede."},
   {"href": "/docs/seguranca", "title": "Segurança", "desc": "Cabeçalhos, CSRF, limite de taxa e o que não vai ao repositório."}]},
]},
]
