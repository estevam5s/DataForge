#!/usr/bin/env python3
"""
Empacota a linguagem para rodar no navegador.

    python3 scripts/gerar_runtime_web.py

Escreve site/public/dataforge-web.zip — o pacote `dataforge/` inteiro,
que o Pyodide descompacta e importa.

Isto só é possível porque a linguagem é Python puro sem dependência de
runtime: não há extensão em C para compilar, e o interpretador roda no
WebAssembly do navegador exatamente como roda no terminal. É a mesma
implementação, não uma reimplementação em JavaScript que divergiria na
primeira correção de bug.
"""

import os
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "site", "public", "dataforge-web.zip")

IGNORAR = {"__pycache__", ".pyc", ".DS_Store"}

#: Os modulos auxiliares dos exercicios.
#:
#: Um exercicio como o 099 faz 'adopt geometria as geo', e o
#: 'geometria.df' mora ao lado dele na pasta. No navegador nao ha
#: "ao lado": o programa e um texto solto, e o 'adopt' falhava com
#:
#:     Module 'geometria' not found. Looked in the standard library,
#:     next to example.df, and in forge_modules/
#:
#: — um erro que nao e do codigo do exercicio, e que aparecia para
#: quem estivesse aprendendo justamente o capitulo de MODULOS.
#:
#: Eles vao no CAMINHO REAL — 'exercicios/09-modulos/geometria.df' —, e
#: quem roda um exercicio diz de que pasta ele veio. Jogar todos na raiz
#: seria mais simples e esta errado: ha dois 'geometria.df', um em cada
#: capitulo, e eles DIFEREM. Um sobrescreveria o outro, e o exercicio de
#: um capitulo passaria a importar o modulo do outro — calado.
AUXILIARES = ("exercicios/09-modulos", "exercicios/16-modulos-e-projetos")


def main():
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    quantos = 0

    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as z:
        for pasta, _, arquivos in os.walk(os.path.join(RAIZ, "dataforge")):
            if any(marca in pasta for marca in IGNORAR):
                continue
            for arquivo in sorted(arquivos):
                if not arquivo.endswith(".py"):
                    continue
                caminho = os.path.join(pasta, arquivo)
                dentro = os.path.relpath(caminho, RAIZ)
                info = zipfile.ZipInfo(dentro)
                # mtime fixo: o zip precisa ser byte a byte igual entre
                # builds, senão o navegador rebaixa o cache a cada deploy.
                info.date_time = (1980, 1, 1, 0, 0, 0)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                with open(caminho, "rb") as f:
                    z.writestr(info, f.read())
                quantos += 1

        for relativa in AUXILIARES:
            pasta = os.path.join(RAIZ, relativa)
            if not os.path.isdir(pasta):
                continue
            for arquivo in sorted(os.listdir(pasta)):
                # So os auxiliares: o que comeca com digito e o
                # exercicio em si, e ele nao vai no pacote.
                if not arquivo.endswith(".df") or arquivo[0].isdigit():
                    continue
                info = zipfile.ZipInfo(f"{relativa}/{arquivo}")
                info.date_time = (1980, 1, 1, 0, 0, 0)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                with open(os.path.join(pasta, arquivo), "rb") as f:
                    z.writestr(info, f.read())
                quantos += 1

    tamanho = os.path.getsize(DESTINO) / 1024
    print(f"{os.path.relpath(DESTINO, RAIZ)}")
    print(f"  {quantos} módulos, {tamanho:.0f} KB")


if __name__ == "__main__":
    main()
