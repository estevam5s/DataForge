"""
Arcane.Crypto — hashes, HMAC, codificações, bytes aleatórios e JWT.

Só primitivas da stdlib do Python. Não implementa criptografia de chave
pública nem cifras de bloco: para isso, use uma biblioteca dedicada.

O JWT mora aqui, e não num módulo próprio: um JWT **é** um HMAC sobre
dois pedaços de base64url, e as duas peças já estavam neste arquivo. Só
`HS256`, `HS384` e `HS512` — as de chave simétrica. `RS256` pede RSA, que
esta biblioteca não tem, e aceitar o nome sem fazer a conta seria pior que
recusar.
"""

import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
import time
import uuid

from ..builtins import _df_type as _nome_do_tipo
from ..errors import ValueError_


def _b64url(dados):
    """Base64url SEM o '=' do fim, como o JWT exige."""
    if isinstance(dados, str):
        dados = dados.encode("utf-8")
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode("ascii")


def _de_b64url(texto):
    """O contrário, repondo o '=' que o JWT tirou."""
    reposto = str(texto) + "=" * (-len(str(texto)) % 4)
    return base64.urlsafe_b64decode(reposto.encode("ascii"))


def _json_compacto(valor):
    """Sem espaço e com as chaves em ordem: dois tokens com a mesma carga
    precisam dar a MESMA assinatura."""
    return json.dumps(valor, separators=(",", ":"), sort_keys=True,
                      ensure_ascii=False)


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

            # ── JWT ──
            "jwt_assinar": cls._jwt_assinar,
            "jwt_verificar": cls._jwt_verificar,
            "jwt_ler": cls._jwt_ler,
            "jwt_algoritmos": lambda: sorted(cls.ALGORITMOS),
            "hmac_verify": cls._hmac_verify,

            # ── Senhas ──
            "pbkdf2": cls._pbkdf2,
            "hash_password": cls._hash_password,
            "verify_password": cls._verify_password,
            "precisa_rehash": cls._precisa_rehash,

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

    # ── JWT ──────────────────────────────────────────────────

    #: Os algoritmos que este módulo sabe fazer, e o hash de cada um.
    #:
    #: 'none' NÃO está aqui, e é o ponto: o JWT permite um token sem
    #: assinatura, e um verificador que aceita 'alg: none' aceita qualquer
    #: token que alguém escrever à mão. É a falha clássica da área.
    ALGORITMOS = {"HS256": "sha256", "HS384": "sha384", "HS512": "sha512"}

    @staticmethod
    def _jwt_assinar(carga, chave, algoritmo="HS256", expira_em=0):
        """Um token assinado. 'expira_em' é em SEGUNDOS a partir de agora.

        Segue a unidade do próprio JWT: 'exp' é um horário em segundos
        desde 1970, e usar milissegundos aqui — como 'sleep' faz — daria
        um token válido por 50 mil anos sem nada denunciando.
        """
        if not isinstance(carga, dict):
            raise ValueError(
                f"'jwt_assinar' precisa de um vault na carga, e recebeu "
                f"{_nome_do_tipo(carga)}")
        algoritmo = str(algoritmo).upper()
        if algoritmo not in ArcaneCrypto.ALGORITMOS:
            raise ValueError(
                f"'{algoritmo}' não é um algoritmo que este módulo assina. "
                f"Os que ele sabe: {', '.join(ArcaneCrypto.ALGORITMOS)}. "
                f"'RS256' pede RSA, que esta biblioteca não tem, e 'none' "
                f"não é assinatura nenhuma.")
        corpo = dict(carga)
        if expira_em:
            corpo["exp"] = int(time.time()) + int(expira_em)
        cabecalho = {"alg": algoritmo, "typ": "JWT"}
        partes = [_b64url(_json_compacto(cabecalho)),
                  _b64url(_json_compacto(corpo))]
        assinado = ".".join(partes)
        marca = hmac.new(_bytes(chave), assinado.encode("ascii"),
                         ArcaneCrypto.ALGORITMOS[algoritmo]).digest()
        return f"{assinado}.{_b64url(marca)}"

    @staticmethod
    def _jwt_verificar(token, chave, algoritmo="HS256"):
        """A carga do token, ou um erro dizendo por quê.

        Devolve vault: 'valido', 'carga', 'motivo'. Não levanta — um token
        inválido é o caso NORMAL de um servidor, e não uma exceção: quem
        recebe pedido de fora trata isso a cada requisição.
        """
        algoritmo = str(algoritmo).upper()
        pedacos = str(token).split(".")
        if len(pedacos) != 3:
            return {"valido": False, "carga": {},
                    "motivo": "o token não tem as três partes"}
        cabecalho_bruto, carga_bruta, marca = pedacos
        try:
            cabecalho = json.loads(_de_b64url(cabecalho_bruto))
            carga = json.loads(_de_b64url(carga_bruta))
        except Exception:                                 # noqa: BLE001
            return {"valido": False, "carga": {},
                    "motivo": "o token não é base64url com JSON dentro"}

        # O 'alg' do token NÃO decide o algoritmo: quem decide é quem
        # verifica. Ler dali é a falha clássica do JWT — um atacante troca
        # por 'none' (ou por um HMAC sobre a chave pública) e assina o que
        # quiser.
        if str(cabecalho.get("alg", "")).upper() != algoritmo:
            return {"valido": False, "carga": {},
                    "motivo": f"o token diz '{cabecalho.get('alg')}' e "
                              f"esperávamos '{algoritmo}'"}
        if algoritmo not in ArcaneCrypto.ALGORITMOS:
            return {"valido": False, "carga": {},
                    "motivo": f"'{algoritmo}' não é um algoritmo aceito"}

        esperado = hmac.new(_bytes(chave),
                            f"{cabecalho_bruto}.{carga_bruta}".encode("ascii"),
                            ArcaneCrypto.ALGORITMOS[algoritmo]).digest()
        if not hmac.compare_digest(_b64url(esperado), marca):
            return {"valido": False, "carga": {},
                    "motivo": "a assinatura não confere"}

        expira = carga.get("exp")
        if expira is not None:
            try:
                venceu = int(expira) < int(time.time())
            except (TypeError, ValueError):
                return {"valido": False, "carga": {},
                        "motivo": "o 'exp' do token não é um horário"}
            if venceu:
                # A carga vai junto: quem expirou precisa saber DE QUEM era
                # o token para renovar, e um vault vazio esconderia isso.
                return {"valido": False, "carga": carga,
                        "motivo": "o token venceu"}
        return {"valido": True, "carga": carga, "motivo": ""}

    @staticmethod
    def _jwt_ler(token):
        """A carga SEM verificar assinatura — para log e depuração.

        O nome diz o que ela não faz. Decidir acesso com isto é aceitar
        qualquer token que alguém escrever à mão.
        """
        pedacos = str(token).split(".")
        if len(pedacos) < 2:
            return {}
        try:
            return json.loads(_de_b64url(pedacos[1]))
        except Exception:                                 # noqa: BLE001
            return {}

    @staticmethod
    def _pbkdf2(senha, sal, iteracoes=200000, algoritmo="sha256"):
        derivada = hashlib.pbkdf2_hmac(algoritmo, _bytes(senha), _bytes(sal), iteracoes)
        return binascii.hexlify(derivada).decode("ascii")

    #: Os parametros de scrypt. N=2^15, r=8, p=1 sao os que o RFC 7914
    #: recomenda para login interativo, e custam ~32 MB por conferencia.
    #:
    #: O 'r' e o 'p' entram na string guardada junto do 'N': subir o
    #: custo no futuro nao pode invalidar o que ja esta no banco, e sem
    #: os tres numeros ali a conferencia teria de adivinhar com quais a
    #: senha foi derivada.
    SCRYPT_N = 1 << 15
    SCRYPT_R = 8
    SCRYPT_P = 1

    @staticmethod
    def _scrypt(senha, sal, n, r, p):
        derivada = hashlib.scrypt(_bytes(senha), salt=_bytes(sal),
                                  n=int(n), r=int(r), p=int(p), dklen=32,
                                  maxmem=(132 * int(n) * int(r)) + (1 << 22))
        return binascii.hexlify(derivada).decode("ascii")

    @staticmethod
    def _hash_password(senha, iteracoes=None, algoritmo="scrypt"):
        """Deriva a senha com sal aleatório. Guarde a string inteira.

        O padrão é **scrypt**, e a troca importa: PBKDF2 é barato de
        acelerar em GPU porque só faz hash em cadeia. O scrypt é
        *memory-hard* — ele exige ~32 MB por tentativa, e memória é o
        que uma GPU não tem em abundância por núcleo. Com os mesmos
        reais gastos, quem ataca consegue ordens de grandeza menos
        tentativas por segundo.

        `algoritmo := "pbkdf2"` volta ao anterior, para quem precisa
        conferir a senha em outro sistema que só tem PBKDF2.

        **Argon2id seria melhor ainda, e não está aqui**: em Python
        puro ele rodaria lento o bastante para ter de usar parâmetros
        fracos — o que o torna *pior* que o scrypt do `hashlib`, e não
        melhor. Esta é a escolha certa para uma linguagem sem
        dependência externa, e não a melhor do mundo.
        """
        sal = secrets.token_hex(16)
        alg = str(algoritmo).lower()
        if alg == "pbkdf2":
            voltas = int(iteracoes) if iteracoes else 200000
            derivada = ArcaneCrypto._pbkdf2(senha, sal, voltas)
            return f"pbkdf2_sha256${voltas}${sal}${derivada}"
        if alg != "scrypt":
            raise ValueError_(
                f"'{algoritmo}' nao e um algoritmo de senha.",
                0, 0, nota="Ha: 'scrypt' (padrao) e 'pbkdf2'.",
                dica="Para um resumo simples, use 'Crypto.sha256' — "
                     "mas nunca para senha.")
        n = int(iteracoes) if iteracoes else ArcaneCrypto.SCRYPT_N
        r, p = ArcaneCrypto.SCRYPT_R, ArcaneCrypto.SCRYPT_P
        derivada = ArcaneCrypto._scrypt(senha, sal, n, r, p)
        return f"scrypt${n}${r}${p}${sal}${derivada}"

    @staticmethod
    def _verify_password(senha, guardada):
        """Confere, e **continua aceitando o formato antigo**.

        Um banco tem senhas guardadas de antes da troca de algoritmo.
        Se `verify_password` só entendesse o formato novo, o dia da
        atualização seria o dia em que ninguém consegue entrar — e a
        saída de emergência seria mandar todo mundo redefinir a senha.

        O formato é auto-descritivo: o primeiro campo diz qual é, e os
        parâmetros vêm junto. É o que torna a próxima troca barata.
        """
        partes = str(guardada).split("$")
        try:
            if partes[0] == "scrypt":
                _, n, r, p, sal, esperada = partes
                derivada = ArcaneCrypto._scrypt(senha, sal, n, r, p)
            elif partes[0].startswith("pbkdf2"):
                _, iteracoes, sal, esperada = partes
                derivada = ArcaneCrypto._pbkdf2(senha, sal, int(iteracoes))
            else:
                return False
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(derivada, esperada)

    @staticmethod
    def _precisa_rehash(guardada):
        """Diz se a senha guardada usa parametro mais fraco que o de hoje.

        Sem isto, um banco fica para sempre no algoritmo com que nasceu:
        ninguem sabe quais linhas estao velhas, e nao ha momento em que
        a senha em claro esteja disponivel para regravar... exceto UM —
        o login bem-sucedido. E dai o uso:

            given Crypto.verify_password(senha, guardada):
                given Crypto.precisa_rehash(guardada):
                    gravar(Crypto.hash_password(senha))
        """
        partes = str(guardada).split("$")
        if partes[0] != "scrypt":
            return True
        try:
            return int(partes[1]) < ArcaneCrypto.SCRYPT_N
        except (ValueError, IndexError):
            return True

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
