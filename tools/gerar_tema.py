#!/usr/bin/env python3
"""Gera os temas de cor do VS Code a partir da gramática.

Por que gerado
--------------
A gramática (`editor/vscode/syntaxes/dataforge.tmLanguage.json`) é gerada de
`tokens.py` e sabe 43 escopos. Um tema escrito à mão pinta os escopos que
o autor lembrou, e os que ele esqueceu herdam a cor do tema do usuário —
o sintoma é `record` e `enum` saindo cinza no meio de código colorido,
que é exatamente o defeito que a gramática gerada existe para não ter.

Este gerador **recusa rodar** se um escopo da gramática não tiver cor. É
a mesma trava de `gerar_gramatica.py`, pelo mesmo motivo: a lista de
escopos cresce, e uma cor faltando não dá erro — só fica feia.

Por que dois temas
------------------
Claro e escuro não são o mesmo tema com as cores invertidas. O amarelo da
marca (`#FED403`) dá contraste 1,3:1 sobre branco, onde a WCAG pede 4,5:1
para texto; no claro ele vira `#8A6A00`. É a mesma decisão que a Vitrine
já tinha tomado, e por isso a razão está escrita nos dois lugares.

    python3 tools/gerar_tema.py
"""

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import marca            # noqa: E402

marca.preparar_saida()

GRAMATICA = os.path.join(RAIZ, "editor", "vscode", "syntaxes",
                         "dataforge.tmLanguage.json")
PASTA_TEMAS = os.path.join(RAIZ, "editor", "vscode", "themes")


# ═══════════════════════════════════════════════════════════
#  Os papéis
# ═══════════════════════════════════════════════════════════
#
# Um PAPEL agrupa escopos que devem ter a mesma cor. Pintar escopo por
# escopo daria 43 cores, e 43 cores não são um tema: são um arco-íris em
# que nada se destaca porque tudo se destaca.

#: escopo da gramática → papel.
PAPEL_DO_ESCOPO = {
    # ── Comentário ──
    "comment.line.double-slash.dataforge": "comentario",
    "comment.line.number-sign.dataforge": "comentario",

    # ── Texto ──
    "string.quoted.double.dataforge": "texto",
    "string.quoted.single.dataforge": "texto",
    "string.quoted.triple.dataforge": "texto",
    "string.interpolated.dataforge": "texto",
    "constant.character.escape.dataforge": "escape",
    # O `{x}` dentro de `$"…"` volta à cor de código: é código.
    "meta.embedded.expression.dataforge": "primeiro-plano",
    "punctuation.section.embedded.dataforge": "pontuacao",

    # ── Número e constante ──
    "constant.numeric.integer.dataforge": "numero",
    "constant.numeric.float.dataforge": "numero",
    "constant.numeric.decimal.dataforge": "numero",
    "constant.numeric.hex.dataforge": "numero",
    "constant.numeric.binary.dataforge": "numero",
    "constant.language.dataforge": "constante",
    "constant.language.http.dataforge": "constante",

    # ── Palavras de controle ──
    "keyword.control.conditional.dataforge": "controle",
    "keyword.control.loop.dataforge": "controle",
    "keyword.control.flow.dataforge": "controle",
    "keyword.control.exception.dataforge": "excecao",
    "keyword.control.import.dataforge": "importacao",

    # ── Outras palavras ──
    "keyword.other.oop.dataforge": "palavra",
    "keyword.other.async.dataforge": "palavra",
    "keyword.other.data.dataforge": "palavra",
    "keyword.other.meta.dataforge": "palavra",
    # As onze do Kiln têm cor PRÓPRIA: elas são contextuais, e quem lê
    # precisa ver num relance que `route` ali é a palavra do framework e
    # não o nome de uma variável — que continua permitido.
    "keyword.other.kiln.dataforge": "kiln",

    # ── Operadores ──
    "keyword.operator.assignment.dataforge": "operador",
    "keyword.operator.arithmetic.dataforge": "operador",
    "keyword.operator.comparison.dataforge": "operador",
    "keyword.operator.nullish.dataforge": "operador",
    "keyword.operator.spread.dataforge": "operador",
    "keyword.operator.arrow.dataforge": "operador",
    "keyword.operator.word.dataforge": "operador-palavra",
    # O pipeline é a sintaxe que mais distingue a linguagem. Ele merece
    # destaque próprio, não a cor de `+`.
    "keyword.operator.pipeline.dataforge": "pipeline",

    # ── Declarações e tipos ──
    "storage.type.dataforge": "declaracao",
    "storage.modifier.dataforge": "modificador",
    "storage.modifier.oop.dataforge": "modificador",
    "keyword.other.contract.dataforge": "palavra",
    "keyword.other.tipo.dataforge": "palavra",
    "entity.name.type.dataforge": "tipo",
    "support.type.dataforge": "tipo-embutido",

    # ── Nomes ──
    "entity.name.function.dataforge": "acao",
    "entity.name.function.call.dataforge": "chamada",
    "entity.name.function.decorator.dataforge": "decorador",
    "support.function.builtin.dataforge": "embutida",
    "support.class.module.dataforge": "modulo",
    "variable.other.property.dataforge": "propriedade",
}


#: Papel → (cor no escuro, cor no claro, estilo).
#:
#: O estilo fica junto da cor porque os dois compõem o mesmo sinal: o
#: comentário é apagado E itálico, e só uma das duas coisas não basta.
CORES = {
    #                           escuro     claro      estilo
    "primeiro-plano":          ("#E8E3D3", "#2A2520", ""),
    "comentario":              ("#7A7361", "#8A8371", "italic"),
    "texto":                   ("#A8C98A", "#3F6B2A", ""),
    "escape":                  ("#E39B7B", "#A8502A", ""),
    "numero":                  ("#E39B7B", "#A8502A", ""),
    "constante":               ("#FF9F6E", "#B0491F", ""),
    "controle":                ("#FED403", "#8A6A00", "bold"),
    "excecao":                 ("#FF8A7A", "#B03A28", "bold"),
    "importacao":              ("#7FD0C0", "#00695C", ""),
    "palavra":                 ("#F0B429", "#8F6200", ""),
    "kiln":                    ("#C99BE0", "#7B3FA0", "bold"),
    "operador":                ("#C9B896", "#5C5445", ""),
    "operador-palavra":        ("#F0B429", "#8F6200", ""),
    "pipeline":                ("#FED403", "#8A6A00", "bold"),
    "declaracao":              ("#FED403", "#8A6A00", "bold"),
    "modificador":             ("#B8A87E", "#6B6047", "italic"),
    "tipo":                    ("#8FC7E8", "#005A87", ""),
    "tipo-embutido":           ("#8FC7E8", "#005A87", "italic"),
    "acao":                    ("#9BD4F5", "#00527A", "bold"),
    "chamada":                 ("#9BD4F5", "#00527A", ""),
    "decorador":               ("#D5B8FF", "#6A3BA8", "italic"),
    "embutida":                ("#7FD0C0", "#00695C", ""),
    "modulo":                  ("#7FD0C0", "#00695C", "bold"),
    "propriedade":             ("#E8E3D3", "#2A2520", ""),
    "pontuacao":               ("#C9B896", "#5C5445", ""),
}


#: As cores da janela nao saem da gramatica: sao do tema, e nao do
#: codigo. Ficam numa funcao, e nao numa tabela, porque claro e escuro
#: nao compartilham valor nenhum — a inversao mecanica de um tema bom
#: da um tema ruim nos dois sentidos.


def _janela(escuro):
    """As cores de fundo, cursor, seleção e barras."""
    if escuro:
        return {
            "editor.background": "#16140D",
            "editor.foreground": "#E8E3D3",
            "editorLineNumber.foreground": "#4A4638",
            "editorLineNumber.activeForeground": "#FED403",
            "editorCursor.foreground": "#FED403",
            "editor.selectionBackground": "#41381F",
            "editor.lineHighlightBackground": "#1E1B12",
            "editorIndentGuide.background1": "#2A2618",
            "editorIndentGuide.activeBackground1": "#4A4127",
            "editorBracketMatch.background": "#41381F",
            "editorBracketMatch.border": "#FED403",
            "editorWhitespace.foreground": "#2A2618",
            "sideBar.background": "#110F0A",
            "activityBar.background": "#110F0A",
            "activityBar.foreground": "#FED403",
            "statusBar.background": "#1E1B12",
            "statusBar.foreground": "#C9B896",
            "titleBar.activeBackground": "#110F0A",
            "titleBar.activeForeground": "#E8E3D3",
            "tab.activeBackground": "#16140D",
            "tab.activeBorderTop": "#FED403",
            "tab.inactiveBackground": "#110F0A",
            "panel.background": "#110F0A",
            "terminal.background": "#110F0A",
            "terminal.foreground": "#E8E3D3",
            "editorError.foreground": "#FF8A7A",
            "editorWarning.foreground": "#F0B429",
            "editorInfo.foreground": "#8FC7E8",
            "focusBorder": "#4A4127",
            "list.activeSelectionBackground": "#2A2618",
            "list.activeSelectionForeground": "#FED403",
        }
    return {
        "editor.background": "#FBF9F2",
        "editor.foreground": "#2A2520",
        "editorLineNumber.foreground": "#B5AE9B",
        "editorLineNumber.activeForeground": "#8A6A00",
        "editorCursor.foreground": "#8A6A00",
        "editor.selectionBackground": "#EDE4C4",
        "editor.lineHighlightBackground": "#F4F0E2",
        "editorIndentGuide.background1": "#E6E0CC",
        "editorIndentGuide.activeBackground1": "#C9BF9E",
        "editorBracketMatch.background": "#EDE4C4",
        "editorBracketMatch.border": "#8A6A00",
        "editorWhitespace.foreground": "#E6E0CC",
        "sideBar.background": "#F4F0E2",
        "activityBar.background": "#F4F0E2",
        "activityBar.foreground": "#8A6A00",
        "statusBar.background": "#EFE9D6",
        "statusBar.foreground": "#5C5445",
        "titleBar.activeBackground": "#F4F0E2",
        "titleBar.activeForeground": "#2A2520",
        "tab.activeBackground": "#FBF9F2",
        "tab.activeBorderTop": "#8A6A00",
        "tab.inactiveBackground": "#F0EBDA",
        "panel.background": "#F4F0E2",
        "terminal.background": "#FBF9F2",
        "terminal.foreground": "#2A2520",
        "editorError.foreground": "#B03A28",
        "editorWarning.foreground": "#8F6200",
        "editorInfo.foreground": "#005A87",
        "focusBorder": "#C9BF9E",
        "list.activeSelectionBackground": "#EDE4C4",
        "list.activeSelectionForeground": "#6B5200",
    }


def escopos_da_gramatica():
    """Os escopos que a gramática realmente emite."""
    with open(GRAMATICA, encoding="utf-8") as f:
        gramatica = json.load(f)

    achados = set()

    def andar(objeto):
        if isinstance(objeto, dict):
            for chave, valor in objeto.items():
                if (chave == "name" and isinstance(valor, str)
                        and valor.endswith(".dataforge")
                        and " " not in valor):
                    achados.add(valor)
                andar(valor)
        elif isinstance(objeto, list):
            for item in objeto:
                andar(item)

    andar(gramatica)
    return achados


def conferir():
    """Recusa gerar com escopo sem cor, ou cor sem escopo.

    Os dois lados importam. Um escopo sem cor sai cinza no meio de código
    colorido; uma cor sem escopo é uma linha que nunca pinta nada, e ela
    envelhece em silêncio — daqui a seis meses ninguém sabe se ainda vale.
    """
    da_gramatica = escopos_da_gramatica()
    na_tabela = set(PAPEL_DO_ESCOPO)

    sem_cor = sorted(da_gramatica - na_tabela)
    sobrando = sorted(na_tabela - da_gramatica)
    papeis_orfaos = sorted(set(PAPEL_DO_ESCOPO.values()) - set(CORES))

    problemas = []
    if sem_cor:
        problemas.append(
            "escopo da gramatica sem cor no tema:\n    " + "\n    ".join(sem_cor))
    if sobrando:
        problemas.append(
            "cor para escopo que a gramatica nao emite:\n    "
            + "\n    ".join(sobrando))
    if papeis_orfaos:
        problemas.append(
            "papel sem cor definida:\n    " + "\n    ".join(papeis_orfaos))
    if problemas:
        raise SystemExit("gerar_tema.py recusou gerar:\n\n  "
                         + "\n\n  ".join(problemas))
    return da_gramatica


def montar(escuro):
    """O JSON de um tema."""
    conferir()

    # Um papel, uma regra, com todos os escopos dele juntos. Uma regra por
    # escopo daria 43 regras dizendo a mesma coisa, e o arquivo deixaria
    # de ser legivel — que e a unica vantagem de um tema em JSON.
    por_papel = {}
    for escopo, papel in sorted(PAPEL_DO_ESCOPO.items()):
        por_papel.setdefault(papel, []).append(escopo)

    regras = []
    for papel, escopos in sorted(por_papel.items()):
        cor_escuro, cor_claro, estilo = CORES[papel]
        ajuste = {"foreground": cor_escuro if escuro else cor_claro}
        if estilo:
            ajuste["fontStyle"] = estilo
        regras.append({"name": f"DataForge · {papel}",
                       "scope": escopos,
                       "settings": ajuste})

    return {
        "name": "DataForge Escuro" if escuro else "DataForge Claro",
        "type": "dark" if escuro else "light",
        "semanticHighlighting": True,
        "colors": _janela(escuro),
        "tokenColors": regras,
    }


def main():
    os.makedirs(PASTA_TEMAS, exist_ok=True)
    for escuro, nome in ((True, "dataforge-escuro.json"),
                         (False, "dataforge-claro.json")):
        caminho = os.path.join(PASTA_TEMAS, nome)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(montar(escuro), f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  {os.path.relpath(caminho, RAIZ)}")
    total = len(PAPEL_DO_ESCOPO)
    print(f"\n  {total} escopos em {len(set(PAPEL_DO_ESCOPO.values()))} papeis, "
          f"dois temas")


if __name__ == "__main__":
    main()
