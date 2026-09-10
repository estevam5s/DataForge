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
        self.observadas = []           # expressões a mostrar a cada parada
        self.modo = PASSO if not paradas else CONTINUAR
        self.profundidade_alvo = None
        self.ultima_linha = None
        self.quadro_atual = None
        self.saindo = False
        self.original = None

    # ── instalar ────────────────────────────────────────────

    def ligar(self):
        """Sombreia 'execute'. Nada muda para quem não depura."""
        self.original = self.interp.execute

        def executar(no, env):
            if not self.saindo:
                self._antes(no, env)
            return self.original(no, env)

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

        if linha in self.paradas:
            parar = True
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

    # ── a interface ─────────────────────────────────────────

    def _parar(self, no, env, linha):
        marca = "●" if linha in self.paradas else "→"
        print()
        print(f"{_cor(marca, '1;33')} {_cor(f'{self.arquivo}:{linha}', '1;37')}"
              f"  {_cor(type(no).__name__, '0;90')}")
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
        alvo = int(resto) if resto.isdigit() else linha_atual
        if alvo in self.paradas:
            self.paradas.discard(alvo)
            print(_cor(f"  parada removida da linha {alvo}", "0;90"))
        else:
            self.paradas.add(alvo)
            print(_cor(f"  ● parada na linha {alvo}", "1;31"))

    def _mostrar_paradas(self):
        if not self.paradas:
            print(_cor("  nenhuma parada", "0;90"))
            return
        for n in sorted(self.paradas):
            print(f"  {_cor('●', '1;31')} {n:>4}  {self.linhas[n - 1].strip()
                                                  if n <= len(self.linhas) else ''}")

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
    {_cor('paradas', '1;36')}     lista as que existem

    {_cor('q', '1;36')}           encerra
""")


def depurar(caminho, paradas=(), argv=()):
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

    print(f"{_cor('depurador do DataForge', '1;37')} — "
          f"{_cor('h', '1;36')} para a ajuda, {_cor('c', '1;36')} para correr")
    if paradas:
        print(_cor(f"  paradas: {', '.join(str(p) for p in sorted(paradas))}",
                   "0;90"))

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
