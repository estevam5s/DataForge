# -*- coding: utf-8 -*-
"""Arcane.Cli — argumentos, perguntas e o console interativo.

O que faltava
-------------
`dataforge` tem uma CLI completa. Um programa ESCRITO em DataForge não
tinha nada: `OS.args()` devolve a lista crua, e ler `--porta=8080` dela
é escrever o mesmo laço de novo em cada programa.

Três decisões
-------------
1. **A ajuda é gerada da declaração.** Uma ajuda escrita à mão envelhece
   no primeiro flag novo — e a ajuda errada é pior que nenhuma, porque
   quem lê confia nela.

2. **O erro diz o que era esperado, e sai com código 2.** Código 1 é
   "o programa rodou e deu errado"; 2 é "você chamou errado". Um script
   que testa `$?` precisa distinguir os dois.

3. **`perguntar` recusa rodar sem terminal.** Numa pipeline de CI, uma
   pergunta interativa trava o build para sempre, sem dizer por quê. É
   melhor falhar na hora, dizendo qual flag passar.
"""

import os
import sys


class ErroDeCli(Exception):
    pass


class SaidaDaCli(Exception):
    """Pediu ajuda ou errou a chamada: o programa termina aqui."""

    def __init__(self, texto, codigo=0):
        self.texto = texto
        self.codigo = codigo
        super().__init__(texto)


# ══════════════════════════════════════════════════════════════
#  Declarar e ler argumentos
# ══════════════════════════════════════════════════════════════

TIPOS = {
    "texto": str,
    "inteiro": int,
    "numero": float,
    "sim_nao": bool,
    "lista": list,
}


class Comando:
    """Um comando: o que ele aceita, e como ele se explica."""

    def __init__(self, nome=None, sobre="", versao=""):
        self.nome = nome or os.path.basename(sys.argv[0] or "programa")
        self.sobre = sobre
        self.versao = versao
        self.opcoes = {}          # nome longo -> ficha
        self.curtas = {}          # letra -> nome longo
        self.posicionais = []
        self.subcomandos = {}
        self.exemplos = []

    # ── declarar ──

    def opcao(self, nome, tipo="texto", curta="", padrao=None, sobre="",
              exigida=False, escolhas=None):
        """`--nome valor`. Com `tipo := "sim_nao"`, é só `--nome`."""
        if nome in self.opcoes:
            raise ErroDeCli(f"a opção '--{nome}' foi declarada duas vezes")
        if tipo not in TIPOS:
            raise ErroDeCli(
                f"não conheço o tipo '{tipo}'. Há: {', '.join(TIPOS)}")
        ficha = {"nome": nome, "tipo": tipo, "curta": curta,
                 "padrao": padrao if padrao is not None
                 else (False if tipo == "sim_nao" else None),
                 "sobre": sobre, "exigida": exigida,
                 "escolhas": list(escolhas) if escolhas else None}
        self.opcoes[nome] = ficha
        if curta:
            letra = curta.lstrip("-")[:1]
            if letra in self.curtas:
                raise ErroDeCli(
                    f"'-{letra}' já é de '--{self.curtas[letra]}'")
            self.curtas[letra] = nome
        return self

    def posicional(self, nome, sobre="", varios=False, exigido=True):
        self.posicionais.append({"nome": nome, "sobre": sobre,
                                 "varios": varios, "exigido": exigido})
        return self

    def exemplo(self, linha, sobre=""):
        self.exemplos.append({"linha": linha, "sobre": sobre})
        return self

    def subcomando(self, nome, sobre=""):
        sub = Comando(f"{self.nome} {nome}", sobre)
        self.subcomandos[nome] = sub
        return sub

    # ── ler ──

    def ler(self, argumentos=None):
        """Os argumentos viram um vault. Levanta SaidaDaCli para ajuda/erro."""
        bruto = list(argumentos if argumentos is not None else sys.argv[1:])

        if bruto and bruto[0] in self.subcomandos:
            sub = bruto[0]
            saida = self.subcomandos[sub].ler(bruto[1:])
            saida["__comando__"] = sub
            return saida
        if self.subcomandos and bruto and not bruto[0].startswith("-"):
            raise SaidaDaCli(
                f"{self.nome}: não conheço o comando '{bruto[0]}'.\n"
                f"  Há: {', '.join(sorted(self.subcomandos))}\n"
                f"  Use '{self.nome} --ajuda' para ver tudo.", 2)

        valores = {n: f["padrao"] for n, f in self.opcoes.items()}
        soltos = []
        i = 0
        while i < len(bruto):
            peca = bruto[i]

            if peca in ("--ajuda", "-h", "--help"):
                raise SaidaDaCli(self.ajuda(), 0)
            if peca in ("--versao", "--version") and self.versao:
                raise SaidaDaCli(f"{self.nome} {self.versao}", 0)
            if peca == "--":
                soltos.extend(bruto[i + 1:])
                break

            if peca.startswith("--"):
                nome, _, junto = peca[2:].partition("=")
                ficha = self.opcoes.get(nome)
                if ficha is None:
                    raise SaidaDaCli(self._nao_conheco(f"--{nome}"), 2)
                i = self._pegar(ficha, valores, junto or None, bruto, i)
                continue

            if peca.startswith("-") and len(peca) > 1:
                letra = peca[1]
                nome = self.curtas.get(letra)
                if nome is None:
                    raise SaidaDaCli(self._nao_conheco(f"-{letra}"), 2)
                junto = peca[2:] or None
                i = self._pegar(self.opcoes[nome], valores, junto, bruto, i)
                continue

            soltos.append(peca)
            i += 1

        self._exigir(valores)
        self._posicionais(soltos, valores)
        valores["__soltos__"] = soltos
        return valores

    def _pegar(self, ficha, valores, junto, bruto, i):
        nome, tipo = ficha["nome"], ficha["tipo"]
        if tipo == "sim_nao":
            valores[nome] = True
            return i + 1
        if junto is None:
            if i + 1 >= len(bruto):
                raise SaidaDaCli(
                    f"{self.nome}: '--{nome}' precisa de um valor.\n"
                    f"  {ficha['sobre'] or ''}".rstrip(), 2)
            junto = bruto[i + 1]
            i += 1
        valores[nome] = self._converter(ficha, junto)
        return i + 1

    def _converter(self, ficha, texto):
        nome, tipo = ficha["nome"], ficha["tipo"]
        if tipo == "lista":
            itens = [p.strip() for p in str(texto).split(",") if p.strip()]
            self._conferir_escolha(ficha, itens)
            return itens
        try:
            valor = TIPOS[tipo](texto)
        except (TypeError, ValueError):
            raise SaidaDaCli(
                f"{self.nome}: '--{nome}' espera {tipo} e recebeu "
                f"'{texto}'.", 2) from None
        self._conferir_escolha(ficha, [valor])
        return valor

    def _conferir_escolha(self, ficha, valores):
        if not ficha["escolhas"]:
            return
        for v in valores:
            if v not in ficha["escolhas"]:
                raise SaidaDaCli(
                    f"{self.nome}: '--{ficha['nome']}' aceita "
                    f"{', '.join(map(str, ficha['escolhas']))} — "
                    f"veio '{v}'.", 2)

    def _exigir(self, valores):
        faltando = [f"--{n}" for n, f in self.opcoes.items()
                    if f["exigida"] and valores.get(n) in (None, [])]
        if faltando:
            raise SaidaDaCli(
                f"{self.nome}: falta {', '.join(faltando)}.\n"
                f"  Use '{self.nome} --ajuda'.", 2)

    def _posicionais(self, soltos, valores):
        restantes = list(soltos)
        for k, ficha in enumerate(self.posicionais):
            if ficha["varios"]:
                valores[ficha["nome"]] = restantes
                restantes = []
                continue
            if restantes:
                valores[ficha["nome"]] = restantes.pop(0)
            elif ficha["exigido"]:
                raise SaidaDaCli(
                    f"{self.nome}: falta o argumento "
                    f"<{ficha['nome']}>.\n  Use '{self.nome} --ajuda'.", 2)
            else:
                valores[ficha["nome"]] = None

    def _nao_conheco(self, escrito):
        import difflib
        nomes = [f"--{n}" for n in self.opcoes] + \
                [f"-{c}" for c in self.curtas]
        perto = difflib.get_close_matches(escrito, nomes, n=1, cutoff=0.5)
        dica = (f"  Você quis dizer '{perto[0]}'?" if perto
                else f"  Use '{self.nome} --ajuda' para ver as opções.")
        return f"{self.nome}: não conheço '{escrito}'.\n{dica}"

    # ── explicar ──

    def ajuda(self):
        """A ajuda, GERADA da declaração.

        Escrita à mão, ela envelhece no primeiro flag novo — e a ajuda
        errada é pior que nenhuma, porque quem lê confia nela.
        """
        linhas = []
        if self.sobre:
            linhas += [self.sobre, ""]

        uso = [self.nome]
        if self.opcoes:
            uso.append("[opções]")
        if self.subcomandos:
            uso.append("<comando>")
        for p in self.posicionais:
            marca = f"<{p['nome']}>" if p["exigido"] else f"[{p['nome']}]"
            uso.append(marca + ("..." if p["varios"] else ""))
        linhas += [f"uso: {' '.join(uso)}", ""]

        if self.subcomandos:
            linhas.append("comandos:")
            largura = max(len(n) for n in self.subcomandos)
            for nome, sub in sorted(self.subcomandos.items()):
                linhas.append(f"  {nome:<{largura}}  {sub.sobre}")
            linhas.append("")

        if self.posicionais:
            linhas.append("argumentos:")
            largura = max(len(p["nome"]) for p in self.posicionais)
            for p in self.posicionais:
                linhas.append(f"  {p['nome']:<{largura}}  {p['sobre']}")
            linhas.append("")

        if self.opcoes:
            linhas.append("opções:")
            rotulos = {}
            for nome, f in self.opcoes.items():
                curta = f"-{f['curta'].lstrip('-')}, " if f["curta"] else "    "
                valor = "" if f["tipo"] == "sim_nao" else f" {f['tipo'].upper()}"
                rotulos[nome] = f"  {curta}--{nome}{valor}"
            largura = max(len(r) for r in rotulos.values())
            for nome, f in self.opcoes.items():
                extra = []
                if f["escolhas"]:
                    extra.append("|".join(map(str, f["escolhas"])))
                if f["padrao"] not in (None, False):
                    extra.append(f"padrão: {f['padrao']}")
                if f["exigida"]:
                    extra.append("exigida")
                cauda = f"  ({'; '.join(extra)})" if extra else ""
                linhas.append(
                    f"{rotulos[nome]:<{largura}}  {f['sobre']}{cauda}")
            linhas.append(f"{'  -h, --ajuda':<{largura}}  mostra esta ajuda")
            if self.versao:
                linhas.append(f"{'      --versao':<{largura}}  mostra a versão")
            linhas.append("")

        if self.exemplos:
            linhas.append("exemplos:")
            for e in self.exemplos:
                linhas.append(f"  {e['linha']}")
                if e["sobre"]:
                    linhas.append(f"      {e['sobre']}")
            linhas.append("")

        return "\n".join(linhas).rstrip()

    def rodar(self, argumentos=None, sair=True):
        """Lê e devolve o vault. Imprime a ajuda ou o erro e sai."""
        try:
            return self.ler(argumentos)
        except SaidaDaCli as fim:
            fluxo = sys.stdout if fim.codigo == 0 else sys.stderr
            print(fim.texto, file=fluxo)
            if sair:
                sys.exit(fim.codigo)
            return None

    def __repr__(self):
        return f"<comando '{self.nome}' {len(self.opcoes)} opções>"


def comando(nome=None, sobre="", versao=""):
    return Comando(nome, sobre, versao)


# ══════════════════════════════════════════════════════════════
#  Perguntar
# ══════════════════════════════════════════════════════════════

def tem_terminal():
    """Há alguém do outro lado para responder?"""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False


def _exigir_terminal(o_que):
    if tem_terminal():
        return
    raise ErroDeCli(
        f"não dá para {o_que}: não há terminal.\n"
        f"  Numa pipeline de CI ou com a entrada redirecionada, uma\n"
        f"  pergunta trava o processo para sempre, sem dizer por quê.\n"
        f"  Passe o valor por opção de linha de comando.")


def perguntar(texto, padrao=None, valida=None):
    _exigir_terminal("perguntar")
    marca = f" [{padrao}]" if padrao is not None else ""
    while True:
        resposta = input(f"{texto}{marca}: ").strip()
        if not resposta and padrao is not None:
            return padrao
        if not resposta:
            continue
        if valida is None:
            return resposta
        try:
            if valida(resposta):
                return resposta
        except Exception:                            # noqa: BLE001
            pass
        print("  valor inválido, tente de novo")


def confirmar(texto, padrao=False):
    _exigir_terminal("confirmar")
    marca = "[S/n]" if padrao else "[s/N]"
    resposta = input(f"{texto} {marca}: ").strip().lower()
    if not resposta:
        return padrao
    return resposta in ("s", "sim", "y", "yes")


def escolher(texto, opcoes, padrao=0):
    _exigir_terminal("escolher")
    itens = list(opcoes)
    print(texto)
    for i, item in enumerate(itens, 1):
        marca = " ←" if i - 1 == padrao else ""
        print(f"  {i}) {item}{marca}")
    while True:
        resposta = input(f"escolha [1-{len(itens)}]: ").strip()
        if not resposta:
            return itens[padrao]
        if resposta.isdigit() and 1 <= int(resposta) <= len(itens):
            return itens[int(resposta) - 1]
        print("  número fora da lista")


def segredo(texto="senha"):
    """Lê sem ecoar. Para senha e token."""
    _exigir_terminal("pedir um segredo")
    import getpass
    return getpass.getpass(f"{texto}: ")


# ══════════════════════════════════════════════════════════════
#  Console interativo
# ══════════════════════════════════════════════════════════════

class Console:
    """Um laço de comandos, com ajuda e histórico."""

    def __init__(self, prompt="> ", sobre=""):
        self.prompt = prompt
        self.sobre = sobre
        self.comandos = {}
        self.historico = []
        self.rodando = False

    def registrar(self, nome, acao, sobre=""):
        self.comandos[nome] = {"acao": acao, "sobre": sobre}
        return self

    def rodar(self):
        _exigir_terminal("abrir o console")
        self.rodando = True
        if self.sobre:
            print(self.sobre)
        print("  'ajuda' lista os comandos, 'sair' encerra.\n")
        while self.rodando:
            try:
                linha = input(self.prompt).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not linha:
                continue
            self.historico.append(linha)
            nome, _, resto = linha.partition(" ")
            if nome in ("sair", "exit", "quit"):
                break
            if nome in ("ajuda", "help", "?"):
                print(self.ajuda())
                continue
            ficha = self.comandos.get(nome)
            if ficha is None:
                import difflib
                perto = difflib.get_close_matches(nome, list(self.comandos),
                                                  n=1, cutoff=0.5)
                print(f"  não conheço '{nome}'." +
                      (f" Você quis dizer '{perto[0]}'?" if perto
                       else " Digite 'ajuda'."))
                continue
            try:
                saida = ficha["acao"](resto.strip()) if resto.strip() \
                    else ficha["acao"]("")
                if saida is not None:
                    print(saida)
            except Exception as erro:                # noqa: BLE001
                print(f"  erro: {erro}")
        self.rodando = False
        return self

    def ajuda(self):
        if not self.comandos:
            return "  (nenhum comando registrado)"
        largura = max(len(n) for n in self.comandos)
        linhas = [f"  {n:<{largura}}  {f['sobre']}"
                  for n, f in sorted(self.comandos.items())]
        linhas.append(f"  {'ajuda':<{largura}}  esta lista")
        linhas.append(f"  {'sair':<{largura}}  encerra")
        return "\n".join(linhas)


def console(prompt="> ", sobre=""):
    return Console(prompt, sobre)


# ══════════════════════════════════════════════════════════════
#  Saída
# ══════════════════════════════════════════════════════════════

def largura():
    """Quantas colunas o terminal tem. 80 quando não há terminal."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def limpar():
    print("\033[2J\033[H", end="")


def erro(texto, codigo=1):
    """Escreve no stderr e sai. É o `die` que todo script precisa."""
    print(texto, file=sys.stderr)
    sys.exit(codigo)


class ArcaneCli:
    """O dicionário que `adopt Arcane.Cli` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Cli",

            "comando": comando,
            "Comando": Comando,

            "perguntar": perguntar,
            "confirmar": confirmar,
            "escolher": escolher,
            "segredo": segredo,
            "tem_terminal": tem_terminal,

            "console": console,
            "Console": Console,

            "largura": largura,
            "limpar": limpar,
            "erro": erro,
        }
