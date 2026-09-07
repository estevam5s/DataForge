"""OOP do DataForge 4.1: campos, propriedades, operadores, visibilidade,
metodos estaticos, abstratos e contrato de trait."""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import DataForgeError            # noqa: E402
from dataforge.interpreter import Interpreter          # noqa: E402
from dataforge.lexer import tokenize                   # noqa: E402
from dataforge.parser import parse                     # noqa: E402


def rodar(fonte):
    """Executa e devolve a saida."""
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<teste>"), "<teste>"), "<teste>")
    return saida.getvalue().strip()


def erro_de(fonte):
    """Executa esperando falha; devolve a mensagem."""
    with pytest.raises(DataForgeError) as exc:
        rodar(fonte)
    return str(exc.value)


# ─── Campos declarados ─────────────────────────────────────

def test_campo_declarado_com_padrao():
    assert rodar('''
blueprint Contador:
    valor: Integer := 0
    action somar():
        self.valor += 1
        yield self.valor

c := spawn Contador()
out c.valor
out c.somar()
''') == "0\n1"


def test_campo_sem_padrao_comeca_void():
    assert rodar('''
blueprint P:
    nome: String
p := spawn P()
out p.nome is void
''') == "yes"


def test_campo_e_herdado():
    assert rodar('''
blueprint Base:
    id: Integer := 7
blueprint Filho extends Base:
    action ler():
        yield self.id
out (spawn Filho()).ler()
''') == "7"


# ─── Propriedades ──────────────────────────────────────────

def test_getter_roda_codigo():
    assert rodar('''
blueprint Circulo:
    action setup(r):
        self.r := r
    get area():
        yield 3 * self.r * self.r
out (spawn Circulo(2)).area
''') == "12"


def test_setter_valida():
    fonte = '''
blueprint Conta:
    action setup():
        self._saldo := 0
    get saldo():
        yield self._saldo
    set saldo(v):
        given v smaller 0:
            trigger "saldo nao pode ser negativo"
        self._saldo := v

c := spawn Conta()
c.saldo := 50
out c.saldo
'''
    assert rodar(fonte) == "50"
    assert "negativo" in erro_de(fonte.replace("c.saldo := 50", "c.saldo := -1"))


def test_propriedade_so_leitura_recusa_escrita():
    msg = erro_de('''
blueprint P:
    get x():
        yield 1
p := spawn P()
p.x := 5
''')
    assert "read-only" in msg
    assert "set x(" in msg          # diz como resolver


def test_propriedade_so_escrita_recusa_leitura():
    msg = erro_de('''
blueprint P:
    action setup():
        self._v := 0
    set x(v):
        self._v := v
p := spawn P()
out p.x
''')
    assert "write-only" in msg


def test_propriedade_herdada():
    assert rodar('''
blueprint Base:
    action setup():
        self.n := 3
    get dobro():
        yield self.n * 2
blueprint Filho extends Base:
    action setup():
        self.n := 5
out (spawn Filho()).dobro
''') == "10"


# ─── Operadores ────────────────────────────────────────────

def test_operadores_aritmeticos():
    assert rodar('''
blueprint V:
    action setup(x):
        self.x := x
    operator + (o):
        yield spawn V(self.x + o.x)
    operator * (k):
        yield spawn V(self.x * k)
    action toString():
        yield str(self.x)

out str(spawn V(2) + spawn V(3))
out str(spawn V(4) * 5)
''') == "5\n20"


def test_operador_de_igualdade_e_negacao_derivada():
    assert rodar('''
blueprint Ponto:
    action setup(x, y):
        self.x := x
        self.y := y
    operator == (o):
        yield self.x is o.x and self.y is o.y

a := spawn Ponto(1, 2)
out a == spawn Ponto(1, 2)
out a == spawn Ponto(9, 9)
out a isnt spawn Ponto(9, 9)
''') == "yes\nno\nyes"


def test_operador_de_ordem():
    assert rodar('''
blueprint Peso:
    action setup(kg):
        self.kg := kg
    operator < (o):
        yield self.kg smaller o.kg

out (spawn Peso(1)) smaller (spawn Peso(2))
out (spawn Peso(5)) smaller (spawn Peso(2))
''') == "yes\nno"


def test_operador_herdado():
    assert rodar('''
blueprint Base:
    action setup(v):
        self.v := v
    operator + (o):
        yield self.v + o.v
blueprint Filho extends Base:
    action setup(v):
        self.v := v
out (spawn Filho(2)) + (spawn Filho(3))
''') == "5"


def test_operador_nao_sobrecarregavel_e_recusado():
    """'operator' seguido de algo que nao e operador da erro claro."""
    msg = erro_de('''
blueprint P:
    operator @ (o):
        yield 1
''')
    assert "overload" in msg.lower()
    # a mensagem lista o que pode ser sobrecarregado
    assert "+" in msg


# ─── Visibilidade ──────────────────────────────────────────

def test_private_bloqueia_de_fora():
    msg = erro_de('''
blueprint Conta:
    private saldo: Float := 0.0
    action depositar(v):
        self.saldo += v
        yield self.saldo

c := spawn Conta()
out c.depositar(10)
out c.saldo
''')
    assert "private" in msg
    assert "Conta.saldo" in msg


def test_private_funciona_de_dentro():
    assert rodar('''
blueprint Conta:
    private saldo: Float := 0.0
    action depositar(v):
        self.saldo += v
        yield self.saldo
out (spawn Conta()).depositar(10)
''') == "10.0"


def test_protected_alcanca_o_herdeiro():
    assert rodar('''
blueprint Base:
    protected segredo: Integer := 42
    action nada():
        yield 0
blueprint Filho extends Base:
    action revelar():
        yield self.segredo
out (spawn Filho()).revelar()
''') == "42"


# ─── Estaticos ─────────────────────────────────────────────

def test_metodo_estatico():
    assert rodar('''
blueprint Mat:
    static action dobro(x):
        yield x * 2
out Mat.dobro(21)
''') == "42"


def test_metodo_de_instancia_pelo_blueprint_da_erro_util():
    msg = erro_de('''
blueprint P:
    action f():
        yield 1
out P.f()
''')
    assert "instance method" in msg
    assert "spawn P" in msg          # diz o que fazer


# ─── Abstratos e contratos ─────────────────────────────────

def test_blueprint_abstrato_nao_pode_ser_spawnado():
    msg = erro_de('''
abstract blueprint Forma:
    abstract action area()
f := spawn Forma()
''')
    assert "abstract" in msg
    assert "extends" in msg


def test_herdeiro_concreto_precisa_implementar():
    msg = erro_de('''
abstract blueprint Forma:
    abstract action area()
blueprint Quadrado extends Forma:
    action setup(l):
        self.l := l
''')
    assert "area()" in msg
    assert "Forma" in msg


def test_herdeiro_que_implementa_funciona():
    assert rodar('''
abstract blueprint Forma:
    abstract action area()
    action descrever():
        yield $"area = {self.area()}"

blueprint Quadrado extends Forma:
    action setup(l):
        self.l := l
    action area():
        yield self.l * self.l

out (spawn Quadrado(4)).descrever()
''') == "area = 16"


def test_contrato_de_trait_falha_na_declaracao():
    """O erro tem de aparecer ao declarar, nao ao chamar."""
    msg = erro_de('''
trait Serializavel:
    action serializar()

blueprint Dado with Serializavel:
    action outra():
        yield 1
''')
    assert "serializar()" in msg
    assert "Serializavel" in msg


def test_trait_com_implementacao_padrao():
    assert rodar('''
trait Saudavel:
    action ola():
        yield "ola"
blueprint P with Saudavel:
    action setup():
        self.x := 1
out (spawn P()).ola()
''') == "ola"


def test_final_impede_sobrescrita():
    msg = erro_de('''
blueprint Base:
    final action id():
        yield 1
blueprint Filho extends Base:
    action id():
        yield 2
''')
    assert "final" in msg


# ─── Palavras contextuais ──────────────────────────────────

@pytest.mark.parametrize("palavra", ["get", "set", "final", "private",
                                     "protected", "operator", "abstract"])
def test_contextual_continua_valendo_como_identificador(palavra):
    """Nenhuma das palavras novas pode roubar um nome de quem escreve."""
    assert rodar(f'''
{palavra} := 10
out {palavra}
''') == "10"


@pytest.mark.parametrize("palavra", ["get", "set", "final"])
def test_contextual_serve_de_nome_de_acao(palavra):
    assert rodar(f'''
action {palavra}(x):
    yield x * 2
out {palavra}(21)
''') == "42"


# ─── Qualidade das mensagens de erro ───────────────────────

def render_de(fonte, arquivo="/tmp/df_erro_teste.df"):
    """Roda esperando erro; devolve o relatorio renderizado, sem cor."""
    import pathlib
    pathlib.Path(arquivo).write_text(fonte, encoding="utf-8")
    with pytest.raises(DataForgeError) as exc:
        Interpreter().run(parse(tokenize(fonte, arquivo), arquivo), arquivo)
    erro = exc.value
    erro.filename = arquivo
    return erro.render(color=False, source_lines=fonte.split("\n"))


def test_erro_tem_codigo_local_e_trecho():
    r = render_de('nums := [1, 2, 3]\nout nums[10]\n')
    assert "erro[DF0601]" in r          # codigo estavel
    assert ":2:" in r                    # linha e coluna
    assert "out nums[10]" in r           # a linha que falhou
    assert "^" in r                      # o marcador
    assert "nums := [1, 2, 3]" in r      # contexto acima


def test_erro_de_indice_diz_o_tamanho_e_a_faixa():
    r = render_de('out [10, 20, 30][7]\n')
    assert "3 items" in r
    assert "0 to 2" in r


def test_erro_de_chave_lista_o_que_existe():
    r = render_de('v := {"nome": "ana", "idade": 30}\nout v["nomes"]\n')
    assert "nomes" in r
    assert '"nome"' in r                 # sugere a chave parecida
    assert "did you mean" in r


def test_erro_de_nome_sugere_o_parecido():
    r = render_de('contador := 1\nout contadr\n')
    assert "'contadr' is not defined" in r
    assert "contador" in r


def test_divisao_por_zero_ensina_a_guardar():
    r = render_de('a := 10\nb := 0\nout a / b\n')
    assert "Division by zero" in r
    assert "given" in r                  # mostra a guarda


def test_erro_aponta_para_a_documentacao():
    r = render_de('out [1][9]\n')
    assert "dataforge-lang.vercel.app/docs" in r


def test_steady_reatribuida_explica():
    r = render_de('steady PI := 3.14\nPI := 3\n')
    assert "steady" in r
    assert "PI" in r
