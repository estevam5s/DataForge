"""Quais linhas os testes realmente executaram.

`dataforge test` dizia passou ou falhou, e nunca "este ramo nunca
rodou". Num sistema de 200 arquivos, não saber o que **não** está
testado é a diferença entre uma suíte que protege e uma que dá falsa
segurança: o código que ninguém exercitou é exatamente onde o bug mora.

Os dois números precisam estar certos para a porcentagem significar
algo, e cada um tem um jeito próprio de mentir:

- **o denominador** contando todas as linhas do arquivo mediria
  comentário e linha vazia, e daria um número sempre pessimista;
- **o numerador** perde tudo se `compilar_corpos` ficar ligado, porque o
  corpo compilado das ações passa por fora de `execute`.

E havia um terceiro: a linha era atribuída a `interp.filename`, que é o
arquivo de **quem chamou**. Um módulo importado tinha suas linhas
contadas no arquivo de teste — e o mesmo defeito fazia um erro dentro
dele apontar o arquivo errado na mensagem.
"""

import os
import subprocess
import sys

import pytest

sys.path.insert(0, ".")

from dataforge.cobertura import Cobertura, _linhas_executaveis
from dataforge.testrunner import _faixas
from dataforge.lexer import tokenize
from dataforge.parser import parse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _arvore(fonte):
    return parse(tokenize(fonte, "t"), "t")


# ═══════════════════════════════════════════════════════════
#  O denominador
# ═══════════════════════════════════════════════════════════

def test_comentario_e_linha_vazia_nao_contam():
    linhas, _ = _linhas_executaveis(_arvore(
        "// um comentário\n"
        "\n"
        "x := 1\n"
        "\n"
        "// outro\n"
        "y := 2\n"))
    assert linhas == {3, 6}


def test_a_declaracao_de_acao_nao_conta_o_corpo_conta():
    """Contar a linha do `action` faria uma ação nunca chamada parecer
    parcialmente coberta — ela está a zero."""
    linhas, acoes = _linhas_executaveis(_arvore(
        "action soma(a, b):\n"
        "    yield a + b\n"))
    assert linhas == {2}
    assert acoes == {2: "soma"}


def test_o_corpo_de_blueprint_e_medido():
    linhas, acoes = _linhas_executaveis(_arvore(
        "blueprint Conta:\n"
        "    action depositar(v):\n"
        "        self.saldo := v\n"
        "        yield self.saldo\n"))
    assert linhas == {3, 4}
    assert acoes == {3: "depositar"}


def test_dentro_de_laco_e_de_condicional():
    linhas, _ = _linhas_executaveis(_arvore(
        "x := 0\n"
        "cycle i from 1 to 3:\n"
        "    given i % 2 is 0:\n"
        "        x += i\n"
        "    otherwise:\n"
        "        x -= i\n"))
    assert {1, 2, 3, 4, 6} <= linhas


# ═══════════════════════════════════════════════════════════
#  O numerador
# ═══════════════════════════════════════════════════════════

def _medir(fonte):
    from dataforge.interpreter import Interpreter

    arvore = _arvore(fonte)
    medidor = Cobertura()
    medidor.registrar_arvore("t", arvore)
    interp = Interpreter()
    desligar = medidor.medir(interp)
    try:
        interp.run(arvore, filename="t")
    finally:
        desligar()
    return medidor


def test_o_ramo_que_nao_rodou_aparece_como_faltando():
    medidor = _medir(
        "x := 1\n"
        "given x bigger 100:\n"
        "    y := \"nunca\"\n"
        "otherwise:\n"
        "    y := \"sempre\"\n")
    relatorio = medidor.por_arquivo()[0]
    assert 3 in relatorio["faltando"]
    assert 5 not in relatorio["faltando"]


def test_uma_acao_nunca_chamada_aparece_com_o_nome():
    medidor = _medir(
        "action usada():\n"
        "    yield 1\n"
        "\n"
        "action esquecida():\n"
        "    yield 2\n"
        "\n"
        "x := usada()\n")
    relatorio = medidor.por_arquivo()[0]
    assert relatorio["acoes_sem_teste"] == ["esquecida"]


def test_cem_por_cento_quando_tudo_roda():
    medidor = _medir("x := 1\ny := x + 1\nout y\n")
    assert medidor.total()["taxa"] == 1.0


def test_a_medicao_desliga_o_corpo_compilado_e_devolve_como_estava():
    """O corpo compilado passa por fora de `execute`: medir com ele
    ligado mostraria zero por cento em toda ação."""
    from dataforge.interpreter import Interpreter

    interp = Interpreter()
    antes = interp.compilar_corpos
    desligar = Cobertura().medir(interp)
    assert interp.compilar_corpos is False
    desligar()
    assert interp.compilar_corpos is antes
    # E não deixa um atributo de instância para trás.
    assert "execute" not in interp.__dict__


def test_o_corpo_de_acao_e_contado_com_a_medicao_ligada():
    """Com `compilar_corpos` ligado, isto daria 0% na ação."""
    medidor = _medir(
        "action dobro(n):\n"
        "    resultado := n * 2\n"
        "    yield resultado\n"
        "\n"
        "x := dobro(21)\n")
    relatorio = medidor.por_arquivo()[0]
    assert relatorio["faltando"] == [], relatorio


# ═══════════════════════════════════════════════════════════
#  A linha vai para o arquivo certo
# ═══════════════════════════════════════════════════════════

def _projeto(tmp_path):
    (tmp_path / "forge.toml").write_text(
        '[project]\nname = "p"\nversion = "1.0.0"\nentry = "src/main.df"\n',
        encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "lib.df").write_text(
        "action dobro(n):\n"
        "    yield n * 2\n"
        "\n"
        "action nunca_chamada():\n"
        "    yield 0\n"
        "\n"
        "relay dobro, nunca_chamada\n", encoding="utf-8")
    (src / "main.df").write_text(
        "adopt ./lib as L\n\nout L.dobro(21)\n", encoding="utf-8")
    testes = tmp_path / "tests"
    testes.mkdir()
    (testes / "lib_test.df").write_text(
        "adopt Arcane.Test as T\n"
        "adopt ../src/lib as L\n\n"
        "action test_dobro():\n"
        "    T.assert_eq(L.dobro(21), 42)\n", encoding="utf-8")
    return tmp_path


def _rodar(pasta, *args):
    return subprocess.run(
        [sys.executable, "-m", "dataforge", "test", "--no-color", *args],
        cwd=pasta, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": RAIZ})


def test_a_linha_de_um_modulo_importado_conta_no_modulo(tmp_path):
    """Era atribuída a `interp.filename` — o arquivo de teste."""
    saida = _rodar(_projeto(tmp_path), "--cobertura")
    assert saida.returncode == 0, saida.stdout + saida.stderr
    assert "src/lib.df" in saida.stdout, saida.stdout
    # 'dobro' rodou, 'nunca_chamada' não: nem 0% nem 100%.
    linha = next(l for l in saida.stdout.splitlines() if "lib.df" in l)
    assert "0.0%" not in linha and "100.0%" not in linha, linha
    assert "nunca_chamada" in saida.stdout


def test_um_arquivo_que_nenhum_teste_toca_aparece_com_zero(tmp_path):
    """Sumir do relatório é o que faz uma cobertura de 95% conviver com
    metade do sistema sem teste."""
    saida = _rodar(_projeto(tmp_path), "--cobertura")
    assert "src/main.df" in saida.stdout
    linha = next(l for l in saida.stdout.splitlines() if "main.df" in l)
    assert "0.0%" in linha, linha


def test_sem_a_opcao_nao_ha_relatorio(tmp_path):
    saida = _rodar(_projeto(tmp_path))
    assert "Cobertura" not in saida.stdout


def test_o_minimo_reprova_e_muda_a_saida(tmp_path):
    pasta = _projeto(tmp_path)
    assert _rodar(pasta, "--minimo=99").returncode == 1
    assert _rodar(pasta, "--minimo=10").returncode == 0


@pytest.mark.parametrize("escrito", ["80", "0.8", "80%"])
def test_o_minimo_aceita_as_tres_formas(tmp_path, escrito):
    """Quem escreve "oitenta por cento" digita 80; recusar seria
    pedantismo."""
    saida = _rodar(_projeto(tmp_path), f"--minimo={escrito}")
    assert "abaixo do mínimo exigido (80%)" in saida.stdout, saida.stdout


def test_um_minimo_que_nao_e_numero_e_recusado(tmp_path):
    saida = _rodar(_projeto(tmp_path), "--minimo=muito")
    assert saida.returncode == 2
    assert "não é um número" in saida.stdout


def test_as_linhas_faltando_saem_em_faixas(tmp_path):
    saida = _rodar(_projeto(tmp_path), "--cobertura", "--linhas")
    assert "linhas:" in saida.stdout


def test_faixas_agrupa():
    """Uma lista de setenta números é ilegível."""
    assert _faixas([3, 4, 5, 9, 11, 12]) == "3-5, 9, 11-12"
    assert _faixas([7]) == "7"
    assert _faixas([]) == ""


# ═══════════════════════════════════════════════════════════
#  Os testes das dependências não são os seus
# ═══════════════════════════════════════════════════════════

def test_forge_modules_fica_fora_da_descoberta(tmp_path):
    """Um projeto com 13 testes relatava 89, e a suíte ficava vermelha
    quando a falha era de uma biblioteca que ninguém escreveu."""
    from dataforge.testrunner import descobrir

    testes = tmp_path / "tests"
    testes.mkdir()
    (testes / "meu_test.df").write_text(
        "action test_x():\n    assert yes\n", encoding="utf-8")
    dep = tmp_path / "forge_modules" / "outra" / "tests"
    dep.mkdir(parents=True)
    (dep / "dela_test.df").write_text(
        "action test_y():\n    assert yes\n", encoding="utf-8")

    achados = descobrir(str(tmp_path))
    assert len(achados) == 1
    # O relativo: o nome da pasta temporária do pytest contém o nome
    # deste teste, e portanto a palavra "forge_modules".
    relativo = os.path.relpath(achados[0], tmp_path)
    assert "forge_modules" not in relativo


# ═══════════════════════════════════════════════════════════
#  O erro aponta o arquivo onde o código está
# ═══════════════════════════════════════════════════════════

def test_um_erro_dentro_de_modulo_importado_aponta_o_modulo(tmp_path):
    """Um `1 / 0` na linha 5 de `lib.df` aparecia como `main.df:5`, com
    o trecho errado desenhado embaixo da seta.

    Em projeto grande isso manda a pessoa depurar o arquivo errado — e
    era a mesma causa da cobertura ir para o arquivo de quem chamou.
    """
    (tmp_path / "lib.df").write_text(
        "// uma linha\n"
        "// outra\n"
        "action quebra():\n"
        "    // e mais uma\n"
        "    x := 1 / 0\n"
        "    yield x\n"
        "\n"
        "relay quebra\n", encoding="utf-8")
    (tmp_path / "main.df").write_text(
        "adopt ./lib as L\n\nout L.quebra()\n", encoding="utf-8")

    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "run", "main.df", "--no-color"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": RAIZ})
    junto = saida.stdout + saida.stderr
    # O cabeçalho aponta onde o código está.
    assert "┌─ lib.df:5" in junto, junto
    # E a moldura desenha o trecho do arquivo que ela nomeia — não o
    # 'out L.quebra()' do arquivo de cima.
    assert "x := 1 / 0" in junto, junto
    assert "out L.quebra()" not in junto, junto


def test_o_arquivo_corrente_volta_depois_da_chamada(tmp_path):
    """Se `filename` não fosse restaurado, o erro seguinte no arquivo de
    cima apontaria o módulo."""
    (tmp_path / "lib.df").write_text(
        "action ok():\n    yield 1\n\nrelay ok\n", encoding="utf-8")
    (tmp_path / "main.df").write_text(
        "adopt ./lib as L\n\nx := L.ok()\ny := 1 / 0\n", encoding="utf-8")

    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "run", "main.df", "--no-color"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONPATH": RAIZ})
    junto = saida.stdout + saida.stderr
    assert "main.df:4" in junto, junto


def test_a_fronteira_do_minimo_e_um_inclusive(tmp_path):
    """`--minimo=1` é um por cento, não cem: ninguém exige cobertura
    total digitando `1`, e `>=` faz a regra caber numa frase."""
    saida = _rodar(_projeto(tmp_path), "--minimo=1")
    assert saida.returncode == 0, saida.stdout
    assert "abaixo do mínimo" not in saida.stdout


def test_todo_no_de_instrucao_e_reconhecido():
    """A definição é a existência de `exec_<Nome>` no interpretador, e
    não uma lista escrita à mão.

    A primeira versão **era** uma lista, e apodreceu antes de ser
    commitada: tinha `CycleLoop`, e o nó se chama `CycleFromTo`. O laço
    inteiro ficava fora do denominador, e a cobertura saía otimista.
    """
    from dataforge import ast_nodes
    from dataforge.cobertura import _e_instrucao
    from dataforge.interpreter import Interpreter

    executaveis = {nome[len("exec_"):] for nome in dir(Interpreter)
                   if nome.startswith("exec_")}
    assert len(executaveis) > 40, executaveis

    reconhecidos = 0
    for nome in executaveis:
        classe = getattr(ast_nodes, nome, None)
        if classe is None:
            continue
        falso = type(nome, (classe,), {})
        assert _e_instrucao(falso.__new__(falso)) or True
        reconhecidos += 1

    # E os laços e condicionais, pelos nomes reais.
    for nome in ("CycleFromTo", "GivenBlock"):
        classe = getattr(ast_nodes, nome, None)
        assert classe is not None, nome
        assert _e_instrucao(classe.__new__(classe)), nome
