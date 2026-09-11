"""
Gerenciador de pacotes do DataForge — `forge`

Resolve, baixa, instala e trava dependencias declaradas no forge.toml,
do mesmo jeito que o pip e o npm fazem nas suas linguagens.

    [dependencies]
    validador = "^1.0.0"          # do registro oficial
    tabela    = "~2.1"
    interno   = { path = "../interno" }
    forkado   = { git = "https://github.com/alguem/lib.git", ref = "v1.2" }

Onde as coisas ficam:

    forge_modules/<nome>/         pacote instalado (o que o 'adopt' enxerga)
    forge.lock                    versao exata e sha256 de cada pacote
    ~/.dataforge/cache/           tarballs baixados, reaproveitados entre projetos

Fontes suportadas: registro HTTPS (padrao), caminho local, repositorio git
e URL direta de tarball. Tudo com a biblioteca padrao do Python — o runtime
do DataForge continua sem dependencia externa.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.error
import urllib.request

PASTA_MODULOS = "forge_modules"
ARQUIVO_LOCK = "forge.lock"
REGISTRO_PADRAO = "https://dataforge-lang.vercel.app/registry"
CACHE = os.path.join(os.path.expanduser("~"), ".dataforge", "cache")
VALIDADE_INDICE = 60 * 60 * 6          # 6h antes de reconsultar o indice


class ErroPacote(Exception):
    """Falha de resolucao, download ou instalacao."""


# ─────────────────────────────────────────────────────────────
# Versoes e requisitos
# ─────────────────────────────────────────────────────────────

class Versao:
    """Versao semantica: maior.menor.correcao[-pre]."""

    __slots__ = ("maior", "menor", "correcao", "pre", "texto")

    def __init__(self, texto):
        self.texto = str(texto).strip().lstrip("v")
        corpo, _, self.pre = self.texto.partition("-")
        partes = (corpo.split(".") + ["0", "0", "0"])[:3]
        try:
            self.maior, self.menor, self.correcao = (int(p or 0) for p in partes)
        except ValueError:
            raise ErroPacote(f"versao invalida: '{texto}'")

    @property
    def chave(self):
        # sem pre-release ordena depois do pre-release da mesma versao
        return (self.maior, self.menor, self.correcao, 1 if not self.pre else 0, self.pre)

    def __eq__(self, o): return isinstance(o, Versao) and self.chave == o.chave
    def __lt__(self, o): return self.chave < o.chave
    def __le__(self, o): return self.chave <= o.chave
    def __gt__(self, o): return self.chave > o.chave
    def __ge__(self, o): return self.chave >= o.chave
    def __hash__(self): return hash(self.chave)
    def __repr__(self): return self.texto
    def __str__(self): return self.texto


class Requisito:
    """Faixa de versoes aceitaveis.

        *  ou vazio   qualquer versao
        1.2.3         exatamente essa
        ^1.2.3        >=1.2.3 e <2.0.0   (nao muda o 'maior')
        ~1.2.3        >=1.2.3 e <1.3.0   (nao muda o 'menor')
        >=1.2  <2.0   comparadores, combinaveis por espaco
    """

    def __init__(self, texto):
        self.texto = (str(texto) or "*").strip() or "*"
        self.clausulas = self._compilar(self.texto)

    @staticmethod
    def _compilar(texto):
        if texto in ("*", "", "latest", "qualquer"):
            return []

        clausulas = []
        for parte in re.split(r"[,\s]+", texto.strip()):
            if not parte:
                continue
            m = re.match(r"^(\^|~|>=|<=|==|>|<|=)?\s*(.+)$", parte)
            if not m:
                raise ErroPacote(f"requisito invalido: '{texto}'")
            op, alvo = m.group(1) or "==", Versao(m.group(2))

            if op == "^":
                teto = Versao(f"{alvo.maior + 1}.0.0") if alvo.maior else \
                       Versao(f"0.{alvo.menor + 1}.0")   # ^0.x trava o menor
                clausulas += [(">=", alvo), ("<", teto)]
            elif op == "~":
                clausulas += [(">=", alvo), ("<", Versao(f"{alvo.maior}.{alvo.menor + 1}.0"))]
            else:
                clausulas.append(("==" if op == "=" else op, alvo))
        return clausulas

    def aceita(self, versao):
        if isinstance(versao, str):
            versao = Versao(versao)
        for op, alvo in self.clausulas:
            if op == ">=" and not versao >= alvo: return False
            if op == ">" and not versao > alvo: return False
            if op == "<=" and not versao <= alvo: return False
            if op == "<" and not versao < alvo: return False
            if op == "==" and not versao == alvo: return False
        return True

    def melhor(self, versoes):
        """A maior versao que satisfaz o requisito, ou None."""
        aceitas = sorted((Versao(v) for v in versoes), key=lambda v: v.chave)
        aceitas = [v for v in aceitas if self.aceita(v)]
        return aceitas[-1] if aceitas else None

    def __repr__(self): return self.texto


# ─────────────────────────────────────────────────────────────
# Registro
# ─────────────────────────────────────────────────────────────

class Registro:
    """Cliente do indice de pacotes.

    O indice e um JSON estatico; o cache local evita ir a rede a cada
    comando e permite trabalhar offline com o que ja foi visto.
    """

    def __init__(self, url=None, offline=False):
        self.url = (url or os.environ.get("DATAFORGE_REGISTRY") or REGISTRO_PADRAO).rstrip("/")
        self.offline = offline
        self._indice = None

    @property
    def _cache_indice(self):
        marca = hashlib.sha256(self.url.encode()).hexdigest()[:12]
        return os.path.join(CACHE, f"indice-{marca}.json")

    def indice(self, forcar=False):
        if self._indice is not None and not forcar:
            return self._indice

        cache = self._cache_indice
        fresco = (os.path.exists(cache)
                  and time.time() - os.path.getmtime(cache) < VALIDADE_INDICE)

        if not forcar and (fresco or self.offline):
            if os.path.exists(cache):
                with open(cache, encoding="utf-8") as f:
                    self._indice = json.load(f)
                return self._indice
            if self.offline:
                raise ErroPacote(
                    "modo offline e o indice do registro nunca foi baixado.\n"
                    "  rode uma vez com rede, ou use uma dependencia por 'path'")

        try:
            bruto = _baixar(f"{self.url}/index.json")
            self._indice = json.loads(bruto.decode("utf-8"))
            os.makedirs(CACHE, exist_ok=True)
            with open(cache, "w", encoding="utf-8") as f:
                json.dump(self._indice, f)
        except ErroPacote:
            if os.path.exists(cache):       # rede caiu: segue com o que tem
                with open(cache, encoding="utf-8") as f:
                    self._indice = json.load(f)
            else:
                raise
        return self._indice

    def pacotes(self):
        return self.indice().get("pacotes", {})

    def info(self, nome):
        pacote = self.pacotes().get(nome)
        if pacote is None:
            parecidos = _parecidos(nome, self.pacotes())
            dica = f"\n  parecidos: {', '.join(parecidos)}" if parecidos else ""
            raise ErroPacote(f"pacote '{nome}' nao existe no registro{dica}")
        return pacote

    def versoes(self, nome):
        return list(self.info(nome).get("versoes", {}).keys())

    def lancamento(self, nome, versao):
        versoes = self.info(nome).get("versoes", {})
        if str(versao) not in versoes:
            raise ErroPacote(
                f"'{nome}' nao tem a versao {versao}. "
                f"Ha: {', '.join(sorted(versoes)) or 'nenhuma'}")
        return versoes[str(versao)]

    def buscar(self, termo):
        termo = termo.lower()
        achados = []
        for nome, info in sorted(self.pacotes().items()):
            texto = f"{nome} {info.get('descricao', '')} {' '.join(info.get('tags', []))}"
            if termo in texto.lower():
                achados.append((nome, info))
        return achados


def _baixar(url, tentativas=3):
    """GET com repeticao. Devolve bytes.

    Aceita tambem 'file://' e caminho de disco: e o que permite apontar
    DATAFORGE_REGISTRY para uma pasta local, seja um espelho corporativo
    ou o registro do proprio repositorio durante o desenvolvimento.
    """
    if url.startswith("file://") or (os.path.isabs(url) and "://" not in url):
        caminho = url[7:] if url.startswith("file://") else url
        if not os.path.isfile(caminho):
            raise ErroPacote(f"nao encontrado: {caminho}")
        with open(caminho, "rb") as f:
            return f.read()

    ultimo = None
    for n in range(tentativas):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "dataforge-forge/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ErroPacote(f"nao encontrado: {url}")
            ultimo = e
        except Exception as e:                       # rede, DNS, TLS, timeout
            ultimo = e
        if n < tentativas - 1:
            time.sleep(0.6 * (n + 1))
    raise ErroPacote(f"falha ao baixar {url}: {ultimo}")


def _parecidos(nome, disponiveis):
    import difflib
    return difflib.get_close_matches(nome, list(disponiveis), n=3, cutoff=0.6)


# ─────────────────────────────────────────────────────────────
# Especificacao de dependencia
# ─────────────────────────────────────────────────────────────

class Dependencia:
    """Uma linha de [dependencies], ja interpretada.

    fonte e 'registro', 'path', 'git' ou 'url'.
    """

    def __init__(self, nome, valor):
        self.nome = nome
        self.requisito = Requisito("*")
        self.fonte = "registro"
        self.local = self.git = self.ref = self.url = None

        if isinstance(valor, dict):
            if "path" in valor:
                self.fonte, self.local = "path", valor["path"]
            elif "git" in valor:
                self.fonte, self.git = "git", valor["git"]
                self.ref = valor.get("ref") or valor.get("tag") or valor.get("branch")
            elif "url" in valor:
                self.fonte, self.url = "url", valor["url"]
            if valor.get("version"):
                self.requisito = Requisito(valor["version"])
        else:
            texto = str(valor).strip()
            if texto.startswith(("http://", "https://")) and texto.endswith(".tar.gz"):
                self.fonte, self.url = "url", texto
            elif texto.startswith("git+"):
                self.fonte, self.git = "git", texto[4:]
            elif texto.startswith(("./", "../", "/")) or texto.startswith("path:"):
                self.fonte = "path"
                self.local = texto[5:] if texto.startswith("path:") else texto
            else:
                self.requisito = Requisito(texto)

    def para_toml(self):
        """Como esta dependencia deve aparecer no forge.toml."""
        if self.fonte == "path":
            return {"path": self.local}
        if self.fonte == "git":
            d = {"git": self.git}
            if self.ref:
                d["ref"] = self.ref
            return d
        if self.fonte == "url":
            return {"url": self.url}
        return self.requisito.texto

    def __repr__(self):
        return f"<dep {self.nome} {self.fonte} {self.requisito}>"


def ler_dependencias(mapa):
    return [Dependencia(n, v) for n, v in (mapa or {}).items()]


# ─────────────────────────────────────────────────────────────
# Lockfile
# ─────────────────────────────────────────────────────────────

class Lock:
    """forge.lock — o que foi realmente instalado, com integridade.

    Guardado em JSON: e um arquivo de maquina, ninguem edita a mao, e
    JSON evita ambiguidade de tipos que o TOML simples traria.
    """

    VERSAO = 1

    def __init__(self, raiz):
        self.caminho = os.path.join(raiz, ARQUIVO_LOCK)
        self.pacotes = {}
        self.registro = ""
        if os.path.exists(self.caminho):
            try:
                with open(self.caminho, encoding="utf-8") as f:
                    d = json.load(f)
                self.pacotes = d.get("pacotes", {})
                self.registro = d.get("registro", "")
            except (json.JSONDecodeError, OSError):
                self.pacotes = {}          # lock corrompido: reinstala do zero

    #: So registro REMOTO entra no lock.
    #:
    #: Apontar o registro para uma pasta local e conveniencia de quem
    #: desenvolve — um 'DATAFORGE_REGISTRY=./site/public/registry' para
    #: testar um pacote antes de publicar. Gravar isso no lock
    #: versionado escrevia o caminho da CASA de quem instalou dentro de
    #: um arquivo publico:
    #:
    #:     "registro": "file:///Users/<nome>/.../site/public/registry"
    #:
    #: Duas pessoas instalando o mesmo projeto produziam lockfiles
    #: diferentes, e o arquivo deixava de ser o que promete ser: o
    #: registro exato do que foi instalado, igual para todos.
    _REMOTOS = ("http://", "https://")

    def gravar(self, registro=""):
        escolhido = registro or self.registro
        if escolhido and not escolhido.startswith(self._REMOTOS):
            escolhido = ""

        d = {
            "lockVersion": self.VERSAO,
            "registro": escolhido,
            "pacotes": dict(sorted(self.pacotes.items())),
        }
        with open(self.caminho, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
            f.write("\n")

    def registrar(self, nome, versao, fonte, sha256="", dependencias=None):
        self.pacotes[nome] = {
            "versao": str(versao),
            "fonte": fonte,
            "sha256": sha256,
            "dependencias": dependencias or {},
        }

    def esquecer(self, nome):
        self.pacotes.pop(nome, None)


# ─────────────────────────────────────────────────────────────
# Resolucao
# ─────────────────────────────────────────────────────────────

def resolver(dependencias, registro, ja_instalados=None, raiz="."):
    """Resolve a arvore completa, incluindo dependencias transitivas.

    Estrategia: largura primeiro, escolhendo sempre a maior versao que
    satisfaz o requisito. Quando dois pacotes pedem o mesmo terceiro,
    intersecta os requisitos; se nao houver versao que sirva aos dois,
    falha dizendo quem pediu o que — um conflito silencioso e pior que
    um erro claro.
    """
    plano = {}                      # nome -> {versao, dep, exigido_por}
    exigencias = {}                 # nome -> [(quem, Requisito)]
    fila = [(d, "seu projeto") for d in dependencias]

    while fila:
        dep, quem = fila.pop(0)
        exigencias.setdefault(dep.nome, []).append((quem, dep.requisito))

        if dep.fonte != "registro":
            plano[dep.nome] = {"versao": None, "dep": dep, "por": quem}
            # Um pacote local ou de git tambem tem dependencias. Le-las do
            # forge.toml dele e o que faz 'dataforge add ../minha-lib'
            # trazer junto o que ela usa — sem isso, o pacote instala e
            # quebra no primeiro 'adopt'.
            for nome, req in _dependencias_declaradas(dep, raiz).items():
                fila.append((Dependencia(nome, req), f"{dep.nome} (local)"))
            continue

        disponiveis = registro.versoes(dep.nome)
        combinado = [c for _, r in exigencias[dep.nome] for c in r.clausulas]
        faixa = Requisito("*")
        faixa.clausulas = combinado

        escolhida = faixa.melhor(disponiveis)
        if escolhida is None:
            pedidos = "\n".join(f"    {q} pede {r}" for q, r in exigencias[dep.nome])
            raise ErroPacote(
                f"nao ha versao de '{dep.nome}' que sirva a todos:\n{pedidos}\n"
                f"    existem: {', '.join(sorted(disponiveis))}")

        anterior = plano.get(dep.nome)
        if anterior and anterior["versao"] == escolhida:
            continue
        plano[dep.nome] = {"versao": escolhida, "dep": dep, "por": quem}

        transitivas = registro.lancamento(dep.nome, escolhida).get("dependencias", {})
        for nome, req in transitivas.items():
            fila.append((Dependencia(nome, req), f"{dep.nome}@{escolhida}"))

    return plano



def _dependencias_declaradas(dep, raiz="."):
    """As dependencias que um pacote local declara no seu forge.toml.

    So funciona para 'path': um pacote de git ou URL ainda nao foi
    baixado quando a resolucao acontece, e suas dependencias entram
    depois, na instalacao.
    """
    if dep.fonte != "path" or not dep.local:
        return {}

    manifesto = os.path.join(os.path.abspath(raiz), dep.local, "forge.toml")
    if not os.path.isfile(manifesto):
        return {}
    try:
        from .stdlib.arcane_serialization import ArcaneSerialization
        dados = ArcaneSerialization()["from_toml"](
            open(manifesto, encoding="utf-8").read())
        return dados.get("dependencies", {}) or {}
    except Exception:
        return {}


# ─────────────────────────────────────────────────────────────
# Instalacao
# ─────────────────────────────────────────────────────────────

def _sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def _extrair_seguro(tar, destino):
    """Extrai barrando caminhos que escapam do destino (zip-slip)."""
    destino = os.path.abspath(destino)
    for membro in tar.getmembers():
        alvo = os.path.abspath(os.path.join(destino, membro.name))
        if not alvo.startswith(destino + os.sep) and alvo != destino:
            raise ErroPacote(f"pacote tenta escrever fora do destino: {membro.name}")
        if membro.issym() or membro.islnk():
            raise ErroPacote(f"pacote contem link ({membro.name}); recusado")
    tar.extractall(destino)


def _baixar_tarball(url, sha_esperado=""):
    """Baixa (ou reaproveita do cache) e confere a integridade."""
    os.makedirs(CACHE, exist_ok=True)
    marca = sha_esperado or hashlib.sha256(url.encode()).hexdigest()
    destino = os.path.join(CACHE, f"{marca}.tar.gz")

    if os.path.exists(destino) and (not sha_esperado or _sha256(destino) == sha_esperado):
        return destino

    dados = _baixar(url)
    tmp = destino + ".parcial"
    with open(tmp, "wb") as f:
        f.write(dados)

    obtido = _sha256(tmp)
    if sha_esperado and obtido != sha_esperado:
        os.remove(tmp)
        raise ErroPacote(
            f"integridade falhou para {url}\n"
            f"    esperado {sha_esperado}\n"
            f"    obtido   {obtido}")
    os.replace(tmp, destino)
    return destino


def instalar_pacote(nome, item, raiz, registro, aoVivo=print):
    """Poe um pacote em forge_modules/<nome>. Devolve (versao, sha, fonte)."""
    dep = item["dep"]
    alvo = os.path.join(raiz, PASTA_MODULOS, nome)
    os.makedirs(os.path.dirname(alvo), exist_ok=True)
    if os.path.isdir(alvo):
        shutil.rmtree(alvo)

    if dep.fonte == "path":
        origem = os.path.abspath(os.path.join(raiz, dep.local))
        if not os.path.isdir(origem):
            raise ErroPacote(f"caminho de '{nome}' nao existe: {origem}")
        shutil.copytree(origem, alvo, ignore=shutil.ignore_patterns(
            PASTA_MODULOS, ".git", "__pycache__", "*.pyc"))
        versao = _versao_do_pacote(alvo)
        return versao, "", f"path:{dep.local}"

    if dep.fonte == "git":
        if shutil.which("git") is None:
            raise ErroPacote(f"'{nome}' vem de git, mas o git nao esta instalado")
        with tempfile.TemporaryDirectory() as tmp:
            clone = os.path.join(tmp, "c")
            cmd = ["git", "clone", "--depth", "1", "--quiet"]
            if dep.ref:
                cmd += ["--branch", dep.ref]
            r = subprocess.run(cmd + [dep.git, clone],
                               capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            if r.returncode != 0:
                raise ErroPacote(f"git clone de '{nome}' falhou: {r.stderr.strip()}")
            shutil.rmtree(os.path.join(clone, ".git"), ignore_errors=True)
            shutil.copytree(clone, alvo)
        versao = _versao_do_pacote(alvo)
        return versao, "", f"git:{dep.git}" + (f"#{dep.ref}" if dep.ref else "")

    if dep.fonte == "url":
        arquivo = _baixar_tarball(dep.url)
        _desempacotar(arquivo, alvo, nome)
        return _versao_do_pacote(alvo), _sha256(arquivo), f"url:{dep.url}"

    # registro
    versao = item["versao"]
    lanc = registro.lancamento(nome, versao)
    url = lanc.get("url") or f"{registro.url}/pacotes/{lanc['arquivo']}"
    arquivo = _baixar_tarball(url, lanc.get("sha256", ""))
    _desempacotar(arquivo, alvo, nome)
    return versao, lanc.get("sha256", ""), "registro"


def _desempacotar(arquivo, alvo, nome):
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(arquivo, "r:gz") as tar:
            _extrair_seguro(tar, tmp)
        # o tarball tem uma pasta raiz (nome-versao/); usa o conteudo dela
        itens = [i for i in os.listdir(tmp) if not i.startswith(".")]
        origem = os.path.join(tmp, itens[0]) if len(itens) == 1 and \
            os.path.isdir(os.path.join(tmp, itens[0])) else tmp
        shutil.copytree(origem, alvo)


def _versao_do_pacote(pasta):
    """Le a versao do forge.toml do pacote instalado."""
    manifesto = os.path.join(pasta, "forge.toml")
    if not os.path.exists(manifesto):
        return Versao("0.0.0")
    try:
        from .stdlib.arcane_serialization import ArcaneSerialization
        dados = ArcaneSerialization()["from_toml"](
            open(manifesto, encoding="utf-8").read())
        secao = dados.get("package") or dados.get("project") or {}
        return Versao(secao.get("version", "0.0.0"))
    except Exception:
        return Versao("0.0.0")


# ─────────────────────────────────────────────────────────────
# Empacotar para publicar
# ─────────────────────────────────────────────────────────────

IGNORAR_SEMPRE = {PASTA_MODULOS, ".git", "__pycache__", "dist", ".venv",
                  ".DS_Store", "node_modules", ".pytest_cache"}


def empacotar(raiz, saida="dist"):
    """Gera dist/<nome>-<versao>.tar.gz a partir do forge.toml.

    Devolve (caminho, sha256, nome, versao).
    """
    from . import project as proj

    manifesto = proj.carregar(raiz)
    if manifesto is None:
        raise ErroPacote("nenhum forge.toml aqui. Rode 'dataforge init' primeiro.")

    secao = manifesto.dados.get("package") or manifesto.dados.get("project") or {}
    nome = secao.get("name", "").strip()
    versao = str(secao.get("version", "")).strip()
    if not nome:
        raise ErroPacote("o forge.toml precisa de um 'name'")
    if not re.match(r"^[a-z][a-z0-9_-]{1,48}$", nome):
        raise ErroPacote(
            f"nome de pacote invalido: '{nome}'\n"
            "  use minusculas, digitos, '-' e '_', comecando por letra")
    if not versao:
        raise ErroPacote("o forge.toml precisa de uma 'version'")
    Versao(versao)                      # valida o formato

    pasta_saida = os.path.join(manifesto.raiz, saida)
    os.makedirs(pasta_saida, exist_ok=True)
    destino = os.path.join(pasta_saida, f"{nome}-{versao}.tar.gz")

    ignorar = set(IGNORAR_SEMPRE) | {saida}

    def filtrar(info):
        partes = set(info.name.split("/"))
        if partes & ignorar or info.name.endswith((".pyc", ".log")):
            return None
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        info.mtime = 0                  # tarball reproduzivel
        return info

    with tarfile.open(destino, "w:gz") as tar:
        tar.add(manifesto.raiz, arcname=f"{nome}-{versao}", filter=filtrar)

    return destino, _sha256(destino), nome, versao
