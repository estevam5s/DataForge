# -*- coding: utf-8 -*-
"""A aplicacao de um bot: rotas, contexto, conversa, polling e webhook.

O `arcane_telegram.py` fala com a Bot API. Este arquivo e o que
transforma noventa metodos HTTP num programa que se le de cima para
baixo:

    mark @app.comando("start")
    action comecar(ctx):
        ctx.responder("Ola!")

Cinco decisoes, e o problema de cada uma
----------------------------------------
1. **O update e casado uma vez, na ordem do registro.** O primeiro
   tratador que casa atende, e os outros nao veem o update. A
   alternativa — entregar a todos — parece mais flexivel e produz o
   bug mais confuso que um bot tem: duas respostas para uma mensagem,
   e ninguem sabe de onde veio a segunda.

2. **O estado e POR CHAT, e o armazem e trocavel.** Guardar "em que
   passo este chat esta" num dicionario solto e o que todo bot faz
   errado: funciona ate o segundo usuario, e some quando o processo
   reinicia. Em memoria e o padrao; `Tg.estado_em_arquivo(...)`
   sobrevive ao reinicio.

3. **Um erro num tratador nao derruba o bot.** Ele e anotado, o
   tratador de erro roda, e o proximo update e atendido. Um bot que
   morre porque uma pessoa mandou um emoji inesperado e um bot que
   fica fora do ar de madrugada.

4. **O `offset` so avanca depois do update ser tratado.** Avancar
   antes perde a mensagem quando o processo cai no meio — e e
   exatamente no meio que ele cai.

5. **Polling e webhook sao o MESMO caminho.** `_atender` recebe um
   update e nao sabe de onde ele veio. Sem isso, um bot testado em
   polling quebra ao ir para webhook, que e justamente quando ele vai
   para producao.
"""

import json
import os
import re
import threading
import time
import traceback

from . import arcane_telegram as T

_erro = T._erro


# ═══════════════════════════════════════════════════════════
#  O que um tratador recebe
# ═══════════════════════════════════════════════════════════

class _EstadoDoChat:
    """O estado de um chat, lido e gravado ATRAVES do armazem.

    Ela finge ser um vault para quem escreve o bot — indexar, escrever,
    `in`, `len`, `keys` e `cycle` funcionam —, e cada operacao fala com
    o armazem. Num armazem em arquivo isso e uma leitura por acesso; e
    o preco de a promessa ser verdadeira, e um bot faz punhados de
    acessos por mensagem, nao milhares.
    """

    __slots__ = ("_app", "_chat")

    def __init__(self, app, chat):
        self._app = app
        self._chat = chat

    def _ler(self):
        return self._app.estado_de(self._chat)

    def __getitem__(self, chave):
        return self._ler()[str(chave)]

    def __setitem__(self, chave, valor):
        self._app.guardar(self._chat, chave, valor)

    def __delitem__(self, chave):
        self._app.esquecer(self._chat, chave)

    def __contains__(self, chave):
        return str(chave) in self._ler()

    def __iter__(self):
        return iter(self._ler())

    def __len__(self):
        return len(self._ler())

    def __eq__(self, outro):
        return self._ler() == outro

    def __ne__(self, outro):
        return self._ler() != outro

    def get(self, chave, padrao=None):
        return self._ler().get(str(chave), padrao)

    def keys(self):
        return list(self._ler())

    def values(self):
        return list(self._ler().values())

    def items(self):
        return list(self._ler().items())

    def para_vault(self):
        """Uma copia, para quem quer a foto e nao a vista."""
        return self._ler()

    def __repr__(self):
        return f"<estado do chat {self._chat}: {self._ler()!r}>"


class Contexto:
    """Tudo o que o tratador precisa, sem ele ter de cavar o update.

    O update cru continua em `ctx.update` — um bot de verdade sempre
    acaba precisando de um campo que nenhuma conveniencia cobre, e
    esconder o dado original so adiaria o problema.
    """

    __slots__ = ("bot", "app", "update", "tipo", "mensagem", "chat",
                 "usuario", "texto", "args", "dados", "callback",
                 "consulta", "_respostas")

    def __init__(self, app, update):
        self.app = app
        self.bot = app.bot
        self.update = update
        self._respostas = []

        self.tipo, self.mensagem = _tipo_do_update(update)
        self.callback = update.get("callback_query")
        self.consulta = update.get("inline_query")

        origem = self.mensagem or {}
        if self.callback:
            origem = self.callback.get("message") or {}
        self.chat = (origem.get("chat") or {}).get("id")
        self.usuario = (self.callback or self.consulta
                        or self.mensagem or {}).get("from") or {}
        self.texto = str((self.mensagem or {}).get("text")
                         or (self.mensagem or {}).get("caption") or "")
        self.dados = str((self.callback or {}).get("data") or "")
        if self.consulta:
            self.texto = str(self.consulta.get("query") or "")
        self.args = _argumentos(self.texto)

    # ── Quem ─────────────────────────────────────────────────

    def id_do_usuario(self):
        return self.usuario.get("id")

    def nome(self):
        """O nome de quem falou — o primeiro, que e o que sempre existe."""
        return str(self.usuario.get("first_name") or
                   self.usuario.get("username") or "")

    def apelido(self):
        return str(self.usuario.get("username") or "")

    def e_privado(self):
        origem = self.mensagem or (self.callback or {}).get("message") or {}
        return str((origem.get("chat") or {}).get("type", "")) == "private"

    def e_grupo(self):
        origem = self.mensagem or (self.callback or {}).get("message") or {}
        return str((origem.get("chat") or {}).get("type", "")) in (
            "group", "supergroup")

    def e_admin(self):
        """Se quem falou administra este chat. Em privado, e sempre `yes`."""
        if self.e_privado():
            return True
        return self.bot.e_admin(self.chat, self.id_do_usuario())

    # ── Responder ────────────────────────────────────────────

    def responder(self, texto, **opcoes):
        """Manda no mesmo chat. E o que 90% dos tratadores fazem."""
        return self._registrar("texto", self.bot.enviar(
            self.chat, texto, **opcoes), texto=texto)

    def citar(self, texto, **opcoes):
        """Responde CITANDO a mensagem. Em grupo, e o que da contexto."""
        if self.mensagem:
            opcoes.setdefault("responder_a", self.mensagem.get("message_id"))
        return self.responder(texto, **opcoes)

    def responder_foto(self, foto, legenda="", **opcoes):
        return self._registrar("foto", self.bot.foto(
            self.chat, foto, legenda, **opcoes), texto=legenda)

    def responder_documento(self, arquivo, legenda="", **opcoes):
        return self._registrar("documento", self.bot.documento(
            self.chat, arquivo, legenda, **opcoes), texto=legenda)

    def digitando(self, tipo="typing"):
        return self.bot.acao(self.chat, tipo)

    def editar(self, texto, **opcoes):
        """Edita a mensagem do botao. So faz sentido num callback."""
        origem = (self.callback or {}).get("message") or {}
        if not origem:
            raise _erro("nao ha mensagem para editar neste update.",
                        nota="'ctx.editar' edita a mensagem do BOTAO",
                        dica="num tratador de texto, use ctx.responder(...)")
        return self._registrar("edicao", self.bot.editar(
            self.chat, origem.get("message_id"), texto, **opcoes),
            texto=texto)

    def apagar(self):
        origem = self.mensagem or (self.callback or {}).get("message") or {}
        return self.bot.apagar(self.chat, origem.get("message_id"))

    def avisar(self, texto="", alerta=False):
        """A resposta do botao. Chamar SEMPRE, mesmo sem texto.

        Sem ela, o Telegram deixa o botao com o relogio girando por ate
        um minuto e quem clicou conclui que o bot travou.
        """
        if not self.callback:
            return None
        return self._registrar("aviso", self.bot.responder_botao(
            self.callback.get("id"), texto, alerta), texto=texto)

    def _registrar(self, tipo, resultado, texto=""):
        self._respostas.append({"tipo": tipo, "texto": texto,
                                "resultado": resultado})
        return resultado

    # ── Estado deste chat ────────────────────────────────────

    @property
    def estado(self):
        """O vault deste chat, que sobrevive entre mensagens.

        E uma VISTA sobre o armazem, e nao uma copia dele. A primeira
        versao devolvia `dict(...)`: `ctx.estado["carrinho"] := c`
        escrevia num dicionario descartavel e a mudanca sumia — sem
        erro, sem aviso, e com a documentacao prometendo o contrario.
        O sintoma era um carrinho que nunca enchia.

        A copia nao era descuido: `EmArquivo` LE do disco, e ali nao
        ha dicionario vivo para entregar. Por isso a vista, que le e
        grava atraves do armazem e funciona igual nos dois.
        """
        return _EstadoDoChat(self.app, self.chat)

    def guardar(self, chave, valor):
        return self.app.guardar(self.chat, chave, valor)

    def lembrar(self, chave, padrao=None):
        return self.app.estado_de(self.chat).get(str(chave), padrao)

    def esquecer(self, chave=None):
        return self.app.esquecer(self.chat, chave)

    # ── Consulta inline ──────────────────────────────────────

    def responder_consulta(self, resultados, cache=300, pessoal=False,
                           proxima=""):
        """Responde uma consulta inline, com o id JA preenchido.

        Era a unica resposta que caia no bot cru: todas as outras sao
        `ctx.responder*`, e esta obrigava a escrever
        `ctx.bot.responder_inline(ctx.consulta["id"], …)` — com o id
        a mao, que e exatamente o que se esquece.

        Cada item aceita a forma curta (`id`, `titulo`, `texto`) e vira
        o `article` que a Bot API espera. Passar o vault completo
        continua valendo, para quem precisa de um tipo diferente.
        """
        if not self.consulta:
            raise _erro(
                "esta nao e uma consulta inline.",
                nota=f"o update e do tipo '{self.tipo}'",
                dica="responda uma consulta dentro de um "
                     "'mark @app.inline()'")
        prontos = [self._resultado_inline(r) for r in (resultados or [])]
        return self._registrar(
            "consulta",
            self.bot.responder_inline(self.consulta.get("id"), prontos,
                                      cache, pessoal, proxima),
            texto=f"{len(prontos)} resultado(s)")

    @staticmethod
    def _resultado_inline(item):
        """A forma curta vira o 'article' da Bot API."""
        if not isinstance(item, dict):
            raise _erro("cada resultado de uma consulta e um vault.",
                        nota='ex.: {"id": "1", "titulo": "Cafe", '
                             '"texto": "R$ 6,50"}')
        if "type" in item or "input_message_content" in item:
            return dict(item)
        texto = str(item.get("texto", item.get("titulo", "")))
        pronto = {
            "type": "article",
            "id": str(item.get("id", "")),
            "title": str(item.get("titulo", "")),
            "input_message_content": {"message_text": texto},
        }
        if item.get("descricao"):
            pronto["description"] = str(item["descricao"])
        if item.get("miniatura"):
            pronto["thumbnail_url"] = str(item["miniatura"])
        return pronto

    # ── Conversa ─────────────────────────────────────────────

    def comecar_conversa(self, nome):
        return self.app.comecar_conversa(self.chat, nome, self)

    def encerrar_conversa(self):
        return self.app.encerrar_conversa(self.chat)

    def __repr__(self):
        return f"<ctx {self.tipo} chat={self.chat}>"


def _tipo_do_update(update):
    """Que especie de update e este, e qual e a mensagem dele.

    A ordem importa: `edited_message` tambem tem `message`, e trocar a
    ordem faria toda edicao ser tratada como mensagem nova — um bot
    que responde de novo cada vez que alguem corrige um typo.
    """
    for chave, tipo in (("callback_query", "callback"),
                        ("inline_query", "inline"),
                        ("edited_message", "editada"),
                        ("channel_post", "canal"),
                        ("my_chat_member", "membro_do_bot"),
                        ("chat_member", "membro"),
                        ("poll_answer", "resposta_de_enquete"),
                        ("message", "mensagem")):
        if chave in update:
            if tipo in ("callback", "inline"):
                return tipo, None
            return tipo, update[chave]
    return "desconhecido", None


def _argumentos(texto):
    """O que vem depois do comando, ja separado."""
    partes = str(texto).strip().split()
    return partes[1:] if partes and partes[0].startswith("/") else []


# ═══════════════════════════════════════════════════════════
#  Estado por chat
# ═══════════════════════════════════════════════════════════

class EmMemoria:
    """O padrao. Some quando o processo reinicia, e isso esta dito."""

    def __init__(self):
        self._dados = {}
        self._trava = threading.RLock()

    def ler(self, chat):
        with self._trava:
            return dict(self._dados.get(str(chat), {}))

    def gravar(self, chat, dados):
        with self._trava:
            self._dados[str(chat)] = dict(dados)

    def apagar(self, chat):
        with self._trava:
            self._dados.pop(str(chat), None)

    def chats(self):
        with self._trava:
            return sorted(self._dados)


class EmArquivo:
    """Um JSON por chat, numa pasta. Sobrevive ao reinicio.

    O nome do arquivo sai do id do chat, e ele e CONFERIDO: um id que
    chegasse com '../' escreveria fora da pasta. O id vem do Telegram
    e e sempre numerico, mas 'sempre' e uma suposicao sobre um sistema
    de terceiros — e e barato nao depender dela.
    """

    def __init__(self, pasta):
        self.pasta = str(pasta)
        os.makedirs(self.pasta, exist_ok=True)
        self._trava = threading.RLock()

    def _arquivo(self, chat):
        limpo = re.sub(r"[^0-9-]", "", str(chat)) or "0"
        return os.path.join(self.pasta, f"{limpo}.json")

    def ler(self, chat):
        try:
            with open(self._arquivo(chat), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def gravar(self, chat, dados):
        with self._trava:
            alvo = self._arquivo(chat)
            # Escreve ao lado e troca: um processo interrompido no meio
            # da gravacao deixaria o estado do chat pela metade, e o
            # bot leria um JSON quebrado na proxima mensagem.
            temporario = alvo + ".tmp"
            with open(temporario, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False)
            os.replace(temporario, alvo)

    def apagar(self, chat):
        try:
            os.remove(self._arquivo(chat))
        except OSError:
            pass

    def chats(self):
        try:
            return sorted(n[:-5] for n in os.listdir(self.pasta)
                          if n.endswith(".json"))
        except OSError:
            return []


def estado_em_memoria():
    return EmMemoria()


def estado_em_arquivo(pasta=".telegram/estado"):
    return EmArquivo(pasta)


# ═══════════════════════════════════════════════════════════
#  Limite de ritmo
# ═══════════════════════════════════════════════════════════

class Limitador:
    """Segura o ritmo de envio. O Telegram corta acima de ~30 por segundo.

    E por chat tambem: num grupo o limite e de cerca de 20 por minuto,
    e estourar isso rende 429 com espera longa. Segurar aqui custa
    milissegundos; ser bloqueado custa minutos.
    """

    def __init__(self, por_segundo=25.0, por_chat_por_minuto=18):
        self.intervalo = 1.0 / max(0.1, float(por_segundo))
        self.por_chat = int(por_chat_por_minuto)
        self._ultimo = 0.0
        self._chats = {}
        self._trava = threading.RLock()

    def esperar(self, chat=None):
        with self._trava:
            agora = time.monotonic()
            falta = self.intervalo - (agora - self._ultimo)
            if falta > 0:
                time.sleep(falta)
                agora = time.monotonic()
            self._ultimo = agora

            if chat is not None and self.por_chat > 0:
                marcas = [t for t in self._chats.get(str(chat), [])
                          if agora - t < 60.0]
                if len(marcas) >= self.por_chat:
                    time.sleep(max(0.0, 60.0 - (agora - marcas[0])))
                    marcas = marcas[1:]
                marcas.append(time.monotonic())
                self._chats[str(chat)] = marcas


def limitar(por_segundo=25.0, por_chat_por_minuto=18):
    return Limitador(por_segundo, por_chat_por_minuto)


# ═══════════════════════════════════════════════════════════
#  A aplicacao
# ═══════════════════════════════════════════════════════════

class Aplicacao:
    """O bot como programa: tratadores, despacho e o laco.

    Uma por processo na pratica, mas nada impede duas — e e isso que
    torna cada teste independente do anterior.
    """

    def __init__(self, token, estado=None, limitador=None, raiz=None):
        self.bot = T.Bot(token, raiz=raiz) if not isinstance(token, T.Bot) \
            else token
        self.rotas = []
        self.antes = []
        self.depois = []
        self.tratador_de_erro = None
        self.conversas = {}
        self.armazem = estado or EmMemoria()
        self.limitador = limitador
        self._parar = threading.Event()
        self._offset = 0
        self._trava = threading.RLock()
        self.metricas = {"updates": 0, "tratados": 0, "erros": 0,
                         "ignorados": 0, "inicio": time.time()}
        #: comando -> a linha de ajuda dele. Vira o menu do Telegram.
        #: Por INSTANCIA: um dicionario de classe faria dois bots no
        #: mesmo processo dividirem o menu, e o segundo herdaria os
        #: comandos do primeiro.
        self.ajudas = {}
        self.falhas = []

    # ── Registro ─────────────────────────────────────────────

    def registrar(self, tipo, teste, acao, nome=""):
        # Uma rota registrada DEPOIS de um 'qualquer' nunca e alcancada:
        # o despacho para no primeiro que casa, e o 'qualquer' casa com
        # tudo. Isso nao da erro em lugar nenhum — o bot simplesmente
        # responde "nao entendi" a um comando que existe, e quem
        # escreveu vai procurar o defeito no tratador certo.
        #
        # E a mesma classe do 'point' inalcancavel, que o 'check' acusa
        # na linguagem. Aqui o registro acontece na partida, entao falhar
        # nele e falhar antes de qualquer pessoa conversar com o bot.
        curinga = next((r for r in self.rotas if r["tipo"] == "qualquer"),
                       None)
        if curinga is not None and tipo != "qualquer":
            raise _erro(
                f"a rota '{nome or tipo}' nunca seria alcancada.",
                nota="'qualquer' ja foi registrada, e ela casa com tudo: o "
                     "despacho para no primeiro tratador que casa",
                dica="registre 'qualquer' por ULTIMO — ela e o ultimo recurso")
        self.rotas.append({"tipo": tipo, "teste": teste, "acao": acao,
                           "nome": nome or getattr(acao, "name", "")
                           or getattr(acao, "__name__", "")})
        return acao

    def comando(self, nome, acao=None, ajuda=""):
        """`/start`, `/ajuda`. Tambem serve de decorador.

        O comando casa com `/nome`, com `/nome argumento` e com
        `/nome@meubot` — a ultima forma e a que o Telegram usa em
        grupo, e um bot que nao a trata parece mudo la dentro.
        """
        nomes = [str(n).lstrip("/").lower()
                 for n in (nome if isinstance(nome, (list, tuple)) else [nome])]

        def casa(ctx):
            if ctx.tipo != "mensagem" or not ctx.texto.startswith("/"):
                return False
            primeiro = ctx.texto.split()[0][1:].lower()
            return primeiro.split("@")[0] in nomes

        def registrar(alvo):
            rota = self.registrar("comando", casa, alvo, nomes[0])
            if ajuda:
                self.ajudas[nomes[0]] = str(ajuda)
            return rota

        return registrar if acao is None else registrar(acao)

    def texto(self, padrao="", acao=None):
        """Casa o texto de uma mensagem. `padrao` e regex, ou vazio para tudo."""
        regex = re.compile(str(padrao), re.I) if padrao else None

        def casa(ctx):
            if ctx.tipo != "mensagem" or not ctx.texto:
                return False
            if ctx.texto.startswith("/"):
                return False
            return regex.search(ctx.texto) if regex else True

        def registrar(alvo):
            return self.registrar("texto", casa, alvo, str(padrao))

        return registrar if acao is None else registrar(acao)

    def botao(self, padrao="", acao=None):
        """Casa o `dados` de um botao embutido."""
        regex = re.compile(str(padrao)) if padrao else None

        def casa(ctx):
            if ctx.tipo != "callback":
                return False
            return regex.search(ctx.dados) if regex else True

        def registrar(alvo):
            return self.registrar("botao", casa, alvo, str(padrao))

        return registrar if acao is None else registrar(acao)

    def inline(self, acao=None):
        def casa(ctx):
            return ctx.tipo == "inline"

        def registrar(alvo):
            return self.registrar("inline", casa, alvo, "inline")

        return registrar if acao is None else registrar(acao)

    def midia(self, especie="foto", acao=None):
        """Casa foto, documento, voz, video, audio, adesivo, local ou contato."""
        campos = {"foto": "photo", "documento": "document", "voz": "voice",
                  "video": "video", "audio": "audio", "adesivo": "sticker",
                  "local": "location", "contato": "contact",
                  "animacao": "animation", "enquete": "poll"}
        campo = campos.get(str(especie))
        if campo is None:
            raise _erro(
                f"'{especie}' nao e uma especie de midia que eu conheca.",
                nota="as especies: " + ", ".join(sorted(campos)))

        def casa(ctx):
            return ctx.tipo == "mensagem" and campo in (ctx.mensagem or {})

        def registrar(alvo):
            return self.registrar("midia", casa, alvo, str(especie))

        return registrar if acao is None else registrar(acao)

    def entrou(self, acao=None):
        """Alguem entrou no grupo."""
        def casa(ctx):
            return ctx.tipo == "mensagem" and \
                "new_chat_members" in (ctx.mensagem or {})

        def registrar(alvo):
            return self.registrar("entrou", casa, alvo, "entrou")

        return registrar if acao is None else registrar(acao)

    def saiu(self, acao=None):
        def casa(ctx):
            return ctx.tipo == "mensagem" and \
                "left_chat_member" in (ctx.mensagem or {})

        def registrar(alvo):
            return self.registrar("saiu", casa, alvo, "saiu")

        return registrar if acao is None else registrar(acao)

    def qualquer(self, acao=None):
        """O ultimo recurso. Registre por ultimo, ou ele engole o resto."""
        def registrar(alvo):
            return self.registrar("qualquer", lambda ctx: True, alvo,
                                  "qualquer")

        return registrar if acao is None else registrar(acao)

    def ao_falhar(self, acao=None):
        def registrar(alvo):
            self.tratador_de_erro = alvo
            return alvo

        return registrar if acao is None else registrar(acao)

    def antes_de_cada(self, acao=None):
        """Roda antes do tratador. Devolver `no` interrompe o update."""
        def registrar(alvo):
            self.antes.append(alvo)
            return alvo

        return registrar if acao is None else registrar(acao)

    def depois_de_cada(self, acao=None):
        def registrar(alvo):
            self.depois.append(alvo)
            return alvo

        return registrar if acao is None else registrar(acao)

    # ── Conversa ─────────────────────────────────────────────

    def conversa(self, nome, passos):
        """Uma maquina de estados por chat.

            app.conversa("cadastro", [
                {"pergunta": "Qual seu nome?", "guarda": "nome"},
                {"pergunta": "E o e-mail?", "guarda": "email",
                 "valida": e_email, "erro": "Esse e-mail nao parece valido."}])

        Cada passo pergunta, espera a resposta, valida e guarda. O
        estado fica no chat, entao duas pessoas conversando ao mesmo
        tempo nao se atrapalham — que e o defeito que um dicionario
        solto de 'passo atual' sempre tem.
        """
        limpos = []
        for passo in (passos or []):
            if not isinstance(passo, dict):
                raise _erro("cada passo de uma conversa e um vault.",
                            nota='ex.: {"pergunta": "Nome?", "guarda": "nome"}')
            limpos.append({
                "pergunta": str(passo.get("pergunta", "")),
                "guarda": str(passo.get("guarda", "")),
                "valida": passo.get("valida"),
                "erro": str(passo.get("erro", "Valor invalido, tente de novo.")),
                "teclado": passo.get("teclado"),
            })
        self.conversas[str(nome)] = {"passos": limpos,
                                     "ao_fim": None, "nome": str(nome)}
        return _Conversa(self, str(nome))

    def comecar_conversa(self, chat, nome, ctx=None):
        fluxo = self.conversas.get(str(nome))
        if fluxo is None:
            raise _erro(f"nao ha conversa chamada '{nome}'.",
                        nota="as registradas: " +
                             (", ".join(sorted(self.conversas)) or "nenhuma"))
        self.guardar(chat, "__conversa__", {"nome": str(nome), "passo": 0,
                                            "respostas": {}})
        primeiro = fluxo["passos"][0]
        alvo = ctx.bot if ctx else self.bot
        return alvo.enviar(chat, primeiro["pergunta"],
                           teclado=primeiro.get("teclado"))

    def encerrar_conversa(self, chat):
        self.esquecer(chat, "__conversa__")

    def _em_conversa(self, ctx):
        """Se este chat esta no meio de uma conversa, conduz o proximo passo."""
        aberta = self.estado_de(ctx.chat).get("__conversa__")
        if not aberta or ctx.tipo != "mensagem":
            return False
        # Um comando SEMPRE escapa da conversa. Sem isso, quem se perde
        # no meio de um cadastro nao consegue nem mandar /cancelar — e a
        # unica saida vira bloquear o bot.
        if ctx.texto.startswith("/"):
            self.encerrar_conversa(ctx.chat)
            return False

        fluxo = self.conversas.get(aberta["nome"])
        if fluxo is None:
            self.encerrar_conversa(ctx.chat)
            return False

        passo = fluxo["passos"][aberta["passo"]]
        valida = passo.get("valida")
        if callable(valida):
            try:
                bom = valida(ctx.texto)
            except Exception:                                # noqa: BLE001
                bom = False
            if bom is False:
                ctx.responder(passo["erro"])
                return True

        aberta["respostas"][passo["guarda"] or f"passo{aberta['passo']}"] = \
            ctx.texto
        aberta["passo"] += 1

        if aberta["passo"] >= len(fluxo["passos"]):
            self.encerrar_conversa(ctx.chat)
            if callable(fluxo.get("ao_fim")):
                fluxo["ao_fim"](ctx, aberta["respostas"])
            return True

        self.guardar(ctx.chat, "__conversa__", aberta)
        seguinte = fluxo["passos"][aberta["passo"]]
        ctx.responder(seguinte["pergunta"], teclado=seguinte.get("teclado"))
        return True

    # ── Estado ───────────────────────────────────────────────

    def estado_de(self, chat):
        return self.armazem.ler(chat)

    def guardar(self, chat, chave, valor):
        dados = self.armazem.ler(chat)
        dados[str(chave)] = valor
        self.armazem.gravar(chat, dados)
        return valor

    def esquecer(self, chat, chave=None):
        if chave is None:
            self.armazem.apagar(chat)
            return True
        dados = self.armazem.ler(chat)
        dados.pop(str(chave), None)
        self.armazem.gravar(chat, dados)
        return True

    def chats(self):
        return self.armazem.chats()

    # ── Despacho ─────────────────────────────────────────────

    def atender(self, update):
        """Trata UM update. E o mesmo caminho do polling e do webhook.

        Ter um caminho so nao e elegancia: um bot testado em polling
        que quebra ao virar webhook quebra exatamente quando vai para
        producao.
        """
        with self._trava:
            self.metricas["updates"] += 1
        ctx = Contexto(self, update)

        try:
            for meio in self.antes:
                if meio(ctx) is False:
                    with self._trava:
                        self.metricas["ignorados"] += 1
                    return ctx

            if self._em_conversa(ctx):
                with self._trava:
                    self.metricas["tratados"] += 1
                return ctx

            for rota in self.rotas:
                if not rota["teste"](ctx):
                    continue
                if self.limitador is not None:
                    self.limitador.esperar(ctx.chat)
                rota["acao"](ctx)
                with self._trava:
                    self.metricas["tratados"] += 1
                break
            else:
                with self._trava:
                    self.metricas["ignorados"] += 1

            for meio in self.depois:
                meio(ctx)
        except Exception as erro:                            # noqa: BLE001
            self._anotar(ctx, erro)
        return ctx

    def _anotar(self, ctx, erro):
        with self._trava:
            self.metricas["erros"] += 1
        mensagem = (getattr(erro, "message", None) or str(erro)
                    or type(erro).__name__)
        self.falhas.append({"mensagem": mensagem, "chat": ctx.chat,
                            "tipo": ctx.tipo,
                            "detalhe": traceback.format_exc()[-1500:]})
        del self.falhas[:-50]
        if self.tratador_de_erro is not None:
            try:
                self.tratador_de_erro(ctx, erro)
                return
            except Exception:                                # noqa: BLE001
                # Um tratador de erro que tambem falha nao pode entrar
                # em laco: aqui a linha para, e o bot segue vivo.
                pass
        print(f"  [telegram:erro] {mensagem}")

    # ── O laco ───────────────────────────────────────────────

    def rodar(self, espera=None, tipos=None, silencioso=False):
        """Long polling ate alguem parar. E o modo de desenvolvimento.

        Em producao, `webhook` custa menos e responde mais rapido — mas
        exige HTTPS com certificado valido, o que em desenvolvimento e
        atrito puro.
        """
        eu = self.bot.eu()
        if not silencioso:
            print(f"  bot @{eu.get('username')} no ar — Ctrl+C para parar")
        # Um webhook ativo faz o `getUpdates` responder 409 para sempre.
        # Desligar antes e o conserto que todo mundo descobre depois de
        # meia hora lendo o erro errado.
        try:
            info = self.bot.info_do_webhook()
            if info.get("url"):
                self.bot.sem_webhook()
                if not silencioso:
                    print("  (webhook desligado: ele e o polling nao convivem)")
        except Exception:                                    # noqa: BLE001
            pass

        self._parar.clear()
        while not self._parar.is_set():
            try:
                lote = self.bot.updates(
                    self._offset,
                    espera if espera is not None else T.ESPERA_LONGA, tipos)
            except Exception as erro:                        # noqa: BLE001
                if self._parar.is_set():
                    break
                print(f"  [telegram] sem resposta: {erro}")
                self._parar.wait(3.0)
                continue
            for update in lote:
                if self._parar.is_set():
                    break
                self.atender(update)
                # O offset avanca DEPOIS de tratar: avancar antes perde
                # a mensagem quando o processo cai no meio — e e no
                # meio que ele cai.
                self._offset = int(update.get("update_id", 0)) + 1
        if not silencioso:
            print("  bot parado.")
        return self.metricas

    def parar(self):
        self._parar.set()

    # ── Webhook ──────────────────────────────────────────────

    def montar(self, caminho="/telegram", segredo=""):
        """Um app Kiln que recebe os updates. Para producao.

        O `segredo` e conferido no cabecalho: sem ele, qualquer um que
        descubra a URL manda updates falsos para o seu bot — e a URL
        vaza em log de proxy, em print de tela, em qualquer lugar.
        """
        from .kiln import ArcaneKiln as K

        app = K._forge("telegram")
        esperado = str(segredo or "")

        def receber(req):
            if esperado:
                veio = (req.get("headers") or {}).get(
                    "x-telegram-bot-api-secret-token", "")
                if veio != esperado:
                    return {"__kiln__": True, "status": 403, "headers": {},
                            "body": {"erro": "segredo invalido"},
                            "content_type": "application/json", "cookies": []}
            corpo = req.get("body")
            if isinstance(corpo, dict):
                self.atender(corpo)
            # O Telegram REENVIA o update quando a resposta demora ou
            # falha. Responder 200 sempre, e rapido, e o que impede o
            # mesmo comando de rodar tres vezes.
            return {"__kiln__": True, "status": 200, "headers": {},
                    "body": {"ok": True},
                    "content_type": "application/json", "cookies": []}

        K._post(app, str(caminho), receber)
        K._get(app, str(caminho) + "/saude",
               lambda req: {"ok": True, "metricas": self.metricas})
        return app

    def publicar(self, url, porta=8443, host="0.0.0.0", caminho="/telegram",
                 segredo="", subir=True):
        """Registra o webhook e sobe o servidor. E o 'deploy' do bot.

        `url` e o endereco PUBLICO e HTTPS — o Telegram nao aceita
        HTTP, e nao aceita certificado que ele nao consiga validar.
        Atras de um nginx ou de um tunel, `porta` e a local.
        """
        if not str(url).startswith("https://"):
            raise _erro(
                "o Telegram so aceita webhook em HTTPS.",
                nota="ele recusa HTTP e certificado invalido, sem excecao",
                dica="ponha um nginx ou Caddy na frente, ou use um tunel "
                     "(cloudflared, ngrok) durante o desenvolvimento")
        alvo = str(url).rstrip("/") + str(caminho)
        self.bot.webhook(alvo, segredo=segredo)
        if not subir:
            return alvo
        from .kiln import ArcaneKiln as K
        app = self.montar(caminho, segredo)
        print(f"  webhook registrado em {alvo}")
        K._listen(app, porta, host)
        return alvo

    # ── Operacao ─────────────────────────────────────────────

    def publicar_comandos(self):
        """Manda ao Telegram o menu de comandos, montado dos registros.

        Sem isso, quem abre o bot nao descobre o que ele faz: a lista
        de '/' vem vazia, e um bot sem menu parece quebrado.
        """
        lista = {}
        for rota in self.rotas:
            if rota["tipo"] != "comando":
                continue
            lista[rota["nome"]] = self.ajudas.get(
                rota["nome"], rota["nome"].capitalize())
        if not lista:
            return {}
        self.bot.comandos(lista)
        return lista

    def saude(self):
        return {"ok": not self.falhas,
                "no_ar_ha": round(time.time() - self.metricas["inicio"], 1),
                **self.metricas, "rotas": len(self.rotas),
                "ultimas_falhas": [f["mensagem"] for f in self.falhas[-3:]]}

    def __repr__(self):
        return f"<app telegram, {len(self.rotas)} rota(s)>"


class _Conversa:
    """O que `app.conversa(...)` devolve, so para ligar o fim."""

    __slots__ = ("_app", "_nome")

    def __init__(self, app, nome):
        self._app = app
        self._nome = nome

    def ao_terminar(self, acao=None):
        """A acao que recebe `(ctx, respostas)` quando o ultimo passo cai."""
        def registrar(alvo):
            self._app.conversas[self._nome]["ao_fim"] = alvo
            return alvo

        return registrar if acao is None else registrar(acao)

    def comecar(self, ctx):
        return self._app.comecar_conversa(ctx.chat, self._nome, ctx)


def app(token, estado=None, limitador=None, raiz=None):
    return Aplicacao(token, estado, limitador, raiz)


# ═══════════════════════════════════════════════════════════
#  Testar sem token e sem rede
# ═══════════════════════════════════════════════════════════

class BotFalso:
    """Um bot que nao fala com ninguem e anota tudo o que mandaria.

    Ele e o que torna um bot testavel. A alternativa — conversar com o
    bot no celular — nao e teste: nao roda no CI, nao repete, e nao
    diz o que quebrou.
    """

    def __init__(self, respostas=None):
        self.enviadas = []
        self.chamadas = []
        self.respostas = dict(respostas or {})
        self.token = "0:teste"

    def _anotar(self, metodo, **campos):
        registro = {"metodo": metodo, **campos}
        self.chamadas.append(registro)
        if metodo in ("sendMessage", "sendPhoto", "sendDocument",
                      "editMessageText"):
            self.enviadas.append(registro)
        return self.respostas.get(metodo, {"message_id": len(self.chamadas),
                                           "chat": {"id": campos.get("chat")},
                                           "text": campos.get("texto", "")})

    def eu(self):
        return {"id": 0, "username": "bot_de_teste", "first_name": "Teste"}

    def chamar(self, metodo, params=None, arquivos=None, prazo=None):
        return self._anotar(metodo, params=params or {})

    def enviar(self, chat, texto, **opcoes):
        return self._anotar("sendMessage", chat=chat, texto=str(texto),
                            opcoes=opcoes)

    def foto(self, chat, foto, legenda="", **opcoes):
        return self._anotar("sendPhoto", chat=chat, texto=str(legenda),
                            arquivo=foto, opcoes=opcoes)

    def documento(self, chat, arquivo, legenda="", **opcoes):
        return self._anotar("sendDocument", chat=chat, texto=str(legenda),
                            arquivo=arquivo, opcoes=opcoes)

    def editar(self, chat, id_mensagem, texto, **opcoes):
        return self._anotar("editMessageText", chat=chat, texto=str(texto),
                            mensagem=id_mensagem, opcoes=opcoes)

    def apagar(self, chat, id_mensagem):
        return self._anotar("deleteMessage", chat=chat, mensagem=id_mensagem)

    def acao(self, chat, tipo="typing"):
        return self._anotar("sendChatAction", chat=chat, acao=tipo)

    def responder_botao(self, id_callback, texto="", alerta=False, url=""):
        return self._anotar("answerCallbackQuery", texto=str(texto),
                            alerta=alerta)

    # As assinaturas espelham as do 'Bot' de verdade, e nao '**kw'.
    # Um '**kw' aceita argumento por NOME e recusa por POSICAO: a
    # chamada posicional funcionava em producao e estourava no teste,
    # com uma mensagem sobre "argumentos demais" que nao fala do que
    # realmente diverge. Um duble mais estreito que o original e pior
    # que nenhum duble — ele aprova o que quebra, ou reprova o que
    # funciona.
    def responder_inline(self, id_consulta, resultados, cache=300,
                         pessoal=False, proxima=""):
        return self._anotar("answerInlineQuery", resultados=list(resultados))

    def e_admin(self, chat, usuario):
        return bool(self.respostas.get("e_admin", False))

    def comandos(self, lista, escopo=None, idioma=""):
        return self._anotar("setMyCommands", lista=lista)

    def info_do_webhook(self):
        return {"url": ""}

    def sem_webhook(self, descartar=False):
        return True

    def __getattr__(self, nome):
        # Qualquer metodo que este dublê nao conheca vira uma anotacao,
        # em vez de um AttributeError no meio do teste. Um dublê que
        # precisa acompanhar cada metodo novo do cliente envelhece no
        # primeiro recurso acrescentado.
        def qualquer(*args, **kwargs):
            return self._anotar(nome, args=args, kwargs=kwargs)
        return qualquer


class Sonda:
    """Um bot rodando em memoria. Injeta updates e le o que ele mandou."""

    def __init__(self, aplicacao, chat=1001, usuario=None):
        self.app = aplicacao
        self.chat = chat
        self.usuario = usuario or {"id": 42, "first_name": "Ana",
                                   "username": "ana"}
        self.falso = BotFalso()
        self.app.bot = self.falso
        self._proximo = 1

    # ── Agir ─────────────────────────────────────────────────

    def mandar(self, texto):
        """Manda uma mensagem de texto, como uma pessoa faria."""
        return self._update({"message": self._mensagem(texto)})

    def comando(self, nome, *args):
        linha = "/" + str(nome).lstrip("/")
        if args:
            linha += " " + " ".join(str(a) for a in args)
        return self.mandar(linha)

    def clicar(self, dados, id_mensagem=1):
        """Clica num botao embutido."""
        return self._update({"callback_query": {
            "id": str(self._proximo), "from": self.usuario,
            "data": str(dados),
            "message": {"message_id": id_mensagem,
                        "chat": {"id": self.chat, "type": "private"}}}})

    def enviar_foto(self, file_id="foto123", legenda=""):
        mensagem = self._mensagem(legenda)
        mensagem["photo"] = [{"file_id": str(file_id), "width": 90,
                              "height": 90}]
        return self._update({"message": mensagem})

    def enviar_documento(self, nome="a.pdf", file_id="doc123"):
        mensagem = self._mensagem("")
        mensagem["document"] = {"file_id": str(file_id), "file_name": nome}
        return self._update({"message": mensagem})

    def consultar(self, texto):
        """Uma consulta inline."""
        return self._update({"inline_query": {
            "id": str(self._proximo), "from": self.usuario,
            "query": str(texto), "offset": ""}})

    def entrar(self, quem=None):
        mensagem = self._mensagem("")
        mensagem["new_chat_members"] = [quem or self.usuario]
        return self._update({"message": mensagem})

    def _mensagem(self, texto):
        return {"message_id": self._proximo, "from": self.usuario,
                "chat": {"id": self.chat, "type": "private"},
                "date": int(time.time()), "text": str(texto)}

    def _update(self, corpo):
        corpo["update_id"] = self._proximo
        self._proximo += 1
        return self.app.atender(corpo)

    # ── Perguntar ────────────────────────────────────────────

    def respostas(self):
        """Tudo o que o bot mandou, como texto."""
        return [c.get("texto", "") for c in self.falso.enviadas]

    def ultima(self):
        enviadas = self.falso.enviadas
        return enviadas[-1].get("texto", "") if enviadas else None

    def ultimo_teclado(self):
        for registro in reversed(self.falso.enviadas):
            teclado = (registro.get("opcoes") or {}).get("teclado")
            if teclado:
                return teclado
        return None

    def chamadas(self, metodo=""):
        if not metodo:
            return list(self.falso.chamadas)
        return [c for c in self.falso.chamadas if c["metodo"] == metodo]

    def quantas(self, metodo=""):
        return len(self.chamadas(metodo))

    def falhou(self):
        return bool(self.app.falhas)

    def falhas(self):
        return [f["mensagem"] for f in self.app.falhas]

    def estado(self, chave=None, padrao=None):
        dados = self.app.estado_de(self.chat)
        return dados if chave is None else dados.get(str(chave), padrao)

    def disse(self, trecho):
        """`yes` quando alguma resposta contem esse trecho."""
        return any(str(trecho) in r for r in self.respostas())


def testar(aplicacao, chat=1001, usuario=None):
    """Prepara uma sonda: um bot em memoria, sem token e sem rede."""
    return Sonda(aplicacao, chat, usuario)
