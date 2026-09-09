#!/usr/bin/env python3
"""
Gera a gramatica TextMate do VS Code a partir do proprio codigo.

A lista de palavras coloridas sai de dataforge/tokens.py e a de funcoes
globais sai de dataforge/builtins.py. Escrever a gramatica a mao
garantia que, um dia, ela ficaria atrasada em relacao a linguagem — e
foi exatamente o que aconteceu com a versao 3.0.

    python3 tools/gerar_gramatica.py
"""

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.builtins import get_builtins                       # noqa: E402
from dataforge.stdlib import list_modules                         # noqa: E402
from dataforge.tokens import (                                    # noqa: E402
    CONTEXTUAIS_BLUEPRINT, CONTEXTUAIS_KILN, KEYWORDS,
)

DESTINO = os.path.join(RAIZ, "editor", "vscode", "syntaxes",
                       "dataforge.tmLanguage.json")

#: Como cada palavra reservada e pintada. O escopo TextMate decide a
#: cor no tema do usuario — 'keyword.control' fica roxo no Dark+,
#: 'storage.type' fica azul, e assim por diante.
GRUPOS = {
    "keyword.control.conditional.dataforge": [
        "given", "orif", "otherwise", "match", "point", "default", "when",
    ],
    "keyword.control.loop.dataforge": [
        "cycle", "persist", "perform", "halt", "skip", "from", "to", "step",
    ],
    "keyword.control.flow.dataforge": [
        "yield", "emit", "out", "trigger", "propagate", "defer", "wait",
    ],
    "keyword.control.exception.dataforge": [
        "monitor", "handle", "ensure", "retry", "recover", "guard",
        "validate", "assert",
    ],
    "keyword.control.import.dataforge": ["adopt", "relay", "as", "using"],
    "storage.type.dataforge": [
        "action", "blueprint", "record", "enum", "trait", "stream", "frame",
        "channel", "lambda",
    ],
    "storage.modifier.dataforge": [
        "steady", "static", "shadow", "abstract", "final", "private", "slots",
        "protected", "get", "set", "operator", "extends", "with",
    ],
    "keyword.other.oop.dataforge": ["spawn", "self", "root", "delete"],
    "keyword.other.async.dataforge": [
        "async", "await", "thread", "parallel", "pulse", "observe",
    ],
    "keyword.other.data.dataforge": [
        "sift", "morph", "distill", "train", "predict", "cast", "forge",
        "inspect", "typeof",
    ],
    "keyword.other.meta.dataforge": ["mark"],
    "keyword.other.kiln.dataforge": list(CONTEXTUAIS_KILN),
    "keyword.operator.word.dataforge": [
        "is", "isnt", "bigger", "smaller", "bigger_eq", "smaller_eq",
        "and", "or", "not", "in",
    ],
    "constant.language.dataforge": ["yes", "no", "void"],
}

#: Tipos embutidos, pintados como tipo mesmo sem serem reservados.
TIPOS = ["Integer", "Float", "String", "Boolean", "Cluster", "Vault",
         "Record", "Any", "Void", "Action", "Stream", "Frame", "Server"]


def _alternativa(palavras):
    """Palavras mais longas primeiro: senao 'bigger' come 'bigger_eq'."""
    return "|".join(sorted(set(palavras), key=lambda p: (-len(p), p)))


def _conferir_cobertura():
    """Toda palavra reservada precisa estar em algum grupo.

    Sem esta checagem, adicionar uma palavra a linguagem e esquecer da
    gramatica passaria despercebido — a palavra so ficaria sem cor.
    """
    pintadas = {p for palavras in GRUPOS.values() for p in palavras}
    todas = set(KEYWORDS) | set(CONTEXTUAIS_BLUEPRINT) | set(CONTEXTUAIS_KILN)
    esquecidas = todas - pintadas
    if esquecidas:
        raise SystemExit(
            f"palavras sem cor definida em GRUPOS: {sorted(esquecidas)}\n"
            f"adicione cada uma ao grupo que faz sentido em "
            f"tools/gerar_gramatica.py")
    inventadas = pintadas - todas
    if inventadas:
        raise SystemExit(
            f"GRUPOS pinta palavras que a linguagem nao tem: "
            f"{sorted(inventadas)}")


def construir():
    _conferir_cobertura()

    globais = sorted(get_builtins())
    modulos = sorted({m.split(".")[-1] for m in list_modules()})

    padroes_palavra = [
        {"name": escopo, "match": rf"\b({_alternativa(palavras)})\b"}
        for escopo, palavras in GRUPOS.items()
    ]

    return {
        "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/"
                   "master/tmlanguage.json",
        "name": "DataForge",
        "scopeName": "source.dataforge",
        "fileTypes": ["df"],
        "patterns": [{"include": f"#{nome}"} for nome in (
            "comentarios", "interpolacao", "textos", "numeros", "palavras",
            "tipos", "decoradores", "rotas", "declaracoes", "globais",
            "modulos", "chamadas", "operadores", "propriedades",
        )],
        "repository": {
            # '//' e comentario, menos quando divide: '// 2' é divisão.
            # A gramatica reproduz a regra do lexer.
            "comentarios": {"patterns": [
                {"name": "comment.line.double-slash.dataforge",
                 "match": r"//(?![\d(\s]*[\d(])[^\n]*"},
                {"name": "comment.line.number-sign.dataforge",
                 "match": r"#[^\n]*"},
            ]},
            "interpolacao": {
                "name": "string.interpolated.dataforge",
                "begin": r'\$"', "end": r'"',
                "patterns": [
                    {"name": "constant.character.escape.dataforge",
                     "match": r"\\."},
                    {"name": "meta.embedded.expression.dataforge",
                     "begin": r"\{", "end": r"\}",
                     "beginCaptures": {
                         "0": {"name": "punctuation.section.embedded.dataforge"}},
                     "endCaptures": {
                         "0": {"name": "punctuation.section.embedded.dataforge"}},
                     "patterns": [{"include": "$self"}]},
                ],
            },
            "textos": {"patterns": [
                {"name": "string.quoted.triple.dataforge",
                 "begin": r'"""', "end": r'"""'},
                {"name": "string.quoted.double.dataforge",
                 "begin": r'"', "end": r'"',
                 "patterns": [{"name": "constant.character.escape.dataforge",
                               "match": r"\\."}]},
                {"name": "string.quoted.single.dataforge",
                 "begin": r"'", "end": r"'",
                 "patterns": [{"name": "constant.character.escape.dataforge",
                               "match": r"\\."}]},
            ]},
            "numeros": {"patterns": [
                {"name": "constant.numeric.hex.dataforge",
                 "match": r"\b0[xX][0-9a-fA-F_]+\b"},
                {"name": "constant.numeric.binary.dataforge",
                 "match": r"\b0[bB][01_]+\b"},
                {"name": "constant.numeric.float.dataforge",
                 "match": r"\b\d[\d_]*\.\d[\d_]*([eE][+-]?\d+)?\b"},
                {"name": "constant.numeric.integer.dataforge",
                 "match": r"\b\d[\d_]*\b"},
            ]},
            "palavras": {"patterns": padroes_palavra},
            "tipos": {
                "name": "support.type.dataforge",
                "match": rf"\b({_alternativa(TIPOS)})\b",
            },
            "decoradores": {
                "name": "entity.name.function.decorator.dataforge",
                "match": r"\bmark\s+@[A-Za-z_]\w*",
            },
            # 'route GET "/x"' — o verbo merece destaque proprio.
            "rotas": {
                "match": r"\b(route)\s+(GET|POST|PUT|PATCH|DELETE|HEAD|"
                         r"OPTIONS|ANY)\b",
                "captures": {
                    "1": {"name": "keyword.other.kiln.dataforge"},
                    "2": {"name": "constant.language.http.dataforge"},
                },
            },
            "declaracoes": {"patterns": [
                {"match": r"\b(action|stream\s+action)\s+([A-Za-z_]\w*)",
                 "captures": {"1": {"name": "storage.type.dataforge"},
                              "2": {"name": "entity.name.function.dataforge"}}},
                {"match": r"\b(blueprint|record|enum|trait)\s+([A-Za-z_]\w*)",
                 "captures": {"1": {"name": "storage.type.dataforge"},
                              "2": {"name": "entity.name.type.dataforge"}}},
                {"match": r"\b(server)\s+([A-Za-z_]\w*)",
                 "captures": {"1": {"name": "keyword.other.kiln.dataforge"},
                              "2": {"name": "entity.name.type.dataforge"}}},
            ]},
            "globais": {
                "name": "support.function.builtin.dataforge",
                "match": rf"\b({_alternativa(globais)})\b(?=\s*\()",
            },
            "modulos": {
                "name": "support.class.module.dataforge",
                "match": rf"\b(Arcane|{_alternativa(modulos)})\b(?=\s*\.)",
            },
            "chamadas": {
                "name": "entity.name.function.call.dataforge",
                "match": r"\b([A-Za-z_]\w*)\b(?=\s*\()",
            },
            "operadores": {"patterns": [
                {"name": "keyword.operator.assignment.dataforge",
                 "match": r":=|\+=|-=|\*=|/=|%="},
                {"name": "keyword.operator.pipeline.dataforge", "match": r">>"},
                {"name": "keyword.operator.arrow.dataforge", "match": r"->|=>"},
                {"name": "keyword.operator.nullish.dataforge",
                 "match": r"\?\?|\?\."},
                {"name": "keyword.operator.spread.dataforge", "match": r"\.\.\."},
                {"name": "keyword.operator.arithmetic.dataforge",
                 "match": r"~/|\*\*|[+\-*/%]"},
                {"name": "keyword.operator.comparison.dataforge",
                 "match": r"==|!=|<=|>=|<|>"},
            ]},
            "propriedades": {
                "name": "variable.other.property.dataforge",
                "match": r"(?<=\.)\s*([A-Za-z_]\w*)",
            },
        },
    }


def main():
    gramatica = construir()
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    with open(DESTINO, "w", encoding="utf-8") as f:
        json.dump(gramatica, f, indent=2, ensure_ascii=False)
        f.write("\n")

    total = sum(len(p) for p in GRUPOS.values())
    print(f"gramatica gerada: {DESTINO}")
    print(f"  {total} palavras reservadas em {len(GRUPOS)} grupos de cor")
    print(f"  {len(get_builtins())} funcoes globais")
    print(f"  {len(set(list_modules()))} modulos da stdlib")


if __name__ == "__main__":
    main()
