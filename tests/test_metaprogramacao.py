"""Metaprogramação: `comptime`, macros sobre a árvore, DSLs e plugins do `check`.

A linguagem já tinha decorador (`mark @nome`), metaclasse e `augment` —
tudo em **execução**. O que faltava é o que acontece **antes** dela
rodar:

1. **`comptime`** — a conta feita uma vez, na carga, e congelada: a
   tabela de consulta gerada, a constante calculada, e a validação que
   falha antes de a primeira linha do programa rodar;
2. **macro** — ler e reescrever a ÁRVORE de uma ação, e gerar código a
   partir dela (o decorador só troca o valor; a macro troca o corpo);
3. **DSL** — combinadores de análise para escrever uma linguagem
   pequena, própria, sem sair daqui;
4. **plugin do `check`** — a regra que o SEU projeto cobra, rodando no
   mesmo comando que as 177 embutidas.

O que os testes cobram, e que o jeito ingênuo erraria:

- `comptime` roda numa caixa: sem `adopt`, sem `out`, sem thread — senão
  "tempo de compilação" seria só "mais cedo";
- a macro é higiênica quando renomeia o que gera, e o teste prova que um
  nome do usuário não é capturado;
- o plugin acusa com linha e coluna, e o `check` sai com código 1.
"""

import io
import json
import os
import subprocess
import sys
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import DataForgeError                  # noqa: E402
from dataforge.interpreter import Interpreter                 # noqa: E402
from dataforge.lexer import tokenize                          # noqa: E402
from dataforge.parser import parse                            # noqa: E402
from dataforge.stdlib import get_module                       # noqa: E402
from dataforge.typechecker import check_program               # noqa: E402


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


# ── comptime ─────────────────────────────────────────────────

def test_comptime_calcula_uma_vez_e_congela():
    assert rodar('''
comptime QUADRADOS := [i * i cycle i in range(0, 6)]
comptime steady MAXIMO := 2 ** 10

out QUADRADOS, MAXIMO, len(QUADRADOS)
''') == "[0, 1, 4, 9, 16, 25] 1024 6"


def test_comptime_roda_antes_do_programa():
    assert rodar('''
ordem := []

action marcar(quem):
    ordem.append(quem)
    yield quem

comptime CEDO := 1
out "o programa comeca aqui", CEDO
''') == "o programa comeca aqui 1"


def test_comptime_em_bloco_com_acao_propria():
    assert rodar('''
comptime:
    action fatorial(n):
        yield 1 given n smaller_eq 1 otherwise n * fatorial(n - 1)

    TABELA := [fatorial(i) cycle i in range(0, 6)]
    LIMITE := TABELA[5]

out TABELA, LIMITE
''') == "[1, 1, 2, 6, 24, 120] 120"


def test_comptime_valida_antes_de_rodar():
    erro = erro_de('''
comptime TABELA := [1, 2]
comptime:
    assert len(TABELA) is 3
out "nao chega aqui"
''')
    assert "comptime" in erro.message.lower() or "Assertion" in erro.message


def test_o_check_acusa_o_comptime_que_falha():
    d = diagnosticos('''
comptime TABELA := [1, 2]
comptime:
    assert len(TABELA) is 3
''', "comptime-falhou")
    assert d and d[0].severity == "error"


def test_comptime_nao_faz_entrada_e_saida():
    erro = erro_de('comptime X := 1\ncomptime:\n    out "oi"\n')
    assert "comptime" in erro.message.lower()
    erro = erro_de('comptime:\n    adopt Arcane.IO as IO\n    X := 1\n')
    assert "comptime" in erro.message.lower()


def test_o_valor_de_comptime_e_constante():
    erro = erro_de('comptime steady N := 3\nN := 4\n')
    assert "steady" in erro.message.lower() or "constant" in erro.message.lower()


def test_comptime_continua_sendo_nome_comum():
    assert rodar('comptime := 3\nout comptime + 1') == "4"
    assert rodar('action comptime(x):\n    yield x\nout comptime(2)') == "2"


# ── macros: ler e reescrever a árvore ────────────────────────

def test_a_arvore_de_uma_acao_e_um_dado():
    assert rodar('''
adopt Arcane.Macro as M

action somar(a, b):
    yield a + b

arvore := M.arvore(somar)
out arvore["tipo"], len(arvore["corpo"]), arvore["parametros"]
out arvore["corpo"][0]["tipo"]
''') == "ActionDeclaration 1 [a, b]\nYieldStatement"


def test_citar_transforma_texto_em_arvore():
    assert rodar('''
adopt Arcane.Macro as M
arvore := M.citar("x * 2 + 1")
out arvore["tipo"], M.texto(arvore)
''') == "BinaryOp x * 2 + 1"


def test_a_macro_reescreve_o_corpo_da_acao():
    assert rodar('''
adopt Arcane.Macro as M

action dobro(x):
    yield x * 2

// troca toda multiplicação por soma: x * 2 vira x + x
action trocar(nodo):
    given nodo["tipo"] is "BinaryOp" and nodo["op"] is "*":
        yield M.citar("x + x")
    yield nodo

trocada := M.reescrever(dobro, trocar)
out dobro(5), trocada(5)
''') == "10 10"


def test_a_macro_gera_uma_acao_nova():
    assert rodar('''
adopt Arcane.Macro as M

corpo := M.citar("a * 10")
gerada := M.acao("dez_vezes", ["a"], corpo)
out gerada(4), M.arvore(gerada)["nome"]
''') == "40 dez_vezes"


def test_a_macro_e_higienica_quando_renomeia():
    assert rodar('''
adopt Arcane.Macro as M

temporario := "do usuario"

corpo := M.citar("temporario + 1")
limpo := M.renomear(corpo, "temporario", M.nome_fresco("temporario"))

out M.texto(limpo) isnt M.texto(corpo), "temporario" in M.texto(limpo)
''') == "yes yes"


def test_a_macro_de_atributo_deriva_metodos():
    assert rodar('''
adopt Arcane.Macro as M

mark @M.derivar("texto", "igualdade")
blueprint Ponto:
    x := 1
    y := 2

a := spawn Ponto()
b := spawn Ponto()
out $"{a}", a is b
''') == "Ponto(x=1, y=2) yes"


def test_percorrer_conta_os_nos():
    assert rodar('''
adopt Arcane.Macro as M

action f(a):
    b := a + 1
    yield b * 2

vistos := []

action anotar(nodo):
    vistos.append(nodo["tipo"])

M.percorrer(M.arvore(f), anotar)
out len(vistos) bigger 5, "BinaryOp" in vistos
''') == "yes yes"


# ── DSL: combinadores de análise ─────────────────────────────

def test_a_dsl_analisa_uma_expressao_propria():
    assert rodar('''
adopt Arcane.Dsl as D

numero := D.mapear(D.numero(), lambda t => cast t as Integer)
soma := D.mapear(D.seq([numero, D.texto("+"), numero]),
                 lambda partes => partes[0] + partes[2])

r := D.analisar(soma, "2+3")
out r.deu_certo(), r.valor()
''') == "yes 5"


def test_a_dsl_diz_onde_o_texto_quebrou():
    assert rodar('''
adopt Arcane.Dsl as D
r := D.analisar(D.numero(), "abc")
out r.falhou(), r.erro()["posicao"], "numero" in r.erro()["esperado"]
''') == "yes 0 yes"


def test_a_dsl_tem_ou_muitos_e_opcional():
    assert rodar('''
adopt Arcane.Dsl as D

palavra := D.ou([D.texto("sim"), D.texto("nao")])
lista := D.muitos(D.seq([palavra, D.opcional(D.texto(","))]))

r := D.analisar(lista, "sim,nao,sim")
out r.deu_certo(), len(r.valor())
''') == "yes 3"


def test_uma_calculadora_em_dez_linhas():
    assert rodar('''
adopt Arcane.Dsl as D

numero := D.mapear(D.numero(), lambda t => cast t as Float)
operador := D.ou([D.texto("+"), D.texto("-"), D.texto("*")])

action aplicar(partes):
    esquerda := partes[0]
    cycle par in partes[1]:
        given par[0] is "+":
            esquerda := esquerda + par[1]
        orif par[0] is "-":
            esquerda := esquerda - par[1]
        otherwise:
            esquerda := esquerda * par[1]
    yield esquerda

expressao := D.mapear(D.seq([numero, D.muitos(D.seq([operador, numero]))]), aplicar)

out D.analisar(expressao, "2+3*4").valor()
out D.analisar(expressao, "10-4").valor()
''') == "20.0\n6.0"


# ── plugins do check ─────────────────────────────────────────

def test_o_plugin_acusa_a_regra_do_projeto(tmp_path):
    (tmp_path / "regras.df").write_text('''
adopt Arcane.Macro as M

action verificar(arvore, arquivo):
    achados := []
    action olhar(nodo):
        given nodo["tipo"] is "Identifier" and len(nodo["nome"]) is 1:
            achados.append({"linha": nodo["linha"], "coluna": nodo["coluna"],
                            "codigo": "sem-nome-curto",
                            "mensagem": "nome de uma letra nao diz nada",
                            "sugestao": "use um nome que se leia"})

    M.percorrer(arvore, olhar)
    yield achados

relay verificar
''', encoding="utf-8")
    (tmp_path / "alvo.df").write_text('x := 1\nout x\n', encoding="utf-8")

    r = subprocess.run([sys.executable, "-m", "dataforge", "check",
                        str(tmp_path / "alvo.df"),
                        f"--plugin={tmp_path / 'regras.df'}"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=RAIZ,
                       env={**os.environ, "NO_COLOR": "1"})
    assert "sem-nome-curto" in r.stdout, r.stdout
    assert "nome de uma letra" in r.stdout
    assert r.returncode == 1


def test_o_plugin_do_forge_toml_roda_sozinho(tmp_path):
    (tmp_path / "forge.toml").write_text(
        '[project]\nname = "exemplo"\nversion = "0.1.0"\n\n'
        '[check]\nplugins = ["regras.df"]\n', encoding="utf-8")
    (tmp_path / "regras.df").write_text('''
action verificar(arvore, arquivo):
    yield [{"linha": 1, "coluna": 1, "codigo": "projeto",
            "mensagem": "a regra do projeto rodou", "severidade": "aviso"}]
relay verificar
''', encoding="utf-8")
    (tmp_path / "alvo.df").write_text('out 1\n', encoding="utf-8")

    r = subprocess.run([sys.executable, "-m", "dataforge", "check", "alvo.df"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(tmp_path),
                       env={**os.environ, "NO_COLOR": "1",
                            "PYTHONPATH": RAIZ})
    assert "a regra do projeto rodou" in r.stdout, r.stdout
    assert r.returncode == 0      # aviso não reprova


def test_um_plugin_quebrado_nao_derruba_o_check(tmp_path):
    (tmp_path / "ruim.df").write_text(
        'action verificar(arvore, arquivo):\n    trigger "quebrei"\nrelay verificar\n',
        encoding="utf-8")
    (tmp_path / "alvo.df").write_text('out 1\n', encoding="utf-8")

    r = subprocess.run([sys.executable, "-m", "dataforge", "check",
                        str(tmp_path / "alvo.df"),
                        f"--plugin={tmp_path / 'ruim.df'}"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=RAIZ,
                       env={**os.environ, "NO_COLOR": "1"})
    assert "plugin" in r.stdout.lower()
    assert "quebrei" in r.stdout
    assert "Traceback" not in r.stdout and "Traceback" not in r.stderr


# ── os módulos ───────────────────────────────────────────────

def test_os_modulos_estao_registrados_e_descritos():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.Macro", "Macro", "Arcane.Dsl", "Dsl"):
        assert get_module(nome) is not None, nome
    for nome in ("Arcane.Macro", "Arcane.Dsl"):
        assert nome in DESCRICOES


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import metaprogramacao
    for pagina in metaprogramacao.PAGINAS:
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
