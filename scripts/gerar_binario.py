#!/usr/bin/env python3
"""Empacota o DataForge num executável único, sem Python na máquina.

Por que isto existe
-------------------
Instalar a linguagem exigia ter Python 3.10 ou mais novo. Para quem já
escreve Python isso é nada; para todo mundo mais é a primeira porta e
uma porta fechada — e "instale outra linguagem antes de experimentar
esta" é um pedido difícil de justificar.

O executável carrega o interpretador do Python junto. Quem baixa roda.

O que ele NÃO muda
------------------
A promessa de zero dependências continua valendo onde ela importa: em
`dataforge/`, que só usa a biblioteca padrão. O PyInstaller é ferramenta
de *empacotamento*, roda aqui e não vai para o produto — do mesmo jeito
que o `pytest` não acompanha a linguagem.

Uso
---
    python scripts/gerar_binario.py             # para este sistema
    python scripts/gerar_binario.py --verificar # constrói e testa
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "dist", "bin")

#: Nome com plataforma e arquitetura no próprio arquivo.
#:
#: Um usuário baixa três binários para três máquinas e precisa saber
#: qual é qual depois de o navegador salvar os três na mesma pasta.
_SISTEMAS = {"Darwin": "macos", "Linux": "linux", "Windows": "windows"}


def nome_do_alvo() -> str:
    sistema = _SISTEMAS.get(platform.system(), platform.system().lower())
    arquitetura = platform.machine().lower()
    # 'x86_64' e 'amd64' são a mesma coisa com dois nomes, e 'arm64' e
    # 'aarch64' também. Usar um nome só evita o usuário achar que não
    # existe binário para a máquina dele.
    arquitetura = {"x86_64": "x64", "amd64": "x64",
                   "aarch64": "arm64"}.get(arquitetura, arquitetura)
    return f"dataforge-{sistema}-{arquitetura}"


def _dados_embutidos():
    """A extensão do VS Code viaja dentro do executável.

    'dataforge editor' a instala sem repositório e sem internet; se ela
    ficasse de fora, o comando existiria e não funcionaria.
    """
    origem = os.path.join(RAIZ, "dataforge", "editor")
    if not os.path.isdir(origem):
        return []
    separador = ";" if platform.system() == "Windows" else ":"
    return ["--add-data", f"{origem}{separador}dataforge/editor"]


def construir() -> str:
    os.makedirs(SAIDA, exist_ok=True)
    alvo = nome_do_alvo()

    with tempfile.TemporaryDirectory() as trabalho:
        comando = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", alvo,
            "--distpath", SAIDA,
            "--workpath", os.path.join(trabalho, "build"),
            "--specpath", trabalho,
            "--noconfirm",
            "--clean",
            # Sem console extra no Windows: é uma ferramenta de terminal.
            "--console",
            # A stdlib da linguagem é importada estaticamente em
            # 'stdlib/__init__.py', então a análise a encontra sozinha.
            # 'pkg_resources' e 'setuptools' não: entram por engano pelo
            # metadado do pacote instalado e engordam o binário à toa.
            "--exclude-module", "pkg_resources",
            "--exclude-module", "setuptools",
            "--exclude-module", "pytest",
            "--exclude-module", "PIL",
            "--exclude-module", "tkinter",
            *_dados_embutidos(),
            os.path.join(RAIZ, "scripts", "_entrada_binario.py"),
        ]
        r = subprocess.run(comando, cwd=RAIZ)
        if r.returncode != 0:
            raise SystemExit("o empacotamento falhou")

    caminho = os.path.join(SAIDA, alvo + (".exe" if os.name == "nt" else ""))
    if not os.path.exists(caminho):
        raise SystemExit(f"o empacotador terminou mas '{caminho}' nao existe")
    return caminho


def verificar(caminho: str) -> None:
    """Roda o binário de verdade. Construir sem testar não prova nada.

    Um executável que abre e não consegue rodar um `.df` é pior que
    nenhum: o usuário culpa a linguagem, não o empacotamento.
    """
    programa = '''adopt Arcane.Math as M
adopt Arcane.IO as IO

blueprint Contador(n):
    action dobro():
        yield self.n * 2

c := spawn Contador(21)
assert c.dobro() is 42, "blueprint"
assert M.sqrt(16) is 4.0, "stdlib"
assert [n * n cycle n in [1, 2, 3]] is [1, 4, 9], "compreensao"

async action tarefa(n):
    yield n + 1
assert await tarefa(1) is 2, "async"

out "ok"'''

    with tempfile.TemporaryDirectory() as pasta:
        arquivo = os.path.join(pasta, "prova.df")
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(programa)

        casos = [
            (["--version"], None),
            (["run", arquivo], "ok"),
            (["check", arquivo], None),
            (["lint", arquivo], None),
            # O 'fmt' reescreve; o '--check' logo depois confirma que a
            # formatacao e estavel — que e a propriedade que o
            # formatador promete.
            (["fmt", arquivo], None),
            (["fmt", arquivo, "--check"], None),
            (["run", arquivo], "ok"),
        ]
        for argumentos, esperado in casos:
            r = subprocess.run([caminho] + argumentos, capture_output=True,
                               text=True, encoding="utf-8", timeout=180)
            rotulo = " ".join(argumentos[:2])
            if r.returncode != 0:
                raise SystemExit(
                    f"'{rotulo}' saiu {r.returncode}:\n{r.stdout}\n{r.stderr}")
            if esperado and esperado not in r.stdout:
                raise SystemExit(
                    f"'{rotulo}' nao imprimiu {esperado!r}:\n{r.stdout}")
            print(f"  ok  {rotulo}")


def main() -> int:
    if shutil.which("pyinstaller") is None:
        try:
            import PyInstaller       # noqa: F401
        except ImportError:
            print("o PyInstaller nao esta instalado.")
            print("  pip install pyinstaller")
            return 1

    caminho = construir()
    tamanho = os.path.getsize(caminho) / (1024 * 1024)
    print(f"\n  {caminho}")
    print(f"  {tamanho:.1f} MB")

    if "--verificar" in sys.argv:
        print()
        verificar(caminho)
        print("\n  o binario roda DataForge de verdade")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
