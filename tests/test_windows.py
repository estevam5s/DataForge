"""O Windows: os manifestos, o diagnóstico e o que a página promete.

Três coisas que este arquivo cobra, e cada uma já custou um defeito:

1. **Os manifestos saem do mesmo lugar.** winget, Chocolatey e Scoop
   descrevem o MESMO instalador, e a versão escrita à mão em três
   arquivos divergiria no primeiro release — o sintoma seria um
   `winget install` que baixa um `.exe` que não existe mais.

2. **Nenhum manifesto publicado carrega hash de mentira.** O hash real
   só existe depois de o release construir o `.exe`; até lá, o gerador
   emite um placeholder e avisa. Um manifesto publicado com placeholder
   faz o gerenciador recusar a instalação com uma mensagem sobre
   integridade, e a pessoa conclui que o arquivo foi adulterado.

3. **O tarball que o site serve tem de INSTALAR.** Ver
   `tests/test_editor.py` — o `pyproject.toml` mapeia
   `dataforge.editor` para a pasta `editor/`, e o tarball não a
   incluía: todo `pip install` dele morria com *"package directory
   'editor' does not exist"*, e era o tarball do instalador oficial.
"""

import os
import re
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "packaging"))

from dataforge import __version__                              # noqa: E402

JANELAS = os.path.join(RAIZ, "packaging", "windows")


def _ler(relativo):
    caminho = os.path.join(JANELAS, relativo)
    assert os.path.isfile(caminho), (
        f"{relativo} não existe — rode 'python3 packaging/gerar_pacotes.py'")
    return open(caminho, encoding="utf-8").read()


# ═══ A versão, nos quatro lugares ══════════════════════════

def test_os_tres_manifestos_e_o_inno_falam_a_MESMA_versao():
    """Quatro arquivos descrevem o mesmo instalador."""
    do_inno = re.search(r'#define Versao "([^"]+)"', _ler("dataforge.iss"))
    assert do_inno, "o .iss mudou de forma"

    versoes = {
        "inno": do_inno.group(1),
        "winget/version": re.search(
            r"^PackageVersion: (.+)$",
            _ler("winget/EstevamSouza.DataForge/"
                 "EstevamSouza.DataForge.yaml"), re.M).group(1),
        "winget/installer": re.search(
            r"^PackageVersion: (.+)$",
            _ler("winget/EstevamSouza.DataForge/"
                 "EstevamSouza.DataForge.installer.yaml"), re.M).group(1),
        "choco": re.search(r"<version>([^<]+)</version>",
                           _ler("chocolatey/dataforge.nuspec")).group(1),
        "scoop": re.search(r'"version": "([^"]+)"',
                           _ler("scoop/dataforge.json")).group(1),
    }
    fora = {k: v for k, v in versoes.items() if v != __version__}
    assert not fora, (
        f"a linguagem está em {__version__} e estes discordam: {fora} — "
        f"rode 'python3 packaging/gerar_pacotes.py'")


def test_os_manifestos_apontam_para_um_arquivo_que_o_release_constroi():
    """Um manifesto que aponta para um nome que o release não produz
    responde 404 na máquina de quem tentou instalar."""
    release = open(os.path.join(RAIZ, ".github", "workflows",
                                "release.yml"), encoding="utf-8").read()

    do_exe = re.search(r"InstallerUrl: (\S+)",
                       _ler("winget/EstevamSouza.DataForge/"
                            "EstevamSouza.DataForge.installer.yaml")).group(1)
    do_zip = re.search(r'"url": "([^"]+)"',
                       _ler("scoop/dataforge.json")).group(1)

    inno = _ler("dataforge.iss")

    for url in (do_exe, do_zip):
        assert f"/v{__version__}/" in url, f"{url} não aponta a versão atual"

    # O '.exe' é nomeado pelo Inno, e não pelo workflow.
    nome_do_exe = do_exe.rsplit("/", 1)[1].replace(".exe", "")
    molde = nome_do_exe.replace(__version__, "{#Versao}")
    assert f"OutputBaseFilename={molde}" in inno, (
        f"o manifesto do winget espera '{nome_do_exe}.exe', e o .iss "
        f"produz outro nome — o 'winget install' daria 404")

    # O '.zip' é nomeado pelo job que constrói os binários.
    nome_do_zip = do_zip.rsplit("/", 1)[1]
    assert "windows-x64" in nome_do_zip and "windows-x64" in release, (
        f"o Scoop espera '{nome_do_zip}' e o release.yml não nomeia esse "
        f"artefato")


# ═══ O hash ════════════════════════════════════════════════

def test_o_placeholder_e_reconhecivel_e_o_gerador_AVISA():
    """Um hash de mentira publicado é pior que nenhum manifesto."""
    import gerar_pacotes as g

    assert g.PLACEHOLDER_SHA == "0" * 64
    sha, real = g._sha_do_windows()
    if not real:
        assert sha == g.PLACEHOLDER_SHA, (
            "sem hash conhecido, o gerador tem de usar o placeholder — e "
            "não inventar um valor")


def test_o_release_preenche_o_hash_de_verdade():
    """O caminho que substitui o placeholder tem de existir no workflow.

    Sem isto, o placeholder chegaria publicado e ninguém saberia: o
    gerador avisa no terminal, e terminal de CI ninguém lê duas vezes.
    """
    release = open(os.path.join(RAIZ, ".github", "workflows",
                                "release.yml"), encoding="utf-8").read()
    assert "DF_SHA_WINDOWS" in release, (
        "o release.yml não passa 'DF_SHA_WINDOWS' ao gerador, então os "
        "manifestos do Windows sairiam com hash de placeholder")


# ═══ O Chocolatey ══════════════════════════════════════════

def test_o_choco_instala_em_silencio_e_NAO_reinicia():
    """Reiniciar a máquina de quem rodou um 'choco install' é
    inaceitável, e é o padrão de vários instaladores."""
    texto = _ler("chocolatey/tools/chocolateyinstall.ps1")
    assert "/VERYSILENT" in texto
    assert "/NORESTART" in texto
    assert "checksumType64 = 'sha256'" in texto, (
        "sem 'checksum', o Chocolatey instala o que baixou, seja o que for")


def test_o_choco_sabe_desinstalar():
    texto = _ler("chocolatey/tools/chocolateyuninstall.ps1")
    assert "Uninstall-ChocolateyPackage" in texto
    assert "UninstallString" in texto, (
        "o desinstalador do Inno vive no registro; sem ler o "
        "'UninstallString' o 'choco uninstall' não acha nada")


# ═══ O Scoop ═══════════════════════════════════════════════

def test_o_scoop_usa_o_ZIP_porque_instala_sem_administrador():
    """É o único dos três que não precisa de administrador — e o `.exe`
    do Inno escreve em 'Program Files', que precisa."""
    import json

    d = json.loads(_ler("scoop/dataforge.json"))
    url = d["architecture"]["64bit"]["url"]
    assert url.endswith(".zip"), (
        f"o Scoop tem de usar o zip portátil, e aponta {url}")
    nomes = {par[1] for par in d["bin"]}
    assert nomes == {"dataforge", "df"}, (
        "os dois comandos da linguagem têm de ficar no PATH do usuário")
    assert "autoupdate" in d, "sem 'autoupdate' o bucket envelhece à mão"


# ═══ O diagnóstico ═════════════════════════════════════════

def test_o_diagnostico_confere_as_SEIS_coisas_que_quebram():
    """Cada uma dessas seis já apareceu como 'a instalação falhou'."""
    texto = open(os.path.join(RAIZ, "scripts", "diagnostico.ps1"),
                 encoding="utf-8").read()
    for marca, o_que in (
            ("PSVersionTable", "a versão do PowerShell"),
            ("SecurityProtocol", "o TLS que ele negocia"),
            ("Get-ExecutionPolicy", "a política de execução"),
            ("Invoke-WebRequest", "o site responde"),
            ("python", "há Python (só o .ps1 precisa)"),
            ("USERPROFILE", "o PATH e a instalação anterior")):
        assert marca in texto, f"o diagnóstico não confere {o_que}"


def test_o_diagnostico_NAO_instala_nada():
    """Quem precisa dele é justamente quem não conseguiu instalar."""
    texto = open(os.path.join(RAIZ, "scripts", "diagnostico.ps1"),
                 encoding="utf-8").read()
    # Só o que ele EXECUTA conta, e isso exclui duas coisas:
    #
    #   * o COMENTÁRIO — a linha de uso no cabeçalho traz 'irm … | iex'
    #     de propósito, porque é como a pessoa chama o script;
    #   * a STRING — ele IMPRIME o conselho "use 'irm ... | iex'" para
    #     quem tem a política de execução travada.
    #
    # Acusar os dois seria acusar a documentação e a ajuda do próprio
    # script. O que a regra quer proibir é a CHAMADA.
    sem_comentario = [linha for linha in texto.splitlines()
                      if not linha.lstrip().startswith("#")]
    executavel = "\n".join(
        re.sub(r"'[^']*'|\"[^\"]*\"", "''", linha)
        for linha in sem_comentario)
    for proibido in ("pip install", "venv", "Expand-Archive",
                     "Start-Process", "iex", "Invoke-Expression"):
        assert proibido not in executavel, (
            f"o diagnóstico usa '{proibido}': ele tem de OLHAR, e não agir")


def test_o_diagnostico_prepara_a_saida_antes_de_imprimir():
    """A saída do 5.1 é cp1252, e um acento basta para estourar — no
    meio do relatório, que é o pior lugar possível."""
    texto = open(os.path.join(RAIZ, "scripts", "diagnostico.ps1"),
                 encoding="utf-8").read()
    assert "OutputEncoding" in texto
    assert texto.index("OutputEncoding") < texto.index("Write-Host"), (
        "a codificação tem de ser ajustada ANTES do primeiro Write-Host")


def test_o_diagnostico_sai_com_codigo_util():
    texto = open(os.path.join(RAIZ, "scripts", "diagnostico.ps1"),
                 encoding="utf-8").read()
    assert "exit 1" in texto and "exit 0" in texto, (
        "sem código de saída, ele não serve a quem chama de um script")


# ═══ O instalador .ps1 ═════════════════════════════════════

def test_o_instalador_ps1_liga_o_TLS_12_ANTES_de_baixar():
    """A causa número um: o 'powershell.exe' de todo Windows 10 e 11 é o
    5.1, que negocia TLS 1.0, e o host recusa abaixo de 1.2. O erro que
    aparece não menciona TLS versão nenhuma."""
    texto = open(os.path.join(RAIZ, "scripts", "instalar.ps1"),
                 encoding="utf-8").read()
    assert "SecurityProtocol" in texto
    posicao_tls = texto.index("SecurityProtocol")
    for baixa in ("Invoke-WebRequest", "Invoke-RestMethod", "DownloadFile"):
        if baixa in texto:
            assert posicao_tls < texto.index(baixa), (
                f"o TLS é ligado DEPOIS do primeiro {baixa}")


def test_a_pagina_oferece_as_formas_do_windows_com_o_que_cada_uma_exige():
    pagina = open(os.path.join(RAIZ, "site", "app", "download",
                               "page.tsx"), encoding="utf-8").read()
    for comando in ("winget install EstevamSouza.DataForge",
                    "choco install dataforge",
                    "scoop install dataforge",
                    "diagnostico.ps1"):
        assert comando in pagina, f"a página não oferece '{comando}'"
    # E a forma auditável, que baixa antes de executar.
    assert "-OutFile instalar.ps1" in pagina, (
        "falta a forma que baixa, deixa LER, e só então executa")


def test_o_id_do_winget_e_o_mesmo_na_pagina_e_no_manifesto():
    """Dois nomes para o mesmo pacote fazem 'winget install' falhar com
    'No package found'."""
    import gerar_pacotes as g

    pagina = open(os.path.join(RAIZ, "site", "app", "download",
                               "page.tsx"), encoding="utf-8").read()
    assert f"winget install {g.ID_WINGET}" in pagina
    assert f"PackageIdentifier: {g.ID_WINGET}" in _ler(
        f"winget/{g.ID_WINGET}/{g.ID_WINGET}.yaml")


def test_todo_script_que_a_pagina_manda_CANALIZAR_e_servido_como_texto():
    """`irm .../x.ps1 | iex` não executa nada se o tipo for binário.

    O `Invoke-RestMethod` decide o que devolver pelo `Content-Type`: com
    um tipo textual devolve a string do script, e com
    `application/octet-stream` devolve os **bytes**. O `iex` recebe um
    `Byte[]`, não tem o que executar, e **não dá erro** — o terminal
    volta ao prompt como se tivesse funcionado.

    Foi exatamente o que aconteceu com o harness que eu mesmo escrevi
    para testar na máquina virtual: o `http.server` do Python serve
    `.ps1` como octet-stream, a VM nunca reportou nada, e o silêncio
    parecia problema de rede.

    A Vercel faz a mesma coisa: `instalar.ps1` tinha o cabeçalho
    declarado em `vercel.json` e `diagnostico.ps1` não — e a página
    manda canalizar os dois. Como é um arquivo de configuração de host,
    nada no repositório denunciava.
    """
    import json

    config = os.path.join(RAIZ, "site", "vercel.json")
    vercel = json.load(open(config, encoding="utf-8"))
    cabecalhos = vercel.get("headers") or []

    tipo_de = {}
    for entrada in cabecalhos:
        for c in entrada.get("headers", []):
            if c["key"].lower() == "content-type":
                tipo_de[entrada["source"]] = c["value"].lower()

    pagina = open(os.path.join(RAIZ, "site", "app", "download", "page.tsx"),
                  encoding="utf-8").read()
    docs = os.path.join(RAIZ, "site", "app", "docs", "instalacao", "page.tsx")
    if os.path.isfile(docs):
        pagina += open(docs, encoding="utf-8").read()

    # O que a página manda canalizar: 'irm .../x.ps1 | iex' e
    # 'curl .../x.sh | sh'.
    canalizados = set(re.findall(
        r"dataforge-lang\.vercel\.app(/[\w.-]+\.(?:ps1|sh))\b[^\n]*\|", pagina))
    assert canalizados, (
        "nenhum comando canalizado na página — se a forma mudou, ajuste "
        "este padrão em vez de deixar a trava passar vazia")

    sem_tipo = []
    binarios = []
    for rota in sorted(canalizados):
        arquivo = os.path.join(RAIZ, "site", "public", rota.lstrip("/"))
        if not os.path.isfile(arquivo):
            continue        # coberto por outra trava (o arquivo publicado)
        tipo = tipo_de.get(rota)
        if tipo is None:
            sem_tipo.append(rota)
        elif not (tipo.startswith("text/")
                  or "charset=utf-8" in tipo):
            binarios.append(f"{rota} ({tipo})")

    assert not sem_tipo, (
        "a página manda canalizar estes arquivos e 'site/vercel.json' não "
        "declara o Content-Type deles — a edge serve como "
        "application/octet-stream, e o 'iex' recebe bytes:\n  "
        + "\n  ".join(sem_tipo))
    assert not binarios, (
        "Content-Type binário num script canalizado:\n  "
        + "\n  ".join(binarios))
