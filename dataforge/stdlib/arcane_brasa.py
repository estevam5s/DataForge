# -*- coding: utf-8 -*-
"""Arcane.Brasa — o framework de aplicativos para o celular.

Um programa DataForge vira um aplicativo que o Android e o iPhone
instalam na tela inicial, abrem em tela cheia e usam sem conexão. Por
baixo, é a Vitrine — o programa roda no servidor, de cima para baixo,
e o estado sobrevive por sessão. A Brasa acrescenta o que faz um
painel virar um APLICATIVO:

    | Peça                        | O que resolve                                 |
    |-----------------------------|-----------------------------------------------|
    | barra de abas embaixo       | a navegação que o polegar alcança             |
    | topo com "voltar"           | a tela de detalhe, e o gesto de voltar        |
    | lista tocável               | a linha inteira é o alvo, com 56 px de altura |
    | botão flutuante             | a ação principal da tela                      |
    | PWA completo, embutido      | manifesto, service worker e ícones PNG        |
    | recursos do aparelho        | compartilhar, ligar, mapa, localização        |
    | a rede local                | `Br.rodar(app)` mostra o endereço do celular  |
    | a Sonda                     | toca, volta e confere — sem navegador         |

O que ela NÃO é — escrito aqui para ninguém inventar
----------------------------------------------------
**Não há APK nem app de loja.** O que a Brasa entrega é um PWA: uma
página que o sistema instala como aplicativo. Empacotar o interpretador
num APK exigiria python-for-android ou Chaquopy, e as duas trazem a
cadeia de dependências que esta linguagem não tem.

E duas regras do navegador, que não são desta linguagem:

- **Instalar exige HTTPS.** Pela rede local (`http://192.168…`) o
  aplicativo abre e funciona, mas o celular não oferece "instalar" nem
  roda o service worker. `localhost` é a exceção, para desenvolver.
- **A localização exige HTTPS** pelo mesmo motivo: fora dele,
  `navigator.geolocation` não existe.
"""

import html as _html
import json
import os
import socket
import struct
import unicodedata
import zlib

from ..errors import RuntimeError_

_DOC = "mobile"


def _erro(mensagem, nota="", dica=""):
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


def _V():
    from . import get_module
    return get_module("Arcane.Vitrine")


def _e(texto):
    return _html.escape(str(texto if texto is not None else ""), quote=True)


#: O que um destino de link pode ser. Um `javascript:` vindo de um dado
#: ('destino := "/p?id={id}"' com um id malicioso) viraria XSS — então
#: só caminho da própria aplicação e os esquemas que abrem um aplicativo
#: do aparelho.
_ESQUEMAS = ("tel:", "sms:", "mailto:", "geo:", "https:", "http:")


def _destino_seguro(destino):
    texto = str(destino or "").strip()
    if not texto:
        return ""
    if texto.startswith("/") and not texto.startswith("//"):
        return texto
    if texto.lower().startswith(_ESQUEMAS):
        return texto
    raise _erro(f"destino recusado: '{texto}'",
                nota="um link so pode ir para um caminho da aplicacao "
                     "('/produto?id=3') ou abrir tel:, sms:, mailto:, geo: e https:",
                dica='destino := "/produto?id={id}"')


def _campo(item, nome):
    from .arcane_collections import _campo_de
    return _campo_de(item, nome)


def _preencher(molde, item):
    """'/produto?id={id}' com os campos do item — e cada valor codificado."""
    from urllib.parse import quote
    saida, i = [], 0
    texto = str(molde)
    while i < len(texto):
        if texto[i] == "{":
            fim = texto.find("}", i)
            if fim < 0:
                raise _erro(f"molde sem '}}': {molde}")
            saida.append(quote(str(_campo(item, texto[i + 1:fim]) or ""), safe=""))
            i = fim + 1
        else:
            saida.append(texto[i])
            i += 1
    return "".join(saida)


# ═══════════════════════════════════════════════════════════
#  O registro do que a tela desenhou — é o que a Sonda lê
# ═══════════════════════════════════════════════════════════

def _anotar(tipo, **dados):
    """Guarda no contexto da execução o que foi desenhado, como DADO.

    O HTML da casca é cru; a Sonda não o analisa. Ela lê esta lista — e
    por isso 'tocar("café")' acha a linha pelo que o programa passou, e
    não por uma expressão regular sobre o HTML.
    """
    from .vitrine.nucleo import Contexto
    ctx = Contexto.atual()
    if ctx is None:
        raise _erro("componente da Brasa fora de uma tela",
                    dica="chame dentro da acao registrada com Br.tela(...)")
    if not hasattr(ctx, "brasa"):
        ctx.brasa = []
    ctx.brasa.append({"tipo": tipo, **dados})


def _por_html(conteudo):
    _V()["html"](conteudo)


# ═══════════════════════════════════════════════════════════
#  Os componentes
# ═══════════════════════════════════════════════════════════

def _svg(nome, tamanho=24):
    from .vitrine.conteudo import ICONES
    caminho = ICONES.get(str(nome))
    if caminho is None:
        # Um NOME que não existe é erro; um emoji é um ícone. Sem esta
        # separação, 'icone := "caixa"' desenhava a palavra "caixa" na
        # barra de abas, calado.
        if str(nome).isascii() and str(nome).replace("_", "").isalpha():
            import difflib
            perto = difflib.get_close_matches(str(nome), ICONES, n=3, cutoff=0.5)
            raise _erro(f"nao ha icone '{nome}'",
                        nota=("voce quis dizer: " + ", ".join(perto)) if perto
                        else f"ha {len(ICONES)}: V.icones() lista todos",
                        dica="um emoji tambem serve: icone := \"📦\"")
        return f'<span class="br-emoji" aria-hidden="true">{_e(nome)}</span>'
    return (f'<svg width="{tamanho}" height="{tamanho}" viewBox="0 0 24 24" '
            f'fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'<path d="{_e(caminho)}"/></svg>')


def topo(titulo, voltar=False, destino_voltar="/"):
    """O cabeçalho da tela. Com `voltar`, a seta que volta.

    A seta usa o histórico do navegador — é o que o gesto de voltar do
    Android faz —, e cai em `destino_voltar` quando não há para onde
    voltar (o aplicativo foi aberto direto nesta tela, por um link).
    """
    destino = _destino_seguro(destino_voltar) or "/"
    seta = (f'<a class="br-voltar" data-br="voltar" href="{_e(destino)}" '
            f'aria-label="Voltar">{_svg("esquerda")}</a>') if voltar else ""
    _anotar("topo", titulo=str(titulo), voltar=bool(voltar), destino=destino)
    _por_html(f'<header class="br-topo">{seta}<h1>{_e(titulo)}</h1></header>')
    return titulo


def secao(titulo):
    _anotar("secao", titulo=str(titulo))
    _por_html(f'<h2 class="br-secao">{_e(titulo)}</h2>')
    return titulo


def lista(itens, titulo="nome", detalhe="", destino="", icone=""):
    """Linhas tocáveis. Cada uma leva a `destino` com os campos do item.

        Br.lista(produtos, titulo := "nome", detalhe := "qtd",
                 destino := "/produto?id={id}")

    A linha INTEIRA é o alvo, com 56 px de altura: o dedo não acerta um
    link de 14 px no meio de um texto. Devolve quantas linhas desenhou.
    """
    partes = ['<ul class="br-lista">']
    for item in list(itens or []):
        rotulo = _campo(item, titulo) if isinstance(titulo, str) else str(item)
        extra = _campo(item, detalhe) if detalhe else ""
        alvo = _destino_seguro(_preencher(destino, item)) if destino else ""
        _anotar("item", titulo=str(rotulo if rotulo is not None else ""),
                detalhe=str(extra if extra is not None else ""), destino=alvo)
        miolo = (f'{_svg(icone, 22) if icone else ""}'
                 f'<span class="br-item-texto"><b>{_e(rotulo)}</b>'
                 + (f'<small>{_e(extra)}</small>' if detalhe else "")
                 + '</span>')
        if alvo:
            miolo += _svg("direita", 18)
            partes.append(f'<li><a class="br-item" href="{_e(alvo)}">{miolo}</a></li>')
        else:
            partes.append(f'<li><div class="br-item">{miolo}</div></li>')
    partes.append("</ul>")
    _por_html("".join(partes))
    return len(list(itens or []))


def vazio(mensagem, dica=""):
    """A tela sem dado. Uma lista vazia sem explicação parece travada."""
    _anotar("vazio", mensagem=str(mensagem))
    _por_html(f'<div class="br-vazio"><p>{_e(mensagem)}</p>'
          + (f'<small>{_e(dica)}</small>' if dica else "") + '</div>')
    return mensagem


def botao_flutuante(rotulo, destino, icone="mais"):
    """A ação principal da tela, no canto — acima da barra de abas."""
    alvo = _destino_seguro(destino)
    _anotar("flutuante", titulo=str(rotulo), destino=alvo)
    _por_html(f'<a class="br-fab" href="{_e(alvo)}" aria-label="{_e(rotulo)}">'
          f'{_svg(icone)}</a>')
    return rotulo


# ── o aparelho, pelo navegador ─────────────────────────────

def compartilhar(texto, rotulo="Compartilhar", url=""):
    """A folha de compartilhar do sistema (WhatsApp, e-mail…).

    Onde o navegador não a tem (a maioria dos computadores), o texto vai
    para a área de transferência — e o botão diz "Copiado".
    """
    _anotar("compartilhar", titulo=str(rotulo), texto=str(texto))
    _por_html(f'<button class="br-acao" data-br="compartilhar" '
          f'data-texto="{_e(texto)}" data-url="{_e(url)}">'
          f'{_svg("enviar", 20)}{_e(rotulo)}</button>')
    return rotulo


def ligar(numero, rotulo=""):
    so_digitos = "".join(c for c in str(numero) if c.isdigit() or c == "+")
    destino = f"tel:{so_digitos}"
    _anotar("ligar", titulo=str(rotulo or numero), destino=destino)
    _por_html(f'<a class="br-acao" href="{_e(destino)}">{_e(rotulo or numero)}</a>')
    return destino


def mapa(latitude, longitude, rotulo="Abrir no mapa"):
    """Abre o aplicativo de mapas do celular naquele ponto."""
    lat, lon = float(latitude), float(longitude)
    destino = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    _anotar("mapa", titulo=str(rotulo), destino=destino)
    _por_html(f'<a class="br-acao" href="{_e(destino)}" target="_blank" '
          f'rel="noopener">{_svg("mapa", 20)}{_e(rotulo)}</a>')
    return destino


def localizacao(rotulo="Usar minha localização"):
    """A posição do aparelho — `{lat, lon, precisao}` — ou `void`.

    O botão pede a posição ao navegador, que pergunta ao usuário; a
    resposta volta como parâmetro, e a tela roda de novo com ela. Ela
    fica guardada na sessão: a próxima tela não pede de novo.

    Exige HTTPS (ou `localhost`): fora dele, o navegador não oferece
    `navigator.geolocation`, e o botão diz isso em vez de ficar mudo.
    """
    V = _V()
    p = V["parametros"]()
    estado = V["estado"]
    if "__br_lat" in p and "__br_lon" in p:
        try:
            estado["__br_local"] = {"lat": float(p["__br_lat"]),
                                    "lon": float(p["__br_lon"]),
                                    "precisao": float(p.get("__br_prec", 0) or 0)}
        except ValueError:
            pass
    atual = estado["__br_local"] if "__br_local" in estado else None
    _anotar("localizacao", titulo=str(rotulo), valor=atual)
    _por_html(f'<button class="br-acao" data-br="local">{_svg("alvo", 20)}'
          f'{_e(rotulo)}</button>')
    return atual


# ═══════════════════════════════════════════════════════════
#  A aplicação
# ═══════════════════════════════════════════════════════════

def app(nome="DataForge", cor="#E8453C", icone="", descricao="", versao="1",
        fundo="#FFFFFF"):
    """Cria o aplicativo: uma aplicação Vitrine com a casca do celular.

    `cor` pinta a barra do sistema, o topo e o ícone; `icone` é um
    emoji ou o nome de um ícone da Vitrine; `versao` entra no nome do
    cache do service worker — suba-a a cada publicação, senão o celular
    continua servindo a versão antiga guardada.
    """
    cor = str(cor)
    if not (cor.startswith("#") and len(cor) in (4, 7)):
        raise _erro(f"cor invalida: '{cor}'", dica='cor := "#E8453C"')
    V = _V()
    aplicacao = V["app"](str(nome))
    aplicacao.config.update({
        "brasa": {"abas": [], "cor": cor, "icone": str(icone), "fundo": str(fundo),
                  "descricao": str(descricao), "versao": str(versao),
                  "nome": str(nome)},
        "viewport": "width=device-width,initial-scale=1,viewport-fit=cover",
        "css": _CSS.replace("__COR__", cor),
        "javascript": _JS,
        "cabeca": [
            '<link rel="manifest" href="/manifest.webmanifest">',
            f'<meta name="theme-color" content="{_e(cor)}">',
            '<meta name="mobile-web-app-capable" content="yes">',
            '<meta name="apple-mobile-web-app-capable" content="yes">',
            '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
            f'<meta name="apple-mobile-web-app-title" content="{_e(str(nome)[:12])}">',
            '<link rel="apple-touch-icon" href="/__brasa__/icone-192.png">',
            '<link rel="icon" type="image/png" href="/__brasa__/icone-192.png">',
        ],
    })
    if descricao:
        aplicacao.config["descricao"] = str(descricao)
    return aplicacao


def _config(aplicacao):
    brasa = getattr(aplicacao, "config", {}).get("brasa")
    if brasa is None:
        raise _erro("isto nao e um app da Brasa",
                    dica='app := Br.app("Nome")')
    return brasa


def tela(caminho, acao, titulo="", icone="", aba=False, aplicacao=None):
    """Registra uma tela. Com `aba`, ela aparece na barra de baixo.

    A barra de abas é desenhada pela Brasa DEPOIS da tela, em toda tela
    registrada — inclusive nas de detalhe, onde nenhuma aba fica acesa.
    """
    from .vitrine.api import _app
    aplicacao = aplicacao or _app()
    brasa = _config(aplicacao)
    caminho = str(caminho)
    if not caminho.startswith("/"):
        raise _erro(f"o caminho de uma tela comeca com '/': '{caminho}'")
    if aba:
        if len(brasa["abas"]) >= 5:
            raise _erro("a barra de abas ja tem 5",
                        nota="acima de cinco o rotulo nao cabe numa tela de "
                             "celular, e o Material e a Apple param em cinco",
                        dica="ponha as outras telas numa lista dentro de uma aba")
        _svg(icone or "casa")      # acusa o ícone errado AQUI, na linha que registra
        brasa["abas"].append({"caminho": caminho, "titulo": str(titulo or caminho),
                              "icone": str(icone or "casa")})

    def envolvida():
        from .vitrine.nucleo import Contexto
        ctx = Contexto.atual()
        if ctx is not None:
            ctx.brasa = []
        try:
            acao()
        finally:
            _desenhar_abas(aplicacao, caminho)

    envolvida.__name__ = getattr(acao, "name", "tela")
    envolvida.brasa_acao = acao
    _V()["pagina"](caminho, envolvida, str(titulo or ""))
    return caminho


def _desenhar_abas(aplicacao, atual):
    abas = _config(aplicacao)["abas"]
    if not abas:
        return
    partes = ['<nav class="br-abas" aria-label="Navegação">']
    for aba in abas:
        acesa = aba["caminho"] == atual
        _anotar("aba", titulo=aba["titulo"], destino=aba["caminho"], ativa=acesa)
        partes.append(
            f'<a href="{_e(aba["caminho"])}" class="br-aba{" br-acesa" if acesa else ""}"'
            + (' aria-current="page"' if acesa else "") + '>'
            f'{_svg(aba["icone"], 22)}<span>{_e(aba["titulo"])}</span></a>')
    partes.append("</nav>")
    _por_html("".join(partes))


# ═══════════════════════════════════════════════════════════
#  O PWA: manifesto, service worker e ícones
# ═══════════════════════════════════════════════════════════

def manifesto(aplicacao):
    brasa = _config(aplicacao)
    return {
        "id": "/",
        "name": brasa["nome"],
        "short_name": brasa["nome"][:12],
        "description": brasa["descricao"],
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": brasa["fundo"],
        "theme_color": brasa["cor"],
        "lang": "pt-BR",
        "icons": [
            {"src": "/__brasa__/icone-192.png", "sizes": "192x192",
             "type": "image/png", "purpose": "any"},
            {"src": "/__brasa__/icone-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "any"},
            # O maskable é SEPARADO: o Android recorta o ícone num círculo
            # ou numa gota, e um ícone arredondado recortado de novo fica
            # com a borda comida. Este preenche tudo e deixa a margem.
            {"src": "/__brasa__/icone-maskable-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
        ],
    }


def service_worker(aplicacao):
    """Rede primeiro, cache de reserva — e o cache leva a versão.

    Cache primeiro seria mais rápido, e faz um aplicativo mostrar dado
    velho sem avisar. Aqui a rede responde sempre que pode, e o que ela
    respondeu fica guardado para quando não puder. Só GET entra: uma
    ação (POST) repetida do cache seria um pedido duplicado.
    """
    versao = _config(aplicacao)["versao"]
    return _SW.replace("__VERSAO__", json.dumps(f"brasa-{versao}"))


# ── um PNG em Python puro ─────────────────────────────────

#: Um alfabeto 5x7, para a inicial do ícone. Cinco linhas de bits por
#: letra seriam ilegíveis de ler aqui; sete linhas de 5 caracteres não.
_FONTE = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
}


def _iniciais(nome):
    """'Estoque da Loja' -> 'EL'. Sem acento: 'Área' vira 'A'."""
    limpo = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode()
    palavras = [p for p in limpo.split() if p[:1].isalnum()]
    letras = "".join(p[0] for p in palavras[:2]).upper() or "A"
    return "".join(c for c in letras if c in _FONTE) or "A"


def _cor_rgb(cor):
    cor = cor.lstrip("#")
    if len(cor) == 3:
        cor = "".join(c * 2 for c in cor)
    return tuple(int(cor[i:i + 2], 16) for i in (0, 2, 4))


def icone_png(nome, cor="#E8453C", tamanho=192, maskable=False):
    """O ícone do aplicativo: a cor da marca e as iniciais em branco.

    PNG escrito à mão (cabeçalho, IDAT com zlib, CRC): a biblioteca
    padrão do Python não desenha imagem, e trazer o Pillow quebraria a
    promessa de zero dependência por um quadrado com duas letras.
    """
    n = int(tamanho)
    if not 48 <= n <= 1024:
        raise _erro(f"tamanho de icone fora da faixa: {n}", nota="de 48 a 1024 px")
    fundo = _cor_rgb(cor)
    raio = 0 if maskable else n * 0.22
    letras = _iniciais(nome)
    # A área segura do maskable é o círculo central de 80%: as letras
    # ficam dentro dela, e o recorte do sistema não as corta.
    escala = max(1, int(n * (0.28 if maskable else 0.34) / 7))
    largura_texto = len(letras) * 5 * escala + (len(letras) - 1) * escala
    x0 = (n - largura_texto) // 2
    y0 = (n - 7 * escala) // 2
    tinta = set()
    for k, letra in enumerate(letras):
        for lin, bits in enumerate(_FONTE[letra]):
            for col, bit in enumerate(bits):
                if bit == "1":
                    bx = x0 + k * 6 * escala + col * escala
                    by = y0 + lin * escala
                    for dy in range(escala):
                        for dx in range(escala):
                            tinta.add((bx + dx, by + dy))

    def dentro(x, y):
        if raio <= 0:
            return True
        cx = min(max(x, raio), n - 1 - raio)
        cy = min(max(y, raio), n - 1 - raio)
        return (x - cx) ** 2 + (y - cy) ** 2 <= raio ** 2

    linhas = bytearray()
    for y in range(n):
        linhas.append(0)
        for x in range(n):
            if not dentro(x, y):
                linhas += b"\x00\x00\x00\x00"
            elif (x, y) in tinta:
                linhas += b"\xff\xff\xff\xff"
            else:
                linhas += bytes(fundo) + b"\xff"

    def pedaco(tipo, dados):
        return (struct.pack(">I", len(dados)) + tipo + dados
                + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF))

    return (b"\x89PNG\r\n\x1a\n"
            + pedaco(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0))
            + pedaco(b"IDAT", zlib.compress(bytes(linhas), 9))
            + pedaco(b"IEND", b""))


# ═══════════════════════════════════════════════════════════
#  Servir
# ═══════════════════════════════════════════════════════════

def _montar(aplicacao):
    """O app Kiln da Vitrine, com as rotas do aplicativo acrescentadas."""
    kiln_app = aplicacao.montar()
    if kiln_app.config.get("brasa_rotas"):
        return kiln_app
    from .vitrine.runtime import _kiln
    K = _kiln()
    brasa = _config(aplicacao)
    icones = {}

    def resposta(corpo, tipo, extra=None):
        return {"__kiln__": True, "status": 200, "body": corpo,
                "content_type": tipo, "cookies": [],
                "headers": {"Cache-Control": "no-cache", **(extra or {})}}

    def icone(req, tamanho, maskable=False):
        chave = (tamanho, maskable)
        if chave not in icones:
            icones[chave] = icone_png(brasa["nome"], brasa["cor"], tamanho, maskable)
        return resposta(icones[chave], "image/png")

    K._get(kiln_app, "/manifest.webmanifest",
           lambda req: resposta(json.dumps(manifesto(aplicacao), ensure_ascii=False),
                                "application/manifest+json"))
    K._get(kiln_app, "/sw.js",
           lambda req: resposta(service_worker(aplicacao), "text/javascript",
                                {"Service-Worker-Allowed": "/"}))
    K._get(kiln_app, "/__brasa__/icone-192.png", lambda req: icone(req, 192))
    K._get(kiln_app, "/__brasa__/icone-512.png", lambda req: icone(req, 512))
    K._get(kiln_app, "/__brasa__/icone-maskable-512.png",
           lambda req: icone(req, 512, True))
    kiln_app.config["brasa_rotas"] = True
    return kiln_app


def enderecos_na_rede(porta):
    """Os endereços pelos quais o celular, na mesma rede, alcança o app.

    Descobre o IP da interface que sai para a rede sem mandar pacote
    nenhum: um socket UDP "conectado" só escolhe a rota.
    """
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ips.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return [f"http://{ip}:{int(porta)}" for ip in ips if not ip.startswith("127.")]


def rodar(aplicacao, porta=8600, rede=True):
    """Sobe o aplicativo. Com `rede`, o celular na mesma rede o alcança."""
    _config(aplicacao)
    porta = int(os.environ.get("BRASA_PORTA") or porta)
    host = "0.0.0.0" if rede else "127.0.0.1"
    _montar(aplicacao)
    print(f"  {_config(aplicacao)['nome']} no ar")
    print(f"  neste computador:  http://localhost:{porta}")
    if rede:
        for endereco in enderecos_na_rede(porta):
            print(f"  no celular:        {endereco}   (mesma rede Wi-Fi)")
        print("  para INSTALAR no celular, o endereco precisa ser HTTPS —")
        print("  pela rede local o app abre e funciona, mas nao oferece 'instalar'.")
    return aplicacao.subir(porta, host, silencioso=True)


def servir(aplicacao, porta=0):
    """Em segundo plano, para teste e para `conferir_pwa`. Devolve a porta."""
    _montar(aplicacao)
    return aplicacao.servir(porta, "127.0.0.1")


def conferir_pwa(aplicacao):
    """O que o Android exige para oferecer "instalar" — conferido SERVINDO.

    Não confere a configuração: sobe o aplicativo, pede cada arquivo por
    HTTP e olha o que chegou. Um manifesto certo servido com o tipo
    errado não instala, e só pedindo se descobre isso.
    """
    import urllib.request
    porta = servir(aplicacao)
    base = f"http://127.0.0.1:{porta}"

    def pedir(caminho):
        with urllib.request.urlopen(base + caminho, timeout=5) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()

    achados = []

    def conferir(item, ok, detalhe=""):
        achados.append({"item": item, "ok": bool(ok), "detalhe": detalhe})

    try:
        _st, _tipo, pagina = pedir("/")
        texto = pagina.decode("utf-8", "replace")
        conferir("a pagina liga o manifesto", 'rel="manifest"' in texto)
        conferir("a pagina declara a cor do sistema", 'name="theme-color"' in texto)
        conferir("a pagina registra o service worker",
                 "serviceWorker.register('/sw.js')" in texto)
        conferir("viewport para celular (viewport-fit=cover)", "viewport-fit=cover" in texto)

        st, tipo, corpo = pedir("/manifest.webmanifest")
        m = json.loads(corpo)
        conferir("manifesto servido como manifest+json", "manifest+json" in tipo, tipo)
        for campo in ("name", "short_name", "start_url", "display", "icons"):
            conferir(f"manifesto tem '{campo}'", bool(m.get(campo)))
        conferir("display standalone", m.get("display") == "standalone")

        tamanhos = {}
        for ic in m.get("icons", []):
            st, tipo, png = pedir(ic["src"])
            largura, altura = struct.unpack(">II", png[16:24]) if png[:8] == b"\x89PNG\r\n\x1a\n" else (0, 0)
            tamanhos[(ic.get("purpose"), ic["sizes"])] = (tipo, largura, altura)
        for proposito, medida in (("any", "192x192"), ("any", "512x512"),
                                  ("maskable", "512x512")):
            tipo, largura, altura = tamanhos.get((proposito, medida), ("", 0, 0))
            conferir(f"icone {medida} ({proposito}) em PNG do tamanho certo",
                     tipo == "image/png" and f"{largura}x{altura}" == medida,
                     f"{tipo} {largura}x{altura}")

        st, tipo, sw = pedir("/sw.js")
        conferir("service worker na raiz, como JavaScript", "javascript" in tipo, tipo)
        conferir("service worker trata 'fetch'", b"addEventListener('fetch'" in sw)
    finally:
        aplicacao.parar()
        aplicacao.app = None
    return achados


# ═══════════════════════════════════════════════════════════
#  A Sonda
# ═══════════════════════════════════════════════════════════

class Sonda:
    """Usa o aplicativo sem navegador: toca, volta e confere.

    Por baixo é a Sonda da Vitrine — a tela roda de verdade. O que a
    Brasa acrescenta é o que um dedo faz: tocar numa linha, numa aba ou
    no botão flutuante, e voltar.
    """

    def __init__(self, aplicacao, caminho="/"):
        _config(aplicacao)
        self.app = aplicacao
        self.v = _V()["testar"](aplicacao, str(caminho))
        self.historico = [str(caminho)]

    # ── o que a tela desenhou ───────────────────────────────

    def _desenhado(self, tipo=None):
        itens = getattr(self.v.ctx, "brasa", []) or []
        return [i for i in itens if tipo is None or i["tipo"] == tipo]

    def abas(self):
        return [{"titulo": a["titulo"], "ativa": a["ativa"]} for a in self._desenhado("aba")]

    def itens(self):
        return [{"titulo": i["titulo"], "detalhe": i["detalhe"]} for i in self._desenhado("item")]

    def titulo(self):
        topos = self._desenhado("topo")
        return topos[0]["titulo"] if topos else ""

    def caminho(self):
        return self.historico[-1]

    # ── agir ────────────────────────────────────────────────

    def ir(self, caminho):
        self.historico.append(str(caminho))
        self.v.ir_para(str(caminho))
        return self

    def tocar(self, rotulo):
        """Toca numa linha da lista, numa aba ou no botão flutuante."""
        for tipo in ("item", "aba", "flutuante"):
            for i in self._desenhado(tipo):
                if i["titulo"] == str(rotulo):
                    if not i.get("destino"):
                        raise _erro(f"'{rotulo}' nao leva a lugar nenhum",
                                    dica="Br.lista(..., destino := \"/x?id={id}\")")
                    if not i["destino"].startswith("/"):
                        raise _erro(f"'{rotulo}' abre outro aplicativo ({i['destino']})",
                                    nota="a Sonda nao sai do app")
                    return self.ir(i["destino"])
        tocaveis = [i["titulo"] for i in self._desenhado()
                    if i["tipo"] in ("item", "aba", "flutuante")]
        raise _erro(f"nao ha '{rotulo}' para tocar nesta tela",
                    nota=f"da para tocar em: {', '.join(tocaveis) or 'nada'}")

    def voltar(self):
        if len(self.historico) > 1:
            self.historico.pop()
            self.v.ir_para(self.historico[-1])
        return self

    def localizacao(self, latitude, longitude, precisao=10):
        """O que o navegador responderia depois de o usuário permitir."""
        from urllib.parse import urlencode
        base, _, consulta = self.caminho().partition("?")
        extra = urlencode({"__br_lat": latitude, "__br_lon": longitude,
                           "__br_prec": precisao})
        return self.ir(f"{base}?{consulta + '&' if consulta else ''}{extra}")

    # ── o resto é a Sonda da Vitrine ────────────────────────

    def clicar(self, rotulo):
        self.v.clicar(rotulo)
        return self

    def digitar(self, rotulo, valor):
        self.v.digitar(rotulo, valor)
        return self

    def texto(self):
        partes = [self.v.texto()]
        for i in self._desenhado():
            for campo in ("titulo", "detalhe", "mensagem"):
                if i.get(campo):
                    partes.append(str(i[campo]))
        return "\n".join(p for p in partes if p)

    def tem(self, texto):
        return str(texto) in self.texto()

    def html(self):
        return self.v.html()


def testar(aplicacao, caminho="/"):
    return Sonda(aplicacao, caminho)


# ═══════════════════════════════════════════════════════════
#  A casca: CSS, cliente e service worker
# ═══════════════════════════════════════════════════════════

_CSS = """
:root{--br-cor:__COR__}
body.v-app{padding-bottom:calc(72px + env(safe-area-inset-bottom));
  -webkit-tap-highlight-color:transparent}
.v-largura{max-width:640px;margin:0 auto;padding:0 16px}
input,select,textarea{font-size:16px!important}
button,.v-botao{min-height:44px}
.br-topo{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:8px;
  margin:0 -16px 12px;padding:calc(10px + env(safe-area-inset-top)) 16px 10px;
  background:var(--br-cor);color:#fff}
.br-topo h1{font-size:19px;margin:0;font-weight:650;line-height:1.3}
.br-voltar{display:inline-flex;width:40px;height:40px;align-items:center;
  justify-content:center;color:#fff;border-radius:50%;margin-left:-8px}
.br-voltar:active{background:rgba(255,255,255,.18)}
.br-secao{font-size:13px;letter-spacing:.04em;text-transform:uppercase;opacity:.7;
  margin:20px 0 6px}
.br-lista{list-style:none;margin:0 -16px;padding:0}
.br-lista li+li{border-top:1px solid rgba(127,127,127,.18)}
.br-item{display:flex;align-items:center;gap:12px;min-height:56px;padding:8px 16px;
  color:inherit;text-decoration:none}
a.br-item:active{background:rgba(127,127,127,.12)}
.br-item-texto{flex:1;display:flex;flex-direction:column;gap:2px;min-width:0}
.br-item-texto b{font-weight:560;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.br-item-texto small{opacity:.65}
.br-vazio{text-align:center;padding:48px 16px;opacity:.75}
.br-acao{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 16px;
  border-radius:12px;border:1px solid rgba(127,127,127,.3);background:transparent;
  color:inherit;font:inherit;text-decoration:none;margin:4px 8px 4px 0;cursor:pointer}
.br-fab{position:fixed;right:18px;bottom:calc(84px + env(safe-area-inset-bottom));
  width:56px;height:56px;border-radius:18px;background:var(--br-cor);color:#fff;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 8px 24px -8px rgba(0,0,0,.45);z-index:25}
.br-abas{position:fixed;left:0;right:0;bottom:0;z-index:30;display:flex;
  padding-bottom:env(safe-area-inset-bottom);background:var(--v-fundo,#fff);
  border-top:1px solid rgba(127,127,127,.2)}
.br-aba{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;
  padding:8px 0 6px;min-height:56px;font-size:11.5px;color:inherit;opacity:.6;
  text-decoration:none}
.br-aba.br-acesa{opacity:1;color:var(--br-cor);font-weight:600}
"""

_JS = """
(function(){
  if('serviceWorker' in navigator){
    navigator.serviceWorker.register('/sw.js').catch(function(){});
  }
  document.addEventListener('click',function(ev){
    var el=ev.target.closest('[data-br]'); if(!el) return;
    var tipo=el.getAttribute('data-br');
    if(tipo==='voltar'){
      ev.preventDefault();
      if(history.length>1){history.back();}else{location.href=el.getAttribute('href')||'/';}
    }else if(tipo==='compartilhar'){
      ev.preventDefault();
      var d={title:document.title,text:el.dataset.texto||'',url:el.dataset.url||location.href};
      if(navigator.share){navigator.share(d).catch(function(){});}
      else if(navigator.clipboard){
        navigator.clipboard.writeText([d.text,d.url].filter(Boolean).join(' '));
        el.lastChild.textContent=' Copiado';
      }
    }else if(tipo==='local'){
      ev.preventDefault();
      if(!navigator.geolocation){el.lastChild.textContent=' Precisa de HTTPS para localizar';return;}
      el.lastChild.textContent=' Localizando…';
      navigator.geolocation.getCurrentPosition(function(p){
        var u=new URL(location.href);
        u.searchParams.set('__br_lat',p.coords.latitude.toFixed(6));
        u.searchParams.set('__br_lon',p.coords.longitude.toFixed(6));
        u.searchParams.set('__br_prec',Math.round(p.coords.accuracy));
        location.href=u.toString();
      },function(e){
        el.lastChild.textContent=e.code===1?' Permissão negada':' Não consegui localizar';
      },{enableHighAccuracy:true,timeout:15000});
    }
  });
})();
"""

_SW = """
const CACHE = __VERSAO__;
self.addEventListener('install', function (e) { self.skipWaiting(); });
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (nomes) {
    return Promise.all(nomes.filter(function (n) { return n !== CACHE; })
                            .map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  e.respondWith(fetch(e.request).then(function (r) {
    if (r.ok) { var copia = r.clone(); caches.open(CACHE).then(function (c) { c.put(e.request, copia); }); }
    return r;
  }).catch(function () {
    return caches.match(e.request).then(function (r) {
      return r || new Response(
        '<meta name="viewport" content="width=device-width"><body style="font:16px system-ui;padding:40px;text-align:center">' +
        '<h1>Sem conexão</h1><p>Esta tela ainda não foi aberta com internet.</p></body>',
        { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
    });
  }));
});
"""


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

class ArcaneBrasa(dict):
    """O dicionário que `adopt Arcane.Brasa` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Brasa",
            "app": app,
            "tela": tela,
            "rodar": rodar,
            "servir": servir,
            "testar": testar,
            "conferir_pwa": conferir_pwa,
            "manifesto": manifesto,
            "icone_png": icone_png,
            "enderecos_na_rede": enderecos_na_rede,
            # componentes
            "topo": topo,
            "secao": secao,
            "lista": lista,
            "vazio": vazio,
            "botao_flutuante": botao_flutuante,
            "compartilhar": compartilhar,
            "ligar": ligar,
            "mapa": mapa,
            "localizacao": localizacao,
            "Sonda": Sonda,
        }
