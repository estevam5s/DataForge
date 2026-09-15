"""Configuração comum da suíte.

**A suíte roda em inglês, de propósito.** As mensagens nascem em inglês e
são traduzidas na hora de desenhar (ver `dataforge/idioma.py`); um teste
que afirma "Division by zero" está checando a **estrutura** do relatório
— que a linha aparece, que a pilha aparece, que o trecho aparece — e não
a redação. Deixar o idioma solto faria cada um desses testes reprovar a
cada tradução nova, o que ensinaria a não traduzir.

O caminho em português não fica sem teste por isso: `test_idioma.py`
desenha o corpus inteiro em pt-BR e cobra o que a tradução pode estragar
— um molde com campo não preenchido, um nome de tipo do Python que
reaparece, o relatório perdendo a forma — e mede a cobertura do catálogo,
que é o número que faz a lista crescer.
"""

import os

import pytest


@pytest.fixture(autouse=True, scope="session")
def _idioma_da_suite():
    """Fixa `DF_IDIOMA=en` para a suíte inteira."""
    anterior = os.environ.get("DF_IDIOMA")
    os.environ["DF_IDIOMA"] = "en"
    yield
    if anterior is None:
        os.environ.pop("DF_IDIOMA", None)
    else:
        os.environ["DF_IDIOMA"] = anterior
