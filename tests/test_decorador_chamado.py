"""`@f` e `@f()` não são a mesma coisa.

Com parênteses — mesmo vazios — o decorador é uma fábrica: `f()(alvo)`.
Tratar `@f()` como `@f` fazia `@app.texto()` virar `app.texto(acao)`, e
a ação caía no parâmetro do padrão: uma regex que nunca casa, e um bot
que fica calado sem erro nenhum.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from tests._df import rodar  # noqa: E402


def test_as_tres_formas(tmp_path):
    r = rodar(tmp_path, '''log := []
action anotar(alvo):
    log.append("direto")
    yield alvo
action fabrica(rotulo := "padrao"):
    action aplicar(alvo):
        log.append($"fabrica:{rotulo}")
        yield alvo
    yield aplicar
@anotar
action a():
    yield 1
@fabrica()
action b():
    yield 2
@fabrica("x")
action c():
    yield 3
out log, a(), b(), c()
''')
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "[direto, fabrica:padrao, fabrica:x] 1 2 3"


def test_o_bot_com_texto_vazio_responde(tmp_path):
    r = rodar(tmp_path, '''adopt Arcane.Telegram as Tg
app := Tg.app("123456:TESTE-exemplo")
mark @app.texto()
action eco(ctx):
    ctx.responder($"eco: {ctx.texto}")
t := Tg.testar(app)
t.mandar("oi")
out t.ultima()
''')
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "eco: oi"
