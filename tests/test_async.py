"""'async' e 'await' — concorrência de verdade, e não decoração.

Durante muito tempo `async` foi uma palavra que a linguagem aceitava,
guardava em `is_async` e nunca lia. A ação era chamada como qualquer
outra e `await` devolvia o valor que já estava pronto. Escrever `async`
não deixava nada mais rápido, e a documentação dizia que sim — o pior
tipo de bug, o que compila, roda e mente.

O que estes testes cobram: que a chamada comece o trabalho na hora, que
duas chamadas de fato se sobreponham no tempo, e que o erro atravesse a
thread até o `await`.
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.lexer import tokenize          # noqa: E402
from dataforge.parser import parse            # noqa: E402
from dataforge.interpreter import Interpreter, DFTarefa   # noqa: E402
from dataforge.errors import DataForgeError   # noqa: E402


def rodar(fonte, arquivo="<teste>"):
    """Executa e devolve o que foi impresso."""
    import io
    from contextlib import redirect_stdout

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(fonte, arquivo), arquivo), arquivo)
    return buffer.getvalue().strip()


def valor_de(fonte, nome):
    """Executa e devolve uma variável global do programa."""
    interp = Interpreter()
    interp.run(parse(tokenize(fonte, "<teste>"), "<teste>"), "<teste>")
    return interp.global_env.get(nome)


# ── O que 'async' passou a valer ─────────────────────────────

def test_chamar_uma_acao_async_devolve_uma_tarefa():
    """A chamada entrega o TRABALHO, não o resultado dele.

    É a diferença que faz o paralelismo possível — e é também o engano
    mais comum de quem escreve código assíncrono.
    """
    tarefa = valor_de('''
async action buscar():
    yield 42

t := buscar()''', "t")
    assert isinstance(tarefa, DFTarefa)
    assert tarefa.aguardar() == 42


def test_await_entrega_o_valor():
    assert rodar('''
async action buscar():
    yield 42

out await buscar()''') == "42"


def test_as_tarefas_correm_ao_mesmo_tempo():
    """O teste que teria apanhado a mentira.

    Seis esperas de 0,15 s. Em sequência são 0,9 s; sobrepostas, o custo
    é o da mais lenta. A folga é generosa de propósito — a máquina do CI
    é lenta e o que se mede aqui é a diferença entre 'juntas' e 'uma de
    cada vez', que é de seis vezes.
    """
    fonte = '''
adopt Arcane.Time as T

async action esperar(n):
    T.sleep(0.15)
    yield n

tarefas := [esperar(n) cycle n in [1, 2, 3, 4, 5, 6]]
valores := await tarefas'''

    inicio = time.monotonic()
    resultado = valor_de(fonte, "valores")
    decorrido = time.monotonic() - inicio

    assert resultado == [1, 2, 3, 4, 5, 6]
    assert decorrido < 0.6, (
        f"seis esperas de 0,15 s levaram {decorrido:.2f} s — "
        f"em paralelo custam 0,15 s, uma de cada vez custam 0,9 s")


def test_uma_de_cada_vez_realmente_custa_a_soma():
    """O contraponto do anterior: sem a medição, ele não prova nada.

    Se 'sleep' não estivesse esperando de verdade, o teste de cima
    passaria por engano.
    """
    fonte = '''
adopt Arcane.Time as T

async action esperar(n):
    T.sleep(0.15)
    yield n

seq := []
cycle n in [1, 2, 3]:
    seq.append(await esperar(n))'''

    inicio = time.monotonic()
    assert valor_de(fonte, "seq") == [1, 2, 3]
    decorrido = time.monotonic() - inicio
    assert decorrido >= 0.4, (
        f"três esperas de 0,15 s em sequência levaram {decorrido:.2f} s — "
        f"deveriam custar 0,45 s")


def test_a_tarefa_comeca_antes_do_await():
    """Eager, não preguiçosa.

    Fosse preguiçosa, `[f(x) cycle x in xs]` não adiantaria nada: cada
    uma só começaria quando o `await` chegasse nela, uma de cada vez.
    """
    saida = rodar('''
adopt Arcane.Time as T

async action marcar():
    T.sleep(0.2)
    yield "fim"

t := marcar()
T.sleep(0.4)
// se so comecasse agora, ainda estaria rodando
out t.pronta()
out await t''')
    assert saida.split("\n")[0] == "yes"


# ── Erros atravessam a thread ────────────────────────────────

def test_o_trigger_de_dentro_chega_a_quem_aguarda():
    saida = rodar('''
async action falhar():
    trigger "a busca falhou"

monitor:
    await falhar()
handle e:
    out e.message''')
    assert saida == "a busca falhou"


def test_o_erro_e_relevantado_na_linha_do_await():
    """E não na chamada — é no `await` que quem escreveu pode reagir."""
    saida = rodar('''
async action dividir():
    yield 1 / 0

t := dividir()
out "a chamada nao explodiu"
monitor:
    await t
handle e:
    out e.type''')
    assert saida.split("\n") == ["a chamada nao explodiu", "DivisionByZeroError"]


def test_a_aridade_e_conferida_na_chamada_e_nao_na_thread():
    """O erro de aridade tem que sair com a linha de quem chamou.

    Conferir dentro da tarefa mandaria o erro para outra thread, e ele
    só apareceria num `await` que talvez nunca aconteça.
    """
    saida = rodar('''
async action dobro(n):
    yield n * 2

monitor:
    dobro(1, 2, 3)
handle e:
    out "pego na chamada"''')
    assert saida == "pego na chamada"


def test_tarefa_esquecida_nao_derruba_o_programa():
    assert rodar('''
async action falhar():
    trigger "ninguem vai ver"

esquecida := falhar()
out "segui em frente"''') == "segui em frente"


# ── Usar a tarefa sem 'await' dá uma mensagem útil ───────────

@pytest.mark.parametrize("uso", [
    'out t["nome"]',
    'out t + 1',
])
def test_usar_a_tarefa_sem_await_diz_a_palavra_que_faltou(uso):
    """'A dftarefa cannot be indexed' está correto e não ajuda ninguém."""
    with pytest.raises(DataForgeError) as capturado:
        rodar(f'''
async action buscar():
    yield 1

t := buscar()
{uso}''')
    texto = str(capturado.value) + str(getattr(capturado.value, "dica", ""))
    assert "async" in texto
    assert "await" in texto
    assert "DFTarefa" not in texto, "o nome da classe do Python vazou"


# ── Precedência: 'await' aperta como operador unário ─────────

def test_await_aperta_mais_que_a_comparacao():
    """`await f() is "ok"` é `(await f()) is "ok"`.

    Com `parse_expression`, `await` engolia a comparação inteira e
    aguardava o BOOLEANO dela. Ficou escondido enquanto `await` era
    identidade: comparar antes ou depois de não fazer nada dá no mesmo.
    """
    assert rodar('''
async action ok():
    yield "ok"

out await ok() is "ok"''') == "yes"


def test_await_de_um_valor_comum_devolve_o_valor():
    """Trocar uma ação 'async' por uma comum não deve quebrar quem chama."""
    assert rodar('out await 7') == "7"
    assert rodar('out await [1, 2]') == "[1, 2]"


def test_await_de_um_cluster_aguarda_todas():
    assert rodar('''
async action dobro(n):
    yield n * 2

out await [dobro(1), dobro(2), dobro(3)]''') == "[2, 4, 6]"


# ── Composição ───────────────────────────────────────────────

def test_async_dentro_de_async():
    """Uma tarefa aguardando outra não pode travar.

    É por isso que cada chamada ganha uma thread própria em vez de uma
    vaga numa piscina de tamanho fixo: com piscina, as trabalhadoras
    ficariam todas bloqueadas esperando uma vaga que só elas poderiam
    liberar.
    """
    assert rodar('''
async action interna(n):
    yield n + 1

async action externa(n):
    a := await interna(n)
    b := await interna(a)
    yield b

out await externa(1)''') == "3"


def test_muitas_tarefas_aninhadas_nao_travam():
    """Vinte tarefas, cada uma aguardando outra. Uma piscina travaria."""
    assert rodar('''
async action folha(n):
    yield n

async action galho(n):
    yield await folha(n) * 2

out await [galho(n) cycle n in range(20)] >> distill a, v: a + v 0''') == "380"


def test_o_tipo_de_retorno_declarado_continua_valendo():
    assert rodar('''
async action dobro(n: Integer) -> Integer:
    yield n * 2

out await dobro(21)''') == "42"


def test_metodo_async_de_um_blueprint():
    assert rodar('''
blueprint Api:
    async action buscar(id):
        yield $"item {id}"

a := spawn Api()
out await a.buscar(3)''') == "item 3"


# ── A pilha de chamadas é por thread ─────────────────────────

def test_tarefas_paralelas_nao_somam_a_profundidade_uma_da_outra():
    """Compartilhada, a profundidade era a soma de todas as threads.

    Vinte tarefas de cinquenta quadros cada pareciam mil ao guarda de
    recursão, e o programa morria com 'stack overflow' sem ter recursão
    nenhuma.
    """
    assert rodar('''
action fundo(n):
    given n is 0:
        yield 0
    yield fundo(n - 1) + 1

async action trabalho():
    yield fundo(100)

out await [trabalho() cycle n in range(20)] >> distill a, v: a + v 0''') == "2000"


# ── Pilha: recursão profunda não pode matar o processo ───────

def test_recursao_no_limite_da_erro_da_linguagem_e_nao_segfault():
    """No Python 3.10 e no 3.11 isto MATAVA o processo.

    Uma chamada da linguagem custa cerca de nove quadros do Python, e
    `MAX_CALL_DEPTH` permite mil — perto de nove mil quadros. Cabem nos
    8 MB da thread principal? No macOS com 3.10, não: o processo morria
    com 'Segmentation fault', sem mensagem nenhuma, exatamente onde
    deveria sair o erro da linguagem.

    O 3.12 não sofria porque a CPython passou a vigiar a pilha de C por
    conta própria. Como a linguagem promete 3.10, a rede tem que ser
    nossa: o programa roda numa thread com pilha suficiente.
    """
    from dataforge.errors import StackOverflowError_

    with pytest.raises(StackOverflowError_):
        rodar('''
action r(n):
    yield r(n + 1)

r(1)''')


def test_recursao_profunda_dentro_de_uma_tarefa_async():
    """A thread de uma tarefa também precisa da pilha.

    No macOS uma thread comum nasce com 512 KB contra os 8 MB da
    principal. Sem reservar, uma recursão que funciona no corpo do
    programa derrubaria o processo só por estar dentro de um `async`.
    """
    assert rodar('''
action fundo(n):
    given n is 0:
        yield 0
    yield fundo(n - 1) + 1

async action trabalho():
    yield fundo(400)

out await trabalho()''') == "400"


def test_o_programa_roda_numa_thread_provisionada():
    """A garantia de cima, dita diretamente."""
    from dataforge import interpreter as m

    assert m._PILHA >= 64 * 1024 * 1024 or m._PILHA == -1, (
        f"a pilha reservada ficou em {m._PILHA} — o Windows 3.10 gasta "
        f"mais de 6,5 KB por quadro, e uma recursao no limite pede "
        f"~10 mil quadros")

    visto = {}
    interp = Interpreter()
    interp.global_env.set_local("marcar", lambda: visto.setdefault(
        "provisionada", getattr(m._PROVISIONADA, "sim", False)))
    interp.run(parse(tokenize("marcar()", "<t>"), "<t>"), "<t>")
    assert visto["provisionada"] is True


def test_a_recursao_no_limite_da_linguagem_cabe_na_pilha():
    """A garantia numérica, em vez de descobrir com o processo morrendo.

    `MAX_CALL_DEPTH` permite mil chamadas. Se a pilha não couber nelas, o
    guarda da linguagem nunca chega a disparar e o processo morre sem
    mensagem — foi o que aconteceu no Windows 3.10, com 32 MB, já na
    quingentésima chamada.

    Aqui a falha vira um número: chega-se a um fio do limite, e o que
    falta aparece no `assert` em vez de num "fatal exception".
    """
    from dataforge.interpreter import Interpreter as _I

    alvo = _I.MAX_CALL_DEPTH - 40
    assert rodar(f'''
action contar(n):
    given n smaller_eq 0:
        yield 0
    yield 1 + contar(n - 1)

out contar({alvo})''') == str(alvo)
