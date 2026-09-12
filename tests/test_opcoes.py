"""Um vault de opções que não engole erro de digitação.

O problema, com o sintoma exato:

    doc := API.openapi(app, {"title": "Loja", "version": "2.0"})

As chaves são `titulo` e `versao`. As minhas foram **ignoradas em
silêncio**, e o documento saiu com o título padrão. Quem escreve isso
publica um contrato com o nome errado e não tem como descobrir: não há
erro, não há aviso, e o campo existe no resultado.

O mesmo com um erro de digitação: `{"tentativa": 9}` deixava o cliente
com as 3 tentativas do padrão, e o 9 nunca chegava a lugar nenhum.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib.opcoes import OpcaoDesconhecida, ler   # noqa: E402

CONHECIDAS = {"prazo": 5.0, "tentativas": 3, "nome": ""}


def test_a_opcao_conhecida_passa():
    assert ler({"prazo": 1.0}, CONHECIDAS) == {"prazo": 1.0}


def test_vazio_e_void_passam():
    assert ler(None, CONHECIDAS) == {}
    assert ler({}, CONHECIDAS) == {}


def test_a_opcao_desconhecida_e_recusada():
    with pytest.raises(OpcaoDesconhecida) as falha:
        ler({"tentativa": 9}, CONHECIDAS)
    assert "tentativa" in str(falha.value)


def test_a_recusa_sugere_o_nome_parecido():
    """A sugestão é o que transforma a recusa em correção. Sem ela, a
    mensagem diz que algo está errado e não diz o quê."""
    with pytest.raises(OpcaoDesconhecida) as falha:
        ler({"tentativa": 9}, CONHECIDAS)
    assert "did you mean 'tentativas'" in str(falha.value)


def test_a_recusa_lista_o_que_existe():
    """Quem errou um nome que não se parece com nenhum continua sem
    saber o que existe."""
    with pytest.raises(OpcaoDesconhecida) as falha:
        ler({"xyzabc": 1}, CONHECIDAS)
    texto = str(falha.value)
    assert "did you mean" not in texto        # nada parecido
    for nome in CONHECIDAS:
        assert nome in texto


def test_varias_erradas_numa_mensagem():
    """Uma exceção por chave faria a pessoa corrigir uma, rodar de
    novo, e descobrir a seguinte."""
    with pytest.raises(OpcaoDesconhecida) as falha:
        ler({"tentativa": 1, "przo": 2}, CONHECIDAS)
    texto = str(falha.value)
    assert "tentativa" in texto and "przo" in texto
    assert "options" in texto                 # plural


def test_o_nome_da_funcao_entra_na_mensagem():
    """Num programa com cinco chamadas parecidas, "unknown option" sem
    dizer onde não ajuda."""
    with pytest.raises(OpcaoDesconhecida) as falha:
        ler({"x": 1}, CONHECIDAS, "Malha.cliente")
    assert "Malha.cliente" in str(falha.value)


def test_uma_chave_com_underscore_passa():
    """É como se marca "isto é meu, e a função não precisa conhecer" —
    um campo que o programa usa para si, num vault que ele reaproveita.
    """
    assert ler({"_meu": 1, "prazo": 2}, CONHECIDAS) == {"_meu": 1, "prazo": 2}


def test_o_que_nao_e_vault_e_recusado_dizendo_o_que_veio():
    with pytest.raises(OpcaoDesconhecida) as falha:
        ler([1, 2, 3], CONHECIDAS, "Malha.cliente")
    assert "vault" in str(falha.value)
    assert "list" in str(falha.value)


def test_ler_devolve_uma_copia():
    """Guardar a referência deixaria a função enxergar mudanças que
    quem chamou fizesse depois — e o bug seria de tempo, não de
    valor."""
    original = {"prazo": 1.0}
    saida = ler(original, CONHECIDAS)
    saida["prazo"] = 99.0
    assert original["prazo"] == 1.0


def test_e_um_value_error_para_o_interpretador_traduzir():
    """O interpretador traduz o que a stdlib levanta: isto chega ao
    programa DataForge como erro com tipo, capturável por `handle`."""
    assert issubclass(OpcaoDesconhecida, ValueError)


def test_o_modulo_nao_importa_nada_de_fora():
    import ast

    padrao = set(sys.stdlib_module_names)
    arvore = ast.parse(open("dataforge/stdlib/opcoes.py",
                            encoding="utf-8").read())
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                assert alias.name.split(".")[0] in padrao, alias.name
        elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
            assert no.module.split(".")[0] in padrao, no.module


# ═══════════════════════════════════════════════════════════
#  Quem usa
# ═══════════════════════════════════════════════════════════

def test_a_malha_recusa_a_opcao_errada_do_cliente():
    from dataforge.stdlib import get_module

    M = get_module("Arcane.Malha")
    with pytest.raises(Exception) as falha:
        M["cliente"]("http://x", {"tentativa": 9})
    assert "tentativas" in str(falha.value)


def test_a_malha_recusa_a_opcao_errada_do_disjuntor():
    """O vault de dentro tem as opções dele, e um `falha` no singular
    deixava o disjuntor com o limite padrão 5 — o número que a pessoa
    escreveu não valia nada."""
    from dataforge.stdlib import get_module

    M = get_module("Arcane.Malha")
    with pytest.raises(Exception) as falha:
        M["cliente"]("http://x", {"disjuntor": {"falha": 3}})
    texto = str(falha.value)
    assert "falhas" in texto
    assert "disjuntor" in texto


def test_o_disjuntor_desligado_com_no_continua_valendo():
    """`{"disjuntor": no}` desliga — e não pode ser lido como um vault
    de opções vazio, que ligaria o disjuntor com os padrões."""
    from dataforge.stdlib import get_module

    M = get_module("Arcane.Malha")
    cliente = M["cliente"]("http://x", {"disjuntor": False})
    assert cliente.disjuntor is None


def test_a_opcao_certa_da_malha_chega_ao_cliente():
    from dataforge.stdlib import get_module

    M = get_module("Arcane.Malha")
    cliente = M["cliente"]("http://x", {
        "tentativas": 9, "prazo": 1.5, "nome": "estoque",
        "disjuntor": {"falhas": 2, "espera": 0.5}})
    assert cliente.tentativas == 9
    assert cliente.prazo == 1.5
    assert cliente.nome == "estoque"
    assert cliente.disjuntor.limite == 2
    assert cliente.disjuntor.espera == 0.5
