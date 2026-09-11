"""Roda os exemplos da documentação que trazem 'assert'.

`verificar_docs.py` confere que os blocos COMPILAM. Este roda os que
afirmam um resultado — e é isso que pega um exemplo que compila e
responde errado, que é o pior tipo de exemplo: ele ensina com
confiança.

    python3 tools/rodar_exemplos_doc.py            # tudo
    python3 tools/rodar_exemplos_doc.py docs/oop   # só um trecho
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINAS = os.path.join(RAIZ, "site", "app")


def blocos_de(caminho):
    """Os blocos `code` com lang 'df' de uma página.

    A leitura é caractere a caractere e não por expressão regular: uma
    regex com `.*?` atravessa de um bloco para outro quando o primeiro
    não é 'df', e o resultado é um pedaço de texto colado num pedaço de
    código.
    """
    fonte = open(caminho, encoding="utf-8").read()
    saida = []
    i = 0
    marca = "{ code: `"
    while True:
        i = fonte.find(marca, i)
        if i < 0:
            return saida
        inicio = i + len(marca)
        j = inicio
        while True:
            j = fonte.find("`", j)
            if j < 0 or fonte[j - 1] != "\\":
                break
            j += 1
        if j < 0:
            return saida
        corpo = fonte[inicio:j]
        if "lang: 'df'" in fonte[j:j + 40]:
            saida.append(corpo.replace("\\`", "`")
                         .replace("\\${", "${").replace("\\\\", "\\"))
        i = j


def _depende_de_fora(codigo):
    """O exemplo importa algo que não existe fora do contexto dele?

    'adopt meu_pacote' num guia sobre publicar pacotes é correto e não
    roda sozinho — o pacote é hipotético. Rodá-lo só produziria um
    falso alarme, que ensina a ignorar o verificador.
    """
    from dataforge.stdlib import list_modules

    conhecidos = set(list_modules())
    for linha in codigo.split("\n"):
        limpa = linha.strip()
        if not limpa.startswith("adopt "):
            continue
        alvo = limpa[len("adopt "):].split()[0].strip('"')
        if alvo.startswith((".", "/", "{")):
            return True                              # caminho relativo
        raiz = alvo.split(".{")[0]
        if raiz not in conhecidos:
            return True
    return False


def main(filtro=""):
    paginas = [os.path.join(r, a)
               for r, _, fs in os.walk(PAGINAS)
               for a in fs if a == "page.tsx"
               and (not filtro or filtro in os.path.join(r, a))]

    total = falhas = 0
    for caminho in sorted(paginas):
        for codigo in blocos_de(caminho):
            if "assert" not in codigo:
                continue
            if _depende_de_fora(codigo):
                continue
            total += 1
            with tempfile.NamedTemporaryFile("w", suffix=".df", delete=False,
                                             encoding="utf-8") as f:
                f.write(codigo)
                temp = f.name
            r = subprocess.run(
                [sys.executable, "-m", "dataforge", "run", temp],
                capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
            if r.returncode != 0:
                falhas += 1
                print(f"\n\033[1;31m✗\033[0m {os.path.relpath(caminho, RAIZ)}")
                for linha in codigo.split("\n")[:14]:
                    print(f"    {linha}")
                erro = (r.stdout + r.stderr).strip().split("\n")
                print(f"  → {erro[0][:200] if erro else '?'}")
            os.unlink(temp)

    print()
    if falhas:
        print(f"\033[1;31m  {falhas} de {total} exemplo(s) com assert "
              f"falharam\033[0m")
        sys.exit(1)
    print(f"\033[1;32m  os {total} exemplos com assert rodam\033[0m")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
