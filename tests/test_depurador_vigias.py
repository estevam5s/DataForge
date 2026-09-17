# -*- coding: utf-8 -*-
"""Watchpoints: parar quando um valor MUDA, e nao quando uma linha passa.

Uma parada por linha responde "o programa passou aqui?". A pergunta de
quem depura um valor errado e outra: "QUEM mudou isto?" — e a resposta
pode estar numa acao chamada de outra acao chamada num laco. A vigia e
conferida depois de cada instrucao, e a parada mostra a linha que mudou.

Tres coisas que os testes cobram, e que o jeito ingenuo erraria:

1. a MUTACAO conta: 'xs.append(1)' nao troca a referencia, e comparar
   referencia diria que nada mudou;
2. o campo de um objeto mudado dentro de um METODO conta, e a parada e na
   linha do metodo;
3. uma vigia criada dentro de uma acao olha o escopo DAQUELA acao — a
   mesma variavel com o mesmo nome em outro lugar e outra.
"""

import io
import json
import os
import subprocess
import sys
import threading
import time

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.depurador import CONTINUAR, Depurador, depurar     # noqa: E402
from dataforge.interpreter import Interpreter                      # noqa: E402
from dataforge.lexer import tokenize                               # noqa: E402
from dataforge.parser import parse                                 # noqa: E402


class Gravador(Depurador):
    """Anota cada parada e segue — a conversa sem terminal."""

    def __init__(self, *args, ao_parar=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.vistas = []
        self.ao_parar = ao_parar

    def _parar(self, no, env, linha):
        self.vistas.append((linha, self.motivo))
        if self.ao_parar is not None:
            self.ao_parar(self, no, env, linha)
        self.modo = CONTINUAR


def _rodar(fonte, vigias=(), paradas=(), ao_parar=None):
    interp = Interpreter()
    d = Gravador(interp, "p.df", fonte, paradas, ao_parar=ao_parar)
    d.modo = CONTINUAR
    for expressao in vigias:
        d.vigiar(expressao)
    d.ligar()
    saida = io.StringIO()
    anterior = sys.stdout
    sys.stdout = saida
    try:
        interp.run(parse(tokenize(fonte, "p.df"), "p.df"), "p.df")
    finally:
        sys.stdout = anterior
        d.desligar()
    return d, saida.getvalue()


LACO = '''total := 0
cycle i from 1 to 3:
    x := i * 2
    total += x
out total
'''


def test_para_em_cada_mudanca_na_linha_que_mudou():
    d, saida = _rodar(LACO, vigias=["total"])
    assert [linha for linha, _ in d.vistas] == [1, 4, 4, 4]
    assert "12" in saida, "o programa nao terminou"


def test_o_motivo_diz_de_quanto_para_quanto():
    d, _ = _rodar(LACO, vigias=["total"])
    _, motivo = d.vistas[2]
    assert "total" in motivo and "2" in motivo and "6" in motivo, motivo


def test_valor_que_nao_muda_nao_para():
    d, _ = _rodar("y := 5\ncycle i from 1 to 3:\n    z := i\nout y\n", vigias=["y"])
    assert [linha for linha, _ in d.vistas] == [1]


def test_mutacao_no_lugar_conta():
    fonte = 'xs := []\nxs.append(1)\nn := len(xs)\nxs.append(2)\n'
    d, _ = _rodar(fonte, vigias=["xs"])
    assert [linha for linha, _ in d.vistas] == [1, 2, 4]


def test_campo_mudado_dentro_de_um_metodo_para_na_linha_do_metodo():
    fonte = '''blueprint Conta:
    saldo := 0
    action depositar(v):
        self.saldo += v
c := spawn Conta()
c.depositar(10)
c.depositar(0)
c.depositar(5)
'''
    d, _ = _rodar(fonte, vigias=["c.saldo"])
    linhas = [linha for linha, _ in d.vistas]
    # nasce na 5; muda na 4 (dentro do metodo) duas vezes — o deposito de
    # zero nao muda nada
    assert linhas == [5, 4, 4], linhas


def test_vigia_criada_numa_acao_olha_o_escopo_dela():
    fonte = '''action somar(ate):
    acc := 0
    cycle i from 1 to ate:
        acc += i
    yield acc
acc := 100
out somar(3)
acc := 200
'''
    criou = []

    def ao_parar(d, no, env, linha):
        if linha == 3 and not criou:
            d.vigiar("acc", env)
            criou.append(1)

    d, _ = _rodar(fonte, paradas=[3], ao_parar=ao_parar)
    mudancas = [linha for linha, motivo in d.vistas if "acc" in motivo]
    # as tres somas dentro da acao; 'acc := 200' de fora e OUTRO 'acc'
    assert mudancas == [4, 4, 4], d.vistas


def test_valor_que_passa_a_existir_e_mudanca():
    d, _ = _rodar("a := 1\nb := 2\n", vigias=["b"])
    assert [linha for linha, _ in d.vistas] == [2]
    assert "passou a existir" in d.vistas[0][1] or "2" in d.vistas[0][1]


def test_desvigiar():
    interp = Interpreter()
    d = Depurador(interp, "p.df", "x := 1\n")
    v = d.vigiar("x")
    assert d.vigias == [v]
    assert d.desvigiar(1) is True
    assert d.vigias == []
    assert d.desvigiar(9) is False


def test_expressao_invalida_e_recusada_na_hora():
    d = Depurador(Interpreter(), "p.df", "x := 1\n")
    with pytest.raises(ValueError):
        d.vigiar("x := := 2")


def test_sem_vigia_nada_e_avaliado(monkeypatch):
    """O custo: sem vigia, a conferencia nao roda — nem uma avaliacao."""
    chamadas = []
    monkeypatch.setattr(Depurador, "_conferir_vigias",
                        lambda self, no, env: chamadas.append(no))
    _rodar(LACO)
    assert chamadas == []


def test_threads_param_cada_uma_na_sua_mudanca():
    fonte = '''contador := {"n": 0}
parallel:
    thread:
        contador["n"] := contador["n"] + 1
    thread:
        contador["n"] := contador["n"] + 1
'''
    d, _ = _rodar(fonte, vigias=['contador["n"]'])
    assert len([l for l, m in d.vistas if "contador" in m]) >= 2


# ── o terminal ───────────────────────────────────────────────

def _depurar(tmp_path, comandos, fonte=LACO, paradas=(), vigias=()):
    arquivo = tmp_path / "p.df"
    arquivo.write_text(fonte, encoding="utf-8")
    entrada, saida = sys.stdin, sys.stdout
    sys.stdin = io.StringIO("\n".join(comandos) + "\n")
    sys.stdout = io.StringIO()
    try:
        codigo = depurar(str(arquivo), paradas, (), vigias=vigias)
        return sys.stdout.getvalue(), codigo
    finally:
        sys.stdin, sys.stdout = entrada, saida


def test_comando_w_vigia_e_para_na_mudanca(tmp_path):
    saida, codigo = _depurar(tmp_path, ["w total", "c", "c", "c", "c", "c"],
                             paradas=[2])
    assert codigo == 0
    assert saida.count("mudou") == 3, saida
    assert "p.df:4" in saida


def test_comando_vigias_lista_e_desvigiar_remove(tmp_path):
    saida, _ = _depurar(tmp_path, ["w total", "vigias", "desvigiar 1", "vigias",
                                   "c", "c", "c", "c"], paradas=[2])
    assert "1  total" in saida
    assert "nenhuma vigia" in saida
    assert "mudou" not in saida


def test_flag_vigiar_na_linha_de_comando(tmp_path):
    saida, _ = _depurar(tmp_path, ["c"] * 6, vigias=["total"])
    assert saida.count("mudou") >= 3


def test_cli_aceita_vigiar(tmp_path):
    arquivo = tmp_path / "p.df"
    arquivo.write_text(LACO, encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "debug", str(arquivo),
                        "--vigiar=total"], input="c\nc\nc\nc\nc\n",
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=RAIZ,
                       env={**os.environ, "NO_COLOR": "1"})
    assert r.returncode == 0, r.stderr
    assert r.stdout.count("mudou") >= 3, r.stdout


# ── o editor (DAP): data breakpoints ─────────────────────────

def test_dap_anuncia_e_para_por_data_breakpoint(tmp_path):
    sys.path.insert(0, os.path.join(RAIZ, "tests"))
    from test_dap import Cliente

    arquivo = tmp_path / "laco.df"
    arquivo.write_text('''total := 0
cycle i from 1 to 10:
    total := total + i
out total
''', encoding="utf-8")
    c = Cliente()
    try:
        corpo = c.chamar("initialize", adapterID="dataforge")["body"]
        assert corpo["supportsDataBreakpoints"] is True
        c.esperar_evento("initialized")
        c.chamar("setBreakpoints", source={"path": str(arquivo)},
                 breakpoints=[{"line": 2}])
        c.chamar("configurationDone")
        c.chamar("launch", program=str(arquivo))
        i, _ = c.esperar_evento("stopped")

        quadro = c.chamar("stackTrace", threadId=1)["body"]["stackFrames"][0]["id"]
        escopos = c.chamar("scopes", frameId=quadro)["body"]["scopes"]
        info = c.chamar("dataBreakpointInfo",
                        variablesReference=escopos[0]["variablesReference"],
                        name="total")
        assert info["success"], info
        data_id = info["body"]["dataId"]
        assert data_id and "total" in info["body"]["description"]

        definidos = c.chamar("setDataBreakpoints", breakpoints=[{"dataId": data_id}])
        assert definidos["body"]["breakpoints"][0]["verified"] is True
        c.chamar("setBreakpoints", source={"path": str(arquivo)}, breakpoints=[])

        c.chamar("continue", threadId=1)
        j, parada = c.esperar_evento("stopped", depois_de=i + 1)
        assert parada["body"]["reason"] == "data breakpoint", parada
        assert "total" in parada["body"].get("description", "")
        c.chamar("continue", threadId=1)
        _, outra = c.esperar_evento("stopped", depois_de=j + 1)
        assert outra["body"]["reason"] == "data breakpoint"

        c.chamar("setDataBreakpoints", breakpoints=[])
        c.chamar("continue", threadId=1)
        c.esperar_evento("terminated")
    finally:
        c.fechar()
