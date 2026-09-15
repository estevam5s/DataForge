"""O middleware do Arcane.Http falha FECHADO.

Um middleware que levantava era pulado com 'except Exception: pass', e o
handler rodava. Com a autenticação que recusa levantando — a forma mais
natural de recusar —, um pedido SEM credencial recebia 200 e os dados da
rota. E um middleware que respondia 401 não interrompia nada: o handler
rodava depois, com os efeitos dele, e a resposta saía 200 porque o
'send' atropelava o status escolhido uma linha acima.

Os dois foram medidos contra um servidor de verdade antes da correção, e
é contra um servidor de verdade que estes testes rodam: um framework HTTP
testado por dublê não prova nada sobre o que o cliente recebe.
"""

import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import HTTPServer

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib import arcane_http, get_module   # noqa: E402

# O handler de requisição guarda o roteador numa variável de CLASSE, então
# dois servidores ao mesmo tempo dividiriam as rotas. Os testes deste
# arquivo sobem um de cada vez.
_UM_POR_VEZ = threading.Lock()


@pytest.fixture
def servidor(capsys):
    """Sobe um app, devolve (porta, estado) e desliga no fim."""
    abertos = []

    def subir(configurar):
        _UM_POR_VEZ.acquire()
        http = get_module("Arcane.Http")
        app = http["create"]("teste")
        estado = {"efeitos": []}
        configurar(http, app, estado)
        arcane_http._DFRequestHandler.router = app["_router"]
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            porta = s.getsockname()[1]
        srv = HTTPServer(("127.0.0.1", porta), arcane_http._DFRequestHandler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        abertos.append(srv)
        time.sleep(0.05)
        return porta, estado

    yield subir
    for srv in abertos:
        srv.shutdown()
        srv.server_close()
    if abertos:
        _UM_POR_VEZ.release()


def _pedir(porta, caminho, cabecalhos=None):
    pedido = urllib.request.Request(f"http://127.0.0.1:{porta}{caminho}",
                                    headers=cabecalhos or {})
    try:
        with urllib.request.urlopen(pedido, timeout=10) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _com_autenticacao_que_levanta(http, app, estado):
    def autenticar(req, res):
        if (req.get("headers") or {}).get("Authorization") != "Bearer segredo":
            raise PermissionError("nao autorizado")

    def restrita(req, res):
        estado["efeitos"].append("rodou")
        return {"dados": "confidenciais"}

    http["use"](app, autenticar)
    http["get"](app, "/admin", restrita)


def test_middleware_que_levanta_nao_deixa_o_pedido_passar(servidor):
    porta, estado = servidor(_com_autenticacao_que_levanta)
    status, corpo = _pedir(porta, "/admin")
    assert status == 500, f"um pedido sem credencial recebeu {status}"
    assert "confidenciais" not in corpo, "os dados da rota vazaram"
    assert estado["efeitos"] == [], "o handler rodou num pedido recusado"


def test_o_pedido_legitimo_continua_passando(servidor):
    """Falhar fechado não pode virar recusar tudo."""
    porta, estado = servidor(_com_autenticacao_que_levanta)
    status, corpo = _pedir(porta, "/admin", {"Authorization": "Bearer segredo"})
    assert status == 200
    assert "confidenciais" in corpo
    assert estado["efeitos"] == ["rodou"]


def test_middleware_que_responde_interrompe_o_handler(servidor):
    """Os efeitos do handler não podem acontecer num pedido recusado."""
    def configurar(http, app, estado):
        def recusar(req, res):
            res["status"](401)
            res["send"]("nao autorizado")

        def apagar(req, res):
            estado["efeitos"].append("APAGOU")
            return {"ok": True}

        http["use"](app, recusar)
        http["get"](app, "/apagar", apagar)

    porta, estado = servidor(configurar)
    status, corpo = _pedir(porta, "/apagar")
    assert estado["efeitos"] == [], "o handler apagou num pedido recusado"
    assert status == 401, f"o 401 do middleware saiu como {status}"
    assert corpo == "nao autorizado"


def test_send_nao_atropela_o_status_escolhido_antes(servidor):
    """'res.status(404)' seguido de 'res.send(...)' respondia 200."""
    def configurar(http, app, estado):
        def rota(req, res):
            res["status"](404)
            res["send"]("nao achei")

        http["get"](app, "/x", rota)

    porta, _ = servidor(configurar)
    assert _pedir(porta, "/x") == (404, "nao achei")


def test_middleware_que_so_observa_deixa_seguir(servidor):
    """O caso comum — logar, anotar — continua funcionando."""
    def configurar(http, app, estado):
        def anotar(req, res):
            estado["efeitos"].append("viu")

        def rota(req, res):
            estado["efeitos"].append("rodou")
            return {"ok": True}

        http["use"](app, anotar)
        http["get"](app, "/", rota)

    porta, estado = servidor(configurar)
    status, _ = _pedir(porta, "/")
    assert status == 200
    assert estado["efeitos"] == ["viu", "rodou"]
