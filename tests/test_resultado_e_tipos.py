"""`Arcane.Resultado` e `Arcane.Tipos`: a falha como valor, e a reflexão.

A linguagem tinha duas formas de lidar com o que dá errado —
`monitor`/`handle` para o erro que interrompe, `void` com `??` para a
ausência — e não tinha a terceira, que é a que uma fronteira pede:
**devolver** a falha. E tinha `typeof`, que responde um nome, sem nada
que responda "este tipo é união? refinamento? qual é a regra?".

O que os testes cobram:

1. `ok`/`falha` atravessam `mapear`, `entao` e `ou` sem levantar — ler
   `valor()` de uma falha levanta, porque ali quem escreveu afirmou;
2. `tentar` captura o erro da LINGUAGEM e deixa passar sinal de
   controle: um `halt` dentro dele tem de sair do laço;
3. `Talvez` distingue "não tem a chave" de "tem, e vale void" — o que
   `??` não faz, e é a dúvida de todo vault de configuração;
4. `Tipos.satisfaz` responde sem levantar, e a base vem antes da regra;
5. `Tipos.forma` é ESTRUTURAL (`Cluster<Integer>`), e não o `typeof`.
"""

import io
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


def erros(fonte):
    todos = check_program(parse(tokenize(fonte, "t.df"), "t.df"), "t.df")
    return [d for d in todos if d.severity == "error"]


# ── Resultado ────────────────────────────────────────────────

def test_ok_e_falha_sao_valores():
    assert rodar('''
adopt Arcane.Resultado as R
bom := R.ok(3)
ruim := R.falha("nao achei", 404)
out bom.deu_certo(), bom.valor(), bom.ou(0)
out ruim.falhou(), ruim.erro(), ruim.detalhe(), ruim.ou(0)
out bom, ruim
''') == "yes 3 3\nyes nao achei 404 0\nok(3) falha('nao achei')"


def test_a_falha_atravessa_mapear_e_entao():
    assert rodar('''
adopt Arcane.Resultado as R

action dobro(x):
    yield R.ok(x * 2)

out R.ok(2).mapear(lambda x => x + 1).valor()
out R.ok(2).entao(dobro).valor()
out R.falha("parou").mapear(lambda x => x + 1).erro()
out R.falha("parou").entao(dobro).erro()
out R.falha("parou").recuperar(lambda motivo => R.ok(0)).valor()
''') == "3\n4\nparou\nparou\n0"


def test_ler_o_valor_de_uma_falha_levanta_e_ou_nunca():
    erro = erro_de('adopt Arcane.Resultado as R\nR.falha("x").valor()\n')
    assert "failed" in erro.message.lower() or "falh" in erro.message.lower()
    assert rodar('adopt Arcane.Resultado as R\nout R.falha("x").ou("padrao")') == "padrao"
    erro = erro_de('adopt Arcane.Resultado as R\n'
                   'R.falha("x").exigir("o cliente nao existe")\n')
    assert "o cliente nao existe" in erro.message


def test_tentar_captura_o_erro_da_linguagem():
    assert rodar('''
adopt Arcane.Resultado as R

action dividir(a, b):
    yield a / b

bom := R.tentar(dividir, 10, 2)
ruim := R.tentar(dividir, 1, 0)
out bom.valor(), ruim.falhou(), "zero" in ruim.erro()
''') == "5.0 yes yes"


def test_tentar_nao_engole_sinal_de_controle():
    """Um 'halt' dentro do 'tentar' tem de sair do laço, e não virar falha."""
    assert rodar('''
adopt Arcane.Resultado as R

voltas := 0
cycle i from 1 to 10:
    voltas += 1
    given i is 3:
        halt
out voltas
''') == "3"


def test_todos_junta_ou_para_na_primeira_falha():
    assert rodar('''
adopt Arcane.Resultado as R
out R.todos([R.ok(1), R.ok(2), R.ok(3)]).valor()
out R.todos([R.ok(1), R.falha("cpf invalido"), R.falha("email")]).erro()
out R.erros([R.ok(1), R.falha("a"), R.falha("b")])
''') == '[1, 2, 3]\ncpf invalido\n[a, b]'


def test_o_resultado_numa_fronteira_de_verdade():
    assert rodar('''
adopt Arcane.Resultado as R

action buscar(id) -> Resultado:
    given id smaller 0:
        yield R.falha("id negativo")
    yield R.ok({"id": id, "nome": "Ana"})

achado := buscar(7)
perdido := buscar(-1)

given achado.deu_certo():
    out achado.valor()["nome"]
given perdido.falhou():
    out perdido.erro()
''') == "Ana\nid negativo"


# ── Talvez ───────────────────────────────────────────────────

def test_talvez_distingue_nao_tem_de_vale_void():
    assert rodar('''
adopt Arcane.Resultado as R
config := {"tema": void}
tem := R.chave(config, "tema")
nao := R.chave(config, "idioma")
out tem.tem(), tem.valor(), nao.tem(), nao.ou("pt-BR")
''') == "yes void no pt-BR"


def test_talvez_mapeia_filtra_e_vira_resultado():
    assert rodar('''
adopt Arcane.Resultado as R
out R.algo(2).mapear(lambda x => x * 5).valor()
out R.nada().mapear(lambda x => x * 5).ou("nada")
out R.algo(4).filtrar(lambda x => x bigger 10).tem()
out R.primeiro([1, 2, 3], lambda x => x bigger 2).valor()
out R.primeiro([1, 2], lambda x => x bigger 9).tem()
out R.nada().para_resultado("vazio").erro()
''') == "10\nnada\nno\n3\nno\nvazio"


# ── Arcane.Tipos ─────────────────────────────────────────────

def test_os_metadados_de_um_tipo_declarado():
    assert rodar('''
adopt Arcane.Tipos as T
type Id := Integer
type Json := String | Integer
type Positivo := Integer where valor bigger 0
opaque type Cpf := String where len(valor) is 11

out T.de("Id")["especie"], T.de("Json")["especie"]
out T.de("Positivo")["especie"], T.de("Positivo")["regra"]
out T.de("Cpf")["opaco"], T.de("Json")["partes"]
out T.existe("Id"), T.existe("NaoExiste"), len(T.declarados())
''') == 'alias uniao\nrefinamento valor bigger 0\nyes [String, Integer]\nyes no 4'


def test_satisfaz_responde_sem_levantar():
    assert rodar('''
adopt Arcane.Tipos as T
type Positivo := Integer where valor bigger 0
type Json := String | Integer
opaque type Cpf := String where len(valor) is 11

out T.satisfaz(5, "Positivo"), T.satisfaz(-5, "Positivo")
out T.satisfaz("texto", "Positivo")
out T.satisfaz("oi", "Json"), T.satisfaz([1], "Json")
out T.satisfaz(Cpf("12345678901"), "Cpf"), T.satisfaz("12345678901", "Cpf")
''') == "yes no\nno\nyes no\nyes no"


def test_conferir_levanta_o_erro_de_sempre():
    erro = erro_de('''
adopt Arcane.Tipos as T
type Positivo := Integer where valor bigger 0
T.conferir(-1, "Positivo")
''')
    assert "Positivo" in erro.message


def test_a_forma_e_estrutural_e_typeof_e_o_nome():
    assert rodar('''
adopt Arcane.Tipos as T
out typeof([1, 2]), T.forma([1, 2])
out T.forma([1, "a"]), T.forma((1, "a")), T.forma({"a": 1})
out T.forma([[1], [2]]), T.forma(3), T.nome_de("x")
''') == 'Cluster Cluster<Integer>\nCluster<Any> Tuple<Integer, String> Vault<String, Integer>\n' \
        'Cluster<Cluster<Integer>> Integer String'


def test_os_campos_de_um_record_e_de_uma_instancia():
    assert rodar('''
adopt Arcane.Tipos as T
record Cliente:
    nome: String
    idade: Integer

blueprint Conta:
    saldo := 0.0

c := Cliente("Ana", 30)
campos := T.campos(c)
out campos["nome"]["tipo"], campos["idade"]["valor"]
out T.campos(spawn Conta())["saldo"]["tipo"]
out T.campos({"a": 1})["a"]["tipo"]
''') == "String 30\nFloat\nInteger"


def test_colecao_e_imutabilidade():
    assert rodar('''
adopt Arcane.Tipos as T
out T.e_colecao([1]), T.e_colecao((1, 2)), T.e_colecao(3)
out T.e_imutavel((1, 2)), T.e_imutavel([1, 2]), T.e_imutavel("texto")
''') == "yes yes no\nyes no yes"


# ── o módulo, e o repositório ────────────────────────────────

def test_os_modulos_estao_registrados_pelos_apelidos():
    for nome in ("Arcane.Resultado", "Resultado", "Result"):
        assert get_module(nome) is not None, nome
    for nome in ("Arcane.Tipos", "Tipos"):
        assert get_module(nome) is not None, nome
    assert get_module("Arcane.Resultado")["__name__"] == "Arcane.Resultado"


def test_o_catalogo_descreve_os_dois():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.Resultado", "Arcane.Tipos"):
        assert nome in DESCRICOES, nome
        assert len(DESCRICOES[nome][0]) > 60


def test_o_check_nao_reclama_do_uso_normal():
    assert not erros('''
adopt Arcane.Resultado as R
adopt Arcane.Tipos as T
type Positivo := Integer where valor bigger 0

action buscar(id):
    given id smaller 0:
        yield R.falha("id negativo")
    yield R.ok(id)

r := buscar(3)
out r.ou(0), T.satisfaz(3, "Positivo")
''')


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import tipos_resultado
    for pagina in tipos_resultado.PAGINAS:
        for i, bloco in enumerate(pagina["blocos"]):
            if "code" in bloco and bloco.get("lang") == "df" \
                    and not bloco.get("title"):
                yield f"{pagina['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_da_doc()))
def test_todo_exemplo_da_doc_roda_e_passa_no_check(onde, codigo):
    rodar(codigo)
    assert not erros(codigo), f"{onde}: {[d.message for d in erros(codigo)]}"


def test_o_repositorio_continua_limpo():
    for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"):
        r = subprocess.run([sys.executable, "-m", "dataforge", "check", pasta],
                           cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env={**os.environ, "NO_COLOR": "1"})
        assert r.returncode == 0, f"{pasta}: {r.stdout[-600:]}"
