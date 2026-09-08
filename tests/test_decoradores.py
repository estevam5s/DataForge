"""
Testes dos decoradores.

Um decorador tem duas funções: **embrulhar** (trocar o comportamento) e
**anotar** (deixar um metadado que outra parte lê). A segunda é a que
torna possível escrever, na própria linguagem, o tipo de framework que
o NestJS escreve em TypeScript — e é a que faltava.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import DataForgeError                      # noqa: E402
from dataforge.interpreter import Interpreter                    # noqa: E402
from dataforge.lexer import tokenize                             # noqa: E402
from dataforge.parser import parse                               # noqa: E402


def run(fonte):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(fonte)))
    return buffer.getvalue().strip()


ENVOLVE = '''
action logar(f):
    action envolvida(x):
        out "→", x
        yield f(x)
    yield envolvida
'''

ANOTA = '''
action Rota(caminho):
    action aplicar(alvo):
        yield void
    yield aplicar
'''


# ── Sintaxe ──────────────────────────────────────────────────

def test_arroba_sozinho_sem_a_palavra_mark():
    """'@Nome' é a forma normal; 'mark' era uma muleta do parser."""
    assert run(ENVOLVE + '''
@logar
action dobrar(n):
    yield n * 2

out dobrar(21)''') == "→ 21\n42"


def test_mark_arroba_continua_funcionando():
    """Código escrito antes não pode quebrar."""
    assert run(ENVOLVE + '''
mark @logar
action dobrar(n):
    yield n * 2

out dobrar(21)''') == "→ 21\n42"


def test_pilha_de_decoradores_aplica_de_baixo_para_cima():
    assert run('''
action A(f):
    action envolvida(x):
        out "A"
        yield f(x)
    yield envolvida

action B(f):
    action envolvida(x):
        out "B"
        yield f(x)
    yield envolvida

@A
@B
action f(x):
    yield x

out f(1)''') == "A\nB\n1"


def test_decorador_com_argumentos_e_uma_fabrica():
    assert run('''
action repetir(vezes):
    action aplicar(f):
        action envolvida(x):
            cycle i from 1 to vezes:
                f(x)
            yield vezes
        yield envolvida
    yield aplicar

@repetir(3)
action falar(t):
    out t

out falar("oi")''') == "oi\noi\noi\n3"


def test_decorador_aceita_argumento_nomeado():
    from dataforge import ast_nodes as ast
    no = parse(tokenize('@Rota("/x", metodo: "GET")\naction f():\n    yield 1')).body[0]
    deco = no.decorators[0]
    assert len(deco.args) == 1
    assert set(deco.kwargs) == {"metodo"}


def test_decorador_com_nome_pontuado():
    no = parse(tokenize('@Http.Get("/x")\naction f():\n    yield 1')).body[0]
    assert no.decorators[0].name == "Http.Get"


def test_decorador_sobre_coisa_indecoravel_explica():
    from dataforge.errors import ParseError
    with pytest.raises(ParseError, match="não pode decorar"):
        parse(tokenize('@algo\nx := 1'))


def test_decorador_inexistente_diz_o_que_fazer():
    with pytest.raises(DataForgeError, match="não existe"):
        run('@NaoExiste\naction f():\n    yield 1\n\nf()')


# ── Onde vale ────────────────────────────────────────────────

def test_decora_blueprint():
    assert run(ANOTA + '''
adopt Arcane.Meta as Meta

@Rota("/usuarios")
blueprint C:
    action f():
        yield 1

out Meta.arg(C, "Rota", 0)''') == "/usuarios"


def test_decora_record():
    assert run(ANOTA + '''
adopt Arcane.Meta as Meta

@Rota("/pontos")
record P:
    x: Integer

out Meta.tem(P, "Rota"), P(5).x''') == "yes 5"


def test_decora_metodo_dentro_de_blueprint():
    """É onde o decorador mais serve: rotas ao lado dos métodos."""
    assert run(ANOTA + '''
adopt Arcane.Meta as Meta

blueprint C:
    @Rota("/listar")
    action listar():
        yield 1

    @Rota("/criar")
    action criar():
        yield 2

achados := Meta.metodos_com(C, "Rota")
out len(achados)''') == "2"


def test_o_alvo_continua_funcionando_depois_de_anotado():
    """Um decorador que só anota devolve void — e isso não pode apagar
    a ação que ele decorou."""
    assert run(ANOTA + '''
@Rota("/x")
action dobrar(n):
    yield n * 2

out dobrar(21)''') == "42"


# ── Metadados ────────────────────────────────────────────────

def test_le_os_nomes_dos_decoradores():
    assert run(ANOTA + '''
adopt Arcane.Meta as Meta

action Injetavel(alvo):
    yield void

@Injetavel
@Rota("/x")
action f():
    yield 1

out Meta.nomes(f)''') == "[Injetavel, Rota]"


def test_le_argumento_posicional_e_nomeado():
    assert run('''
adopt Arcane.Meta as Meta

action Rota(caminho, metodo):
    action aplicar(alvo):
        yield void
    yield aplicar

@Rota("/itens", metodo: "POST")
action criar():
    yield 1

out Meta.arg(criar, "Rota", 0), Meta.opcao(criar, "Rota", "metodo")''') \
        == "/itens POST"


def test_metadado_ausente_devolve_o_padrao():
    assert run('''
adopt Arcane.Meta as Meta

action f():
    yield 1

out Meta.arg(f, "NaoTem", 0, "padrao"), Meta.tem(f, "NaoTem")''') \
        == "padrao no"


def test_metadado_sobrevive_ao_embrulho():
    """'@Injetavel @Rota(...)' — o embrulho herda a anotação de baixo."""
    assert run(ENVOLVE + ANOTA + '''
adopt Arcane.Meta as Meta

@logar
@Rota("/x")
action f(n):
    yield n

out Meta.tem(f, "Rota")''') == "yes"


def test_filtrar_acha_o_que_foi_anotado():
    """É como um contêiner de injeção descobre o que registrar."""
    assert run('''
adopt Arcane.Meta as Meta

action Injetavel(alvo):
    yield void

@Injetavel
blueprint A:
    action f():
        yield 1

blueprint B:
    action f():
        yield 2

achados := Meta.filtrar([A, B], "Injetavel")
out len(achados)''') == "1"


def test_marcar_anota_sem_a_sintaxe():
    assert run('''
adopt Arcane.Meta as Meta

action f():
    yield 1

Meta.marcar(f, "Cache", 60)
out Meta.arg(f, "Cache", 0)''') == "60"


def test_descrever_mostra_a_forma_do_alvo():
    saida = run('''
adopt Arcane.Meta as Meta

action Entidade(tabela):
    action aplicar(alvo):
        yield void
    yield aplicar

@Entidade("usuarios")
blueprint Usuario:
    nome: String := ""

    action ola():
        yield 1

d := Meta.descrever(Usuario)
out d["nome"], d["decoradores"], d["metodos"], d["campos"]''')
    assert "Usuario" in saida
    assert "Entidade" in saida
    assert "ola" in saida
    assert "nome" in saida


# ── O caso completo ──────────────────────────────────────────

def test_um_roteador_descobre_as_rotas_pelos_decoradores():
    """O teste que justifica tudo: um framework escrito na linguagem."""
    saida = run('''
adopt Arcane.Meta as Meta

action Controlador(prefixo):
    action aplicar(alvo):
        yield void
    yield aplicar

action Rota(metodo, caminho):
    action aplicar(alvo):
        yield void
    yield aplicar

@Controlador("/usuarios")
blueprint UsuariosController:
    @Rota("GET", "/")
    action listar():
        yield "todos"

    @Rota("POST", "/")
    action criar():
        yield "criado"

prefixo := Meta.arg(UsuariosController, "Controlador", 0)
cycle r in Meta.metodos_com(UsuariosController, "Rota"):
    verbo := r["meta"]["args"][0]
    caminho := r["meta"]["args"][1]
    out verbo, prefixo + caminho''')
    assert "GET /usuarios/" in saida
    assert "POST /usuarios/" in saida
