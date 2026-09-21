# -*- coding: utf-8 -*-
"""Arcane.Regex — o que faltava, e o problema de cada peca.

O modulo tinha as operacoes (`match`, `search`, `findall`, `sub`), os
validadores brasileiros e um catalogo de padroes prontos. Quatro coisas
faltavam, e cada uma tornava inalcancavel um recurso que a expressao
regular ja tem:

    grupo nomeado   '(?P<ano>\\d{4})' compilava, e o nome NAO chegava ao
                    resultado: ele vinha por posicao, e ninguem escreve
                    '(?P<ano>…)' para depois ler 'groups[2]'
    fullmatch       'match' ancora so no comeco — 'is_cpf' e parentes
                    aceitavam lixo no fim, calados
    repl que CALCULA 'sub' so troca por texto; mascarar um CPF, virar a
                    caixa de uma palavra ou somar 1 a um numero exigia
                    sair do modulo
    o risco          '(a+)+$' trava o processo em trinta caracteres, e
                    nada no modulo dizia isso

Este arquivo e a segunda metade do `arcane_regex.py`, no mesmo formato
do `crucible_extra.py`: ele existe para nao dobrar um arquivo que ja
esta escrito, e as duas partes entram no mesmo dicionario.

Os nomes seguem o arquivo: `Arcane.Regex` e um modulo antigo, e a
superficie dele e em ingles. Um `nomeados` ao lado de `findall` faria o
mesmo modulo responder em duas linguas.
"""

import re
import time

_DOC = "referencia/regex"


def _erro(mensagem, nota="", dica="", classe="RegexError"):
    from .. import errors
    alvo = errors.erro_por_nome(classe) or errors.RuntimeError_
    return alvo(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


def _compilar(padrao, flags=0):
    """Compila dizendo ONDE o padrao esta errado.

    A mensagem do Python traz a posicao (`at position 7`) e nao mostra
    o padrao com a marca. Num padrao de sessenta caracteres, contar ate
    sete e o que a pessoa faz em seguida.
    """
    if hasattr(padrao, "pattern"):
        return padrao
    try:
        return re.compile(padrao, flags)
    except re.error as erro:
        texto = str(padrao)
        onde = getattr(erro, "pos", None)
        seta = ""
        if isinstance(onde, int) and 0 <= onde <= len(texto):
            seta = f"\n    {texto}\n    {' ' * onde}^"
        raise _erro(
            f"o padrao nao compila: {erro.msg}{seta}",
            nota=f"padrao: {texto!r}")


def _do_casamento(m):
    """O resultado de um casamento, com os nomes JUNTO.

    `groups` continua vindo por posicao — havia codigo lendo dali, e
    tira-lo seria quebrar o que funciona. `named` e o acrescimo.
    """
    return {
        "matched": True,
        "value": m.group(),
        "groups": list(m.groups()),
        "named": {k: v for k, v in m.groupdict().items()},
        "span": list(m.span()),
        "start": m.start(),
        "end": m.end(),
    }


_VAZIO = {"matched": False, "value": "", "groups": [], "named": {},
          "span": [], "start": -1, "end": -1}


# ═══════════════════════════════════════════════════════════
#  Grupos nomeados
# ═══════════════════════════════════════════════════════════

def group_names(pattern):
    """Os nomes que o padrao declara, na ordem em que aparecem."""
    compilado = _compilar(pattern)
    porindice = {i: nome for nome, i in compilado.groupindex.items()}
    return [porindice[i] for i in sorted(porindice)]


def named(pattern, string, flags=0):
    """O primeiro casamento como vault de NOMES. Vazio quando nao casa.

        d := Regex.named("(?P<dia>\\d{2})/(?P<mes>\\d{2})", "07/09")
        out d["mes"]

    Sem isto, `(?P<mes>…)` era decoracao: o nome compilava e o
    resultado vinha por posicao.
    """
    m = _compilar(pattern, flags).search(str(string))
    return dict(m.groupdict()) if m else {}


def findnamed(pattern, string, flags=0):
    """Um vault por casamento — a leitura de um log linha a linha."""
    return [dict(m.groupdict())
            for m in _compilar(pattern, flags).finditer(str(string))]


# ═══════════════════════════════════════════════════════════
#  Ancorar nas duas pontas
# ═══════════════════════════════════════════════════════════

def fullmatch(pattern, string, flags=0):
    """Casa a string INTEIRA, e nao so o comeco.

    `match` ancora apenas no inicio: validar com ele aceita lixo no
    fim, calado. `Regex.match("\\d{3}", "123abc")` responde que casou.
    """
    m = _compilar(pattern, flags).fullmatch(str(string))
    return _do_casamento(m) if m else dict(_VAZIO)


def is_exactly(pattern, string, flags=0):
    """`yes` quando a string inteira casa. A pergunta de um validador."""
    return _compilar(pattern, flags).fullmatch(str(string)) is not None


# ═══════════════════════════════════════════════════════════
#  Substituir calculando
# ═══════════════════════════════════════════════════════════

def sub_with(pattern, action, string, count=0, flags=0):
    """Troca cada casamento pelo que a acao devolver.

        Regex.sub_with("\\d+", lambda m => str(int(m["value"]) * 2), texto)

    A acao recebe o mesmo vault de `search` — com `value`, `groups`,
    `named` e `span`. Passar o objeto de casamento do Python
    funcionaria por protocolo e obrigaria a escrever `m.group(1)`,
    que e vocabulario de outra linguagem.
    """
    if not callable(action):
        raise _erro("sub_with precisa de uma acao que devolve o texto.",
                    dica='Regex.sub_with(padrao, lambda m => …, texto)')

    def trocar(m):
        saida = action(_do_casamento(m))
        if saida is None:
            # Devolver o casamento intacto e o que deixa a acao
            # escolher o que NAO trocar, sem precisar reconstruir.
            return m.group()
        return str(saida)

    return _compilar(pattern, flags).sub(trocar, str(string), count)


def replace_map(pattern, table, string, flags=0):
    """Troca cada casamento pelo valor dele na tabela.

    O que nao estiver na tabela fica como esta — e nao vira vazio, que
    e o que uma tabela com `get` sem padrao faria.
    """
    tabela = dict(table or {})
    return sub_with(pattern,
                    lambda m: tabela.get(m["value"], m["value"]),
                    string, 0, flags)


# ═══════════════════════════════════════════════════════════
#  Partir sem perder o separador
# ═══════════════════════════════════════════════════════════

def split_keep(pattern, string, flags=0):
    """Parte mantendo os separadores, na ordem em que aparecem.

    `split` os descarta. Reconstruir o texto depois de transformar os
    pedacos exige saber o que havia entre eles — e adivinhar ali e como
    um `join(" ")` transforma tabulacao em espaco sem ninguem ver.
    """
    compilado = _compilar(pattern, flags)
    saida = []
    ultimo = 0
    texto = str(string)
    for m in compilado.finditer(texto):
        if m.start() > ultimo:
            saida.append(texto[ultimo:m.start()])
        saida.append(m.group())
        ultimo = m.end()
    if ultimo < len(texto):
        saida.append(texto[ultimo:])
    return saida


def between(pattern_start, pattern_end, string, flags=0):
    """O que ha entre cada par de marcas, sem as marcas."""
    inicio = _compilar(pattern_start, flags)
    fim = _compilar(pattern_end, flags)
    texto = str(string)
    saida = []
    posicao = 0
    while True:
        a = inicio.search(texto, posicao)
        if a is None:
            return saida
        b = fim.search(texto, a.end())
        if b is None:
            return saida
        saida.append(texto[a.end():b.start()])
        posicao = b.end()


# ═══════════════════════════════════════════════════════════
#  Ver o que casou
# ═══════════════════════════════════════════════════════════

def highlight(pattern, string, before="[", after="]", flags=0):
    """O texto com os casamentos marcados. Para depurar um padrao.

    Um padrao que devolve a lista errada quase sempre casa num lugar
    que nao se esperava — e uma lista de resultados nao diz ONDE.
    """
    return _compilar(pattern, flags).sub(
        lambda m: f"{before}{m.group()}{after}", str(string))


def positions(pattern, string, flags=0):
    """Linha, coluna e texto de cada casamento.

    A posicao em BYTES de um `span` nao serve para apontar num arquivo:
    quem le um erro procura linha e coluna.
    """
    texto = str(string)
    saida = []
    for m in _compilar(pattern, flags).finditer(texto):
        antes = texto[:m.start()]
        linha = antes.count("\n") + 1
        coluna = m.start() - (antes.rfind("\n") + 1) + 1
        saida.append({"linha": linha, "coluna": coluna,
                      "value": m.group(), "start": m.start(),
                      "end": m.end()})
    return saida


# ═══════════════════════════════════════════════════════════
#  Explicar o padrao
# ═══════════════════════════════════════════════════════════

#: O que cada pedaco quer dizer, em portugues. A tabela e fechada de
#: proposito: explicar o que nao se reconhece com uma frase generica
#: ("um grupo") e pior que nao explicar, porque parece resposta.
_PARTES = [
    (r"\(\?P<(\w+)>", lambda m: f"abre o grupo chamado '{m.group(1)}'"),
    (r"\(\?:", lambda m: "abre um grupo que NAO captura"),
    (r"\(\?=", lambda m: "exige que venha a seguir (sem consumir)"),
    (r"\(\?!", lambda m: "exige que NAO venha a seguir"),
    (r"\(\?<=", lambda m: "exige que viesse antes"),
    (r"\(\?<!", lambda m: "exige que NAO viesse antes"),
    (r"\(", lambda m: "abre um grupo que captura"),
    (r"\)", lambda m: "fecha o grupo"),
    (r"\[\^([^\]]*)\]", lambda m: f"qualquer caractere FORA de '{m.group(1)}'"),
    (r"\[([^\]]*)\]", lambda m: f"um caractere entre '{m.group(1)}'"),
    (r"\{(\d+),(\d+)\}", lambda m: f"de {m.group(1)} a {m.group(2)} vezes"),
    (r"\{(\d+),\}", lambda m: f"{m.group(1)} vezes ou mais"),
    (r"\{(\d+)\}", lambda m: f"exatamente {m.group(1)} vezes"),
    (r"\\d", lambda m: "um digito"),
    (r"\\D", lambda m: "qualquer coisa menos digito"),
    (r"\\w", lambda m: "letra, digito ou sublinhado"),
    (r"\\W", lambda m: "nem letra, nem digito, nem sublinhado"),
    (r"\\s", lambda m: "espaco, tabulacao ou quebra de linha"),
    (r"\\S", lambda m: "qualquer coisa menos espaco"),
    (r"\\b", lambda m: "fronteira de palavra"),
    (r"\\.", lambda m: f"o caractere '{m.group()[1]}', literal"),
    (r"\+\?", lambda m: "uma vez ou mais, o MENOS possivel"),
    (r"\*\?", lambda m: "zero vezes ou mais, o MENOS possivel"),
    (r"\?\?", lambda m: "zero ou uma vez, o MENOS possivel"),
    (r"\+", lambda m: "uma vez ou mais"),
    (r"\*", lambda m: "zero vezes ou mais"),
    (r"\?", lambda m: "zero ou uma vez"),
    (r"\^", lambda m: "o comeco"),
    (r"\$", lambda m: "o fim"),
    (r"\|", lambda m: "ou"),
    (r"\.", lambda m: "qualquer caractere"),
]

_COMPILADAS = [(re.compile(p), f) for p, f in _PARTES]


def explain(pattern):
    """O padrao pedaco a pedaco, em portugues.

    Ler uma expressao regular e o custo dela: o padrao que valida um
    e-mail cabe numa linha e leva dez minutos para ser entendido por
    quem nao a escreveu. Isto nao substitui aprender a sintaxe — e o
    que se consulta ao encontrar uma no codigo de outra pessoa.
    """
    texto = str(pattern)
    _compilar(texto)                       # um padrao quebrado nao e explicado
    saida = []
    i = 0
    literal = ""

    def despejar():
        if literal:
            saida.append({"trecho": literal,
                          "quer_dizer": f"o texto '{literal}', literal"})

    while i < len(texto):
        achou = None
        for compilada, dizer in _COMPILADAS:
            m = compilada.match(texto, i)
            if m:
                achou = (m, dizer)
                break
        if achou is None:
            literal += texto[i]
            i += 1
            continue
        despejar()
        literal = ""
        m, dizer = achou
        saida.append({"trecho": m.group(), "quer_dizer": dizer(m)})
        i = m.end()
    despejar()
    return saida


# ═══════════════════════════════════════════════════════════
#  O risco de travar
# ═══════════════════════════════════════════════════════════

#: As formas classicas de retrocesso catastrofico. Sao SHAPES: um
#: quantificador dentro de outro, e uma alternancia que casa a mesma
#: coisa duas vezes.
_PERIGOSOS = [
    (re.compile(r"\([^()]*[+*]\)[+*]"),
     "um quantificador dentro de outro: '(a+)+'"),
    (re.compile(r"\([^()]*\{\d+,\}\)[+*]"),
     "uma repeticao aberta dentro de outra: '(a{2,})+'"),
    (re.compile(r"\((\w+)\|\1\)[+*]"),
     "uma alternancia que casa a mesma coisa dos dois lados: '(a|a)+'"),
    (re.compile(r"\(\[[^\]]+\][+*]\)[+*]"),
     "uma classe repetida dentro de um grupo repetido: '([a-z]+)+'"),
]


def risk(pattern):
    """Quanto este padrao pode custar num texto que nao casa.

        r := Regex.risk("(a+)+$")
        out r["perigoso"], r["motivo"]

    `(a+)+$` contra trinta caracteres que nao casam leva **anos**: o
    motor tenta todas as formas de dividir a entrada entre os dois
    quantificadores, e sao 2^n.

    Isto e uma leitura de FORMA, e nao uma prova. Ela acusa os quatro
    desenhos classicos e cala no resto — inclusive em padroes que
    travam por outro caminho. Um padrao que vem de fora (de um campo,
    de um arquivo de configuracao) nunca deveria ser compilado sem
    passar por aqui, e passar por aqui nao o torna seguro.
    """
    texto = str(pattern)
    _compilar(texto)
    motivos = [motivo for compilada, motivo in _PERIGOSOS
               if compilada.search(texto)]
    return {
        "padrao": texto,
        "perigoso": bool(motivos),
        "motivo": motivos[0] if motivos else "",
        "motivos": motivos,
        "nota": ("isto e uma leitura de forma, e nao uma prova: ela "
                 "reconhece os quatro desenhos classicos e cala no resto"),
    }


def safe_search(pattern, string, ms=100, flags=0):
    """Procura recusando o padrao perigoso ANTES de rodar.

    Nao ha como interromper uma busca ja comecada: o motor de
    expressao regular do Python nao solta o GIL, entao um prazo numa
    thread nao para nada — ela so deixaria de esperar enquanto o
    processo inteiro continua travado. A unica defesa util e a recusa
    antes, e um teto no tamanho da entrada.

    `ms` nao interrompe: ele e MEDIDO, e a busca que passar do prazo
    volta com `demorou` marcado, para o proximo texto ser recusado.
    """
    analise = risk(pattern)
    if analise["perigoso"]:
        raise _erro(
            f"este padrao pode travar: {analise['motivo']}.",
            nota="contra um texto que nao casa, o motor tenta todas as "
                 "divisoes possiveis da entrada — e sao 2^n",
            dica="reescreva sem o quantificador aninhado, ou use "
                 "Regex.search se o padrao e seu e o texto e curto")
    comeco = time.perf_counter()
    m = _compilar(pattern, flags).search(str(string))
    gasto = (time.perf_counter() - comeco) * 1000.0
    saida = _do_casamento(m) if m else dict(_VAZIO)
    saida["ms"] = gasto
    saida["demorou"] = gasto > float(ms)
    return saida


# ═══════════════════════════════════════════════════════════
#  O que entra no modulo
# ═══════════════════════════════════════════════════════════

EXTRAS = {
    # ── grupos nomeados ──
    "named": named,
    "findnamed": findnamed,
    "group_names": group_names,

    # ── ancorar nas duas pontas ──
    "fullmatch": fullmatch,
    "is_exactly": is_exactly,

    # ── substituir calculando ──
    "sub_with": sub_with,
    "replace_map": replace_map,

    # ── partir e recortar ──
    "split_keep": split_keep,
    "between": between,

    # ── ver ──
    "highlight": highlight,
    "positions": positions,
    "explain": explain,

    # ── o risco ──
    "risk": risk,
    "safe_search": safe_search,
}
