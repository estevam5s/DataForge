"""Kiln — upload, streaming e WebSocket.

As três coisas que o framework não tinha, e que separam um servidor de
demonstração de um que atende um sistema.

**Upload.** O corpo era interpretado como JSON ou formulário simples; um
`<input type="file">` chegava como texto ilegível. Isso deixava de fora
toda tela que recebe planilha, foto ou documento.

**SSE.** Uma resposta que não termina: são trinta linhas de protocolo e
resolvem o "tempo real" que quase todo painel precisa.

**WebSocket.** O `http.server` não tem suporte, mas tem o que basta: o
handshake é HTTP com `Upgrade`, e depois dele o socket é nosso.

Os testes de WebSocket falam o protocolo à mão, de propósito: um cliente
pronto esconderia exatamente os erros de enquadramento que se quer
pegar — o quadro que atravessa pacotes, o tamanho de 16 bits, a máscara.
"""

import base64
import hashlib
import json
import os
import socket
import struct
import sys
import urllib.error
import urllib.request

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import get_module
from dataforge.stdlib.kiln_tempo_real import (Sala, chave_de_resposta,
                                              evento, interpretar_multipart,
                                              salvar_upload)


@pytest.fixture
def K():
    return get_module("Kiln")


# ═══════════════════════════════════════════════════════════
#  Upload — o formato
# ═══════════════════════════════════════════════════════════

def _corpo_multipart(partes, fronteira="----df"):
    montado = []
    for nome, valor, arquivo, tipo in partes:
        cabeca = f'Content-Disposition: form-data; name="{nome}"'
        if arquivo is not None:
            cabeca += f'; filename="{arquivo}"'
        extra = f"\r\nContent-Type: {tipo}" if tipo else ""
        montado.append(f"--{fronteira}\r\n{cabeca}{extra}\r\n\r\n{valor}\r\n")
    montado.append(f"--{fronteira}--\r\n")
    return ("".join(montado).encode(),
            f"multipart/form-data; boundary={fronteira}")


def test_campo_e_arquivo_saem_separados():
    corpo, tipo = _corpo_multipart([
        ("titulo", "Meu título", None, None),
        ("foto", "conteúdo do arquivo", "gato.txt", "text/plain"),
    ])
    partes = interpretar_multipart(corpo, tipo)
    assert partes["campos"] == {"titulo": "Meu título"}
    arquivo = partes["arquivos"]["foto"]
    assert arquivo["nome"] == "gato.txt"
    assert arquivo["tipo"] == "text/plain"
    assert arquivo["texto"] == "conteúdo do arquivo"
    assert isinstance(arquivo["conteudo"], bytes)


def test_campo_repetido_vira_cluster():
    """É assim que um `<select multiple>` e uma lista de caixas chegam —
    e o último valor sozinho perderia os outros."""
    corpo, tipo = _corpo_multipart([
        ("tags", "a", None, None),
        ("tags", "b", None, None),
        ("tags", "c", None, None),
    ])
    assert interpretar_multipart(corpo, tipo)["campos"]["tags"] == \
        ["a", "b", "c"]


def test_campo_de_arquivo_vazio_nao_conta_como_arquivo():
    """`filename=""` é o que o navegador manda quando ninguém escolheu
    nada: não é um arquivo de nome vazio."""
    corpo, tipo = _corpo_multipart([("foto", "", "", "application/octet-stream")])
    assert interpretar_multipart(corpo, tipo)["arquivos"] == {}


def test_o_caminho_do_cliente_e_descartado():
    """O IE mandava `C:\\Users\\x\\foto.jpg`; um navegador hostil manda o
    que quiser."""
    corpo, tipo = _corpo_multipart([
        ("f", "x", "C:\\Users\\ana\\foto.jpg", None)])
    assert interpretar_multipart(corpo, tipo)["arquivos"]["f"]["nome"] == \
        "foto.jpg"


def test_bytes_binarios_sobrevivem():
    """Uma imagem tem `\\r\\n` no meio, e um split ingênuo a parte."""
    fronteira = b"----df"
    dados = bytes(range(256)) * 4
    corpo = (b"--" + fronteira + b"\r\n"
             b'Content-Disposition: form-data; name="img"; filename="a.bin"'
             b"\r\nContent-Type: application/octet-stream\r\n\r\n"
             + dados + b"\r\n--" + fronteira + b"--\r\n")
    partes = interpretar_multipart(
        corpo, "multipart/form-data; boundary=----df")
    assert partes["arquivos"]["img"]["conteudo"] == dados


def test_um_corpo_que_nao_e_multipart_devolve_none():
    assert interpretar_multipart(b"{}", "application/json") is None


# ═══════════════════════════════════════════════════════════
#  Upload — gravar
# ═══════════════════════════════════════════════════════════

def _arquivo(nome="foto.jpg", conteudo=b"dados"):
    return {"nome": nome, "tipo": "", "tamanho": len(conteudo),
            "conteudo": conteudo, "texto": ""}


def test_salvar_gera_nome_proprio(tmp_path):
    """Dois usuários enviando "foto.jpg" não podem sobrescrever um ao
    outro, e um nome escolhido por quem envia é um nome que ele pode
    adivinhar depois."""
    a = salvar_upload(_arquivo(), str(tmp_path))
    b = salvar_upload(_arquivo(), str(tmp_path))
    assert a["nome"] != b["nome"]
    assert a["nome"].endswith(".jpg")
    assert a["nome_original"] == "foto.jpg"
    assert os.path.isfile(a["caminho"])


@pytest.mark.parametrize("veneno", [
    "../../.ssh/authorized_keys",
    "..",
    "/etc/passwd",
    "",
])
def test_nome_que_escapa_da_pasta_e_recusado(tmp_path, veneno):
    with pytest.raises(Exception):
        salvar_upload(_arquivo(veneno), str(tmp_path))


def test_acima_do_limite_e_recusado(tmp_path):
    with pytest.raises(Exception) as erro:
        salvar_upload(_arquivo(conteudo=b"x" * 100), str(tmp_path),
                      limite=50)
    assert "acima do limite" in str(erro.value)


def test_extensao_fora_da_lista_e_recusada(tmp_path):
    """`.php` numa pasta servida como estática é execução remota."""
    with pytest.raises(Exception) as erro:
        salvar_upload(_arquivo("shell.php"), str(tmp_path),
                      tipos=[".jpg", ".png"])
    assert "extensao" in str(erro.value)
    # E a aceita passa.
    assert salvar_upload(_arquivo("ok.jpg"), str(tmp_path),
                         tipos=["jpg", ".png"])["nome"].endswith(".jpg")


# ═══════════════════════════════════════════════════════════
#  SSE — o formato
# ═══════════════════════════════════════════════════════════

def test_um_evento_termina_com_linha_vazia():
    """Sem o `\\n\\n`, o cliente espera para sempre."""
    assert evento("oi").endswith("\n\n")


def test_um_texto_com_quebra_leva_um_data_por_linha():
    """Um `\\n` dentro do dado quebraria o evento no meio."""
    saida = evento("uma\nduas")
    assert saida.count("data: ") == 2
    assert "data: uma" in saida and "data: duas" in saida


def test_um_vault_vira_json():
    saida = evento({"a": 1})
    assert 'data: {"a": 1}' in saida


def test_tipo_id_e_retry_saem_antes_do_dado():
    saida = evento("x", tipo="fila", identificador="7", reconectar=3000)
    linhas = saida.strip().split("\n")
    assert linhas[0] == "id: 7"
    assert linhas[1] == "event: fila"
    assert linhas[2] == "retry: 3000"
    assert linhas[3] == "data: x"


# ═══════════════════════════════════════════════════════════
#  A sala
# ═══════════════════════════════════════════════════════════

class _Falso:
    def __init__(self, vivo=True):
        self.aberto = vivo
        self.recebeu = []

    def enviar(self, msg):
        if not self.aberto:
            return False
        self.recebeu.append(msg)
        return True

    def fechar(self, codigo=1000, motivo=""):
        self.aberto = False
        return True


def test_a_sala_transmite_a_todos_menos_a_um():
    sala = Sala("chat")
    a, b, c = _Falso(), _Falso(), _Falso()
    for s in (a, b, c):
        sala.entrar(s)
    assert sala.transmitir("oi", exceto=a) == 2
    assert a.recebeu == []
    assert b.recebeu == ["oi"] and c.recebeu == ["oi"]


def test_um_soquete_morto_e_removido_e_nao_derruba_os_outros():
    """Um cliente que fechou a aba não pode derrubar a mensagem dos
    outros."""
    sala = Sala()
    vivo, morto = _Falso(), _Falso(vivo=False)
    sala.entrar(vivo)
    sala.entrar(morto)
    assert sala.transmitir("oi") == 1
    assert sala.quantos() == 1


def test_a_sala_e_segura_entre_threads():
    import threading

    sala = Sala()
    membros = [_Falso() for _ in range(50)]

    def entrar_e_sair(s):
        for _ in range(20):
            sala.entrar(s)
            sala.transmitir("x")
            sala.sair(s)

    linhas = [threading.Thread(target=entrar_e_sair, args=(m,))
              for m in membros]
    for t in linhas:
        t.start()
    for t in linhas:
        t.join()
    assert sala.quantos() == 0


# ═══════════════════════════════════════════════════════════
#  WebSocket — o handshake
# ═══════════════════════════════════════════════════════════

def test_a_chave_de_resposta_segue_o_rfc():
    """O exemplo do RFC 6455, §1.3."""
    assert chave_de_resposta("dGhlIHNhbXBsZSBub25jZQ==") == \
        "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="


# ═══════════════════════════════════════════════════════════
#  Ponta a ponta, com socket
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def servidor(K):
    app = K["forge"]("tr")
    sala = K["sala"]("chat")

    def fila(fluxo):
        for i in range(3):
            if not fluxo.enviar({"n": i}, tipo="tick"):
                return
        fluxo.enviar("fim", tipo="fim")

    def csv(fluxo):
        fluxo.escrever("id,valor\n")
        for i in range(3):
            fluxo.escrever(f"{i},{i * 10}\n")

    def receber(req):
        arquivo = K["upload"](req, "foto")
        if arquivo is None:
            return {"erro": "sem arquivo"}
        return {"nome": arquivo["nome"], "tamanho": arquivo["tamanho"],
                "titulo": req["body"].get("titulo", "")}

    def eco(req, ws):
        sala.entrar(ws)
        ws.enviar({"id": ws.id, "na_sala": sala.quantos()})
        while ws.aberto:
            msg = ws.receber(prazo=5)
            if msg is None or msg == "sair":
                break
            ws.enviar(f"eco: {msg}")
            sala.transmitir({"de": ws.id, "texto": msg}, exceto=ws)
        sala.sair(ws)

    K["get"](app, "/eventos", lambda req: K["sse"](fila))
    K["get"](app, "/export.csv", lambda req: K["stream"](csv, "text/csv"))
    K["post"](app, "/enviar", receber)
    K["ws"](app, "/ws", eco)
    K["get"](app, "/ws", lambda req: {"pagina": "abre a conexao"})

    porta = K["serve"](app, 0)
    yield porta
    K["stop"](app)


def test_o_sse_chega_evento_por_evento(servidor):
    resposta = urllib.request.urlopen(f"http://127.0.0.1:{servidor}/eventos")
    assert resposta.headers.get("Content-Type").startswith("text/event-stream")
    assert resposta.headers.get("X-Accel-Buffering") == "no"
    corpo = resposta.read().decode()
    assert corpo.count("event: tick") == 3
    assert "event: fim" in corpo
    assert 'data: {"n": 0}' in corpo


def test_o_stream_manda_pedacos_crus(servidor):
    resposta = urllib.request.urlopen(f"http://127.0.0.1:{servidor}/export.csv")
    assert resposta.headers.get("Content-Type") == "text/csv"
    assert resposta.read().decode() == "id,valor\n0,0\n1,10\n2,20\n"


def test_o_upload_chega_pela_rota(servidor):
    corpo, tipo = _corpo_multipart([
        ("titulo", "Relatório", None, None),
        ("foto", "conteudo", "a.txt", "text/plain"),
    ])
    pedido = urllib.request.Request(
        f"http://127.0.0.1:{servidor}/enviar", data=corpo,
        headers={"Content-Type": tipo})
    dado = json.loads(urllib.request.urlopen(pedido).read())
    assert dado == {"nome": "a.txt", "tamanho": 8, "titulo": "Relatório"}


def _abrir_ws(porta, caminho="/ws"):
    conexao = socket.create_connection(("127.0.0.1", porta), timeout=5)
    chave = base64.b64encode(os.urandom(16)).decode()
    conexao.sendall(
        f"GET {caminho} HTTP/1.1\r\nHost: localhost\r\n"
        f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {chave}\r\nSec-WebSocket-Version: 13\r\n"
        f"\r\n".encode())
    cabeca = b""
    while b"\r\n\r\n" not in cabeca:
        pedaco = conexao.recv(1)
        if not pedaco:
            break
        cabeca += pedaco
    return conexao, cabeca, chave


def _mandar(conexao, texto):
    """Um quadro de texto mascarado — o cliente SEMPRE mascara."""
    dados = texto.encode()
    mascara = os.urandom(4)
    corpo = bytes(b ^ mascara[i % 4] for i, b in enumerate(dados))
    n = len(dados)
    if n < 126:
        cabeca = bytes([0x81, 0x80 | n])
    elif n < 65536:
        cabeca = bytes([0x81, 0x80 | 126]) + struct.pack("!H", n)
    else:
        cabeca = bytes([0x81, 0x80 | 127]) + struct.pack("!Q", n)
    conexao.sendall(cabeca + mascara + corpo)


def _ler(conexao):
    cabeca = conexao.recv(2)
    if len(cabeca) < 2:
        return None, b""
    n = cabeca[1] & 0x7F
    if n == 126:
        n = struct.unpack("!H", conexao.recv(2))[0]
    elif n == 127:
        n = struct.unpack("!Q", conexao.recv(8))[0]
    dados = b""
    while len(dados) < n:
        pedaco = conexao.recv(n - len(dados))
        if not pedaco:
            break
        dados += pedaco
    return cabeca[0] & 0x0F, dados


def test_o_handshake_segue_o_protocolo(servidor):
    conexao, cabeca, chave = _abrir_ws(servidor)
    try:
        assert b"101" in cabeca, cabeca
        assert b"Upgrade: websocket" in cabeca
        assert chave_de_resposta(chave).encode() in cabeca
    finally:
        conexao.close()


def test_o_eco_e_a_transmissao(servidor):
    a, _, _ = _abrir_ws(servidor)
    b, _, _ = _abrir_ws(servidor)
    try:
        primeiro = json.loads(_ler(a)[1])
        assert primeiro["na_sala"] == 1
        assert json.loads(_ler(b)[1])["na_sala"] == 2

        _mandar(a, "olá mundo")
        assert _ler(a)[1].decode() == "eco: olá mundo"
        # E o outro recebeu a transmissão.
        assert json.loads(_ler(b)[1])["texto"] == "olá mundo"
    finally:
        a.close()
        b.close()


@pytest.mark.parametrize("tamanho", [100, 300, 70000])
def test_mensagem_de_qualquer_tamanho(servidor, tamanho):
    """Os três caminhos do enquadramento: 7 bits, 16 bits e 64 bits."""
    conexao, _, _ = _abrir_ws(servidor)
    try:
        _ler(conexao)          # a saudação
        texto = "x" * tamanho
        _mandar(conexao, texto)
        assert _ler(conexao)[1].decode() == "eco: " + texto
    finally:
        conexao.close()


def test_um_get_comum_no_mesmo_caminho_continua_servindo(servidor):
    """A rota de WebSocket usa o método `WS`, que não existe em HTTP:
    assim o `GET /ws` continua livre para servir a página que abre a
    conexão."""
    dado = json.loads(urllib.request.urlopen(
        f"http://127.0.0.1:{servidor}/ws").read())
    assert dado == {"pagina": "abre a conexao"}


def test_upgrade_num_caminho_sem_websocket_da_404(servidor):
    conexao, cabeca, _ = _abrir_ws(servidor, "/nao-existe")
    try:
        assert b"404" in cabeca, cabeca
    finally:
        conexao.close()
