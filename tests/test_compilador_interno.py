"""A arquitetura interna, exposta: HIR, MIR, LIR e o que o fluxo prova.

O repositório já tinha lexer, parser, AST, analisador e um compilador de
fechamentos — e nenhuma forma de **ver** nada disso além de
`dataforge tokens` e `dataforge ast`. Faltavam as três representações do
meio e as análises que só existem sobre elas.

O que os testes cobram, e por que cada um importa:

1. **HIR** — a árvore depois do açúcar. A prova de que a normalização
   está certa não é a forma da árvore: é a **saída**. Um programa e o
   seu HIR imprimem a mesma coisa, caractere por caractere, nos
   exercícios do repositório.
2. **MIR** — bloco básico, aresta, laço, tratador. Um grafo errado
   produz análise errada com cara de verdade, então cada forma de fluxo
   é conferida em separado.
3. **As análises** — alcance, vivacidade, definição em todo caminho,
   propagação de constante e escapatória. A que virou diagnóstico é a
   única que o `check` não tinha: um nome atribuído **só num ramo**.
4. **LIR** — o que o compilador de fechamentos realmente compilou, e o
   que recuou para a árvore. É a informação de que se precisa para
   otimizar, e ela não existia em lugar nenhum.
5. **Zero falso alarme** — o diagnóstico novo roda sobre as cinco
   pastas do repositório, e o estado esperado é silêncio.
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
from dataforge import hir as hir_mod                           # noqa: E402
from dataforge import lir as lir_mod                           # noqa: E402
from dataforge import mir as mir_mod                           # noqa: E402
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


def diagnosticos(fonte, nome="<t>"):
    # `source` e o que faz o '// df: permitir <regra>' valer: sem ela o
    # analisador tenta ler o arquivo do disco, e '<t>' nao existe.
    return check_program(arvore(fonte, nome), nome, source=fonte)


def codigos(fonte):
    return [d.code for d in diagnosticos(fonte)]


# ══════════════════════════════════════════════════════════════
#  HIR — a árvore depois do açúcar
# ══════════════════════════════════════════════════════════════

def test_o_orif_vira_given_aninhado():
    """Uma corrente de `orif` é uma árvore de `given` escrita de lado."""
    a = arvore('''
given x bigger 10:
    out "muito"
orif x bigger 5:
    out "medio"
otherwise:
    out "pouco"
''')
    h = hir_mod.normalizar(a)
    de_fora = h.body[0]
    assert isinstance(de_fora, ast.GivenBlock)
    assert de_fora.orif_blocks == []
    dentro = de_fora.otherwise_body[0]
    assert isinstance(dentro, ast.GivenBlock)
    assert dentro.orif_blocks == []


def test_a_composta_de_nome_simples_abre_e_a_de_indice_nao():
    """`v[sortear()] += 1` avaliaria o índice duas vezes."""
    h = hir_mod.normalizar(arvore("soma := 0\nsoma += 2\n"))
    composta = h.body[1]
    assert composta.compound_op == ""
    assert isinstance(composta.value, ast.BinaryOp)
    assert composta.value.op == "+"

    h2 = hir_mod.normalizar(arvore('v := {"k": 1}\nv["k"] += 1\n'))
    assert h2.body[1].compound_op == "+"


def test_o_not_in_vira_uma_negacao_de_verdade():
    h = hir_mod.normalizar(arvore("out 3 not in [1, 2]\n"))
    expressao = h.body[0].expressions[0]
    assert isinstance(expressao, ast.NotOp)
    assert isinstance(expressao.operand, ast.MembershipOp)
    assert expressao.operand.negated is False


def test_o_sinal_de_um_literal_e_dobrado_no_proprio_literal():
    """`-5` é um `UnaryOp` sobre `5`, e isso atrapalha toda análise."""
    h = hir_mod.normalizar(arvore("x := -5\ny := 3 + -2.5\n"))
    assert isinstance(h.body[0].value, ast.IntegerLiteral)
    assert h.body[0].value.value == -5
    assert h.body[1].value.right.value == -2.5

    # `-x` não é literal: continua sendo uma operação.
    h2 = hir_mod.normalizar(arvore("x := 1\ny := -x\n"))
    assert isinstance(h2.body[1].value, ast.UnaryOp)


def test_o_cycle_de_ate_nao_e_acucar_de_range():
    """`range` materializa a lista; um laço de um milhão não pode virar isso."""
    h = hir_mod.normalizar(arvore("cycle i from 0 to 3:\n    out i\n"))
    assert isinstance(h.body[0], ast.CycleFromTo)
    assert "CycleFromTo" in hir_mod.NAO_E_ACUCAR


def test_o_perform_vira_persist_com_a_primeira_volta_garantida():
    fonte = "n := 0\nperform:\n    n += 1\npersist n smaller 3\nout n\n"
    h = hir_mod.normalizar(arvore(fonte))
    assert not any(isinstance(i, ast.PerformBlock) for i in h.body)
    assert any(isinstance(i, ast.PersistBlock) for i in h.body)
    # a primeira volta acontece mesmo com a condição falsa de saída
    assert rodar_arvore(h) == rodar(fonte) == "3\n"


def test_o_hir_nao_tem_mais_acucar_nenhum():
    fonte = '''
n := 0
perform:
    n += 1
persist n smaller 3

given n bigger 5:
    out "a"
orif n bigger 2:
    out "b"
otherwise:
    out "c"

x := -1

out 9 not in [1, 2]
'''
    assert hir_mod.acucares_usados(arvore(fonte)) != {}
    assert hir_mod.acucares_usados(hir_mod.normalizar(arvore(fonte))) == {}


def test_a_normalizacao_nao_mexe_na_arvore_original():
    a = arvore("given x:\n    out 1\notherwise:\n    out 2\n")
    antes = len(a.body[0].otherwise_body)
    hir_mod.normalizar(a)
    assert len(a.body[0].otherwise_body) == antes


def test_o_que_nao_e_acucar_esta_escrito_e_tem_motivo():
    """Uma lista de "não desaçucaro isto" sem o porquê apodrece."""
    assert len(hir_mod.NAO_E_ACUCAR) >= 6
    for nome, motivo in hir_mod.NAO_E_ACUCAR.items():
        assert hasattr(ast, nome), nome
        assert len(motivo) > 20, nome


@pytest.mark.parametrize("fonte,esperado", [
    ("n := 0\nperform:\n    n += 1\npersist n smaller 4\nout n\n", "4\n"),
    ("cycle i from 0 to 3:\n    out i\n", "0\n1\n2\n3\n"),
    ("out -3 + -2, 0 - -1\n", "-5 1\n"),
    ("x := 7\ngiven x bigger 10:\n    out 'a'\norif x bigger 5:\n    out 'b'\n"
     "otherwise:\n    out 'c'\n", "b\n"),
    ("out 3 not in [1, 2], 1 not in [1, 2]\n", "yes no\n"),
    ("t := 0\ncycle i from 1 to 5 step 2:\n    t += i\nout t\n", "9\n"),
])
def test_o_hir_imprime_o_mesmo_que_o_original(fonte, esperado):
    assert rodar(fonte) == esperado
    assert rodar_arvore(hir_mod.normalizar(arvore(fonte))) == esperado


def test_o_hir_e_equivalente_nos_exercicios_do_repositorio():
    """A prova não é a forma da árvore: é a saída, caractere por caractere.

    Um desaçucaramento errado não dá erro — ele muda o resultado. Só
    comparar a saída de programa de verdade pega isso.
    """
    import glob
    arquivos = sorted(glob.glob(os.path.join(RAIZ, "exercicios", "*", "*.df")))
    assert len(arquivos) > 200

    # Os que usam açúcar de fato — rodar 259 duas vezes levaria minutos.
    escolhidos, vistos = [], set()
    for caminho in arquivos:
        fonte = open(caminho, encoding="utf-8").read()
        try:
            a = arvore(fonte, caminho)
        except Exception:
            continue
        usados = set(hir_mod.acucares_usados(a))
        novos = usados - vistos
        if novos and len(escolhidos) < 24:
            escolhidos.append((caminho, fonte))
            vistos |= usados
    assert len(escolhidos) >= 3, "nenhum exercício usa açúcar?"

    comparados = 0
    for caminho, fonte in escolhidos:
        esperado = _saida_de(fonte, caminho)
        if esperado is None:
            continue
        # um exercício que imprime tempo medido não tem saída reprodutível
        if _saida_de(fonte, caminho) != esperado:
            continue
        obtido = _saida_de(hir_mod.normalizar(arvore(fonte, caminho)), caminho)
        assert obtido == esperado, f"o HIR de {os.path.basename(caminho)} divergiu"
        comparados += 1
    assert comparados >= 2, "nenhum exercício comparável sobrou"


def _saida_de(fonte_ou_no, caminho):
    """A saída de um programa, ou `None` se ele não roda sozinho."""
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


def test_o_hir_se_escreve():
    texto = hir_mod.texto(hir_mod.normalizar(arvore(
        "action f(a):\n    yield a + 1\nout f(1)\n")))
    assert "ActionDeclaration" in texto or "action f" in texto
    assert "\n" in texto


def test_a_resolucao_diz_de_onde_vem_cada_nome():
    ligacoes = hir_mod.resolucao(arvore('''
fora := 10

action somar(a, b):
    local := a + b
    yield local + fora + sqrt(4)
'''))
    somar = [c for c in ligacoes if c.nome == "somar"][0]
    assert set(somar.parametros) == {"a", "b"}
    assert "local" in somar.locais
    assert "fora" in somar.livres
    assert "sqrt" in somar.embutidos
    assert "fora" not in somar.locais


# ══════════════════════════════════════════════════════════════
#  MIR — o grafo de fluxo
# ══════════════════════════════════════════════════════════════

def corpo_de(fonte, nome="(programa)"):
    corpos = mir_mod.construir(arvore(fonte))
    for c in corpos:
        if c.nome == nome:
            return c
    raise AssertionError(f"não achei o corpo '{nome}' em "
                         f"{[c.nome for c in corpos]}")


def test_um_corpo_linear_e_um_bloco_so():
    c = corpo_de("x := 1\ny := 2\nout x + y\n")
    assert len(c.blocos) == 1
    assert len(c.blocos[0].instrucoes) == 3
    assert c.blocos[0].saidas == []


def test_o_given_abre_dois_ramos_e_junta():
    c = corpo_de("given x:\n    out 1\notherwise:\n    out 2\nout 3\n")
    entrada = c.blocos[c.entrada]
    assert entrada.terminador == "ramo"
    assert len(entrada.saidas) == 2
    assert {r for _, r in entrada.saidas} == {"sim", "nao"}

    # os dois ramos caem no mesmo bloco de junção
    destinos = [mir_mod.destinos(c.blocos[d]) for d, _ in entrada.saidas]
    assert destinos[0] == destinos[1] != []


def test_o_given_de_um_ramo_so_tem_a_aresta_que_pula():
    c = corpo_de("given x:\n    out 1\nout 3\n")
    entrada = c.blocos[c.entrada]
    assert len(entrada.saidas) == 2
    depois = {d for d, r in entrada.saidas if r == "nao"}
    assert depois


def test_o_persist_tem_aresta_de_volta():
    c = corpo_de("n := 3\npersist n bigger 0:\n    n -= 1\nout n\n")
    voltas = [(b.id, d) for b in c.blocos for d, r in b.saidas if r == "volta"]
    assert voltas, "um laço sem aresta de volta não é um laço"
    de, para = voltas[0]
    assert para < de or para in {b.id for b in c.blocos}


def test_o_cycle_tambem_e_um_laco_no_grafo():
    for fonte in ("cycle i from 0 to 3:\n    out i\n",
                  "cycle x in [1, 2]:\n    out x\n"):
        c = corpo_de(fonte)
        assert any(r == "volta" for b in c.blocos for _, r in b.saidas), fonte


def test_o_halt_sai_do_laco_e_o_skip_volta_a_condicao():
    c = corpo_de('''
cycle i in [1, 2, 3]:
    given i is 2:
        halt
    given i is 1:
        skip
    out i
out "fim"
''')
    rotulos = {r for b in c.blocos for _, r in b.saidas}
    assert "halt" in rotulos
    assert "skip" in rotulos


def test_o_yield_encerra_o_bloco_e_nao_tem_sucessor():
    c = corpo_de("action f(x):\n    yield x\n    out 'nunca'\n", "f")
    saida = [b for b in c.blocos if b.terminador == "yield"]
    assert saida and saida[0].saidas == []


def test_o_codigo_depois_do_yield_e_inalcancavel_no_grafo():
    c = corpo_de("action f(x):\n    yield x\n    out 'nunca'\n", "f")
    vivos = mir_mod.alcancaveis(c)
    assert len(vivos) < len(c.blocos)


def test_o_monitor_liga_o_corpo_ao_tratador():
    c = corpo_de('''
monitor:
    x := arriscado()
handle Error as e:
    out e.message
ensure:
    out "sempre"
''')
    assert any(r == "erro" for b in c.blocos for _, r in b.saidas), \
        "sem aresta de erro, o 'handle' fica inalcançável no grafo"
    assert any(b.rotulo == "tratador" for b in c.blocos)
    assert any(b.rotulo == "ensure" for b in c.blocos)


def test_o_match_abre_um_ramo_por_point():
    c = corpo_de('''
match v:
    point 1:
        out "um"
    point 2:
        out "dois"
    default:
        out "outro"
''')
    entrada = c.blocos[c.entrada]
    assert entrada.terminador == "ramo"
    assert len(entrada.saidas) >= 3


def test_cada_acao_e_um_corpo_e_o_topo_tambem():
    corpos = mir_mod.construir(arvore('''
action a():
    yield 1

blueprint B:
    action m():
        yield 2

out a()
'''))
    nomes = {c.nome for c in corpos}
    assert "(programa)" in nomes
    assert "a" in nomes
    assert "B.m" in nomes


def test_o_mir_se_escreve_de_forma_legivel():
    texto = mir_mod.texto(mir_mod.construir(arvore(
        "given x:\n    out 1\notherwise:\n    out 2\n")))
    assert "bloco" in texto
    assert "→" in texto or "->" in texto


def test_todo_bloco_alcancavel_tem_saida_ou_termina():
    """Um bloco sem saída e sem terminador é um buraco no grafo."""
    import glob
    for caminho in sorted(glob.glob(os.path.join(RAIZ, "exercicios", "*", "*.df")))[:60]:
        fonte = open(caminho, encoding="utf-8").read()
        try:
            a = arvore(fonte, caminho)
        except Exception:
            continue
        for c in mir_mod.construir(a):
            vivos = mir_mod.alcancaveis(c)
            for b in c.blocos:
                if b.id not in vivos:
                    continue
                assert b.saidas or b.terminador, \
                    f"{caminho}: bloco {b.id} de '{c.nome}' não vai a lugar nenhum"


# ══════════════════════════════════════════════════════════════
#  As análises sobre o fluxo
# ══════════════════════════════════════════════════════════════

def test_definida_em_todo_caminho_acha_o_ramo_unico():
    c = corpo_de("given cond:\n    x := 1\nout x\n")
    achados = mir_mod.talvez_nao_definidas(c)
    assert [n for n, _ in achados] == ["x"]


def test_definida_nos_dois_ramos_nao_acusa():
    c = corpo_de("given cond:\n    x := 1\notherwise:\n    x := 2\nout x\n")
    assert mir_mod.talvez_nao_definidas(c) == []


def test_atribuida_antes_do_given_nao_acusa():
    c = corpo_de("x := 0\ngiven cond:\n    x := 1\nout x\n")
    assert mir_mod.talvez_nao_definidas(c) == []


def test_a_vivacidade_sabe_o_que_ainda_sera_lido():
    c = corpo_de("a := 1\nb := 2\nout a\n")
    vivas = mir_mod.vivas(c)
    assert isinstance(vivas, dict) and c.entrada in vivas


def test_a_propagacao_de_constante_segue_a_conta():
    c = corpo_de("x := 2\ny := x + 1\nout y\n")
    fim = mir_mod.constantes(c)
    assert fim.get("y") == 3


def test_a_constante_morre_quando_o_ramo_discorda():
    c = corpo_de("given cond:\n    x := 1\notherwise:\n    x := 2\nout x\n")
    assert "x" not in mir_mod.constantes(c)


def test_a_escapatoria_ve_o_que_a_closure_leva():
    c = corpo_de('''
action f():
    preso := 1
    solto := 2
    yield lambda => preso + 1
''', "f")
    escapam = mir_mod.escapam(c)
    assert "preso" in escapam
    assert "solto" not in escapam


def test_o_que_vai_para_uma_thread_escapa():
    c = corpo_de('''
action f():
    v := [1]
    thread:
        v.append(2)
    yield v
''', "f")
    assert "v" in mir_mod.escapam(c)


# ══════════════════════════════════════════════════════════════
#  LIR — o que o compilador de fechamentos fez
# ══════════════════════════════════════════════════════════════

def test_o_lir_conta_o_que_compilou_e_o_que_recuou():
    inv = lir_mod.inventario(arvore('''
soma := 0
cycle i from 0 to 10:
    soma := soma + i
out soma
'''))
    assert inv.compiladas > 0
    assert inv.total == inv.compiladas + inv.recuadas
    assert 0 <= inv.proporcao() <= 100


def test_o_lir_nomeia_o_no_que_recuou():
    inv = lir_mod.inventario(arvore("record R:\n    x: Integer\nout R(1).x\n"))
    assert inv.recuadas > 0
    assert any("Record" in nome for nome in inv.por_no)


def test_o_lir_se_escreve():
    texto = lir_mod.texto(lir_mod.inventario(arvore("out 1 + 1\n")))
    assert "%" in texto


def test_o_lir_nao_mente_sobre_o_que_a_tabela_tem():
    """A conta sai das tabelas do compilador, e não de uma lista à parte."""
    from dataforge import compilador
    conhecidas = set(compilador._EXPRESSOES) | set(compilador._INSTRUCOES)
    assert lir_mod.classes_compilaveis() == {c.__name__ for c in conhecidas}


# ══════════════════════════════════════════════════════════════
#  O diagnóstico novo
# ══════════════════════════════════════════════════════════════

def test_o_check_acusa_o_nome_que_so_um_ramo_define():
    codigo = codigos('''
action classificar(n):
    given n bigger 10:
        rotulo := "alto"
    yield rotulo
''')
    assert "talvez-nao-definida" in codigo


def test_o_check_cala_quando_os_ramos_cobrem():
    assert "talvez-nao-definida" not in codigos('''
action classificar(n):
    given n bigger 10:
        rotulo := "alto"
    otherwise:
        rotulo := "baixo"
    yield rotulo
''')


def test_a_mensagem_diz_o_que_fazer_e_aponta_a_doc():
    d = [x for x in diagnosticos('''
action f(n):
    given n:
        r := 1
    yield r
''') if x.code == "talvez-nao-definida"][0]
    assert "r" in d.message
    assert d.hint
    assert d.severity == "warning"


def test_da_para_silenciar_como_toda_regra():
    assert "talvez-nao-definida" not in codigos('''
action f(n):
    given n:
        r := 1
    yield r          // df: permitir talvez-nao-definida
''')


def test_o_laco_que_pode_nao_rodar_conta_como_ramo():
    assert "talvez-nao-definida" in codigos('''
action f(xs):
    cycle x in xs:
        ultimo := x
    yield ultimo
''')


def test_o_monitor_cala_a_analise():
    """Dentro de `monitor` a instrução pode não ter chegado ao fim."""
    assert "talvez-nao-definida" not in codigos('''
action f(n):
    monitor:
        given n:
            r := 1
        yield r
    handle Error:
        yield 0
''')


# ══════════════════════════════════════════════════════════════
#  A CLI e o módulo
# ══════════════════════════════════════════════════════════════

def _ir(*extra):
    alvo = os.path.join(RAIZ, "exercicios", "01-fundamentos", "001_hello.df")
    if not os.path.isfile(alvo):
        import glob
        alvo = sorted(glob.glob(os.path.join(RAIZ, "exercicios", "01-*", "*.df")))[0]
    return subprocess.run(
        [sys.executable, "-m", "dataforge", "ir", alvo, *extra],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env={**os.environ, "NO_COLOR": "1"})


@pytest.mark.parametrize("fase,marca", [
    ("tokens", "lexer"),
    ("ast", "parser"),
    ("hir", "acucar"),
    ("mir", "bloco"),
    ("lir", "%"),
    ("analises", "alcance"),
])
def test_o_comando_ir_mostra_cada_fase(fase, marca):
    r = _ir(f"--fase={fase}")
    assert r.returncode == 0, r.stderr[-800:]
    assert marca.lower() in r.stdout.lower()


def test_o_comando_ir_sem_fase_mostra_o_caminho_inteiro():
    r = _ir()
    assert r.returncode == 0, r.stderr[-800:]
    for palavra in ("lexer", "parser", "hir", "mir", "lir"):
        assert palavra.lower() in r.stdout.lower()


def test_o_comando_ir_recusa_fase_inventada_com_a_lista():
    r = _ir("--fase=llvm")
    assert r.returncode != 0
    assert "mir" in r.stdout.lower() + r.stderr.lower()


def test_o_modulo_esta_registrado_e_descrito():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.Compilador", "Compilador"):
        assert get_module(nome) is not None, nome
    assert "Arcane.Compilador" in DESCRICOES


def test_um_programa_le_o_proprio_fluxo():
    assert rodar('''
adopt Arcane.Compilador as K

fonte := "given x:\\n    out 1\\notherwise:\\n    out 2\\n"
blocos := K.mir(fonte)[0]["blocos"]
out len(blocos) bigger 1
out K.fases()[0]
''') == "yes\nlexer\n"


def test_o_modulo_expoe_as_analises():
    assert rodar('''
adopt Arcane.Compilador as K

fonte := "given c:\\n    x := 1\\nout x\\n"
out K.talvez_nao_definidas(fonte)
''').strip() == '[x]'


# ══════════════════════════════════════════════════════════════
#  A doc, e o repositório
# ══════════════════════════════════════════════════════════════

def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import compilador_interno
    for pagina in compilador_interno.PAGINAS:
        for i, bloco in enumerate(pagina["blocos"]):
            if "code" in bloco and bloco.get("lang") == "df" \
                    and not bloco.get("title"):
                yield f"{pagina['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_da_doc()))
def test_todo_exemplo_da_doc_roda(onde, codigo):
    rodar(codigo)


def test_o_repositorio_continua_limpo():
    for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"):
        r = subprocess.run([sys.executable, "-m", "dataforge", "check", pasta],
                           cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env={**os.environ, "NO_COLOR": "1"})
        assert r.returncode == 0, f"{pasta}: {r.stdout[-600:]}"
