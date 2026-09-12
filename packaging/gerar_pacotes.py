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

import io
import os
import subprocess
import sys
import tarfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import __version__, marca  # noqa: E402

marca.preparar_saida()

SAIDA = os.path.join(RAIZ, "dist", "pacotes")


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
    """Um `.tar.gz` na memória, reprodutível."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for caminho_interno, conteudo, modo in arquivos:
            info = tarfile.TarInfo(caminho_interno)
            info.size = len(conteudo)
            info.mode = modo
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = "root"
            tar.addfile(info, io.BytesIO(conteudo))
    return buffer.getvalue()


def gerar_deb():
    """Um `.deb` que instala a linguagem pelo pip do sistema.

    É deliberadamente fino: o corpo do pacote é um script `postinst` que
    chama `pip install`. Empacotar a árvore inteira de `site-packages`
    num `.deb` exigiria repetir o que o pip já sabe fazer, e divergiria
    na primeira mudança de dependência.
    """
    os.makedirs(SAIDA, exist_ok=True)
    destino = os.path.join(SAIDA, f"dataforge_{__version__}_all.deb")

    modelo = os.path.join(RAIZ, "packaging", "debian", "control.template")
    with open(modelo, encoding="utf-8") as f:
        control = (f.read()
                   .replace("{VERSAO}", __version__)
                   # A descricao dizia "37 modulos" quando eram 39.
                   # Numero escrito a mao no modelo de um pacote
                   # envelhece sem ninguem ver: o '.deb' e gerado no
                   # release, e ninguem le a descricao dele duas vezes.
                   .replace("{MODULOS}", str(_modulos()))
                   .replace("{SIMBOLOS}", str(_simbolos())))

    postinst = f"""#!/bin/sh
set -e
# Instala no Python do sistema. Falhar aqui NAO pode deixar o pacote
# meio instalado, entao o erro e explicito.
python3 -m pip install --upgrade --break-system-packages \\
    "dataforge-lang=={__version__}" 2>/dev/null \\
  || python3 -m pip install --upgrade "dataforge-lang=={__version__}"
echo "DataForge {__version__} instalado. Comece por: dataforge repl"
"""
    prerm = """#!/bin/sh
set -e
python3 -m pip uninstall -y dataforge-lang 2>/dev/null || true
"""

    controle = _tar_gz([
        ("./control", control.encode(), 0o644),
        ("./postinst", postinst.encode(), 0o755),
        ("./prerm", prerm.encode(), 0o755),
    ])
    dados = _tar_gz([
        ("./usr/share/doc/dataforge/README.Debian",
         b"DataForge e instalado pelo pip no postinst.\n"
         b"Veja https://dataforge-lang.vercel.app/docs\n", 0o644),
    ])

    _ar(destino, [
        ("debian-binary", b"2.0\n"),
        ("control.tar.gz", controle),
        ("data.tar.gz", dados),
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
    tamanho = os.path.getsize(deb)
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
