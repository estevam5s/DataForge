# -*- coding: utf-8 -*-
"""JWT e compressão de valor — duas lacunas medidas contra o que existia.

O JWT mora em `Arcane.Crypto` porque um JWT **é** um HMAC sobre dois
pedaços de base64url, e as duas peças já estavam lá. A compressão mora em
`Arcane.Archive`, que já fazia zip e tar de ARQUIVO e não tinha como
encolher um valor na memória — que é o que um corpo de HTTP, um campo de
banco ou uma mensagem de fila precisam.
"""

import gzip
import io
import os
import sys
import time
import zlib
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.interpreter import Interpreter        # noqa: E402
from dataforge.lexer import tokenize                 # noqa: E402
from dataforge.parser import parse                   # noqa: E402
from dataforge.stdlib import get_module              # noqa: E402

C = get_module("Arcane.Crypto")
A = get_module("Arcane.Archive")


def rodar(fonte):
    interp = Interpreter()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        interp.run(parse(tokenize(fonte, "t.df"), "t.df"))
    return buffer.getvalue().strip()


# ══════════════════════════════════════════════════════════
#  JWT
# ══════════════════════════════════════════════════════════

def test_o_token_assinado_volta_valido():
    token = C["jwt_assinar"]({"sub": "ana", "papel": "admin"}, "segredo")
    r = C["jwt_verificar"](token, "segredo")
    assert r["valido"] is True
    assert r["carga"]["sub"] == "ana" and r["carga"]["papel"] == "admin"


def test_a_chave_errada_nao_passa():
    token = C["jwt_assinar"]({"sub": "ana"}, "segredo")
    r = C["jwt_verificar"](token, "outra")
    assert r["valido"] is False and "assinatura" in r["motivo"]


def test_um_token_de_outra_biblioteca_e_aceito():
    """Interoperabilidade — o vetor conhecido do jwt.io.

    Um JWT que só esta biblioteca entende não é um JWT.
    """
    externo = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
               "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0Ijox"
               "NTE2MjM5MDIyfQ."
               "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    r = C["jwt_verificar"](externo, "your-256-bit-secret")
    assert r["valido"] is True
    assert r["carga"]["name"] == "John Doe"


def test_alg_none_e_recusado():
    """A falha clássica do JWT: quem verifica lê o 'alg' do TOKEN e aceita
    'none'. Aí qualquer um escreve o token que quiser."""
    forjado = "eyJhbGciOiJub25lIn0.eyJzdWIiOiJhbmEifQ."
    r = C["jwt_verificar"](forjado, "segredo")
    assert r["valido"] is False


def test_trocar_o_algoritmo_do_token_nao_muda_a_verificacao():
    """Quem decide o algoritmo é quem verifica, e não o token."""
    token = C["jwt_assinar"]({"sub": "ana"}, "segredo", "HS512")
    assert C["jwt_verificar"](token, "segredo", "HS512")["valido"] is True
    assert C["jwt_verificar"](token, "segredo", "HS256")["valido"] is False


def test_o_token_vencido_diz_que_venceu_e_entrega_a_carga():
    """Quem expirou precisa saber DE QUEM era o token, para renovar."""
    token = C["jwt_assinar"]({"sub": "ana", "exp": int(time.time()) - 10},
                             "segredo")
    r = C["jwt_verificar"](token, "segredo")
    assert r["valido"] is False and r["motivo"] == "o token venceu"
    assert r["carga"]["sub"] == "ana"


def test_expira_em_conta_em_segundos():
    """A unidade é a do próprio JWT: 'exp' é em segundos desde 1970.

    Milissegundos aqui dariam um token válido por 50 mil anos. O limite
    abaixo é o PRAZO que este teste configurou, e não a velocidade da
    máquina: uma máquina lenta só encurta a folga, e o piso a reforça.
    """
    prazo = 60
    token = C["jwt_assinar"]({"sub": "ana"}, "k", "HS256", prazo)
    falta = C["jwt_ler"](token)["exp"] - int(time.time())
    assert prazo - 5 <= falta <= prazo


def test_um_algoritmo_que_nao_se_sabe_fazer_e_recusado_ao_assinar():
    """'RS256' pede RSA, que esta biblioteca não tem. Aceitar o nome sem
    fazer a conta seria pior que recusar."""
    with pytest.raises(Exception) as erro:
        C["jwt_assinar"]({"sub": "a"}, "k", "RS256")
    assert "RS256" in str(erro.value)


def test_jwt_ler_nao_verifica_e_o_nome_diz():
    forjado = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJpbnZhc29yIn0.lixo"
    assert C["jwt_ler"](forjado)["sub"] == "invasor"
    assert C["jwt_verificar"](forjado, "k")["valido"] is False


def test_um_token_quebrado_nao_levanta():
    """Token inválido é o caso NORMAL de um servidor, e não uma exceção."""
    for ruim in ("", "abc", "a.b", "a.b.c.d", "...", "x.y.z"):
        r = C["jwt_verificar"](ruim, "k")
        assert r["valido"] is False and r["motivo"]


def test_a_mesma_carga_da_a_mesma_assinatura():
    """As chaves do JSON saem ordenadas: sem isso, dois tokens com a mesma
    carga teriam assinaturas diferentes conforme a ordem do vault."""
    a = C["jwt_assinar"]({"b": 2, "a": 1}, "k")
    b = C["jwt_assinar"]({"a": 1, "b": 2}, "k")
    assert a == b


def test_o_jwt_funciona_pela_linguagem():
    assert rodar('adopt Arcane.Crypto as C\n'
                 't := C.jwt_assinar({"sub": "ana"}, "k", "HS256", 60)\n'
                 'r := C.jwt_verificar(t, "k")\n'
                 'out r["valido"], r["carga"]["sub"]\n') == "yes ana"


# ══════════════════════════════════════════════════════════
#  Compressão
# ══════════════════════════════════════════════════════════

TEXTO = "DataForge " * 200


def test_comprimir_e_descomprimir_fecham_o_ciclo():
    assert A["descomprimir"](A["comprimir"](TEXTO), True) == TEXTO


def test_gzip_e_de_gzip_fecham_o_ciclo():
    assert A["de_gzip"](A["gzip"](TEXTO), True) == TEXTO


def test_o_gzip_do_sistema_le_o_nosso_e_vice_versa():
    """Um gzip que só esta biblioteca lê não serve para
    'Content-Encoding: gzip'."""
    assert gzip.decompress(A["gzip"](TEXTO)).decode() == TEXTO
    assert A["de_gzip"](gzip.compress(TEXTO.encode()), True) == TEXTO


def test_deflate_e_gzip_sao_formatos_diferentes():
    """Mandar deflate onde se prometeu gzip dá um corpo que o navegador
    recusa, e a mensagem dele não diz por quê."""
    with pytest.raises(Exception) as erro:
        A["de_gzip"](A["comprimir"](TEXTO))
    assert "gzip" in str(erro.value)
    assert zlib.decompress(A["comprimir"](TEXTO)).decode() == TEXTO


def test_a_taxa_diz_quanto_encolheu():
    medida = A["taxa"](TEXTO, A["comprimir"](TEXTO))
    assert medida["antes"] == 2000
    assert medida["depois"] < 100
    assert medida["taxa"] < 0.1 and medida["porcento"] > 90


def test_a_taxa_passa_de_um_quando_o_dado_nao_encolhe():
    """Comprimir o que já está comprimido é desperdício, e é a informação
    mais útil que a taxa dá."""
    ja_comprimido = A["gzip"]("x" * 64)
    medida = A["taxa"](ja_comprimido, A["gzip"](ja_comprimido))
    assert medida["taxa"] > 1


@pytest.mark.parametrize("nivel", [0, 1, 6, 9])
def test_todo_nivel_valido_fecha_o_ciclo(nivel):
    assert A["descomprimir"](A["comprimir"](TEXTO, nivel), True) == TEXTO


def test_um_nivel_fora_da_faixa_e_recusado():
    with pytest.raises(Exception) as erro:
        A["comprimir"](TEXTO, 12)
    assert "0 a 9" in str(erro.value)


def test_um_valor_que_nao_e_bytes_nem_texto_e_recusado_pelo_tipo():
    with pytest.raises(Exception) as erro:
        A["comprimir"](42)
    assert "Integer" in str(erro.value)


def test_a_compressao_funciona_pela_linguagem():
    assert rodar('adopt Arcane.Archive as Z\n'
                 'c := Z.gzip("oi " * 50)\n'
                 'out len(c) smaller 200, Z.de_gzip(c, yes) is "oi " * 50\n'
                 ) == "yes yes"
