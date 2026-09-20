"""O núcleo: componente, árvore, sessão e estado.

Três objetos sustentam o framework inteiro.

**`No`** — um componente na árvore. Ele não sabe desenhar a si mesmo:
carrega o tipo, as propriedades e os filhos, e quem desenha é o
renderizador. Essa separação é o que permite a mesma árvore virar HTML,
JSON (para teste) ou texto (para o terminal).

**`Sessao`** — o estado de um usuário. Sobrevive entre execuções do
programa, que é o que torna o modelo "roda tudo de novo" utilizável.

**`Contexto`** — onde a árvore está sendo montada agora. É ele que faz
`V.texto(...)` saber em qual coluna, aba ou cartão o texto entra, sem
que quem escreve precise passar um pai a cada chamada.
"""

import hashlib
import threading
import time


class No:
    """Um componente. Tipo, propriedades, filhos.

    `chave` identifica o componente entre execuções — é como o valor de
    um campo sobrevive a um clique em outro lugar da página. Quando não
    é dada, sai do tipo mais o rótulo mais a posição, que é estável
    enquanto o programa não muda.
    """

    __slots__ = ("tipo", "props", "filhos", "chave")

    def __init__(self, tipo, props=None, filhos=None, chave=None):
        self.tipo = tipo
        self.props = props or {}
        self.filhos = filhos if filhos is not None else []
        self.chave = chave

    def acrescentar(self, filho):
        self.filhos.append(filho)
        return filho

    def para_vault(self):
        """A árvore como dado — é o que os testes conferem.

        Testar um componente não deveria exigir um navegador. Com a
        árvore em mãos, `V.teste.achar(arvore, "botao")` responde o que
        um teste precisa saber.
        """
        return {
            "tipo": self.tipo,
            "props": dict(self.props),
            "chave": self.chave,
            "filhos": [f.para_vault() for f in self.filhos],
        }

    def __repr__(self):
        return f"<{self.tipo} {len(self.filhos)} filho(s)>"


class Sessao:
    """O estado de um usuário, entre execuções.

    Ele existe porque o programa roda inteiro a cada interação: sem um
    lugar que sobreviva, um contador voltaria a zero a cada clique.

    A trava não é enfeite. O Kiln atende **um pedido por thread**, e
    dois pedidos da mesma sessão — duas abas, um clique duplo — chegam
    ao mesmo dicionário ao mesmo tempo.
    """

    def __init__(self, identificador):
        self.id = identificador
        self.dados = {}
        self.criada_em = time.time()
        self.tocada_em = time.time()
        self._trava = threading.RLock()

        #: O que o usuário mandou nesta execução: valor de campo, clique.
        self.entrada = {}
        #: O que foi clicado. Vale por UMA execução — um botão que
        #: continuasse "pressionado" dispararia a ação de novo no
        #: próximo carregamento da página.
        self.eventos = set()

    def obter(self, chave, padrao=None):
        with self._trava:
            return self.dados.get(chave, padrao)

    def definir(self, chave, valor):
        with self._trava:
            self.dados[chave] = valor
            self.tocada_em = time.time()
        return valor

    def existe(self, chave):
        with self._trava:
            return chave in self.dados

    def remover(self, chave):
        with self._trava:
            self.dados.pop(chave, None)

    def limpar(self):
        with self._trava:
            self.dados.clear()

    def tudo(self):
        with self._trava:
            return dict(self.dados)

    def expirou(self, segundos):
        return (time.time() - self.tocada_em) > segundos


class Contexto:
    """Onde a árvore está sendo montada agora.

    Uma pilha de nós: `V.texto(...)` entra no topo dela. É o que faz
    `coluna.texto(...)` cair dentro da coluna sem que cada chamada de
    componente precise receber um pai.

    Vive em `threading.local` porque o Kiln atende um pedido por thread,
    e duas sessões montando a árvore ao mesmo tempo não podem escrever
    uma na outra — esse bug seria intermitente e quase impossível de
    reproduzir.
    """

    _local = threading.local()

    @classmethod
    def atual(cls):
        return getattr(cls._local, "ctx", None)

    @classmethod
    def comecar(cls, sessao, config=None):
        ctx = cls(sessao, config)
        cls._local.ctx = ctx
        return ctx

    @classmethod
    def terminar(cls):
        ctx = cls.atual()
        cls._local.ctx = None
        return ctx

    def __init__(self, sessao, config=None):
        self.sessao = sessao
        self.config = config or {}
        self.raiz = No("pagina")
        self.pilha = [self.raiz]
        self.barra_lateral = No("barra_lateral")
        self.contador = 0
        #: Erros que o programa levantou — mostrados na página em vez de
        #: derrubarem a aplicação inteira.
        self.falhas = []

        #: Formulários a esvaziar DEPOIS que a página estiver montada.
        #: Esvaziar na hora apagaria os valores antes de quem escreveu
        #: o formulário poder lê-los.
        self.limpar_depois = []

        #: Onde estamos, e o que a aplicação precisa saber disto.
        self.app = None
        self.caminho = "/"
        self.pagina = "/"
        self.params = {}
        self.menu = []
        self.redirecionar = None
        self.duracao_ms = 0.0

        #: Configuração que ESTA execução mudou — 'V.configurar_pagina'.
        #: Fica separada da configuração da aplicação porque uma página
        #: que muda o título não deveria mudar o das outras.
        self.config_local = {}

        #: As chaves cujo valor CHEGOU diferente do que estava guardado.
        #: É o que faz `V.mudou(...)` responder sem callback: o modelo
        #: roda tudo de novo, e sem esta marca não haveria como saber
        #: se o campo mudou agora ou já estava assim.
        self.mudados = set()

        #: Avisos flutuantes desta execução — `V.toast(...)`.
        self.avisos = []

        #: A largura em que o que está sendo montado vai aparecer, em
        #: pixels de tela. É uma PILHA porque o layout aninha: uma
        #: coluna dentro de um painel dentro de uma malha.
        #:
        #: Ela existe por um defeito concreto: o gráfico é desenhado
        #: num sistema de 800 unidades e depois encolhido para caber no
        #: container. Num painel de um terço da tela, o fator é 0,45 —
        #: e um rótulo de 11px chega ao olho com 5px. Sem alguém dizer
        #: ao desenho quanto ele vai encolher, não há como compensar:
        #: o servidor não mede a tela.
        self.larguras = [1100]

        #: A pilha dos fragmentos abertos. Um componente montado aqui
        #: dentro pertence ao fragmento do topo, e é isso que permite
        #: responder a um clique redesenhando só aquele pedaço.
        self.fragmentos = []
        #: chave de componente -> chave do fragmento que o contém.
        self.dono_do_fragmento = {}
        #: chave do fragmento -> o nó dele, nesta montagem.
        self.nos_de_fragmento = {}

    # ── A pilha ──────────────────────────────────────────────

    @property
    def topo(self):
        return self.pilha[-1]

    def empilhar(self, no):
        self.topo.acrescentar(no)
        self.pilha.append(no)
        return no

    def desempilhar(self):
        if len(self.pilha) > 1:
            return self.pilha.pop()
        return None

    def por(self, no):
        """Acrescenta um componente onde a árvore está agora."""
        self.topo.acrescentar(no)
        return no

    # ── Quanto espaço há aqui ────────────────────────────────

    @property
    def largura(self):
        """A largura de tela do lugar em que estamos montando."""
        return self.larguras[-1]

    def estreitar(self, pixels):
        self.larguras.append(max(120.0, float(pixels)))
        return self.larguras[-1]

    def alargar(self):
        if len(self.larguras) > 1:
            self.larguras.pop()

    # ── Identidade estável ───────────────────────────────────

    def chave_para(self, tipo, rotulo="", chave=None):
        """A identidade do componente entre execuções.

        Com `chave` dada, é ela — e é assim que se mantém o valor de um
        campo quando a ordem dos componentes muda.

        Sem ela, sai do tipo, do rótulo e de um contador. É estável
        enquanto o programa não muda, e é o que permite não exigir uma
        chave de cada `V.entrada(...)`.
        """
        if chave:
            final = str(chave)
        else:
            self.contador += 1
            crua = f"{tipo}:{rotulo}:{self.contador}"
            final = hashlib.sha256(crua.encode()).hexdigest()[:12]
        if self.fragmentos:
            self.dono_do_fragmento[final] = self.fragmentos[-1]
        return final

    # ── Entrada do usuário ───────────────────────────────────

    def valor_de(self, chave, padrao=None):
        """O que o usuário mandou, ou o que ficou guardado, ou o padrão.

        A ordem importa: a entrada desta execução vence o que estava
        guardado, senão um campo editado voltaria ao valor anterior no
        mesmo instante em que se digita.
        """
        if chave in self.sessao.entrada:
            novo = self.sessao.entrada[chave]
            anterior = self.sessao.obter(f"__campo__{chave}")
            # A comparação é feita aqui, e não na gravação: é o único
            # ponto por onde o valor recém-chegado e o guardado passam
            # juntos. Sem isso, 'V.mudou' teria de adivinhar.
            if anterior != novo:
                self.mudados.add(chave)
            return novo
        if self.sessao.existe(f"__campo__{chave}"):
            return self.sessao.obter(f"__campo__{chave}")
        return padrao

    def guardar_valor(self, chave, valor):
        self.sessao.definir(f"__campo__{chave}", valor)

    def foi_acionado(self, chave):
        return chave in self.sessao.eventos
