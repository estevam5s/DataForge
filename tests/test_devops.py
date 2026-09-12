"""`dataforge devops` — os artefatos que levam um projeto ao ar.

A decisão de fundo: **gerar o artefato certo, e sair da frente.** Um
`dataforge deploy` que falasse com Docker e Kubernetes por dentro
esconderia o que a imagem é — e no dia em que alguém precisa mudar uma
camada, não haveria onde mexer. `docker build`, `kubectl apply` e
`helm upgrade` já existem, são maduros, e têm gente que os conhece.

O que estes testes protegem é que o artefato gerado seja o que se põe em
produção, e não um esboço:

| O quê | Sem ele |
|---|---|
| `USER` no Dockerfile | um escape de container vira root no host |
| o manifesto copiado antes do código | um commit numa linha reinstala tudo |
| `.env` no `.dockerignore` | o segredo fica na camada, e `docker history` o mostra |
| `resources` no Deployment | um pod come o nó inteiro |
| `readinessProbe` | o Service manda tráfego antes da hora |
| `depends_on: service_healthy` | a aplicação falha na primeira consulta |
| não sobrescrever em silêncio | seis meses de ajuste à mão apagados |
"""

import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, ".")

from dataforge import devops as g

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ═══════════════════════════════════════════════════════════
#  O que o projeto é
# ═══════════════════════════════════════════════════════════

def _projeto(tmp_path, fonte="", manifesto=None):
    (tmp_path / "forge.toml").write_text(
        manifesto or '[project]\nname = "meu-app"\nversion = "2.1.0"\n'
                     'entry = "src/main.df"\n', encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir(exist_ok=True)
    (src / "main.df").write_text(fonte or "out 1\n", encoding="utf-8")
    return g.Projeto(str(tmp_path))


def test_le_o_manifesto(tmp_path):
    p = _projeto(tmp_path)
    assert p.nome == "meu-app"
    assert p.versao == "2.1.0"
    assert p.entrada == "src/main.df"


def test_descobre_o_que_o_codigo_adota(tmp_path):
    """Os artefatos saem conforme isto: quem não usa banco não ganha um
    Postgres no compose, e um compose com serviço que ninguém usa é um
    compose que as pessoas param de ler."""
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(pagina)\n")
    assert p.usa_vitrine and p.e_servidor
    assert p.porta == g.PORTA_VITRINE

    outro = _projeto(tmp_path, "adopt Kiln\nserver app on 8080:\n"
                               "    route GET \"/\":\n        respond text \"oi\"\n")
    assert outro.usa_kiln and outro.porta == g.PORTA_KILN


def test_um_programa_comum_nao_e_servidor(tmp_path):
    p = _projeto(tmp_path, "out 1 + 1\n")
    assert not p.e_servidor


def test_le_as_fontes_mesmo_que_nao_compilem(tmp_path):
    """O `doctor` precisa funcionar num projeto que **não** compila — e é
    justamente aí que ele é mais útil."""
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nthis is not (valid\n")
    assert p.usa_vitrine


def test_o_slug_vira_nome_de_recurso(tmp_path):
    p = _projeto(tmp_path,
                 manifesto='[project]\nname = "Meu App! v2"\nversion = "1.0"\n')
    assert p.slug == "meu-app-v2"


# ═══════════════════════════════════════════════════════════
#  Dockerfile
# ═══════════════════════════════════════════════════════════

def test_a_imagem_nao_roda_como_root(tmp_path):
    """Um processo que roda como root num container tem capacidades que
    não precisa, e um escape vira root no host."""
    conteudo = g.dockerfile(_projeto(tmp_path))
    assert "USER forge" in conteudo
    assert "useradd" in conteudo


def test_o_manifesto_e_copiado_antes_do_codigo(tmp_path):
    """A camada de dependência só é refeita quando o `forge.toml` muda.
    Sem isso, um commit numa linha reinstala tudo."""
    conteudo = g.dockerfile(_projeto(tmp_path))
    posicao_manifesto = conteudo.index("COPY --chown=forge:forge forge.toml")
    posicao_codigo = conteudo.index("COPY --chown=forge:forge . .")
    assert posicao_manifesto < posicao_codigo


def test_duas_etapas(tmp_path):
    """A imagem final não carrega pip nem compilador."""
    conteudo = g.dockerfile(_projeto(tmp_path))
    assert conteudo.count("FROM ") == 2
    assert "AS construcao" in conteudo
    assert "COPY --from=construcao" in conteudo


def test_um_servidor_ganha_healthcheck_e_a_porta(tmp_path):
    conteudo = g.dockerfile(
        _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n"))
    assert "EXPOSE 8501" in conteudo
    assert "HEALTHCHECK" in conteudo
    assert "/__vitrine__/saude" in conteudo


def test_um_programa_comum_nao_ganha_healthcheck(tmp_path):
    conteudo = g.dockerfile(_projeto(tmp_path, "out 1\n"))
    assert "HEALTHCHECK" not in conteudo
    assert "EXPOSE" not in conteudo


def test_a_sonda_usa_o_proprio_python(tmp_path):
    """`curl` não está na imagem slim, e instalar 30 MB para uma sonda de
    200 bytes seria trocar tamanho por conveniência."""
    conteudo = g.dockerfile(
        _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n"))
    # Só as linhas de código: o comentário cita o 'curl' para explicar
    # por que ele NÃO é usado.
    codigo = [l for l in conteudo.splitlines() if not l.startswith("#")]
    assert not any("curl" in l for l in codigo)
    assert "urllib.request" in conteudo


def test_a_sonda_do_healthcheck_realmente_funciona(tmp_path):
    """O comando do HEALTHCHECK é extraído do Dockerfile gerado e
    executado contra uma Vitrine de verdade.

    Um HEALTHCHECK que não funciona é pior que nenhum: o orquestrador
    reinicia um container saudável, em laço.
    """
    import re
    import time
    import urllib.error
    import urllib.request

    from dataforge.stdlib.vitrine.api import ArcaneVitrine, _ATUAL

    _ATUAL["app"] = None
    V = ArcaneVitrine()
    V["app"]("sonda")
    V["pagina"]("/", lambda: V["titulo"]("x"))
    porta = V["servir"](0)
    try:
        conteudo = g.dockerfile(
            _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n"))
        comando = re.search(r'CMD python -c "(.+?)"\n', conteudo,
                            re.S).group(1)
        # A porta do Dockerfile é fixa; a do teste, sorteada.
        comando = comando.replace(":8501", f":{porta}")
        saida = subprocess.run([sys.executable, "-c", comando],
                               capture_output=True, text=True,
                               encoding="utf-8", timeout=20)
        assert saida.returncode == 0, saida.stderr
    finally:
        V["parar_servidor"]()


def test_o_comando_casa_com_o_framework(tmp_path):
    vitrine = g.Projeto.__new__(g.Projeto)
    vitrine.usa_vitrine = True
    vitrine.entrada = "src/main.df"
    assert vitrine.comando == ["dataforge", "vitrine", "run", "--host=0.0.0.0"]

    comum = g.Projeto.__new__(g.Projeto)
    comum.usa_vitrine = False
    comum.entrada = "app.df"
    assert comum.comando == ["dataforge", "run", "app.df"]


# ═══════════════════════════════════════════════════════════
#  .dockerignore
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("perigoso", [".env", "*.pem", "*.key", "secrets/"])
def test_o_segredo_fica_fora_da_imagem(tmp_path, perigoso):
    """Um segredo copiado para uma camada continua nela depois de apagado
    numa camada seguinte — `docker history` o mostra."""
    assert perigoso in g.dockerignore(_projeto(tmp_path))


def test_o_que_e_reconstruivel_fica_fora(tmp_path):
    conteudo = g.dockerignore(_projeto(tmp_path))
    for nome in ("forge_modules/", "__pycache__/", "node_modules/", ".venv/"):
        assert nome in conteudo


# ═══════════════════════════════════════════════════════════
#  Compose
# ═══════════════════════════════════════════════════════════

def test_o_compose_e_valido_para_o_docker(tmp_path):
    """Validado pelo próprio Docker, e não por um parser de YAML: o
    `docker compose config` cobra o esquema, não só a sintaxe."""
    if not _tem("docker"):
        pytest.skip("docker não está no PATH")
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nadopt Arcane.Database\n"
                           "V.rodar(p)\n")
    (tmp_path / "docker-compose.yml").write_text(g.compose(p),
                                                 encoding="utf-8")
    (tmp_path / "Dockerfile").write_text(g.dockerfile(p), encoding="utf-8")
    saida = subprocess.run(["docker", "compose", "config"], cwd=tmp_path,
                           capture_output=True, text=True,
                           encoding="utf-8", timeout=60)
    if "Cannot connect to the Docker daemon" in saida.stderr:
        pytest.skip("o daemon do Docker não está rodando")
    assert saida.returncode == 0, saida.stderr


def test_o_servico_de_apoio_sai_do_que_o_codigo_usa(tmp_path):
    sem = g.compose(_projeto(tmp_path, "out 1\n"))
    assert "postgres" not in sem
    assert "redis" not in sem

    com = g.compose(_projeto(tmp_path, "adopt Arcane.Database as Banco\n"
                                       "db := Banco.memory()\n"))
    assert "postgres:16-alpine" in com


def test_espera_a_sonda_e_nao_so_o_container(tmp_path):
    """O Postgres aceita conexão segundos depois de o container subir, e
    sem esperar a sonda a aplicação falha na primeira consulta — de forma
    intermitente, que é a pior."""
    conteudo = g.compose(_projeto(tmp_path,
                                  "adopt Arcane.Database as Banco\n"))
    assert "service_healthy" in conteudo
    assert "pg_isready" in conteudo


def test_a_senha_de_desenvolvimento_esta_marcada_como_tal(tmp_path):
    """Um leitor apressado copia o compose para produção, e precisa topar
    com o aviso."""
    conteudo = g.compose(_projeto(tmp_path, "adopt Arcane.Database\n"))
    assert "DESENVOLVIMENTO" in conteudo


# ═══════════════════════════════════════════════════════════
#  Kubernetes
# ═══════════════════════════════════════════════════════════

def _carregar(texto):
    """O YAML como dado, para conferir estrutura e não texto."""
    yaml = pytest.importorskip("yaml", reason="pyyaml ausente")
    return yaml.safe_load(texto)


@pytest.mark.parametrize("gerador", ["k8s_deployment", "k8s_service",
                                     "k8s_ingress", "k8s_config", "k8s_hpa"])
def test_o_manifesto_e_yaml_valido(tmp_path, gerador):
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    documento = _carregar(getattr(g, gerador)(p))
    assert documento["kind"]
    # O ConfigMap e o Secret levam sufixo: eles são recursos auxiliares
    # do mesmo app, e o nome precisa distingui-los.
    assert documento["metadata"]["name"].startswith(p.slug)


def test_o_deployment_tem_o_que_um_cluster_cobra(tmp_path):
    """As quatro coisas que quase todo exemplo de Deployment omite, e que
    são a diferença entre funcionar e ficar de pé."""
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    doc = _carregar(g.k8s_deployment(p))
    container = doc["spec"]["template"]["spec"]["containers"][0]

    # Sem limite, um pod come o nó inteiro e derruba os vizinhos.
    assert container["resources"]["requests"]["cpu"]
    assert container["resources"]["limits"]["memory"]

    # Sem readiness, o Service manda tráfego antes da hora.
    assert container["readinessProbe"]["httpGet"]["path"]
    # Sem liveness, um processo travado continua recebendo pedido.
    assert container["livenessProbe"]["httpGet"]["path"]

    # Sem securityContext, o container roda como root.
    assert doc["spec"]["template"]["spec"]["securityContext"]["runAsNonRoot"]
    assert container["securityContext"]["readOnlyRootFilesystem"] is True
    assert container["securityContext"]["capabilities"]["drop"] == ["ALL"]


def test_o_prazo_do_liveness_e_maior_que_o_do_readiness(tmp_path):
    """Matar um processo que está só lento piora tudo."""
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    container = (_carregar(g.k8s_deployment(p))
                 ["spec"]["template"]["spec"]["containers"][0])
    assert (container["livenessProbe"]["initialDelaySeconds"]
            > container["readinessProbe"]["initialDelaySeconds"])


def test_o_readonly_vem_com_um_tmp_gravavel(tmp_path):
    """Com `readOnlyRootFilesystem`, o processo ainda precisa de /tmp."""
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    doc = _carregar(g.k8s_deployment(p))
    volumes = {v["name"] for v in doc["spec"]["template"]["spec"]["volumes"]}
    assert "tmp" in volumes


def test_a_atualizacao_nao_derruba_capacidade(tmp_path):
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    estrategia = (_carregar(g.k8s_deployment(p))
                  ["spec"]["strategy"]["rollingUpdate"])
    assert estrategia["maxUnavailable"] == 0


def test_a_vitrine_ganha_afinidade_de_sessao(tmp_path):
    """A sessão vive na memória do processo: sem afinidade, dois pedidos
    da mesma pessoa caem em pods diferentes e a sessão se perde."""
    vitrine = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    assert _carregar(g.k8s_service(vitrine))["spec"]["sessionAffinity"] \
        == "ClientIP"

    kiln = _projeto(tmp_path, "adopt Kiln\nserver app on 8080:\n"
                              "    route GET \"/\":\n        respond text \"x\"\n")
    assert "sessionAffinity" not in _carregar(g.k8s_service(kiln))["spec"]


def test_o_ingress_nao_corta_sse_nem_websocket(tmp_path):
    """Sem estes dois tempos, uma conexão é cortada em 60 segundos."""
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    anotacoes = _carregar(g.k8s_ingress(p))["metadata"]["annotations"]
    assert anotacoes["nginx.ingress.kubernetes.io/proxy-read-timeout"] == "3600"
    assert anotacoes["nginx.ingress.kubernetes.io/proxy-send-timeout"] == "3600"


def test_o_hpa_sobe_rapido_e_desce_devagar(tmp_path):
    """Um pico atendido a menos custa usuário; um pod a mais por cinco
    minutos custa centavos."""
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    comportamento = _carregar(g.k8s_hpa(p))["spec"]["behavior"]
    assert (comportamento["scaleDown"]["stabilizationWindowSeconds"]
            > comportamento["scaleUp"]["stabilizationWindowSeconds"])


# ═══════════════════════════════════════════════════════════
#  CI
# ═══════════════════════════════════════════════════════════

def test_o_pipeline_e_yaml_valido_e_tem_os_passos(tmp_path):
    p = _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    doc = _carregar(g.ci_github(p))
    passos = doc["jobs"]["verificar"]["steps"]
    comandos = " ".join(str(passo.get("run", "")) for passo in passos)
    for esperado in ("dataforge fmt", "dataforge check", "dataforge test"):
        assert esperado in comandos


def test_o_check_vem_antes_dos_testes(tmp_path):
    """Ele acha nome errado, aridade errada e ciclo de import em menos de
    um segundo, e falhar ali poupa os minutos da suíte."""
    p = _projeto(tmp_path)
    conteudo = g.ci_github(p)
    assert conteudo.index("dataforge check") < conteudo.index("dataforge test")


def test_um_push_novo_cancela_o_anterior(tmp_path):
    doc = _carregar(g.ci_github(_projeto(tmp_path)))
    assert doc["concurrency"]["cancel-in-progress"] is True


def test_um_servidor_ganha_o_job_da_imagem(tmp_path):
    servidor = g.ci_github(
        _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n"))
    assert "docker build" in servidor
    assert "nao roda como root" in servidor

    comum = g.ci_github(_projeto(tmp_path, "out 1\n"))
    assert "docker build" not in comum


def test_a_sonda_da_ci_tem_prazo_e_nao_sleep_fixo(tmp_path):
    """Um `sleep 5` fixo falha na máquina lenta e desperdiça tempo na
    rápida."""
    conteudo = g.ci_github(
        _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n"))
    assert "seq 30" in conteudo


# ═══════════════════════════════════════════════════════════
#  SBOM e segredos
# ═══════════════════════════════════════════════════════════

def test_o_sbom_e_cyclonedx_valido(tmp_path):
    p = _projeto(tmp_path, manifesto='[project]\nname = "app"\n'
                                     'version = "1.2.3"\n\n'
                                     '[dependencies]\nvalidador = "^1.0.0"\n')
    doc = json.loads(g.sbom(p))
    assert doc["bomFormat"] == "CycloneDX"
    assert doc["metadata"]["component"]["version"] == "1.2.3"
    nomes = {c["name"] for c in doc["components"]}
    assert "dataforge-lang" in nomes
    assert "validador" in nomes


def test_o_sbom_diz_que_o_runtime_nao_tem_dependencia(tmp_path):
    """A ausência precisa ser explícita, senão parece descuido."""
    doc = json.loads(g.sbom(_projeto(tmp_path)))
    runtime = next(c for c in doc["components"]
                   if c["name"] == "dataforge-lang")
    assert "sem dependencia" in runtime["description"]


def test_o_env_exemplo_documenta_sem_vazar(tmp_path):
    p = _projeto(tmp_path, "adopt Arcane.Database as Banco\n"
                           "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    conteudo = g.env_exemplo(p)
    assert "DATABASE_URL" in conteudo
    assert "troque-isto" in conteudo
    # E ele diz que vai para o repositório, ao contrário do '.env'.
    assert "vai para o repositorio" in conteudo


def test_o_gitignore_cobre_o_que_nunca_pode_subir():
    for nome in (".env", "*.pem", "*.key", "*.db", "forge_modules/"):
        assert nome in g.GITIGNORE


# ═══════════════════════════════════════════════════════════
#  Escrever no disco
# ═══════════════════════════════════════════════════════════

def _cli(pasta, *args):
    return subprocess.run(
        [sys.executable, "-m", "dataforge", "devops", "--no-color", *args],
        cwd=pasta, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": RAIZ}, timeout=120)


def test_init_escreve_os_artefatos(tmp_path):
    _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    saida = _cli(tmp_path, "init")
    assert saida.returncode == 0, saida.stdout + saida.stderr
    for relativo in ("Dockerfile", ".dockerignore", "docker-compose.yml",
                     ".env.example", ".github/workflows/ci.yml",
                     "k8s/deployment.yml", "k8s/service.yml",
                     "deploy/nginx.conf"):
        assert (tmp_path / relativo).is_file(), relativo


def test_um_programa_comum_nao_ganha_k8s(tmp_path):
    _projeto(tmp_path, "out 1\n")
    _cli(tmp_path, "init")
    assert (tmp_path / "Dockerfile").is_file()
    assert not (tmp_path / "k8s").exists()


def test_nunca_sobrescreve_em_silencio(tmp_path):
    """Um Dockerfile ajustado à mão ao longo de seis meses não pode ser
    apagado por quem digitou o comando só para ver o que ele faz."""
    _projeto(tmp_path)
    (tmp_path / "Dockerfile").write_text("# MEU, ajustado à mão\n",
                                         encoding="utf-8")
    saida = _cli(tmp_path, "docker")
    assert "já existe" in saida.stdout
    assert (tmp_path / "Dockerfile").read_text(encoding="utf-8") == \
        "# MEU, ajustado à mão\n"


def test_forcar_guarda_o_anterior(tmp_path):
    """`--forcar` é explícito, mas a pessoa ainda pode ter digitado no
    projeto errado."""
    _projeto(tmp_path)
    (tmp_path / "Dockerfile").write_text("# MEU\n", encoding="utf-8")
    _cli(tmp_path, "docker", "--forcar")
    assert "FROM" in (tmp_path / "Dockerfile").read_text(encoding="utf-8")
    assert (tmp_path / "Dockerfile.anterior").read_text(
        encoding="utf-8") == "# MEU\n"


def test_seco_nao_escreve_nada(tmp_path):
    _projeto(tmp_path)
    saida = _cli(tmp_path, "docker", "--seco")
    assert "Dockerfile" in saida.stdout
    assert not (tmp_path / "Dockerfile").exists()


def test_o_gitignore_e_acrescentado_nao_substituido(tmp_path):
    """Ele costuma ter linhas que só quem escreveu conhece."""
    _projeto(tmp_path)
    (tmp_path / ".gitignore").write_text("# meu\nmeu-diretorio/\n",
                                         encoding="utf-8")
    _cli(tmp_path, "secrets")
    conteudo = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "meu-diretorio/" in conteudo
    assert ".env" in conteudo


def test_o_registro_e_o_dominio_chegam_nos_manifestos(tmp_path):
    _projeto(tmp_path, "adopt Arcane.Vitrine as V\nV.rodar(p)\n")
    _cli(tmp_path, "k8s", "--registro=reg.exemplo.br",
         "--dominio=app.exemplo.br")
    deployment = (tmp_path / "k8s" / "deployment.yml").read_text(
        encoding="utf-8")
    ingress = (tmp_path / "k8s" / "ingress.yml").read_text(encoding="utf-8")
    assert "reg.exemplo.br" in deployment
    assert "app.exemplo.br" in ingress


# ═══════════════════════════════════════════════════════════
#  doctor
# ═══════════════════════════════════════════════════════════

def test_o_doctor_aprova_um_projeto_pronto(tmp_path):
    _projeto(tmp_path, "adopt Arcane.Vitrine as V\n\n"
                       "action pagina():\n    V.titulo(\"x\")\n\n"
                       "V.rodar(pagina)\n")
    (tmp_path / "tests").mkdir()
    _cli(tmp_path, "init")
    saida = _cli(tmp_path, "doctor")
    assert saida.returncode == 0, saida.stdout
    assert "pronto para subir" in saida.stdout


def test_o_doctor_acusa_o_que_falta(tmp_path):
    _projeto(tmp_path, "out 1\n")
    saida = _cli(tmp_path, "doctor")
    assert saida.returncode == 1
    assert "há Dockerfile" in saida.stdout
    assert "coisa(s) a resolver" in saida.stdout


def test_o_doctor_acha_o_segredo_versionado(tmp_path):
    """Confere o **git**, e não o disco: um `.env` no disco é normal; um
    `.env` rastreado é um segredo publicado."""
    _projeto(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, timeout=30)
    (tmp_path / ".env").write_text("SENHA=secreta\n", encoding="utf-8")
    subprocess.run(["git", "add", "-f", ".env"], cwd=tmp_path, timeout=30)

    saida = _cli(tmp_path, "doctor")
    assert "nenhum segredo versionado" in saida.stdout
    assert "ROTACIONE" in saida.stdout


def test_um_env_nao_rastreado_nao_e_acusado(tmp_path):
    """A diferença entre as duas coisas é o que faz o aviso valer a
    atenção."""
    _projeto(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, timeout=30)
    (tmp_path / ".env").write_text("SENHA=x\n", encoding="utf-8")
    saida = _cli(tmp_path, "doctor")
    assert "ROTACIONE" not in saida.stdout


def test_o_doctor_nao_estoura_fora_de_um_projeto(tmp_path):
    saida = _cli(tmp_path, "doctor")
    assert "Traceback" not in saida.stdout + saida.stderr


# ═══════════════════════════════════════════════════════════
#  O YAML sem biblioteca
# ═══════════════════════════════════════════════════════════

def test_yes_e_no_sao_citados():
    """Em YAML 1.1, `yes` e `no` são booleanos: um valor assim sem aspas
    muda de tipo sozinho."""
    assert g._escalar("yes") == '"yes"'
    assert g._escalar("no") == '"no"'
    assert g._escalar("null") == '"null"'


def test_um_numero_em_texto_e_citado():
    """`8501` sem aspas é um número em YAML, e uma porta que deveria ser
    texto viraria inteiro no lugar errado."""
    assert g._escalar(8501) == "8501"
    assert g._escalar(True) == "true"


def test_dois_pontos_e_espaco_e_citado():
    assert g._escalar("chave: valor").startswith('"')


def _tem(programa):
    import shutil
    return shutil.which(programa) is not None


# ═══════════════════════════════════════════════════════════
#  O README do Docker Hub
# ═══════════════════════════════════════════════════════════
#
# Ele é a primeira coisa que alguém lê sobre a linguagem, e o Hub não
# o valida: um comando errado ali fica errado até alguém reclamar.

README_DOCKER = os.path.join(RAIZ, "docker", "README.md")


@pytest.fixture(scope="module")
def readme():
    if not os.path.isfile(README_DOCKER):
        pytest.skip("docker/README.md ausente")
    return open(README_DOCKER, encoding="utf-8").read()


def test_o_readme_traz_o_logo_da_linguagem(readme):
    assert "marca-256.png" in readme
    assert "dataforge-lang.vercel.app" in readme


def test_os_numeros_do_readme_batem_com_a_realidade(readme):
    """Um README que diz "38 módulos" quando são 40 é um README que
    ninguém confia na segunda leitura."""
    import re

    from dataforge.cli import COMANDOS
    from dataforge.stdlib import get_module, list_modules

    oficiais = {get_module(m)["__name__"] for m in list_modules()}
    simbolos = sum(len([k for k in get_module(n) if not k.startswith("__")])
                   for n in oficiais)
    comandos = len({c.nome for c in COMANDOS.values()})

    # O número vem antes do rótulo no texto corrido ("38 módulos") e
    # depois dele na tabela ("| **Comandos** | 44, …"). As duas formas
    # são aceitas: exigir uma faria o teste quebrar por causa de uma
    # reescrita que não mudou fato nenhum.
    reais = {
        "módulos": len(oficiais),
        "símbolos": simbolos,
        "Comandos": comandos,
    }
    for rotulo, quantos in reais.items():
        antes = re.search(rf"(\d+)[^\n\d]{{0,12}}{rotulo}", readme)
        depois = re.search(rf"{rotulo}\**\s*\|\s*(\d+)", readme)
        achado = antes or depois
        assert achado, f"o README não cita mais '{rotulo}'"
        assert int(achado.group(1)) == quantos, (
            f"o README diz {achado.group(1)} {rotulo}, são {quantos}")


def test_o_readme_avisa_do_host_no_container(readme):
    """É o erro mais comum ao pôr um servidor DataForge em Docker, e o
    sintoma é enganoso: o log diz "no ar" e o `curl` de fora não recebe
    nada."""
    assert "--host=0.0.0.0" in readme
    assert 'at "0.0.0.0"' in readme, (
        "o 'ignite' do Kiln também precisa do host; sem isso o exemplo "
        "do README não responde de fora do container")


def test_todo_bloco_dataforge_do_readme_compila(readme):
    """O mesmo tratamento que a documentação do site recebe."""
    import re

    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    falhas = []
    for bloco in re.findall(r"```dataforge\n(.*?)```", readme, re.S):
        if "…" in bloco or "..." in bloco:
            continue
        try:
            parse(tokenize(bloco, "readme"), "readme")
        except Exception as erro:
            # Fragmento de rota: envolve num 'server', como o
            # verificador de docs do site faz.
            try:
                dentro = "\n".join("    " + l for l in bloco.split("\n"))
                parse(tokenize("server app on 8080:\n" + dentro, "r"), "r")
            except Exception:
                falhas.append((bloco.strip().split("\n")[0][:50], str(erro)))
    assert not falhas, "blocos que não compilam:\n" + "\n".join(
        f"  {primeiro}: {e.splitlines()[0][:70]}" for primeiro, e in falhas)


def test_a_tag_recomendada_e_a_versao_da_linguagem(readme):
    """O README mandava usar `1.0.0`, e a imagem publicada era a
    `4.2.0` — a numeração antiga do projeto. Um `docker pull` da tag
    recomendada falharia."""
    from dataforge import __version__

    assert f"`{__version__}` | fixa" in readme, (
        f"o README precisa recomendar a tag {__version__}, que é a "
        f"versão da linguagem")


def test_o_readme_nao_promete_o_que_o_kiln_nao_tem(readme):
    """Ele roda sobre o `http.server`: sem TLS, HTTP/2 nem compressão."""
    assert "proxy reverso na frente" in readme
    assert "não há TLS" in readme


def test_a_imagem_do_repositorio_nao_roda_como_root():
    """O Dockerfile versionado — não a imagem publicada, que este teste
    não pode baixar."""
    conteudo = open(os.path.join(RAIZ, "Dockerfile"),
                    encoding="utf-8").read()
    assert "USER forge" in conteudo
    assert "useradd" in conteudo
