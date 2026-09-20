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
import shutil
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
#: terminava com codigo 0: nada recusava.
#:
#: O piso ficava em 2 MB, e media a coisa errada. Com a extensao do VS
#: Code compilada o pacote tem ~6,5 MB; SEM ela, ~1,3 MB — e
#: 'editor/vscode/out/' e gitignored, porque e artefato de build. Numa
#: maquina limpa (a CI, por exemplo) o pacote nasce legitimamente menor,
#: e o piso de 2 MB o recusava: tres testes falhavam desde que ele
#: existe, e a mensagem culpava o 'pip install --target', que estava
#: certo.
#:
#: O piso agora pega o que ele sempre quis pegar — o pacote VAZIO — e
#: quem cobra o conteudo e '_conferir_conteudo', que olha se a
#: linguagem esta lá dentro em vez de contar bytes.
TAMANHO_MINIMO_DO_DEB = 600 * 1024

#: O minimo de modulos da biblioteca que o pacote tem de carregar. Um
#: numero exato envelheceria a cada modulo novo; o que importa e que a
#: 'stdlib' nao chegou vazia.
MINIMO_DE_MODULOS_NO_PACOTE = 40

#: Os arquivos sem os quais o pacote nao instala uma linguagem.
ESSENCIAIS = ("dataforge/interpreter.py", "dataforge/parser.py",
              "dataforge/lexer.py", "dataforge/cli.py",
              "dataforge/stdlib/__init__.py")


def conferir_tamanho(caminho):
    """Recusa, com codigo de saida, um `.deb` vazio."""
    tamanho = os.path.getsize(caminho)
    if tamanho < TAMANHO_MINIMO_DO_DEB:
        raise SystemExit(
            f"o .deb tem {tamanho} bytes, e o piso e "
            f"{TAMANHO_MINIMO_DO_DEB} — ele nao tem a linguagem dentro. "
            f"Confira o 'pip install --target' em '_arvore_instalada'.")
    return tamanho


def _conferir_conteudo(arquivos):
    """A linguagem esta DENTRO? A pergunta que o piso de bytes nao faz.

    Contar bytes confunde 'perdeu a biblioteca' com 'nao compilou a
    extensao do editor'. Aqui a conferencia e pelo que tem de estar lá:
    os cinco arquivos sem os quais nada roda, e uma 'stdlib' que nao
    chegou vazia.
    """
    nomes = {caminho.split("dist-packages/", 1)[-1] for caminho, _, _ in arquivos}
    faltando = [e for e in ESSENCIAIS if e not in nomes]
    if faltando:
        raise SystemExit(
            f"o .deb nao tem {', '.join(faltando)} — ele nao instala uma "
            f"linguagem. Confira o 'pip install --target' em "
            f"'_arvore_instalada'.")
    modulos = len([n for n in nomes
                   if n.startswith("dataforge/stdlib/") and n.endswith(".py")])
    if modulos < MINIMO_DE_MODULOS_NO_PACOTE:
        raise SystemExit(
            f"o .deb tem {modulos} arquivos em 'dataforge/stdlib/', e o "
            f"minimo e {MINIMO_DE_MODULOS_NO_PACOTE} — a biblioteca "
            f"chegou pela metade.")
    return modulos


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
import multiprocessing
import sys

from dataforge.cli import main

# O 'if' NAO e formalidade. 'map_processos' usa o metodo 'spawn' nos
# tres sistemas (ver 'arcane_paralelo._contexto'), e o filho de um
# spawn IMPORTA o modulo principal para reconstruir o estado. Sem a
# guarda, esse import roda o programa de novo dentro de cada
# trabalhador — e a mensagem do Python fala de 'bootstrapping phase',
# tres camadas longe de um usuario que so chamou 'dataforge run'.
if __name__ == "__main__":
    multiprocessing.freeze_support()
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
        # O 'pip' e programa de terceiro: escreve na codificacao do
        # console, e 'text=True' sozinho decodifica com a do SISTEMA. No
        # Windows isso e cp1252, onde cinco bytes nao existem — e a
        # leitura da saida levanta UnicodeDecodeError. O gerador morria
        # com traceback e o .deb nao chegava a ser escrito.
        capture_output=True, text=True,
        encoding="utf-8", errors="replace")
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

    # 'ignore_cleanup_errors': no Windows o 'pip install --target'
    # deixa arquivo somente-leitura, e apagar a arvore levanta
    # PermissionError DEPOIS de o pacote estar pronto — a falha seria na
    # limpeza, e o .deb ja construido nao chegaria a ser escrito.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as arvore:
        _arvore_instalada(arvore)
        arquivos, kb = _arquivos_do_deb(arvore)
        _conferir_conteudo(arquivos)

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


# ═══ Windows: winget, Chocolatey e Scoop ═══════════════════
#
# Sao TRES manifestos para o mesmo instalador, e nenhum deles e opcional
# se a intenca e que alguem no Windows instale a linguagem: o winget vem
# no Windows 11, o Chocolatey e o que uma empresa ja tem, e o Scoop e o
# que quem nao quer administrador usa.
#
# Todos saem daqui, do MESMO lugar, porque a versao escrita a mao em tres
# arquivos divergiria no primeiro release — e o sintoma seria um 'winget
# install' que baixa um .exe que nao existe mais.

#: O identificador do pacote em cada gerenciador. Mudar um destes depois
#: de publicado quebra quem ja instalou: o winget e o choco identificam o
#: pacote instalado por este nome.
ID_WINGET = "EstevamSouza.DataForge"
ID_CHOCO = "dataforge"
ID_SCOOP = "dataforge"

#: O que ainda nao existe, dito aqui: o release constroi so x64. Num
#: Windows ARM o x64 roda por emulacao (o Windows 11 faz isso sozinho), e
#: e por isso que o manifesto declara 'x64' e nao 'neutral' — declarar
#: neutral prometeria um binario nativo que ninguem constroi.
ARQUITETURAS = ("x64",)

PLACEHOLDER_SHA = "0" * 64


def _sha_do_windows():
    """O sha256 do .exe do release, se ele estiver por aqui.

    A ordem: a variavel de ambiente (e como o release passa), depois um
    SHA256SUMS.txt local. Sem nenhum dos dois, devolve o placeholder E
    avisa — um manifesto com hash falso publicado e pior que nenhum
    manifesto, porque o gerenciador recusa a instalacao com uma mensagem
    sobre integridade e a pessoa pensa que o arquivo foi adulterado.
    """
    da_variavel = os.environ.get("DF_SHA_WINDOWS", "").strip().lower()
    if len(da_variavel) == 64:
        return da_variavel, True
    for pasta in (SAIDA, os.path.join(RAIZ, "dist")):
        caminho = os.path.join(pasta, "SHA256SUMS.txt")
        if not os.path.isfile(caminho):
            continue
        with open(caminho, encoding="utf-8") as arquivo:
            for linha in arquivo:
                partes = linha.split()
                if len(partes) >= 2 and partes[1].lstrip("*").endswith(
                        f"windows-x64-setup.exe"):
                    return partes[0].lower(), True
    return PLACEHOLDER_SHA, False


def _url_do_exe():
    return (f"https://github.com/estevam5s/DataForge/releases/download/"
            f"v{__version__}/DataForge-{__version__}-windows-x64-setup.exe")


def gerar_manifestos_do_windows():
    """winget (tres arquivos), Chocolatey (nuspec + install) e Scoop."""
    sha, real = _sha_do_windows()
    url = _url_do_exe()
    escritos = []

    def escrever(relativo, texto):
        caminho = os.path.join(RAIZ, "packaging", "windows", relativo)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(texto)
        escritos.append(os.path.relpath(caminho, RAIZ))

    # ── winget ──────────────────────────────────────────────
    #
    # Sao tres arquivos, e o formato exige os tres: o 'version' aponta o
    # pacote, o 'installer' descreve o binario, o 'locale' e o texto que
    # a pessoa le em 'winget show'.
    pasta = f"winget/{ID_WINGET}"
    escrever(f"{pasta}/{ID_WINGET}.yaml", f"""# Gerado por 'packaging/gerar_pacotes.py'. Nao edite aqui.
PackageIdentifier: {ID_WINGET}
PackageVersion: {__version__}
DefaultLocale: pt-BR
ManifestType: version
ManifestVersion: 1.6.0
""")
    escrever(f"{pasta}/{ID_WINGET}.installer.yaml", f"""# Gerado por 'packaging/gerar_pacotes.py'. Nao edite aqui.
PackageIdentifier: {ID_WINGET}
PackageVersion: {__version__}
InstallerType: inno
Scope: machine
InstallModes:
  - interactive
  - silent
  - silentWithProgress
UpgradeBehavior: install
ReleaseDate: {time.strftime('%Y-%m-%d')}
Installers:
  - Architecture: x64
    InstallerUrl: {url}
    InstallerSha256: {sha.upper()}
ManifestType: installer
ManifestVersion: 1.6.0
""")
    escrever(f"{pasta}/{ID_WINGET}.locale.pt-BR.yaml", f"""# Gerado por 'packaging/gerar_pacotes.py'. Nao edite aqui.
PackageIdentifier: {ID_WINGET}
PackageVersion: {__version__}
PackageLocale: pt-BR
Publisher: Estevam Souza
PublisherUrl: https://dataforge-lang.vercel.app
PackageName: DataForge
PackageUrl: https://dataforge-lang.vercel.app
License: MIT
LicenseUrl: https://github.com/estevam5s/DataForge/blob/main/LICENSE
ShortDescription: Linguagem de programacao interpretada, com {_modulos()} modulos de biblioteca padrao.
Description: >-
  Linguagem de proposito geral com lexer, parser, analisador estatico e
  interpretador proprios. Traz {_modulos()} modulos de biblioteca
  ({_simbolos()} simbolos), dois frameworks web, depurador, LSP e
  gerenciador de pacotes. O instalador embute o runtime: nao e preciso
  ter Python na maquina.
Moniker: dataforge
Tags:
  - programming-language
  - interpreter
  - cli
  - data
ManifestType: defaultLocale
ManifestVersion: 1.6.0
""")

    # ── Chocolatey ──────────────────────────────────────────
    escrever(f"chocolatey/{ID_CHOCO}.nuspec", f"""<?xml version="1.0" encoding="utf-8"?>
<!-- Gerado por 'packaging/gerar_pacotes.py'. Nao edite aqui. -->
<package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd">
  <metadata>
    <id>{ID_CHOCO}</id>
    <version>{__version__}</version>
    <title>DataForge</title>
    <authors>Estevam Souza</authors>
    <projectUrl>https://dataforge-lang.vercel.app</projectUrl>
    <licenseUrl>https://github.com/estevam5s/DataForge/blob/main/LICENSE</licenseUrl>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <projectSourceUrl>https://github.com/estevam5s/DataForge</projectSourceUrl>
    <docsUrl>https://dataforge-lang.vercel.app/docs</docsUrl>
    <bugTrackerUrl>https://github.com/estevam5s/DataForge/issues</bugTrackerUrl>
    <tags>dataforge programming-language interpreter cli</tags>
    <summary>Linguagem interpretada com {_modulos()} modulos de biblioteca padrao.</summary>
    <description>
Linguagem de proposito geral com lexer, parser, analisador estatico e
interpretador proprios. O instalador embute o runtime: nao e preciso ter
Python na maquina.
    </description>
    <releaseNotes>https://github.com/estevam5s/DataForge/releases/tag/v{__version__}</releaseNotes>
  </metadata>
  <files>
    <file src="tools\\**" target="tools" />
  </files>
</package>
""")
    escrever("chocolatey/tools/chocolateyinstall.ps1", f"""# Gerado por 'packaging/gerar_pacotes.py'. Nao edite aqui.
$ErrorActionPreference = 'Stop'

# 'checksum' nao e opcional: sem ele o Chocolatey instala o que baixou,
# seja o que for. Com ele, um arquivo trocado no meio do caminho para a
# instalacao com uma mensagem sobre integridade.
$pacote = @{{
  packageName    = '{ID_CHOCO}'
  fileType       = 'exe'
  url64bit       = '{url}'
  checksum64     = '{sha}'
  checksumType64 = 'sha256'
  # Os silenciosos do Inno Setup. '/NORESTART' porque reiniciar a
  # maquina de quem rodou um 'choco install' e inaceitavel.
  silentArgs     = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  validExitCodes = @(0)
}}

Install-ChocolateyPackage @pacote
""")
    escrever("chocolatey/tools/chocolateyuninstall.ps1", """# Gerado por 'packaging/gerar_pacotes.py'. Nao edite aqui.
$ErrorActionPreference = 'Stop'

# O Inno Setup deixa o proprio desinstalador; o registro e que diz onde.
$chave = Get-ChildItem -Path @(
  'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
  'HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
) -ErrorAction SilentlyContinue |
  Where-Object { $_.GetValue('DisplayName') -like 'DataForge*' } |
  Select-Object -First 1

if (-not $chave) {
  Write-Host 'DataForge nao esta instalado por aqui.'
  return
}

$desinstalador = $chave.GetValue('UninstallString')
Uninstall-ChocolateyPackage -PackageName 'dataforge' -FileType 'exe' `
  -SilentArgs '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART' -File $desinstalador
""")

    # ── Scoop ───────────────────────────────────────────────
    #
    # O Scoop instala SEM administrador, e e o unico dos tres que faz
    # isso. Por isso ele nao usa o .exe do Inno (que escreve em
    # 'Program Files'): usa o ZIP portatil.
    zip = (f"https://github.com/estevam5s/DataForge/releases/download/"
           f"v{__version__}/dataforge-windows-x64.zip")
    escrever(f"scoop/{ID_SCOOP}.json", f"""{{
  "_comentario": "Gerado por 'packaging/gerar_pacotes.py'. Nao edite aqui.",
  "version": "{__version__}",
  "description": "Linguagem interpretada com {_modulos()} modulos de biblioteca padrao.",
  "homepage": "https://dataforge-lang.vercel.app",
  "license": "MIT",
  "architecture": {{
    "64bit": {{
      "url": "{zip}",
      "hash": "{sha if real else PLACEHOLDER_SHA}"
    }}
  }},
  "bin": [["dataforge.exe", "dataforge"], ["dataforge.exe", "df"]],
  "checkver": {{
    "github": "https://github.com/estevam5s/DataForge"
  }},
  "autoupdate": {{
    "architecture": {{
      "64bit": {{
        "url": "https://github.com/estevam5s/DataForge/releases/download/v$version/dataforge-windows-x64.zip"
      }}
    }}
  }}
}}
""")
    return escritos, real


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

    escritos, sha_real = gerar_manifestos_do_windows()
    for caminho in escritos:
        print(f"  {caminho}")
    if not sha_real:
        print("  aviso: o sha256 do .exe do Windows e um PLACEHOLDER.")
        print("         o release o preenche (DF_SHA_WINDOWS), e ha teste")
        print("         proibindo publicar manifesto com placeholder.")

    deb = gerar_deb()
    tamanho = conferir_tamanho(deb)
    print(f"  {os.path.relpath(deb, RAIZ)}  ({tamanho} bytes)")

    # Conferir que o .deb e um 'ar' valido, e nao so um arquivo com o
    # nome certo. Publicar um pacote quebrado e pior que nao publicar.
    with open(deb, "rb") as f:
        assert f.read(8) == b"!<arch>\n", "o .deb nao e um arquivo 'ar'"
    # 'which' e um comando do Unix: no Windows ele nao existe, e o
    # 'subprocess.run' levanta FileNotFoundError — o gerador morria com
    # traceback DEPOIS de ter escrito o .deb inteiro, e tres testes
    # reprovavam mostrando a primeira linha do stdout.
    if shutil.which("dpkg-deb"):
        r = subprocess.run(["dpkg-deb", "--info", deb],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        print(f"  dpkg-deb: {'ok' if r.returncode == 0 else r.stderr[:80]}")
    else:
        print("  (dpkg-deb nao esta nesta maquina; o CI confere)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
