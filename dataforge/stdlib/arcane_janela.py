# -*- coding: utf-8 -*-
"""Arcane.Janela — aplicação de mesa nativa, com zero dependência.

O Tk vem **na biblioteca padrão do Python**, e é a única forma de
desenhar uma janela nativa em macOS, Windows e Linux sem trazer nada de
fora. Qt, GTK e wx dariam mais controle e quebrariam a única promessa
inegociável do projeto.

A forma é a da Vitrine, e isso não é coincidência: **o programa inteiro
roda de novo a cada interação**, e o estado da sessão sobrevive. É o que
dispensa callback, diffing e a pergunta "onde fica o estado" — e é o que
torna uma tela testável.

    adopt Arcane.Janela as J

    action tela(t):
        t.titulo("Cadastro")
        nome := t.entrada("Nome")
        given t.botao("Salvar"):
            t.aviso($"salvo: {nome}")

    J.abrir(J.app("Cadastro"), tela)     # com Tk, na sua máquina
    s := J.testar(tela)                  # sem Tk, no CI

A separação entre a ÁRVORE e o DESENHO é o que permite a segunda linha.
Uma biblioteca de interface que só funciona com display é uma biblioteca
sem teste — e o runner do CI não tem display nenhum.

O que ela NÃO é
---------------
Não é um construtor de interface rica: não há animação, tema
personalizado por componente, arrastar-e-soltar, nem gráfico
interativo. Para painel de dados existe a **Vitrine**, que roda no
navegador e desenha 27 tipos de gráfico. Esta peça é para a ferramenta
interna de mesa — a que lê um arquivo, mostra uma tabela, tem quatro
botões e precisa rodar numa máquina sem navegador.
"""

import os
import sys

from ..errors import RuntimeError_

_DOC = "desktop/janela"

#: Os componentes que a árvore conhece. A lista é fechada de propósito:
#: cada um precisa saber se desenhar E se testar, e um componente que
#: só existe de um lado é o que faz a Sonda mentir.
COMPONENTES = (
    "titulo", "texto", "aviso", "erro", "separador", "espaco",
    "entrada", "senha", "numero", "area", "escolha", "caixa",
    "opcoes", "deslizante", "data", "arquivo",
    "botao", "tabela", "lista", "progresso", "abas", "grupo",
)


def _erro(mensagem, nota="", dica=""):
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


class No:
    """Um componente da árvore: o que ele é, e o que ele mostra."""

    __slots__ = ("especie", "rotulo", "valor", "opcoes", "filhos", "chave")

    def __init__(self, especie, rotulo="", valor=None, opcoes=None, chave=""):
        self.especie = especie
        self.rotulo = str(rotulo)
        self.valor = valor
        self.opcoes = dict(opcoes or {})
        self.filhos = []
        self.chave = chave or f"{especie}:{rotulo}"

    def como_vault(self):
        return {"especie": self.especie, "rotulo": self.rotulo,
                "valor": self.valor, "opcoes": dict(self.opcoes),
                "filhos": [f.como_vault() for f in self.filhos]}

    def __repr__(self):                                  # pragma: no cover
        return f"<{self.especie} {self.rotulo!r}>"


class Tela:
    """O que a ação de tela recebe: os componentes, e o estado.

    Cada chamada devolve o VALOR daquele campo — `nome := t.entrada(…)`
    lê o que está digitado. É o que faz a tela ser um programa comum,
    de cima para baixo, em vez de um grafo de callbacks.
    """

    def __init__(self, estado, eventos=None, titulo=""):
        self.arvore = No("raiz", titulo)
        self._pilha = [self.arvore]
        self.estado = estado if estado is not None else {}
        self._eventos = dict(eventos or {})
        self._usados = set()

    # ── a pilha de montagem ─────────────────────────────────

    def _por(self, no):
        self._pilha[-1].filhos.append(no)
        return no

    def _chave(self, especie, rotulo):
        """Uma chave estável por componente, e única na tela.

        Dois campos com o mesmo rótulo existem — e sem o contador eles
        dividiriam o estado, o que faz digitar num mudar o outro.
        """
        base = f"{especie}:{rotulo}"
        if base not in self._usados:
            self._usados.add(base)
            return base
        n = 2
        while f"{base}#{n}" in self._usados:
            n += 1
        self._usados.add(f"{base}#{n}")
        return f"{base}#{n}"

    # ── conteúdo ────────────────────────────────────────────

    def titulo(self, texto):
        self._por(No("titulo", texto))
        return texto

    def texto(self, conteudo):
        self._por(No("texto", str(conteudo)))
        return conteudo

    def aviso(self, conteudo):
        self._por(No("aviso", str(conteudo)))
        return conteudo

    def erro(self, conteudo):
        self._por(No("erro", str(conteudo)))
        return conteudo

    def separador(self):
        self._por(No("separador"))
        return True

    def espaco(self, altura=8):
        self._por(No("espaco", "", int(altura)))
        return True

    # ── entradas ────────────────────────────────────────────

    def _campo(self, especie, rotulo, padrao, opcoes=None):
        chave = self._chave(especie, rotulo)
        valor = self.estado.get(chave, padrao)
        self._por(No(especie, rotulo, valor, opcoes, chave))
        return valor

    def entrada(self, rotulo, padrao=""):
        return self._campo("entrada", rotulo, padrao)

    def senha(self, rotulo, padrao=""):
        return self._campo("senha", rotulo, padrao)

    def numero(self, rotulo, padrao=0, minimo=None, maximo=None):
        valor = self._campo("numero", rotulo, padrao,
                            {"minimo": minimo, "maximo": maximo})
        try:
            return int(valor) if float(valor) == int(float(valor)) else float(valor)
        except (TypeError, ValueError):
            return padrao

    def area(self, rotulo, padrao="", linhas=5):
        return self._campo("area", rotulo, padrao, {"linhas": int(linhas)})

    def escolha(self, rotulo, opcoes, padrao=None):
        lista = [str(o) for o in opcoes]
        if not lista:
            raise _erro(f"a escolha '{rotulo}' nao tem opcao nenhuma",
                        dica="passe ao menos uma: t.escolha(\"Cor\", [\"azul\"])")
        inicial = str(padrao) if padrao is not None else lista[0]
        return self._campo("escolha", rotulo, inicial, {"opcoes": lista})

    def opcoes(self, rotulo, opcoes, padrao=None):
        """Várias de uma lista — devolve os marcados."""
        lista = [str(o) for o in opcoes]
        return self._campo("opcoes", rotulo, list(padrao or []),
                           {"opcoes": lista})

    def caixa(self, rotulo, padrao=False):
        return bool(self._campo("caixa", rotulo, bool(padrao)))

    def deslizante(self, rotulo, minimo=0, maximo=100, padrao=None):
        inicial = minimo if padrao is None else padrao
        return self._campo("deslizante", rotulo, inicial,
                           {"minimo": minimo, "maximo": maximo})

    def data(self, rotulo, padrao=""):
        return self._campo("data", rotulo, padrao)

    def arquivo(self, rotulo, padrao="", tipos=None):
        """O caminho escolhido. Sem display, é só um campo de texto."""
        return self._campo("arquivo", rotulo, padrao,
                           {"tipos": list(tipos or [])})

    # ── ação ────────────────────────────────────────────────

    def botao(self, rotulo, destaque=False):
        """`yes` na execução em que ele foi clicado, e só nela.

        O clique é um EVENTO, e não estado: se ele ficasse guardado, a
        próxima reexecução salvaria o formulário de novo — que é o
        defeito clássico de quem monta isto à mão.
        """
        chave = self._chave("botao", rotulo)
        self._por(No("botao", rotulo, None, {"destaque": bool(destaque)}, chave))
        return bool(self._eventos.get(chave))

    # ── mostrar ─────────────────────────────────────────────

    def tabela(self, colunas, linhas):
        cabecalho = [str(c) for c in colunas]
        corpo = []
        for linha in linhas:
            if isinstance(linha, dict):
                corpo.append([_texto(linha.get(c)) for c in cabecalho])
            else:
                corpo.append([_texto(v) for v in linha])
        self._por(No("tabela", "", corpo, {"colunas": cabecalho}))
        return len(corpo)

    def lista(self, itens):
        valores = [_texto(i) for i in itens]
        self._por(No("lista", "", valores))
        return len(valores)

    def progresso(self, fracao, rotulo=""):
        f = max(0.0, min(1.0, float(fracao)))
        self._por(No("progresso", rotulo, f))
        return f

    # ── layout ──────────────────────────────────────────────

    def grupo(self, titulo=""):
        """Uma moldura com título. Use com `t.fim()`."""
        no = self._por(No("grupo", titulo))
        self._pilha.append(no)
        return no

    def aba(self, titulo):
        no = self._por(No("abas", titulo))
        self._pilha.append(no)
        return no

    def fim(self):
        """Fecha o grupo ou a aba aberta."""
        if len(self._pilha) == 1:
            raise _erro("nao ha grupo aberto para fechar",
                        dica="cada t.fim() fecha um t.grupo() ou um t.aba()")
        self._pilha.pop()
        return True

    # ── ler a árvore ────────────────────────────────────────

    def campos(self):
        """Os campos da tela, por chave — é o que a Sonda preenche."""
        achados = {}

        def descer(no):
            if no.especie in ("entrada", "senha", "numero", "area", "escolha",
                              "opcoes", "caixa", "deslizante", "data", "arquivo"):
                achados[no.chave] = no
            for f in no.filhos:
                descer(f)

        descer(self.arvore)
        return achados

    def texto_todo(self):
        """Tudo o que a tela mostra, como texto — para conferir."""
        partes = []

        def descer(no):
            if no.especie in ("titulo", "texto", "aviso", "erro"):
                partes.append(no.rotulo)
            elif no.especie in ("botao", "grupo", "abas"):
                partes.append(no.rotulo)
            elif no.especie in ("entrada", "senha", "numero", "area", "escolha",
                                "opcoes", "caixa", "deslizante", "data", "arquivo"):
                partes.append(f"{no.rotulo}: {_texto(no.valor)}")
            elif no.especie == "lista":
                partes.extend(no.valor or [])
            elif no.especie == "tabela":
                partes.extend(no.opcoes.get("colunas", []))
                for linha in (no.valor or []):
                    partes.extend(linha)
            for f in no.filhos:
                descer(f)

        descer(self.arvore)
        return "\n".join(p for p in partes if p)


def _texto(valor):
    if valor is None:
        return ""
    if valor is True:
        return "yes"
    if valor is False:
        return "no"
    if isinstance(valor, list):
        return ", ".join(_texto(v) for v in valor)
    return str(valor)


# ═══════════════════════════════════════════════════════════
#  A aplicação
# ═══════════════════════════════════════════════════════════

class App:
    """O que a janela é: nome, tamanho e o estado que sobrevive."""

    def __init__(self, titulo="DataForge", largura=720, altura=520,
                 tema="claro"):
        self.titulo = str(titulo)
        self.largura = int(largura)
        self.altura = int(altura)
        self.tema = str(tema)
        self.estado = {}

    def __repr__(self):                                  # pragma: no cover
        return f"<app {self.titulo!r} {self.largura}x{self.altura}>"


def app(titulo="DataForge", largura=720, altura=520, tema="claro"):
    return App(titulo, largura, altura, tema)


def montar(tela_acao, estado=None, eventos=None, titulo=""):
    """Roda a ação de tela e devolve a Tela montada — sem desenhar nada.

    É o que a Sonda usa, e é o que o desenho usa: uma ÁRVORE só, e duas
    leituras dela. Duas montagens diferentes fariam a Sonda aprovar o
    que a janela reprova.
    """
    if not callable(tela_acao):
        raise _erro("Janela.montar espera uma acao de tela",
                    dica="action tela(t): t.titulo(\"Olá\")")
    t = Tela(estado if estado is not None else {}, eventos, titulo)
    tela_acao(t)
    return t


# ═══════════════════════════════════════════════════════════
#  A Sonda — clicar e digitar sem display nenhum
# ═══════════════════════════════════════════════════════════

class Sonda:
    """Preenche, clica e pergunta — sem Tk.

    Uma biblioteca de interface que só funciona com display é uma
    biblioteca sem teste: o runner do CI não tem display. Por isso a
    árvore é a mesma dos dois lados, e a Sonda não simula nada — ela
    monta a tela de verdade.
    """

    def __init__(self, tela_acao, estado=None, titulo=""):
        self.acao = tela_acao
        self.estado = dict(estado or {})
        self.titulo = titulo
        self.tela = None
        self.execucoes = 0
        self.falha = None
        self.rodar()

    def rodar(self, eventos=None):
        self.execucoes += 1
        try:
            self.tela = montar(self.acao, self.estado, eventos, self.titulo)
            self.falha = None
        except RuntimeError_:
            raise
        except Exception as erro:                        # noqa: BLE001
            self.falha = str(erro)
            raise
        return self.tela

    # ── agir ────────────────────────────────────────────────

    def _campo(self, rotulo):
        campos = self.tela.campos()
        for chave, no in campos.items():
            if no.rotulo == rotulo:
                return chave, no
        perto = ", ".join(sorted({n.rotulo for n in campos.values()})) or "nenhum"
        raise _erro(f"nao ha campo '{rotulo}' nesta tela",
                    nota=f"os campos sao: {perto}",
                    dica="o rotulo e o mesmo texto que aparece ao lado")

    def digitar(self, rotulo, valor):
        chave, _ = self._campo(rotulo)
        self.estado[chave] = valor
        return self.rodar()

    def marcar(self, rotulo, ligado=True):
        chave, _ = self._campo(rotulo)
        self.estado[chave] = bool(ligado)
        return self.rodar()

    def escolher(self, rotulo, valor):
        chave, no = self._campo(rotulo)
        opcoes = no.opcoes.get("opcoes") or []
        if opcoes and str(valor) not in opcoes:
            raise _erro(f"'{valor}' nao e uma opcao de '{rotulo}'",
                        nota=f"as opcoes sao: {', '.join(opcoes)}")
        self.estado[chave] = valor
        return self.rodar()

    def clicar(self, rotulo):
        """Clica e reexecuta — o clique vale para UMA execução."""
        for no in self._todos():
            if no.especie == "botao" and no.rotulo == rotulo:
                return self.rodar({no.chave: True})
        botoes = ", ".join(n.rotulo for n in self._todos()
                           if n.especie == "botao") or "nenhum"
        raise _erro(f"nao ha botao '{rotulo}' nesta tela",
                    nota=f"os botoes sao: {botoes}")

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
        return self.tela.texto_todo()

    def valor(self, rotulo):
        _, no = self._campo(rotulo)
        return no.valor

    def tem(self, texto):
        return str(texto) in self.texto()

    def botoes(self):
        return [n.rotulo for n in self._todos() if n.especie == "botao"]

    def campos(self):
        return sorted({n.rotulo for n in self.tela.campos().values()})

    def tabelas(self):
        return [{"colunas": n.opcoes.get("colunas", []), "linhas": n.valor or []}
                for n in self._todos() if n.especie == "tabela"]

    def arvore(self):
        return self.tela.arvore.como_vault()


def testar(tela_acao, estado=None, titulo=""):
    return Sonda(tela_acao, estado, titulo)


# ═══════════════════════════════════════════════════════════
#  O desenho, com Tk
# ═══════════════════════════════════════════════════════════

def tem_display():
    """Há como abrir uma janela nesta máquina?

    Ela **não abre uma janela para descobrir**, e essa foi a primeira
    versão: criar um `Tk()` de sondagem derrubou o processo inteiro no
    macOS — e não com uma exceção, com um **crash**, porque o Tk exige
    a thread principal e o programa roda numa thread propria. Uma
    pergunta que mata o processo e pior que nenhuma pergunta.

    O que sobra é o que dá para saber sem abrir nada: o Tk existe, e o
    sistema tem para onde desenhar. Quando isso passa e mesmo assim não
    há display, quem diz é o `abrir` — com a mensagem dele, e não com
    um traceback do Tcl.
    """
    try:
        import tkinter  # noqa: F401
    except ImportError:
        return False
    if sys.platform.startswith("linux"):
        return bool(os.environ.get("DISPLAY")
                    or os.environ.get("WAYLAND_DISPLAY"))
    return True


def _exigir_tk():
    try:
        import tkinter  # noqa: F401
    except ImportError:
        raise _erro(
            "este Python nao tem Tk.",
            nota="o Tk vem com o Python, mas algumas distribuicoes o separam",
            dica="Debian e Ubuntu: apt install python3-tk") from None
    if not tem_display():
        raise _erro(
            "nao ha display para abrir a janela.",
            nota="num servidor, num contêiner ou por ssh sem X isto e normal",
            dica="para testar sem display use Janela.testar(tela); para servir "
                 "uma interface por rede, a Vitrine roda no navegador")


def abrir(aplicacao, tela_acao, quando_fechar=None, fechar_em=0):
    """Abre a janela e fica nela até fecharem. Devolve o estado final.

    Ela pede a **thread principal** para desenhar. O programa roda numa
    thread própria (a da pilha maior), e o Tk do macOS exige a
    principal: chamado de outra, ele não levanta — ele **derruba o
    processo**, com um despejo de pilha do Objective-C que não menciona
    nada do programa de quem escreveu.
    """
    import threading

    if not isinstance(aplicacao, App):
        raise _erro("Janela.abrir espera um app",
                    dica='J.abrir(J.app("Título"), tela)')

    if threading.current_thread() is not threading.main_thread():
        from ..interpreter import na_thread_principal
        feito = na_thread_principal(
            lambda: _abrir_aqui(aplicacao, tela_acao, quando_fechar, fechar_em),
            prazo=86400.0)
        if feito is None:
            raise _erro(
                "nao consegui a thread principal para abrir a janela.",
                nota="o Tk do macOS so desenha na principal, e chamado de "
                     "outra ele derruba o processo em vez de levantar",
                dica="abra a janela no topo do programa, e nao dentro de "
                     "um 'thread' ou de um 'parallel'")
        return feito
    return _abrir_aqui(aplicacao, tela_acao, quando_fechar, fechar_em)


def _abrir_aqui(aplicacao, tela_acao, quando_fechar=None, fechar_em=0):
    """O desenho de verdade — sempre na thread principal.

    `fechar_em` (em milissegundos) fecha a janela sozinha. Ele existe
    para o teste de ponta a ponta: uma janela que só fecha no clique
    nao tem como ser exercitada num CI, e o que nao se exercita quebra
    calado — a Sonda prova a arvore, e nao o desenho.
    """
    _exigir_tk()
    import tkinter as tk
    from tkinter import ttk

    raiz = tk.Tk()
    raiz.title(aplicacao.titulo)
    raiz.geometry(f"{aplicacao.largura}x{aplicacao.altura}")
    estado = aplicacao.estado

    quadro = {"atual": None}

    def redesenhar(eventos=None):
        if quadro["atual"] is not None:
            quadro["atual"].destroy()
        corpo = ttk.Frame(raiz, padding=12)
        corpo.pack(fill="both", expand=True)
        quadro["atual"] = corpo
        tela = montar(tela_acao, estado, eventos, aplicacao.titulo)
        _desenhar(corpo, tela.arvore, estado, redesenhar, tk, ttk)

    redesenhar()
    if fechar_em and int(fechar_em) > 0:
        raiz.after(int(fechar_em), raiz.destroy)
    if quando_fechar is not None:
        raiz.protocol("WM_DELETE_WINDOW",
                      lambda: (quando_fechar(estado), raiz.destroy()))
    raiz.mainloop()
    return estado


def _desenhar(pai, no, estado, redesenhar, tk, ttk):
    """A árvore vira widgets. Uma espécie por ramo, e nada de genérico."""
    for filho in no.filhos:
        e = filho.especie
        if e == "titulo":
            ttk.Label(pai, text=filho.rotulo,
                      font=("TkDefaultFont", 15, "bold")).pack(anchor="w", pady=(0, 8))
        elif e == "texto":
            ttk.Label(pai, text=filho.rotulo, wraplength=640,
                      justify="left").pack(anchor="w", pady=2)
        elif e == "aviso":
            ttk.Label(pai, text=filho.rotulo, foreground="#0a7").pack(anchor="w", pady=2)
        elif e == "erro":
            ttk.Label(pai, text=filho.rotulo, foreground="#c33").pack(anchor="w", pady=2)
        elif e == "separador":
            ttk.Separator(pai, orient="horizontal").pack(fill="x", pady=8)
        elif e == "espaco":
            ttk.Frame(pai, height=int(filho.valor or 8)).pack()
        elif e in ("entrada", "senha", "numero", "data", "arquivo"):
            linha = ttk.Frame(pai)
            linha.pack(fill="x", pady=3)
            ttk.Label(linha, text=filho.rotulo, width=18).pack(side="left")
            var = tk.StringVar(value=_texto(filho.valor))
            campo = ttk.Entry(linha, textvariable=var,
                              show="•" if e == "senha" else "")
            campo.pack(side="left", fill="x", expand=True)
            var.trace_add("write",
                          lambda *_a, c=filho.chave, v=var: estado.__setitem__(c, v.get()))
        elif e == "area":
            ttk.Label(pai, text=filho.rotulo).pack(anchor="w", pady=(6, 2))
            campo = tk.Text(pai, height=int(filho.opcoes.get("linhas", 5)))
            campo.insert("1.0", _texto(filho.valor))
            campo.pack(fill="both", expand=True)
            campo.bind("<KeyRelease>",
                       lambda _e, c=filho.chave, w=campo:
                       estado.__setitem__(c, w.get("1.0", "end-1c")))
        elif e == "escolha":
            linha = ttk.Frame(pai)
            linha.pack(fill="x", pady=3)
            ttk.Label(linha, text=filho.rotulo, width=18).pack(side="left")
            var = tk.StringVar(value=_texto(filho.valor))
            caixa = ttk.Combobox(linha, textvariable=var, state="readonly",
                                 values=filho.opcoes.get("opcoes", []))
            caixa.pack(side="left", fill="x", expand=True)
            caixa.bind("<<ComboboxSelected>>",
                       lambda _e, c=filho.chave, v=var:
                       (estado.__setitem__(c, v.get()), redesenhar()))
        elif e == "caixa":
            var = tk.BooleanVar(value=bool(filho.valor))
            ttk.Checkbutton(
                pai, text=filho.rotulo, variable=var,
                command=lambda c=filho.chave, v=var:
                (estado.__setitem__(c, v.get()), redesenhar())).pack(anchor="w", pady=2)
        elif e == "deslizante":
            linha = ttk.Frame(pai)
            linha.pack(fill="x", pady=3)
            ttk.Label(linha, text=filho.rotulo, width=18).pack(side="left")
            var = tk.DoubleVar(value=float(filho.valor or 0))
            ttk.Scale(linha, from_=float(filho.opcoes.get("minimo", 0)),
                      to=float(filho.opcoes.get("maximo", 100)), variable=var,
                      command=lambda _v, c=filho.chave, v=var:
                      estado.__setitem__(c, v.get())).pack(side="left", fill="x",
                                                           expand=True)
        elif e == "botao":
            ttk.Button(pai, text=filho.rotulo,
                       command=lambda c=filho.chave: redesenhar({c: True})
                       ).pack(anchor="w", pady=4)
        elif e == "tabela":
            colunas = filho.opcoes.get("colunas", [])
            grade = ttk.Treeview(pai, columns=colunas, show="headings", height=8)
            for c in colunas:
                grade.heading(c, text=c)
            for linha in (filho.valor or []):
                grade.insert("", "end", values=linha)
            grade.pack(fill="both", expand=True, pady=6)
        elif e == "lista":
            caixa = tk.Listbox(pai, height=min(10, max(3, len(filho.valor or []))))
            for item in (filho.valor or []):
                caixa.insert("end", item)
            caixa.pack(fill="both", expand=True, pady=6)
        elif e == "progresso":
            barra = ttk.Progressbar(pai, maximum=1.0, value=float(filho.valor or 0))
            barra.pack(fill="x", pady=6)
        elif e == "grupo":
            moldura = ttk.LabelFrame(pai, text=filho.rotulo, padding=10)
            moldura.pack(fill="both", expand=True, pady=6)
            _desenhar(moldura, filho, estado, redesenhar, tk, ttk)
        elif e == "abas":
            # Uma aba solta vira um grupo: o Tk precisa de um Notebook,
            # e criar um por aba daria uma pilha de abas de uma aba só.
            moldura = ttk.LabelFrame(pai, text=filho.rotulo, padding=10)
            moldura.pack(fill="both", expand=True, pady=6)
            _desenhar(moldura, filho, estado, redesenhar, tk, ttk)


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

class ArcaneJanela(dict):
    """O dicionário que `adopt Arcane.Janela` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Janela",

            "app": app,
            "abrir": abrir,
            "montar": montar,
            "testar": testar,
            "tem_display": tem_display,

            "App": App,
            "Tela": Tela,
            "Sonda": Sonda,
            "No": No,

            "componentes": lambda: list(COMPONENTES),
        }
