"""A superfície como contrato, e o alvo como restrição.

**Parte 18 — ABI.** Numa linguagem compilada, quebrar a ABI é trocar o
layout de uma struct ou a convenção de chamada, e o sintoma é um
programa que carrega e corrompe memória. Aqui não há layout binário a
quebrar — mas há **exatamente o mesmo problema**, com outro nome: a
**superfície** de um módulo é o contrato dele, e mudá-la quebra quem
depende, em silêncio, no dia da atualização.

O gerenciador de pacotes já tem semver, `forge.lock` e verificação de
integridade. O que faltava era o que **decide o número**: nada conferia
se a versão nova quebra a anterior.

**Parte 19 — alvos.** "Isso roda no navegador?" é uma pergunta real, e
a resposta dependia de alguém conhecer de cor o que cada ambiente
suporta. `Arcane.Alvo` responde a partir dos `adopt` — e diz, com todas
as letras, que é uma leitura **estática**, e não uma prova.
"""

import io
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import DataForgeError                    # noqa: E402
from dataforge.interpreter import Interpreter                  # noqa: E402
from dataforge.lexer import tokenize                           # noqa: E402
from dataforge.parser import parse                             # noqa: E402
from dataforge.stdlib import get_module                        # noqa: E402


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
    return saida.getvalue()


@pytest.fixture
def A():
    return get_module("Arcane.Abi")


@pytest.fixture
def T():
    return get_module("Arcane.Alvo")


@pytest.fixture
def pasta():
    with tempfile.TemporaryDirectory() as d:
        yield d


def escrever(pasta, nome, fonte):
    caminho = os.path.join(pasta, nome)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(fonte)
    from dataforge import superficie
    superficie.limpar_cache()
    # O caminho entra numa string DE DATAFORGE, e ali a barra invertida
    # é escape: 'C:\\Users\\runneradmin\\Temp' chega com um retorno de
    # carro e uma tabulação no lugar das pastas. O sintoma no Windows
    # era um 'Index 0 is out of range' — o arquivo não foi achado, a
    # comparação não teve o que comparar, e o erro apareceu três
    # chamadas depois. O Windows aceita '/'.
    return caminho.replace(os.sep, "/")


V1 = '''action somar(a: Integer, b: Integer) -> Integer:
    yield a + b

action saudar(nome: String) -> String:
    yield $"ola, {nome}"

record Ponto:
    x: Integer
    y: Integer

relay somar, saudar, Ponto
'''


# ══════════════════════════════════════════════════════════════
#  A superfície
# ══════════════════════════════════════════════════════════════

def test_a_superficie_traz_o_contrato_inteiro(A, pasta):
    caminho = escrever(pasta, "lib.df", V1)
    s = A["superficie"](caminho)

    assert set(s) == {"somar", "saudar", "Ponto"}
    assert s["somar"]["especie"] == "acao"
    assert s["somar"]["parametros"] == ["a", "b"]
    assert s["somar"]["tipos"]["a"] == "Integer"
    assert s["somar"]["retorno"] == "Integer"
    assert s["Ponto"]["especie"] == "record"
    assert sorted(s["Ponto"]["campos"]) == ["x", "y"]


def test_o_que_nao_e_exportado_nao_e_contrato(A, pasta):
    """Um módulo que declara o que exporta está dizendo que o resto é dele."""
    caminho = escrever(pasta, "lib.df", V1 + '''
action interna():
    yield 1
''')
    s = A["superficie"](caminho)
    assert "interna" not in s, "o que o relay não nomeia não é contrato"


def test_sem_relay_tudo_o_que_e_de_topo_e_contrato(A, pasta):
    caminho = escrever(pasta, "solto.df", '''action um():
    yield 1

action dois():
    yield 2
''')
    s = A["superficie"](caminho)
    assert set(s) == {"um", "dois"}


# ══════════════════════════════════════════════════════════════
#  O que quebra
# ══════════════════════════════════════════════════════════════

def comparar(A, pasta, antes, depois):
    a = escrever(pasta, "antes.df", antes)
    b = escrever(pasta, "depois.df", depois)
    return A["comparar"](a, b)


def test_nada_mudou_e_correcao(A, pasta):
    r = comparar(A, pasta, V1, V1)
    assert r["quebras"] == []
    assert r["compativeis"] == []
    assert r["veredito"] == "correcao"


def test_um_simbolo_novo_e_menor(A, pasta):
    r = comparar(A, pasta, V1, V1.replace(
        "relay somar, saudar, Ponto",
        "action dobrar(n):\n    yield n * 2\n\nrelay somar, saudar, Ponto, dobrar"))
    assert r["quebras"] == []
    assert [c["tipo"] for c in r["compativeis"]] == ["simbolo-novo"]
    assert r["veredito"] == "menor"


def test_tirar_um_simbolo_e_maior(A, pasta):
    r = comparar(A, pasta, V1,
                 V1.replace("relay somar, saudar, Ponto", "relay somar, Ponto"))
    assert [q["tipo"] for q in r["quebras"]] == ["simbolo-removido"]
    assert r["quebras"][0]["nome"] == "saudar"
    assert r["veredito"] == "maior"


def test_exigir_mais_um_argumento_e_maior(A, pasta):
    """`somar(1, 2)` compilava ontem, e hoje não."""
    r = comparar(A, pasta, V1,
                 V1.replace("action somar(a: Integer, b: Integer)",
                            "action somar(a: Integer, b: Integer, c: Integer)"))
    tipos = [q["tipo"] for q in r["quebras"]]
    assert "aridade-incompativel" in tipos
    assert r["veredito"] == "maior"


def test_um_parametro_OPCIONAL_novo_e_menor(A, pasta):
    """Quem chamava com dois continua chamando com dois."""
    r = comparar(A, pasta, V1,
                 V1.replace("action somar(a: Integer, b: Integer)",
                            "action somar(a: Integer, b: Integer, c := 0)"))
    assert r["quebras"] == []
    assert any(c["tipo"] == "parametro-opcional-novo"
               for c in r["compativeis"])
    assert r["veredito"] == "menor"


def test_renomear_um_parametro_e_maior(A, pasta):
    """Chamada com nome existe nesta linguagem: `somar(a := 1, b := 2)`."""
    r = comparar(A, pasta, V1,
                 V1.replace("action somar(a: Integer, b: Integer)",
                            "action somar(x: Integer, b: Integer)"))
    assert any(q["tipo"] == "parametro-renomeado" for q in r["quebras"])
    assert r["veredito"] == "maior"


def test_trocar_o_tipo_de_um_parametro_e_maior(A, pasta):
    r = comparar(A, pasta, V1,
                 V1.replace("action somar(a: Integer, b: Integer)",
                            "action somar(a: String, b: Integer)"))
    quebra = [q for q in r["quebras"] if q["tipo"] == "tipo-de-parametro"][0]
    assert quebra["antes"] == "Integer" and quebra["depois"] == "String"


def test_trocar_o_retorno_e_maior(A, pasta):
    r = comparar(A, pasta, V1,
                 V1.replace("action somar(a: Integer, b: Integer) -> Integer",
                            "action somar(a: Integer, b: Integer) -> Float"))
    assert any(q["tipo"] == "retorno-trocado" for q in r["quebras"])


def test_tirar_um_campo_de_record_e_maior(A, pasta):
    r = comparar(A, pasta, V1, V1.replace("    y: Integer\n", ""))
    assert any(q["tipo"] == "campo-removido" for q in r["quebras"])
    assert r["veredito"] == "maior"


def test_campo_novo_num_record_e_ATENCAO_e_nao_quebra(A, pasta):
    """A superfície não carrega valor padrão, então ela não decide.

    Acusar quebra reprovaria um release correto (o campo pode ter
    padrão); calar deixaria passar um que quebra. O honesto é um
    terceiro balde, em destaque, que `--estrito` transforma em quebra.
    """
    r = comparar(A, pasta, V1, V1.replace(
        "    y: Integer\n", "    y: Integer\n    z: Integer\n"))
    assert [a["tipo"] for a in r["atencao"]] == ["campo-novo-em-record"]
    assert not any(q["nome"] == "Ponto" for q in r["quebras"]), \
        "o campo e a aridade de um record: contar os dois é contar duas vezes"
    assert not any(c["nome"] == "Ponto" for c in r["compativeis"])


def test_trocar_a_especie_e_maior(A, pasta):
    r = comparar(A, pasta, V1,
                 V1.replace("record Ponto:\n    x: Integer\n    y: Integer",
                            "action Ponto(x, y):\n    yield [x, y]"))
    assert any(q["tipo"] == "especie-trocada" for q in r["quebras"])


def test_cada_quebra_diz_onde_e_o_que_fazer(A, pasta):
    r = comparar(A, pasta, V1,
                 V1.replace("relay somar, saudar, Ponto", "relay somar, Ponto"))
    quebra = r["quebras"][0]
    for chave in ("tipo", "nome", "explica", "dica"):
        assert chave in quebra, chave
    assert len(quebra["explica"]) > 25
    assert len(quebra["dica"]) > 15


def test_as_regras_estao_nomeadas_e_descritas(A):
    regras = A["regras"]()
    assert len(regras) >= 7
    for nome, texto in regras.items():
        assert len(texto) > 25, nome


def test_uma_superficie_que_nao_compila_nao_julga(A, pasta):
    """Um falso alarme aqui reprova um release que está certo."""
    a = escrever(pasta, "a.df", V1)
    b = escrever(pasta, "b.df", "action quebrada(:\n")
    r = A["comparar"](a, b)
    assert r["veredito"] == "desconhecido"
    assert r["motivo"] != ""


# ══════════════════════════════════════════════════════════════
#  O mapa de símbolos — o análogo do mapa do ligador
# ══════════════════════════════════════════════════════════════

def test_o_mapa_diz_de_onde_vem_cada_nome(A, pasta):
    caminho = escrever(pasta, "prog.df", '''adopt Arcane.Math as M

action calcular(n):
    yield M.sqrt(n) + len("abc") + solto

solto := 2
out calcular(16)
''')
    mapa = A["mapa"](caminho)
    por_nome = {e["nome"]: e for e in mapa}
    assert por_nome["M"]["origem"] == "modulo"
    assert por_nome["M"]["de"] == "Arcane.Math"
    assert por_nome["len"]["origem"] == "embutido"
    assert por_nome["calcular"]["origem"] == "local"


def test_o_mapa_acha_o_nome_que_nao_tem_dono(A, pasta):
    caminho = escrever(pasta, "prog.df", '''action f():
    yield fantasma + 1
''')
    mapa = A["mapa"](caminho)
    orfaos = [e for e in mapa if e["origem"] == "desconhecido"]
    assert [e["nome"] for e in orfaos] == ["fantasma"]


# ══════════════════════════════════════════════════════════════
#  Parte 19 — alvos
# ══════════════════════════════════════════════════════════════

def test_os_alvos_estao_descritos_e_dizem_o_que_suportam(T):
    alvos = T["alvos"]()
    for nome in ("servidor", "navegador", "wasi", "embarcado"):
        assert nome in alvos, nome
        assert len(alvos[nome]["o_que_e"]) > 30
        assert isinstance(alvos[nome]["suporta"], list)


def test_o_servidor_suporta_tudo(T):
    alvos = T["alvos"]()
    assert set(alvos["servidor"]["nao_suporta"]) == set()


def test_o_navegador_nao_tem_processo_nem_ffi(T):
    nao = set(T["alvos"]()["navegador"]["nao_suporta"])
    assert {"processo", "nativo", "threads"} <= nao


def test_as_exigencias_saem_dos_adopt(T, pasta):
    caminho = escrever(pasta, "p.df", '''adopt Arcane.IO as IO
adopt Arcane.Math as M
adopt Arcane.Process as P

out 1
''')
    exigencias = T["exigencias"](caminho)
    capacidades = {e["capacidade"] for e in exigencias}
    assert capacidades == {"arquivos", "processo"}
    assert all("linha" in e and "modulo" in e for e in exigencias)


def test_um_programa_puro_nao_exige_nada(T, pasta):
    caminho = escrever(pasta, "puro.df", "adopt Arcane.Math as M\nout M.sqrt(4)\n")
    assert T["exigencias"](caminho) == []


def test_o_que_roda_no_servidor_pode_nao_rodar_no_navegador(T, pasta):
    caminho = escrever(pasta, "p.df", '''adopt Arcane.Process as P
out 1
''')
    assert T["conferir"](caminho, "servidor")["roda"]
    veredito = T["conferir"](caminho, "navegador")
    assert not veredito["roda"]
    assert veredito["problemas"][0]["capacidade"] == "processo"
    assert len(veredito["problemas"][0]["porque"]) > 25


def test_um_alvo_inventado_e_recusado_com_a_lista(T, pasta):
    caminho = escrever(pasta, "p.df", "out 1\n")
    with pytest.raises(DataForgeError) as capturado:
        T["conferir"](caminho, "nintendo")
    assert "nintendo" in str(capturado.value)
    assert "navegador" in str(capturado.value)


def test_o_relatorio_diz_que_a_leitura_e_ESTATICA(T):
    limites = T["limites"]()
    inteiro = " ".join(limites).lower()
    assert "estátic" in inteiro or "estatic" in inteiro
    assert "adopt" in inteiro


def test_a_ponte_para_o_python_conta_como_exigencia(T, pasta):
    caminho = escrever(pasta, "p.df", "adopt Python.os as so\nout 1\n")
    exigencias = T["exigencias"](caminho)
    assert exigencias[0]["capacidade"] == "python"


# ══════════════════════════════════════════════════════════════
#  A CLI
# ══════════════════════════════════════════════════════════════

def _cli(*args):
    return subprocess.run([sys.executable, "-m", "dataforge", *args],
                          cwd=RAIZ, capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          env={**os.environ, "NO_COLOR": "1"})


def test_o_comando_abi_acusa_a_quebra(pasta):
    a = escrever(pasta, "antes.df", V1)
    b = escrever(pasta, "depois.df",
                 V1.replace("relay somar, saudar, Ponto", "relay somar, Ponto"))
    r = _cli("abi", a, b)
    assert r.returncode != 0, "uma quebra tem de reprovar no CI"
    assert "saudar" in r.stdout
    assert "maior" in r.stdout.lower()


def test_o_comando_abi_aprova_o_que_so_acrescenta(pasta):
    a = escrever(pasta, "antes.df", V1)
    b = escrever(pasta, "depois.df", V1.replace(
        "relay somar, saudar, Ponto",
        "action novo():\n    yield 1\n\nrelay somar, saudar, Ponto, novo"))
    r = _cli("abi", a, b)
    assert r.returncode == 0
    assert "menor" in r.stdout.lower()


def test_o_comando_alvo_responde_a_pergunta(pasta):
    caminho = escrever(pasta, "p.df", "adopt Arcane.Process as P\nout 1\n")
    r = _cli("alvo", caminho, "--alvo=navegador")
    assert r.returncode != 0
    assert "processo" in r.stdout.lower()
    ok = _cli("alvo", caminho, "--alvo=servidor")
    assert ok.returncode == 0


def test_o_comando_alvo_sem_alvo_mostra_todos(pasta):
    caminho = escrever(pasta, "p.df", "adopt Arcane.IO as IO\nout 1\n")
    r = _cli("alvo", caminho)
    assert r.returncode == 0
    for nome in ("servidor", "navegador", "wasi"):
        assert nome in r.stdout


# ══════════════════════════════════════════════════════════════
#  Da linguagem, o módulo e a doc
# ══════════════════════════════════════════════════════════════

def test_funciona_de_dentro_da_linguagem(pasta):
    a = escrever(pasta, "v1.df", V1)
    b = escrever(pasta, "v2.df",
                 V1.replace("relay somar, saudar, Ponto", "relay somar, Ponto"))
    saida = rodar(f'''
adopt Arcane.Abi as Abi

r := Abi.comparar("{a}", "{b}")
out r["veredito"], len(r["quebras"])
out r["quebras"][0]["tipo"]
''')
    assert saida == "maior 1\nsimbolo-removido\n"


def test_os_modulos_estao_registrados_e_descritos():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.Abi", "Abi", "Arcane.Alvo", "Alvo"):
        assert get_module(nome) is not None, nome
    for nome in ("Arcane.Abi", "Arcane.Alvo"):
        assert nome in DESCRICOES


def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import abi_e_alvos
    for pagina in abi_e_alvos.PAGINAS:
        for i, bloco in enumerate(pagina["blocos"]):
            if "code" in bloco and bloco.get("lang") == "df" \
                    and not bloco.get("title"):
                yield f"{pagina['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_da_doc()))
def test_todo_exemplo_da_doc_roda(onde, codigo):
    rodar(codigo)


def test_o_repositorio_continua_limpo():
    for pasta_alvo in ("examples", "exercicios", "projetos", "packages",
                       "trilha"):
        r = _cli("check", pasta_alvo)
        assert r.returncode == 0, f"{pasta_alvo}: {r.stdout[-600:]}"
