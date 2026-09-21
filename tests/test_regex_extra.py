# -*- coding: utf-8 -*-
"""Arcane.Regex — o que faltava, e por que cada lacuna custava.

Quatro recursos que a expressao regular JA tem e que o modulo tornava
inalcancaveis:

1. **O grupo nomeado nao chegava ao resultado.** `(?P<ano>\\d{4})`
   compilava e o valor vinha por posicao — e ninguem escreve
   `(?P<ano>…)` para depois ler `groups[2]`.

2. **`match` ancora so no comeco.** Validar com ele aceita lixo no fim,
   calado.

3. **`sub` so troca por texto.** Mascarar um CPF ou dobrar um numero
   exigia sair do modulo.

4. **Nada dizia que um padrao pode travar o processo.**
"""

import sys

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import get_module                       # noqa: E402
from dataforge.errors import erro_por_nome                    # noqa: E402

RegexError = erro_por_nome("RegexError")


@pytest.fixture
def R():
    return get_module("Arcane.Regex")


# ═══════════════════════════════════════════════════════════
#  Grupos nomeados
# ═══════════════════════════════════════════════════════════

def test_o_nome_chega_no_resultado_de_search(R):
    achado = R["search"](r"(?P<ano>\d{4})-(?P<mes>\d{2})", "em 2026-09")
    assert achado["named"] == {"ano": "2026", "mes": "09"}


def test_groups_por_posicao_continua_existindo(R):
    """Havia codigo lendo dali; tira-lo seria quebrar o que funciona."""
    achado = R["search"](r"(?P<ano>\d{4})-(?P<mes>\d{2})", "em 2026-09")
    assert achado["groups"] == ["2026", "09"]


def test_named_devolve_vault_vazio_quando_nao_casa(R):
    assert R["named"](r"(?P<ano>\d{4})", "sem numero") == {}


def test_findnamed_le_um_log_linha_a_linha(R):
    log = ("2026-09-20 ERRO falha ao gravar\n"
           "2026-09-20 AVISO disco cheio\n"
           "2026-09-21 ERRO conexao perdida\n")
    padrao = r"(?P<data>[\d-]+) (?P<nivel>\w+) (?P<texto>.+)"
    linhas = R["findnamed"](padrao, log)
    assert len(linhas) == 3
    assert linhas[0]["nivel"] == "ERRO"
    assert linhas[1]["texto"] == "disco cheio"
    assert [l["data"] for l in linhas].count("2026-09-20") == 2


def test_group_names_na_ordem_em_que_aparecem(R):
    assert R["group_names"](r"(?P<a>x)(\d)(?P<b>y)") == ["a", "b"]


def test_o_resultado_sem_grupo_nomeado_traz_named_vazio(R):
    """Ler `["named"]` nao pode depender de o padrao ter nomes."""
    assert R["search"](r"\d+", "abc 12")["named"] == {}
    assert R["search"](r"\d+", "sem numero")["named"] == {}


def test_finditer_tambem_traz_os_nomes(R):
    achados = R["finditer"](r"(?P<n>\d+)", "1 22 333")
    assert [a["named"]["n"] for a in achados] == ["1", "22", "333"]


# ═══════════════════════════════════════════════════════════
#  Ancorar nas duas pontas
# ═══════════════════════════════════════════════════════════

def test_match_aceita_lixo_no_fim_e_fullmatch_nao(R):
    """A diferenca que fazia um validador passar o que nao devia."""
    assert R["match"](r"\d{3}", "123abc")["matched"] is True
    assert R["fullmatch"](r"\d{3}", "123abc")["matched"] is False
    assert R["fullmatch"](r"\d{3}", "123")["matched"] is True


def test_is_exactly_e_a_pergunta_de_um_validador(R):
    assert R["is_exactly"](r"\d{5}-?\d{3}", "88010-000") is True
    assert R["is_exactly"](r"\d{5}-?\d{3}", "88010-000 e mais") is False


def test_o_vazio_tem_as_mesmas_chaves_do_casamento(R):
    """Senao ler `["start"]` de um nao-casamento levanta."""
    vazio = R["fullmatch"](r"\d+", "abc")
    cheio = R["fullmatch"](r"\d+", "12")
    assert set(vazio) == set(cheio)
    assert vazio["start"] == -1


# ═══════════════════════════════════════════════════════════
#  Substituir calculando
# ═══════════════════════════════════════════════════════════

def test_sub_with_calcula_a_troca(R):
    assert R["sub_with"](r"\d+", lambda m: str(int(m["value"]) * 2),
                         "a1 b20") == "a2 b40"


def test_sub_with_recebe_os_grupos_nomeados(R):
    def trocar(m):
        return m["named"]["mes"] + "/" + m["named"]["dia"]

    assert R["sub_with"](r"(?P<dia>\d{2})-(?P<mes>\d{2})", trocar,
                         "em 07-09") == "em 09/07"


def test_sub_with_devolvendo_void_nao_troca(R):
    """E o que deixa a acao escolher o que NAO trocar."""
    def so_os_grandes(m):
        return "N" if int(m["value"]) > 10 else None

    assert R["sub_with"](r"\d+", so_os_grandes, "1 20 3 40") == "1 N 3 N"


def test_sub_with_respeita_o_limite(R):
    assert R["sub_with"](r"\d", lambda m: "x", "123", count=2) == "xx3"


def test_sub_with_sem_acao_e_recusado(R):
    with pytest.raises(RegexError):
        R["sub_with"](r"\d", "x", "1")


def test_replace_map_deixa_o_que_nao_esta_na_tabela(R):
    """Uma tabela sem padrao transformaria o desconhecido em vazio."""
    tabela = {"sim": "yes", "nao": "no"}
    assert R["replace_map"](r"\w+", tabela, "sim talvez nao") == \
        "yes talvez no"


# ═══════════════════════════════════════════════════════════
#  Partir e recortar
# ═══════════════════════════════════════════════════════════

def test_split_keep_mantem_os_separadores(R):
    assert R["split"](r"\s+", "a  b\tc") == ["a", "b", "c"]
    assert R["split_keep"](r"\s+", "a  b\tc") == ["a", "  ", "b", "\t", "c"]


def test_split_keep_reconstroi_o_texto(R):
    """E a razao de existir: transformar os pedacos e juntar de volta."""
    texto = "campo1 = valor;  campo2 =outro"
    pedacos = R["split_keep"](r"[=;]", texto)
    assert "".join(pedacos) == texto


def test_split_keep_com_separador_nas_pontas(R):
    assert R["split_keep"](r",", ",a,") == [",", "a", ","]


def test_between_recorta_entre_marcas(R):
    html = "<b>um</b> e <b>dois</b>"
    assert R["between"](r"<b>", r"</b>", html) == ["um", "dois"]


def test_between_ignora_a_marca_de_abertura_sem_fecho(R):
    assert R["between"](r"\[", r"\]", "[a] e [sem fim") == ["a"]


# ═══════════════════════════════════════════════════════════
#  Ver o que casou
# ═══════════════════════════════════════════════════════════

def test_highlight_mostra_ONDE_casou(R):
    """Uma lista de resultados nao diz onde o padrao pegou."""
    assert R["highlight"](r"\d+", "a1 b22") == "a[1] b[22]"
    assert R["highlight"](r"\d+", "a1", before="<<", after=">>") == "a<<1>>"


def test_positions_responde_em_linha_e_coluna(R):
    texto = "primeira\nsegunda com 42\nterceira"
    achados = R["positions"](r"\d+", texto)
    assert len(achados) == 1
    assert achados[0]["linha"] == 2
    assert achados[0]["coluna"] == 13
    assert achados[0]["value"] == "42"


def test_positions_conta_a_coluna_a_partir_de_um(R):
    achados = R["positions"](r"x", "x")
    assert achados[0] == {"linha": 1, "coluna": 1, "value": "x",
                          "start": 0, "end": 1}


# ═══════════════════════════════════════════════════════════
#  Explicar
# ═══════════════════════════════════════════════════════════

def test_explain_le_o_padrao_pedaco_a_pedaco(R):
    partes = R["explain"](r"^\d{3}-\w+$")
    trechos = [p["trecho"] for p in partes]
    assert trechos == ["^", r"\d", "{3}", "-", r"\w", "+", "$"]
    assert "comeco" in partes[0]["quer_dizer"]
    assert "exatamente 3" in partes[2]["quer_dizer"]
    assert "literal" in partes[3]["quer_dizer"]


def test_explain_nomeia_o_grupo(R):
    partes = R["explain"](r"(?P<ano>\d{4})")
    assert "'ano'" in partes[0]["quer_dizer"]


def test_explain_distingue_o_preguicoso(R):
    assert "MENOS" in R["explain"](r"a+?")[1]["quer_dizer"]
    assert "MENOS" not in R["explain"](r"a+")[1]["quer_dizer"]


def test_explain_distingue_a_classe_negada(R):
    assert "FORA" in R["explain"](r"[^abc]")[0]["quer_dizer"]
    assert "FORA" not in R["explain"](r"[abc]")[0]["quer_dizer"]


def test_explain_junta_os_literais_seguidos(R):
    partes = R["explain"]("abc")
    assert len(partes) == 1
    assert partes[0]["trecho"] == "abc"


def test_um_padrao_quebrado_nao_e_explicado(R):
    with pytest.raises(RegexError):
        R["explain"](r"(sem fecho")


def test_o_padrao_quebrado_mostra_ONDE(R):
    """A mensagem do Python diz `at position 7` e nao mostra o padrao."""
    with pytest.raises(RegexError) as erro:
        R["explain"](r"a{2,1}")
    assert "^" in str(erro.value)


# ═══════════════════════════════════════════════════════════
#  O risco de travar
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("padrao", [
    r"(a+)+$",
    r"([a-z]+)+$",
    r"(a{2,})+$",
    r"(x|x)+$",
])
def test_os_quatro_desenhos_classicos_sao_acusados(R, padrao):
    analise = R["risk"](padrao)
    assert analise["perigoso"] is True, padrao
    assert analise["motivo"]


@pytest.mark.parametrize("padrao", [
    r"\d{3}-\d{4}",
    r"^[a-z]+@[a-z]+\.[a-z]{2,}$",
    r"(?P<ano>\d{4})-(?P<mes>\d{2})",
])
def test_um_padrao_comum_nao_e_acusado(R, padrao):
    """Um falso alarme aqui ensinaria a desligar a conferencia."""
    assert R["risk"](padrao)["perigoso"] is False, padrao


def test_a_analise_diz_que_e_forma_e_nao_prova(R):
    """Prometer mais do que ela entrega e o defeito de uma ferramenta assim."""
    assert "forma" in R["risk"](r"\d+")["nota"]
    assert "e nao uma prova" in R["risk"](r"\d+")["nota"]


def test_safe_search_recusa_o_padrao_perigoso_ANTES_de_rodar(R):
    with pytest.raises(RegexError) as erro:
        R["safe_search"](r"(a+)+$", "a" * 30 + "b")
    assert "travar" in str(erro.value)


def test_safe_search_funciona_no_padrao_comum(R):
    achado = R["safe_search"](r"(?P<n>\d+)", "abc 42")
    assert achado["named"]["n"] == "42"
    assert achado["demorou"] is False
    assert achado["ms"] >= 0


def test_safe_search_mede_e_nao_interrompe(R):
    """O motor do Python nao solta o GIL: um prazo numa thread nao para nada.

    A honestidade aqui e o recurso — `demorou` diz que passou do prazo,
    e nao que a busca foi cancelada.
    """
    achado = R["safe_search"](r"\d+", "x" * 100, ms=0)
    assert achado["demorou"] is True
    assert achado["matched"] is False


# ═══════════════════════════════════════════════════════════
#  O modulo continua inteiro
# ═══════════════════════════════════════════════════════════

def test_as_duas_metades_estao_no_mesmo_dicionario(R):
    from dataforge.stdlib.arcane_regex_extra import EXTRAS
    for nome in EXTRAS:
        assert nome in R, nome
    # E o que ja existia continua la.
    for nome in ["match", "search", "findall", "sub", "split", "is_cpf",
                 "patterns", "escape"]:
        assert nome in R, nome


def test_nenhum_nome_novo_sobrescreve_um_antigo(R):
    """Um extra com o nome de uma operacao trocaria o comportamento
    de codigo que ja existe, em silencio."""
    from dataforge.stdlib.arcane_regex import ArcaneRegex
    from dataforge.stdlib.arcane_regex_extra import EXTRAS
    import dataforge.stdlib.arcane_regex as mod

    original = mod.ArcaneRegex.__new__
    # O dicionario sem os extras: o que o modulo tinha antes.
    antigos = {"match", "search", "findall", "finditer", "sub", "subn",
               "split", "test", "count", "extract", "compile", "patterns",
               "escape", "replace_all"}
    assert antigos.isdisjoint(set(EXTRAS)), sorted(antigos & set(EXTRAS))
    assert callable(original)


# ═══════════════════════════════════════════════════════════
#  O objeto compilado
# ═══════════════════════════════════════════════════════════

def test_o_compilado_tem_TODAS_as_operacoes_de_padrao(R):
    """Ele tinha cinco, na forma que a doc recomenda para um laço.

    Quem compilava perdia `finditer`, os grupos nomeados, `fullmatch`,
    `split` e a contagem — e voltava a chamar a versão por texto, que
    é o contrário do motivo de compilar.
    """
    from dataforge.stdlib.arcane_regex import _COM_PADRAO_E_TEXTO

    compilado = R["compile"](r"(?P<k>\w+)=(?P<v>[^;]+)")
    for nome in _COM_PADRAO_E_TEXTO:
        assert nome in compilado, nome


def test_o_compilado_responde_o_MESMO_que_a_versao_por_texto(R):
    padrao = r"(?P<k>\w+)=(?P<v>[^;]+)"
    linha = "nome=Ana;cidade=Floripa"
    c = R["compile"](padrao)

    assert c["findall"](linha) == R["findall"](padrao, linha)
    assert c["named"](linha) == R["named"](padrao, linha)
    assert c["search"](linha) == R["search"](padrao, linha)
    assert c["sub"]("X", linha) == R["sub"](padrao, "X", linha)
    assert c["group_names"]() == R["group_names"](padrao)
    assert c["split"](linha) == R["split"](padrao, linha)
    assert c["count"](linha) == R["count"](padrao, linha)


def test_o_compilado_carrega_a_flag(R):
    c = R["compile"]("[a-z]+", R["IGNORECASE"])
    assert c["is_exactly"]("ABC") is True
    assert R["is_exactly"]("[a-z]+", "ABC") is False


def test_a_lista_do_compilado_sai_do_modulo(R):
    """Uma segunda lista a mão divergiria no primeiro símbolo novo."""
    from dataforge.stdlib.arcane_regex import _COM_PADRAO_E_TEXTO

    inventados = [n for n in _COM_PADRAO_E_TEXTO if n not in R]
    assert not inventados, inventados


def test_um_padrao_quebrado_falha_ao_COMPILAR(R):
    """E não no primeiro uso, três camadas adiante."""
    import re as _re
    with pytest.raises(_re.error):
        R["compile"]("(sem fecho")
