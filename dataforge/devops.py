# -*- coding: utf-8 -*-
"""'dataforge devops' — os artefatos que levam um projeto ao ar.

Por que geradores, e nao um orquestrador
----------------------------------------
A tentacao aqui e escrever um 'dataforge deploy' que fala com Docker,
Kubernetes e nuvem. Seria errado por tres motivos.

**O artefato e o contrato.** Um Dockerfile no repositorio e lido,
revisado, versionado e alterado por quem opera. Um 'deploy' que monta a
imagem por dentro esconde o que ela e — e no dia em que alguem precisa
mudar uma camada, nao ha onde mexer.

**O ecossistema ja existe e e melhor.** 'docker build', 'kubectl apply',
'helm upgrade' e 'terraform plan' sao ferramentas maduras, com
documentacao, com gente que as conhece. Reimplementa-las daria um
subconjunto pior, e amarraria a linguagem a versao de cada uma.

**Zero dependencia e uma regra.** Um cliente de Kubernetes exigiria
bibliotecas; um YAML de Deployment nao exige nada.

Entao o que este modulo faz e **gerar o artefato certo, com as decisoes
certas ja tomadas** — e sair da frente. O que ele gera nao e um esboco:
e o que se poria em producao, com usuario sem privilegio, limite de
recurso, sonda de saude, camada de cache aproveitada e segredo fora do
repositorio.

    dataforge devops init            tudo o que faz sentido para o projeto
    dataforge devops docker          Dockerfile, .dockerignore, compose
    dataforge devops ci github       .github/workflows/ci.yml
    dataforge devops k8s             deployment, service, ingress, hpa
    dataforge devops helm            um chart
    dataforge devops terraform       o esqueleto
    dataforge devops nginx           proxy reverso com TLS
    dataforge devops observar        Prometheus, Grafana, OpenTelemetry
    dataforge devops sbom            o inventario, em CycloneDX
    dataforge devops secrets         o que NAO pode ir para o repositorio
    dataforge devops doctor          o que falta para o projeto subir
"""

import json
import os
import re
import time

#: A imagem base. Pinada por MINOR, e nao por patch: patch traz
#: correcao de seguranca e nao quebra nada, e pinar nele obriga a mexer
#: no Dockerfile a cada CVE do Python.
BASE_PYTHON = "python:3.12-slim"

#: A porta padrao de uma aplicacao Vitrine. O Kiln usa 8080.
PORTA_VITRINE = 8501
PORTA_KILN = 8080


# ═══════════════════════════════════════════════════════════
#  O que este projeto e
# ═══════════════════════════════════════════════════════════

class Projeto:
    """O que se sabe do projeto, lido do disco.

    Os geradores mudam de forma conforme isto: um projeto de biblioteca
    nao ganha Dockerfile de servidor, e um que nao usa banco nao ganha
    um PostgreSQL no compose. Gerar tudo para todos daria artefato que
    ninguem le, e artefato que ninguem le e artefato que mente.
    """

    def __init__(self, raiz="."):
        self.raiz = os.path.abspath(raiz)
        self.nome = os.path.basename(self.raiz)
        self.versao = "0.1.0"
        self.entrada = ""
        self.dependencias = []
        self.usa_vitrine = False
        self.usa_kiln = False
        self.usa_banco = False
        self.usa_redis = False
        self.e_biblioteca = False
        self._ler_manifesto()
        self._ler_fontes()

    # ── Leitura ──────────────────────────────────────────────

    def _ler_manifesto(self):
        caminho = os.path.join(self.raiz, "forge.toml")
        if not os.path.isfile(caminho):
            return
        secao = ""
        try:
            with open(caminho, encoding="utf-8") as f:
                for linha in f:
                    limpa = linha.strip()
                    if limpa.startswith("["):
                        secao = limpa.strip("[]").lower()
                        continue
                    if limpa.startswith("#") or "=" not in limpa:
                        continue
                    chave, _, valor = limpa.partition("=")
                    chave = chave.strip()
                    valor = valor.strip().strip('"').strip("'")
                    if secao in ("project", "package"):
                        if chave == "name":
                            self.nome = valor
                        elif chave == "version":
                            self.versao = valor
                        elif chave == "entry":
                            self.entrada = valor
                        self.e_biblioteca = self.e_biblioteca or secao == "package"
                    elif secao == "dependencies":
                        self.dependencias.append((chave, valor))
        except OSError:
            pass

    def _ler_fontes(self):
        """Quais frameworks o codigo adota.

        Le os 'adopt' com uma varredura de texto, e nao com o parser: o
        'devops doctor' precisa funcionar num projeto que NAO compila —
        e e justamente aí que ele e mais util.
        """
        ignorar = ("forge_modules", "__pycache__", ".git", "node_modules",
                   ".venv", "dist", "build")
        for pasta, subpastas, nomes in os.walk(self.raiz):
            subpastas[:] = [d for d in subpastas
                            if d not in ignorar and not d.startswith(".")]
            for nome in nomes:
                if not nome.endswith(".df"):
                    continue
                try:
                    with open(os.path.join(pasta, nome), encoding="utf-8",
                              errors="replace") as f:
                        fonte = f.read()
                except OSError:
                    continue
                self.usa_vitrine = self.usa_vitrine or "Vitrine" in fonte
                self.usa_kiln = self.usa_kiln or bool(
                    re.search(r"\badopt\s+(Arcane\.)?Kiln\b|\bserver\s+\w+\s+on\b",
                              fonte))
                self.usa_banco = self.usa_banco or bool(
                    re.search(r"Arcane\.(Database|Forge)\b|\bBanco\.", fonte))
                self.usa_redis = self.usa_redis or "redis://" in fonte

    # ── Perguntas ────────────────────────────────────────────

    @property
    def e_servidor(self):
        return self.usa_vitrine or self.usa_kiln

    @property
    def porta(self):
        return PORTA_VITRINE if self.usa_vitrine else PORTA_KILN

    @property
    def comando(self):
        """O que o container roda."""
        if self.usa_vitrine:
            return ["dataforge", "vitrine", "run", "--host=0.0.0.0"]
        alvo = self.entrada or "main.df"
        return ["dataforge", "run", alvo]

    @property
    def slug(self):
        """O nome em forma de identificador de recurso."""
        limpo = re.sub(r"[^a-z0-9-]+", "-", self.nome.lower()).strip("-")
        return limpo or "dataforge-app"

    def resumo(self):
        partes = []
        if self.usa_vitrine:
            partes.append("Vitrine")
        if self.usa_kiln:
            partes.append("Kiln")
        if self.usa_banco:
            partes.append("banco")
        if self.usa_redis:
            partes.append("Redis")
        if self.e_biblioteca:
            partes.append("biblioteca")
        return ", ".join(partes) or "programa"


# ═══════════════════════════════════════════════════════════
#  Docker
# ═══════════════════════════════════════════════════════════

def dockerfile(p):
    """A imagem, em duas etapas.

    Tres decisoes que valem explicar, porque todas ja custaram uma noite
    de alguem:

    **Duas etapas.** A imagem final nao carrega pip, compilador nem
    cache — sao ~120 MB que nao servem para nada em producao e sao
    superficie de ataque.

    **O manifesto e copiado ANTES do codigo.** A camada de dependencia
    so e refeita quando o 'forge.toml' muda; sem isso, um commit numa
    linha de codigo reinstala tudo, e o build vai de 8 s para 2 min.

    **Usuario sem privilegio.** Um processo que roda como root num
    container tem, por padrao, capacidades que ele nao precisa — e um
    escape de container vira root no host.
    """
    linhas = [
        f"# {p.nome} {p.versao} — gerado por 'dataforge devops docker'",
        "#",
        "# Duas etapas: a final nao carrega pip nem compilador.",
        "",
        f"FROM {BASE_PYTHON} AS construcao",
        "",
        "RUN pip install --no-cache-dir --upgrade pip \\",
        " && pip install --no-cache-dir --prefix=/instalado dataforge-lang",
        "",
        "",
        f"FROM {BASE_PYTHON}",
        "",
        f'LABEL org.opencontainers.image.title="{p.nome}"',
        f'LABEL org.opencontainers.image.version="{p.versao}"',
        "",
        "COPY --from=construcao /instalado /usr/local",
        "",
        "# Um processo que roda como root num container tem capacidades",
        "# que nao precisa — e um escape vira root no host.",
        "RUN useradd --create-home --shell /bin/bash forge",
        "WORKDIR /app",
        "",
        "# O manifesto ANTES do codigo: a camada de dependencia so e",
        "# refeita quando ele muda. Sem isto, um commit numa linha",
        "# reinstala tudo e o build vai de 8 s para 2 min.",
        "COPY --chown=forge:forge forge.toml forge.lock* ./",
        "RUN dataforge install || true",
        "",
        "COPY --chown=forge:forge . .",
        "USER forge",
        "",
    ]

    if p.e_servidor:
        rota = "/__vitrine__/saude" if p.usa_vitrine else "/saude"
        linhas += [
            f"EXPOSE {p.porta}",
            "",
            "# A sonda usa o proprio Python: 'curl' nao esta na imagem",
            "# slim, e instalar 30 MB para uma sonda de 200 bytes seria",
            "# trocar tamanho por conveniencia.",
            "HEALTHCHECK --interval=30s --timeout=3s --start-period=10s "
            "--retries=3 \\",
            "  CMD python -c \"import urllib.request,sys; "
            f"sys.exit(0 if urllib.request.urlopen("
            f"'http://127.0.0.1:{p.porta}{rota}', timeout=2).status == 200 "
            "else 1)\"",
            "",
        ]

    linhas.append(f"CMD {json.dumps(p.comando)}")
    return "\n".join(linhas) + "\n"


def dockerignore(p):
    """O que NAO entra na imagem.

    Ele existe por dois motivos, e o segundo e mais importante que o
    primeiro: a imagem fica menor, e o '.env' nao vaza dentro dela.
    Um segredo copiado para uma camada continua la depois de ser
    apagado numa camada seguinte — 'docker history' o mostra.
    """
    return """# Gerado por 'dataforge devops docker'.
#
# O segundo motivo importa mais que o primeiro: o '.env' NAO pode
# entrar na imagem. Um segredo copiado para uma camada continua nela
# depois de apagado numa camada seguinte, e 'docker history' o mostra.

.git
.gitignore
.github

# segredo
.env
.env.*
*.pem
*.key
secrets/

# artefato local
forge_modules/
__pycache__/
*.pyc
.venv/
venv/
dist/
build/
node_modules/

# o que so serve para desenvolver
tests/
testes/
__instantaneos__/
__snapshots__/
.pytest_cache/
*.db
*.sqlite3
.DS_Store

# o proprio Docker
Dockerfile*
docker-compose*.yml
.dockerignore
k8s/
helm/
"""


def compose(p):
    """Um ambiente completo, para desenvolver.

    Os servicos de apoio saem do que o codigo ADOTA. Um projeto que nao
    toca banco nao ganha um PostgreSQL — e um compose com servico que
    ninguem usa e um compose que as pessoas param de ler.
    """
    servicos = {
        "app": {
            "build": ".",
            "command": p.comando,
            "volumes": ["./:/app"],
            "environment": ["DATAFORGE_AMBIENTE=desenvolvimento"],
        }
    }
    if p.e_servidor:
        servicos["app"]["ports"] = [f"{p.porta}:{p.porta}"]

    dependencias = []
    if p.usa_banco:
        servicos["postgres"] = {
            "image": "postgres:16-alpine",
            "environment": [
                f"POSTGRES_DB={p.slug}",
                "POSTGRES_USER=forge",
                # Senha de DESENVOLVIMENTO, e o comentario diz isso no
                # arquivo: um leitor apressado copia o compose para
                # producao, e ele precisa topar com o aviso.
                "POSTGRES_PASSWORD=desenvolvimento",
            ],
            "ports": ["5432:5432"],
            "volumes": ["postgres:/var/lib/postgresql/data"],
            "healthcheck": {
                "test": ["CMD-SHELL", "pg_isready -U forge"],
                "interval": "5s",
                "retries": 10,
            },
        }
        dependencias.append("postgres")
    if p.usa_redis:
        servicos["redis"] = {
            "image": "redis:7-alpine",
            "ports": ["6379:6379"],
            "healthcheck": {
                "test": ["CMD", "redis-cli", "ping"],
                "interval": "5s",
                "retries": 10,
            },
        }
        dependencias.append("redis")

    if dependencias:
        # 'service_healthy', e nao 'service_started': o Postgres aceita
        # conexao segundos depois de o container subir, e sem esperar a
        # sonda a aplicacao falha na primeira consulta — de forma
        # intermitente, que e a pior.
        servicos["app"]["depends_on"] = {
            nome: {"condition": "service_healthy"} for nome in dependencias
        }

    texto = ["# Gerado por 'dataforge devops docker'.",
             "#",
             "# As senhas aqui sao de DESENVOLVIMENTO. Em producao, use",
             "# segredo de verdade — ver 'dataforge devops secrets'.",
             "",
             "services:"]
    for nome, corpo in servicos.items():
        texto.append(f"  {nome}:")
        texto += _yaml(corpo, 4)
        texto.append("")
    if p.usa_banco:
        texto += ["volumes:", "  postgres:"]
    return "\n".join(texto).rstrip() + "\n"


# ═══════════════════════════════════════════════════════════
#  CI
# ═══════════════════════════════════════════════════════════

def ci_github(p):
    """O pipeline, com os passos na ordem que economiza tempo.

    'check' antes de 'test' nao e detalhe: ele acha nome errado, aridade
    errada, campo inexistente e ciclo de import em menos de um segundo,
    e falhar ali poupa os minutos da suite.
    """
    passos = [
        ("instalar", "pip install dataforge-lang"),
        ("formato", "dataforge fmt . --check"),
        ("analise estatica", "dataforge check . --strict"),
        ("lint", "dataforge lint ."),
    ]
    passos.append(("testes", "dataforge test --minimo=70"))
    if os.path.isdir(os.path.join(p.raiz, "tests")):
        passos.append(("suites do Crucible",
                       "dataforge crucible --formato=junit "
                       "--saida=relatorio.xml || true"))

    linhas = [
        f"# CI de {p.nome} — gerado por 'dataforge devops ci github'.",
        "#",
        "# A ordem economiza tempo: 'check' acha nome errado, aridade",
        "# errada e ciclo de import em menos de um segundo, e falhar ali",
        "# poupa os minutos da suite.",
        "",
        "name: CI",
        "",
        "on:",
        "  push:",
        "    branches: [main]",
        "  pull_request:",
        "",
        "# Um push novo cancela o anterior: dois commits em um minuto",
        "# nao precisam de duas execucoes completas.",
        "concurrency:",
        "  group: ${{ github.workflow }}-${{ github.ref }}",
        "  cancel-in-progress: true",
        "",
        "jobs:",
        "  verificar:",
        "    runs-on: ubuntu-latest",
        "    strategy:",
        "      fail-fast: false",
        "      matrix:",
        "        python: ['3.10', '3.13']",
        "",
        "    steps:",
        "      - uses: actions/checkout@v4",
        "      - uses: actions/setup-python@v5",
        "        with:",
        "          python-version: ${{ matrix.python }}",
        "",
    ]
    for nome, comando in passos:
        linhas += [f"      - name: {nome}", f"        run: {comando}", ""]

    if p.e_servidor:
        linhas += [
            "  imagem:",
            "    needs: verificar",
            "    runs-on: ubuntu-latest",
            "    if: github.ref == 'refs/heads/main'",
            "    steps:",
            "      - uses: actions/checkout@v4",
            "",
            "      - name: construir",
            f"        run: docker build -t {p.slug}:${{{{ github.sha }}}} .",
            "",
            "      - name: ela roda",
            "        run: |",
            f"          docker run --rm -d -p {p.porta}:{p.porta} \\",
            f"            --name teste {p.slug}:${{{{ github.sha }}}}",
            "          # A sonda tem prazo: um 'sleep 5' fixo falha na",
            "          # maquina lenta e desperdica tempo na rapida.",
            "          for i in $(seq 30); do",
            f"            curl -fs localhost:{p.porta}"
            f"{'/__vitrine__/saude' if p.usa_vitrine else '/'} && break",
            "            sleep 1",
            "          done",
            "          docker logs teste",
            "          docker rm -f teste",
            "",
            "      - name: e nao roda como root",
            "        run: |",
            f"          quem=$(docker run --rm --entrypoint sh "
            f"{p.slug}:${{{{ github.sha }}}} -c 'id -u')",
            '          test "$quem" != "0" || { echo "roda como root"; exit 1; }',
            "",
        ]
    return "\n".join(linhas).rstrip() + "\n"


# ═══════════════════════════════════════════════════════════
#  Kubernetes
# ═══════════════════════════════════════════════════════════

def k8s_deployment(p, registro="registry.example.com"):
    """O Deployment, com o que um cluster de verdade cobra.

    Quatro coisas que quase todo exemplo de Deployment omite, e as
    quatro sao a diferenca entre funcionar e ficar de pe:

    | O quê | Sem ele |
    |---|---|
    | `resources` | um pod sem limite come o no inteiro e derruba os vizinhos |
    | `readinessProbe` | o Service manda trafego antes de a aplicacao estar pronta |
    | `livenessProbe` | um processo travado continua recebendo pedido |
    | `securityContext` | o container roda como root, com sistema de arquivos gravavel |
    """
    rota = "/__vitrine__/saude" if p.usa_vitrine else "/saude"
    return f"""# Gerado por 'dataforge devops k8s'.
#
# 'resources', 'readinessProbe', 'livenessProbe' e 'securityContext'
# nao sao enfeite: sem o primeiro um pod come o no inteiro; sem o
# segundo o Service manda trafego antes da hora; sem o terceiro um
# processo travado continua recebendo pedido; sem o quarto o container
# roda como root.

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {p.slug}
  labels:
    app: {p.slug}
spec:
  replicas: 3
  # 'maxUnavailable: 0' faz a atualizacao nao derrubar capacidade: o pod
  # novo entra em servico antes de o velho sair.
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: {p.slug}
  template:
    metadata:
      labels:
        app: {p.slug}
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: app
          image: {registro}/{p.slug}:{p.versao}
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: {p.porta}
              name: http
          env:
            - name: DATAFORGE_AMBIENTE
              value: producao
          envFrom:
            - configMapRef:
                name: {p.slug}-config
            - secretRef:
                name: {p.slug}-secret
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          # 'readiness' decide se recebe trafego; 'liveness', se e
          # reiniciado. O prazo do liveness e maior de proposito: matar
          # um processo que esta so lento piora tudo.
          readinessProbe:
            httpGet:
              path: {rota}
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: {rota}
              port: http
            initialDelaySeconds: 30
            periodSeconds: 30
            failureThreshold: 3
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      # Com 'readOnlyRootFilesystem', o processo ainda precisa de /tmp.
      volumes:
        - name: tmp
          emptyDir: {{}}
      # A sessao da Vitrine vive na memoria do processo: com mais de uma
      # replica, ou se usa 'sessionAffinity' no Service, ou a sessao
      # precisa sair para um armazenamento comum.
      terminationGracePeriodSeconds: 30
"""


def k8s_service(p):
    afinidade = ""
    if p.usa_vitrine:
        afinidade = """
  # A sessao da Vitrine vive na memoria do processo: sem afinidade, dois
  # pedidos da mesma pessoa caem em pods diferentes e a sessao se perde.
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800"""
    return f"""# Gerado por 'dataforge devops k8s'.

apiVersion: v1
kind: Service
metadata:
  name: {p.slug}
  labels:
    app: {p.slug}
spec:
  type: ClusterIP
  selector:
    app: {p.slug}
  ports:
    - port: 80
      targetPort: http
      name: http{afinidade}
"""


def k8s_ingress(p, dominio=""):
    host = dominio or f"{p.slug}.example.com"
    return f"""# Gerado por 'dataforge devops k8s'.
#
# TLS pelo cert-manager: a Vitrine e o Kiln rodam sobre o 'http.server'
# do Python, que nao tem TLS. Quem termina HTTPS e o ingress.

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {p.slug}
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: 10m
    # Sem estes dois, um SSE ou WebSocket e cortado em 60 segundos.
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
spec:
  ingressClassName: nginx
  tls:
    - hosts: [{host}]
      secretName: {p.slug}-tls
  rules:
    - host: {host}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {p.slug}
                port:
                  name: http
"""


def k8s_config(p):
    return f"""# Gerado por 'dataforge devops k8s'.
#
# O que NAO e segredo. Segredo vai no Secret, e o Secret nao vai para o
# repositorio — ver 'dataforge devops secrets'.

apiVersion: v1
kind: ConfigMap
metadata:
  name: {p.slug}-config
data:
  DATAFORGE_AMBIENTE: producao
  DATAFORGE_PORTA: "{p.porta}"
  DATAFORGE_LOG: json
"""


def k8s_hpa(p):
    return f"""# Gerado por 'dataforge devops k8s'.
#
# O HPA precisa de 'resources.requests' no Deployment: a porcentagem de
# CPU e calculada CONTRA o request, e sem ele a metrica nao existe.

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {p.slug}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {p.slug}
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
  behavior:
    # Subir rapido e descer devagar: um pico atendido a menos custa
    # usuario, e um pod a mais por cinco minutos custa centavos.
    scaleUp:
      stabilizationWindowSeconds: 30
    scaleDown:
      stabilizationWindowSeconds: 300
"""


# ═══════════════════════════════════════════════════════════
#  Nginx
# ═══════════════════════════════════════════════════════════

def nginx(p, dominio=""):
    host = dominio or f"{p.slug}.example.com"
    return f"""# Gerado por 'dataforge devops nginx'.
#
# A Vitrine e o Kiln rodam sobre o 'http.server' do Python: sem TLS, sem
# HTTP/2, sem compressao e sem servir estatico com cache. Quem faz isso
# e o nginx — e e por isso que ele vai na frente, nao por gosto.

upstream {p.slug} {{
    server 127.0.0.1:{p.porta};
    keepalive 32;
}}

server {{
    listen 80;
    server_name {host};
    # O ACME do certbot precisa continuar alcancavel em HTTP.
    location /.well-known/acme-challenge/ {{ root /var/www/certbot; }}
    location / {{ return 301 https://$host$request_uri; }}
}}

server {{
    listen 443 ssl;
    http2 on;
    server_name {host};

    ssl_certificate     /etc/letsencrypt/live/{host}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{host}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_session_cache shared:SSL:10m;

    # HSTS depois de o certificado estar de pe, e nao antes: ligado com
    # o TLS quebrado, ele tranca o dominio fora do ar no navegador de
    # quem visitou.
    add_header Strict-Transport-Security "max-age=31536000" always;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript
               image/svg+xml;
    gzip_min_length 1024;

    client_max_body_size 10m;

    location / {{
        proxy_pass http://{p.slug};
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Upgrade para WebSocket. As duas linhas sao obrigatorias: sem
        # elas o handshake responde 400 e o erro nao diz por que.
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}

    # SSE: o buffer do nginx guarda a resposta e o evento so chega
    # quando ele enche — o que destroi o streaming. A Vitrine e o Kiln
    # ja mandam 'X-Accel-Buffering: no', e isto e o cinto de seguranca.
    location /__vitrine__/ {{
        proxy_pass http://{p.slug};
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
    }}
}}
"""


# ═══════════════════════════════════════════════════════════
#  Observabilidade
# ═══════════════════════════════════════════════════════════

def prometheus(p):
    return f"""# Gerado por 'dataforge devops observar'.

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: {p.slug}
    metrics_path: {'/__vitrine__/metricas' if p.usa_vitrine else '/metricas'}
    static_configs:
      - targets: ['app:{p.porta}']

# A rota de metricas da Vitrine devolve JSON, e o Prometheus quer o
# formato de exposicao dele. 'Arcane.Observar.exportar_prometheus'
# converte:
#
#     route GET "/metrics":
#         respond text Observar.exportar_prometheus(V.metricas())
"""


def compose_observar(p):
    return f"""# Gerado por 'dataforge devops observar'.
#
#   docker compose -f docker-compose.observar.yml up -d
#   Grafana em http://localhost:3000  (admin / admin)

services:
  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - ./observar/prometheus.yml:/etc/prometheus/prometheus.yml:ro

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana:/var/lib/grafana
    depends_on: [prometheus]

  # O coletor recebe tracos por OTLP e os repassa. Ele existe para a
  # aplicacao nao precisar saber para onde o traco vai: trocar de
  # backend passa a ser mudar a config do coletor.
  otel:
    image: otel/opentelemetry-collector-contrib:latest
    ports: ["4317:4317", "4318:4318"]
    volumes:
      - ./observar/otel.yml:/etc/otelcol-contrib/config.yaml:ro

volumes:
  grafana:
"""


def otel(p):
    return """# Gerado por 'dataforge devops observar'.

receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 5s
  # Sem limite de memoria, um pico de traco derruba o coletor — e aí
  # perde-se justamente o traco do incidente.
  memory_limiter:
    check_interval: 1s
    limit_percentage: 75

exporters:
  debug:
    verbosity: basic

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [debug]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [debug]
"""


# ═══════════════════════════════════════════════════════════
#  SBOM
# ═══════════════════════════════════════════════════════════

def sbom(p):
    """O inventario de dependencias, em CycloneDX.

    Ele responde a pergunta que aparece no dia em que sai um CVE: "eu
    uso isso?". Sem inventario, a resposta e uma tarde de arqueologia
    por repositorio.

    O DataForge tem uma resposta curta para a maior parte dessa
    pergunta — o runtime nao tem dependencia nenhuma —, e o SBOM diz
    isso explicitamente em vez de deixar a ausencia parecer descuido.
    """
    componentes = [{
        "type": "library",
        "name": "dataforge-lang",
        "version": "1.0.0",
        "purl": "pkg:pypi/dataforge-lang@1.0.0",
        "description": "o runtime — sem dependencia externa",
        "licenses": [{"license": {"id": "MIT"}}],
    }]
    for nome, faixa in p.dependencias:
        componentes.append({
            "type": "library",
            "name": nome,
            "version": faixa.lstrip("^~>=<"),
            "purl": f"pkg:dataforge/{nome}@{faixa.lstrip('^~>=<')}",
        })

    documento = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                       time.gmtime()),
            "tools": [{"vendor": "DataForge", "name": "dataforge devops",
                       "version": "1.0.0"}],
            "component": {
                "type": "application",
                "name": p.nome,
                "version": p.versao,
            },
        },
        "components": componentes,
    }
    return json.dumps(documento, indent=2, ensure_ascii=False) + "\n"


# ═══════════════════════════════════════════════════════════
#  Segredos
# ═══════════════════════════════════════════════════════════

def env_exemplo(p):
    linhas = [
        "# Gerado por 'dataforge devops secrets'.",
        "#",
        "# ESTE arquivo vai para o repositorio; o '.env' NAO.",
        "# Ele existe para dizer QUAIS variaveis a aplicacao espera —",
        "# um projeto que nao documenta isso obriga cada pessoa nova a",
        "# descobrir por tentativa e erro.",
        "",
        "DATAFORGE_AMBIENTE=desenvolvimento",
    ]
    if p.e_servidor:
        linhas += [f"DATAFORGE_PORTA={p.porta}", "DATAFORGE_HOST=127.0.0.1"]
    if p.usa_banco:
        linhas += ["",
                   f"DATABASE_URL=postgres://forge:desenvolvimento@localhost:5432/{p.slug}"]
    if p.usa_redis:
        linhas.append("REDIS_URL=redis://localhost:6379")
    linhas += ["",
               "# Gere com: dataforge eval 'out Crypto.token(32)'",
               "SEGREDO_DA_SESSAO=troque-isto"]
    return "\n".join(linhas) + "\n"


#: As linhas que TODO .gitignore de projeto DataForge precisa.
#:
#: 'forge_modules/' porque ele e reconstruivel a partir do lock;
#: '*.db' porque um SQLite commitado e conflito de merge binario; e o
#: '.env' porque um segredo no historico do git continua la depois de
#: apagado no arquivo.
GITIGNORE = """
# DataForge
forge_modules/
__pycache__/
*.pyc
dist/
build/

# segredo — no historico do git, ele continua la depois de apagado
.env
.env.*
!.env.example
*.pem
*.key

# banco local: um SQLite commitado e conflito de merge binario
*.db
*.db-wal
*.db-shm
*.sqlite3

# relatorio
relatorio.xml
cobertura.json
"""


# ═══════════════════════════════════════════════════════════
#  Helm e Terraform
# ═══════════════════════════════════════════════════════════

def helm_chart(p):
    return f"""apiVersion: v2
name: {p.slug}
description: {p.nome}
type: application
version: 0.1.0
appVersion: "{p.versao}"
"""


def helm_values(p, registro="registry.example.com"):
    return f"""# Gerado por 'dataforge devops helm'.

replicaCount: 3

image:
  repository: {registro}/{p.slug}
  tag: "{p.versao}"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  host: {p.slug}.example.com
  tls: true

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

# O que NAO e segredo. Segredo entra por 'existingSecret', e nao aqui:
# um values.yaml e commitado.
config:
  DATAFORGE_AMBIENTE: producao

existingSecret: {p.slug}-secret
"""


def terraform(p):
    return f"""# Gerado por 'dataforge devops terraform'.
#
# O ESQUELETO, e nao a infraestrutura: o provedor e a topologia sao
# decisao de quem opera, e um Terraform que assume AWS obriga quem usa
# outra nuvem a apagar mais do que aproveita.
#
#   terraform init
#   terraform plan
#   terraform apply

terraform {{
  required_version = ">= 1.6"
  required_providers {{
    kubernetes = {{
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }}
  }}

  # Estado LOCAL e a primeira coisa a trocar: em equipe, dois 'apply'
  # simultaneos sobre estado local corrompem o que existe. Use S3 com
  # DynamoDB, GCS, ou o backend do seu provedor.
  # backend "s3" {{ … }}
}}

variable "namespace" {{
  type    = string
  default = "{p.slug}"
}}

variable "imagem" {{
  type        = string
  description = "a imagem com a tag — nunca ':latest' em producao"
}}

variable "replicas" {{
  type    = number
  default = 3
}}

resource "kubernetes_namespace" "app" {{
  metadata {{
    name = var.namespace
  }}
}}

# O restante vem dos manifestos de 'dataforge devops k8s'. Aplique-os
# com 'kubernetes_manifest', ou com o Helm desta mesma pasta:
#
# resource "helm_release" "app" {{
#   name      = "{p.slug}"
#   chart     = "./helm"
#   namespace = kubernetes_namespace.app.metadata[0].name
#   set {{
#     name  = "image.tag"
#     value = var.imagem
#   }}
# }}
"""


# ═══════════════════════════════════════════════════════════
#  YAML sem biblioteca
# ═══════════════════════════════════════════════════════════

def _yaml(valor, recuo=0):
    """Um vault vira YAML. Só o que os geradores usam.

    Um escritor de YAML completo seria um projeto; aqui o dado e nosso e
    a forma e conhecida. O que ele NAO faz — ancora, tag, multilinha —
    nao aparece em manifesto de Deployment.
    """
    espaco = " " * recuo
    linhas = []
    if isinstance(valor, dict):
        for chave, dentro in valor.items():
            if isinstance(dentro, dict):
                linhas.append(f"{espaco}{chave}:")
                linhas += _yaml(dentro, recuo + 2)
            elif isinstance(dentro, list):
                linhas.append(f"{espaco}{chave}:")
                for item in dentro:
                    if isinstance(item, (dict, list)):
                        linhas += _yaml(item, recuo + 2)
                    else:
                        linhas.append(f"{espaco}  - {_escalar(item)}")
            else:
                linhas.append(f"{espaco}{chave}: {_escalar(dentro)}")
    elif isinstance(valor, list):
        for item in valor:
            linhas.append(f"{espaco}- {_escalar(item)}")
    else:
        linhas.append(f"{espaco}{_escalar(valor)}")
    return linhas


def _escalar(valor):
    """Um valor simples, citado quando precisa.

    A regra que importa: '8501' sem aspas e um NUMERO em YAML, e uma
    porta que deveria ser texto viraria inteiro no lugar errado. E 'yes'
    e 'no' sao booleanos em YAML 1.1 — um valor assim sem aspas muda de
    tipo sozinho.
    """
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, (int, float)):
        return str(valor)
    texto = str(valor)
    perigosos = {"yes", "no", "on", "off", "true", "false", "null", "~"}
    if (not texto or texto.lower() in perigosos
            or texto[0] in "&*!|>%@`{[" or ": " in texto
            or texto != texto.strip()):
        return json.dumps(texto)
    return texto
