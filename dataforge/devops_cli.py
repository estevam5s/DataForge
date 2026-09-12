# -*- coding: utf-8 -*-
"""'dataforge devops <o que>' — escreve os artefatos.

O que este arquivo decide, e 'devops.py' nao
--------------------------------------------
'devops.py' produz TEXTO; este escreve ARQUIVO. A separacao importa por
dois motivos: os geradores ficam testaveis sem tocar em disco, e a
politica de "o que fazer quando o arquivo ja existe" mora num lugar so.

E a politica e: **nunca sobrescrever em silencio.** Um Dockerfile
ajustado a mao ao longo de seis meses nao pode ser apagado por alguem
que digitou o comando para ver o que ele faz. Sem '--forcar', o arquivo
existente e PULADO, e o relatorio diz isso.
"""

import os
import shutil

from . import devops as g

#: Os grupos, e o que cada um escreve. A ordem e a do relatorio.
GRUPOS = ("docker", "ci", "k8s", "helm", "terraform", "nginx", "observar",
          "sbom", "secrets")


def executar(args, flags):
    """Ponto de entrada. Devolve o codigo de saida."""
    from .cli import color

    sub = args[0] if args else "init"
    resto = args[1:]
    forcar = "--forcar" in flags or "--force" in flags
    seco = "--dry-run" in flags or "--seco" in flags

    projeto = g.Projeto(_flag(flags, "--em", "."))

    if sub in ("init", "tudo"):
        return _init(projeto, forcar, seco, flags)
    if sub == "docker":
        return _escrever_grupo(projeto, _docker(projeto, resto, flags),
                               forcar, seco, "docker")
    if sub in ("ci", "pipeline"):
        return _escrever_grupo(projeto, _ci(projeto, resto), forcar, seco, "ci")
    if sub in ("k8s", "kubernetes"):
        return _escrever_grupo(projeto, _k8s(projeto, flags), forcar, seco,
                               "kubernetes")
    if sub == "helm":
        return _escrever_grupo(projeto, _helm(projeto, flags), forcar, seco,
                               "helm")
    if sub == "terraform":
        return _escrever_grupo(projeto, _terraform(projeto), forcar, seco,
                               "terraform")
    if sub == "nginx":
        return _escrever_grupo(projeto, _nginx(projeto, flags), forcar, seco,
                               "nginx")
    if sub in ("observar", "observabilidade", "observe"):
        return _escrever_grupo(projeto, _observar(projeto), forcar, seco,
                               "observabilidade")
    if sub == "sbom":
        return _escrever_grupo(projeto, {"sbom.json": g.sbom(projeto)},
                               forcar, seco, "sbom")
    if sub in ("secrets", "segredos"):
        return _secrets(projeto, forcar, seco)
    if sub == "doctor":
        return _doctor(projeto)

    print(color(f"  nao conheco 'devops {sub}'.", "1;31"))
    print()
    print(_uso())
    return 1


def _uso():
    return (
        "  uso: dataforge devops <o que>\n\n"
        "    init            tudo o que faz sentido para este projeto\n"
        "    docker          Dockerfile, .dockerignore, docker-compose.yml\n"
        "    ci github       .github/workflows/ci.yml\n"
        "    k8s             deployment, service, ingress, configmap, hpa\n"
        "    helm            um chart\n"
        "    terraform       o esqueleto\n"
        "    nginx           proxy reverso com TLS, WebSocket e SSE\n"
        "    observar        Prometheus, Grafana e OpenTelemetry\n"
        "    sbom            o inventario, em CycloneDX\n"
        "    secrets         .env.example e o .gitignore\n"
        "    doctor          o que falta para este projeto subir\n\n"
        "    --forcar        sobrescreve o que ja existe\n"
        "    --seco          mostra o que faria, sem escrever\n"
        "    --registro=X    o registro das imagens\n"
        "    --dominio=X     o dominio, no ingress e no nginx\n"
        "    --em=<pasta>    o projeto (padrao: a pasta atual)\n")


# ═══════════════════════════════════════════════════════════
#  Os grupos
# ═══════════════════════════════════════════════════════════

def _docker(p, resto, flags):
    acao = resto[0] if resto else ""
    if acao == "build":
        return _rodar_docker(p, "build", flags)
    if acao == "run":
        return _rodar_docker(p, "run", flags)
    arquivos = {
        "Dockerfile": g.dockerfile(p),
        ".dockerignore": g.dockerignore(p),
        "docker-compose.yml": g.compose(p),
    }
    return arquivos


def _ci(p, resto):
    onde = (resto[0] if resto else "github").lower()
    if onde not in ("github", "gh"):
        from .cli import color
        print(color(f"  so sei gerar para o GitHub Actions, nao para "
                    f"'{onde}'.", "1;33"))
        print("  Os comandos sao os mesmos em qualquer CI:")
        print("    dataforge fmt . --check")
        print("    dataforge check . --strict")
        print("    dataforge test --minimo=70")
        return {}
    return {os.path.join(".github", "workflows", "ci.yml"): g.ci_github(p)}


def _k8s(p, flags):
    registro = _flag(flags, "--registro", "registry.example.com")
    dominio = _flag(flags, "--dominio", "")
    arquivos = {
        os.path.join("k8s", "deployment.yml"): g.k8s_deployment(p, registro),
        os.path.join("k8s", "service.yml"): g.k8s_service(p),
        os.path.join("k8s", "configmap.yml"): g.k8s_config(p),
    }
    if p.e_servidor:
        arquivos[os.path.join("k8s", "ingress.yml")] = g.k8s_ingress(p, dominio)
        arquivos[os.path.join("k8s", "hpa.yml")] = g.k8s_hpa(p)
    return arquivos


def _helm(p, flags):
    registro = _flag(flags, "--registro", "registry.example.com")
    return {
        os.path.join("helm", "Chart.yaml"): g.helm_chart(p),
        os.path.join("helm", "values.yaml"): g.helm_values(p, registro),
    }


def _terraform(p):
    return {os.path.join("terraform", "main.tf"): g.terraform(p)}


def _nginx(p, flags):
    dominio = _flag(flags, "--dominio", "")
    return {os.path.join("deploy", "nginx.conf"): g.nginx(p, dominio)}


def _observar(p):
    return {
        os.path.join("observar", "prometheus.yml"): g.prometheus(p),
        os.path.join("observar", "otel.yml"): g.otel(p),
        "docker-compose.observar.yml": g.compose_observar(p),
    }


def _secrets(p, forcar, seco):
    from .cli import color

    arquivos = {".env.example": g.env_exemplo(p)}
    codigo = _escrever_grupo(p, arquivos, forcar, seco, "segredos")

    # O .gitignore e ACRESCENTADO, nunca substituido: ele costuma ter
    # linhas que so quem escreveu conhece.
    alvo = os.path.join(p.raiz, ".gitignore")
    atual = ""
    if os.path.isfile(alvo):
        with open(alvo, encoding="utf-8") as f:
            atual = f.read()

    faltando = [l for l in g.GITIGNORE.strip().split("\n")
                if l.strip() and not l.startswith("#")
                and l.strip() not in atual]
    if not faltando:
        print(color("  ✓ .gitignore", "1;32")
              + color("  já cobre o que precisa", "0;90"))
    elif seco:
        print(color(f"  + .gitignore  ({len(faltando)} linha(s))", "1;36"))
    else:
        with open(alvo, "a", encoding="utf-8") as f:
            if atual and not atual.endswith("\n"):
                f.write("\n")
            f.write(g.GITIGNORE)
        print(color(f"  ✓ .gitignore", "1;32")
              + color(f"  {len(faltando)} linha(s) acrescentada(s)", "0;90"))

    print()
    print(color("  O que NUNCA vai para o repositório:", "1;33"))
    for linha in ("  .env e .env.*        — use .env.example para documentar",
                  "  *.pem, *.key         — chave privada",
                  "  o Secret do k8s      — aplique com 'kubectl create secret'",
                  "  senha no values.yaml — use 'existingSecret'"):
        print(color(linha, "0;90"))
    print()
    print(color("  Um segredo no histórico do git continua lá depois de "
                "apagado no arquivo.", "0;90"))
    print(color("  Se vazou: rotacione. Reescrever o histórico não basta —"
                " alguém já clonou.", "0;90"))
    return codigo


def _init(p, forcar, seco, flags):
    """Tudo o que faz sentido para ESTE projeto."""
    from .cli import color

    print()
    print(color(f"  ◆ {p.nome} {p.versao}", "1;33")
          + color(f"  ({p.resumo()})", "0;90"))
    print()

    arquivos = {}
    arquivos.update(_docker(p, [], flags))
    arquivos.update(_ci(p, ["github"]))
    arquivos.update({".env.example": g.env_exemplo(p)})
    if p.e_servidor:
        arquivos.update(_k8s(p, flags))
        arquivos.update(_nginx(p, flags))
    else:
        print(color("  (sem Kubernetes nem nginx: este projeto não é um "
                    "servidor)", "0;90"))
        print()

    codigo = _escrever_grupo(p, arquivos, forcar, seco, "")
    print()
    print(color("  Depois:", "1;36"))
    print("    dataforge devops doctor        o que falta para subir")
    if p.e_servidor:
        print(f"    docker build -t {p.slug} .")
        print("    dataforge devops observar      Prometheus e Grafana")
    print("    dataforge devops secrets       e o que não pode ir ao repo")
    return codigo


# ═══════════════════════════════════════════════════════════
#  Escrever
# ═══════════════════════════════════════════════════════════

def _escrever_grupo(p, arquivos, forcar, seco, titulo):
    from .cli import color

    if not arquivos:
        return 1
    if titulo:
        print()
        print(color(f"  {titulo}", "1;36"))
    escritos = pulados = 0
    for relativo, conteudo in sorted(arquivos.items()):
        alvo = os.path.join(p.raiz, relativo)
        existe = os.path.isfile(alvo)

        if existe and not forcar:
            # Um Dockerfile ajustado a mao ao longo de seis meses nao
            # pode ser apagado por quem digitou o comando so para ver o
            # que ele faz.
            print(color(f"  · {relativo}", "0;90")
                  + color("  já existe (--forcar sobrescreve)", "0;90"))
            pulados += 1
            continue

        if seco:
            linhas = conteudo.count("\n")
            print(color(f"  + {relativo}", "1;36")
                  + color(f"  {linhas} linha(s)", "0;90"))
            escritos += 1
            continue

        if existe:
            # Copia antes de sobrescrever: '--forcar' e explicito, mas a
            # pessoa ainda pode ter digitado no projeto errado.
            shutil.copy2(alvo, alvo + ".anterior")
        os.makedirs(os.path.dirname(alvo) or p.raiz, exist_ok=True)
        with open(alvo, "w", encoding="utf-8") as f:
            f.write(conteudo)
        marca = "  (o anterior ficou em .anterior)" if existe else ""
        print(color(f"  ✓ {relativo}", "1;32") + color(marca, "0;90"))
        escritos += 1

    if pulados and not seco:
        print()
        print(color(f"  {pulados} arquivo(s) preservado(s). "
                    f"Use --forcar para sobrescrever.", "0;90"))
    return 0


def _rodar_docker(p, acao, flags):
    """'devops docker build' e 'run' — atalhos, nao abstracao.

    Eles montam o comando e o EXIBEM antes de rodar, para quem quiser
    copiar. Esconder o 'docker build' faria a pessoa depender deste
    comando para sempre; mostrar ensina o que ele faz.
    """
    import subprocess

    from .cli import color

    if not os.path.isfile(os.path.join(p.raiz, "Dockerfile")):
        print(color("  não há Dockerfile aqui.", "1;31"))
        print("  crie um com:  dataforge devops docker")
        return 1

    tag = _flag(flags, "--tag", f"{p.slug}:{p.versao}")
    if acao == "build":
        comando = ["docker", "build", "-t", tag, "."]
    else:
        comando = ["docker", "run", "--rm", "-it"]
        if p.e_servidor:
            comando += ["-p", f"{p.porta}:{p.porta}"]
        comando.append(tag)

    print(color("  " + " ".join(comando), "0;90"))
    print()
    try:
        return subprocess.call(comando, cwd=p.raiz)
    except FileNotFoundError:
        print(color("  o 'docker' não está no PATH.", "1;31"))
        print("  instale o Docker, ou copie o comando acima.")
        return 1


# ═══════════════════════════════════════════════════════════
#  doctor
# ═══════════════════════════════════════════════════════════

def _doctor(p):
    """O que falta para este projeto subir.

    A ordem e da causa mais provavel para a menos, como o 'vitrine
    doctor'. Cada linha responde uma pergunta que alguem faria olhando
    um deploy que nao funciona.
    """
    from .cli import color

    print()
    print(color(f"  ◆ {p.nome} {p.versao}", "1;33")
          + color(f"  ({p.resumo()})", "0;90"))
    print()

    problemas = []

    def linha(rotulo, ok, detalhe="", conserto=""):
        marca = color("✓", "1;32") if ok else color("✗", "1;31")
        print(f"  {marca} {rotulo}"
              + (color(f"  {detalhe}", "0;90") if detalhe else ""))
        if not ok and conserto:
            problemas.append(conserto)

    def aviso(rotulo, detalhe=""):
        print(f"  {color('!', '1;33')} {rotulo}"
              + (color(f"  {detalhe}", '0;90') if detalhe else ""))

    # ── O projeto ──
    tem_manifesto = os.path.isfile(os.path.join(p.raiz, "forge.toml"))
    linha("há um forge.toml", tem_manifesto, "",
          "crie com 'dataforge init'")

    if p.entrada:
        existe = os.path.isfile(os.path.join(p.raiz, p.entrada))
        linha(f"a entrada existe ({p.entrada})", existe, "",
              f"a entrada do forge.toml aponta para '{p.entrada}', "
              f"que não existe")
    elif tem_manifesto:
        aviso("o forge.toml não declara 'entry'",
              "'dataforge run' sem argumento não saberá o que rodar")

    # ── O código roda? ──
    compila = _compila(p)
    linha("o código passa no 'check'", compila[0], compila[1],
          "rode 'dataforge check .' e corrija")

    # ── Dependência ──
    if p.dependencias:
        instalado = os.path.isdir(os.path.join(p.raiz, "forge_modules"))
        linha(f"as {len(p.dependencias)} dependências estão instaladas",
              instalado, "", "rode 'dataforge install'")
        tem_lock = os.path.isfile(os.path.join(p.raiz, "forge.lock"))
        linha("há forge.lock (build reproduzível)", tem_lock, "",
              "rode 'dataforge install' para gerar o lock, e versione-o")

    # ── Docker ──
    tem_docker = os.path.isfile(os.path.join(p.raiz, "Dockerfile"))
    linha("há Dockerfile", tem_docker, "",
          "gere com 'dataforge devops docker'")
    if tem_docker:
        conteudo = open(os.path.join(p.raiz, "Dockerfile"),
                        encoding="utf-8").read()
        linha("a imagem não roda como root", "USER " in conteudo, "",
              "acrescente 'USER' ao Dockerfile: um escape de container "
              "vira root no host")
        if p.e_servidor:
            linha("a imagem tem HEALTHCHECK", "HEALTHCHECK" in conteudo,
                  "", "sem ele, o orquestrador não sabe se a aplicação "
                      "está de pé")

    tem_ignore = os.path.isfile(os.path.join(p.raiz, ".dockerignore"))
    linha("há .dockerignore", tem_ignore, "",
          "sem ele, o '.env' entra na imagem — e continua nela depois "
          "de apagado numa camada seguinte")

    # ── Segredo ──
    vazando = _segredo_versionado(p)
    linha("nenhum segredo versionado", not vazando,
          ", ".join(vazando[:3]) if vazando else "",
          f"REMOVA do git e ROTACIONE: {', '.join(vazando[:3])}")

    tem_exemplo = os.path.isfile(os.path.join(p.raiz, ".env.example"))
    if not tem_exemplo and (p.usa_banco or p.usa_redis or p.e_servidor):
        aviso("não há .env.example",
              "cada pessoa nova descobre as variáveis por tentativa")

    # ── CI ──
    tem_ci = os.path.isdir(os.path.join(p.raiz, ".github", "workflows"))
    linha("há pipeline de CI", tem_ci, "",
          "gere com 'dataforge devops ci github'")

    # ── Teste ──
    tem_teste = any(
        os.path.isdir(os.path.join(p.raiz, d)) for d in ("tests", "testes"))
    linha("há testes", tem_teste, "",
          "sem teste, nada impede uma mudança de quebrar o que "
          "funcionava")

    # ── Produção ──
    if p.e_servidor:
        print()
        print(color("  Para produção:", "1;36"))
        for texto in (
            "há um proxy reverso na frente (TLS, compressão, HTTP/2)"
            if not os.path.isfile(os.path.join(p.raiz, "deploy", "nginx.conf"))
            else "o nginx.conf está gerado — confira o domínio e o certificado",
            "a sessão vive na memória do processo: UM processo por aplicação",
            "'V.configurar(\"producao\", yes)' esconde o stack trace da página"
            if p.usa_vitrine else
            "'Kiln.secure_headers()' como middleware de saída",
        ):
            print(color(f"    · {texto}", "0;90"))

    print()
    if problemas:
        print(color(f"  {len(problemas)} coisa(s) a resolver:", "1;33"))
        for i, conserto in enumerate(problemas, 1):
            print(f"    {i}. {conserto}")
        print()
        return 1
    print(color("  pronto para subir.", "1;32"))
    print()
    return 0


def _compila(p):
    """(ok, detalhe) — o 'check' sobre o projeto."""
    import subprocess
    import sys

    alvos = [d for d in ("src", ".") if os.path.isdir(os.path.join(p.raiz, d))]
    if not alvos:
        return True, "nada a conferir"
    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "check", alvos[0], "--no-color"],
        cwd=p.raiz, capture_output=True, text=True, encoding="utf-8")
    if saida.returncode == 0:
        return True, ""
    erros = [l for l in saida.stdout.splitlines() if ": erro:" in l]
    return False, f"{len(erros)} erro(s)" if erros else "não compila"


#: Os nomes que NAO podem estar versionados.
_PERIGOSOS = (".env", ".env.local", ".env.production", ".env.prod")


def _segredo_versionado(p):
    """Os segredos que o git conhece.

    Confere o git, e nao o disco: um '.env' no disco e normal e
    esperado; um '.env' RASTREADO e um segredo publicado. E a diferenca
    entre as duas coisas e o que faz este aviso valer a atenção.
    """
    import subprocess

    if not os.path.isdir(os.path.join(p.raiz, ".git")):
        return []
    try:
        saida = subprocess.run(["git", "ls-files"], cwd=p.raiz,
                               capture_output=True, text=True,
                               encoding="utf-8", timeout=10)
    except (OSError, subprocess.SubprocessError):
        return []
    achados = []
    for caminho in saida.stdout.splitlines():
        nome = os.path.basename(caminho)
        if nome in _PERIGOSOS or nome.endswith((".pem", ".key", ".p12")):
            achados.append(caminho)
    return achados


def _flag(flags, nome, padrao):
    for f in flags:
        if f.startswith(nome + "="):
            return f.split("=", 1)[1]
    return padrao
