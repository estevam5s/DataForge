# -*- coding: utf-8 -*-
"""Arcane.Telegram — bots de Telegram, do primeiro '/start' ao webhook.

O que este modulo e
-------------------
A Bot API do Telegram e HTTP com JSON. Falar com ela do zero e possivel
e chato: sao noventa metodos, um formato de erro proprio, um limite de
taxa que responde no CORPO e nao no status, upload multipart, e uma
sintaxe de formatacao que quebra a mensagem inteira se um caractere
escapar. Este modulo cobre isso e para ali — ele nao inventa um
framework de conversa que o Telegram nao tem.

    adopt Arcane.Telegram as Tg

    app := Tg.app(Tg.segredo_do_ambiente())

    mark @app.comando("start")
    action comecar(ctx):
        ctx.responder("Ola! Mande /ajuda para ver o que eu faco.")

    app.rodar()

Cinco decisoes que valem lembrar
--------------------------------
1. **O transporte e proprio, e nao o 'Arcane.Malha'.** A Malha e o
   cliente certo para chamada entre servicos, e tem disjuntor. Um bot
   faz long polling com prazo de 50 segundos: para a Malha isso e uma
   chamada lenta atras da outra, e o disjuntor abriria sozinho. Alem
   disso o erro do Telegram vem no CORPO (`ok: false`) com status 200
   em varios casos, e o limite de taxa chega em
   `parameters.retry_after` — um cliente generico nao sabe ler nada
   disso. O que NAO se duplica e o calculo do recuo: ele vem de
   `Arcane.Malha.recuo`, porque duas nocoes de "espera com tremor"
   divergiriam.

2. **O token nunca aparece numa mensagem de erro.** Ele esta na URL de
   toda chamada, e a URL entra em todo traceback. `_esconder` troca o
   token por `<token>` antes de qualquer texto sair daqui. Um token
   vazado num log de CI e um bot sequestrado.

3. **`escapar` existe porque o MarkdownV2 e uma armadilha.** Um hifen
   ou um ponto sem escape faz o Telegram recusar a mensagem INTEIRA
   com 400, e o texto que quebra costuma ser o que veio do usuario —
   ou seja, funciona em teste e falha em producao.

4. **A conversa e uma maquina de estados explicita.** Guardar "em que
   passo este chat esta" num dicionario solto e o que todo bot faz
   errado: dois chats se misturam, e um bot reiniciado esquece todo
   mundo. Aqui o estado e por chat, e o armazem e trocavel.

5. **Da para testar sem token e sem rede.** `Tg.testar(app)` injeta
   updates e devolve o que o bot teria enviado. Um bot que so pode ser
   testado conversando com ele no celular nao tem teste nenhum.
"""

import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from .opcoes import ler as _ler_opcoes

#: A raiz da Bot API. Trocavel para apontar a um servidor local da Bot
#: API (o Telegram publica um, e quem tem volume alto o roda por conta).
RAIZ = "https://api.telegram.org"

#: Quanto o long polling espera o Telegram segurar a conexao. O valor
#: alto e de proposito: e o que troca "uma consulta por segundo" por
#: "uma conexao aberta", e e o modo que a documentacao do Telegram
#: recomenda.
ESPERA_LONGA = 50

#: Quantas vezes uma chamada e repetida quando a rede falha. O 429 do
#: Telegram NAO conta aqui: ele traz o tempo exato de espera, e repetir
#: antes dele so gasta a cota.
TENTATIVAS = 3


# ═══════════════════════════════════════════════════════════
#  Erros
# ═══════════════════════════════════════════════════════════

def _erro(mensagem, nota="", dica="", doc="telegram"):
    from ..errors import RuntimeError_
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=doc)


def _esconder(texto, token):
    """Tira o token de qualquer texto que va sair daqui.

    Ele esta na URL de toda chamada, e a URL entra em toda mensagem de
    erro do `urllib`. Um token num log de CI e um bot sequestrado, e o
    dono so descobre quando o bot comeca a mandar spam.
    """
    limpo = str(texto)
    if token:
        limpo = limpo.replace(str(token), "<token>")
        # O `bot<token>` do caminho tambem, para o caso de alguem ter
        # montado a URL a mao.
        limpo = limpo.replace("bot<token>", "bot<token>")
    return limpo


# ═══════════════════════════════════════════════════════════
#  Transporte
# ═══════════════════════════════════════════════════════════

def _recuo(tentativa):
    """A espera entre tentativas. Vem da Malha — uma conta so."""
    from .arcane_malha import recuo
    return recuo(tentativa, base=0.4, teto=8.0, tremor=True)


def chamar(token, metodo, params=None, arquivos=None, prazo=25.0,
           raiz=None, tentativas=None):
    """Uma chamada crua a Bot API. Devolve o `result` do Telegram.

    E a porta de saida para os metodos que este modulo nao embrulha:
    a Bot API cresce, e um modulo que so oferece o que ele conhece
    envelhece no dia seguinte.

        Tg.chamar(token, "setChatTitle",
                  {"chat_id": -100123, "title": "Novo nome"})
    """
    alvo = f"{raiz or RAIZ}/bot{token}/{metodo}"
    limite = int(tentativas if tentativas is not None else TENTATIVAS)
    ultima = None

    for tentativa in range(1, max(1, limite) + 1):
        try:
            corpo, tipo = _empacotar(params or {}, arquivos)
            pedido = urllib.request.Request(
                alvo, data=corpo, method="POST",
                headers={"Content-Type": tipo,
                         "User-Agent": "DataForge-Telegram/1.0"})
            with urllib.request.urlopen(pedido, timeout=prazo) as resposta:
                pacote = json.loads(resposta.read().decode("utf-8"))
            return _resultado(pacote, metodo, token)
        except urllib.error.HTTPError as erro:
            try:
                pacote = json.loads(erro.read().decode("utf-8"))
            except Exception:                                # noqa: BLE001
                pacote = {"ok": False, "description": str(erro),
                          "error_code": erro.code}
            espera = _quanto_esperar(pacote)
            if espera is not None and tentativa < limite:
                # O 429 do Telegram traz o tempo EXATO. Repetir antes
                # dele so gasta cota e prolonga o bloqueio.
                time.sleep(espera)
                continue
            return _resultado(pacote, metodo, token)
        except (urllib.error.URLError, TimeoutError, OSError) as erro:
            ultima = erro
            if tentativa < limite:
                time.sleep(_recuo(tentativa))
                continue

    raise _erro(
        f"nao consegui falar com o Telegram em '{metodo}'.",
        nota=_esconder(str(ultima), token),
        dica="confira a rede e se 'api.telegram.org' nao esta bloqueado")


def _resultado(pacote, metodo, token):
    if pacote.get("ok"):
        return pacote.get("result")
    codigo = pacote.get("error_code", 0)
    descricao = _esconder(pacote.get("description", "sem descricao"), token)
    raise _erro(
        f"o Telegram recusou '{metodo}': {descricao}",
        nota=_ajuda_do_codigo(codigo, descricao),
        dica=_conserto_do_codigo(codigo))


#: O que cada codigo costuma significar, na pratica. A Bot API devolve
#: a mesma familia de numeros para causas bem diferentes, e a descricao
#: e em ingles e curta — sem esta traducao, o primeiro erro de quem
#: comeca e uma busca no Google.
_CODIGOS = {
    400: "pedido malformado — quase sempre o 'parse_mode' com um "
         "caractere sem escape, ou um 'chat_id' que nao existe",
    401: "o token nao vale. Ele foi revogado, ou veio com espaco em volta",
    403: "o bot foi bloqueado por essa pessoa, ou removido do grupo",
    404: "metodo que nao existe na Bot API — confira o nome",
    409: "outro processo esta fazendo polling com o MESMO token; o "
         "Telegram entrega o update a um so",
    429: "limite de taxa: mande menos mensagens por segundo",
}

_CONSERTOS = {
    400: "para texto com marcacao, passe por Tg.escapar(...) antes",
    401: "confira o token com Tg.bot(token).eu()",
    403: "nao ha conserto: quem bloqueou precisa desbloquear",
    409: "derrube o outro processo, ou troque para webhook",
    429: "use Tg.limitar(...) para segurar o ritmo",
}


def _ajuda_do_codigo(codigo, descricao):
    base = _CODIGOS.get(int(codigo or 0), "")
    if int(codigo or 0) == 400 and "entity" in descricao.lower():
        return ("a marcacao do texto esta quebrada: um caractere de "
                "MarkdownV2 sem escape recusa a mensagem INTEIRA")
    return base


def _conserto_do_codigo(codigo):
    return _CONSERTOS.get(int(codigo or 0), "")


def _quanto_esperar(pacote):
    """Os segundos que o Telegram pediu, ou `None` quando nao pediu."""
    parametros = pacote.get("parameters") or {}
    quanto = parametros.get("retry_after")
    # 'is not None', e nao 'or': um 'retry_after' de 0 significa
    # "pode tentar agora", e cair no caminho do None seria desistir.
    return float(quanto) if quanto is not None else None


def _empacotar(params, arquivos):
    """O corpo do pedido: JSON quando so ha dado, multipart quando ha arquivo."""
    limpo = {}
    for chave, valor in (params or {}).items():
        if valor is None:
            continue
        if isinstance(valor, (dict, list, tuple)):
            limpo[chave] = json.dumps(_serializavel(valor),
                                      ensure_ascii=False)
        elif isinstance(valor, bool):
            limpo[chave] = "true" if valor else "false"
        else:
            limpo[chave] = valor

    if not arquivos:
        return (json.dumps(_json_dos_campos(limpo),
                           ensure_ascii=False).encode("utf-8"),
                "application/json")
    return _multipart(limpo, arquivos)


def _json_dos_campos(limpo):
    """Os campos ja serializados voltam a ser objeto, para o corpo JSON.

    O caminho multipart precisa de tudo como texto; o JSON precisa do
    teclado como objeto. Serializar duas vezes faria o Telegram receber
    uma STRING onde espera um markup, e a resposta e um 400 que fala de
    'reply_markup' sem dizer que o problema e o formato.
    """
    saida = {}
    for chave, valor in limpo.items():
        if isinstance(valor, str) and valor[:1] in ("{", "["):
            try:
                saida[chave] = json.loads(valor)
                continue
            except ValueError:
                pass
        if isinstance(valor, str) and valor in ("true", "false"):
            saida[chave] = valor == "true"
            continue
        saida[chave] = valor
    return saida


def _multipart(campos, arquivos):
    import uuid

    limite = f"----DataForge{uuid.uuid4().hex}"
    partes = []
    for chave, valor in campos.items():
        partes.append(f"--{limite}\r\n".encode())
        partes.append(
            f'Content-Disposition: form-data; name="{chave}"\r\n\r\n'.encode())
        partes.append(str(valor).encode("utf-8"))
        partes.append(b"\r\n")

    for chave, arquivo in (arquivos or {}).items():
        nome, dados, tipo = _ler_arquivo(arquivo)
        partes.append(f"--{limite}\r\n".encode())
        partes.append(
            f'Content-Disposition: form-data; name="{chave}"; '
            f'filename="{nome}"\r\n'.encode())
        partes.append(f"Content-Type: {tipo}\r\n\r\n".encode())
        partes.append(dados)
        partes.append(b"\r\n")

    partes.append(f"--{limite}--\r\n".encode())
    return b"".join(partes), f"multipart/form-data; boundary={limite}"


def _ler_arquivo(arquivo):
    """Aceita caminho, bytes ou o vault de um upload. Devolve (nome, bytes, tipo)."""
    if isinstance(arquivo, dict):
        return (str(arquivo.get("nome", "arquivo")),
                arquivo.get("conteudo") or b"",
                str(arquivo.get("tipo") or "application/octet-stream"))
    if isinstance(arquivo, (bytes, bytearray)):
        return "arquivo", bytes(arquivo), "application/octet-stream"
    caminho = str(arquivo)
    if not os.path.isfile(caminho):
        raise _erro(f"nao achei o arquivo '{caminho}'.",
                    dica="passe o caminho, os bytes, ou o vault de um upload")
    import mimetypes
    tipo = mimetypes.guess_type(caminho)[0] or "application/octet-stream"
    with open(caminho, "rb") as f:
        return os.path.basename(caminho), f.read(), tipo


def _serializavel(valor):
    if isinstance(valor, dict):
        return {str(k): _serializavel(v) for k, v in valor.items()
                if v is not None}
    if isinstance(valor, (list, tuple)):
        return [_serializavel(v) for v in valor]
    if isinstance(valor, (str, int, float, bool)) or valor is None:
        return valor
    if hasattr(valor, "fields"):
        return _serializavel(dict(valor.fields))
    return str(valor)


# ═══════════════════════════════════════════════════════════
#  Formatacao
# ═══════════════════════════════════════════════════════════

#: Os caracteres que o MarkdownV2 exige escapados. A lista e a da
#: documentacao do Telegram, e ela e maior do que qualquer um espera —
#: o ponto e o hifen estao nela, e sao os que quebram um texto normal.
_RESERVADOS = r"_*[]()~`>#+-=|{}.!"


def escapar(texto):
    """Escapa o que o MarkdownV2 exige. Use SEMPRE no que veio de fora.

    Um hifen ou um ponto sem escape faz o Telegram recusar a mensagem
    **inteira** com 400 — e o texto que quebra costuma ser justamente o
    que veio do usuario, entao o bot funciona em teste e falha em
    producao, com o nome de alguem.
    """
    saida = []
    for c in str(texto):
        if c in _RESERVADOS:
            saida.append("\\")
        saida.append(c)
    return "".join(saida)


def escapar_html(texto):
    """O mesmo para `parse_mode := "HTML"`, que exige so tres trocas."""
    return (str(texto).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def negrito(texto):
    return f"*{escapar(texto)}*"


def italico(texto):
    return f"_{escapar(texto)}_"


def riscado(texto):
    return f"~{escapar(texto)}~"


def sublinhado(texto):
    return f"__{escapar(texto)}__"


def spoiler(texto):
    return f"||{escapar(texto)}||"


def codigo(texto):
    """Codigo em linha. Dentro dele so a crase e a barra sao escapadas."""
    limpo = str(texto).replace("\\", "\\\\").replace("`", "\\`")
    return f"`{limpo}`"


def bloco(texto, linguagem=""):
    limpo = str(texto).replace("\\", "\\\\").replace("`", "\\`")
    return f"```{linguagem}\n{limpo}\n```"


def link(texto, destino):
    limpo = str(destino).replace(")", "\\)").replace("\\", "\\\\")
    return f"[{escapar(texto)}]({limpo})"


def mencao(texto, id_usuario):
    return f"[{escapar(texto)}](tg://user?id={int(id_usuario)})"


# ═══════════════════════════════════════════════════════════
#  Teclados
# ═══════════════════════════════════════════════════════════

def botao(texto, dados=None, url=None, inline_atual=None, pedir_contato=False,
          pedir_local=False, jogo=False, pagar=False, app_web=None):
    """Um botao. O que ele faz depende do que voce preencher.

    `dados` faz dele um botao de callback — e o `dados` volta em
    `ctx.dados`. `url` abre um endereco. Os dois juntos sao um erro do
    Telegram, e e melhor descobrir isso aqui.
    """
    if dados is not None and url is not None:
        raise _erro("um botao nao pode ter 'dados' e 'url' ao mesmo tempo.",
                    nota="o Telegram recusa o teclado inteiro nesse caso",
                    dica="escolha: 'dados' responde ao bot, 'url' abre o link")
    marca = {"text": str(texto)}
    if dados is not None:
        cru = str(dados)
        # O limite e do protocolo: 64 BYTES, e nao 64 caracteres. Um
        # texto com acento estoura antes do que parece, e o Telegram
        # recusa o teclado inteiro com uma mensagem que nao diz qual
        # botao e o culpado.
        if len(cru.encode("utf-8")) > 64:
            raise _erro(
                f"o 'dados' do botao '{texto}' tem mais de 64 bytes.",
                nota=f"sao {len(cru.encode('utf-8'))} bytes; o limite e do "
                     f"protocolo, e conta BYTES, nao caracteres",
                dica="guarde o valor no estado e mande so uma chave curta")
        marca["callback_data"] = cru
    if url is not None:
        marca["url"] = str(url)
    if inline_atual is not None:
        marca["switch_inline_query_current_chat"] = str(inline_atual)
    if pedir_contato:
        marca["request_contact"] = True
    if pedir_local:
        marca["request_location"] = True
    if jogo:
        marca["callback_game"] = {}
    if pagar:
        marca["pay"] = True
    if app_web is not None:
        marca["web_app"] = {"url": str(app_web)}
    return marca


def botoes(linhas):
    """Um teclado embutido na mensagem. `linhas` e um cluster de clusters.

        Tg.botoes([[Tg.botao("Sim", dados := "sim"),
                    Tg.botao("Nao", dados := "nao")]])
    """
    return {"inline_keyboard": [_linha_de_botoes(l) for l in (linhas or [])]}


def teclado(linhas, uma_vez=True, ajustar=True, dica="", persistente=False):
    """O teclado que substitui o do celular. Cada item pode ser texto."""
    montadas = []
    for linha in (linhas or []):
        itens = linha if isinstance(linha, (list, tuple)) else [linha]
        montadas.append([
            i if isinstance(i, dict) else {"text": str(i)} for i in itens])
    marca = {"keyboard": montadas, "resize_keyboard": bool(ajustar),
             "one_time_keyboard": bool(uma_vez),
             "is_persistent": bool(persistente)}
    if dica:
        marca["input_field_placeholder"] = str(dica)
    return marca


def _unidades(texto):
    """O tamanho como o Telegram conta: em unidades UTF-16.

    Um emoji fora do plano basico (quase todos) vale DOIS. Contar
    caracteres do Python deixa passar uma mensagem de 4090 caracteres
    com emojis que o Telegram recusa com 'message is too long'.
    """
    return len(str(texto).encode("utf-16-le")) // 2


def dividir(texto, limite=4096):
    """O texto em pedaços que o Telegram aceita, cortando no lugar certo.

    A ordem de preferência para o corte é: parágrafo, linha, espaço — e
    só então no meio de uma palavra. Um escape do MarkdownV2 (`\\.`)
    nunca é separado da sua barra: um pedaço terminando em `\\` e o
    seguinte começando em `.` são DUAS mensagens recusadas.
    """
    limite = int(limite)
    if limite < 2:
        raise _erro("o limite precisa ser de ao menos 2 unidades.",
                    dica="o do Telegram e 4096; o de uma legenda, 1024")
    resto = str(texto)
    pedacos = []
    while _unidades(resto) > limite:
        # O maior prefixo que cabe, medido em UTF-16.
        corte, usados = 0, 0
        for i, c in enumerate(resto):
            usados += 2 if ord(c) > 0xFFFF else 1
            if usados > limite:
                break
            corte = i + 1
        janela = resto[:corte]
        posicao = -1
        for separador in ("\n\n", "\n", " "):
            achado = janela.rfind(separador)
            if achado > 0:
                posicao = achado + len(separador)
                break
        if posicao <= 0:
            posicao = corte
        # Barras no fim do pedaco: numero impar quer dizer um escape
        # partido ao meio. Recua uma posicao.
        barras = len(janela[:posicao]) - len(janela[:posicao].rstrip("\\"))
        if barras % 2 == 1:
            posicao -= 1
        pedaco = resto[:posicao].rstrip("\n ") or resto[:posicao]
        pedacos.append(pedaco)
        resto = resto[posicao:].lstrip("\n ") if posicao < len(resto) else ""
    if resto or not pedacos:
        pedacos.append(resto)
    return pedacos


def paginado(itens, pagina=1, por_pagina=5, prefixo="pg"):
    """Uma pagina de itens, com o teclado de navegacao pronto.

    Devolve `{itens, pagina, paginas, total, teclado}`. Os botoes mandam
    `prefixo:N` como `dados`; `Tg.ler_pagina(ctx.dados, prefixo)` devolve
    o N. A pagina e **limitada** ao intervalo: um callback velho (a
    lista encolheu desde que o teclado foi enviado) mostra a ultima
    pagina que existe, em vez de uma pagina vazia.
    """
    lista = list(itens or [])
    tamanho = max(1, int(por_pagina))
    paginas = max(1, -(-len(lista) // tamanho))
    atual = min(max(1, int(pagina)), paginas)
    inicio = (atual - 1) * tamanho
    linha = []
    if atual > 1:
        linha.append(botao("◀", dados=f"{prefixo}:{atual - 1}"))
    if paginas > 1:
        linha.append(botao(f"{atual}/{paginas}", dados=f"{prefixo}:{atual}"))
    if atual < paginas:
        linha.append(botao("▶", dados=f"{prefixo}:{atual + 1}"))
    return {
        "itens": lista[inicio:inicio + tamanho],
        "pagina": atual,
        "paginas": paginas,
        "total": len(lista),
        "teclado": botoes([linha]) if linha else None,
    }


def ler_pagina(dados, prefixo="pg"):
    """O numero da pagina de um callback `prefixo:N`, ou `void`.

    `void` para o que nao e deste teclado: o mesmo bot tem varios, e
    confundir `pg:2` com `menu:2` e o defeito que isto evita.
    """
    texto = str(dados or "")
    cabeca, _, numero = texto.partition(":")
    if cabeca != str(prefixo) or not numero.isdigit():
        return None
    return int(numero)


def remover_teclado(seletivo=False):
    return {"remove_keyboard": True, "selective": bool(seletivo)}


def forcar_resposta(dica="", seletivo=False):
    marca = {"force_reply": True, "selective": bool(seletivo)}
    if dica:
        marca["input_field_placeholder"] = str(dica)
    return marca


def _linha_de_botoes(linha):
    itens = linha if isinstance(linha, (list, tuple)) else [linha]
    return [i if isinstance(i, dict) else botao(str(i), dados=str(i))
            for i in itens]


# ═══════════════════════════════════════════════════════════
#  O bot
# ═══════════════════════════════════════════════════════════

class Bot:
    """O cliente da Bot API. Cada metodo e uma chamada, e nada mais.

    Ele NAO guarda estado de conversa: isso e da `Aplicacao`. Um
    cliente que tambem gerencia conversa e um objeto que faz duas
    coisas, e a segunda e a que difere entre um bot e outro.
    """

    def __init__(self, token, raiz=None, prazo=25.0):
        limpo = str(token or "").strip()
        if not limpo:
            raise _erro(
                "o token do bot esta vazio.",
                nota="peca um ao @BotFather; ele parece "
                     "'123456789:AAH...' ",
                dica='guarde num .env e leia com Tg.segredo_do_ambiente()')
        if ":" not in limpo:
            raise _erro(
                "isso nao parece um token de bot.",
                nota="um token tem a forma '<id>:<segredo>'; sem os dois "
                     "pontos, o Telegram responde 404 e nao 401 — o que "
                     "manda procurar o erro no lugar errado",
                dica="confira se nao veio um espaco ou uma aspa junto")
        self.token = limpo
        self.raiz = raiz or RAIZ
        self.prazo = float(prazo)
        self._eu = None
        self._trava = threading.RLock()

    # ── O basico ─────────────────────────────────────────────

    def chamar(self, metodo, params=None, arquivos=None, prazo=None):
        return chamar(self.token, metodo, params, arquivos,
                      prazo if prazo is not None else self.prazo, self.raiz)

    def eu(self):
        """Quem e este bot. Serve de teste de token: falha rapido e claro."""
        with self._trava:
            if self._eu is None:
                self._eu = self.chamar("getMe")
            return self._eu

    # ── Mandar ───────────────────────────────────────────────

    def enviar(self, chat, texto, **opcoes):
        """Manda texto. Devolve o vault da mensagem enviada."""
        config = _ler_opcoes(opcoes, _OPCOES_DE_ENVIO, "Telegram.enviar")
        params = {"chat_id": _chat(chat), "text": str(texto)}
        _juntar_comuns(params, config)
        if config.get("sem_previa"):
            params["link_preview_options"] = {"is_disabled": True}
        return self.chamar("sendMessage", params)

    def responder_para(self, mensagem, texto, **opcoes):
        """Responde CITANDO a mensagem. Em grupo, e o que da contexto."""
        opcoes.setdefault("responder_a", _id_da_mensagem(mensagem))
        return self.enviar(_chat_da_mensagem(mensagem), texto, **opcoes)

    def foto(self, chat, foto, legenda="", **opcoes):
        return self._midia("sendPhoto", "photo", chat, foto, legenda, opcoes)

    def documento(self, chat, arquivo, legenda="", **opcoes):
        return self._midia("sendDocument", "document", chat, arquivo,
                           legenda, opcoes)

    def audio(self, chat, arquivo, legenda="", **opcoes):
        return self._midia("sendAudio", "audio", chat, arquivo, legenda,
                           opcoes)

    def video(self, chat, arquivo, legenda="", **opcoes):
        return self._midia("sendVideo", "video", chat, arquivo, legenda,
                           opcoes)

    def voz(self, chat, arquivo, legenda="", **opcoes):
        return self._midia("sendVoice", "voice", chat, arquivo, legenda,
                           opcoes)

    def animacao(self, chat, arquivo, legenda="", **opcoes):
        return self._midia("sendAnimation", "animation", chat, arquivo,
                           legenda, opcoes)

    def adesivo(self, chat, arquivo, **opcoes):
        return self._midia("sendSticker", "sticker", chat, arquivo, "", opcoes)

    def _midia(self, metodo, campo, chat, arquivo, legenda, opcoes):
        config = _ler_opcoes(opcoes, _OPCOES_DE_ENVIO, f"Telegram.{campo}")
        params = {"chat_id": _chat(chat)}
        if legenda:
            params["caption"] = str(legenda)
        _juntar_comuns(params, config)
        # Um `file_id` ou uma URL vao como TEXTO; so o que esta em disco
        # (ou em memoria) sobe por multipart. Mandar tudo por multipart
        # funcionaria e reenviaria um arquivo que o Telegram ja tem.
        if _e_referencia(arquivo):
            params[campo] = str(arquivo)
            return self.chamar(metodo, params)
        return self.chamar(metodo, params, arquivos={campo: arquivo},
                           prazo=max(self.prazo, 120.0))

    def localizacao(self, chat, latitude, longitude, **opcoes):
        config = _ler_opcoes(opcoes, _OPCOES_DE_ENVIO, "Telegram.localizacao")
        params = {"chat_id": _chat(chat), "latitude": float(latitude),
                  "longitude": float(longitude)}
        _juntar_comuns(params, config)
        return self.chamar("sendLocation", params)

    def contato(self, chat, telefone, nome, sobrenome="", **opcoes):
        config = _ler_opcoes(opcoes, _OPCOES_DE_ENVIO, "Telegram.contato")
        params = {"chat_id": _chat(chat), "phone_number": str(telefone),
                  "first_name": str(nome), "last_name": str(sobrenome)}
        _juntar_comuns(params, config)
        return self.chamar("sendContact", params)

    def enquete(self, chat, pergunta, opcoes_da_enquete, anonima=True,
                varias=False, quiz=False, correta=None, **opcoes):
        config = _ler_opcoes(opcoes, _OPCOES_DE_ENVIO, "Telegram.enquete")
        params = {"chat_id": _chat(chat), "question": str(pergunta),
                  "options": [str(o) for o in (opcoes_da_enquete or [])],
                  "is_anonymous": bool(anonima),
                  "allows_multiple_answers": bool(varias)}
        if quiz:
            params["type"] = "quiz"
            params["correct_option_id"] = int(correta or 0)
        _juntar_comuns(params, config)
        return self.chamar("sendPoll", params)

    def acao(self, chat, tipo="typing"):
        """"Digitando…" no topo do chat. Vale 5 segundos, ou ate a mensagem.

        Chamar antes de um trabalho demorado e a diferenca entre um bot
        que parece travado e um que parece pensando.
        """
        return self.chamar("sendChatAction",
                           {"chat_id": _chat(chat), "action": str(tipo)})

    # ── Mexer no que ja foi ──────────────────────────────────

    def editar(self, chat, id_mensagem, texto, **opcoes):
        config = _ler_opcoes(opcoes, _OPCOES_DE_ENVIO, "Telegram.editar")
        params = {"chat_id": _chat(chat), "message_id": int(id_mensagem),
                  "text": str(texto)}
        _juntar_comuns(params, config)
        return self.chamar("editMessageText", params)

    def editar_teclado(self, chat, id_mensagem, teclado_novo=None):
        return self.chamar("editMessageReplyMarkup", {
            "chat_id": _chat(chat), "message_id": int(id_mensagem),
            "reply_markup": teclado_novo})

    def apagar(self, chat, id_mensagem):
        return self.chamar("deleteMessage", {
            "chat_id": _chat(chat), "message_id": int(id_mensagem)})

    def fixar(self, chat, id_mensagem, silencioso=True):
        return self.chamar("pinChatMessage", {
            "chat_id": _chat(chat), "message_id": int(id_mensagem),
            "disable_notification": bool(silencioso)})

    def desafixar(self, chat, id_mensagem=None):
        params = {"chat_id": _chat(chat)}
        if id_mensagem is not None:
            params["message_id"] = int(id_mensagem)
        return self.chamar("unpinChatMessage", params)

    # ── Responder a interacao ────────────────────────────────

    def responder_botao(self, id_callback, texto="", alerta=False, url=""):
        """SEMPRE chame isto num callback.

        Sem a resposta, o Telegram deixa o botao com o relogio girando
        por ate um minuto, e quem clicou conclui que o bot travou.
        """
        params = {"callback_query_id": str(id_callback),
                  "show_alert": bool(alerta)}
        if texto:
            params["text"] = str(texto)
        if url:
            params["url"] = str(url)
        return self.chamar("answerCallbackQuery", params)

    def responder_inline(self, id_consulta, resultados, cache=300,
                         pessoal=False, proxima=""):
        params = {"inline_query_id": str(id_consulta),
                  "results": list(resultados or []),
                  "cache_time": int(cache),
                  "is_personal": bool(pessoal)}
        if proxima:
            params["next_offset"] = str(proxima)
        return self.chamar("answerInlineQuery", params)

    # ── Arquivos ─────────────────────────────────────────────

    def baixar(self, file_id, destino=""):
        """Baixa um arquivo do Telegram. Devolve os bytes, ou o caminho.

        Sao DUAS chamadas: `getFile` devolve um caminho temporario, e o
        download e num endereco diferente. Um bot que guarda o `file_id`
        e o re-envia depois nao precisa de nenhuma das duas — e e o que
        se deve fazer quando o arquivo so vai voltar ao Telegram.
        """
        info = self.chamar("getFile", {"file_id": str(file_id)})
        caminho = info.get("file_path")
        if not caminho:
            raise _erro("o Telegram nao devolveu o caminho do arquivo.",
                        nota="arquivos acima de 20 MB nao podem ser baixados "
                             "pela Bot API")
        url = f"{self.raiz}/file/bot{self.token}/{caminho}"
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                dados = r.read()
        except Exception as erro:                            # noqa: BLE001
            raise _erro("nao consegui baixar o arquivo.",
                        nota=_esconder(str(erro), self.token))
        if destino:
            pasta = os.path.dirname(os.path.abspath(str(destino)))
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(str(destino), "wb") as f:
                f.write(dados)
            return str(destino)
        return dados

    # ── Grupos ───────────────────────────────────────────────

    def banir(self, chat, usuario, ate=None):
        params = {"chat_id": _chat(chat), "user_id": int(usuario)}
        if ate is not None:
            params["until_date"] = int(ate)
        return self.chamar("banChatMember", params)

    def desbanir(self, chat, usuario):
        return self.chamar("unbanChatMember", {
            "chat_id": _chat(chat), "user_id": int(usuario)})

    def silenciar(self, chat, usuario, ate=None):
        """Tira a permissao de enviar. E o `restrictChatMember` sem nada ligado."""
        params = {"chat_id": _chat(chat), "user_id": int(usuario),
                  "permissions": {"can_send_messages": False}}
        if ate is not None:
            params["until_date"] = int(ate)
        return self.chamar("restrictChatMember", params)

    def membro(self, chat, usuario):
        return self.chamar("getChatMember", {
            "chat_id": _chat(chat), "user_id": int(usuario)})

    def e_admin(self, chat, usuario):
        """`yes` quando a pessoa administra o chat. A pergunta mais comum."""
        try:
            info = self.membro(chat, usuario)
        except Exception:                                    # noqa: BLE001
            return False
        return str(info.get("status", "")) in ("creator", "administrator")

    def chat(self, chat):
        return self.chamar("getChat", {"chat_id": _chat(chat)})

    # ── A cara do bot ────────────────────────────────────────

    def comandos(self, lista, escopo=None, idioma=""):
        """Registra o menu de comandos — o que aparece ao digitar '/'.

        `lista` e um vault `{"start": "comecar"}` ou um cluster de
        vaults. Sem isso, quem abre o bot nao descobre o que ele faz.
        """
        if isinstance(lista, dict):
            comandos = [{"command": str(k).lstrip("/"), "description": str(v)}
                        for k, v in lista.items()]
        else:
            comandos = []
            for item in (lista or []):
                if isinstance(item, dict):
                    comandos.append({
                        "command": str(item.get("comando",
                                                item.get("command", ""))
                                       ).lstrip("/"),
                        "description": str(item.get("descricao",
                                                    item.get("description", "")))})
        params = {"commands": comandos}
        if escopo:
            params["scope"] = escopo
        if idioma:
            params["language_code"] = str(idioma)
        return self.chamar("setMyCommands", params)

    def descricao(self, texto, curta=""):
        self.chamar("setMyDescription", {"description": str(texto)})
        if curta:
            self.chamar("setMyShortDescription",
                        {"short_description": str(curta)})
        return True

    def nome(self, texto, idioma=""):
        params = {"name": str(texto)}
        if idioma:
            params["language_code"] = str(idioma)
        return self.chamar("setMyName", params)

    # ── Updates ──────────────────────────────────────────────

    def updates(self, desde=0, espera=ESPERA_LONGA, tipos=None):
        params = {"offset": int(desde), "timeout": int(espera)}
        if tipos:
            params["allowed_updates"] = [str(t) for t in tipos]
        # O prazo do HTTP precisa ser MAIOR que o do long polling, senao
        # o cliente desiste no exato instante em que o Telegram ia
        # responder — e o sintoma e um bot que perde mensagens sob carga
        # baixa, que e quando o polling chega ao fim do prazo.
        return self.chamar("getUpdates", params,
                           prazo=float(espera) + 15.0) or []

    def webhook(self, url, segredo="", tipos=None, max_conexoes=40,
                certificado=None):
        params = {"url": str(url), "max_connections": int(max_conexoes)}
        if segredo:
            params["secret_token"] = str(segredo)
        if tipos:
            params["allowed_updates"] = [str(t) for t in tipos]
        if certificado:
            return self.chamar("setWebhook", params,
                               arquivos={"certificate": certificado})
        return self.chamar("setWebhook", params)

    def sem_webhook(self, descartar=False):
        return self.chamar("deleteWebhook",
                           {"drop_pending_updates": bool(descartar)})

    def info_do_webhook(self):
        return self.chamar("getWebhookInfo")

    def __repr__(self):
        return f"<bot {self.token.split(':')[0]}>"


#: As opcoes que todo envio aceita. A lista fica num lugar so, e ela e
#: a documentacao: 'Telegram.enviar(chat, texto, marcacao := "HTML")'
#: com um nome errado seria uma mensagem sem formatacao, calada.
_OPCOES_DE_ENVIO = {
    "marcacao": "",            # MarkdownV2, HTML, ou vazio
    "teclado": None,
    "responder_a": None,
    "silencioso": False,
    "sem_previa": False,
    "proteger": False,
    "topico": None,
}


def _juntar_comuns(params, config):
    if config.get("marcacao"):
        params["parse_mode"] = str(config["marcacao"])
    if config.get("teclado") is not None:
        params["reply_markup"] = config["teclado"]
    if config.get("responder_a"):
        params["reply_parameters"] = {
            "message_id": int(config["responder_a"]),
            # Sem isto, responder a uma mensagem que foi apagada faz a
            # chamada inteira falhar — e apagar mensagem e comum.
            "allow_sending_without_reply": True}
    if config.get("silencioso"):
        params["disable_notification"] = True
    if config.get("proteger"):
        params["protect_content"] = True
    if config.get("topico") is not None:
        params["message_thread_id"] = int(config["topico"])


def _e_referencia(arquivo):
    """Um `file_id` ou uma URL nao precisam subir de novo."""
    if not isinstance(arquivo, str):
        return False
    if arquivo.startswith(("http://", "https://")):
        return True
    return not os.path.isfile(arquivo) and len(arquivo) > 20 and \
        " " not in arquivo and "/" not in arquivo


def _chat(chat):
    """Aceita id, @usuario, ou o vault de um chat."""
    if isinstance(chat, dict):
        return chat.get("id", chat.get("chat_id"))
    return chat


def _id_da_mensagem(mensagem):
    if isinstance(mensagem, dict):
        return mensagem.get("message_id", mensagem.get("id"))
    return mensagem


def _chat_da_mensagem(mensagem):
    if isinstance(mensagem, dict):
        return (mensagem.get("chat") or {}).get("id")
    return mensagem


def bot(token, raiz=None, prazo=25.0):
    """Abre o cliente da Bot API."""
    return Bot(token, raiz, prazo)


def segredo_do_ambiente(nome="TELEGRAM_TOKEN"):
    """O token, do ambiente. Falha dizendo o que fazer quando falta.

    Um token no codigo vira um token no GitHub — e o @BotFather nao
    avisa quando alguem o usa. Esta funcao existe para que o caminho
    certo seja o mais curto.
    """
    valor = os.environ.get(str(nome), "").strip()
    if not valor:
        raise _erro(
            f"a variavel de ambiente '{nome}' esta vazia.",
            nota="o token do bot nunca deve ficar no codigo: ele vai para "
                 "o Git, e de la para qualquer um",
            dica=f'exporte antes de rodar:  export {nome}="123:AAH..."')
    return valor


def modo_servidor():
    """`yes` quando quem chamou quer o bot **no ar**.

    Um arquivo de bot tem dois destinos, e eles se contradizem:
    `dataforge telegram run` espera que ele suba e fique atendendo; a
    suite roda o mesmo arquivo com `dataforge run`, e um arquivo que
    entra em long polling ali nunca termina.

        given Tg.modo_servidor():
            app.rodar()
        otherwise:
            conferir()

    Responde `yes` quando o `dataforge telegram` anunciou o modo no
    ambiente, e quando `--servir` esta nos argumentos — a segunda forma
    continua valendo para quem chama `dataforge run` direto. E o mesmo
    contrato do `V.modo_servidor()` da Vitrine, de proposito: duas
    respostas para a mesma pergunta divergiriam.
    """
    import sys

    if os.environ.get("TELEGRAM_MODO"):
        return True
    return any(arg in ("--servir", "--serve") for arg in sys.argv[1:])


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

class ArcaneTelegram:
    """Arcane.Telegram — bots de Telegram, do '/start' ao webhook."""

    def __new__(cls):
        # O import e aqui dentro, e nao no topo: 'arcane_telegram_app'
        # importa este arquivo, e o par no topo daria um ciclo. E o
        # mesmo motivo do import de baixo em 'render.py'.
        from .arcane_telegram_app import (
            Aplicacao, BotFalso, Contexto, EmArquivo, EmMemoria, Limitador,
            Sonda, app, estado_em_arquivo, estado_em_memoria, limitar, testar)

        return {
            "__name__": "Arcane.Telegram",

            # ── O bot e o app ──
            "bot": bot,
            "Bot": Bot,
            "app": app,
            "Aplicacao": Aplicacao,
            "chamar": chamar,
            "segredo_do_ambiente": segredo_do_ambiente,
            "modo_servidor": modo_servidor,

            # ── Teclados ──
            "botao": botao,
            "botoes": botoes,
            "teclado": teclado,
            "remover_teclado": remover_teclado,
            "forcar_resposta": forcar_resposta,
            "paginado": paginado,
            "ler_pagina": ler_pagina,
            "dividir": dividir,

            # ── Formatação ──
            "escapar": escapar,
            "escapar_html": escapar_html,
            "negrito": negrito,
            "italico": italico,
            "riscado": riscado,
            "sublinhado": sublinhado,
            "spoiler": spoiler,
            "codigo": codigo,
            "bloco": bloco,
            "link": link,
            "mencao": mencao,

            # ── Estado e ritmo ──
            "estado_em_memoria": estado_em_memoria,
            "estado_em_arquivo": estado_em_arquivo,
            "limitar": limitar,
            "Limitador": Limitador,

            # ── Testar ──
            "testar": testar,
            "Sonda": Sonda,
            "BotFalso": BotFalso,
            "Contexto": Contexto,

            # ── Constantes ──
            "RAIZ": RAIZ,
            "ESPERA_LONGA": ESPERA_LONGA,
            "acoes": ["typing", "upload_photo", "record_video",
                      "upload_video", "record_voice", "upload_voice",
                      "upload_document", "choose_sticker", "find_location",
                      "record_video_note", "upload_video_note"],
        }
