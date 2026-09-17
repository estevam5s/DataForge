"""OOP 1.2: contratos, modificadores, sobrecarga, metaclasses, reflexao,
injecao, padroes, memoria e metricas.

Organizado pela lista de testes obrigatorios do documento de OOP: classes,
objetos, construtores, destrutores, encapsulamento, heranca, polimorfismo,
interfaces, abstratos, traits, generics, overloads, overrides, operadores,
reflexao, metaclasses, decoradores, anotacoes, injecao, eventos,
serializacao, concorrencia, imutabilidade, coleta, erros de tipo, de
acesso, de heranca, de metaprogramacao, e SOLID.

Cada recurso tem os dois lados: o que funciona, e o que e recusado — com o
TIPO do erro, porque e ele que um 'handle' pega.
"""

import io
import os
import re
import subprocess
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.interpreter import Interpreter           # noqa: E402
from dataforge.lexer import tokenize                     # noqa: E402
from dataforge.parser import parse                       # noqa: E402
from dataforge.typechecker import check_program          # noqa: E402
from dataforge.errors import DataForgeError, ParseError  # noqa: E402


def rodar(fonte, arquivo="<oop>"):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, arquivo), arquivo), arquivo)
    return saida.getvalue().strip()


def erro_de(fonte):
    try:
        rodar(fonte)
    except DataForgeError as erro:
        return erro
    raise AssertionError("era para dar erro, e rodou")


def diagnosticos(fonte, codigo=None):
    arvore = parse(tokenize(fonte, "t.df"), "t.df")
    todos = check_program(arvore, "t.df")
    if codigo is None:
        return todos
    return [d for d in todos if d.code == codigo]


# ═════════════════════════════════════════════════════════════
#  Classes, objetos, construtores
# ═════════════════════════════════════════════════════════════

def test_cabecalho_aceita_tipo_e_padrao():
    assert rodar('''
blueprint Caixa<T>(valor: T, rotulo := "caixa"):
    action obter() -> T:
        yield self.valor
c := spawn Caixa(5)
out c.obter(), c.rotulo
''') == "5 caixa"


def test_tipo_do_cabecalho_e_conferido():
    erro = erro_de('''
blueprint Idade(anos: Integer):
    x := 0
spawn Idade("dez")
''')
    assert "anos" in erro.message


def test_argumento_nomeado_no_cabecalho():
    assert rodar('''
blueprint P(x, y := 0):
    z := 1
out (spawn P(y := 2, x := 1)).y
''') == "2"


def test_chamar_blueprint_copia_os_padroes_como_spawn():
    """Eram dois caminhos, e 'Nome()' nascia sem os padroes dos campos."""
    assert rodar('''
blueprint C:
    itens: Cluster := []
    n := 3
a := C()
out len(a.itens), a.n
''') == "0 3"


def test_init_e_sinonimo_de_setup():
    assert rodar('''
blueprint U:
    action __init__(nome):
        self.nome := nome
out (spawn U("ana")).nome
''') == "ana"


def test_blueprint_aninhado_vira_estatico():
    assert rodar('''
blueprint Loja:
    blueprint Item(nome):
        action rotulo():
            yield "item " + self.nome
    enum Tipo:
        Fisico
out (spawn Loja.Item("x")).rotulo(), Loja.Tipo.Fisico.name
''') == "item x Fisico"


def test_novo_pode_entregar_objeto_pronto():
    assert rodar('''
blueprint Unico:
    static instancia := void
    static action __new__():
        given Unico.instancia isnt void:
            yield Unico.instancia
    action setup():
        Unico.instancia := self
a := spawn Unico()
b := spawn Unico()
out a is b
''') == "yes"


def test_campo_de_instancia_lido_no_blueprint_diz_o_que_fazer():
    erro = erro_de('''
blueprint R:
    lista := []
out R.lista
''')
    assert "field of each" in erro.message


# ═════════════════════════════════════════════════════════════
#  Destrutores e memoria
# ═════════════════════════════════════════════════════════════

def test_teardown_roda_quando_o_objeto_e_solto():
    assert rodar('''
log := []
blueprint Arquivo(nome):
    action teardown():
        log.append(self.nome)
a := spawn Arquivo("x.csv")
a := void
out log
''') == '[x.csv]'


def test_del_tambem_e_finalizador():
    assert "morreu" in rodar('''
blueprint A:
    action __del__():
        out "morreu"
a := spawn A()
a := void
''')


def test_blueprint_sem_finalizador_nao_paga_por_ele():
    from dataforge.interpreter import DFInstance
    interp = Interpreter()
    interp.run(parse(tokenize("blueprint S:\n    x := 1\ns := spawn S()", "<t>"), "<t>"), "<t>")
    assert type(interp.global_env.get("s")) is DFInstance


def test_erro_no_finalizador_nao_propaga(capsys):
    rodar('''
blueprint Ruim:
    action teardown():
        trigger "falhei"
r := spawn Ruim()
r := void
out "seguiu"
''')


def test_referencia_fraca_e_mapa_fraco():
    assert rodar('''
adopt Arcane.Memoria as Mem
blueprint S:
    x := 1
s := spawn S()
ref := Mem.fraca(s)
m := Mem.mapa_fraco()
m.definir(s, 1)
antes := ref.viva() and m.tamanho is 1
s := void
out antes, ref.viva(), m.tamanho
''') == "yes no 0"


def test_memoria_conta_instancias_vivas():
    assert rodar('''
adopt Arcane.Memoria as Mem
blueprint Q:
    x := 1
xs := [spawn Q(), spawn Q(), spawn Q()]
out Mem.vivos(Q)
''') == "3"


# ═════════════════════════════════════════════════════════════
#  Encapsulamento e erros de acesso
# ═════════════════════════════════════════════════════════════

def test_private_sem_tipo_e_campo():
    assert rodar('''
blueprint Conta:
    private saldo := 10
    action ver():
        yield self.saldo
out (spawn Conta()).ver()
''') == "10"


def test_metodo_private_nao_e_chamavel_de_fora():
    erro = erro_de('''
blueprint A:
    private action segredo():
        yield 1
(spawn A()).segredo()
''')
    assert "private" in erro.message


def test_protected_de_fora_e_recusado():
    erro = erro_de('''
blueprint A:
    protected x := 1
blueprint B extends A:
    action ler():
        yield self.x
b := spawn B()
b.ler()
out b.x
''')
    assert "protected" in erro.message


def test_internal_vale_no_arquivo_e_nao_fora(tmp_path):
    (tmp_path / "banco.df").write_text(
        'blueprint Conexao:\n    internal action bruta():\n        yield "sql"\n'
        'action usar():\n    yield (spawn Conexao()).bruta()\n'
        'relay Conexao, usar\n', encoding="utf-8")
    (tmp_path / "app.df").write_text(
        'adopt ./banco as B\nout B.usar()\n'
        'monitor:\n    (spawn B.Conexao()).bruta()\n'
        'handle InternalAccessError:\n    out "recusado"\n', encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "run", "app.df"],
                       cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "PYTHONPATH": RAIZ, "NO_COLOR": "1"})
    assert r.stdout.split() == ["sql", "recusado"], r.stderr


def test_readonly_so_na_construcao():
    assert rodar('''
blueprint P:
    readonly id := 0
    action setup(id):
        self.id := id
p := spawn P(7)
monitor:
    p.id := 8
handle ReadOnlyFieldError:
    out "recusado"
out p.id
''') == "recusado\n7"


def test_readonly_escrito_num_metodo_e_erro_do_check():
    assert diagnosticos('''
blueprint P:
    readonly id := 0
    action mudar():
        self.id := 1
''', "readonly-fora-da-construcao")


def test_constante_de_classe():
    erro = erro_de('''
blueprint H:
    static steady PORTA := 80
H.PORTA := 81
''')
    assert type(erro).__name__ == "ConstantReassignmentError"


def test_congelar_recusa_escrita():
    erro = erro_de('''
adopt Arcane.Objetos as O
blueprint C:
    x := 1
c := O.congelar(spawn C())
c.x := 2
''')
    assert type(erro).__name__ == "FrozenObjectError"


def test_reflexao_respeita_a_visibilidade():
    erro = erro_de('''
adopt Arcane.Reflexo as R
blueprint A:
    private segredo := 1
R.ler(spawn A(), "segredo")
''')
    assert "private" in erro.message


# ═════════════════════════════════════════════════════════════
#  Heranca, final, sealed, override
# ═════════════════════════════════════════════════════════════

def test_final_blueprint_nao_e_herdado():
    erro = erro_de('''
final blueprint F:
    x := 1
blueprint G extends F:
    y := 1
''')
    assert type(erro).__name__ == "FinalBlueprintError"
    assert diagnosticos("final blueprint F:\n    x := 1\nblueprint G extends F:\n    y := 1\n",
                        "heranca-final")


def test_sealed_aceita_filha_no_mesmo_arquivo_e_recusa_fora(tmp_path):
    assert rodar('''
abstract sealed blueprint Forma:
    abstract action area()
blueprint Q(l) extends Forma:
    action area():
        yield self.l ** 2
out (spawn Q(3)).area()
''') == "9"
    (tmp_path / "formas.df").write_text(
        "abstract sealed blueprint Forma:\n    abstract action area()\nrelay Forma\n",
        encoding="utf-8")
    (tmp_path / "app.df").write_text(
        "adopt ./formas as F\nmonitor:\n    blueprint H extends F.Forma:\n"
        "        action area():\n            yield 0\n"
        "handle SealedBlueprintError:\n    out \"recusado\"\n", encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "run", "app.df"],
                       cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "PYTHONPATH": RAIZ, "NO_COLOR": "1"})
    assert r.stdout.strip() == "recusado", r.stderr


def test_abstract_e_final_juntos_e_recusado_na_leitura():
    with pytest.raises(ParseError):
        parse(tokenize("abstract final blueprint X:\n    x := 1\n", "t"), "t")


def test_override_sem_alvo():
    erro = erro_de('''
blueprint A:
    action falar():
        yield 1
blueprint B extends A:
    override action fala():
        yield 2
''')
    assert type(erro).__name__ == "OverrideTargetError"
    assert "falar" in (erro.dica or "")


def test_override_de_metodo_de_contrato_vale():
    assert rodar('''
contract Som:
    action som()
blueprint Gato with Som:
    override action som():
        yield "miau"
out (spawn Gato()).som()
''') == "miau"


def test_override_de_propriedade():
    assert rodar('''
blueprint A:
    get nome():
        yield "a"
blueprint B extends A:
    override get nome():
        yield "b"
out (spawn B()).nome
''') == "b"


def test_final_de_metodo_continua_valendo():
    erro = erro_de('''
blueprint A:
    final action id():
        yield 1
blueprint B extends A:
    action id():
        yield 2
''')
    assert type(erro).__name__ == "FinalOverrideError"


def test_substituicao_quebrada_e_aviso():
    avisos = diagnosticos('''
blueprint A:
    action f(x, y := 0):
        yield x
blueprint B extends A:
    action f(x):
        yield x
''', "substituicao-quebrada")
    assert avisos and avisos[0].severity == "warning"


def test_substituicao_compativel_nao_avisa():
    assert not diagnosticos('''
blueprint A:
    action f(x):
        yield x
blueprint B extends A:
    action f(x, extra := 1):
        yield x
    action setup(a, b, c):
        self.a := a
''', "substituicao-quebrada")


# ═════════════════════════════════════════════════════════════
#  Polimorfismo e sobrecarga
# ═════════════════════════════════════════════════════════════

def test_sobrecarga_por_aridade_e_tipo():
    assert rodar('''
overload action f(x: Integer):
    yield "int"
overload action f(x: Float):
    yield "float"
overload action f(x: String, n: Integer):
    yield "dois"
out f(1), f(1.5), f("a", 2)
''') == "int float dois"


def test_sobrecarga_em_metodo_e_construtor():
    assert rodar('''
blueprint Cor:
    v := 0
    overload action setup(cinza: Integer):
        self.v := cinza
    overload action setup(r: Integer, g: Integer, b: Integer):
        self.v := r + g + b
    overload action escala(k: Integer):
        yield self.v * k
    overload action escala(k: String):
        yield k
out (spawn Cor(5)).v, (spawn Cor(1, 2, 3)).escala(2), (spawn Cor(1)).escala("x")
''') == "5 12 x"


def test_sobrecarga_sem_variante_que_sirva():
    erro = erro_de('''
overload action f(x: Integer):
    yield 1
overload action f(x: String):
    yield 2
f(yes)
''')
    assert type(erro).__name__ == "OverloadResolutionError"
    assert "f(x: Integer)" in erro.nota


def test_sobrecarga_ambigua():
    erro = erro_de('''
overload action f(x: Integer, y):
    yield 1
overload action f(x, y: Integer):
    yield 2
f(1, 2)
''')
    assert type(erro).__name__ == "AmbiguousOverloadError"


def test_sobrecarga_com_mesma_assinatura_e_recusada():
    erro = erro_de('''
blueprint S:
    overload action f(x: Integer):
        yield 1
    overload action f(y: Integer):
        yield 2
''')
    assert type(erro).__name__ == "AmbiguousOverloadError"
    assert diagnosticos('''
blueprint S:
    overload action f(x: Integer):
        yield 1
    overload action f(y: Integer):
        yield 2
''', "sobrecarga-duplicada")


def test_sobrecarga_nao_e_declaracao_repetida_nem_aridade():
    diags = diagnosticos('''
overload action f(x):
    yield 1
overload action f(x, y):
    yield 2
out f(1), f(1, 2)
''')
    assert not [d for d in diags if d.code in ("declaracao-repetida", "arity")
                or d.severity == "error"]


def test_filha_acrescenta_variante():
    assert rodar('''
blueprint A:
    overload action f(x: Integer):
        yield "a-int"
blueprint B extends A:
    overload action f(x: String):
        yield "b-str"
b := spawn B()
out b.f(1), b.f("s")
''') == "a-int b-str"


# ═════════════════════════════════════════════════════════════
#  Interfaces (contratos), abstratos e traits
# ═════════════════════════════════════════════════════════════

def test_contrato_com_corpo_e_recusado_na_leitura():
    with pytest.raises(ParseError):
        parse(tokenize("contract C:\n    action f():\n        yield 1\n", "t"), "t")


def test_contrato_incompleto():
    erro = erro_de('''
contract Repo:
    action salvar(item)
    action buscar(id)
blueprint R with Repo:
    action salvar(item):
        yield item
''')
    assert type(erro).__name__ == "TraitContractError"
    assert "buscar" in erro.message


def test_contrato_herdado_e_cobrado():
    erro = erro_de('''
contract Leitura:
    action ler()
contract Escrita extends Leitura:
    action escrever(x)
blueprint Arq with Escrita:
    action escrever(x):
        yield x
''')
    assert "ler" in erro.message
    assert diagnosticos('''
contract Leitura:
    action ler()
contract Escrita extends Leitura:
    action escrever(x)
blueprint Arq with Escrita:
    action escrever(x):
        yield x
''', "contrato-de-trait")


def test_aridade_incompativel_com_contrato():
    erro = erro_de('''
contract C:
    action salvar(item, destino)
blueprint R with C:
    action salvar(item):
        yield item
''')
    assert type(erro).__name__ == "SignatureMismatchError"


def test_propriedade_exigida_por_contrato():
    erro = erro_de('''
contract Medivel:
    get tamanho() -> Integer
blueprint Caixa with Medivel:
    x := 1
''')
    assert "tamanho" in erro.message
    assert rodar('''
contract Medivel:
    get tamanho() -> Integer
blueprint Caixa with Medivel:
    tamanho := 3
out (spawn Caixa()).tamanho
''') == "3"


def test_contrato_como_tipo_inclusive_o_herdado():
    assert rodar('''
contract Leitura:
    action ler()
contract Arquivo extends Leitura:
    action fechar()
blueprint Local with Arquivo:
    action ler():
        yield "ok"
    action fechar():
        yield void
action usar(f: Leitura):
    yield f.ler()
out usar(spawn Local())
''') == "ok"


def test_contrato_nao_se_instancia_nem_se_herda():
    assert type(erro_de("contract C:\n    action f()\nspawn C()\n")).__name__ \
        == "AbstractInstantiationError"
    erro = erro_de("contract C:\n    action f()\nblueprint B extends C:\n    x := 1\n")
    assert "with" in (erro.dica or "")
    assert diagnosticos("contract C:\n    action f()\nx := spawn C()\n", "spawn-de-contrato")


def test_trait_com_padrao_continua_valendo():
    assert rodar('''
trait Saudavel:
    action saudar():
        yield "oi, " + self.nome()
    action nome()
blueprint P with Saudavel:
    action nome():
        yield "ana"
out (spawn P()).saudar()
''') == "oi, ana"


# ═════════════════════════════════════════════════════════════
#  Design por contrato
# ═════════════════════════════════════════════════════════════

CONTA = '''
blueprint Conta:
    saldo := 0
    invariant self.saldo bigger_eq 0, "saldo negativo"
    action depositar(v):
        expects v bigger 0, "valor precisa ser positivo"
        promises self.saldo is before(self.saldo) + v
        self.saldo += v
        yield self.saldo
    action sacar(v):
        self.saldo -= v
    action errado(v):
        promises self.saldo is before(self.saldo) + v, "nao somou"
        self.saldo += 1
'''


def test_expects_culpa_quem_chamou():
    erro = erro_de(CONTA + "(spawn Conta()).depositar(-1)")
    assert type(erro).__name__ == "PreconditionError"
    assert "positivo" in erro.message


def test_promises_culpa_a_acao():
    erro = erro_de(CONTA + "(spawn Conta()).errado(5)")
    assert type(erro).__name__ == "PostconditionError"
    assert "nao somou" in erro.message


def test_invariant_depois_do_metodo_publico():
    erro = erro_de(CONTA + "(spawn Conta()).sacar(10)")
    assert type(erro).__name__ == "InvariantError"
    assert "sacar" in erro.message


def test_contrato_cumprido_passa():
    assert rodar(CONTA + "c := spawn Conta()\nout c.depositar(5)") == "5"


def test_invariant_nao_e_cobrada_no_meio_do_metodo():
    assert rodar('''
blueprint Par:
    a := 1
    b := 1
    invariant self.a is self.b
    action trocar(v):
        self.a := v
        self.b := v
    action ajudante():
        self.a := 99
p := spawn Par()
p.trocar(5)
out p.a
''') == "5"


def test_invariant_da_mae_vale_na_filha():
    erro = erro_de('''
blueprint Positivo:
    n := 1
    invariant self.n bigger 0
blueprint Filho extends Positivo:
    action zerar():
        self.n := 0
(spawn Filho()).zerar()
''')
    assert type(erro).__name__ == "InvariantError"


def test_invariant_depois_da_construcao():
    erro = erro_de('''
blueprint N(v):
    invariant self.v bigger 0, "precisa ser positivo"
spawn N(-1)
''')
    assert type(erro).__name__ == "InvariantError"


def test_promises_fora_do_topo_e_invariant_fora_do_blueprint():
    assert diagnosticos("action f(x):\n    given yes:\n        promises x is 1\n    yield x\n",
                        "promises-fora-do-topo")
    assert diagnosticos("invariant yes\n", "invariant-fora")
    assert "blueprint" in erro_de("invariant yes\n").message


def test_palavras_de_contrato_continuam_livres_como_nome():
    assert rodar('''
expects := 1
promises := 2
invariant := 3
contract := 4
readonly := 5
out expects + promises + invariant + contract + readonly
''') == "15"


# ═════════════════════════════════════════════════════════════
#  Operadores e metodos magicos
# ═════════════════════════════════════════════════════════════

MAGICO = '''
blueprint Dinheiro(c):
    action __int__():
        yield self.c
    action __float__():
        yield self.c / 100
    action __round__(n := 0):
        yield self.c
    action __abs__():
        yield abs(self.c)
    action __hash__():
        yield self.c
    action __eq__(o):
        yield self.c is o.c
    action __lt__(o):
        yield self.c smaller o.c
    action __format__(spec):
        yield "R$" + str(self.c)
    action __reversed__():
        yield [3, 2, 1]
'''


@pytest.mark.parametrize("uso,esperado", [
    ("out int(spawn Dinheiro(5))", "5"),
    ("out float(spawn Dinheiro(250))", "2.5"),
    ("out round(spawn Dinheiro(7))", "7"),
    ("out abs(spawn Dinheiro(-3))", "3"),
    ("out hash(spawn Dinheiro(4)) is hash(spawn Dinheiro(4))", "yes"),
    ("out sorted([spawn Dinheiro(3), spawn Dinheiro(1)])[0].c", "1"),
    ("out min([spawn Dinheiro(3), spawn Dinheiro(1)]).c", "1"),
    ("d := {}\nd[spawn Dinheiro(9)] := 1\nout d[spawn Dinheiro(9)]", "1"),
    ("out $\"{spawn Dinheiro(5):x}\"", "R$5"),
    ("out reversed(spawn Dinheiro(1))", "[3, 2, 1]"),
])
def test_protocolos_honram_os_magicos(uso, esperado):
    assert rodar(MAGICO + uso) == esperado


def test_conversao_sem_magico_nao_vaza_nome_do_python():
    erro = erro_de("blueprint X:\n    a := 1\nout int(spawn X())\n")
    assert "DFInstance" not in erro.message
    assert "__int__" in erro.message


def test_getattr_setattr_e_delattr():
    assert rodar('''
blueprint Dinamico:
    action __getattr__(nome):
        yield "sem " + nome
    action __setattr__(nome, valor):
        out "grava", nome, valor
    action __delattr__(nome):
        out "apaga", nome
d := spawn Dinamico()
out d.qualquer
d.x := 3
delete d.x
''') == "sem qualquer\ngrava x 3\napaga x"


def test_getattribute_intercepta_e_le_cru_por_dentro():
    assert rodar('''
blueprint Contador:
    leituras := 0
    valor := 7
    action __getattribute__(nome):
        given nome is "valor":
            yield self.valor * 10
        yield self.leituras
out (spawn Contador()).valor
''') == "70"


def test_descritor_valida_campo():
    assert rodar('''
blueprint Positivo:
    valores := {}
    action __set_name__(dono, nome):
        self.nome := nome
    action __get__(obj, dono):
        yield self.valores[id(obj)] ?? 0
    action __set__(obj, v):
        given v smaller 0:
            trigger $"{self.nome} não pode ser negativo"
        self.valores[id(obj)] := v
blueprint Produto:
    preco := spawn Positivo()
p := spawn Produto()
p.preco := 10
out p.preco
monitor:
    p.preco := -1
handle Error as e:
    out e.message
''') == "10\npreco não pode ser negativo"


def test_init_subclass():
    assert rodar('''
filhas := []
blueprint Base:
    static action __init_subclass__(filha):
        filhas.append(typeof(filha))
blueprint A extends Base:
    x := 1
out len(filhas)
''') == "1"


def test_exit_com_tres_argumentos():
    assert rodar('''
blueprint R:
    action __enter__():
        yield self
    action __exit__(tipo, erro, pilha):
        out "saiu", tipo is void
with spawn R() as r:
    out "dentro"
''') == "dentro\nsaiu yes"


def test_with_numa_instancia_copia_sem_estourar():
    assert rodar('''
blueprint P:
    x := 1
    y := 2
p := spawn P()
q := p with {"x": 9}
out q.x, q.y, p.x
''') == "9 2 1"


# ═════════════════════════════════════════════════════════════
#  Metaclasses e metaprogramacao
# ═════════════════════════════════════════════════════════════

def test_metaclasse_registra_e_e_herdada():
    assert rodar('''
adopt Arcane.Reflexo as R
meta blueprint Registro:
    nomes := []
    action on_forge(molde):
        self.nomes.append(R.nome(molde))
blueprint Base using Registro:
    x := 1
blueprint Filha extends Base:
    y := 1
out R.meta_instancia(Filha).nomes
''') == '[Base, Filha]'


def test_ganchos_de_instancia():
    assert rodar('''
meta blueprint Espiao:
    log := []
    action on_spawn(molde, args):
        self.log.append("spawn")
    action on_ready(obj):
        self.log.append("ready")
    action on_call(obj, nome, args):
        self.log.append("call " + nome)
    action on_write(obj, nome, valor):
        self.log.append("write " + nome)
        yield valor * 2
    action on_read(obj, nome, valor):
        self.log.append("read " + nome)
    action on_missing(obj, nome):
        yield "faltou " + nome
blueprint Alvo using Espiao:
    n := 1
    action mudar(v):
        self.n := v
a := spawn Alvo()
a.mudar(5)
out a.n
out a.nada
adopt Arcane.Reflexo as R
out R.meta_instancia(Alvo).log
''') == ('10\nfaltou nada\n'
         '[spawn, ready, call mudar, write n, read n, read nada]')


def test_on_spawn_pode_entregar_singleton():
    assert rodar('''
adopt Arcane.Reflexo as R
meta blueprint Unico:
    feitos := {}
    action on_spawn(molde, args):
        yield self.feitos[R.nome(molde)] ?? void
    action on_ready(obj):
        self.feitos[R.nome(obj)] := obj
blueprint Config using Unico:
    x := 1
out (spawn Config()) is (spawn Config())
''') == "yes"


def test_on_forge_pode_validar():
    erro = erro_de('''
meta blueprint Exige:
    action on_forge(molde):
        trigger "recusado pela metaclasse"
blueprint X using Exige:
    x := 1
''')
    assert "recusado pela metaclasse" in erro.message


def test_gancho_desconhecido():
    erro = erro_de("meta blueprint M:\n    action on_forje(m):\n        yield void\n")
    assert type(erro).__name__ == "MetaclassError"
    assert "on_forge" in erro.dica
    assert diagnosticos("meta blueprint M:\n    action on_forje(m):\n        yield void\n",
                        "gancho-desconhecido")


def test_using_de_blueprint_comum_e_conflito():
    assert type(erro_de("blueprint A:\n    x := 1\nblueprint B using A:\n    y := 1\n")).__name__ \
        == "MetaclassError"
    erro = erro_de('''
meta blueprint M1:
    action on_ready(o):
        yield void
meta blueprint M2:
    action on_ready(o):
        yield void
blueprint A using M1:
    x := 1
blueprint B extends A using M2:
    y := 1
''')
    assert type(erro).__name__ == "MetaclassError"


def test_augment_acrescenta_e_recusa():
    assert rodar('''
blueprint Ponto(x, y):
    action soma():
        yield self.x + self.y
p := spawn Ponto(1, 2)
augment Ponto:
    action dobro():
        yield self.soma() * 2
out p.dobro()
''') == "6"
    assert type(erro_de('''
blueprint P:
    action f():
        yield 1
augment P:
    action f():
        yield 2
''')).__name__ == "AugmentError"
    assert type(erro_de("final blueprint F:\n    x := 1\naugment F:\n    action g():\n        yield 1\n")).__name__ \
        == "AugmentError"


def test_reflexao_define_metodo_e_cria_blueprint():
    assert rodar('''
adopt Arcane.Reflexo as R
blueprint Caixa:
    n := 2
R.definir_metodo(Caixa, "dobro", lambda => 4)
Ponto := R.criar_blueprint("Ponto", {
    "campos": {"x": 3, "y": 4},
    "metodos": {"norma": lambda p => sqrt(p.x ** 2 + p.y ** 2)},
})
out (spawn Caixa()).dobro(), R.instanciar(Ponto).norma(), R.procurar("Ponto") is Ponto
''') == "4 5.0 yes"


def test_reflexao_descreve_os_membros():
    saida = rodar('''
adopt Arcane.Reflexo as R
contract C:
    action f()
abstract blueprint A with C:
    readonly id := 0
    mark @Coluna("chave")
    codigo := ""
    static steady MAX := 3
blueprint B extends A:
    override action f():
        yield 1
    exclusive action g():
        yield 2
out R.especie(C), R.mro(B)[1] is A, R.contratos(B)
out R.modificadores(B, "id"), R.modificadores(A, "MAX")
out R.anotacoes(A, "codigo")[0]["nome"], "g" in R.membros(B)
out "exclusive" in R.modificadores(B, "g"), B in R.herdeiros(A)
''')
    assert saida.splitlines() == [
        'contract yes [C]',
        '[public, readonly] [public, static, steady]',
        'Coluna yes',
        'yes yes']


def test_diagrama_mermaid():
    saida = rodar('''
adopt Arcane.Reflexo as R
contract Forma:
    action area()
blueprint Q(lado: Float) with Forma:
    action area():
        yield self.lado ** 2
out R.diagrama([Forma, Q])
''')
    assert "classDiagram" in saida
    assert "Forma <|.. Q" in saida
    assert "<<interface>>" in saida


# ═════════════════════════════════════════════════════════════
#  Decoradores e anotacoes
# ═════════════════════════════════════════════════════════════

def test_decorador_em_campo_e_anotacao_empilhada():
    assert rodar('''
adopt Arcane.Reflexo as R
blueprint Usuario:
    @Chave
    @Coluna("id_usuario")
    id := 0
out [a["nome"] cycle a in R.anotacoes(Usuario, "id")]
''') == '[Chave, Coluna]'


def test_decorador_em_propriedade():
    assert rodar('''
adopt Arcane.Reflexo as R
action Cache(alvo):
    yield void
blueprint A:
    @Cache
    get pesado():
        yield 1
out R.anotacoes(A, "pesado")[0]["nome"]
''') == "Cache"


def test_modificador_sem_membro_e_erro_de_leitura():
    with pytest.raises(ParseError):
        parse(tokenize("blueprint A:\n    lazy x := 1\n", "t"), "t")
    with pytest.raises(ParseError):
        parse(tokenize("blueprint A:\n    readonly action f():\n        yield 1\n", "t"), "t")


# ═════════════════════════════════════════════════════════════
#  Injecao de dependencia
# ═════════════════════════════════════════════════════════════

DI = '''
adopt Arcane.Injecao as DI
contract Repo:
    action salvar(x)
blueprint RepoMem with Repo:
    itens := []
    action salvar(x):
        self.itens.append(x)
        yield len(self.itens)
blueprint Servico(repo: Repo, prefixo := "p"):
    action registrar(x):
        yield self.repo.salvar(self.prefixo + x)
'''


def test_injecao_por_construtor_e_escopos():
    assert rodar(DI + '''
c := DI.conteiner()
c.unico(Repo, RepoMem)
s1 := c.resolver(Servico)
s2 := c.resolver(Servico)
out s1 isnt s2, s1.repo is s2.repo, s1.registrar("a"), s2.registrar("b")
''') == "yes yes 1 2"


def test_injecao_valor_fabrica_preguicoso_e_campo():
    assert rodar(DI + '''
blueprint Tela:
    @Injetar
    repo: Repo := void
c := DI.conteiner()
c.valor(Repo, spawn RepoMem())
c.fabrica(Servico, lambda k => spawn Servico(k.resolver(Repo), "f"))
t := c.resolver(Tela)
p := c.preguicoso(Repo)
out c.resolver(Servico).registrar("x"), t.repo is c.resolver(Repo), p.pronto(), p.valor is t.repo
''') == "1 yes no yes"


def test_injecao_recusa_o_que_falta_ciclo_e_cativo():
    assert type(erro_de(DI + "DI.conteiner().resolver(Servico)")).__name__ \
        == "DependencyResolutionError"
    erro = erro_de('''
adopt Arcane.Injecao as DI
blueprint A(b: B):
    x := 1
blueprint B(a: A):
    x := 1
DI.conteiner().resolver(A)
''')
    assert type(erro).__name__ == "CircularDependencyError"
    assert "A → B → A" in erro.message
    cativo = erro_de(DI + '''
c := DI.conteiner()
c.por_escopo(Repo, RepoMem)
c.unico(Servico)
c.resolver(Servico)
''')
    assert "per scope" in cativo.message


def test_por_escopo_e_fechar():
    assert rodar('''
adopt Arcane.Injecao as DI
blueprint Conexao:
    aberta := yes
    action fechar():
        self.aberta := no
c := DI.conteiner()
c.por_escopo(Conexao)
e := c.escopo()
a := e.resolver(Conexao)
iguais := a is e.resolver(Conexao)
e.fechar()
out iguais, a.aberta, c.escopo().resolver(Conexao) isnt a
''') == "yes no yes"


def test_conferir_lista_problemas():
    assert rodar(DI + '''
c := DI.conteiner()
c.transitorio(Servico)
out len(c.conferir())
''') == "1"


# ═════════════════════════════════════════════════════════════
#  Eventos, padroes e serializacao
# ═════════════════════════════════════════════════════════════

def test_observavel_com_prioridade_filtro_e_parar():
    assert rodar('''
adopt Arcane.Padroes as P
log := []
ev := P.observavel()
ev.assinar(lambda d => log.append("baixa"), 0)
ev.assinar(lambda d => log.append("alta"), 10)
ev.assinar(lambda d => log.append("filtrada"), 5, lambda d => d bigger 100)
n := ev.notificar(1)
out log, n
''') == '[alta, baixa] 2'


def test_padroes_criacionais():
    assert rodar('''
adopt Arcane.Padroes as P
blueprint Conexao:
    usos := 0
unico := P.unico(Conexao)
pool := P.pool(lambda => spawn Conexao(), 1)
pool.usar(lambda c => c.usos)
monitor:
    pool.usar(lambda c => 1 / 0)
handle Error:
    out "erro"
proto := P.prototipos()
proto.registrar("padrao", spawn Conexao())
copia := proto.criar("padrao", {"usos": 5})
blueprint Pessoa(nome, idade := 0):
    x := 1
b := P.construtor(Pessoa, ["nome"]).com("nome", "ana").com("idade", 3).construir()
fly := P.compartilhado(lambda cor => [cor])
out unico() is unico(), pool.livres, copia.usos, b.idade, fly("azul") is fly("azul")
''') == "erro\nyes 1 5 3 yes"


def test_padroes_comportamentais():
    assert rodar('''
adopt Arcane.Padroes as P
blueprint Soma(alvo, n):
    action executar():
        self.alvo["v"] := self.alvo["v"] + self.n
    action desfazer():
        self.alvo["v"] := self.alvo["v"] - self.n
estado := {"v": 0}
cmds := P.comandos()
cmds.executar(spawn Soma(estado, 5))
cmds.executar(spawn Soma(estado, 2))
cmds.desfazer()
cadeia := P.cadeia([lambda p, prox => ("pequeno" given p smaller 10 otherwise prox()),
                    lambda p, prox => "grande"])
blueprint No:
    x := 1
blueprint Folha extends No:
    y := 1
blueprint Visitante:
    action visitar_No(n):
        yield "no"
m := P.memento(spawn No())
out estado["v"], cadeia(3), cadeia(50), P.visitar(spawn Folha(), spawn Visitante())
''') == "5 pequeno grande no"


def test_serializacao_polimorfica_com_ciclo():
    assert rodar('''
adopt Arcane.Objetos as O
blueprint Cliente(nome):
    pedidos := []
blueprint Pedido(cliente, total):
    x := 1
c := spawn Cliente("ana")
c.pedidos.append(spawn Pedido(c, 10))
v := O.para_vault(c)
volta := O.de_vault(v, [Cliente, Pedido])
out volta.nome, volta.pedidos[0].total, volta.pedidos[0].cliente is volta
''') == "ana 10 yes"


def test_serializacao_recusa_tipo_fora_da_lista_e_esconde_private():
    erro = erro_de('''
adopt Arcane.Objetos as O
blueprint P:
    x := 1
O.de_vault({"$tipo": "Admin"}, [P])
''')
    assert type(erro).__name__ == "UnsafeDeserializationError"
    assert rodar('''
adopt Arcane.Objetos as O
blueprint Conta:
    private senha := "123"
    nome := "ana"
v := O.para_vault(spawn Conta())
out "senha" in v, "nome" in v
''') == "no yes"


def test_desserializacao_confere_invariante():
    erro = erro_de('''
adopt Arcane.Objetos as O
blueprint Idade:
    anos := 0
    invariant self.anos bigger_eq 0
O.de_vault({"$tipo": "Idade", "anos": -3}, [Idade])
''')
    assert type(erro).__name__ == "InvariantError"


# ═════════════════════════════════════════════════════════════
#  Concorrencia e imutabilidade
# ═════════════════════════════════════════════════════════════

def test_exclusive_serializa_o_objeto():
    assert rodar('''
blueprint C:
    n := 0
    exclusive action somar():
        atual := self.n
        self.n := atual + 1
    exclusive action duas():
        self.somar()
        self.somar()
c := spawn C()
parallel:
    thread:
        cycle i from 1 to 400:
            c.duas()
    thread:
        cycle i from 1 to 400:
            c.somar()
out c.n
''') == "1200"


def test_exclusive_estatico_e_recusado():
    with pytest.raises(ParseError):
        parse(tokenize("blueprint A:\n    exclusive static action f():\n        yield 1\n", "t"), "t")


def test_lazy_calcula_uma_vez():
    assert rodar('''
blueprint R:
    vezes := 0
    lazy get total():
        self.vezes += 1
        yield 42
r := spawn R()
out r.total, r.total, r.vezes
''') == "42 42 1"


# ═════════════════════════════════════════════════════════════
#  Metricas e SOLID
# ═════════════════════════════════════════════════════════════

def test_metricas_ck(tmp_path):
    from dataforge import oop_analise
    fonte = tmp_path / "m.df"
    fonte.write_text('''
contract Leitura:
    action ler()
abstract blueprint Base:
    a := 1
    abstract action f()
blueprint Filha extends Base with Leitura:
    b := 2
    action f():
        given self.a bigger 0:
            yield self.a
        yield self.b
    action ler():
        yield self.b
blueprint Neta extends Filha:
    c := 3
''', encoding="utf-8")
    tipos, problemas = oop_analise.analisar([str(fonte)])
    assert not problemas
    assert tipos["Neta"].metricas["dit"] == 2
    assert tipos["Base"].metricas["noc"] == 1
    assert tipos["Filha"].metricas["wmc"] == 3
    assert "Leitura" in tipos["Filha"].referencias


def test_cheiros_de_solid(tmp_path):
    from dataforge import oop_analise
    fonte = tmp_path / "s.df"
    metodos = "\n".join(f"    action m{i}():\n        yield {i}" for i in range(22))
    fonte.write_text(f'''
contract Gordo:
{chr(10).join(f"    action a{i}()" for i in range(9))}
blueprint Deus:
{metodos}
blueprint Ave:
    action voar():
        yield 1
blueprint Pinguim extends Ave:
    override action voar():
        trigger "pinguim não voa"
blueprint Relatorio:
    action gerar(x):
        given typeof(x) is "Integer":
            yield 1
        orif typeof(x) is "String":
            yield 2
        orif typeof(x) is "Float":
            yield 3
''', encoding="utf-8")
    tipos, _ = oop_analise.analisar([str(fonte)])
    codigos = {c["codigo"]: c["principio"] for t in tipos.values() for c in t.cheiros}
    assert codigos["god-blueprint"] == "SRP"
    assert codigos["contrato-gordo"] == "ISP"
    assert codigos["sobrescrita-que-recusa"] == "LSP"
    assert codigos["switch-de-tipo"] == "OCP"


def test_comando_oop_e_diagrama(tmp_path):
    (tmp_path / "a.df").write_text(
        "blueprint A:\n    x := 1\nblueprint B extends A:\n    y := 2\n", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": RAIZ, "NO_COLOR": "1"}
    r = subprocess.run([sys.executable, "-m", "dataforge", "oop", "a.df", "--diagrama"],
                       cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", env=env)
    assert r.returncode == 0 and "A <|-- B" in r.stdout
    r = subprocess.run([sys.executable, "-m", "dataforge", "oop", "a.df", "--json"],
                       cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", env=env)
    import json
    assert {t["nome"] for t in json.loads(r.stdout)["tipos"]} == {"A", "B"}


def test_lsp_implementacao_e_hierarquia():
    from dataforge import lsp
    fonte = ("contract C:\n    action f()\n"
             "blueprint A with C:\n    action f():\n        yield 1\n"
             "blueprint B extends A:\n    action f():\n        yield 2\n")
    a = lsp.analisar(fonte, "file:///t.df")
    impl = lsp.implementacoes(a, 1, 10)
    assert [i["range"]["start"]["line"] for i in impl] == [2, 5]
    assert [x["name"] for x in lsp.hierarquia_abaixo(a, {"name": "A"})] == ["B"]
    assert [x["name"] for x in lsp.hierarquia_acima(a, {"name": "A"})] == ["C"]


# ═════════════════════════════════════════════════════════════
#  O repositorio continua limpo, e a doc roda
# ═════════════════════════════════════════════════════════════

def _blocos_df_das_paginas():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import oop_meta
    for pagina in oop_meta.PAGINAS:
        for i, bloco in enumerate(pagina["blocos"]):
            if "code" in bloco and bloco.get("lang") == "df":
                yield f"{pagina['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_das_paginas()))
def test_todo_exemplo_da_doc_de_oop_roda_e_passa_no_check(onde, codigo):
    rodar(codigo, "<doc>")
    erros = [d for d in diagnosticos(codigo) if d.severity == "error"]
    assert not erros, f"{onde}: {[d.message for d in erros]}"


def test_a_referencia_de_blueprints_roda():
    texto = open(os.path.join(RAIZ, "doc", "REFERENCIA.md"), encoding="utf-8").read()
    secao = texto[texto.index("## 7. Blueprints"):texto.index("## 8. Erros")]
    blocos = re.findall(r"```dataforge\n(.*?)```", secao, re.S)
    assert len(blocos) >= 10
    for bloco in blocos:
        rodar(bloco, "<referencia>")


def test_invariante_que_chama_metodo_publico_nao_recursa():
    """Achado escrevendo o guia: 'invariant self.area() bigger_eq 0' recursava.

    Conferir a invariante chamava 'area', que, sendo publica e de fora,
    conferia a invariante — que chamava 'area'. O caso mais natural de
    escrever uma invariante estourava a pilha.
    """
    assert rodar('''
contract Forma:
    action area() -> Float
abstract blueprint Base with Forma:
    invariant self.area() bigger_eq 0.0, "area negativa"
    promises_ok := yes
final blueprint Q(l: Float) extends Base:
    override action area() -> Float:
        yield self.l * self.l
    action dobrar():
        promises self.area() is before(self.area()) * 4
        self.l := self.l * 2
q := spawn Q(2.0)
q.dobrar()
out q.area()
''') == "16.0"
