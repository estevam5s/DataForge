"""
Criação de projetos, com a apresentação que a CLI merece.

Um `dataforge new` é a primeira coisa que alguém faz com a linguagem.
Se essa etapa é confusa ou feia, a impressão fica — por isso aqui há
spinner, árvore de arquivos e cores, no mesmo espírito do `nest new`.

Nada disso é enfeite gratuito: o spinner mostra que algo acontece, a
árvore mostra o que foi criado e onde, e a lista de próximos passos
responde "e agora?" sem obrigar a abrir a documentação.
"""

import itertools
import os
import sys
import threading
import time

from .marca import AMARELO, cor, largura_terminal, marca_colorida

#: Quadros do girador. Braille porque ele gira de verdade em qualquer
#: fonte monoespaçada, sem depender de emoji.
QUADROS = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


class Girador:
    """Um spinner que não atrapalha quando a saída não é um terminal.

    Redirecionar a saída para um arquivo com um spinner rodando produz
    milhares de linhas de lixo; aqui, sem tty, ele só imprime o texto
    uma vez e segue.
    """

    def __init__(self, texto: str):
        self.texto = texto
        self._parar = threading.Event()
        self._thread = None
        self._tty = sys.stdout.isatty()

    def __enter__(self):
        if not self._tty:
            print(f"  {self.texto}")
            return self
        self._thread = threading.Thread(target=self._girar, daemon=True)
        self._thread.start()
        return self

    def _girar(self):
        for quadro in itertools.cycle(QUADROS):
            if self._parar.is_set():
                break
            sys.stdout.write(
                f"\r  {cor(quadro, AMARELO)} {self.texto}")
            sys.stdout.flush()
            time.sleep(0.08)

    def __exit__(self, *_):
        self._parar.set()
        if self._thread:
            self._thread.join(timeout=0.4)
        if self._tty:
            # Limpa a linha inteira: um texto mais curto deixaria o
            # rabo do anterior na tela.
            sys.stdout.write("\r" + " " * (largura_terminal() - 1) + "\r")
            sys.stdout.flush()
        return False

    def ok(self, texto: str = ""):
        """Fecha o passo com um visto."""
        self.__exit__()
        print(f"  {cor('✓', '1;32')} {texto or self.texto}")


def arvore(raiz: str, arquivos: dict) -> str:
    """Desenha os arquivos criados como uma árvore.

    Mostrar onde as coisas ficaram poupa o primeiro `ls -R` de todo
    mundo — e deixa claro que um projeto é mais que um arquivo solto.
    """
    # Agrupa por pasta, mantendo a ordem em que foram criados.
    por_pasta: dict[str, list[str]] = {}
    for caminho in arquivos:
        pasta, _, nome = caminho.rpartition("/")
        por_pasta.setdefault(pasta, []).append(nome)

    linhas = [cor(raiz + "/", "1;37")]
    # Raiz primeiro, depois as pastas em ordem.
    pastas = sorted(por_pasta, key=lambda p: (p != "", p))

    # O '└──' marca o último item da árvore INTEIRA, não de cada grupo:
    # senão um arquivo da raiz aparece como último com pastas embaixo.
    total_grupos = len(pastas)

    for i, pasta in enumerate(pastas):
        ultimo_grupo = i == total_grupos - 1
        nomes = por_pasta[pasta]
        recuo = ""

        if pasta:
            marca_p = "└── " if ultimo_grupo else "├── "
            linhas.append(cor(marca_p, "0;90") + cor(pasta + "/", "1;36"))
            recuo = "    " if ultimo_grupo else cor("│   ", "0;90")

        for j, nome in enumerate(nomes):
            # Um arquivo da raiz só é o último se não vier pasta depois.
            ultimo_do_grupo = j == len(nomes) - 1
            ultimo = ultimo_do_grupo and (pasta or ultimo_grupo)
            marca_a = "└── " if ultimo else "├── "
            cor_nome = "1;33" if nome.endswith(".df") else "0;37"
            linhas.append(recuo + cor(marca_a, "0;90") + cor(nome, cor_nome))

    return "\n".join("  " + l for l in linhas)


def criar_projeto(destino: str, modelo: dict, nome: str, versao: str,
                  silencioso: bool = False) -> list[str]:
    """Escreve os arquivos do modelo. Devolve o que foi criado."""
    criados = []
    for relativo, conteudo in modelo["files"].items():
        caminho = os.path.join(destino, relativo)
        os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
        texto = conteudo.replace("{name}", nome).replace("{version}", versao)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        criados.append(relativo)
        if not silencioso:
            # Um respiro por arquivo: sem isso a árvore aparece de uma
            # vez e a sensação é de que nada aconteceu.
            time.sleep(0.03)
    return criados


def apresentar(nome: str, modelo: dict, criados: list[str],
               destino: str) -> None:
    """O que aparece depois que o projeto existe."""
    print()
    print(arvore(nome, dict.fromkeys(criados)))
    print()

    quantos = len(criados)
    linhas = sum(1 for c in criados if c.endswith(".df"))
    print(f"  {cor('✓', '1;32')} {quantos} arquivo(s), "
          f"{cor(modelo['name'], '1;37')}")
    print()

    print(cor("  Comece por:", "1;37"))
    print()
    if destino != ".":
        print(f"    {cor('cd ' + nome, '1;36')}")
    for comando, nota in modelo.get("proximos", [
            ("dataforge run src/main.df", "roda o projeto"),
            ("dataforge test tests/", "roda os testes"),
    ]):
        print(f"    {cor(comando, '1;36')}"
              f"{'   ' + cor('# ' + nota, '0;90') if nota else ''}")
    print()
    print(cor("  documentação: https://dataforge-lang.vercel.app/docs",
              "0;90"))
    print()


def abertura(subtitulo: str) -> None:
    """A marca no topo do comando."""
    print()
    print(marca_colorida())
    print()
    print(f"  {cor('DataForge', '1;37')} {cor(subtitulo, '0;90')}")
    print()
