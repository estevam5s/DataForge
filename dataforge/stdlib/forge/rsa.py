"""
RSA-OAEP, so o lado publico — o suficiente para o MySQL 8.

O 'caching_sha2_password' do MySQL 8 exige, quando o cache do servidor
nao tem a senha, que ela viaje cifrada com a chave publica dele. Sem
isso, conectar num MySQL 8 recem-instalado por canal sem TLS
simplesmente nao funciona — e e onde a maioria dos drivers caseiros
para.

─── Por que isto e seguro de escrever ──────────────────────

"Nao escreva sua propria criptografia" e um bom conselho, e vale
principalmente para o que guarda segredo: geracao de chave, assinatura,
decifracao. Nenhum deles esta aqui.

O que esta e a operacao **publica**: pegar uma mensagem, aplicar o
padding OAEP e elevar a mensagem a 'e' modulo 'n'. Tres razoes de isso
ser diferente:

  1. Nao ha segredo nosso no calculo. A chave e publica — o servidor a
     manda em texto claro. Nao ha nada para vazar por canal lateral,
     porque nao ha nada secreto sendo manipulado alem da mensagem, que
     e curta e de tempo constante aqui.

  2. 'pow(m, e, n)' e a exponenciacao modular do proprio Python,
     escrita em C e usada por toda a stdlib. Nao estamos implementando
     aritmetica de precisao arbitraria.

  3. O OAEP e determinado pelo RFC 8017 e verificavel: se o padding
     estiver errado, o servidor recusa a autenticacao. Nao ha o modo
     de falha silenciosa que torna criptografia caseira perigosa —
     ou funciona, ou nao conecta.

O que NAO esta aqui, e nao deve estar: decifrar, assinar, gerar chave.
Para isso, TLS.
"""

import hashlib
import os

from ...errors import AuthenticationError


def _mgf1(semente, tamanho, algoritmo=hashlib.sha1):
    """A funcao de mascara do OAEP (RFC 8017, B.2.1).

    Estica um hash ate o tamanho pedido, concatenando hashes de
    'semente || contador'.
    """
    saida = b""
    contador = 0
    while len(saida) < tamanho:
        saida += algoritmo(semente + contador.to_bytes(4, "big")).digest()
        contador += 1
    return saida[:tamanho]


def _oaep(mensagem, tamanho_modulo, algoritmo=hashlib.sha1, rotulo=b""):
    """Empacota a mensagem no formato OAEP (RFC 8017, 7.1.1).

        EM = 0x00 || semente_mascarada || bloco_mascarado

    O byte zero na frente garante que o inteiro resultante seja menor
    que o modulo — sem ele, a cifragem pode estourar.
    """
    n_hash = algoritmo().digest_size
    maximo = tamanho_modulo - 2 * n_hash - 2
    if len(mensagem) > maximo:
        raise AuthenticationError(
            f"the password is too long for this key "
            f"({len(mensagem)} bytes, at most {maximo}).",
            doc="banco-de-dados")

    hash_rotulo = algoritmo(rotulo).digest()
    enchimento = b"\x00" * (maximo - len(mensagem))
    bloco = hash_rotulo + enchimento + b"\x01" + mensagem

    semente = os.urandom(n_hash)
    mascara_bloco = _mgf1(semente, len(bloco), algoritmo)
    bloco_mascarado = bytes(a ^ b for a, b in zip(bloco, mascara_bloco))

    mascara_semente = _mgf1(bloco_mascarado, n_hash, algoritmo)
    semente_mascarada = bytes(a ^ b for a, b in zip(semente, mascara_semente))

    return b"\x00" + semente_mascarada + bloco_mascarado


# ─────────────────────────────────────────────────────────────
#  Leitura da chave publica
# ─────────────────────────────────────────────────────────────

def _ler_der(dados, i=0):
    """Um valor DER: devolve (etiqueta, conteudo, proximo indice).

    DER e o formato em que a chave vem: etiqueta, tamanho, conteudo. O
    tamanho e curto (um byte) ou longo (o primeiro byte diz quantos
    bytes o tamanho ocupa).
    """
    etiqueta = dados[i]
    i += 1
    primeiro = dados[i]
    i += 1
    if primeiro & 0x80:
        n = primeiro & 0x7F
        tamanho = int.from_bytes(dados[i:i + n], "big")
        i += n
    else:
        tamanho = primeiro
    return etiqueta, dados[i:i + tamanho], i + tamanho


def ler_chave_publica(pem):
    """Extrai (n, e) de uma chave publica em PEM.

    Aceita os dois formatos que o MySQL manda: 'PUBLIC KEY'
    (SubjectPublicKeyInfo, o comum) e 'RSA PUBLIC KEY' (PKCS#1).
    """
    import base64

    if isinstance(pem, bytes):
        pem = pem.decode("ascii", "replace")

    linhas = [l.strip() for l in pem.strip().splitlines()]
    corpo = "".join(l for l in linhas if l and not l.startswith("-----"))
    if not corpo:
        raise AuthenticationError(
            "the server sent something that is not a public key.",
            doc="banco-de-dados")

    try:
        der = base64.b64decode(corpo)
    except Exception:                                # noqa: BLE001
        raise AuthenticationError(
            "the server's public key is not valid base64.",
            doc="banco-de-dados") from None

    # SubjectPublicKeyInfo: SEQUENCE { AlgorithmIdentifier, BIT STRING }
    etiqueta, conteudo, _ = _ler_der(der)
    if etiqueta != 0x30:
        raise AuthenticationError("the public key is not a DER sequence.",
                                  doc="banco-de-dados")

    etiqueta_interna, interno, proximo = _ler_der(conteudo)
    if etiqueta_interna == 0x30:
        # E SubjectPublicKeyInfo: o proximo campo e a BIT STRING que
        # embrulha o PKCS#1 de verdade.
        etiqueta_bits, bits, _ = _ler_der(conteudo, proximo)
        if etiqueta_bits != 0x03:
            raise AuthenticationError("unexpected public key layout.",
                                      doc="banco-de-dados")
        conteudo = bits[1:]                          # o 1o byte e o padding
        _, conteudo, _ = _ler_der(conteudo)

    # PKCS#1 RSAPublicKey: SEQUENCE { INTEGER n, INTEGER e }
    _, bruto_n, i = _ler_der(conteudo)
    _, bruto_e, _ = _ler_der(conteudo, i)
    return int.from_bytes(bruto_n, "big"), int.from_bytes(bruto_e, "big")


def cifrar(mensagem, pem):
    """A mensagem cifrada com a chave publica, no formato OAEP-SHA1.

    E o que o MySQL espera: 'RSA_PKCS1_OAEP_PADDING' com SHA-1, que e o
    padrao do OpenSSL e o que o servidor usa para decifrar.
    """
    n, e = ler_chave_publica(pem)
    tamanho = (n.bit_length() + 7) // 8

    empacotada = _oaep(mensagem, tamanho)
    numero = int.from_bytes(empacotada, "big")
    if numero >= n:
        raise AuthenticationError(
            "the padded message does not fit the modulus.",
            doc="banco-de-dados")

    cifrada = pow(numero, e, n)
    return cifrada.to_bytes(tamanho, "big")
