# -*- coding: utf-8 -*-
"""
O adaptador de depuração — o protocolo que o VS Code fala.

    dataforge dap

Ele não é um depurador novo. `depurador.py` já decide **quando parar**,
e essa é a parte difícil: distinguir "entrar na ação" de "passar por
cima dela" exige saber a profundidade de chamada no instante em que o
comando foi dado. Aqui só se troca a interface — em vez de `input()` no
terminal, mensagens JSON no stdio.

─── O que o DAP pede, e de onde vem ───────────────────────

| O painel mostra | Vem de |
|---|---|
| a seta na margem | o evento `stopped` que `_parar` manda |
| a pilha de chamadas | `interp._call_stack`, mais a linha de agora |
| o painel de variáveis | a cadeia de escopos do quadro escolhido |
| avaliar no console | `interp.evaluate` **no quadro escolhido** |
| entrar / passar / sair | os três modos que o depurador já tinha |

─── Duas threads, e por quê ───────────────────────────────

O programa roda numa thread, e o laço que lê o stdio fica na principal.
Sem essa separação não haveria como atender `pause` nem `disconnect`
enquanto o programa corre — e um depurador que só responde quando já
está parado não serve para um laço infinito, que é justamente quando se
quer parar.

Quando o depurador para, a thread do programa **bloqueia** num
`threading.Event`. É o que faz o tempo do programa parar de verdade: um
`sleep` em laço consumiria CPU e deixaria o interpretador andar.

─── A foto é tirada na thread do programa ─────────────────

`interp._call_stack` e a profundidade de chamada são **por thread** — e
têm de ser, senão duas ações `async` somariam a pilha uma da outra. Mas
o laço do DAP roda na thread principal, e ler a pilha de lá devolve a
da thread errada: **vazia**.

O sintoma foi exato e enganoso: a parada disparava na linha certa,
dentro de uma ação, e o painel mostrava um quadro só chamado
"(programa)". Por isso `_parar` tira a foto da pilha no instante em que
para, na thread que está executando, e o laço responde `stackTrace` com
ela.

─── Por que o env não vem do quadro ───────────────────────

`Frame` carrega nome, linha e arquivo, e **não** o escopo: acrescentar
um campo custaria uma atribuição em toda chamada de toda ação, em todo
programa, para servir a depuração. Em vez disso, este arquivo mantém o
próprio mapa `profundidade → escopo`, alimentado pela sombra de
`execute` que ele já instala. Custa zero para quem não depura.

─── Sem dependência ───────────────────────────────────────

O DAP é JSON com um cabeçalho `Content-Length`. `json` e `sys` bastam;
não há biblioteca de DAP para o Python na stdlib, e a que existe no
PyPI traria dependência para um projeto que não tem nenhuma.
"""

import json
import os
import sys
import threading
import traceback

from .depurador import CONTINUAR, PASSO, PROXIMO, SAIR_DO_QUADRO, Depurador
from .errors import ControlSignal, DataForgeError

#: O limite de itens que um vault ou cluster mostra expandido. Um frame
#: de um milhão de linhas travaria o painel do editor, e ninguém lê um
#: milhão de linhas num painel.
TETO_DE_FILHOS = 500

#: Profundidade máxima da cadeia de escopos mostrada. Um escopo por
#: bloco aninhado, e doze é mais do que qualquer código legível tem.
TETO_DE_ESCOPOS = 12


class Canal:
    """O stdio, falando DAP.

    Escrever é protegido por trava porque os eventos saem da thread do
    programa (`stopped`, `output`) e as respostas saem da thread do
    laço. Duas mensagens intercaladas no meio do cabeçalho deixariam o
    editor sem saber onde uma acaba — e o sintoma seria a sessão
    morrendo sem erro.
    """

    def __init__(self, entrada=None, saida=None):
        self.entrada = entrada or sys.stdin.buffer
        self.saida = saida or sys.stdout.buffer
        self._trava = threading.Lock()
        self._sequencia = 0

    def ler(self):
        """A próxima mensagem, ou `None` quando o editor fechou."""
        tamanho = None
        while True:
            linha = self.entrada.readline()
            if not linha:
                return None
            linha = linha.strip()
            if not linha:
                break
            if linha.lower().startswith(b"content-length:"):
                try:
                    tamanho = int(linha.split(b":", 1)[1])
                except ValueError:
                    return None
        if not tamanho:
            return None
        corpo = b""
        while len(corpo) < tamanho:
            pedaco = self.entrada.read(tamanho - len(corpo))
            if not pedaco:
                return None
            corpo += pedaco
        try:
            return json.loads(corpo.decode("utf-8"))
        except ValueError:
            return None

    def escrever(self, mensagem):
        with self._trava:
            self._sequencia += 1
            mensagem["seq"] = self._sequencia
            bruto = json.dumps(mensagem).encode("utf-8")
            self.saida.write(b"Content-Length: %d\r\n\r\n" % len(bruto))
            self.saida.write(bruto)
            self.saida.flush()

    def responder(self, pedido, corpo=None, sucesso=True, mensagem=""):
        resposta = {
            "type": "response",
            "request_seq": pedido.get("seq", 0),
            "success": sucesso,
            "command": pedido.get("command", ""),
        }
        if corpo is not None:
            resposta["body"] = corpo
        if mensagem:
            resposta["message"] = mensagem
        self.escrever(resposta)

    def evento(self, nome, corpo=None):
        mensagem = {"type": "event", "event": nome}
        if corpo is not None:
            mensagem["body"] = corpo
        self.escrever(mensagem)


class _Referencias:
    """Os números que o DAP usa para pedir "os filhos daquilo".

    O protocolo não manda o objeto de volta: ele manda um inteiro que o
    adaptador deu antes. A tabela é limpa a cada parada — um número de
    uma parada anterior aponta para um escopo que já não existe, e
    responder com ele mostraria valores velhos como se fossem os de
    agora.
    """

    def __init__(self):
        self._por_numero = {}
        self._proximo = 1000

    def novo(self, carga):
        self._proximo += 1
        self._por_numero[self._proximo] = carga
        return self._proximo

    def obter(self, numero):
        return self._por_numero.get(numero)

    def limpar(self):
        self._por_numero.clear()


#: Os quadros de todas as threads dividem um espaço de números, porque o
#: protocolo manda de volta só o inteiro. O id é thread × FATOR +
#: profundidade — uma recursão de dez mil quadros teria de acontecer
#: para duas threads colidirem, e o teto de quadros da linguagem é mil.
FATOR_DE_QUADRO = 10_000


class _Thread:
    """O estado de parada de UMA thread do programa.

    Antes havia um só — um '_parado_em', um 'Event', um 'modo' para o
    interpretador inteiro. Com duas threads batendo em paradas, a segunda
    sobrescrevia a foto da primeira: o painel mostrava a pilha de uma e
    as variáveis da outra, e soltar uma soltava as duas.
    """

    __slots__ = ("id", "nome", "objeto", "parado_em", "pilha", "liberado",
                 "modo", "profundidade_alvo", "ultima_linha", "quadro_atual",
                 "motivo", "escopos", "pedir_pausa")

    def __init__(self, numero, objeto, modo):
        self.id = numero
        self.nome = "programa" if numero == 1 else f"thread {numero}"
        self.objeto = objeto
        self.parado_em = None           # (no, env, linha) enquanto parada
        self.pilha = []                 # a foto, tirada na thread certa
        self.liberado = threading.Event()
        self.modo = modo
        self.profundidade_alvo = None
        self.ultima_linha = None
        self.quadro_atual = None
        self.motivo = "step"
        #: profundidade de chamada -> o escopo visto nela. Ver o cabeçalho
        #: do módulo: o 'Frame' não carrega o escopo.
        self.escopos = {}
        self.pedir_pausa = False


def _por_thread(nome):
    """Um atributo do 'Depurador' que vale para a thread que o lê.

    A decisão de parar mora em 'Depurador._antes', e ela lê e escreve
    'self.modo', 'self.ultima_linha', 'self.profundidade_alvo'. Trocá-los
    por propriedades que olham a thread atual é o que deixa a decisão ser
    HERDADA em vez de copiada — duas cópias da parte mais difícil do
    depurador divergiriam na primeira correção.

    Fora de uma thread do programa (no '__init__', que roda na thread do
    protocolo), o valor vai para '_fora', e é de lá que a primeira thread
    do programa herda o modo inicial.
    """
    def ler(self):
        estado = self._threads.get(threading.get_ident())
        if estado is not None:
            return getattr(estado, nome)
        return self._fora.get(nome)

    def escrever(self, valor):
        estado = self._threads.get(threading.get_ident())
        if estado is not None:
            setattr(estado, nome, valor)
        else:
            self._fora[nome] = valor

    return property(ler, escrever)


class DepuradorDAP(Depurador):
    """O depurador com a interface trocada, e uma parada por thread.

    Ele herda a decisão de parar — que é a parte que custou — e substitui
    `_parar`: em vez de um laço de `input()`, um evento e uma espera, na
    thread que parou. As outras seguem rodando.
    """

    modo = _por_thread("modo")
    profundidade_alvo = _por_thread("profundidade_alvo")
    ultima_linha = _por_thread("ultima_linha")
    quadro_atual = _por_thread("quadro_atual")
    motivo = _por_thread("motivo")

    def __init__(self, canal, interpretador, arquivo, fonte, paradas=(),
                 parar_na_entrada=False):
        self._threads = {}              # ident do Python -> _Thread
        self._fora = {}
        self._proximo_id = 1
        self._trava_estado = threading.RLock()
        super().__init__(interpretador, arquivo, fonte, paradas)
        self.canal = canal
        self.caminho = os.path.abspath(arquivo)
        # Vai para '_fora': é o modo com que a PRIMEIRA thread do programa
        # nasce. As que nascem depois começam correndo — parar cada thread
        # nova na primeira instrução seria um 'stopOnEntry' que ninguém
        # pediu, uma vez por 'parallel'.
        self.modo = PASSO if parar_na_entrada else CONTINUAR
        self.refs = _Referencias()
        self._encerrar = False

    # ── as threads ──────────────────────────────────────────

    def _registrar_thread(self):
        ident = threading.get_ident()
        estado = self._threads.get(ident)
        if estado is not None:
            return estado
        with self._trava_estado:
            numero = self._proximo_id
            self._proximo_id += 1
            modo = (self._fora.get("modo") or CONTINUAR) if numero == 1 else CONTINUAR
            estado = _Thread(numero, threading.current_thread(), modo)
            if numero > 1 and any(t.pedir_pausa for t in self._threads.values()):
                estado.pedir_pausa = True
            self._threads[ident] = estado
        if numero > 1:
            self.canal.evento("thread", {"reason": "started", "threadId": numero})
        return estado

    def _thread_por_id(self, numero):
        with self._trava_estado:
            for estado in self._threads.values():
                if estado.id == numero:
                    return estado
        return None

    def _alguma_parada(self, exceto=None):
        with self._trava_estado:
            for estado in self._threads.values():
                if estado is not exceto and estado.parado_em is not None:
                    return estado
        return None

    def threads(self):
        """As threads vivas, e o aviso das que terminaram.

        Antes era sempre uma, "programa": o depurador sombreia 'execute'
        no interpretador inteiro, e apresentar N threads sem poder
        pará-las uma a uma seria prometer o que não cumpria. Agora cada
        uma para e anda sozinha, e a lista pode dizer a verdade.
        """
        vivas, mortas = [], []
        with self._trava_estado:
            for ident, estado in list(self._threads.items()):
                if estado.id == 1 or estado.objeto.is_alive() \
                        or estado.parado_em is not None:
                    vivas.append(estado)
                else:
                    mortas.append(ident)
            for ident in mortas:
                morta = self._threads.pop(ident)
                self.canal.evento("thread", {"reason": "exited",
                                             "threadId": morta.id})
        if not vivas:
            return [{"id": 1, "name": "programa"}]
        return [{"id": t.id, "name": t.nome}
                for t in sorted(vivas, key=lambda t: t.id)]

    # ── o que o laço do DAP pergunta ────────────────────────

    @property
    def parado(self):
        return self._alguma_parada() is not None

    def quadro_parado(self, numero=None):
        estado = (self._thread_por_id(numero) if numero is not None
                  else self._alguma_parada_preferindo_a_primeira())
        return estado.parado_em if estado is not None else None

    def _alguma_parada_preferindo_a_primeira(self):
        primeira = self._thread_por_id(1)
        if primeira is not None and primeira.parado_em is not None:
            return primeira
        return self._alguma_parada()

    # ── decidir se para ─────────────────────────────────────

    def _antes(self, no, env):
        """Registra a thread, anota o escopo desta profundidade, atende `pause`."""
        estado = self._registrar_thread()
        profundidade = self._profundidade()
        anotar = estado.escopos
        anotar[profundidade] = env
        # Ao voltar de uma chamada, o que estava mais fundo morreu. Sem
        # esta limpeza, a pilha mostraria escopos de ações que já
        # retornaram.
        if len(anotar) > profundidade + 1:
            for fundo in [d for d in anotar if d > profundidade]:
                del anotar[fundo]
        if estado.id > 1 and estado.nome == f"thread {estado.id}":
            linha = getattr(no, "line", 0)
            if linha:
                estado.nome = f"thread {estado.id} (linha {linha})"

        if self._encerrar:
            raise _Encerrar()
        if estado.pedir_pausa:
            estado.pedir_pausa = False
            estado.modo = PASSO
        return super()._antes(no, env)

    # ── parar: o evento, e a espera ─────────────────────────

    def _parar(self, no, env, linha, motivo=None):
        estado = self._registrar_thread()
        razao = self.motivo if motivo is None else motivo
        descricao = None
        if razao not in ("step", "breakpoint", "pause", "entry"):
            # O texto de uma condição que não deu para avaliar. O DAP só
            # aceita razões fixas, e a explicação vai em 'description'.
            descricao, razao = razao, "breakpoint"
        with self._trava_estado:
            estado.parado_em = (no, env, linha)
            # A pilha é POR THREAD, e quem responde 'stackTrace' é a
            # thread do protocolo: lá ela está vazia. A foto tem de ser
            # tirada AQUI, na thread que está executando.
            estado.pilha = list(getattr(self.interp, "_call_stack", ()) or [])
            # As referências só são descartadas se ninguém mais estiver
            # parado: limpar aqui apagaria o painel de variáveis de uma
            # thread que a pessoa ainda está olhando.
            if self._alguma_parada(exceto=estado) is None:
                self.refs.limpar()
        estado.liberado.clear()
        corpo = {"reason": razao, "threadId": estado.id,
                 "allThreadsStopped": False, "line": linha}
        if descricao:
            corpo["description"] = descricao
            corpo["text"] = descricao
        self.canal.evento("stopped", corpo)
        # Bloquear, e não girar num 'sleep': o tempo desta thread precisa
        # parar de verdade.
        estado.liberado.wait()
        with self._trava_estado:
            estado.parado_em = None
        if self._encerrar:
            raise _Encerrar()

    def _registrar_log(self, texto, linha):
        """O logpoint vai para o console do editor, e o programa segue."""
        self.canal.evento("output", {
            "category": "console",
            "output": f"{texto}\n",
            "source": {"name": os.path.basename(self.caminho),
                       "path": self.caminho},
            "line": linha,
        })

    def seguir(self, modo, numero=None):
        """Solta UMA thread no modo pedido."""
        estado = (self._thread_por_id(numero) if numero is not None
                  else self._alguma_parada_preferindo_a_primeira())
        if estado is None:
            # Ainda não há thread do programa: o modo vale para a primeira.
            self._fora["modo"] = modo
            return
        estado.modo = modo
        if modo in (PROXIMO, SAIR_DO_QUADRO):
            # Pela mesma razão da pilha: a profundidade tem de ser a da
            # foto, e não a da thread do protocolo, que é zero.
            with self._trava_estado:
                estado.profundidade_alvo = len(estado.pilha)
        if modo == PASSO:
            # Um passo a partir da linha onde já estamos precisa poder
            # parar na MESMA linha do corpo de um laço.
            estado.ultima_linha = None
        if estado.parado_em is not None:
            self.canal.evento("continued", {"threadId": estado.id,
                                            "allThreadsContinued": False})
        estado.liberado.set()

    def pausar(self, numero=None):
        with self._trava_estado:
            alvos = ([self._thread_por_id(numero)] if numero is not None
                     else list(self._threads.values()))
            if not [a for a in alvos if a is not None]:
                # Nada rodando ainda: a primeira thread nasce em passo.
                self._fora["modo"] = PASSO
            for alvo in alvos:
                if alvo is not None:
                    alvo.pedir_pausa = True

    def encerrar(self):
        self._encerrar = True
        with self._trava_estado:
            for estado in self._threads.values():
                estado.liberado.set()

    # ── a pilha ─────────────────────────────────────────────

    def pilha(self, numero=None):
        """Os quadros de UMA thread, do mais interno para o mais externo.

        O `id` de cada um é thread × FATOR + profundidade: é o que o
        painel manda de volta em `scopes`, e o que liga o quadro ao
        escopo anotado naquela thread.
        """
        estado = (self._thread_por_id(numero) if numero is not None
                  else self._alguma_parada_preferindo_a_primeira())
        if estado is None or estado.parado_em is None:
            return []
        _, _, linha = estado.parado_em
        with self._trava_estado:
            chamadas = list(estado.pilha)
        base = estado.id * FATOR_DE_QUADRO
        # O quadro de topo é "(programa)" — nome de QUADRO, entre
        # parênteses, e não o nome da thread. Numa thread de 'parallel',
        # "(thread 2)".
        topo = "(programa)" if estado.id == 1 else f"(thread {estado.id})"

        quadros = [{
            "id": base + len(chamadas),
            "name": chamadas[-1].name if chamadas else topo,
            "line": linha,
            "column": 1,
            "source": {"name": os.path.basename(self.caminho),
                       "path": self.caminho},
        }]
        # Os de fora param na linha de onde CHAMARAM — é o que o painel
        # precisa para levar o cursor ao lugar certo ao clicar.
        for indice in range(len(chamadas) - 1, -1, -1):
            quadro = chamadas[indice]
            de_fora = chamadas[indice - 1].name if indice > 0 else topo
            quadros.append({
                "id": base + indice,
                "name": de_fora,
                "line": getattr(quadro, "line", 0),
                "column": getattr(quadro, "column", 0) or 1,
                "source": {
                    "name": os.path.basename(
                        getattr(quadro, "filename", "") or self.caminho),
                    "path": os.path.abspath(
                        getattr(quadro, "filename", "") or self.caminho),
                },
            })
        return quadros

    def escopo_do_quadro(self, id_do_quadro):
        numero, profundidade = divmod(int(id_do_quadro or 0), FATOR_DE_QUADRO)
        estado = self._thread_por_id(numero)
        if estado is None:
            return None
        return estado.escopos.get(profundidade)

    # ── variáveis ───────────────────────────────────────────

    def escopos(self, id_do_quadro):
        """Um escopo por nível da cadeia, do mais próximo ao global.

        As 228 embutidas ficam de fora: elas vivem no escopo global, e
        despejá-las enterra as três variáveis que a pessoa parou para
        ver — que é a única coisa que ela pediu.
        """
        env = self.escopo_do_quadro(id_do_quadro)
        if env is None:
            return []
        embutidas = self._nomes_embutidos()
        saida = []
        vistos = set()
        atual, nivel = env, 0
        while atual is not None and nivel < TETO_DE_ESCOPOS:
            proprias = {k: v for k, v in getattr(atual, "variables", {}).items()
                        if not k.startswith("__") and k not in vistos
                        and k not in embutidas}
            vistos.update(proprias)
            e_global = getattr(atual, "parent", None) is None
            if proprias or not saida:
                nome = getattr(atual, "name", "") or (
                    "global" if e_global else "bloco")
                saida.append({
                    "name": nome,
                    "variablesReference": self.refs.novo(("vars", proprias)),
                    # O global fica recolhido: é o maior, e é o que menos
                    # interessa quando se parou dentro de uma ação.
                    "expensive": e_global,
                })
            atual = getattr(atual, "parent", None)
            nivel += 1
        return saida

    def variaveis(self, referencia):
        carga = self.refs.obter(referencia)
        if carga is None:
            return []
        especie, alvo = carga
        if especie == "vars":
            return [self._variavel(nome, alvo[nome])
                    for nome in sorted(alvo)]
        return self._filhos(alvo)

    def _variavel(self, nome, valor):
        return {
            "name": str(nome),
            "value": self._texto(valor),
            "type": self._tipo(valor),
            "variablesReference": (self.refs.novo(("filhos", valor))
                                   if self._tem_filhos(valor) else 0),
        }

    def _tem_filhos(self, valor):
        if isinstance(valor, (dict, list, tuple, set)):
            return bool(valor)
        # Record e instância: os campos são o que se quer abrir.
        return bool(getattr(valor, "fields", None)) or bool(
            getattr(valor, "values", None))

    def _filhos(self, valor):
        if isinstance(valor, dict):
            itens = list(valor.items())[:TETO_DE_FILHOS]
            return [self._variavel(k, v) for k, v in itens]
        if isinstance(valor, (list, tuple)):
            return [self._variavel(f"[{i}]", v)
                    for i, v in enumerate(valor[:TETO_DE_FILHOS])]
        if isinstance(valor, set):
            return [self._variavel(f"[{i}]", v)
                    for i, v in enumerate(sorted(valor, key=repr)[:TETO_DE_FILHOS])]
        campos = getattr(valor, "fields", None) or getattr(valor, "values", None)
        if isinstance(campos, dict):
            return [self._variavel(k, v) for k, v in list(campos.items())[
                :TETO_DE_FILHOS]]
        return []

    def _texto(self, valor):
        try:
            texto = self.interp._to_str(valor)
        except Exception:                               # noqa: BLE001
            texto = repr(valor)
        return texto if len(texto) <= 240 else texto[:237] + "…"

    def _tipo(self, valor):
        try:
            return self.interp._type_of(valor)
        except Exception:                               # noqa: BLE001
            return type(valor).__name__

    # ── avaliar ─────────────────────────────────────────────

    def avaliar(self, expressao, id_do_quadro=None):
        """No quadro escolhido, e não no global.

        Avaliar no global mostraria o valor errado — ou nenhum —
        justamente para as variáveis locais, que são as que se quer ver
        ao parar dentro de uma ação.
        """
        from .lexer import tokenize
        from .parser import parse

        env = None
        if id_do_quadro is not None:
            env = self.escopo_do_quadro(id_do_quadro)
        if env is None:
            parado = self.quadro_parado()
            env = parado[1] if parado else self.interp.global_env

        arvore = parse(tokenize(expressao, "<dap>"), "<dap>")
        if not arvore.body:
            return None, 0
        valor = self.interp.evaluate(arvore.body[0], env)
        return (self._texto(valor),
                self.refs.novo(("filhos", valor)) if self._tem_filhos(valor)
                else 0)


def _texto_do_erro(erro):
    """A mensagem do erro, e nunca uma exceção nova.

    Isto roda DENTRO de um `except`, na thread do programa. Uma
    exceção aqui mata a thread antes de o evento sair, e o editor fica
    esperando para sempre por um `terminated` que não vem — sem erro
    visível em lugar nenhum. Foi o que aconteceu: `erro.format()` não
    aceita `color`, e o `TypeError` engoliu o programa inteiro.
    """
    try:
        formatar = getattr(erro, "format", None)
        if callable(formatar):
            return formatar()
    except Exception:                                   # noqa: BLE001
        pass
    return f"{type(erro).__name__}: {erro}"


class _Encerrar(BaseException):
    """`disconnect` no meio da execução.

    Deriva de `BaseException` pelo mesmo motivo de `halt` e `skip`: o
    interpretador embrulha toda `Exception` que sobe de dentro num
    `RuntimeError_`, e o pedido de encerrar viraria uma mensagem de erro
    no meio do programa em vez de encerrá-lo.
    """


class Sessao:
    """Um `launch`, do `initialize` ao `terminated`."""

    def __init__(self, canal=None):
        self.canal = canal or Canal()
        self.depurador = None
        self.thread = None
        self.caminho = None
        self.pedidas = {}          # arquivo -> linhas que o editor marcou
        #: arquivo -> {linha: (condicao, vezes, log)}
        self.condicoes_pedidas = {}
        self.terminou = False
        self.codigo = 0

    # ── o laço ──────────────────────────────────────────────

    def rodar(self):
        while True:
            pedido = self.canal.ler()
            if pedido is None:
                break
            if pedido.get("type") != "request":
                continue
            comando = pedido.get("command", "")
            metodo = getattr(self, f"req_{comando}", None)
            if metodo is None:
                # Responder com sucesso a um comando que não se atende
                # faria o editor esperar por um efeito que não vem.
                self.canal.responder(pedido, sucesso=False,
                                     mensagem=f"'{comando}' não é atendido")
                continue
            try:
                metodo(pedido)
            except Exception as erro:                   # noqa: BLE001
                self.canal.responder(pedido, sucesso=False,
                                     mensagem=str(erro))
                self.canal.evento("output", {
                    "category": "stderr",
                    "output": traceback.format_exc(),
                })
            if comando in ("disconnect", "terminate"):
                break
        if self.depurador is not None:
            self.depurador.encerrar()
        return 0

    # ── inicialização ───────────────────────────────────────

    def req_initialize(self, pedido):
        self.canal.responder(pedido, {
            "supportsConfigurationDoneRequest": True,
            "supportsEvaluateForHovers": True,
            "supportsSetVariable": False,
            "supportsTerminateRequest": True,
            "supportsStepBack": False,
            "supportsConditionalBreakpoints": True,
            "supportsHitConditionalBreakpoints": True,
            "supportsLogPoints": True,
            "supportsDelayedStackTraceLoading": False,
            "exceptionBreakpointFilters": [],
        })
        # 'initialized' DEPOIS da resposta: é ele que autoriza o editor
        # a mandar os breakpoints, e mandá-lo antes faz o cliente
        # descartar a configuração.
        self.canal.evento("initialized")

    def req_setBreakpoints(self, pedido):
        args = pedido.get("arguments", {})
        fonte = (args.get("source") or {}).get("path") or ""
        brutas = list(args.get("breakpoints") or [])
        if not brutas:
            brutas = [{"line": n} for n in (args.get("lines") or [])]

        executaveis = self._linhas_executaveis(fonte)
        confirmados = []
        linhas = set()
        condicoes = {}
        for bruta in brutas:
            linha = bruta.get("line", 0)
            #: Uma parada em comentário ou linha vazia nunca disparava, e
            #: o editor a mostrava acesa — o pior dos dois mundos. Aqui
            #: ela é MOVIDA para a próxima linha executável, e o painel
            #: mostra onde ela realmente ficou.
            destino = self._proxima_executavel(linha, executaveis)
            if destino is None:
                confirmados.append({
                    "verified": False,
                    "line": linha,
                    "message": "não há instrução nesta linha nem abaixo dela",
                })
                continue
            trio = (bruta.get("condition") or "", bruta.get("hitCondition") or "",
                    bruta.get("logMessage") or "")
            if any(trio):
                # Conferido AQUI, e não na primeira passagem: uma contagem
                # que não se entende tem de aparecer na margem do editor
                # como parada inválida, com o motivo, e não virar uma
                # parada que nunca dispara sem nada dizendo por quê.
                try:
                    from .depurador import Condicao
                    Condicao(*trio)
                except ValueError as erro:
                    confirmados.append({"verified": False, "line": destino,
                                        "message": str(erro)})
                    continue
                condicoes[destino] = trio
            linhas.add(destino)
            confirmados.append({"verified": True, "line": destino})

        if fonte:
            self.pedidas[os.path.abspath(fonte)] = linhas
            self.condicoes_pedidas[os.path.abspath(fonte)] = condicoes
        if self.depurador is not None:
            self._aplicar_paradas(self.depurador, linhas, condicoes)
        self.canal.responder(pedido, {"breakpoints": confirmados})

    @staticmethod
    def _aplicar_paradas(depurador, linhas, condicoes):
        """Troca as paradas de uma vez. A contagem de uma parada que já
        existia com a MESMA condição é mantida: o editor reenvia a lista
        inteira a cada clique na margem, e zerar a contagem de todas por
        causa de uma parada nova faria 'vezes >= 5' recomeçar do zero."""
        antigas = dict(depurador.condicoes)
        depurador.paradas = set(linhas)
        depurador.condicoes = {}
        for linha, (condicao, vezes, log) in condicoes.items():
            nova = depurador.definir_parada(linha, condicao, vezes, log)
            velha = antigas.get(linha)
            if velha is not None and (velha.condicao, velha.vezes, velha.log) == \
                    (nova.condicao, nova.vezes, nova.log):
                depurador.condicoes[linha] = velha

    def _linhas_executaveis(self, caminho):
        """As linhas em que faz sentido parar, tiradas do parser.

        A mesma pergunta que a cobertura faz — e a mesma resposta, pelo
        mesmo módulo. Duas definições de "linha executável" divergiriam,
        e a parada cairia onde a cobertura não conta.
        """
        if not caminho or not os.path.isfile(caminho):
            return None
        try:
            from .cobertura import linhas_executaveis
            from .lexer import tokenize
            from .parser import parse
            with open(caminho, encoding="utf-8") as f:
                fonte = f.read()
            return linhas_executaveis(parse(tokenize(fonte, caminho), caminho))
        except Exception:                               # noqa: BLE001
            # Arquivo que não compila: aceitar a linha como pedida. O
            # `launch` vai falhar com o erro de sintaxe de verdade, que é
            # a mensagem útil.
            return None

    @staticmethod
    def _proxima_executavel(linha, executaveis):
        if not executaveis:
            return linha
        if linha in executaveis:
            return linha
        adiante = [n for n in executaveis if n > linha]
        return min(adiante) if adiante else None

    def req_configurationDone(self, pedido):
        self.canal.responder(pedido)

    # ── launch ──────────────────────────────────────────────

    def req_launch(self, pedido):
        from .interpreter import Interpreter
        from .lexer import tokenize
        from .parser import parse

        args = pedido.get("arguments", {})
        caminho = args.get("program") or ""
        caminho = os.path.abspath(os.path.expanduser(caminho))
        if not os.path.isfile(caminho):
            self.canal.responder(pedido, sucesso=False,
                                 mensagem=f"não encontrei '{caminho}'")
            self.canal.evento("terminated")
            return

        try:
            with open(caminho, encoding="utf-8") as f:
                fonte = f.read()
            arvore = parse(tokenize(fonte, caminho), caminho)
        except DataForgeError as erro:
            self.canal.evento("output", {
                "category": "stderr",
                "output": _texto_do_erro(erro) + "\n"})
            self.canal.responder(pedido, sucesso=False,
                                 mensagem="o arquivo não compila")
            self.canal.evento("terminated")
            return

        self.caminho = caminho
        interpretador = Interpreter()
        interpretador.script_args = list(args.get("args") or [])

        cwd = args.get("cwd")
        if cwd and os.path.isdir(cwd):
            os.chdir(cwd)

        d = DepuradorDAP(self.canal, interpretador, caminho, fonte,
                         paradas=self.pedidas.get(caminho, set()),
                         parar_na_entrada=bool(args.get("stopOnEntry")))
        self._aplicar_paradas(d, self.pedidas.get(caminho, set()),
                              self.condicoes_pedidas.get(caminho, {}))
        self.depurador = d
        self.canal.responder(pedido)

        def correr():
            d.ligar()
            codigo = 0
            try:
                interpretador.run(arvore)
            except _Encerrar:
                codigo = 0
            except DataForgeError as erro:
                codigo = 1
                self.canal.evento("output", {
                    "category": "stderr",
                    "output": _texto_do_erro(erro) + "\n"})
            except ControlSignal:
                pass
            except BaseException as erro:               # noqa: BLE001
                codigo = 1
                self.canal.evento("output", {
                    "category": "stderr",
                    "output": f"{type(erro).__name__}: {erro}\n"})
            finally:
                d.desligar()
            self.terminou = True
            self.codigo = codigo
            self.canal.evento("exited", {"exitCode": codigo})
            self.canal.evento("terminated")

        self.thread = threading.Thread(target=correr, name="df-programa",
                                       daemon=True)
        self.thread.start()

    # ── andar ───────────────────────────────────────────────

    def _seguir(self, pedido, modo):
        if self.depurador is None:
            self.canal.responder(pedido, sucesso=False,
                                 mensagem="nada está rodando")
            return
        numero = pedido.get("arguments", {}).get("threadId")
        self.canal.responder(pedido, {"allThreadsContinued": False}
                             if modo == CONTINUAR else None)
        self.depurador.seguir(modo, numero)

    def req_continue(self, pedido):
        self._seguir(pedido, CONTINUAR)

    def req_next(self, pedido):
        self._seguir(pedido, PROXIMO)

    def req_stepIn(self, pedido):
        self._seguir(pedido, PASSO)

    def req_stepOut(self, pedido):
        self._seguir(pedido, SAIR_DO_QUADRO)

    def req_pause(self, pedido):
        if self.depurador is None:
            self.canal.responder(pedido, sucesso=False,
                                 mensagem="nada está rodando")
            return
        self.depurador.pausar(pedido.get("arguments", {}).get("threadId"))
        self.canal.responder(pedido)

    # ── olhar ───────────────────────────────────────────────

    def req_threads(self, pedido):
        lista = (self.depurador.threads() if self.depurador is not None
                 else [{"id": 1, "name": "programa"}])
        self.canal.responder(pedido, {"threads": lista})

    def req_stackTrace(self, pedido):
        if self.depurador is None:
            self.canal.responder(pedido, {"stackFrames": [], "totalFrames": 0})
            return
        quadros = self.depurador.pilha(
            pedido.get("arguments", {}).get("threadId"))
        self.canal.responder(pedido, {"stackFrames": quadros,
                                      "totalFrames": len(quadros)})

    def req_scopes(self, pedido):
        if self.depurador is None:
            self.canal.responder(pedido, {"scopes": []})
            return
        quadro = pedido.get("arguments", {}).get("frameId", 0)
        self.canal.responder(pedido,
                             {"scopes": self.depurador.escopos(quadro)})

    def req_variables(self, pedido):
        if self.depurador is None:
            self.canal.responder(pedido, {"variables": []})
            return
        ref = pedido.get("arguments", {}).get("variablesReference", 0)
        self.canal.responder(pedido,
                             {"variables": self.depurador.variaveis(ref)})

    def req_evaluate(self, pedido):
        args = pedido.get("arguments", {})
        expressao = (args.get("expression") or "").strip()
        if self.depurador is None or not expressao:
            self.canal.responder(pedido, sucesso=False,
                                 mensagem="nada para avaliar")
            return
        try:
            texto, ref = self.depurador.avaliar(expressao, args.get("frameId"))
        except DataForgeError as erro:
            self.canal.responder(pedido, sucesso=False,
                                 mensagem=getattr(erro, "message", str(erro)))
            return
        except Exception as erro:                       # noqa: BLE001
            self.canal.responder(pedido, sucesso=False, mensagem=str(erro))
            return
        self.canal.responder(pedido, {"result": texto if texto is not None
                                      else "void",
                                      "variablesReference": ref})

    # ── encerrar ────────────────────────────────────────────

    def req_disconnect(self, pedido):
        if self.depurador is not None:
            self.depurador.encerrar()
        self.canal.responder(pedido)

    def req_terminate(self, pedido):
        if self.depurador is not None:
            self.depurador.encerrar()
        self.canal.responder(pedido)
        self.canal.evento("terminated")


def servir(entrada=None, saida=None):
    """`dataforge dap` — fala DAP no stdio até o editor fechar."""
    return Sessao(Canal(entrada, saida)).rodar()
