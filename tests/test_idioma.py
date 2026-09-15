"""A camada de idioma.

O runtime falava inglês e a CLI falava português: `interpreter.py` tinha
234 mensagens em inglês contra 55 em português, e `cli.py` o inverso —
200 contra 15. Quem escreve em pt-BR recebia `dataforge check` em
português e o erro de execução em inglês, na mesma sessão.

Estes testes cobram as três coisas que uma camada de tradução estraga
quando está errada: um molde com campo não preenchido, o texto que ela
**não** devia tocar, e a cobertura — que é o número sem o qual a lista
para de crescer, porque o que falta continua saindo em inglês legível.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge import idioma as mod_idioma           # noqa: E402
from dataforge.errors import DataForgeError          # noqa: E402
from dataforge.interpreter import Interpreter        # noqa: E402
from dataforge.lexer import tokenize                 # noqa: E402
from dataforge.parser import parse                   # noqa: E402


@pytest.fixture
def em_portugues(monkeypatch):
    monkeypatch.setenv("DF_IDIOMA", "pt")
    return "pt"


@pytest.fixture
def em_ingles(monkeypatch):
    monkeypatch.setenv("DF_IDIOMA", "en")
    return "en"


#: Programas que falham, um por família de erro. É o mesmo corpus que
#: mediu o vazamento de tipo do Python.
CORPUS = [
    'out naoDefinido',
    'v := {"a":1}\nout v["b"]',
    'out [1,2][9]',
    'out 1/0',
    'action f(a,b):\n    yield a\nout f(1)',
    'action f(a):\n    yield a\nout f(1,2,3)',
    'no := 1',
    'record P:\n    x: Integer\np := P(1)\nout p.zz',
    'record P:\n    x: Integer\np := P(1)\nout p.zz()',
    'record P:\n    x: Integer\np := P(1)\np.x := 2',
    'blueprint B:\n    action m():\n        yield 1\nb := spawn B()\nout b.zz',
    'out 5()',
    'cycle x in 5:\n    out x',
    'x := 1\nout x.y',
    'enum E:\n    A\nout E.Z',
    'out len(42)',
    'out "a" + void',
    'steady C := 1\nC := 2',
    'x := := 1',
    'given yes\n    out 1',
    'out void.x',
    'out "x" * "y"',
    'out [1] - [2]',
    'adopt Arcane.Math as M\nout M.sqrt("a")',
]


def _erros_do_corpus():
    """Os erros que o corpus levanta, um por programa."""
    saida = []
    for fonte in CORPUS:
        try:
            interp = Interpreter()
            with redirect_stdout(io.StringIO()):
                interp.run(parse(tokenize(fonte, "c.df"), "c.df"))
        except DataForgeError as erro:
            saida.extend([erro] + list(getattr(erro, "outros", ())))
        except BaseException:
            pass
    return saida


# ── O que a tradução não pode estragar ─────────────────────

def test_nenhum_molde_fica_com_campo_nao_preenchido(em_portugues):
    """`'{n}' não está definido.` com o `{n}` literal na tela é pior que
    a mensagem em inglês: além de não ajudar, parece defeito da
    linguagem. Acontece quando o grupo do padrão e o campo do molde
    deixam de concordar, e nada além de um teste denuncia.
    """
    # Procura o CAMPO do molde, e não qualquer chave: as mensagens
    # contêm chaves de propósito — `registro with {'x': valor}` e
    # `$"Ola, {nome}"` são sintaxe da linguagem dentro de uma dica, e
    # um teste que reprovasse nelas seria ruído.
    import re
    campos = set()
    for tabela in (mod_idioma.INTEIRAS, mod_idioma.PEDACOS):
        for _, molde in tabela:
            campos.update(re.findall(r"\{(\w+)\}", molde))

    vazando = []
    for erro in _erros_do_corpus():
        desenho = erro.render(color=False)
        for campo in sorted(campos):
            if "{" + campo + "}" in desenho:
                vazando.append(f"{{{campo}}} em: {desenho.splitlines()[0]}")
    assert not vazando, "molde não preenchido:\n  " + "\n  ".join(vazando)


def test_o_relatorio_mantem_a_forma_em_portugues(em_portugues):
    """Cabeçalho, local e trecho continuam onde estavam."""
    fonte = 'v := {"a": 1}\nout v["b"]\n'
    with pytest.raises(DataForgeError) as capturado:
        interp = Interpreter()
        with redirect_stdout(io.StringIO()):
            interp.run(parse(tokenize(fonte, "t.df"), "t.df"))
    desenho = capturado.value.render(color=False,
                                     source_lines=fonte.splitlines())
    assert "erro[DF0602]" in desenho
    assert "┌─" in desenho
    assert 'out v["b"]' in desenho
    assert "nota:" in desenho
    assert "dica:" in desenho
    # e o texto e portugues
    assert "não está neste vault" in desenho


def test_nenhuma_traducao_reintroduz_tipo_do_python(em_portugues):
    """A tradução passa depois de `_traduzir_tipos`. Um molde escrito com
    `int` ou `dict` desfaria aquele trabalho pelas costas.
    """
    import re
    proibidos = ("NoneType", "bytearray", "dict", "list", "tuple",
                 "frozenset", "int", "str", "float", "bool", "bytes")
    culpados = []
    for erro in _erros_do_corpus():
        desenho = erro.render(color=False).split("│")[0]
        for p in proibidos:
            if re.search(r"\b" + p + r"\b", desenho):
                culpados.append(f"{p!r} em: {desenho.splitlines()[0]}")
    assert not culpados, culpados


# ── Os dois idiomas ────────────────────────────────────────

def test_o_padrao_e_portugues(monkeypatch):
    monkeypatch.delenv("DF_IDIOMA", raising=False)
    assert mod_idioma.atual() == "pt"


@pytest.mark.parametrize("valor,esperado", [
    ("en", "en"), ("EN", "en"), ("en_US", "en"), ("english", "en"),
    ("pt", "pt"), ("pt-BR", "pt"), ("", "pt"), ("qualquer", "pt"),
])
def test_df_idioma_e_lido_com_tolerancia(monkeypatch, valor, esperado):
    monkeypatch.setenv("DF_IDIOMA", valor)
    assert mod_idioma.atual() == esperado


def test_em_ingles_o_texto_sai_como_nasceu(em_ingles):
    fonte = 'v := {"a": 1}\nout v["b"]\n'
    with pytest.raises(DataForgeError) as capturado:
        interp = Interpreter()
        with redirect_stdout(io.StringIO()):
            interp.run(parse(tokenize(fonte, "t.df"), "t.df"))
    desenho = capturado.value.render(color=False)
    assert "Key \"b\" is not in this vault." in desenho
    assert "não está" not in desenho


def test_message_nao_e_traduzido(em_portugues):
    """A decisão que mantém a suíte e os programas em pé.

    `e.message` é o que um `handle` compara e o que 2600 testes comparam.
    Traduzir ali mudaria o comportamento de programa já escrito — e a
    informação que interessa a um programa é a identidade do erro, não a
    redação dela.
    """
    fonte = 'v := {"a": 1}\nout v["b"]\n'
    with pytest.raises(DataForgeError) as capturado:
        interp = Interpreter()
        with redirect_stdout(io.StringIO()):
            interp.run(parse(tokenize(fonte, "t.df"), "t.df"))
    assert capturado.value.message == 'Key "b" is not in this vault.'


def test_o_que_nao_tem_traducao_sai_em_ingles(em_portugues):
    """O fallback. Um catálogo incompleto que levantasse, ou devolvesse a
    chave crua, seria pior que o inglês.
    """
    assert mod_idioma.traduzir("Some message nobody translated yet") == \
        "Some message nobody translated yet"


# ── A medida ───────────────────────────────────────────────

def test_a_cobertura_do_catalogo_nao_regride():
    """O número que faz a lista crescer.

    Sem medida, uma camada de idioma fica pela metade sem ninguém
    perceber: o que falta continua saindo em inglês legível, que é o
    fallback certo e também o que esconde o buraco.

    **Ao traduzir mais mensagens, suba o piso.** Ele existe para não
    descer.
    """
    PISO = 0.95
    mensagens = [e.message for e in _erros_do_corpus()]
    assert mensagens, "o corpus nao levantou erro nenhum"
    cobertura = mod_idioma.cobertura(mensagens)
    assert cobertura >= PISO, (
        f"cobertura caiu para {cobertura:.0%} (piso {PISO:.0%}). "
        "Sem traducao:\n  " + "\n  ".join(
            m for m in mensagens if not mod_idioma.tem_traducao(m)))


def test_o_catalogo_nao_tem_molde_quebrado():
    """Todo campo do molde tem um grupo no padrão.

    É o erro que produz `KeyError` no meio de um relatório de erro — a
    pior hora possível, porque o erro de verdade desaparece.
    """
    import re
    quebrados = []
    for tabela in (mod_idioma.INTEIRAS, mod_idioma.PEDACOS):
        for padrao, molde in tabela:
            grupos = set(re.compile(padrao).groupindex)
            campos = set(re.findall(r"\{(\w+)\}", molde))
            if campos - grupos:
                quebrados.append(f"{padrao!r}: falta {campos - grupos}")
    assert not quebrados, quebrados
