"""SLO, desligamento gracioso, a próxima versão calculada, e atores."""
import os
import signal
import subprocess
import sys
import threading
import time

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402
from tests._df import rodar  # noqa: E402

O = get_module("Arcane.Observar")
Abi = get_module("Arcane.Abi")
P = get_module("Arcane.Concurrent")


# ── SLO ───────────────────────────────────────────────────────

def test_orcamento_de_erro():
    o = O["orcamento"](0.999, 1_000_000, 400)
    assert o["permitidas"] == 1000.0 and o["consumido"] == 0.4
    assert o["restante"] == 0.6 and not o["esgotado"]
    assert O["orcamento"](0.999, 1000, 2)["esgotado"]


def test_sem_trafego_nao_ha_queima():
    assert O["queima"](0.99, 0, 0) == 0.0
    assert O["orcamento"](0.99, 0, 0)["disponibilidade"] == 1.0


def test_queima_de_14_4_e_o_limiar_classico():
    # 1,44% de erro com objetivo de 99,9% = 14,4x
    assert O["queima"](0.999, 10_000, 144) == 14.4


def test_alerta_so_com_as_duas_janelas():
    longa = {"total": 10_000, "falhas": 200}
    assert O["alerta_slo"](0.999, longa, {"total": 800, "falhas": 20})["disparar"]
    passou = O["alerta_slo"](0.999, longa, {"total": 800, "falhas": 1})
    assert not passou["disparar"] and "ja passou" in passou["motivo"]
    pico = O["alerta_slo"](0.999, {"total": 10_000, "falhas": 5},
                           {"total": 800, "falhas": 20})
    assert not pico["disparar"] and "pico" in pico["motivo"]


@pytest.mark.parametrize("objetivo", [0, 1, 1.5, -0.1])
def test_objetivo_fora_de_0_e_1_e_recusado(objetivo):
    with pytest.raises(Exception, match="fracao entre 0 e 1"):
        O["queima"](objetivo, 10, 1)


def test_contagem_impossivel_e_recusada():
    with pytest.raises(Exception, match="impossivel"):
        O["orcamento"](0.99, 10, 11)


# ── desligamento gracioso ─────────────────────────────────────

PROGRAMA_LONGO = '''adopt Arcane.Inicio as Inicio
adopt Arcane.IO as IO
saida := env_var("SAIDA")
Inicio.ao_encerrar(lambda => IO.append(saida, "banco\\n"))
Inicio.ao_encerrar(lambda => IO.append(saida, "fila\\n"))
voltas := 0
persist not Inicio.encerrando() and voltas smaller 400:
    sleep(25)
    voltas += 1
'''


@pytest.mark.skipif(sys.platform.startswith("win"),
                    reason="o Windows nao entrega SIGTERM a um processo filho")
def test_sigterm_roda_os_finalizadores_ao_contrario_e_sai_com_143(tmp_path):
    programa = tmp_path / "longo.df"
    programa.write_text(PROGRAMA_LONGO, encoding="utf-8")
    saida = tmp_path / "saida.txt"
    p = subprocess.Popen([sys.executable, "-m", "dataforge", "run", str(programa)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, encoding="utf-8", cwd=RAIZ,
                         env=dict(os.environ, SAIDA=str(saida), NO_COLOR="1"))
    # A espera é pelo arquivo do programa existir e o laço estar girando:
    # a saída padrão num cano fica em buffer, e ler dela não sincroniza.
    time.sleep(1.5)
    p.send_signal(signal.SIGTERM)
    p.communicate(timeout=20)
    assert p.returncode == 143
    assert saida.read_text(encoding="utf-8") == "fila\nbanco\n"


def test_fim_normal_tambem_roda_os_finalizadores(tmp_path):
    saida = tmp_path / "saida.txt"
    r = rodar(tmp_path, PROGRAMA_LONGO.replace("smaller 400", "smaller 1"),
              SAIDA=str(saida))
    assert r.returncode == 0, r.stderr
    assert saida.read_text(encoding="utf-8") == "fila\nbanco\n"


def test_finalizador_que_falha_nao_impede_os_outros(tmp_path):
    saida = tmp_path / "saida.txt"
    r = rodar(tmp_path, '''adopt Arcane.Inicio as Inicio
adopt Arcane.IO as IO
Inicio.ao_encerrar(lambda => IO.append(env_var("SAIDA"), "fechou\\n"))
Inicio.ao_encerrar(lambda => 1 / 0)
''', SAIDA=str(saida))
    assert saida.read_text(encoding="utf-8") == "fechou\n"
    assert "finalizador falhou" in r.stderr


# ── a próxima versão ──────────────────────────────────────────

def _versoes(tmp_path):
    v1 = tmp_path / "v1.df"
    v1.write_text("action somar(a, b):\n    yield a + b\n"
                  "action dobro(x):\n    yield x * 2\nrelay somar, dobro\n",
                  encoding="utf-8")
    quebra = tmp_path / "quebra.df"
    quebra.write_text("action somar(a, b):\n    yield a + b\nrelay somar\n",
                      encoding="utf-8")
    soma = tmp_path / "soma.df"
    soma.write_text(v1.read_text(encoding="utf-8").replace(
        "relay somar, dobro", "action triplo(x):\n    yield x * 3\n"
        "relay somar, dobro, triplo"), encoding="utf-8")
    return str(v1), str(quebra), str(soma)


@pytest.mark.parametrize("atual,qual,esperada", [
    ("1.4.2", "quebra", "2.0.0"), ("1.4.2", "soma", "1.5.0"),
    ("1.4.2", "igual", "1.4.3"), ("0.4.2", "quebra", "0.5.0"),
    ("0.4.2", "soma", "0.4.3"), ("v2.0.0", "soma", "2.1.0"),
])
def test_proxima_versao(tmp_path, atual, qual, esperada):
    v1, quebra, soma = _versoes(tmp_path)
    depois = {"quebra": quebra, "soma": soma, "igual": v1}[qual]
    assert Abi["proxima_versao"](atual, v1, depois)["proxima"] == esperada


def test_versao_invalida_e_recusada(tmp_path):
    v1, _q, _s = _versoes(tmp_path)
    with pytest.raises(Exception, match="nao e uma versao"):
        Abi["proxima_versao"]("1.0", v1, v1)


def test_changelog_separa_quebra_de_acrescimo(tmp_path):
    v1, quebra, soma = _versoes(tmp_path)
    texto = Abi["changelog"](v1, quebra, "2.0.0")
    assert texto.startswith("## 2.0.0") and "### Quebra compatibilidade" in texto
    assert "`dobro`" in texto
    assert "### Adicionado" in Abi["changelog"](v1, soma)
    assert "Nenhuma mudanca" in Abi["changelog"](v1, v1)


# ── atores ────────────────────────────────────────────────────

def test_ator_nao_perde_atualizacao_entre_threads():
    a = P["ator"](lambda e, m: e + m, 0)
    ts = [threading.Thread(target=lambda: [a.enviar(1) for _ in range(5000)])
          for _ in range(4)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert a.consultar(lambda e: e) == 20000


def test_consulta_ve_tudo_que_foi_enviado_antes():
    a = P["ator"](lambda e, m: (time.sleep(0.001), e + [m])[1], [])
    for i in range(50):
        a.enviar(i)
    assert a.consultar(len) == 50


def test_erro_na_mensagem_e_anotado_e_o_estado_fica():
    avisos = []
    a = P["ator"](lambda e, m: e / m, 10, "div", lambda erro, m: avisos.append(m))
    a.enviar(0)
    a.enviar(2)
    assert a.consultar(lambda e: e) == 5.0
    assert a.falhas()[0]["mensagem"] == 0 and avisos == [0]


def test_parar_trata_o_que_esta_na_caixa_e_recusa_o_resto():
    a = P["ator"](lambda e, m: e + m, 0)
    for _ in range(100):
        a.enviar(1)
    assert a.parar() == 100 and not a.vivo()
    with pytest.raises(Exception, match="ja parou"):
        a.enviar(1)


def test_ator_na_linguagem(tmp_path):
    r = rodar(tmp_path, '''adopt Arcane.Concurrent as P
action conta(saldo, msg):
    given msg["valor"] bigger saldo and msg["tipo"] is "sacar":
        trigger "saldo insuficiente"
    yield saldo + msg["valor"] given msg["tipo"] is "depositar" otherwise saldo - msg["valor"]
a := P.ator(conta, 0)
action encher():
    cycle i from 1 to 300:
        a.enviar({"tipo": "depositar", "valor": 1})
parallel:
    encher()
    encher()
a.enviar({"tipo": "sacar", "valor": 1000})
out a.parar(), len(a.falhas())
''')
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "600 1"
