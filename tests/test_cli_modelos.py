"""
Testes dos modelos de projeto e das correções que eles revelaram.

Um `dataforge new` é a primeira coisa que alguém faz com a linguagem.
Um modelo que não compila, ou cujos testes falham, faz a pessoa achar
que errou alguma coisa — e desistir.
"""

import os
import subprocess
import sys
import tempfile

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.interpreter import Interpreter                    # noqa: E402
from dataforge.lexer import tokenize                             # noqa: E402
from dataforge.modelos import MODELOS                            # noqa: E402
from dataforge.parser import parse                               # noqa: E402


def rodar(fonte):
    import io
    from contextlib import redirect_stdout
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(fonte)))
    return buffer.getvalue().strip()


# ── Os modelos ───────────────────────────────────────────────

def test_ha_modelos_para_os_casos_principais():
    for esperado in ("cli", "api", "web", "data", "lib", "oop",
                     "script", "test"):
        assert esperado in MODELOS


@pytest.mark.parametrize("chave", sorted(MODELOS))
def test_modelo_esta_completo(chave):
    """Todo projeto precisa de manifesto, código, teste e README."""
    modelo = MODELOS[chave]
    arquivos = modelo["files"]

    for campo in ("name", "description", "icon", "files"):
        assert modelo.get(campo), f"{chave} sem {campo}"

    assert "forge.toml" in arquivos, f"{chave} sem manifesto"
    assert "README.md" in arquivos, f"{chave} sem README"
    assert ".gitignore" in arquivos, f"{chave} sem .gitignore"
    assert any(a.startswith("src/") for a in arquivos), f"{chave} sem src/"
    assert any(a.startswith("tests/") for a in arquivos), f"{chave} sem testes"


@pytest.mark.parametrize("chave", sorted(MODELOS))
def test_todo_arquivo_df_do_modelo_compila(chave):
    """Um modelo que não compila é pior que nenhum."""
    falhas = []
    for relativo, conteudo in MODELOS[chave]["files"].items():
        if not relativo.endswith(".df"):
            continue
        texto = conteudo.replace("{name}", "prova").replace("{version}", "1.0.0")
        try:
            parse(tokenize(texto))
        except Exception as erro:
            falhas.append(f"{relativo}: {str(erro).splitlines()[0][:90]}")
    assert not falhas, f"{chave} não compila:\n  " + "\n  ".join(falhas)


@pytest.mark.parametrize("chave", sorted(MODELOS))
def test_o_manifesto_declara_a_versao_certa(chave):
    from dataforge import __version__
    manifesto = MODELOS[chave]["files"]["forge.toml"]
    maior_menor = ".".join(__version__.split(".")[:2])
    assert f'dataforge = ">={maior_menor}"' in manifesto, (
        f"{chave} exige uma versão que não é a atual")


@pytest.mark.slow
@pytest.mark.parametrize("chave", sorted(MODELOS))
def test_o_projeto_criado_passa_nos_proprios_testes(chave):
    """O teste que mais importa: o projeto gerado funciona de verdade.

    Roda `dataforge new` e depois `dataforge test` na pasta criada,
    exatamente como um usuário faria.
    """
    with tempfile.TemporaryDirectory() as pasta:
        criar = subprocess.run(
            [sys.executable, "-m", "dataforge", "new", chave, "prova"],
            cwd=pasta, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONPATH": RAIZ, "NO_COLOR": "1"},
            timeout=120)
        assert criar.returncode == 0, criar.stdout + criar.stderr

        projeto = os.path.join(pasta, "prova")
        assert os.path.isdir(projeto), "a pasta não foi criada"

        testar = subprocess.run(
            [sys.executable, "-m", "dataforge", "test", "tests/"],
            cwd=projeto, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONPATH": RAIZ, "NO_COLOR": "1"},
            timeout=120)
        assert testar.returncode == 0, (
            f"os testes do modelo '{chave}' falharam:\n"
            + testar.stdout + testar.stderr)


# ── Campo declarado com padrão mutável ───────────────────────

def test_cada_instancia_tem_a_propria_lista():
    """'itens: Cluster := []' compartilhava a lista entre instâncias.

    O literal é avaliado uma vez, na declaração do blueprint. Sem copiar
    no spawn, o append de uma instância aparecia em todas — a armadilha
    do argumento mutável padrão do Python, sem justificativa nenhuma
    aqui.
    """
    saida = rodar('''
blueprint Caixa:
    itens: Cluster := []

    action por(x):
        self.itens.append(x)

a := spawn Caixa()
b := spawn Caixa()
a.por(1)
out len(a.itens), len(b.itens)''')
    assert saida == "1 0"


def test_cada_instancia_tem_o_proprio_vault():
    saida = rodar('''
blueprint Registro:
    contagem: Vault := {}

    action marcar(chave):
        self.contagem[chave] := 1

a := spawn Registro()
b := spawn Registro()
a.marcar("x")
out len(a.contagem), len(b.contagem)''')
    assert saida == "1 0"


def test_padrao_imutavel_continua_compartilhado_sem_problema():
    """Copiar número e texto seria desperdício — eles não mudam."""
    saida = rodar('''
blueprint Contador:
    valor: Integer := 10
    nome: String := "padrão"

a := spawn Contador()
b := spawn Contador()
a.valor := 99
out a.valor, b.valor, b.nome''')
    assert saida == "99 10 padrão"


# ── sorted com chave ─────────────────────────────────────────

def test_sorted_aceita_uma_acao_como_criterio():
    """Sem a chave, ordenar vaults falhava com a mensagem do Python."""
    saida = rodar('''
itens := [{"n": "p", "b": 10}, {"n": "g", "b": 900}, {"n": "m", "b": 100}]
out sorted(itens, lambda e => -e["b"])[0]["n"]''')
    assert saida == "g"


def test_sorted_sem_chave_continua_igual():
    assert rodar("out sorted([3, 1, 2])") == "[1, 2, 3]"


def test_sorted_com_reverse_continua_igual():
    assert rodar("out sorted([3, 1, 2], void, yes)") == "[3, 2, 1]"


def test_sorted_por_tamanho_de_texto():
    saida = rodar('out sorted(["banana", "ai", "casa"], lambda p => len(p))')
    assert saida == "[ai, casa, banana]"


def test_sorted_com_criterio_que_nao_e_acao_explica_o_que_fazer():
    from dataforge.errors import DataForgeError
    with pytest.raises(DataForgeError) as capturado:
        rodar('out sorted([1, 2], "não é ação")')
    assert "lambda" in str(capturado.value)


# ── 'trigger' levanta TriggerError ───────────────────────────

def test_trigger_e_capturado_por_handle_trigger_error():
    """Foi um erro nos modelos: 'handle RuntimeError' não pega 'trigger'."""
    saida = rodar('''
action falhar():
    trigger "boom"

monitor:
    falhar()
handle TriggerError as e:
    out "peguei:", e.message''')
    assert saida == "peguei: boom"


@pytest.mark.parametrize("chave", sorted(MODELOS))
def test_nenhum_modelo_usa_o_handle_errado_para_trigger(chave):
    for relativo, conteudo in MODELOS[chave]["files"].items():
        if not relativo.endswith(".df"):
            continue
        if "trigger " in conteudo:
            assert "handle RuntimeError" not in conteudo, (
                f"{chave}/{relativo}: 'trigger' levanta TriggerError")


# ── Comandos de análise ──────────────────────────────────────

def _rodar_cli(*argumentos, cwd=None):
    """Roda a CLI como um usuário rodaria, e devolve (código, saída)."""
    resultado = subprocess.run(
        [sys.executable, "-m", "dataforge", *argumentos],
        cwd=cwd or RAIZ, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": RAIZ, "NO_COLOR": "1"},
        timeout=180)
    return resultado.returncode, resultado.stdout + resultado.stderr


@pytest.mark.parametrize("comando", ["stats", "profile", "fix"])
def test_comando_esta_no_catalogo_de_ajuda(comando):
    from dataforge.cli import COMANDOS
    assert comando in COMANDOS


@pytest.mark.slow
def test_stats_conta_o_que_existe():
    codigo, saida = _rodar_cli("stats", "exercicios/22-web-kiln")
    assert codigo == 0, saida
    assert "arquivo(s) .df" in saida
    assert "ações" in saida
    assert "linhas" in saida


@pytest.mark.slow
def test_stats_sem_arquivo_avisa_em_vez_de_estourar():
    with tempfile.TemporaryDirectory() as vazio:
        codigo, saida = _rodar_cli("stats", vazio)
        assert codigo == 1
        assert "Nenhum arquivo" in saida


@pytest.mark.slow
def test_profile_mede_por_acao():
    """O tempo próprio não pode passar de 100% — uma ação recursiva
    tem o tempo das chamadas internas dentro do próprio, e somar tudo
    dava 207% na primeira versão."""
    with tempfile.NamedTemporaryFile("w", suffix=".df", delete=False,
                                     encoding="utf-8") as f:
        f.write('''action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)

out fib(15)
''')
        caminho = f.name

    try:
        codigo, saida = _rodar_cli("profile", caminho)
        assert codigo == 0, saida
        assert "fib" in saida
        assert "próprio" in saida

        # Nenhuma fatia pode passar de 100%.
        import re
        for fatia in re.findall(r"(\d+\.\d)%", saida):
            assert float(fatia) <= 100.5, f"fatia impossível: {fatia}%"
    finally:
        os.unlink(caminho)


@pytest.mark.slow
def test_profile_sem_arquivo_explica():
    codigo, saida = _rodar_cli("profile")
    assert codigo == 1
    assert "informe o arquivo" in saida


@pytest.mark.slow
def test_fix_dry_run_nao_escreve():
    """'--dry-run' que escrevesse seria o pior tipo de bug: silencioso."""
    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "torto.df")
        # Espaçamento fora do padrão, para o formatador ter o que fazer.
        original = 'x:=1\nout    x\n'
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(original)

        codigo, saida = _rodar_cli("fix", "--dry-run", pasta)
        assert codigo == 0, saida
        assert open(caminho, encoding="utf-8").read() == original, (
            "--dry-run não pode escrever no arquivo")


@pytest.mark.slow
def test_fix_formata_de_verdade_sem_dry_run():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "torto.df")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write('x:=1\nout    x\n')

        codigo, _ = _rodar_cli("fix", pasta)
        assert codigo == 0
        assert open(caminho, encoding="utf-8").read() != 'x:=1\nout    x\n'


def test_nenhum_modelo_crava_caminho_de_um_sistema_so():
    """O modelo 'data' gravava o banco em '/tmp/prova.db'.

    Funcionava no Mac e no Linux e falhava no Windows, que não tem essa
    pasta. O primeiro programa que alguém roda na linguagem não é lugar
    de aprender isso — e um modelo é copiado, então o erro se
    multiplica.

    A forma certa é `IO.join(OS.temp_dir(), ...)`, que pergunta ao
    sistema.
    """
    ruins = []
    for chave, modelo in sorted(MODELOS.items()):
        for nome, conteudo in modelo.get("files", {}).items():
            if not isinstance(conteudo, str):
                continue
            for numero, linha in enumerate(conteudo.split("\n"), 1):
                if linha.lstrip().startswith("//"):
                    continue
                for cravado in ('"/tmp/', "'/tmp/", '"/var/', '"/usr/',
                                '"C:\\\\', '"/home/', '"~/'):
                    if cravado in linha:
                        ruins.append(f"{chave}/{nome}:{numero}: {linha.strip()}")
    assert not ruins, (
        "modelo com caminho de um sistema só — use IO.join(OS.temp_dir(), …):\n"
        + "\n".join(ruins))
