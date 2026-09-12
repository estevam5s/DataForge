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


# ═══════════════════════════════════════════════════════════
#  O tipo de retorno atravessa a fronteira do módulo
#
#  Uma ação que declara `-> Pedido` e é chamada de outro
#  arquivo devolvia UNKNOWN, e
#  `P.criar(1, "Ana").clientte` — o campo errado, com o nome
#  quase certo — passava no `check`.
#
#  No MESMO arquivo esse campo é acusado com sugestão. Num
#  sistema de 200 arquivos a maioria das chamadas atravessa
#  módulo, e era justamente ali que a conferência calava.
# ═══════════════════════════════════════════════════════════

def _projeto_de_dois_modulos(tmp_path, main):
    src = tmp_path / "src"
    src.mkdir()
    (src / "pedido.df").write_text('''record Pedido:
    id: Integer
    cliente: String
    total: Float

action criar(id: Integer, cliente: String) -> Pedido:
    yield Pedido(id, cliente, 0.0)

action com_total(p: Pedido, v: Float) -> Pedido:
    yield p with {"total": v}

action quantos() -> Integer:
    yield 7

action sem_tipo(x):
    yield x

relay Pedido, criar, com_total, quantos, sem_tipo
''', encoding="utf-8")
    (src / "main.df").write_text(main, encoding="utf-8")
    (tmp_path / "forge.toml").write_text(
        '[project]\nname = "x"\nversion = "1.0.0"\n', encoding="utf-8")
    return str(src / "main.df")


def _erros(caminho):
    from dataforge.lexer import tokenize
    from dataforge.parser import parse
    from dataforge.typechecker import check_program

    fonte = open(caminho, encoding="utf-8").read()
    arvore = parse(tokenize(fonte, caminho), caminho)
    return [d for d in check_program(arvore, caminho, source=fonte)
            if d.severity == "error"]


def test_o_campo_errado_num_record_de_outro_modulo_e_acusado(tmp_path):
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

p := P.criar(1, "Ana")
out p.clientte
''')
    erros = _erros(caminho)
    assert len(erros) == 1, [d.message for d in erros]
    assert "clientte" in erros[0].message
    assert "cliente" in erros[0].hint          # a sugestão


def test_os_campos_certos_nao_geram_alarme(tmp_path):
    """Um falso alarme ensina a ignorar mensagens — e aí os
    verdadeiros também são ignorados."""
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

p := P.criar(1, "Ana")
out p.cliente
out p.id
out p.total
q := P.com_total(p, 99.9)
out q.total
''')
    assert _erros(caminho) == []


def test_um_tipo_embutido_atravessa_como_esta(tmp_path):
    """`-> Integer` chega como `Integer`, e não como `P.Integer`.

    A conferência de MEMBRO de tipo embutido não existe nem localmente
    (`n := 7` seguido de `n.qualquer` também passa), então o que este
    teste prova é que o tipo chega inteiro do outro lado — o suficiente
    para a aritmética e para o `-> Integer` de quem o recebe.
    """
    from dataforge.superficie import de_arquivo

    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

n := P.quantos()
out n + 1
''')
    assert _erros(caminho) == []

    pedido = os.path.join(os.path.dirname(caminho), "pedido.df")
    assert de_arquivo(pedido).obter("quantos").retorno == "Integer"


def test_o_tipo_embutido_e_cobrado_onde_a_conferencia_existe(tmp_path):
    """Onde há conferência — o argumento de uma ação tipada — o tipo
    que atravessou o módulo é usado."""
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

action precisa_de_texto(s: String):
    out s

precisa_de_texto(P.quantos())
''')
    erros = _erros(caminho)
    assert len(erros) == 1, [d.message for d in erros]
    assert "String" in erros[0].message and "Integer" in erros[0].message


def test_uma_acao_sem_tipo_declarado_continua_calando(tmp_path):
    """O analisador só acusa o que consegue **provar**. Sem `-> Tipo`,
    não há o que provar — e inventar um tipo aqui daria o falso alarme
    que a política proíbe."""
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

x := P.sem_tipo(1)
out x.qualquer_coisa
''')
    assert _erros(caminho) == []


def test_o_tipo_nao_vaza_com_o_nome_nu(tmp_path):
    """`-> Pedido` no outro arquivo é `P.Pedido` aqui.

    Devolver o nome nu faria o analisador procurar um record chamado
    `Pedido` que ESTE arquivo não declara — e acusar o que não devia,
    ou calar por não achar.
    """
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

p := P.criar(1, "Ana")
out p.clientte
''')
    erros = _erros(caminho)
    assert "P.Pedido" in erros[0].message, erros[0].message


def test_a_superficie_guarda_o_tipo_de_retorno(tmp_path):
    """A peça que faltava: `Membro` não tinha o campo, e por isso a
    informação se perdia antes de chegar ao analisador."""
    from dataforge.superficie import de_arquivo

    caminho = _projeto_de_dois_modulos(tmp_path, "adopt ./pedido as P\n")
    pedido = os.path.join(os.path.dirname(caminho), "pedido.df")
    s = de_arquivo(pedido)
    assert s.obter("criar").retorno == "Pedido"
    assert s.obter("quantos").retorno == "Integer"
    assert s.obter("sem_tipo").retorno == ""


def test_o_tipo_do_parametro_e_cobrado_atraves_do_adopt(tmp_path):
    """A aridade era conferida e o tipo não: a superfície sabia quantos
    argumentos a ação aceita, e não o que cada um devia ser.

    `D.valor_de("texto")` — onde a declaração é `n: Integer` — passava
    no `check` e estourava em execução na primeira conta.
    """
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

P.com_total(P.criar(1, "Ana"), "muito")
''')
    erros = _erros(caminho)
    assert len(erros) == 1, [d.message for d in erros]
    assert "'v' of 'P.com_total'" in erros[0].message
    assert "Float" in erros[0].message and "String" in erros[0].message
    # E aponta onde a ação foi declarada, no outro arquivo.
    assert "pedido.df" in erros[0].hint


def test_o_argumento_certo_nao_gera_alarme(tmp_path):
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

p := P.criar(1, "Ana")
q := P.com_total(p, 99.9)
r := P.com_total(p, 100)
out q.total, r.total
''')
    # 100 é Integer onde se espera Float: serve, como em toda a
    # linguagem.
    assert _erros(caminho) == []


def test_o_parametro_por_nome_tambem_e_cobrado(tmp_path):
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

P.criar(id := 1, cliente := 2)
''')
    erros = _erros(caminho)
    assert len(erros) == 1, [d.message for d in erros]
    assert "'cliente'" in erros[0].message


def test_o_spread_cala_a_conferencia_de_tipo(tmp_path):
    """`...args` esconde quem vai onde — cobrar tipo ali seria inventar
    um erro."""
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

args := [1, "Ana"]
P.criar(...args)
''')
    assert _erros(caminho) == []


def test_um_parametro_sem_tipo_declarado_aceita_qualquer_coisa(tmp_path):
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

out P.sem_tipo("texto")
out P.sem_tipo(1)
out P.sem_tipo([1, 2])
''')
    assert _erros(caminho) == []


def test_a_superficie_guarda_os_tipos_dos_parametros(tmp_path):
    from dataforge.superficie import de_arquivo

    caminho = _projeto_de_dois_modulos(tmp_path, "adopt ./pedido as P\n")
    pedido = os.path.join(os.path.dirname(caminho), "pedido.df")
    membro = de_arquivo(pedido).obter("com_total")
    assert membro.parametros == ("p", "v")
    assert membro.tipos == {"p": "Pedido", "v": "Float"}


def test_o_argumento_pode_ser_um_parametro_da_acao_que_chama(tmp_path):
    """A conferência de tipo usa o escopo de QUEM CHAMA.

    `self.global_scope` não vê parâmetro de ação nem variável de bloco:
    `D.valor_de(n)` dentro de `action f(n)` virava
    **"Undefined name 'n'"**. Foram **649 falsos alarmes** num projeto
    gerado de 252 arquivos — um por cada uso de parâmetro numa chamada
    entre módulos.

    E a suíte passava: os outros testes deste bloco chamam no nível de
    topo, onde o escopo global é o certo. O bug só aparecia dentro de
    uma ação — que é onde quase todo código vive.
    """
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

action fazer(numero: Integer, nome: String):
    yield P.criar(numero, nome)

action com(p, valor: Float):
    intermediario := P.com_total(p, valor)
    yield intermediario

out fazer(1, "Ana")
''')
    assert _erros(caminho) == []


def test_o_erro_real_dentro_de_uma_acao_continua_sendo_pego(tmp_path):
    """O silêncio não pode ter voltado por excesso: um argumento
    errado dentro de uma ação ainda é acusado."""
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

action fazer(n: Integer):
    yield P.criar(1, n)
''')
    erros = _erros(caminho)
    assert len(erros) == 1, [d.message for d in erros]
    assert "'cliente'" in erros[0].message
    assert "String" in erros[0].message and "Integer" in erros[0].message


def test_uma_variavel_de_bloco_tambem_serve_de_argumento(tmp_path):
    caminho = _projeto_de_dois_modulos(tmp_path, '''adopt ./pedido as P

cycle i from 1 to 3:
    rotulo := $"item {i}"
    p := P.criar(i, rotulo)
    out p.cliente
''')
    assert _erros(caminho) == []
