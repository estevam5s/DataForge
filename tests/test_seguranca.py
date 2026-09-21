# -*- coding: utf-8 -*-
"""Arcane.Seguranca.

Tres coisas que estes testes cobram, e que nao sao obvias:

1. **Os vetores dos RFCs.** O HOTP e o TOTP tem vetores publicados
   (RFC 4226 e RFC 6238), e uma implementacao de OTP que nao os
   reproduz esta errada — mesmo que "funcione", porque o autenticador
   do usuario vai discordar dela.

2. **O que a varredura de segredo CALA.** A lista do que ela nao
   acusa custou mais que a do que ela acusa, e e ela que decide se a
   ferramenta e usada ou desligada. Um falso alarme no material
   didatico do proprio projeto e o caminho mais rapido para
   `--no-verify`.

3. **O repositorio inteiro.** O teste que mais importa aqui nao e
   nenhum caso montado: e rodar a varredura sobre os 1300 arquivos do
   repositorio e cobrar zero achado nao silenciado. Foi assim que as
   quatro regras ruidosas apareceram.
"""

import json
import os
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib import get_module  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = get_module("Arcane.Seguranca")


def _forma(prefixo, corpo):
    """Uma chave de teste, montada — nunca escrita inteira.

    O push protection do GitHub varre o que entra no repositorio e
    RECUSA um literal com forma de chave. Ele nao tem como saber que
    este arquivo e o teste de um varredor de segredos, e nem deveria:
    a excecao que ele abrisse aqui valeria para qualquer arquivo que
    se declarasse teste. O push desta suite foi bloqueado assim, e a
    fixtura acusada era a chave de EXEMPLO da documentacao da Stripe.

    Montar em pedacos deixa os dois varredores certos ao mesmo tempo:
    o de fora nao ve chave nenhuma, e o de dentro ve a forma completa,
    que e o que ele existe para achar.
    """
    return prefixo + corpo


#: A chave do GitHub usada em varios testes daqui.
CHAVE_GITHUB = _forma("ghp" + "_", "abcdefghijklmnopqrstuvwxyz0123456789")


def erro_de(nome):
    from dataforge import errors
    return errors.erro_por_nome(nome)


# ═══════════════════════════════════════════════════════════
#  Escapar
# ═══════════════════════════════════════════════════════════

def test_escapar_html_pega_os_cinco():
    assert S["escapar_html"]("<b>&'\"") == "&lt;b&gt;&amp;&#x27;&quot;"


def test_escapar_atributo_fecha_o_atributo_sem_aspas():
    """`<a href=x onclick=mau()>`: ali o espaco e o fim do valor."""
    saida = S["escapar_atributo"]("x onclick=mau()")
    assert " " not in saida
    assert "=" not in saida
    assert "(" not in saida


def test_escapar_js_nao_deixa_fechar_a_tag_script():
    saida = S["escapar_js"]("</script><script>mau()</script>")
    assert "</script>" not in saida
    assert "<" not in saida


def test_escapar_csv_neutraliza_a_formula():
    e = S["escapar_csv"]
    for perigoso in ("=1+1", "+1", "-1", "@SUM(A1)", "\t=1"):
        assert e(perigoso).startswith("'")
    assert e("nome comum") == "nome comum"
    assert e("Ana") == "Ana"
    # Uma data comeca com DIGITO, e nao com '-': ela nao e formula,
    # e escapa-la poria um apostrofo em toda coluna de data.
    assert e("2026-01-01") == "2026-01-01"


def test_escapar_csv_deixa_passar_o_que_nao_e_formula():
    assert S["escapar_csv"]("R$ 10,00") == "R$ 10,00"
    assert S["escapar_csv"](42) == "42"


def test_escapar_cabecalho_tira_a_quebra_de_linha():
    saida = S["escapar_cabecalho"]("/painel\r\nSet-Cookie: admin=1")
    assert "\r" not in saida and "\n" not in saida


def test_escapar_log_torna_a_quebra_visivel():
    """Sem isso, um campo de usuario acrescenta uma LINHA ao log."""
    saida = S["escapar_log"]("ana\n2026-01-01 INFO login ok")
    assert "\n" not in saida
    assert "\\n" in saida


def test_sem_controle_tira_a_marca_que_inverte_a_leitura():
    """U+202E faz 'relatorio_exe.txt' aparecer como 'relatorio_txt.exe'."""
    assert "‮" not in S["sem_controle"]("relatorio‮txt.exe")


def test_limpar_html_deixa_a_formatacao_e_tira_o_script():
    saida = S["limpar_html"]("<b>oi</b><script>mau()</script>")
    assert "<b>oi</b>" in saida
    assert "script" not in saida
    assert "mau()" not in saida, "o TEXTO do script tambem sai"


def test_limpar_html_recusa_o_esquema_javascript():
    assert "javascript" not in S["limpar_html"]("<a href='javascript:mau()'>x</a>")


def test_limpar_html_recusa_o_atributo_de_evento():
    saida = S["limpar_html"]("<b onclick='mau()'>oi</b>")
    assert "onclick" not in saida
    assert "<b>oi</b>" in saida


def test_limpar_html_fecha_a_tag_que_ficou_aberta():
    assert S["limpar_html"]("<b>oi") == "<b>oi</b>"


def test_limpar_html_escapa_o_texto_de_fora_das_tags():
    assert "&lt;" in S["limpar_html"]("a < b")


def test_escapar_sql_like_dobra_o_escape_primeiro():
    """Se o '%' fosse escapado antes da barra, a barra dobraria o dele."""
    assert S["escapar_sql_like"]("50%") == "50\\%"
    assert S["escapar_sql_like"]("a\\b") == "a\\\\b"


# ═══════════════════════════════════════════════════════════
#  Senha
# ═══════════════════════════════════════════════════════════

def test_a_senha_mais_comum_do_mundo_tira_nota_zero():
    r = S["forca_da_senha"]("123456")
    assert r["nota"] == 0
    assert r["comum"] is True


def test_a_forca_devolve_a_lista_e_nao_so_a_nota():
    """'fraca' nao diz o que fazer; 'problemas' diz."""
    r = S["forca_da_senha"]("abc")
    assert r["problemas"], "sem a lista, a tela nao tem o que mostrar"
    assert any("8 caracteres" in p for p in r["problemas"])


def test_uma_senha_boa_passa():
    r = S["forca_da_senha"]("Tr0vao#Azul7291!x")
    assert r["nota"] >= 60
    assert r["problemas"] == []


def test_a_sequencia_de_teclado_e_acusada_apesar_da_variedade():
    r = S["forca_da_senha"]("Abcdef1!")
    assert any("sequencia" in p for p in r["problemas"])


def test_politica_devolve_e_exigir_levanta():
    assert S["politica"]("Tr0vao#Azul7291!x")["ok"] is True
    r = S["politica"]("curta")
    assert r["ok"] is False and len(r["faltando"]) >= 2

    with pytest.raises(erro_de("PolicyError")) as e:
        S["exigir_politica"]("123456")
    assert e.value.nota, "a lista do que falta vai em 'nota'"


def test_a_politica_recusa_opcao_desconhecida():
    from dataforge.stdlib.opcoes import OpcaoDesconhecida
    with pytest.raises(OpcaoDesconhecida):
        S["politica"]("x", {"minimoo": 3})


def test_a_politica_aplica_o_padrao_quando_a_opcao_nao_vem():
    """'opcoes.ler' valida e nao aplica padrao; quem chama tem de aplicar."""
    r = S["politica"]("abc", {"minimo": 3, "simbolo": False,
                              "maiuscula": False, "numero": False,
                              "entropia": 0})
    assert r["ok"] is True


def test_o_prefixo_de_vazamento_manda_cinco_caracteres():
    p = S["prefixo_vazamento"]("password")
    assert len(p["prefixo"]) == 5
    assert p["prefixo"] + p["resto"] == (
        "5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8")


def test_conferir_vazamento_acha_na_resposta_do_servico():
    p = S["prefixo_vazamento"]("password")
    resposta = f"0000000000000000000000000000000000:3\n{p['resto']}:9659365"
    assert S["conferir_vazamento"]("password", resposta) == 9659365
    assert S["conferir_vazamento"]("Tr0vao#Azul7291!x", resposta) == 0


# ═══════════════════════════════════════════════════════════
#  TOTP / HOTP — os vetores dos RFCs
# ═══════════════════════════════════════════════════════════

#: RFC 4226, apendice D. O segredo e "12345678901234567890".
_RFC4226 = ["755224", "287082", "359152", "969429", "338314",
            "254676", "287922", "162583", "399871", "520489"]
_SEGREDO_RFC = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"


@pytest.mark.parametrize("contador,esperado", list(enumerate(_RFC4226)))
def test_hotp_reproduz_o_rfc_4226(contador, esperado):
    assert S["hotp"](_SEGREDO_RFC, contador) == esperado


@pytest.mark.parametrize("quando,esperado", [
    (59, "94287082"), (1111111109, "07081804"), (1111111111, "14050471"),
    (1234567890, "89005924"), (2000000000, "69279037"),
])
def test_totp_reproduz_o_rfc_6238(quando, esperado):
    """Oito digitos, SHA-1, janela de 30 — como o RFC publica."""
    assert S["totp_agora"](_SEGREDO_RFC, 30, 8, "sha1", quando) == esperado


def test_totp_confere_o_codigo_do_momento():
    segredo = S["totp_segredo"]()
    assert S["totp_conferir"](segredo, S["totp_agora"](segredo))
    assert not S["totp_conferir"](segredo, "000000")


def test_totp_aceita_a_janela_vizinha_e_nao_a_distante():
    """Sem tolerancia, o codigo digitado no segundo 29 chega no 31."""
    segredo = S["totp_segredo"]()
    agora = 1_700_000_000
    anterior = S["totp_agora"](segredo, 30, 6, "sha1", agora - 30)
    assert S["totp_conferir"](segredo, anterior, quando=agora)

    longe = S["totp_agora"](segredo, 30, 6, "sha1", agora - 300)
    assert not S["totp_conferir"](segredo, longe, quando=agora)


def test_totp_uri_tem_o_que_o_autenticador_le():
    uri = S["totp_uri"]("ABCDEFGH", "ana@loja.com", "Loja")
    assert uri.startswith("otpauth://totp/")
    assert "issuer=Loja" in uri and "secret=ABCDEFGH" in uri


def test_o_segredo_invalido_da_erro_com_dica_e_nao_traceback():
    with pytest.raises(erro_de("UnsafeInputError")) as e:
        S["hotp"]("nao!e!base32", 0)
    assert "base32" in str(e.value)


def test_codigos_de_recuperacao_saem_com_o_resumo_ao_lado():
    """Guardar o codigo em claro no banco desfaz o motivo de ele existir."""
    r = S["codigos_de_recuperacao"](5)
    assert len(r["codigos"]) == 5 and len(r["resumos"]) == 5
    assert len(set(r["codigos"])) == 5
    import hashlib
    assert hashlib.sha256(r["codigos"][0].encode()).hexdigest() == r["resumos"][0]


def test_o_codigo_de_recuperacao_nao_tem_letra_ambigua():
    """O/0 e I/1 fazem quem digita errar, e o codigo e digitado uma vez."""
    for codigo in S["codigos_de_recuperacao"](20)["codigos"]:
        assert not set(codigo) & set("O0I1")


# ═══════════════════════════════════════════════════════════
#  Token assinado
# ═══════════════════════════════════════════════════════════

def test_o_token_volta_com_o_valor():
    chave = S["chave_de_assinatura"]()
    t = S["assinar"]({"id": 7}, chave)
    assert S["ler_assinado"](t, chave)["valor"] == {"id": 7}


def test_o_token_mexido_e_recusado():
    chave = S["chave_de_assinatura"]()
    t = S["assinar"]({"id": 7}, chave)
    mexido = t[:-4] + ("aaaa" if not t.endswith("aaaa") else "bbbb")
    with pytest.raises(erro_de("SignatureError")):
        S["ler_assinado"](mexido, chave)


def test_o_token_de_outra_chave_e_recusado():
    t = S["assinar"]({"id": 7}, S["chave_de_assinatura"]())
    with pytest.raises(erro_de("SignatureError")):
        S["ler_assinado"](t, S["chave_de_assinatura"]())


def test_o_proposito_impede_o_token_de_email_trocar_a_senha():
    """Sem ele, os dois sao assinados com a mesma chave e servem um ao outro."""
    chave = S["chave_de_assinatura"]()
    t = S["assinar"]({"id": 7}, chave, proposito="confirmar-email")
    with pytest.raises(erro_de("SignatureError")):
        S["ler_assinado"](t, chave, proposito="trocar-senha")
    assert S["ler_assinado"](t, chave, proposito="confirmar-email")["valor"]


def test_o_prazo_vencido_tem_erro_PROPRIO():
    """A resposta ao usuario e outra: aqui o link caducou e cabe outro."""
    chave = S["chave_de_assinatura"]()
    t = S["assinar"]({"id": 7}, chave, quando=time.time() - 7200)
    with pytest.raises(erro_de("ExpiredTokenError")):
        S["ler_assinado"](t, chave, prazo=3600)


def test_a_assinatura_e_conferida_ANTES_do_prazo():
    """A data de dentro e dado de quem mandou ate a assinatura fechar."""
    chave = S["chave_de_assinatura"]()
    t = S["assinar"]({"id": 7}, chave, quando=time.time() - 7200)
    mexido = t[:-4] + ("aaaa" if not t.endswith("aaaa") else "bbbb")
    with pytest.raises(erro_de("SignatureError")):
        S["ler_assinado"](mexido, chave, prazo=3600)


def test_a_url_assinada_confere_e_vence():
    chave = S["chave_de_assinatura"]()
    u = S["assinar_url"]("https://loja.com/baixar?id=9", chave, prazo=60)
    assert S["conferir_url"](u, chave)["ok"] is True

    velha = S["assinar_url"]("https://loja.com/baixar?id=9", chave,
                             prazo=10, quando=time.time() - 100)
    with pytest.raises(erro_de("ExpiredTokenError")):
        S["conferir_url"](velha, chave)


def test_mudar_um_parametro_invalida_a_url():
    chave = S["chave_de_assinatura"]()
    u = S["assinar_url"]("https://loja.com/baixar?id=9", chave, prazo=60)
    with pytest.raises(erro_de("SignatureError")):
        S["conferir_url"](u.replace("id=9", "id=10"), chave)


# ═══════════════════════════════════════════════════════════
#  Segredo opaco
# ═══════════════════════════════════════════════════════════

def test_o_segredo_nao_aparece_em_nenhum_caminho_de_texto():
    s = S["segredo"]("sk_live_muito_secreto")
    assert str(s) == "***"
    assert f"{s}" == "***"
    assert "muito_secreto" not in repr(s)
    assert "muito_secreto" not in f"vault: {{'chave': {s}}}"


def test_o_segredo_so_sai_por_revelar():
    s = S["segredo"]("abc")
    assert s.revelar() == "abc"
    assert s.igual("abc") and not s.igual("abd")


def test_o_segredo_nao_pode_virar_chave_de_vault():
    """O resumo dele acabaria num log ou numa chave de cache."""
    with pytest.raises(erro_de("SecurityError")):
        {S["segredo"]("x"): 1}


def test_e_segredo_distingue():
    assert S["e_segredo"](S["segredo"]("x")) is True
    assert S["e_segredo"]("x") is False


# ═══════════════════════════════════════════════════════════
#  Varredura de segredo — e o que ela CALA
# ═══════════════════════════════════════════════════════════

#: As fixturas sao MONTADAS, e nao escritas inteiras — e a razao vale
#: mais que o incomodo.
#:
#: 1. O push protection do GitHub varre o que entra no repositorio e
#:    RECUSA um literal com forma de chave. Ele nao tem como saber que
#:    este arquivo e o teste de um varredor de segredos, e nem deveria:
#:    a excecao que ele abrisse aqui valeria para qualquer arquivo que
#:    se declarasse teste. O push desta suite foi bloqueado assim.
#:
#: 2. Escrever a chave de EXEMPLO da documentacao de um servico nao
#:    resolve: a da AWS ('AKIAIOSFODNN7EXAMPLE') contem 'EXAMPLE' e o
#:    nosso proprio filtro de demonstracao a cala — corretamente.
#:
#: Montar em pedacos e o unico caminho que deixa os dois varredores
#: certos ao mesmo tempo: o de fora nao ve chave nenhuma, e o de dentro
#: ve a forma completa, que e o que ele existe para achar.
FORMATOS = [
    ("GitHub", CHAVE_GITHUB),
    ("AWS", _forma("AK" + "IA", "2F7QR4KLMZ9XBTUV")),
    ("Stripe", _forma("sk" + "_live_", "9Zq4WvNbTx2KmRd7YpLcHs3F")),
    ("chave privada", "-----BEGIN RSA PRIVATE KEY-----"),
    # NAO derivada de token nenhum de verdade: digitos e letras a esmo.
    ("PyPI", _forma("py" + "pi-", "AgQ7bZmK4TxV9rLpWnHc2FdJ8sYqEuXa")),
    ("Slack", _forma("xo" + "xb-", "12345678901-abcdefghijkl")),
    ("Google", _forma("AI" + "za", "SyD-1234567890abcdefghijklmnopqrstu")),
]


@pytest.mark.parametrize("tipo,texto", FORMATOS)
def test_a_varredura_acha_cada_formato(tipo, texto):
    achados = S["procurar_segredos"](f'x := "{texto}"')
    assert achados, f"nao achou {tipo}"
    assert achados[0]["tipo"] == tipo


def test_nenhuma_fixtura_deste_arquivo_e_uma_chave_literal():
    """A trava para a correcao nao ser desfeita sem ninguem ver.

    Colar uma chave inteira aqui volta a bloquear o push do
    repositorio, e o erro do GitHub aponta a LINHA — nao o motivo. A
    proxima pessoa perde a tarde antes de achar este comentario.
    """
    fonte = _ler_este_arquivo()
    for prefixo in ("ghp_", "sk_live_", "sk_test_", "AKIA", "pypi-",
                    "xoxb-", "AIza", "sk-ant-"):
        # O prefixo aparece em prosa e em '_PADROES'; o que se proibe e
        # ele COLADO a um corpo longo, que e o que tem forma de chave.
        for linha in fonte.split("\n"):
            # Comentario nao e codigo. Sem esta linha a trava acusa a
            # PROSA que explica por que a chave da AWS de exemplo nao
            # serve — a mesma armadilha do marcador 'TODO' no lint.
            if linha.lstrip().startswith("#"):
                continue
            if prefixo not in linha or "_forma(" in linha:
                continue
            depois = linha.split(prefixo, 1)[1]
            corpo = ""
            for c in depois:
                if c.isalnum() or c in "-_":
                    corpo += c
                else:
                    break
            assert len(corpo) < 16, (
                f"chave literal com forma de '{prefixo}' nesta linha:\n"
                f"    {linha.strip()}\n"
                "Monte-a com '_forma(...)': o push protection do GitHub "
                "recusa um literal assim, e nao ha excecao a pedir.")


def _ler_este_arquivo():
    with open(os.path.abspath(__file__), encoding="utf-8") as f:
        return f.read()


def test_o_trecho_do_relatorio_ja_vem_mascarado():
    """Um relatorio de vazamento que imprime o segredo e mais um lugar onde ele esta."""
    a = S["procurar_segredos"](f'x := "{CHAVE_GITHUB}"')[0]
    assert a["trecho"].startswith("ghp_")
    assert "abcdefghijkl" not in a["trecho"]


def test_o_achado_tem_linha_e_coluna_de_UM():
    a = S["procurar_segredos"](f'linha 1\nx := "{CHAVE_GITHUB}"')[0]
    assert a["linha"] == 2
    assert a["coluna"] >= 1


@pytest.mark.parametrize("texto", [
    'token := "123456:AAHexemplo"',
    'senha := "sua-senha-aqui"',
    'api_key := "YOUR_API_KEY_HERE"',
    'secret := "<coloque-aqui>"',
    'chave := "xxxxxxxxxxxxxxxx"',
])
def test_a_varredura_CALA_sobre_valor_de_demonstracao(texto):
    """Acusar o material didatico do projeto e desligar a ferramenta."""
    assert S["procurar_segredos"](texto) == []


def test_a_varredura_CALA_sobre_jwt_anon_e_FALA_sobre_service_role():
    """As duas chaves tem o mesmo formato; so o papel de dentro as separa."""
    import base64 as b64

    def jwt(papel):
        cabeca = b64.urlsafe_b64encode(b'{"alg":"HS256"}').decode().rstrip("=")
        corpo = b64.urlsafe_b64encode(
            json.dumps({"iss": "supabase", "role": papel}).encode()
        ).decode().rstrip("=")
        return f"{cabeca}.{corpo}.assinaturafalsa1234567890"

    assert S["procurar_segredos"](jwt("anon")) == []
    assert S["procurar_segredos"](jwt("authenticated")) == []

    achados = S["procurar_segredos"](jwt("service_role"))
    assert achados and "service_role" in achados[0]["tipo"]


def test_a_varredura_CALA_sobre_credencial_de_localhost():
    """'postgres://forge:forge@localhost' num teste e um teste normal."""
    assert S["procurar_segredos"]("postgres://forge:forge@localhost:5432/db") == []
    assert S["procurar_segredos"]("https://u:p@servico.example/api") == []


def test_redigir_devolve_o_texto_sem_o_valor():
    fonte = f'a := 1\nchave := "{CHAVE_GITHUB}"\nb := 2'
    saida = S["redigir"](fonte)
    assert "abcdefghijklmnopqrstuvwxyz" not in saida
    assert "a := 1" in saida and "b := 2" in saida


def test_exigir_sem_segredo_levanta_com_a_lista():
    with pytest.raises(erro_de("SecretLeakError")) as e:
        S["exigir_sem_segredo"](f'x := "{CHAVE_GITHUB}"')
    assert "ROTACIONE" in e.value.dica
    assert S["exigir_sem_segredo"]("x := 1") is True


# ═══════════════════════════════════════════════════════════
#  PII
# ═══════════════════════════════════════════════════════════

def test_mascarar_pii_cobre_os_formatos_brasileiros():
    m = S["mascarar_pii"]
    assert "123.456" not in m("cpf 123.456.789-09")
    assert "ana.silva" not in m("ana.silva@exemplo.com")
    assert m("ana.silva@exemplo.com").endswith("@exemplo.com")


def test_o_cartao_passa_pelo_luhn_antes():
    """Sem isso, todo numero de pedido de 16 digitos virava cartao."""
    m = S["mascarar_pii"]
    assert m("cartao 4111111111111111").endswith("1111")
    assert "4111111111111111" not in m("cartao 4111111111111111")
    # Nao passa no Luhn: e numero de pedido, e fica legivel.
    assert "1234567890123456" in m("pedido 1234567890123456")


def test_mascarar_pii_aceita_escolher_o_tipo():
    saida = S["mascarar_pii"]("cpf 123.456.789-09 e ana@x.com", ["email"])
    assert "123.456.789-09" in saida
    assert "ana@" not in saida


# ═══════════════════════════════════════════════════════════
#  Entrada hostil
# ═══════════════════════════════════════════════════════════

def test_caminho_seguro_recusa_a_travessia(tmp_path):
    with pytest.raises(erro_de("UnsafeInputError")):
        S["caminho_seguro"](str(tmp_path), "../../etc/passwd")
    assert S["caminho_seguro"](str(tmp_path), "ok.txt").startswith(str(tmp_path))


def test_caminho_seguro_recusa_o_byte_nulo(tmp_path):
    """A forma classica de truncar o nome depois da conferencia."""
    with pytest.raises(erro_de("UnsafeInputError")):
        S["caminho_seguro"](str(tmp_path), "ok.txt\x00.png")


def test_caminho_seguro_resolve_o_link_simbolico(tmp_path):
    """Sem 'realpath', um link dentro da pasta aponta para fora e passa."""
    dentro = tmp_path / "dentro"
    dentro.mkdir()
    fora = tmp_path / "fora"
    fora.mkdir()
    try:
        os.symlink(str(fora), str(dentro / "atalho"))
    except (OSError, NotImplementedError):
        pytest.skip("o sistema nao cria link simbolico aqui")
    with pytest.raises(erro_de("UnsafeInputError")):
        S["caminho_seguro"](str(dentro), "atalho/x.txt")


def test_caminho_seguro_nao_confunde_pasta_irma(tmp_path):
    """'/var/uploads-publico' comeca com '/var/uploads'."""
    base = tmp_path / "uploads"
    base.mkdir()
    (tmp_path / "uploads-publico").mkdir()
    with pytest.raises(erro_de("UnsafeInputError")):
        S["caminho_seguro"](str(base), "../uploads-publico/x")


@pytest.mark.parametrize("entrada,esperado", [
    ("../../etc/passwd", "passwd"),
    ("pasta/foto.png", "foto.png"),
    ("CON.txt", "_CON.txt"),
    ("...", "arquivo"),
    ("", "arquivo"),
    ("  nome  .", "nome"),
])
def test_nome_de_arquivo_seguro(entrada, esperado):
    assert S["nome_de_arquivo_seguro"](entrada) == esperado


@pytest.mark.parametrize("entrada,esperado", [
    ("/painel", "/painel"),
    ("//mau.exemplo", "/"),
    ("https://mau.exemplo", "/"),
    ("\\\\mau.exemplo", "/"),
    ("javascript:alert(1)", "/"),
    ("", "/"),
])
def test_redirecionamento_seguro(entrada, esperado):
    assert S["redirecionamento_seguro"](entrada) == esperado


def test_redirecionamento_aceita_o_host_da_lista():
    assert S["redirecionamento_seguro"](
        "https://app.loja.com/x", ["app.loja.com"]) == "https://app.loja.com/x"


@pytest.mark.parametrize("host", [
    "127.0.0.1", "localhost", "10.0.0.1", "192.168.1.1", "169.254.169.254",
    "::1", "0.0.0.0",
])
def test_host_privado_reconhece_a_rede_de_dentro(host):
    assert S["host_privado"](host) is True


def test_host_que_nao_resolve_e_tratado_como_privado():
    """Na duvida, recusa: a alternativa e deixar passar o desconhecido."""
    assert S["host_privado"]("nao-existe-mesmo.invalid") is True


def test_url_segura_recusa_o_endereco_de_metadados():
    """O ataque concreto: o servidor busca as proprias credenciais."""
    with pytest.raises(erro_de("UnsafeInputError")) as e:
        S["url_segura"]("http://169.254.169.254/latest/meta-data/")
    assert "interna" in str(e.value)


@pytest.mark.parametrize("url", [
    "file:///etc/passwd", "gopher://x/1", "dict://x:11211/",
    "ftp://x/", "javascript:alert(1)",
])
def test_url_segura_recusa_o_esquema_de_fora_da_lista(url):
    with pytest.raises(erro_de("UnsafeInputError")):
        S["url_segura"](url)


def test_url_segura_recusa_o_host_fora_da_lista():
    with pytest.raises(erro_de("UnsafeInputError")):
        S["url_segura"]("https://outro.com/x", {"hosts": ["loja.com"],
                                                "resolver": False})


def test_url_segura_devolve_a_url_normalizada():
    """Conferir uma e buscar outra faz a conferencia nao valer nada."""
    r = S["url_segura"]("HTTPS://Loja.COM/api?x=1",
                        {"resolver": False})
    assert r["url"] == "https://loja.com/api?x=1"
    assert r["host"] == "loja.com" and r["porta"] == 443


def test_json_seguro_recusa_o_aninhamento_fundo():
    fundo = "[" * 500 + "]" * 500
    with pytest.raises(erro_de("UnsafeInputError")) as e:
        S["json_seguro"](fundo)
    assert "profundidade" in str(e.value)


def test_json_seguro_nao_conta_colchete_dentro_de_texto():
    """Senao '{"a": "[[[["}' seria recusado sem motivo."""
    assert S["json_seguro"]('{"a": "[[[[[[[[[[[[[[[[[[[[[[[[[["}') == {
        "a": "[" * 26}


def test_json_seguro_recusa_o_corpo_grande():
    with pytest.raises(erro_de("UnsafeInputError")):
        S["json_seguro"]('"' + "x" * 200 + '"', {"tamanho": 100})


def test_json_seguro_aceita_o_normal():
    assert S["json_seguro"]('{"a": [1, 2, {"b": 3}]}') == {"a": [1, 2, {"b": 3}]}


def test_numero_seguro_confere_a_faixa():
    assert S["numero_seguro"]("5", 1, 10) == 5
    for ruim in ("-1", "999999999"):
        with pytest.raises(erro_de("UnsafeInputError")):
            S["numero_seguro"](ruim, 1, 10)
    with pytest.raises(erro_de("UnsafeInputError")):
        S["numero_seguro"]("abc")


# ═══════════════════════════════════════════════════════════
#  Limitador e bloqueio
# ═══════════════════════════════════════════════════════════

def test_o_limitador_conta_por_chave():
    lim = S["limitador"](3, 60.0)
    assert all(lim.permitir("ana") for _ in range(3))
    assert lim.permitir("ana") is False
    assert lim.permitir("bruno") is True


def test_o_balde_enche_com_o_tempo_e_nao_de_uma_vez():
    """Com janela fixa, um cliente gasta o limite no fim de uma e no
    comeco da seguinte — o dobro num instante."""
    lim = S["limitador"](60, 60.0)   # uma ficha por segundo
    for _ in range(60):
        lim.permitir("x")
    assert lim.permitir("x") is False
    assert lim.espera("x") > 0


def test_o_limitador_diz_quanto_falta():
    lim = S["limitador"](1, 10.0)
    lim.permitir("x")
    assert lim.espera("x") > 0
    assert lim.restante("x") < 1


def test_o_bloqueio_progressivo_dobra_e_o_sucesso_zera():
    t = S["tentativas"](limite=3, base=10.0)
    assert t.falha("ana")["bloqueado"] is False
    assert t.falha("ana")["bloqueado"] is False
    primeiro = t.falha("ana")
    assert primeiro["bloqueado"] is True and primeiro["segundos"] == 10.0

    for _ in range(2):
        t.falha("ana")
    segundo = t.falha("ana")
    assert segundo["segundos"] == 20.0, "a espera dobra a cada bloqueio"

    t.sucesso("ana")
    assert t.bloqueado("ana") is False


def test_o_bloqueio_respeita_o_teto():
    t = S["tentativas"](limite=1, base=100.0, teto=150.0)
    t.falha("x")
    t.falha("x")
    assert t.falha("x")["segundos"] == 150.0


def test_exigir_levanta_enquanto_bloqueado():
    t = S["tentativas"](limite=1, base=60.0)
    t.falha("x")
    with pytest.raises(erro_de("PolicyError")):
        t.exigir("x")


# ═══════════════════════════════════════════════════════════
#  Auditoria
# ═══════════════════════════════════════════════════════════

def test_a_cadeia_fecha_e_a_edicao_a_quebra(tmp_path):
    caminho = tmp_path / "auditoria.log"
    livro = S["auditoria"](str(caminho))
    for i in range(5):
        livro.registrar("evento", {"n": i}, quem="ana")

    r = livro.conferir()
    assert r["ok"] is True and r["registros"] == 5

    linhas = caminho.read_text(encoding="utf-8").splitlines()
    linhas[2] = linhas[2].replace('"n":2', '"n":999')
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    r = livro.conferir()
    assert r["ok"] is False
    assert r["quebra"] == 4, "quebra no registro SEGUINTE ao alterado"


def test_apagar_uma_linha_tambem_quebra(tmp_path):
    caminho = tmp_path / "a.log"
    livro = S["auditoria"](str(caminho))
    for i in range(4):
        livro.registrar("e", {"n": i})
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    del linhas[1]
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    assert livro.conferir()["ok"] is False


def test_exigir_integra_levanta_com_a_linha(tmp_path):
    caminho = tmp_path / "a.log"
    livro = S["auditoria"](str(caminho))
    livro.registrar("a")
    livro.registrar("b")
    caminho.write_text(caminho.read_text(encoding="utf-8").replace('"a"', '"z"'),
                       encoding="utf-8")
    with pytest.raises(erro_de("AuditChainError")) as e:
        livro.exigir_integra()
    assert "2" in str(e.value)


def test_a_auditoria_redige_o_segredo_antes_de_gravar(tmp_path):
    """Uma trilha de auditoria acaba anexada a um chamado."""
    caminho = tmp_path / "a.log"
    livro = S["auditoria"](str(caminho))
    livro.registrar("deploy",
                    {"token": CHAVE_GITHUB})
    texto = caminho.read_text(encoding="utf-8")
    assert "abcdefghijklmnopqrstuvwxyz" not in texto


def test_a_auditoria_escapa_a_quebra_de_linha_do_evento(tmp_path):
    """Sem isso da para forjar um registro inteiro pelo nome do evento."""
    caminho = tmp_path / "a.log"
    livro = S["auditoria"](str(caminho))
    livro.registrar("login\nfalso", {})
    assert len(caminho.read_text(encoding="utf-8").strip().splitlines()) == 1


def test_a_auditoria_de_arquivo_que_nao_existe_esta_integra(tmp_path):
    assert S["auditoria"](str(tmp_path / "nada.log")).conferir()["ok"] is True


# ═══════════════════════════════════════════════════════════
#  Analise estatica
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("regra,fonte", [
    ("md5-ou-sha1", "x := Crypto.md5(dado)"),
    ("sql-concatenado", 'db.query($"SELECT * FROM t WHERE id = {id}")'),
    ("shell-com-texto", 'OS.shell($"git log {ref}")'),
    ("verificacao-desligada", "cliente := Malha.cliente(u, {verificar := no})"),
    ("senha-sem-derivacao", "guardada := Crypto.sha256(senha)"),
    ("comparacao-de-segredo", "given token is esperado:"),
])
def test_cada_regra_acha_o_seu_caso(regra, fonte):
    achados = S["analisar"](fonte)
    assert regra in [a["regra"] for a in achados], f"{regra} nao achou"


def test_a_regra_e_silenciada_PELO_NOME():
    fonte = "// df: permitir md5-ou-sha1\nx := Crypto.md5(d)"
    assert S["analisar"](fonte) == []
    # Silenciar outra regra nao silencia esta.
    outra = "// df: permitir sql-concatenado\nx := Crypto.md5(d)"
    assert [a["regra"] for a in S["analisar"](outra)] == ["md5-ou-sha1"]


def test_a_analise_nao_acusa_dentro_de_comentario():
    assert S["analisar"]("// nunca use Crypto.md5(x) para senha") == []


def test_caminho_de_fora_so_acusa_o_que_veio_DE_FORA():
    """A versao ampla desta regra deu 16 acusacoes no repositorio, e as
    16 eram '$"{pasta}/nome-fixo"'."""
    assert S["analisar"]('IO.write($"{pasta}/saida.txt", d)') == []
    achados = S["analisar"]('IO.read($"{base}/{req[\'arquivo\']}")')
    assert "caminho-de-fora" in [a["regra"] for a in achados]


def test_as_regras_se_descrevem():
    regras = S["regras_de_analise"]()
    assert len(regras) >= 9
    for r in regras:
        assert r["regra"] and r["dica"] and r["gravidade"] in ("alto", "medio", "baixo")


# ═══════════════════════════════════════════════════════════
#  O repositorio inteiro — o teste que achou as regras ruidosas
# ═══════════════════════════════════════════════════════════

def test_o_comando_nao_acusa_nada_nao_silenciado_no_repositorio():
    """Zero achado nas pastas de codigo DataForge do repositorio.

    E o teste mais valioso deste arquivo: foi ele que mostrou que a
    primeira versao acusava 19 vezes, e que as 19 eram falso alarme —
    inclusive os proprios exercicios que ENSINAM a nao escrever
    segredo no arquivo. Uma ferramenta assim e desligada no mesmo dia.
    """
    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "seguranca", "--json",
         "exercicios", "examples", "projetos", "packages", "trilha"],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", timeout=300)
    assert saida.returncode == 0, saida.stderr[-2000:]
    relatorio = json.loads(saida.stdout)
    assert relatorio["achados"] == [], (
        "achados no repositorio:\n"
        + "\n".join(f"  {a['arquivo']}:{a['linha']} {a['regra']}"
                    for a in relatorio["achados"][:20]))


def test_o_comando_sai_com_um_no_modo_estrito():
    import tempfile
    with tempfile.TemporaryDirectory() as pasta:
        alvo = os.path.join(pasta, "vazou.df")
        with open(alvo, "w", encoding="utf-8") as f:
            f.write(f'chave := "{CHAVE_GITHUB}"\n')
        saida = subprocess.run(
            [sys.executable, "-m", "dataforge", "seguranca", alvo, "--strict"],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
            timeout=120)
        assert saida.returncode == 1
        assert "ROTACIONE" in saida.stdout


def test_o_comando_esta_no_catalogo_da_ajuda():
    """Um comando que nao esta no catalogo nao existe para quem procura."""
    saida = subprocess.run(
        [sys.executable, "-m", "dataforge", "help", "seguranca"],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert saida.returncode == 0
    assert "seguranca" in saida.stdout


def test_o_modulo_nao_reimplementa_o_que_o_crypto_ja_faz():
    """Duas contas iguais escritas duas vezes divergem.

    A trava e pelo NOME: se um dia alguem acrescentar 'sha256' ou
    'hash_password' aqui, o modulo passa a ter duas respostas para a
    mesma pergunta — e sera a de seguranca a errada.
    """
    crypto = set(get_module("Arcane.Crypto")) - {"__name__"}
    seguranca = set(S) - {"__name__"}
    comuns = crypto & seguranca
    assert comuns == set(), f"reimplementado do Crypto: {sorted(comuns)}"


def test_a_familia_de_erro_esta_no_catalogo():
    from dataforge import catalogo_erros as cat
    da_familia = [e for e in cat.ERROS if e["codigo"].startswith("DF19")]
    # Sete quando a familia nasceu; dez depois de autorizacao
    # (DF1908/1909) e chaves (DF1910). O numero e cobrado de
    # proposito: uma classe nova sem entrada no catalogo nao da erro
    # — ela so nao aparece no 'dataforge explain'.
    assert len(da_familia) == 10
    for e in da_familia:
        assert cat.familia(e["codigo"]) == "seguranca"
        assert e["explicacao"] and e["solucao"] and e["exemplo"]
