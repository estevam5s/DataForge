# -*- coding: utf-8 -*-
"""Arcane.Telegram — bots, testados sem token e sem rede.

O que estes testes protegem, em ordem de quanto custa descobrir na
prática:

1. **O token nunca sai numa mensagem de erro.** Ele está na URL de
   toda chamada, e a URL entra em todo traceback. Um token num log de
   CI é um bot sequestrado, e o @BotFather não avisa.

2. **O escape do MarkdownV2.** Um hífen ou um ponto sem escape faz o
   Telegram recusar a mensagem **inteira** com 400 — e o texto que
   quebra costuma ser o que veio do usuário, então funciona em teste e
   falha em produção.

3. **Uma rota registrada depois de `qualquer` nunca é alcançada.** O
   bot responde "não entendi" a um comando que existe, e quem escreveu
   procura o defeito no tratador certo.

4. **O `offset` só avança depois do update ser tratado.** Avançar antes
   perde a mensagem quando o processo cai no meio.

5. **Polling e webhook são o MESMO caminho.** Um bot testado em
   polling que quebra ao virar webhook quebra exatamente ao ir para
   produção.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import get_module


@pytest.fixture
def Tg():
    return get_module("Arcane.Telegram")


@pytest.fixture
def app(Tg):
    return Tg["app"]("123456:AAHtoken_de_teste")


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

def test_o_modulo_responde_pelos_tres_nomes():
    for nome in ("Arcane.Telegram", "Telegram", "Bot"):
        modulo = get_module(nome)
        assert modulo is not None and modulo["__name__"] == "Arcane.Telegram"


def test_o_catalogo_descreve_o_modulo():
    from dataforge.stdlib.catalogo import DESCRICOES

    assert "Arcane.Telegram" in DESCRICOES
    descricao, curto = DESCRICOES["Arcane.Telegram"]
    assert len(descricao) > 80 and curto == "Telegram"


# ═══════════════════════════════════════════════════════════
#  O token
# ═══════════════════════════════════════════════════════════

def test_um_token_vazio_diz_onde_conseguir_um(Tg):
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        Tg["bot"]("")
    assert "BotFather" in str(erro.value.nota)


def test_um_token_sem_dois_pontos_e_recusado_na_hora(Tg):
    """Sem os dois pontos o Telegram responde 404, e não 401 — o que
    manda procurar o erro no lugar errado."""
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        Tg["bot"]("token-sem-dois-pontos")
    assert "404" in str(erro.value.nota)


def test_o_token_nunca_aparece_num_erro(Tg):
    from dataforge.stdlib import arcane_telegram as T

    token = "123456:AAHsegredo_que_nao_pode_vazar"
    texto = T._esconder(
        f"<urlopen error> https://api.telegram.org/bot{token}/getMe", token)
    assert token not in texto and "segredo_que_nao_pode_vazar" not in texto
    assert "<token>" in texto


def test_o_segredo_do_ambiente_falha_dizendo_o_que_fazer(Tg, monkeypatch):
    from dataforge.errors import RuntimeError_

    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    with pytest.raises(RuntimeError_) as erro:
        Tg["segredo_do_ambiente"]()
    assert "export" in str(erro.value.dica)

    monkeypatch.setenv("TELEGRAM_TOKEN", "  9:AAH  ")
    assert Tg["segredo_do_ambiente"]() == "9:AAH", "o espaço em volta ficou"


# ═══════════════════════════════════════════════════════════
#  Formatação
# ═══════════════════════════════════════════════════════════

def test_o_escape_cobre_todos_os_reservados(Tg):
    """A lista é a da documentação do Telegram, e é maior do que
    qualquer um espera: o ponto e o hífen estão nela."""
    from dataforge.stdlib.arcane_telegram import _RESERVADOS

    for c in _RESERVADOS:
        assert Tg["escapar"](f"a{c}b") == f"a\\{c}b", f"não escapou {c!r}"


def test_o_escape_pega_o_ponto_e_o_hifen(Tg):
    """São os dois que quebram um texto normal — um preço, uma data."""
    assert Tg["escapar"]("R$ 1.099,90 - hoje") == "R$ 1\\.099,90 \\- hoje"


def test_o_html_escapa_o_e_comercial_primeiro(Tg):
    """Trocar '<' antes de '&' geraria '&amp;lt;' — o escape do escape."""
    assert Tg["escapar_html"]("a & b < c") == "a &amp; b &lt; c"


def test_o_codigo_em_linha_escapa_so_a_crase(Tg):
    """Escapar o ponto dentro de um bloco de código o mostraria na tela."""
    assert Tg["codigo"]("a.b") == "`a.b`"
    assert "\\`" in Tg["codigo"]("crase ` aqui")


def test_a_marcacao_monta_o_que_o_telegram_espera(Tg):
    assert Tg["negrito"]("oi") == "*oi*"
    assert Tg["link"]("site", "https://x.dev") == "[site](https://x.dev)"
    assert Tg["mencao"]("Ana", 42) == "[Ana](tg://user?id=42)"


# ═══════════════════════════════════════════════════════════
#  Teclados
# ═══════════════════════════════════════════════════════════

def test_um_botao_com_dados_e_url_e_recusado(Tg):
    """O Telegram recusa o teclado INTEIRO nesse caso, e a mensagem
    dele não diz qual botão é o culpado."""
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_):
        Tg["botao"]("x", dados="a", url="https://x.dev")


def test_o_dados_do_botao_e_medido_em_BYTES(Tg):
    """O limite do protocolo é 64 bytes. Um texto com acento estoura
    antes do que parece, e o Telegram recusa o teclado inteiro."""
    from dataforge.errors import RuntimeError_

    assert Tg["botao"]("ok", dados="a" * 64)["callback_data"]
    with pytest.raises(RuntimeError_) as erro:
        Tg["botao"]("ok", dados="á" * 33)
    assert "bytes" in str(erro.value.nota)


def test_os_teclados_saem_no_formato_da_bot_api(Tg):
    inline = Tg["botoes"]([[Tg["botao"]("Sim", dados="s")]])
    assert inline["inline_keyboard"][0][0]["callback_data"] == "s"

    normal = Tg["teclado"]([["A", "B"]])
    assert normal["keyboard"] == [[{"text": "A"}, {"text": "B"}]]
    assert normal["resize_keyboard"] is True


# ═══════════════════════════════════════════════════════════
#  Roteamento
# ═══════════════════════════════════════════════════════════

def test_o_comando_casa_com_a_forma_de_grupo(Tg, app):
    """Em grupo o Telegram manda '/start@meubot'. Um bot que não trata
    essa forma fica mudo lá dentro — e funciona em privado."""
    vistos = []
    app.comando("start")(lambda ctx: vistos.append(ctx.texto))
    t = Tg["testar"](app)

    t.mandar("/start")
    t.mandar("/start@meubot")
    t.mandar("/start com argumento")
    assert len(vistos) == 3


def test_o_comando_entrega_os_argumentos_separados(Tg, app):
    argumentos = []
    app.comando("somar")(lambda ctx: argumentos.append(ctx.args))
    Tg["testar"](app).comando("somar", 2, 3)
    assert argumentos == [["2", "3"]]


def test_uma_rota_depois_do_qualquer_e_recusada(Tg, app):
    """Ela nunca seria alcançada: o despacho para no primeiro que casa.

    É a mesma classe do `point` inalcançável, que o `check` acusa na
    linguagem — e aqui o registro acontece na partida, então falhar
    nele é falhar antes de qualquer pessoa conversar com o bot.
    """
    from dataforge.errors import RuntimeError_

    app.qualquer()(lambda ctx: None)
    with pytest.raises(RuntimeError_) as erro:
        app.comando("start")(lambda ctx: None)
    assert "nunca seria alcancada" in str(erro.value.message)


def test_so_UM_tratador_atende_cada_update(Tg, app):
    """Dois tratadores respondendo produzem duas mensagens para uma, e
    ninguém descobre de onde veio a segunda."""
    chamados = []
    app.texto(r"oi")(lambda ctx: chamados.append("primeiro"))
    app.texto(r"oi")(lambda ctx: chamados.append("segundo"))
    Tg["testar"](app).mandar("oi")
    assert chamados == ["primeiro"]


def test_o_comando_nao_cai_no_tratador_de_texto(Tg, app):
    """Um '/' no começo é comando, e um tratador de texto que o
    engolisse faria todo comando novo parar de funcionar."""
    textos = []
    app.texto()(lambda ctx: textos.append(ctx.texto))
    Tg["testar"](app).mandar("/qualquer")
    assert textos == []


def test_a_midia_e_casada_pela_especie(Tg, app):
    vistas = []
    app.midia("foto")(lambda ctx: vistas.append("foto"))
    app.midia("documento")(lambda ctx: vistas.append("doc"))
    t = Tg["testar"](app)
    t.enviar_foto()
    t.enviar_documento()
    assert vistas == ["foto", "doc"]


def test_uma_especie_de_midia_que_nao_existe_lista_as_que_existem(Tg, app):
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        app.midia("holograma")
    assert "foto" in str(erro.value.nota)


def test_o_callback_chega_com_os_dados(Tg, app):
    recebidos = []
    app.botao(r"^rem:(\d+)$")(lambda ctx: recebidos.append(ctx.dados))
    Tg["testar"](app).clicar("rem:42")
    assert recebidos == ["rem:42"]


def test_a_edicao_de_mensagem_nao_e_tratada_como_mensagem_nova(Tg, app):
    """Trocar a ordem faria o bot responder de novo cada vez que alguém
    corrige um typo."""
    from dataforge.stdlib.arcane_telegram_app import _tipo_do_update

    tipo, _ = _tipo_do_update({"edited_message": {"text": "x"},
                               "message": {"text": "x"}})
    assert tipo == "editada"


# ═══════════════════════════════════════════════════════════
#  Middleware e erro
# ═══════════════════════════════════════════════════════════

def test_o_middleware_pode_interromper(Tg, app):
    atendidos = []
    app.antes_de_cada()(lambda ctx: False)
    app.qualquer()(lambda ctx: atendidos.append(1))
    Tg["testar"](app).mandar("oi")
    assert atendidos == [] and app.metricas["ignorados"] == 1


def test_um_erro_no_tratador_nao_derruba_o_bot(Tg, app):
    """Um bot que morre porque alguém mandou um emoji inesperado é um
    bot que fica fora do ar de madrugada."""
    def quebrar(ctx):
        raise ValueError("estourou")

    app.comando("quebra")(quebrar)
    app.qualquer()(lambda ctx: ctx.responder("vivo"))

    t = Tg["testar"](app)
    t.comando("quebra")
    assert t.falhou()
    t.mandar("e depois?")
    assert t.ultima() == "vivo", "o bot morreu no primeiro erro"


def test_o_tratador_de_erro_recebe_o_erro(Tg, app):
    vistos = []
    app.ao_falhar()(lambda ctx, erro: vistos.append(str(erro)))
    app.comando("x")(lambda ctx: 1 / 0)
    Tg["testar"](app).comando("x")
    assert vistos and "division" in vistos[0].lower()


def test_um_tratador_de_erro_que_falha_nao_entra_em_laco(Tg, app):
    def tambem_quebra(ctx, erro):
        raise RuntimeError("o tratador tambem")

    app.ao_falhar()(tambem_quebra)
    app.comando("x")(lambda ctx: 1 / 0)
    Tg["testar"](app).comando("x")      # não pode travar nem estourar
    assert app.metricas["erros"] == 1


# ═══════════════════════════════════════════════════════════
#  Estado e conversa
# ═══════════════════════════════════════════════════════════

def test_o_estado_e_por_chat(Tg, app):
    """Dois chats no mesmo dicionário é o defeito que todo bot tem: o
    segundo usuário vê o cadastro do primeiro."""
    app.qualquer()(lambda ctx: ctx.guardar("nome", ctx.texto))
    Tg["testar"](app, chat=1).mandar("Ana")
    Tg["testar"](app, chat=2).mandar("Bruno")
    assert app.estado_de(1)["nome"] == "Ana"
    assert app.estado_de(2)["nome"] == "Bruno"


def test_a_conversa_pergunta_valida_e_guarda(Tg, app):
    fim = []
    conversa = app.conversa("cadastro", [
        {"pergunta": "Nome?", "guarda": "nome"},
        {"pergunta": "E-mail?", "guarda": "email",
         "valida": lambda t: "@" in t, "erro": "E-mail inválido."}])
    conversa.ao_terminar()(lambda ctx, r: fim.append(r))
    app.comando("cadastro")(lambda ctx: conversa.comecar(ctx))

    t = Tg["testar"](app)
    t.comando("cadastro")
    assert t.ultima() == "Nome?"
    t.mandar("Ana")
    assert t.ultima() == "E-mail?"
    t.mandar("sem arroba")
    assert t.ultima() == "E-mail inválido.", "a validação não segurou"
    t.mandar("ana@x.com")
    assert fim == [{"nome": "Ana", "email": "ana@x.com"}]
    assert t.estado("__conversa__") is None, "a conversa não foi encerrada"


def test_um_comando_SEMPRE_escapa_da_conversa(Tg, app):
    """Sem isso, quem se perde no meio de um cadastro não consegue nem
    mandar /cancelar — e a única saída vira bloquear o bot."""
    conversa = app.conversa("x", [{"pergunta": "Nome?", "guarda": "nome"}])
    app.comando("cadastro")(lambda ctx: conversa.comecar(ctx))
    app.comando("cancelar")(lambda ctx: ctx.responder("cancelado"))

    t = Tg["testar"](app)
    t.comando("cadastro")
    t.comando("cancelar")
    assert t.ultima() == "cancelado"
    assert t.estado("__conversa__") is None


def test_uma_conversa_que_nao_existe_lista_as_que_existem(Tg, app):
    from dataforge.errors import RuntimeError_

    app.conversa("cadastro", [{"pergunta": "?", "guarda": "a"}])
    with pytest.raises(RuntimeError_) as erro:
        app.comecar_conversa(1, "inexistente")
    assert "cadastro" in str(erro.value.nota)


def test_o_estado_em_arquivo_sobrevive_ao_reinicio(Tg, tmp_path):
    armazem = Tg["estado_em_arquivo"](str(tmp_path / "estado"))
    armazem.gravar(99, {"passo": 2})
    outro = Tg["estado_em_arquivo"](str(tmp_path / "estado"))
    assert outro.ler(99) == {"passo": 2}


def test_o_id_do_chat_nao_escreve_fora_da_pasta(Tg, tmp_path):
    """O id vem do Telegram e é sempre numérico — mas 'sempre' é uma
    suposição sobre um sistema de terceiros, e é barato não depender."""
    armazem = Tg["estado_em_arquivo"](str(tmp_path / "estado"))
    armazem.gravar("../../fora", {"x": 1})
    assert not (tmp_path / "fora.json").exists()
    assert not (tmp_path.parent / "fora.json").exists()


# ═══════════════════════════════════════════════════════════
#  Contexto
# ═══════════════════════════════════════════════════════════

def test_o_contexto_sabe_quem_falou(Tg, app):
    vistos = {}

    def anotar(ctx):
        vistos.update({"nome": ctx.nome(), "id": ctx.id_do_usuario(),
                       "privado": ctx.e_privado()})

    app.qualquer()(anotar)
    Tg["testar"](app).mandar("oi")
    assert vistos == {"nome": "Ana", "id": 42, "privado": True}


def test_editar_fora_de_um_callback_diz_o_que_usar(Tg, app):
    from dataforge.errors import RuntimeError_

    erros = []
    app.qualquer()(lambda ctx: ctx.editar("x"))
    app.ao_falhar()(lambda ctx, e: erros.append(e))
    Tg["testar"](app).mandar("oi")
    assert erros and "responder" in str(getattr(erros[0], "dica", ""))


def test_o_update_cru_continua_acessivel(Tg, app):
    """Um bot de verdade sempre acaba precisando de um campo que
    nenhuma conveniência cobre."""
    vistos = []
    app.qualquer()(lambda ctx: vistos.append(ctx.update["update_id"]))
    Tg["testar"](app).mandar("oi")
    assert vistos == [1]


# ═══════════════════════════════════════════════════════════
#  Transporte
# ═══════════════════════════════════════════════════════════

def test_o_retry_after_zero_nao_cai_no_caminho_do_none(Tg):
    """`0` significa 'tente agora'. Com `or`, ele cairia em 'não pediu'
    — e o cliente desistiria de uma chamada que podia repetir."""
    from dataforge.stdlib.arcane_telegram import _quanto_esperar

    assert _quanto_esperar({"parameters": {"retry_after": 0}}) == 0.0
    assert _quanto_esperar({"parameters": {"retry_after": 3}}) == 3.0
    assert _quanto_esperar({}) is None


def test_o_corpo_vira_json_quando_nao_ha_arquivo(Tg):
    from dataforge.stdlib.arcane_telegram import _empacotar

    corpo, tipo = _empacotar({"chat_id": 1, "text": "oi"}, None)
    assert tipo == "application/json"
    assert json.loads(corpo.decode())["text"] == "oi"


def test_o_teclado_nao_e_serializado_duas_vezes(Tg):
    """Serializar duas vezes faz o Telegram receber uma STRING onde
    espera um markup, e o 400 fala de 'reply_markup' sem dizer que o
    problema é o formato."""
    from dataforge.stdlib.arcane_telegram import _empacotar

    teclado = {"inline_keyboard": [[{"text": "a", "callback_data": "b"}]]}
    corpo, _ = _empacotar({"chat_id": 1, "reply_markup": teclado}, None)
    lido = json.loads(corpo.decode())
    assert isinstance(lido["reply_markup"], dict)
    assert lido["reply_markup"]["inline_keyboard"][0][0]["text"] == "a"


def test_o_multipart_sai_com_fronteira_e_nome(Tg, tmp_path):
    from dataforge.stdlib.arcane_telegram import _empacotar

    alvo = tmp_path / "foto.png"
    alvo.write_bytes(b"\x89PNG\r\n")
    corpo, tipo = _empacotar({"chat_id": 1}, {"photo": str(alvo)})
    assert tipo.startswith("multipart/form-data; boundary=")
    assert b'filename="foto.png"' in corpo and b"\x89PNG" in corpo


def test_um_file_id_nao_sobe_de_novo(Tg):
    """Mandar tudo por multipart funcionaria e reenviaria um arquivo
    que o Telegram já tem."""
    from dataforge.stdlib.arcane_telegram import _e_referencia

    assert _e_referencia("AgACAgEAAxkBAAIBY2ZvdG8tbG9uZ2EtYXNzaW0")
    assert _e_referencia("https://exemplo.dev/a.png")
    assert not _e_referencia("./local/a.png")


def test_o_prazo_do_polling_e_maior_que_a_espera(Tg):
    """Iguais, o cliente desiste no instante em que o Telegram ia
    responder — e o sintoma é um bot que perde mensagens sob carga
    baixa, que é quando o polling chega ao fim do prazo."""
    import inspect

    from dataforge.stdlib.arcane_telegram import Bot

    fonte = inspect.getsource(Bot.updates)
    assert "float(espera) + " in fonte


def test_o_erro_do_telegram_vira_uma_mensagem_que_ensina(Tg):
    from dataforge.errors import RuntimeError_
    from dataforge.stdlib.arcane_telegram import _resultado

    with pytest.raises(RuntimeError_) as erro:
        _resultado({"ok": False, "error_code": 409,
                    "description": "Conflict: terminated by other getUpdates"},
                   "getUpdates", "1:AAH")
    assert "polling" in str(erro.value.nota).lower()
    assert "webhook" in str(erro.value.dica)


# ═══════════════════════════════════════════════════════════
#  Webhook
# ═══════════════════════════════════════════════════════════

def test_o_webhook_e_o_polling_passam_pelo_MESMO_caminho(Tg, app):
    """Um bot testado em polling que quebra ao virar webhook quebra
    exatamente quando vai para produção."""
    vistos = []
    app.qualquer()(lambda ctx: vistos.append(ctx.texto))
    kiln = get_module("Arcane.Kiln")
    montado = app.montar("/tg")

    update = {"update_id": 1, "message": {
        "message_id": 1, "from": {"id": 7, "first_name": "Ana"},
        "chat": {"id": 7, "type": "private"}, "text": "por webhook"}}
    resposta = kiln["test"](montado, "POST", "/tg", update)
    assert resposta["status"] == 200
    assert vistos == ["por webhook"]


def test_o_webhook_com_segredo_recusa_quem_nao_o_tem(Tg, app):
    """Sem ele, qualquer um que descubra a URL manda updates falsos —
    e a URL vaza em log de proxy, em print de tela, em qualquer lugar."""
    app.qualquer()(lambda ctx: None)
    kiln = get_module("Arcane.Kiln")
    montado = app.montar("/tg", segredo="abracadabra")

    sem = kiln["test"](montado, "POST", "/tg", {"update_id": 1})
    assert sem["status"] == 403

    com = kiln["test"](montado, "POST", "/tg", {"update_id": 1},
                       {"x-telegram-bot-api-secret-token": "abracadabra"})
    assert com["status"] == 200


def test_o_webhook_responde_200_mesmo_quando_o_tratador_falha(Tg, app):
    """O Telegram REENVIA quando a resposta falha. Responder 200 sempre
    é o que impede o mesmo comando de rodar três vezes."""
    app.qualquer()(lambda ctx: 1 / 0)
    kiln = get_module("Arcane.Kiln")
    montado = app.montar("/tg")
    resposta = kiln["test"](montado, "POST", "/tg", {
        "update_id": 1, "message": {"message_id": 1,
                                    "from": {"id": 1, "first_name": "A"},
                                    "chat": {"id": 1, "type": "private"},
                                    "text": "x"}})
    assert resposta["status"] == 200


def test_publicar_recusa_uma_url_sem_https(Tg, app):
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        app.publicar("http://sem-tls.dev", subir=False)
    assert "HTTPS" in str(erro.value.message)


# ═══════════════════════════════════════════════════════════
#  Operação
# ═══════════════════════════════════════════════════════════

def test_o_menu_de_comandos_sai_dos_registros(Tg, app):
    """Sem o menu, a lista de '/' vem vazia e o bot parece quebrado."""
    app.comando("start", ajuda="Começa")(lambda ctx: None)
    app.comando("ajuda")(lambda ctx: None)
    t = Tg["testar"](app)
    menu = app.publicar_comandos()
    assert menu == {"start": "Começa", "ajuda": "Ajuda"}
    assert t.quantas("setMyCommands") == 1


def test_as_ajudas_nao_vazam_entre_dois_bots(Tg):
    """Um dicionário de classe faria o segundo bot herdar os comandos
    do primeiro."""
    um = Tg["app"]("1:AAH")
    outro = Tg["app"]("2:AAH")
    um.comando("start", ajuda="do primeiro")(lambda ctx: None)
    assert outro.ajudas == {}


def test_a_saude_conta_o_que_aconteceu(Tg, app):
    app.qualquer()(lambda ctx: ctx.responder("ok"))
    t = Tg["testar"](app)
    t.mandar("a")
    t.mandar("b")
    saude = app.saude()
    assert saude["updates"] == 2 and saude["tratados"] == 2
    assert saude["ok"] is True


def test_o_limitador_segura_o_ritmo(Tg):
    import time

    limitador = Tg["limitar"](por_segundo=50.0, por_chat_por_minuto=0)
    comeco = time.monotonic()
    for _ in range(5):
        limitador.esperar(1)
    assert time.monotonic() - comeco >= 0.06, "não segurou nada"


# ═══════════════════════════════════════════════════════════
#  A sonda
# ═══════════════════════════════════════════════════════════

def test_a_sonda_nao_toca_a_rede(Tg, app):
    """Um bot que só pode ser testado conversando com ele no celular
    não tem teste nenhum."""
    app.qualquer()(lambda ctx: ctx.responder("oi"))
    t = Tg["testar"](app)
    t.mandar("x")
    assert t.disse("oi")
    assert all(c["metodo"] != "getUpdates" for c in t.chamadas())


def test_o_duble_aceita_metodo_que_ele_nao_conhece(Tg, app):
    """Um dublê que precisa acompanhar cada método novo do cliente
    envelhece no primeiro recurso acrescentado."""
    app.qualquer()(lambda ctx: ctx.bot.fixar(ctx.chat, 1))
    t = Tg["testar"](app)
    t.mandar("x")
    assert t.quantas("fixar") == 1
    assert not t.falhou()


def test_a_sonda_ve_o_teclado_que_foi_mandado(Tg, app):
    app.qualquer()(lambda ctx: ctx.responder(
        "escolha", teclado=Tg["botoes"]([[Tg["botao"]("A", dados="a")]])))
    t = Tg["testar"](app)
    t.mandar("x")
    assert t.ultimo_teclado()["inline_keyboard"][0][0]["text"] == "A"


# ═══════════════════════════════════════════════════════════
#  O CLI e o modelo
# ═══════════════════════════════════════════════════════════

def test_o_comando_telegram_esta_no_catalogo():
    """Um comando despachado e fora do catálogo não aparece em
    'dataforge help', nem em /api/comandos.json."""
    from dataforge.cli import GRUPOS

    nomes = {c.nome for grupo in GRUPOS for c in grupo[1]}
    assert "telegram" in nomes


def test_o_modelo_de_bot_existe_e_roda():
    from dataforge.modelos import MODELOS

    assert "bot" in MODELOS
    arquivos = MODELOS["bot"]["files"]
    assert any(a.startswith("src/") for a in arquivos)
    assert any(a.startswith("tests/") for a in arquivos)
    # O token NUNCA no código: é o erro que custa o bot inteiro. O que
    # se cobra é o CAMINHO — que o bot leia do ambiente — e não a
    # ausência da string ':AAH', que aparece de propósito no comentário
    # que ensina a exportar a variável.
    import re

    bot = arquivos["src/bot.df"]
    assert "segredo_do_ambiente()" in bot
    literais = re.findall(r'Tg\.app\(\s*"', bot)
    assert not literais, "o modelo passa um token literal para Tg.app"


def test_o_doctor_pergunta_pelas_causas_conhecidas():
    """As cinco causas de um bot calado, e nenhuma aparece no terminal
    sozinha."""
    import inspect

    from dataforge import telegram_cli

    fonte = inspect.getsource(telegram_cli._diagnosticar)
    for causa in ("can_read_all_group_messages", "info_do_webhook",
                  "can_join_groups", "pending_update_count"):
        assert causa in fonte, f"o doctor não pergunta por {causa}"


def test_o_decorador_conta_como_uso_do_nome(tmp_path):
    """`action registra(app)` com um `mark @app.rota(...)` dentro era
    acusado de não usar `app`.

    O nome de um decorador é **texto** na árvore (`'app.rota'`), e não
    um `Identifier` — então ele não era visto como leitura. É o padrão
    mais comum de quem registra rotas, e um falso alarme no caminho
    mais comum ensina a ignorar o lint inteiro.
    """
    from dataforge.lexer import tokenize
    from dataforge.linter import lint_program
    from dataforge.parser import parse

    fonte = ("action registra(app):\n"
             "    mark @app.rota(\"/x\")\n"
             "    action handler():\n"
             "        yield 1\n")
    programa = parse(tokenize(fonte, "x.df"), "x.df")
    avisos = [d for d in lint_program(programa, "x.df", fonte)
              if "never used" in d.message]
    assert not avisos, [a.message for a in avisos]


def test_o_exemplo_do_bot_roda():
    """O exemplo monta um bot inteiro e se confere com os próprios
    `assert` — sem token e sem rede."""
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alvo = os.path.join(raiz, "examples", "telegram_bot.df")
    if not os.path.isfile(alvo):
        pytest.skip("o exemplo não está neste checkout")
    saida = subprocess.run([sys.executable, "-m", "dataforge", "run", alvo],
                           capture_output=True, text=True, encoding="utf-8",
                           cwd=raiz)
    assert saida.returncode == 0, saida.stdout + saida.stderr
    assert "bot ok" in saida.stdout


# ═══════════════════════════════════════════════════════════
#  'ctx.estado' prometia sobreviver, e era uma cópia
# ═══════════════════════════════════════════════════════════

def test_escrever_em_ctx_estado_persiste():
    """`ctx.estado["k"] := v` escrevia num dicionário descartável.

    Sem erro, sem aviso, e com a documentação prometendo o contrário
    (*"o vault deste chat, que sobrevive entre mensagens"*). O sintoma
    era um carrinho que nunca enchia.

    A cópia não era descuido: `EmArquivo` **lê do disco**, e ali não há
    dicionário vivo para entregar. Por isso a vista, que lê e grava
    através do armazém e funciona igual nos dois.
    """
    Tg = get_module("Arcane.Telegram")
    app = Tg["app"]("123456:AAH")

    def somar(ctx):
        atual = ctx.estado.get("n", 0)
        ctx.estado["n"] = atual + 1

    app.comando("somar")(somar)
    sonda = Tg["testar"](app)
    sonda.comando("somar")
    sonda.comando("somar")
    sonda.comando("somar")
    assert sonda.estado("n") == 3


def test_a_vista_funciona_com_o_armazem_em_arquivo(tmp_path):
    """É o armazém que obrigava a cópia; a vista tem de valer nele."""
    Tg = get_module("Arcane.Telegram")
    app = Tg["app"]("123456:AAH",
                    estado=Tg["estado_em_arquivo"](str(tmp_path)))

    def guardar(ctx):
        itens = ctx.estado.get("itens", [])
        itens.append(ctx.texto)
        ctx.estado["itens"] = itens

    app.qualquer()(guardar)
    sonda = Tg["testar"](app)
    sonda.mandar("a")
    sonda.mandar("b")
    assert sonda.estado("itens") == ["a", "b"]


def test_a_vista_se_comporta_como_vault():
    Tg = get_module("Arcane.Telegram")
    app = Tg["app"]("123456:AAH")
    vistos = {}

    def mexer(ctx):
        ctx.estado["a"] = 1
        ctx.estado["b"] = 2
        vistos["len"] = len(ctx.estado)
        vistos["tem"] = "a" in ctx.estado
        vistos["nao_tem"] = "z" in ctx.estado
        vistos["chaves"] = sorted(ctx.estado.keys())
        vistos["foto"] = ctx.estado.para_vault()
        del ctx.estado["a"]
        vistos["depois"] = sorted(ctx.estado.keys())

    app.qualquer()(mexer)
    Tg["testar"](app).mandar("x")

    assert vistos["len"] == 2
    assert vistos["tem"] is True
    assert vistos["nao_tem"] is False
    assert vistos["chaves"] == ["a", "b"]
    assert vistos["foto"] == {"a": 1, "b": 2}
    assert vistos["depois"] == ["b"]


def test_a_foto_nao_acompanha():
    """`para_vault()` existe para quem quer a cópia, e ela é cópia."""
    Tg = get_module("Arcane.Telegram")
    app = Tg["app"]("123456:AAH")
    guardado = {}

    def mexer(ctx):
        ctx.estado["n"] = 1
        foto = ctx.estado.para_vault()
        ctx.estado["n"] = 2
        guardado["foto"] = foto["n"]
        guardado["vista"] = ctx.estado["n"]

    app.qualquer()(mexer)
    Tg["testar"](app).mandar("x")
    assert guardado == {"foto": 1, "vista": 2}


def test_o_duble_tem_a_MESMA_assinatura_do_bot_de_verdade():
    """Um dublê mais estreito que o original aprova o que quebra.

    `BotFalso.responder_inline` aceitava `**kw` — por **nome**, e não
    por **posição**. Uma chamada posicional funcionava em produção e
    estourava no teste, com uma mensagem sobre "argumentos demais" que
    não fala do que realmente diverge.
    """
    import inspect

    from dataforge.stdlib.arcane_telegram import Bot
    from dataforge.stdlib.arcane_telegram_app import BotFalso

    divergentes = []
    for nome, valor in sorted(vars(BotFalso).items()):
        if nome.startswith("_") or not callable(valor):
            continue
        real = getattr(Bot, nome, None)
        if real is None:
            continue
        do_duble = str(inspect.signature(valor))
        do_real = str(inspect.signature(real))
        if do_duble != do_real:
            divergentes.append(f"{nome}: dublê{do_duble} × real{do_real}")

    assert not divergentes, "\n".join(divergentes)


def test_responder_consulta_preenche_o_id_sozinho():
    """Era a única resposta que caía no bot cru.

    Todas as outras são `ctx.responder*`; esta obrigava a escrever
    `ctx.bot.responder_inline(ctx.consulta["id"], …)` — com o id à
    mão, que é exatamente o que se esquece.
    """
    Tg = get_module("Arcane.Telegram")
    app = Tg["app"]("123456:AAH")

    def buscar(ctx):
        ctx.responder_consulta([
            {"id": "1", "titulo": "Café", "texto": "R$ 6,50"},
            {"id": "2", "titulo": "Bolo", "texto": "R$ 8,00",
             "descricao": "de fubá"}])

    app.inline()(buscar)
    sonda = Tg["testar"](app)
    sonda.consultar("ca")

    assert sonda.quantas("answerInlineQuery") == 1
    itens = sonda.chamadas()[-1]["resultados"]
    assert [i["type"] for i in itens] == ["article", "article"]
    assert itens[0]["title"] == "Café"
    assert itens[0]["input_message_content"]["message_text"] == "R$ 6,50"
    assert itens[1]["description"] == "de fubá"


def test_responder_consulta_aceita_o_vault_completo():
    """Quem precisa de outro tipo de resultado passa o objeto pronto."""
    Tg = get_module("Arcane.Telegram")
    app = Tg["app"]("123456:AAH")

    def buscar(ctx):
        ctx.responder_consulta([
            {"type": "photo", "id": "9", "photo_url": "x", "thumbnail_url": "y"}])

    app.inline()(buscar)
    sonda = Tg["testar"](app)
    sonda.consultar("")
    assert sonda.chamadas()[-1]["resultados"][0]["type"] == "photo"


def test_responder_consulta_fora_de_uma_consulta_e_recusado():
    Tg = get_module("Arcane.Telegram")
    app = Tg["app"]("123456:AAH")
    visto = {}

    def qualquer(ctx):
        try:
            ctx.responder_consulta([])
        except Exception as erro:                            # noqa: BLE001
            visto["erro"] = str(erro)

    app.qualquer()(qualquer)
    Tg["testar"](app).mandar("x")
    assert "consulta inline" in visto["erro"]
