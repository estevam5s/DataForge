"""Metodos magicos, slots e MRO.

Um metodo magico e um gancho: a linguagem o procura quando uma operacao
acontece. Se o gancho nao for consultado, o recurso nao existe — e o
programa segue funcionando do jeito antigo, sem avisar. Por isso quase
todo teste aqui confere que a operacao REALMENTE passou pelo metodo.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge import magicos                          # noqa: E402
from dataforge.errors import DataForgeError            # noqa: E402
from dataforge.interpreter import Interpreter          # noqa: E402
from dataforge.lexer import tokenize                   # noqa: E402
from dataforge.parser import parse                     # noqa: E402


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<teste>"), "<teste>"), "<teste>")
    return saida.getvalue().strip()


def erro_de(fonte):
    with pytest.raises(DataForgeError) as exc:
        rodar(fonte)
    return str(exc.value)


VETOR = '''
blueprint Vetor(x, y):
    action __add__(o):
        yield spawn Vetor(self.x + o.x, self.y + o.y)
    action __sub__(o):
        yield spawn Vetor(self.x - o.x, self.y - o.y)
    action __mul__(k):
        yield spawn Vetor(self.x * k, self.y * k)
    action __rmul__(k):
        yield spawn Vetor(self.x * k, self.y * k)
    action __neg__():
        yield spawn Vetor(0 - self.x, 0 - self.y)
    action __eq__(o):
        yield self.x is o.x and self.y is o.y
    action __lt__(o):
        yield self.x * self.x + self.y * self.y smaller o.x * o.x + o.y * o.y
    action __str__():
        yield $"({self.x}, {self.y})"
    action __len__():
        yield 2
    action __getitem__(i):
        yield self.x given i is 0 otherwise self.y
'''


# ═══ A tabela ══════════════════════════════════════════════

def test_o_pedido_de_setenta_foi_cumprido():
    """O Python tem pouco mais de 70; a tabela cobre isso."""
    assert magicos.total() > 70


def test_todo_magico_tem_grupo_e_descricao():
    for nome, (grupo, aridade, descricao) in magicos.MAGICOS.items():
        assert grupo, nome
        assert descricao, nome
        assert isinstance(aridade, int), nome


def test_nomes_seguem_a_convencao():
    for nome in magicos.MAGICOS:
        assert magicos.e_magico(nome), nome
    assert not magicos.e_magico("soma")
    assert not magicos.e_magico("_privado")


def test_todo_operador_aponta_para_magico_da_tabela():
    for tabela in (magicos.POR_OPERADOR, magicos.POR_COMPARACAO,
                   magicos.POR_UNARIO):
        for simbolo, nome in tabela.items():
            assert nome in magicos.MAGICOS, f"{simbolo} -> {nome}"


def test_todo_refletido_e_no_lugar_existe():
    for base, outro in list(magicos.REFLETIDO.items()) + \
            list(magicos.NO_LUGAR.items()):
        assert base in magicos.MAGICOS, base
        assert outro in magicos.MAGICOS, outro


# ═══ Aritmetica ════════════════════════════════════════════

def test_soma_e_subtracao():
    assert rodar(VETOR + '''
out spawn Vetor(1, 2) + spawn Vetor(3, 4)
out spawn Vetor(5, 5) - spawn Vetor(1, 2)
''') == "(4, 6)\n(4, 3)"


def test_refletido_quando_a_esquerda_nao_sabe():
    """'2 * vetor' — o inteiro nao sabe multiplicar por um vetor."""
    assert rodar(VETOR + 'out 3 * spawn Vetor(1, 2)') == "(3, 6)"


def test_unario():
    assert rodar(VETOR + 'out -(spawn Vetor(1, 2))') == "(-1, -2)"


def test_sem_o_magico_o_erro_e_de_tipo():
    fonte = '''
blueprint Vazio:
    action f():
        yield 1
out (spawn Vazio()) + 1
'''
    assert "unsupported" in erro_de(fonte) or "Type" in erro_de(fonte)


# ═══ Comparacao ════════════════════════════════════════════

def test_igualdade_e_ordem():
    assert rodar(VETOR + '''
out spawn Vetor(1, 2) is spawn Vetor(1, 2)
out spawn Vetor(1, 2) is spawn Vetor(9, 9)
out spawn Vetor(1, 1) smaller spawn Vetor(5, 5)
''') == "yes\nno\nyes"


def test_diferente_sai_de_igual_negado():
    """Declarar '__eq__' deveria bastar para '!=' funcionar."""
    assert rodar(VETOR + 'out spawn Vetor(1, 2) isnt spawn Vetor(3, 4)') == "yes"


def test_cmp_responde_os_seis():
    """Um objeto com ordem natural nao deveria escrever seis metodos."""
    assert rodar('''
blueprint Nota(valor):
    action __cmp__(o):
        yield self.valor - o.valor

a := spawn Nota(5)
b := spawn Nota(9)
out a smaller b, a bigger b, a is spawn Nota(5), a isnt b
''') == "yes no yes yes"


# ═══ Texto ═════════════════════════════════════════════════

def test_str_decide_o_que_out_imprime():
    assert rodar(VETOR + 'out spawn Vetor(7, 8)') == "(7, 8)"


def test_str_vale_na_interpolacao():
    assert rodar(VETOR + 'v := spawn Vetor(1, 2)\nout $"vetor {v}"') == "vetor (1, 2)"


def test_repr_serve_de_reserva():
    assert rodar('''
blueprint Coisa:
    action __repr__():
        yield "<a coisa>"
out spawn Coisa()
''') == "<a coisa>"


def test_tostring_antigo_continua_valendo():
    """Quem ja usava 'toString' nao pode descobrir que parou."""
    assert rodar('''
blueprint Antigo:
    action toString():
        yield "ainda funciona"
out spawn Antigo()
''') == "ainda funciona"


# ═══ Colecao ═══════════════════════════════════════════════

def test_len_getitem_e_contains():
    assert rodar('''
blueprint Caixa:
    action setup():
        self.itens := [10, 20, 30]
    action __len__():
        yield len(self.itens)
    action __getitem__(i):
        yield self.itens[i]
    action __contains__(x):
        yield x in self.itens

c := spawn Caixa()
out len(c), c[1], 20 in c, 99 in c
''') == "3 20 yes no"


def test_setitem_e_atribuicao_composta():
    assert rodar('''
blueprint Contagem:
    action setup():
        self.d := {}
    action __getitem__(k):
        yield self.d.get(k, 0)
    action __setitem__(k, v):
        self.d[k] := v

c := spawn Contagem()
c["a"] := 1
c["a"] += 5
c["novo"] += 2
out c["a"], c["novo"], c["nunca visto"]
''') == "6 2 0"


def test_iter_com_colecao():
    assert rodar('''
blueprint Tres:
    action __iter__():
        yield [1, 2, 3]

cycle x in spawn Tres():
    out x
''') == "1\n2\n3"


def test_iter_com_next_para_no_void():
    """O fim do percurso e 'void', e nao um erro: fluxo normal nao
    deveria custar uma excecao."""
    assert rodar('''
blueprint Contador:
    action setup():
        self.n := 0
    action __next__():
        given self.n bigger_eq 3:
            yield void
        self.n += 1
        yield self.n

cycle x in spawn Contador():
    out x
''') == "1\n2\n3"


def test_contains_sem_o_magico_percorre():
    """Quem declarou '__iter__' espera que 'in' funcione."""
    assert rodar('''
blueprint Tres:
    action __iter__():
        yield [1, 2, 3]
out 2 in spawn Tres(), 9 in spawn Tres()
''') == "yes no"


def test_percorrer_o_que_nao_sabe_explica():
    fonte = '''
blueprint Mudo:
    action f():
        yield 1
cycle x in spawn Mudo():
    out x
'''
    msg = erro_de(fonte)
    assert "__iter__" in msg or "cycled over" in msg


def test_next_infinito_para_e_explica():
    """Um '__next__' que nunca devolve void travaria em silencio."""
    fonte = '''
blueprint SemFim:
    action __next__():
        yield 1
cycle x in spawn SemFim():
    given x is 1:
        skip
'''
    with pytest.raises(DataForgeError) as exc:
        rodar(fonte)
    assert "void" in str(exc.value) or "never returned" in str(exc.value)


# ═══ Verdade ═══════════════════════════════════════════════

def test_bool_decide_o_given():
    assert rodar('''
blueprint Interruptor(ligado):
    action __bool__():
        yield self.ligado

given spawn Interruptor(yes):
    out "ligado"
given spawn Interruptor(no):
    out "nao devia"
otherwise:
    out "desligado"
''') == "ligado\ndesligado"


def test_sem_bool_o_tamanho_decide():
    """A regra do Python: sem '__bool__', tamanho zero e falso."""
    assert rodar('''
blueprint Saco:
    action setup(n):
        self.n := n
    action __len__():
        yield self.n

given spawn Saco(0):
    out "nao devia"
otherwise:
    out "vazio e falso"
given spawn Saco(3):
    out "cheio e verdadeiro"
''') == "vazio e falso\ncheio e verdadeiro"


def test_objeto_sem_nenhum_dos_dois_e_verdadeiro():
    assert rodar('''
blueprint Simples:
    action f():
        yield 1
given spawn Simples():
    out "existe, logo e verdadeiro"
''') == "existe, logo e verdadeiro"


def test_not_honra_bool():
    assert rodar('''
blueprint Falso:
    action __bool__():
        yield no
out not spawn Falso()
''') == "yes"


# ═══ Chamada ═══════════════════════════════════════════════

def test_call_faz_o_objeto_virar_acao():
    assert rodar('''
blueprint Acumulador:
    action setup():
        self.total := 0
    action __call__(x):
        self.total += x
        yield self.total

a := spawn Acumulador()
a(10)
a(5)
out a(1)
''') == "16"


def test_chamar_o_que_nao_tem_call_explica():
    """A dica precisa nomear o metodo que falta, nao so recusar."""
    with pytest.raises(DataForgeError) as exc:
        rodar('''
blueprint Mudo:
    action f():
        yield 1
m := spawn Mudo()
m()
''')
    assert "not callable" in str(exc.value)
    assert "__call__" in exc.value.dica


# ═══ Contexto ══════════════════════════════════════════════

def test_enter_e_exit():
    assert rodar('''
blueprint Recurso(nome):
    action __enter__():
        out "abre"
        yield self.nome
    action __exit__():
        out "fecha"

with spawn Recurso("x") as r:
    out r
''') == "abre\nx\nfecha"


def test_exit_roda_mesmo_com_erro():
    assert rodar('''
blueprint Recurso:
    action __enter__():
        yield 1
    action __exit__():
        out "fechou"

monitor:
    with spawn Recurso() as r:
        trigger "falhou"
handle e:
    out "capturado"
''') == "fechou\ncapturado"


# ═══ Slots ═════════════════════════════════════════════════

def test_slots_recusa_campo_nao_declarado():
    msg = erro_de('''
blueprint Ponto:
    slots ["x", "y"]
    action setup(x, y):
        self.x := x
        self.y := y

p := spawn Ponto(1, 2)
p.z := 3
''')
    assert "'z'" in msg


def test_slots_aceita_os_declarados():
    assert rodar('''
blueprint Ponto:
    slots ["x", "y"]
    action setup(x, y):
        self.x := x
        self.y := y
    action __str__():
        yield $"({self.x}, {self.y})"

p := spawn Ponto(1, 2)
p.x := 9
out p
''') == "(9, 2)"


def test_slots_sao_herdados_e_somados():
    assert rodar('''
blueprint Base:
    slots ["a"]
    action setup():
        self.a := 1

blueprint Filho extends Base:
    slots ["b"]
    action setup():
        self.a := 1
        self.b := 2

f := spawn Filho()
out f.a, f.b
''') == "1 2"


def test_slots_economizam_memoria_de_verdade():
    """Se nao economiza, o recurso e so uma restricao sem beneficio."""
    import tracemalloc

    def pico(fonte):
        tracemalloc.start()
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
        _, p = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return p

    sem = '''
blueprint P:
    action setup(x, y, z):
        self.x := x
        self.y := y
        self.z := z
xs := []
cycle i from 1 to 5000:
    xs.append(spawn P(i, i, i))
'''
    com = sem.replace("blueprint P:", 'blueprint P:\n    slots ["x", "y", "z"]\n')
    assert pico(com) < pico(sem) * 0.85, "os slots deviam economizar memoria"


def test_sem_slots_o_campo_livre_continua():
    assert rodar('''
blueprint Livre:
    action setup():
        self.qualquer := 1
l := spawn Livre()
l.outro := 2
out l.qualquer, l.outro
''') == "1 2"


# ═══ MRO ═══════════════════════════════════════════════════

def test_mro_do_diamante():
    assert rodar('''
blueprint A:
    action f():
        yield 1
blueprint B extends A:
    action f():
        yield 2
blueprint C extends A:
    action f():
        yield 3
blueprint D extends B, C:
    action g():
        yield 4
out linhagem(spawn D())
''') == "[D, B, C, A]"


def test_o_primeiro_pai_escrito_tem_prioridade():
    """A regra de toda linguagem com heranca multipla."""
    assert rodar('''
blueprint A:
    action quem():
        yield "A"
blueprint B extends A:
    action quem():
        yield "B"
blueprint C extends A:
    action quem():
        yield "C"
blueprint D extends B, C:
    action g():
        yield 1
out (spawn D()).quem()
''') == "B"


def test_o_que_so_o_segundo_pai_tem_e_alcancado():
    assert rodar('''
blueprint A:
    action f():
        yield 1
blueprint B extends A:
    action f():
        yield 2
blueprint C extends A:
    action so_meu():
        yield "de C"
blueprint D extends B, C:
    action g():
        yield 1
out (spawn D()).so_meu()
''') == "de C"


def test_heranca_simples_continua_igual():
    assert rodar('''
blueprint A:
    action f():
        yield "A"
blueprint B extends A:
    action g():
        yield "B"
blueprint C extends B:
    action h():
        yield "C"
out linhagem(spawn C())
out (spawn C()).f()
''') == "[C, B, A]\nA"


# ═══ Nao quebrou o que ja havia ════════════════════════════

def test_operator_continua_tendo_prioridade():
    """'operator +' e a forma nativa, e veio antes."""
    assert rodar('''
blueprint N(v):
    operator +(o):
        yield spawn N(self.v + o.v)
    action __add__(o):
        yield spawn N(999)
    action __str__():
        yield str(self.v)
out spawn N(1) + spawn N(2)
''') == "3"


def test_magicos_nao_atrapalham_numeros_e_textos():
    assert rodar('out 2 + 3, "a" + "b", [1] + [2], len("abc")') == "5 ab [1, 2] 3"
