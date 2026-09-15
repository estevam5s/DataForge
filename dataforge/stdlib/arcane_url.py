# -*- coding: utf-8 -*-
"""Arcane.Url — ler, montar e escapar endereços.

O que faltava
-------------
Todo programa que fala HTTP mexe com URL, e a linguagem não tinha onde.
O Kiln parte a query string por dentro para entregar `req["query"]`, e
`Arcane.Http` monta endereços com concatenação de texto — mas nada disso
estava ao alcance de quem escreve:

    ler("https://loja.com/itens?pagina=2&q=café#topo")
        -> {"esquema": "https", "host": "loja.com", "caminho": "/itens",
            "query": {"pagina": "2", "q": "café"}, ...}

Escrever isso com `split` é o caminho conhecido para dois bugs: o `?`
que também aparece dentro de um valor, e o acento que precisa virar
`%C3%A9` — e não virava.

Três decisões que valem lembrar
-------------------------------
1. **`query` devolve VAULT, e `query_lista` devolve o cluster.**
   `?tag=a&tag=b` é legítimo e comum em filtro de busca. Um vault não
   guarda as duas, e devolver só a última, calado, perde metade do
   filtro. O vault (com a última, que é o que quase todo servidor usa)
   atende o caso comum; quem precisa das duas pede `query_lista`, e a
   diferença está escrita aqui em vez de virar surpresa.

2. **A porta sai como `Integer`, ou `void`.** Ela vem de texto, e
   devolvê-la como texto faria `porta + 1` concatenar em vez de somar.
   Sem porta na URL, `void` — e não 80, que seria inventar o que a URL
   não disse.

3. **`juntar` resolve caminho relativo, como um navegador.**
   `juntar("https://a.com/doc/x", "../y")` dá `https://a.com/y`. Colar
   com `+` produz `https://a.com/doc/x/../y`, que funciona por acidente
   num servidor e falha em outro.
"""

import urllib.parse as _up

from ..builtins import _df_type as _nome_do_tipo
from ..errors import RuntimeError_


def _erro(mensagem, nota="", dica=""):
    return RuntimeError_(mensagem, 0, 0, nota=nota, dica=dica,
                         doc="biblioteca/url")


def _exigir_texto(valor, onde):
    if not isinstance(valor, str):
        raise _erro(f"'{onde}' precisa de um texto, e recebeu "
                    f"{_nome_do_tipo(valor)}.",
                    dica="converta antes com  str(x)")
    return valor


# ══════════════════════════════════════════════════════════════
#  Ler
# ══════════════════════════════════════════════════════════════

def ler(endereco):
    """As partes de um endereço, como vault.

    Campos: esquema, usuario, senha, host, porta, caminho, query,
    query_texto, fragmento e origem.
    """
    _exigir_texto(endereco, "Url.ler")
    p = _up.urlsplit(endereco)
    try:
        porta = p.port
    except ValueError:
        # 'http://a:99999' — porta fora da faixa. O resto da URL ainda é
        # legível, e recusar tudo por causa dela esconderia o que se quer
        # ver: qual host essa URL maluca aponta.
        porta = None
    return {
        "esquema": p.scheme,
        "usuario": p.username or "",
        "senha": p.password or "",
        "host": p.hostname or "",
        "porta": porta,
        "caminho": p.path,
        "query": query(p.query),
        "query_lista": query_lista(p.query),
        "query_texto": p.query,
        "fragmento": p.fragment,
        # A origem NAO leva credencial: 'netloc' traz 'ana:senha@host', e
        # 'origem' e o campo que vai para log e para cabecalho de CORS.
        # A senha vazaria por ali sem ninguem pedir.
        "origem": (f"{p.scheme}://{p.hostname}"
                   + (f":{porta}" if porta is not None else "")
                   if p.scheme and p.hostname else ""),
    }


def host_de(endereco):
    """Só o host — o caso mais comum de 'ler'."""
    return ler(endereco)["host"]


def e_absoluto(endereco):
    """Tem esquema e host? `/itens` não é absoluto; `https://a.com/` é."""
    p = _up.urlsplit(_exigir_texto(endereco, "Url.e_absoluto"))
    return bool(p.scheme and p.netloc)


# ══════════════════════════════════════════════════════════════
#  Montar
# ══════════════════════════════════════════════════════════════

#: As chaves que 'montar' conhece. Ler as soltas engoliria um erro de
#: digitação: 'caminh' viraria uma URL sem caminho, sem nada denunciando.
CAMPOS = ("esquema", "usuario", "senha", "host", "porta", "caminho",
          "query", "fragmento")


def montar(partes):
    """O endereço a partir das partes. É o contrário de `ler`.

    `query` aceita vault (`{"p": 2}`) ou texto já pronto.
    """
    if not isinstance(partes, dict):
        raise _erro(f"'Url.montar' precisa de um vault, e recebeu "
                    f"{_nome_do_tipo(partes)}.",
                    dica='montar({"esquema": "https", "host": "a.com"})')
    desconhecidas = [k for k in partes if k not in CAMPOS
                     and not k.startswith("_")]
    if desconhecidas:
        raise _erro(
            f"'Url.montar' não conhece: {', '.join(sorted(desconhecidas))}.",
            nota=f"os campos são: {', '.join(CAMPOS)}",
            dica="um nome trocado montaria um endereço sem aquela parte, "
                 "sem nada denunciando")

    esquema = partes.get("esquema") or ""
    host = partes.get("host") or ""
    porta = partes.get("porta")
    usuario = partes.get("usuario") or ""
    senha = partes.get("senha") or ""

    autoridade = host
    if porta not in (None, ""):
        autoridade = f"{host}:{porta}"
    if usuario:
        credencial = f"{usuario}:{senha}" if senha else usuario
        autoridade = f"{credencial}@{autoridade}"

    consulta = partes.get("query")
    if isinstance(consulta, dict):
        consulta = query_texto(consulta)
    elif consulta is None:
        consulta = ""

    return _up.urlunsplit((esquema, autoridade, partes.get("caminho") or "",
                           consulta, partes.get("fragmento") or ""))


def juntar(base, relativo):
    """Resolve um endereço relativo contra uma base, como um navegador."""
    _exigir_texto(base, "Url.juntar")
    _exigir_texto(relativo, "Url.juntar")
    return _up.urljoin(base, relativo)


def com_query(endereco, novos):
    """O mesmo endereço com estes parâmetros — os outros ficam.

    É o que se faz para paginar: `com_query(url, {"pagina": 3})`.
    """
    partes = _up.urlsplit(_exigir_texto(endereco, "Url.com_query"))
    if not isinstance(novos, dict):
        raise _erro(f"'Url.com_query' precisa de um vault, e recebeu "
                    f"{_nome_do_tipo(novos)}.")
    atual = query(partes.query)
    atual.update({k: v for k, v in novos.items() if v is not None})
    # 'void' APAGA o parâmetro: é como se tira um filtro de uma busca.
    for chave, valor in novos.items():
        if valor is None:
            atual.pop(chave, None)
    return _up.urlunsplit((partes.scheme, partes.netloc, partes.path,
                           query_texto(atual), partes.fragment))


def sem_query(endereco):
    """O endereço sem a query nem o fragmento."""
    p = _up.urlsplit(_exigir_texto(endereco, "Url.sem_query"))
    return _up.urlunsplit((p.scheme, p.netloc, p.path, "", ""))


# ══════════════════════════════════════════════════════════════
#  Query string
# ══════════════════════════════════════════════════════════════

def query(texto):
    """A query string como vault. Chave repetida fica com a ÚLTIMA.

    `?tag=a&tag=b` é legítimo, e um vault não guarda as duas. A última é
    o que quase todo servidor usa; `query_lista` devolve as duas.
    """
    if isinstance(texto, dict):
        return dict(texto)
    _exigir_texto(texto, "Url.query")
    return {k: v[-1] for k, v in
            _up.parse_qs(texto.lstrip("?"), keep_blank_values=True).items()}


def query_lista(texto):
    """A query string como vault de clusters — guarda a chave repetida."""
    if isinstance(texto, dict):
        return {k: (v if isinstance(v, list) else [v]) for k, v in texto.items()}
    _exigir_texto(texto, "Url.query_lista")
    return {k: list(v) for k, v in
            _up.parse_qs(texto.lstrip("?"), keep_blank_values=True).items()}


def query_texto(dados):
    """O vault como query string, já escapada.

    Um valor em cluster vira a chave repetida (`tag=a&tag=b`), que é o
    contrário exato de `query_lista`.
    """
    if not isinstance(dados, dict):
        raise _erro(f"'Url.query_texto' precisa de um vault, e recebeu "
                    f"{_nome_do_tipo(dados)}.")
    pares = []
    for chave, valor in dados.items():
        if isinstance(valor, (list, tuple)):
            pares.extend((chave, _texto_do_valor(v)) for v in valor)
        elif valor is None:
            continue
        else:
            pares.append((chave, _texto_do_valor(valor)))
    return _up.urlencode(pares)


def _texto_do_valor(valor):
    """`yes` vira "yes", e não "True": quem lê é um .df do outro lado."""
    if isinstance(valor, bool):
        return "yes" if valor else "no"
    if valor is None:
        return ""
    return str(valor)


# ══════════════════════════════════════════════════════════════
#  Escapar
# ══════════════════════════════════════════════════════════════

def escapar(texto):
    """Para dentro de um CAMINHO: '/' é preservado."""
    return _up.quote(_exigir_texto(texto, "Url.escapar"), safe="/")


def escapar_tudo(texto):
    """Para dentro de um VALOR de query: '/' também é escapado."""
    return _up.quote(_exigir_texto(texto, "Url.escapar_tudo"), safe="")


def desescapar(texto):
    """Volta de `%C3%A9` para `é`. O '+' vira espaço, como numa query."""
    return _up.unquote_plus(_exigir_texto(texto, "Url.desescapar"))


class ArcaneUrl:
    """O dicionario que `adopt Arcane.Url` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Url",

            # ── Ler ──
            "ler": ler,
            "host_de": host_de,
            "e_absoluto": e_absoluto,
            "campos": lambda: list(CAMPOS),

            # ── Montar ──
            "montar": montar,
            "juntar": juntar,
            "com_query": com_query,
            "sem_query": sem_query,

            # ── Query string ──
            "query": query,
            "query_lista": query_lista,
            "query_texto": query_texto,

            # ── Escapar ──
            "escapar": escapar,
            "escapar_tudo": escapar_tudo,
            "desescapar": desescapar,
        }
