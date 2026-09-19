"""SSA, propagação condicional e o pipeline de otimização — medido.

A parte 8 de uma referência Deep Tech é sobre backend LLVM, e é a
primeira em que a resposta honesta é em boa medida **não se aplica**: o
DataForge é interpretado, e não há código de máquina. O que transfere:

1. **SSA** — dominância, fronteira de dominância e nó φ. É a
   representação que responde "qual atribuição esta leitura vê?", e é
   ela que torna a propagação de constante **condicional**: um ramo cuja
   condição se prova falsa não é avaliado, e o que ele escreve não
   contamina a junção. Há um teste que prova que isso é *estritamente*
   mais forte que a propagação sobre o MIR.

2. **O pipeline de otimização que existe.** Ele não é o do LLVM: é
   `compilador.py`, e a descida dele é parcial. O inventário do LIR
   aponta onde dói, e esta parte **seguiu o inventário** — com o
   resultado medido, inclusive quando o resultado é "não mudou nada".

3. **Equivalência, sempre pela saída.** Uma otimização errada não
   levanta erro: ela muda o resultado. Cada passe é conferido rodando o
   programa nas duas formas.
"""

import io
import os
import subprocess
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import ast_nodes as ast                         # noqa: E402
from dataforge import mir as mir_mod                           # noqa: E402
from dataforge import otimizar as ot                           # noqa: E402
from dataforge import ssa as ssa_mod                           # noqa: E402
from dataforge.interpreter import Interpreter                  # noqa: E402
from dataforge.lexer import tokenize                           # noqa: E402
from dataforge.parser import parse                             # noqa: E402
from dataforge.stdlib import get_module                        # noqa: E402
from dataforge.typechecker import check_program                # noqa: E402


def arvore(fonte, nome="<t>"):
    return parse(tokenize(fonte, nome), nome)


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(arvore(fonte), "<t>")
    return saida.getvalue()


def rodar_arvore(no):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(no, "<t>")
    return saida.getvalue()


def corpo_de(fonte, nome="(programa)"):
    for c in mir_mod.construir(arvore(fonte)):
        if c.nome == nome:
            return c
    raise AssertionError(f"não achei '{nome}'")


def ssa_de(fonte, nome="(programa)"):
    return ssa_mod.construir(corpo_de(fonte, nome))


def codigos(fonte):
    return [d.code for d in check_program(arvore(fonte), "<t>", source=fonte)]


# ══════════════════════════════════════════════════════════════
#  Dominância
# ══════════════════════════════════════════════════════════════

DIAMANTE = "given c:\n    x := 1\notherwise:\n    x := 2\nout x\n"


def test_a_entrada_domina_todo_bloco_alcancavel():
    corpo = corpo_de(DIAMANTE)
    dom = ssa_mod.dominadores(corpo)
    vivos = mir_mod.alcancaveis(corpo)
    for id_ in vivos:
        assert corpo.entrada in dom[id_], id_


def test_um_ramo_nao_domina_a_juncao():
    """É o que distingue dominância de alcançabilidade."""
    corpo = corpo_de(DIAMANTE)
    dom = ssa_mod.dominadores(corpo)
    juncao = [b for b in corpo.blocos if b.rotulo == "juncao"][0]
    ramos = [b for b in corpo.blocos if b.rotulo in ("sim", "nao")]
    assert len(ramos) == 2
    for ramo in ramos:
        assert ramo.id not in dom[juncao.id]


def test_o_dominador_imediato_e_unico_e_forma_arvore():
    corpo = corpo_de(DIAMANTE)
    idom = ssa_mod.dominador_imediato(corpo)
    assert idom.get(corpo.entrada) is None
    for id_, pai in idom.items():
        if pai is None:
            continue
        assert pai != id_
        # subindo pelos pais chega-se sempre à entrada
        visto, atual = set(), id_
        while atual is not None and atual not in visto:
            visto.add(atual)
            atual = idom.get(atual)
        assert corpo.entrada in visto


def test_a_juncao_esta_na_fronteira_dos_dois_ramos():
    corpo = corpo_de(DIAMANTE)
    fronteira = ssa_mod.fronteira_de_dominancia(corpo)
    juncao = [b for b in corpo.blocos if b.rotulo == "juncao"][0]
    ramos = [b for b in corpo.blocos if b.rotulo in ("sim", "nao")]
    for ramo in ramos:
        assert juncao.id in fronteira[ramo.id]


# ══════════════════════════════════════════════════════════════
#  Nós φ e versões
# ══════════════════════════════════════════════════════════════

def test_dois_ramos_que_escrevem_o_mesmo_nome_geram_um_fi():
    forma = ssa_de(DIAMANTE)
    fis = [(b.id, f) for b in forma.blocos for f in b.fis]
    assert [f.nome for _, f in fis] == ["x"]
    _, fi = fis[0]
    assert len(fi.fontes) == 2


def test_um_nome_com_uma_definicao_so_nao_tem_fi():
    forma = ssa_de("x := 1\nout x\n")
    assert all(not b.fis for b in forma.blocos)


def test_o_laco_tem_fi_na_cabeca():
    """O nome escrito no corpo volta pela aresta de trás: são duas fontes."""
    forma = ssa_de("t := 0\ncycle i in [1, 2]:\n    t := t + i\nout t\n")
    cabecas = [b for b in forma.blocos if b.rotulo == "condicao"]
    assert cabecas, "o laço tem de ter cabeça"
    assert any(f.nome == "t" for b in cabecas for f in b.fis)


def test_a_leitura_ve_a_ultima_escrita():
    forma = ssa_de("x := 1\nx := 2\nout x\n")
    # a versão lida pelo 'out' é a criada pela segunda atribuição
    escritas = [i.escreve[1] for b in forma.blocos for i in b.instrucoes
                if i.escreve and i.escreve[0] == "x"]
    lidas = [i.le["x"] for b in forma.blocos for i in b.instrucoes
             if "x" in i.le]
    assert escritas == [1, 2]
    assert lidas == [2]


def test_cada_versao_tem_exatamente_uma_definicao():
    """É a propriedade que define SSA, e a que faz a análise valer."""
    for fonte in (DIAMANTE,
                  "t := 0\ncycle i in [1, 2]:\n    t := t + i\nout t\n",
                  "given a:\n    y := 1\nout y\n"):
        forma = ssa_de(fonte)
        vistas = []
        for b in forma.blocos:
            vistas += [(f.nome, f.versao) for f in b.fis]
            vistas += [i.escreve for i in b.instrucoes if i.escreve]
        assert len(vistas) == len(set(vistas)), fonte


def test_a_definicao_de_uma_versao_se_encontra():
    forma = ssa_de(DIAMANTE)
    fi = [f for b in forma.blocos for f in b.fis][0]
    for _bloco, versao in fi.fontes.items():
        onde = ssa_mod.definicao_de(forma, "x", versao)
        assert onde is not None


def test_o_ssa_se_escreve_com_os_fis():
    texto = ssa_mod.texto(ssa_de(DIAMANTE))
    assert "φ" in texto or "fi " in texto
    assert "x" in texto


# ══════════════════════════════════════════════════════════════
#  Propagação condicional — e por que ela é mais forte
# ══════════════════════════════════════════════════════════════

MORTO = '''x := 1
given x bigger 5:
    y := "nunca"
otherwise:
    y := "sempre"
out y
'''


def test_a_propagacao_sobre_o_mir_nao_conclui_o_y():
    """A de referência junta os dois ramos e perde — e está certa em perder."""
    assert "y" not in mir_mod.constantes(corpo_de(MORTO))


def test_a_condicional_sobre_ssa_conclui_o_y():
    """Ela **não avalia** o ramo que não roda, e por isso conclui."""
    fixas, mortos = ssa_mod.constantes_condicionais(ssa_de(MORTO))
    assert fixas.get(("y", 1)) == "sempre" or "sempre" in fixas.values()
    assert mortos, "o ramo que nunca roda tem de aparecer"


def test_o_ramo_que_nunca_roda_e_nomeado():
    forma = ssa_de(MORTO)
    _fixas, mortos = ssa_mod.constantes_condicionais(forma)
    rotulos = {forma.bloco(i).rotulo for i in mortos}
    assert "sim" in rotulos


def test_uma_condicao_que_nao_se_prova_nao_mata_nada():
    forma = ssa_de("given entrada:\n    y := 1\notherwise:\n    y := 2\nout y\n")
    _fixas, mortos = ssa_mod.constantes_condicionais(forma)
    assert mortos == set()


def test_o_persist_yes_nao_e_acusado_de_nada():
    """`persist yes:` com `halt` é o laço infinito legítimo."""
    forma = ssa_de("n := 0\npersist yes:\n    n += 1\n    given n bigger 2:\n"
                   "        halt\nout n\n")
    _fixas, mortos = ssa_mod.constantes_condicionais(forma)
    rotulos = {forma.bloco(i).rotulo for i in mortos}
    assert "corpo" not in rotulos


# ══════════════════════════════════════════════════════════════
#  O pipeline de otimização
# ══════════════════════════════════════════════════════════════

def test_os_passes_estao_nomeados_e_descritos():
    assert len(ot.PASSES) >= 3
    for nome, descricao in ot.PASSES.items():
        assert len(descricao) > 25, nome


def test_a_dobra_de_constante_acontece():
    antes = arvore("x := 2 + 3 * 4\nout x\n")
    depois, relatorio = ot.otimizar(antes)
    assert relatorio["dobra-de-constante"] >= 1
    assert isinstance(depois.body[0].value, ast.IntegerLiteral)
    assert depois.body[0].value.value == 14


def test_a_dobra_nao_inventa_conta_que_pode_falhar():
    """`1 / 0` dobrado viraria erro na CARGA, e não na linha que o causa."""
    depois, _r = ot.otimizar(arvore("x := 1 / 0\nout x\n"))
    assert isinstance(depois.body[0].value, ast.BinaryOp)


def test_a_dobra_nao_mistura_texto_com_numero():
    depois, _r = ot.otimizar(arvore('x := "a" + 1\nout x\n'))
    assert isinstance(depois.body[0].value, ast.BinaryOp)


def test_o_ramo_morto_sai():
    depois, relatorio = ot.otimizar(arvore(MORTO))
    assert relatorio["ramo-morto"] >= 1
    assert rodar_arvore(depois) == "sempre\n"


def test_o_que_vem_depois_de_um_yield_sai():
    fonte = "action f():\n    yield 1\n    out 'nunca'\nout f()\n"
    depois, relatorio = ot.otimizar(arvore(fonte))
    assert relatorio["inalcancavel"] >= 1
    assert rodar_arvore(depois) == "1\n"


def test_o_relatorio_conta_por_passe():
    _depois, relatorio = ot.otimizar(arvore(
        "x := 1 + 1\ngiven no:\n    out 'nunca'\notherwise:\n    out 'sim'\n"))
    assert set(relatorio) <= set(ot.PASSES)
    assert sum(relatorio.values()) >= 2


@pytest.mark.parametrize("fonte,esperado", [
    ("x := 2 + 3\nout x\n", "5\n"),
    (MORTO, "sempre\n"),
    ("out 10 ~/ 3, 2 ** 8, -4 + 1\n", "3 256 -3\n"),
    ("t := 0\ncycle i from 1 to 4:\n    t += i * 2\nout t\n", "20\n"),
    ("given yes:\n    out 'a'\notherwise:\n    out 'b'\n", "a\n"),
    ("action f(n):\n    given n bigger 0:\n        yield 'mais'\n"
     "    yield 'menos'\nout f(1), f(-1)\n", "mais menos\n"),
])
def test_o_programa_otimizado_imprime_o_mesmo(fonte, esperado):
    assert rodar(fonte) == esperado
    depois, _r = ot.otimizar(arvore(fonte))
    assert rodar_arvore(depois) == esperado


def test_otimizar_nao_mexe_na_arvore_original():
    a = arvore("x := 1 + 1\nout x\n")
    ot.otimizar(a)
    assert isinstance(a.body[0].value, ast.BinaryOp)


def test_a_otimizacao_e_equivalente_nos_exercicios_do_repositorio():
    """A prova é a saída, como no HIR. Uma otimização errada não avisa."""
    import glob
    escolhidos = []
    for caminho in sorted(glob.glob(os.path.join(RAIZ, "exercicios",
                                                 "*", "*.df"))):
        fonte = open(caminho, encoding="utf-8").read()
        try:
            a = arvore(fonte, caminho)
        except Exception:
            continue
        _depois, relatorio = ot.otimizar(a)
        if sum(relatorio.values()) and len(escolhidos) < 30:
            escolhidos.append((caminho, fonte))
    assert len(escolhidos) >= 5, "nenhum exercício é otimizável?"

    comparados = 0
    for caminho, fonte in escolhidos:
        esperado = _saida_de(fonte, caminho)
        if esperado is None:
            continue
        # Um exercicio que imprime TEMPO MEDIDO nao tem saida reprodutivel,
        # e comparar byte a byte ali reprovaria a cada execucao por um
        # motivo que nada tem a ver com a otimizacao. A pergunta certa e
        # "este programa da a mesma saida duas vezes?", e ela e feita
        # antes de a otimizacao entrar na conta.
        if _saida_de(fonte, caminho) != esperado:
            continue
        otimizada, _r = ot.otimizar(arvore(fonte, caminho))
        assert _saida_de(otimizada, caminho) == esperado, \
            f"a otimização de {os.path.basename(caminho)} mudou a saída"
        comparados += 1
    assert comparados >= 4, "nenhum exercício comparável sobrou"


def _saida_de(fonte_ou_no, caminho):
    saida = io.StringIO()
    anterior = os.getcwd()
    os.chdir(os.path.dirname(caminho))
    try:
        no = fonte_ou_no if not isinstance(fonte_ou_no, str) \
            else parse(tokenize(fonte_ou_no, caminho), caminho)
        with redirect_stdout(saida):
            Interpreter().run(no, caminho)
    except BaseException:
        return None
    finally:
        os.chdir(anterior)
    return saida.getvalue()


# ══════════════════════════════════════════════════════════════
#  O que o backend REALMENTE compila
# ══════════════════════════════════════════════════════════════

def test_os_nos_que_o_inventario_apontou_agora_compilam():
    """A lista não foi escolhida por intuição: saiu do `dataforge ir --fase=lir`."""
    from dataforge import lir
    compilaveis = lir.classes_compilaveis()
    for classe in ("UnaryOp", "MembershipOp", "TernaryExpression",
                   "CoalesceOp", "TypeofExpression", "SliceAccess",
                   "SteadyDeclaration", "AssertStatement",
                   "HaltStatement", "SkipStatement"):
        assert classe in compilaveis, classe


def test_a_compilacao_nova_nao_muda_a_saida():
    """O que o compilador faz tem de ser o que o interpretador faria."""
    fonte = '''steady L := 3
v := {"a": 0}
xs := [1, 2, 3, 4, 5]
soma := 0
cycle i from 1 to L:
    r := "par" given i % 2 is 0 otherwise "impar"
    v[r] := (v[r] ?? 0) + 1
    given i in xs:
        soma += -i
    soma += len(xs[1:3])
    assert typeof(r) is "String"
    given i is 2:
        skip
out v["par"], v["impar"], soma
'''
    esperado = rodar(fonte)
    assert esperado.strip()
    interp = Interpreter()
    interp.compilar_corpos = False
    saida = io.StringIO()
    with redirect_stdout(saida):
        interp.run(arvore(fonte), "<t>")
    assert saida.getvalue() == esperado


def test_a_compilacao_por_indice_avalia_o_alvo_uma_vez_so():
    """`v[sortear()] := x` não pode consumir dois sorteios."""
    assert rodar('''
vezes := 0
action chave():
    vezes += 1
    yield "k"

v := {"k": 0}
cycle i from 1 to 3:
    v[chave()] := i
out v["k"], vezes
''') == "3 3\n"


# ══════════════════════════════════════════════════════════════
#  O diagnóstico novo
# ══════════════════════════════════════════════════════════════

def test_o_check_acusa_o_ramo_que_nunca_roda():
    assert "ramo-morto" in codigos('''
action f():
    limite := 5
    given limite bigger 10:
        yield "alto"
    yield "baixo"
''')


def test_a_condicao_que_depende_de_fora_nao_e_acusada():
    assert "ramo-morto" not in codigos('''
action f(limite):
    given limite bigger 10:
        yield "alto"
    yield "baixo"
''')


def test_da_para_silenciar_o_ramo_morto():
    assert "ramo-morto" not in codigos('''
action f():
    limite := 5
    given limite bigger 10:      // df: permitir ramo-morto
        yield "alto"
    yield "baixo"
''')


def test_o_repositorio_nao_ganha_falso_alarme():
    for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"):
        r = subprocess.run([sys.executable, "-m", "dataforge", "check", pasta],
                           cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env={**os.environ, "NO_COLOR": "1"})
        assert r.returncode == 0, f"{pasta}: {r.stdout[-600:]}"


# ══════════════════════════════════════════════════════════════
#  A CLI, o módulo e a doc
# ══════════════════════════════════════════════════════════════

def _ir(*extra):
    import glob
    alvo = sorted(glob.glob(os.path.join(RAIZ, "exercicios", "02-*", "*.df")))[0]
    return subprocess.run(
        [sys.executable, "-m", "dataforge", "ir", alvo, *extra],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env={**os.environ, "NO_COLOR": "1"})


@pytest.mark.parametrize("fase,marca", [
    ("ssa", "bloco"),
    ("otimizado", "passe"),
])
def test_as_fases_novas_aparecem_no_comando(fase, marca):
    r = _ir(f"--fase={fase}")
    assert r.returncode == 0, r.stderr[-800:]
    assert marca.lower() in r.stdout.lower()


def test_o_modulo_expoe_ssa_e_otimizacao():
    assert rodar('''
adopt Arcane.Compilador as K

fonte := "given c:\\n    x := 1\\notherwise:\\n    x := 2\\nout x\\n"
forma := K.ssa(fonte)[0]
out len([f cycle b in forma["blocos"] cycle f in b["fis"]])

morto := "x := 1\\ngiven x bigger 5:\\n    out 1\\notherwise:\\n    out 2\\n"
out len(K.ramos_mortos(morto)) bigger 0
out K.otimizar("y := 2 + 3\\n")["dobra-de-constante"]
''') == "1\nyes\n1\n"


def test_o_ssa_esta_na_lista_de_fases():
    assert rodar('adopt Arcane.Compilador as K\nout "ssa" in K.fases()\n') \
        == "yes\n"


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import compilador_backend
    for pagina in compilador_backend.PAGINAS:
        for i, bloco in enumerate(pagina["blocos"]):
            if "code" in bloco and bloco.get("lang") == "df" \
                    and not bloco.get("title"):
                yield f"{pagina['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_da_doc()))
def test_todo_exemplo_da_doc_roda(onde, codigo):
    rodar(codigo)
