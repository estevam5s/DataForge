# -*- coding: utf-8 -*-
"""A linguagem de consulta: ler o texto que o cliente manda.

Por que ela é indentada
-----------------------
O GraphQL usa chaves porque nasceu em JavaScript. DataForge é
indentada, e uma consulta escrita ao lado do código que a usa tem de
parecer com ele:

    busca:
        usuario(id: 7):
            nome
            email
            pedidos(limite: 3):
                numero
                total

A mesma consulta em GraphQL teria quatro `{` e quatro `}` dizendo o que
a indentação já dizia. O `:` no fim marca "isto tem seleção dentro" —
exatamente como `given`, `cycle` e `action` na linguagem.

Um campo sem seleção é uma folha (`nome`); um com seleção precisa dos
dois pontos. É a mesma regra do bloco, e o erro de esquecer o `:` diz
isso.

O que existe
------------
    busca / mudanca / assinatura       as três operações
    nome(arg: valor)                   argumentos
    apelido: campo                     apelido
    ...Trecho                          usar um trecho
    ... em Tipo:                       trecho condicional (união/contrato)
    @incluir(se: $x) / @pular(se: $x)  diretivas
    trecho Nome em Tipo:               declarar um trecho
    busca Nome($v: Tipo! := padrao):   variáveis, com padrão
"""

import re

from .esquema import ler_tipo


class ErroDeConsulta(Exception):
    """O texto da consulta não é uma consulta. Sempre com linha e coluna."""

    def __init__(self, mensagem, linha=0, coluna=0, dica=""):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        self.dica = dica
        onde = f" (linha {linha}, coluna {coluna})" if linha else ""
        super().__init__(mensagem + onde + (f"\n  dica: {dica}" if dica else ""))


# ── A árvore ───────────────────────────────────────────────────

class Selecao:
    """Um campo pedido: o nome, o apelido, os argumentos e o que vem dentro."""

    __slots__ = ("nome", "apelido", "argumentos", "selecoes", "diretivas",
                 "linha", "coluna", "tipo_condicional", "trecho")

    def __init__(self, nome, apelido=None, argumentos=None, selecoes=None,
                 diretivas=None, linha=0, coluna=0, tipo_condicional=None,
                 trecho=None):
        self.nome = nome
        self.apelido = apelido or nome
        self.argumentos = argumentos or {}
        self.selecoes = selecoes or []
        self.diretivas = diretivas or []
        self.linha = linha
        self.coluna = coluna
        self.tipo_condicional = tipo_condicional
        self.trecho = trecho

    def __repr__(self):
        return f"<selecao {self.apelido}>"


class Operacao:
    __slots__ = ("especie", "nome", "variaveis", "selecoes", "linha")

    def __init__(self, especie, nome=None, variaveis=None, selecoes=None,
                 linha=0):
        self.especie = especie      # busca | mudanca | assinatura
        self.nome = nome
        self.variaveis = variaveis or {}
        self.selecoes = selecoes or []
        self.linha = linha

    def __repr__(self):
        return f"<{self.especie} {self.nome or 'anônima'}>"


class Trecho:
    __slots__ = ("nome", "tipo", "selecoes", "linha")

    def __init__(self, nome, tipo, selecoes=None, linha=0):
        self.nome = nome
        self.tipo = tipo
        self.selecoes = selecoes or []
        self.linha = linha


class Documento:
    __slots__ = ("operacoes", "trechos")

    def __init__(self, operacoes=None, trechos=None):
        self.operacoes = operacoes or []
        self.trechos = trechos or {}

    def operacao(self, nome=None):
        """A operação pedida — ou a única, quando só há uma."""
        if nome:
            for op in self.operacoes:
                if op.nome == nome:
                    return op
            disponiveis = ", ".join(o.nome or "(anônima)"
                                    for o in self.operacoes) or "nenhuma"
            raise ErroDeConsulta(
                f"o documento não tem a operação '{nome}'",
                dica=f"ele tem: {disponiveis}")
        if not self.operacoes:
            raise ErroDeConsulta("o documento não tem nenhuma operação",
                                 dica="comece com 'busca:'")
        if len(self.operacoes) > 1:
            nomes = ", ".join(o.nome or "(anônima)" for o in self.operacoes)
            raise ErroDeConsulta(
                "o documento tem mais de uma operação e nenhuma foi escolhida",
                dica=f"passe 'operacao := \"…\"'. Há: {nomes}")
        return self.operacoes[0]


# ── O leitor ───────────────────────────────────────────────────

_ESPACOS = re.compile(r"[ \t]*")
_NOME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_NUMERO = re.compile(r"-?\d+(\.\d+)?([eE][+-]?\d+)?")

OPERACOES = {"busca": "busca", "mudanca": "mudanca", "mudança": "mudanca",
             "assinatura": "assinatura"}


class Leitor:
    """Lê o texto e devolve o Documento. Um passo, sem árvore intermediária."""

    def __init__(self, texto):
        # Uma consulta vem de FORA — de um corpo HTTP, de um arquivo, de
        # um editor. Normalizar a quebra de linha aqui evita que um
        # cliente Windows receba erro de coluna em toda linha.
        self.texto = texto.replace("\r\n", "\n").replace("\r", "\n")
        self.linhas = self.texto.split("\n")

    def ler(self):
        operacoes, trechos = [], {}
        i = 0
        while i < len(self.linhas):
            crua = self.linhas[i]
            nua = self._sem_comentario(crua).strip()
            if not nua:
                i += 1
                continue
            recuo = self._recuo(crua)
            if recuo != 0:
                raise ErroDeConsulta(
                    "esta linha está indentada e não há nada acima dela para "
                    "pertencer", i + 1, recuo + 1,
                    dica="uma operação ('busca:') começa na coluna 1")
            if nua.startswith("trecho "):
                trecho, i = self._ler_trecho(i)
                if trecho.nome in trechos:
                    raise ErroDeConsulta(
                        f"o trecho '{trecho.nome}' foi declarado duas vezes",
                        trecho.linha, 1)
                trechos[trecho.nome] = trecho
                continue
            operacao, i = self._ler_operacao(i)
            operacoes.append(operacao)
        return Documento(operacoes, trechos)

    # ── linhas ─────────────────────────────────────────────

    @staticmethod
    def _sem_comentario(linha):
        """'#' e '//' comentam — fora de aspas."""
        saida, aspas, k = [], "", 0
        while k < len(linha):
            c = linha[k]
            if aspas:
                if c == "\\":
                    saida.append(linha[k:k + 2])
                    k += 2
                    continue
                if c == aspas:
                    aspas = ""
                saida.append(c)
                k += 1
                continue
            if c in "\"'":
                aspas = c
                saida.append(c)
                k += 1
                continue
            if c == "#" or linha.startswith("//", k):
                break
            saida.append(c)
            k += 1
        return "".join(saida)

    @staticmethod
    def _recuo(linha):
        if "\t" in _ESPACOS.match(linha).group(0):
            raise ErroDeConsulta(
                "há um tab na indentação desta consulta",
                dica="use espaços — a mesma regra da linguagem")
        return len(linha) - len(linha.lstrip(" "))

    def _bloco(self, inicio, recuo_pai):
        """As linhas indentadas abaixo de `inicio`, e onde o bloco termina."""
        corpo, i = [], inicio
        recuo_do_bloco = None
        while i < len(self.linhas):
            crua = self.linhas[i]
            if not self._sem_comentario(crua).strip():
                i += 1
                continue
            recuo = self._recuo(crua)
            if recuo <= recuo_pai:
                break
            if recuo_do_bloco is None:
                recuo_do_bloco = recuo
            elif recuo < recuo_do_bloco:
                break
            corpo.append(i)
            i += 1
        return corpo, i, recuo_do_bloco or (recuo_pai + 4)

    # ── operação e trecho ──────────────────────────────────

    def _ler_operacao(self, i):
        nua = self._sem_comentario(self.linhas[i]).strip()
        casou = _NOME.match(nua)
        if not casou or casou.group(0) not in OPERACOES:
            raise ErroDeConsulta(
                f"esperava 'busca', 'mudanca' ou 'assinatura', e veio "
                f"'{nua.split(':')[0].strip() or nua}'", i + 1, 1,
                dica="toda consulta começa por uma dessas três")
        especie = OPERACOES[casou.group(0)]
        resto = nua[casou.end():].strip()

        nome = None
        variaveis = {}
        casou_nome = _NOME.match(resto)
        if casou_nome:
            nome = casou_nome.group(0)
            resto = resto[casou_nome.end():].strip()
        if resto.startswith("("):
            fecha = _fechar(resto, 0, i + 1)
            variaveis = self._ler_variaveis(resto[1:fecha], i + 1)
            resto = resto[fecha + 1:].strip()
        if resto != ":":
            raise ErroDeConsulta(
                f"esperava ':' no fim da linha da {especie}", i + 1,
                len(self.linhas[i]),
                dica=f"escreva  {especie}:  e indente o que vem dentro")

        corpo, fim, recuo = self._bloco(i + 1, self._recuo(self.linhas[i]))
        if not corpo:
            raise ErroDeConsulta(
                f"esta {especie} não pede nada", i + 1, 1,
                dica="indente ao menos um campo abaixo dela")
        return Operacao(especie, nome, variaveis,
                        self._ler_selecoes(corpo, recuo), i + 1), fim

    def _ler_trecho(self, i):
        nua = self._sem_comentario(self.linhas[i]).strip()
        casou = re.match(r"trecho\s+(\w+)\s+em\s+(\w+)\s*:$", nua)
        if not casou:
            raise ErroDeConsulta(
                "um trecho se declara como  trecho Nome em Tipo:", i + 1, 1,
                dica="o 'em Tipo' diz a que tipo ele se aplica, e é o que "
                     "permite conferi-lo antes de rodar")
        corpo, fim, recuo = self._bloco(i + 1, self._recuo(self.linhas[i]))
        if not corpo:
            raise ErroDeConsulta(f"o trecho '{casou.group(1)}' está vazio",
                                 i + 1, 1)
        return Trecho(casou.group(1), casou.group(2),
                      self._ler_selecoes(corpo, recuo), i + 1), fim

    def _ler_variaveis(self, texto, linha):
        """'$id: Integer!, $limite: Integer := 3'."""
        variaveis = {}
        for parte in _dividir(texto, ","):
            parte = parte.strip()
            if not parte:
                continue
            casou = re.match(r"\$?(\w+)\s*:\s*(.+)$", parte)
            if not casou:
                raise ErroDeConsulta(
                    f"'{parte}' não é uma declaração de variável", linha, 1,
                    dica="escreva  $nome: Tipo  ou  $nome: Tipo := padrao")
            nome, resto = casou.group(1), casou.group(2).strip()
            padrao = _SEM
            if ":=" in resto:
                tipo_txt, _, padrao_txt = resto.partition(":=")
                resto = tipo_txt.strip()
                padrao = ler_valor(padrao_txt.strip(), linha, {})
            ler_tipo(resto)             # valida a notação já aqui
            variaveis[nome] = {"tipo": resto, "padrao": padrao}
        return variaveis

    # ── seleções ───────────────────────────────────────────

    def _ler_selecoes(self, indices, recuo):
        selecoes = []
        k = 0
        while k < len(indices):
            i = indices[k]
            crua = self.linhas[i]
            if self._recuo(crua) > recuo:
                raise ErroDeConsulta(
                    "esta linha está mais indentada que a irmã de cima, e a "
                    "de cima não abre bloco", i + 1, self._recuo(crua) + 1,
                    dica="um campo com seleção dentro termina em ':'")
            nua = self._sem_comentario(crua).strip()
            selecao, salto = self._ler_selecao(i, nua, recuo)
            selecoes.append(selecao)
            # Pula as linhas que já foram consumidas como corpo desta.
            k += 1
            while k < len(indices) and indices[k] < salto:
                k += 1
        return selecoes

    def _ler_selecao(self, i, nua, recuo):
        linha_num = i + 1

        # ── trecho ──
        if nua.startswith("..."):
            resto = nua[3:].strip()
            if resto.startswith("em ") or resto.startswith("em\t"):
                casou = re.match(r"em\s+(\w+)\s*:$", resto)
                if not casou:
                    raise ErroDeConsulta(
                        "um trecho condicional se escreve  ... em Tipo:",
                        linha_num, 1)
                corpo, fim, recuo_filho = self._bloco(i + 1, recuo)
                if not corpo:
                    raise ErroDeConsulta(
                        f"'... em {casou.group(1)}' não pede nada", linha_num, 1)
                return Selecao("...", "...", linha=linha_num,
                               tipo_condicional=casou.group(1),
                               selecoes=self._ler_selecoes(corpo, recuo_filho)), fim
            casou = _NOME.match(resto)
            if not casou or casou.end() != len(resto.rstrip()):
                raise ErroDeConsulta(
                    f"'...{resto}' não é o uso de um trecho", linha_num, 1,
                    dica="escreva  ...NomeDoTrecho  ou  ... em Tipo:")
            return Selecao("...", "...", linha=linha_num,
                           trecho=casou.group(0)), i + 1

        # ── apelido ──
        apelido = None
        casou = re.match(r"(\w+)\s*:\s*(\w.*)$", nua)
        if casou and not nua.rstrip().endswith(":"):
            apelido, nua = casou.group(1), casou.group(2).strip()
        elif casou and casou.group(2).strip() not in ("", ":"):
            # 'ana: usuario(id: 1):' — apelido E bloco.
            apelido, nua = casou.group(1), casou.group(2).strip()

        casou = _NOME.match(nua)
        if not casou:
            raise ErroDeConsulta(
                f"'{nua}' não é um nome de campo", linha_num,
                self._recuo(self.linhas[i]) + 1,
                dica="um campo é um nome, opcionalmente com (argumentos) e ':'")
        nome = casou.group(0)
        resto = nua[casou.end():].strip()

        argumentos = {}
        if resto.startswith("("):
            fecha = _fechar(resto, 0, linha_num)
            argumentos = ler_argumentos(resto[1:fecha], linha_num)
            resto = resto[fecha + 1:].strip()

        diretivas = []
        while resto.startswith("@"):
            casou_d = _NOME.match(resto[1:])
            if not casou_d:
                raise ErroDeConsulta("esperava o nome da diretiva depois de '@'",
                                     linha_num, 1)
            nome_d = casou_d.group(0)
            resto = resto[1 + casou_d.end():].strip()
            args_d = {}
            if resto.startswith("("):
                fecha = _fechar(resto, 0, linha_num)
                args_d = ler_argumentos(resto[1:fecha], linha_num)
                resto = resto[fecha + 1:].strip()
            diretivas.append({"nome": nome_d, "argumentos": args_d})

        if resto == ":":
            corpo, fim, recuo_filho = self._bloco(i + 1, recuo)
            if not corpo:
                raise ErroDeConsulta(
                    f"'{nome}' termina em ':' e não tem nada dentro",
                    linha_num, 1,
                    dica="ou indente os campos que quer dele, ou tire o ':'")
            return Selecao(nome, apelido, argumentos,
                           self._ler_selecoes(corpo, recuo_filho),
                           diretivas, linha_num), fim
        if resto:
            raise ErroDeConsulta(
                f"sobrou '{resto}' depois do campo '{nome}'", linha_num, 1,
                dica="um campo com seleção dentro termina em ':'")
        return Selecao(nome, apelido, argumentos, [], diretivas,
                       linha_num), i + 1


# ── valores ────────────────────────────────────────────────────

class _Sem:
    __slots__ = ()

    def __repr__(self):
        return "<ausente>"


_SEM = _Sem()
SEM = _SEM


class Variavel:
    """`$nome` dentro da consulta — resolvido na execução, não aqui."""

    __slots__ = ("nome",)

    def __init__(self, nome):
        self.nome = nome

    def __repr__(self):
        return f"${self.nome}"


def ler_argumentos(texto, linha):
    argumentos = {}
    for parte in _dividir(texto, ","):
        parte = parte.strip()
        if not parte:
            continue
        casou = re.match(r"(\w+)\s*:\s*(.*)$", parte, re.S)
        if not casou:
            raise ErroDeConsulta(
                f"'{parte}' não é um argumento", linha, 1,
                dica="escreva  nome: valor")
        argumentos[casou.group(1)] = ler_valor(casou.group(2).strip(), linha,
                                               argumentos)
    return argumentos


def ler_valor(texto, linha, _contexto):
    texto = texto.strip()
    if not texto:
        raise ErroDeConsulta("faltou o valor do argumento", linha, 1)

    if texto.startswith("$"):
        casou = _NOME.match(texto[1:])
        if not casou or casou.end() + 1 != len(texto):
            raise ErroDeConsulta(f"'{texto}' não é uma variável", linha, 1)
        return Variavel(casou.group(0))

    if texto[0] in "\"'":
        return _ler_texto(texto, linha)

    if texto.startswith("["):
        if not texto.endswith("]"):
            raise ErroDeConsulta(f"lista sem fechar: '{texto}'", linha, 1)
        return [ler_valor(p.strip(), linha, {})
                for p in _dividir(texto[1:-1], ",") if p.strip()]

    if texto.startswith("{"):
        if not texto.endswith("}"):
            raise ErroDeConsulta(f"vault sem fechar: '{texto}'", linha, 1)
        return ler_argumentos(texto[1:-1], linha)

    if texto in ("yes", "true"):
        return True
    if texto in ("no", "false"):
        return False
    if texto in ("void", "null"):
        return None

    casou = _NUMERO.match(texto)
    if casou and casou.end() == len(texto):
        bruto = casou.group(0)
        return float(bruto) if any(c in bruto for c in ".eE") else int(bruto)

    if _NOME.match(texto) and _NOME.match(texto).end() == len(texto):
        # Nome nu: é um membro de enum. Quem decide é o esquema, na
        # coerção — aqui ele viaja como texto, e um enum inexistente
        # vira erro com a lista dos que existem.
        return texto

    raise ErroDeConsulta(
        f"não entendi o valor '{texto}'", linha, 1,
        dica='texto entre aspas, número, yes/no/void, [lista], {vault}, '
             '$variavel ou um membro de enum')


def _ler_texto(texto, linha):
    aspas = texto[0]
    saida, k = [], 1
    while k < len(texto):
        c = texto[k]
        if c == "\\":
            if k + 1 >= len(texto):
                break
            seguinte = texto[k + 1]
            saida.append({"n": "\n", "t": "\t", "r": "\r",
                          "\\": "\\", '"': '"', "'": "'"}.get(seguinte, seguinte))
            k += 2
            continue
        if c == aspas:
            if k + 1 != len(texto.rstrip()):
                raise ErroDeConsulta(
                    f"sobrou algo depois do texto: '{texto[k + 1:]}'", linha, 1)
            return "".join(saida)
        saida.append(c)
        k += 1
    raise ErroDeConsulta(f"texto sem fechar: {texto}", linha, 1,
                         dica=f"falta um {aspas} no fim")


def _dividir(texto, separador):
    """Divide no separador, respeitando aspas, (), [] e {}."""
    partes, atual, nivel, aspas = [], [], 0, ""
    for k, c in enumerate(texto):
        if aspas:
            atual.append(c)
            if c == "\\":
                continue
            if c == aspas and texto[k - 1] != "\\":
                aspas = ""
            continue
        if c in "\"'":
            aspas = c
            atual.append(c)
            continue
        if c in "([{":
            nivel += 1
        elif c in ")]}":
            nivel -= 1
        if c == separador and nivel == 0:
            partes.append("".join(atual))
            atual = []
            continue
        atual.append(c)
    partes.append("".join(atual))
    return partes


def _fechar(texto, inicio, linha):
    """O índice do ')' que fecha o '(' em `inicio`."""
    nivel, aspas = 0, ""
    for k in range(inicio, len(texto)):
        c = texto[k]
        if aspas:
            if c == "\\":
                continue
            if c == aspas:
                aspas = ""
            continue
        if c in "\"'":
            aspas = c
            continue
        if c in "([{":
            nivel += 1
        elif c in ")]}":
            nivel -= 1
            if nivel == 0:
                return k
    raise ErroDeConsulta("faltou fechar o parêntese", linha, inicio + 1)


def ler(texto):
    return Leitor(texto).ler()
