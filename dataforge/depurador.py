# -*- coding: utf-8 -*-
"""
O depurador do DataForge.

    dataforge debug programa.df
    dataforge debug programa.df --parar=42

Ele para onde você mandar, mostra o que está valendo e deixa andar de
uma instrução por vez.

─── Custo zero quando desligado ────────────────────────────

`execute` roda uma vez por instrução — mais de um milhão de vezes num
programa de porte médio. Um `if self.depurando:` ali custaria em TODA
execução, inclusive nas que nunca vão depurar nada.

Por isso o depurador não é um campo consultado: ele SUBSTITUI o método.
Atribuir `interpretador.execute` cria um atributo de instância que
sombreia o da classe, e o interpretador não depurado continua chamando
exatamente o mesmo código de antes, sem um teste a mais.

─── Por que um depurador de terminal ───────────────────────

O protocolo que o VS Code fala (DAP) é primo do LSP e daria a interface
gráfica. Mas ele pressupõe o que este arquivo entrega — parar, andar,
listar quadros, avaliar no quadro certo. Construir a máquina primeiro, e
o protocolo depois, deixa o depurador utilizável em qualquer terminal,
inclusive por ssh, onde interface gráfica nenhuma chega.
"""

import os
import sys

from .environment import Environment
from .errors import ControlSignal, DataForgeError

#: Os modos de andar.
CONTINUAR, PASSO, PROXIMO, SAIR_DO_QUADRO = "continuar", "passo", "proximo", "sair"


def _cor(texto, codigo):
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return texto
    return f"\033[{codigo}m{texto}\033[0m"


class Condicao:
    """O que decide se uma parada dispara, além da linha.

    Três formas, combináveis, e as três com o nome que o VS Code usa:

        condicao   'x bigger 100'  — só para quando a expressão vale
        vezes      '>= 5', '% 10'  — conta as passagens pela linha
        log        'x vale {x}'    — imprime e NÃO para

    A contagem só anda quando a condição vale: "a quinta vez que x passou
    de 100" é o que se quer dizer com as duas juntas, e contar todas as
    passagens daria outra pergunta.

    Um número sozinho em 'vezes' quer dizer "a partir da N-ésima": parar
    SÓ na N-ésima e nunca mais deixaria a pessoa sem parada no resto do
    laço, que é quase sempre onde o bug está.
    """

    __slots__ = ("condicao", "vezes", "log", "contagem",
                 "_arvore", "_operador", "_alvo", "_trava")

    def __init__(self, condicao="", vezes="", log=""):
        import re
        import threading

        self.condicao = (condicao or "").strip()
        self.vezes = (vezes or "").strip()
        self.log = log or ""
        self.contagem = 0
        self._arvore = None
        self._trava = threading.Lock()
        self._operador, self._alvo = None, None
        if self.vezes:
            achado = re.fullmatch(r"(>=|>|==|%)?\s*(\d+)", self.vezes)
            if not achado:
                raise ValueError(
                    f"'{self.vezes}' não é uma contagem — use um número, "
                    f"'>= N', '> N', '== N' ou '% N'")
            self._operador = achado.group(1) or ">="
            self._alvo = int(achado.group(2))
            if self._operador == "%" and self._alvo == 0:
                raise ValueError("'% 0' nunca dispara")

    @property
    def vazia(self):
        return not (self.condicao or self.vezes or self.log)

    def _contagem_dispara(self):
        with self._trava:
            self.contagem += 1
            n = self.contagem
        if self._operador is None:
            return True
        return {">=": n >= self._alvo, ">": n > self._alvo,
                "==": n == self._alvo, "%": n % self._alvo == 0
                }[self._operador]

    def descrever(self):
        partes = []
        if self.condicao:
            partes.append(f"se {self.condicao}")
        if self.vezes:
            partes.append(f"vezes {self.vezes}")
        if self.log:
            partes.append(f"log {self.log!r}")
        return ", ".join(partes)


#: O valor de uma vigia cuja expressao ainda nao da para avaliar — a
#: variavel nao existe, o objeto e void. Nao e 'None': 'void' e um valor
#: legitimo, e confundir os dois esconderia a mudanca de void para algo.
INDISPONIVEL = ("<indisponivel>",)


def impressao(valor, _profundidade=0, _vistos=None):
    """Uma foto do valor que muda quando o valor MUDA.

    Comparar a referencia nao serve: 'xs.append(1)' muda a lista e a
    referencia continua a mesma. Comparar o texto ('_to_str') tambem nao:
    uma instancia sem '__str__' imprime '<Conta instance>' com qualquer
    saldo. A foto desce na estrutura — itens, chaves, campos —, com teto
    de profundidade e de tamanho, porque o depurador confere a vigia a
    cada instrucao, e uma lista de um milhao de itens nao pode custar um
    milhao de comparacoes por passo sem aviso.
    """
    if valor is None or isinstance(valor, (bool, int, float, str, bytes)):
        return (type(valor).__name__, valor)
    if _profundidade > 6:
        return ("fundo", id(valor))
    _vistos = set() if _vistos is None else _vistos
    if id(valor) in _vistos:
        return ("ciclo", id(valor))
    _vistos.add(id(valor))
    teto = 5000
    abaixo = _profundidade + 1
    if isinstance(valor, (list, tuple)):
        return ("L", len(valor), tuple(impressao(v, abaixo, _vistos)
                                       for v in valor[:teto]))
    if isinstance(valor, dict):
        return ("V", len(valor), tuple((repr(k), impressao(v, abaixo, _vistos))
                                       for k, v in list(valor.items())[:teto]))
    if isinstance(valor, (set, frozenset)):
        return ("S", len(valor), tuple(sorted(repr(v) for v in list(valor)[:teto])))
    campos = getattr(valor, "fields", None)
    if isinstance(campos, dict):                       # instancia de blueprint
        return ("I", id(valor), impressao(dict(campos), abaixo, _vistos))
    valores = getattr(valor, "values", None)
    if isinstance(valores, dict):                      # record
        return ("R", impressao(dict(valores), abaixo, _vistos))
    return ("O", id(valor))


def _dentro_de(env, escopo):
    """'env' e 'escopo' ou um escopo aninhado nele?"""
    while env is not None:
        if env is escopo:
            return True
        env = env.parent
    return False


class Vigia:
    """Uma expressao observada, presa ao escopo onde foi criada.

    O escopo importa: 'acc' dentro de 'somar' e outra variavel que 'acc'
    no topo. Uma vigia sem escopo olha o global.
    """

    __slots__ = ("expressao", "escopo", "arvore", "foto", "texto", "mudancas",
                 "ler", "origem")

    def __init__(self, expressao, escopo=None, arvore=None, ler=None, origem=""):
        self.expressao = expressao
        self.origem = origem      # "dap": as do editor sao trocadas em bloco
        self.escopo = escopo
        self.arvore = arvore
        self.ler = ler            # alternativa a 'arvore': o DAP le por chave
        self.foto = INDISPONIVEL
        self.texto = "(não existe)"
        self.mudancas = 0


class Depurador:
    """Para, mostra e anda.

    O estado que importa é pequeno: onde parar, como andar, e em que
    profundidade de chamada estávamos quando o comando foi dado — é ela
    que distingue 'entrar na ação' de 'passar por cima dela'.
    """

    def __init__(self, interpretador, arquivo, fonte, paradas=()):
        self.interp = interpretador
        self.arquivo = arquivo
        self.linhas = fonte.split("\n")
        self.paradas = set(paradas)
        #: linha -> Condicao. A linha continua em 'paradas' — uma parada
        #: sem condição não tem entrada aqui.
        self.condicoes = {}
        self.observadas = []           # expressões a mostrar a cada parada
        #: As vigias: param quando o valor MUDA. Conferidas depois de cada
        #: instrucao, e so enquanto houver alguma.
        self.vigias = []
        #: Por que a última parada aconteceu: 'breakpoint', 'step' ou o
        #: texto de uma condição que não deu para avaliar.
        self.motivo = "step"
        import threading as _threading
        #: Por thread: avaliar uma condição chama 'evaluate', que pode
        #: chamar 'execute' — que é a sombra. Sem esta marca, uma condição
        #: que chama uma ação com uma parada dentro pararia no meio da
        #: própria avaliação.
        self._local = _threading.local()
        self._trava_do_terminal = _threading.RLock()
        self._trava_das_vigias = _threading.RLock()
        self.modo = PASSO if not paradas else CONTINUAR
        self.profundidade_alvo = None
        self.ultima_linha = None
        self.quadro_atual = None
        self.saindo = False
        self.original = None

    # ── instalar ────────────────────────────────────────────

    def ligar(self):
        """Sombreia 'execute'. Nada muda para quem não depura."""
        # O corpo compilado das ações passa POR FORA de 'execute' — é
        # justamente assim que ele economiza o despacho. Com ele ligado,
        # a sombra abaixo veria as instruções de topo e nenhuma de
        # dentro de ação: o depurador pararia no lugar errado, ou em
        # lugar nenhum, sem nada explicando.
        self.interp.compilar_corpos = False
        self.original = self.interp.execute

        def executar(no, env):
            livre = not self.saindo and not getattr(self._local, "avaliando", False)
            if livre:
                self._antes(no, env)
            if not self.vigias:
                return self.original(no, env)
            # A vigia e conferida DEPOIS da instrucao: e ela que mudou o
            # valor, e a parada mostra a linha dela. 'yield', 'halt' e
            # 'skip' saem como sinal, e tambem podem ter mudado algo.
            try:
                resultado = self.original(no, env)
            except ControlSignal:
                if livre and self.vigias:
                    self._conferir_vigias(no, env)
                raise
            if livre and self.vigias:
                self._conferir_vigias(no, env)
            return resultado

        self.interp.execute = executar

    def desligar(self):
        """Tira a sombra — e nao poe outra no lugar.

        Reatribuir 'self.interp.execute = self.original' pareceria
        desfazer, mas cria de novo um atributo de INSTANCIA com o metodo
        ligado. O interpretador sairia da depuracao carregando uma
        indirecao que ele nao tinha antes; 'del' devolve o objeto ao
        estado exato de origem.
        """
        if self.original is not None:
            self.interp.__dict__.pop("execute", None)
            self.original = None
        self.interp.compilar_corpos = True

    # ── decidir se para ─────────────────────────────────────

    def _profundidade(self):
        return len(getattr(self.interp, "_call_stack", ()) or ())

    def _antes(self, no, env):
        linha = getattr(no, "line", 0)
        if not linha:
            return

        # Uma instrução composta ('given', 'cycle') e o corpo dela
        # compartilham a linha de abertura; parar duas vezes na mesma
        # linha faz o passo a passo parecer travado.
        if linha == self.ultima_linha and self.modo != CONTINUAR:
            return

        profundidade = self._profundidade()
        parar = False
        self.motivo = "step"

        if linha in self.paradas and self._parada_dispara(linha, env):
            parar = True
            if self.motivo == "step":
                self.motivo = "breakpoint"
        elif self.modo == PASSO:
            parar = True
        elif self.modo == PROXIMO:
            # 'próximo' anda na MESMA ação: mais fundo é a chamada que
            # ele decidiu pular.
            parar = profundidade <= (self.profundidade_alvo or 0)
        elif self.modo == SAIR_DO_QUADRO:
            parar = profundidade < (self.profundidade_alvo or 0)

        if parar:
            self.ultima_linha = linha
            self.quadro_atual = env
            self._parar(no, env, linha)

    def _parada_dispara(self, linha, env):
        """A linha tem parada; ela dispara AGORA?"""
        condicao = self.condicoes.get(linha)
        if condicao is None or condicao.vazia:
            return True

        if condicao.condicao:
            try:
                valor = self._avaliar_cru(condicao.condicao, env)
            except Exception as erro:                   # noqa: BLE001
                # Uma condição que não dá para avaliar PARA, e diz por
                # quê. Calar faria a parada nunca disparar, e a pessoa
                # concluiria que o código não passa por ali — a conclusão
                # errada, tirada com toda a confiança.
                self.motivo = ("a condição da parada falhou: "
                               + (getattr(erro, "message", None) or str(erro)))
                return True
            if not self.interp._verdade(valor):
                return False

        if not condicao._contagem_dispara():
            return False

        if condicao.log:
            self._registrar_log(self._texto_do_log(condicao.log, env), linha)
            return False
        return True

    def _avaliar_cru(self, expressao, env):
        """Avalia sem tocar em nada da depuração, e LEVANTA se falhar."""
        from .lexer import tokenize
        from .parser import parse

        self._local.avaliando = True
        try:
            arvore = parse(tokenize(expressao, "<condição>"), "<condição>")
            if not arvore.body:
                return None
            return self.interp.evaluate(arvore.body[0], env)
        finally:
            self._local.avaliando = False

    def _texto_do_log(self, molde, env):
        """'x vale {x}' pela interpolação da própria linguagem.

        Reusar '$"…"' dá ao logpoint exatamente as regras que quem escreve
        já conhece — inclusive o formato, '{preco:.2f}'. Uma segunda
        implementação de '{…}' divergiria na primeira expressão com
        chave dentro.
        """
        texto = molde.replace("\\", "\\\\").replace('"', '\\"')
        try:
            return self.interp._to_str(self._avaliar_cru(f'$"{texto}"', env))
        except Exception as erro:                       # noqa: BLE001
            return (f"{molde}  ← não deu para avaliar: "
                    f"{getattr(erro, 'message', None) or erro}")

    def _registrar_log(self, texto, linha):
        print(f"{_cor('◆', '1;35')} {_cor(f'{self.arquivo}:{linha}', '0;90')} {texto}")

    # ── vigias ──────────────────────────────────────────────

    def vigiar(self, expressao, escopo=None):
        """Passa a parar quando o valor da expressao mudar. Levanta ValueError."""
        from .lexer import tokenize
        from .parser import parse
        texto = (expressao or "").strip()
        try:
            arvore = parse(tokenize(texto, "<vigia>"), "<vigia>")
        except DataForgeError as erro:
            raise ValueError(f"'{texto}' nao e uma expressao: "
                             f"{getattr(erro, 'message', erro)}") from None
        if len(arvore.body) != 1 or type(arvore.body[0]).__name__ in (
                "Assignment", "OutStatement", "ActionDeclaration"):
            raise ValueError(f"'{texto}' nao e uma expressao que se possa vigiar")
        vigia = Vigia(texto, escopo, arvore.body[0])
        self._fotografar(vigia)
        with self._trava_das_vigias:
            self.vigias.append(vigia)
        return vigia

    def vigiar_leitura(self, descricao, ler, escopo=None, origem=""):
        """Uma vigia que le por uma funcao, e nao por expressao — o DAP
        aponta uma variavel de um escopo, ou um item de uma colecao."""
        vigia = Vigia(descricao, escopo, None, ler, origem)
        self._fotografar(vigia)
        with self._trava_das_vigias:
            self.vigias.append(vigia)
        return vigia

    def desvigiar(self, numero):
        """Tira a vigia de numero N (1, 2, …). Devolve se havia."""
        with self._trava_das_vigias:
            if 1 <= int(numero) <= len(self.vigias):
                self.vigias.pop(int(numero) - 1)
                return True
        return False

    def _ler_vigia(self, vigia):
        if vigia.ler is not None:
            return vigia.ler()
        escopo = vigia.escopo if vigia.escopo is not None else self.interp.global_env
        self._local.avaliando = True
        try:
            return self.interp.evaluate(vigia.arvore, escopo)
        finally:
            self._local.avaliando = False

    def _fotografar(self, vigia):
        """(foto, texto) do valor agora — ou INDISPONIVEL."""
        try:
            valor = self._ler_vigia(vigia)
        except (DataForgeError, Exception):            # noqa: BLE001
            vigia.foto, vigia.texto = INDISPONIVEL, "(não existe)"
            return
        vigia.foto = impressao(valor)
        texto = self.interp._to_str(valor)
        vigia.texto = texto if len(texto) <= 60 else texto[:57] + "…"

    def _conferir_vigias(self, no, env):
        """Alguma vigia mudou com a instrucao que acabou de rodar? Para."""
        mudaram = []
        with self._trava_das_vigias:
            for numero, vigia in enumerate(list(self.vigias), start=1):
                if vigia.escopo is not None and not _dentro_de(env, vigia.escopo):
                    # a vigia de uma acao so vale enquanto a acao roda: um
                    # escopo que ja saiu pode ser reaproveitado, e o mesmo
                    # nome la fora e OUTRA variavel
                    continue
                antes_foto, antes_texto = vigia.foto, vigia.texto
                self._fotografar(vigia)
                if vigia.foto == antes_foto:
                    continue
                vigia.mudancas += 1
                if antes_foto is INDISPONIVEL:
                    mudaram.append(f"vigia {numero}: {vigia.expressao} passou a "
                                   f"existir, e vale {vigia.texto}")
                elif vigia.foto is INDISPONIVEL:
                    mudaram.append(f"vigia {numero}: {vigia.expressao} deixou de "
                                   f"existir (valia {antes_texto})")
                else:
                    mudaram.append(f"vigia {numero}: {vigia.expressao} mudou de "
                                   f"{antes_texto} para {vigia.texto}")
        if not mudaram:
            return
        linha = getattr(no, "line", 0) or (self.ultima_linha or 0)
        self.ultima_linha = linha
        self.quadro_atual = env
        self._parar_por_vigia(no, env, linha, "; ".join(mudaram))

    def _parar_por_vigia(self, no, env, linha, texto):
        self.motivo = texto
        self._parar(no, env, linha)

    def _mostrar_vigias(self):
        with self._trava_das_vigias:
            vigias = list(self.vigias)
        if not vigias:
            print(_cor("  nenhuma vigia", "0;90"))
            return
        for numero, vigia in enumerate(vigias, start=1):
            print(f"  {numero}  {vigia.expressao} = {_cor(vigia.texto, '1;32')}"
                  f"{_cor(f'  ({vigia.mudancas} mudança(s))', '0;90')}")

    def definir_parada(self, linha, condicao="", vezes="", log=""):
        """Liga a parada, com ou sem condição. Levanta se a contagem é inválida."""
        c = Condicao(condicao, vezes, log)
        self.paradas.add(linha)
        if c.vazia:
            self.condicoes.pop(linha, None)
        else:
            self.condicoes[linha] = c
        return c

    # ── a interface ─────────────────────────────────────────

    def _parar(self, no, env, linha):
        # Um terminal é UMA conversa. Duas threads paradas ao mesmo tempo
        # disputariam o mesmo 'input()' e embaralhariam as respostas; com a
        # trava, a segunda espera a primeira ser solta. Parar cada thread
        # de forma independente é o que o 'dataforge dap' faz, onde o
        # painel mostra uma de cada vez.
        with self._trava_do_terminal:
            return self._parar_no_terminal(no, env, linha)

    def _parar_no_terminal(self, no, env, linha):
        marca = ("◉" if str(self.motivo).startswith("vigia ")
                 else "●" if linha in self.paradas else "→")
        print()
        print(f"{_cor(marca, '1;33')} {_cor(f'{self.arquivo}:{linha}', '1;37')}"
              f"  {_cor(type(no).__name__, '0;90')}")
        if str(self.motivo).startswith("vigia "):
            for trecho in str(self.motivo).split("; "):
                print(f"  {_cor(trecho, '1;35')}")
        elif self.motivo not in ("step", "breakpoint"):
            print(f"  {_cor(self.motivo, '1;31')}")
        self._listar(linha, 2)
        for expressao in self.observadas:
            print(f"  {_cor('olho', '0;90')} {expressao} = "
                  f"{self._avaliar(expressao, env)}")

        while True:
            try:
                comando = input(_cor("(df) ", "1;36")).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                self.saindo = True
                self.modo = CONTINUAR
                return
            if self._comando(comando, no, env, linha):
                return

    def _comando(self, entrada, no, env, linha):
        """Devolve True quando é para voltar a executar."""
        if not entrada:
            entrada = "p"                       # Enter repete o passo
        palavra, _, resto = entrada.partition(" ")
        resto = resto.strip()
        palavra = palavra.lower()

        if palavra in ("c", "continuar"):
            self.modo = CONTINUAR
            return True
        if palavra in ("p", "passo"):
            self.modo = PASSO
            return True
        if palavra in ("n", "proximo", "próximo"):
            self.modo = PROXIMO
            self.profundidade_alvo = self._profundidade()
            return True
        if palavra in ("f", "fora", "sair-do-quadro"):
            self.modo = SAIR_DO_QUADRO
            self.profundidade_alvo = self._profundidade()
            return True

        if palavra in ("b", "parar"):
            self._alternar_parada(resto, linha)
        elif palavra in ("paradas",):
            self._mostrar_paradas()
        elif palavra in ("w", "vigiar", "watch"):
            if not resto:
                print(_cor("  vigiar <expressão>", "0;90"))
            else:
                try:
                    vigia = self.vigiar(resto, env)
                except ValueError as erro:
                    print(_cor(f"  {erro}", "1;31"))
                else:
                    print(_cor(f"  ◉ vigia {len(self.vigias)}: {vigia.expressao} "
                               f"= {vigia.texto} — para quando mudar", "1;35"))
        elif palavra in ("vigias", "watches"):
            self._mostrar_vigias()
        elif palavra in ("desvigiar", "unwatch"):
            if resto.isdigit() and self.desvigiar(int(resto)):
                print(_cor(f"  vigia {resto} removida", "0;90"))
            else:
                print(_cor("  desvigiar <número> — veja 'vigias'", "1;31"))
        elif palavra in ("l", "listar"):
            self._listar(linha, int(resto) if resto.isdigit() else 5)
        elif palavra in ("v", "ver"):
            if resto:
                print(f"  {resto} = {self._avaliar(resto, env)}")
            else:
                print(_cor("  ver <expressão>", "0;90"))
        elif palavra in ("olho", "observar"):
            if resto:
                self.observadas.append(resto)
                print(_cor(f"  observando '{resto}'", "0;90"))
        elif palavra in ("vars", "variaveis", "variáveis"):
            self._mostrar_variaveis(env)
        elif palavra in ("pilha",):
            self._mostrar_pilha()
        elif palavra in ("q", "sair", "quit"):
            self.saindo = True
            self.modo = CONTINUAR
            print(_cor("  encerrando", "0;90"))
            return True
        elif palavra in ("h", "?", "ajuda"):
            self._ajuda()
        else:
            # Sem comando, é expressão: é o que se quer 9 em 10 vezes.
            print(f"  {entrada} = {self._avaliar(entrada, env)}")
        return False

    # ── as respostas ────────────────────────────────────────

    def _listar(self, centro, volta):
        inicio = max(1, centro - volta)
        fim = min(len(self.linhas), centro + volta)
        for n in range(inicio, fim + 1):
            texto = self.linhas[n - 1]
            if n == centro:
                print(f"  {_cor(f'{n:>4} →', '1;33')} {_cor(texto, '1;37')}")
            else:
                marca = _cor("●", "1;31") if n in self.paradas else " "
                print(f"  {_cor(f'{n:>4}', '0;90')} {marca} {_cor(texto, '0;90')}")

    def _alternar_parada(self, resto, linha_atual):
        """'b', 'b 12', 'b 12 se x bigger 3', 'b 12 vezes >= 5', 'b 12 log x={x}'.

        Sem condição, alterna. Com condição, sempre LIGA — alternar uma
        parada condicional desligaria justamente a que se acabou de pedir.
        """
        import re

        numero, _, extra = resto.partition(" ")
        if numero.isdigit():
            alvo, extra = int(numero), extra.strip()
        else:
            alvo, extra = linha_atual, resto.strip()

        if not extra:
            if alvo in self.paradas:
                self.paradas.discard(alvo)
                self.condicoes.pop(alvo, None)
                print(_cor(f"  parada removida da linha {alvo}", "0;90"))
            else:
                self.paradas.add(alvo)
                print(_cor(f"  ● parada na linha {alvo}", "1;31"))
            return

        achado = re.fullmatch(r"(se|if|vezes|log)\s+(.+)", extra)
        if not achado:
            print(_cor("  use: b <linha> se <expr> | vezes <n> | log <texto>",
                       "1;31"))
            return
        tipo, valor = achado.group(1), achado.group(2).strip()
        try:
            c = self.definir_parada(
                alvo,
                condicao=valor if tipo in ("se", "if") else "",
                vezes=valor if tipo == "vezes" else "",
                log=valor if tipo == "log" else "")
        except ValueError as erro:
            print(_cor(f"  {erro}", "1;31"))
            return
        print(_cor(f"  ● parada na linha {alvo} ({c.descrever()})", "1;31"))

    def _mostrar_paradas(self):
        if not self.paradas:
            print(_cor("  nenhuma parada", "0;90"))
            return
        for n in sorted(self.paradas):
            # A expressao sai da f-string: quebra-la dentro das chaves so
            # e valido a partir do Python 3.12, e a linguagem promete
            # 3.10+. O arquivo inteiro deixava de importar la.
            texto = self.linhas[n - 1].strip() if n <= len(self.linhas) else ""
            condicao = self.condicoes.get(n)
            extra = _cor(f"  [{condicao.descrever()}]", "0;90") if condicao else ""
            print(f"  {_cor('●', '1;31')} {n:>4}  {texto}{extra}")

    def _avaliar(self, expressao, env):
        """Avalia no QUADRO onde paramos, não no global.

        Avaliar no escopo global mostraria o valor errado — ou nenhum —
        justamente para as variáveis locais, que são as que se quer ver
        ao parar dentro de uma ação.
        """
        from .lexer import tokenize
        from .parser import parse
        try:
            arvore = parse(tokenize(expressao, "<debug>"), "<debug>")
            if not arvore.body:
                return _cor("(vazio)", "0;90")
            valor = self.interp.evaluate(arvore.body[0], env)
            return _cor(self.interp._to_str(valor), "1;32")
        except DataForgeError as erro:
            return _cor(getattr(erro, "message", str(erro)), "1;31")
        except Exception as erro:                       # noqa: BLE001
            return _cor(str(erro), "1;31")

    def _mostrar_variaveis(self, env):
        """O que está valendo aqui, do escopo mais próximo ao global.

        Um nome redeclarado aparece uma vez só, com o valor que vale
        AGORA — mostrar as duas cópias sugeriria que ambas estão vivas.

        As 227 embutidas ficam de fora. Elas VIVEM no escopo global, e
        despejá-las enterra as três variáveis que a pessoa parou para
        ver — que é a única coisa que ela pediu.
        """
        embutidas = self._nomes_embutidos()
        vistos = set()
        atual, nivel = env, 0
        while atual is not None and nivel < 12:
            proprias = {k: v for k, v in getattr(atual, "variables", {}).items()
                        if not k.startswith("__") and k not in vistos
                        and k not in embutidas}
            if proprias:
                nome = getattr(atual, "name", "") or (
                    "global" if getattr(atual, "parent", None) is None else "bloco")
                print(f"  {_cor(nome, '1;36')}")
                for chave in sorted(proprias):
                    vistos.add(chave)
                    valor = self.interp._to_str(proprias[chave])
                    if len(valor) > 68:
                        valor = valor[:65] + "…"
                    print(f"    {chave:<18} {_cor(valor, '0;37')}")
            atual = getattr(atual, "parent", None)
            nivel += 1

    _embutidas = None

    @classmethod
    def _nomes_embutidos(cls):
        if cls._embutidas is None:
            from .builtins import get_builtins
            cls._embutidas = frozenset(get_builtins())
        return cls._embutidas

    def _mostrar_pilha(self):
        pilha = list(getattr(self.interp, "_call_stack", ()) or ())
        if not pilha:
            print(_cor("  no topo — nenhuma ação em andamento", "0;90"))
            return
        for i, quadro in enumerate(reversed(pilha)):
            seta = "→" if i == 0 else " "
            nome = getattr(quadro, "name", "?")
            linha = getattr(quadro, "line", 0)
            print(f"  {seta} {_cor(nome, '1;37')}  "
                  f"{_cor(f'{self.arquivo}:{linha}', '0;90')}")

    @staticmethod
    def _ajuda():
        print(f"""
  {_cor('andar', '1;37')}
    {_cor('p', '1;36')} / Enter   passo — entra na ação
    {_cor('n', '1;36')}           próximo — passa por cima da chamada
    {_cor('f', '1;36')}           fora — roda até esta ação retornar
    {_cor('c', '1;36')}           continuar até a próxima parada

  {_cor('olhar', '1;37')}
    {_cor('v', '1;36')} <expr>    avalia no quadro onde você está
    <expr>        o mesmo, sem escrever 'v' — mas um nome de uma letra
                  que seja comando ('n', 'p', 'c', 'l', 'f', 'b', 'v')
                  vale como comando: para esses, use 'v n'
    {_cor('vars', '1;36')}        o que está valendo, escopo por escopo
    {_cor('pilha', '1;36')}       quem chamou quem
    {_cor('l', '1;36')} [n]       lista a fonte em volta
    {_cor('olho', '1;36')} <expr> mostra a expressão a cada parada

  {_cor('paradas', '1;37')}
    {_cor('b', '1;36')} [linha]   liga/desliga (sem número, a linha atual)
    {_cor('b', '1;36')} 12 se <expr>      só para quando a expressão vale
    {_cor('b', '1;36')} 12 vezes >= 5     conta as passagens ('N', '>', '==', '%')
    {_cor('b', '1;36')} 12 log x={{x}}      imprime e não para
    {_cor('paradas', '1;36')}     lista as que existem

  {_cor('vigias', '1;37')}  (param quando um valor MUDA)
    {_cor('w', '1;36')} <expr>    vigia a expressão, no quadro onde você está
    {_cor('vigias', '1;36')}      lista as vigias, com o valor e quantas mudanças
    {_cor('desvigiar', '1;36')} N tira a vigia N

    {_cor('q', '1;36')}           encerra
""")


def depurar(caminho, paradas=(), argv=(), vigias=()):
    """Roda o programa sob o depurador."""
    from .interpreter import Interpreter
    from .lexer import tokenize
    from .parser import parse

    if not os.path.isfile(caminho):
        print(_cor(f"não encontrei '{caminho}'", "1;31"), file=sys.stderr)
        return 1

    with open(caminho, encoding="utf-8") as f:
        fonte = f.read()

    try:
        arvore = parse(tokenize(fonte, caminho), caminho)
    except DataForgeError as erro:
        print(erro.format() if hasattr(erro, "format") else str(erro),
              file=sys.stderr)
        return 1

    interpretador = Interpreter()
    interpretador.script_args = list(argv)
    d = Depurador(interpretador, os.path.basename(caminho), fonte, paradas)
    for expressao in vigias:
        try:
            d.vigiar(expressao)
        except ValueError as erro:
            print(_cor(f"  {erro}", "1;31"), file=sys.stderr)
            return 1

    print(f"{_cor('depurador do DataForge', '1;37')} — "
          f"{_cor('h', '1;36')} para a ajuda, {_cor('c', '1;36')} para correr")
    if paradas:
        print(_cor(f"  paradas: {', '.join(str(p) for p in sorted(paradas))}",
                   "0;90"))
    if vigias:
        print(_cor(f"  vigias: {', '.join(vigias)}", "0;90"))

    d.ligar()
    try:
        interpretador.run(arvore)
    except DataForgeError as erro:
        d.desligar()
        print()
        print(erro.format() if hasattr(erro, "format") else str(erro),
              file=sys.stderr)
        return 1
    except ControlSignal:
        pass
    finally:
        d.desligar()

    print()
    print(_cor("  programa terminou", "0;90"))
    return 0
