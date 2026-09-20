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

#: O tema do painel: quase preto azulado, painéis um degrau acima do
#: fundo e a marca em âmbar. Ele existe porque um painel de operação
#: costuma ficar aberto o dia inteiro numa tela grande, e ali o que
#: cansa é o fundo claro — não a falta de cor.
MEIA_NOITE = {
    **ESCURO,
    "nome": "meia-noite",
    "fundo": "#080A0F",
    "fundo_alt": "#0E1118",
    "superficie": "#111521",
    "borda": "#1E2433",
    "texto": "#EDF1F7",
    "texto_fraco": "#8C97AB",
    "primaria": "#F5B301",
    "primaria_texto": "#0B0D12",
    "sucesso": "#3DD68C",
    "erro": "#FF6B6B",
    "aviso": "#FFC53D",
    "info": "#5B9BFF",
    "raio": "10px",
    "largura": "1440px",
}

#: Azul profundo, para quem quer o painel escuro sem o preto.
OCEANO = {
    **ESCURO,
    "nome": "oceano",
    "fundo": "#0A1424",
    "fundo_alt": "#0F1B2E",
    "superficie": "#122138",
    "borda": "#1D3050",
    "texto": "#E6EEF9",
    "texto_fraco": "#8BA3C0",
    "primaria": "#4CC9F0",
    "primaria_texto": "#06101E",
    "info": "#7BB6FF",
}

#: Contraste alto, dentro do nível AAA da WCAG. Não é um tema bonito —
#: é o que alguém escolhe quando o bonito não dá para ler.
CONTRASTE = {
    **CLARO,
    "nome": "contraste",
    "fundo": "#FFFFFF",
    "fundo_alt": "#F2F2F2",
    "superficie": "#FFFFFF",
    "borda": "#000000",
    "texto": "#000000",
    "texto_fraco": "#333333",
    "primaria": "#00458A",
    "primaria_texto": "#FFFFFF",
    "sucesso": "#005C29",
    "erro": "#9B0016",
    "aviso": "#6B4400",
    "info": "#00458A",
    "raio": "4px",
}

#: Papel: claro, quente e de baixo contraste azul — para leitura longa.
PAPEL = {
    **CLARO,
    "nome": "papel",
    "fundo": "#FBF7EF",
    "fundo_alt": "#F3EDE1",
    "superficie": "#FFFCF6",
    "borda": "#E0D6C4",
    "texto": "#2A2520",
    "texto_fraco": "#6B6157",
    "primaria": "#8A5A17",
    "info": "#1F5FA8",
}

PRONTOS = {"claro": CLARO, "escuro": ESCURO, "meia-noite": MEIA_NOITE,
           "meia_noite": MEIA_NOITE, "oceano": OCEANO,
           "contraste": CONTRASTE, "papel": PAPEL}

#: Um tema escuro pedido como texto vale para os dois modos; a página
#: não volta ao claro quando o sistema está claro. Quem pede
#: "meia-noite" está pedindo meia-noite.
ESCUROS = {"escuro", "meia-noite", "meia_noite", "oceano"}

#: A densidade muda espaçamento e tamanho de fonte sem tocar nas cores.
#: Um painel de operação cabe um terço mais de linha na mesma tela com
#: `compacta`, e é a diferença entre rolar e não rolar.
DENSIDADES = {
    "compacta": {"escala": "13.5px", "respiro": "0.78"},
    "normal": {"escala": "15px", "respiro": "1"},
    "folgada": {"escala": "16px", "respiro": "1.2"},
}

#: A cor primária do tema claro é #B28600, e não o #FED403 da marca,
#: porque amarelo sobre branco dá contraste 1,3:1 — a WCAG pede 4,5:1
#: para texto. O amarelo continua sendo a marca no tema escuro, onde
#: ele funciona.


def resolver(pedido):
    """Um tema a partir de um nome, de um vault, ou dos dois."""
    if pedido is None:
        return dict(CLARO), dict(ESCURO)
    if isinstance(pedido, str):
        if pedido.lower() == "automatico":
            return dict(CLARO), dict(ESCURO)
        base = PRONTOS.get(pedido.lower())
        if base is None:
            import difflib
            from ...errors import RuntimeError_
            perto = difflib.get_close_matches(pedido.lower(), sorted(PRONTOS), n=1)
            raise RuntimeError_(
                f"tema '{pedido}' nao existe.", 0, 0,
                nota=(f"voce quis dizer '{perto[0]}'?" if perto else
                      "os prontos: " + ", ".join(sorted(set(
                          p for p in PRONTOS if "_" not in p)) | {"automatico"})),
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


def nomes():
    """Os temas prontos, sem os apelidos com sublinhado."""
    return sorted({t["nome"] for t in PRONTOS.values()})


def e_escuro(pedido):
    """Se este tema pede o modo escuro fixo.

    Sem esta pergunta, `V.app(tema := "meia-noite")` no modo automático
    voltaria ao claro numa máquina configurada como clara — e o tema
    escolhido explicitamente deixaria de valer.
    """
    return isinstance(pedido, str) and pedido.lower() in ESCUROS


def densidade(nome="normal"):
    """As variáveis CSS de uma densidade."""
    escolhida = DENSIDADES.get(str(nome), DENSIDADES["normal"])
    return "".join(f"--v-{c}:{v};" for c, v in escolhida.items())
