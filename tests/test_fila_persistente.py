"""A fila de trabalho que sobrevive ao processo.

A 'Fila' do Arcane.Eventos vive na memoria: um processo que morre leva
junto o que nao foi feito. A persistente guarda cada tarefa num SQLite, e
os testes abaixo cobram as quatro promessas que ela faz:

1. o que foi publicado continua la depois que o processo morre — inclusive
   o que estava SENDO feito quando ele morreu;
2. uma falha e repetida com recuo exponencial, e nao na hora;
3. uma tarefa pode esperar um tempo, ou uma hora marcada;
4. depois de N falhas, ela vai para a carta morta — com o erro, para ser
   analisada, reprocessada ou descartada.

O relogio e injetado: um teste de recuo que dorme de verdade e lento, e um
que dorme pouco e instavel.
"""

import io
import json
import os
import subprocess
import sys
import threading
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module                  # noqa: E402

E = get_module("Arcane.Eventos")


class Relogio:
    def __init__(self, agora=1000.0):
        self.agora = agora

    def __call__(self):
        return self.agora

    def andar(self, segundos):
        self.agora += segundos


def _fila(caminho, trabalhador=None, relogio=None, **opcoes):
    base = {"operarios": 0, "tremor": 0.0}
    base.update(opcoes)
    if relogio is not None:
        base["_relogio"] = relogio
    return E["fila_persistente"](str(caminho), trabalhador, base)


# ── 1. sobreviver ao processo ────────────────────────────────

def test_o_publicado_sobrevive_a_outra_instancia(tmp_path):
    banco = tmp_path / "fila.db"
    a = _fila(banco)
    a.publicar({"email": "ana@x.com"})
    a.publicar({"email": "bia@x.com"})
    a.fechar()

    feitos = []
    b = _fila(banco, feitos.append)
    assert b.pendentes() == 2
    assert b.processar() == 2
    assert [f["email"] for f in feitos] == ["ana@x.com", "bia@x.com"]
    assert b.pendentes() == 0


def test_tarefa_de_processo_morto_volta_depois_do_prazo_de_reserva(tmp_path):
    """O processo filho reserva a tarefa e morre com os._exit, sem 'finally'."""
    banco = tmp_path / "fila.db"
    codigo = (
        "import os, sys\n"
        f"sys.path.insert(0, {RAIZ!r})\n"
        "from dataforge.stdlib import get_module\n"
        "E = get_module('Arcane.Eventos')\n"
        f"f = E['fila_persistente']({str(banco)!r}, None, {{'operarios': 0, 'reserva': 5}})\n"
        "f.publicar('relatorio')\n"
        "assert f._reservar() is not None\n"
        "os._exit(9)\n")
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True,
                       text=True, encoding="utf-8")
    assert r.returncode == 9, r.stderr

    relogio = Relogio(agora=__import__("time").time())
    feitos = []
    f = _fila(banco, feitos.append, relogio, reserva=5)
    assert f.processar() == 0, "a reserva do morto ainda vale"
    relogio.andar(6)
    assert f.processar() == 1
    assert feitos == ["relatorio"]


# ── 2. recuo exponencial ─────────────────────────────────────

def test_falha_e_repetida_com_recuo_exponencial(tmp_path):
    relogio = Relogio()
    tentativas = []

    def trabalhador(item):
        tentativas.append(relogio())
        raise RuntimeError("servico fora")

    f = _fila(tmp_path / "f.db", trabalhador, relogio,
              tentativas=4, recuo=1.0, fator=2.0)
    f.publicar("x")
    assert f.processar() == 0          # 1a tentativa falha
    assert f.processar() == 0          # nada disponivel antes de 1 s
    relogio.andar(0.9)
    assert f.processar() == 0
    relogio.andar(0.2)
    f.processar()                      # 2a, em t+1
    relogio.andar(1.9)
    f.processar()
    assert len(tentativas) == 2, "a 3a espera 2 s depois da 2a"
    relogio.andar(0.2)
    f.processar()                      # 3a, 2 s depois
    relogio.andar(4.0)
    f.processar()                      # 4a, 4 s depois
    intervalos = [round(b - a, 1) for a, b in zip(tentativas, tentativas[1:])]
    assert intervalos == [1.1, 2.1, 4.0]


def test_recuo_tem_teto_e_tremor_limitado(tmp_path):
    f = _fila(tmp_path / "f.db", None, Relogio(), recuo=1.0, fator=10.0,
              recuo_maximo=30.0, tremor=0.25)
    for tentativa in range(1, 8):
        espera = f.recuo_de(tentativa)
        base = min(30.0, 1.0 * 10.0 ** (tentativa - 1))
        assert base * 0.75 <= espera <= base * 1.25


def test_sucesso_depois_de_falha_nao_vai_para_a_carta_morta(tmp_path):
    relogio = Relogio()
    vezes = []

    def instavel(item):
        vezes.append(1)
        if len(vezes) < 3:
            raise RuntimeError("timeout")

    f = _fila(tmp_path / "f.db", instavel, relogio, tentativas=5, recuo=1.0)
    f.publicar("pagamento")
    for _ in range(3):
        f.processar()
        relogio.andar(10)
    assert f.resumo()["feitos"] == 1
    assert f.mortas() == []


# ── 3. atraso e agendamento ──────────────────────────────────

def test_atraso_e_hora_marcada(tmp_path):
    relogio = Relogio(agora=5000.0)
    feitos = []
    f = _fila(tmp_path / "f.db", feitos.append, relogio)
    f.publicar("lembrete", {"atraso": 60})
    f.agendar("fechamento", 5000.0 + 3600)
    f.publicar("agora")

    assert f.processar() == 1 and feitos == ["agora"]
    assert f.agendadas() == 2
    relogio.andar(61)
    assert f.processar() == 1 and feitos[-1] == "lembrete"
    relogio.andar(3600)
    assert f.processar() == 1 and feitos[-1] == "fechamento"


def test_prioridade_decide_entre_as_disponiveis(tmp_path):
    feitos = []
    f = _fila(tmp_path / "f.db", feitos.append, Relogio())
    f.publicar("comum")
    f.publicar("urgente", {"prioridade": 10})
    f.processar()
    assert feitos == ["urgente", "comum"]


def test_chave_evita_tarefa_repetida(tmp_path):
    f = _fila(tmp_path / "f.db", None, Relogio())
    primeiro = f.publicar("cobrar pedido 7", {"chave": "cobranca-7"})
    segundo = f.publicar("cobrar pedido 7", {"chave": "cobranca-7"})
    assert primeiro == segundo
    assert f.pendentes() == 1


# ── 4. carta morta ───────────────────────────────────────────

def test_carta_morta_guarda_o_erro_e_permite_reprocessar(tmp_path):
    relogio = Relogio()
    quebrado = {"sim": True}

    def trabalhador(item):
        if quebrado["sim"]:
            raise ValueError(f"cep invalido em {item['pedido']}")

    f = _fila(tmp_path / "f.db", trabalhador, relogio, tentativas=3, recuo=1.0)
    f.publicar({"pedido": 42})
    for _ in range(5):
        f.processar()
        relogio.andar(100)

    mortas = f.mortas()
    assert len(mortas) == 1
    morta = mortas[0]
    assert morta["item"] == {"pedido": 42}
    assert morta["tentativas"] == 3
    assert "cep invalido em 42" in morta["erro"]
    assert len(morta["historico"]) == 3
    assert f.pendentes() == 0

    quebrado["sim"] = False
    assert f.reprocessar(morta["id"]) == 1
    f.processar()
    assert f.mortas() == [] and f.resumo()["feitos"] == 1


def test_descartar_a_carta_morta(tmp_path):
    relogio = Relogio()

    def sempre_falha(item):
        raise RuntimeError("nao")

    f = _fila(tmp_path / "f.db", sempre_falha, relogio, tentativas=1)
    f.publicar("a")
    f.publicar("b")
    f.processar()
    assert len(f.mortas()) == 2
    assert f.descartar_mortas() == 2
    assert f.mortas() == []


# ── concorrencia ─────────────────────────────────────────────

def test_varios_operarios_e_duas_instancias_nao_repetem_tarefa(tmp_path):
    banco = tmp_path / "f.db"
    vistos = []
    trava = threading.Lock()

    def trabalhador(item):
        with trava:
            vistos.append(item)

    produtor = _fila(banco)
    for i in range(300):
        produtor.publicar(i)
    a = E["fila_persistente"](str(banco), trabalhador, {"operarios": 3})
    b = E["fila_persistente"](str(banco), trabalhador, {"operarios": 3})
    a.esperar(20)
    b.esperar(20)
    a.parar()
    b.parar()
    assert sorted(vistos) == list(range(300)), "tarefa repetida ou perdida"


def test_filas_com_nomes_diferentes_no_mesmo_arquivo(tmp_path):
    banco = tmp_path / "f.db"
    emails = _fila(banco, nome="emails")
    relatorios = _fila(banco, nome="relatorios")
    emails.publicar("oi")
    assert emails.pendentes() == 1 and relatorios.pendentes() == 0


# ── a mensagem, e a linguagem ────────────────────────────────

def test_item_que_nao_vira_json_e_recusado_com_mensagem_clara(tmp_path):
    f = _fila(tmp_path / "f.db")
    with pytest.raises(Exception) as erro:
        f.publicar(object())
    assert "fila persistente" in str(erro.value).lower()


def test_opcao_desconhecida_e_recusada(tmp_path):
    with pytest.raises(Exception) as erro:
        E["fila_persistente"](str(tmp_path / "f.db"), None, {"tentativa": 9})
    assert "tentativas" in str(erro.value)


def test_a_fila_persistente_em_dataforge(tmp_path):
    from dataforge.interpreter import Interpreter
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    banco = str(tmp_path / "loja.db").replace("\\", "/")
    fonte = f'''
adopt Arcane.Eventos as E
enviados := []
action enviar(pedido):
    given pedido["total"] smaller 0:
        trigger "total negativo"
    enviados.append(pedido["id"])

f := E.fila_persistente("{banco}", enviar, {{"operarios": 0, "tentativas": 2, "recuo": 0}})
f.publicar({{"id": 1, "total": 10}})
f.publicar({{"id": 2, "total": -5}})
f.processar()
f.processar()
out enviados
out len(f.mortas()), f.mortas()[0]["erro"]
'''
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
    linhas = saida.getvalue().strip().splitlines()
    assert linhas[0] == "[1]"
    assert linhas[1].startswith("1 ") and "total negativo" in linhas[1]
