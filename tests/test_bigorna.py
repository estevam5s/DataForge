"""Arcane.Bigorna — o framework de aplicações de mesa.

A Sonda prova a aplicação sem display: telas, menus, atalhos, diálogos,
seleção, status, notificação e preferências. A janela de verdade é
montada e INSPECIONADA quando há display — o menu é acionado pelo
próprio Tk, e não por uma chamada que o contorna.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import arcane_bigorna as B  # noqa: E402
from dataforge.stdlib import get_module  # noqa: E402

MOD = get_module("Arcane.Bigorna")


def _app(tmp_path, **k):
    return B.app("Estoque", pasta_de_config=str(tmp_path / "config"), **k)


@pytest.fixture()
def estoque(tmp_path):
    produtos = [{"nome": "café", "qtd": 12}, {"nome": "açúcar", "qtd": 3}]
    a = _app(tmp_path)
    a.menu("Arquivo", [B.item("Novo produto", "novo", "Ctrl+N"),
                       B.separador(),
                       B.item("Exportar", "exportar", "Ctrl+E")])

    def inicio(t):
        t.titulo("Produtos")
        escolhido = t.tabela(["nome", "qtd"], produtos, selecionar=True)
        t.status(f"{len(produtos)} produtos")
        if t.comando("novo") or t.botao("Novo"):
            t.ir("produto")
        if escolhido is not None:
            t.texto(f"escolhido: {escolhido['nome']}")
            if t.botao("Excluir") and t.confirmar(f"Excluir {escolhido['nome']}?"):
                produtos.remove(escolhido)
                t.notificar("excluido")
                t.atualizar()
        if t.comando("exportar"):
            caminho = t.salvar_arquivo("estoque.csv", ["csv"])
            if caminho:
                t.guardar_pref("ultimo_export", caminho)
                t.notificar(f"exportado em {caminho}")

    def produto(t):
        t.titulo("Novo produto")
        nome = t.entrada("Nome")
        qtd = t.numero("Quantidade", 0)
        if t.botao("Salvar"):
            produtos.append({"nome": nome, "qtd": qtd})
            t.voltar()
        if t.botao("Cancelar"):
            t.voltar()

    a.tela("inicio", inicio)
    a.tela("produto", produto)
    return a, produtos


# ═══════════════════════════════════════════════════════════
#  Telas e navegação
# ═══════════════════════════════════════════════════════════

def test_a_primeira_tela_registrada_e_a_que_abre(estoque):
    s = B.testar(estoque[0])
    assert s.tela_atual() == "inicio"
    assert s.status() == "2 produtos"


def test_ir_e_voltar(estoque):
    a, produtos = estoque
    s = B.testar(a)
    s.clicar("Novo")
    assert s.tela_atual() == "produto"
    s.digitar("Nome", "sal")
    s.digitar("Quantidade", 7)
    s.clicar("Salvar")
    assert s.tela_atual() == "inicio"
    assert produtos[-1] == {"nome": "sal", "qtd": 7}
    assert s.status() == "3 produtos"


def test_uma_tela_nova_comeca_limpa(estoque):
    """Os campos da visita anterior não aparecem na próxima."""
    s = B.testar(estoque[0])
    s.clicar("Novo")
    s.digitar("Nome", "rascunho")
    s.clicar("Cancelar")
    s.clicar("Novo")
    assert s.valor("Nome") == ""


def test_ir_para_uma_tela_que_nao_existe_diz_quais_existem(tmp_path):
    a = _app(tmp_path)
    a.tela("inicio", lambda t: t.ir("perfil") if t.botao("Ir") else None)
    s = B.testar(a)
    with pytest.raises(Exception) as erro:
        s.clicar("Ir")
    assert "nao ha tela 'perfil'" in erro.value.message
    assert "inicio" in erro.value.nota


def test_navegacao_sem_condicao_e_recusada_em_vez_de_travar(tmp_path):
    a = _app(tmp_path)
    a.tela("a", lambda t: t.ir("b"))
    a.tela("b", lambda t: t.ir("a"))
    with pytest.raises(Exception, match="nao parou"):
        B.testar(a)


def test_parametros_da_navegacao(tmp_path):
    a = _app(tmp_path)

    def lista(t):
        if t.botao("Ver 3"):
            t.ir("detalhe", {"id": 3})

    def detalhe(t):
        t.texto(f"produto {t.parametro('id')}")

    a.tela("lista", lista)
    a.tela("detalhe", detalhe)
    s = B.testar(a)
    s.clicar("Ver 3")
    assert s.tem("produto 3")


def test_atualizar_redesenha_depois_da_mudanca(estoque):
    """Um clique vale para UMA execução: o status já tinha sido calculado
    antes de apagar. Sem 't.atualizar()' ele ficava em 2."""
    a, produtos = estoque
    s = B.testar(a)
    s.selecionar(0)
    s.responder(True)
    s.clicar("Excluir")
    assert len(produtos) == 1
    assert s.status() == "1 produtos"
    assert s.notificacoes()[-1] == "excluido"


# ═══════════════════════════════════════════════════════════
#  Menus e atalhos
# ═══════════════════════════════════════════════════════════

def test_menu_e_atalho_disparam_o_mesmo_comando(estoque):
    s = B.testar(estoque[0])
    s.menu("Arquivo", "Novo produto")
    assert s.tela_atual() == "produto"
    s.clicar("Cancelar")
    s.atalho("Ctrl+N")
    assert s.tela_atual() == "produto"


def test_cmd_e_ctrl_sao_o_mesmo_atalho(estoque):
    s = B.testar(estoque[0])
    s.atalho("cmd+n")
    assert s.tela_atual() == "produto"


@pytest.mark.parametrize("entrada,saida", [
    ("ctrl+n", "Ctrl+N"), ("Cmd+N", "Ctrl+N"), ("shift + ctrl + s", "Ctrl+Shift+S"),
    ("Alt+F4", "Alt+F4"), ("Ctrl-Q", "Ctrl+Q")])
def test_o_atalho_e_normalizado(entrada, saida):
    assert B._normalizar_atalho(entrada) == saida


def test_o_atalho_vira_o_do_sistema():
    assert B._atalho_tk("Ctrl+N", macos=True) == "<Command-n>"
    assert B._atalho_tk("Ctrl+N", macos=False) == "<Control-n>"
    assert B._atalho_tk("Ctrl+Shift+S", macos=False) == "<Control-Shift-S>"
    assert B._atalho_visivel("Ctrl+Shift+S", macos=True) == "⌘⇧S"
    assert B._atalho_visivel("Ctrl+Shift+S", macos=False) == "Ctrl+Shift+S"


def test_um_atalho_em_dois_itens_e_recusado(tmp_path):
    a = _app(tmp_path)
    a.menu("A", [B.item("Um", "um", "Ctrl+N"), B.item("Dois", "dois", "Ctrl+N")])
    with pytest.raises(Exception, match="esta em dois itens"):
        a.atalhos()


def test_menu_ou_item_que_nao_existe_lista_o_que_existe(estoque):
    s = B.testar(estoque[0])
    with pytest.raises(Exception) as erro:
        s.menu("Arquivo", "Imprimir")
    assert "Novo produto" in erro.value.nota
    with pytest.raises(Exception) as erro:
        s.atalho("Ctrl+P")
    assert "Ctrl+N" in erro.value.nota


def test_modificador_desconhecido_e_recusado():
    with pytest.raises(Exception, match="nao e um modificador"):
        B.item("X", "x", "Super+X")


# ═══════════════════════════════════════════════════════════
#  Diálogos: o teste responde, e o que ele não responde é falha
# ═══════════════════════════════════════════════════════════

def test_dialogo_sem_resposta_e_falha_e_nao_um_sim_inventado(estoque):
    s = B.testar(estoque[0])
    with pytest.raises(Exception) as erro:
        s.menu("Arquivo", "Exportar")
    assert "o teste nao respondeu" in erro.value.message
    assert "s.responder" in erro.value.dica


def test_dialogo_de_salvar_responde_o_caminho(estoque):
    a = estoque[0]
    s = B.testar(a)
    s.responder("/tmp/x.csv")
    s.menu("Arquivo", "Exportar")
    assert s.notificacoes()[-1] == "exportado em /tmp/x.csv"
    assert s.dialogos_pedidos()[-1] == {"dialogo": "salvar_arquivo", "texto": "estoque.csv"}


def test_cancelar_o_dialogo_nao_faz_nada(estoque):
    a = estoque[0]
    s = B.testar(a)
    s.responder(None)
    s.menu("Arquivo", "Exportar")
    assert s.notificacoes() == []


def test_confirmacao_negada_nao_apaga(estoque):
    a, produtos = estoque
    s = B.testar(a)
    s.selecionar(1)
    s.responder(False)
    s.clicar("Excluir")
    assert len(produtos) == 2


# ═══════════════════════════════════════════════════════════
#  Tabela com seleção
# ═══════════════════════════════════════════════════════════

def test_a_selecao_devolve_a_linha_original(estoque):
    s = B.testar(estoque[0])
    assert not s.tem("escolhido")
    s.selecionar(1)
    assert s.tem("escolhido: açúcar")


def test_selecao_alem_da_lista_volta_a_void(tmp_path):
    itens = [{"n": 1}, {"n": 2}]
    visto = {}
    a = _app(tmp_path)

    def tela(t):
        visto["linha"] = t.tabela(["n"], itens, selecionar=True)
    a.tela("t", tela)
    s = B.testar(a)
    s.selecionar(1)
    assert visto["linha"] == {"n": 2}
    itens.pop()
    s.rodar()
    assert visto["linha"] is None


# ═══════════════════════════════════════════════════════════
#  Preferências
# ═══════════════════════════════════════════════════════════

def test_a_preferencia_sobrevive_a_outra_execucao(estoque, tmp_path):
    a = estoque[0]
    s = B.testar(a)
    s.responder("/tmp/x.csv")
    s.menu("Arquivo", "Exportar")
    gravado = json.loads((tmp_path / "config" / "preferencias.json").read_text())
    assert gravado == {"ultimo_export": "/tmp/x.csv"}
    outra = _app(tmp_path)
    assert outra.preferencias.ler("ultimo_export") == "/tmp/x.csv"


def test_preferencia_corrompida_volta_aos_padroes(tmp_path):
    pasta = tmp_path / "config"
    pasta.mkdir()
    (pasta / "preferencias.json").write_text("{isto nao e json")
    a = _app(tmp_path)
    assert a.preferencias.ler("tema", "claro") == "claro"
    a.preferencias.gravar("tema", "escuro")
    assert json.loads((pasta / "preferencias.json").read_text()) == {"tema": "escuro"}


@pytest.mark.parametrize("plataforma,esperado", [
    ("darwin", os.path.join("Library", "Application Support", "Meu App")),
    ("linux", os.path.join(".config", "Meu App"))])
def test_a_pasta_de_config_e_a_de_cada_sistema(monkeypatch, plataforma, esperado):
    monkeypatch.setattr(B.sys, "platform", plataforma)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    assert B.pasta_de_config("Meu App").endswith(esperado)


def test_a_pasta_de_config_do_windows(monkeypatch):
    monkeypatch.setattr(B.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", os.path.join("C:", "Users", "ana", "AppData"))
    assert B.pasta_de_config("Meu/App").endswith(os.path.join("AppData", "MeuApp"))


# ═══════════════════════════════════════════════════════════
#  Recusas
# ═══════════════════════════════════════════════════════════

def test_tema_desconhecido_e_recusado(tmp_path):
    with pytest.raises(Exception) as erro:
        _app(tmp_path, tema="neon")
    assert "claro, escuro, sistema" in erro.value.nota


def test_app_sem_tela_e_recusado(tmp_path):
    with pytest.raises(Exception, match="nao tem tela nenhuma"):
        B.testar(_app(tmp_path))


def test_o_modulo_expoe_o_que_a_documentacao_usa():
    for nome in ("app", "item", "separador", "rodar", "testar",
                 "tem_display", "pasta_de_config", "temas"):
        assert nome in MOD, nome


# ═══════════════════════════════════════════════════════════
#  A janela de verdade
# ═══════════════════════════════════════════════════════════

@pytest.mark.skipif(not B.tem_display() or os.environ.get("CI") == "true",
                    reason="sem display — e é assim no CI")
def test_a_janela_de_verdade_tem_menu_status_e_navega(estoque):
    """Montada pelo Tk, e o menu acionado pelo PRÓPRIO Tk (`invoke`)."""
    a = estoque[0]
    j = B._construir(a)
    raiz = j["raiz"]
    try:
        raiz.update()
        assert j["status"].cget("text") == "2 produtos"
        barra = j["barra"]
        assert barra.entrycget(0, "label") == "Arquivo"
        sub = raiz.nametowidget(barra.entrycget(0, "menu"))
        assert sub.entrycget(0, "label") == "Novo produto"
        grades = [w for w in j["quadro"]["corpo"].winfo_children()
                  if w.winfo_class() == "Treeview"]
        assert len(grades[0].get_children()) == 2
        sub.invoke(0)
        raiz.update()
        assert a.tela_atual() == "produto"
    finally:
        raiz.destroy()


# ═══════════════════════════════════════════════════════════
#  Pela linguagem
# ═══════════════════════════════════════════════════════════

def test_pela_linguagem(tmp_path):
    from tests._df import rodar

    r = rodar(tmp_path, f'''adopt Arcane.Bigorna as B

itens := ["café"]
app := B.app("Lista", pasta_de_config := "{tmp_path / 'cfg'}")
app.menu("Arquivo", [B.item("Novo", "novo", atalho := "Ctrl+N")])

action inicio(t):
    t.titulo("Itens")
    t.lista(itens)
    t.status($"{{len(itens)}} itens")
    given t.comando("novo"):
        t.ir("novo")

action novo(t):
    nome := t.entrada("Nome")
    given t.botao("Salvar"):
        itens.append(nome)
        t.voltar()

app.tela("inicio", inicio)
app.tela("novo", novo)

s := B.testar(app)
s.atalho("Cmd+N")
s.digitar("Nome", "sal")
s.clicar("Salvar")
assert s.tela_atual() is "inicio"
assert s.status() is "2 itens"
out "ok"
''')
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ok" in r.stdout
