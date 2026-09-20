"""Dados — a grade, o editor, o indicador e os formatos.

A `V.tabela` mostra; a **grade** é para trabalhar: ela pagina, ordena
no servidor, filtra, soma o rodapé, pinta a célula por regra, desenha a
barra dentro da célula e devolve o que foi selecionado.

A diferença entre as duas não é de tamanho — é de onde a decisão mora.
A `V.frame` ordena e filtra **no navegador**, com o que já está na
tela: é instantâneo e mente sobre um conjunto de cem mil linhas, porque
só as que vieram participam. A grade ordena e pagina **no servidor**,
sobre o conjunto inteiro, e por isso é ela que serve a uma listagem de
verdade.

Três decisões que valem lembrar:

1. **A configuração de coluna é um vault, e não um objeto.** Ela
   atravessa a fronteira da linguagem o tempo todo — vem de um
   `forge.toml`, de um banco, de um `cycle` que a monta. Um objeto
   exigiria construtor de dentro do DataForge para algo que é dado.

2. **O formato é aplicado na hora de desenhar, nunca no dado.** A
   coluna continua numérica: é o que permite ordenar por valor e somar
   o rodapé depois de a célula já dizer `R$ 1.091.947,91`.

3. **A seleção é devolvida, e não notificada.** `selecionadas` sai da
   própria chamada, porque a linha seguinte do programa é quem vai
   usá-la — não há retorno de chamada em lugar nenhum deste framework.
"""

import math

from . import componentes as C
from .nucleo import No

_str = C._str
_por = C._por
_ctx = C._ctx


# ═══════════════════════════════════════════════════════════
#  Formatos
# ═══════════════════════════════════════════════════════════

def moeda(valor, simbolo="R$", casas=2):
    """`1091947.91` vira `R$ 1.091.947,91`."""
    numero = _num(valor)
    if numero is None:
        return _str(valor)
    texto = _milhar(abs(numero), casas)
    sinal = "-" if numero < 0 else ""
    return f"{sinal}{simbolo} {texto}".strip()


def numero(valor, casas=0):
    """Separador de milhar e vírgula decimal, como se escreve em pt-BR."""
    n = _num(valor)
    if n is None:
        return _str(valor)
    return ("-" if n < 0 else "") + _milhar(abs(n), casas)


def percentual(valor, casas=1, ja_e_percentual=True):
    """`12.5` vira `12,5%`; com `ja_e_percentual := no`, `0.125` também."""
    n = _num(valor)
    if n is None:
        return _str(valor)
    if not ja_e_percentual:
        n *= 100
    return _milhar(n, casas) + "%"


def compacto(valor, casas=1):
    """`1234567` vira `1,2 mi`. Um eixo cheio de zeros não se lê."""
    n = _num(valor)
    if n is None:
        return _str(valor)
    sinal = "-" if n < 0 else ""
    n = abs(n)
    for limite, sufixo in ((1e12, " tri"), (1e9, " bi"), (1e6, " mi"),
                           (1e3, " mil")):
        if n >= limite:
            return sinal + _milhar(n / limite, casas).rstrip("0").rstrip(",") + sufixo
    return sinal + _milhar(n, 0 if float(n).is_integer() else casas)


def data_br(valor):
    """`2026-09-20` vira `20/09/2026`. O que não for data sai como veio."""
    texto = _str(valor).strip()
    if len(texto) >= 10 and texto[4] == "-" and texto[7] == "-":
        return f"{texto[8:10]}/{texto[5:7]}/{texto[0:4]}"
    return texto


def _milhar(n, casas):
    texto = f"{float(n):,.{max(0, int(casas))}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def _num(valor):
    if isinstance(valor, bool) or valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    try:
        texto = str(valor).strip().replace(".", "").replace(",", ".")
        return float(texto)
    except (TypeError, ValueError):
        return None


#: O nome do formato -> a função. Uma lista fechada, e não um `eval` do
#: que vier: o formato chega de configuração, e configuração é dado.
FORMATOS = {
    "moeda": moeda,
    "numero": numero,
    "percentual": percentual,
    "compacto": compacto,
    "data": data_br,
    "texto": _str,
}


def formatar(valor, formato="", casas=None):
    """Aplica um dos formatos conhecidos pelo nome."""
    nome = _str(formato)
    funcao = FORMATOS.get(nome)
    if funcao is None:
        return _str(valor)
    if casas is not None and nome in ("moeda", "numero", "percentual", "compacto"):
        return funcao(valor, casas) if nome != "moeda" else moeda(valor, casas=casas)
    return funcao(valor)


# ═══════════════════════════════════════════════════════════
#  Configuração de coluna
# ═══════════════════════════════════════════════════════════

#: Os tipos que a grade sabe desenhar. `barra` e `mini` desenham dentro
#: da célula, e são o que separa uma listagem de uma planilha.
TIPOS_DE_COLUNA = ("texto", "numero", "moeda", "percentual", "compacto",
                   "data", "logico", "link", "imagem", "selo", "barra",
                   "mini", "progresso")


def coluna(nome, titulo="", tipo="texto", formato="", largura=0,
           alinhar="", casas=None, ajuda="", editavel=False,
           opcoes=None, minimo=None, maximo=None, prefixo="", sufixo="",
           cores=None, oculta=False):
    """A configuração de uma coluna da grade, como vault.

        V.grade(pedidos, colunas := [
            V.coluna("cliente", "Cliente", largura := 240),
            V.coluna("total", "Total", tipo := "moeda"),
            V.coluna("margem", tipo := "barra", maximo := 100),
        ])

    O que não é dito fica no padrão: uma coluna que só precisa de um
    título não deveria exigir mais do que o título.
    """
    chave = _str(nome)
    modelo = _str(tipo)
    if modelo not in TIPOS_DE_COLUNA:
        import difflib
        from ...errors import RuntimeError_
        perto = difflib.get_close_matches(modelo, TIPOS_DE_COLUNA, n=1)
        raise RuntimeError_(
            f"coluna de tipo '{tipo}' nao existe.", 0, 0,
            nota=(f"voce quis dizer '{perto[0]}'?" if perto else
                  "os tipos: " + ", ".join(TIPOS_DE_COLUNA)),
            doc="vitrine/referencia")
    if not alinhar:
        alinhar = "direita" if modelo in (
            "numero", "moeda", "percentual", "compacto") else "esquerda"
    # Uma barra sem formato saía com o número cru da conta —
    # `95.77777777777777` ao lado da barrinha. O valor que acompanha a
    # barra é uma leitura rápida, e catorze casas não são leitura.
    if modelo in ("barra", "progresso") and not formato:
        formato = "numero"
        if casas is None:
            casas = 1
    return {
        "nome": chave, "titulo": _str(titulo) or chave, "tipo": modelo,
        "formato": _str(formato) or (modelo if modelo in FORMATOS else ""),
        "largura": int(largura or 0), "alinhar": _str(alinhar),
        "casas": casas, "ajuda": _str(ajuda), "editavel": bool(editavel),
        "opcoes": [_str(o) for o in (opcoes or [])],
        "minimo": minimo, "maximo": maximo,
        "prefixo": _str(prefixo), "sufixo": _str(sufixo),
        "cores": [_str(c) for c in (cores or [])], "oculta": bool(oculta),
    }


def regra(coluna_alvo, condicao, valor=None, cor="aviso", coluna_pintada=""):
    """Uma regra de formatação condicional.

        V.grade(vendas, destacar := [
            V.regra("margem", "menor", 10, "erro"),
            V.regra("situacao", "igual", "pago", "sucesso"),
        ])

    `condicao`: maior, maior_igual, menor, menor_igual, igual, diferente,
    contem, vazio, preenchido.
    """
    permitidas = ("maior", "maior_igual", "menor", "menor_igual", "igual",
                  "diferente", "contem", "vazio", "preenchido")
    qual = _str(condicao)
    if qual not in permitidas:
        from ...errors import RuntimeError_
        raise RuntimeError_(
            f"condicao '{condicao}' nao existe numa regra de destaque.", 0, 0,
            nota="as condicoes: " + ", ".join(permitidas),
            doc="vitrine/referencia")
    return {"coluna": _str(coluna_alvo), "condicao": qual, "valor": valor,
            "cor": _str(cor), "pintar": _str(coluna_pintada) or _str(coluna_alvo)}


def _casa_regra(valor, condicao, alvo):
    if condicao == "vazio":
        return valor is None or _str(valor).strip() == ""
    if condicao == "preenchido":
        return valor is not None and _str(valor).strip() != ""
    if condicao == "contem":
        return _str(alvo).lower() in _str(valor).lower()
    if condicao in ("igual", "diferente"):
        igual = _str(valor).strip().lower() == _str(alvo).strip().lower()
        return igual if condicao == "igual" else not igual
    a, b = _num(valor), _num(alvo)
    if a is None or b is None:
        return False
    return {"maior": a > b, "maior_igual": a >= b,
            "menor": a < b, "menor_igual": a <= b}[condicao]


# ═══════════════════════════════════════════════════════════
#  A grade
# ═══════════════════════════════════════════════════════════

def grade(dados, colunas=None, busca=True, paginar=25, selecionar="",
          ordenar_por="", decrescente=False, destacar=None, totais=None,
          altura=None, densidade="normal", numerar=False, chave=None,
          vazio="sem dados"):
    """Uma grade de dados completa. Devolve as linhas **selecionadas**.

        escolhidas := V.grade(pedidos,
            colunas := [V.coluna("total", tipo := "moeda")],
            selecionar := "varias",
            totais := ["total"])

    Sem seleção, devolve as linhas da página atual — que é o que se usa
    para exportar exatamente o que está na tela.

    `paginar := 0` desliga a paginação. Ela é ligada por padrão porque
    uma listagem sem teto é a forma mais comum de um painel travar: mil
    linhas viram mil vezes o custo de desenhar, a cada clique.
    """
    ctx = _ctx()
    k = ctx.chave_para("grade", "", chave)
    registros = _registros(dados)
    config = _colunas_de(registros, colunas)
    nomes = [c["nome"] for c in config if not c["oculta"]]

    # ── filtro ──
    termo = _str(ctx.valor_de(f"{k}:busca", "")).strip().lower()
    if busca and termo:
        registros = [r for r in registros
                     if any(termo in _str(r.get(c)).lower() for c in nomes)]

    # ── ordem ──
    ordem = _str(ctx.valor_de(f"{k}:ordem", _str(ordenar_por)))
    desc = bool(ctx.valor_de(f"{k}:desc", bool(decrescente)))
    if ordem and ordem in nomes:
        registros = sorted(registros, key=lambda r: _chave_de_ordem(r.get(ordem)),
                           reverse=desc)

    total_linhas = len(registros)
    por_pagina = max(0, int(paginar or 0))
    paginas = max(1, math.ceil(total_linhas / por_pagina)) if por_pagina else 1
    atual = int(C._numero_de(ctx.valor_de(f"{k}:pagina", 1), 1) or 1)
    atual = max(1, min(paginas, atual))
    ctx.guardar_valor(f"{k}:pagina", atual)
    visiveis = (registros[(atual - 1) * por_pagina: atual * por_pagina]
                if por_pagina else registros)

    # ── seleção ──
    modo = _str(selecionar)
    marcadas = ctx.valor_de(f"{k}:selecao", [])
    if not isinstance(marcadas, (list, tuple)):
        marcadas = [marcadas] if marcadas not in (None, "") else []
    marcadas = [_str(m) for m in marcadas]
    if modo == "linha" and len(marcadas) > 1:
        marcadas = marcadas[-1:]
    ctx.guardar_valor(f"{k}:selecao", marcadas)

    linhas = []
    for posicao, registro in enumerate(visiveis):
        indice = (atual - 1) * por_pagina + posicao
        celulas = []
        for col in config:
            if col["oculta"]:
                continue
            celulas.append(_celula(registro, col, destacar))
        linhas.append({"id": str(indice), "celulas": celulas,
                       "marcada": str(indice) in marcadas})

    rodape = _totais(registros, config, totais)
    _por("grade", {
        "chave": k, "colunas": [c for c in config if not c["oculta"]],
        "linhas": linhas, "busca": bool(busca), "termo": termo,
        "ordem": ordem, "desc": desc, "pagina": atual, "paginas": paginas,
        "total": total_linhas, "por_pagina": por_pagina,
        "selecionar": modo, "rodape": rodape, "altura": altura,
        "densidade": _str(densidade), "numerar": bool(numerar),
        "vazio": _str(vazio), "primeiro": (atual - 1) * por_pagina,
    }, chave=k)

    if modo:
        escolhidas = [registros[int(i)] for i in marcadas
                      if i.isdigit() and int(i) < len(registros)]
        return escolhidas
    return visiveis


def _celula(registro, col, destacar):
    bruto = registro.get(col["nome"])
    texto = _texto_de_celula(bruto, col)
    cor = ""
    for r in (destacar or []):
        if r.get("pintar") != col["nome"]:
            continue
        if _casa_regra(registro.get(r["coluna"]), r["condicao"], r.get("valor")):
            cor = r.get("cor", "")
            break
    dado = {"texto": texto, "cor": cor, "tipo": col["tipo"],
            "alinhar": col["alinhar"]}
    if col["tipo"] in ("barra", "progresso"):
        valor = _num(bruto) or 0.0
        piso = _num(col.get("minimo")) or 0.0
        teto = _num(col.get("maximo"))
        if teto is None or teto == piso:
            teto = piso + 100.0
        dado["fracao"] = max(0.0, min(1.0, (valor - piso) / (teto - piso)))
        dado["texto"] = _texto_de_celula(bruto, col)
    elif col["tipo"] == "mini":
        serie = bruto if isinstance(bruto, (list, tuple)) else []
        dado["serie"] = [_num(v) or 0.0 for v in serie]
        dado["texto"] = ""
    elif col["tipo"] == "logico":
        dado["logico"] = bool(bruto) and _str(bruto) not in ("no", "0", "")
        dado["texto"] = ""
    elif col["tipo"] == "link":
        dado["destino"] = _str(bruto)
        dado["texto"] = _str(col.get("prefixo") or bruto)
    elif col["tipo"] == "imagem":
        dado["origem"] = _str(bruto)
        dado["texto"] = ""
    elif col["tipo"] == "selo":
        dado["texto"] = _str(bruto)
        dado["cor"] = cor or _cor_de_selo(bruto, col)
    return dado


def _cor_de_selo(valor, col):
    """A cor de um selo sai da posição do valor nas opções.

    Sem opções, ela sai do próprio texto por uma soma estável: a mesma
    palavra recebe a mesma cor em toda a aplicação, que é o que faz a
    cor significar alguma coisa.
    """
    texto = _str(valor)
    if col.get("opcoes") and texto in col["opcoes"]:
        cores = col.get("cores") or ["info", "sucesso", "aviso", "erro",
                                     "primaria", "neutro"]
        return cores[col["opcoes"].index(texto) % len(cores)]
    conhecidas = {"pago": "sucesso", "ativo": "sucesso", "ok": "sucesso",
                  "pendente": "aviso", "aberto": "aviso",
                  "cancelado": "erro", "erro": "erro", "falhou": "erro",
                  "inativo": "neutro"}
    return conhecidas.get(texto.strip().lower(), "neutro")


def _texto_de_celula(bruto, col):
    if bruto is None:
        return ""
    formato = col.get("formato") or ""
    if formato in FORMATOS and formato != "texto":
        casas = col.get("casas")
        if formato == "moeda":
            return moeda(bruto, casas=casas if casas is not None else 2)
        if formato in ("numero", "percentual", "compacto") and casas is not None:
            return FORMATOS[formato](bruto, casas)
        return FORMATOS[formato](bruto)
    return _str(col.get("prefixo", "")) + _str(bruto) + _str(col.get("sufixo", ""))


def _chave_de_ordem(valor):
    """Número antes de texto, e ausência por último.

    Sem isto, ordenar uma coluna com um `void` no meio compara tipos
    diferentes e dispara — a listagem inteira some por causa de uma
    célula vazia.
    """
    if valor is None or _str(valor) == "":
        return (2, 0.0, "")
    n = _num(valor)
    if n is not None:
        return (0, n, "")
    return (1, 0.0, _str(valor).lower())


def _totais(registros, config, pedidos):
    """A linha de rodapé. `totais` aceita nomes ou `{coluna: operacao}`."""
    if not pedidos:
        return []
    if isinstance(pedidos, (list, tuple, set)):
        pedidos = {str(nome): "soma" for nome in pedidos}
    saida = []
    for col in config:
        if col["oculta"]:
            continue
        operacao = pedidos.get(col["nome"])
        if not operacao:
            saida.append({"texto": "", "alinhar": col["alinhar"]})
            continue
        valores = [v for v in (_num(r.get(col["nome"])) for r in registros)
                   if v is not None]
        resultado = _operar(operacao, valores)
        saida.append({"texto": _texto_de_celula(resultado, col)
                      if resultado is not None else "—",
                      "alinhar": col["alinhar"], "operacao": _str(operacao)})
    return saida


def _operar(operacao, valores):
    if not valores:
        return None
    nome = _str(operacao)
    if nome == "soma":
        return sum(valores)
    if nome in ("media", "média"):
        return sum(valores) / len(valores)
    if nome in ("minimo", "mínimo"):
        return min(valores)
    if nome in ("maximo", "máximo"):
        return max(valores)
    if nome in ("contar", "quantidade"):
        return len(valores)
    return sum(valores)


# ═══════════════════════════════════════════════════════════
#  O editor
# ═══════════════════════════════════════════════════════════

def editor(dados, colunas=None, acrescentar=True, remover=True,
           altura=None, chave=None):
    """Uma tabela que se edita na tela. Devolve as linhas como estão agora.

        linhas := V.editor(precos, colunas := [
            V.coluna("produto"),
            V.coluna("preco", tipo := "moeda", editavel := yes),
        ])

    O que sai daqui é um cluster de vaults novo — o original não é
    tocado. É a mesma escolha do `record`/`with` da linguagem: o
    pipeline que trouxe o dado continua reexecutável.

    **Toda coluna é editável a menos que se diga o contrário** com
    `V.coluna(..., editavel := no)`: um editor cujas colunas nascem
    travadas é um editor que não edita.
    """
    ctx = _ctx()
    k = ctx.chave_para("editor", "", chave)
    originais = _registros(dados)
    config = _colunas_de(originais, colunas)
    for col in config:
        if colunas is None:
            col["editavel"] = True

    # As linhas acrescentadas moram na sessão: elas não existem no dado
    # que veio, e reconstruí-las do zero a cada execução as apagaria.
    extras = ctx.sessao.obter(f"__editor__{k}", [])
    if not isinstance(extras, list):
        extras = []
    removidas = set(ctx.sessao.obter(f"__editor_rm__{k}", []) or [])

    if acrescentar and ctx.foi_acionado(f"{k}:novo"):
        extras = extras + [{c["nome"]: "" for c in config}]
        ctx.sessao.definir(f"__editor__{k}", extras)
    for alvo in list(ctx.sessao.eventos):
        if alvo.startswith(f"{k}:rm:"):
            removidas.add(alvo.rsplit(":", 1)[-1])
            ctx.sessao.definir(f"__editor_rm__{k}", sorted(removidas))

    todas = list(originais) + list(extras)
    saida, linhas = [], []
    for indice, registro in enumerate(todas):
        if str(indice) in removidas:
            continue
        novo, celulas = {}, []
        for col in config:
            campo = f"{k}:{indice}:{col['nome']}"
            bruto = registro.get(col["nome"])
            if col["editavel"]:
                atual = ctx.valor_de(campo, bruto)
                ctx.guardar_valor(campo, atual)
            else:
                atual = bruto
            novo[col["nome"]] = _converter(atual, col)
            celulas.append({
                "campo": campo, "valor": _str(atual if atual is not None else ""),
                "tipo": col["tipo"], "editavel": col["editavel"],
                "opcoes": col.get("opcoes") or [],
                "alinhar": col["alinhar"],
                "texto": _texto_de_celula(bruto, col),
            })
        saida.append(novo)
        linhas.append({"id": str(indice), "celulas": celulas})

    _por("editor", {"chave": k, "colunas": config, "linhas": linhas,
                    "acrescentar": bool(acrescentar), "remover": bool(remover),
                    "altura": altura}, chave=k)
    return saida


def _converter(valor, col):
    """O texto do campo volta ao tipo da coluna.

    Sem isso, editar uma célula numérica devolveria `"12"` e a soma do
    rodapé passaria a concatenar — um bug que aparece como um total
    absurdo, e não como erro.
    """
    if col["tipo"] in ("numero", "moeda", "percentual", "compacto", "barra",
                       "progresso"):
        n = _num(valor)
        if n is None:
            return valor
        return int(n) if float(n).is_integer() else n
    if col["tipo"] == "logico":
        return bool(valor) and _str(valor) not in ("no", "0", "", "false")
    return valor


# ═══════════════════════════════════════════════════════════
#  Indicadores
# ═══════════════════════════════════════════════════════════

def indicador(rotulo, valor, variacao=None, cor="", ajuda="", nota="",
              mini=None, alvo=None, formato="", icone=""):
    """O cartão de um número — o bloco de que um painel é feito.

        V.indicador("Patrimônio líquido", 1091947.91,
                    variacao := 4.2, cor := "info",
                    nota := "Total em ago/26", formato := "moeda")

    A diferença para `V.metrica` é o que ele carrega: faixa de cor à
    esquerda, nota abaixo, alvo com barra de progresso e uma série
    miúda ao fundo. A métrica continua existindo porque um número
    simples não deveria pagar por nada disso.
    """
    texto = formatar(valor, formato) if formato else _str(valor)
    progresso = None
    if alvo is not None:
        atingido, esperado = _num(valor) or 0.0, _num(alvo) or 0.0
        progresso = {
            "fracao": max(0.0, min(1.0, atingido / esperado)) if esperado else 0.0,
            "alvo": formatar(alvo, formato) if formato else _str(alvo)}
    serie = [_num(v) or 0.0 for v in (mini or [])] if mini else []
    _por("indicador", {
        "rotulo": _str(rotulo), "valor": texto, "variacao": variacao,
        "cor": _str(cor), "ajuda": _str(ajuda), "nota": _str(nota),
        "serie": serie, "progresso": progresso, "icone": _str(icone)})
    return valor


#: O que um vault de `V.indicadores` pode trazer. Uma chave a mais
#: seria um erro de digitação passando calado — e o cartão sairia com o
#: padrão, sem nada denunciando.
_CAMPOS_DE_INDICADOR = ("variacao", "cor", "ajuda", "nota", "mini", "alvo",
                        "formato", "icone")


def indicadores(itens, colunas=0):
    """Vários indicadores numa faixa. Cada item é o vault de um cartão.

        V.indicadores([
            {"rotulo": "Receita", "valor": 128400, "formato": "moeda"},
            {"rotulo": "Clientes", "valor": 2500, "variacao": 8.1},
        ])

    Sem `colunas`, a faixa se ajusta sozinha à largura — quatro cartões
    numa tela larga, um no celular, sem ninguém escolher o número.
    """
    from .layout import Area
    lista = list(itens or [])
    no = _ctx().por(No("indicadores", {"colunas": max(0, int(colunas))}))
    area = Area(no)
    for item in lista:
        if not isinstance(item, dict):
            area._dentro(indicador, (_str(item), item), {})
            continue
        dados = {k: v for k, v in item.items() if k in _CAMPOS_DE_INDICADOR}
        area._dentro(indicador, (
            item.get("rotulo", ""), item.get("valor", "")), dados)
    return lista


# ═══════════════════════════════════════════════════════════
#  Descrever
# ═══════════════════════════════════════════════════════════

def estatisticas(dados, colunas=None):
    """Contagem, ausências, média, desvio, mínimo, mediana e máximo.

    Só das colunas numéricas: a média de uma coluna de nomes é a
    resposta a uma pergunta que ninguém fez, e enchê-la de traços
    esconde as colunas que interessam.
    """
    registros = _registros(dados)
    nomes = [c["nome"] for c in _colunas_de(registros, colunas)]
    linhas = []
    for nome in nomes:
        valores = [_num(r.get(nome)) for r in registros]
        numericos = [v for v in valores if v is not None]
        if not numericos:
            continue
        ordenados = sorted(numericos)
        media = sum(numericos) / len(numericos)
        variancia = (sum((v - media) ** 2 for v in numericos) / len(numericos)
                     if len(numericos) > 1 else 0.0)
        meio = len(ordenados) // 2
        mediana = (ordenados[meio] if len(ordenados) % 2
                   else (ordenados[meio - 1] + ordenados[meio]) / 2)
        linhas.append({
            "coluna": nome,
            "contagem": len(numericos),
            "ausentes": len(registros) - len(numericos),
            "media": round(media, 4),
            "desvio": round(math.sqrt(variancia), 4),
            "minimo": ordenados[0],
            "mediana": round(mediana, 4),
            "maximo": ordenados[-1],
        })
    C.frame(linhas, ["coluna", "contagem", "ausentes", "media", "desvio",
                     "minimo", "mediana", "maximo"])
    return linhas


# ═══════════════════════════════════════════════════════════
#  Internas
# ═══════════════════════════════════════════════════════════

def _registros(dados):
    """Tudo o que a Vitrine aceita como tabela vira cluster de vaults."""
    from . import graficos as G
    registros = G._registros(dados)
    return [r if isinstance(r, dict) else {"valor": r} for r in registros]


def _colunas_de(registros, colunas):
    """A configuração final, completando o que não foi dito.

    Um nome solto vira uma coluna com o tipo **inferido do dado**, e a
    inferência olha o primeiro valor não nulo — não o primeiro, que num
    conjunto real costuma ser justamente o que falta.
    """
    if colunas:
        saida = []
        for item in colunas:
            if isinstance(item, dict) and "nome" in item:
                saida.append({**coluna(item["nome"]), **item})
            else:
                saida.append(coluna(_str(item)))
        return saida

    vistos = []
    for registro in registros:
        for nome in registro:
            if nome not in vistos:
                vistos.append(nome)
    saida = []
    for nome in vistos:
        amostra = next((r.get(nome) for r in registros
                        if r.get(nome) is not None), None)
        if isinstance(amostra, bool):
            saida.append(coluna(nome, tipo="logico"))
        elif isinstance(amostra, (int, float)):
            saida.append(coluna(nome, tipo="numero",
                                casas=0 if isinstance(amostra, int) else 2))
        elif isinstance(amostra, (list, tuple)):
            saida.append(coluna(nome, tipo="mini"))
        else:
            saida.append(coluna(nome))
    return saida
