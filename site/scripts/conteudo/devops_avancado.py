# -*- coding: utf-8 -*-
"""DevOps — as doze páginas do ecossistema.

`/docs/devops` apresenta o comando. Estas descem em cada artefato e em
cada integração: o contêiner, o cluster, o CI que anota o PR, o passo
de workflow escrito em DataForge, o webhook assinado, a API do GitHub,
o release por tag, o repositório, o GitLab, o ambiente de
desenvolvimento e a VM sem contêiner.

Os blocos `df` rodam — os de Actions apontam `GITHUB_OUTPUT` e
`GITHUB_STEP_SUMMARY` para arquivos temporários, que é exatamente o que
o executor faz.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/docker",
"title": "Docker e Compose",
"description": "A imagem multiestágio, o compose com banco — e as cinco decisões que cada artefato carrega.",
"blocos": [
 {"p": "`dataforge devops docker` escreve três arquivos: `Dockerfile`, `.dockerignore` e `docker-compose.yml`. Eles saem do que o projeto **usa** — o gerador lê os `adopt` e o `forge.toml` —, e cada linha tem um motivo que um artefato copiado da internet não tem."},
 {"code": """dataforge devops docker              # os tres arquivos
dataforge devops docker --seco       # mostra, sem escrever
dataforge devops docker build        # docker build com a tag do projeto
dataforge devops doctor              # o que falta para subir""", "lang": "bash"},

 {"h2": "O que a imagem carrega, e por quê"},
 {"table": {"head": ["No artefato", "Sem ele"], "rows": [
   ["`USER forge`", "um escape de contêiner vira root no host"],
   ["o manifesto copiado **antes** do código", "um commit numa linha reinstala tudo — de 8 s para 2 min"],
   ["`.env` no `.dockerignore`", "o segredo fica na camada, e `docker history` o mostra"],
   ["`HEALTHCHECK` com prazo", "o orquestrador manda tráfego para um contêiner que ainda está subindo"],
   ["`depends_on: service_healthy` no compose", "a aplicação falha na primeira consulta, de forma intermitente"]]}},

 {"callout": {"tipo": "atencao", "titulo": "`0.0.0.0` dentro do contêiner", "texto": "O padrão do Kiln e da Vitrine é `127.0.0.1`, que de dentro do contêiner significa **o próprio contêiner**. O sintoma engana: o log diz *“no ar”* e o `curl` de fora não recebe nada. `ignite api at \"0.0.0.0\"` — e o gerador já escreve isso no comando."}},

 {"h2": "O banco no compose"},
 {"p": "Quando o projeto adota `Forge`, o compose ganha o serviço do banco com sonda de saúde, e a aplicação lê a URL de `DATABASE_URL`. `Forge.esperar` espera o banco **aceitar** conexão antes da primeira consulta — ver [O banco em contêiner](/docs/banco-de-dados/docker)."},
 {"code": """services:
  app:
    build: .
    environment:
      DATABASE_URL: postgres://app:app@banco:5432/app
    depends_on:
      banco:
        condition: service_healthy
  banco:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 2s
      retries: 30""", "lang": "yaml"},

 {"p": "Continue em [Kubernetes](/docs/devops/kubernetes) e [Instalação com Docker](/docs/instalacao/docker)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/kubernetes",
"title": "Kubernetes",
"description": "Deployment, Service, Ingress, ConfigMap e HPA — com sondas e limites, que é o que falta em quase todo manifesto.",
"blocos": [
 {"p": "`dataforge devops k8s` escreve os cinco manifestos em `k8s/`. O Ingress e o HPA só saem quando o projeto é um servidor — um *job* que processa uma fila não recebe tráfego, e um Ingress para ele seria uma porta aberta para nada."},
 {"code": """dataforge devops k8s --registro=ghcr.io/minha-org --dominio=loja.exemplo.com
kubectl apply -f k8s/
kubectl rollout status deploy/loja""", "lang": "bash"},

 {"h2": "As duas sondas não são a mesma pergunta"},
 {"table": {"head": ["Sonda", "Pergunta", "Se falha"], "rows": [
   ["`readinessProbe`", "posso receber tráfego **agora**?", "sai do Service, e volta quando responder"],
   ["`livenessProbe`", "ainda estou vivo?", "o pod é **reiniciado**"],
   ["`startupProbe`", "já terminei de subir?", "as outras duas esperam"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Liveness que depende do banco derruba tudo", "texto": "Se a sonda de vida consulta o banco, uma lentidão no banco reinicia **todos** os pods ao mesmo tempo — e eles voltam juntos, martelando o banco que já estava lento. A sonda de vida pergunta só se o processo responde; a de prontidão pode olhar as dependências."}},

 {"h2": "Limites"},
 {"table": {"head": ["No manifesto", "Sem ele"], "rows": [
   ["`resources.requests`", "o agendador não sabe onde o pod cabe, e empilha tudo num nó"],
   ["`resources.limits.memory`", "um vazamento come o nó inteiro, e derruba os vizinhos"],
   ["`HorizontalPodAutoscaler`", "o pico de tráfego encontra o mesmo número de réplicas da madrugada"],
   ["`securityContext.runAsNonRoot`", "a imagem que alguém trocou por uma que roda como root sobe sem aviso"]]}},

 {"p": "Continue em [Helm e Terraform](/docs/devops/helm-terraform)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/helm-terraform",
"title": "Helm e Terraform",
"description": "O chart para variar por ambiente, e o esqueleto de infraestrutura como código.",
"blocos": [
 {"p": "Os manifestos de `k8s/` são um ambiente. Quando há três — desenvolvimento, homologação, produção —, copiar a pasta três vezes é o começo da divergência. O chart do Helm é **um** conjunto de modelos e um `values.yaml` por ambiente."},
 {"code": """dataforge devops helm --registro=ghcr.io/minha-org
helm install loja ./chart -f chart/values.yaml
helm upgrade loja ./chart --set imagem.tag=1.4.2

dataforge devops terraform
cd infra && terraform init && terraform plan""", "lang": "bash"},

 {"table": {"head": ["Ferramenta", "Responde", "Não responde"], "rows": [
   ["**Helm**", "o que roda **dentro** do cluster, e como varia por ambiente", "onde o cluster mora"],
   ["**Terraform**", "o que existe **fora**: cluster, banco gerenciado, DNS, bucket", "o que roda dentro dele"]]}},

 {"callout": {"tipo": "dica", "titulo": "O estado do Terraform é um segredo", "texto": "O `terraform.tfstate` guarda senhas e chaves em texto. Ele vai para um *backend* remoto com trava (S3 + DynamoDB, GCS, Terraform Cloud) — nunca para o repositório. O esqueleto gerado já traz o `.gitignore` com ele."}},

 {"h2": "O que o gerador não faz"},
 {"p": "Ele não fala com o cluster nem com a nuvem. `dataforge devops` gera **texto** e sai da frente: um `deploy` que falasse com Kubernetes por dentro esconderia o que a imagem é, e no dia em que alguém precisasse mudar uma camada não haveria onde mexer."},

 {"p": "Continue em [GitHub Actions](/docs/devops/github-actions)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/github-actions",
"title": "GitHub Actions",
"description": "O pipeline na ordem que economiza tempo — e o erro de análise anotado na linha do PR.",
"blocos": [
 {"p": "`dataforge devops ci github` escreve `.github/workflows/ci.yml`: formato, análise estática, lint e testes, numa matriz de Python, com um push novo cancelando o anterior. A ordem é a do custo: o `check` acha nome errado e ciclo de import em menos de um segundo, e falhar ali poupa os minutos da suíte."},
 {"code": """dataforge devops ci github
git add .github/workflows/ci.yml && git commit -m "CI\"""", "lang": "bash"},

 {"h2": "O erro na linha do PR"},
 {"p": "`dataforge check --formato=github` troca o desenho do terminal por **anotações do Actions**. Com elas o erro aparece na aba *Files changed*, na linha exata — e não só no log do job, que ninguém abre enquanto o resto do PR está verde."},
 {"code": """$ dataforge check src/ --formato=github
::error file=src/pedido.df,line=14,col=5,title=arity::Action 'total' takes 1 argument(s) but 2 were given%0Asugestão: Chame como total(itens)
::warning file=src/pedido.df,line=30,col=9,title=escrita-concorrente::…""", "lang": "text"},

 {"table": {"head": ["Decisão", "Porque"], "rows": [
   ["o nível segue a gravidade", "erro vira `::error`, aviso vira `::warning` — o PR distingue os dois"],
   ["o `title` é o código do diagnóstico", "`arity`, `undefined-name`: é o que se procura e o que se silencia com `// df: permitir`"],
   ["a sugestão vai junto", "a correção aparece na mesma caixa que o erro"],
   ["a mensagem é escapada", "um `%` ou uma quebra de linha cortaria a anotação no meio"],
   ["o código de saída não muda", "o job continua reprovando com erro, com ou sem anotação"]]}},

 {"h2": "O que o workflow gerado já faz"},
 {"table": {"head": ["No workflow", "Sem ele"], "rows": [
   ["`concurrency` com `cancel-in-progress`", "dois commits num minuto rodam a suíte duas vezes inteiras"],
   ["matriz `3.10` e `3.13`", "o que quebra na versão mínima só aparece com o primeiro usuário dela"],
   ["`fail-fast: false`", "a primeira versão que falha cancela a outra, e não se sabe se é geral"],
   ["o job da imagem confere `id -u`", "a imagem que roda como root chega ao registro"]]}},

 {"p": "Continue em [Actions na linguagem](/docs/devops/actions-na-linguagem)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/actions-na-linguagem",
"title": "Um passo de workflow em DataForge",
"description": "Saídas, variáveis, resumo, anotações, máscara e grupos — com Arcane.GitHub, e sem injeção.",
"blocos": [
 {"p": "Um passo de workflow conversa com o executor por **arquivos** (`GITHUB_OUTPUT`, `GITHUB_ENV`, `GITHUB_STEP_SUMMARY`) e por **linhas mágicas** na saída. Escrever isso à mão erra calado de dois jeitos: uma saída com quebra de linha vira duas (ou injeta uma variável), e uma mensagem com `%` é cortada. `Arcane.GitHub` escreve do jeito que o toolkit oficial escreve."},
 {"code": """- name: relatorio
  id: relatorio
  run: dataforge run ci/relatorio.df
- name: usar
  run: echo "${{ steps.relatorio.outputs.cobertura }}\"""", "lang": "yaml"},

 {"h2": "Saída e resumo"},
 {"code": """adopt Arcane.GitHub as GH
adopt Arcane.OS as OS
adopt Arcane.IO as IO

// O executor aponta estas variaveis para arquivos. Aqui, para
// temporarios — e exatamente o que acontece dentro do job.
pasta := $"{OS.temp_dir()}/df-gh-{randint(100000, 999999)}"
IO.mkdir(pasta)
OS.set_env("GITHUB_OUTPUT", $"{pasta}/output")
OS.set_env("GITHUB_STEP_SUMMARY", $"{pasta}/resumo.md")

resultados := [
    {"suite": "pedidos", "passou": 42, "falhou": 0},
    {"suite": "estoque", "passou": 17, "falhou": 1}
]

// Uma saida multilinha: sem o delimitador aleatorio, a segunda linha
// viraria outra saida — ou outra variavel.
GH.saida("resumo", "pedidos: 42\\nestoque: 17")
GH.saida("falhas", str(sum(resultados >> morph r: r["falhou"])))
GH.resumo("## Testes\\n\\n" + GH.tabela_markdown(resultados))

saidas := IO.read($"{pasta}/output")
assert "falhas<<ghadelimiter_" in saidas
assert "| estoque | 17 | 1 |" in IO.read($"{pasta}/resumo.md")

OS.unset_env("GITHUB_OUTPUT")
OS.unset_env("GITHUB_STEP_SUMMARY")
IO.remove_tree(pasta)
out "saidas escritas como o executor espera\"""", "lang": "df"},

 {"h2": "Anotações, máscara e grupos"},
 {"code": """adopt Arcane.GitHub as GH

// A anotacao aparece na linha do arquivo, no PR.
a := GH.anotacao("aviso", "cobertura caiu para 71%\\nminimo: 80%", "src/regras.df", 12,
    titulo := "cobertura")
out a
assert a is "::warning file=src/regras.df,line=12,title=cobertura::cobertura caiu para 71%25%0Aminimo: 80%25"

// Nivel desconhecido e recusado: o executor ignoraria a linha calado.
monitor:
    GH.anotacao("fatal", "x")
    assert no
handle Error as e:
    out e.message

// Fora do Actions, o contexto vem vazio — e nao levanta.
c := GH.contexto()
out $"em actions: {c['em_actions']}\"""", "lang": "df"},

 {"table": {"head": ["Função", "O que ela resolve"], "rows": [
   ["`saida(nome, valor)`", "multilinha com delimitador aleatório — o valor não injeta outra saída"],
   ["`exportar(nome, valor)`", "variável para os passos seguintes; nome com `=` é recusado"],
   ["`resumo(md)` + `tabela_markdown`", "a página do job; a `|` dentro de um valor é escapada"],
   ["`anotar` / `anotacao`", "`%`, `\\n`, `:` e `,` escapados"],
   ["`mascarar_no_log(segredo)`", "linha a linha — o executor casa por linha"],
   ["`grupo(nome, acao)`", "o `::endgroup::` sai mesmo se a ação falhar"],
   ["`contexto()` / `evento()`", "repositório, commit, quem disparou, a carga do evento"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Mascarar antes de imprimir", "texto": "`mascarar_no_log` só esconde o que for impresso **depois** dele. Um segredo lido de uma API e impresso para depurar antes da máscara já está no log — e o log de um repositório público é público."}},

 {"p": "Continue em [Webhooks](/docs/devops/webhooks) e [Arcane.GitHub](/docs/biblioteca/github)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/webhooks",
"title": "Receber webhooks do GitHub",
"description": "A assinatura HMAC sobre os bytes originais, a entrega que chega duas vezes, e o 401 que não processa nada.",
"blocos": [
 {"p": "Um webhook é um POST que chega de fora dizendo *“houve um push”*. Qualquer um que descubra a URL pode mandar o mesmo POST — por isso o GitHub **assina** o corpo com HMAC-SHA256, e o cabeçalho `X-Hub-Signature-256` traz a assinatura. Conferi-la é a única coisa que separa um evento do GitHub de um pedido forjado."},

 {"h2": "No Kiln"},
 {"code": """adopt Kiln
adopt Arcane.GitHub as GH

steady SEGREDO := "troque-por-OS.env"
vistos := []
processados := []

server hooks on 0:
    route POST "/github":
        monitor:
            // raw_body: os BYTES que chegaram. Decodificar e re-serializar o
            // JSON muda espacos e ordem das chaves, e a assinatura nao bate.
            e := GH.evento_de_webhook(headers, req["raw_body"], SEGREDO)
        handle Error:
            respond 401 json {"erro": "assinatura invalida"}
        // O GitHub reentrega. Processar duas vezes e o proximo defeito.
        given e["entrega"] in vistos:
            respond 200 json {"repetida": yes}
        vistos.append(e["entrega"])
        given e["tipo"] is "pull_request" and e["acao"] is "opened":
            processados.append(e["carga"]["number"])
        respond 202 json {"ok": yes}

corpo := to_json({"action": "opened", "number": 7})
cab := {"X-GitHub-Event": "pull_request", "X-GitHub-Delivery": "d-1",
        "X-Hub-Signature-256": GH.assinatura(SEGREDO, corpo)}

assert Kiln.test(hooks, "POST", "/github", corpo, cab)["status"] is 202
assert Kiln.test(hooks, "POST", "/github", corpo, cab)["body"]["repetida"]
assert processados is [7]

forjado := cab with {}
forjado["X-Hub-Signature-256"] := GH.assinatura("outro", corpo)
assert Kiln.test(hooks, "POST", "/github", corpo, forjado)["status"] is 401
out "webhook: assinado, idempotente, e o forjado recusado\"""", "lang": "df"},

 {"h2": "As quatro decisões"},
 {"table": {"head": ["Decisão", "Sem ela"], "rows": [
   ["conferir sobre `raw_body`", "a assinatura nunca bate, e alguém desliga a conferência para *“funcionar”*"],
   ["comparar em **tempo constante**", "`==` vaza, pelo tempo, quantos caracteres da assinatura acertaram"],
   ["guardar o `X-GitHub-Delivery`", "a reentrega cria o mesmo deploy, o mesmo e-mail, a mesma cobrança duas vezes"],
   ["responder rápido (202) e processar depois", "o GitHub desiste em 10 s e marca a entrega como falha"]]}},

 {"callout": {"tipo": "dica", "titulo": "O vetor da documentação", "texto": "O teste de `Arcane.GitHub` confere a assinatura contra o exemplo publicado pelo GitHub (segredo *“It's a Secret to Everybody”*, corpo *“Hello, World!”*). Comparar a implementação com ela mesma não prova nada; com o vetor oficial, prova."}},

 {"p": "Continue em [A API do GitHub](/docs/devops/api-github)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/api-github",
"title": "A API do GitHub",
"description": "Issue, comentário no PR, status do commit, release e workflow_dispatch — com paginação e o limite de taxa.",
"blocos": [
 {"p": "`GH.cliente(token)` fala a API REST v3: manda os cabeçalhos que ela pede (`Accept`, `X-GitHub-Api-Version`), pagina seguindo `Link: rel=\"next\"`, guarda o limite de taxa que sobrou e nunca imprime o token. Sem `token`, ele usa o `GITHUB_TOKEN` do ambiente — que é o que existe dentro de um job."},

 {"code": """adopt Arcane.GitHub as GH

gh := GH.cliente()          // GITHUB_TOKEN do ambiente
out gh                      // o token nunca aparece
assert "sem token" in str(gh) or "com token" in str(gh)

// O que e recusado ANTES de ir a rede:
monitor:
    gh.status("dono/repo", "abc123", "ok")
    assert no
handle Error as e:
    out e.message

monitor:
    gh.repositorio("sem-barra")
    assert no
handle Error as e:
    out e.message""", "lang": "df"},

 {"h2": "No CI: comentar o resultado no PR"},
 {"code": """adopt Arcane.GitHub as GH

// ci/comentar.df — roda num job de pull_request
action comentar_cobertura(percentual):
    c := GH.contexto()
    ev := GH.evento()
    numero := ev["pull_request"]["number"] ?? void
    given numero is void:
        yield no
    gh := GH.cliente()
    gh.comentar(c["repositorio"], numero,
        $"Cobertura: **{percentual}%** — [execucao]({c['url_da_execucao']})")
    yield yes

// Fora de um PR nao comenta nada — e nao quebra.
assert comentar_cobertura(87) is no""", "lang": "df"},

 {"h2": "O que ele oferece"},
 {"table": {"head": ["Método", "Endpoint"], "rows": [
   ["`repositorio(repo)`", "`GET /repos/{repo}`"],
   ["`issues(repo, estado)`", "todas as páginas — e **sem** os PRs, que a API mistura"],
   ["`criar_issue(repo, titulo, corpo, rotulos)`", "`POST /repos/{repo}/issues`"],
   ["`comentar(repo, numero, texto)`", "issue **ou** PR — para a API, os dois são issues"],
   ["`status(repo, sha, estado, contexto)`", "o ✓/✗ ao lado do commit"],
   ["`criar_release(repo, tag, …)`", "`POST /repos/{repo}/releases`"],
   ["`disparar_workflow(repo, arquivo, ref, entradas)`", "`workflow_dispatch`"],
   ["`todas(caminho)` / `pedir(metodo, caminho, corpo)`", "qualquer outro endpoint"]]}},

 {"callout": {"tipo": "atencao", "titulo": "404 num repositório privado", "texto": "Um token sem acesso a um repositório privado recebe **404**, e não 403 — a API não confirma que o repositório existe. A mensagem do erro diz isso, porque a reação natural a um 404 é procurar um erro de digitação que não existe."}},

 {"p": "Continue em [Release por tag](/docs/devops/release)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/release",
"title": "Release por tag",
"description": "Uma tag v* testa de novo, confere a versão do manifesto, empacota e publica.",
"blocos": [
 {"p": "`dataforge devops github` escreve `.github/workflows/release.yml`. Ele dispara numa tag `v*` e faz quatro coisas, nesta ordem — e a ordem é o que impede o release errado."},
 {"list": [
   "**Confere a tag contra o `forge.toml`.** `v1.4.0` com `version = \"1.3.9\"` no manifesto é recusado: o pacote sairia com um número e a tag diria outro.",
   "**Testa de novo.** A tag pode apontar para um commit que nunca passou pelo CI.",
   "**Empacota.** Uma biblioteca vira o tarball reprodutível de `dataforge pack`; uma aplicação, um `.tar.gz` sem `.git` nem `forge_modules`.",
   "**Publica** com `gh release create --generate-notes`.",
 ], "ordered": True},

 {"code": """# subir a versao
sed -i 's/^version = .*/version = "1.4.0"/' forge.toml
git commit -am "1.4.0"
git tag v1.4.0
git push --follow-tags""", "lang": "bash"},

 {"table": {"head": ["No workflow", "Sem ele"], "rows": [
   ["`permissions: contents: write`", "o token padrão é somente-leitura, e o passo de publicar falha com 403 no primeiro release"],
   ["a conferência tag × manifesto", "o pacote `1.3.9` publicado na release `v1.4.0`"],
   ["os testes antes do pacote", "a tag num commit quebrado vira uma versão publicada"],
   ["`--generate-notes`", "as notas escritas à mão esquecem metade dos PRs"]]}},

 {"callout": {"tipo": "dica", "titulo": "Que número subir", "texto": "`dataforge abi` compara a superfície da versão anterior com a atual e diz se a mudança é patch, minor ou major — renomear um parâmetro é quebra, porque a chamada com nome existe nesta linguagem. Ver [Compatibilidade](/docs/abi/compatibilidade)."}},

 {"p": "Continue em [O repositório](/docs/devops/repositorio)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/repositorio",
"title": "O repositório",
"description": "Dependabot, CODEOWNERS, modelos de PR e de issue, e a proteção do ramo principal.",
"blocos": [
 {"p": "O mesmo `dataforge devops github` escreve os arquivos que fazem um repositório se manter sozinho. Nenhum deles é código, e todos evitam um tipo de incidente."},
 {"code": """dataforge devops github --dono=@minha-org/plataforma

  ✓ .github/workflows/release.yml
  ✓ .github/dependabot.yml
  ✓ .github/CODEOWNERS
  ✓ .github/pull_request_template.md
  ✓ .github/ISSUE_TEMPLATE/bug.yml""", "lang": "text"},

 {"table": {"head": ["Arquivo", "Evita"], "rows": [
   ["`dependabot.yml`", "a *action* e a imagem base que envelhecem sem ninguém ver"],
   ["`CODEOWNERS`", "a mudança no workflow — que muda o que chega à produção — sem revisão de quem responde por ele"],
   ["`pull_request_template.md`", "o PR que não diz o que muda nem como foi conferido"],
   ["`ISSUE_TEMPLATE/bug.yml`", "o bug sem versão e sem o programa que reproduz"]]}},

 {"callout": {"tipo": "atencao", "titulo": "O Dependabot não lê o `forge.toml`", "texto": "Ele não conhece o ecossistema do DataForge, e o arquivo gerado diz isso num comentário — melhor que esperar um PR de atualização que nunca vai chegar. Para as dependências DataForge, rode `dataforge outdated` num job agendado."}},

 {"h2": "Proteger o ramo principal"},
 {"p": "A proteção é configuração do GitHub, não arquivo — por isso o gerador não a escreve. O que ligar em *Settings → Branches*:"},
 {"table": {"head": ["Regra", "Porque"], "rows": [
   ["exigir o job `verificar` verde", "o CI que ninguém é obrigado a esperar é decoração"],
   ["exigir revisão dos `CODEOWNERS`", "é o que dá dentes ao arquivo"],
   ["proibir `push --force`", "o histórico que alguém reescreveu não tem como ser auditado"],
   ["exigir o ramo atualizado", "dois PRs verdes separados podem ser vermelhos juntos"]]}},

 {"p": "Continue em [GitLab CI](/docs/devops/gitlab)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/gitlab",
"title": "GitLab CI",
"description": "O mesmo pipeline no GitLab, com o relatório JUnit na página do merge request.",
"blocos": [
 {"p": "`dataforge devops ci gitlab` escreve `.gitlab-ci.yml`. Os comandos são os mesmos do GitHub — a ordem do custo não muda de plataforma —, e o relatório JUnit do Crucible vai em `artifacts.reports.junit`, que é o que faz o GitLab listar os testes que falharam **na página do merge request**."},
 {"code": """dataforge devops ci gitlab
git add .gitlab-ci.yml && git commit -m "CI no GitLab\"""", "lang": "bash"},
 {"code": """verificar:
  stage: verificar
  script:
    - pip install dataforge-lang
    - dataforge fmt . --check
    - dataforge check . --strict
    - dataforge lint .
    - dataforge test --minimo=70
    - dataforge crucible --formato=junit --saida=relatorio.xml || true
  artifacts:
    when: always
    reports:
      junit: relatorio.xml""", "lang": "yaml"},

 {"table": {"head": ["No arquivo", "Sem ele"], "rows": [
   ["`when: always` nos artefatos", "o relatório só é guardado quando tudo passa — e é quando falha que ele importa"],
   ["cache de `pip` e `forge_modules`", "cada job baixa tudo de novo"],
   ["`|| true` no JUnit", "o `crucible` reprovado impediria o relatório de ser publicado; quem reprova é o `test` acima"]]}},

 {"callout": {"tipo": "nota", "titulo": "E os outros CIs", "texto": "Jenkins, CircleCI, Azure Pipelines e Bitbucket rodam os mesmos cinco comandos. `dataforge devops ci <outro>` imprime a lista, em vez de gerar um arquivo que ninguém aqui conferiu — um artefato não testado para uma plataforma é pior que nenhum."}},

 {"p": "Continue em [Ambiente de desenvolvimento](/docs/devops/ambiente-de-dev)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/ambiente-de-dev",
"title": "Ambiente de desenvolvimento",
"description": "Devcontainer para Codespaces e VS Code, e os ganchos do pre-commit que rodam o CI antes do commit.",
"blocos": [
 {"p": "O defeito mais caro de um projeto novo é o *“na minha máquina funciona”*. Duas peças o reduzem: um contêiner de desenvolvimento, igual para todos, e ganchos que rodam o que o CI roda **antes** do commit — onde consertar custa segundos, e não um ciclo inteiro de revisão."},

 {"h2": "Devcontainer"},
 {"code": """dataforge devops devcontainer
# .devcontainer/devcontainer.json — abra no VS Code ("Reopen in Container")
# ou num Codespace, e a linguagem, a extensao e as dependencias ja estao la""", "lang": "bash"},
 {"code": """{
  "name": "loja",
  "image": "mcr.microsoft.com/devcontainers/python:3.13",
  "postCreateCommand": "pip install dataforge-lang && dataforge editor && dataforge install",
  "forwardPorts": [8080]
}""", "lang": "json"},
 {"p": "A extensão é instalada por `dataforge editor`, e não por id do marketplace: ela vem **no pacote**, na mesma versão da linguagem. Um id do marketplace instalaria a última, que pode não concordar com a linguagem instalada."},

 {"h2": "pre-commit"},
 {"code": """dataforge devops pre-commit
pip install pre-commit
pre-commit install          # a partir daqui, todo commit roda os ganchos""", "lang": "bash"},
 {"table": {"head": ["Gancho", "O que para"], "rows": [
   ["`dataforge fmt`", "o diff de formatação no meio do diff de lógica"],
   ["`dataforge check --strict`", "o nome errado que só apareceria no CI, dez minutos depois"],
   ["`dataforge seguranca`", "o token colado no código — o único erro que não se desfaz com outro commit"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Um segredo commitado é um segredo vazado", "texto": "Apagar o arquivo no commit seguinte não o tira do histórico, e um repositório público é espelhado em minutos. O gancho de segurança é o único que roda **antes** — depois, a única resposta é rotacionar a credencial."}},

 {"p": "Continue em [Numa VM](/docs/devops/vm)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/devops/vm",
"title": "Numa VM, sem contêiner",
"description": "A unidade systemd endurecida, o nginx na frente com TLS — e o que o Kiln não faz sozinho.",
"blocos": [
 {"p": "Nem todo serviço precisa de um cluster. Uma VM pequena com systemd e nginx atende a maioria dos projetos — e tem menos peças para quebrar. `dataforge devops systemd` e `dataforge devops nginx` escrevem as duas."},
 {"code": """dataforge devops systemd --usuario=loja
dataforge devops nginx --dominio=loja.exemplo.com

sudo useradd --system --home /srv/loja loja
sudo cp loja.service /etc/systemd/system/
sudo systemctl enable --now loja
sudo cp deploy/nginx.conf /etc/nginx/sites-enabled/loja
sudo certbot --nginx -d loja.exemplo.com""", "lang": "bash"},

 {"h2": "O endurecimento da unidade"},
 {"table": {"head": ["Diretiva", "O que ela contém"], "rows": [
   ["`User=` sem privilégio", "a aplicação comprometida não é root"],
   ["`NoNewPrivileges=true`", "nem um binário *setuid* devolve o root"],
   ["`ProtectSystem=strict`", "o sistema de arquivos inteiro é somente-leitura…"],
   ["`ReadWritePaths=/srv/app/dados`", "…menos a pasta de dados, que é a única que ela escreve"],
   ["`ProtectHome` / `PrivateTmp`", "as pastas dos usuários somem, e o `/tmp` é só dela"],
   ["`Restart=on-failure`", "a queda às 3h volta sozinha, e o log diz por quê"]]}},

 {"h2": "Por que o nginx na frente"},
 {"p": "O Kiln roda sobre o `http.server` do Python: não tem **HTTP/2 nem TLS**. Em produção pública, o nginx (ou Caddy) termina o TLS, serve os estáticos, limita o corpo e repassa para o Kiln em `127.0.0.1`. O gerador já escreve o repasse de WebSocket e de SSE — sem os cabeçalhos de `Upgrade`, o tempo real para de funcionar atrás do proxy."},

 {"callout": {"tipo": "dica", "titulo": "Confira antes de subir", "texto": "`dataforge devops doctor` lê o projeto — sem executá-lo — e diz o que falta: porta, variáveis de ambiente, `0.0.0.0`, banco sem sonda. Ele funciona num projeto que não compila, que é quando ele é mais útil."}},

 {"p": "Volte para [DevOps](/docs/devops) ou veja [Observabilidade](/docs/tecnicas/observar)."},
]},
]
