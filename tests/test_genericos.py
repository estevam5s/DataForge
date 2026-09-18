"""Generics de verdade: record, enum e trait genéricos, limites e índices.

`action f<T>(…)` e `blueprint Caixa<T>` já existiam. O resto do sistema
de tipos não: `record Par<T>` era erro de sintaxe, um `trait` não podia
receber parâmetro, um trait não herdava de outro, e não havia como
escrever "um vetor de três posições" — o tamanho é um VALOR, e valor não
entrava em anotação nenhuma.

O que os testes cobram:

1. `<T>` vale nas quatro declarações (ação, blueprint, record, enum) e no
   trait, e `<T extends X>` é cobrado nas duas metades — `check` e
   execução;
2. o argumento chega ao CONTEÚDO: `Caixa<Integer>` recusa um texto no
   campo, e o erro nomeia o campo;
3. um parâmetro pode ser um NÚMERO (`Vetor<3>`), e a regra do tipo o
   enxerga — é o tipo indexado, e é o que dá "cluster de três";
4. `trait B extends A` herda exigências e implementações padrão;
5. um trait declara tipo associado (`type Item`) e constante associada
   (`steady MAXIMO := 10`), e quem implementa os recebe.
"""

import io
import os
import subprocess
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import DataForgeError, ParseError      # noqa: E402
from dataforge.formatter import format_source                # noqa: E402
from dataforge.interpreter import Interpreter                # noqa: E402
from dataforge.lexer import tokenize                         # noqa: E402
from dataforge.parser import parse                           # noqa: E402
from dataforge.typechecker import check_program              # noqa: E402


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
    return saida.getvalue().strip()


def erro_de(fonte):
    try:
        rodar(fonte)
    except DataForgeError as erro:
        return erro
    raise AssertionError("era para dar erro, e rodou")


def diagnosticos(fonte, codigo=None):
    todos = check_program(parse(tokenize(fonte, "t.df"), "t.df"), "t.df")
    return [d for d in todos if codigo is None or d.code == codigo]


def erros(fonte):
    return [d for d in diagnosticos(fonte) if d.severity == "error"]


# ── record genérico ──────────────────────────────────────────

def test_record_generico_guarda_e_devolve():
    assert rodar('''
record Caixa<T>:
    valor: T

c := Caixa(7)
t := Caixa("oi")
out c.valor, t.valor, typeof(c)
''') == "7 oi Caixa"


def test_record_generico_confere_o_conteudo_na_anotacao():
    erro = erro_de('''
record Caixa<T>:
    valor: T
c: Caixa<Integer> := Caixa("nao e numero")
''')
    assert "Caixa<Integer>" in erro.message
    assert "valor" in erro.message and "String" in erro.message


def test_record_generico_com_limite_cobra_o_argumento():
    fonte = '''
record Medida<T extends Number>:
    quanto: T
    action dobro():
        yield self.quanto * 2
out Medida(2.5).dobro()
'''
    assert rodar(fonte) == "5.0"
    erro = erro_de(fonte.replace("out Medida(2.5).dobro()", 'Medida("dois")'))
    assert "Number" in erro.message


def test_record_generico_em_parametro_e_retorno():
    assert rodar('''
record Par<A, B>:
    esquerda: A
    direita: B

action girar(p: Par<Integer, String>) -> Par<String, Integer>:
    yield Par(p.direita, p.esquerda)

g := girar(Par(1, "um"))
out g.esquerda, g.direita
''') == "um 1"
    assert "Par<Integer, String>" in erro_de('''
record Par<A, B>:
    esquerda: A
    direita: B
action girar(p: Par<Integer, String>):
    yield p
girar(Par("um", 1))
''').message


# ── enum genérico ────────────────────────────────────────────

def test_enum_generico_e_o_resultado_que_ele_modela():
    assert rodar('''
enum Talvez<T>:
    Nada
    Algo

action achar<T>(xs: Cluster<T>, alvo: T) -> Talvez<T>:
    cycle x in xs:
        given x is alvo:
            yield Talvez.Algo
    yield Talvez.Nada

out achar([1, 2, 3], 2).name, achar([1], 9).name
''') == "Algo Nada"


# ── trait genérico, herança e membros associados ─────────────

def test_trait_generico_declara_a_relacao():
    assert rodar('''
trait Comparavel<T>:
    action comparar(outro: T) -> Integer

blueprint Dinheiro extends Comparavel:
    valor := 0
    action comparar(outro: Dinheiro) -> Integer:
        yield self.valor - outro.valor

a := spawn Dinheiro()
b := spawn Dinheiro()
b.valor := 5
out a.comparar(b)
''') == "-5"


def test_trait_herda_de_trait():
    assert rodar('''
trait Legivel:
    action ler()
    action descrever():
        yield $"leio: {self.ler()}"

trait Editavel extends Legivel:
    action escrever(x)

blueprint Documento extends Editavel:
    conteudo := "vazio"
    action ler():
        yield self.conteudo
    action escrever(x):
        self.conteudo := x

d := spawn Documento()
d.escrever("oi")
out d.ler(), d.descrever()
''') == "oi leio: oi"


def test_trait_herdado_cobra_o_que_falta():
    erro = erro_de('''
trait Legivel:
    action ler()
trait Editavel extends Legivel:
    action escrever(x)
blueprint Meio extends Editavel:
    action escrever(x):
        yield x
''')
    assert "ler" in erro.message and "Legivel" in erro.message


def test_trait_declara_tipo_e_constante_associados():
    assert rodar('''
trait Coletor:
    type Item := Any
    steady LIMITE := 3
    action pegar() -> Item

blueprint Fila extends Coletor:
    type Item := Integer
    itens := [1, 2]
    action pegar() -> Item:
        yield self.itens[0]

f := spawn Fila()
out f.pegar(), Fila.LIMITE, Fila.Item
''') == "1 3 Integer"


def test_o_tipo_associado_confere_o_retorno():
    erro = erro_de('''
trait Coletor:
    type Item := Any
    action pegar() -> Item

blueprint Fila extends Coletor:
    type Item := Integer
    action pegar() -> Item:
        yield "nao e numero"

(spawn Fila()).pegar()
''')
    assert "Integer" in erro.message and "String" in erro.message


# ── tipos indexados: o parâmetro que é um número ─────────────

def test_parametro_que_e_numero_chega_na_regra():
    assert rodar('''
type Vetor<N> := Cluster<Float> where len(valor) is N

v: Vetor<3> := [1.0, 2.0, 3.0]
out len(v)
''') == "3"
    erro = erro_de('''
type Vetor<N> := Cluster<Float> where len(valor) is N
v: Vetor<3> := [1.0, 2.0]
''')
    assert "Vetor<3>" in erro.message or "Vetor" in erro.message
    assert "len(valor) is N" in erro.message


def test_o_tipo_indexado_vale_em_acao_e_o_tamanho_faz_parte_do_tipo():
    assert rodar('''
type Vetor<N> := Cluster<Float> where len(valor) is N

action somar(a: Vetor<2>, b: Vetor<2>) -> Vetor<2>:
    yield [a[0] + b[0], a[1] + b[1]]

out somar([1.0, 2.0], [3.0, 4.0])
''') == "[4.0, 6.0]"
    erro = erro_de('''
type Vetor<N> := Cluster<Float> where len(valor) is N
action somar(a: Vetor<2>, b: Vetor<2>) -> Vetor<2>:
    yield [a[0] + b[0]]
somar([1.0, 2.0], [3.0, 4.0])
''')
    assert "return value" in erro.message


def test_check_prova_o_tamanho_de_um_literal():
    assert diagnosticos('type Vetor<N> := Cluster<Float> where len(valor) is N\n'
                        'v: Vetor<3> := [1.0, 2.0]\n', "tipo-refinado")
    assert not erros('type Vetor<N> := Cluster<Float> where len(valor) is N\n'
                     'v: Vetor<2> := [1.0, 2.0]\nout len(v)\n')


# ── o analisador ─────────────────────────────────────────────

def test_check_conhece_os_genericos_de_toda_declaracao():
    assert not erros('''
record Caixa<T>:
    valor: T
enum Talvez<T>:
    Nada
trait Comparavel<T>:
    action comparar(outro: T) -> Integer
blueprint Pilha<T>:
    itens: Cluster<T> := []
action primeiro<T>(xs: Cluster<T>) -> T:
    yield xs[0]
out primeiro([1]), Caixa(1).valor, Talvez.Nada.name
''')


def test_check_acusa_argumento_a_mais_ou_a_menos():
    with pytest.raises(ParseError) as erro:
        parse(tokenize('record Par<A, B>:\n    a: A\n    b: B\n'
                       'x: Par<Integer> := Par(1, 2)\n', "t"), "t")
    assert "Par" in erro.value.message and "2" in erro.value.message


def test_check_acusa_o_limite_na_chamada():
    assert diagnosticos('''
record Medida<T extends Number>:
    quanto: T
m := Medida("texto")
''', "generic-bound")


# ── ferramentas ──────────────────────────────────────────────

def test_o_formatador_mantem_os_genericos():
    fonte = ('record Par<A, B>:\n    esquerda: A\n    direita: B\n\n'
             'enum Talvez<T>:\n    Nada\n\n'
             'trait Comparavel<T>:\n    action comparar(outro: T) -> Integer\n')
    formatado = format_source(fonte)
    assert "record Par<A, B>:" in formatado
    assert "enum Talvez<T>:" in formatado
    assert "trait Comparavel<T>:" in formatado
    assert format_source(formatado) == formatado


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import tipos_genericos
    for pagina in tipos_genericos.PAGINAS:
        for i, bloco in enumerate(pagina["blocos"]):
            if "code" in bloco and bloco.get("lang") == "df" \
                    and not bloco.get("title"):
                yield f"{pagina['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_da_doc()))
def test_todo_exemplo_da_doc_roda_e_passa_no_check(onde, codigo):
    rodar(codigo)
    ruins = [d for d in diagnosticos(codigo) if d.severity == "error"]
    assert not ruins, f"{onde}: {[d.message for d in ruins]}"


def test_o_repositorio_continua_limpo():
    for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"):
        r = subprocess.run([sys.executable, "-m", "dataforge", "check", pasta],
                           cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env={**os.environ, "NO_COLOR": "1"})
        assert r.returncode == 0, f"{pasta}: {r.stdout[-600:]}"
