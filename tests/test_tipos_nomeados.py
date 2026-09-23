"""`type` — alias, união, interseção, refinamento e tipo opaco.

A linguagem sabia declarar `record`, `enum`, `blueprint` e `trait`, e não
sabia dar nome a um TIPO. Sem isso, quatro coisas que toda base grande
pede não tinham como ser escritas:

1. **alias** — `Id` em vez de `Integer` espalhado por 200 arquivos;
2. **união** — o campo que é texto OU número, e nada mais;
3. **refinamento** — `Positivo` é um `Integer` com uma regra, e a regra
   vale em toda fronteira: declaração, parâmetro, retorno e campo;
4. **opaco** — `Cpf` é um texto que ninguém constrói por engano: quem
   quiser um tem de passar pela validação.

O que os testes cobram, e que o jeito ingênuo erraria:

- a regra do refinamento roda na FRONTEIRA, e não só na criação: um
  valor que entra por parâmetro é conferido com a mesma regra;
- o tipo opaco é NOMINAL: um `String` com onze dígitos não é um `Cpf`,
  senão o tipo não protege de nada;
- o `check` prova o que dá para provar antes de rodar, e **cala** no
  resto — um falso alarme ensina a desligar o analisador;
- `type` e `opaque` continuam sendo nomes comuns (`type := 3` roda).
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


# ── alias ────────────────────────────────────────────────────

def test_alias_e_o_tipo_de_baixo():
    assert rodar('''
type Id := Integer
x: Id := 7
action dobro(n: Id) -> Id:
    yield n * 2
out dobro(x), typeof(x)
''') == "14 Integer"


def test_alias_confere_como_o_tipo_original():
    erro = erro_de('type Id := Integer\nx: Id := "sete"\n')
    assert "Id" in erro.message and "Integer" in erro.message
    assert "String" in erro.message


def test_alias_de_alias_e_de_colecao():
    assert rodar('''
type Id := Integer
type Ids := Cluster<Id>
type Chave := Id
xs: Ids := [1, 2]
k: Chave := 3
out len(xs), k
''') == "2 3"
    assert erro_de('type Id := Integer\ntype Ids := Cluster<Id>\n'
                   'xs: Ids := [1, "dois"]\n').line == 3


def test_alias_generico_e_uma_funcao_de_tipo():
    assert rodar('''
type Par<T> := Cluster<T>
p: Par<Integer> := [1, 2]
out len(p)
''') == "2"
    erro = erro_de('type Par<T> := Cluster<T>\np: Par<Integer> := [1, "b"]\n')
    assert "Integer" in erro.message


# ── união ────────────────────────────────────────────────────

def test_uniao_aceita_qualquer_um_dos_membros():
    assert rodar('''
type Json := String | Integer | Boolean | Void
a: Json := "oi"
b: Json := 3
c: Json := yes
d: Json := void
out a, b, c, d
''') == "oi 3 yes void"


def test_uniao_recusa_o_que_nao_esta_na_lista_e_lista_as_opcoes():
    erro = erro_de('type Json := String | Integer\nx: Json := [1]\n')
    assert "Json" in erro.message
    assert "String" in erro.message and "Integer" in erro.message
    assert "Cluster" in erro.message


def test_uniao_anonima_na_anotacao():
    assert rodar('''
action medir(x: Integer | String) -> String:
    yield $"{x}"
out medir(2), medir("a")
''') == "2 a"
    erro = erro_de('action medir(x: Integer | String):\n    yield x\nmedir([1])\n')
    assert "parameter 'x'" in erro.message


def test_uniao_com_record_e_enum():
    assert rodar('''
record Ponto:
    x: Integer
enum Cor:
    Azul
type Coisa := Ponto | Cor
a: Coisa := Ponto(1)
b: Coisa := Cor.Azul
out a.x, b.name
''') == "1 Azul"


# ── interseção ───────────────────────────────────────────────

def test_intersecao_exige_todos_os_lados():
    fonte = '''
trait Serial:
    action serializar()
trait Comparavel:
    action comparar(outro)
blueprint Completo extends Serial, Comparavel:
    action serializar():
        yield "s"
    action comparar(outro):
        yield 0
blueprint SoUm extends Serial:
    action serializar():
        yield "s"
type Ambos := Serial & Comparavel
action usar(x: Ambos) -> String:
    yield x.serializar()
out usar(spawn Completo())
'''
    assert rodar(fonte) == "s"
    erro = erro_de(fonte.replace("out usar(spawn Completo())",
                                 "out usar(spawn SoUm())"))
    assert "Comparavel" in erro.message and "SoUm" in erro.message


# ── refinamento ──────────────────────────────────────────────

def test_refinamento_confere_a_regra_na_declaracao():
    assert rodar('type Positivo := Integer where valor bigger 0\nx: Positivo := 5\nout x') == "5"
    erro = erro_de('type Positivo := Integer where valor bigger 0\nx: Positivo := -5\n')
    assert "Positivo" in erro.message
    assert "valor bigger 0" in erro.message, erro.message
    assert erro.line == 2


@pytest.mark.parametrize("entrada,vale", [("10", True), ("0", False)])
def test_refinamento_vale_em_parametro_retorno_e_campo(entrada, vale):
    fonte = f'''
type Positivo := Integer where valor bigger 0
record Item:
    preco: Positivo
action metade(n: Positivo) -> Positivo:
    yield n ~/ 2
out metade({entrada}), Item({entrada}).preco
'''
    if vale:
        assert rodar(fonte) == "5 10"
    else:
        assert "Positivo" in erro_de(fonte).message


def test_refinamento_no_retorno_acusa_quem_devolve_errado():
    erro = erro_de('''
type Positivo := Integer where valor bigger 0
action f(n) -> Positivo:
    yield n - 10
f(3)
''')
    assert "return value" in erro.message and "Positivo" in erro.message


def test_refinamento_usa_a_base_e_a_regra_e_nesta_ordem():
    """A regra só roda sobre um valor da base: 'len(valor)' num número
    daria um erro do interpretador em vez da mensagem do tipo."""
    erro = erro_de('type Nome := String where len(valor) bigger 2\nx: Nome := 7\n')
    assert "String" in erro.message and "Integer" in erro.message
    assert "len(" not in erro.message


def test_refinamento_sobre_colecao_e_sobre_alias():
    assert rodar('''
type Coordenada := Cluster<Float> where len(valor) is 2
type Rota := Cluster<Coordenada> where len(valor) bigger_eq 2
r: Rota := [[1.0, 2.0], [3.0, 4.0]]
out len(r)
''') == "2"
    assert "Coordenada" in erro_de('''
type Coordenada := Cluster<Float> where len(valor) is 2
c: Coordenada := [1.0, 2.0, 3.0]
''').message


# ── opaco ────────────────────────────────────────────────────

def test_opaco_so_nasce_pela_validacao():
    assert rodar('''
opaque type Cpf := String where len(valor) is 11
c := Cpf("12345678901")
out typeof(c), c.valor, $"{c}"
''') == "Cpf 12345678901 12345678901"
    erro = erro_de('opaque type Cpf := String where len(valor) is 11\nc := Cpf("123")\n')
    assert "Cpf" in erro.message


def test_opaco_e_nominal_um_texto_nao_serve():
    erro = erro_de('''
opaque type Cpf := String where len(valor) is 11
action cadastrar(c: Cpf):
    yield c
cadastrar("12345678901")
''')
    assert "Cpf" in erro.message
    assert "Cpf(" in (erro.dica or ""), erro.dica


def test_opaco_compara_e_serializa_pelo_valor_de_dentro():
    assert rodar('''
adopt Arcane.Serialization as S
adopt Arcane.Collections as C
opaque type Cpf := String where len(valor) is 11
a := Cpf("12345678901")
b := Cpf("12345678901")
out a is b, S.to_json({"cpf": a}), len(C.set([a, b]))
''') == 'yes {"cpf": "12345678901"} 1'


def test_opaco_sobre_numero_faz_conta_pelo_valor():
    assert rodar('''
opaque type Metros := Float where valor bigger_eq 0.0
d := Metros(2.5)
out d.valor * 2, d bigger Metros(1.0)
''') == "5.0 yes"


# ── o que o analisador prova antes de rodar ──────────────────

def test_check_prova_o_literal_contra_a_regra():
    assert diagnosticos('type Positivo := Integer where valor bigger 0\n'
                        'x: Positivo := -1\n', "tipo-refinado")
    assert diagnosticos('type Json := String | Integer\nx: Json := [1]\n', "tipo-uniao")
    assert diagnosticos('opaque type Cpf := String where len(valor) is 11\n'
                        'action f(c: Cpf):\n    yield c\nf("12345678901")\n',
                        "tipo-opaco")


def test_check_cala_quando_nao_prova():
    assert not erros('''
type Positivo := Integer where valor bigger 0
action ler() -> Integer:
    yield 3
x: Positivo := ler()
y: Positivo := 4
out x + y
''')


def test_check_acusa_nome_que_nao_existe_no_tipo():
    d = diagnosticos("type Id := Inteiro\n", "unknown-type")
    assert d and "Integer" in (d[0].hint or "")
    assert diagnosticos("x: NaoExiste := 1\n", "unknown-type")


def test_check_recusa_ciclo_e_nome_repetido():
    assert diagnosticos("type A := B\ntype B := A\n", "tipo-circular")
    assert diagnosticos("type Id := Integer\ntype Id := String\n", "declaracao-repetida")


def test_check_conhece_o_tipo_em_toda_posicao():
    assert not erros('''
type Id := Integer
type Json := String | Integer
record R:
    id: Id
blueprint B:
    id: Id := 0
    action f(x: Json) -> Id:
        yield 1
action g(a: Id, b: Json) -> Cluster<Id>:
    yield [a]
out len(g(1, "x"))
''')


# ── sintaxe, ferramentas e convivência ───────────────────────

def test_type_e_opaque_continuam_sendo_nomes():
    assert rodar('type := 3\nopaque := 4\nwhere := 5\n'
                 'out type + opaque + where') == "12"
    assert rodar('action type(x):\n    yield x\nout type(2)') == "2"


def test_a_declaracao_incompleta_explica_o_que_falta():
    with pytest.raises(ParseError) as erro:
        parse(tokenize("type Id\n", "t"), "t")
    assert ":=" in erro.value.message
    with pytest.raises(ParseError) as erro:
        parse(tokenize("type Id := Integer where\n", "t"), "t")
    assert "valor" in erro.value.message.lower()


def test_o_formatador_e_idempotente_com_os_tipos():
    fonte = ('type Json := String | Integer\n'
             'type Positivo := Integer where valor bigger 0\n'
             'opaque type Cpf := String where len(valor) is 11\n')
    formatado = format_source(fonte)
    assert "String | Integer" in formatado
    assert "where valor bigger 0" in formatado
    assert "opaque type Cpf" in formatado
    assert format_source(formatado) == formatado


def test_o_tipo_atravessa_o_adopt(tmp_path):
    (tmp_path / "tipos.df").write_text(
        'type Positivo := Integer where valor bigger 0\n'
        'opaque type Cpf := String where len(valor) is 11\n'
        'relay Positivo, Cpf\n', encoding="utf-8")
    (tmp_path / "main.df").write_text(
        'adopt ./tipos as T\n'
        'x: T.Positivo := 4\n'
        'c := T.Cpf("12345678901")\n'
        'out x, c.valor\n', encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "run",
                        str(tmp_path / "main.df")], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", cwd=RAIZ,
                       env={**os.environ, "NO_COLOR": "1"})
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "4 12345678901"


def test_a_mensagem_nao_cita_tipo_do_python():
    erro = erro_de('type Positivo := Integer where valor bigger 0\nx: Positivo := "a"\n')
    for palavra in ("str", "int", "list", "dict", "NoneType"):
        assert f"'{palavra}'" not in erro.message


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import tipos_nomeados
    for pagina in tipos_nomeados.PAGINAS:
        for i, bloco in enumerate(pagina["blocos"]):
            # Um bloco com 'title' e um ARQUIVO de um exemplo de varios
            # arquivos: ele nao roda sozinho, e e conferido pelo
            # 'tools/verificar_docs.py', que compila sem executar.
            if "code" in bloco and bloco.get("lang") == "df" \
                    and not bloco.get("title"):
                yield f"{pagina['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_da_doc()))
def test_todo_exemplo_da_doc_roda_e_passa_no_check(onde, codigo):
    """Um exemplo de documentação que não roda ensina errado."""
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


# ═══════════════════════════════════════════════════════════
#  Tipos literais
# ═══════════════════════════════════════════════════════════

class TestTipoLiteral:
    """'type Estado := "ativo" | "inativo"' — o valor vira o tipo.

    Ele era **erro de sintaxe**: o parser esperava um nome onde um
    literal aparecia, e a mensagem falava de "a type", sem dizer que a
    forma não existia. O que se escrevia no lugar era a comparação à mão
    em toda fronteira — e esquecida numa delas.
    """

    def test_a_declaracao_compila(self):
        rodar('type Estado := "ativo" | "inativo"\nout 1\n')

    def test_o_valor_certo_passa_na_fronteira(self):
        saida = rodar('''type Estado := "ativo" | "inativo"

action mudar(e: Estado) -> String:
    yield e

out mudar("ativo")
''')
        assert "ativo" in saida

    def test_o_valor_de_fora_e_recusado_em_EXECUCAO(self):
        with pytest.raises(DataForgeError) as info:
            rodar('''type Estado := "ativo" | "inativo"

action mudar(e: Estado) -> String:
    yield e

out mudar("zzz")
''')
        assert "Estado" in str(info.value)

    def test_o_check_prova_com_o_literal_na_mao(self):
        ruins = [d for d in diagnosticos(
            'type Estado := "ativo" | "inativo"\ne: Estado := "zzz"\nout e\n')
            if d.severity == "error"]
        assert ruins, "o literal errado tinha de ser provado antes de rodar"
        assert ruins[0].code == "tipo-literal"
        assert '"ativo"' in ruins[0].hint

    def test_e_CALA_quando_o_valor_nao_e_literal(self):
        """Sem esta linha ele recusaria o código para o qual o tipo existe.

        Ler a entrada e passá-la adiante é o caso normal, e ali o
        analisador não tem nada para provar — quem cobra é a fronteira.
        """
        ruins = [d for d in diagnosticos('''type Estado := "ativo" | "inativo"

action mudar(e: Estado) -> String:
    yield e

vindo_de_fora := input() ?? "ativo"
out mudar(vindo_de_fora)
''') if d.severity == "error"]
        assert not ruins, [d.message for d in ruins]

    def test_numero_e_booleano_tambem(self):
        saida = rodar('''type Nivel := 1 | 2 | 3
type Ligado := yes

action nivel(n: Nivel) -> Integer:
    yield n * 10

l: Ligado := yes
out nivel(2), l
''')
        assert "20" in saida

    def test_yes_e_1_nao_se_confundem(self):
        """Em Python `True == 1`. Sem conferir o TIPO, um
        `type Ligado := yes` aceitaria o número 1 calado — um valor que
        ninguém escreveu passando por um tipo que existe para não
        deixar."""
        with pytest.raises(DataForgeError):
            rodar('''type Ligado := yes

action ligar(v: Ligado) -> Boolean:
    yield v

out ligar(1)
''')

    def test_a_base_de_uma_uniao_de_literais_e_conhecida(self):
        """'-> String' devolvendo um Estado é código certo.

        Sem esta leitura, a forma mais natural de usar o recurso era
        acusada de devolver o que não declarou."""
        ruins = [d for d in diagnosticos('''type Estado := "ativo" | "inativo"

action rotulo(e: Estado) -> String:
    yield e + "!"

out rotulo("ativo")
''') if d.severity == "error"]
        assert not ruins, [d.message for d in ruins]

    def test_uniao_MISTA_nao_tem_base_e_o_analisador_cala(self):
        """'"auto" | Integer' não tem base única, e escolher uma faria o
        analisador aprovar o que a execução recusa."""
        ruins = [d for d in diagnosticos('''type Modo := "auto" | Integer

action usar(m: Modo) -> String:
    yield str(m)

out usar("auto"), usar(3)
''') if d.severity == "error"]
        assert not ruins, [d.message for d in ruins]

    def test_as_aspas_fazem_parte_do_tipo(self):
        """Sem elas, 'type T := "Integer"' e 'type T := Integer' viram a
        mesma string — e o primeiro, que só aceita a palavra "Integer",
        passaria a aceitar qualquer número."""
        from dataforge.tipos_nomeados import (base_de_tipo_literal,
                                              e_tipo_literal,
                                              valor_do_tipo_literal)
        assert e_tipo_literal('"Integer"')
        assert not e_tipo_literal("Integer")
        assert base_de_tipo_literal('"Integer"') == "String"
        assert valor_do_tipo_literal('"Integer"') == "Integer"


# ═══════════════════════════════════════════════════════════
#  Método que não existe num tipo embutido
# ═══════════════════════════════════════════════════════════

class TestMetodoEmbutido:
    """`p.clientte` num record era acusado; `"ana".naoExiste()` não.

    Medido numa bateria de quinze erros que **falham em execução**: o
    `check` pegava oito, e quatro dos sete silêncios eram este mesmo
    caso em tipos diferentes.
    """

    @pytest.mark.parametrize("codigo,tipo", [
        ('nome := "ana"\nout nome.naoExiste()\n', "String"),
        ('xs := [1, 2]\nout xs.naoExiste()\n', "Cluster"),
        ('nome := "ana"\nf := nome.naoExiste\nout f\n', "String"),
    ])
    def test_acusa_antes_de_rodar(self, codigo, tipo):
        ruins = [d for d in diagnosticos(codigo) if d.severity == "error"]
        assert ruins, "passou limpo, e falha em execução"
        assert ruins[0].code == "metodo-embutido"
        assert tipo in ruins[0].message

    def test_sugere_o_nome_parecido(self):
        ruins = [d for d in diagnosticos('nome := "ana"\nout nome.uppper()\n')
                 if d.severity == "error"]
        assert "upper" in ruins[0].hint

    def test_length_continua_valendo(self):
        """Ele não mora na tabela — é tratado à parte no interpretador —,
        e sem essa linha a forma que a própria doc ensina viraria um
        falso alarme."""
        ruins = [d for d in diagnosticos('nome := "ana"\nout nome.length\n')
                 if d.severity == "error"]
        assert not ruins, [d.message for d in ruins]

    def test_o_vault_fica_de_FORA(self):
        """`v.cidade` cai na chave quando ela existe. Acusar exigiria
        saber as chaves, e um vault montado em execução não tem lista."""
        ruins = [d for d in diagnosticos(
            'v := {"a": 1}\nv["b"] := 2\nout v.b\n') if d.severity == "error"]
        assert not ruins, [d.message for d in ruins]

    def test_a_lista_vem_do_INTERPRETADOR_e_nao_de_uma_copia(self):
        """Uma segunda lista divergiria no primeiro método novo — e a
        divergência faria o analisador acusar um método que funciona,
        que é o falso alarme que ensina a desligar a verificação."""
        import inspect

        from dataforge import typechecker as tc
        fonte = inspect.getsource(tc.TypeChecker._metodos_embutidos)
        assert "from .interpreter import" in fonte

        from dataforge.interpreter import _METODOS_DE_TEXTO
        conhecidos = tc.TypeChecker()._metodos_embutidos("String")
        assert set(_METODOS_DE_TEXTO) <= conhecidos
        assert "length" in conhecidos
