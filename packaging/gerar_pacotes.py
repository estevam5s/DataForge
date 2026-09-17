#!/usr/bin/env python3
"""Gera os pacotes de distribuição: `.deb` e o `PKGBUILD` do Arch.

Por que aqui e não no CI
------------------------
O `.deb` é um `ar` com três membros — dá para montar com a biblioteca
padrão, sem `dpkg`, e por isso roda em qualquer máquina. O `PKGBUILD` é
um arquivo de texto que só precisa da versão certa.

O que este arquivo **não** faz é fingir que publica. Gerar o pacote e
publicá-lo são coisas diferentes: o `.deb` sai aqui, e subir para um
repositório apt é uma decisão de quem mantém.

Uso
---
    python packaging/gerar_pacotes.py            # gera em dist/pacotes/
    python packaging/gerar_pacotes.py --check    # só confere a versão
"""

import hashlib
import io
import os
import subprocess
import sys
import tarfile
import tempfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import __version__, marca  # noqa: E402

marca.preparar_saida()

#: Onde o .deb e escrito. 'DF_PACOTES_SAIDA' troca o destino, e e o que os
#: testes usam: tres deles geravam o pacote em 'dist/pacotes/' do proprio
#: repositorio, e dois liam 'debs[0]' — um .deb de versao antiga deixado
#: ali seria lido no lugar do que acabou de ser gerado.
SAIDA = os.environ.get("DF_PACOTES_SAIDA") or os.path.join(RAIZ, "dist", "pacotes")


#: Abaixo disto o `.deb` nao tem a linguagem dentro.
#:
#: O publicado na 1.0.0 tinha 1.194 bytes, e o gerador que o produziu
#: terminava com codigo 0: nada recusava. O real tem 6,5 MB; o piso fica
#: em 2 MB para o pacote poder emagrecer sem falso alarme, e bem acima de
#: um pacote que perdeu a biblioteca (~300 KB).
TAMANHO_MINIMO_DO_DEB = 2 * 1024 * 1024


def conferir_tamanho(caminho):
    """Recusa, com codigo de saida, um `.deb` pequeno demais."""
    tamanho = os.path.getsize(caminho)
    if tamanho < TAMANHO_MINIMO_DO_DEB:
        raise SystemExit(
            f"o .deb tem {tamanho} bytes, e o piso e "
            f"{TAMANHO_MINIMO_DO_DEB} — ele nao tem a linguagem dentro. "
            f"Confira o 'pip install --target' em '_arvore_instalada'.")
    return tamanho


def _oficiais():
    """Os nomes oficiais dos modulos, sem contar apelido duas vezes."""
    from dataforge.stdlib import get_module, list_modules
    return {get_module(n)["__name__"] for n in set(list_modules())}


def _modulos():
    return len(_oficiais())


def _simbolos():
    from dataforge.stdlib import get_module
    return sum(len([k for k in get_module(n) if not k.startswith("__")])
               for n in _oficiais())


def _ar(destino, membros):
    """Escreve um arquivo `ar` — o formato do `.deb`.

    São três membros, nesta ordem exata: `debian-binary`, `control.tar.gz`
    e `data.tar.gz`. O `dpkg` depende da ordem.
    """
    with open(destino, "wb") as f:
        f.write(b"!<arch>\n")
        for nome, dados in membros:
            cabecalho = (
                f"{nome:<16}"
                f"{int(time.time()):<12}"
                f"{0:<6}{0:<6}{0o100644:<8o}{len(dados):<10}"
            ).encode() + b"`\n"
            f.write(cabecalho)
            f.write(dados)
            if len(dados) % 2:
                f.write(b"\n")           # membros têm tamanho par


def _tar_gz(arquivos):
    """Um `.tar.gz` na memória, reprodutível.

    Um `conteudo` de `None` é uma **pasta**, e as pastas não são
    opcionais: o `dpkg` cria cada caminho na ordem em que aparece no
    tar e não inventa o que falta. Sem elas a instalação para no
    primeiro arquivo, com uma mensagem que culpa o arquivo:

        unable to create '/usr/lib/python3/dist-packages/dataforge/
        __init__.py.dpkg-new': No such file or directory
    """
    buffer = io.BytesIO()
    # 'GNU_FORMAT', e nao o PAX que o Python usa por padrao desde o
    # 3.8. O 'dpkg' le ustar e GNU, e recusa o cabecalho estendido do
    # PAX — que o tarfile emite sozinho assim que um caminho passa de
    # 100 caracteres, o que aqui acontece dentro de 'editor/vscode/
    # node_modules/'. A mensagem nao ajuda nada:
    #
    #     corrupted filesystem tarfile in package archive:
    #     unsupported PAX tar header type 'x'
    with tarfile.open(fileobj=buffer, mode="w:gz",
                      format=tarfile.GNU_FORMAT) as tar:
        for caminho_interno, conteudo, modo in arquivos:
            info = tarfile.TarInfo(caminho_interno)
            if conteudo is None:
                info.type = tarfile.DIRTYPE
                info.size = 0
            else:
                info.size = len(conteudo)
            info.mode = modo
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = "root"
            tar.addfile(info, io.BytesIO(conteudo or b""))
    return buffer.getvalue()


def _com_as_pastas(arquivos):
    """Cada arquivo precedido pelas pastas que o contêm.

    A ordem importa — `dpkg` desempacota sequencialmente — e por isso é
    ordenada por caminho, com a pasta sempre antes do que está dentro
    dela.
    """
    pastas = set()
    for caminho, _, _ in arquivos:
        partes = caminho.split("/")[1:-1]      # sem o './' e sem o nome
        for i in range(1, len(partes) + 1):
            pastas.add("./" + "/".join(partes[:i]))
    entradas = [(p, None, 0o755) for p in pastas] + list(arquivos)
    return sorted(entradas, key=lambda e: (e[0], e[1] is not None))


#: O comando `df` NAO entra no `.deb`.
#:
#: Ele existe no wheel do PyPI, onde mora numa venv e sombrea apenas o
#: que o usuario pediu. Em `/usr/bin`, instalado por um pacote de
#: sistema, ele passaria por cima do `df` do coreutils — o comando que
#: mostra espaco em disco, que scripts de administracao chamam e que
#: ninguem espera que uma linguagem substitua.
COMANDOS = ["dataforge"]

#: O lancador em `/usr/bin/dataforge`.
#:
#: Nao e o script que o `pip` gera: aquele carrega o `entry_points` pelo
#: metadado, o que exige o `dist-info` intacto e o `importlib.metadata`.
#: Este chama a funcao direto — duas linhas que nao tem como envelhecer.
LANCADOR = """#!/usr/bin/python3
import sys
from dataforge.cli import main
sys.exit(main())
"""


def _arvore_instalada(pasta):
    """Instala o pacote numa pasta, do jeito que o `pip` instalaria.

    A lista de arquivos vem do `pyproject.toml`, pelo proprio `pip`, e
    nao de uma segunda lista aqui. Foi de proposito: uma lista escrita
    a mao num empacotador divergiria na primeira vez que o wheel
    ganhasse um arquivo — e o sintoma seria um `.deb` que instala uma
    linguagem com um modulo faltando.
    """
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", RAIZ, "--target", pasta,
         "--no-deps", "--no-compile", "--quiet"],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"o 'pip install --target' falhou:\n{r.stderr[-800:]}")
    if not os.path.isdir(os.path.join(pasta, "dataforge")):
        raise SystemExit("o 'pip install --target' nao criou 'dataforge/'")


def _arquivos_do_deb(arvore):
    """`[(caminho_no_pacote, bytes, modo)]`, e o tamanho em KB."""
    destino = "./usr/lib/python3/dist-packages"
    arquivos = []
    total = 0
    for raiz, pastas, nomes in os.walk(arvore):
        # O '__pycache__' e compilado para o Python DESTA maquina. Num
        # pacote 'all', a maquina que instala pode ter outra versao, e
        # um .pyc de versao errada e ignorado — 29 MB de peso morto.
        pastas[:] = [d for d in sorted(pastas) if d != "__pycache__"]
        # 'bin/' sao os lancadores do pip, substituidos pelo LANCADOR.
        if os.path.relpath(raiz, arvore).split(os.sep)[0] == "bin":
            continue
        for nome in sorted(nomes):
            caminho = os.path.join(raiz, nome)
            if os.path.islink(caminho):
                continue
            with open(caminho, "rb") as f:
                dados = f.read()
            relativo = os.path.relpath(caminho, arvore).replace(os.sep, "/")
            modo = 0o755 if os.access(caminho, os.X_OK) else 0o644
            arquivos.append((f"{destino}/{relativo}", dados, modo))
            total += len(dados)

    for comando in COMANDOS:
        arquivos.append((f"./usr/bin/{comando}", LANCADOR.encode(), 0o755))
        total += len(LANCADOR)

    with open(os.path.join(RAIZ, "LICENSE"), "rb") as f:
        licenca = f.read()
    doc = "./usr/share/doc/dataforge"
    arquivos.append((f"{doc}/copyright", licenca, 0o644))
    arquivos.append((
        f"{doc}/README.Debian",
        f"DataForge {__version__}\n\n"
        f"A linguagem esta em /usr/lib/python3/dist-packages/dataforge.\n"
        f"O comando e 'dataforge'; comece por 'dataforge repl'.\n\n"
        f"O apelido 'df' do PyPI nao e instalado: em /usr/bin ele\n"
        f"sombrearia o df do coreutils.\n\n"
        f"https://dataforge-lang.vercel.app/docs\n".encode(), 0o644))
    total += len(licenca)
    return arquivos, max(1, total // 1024)


def gerar_deb():
    """Um `.deb` que instala a linguagem, e nao um que a baixa.

    A primeira versao era um `postinst` de tres linhas chamando
    `pip install dataforge-lang=={versao}`. Dois problemas, e o segundo
    e o que importa:

    1. `dataforge-lang` **nao esta no PyPI** — 404. O `postinst` saia
       com erro, e o `dpkg` deixava o pacote meio configurado.
    2. Mesmo que estivesse: um pacote de 1,2 KB cujo corpo e um
       download nao instala nada em maquina sem rede, e passa por cima
       da politica de quem escolheu uma distro justamente para nao ter
       `pip install` como raiz.

    O `dpkg-deb --info` do CI passava nas duas versoes: ele confere que
    o `ar` esta bem formado. O pacote estava bem formado e vazio —
    `data.tar.gz` tinha **um** arquivo, um README.
    """
    os.makedirs(SAIDA, exist_ok=True)
    destino = os.path.join(SAIDA, f"dataforge_{__version__}_all.deb")

    with tempfile.TemporaryDirectory() as arvore:
        _arvore_instalada(arvore)
        arquivos, kb = _arquivos_do_deb(arvore)

    modelo = os.path.join(RAIZ, "packaging", "debian", "control.template")
    with open(modelo, encoding="utf-8") as f:
        control = (f.read()
                   .replace("{VERSAO}", __version__)
                   # A descricao dizia "37 modulos" quando eram 39.
                   # Numero escrito a mao no modelo de um pacote
                   # envelhece sem ninguem ver: o '.deb' e gerado no
                   # release, e ninguem le a descricao dele duas vezes.
                   .replace("{MODULOS}", str(_modulos()))
                   .replace("{SIMBOLOS}", str(_simbolos()))
                   .replace("{TAMANHO}", str(kb)))

    # Sem isto, cada 'dataforge' recompila a arvore inteira: o
    # dist-packages nao e escrivel pelo usuario, entao o .pyc nunca fica
    # gravado e o custo se repete a cada chamada.
    postinst = """#!/bin/sh
set -e
if command -v py3compile >/dev/null 2>&1; then
    py3compile -p dataforge 2>/dev/null || true
fi
exit 0
"""
    prerm = """#!/bin/sh
set -e
if command -v py3clean >/dev/null 2>&1; then
    py3clean -p dataforge 2>/dev/null || true
fi
exit 0
"""

    # O 'md5sums' e o que faz 'dpkg --verify' e 'debsums' funcionarem.
    md5 = "".join(
        f"{hashlib.md5(dados).hexdigest()}  {caminho[2:]}\n"
        for caminho, dados, _ in arquivos
        if not caminho.startswith("./usr/share/doc/"))

    controle = _tar_gz([
        ("./control", control.encode(), 0o644),
        ("./md5sums", md5.encode(), 0o644),
        ("./postinst", postinst.encode(), 0o755),
        ("./prerm", prerm.encode(), 0o755),
    ])

    _ar(destino, [
        ("debian-binary", b"2.0\n"),
        ("control.tar.gz", controle),
        ("data.tar.gz", _tar_gz(_com_as_pastas(arquivos))),
    ])
    return destino


def atualizar_pkgbuild():
    """Mantém a versão do `PKGBUILD` em dia com a da linguagem."""
    caminho = os.path.join(RAIZ, "packaging", "arch", "PKGBUILD")
    with open(caminho, encoding="utf-8") as f:
        texto = f.read()

    import re
    novo = re.sub(r"^pkgver=.*$", f"pkgver={__version__}", texto,
                  count=1, flags=re.M)
    if novo != texto:
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(novo)
    return caminho, novo != texto


def main():
    import re

    caminho_pkg = os.path.join(RAIZ, "packaging", "arch", "PKGBUILD")
    with open(caminho_pkg, encoding="utf-8") as f:
        achado = re.search(r"^pkgver=(.+)$", f.read(), re.M)
    versao_arch = achado.group(1) if achado else "?"

    if "--check" in sys.argv:
        if versao_arch != __version__:
            print(f"  o PKGBUILD esta em {versao_arch} e a linguagem "
                  f"em {__version__}")
            return 1
        print(f"  PKGBUILD em dia ({__version__})")
        return 0

    caminho, mudou = atualizar_pkgbuild()
    print(f"  {os.path.relpath(caminho, RAIZ)}"
          f"{' (versao atualizada)' if mudou else ''}")

    deb = gerar_deb()
    tamanho = conferir_tamanho(deb)
    print(f"  {os.path.relpath(deb, RAIZ)}  ({tamanho} bytes)")

    # Conferir que o .deb e um 'ar' valido, e nao so um arquivo com o
    # nome certo. Publicar um pacote quebrado e pior que nao publicar.
    with open(deb, "rb") as f:
        assert f.read(8) == b"!<arch>\n", "o .deb nao e um arquivo 'ar'"
    if subprocess.run(["which", "dpkg-deb"], capture_output=True).returncode == 0:
        r = subprocess.run(["dpkg-deb", "--info", deb],
                           capture_output=True, text=True)
        print(f"  dpkg-deb: {'ok' if r.returncode == 0 else r.stderr[:80]}")
    else:
        print("  (dpkg-deb nao esta nesta maquina; o CI confere)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
