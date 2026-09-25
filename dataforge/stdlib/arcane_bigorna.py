# -*- coding: utf-8 -*-
"""Arcane.Bigorna — o framework de aplicações de mesa.

`Arcane.Janela` desenha UMA janela: uma tela, os campos e os botões dela.
Uma aplicação de mesa de verdade precisa do que vem em volta, e é isso
que a Bigorna acrescenta — sem trocar a forma, e sem dependência nova:

    | Peça                 | O que resolve                                   |
    |----------------------|-------------------------------------------------|
    | várias telas         | `t.ir("produto", {"id": 3})`, `t.voltar()`      |
    | barra de menus       | `app.menu("Arquivo", [B.item(...)])`            |
    | atalhos de teclado   | `Ctrl+N` vira Cmd+N no macOS, sozinho           |
    | diálogos nativos     | confirmar, abrir arquivo, salvar, escolher pasta|
    | barra de status      | `t.status("3 produtos")`                        |
    | notificação          | `t.notificar("salvo")`, some sozinha            |
    | tabela com seleção   | `linha := t.tabela(..., selecionar := yes)`     |
    | preferências         | gravadas na pasta certa de CADA sistema         |
    | tema                 | claro, escuro ou o do sistema                   |

A forma continua a da Janela e da Vitrine: **o programa da tela roda de
novo a cada interação**, e o estado sobrevive. Um clique, um item de
menu e um atalho são EVENTOS — valem para uma execução só, e por isso
não salvam o formulário duas vezes.

E continua testável sem display. A Sonda clica em menu, dispara atalho e
responde diálogo — mas só o que o teste ROTEIRIZOU: uma tela que pede
confirmação sem que o teste tenha dito a resposta falha, em vez de
receber um "sim" inventado. Um diálogo que o teste não viu é
exatamente o que quebra em produção.

O que ela NÃO é
---------------
Não há arrastar-e-soltar, animação, ícone na bandeja do sistema nem
janela transparente: o Tk não os tem de forma portável, e prometer um
recurso que funciona num sistema só é pior que não prometer. Para
painel de dados, a Vitrine (no navegador); para o celular, a Brasa.
"""

import json
import os
import sys

from ..errors import RuntimeError_
from . import arcane_janela as _J

_DOC = "desktop"


def _erro(mensagem, nota="", dica=""):
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


class _Ir(BaseException):
    """`t.ir(...)` e `t.voltar()` — acabam a tela aqui e trocam de tela.

    Deriva de `BaseException`, como o `V.navegar` da Vitrine: é sinal de
    controle, e não erro. O interpretador embrulha toda `Exception` que
    sai de uma função Python num erro da linguagem — e a navegação
    viraria uma mensagem no meio da tela.
    """

    def __init__(self, destino, parametros=None, voltar=False, atualizar=False):
        super().__init__(destino)
        self.destino = destino
        self.parametros = dict(parametros or {})
        self.voltar = voltar
        self.atualizar = atualizar


# ═══════════════════════════════════════════════════════════
#  Menus e atalhos
# ═══════════════════════════════════════════════════════════

def item(rotulo, comando, atalho=""):
    """Um item de menu: o rótulo, o comando que ele dispara e o atalho."""
    if not str(comando):
        raise _erro(f"o item '{rotulo}' nao tem comando",
                    dica='B.item("Novo", "novo", atalho := "Ctrl+N")')
    return {"rotulo": str(rotulo), "comando": str(comando),
            "atalho": _normalizar_atalho(atalho) if atalho else ""}


def separador():
    return {"separador": True}


_TECLAS = {"ctrl": "Ctrl", "control": "Ctrl", "cmd": "Ctrl", "command": "Ctrl",
           "shift": "Shift", "alt": "Alt", "option": "Alt"}


def _normalizar_atalho(texto):
    """'ctrl+n', 'Cmd+N', 'Ctrl + Shift + s' -> 'Ctrl+N', 'Ctrl+Shift+S'.

    `Cmd` e `Ctrl` são o MESMO atalho escrito para sistemas diferentes: o
    programa diz `Ctrl+N` uma vez, e no macOS ele vira Cmd+N sozinho. Um
    atalho que só existe num sistema obriga quem escreve a ramificar.
    """
    partes = [p.strip() for p in str(texto).replace("-", "+").split("+") if p.strip()]
    if not partes:
        raise _erro(f"atalho vazio: '{texto}'", dica='atalho := "Ctrl+N"')
    *mods, tecla = partes
    nomes = []
    for m in mods:
        nome = _TECLAS.get(m.lower())
        if nome is None:
            raise _erro(f"'{m}' nao e um modificador de atalho",
                        nota="os modificadores sao: Ctrl (Cmd no macOS), Shift e Alt")
        if nome not in nomes:
            nomes.append(nome)
    ordem = ["Ctrl", "Shift", "Alt"]
    nomes.sort(key=ordem.index)
    return "+".join(nomes + [tecla.upper() if len(tecla) == 1 else tecla.capitalize()])


def _atalho_tk(atalho, macos=None):
    """'Ctrl+Shift+S' -> '<Control-Shift-S>' (ou '<Command-Shift-S>')."""
    macos = sys.platform == "darwin" if macos is None else macos
    *mods, tecla = atalho.split("+")
    tk_mods = []
    for m in mods:
        tk_mods.append({"Ctrl": "Command" if macos else "Control",
                        "Shift": "Shift", "Alt": "Option" if macos else "Alt"}[m])
    # Com Shift o Tk entrega a letra MAIÚSCULA; sem, a minúscula.
    letra = tecla if "Shift" in mods else tecla.lower()
    return "<" + "-".join(tk_mods + [letra]) + ">"


def _atalho_visivel(atalho, macos=None):
    """O que o menu mostra: '⌘N' no macOS, 'Ctrl+N' nos outros."""
    macos = sys.platform == "darwin" if macos is None else macos
    if not macos:
        return atalho
    simbolos = {"Ctrl": "⌘", "Shift": "⇧", "Alt": "⌥"}
    *mods, tecla = atalho.split("+")
    return "".join(simbolos[m] for m in mods) + tecla


# ═══════════════════════════════════════════════════════════
#  Preferências — a pasta certa de cada sistema
# ═══════════════════════════════════════════════════════════

def pasta_de_config(nome):
    """Onde uma aplicação guarda o que é dela, em cada sistema.

    macOS: ~/Library/Application Support/<nome>
    Windows: %APPDATA%\\<nome>
    Linux: $XDG_CONFIG_HOME/<nome>, ou ~/.config/<nome>

    Gravar ao lado do executável é o erro clássico: num .app assinado e
    em "Arquivos de Programas" a pasta é só de leitura, e a preferência
    some sem erro nenhum.
    """
    seguro = "".join(c for c in str(nome) if c.isalnum() or c in " -_.").strip() or "app"
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    elif sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, seguro)


class Preferencias:
    """Um vault gravado em disco — lido uma vez, gravado a cada mudança."""

    def __init__(self, pasta):
        self.pasta = pasta
        self.caminho = os.path.join(pasta, "preferencias.json") if pasta else ""
        self._dados = None

    def _carregar(self):
        if self._dados is None:
            self._dados = {}
            if self.caminho and os.path.isfile(self.caminho):
                try:
                    with open(self.caminho, encoding="utf-8") as f:
                        lido = json.load(f)
                    if isinstance(lido, dict):
                        self._dados = lido
                except (OSError, ValueError):
                    # Um arquivo corrompido não impede a aplicação de abrir:
                    # ela volta aos padrões, e a próxima gravação o refaz.
                    self._dados = {}
        return self._dados

    def ler(self, chave, padrao=None):
        return self._carregar().get(str(chave), padrao)

    def gravar(self, chave, valor):
        dados = self._carregar()
        dados[str(chave)] = valor
        if self.caminho:
            os.makedirs(self.pasta, exist_ok=True)
            temporario = self.caminho + ".tmp"
            with open(temporario, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            # Escreve ao lado e troca: um processo interrompido no meio
            # não deixa um JSON pela metade.
            os.replace(temporario, self.caminho)
        return valor

    def tudo(self):
        return dict(self._carregar())


# ═══════════════════════════════════════════════════════════
#  A aplicação
# ═══════════════════════════════════════════════════════════

TEMAS = ("claro", "escuro", "sistema")


class AppBigorna:
    """O que a aplicação é: telas, menus, tamanho, tema e preferências."""

    def __init__(self, nome="DataForge", largura=900, altura=600,
                 tema="sistema", pasta_de_config=None):
        if str(tema) not in TEMAS:
            raise _erro(f"'{tema}' nao e um tema",
                        nota=f"os temas sao: {', '.join(TEMAS)}")
        self.nome = str(nome)
        self.largura = int(largura)
        self.altura = int(altura)
        self.tema = str(tema)
        self.telas = {}
        self.menus = []
        self.pilha = []
        self.parametros = {}
        self.estados = {}
        self.status_texto = ""
        self.notificacoes = []
        pasta = globals()["pasta_de_config"](self.nome) \
            if pasta_de_config is None else str(pasta_de_config)
        self.preferencias = Preferencias(pasta)

    # ── montar ──────────────────────────────────────────────

    def tela(self, nome, acao):
        """Registra uma tela. A primeira registrada é a que abre."""
        if not callable(acao):
            raise _erro(f"a tela '{nome}' precisa de uma acao",
                        dica='app.tela("inicio", inicio)   // action inicio(t): …')
        self.telas[str(nome)] = acao
        if not self.pilha:
            self.pilha.append(str(nome))
        return self

    def menu(self, titulo, itens):
        itens = list(itens or [])
        for i in itens:
            if not isinstance(i, dict) or not (i.get("separador") or i.get("comando")):
                raise _erro(f"o menu '{titulo}' tem um item que nao e B.item",
                            dica='[B.item("Novo", "novo"), B.separador()]')
        self.menus.append({"titulo": str(titulo), "itens": itens})
        return self

    # ── perguntar ───────────────────────────────────────────

    def tela_atual(self):
        return self.pilha[-1] if self.pilha else ""

    def atalhos(self):
        """atalho -> comando, de todos os menus. Um atalho repetido é erro."""
        vistos = {}
        for m in self.menus:
            for i in m["itens"]:
                a = i.get("atalho")
                if not a:
                    continue
                if a in vistos and vistos[a] != i["comando"]:
                    raise _erro(f"o atalho {a} esta em dois itens: "
                                f"'{vistos[a]}' e '{i['comando']}'",
                                nota="so um deles rodaria, e qual depende da ordem")
                vistos[a] = i["comando"]
        return vistos

    def _estado_de(self, nome):
        return self.estados.setdefault(nome, {})

    def __repr__(self):                                  # pragma: no cover
        return f"<app {self.nome!r}: {len(self.telas)} tela(s)>"


def app(nome="DataForge", largura=900, altura=600, tema="sistema",
        pasta_de_config=None):
    return AppBigorna(nome, largura, altura, tema, pasta_de_config)


# ═══════════════════════════════════════════════════════════
#  A tela — a da Janela, e o que uma aplicação acrescenta
# ═══════════════════════════════════════════════════════════

class TelaBigorna(_J.Tela):
    """Tudo da `Tela` da Janela, mais navegação, comandos e diálogos."""

    def __init__(self, aplicacao, nome, eventos, dialogos):
        super().__init__(aplicacao._estado_de(nome), eventos, aplicacao.nome)
        self._app = aplicacao
        self._nome = nome
        self._dialogos = dialogos

    # ── eventos que não são botão ───────────────────────────

    def comando(self, nome):
        """`yes` na execução em que o item de menu (ou o atalho) foi usado."""
        return bool(self._eventos.get(f"cmd:{nome}"))

    # ── navegação ───────────────────────────────────────────

    def ir(self, tela, parametros=None):
        if str(tela) not in self._app.telas:
            existem = ", ".join(self._app.telas) or "nenhuma"
            raise _erro(f"nao ha tela '{tela}'",
                        nota=f"as telas sao: {existem}",
                        dica=f'app.tela("{tela}", acao) registra')
        raise _Ir(str(tela), parametros)

    def voltar(self):
        raise _Ir("", voltar=True)

    def atualizar(self):
        """Roda esta tela de novo, sem o evento e sem apagar os campos.

        Um clique vale para UMA execução: o que a tela mostrou ANTES da
        mudança (a contagem, o status) já foi calculado. Depois de apagar
        um item, `t.atualizar()` faz a tela se desenhar com o que ficou.
        """
        raise _Ir(self._nome, atualizar=True)

    def parametro(self, nome, padrao=None):
        return self._app.parametros.get(self._nome, {}).get(str(nome), padrao)

    def tela_atual(self):
        return self._nome

    # ── a moldura ───────────────────────────────────────────

    def status(self, texto):
        self._app.status_texto = str(texto)
        return texto

    def notificar(self, texto):
        self._app.notificacoes.append(str(texto))
        return texto

    # ── diálogos ────────────────────────────────────────────

    def confirmar(self, pergunta):
        return bool(self._dialogos.pedir("confirmar", str(pergunta)))

    def abrir_arquivo(self, titulo="Abrir", tipos=None):
        return self._dialogos.pedir("abrir_arquivo", str(titulo), list(tipos or []))

    def salvar_arquivo(self, nome_sugerido="", tipos=None):
        return self._dialogos.pedir("salvar_arquivo", str(nome_sugerido),
                                    list(tipos or []))

    def escolher_pasta(self, titulo="Escolher pasta"):
        return self._dialogos.pedir("escolher_pasta", str(titulo))

    # ── preferências ────────────────────────────────────────

    def pref(self, chave, padrao=None):
        return self._app.preferencias.ler(chave, padrao)

    def guardar_pref(self, chave, valor):
        return self._app.preferencias.gravar(chave, valor)

    # ── tabela com seleção ──────────────────────────────────

    def tabela(self, colunas, linhas, selecionar=False):
        """Sem `selecionar`, a da Janela. Com, devolve a LINHA escolhida.

        Devolve o que foi passado — o vault inteiro, e não o texto da
        célula —, ou `void` enquanto nada foi escolhido. Uma seleção que
        aponta para além da lista (a lista encolheu) volta a `void`, em
        vez de devolver outra linha.
        """
        if not selecionar:
            return super().tabela(colunas, linhas)
        cabecalho = [str(c) for c in colunas]
        originais = list(linhas)
        corpo = []
        for linha in originais:
            if isinstance(linha, dict):
                corpo.append([_J._texto(linha.get(c)) for c in cabecalho])
            else:
                corpo.append([_J._texto(v) for v in linha])
        chave = self._chave("tabela_sel", ",".join(cabecalho))
        indice = self.estado.get(chave)
        if not isinstance(indice, int) or not 0 <= indice < len(originais):
            indice = None
        self._por(_J.No("tabela_sel", "", corpo,
                        {"colunas": cabecalho, "selecionada": indice}, chave))
        return originais[indice] if indice is not None else None


# ═══════════════════════════════════════════════════════════
#  Rodar uma vez — a mesma para a Sonda e para a janela
# ═══════════════════════════════════════════════════════════

def _executar(aplicacao, eventos, dialogos):
    """Roda a tela atual e segue a navegação. Devolve a tela montada.

    A navegação acontece AQUI, e não no desenho: é o mesmo caminho para a
    Sonda e para o Tk, e por isso o teste prova o que a janela faz.
    """
    if not aplicacao.telas:
        raise _erro("a aplicacao nao tem tela nenhuma",
                    dica='app.tela("inicio", inicio)')
    for _ in range(16):
        nome = aplicacao.tela_atual()
        t = TelaBigorna(aplicacao, nome, eventos, dialogos)
        try:
            aplicacao.telas[nome](t)
            return t
        except _Ir as ir:
            eventos = None
            if ir.atualizar:
                continue
            if ir.voltar:
                if len(aplicacao.pilha) > 1:
                    aplicacao.pilha.pop()
            else:
                if ir.destino == aplicacao.tela_atual():
                    aplicacao.parametros[ir.destino] = ir.parametros
                else:
                    aplicacao.pilha.append(ir.destino)
                    aplicacao.parametros[ir.destino] = ir.parametros
                    # Uma tela nova começa limpa: os campos da visita
                    # anterior não aparecem preenchidos na próxima.
                    aplicacao.estados.pop(ir.destino, None)
    raise _erro("a navegacao nao parou: 16 trocas de tela seguidas",
                nota="uma tela que chama t.ir() sem condicao manda para "
                     "outra, que manda de volta",
                dica="ponha o t.ir() dentro de um given (t.botao(...), t.comando(...))")


class _DialogosRoteirizados:
    """As respostas que o teste deu. Um diálogo sem resposta é falha."""

    def __init__(self):
        self.fila = []
        self.pedidos = []

    def pedir(self, especie, texto, tipos=None):
        self.pedidos.append({"dialogo": especie, "texto": texto})
        if not self.fila:
            raise _erro(
                f"a tela pediu '{especie}' ({texto}) e o teste nao respondeu",
                nota="um dialogo que o teste nao roteirizou e exatamente o "
                     "que quebra em producao — inventar um 'sim' esconderia",
                dica="s.responder(yes) (ou um caminho) ANTES da acao que abre o dialogo")
        return self.fila.pop(0)


# ═══════════════════════════════════════════════════════════
#  A Sonda
# ═══════════════════════════════════════════════════════════

class Sonda:
    """Usa a aplicação sem display: digita, clica, abre menu, responde."""

    def __init__(self, aplicacao):
        if not isinstance(aplicacao, AppBigorna):
            raise _erro("Bigorna.testar espera o app",
                        dica='s := B.testar(app)   // app := B.app("Nome")')
        self.app = aplicacao
        self.dialogos = _DialogosRoteirizados()
        self.tela = None
        self.execucoes = 0
        self.rodar()

    def rodar(self, eventos=None):
        self.execucoes += 1
        self.tela = _executar(self.app, eventos, self.dialogos)
        return self

    # ── agir ────────────────────────────────────────────────

    def _campo(self, rotulo):
        for chave, no in self.tela.campos().items():
            if no.rotulo == rotulo:
                return chave, no
        existem = ", ".join(sorted({n.rotulo for n in self.tela.campos().values()})) or "nenhum"
        raise _erro(f"nao ha campo '{rotulo}' na tela '{self.app.tela_atual()}'",
                    nota=f"os campos sao: {existem}")

    def digitar(self, rotulo, valor):
        chave, _ = self._campo(rotulo)
        self.tela.estado[chave] = valor
        return self.rodar()

    def marcar(self, rotulo, ligado=True):
        chave, _ = self._campo(rotulo)
        self.tela.estado[chave] = bool(ligado)
        return self.rodar()

    def escolher(self, rotulo, valor):
        chave, no = self._campo(rotulo)
        opcoes = no.opcoes.get("opcoes") or []
        if opcoes and str(valor) not in opcoes:
            raise _erro(f"'{valor}' nao e uma opcao de '{rotulo}'",
                        nota=f"as opcoes sao: {', '.join(opcoes)}")
        self.tela.estado[chave] = valor
        return self.rodar()

    def clicar(self, rotulo):
        for no in self._todos():
            if no.especie == "botao" and no.rotulo == rotulo:
                return self.rodar({no.chave: True})
        raise _erro(f"nao ha botao '{rotulo}' na tela '{self.app.tela_atual()}'",
                    nota=f"os botoes sao: {', '.join(self.botoes()) or 'nenhum'}")

    def menu(self, titulo, rotulo):
        """Escolhe um item de menu, como o mouse faria."""
        for m in self.app.menus:
            if m["titulo"] == titulo:
                for i in m["itens"]:
                    if i.get("rotulo") == rotulo:
                        return self.rodar({f"cmd:{i['comando']}": True})
                itens = ", ".join(i["rotulo"] for i in m["itens"] if "rotulo" in i)
                raise _erro(f"o menu '{titulo}' nao tem '{rotulo}'",
                            nota=f"ele tem: {itens}")
        raise _erro(f"nao ha menu '{titulo}'",
                    nota=f"os menus sao: {', '.join(m['titulo'] for m in self.app.menus) or 'nenhum'}")

    def atalho(self, teclas):
        """Aperta um atalho — `s.atalho("Ctrl+N")`, e `Cmd+N` é o mesmo."""
        alvo = _normalizar_atalho(teclas)
        comando = self.app.atalhos().get(alvo)
        if comando is None:
            existem = ", ".join(sorted(self.app.atalhos())) or "nenhum"
            raise _erro(f"nenhum item de menu usa {alvo}",
                        nota=f"os atalhos sao: {existem}")
        return self.rodar({f"cmd:{comando}": True})

    def selecionar(self, indice, tabela=0):
        """Escolhe a linha `indice` (a partir de 0) da tabela selecionável."""
        selecionaveis = [n for n in self._todos() if n.especie == "tabela_sel"]
        if not selecionaveis:
            raise _erro("nao ha tabela selecionavel nesta tela",
                        dica="t.tabela(colunas, linhas, selecionar := yes)")
        no = selecionaveis[int(tabela)]
        if not 0 <= int(indice) < len(no.valor or []):
            raise _erro(f"a tabela tem {len(no.valor or [])} linha(s), e pedi a {indice}")
        self.tela.estado[no.chave] = int(indice)
        return self.rodar()

    def responder(self, resposta):
        """A resposta do PRÓXIMO diálogo: yes/no, um caminho, ou void."""
        self.dialogos.fila.append(resposta)
        return self

    # ── perguntar ───────────────────────────────────────────

    def _todos(self):
        saida = []

        def descer(no):
            saida.append(no)
            for f in no.filhos:
                descer(f)

        descer(self.tela.arvore)
        return saida

    def texto(self):
        partes = [self.tela.texto_todo()]
        for no in self._todos():
            if no.especie == "tabela_sel":
                partes.extend(no.opcoes.get("colunas", []))
                for linha in (no.valor or []):
                    partes.extend(linha)
        return "\n".join(p for p in partes if p)

    def tem(self, texto):
        return str(texto) in self.texto()

    def valor(self, rotulo):
        return self._campo(rotulo)[1].valor

    def tela_atual(self):
        return self.app.tela_atual()

    def botoes(self):
        return [n.rotulo for n in self._todos() if n.especie == "botao"]

    def campos(self):
        return sorted({n.rotulo for n in self.tela.campos().values()})

    def status(self):
        return self.app.status_texto

    def notificacoes(self):
        return list(self.app.notificacoes)

    def dialogos_pedidos(self):
        return list(self.dialogos.pedidos)

    def menus(self):
        return [{"titulo": m["titulo"],
                 "itens": [i.get("rotulo", "—") for i in m["itens"]]}
                for m in self.app.menus]

    def arvore(self):
        return self.tela.arvore.como_vault()


def testar(aplicacao):
    return Sonda(aplicacao)


# ═══════════════════════════════════════════════════════════
#  A janela de verdade
# ═══════════════════════════════════════════════════════════

class _DialogosTk:
    def __init__(self, raiz):
        self.raiz = raiz

    def pedir(self, especie, texto, tipos=None):
        from tkinter import filedialog, messagebox
        filtros = [(t.upper(), f"*.{t.lstrip('.')}") for t in (tipos or [])]
        filtros.append(("Todos", "*.*"))
        if especie == "confirmar":
            return messagebox.askyesno(parent=self.raiz, title="", message=texto)
        if especie == "abrir_arquivo":
            return filedialog.askopenfilename(parent=self.raiz, title=texto,
                                              filetypes=filtros) or None
        if especie == "salvar_arquivo":
            return filedialog.asksaveasfilename(parent=self.raiz, initialfile=texto,
                                                filetypes=filtros) or None
        if especie == "escolher_pasta":
            return filedialog.askdirectory(parent=self.raiz, title=texto) or None
        return None                                       # pragma: no cover


_CORES = {
    "claro": {"fundo": "#F6F6F4", "texto": "#1B1B1B", "campo": "#FFFFFF",
              "linha": "#D9D9D6", "destaque": "#C0392B", "status": "#ECECE9"},
    "escuro": {"fundo": "#1C1C1E", "texto": "#EDEDED", "campo": "#2A2A2D",
               "linha": "#3A3A3D", "destaque": "#FF6B5B", "status": "#232326"},
}


def _aplicar_tema(raiz, tema, ttk):
    """'sistema' deixa o Tk seguir o sistema; claro e escuro pintam tudo."""
    estilo = ttk.Style(raiz)
    if tema == "sistema":
        return None
    cores = _CORES[tema]
    if "clam" in estilo.theme_names():
        estilo.theme_use("clam")
    raiz.configure(background=cores["fundo"])
    estilo.configure(".", background=cores["fundo"], foreground=cores["texto"],
                     fieldbackground=cores["campo"], bordercolor=cores["linha"])
    estilo.configure("TEntry", fieldbackground=cores["campo"], foreground=cores["texto"])
    estilo.configure("Treeview", background=cores["campo"], fieldbackground=cores["campo"],
                     foreground=cores["texto"])
    estilo.configure("Status.TLabel", background=cores["status"], padding=(10, 4))
    return cores


def tem_display():
    return _J.tem_display()


def rodar(aplicacao, fechar_em=0):
    """Abre a aplicação e fica nela até fecharem. Devolve as preferências.

    Pede a thread principal pelo mesmo motivo da Janela: o Tk do macOS
    chamado de outra thread derruba o processo em vez de levantar.
    """
    import threading

    if not isinstance(aplicacao, AppBigorna):
        raise _erro("Bigorna.rodar espera o app", dica="B.rodar(app)")
    if threading.current_thread() is not threading.main_thread():
        from ..interpreter import na_thread_principal
        feito = na_thread_principal(lambda: _rodar_aqui(aplicacao, fechar_em),
                                    prazo=86400.0)
        if feito is None:
            raise _erro("nao consegui a thread principal para abrir a janela.",
                        dica="chame B.rodar(app) no topo do programa")
        return feito
    return _rodar_aqui(aplicacao, fechar_em)


def _rodar_aqui(aplicacao, fechar_em=0):
    janela = _construir(aplicacao)
    raiz = janela["raiz"]
    if fechar_em and int(fechar_em) > 0:
        raiz.after(int(fechar_em), raiz.destroy)
    raiz.mainloop()
    return aplicacao.preferencias.tudo()


def _construir(aplicacao):
    """A janela montada e desenhada — sem o `mainloop`.

    Separado para o teste: ele monta a janela de verdade, aciona o menu
    pelo próprio Tk (`menu.invoke`) e confere os widgets. Fotografar a
    tela provaria menos e exigiria permissão de captura.
    """
    _J._exigir_tk()
    import tkinter as tk
    from tkinter import ttk

    raiz = tk.Tk()
    raiz.title(aplicacao.nome)
    raiz.geometry(f"{aplicacao.largura}x{aplicacao.altura}")
    cores = _aplicar_tema(raiz, aplicacao.tema, ttk)
    dialogos = _DialogosTk(raiz)
    quadro = {"corpo": None, "aviso": None}

    status = ttk.Label(raiz, text="", anchor="w", style="Status.TLabel")
    status.pack(side="bottom", fill="x")

    def redesenhar(eventos=None):
        tela = _executar(aplicacao, eventos, dialogos)
        if quadro["corpo"] is not None:
            quadro["corpo"].destroy()
        corpo = ttk.Frame(raiz, padding=14)
        corpo.pack(fill="both", expand=True)
        quadro["corpo"] = corpo
        _desenhar(corpo, tela.arvore, tela.estado, redesenhar, tk, ttk)
        status.configure(text=aplicacao.status_texto)
        raiz.title(f"{aplicacao.nome} — {aplicacao.tela_atual()}"
                   if len(aplicacao.telas) > 1 else aplicacao.nome)
        if aplicacao.notificacoes:
            mostrar_aviso(aplicacao.notificacoes[-1])
            aplicacao.notificacoes.clear()

    def mostrar_aviso(texto):
        if quadro["aviso"] is not None:
            quadro["aviso"].destroy()
        fundo = (cores or {}).get("destaque", "#C0392B")
        aviso = tk.Label(raiz, text=texto, bg=fundo, fg="white", padx=14, pady=6)
        aviso.place(relx=0.5, y=10, anchor="n")
        quadro["aviso"] = aviso
        raiz.after(2800, lambda a=aviso: a.destroy() if a.winfo_exists() else None)

    def disparar(comando):
        redesenhar({f"cmd:{comando}": True})

    if aplicacao.menus:
        barra = tk.Menu(raiz)
        for m in aplicacao.menus:
            sub = tk.Menu(barra, tearoff=0)
            for i in m["itens"]:
                if i.get("separador"):
                    sub.add_separator()
                    continue
                sub.add_command(label=i["rotulo"],
                                accelerator=_atalho_visivel(i["atalho"]) if i["atalho"] else "",
                                command=lambda c=i["comando"]: disparar(c))
            barra.add_cascade(label=m["titulo"], menu=sub)
        raiz.config(menu=barra)
    for atalho, comando in aplicacao.atalhos().items():
        raiz.bind_all(_atalho_tk(atalho), lambda _e, c=comando: disparar(c))

    redesenhar()
    return {"raiz": raiz, "status": status, "quadro": quadro,
            "barra": raiz.nametowidget(raiz["menu"]) if aplicacao.menus else None,
            "redesenhar": redesenhar, "dialogos": dialogos}


class _Um:
    """Um nó falso com um filho só — para desenhar um componente da Janela."""

    def __init__(self, filho):
        self.filhos = [filho]


def _desenhar(pai, no, estado, redesenhar, tk, ttk):
    """O que é da Bigorna desenha aqui; o resto, o desenho da Janela."""
    for filho in no.filhos:
        e = filho.especie
        if e == "tabela_sel":
            colunas = filho.opcoes.get("colunas", [])
            grade = ttk.Treeview(pai, columns=colunas, show="headings",
                                 height=10, selectmode="browse")
            for c in colunas:
                grade.heading(c, text=c)
            ids = [grade.insert("", "end", values=linha) for linha in (filho.valor or [])]
            escolhida = filho.opcoes.get("selecionada")
            if escolhida is not None and escolhida < len(ids):
                grade.selection_set(ids[escolhida])
            grade.pack(fill="both", expand=True, pady=6)

            def ao_escolher(_e, g=grade, c=filho.chave, lista=ids):
                marcadas = g.selection()
                if marcadas:
                    estado[c] = lista.index(marcadas[0])
                    redesenhar()
            grade.bind("<<TreeviewSelect>>", ao_escolher)
        elif e in ("grupo", "abas"):
            moldura = ttk.LabelFrame(pai, text=filho.rotulo, padding=10)
            moldura.pack(fill="both", expand=True, pady=6)
            _desenhar(moldura, filho, estado, redesenhar, tk, ttk)
        else:
            _J._desenhar(pai, _Um(filho), estado, redesenhar, tk, ttk)


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

class ArcaneBigorna(dict):
    """O dicionário que `adopt Arcane.Bigorna` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Bigorna",
            "app": app,
            "item": item,
            "separador": separador,
            "rodar": rodar,
            "testar": testar,
            "tem_display": tem_display,
            "pasta_de_config": pasta_de_config,
            "temas": lambda: list(TEMAS),
            "App": AppBigorna,
            "Tela": TelaBigorna,
            "Sonda": Sonda,
        }
