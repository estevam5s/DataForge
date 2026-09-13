# -*- coding: utf-8 -*-
"""Arcane.Bytes — dados binarios: empacotar, ler e escrever byte a byte.

O que faltava
-------------
A linguagem tem o tipo `Bytes`, e nao tinha o que fazer com ele. Ler um
arquivo binario, falar um protocolo, montar um cabecalho de quatro
bytes — tudo isso pedia sair da linguagem.

As tres pecas, e o problema de cada uma:

    empacotar/desempacotar   o cabecalho de um protocolo e "um inteiro
                             de 4 bytes, big-endian, seguido de dois de
                             2" — escrito assim, e nao com contas
    Leitor / Escritor        ler um formato e avancar um cursor; fazer
                             isso com fatias exige acertar o indice a
                             cada campo, e um erro ali desalinha TUDO
                             o que vem depois
    janela                   olhar um pedaco sem copiar, porque copiar
                             um arquivo de 200 MB para ler 8 bytes e o
                             jeito mais facil de estourar a memoria

A ORDEM DOS BYTES e obrigatoria
-------------------------------
`empacotar("i32", 1)` nao existe aqui: o formato sempre diz a ordem.
Um inteiro escrito na ordem da MAQUINA e lido na ordem da rede da um
numero diferente, o programa nao falha, e o dado sai errado do outro
lado — que e a falha mais cara desta area inteira.

    empacotar(">i32", 1)    00 00 00 01    ordem de rede (big-endian)
    empacotar("<i32", 1)    01 00 00 00    ordem do Intel (little)
"""

import base64
import binascii
import struct


class ErroDeBytes(Exception):
    pass


#: Os tipos que um formato aceita, e o que cada um vale em `struct`.
#:
#: Os nomes dizem o TAMANHO em bits, e nao uma letra. 'i32' e um
#: inteiro de 32 bits em qualquer maquina; 'int' do C nao e — e
#: descobrir isso depois de gravar um arquivo e caro.
TIPOS = {
    "i8": ("b", 1), "u8": ("B", 1),
    "i16": ("h", 2), "u16": ("H", 2),
    "i32": ("i", 4), "u32": ("I", 4),
    "i64": ("q", 8), "u64": ("Q", 8),
    "f32": ("f", 4), "f64": ("d", 8),
    "bool": ("?", 1),
}

ORDENS = {">": ">", "<": "<", "!": ">", "rede": ">", "maquina": "="}


def _traduzir(formato):
    """'>i32 u16 u16' vira o formato do struct, com a ordem na frente."""
    texto = str(formato).strip()
    if not texto:
        raise ErroDeBytes(
            "o formato esta vazio.\n"
            "  Escreva a ordem e os campos:  '>i32 u16'\n"
            "  '>' e ordem de rede (big-endian), '<' e a do Intel.")

    ordem = None
    if texto[0] in ORDENS:
        ordem, texto = ORDENS[texto[0]], texto[1:].strip()

    if ordem is None:
        raise ErroDeBytes(
            f"o formato '{formato}' nao diz a ORDEM DOS BYTES.\n"
            f"  Comece com '>' (rede) ou '<' (Intel):  '>{texto}'\n"
            f"  Sem a ordem, o mesmo numero escrito numa maquina e lido\n"
            f"  em outra da um valor diferente — e o programa nao falha.")

    partes = []
    for campo in texto.replace(",", " ").split():
        if campo in TIPOS:
            partes.append(TIPOS[campo][0])
            continue
        if campo.startswith("bytes"):
            # 'bytes16' — um bloco de tamanho fixo.
            resto = campo[5:]
            if not resto.isdigit():
                raise ErroDeBytes(
                    f"'{campo}' precisa do tamanho: 'bytes16'")
            partes.append(f"{resto}s")
            continue
        raise ErroDeBytes(
            f"nao conheco o tipo '{campo}'.\n"
            f"  Ha: {', '.join(sorted(TIPOS))}, e 'bytesN' para bloco fixo.")
    if not partes:
        raise ErroDeBytes(f"o formato '{formato}' nao tem nenhum campo")
    return ordem + "".join(partes)


def empacotar(formato, *valores):
    """Os valores viram bytes, na ordem e nos tamanhos declarados."""
    if len(valores) == 1 and isinstance(valores[0], (list, tuple)):
        valores = tuple(valores[0])
    molde = _traduzir(formato)
    esperado = len(struct.unpack(molde, b"\x00" * struct.calcsize(molde)))
    if len(valores) != esperado:
        raise ErroDeBytes(
            f"o formato '{formato}' tem {esperado} campo(s) e recebeu "
            f"{len(valores)} valor(es)")
    try:
        return struct.pack(molde, *[_preparar(v) for v in valores])
    except struct.error as erro:
        raise ErroDeBytes(f"{erro} — formato '{formato}'") from None


def _preparar(valor):
    if isinstance(valor, str):
        return valor.encode("utf-8")
    return valor


def desempacotar(formato, dados):
    """Os bytes viram os valores. Exige o tamanho EXATO."""
    molde = _traduzir(formato)
    precisa = struct.calcsize(molde)
    dados = _como_bytes(dados)
    if len(dados) != precisa:
        raise ErroDeBytes(
            f"o formato '{formato}' pede {precisa} byte(s) e recebeu "
            f"{len(dados)}.\n"
            f"  Para ler o comeco de um bloco maior, use "
            f"'Bytes.ler(dados)' e peca campo a campo.")
    return list(struct.unpack(molde, dados))


def tamanho(formato):
    """Quantos bytes este formato ocupa."""
    return struct.calcsize(_traduzir(formato))


def _como_bytes(valor):
    if isinstance(valor, (bytes, bytearray)):
        return bytes(valor)
    if isinstance(valor, memoryview):
        return valor.tobytes()
    if isinstance(valor, str):
        return valor.encode("utf-8")
    if isinstance(valor, (list, tuple)):
        return bytes(valor)
    raise ErroDeBytes(
        f"esperava bytes e veio {type(valor).__name__}")


# ══════════════════════════════════════════════════════════════
#  Leitor — um cursor que anda
# ══════════════════════════════════════════════════════════════

class Leitor:
    """Le um formato campo a campo, sem acertar indice a mao.

    Ler com fatias exige calcular o deslocamento de cada campo, e um
    erro num deles desalinha tudo o que vem depois — com o programa
    entregando numeros plausiveis e errados. O cursor anda sozinho.
    """

    def __init__(self, dados, ordem=">"):
        self.dados = _como_bytes(dados)
        self.posicao = 0
        self.ordem = ORDENS.get(ordem, ">")

    def ler(self, tipo, quantos=None):
        if quantos is not None:
            return [self.ler(tipo) for _ in range(quantos)]
        formato = self.ordem + ("" if tipo in TIPOS else "")
        if tipo in TIPOS:
            letra, largura = TIPOS[tipo]
            self._exigir(largura, tipo)
            valor = struct.unpack_from(self.ordem + letra, self.dados,
                                       self.posicao)[0]
            self.posicao += largura
            return valor
        if tipo.startswith("bytes"):
            largura = int(tipo[5:])
            self._exigir(largura, tipo)
            pedaco = self.dados[self.posicao:self.posicao + largura]
            self.posicao += largura
            return pedaco
        raise ErroDeBytes(f"nao conheco o tipo '{tipo}'")

    def ler_bytes(self, quantos):
        self._exigir(quantos, f"bytes{quantos}")
        pedaco = self.dados[self.posicao:self.posicao + quantos]
        self.posicao += quantos
        return pedaco

    def ler_texto(self, quantos, codificacao="utf-8"):
        return self.ler_bytes(quantos).decode(codificacao, "replace")

    def ler_ate_zero(self, codificacao="utf-8"):
        """O texto terminado em zero, como num formato antigo."""
        fim = self.dados.find(b"\x00", self.posicao)
        if fim < 0:
            raise ErroDeBytes(
                f"nao achei o zero terminador a partir do byte "
                f"{self.posicao}")
        texto = self.dados[self.posicao:fim].decode(codificacao, "replace")
        self.posicao = fim + 1
        return texto

    def pular(self, quantos):
        self.posicao = min(len(self.dados), self.posicao + quantos)
        return self

    def ir_para(self, posicao):
        if not 0 <= posicao <= len(self.dados):
            raise ErroDeBytes(
                f"a posicao {posicao} esta fora dos {len(self.dados)} bytes")
        self.posicao = posicao
        return self

    def espiar(self, quantos=1):
        """Olha sem andar. Para decidir o que vem a seguir."""
        return self.dados[self.posicao:self.posicao + quantos]

    @property
    def sobrou(self):
        return len(self.dados) - self.posicao

    @property
    def acabou(self):
        return self.posicao >= len(self.dados)

    def resto(self):
        pedaco = self.dados[self.posicao:]
        self.posicao = len(self.dados)
        return pedaco

    def _exigir(self, quantos, tipo):
        if self.posicao + quantos > len(self.dados):
            raise ErroDeBytes(
                f"faltam bytes para ler '{tipo}': o cursor esta em "
                f"{self.posicao}, o campo pede {quantos} e so ha "
                f"{self.sobrou} ate o fim.")

    def __repr__(self):
        return f"<leitor {self.posicao}/{len(self.dados)}>"


def ler(dados, ordem=">"):
    return Leitor(dados, ordem)


# ══════════════════════════════════════════════════════════════
#  Escritor
# ══════════════════════════════════════════════════════════════

class Escritor:
    """Monta um bloco binario campo a campo."""

    def __init__(self, ordem=">"):
        self.partes = []
        self.ordem = ORDENS.get(ordem, ">")

    def escrever(self, tipo, valor):
        if tipo in TIPOS:
            letra, _ = TIPOS[tipo]
            try:
                self.partes.append(struct.pack(self.ordem + letra, valor))
            except struct.error as erro:
                raise ErroDeBytes(
                    f"{valor!r} nao cabe em '{tipo}': {erro}") from None
            return self
        if tipo.startswith("bytes"):
            largura = int(tipo[5:])
            bruto = _como_bytes(valor)[:largura]
            self.partes.append(bruto.ljust(largura, b"\x00"))
            return self
        raise ErroDeBytes(f"nao conheco o tipo '{tipo}'")

    def escrever_bytes(self, dados):
        self.partes.append(_como_bytes(dados))
        return self

    def escrever_texto(self, texto, codificacao="utf-8", com_zero=False):
        self.partes.append(str(texto).encode(codificacao))
        if com_zero:
            self.partes.append(b"\x00")
        return self

    def finalizar(self):
        return b"".join(self.partes)

    @property
    def tamanho(self):
        return sum(len(p) for p in self.partes)

    def __repr__(self):
        return f"<escritor {self.tamanho} bytes>"


def escrever(ordem=">"):
    return Escritor(ordem)


# ══════════════════════════════════════════════════════════════
#  Janela — olhar sem copiar
# ══════════════════════════════════════════════════════════════

def janela(dados, inicio=0, fim=None):
    """Um pedaco que NAO copia.

    Copiar um arquivo de 200 MB para ler 8 bytes e o jeito mais facil
    de estourar a memoria. A janela aponta para os mesmos bytes.
    """
    bruto = dados if isinstance(dados, (bytes, bytearray, memoryview)) \
        else _como_bytes(dados)
    vista = memoryview(bruto)
    return vista[inicio:] if fim is None else vista[inicio:fim]


def copiar(vista):
    """A janela vira bytes de verdade, quando for preciso guardar."""
    return bytes(vista)


# ══════════════════════════════════════════════════════════════
#  Conversao
# ══════════════════════════════════════════════════════════════

def de_texto(texto, codificacao="utf-8"):
    return str(texto).encode(codificacao)


def para_texto(dados, codificacao="utf-8", estrito=False):
    """Bytes viram texto. Sem 'estrito', o que nao decodifica vira '?'.

    O padrao e tolerante de proposito: quase todo uso e mostrar o que
    chegou, e derrubar o programa por um byte invalido no meio de um
    log e pior que mostrar o log com um caractere trocado.
    """
    return _como_bytes(dados).decode(codificacao,
                                     "strict" if estrito else "replace")


def hex(dados, separador=""):
    return _como_bytes(dados).hex(separador) if separador \
        else _como_bytes(dados).hex()


def de_hex(texto):
    limpo = "".join(str(texto).split()).replace(":", "")
    try:
        return bytes.fromhex(limpo)
    except ValueError as erro:
        raise ErroDeBytes(f"'{texto}' nao e hexadecimal: {erro}") from None


def base64_(dados):
    return base64.b64encode(_como_bytes(dados)).decode("ascii")


def de_base64(texto):
    try:
        return base64.b64decode(str(texto), validate=True)
    except (binascii.Error, ValueError) as erro:
        raise ErroDeBytes(f"base64 invalido: {erro}") from None


def bits(dados):
    """A representacao em bits, para olhar um protocolo de perto."""
    return " ".join(f"{b:08b}" for b in _como_bytes(dados))


def de_bits(texto):
    limpo = "".join(str(texto).split())
    if len(limpo) % 8:
        raise ErroDeBytes(
            f"{len(limpo)} bits nao formam bytes inteiros — falta "
            f"{8 - len(limpo) % 8}")
    return bytes(int(limpo[i:i + 8], 2) for i in range(0, len(limpo), 8))


def despejo(dados, por_linha=16):
    """O 'hexdump': o que se olha quando o protocolo nao bate.

    Tres colunas — posicao, hexadecimal e o texto legivel. E a forma de
    ver o byte a mais que desalinhou tudo.
    """
    bruto = _como_bytes(dados)
    linhas = []
    for i in range(0, len(bruto), por_linha):
        pedaco = bruto[i:i + por_linha]
        hexa = " ".join(f"{b:02x}" for b in pedaco)
        texto = "".join(chr(b) if 32 <= b < 127 else "." for b in pedaco)
        linhas.append(f"{i:08x}  {hexa:<{por_linha * 3}} |{texto}|")
    return "\n".join(linhas)


# ══════════════════════════════════════════════════════════════
#  Operacoes
# ══════════════════════════════════════════════════════════════

def concatenar(*pedacos):
    if len(pedacos) == 1 and isinstance(pedacos[0], (list, tuple)):
        pedacos = pedacos[0]
    return b"".join(_como_bytes(p) for p in pedacos)


def fatiar(dados, inicio=0, fim=None):
    bruto = _como_bytes(dados)
    return bruto[inicio:] if fim is None else bruto[inicio:fim]


def ou_exclusivo(a, b):
    """XOR byte a byte. O menor manda no tamanho."""
    x, y = _como_bytes(a), _como_bytes(b)
    return bytes(i ^ j for i, j in zip(x, y))


def igual_em_tempo_fixo(a, b):
    """Compara sem vazar ONDE diferiu.

    Uma comparacao comum para no primeiro byte diferente, e o TEMPO
    conta quantos bateram. Com isso, um atacante descobre um token byte
    a byte. Para segredo, so esta.
    """
    import hmac
    return hmac.compare_digest(_como_bytes(a), _como_bytes(b))


def preencher(dados, tamanho_final, com=b"\x00", a_esquerda=False):
    bruto = _como_bytes(dados)
    enchimento = _como_bytes(com)[:1] or b"\x00"
    if len(bruto) >= tamanho_final:
        return bruto
    falta = enchimento * (tamanho_final - len(bruto))
    return falta + bruto if a_esquerda else bruto + falta


def achar(dados, agulha, desde=0):
    return _como_bytes(dados).find(_como_bytes(agulha), desde)


def dividir(dados, separador):
    return _como_bytes(dados).split(_como_bytes(separador))


def inverter(dados):
    return _como_bytes(dados)[::-1]


class ArcaneBytes:
    """O dicionario que `adopt Arcane.Bytes` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Bytes",

            # ── Empacotar ──
            "empacotar": empacotar,
            "desempacotar": desempacotar,
            "tamanho": tamanho,
            "tipos": lambda: sorted(TIPOS),

            # ── Cursor ──
            "ler": ler,
            "escrever": escrever,

            # ── Sem copiar ──
            "janela": janela,
            "copiar": copiar,

            # ── Conversao ──
            "de_texto": de_texto,
            "para_texto": para_texto,
            "hex": hex,
            "de_hex": de_hex,
            "base64": base64_,
            "de_base64": de_base64,
            "bits": bits,
            "de_bits": de_bits,
            "despejo": despejo,

            # ── Operacoes ──
            "concatenar": concatenar,
            "fatiar": fatiar,
            "ou_exclusivo": ou_exclusivo,
            "igual_em_tempo_fixo": igual_em_tempo_fixo,
            "preencher": preencher,
            "achar": achar,
            "dividir": dividir,
            "inverter": inverter,
        }
