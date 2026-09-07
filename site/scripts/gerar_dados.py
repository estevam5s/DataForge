#!/usr/bin/env python3
"""Extrai do repositorio DataForge os dados que o site usa.

Roda a partir de site/:  python3 scripts/gerar_dados.py

Escreve lib/dados-gerados.json com as assinaturas reais dos modulos
Arcane, os exercicios com codigo-fonte, as palavras reservadas e as
funcoes embutidas. E a fonte unica desses numeros no site — as paginas
nunca devem repetir um total escrito a mao.
"""

import inspect
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(AQUI)
REPO = os.path.dirname(SITE)
sys.path.insert(0, REPO)

from dataforge.stdlib import get_module, list_modules          # noqa: E402
from dataforge.tokens import KEYWORDS                          # noqa: E402


DESCRICOES = {
    "Arcane.Math": "Matemática, álgebra linear e estatística.",
    "Arcane.Text": "Manipulação de texto, tabelas, caixas e conversão de caixa.",
    "Arcane.IO": "Arquivos, diretórios, JSON e CSV.",
    "Arcane.Regex": "Expressões regulares e padrões prontos.",
    "Arcane.Collections": "Pilha, fila, heap, grafo, união-busca e algoritmos.",
    "Arcane.Functional": "Composição, currying, memoização e preguiça.",
    "Arcane.Data": "Estruturas tabulares e transformação de dados.",
    "Arcane.Analytics": "Agregação, agrupamento e séries.",
    "Arcane.Database": "SQLite com transações reais.",
    "Arcane.Serialization": "JSON, CSV, YAML simples e binário.",
    "Arcane.Cortex": "Aprendizado de máquina didático.",
    "Arcane.OS": "Sistema de arquivos, ambiente e caminhos.",
    "Arcane.Process": "Processos externos e pipes.",
    "Arcane.Time": "Datas, durações e fusos.",
    "Arcane.Http": "Cliente e servidor HTTP.",
    "Arcane.Web": "Requisições, URLs e HTML.",
    "Arcane.Async": "Tarefas, canais e concorrência.",
    "Arcane.Test": "Asserções, suítes, mocks e benchmark.",
    "Arcane.Logging": "Registro com níveis e destinos.",
    "Arcane.Crypto": "Hash, HMAC, base64 e aleatoriedade.",
}


def assinatura(valor):
    """Devolve '(a, b)' para funcao, ou o rotulo do que nao e chamavel."""
    if isinstance(valor, dict):
        return "{ … }"          # sub-namespace, como Math.random
    if not callable(valor):
        return ""               # constante, como Math.PI
    try:
        params = list(inspect.signature(valor).parameters)
    except (TypeError, ValueError):
        return "(…)"
    return "(" + ", ".join(params) + ")"


def coletar_modulos():
    modulos, vistos = {}, set()
    for nome in sorted(set(list_modules())):
        mod = get_module(nome)
        if not isinstance(mod, dict):
            continue
        oficial = mod.get("__name__", nome)
        if oficial in vistos:
            continue
        vistos.add(oficial)

        simbolos = []
        for chave in sorted(k for k in mod if not k.startswith("__")):
            valor = mod[chave]
            simbolos.append({
                "nome": chave,
                "sig": assinatura(valor),
                # 'const' e 'grupo' aparecem na doc com marcacao propria
                "tipo": ("grupo" if isinstance(valor, dict)
                         else "funcao" if callable(valor) else "const"),
            })

        chave_curta = oficial.split(".")[-1].lower()
        modulos[chave_curta] = {
            "nome": oficial,
            "desc": DESCRICOES.get(oficial, ""),
            "funcoes": simbolos,
        }
    return modulos


def coletar_exercicios():
    base = os.path.join(REPO, "exercicios")
    saida = {}
    for modulo in sorted(os.listdir(base)):
        pasta = os.path.join(base, modulo)
        if not os.path.isdir(pasta):
            continue
        itens = []
        for arq in sorted(f for f in os.listdir(pasta)
                          if f.endswith(".df") and re.match(r"^\d{3}_", f)):
            caminho = os.path.join(pasta, arq)
            codigo = open(caminho, encoding="utf-8").read()
            num = arq.split("_")[0]
            titulo = enunciado = ""
            for linha in codigo.splitlines()[:4]:
                if linha.startswith("// Exercicio") and "—" in linha:
                    titulo = linha.split("—", 1)[1].strip()
                elif linha.startswith("// Enunciado:"):
                    enunciado = linha.split(":", 1)[1].strip()
            itens.append({
                "num": num,
                "titulo": titulo,
                "enunciado": enunciado,
                "arquivo": arq,
                "temDoc": os.path.exists(caminho[:-3] + ".md"),
                "codigo": codigo,
            })
        if itens:
            saida[modulo] = itens
    return saida


def coletar_builtins():
    """Lista as embutidas, agrupadas pelos marcadores internos do registro.

    A lista de nomes vem de get_builtins() — essa e a verdade. O arquivo
    e lido apenas para saber em que grupo cada nome foi declarado, pelas
    linhas '# \u2500\u2500 Nome \u2500\u2500'. Assim as constantes (PI, TAU, MAX_INT)
    entram junto com as funcoes, em vez de ficarem de fora.
    """
    from dataforge.builtins import get_builtins
    oficiais = set(get_builtins())

    fonte = open(os.path.join(REPO, "dataforge", "builtins.py"),
                 encoding="utf-8").read()
    linhas = fonte.splitlines()
    inicio = next(i for i, l in enumerate(linhas)
                  if l.startswith("def get_builtins"))

    grupos, atual = {}, "Gerais"
    for linha in linhas[inicio:]:
        marca = re.match(r"\s*#\s*\u2500+\s*(.+?)\s*\u2500+\s*$", linha)
        if marca:
            atual = marca.group(1).strip()
            grupos.setdefault(atual, [])
            continue
        m = re.match(r'\s*["\'](\w+)["\']\s*:', linha)
        if m and m.group(1) in oficiais:
            grupos.setdefault(atual, []).append(m.group(1))

    resultado = {g: sorted(set(f)) for g, f in grupos.items() if f}
    capturadas = {n for f in resultado.values() for n in f}
    faltando = oficiais - capturadas
    if faltando:
        resultado.setdefault("Gerais", []).extend(sorted(faltando))
        resultado["Gerais"] = sorted(set(resultado["Gerais"]))
    return resultado


def main():
    modulos = coletar_modulos()
    builtins = coletar_builtins()
    dados = {
        "modulos": modulos,
        "exercicios": coletar_exercicios(),
        "palavras": sorted(KEYWORDS),
        "builtins": builtins,
        "totalBuiltins": sum(len(v) for v in builtins.values()),
    }

    destino = os.path.join(SITE, "lib", "dados-gerados.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)

    total_simbolos = sum(len(m["funcoes"]) for m in modulos.values())
    total_exerc = sum(len(v) for v in dados["exercicios"].values())
    print(f"lib/dados-gerados.json escrito")
    print(f"  {len(modulos)} módulos, {total_simbolos} símbolos")
    print(f"  {len(dados['exercicios'])} módulos de exercício, {total_exerc} exercícios")
    print(f"  {len(dados['palavras'])} palavras reservadas")
    print(f"  {dados['totalBuiltins']} embutidas em {len(builtins)} grupos")


if __name__ == "__main__":
    main()
