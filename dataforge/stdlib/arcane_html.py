# -*- coding: utf-8 -*-
"""Arcane.Html — ler HTML: achar, extrair, limpar.

O que faltava
-------------
Ler uma página — um preço, uma tabela, os links — só dava por expressão
regular, e HTML não é regular. A marcação que funciona no teste quebra
no primeiro atributo fora de ordem, na primeira tag sem fechar, no
primeiro `<br>` no meio.

O parser é o `html.parser` do próprio Python: tolerante com HTML real,
que quase nunca é bem formado.

Três decisões
-------------
1. **O seletor é CSS, e não XPath.** `div.preco > span` é o que quem
   escreve HTML já sabe de cor. XPath é mais poderoso e ninguém lembra.

2. **`texto` junta com espaço, e não colado.** `<b>R$</b><span>10</span>`
   colado vira "R$10"; com espaço, "R$ 10". O segundo é o que a página
   mostra, e é o que quem extrai quer.

3. **`limpar` existe, e é o contrário de tudo isto.** Tirar marcação de
   um texto que veio de fora, antes de gravá-lo, é a defesa contra XSS
   que mais se esquece.
"""

import html as _html
import re
from html.parser import HTMLParser


class ErroDeHtml(Exception):
    pass


#: Tags que não fecham. Tratá-las como abertas empilha para sempre e o
#: documento inteiro vira filho de um `<br>`.
VAZIAS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
          "link", "meta", "param", "source", "track", "wbr"}


class No:
    """Um elemento: a tag, os atributos, os filhos."""

    __slots__ = ("tag", "atributos", "filhos", "pai", "_texto")

    def __init__(self, tag="", atributos=None, pai=None):
        self.tag = tag
        self.atributos = dict(atributos or {})
        self.filhos = []
        self.pai = pai
        self._texto = ""

    # ── ler ──

    @property
    def texto(self):
        """Todo o texto abaixo deste nó, junto com ESPAÇO.

        `<b>R$</b><span>10</span>` colado vira "R$10"; com espaço,
        "R$ 10" — que é o que a página mostra.
        """
        partes = []
        if self._texto.strip():
            partes.append(self._texto.strip())
        for filho in self.filhos:
            pedaco = filho.texto
            if pedaco:
                partes.append(pedaco)
        return " ".join(partes)

    @property
    def texto_cru(self):
        """Sem juntar: o texto exatamente como está."""
        return self._texto + "".join(f.texto_cru for f in self.filhos)

    def atributo(self, nome, padrao=None):
        return self.atributos.get(nome, padrao)

    @property
    def classes(self):
        return (self.atributos.get("class") or "").split()

    @property
    def id(self):
        return self.atributos.get("id", "")

    # ── procurar ──

    def achar(self, seletor):
        """O PRIMEIRO que casa, ou void."""
        achados = self.achar_todos(seletor, limite=1)
        return achados[0] if achados else None

    def achar_todos(self, seletor, limite=0):
        alvos = _compilar(seletor)
        saida = []
        for candidato in self.descendentes():
            if _casa_cadeia(candidato, alvos):
                saida.append(candidato)
                if limite and len(saida) >= limite:
                    break
        return saida

    def descendentes(self):
        for filho in self.filhos:
            if filho.tag:
                yield filho
            yield from filho.descendentes()

    def filhos_tag(self, tag=""):
        return [f for f in self.filhos if f.tag and (not tag or f.tag == tag)]

    def subir(self, tag=""):
        """O ancestral mais próximo com essa tag."""
        atual = self.pai
        while atual is not None:
            if not tag or atual.tag == tag:
                return atual
            atual = atual.pai
        return None

    # ── extrair ──

    def links(self, absolutos_de=""):
        saida = []
        for a in self.achar_todos("a"):
            destino = a.atributo("href", "")
            if not destino:
                continue
            if absolutos_de and not re.match(r"^[a-z]+:", destino):
                from urllib.parse import urljoin
                destino = urljoin(absolutos_de, destino)
            saida.append({"texto": a.texto, "destino": destino,
                          "titulo": a.atributo("title", "")})
        return saida

    def imagens(self):
        return [{"origem": i.atributo("src", ""),
                 "alternativo": i.atributo("alt", "")}
                for i in self.achar_todos("img")]

    def tabela(self, seletor="table"):
        """A primeira tabela, como `{cabecalho, linhas}`."""
        alvo = self.achar(seletor) if seletor else self
        if alvo is None:
            return None
        cabecalho = [c.texto for c in alvo.achar_todos("th")]
        linhas = []
        for tr in alvo.achar_todos("tr"):
            celulas = [td.texto for td in tr.filhos_tag("td")]
            if celulas:
                linhas.append(celulas)
        return {"cabecalho": cabecalho, "linhas": linhas}

    def como_vault(self):
        return {"tag": self.tag, "atributos": dict(self.atributos),
                "texto": self.texto,
                "filhos": [f.como_vault() for f in self.filhos if f.tag]}

    def __repr__(self):
        marca = f"#{self.id}" if self.id else ""
        classe = "." + ".".join(self.classes) if self.classes else ""
        return f"<{self.tag}{marca}{classe}>"


# ══════════════════════════════════════════════════════════════
#  Seletor CSS
# ══════════════════════════════════════════════════════════════

_PARTE = re.compile(
    r"(?P<tag>[\w-]+|\*)?"
    r"(?P<id>#[\w-]+)?"
    r"(?P<classes>(?:\.[\w-]+)*)"
    r"(?P<attr>(?:\[[^\]]+\])*)$")


def _compilar(seletor):
    """'div.preco > span' vira a cadeia de degraus, do fim para o começo."""
    texto = str(seletor).strip()
    if not texto:
        raise ErroDeHtml("o seletor está vazio")
    degraus = []
    for pedaco in re.split(r"\s*(>)\s*|\s+", texto):
        if not pedaco:
            continue
        if pedaco == ">":
            if not degraus:
                raise ErroDeHtml(f"o seletor '{seletor}' começa com '>'")
            degraus[-1]["direto"] = True
            continue
        casou = _PARTE.match(pedaco)
        if not casou:
            raise ErroDeHtml(
                f"não entendi '{pedaco}' em '{seletor}'.\n"
                f"  Aceito: tag, .classe, #id, [attr], [attr=valor] e '>'.")
        atributos = []
        for bruto in re.findall(r"\[([^\]]+)\]", casou.group("attr") or ""):
            chave, sinal, valor = bruto.partition("=")
            atributos.append((chave.strip(), valor.strip().strip("\"'")
                              if sinal else None))
        degraus.append({
            "tag": (casou.group("tag") or "").lower(),
            "id": (casou.group("id") or "")[1:],
            "classes": [c for c in (casou.group("classes") or "").split(".")
                        if c],
            "atributos": atributos,
            "direto": False,
        })
    return degraus


def _casa_um(no, degrau):
    if degrau["tag"] and degrau["tag"] != "*" and no.tag != degrau["tag"]:
        return False
    if degrau["id"] and no.id != degrau["id"]:
        return False
    if degrau["classes"] and not set(degrau["classes"]) <= set(no.classes):
        return False
    for chave, valor in degrau["atributos"]:
        if chave not in no.atributos:
            return False
        if valor is not None and no.atributos[chave] != valor:
            return False
    return True


def _casa_cadeia(no, degraus):
    if not _casa_um(no, degraus[-1]):
        return False
    atual = no
    for i in range(len(degraus) - 2, -1, -1):
        degrau = degraus[i]
        direto = degraus[i]["direto"]
        if direto:
            atual = atual.pai
            if atual is None or not _casa_um(atual, degrau):
                return False
            continue
        atual = atual.pai
        while atual is not None and not _casa_um(atual, degrau):
            atual = atual.pai
        if atual is None:
            return False
    return True


# ══════════════════════════════════════════════════════════════
#  O leitor
# ══════════════════════════════════════════════════════════════

class _Leitor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.raiz = No("[documento]")
        self.atual = self.raiz

    def handle_starttag(self, tag, atributos):
        no = No(tag, {k: (v or "") for k, v in atributos}, self.atual)
        self.atual.filhos.append(no)
        if tag not in VAZIAS:
            self.atual = no

    def handle_startendtag(self, tag, atributos):
        no = No(tag, {k: (v or "") for k, v in atributos}, self.atual)
        self.atual.filhos.append(no)

    def handle_endtag(self, tag):
        if tag in VAZIAS:
            return
        # Sobe até achar quem abriu. Uma tag fechada que ninguém abriu é
        # ignorada — HTML real está cheio delas, e derrubar a leitura
        # por isso não serve a ninguém.
        subindo = self.atual
        while subindo is not None and subindo.tag != tag:
            subindo = subindo.pai
        if subindo is not None and subindo.pai is not None:
            self.atual = subindo.pai

    def handle_data(self, dados):
        if dados.strip():
            texto = No("", None, self.atual)
            texto._texto = dados
            self.atual.filhos.append(texto)


def ler(fonte):
    """O HTML vira uma árvore."""
    leitor = _Leitor()
    try:
        leitor.feed(str(fonte))
        leitor.close()
    except Exception as erro:                        # noqa: BLE001
        raise ErroDeHtml(f"não consegui ler o HTML: {erro}") from None
    return leitor.raiz


def achar(fonte, seletor):
    return ler(fonte).achar(seletor)


def achar_todos(fonte, seletor):
    return ler(fonte).achar_todos(seletor)


def texto_de(fonte):
    return ler(fonte).texto


def links_de(fonte, base=""):
    return ler(fonte).links(base)


def tabela_de(fonte, seletor="table"):
    return ler(fonte).tabela(seletor)


# ══════════════════════════════════════════════════════════════
#  Escapar e limpar
# ══════════════════════════════════════════════════════════════

def escapar(texto):
    """Texto vira HTML seguro. A defesa contra XSS que mais se esquece."""
    return _html.escape(str(texto), quote=True)


def desescapar(texto):
    return _html.unescape(str(texto))


_SCRIPT = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
_TAG = re.compile(r"<[^>]+>")


def limpar(fonte):
    """Tira TODA a marcação, e o conteúdo de script e style junto.

    Um `limpar` que só tira as tags deixa o corpo do `<script>` como
    texto — e aí o "texto limpo" contém o código que se queria tirar.
    """
    sem_script = _SCRIPT.sub(" ", str(fonte))
    sem_tag = _TAG.sub(" ", sem_script)
    return re.sub(r"\s+", " ", _html.unescape(sem_tag)).strip()


PERMITIDAS = {"b", "i", "em", "strong", "p", "br", "ul", "ol", "li",
              "code", "pre", "blockquote", "h1", "h2", "h3", "a"}


def podar(fonte, permitidas=None, links_seguros=True):
    """Deixa só as tags permitidas. Para comentário e conteúdo de usuário.

    A lista é de PERMITIDAS, e não de proibidas: uma lista de proibidas
    esquece a próxima tag perigosa que o navegador inventar.
    """
    aceitas = set(permitidas or PERMITIDAS)
    sem_script = _SCRIPT.sub("", str(fonte))

    def trocar(casou):
        bruto = casou.group(0)
        nome = re.match(r"</?\s*([\w-]+)", bruto)
        if not nome or nome.group(1).lower() not in aceitas:
            return ""
        tag = nome.group(1).lower()
        if tag != "a":
            return f"</{tag}>" if bruto.startswith("</") else f"<{tag}>"
        if bruto.startswith("</"):
            return "</a>"
        destino = re.search(r'href\s*=\s*["\']([^"\']*)', bruto)
        alvo = destino.group(1) if destino else ""
        if links_seguros and not re.match(r"^(https?:|/|#)", alvo):
            # 'javascript:' num href é script com outro nome.
            return "<a>"
        return (f'<a href="{escapar(alvo)}" rel="noopener noreferrer">'
                if alvo else "<a>")

    return _TAG.sub(trocar, sem_script)


class ArcaneHtml:
    """O dicionário que `adopt Arcane.Html` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Html",

            "ler": ler,
            "achar": achar,
            "achar_todos": achar_todos,
            "texto_de": texto_de,
            "links_de": links_de,
            "tabela_de": tabela_de,

            "escapar": escapar,
            "desescapar": desescapar,
            "limpar": limpar,
            "podar": podar,

            "No": No,
        }
