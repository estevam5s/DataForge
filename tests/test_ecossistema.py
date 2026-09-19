"""O ecossistema conferido, os princípios medidos, e o percurso.

**Parte 20 — o ecossistema.** Um desenho de arquitetura é o texto mais
fácil de escrever num projeto e o mais fácil de deixar envelhecer: ele
não roda, ninguém o executa, e no dia em que uma peça muda de nome o
mapa passa a mentir sem nada denunciar. Aqui ele é **conferido** nas duas
direções — todo caminho citado existe, e todo módulo do núcleo aparece.

**Parte 21 — os princípios.** Uma lista de princípios nunca reprova.
Aqui cada um carrega uma prova que **roda**, e o veredito não é dez de
dez: há parciais e há um que não se aplica, com o motivo.

**Parte 22 — o percurso.** As fases em ordem, medidas — e a última é
nomeada e **não percorrida**, porque executar é o que o programa faz.

Os testes deste arquivo cobram, principalmente, as travas que impedem os
três de envelhecerem.
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
from dataforge.stdlib import arcane_ecossistema as eco         # noqa: E402
from dataforge.stdlib import arcane_percurso as perc           # noqa: E402
from dataforge.stdlib import arcane_principios as prin         # noqa: E402


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<teste>"), "<teste>"))
    return saida.getvalue()


def _cli(*args):
    # `encoding` explicito: com `text=True` e sem ele, o Windows le
    # cp1252 e os tracos da saida viram lixo — ha trava no repositorio.
    return subprocess.run([sys.executable, "-m", "dataforge", *args],
                          capture_output=True, text=True,
                          encoding="utf-8", cwd=RAIZ)


# ═══ Parte 20 — o mapa, e as travas que o mantêm honesto ═══

def test_o_mapa_bate_com_o_disco():
    """A trava principal: todo caminho citado existe, e nada ficou fora.

    Ela já pagou por si. A primeira versão do mapa citava
    `dataforge/stdlib/arcane_concurrent.py` em dois componentes — o
    arquivo se chama `arcane_paralelo.py`, e só a CLASSE se chama
    `ArcaneConcurrent`. Os dois foram acusados antes de este teste
    existir.
    """
    r = eco.conferir()
    assert not r["faltando"], f"caminho que sumiu: {r['faltando']}"
    assert not r["orfaos"], (
        "modulo do nucleo fora do mapa do ecossistema: "
        f"{r['orfaos']} — acrescente-o a ARVORE ou a NAO_E_COMPONENTE")
    assert r["ok"]
    assert r["citados"] > 40


def test_todo_modulo_novo_do_nucleo_precisa_entrar_no_mapa():
    """A direção que impede o inventário de ficar incompleto em silêncio.

    Sem ela, um módulo novo nasce fora do mapa e nada acusa: o
    inventário simplesmente deixa de mencionar uma peça que existe.
    """
    nucleo = {f for f in os.listdir(os.path.join(RAIZ, "dataforge"))
              if f.endswith(".py")}
    citados = {os.path.basename(c)
               for _g, no in eco._nos() for c in no["onde"]
               if c.startswith("dataforge/") and "/stdlib/" not in c}
    assert nucleo - set(eco.NAO_E_COMPONENTE) <= citados


def test_os_tres_estados_sao_fechados():
    """Um quarto estado seria onde 'mais ou menos' se esconderia."""
    assert eco.ESTADOS == ("existe", "equivale", "nao-existe")
    for _grupo, no in eco._nos():
        assert no["estado"] in eco.ESTADOS, no["no"]


def test_toda_ausencia_tem_motivo_e_o_que_esta_no_lugar():
    """Uma ausência sem motivo é a linha que o leitor não pode usar."""
    faltam = eco.o_que_nao_existe()
    assert len(faltam) >= 5
    for c in faltam:
        assert c["porque"].strip(), f"{c['no']} sem porque"
        assert c["aqui"].strip(), f"{c['no']} sem o que esta no lugar"
        assert c["o_que_e"].strip(), f"{c['no']} sem descricao"


def test_toda_equivalencia_nomeia_a_peca_que_esta_no_lugar():
    """'Equivale' sem nome do substituto é só um 'não' disfarçado."""
    for c in eco.equivalencias():
        assert c["aqui"].strip(), f"{c['no']}: equivale a nada?"
        assert c["porque"].strip(), f"{c['no']}: sem por que nao e igual"


def test_o_llvm_nao_e_prometido_como_futuro():
    """A ausência do backend nativo é uma DECISÃO, não um atraso.

    'Ainda não temos' sugeriria que vem depois. O motivo real é que ele
    tiraria a zero dependência, e o teto da técnica usada é conhecido.
    """
    llvm = [c for c in eco.o_que_nao_existe()
            if c["no"] == "LLVM Backend"]
    assert llvm, "o LLVM Backend saiu do mapa"
    assert "fechamentos" in llvm[0]["aqui"]
    assert "dependencia" in llvm[0]["porque"]


def test_os_numeros_saem_do_gerador_canonico():
    """Uma soma própria já divergiu em 112 símbolos, e foi publicada.

    A contagem tem de bater com `gerar_pagina_biblioteca.py`, que é
    quem escreve a tabela do site.
    """
    import importlib.util as u
    caminho = os.path.join(RAIZ, "tools", "gerar_pagina_biblioteca.py")
    spec = u.spec_from_file_location("gpb", caminho)
    modulo = u.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    canonico = modulo.levantar()

    n = eco.numeros()
    assert n["modulos"] == len(canonico)
    assert n["simbolos"] == sum(m[1] for m in canonico)


def test_os_numeros_fecham_entre_si():
    n = eco.numeros()
    assert n["existem"] + n["equivalem"] + n["nao_existem"] \
        == n["componentes"]
    assert n["comandos"] > 40
    assert n["alvos"] >= 6


def test_a_arvore_desenha_as_tres_marcas():
    texto = eco.arvore()
    for marca in ("[+]", "[~]", "[-]"):
        assert marca in texto
    for grupo, _nos in eco.ARVORE:
        assert grupo in texto


def test_o_relatorio_diz_o_que_nao_existe():
    texto = eco.relatorio()
    assert "o que NAO existe" in texto
    assert "LLVM Backend" in texto
    assert "bate com o disco" in texto


# ═══ Parte 21 — os princípios, e as provas que rodam ══════

def test_sao_dez_principios_com_todos_os_campos():
    assert len(prin.PRINCIPIOS) == 10
    for p in prin.PRINCIPIOS:
        for campo in ("numero", "principio", "no_documento", "aqui",
                      "veredito", "prova", "custo", "onde"):
            assert campo in p, f"{p.get('principio')}: falta {campo}"
        assert p["veredito"] in prin.VEREDITOS
        assert callable(p["prova"])
        assert p["custo"].strip(), f"{p['principio']} sem custo declarado"
        assert p["onde"], f"{p['principio']} sem rota"


def test_os_numeros_dos_principios_vao_de_um_a_dez():
    assert [p["numero"] for p in prin.PRINCIPIOS] == list(range(1, 11))


def test_toda_prova_roda_e_devolve_uma_medida():
    """A diferença entre afirmar um princípio e demonstrá-lo."""
    for p in prin.conferir():
        assert p["medido"].strip(), f"{p['principio']}: nada medido"
        assert not p["medido"].startswith("a prova falhou"), \
            f"{p['principio']}: {p['medido']}"
        assert p["como"].strip(), f"{p['principio']}: sem dizer como"


def test_a_prova_do_compile_time_roda_o_analisador_de_verdade():
    """Ela acusa quatro erros de execução ANTES de rodar."""
    p = prin.conferir("compile-time-first")[0]
    assert "4 de 4" in p["medido"]


def test_a_prova_do_custo_zero_olha_os_tres_sentinelas():
    """Contrato, invariante e estado por objeto custam zero desligados."""
    p = prin.conferir("custo-zero")[0]
    assert "3 de 3" in p["medido"]
    assert "2 de 2" in p["medido"]


def test_a_escrita_concorrente_continua_sendo_AVISO():
    """A tensão central, cobrada: recusá-la proibiria o uso correto."""
    p = prin.conferir("seguranca-por-padrao")[0]
    assert "'warning'" in p["medido"], (
        "a escrita concorrente virou erro — isso proibiria o acumulador "
        "protegido por mutex, que e o uso correto")


def test_um_interpretador_novo_nao_carrega_modulo_nenhum():
    """'Runtime modular', medido: o dicionário nasce no `adopt`."""
    p = prin.conferir("runtime-modular")[0]
    assert p["medido"].startswith("0 modulos")
    assert "0 dependencias externas" in p["medido"]


def test_o_veredito_nao_e_dez_de_dez():
    """Um relatório que aprovasse os dez seria prova de que ninguém leu."""
    v = prin.veredito()
    assert v["total"] == 10
    assert v["cumprido"] + v["parcial"] + v["nao-se-aplica"] == 10
    assert v["parcial"] >= 1, "nenhum parcial: o relatorio ficou otimista"
    assert v["nao-se-aplica"] >= 1


def test_custo_zero_e_nao_se_aplica_e_a_leitura_esta_escrita():
    """Redefinir a frase em silêncio seria pior que marcá-la."""
    p = [x for x in prin.PRINCIPIOS if x["principio"] == "custo-zero"][0]
    assert p["veredito"] == "nao-se-aplica"
    assert "OUTRA leitura" in p["aqui"]


def test_principio_desconhecido_levanta_com_a_lista():
    with pytest.raises(DataForgeError) as erro:
        prin.conferir("nao-existe-esse")
    assert "compile-time-first" in str(erro.value)


def test_toda_tensao_tem_escolha_custo_e_arquivo():
    """A tensão sem custo é um princípio disfarçado."""
    assert len(prin.TENSOES) >= 9
    for t in prin.TENSOES:
        assert len(t["entre"]) == 2, t
        assert t["escolha"].strip()
        assert t["porque"].strip()
        assert t["custo"].strip(), f"{t['entre']}: sem custo declarado"
        assert t["onde"].strip(), f"{t['entre']}: sem arquivo"


def test_o_arquivo_de_cada_tensao_existe():
    """Uma tensão que aponta um arquivo que não existe não é verificável."""
    quebradas = []
    for t in prin.TENSOES:
        caminho = t["onde"].split("—")[0].strip()
        if not os.path.exists(os.path.join(RAIZ, caminho)):
            quebradas.append(f"{t['entre']}: {caminho}")
    assert not quebradas, quebradas


def test_toda_rota_de_principio_existe_no_site():
    docs = os.path.join(RAIZ, "site", "app", "docs")
    if not os.path.isdir(docs):
        pytest.skip("o site não está neste checkout")
    quebradas = []
    for p in prin.PRINCIPIOS:
        for rota in p["onde"]:
            alvo = os.path.join(docs, rota.replace("/docs/", "", 1)
                                .strip("/"), "page.tsx")
            if not os.path.isfile(alvo):
                quebradas.append(f"{p['principio']}: {rota}")
    assert not quebradas, quebradas


# ═══ Parte 22 — o percurso ════════════════════════════════

def test_sao_dez_fases_na_ordem_do_caminho():
    assert len(perc.FASES) == 10
    assert [f["fase"] for f in perc.FASES][:3] == ["lexer", "parser", "hir"]
    assert perc.FASES[-1]["fase"] == "execucao"


def test_toda_fase_nomeia_o_arquivo_onde_mora_e_ele_existe():
    for f in perc.FASES:
        assert os.path.isfile(os.path.join(RAIZ, f["modulo"])), f["modulo"]
        assert f["o_que_faz"].strip()


def test_percorrer_mede_as_nove_e_nao_executa_a_decima():
    """Executar é o que o programa faz — e este comando não pode.

    A prova é direta: o programa escreve num arquivo, e o arquivo não
    pode existir depois do percurso.
    """
    with tempfile.TemporaryDirectory() as pasta:
        marca = os.path.join(pasta, "rodou.txt").replace("\\", "/")
        alvo = os.path.join(pasta, "efeito.df")
        with open(alvo, "w", encoding="utf-8") as arquivo:
            arquivo.write("adopt Arcane.IO as IO\n"
                          f'IO.write("{marca}", "rodou")\n')
        r = perc.percorrer(alvo)
        assert not os.path.exists(marca), (
            "o percurso EXECUTOU o programa — um comando que mostra fases "
            "nao pode ter efeito no mundo")

    assert len(r["fases"]) == 10
    ultima = r["fases"][-1]
    assert ultima["fase"] == "execucao"
    assert ultima["percorrida"] is False
    assert ultima["ms"] == 0.0
    assert "nao percorrida" in ultima["saiu"]


def test_a_fase_ausente_continua_no_mapa():
    """Apagá-la faria o desenho parecer completo."""
    assert any(not f["percorrida"] for f in perc.percorrer(
        os.path.join(RAIZ, "examples", "01_hello.df"))["fases"])


def test_as_nove_fases_percorridas_dizem_o_que_produziram():
    r = perc.percorrer(os.path.join(RAIZ, "examples", "01_hello.df"))
    percorridas = [f for f in r["fases"] if f["percorrida"]]
    assert len(percorridas) == 9
    for f in percorridas:
        assert f["saiu"].strip(), f"{f['fase']}: nao disse o que saiu"
        assert f["ms"] >= 0.0
    assert r["mais_cara"] in [f["fase"] for f in percorridas]


def test_o_import_nao_e_cobrado_da_fase_que_o_toca():
    """A armadilha que inverteu a resposta da ferramenta.

    O `lir` importa `compilador` e abre um interpretador por dentro. Sem
    aquecer os imports antes do cronometro, ele aparecia com 93,8% num
    arquivo de 12 tokens — contra 0,05 ms de trabalho real. Uma
    ferramenta que aponta a fase errada e pior que nenhuma: a pessoa vai
    otimizar o lugar que ela indicou.

    A trava e estrutural, e nao um limite de tempo: o `lir` de um
    arquivo minusculo nao pode ser a fase dominante.
    """
    r = perc.percorrer(os.path.join(RAIZ, "examples", "01_hello.df"))
    lir = [f for f in r["fases"] if f["fase"] == "lir"][0]
    assert lir["fatia"] < 60.0, (
        f"o 'lir' ficou com {lir['fatia']}% num arquivo minusculo: o "
        f"aquecimento dos imports foi removido?")


def test_sem_tipos_pula_a_fase_mais_cara_de_um_projeto():
    r = perc.percorrer(os.path.join(RAIZ, "examples", "01_hello.df"),
                       com_tipos=False)
    tipos = [f for f in r["fases"] if f["fase"] == "tipos"][0]
    assert tipos["ms"] == 0.0
    assert "pulada" in tipos["saiu"]


def test_percorrer_recusa_o_que_nao_existe_e_o_que_nao_compila():
    with pytest.raises(DataForgeError):
        perc.percorrer(os.path.join(RAIZ, "nao-existe-este-arquivo.df"))

    with tempfile.TemporaryDirectory() as pasta:
        alvo = os.path.join(pasta, "quebrado.df")
        with open(alvo, "w", encoding="utf-8") as arquivo:
            arquivo.write("given :\n")
        with pytest.raises(DataForgeError) as erro:
            perc.percorrer(alvo)
        assert "parser" in str(erro.value) or "lexer" in str(erro.value)


def test_o_desenho_poe_a_ausencia_no_lugar_dela():
    texto = perc.desenho()
    assert "NAO EXISTE" in texto
    assert "LLVM" in texto
    assert "interpretador" in texto


def test_toda_divergencia_tem_motivo():
    assert len(perc.DIVERGENCIAS) >= 5
    for d in perc.DIVERGENCIAS:
        assert d["aqui"].strip()
        assert d["porque"].strip(), f"{d['no_desenho']} sem motivo"


def test_o_aviso_sobre_a_medida_esta_no_resultado():
    """A medida é uma vez, nesta máquina — e o resultado diz isso."""
    r = perc.percorrer(os.path.join(RAIZ, "examples", "01_hello.df"))
    assert "UMA vez" in r["aviso"]
    assert "Bench" in r["aviso"]


# ═══ Os comandos ══════════════════════════════════════════

def test_o_comando_do_ecossistema_confere_e_sai_com_zero():
    r = _cli("ecossistema")
    assert r.returncode == 0, r.stdout[-800:]
    assert "bate com o disco" in r.stdout
    assert "[-]" in r.stdout


def test_o_comando_lista_so_as_ausencias():
    r = _cli("ecossistema", "--ausencias")
    assert r.returncode == 0
    assert "LLVM Backend" in r.stdout
    assert "no lugar:" in r.stdout


def test_o_comando_dos_principios_mostra_veredito_e_medida():
    r = _cli("principios")
    assert r.returncode == 0, r.stdout[-800:]
    assert "medido:" in r.stdout
    assert "nao-se-aplica" in r.stdout
    assert "custo:" in r.stdout


def test_o_comando_mostra_as_tensoes_com_arquivo():
    r = _cli("principios", "--tensoes")
    assert r.returncode == 0
    assert "escolha:" in r.stdout
    assert "dataforge/" in r.stdout


def test_o_comando_do_percurso_desenha_e_percorre():
    r = _cli("percurso", "--desenho")
    assert r.returncode == 0
    assert "NAO EXISTE" in r.stdout

    r = _cli("percurso", os.path.join("examples", "01_hello.df"))
    assert r.returncode == 0, r.stdout[-800:]
    assert "nao percorrida" in r.stdout
    assert "fase mais cara" in r.stdout


def test_os_tres_saem_como_json():
    import json
    for args in (("ecossistema", "--json"), ("principios", "--json"),
                 ("percurso", os.path.join("examples", "01_hello.df"),
                  "--json")):
        r = _cli(*args)
        assert r.returncode == 0, f"{args}: {r.stdout[-400:]}"
        json.loads(r.stdout)


def test_os_modulos_estao_registrados_e_descritos():
    from dataforge.stdlib.catalogo import DESCRICOES
    for nome in ("Arcane.Ecossistema", "Ecossistema", "Arcane.Principios",
                 "Principios", "Arcane.Percurso", "Percurso"):
        assert get_module(nome) is not None, nome
    for nome in ("Arcane.Ecossistema", "Arcane.Principios",
                 "Arcane.Percurso"):
        assert nome in DESCRICOES
        assert get_module(nome)["__name__"] == nome


# ═══ A documentação ═══════════════════════════════════════

def _blocos_df_da_doc():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import ecossistema as pagina
    for p in pagina.PAGINAS:
        for i, bloco in enumerate(p["blocos"]):
            if "code" in bloco and bloco.get("lang") == "df" \
                    and not bloco.get("title"):
                yield f"{p['href']}#{i}", bloco["code"]


@pytest.mark.parametrize("onde,codigo", list(_blocos_df_da_doc()))
def test_todo_exemplo_da_doc_roda(onde, codigo):
    rodar(codigo)


def test_as_sete_paginas_existem_e_estao_na_navegacao():
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    from conteudo import ecossistema as pagina

    nav = os.path.join(RAIZ, "site", "lib", "nav.ts")
    if not os.path.isfile(nav):
        pytest.skip("o site não está neste checkout")
    fonte = open(nav, encoding="utf-8").read()

    assert len(pagina.PAGINAS) == 7
    for p in pagina.PAGINAS:
        gerada = os.path.join(RAIZ, "site", "app",
                              p["href"].strip("/").replace("/", os.sep),
                              "page.tsx")
        assert os.path.isfile(gerada), f"{p['href']} nao foi gerada"
        assert p["href"] in fonte, f"{p['href']} fora do nav.ts"


def test_o_exercicio_266_existe_com_explicacao():
    pasta = os.path.join(RAIZ, "exercicios", "48-ecossistema")
    assert os.path.isfile(os.path.join(
        pasta, "266_ecossistema_e_principios.df"))
    assert os.path.isfile(os.path.join(
        pasta, "266_ecossistema_e_principios.md"))
