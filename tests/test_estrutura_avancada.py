"""Estruturas avançadas: texto e bytes de tamanho fixo, bits, varint,
CRC-32, troca de ordem e arquivo mapeado.

As referências são externas — o `struct`, o `zlib` e os exemplos da
especificação do Protocol Buffers —, para que o módulo não concorde
apenas consigo mesmo.
"""
import os
import struct
import sys
import zlib

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import erro_por_nome  # noqa: E402
from dataforge.stdlib import get_module  # noqa: E402

Est = get_module("Arcane.Estrutura")
Estouro = erro_por_nome("BufferOverflowError")
PNG = b"\x89PNG\r\n\x1a\n"


def _cabecalho_png():
    return Est["definir"]("Cab", [["magica", "bytes", 8], ["tam", "u32"],
                                  ["tipo", "char", 4], ["largura", "u32"],
                                  ["altura", "u32"]])


def test_o_layout_bate_com_o_struct_do_python():
    cab = _cabecalho_png()
    dados = cab.empacotar({"magica": PNG, "tam": 13, "tipo": "IHDR",
                           "largura": 640, "altura": 480}).bytes()
    assert dados == struct.pack(">8sI4sII", PNG, 13, b"IHDR", 640, 480)


def test_char_le_ate_o_zero_e_completa_com_zeros():
    m = Est["definir"]("P", [["nome", "char", 8], ["idade", "u8"]])
    b = m.empacotar({"nome": "Ana", "idade": 30})
    assert b.bytes()[:8] == b"Ana\x00\x00\x00\x00\x00"
    assert m.ler(b) == {"nome": "Ana", "idade": 30}


def test_char_nao_corta_em_silencio():
    m = Est["definir"]("P", [["nome", "char", 4]])
    with pytest.raises(Estouro, match="ate 4 byte"):
        m.empacotar({"nome": "João!"})      # 6 bytes em UTF-8


def test_char_nao_alinha_e_o_campo_seguinte_sim():
    m = Est["definir"]("P", [["nome", "char", 3], ["n", "u32"]])
    assert m.deslocamento("n") == 4 and m.tamanho == 8
    assert Est["alinhamento_de"](m) == 4
    # char e bytes sao so de campo: a lista de tipos escalares nao muda
    assert "char" not in Est["tipos"]() and len(Est["tipos"]()) == 11


def test_campos_de_bits_como_no_cabecalho_ipv4():
    ip = Est["campos_de_bits"]("IPv4", [["versao", 4], ["ihl", 4]])
    assert ip.ler(0x45) == {"versao": 4, "ihl": 5}
    assert ip.juntar({"versao": 4, "ihl": 5}) == 0x45
    assert ip.juntar({"ihl": 5}) == 0x05


def test_bits_que_invadiriam_o_vizinho_sao_recusados():
    ip = Est["campos_de_bits"]("IPv4", [["versao", 4], ["ihl", 4]])
    with pytest.raises(Estouro, match="de 0 a 15"):
        ip.juntar({"versao": 16})


def test_bits_que_passam_da_largura_sao_recusados_na_declaracao():
    with pytest.raises(Exception, match="somam 10 bits") as info:
        Est["campos_de_bits"]("X", [["a", 5], ["b", 5]], 8)
    assert "largura := 16" in info.value.dica


def test_flags_tcp_em_16_bits():
    tcp = Est["campos_de_bits"]("TCP", [["desloc", 4], ["reservado", 3],
                                        ["ns", 1], ["cwr", 1], ["ece", 1],
                                        ["urg", 1], ["ack", 1], ["psh", 1],
                                        ["rst", 1], ["syn", 1], ["fin", 1]], 16)
    syn_ack = tcp.juntar({"desloc": 5, "syn": 1, "ack": 1})
    assert syn_ack == 0x5012
    assert tcp.ler(0x5012)["syn"] == 1 and tcp.ler(0x5012)["fin"] == 0


@pytest.mark.parametrize("n,hexa", [(0, "00"), (1, "01"), (127, "7f"),
                                    (128, "8001"), (150, "9601"),
                                    (300, "ac02")])
def test_varint_bate_com_o_protobuf(n, hexa):
    assert Est["varint"](n).hex() == hexa
    assert Est["ler_varint"](bytes.fromhex(hexa)) == {"valor": n, "tamanho": len(hexa) // 2}


def test_varint_le_no_meio_e_recusa_o_truncado():
    dados = b"\xff" + Est["varint"](300) + b"\x01"
    assert Est["ler_varint"](dados, 1) == {"valor": 300, "tamanho": 2}
    with pytest.raises(Estouro, match="nao termina"):
        Est["ler_varint"](b"\x80\x80")
    with pytest.raises(Exception, match="negativo") as info:
        Est["varint"](-1)
    assert "zigzag" in info.value.dica


def test_zigzag_bate_com_o_protobuf():
    assert [Est["zigzag"](n) for n in (0, -1, 1, -2, 2147483647, -2147483648)] == \
        [0, 1, 2, 3, 4294967294, 4294967295]
    for n in range(-500, 500):
        assert Est["desfazer_zigzag"](Est["zigzag"](n)) == n


def test_crc32_bate_com_o_zlib_e_continua_em_partes():
    assert Est["crc32"](b"IHDR") == zlib.crc32(b"IHDR")
    inteiro = Est["crc32"](b"IHDR" + bytes(13))
    assert Est["crc32"](bytes(13), Est["crc32"](b"IHDR")) == inteiro


def test_trocar_ordem():
    assert Est["trocar_ordem"](0x12345678, "u32") == 0x78563412
    assert Est["trocar_ordem"](0x0102, "u16") == 0x0201
    with pytest.raises(Exception, match="inteiros"):
        Est["trocar_ordem"](1.0, "f64")


def test_arquivo_mapeado_escreve_no_disco(tmp_path):
    cab = _cabecalho_png()
    caminho = tmp_path / "a.bin"
    caminho.write_bytes(bytes(cab.tamanho))
    bloco = Est["mapear"](str(caminho), True)
    assert bloco.mapeado()
    Est["janela"](bloco, cab)["largura"] = 1920
    bloco.sincronizar()
    bloco.liberar()
    assert cab.ler(caminho.read_bytes())["largura"] == 1920


def test_mapeado_so_para_leitura_recusa_escrita(tmp_path):
    cab = _cabecalho_png()
    caminho = tmp_path / "a.bin"
    caminho.write_bytes(bytes(cab.tamanho))
    bloco = Est["mapear"](str(caminho))
    with pytest.raises(Exception, match="so para leitura"):
        cab.escrever(bloco, {"tam": 1})
    assert cab.ler(bloco)["tam"] == 0
    bloco.liberar()


def test_mapear_vazio_ou_ausente_e_recusado_com_motivo(tmp_path):
    vazio = tmp_path / "v.bin"
    vazio.write_bytes(b"")
    with pytest.raises(Exception, match="vazio"):
        Est["mapear"](str(vazio))
    with pytest.raises(Exception, match="nao existe"):
        Est["mapear"](str(tmp_path / "nada.bin"))


# ── operações de bits ─────────────────────────────────────────

def test_operacoes_de_bits_batem_com_o_python():
    for a, b in [(0b1100, 0b1010), (0xFFFF, 0x0F0F), (0, 7)]:
        assert Est["bits_e"](a, b) == a & b
        assert Est["bits_ou"](a, b) == a | b
        assert Est["bits_xou"](a, b) == a ^ b
    assert Est["deslocar"](1, 10) == 1024 and Est["deslocar"](1024, -3) == 128
    assert Est["contar_uns"](0b1011) == 3


def test_nao_respeita_a_largura_e_recusa_o_que_nao_cabe():
    assert Est["bits_nao"](5, 8) == 250
    assert Est["bits_nao"](0, 16) == 0xFFFF
    with pytest.raises(Estouro):
        Est["bits_nao"](256, 8)


def test_um_bit_so():
    assert Est["bit_ligado"](0b100, 2) and not Est["bit_ligado"](0b100, 1)
    assert Est["ligar_bit"](0, 3) == 8 and Est["desligar_bit"](15, 0) == 14


def test_bits_recusa_o_que_nao_e_inteiro():
    with pytest.raises(Exception, match="inteiros"):
        Est["bits_e"](1.5, 1)
    with pytest.raises(Exception, match="inteiros"):
        Est["bits_ou"](True, 1)
