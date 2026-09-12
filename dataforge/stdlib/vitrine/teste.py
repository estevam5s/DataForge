"""Testar uma aplicação Vitrine sem navegador.

O framework foi desenhado para isto: a árvore de componentes é um dado,
e conferir um dado é o que um teste sabe fazer.

    adopt Arcane.Vitrine as V
    adopt Crucible

    action pagina():
        V.titulo("Painel")
        given V.botao("Somar"):
            V.estado.somar("total")
        V.metrica("Total", V.estado.obter("total", 0))

    crucible "a pagina":
        trial "o botao soma":
            t := V.testar(pagina)
            t.clicar("Somar")
            assert t.metrica("Total") is "1"

Duas formas de perguntar
------------------------
`t.achar("botao")` devolve os nós; `t.texto()` devolve a página como
texto corrido, e é com ele que se escreve `assert "erro" in t.texto()`
sem saber a estrutura.
"""

from . import render
from .nucleo import Sessao
from .componentes import _str


class Sonda:
    """Uma aplicação rodando em memória, com uma sessão só."""

    def __init__(self, app, caminho="/"):
        self.app = app
        self.caminho = caminho
        self.sessao = app.sessao()
        self.ctx = None
        self.rodar()

    # ── Rodar ────────────────────────────────────────────────

    def rodar(self, entrada=None, eventos=None):
        self.ctx = self.app.executar(self.sessao, self.caminho,
                                     entrada=entrada, eventos=eventos)
        return self

    def ir_para(self, caminho):
        self.caminho = caminho
        return self.rodar()

    # ── Agir ─────────────────────────────────────────────────

    def clicar(self, rotulo):
        """Clica no botão com esse rótulo e roda a página de novo."""
        no = self._por_rotulo(("botao", "enviar"), rotulo)
        if no is None:
            self._reclamar("botao", rotulo)
        return self.rodar(eventos=[no.props["chave"]])

    def digitar(self, rotulo, valor):
        no = self._por_rotulo(
            ("entrada", "area", "numero", "deslizante", "data", "cor"), rotulo)
        if no is None:
            self._reclamar("campo", rotulo)
        return self.rodar(entrada={no.props["chave"]: valor})

    def marcar(self, rotulo, valor=True):
        no = self._por_rotulo(("caixa", "interruptor"), rotulo)
        if no is None:
            self._reclamar("caixa", rotulo)
        return self.rodar(entrada={no.props["chave"]: bool(valor)})

    def selecionar(self, rotulo, valor):
        no = self._por_rotulo(("escolha", "opcao", "escolhas"), rotulo)
        if no is None:
            self._reclamar("escolha", rotulo)
        return self.rodar(entrada={no.props["chave"]: valor})

    def abrir_aba(self, rotulo):
        for no in self.achar("abas"):
            if rotulo in no.props.get("rotulos", []):
                return self.rodar(entrada={no.props["chave"]: rotulo})
        self._reclamar("aba", rotulo)

    def enviar(self, formulario=""):
        """Aperta o botão de envio — do formulário nomeado, se houver."""
        for no in self.achar("enviar"):
            chave = no.props.get("chave", "")
            if not formulario or chave == f"__form__{formulario}":
                return self.rodar(eventos=[chave])
        self._reclamar("formulario", formulario or "(qualquer)")

    def enviar_arquivo(self, rotulo, nome, conteudo):
        no = self._por_rotulo(("arquivo",), rotulo)
        if no is None:
            self._reclamar("campo de arquivo", rotulo)
        dados = conteudo.encode() if isinstance(conteudo, str) else conteudo
        self.sessao.definir(f"__arquivo__{no.props['chave']}", {
            "nome": nome, "tamanho": len(dados), "tipo": "",
            "conteudo": dados,
            "texto": dados.decode("utf-8", errors="replace")})
        return self.rodar()

    # ── Perguntar ────────────────────────────────────────────

    def achar(self, tipo="", onde=None):
        """Todos os nós de um tipo, na ordem em que aparecem."""
        raiz = onde if onde is not None else self.ctx.raiz
        achados = []

        def descer(no):
            if not tipo or no.tipo == tipo:
                achados.append(no)
            for filho in no.filhos:
                descer(filho)

        descer(raiz)
        if onde is None:
            for filho in self.ctx.barra_lateral.filhos:
                descer(filho)
        return [n for n in achados if n is not raiz or tipo == raiz.tipo]

    def primeiro(self, tipo):
        achados = self.achar(tipo)
        return achados[0] if achados else None

    def existe(self, tipo, rotulo=""):
        if not rotulo:
            return bool(self.achar(tipo))
        return self._por_rotulo((tipo,), rotulo) is not None

    def quantos(self, tipo):
        return len(self.achar(tipo))

    def texto(self):
        """A página inteira como texto corrido, sem marcação."""
        pedacos = []

        def descer(no):
            for campo in ("conteudo", "rotulo", "mensagem", "titulo",
                          "subtitulo", "valor"):
                valor = no.props.get(campo)
                if isinstance(valor, str) and valor:
                    pedacos.append(valor)
            for linha in no.props.get("linhas", []) or []:
                pedacos.extend(str(c) for c in linha)
            for filho in no.filhos:
                descer(filho)

        descer(self.ctx.barra_lateral)
        descer(self.ctx.raiz)
        return "\n".join(pedacos)

    def html(self):
        return render.pagina(self.ctx, {**self.app.config,
                                        **self.ctx.config_local})

    def arvore(self):
        return self.ctx.raiz.para_vault()

    def metrica(self, rotulo):
        no = self._por_rotulo(("metrica",), rotulo)
        return no.props["valor"] if no else None

    def valor(self, rotulo):
        """O valor de um campo, como a página o mostra agora."""
        for no in self.achar():
            if no.props.get("rotulo") == rotulo and "valor" in no.props:
                return no.props["valor"]
        return None

    def alertas(self, nivel=""):
        return [n.props["mensagem"] for n in self.achar("alerta")
                if not nivel or n.props.get("nivel") == nivel]

    def falhou(self):
        return bool(self.ctx.falhas)

    def falhas(self):
        return [f["mensagem"] for f in self.ctx.falhas]

    def estado(self, chave, padrao=None):
        return self.sessao.obter(chave, padrao)

    def duracao_ms(self):
        return self.ctx.duracao_ms

    # ── Internas ─────────────────────────────────────────────

    def _por_rotulo(self, tipos, rotulo):
        alvo = _str(rotulo)
        for no in self.achar():
            if no.tipo in tipos and no.props.get("rotulo") == alvo:
                return no
        return None

    def _reclamar(self, que, rotulo):
        from ...errors import RuntimeError_
        disponiveis = sorted({n.props["rotulo"] for n in self.achar()
                              if n.props.get("rotulo")})
        raise RuntimeError_(
            f"nao ha {que} com o rotulo '{rotulo}' nesta pagina.", 0, 0,
            nota=("os rotulos na pagina: " + ", ".join(disponiveis[:12])
                  if disponiveis else "a pagina nao tem nenhum componente "
                                      "com rotulo"),
            doc="tecnicas/vitrine")


def testar(pagina_ou_app, caminho="/"):
    """Prepara uma sonda. Aceita uma ação de página ou uma aplicação.

    Quando a ação já está registrada na aplicação atual, é ela que é
    testada, no caminho em que foi registrada. Isso importa mais do que
    parece: uma sonda com aplicação própria não teria a autenticação, o
    middleware nem os plugins que o programa configurou — e o teste
    passaria (ou falharia) por um motivo que não existe em produção.
    """
    from .runtime import Aplicacao
    if isinstance(pagina_ou_app, Aplicacao):
        return Sonda(pagina_ou_app, caminho)

    from .api import _ATUAL
    atual = _ATUAL["app"]
    if atual is not None:
        for pagina in atual.paginas:
            if pagina["acao"] is pagina_ou_app:
                return Sonda(atual, pagina["caminho"])

    app = Aplicacao("teste")
    app.config["producao"] = False
    if atual is not None:
        # A página não está registrada — mas o que o programa
        # configurou continua valendo.
        app.config.update({k: v for k, v in atual.config.items()
                           if k != "titulo"})
        app.autenticador = atual.autenticador
        app.permissoes = dict(atual.permissoes)
        app.antes = list(atual.antes)
        app.depois = list(atual.depois)
        app.geral = atual.geral
        app.cache = atual.cache
    app.pagina("/", pagina_ou_app)
    return Sonda(app, caminho)


def pedir(app, metodo, caminho, corpo=None, cabecalhos=None):
    """Um pedido HTTP de verdade contra a aplicação, sem socket.

    É o que testa cabeçalho de segurança, status e redirecionamento —
    coisas que a sonda não vê, porque ela pula o HTTP.
    """
    from .runtime import _kiln
    return _kiln()._test(app.montar(), metodo, caminho, corpo, cabecalhos)
