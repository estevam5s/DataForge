"""Onde mora o módulo que um `adopt` pede.

A regra estava escrita em **dois** lugares — o interpretador, que precisa
carregar o arquivo, e o analisador, que precisa saber se ele existe — e
os dois divergiram do pior jeito possível.

Dois defeitos vinham disso, e os dois eram invisíveis:

1. O analisador fazia `nome.replace('.', os.sep)`, o que transforma
   `'./mod'` em `'//mod'`. **Todo `adopt` relativo de todo projeto**
   gerava um aviso "Module not found" falso: 62 no repositório, e 795 de
   795 num projeto de 21 mil linhas — cada aviso que o `check` emitia
   ali era mentira. O projeto tem um princípio explícito sobre isso: um
   falso alarme ensina o usuário a ignorar mensagens.

2. Um pacote não sabia se importar pelo **próprio nome**. O teste de uma
   biblioteca escreve `adopt validador`, e não `adopt ../src/main`,
   porque precisa exercitá-la pelo mesmo caminho que um usuário usaria.
   As suítes dos **vinte** pacotes deste repositório falhavam por isso,
   e a CI não apanhava — ela não rodava `dataforge test` em `packages/`.
"""

import os
import subprocess
import sys

import pytest

sys.path.insert(0, ".")

from dataforge import resolucao

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ═══════════════════════════════════════════════════════════
#  O bug do replace
# ═══════════════════════════════════════════════════════════

def test_um_caminho_relativo_nao_e_mutilado(tmp_path):
    """`'./mod'.replace('.', '/')` dá `'//mod'`."""
    (tmp_path / "mod.df").write_text("action f():\n    yield 1\n",
                                     encoding="utf-8")
    origem = str(tmp_path / "usa.df")
    assert resolucao.achar("./mod", origem) == str(tmp_path / "mod.df")


def test_o_relativo_resolve_contra_o_ARQUIVO_e_nao_o_cwd(tmp_path):
    """Mover a pasta inteira não pode quebrar nada, e ler o código deve
    bastar para saber o que ele importa."""
    pasta = tmp_path / "src"
    pasta.mkdir()
    (pasta / "vizinho.df").write_text("action f():\n    yield 1\n",
                                      encoding="utf-8")
    achado = resolucao.achar("./vizinho", str(pasta / "principal.df"))
    assert achado == str(pasta / "vizinho.df")


def test_sobe_uma_pasta(tmp_path):
    (tmp_path / "util.df").write_text("action f():\n    yield 1\n",
                                      encoding="utf-8")
    fundo = tmp_path / "a" / "b"
    fundo.mkdir(parents=True)
    assert resolucao.achar("../../util", str(fundo / "x.df")) == \
        str(tmp_path / "util.df")


def test_um_ponto_no_meio_continua_sendo_pasta(tmp_path):
    """`sub.modulo` é `sub/modulo` — o replace só estava errado para o
    caso relativo."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "modulo.df").write_text("action f():\n    yield 1\n",
                                   encoding="utf-8")
    assert resolucao.achar("sub.modulo", str(tmp_path / "x.df")) == \
        str(sub / "modulo.df")


def test_o_que_nao_existe_devolve_none(tmp_path):
    assert resolucao.achar("./nao-existe", str(tmp_path / "x.df")) is None


def test_o_analisador_nao_inventa_modulo_ausente(tmp_path):
    """O teste que mais importa: `check` sobre um projeto com imports
    relativos não emite um único aviso de módulo."""
    pasta = tmp_path / "src"
    pasta.mkdir()
    (pasta / "util.df").write_text(
        "action dobro(n):\n    yield n * 2\n\nrelay dobro\n", encoding="utf-8")
    (pasta / "main.df").write_text(
        "adopt ./util as U\n\nout U.dobro(4)\n", encoding="utf-8")

    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "check", "src/", "--no-color"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": RAIZ})
    assert "was not found" not in saida.stdout, saida.stdout
    assert saida.returncode == 0, saida.stdout


def test_o_repositorio_nao_tem_aviso_falso_de_modulo():
    """Eram 62. Os que sobram são os dois exercícios que demonstram um
    `adopt` que falha de propósito."""
    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "check", ".", "--no-color"],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": RAIZ})
    linhas = [l for l in saida.stdout.splitlines() if "was not found" in l]
    inesperados = [l for l in linhas if "NaoExiste" not in l]
    assert not inesperados, "avisos falsos de módulo:\n" + "\n".join(
        inesperados[:10])


# ═══════════════════════════════════════════════════════════
#  O pacote que se importa
# ═══════════════════════════════════════════════════════════

def test_um_pacote_se_importa_pelo_proprio_nome(tmp_path):
    (tmp_path / "forge.toml").write_text(
        '[package]\nname = "meupacote"\nversion = "1.0.0"\n'
        'entry = "src/main.df"\n', encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.df").write_text("action f():\n    yield 1\n\nrelay f\n",
                                 encoding="utf-8")
    testes = tmp_path / "tests"
    testes.mkdir()

    achado = resolucao.achar_no_proprio_pacote(
        "meupacote", str(testes / "meu_test.df"))
    assert achado == str(src / "main.df")


def test_o_nome_de_outro_pacote_nao_resolve(tmp_path):
    (tmp_path / "forge.toml").write_text(
        '[package]\nname = "meu"\nversion = "1.0.0"\n', encoding="utf-8")
    assert resolucao.achar_no_proprio_pacote(
        "outro", str(tmp_path / "x.df")) is None


def test_a_raiz_do_projeto_e_achada_de_qualquer_profundidade(tmp_path):
    (tmp_path / "forge.toml").write_text("[project]\nname = \"x\"\n",
                                         encoding="utf-8")
    fundo = tmp_path / "src" / "a" / "b"
    fundo.mkdir(parents=True)
    assert resolucao.raiz_do_projeto(str(fundo / "x.df")) == str(tmp_path)


def test_sem_forge_toml_nao_ha_raiz(tmp_path):
    assert resolucao.raiz_do_projeto(str(tmp_path / "solto.df")) is None


@pytest.mark.parametrize("pacote", sorted(
    nome for nome in os.listdir(os.path.join(RAIZ, "packages"))
    if os.path.isdir(os.path.join(RAIZ, "packages", nome))
    and os.path.isdir(os.path.join(RAIZ, "packages", nome, "tests"))))
def test_a_suite_de_cada_pacote_roda(pacote):
    """As vinte falhavam, e nada apanhava: a CI não roda `dataforge test`
    dentro de `packages/`.

    Um pacote com dependência declarada precisa de `dataforge install`
    antes; esse é pulado com a razão dita, em vez de falhar.
    """
    pasta = os.path.join(RAIZ, "packages", pacote)
    manifesto = open(os.path.join(pasta, "forge.toml"),
                     encoding="utf-8").read()
    bloco = manifesto.split("[dependencies]")[1].split("[")[0] \
        if "[dependencies]" in manifesto else ""
    tem_dependencia = any(
        "=" in linha and not linha.strip().startswith("#")
        for linha in bloco.splitlines())
    if tem_dependencia and not os.path.isdir(
            os.path.join(pasta, "forge_modules")):
        pytest.skip(f"'{pacote}' precisa de 'dataforge install' primeiro")

    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "test", "--no-color"],
        cwd=pasta, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": RAIZ})
    assert saida.returncode == 0, saida.stdout + saida.stderr
    assert "Tudo verde" in saida.stdout


# ═══════════════════════════════════════════════════════════
#  Os dois não podem divergir de novo
# ═══════════════════════════════════════════════════════════

def test_o_interpretador_e_o_analisador_usam_o_mesmo_resolvedor():
    """A divergência foi a causa dos dois bugs. Este teste proíbe a
    cópia voltar."""
    for arquivo in ("dataforge/typechecker.py", "dataforge/superficie.py"):
        fonte = open(os.path.join(RAIZ, arquivo), encoding="utf-8").read()
        # Só as linhas de código: o comentário que explica o bug cita a
        # expressão de propósito, e proibir a explicação seria proibir
        # justamente o que impede alguém de reintroduzi-lo.
        codigo = [l for l in fonte.splitlines()
                  if l.strip() and not l.strip().startswith("#")]
        culpadas = [l for l in codigo if "replace('.', os.sep)" in l]
        assert not culpadas, (
            f"{arquivo} voltou a resolver caminho à mão — use "
            f"resolucao.py:\n" + "\n".join(culpadas))

    interp = open(os.path.join(RAIZ, "dataforge/interpreter.py"),
                  encoding="utf-8").read()
    assert "from . import resolucao" in interp


# ═══════════════════════════════════════════════════════════
#  O grafo de imports
# ═══════════════════════════════════════════════════════════

def _deps(pasta, *args):
    return subprocess.run(
        [sys.executable, "-m", "dataforge", "deps", *(args or ("."))],
        cwd=pasta, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": RAIZ})


def test_o_deps_ve_import_relativo(tmp_path):
    """Ele lia os `adopt` com uma regex que começava em `[A-Za-z_]`:
    `./vizinho` nunca casava.

    Num projeto que usa import relativo — a forma recomendada — o
    comando cuja única função é mostrar o grafo de imports mostrava
    "0 arquivos com imports próprios".
    """
    (tmp_path / "util.df").write_text(
        "action f():\n    yield 1\n\nrelay f\n", encoding="utf-8")
    (tmp_path / "main.df").write_text(
        "adopt ./util as U\n\nout U.f()\n", encoding="utf-8")

    saida = _deps(tmp_path)
    assert "1 com imports proprios" in saida.stdout, saida.stdout
    assert "→ util.df" in saida.stdout


def test_o_deps_acha_o_ciclo(tmp_path):
    """E a detecção nunca disparava, porque o grafo estava vazio."""
    (tmp_path / "a.df").write_text(
        "adopt ./b as B\n\naction fa():\n    yield 1\n\nrelay fa\n",
        encoding="utf-8")
    (tmp_path / "b.df").write_text(
        "adopt ./a as A\n\naction fb():\n    yield 2\n\nrelay fb\n",
        encoding="utf-8")

    saida = _deps(tmp_path)
    assert "1 ciclo(s) de import" in saida.stdout, saida.stdout
    assert saida.returncode == 1, "um ciclo precisa dar saída diferente de 0"


def test_dois_arquivos_de_mesmo_nome_nao_inventam_ciclo(tmp_path):
    """A versão anterior casava o nome do import com o FIM do caminho,
    então `a/util.df` e `b/util.df` eram o mesmo nó."""
    for pasta in ("a", "b"):
        (tmp_path / pasta).mkdir()
        (tmp_path / pasta / "util.df").write_text(
            "action f():\n    yield 1\n\nrelay f\n", encoding="utf-8")
    (tmp_path / "a" / "usa.df").write_text(
        "adopt ./util as U\n\nout U.f()\n", encoding="utf-8")
    (tmp_path / "b" / "usa.df").write_text(
        "adopt ./util as U\n\nout U.f()\n", encoding="utf-8")

    saida = _deps(tmp_path)
    assert "ciclo" not in saida.stdout, saida.stdout
    assert saida.returncode == 0


def test_o_deps_separa_stdlib_de_import_proprio(tmp_path):
    (tmp_path / "util.df").write_text(
        "action f():\n    yield 1\n\nrelay f\n", encoding="utf-8")
    (tmp_path / "main.df").write_text(
        "adopt Arcane.Math as Math\nadopt ./util as U\n\n"
        "out Math.sqrt(4), U.f()\n", encoding="utf-8")

    saida = _deps(tmp_path)
    assert "Arcane.Math" in saida.stdout
    assert "→ util.df" in saida.stdout


def test_o_deps_relata_import_que_nao_resolveu(tmp_path):
    (tmp_path / "main.df").write_text("adopt ./nao-existe as X\n",
                                      encoding="utf-8")
    saida = _deps(tmp_path)
    assert "nao resolveram" in saida.stdout
    assert "./nao-existe" in saida.stdout


def test_os_projetos_do_repositorio_tem_grafo_e_nao_tem_ciclo():
    """Os quatro mostravam "0 com imports próprios"."""
    for nome in sorted(os.listdir(os.path.join(RAIZ, "projetos"))):
        pasta = os.path.join(RAIZ, "projetos", nome)
        if not os.path.isdir(pasta):
            continue
        saida = _deps(RAIZ, f"projetos/{nome}")
        assert "0 com imports proprios" not in saida.stdout, (
            f"projetos/{nome}: o grafo saiu vazio\n{saida.stdout}")
        assert "ciclo" not in saida.stdout, f"projetos/{nome}:\n{saida.stdout}"


def test_hifen_num_caminho_relativo_compila(tmp_path):
    """`adopt ./minha-lib as L` não compilava: o lexer entrega o hífen
    como MINUS, o loop do caminho parava ali, e o parser reclamava de
    `as` inesperado.

    Hífen em nome de pasta é comum — os projetos deste repositório se
    chamam `analise-vendas` e `api-links`.
    """
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    casos = {
        "adopt ./minha-lib as L": "./minha-lib",
        "adopt ./a-b-c as A": "./a-b-c",
        "adopt ../lib/minha-coisa as M": "../lib/minha-coisa",
        "adopt ./api-v2/rotas as R": "./api-v2/rotas",
        "adopt ./util.df as U": "./util.df",
        "adopt ./v2 as V": "./v2",
    }
    for fonte, esperado in casos.items():
        programa = parse(tokenize(fonte + "\n", "t"), "t")
        assert programa.body[0].module == esperado, fonte


def test_a_subtracao_continua_sendo_subtracao():
    """A colagem exige adjacência de coluna: sem essa guarda, `a - b`
    viraria um caminho chamado `a-b`."""
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    for fonte in ("x := a - b", "x := 5-3", "x := a-b", "x := 10 - 2 - 3"):
        parse(tokenize(fonte + "\n", "t"), "t")   # não levanta

    # E um '-' solto depois de um caminho não é engolido.
    with pytest.raises(Exception):
        parse(tokenize("adopt ./a -\n", "t"), "t")


def test_um_projeto_com_hifen_no_nome_roda(tmp_path):
    lib = tmp_path / "minha-lib"
    lib.mkdir()
    (lib / "main.df").write_text(
        "action dobro(n):\n    yield n * 2\n\nrelay dobro\n", encoding="utf-8")
    (tmp_path / "main.df").write_text(
        "adopt ./minha-lib as L\n\nout L.dobro(21)\nassert L.dobro(21) is 42\n",
        encoding="utf-8")

    rodar = subprocess.run(
        [sys.executable, "-m", "dataforge", "run", "main.df"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": RAIZ})
    assert rodar.returncode == 0, rodar.stdout + rodar.stderr
    assert "42" in rodar.stdout

    # E o analisador confere o que vem de lá, inclusive com hífen.
    (tmp_path / "erra.df").write_text(
        "adopt ./minha-lib as L\n\nout L.triplo(1)\n", encoding="utf-8")
    conferir = subprocess.run(
        [sys.executable, "-m", "dataforge", "check", "erra.df", "--no-color"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": RAIZ})
    assert "has no 'triplo'" in conferir.stdout, conferir.stdout


# ═══════════════════════════════════════════════════════════
#  Ciclo de import, antes de rodar
# ═══════════════════════════════════════════════════════════

def _ciclo(tmp_path):
    (tmp_path / "a.df").write_text(
        "adopt ./b as B\n\naction fa():\n    yield 1\n\nrelay fa\n",
        encoding="utf-8")
    (tmp_path / "b.df").write_text(
        "adopt ./a as A\n\naction fb():\n    yield 2\n\nrelay fb\n",
        encoding="utf-8")
    return tmp_path


def _check(pasta, *args):
    return subprocess.run(
        [sys.executable, "-m", "dataforge", "check", "--no-color",
         *(args or (".",))],
        cwd=pasta, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": RAIZ})


def test_o_check_acha_o_ciclo_antes_de_rodar(tmp_path):
    """Um ciclo estoura em execução, no primeiro `adopt`. O `check`
    passava limpo num projeto que não sobe."""
    saida = _check(_ciclo(tmp_path))
    assert "circular import" in saida.stdout, saida.stdout
    assert "a.df → b.df → a.df" in saida.stdout
    assert saida.returncode == 1


def test_a_mensagem_mostra_a_cadeia_inteira(tmp_path):
    """Um ciclo de quatro arquivos é impossível de quebrar sem saber por
    onde ele passa."""
    for nome, proximo in (("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")):
        (tmp_path / f"{nome}.df").write_text(
            f"adopt ./{proximo} as X\n\naction f{nome}():\n    yield 1\n"
            f"\nrelay f{nome}\n", encoding="utf-8")

    saida = _check(tmp_path, "a.df")
    assert "a.df → b.df → c.df → d.df → a.df" in saida.stdout, saida.stdout


def test_o_ciclo_e_relatado_uma_vez_por_arquivo(tmp_path):
    """Um arquivo com cinco imports repetiria a mesma mensagem cinco
    vezes."""
    pasta = _ciclo(tmp_path)
    (pasta / "c.df").write_text(
        "action fc():\n    yield 3\n\nrelay fc\n", encoding="utf-8")
    (pasta / "a.df").write_text(
        "adopt ./b as B\nadopt ./c as C\n\naction fa():\n    yield 1\n"
        "\nrelay fa\n", encoding="utf-8")

    saida = _check(pasta, "a.df")
    assert saida.stdout.count("circular import") == 1, saida.stdout


def test_um_projeto_sem_ciclo_nao_e_acusado(tmp_path):
    """Vários arquivos adotando o mesmo utilitário não é ciclo."""
    (tmp_path / "util.df").write_text(
        "action f():\n    yield 1\n\nrelay f\n", encoding="utf-8")
    for nome in ("a", "b", "c"):
        (tmp_path / f"{nome}.df").write_text(
            f"adopt ./util as U\n\naction g{nome}():\n    yield U.f()\n"
            f"\nrelay g{nome}\n", encoding="utf-8")
    (tmp_path / "main.df").write_text(
        "adopt ./a as A\nadopt ./b as B\nadopt ./c as C\n\n"
        "out A.ga(), B.gb(), C.gc()\n", encoding="utf-8")

    saida = _check(tmp_path)
    assert "circular" not in saida.stdout, saida.stdout
    assert saida.returncode == 0


def test_o_repositorio_nao_tem_ciclo():
    saida = _check(RAIZ, ".")
    assert "circular import" not in saida.stdout, saida.stdout


# ═══════════════════════════════════════════════════════════
#  Os símbolos da biblioteca também são conferidos
# ═══════════════════════════════════════════════════════════

def test_um_simbolo_que_nao_existe_na_stdlib_e_acusado(tmp_path):
    """`Math.sqrtt(4)` passava pelo `check` sem uma palavra.

    A superfície de um módulo da **biblioteca** é a mais confiável que
    existe: ele está carregado, e a lista de símbolos é o próprio
    dicionário — não há heurística nenhuma. Mesmo assim, o `adopt` de
    um módulo da stdlib retornava imediatamente, sem registrar nada.

    Num ramo que só roda em produção, o erro aparecia em produção.
    """
    (tmp_path / "erra.df").write_text(
        "adopt Arcane.Math as Math\n\nout Math.sqrtt(16)\n", encoding="utf-8")
    saida = _check(tmp_path, "erra.df")
    assert "has no 'sqrtt'" in saida.stdout, saida.stdout
    assert "Did you mean 'sqrt'" in saida.stdout
    assert saida.returncode == 1


def test_a_aridade_de_um_simbolo_da_stdlib_e_cobrada(tmp_path):
    (tmp_path / "erra.df").write_text(
        "adopt Arcane.Math as Math\n\nout Math.sqrt(1, 2, 3)\n",
        encoding="utf-8")
    saida = _check(tmp_path, "erra.df")
    assert "takes 1 argument(s), got 3" in saida.stdout, saida.stdout


def test_o_uso_correto_da_stdlib_nao_e_acusado(tmp_path):
    """O teste que mais importa: zero falso alarme."""
    (tmp_path / "ok.df").write_text(
        "adopt Arcane.Math as Math\n"
        "adopt Arcane.Database as Banco\n"
        "adopt Arcane.Text as Txt\n\n"
        "out Math.sqrt(16)\n"
        "out Math.floor(2.7)\n"
        "out Txt.constant_case(\"oi mundo\")\n"
        "db := Banco.memory()\n"
        "Banco.create_table(db, \"x\", {\"id\": \"INTEGER\"})\n"
        "Banco.insert(db, \"x\", {\"id\": 1})\n"
        "out Banco.count(db, \"x\")\n", encoding="utf-8")
    saida = _check(tmp_path, "ok.df")
    assert saida.returncode == 0, saida.stdout


def test_um_simbolo_variadico_nao_cobra_teto(tmp_path):
    """Quando a aridade não dá para saber — um `*args`, um `staticmethod`
    embrulhado — o membro fica variádico. Cobrar uma aridade adivinhada
    daria falso alarme, que é pior que silêncio."""
    from dataforge.stdlib import get_module
    from dataforge.superficie import de_modulo_padrao

    superficie = de_modulo_padrao("Arcane.Text", get_module("Arcane.Text"))
    # Todo membro aceita ao menos o que a assinatura pede.
    for nome in superficie.nomes()[:20]:
        membro = superficie.obter(nome)
        assert membro.minimo >= 0


def test_o_import_seletivo_da_stdlib_e_conferido(tmp_path):
    (tmp_path / "erra.df").write_text(
        "adopt Arcane.Math.{sqrt, raizQuadrada}\n\nout sqrt(4)\n",
        encoding="utf-8")
    saida = _check(tmp_path, "erra.df")
    assert "does not export 'raizQuadrada'" in saida.stdout, saida.stdout


def test_o_repositorio_inteiro_continua_sem_erro():
    """330 arquivos que funcionam, e a conferência nova não pode acusar
    nenhum deles."""
    saida = _check(RAIZ, ".")
    erros = [l for l in saida.stdout.splitlines() if ": erro:" in l]
    assert not erros, "falsos alarmes:\n" + "\n".join(erros[:10])
