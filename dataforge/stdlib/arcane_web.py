"""
Arcane.Web - Web & Networking Module
"""

import json
import urllib.error
import urllib.request
import urllib.parse
import http.server
import threading
import socket


def _resposta(status, cabecalhos, corpo, erro=None):
    """A resposta HTTP como vault, venha ela de um 200 ou de um 404."""
    if isinstance(corpo, (bytes, bytearray)):
        corpo = corpo.decode("utf-8", "replace")
    saida = {
        "status": status,
        "headers": dict(cabecalhos or {}),
        "body": corpo,
        "json": lambda: json.loads(corpo),
        "ok": 200 <= (status or 0) < 300,
    }
    if erro is not None:
        saida["error"] = str(erro)
        saida["erro"] = str(erro)
    return saida


class ArcaneWeb:
    """Web server and HTTP client module."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Web",
            "serve": cls._serve,
            "request": cls._request,
            "get": cls._get,
            "post": cls._post,
            "socket": cls._socket,
            "encode_url": cls._encode_url,
            "decode_url": cls._decode_url,
            "json_parse": cls._json_parse,
            "json_stringify": cls._json_stringify,
            "check": cls._check,
            "close": cls._close,
        }

    @staticmethod
    def _serve(port=8080, host="0.0.0.0"):
        """Start a simple HTTP server."""
        handler = http.server.SimpleHTTPRequestHandler

        class QuietHandler(handler):
            def log_message(self, format, *args):
                pass  # Suppress output

        server = http.server.HTTPServer((host, port), QuietHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"[Arcane.Web] Server started on {host}:{port}")
        return {
            "__type__": "WebServer",
            "server": server,
            "port": port,
            "host": host,
            "stop": lambda: server.shutdown(),
            "on_request": lambda method, path: None,  # Placeholder
        }

    @staticmethod
    def _request(url, method="GET", data=None, headers=None):
        """Make an HTTP request."""
        try:
            if headers is None:
                headers = {}

            if data and isinstance(data, dict):
                data = json.dumps(data).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            elif data and isinstance(data, str):
                data = data.encode('utf-8')

            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as response:
                return _resposta(response.status, response.headers,
                                 response.read())
        except urllib.error.HTTPError as erro:
            # Um 404, um 400 e um 500 sao RESPOSTA, e nao falha de rede.
            #
            # O 'urlopen' levanta para todo 4xx e 5xx, e o 'except
            # Exception' abaixo transformava os tres em 'status: 0' com
            # o corpo vazio. Quem chamava nao tinha como distinguir "o
            # servidor recusou" de "a rede nao chegou la", e o corpo do
            # erro — que e onde a API diz o que houve — sumia.
            #
            # 'status: 0' e o caso honesto de "nao se sabe", que e o
            # terceiro desfecho de toda chamada de rede. Gastá-lo com
            # uma resposta que CHEGOU faz quem chama repetir um pedido
            # que o servidor ja recusou.
            return _resposta(erro.code, erro.headers, erro.read(),
                             erro=erro.reason)
        except Exception as e:
            return {
                "status": 0,
                "error": str(e),
                "erro": str(e),
                "body": "",
                "headers": {},
            }

    @staticmethod
    def _get(url, headers=None):
        return ArcaneWeb._request(url, "GET", headers=headers)

    @staticmethod
    def _post(url, data=None, headers=None):
        return ArcaneWeb._request(url, "POST", data=data, headers=headers)

    @staticmethod
    def _socket(host, port):
        """Create a socket connection."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return {
            "__type__": "Socket",
            "send": lambda data: sock.send(data.encode()),
            "receive": lambda size=4096: sock.recv(size).decode(),
            "close": lambda: sock.close(),
        }

    @staticmethod
    def _encode_url(text):
        return urllib.parse.quote(text)

    @staticmethod
    def _decode_url(text):
        return urllib.parse.unquote(text)

    @staticmethod
    def _json_parse(text):
        return json.loads(text)

    @staticmethod
    def _json_stringify(obj, indent=None):
        return json.dumps(obj, indent=indent, ensure_ascii=False)

    @staticmethod
    def _check(user_id=None):
        """Check network/connection status."""
        try:
            urllib.request.urlopen("https://httpbin.org/get", timeout=5)
            return "OK"
        except Exception:
            return "FAIL"

    @staticmethod
    def _close():
        """Close network resources."""
        pass
