# -*- coding: utf-8 -*-
"""Os seis módulos que fechavam os buracos da biblioteca.

Cada um existe porque alguma coisa comum não tinha como ser feita:

    Arcane.Bytes    falar um protocolo, ler um formato binário
    Arcane.Rede     TCP, UDP, DNS e TLS — o que está abaixo do HTTP
    Arcane.Eventos  duas partes conversando sem se conhecerem
    Arcane.Cli      a linha de comando de um programa em DataForge
    Arcane.Email    mandar e-mail sem contratar um serviço
    Arcane.Html     ler uma página sem expressão regular
"""

import os
import sys
import threading
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib import get_module                      # noqa: E402

B = get_module("Arcane.Bytes")
R = get_module("Arcane.Rede")
E = get_module("Arcane.Eventos")
C = get_module("Arcane.Cli")
M = get_module("Arcane.Email")
H = get_module("Arcane.Html")
MATH = get_module("Arcane.Math")


# ══════════════════════════════════════════════════════════════
#  Bytes
# ══════════════════════════════════════════════════════════════

def test_o_formato_exige_a_ordem_dos_bytes():
    """`i32` sem ordem não existe aqui, e é deliberado.

    Um inteiro escrito na ordem da MÁQUINA e lido na ordem da rede dá
    um número diferente, o programa não falha, e o dado sai errado do
    outro lado — a falha mais cara desta área inteira.
    """
    from dataforge.stdlib.arcane_bytes import ErroDeBytes

    with pytest.raises(ErroDeBytes) as erro:
        B["empacotar"]("i32", 1)
    assert "ORDEM DOS BYTES" in str(erro.value)

    assert B["empacotar"](">i32", 1) == b"\x00\x00\x00\x01"
    assert B["empacotar"]("<i32", 1) == b"\x01\x00\x00\x00"


def test_o_cursor_anda_sozinho():
    """Ler com fatias exige acertar o deslocamento de cada campo, e um
    erro num deles desalinha tudo o que vem depois — com o programa
    entregando números plausíveis e errados."""
    dados = B["empacotar"](">u8 u16 u32", 1, 258, 70000)
    leitor = B["ler"](dados)
    assert leitor.ler("u8") == 1
    assert leitor.ler("u16") == 258
    assert leitor.ler("u32") == 70000
    assert leitor.acabou


def test_ler_alem_do_fim_diz_quanto_falta():
    from dataforge.stdlib.arcane_bytes import ErroDeBytes

    leitor = B["ler"](b"\x01\x02")
    leitor.ler("u8")
    with pytest.raises(ErroDeBytes) as erro:
        leitor.ler("u32")
    texto = str(erro.value)
    assert "pede 4" in texto and "1 ate o fim" in texto


def test_a_janela_nao_copia():
    """Copiar um arquivo de 200 MB para ler 8 bytes é o jeito mais
    fácil de estourar a memória."""
    grande = bytes(range(256)) * 100
    vista = B["janela"](grande, 10, 18)
    assert isinstance(vista, memoryview)
    assert len(vista) == 8
    assert B["copiar"](vista) == grande[10:18]


def test_a_comparacao_de_segredo_e_em_tempo_fixo():
    """Uma comparação comum para no primeiro byte diferente, e o TEMPO
    conta quantos bateram — é assim que um token é descoberto byte a
    byte."""
    assert B["igual_em_tempo_fixo"](b"segredo", b"segredo")
    assert not B["igual_em_tempo_fixo"](b"segredo", b"segredx")


def test_o_despejo_mostra_o_byte_a_mais():
    linhas = B["despejo"](b"DataForge\x00\x01").split("\n")
    assert linhas[0].startswith("00000000")
    assert "44 61 74 61" in linhas[0]          # 'Data'
    assert "|DataForge..|" in linhas[0]


def test_bits_ida_e_volta():
    assert B["bits"](b"\x05") == "00000101"
    assert B["de_bits"]("00000101") == b"\x05"
    from dataforge.stdlib.arcane_bytes import ErroDeBytes
    with pytest.raises(ErroDeBytes):
        B["de_bits"]("0101")                  # não forma byte inteiro


# ══════════════════════════════════════════════════════════════
#  Rede
# ══════════════════════════════════════════════════════════════

def test_tcp_ida_e_volta():
    recebido = []

    def atender(conexao):
        recebido.append(conexao.receber_linha())
        conexao.enviar_linha("pong")

    # Sem 'esperar_porta' aqui de proposito: 'servir_em_segundo_plano'
    # so volta depois do 'listen', entao a porta JA esta aberta. E
    # 'porta_aberta' abre uma conexao de verdade — o servidor a contaria
    # como um cliente que conectou e sumiu.
    servidor = R["servir_em_segundo_plano"](atender, porta=0)
    try:
        cliente = R["conectar"]("127.0.0.1", servidor.porta)
        cliente.enviar_linha("ping")
        assert cliente.receber_linha() == "pong"
        cliente.fechar()
        assert recebido == ["ping"]
    finally:
        servidor.parar()


def test_receber_exato_insiste_ate_completar():
    """O `recv` devolve menos do que se pediu com frequência, e tratar o
    retorno curto como a mensagem inteira corrompe a próxima."""
    def atender(conexao):
        # De propósito em três pedaços, com pausa.
        for pedaco in (b"abc", b"def", b"ghij"):
            conexao.enviar(pedaco)
            time.sleep(0.02)

    servidor = R["servir_em_segundo_plano"](atender, porta=0)
    try:
        cliente = R["conectar"]("127.0.0.1", servidor.porta)
        assert cliente.receber_exato(10) == b"abcdefghij"
        cliente.fechar()
    finally:
        servidor.parar()


def test_a_linha_sem_fim_tem_teto():
    """Um cliente que manda bytes sem nunca mandar a quebra enche a
    memória do servidor — e é um ataque de uma linha."""
    from dataforge.stdlib.arcane_rede import ErroDeRede

    def atender(conexao):
        conexao.enviar(b"x" * 5000)
        time.sleep(0.3)

    servidor = R["servir_em_segundo_plano"](atender, porta=0)
    try:
        cliente = R["conectar"]("127.0.0.1", servidor.porta)
        with pytest.raises(ErroDeRede) as erro:
            cliente.receber_linha(limite=100)
        assert "enche a memoria" in str(erro.value)
        cliente.fechar()
    finally:
        servidor.parar()


def test_udp_manda_e_esquece():
    alvo = R["udp"](porta=0, escutar=True)
    emissor = R["udp"]()
    try:
        emissor.enviar("metrica=1", "127.0.0.1", alvo.porta)
        chegou = alvo.receber(prazo=3.0)
        assert chegou["dados"] == b"metrica=1"
        assert chegou["host"] == "127.0.0.1"
    finally:
        alvo.fechar()
        emissor.fechar()


def test_o_erro_de_conexao_diz_o_que_significa():
    from dataforge.stdlib.arcane_rede import ErroDeRede

    livre = R["porta_livre"]()
    with pytest.raises(ErroDeRede) as erro:
        R["conectar"]("127.0.0.1", livre, prazo=2)
    assert "RECUSADA" in str(erro.value)


def test_esperar_porta_diz_por_que_nao_abriu():
    from dataforge.stdlib.arcane_rede import ErroDeRede

    with pytest.raises(ErroDeRede) as erro:
        R["esperar_porta"]("127.0.0.1", R["porta_livre"](), prazo=0.5)
    assert "0.0.0.0" in str(erro.value), (
        "a dica sobre subir em 127.0.0.1 é o caso mais comum")


def test_dns_resolve_o_localhost():
    ips = R["resolver"]("localhost")
    assert any(i["ip"] in ("127.0.0.1", "::1") for i in ips)


# ══════════════════════════════════════════════════════════════
#  Eventos
# ══════════════════════════════════════════════════════════════

def test_emitir_devolve_quantos_ouviram():
    """Zero é informação: um evento com o nome errado não falha, ele
    simplesmente não chega — a falha mais difícil de achar aqui."""
    em = E["emissor"]()
    em.ao("venda", lambda v: None)
    assert em.emitir("venda", 1) == 1
    assert em.emitir("vendaa", 1) == 0


def test_o_ouvinte_que_quebra_sai_da_lista():
    """Um ouvinte quebrado que continua inscrito quebra a cada evento,
    para sempre, e some no meio do log."""
    em = E["emissor"]()
    bons = []
    em.ao("x", lambda v: 1 / 0)
    em.ao("x", lambda v: bons.append(v))

    assert em.emitir("x", 1) == 1, "o bom recebeu mesmo com o outro quebrando"
    assert len(em.erros) == 1
    assert em.ouvintes("x") == 1, "o quebrado saiu"
    assert em.emitir("x", 2) == 1
    assert bons == [1, 2]


def test_uma_vez_ouve_so_o_proximo():
    em = E["emissor"]()
    contagem = []
    em.uma_vez("x", lambda: contagem.append(1))
    em.emitir("x")
    em.emitir("x")
    assert len(contagem) == 1


def test_o_curinga_ouve_tudo():
    em = E["emissor"]()
    tudo = []
    em.ao("*", lambda nome, *r: tudo.append(nome))
    em.emitir("a")
    em.emitir("b")
    assert tudo == ["a", "b"]


def test_inscrever_num_laco_e_recusado():
    """Esse número quase sempre significa um `ao(...)` dentro de um laço
    — cada volta inscreve mais um, e nenhum sai."""
    from dataforge.stdlib.arcane_eventos import ErroDeEventos

    em = E["emissor"](teto=5)
    for _ in range(5):
        em.ao("x", lambda: None)
    with pytest.raises(ErroDeEventos) as erro:
        em.ao("x", lambda: None)
    assert "dentro de um laco" in str(erro.value)


def test_o_contexto_e_por_thread():
    """Um vault global serviria até o segundo pedido simultâneo, e aí o
    id de um apareceria no log do outro."""
    vistos = {}

    def trabalho(nome):
        E["com_contexto"]({"quem": nome},
                          lambda: vistos.__setitem__(nome, E["por"]("quem")))

    fios = [threading.Thread(target=trabalho, args=(f"t{i}",))
            for i in range(8)]
    for f in fios:
        f.start()
    for f in fios:
        f.join()
    assert vistos == {f"t{i}": f"t{i}" for i in range(8)}


def test_a_fila_roda_em_segundo_plano():
    feitos = []
    f = E["fila"](lambda item: feitos.append(item), operarios=3)
    for i in range(20):
        f.publicar(i)
    f.esperar(prazo=5)
    f.parar()
    assert sorted(feitos) == list(range(20))


# ══════════════════════════════════════════════════════════════
#  Cli
# ══════════════════════════════════════════════════════════════

def _comando():
    c = C["comando"]("forja", sobre="Sobe a forja.", versao="1.0.0")
    c.opcao("porta", "inteiro", curta="p", padrao=8080, sobre="a porta")
    c.opcao("modo", escolhas=["dev", "prod"], padrao="dev")
    c.opcao("verboso", "sim_nao", curta="v")
    c.opcao("tags", "lista", sobre="separadas por vírgula")
    c.posicional("arquivo", exigido=False)
    return c


def test_le_opcoes_longas_curtas_e_coladas():
    c = _comando()
    assert c.ler(["--porta", "9000"])["porta"] == 9000
    assert c.ler(["--porta=9000"])["porta"] == 9000
    assert c.ler(["-p", "9000"])["porta"] == 9000
    assert c.ler(["-p9000"])["porta"] == 9000
    assert c.ler(["-v"])["verboso"] is True
    assert c.ler([])["porta"] == 8080
    assert c.ler(["--tags", "a,b,c"])["tags"] == ["a", "b", "c"]


def test_a_opcao_errada_sugere_a_certa():
    from dataforge.stdlib.arcane_cli import SaidaDaCli

    with pytest.raises(SaidaDaCli) as fim:
        _comando().ler(["--portaa", "1"])
    assert fim.value.codigo == 2, (
        "código 1 é 'rodou e deu errado'; 2 é 'você chamou errado'")
    assert "--porta" in fim.value.texto


def test_o_tipo_e_a_escolha_sao_cobrados():
    from dataforge.stdlib.arcane_cli import SaidaDaCli

    with pytest.raises(SaidaDaCli) as fim:
        _comando().ler(["--porta", "abc"])
    assert "espera inteiro" in fim.value.texto

    with pytest.raises(SaidaDaCli) as fim:
        _comando().ler(["--modo", "x"])
    assert "dev, prod" in fim.value.texto


def test_a_ajuda_sai_da_declaracao():
    """Escrita à mão, ela envelhece no primeiro flag novo — e a ajuda
    errada é pior que nenhuma, porque quem lê confia nela."""
    ajuda = _comando().ajuda()
    assert "--porta" in ajuda and "padrão: 8080" in ajuda
    assert "-p, --porta" in ajuda
    assert "dev|prod" in ajuda
    assert "--ajuda" in ajuda and "--versao" in ajuda


def test_subcomandos():
    c = C["comando"]("forja")
    subir = c.subcomando("subir", "põe no ar")
    subir.opcao("porta", "inteiro", padrao=80)
    c.subcomando("parar", "tira do ar")

    lido = c.ler(["subir", "--porta", "90"])
    assert lido["__comando__"] == "subir" and lido["porta"] == 90
    assert "subir" in c.ajuda() and "põe no ar" in c.ajuda()


def test_perguntar_recusa_sem_terminal():
    """Numa pipeline de CI, uma pergunta trava o build para sempre, sem
    dizer por quê."""
    from dataforge.stdlib.arcane_cli import ErroDeCli

    with pytest.raises(ErroDeCli) as erro:
        C["perguntar"]("nome?")
    assert "não há terminal" in str(erro.value)
    assert "opção de linha de comando" in str(erro.value)


# ══════════════════════════════════════════════════════════════
#  Email
# ══════════════════════════════════════════════════════════════

def test_a_copia_oculta_nao_vai_no_cabecalho():
    """Um Bcc escrito no cabeçalho é visível para todo mundo — o oposto
    do que ele significa."""
    m = (M["mensagem"]("de@x.br", "para@x.br", "oi")
         .texto("corpo")
         .copia_oculta(["secreto@x.br"]))
    cabecalho = m.como_texto().split("\n\n")[0]
    assert "secreto@x.br" not in cabecalho
    assert "secreto@x.br" in m.destinatarios(), "mas ele recebe"


def test_montar_e_puro():
    """A primeira versão montava sobre o mesmo objeto, e `prever()`
    antes de `enviar()` quebrava o envio."""
    m = M["mensagem"]("de@x.br", "para@x.br", "oi").texto("corpo")
    assert m.prever()["tamanho"] == m.prever()["tamanho"]
    assert m.como_texto() == m.como_texto()


def test_o_html_ganha_alternativa_em_texto():
    """Sem ela, o cliente de texto puro mostra a marcação crua — e é o
    que boa parte dos leitores de tela recebe."""
    m = (M["mensagem"]("de@x.br", "para@x.br", "oi")
         .html("<h1>Olá</h1><p>tudo bem</p>"))
    assert m.prever()["texto"] == "Olá tudo bem"


def test_o_endereco_invalido_e_recusado_na_hora():
    from dataforge.stdlib.arcane_email import ErroDeEmail

    with pytest.raises(ErroDeEmail):
        M["mensagem"]("de@x.br", "nao-e-email", "oi")
    assert M["valido"]("a@b.co") and not M["valido"]("a@b")


def test_a_caixa_de_teste_tem_o_mesmo_contrato():
    caixa = M["caixa"]()
    m = M["mensagem"]("de@x.br", "ana@x.br", "oi").texto("c")
    r = caixa.enviar(m)
    assert r["ok"] and r["entregues"] == ["ana@x.br"]
    assert len(caixa.para("ana@x.br")) == 1
    assert caixa.ultimo()["assunto"] == "oi"


# ══════════════════════════════════════════════════════════════
#  Html
# ══════════════════════════════════════════════════════════════

PAGINA = """
<html><body>
  <div class="produto destaque" id="p1">
    <h2>Bigorna</h2>
    <span class="preco"><b>R$</b> <span>450,00</span></span>
    <a href="/produto/1">Ver</a>
  </div>
  <div class="produto"><h2>Marreta</h2><span class="preco">R$ 75,00</span></div>
  <table><tr><th>Item</th><th>Preço</th></tr>
         <tr><td>Bigorna</td><td>450</td></tr></table>
</body></html>
"""


def test_o_seletor_css_acha_por_tag_classe_e_id():
    doc = H["ler"](PAGINA)
    assert len(doc.achar_todos("div.produto")) == 2
    assert doc.achar("#p1 h2").texto == "Bigorna"
    assert doc.achar("div.destaque").id == "p1"
    assert len(doc.achar_todos("div.produto > h2")) == 2


def test_o_texto_junta_com_espaco():
    """`<b>R$</b><span>10</span>` colado vira "R$10"; com espaço,
    "R$ 10" — que é o que a página mostra."""
    assert H["ler"](PAGINA).achar("#p1 .preco").texto == "R$ 450,00"


def test_links_viram_absolutos():
    links = H["ler"](PAGINA).links("https://forja.br/loja/")
    assert links[0]["destino"] == "https://forja.br/produto/1"


def test_a_tabela_vira_dado():
    tabela = H["ler"](PAGINA).tabela()
    assert tabela["cabecalho"] == ["Item", "Preço"]
    assert tabela["linhas"] == [["Bigorna", "450"]]


def test_limpar_tira_o_conteudo_do_script_tambem():
    """Um `limpar` que só tira as tags deixa o corpo do `<script>` como
    texto — e aí o "texto limpo" contém o código que se queria tirar."""
    sujo = "<p>antes</p><script>roubar()</script><p>depois</p>"
    limpo = H["limpar"](sujo)
    assert "roubar" not in limpo
    assert limpo == "antes depois"


def test_podar_usa_lista_de_PERMITIDAS():
    """Uma lista de proibidas esquece a próxima tag perigosa que o
    navegador inventar."""
    podado = H["podar"](
        '<p>ok</p><iframe src="x"></iframe><b>b</b>'
        '<a href="javascript:mau()">clique</a>')
    assert "iframe" not in podado
    assert "<b>b</b>" in podado
    assert "javascript" not in podado, "href perigoso vira <a> sem destino"


def test_escapar_protege_contra_xss():
    assert H["escapar"]('<script>"x"</script>') == \
        "&lt;script&gt;&quot;x&quot;&lt;/script&gt;"


def test_tag_sem_fechar_nao_derruba_a_leitura():
    """HTML real quase nunca é bem formado."""
    doc = H["ler"]("<div><p>um<p>dois<br><span>tres</div>")
    assert "um" in doc.texto and "tres" in doc.texto


# ══════════════════════════════════════════════════════════════
#  Math: fração e complexo
# ══════════════════════════════════════════════════════════════

def test_a_fracao_e_exata_onde_o_decimal_nao_alcanca():
    """O Decimal é exato em BASE DEZ; 1/3 não tem forma decimal finita."""
    um_terco = MATH["fracao"](1, 3)
    assert MATH["fracao_texto"](
        MATH["fracao_soma"](um_terco, um_terco, um_terco)) == "1"
    assert MATH["fracao_partes"](MATH["fracao"](6, 8)) == [3, 4], "reduz"


def test_a_fracao_de_um_float_e_a_que_a_pessoa_quis_dizer():
    """De float vem a fração EXATA daquele float — que para 0.1 é
    3602879701896397/36028797018963968, e não 1/10."""
    assert MATH["fracao_texto"](MATH["fracao"](0.1)) == "1/10"
    assert MATH["fracao_texto"](MATH["fracao"](0.25)) == "1/4"


def test_o_complexo_se_escreve_com_i():
    """'3 + 4i', que é como se escreve — e não o 'j' do Python."""
    z = MATH["complexo"](3, 4)
    assert MATH["complexo_texto"](z) == "3 + 4i"
    assert MATH["complexo_modulo"](z) == 5.0
    assert MATH["complexo_texto"](MATH["complexo_raiz"](
        MATH["complexo"](-9))) == "3i"


def test_porta_aberta_abre_uma_conexao_de_verdade():
    """Não há como perguntar sem bater na porta.

    Um servidor que conta conexões vai ver esta também. Documentar isso
    importa: um teste que conta o que chegou e usa `esperar_porta` no
    mesmo servidor recebe uma conexão vazia a mais — foi assim que este
    teste nasceu.
    """
    conexoes = []
    servidor = R["servir_em_segundo_plano"](
        lambda c: conexoes.append(1), porta=0)
    try:
        assert R["porta_aberta"]("127.0.0.1", servidor.porta)
        time.sleep(0.1)
        assert conexoes == [1], "a checagem apareceu como uma conexão"
    finally:
        servidor.parar()
