"""Tema — cores, tipografia, espaçamento.

Um tema é um vault de variáveis CSS. Isso não é preguiça: com o valor
numa variável, mudar a cor primária muda o botão, o link, o foco, a
borda do campo e a primeira série do gráfico ao mesmo tempo — e não em
nove lugares.

    V.tema("escuro")
    V.tema({"primaria": "#0F62FE", "raio": "4px"})

Claro e escuro
--------------
Os dois vêm prontos, e a página respeita o `prefers-color-scheme` do
sistema quando o tema é "automatico" — que é o padrão. Um dashboard
aberto às onze da noite não deveria queimar a retina de ninguém.
"""

CLARO = {
    "nome": "claro",
    "fundo": "#FFFFFF",
    "fundo_alt": "#F6F7F9",
    "superficie": "#FFFFFF",
    "borda": "#E3E6EA",
    "texto": "#16181D",
    "texto_fraco": "#5C636E",
    "primaria": "#B28600",
    "primaria_texto": "#FFFFFF",
    "sucesso": "#1B7F3B",
    "erro": "#C21E2E",
    "aviso": "#9A6400",
    "info": "#0F62FE",
    "raio": "8px",
    "fonte": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
             "'Helvetica Neue', Arial, sans-serif",
    "fonte_mono": "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, "
                  "Consolas, monospace",
    "largura": "1160px",
}

ESCURO = {
    "nome": "escuro",
    "fundo": "#0D0F12",
    "fundo_alt": "#14171C",
    "superficie": "#16191F",
    "borda": "#282D36",
    "texto": "#E9ECF1",
    "texto_fraco": "#9BA3AF",
    "primaria": "#FED403",
    "primaria_texto": "#16181D",
    "sucesso": "#42BE65",
    "erro": "#FF8389",
    "aviso": "#F1C21B",
    "info": "#78A9FF",
    "raio": "8px",
    "fonte": CLARO["fonte"],
    "fonte_mono": CLARO["fonte_mono"],
    "largura": "1160px",
}

PRONTOS = {"claro": CLARO, "escuro": ESCURO}

#: A cor primária do tema claro é #B28600, e não o #FED403 da marca,
#: porque amarelo sobre branco dá contraste 1,3:1 — a WCAG pede 4,5:1
#: para texto. O amarelo continua sendo a marca no tema escuro, onde
#: ele funciona.


def resolver(pedido):
    """Um tema a partir de um nome, de um vault, ou dos dois."""
    if pedido is None:
        return dict(CLARO), dict(ESCURO)
    if isinstance(pedido, str):
        base = PRONTOS.get(pedido.lower())
        if base is None:
            from ...errors import RuntimeError_
            raise RuntimeError_(
                f"tema '{pedido}' nao existe.", 0, 0,
                nota="os prontos sao: claro, escuro, automatico",
                dica='para um tema seu, passe um vault: '
                     'V.tema({"primaria": "#0F62FE"})',
                doc="tecnicas/vitrine")
        return dict(base), dict(base)
    if isinstance(pedido, dict):
        # Um tema parcial completa o que falta a partir dos dois
        # prontos, e não só do claro: quem trocou a primária não deveria
        # perder o modo escuro por isso.
        return {**CLARO, **pedido}, {**ESCURO, **pedido}
    return dict(CLARO), dict(ESCURO)


def variaveis(tema):
    return "".join(f"--v-{c}:{v};" for c, v in tema.items() if c != "nome")
