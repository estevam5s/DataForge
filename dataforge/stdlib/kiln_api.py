# -*- coding: utf-8 -*-
"""
As peças de uma API HTTP que o Kiln não tinha.

    Kiln.problema(404, "Pedido não encontrado", $"não há pedido {id}")
    tipo := Kiln.negociar(req, ["application/json", "text/csv"])
    falha := Kiln.precondicao(req, Kiln.etiqueta(pedido["versao"]))
    proximo := Kiln.cursor({"depois_de": ultimo_id}, segredo)
    Kiln.json(pagina, 200, {"Link": Kiln.links("/pedidos", 2, 9)})

Cada uma responde a uma pergunta que toda API acaba fazendo, e que cada
projeto respondia à mão — e de um jeito diferente do vizinho:

| Peça | A pergunta | A norma |
|---|---|---|
| `problema` | como devolver um erro que um programa consegue ler? | RFC 9457 |
| `negociar` | JSON ou CSV, se o cliente aceita os dois? | RFC 9110 §12 |
| `precondicao` | duas pessoas editaram o mesmo recurso — quem perde? | RFC 9110 §13 |
| `cursor` | como paginar uma lista que muda enquanto se pagina? | — |
| `links` | como o cliente acha a próxima página sem montar URL? | RFC 8288 |

Nada aqui é middleware. São funções que a rota chama, e o motivo é o
mesmo de `Kiln.validar`: a decisão (que status, que tipo, que versão)
é da rota, e esconder isso num gancho faz a resposta depender de algo
que quem lê a rota não vê.
"""

import base64
import hashlib
import json

from ..errors import RuntimeError_

_DOC = "api"

#: As chaves que a RFC 9457 define. Um `extras` que as repita seria
#: silenciosamente sobrescrito — ou sobrescreveria o status real.
_RESERVADAS = ("type", "title", "status", "detail", "instance")


def _erro(mensagem, dica=""):
    erro = RuntimeError_(mensagem, doc=_DOC)
    if dica:
        erro.dica = dica
    return erro


def _resposta(corpo, status, cabecalhos, tipo):
    # Import tardio: kiln.py importa este módulo para montar o seu
    # dicionário, e o caminho contrário no topo seria um ciclo.
    from .kiln import resposta
    return resposta(corpo, status, cabecalhos, tipo)


def _cabecalho(req, nome):
    cabs = (req or {}).get("headers") or {}
    valor = cabs.get(nome)
    if valor is None:
        valor = cabs.get(nome.title())
    return valor


# ═══════════════════════════════════════════════════════════
#  Problema — RFC 9457
# ═══════════════════════════════════════════════════════════

def problema(status, titulo, detalhe=None, tipo="about:blank",
             extras=None, instancia=None):
    """Um erro em `application/problem+json`.

    `titulo` é o mesmo para toda ocorrência do tipo ("Saldo
    insuficiente"); `detalhe` fala desta ocorrência ("o saldo é 30, e a
    compra custa 50"). Separar os dois é o que deixa um cliente decidir
    pelo `type` e mostrar o `detail` — sem comparar texto.
    """
    status = int(status)
    if not 400 <= status <= 599:
        raise _erro(
            f"um problema é um erro, e {status} não é status de erro.",
            dica="use 4xx (o pedido está errado) ou 5xx (o servidor "
                 "falhou); para sucesso, Kiln.json")
    corpo = {"type": str(tipo or "about:blank"), "title": str(titulo),
             "status": status}
    if detalhe is not None:
        corpo["detail"] = str(detalhe)
    if instancia is not None:
        corpo["instance"] = str(instancia)
    for chave, valor in dict(extras or {}).items():
        if chave in _RESERVADAS:
            raise _erro(
                f"'{chave}' é um campo da própria RFC 9457 e não pode vir "
                f"em extras.",
                dica=f"passe-o como argumento: problema(status, titulo, "
                     f"detalhe, tipo, extras, instancia)")
        corpo[chave] = valor
    return _resposta(corpo, status, None,
                     "application/problem+json; charset=utf-8")


# ═══════════════════════════════════════════════════════════
#  Negociação de conteúdo — RFC 9110 §12.5.1
# ═══════════════════════════════════════════════════════════

def _faixas_do_accept(texto):
    """[(tipo, subtipo, q, especificidade, ordem)] do cabeçalho Accept."""
    faixas = []
    for ordem, parte in enumerate(str(texto).split(",")):
        pedacos = [p.strip() for p in parte.split(";")]
        if not pedacos[0]:
            continue
        tipo, _, subtipo = pedacos[0].lower().partition("/")
        q = 1.0
        for parametro in pedacos[1:]:
            nome, _, valor = parametro.partition("=")
            if nome.strip().lower() == "q":
                try:
                    q = float(valor)
                except ValueError:
                    q = 0.0
        especificidade = (0 if tipo == "*" else 1) + (0 if subtipo in ("*", "") else 1)
        faixas.append((tipo, subtipo or "*", q, especificidade, ordem))
    return faixas


def _q_para(oferecido, faixas):
    """O q da faixa MAIS ESPECÍFICA que casa — não o da primeira."""
    tipo, _, subtipo = oferecido.lower().partition("/")
    melhor = None
    for f_tipo, f_sub, q, esp, _ordem in faixas:
        casa = (f_tipo in ("*", tipo)) and (f_sub in ("*", subtipo))
        if casa and (melhor is None or esp > melhor[1]):
            melhor = (q, esp)
    return None if melhor is None else melhor[0]


def negociar(req, oferecidos):
    """O tipo que o cliente mais quer, entre os que você oferece.

    Devolve `void` quando nenhum serve — e aí a resposta honesta é 406.
    Sem `Accept`, vale o primeiro oferecido: o cliente não pediu nada.
    `q=0` é uma recusa explícita, e **vence** o curinga: com
    `*/*, text/csv;q=0` o CSV não é escolhido nunca.
    """
    lista = [str(o) for o in (oferecidos or [])]
    if not lista:
        raise _erro("negociar precisa de ao menos um tipo oferecido.",
                    dica='Kiln.negociar(req, ["application/json"])')
    aceite = _cabecalho(req, "accept")
    if not aceite:
        return lista[0]
    faixas = _faixas_do_accept(aceite)
    melhor, melhor_q = None, 0.0
    for oferecido in lista:
        q = _q_para(oferecido, faixas)
        # Estritamente maior: no empate vence a ordem de quem oferece.
        if q is not None and q > melhor_q:
            melhor, melhor_q = oferecido, q
    return melhor


# ═══════════════════════════════════════════════════════════
#  Pré-condição — RFC 9110 §13
# ═══════════════════════════════════════════════════════════

def etiqueta(valor):
    """Uma ETag FORTE para um valor (a versão, o `atualizado_em`…).

    Forte importa: pela RFC, `If-Match` só compara etiquetas fortes, e
    uma `W/"…"` nunca casa. É a etiqueta que `precondicao` espera.
    """
    bruto = json.dumps(valor, sort_keys=True, default=str).encode()
    return '"' + hashlib.sha256(bruto).hexdigest()[:24] + '"'


def _lista_de_etiquetas(texto):
    return [p.strip() for p in str(texto).split(",") if p.strip()]


def precondicao(req, etiqueta_atual, exigir=False):
    """`void` quando o pedido pode seguir; senão, a resposta pronta.

    É o controle de concorrência **otimista** de uma API: o cliente
    manda o `If-Match` com a etiqueta que leu, e se o recurso mudou no
    meio o servidor responde **412** em vez de apagar a mudança do
    outro. `etiqueta_atual` é `void` quando o recurso não existe.

    | Cabeçalho | Quando falha |
    |---|---|
    | `If-Match: "x"` | a etiqueta atual é outra, ou o recurso não existe |
    | `If-Match: *` | o recurso não existe |
    | `If-None-Match: *` | o recurso **já** existe (criar sem sobrescrever) |
    | nenhum, com `exigir := yes` | sempre — **428** |
    """
    se_corresponde = _cabecalho(req, "if-match")
    se_nao = _cabecalho(req, "if-none-match")

    if se_corresponde:
        pedidas = _lista_de_etiquetas(se_corresponde)
        if "*" in pedidas:
            casa = etiqueta_atual is not None
        else:
            atual = None if etiqueta_atual is None else str(etiqueta_atual)
            # Comparação FORTE: etiqueta fraca nunca casa em If-Match.
            casa = (atual is not None and not atual.startswith("W/")
                    and any(p == atual for p in pedidas
                            if not p.startswith("W/")))
        if not casa:
            return problema(
                412, "O recurso mudou",
                "a versão que você leu não é mais a atual; leia de novo "
                "e reaplique a mudança",
                extras={"atual": etiqueta_atual})
        return None

    if se_nao and _lista_de_etiquetas(se_nao) == ["*"]:
        if etiqueta_atual is not None:
            return problema(412, "O recurso já existe",
                            "If-None-Match: * pede para criar só se não "
                            "existir")
        return None

    if exigir:
        return problema(
            428, "Falta a pré-condição",
            "este recurso só aceita escrita com If-Match: leia-o, guarde "
            "a ETag e mande-a de volta",
            extras={"atual": etiqueta_atual})
    return None


# ═══════════════════════════════════════════════════════════
#  Cursor — paginação que não pula nem repete
# ═══════════════════════════════════════════════════════════

def cursor(dados, segredo=None):
    """Um cursor opaco. Com `segredo`, também à prova de adulteração.

    A paginação por página (`?pagina=3`) pula ou repete itens quando a
    lista muda entre dois pedidos: um item novo no topo empurra todos
    uma posição. O cursor diz **onde parou** (`depois_de: 1042`), e isso
    não se move. Opaco, para o cliente não montar um à mão; assinado,
    para ele não conseguir.
    """
    if not isinstance(dados, dict):
        raise _erro("o cursor guarda um vault.",
                    dica='Kiln.cursor({"depois_de": ultimo["id"]})')
    if segredo:
        from .kiln import _assinar
        return _assinar(dados, str(segredo))
    bruto = json.dumps(dados, sort_keys=True, default=str).encode()
    return base64.urlsafe_b64encode(bruto).decode().rstrip("=")


def ler_cursor(texto, segredo=None):
    """O vault de um cursor, ou `void` se ele é inválido.

    Não levanta: um cursor ruim vem de fora, e a rota decide o 400. Um
    cursor sem assinatura, lido com `segredo`, também é `void` — aceitar
    seria abrir mão da assinatura justamente quando ela foi pedida.
    """
    if not texto:
        return None
    texto = str(texto)
    if segredo:
        from .kiln import _conferir
        lido = _conferir(texto, str(segredo))
        return lido if isinstance(lido, dict) else None
    try:
        preenchido = texto + "=" * (-len(texto) % 4)
        lido = json.loads(base64.urlsafe_b64decode(preenchido.encode()))
    except Exception:                                  # noqa: BLE001
        return None
    return lido if isinstance(lido, dict) else None


# ═══════════════════════════════════════════════════════════
#  Links — RFC 8288
# ═══════════════════════════════════════════════════════════

def links(caminho, pagina, paginas, parametro="pagina"):
    """O cabeçalho `Link` com first, prev, next e last.

    O cliente segue `rel="next"` sem saber como a URL é montada — e a
    URL pode mudar (de página para cursor) sem quebrar cliente nenhum.
    """
    pagina, paginas = int(pagina), max(1, int(paginas))
    separador = "&" if "?" in str(caminho) else "?"

    def url(n):
        return f"<{caminho}{separador}{parametro}={n}>"

    partes = [f'{url(1)}; rel="first"']
    if pagina > 1:
        partes.append(f'{url(pagina - 1)}; rel="prev"')
    if pagina < paginas:
        partes.append(f'{url(pagina + 1)}; rel="next"')
    partes.append(f'{url(paginas)}; rel="last"')
    return ", ".join(partes)


SIMBOLOS = {
    "problema": problema,
    "negociar": negociar,
    "etiqueta": etiqueta,
    "precondicao": precondicao,
    "cursor": cursor,
    "ler_cursor": ler_cursor,
    "links": links,
}
