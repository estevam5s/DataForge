"""A sessão da Vitrine, compartilhada entre processos.

Até aqui a sessão morava num dicionário do processo. Com dois processos
atrás de um balanceador, o segundo pedido da mesma pessoa caía numa
memória que nunca a viu: o contador voltava a 1 e o login "caía" — sem
erro nenhum, só às vezes, conforme o sorteio do balanceador.

Os testes cobram o armazém compartilhado nas duas formas que a
biblioteca traz (SQLite e arquivos) e na forma que quem escreve pode
trazer (um blueprint com `carregar`, `gravar` e `apagar`):

1. o que um processo grava, o outro lê — com processos DE VERDADE, por
   socket, e não só duas aplicações no mesmo interpretador;
2. a mutação no lugar conta: `itens.append(x)` não chama `definir`, e
   mesmo assim tem de chegar ao outro processo;
3. dois pedidos simultâneos que mexem em chaves DIFERENTES não apagam o
   trabalho um do outro;
4. um valor que não atravessa processo é recusado com mensagem clara,
   na página — e o resto da sessão é gravado;
5. um identificador inventado pelo cliente não vira sessão (fixação), e
   nunca vira caminho de arquivo.
"""

import http.cookiejar
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib.vitrine.api import ArcaneVitrine, _ATUAL   # noqa: E402


@pytest.fixture
def V():
    _ATUAL["app"] = None
    modulo = ArcaneVitrine()
    yield modulo
    _ATUAL["app"] = None


def _sid(resposta):
    """O 'Kiln.test' nao devolve cookies: a pagina escreve o id (_marcar)."""
    achado = re.search(r"sid=([0-9a-f]{32})", resposta["body"])
    assert achado, "a pagina nao escreveu o id da sessao"
    return achado.group(1)


def _marcar(V, pagina):
    def marcada():
        V["texto"](f"sid={V['estado'].id()}")
        pagina()
    return marcada


def _pedir(V, app, sid=None, caminho="/"):
    # o id vai pelo cookie, como o navegador manda
    cabecalhos = {"cookie": f"vitrine_sid={sid}"} if sid else None
    return V["pedir"](app, "GET", caminho, cabecalhos=cabecalhos)


def _contador(V):
    def pagina():
        n = V["estado"].somar("n")
        V["texto"](f"n={n}")
    return pagina


@pytest.fixture(params=["banco", "arquivos"])
def armazem(request, tmp_path, V):
    """Um armazém novo — e a fábrica de outro que olha o MESMO lugar."""
    if request.param == "banco":
        lugar = str(tmp_path / "sessoes.db")
        return lambda: V["sessoes_em_banco"](lugar)
    lugar = str(tmp_path / "sessoes")
    return lambda: V["sessoes_em_arquivos"](lugar)


def _dois_processos(V, armazem, pagina):
    """Duas aplicações, cada uma com o seu armazém sobre o mesmo lugar —
    é o que dois processos veem."""
    apps = []
    for nome in ("a", "b"):
        app = V["app"](nome, sessoes_em=armazem())
        V["pagina"]("/", _marcar(V, pagina))
        apps.append(app)
    return apps


# ── 1. o que um grava, o outro lê ────────────────────────────

def test_o_contador_continua_no_outro_processo(V, armazem):
    a, b = _dois_processos(V, armazem, _contador(V))
    r = _pedir(V, a)
    sid = _sid(r)
    assert "n=1" in r["body"]
    assert "n=2" in _pedir(V, b, sid)["body"]
    assert "n=3" in _pedir(V, a, sid)["body"]
    assert "n=4" in _pedir(V, b, sid)["body"]


def test_o_login_vale_no_outro_processo(V, armazem):
    def pagina():
        if not V["autenticado"]():
            V["entrar"]("ana", "certa")
        V["texto"](f"quem={V['usuario']()['nome']}")

    a, b = _dois_processos(V, armazem, pagina)
    for app in (a, b):
        app.autenticacao(lambda u, s: {"nome": u, "papel": "admin"}
                         if s == "certa" else None)
    sid = _sid(_pedir(V, a))

    vistos = []
    b.autenticacao(lambda u, s: vistos.append(u) or None)
    assert "quem=ana" in _pedir(V, b, sid)["body"]
    assert vistos == [], "o outro processo pediu login de novo"


def test_a_mutacao_no_lugar_chega_ao_outro_processo(V, armazem):
    def pagina():
        itens = V["estado"].padrao("itens", [])
        itens.append(len(itens))
        V["texto"](f"itens={itens}")

    a, b = _dois_processos(V, armazem, pagina)
    sid = _sid(_pedir(V, a))
    _pedir(V, b, sid)
    assert "itens=[0, 1, 2]" in _pedir(V, a, sid)["body"]


def test_remover_e_limpar_chegam_ao_outro_processo(V, armazem):
    def grava():
        V["estado"].definir("x", 1)
        V["estado"].definir("y", 2)

    def remove():
        V["estado"].remover("x")

    def mostra():
        V["texto"](f"x={V['estado'].obter('x')} y={V['estado'].obter('y')}")

    a = V["app"]("a", sessoes_em=armazem())
    V["pagina"]("/", _marcar(V, grava))
    V["pagina"]("/remove", _marcar(V, remove))
    b = V["app"]("b", sessoes_em=armazem())
    V["pagina"]("/", _marcar(V, mostra))
    sid = _sid(_pedir(V, a))
    _pedir(V, a, sid, "/remove")
    assert "x=void y=2" in _pedir(V, b, sid)["body"] or \
        "x=None y=2" in _pedir(V, b, sid)["body"]


def test_os_tipos_da_sessao_voltam_iguais(V, armazem):
    valores = {
        "inteiro": 7, "real": 2.5, "texto": "olá", "sim": True, "nada": None,
        "lista": [1, [2, 3], {"a": 1}], "vault_numerico": {1: "um", 2: "dois"},
        "conjunto": {1, 2, 3}, "bytes": b"\x00\xffPNG", "tupla": (1, "a"),
    }
    lidos = {}

    def grava():
        for chave, valor in valores.items():
            V["estado"].definir(chave, valor)

    def le():
        for chave in valores:
            lidos[chave] = V["estado"].obter(chave)

    a = V["app"]("a", sessoes_em=armazem())
    V["pagina"]("/", _marcar(V, grava))
    b = V["app"]("b", sessoes_em=armazem())
    V["pagina"]("/", _marcar(V, le))
    _pedir(V, b, _sid(_pedir(V, a)))
    assert lidos == valores
    assert isinstance(lidos["bytes"], bytes) and isinstance(lidos["conjunto"], set)


# ── 3. concorrência ──────────────────────────────────────────

def test_chaves_diferentes_ao_mesmo_tempo_nao_se_apagam(V, armazem):
    a = V["app"]("a", sessoes_em=armazem())
    b = V["app"]("b", sessoes_em=armazem())
    primeira = a.sessao()
    a.confirmar_sessao(primeira)

    # os dois processos abrem a sessao ANTES de qualquer um gravar
    em_a = a.sessao(primeira.id)
    em_b = b.sessao(primeira.id)
    em_a.definir("carrinho", ["livro"])
    em_b.definir("tema", "escuro")
    a.confirmar_sessao(em_a)
    b.confirmar_sessao(em_b)

    final = a.sessao(primeira.id)
    assert final.obter("carrinho") == ["livro"]
    assert final.obter("tema") == "escuro"


# ── 4. o que não atravessa ───────────────────────────────────

def test_valor_que_nao_atravessa_processo_e_recusado_na_pagina(V, armazem, tmp_path):
    from dataforge.interpreter import Interpreter
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    interp = Interpreter()
    interp.run(parse(tokenize("record Ponto:\n    x: Integer\np := Ponto(1)\n",
                              "<t>"), "<t>"), "<t>")
    ponto = interp.global_env.get("p")

    def pagina():
        V["estado"].definir("ok", 1)
        V["estado"].definir("ponto", ponto)

    a = V["app"]("a", sessoes_em=armazem())
    V["pagina"]("/", _marcar(V, pagina))
    r = _pedir(V, a)
    assert "ponto" in r["body"] and "Ponto" in r["body"]
    assert "processo" in r["body"]
    b = V["app"]("b", sessoes_em=armazem())
    V["pagina"]("/", _marcar(V, lambda: V["texto"](f"ok={V['estado'].obter('ok')}")))
    assert "ok=1" in _pedir(V, b, _sid(r))["body"]


# ── 5. o identificador ───────────────────────────────────────

def test_identificador_inventado_nao_vira_sessao(V, armazem):
    a, _ = _dois_processos(V, armazem, _contador(V))
    r = _pedir(V, a, "a" * 32)
    assert _sid(r) != "a" * 32
    assert "n=1" in r["body"]


def test_identificador_com_caminho_nunca_toca_o_disco(V, tmp_path):
    pasta = tmp_path / "sessoes"
    app = V["app"]("a", sessoes_em=V["sessoes_em_arquivos"](str(pasta)))
    V["pagina"]("/", _marcar(V, _contador(V)))
    alvo = tmp_path / "fora.json"
    r = _pedir(V, app, "../fora")
    assert "n=1" in r["body"]
    assert not alvo.exists()
    assert all(re.fullmatch(r"[0-9a-f]{32}\.json(\.trava)?", p.name) for p in pasta.iterdir())


# ── operação ─────────────────────────────────────────────────

def test_encerrar_vencer_e_contar(V, armazem):
    a = V["app"]("a", sessoes_em=armazem(), validade_sessao=3600)
    V["pagina"]("/", _marcar(V, _contador(V)))
    sid = _sid(_pedir(V, a))
    _pedir(V, a)
    assert a.metricas()["sessoes"] == 2

    a.encerrar_sessao(sid)
    assert a.metricas()["sessoes"] == 1
    assert "n=1" in _pedir(V, a, sid)["body"], "a sessao encerrada voltou"

    loja = a.armazem_de_sessao()
    assert loja.vencer(3600, agora=time.time() + 7200) == 2
    assert a.metricas()["sessoes"] == 0


def test_a_memoria_continua_o_padrao(V):
    app = V["app"]("s")
    V["pagina"]("/", _marcar(V, _contador(V)))
    sid = _sid(_pedir(V, app))
    assert sid in app.sessoes
    assert "n=2" in _pedir(V, app, sid)["body"]


def test_banco_aceita_a_conexao_do_arcane_database(V, tmp_path):
    from dataforge.stdlib import get_module
    Db = get_module("Arcane.Database")
    conexao = Db["connect"](str(tmp_path / "app.db"))
    a = V["app"]("a", sessoes_em=V["sessoes_em_banco"](conexao))
    V["pagina"]("/", _marcar(V, _contador(V)))
    b = V["app"]("b", sessoes_em=V["sessoes_em_banco"](str(tmp_path / "app.db")))
    V["pagina"]("/", _marcar(V, _contador(V)))
    assert "n=2" in _pedir(V, b, _sid(_pedir(V, a)))["body"]


def test_banco_em_memoria_e_recusado(V):
    with pytest.raises(Exception) as erro:
        V["sessoes_em_banco"](":memory:")
    assert "processo" in str(erro.value)


# ── o armazém escrito em DataForge ───────────────────────────

def test_um_blueprint_serve_de_armazem(tmp_path):
    from dataforge.interpreter import Interpreter
    from dataforge.lexer import tokenize
    from dataforge.parser import parse
    import io
    from contextlib import redirect_stdout

    fonte = '''
adopt Arcane.Vitrine as V

blueprint Guarda:
    tudo := {}
    action carregar(id):
        yield self.tudo.get(id)
    action gravar(id, dados):
        self.tudo[id] := dados
    action apagar(id):
        self.tudo.remove(id)

guarda := spawn Guarda()

action pagina():
    V.texto($"sid={V.estado.id()} n={V.estado.somar("n")}")

a := V.app("a", sessoes_em := guarda)
V.pagina("/", pagina)
r := V.pedir(a, "GET", "/")
sid := r["body"].split("sid=")[1][0:32]
b := V.app("b", sessoes_em := guarda)
V.pagina("/", pagina)
r2 := V.pedir(b, "GET", "/", void, {"cookie": $"vitrine_sid={sid}"})
out "n=2" in r2["body"], len(guarda.tudo)
'''
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
    assert saida.getvalue().strip().splitlines()[-1] == "yes 1"


# ── processos de verdade ─────────────────────────────────────

def _porta_livre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _esperar(porta, prazo=20):
    fim = time.time() + prazo
    while time.time() < fim:
        try:
            with socket.create_connection(("127.0.0.1", porta), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise AssertionError(f"o servidor na porta {porta} nao subiu")


@pytest.mark.parametrize("forma", ["banco", "arquivos"])
def test_dois_processos_por_socket_dividem_a_sessao(tmp_path, forma):
    lugar = str(tmp_path / ("s.db" if forma == "banco" else "s")).replace("\\", "/")
    app = tmp_path / "app.df"
    app.write_text(f'''adopt Arcane.Vitrine as V
adopt Arcane.OS as OS

action pagina():
    n := V.estado.somar("n")
    V.texto($"n={{n}} pid={{OS.pid()}}")

V.app("Contador", sessoes_em := V.sessoes_em_{forma}("{lugar}"))
V.pagina("/", pagina)
V.subir(porta := 8501, silencioso := yes)
''', encoding="utf-8")

    portas = [_porta_livre(), _porta_livre()]
    processos = [subprocess.Popen(
        [sys.executable, "-m", "dataforge", "run", str(app)], cwd=RAIZ,
        env={**os.environ, "VITRINE_PORTA": str(p), "NO_COLOR": "1"},
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) for p in portas]
    try:
        for p in portas:
            _esperar(p)
        jar = http.cookiejar.CookieJar()
        abrir = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(jar)).open
        vistos = []
        for i in range(6):
            html = abrir(f"http://127.0.0.1:{portas[i % 2]}/", timeout=10).read().decode()
            n, pid = re.search(r"n=(\d+) pid=(\d+)", html).groups()
            vistos.append((int(n), pid))
        assert [n for n, _ in vistos] == [1, 2, 3, 4, 5, 6], vistos
        assert len({pid for _, pid in vistos}) == 2, "nao foram dois processos"
    finally:
        for proc in processos:
            proc.kill()
            proc.wait(timeout=10)
            proc.stdout.close()
            proc.stderr.close()
