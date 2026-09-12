"""
Kiln — o framework web do DataForge

No forno (kiln) a peca ganha a forma final. Aqui a requisicao entra
crua e sai como resposta.

    adopt Kiln

    app := Kiln.forge("minha-api")

    Kiln.get(app, "/", lambda req => Kiln.html("<h1>Ola</h1>"))
    Kiln.listen(app, 8080)

Ha tambem sintaxe propria na linguagem — 'server', 'route', 'respond' —
que compila para estas mesmas chamadas. Veja doc/KILN.md.

Sem dependencia externa: http.server da biblioteca padrao do Python,
com roteamento, middleware, sessao e templates escritos aqui.
"""

import gzip
import hashlib
import html as _html
import json
import mimetypes
import os
import re
import socket
import threading
import time
import traceback
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ─────────────────────────────────────────────────────────────
#  Requisicao e resposta
# ─────────────────────────────────────────────────────────────

#: Metodos que o roteador reconhece.
METODOS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")

#: Texto de cada status, para a linha de resposta.
RAZOES = {
    200: "OK", 201: "Created", 202: "Accepted", 204: "No Content",
    301: "Moved Permanently", 302: "Found", 304: "Not Modified",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
    404: "Not Found", 405: "Method Not Allowed", 409: "Conflict",
    413: "Payload Too Large", 415: "Unsupported Media Type",
    422: "Unprocessable Entity", 429: "Too Many Requests",
    500: "Internal Server Error", 502: "Bad Gateway",
    503: "Service Unavailable",
}


class Requisicao(dict):
    """O que chegou.

    E um dict para o DataForge poder ler com req["path"], mas tambem
    expoe os campos como atributo para o codigo Python interno.
    """

    def __init__(self, metodo, caminho, cabecalhos, corpo_bruto, cliente):
        partes = urllib.parse.urlsplit(caminho)
        consulta = {}
        for chave, valores in urllib.parse.parse_qs(
                partes.query, keep_blank_values=True).items():
            # ?tag=a&tag=b vira lista; ?nome=x vira string. E o que
            # quem escreve espera — obrigar a indexar [0] sempre seria
            # ruido em 95% dos casos.
            consulta[chave] = valores[0] if len(valores) == 1 else valores

        super().__init__({
            "method": metodo,
            "path": urllib.parse.unquote(partes.path),
            "query": consulta,
            "headers": cabecalhos,
            "params": {},
            "body": _interpretar_corpo(corpo_bruto, cabecalhos),
            "raw_body": corpo_bruto,
            "files": {},
            "cookies": _ler_cookies(cabecalhos.get("cookie", "")),
            "ip": cliente,
            "session": {},
            "state": {},          # espaco para o middleware guardar coisas
        })
        # Os arquivos de um 'multipart' vao para 'files', e nao ficam
        # misturados aos campos: 'req["files"]["foto"]' e explicito, e
        # um 'for' sobre 'body' nao topa com bytes onde espera texto.
        corpo = self["body"]
        if isinstance(corpo, dict) and "__arquivos__" in corpo:
            self["files"] = corpo.pop("__arquivos__")

    def __getattr__(self, nome):
        try:
            return self[nome]
        except KeyError:
            raise AttributeError(nome)


def _interpretar_corpo(bruto, cabecalhos):
    """Interpreta o corpo pelo Content-Type, sem estourar.

    JSON invalido vira o texto cru, nao uma excecao: o handler decide se
    isso e erro. Estourar aqui daria 500 onde o certo e 400.
    """
    if not bruto:
        return None
    tipo = (cabecalhos.get("content-type") or "").split(";")[0].strip().lower()
    texto = bruto.decode("utf-8", errors="replace")

    if tipo == "application/json":
        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            return texto
    if tipo == "application/x-www-form-urlencoded":
        return {k: v[0] if len(v) == 1 else v
                for k, v in urllib.parse.parse_qs(texto).items()}
    if tipo == "multipart/form-data":
        # Um '<input type="file">' chegava aqui como texto ilegivel, e
        # com isso toda tela que recebe planilha, foto ou documento
        # ficava de fora do framework.
        from .kiln_tempo_real import interpretar_multipart
        partes = interpretar_multipart(
            bruto, cabecalhos.get("content-type", ""))
        if partes is not None:
            # Os campos ficam no nivel de cima, como num formulario
            # comum: quem escreve le 'body["nome"]' sem saber se o
            # formulario tinha arquivo. Os arquivos, a parte.
            corpo = dict(partes["campos"])
            corpo["__arquivos__"] = partes["arquivos"]
            return corpo
    return texto


def _ler_cookies(cabecalho):
    cookies = {}
    for parte in cabecalho.split(";"):
        if "=" in parte:
            chave, _, valor = parte.partition("=")
            cookies[chave.strip()] = urllib.parse.unquote(valor.strip())
    return cookies


def resposta(corpo="", status=200, cabecalhos=None, tipo=None):
    """Uma resposta. E um dict para o DataForge montar a mao se quiser."""
    return {
        "__kiln__": True,
        "status": int(status),
        "headers": dict(cabecalhos or {}),
        "body": corpo,
        "content_type": tipo,
        "cookies": [],
    }


# ─────────────────────────────────────────────────────────────
#  Roteamento
# ─────────────────────────────────────────────────────────────

class Rota:
    """Um padrao de caminho, compilado.

        /users/:id        casa /users/42        -> {"id": "42"}
        /files/*caminho   casa /files/a/b.txt   -> {"caminho": "a/b.txt"}
    """

    __slots__ = ("metodo", "padrao", "handler", "regex", "nomes", "meio")

    def __init__(self, metodo, padrao, handler=None, meio=()):
        self.metodo = metodo.upper()
        self.padrao = padrao
        self.handler = handler
        self.meio = list(meio)
        self.regex, self.nomes = self._compilar(padrao)

    @staticmethod
    def _compilar(padrao):
        nomes = []
        partes = ["^"]
        for pedaco in re.split(r"(:[A-Za-z_]\w*|\*[A-Za-z_]\w*)", padrao):
            if pedaco.startswith(":"):
                nomes.append(pedaco[1:])
                partes.append(r"([^/]+)")
            elif pedaco.startswith("*"):
                nomes.append(pedaco[1:])
                partes.append(r"(.*)")
            else:
                partes.append(re.escape(pedaco))
        partes.append("/?$")
        return re.compile("".join(partes)), nomes

    def casa(self, caminho):
        """Devolve os parametros, ou None."""
        achado = self.regex.match(caminho)
        if achado is None:
            return None
        return {nome: urllib.parse.unquote(valor)
                for nome, valor in zip(self.nomes, achado.groups())}

    def __repr__(self):
        return f"<rota {self.metodo} {self.padrao}>"


class App:
    """Uma aplicacao Kiln."""

    def __init__(self, nome="kiln"):
        self.nome = nome
        self.rotas = []
        self.middleware = []            # roda antes do handler
        self.depois = []                # roda depois, com a resposta
        self.estaticos = []             # [(prefixo, pasta)]
        self.tratadores = {}            # status -> handler
        self.pasta_templates = None
        self.sessoes = {}               # id -> dict
        self.config = {}
        self.servidor = None
        self._contador = {"pedidos": 0, "erros": 0, "inicio": time.time()}

    # ── Registro ──

    def rota(self, metodo, padrao, handler, meio=()):
        self.rotas.append(Rota(metodo, padrao, handler, meio))
        return self

    def usar(self, funcao):
        self.middleware.append(funcao)
        return self

    def apos(self, funcao):
        self.depois.append(funcao)
        return self

    def montar(self, prefixo, outro):
        """Junta as rotas de outro app sob um prefixo."""
        limpo = "/" + prefixo.strip("/")
        for r in outro.rotas:
            caminho = (limpo + r.padrao).replace("//", "/")
            self.rotas.append(Rota(r.metodo, caminho, r.handler, r.meio))
        self.middleware.extend(outro.middleware)
        return self

    def erro(self, status, handler):
        self.tratadores[int(status)] = handler
        return self

    # ── Resolucao ──

    def achar(self, metodo, caminho):
        """Devolve (rota, params). Rota None quando nao casa.

        Distingue 404 de 405: se o caminho casa com outro metodo, o
        cliente errou o verbo, e dizer isso poupa depuracao.
        """
        outros_metodos = set()
        for r in self.rotas:
            params = r.casa(caminho)
            if params is None:
                continue
            if r.metodo == metodo or r.metodo == "*":
                return r, params
            outros_metodos.add(r.metodo)
        return None, outros_metodos


# ─────────────────────────────────────────────────────────────
#  Servidor
# ─────────────────────────────────────────────────────────────

class _Handler(BaseHTTPRequestHandler):
    """Ponte entre o http.server e o App."""

    app = None
    server_version = "Kiln"
    sys_version = ""

    def log_message(self, formato, *args):
        pass        # o log e do middleware, nao do http.server

    def _atender(self, metodo):
        app = self.app
        app._contador["pedidos"] += 1
        inicio = time.perf_counter()

        # WebSocket: o handshake e HTTP com 'Upgrade', e depois dele o
        # socket e nosso. Vem antes de tudo porque nao ha corpo a ler e
        # a resposta nao e uma resposta HTTP comum.
        from .kiln_tempo_real import e_pedido_de_upgrade
        cabs_cru = {k.lower(): v for k, v in self.headers.items()}
        if metodo == "GET" and e_pedido_de_upgrade(cabs_cru):
            self._atender_ws(cabs_cru)
            return

        try:
            tamanho = int(self.headers.get("content-length") or 0)
        except ValueError:
            tamanho = 0
        # Um corpo grande demais e recusado antes de ser lido inteiro na
        # memoria: sem isso, um POST de 2 GB derruba o processo.
        limite = app.config.get("limite_corpo", 10 * 1024 * 1024)
        if tamanho > limite:
            self._enviar(resposta(
                {"erro": f"corpo acima do limite de {limite} bytes"}, 413))
            return
        bruto = self.rfile.read(tamanho) if tamanho else b""

        cabecalhos = {k.lower(): v for k, v in self.headers.items()}
        req = Requisicao(metodo, self.path, cabecalhos, bruto,
                         self.client_address[0])
        _ligar_sessao(app, req)

        try:
            resp = _processar(app, req)
        except Exception as erro:
            app._contador["erros"] += 1
            resp = _resposta_de_erro(app, req, erro)

        for depois in app.depois:
            try:
                trocada = depois(req, resp)
                if isinstance(trocada, dict) and trocada.get("__kiln__"):
                    resp = trocada
            except Exception:
                pass        # middleware de saida nao pode derrubar a resposta

        resp["headers"].setdefault(
            "X-Response-Time",
            f"{(time.perf_counter() - inicio) * 1000:.1f}ms")

        if resp.get("__fluxo__") is not None:
            self._enviar_fluxo(resp)
            return
        self._enviar(resp)

    # ── Uma resposta que nao termina ────────────────────────

    def _enviar_fluxo(self, resp):
        """SSE: manda os cabecalhos e entrega a escrita ao gerador.

        Sem 'Content-Length' — nao se sabe quanto vem — e por isso a
        conexao nao pode ser reaproveitada depois. 'Connection: close'
        diz isso ao cliente em vez de deixa-lo esperando.
        """
        from .kiln_tempo_real import Fluxo

        self.send_response(int(resp.get("status", 200)),
                           RAZOES.get(int(resp.get("status", 200)), ""))
        self.send_header("Content-Type",
                         resp.get("content_type", "text/event-stream"))
        for chave, valor in resp.get("headers", {}).items():
            if chave.lower() != "content-length":
                self.send_header(chave, str(valor))
        for cookie in resp.get("cookies", []):
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

        fluxo = Fluxo(self.wfile)
        try:
            resp["__fluxo__"](fluxo)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass        # o cliente fechou a aba
        except Exception as erro:      # noqa: BLE001
            # Um erro aqui nao pode virar 500: os cabecalhos ja foram.
            # O evento 'erro' e o unico canal que sobra.
            try:
                fluxo.enviar({"erro": str(erro)}, tipo="erro")
            except Exception:
                pass
        finally:
            fluxo.fechar()
        self.close_connection = True

    # ── WebSocket ───────────────────────────────────────────

    def _atender_ws(self, cabecalhos):
        """Faz o handshake e chama o handler com um 'Soquete'."""
        from .kiln_tempo_real import Soquete, chave_de_resposta

        app = self.app
        chave = cabecalhos.get("sec-websocket-key", "")
        if not chave:
            self._enviar(resposta(
                {"erro": "falta o cabecalho Sec-WebSocket-Key"}, 400))
            return

        req = Requisicao("GET", self.path, cabecalhos, b"",
                         self.client_address[0])
        _ligar_sessao(app, req)
        rota, params = app.achar("WS", req["path"])
        if rota is None:
            # Sem rota de WebSocket neste caminho, a resposta certa e
            # 404 HTTP — o handshake nem comeca.
            self._enviar(resposta({"erro": "nao ha WebSocket aqui"}, 404))
            return
        req["params"] = params

        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", chave_de_resposta(chave))
        self.end_headers()

        soquete = Soquete(self.connection)
        app._contador.setdefault("ws", 0)
        app._contador["ws"] += 1
        try:
            rota.handler(req, soquete)
        except Exception as erro:      # noqa: BLE001
            app._contador["erros"] += 1
            if not app.config.get("producao"):
                print(f"  [kiln:ws] {type(erro).__name__}: {erro}")
        finally:
            soquete.fechar(1000, "fim")
        self.close_connection = True

    def _enviar(self, resp):
        dados, tipo = _serializar(resp.get("body", ""),
                                  resp.get("content_type"))

        status = int(resp.get("status", 200))
        self.send_response(status, RAZOES.get(status, ""))
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        for chave, valor in resp.get("headers", {}).items():
            self.send_header(chave, str(valor))
        for cookie in resp.get("cookies", []):
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

        if self.command != "HEAD":
            try:
                self.wfile.write(dados)
            except (BrokenPipeError, ConnectionResetError):
                pass        # o cliente desistiu; nao e erro nosso


for _metodo in METODOS:
    setattr(_Handler, f"do_{_metodo}",
            lambda self, _m=_metodo: self._atender(_m))


def _processar(app, req):
    """Middleware, rota estatica, rota casada — nessa ordem.

    A resposta passa por '_aplicar_cors' na saida: um cabecalho que so
    aparece no preflight nao serve para nada (ver a funcao).
    """
    return _aplicar_cors(req, _rotear(app, req))


def _aplicar_cors(req, resp):
    """O 'Access-Control-Allow-Origin' na resposta REAL.

    'Kiln.cors()' respondia o preflight e escrevia
    'req["state"]["cors"]' — que NINGUEM LIA. O navegador aprovava o
    preflight e entao bloqueava o 'fetch', porque a resposta do GET nao
    trazia o cabecalho.

    O sintoma e o pior possivel: o servidor responde 200 com o corpo
    certo, o 'curl' funciona, e so o navegador recusa — com uma
    mensagem no console sobre CORS que manda a pessoa mexer no
    middleware que ela ja pos.

    'setdefault': uma rota que declarou a propria origem manda mais que
    o middleware.
    """
    origem = (req.get("state") or {}).get("cors")
    if origem and isinstance(resp, dict) and "headers" in resp:
        resp["headers"].setdefault("Access-Control-Allow-Origin", origem)
        if origem != "*":
            # Com origem especifica, o cache intermediario precisa saber
            # que a resposta VARIA por 'Origin' — senao ele serve a de
            # um site para outro.
            anterior = resp["headers"].get("Vary", "")
            if "origin" not in anterior.lower():
                resp["headers"]["Vary"] = (
                    f"{anterior}, Origin" if anterior else "Origin")
    return resp


def _rotear(app, req):
    for meio in app.middleware:
        saida = meio(req)
        # Middleware que devolve resposta interrompe a cadeia: e assim
        # que autenticacao e limite de taxa cortam o pedido.
        if isinstance(saida, dict) and saida.get("__kiln__"):
            return saida

    estatica = _servir_estatico(app, req["path"])
    if estatica is not None:
        return estatica

    rota, extra = app.achar(req["method"], req["path"])

    if rota is None:
        if extra:       # o caminho existe, o verbo nao
            permitidos = ", ".join(sorted(extra))
            return _erro(app, req, 405,
                         f"{req['method']} não é aceito em {req['path']}",
                         {"Allow": permitidos})
        return _erro(app, req, 404, f"nada em {req['path']}")

    req["params"] = extra
    for meio in rota.meio:
        saida = meio(req)
        if isinstance(saida, dict) and saida.get("__kiln__"):
            return saida

    return _normalizar(rota.handler(req))


def _normalizar(saida):
    """O que o handler devolveu vira uma resposta."""
    if isinstance(saida, dict) and saida.get("__kiln__"):
        return saida
    if saida is None:
        return resposta("", 204)
    return resposta(saida)


def _erro(app, req, status, mensagem, cabecalhos=None):
    tratador = app.tratadores.get(status)
    if tratador is not None:
        try:
            return _normalizar(tratador(req))
        except Exception:
            pass
    corpo = {"erro": mensagem, "status": status}
    return resposta(corpo, status, cabecalhos)


def _resposta_de_erro(app, req, erro):
    """500 com o detalhe no terminal — e no corpo, se em modo debug."""
    mensagem = getattr(erro, "message", None) or str(erro)
    print(f"\033[1;31m[kiln] {req['method']} {req['path']} → 500\033[0m "
          f"{mensagem}")
    if app.config.get("debug"):
        traceback.print_exc()

    tratador = app.tratadores.get(500)
    if tratador is not None:
        try:
            req["state"]["erro"] = mensagem
            return _normalizar(tratador(req))
        except Exception:
            pass

    corpo = {"erro": "erro interno", "status": 500}
    if app.config.get("debug"):
        corpo["detalhe"] = mensagem
    return resposta(corpo, 500)


def _servir_estatico(app, caminho):
    for prefixo, pasta in app.estaticos:
        if not caminho.startswith(prefixo):
            continue
        relativo = caminho[len(prefixo):].lstrip("/")
        base = os.path.abspath(pasta)
        alvo = os.path.abspath(os.path.join(base, relativo))
        # Um '../' no caminho nao pode escapar da pasta servida.
        if not alvo.startswith(base + os.sep) and alvo != base:
            return resposta({"erro": "caminho inválido"}, 403)
        if os.path.isdir(alvo):
            alvo = os.path.join(alvo, "index.html")
        if not os.path.isfile(alvo):
            continue
        tipo, _ = mimetypes.guess_type(alvo)
        with open(alvo, "rb") as f:
            return resposta(f.read(), 200,
                            {"Cache-Control": "public, max-age=3600"},
                            tipo or "application/octet-stream")
    return None


# ── Sessao ──

def _ligar_sessao(app, req):
    """Sessao em memoria, identificada por cookie.

    Some quando o processo reinicia — e o certo para desenvolvimento e
    para app de um processo so. Producao com varios processos precisa de
    um armazenamento compartilhado.
    """
    sid = req["cookies"].get("kiln_sid")
    if sid and sid in app.sessoes:
        req["session"] = app.sessoes[sid]
        req["state"]["sid"] = sid
    else:
        req["session"] = {}
        req["state"]["sid"] = None


# ─────────────────────────────────────────────────────────────
#  Templates
# ─────────────────────────────────────────────────────────────

def _render(app, nome, dados=None):
    """Renderiza um template do disco.

    Sintaxe pequena de proposito: {{var}}, {{#lista}}…{{/lista}},
    {{^vazio}}…{{/vazio}}. Template que vira linguagem e codigo
    escondido onde ninguem procura.
    """
    if not app.pasta_templates:
        raise ValueError("nenhuma pasta de templates: use Kiln.templates(app, pasta)")
    caminho = os.path.join(app.pasta_templates, nome)
    if not os.path.isfile(caminho):
        raise FileNotFoundError(f"template não encontrado: {nome}")
    with open(caminho, encoding="utf-8") as f:
        return _preencher(f.read(), dados or {})


def _preencher(texto, dados):
    saida, i = [], 0
    while i < len(texto):
        abre = texto.find("{{", i)
        if abre == -1:
            saida.append(texto[i:])
            break
        saida.append(texto[i:abre])
        fecha = texto.find("}}", abre)
        if fecha == -1:
            saida.append(texto[abre:])
            break

        marca = texto[abre + 2:fecha].strip()

        if marca.startswith("#") or marca.startswith("^"):
            negado = marca[0] == "^"
            nome = marca[1:].strip()
            final = texto.find("{{/" + nome + "}}", fecha)
            if final == -1:
                raise ValueError(f"bloco '{nome}' aberto e nunca fechado")
            corpo = texto[fecha + 2:final]
            valor = _buscar(dados, nome)
            if negado:
                if not _tem_conteudo(valor):
                    saida.append(_preencher(corpo, dados))
            elif isinstance(valor, list):
                for item in valor:
                    contexto = item if isinstance(item, dict) else dados
                    trecho = corpo.replace("{{.}}", _escapar(item)) \
                        if not isinstance(item, dict) else corpo
                    saida.append(_preencher(trecho, contexto))
            elif _tem_conteudo(valor):
                contexto = valor if isinstance(valor, dict) else dados
                saida.append(_preencher(corpo, contexto))
            i = final + len(nome) + 5
            continue

        # {{& x}} nao escapa; {{x}} escapa
        if marca.startswith("&"):
            saida.append(str(_buscar(dados, marca[1:].strip()) or ""))
        else:
            saida.append(_escapar(_buscar(dados, marca)))
        i = fecha + 2
    return "".join(saida)


def _buscar(dados, caminho):
    if caminho == ".":
        return dados
    atual = dados
    for parte in caminho.split("."):
        if isinstance(atual, dict):
            atual = atual.get(parte)
        elif isinstance(atual, list) and parte.isdigit():
            indice = int(parte)
            atual = atual[indice] if indice < len(atual) else None
        else:
            return None
        if atual is None:
            return None
    return atual


def _escapar(valor):
    if valor is None:
        return ""
    return _html.escape(str(valor), quote=True)


def _tem_conteudo(valor):
    if valor is None or valor is False:
        return False
    if isinstance(valor, (list, dict, str)):
        return len(valor) > 0
    if isinstance(valor, (int, float)):
        return valor != 0
    return True


# ─────────────────────────────────────────────────────────────
#  Sessao com assinatura
# ─────────────────────────────────────────────────────────────

import base64
import hashlib
import hmac
import secrets


def _serializar(corpo, tipo=None):
    """(bytes, content-type) de um corpo de resposta.

    Existe porque DOIS lugares precisam da mesma decisao: o envio pelo
    socket e a compressao, que precisa dos bytes finais para saber se
    vale a pena e para troca-los. Duplicar a regra faria a compressao
    ver um corpo diferente do que sai na rede — e um 'Content-Length'
    que nao bate trava o navegador esperando bytes que nao vem.
    """
    if isinstance(corpo, (dict, list)) or corpo is None:
        return (json.dumps(corpo, ensure_ascii=False, default=str,
                           indent=2).encode("utf-8"),
                tipo or "application/json; charset=utf-8")
    if isinstance(corpo, (bytes, bytearray)):
        return bytes(corpo), tipo or "application/octet-stream"
    texto = str(corpo)
    if tipo is None:
        tipo = ("text/html; charset=utf-8" if texto.lstrip()[:1] == "<"
                else "text/plain; charset=utf-8")
    return texto.encode("utf-8"), tipo


def _inteiro(valor, padrao=0):
    """Um inteiro vindo de fora, ou o padrao. Nunca levanta."""
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return padrao


def _campo(item, nome):
    """O campo, venha ele de vault, record ou instancia."""
    if isinstance(item, dict):
        return item.get(nome)
    return getattr(item, nome, None)


def _chave_ordenavel(item, campo):
    """Uma chave que nunca estoura ao comparar tipos diferentes.

    'sorted' levanta quando a lista mistura None com texto, ou texto
    com numero — e uma lista vinda de banco mistura o tempo todo. O par
    (categoria, valor) ordena entre categorias primeiro, e so entao
    dentro delas.
    """
    valor = _campo(item, campo)
    if valor is None:
        return (0, "")
    if isinstance(valor, bool):
        return (1, int(valor))
    if isinstance(valor, (int, float)):
        return (1, valor)
    return (2, str(valor).lower())


def _etag(corpo):
    """Uma etiqueta estavel para o conteudo.

    Aspas e W/ fazem parte do formato: sem elas o navegador ignora o
    cabecalho em silencio, e o 304 nunca acontece.
    """
    bruto = corpo if isinstance(corpo, (bytes, bytearray)) else \
        json.dumps(corpo, sort_keys=True, default=str).encode() \
        if isinstance(corpo, (dict, list)) else str(corpo).encode()
    return 'W/"' + hashlib.sha256(bruto).hexdigest()[:24] + '"'


#: Os tipos que 'Kiln.validar' conhece, e como cada um confere.
_TIPOS_VALIDOS = {
    "texto": lambda v: isinstance(v, str),
    "inteiro": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "numero": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "booleano": lambda v: isinstance(v, bool),
    "lista": lambda v: isinstance(v, list),
    "vault": lambda v: isinstance(v, dict),
    "email": lambda v: isinstance(v, str) and
                       re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$", v) is not None,
}


def _conferir_esquema(dados, esquema):
    """Todos os problemas de uma vez — nao so o primeiro.

    Devolver um erro por envio faz quem preenche descobrir os cinco
    problemas em cinco tentativas, e a maioria desiste no terceiro.
    """
    problemas = {}
    for campo, regra in (esquema or {}).items():
        regra = regra if isinstance(regra, dict) else {"tipo": str(regra)}
        presente = campo in dados and dados[campo] not in (None, "")
        if not presente:
            if regra.get("obrigatorio"):
                problemas[campo] = "obrigatório"
            continue

        valor = dados[campo]
        tipo = regra.get("tipo")
        if tipo and tipo in _TIPOS_VALIDOS and not _TIPOS_VALIDOS[tipo](valor):
            problemas[campo] = f"esperava {tipo}"
            continue

        tamanho = len(valor) if isinstance(valor, (str, list, dict)) else valor
        if "min" in regra and isinstance(tamanho, (int, float)) \
                and tamanho < regra["min"]:
            problemas[campo] = f"mínimo {regra['min']}"
        elif "max" in regra and isinstance(tamanho, (int, float)) \
                and tamanho > regra["max"]:
            problemas[campo] = f"máximo {regra['max']}"
        elif "em" in regra and valor not in regra["em"]:
            problemas[campo] = "valor fora da lista permitida"
        elif "padrao" in regra and isinstance(valor, str) \
                and re.match(regra["padrao"], valor) is None:
            problemas[campo] = "formato inválido"
    return problemas


def _assinar(dados, segredo):
    corpo = base64.urlsafe_b64encode(
        json.dumps(dados, default=str).encode()).decode().rstrip("=")
    marca = hmac.new(segredo.encode(), corpo.encode(),
                     hashlib.sha256).hexdigest()[:32]
    return f"{corpo}.{marca}"


def _conferir(token, segredo):
    """Le um token assinado. Devolve None se foi adulterado."""
    if not token or "." not in token:
        return None
    corpo, _, marca = token.rpartition(".")
    esperado = hmac.new(segredo.encode(), corpo.encode(),
                        hashlib.sha256).hexdigest()[:32]
    # compare_digest para o tempo de comparacao nao vazar o prefixo certo
    if not hmac.compare_digest(marca, esperado):
        return None
    try:
        preenchido = corpo + "=" * (-len(corpo) % 4)
        return json.loads(base64.urlsafe_b64decode(preenchido))
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
#  Modulo Kiln para o DataForge
# ─────────────────────────────────────────────────────────────

def _apenas_dict(valor):
    """Converte estruturas do DataForge em algo serializavel."""
    if hasattr(valor, "campos") and hasattr(valor, "blueprint"):
        return dict(valor.campos)
    if hasattr(valor, "_asdict"):
        return valor._asdict()
    if isinstance(valor, dict):
        return {k: _apenas_dict(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_apenas_dict(v) for v in valor]
    return valor


def _classe_sala():
    """A classe 'Sala', para quem preferir 'spawn Kiln.Sala("chat")'."""
    from .kiln_tempo_real import Sala
    return Sala


class ArcaneKiln:
    """Kiln — framework web do DataForge."""

    # ── aplicacao ──

    @staticmethod
    def _forge(nome="kiln", **config):
        app = App(nome)
        app.config.update(config)
        return app

    @staticmethod
    def _config(app, chave, valor):
        app.config[chave] = valor
        return app

    # ── rotas ──

    @staticmethod
    def _rota(app, metodo, padrao, handler):
        return app.rota(metodo, padrao, handler)

    @staticmethod
    def _get(app, padrao, handler):
        return app.rota("GET", padrao, handler)

    @staticmethod
    def _post(app, padrao, handler):
        return app.rota("POST", padrao, handler)

    @staticmethod
    def _put(app, padrao, handler):
        return app.rota("PUT", padrao, handler)

    @staticmethod
    def _patch(app, padrao, handler):
        return app.rota("PATCH", padrao, handler)

    @staticmethod
    def _delete(app, padrao, handler):
        return app.rota("DELETE", padrao, handler)

    @staticmethod
    def _options(app, padrao, handler):
        return app.rota("OPTIONS", padrao, handler)

    @staticmethod
    def _head(app, padrao, handler):
        return app.rota("HEAD", padrao, handler)

    @staticmethod
    def _any(app, padrao, handler):
        return app.rota("*", padrao, handler)

    @staticmethod
    def _resource(app, base, controlador):
        """Sete rotas RESTful de uma vez.

        index/show/create/update/patch/destroy — os que o controlador
        (um vault) tiver. Os que faltarem simplesmente nao existem.
        """
        base = "/" + base.strip("/")
        mapa = [
            ("GET", base, "index"),
            ("GET", f"{base}/:id", "show"),
            ("POST", base, "create"),
            ("PUT", f"{base}/:id", "update"),
            ("PATCH", f"{base}/:id", "patch"),
            ("DELETE", f"{base}/:id", "destroy"),
        ]
        for metodo, caminho, nome in mapa:
            handler = controlador.get(nome) if isinstance(controlador, dict) \
                else getattr(controlador, nome, None)
            if handler is not None:
                app.rota(metodo, caminho, handler)
        return app

    @staticmethod
    def _mount(app, prefixo, outro):
        return app.montar(prefixo, outro)

    @staticmethod
    def _group(app, prefixo, meio=None):
        """Sub-app: rotas registradas nele herdam prefixo e middleware."""
        filho = App(f"{app.nome}{prefixo}")
        if meio:
            filho.middleware.extend(meio if isinstance(meio, list) else [meio])
        filho.config = app.config
        filho.pasta_templates = app.pasta_templates
        app.config.setdefault("__grupos__", []).append((prefixo, filho))
        return filho

    @staticmethod
    def _routes(app):
        """Lista as rotas — util para depurar e para o comando 'kiln rotas'."""
        return [{"method": r.metodo, "path": r.padrao,
                 "params": list(r.nomes)} for r in app.rotas]

    # ── middleware ──

    @staticmethod
    def _use(app, funcao):
        return app.usar(funcao)

    @staticmethod
    def _after(app, funcao):
        return app.apos(funcao)

    @staticmethod
    def _on_error(app, status, handler):
        return app.erro(status, handler)

    @staticmethod
    def _cors(origens="*", metodos=None, cabecalhos=None):
        permitidos = metodos or "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        cabs = cabecalhos or "Content-Type, Authorization"

        def middleware(req):
            # OPTIONS e respondido aqui: o preflight nunca chega na rota.
            if req["method"] == "OPTIONS":
                return resposta("", 204, {
                    "Access-Control-Allow-Origin": origens,
                    "Access-Control-Allow-Methods": permitidos,
                    "Access-Control-Allow-Headers": cabs,
                    "Access-Control-Max-Age": "86400",
                })
            req["state"]["cors"] = origens
            return None
        return middleware

    @staticmethod
    def _logger(formato="dev"):
        def middleware(req):
            hora = time.strftime("%H:%M:%S")
            print(f"\033[2m{hora}\033[0m \033[1;36m{req['method']:<6}\033[0m "
                  f"{req['path']}")
            return None
        return middleware

    @staticmethod
    def _rate_limit(maximo=60, janela=60):
        """Limita pedidos por IP numa janela deslizante."""
        registro = {}
        trava = threading.Lock()

        def middleware(req):
            agora = time.time()
            ip = req["ip"]
            with trava:
                marcas = [t for t in registro.get(ip, []) if agora - t < janela]
                if len(marcas) >= maximo:
                    espera = int(janela - (agora - marcas[0])) + 1
                    return resposta(
                        {"erro": "pedidos demais", "tente_em": espera}, 429,
                        {"Retry-After": str(espera)})
                marcas.append(agora)
                registro[ip] = marcas
            return None
        return middleware

    @staticmethod
    def _auth(verificador, esquema="Bearer"):
        """Exige Authorization; 'verificador' recebe o token e devolve
        o usuario (ou void para recusar)."""
        def middleware(req):
            cabecalho = req["headers"].get("authorization", "")
            prefixo = esquema + " "
            if not cabecalho.startswith(prefixo):
                return resposta({"erro": "não autenticado"}, 401,
                                {"WWW-Authenticate": esquema})
            usuario = verificador(cabecalho[len(prefixo):])
            if usuario is None or usuario is False:
                return resposta({"erro": "credencial inválida"}, 401)
            req["state"]["user"] = usuario
            return None
        return middleware

    #: Os metodos que NAO mudam estado. O CSRF nao os cobra: exigir
    #: token num GET nao protege nada e quebra todo link do site.
    SEGUROS = ("GET", "HEAD", "OPTIONS", "TRACE")

    @staticmethod
    def _secure_headers(csp="default-src 'self'", hsts=False,
                        frame="DENY", referrer="strict-origin-when-cross-origin",
                        permissoes="geolocation=(), microphone=(), camera=()"):
        """Os cabecalhos que o navegador so respeita se voce mandar.

        Nenhum deles e ligado por padrao pelo servidor: sem estes, uma
        pagina do seu site pode ser posta num <iframe> de outro
        (clickjacking), e um .txt com HTML dentro pode ser executado
        como pagina (sniffing de tipo).

        HSTS fica DESLIGADO por padrao, e isso e deliberado. Ele diz ao
        navegador "so me acesse por https, pelos proximos meses" — e o
        navegador OBEDECE, mesmo que o https ainda nao exista. Mandado
        cedo demais, ele tira o site do ar para quem ja o visitou, e
        nao ha como voltar atras a tempo. Ligue quando o certificado
        estiver de pe.
        """
        cabecalhos = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": frame,
            "Referrer-Policy": referrer,
            "Content-Security-Policy": csp,
            "Permissions-Policy": permissoes,
        }
        if hsts:
            cabecalhos["Strict-Transport-Security"] = \
                "max-age=31536000; includeSubDomains"

        def depois(req, resp):
            # setdefault: a rota manda mais que o padrao. Uma pagina que
            # precisa ser embutida ja declarou o seu X-Frame-Options, e
            # sobrescreve-lo aqui quebraria justamente o caso pensado.
            for chave, valor in cabecalhos.items():
                resp["headers"].setdefault(chave, valor)
            return resp
        return depois

    @staticmethod
    def _csrf(segredo, campo="_csrf", cabecalho="X-CSRF-Token"):
        """Recusa POST/PUT/PATCH/DELETE sem um token que voce assinou.

        O ataque: voce esta logado no seu banco, abre outra aba num site
        qualquer, e um <form> escondido dela dispara um POST para o
        banco. O navegador manda o seu cookie junto — porque o cookie e
        do banco, e o pedido vai para o banco. Do lado do servidor, o
        pedido parece seu.

        O token quebra isso porque o site atacante nao consegue LE-LO:
        ele esta na sua pagina, e a politica de mesma origem impede que
        outro site a leia. Sem poder ler, nao ha como reenviar.

        A checagem e por assinatura HMAC, nao por sessao guardada: o
        servidor confere que ELE emitiu o token, sem precisar lembrar
        de cada um. E o que faz isto funcionar com varios processos.
        """
        def middleware(req):
            if req["method"] in ArcaneKiln.SEGUROS:
                return None
            # Os cabecalhos chegam em minusculas; o corpo e o que um
            # <form> comum manda, que nao consegue por cabecalho nenhum.
            cabs = req.get("headers") or {}
            enviado = cabs.get(cabecalho.lower()) or cabs.get(cabecalho)
            if not enviado:
                corpo = req.get("body")
                if isinstance(corpo, dict):
                    enviado = corpo.get(campo)
            if not enviado or _conferir(enviado, segredo) is None:
                return resposta(
                    {"erro": "token CSRF ausente ou inválido",
                     "dica": f"mande-o no cabeçalho '{cabecalho}' "
                             f"ou no campo '{campo}'"}, 403)
            return None
        return middleware

    @staticmethod
    def _csrf_token(req, segredo=None):
        """Um token para pôr no formulário ou no fetch.

        Ele carrega a hora de emissão: dois tokens seguidos são
        diferentes, e um vazamento em log não vale para sempre.
        """
        chave = segredo or req.get("state", {}).get("csrf_segredo")
        if chave is None:
            chave = req["state"].get("__csrf__")
        if chave is None:
            raise ValueError(
                "csrf_token precisa do segredo: use Kiln.csrf(segredo) "
                "como middleware, ou passe o segredo aqui")
        return _assinar({"t": int(time.time())}, chave)

    # ── validacao ───────────────────────────────────────────

    @staticmethod
    def _validar(esquema, alvo="body"):
        """Recusa o pedido que nao casa com o esquema, com 422.

            middleware Kiln.validar({
                "nome":  {"tipo": "texto", "obrigatorio": yes, "min": 2},
                "idade": {"tipo": "inteiro", "min": 0, "max": 130},
                "email": {"tipo": "email"},
            })

        Ele responde com TODOS os campos errados de uma vez, nao com o
        primeiro. Um formulario que corrige um erro por envio faz o
        usuario descobrir os cinco problemas em cinco tentativas — e a
        maioria desiste no terceiro.

        422 e nao 400: o corpo foi entendido (e JSON valido), o que
        falhou foi o CONTEUDO. Um cliente consegue distinguir "mandei
        lixo" de "faltou um campo".
        """
        def middleware(req):
            dados = req.get(alvo) or {}
            if not isinstance(dados, dict):
                return resposta({"erro": f"esperava um vault em '{alvo}'"}, 422)
            problemas = _conferir_esquema(dados, esquema)
            if problemas:
                return resposta(
                    {"erro": "dados inválidos", "campos": problemas}, 422)
            return None
        return middleware

    # ── paginacao, ordenacao e busca ────────────────────────

    @staticmethod
    def _paginar(itens, req=None, por_pagina=20, teto=100):
        """Uma fatia da lista, com o que o cliente precisa para navegar.

        Le 'pagina' e 'por_pagina' da query. O TETO existe porque
        'por_pagina' vem de fora: sem ele, '?por_pagina=1000000' e um
        pedido que derruba o servidor sem nenhuma ferramenta especial.
        """
        consulta = (req or {}).get("query", {}) or {}
        pagina = max(1, _inteiro(consulta.get("pagina"), 1))
        tamanho = min(teto, max(1, _inteiro(consulta.get("por_pagina"),
                                            por_pagina)))
        total = len(itens)
        paginas = max(1, -(-total // tamanho))     # divisao para cima
        inicio = (pagina - 1) * tamanho
        return {
            "itens": list(itens[inicio:inicio + tamanho]),
            "pagina": pagina,
            "por_pagina": tamanho,
            "total": total,
            "paginas": paginas,
            "tem_proxima": pagina < paginas,
            "tem_anterior": pagina > 1,
        }

    @staticmethod
    def _ordenar(itens, req=None, campos=None, padrao=""):
        """Ordena por '?ordenar=campo' ou '?ordenar=-campo' (descendente).

        A lista 'campos' NAO e conforto: sem ela, o cliente escolhe por
        qual campo ordenar, e isso inclui campos que voce nunca quis
        expor. Ordenar por 'senha_hash' revela a ordem deles.
        """
        pedido = ((req or {}).get("query", {}) or {}).get("ordenar") or padrao
        if not pedido:
            return list(itens)
        desc = pedido.startswith("-")
        campo = pedido.lstrip("-+")
        if campos is not None and campo not in campos:
            return list(itens)
        return sorted(itens, key=lambda i: _chave_ordenavel(i, campo),
                      reverse=desc)

    @staticmethod
    def _buscar(itens, req=None, campos=(), parametro="q"):
        """Filtra por '?q=texto', olhando os campos que voce indicar."""
        termo = (((req or {}).get("query", {}) or {}).get(parametro) or "").strip()
        if not termo:
            return list(itens)
        alvo = termo.lower()
        return [i for i in itens
                if any(alvo in str(_campo(i, c) or "").lower() for c in campos)]

    # ── identificacao e registro ────────────────────────────

    @staticmethod
    def _request_id(cabecalho="X-Request-Id"):
        """Um id por pedido, no estado e na resposta.

        Ele existe para juntar as pontas: a linha do log, o erro que o
        usuario viu e o pedido que o proxy registrou sao o mesmo evento,
        e sem um id comum ninguem prova isso depois.

        Um id que ja veio de fora e MANTIDO — o proxy na frente ja o
        gerou, e trocar quebra a corrente.
        """
        def middleware(req):
            cabs = req.get("headers") or {}
            atual = cabs.get(cabecalho.lower()) or cabs.get(cabecalho)
            req["state"]["request_id"] = atual or secrets.token_hex(8)
            return None

        def depois(req, resp):
            ident = req.get("state", {}).get("request_id")
            if ident:
                resp["headers"].setdefault(cabecalho, ident)
            return resp

        middleware.depois = depois
        return middleware

    @staticmethod
    def _audit(escrever=None, metodos=("POST", "PUT", "PATCH", "DELETE")):
        """Registra quem mudou o que, e quando.

        So os metodos que MUDAM estado. Auditar GET enche o registro de
        ruido e esconde justamente o que se procura numa investigacao.

        O corpo nao entra: ele carrega senha, cartao e token. Um log de
        auditoria que vaza credenciais e uma falha, nao um recurso.
        """
        registro = []

        def depois(req, resp):
            if req["method"] not in metodos:
                return resp
            linha = {
                "quando": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "metodo": req["method"],
                "caminho": req["path"],
                "status": resp["status"],
                "ip": req.get("ip", ""),
                "id": req.get("state", {}).get("request_id", ""),
                "quem": (req.get("session") or {}).get("usuario", ""),
            }
            if escrever is not None:
                escrever(linha)
            else:
                registro.append(linha)
            return resp

        depois.registro = registro
        return depois

    # ── cache e transferencia ───────────────────────────────

    @staticmethod
    def _cache(segundos=60, privado=False):
        """Cache-Control e ETag, com 304 quando nada mudou.

        O 304 e o que economiza banda de verdade: o servidor ainda
        calcula a resposta, mas nao a transmite. Para uma lista que o
        cliente pede a cada segundo, a diferenca e o tamanho do corpo.
        """
        escopo = "private" if privado else "public"

        def depois(req, resp):
            if req["method"] not in ("GET", "HEAD") or resp["status"] != 200:
                return resp
            resp["headers"].setdefault(
                "Cache-Control", f"{escopo}, max-age={int(segundos)}")
            etiqueta = resp["headers"].get("ETag") or _etag(resp["body"])
            resp["headers"].setdefault("ETag", etiqueta)
            cabs = req.get("headers") or {}
            if cabs.get("if-none-match") == etiqueta:
                return resposta("", 304, {"ETag": etiqueta,
                                          "Cache-Control": resp["headers"]["Cache-Control"]})
            return resp
        return depois

    @staticmethod
    def _comprimir(minimo=1024):
        """gzip quando o cliente aceita e o corpo compensa.

        Abaixo de ~1 KB comprimir custa mais do que economiza: o
        cabecalho do gzip sozinho tem 18 bytes, e a CPU dos dois lados
        nao e de graca. O minimo existe por isso.

        Nao mexe em imagem, video nem zip: eles ja estao comprimidos, e
        passar gzip por cima costuma AUMENTAR o tamanho.
        """
        def depois(req, resp):
            cabs = req.get("headers") or {}
            if "gzip" not in (cabs.get("accept-encoding") or ""):
                return resp
            if resp["headers"].get("Content-Encoding"):
                return resp
            # Serializa com a MESMA regra do envio: um vault vira JSON
            # aqui tambem. Sem isto, resposta de API — o caso mais comum
            # — nunca era comprimida, porque o corpo ainda era um vault
            # quando a decisao acontecia.
            corpo, tipo = _serializar(resp["body"], resp.get("content_type"))
            if len(corpo) < minimo:
                return resp
            if any(t in tipo for t in ("image/", "video/", "audio/", "zip",
                                       "gzip", "octet-stream")):
                return resp
            # O tipo precisa ficar FIXADO: o corpo agora e bytes, e sem
            # isto o envio o chamaria de 'octet-stream' e o navegador
            # baixaria o JSON em vez de o interpretar.
            resp["content_type"] = tipo
            resp["body"] = gzip.compress(corpo)
            resp["headers"]["Content-Encoding"] = "gzip"
            resp["headers"]["Vary"] = "Accept-Encoding"
            return resp
        return depois

    # ── limites ─────────────────────────────────────────────

    @staticmethod
    def _limite_de_corpo(bytes_maximos=1024 * 1024):
        """Recusa corpo grande demais, com 413.

        Sem teto, um POST de 2 GB e um jeito trivial de derrubar o
        processo — nao precisa de exploit, so de largura de banda. O
        padrao de 1 MB cobre formulario e JSON; upload de arquivo
        declara o seu proprio.
        """
        def middleware(req):
            bruto = req.get("raw_body") or b""
            declarado = _inteiro((req.get("headers") or {})
                                 .get("content-length"), len(bruto))
            if max(declarado, len(bruto)) > bytes_maximos:
                return resposta(
                    {"erro": "corpo grande demais",
                     "limite_bytes": int(bytes_maximos)}, 413)
            return None
        return middleware

    @staticmethod
    def _idempotente(janela=86400):
        """Repetir o pedido com a mesma 'Idempotency-Key' devolve o
        mesmo resultado, em vez de cobrar duas vezes.

        E o problema real de todo checkout: a resposta se perde na rede,
        o cliente reenvia, e a cobranca acontece de novo. A chave deixa
        o SERVIDOR reconhecer o reenvio — o cliente sozinho nao tem como.

        Fica em memoria: some se o processo reiniciar, e nao atravessa
        varios processos. Para valer de verdade, guarde num banco.
        """
        guardadas = {}
        trava = threading.Lock()

        def middleware(req):
            if req["method"] in ArcaneKiln.SEGUROS:
                return None
            chave = ((req.get("headers") or {}).get("idempotency-key") or
                     (req.get("headers") or {}).get("Idempotency-Key"))
            if not chave:
                return None
            agora = time.time()
            with trava:
                for k, (quando, _) in list(guardadas.items()):
                    if agora - quando > janela:
                        guardadas.pop(k, None)
                achado = guardadas.get(chave)
            if achado:
                repetida = dict(achado[1])
                repetida["headers"] = dict(repetida["headers"])
                repetida["headers"]["Idempotent-Replay"] = "true"
                return repetida
            req["state"]["idempotency_key"] = chave
            return None

        def depois(req, resp):
            chave = req.get("state", {}).get("idempotency_key")
            if chave and 200 <= resp["status"] < 300:
                with trava:
                    guardadas[chave] = (time.time(), resp)
            return resp

        middleware.depois = depois
        return middleware

    @staticmethod
    def _guard(condicao, status=403, mensagem="sem permissão"):
        """Middleware a partir de uma condicao qualquer."""
        def middleware(req):
            if not condicao(req):
                return resposta({"erro": mensagem}, int(status))
            return None
        return middleware

    # ── respostas ──

    @staticmethod
    def _json(dados, status=200, cabecalhos=None):
        return resposta(_apenas_dict(dados), int(status), cabecalhos,
                        "application/json; charset=utf-8")

    @staticmethod
    def _html(texto, status=200, cabecalhos=None):
        return resposta(texto, int(status), cabecalhos,
                        "text/html; charset=utf-8")

    @staticmethod
    def _text(texto, status=200, cabecalhos=None):
        return resposta(str(texto), int(status), cabecalhos,
                        "text/plain; charset=utf-8")

    @staticmethod
    def _status(codigo, mensagem=None):
        corpo = {"status": int(codigo),
                 "mensagem": mensagem or RAZOES.get(int(codigo), "")}
        return resposta(corpo, int(codigo))

    @staticmethod
    def _redirect(destino, status=302):
        return resposta("", int(status), {"Location": destino})

    @staticmethod
    def _file(caminho, tipo=None, baixar=None):
        if not os.path.isfile(caminho):
            return resposta({"erro": "arquivo não encontrado"}, 404)
        adivinhado, _ = mimetypes.guess_type(caminho)
        cabecalhos = {}
        if baixar:
            cabecalhos["Content-Disposition"] = f'attachment; filename="{baixar}"'
        with open(caminho, "rb") as f:
            return resposta(f.read(), 200, cabecalhos,
                            tipo or adivinhado or "application/octet-stream")

    @staticmethod
    def _header(resp, chave, valor):
        resp["headers"][chave] = str(valor)
        return resp

    @staticmethod
    def _cookie(resp, nome, valor, dias=None, http_only=True, caminho="/",
                same_site="Lax", seguro=False):
        partes = [f"{nome}={urllib.parse.quote(str(valor))}",
                  f"Path={caminho}", f"SameSite={same_site}"]
        if dias is not None:
            partes.append(f"Max-Age={int(float(dias) * 86400)}")
        if http_only:
            partes.append("HttpOnly")
        if seguro:
            partes.append("Secure")
        resp["cookies"].append("; ".join(partes))
        return resp

    # ── sessao ──

    @staticmethod
    def _session_start(app, req, resp, dados=None):
        sid = req["state"].get("sid") or secrets.token_urlsafe(24)
        app.sessoes[sid] = dict(dados or req.get("session") or {})
        req["session"] = app.sessoes[sid]
        req["state"]["sid"] = sid
        return ArcaneKiln._cookie(resp, "kiln_sid", sid, dias=7)

    @staticmethod
    def _session_end(app, req, resp):
        sid = req["state"].get("sid")
        if sid:
            app.sessoes.pop(sid, None)
        req["session"] = {}
        return ArcaneKiln._cookie(resp, "kiln_sid", "", dias=0)

    @staticmethod
    def _sign(dados, segredo):
        return _assinar(_apenas_dict(dados), segredo)

    @staticmethod
    def _unsign(token, segredo):
        return _conferir(token, segredo)

    # ── templates e estaticos ──

    @staticmethod
    def _templates(app, pasta):
        app.pasta_templates = pasta
        return app

    @staticmethod
    def _render(app, nome, dados=None, status=200):
        texto = _render(app, nome, _apenas_dict(dados or {}))
        return resposta(texto, int(status), None, "text/html; charset=utf-8")

    @staticmethod
    def _render_string(texto, dados=None):
        return _preencher(texto, _apenas_dict(dados or {}))

    @staticmethod
    def _static(app, prefixo, pasta):
        app.estaticos.append(("/" + prefixo.strip("/"), pasta))
        return app

    @staticmethod
    def _escape(texto):
        return _escapar(texto)

    # ── tempo real ──

    @staticmethod
    def _ws(app, padrao, handler):
        """Registra uma rota de WebSocket.

        O metodo e 'WS', que nao existe em HTTP: assim ela nao pode ser
        alcancada por um GET comum, e um GET no mesmo caminho continua
        livre para servir a pagina que abre a conexao.
        """
        return app.rota("WS", padrao, handler)

    @staticmethod
    def _sala(nome="sala"):
        """Um grupo de conexoes, para transmitir a todos."""
        from .kiln_tempo_real import Sala
        return Sala(nome)

    @staticmethod
    def _sse(gerador, cabecalhos=None):
        """Uma resposta SSE: o servidor empurra evento por evento.

            route GET "/fila":
                respond Kiln.sse(action (fluxo):
                    persist fluxo.aberto:
                        fluxo.enviar({"tamanho": tamanho_da_fila()})
                        wait 1
                )

        Prefira SSE a WebSocket quando o cliente so ouve: ele e HTTP
        comum, reconecta sozinho e passa em qualquer proxy.
        """
        from .kiln_tempo_real import resposta_de_fluxo
        return resposta_de_fluxo(gerador, cabecalhos)

    @staticmethod
    def _evento(dados, tipo="", identificador="", reconectar=0):
        """Um evento SSE em texto, para quem monta o fluxo a mao."""
        from .kiln_tempo_real import evento
        return evento(dados, tipo, identificador, reconectar)

    @staticmethod
    def _stream(gerador, tipo="text/plain; charset=utf-8", cabecalhos=None):
        """Uma resposta em pedacos, de qualquer tipo.

        Serve para exportar um CSV de um milhao de linhas sem montar o
        arquivo inteiro na memoria: cada pedaco sai enquanto o proximo e
        calculado.
        """
        from .kiln_tempo_real import resposta_de_fluxo
        resp = resposta_de_fluxo(gerador, cabecalhos)
        resp["content_type"] = tipo
        # Sem 'text/event-stream', nao e SSE: o 'no-transform' e o
        # 'X-Accel-Buffering' continuam valendo, mas o cliente nao vai
        # esperar o formato de evento.
        return resp

    # ── upload ──

    @staticmethod
    def _upload(req, campo):
        """Um arquivo enviado, ou `void`.

        O vault tem 'nome', 'tipo', 'tamanho', 'conteudo' (bytes) e
        'texto'.
        """
        return (req.get("files") or {}).get(campo)

    @staticmethod
    def _uploads(req):
        """Todos os arquivos enviados, por nome de campo."""
        return dict(req.get("files") or {})

    @staticmethod
    def _salvar_upload(arquivo, pasta, nome=None, limite=0, tipos=None):
        """Grava um arquivo recebido, recusando o que nao deveria entrar."""
        from .kiln_tempo_real import salvar_upload
        return salvar_upload(arquivo, pasta, nome, limite, tipos)

    # ── ciclo de vida ──

    @staticmethod
    def _listen(app, porta=8080, host="127.0.0.1", silencioso=False):
        """Sobe o servidor e bloqueia ate Ctrl-C."""
        for prefixo, filho in app.config.pop("__grupos__", []):
            app.montar(prefixo, filho)

        handler = type("KilnHandler", (_Handler,), {"app": app})
        servidor = ThreadingHTTPServer((host, int(porta)), handler)
        servidor.daemon_threads = True
        app.servidor = servidor

        if not silencioso:
            print(f"\n  \033[1;33m▲ Kiln\033[0m  {app.nome}")
            print(f"  \033[2mno ar em\033[0m  http://{host}:{int(porta)}")
            print(f"  \033[2m{len(app.rotas)} rota(s) · Ctrl-C para parar\033[0m\n")
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            if not silencioso:
                print("\n  \033[2mforno apagado.\033[0m")
        finally:
            servidor.server_close()
        return app

    @staticmethod
    def _serve(app, porta=8080, host="127.0.0.1"):
        """Sobe em segundo plano e devolve na hora. Devolve a porta real
        (util com porta 0, que deixa o SO escolher)."""
        for prefixo, filho in app.config.pop("__grupos__", []):
            app.montar(prefixo, filho)
        handler = type("KilnHandler", (_Handler,), {"app": app})
        servidor = ThreadingHTTPServer((host, int(porta)), handler)
        servidor.daemon_threads = True
        app.servidor = servidor
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        return servidor.server_address[1]

    @staticmethod
    def _stop(app):
        if app.servidor is not None:
            app.servidor.shutdown()
            app.servidor.server_close()
            app.servidor = None
        return app

    @staticmethod
    def _stats(app):
        return {
            "pedidos": app._contador["pedidos"],
            "erros": app._contador["erros"],
            "rotas": len(app.rotas),
            "uptime": round(time.time() - app._contador["inicio"], 1),
        }

    # ── cliente, para testar sem rede ──

    @staticmethod
    def _test(app, metodo, caminho, corpo=None, cabecalhos=None):
        """Executa um pedido direto no app, sem socket.

        Torna teste de rota tao barato quanto teste de funcao — que e o
        que faz alguem realmente escrever esses testes.
        """
        cabs = {k.lower(): v for k, v in (cabecalhos or {}).items()}
        bruto = b""
        if corpo is not None:
            if isinstance(corpo, (dict, list)):
                bruto = json.dumps(_apenas_dict(corpo)).encode()
                cabs.setdefault("content-type", "application/json")
            else:
                bruto = str(corpo).encode()
        req = Requisicao(metodo.upper(), caminho, cabs, bruto, "127.0.0.1")
        _ligar_sessao(app, req)
        try:
            resp = _processar(app, req)
        except Exception as erro:
            resp = _resposta_de_erro(app, req, erro)

        # A cadeia de saida tambem. Sem isto, 'Kiln.test' pulava TODO o
        # middleware registrado com 'after' — cabecalhos de seguranca,
        # compressao, metricas — e um teste passava sobre uma resposta
        # que o servidor de verdade nunca devolve. Um teste que mente e
        # pior que teste nenhum.
        for depois in app.depois:
            try:
                trocada = depois(req, resp)
                if isinstance(trocada, dict) and trocada.get("__kiln__"):
                    resp = trocada
            except Exception:
                pass        # middleware de saida nao derruba a resposta
        corpo = resp["body"]
        # Um arquivo servido do disco volta em bytes. Num teste isso
        # obriga a decodificar a mao toda vez; quando o tipo e textual,
        # entregamos texto — que e o que o teste vai comparar.
        if isinstance(corpo, bytes):
            tipo = resp.get("content_type") or ""
            if tipo.startswith("text/") or "json" in tipo or "xml" in tipo \
                    or "javascript" in tipo:
                corpo = corpo.decode("utf-8", errors="replace")
        return {"status": resp["status"], "body": corpo,
                "headers": resp["headers"]}

    def __new__(cls):
        return {
            "__name__": "Kiln",

            # aplicacao
            "forge": cls._forge,
            "app": cls._forge,
            "config": cls._config,

            # rotas
            "route": cls._rota,
            "get": cls._get,
            "post": cls._post,
            "put": cls._put,
            "patch": cls._patch,
            "delete": cls._delete,
            "options": cls._options,
            "head": cls._head,
            "any": cls._any,
            "resource": cls._resource,
            "mount": cls._mount,
            "group": cls._group,
            "routes": cls._routes,

            # middleware
            "use": cls._use,
            "after": cls._after,
            "on_error": cls._on_error,
            "cors": cls._cors,
            "logger": cls._logger,
            "rate_limit": cls._rate_limit,
            "auth": cls._auth,
            "guard": cls._guard,
            "secure_headers": cls._secure_headers,
            "cabecalhos_seguros": cls._secure_headers,
            "csrf": cls._csrf,
            "csrf_token": cls._csrf_token,
            "limite_de_corpo": cls._limite_de_corpo,
            "body_limit": cls._limite_de_corpo,

            # validacao e listagem
            "validar": cls._validar,
            "validate": cls._validar,
            # Validar SEM responder: as vezes o campo errado nao e 422,
            # e uma pergunta para o usuario, ou um valor padrao.
            "conferir": staticmethod(_conferir_esquema).__func__,
            "paginar": cls._paginar,
            "ordenar": cls._ordenar,
            "buscar": cls._buscar,

            # observabilidade
            "request_id": cls._request_id,
            "audit": cls._audit,
            "auditoria": cls._audit,

            # transferencia
            "cache": cls._cache,
            "comprimir": cls._comprimir,
            "idempotente": cls._idempotente,

            # respostas
            "json": cls._json,
            "html": cls._html,
            "text": cls._text,
            "status": cls._status,
            "redirect": cls._redirect,
            "file": cls._file,
            "header": cls._header,
            "cookie": cls._cookie,

            # sessao
            "session_start": cls._session_start,
            "session_end": cls._session_end,
            "sign": cls._sign,
            "unsign": cls._unsign,

            # views
            "templates": cls._templates,
            "render": cls._render,
            "render_string": cls._render_string,
            "static": cls._static,
            "escape": cls._escape,

            # ciclo de vida
            # ── Tempo real ──
            "ws": cls._ws,
            "sala": cls._sala,
            "Sala": _classe_sala(),
            "sse": cls._sse,
            "evento": cls._evento,
            "stream": cls._stream,

            # ── Upload ──
            "upload": cls._upload,
            "uploads": cls._uploads,
            "salvar_upload": cls._salvar_upload,

            "listen": cls._listen,
            "serve": cls._serve,
            "stop": cls._stop,
            "stats": cls._stats,
            "test": cls._test,
        }
