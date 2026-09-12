# -*- coding: utf-8 -*-
"""Kiln — upload, streaming e WebSocket.

As tres coisas que o framework nao tinha, e que separam um servidor de
demonstracao de um que atende um sistema.

**Upload** (`multipart/form-data`). O corpo era interpretado como JSON
ou como formulario simples; um `<input type="file">` chegava como texto
ilegivel. Isso deixava de fora toda tela que recebe planilha, foto ou
documento — que e a maioria das telas de cadastro.

**SSE** (`text/event-stream`). Uma resposta que nao termina: o servidor
empurra evento por evento e o navegador reconecta sozinho. Sao trinta
linhas de protocolo e resolvem o caso de "tempo real" que quase todo
painel precisa — fila, progresso de importacao, notificacao.

**WebSocket** (RFC 6455). Duas vias, quadro binario, sobre a mesma
porta. O `http.server` nao tem suporte, mas tem o que basta: o handshake
e HTTP com `Upgrade`, e depois dele o socket e nosso.

Quando usar qual
----------------
| Precisa | Use |
|---|---|
| o servidor avisa, o cliente so ouve | **SSE** — mais simples, reconecta sozinho, passa em qualquer proxy |
| os dois falam | **WebSocket** |
| um arquivo grande sem carregar na memoria | `Kiln.stream` |

SSE primeiro, sempre que servir: ele e HTTP comum, e um proxy velho no
caminho nao o quebra.
"""

import base64
import hashlib
import json
import os
import struct
import time
import uuid

#: A constante do RFC 6455 que o handshake exige. Nao e um segredo — e
#: um valor fixo do protocolo, e esta aqui para o calculo ser legivel.
_MAGICA_WS = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

#: Os opcodes do WebSocket que tratamos.
_TEXTO, _BINARIO, _FECHAR, _PING, _PONG = 0x1, 0x2, 0x8, 0x9, 0xA

#: Teto de um quadro recebido. Sem ele, um cliente anuncia 8 exabytes no
#: cabecalho e o servidor tenta alocar.
_MAX_QUADRO = 8 * 1024 * 1024


# ═══════════════════════════════════════════════════════════
#  Upload — multipart/form-data
# ═══════════════════════════════════════════════════════════

def interpretar_multipart(bruto, tipo_de_conteudo):
    """`multipart/form-data` vira um vault de campos e arquivos.

    Devolve `{"campos": {...}, "arquivos": {...}}`. Cada arquivo tem
    `nome`, `tipo`, `tamanho`, `conteudo` (bytes) e `texto`.

    Escrito a mao em vez de usar o `cgi` do Python: o modulo foi
    removido no 3.13, e o `email.parser` que sobrou precisa do corpo
    inteiro remontado como mensagem MIME — mais codigo e mais copia da
    mesma memoria.

    Um campo repetido vira **cluster**, e nao o ultimo valor: e assim
    que um `<select multiple>` e uma lista de caixas chegam.
    """
    fronteira = _fronteira_de(tipo_de_conteudo)
    if not fronteira:
        return None

    marca = b"--" + fronteira
    campos = {}
    arquivos = {}

    # O corpo e uma sequencia de partes entre marcas. A primeira e a
    # ultima sao vazias, por construcao do protocolo.
    for parte in bruto.split(marca)[1:-1]:
        parte = parte.lstrip(b"\r\n")
        if not parte or parte.startswith(b"--"):
            continue
        cabeca, _, corpo = parte.partition(b"\r\n\r\n")
        # O CRLF final pertence a marca seguinte, nao ao dado.
        corpo = corpo[:-2] if corpo.endswith(b"\r\n") else corpo

        cabecalhos = _cabecalhos_da_parte(cabeca)
        disposicao = cabecalhos.get("content-disposition", "")
        nome = _parametro(disposicao, "name")
        if not nome:
            continue

        arquivo = _parametro(disposicao, "filename")
        if arquivo is not None:
            # 'filename=""' e o que o navegador manda quando o campo de
            # arquivo ficou vazio: nao e um arquivo de nome vazio.
            if not arquivo:
                continue
            arquivos[nome] = {
                "nome": os.path.basename(arquivo.replace("\\", "/")),
                "tipo": cabecalhos.get("content-type", ""),
                "tamanho": len(corpo),
                "conteudo": corpo,
                "texto": corpo.decode("utf-8", errors="replace"),
            }
        else:
            valor = corpo.decode("utf-8", errors="replace")
            if nome in campos:
                atual = campos[nome]
                campos[nome] = (atual + [valor] if isinstance(atual, list)
                                else [atual, valor])
            else:
                campos[nome] = valor

    return {"campos": campos, "arquivos": arquivos}


def _fronteira_de(tipo):
    """O `boundary=` do Content-Type, em bytes."""
    if not tipo or "multipart/form-data" not in tipo.lower():
        return None
    for pedaco in tipo.split(";"):
        chave, _, valor = pedaco.strip().partition("=")
        if chave.strip().lower() == "boundary":
            return valor.strip().strip('"').encode("latin-1")
    return None


def _cabecalhos_da_parte(cabeca):
    saida = {}
    for linha in cabeca.decode("utf-8", errors="replace").split("\r\n"):
        chave, _, valor = linha.partition(":")
        if valor:
            saida[chave.strip().lower()] = valor.strip()
    return saida


def _parametro(disposicao, nome):
    """`name="foto"` vira `foto`. Devolve None quando não há o parâmetro."""
    for pedaco in disposicao.split(";"):
        chave, _, valor = pedaco.strip().partition("=")
        if chave.strip().lower() == nome:
            return valor.strip().strip('"')
    return None


def salvar_upload(arquivo, pasta, nome=None, limite=0, tipos=None):
    """Grava um arquivo recebido, recusando o que nao deveria entrar.

    Tres recusas, e as tres ja foram exploradas em servidor de verdade:

    | Recusa | Porque |
    |---|---|
    | nome com `/` ou `..` | `../../.ssh/authorized_keys` escreve fora da pasta |
    | acima do limite | um upload de 4 GB enche o disco |
    | extensao fora da lista | `.php` numa pasta servida como estatica e execucao remota |

    O nome final nunca e o que o cliente mandou: leva um prefixo
    aleatorio. Dois usuarios enviando "foto.jpg" nao podem sobrescrever
    um ao outro, e um nome escolhido por quem envia e um nome que ele
    pode adivinhar depois.
    """
    from ..errors import RuntimeError_

    bruto = arquivo.get("nome", "") if isinstance(arquivo, dict) else ""
    dados = arquivo.get("conteudo", b"") if isinstance(arquivo, dict) else b""
    if isinstance(dados, str):
        dados = dados.encode()

    pedido = str(nome or bruto)
    # RECUSA, e nao 'basename' em silencio. O 'basename' neutralizaria a
    # travessia — 'passwd' e um nome valido —, mas um cliente que manda
    # '../../.ssh/authorized_keys' esta quebrado ou e hostil, e aceitar
    # como 'authorized_keys' esconde isso de quem le o log.
    #
    # O caminho do Windows que o IE mandava ('C:\Users\ana\foto.jpg') ja
    # foi reduzido a 'foto.jpg' por 'interpretar_multipart': aqui, uma
    # barra significa que alguem passou por fora do interpretador.
    if any(marca in pedido for marca in ("/", "\\")) or ".." in pedido \
            or not pedido or pedido in (".", ".."):
        raise RuntimeError_(
            f"nome de arquivo recusado: {pedido!r}", 0, 0,
            nota="um nome com '/', '\\' ou '..' escreve fora da pasta "
                 "de destino",
            dica="passe apenas o nome do arquivo, sem caminho",
            doc="kiln/uploads")
    seguro = pedido

    if limite and len(dados) > limite:
        raise RuntimeError_(
            f"arquivo de {len(dados)} bytes acima do limite de {limite}.",
            0, 0, dica="aumente o limite, ou recuse antes de ler o corpo",
            doc="kiln/uploads")

    extensao = os.path.splitext(seguro)[1].lower()
    if tipos is not None:
        aceitos = {("." + t.lstrip(".")).lower() for t in tipos}
        if extensao not in aceitos:
            raise RuntimeError_(
                f"extensao '{extensao}' nao esta na lista aceita.", 0, 0,
                nota="aceitas: " + ", ".join(sorted(aceitos)),
                doc="kiln/uploads")

    os.makedirs(pasta, exist_ok=True)
    final = f"{uuid.uuid4().hex[:12]}{extensao}"
    caminho = os.path.join(pasta, final)
    with open(caminho, "wb") as destino:
        destino.write(dados)
    return {"caminho": caminho, "nome": final, "nome_original": seguro,
            "tamanho": len(dados)}


# ═══════════════════════════════════════════════════════════
#  SSE — o servidor empurra
# ═══════════════════════════════════════════════════════════

def evento(dados, tipo="", identificador="", reconectar=0):
    """Um evento SSE, no formato do protocolo.

    O `\\n\\n` final nao e enfeite: e ele que diz ao navegador que o
    evento acabou. Sem a linha vazia, o cliente espera para sempre.
    """
    linhas = []
    if identificador:
        linhas.append(f"id: {identificador}")
    if tipo:
        linhas.append(f"event: {tipo}")
    if reconectar:
        linhas.append(f"retry: {int(reconectar)}")

    corpo = (dados if isinstance(dados, str)
             else json.dumps(_serializavel(dados), ensure_ascii=False))
    # Cada linha do dado leva seu proprio 'data:' — um texto com '\\n'
    # dentro quebraria o evento no meio.
    for linha in corpo.split("\n"):
        linhas.append(f"data: {linha}")
    return "\n".join(linhas) + "\n\n"


class Fluxo:
    """A ponta do servidor numa resposta que nao termina.

    Quem escreve a rota recebe este objeto e chama `enviar`. Quando o
    cliente fecha a aba, `aberto` passa a ser `no` e o laco termina —
    sem isso, um painel fechado deixa uma thread empurrando dado para
    ninguem, para sempre.
    """

    __slots__ = ("_escrita", "aberto", "enviados", "comecou_em")

    def __init__(self, escrita):
        self._escrita = escrita
        self.aberto = True
        self.enviados = 0
        self.comecou_em = time.time()

    def enviar(self, dados, tipo="", identificador=""):
        """Um evento. Devolve `no` quando o cliente ja foi embora."""
        return self._escrever(evento(dados, tipo, identificador))

    def escrever(self, texto):
        """Um pedaco cru, sem formato de evento.

        E o que 'Kiln.stream' usa: exportar um CSV de um milhao de
        linhas manda linha por linha, e nao um evento por linha.
        Devolve `no` quando o cliente ja foi embora.
        """
        return self._escrever(texto if isinstance(texto, str)
                              else str(texto))

    def comentario(self, texto=""):
        """Um comentario SSE — o batimento que mantem a conexao viva.

        Proxy e balanceador fecham conexao ociosa, tipicamente em 30 a
        60 segundos. Um comentario a cada 15 e barato e evita isso; o
        navegador o ignora.
        """
        return self._escrever(f": {texto}\n\n")

    def fechar(self):
        self.aberto = False

    def _escrever(self, texto):
        if not self.aberto:
            return False
        try:
            self._escrita.write(texto.encode("utf-8"))
            self._escrita.flush()
            self.enviados += 1
            return True
        except (BrokenPipeError, ConnectionResetError, OSError, ValueError):
            self.aberto = False
            return False


def resposta_de_fluxo(gerador, cabecalhos=None):
    """Marca a resposta como um fluxo SSE.

    O handler reconhece a marca e chama o gerador com um `Fluxo`, em vez
    de serializar um corpo e fechar a conexao.
    """
    cabs = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        # O nginx guarda resposta em buffer por padrao, e com isso o
        # evento so chega quando o buffer enche — o que destroi o SSE.
        "X-Accel-Buffering": "no",
    }
    cabs.update(cabecalhos or {})
    return {"__kiln__": True, "__fluxo__": gerador, "status": 200,
            "headers": cabs, "content_type": "text/event-stream; charset=utf-8",
            "body": "", "cookies": []}


# ═══════════════════════════════════════════════════════════
#  WebSocket
# ═══════════════════════════════════════════════════════════

def chave_de_resposta(chave_do_cliente):
    """A resposta do handshake: sha1(chave + magica), em base64.

    O RFC pede exatamente isso. Nao ha seguranca nenhuma nessa conta —
    ela existe para provar que o servidor entende o protocolo, e nao
    para autenticar.
    """
    bruto = (str(chave_do_cliente).strip() + _MAGICA_WS).encode()
    return base64.b64encode(hashlib.sha1(bruto).digest()).decode()


def e_pedido_de_upgrade(cabecalhos):
    """O pedido esta pedindo para virar WebSocket?"""
    conexao = str(cabecalhos.get("connection", "")).lower()
    upgrade = str(cabecalhos.get("upgrade", "")).lower()
    return "upgrade" in conexao and upgrade == "websocket"


class Soquete:
    """Uma conexao WebSocket aberta, do lado do servidor.

    `receber` bloqueia ate chegar um quadro ou a conexao morrer, e
    devolve `void` no segundo caso — que e como o laco de quem escreve
    termina:

        route GET "/ws":
            ws := Kiln.aceitar_ws(req)
            persist ws.aberto:
                msg := ws.receber()
                given msg is void:
                    halt
                ws.enviar($"ecoando: {msg}")

    Ping e pong sao respondidos aqui dentro, sem chegar a quem escreve:
    eles sao manutencao do protocolo, e obrigar a tratar isso seria
    obrigar a conhecer o RFC.
    """

    __slots__ = ("_conexao", "aberto", "recebidos", "enviados", "id",
                 "aberto_em")

    def __init__(self, conexao):
        self._conexao = conexao
        self.aberto = True
        self.recebidos = 0
        self.enviados = 0
        self.id = uuid.uuid4().hex[:12]
        self.aberto_em = time.time()

    # ── Enviar ──────────────────────────────────────────────

    def enviar(self, mensagem):
        """Texto, ou qualquer valor — que vira JSON."""
        if isinstance(mensagem, (bytes, bytearray)):
            return self._quadro(_BINARIO, bytes(mensagem))
        texto = (mensagem if isinstance(mensagem, str)
                 else json.dumps(_serializavel(mensagem), ensure_ascii=False))
        return self._quadro(_TEXTO, texto.encode("utf-8"))

    def enviar_json(self, valor):
        return self._quadro(
            _TEXTO,
            json.dumps(_serializavel(valor), ensure_ascii=False).encode())

    def ping(self, dados=b""):
        return self._quadro(_PING, dados)

    def fechar(self, codigo=1000, motivo=""):
        """Fecha com aperto de mao, e nao cortando o cabo.

        Um fechamento limpo faz o navegador saber que acabou; cortar o
        socket faz o `onerror` disparar do outro lado, e quem escreveu o
        cliente vai procurar um bug que nao existe.
        """
        if not self.aberto:
            return False
        corpo = struct.pack("!H", int(codigo)) + motivo.encode("utf-8")[:123]
        self._quadro(_FECHAR, corpo)
        self.aberto = False
        try:
            self._conexao.close()
        except OSError:
            pass
        return True

    # ── Receber ─────────────────────────────────────────────

    def receber(self, prazo=None):
        """A proxima mensagem, ou `void` se a conexao acabou.

        `prazo` em segundos; sem ele, espera indefinidamente. Um prazo e
        o que permite um laco que tambem faz outra coisa — mandar um
        relogio a cada segundo, por exemplo.
        """
        if prazo is not None:
            try:
                self._conexao.settimeout(float(prazo))
            except OSError:
                return None

        while self.aberto:
            quadro = self._ler_quadro()
            if quadro is None:
                self.aberto = False
                return None
            opcode, dados = quadro

            if opcode == _FECHAR:
                self.aberto = False
                try:
                    self._conexao.close()
                except OSError:
                    pass
                return None
            if opcode == _PING:
                self._quadro(_PONG, dados)
                continue
            if opcode == _PONG:
                continue
            self.recebidos += 1
            if opcode == _BINARIO:
                return dados
            return dados.decode("utf-8", errors="replace")
        return None

    def receber_json(self, prazo=None):
        """A proxima mensagem, interpretada. `void` se nao for JSON."""
        bruto = self.receber(prazo)
        if bruto is None:
            return None
        try:
            return json.loads(bruto if isinstance(bruto, str)
                              else bruto.decode("utf-8", errors="replace"))
        except (ValueError, TypeError):
            return None

    # ── O protocolo ─────────────────────────────────────────

    def _quadro(self, opcode, dados):
        """Monta e envia um quadro. O servidor NUNCA mascara."""
        if not self.aberto:
            return False
        tamanho = len(dados)
        cabeca = bytearray([0x80 | opcode])
        if tamanho < 126:
            cabeca.append(tamanho)
        elif tamanho < 65536:
            cabeca.append(126)
            cabeca += struct.pack("!H", tamanho)
        else:
            cabeca.append(127)
            cabeca += struct.pack("!Q", tamanho)
        try:
            self._conexao.sendall(bytes(cabeca) + dados)
            self.enviados += 1
            return True
        except (BrokenPipeError, ConnectionResetError, OSError):
            self.aberto = False
            return False

    def _ler_quadro(self):
        """(opcode, dados) do proximo quadro, ou None.

        Junta os quadros de continuacao: uma mensagem grande chega
        partida, e entregar os pedacos a quem escreve seria vazar o
        protocolo para dentro da aplicacao.
        """
        primeiro = self._ler_exato(2)
        if primeiro is None:
            return None

        fim = primeiro[0] & 0x80
        opcode = primeiro[0] & 0x0F
        mascarado = primeiro[1] & 0x80
        tamanho = primeiro[1] & 0x7F

        if tamanho == 126:
            extra = self._ler_exato(2)
            if extra is None:
                return None
            tamanho = struct.unpack("!H", extra)[0]
        elif tamanho == 127:
            extra = self._ler_exato(8)
            if extra is None:
                return None
            tamanho = struct.unpack("!Q", extra)[0]

        if tamanho > _MAX_QUADRO:
            # Um cliente pode anunciar 8 exabytes no cabecalho. Fechar e
            # a resposta certa: alocar seria derrubar o processo.
            self.fechar(1009, "quadro grande demais")
            return None

        mascara = self._ler_exato(4) if mascarado else None
        if mascarado and mascara is None:
            return None

        corpo = self._ler_exato(tamanho) if tamanho else b""
        if corpo is None:
            return None
        if mascara:
            corpo = bytes(b ^ mascara[i % 4] for i, b in enumerate(corpo))

        if fim:
            return opcode, corpo

        # Continuacao: o opcode real e o do primeiro quadro.
        partes = [corpo]
        while True:
            seguinte = self._ler_quadro_cru()
            if seguinte is None:
                return None
            mais_fim, mais_op, mais_corpo = seguinte
            partes.append(mais_corpo)
            if mais_fim:
                break
            if sum(len(p) for p in partes) > _MAX_QUADRO:
                self.fechar(1009, "mensagem grande demais")
                return None
        return opcode, b"".join(partes)

    def _ler_quadro_cru(self):
        """Um quadro sem juntar continuacao — (fim, opcode, dados)."""
        primeiro = self._ler_exato(2)
        if primeiro is None:
            return None
        fim = primeiro[0] & 0x80
        opcode = primeiro[0] & 0x0F
        mascarado = primeiro[1] & 0x80
        tamanho = primeiro[1] & 0x7F
        if tamanho == 126:
            extra = self._ler_exato(2)
            if extra is None:
                return None
            tamanho = struct.unpack("!H", extra)[0]
        elif tamanho == 127:
            extra = self._ler_exato(8)
            if extra is None:
                return None
            tamanho = struct.unpack("!Q", extra)[0]
        if tamanho > _MAX_QUADRO:
            return None
        mascara = self._ler_exato(4) if mascarado else None
        corpo = self._ler_exato(tamanho) if tamanho else b""
        if corpo is None:
            return None
        if mascara:
            corpo = bytes(b ^ mascara[i % 4] for i, b in enumerate(corpo))
        return fim, opcode, corpo

    def _ler_exato(self, quantos):
        """Exatamente N bytes, ou None.

        'recv' pode devolver menos do que se pediu — e devolve, com
        frequencia, num quadro que atravessa pacotes. Tratar o retorno
        curto como o quadro inteiro corrompe a mensagem seguinte, e o
        sintoma e uma conexao que funciona e de repente para.
        """
        if quantos <= 0:
            return b""
        pedacos = []
        faltam = quantos
        while faltam > 0:
            try:
                pedaco = self._conexao.recv(faltam)
            except (TimeoutError, OSError):
                return None
            if not pedaco:
                return None
            pedacos.append(pedaco)
            faltam -= len(pedaco)
        return b"".join(pedacos)


class Sala:
    """Um grupo de soquetes, para mandar a todos.

    O que um chat, um painel compartilhado e uma notificacao precisam. A
    trava protege a lista, e o envio a um soquete morto o REMOVE em vez
    de levantar — um cliente que fechou a aba nao pode derrubar a
    mensagem dos outros.
    """

    def __init__(self, nome="sala"):
        import threading

        self.nome = nome
        self._membros = []
        self._trava = threading.RLock()

    def entrar(self, soquete):
        with self._trava:
            self._membros.append(soquete)
        return len(self._membros)

    def sair(self, soquete):
        with self._trava:
            if soquete in self._membros:
                self._membros.remove(soquete)
        return len(self._membros)

    def quantos(self):
        with self._trava:
            return len(self._membros)

    def transmitir(self, mensagem, exceto=None):
        """Manda a todos. Devolve para quantos chegou."""
        with self._trava:
            alvos = [s for s in self._membros if s is not exceto]
        chegou = 0
        mortos = []
        for soquete in alvos:
            if soquete.aberto and soquete.enviar(mensagem):
                chegou += 1
            else:
                mortos.append(soquete)
        for morto in mortos:
            self.sair(morto)
        return chegou

    def fechar_todos(self, motivo="servidor encerrando"):
        with self._trava:
            alvos = list(self._membros)
            self._membros.clear()
        for soquete in alvos:
            soquete.fechar(1001, motivo)
        return len(alvos)


def _serializavel(valor):
    """O que o `json` nao conhece vira texto, em vez de derrubar a rota."""
    if isinstance(valor, dict):
        return {str(k): _serializavel(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_serializavel(v) for v in valor]
    if isinstance(valor, (str, int, float, bool)) or valor is None:
        return valor
    if hasattr(valor, "fields"):
        return _serializavel(dict(valor.fields))
    return str(valor)
