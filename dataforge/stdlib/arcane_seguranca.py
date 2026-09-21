# -*- coding: utf-8 -*-
"""Arcane.Seguranca — o que se faz com a entrada de fora.

    adopt Arcane.Seguranca as Seg

    Seg.escapar_html(comentario)          // antes de por numa pagina
    Seg.caminho_seguro("uploads/", nome)  // antes de abrir
    Seg.url_segura(webhook)               // antes de chamar
    Seg.exigir_sem_segredo(fonte)         // antes de commitar

─── A divisao de trabalho, e por que ela existe ────────────

`Arcane.Crypto` tem as PRIMITIVAS: resumo, HMAC, senha derivada,
aleatorio de verdade, ChaCha20-Poly1305, JWT. Este modulo nao
reimplementa nenhuma delas — ele as chama. Duas implementacoes da
mesma conta divergem, e no dia em que divergirem sera a de seguranca
que estara errada.

O `Kiln` tem `csrf`, `rate_limit`, `secure_headers` e `body_limit`:
sao **middleware**, presos ao ciclo de um pedido HTTP. Este modulo e
para o resto do programa — o script que grava um CSV, o bot que abre
um arquivo, o comando que monta uma linha de shell. Foi ali que a
linguagem nao tinha resposta.

─── As cinco perguntas que ele responde ────────────────────

1. **Para onde este texto vai?** Escapar e por destino, nunca "em
   geral": o que protege uma pagina HTML nao protege uma linha de
   shell, e o que protege shell estraga um CSV. Sao doze destinos, e
   cada um tem a sua funcao.

2. **Quem e esta pessoa, de novo?** TOTP (RFC 6238), os codigos de
   recuperacao, e o token assinado com prazo — o link de confirmar
   e-mail e o de trocar senha sao o mesmo mecanismo.

3. **Ha segredo aqui?** A varredura acha por FORMATO — `ghp_`, `sk_`,
   `AKIA`, bloco de chave privada, e o valor de alta entropia sem
   nome conhecido. Ela acha o que voce esqueceu, que e o unico tipo
   que importa.

4. **Esta entrada pede o que pode?** Caminho que sai da pasta, URL
   que aponta para a rede interna, redirecionamento para fora do
   site, JSON fundo demais. Todos recusados pelo mesmo erro.

5. **O que aconteceu, e da para provar?** A trilha encadeia o resumo
   do registro anterior em cada registro: apagar ou editar um deles
   quebra a cadeia, e `conferir()` diz em qual linha.

─── O que ele NAO faz, e o motivo ──────────────────────────

**Nao ha TLS nem certificado aqui.** Isso e do `ssl` do Python e de
quem esta na frente do servidor (nginx, Caddy); uma camada propria
seria um subconjunto pior de algo que ja existe e ja e auditado.

**Nao ha Argon2.** O `hashlib` do Python tem `scrypt` e `pbkdf2`, e e
neles que `Crypto.hash_password` se apoia. Um Argon2 escrito em
Python puro seria lento o bastante para ter de rodar com parametros
fracos — o que o torna PIOR que o scrypt, e nao melhor.

**`vazada` fala com a rede, e isso esta no nome da funcao.** Ela
manda os **cinco primeiros** caracteres do SHA-1 da senha, nunca a
senha: e o k-anonimato do Have I Been Pwned. Ainda assim e uma
chamada externa, e por isso nao acontece dentro de `exigir_politica`
sem que alguem peca.

─── O segredo que se recusa a aparecer ─────────────────────

    chave := Seg.segredo(OS.env("STRIPE_KEY"))
    out chave                     // ***
    out $"usando {chave}"         // usando ***
    cobrar(chave.revelar())       // aqui, e so aqui

Um segredo vaza em log muito mais do que em commit, e vaza pelo
caminho mais inocente que existe: alguem imprime o vault inteiro para
depurar. `Segredo` e opaco para texto, para interpolacao e para
serializacao — o valor so sai por `revelar()`, que e uma linha
visivel na revisao de codigo.
"""

import base64
import binascii
import hashlib
import hmac
import ipaddress
import json
import math
import os
import re
import shlex
import socket
import struct
import threading
import time
import unicodedata
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from ..builtins import _df_type as _nome_do_tipo
from .opcoes import ler as _ler_opcoes

_DOC = "seguranca"


def _erro(mensagem, nota="", dica="", classe="SecurityError"):
    """O erro da familia DF19xx, pelo nome que o catalogo registra."""
    from .. import errors

    alvo = errors.erro_por_nome(classe) or errors.RuntimeError_
    return alvo(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


def _opcoes(opcoes, padroes, onde):
    """Valida com 'opcoes.ler' e aplica os padroes, do MESMO vault.

    'ler' recusa a chave desconhecida e nao aplica padrao, para nao
    haver dois lugares onde o padrao mora. Aqui ha um so: o vault de
    modulo que tambem serve de lista de conhecidas.
    """
    escolhido = dict(padroes)
    escolhido.update(_ler_opcoes(opcoes, padroes, onde))
    return escolhido


def _texto(valor, onde):
    """Aceita texto; recusa o resto pelo nome DataForge do tipo."""
    if isinstance(valor, str):
        return valor
    if isinstance(valor, (bytes, bytearray)):
        return bytes(valor).decode("utf-8", "replace")
    raise _erro(
        f"'{onde}' espera um texto, e recebeu um {_nome_do_tipo(valor)}.",
        dica="Converta com 'text(valor)' antes de passar.",
        classe="UnsafeInputError",
    )


def _bytes(valor, onde):
    """Texto vira UTF-8; Bytes passa."""
    if isinstance(valor, (bytes, bytearray)):
        return bytes(valor)
    if isinstance(valor, str):
        return valor.encode("utf-8")
    raise _erro(
        f"'{onde}' espera texto ou bytes, e recebeu um {_nome_do_tipo(valor)}.",
        classe="UnsafeInputError",
    )


# ═══════════════════════════════════════════════════════════
#  1. Escapar — e o destino decide qual
# ═══════════════════════════════════════════════════════════

_HTML = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#x27;"}


def _escapar_html(texto):
    t = _texto(texto, "escapar_html")
    return "".join(_HTML.get(c, c) for c in t)


def _escapar_atributo(texto):
    """Mais duro que o de corpo: um atributo sem aspas termina no espaco.

    `<a href=x onclick=mau()>` nao tem aspas nenhuma, e ali o espaco e
    o fim do valor. Escapar so `<`, `>` e `&` — o suficiente no corpo
    — deixa esse caso inteiro passar.
    """
    t = _texto(texto, "escapar_atributo")
    saida = []
    for c in t:
        if c.isalnum() or c in "-_.":
            saida.append(c)
        else:
            saida.append(f"&#x{ord(c):X};")
    return "".join(saida)


def _escapar_js(texto):
    """Para um valor que vai DENTRO de um <script>.

    O caso que pega todo mundo e `</script>` no meio de uma string: o
    navegador fecha a tag antes de o JavaScript ser lido, e o resto da
    pagina vira codigo. Escapar aspas nao resolve isso.
    """
    t = _texto(texto, "escapar_js")
    saida = []
    for c in t:
        o = ord(c)
        if c.isalnum() and o < 128:
            saida.append(c)
        elif o < 0x10000:
            saida.append(f"\\u{o:04x}")
        else:
            o -= 0x10000
            saida.append(f"\\u{0xD800 + (o >> 10):04x}\\u{0xDC00 + (o & 0x3FF):04x}")
    return "".join(saida)


def _escapar_url(texto):
    t = _texto(texto, "escapar_url")
    return urllib.parse.quote(t, safe="")


def _escapar_shell(texto):
    """`shlex.quote`. E a resposta certa so quando o argumento e DADO.

    Montar `sh -c "comando " + argumento` e perigoso mesmo escapando,
    porque o proprio comando veio de texto. A forma segura e passar a
    lista de argumentos ao sistema, sem shell no meio — e e isso que
    'Arcane.OS.run' faz.
    """
    return shlex.quote(_texto(texto, "escapar_shell"))


def _escapar_sql_like(texto, escape="\\"):
    """So o `%` e o `_` de um LIKE. NAO e defesa contra injecao.

    O valor continua tendo de ir por parametro. Isto existe para que
    uma busca por "50%" nao vire uma busca por "50 seguido de
    qualquer coisa" — que e um bug de resultado, nao de seguranca.
    """
    t = _texto(texto, "escapar_sql_like")
    e = _texto(escape, "escapar_sql_like")
    return t.replace(e, e + e).replace("%", e + "%").replace("_", e + "_")


def _escapar_csv(valor):
    """Injecao de formula: uma celula que comeca com '=' e codigo.

    O Excel e o Sheets executam `=`, `+`, `-`, `@` e as duas tabulacoes
    no inicio da celula. Um nome de usuario `=HYPERLINK(...)` vira um
    link ativo na planilha de quem exportou — e nada no CSV denuncia.
    """
    t = valor if isinstance(valor, str) else str(valor)
    if t[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + t
    return t


def _escapar_regex(texto):
    return re.escape(_texto(texto, "escapar_regex"))


def _escapar_cabecalho(texto):
    """CRLF num cabecalho HTTP injeta outro cabecalho, ou um corpo.

    Um `Location:` montado com valor de fora e o caminho classico: um
    `\\r\\n` no meio acrescenta `Set-Cookie`. Aqui os dois somem, e o
    resultado nunca tem quebra de linha.
    """
    t = _texto(texto, "escapar_cabecalho")
    return "".join(c for c in t if c not in "\r\n\x00")


def _escapar_log(texto):
    """Para o log NAO poder ser forjado.

    Quem escreve `\\n2026-01-01 INFO login ok` num campo de usuario
    acrescenta uma linha inteira ao log — e a investigacao seguinte le
    um evento que nunca aconteceu. Aqui a quebra vira texto visivel.
    """
    t = _texto(texto, "escapar_log")
    saida = []
    for c in t:
        if c == "\n":
            saida.append("\\n")
        elif c == "\r":
            saida.append("\\r")
        elif c == "\t":
            saida.append("\\t")
        elif ord(c) < 0x20 or ord(c) == 0x7F:
            saida.append(f"\\x{ord(c):02x}")
        else:
            saida.append(c)
    return "".join(saida)


def _sem_controle(texto, permitir_quebra=False):
    """Tira caracteres de controle e os invisiveis que enganam o olho.

    Inclui os de direcao de escrita (U+202E e familia), que invertem a
    ordem do que se le sem mudar o que o computador executa. E como
    `relatorio_exe.txt` aparece na tela sendo `relatorio_txt.exe`.
    """
    t = _texto(texto, "sem_controle")
    t = unicodedata.normalize("NFC", t)
    saida = []
    for c in t:
        if c in "\n\r\t" and permitir_quebra:
            saida.append(c)
            continue
        cat = unicodedata.category(c)
        if cat in ("Cc", "Cf", "Co", "Cs", "Cn"):
            continue
        saida.append(c)
    return "".join(saida)


_TAGS_PADRAO = ["b", "i", "em", "strong", "u", "p", "br", "ul", "ol", "li",
                "code", "pre", "blockquote", "a", "h1", "h2", "h3", "span"]
_ATRIBUTOS_PADRAO = {"a": ["href", "title"], "span": ["class"]}
_ESQUEMAS_PADRAO = ["http", "https", "mailto"]
_MUDAS = {"script", "style", "iframe", "object", "embed", "template"}


class _Limpador(HTMLParser):
    """Lista de PERMITIDOS, nunca de proibidos.

    Uma lista de proibidos e uma aposta de que se pensou em tudo, e a
    historia do XSS e a lista dos que nao pensaram: `<svg onload>`,
    `<math>`, `javascript:` com tabulacao no meio, entidade HTML
    dentro do atributo. A lista de permitidos erra para o lado de
    perder uma tag legitima, que e um bug visivel.
    """

    def __init__(self, tags, atributos, esquemas):
        super().__init__(convert_charrefs=True)
        self.tags = set(tags)
        self.atributos = {k: set(v) for k, v in atributos.items()}
        self.esquemas = set(esquemas)
        self.saida = []
        self.abertas = []
        self.mudo = 0

    def _atributo_ok(self, tag, nome, valor):
        if nome not in self.atributos.get(tag, ()):
            return None
        if valor is None:
            return ""
        v = _sem_controle(valor).strip()
        if nome in ("href", "src", "action"):
            esquema = v.split(":", 1)[0].lower() if ":" in v.split("?", 1)[0] else ""
            if esquema and esquema not in self.esquemas:
                return None
            if not esquema and v.startswith("//"):
                return None
        return v

    def handle_starttag(self, tag, attrs):
        if tag in _MUDAS:
            # O TEXTO de um <script> tambem sai. Deixar 'mau()' como
            # texto visivel nao e perigoso, e e confuso: quem le o
            # resultado acha que o filtro deixou codigo passar.
            self.mudo += 1
            return
        if tag not in self.tags:
            return
        pedacos = [tag]
        for nome, valor in attrs:
            ok = self._atributo_ok(tag, nome, valor)
            if ok is None:
                continue
            pedacos.append(f'{nome}="{_escapar_atributo(ok)}"')
        self.saida.append("<" + " ".join(pedacos) + ">")
        if tag not in ("br", "hr", "img"):
            self.abertas.append(tag)

    def handle_endtag(self, tag):
        if tag in _MUDAS:
            self.mudo = max(0, self.mudo - 1)
            return
        if tag in self.tags and tag in self.abertas:
            while self.abertas:
                aberta = self.abertas.pop()
                self.saida.append(f"</{aberta}>")
                if aberta == tag:
                    break

    def handle_data(self, dado):
        if self.mudo:
            return
        self.saida.append(_escapar_html(dado))

    def resultado(self):
        while self.abertas:
            self.saida.append(f"</{self.abertas.pop()}>")
        return "".join(self.saida)


_LIMPAR = {"tags": _TAGS_PADRAO, "atributos": _ATRIBUTOS_PADRAO,
           "esquemas": _ESQUEMAS_PADRAO}


def _limpar_html(texto, opcoes=None):
    """Deixa a formatacao e tira o que executa.

    Para um comentario ou uma descricao em que negrito e link sao
    desejados. Quando nao forem, `escapar_html` e a resposta — e e a
    resposta certa em quase todo lugar.
    """
    t = _texto(texto, "limpar_html")
    o = _opcoes(opcoes, _LIMPAR, "Seguranca.limpar_html")
    p = _Limpador(o["tags"], o["atributos"], o["esquemas"])
    p.feed(t)
    p.close()
    return p.resultado()


# ═══════════════════════════════════════════════════════════
#  2. Senha — e o motivo junto da recusa
# ═══════════════════════════════════════════════════════════

_PIORES = {
    "123456", "password", "123456789", "12345678", "12345", "qwerty",
    "abc123", "senha", "111111", "123123", "admin", "letmein", "welcome",
    "monkey", "1234567890", "senha123", "mudar123", "iloveyou", "sunshine",
    "princess", "dragon", "football", "master", "hello", "freedom",
    "whatever", "qazwsx", "trustno1", "1q2w3e4r", "654321", "batman",
}

_POLITICA = {"minimo": 12, "maiuscula": True, "minuscula": True,
             "numero": True, "simbolo": True, "entropia": 50.0,
             "proibir_comuns": True, "proibidas": []}


def _entropia(texto):
    """Shannon, em bits por caractere vezes o tamanho.

    E uma medida do TEXTO, nao de como ele foi escolhido: 'abababab'
    tem entropia baixa e 'correcthorse' tem alta, e as duas sao ruins
    por motivos diferentes. Por isso ela e um dos criterios, e nunca o
    unico.
    """
    t = _texto(texto, "entropia")
    if not t:
        return 0.0
    contagem = {}
    for c in t:
        contagem[c] = contagem.get(c, 0) + 1
    n = len(t)
    bits = -sum((q / n) * math.log2(q / n) for q in contagem.values())
    return round(bits * n, 2)


def _variedade(senha):
    return {
        "maiuscula": any(c.isupper() for c in senha),
        "minuscula": any(c.islower() for c in senha),
        "numero": any(c.isdigit() for c in senha),
        "simbolo": any(not c.isalnum() for c in senha),
    }


def _sequencial(senha):
    """'abcdef' e '123456' passam em variedade e nao valem nada."""
    baixa = senha.lower()
    corridas = 1
    maior = 1
    for a, b in zip(baixa, baixa[1:]):
        if ord(b) - ord(a) in (1, -1):
            corridas += 1
            maior = max(maior, corridas)
        else:
            corridas = 1
    return maior


def _repetida(senha):
    baixa = senha.lower()
    maior = 1
    corridas = 1
    for a, b in zip(baixa, baixa[1:]):
        corridas = corridas + 1 if a == b else 1
        maior = max(maior, corridas)
    return maior


def _forca_da_senha(senha):
    """Uma nota de 0 a 100, e a LISTA do que esta faltando.

    A nota sozinha e inutil numa tela: 'fraca' nao diz o que fazer. O
    que a pessoa usa e 'problemas', e e por isso que ela existe.
    """
    s = _texto(senha, "forca_da_senha")
    v = _variedade(s)
    bits = _entropia(s)
    problemas = []

    if len(s) < 8:
        problemas.append("tem menos de 8 caracteres")
    elif len(s) < 12:
        problemas.append("tem menos de 12 caracteres")
    for nome, rotulo in (("maiuscula", "letra maiuscula"),
                         ("minuscula", "letra minuscula"),
                         ("numero", "numero"), ("simbolo", "simbolo")):
        if not v[nome]:
            problemas.append(f"nao tem {rotulo}")
    if s.lower() in _PIORES:
        problemas.append("esta entre as senhas mais usadas do mundo")
    if _sequencial(s) >= 4:
        problemas.append("tem uma sequencia de teclado ou de alfabeto")
    if _repetida(s) >= 4:
        problemas.append("tem um caractere repetido quatro vezes ou mais")

    nota = min(100, int(bits * 1.1)) - len(problemas) * 12
    nota = max(0, min(100, nota))
    if s.lower() in _PIORES:
        nota = 0
    rotulo = ("muito fraca" if nota < 25 else "fraca" if nota < 45
              else "razoavel" if nota < 65 else "boa" if nota < 85
              else "forte")

    return {"nota": nota, "rotulo": rotulo, "entropia": bits,
            "tamanho": len(s), "problemas": problemas,
            "maiuscula": v["maiuscula"], "minuscula": v["minuscula"],
            "numero": v["numero"], "simbolo": v["simbolo"],
            "comum": s.lower() in _PIORES}


def _politica(senha, opcoes=None):
    """Confere e DEVOLVE o resultado — nao levanta."""
    s = _texto(senha, "politica")
    o = _opcoes(opcoes, _POLITICA, "Seguranca.politica")
    v = _variedade(s)
    faltando = []

    if len(s) < o["minimo"]:
        faltando.append(f"precisa de pelo menos {o['minimo']} caracteres")
    for chave, rotulo in (("maiuscula", "uma letra maiuscula"),
                          ("minuscula", "uma letra minuscula"),
                          ("numero", "um numero"), ("simbolo", "um simbolo")):
        if o[chave] and not v[chave]:
            faltando.append(f"precisa de {rotulo}")
    bits = _entropia(s)
    if o["entropia"] and bits < o["entropia"]:
        faltando.append(f"precisa de mais variedade ({bits:.0f} de {o['entropia']:.0f} bits)")
    if o["proibir_comuns"] and s.lower() in _PIORES:
        faltando.append("esta entre as senhas mais usadas do mundo")
    for proibida in o["proibidas"] or []:
        if proibida and proibida.lower() in s.lower():
            faltando.append(f"nao pode conter '{proibida}'")

    return {"ok": not faltando, "faltando": faltando, "entropia": bits}


def _exigir_politica(senha, opcoes=None):
    """O mesmo, levantando — para quem escreve o caminho feliz.

    A lista do que falta vai em 'e.nota', e nao so na mensagem: uma
    tela de cadastro mostra os itens um a um, e concatenar tudo numa
    frase obriga quem escreve a separar de novo.
    """
    r = _politica(senha, opcoes)
    if not r["ok"]:
        raise _erro(
            "A senha nao atende a politica.",
            nota="; ".join(r["faltando"]),
            dica="Mostre 'e.nota' ao usuario: ela diz o que falta.",
            classe="PolicyError",
        )
    return True


def _prefixo_vazamento(senha):
    """Os 5 primeiros do SHA-1, que e o unico que sai da maquina."""
    s = _texto(senha, "prefixo_vazamento")
    resumo = hashlib.sha1(s.encode("utf-8")).hexdigest().upper()
    return {"prefixo": resumo[:5], "resto": resumo[5:]}


def _conferir_vazamento(senha, respostas):
    """Offline: confere contra o que o servico ja devolveu.

    Separada de 'vazada' de proposito. Assim da para conferir mil
    senhas com uma consulta por prefixo, e para testar sem rede.
    """
    p = _prefixo_vazamento(senha)
    linhas = respostas if isinstance(respostas, (list, tuple)) else str(respostas).splitlines()
    for linha in linhas:
        texto = linha if isinstance(linha, str) else str(linha)
        if ":" not in texto:
            continue
        sufixo, contagem = texto.strip().split(":", 1)
        if hmac.compare_digest(sufixo.strip().upper(), p["resto"]):
            try:
                return int(contagem.strip().replace(",", ""))
            except ValueError:
                return 1
    return 0


def _vazada(senha, tempo_limite=5.0):
    """Pergunta ao Have I Been Pwned, mandando 5 caracteres.

    O k-anonimato: o servico recebe o prefixo do SHA-1 e devolve todos
    os resumos que comecam com ele — centenas. A senha nunca sai, e o
    servico nao tem como saber qual das centenas era a sua.

    E uma chamada de rede, e o nome diz isso. Ela devolve **-1**, e
    nao levanta, quando a rede falha: uma politica de senha que para
    de funcionar porque um servico de terceiro caiu impede cadastro
    por um motivo que nao e de seguranca.
    """
    p = _prefixo_vazamento(senha)
    url = f"https://api.pwnedpasswords.com/range/{p['prefixo']}"
    try:
        pedido = urllib.request.Request(
            url, headers={"User-Agent": "DataForge-Seguranca",
                          "Add-Padding": "true"})
        with urllib.request.urlopen(pedido, timeout=float(tempo_limite)) as r:
            corpo = r.read().decode("utf-8", "replace")
    except Exception:
        return -1
    return _conferir_vazamento(senha, corpo)


# ═══════════════════════════════════════════════════════════
#  3. Segundo fator — TOTP (RFC 6238) e HOTP (RFC 4226)
# ═══════════════════════════════════════════════════════════

_ALGORITMOS_OTP = {"sha1": hashlib.sha1, "sha256": hashlib.sha256,
                   "sha512": hashlib.sha512}


def _base32(dados):
    return base64.b32encode(dados).decode("ascii").rstrip("=")


def _de_base32(segredo, onde):
    s = _texto(segredo, onde).replace(" ", "").upper()
    s += "=" * (-len(s) % 8)
    try:
        return base64.b32decode(s, casefold=True)
    except (binascii.Error, ValueError):
        raise _erro(
            "O segredo TOTP nao e base32 valido.",
            nota="Um segredo de autenticador usa A-Z e 2-7, sem 0, 1 e 8.",
            dica="Gere um com 'Seg.totp_segredo()'.",
            classe="UnsafeInputError",
        )


def _totp_segredo(bytes_=20):
    """20 bytes — o que o RFC 4226 recomenda, e o que o Google Authenticator usa."""
    return _base32(os.urandom(int(bytes_)))


def _hotp(segredo, contador, digitos=6, algoritmo="sha1"):
    """O contador vira codigo. E a base do TOTP, e serve sozinha."""
    chave = _de_base32(segredo, "hotp")
    alg = _ALGORITMOS_OTP.get(str(algoritmo).lower())
    if alg is None:
        raise _erro(
            f"Algoritmo '{algoritmo}' nao existe para OTP.",
            nota="Ha: " + ", ".join(sorted(_ALGORITMOS_OTP)),
            classe="UnsafeInputError",
        )
    bloco = struct.pack(">Q", int(contador))
    mac = hmac.new(chave, bloco, alg).digest()
    desloca = mac[-1] & 0x0F
    numero = struct.unpack(">I", mac[desloca:desloca + 4])[0] & 0x7FFFFFFF
    d = int(digitos)
    return str(numero % (10 ** d)).zfill(d)


def _totp_agora(segredo, janela=30, digitos=6, algoritmo="sha1", quando=None):
    agora = time.time() if quando is None else float(quando)
    return _hotp(segredo, int(agora // int(janela)), digitos, algoritmo)


def _totp_conferir(segredo, codigo, janela=30, digitos=6, algoritmo="sha1",
                   tolerancia=1, quando=None):
    """Confere, aceitando a janela anterior e a seguinte.

    A tolerancia nao e frouxidao: o relogio do telefone anda alguns
    segundos fora, e um codigo digitado no segundo 29 chega no 31. Sem
    ela, uma fracao real dos logins legitimos falha — e o usuario
    aprende a desligar o segundo fator.

    A comparacao e em tempo constante. Comparar codigo com '==' vaza,
    pelo tempo, quantos digitos iniciais estavam certos.
    """
    c = _texto(codigo, "totp_conferir").strip().replace(" ", "")
    agora = time.time() if quando is None else float(quando)
    passo = int(agora // int(janela))
    t = int(tolerancia)
    for desvio in range(-t, t + 1):
        esperado = _hotp(segredo, passo + desvio, digitos, algoritmo)
        if hmac.compare_digest(esperado, c):
            return True
    return False


def _totp_uri(segredo, conta, emissor="", digitos=6, janela=30, algoritmo="sha1"):
    """O `otpauth://` que vira QR code no autenticador."""
    rotulo = f"{emissor}:{conta}" if emissor else str(conta)
    p = {"secret": _texto(segredo, "totp_uri").replace(" ", "").upper(),
         "digits": str(int(digitos)), "period": str(int(janela)),
         "algorithm": str(algoritmo).upper()}
    if emissor:
        p["issuer"] = emissor
    return ("otpauth://totp/" + urllib.parse.quote(rotulo, safe="")
            + "?" + urllib.parse.urlencode(p))


def _codigos_de_recuperacao(quantos=10, grupos=3, tamanho=4):
    """O que salva quem perdeu o telefone.

    Devolve os codigos em claro **e** o resumo de cada um. O sistema
    guarda so os resumos; os codigos vao para a pessoa uma unica vez.
    Guardar o codigo em claro no banco desfaz o motivo de ele existir.
    """
    alfabeto = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sem O/0, I/1
    codigos = []
    for _ in range(int(quantos)):
        pedacos = ["".join(alfabeto[b % len(alfabeto)]
                           for b in os.urandom(int(tamanho)))
                   for _ in range(int(grupos))]
        codigos.append("-".join(pedacos))
    return {
        "codigos": codigos,
        "resumos": [hashlib.sha256(c.encode()).hexdigest() for c in codigos],
    }


# ═══════════════════════════════════════════════════════════
#  4. Token assinado com prazo
# ═══════════════════════════════════════════════════════════

_MARCA_TOKEN = "DF1"


def _b64(dados):
    return base64.urlsafe_b64encode(dados).decode("ascii").rstrip("=")


def _de_b64(texto, onde):
    t = _texto(texto, onde)
    try:
        return base64.urlsafe_b64decode(t + "=" * (-len(t) % 4))
    except (binascii.Error, ValueError):
        raise _erro("O token nao e base64url valido.",
                    dica="Ele foi cortado, ou passou por um campo que reescreve texto.",
                    classe="SignatureError")


def _chave_de_assinatura(bytes_=32):
    """Uma chave nova. Ela e um SEGREDO — guarde no ambiente."""
    return _b64(os.urandom(int(bytes_)))


def _assinar(valor, chave, proposito="", quando=None):
    """Assina qualquer valor serializavel, com a hora dentro.

    O **proposito** e o detalhe que quase todo mundo esquece: sem ele,
    o token que confirma um e-mail serve para trocar a senha, porque
    os dois sao assinados com a mesma chave. Ele entra no que e
    assinado, entao um token de outro proposito nao confere.
    """
    agora = int(time.time() if quando is None else quando)
    corpo = json.dumps({"v": valor, "t": agora, "p": str(proposito)},
                       separators=(",", ":"), sort_keys=True,
                       ensure_ascii=False).encode("utf-8")
    parte = _MARCA_TOKEN + "." + _b64(corpo)
    mac = hmac.new(_bytes(chave, "assinar"), parte.encode("ascii"),
                   hashlib.sha256).digest()
    return parte + "." + _b64(mac)


def _ler_assinado(token, chave, prazo=None, proposito=""):
    """Confere a assinatura, DEPOIS o prazo, e so entao devolve.

    A ordem importa: conferir o prazo primeiro significa ler o corpo
    de um token que ainda nao se sabe se e legitimo. A data de dentro
    dele e dado de quem o mandou ate a assinatura fechar.
    """
    t = _texto(token, "ler_assinado")
    partes = t.split(".")
    if len(partes) != 3 or partes[0] != _MARCA_TOKEN:
        raise _erro("O token nao tem a forma de um token assinado.",
                    nota="A forma e 'DF1.<corpo>.<assinatura>'.",
                    classe="SignatureError")
    parte = partes[0] + "." + partes[1]
    esperado = hmac.new(_bytes(chave, "ler_assinado"), parte.encode("ascii"),
                        hashlib.sha256).digest()
    if not hmac.compare_digest(esperado, _de_b64(partes[2], "ler_assinado")):
        raise _erro(
            "A assinatura nao confere.",
            nota="O conteudo mudou depois de assinado, ou a chave e outra.",
            dica="Trate como pedido invalido; nao leia o conteudo mesmo assim.",
            classe="SignatureError",
        )
    try:
        corpo = json.loads(_de_b64(partes[1], "ler_assinado").decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise _erro("O corpo do token nao e legivel.", classe="SignatureError")

    if str(proposito) != str(corpo.get("p", "")):
        raise _erro(
            f"Este token foi assinado para '{corpo.get('p', '')}', "
            f"e esta sendo lido como '{proposito}'.",
            nota="Um token de confirmar e-mail nao serve para trocar senha.",
            dica="Use o mesmo 'proposito' ao assinar e ao ler.",
            classe="SignatureError",
        )
    idade = int(time.time()) - int(corpo.get("t", 0))
    if prazo is not None and idade > float(prazo):
        raise _erro(
            f"O token venceu ha {idade - int(float(prazo))} segundos.",
            nota=f"Ele vale por {int(float(prazo))} segundos, e tem {idade}.",
            dica="Ofereca gerar um novo; nao estenda o prazo do antigo.",
            classe="ExpiredTokenError",
        )
    return {"valor": corpo.get("v"), "idade": idade,
            "assinado_em": int(corpo.get("t", 0)), "proposito": corpo.get("p", "")}


def _assinar_url(url, chave, prazo=3600, quando=None):
    """Um link que expira — para download temporario e para confirmacao."""
    u = _texto(url, "assinar_url")
    agora = int(time.time() if quando is None else quando)
    vence = agora + int(prazo)
    partes = urllib.parse.urlsplit(u)
    consulta = urllib.parse.parse_qsl(partes.query, keep_blank_values=True)
    consulta = [(k, v) for k, v in consulta if k not in ("df_vence", "df_sig")]
    consulta.append(("df_vence", str(vence)))
    base = urllib.parse.urlunsplit(
        (partes.scheme, partes.netloc, partes.path,
         urllib.parse.urlencode(sorted(consulta)), ""))
    mac = hmac.new(_bytes(chave, "assinar_url"), base.encode("utf-8"),
                   hashlib.sha256).digest()
    consulta.append(("df_sig", _b64(mac)))
    return urllib.parse.urlunsplit(
        (partes.scheme, partes.netloc, partes.path,
         urllib.parse.urlencode(sorted(consulta)), partes.fragment))


def _conferir_url(url, chave, quando=None):
    u = _texto(url, "conferir_url")
    partes = urllib.parse.urlsplit(u)
    consulta = urllib.parse.parse_qsl(partes.query, keep_blank_values=True)
    assinatura = [v for k, v in consulta if k == "df_sig"]
    vence = [v for k, v in consulta if k == "df_vence"]
    if not assinatura or not vence:
        raise _erro("A URL nao esta assinada.",
                    nota="Faltam os campos 'df_sig' e 'df_vence'.",
                    classe="SignatureError")
    resto = [(k, v) for k, v in consulta if k != "df_sig"]
    base = urllib.parse.urlunsplit(
        (partes.scheme, partes.netloc, partes.path,
         urllib.parse.urlencode(sorted(resto)), ""))
    esperado = hmac.new(_bytes(chave, "conferir_url"), base.encode("utf-8"),
                        hashlib.sha256).digest()
    if not hmac.compare_digest(esperado, _de_b64(assinatura[0], "conferir_url")):
        raise _erro("A assinatura da URL nao confere.",
                    nota="Algum parametro foi mudado depois de assinada.",
                    classe="SignatureError")
    agora = int(time.time() if quando is None else quando)
    if agora > int(vence[0]):
        raise _erro(f"O link venceu ha {agora - int(vence[0])} segundos.",
                    dica="Gere outro link.", classe="ExpiredTokenError")
    return {"ok": True, "vence_em": int(vence[0]) - agora}


def _pkce(tamanho=64):
    """PKCE (RFC 7636) — o par que o OAuth 2.0 exige hoje.

    O problema que ele resolve: no fluxo de codigo de autorizacao, o
    `code` volta pela URL do navegador. Num aplicativo de celular ou
    numa SPA **nao existe segredo do cliente** para provar quem e — e
    quem interceptar o `code` (outro app registrado no mesmo esquema
    de URL, um log de proxy, o historico) o troca por um token.

    PKCE fecha isso sem segredo guardado: o cliente sorteia um
    `verificador`, manda o `desafio` (o SHA-256 dele) ao pedir o
    codigo, e manda o `verificador` ao trocar. So quem sorteou tem o
    original.

    **`S256`, nunca `plain`.** O metodo `plain` manda o verificador
    como desafio — o que nao protege de nada, porque quem intercepta a
    primeira ida ja tem os dois. Ele existe no RFC por compatibilidade
    e nao e oferecido aqui.
    """
    n = max(43, min(128, int(tamanho)))
    bruto = base64.urlsafe_b64encode(os.urandom(96)).decode("ascii")
    verificador = bruto.rstrip("=")[:n]
    resumo = hashlib.sha256(verificador.encode("ascii")).digest()
    return {
        "verificador": verificador,
        "desafio": base64.urlsafe_b64encode(resumo).decode("ascii").rstrip("="),
        "metodo": "S256",
    }


def _conferir_pkce(verificador, desafio):
    """Do lado do servidor de autorizacao: o par fecha?

    Em tempo constante — comparar com `is` vazaria, pelo tempo, quantos
    caracteres iniciais estavam certos.
    """
    v = _texto(verificador, "conferir_pkce")
    resumo = hashlib.sha256(v.encode("utf-8")).digest()
    esperado = base64.urlsafe_b64encode(resumo).decode("ascii").rstrip("=")
    return hmac.compare_digest(esperado, _texto(desafio, "conferir_pkce"))


def _estado_de_oauth(bytes_=32):
    """O `state` do OAuth, que e a defesa de CSRF do fluxo.

    Sem ele, um atacante inicia o proprio fluxo e faz a vitima
    completa-lo: a conta da vitima acaba ligada a conta do atacante no
    provedor. Ele e sorteado, guardado na sessao, e **conferido na
    volta** — guardar e nao conferir e o defeito mais comum.
    """
    return base64.urlsafe_b64encode(os.urandom(int(bytes_))).decode("ascii").rstrip("=")


# ═══════════════════════════════════════════════════════════
#  5. Segredo: o que se recusa a aparecer, e o que se procura
# ═══════════════════════════════════════════════════════════

class Segredo:
    """Um valor que nao aparece em texto, em log nem em JSON.

    Todo caminho que serializa foi fechado — `__str__`, `__repr__`,
    `__format__`. Interpolar um Segredo numa mensagem da `***`, e e
    esse o ponto: o vazamento mais comum nao e um commit, e um vault
    inteiro impresso para depurar.

    Ele **nao** protege da memoria nem de quem chama `revelar()`. O que
    ele faz e transformar um vazamento acidental numa linha explicita
    que aparece na revisao de codigo.
    """

    __slots__ = ("_valor", "_rotulo")

    def __init__(self, valor, rotulo="segredo"):
        object.__setattr__(self, "_valor", valor)
        object.__setattr__(self, "_rotulo", str(rotulo))

    def revelar(self):
        """A unica saida. Uma linha, visivel, buscavel."""
        return self._valor

    def vazio(self):
        return not self._valor

    def tamanho(self):
        return len(self._valor) if self._valor is not None else 0

    def igual(self, outro):
        """Em tempo constante, e aceitando outro Segredo."""
        alvo = outro.revelar() if isinstance(outro, Segredo) else outro
        a = self._valor if isinstance(self._valor, (str, bytes)) else str(self._valor)
        b = alvo if isinstance(alvo, (str, bytes)) else str(alvo)
        if isinstance(a, str):
            a = a.encode("utf-8")
        if isinstance(b, str):
            b = b.encode("utf-8")
        return hmac.compare_digest(a, b)

    def __str__(self):
        return "***"

    def __repr__(self):
        return f"<Segredo {self._rotulo}: ***>"

    def __format__(self, _spec):
        return "***"

    def __bool__(self):
        return bool(self._valor)

    def __eq__(self, outro):
        return self.igual(outro)

    def __hash__(self):
        raise _erro(
            "Um Segredo nao pode virar chave de vault.",
            nota="O resumo dele acabaria num log ou numa chave de cache.",
            dica="Use 'chave.revelar()' se for mesmo isso que voce quer.",
        )


_PADROES = [
    ("chave privada", r"-----BEGIN [A-Z ]*PRIVATE KEY-----", 1.0),
    ("AWS", r"\b(?:AKIA|ASIA|AIDA|AROA)[0-9A-Z]{16}\b", 1.0),
    ("GitHub", r"\b(?:ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{16,}\b", 1.0),
    ("Stripe", r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{10,}\b", 1.0),
    ("Slack", r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b", 1.0),
    ("Google", r"\bAIza[0-9A-Za-z_-]{35}\b", 1.0),
    ("OpenAI", r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b", 0.9),
    ("Anthropic", r"\bsk-ant-[A-Za-z0-9_-]{20,}\b", 1.0),
    ("PyPI", r"\bpypi-[A-Za-z0-9_-]{16,}\b", 1.0),
    ("Telegram", r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b", 0.9),
    ("JWT com papel privilegiado",
     r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b", 0.9),
    ("SendGrid", r"\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\b", 1.0),
    ("senha em URL", r"\b[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]{3,}@", 0.9),
    ("atribuicao suspeita",
     r"(?i)\b(?:senha|password|passwd|secret|segredo|token|api[_-]?key|"
     r"apikey|access[_-]?key|private[_-]?key|client[_-]?secret)\b"
     r"\s*[:=]+\s*[\"']([^\"'\n]{8,})[\"']", 0.5),
]

_INOCENTES = {
    "", "x", "xxx", "senha", "password", "secret", "token", "changeme",
    "your-api-key", "your_api_key", "sua-chave", "seu-token", "exemplo",
    "example", "placeholder", "redacted", "removido", "todo", "fixme",
    "null", "none", "void", "undefined", "test", "teste", "dummy", "fake",
    "usuario", "user", "admin", "root", "localhost", "minha senha",
}

#: Marcas de valor de DEMONSTRACAO, procuradas DENTRO do valor.
#:
#: A lista de iguais acima nao alcanca `"123456:AAHexemplo"`, e foi
#: exatamente esse token de brinquedo — num exercicio que ENSINA a nao
#: escrever token no arquivo — que a primeira versao acusou. Uma
#: varredura que acusa o material didatico do proprio projeto e
#: desligada no mesmo dia, e junto com ela vao os achados de verdade.
_MARCAS_DE_EXEMPLO = (
    "exemplo", "example", "sample", "placeholder", "changeme", "troque",
    "seu-", "seu_", "sua-", "sua_", "your-", "your_", "my-", "meu-",
    "xxxx", "abc-def", "aaaa", "0000", "1111", "...", "<", ">",
    "fake", "dummy", "teste", "test-", "test_", "redacted", "removido",
    "minha", "minhas", "meu-", "meu_", "outro", "outra", "senha",
    "desenvolvimento", "development", "s3nha", "hunter2", "segredo",
)

#: Hosts que nao valem um alarme: a credencial nao alcanca nada.
#:
#: 'postgres://forge:forge@localhost' num teste e a forma normal de
#: escrever um teste. Os dominios reservados (RFC 2606 e RFC 6761)
#: existem para documentacao e nunca resolvem para nada de verdade.
_HOSTS_DE_EXEMPLO = ("localhost", "127.0.0.1", "0.0.0.0", "::1",
                     "[::1]", "host.docker.internal")
_TLDS_DE_EXEMPLO = (".example", ".test", ".invalid", ".localhost",
                    ".local", ".exemplo")


def _e_de_exemplo(valor):
    """Um valor que se anuncia como demonstracao.

    Ela erra para o lado de CALAR: quem escolhe `senha_exemplo` como
    senha de producao tem um problema que uma varredura de formato nao
    ia resolver de qualquer jeito.
    """
    baixo = str(valor).strip().lower()
    if baixo in _INOCENTES:
        return True
    return any(marca in baixo for marca in _MARCAS_DE_EXEMPLO)


#: Papeis de JWT que sao PUBLICOS por desenho.
#:
#: A chave `anon` do Supabase vai no pacote do navegador de proposito
#: — quem protege a linha e o RLS, nao o segredo da chave. A
#: `service_role` ignora o RLS e e comprometimento total. As duas tem
#: o mesmo formato, e so o conteudo as separa.
#:
#: Acusar as duas igual faz o relatorio encher de chave que esta certa
#: onde esta, e e assim que o achado de verdade se perde no meio.
_PAPEIS_PUBLICOS = {"anon", "authenticated", "public"}


def _papel_do_jwt(token):
    """O 'role' de dentro do JWT, sem verificar a assinatura.

    Nao verificar e o certo AQUI: a pergunta nao e 'este token e
    valido?', e 'que autoridade ele carrega?'. Um token forjado com
    'service_role' escrito dentro continua sendo algo que nao devia
    estar num arquivo.
    """
    partes = str(token).split(".")
    if len(partes) != 3:
        return ""
    try:
        corpo = base64.urlsafe_b64decode(partes[1] + "=" * (-len(partes[1]) % 4))
        return str(json.loads(corpo.decode("utf-8", "replace")).get("role", ""))
    except Exception:
        return ""


def _padroes_de_segredo():
    """A lista, para quem quiser saber o que e procurado."""
    return [{"tipo": t, "padrao": p, "confianca": c} for t, p, c in _PADROES]


def _e_alta_entropia(texto, minimo=3.5):
    """Bits POR CARACTERE — a medida que separa chave de palavra.

    Um texto em portugues fica perto de 4 bits/caractere; uma chave
    base64 aleatoria passa de 5. A medida absoluta nao serve aqui,
    porque ela cresce com o tamanho e um paragrafo longo passaria.
    """
    t = _texto(texto, "e_alta_entropia")
    if len(t) < 8:
        return False
    return (_entropia(t) / len(t)) >= float(minimo)


def _procurar_segredos(texto, opcoes=None):
    """Onde ha o que parece um segredo, com linha, coluna e mascara.

    Ela acha por FORMATO, e por isso acha o que quem escreveu
    esqueceu. O `trecho` ja vem mascarado: um relatorio de vazamento
    que imprime o segredo inteiro e mais um lugar onde ele esta.
    """
    t = _texto(texto, "procurar_segredos")
    o = _opcoes(opcoes, {"minimo_de_confianca": 0.5, "entropia": True},
                    "Seguranca.procurar_segredos")
    achados = []
    vistos = set()

    for tipo, padrao, confianca in _PADROES:
        if confianca < float(o["minimo_de_confianca"]):
            continue
        for m in re.finditer(padrao, t):
            bruto = m.group(1) if m.groups() else m.group(0)
            if _e_de_exemplo(bruto):
                continue
            if tipo == "JWT com papel privilegiado":
                papel = _papel_do_jwt(bruto)
                if not papel or papel in _PAPEIS_PUBLICOS:
                    continue
                tipo = f"JWT '{papel}'"
            if tipo == "senha em URL":
                # O que interessa e a SENHA, nao a URL inteira:
                # 'postgres://usuario:senha@localhost' e um exemplo de
                # manual, e a cadeia toda nunca casa com a lista.
                credencial = bruto.split("//", 1)[-1].rstrip("@")
                if any(_e_de_exemplo(parte)
                       for parte in credencial.split(":", 1)):
                    continue
                # E o host importa: uma senha de 'localhost' nao
                # alcanca nada que nao seja a maquina de quem rodou.
                resto = t[m.end():m.end() + 80].lower()
                if resto.startswith(_HOSTS_DE_EXEMPLO):
                    continue
                dominio = re.split(r"[/:\"'\s]", resto, 1)[0]
                if dominio.endswith(_TLDS_DE_EXEMPLO):
                    continue
            if m.groups() and o["entropia"] and not _e_alta_entropia(bruto, 2.6):
                continue
            inicio = m.start(1) if m.groups() else m.start()
            if (inicio, tipo) in vistos:
                continue
            vistos.add((inicio, tipo))
            linha = t.count("\n", 0, inicio) + 1
            comeco = t.rfind("\n", 0, inicio) + 1
            achados.append({
                "tipo": tipo, "linha": linha, "coluna": inicio - comeco + 1,
                "inicio": inicio, "tamanho": len(bruto),
                "trecho": _mascarar(bruto), "confianca": confianca,
            })
    achados.sort(key=lambda a: (a["linha"], a["coluna"]))
    return achados


def _mascarar(valor, visivel=4):
    """Mostra o comeco, esconde o resto. O comeco identifica sem entregar."""
    t = valor if isinstance(valor, str) else str(valor)
    v = int(visivel)
    if len(t) <= v:
        return "*" * len(t)
    return t[:v] + "*" * min(12, len(t) - v)


def _exigir_sem_segredo(texto, onde=""):
    """Levanta se houver. Para um gancho de pre-commit, ou um upload.

    A dica diz 'rotacione', e nao 'apague': um segredo que ja foi
    gravado num arquivo ja pode ter sido lido. Tirar do arquivo
    resolve o proximo vazamento, nao este.
    """
    achados = _procurar_segredos(texto)
    if achados:
        primeiro = achados[0]
        lugar = f" em {onde}" if onde else ""
        raise _erro(
            f"Ha {len(achados)} segredo(s){lugar}: "
            f"{primeiro['tipo']} na linha {primeiro['linha']}.",
            nota="; ".join(f"{a['tipo']} l.{a['linha']} ({a['trecho']})"
                           for a in achados[:5]),
            dica="Tire o valor do arquivo, ponha num '.env' ignorado, e ROTACIONE "
                 "a chave: se ela foi gravada, pode ja ter sido lida.",
            classe="SecretLeakError",
        )
    return True


def _redigir(texto):
    """O mesmo texto, com os segredos mascarados no lugar.

    Para gravar num log o corpo de um pedido, ou o ambiente inteiro,
    sem que o log vire o proximo vazamento.
    """
    t = _texto(texto, "redigir")
    achados = _procurar_segredos(t)
    for a in sorted(achados, key=lambda x: -x["inicio"]):
        fim = a["inicio"] + a["tamanho"]
        t = t[:a["inicio"]] + a["trecho"] + t[fim:]
    return t


_PII = [
    ("cpf", r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    ("cnpj", r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"),
    ("cartao", r"\b(?:\d[ -]?){13,19}\b"),
    ("email", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    ("telefone", r"\b(?:\+55\s?)?\(?\d{2}\)?\s?9?\d{4}[- ]?\d{4}\b"),
    ("cep", r"\b\d{5}-\d{3}\b"),
]


def _luhn(digitos):
    total = 0
    for i, c in enumerate(reversed(digitos)):
        n = int(c)
        if i % 2:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _mascarar_pii(texto, tipos=None):
    """CPF, CNPJ, cartao, e-mail, telefone e CEP viram forma sem valor.

    O cartao passa pelo Luhn antes: sem isso, todo numero de pedido de
    16 digitos virava cartao mascarado, e o relatorio ficava ilegivel
    — um falso positivo que faz desligar a mascara inteira.
    """
    t = _texto(texto, "mascarar_pii")
    quais = set(tipos) if tipos else {n for n, _ in _PII}

    def troca(tipo):
        def _f(m):
            bruto = m.group(0)
            so_digitos = re.sub(r"\D", "", bruto)
            if tipo == "cartao":
                if not (13 <= len(so_digitos) <= 19) or not _luhn(so_digitos):
                    return bruto
                return "*" * (len(so_digitos) - 4) + so_digitos[-4:]
            if tipo == "email":
                nome, _, dominio = bruto.partition("@")
                return (nome[:1] + "*" * max(1, len(nome) - 1)) + "@" + dominio
            if tipo in ("cpf", "cnpj"):
                return "*" * (len(bruto) - 2) + bruto[-2:]
            return "*" * len(bruto)
        return _f

    for tipo, padrao in _PII:
        if tipo in quais:
            t = re.sub(padrao, troca(tipo), t)
    return t


# ═══════════════════════════════════════════════════════════
#  6. Entrada hostil
# ═══════════════════════════════════════════════════════════

_URL = {"esquemas": ["http", "https"], "permitir_privado": False,
        "permitir_local": False, "portas": [], "hosts": [],
        "resolver": True}

_METADADOS = {"169.254.169.254", "metadata.google.internal", "100.100.100.200"}


def _host_privado(host):
    """Diz se um host aponta para dentro — resolvendo o nome.

    Bloquear por texto nao funciona: `localtest.me` resolve para
    127.0.0.1, e um atacante controla o DNS do dominio dele. A unica
    pergunta que vale e para onde o nome RESOLVE.
    """
    h = _texto(host, "host_privado").strip().strip("[]")
    if h.lower() in _METADADOS:
        return True
    enderecos = []
    try:
        enderecos.append(ipaddress.ip_address(h))
    except ValueError:
        try:
            for info in socket.getaddrinfo(h, None):
                try:
                    enderecos.append(ipaddress.ip_address(info[4][0]))
                except ValueError:
                    continue
        except (socket.gaierror, UnicodeError, OSError):
            return True  # nao resolve: na duvida, recusa
    if not enderecos:
        return True
    for ip in enderecos:
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified
                or str(ip) in _METADADOS):
            return True
    return False


def _url_segura(url, opcoes=None):
    """Recusa a URL que aponta para dentro. E a defesa do SSRF.

    O caso concreto: um campo "URL do seu webhook" com
    `http://169.254.169.254/latest/meta-data/` faz o SEU servidor
    buscar as credenciais da instancia e devolve-las na resposta. O
    pedido sai de dentro, entao o firewall nao ve nada de errado.

    Ela devolve a URL **normalizada**, e e essa que deve ser usada: se
    o programa conferir uma e buscar outra, a conferencia nao vale
    nada. E uma corrida continua possivel (o DNS pode mudar entre a
    conferencia e a busca); para fechar isso e preciso buscar pelo IP
    ja resolvido, e o modulo devolve ele em 'ip' para quem precisar.
    """
    u = _texto(url, "url_segura").strip()
    o = _opcoes(opcoes, _URL, "Seguranca.url_segura")
    partes = urllib.parse.urlsplit(u)

    if partes.scheme.lower() not in [str(e).lower() for e in o["esquemas"]]:
        raise _erro(
            f"O esquema '{partes.scheme or '(nenhum)'}' nao e aceito.",
            nota="Aceitos: " + ", ".join(o["esquemas"]),
            dica="'file:', 'gopher:' e 'dict:' servem para ler a maquina de dentro.",
            classe="UnsafeInputError",
        )
    if not partes.hostname:
        raise _erro("A URL nao tem host.", classe="UnsafeInputError")

    host = partes.hostname
    if o["hosts"] and host.lower() not in [str(h).lower() for h in o["hosts"]]:
        raise _erro(
            f"O host '{host}' nao esta na lista de permitidos.",
            nota="Permitidos: " + ", ".join(o["hosts"]),
            classe="UnsafeInputError",
        )
    if o["portas"] and partes.port and partes.port not in [int(p) for p in o["portas"]]:
        raise _erro(f"A porta {partes.port} nao esta na lista.",
                    classe="UnsafeInputError")

    ip = ""
    if o["resolver"] and not o["permitir_privado"]:
        if _host_privado(host):
            raise _erro(
                f"'{host}' aponta para a rede interna.",
                nota="Endereco privado, loopback, link-local ou de metadados.",
                dica="Um campo de URL preenchido por usuario nunca deve alcancar "
                     "a rede de dentro.",
                classe="UnsafeInputError",
            )
        try:
            ip = socket.getaddrinfo(host, None)[0][4][0]
        except (socket.gaierror, OSError, IndexError):
            ip = ""

    limpa = urllib.parse.urlunsplit(
        (partes.scheme.lower(), partes.netloc.lower(), partes.path or "/",
         partes.query, ""))
    return {"url": limpa, "host": host.lower(),
            "porta": partes.port or (443 if partes.scheme == "https" else 80),
            "esquema": partes.scheme.lower(), "ip": ip}


def _caminho_seguro(base, pedido):
    """O caminho final tem de ficar DENTRO da base. Resolvido.

    `realpath` antes de comparar e o que fecha o buraco: sem ele, um
    link simbolico dentro da pasta aponta para fora e a comparacao de
    texto aprova. Comparar com `startswith` sem o separador tambem
    erra — `/var/uploads-publico` comeca com `/var/uploads`.
    """
    b = os.path.realpath(_texto(base, "caminho_seguro"))
    p = _texto(pedido, "caminho_seguro")
    if "\x00" in p:
        raise _erro("O caminho tem um byte nulo.",
                    nota="E a forma classica de truncar o nome depois da conferencia.",
                    classe="UnsafeInputError")
    alvo = os.path.realpath(os.path.join(b, p))
    if alvo != b and not alvo.startswith(b + os.sep):
        raise _erro(
            f"O caminho sai da pasta base: '{p}'.",
            nota=f"Ele resolve para fora de '{b}'.",
            dica="Nao conserte o caminho: recuse o pedido.",
            classe="UnsafeInputError",
        )
    return alvo


_PROIBIDOS_WINDOWS = {
    "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
    "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4",
    "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


def _nome_de_arquivo_seguro(nome, padrao="arquivo"):
    """Um nome que nao navega, nao engana e existe no Windows.

    Tres coisas alem do obvio: o `..` some, os nomes reservados do
    Windows (`CON`, `NUL`, `LPT1`) ganham sufixo — criar um arquivo
    com esse nome falha la e funciona aqui —, e os caracteres de
    direcao de escrita somem, porque sao eles que fazem `foto_exe.txt`
    aparecer na tela sendo `foto_txt.exe`.
    """
    n = _sem_controle(_texto(nome, "nome_de_arquivo_seguro"))
    n = n.replace("\\", "/").split("/")[-1]
    n = re.sub(r'[<>:"|?*\x00-\x1f]', "", n)
    n = n.strip(" .")
    n = re.sub(r"\.{2,}", ".", n)
    if not n:
        return padrao
    raiz = n.split(".")[0].upper()
    if raiz in _PROIBIDOS_WINDOWS:
        n = "_" + n
    if len(n) > 200:
        raiz, ponto, ext = n.rpartition(".")
        n = (raiz[:200 - len(ext) - 1] + ponto + ext) if ponto else n[:200]
    return n


def _redirecionamento_seguro(destino, permitidos=None, padrao="/"):
    """Redirecionamento aberto: o phishing que usa o SEU dominio.

    `/sair?proximo=https://banco-falso.exemplo` sai do seu site com a
    barra de endereco mostrando o seu nome ate o ultimo instante. Aqui
    so passa caminho relativo — e host que esteja na lista.

    `//exemplo.com` e o caso que engana: parece caminho, e o navegador
    le como 'mesmo esquema, outro host'.
    """
    d = _sem_controle(_texto(destino, "redirecionamento_seguro")).strip()
    if not d or d.startswith(("//", "\\\\", "/\\", "\\/")):
        return padrao
    partes = urllib.parse.urlsplit(d)
    if not partes.scheme and not partes.netloc:
        return d if d.startswith("/") else padrao
    lista = [str(h).lower() for h in (permitidos or [])]
    if partes.scheme.lower() in ("http", "https") and partes.hostname:
        if partes.hostname.lower() in lista:
            return d
    return padrao


_JSON = {"profundidade": 20, "tamanho": 1048576, "chaves": 10000}


def _json_seguro(texto, opcoes=None):
    """JSON com teto de tamanho, de profundidade e de chaves.

    Um `[[[[[...]]]]]` de dez mil niveis estoura a pilha do leitor, e
    um objeto de um milhao de chaves come a memoria. Sao negacao de
    servico com 50 KB de corpo, e o leitor padrao aceita os dois.
    """
    t = _texto(texto, "json_seguro")
    o = _opcoes(opcoes, _JSON, "Seguranca.json_seguro")
    if len(t.encode("utf-8")) > int(o["tamanho"]):
        raise _erro(f"O JSON passa de {o['tamanho']} bytes.",
                    classe="UnsafeInputError")

    profundidade = 0
    maior = 0
    dentro_de_texto = False
    escapado = False
    for c in t:
        if dentro_de_texto:
            if escapado:
                escapado = False
            elif c == "\\":
                escapado = True
            elif c == '"':
                dentro_de_texto = False
            continue
        if c == '"':
            dentro_de_texto = True
        elif c in "[{":
            profundidade += 1
            maior = max(maior, profundidade)
            if maior > int(o["profundidade"]):
                raise _erro(
                    f"O JSON passa de {o['profundidade']} niveis de profundidade.",
                    nota="Aninhamento fundo estoura a pilha de quem le.",
                    classe="UnsafeInputError")
        elif c in "]}":
            profundidade -= 1

    try:
        valor = json.loads(t)
    except ValueError as erro:
        raise _erro(f"O JSON nao e valido: {erro}", classe="UnsafeInputError")

    def contar(v, total=0):
        if isinstance(v, dict):
            total += len(v)
            for x in v.values():
                total = contar(x, total)
        elif isinstance(v, list):
            for x in v:
                total = contar(x, total)
        return total

    if contar(valor) > int(o["chaves"]):
        raise _erro(f"O JSON passa de {o['chaves']} chaves.",
                    classe="UnsafeInputError")
    return valor


def _numero_seguro(texto, minimo=None, maximo=None, inteiro=True):
    """Converte e confere a faixa numa chamada so.

    `?pagina=-1` e `?tamanho=999999999` sao os dois pedidos que
    derrubam uma listagem, e os dois passam por qualquer conversao.
    """
    t = texto if isinstance(texto, (int, float)) else _texto(texto, "numero_seguro").strip()
    try:
        valor = int(t) if inteiro else float(t)
    except (ValueError, TypeError):
        raise _erro(f"'{t}' nao e um numero.", classe="UnsafeInputError")
    if minimo is not None and valor < minimo:
        raise _erro(f"{valor} e menor que o minimo ({minimo}).",
                    classe="UnsafeInputError")
    if maximo is not None and valor > maximo:
        raise _erro(f"{valor} passa do maximo ({maximo}).",
                    classe="UnsafeInputError")
    return valor


# ═══════════════════════════════════════════════════════════
#  7. Limite e bloqueio
# ═══════════════════════════════════════════════════════════

class _Limitador:
    """Balde de fichas: N por periodo, com rajada.

    O balde enche continuamente, e nao de uma vez por janela. Com
    janela fixa, um cliente gasta o limite no ultimo segundo de uma e
    no primeiro da seguinte — o dobro do limite num instante, que e
    exatamente o que se queria evitar.

    E por PROCESSO e em memoria. Num servidor com varios processos,
    cada um tem o seu balde, e o limite efetivo e N vezes maior;
    limite compartilhado pede um banco ou um Redis, e este modulo nao
    pretende ser nenhum dos dois.
    """

    __slots__ = ("limite", "periodo", "rajada", "_baldes", "_trava")

    def __init__(self, limite, periodo=60.0, rajada=None):
        self.limite = float(limite)
        self.periodo = float(periodo)
        self.rajada = float(rajada) if rajada is not None else float(limite)
        self._baldes = {}
        self._trava = threading.Lock()

    def permitir(self, chave="", custo=1.0):
        agora = time.monotonic()
        k = str(chave)
        with self._trava:
            fichas, quando = self._baldes.get(k, (self.rajada, agora))
            fichas = min(self.rajada,
                         fichas + (agora - quando) * (self.limite / self.periodo))
            if fichas >= float(custo):
                self._baldes[k] = (fichas - float(custo), agora)
                return True
            self._baldes[k] = (fichas, agora)
            return False

    def restante(self, chave=""):
        agora = time.monotonic()
        with self._trava:
            fichas, quando = self._baldes.get(str(chave), (self.rajada, agora))
            return round(min(self.rajada,
                             fichas + (agora - quando) * (self.limite / self.periodo)), 3)

    def espera(self, chave="", custo=1.0):
        """Quantos segundos faltam. E o valor do 'Retry-After'."""
        falta = float(custo) - self.restante(chave)
        if falta <= 0:
            return 0.0
        return round(falta * (self.periodo / self.limite), 3)

    def limpar(self, chave=None):
        with self._trava:
            if chave is None:
                self._baldes.clear()
            else:
                self._baldes.pop(str(chave), None)
        return True


class _Tentativas:
    """Bloqueio progressivo depois de N falhas.

    A espera dobra a cada bloqueio, ate um teto. Um limite fixo e
    contornado esperando o periodo; o crescimento torna a forca bruta
    cara sem nunca trancar de vez quem so errou a senha.

    `sucesso()` zera. Sem isso, quem erra duas vezes por mes fica
    perto do bloqueio para sempre.
    """

    __slots__ = ("limite", "base", "teto", "_estado", "_trava")

    def __init__(self, limite=5, base=30.0, teto=3600.0):
        self.limite = int(limite)
        self.base = float(base)
        self.teto = float(teto)
        self._estado = {}
        self._trava = threading.Lock()

    def _agora(self):
        return time.monotonic()

    def bloqueado(self, chave=""):
        with self._trava:
            falhas, ate, _ = self._estado.get(str(chave), (0, 0.0, 0))
            return self._agora() < ate

    def falta(self, chave=""):
        with self._trava:
            falhas, ate, _ = self._estado.get(str(chave), (0, 0.0, 0))
            return max(0.0, round(ate - self._agora(), 2))

    def falha(self, chave=""):
        k = str(chave)
        with self._trava:
            falhas, ate, bloqueios = self._estado.get(k, (0, 0.0, 0))
            falhas += 1
            if falhas >= self.limite:
                espera = min(self.teto, self.base * (2 ** bloqueios))
                self._estado[k] = (0, self._agora() + espera, bloqueios + 1)
                return {"bloqueado": True, "segundos": round(espera, 2),
                        "falhas": falhas}
            self._estado[k] = (falhas, ate, bloqueios)
            return {"bloqueado": False, "segundos": 0.0, "falhas": falhas,
                    "restantes": self.limite - falhas}

    def sucesso(self, chave=""):
        with self._trava:
            self._estado.pop(str(chave), None)
        return True

    def exigir(self, chave=""):
        """Levanta se estiver bloqueado. Para o caminho feliz."""
        if self.bloqueado(chave):
            raise _erro(
                f"Bloqueado por tentativas. Faltam {self.falta(chave)}s.",
                nota=f"Depois de {self.limite} falhas, a espera dobra a cada bloqueio.",
                classe="PolicyError",
            )
        return True


# ═══════════════════════════════════════════════════════════
#  8. Auditoria encadeada
# ═══════════════════════════════════════════════════════════

class _Auditoria:
    """Uma linha por evento, cada uma carregando o resumo da anterior.

    Isso nao impede editar o arquivo — nada num arquivo local impede.
    O que ele da e **evidencia**: alterar ou apagar uma linha faz a
    proxima deixar de fechar, e `conferir()` diz em qual. Para que a
    evidencia valha, a trilha tem de ser copiada para fora da maquina
    que a escreve — e isso esta na documentacao, e nao no codigo,
    porque o codigo nao tem como garantir.

    Os dados de cada evento passam por `redigir` antes de serem
    gravados: uma trilha de auditoria e exatamente o tipo de arquivo
    que acaba anexado a um chamado.
    """

    __slots__ = ("caminho", "_trava")

    GENESE = "0" * 64

    def __init__(self, caminho):
        self.caminho = str(caminho)
        self._trava = threading.Lock()

    @staticmethod
    def _resumo(linha):
        return hashlib.sha256(linha.encode("utf-8")).hexdigest()

    def _ultima(self):
        if not os.path.exists(self.caminho):
            return self.GENESE, 0
        anterior = self.GENESE
        n = 0
        with open(self.caminho, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    anterior = self._resumo(linha)
                    n += 1
        return anterior, n

    def registrar(self, evento, dados=None, quem=""):
        with self._trava:
            anterior, n = self._ultima()
            registro = {
                "n": n + 1,
                "quando": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                "evento": _escapar_log(str(evento)),
                "quem": _escapar_log(str(quem)),
                "dados": json.loads(_redigir(json.dumps(
                    dados if dados is not None else {}, ensure_ascii=False,
                    default=str))),
                "anterior": anterior,
            }
            linha = json.dumps(registro, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"))
            pasta = os.path.dirname(os.path.abspath(self.caminho))
            if pasta and not os.path.isdir(pasta):
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho, "a", encoding="utf-8") as f:
                f.write(linha + "\n")
                f.flush()
                os.fsync(f.fileno())
            return {"n": registro["n"], "resumo": self._resumo(linha)}

    def ler(self, limite=0):
        if not os.path.exists(self.caminho):
            return []
        saida = []
        with open(self.caminho, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    try:
                        saida.append(json.loads(linha))
                    except ValueError:
                        saida.append({"invalida": linha})
        return saida[-int(limite):] if limite else saida

    def conferir(self):
        """Percorre a cadeia. Diz OK, ou em qual registro ela quebra."""
        if not os.path.exists(self.caminho):
            return {"ok": True, "registros": 0, "quebra": 0}
        anterior = self.GENESE
        n = 0
        with open(self.caminho, "r", encoding="utf-8") as f:
            for numero, linha in enumerate(f, 1):
                linha = linha.strip()
                if not linha:
                    continue
                n += 1
                try:
                    registro = json.loads(linha)
                except ValueError:
                    return {"ok": False, "registros": n, "quebra": numero,
                            "motivo": "a linha nao e um registro legivel"}
                if registro.get("anterior") != anterior:
                    return {"ok": False, "registros": n, "quebra": numero,
                            "motivo": "o elo com o registro anterior nao fecha"}
                if registro.get("n") != n:
                    return {"ok": False, "registros": n, "quebra": numero,
                            "motivo": f"a numeracao pula (esperado {n}, achado {registro.get('n')})"}
                anterior = self._resumo(linha)
        return {"ok": True, "registros": n, "quebra": 0}

    def exigir_integra(self):
        r = self.conferir()
        if not r["ok"]:
            raise _erro(
                f"A cadeia de auditoria quebra no registro {r['quebra']}.",
                nota=r.get("motivo", ""),
                dica="Um registro foi alterado ou removido depois de escrito.",
                classe="AuditChainError",
            )
        return True


# ═══════════════════════════════════════════════════════════
#  9. Analise estatica de seguranca, sobre fonte DataForge
# ═══════════════════════════════════════════════════════════

_REGRAS = [
    ("segredo-no-codigo", "alto",
     None, "Um segredo escrito no arquivo.",
     "Leia de 'OS.env' e guarde num '.env' ignorado."),
    ("sql-concatenado", "alto",
     r"(?i)(?:query|execute|consultar|executar)\s*\(\s*(?:\$\"|[\"'][^\"']*[\"']\s*\+)",
     "SQL montado com interpolacao ou concatenacao.",
     "Passe os valores por parametro: 'query(sql, [valor])'."),
    ("shell-com-texto", "alto",
     r"(?i)\b(?:shell|system|popen)\s*\(\s*\$\"",
     "Linha de shell montada com interpolacao.",
     "Passe a lista de argumentos: 'OS.run([\"git\", \"log\", ref])'."),
    ("html-sem-escape", "medio",
     r"(?i)\brespond\s*\(\s*\$\"[^\"]*<",
     "HTML montado com interpolacao, sem escapar.",
     "Use 'render' com template, ou 'Seg.escapar_html' no valor."),
    ("md5-ou-sha1", "medio",
     r"(?i)\b(?:Crypto\.)?(?:md5|sha1)\s*\(",
     "MD5 e SHA-1 estao quebrados para assinatura.",
     "Use 'sha256'. Para senha, 'hash_password'."),
    ("senha-sem-derivacao", "alto",
     r"(?i)\b(?:Crypto\.)?(?:sha256|sha512)\s*\(\s*senha",
     "Senha guardada com resumo simples.",
     "Use 'Crypto.hash_password', que deriva com sal e custo."),
    ("aleatorio-fraco", "medio",
     r"(?i)\b(?:token|senha|chave|sessao|sess[aã]o)\w*\s*:?=\s*"
     r"[^\n]{0,40}\b(?:randint|randfloat|random|rand|shuffle|choice)\s*\(",
     "Aleatorio comum usado para valor de seguranca.",
     "Use 'Crypto.random_token' ou 'Crypto.random_bytes'."),
    ("comparacao-de-segredo", "medio",
     r"(?i)\b(?:token|assinatura|hmac|senha_hash|resumo)\s+is\s+",
     "Comparacao de segredo com 'is' vaza tempo.",
     "Use 'Crypto.constant_time_equals'."),
    ("verificacao-desligada", "alto",
     r"(?i)(?:verify|verificar|conferir)\s*:?=\s*no\b",
     "Verificacao desligada explicitamente.",
     "Se for para um teste, isole; nunca deixe no caminho de producao."),
    # A versao ampla desta regra — "IO.algo com interpolacao" — deu 16
    # acusacoes no repositorio e TODAS eram '$"{pasta}/nome-fixo"', com
    # 'pasta' criada duas linhas acima. O que torna um caminho perigoso
    # nao e a interpolacao: e a ORIGEM do que se interpola.
    ("caminho-de-fora", "medio",
     r"(?i)\bIO\.(?:read|write|ler|gravar|remove|append|copy)\w*\s*\(\s*"
     r"[^)\n]{0,60}\{[^}\n]*\b(?:req|query|params|body|corpo|entrada|"
     r"pedido|upload|enviado|form|formulario|argv|args)\b",
     "Caminho de arquivo montado com valor que veio de fora.",
     "Passe por 'Seg.caminho_seguro(base, pedido)' antes de abrir."),
]


def _regras_de_analise():
    return [{"regra": r[0], "gravidade": r[1], "descricao": r[3], "dica": r[4]}
            for r in _REGRAS]


def _analisar(fonte, caminho=""):
    """As dez regras sobre um arquivo `.df`, mais a varredura de segredos.

    E deliberadamente pequena e sintatica — ela le texto, nao a arvore.
    Um analisador de seguranca que tenta provar fluxo de dado erra nos
    dois sentidos, e o que se faz com o alarme errado e desligar tudo.
    Estas dez sao formas que quase nunca sao inocentes.

    O escape do analisador da linguagem vale aqui:
    `// df: permitir sql-concatenado` na linha, ou na de cima.
    """
    t = _texto(fonte, "analisar")
    linhas = t.split("\n")
    achados = []

    def silenciada(regra, indice):
        for i in (indice, indice - 1):
            if 0 <= i < len(linhas):
                m = re.search(r"//\s*df:\s*permitir\s+([\w-]+)", linhas[i])
                if m and m.group(1) == regra:
                    return True
        return False

    for a in _procurar_segredos(t):
        if silenciada("segredo-no-codigo", a["linha"] - 1):
            continue
        achados.append({
            "regra": "segredo-no-codigo", "gravidade": "alto",
            "linha": a["linha"], "coluna": a["coluna"], "arquivo": caminho,
            "mensagem": f"{a['tipo']} escrito no arquivo ({a['trecho']}).",
            "dica": "Leia de 'OS.env' e ROTACIONE a chave que ja esteve aqui.",
        })

    for regra, gravidade, padrao, descricao, dica in _REGRAS:
        if padrao is None:
            continue
        for i, linha in enumerate(linhas):
            sem_comentario = re.sub(r"(?<!\S)//(?![\d(]).*$", "", linha)
            m = re.search(padrao, sem_comentario)
            if not m or silenciada(regra, i):
                continue
            achados.append({
                "regra": regra, "gravidade": gravidade, "linha": i + 1,
                "coluna": m.start() + 1, "arquivo": caminho,
                "mensagem": descricao, "dica": dica,
            })

    ordem = {"alto": 0, "medio": 1, "baixo": 2}
    achados.sort(key=lambda a: (a["linha"], ordem.get(a["gravidade"], 3)))
    return achados


# ═══════════════════════════════════════════════════════════
#  O modulo
# ═══════════════════════════════════════════════════════════

class ArcaneSeguranca(dict):
    """O vault que o 'adopt' entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Seguranca",

            # 1. escapar, por destino
            "escapar_html": _escapar_html,
            "escapar_atributo": _escapar_atributo,
            "escapar_js": _escapar_js,
            "escapar_url": _escapar_url,
            "escapar_shell": _escapar_shell,
            "escapar_sql_like": _escapar_sql_like,
            "escapar_csv": _escapar_csv,
            "escapar_regex": _escapar_regex,
            "escapar_cabecalho": _escapar_cabecalho,
            "escapar_log": _escapar_log,
            "sem_controle": _sem_controle,
            "limpar_html": _limpar_html,

            # 2. senha
            "forca_da_senha": _forca_da_senha,
            "politica": _politica,
            "exigir_politica": _exigir_politica,
            "entropia": _entropia,
            "vazada": _vazada,
            "prefixo_vazamento": _prefixo_vazamento,
            "conferir_vazamento": _conferir_vazamento,

            # 3. segundo fator
            "totp_segredo": _totp_segredo,
            "totp_agora": _totp_agora,
            "totp_conferir": _totp_conferir,
            "totp_uri": _totp_uri,
            "hotp": _hotp,
            "codigos_de_recuperacao": _codigos_de_recuperacao,

            # 4. token assinado, e o fluxo do OAuth
            "chave_de_assinatura": _chave_de_assinatura,
            "pkce": _pkce,
            "conferir_pkce": _conferir_pkce,
            "estado_de_oauth": _estado_de_oauth,
            "assinar": _assinar,
            "ler_assinado": _ler_assinado,
            "assinar_url": _assinar_url,
            "conferir_url": _conferir_url,

            # 5. segredo
            "segredo": lambda valor, rotulo="segredo": Segredo(valor, rotulo),
            "e_segredo": lambda v: isinstance(v, Segredo),
            "procurar_segredos": _procurar_segredos,
            "exigir_sem_segredo": _exigir_sem_segredo,
            "redigir": _redigir,
            "mascarar": _mascarar,
            "mascarar_pii": _mascarar_pii,
            "e_alta_entropia": _e_alta_entropia,
            "padroes_de_segredo": _padroes_de_segredo,

            # 6. entrada hostil
            "url_segura": _url_segura,
            "host_privado": _host_privado,
            "caminho_seguro": _caminho_seguro,
            "nome_de_arquivo_seguro": _nome_de_arquivo_seguro,
            "redirecionamento_seguro": _redirecionamento_seguro,
            "json_seguro": _json_seguro,
            "numero_seguro": _numero_seguro,

            # 7. limite e bloqueio
            "limitador": lambda limite, periodo=60.0, rajada=None:
                _Limitador(limite, periodo, rajada),
            "tentativas": lambda limite=5, base=30.0, teto=3600.0:
                _Tentativas(limite, base, teto),

            # 8. auditoria
            "auditoria": lambda caminho: _Auditoria(caminho),

            # 9. analise
            "analisar": _analisar,
            "regras_de_analise": _regras_de_analise,
        }
