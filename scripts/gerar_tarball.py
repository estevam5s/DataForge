#!/usr/bin/env python3
"""Gera o tarball do DataForge que o site serve para os instaladores.

    python3 scripts/gerar_tarball.py

Escreve site/public/dist/dataforge-<versao>.tar.gz e o .sha256 ao lado.
A versao vem de dataforge/__init__.py — nao ha numero repetido a mao.

Roda isto sempre que a versao mudar: o instalador baixa deste arquivo.
"""

import hashlib
import os
import pathlib
import sys
import tarfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from dataforge import __version__ as VERSAO  # noqa: E402

# O que o pacote instalavel precisa. Exercicios, exemplos, testes e o
# site ficam de fora: sao dezenas de MB que ninguem baixa para rodar
# 'dataforge run'. Quem quer isso clona o repositorio.
#: O que vai no tarball que o site serve.
#:
#: 'examples' e 'exercicios' entram porque o instalador oferece
#: baixa-los, e baixar um segundo arquivo so para isso dobraria o
#: tempo de instalacao de quem so quer olhar dois programas.
INCLUIR = ["dataforge", "pyproject.toml", "README.md", "LICENSE",
           "CLAUDE.md", "doc", "examples", "exercicios"]

# A extensao do VS Code entra no MESMO lugar em que ela mora no
# repositorio: 'editor/vscode', na raiz.
#
# Ela acaba DENTRO do pacote instalado de todo jeito — quem faz isso e o
# 'pyproject.toml':
#
#     packages = [… "dataforge.editor"]
#     [tool.setuptools.package-dir]
#     "dataforge.editor" = "editor"
#
# A versao anterior a punha direto em 'dataforge/editor/vscode' e NAO
# incluia a raiz 'editor/'. O efeito: o 'pip install' do tarball morria
# com "error: package directory 'editor' does not exist" — e era o
# tarball que o site serve, entao o instalador oficial falhava em todas
# as maquinas. No repositorio 'pip install .' funcionava, porque ali a
# pasta existe: a divergencia entre os dois layouts era invisivel de
# dentro.
EMBUTIR = [("editor/vscode", "editor/vscode")]
IGNORAR = {"__pycache__", ".pyc", ".DS_Store", ".pytest_cache", "dist", ".egg-info"}


def producao_da_extensao():
    """Os pacotes npm que a extensao carrega EM EXECUCAO.

    'node_modules' tem 29 MB, e quase tudo e TypeScript e tipos, que so
    servem para compilar. Em execucao a extensao carrega uma dependencia
    so — 'vscode-languageclient' — mais o que ela puxa: cerca de 2,5 MB.

    Sem isto o tarball leva 29 MB para entregar 2,5, e o wheel construido
    a partir dele nao levava NENHUM: os globs do 'pyproject' alcancam dois
    niveis, e a biblioteca esta mais fundo. O resultado era um LSP que
    nao subia em nenhuma instalacao por pip, com a extensao dizendo
    "vscode-languageclient nao encontrado" no painel de saida.

    Resolvido lendo os 'package.json', e nao chamando o npm: ele pode nao
    estar na maquina que empacota.
    """
    import json

    base = RAIZ / "editor" / "vscode"
    modulos = base / "node_modules"
    if not modulos.is_dir():
        return set()

    def dependencias(pasta):
        manifesto = pasta / "package.json"
        if not manifesto.is_file():
            return []
        return list(json.loads(manifesto.read_text(encoding="utf-8"))
                    .get("dependencies", {}))

    vistos, fila = set(), dependencias(base)
    while fila:
        nome = fila.pop(0)
        if nome in vistos or not (modulos / nome).is_dir():
            continue
        vistos.add(nome)
        fila.extend(dependencias(modulos / nome))
    return vistos


PRODUCAO = producao_da_extensao()


def filtrar(info):
    if any(marca in info.name for marca in IGNORAR):
        return None

    # De 'node_modules', so o fecho de execucao.
    if "/node_modules/" in info.name:
        resto = info.name.split("/node_modules/", 1)[1]
        pacote = "/".join(resto.split("/")[:2]) if resto.startswith("@") \
            else resto.split("/")[0]
        if pacote and pacote not in PRODUCAO:
            return None
    # tarball reproduzivel: mesmo fonte, mesmo sha256
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = 0
    return info


#: Sem estes tres, a extensao instala e nao ativa. Eles sao compilados
#: do TypeScript, e 'editor/vscode/out/' e gitignored: num checkout
#: limpo nao existem.
COMPILADOS = ["editor/vscode/out/extension.js",
              "editor/vscode/out/servidor.js",
              "editor/vscode/out/depuracao.js"]


def _exigir_extensao_compilada():
    """Recusa gerar o tarball do site sem o JavaScript da extensao.

    O tarball e o que o 'curl | sh' e o 'irm | iex' baixam, e ele leva a
    extensao inteira — menos o 'out/', se ninguem compilou. O sintoma nao
    e erro: o 'dataforge editor' instala, o VS Code carrega o manifesto,
    e nada acontece. Cores, comandos, LSP e depurador ficam de fora.

    Avisar nao serve: um aviso impresso num gerador que roda antes de um
    deploy nao para nada, e o arquivo vai ao ar igual.
    """
    faltando = [c for c in COMPILADOS if not (RAIZ / c).is_file()]
    if faltando:
        raise SystemExit(
            "  a extensao do editor nao esta compilada, e o tarball do "
            "site a leva:\n    " + "\n    ".join(faltando)
            + "\n  compile antes de gerar:\n"
              "    cd editor/vscode && npm install && npx tsc -p ./")


def main():
    _exigir_extensao_compilada()
    saida = RAIZ / "site" / "public" / "dist"
    saida.mkdir(parents=True, exist_ok=True)
    destino = saida / f"dataforge-{VERSAO}.tar.gz"

    with tarfile.open(destino, "w:gz") as tar:
        for item in INCLUIR:
            caminho = RAIZ / item
            if caminho.exists():
                tar.add(caminho, arcname=f"dataforge-{VERSAO}/{item}",
                        filter=filtrar)
            else:
                print(f"  aviso: {item} nao existe, pulando")

        for origem, dentro in EMBUTIR:
            caminho = RAIZ / origem
            if caminho.exists():
                tar.add(caminho, arcname=f"dataforge-{VERSAO}/{dentro}",
                        filter=filtrar)
            else:
                print(f"  aviso: {origem} nao existe, pulando")

    sha = hashlib.sha256(destino.read_bytes()).hexdigest()
    (saida / f"dataforge-{VERSAO}.tar.gz.sha256").write_text(
        f"{sha}  dataforge-{VERSAO}.tar.gz\n", encoding="utf-8")

    print(f"{destino.relative_to(RAIZ)}")
    print(f"  {destino.stat().st_size / 1024:.0f} KB")
    print(f"  sha256 {sha}")

    # Os instaladores tem a versao embutida como padrao. Se ela divergir,
    # quem roda o curl baixa um arquivo que nao existe — foi o que
    # aconteceu no 4.1.0, porque havia duas copias do script e so uma foi
    # atualizada. Agora a copia publicada e gerada aqui, sempre.
    problemas = []
    for origem, destino in [("scripts/instalar.sh", "site/public/instalar.sh"),
                            ("scripts/instalar.ps1", "site/public/instalar.ps1"),
                            ("scripts/diagnostico.ps1",
                             "site/public/diagnostico.ps1")]:
        fonte = RAIZ / origem
        if not fonte.exists():
            continue
        texto = fonte.read_text(encoding="utf-8")
        if VERSAO not in texto:
            problemas.append(f"{origem} nao menciona {VERSAO}")
        alvo = RAIZ / destino
        alvo.write_text(texto, encoding="utf-8")
        alvo.chmod(fonte.stat().st_mode)
        print(f"  {destino} <- {origem}")

    if problemas:
        print("\n  ATENCAO:")
        for p_ in problemas:
            print(f"    {p_}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
