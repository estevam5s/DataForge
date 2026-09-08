"""Gera a parte de índice do exercicios/README.md a partir dos arquivos.

Escrita à mão, a lista envelhece: os módulos 21 a 26 existiam e o índice
parava no 20, e ninguém percebeu — porque conferir 216 linhas à mão não
é algo que se faça duas vezes.

    python3 tools/gerar_indice_exercicios.py           # reescreve
    python3 tools/gerar_indice_exercicios.py --check   # só confere
"""
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXERCICIOS = os.path.join(RAIZ, "exercicios")
README = os.path.join(EXERCICIOS, "README.md")

#: Onde o índice começa e termina. O que está fora é escrito à mão.
INICIO = "<!-- indice:inicio -->"
FIM = "<!-- indice:fim -->"


def titulo_de(caminho):
    """O assunto do exercício, tirado da segunda linha de comentário.

    O formato é `// Exercicio NNN — Assunto`, e é o mesmo em todos.
    """
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            limpa = linha.strip()
            if not limpa.startswith("//"):
                continue
            texto = limpa.lstrip("/ ").strip()
            casou = re.match(r"Exerc[ií]cio\s+\d+\s*[—–-]\s*(.+)", texto)
            if casou:
                return casou.group(1).strip()
    return os.path.basename(caminho).replace(".df", "").split("_", 1)[-1]


def modulos():
    for nome in sorted(os.listdir(EXERCICIOS)):
        pasta = os.path.join(EXERCICIOS, nome)
        if not os.path.isdir(pasta) or not nome[0].isdigit():
            continue
        # Arquivo que comeca com LETRA e modulo auxiliar: ele existe
        # para ser importado por um exercicio, nao executado. E a mesma
        # regra que 'run_all.py' aplica — sem ela, o indice contava 219
        # onde a suite roda 216.
        arquivos = sorted(f for f in os.listdir(pasta)
                          if f.endswith(".df") and f[0].isdigit())
        if arquivos:
            yield nome, pasta, arquivos


def gerar():
    partes = []
    total = 0

    for nome, pasta, arquivos in modulos():
        numero, _, rotulo = nome.partition("-")
        rotulo = rotulo.replace("-", " ")
        rotulo = rotulo[:1].upper() + rotulo[1:]

        com_doc = sum(1 for f in arquivos
                      if os.path.isfile(os.path.join(pasta,
                                                     f.replace(".df", ".md"))))
        nota = " · com documentação `.md`" if com_doc == len(arquivos) else ""

        partes.append(f"\n## {numero} — {rotulo}\n")
        partes.append(f"\n*{len(arquivos)} exercícios{nota}*\n")
        partes.append("\n| # | Exercício | Assunto |\n|---|-----------|---------|\n")

        for arquivo in arquivos:
            caminho = os.path.join(pasta, arquivo)
            n = arquivo.split("_", 1)[0]
            doc = arquivo.replace(".df", ".md")
            link = f"[`{arquivo}`]({nome}/{arquivo})"
            if os.path.isfile(os.path.join(pasta, doc)):
                link += f" · [doc]({nome}/{doc})"
            partes.append(f"| {n} | {link} | {titulo_de(caminho)} |\n")
            total += 1

    partes.append(f"\n---\n\n**Total: {total} exercícios.** Todos passam — o "
                  f"estado esperado do repositório é verde. Se algum falhar, é "
                  f"regressão no interpretador: veja\n"
                  f"[`../CLAUDE.md`](../CLAUDE.md).\n")
    return "".join(partes)


def main():
    with open(README, encoding="utf-8") as f:
        atual = f.read()

    if INICIO not in atual:
        # Primeira vez: acha onde o índice antigo começa e o substitui.
        marca = "\n## 01"
        if marca not in atual:
            print("não achei onde o índice começa", file=sys.stderr)
            sys.exit(1)
        cabeca = atual[:atual.index(marca)]
        depois = atual[atual.index("## Depois dos exercícios"):]
        novo = f"{cabeca}{INICIO}\n{gerar()}\n{FIM}\n\n{depois}"
    else:
        cabeca = atual[:atual.index(INICIO) + len(INICIO)]
        depois = atual[atual.index(FIM):]
        novo = f"{cabeca}\n{gerar()}\n{depois}"

    if "--check" in sys.argv:
        if novo != atual:
            print("o índice está desatualizado; rode sem --check",
                  file=sys.stderr)
            sys.exit(1)
        print("o índice está em dia")
        return

    with open(README, "w", encoding="utf-8") as f:
        f.write(novo)
    total = sum(len(a) for _, _, a in modulos())
    print(f"  {total} exercícios em {len(list(modulos()))} módulos")


if __name__ == "__main__":
    main()
