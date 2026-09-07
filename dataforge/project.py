"""
Manifesto de projeto DataForge — `forge.toml`

Estrutura reconhecida:

    [project]
    name = "meu-app"
    version = "0.1.0"
    description = "..."
    authors = ["Fulano"]
    license = "MIT"
    entry = "src/main.df"
    dataforge = ">=4.0"

    [dependencies]
    # nome = "versão"   (o gerenciador de pacotes ainda não resolve isto)

    [scripts]
    start = "run src/main.df"
    test  = "test tests/"

    [build]
    out = "dist"
    include = ["src", "assets"]

    [lint]
    strict = false
    ignore = ["magic-number"]
"""

import os

from .stdlib.arcane_serialization import ArcaneSerialization

ARQUIVO = "forge.toml"

MODELO = '''[project]
name = "{nome}"
version = "0.1.0"
description = "{descricao}"
authors = ["{autor}"]
license = "MIT"
entry = "{entrada}"
dataforge = ">={versao}"

[dependencies]

[scripts]
start = "run {entrada}"
test = "test tests/"
check = "check ."
fmt = "fmt ."

[build]
out = "dist"
include = ["src"]

[lint]
strict = false
ignore = []
'''

PADRAO = {
    "project": {"name": "", "version": "0.1.0", "description": "",
                "authors": [], "license": "", "entry": "main.df",
                "dataforge": ""},
    "dependencies": {},
    "scripts": {},
    "build": {"out": "dist", "include": ["src"]},
    "lint": {"strict": False, "ignore": []},
}


class Manifest:
    """Um forge.toml carregado."""

    def __init__(self, dados, caminho):
        self.caminho = caminho
        self.raiz = os.path.dirname(os.path.abspath(caminho)) if caminho else os.getcwd()
        self.dados = {**{k: dict(v) if isinstance(v, dict) else v
                         for k, v in PADRAO.items()}}
        for secao, valores in (dados or {}).items():
            if isinstance(valores, dict) and isinstance(self.dados.get(secao), dict):
                self.dados[secao].update(valores)
            else:
                self.dados[secao] = valores

    # ── Acesso ──
    @property
    def name(self): return self.dados["project"].get("name", "")

    @property
    def version(self): return self.dados["project"].get("version", "0.0.0")

    @property
    def entry(self): return self.dados["project"].get("entry", "main.df")

    @property
    def scripts(self): return self.dados.get("scripts", {})

    @property
    def dependencies(self): return self.dados.get("dependencies", {})

    @property
    def lint_ignore(self): return self.dados.get("lint", {}).get("ignore", [])

    @property
    def lint_strict(self): return bool(self.dados.get("lint", {}).get("strict", False))

    def entry_path(self):
        return os.path.join(self.raiz, self.entry)

    def requires(self, versao_atual):
        """A versão atual do DataForge satisfaz o requisito do manifesto?"""
        exigido = str(self.dados["project"].get("dataforge", "")).strip()
        if not exigido:
            return True, ""
        operador = ""
        for candidato in (">=", "<=", "==", ">", "<", "^", "~"):
            if exigido.startswith(candidato):
                operador = candidato
                exigido = exigido[len(candidato):].strip()
                break
        atual = _versao(versao_atual)
        alvo = _versao(exigido)
        if operador in (">=", "^", "~", ""):
            ok = atual >= alvo
        elif operador == ">":
            ok = atual > alvo
        elif operador == "<=":
            ok = atual <= alvo
        elif operador == "<":
            ok = atual < alvo
        else:
            ok = atual == alvo
        return ok, exigido

    def __repr__(self):
        return f"<forge.toml {self.name} {self.version}>"


def _versao(texto):
    partes = []
    for parte in str(texto).split("."):
        digitos = "".join(c for c in parte if c.isdigit())
        partes.append(int(digitos) if digitos else 0)
    while len(partes) < 3:
        partes.append(0)
    return tuple(partes[:3])


def encontrar(inicio="."):
    """Sobe os diretórios procurando um forge.toml."""
    atual = os.path.abspath(inicio)
    if os.path.isfile(atual):
        atual = os.path.dirname(atual)
    while True:
        candidato = os.path.join(atual, ARQUIVO)
        if os.path.exists(candidato):
            return candidato
        pai = os.path.dirname(atual)
        if pai == atual:
            return None
        atual = pai


def carregar(inicio="."):
    """Carrega o manifesto mais próximo. Devolve None se não houver."""
    caminho = encontrar(inicio)
    if not caminho:
        return None
    texto = open(caminho, encoding="utf-8").read()
    dados = ArcaneSerialization()["from_toml"](texto)
    return Manifest(dados, caminho)


def criar(pasta, nome, descricao="", autor="", entrada="src/main.df", versao="4.0"):
    """Escreve um forge.toml novo."""
    caminho = os.path.join(pasta, ARQUIVO)
    conteudo = MODELO.format(nome=nome, descricao=descricao, autor=autor or "voce",
                             entrada=entrada, versao=versao)
    os.makedirs(pasta, exist_ok=True)
    open(caminho, "w", encoding="utf-8").write(conteudo)
    return caminho
