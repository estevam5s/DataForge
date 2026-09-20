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


# ── A anotação genérica de um blueprint próprio ──────────────
#
# Era ERRO DE SINTAXE, e três defeitos moravam atrás disso:
#
# 1. `parse_blueprint` não registrava os parâmetros de tipo. `type`,
#    `record`, `enum` e `trait` registram; o blueprint lia os dele e
#    jogava fora. Dava uma assimetria sem explicação —
#    `Par<Integer, String>` num record anotava, e `Caixa<Integer>` num
#    blueprint respondia "não é um tipo de coleção", sugerindo escrever
#    `type Caixa<T> := …`, que é o caminho errado.
#
# 2. O ramo de blueprint da conferência era CÓDIGO MORTO: ele lia
#    `alvo.tipos_dos_campos`, atributo que nunca existiu. `getattr` com
#    padrão devolvia `{}` e o laço não conferia nada.
#
# 3. Escrever o argumento de tipo DESLIGAVA a conferência de membro —
#    escrever MAIS informação de tipo comprava MENOS verificação.

GUARDA = """blueprint Guarda<T>(valor: T):
    action guardar(v: T):
        self.valor := v
    action ler() -> T:
        yield self.valor
"""


def test_a_anotacao_generica_de_blueprint_e_aceita():
    """O runtime já estava pronto; faltava poder ESCREVER a anotação."""
    assert rodar(GUARDA + "c: Guarda<Integer> := spawn Guarda(7)\n"
                          "out c.ler()\n") == "7"


def test_record_e_blueprint_respondem_IGUAL_a_mesma_forma():
    """A assimetria era o defeito: mesma forma, respostas diferentes."""
    assert rodar("""record Par<A, B>:
    um: A
    dois: B

p: Par<Integer, String> := Par(1, "a")
out p.um
""") == "1"
    assert rodar(GUARDA + "c: Guarda<Integer> := spawn Guarda(1)\n"
                          "out c.ler()\n") == "1"


def test_a_aridade_do_generico_de_blueprint_e_cobrada():
    e = erro_de(GUARDA + "c: Guarda<Integer, String> := spawn Guarda(1)\n")
    assert "takes one type" in e.message


def test_um_blueprint_sem_generico_continua_recusando_a_anotacao():
    """A mensagem que já existia não pode ter sido perdida."""
    e = erro_de("blueprint Simples:\n"
                "    action f():\n"
                "        yield 1\n"
                "c: Simples<Integer> := spawn Simples()\n")
    assert "not a collection type" in e.message


# ── O ramo que era código morto ──────────────────────────────

def test_o_conteudo_errado_e_recusado_na_fronteira():
    e = erro_de(GUARDA + 'c: Guarda<Integer> := spawn Guarda("texto")\n')
    assert "field 'valor' of Guarda<Integer>" in e.message
    assert "declared as Integer but got String" in e.message


def test_o_campo_do_CORPO_tambem_conta():
    e = erro_de("""blueprint Guarda<T>:
    guardado: T

c := spawn Guarda()
c.guardado := "texto"
d: Guarda<Integer> := c
""")
    assert "field 'guardado'" in e.message


def test_o_campo_HERDADO_tambem_conta():
    """Um campo herdado é tão declarado quanto um próprio — e a mãe é
    quem costuma declarar o genérico."""
    e = erro_de("""blueprint Raiz<T>:
    do_pai: T

blueprint Guarda<T> extends Raiz:
    proprio: T

c := spawn Guarda()
c.do_pai := "texto"
d: Guarda<Integer> := c
""")
    assert "field 'do_pai'" in e.message


def test_a_filha_vence_a_mae_no_tipo_do_campo():
    """A primeira versão empilhava, e a mãe sobrescrevia a filha.

    O `campo: T` da filha virava o `campo: String` da mãe, e a
    conferência passava a falar do tipo errado.
    """
    interp = Interpreter()
    interp.run(parse(tokenize(
        "blueprint Raiz<T>:\n"
        "    campo: String\n"
        "blueprint Filha<T> extends Raiz:\n"
        "    campo: T\n", "<t>"), "<t>"))
    tipos = Interpreter._tipos_de_campo_do_molde(
        interp.global_env.get("Filha"))
    assert tipos["campo"] == "T", tipos


def test_campo_AINDA_SEM_VALOR_nao_da_falso_alarme():
    """`spawn Guarda()` deixa os campos em `void`.

    A primeira versão acusava "declared as Integer but got Void" em TODO
    blueprint genérico anotado: o recurso inteiro ficava inutilizável, e
    o falso alarme era no caminho mais comum que existe.
    """
    assert rodar("""blueprint Guarda<T>:
    guardado: T

c: Guarda<Integer> := spawn Guarda()
c.guardado := 7
out c.guardado
""") == "7"


def test_o_record_continua_cobrado_como_antes():
    """A mudança não pode ter mexido no caminho que já funcionava."""
    e = erro_de("""record Par<A, B>:
    um: A
    dois: B

p: Par<Integer, String> := Par("texto", 99)
""")
    assert "field 'um' of Par<Integer, String>" in e.message


# ── O silêncio: o argumento de tipo desligava a conferência ──

def test_o_argumento_de_tipo_nao_desliga_a_conferencia_de_metodo():
    """Escrever MAIS tipo não pode comprar MENOS verificação."""
    com = erros(GUARDA + "c: Guarda<Integer> := spawn Guarda(1)\n"
                         "out c.naoExiste()\n")
    sem = erros(GUARDA + "c: Guarda := spawn Guarda(1)\n"
                         "out c.naoExiste()\n")
    assert len(com) == len(sem) == 1, (com, sem)


def test_o_argumento_de_tipo_nao_desliga_a_conferencia_em_record():
    """O defeito já existia aqui, desde que record aceitou a anotação."""
    base = "record Par<A, B>:\n    um: A\n    dois: B\n\n"
    com = erros(base + 'p: Par<Integer, String> := Par(1, "a")\n'
                       "out p.naoExiste\n")
    sem = erros(base + 'p: Par := Par(1, "a")\n'
                       "out p.naoExiste\n")
    assert len(com) == len(sem) == 1, (com, sem)


def test_o_campo_certo_continua_passando():
    """A correção não pode acusar o que existe."""
    assert not erros("""record Par<A, B>:
    um: A
    dois: B

p: Par<Integer, String> := Par(1, "a")
out p.um
""")


# ── O `check` acusa a linha que CAUSA ───────────────────────

def test_o_check_acusa_o_argumento_generico_na_causa():
    """O erro existia, e aparecia uma linha depois, sobre outro nome.

    Em execução o parâmetro de um `T` sem limite não é conferido: o campo
    recebia o texto calado, e a queixa saía na leitura seguinte — *"a
    variável 'n' declared as Integer but got String"*. Quem lê vai
    depurar o `n`, que está certo.
    """
    fonte = (GUARDA + "c: Guarda<Integer> := spawn Guarda(1)\n"
                      'c.guardar("texto")\n')
    achados = diagnosticos(fonte, "generic-argument")
    assert len(achados) == 1, erros(fonte)
    assert achados[0].line == 7, f"acusou a linha {achados[0].line}, não a 7"
    assert "T is Integer" in achados[0].message
    assert "got String" in achados[0].message


def test_o_check_CALA_sem_a_anotacao():
    """Sem anotação não há vínculo, e concluir seria inventar."""
    assert not diagnosticos(
        GUARDA + 'c := spawn Guarda(1)\nc.guardar("texto")\n',
        "generic-argument")


def test_o_check_deixa_passar_o_argumento_certo():
    assert not diagnosticos(
        GUARDA + "c: Guarda<Integer> := spawn Guarda(1)\nc.guardar(2)\n",
        "generic-argument")


def test_o_limite_continua_cobrado_em_execucao_no_blueprint():
    e = erro_de("""blueprint Medida<T extends Number>(quanto: T):
    action dobro() -> T:
        yield self.quanto * 2

m: Medida<Integer> := spawn Medida("texto")
""")
    assert "extends Number" in e.message


# ── Variância: a decisão, medida ────────────────────────────

def test_a_covariancia_sai_de_graca_da_conferencia_estrutural():
    """`Guarda<Integer>` serve onde se espera `Guarda<Number>`.

    E isso não vem de uma declaração de variância: vem de a conferência
    olhar os VALORES reais na fronteira. Um Integer é um Number.
    """
    assert rodar(GUARDA + "inteira: Guarda<Integer> := spawn Guarda(7)\n"
                          "larga: Guarda<Number> := inteira\n"
                          "out larga.ler()\n") == "7"


def test_e_o_incompativel_e_recusado_sem_variancia_declarada():
    """O outro lado da mesma conferência — e é o que a torna sólida."""
    e = erro_de(GUARDA + "inteira: Guarda<Integer> := spawn Guarda(7)\n"
                         "errada: Guarda<String> := inteira\n")
    assert "declared as String but got Integer" in e.message


def test_nao_ha_palavra_de_variancia_na_linguagem():
    """E não deve haver: ela não teria o que decidir.

    A conferência é estrutural na fronteira, então a resposta de
    assignability já está certa sem ela — provado pelos dois testes
    acima. `covariant`/`contravariant` seriam a oitava e a nona palavra
    reservada removida por serem caras sem entregar nada.
    """
    from dataforge import tokens

    for palavra in ("covariant", "contravariant", "covariante",
                    "contravariante"):
        assert palavra not in tokens.KEYWORDS


def test_a_regra_nova_pode_ser_silenciada_pelo_nome():
    """Um analisador sem escape obriga a escolher entre conviver com um
    alarme e desligar a verificação inteira — e a segunda é o que
    acontece. A regra tem nome, então o escape vem de graça."""
    fonte = (GUARDA + "c: Guarda<Integer> := spawn Guarda(1)\n"
                      'c.guardar("texto")  // df: permitir generic-argument\n')
    # `source=` e como o LSP passa o texto do editor: sem ela o
    # verificador leria o arquivo do DISCO, e aqui nao ha arquivo.
    todos = check_program(parse(tokenize(fonte, "t.df"), "t.df"), "t.df",
                          source=fonte)
    assert not [d for d in todos if d.code == "generic-argument"]

    # E sem o comentario ela continua acusando — senao o teste acima
    # passaria por acidente.
    sem = fonte.replace("  // df: permitir generic-argument", "")
    todos = check_program(parse(tokenize(sem, "t.df"), "t.df"), "t.df",
                          source=sem)
    assert [d for d in todos if d.code == "generic-argument"]


# ═══════════════════════════════════════════════════════════
#  O vínculo do objeto, cobrado ANTES de rodar
# ═══════════════════════════════════════════════════════════

def test_o_check_acusa_o_campo_generico_na_linha_que_causa():
    """`c.guardado := "texto"` num `Caixa<Integer>`.

    A execução já recusava isto desde que a instância passou a carregar
    o vínculo. O que faltava era o `check` dizer o mesmo **antes** — a
    diferença entre descobrir num teste e descobrir no dia em que
    aquele ramo roda.
    """
    achados = diagnosticos('''blueprint Caixa<T>:
    guardado: T

c: Caixa<Integer> := spawn Caixa()
c.guardado := "texto"
''')
    codigos = [d.code for d in achados]
    assert "generic-field" in codigos, [str(d) for d in achados]

    acusado = [d for d in achados if d.code == "generic-field"][0]
    # A linha é a da ATRIBUIÇÃO, e não a da leitura seguinte: era
    # exatamente isso que a mensagem de execução não conseguia dar.
    assert acusado.line == 5, acusado.line
    assert "Integer" in acusado.message and "String" in acusado.message


def test_o_check_e_a_EXECUCAO_dao_a_mesma_resposta_no_campo_herdado():
    """Duas respostas para a mesma pergunta é o pior resultado possível.

    O campo genérico declarado na mãe vale na filha, e as duas metades
    — o analisador e o interpretador — precisam concordar sobre isso.
    Elas leem tabelas diferentes (`tipos_de_campo` de um lado,
    `tipos_do_cabecalho`/`fields_decl` do outro), então a concordância
    é uma coisa a provar, não a supor.
    """
    fonte = '''blueprint Caixa<T>:
    guardado: T

blueprint CaixaForte<T> extends Caixa:
    action selar():
        yield yes

f: CaixaForte<Integer> := spawn CaixaForte()
f.guardado := "texto"
'''
    acusados = diagnosticos(fonte, "generic-field")
    assert acusados, "o check calou sobre o campo herdado"

    with pytest.raises(DataForgeError) as execucao:
        rodar(fonte)
    assert "CaixaForte<Integer>" in str(execucao.value)
    assert "Integer" in str(execucao.value) and "String" in str(execucao.value)


@pytest.mark.parametrize("fonte,porque", [
    ('''blueprint Caixa<T>:
    guardado: T

solta := spawn Caixa()
solta.guardado := "texto"
''', "sem anotação não há vínculo — é assim que a maioria do código cria instância"),
    ('''blueprint Caixa<T>:
    guardado: T

c: Caixa<String> := spawn Caixa()
c.guardado := "texto"
''', "o código certo não pode ser acusado"),
    ('''blueprint Saco<T>:
    itens: Cluster<T>

s: Saco<Integer> := spawn Saco()
s.itens := ["a"]
''', "o campo não é um parâmetro puro: descer na coleção seria impreciso"),
])
def test_o_check_do_campo_generico_CALA_quando_nao_prova(fonte, porque):
    """Um falso alarme ensina a desligar a verificação inteira."""
    acusados = diagnosticos(fonte, "generic-field")
    assert not acusados, f"{porque}: {[str(d) for d in acusados]}"
