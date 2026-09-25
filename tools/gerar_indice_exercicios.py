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
sys.path.insert(0, RAIZ)

from dataforge import marca                                 # noqa: E402

# A tabela de trilhas escreve "→", e o console do Windows morre ao
# imprimir o que não cabe na página de código dele.
marca.preparar_saida()
README = os.path.join(EXERCICIOS, "README.md")

#: Onde o índice começa e termina. O que está fora é escrito à mão —
#: menos os NÚMEROS e a tabela de trilhas, que '_cabeca_em_dia' mantém.
INICIO = "<!-- indice:inicio -->"
FIM = "<!-- indice:fim -->"

#: As trilhas e os níveis: o mesmo arquivo que a página /docs/exercicios lê.
TRILHAS = os.path.join(EXERCICIOS, "trilhas.json")


def _cabeca_em_dia(cabeca):
    """O texto escrito à mão, com os números e as trilhas do disco.

    O cabeçalho dizia "397 exercícios em 58 módulos" quando eram 399 em
    59, e o '--check' passava: ele só olhava a parte gerada. Um número
    escrito à mão envelhece calado, e o README é a primeira coisa que se
    lê na pasta. A tabela de trilhas parava no módulo 20 pelo mesmo motivo.
    """
    import json

    lista = list(modulos())
    total = sum(len(a) for _, _, a in lista)
    cabeca = re.sub(r"\*\*\d+ exercícios em \d+ módulos\*\*",
                    f"**{total} exercícios em {len(lista)} módulos**", cabeca)
    cabeca = re.sub(r"# todos os \d+", f"# todos os {total}", cabeca)

    nomes = {nome[:2]: nome for nome, _, _ in lista}
    dados = json.load(open(TRILHAS, encoding="utf-8"))
    linhas = ["| Se você quer… | Comece por |", "|---------------|------------|"]
    for trilha in dados["trilhas"]:
        passos = " → ".join(f"[{m}]({nomes[m]}/)" for m in trilha["modulos"])
        linhas.append(f"| {trilha['quero']} | {passos} |")
    tabela = "\n".join(linhas) + "\n"
    return re.sub(r"(## Trilhas\n\n)\|.*?\n(?=\n)",
                  lambda m: m.group(1) + tabela, cabeca, count=1, flags=re.S)


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
        novo = f"{_cabeca_em_dia(cabeca)}\n{gerar()}\n{depois}"

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
