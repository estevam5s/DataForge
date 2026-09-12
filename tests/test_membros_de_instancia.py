"""`p.clientte` deixa de passar pelo `check` em silêncio.

O buraco mais caro em projeto grande: o analisador não via dentro dos
objetos. Isto passava como "sem erros":

    blueprint Pedido(cliente, total):
        action resumo():
            yield $"{self.clientte}: {self.total}"

O programa roda, imprime o certo, e o `self.clientte` só explode no dia
em que aquele ramo rodar. Num arquivo de 40 linhas você acha na primeira
execução; num sistema de 200 arquivos, você acha em produção.

**Metade destes testes cobra o que ele acusa. A outra metade cobra o que
ele CALA** — e essa é a metade que decide se a ferramenta é usável. Um
falso alarme ensina a ignorar o `check` inteiro, e aí ele deixa de pegar
também o que pegava antes.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.lexer import tokenize             # noqa: E402
from dataforge.parser import parse               # noqa: E402
from dataforge.typechecker import check_program  # noqa: E402


def erros(fonte):
    arvore = parse(tokenize(fonte, "t.df"), "t.df")
    return [d for d in check_program(arvore, "t.df") if d.severity == "error"]


def um_erro(fonte):
    achados = erros(fonte)
    assert len(achados) == 1, \
        f"esperava 1 erro, vieram {len(achados)}: {[d.message for d in achados]}"
    return achados[0]


# ── O que ele passa a acusar ─────────────────────────────────

def test_campo_que_nao_existe():
    erro = um_erro('''
blueprint Pedido(cliente, total):
    action resumo():
        yield $"{self.clientte}"
''')
    assert "no member 'clientte'" in erro.message
    assert "cliente" in erro.hint, "devia sugerir o nome parecido"


def test_metodo_que_nao_existe():
    erro = um_erro('''
blueprint Conta(saldo):
    action sacar(v):
        yield self.saldo - v

c := spawn Conta(100.0)
out c.sacarr(10.0)
''')
    assert "no member 'sacarr'" in erro.message
    assert "sacar" in erro.hint


def test_campo_errado_na_instancia_de_fora():
    erro = um_erro('''
blueprint Usuario(nome, email):
    action rotulo():
        yield self.nome

u := spawn Usuario("Ana", "a@x.com")
out u.emial
''')
    assert "no member 'emial'" in erro.message


def test_sem_nome_parecido_lista_o_que_existe():
    """Quando não há sugestão, a mensagem tem de dizer o que existe."""
    erro = um_erro('''
blueprint A(x):
    action m():
        yield self.zzzzz
''')
    assert "It has:" in erro.hint
    assert "x" in erro.hint and "m" in erro.hint


# ── O que ele CALA, e é onde a ferramenta se prova ───────────

@pytest.mark.parametrize("rotulo,fonte", [
    ("metodo herdado", '''
blueprint Base:
    action falar():
        yield "oi"

blueprint Filha extends Base:
    action usar():
        yield self.falar()
'''),
    ("campo herdado", '''
blueprint Base(x):
    action m():
        yield 1

blueprint Filha(x) extends Base:
    action ver():
        yield self.x
'''),
    ("metodo de trait", '''
trait Falante:
    action falar()

blueprint Gato with Falante:
    action falar():
        yield "miau"

out (spawn Gato()).falar()
'''),
    ("propriedade get", '''
blueprint R(l, a):
    get area():
        yield self.l * self.a

out (spawn R(2, 3)).area
'''),
    ("membro estatico", '''
blueprint C:
    static padrao := "x"

out C.padrao
'''),
    ("campo criado no construtor inline", '''
blueprint Conta(titular):
    this.numero := "123"
    this.ativa := yes

    action estado():
        yield $"{self.numero} {self.ativa}"
'''),
    ("campo criado dentro de um metodo", '''
blueprint Cache:
    action guardar(v):
        self.ultimo := v
        yield v

    action ler():
        yield self.ultimo
'''),
    ("campo declarado com padrao", '''
blueprint Caixa:
    itens: Cluster := []

    action por(x):
        self.itens.append(x)
'''),
    ("metodo magico", '''
blueprint P(v):
    action __add__(o):
        yield self.v + o.v

out (spawn P(1)) + (spawn P(2))
'''),
    ("campo posto de fora", '''
blueprint A:
    action m():
        yield 1

a := spawn A()
a.novo := 7
out a.novo
'''),
])
def test_o_que_e_legitimo_passa_calado(rotulo, fonte):
    achados = erros(fonte)
    assert not achados, \
        f"falso alarme em '{rotulo}': {[d.message for d in achados]}"


def test_mae_desconhecida_desliga_a_conferencia_de_membro():
    """Herdar de algo que o analisador não viu é motivo para silêncio.

    O blueprint pode ganhar qualquer membro pela mãe, e acusar sem poder
    provar é o pior dos dois mundos: o erro real continua passando, e o
    código certo passa a gritar.

    A mãe desconhecida **em si** continua sendo erro — isso é outra
    checagem, anterior a esta, e ela está certa: uma herança que não
    resolve é um problema de verdade.
    """
    achados = erros('''
blueprint X extends VindoDeOutroArquivo:
    action m():
        yield self.qualquerCoisa
''')
    codigos = [d.code for d in achados]
    assert "unknown-member" not in codigos, \
        "nao da para afirmar nada sobre os membros de quem herda do desconhecido"
    assert codigos == ["unknown-parent"], \
        f"so a heranca devia ser acusada, e vieram: {codigos}"


def test_heranca_em_ciclo_nao_trava():
    """Ciclo de herança é erro em outro lugar; aqui não pode ser recursão."""
    erros('''
blueprint A extends B:
    action m():
        yield 1

blueprint B extends A:
    action n():
        yield 2
''')  # basta não travar


def test_tres_niveis_de_heranca():
    assert not erros('''
blueprint Avo:
    action raiz():
        yield 1

blueprint Mae extends Avo:
    action meio():
        yield 2

blueprint Filha extends Mae:
    action tudo():
        yield self.raiz() + self.meio()
''')


# ── A garantia que impede a ferramenta de virar ruído ────────

def test_o_repositorio_inteiro_continua_sem_erro():
    """320 arquivos que funcionam há meses.

    A primeira versão desta checagem deu **32 falsos alarmes** num
    exemplo de sistema bancário: ela olhava `self.x := …` só dentro de
    métodos, e o construtor inline — `this.numero := …` solto no corpo
    do blueprint — escapava.
    """
    import glob
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = subprocess.run(
        [sys.executable, "-m", "dataforge", "check",
         "exercicios/", "examples/", "packages/", "projetos/"],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz,
        env={**os.environ, "PYTHONPATH": raiz, "NO_COLOR": "1"}, timeout=180)

    linhas = [l for l in r.stdout.split("\n") if ": erro:" in l]
    assert not linhas, (
        "a conferencia de membro acusou codigo que funciona:\n  "
        + "\n  ".join(linhas[:10]))
