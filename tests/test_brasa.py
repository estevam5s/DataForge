"""Arcane.Brasa — o framework de aplicativos para o celular.

A Sonda prova as telas sem navegador: tocar numa linha, numa aba e no
botão flutuante, voltar, e a localização que o navegador responderia.
O PWA é conferido SERVINDO: o manifesto, os ícones e o service worker
são pedidos por HTTP, e o que chegou é o que se confere.
"""

import json
import struct
import sys
import urllib.request

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import arcane_brasa as Br  # noqa: E402
from dataforge.stdlib import get_module  # noqa: E402

V = get_module("Arcane.Vitrine")


@pytest.fixture()
def estoque():
    produtos = [{"id": 1, "nome": "café", "qtd": 12},
                {"id": 2, "nome": "açúcar", "qtd": 3}]
    app = Br.app("Estoque", cor="#E8453C", descricao="o estoque no bolso")

    def inicio():
        Br.topo("Produtos")
        if produtos:
            Br.lista(produtos, titulo="nome", detalhe="qtd",
                     destino="/produto?id={id}")
        else:
            Br.vazio("Nenhum produto", "toque em + para cadastrar")
        Br.botao_flutuante("Novo", "/novo")

    def produto():
        pid = int(V["parametro"]("id", "0"))
        p = next((x for x in produtos if x["id"] == pid), None)
        Br.topo(p["nome"] if p else "Produto", voltar=True)
        if p:
            V["metrica"]("Quantidade", p["qtd"])

    def novo():
        Br.topo("Novo produto", voltar=True)
        nome = V["entrada"]("Nome")
        if V["botao"]("Salvar"):
            produtos.append({"id": len(produtos) + 1, "nome": nome, "qtd": 0})
            V["navegar"]("/")

    def perfil():
        Br.topo("Perfil")
        onde = Br.localizacao()
        if onde:
            V["texto"](f"em {onde['lat']}, {onde['lon']}")

    Br.tela("/", inicio, titulo="Estoque", icone="carrinho", aba=True, aplicacao=app)
    Br.tela("/perfil", perfil, titulo="Perfil", icone="usuario", aba=True, aplicacao=app)
    Br.tela("/produto", produto, titulo="Produto", aplicacao=app)
    Br.tela("/novo", novo, titulo="Novo", aplicacao=app)
    return app, produtos


# ═══════════════════════════════════════════════════════════
#  Telas, toque e navegação
# ═══════════════════════════════════════════════════════════

def test_a_lista_e_as_abas_sao_dado_para_a_sonda(estoque):
    s = Br.testar(estoque[0])
    assert s.titulo() == "Produtos"
    assert s.itens() == [{"titulo": "café", "detalhe": "12"},
                         {"titulo": "açúcar", "detalhe": "3"}]
    assert s.abas() == [{"titulo": "Estoque", "ativa": True},
                        {"titulo": "Perfil", "ativa": False}]


def test_tocar_na_linha_leva_ao_detalhe_com_o_parametro(estoque):
    s = Br.testar(estoque[0])
    s.tocar("açúcar")
    assert s.caminho() == "/produto?id=2"
    assert s.titulo() == "açúcar"
    assert s.tem("3")


def test_voltar_volta_para_onde_estava(estoque):
    s = Br.testar(estoque[0])
    s.tocar("café")
    s.voltar()
    assert s.titulo() == "Produtos"


def test_na_tela_de_detalhe_nenhuma_aba_fica_acesa(estoque):
    s = Br.testar(estoque[0])
    s.tocar("café")
    assert [a["ativa"] for a in s.abas()] == [False, False]


def test_botao_flutuante_e_formulario(estoque):
    app, produtos = estoque
    s = Br.testar(app)
    s.tocar("Novo")
    s.digitar("Nome", "sal")
    s.clicar("Salvar")
    s.ir("/")
    assert produtos[-1]["nome"] == "sal"
    assert len(s.itens()) == 3


def test_a_lista_vazia_explica(estoque):
    app, produtos = estoque
    produtos.clear()
    s = Br.testar(app)
    assert s.tem("Nenhum produto")


def test_tocar_no_que_nao_existe_lista_o_que_existe(estoque):
    s = Br.testar(estoque[0])
    with pytest.raises(Exception) as erro:
        s.tocar("sal")
    assert "café" in erro.value.nota and "Perfil" in erro.value.nota


def test_a_localizacao_volta_e_fica_na_sessao(estoque):
    s = Br.testar(estoque[0])
    s.tocar("Perfil")
    assert not s.tem("em -23")
    s.localizacao(-23.55, -46.63)
    assert s.tem("em -23.55, -46.63")
    s.tocar("Estoque")
    s.tocar("Perfil")
    assert s.tem("em -23.55, -46.63"), "a posição fica na sessão"


# ═══════════════════════════════════════════════════════════
#  Segurança: o dado não vira HTML nem link perigoso
# ═══════════════════════════════════════════════════════════

def test_o_texto_da_lista_e_escapado():
    app = Br.app("X")
    Br.tela("/", lambda: Br.lista([{"nome": "<script>alert(1)</script>"}]),
            aplicacao=app)
    html = Br.testar(app).html()
    assert "<script>alert(1)" not in html
    assert "&lt;script&gt;" in html


def test_o_valor_no_destino_e_codificado():
    app = Br.app("X")
    Br.tela("/", lambda: Br.lista([{"nome": "a", "id": "1&apagar=sim"}],
                                  destino="/p?id={id}"), aplicacao=app)
    s = Br.testar(app)
    assert s._desenhado("item")[0]["destino"] == "/p?id=1%26apagar%3Dsim"


@pytest.mark.parametrize("destino", ["javascript:alert(1)", "//outro.site/x", "data:text/html,oi"])
def test_destino_perigoso_e_recusado(destino):
    with pytest.raises(Exception, match="destino recusado"):
        Br._destino_seguro(destino)


@pytest.mark.parametrize("destino", ["/produto?id=3", "tel:+5511999", "https://maps.google.com"])
def test_destino_legitimo_passa(destino):
    assert Br._destino_seguro(destino) == destino


# ═══════════════════════════════════════════════════════════
#  Recusas
# ═══════════════════════════════════════════════════════════

def test_icone_desconhecido_e_acusado_no_registro_com_sugestao():
    app = Br.app("X")
    with pytest.raises(Exception) as erro:
        Br.tela("/", lambda: None, aba=True, icone="caixa", aplicacao=app)
    assert "casa" in erro.value.nota


def test_emoji_serve_de_icone():
    app = Br.app("X")
    Br.tela("/", lambda: None, aba=True, icone="📦", aplicacao=app)


def test_mais_de_cinco_abas_e_recusado():
    app = Br.app("X")
    for i in range(5):
        Br.tela(f"/t{i}", lambda: None, aba=True, aplicacao=app)
    with pytest.raises(Exception, match="ja tem 5"):
        Br.tela("/t5", lambda: None, aba=True, aplicacao=app)


def test_cor_invalida_e_recusada():
    with pytest.raises(Exception, match="cor invalida"):
        Br.app("X", cor="vermelho")


# ═══════════════════════════════════════════════════════════
#  O PWA — conferido servindo
# ═══════════════════════════════════════════════════════════

def test_o_pwa_passa_em_tudo_que_o_android_exige(estoque):
    achados = Br.conferir_pwa(estoque[0])
    reprovados = [a for a in achados if not a["ok"]]
    assert reprovados == [], reprovados
    assert len(achados) >= 15


def test_o_manifesto_tem_o_icone_maskable_separado(estoque):
    m = Br.manifesto(estoque[0])
    propositos = {(i["sizes"], i["purpose"]) for i in m["icons"]}
    assert ("512x512", "maskable") in propositos
    assert ("192x192", "any") in propositos
    assert m["display"] == "standalone" and m["theme_color"] == "#E8453C"


def test_o_service_worker_leva_a_versao_e_nao_repete_post():
    app = Br.app("X", versao="7")
    sw = Br.service_worker(app)
    assert '"brasa-7"' in sw
    assert "method !== 'GET'" in sw


@pytest.mark.parametrize("tamanho", [192, 512])
def test_o_icone_e_um_png_valido_do_tamanho_pedido(tamanho):
    import zlib
    png = Br.icone_png("Estoque", "#E8453C", tamanho)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    largura, altura = struct.unpack(">II", png[16:24])
    assert (largura, altura) == (tamanho, tamanho)
    # O IDAT descomprime no tamanho exato de uma imagem RGBA com filtro.
    inicio = png.index(b"IDAT") + 4
    comprimento = struct.unpack(">I", png[inicio - 8:inicio - 4])[0]
    cru = zlib.decompress(png[inicio:inicio + comprimento])
    assert len(cru) == tamanho * (1 + 4 * tamanho)


def test_as_iniciais_do_icone():
    assert Br._iniciais("Estoque da Loja") == "ED"
    assert Br._iniciais("Área") == "A"
    assert Br._iniciais("") == "A"


def test_o_servidor_entrega_os_tipos_certos(estoque):
    app = estoque[0]
    porta = Br.servir(app)
    try:
        base = f"http://127.0.0.1:{porta}"
        with urllib.request.urlopen(base + "/sw.js") as r:
            assert "javascript" in r.headers["Content-Type"]
        with urllib.request.urlopen(base + "/manifest.webmanifest") as r:
            assert "manifest+json" in r.headers["Content-Type"]
            assert json.loads(r.read())["name"] == "Estoque"
        with urllib.request.urlopen(base + "/") as r:
            pagina = r.read().decode()
            assert 'rel="manifest"' in pagina and "viewport-fit=cover" in pagina
            assert "br-abas" in pagina
    finally:
        app.parar()


def test_o_modulo_expoe_o_que_a_documentacao_usa():
    M = get_module("Arcane.Brasa")
    for nome in ("app", "tela", "rodar", "testar", "conferir_pwa", "topo",
                 "lista", "vazio", "botao_flutuante", "compartilhar",
                 "ligar", "mapa", "localizacao", "secao"):
        assert nome in M, nome


# ═══════════════════════════════════════════════════════════
#  Pela linguagem
# ═══════════════════════════════════════════════════════════

def test_pela_linguagem(tmp_path):
    from tests._df import rodar

    r = rodar(tmp_path, '''adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V

tarefas := [{"id": 1, "titulo": "comprar café"}]
app := Br.app("Tarefas", cor := "#2F6FED")

action lista():
    Br.topo("Tarefas")
    Br.lista(tarefas, titulo := "titulo", destino := "/tarefa?id={id}")

action tarefa():
    Br.topo("Tarefa", voltar := yes)
    V.texto($"tarefa {V.parametro("id")}")

Br.tela("/", lista, titulo := "Tarefas", icone := "conferir", aba := yes)
Br.tela("/tarefa", tarefa)

s := Br.testar(app)
s.tocar("comprar café")
assert s.tem("tarefa 1")
s.voltar()
assert s.titulo() is "Tarefas"
falhas := [c cycle c in Br.conferir_pwa(app) given not c["ok"]]
assert len(falhas) is 0
out "ok"
''')
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ok" in r.stdout
