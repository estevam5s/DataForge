"""A ponte para o Python — `adopt Python.numpy as np`.

Sem ela, toda capacidade nova precisava ser reescrita do zero na
biblioteca padrão. A ironia era que o DataForge **roda sobre Python** e
não alcançava nada dele.

O que estes testes cobram, em ordem de importância:

1. que a ponte **não converta** — é o que mantém o `ndarray` sendo um
   `ndarray`, e é a razão de a coisa ser útil;
2. que a mensagem de erro responda as perguntas certas quando o pacote
   não está lá;
3. que `Python` seja um espaço de nomes reservado de verdade.

Os testes que precisam de um pacote de terceiro pulam quando ele não
está instalado, e nomeiam qual. Um teste que finge passar por ausência
do que ele testa é pior que nenhum.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge import ponte                       # noqa: E402
from dataforge.errors import DataForgeError, ImportError_, NameError_  # noqa: E402
from dataforge.interpreter import Interpreter     # noqa: E402
from dataforge.lexer import tokenize              # noqa: E402
from dataforge.parser import parse                # noqa: E402


def rodar(fonte, arquivo="<ponte>"):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(fonte, arquivo), arquivo), arquivo)
    return buffer.getvalue().strip()


def precisa(pacote):
    if not ponte.tem(pacote):
        pytest.skip(f"'{pacote}' nao esta instalado neste Python")


# ── O caminho feliz ──────────────────────────────────────────

def test_adopt_traz_um_modulo_do_python():
    assert rodar('''adopt Python.math as m
out m.floor(3.9), m.gcd(12, 18)''') == "3 6"


def test_submodulo():
    assert rodar('''adopt Python.os.path as caminho
out caminho.basename("/a/b/c.txt")''') == "c.txt"


def test_selecao_de_nomes():
    assert rodar('''adopt Python.math.{floor, gcd}
out floor(3.9), gcd(12, 18)''') == "3 6"


def test_selecao_invertida():
    assert rodar('''adopt {dumps} from Python.json
out dumps({"a": 1})''') == '{"a": 1}'


def test_valores_do_dataforge_atravessam_sem_conversao():
    """Um Cluster **é** uma lista do Python; um Vault **é** um dict.

    Não há cópia na ida, e é por isso que passar uma coleção grande para
    uma biblioteca não custa nada.
    """
    assert rodar('''adopt Python.json as json
v := {"nome": "Ana", "notas": [9, 8]}
texto := json.dumps(v)
de_volta := json.loads(texto)
out typeof(de_volta), de_volta["nome"], de_volta["notas"][0]''') \
        == "Vault Ana 9"


def test_uma_acao_do_dataforge_vira_funcao_do_python():
    """`sorted(xs, key=…)` com uma ação escrita em DataForge."""
    assert rodar('''adopt Python.functools as ft

action somar(a, b):
    yield a + b

out ft.reduce(somar, [1, 2, 3, 4], 0)''') == "10"


# ── A ponte não converte, e é isso que a faz valer ───────────

def test_o_ndarray_continua_ndarray():
    """Se a ponte copiasse, `a * 2` viraria um laço sobre um milhão.

    A conta abaixo é vetorizada pelo numpy. O teste prova que o objeto
    atravessou inteiro, e não como cópia.
    """
    precisa("numpy")
    assert rodar('''adopt Python.numpy as np
a := np.array([1, 2, 3, 4])
out a * 2 + 1
out typeof(a)''') == "[3 5 7 9]\nndarray"


def test_escalar_de_biblioteca_responde_Integer_no_typeof():
    """`np.int64` não é subclasse de `int`, mas FAZ conta de inteiro.

    Sem isto, `given typeof(x) is "Integer"` seria falso para um valor
    que soma, divide e compara como um. A regra vem do protocolo
    `numbers` do Python — não há nada de numpy no interpretador.
    """
    precisa("numpy")
    assert rodar('''adopt Python.numpy as np
a := np.array([1, 2, 3])
out typeof(a.sum()), typeof(a.mean()), a.sum() + 10''') \
        == "Integer Float 16"


def test_o_protocolo_numerico_nao_e_sobre_numpy():
    """`Fraction` e `Decimal` entram pela mesma porta."""
    assert rodar('''adopt Python.fractions.{Fraction}
f := Fraction(3, 4)
out typeof(f), f * 4''') == "Float 3"


def test_tupla_nao_finge_ser_cluster():
    """Ela indexa e percorre, mas não tem `append`. Dizer `Cluster` mentiria."""
    precisa("numpy")
    assert rodar('''adopt Python.numpy as np
adopt Arcane.Ponte as Ponte
forma := np.zeros([2, 3]).shape
out typeof(forma), typeof(Ponte.cluster(forma)), Ponte.cluster(forma)''') \
        == "tuple Cluster [2, 3]"


def test_o_objeto_do_python_funciona_por_protocolo():
    """Membro, método, índice, len, iteração, verdade — tudo já passava.

    Este teste existe para travar isso: se alguém um dia fizer o
    interpretador exigir tipo em vez de protocolo, a ponte quebra
    inteira e só este teste denuncia.
    """
    precisa("numpy")
    assert rodar('''adopt Python.numpy as np
a := np.array([10, 20, 30])
out len(a)
out a[1]
cycle x in a:
    out x
given a.size:
    out "tem tamanho"''') == "3\n20\n10\n20\n30\ntem tamanho"


# ── Erros do outro lado chegam capturáveis ───────────────────

def test_excecao_do_python_e_capturavel_com_monitor():
    precisa("numpy")
    assert rodar('''adopt Python.numpy as np
monitor:
    np.array([1, 2, 3]) + np.array([1, 2])
handle e:
    out e.type''') == "ValueError"


# ── As mensagens, que é onde a FFI se prova ──────────────────

def test_pacote_ausente_diz_qual_python_e_o_comando_exato():
    """A pessoa vai ter três perguntas, nesta ordem.

    O que faltou, **em qual Python** faltou, e o comando para aquele
    Python. O terceiro é o que mais importa: o instalador cria uma venv
    em `~/.dataforge`, e quem roda `pip install` no terminal instala no
    Python do sistema, que é outro.
    """
    nome = "pacote_que_nao_existe_em_lugar_nenhum_xyz"
    with pytest.raises(ImportError_) as capturado:
        rodar(f"adopt Python.{nome} as x")

    erro = capturado.value
    texto = str(erro) + str(getattr(erro, "nota", "")) + \
        str(getattr(erro, "dica", ""))
    assert nome in texto
    assert ponte.onde() in texto, "a mensagem nao diz QUAL Python"
    assert "pip install" in texto


def test_atributo_errado_sugere_o_certo():
    precisa("numpy")
    with pytest.raises(DataForgeError) as capturado:
        rodar("adopt Python.numpy as np\nout np.arrray([1])")
    assert "array" in str(getattr(capturado.value, "dica", ""))


def test_o_erro_do_atributo_sabe_a_linha():
    """Quem levanta o erro não conhece o arquivo; a posição é do acesso.

    Sem isto a mensagem sai com `0:0` e sem o trecho de código — a dica
    estaria certa e ninguém saberia onde aplicá-la.
    """
    precisa("numpy")
    with pytest.raises(DataForgeError) as capturado:
        rodar("adopt Python.numpy as np\n\nout np.naoexiste")
    assert capturado.value.line == 3, \
        f"saiu na linha {capturado.value.line}, devia ser a 3"


def test_adopt_python_sozinho_explica_o_que_falta():
    with pytest.raises(ImportError_) as capturado:
        rodar("adopt Python")
    assert "adopt Python.numpy" in str(getattr(capturado.value, "dica", ""))


def test_o_executavel_empacotado_nao_manda_rodar_pip(monkeypatch):
    """Ele traz um Python próprio e sem `pip`: nunca vai instalar nada.

    Mandar `pip install numpy` ali é mandar a pessoa a lugar nenhum, e
    ela levaria um tempo até desconfiar do conselho.
    """
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    erro = ponte._erro_de_ausencia("Python.numpy", "numpy", None)
    texto = str(erro) + str(erro.nota) + str(erro.dica)
    assert "pip install numpy" not in texto, \
        "mandou instalar num Python que nao tem pip"
    assert "dataforge-lang" in texto, "nao disse qual e a saida"


# ── 'Python' é um espaço de nomes reservado ──────────────────

def test_um_arquivo_local_nao_sequestra_o_espaco_de_nomes(tmp_path):
    """Um `Python.df` no disco não pode responder por `adopt Python.x`.

    Se respondesse, o import mudaria de destino pela simples presença de
    um arquivo, e nada denunciaria.
    """
    (tmp_path / "Python.df").write_text("relay nada\naction nada():\n    yield 1\n",
                                        encoding="utf-8")
    programa = tmp_path / "app.df"
    programa.write_text("adopt Python.math as m\nout m.floor(1.5)\n",
                        encoding="utf-8")

    assert rodar(programa.read_text(encoding="utf-8"),
                 str(programa)) == "1"


def test_pythonico_nao_abre_a_ponte():
    """O prefixo é `Python.`, não `Python` como pedaço de palavra."""
    assert not ponte.e_caminho_de_ponte("Pythonico")
    assert not ponte.e_caminho_de_ponte("Arcane.Python")
    assert ponte.e_caminho_de_ponte("Python")
    assert ponte.e_caminho_de_ponte("Python.numpy")


# ── Arcane.Ponte ─────────────────────────────────────────────

def test_tem_responde_sem_levantar():
    assert rodar('''adopt Arcane.Ponte as Ponte
out Ponte.tem("math"), Ponte.tem("nao_existe_xyz_123")''') == "yes no"


def test_o_programa_pode_se_adaptar():
    """O caso que justifica `Ponte.tem`: escolher o caminho na hora."""
    assert rodar('''adopt Arcane.Ponte as Ponte

dados := [4.0, 8.0, 15.0, 16.0]
media := 0.0
given Ponte.tem("statistics"):
    adopt Python.statistics as st
    media := st.mean(dados)
otherwise:
    media := (dados >> distill a, v: a + v 0) / len(dados)
out media''') == "10.75"


def test_explorar_um_pacote_de_dentro_da_linguagem():
    saida = rodar('''adopt Arcane.Ponte as Ponte
adopt Python.json as json
out "dumps" in Ponte.atributos(json)
out Ponte.assinatura(json.dumps).startswith("dumps(")
out len(Ponte.doc(json.loads)) bigger 10''')
    assert saida == "yes\nyes\nyes"


def test_assinatura_devolve_void_quando_o_python_nao_declara():
    """Inventar `(…)` faria a pessoa achar que a função não tem argumento."""
    from dataforge.stdlib import get_module
    assinatura = get_module("Arcane.Ponte")["assinatura"]
    assert assinatura(len) is None or isinstance(assinatura(len), str)
    assert assinatura(42) is None


def test_converter_o_que_nao_da_diz_por_que():
    with pytest.raises(NameError_) as capturado:
        ponte.para_cluster(42)
    assert "percorriv" in str(capturado.value).lower()


def test_onde_aponta_para_o_python_que_esta_rodando():
    assert ponte.onde() == sys.executable


# ── O analisador estático ────────────────────────────────────

def test_o_check_avisa_quando_o_pacote_nao_esta_aqui():
    from dataforge.typechecker import check_program

    fonte = "adopt Python.pacote_ausente_xyz_123 as x"
    avisos = check_program(parse(tokenize(fonte, "t.df"), "t.df"), "t.df")
    codigos = [d.code for d in avisos]
    assert "pacote-python-ausente" in codigos
    assert "unknown-module" not in codigos, \
        "a ponte nao e um modulo que 'nao foi encontrado'"


def test_o_check_fica_calado_com_o_pacote_instalado():
    from dataforge.typechecker import check_program

    fonte = "adopt Python.math as m\nout m.floor(1.5)"
    avisos = check_program(parse(tokenize(fonte, "t.df"), "t.df"), "t.df")
    assert not [d for d in avisos if d.code in ("pacote-python-ausente",
                                                "unknown-module")]
