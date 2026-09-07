"""
Arcane.Crypto — hashes, HMAC, codificações e bytes aleatórios seguros.

Só primitivas da stdlib do Python. Não implementa criptografia de chave
pública nem cifras de bloco: para isso, use uma biblioteca dedicada.
"""

import base64
import binascii
import hashlib
import hmac
import os
import secrets
import uuid


def _bytes(valor):
    if isinstance(valor, bytes):
        return valor
    if isinstance(valor, (list, tuple)):
        return bytes(valor)
    return str(valor).encode("utf-8")


class ArcaneCrypto:
    """Hashes, HMAC, codificações e aleatoriedade segura."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Crypto",

            # ── Hashes ──
            "md5": lambda v: hashlib.md5(_bytes(v)).hexdigest(),
            "sha1": lambda v: hashlib.sha1(_bytes(v)).hexdigest(),
            "sha224": lambda v: hashlib.sha224(_bytes(v)).hexdigest(),
            "sha256": lambda v: hashlib.sha256(_bytes(v)).hexdigest(),
            "sha384": lambda v: hashlib.sha384(_bytes(v)).hexdigest(),
            "sha512": lambda v: hashlib.sha512(_bytes(v)).hexdigest(),
            "blake2b": lambda v: hashlib.blake2b(_bytes(v)).hexdigest(),
            "blake2s": lambda v: hashlib.blake2s(_bytes(v)).hexdigest(),
            "hash": cls._hash,
            "hash_file": cls._hash_file,
            "algorithms": lambda: sorted(hashlib.algorithms_guaranteed),

            # ── HMAC ──
            "hmac": cls._hmac,
            "hmac_verify": cls._hmac_verify,

            # ── Senhas ──
            "pbkdf2": cls._pbkdf2,
            "hash_password": cls._hash_password,
            "verify_password": cls._verify_password,

            # ── Codificações ──
            "base64_encode": lambda v: base64.b64encode(_bytes(v)).decode("ascii"),
            "base64_decode": cls._base64_decode,
            "base64url_encode": lambda v: base64.urlsafe_b64encode(
                _bytes(v)).decode("ascii").rstrip("="),
            "base64url_decode": cls._base64url_decode,
            "base32_encode": lambda v: base64.b32encode(_bytes(v)).decode("ascii"),
            "base32_decode": lambda v: base64.b32decode(v).decode("utf-8", "replace"),
            "hex_encode": lambda v: binascii.hexlify(_bytes(v)).decode("ascii"),
            "hex_decode": lambda v: binascii.unhexlify(v).decode("utf-8", "replace"),

            # ── Aleatoriedade segura ──
            "random_bytes": lambda n=32: list(secrets.token_bytes(n)),
            "random_hex": lambda n=32: secrets.token_hex(n),
            "random_token": lambda n=32: secrets.token_urlsafe(n),
            "random_int": lambda a, b: secrets.randbelow(b - a + 1) + a,
            "random_choice": lambda itens: secrets.choice(list(itens)),
            "random_password": cls._random_password,

            # ── Identificadores ──
            "uuid": lambda: str(uuid.uuid4()),
            "uuid4": lambda: str(uuid.uuid4()),
            "uuid_hex": lambda: uuid.uuid4().hex,
            "short_id": lambda n=12: secrets.token_urlsafe(n)[:n],

            # ── Comparação ──
            "constant_time_equals": lambda a, b: secrets.compare_digest(
                str(a).encode(), str(b).encode()),

            # ── Ofuscação simples (NÃO é criptografia) ──
            "xor_cipher": cls._xor,
            "rot13": lambda t: str(t).translate(str.maketrans(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm")),
            "mask": cls._mask,
        }

    @staticmethod
    def _hash(valor, algoritmo="sha256"):
        try:
            h = hashlib.new(algoritmo)
        except ValueError:
            raise ValueError(
                f"Algoritmo desconhecido: {algoritmo}. "
                f"Disponíveis: {', '.join(sorted(hashlib.algorithms_guaranteed))}")
        h.update(_bytes(valor))
        return h.hexdigest()

    @staticmethod
    def _hash_file(caminho, algoritmo="sha256"):
        h = hashlib.new(algoritmo)
        with open(caminho, "rb") as f:
            for bloco in iter(lambda: f.read(65536), b""):
                h.update(bloco)
        return h.hexdigest()

    @staticmethod
    def _hmac(chave, mensagem, algoritmo="sha256"):
        return hmac.new(_bytes(chave), _bytes(mensagem), algoritmo).hexdigest()

    @staticmethod
    def _hmac_verify(chave, mensagem, assinatura, algoritmo="sha256"):
        esperado = hmac.new(_bytes(chave), _bytes(mensagem), algoritmo).hexdigest()
        return hmac.compare_digest(esperado, str(assinatura))

    @staticmethod
    def _pbkdf2(senha, sal, iteracoes=200000, algoritmo="sha256"):
        derivada = hashlib.pbkdf2_hmac(algoritmo, _bytes(senha), _bytes(sal), iteracoes)
        return binascii.hexlify(derivada).decode("ascii")

    @staticmethod
    def _hash_password(senha, iteracoes=200000):
        """Deriva a senha com sal aleatório. Guarde a string inteira."""
        sal = secrets.token_hex(16)
        derivada = ArcaneCrypto._pbkdf2(senha, sal, iteracoes)
        return f"pbkdf2_sha256${iteracoes}${sal}${derivada}"

    @staticmethod
    def _verify_password(senha, guardada):
        try:
            _, iteracoes, sal, esperada = str(guardada).split("$")
        except ValueError:
            return False
        derivada = ArcaneCrypto._pbkdf2(senha, sal, int(iteracoes))
        return hmac.compare_digest(derivada, esperada)

    @staticmethod
    def _base64_decode(texto):
        faltando = len(texto) % 4
        if faltando:
            texto += "=" * (4 - faltando)
        return base64.b64decode(texto).decode("utf-8", "replace")

    @staticmethod
    def _base64url_decode(texto):
        faltando = len(texto) % 4
        if faltando:
            texto += "=" * (4 - faltando)
        return base64.urlsafe_b64decode(texto).decode("utf-8", "replace")

    @staticmethod
    def _random_password(tamanho=16, simbolos=True):
        alfabeto = ("abcdefghijklmnopqrstuvwxyz"
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        if simbolos:
            alfabeto += "!@#$%&*_-+="
        return "".join(secrets.choice(alfabeto) for _ in range(tamanho))

    @staticmethod
    def _xor(texto, chave):
        dados = _bytes(texto)
        k = _bytes(chave)
        if not k:
            raise ValueError("a chave não pode ser vazia")
        return list(bytes(b ^ k[i % len(k)] for i, b in enumerate(dados)))

    @staticmethod
    def _mask(texto, visiveis=4, caractere="*"):
        texto = str(texto)
        if len(texto) <= visiveis:
            return caractere * len(texto)
        return caractere * (len(texto) - visiveis) + texto[-visiveis:]
