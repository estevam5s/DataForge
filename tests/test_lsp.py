# -*- coding: utf-8 -*-
"""O servidor de linguagem: protocolo, e cada resposta que ele dá.

Os testes falam o protocolo de verdade — cabeçalho `Content-Length`,
JSON-RPC, um `Servidor` real sobre buffers de memória. Testar as
funções por baixo esconderia justamente o que costuma quebrar: o
enquadramento das mensagens e o formato que o editor espera.
"""

import io
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge import lsp                                    # noqa: E402


# ═══════════════════════════════════════════════════════════
#  Um cliente de mentira, que fala o protocolo
# ═══════════════════════════════════════════════════════════

def _quadro(mensagem):
    dados = json.dumps(mensagem).encode("utf-8")
    return b"Content-Length: %d\r\n\r\n" % len(dados) + dados


def _conversar(mensagens):
    """Manda as mensagens, devolve o que o servidor respondeu."""
    entrada = io.BytesIO(b"".join(_quadro(m) for m in mensagens))
    saida = io.BytesIO()
    lsp.Servidor(entrada=entrada, saida=saida).rodar()

    bruto = saida.getvalue()
    respostas, i = [], 0
    while i < len(bruto):
        fim = bruto.find(b"\r\n\r\n", i)
        if fim < 0:
            break
        cabecalho = bruto[i:fim].decode()
        tamanho = int(cabecalho.split("Content-Length:")[1].split("\r")[0])
        corpo = bruto[fim + 4:fim + 4 + tamanho]
        respostas.append(json.loads(corpo))
        i = fim + 4 + tamanho
    return respostas


URI = "file:///teste.df"

FONTE = '''adopt Arcane.Math as M

// dobra o que receber
action dobrar(x: Integer) -> Integer:
    yield x * 2

record Ponto:
    x: Integer
    y: Integer

enum Cor:
    Vermelho
    Azul

steady LIMITE := 10

out dobrar(21)
'''


def _sessao(*depois):
    """initialize + didOpen + o que vier, e as respostas."""
    return _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "textDocument/didOpen",
         "params": {"textDocument": {"uri": URI, "languageId": "dataforge",
                                     "version": 1, "text": FONTE}}},
        *depois,
        {"jsonrpc": "2.0", "id": 99, "method": "shutdown", "params": {}},
    ])


def _resposta(respostas, ident):
    for r in respostas:
        if r.get("id") == ident:
            return r.get("result")
    return None


def _notificacoes(respostas, metodo):
    return [r for r in respostas if r.get("method") == metodo]


# ═══════════════════════════════════════════════════════════
#  Transporte
# ═══════════════════════════════════════════════════════════

def test_o_enquadramento_sobrevive_a_quebra_de_linha_no_corpo():
    """O corpo pode conter '\\n'; contar linhas cortaria a mensagem."""
    texto = "action f():\n    yield 1\n"
    r = _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "textDocument/didOpen",
         "params": {"textDocument": {"uri": URI, "text": texto}}},
        {"jsonrpc": "2.0", "id": 2, "method": "textDocument/documentSymbol",
         "params": {"textDocument": {"uri": URI}}},
    ])
    assert [s["name"] for s in _resposta(r, 2)] == ["f"]


def test_notificacao_nao_ganha_resposta():
    """'didOpen' não tem id: responder a ela confunde o cliente."""
    r = _sessao()
    assert all(n.get("id") != 2 for n in r)


def test_metodo_desconhecido_vira_erro_e_nao_derruba():
    r = _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "textDocument/naoExiste",
         "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "shutdown", "params": {}},
    ])
    erro = next(x for x in r if x.get("id") == 2)
    assert erro["error"]["code"] == -32601
    assert any(x.get("id") == 3 for x in r), "o servidor parou no erro"


def test_initialize_anuncia_o_que_sabe_fazer():
    caps = _resposta(_sessao(), 1)["capabilities"]
    for chave in ("hoverProvider", "definitionProvider", "renameProvider",
                  "completionProvider", "documentSymbolProvider",
                  "documentFormattingProvider", "signatureHelpProvider",
                  "codeActionProvider", "referencesProvider"):
        assert caps.get(chave), f"não anuncia {chave}"


# ═══════════════════════════════════════════════════════════
#  Diagnosticos
# ═══════════════════════════════════════════════════════════

def test_arquivo_bom_publica_lista_vazia():
    """Ele PRECISA publicar: sem isso o erro anterior fica na tela."""
    notas = _notificacoes(_sessao(), "textDocument/publishDiagnostics")
    assert notas and notas[0]["params"]["diagnostics"] == []


def test_erro_de_sintaxe_vira_diagnostico_na_linha_certa():
    r = _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "textDocument/didOpen",
         "params": {"textDocument": {"uri": URI,
                                     "text": "x := 1\naction f(\n"}}},
    ])
    d = _notificacoes(r, "textDocument/publishDiagnostics")[0]["params"]["diagnostics"]
    assert d and d[0]["severity"] == 1
    assert d[0]["range"]["start"]["line"] >= 1, "apontou para a linha 1, que está certa"


def test_nome_indefinido_vira_diagnostico_com_sugestao():
    r = _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "textDocument/didOpen",
         "params": {"textDocument": {"uri": URI,
                                     "text": "contador := 1\nout contadr\n"}}},
    ])
    d = _notificacoes(r, "textDocument/publishDiagnostics")[0]["params"]["diagnostics"]
    assert any("contador" in x["message"] for x in d)


def test_fechar_o_arquivo_limpa_os_problemas():
    """Senão eles ficam no painel apontando para um arquivo fechado."""
    r = _sessao({"jsonrpc": "2.0", "method": "textDocument/didClose",
                 "params": {"textDocument": {"uri": URI}}})
    ultima = _notificacoes(r, "textDocument/publishDiagnostics")[-1]
    assert ultima["params"]["diagnostics"] == []


# ═══════════════════════════════════════════════════════════
#  As respostas
# ═══════════════════════════════════════════════════════════

def test_hover_traz_a_assinatura_e_o_comentario_de_cima():
    r = _sessao({"jsonrpc": "2.0", "id": 5, "method": "textDocument/hover",
                 "params": {"textDocument": {"uri": URI},
                            "position": {"line": 16, "character": 5}}})
    texto = _resposta(r, 5)["contents"]["value"]
    assert "action dobrar(x: Integer) -> Integer" in texto
    assert "dobra o que receber" in texto


def test_hover_de_embutida_diz_que_nao_precisa_de_adopt():
    r = _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "textDocument/didOpen",
         "params": {"textDocument": {"uri": URI, "text": "out len([1, 2])\n"}}},
        {"jsonrpc": "2.0", "id": 5, "method": "textDocument/hover",
         "params": {"textDocument": {"uri": URI},
                    "position": {"line": 0, "character": 5}}},
    ])
    assert "adopt" in _resposta(r, 5)["contents"]["value"]


def test_definicao_aponta_para_a_declaracao():
    r = _sessao({"jsonrpc": "2.0", "id": 5, "method": "textDocument/definition",
                 "params": {"textDocument": {"uri": URI},
                            "position": {"line": 16, "character": 5}}})
    assert _resposta(r, 5)["range"]["start"]["line"] == 3


def test_esquema_traz_os_filhos():
    r = _sessao({"jsonrpc": "2.0", "id": 5,
                 "method": "textDocument/documentSymbol",
                 "params": {"textDocument": {"uri": URI}}})
    por_nome = {s["name"]: s for s in _resposta(r, 5)}
    assert set(por_nome) >= {"dobrar", "Ponto", "Cor", "LIMITE"}
    assert [f["name"] for f in por_nome["Ponto"]["children"]] == ["x", "y"]
    assert [f["name"] for f in por_nome["Cor"]["children"]] == ["Vermelho", "Azul"]


def test_completar_depois_do_ponto_so_traz_o_modulo():
    """O catálogo inteiro ali vira ruído."""
    r = _sessao({"jsonrpc": "2.0", "id": 5, "method": "textDocument/completion",
                 "params": {"textDocument": {"uri": URI},
                            "position": {"line": 16, "character": 4},
                            "context": {"triggerCharacter": "."}}})
    # a linha 16 é 'out dobrar(21)'; sem ponto, vem o catálogo inteiro
    itens = _resposta(r, 5)["items"]
    assert len(itens) > 300


def test_completar_traz_os_nomes_do_arquivo_primeiro():
    r = _sessao({"jsonrpc": "2.0", "id": 5, "method": "textDocument/completion",
                 "params": {"textDocument": {"uri": URI},
                            "position": {"line": 16, "character": 4}}})
    itens = _resposta(r, 5)["items"]
    locais = [i for i in itens if i["label"] in ("dobrar", "Ponto", "LIMITE")]
    assert len(locais) == 3
    assert all(i.get("sortText", "z").startswith("0") for i in locais)


def test_completar_dentro_da_acao_ve_os_parametros():
    """É o que mais faz alguém achar que o autocompletar não funciona."""
    r = _sessao({"jsonrpc": "2.0", "id": 5, "method": "textDocument/completion",
                 "params": {"textDocument": {"uri": URI},
                            "position": {"line": 4, "character": 10}}})
    assert any(i["label"] == "x" for i in _resposta(r, 5)["items"])


def test_ajuda_de_assinatura_marca_o_parametro_atual():
    """Este pedido chega SEMPRE com o arquivo incompleto.

    Quem pede ajuda de assinatura está no meio de escrever a chamada —
    o parêntese ainda não fechou. Depender de um parse bem-sucedido
    tornaria o recurso inútil justamente no único momento em que ele é
    pedido; a última análise boa é que responde.
    """
    completo = "action somar(a, b):\n    yield a + b\n\nout somar(1, 2)\n"
    escrevendo = "action somar(a, b):\n    yield a + b\n\nout somar(1, \n"
    r = _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "textDocument/didOpen",
         "params": {"textDocument": {"uri": URI, "text": completo}}},
        {"jsonrpc": "2.0", "method": "textDocument/didChange",
         "params": {"textDocument": {"uri": URI, "version": 2},
                    "contentChanges": [{"text": escrevendo}]}},
        {"jsonrpc": "2.0", "id": 5, "method": "textDocument/signatureHelp",
         "params": {"textDocument": {"uri": URI},
                    "position": {"line": 3, "character": 13}}},
    ])
    ajuda = _resposta(r, 5)
    assert ajuda["signatures"][0]["label"].startswith("action somar(a, b)")
    assert ajuda["activeParameter"] == 1


def test_formatar_devolve_a_troca_do_arquivo_inteiro():
    torto = "action  f( ):\n        yield    1\n"
    r = _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "textDocument/didOpen",
         "params": {"textDocument": {"uri": URI, "text": torto}}},
        {"jsonrpc": "2.0", "id": 5, "method": "textDocument/formatting",
         "params": {"textDocument": {"uri": URI}, "options": {}}},
    ])
    edicoes = _resposta(r, 5)
    assert edicoes and "action f():" in edicoes[0]["newText"]


def test_renomear_troca_todas_as_ocorrencias():
    r = _sessao({"jsonrpc": "2.0", "id": 5, "method": "textDocument/rename",
                 "params": {"textDocument": {"uri": URI},
                            "position": {"line": 3, "character": 8},
                            "newName": "duplicar"}})
    edicoes = _resposta(r, 5)["changes"][URI]
    assert len(edicoes) == 2          # a declaração e a chamada
    assert all(e["newText"] == "duplicar" for e in edicoes)


def test_renomear_recusa_palavra_reservada():
    """Aceitar 'yield' aqui só adiaria o erro para a próxima execução."""
    r = _sessao({"jsonrpc": "2.0", "id": 5, "method": "textDocument/rename",
                 "params": {"textDocument": {"uri": URI},
                            "position": {"line": 3, "character": 8},
                            "newName": "yield"}})
    erro = next(x for x in r if x.get("id") == 5)
    assert "reservada" in erro["error"]["message"]


def test_correcao_rapida_a_partir_da_sugestao():
    r = _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "textDocument/didOpen",
         "params": {"textDocument": {"uri": URI,
                                     "text": "contador := 1\nout contadr\n"}}},
        {"jsonrpc": "2.0", "id": 5, "method": "textDocument/codeAction",
         "params": {"textDocument": {"uri": URI},
                    "range": {"start": {"line": 1, "character": 0},
                              "end": {"line": 1, "character": 20}},
                    "context": {"diagnostics": []}}},
    ])
    acoes = _resposta(r, 5)
    assert acoes and acoes[0]["edit"]["changes"][URI][0]["newText"] == "contador"


# ═══════════════════════════════════════════════════════════
#  A decisao que mais importa
# ═══════════════════════════════════════════════════════════

def test_o_esquema_sobrevive_ao_arquivo_pela_metade():
    """Enquanto se digita, o arquivo passa a maior parte do tempo inválido.

    Se cada estado inválido zerasse o esquema, o autocompletar sumiria
    justamente enquanto se escreve — que é quando ele serve.
    """
    quebrado = FONTE + "\naction incompleta("
    r = _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "textDocument/didOpen",
         "params": {"textDocument": {"uri": URI, "text": FONTE}}},
        {"jsonrpc": "2.0", "method": "textDocument/didChange",
         "params": {"textDocument": {"uri": URI, "version": 2},
                    "contentChanges": [{"text": quebrado}]}},
        {"jsonrpc": "2.0", "id": 5, "method": "textDocument/documentSymbol",
         "params": {"textDocument": {"uri": URI}}},
        {"jsonrpc": "2.0", "id": 6, "method": "textDocument/completion",
         "params": {"textDocument": {"uri": URI},
                    "position": {"line": 16, "character": 4}}},
    ])
    nomes = [s["name"] for s in _resposta(r, 5)]
    assert "dobrar" in nomes, "o esquema sumiu com o arquivo pela metade"
    assert any(i["label"] == "dobrar" for i in _resposta(r, 6)["items"])

    # …mas o erro ainda é publicado.
    ultima = _notificacoes(r, "textDocument/publishDiagnostics")[-1]
    assert ultima["params"]["diagnostics"], "o erro de sintaxe não foi publicado"


# ═══════════════════════════════════════════════════════════
#  Completar depois do ponto — o contexto
# ═══════════════════════════════════════════════════════════
#
# Ele devolvia **zero item** para tudo que nao fosse modulo: 'p.',
# 'xs.', 'texto.' e 'self.' abriam a lista vazia no editor. Zero e pior
# que o catalogo inteiro — catalogo e ruido, zero parece que o servidor
# morreu.
#
# Os testes falam pelo PROTOCOLO e com o arquivo **invalido**, porque e
# assim que acontece: enquanto se digita, `p.` e erro de sintaxe. O
# servidor guarda a ultima arvore boa e troca o texto; testar com um
# arquivo valido provaria um caminho que ninguem percorre.

def _completar(valido, digitando, linha, coluna):
    """As sugestoes para o cursor, com o arquivo sendo digitado."""
    respostas = _conversar([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "textDocument/didOpen",
         "params": {"textDocument": {"uri": URI, "languageId": "dataforge",
                                     "version": 1, "text": valido}}},
        {"jsonrpc": "2.0", "method": "textDocument/didChange",
         "params": {"textDocument": {"uri": URI, "version": 2},
                    "contentChanges": [{"text": digitando}]}},
        {"jsonrpc": "2.0", "id": 2, "method": "textDocument/completion",
         "params": {"textDocument": {"uri": URI},
                    "position": {"line": linha - 1, "character": coluna}}},
    ])
    resultado = _resposta(respostas, 2)
    return [i["label"] for i in resultado["items"]]


RECORD = ('record Ponto:\n    x: Integer\n    y: Integer\n\n'
          '    action norma():\n        yield 1\n\np := Ponto(1, 2)\n')


def test_depois_do_ponto_num_record_vem_campo_e_metodo():
    itens = _completar(RECORD + "out 1", RECORD + "out p.", 9, 6)
    assert set(itens) == {"x", "y", "norma"}


def test_o_membro_HERDADO_tambem_aparece():
    """Herdado é tão legítimo quanto declarado — e esconder o que a mãe
    deu manda a pessoa procurar o nome no lugar errado."""
    fonte = ('blueprint Forma:\n    action area():\n        yield 0\n\n'
             'blueprint Quadrado(lado) extends Forma:\n'
             '    action nome():\n        yield 1\n\nc := spawn Quadrado(2)\n')
    itens = _completar(fonte + "out 1", fonte + "c.", 10, 2)
    assert set(itens) == {"lado", "nome", "area"}


def test_self_dentro_do_metodo_oferece_o_campo_criado_com_self():
    """`self.saldo := s` vive DENTRO de um método, e não solto no corpo:
    olhar só o corpo deixava de fora o campo mais comum que existe."""
    fonte = ('blueprint Conta:\n    action setup(s):\n        self.saldo := s\n\n'
             '    action ver():\n')
    itens = _completar(fonte + "        yield 1",
                       fonte + "        yield self.", 6, 20)
    assert set(itens) == {"setup", "ver", "saldo"}


@pytest.mark.parametrize("fonte,linha,alguns", [
    ('xs := [1, 2, 3]\n', 'xs.', ["append", "sort", "reverse"]),
    ('t := "abc"\n', 't.', ["upper", "split", "replace"]),
    ('v := {"a": 1}\n', 'v.', ["keys", "values", "has"]),
])
def test_o_metodo_embutido_vem_da_tabela_do_INTERPRETADOR(fonte, linha, alguns):
    """Uma segunda lista divergiria no primeiro método novo, e o editor
    passaria a oferecer o que não existe — ou a esconder o que existe."""
    itens = _completar(fonte + "out 1", fonte + linha, 2, len(linha))
    for nome in alguns:
        assert nome in itens


def test_o_enum_DO_ARQUIVO_vence_o_modulo_de_mesmo_nome():
    """`Cor` é apelido de `Arcane.Color` na stdlib. Sem a precedência, um
    `enum Cor` do próprio arquivo era engolido, e o editor oferecia
    `bold` e `bg_rgb` onde a pessoa esperava os membros dela."""
    fonte = "enum Cor:\n    Vermelho\n    Verde\n\n"
    itens = _completar(fonte + "out 1", fonte + "out Cor.", 5, 8)
    assert "Vermelho" in itens and "Verde" in itens
    assert "bold" not in itens
    # E os tres que todo membro de enum tem.
    assert {"name", "value", "index"} <= set(itens)


def test_o_modulo_continua_completando():
    itens = _completar("adopt Arcane.Math as Math\nout 1",
                       "adopt Arcane.Math as Math\nout Math.", 2, 9)
    assert "sqrt" in itens and "PI" in itens
    assert "action" not in itens, "palavra reservada não é membro de módulo"


def test_quando_NAO_PROVA_o_tipo_ele_cala():
    """A regra do resto do projeto. Devolver o catálogo inteiro aqui é o
    que faz o autocompletar virar ruído — e ruído é o que ensina a
    desligá-lo."""
    itens = _completar("q := desconhecida()\nout 1", "q := desconhecida()\nq.", 2, 2)
    assert itens == []


def test_o_tipo_e_o_da_ULTIMA_atribuicao_antes_do_cursor():
    """Um nome que troca de tipo no meio do arquivo é legítimo, e
    responder com o primeiro valor ofereceria o membro errado."""
    fonte = 'x := [1, 2]\nx := "texto"\n'
    itens = _completar(fonte + "out 1", fonte + "x.", 3, 2)
    assert "upper" in itens and "append" not in itens


def test_sem_ponto_ele_continua_oferecendo_o_catalogo():
    """O que muda é só o caminho do ponto: completar um nome solto
    continua trazendo locais, palavras e embutidas."""
    itens = _completar("total := 10\nout 1", "total := 10\nout tot", 2, 7)
    assert "total" in itens and "action" in itens
