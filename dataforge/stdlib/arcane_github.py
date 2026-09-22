# -*- coding: utf-8 -*-
"""Arcane.GitHub — o que um programa precisa para viver no GitHub.

Três frentes, e cada uma tem um defeito clássico que o módulo existe
para evitar:

**Actions.** Um passo de workflow conversa com o executor por arquivos
(`GITHUB_OUTPUT`, `GITHUB_ENV`, `GITHUB_STEP_SUMMARY`) e por linhas
mágicas na saída (`::error file=…::`). Escrever isso à mão erra de dois
jeitos calados: uma saída com quebra de linha vira **duas** saídas (ou
injeta uma variável), e uma mensagem com `%` ou `\\n` é cortada no
meio. Aqui o valor multilinha usa delimitador aleatório, e a anotação
é escapada como o toolkit oficial escapa.

**Webhooks.** O GitHub assina o corpo com HMAC-SHA256
(`X-Hub-Signature-256`). O erro mais comum é conferir a assinatura
contra o corpo **já decodificado e re-serializado** — os bytes mudam, e
a conferência passa a falhar sempre, ou pior, é desligada. O segundo é
comparar com `==`, que vaza pelo tempo quantos caracteres acertaram.
`evento_de_webhook` recusa o corpo que não é o original e compara em
tempo constante.

**API REST.** `cliente(token)` fala a API v3 com os cabeçalhos que ela
pede, pagina pelo `Link: rel="next"` (a lista de issues de um repositório
grande tem mais de 100 itens, e a primeira página parece ser tudo), e
guarda o limite de taxa que sobrou. O token nunca aparece em texto.

O que ele **não** é: não é o `gh` (não há login interativo) e não é
Octokit (não há um método por endpoint — `pedir` fala qualquer um).
"""

import hashlib
import hmac as _hmac
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid


def _erro(mensagem, nota="", dica="", doc="biblioteca/github"):
    from ..errors import RuntimeError_
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=doc)


# ═══════════════════════════════════════════════════════════
#  Actions — o executor
# ═══════════════════════════════════════════════════════════

_NIVEIS = {"error": "error", "erro": "error",
           "warning": "warning", "aviso": "warning",
           "notice": "notice", "nota": "notice"}


def escapar_dado(texto):
    """O corpo de um comando de workflow: `%`, `\\r` e `\\n` escapados.

    Sem isso uma mensagem de duas linhas vira uma anotação cortada na
    primeira, e um `%0A` literal vira quebra de linha.
    """
    return (str(texto).replace("%", "%25").replace("\r", "%0D")
            .replace("\n", "%0A"))


def escapar_propriedade(texto):
    """Uma propriedade (`file=`, `title=`): também `:` e `,`.

    Um título com vírgula terminaria a propriedade no meio, e o resto
    viraria uma propriedade que o executor ignora.
    """
    return escapar_dado(texto).replace(":", "%3A").replace(",", "%2C")


def anotacao(nivel, mensagem, arquivo="", linha=0, coluna=0, titulo="",
             fim_linha=0):
    """A linha `::error file=a.df,line=3::mensagem` — sem imprimir.

    `nivel` aceita `error`/`warning`/`notice` e os nomes em português
    (`erro`, `aviso`, `nota`). Qualquer outro é recusado: o executor
    ignoraria a linha em silêncio, e a anotação que devia aparecer no PR
    simplesmente não apareceria.
    """
    tipo = _NIVEIS.get(str(nivel).lower())
    if tipo is None:
        raise _erro(
            f"'{nivel}' nao e um nivel de anotacao. Use erro, aviso ou nota.",
            nota="o executor ignora a linha com um nivel desconhecido, "
                 "e a anotacao some sem erro.",
            dica="use 'erro', 'aviso' ou 'nota' (ou error, warning, notice).")
    props = []
    if arquivo:
        props.append(f"file={escapar_propriedade(arquivo)}")
    if linha:
        props.append(f"line={int(linha)}")
    if fim_linha:
        props.append(f"endLine={int(fim_linha)}")
    if coluna:
        props.append(f"col={int(coluna)}")
    if titulo:
        props.append(f"title={escapar_propriedade(titulo)}")
    cabeca = f"::{tipo}"
    if props:
        cabeca += " " + ",".join(props)
    return f"{cabeca}::{escapar_dado(mensagem)}"


def anotar(nivel, mensagem, arquivo="", linha=0, coluna=0, titulo=""):
    """Imprime a anotação. No PR, ela aparece na linha do arquivo."""
    texto = anotacao(nivel, mensagem, arquivo, linha, coluna, titulo)
    print(texto, flush=True)
    return texto


def em_actions():
    """`yes` quando o programa roda dentro de um job do GitHub Actions."""
    return os.environ.get("GITHUB_ACTIONS") == "true"


def contexto():
    """O que o executor diz sobre a execução — repositório, commit, quem.

    Fora do Actions os campos vêm vazios, e `em_actions` é `no`: um
    script que roda nos dois lugares decide pelo campo, e não por um
    `try` em volta de uma variável que não existe.
    """
    e = os.environ
    servidor = e.get("GITHUB_SERVER_URL", "https://github.com")
    repo = e.get("GITHUB_REPOSITORY", "")
    execucao = e.get("GITHUB_RUN_ID", "")
    return {
        "em_actions": em_actions(),
        "repositorio": repo,
        "sha": e.get("GITHUB_SHA", ""),
        "ref": e.get("GITHUB_REF", ""),
        "ramo": e.get("GITHUB_REF_NAME", ""),
        "evento": e.get("GITHUB_EVENT_NAME", ""),
        "ator": e.get("GITHUB_ACTOR", ""),
        "execucao": execucao,
        "numero": e.get("GITHUB_RUN_NUMBER", ""),
        "tentativa": e.get("GITHUB_RUN_ATTEMPT", ""),
        "pasta": e.get("GITHUB_WORKSPACE", ""),
        "url_da_execucao": (f"{servidor}/{repo}/actions/runs/{execucao}"
                            if repo and execucao else ""),
    }


def evento():
    """A carga do evento que disparou o job (`GITHUB_EVENT_PATH`).

    Num `pull_request`, é aqui que moram o número do PR, o ramo de
    origem e quem abriu. Fora do Actions devolve um vault vazio.
    """
    caminho = os.environ.get("GITHUB_EVENT_PATH", "")
    if not caminho or not os.path.isfile(caminho):
        return {}
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _arquivo_do_executor(variavel, para_que):
    caminho = os.environ.get(variavel, "")
    if not caminho:
        raise _erro(
            f"'{variavel}' nao esta definida — {para_que} so existe "
            "dentro de um job do GitHub Actions.",
            dica="confira com 'GitHub.em_actions()' antes, se o mesmo "
                 "script tambem roda na sua maquina.")
    return caminho


def _nome_valido(nome, o_que):
    nome = str(nome)
    if not nome or "\n" in nome or "\r" in nome or "=" in nome:
        raise _erro(
            f"'{nome}' nao serve como nome de {o_que}.",
            nota="um nome com '=' ou quebra de linha injetaria outra "
                 "variavel no arquivo do executor.")
    return nome


def _par(nome, valor):
    """`nome<<DELIM\\nvalor\\nDELIM` — o formato que aceita qualquer valor.

    O delimitador é aleatório pelo mesmo motivo do toolkit oficial: um
    delimitador fixo pode aparecer DENTRO do valor (um log, um diff), e
    aí o que vem depois dele vira uma variável nova.
    """
    valor = "" if valor is None else str(valor)
    delim = f"ghadelimiter_{uuid.uuid4()}"
    return f"{nome}<<{delim}\n{valor}\n{delim}\n"


def saida(nome, valor):
    """Uma saída do passo: `steps.<id>.outputs.<nome>` nos seguintes."""
    nome = _nome_valido(nome, "saida")
    with open(_arquivo_do_executor("GITHUB_OUTPUT", "uma saida de passo"),
              "a", encoding="utf-8") as f:
        f.write(_par(nome, valor))
    return valor


def exportar(nome, valor):
    """Uma variável de ambiente para os passos SEGUINTES do job."""
    nome = _nome_valido(nome, "variavel")
    with open(_arquivo_do_executor("GITHUB_ENV", "exportar variavel"),
              "a", encoding="utf-8") as f:
        f.write(_par(nome, valor))
    return valor


def no_path(pasta):
    """Acrescenta uma pasta ao PATH dos passos seguintes."""
    with open(_arquivo_do_executor("GITHUB_PATH", "mudar o PATH"),
              "a", encoding="utf-8") as f:
        f.write(str(pasta) + "\n")
    return pasta


def resumo(markdown):
    """Acrescenta Markdown ao resumo da execução (a página do job)."""
    with open(_arquivo_do_executor("GITHUB_STEP_SUMMARY", "o resumo do job"),
              "a", encoding="utf-8") as f:
        f.write(str(markdown).rstrip("\n") + "\n")
    return markdown


def tabela_markdown(linhas, colunas=None):
    """Uma tabela Markdown a partir de uma lista de vaults — para o resumo.

    A barra vertical dentro de um valor é escapada: sem isso ela abriria
    uma coluna a mais e desalinharia a tabela inteira.
    """
    linhas = list(linhas or [])
    if not linhas:
        return ""
    colunas = list(colunas or linhas[0].keys())

    def celula(v):
        return str("" if v is None else v).replace("|", "\\|").replace("\n", " ")

    saida_ = ["| " + " | ".join(celula(c) for c in colunas) + " |",
              "|" + "|".join("---" for _ in colunas) + "|"]
    for l in linhas:
        saida_.append("| " + " | ".join(celula(l.get(c, "")) for c in colunas) + " |")
    return "\n".join(saida_)


def mascarar_no_log(valor):
    """Esconde o valor em todo log que vier depois (`::add-mask::`).

    Um segredo de várias linhas é mascarado **linha a linha**: o
    executor casa por linha, e mascarar o bloco inteiro deixaria cada
    linha aparecer sozinha.
    """
    texto = str(valor)
    for linha in texto.splitlines() or [texto]:
        if linha.strip():
            print(f"::add-mask::{escapar_dado(linha)}", flush=True)
    return valor


def grupo(nome, acao):
    """Roda a ação dentro de um grupo recolhível do log.

    O `::endgroup::` sai mesmo se a ação falhar: sem isso, todo o log
    depois do erro fica escondido dentro do grupo que nunca fechou.
    """
    print(f"::group::{escapar_dado(nome)}", flush=True)
    try:
        return acao()
    finally:
        print("::endgroup::", flush=True)


# ═══════════════════════════════════════════════════════════
#  Webhooks
# ═══════════════════════════════════════════════════════════

def _bytes_do_corpo(corpo):
    if isinstance(corpo, (bytes, bytearray)):
        return bytes(corpo)
    if isinstance(corpo, str):
        return corpo.encode("utf-8")
    raise _erro(
        "o corpo do webhook precisa ser o TEXTO que chegou, e nao um vault: "
        "a assinatura e sobre os BYTES originais.",
        nota="a assinatura e sobre os BYTES do corpo. Decodificar o JSON "
             "e serializar de novo muda espacos e ordem das chaves, e a "
             "assinatura deixa de bater.",
        dica="no Kiln, use o corpo cru do pedido, antes de ler como JSON.")


def assinatura(segredo, corpo):
    """`sha256=<hex>` — o que o GitHub manda em `X-Hub-Signature-256`."""
    if not segredo:
        raise _erro("o segredo do webhook esta vazio.",
                    nota="um webhook sem segredo aceita qualquer pedido de "
                         "qualquer um que descubra a URL.")
    digest = _hmac.new(str(segredo).encode("utf-8"), _bytes_do_corpo(corpo),
                       hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def conferir_webhook(segredo, corpo, cabecalho):
    """`yes` se a assinatura bate — comparada em tempo constante."""
    if not cabecalho:
        return False
    esperado = assinatura(segredo, corpo)
    return _hmac.compare_digest(esperado.encode("utf-8"),
                                str(cabecalho).encode("utf-8"))


def _cabecalho(cabecalhos, nome):
    alvo = nome.lower()
    for k, v in (cabecalhos or {}).items():
        if str(k).lower() == alvo:
            return v
    return None


def evento_de_webhook(cabecalhos, corpo, segredo):
    """Confere a assinatura e devolve o evento — ou recusa.

    Devolve `{tipo, entrega, acao, carga}`. `tipo` é o
    `X-GitHub-Event` (`push`, `pull_request`…), `entrega` o id da
    entrega (guarde-o: o GitHub reentrega, e processar duas vezes é o
    defeito seguinte), e `acao` o campo `action` da carga, quando há.
    """
    cab = _cabecalho(cabecalhos, "X-Hub-Signature-256")
    if not conferir_webhook(segredo, corpo, cab):
        raise _erro(
            "a assinatura do webhook nao confere.",
            nota="ou o segredo esta errado, ou o corpo foi alterado — ou "
                 "nao veio do GitHub." if cab else
                 "o pedido nao trouxe 'X-Hub-Signature-256'.",
            dica="responda 401 e nao processe nada.")
    texto = _bytes_do_corpo(corpo).decode("utf-8")
    carga = json.loads(texto) if texto.strip() else {}
    return {
        "tipo": _cabecalho(cabecalhos, "X-GitHub-Event") or "",
        "entrega": _cabecalho(cabecalhos, "X-GitHub-Delivery") or "",
        "acao": carga.get("action", "") if isinstance(carga, dict) else "",
        "carga": carga,
    }


# ═══════════════════════════════════════════════════════════
#  A API REST
# ═══════════════════════════════════════════════════════════

_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_ESTADOS = ("error", "failure", "pending", "success")


def _repo(repo):
    if not _REPO.match(str(repo)):
        raise _erro(f"'{repo}' nao e um repositorio no formato 'dono/nome'.")
    return str(repo)


def _proxima(link):
    """A URL de `rel="next"` no cabeçalho `Link`, ou `None`."""
    for parte in (link or "").split(","):
        pedacos = parte.split(";")
        if len(pedacos) >= 2 and 'rel="next"' in pedacos[1]:
            return pedacos[0].strip().strip("<>")
    return None


class ClienteGitHub:
    """Fala a API REST do GitHub. Ver `cliente`."""

    def __init__(self, token="", base="https://api.github.com", prazo=30.0):
        self._token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base = str(base).rstrip("/")
        self.prazo = float(prazo)
        #: o que sobrou do limite de taxa, lido do último pedido
        self.limite = None

    def __repr__(self):
        tem = "com token" if self._token else "sem token"
        return f"<GitHub {self.base} ({tem})>"

    __str__ = __repr__

    def pedir(self, metodo, caminho, corpo=None):
        """Qualquer endpoint. Devolve `{status, corpo, cabecalhos}`.

        Não levanta por status: um 404 é resposta, e é quem chama que
        sabe se ele é erro. Levanta só quando não há resposta nenhuma.
        """
        url = caminho if str(caminho).startswith("http") else \
            f"{self.base}/{str(caminho).lstrip('/')}"
        dados = None
        cab = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "dataforge-arcane-github"}
        if self._token:
            cab["Authorization"] = f"Bearer {self._token}"
        if corpo is not None:
            dados = json.dumps(corpo).encode("utf-8")
            cab["Content-Type"] = "application/json"
        pedido = urllib.request.Request(url, data=dados, method=str(metodo).upper(),
                                        headers=cab)
        try:
            with urllib.request.urlopen(pedido, timeout=self.prazo) as r:
                status, bruto, cabecalhos = r.status, r.read(), dict(r.headers)
        except urllib.error.HTTPError as e:
            status, bruto, cabecalhos = e.code, e.read(), dict(e.headers or {})
        except urllib.error.URLError as e:
            raise _erro(f"nao alcancei {self.base}: {e.reason}",
                        dica="confira a rede e a URL base.")
        restante = cabecalhos.get("X-RateLimit-Remaining")
        if restante is not None:
            try:
                self.limite = int(restante)
            except ValueError:
                pass
        texto = bruto.decode("utf-8", "replace") if bruto else ""
        try:
            valor = json.loads(texto) if texto.strip() else None
        except ValueError:
            valor = texto
        return {"status": status, "corpo": valor, "cabecalhos": cabecalhos}

    def _exigir(self, r, o_que):
        if 200 <= r["status"] < 300:
            return r["corpo"]
        msg = r["corpo"].get("message", "") if isinstance(r["corpo"], dict) else ""
        dicas = {401: "o token e invalido ou expirou.",
                 403: "o token nao tem permissao — ou o limite de taxa acabou.",
                 404: "o recurso nao existe, ou o token nao o enxerga "
                      "(um repositorio privado responde 404, e nao 403).",
                 422: "o GitHub recusou os dados — veja 'errors' na resposta."}
        raise _erro(f"{o_que}: o GitHub respondeu {r['status']}"
                    + (f" — {msg}" if msg else ""),
                    dica=dicas.get(r["status"], ""))

    def todas(self, caminho, limite=1000):
        """Todas as páginas de uma lista, seguindo `Link: rel="next"`.

        Sem isto, a lista de issues de um repositório grande devolve as
        primeiras 30 — e parece ser tudo.
        """
        sep = "&" if "?" in caminho else "?"
        url = f"{caminho}{sep}per_page=100"
        itens = []
        while url and len(itens) < limite:
            r = self.pedir("GET", url)
            pagina = self._exigir(r, f"GET {caminho}")
            itens.extend(pagina or [])
            url = _proxima(r["cabecalhos"].get("Link", ""))
        return itens[:limite]

    def repositorio(self, repo):
        return self._exigir(self.pedir("GET", f"repos/{_repo(repo)}"),
                            f"ler {repo}")

    def issues(self, repo, estado="open"):
        """As issues do repositório (sem os PRs, que a API mistura)."""
        itens = self.todas(f"repos/{_repo(repo)}/issues?state={estado}")
        return [i for i in itens if "pull_request" not in i]

    def criar_issue(self, repo, titulo, corpo="", rotulos=None):
        if not str(titulo).strip():
            raise _erro("uma issue precisa de titulo.")
        dados = {"title": str(titulo), "body": str(corpo or "")}
        if rotulos:
            dados["labels"] = [str(r) for r in rotulos]
        return self._exigir(self.pedir("POST", f"repos/{_repo(repo)}/issues", dados),
                            "criar a issue")

    def comentar(self, repo, numero, texto):
        """Comenta numa issue **ou** num PR — para a API, os dois são issues."""
        return self._exigir(
            self.pedir("POST", f"repos/{_repo(repo)}/issues/{int(numero)}/comments",
                       {"body": str(texto)}),
            f"comentar em #{numero}")

    def criar_release(self, repo, tag, nome="", notas="", rascunho=False,
                      pre=False):
        return self._exigir(
            self.pedir("POST", f"repos/{_repo(repo)}/releases",
                       {"tag_name": str(tag), "name": str(nome or tag),
                        "body": str(notas or ""), "draft": bool(rascunho),
                        "prerelease": bool(pre)}),
            f"criar a release {tag}")

    def disparar_workflow(self, repo, workflow, ref="main", entradas=None):
        """`workflow_dispatch` — roda um workflow por nome de arquivo."""
        r = self.pedir("POST",
                       f"repos/{_repo(repo)}/actions/workflows/{workflow}/dispatches",
                       {"ref": str(ref), "inputs": dict(entradas or {})})
        self._exigir(r, f"disparar {workflow}")
        return r["status"] == 204

    def status(self, repo, sha, estado, contexto_="dataforge", descricao="",
               url=""):
        """O selo de status de um commit (o ✓ ou ✗ ao lado do commit)."""
        if estado not in _ESTADOS:
            raise _erro(f"'{estado}' nao e um estado de commit. Use um de: "
                        f"{', '.join(_ESTADOS)}.")
        dados = {"state": estado, "context": str(contexto_),
                 "description": str(descricao)[:140]}
        if url:
            dados["target_url"] = str(url)
        return self._exigir(
            self.pedir("POST", f"repos/{_repo(repo)}/statuses/{sha}", dados),
            "publicar o status")


def cliente(token="", base="https://api.github.com", prazo=30.0):
    """Um cliente da API. Sem `token`, usa `GITHUB_TOKEN` do ambiente."""
    return ClienteGitHub(token, base, prazo)


class ArcaneGitHub:
    """Arcane.GitHub — Actions, webhooks e a API REST."""

    def __new__(cls):
        return {
            # Actions
            "anotacao": anotacao,
            "anotar": anotar,
            "escapar_dado": escapar_dado,
            "escapar_propriedade": escapar_propriedade,
            "em_actions": em_actions,
            "contexto": contexto,
            "evento": evento,
            "saida": saida,
            "exportar": exportar,
            "no_path": no_path,
            "resumo": resumo,
            "tabela_markdown": tabela_markdown,
            "mascarar_no_log": mascarar_no_log,
            "grupo": grupo,
            # Webhooks
            "assinatura": assinatura,
            "conferir_webhook": conferir_webhook,
            "evento_de_webhook": evento_de_webhook,
            # API
            "cliente": cliente,
            "ClienteGitHub": ClienteGitHub,
        }
