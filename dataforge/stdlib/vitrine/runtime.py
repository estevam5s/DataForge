"""O runtime — a aplicação, o servidor, as sessões e o ciclo do pedido.

O ciclo, inteiro
----------------
1. O navegador pede `/`. O servidor acha (ou cria) a sessão.
2. O programa da página **roda do começo**, montando a árvore.
3. A árvore vira HTML e vai junto com o CSS e o cliente.
4. Alguém clica. O cliente manda `POST /__vitrine__/acao` com o que
   mudou.
5. Volta ao passo 2 — e a resposta é só o miolo da página.

Não há diffing, não há estado no cliente além do que está na tela, e o
caminho do primeiro carregamento é o mesmo de todos os outros. É o que
faz um bug ser reproduzível recarregando a página.

Sobre o Kiln
------------
Todo HTTP é dele: rota, corpo, cabeçalho, cookie, arquivo estático,
CORS, limite de taxa, teste sem socket. A Vitrine acrescenta o que o
Kiln não tem — sessão com estado vivo, montagem de árvore e o protocolo
de interação.
"""

import base64
import json
import os
import sys
import threading
import time
import traceback
import uuid

from . import render
from .componentes import _str
from .estado import Cache, Geral
from .nucleo import Contexto, No, Sessao

_KILN = None


def _kiln():
    global _KILN
    if _KILN is None:
        from ..kiln import ArcaneKiln
        _KILN = ArcaneKiln
    return _KILN


class Aplicacao:
    """Uma aplicação Vitrine.

    Guarda a configuração, as páginas, as sessões e o app Kiln que
    atende. Há uma por processo na prática, mas nada impede duas — e é
    isso que torna os testes independentes entre si.
    """

    def __init__(self, titulo="Vitrine", **config):
        self.config = {
            "titulo": titulo,
            "icone": "",
            "descricao": "",
            "idioma": "pt-BR",
            "tema": None,
            "modo_tema": "automatico",
            "cabecalho": False,
            "css": "",
            "javascript": "",
            "validade_sessao": 3600,
            "producao": False,
            "atualizar_a_cada": 0,
            "limite_upload": 8 * 1024 * 1024,
            "manifesto": False,
            "segredo": "",
        }
        self.config.update({k: v for k, v in config.items() if v is not None})

        self.paginas = []                 # [(caminho, acao, vault)]
        self.sessoes = {}
        self.geral = Geral()
        self.cache = Cache()
        self.antes = []                   # middleware da Vitrine
        self.depois = []
        self.plugins = {}
        #: Componentes registrados por nome. Ficam na APLICAÇÃO, e não
        #: no módulo: dois apps no mesmo processo — o que os testes
        #: fazem o tempo todo — não podem ver os componentes um do
        #: outro, ou um teste passaria por um registro que o anterior
        #: deixou.
        self.componentes = {}
        self.autenticador = None
        self.permissoes = {}
        self.trabalhos = []
        self.app = None                   # o App do Kiln
        self._trava = threading.RLock()
        self._metricas = {"execucoes": 0, "erros": 0, "ms_total": 0.0,
                          "inicio": time.time()}
        self._registro = []               # log em memória
        self.porta = None

    # ═══════════════════════════════════════════════════════
    #  Configuração
    # ═══════════════════════════════════════════════════════

    def configurar(self, chave=None, valor=None, **pares):
        """`V.configurar("titulo", "Painel")` ou por vault."""
        if isinstance(chave, dict):
            self.config.update(chave)
        elif chave is not None:
            self.config[str(chave)] = valor
        self.config.update(pares)
        return self

    # ═══════════════════════════════════════════════════════
    #  Páginas
    # ═══════════════════════════════════════════════════════

    def pagina(self, caminho, acao, titulo="", icone="", oculta=False):
        """Registra uma página.

        A ordem do registro é a ordem do menu. A primeira registrada é
        a de `/` quando ninguém reivindicou a raiz — um app de uma
        página não deveria precisar declarar rota nenhuma.
        """
        limpo = "/" + str(caminho).strip("/") if caminho != "/" else "/"
        self.paginas.append({
            "caminho": limpo,
            "acao": acao,
            "titulo": _str(titulo) or _titulo_de(limpo, acao),
            "icone": _str(icone),
            "oculta": bool(oculta),
        })
        return self

    def achar_pagina(self, caminho):
        limpo = "/" + str(caminho or "/").split("?")[0].strip("/")
        for pagina in self.paginas:
            if pagina["caminho"] == limpo:
                return pagina, {}
            params = _casa(pagina["caminho"], limpo)
            if params is not None:
                return pagina, params
        if limpo == "/" and self.paginas:
            return self.paginas[0], {}
        return None, {}

    def menu(self):
        return [{"caminho": p["caminho"], "titulo": p["titulo"],
                 "icone": p["icone"]}
                for p in self.paginas if not p["oculta"]]

    # ═══════════════════════════════════════════════════════
    #  Sessões
    # ═══════════════════════════════════════════════════════

    def sessao(self, identificador=None):
        with self._trava:
            self._limpar_vencidas()
            if identificador and identificador in self.sessoes:
                sessao = self.sessoes[identificador]
                sessao.tocada_em = time.time()
                return sessao
            nova = Sessao(identificador or uuid.uuid4().hex)
            self.sessoes[nova.id] = nova
            return nova

    def _limpar_vencidas(self):
        validade = self.config.get("validade_sessao") or 0
        if validade <= 0:
            return
        # Sem isto, um app público acumula uma sessão por visitante para
        # sempre — um vazamento de memória que só aparece depois de
        # semanas no ar, quando ninguém mais lembra de onde veio.
        vencidas = [i for i, s in self.sessoes.items() if s.expirou(validade)]
        for i in vencidas:
            del self.sessoes[i]

    def encerrar_sessao(self, identificador):
        with self._trava:
            self.sessoes.pop(identificador, None)

    # ═══════════════════════════════════════════════════════
    #  A execução de uma página
    # ═══════════════════════════════════════════════════════

    def executar(self, sessao, caminho="/", entrada=None, eventos=None,
                 params=None):
        """Roda o programa da página e devolve o contexto montado.

        Isto é o coração: tudo o mais é transporte.
        """
        pagina, da_rota = self.achar_pagina(caminho)
        sessao.entrada = dict(entrada or {})
        sessao.eventos = set(eventos or ())

        ctx = Contexto.comecar(sessao, self.config)
        ctx.app = self
        ctx.caminho = caminho
        ctx.params = {**da_rota, **(params or {})}
        ctx.pagina = pagina["caminho"] if pagina else caminho
        ctx.menu = self.menu()

        comeco = time.perf_counter()
        try:
            if pagina is None:
                _pagina_ausente(ctx, caminho)
            else:
                for meio in self.antes:
                    # Um middleware que devolve 'no' interrompe: é como
                    # se faz uma barreira de login sem espalhar o
                    # 'given' por todas as páginas.
                    if meio(ctx) is False:
                        break
                else:
                    self._rodar_pagina(ctx, pagina)
            for depois in self.depois:
                depois(ctx)
        finally:
            decorrido = (time.perf_counter() - comeco) * 1000
            with self._trava:
                self._metricas["execucoes"] += 1
                self._metricas["ms_total"] += decorrido
                if ctx.falhas:
                    self._metricas["erros"] += 1
            ctx.duracao_ms = round(decorrido, 2)
            Contexto.terminar()
            for no in ctx.limpar_depois:
                self._limpar_formulario(sessao, no)
        return ctx

    #: Quantas vezes uma página pode se reexecutar numa interação.
    #: Um 'V.recarregar()' incondicional é um laço infinito, e o teto
    #: transforma um travamento de servidor num erro que se lê.
    MAX_REEXECUCOES = 4

    def _rodar_pagina(self, ctx, pagina, tentativa=1):
        try:
            pagina["acao"]()
        except _Reexecutar:
            if tentativa >= self.MAX_REEXECUCOES:
                ctx.falhas.append({
                    "mensagem": "a pagina se reexecutou vezes demais.",
                    "detalhe": "V.recarregar() sem condicao roda para "
                               "sempre; ponha um 'given' em volta."})
                return
            # A árvore montada até aqui é descartada: ela foi montada
            # com o estado velho, que é justamente o que mudou.
            ctx.raiz.filhos.clear()
            ctx.barra_lateral.filhos.clear()
            ctx.pilha[:] = [ctx.raiz]
            ctx.contador = 0
            return self._rodar_pagina(ctx, pagina, tentativa + 1)
        except _Parar:
            # 'V.parar()' — o programa decidiu que a página acaba aqui.
            pass
        except _Navegar as salto:
            ctx.redirecionar = salto.destino
        except BaseException as erro:      # noqa: BLE001
            # Os sinais da própria linguagem — 'halt', 'skip', 'yield'
            # — também derivam de BaseException, e engoli-los aqui
            # transformaria um 'yield' fora de lugar em página em
            # branco. Eles seguem para quem sabe o que fazer com eles.
            if type(erro).__name__.endswith("Signal"):
                raise
            # Amplo de propósito: uma exceção numa página derrubaria o
            # servidor inteiro e tiraria do ar as outras sessões. O erro
            # aparece NA página, que é onde quem está desenvolvendo o vê.
            if type(erro).__name__ in ("KeyboardInterrupt", "SystemExit"):
                raise
            self._anotar_falha(ctx, erro)

    def _anotar_falha(self, ctx, erro):
        detalhe = ""
        if not self.config.get("producao"):
            detalhe = "".join(traceback.format_exception(
                type(erro), erro, erro.__traceback__))[-2400:]
        mensagem = getattr(erro, "message", None) or str(erro) or type(erro).__name__
        ctx.falhas.append({"mensagem": mensagem, "detalhe": detalhe})
        self.registrar("erro", mensagem, {"pagina": ctx.pagina})

    def _limpar_formulario(self, sessao, no):
        """Esvazia só os campos DESTE formulário.

        Varrer tudo o que comeca com '__campo__' apagaria os campos da
        página inteira — o filtro da barra lateral voltaria ao padrão
        toda vez que alguém cadastrasse alguma coisa.
        """
        for chave in _chaves_de(no):
            sessao.remover(f"__campo__{chave}")

    # ═══════════════════════════════════════════════════════
    #  Autenticação e autorização
    # ═══════════════════════════════════════════════════════

    def autenticacao(self, verificador, papeis=None):
        """A ação que confere usuário e senha.

        Recebe `(usuario, senha)` e devolve o vault do usuário, ou
        `void`. O que ela devolve fica na sessão e sai em `V.usuario()`.
        """
        self.autenticador = verificador
        self.permissoes = dict(papeis or {})
        return self

    def entrar(self, sessao, usuario, senha):
        if self.autenticador is None:
            from ...errors import RuntimeError_
            raise RuntimeError_(
                "nenhuma autenticacao foi registrada.", 0, 0,
                dica="V.autenticacao(conferir) antes de V.entrar(...)",
                doc="tecnicas/vitrine")
        quem = self.autenticador(usuario, senha)
        if not quem:
            self.registrar("aviso", "login recusado", {"usuario": usuario})
            return None
        if not isinstance(quem, dict):
            quem = {"nome": _str(quem)}
        sessao.definir("__usuario__", quem)
        # Trocar o identificador no login fecha a fixação de sessão: um
        # id plantado antes do login deixa de valer no instante em que
        # ele importaria.
        self.registrar("info", "login", {"usuario": quem.get("nome", "")})
        return quem

    def sair(self, sessao):
        sessao.remover("__usuario__")
        sessao.remover("__papel__")

    def pode(self, sessao, permissao):
        quem = sessao.obter("__usuario__") or {}
        papel = quem.get("papel") or quem.get("perfil") or ""
        concedidas = self.permissoes.get(papel, [])
        return permissao in concedidas or "*" in concedidas

    # ═══════════════════════════════════════════════════════
    #  Observabilidade
    # ═══════════════════════════════════════════════════════

    def registrar(self, nivel, mensagem, extra=None):
        linha = {"quando": time.time(), "nivel": nivel,
                 "mensagem": _str(mensagem), "extra": dict(extra or {})}
        with self._trava:
            self._registro.append(linha)
            # Um log em memória sem teto é um vazamento; 2000 linhas é o
            # suficiente para investigar o que acabou de acontecer, que
            # é para o que ele serve.
            if len(self._registro) > 2000:
                del self._registro[:-1000]
        if not self.config.get("producao") and nivel in ("erro", "aviso"):
            # No stderr, e não no stdout: isto é diagnóstico, não saída
            # do programa. Misturado ao 'out', ele suja o que um teste
            # compara e o que um pipe recebe.
            print(f"  [vitrine:{nivel}] {mensagem}", file=sys.stderr)
        return linha

    def logs(self, quantos=100, nivel=""):
        with self._trava:
            linhas = [l for l in self._registro
                      if not nivel or l["nivel"] == nivel]
            return linhas[-int(quantos):]

    def metricas(self):
        with self._trava:
            m = dict(self._metricas)
        execucoes = m["execucoes"] or 1
        return {
            "execucoes": m["execucoes"],
            "erros": m["erros"],
            "media_ms": round(m["ms_total"] / execucoes, 2),
            "sessoes": len(self.sessoes),
            "paginas": len(self.paginas),
            "no_ar_s": round(time.time() - m["inicio"], 1),
            "cache": self.cache.estatisticas(),
        }

    def saude(self):
        """O que um balanceador pergunta antes de mandar tráfego."""
        return {"estado": "ok", "no_ar_s": round(
            time.time() - self._metricas["inicio"], 1),
            "sessoes": len(self.sessoes), "versao": self.config.get("versao", "")}

    # ═══════════════════════════════════════════════════════
    #  Plugins
    # ═══════════════════════════════════════════════════════

    def plugin(self, nome, instalar):
        """Um plugin é uma ação que recebe a aplicação e acrescenta algo.

        Registrar duas vezes o mesmo nome é erro, e não substituição
        silenciosa: dois plugins com o mesmo nome quase sempre são um
        `adopt` duplicado, e descobrir isso por um comportamento que
        sumiu é caro.
        """
        nome = _str(nome)
        if nome in self.plugins:
            from ...errors import RuntimeError_
            raise RuntimeError_(
                f"o plugin '{nome}' ja foi instalado.", 0, 0,
                dica="cada plugin entra uma vez; escolha outro nome",
                doc="tecnicas/vitrine")
        self.plugins[nome] = instalar
        instalar(self)
        return self

    # ═══════════════════════════════════════════════════════
    #  O servidor
    # ═══════════════════════════════════════════════════════

    def montar(self):
        """Monta o app Kiln. Não sobe nada — é o que torna testável."""
        if self.app is not None:
            return self.app
        K = _kiln()
        app = K._forge(self.config.get("titulo", "vitrine"))
        app.config["vitrine"] = self

        K._get(app, "/__vitrine__/saude", lambda req: self.saude())
        K._get(app, "/__vitrine__/metricas", lambda req: self.metricas())
        K._post(app, "/__vitrine__/acao", lambda req: self._atender_acao(req))
        K._get(app, "/__vitrine__/baixar/:chave",
               lambda req: self._atender_baixar(req))
        if self.config.get("manifesto"):
            K._get(app, "/__vitrine__/manifesto.json",
                   lambda req: self._manifesto())

        for pasta in self.config.get("estaticos", []) or []:
            K._static(app, pasta.get("rota", "/static"), pasta.get("pasta", "."))

        for caminho in {p["caminho"] for p in self.paginas} or {"/"}:
            K._get(app, caminho, self._atender_pagina)
        if not any(p["caminho"] == "/" for p in self.paginas):
            K._get(app, "/", self._atender_pagina)
        # A curinga vem por último: o Kiln casa na ordem do registro, e
        # posta antes ela engoliria as páginas declaradas.
        K._get(app, "/*caminho", self._atender_pagina)

        self.app = app
        return app

    def subir(self, porta=8501, host="127.0.0.1", silencioso=False,
              recarregar=False):
        """Sobe e bloqueia. `recarregar := yes` reinicia ao salvar.

        O `dataforge vitrine` passa porta, host e recarregar pelo
        **ambiente**, e eles vencem o que está escrito no arquivo. É o
        que permite `dataforge vitrine dev --porta=8600` sem reescrever
        o `V.subir(porta := 8501)` de quem escreveu o programa.
        """
        porta = int(os.environ.get("VITRINE_PORTA") or porta)
        host = os.environ.get("VITRINE_HOST") or host
        recarregar = recarregar or os.environ.get("VITRINE_RECARREGAR") == "1"
        app = self.montar()
        if recarregar:
            _vigiar(self, host, porta)
        if not silencioso:
            _anunciar(self, host, porta)
        return _kiln()._listen(app, porta, host, silencioso=True)

    def servir(self, porta=0, host="127.0.0.1"):
        """Sobe em segundo plano e devolve a porta. Para testes."""
        self.porta = _kiln()._serve(self.montar(), porta, host)
        return self.porta

    def parar(self):
        if self.app is not None:
            _kiln()._stop(self.app)
        return self

    # ── Os handlers ──────────────────────────────────────────

    def _atender_pagina(self, req):
        sessao = self.sessao(req["cookies"].get("vitrine_sid"))
        ctx = self.executar(sessao, req["path"], params=req.get("query"))
        if getattr(ctx, "redirecionar", None):
            return {"__kiln__": True, "status": 302,
                    "headers": {"Location": ctx.redirecionar}, "body": "",
                    "content_type": "text/html", "cookies": []}
        corpo = render.pagina(ctx, {**self.config, **ctx.config_local})
        return {
            "__kiln__": True, "status": 200,
            "headers": dict(_SEGURANCA), "body": corpo,
            "content_type": "text/html; charset=utf-8",
            "cookies": [self._cookie_de_sessao(sessao)],
        }

    def _cookie_de_sessao(self, sessao):
        """A linha `Set-Cookie`, **já formatada**.

        O Kiln guarda cookie como texto pronto, e não como vault: quem
        põe um dicionário aqui vê `Set-Cookie: {'nome': …}` sair no
        cabeçalho, o navegador descartar o cookie e cada pedido abrir
        uma sessão nova. O sintoma é cruel — um contador que nunca passa
        de 1 e um login que nunca "pega" —, e nada dá erro.
        """
        partes = [f"vitrine_sid={sessao.id}", "Path=/", "SameSite=Lax",
                  "HttpOnly"]
        validade = int(self.config.get("validade_sessao") or 0)
        if validade > 0:
            partes.append(f"Max-Age={validade}")
        if self.config.get("https"):
            partes.append("Secure")
        return "; ".join(partes)

    def _atender_acao(self, req):
        corpo = req["body"] if isinstance(req["body"], dict) else {}
        sessao = self.sessao(req["cookies"].get("vitrine_sid"))
        extra = corpo.get("extra") or {}
        if extra.get("arquivo"):
            self._guardar_arquivos(sessao, extra)

        evento = corpo.get("evento") or ""
        caminho = corpo.get("caminho") or "/"
        ctx = self.executar(sessao, caminho,
                            entrada=corpo.get("campos") or {},
                            eventos=[evento] if evento else [])
        if getattr(ctx, "redirecionar", None):
            return {"__kiln__": True, "status": 200, "headers": {},
                    "content_type": "application/json",
                    "body": {"redirecionar": ctx.redirecionar},
                    "cookies": [self._cookie_de_sessao(sessao)]}
        config = {**self.config, **ctx.config_local}
        return {
            "__kiln__": True, "status": 200,
            "headers": {"X-Content-Type-Options": "nosniff"},
            "content_type": "application/json; charset=utf-8",
            "body": {"html": render.corpo_html(ctx, config),
                     "titulo": config.get("titulo", ""),
                     "ms": ctx.duracao_ms},
            "cookies": [self._cookie_de_sessao(sessao)],
        }

    def _guardar_arquivos(self, sessao, extra):
        """O que o navegador mandou em base64 vira bytes na sessão."""
        limite = int(self.config.get("limite_upload") or 0)
        pacote = []
        for arquivo in extra.get("arquivos") or []:
            try:
                dados = base64.b64decode(arquivo.get("conteudo") or "")
            except (ValueError, TypeError):
                continue
            if limite and len(dados) > limite:
                self.registrar("aviso", "arquivo recusado por tamanho",
                               {"nome": arquivo.get("nome", "")})
                continue
            pacote.append({
                "nome": _str(arquivo.get("nome", "")),
                "tamanho": len(dados),
                "tipo": _str(arquivo.get("tipo", "")),
                "conteudo": dados,
                "texto": dados.decode("utf-8", errors="replace"),
            })
        chave = extra["arquivo"]
        sessao.definir(f"__arquivo__{chave}",
                       pacote if len(pacote) != 1 else pacote[0])

    def _atender_baixar(self, req):
        sessao = self.sessao(req["cookies"].get("vitrine_sid"))
        pacote = sessao.obter(f"__baixar__{req['params'].get('chave', '')}")
        if not pacote:
            return {"__kiln__": True, "status": 404, "headers": {},
                    "body": "nada para baixar", "content_type": "text/plain",
                    "cookies": []}
        return {
            "__kiln__": True, "status": 200,
            "headers": {"Content-Disposition":
                        f'attachment; filename="{pacote["nome"]}"'},
            "body": pacote["conteudo"], "content_type": pacote["tipo"],
            "cookies": [],
        }

    def _manifesto(self):
        return {
            "name": self.config.get("titulo", "Vitrine"),
            "short_name": self.config.get("titulo", "Vitrine")[:12],
            "start_url": "/", "display": "standalone",
            "background_color": "#FFFFFF", "theme_color": "#FED403",
            "description": self.config.get("descricao", ""),
        }


#: Os cabeçalhos que toda resposta HTML leva. Não são configuráveis
#: para cima: uma aplicação que precise afrouxar um deles diz isso
#: explicitamente em 'V.configurar', e aí fica escrito no código.
_SEGURANCA = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy":
        "default-src 'self'; img-src 'self' data: https:; "
        "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; "
        "frame-ancestors 'self'",
}


class _Parar(BaseException):
    """`V.parar()` — acaba a página aqui, sem erro.

    Deriva de `BaseException`, e não de `Exception`, pelo mesmo motivo
    que `halt` e `skip` na linguagem: é um **sinal de controle**, não
    um erro. O interpretador embrulha toda `Exception` que sai de uma
    função Python num `RuntimeError_` — e com isso `V.parar()` virava
    a mensagem "exigir_login: _Parar" no meio da página, em vez de
    parar coisa alguma.
    """


class _Navegar(BaseException):
    """`V.navegar(...)` — sai desta página e vai para outra. Ver `_Parar`."""

    def __init__(self, destino):
        super().__init__(destino)
        self.destino = destino


class _Reexecutar(BaseException):
    """Joga fora o que foi montado e roda a página de novo, do começo.

    É o que `V.recarregar()` faz, e o que acontece sozinho quando
    alguém acaba de entrar: a página precisa ser montada como a de
    quem já está logado, e não continuar de dentro do `otherwise` em
    que o formulário de entrada estava.
    """


def _chaves_de(no):
    """Todas as chaves de componente dentro de um nó, recursivamente."""
    achadas = []
    pilha = [no]
    while pilha:
        atual = pilha.pop()
        if atual.chave:
            achadas.append(atual.chave)
        pilha.extend(atual.filhos)
    return achadas


def _titulo_de(caminho, acao):
    nome = getattr(acao, "name", None) or getattr(acao, "__name__", "")
    if caminho == "/":
        return nome.replace("_", " ").capitalize() or "Início"
    return caminho.strip("/").split("/")[-1].replace("_", " ").replace(
        "-", " ").capitalize()


def _casa(padrao, caminho):
    """`/produto/:id` casa com `/produto/42` e entrega `{"id": "42"}`."""
    if ":" not in padrao:
        return None
    partes_p = padrao.strip("/").split("/")
    partes_c = caminho.strip("/").split("/")
    if len(partes_p) != len(partes_c):
        return None
    params = {}
    for p, c in zip(partes_p, partes_c):
        if p.startswith(":"):
            params[p[1:]] = c
        elif p != c:
            return None
    return params


def _pagina_ausente(ctx, caminho):
    from . import componentes as C
    C.titulo("404")
    C.texto(f"A página {caminho} não existe.")
    if ctx.menu:
        C.texto("Páginas disponíveis:")
        for item in ctx.menu:
            C.link(item["titulo"], item["caminho"])


def _anunciar(app, host, porta):
    titulo = app.config.get("titulo", "Vitrine")
    print(f"\n  \033[1;33m◆ Vitrine\033[0m  {titulo}")
    print(f"  \033[2mno ar em\033[0m  http://{host}:{int(porta)}")
    paginas = len(app.paginas) or 1
    print(f"  \033[2m{paginas} pagina(s) · Ctrl-C para parar\033[0m\n")


# ═══════════════════════════════════════════════════════════
#  Hot reload
# ═══════════════════════════════════════════════════════════

def _vigiar(app, host, porta, intervalo=0.7):
    """Reinicia o processo quando um `.df` do projeto muda.

    Reiniciar o **processo**, e não recarregar o módulo: o estado de um
    módulo recarregado pela metade produz erros que não existem no
    código, e depurar isso custa mais do que o segundo do reinício.
    """
    raiz = os.getcwd()

    def instantaneo():
        marcas = {}
        for pasta, _dirs, arquivos in os.walk(raiz):
            if any(p in pasta for p in (".git", "forge_modules", "__pycache__")):
                continue
            for nome in arquivos:
                if nome.endswith(".df"):
                    caminho = os.path.join(pasta, nome)
                    try:
                        marcas[caminho] = os.path.getmtime(caminho)
                    except OSError:
                        pass
        return marcas

    def laco():
        anterior = instantaneo()
        while True:
            time.sleep(intervalo)
            atual = instantaneo()
            if atual != anterior:
                mudou = [c for c in atual
                         if anterior.get(c) != atual[c]]
                nome = os.path.basename(mudou[0]) if mudou else "projeto"
                print(f"\n  \033[2m↻ {nome} mudou — reiniciando\033[0m\n")
                app.parar()
                os.execv(sys.executable, [sys.executable] + sys.argv)
            anterior = atual

    threading.Thread(target=laco, daemon=True).start()
