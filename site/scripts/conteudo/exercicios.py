# -*- coding: utf-8 -*-
"""As páginas dos exercícios — geradas dos próprios arquivos .df.

Escritas à mão, elas pararam no módulo 23: os módulos 24 (banco de
dados), 25 (Crucible) e 26 (complexidade) existiam no repositório e não
apareciam no site. E o índice ainda anunciava "os vinte módulos" e
"todos os 180" quando já eram 26 e 216.

Nada aqui é digitado duas vezes: o título e o enunciado saem das duas
primeiras linhas de comentário de cada exercício, que é onde eles já
estavam.
"""

import glob
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
EXERCICIOS = os.path.join(RAIZ, "exercicios")

#: O assunto de cada módulo, para a página de índice. O que o nome da
#: pasta não diz — 'controle-fluxo' não explica o que se aprende ali.
ASSUNTOS = {
    "01-fundamentos": "tipos, operadores, precedência, conversão e anotações",
    "02-controle-fluxo": "given/orif/otherwise, ternário, match e guardas",
    "03-colecoes": "cluster e vault, fatias, spread e compreensões",
    "04-strings": "interpolação, métodos de texto, formatação e regex",
    "05-acoes": "parâmetros, padrões, retorno, closures e recursão",
    "06-blueprints": "campos, métodos, herança, traits e records",
    "07-erros": "monitor/handle/ensure, trigger, retry e defer",
    "08-pipelines": "sift, morph, distill e composição",
    "09-modulos": "adopt, relay, seleção e apelidos",
    "10-avancado": "decoradores, generators, threads e canais",
    "11-tipos-e-checagem": "anotações, o analisador estático e generics",
    "12-records-e-enums": "imutabilidade, 'with' e enums com valor",
    "13-desestruturacao": "cluster, vault, rest e troca de variáveis",
    "14-pattern-matching": "point, when, tipos, sequências e vaults",
    "15-streams-e-generators": "stream action, emit, take e sequências infinitas",
    "16-modulos-e-projetos": "forge.toml, pacotes e organização",
    "17-tempo-e-sistema": "datas, durações, ambiente e processos",
    "18-dados-e-persistencia": "JSON, CSV, SQLite e serialização",
    "19-concorrencia": "threads, canais, tarefas e paralelismo",
    "20-projetos-finais": "programas completos, de ponta a ponta",
    "21-oop-avancado": "propriedades, estáticos, operadores, SOLID",
    "22-web-kiln": "rotas, respostas, templates e estáticos",
    "23-dados-e-planilhas": "frames, agregação e .xlsx",
    "24-banco-de-dados": "Forge: conexão, consultas, transações e ORM",
    "25-testes-crucible": "suítes, matchers, fixtures e dublês",
    "26-complexidade": "Big-O, memoização e custo de estrutura",
}


def _cabecalho(caminho):
    """(numero, titulo, enunciado) das duas primeiras linhas de comentário."""
    numero = titulo = enunciado = ""
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha.startswith("//"):
                if linha:
                    break
                continue
            texto = linha.lstrip("/").strip()
            m = re.match(r"Exercicio\s+(\d+)\s+[—-]\s+(.+)", texto)
            if m:
                numero, titulo = m.group(1), m.group(2)
            elif texto.lower().startswith("enunciado:"):
                enunciado = texto.split(":", 1)[1].strip()
            if numero and enunciado:
                break
    return numero, titulo, enunciado


def _modulos():
    saida = []
    for pasta in sorted(glob.glob(os.path.join(EXERCICIOS, "*"))):
        nome = os.path.basename(pasta)
        if not os.path.isdir(pasta) or not nome[:2].isdigit():
            continue
        arquivos = sorted(
            a for a in glob.glob(os.path.join(pasta, "*.df"))
            if os.path.basename(a)[0].isdigit())
        if arquivos:
            saida.append((nome, [_cabecalho(a) for a in arquivos],
                          [os.path.basename(a) for a in arquivos]))
    return saida


def _rotulo(nome):
    """'01-fundamentos' -> '01 · Fundamentos'."""
    num, resto = nome.split("-", 1)
    return f"{num} · {resto.replace('-', ' ').capitalize()}"


MODULOS = _modulos()
TOTAL = sum(len(itens) for _, itens, _ in MODULOS)

#: Os módulos que trazem um .md explicativo ao lado de cada .df.
COM_EXPLICACAO = sorted(
    nome for nome, _, arquivos in MODULOS
    if all(os.path.isfile(os.path.join(EXERCICIOS, nome, a.replace(".df", ".md")))
           for a in arquivos))


def _pagina_indice():
    linhas = [[
        f"[**{_rotulo(nome)}**](/docs/exercicios/{nome})",
        str(len(itens)),
        ASSUNTOS.get(nome, ""),
    ] for nome, itens, _ in MODULOS]

    faixa = ""
    if COM_EXPLICACAO:
        nums = [n[:2] for n in COM_EXPLICACAO]
        faixa = (f"Os módulos **{nums[0]} a {nums[-1]}** trazem um arquivo `.md` "
                 "ao lado de cada `.df`, com enunciado, conceitos, saída esperada "
                 "e sugestões para experimentar.")

    return {
        "href": "/docs/exercicios",
        "title": "Exercícios",
        "description": f"{TOTAL} exercícios em {len(MODULOS)} módulos, "
                       "cada um verificando o próprio resultado.",
        "blocos": [
            {"h2": "Como funcionam"},
            {"p": "Cada exercício **verifica o próprio resultado com `assert`** — se ele roda sem erro, está correto. Não há gabarito separado: o código é a resposta e o teste ao mesmo tempo."},
            {"code": f"""python3 exercicios/run_all.py          # todos os {TOTAL}
python3 exercicios/run_all.py 14       # só o módulo 14
python3 exercicios/run_all.py 03 07    # módulos 03 e 07

dataforge run exercicios/01-fundamentos/001_ola_mundo.df""", "lang": "bash"},
            *([{"p": faixa}] if faixa else []),
            {"callout": {"tipo": "nota", "titulo": "Eles rodam a cada mudança",
                         "texto": f"Os {TOTAL} são executados na suíte do repositório. Um exercício que quebrasse com uma mudança na linguagem apareceria no mesmo instante — é por isso que os exemplos desta documentação podem ser citados sem medo."}},
            {"h2": f"Os {len(MODULOS)} módulos"},
            {"table": {"head": ["Módulo", "Exercícios", "Assunto"], "rows": linhas}},
        ],
    }


def _pagina_modulo(nome, itens, arquivos):
    tem_md = os.path.isfile(
        os.path.join(EXERCICIOS, nome, arquivos[0].replace(".df", ".md")))
    linhas = [[n, f"**{t}**", e] for n, t, e in itens if n]

    blocos = [
        {"code": f"python3 exercicios/run_all.py {nome[:2]}", "lang": "bash"},
        {"h2": "Os exercícios"},
        {"table": {"head": ["#", "Título", "Enunciado"], "rows": linhas}},
    ]
    if tem_md:
        blocos.append({"callout": {
            "tipo": "dica", "titulo": "Cada um tem explicação ao lado",
            "texto": f"Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/{nome}/`."}})
    blocos.append({"p": f"Rode um isolado com `dataforge run exercicios/{nome}/{arquivos[0]}`."})

    return {
        "href": f"/docs/exercicios/{nome}",
        "title": _rotulo(nome),
        "description": f"{len(linhas)} exercícios: {ASSUNTOS.get(nome, '')}.",
        "blocos": blocos,
    }


PAGINAS = [_pagina_indice()] + [
    _pagina_modulo(nome, itens, arquivos) for nome, itens, arquivos in MODULOS
]
