"""Cada exemplo do hover **roda**.

O hover do editor dizia *o que* a palavra faz. Dizer é metade: quem está
aprendendo precisa ver como se escreve, e uma frase de dez palavras não
substitui três linhas de código.

Mas um exemplo de documentação que não compila é **pior que nenhum**: ele
ensina errado, e a pessoa passa meia hora achando que o erro é dela. Por
isso cada um é executado aqui.
"""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.exemplos_palavras import PALAVRAS   # noqa: E402
from dataforge.interpreter import Interpreter      # noqa: E402
from dataforge.lexer import tokenize               # noqa: E402
from dataforge.parser import parse                 # noqa: E402
from dataforge.tokens import KEYWORDS              # noqa: E402
from dataforge.typechecker import check_program    # noqa: E402


@pytest.mark.parametrize("palavra", sorted(PALAVRAS))
def test_o_exemplo_roda(palavra):
    """Executa, e não só compila.

    Compilar não basta: `spawn Ponto().norma()` compila e explode, e foi
    exatamente esse tipo de erro que apareceu escrevendo estes exemplos.
    """
    _, exemplo = PALAVRAS[palavra]
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            Interpreter().run(
                parse(tokenize(exemplo, f"<{palavra}>"), f"<{palavra}>"),
                f"<{palavra}>")
    except BaseException as erro:                  # noqa: BLE001
        pytest.fail(
            f"o exemplo de '{palavra}' nao roda:\n"
            f"  {type(erro).__name__}: {erro}\n\n"
            f"{exemplo}")


@pytest.mark.parametrize("palavra", sorted(PALAVRAS))
def test_o_exemplo_passa_no_analisador(palavra):
    """O `dataforge check` não pode reclamar do que a doc ensina."""
    _, exemplo = PALAVRAS[palavra]
    arvore = parse(tokenize(exemplo, "e.df"), "e.df")
    erros = [d for d in check_program(arvore, "e.df") if d.severity == "error"]
    assert not erros, (
        f"o analisador reclama do exemplo de '{palavra}': "
        f"{[d.message for d in erros]}\n\n{exemplo}")


@pytest.mark.parametrize("palavra", sorted(PALAVRAS))
def test_o_exemplo_usa_a_palavra_que_explica(palavra):
    """Um exemplo que não mostra a palavra não ensina nada sobre ela."""
    _, exemplo = PALAVRAS[palavra]
    assert palavra in exemplo, \
        f"o exemplo de '{palavra}' nao contem a palavra"


def test_toda_palavra_reservada_tem_exemplo():
    """A cobertura, para a tabela não envelhecer.

    Uma palavra nova em `tokens.py` sem exemplo aqui deixa o hover pela
    metade — e ninguém percebe, porque o hover continua aparecendo.
    """
    faltando = sorted(set(KEYWORDS) - set(PALAVRAS))
    assert not faltando, (
        f"palavras reservadas sem exemplo no hover: {faltando}\n"
        f"  acrescente em 'dataforge/exemplos_palavras.py'")


#: Modificadores que o parser reconhece pelo TEXTO, e por isso não estão
#: em `KEYWORDS`.
#:
#: `get`, `set`, `private` e companhia são nomes bons demais para tirar
#: de quem escreve — a mesma razão de `route` e `render` serem
#: contextuais no Kiln. Eles aparecem no hover porque a pessoa vai
#: digitá-los, mesmo não sendo reservados.
_CONTEXTUAIS_DE_OOP = {"abstract", "final", "get", "set",
                       "private", "protected"}


def test_nenhum_exemplo_sobra_na_tabela():
    """Uma entrada que não é palavra da linguagem é ruído que envelhece."""
    from dataforge.tokens import CONTEXTUAIS_KILN

    validas = set(KEYWORDS) | set(CONTEXTUAIS_KILN) | _CONTEXTUAIS_DE_OOP
    sobrando = sorted(set(PALAVRAS) - validas)
    assert not sobrando, f"exemplos de coisas que nao sao palavras: {sobrando}"


def test_os_contextuais_de_oop_ainda_sao_contextuais():
    """A lista acima existe porque eles NÃO estão em `KEYWORDS`.

    Se um deles virar palavra reservada de verdade, a exceção deixa de
    ser necessária — e uma exceção que não é mais necessária é a próxima
    a esconder um erro.
    """
    virou_reservada = sorted(_CONTEXTUAIS_DE_OOP & set(KEYWORDS))
    assert not virou_reservada, (
        f"{virou_reservada} agora esta em KEYWORDS — tire da excecao")


def test_a_explicacao_nao_repete_o_nome():
    """"`given` — o given" não ajuda ninguém.

    O espaço do hover é curto; gastá-lo repetindo a palavra que a pessoa
    acabou de ler é desperdiçá-lo.
    """
    ruins = [p for p, (texto, _) in PALAVRAS.items()
             if texto.strip().lower().startswith(p.lower())]
    assert not ruins, f"a explicacao comeca repetindo a palavra: {ruins}"
