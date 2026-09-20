"""A travessia de processo — o unico caminho para mais de um nucleo.

'map_processos' era a unica forma de usar mais de um nucleo, e ela
falhava SEMPRE, com uma mensagem que mandava consertar o que ja estava
certo ("declare a acao no topo do arquivo" — ela estava). O objeto que
o pickle nao copiava era um lambda da propria biblioteca, alcancado
pela cadeia de escopos a partir do fechamento da acao.

Por isso os testes daqui nao conferem que a chamada nao estourou: eles
conferem que o RESULTADO esta certo e que ele veio de processos de
verdade — e, do outro lado, que o que nao pode atravessar e dito pelo
nome.
"""

import io
import os
import sys
import time
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import DataForgeError  # noqa: E402
from dataforge.interpreter import Interpreter  # noqa: E402
from dataforge.lexer import tokenize  # noqa: E402
from dataforge.parser import parse  # noqa: E402
from dataforge.travessia import nomes_livres  # noqa: E402


def run(source: str) -> str:
    interp = Interpreter()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        interp.run(parse(tokenize(source), "<travessia>"))
    return buffer.getvalue().strip()


CABECA = "adopt Arcane.Concurrent as P\n"


# ═══ A acao atravessa ══════════════════════════════════════

def test_uma_acao_do_arquivo_atravessa():
    """O caso que falhava sempre: uma acao no topo, sem nada em volta."""
    assert run(CABECA + """
action quadrado(n):
    yield n * n

out P.map_processos(quadrado, [1, 2, 3, 4, 5])
""") == "[1, 4, 9, 16, 25]"


def test_um_lambda_tambem_atravessa():
    """Um lambda de DataForge e uma acao: o que viaja e a declaracao."""
    assert run(CABECA + """
out P.map_processos(lambda x => x * 3, [1, 2, 3])
""") == "[3, 6, 9]"


def test_a_ordem_da_entrada_e_a_da_saida():
    """Reassociar item e resultado e onde se erra."""
    assert run(CABECA + """
action eco(n):
    yield n

out P.map_processos(eco, [9, 1, 8, 2, 7, 3])
""") == "[9, 1, 8, 2, 7, 3]"


def test_lista_vazia_nao_abre_processo_nenhum():
    assert run(CABECA + """
action f(n):
    yield n

out P.map_processos(f, [])
""") == "[]"


# ═══ O que a acao LE vai junto ═════════════════════════════

def test_um_nome_de_fora_vai_junto():
    assert run(CABECA + """
steady TAXA := 10

action com_taxa(n):
    yield n * TAXA

out P.map_processos(com_taxa, [1, 2, 3])
""") == "[10, 20, 30]"


def test_uma_acao_que_chama_outra_leva_a_outra():
    assert run(CABECA + """
action dobro(n):
    yield n * 2

action quadruplo(n):
    yield dobro(dobro(n))

out P.map_processos(quadruplo, [1, 2, 3])
""") == "[4, 8, 12]"


def test_um_modulo_adotado_vai_pelo_nome():
    """O modulo nao e copiado: o filho o carrega de novo, pelo nome.

    Copia-lo seria impossivel — ele tem funcoes anonimas dentro, e foi
    exatamente uma delas que quebrava a travessia inteira.
    """
    assert run(CABECA + """
adopt Arcane.Math as M

action raiz(n):
    yield M.floor(M.sqrt(n))

out P.map_processos(raiz, [4, 9, 17])
""") == "[2, 3, 4]"


def test_uma_acao_recursiva_se_encontra_do_outro_lado():
    assert run(CABECA + """
action fat(n):
    given n <= 1:
        yield 1
    yield n * fat(n - 1)

out P.map_processos(fat, [3, 4, 5])
""") == "[6, 24, 120]"


# ═══ Os dados atravessam nos dois sentidos ═════════════════

def test_um_record_vai_e_volta_como_o_mesmo_tipo():
    """O tipo que volta tem de ser o DESTE arquivo.

    Se o filho devolvesse uma copia do tipo, 'with' — que confere os
    campos contra o record — recusaria o proprio resultado.
    """
    assert run(CABECA + """
record Ponto:
    x: Integer
    y: Integer

action girar(p):
    yield Ponto(p.y, p.x)

vindos := P.map_processos(girar, [Ponto(1, 2), Ponto(3, 4)])
out vindos
out vindos[0] with {"x": 9}
""") == "[Ponto(x: 2, y: 1), Ponto(x: 4, y: 3)]\nPonto(x: 9, y: 1)"


def test_um_enum_atravessa_e_continua_comparavel():
    assert run(CABECA + """
enum Faixa:
    Baixa
    Alta

action faixa_de(n):
    yield Faixa.Alta given n bigger 10 otherwise Faixa.Baixa

vindos := P.map_processos(faixa_de, [1, 50])
out vindos[0] is Faixa.Baixa
out vindos[1] is Faixa.Alta
""") == "yes\nyes"


def test_uma_instancia_de_blueprint_atravessa():
    assert run(CABECA + """
blueprint Caixa(peso):
    action dobro():
        yield self.peso * 2

action pesar(c):
    yield c.dobro()

out P.map_processos(pesar, [spawn Caixa(2), spawn Caixa(5)])
""") == "[4, 10]"


def test_um_vault_aninhado_atravessa_inteiro():
    assert run(CABECA + """
action total(v):
    yield sum(v["itens"])

out P.map_processos(total, [{"itens": [1, 2]}, {"itens": [3, 4, 5]}])
""") == "[3, 12]"


# ═══ O que NAO atravessa, e como isso e dito ═══════════════

def test_o_recurso_que_a_acao_usa_e_acusado_pelo_NOME():
    """A mensagem antiga culpava quem escreveu, e nomeava um lambda da
    biblioteca. A nova nomeia a variavel, e diz o que ela guarda."""
    with pytest.raises(DataForgeError) as exc:
        run(CABECA + """
adopt Arcane.Database as DB

db := DB.connect(":memory:")

action contar(n):
    yield len(DB.query(db, "select 1")) + n

out P.map_processos(contar, [1, 2])
""")
    texto = str(exc.value) + exc.value.nota + exc.value.dica
    assert "'db'" in str(exc.value)
    assert "connection to a database" in texto
    assert "another process" in texto
    # Nunca o vocabulario do pickle, nem o de um objeto da biblioteca.
    assert "pickle" not in texto.lower()
    assert "lambda" not in texto.lower()


def test_o_recurso_que_a_acao_NAO_usa_nao_atrapalha():
    """A varredura de nomes livres captura de mais, de proposito.

    Um banco aberto no arquivo nao pode impedir que uma acao que nem o
    menciona use os outros nucleos — e essa e a diferenca entre uma
    analise generosa que falha tarde e uma que falha cedo e errado.
    """
    assert run(CABECA + """
adopt Arcane.Database as DB

db := DB.connect(":memory:")
trava := P.mutex()

action soma(n):
    yield n + 1

out P.map_processos(soma, [1, 2, 3])
""") == "[2, 3, 4]"


def test_a_acao_abre_o_proprio_recurso_do_outro_lado():
    """A dica diz 'abra dentro da acao'. Ela precisa ser verdade."""
    assert run(CABECA + """
adopt Arcane.Database as DB

action conta(n):
    meu := DB.connect(":memory:")
    DB.execute(meu, "create table t (n integer)")
    DB.execute(meu, "insert into t values (?)", [n])
    yield len(DB.query(meu, "select * from t")) * n

out P.map_processos(conta, [2, 3])
""") == "[2, 3]"


def test_o_erro_de_dentro_volta_dizendo_onde_aconteceu():
    """Sem isso, o erro parece ter acontecido na linha do
    'map_processos' — a unica que este processo executou."""
    with pytest.raises(DataForgeError) as exc:
        run(CABECA + """
action quebra(n):
    yield n / 0

out P.map_processos(quebra, [1, 2])
""")
    assert "another process" in exc.value.nota


def test_o_nome_errado_dentro_da_acao_ainda_sugere_o_certo():
    """A tradução do erro não pode comer a dica que já existia."""
    with pytest.raises(DataForgeError) as exc:
        run(CABECA + """
adopt Arcane.Math as M

action f(n):
    yield M.sqrtt(n)

out P.map_processos(f, [4])
""")
    assert "sqrt" in exc.value.dica


# ═══ Mais de um nucleo, medido ═════════════════════════════

@pytest.mark.skipif((os.cpu_count() or 1) < 4,
                    reason="menos de 4 nucleos: nao ha o que medir")
def test_processos_usam_mais_de_um_nucleo_e_threads_nao():
    """A prova de que a travessia entrega o que promete.

    A comparacao e a RAZAO contra a serie medida na mesma maquina — um
    limite absoluto mediria a maquina, e nao o paralelismo. E o
    trabalho por item e grande de proposito: com pouco trabalho o custo
    de iniciar os processos domina, e a razao mede a partida.

    As threads entram na conta porque sao a metade que prova a outra:
    elas nao passam de ~1x com trabalho de CPU, por causa do GIL, e e
    isso que torna os processos o unico caminho.

    **O tamanho do bloco subiu de 150 mil para 300 mil**, e a razao e
    o metodo de partida. Enquanto o Linux usava 'fork', o trabalhador
    nascia de graca; desde que ele passou a nascer limpo — por causa da
    conexao SQLite que o fork herdava —, a partida virou um custo fixo
    e visivel. Medido no CI com blocos de 150 mil: 1,21x a 1,42x no
    Linux e **1,02x** no Windows, contra 2,37x nesta maquina. O que
    reprovava nao era o paralelismo: era a partida ocupando metade da
    medida.

    Duas coisas mudaram por isso. O 'forkserver' passou a ser o metodo
    no Linux (um servidor limpo que importa o interpretador UMA vez, e
    de onde cada trabalhador sai por fork) e o bloco dobrou, para que a
    conta meca o trabalho. Medido aqui com 300 mil: 3,16x.
    """
    fonte = CABECA + """
adopt Arcane.Time as Time

action cpu(n):
    s := 0
    cycle i from 1 to n:
        s += i * i
    yield s

blocos := [300000, 300000, 300000, 300000]

t := Time.monotonic()
serie := [cpu(b) cycle b in blocos]
ms_serie := Time.monotonic() - t

t := Time.monotonic()
com_threads := P.map(cpu, blocos)
ms_threads := Time.monotonic() - t

t := Time.monotonic()
com_processos := P.map_processos(cpu, blocos)
ms_processos := Time.monotonic() - t

assert com_processos is serie
assert com_threads is serie
out round(ms_serie / ms_processos, 2)
out round(ms_serie / ms_threads, 2)
"""
    saida = run(fonte).splitlines()
    ganho_processos, ganho_threads = float(saida[0]), float(saida[1])
    assert ganho_processos > 1.5, (
        f"processos nao ganharam da serie: {ganho_processos}x — "
        f"ou a travessia voltou a rodar em um nucleo so")
    assert ganho_threads < 1.4, (
        f"threads ganharam {ganho_threads}x em trabalho de CPU; "
        f"se o GIL sumiu, este teste e que precisa mudar")


# ═══ Os nomes livres ═══════════════════════════════════════

def livres(fonte, params=()):
    corpo = parse(tokenize(fonte), "<t>").body
    return nomes_livres(corpo, set(params))


def test_um_nome_criado_antes_de_ser_lido_nao_e_livre():
    assert "total" not in livres("total := 0\nout total + 1")


def test_uma_atribuicao_composta_LE_antes_de_escrever():
    """'total += 1' sobre um nome de fora precisa do valor de fora."""
    assert "total" in livres("total += 1")


def test_a_variavel_do_laco_nao_e_livre():
    assert "i" not in livres("cycle i from 1 to 3:\n    out i")
    assert "x" not in livres("cycle x in [1]:\n    out x")


def test_o_parametro_nao_e_livre():
    assert "n" not in livres("out n * 2", params=["n"])


def test_o_tipo_de_uma_anotacao_conta_como_nome():
    """Sem isto, 'action f(p: Pedido)' atravessava sem o record."""
    assert "Pedido" in livres("p: Pedido := void")


def test_o_erro_de_um_handle_nao_e_livre():
    assert "e" not in livres(
        "monitor:\n    out 1\nhandle Error as e:\n    out e")


def test_o_que_o_padrao_captura_nao_e_livre():
    corpo = ("match v:\n"
             "    point [a, b]:\n"
             "        out a + b\n"
             "    default:\n"
             "        out 0")
    nomes = livres(corpo)
    assert "a" not in nomes and "b" not in nomes
    assert "v" in nomes


# ═══ O pool reaproveitado ══════════════════════════════════

def test_o_pool_reaproveita_os_processos():
    """Iniciar um processo custa mais de cem milissegundos.

    Num script isso acontece uma vez; num servidor, a cada pedido — e
    ai a conta nao fecha. A comparacao e entre a PRIMEIRA chamada, que
    paga a partida, e a segunda, que nao: sao as duas medidas na mesma
    maquina, no mesmo instante.

    O tamanho do bloco e escolhido, e nao arbitrario: e o que faz a
    PARTIDA dominar a primeira chamada. Medido nesta maquina, com pool
    de 4 e spawn:

        40000 por bloco ....  2,59x   (1a 137 ms, 2a  53 ms)
         8000 por bloco ....  8,90x   (1a  94 ms, 2a  11 ms)
         2000 por bloco .... 28,64x   (1a  87 ms, 2a   3 ms)

    Com 40000 o trabalho de CPU dominava, a razao encostava no limite e
    o teste reprovava no CI com **1,08** — o pool estava certo, e a
    medida media a carga. Com 2000 a segunda chamada vira 3 ms, e ai o
    ruido do relogio e que decide. 8000 e o meio: margem de sete vezes
    sobre o limite, e uma segunda chamada ainda mensuravel.
    """
    saida = run(CABECA + """
adopt Arcane.Time as Time

action cpu(n):
    s := 0
    cycle i from 1 to n:
        s += i * i
    yield s

pool := P.pool_processos(4)
blocos := [8000, 8000, 8000, 8000]

t := Time.monotonic()
a := pool.map(cpu, blocos)
primeiro := Time.monotonic() - t

t := Time.monotonic()
b := pool.map(cpu, blocos)
segundo := Time.monotonic() - t

pool.fechar()
assert a is b, "o mesmo trabalho deu resultados diferentes"
out round(primeiro / segundo, 2)
""")
    assert float(saida) > 1.2, (
        f"a segunda chamada nao foi mais rapida que a primeira ({saida}x): "
        f"o pool esta reabrindo os processos")


def test_o_pool_fechado_recusa_e_diz_por_que():
    with pytest.raises(DataForgeError) as exc:
        run(CABECA + """
action f(n):
    yield n

pool := P.pool_processos(2)
pool.fechar()
pool.map(f, [1])
""")
    assert "closed" in exc.value.message
    assert "P.pool_processos()" in exc.value.dica


def test_uma_chamada_so_vai_para_outro_processo():
    """'P.processo' e o 'thread' da linguagem, num nucleo de verdade."""
    assert run(CABECA + """
action somar(n):
    yield n + 1

tarefa := P.processo(somar, 41)
out tarefa.esperar()
""") == "42"


def test_o_record_atravessa_pelo_pool_tambem():
    assert run(CABECA + """
record Caixa:
    peso: Integer

action pesar(c):
    yield Caixa(c.peso * 2)

pool := P.pool_processos(2)
out pool.map(pesar, [Caixa(1), Caixa(2)])
pool.fechar()
""") == "[Caixa(peso: 2), Caixa(peso: 4)]"


def test_o_erro_de_uma_tarefa_de_processo_volta_traduzido():
    with pytest.raises(DataForgeError) as exc:
        run(CABECA + """
action quebra(n):
    yield n / 0

out P.processo(quebra, 1).esperar()
""")
    assert "another process" in exc.value.nota


def test_um_membro_de_enum_leva_os_metodos_do_enum():
    """Ele atravessava como CÓPIA, e chegava sem o enum a que pertence.

    O sintoma só aparecia depois da volta: `Faixa.Alta.dobro()` funciona
    aqui, atravessa, volta, e então responde "has no member 'dobro'".

    Hoje ele viaja pelo enum e pelo nome — os dois lados devolvem o
    membro de verdade.
    """
    assert run(CABECA + """
enum Faixa:
    Baixa := 1
    Alta := 10

    action dobro():
        yield self.value * 2

action classificar(n):
    yield Faixa.Alta given n bigger 5 otherwise Faixa.Baixa

vindos := P.map_processos(classificar, [1, 9])
out vindos[1].dobro()

action usar_metodo(f):
    yield f.dobro()

out P.map_processos(usar_metodo, [Faixa.Baixa, Faixa.Alta])
""") == "20\n[2, 20]"
