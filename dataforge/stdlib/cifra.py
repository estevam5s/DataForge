"""
ChaCha20-Poly1305 em Python puro (RFC 8439).

E a cifra que sustenta 'Arcane.Vault'. Sem dependencia externa, como o
resto do runtime.

─── "Nao escreva sua propria criptografia" ─────────────────

O conselho e bom, e vale principalmente contra dois riscos: errar o
algoritmo, e vazar o segredo pelo TEMPO que a operacao leva.

O primeiro se resolve com os vetores de teste OFICIAIS do RFC 8439 —
eles estao em 'tests/test_cifra.py', e se qualquer bit sair errado o
teste falha. Uma implementacao que reproduz os vetores byte a byte
esta certa; nao ha meio-termo.

O segundo e o motivo de a escolha ser ChaCha20 e nao AES. O AES em
software depende de TABELAS, e o tempo de ler uma tabela varia com o
que esta em cache — que depende da chave. E o vazamento classico, e
por isso AES em software puro e desaconselhado.

ChaCha20 nao tem tabela nenhuma: e soma, rotacao e XOR, sempre nas
mesmas posicoes, sem nenhum desvio que dependa do segredo. Daniel
Bernstein a projetou exatamente assim para ser implementavel com
seguranca em qualquer linguagem. Este e o caso raro em que escrever a
cifra e defensavel.

─── O que este modulo NAO promete ──────────────────────────

O Poly1305 — o autenticador — multiplica inteiros grandes, e a
multiplicacao do Python nao e de tempo constante. Para cifrar um
arquivo no seu disco isso nao importa: o atacante precisaria medir o
tempo de milhares de tentativas de autenticacao escolhidas por ele.

Para um canal em rede contra um adversario ativo, use TLS — que e o
que 'Arcane.Http' ja faz.
"""

import hashlib
import hmac
import os
import struct


# ═════════════════════════════════════════════════════════════
#  ChaCha20
# ═════════════════════════════════════════════════════════════

#: "expand 32-byte k" — a constante do estado inicial. Ela existe para
#: o bloco nunca ser todo controlado pelo atacante.
_CONSTANTE = (0x61707865, 0x3320646e, 0x79622d32, 0x6b206574)

_MASCARA = 0xFFFFFFFF


def _rot(v, n):
    """Rotacao a esquerda em 32 bits."""
    return ((v << n) & _MASCARA) | (v >> (32 - n))


def _quarto_de_volta(x, a, b, c, d):
    """A operacao basica: soma, XOR, rotaciona. Quatro vezes.

    Nenhum desvio, nenhuma leitura de tabela, nenhuma dependencia do
    segredo no CAMINHO — so nos valores. E o que torna a cifra
    naturalmente de tempo constante.
    """
    x[a] = (x[a] + x[b]) & _MASCARA
    x[d] = _rot(x[d] ^ x[a], 16)
    x[c] = (x[c] + x[d]) & _MASCARA
    x[b] = _rot(x[b] ^ x[c], 12)
    x[a] = (x[a] + x[b]) & _MASCARA
    x[d] = _rot(x[d] ^ x[a], 8)
    x[c] = (x[c] + x[d]) & _MASCARA
    x[b] = _rot(x[b] ^ x[c], 7)


def bloco(chave, contador, nonce):
    """Um bloco de 64 bytes do fluxo, a partir de (chave, contador, nonce)."""
    estado = list(_CONSTANTE)
    estado += list(struct.unpack("<8I", chave))
    estado.append(contador & _MASCARA)
    estado += list(struct.unpack("<3I", nonce))

    x = list(estado)
    # 20 voltas = 10 duplas: quatro colunas, depois quatro diagonais.
    for _ in range(10):
        _quarto_de_volta(x, 0, 4, 8, 12)
        _quarto_de_volta(x, 1, 5, 9, 13)
        _quarto_de_volta(x, 2, 6, 10, 14)
        _quarto_de_volta(x, 3, 7, 11, 15)
        _quarto_de_volta(x, 0, 5, 10, 15)
        _quarto_de_volta(x, 1, 6, 11, 12)
        _quarto_de_volta(x, 2, 7, 8, 13)
        _quarto_de_volta(x, 3, 4, 9, 14)

    # Somar o estado inicial e o que impede inverter as 20 voltas.
    return struct.pack("<16I", *[(a + b) & _MASCARA
                                 for a, b in zip(x, estado)])


def chacha20(chave, nonce, dados, contador=1):
    """Cifra ou decifra — a mesma operacao, porque e XOR com o fluxo.

    E por isso que o NONCE nunca pode se repetir com a mesma chave:
    dois textos cifrados com o mesmo fluxo se cancelam no XOR, e quem
    vir os dois recupera ambos sem saber a chave.
    """
    if len(chave) != 32:
        raise ValueError("a chave tem 32 bytes")
    if len(nonce) != 12:
        raise ValueError("o nonce tem 12 bytes")

    saida = bytearray(len(dados))
    for i in range(0, len(dados), 64):
        fluxo = bloco(chave, contador + i // 64, nonce)
        pedaco = dados[i:i + 64]
        for j, b in enumerate(pedaco):
            saida[i + j] = b ^ fluxo[j]
    return bytes(saida)


# ═════════════════════════════════════════════════════════════
#  Poly1305
# ═════════════════════════════════════════════════════════════

_P = (1 << 130) - 5


def poly1305(chave, mensagem):
    """A etiqueta de autenticacao: 16 bytes que provam que nada mudou.

    Sem ela, cifrar nao basta: quem intercepta pode VIRAR bits do texto
    cifrado, e como a cifra e XOR, isso vira bits do texto claro. O
    destinatario decifraria lixo controlado pelo atacante sem perceber.
    """
    r = int.from_bytes(chave[:16], "little") & 0x0FFFFFFC0FFFFFFC0FFFFFFC0FFFFFFF
    s = int.from_bytes(chave[16:32], "little")

    acumulado = 0
    for i in range(0, len(mensagem), 16):
        pedaco = mensagem[i:i + 16]
        # O 1 no fim marca o tamanho do bloco: sem ele, um bloco de
        # zeros a mais nao mudaria a etiqueta.
        n = int.from_bytes(pedaco + b"\x01", "little")
        acumulado = ((acumulado + n) * r) % _P

    return ((acumulado + s) & ((1 << 128) - 1)).to_bytes(16, "little")


def _preencher16(dados):
    """Zeros ate o multiplo de 16, como o RFC manda."""
    resto = len(dados) % 16
    return b"" if resto == 0 else b"\x00" * (16 - resto)


def selar(chave, nonce, texto, extra=b""):
    """Cifra e autentica. Devolve (cifrado, etiqueta).

    'extra' e autenticado mas NAO cifrado — serve para cabecalho que
    precisa ser lido antes de decifrar, e ainda assim nao pode ser
    adulterado.
    """
    # A chave do autenticador sai do bloco ZERO do mesmo fluxo. Usar a
    # chave da cifra diretamente permitiria recuperar 'r'.
    chave_poly = bloco(chave, 0, nonce)[:32]
    cifrado = chacha20(chave, nonce, texto, contador=1)

    corpo = (extra + _preencher16(extra) +
             cifrado + _preencher16(cifrado) +
             struct.pack("<Q", len(extra)) +
             struct.pack("<Q", len(cifrado)))
    return cifrado, poly1305(chave_poly, corpo)


def abrir(chave, nonce, cifrado, etiqueta, extra=b""):
    """Confere a etiqueta e decifra. Devolve None se nao bater.

    A conferencia vem ANTES de decifrar, e usa comparacao de tempo
    constante: comparar byte a byte com saida antecipada revelaria,
    pelo tempo, quantos bytes iniciais o atacante acertou — e com isso
    ele forja a etiqueta em 16 x 256 tentativas em vez de 2^128.
    """
    chave_poly = bloco(chave, 0, nonce)[:32]
    corpo = (extra + _preencher16(extra) +
             cifrado + _preencher16(cifrado) +
             struct.pack("<Q", len(extra)) +
             struct.pack("<Q", len(cifrado)))

    if not hmac.compare_digest(poly1305(chave_poly, corpo), etiqueta):
        return None
    return chacha20(chave, nonce, cifrado, contador=1)


# ═════════════════════════════════════════════════════════════
#  Chave a partir de senha
# ═════════════════════════════════════════════════════════════

#: Quantas iteracoes na derivacao.
#:
#: O numero e alto de proposito: ele e o que separa uma senha fraca de
#: uma quebrada em segundos. Custa ~0,3s aqui, e multiplica por 600 mil
#: o custo de quem tenta adivinhar.
ITERACOES = 600_000


def derivar(senha, sal, iteracoes=ITERACOES):
    """Uma chave de 32 bytes a partir de uma senha.

    PBKDF2-HMAC-SHA256, que esta na stdlib do Python e e implementado
    em C — nao ha nada a escrever aqui, e o que existe e o certo.
    """
    if isinstance(senha, str):
        senha = senha.encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", senha, sal, iteracoes, dklen=32)


def sal_novo(n=16):
    return os.urandom(n)


def nonce_novo():
    return os.urandom(12)
