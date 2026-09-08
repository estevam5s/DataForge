"""
BSON — o formato binario do MongoDB.

Um documento BSON e: tamanho total (4 bytes), os campos, e um zero.
Cada campo e: um byte de tipo, o nome terminado em zero, e o valor no
formato daquele tipo. Tudo little-endian.

Sao ~20 tipos, e o Mongo usa uns dez. O que importa e a ida e a volta
serem exatas: um documento que sai e volta diferente corrompe dados
sem avisar, e o erro so aparece quando alguem le.
"""

import datetime
import os
import re
import struct
import time

from ...errors import SerializationError


# ── tipos ──
DOUBLE = 0x01
STRING = 0x02
DOCUMENTO = 0x03
ARRANJO = 0x04
BINARIO = 0x05
OBJECTID = 0x07
BOOLEANO = 0x08
DATA = 0x09
NULO = 0x0A
REGEX = 0x0B
JAVASCRIPT = 0x0D
INT32 = 0x10
TIMESTAMP = 0x11
INT64 = 0x12
DECIMAL128 = 0x13
MIN_KEY = 0xFF
MAX_KEY = 0x7F


class ObjectId:
    """O identificador de 12 bytes do MongoDB.

    Quatro de tempo, cinco aleatorios por processo, tres de contador.
    O tempo na frente e o que faz os ids nascerem quase ordenados —
    e por isso que o indice do '_id' nao fragmenta.
    """

    _aleatorio = os.urandom(5)
    _contador = int.from_bytes(os.urandom(3), "big")

    __slots__ = ("bytes",)

    def __init__(self, valor=None):
        if valor is None:
            ObjectId._contador = (ObjectId._contador + 1) % 0xFFFFFF
            self.bytes = (int(time.time()).to_bytes(4, "big")
                          + ObjectId._aleatorio
                          + ObjectId._contador.to_bytes(3, "big"))
        elif isinstance(valor, bytes):
            self.bytes = valor
        elif isinstance(valor, ObjectId):
            self.bytes = valor.bytes
        else:
            texto = str(valor)
            if len(texto) != 24:
                raise SerializationError(
                    f"'{texto}' is not an ObjectId: it must be 24 hex digits.",
                    doc="banco-de-dados")
            self.bytes = bytes.fromhex(texto)

    @property
    def criado_em(self):
        return datetime.datetime.fromtimestamp(
            int.from_bytes(self.bytes[:4], "big"), datetime.timezone.utc)

    def __str__(self):
        return self.bytes.hex()

    def __repr__(self):
        return f"ObjectId('{self.bytes.hex()}')"

    def __eq__(self, outro):
        if isinstance(outro, ObjectId):
            return self.bytes == outro.bytes
        return str(self) == str(outro)

    def __hash__(self):
        return hash(self.bytes)


# ─────────────────────────────────────────────────────────────
#  Escrita
# ─────────────────────────────────────────────────────────────

def _cstr(texto):
    bruto = texto.encode("utf-8")
    if b"\x00" in bruto:
        raise SerializationError(
            "a BSON field name cannot contain a zero byte.",
            doc="banco-de-dados")
    return bruto + b"\x00"


def _texto(valor):
    bruto = valor.encode("utf-8")
    return struct.pack("<i", len(bruto) + 1) + bruto + b"\x00"


def _campo(nome, valor):
    """Um campo: tipo, nome, valor."""
    chave = _cstr(str(nome))

    if valor is None:
        return bytes([NULO]) + chave
    if isinstance(valor, bool):
        return bytes([BOOLEANO]) + chave + (b"\x01" if valor else b"\x00")
    if isinstance(valor, ObjectId):
        return bytes([OBJECTID]) + chave + valor.bytes
    if isinstance(valor, int):
        # O tamanho segue o valor: um contador que passa de 2^31 nao
        # pode virar negativo silenciosamente.
        if -2**31 <= valor < 2**31:
            return bytes([INT32]) + chave + struct.pack("<i", valor)
        if -2**63 <= valor < 2**63:
            return bytes([INT64]) + chave + struct.pack("<q", valor)
        raise SerializationError(
            f"{valor} does not fit a 64-bit integer, which is BSON's largest.",
            dica="store it as text if the exact value matters",
            doc="banco-de-dados")
    if isinstance(valor, float):
        return bytes([DOUBLE]) + chave + struct.pack("<d", valor)
    if isinstance(valor, str):
        return bytes([STRING]) + chave + _texto(valor)
    if isinstance(valor, bytes):
        return (bytes([BINARIO]) + chave
                + struct.pack("<i", len(valor)) + b"\x00" + valor)
    if isinstance(valor, dict):
        return bytes([DOCUMENTO]) + chave + codificar(valor)
    if isinstance(valor, (list, tuple)):
        # Um arranjo BSON e um documento cujas chaves sao "0", "1", "2".
        return (bytes([ARRANJO]) + chave
                + codificar({str(i): v for i, v in enumerate(valor)}))
    if isinstance(valor, datetime.datetime):
        ms = int(valor.timestamp() * 1000)
        return bytes([DATA]) + chave + struct.pack("<q", ms)
    if isinstance(valor, re.Pattern):
        opcoes = ""
        if valor.flags & re.I:
            opcoes += "i"
        if valor.flags & re.M:
            opcoes += "m"
        if valor.flags & re.S:
            opcoes += "s"
        if valor.flags & re.X:
            opcoes += "x"
        return bytes([REGEX]) + chave + _cstr(valor.pattern) + _cstr(opcoes)

    raise SerializationError(
        f"BSON has no type for {type(valor).__name__}.",
        nota=f"the value was: {valor!r}"[:120],
        dica="convert it to text, number, cluster or vault first",
        doc="banco-de-dados")


def codificar(documento):
    """Um vault vira BSON."""
    if not isinstance(documento, dict):
        raise SerializationError(
            f"BSON encodes a Vault, not {type(documento).__name__}.",
            doc="banco-de-dados")
    corpo = b"".join(_campo(k, v) for k, v in documento.items())
    return struct.pack("<i", len(corpo) + 5) + corpo + b"\x00"


# ─────────────────────────────────────────────────────────────
#  Leitura
# ─────────────────────────────────────────────────────────────

def _ler_cstr(dados, i):
    fim = dados.index(b"\x00", i)
    return dados[i:fim].decode("utf-8", "replace"), fim + 1


def _ler_texto(dados, i):
    n = struct.unpack_from("<i", dados, i)[0]
    i += 4
    return dados[i:i + n - 1].decode("utf-8", "replace"), i + n


def _ler_valor(tipo, dados, i):
    if tipo == DOUBLE:
        return struct.unpack_from("<d", dados, i)[0], i + 8
    if tipo == STRING or tipo == JAVASCRIPT:
        return _ler_texto(dados, i)
    if tipo == DOCUMENTO:
        n = struct.unpack_from("<i", dados, i)[0]
        return decodificar(dados[i:i + n]), i + n
    if tipo == ARRANJO:
        n = struct.unpack_from("<i", dados, i)[0]
        interno = decodificar(dados[i:i + n])
        # As chaves sao "0", "1", "2": voltam a ser um cluster.
        return [interno[k] for k in sorted(interno, key=int)], i + n
    if tipo == BINARIO:
        n = struct.unpack_from("<i", dados, i)[0]
        subtipo = dados[i + 4]
        bruto = dados[i + 5:i + 5 + n]
        return bruto, i + 5 + n
    if tipo == OBJECTID:
        return ObjectId(dados[i:i + 12]), i + 12
    if tipo == BOOLEANO:
        return dados[i] == 1, i + 1
    if tipo == DATA:
        ms = struct.unpack_from("<q", dados, i)[0]
        return datetime.datetime.fromtimestamp(
            ms / 1000, datetime.timezone.utc), i + 8
    if tipo == NULO:
        return None, i
    if tipo == REGEX:
        padrao, i = _ler_cstr(dados, i)
        opcoes, i = _ler_cstr(dados, i)
        return {"$regex": padrao, "$options": opcoes}, i
    if tipo == INT32:
        return struct.unpack_from("<i", dados, i)[0], i + 4
    if tipo == TIMESTAMP:
        return struct.unpack_from("<Q", dados, i)[0], i + 8
    if tipo == INT64:
        return struct.unpack_from("<q", dados, i)[0], i + 8
    if tipo == DECIMAL128:
        # Nao ha decimal de 128 bits no Python; devolver texto e melhor
        # que um float que perde digitos em silencio — que e o unico
        # motivo de alguem usar decimal128.
        return {"$numberDecimal": dados[i:i + 16].hex()}, i + 16
    if tipo in (MIN_KEY, MAX_KEY):
        return {"$minKey" if tipo == MIN_KEY else "$maxKey": 1}, i

    raise SerializationError(
        f"unknown BSON type: 0x{tipo:02x}",
        nota="the server may be speaking a newer BSON",
        doc="banco-de-dados")


def decodificar(dados):
    """BSON vira vault."""
    if len(dados) < 5:
        return {}
    documento = {}
    i = 4                                            # pula o tamanho
    while i < len(dados) - 1:
        tipo = dados[i]
        i += 1
        if tipo == 0:
            break
        nome, i = _ler_cstr(dados, i)
        documento[nome], i = _ler_valor(tipo, dados, i)
    return documento


def para_json(valor):
    """O documento em tipos que o DataForge imprime bem.

    ObjectId vira texto e data vira ISO: sem isso, 'out documento'
    mostra '<ObjectId object at 0x...>', que nao ajuda ninguem.
    """
    if isinstance(valor, ObjectId):
        return str(valor)
    if isinstance(valor, datetime.datetime):
        return valor.isoformat()
    if isinstance(valor, bytes):
        return valor.hex()
    if isinstance(valor, dict):
        return {k: para_json(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [para_json(v) for v in valor]
    return valor
