# -*- coding: utf-8 -*-
"""Arcane.Estrutura — o layout binario, e o que ele recusa.

O que estes testes protegem:

1. **A ordem dos bytes e obrigatoria.** Sem ela, o mesmo arquivo lido
   em duas maquinas da dois valores — e nenhuma das duas falha.

2. **O alinhamento e conferido, e nao adivinhado.** E o que faz o mesmo
   `.struct` ter 12 bytes de um lado e 16 do outro.

3. **Ler fora do bloco levanta.** Sem isso o resultado e um numero
   plausivel, e o defeito aparece tres camadas adiante.

4. **A janela nao copia.** Se copiasse, escrever nela nao mudaria nada
   no bloco — e o teste e justamente esse.

5. **O ponteiro anda por ELEMENTO.** `p + 1` num `u32*` anda quatro
   bytes; andar um byte e um indice, e nao um ponteiro.
"""

import struct
import sys

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import get_module                       # noqa: E402
from dataforge.errors import erro_por_nome                    # noqa: E402

LayoutError = erro_por_nome("LayoutError")


@pytest.fixture
def E():
    return get_module("Arcane.Estrutura")


@pytest.fixture
def Cabecalho(E):
    return E["definir"]("Cabecalho", [
        ["magia", "u32"], ["versao", "u16"], ["itens", "u16"]])


# ═══════════════════════════════════════════════════════════
#  O molde
# ═══════════════════════════════════════════════════════════

def test_o_layout_bate_com_o_que_o_struct_do_python_produz(E, Cabecalho):
    """A fonte de verdade e o `struct`, e nao a minha conta."""
    valores = {"magia": 0x89504E47, "versao": 3, "itens": 7}
    bloco = Cabecalho.empacotar(valores)
    assert bloco.bytes() == struct.pack(">IHH", 0x89504E47, 3, 7)
    assert Cabecalho.ler(bloco) == valores


def test_a_ordem_dos_bytes_muda_o_arquivo(E):
    campos = [["n", "u32"]]
    rede = E["definir"]("A", campos, ordem="rede").empacotar({"n": 1})
    intel = E["definir"]("A", campos, ordem="intel").empacotar({"n": 1})
    assert rede.bytes() == b"\x00\x00\x00\x01"
    assert intel.bytes() == b"\x01\x00\x00\x00"


def test_uma_ordem_que_nao_existe_e_recusada(E):
    with pytest.raises(LayoutError) as erro:
        E["definir"]("A", [["n", "u32"]], ordem="qualquer")
    assert "ordem de bytes" in str(erro.value)


def test_o_alinhamento_insere_enchimento_como_o_C(E):
    alinhado = E["definir"]("P", [["a", "u8"], ["b", "u32"]])
    assert alinhado.deslocamento("b") == 4      # e nao 1
    assert alinhado.tamanho == 8
    assert alinhado.enchimento() == 3


def test_empacotado_nao_tem_enchimento(E):
    junto = E["definir"]("P", [["a", "u8"], ["b", "u32"]], empacotado=True)
    assert junto.deslocamento("b") == 1
    assert junto.tamanho == 5
    assert junto.enchimento() == 0


def test_o_registro_inteiro_tambem_e_alinhado(E):
    """Senao um cluster deles sai torto a partir do segundo."""
    molde = E["definir"]("P", [["a", "u32"], ["b", "u8"]])
    assert molde.tamanho == 8                   # e nao 5


def test_campo_repetido_e_recusado(E):
    """O segundo seria inalcancavel: a leitura devolve um vault."""
    with pytest.raises(LayoutError) as erro:
        E["definir"]("P", [["x", "u8"], ["x", "u32"]])
    assert "duas vezes" in str(erro.value)


def test_tipo_desconhecido_sugere_o_parecido_e_lista_os_demais(E):
    """O nome certo esta a um caractere; a lista e a segunda linha."""
    with pytest.raises(LayoutError) as erro:
        E["definir"]("P", [["x", "u128"]])
    assert "u8" in str(erro.value)              # a sugestao
    assert "u64" in erro.value.nota             # e a lista inteira


def test_um_molde_sem_campo_nenhum_e_recusado(E):
    with pytest.raises(LayoutError):
        E["definir"]("P", [])


def test_o_mapa_e_a_tabela_do_layout(E):
    molde = E["definir"]("P", [["a", "u8"], ["b", "u32"]])
    assert molde.mapa() == [
        {"campo": "a", "tipo": "u8", "quantos": 1,
         "deslocamento": 0, "bytes": 1},
        {"campo": "b", "tipo": "u32", "quantos": 1,
         "deslocamento": 4, "bytes": 4}]


def test_campo_com_varias_posicoes(E):
    molde = E["definir"]("Cor", [["rgba", "u8", 4]])
    bloco = molde.empacotar({"rgba": [1, 2, 3, 255]})
    assert molde.ler(bloco)["rgba"] == [1, 2, 3, 255]
    assert molde.tamanho == 4


def test_a_quantidade_errada_num_campo_de_varias_posicoes(E):
    molde = E["definir"]("Cor", [["rgba", "u8", 4]])
    with pytest.raises(LayoutError):
        molde.empacotar({"rgba": [1, 2]})


# ═══════════════════════════════════════════════════════════
#  Os limites
# ═══════════════════════════════════════════════════════════

def test_ler_alem_do_fim_levanta_em_vez_de_devolver_lixo(E, Cabecalho):
    curto = E["bloco"](4)
    with pytest.raises(erro_por_nome("BufferOverflowError")) as erro:
        Cabecalho.ler(curto)
    assert "8 byte" in str(erro.value)


def test_ler_a_partir_de_um_deslocamento_que_nao_cabe(E, Cabecalho):
    bloco = E["bloco"](12)
    Cabecalho.ler(bloco, 4)                     # cabe
    with pytest.raises(erro_por_nome("BufferOverflowError")):
        Cabecalho.ler(bloco, 8)                 # nao cabe


def test_um_valor_fora_da_faixa_do_tipo_nao_e_truncado(E):
    molde = E["definir"]("P", [["n", "u8"]])
    with pytest.raises(erro_por_nome("BufferOverflowError")) as erro:
        molde.empacotar({"n": 300})
    assert "u8" in str(erro.value)
    assert "0 a 255" in str(erro.value)


def test_a_mensagem_de_faixa_nao_cita_o_formato_do_python(E):
    """O `struct` responde `'B' format requires 0 <= number <= 255`.

    A letra e do formato interno do Python, e quem escreveu `u8` nao
    tem como ligar uma coisa a outra — e a mesma regra que proibe uma
    mensagem do interpretador citar `int` ou `list`.
    """
    for tipo, faixa, valor in [("u8", "0 a 255", 300),
                               ("i8", "-128 a 127", 200),
                               ("u16", "0 a 65535", 70000),
                               ("i32", "-2147483648 a 2147483647", 2 ** 40)]:
        molde = E["definir"]("P", [["n", tipo]])
        with pytest.raises(erro_por_nome("BufferOverflowError")) as erro:
            molde.empacotar({"n": valor})
        texto = str(erro.value)
        assert faixa in texto, (tipo, texto)
        assert "format requires" not in texto, (tipo, texto)


def test_o_ponteiro_tambem_diz_a_faixa(E):
    with pytest.raises(erro_por_nome("BufferOverflowError")) as erro:
        E["ponteiro"](E["bloco"](8), "u8").escrever(999)
    assert "0 a 255" in str(erro.value)


def test_campo_desconhecido_na_escrita_e_recusado(E, Cabecalho):
    bloco = Cabecalho.empacotar({"magia": 1})
    with pytest.raises(LayoutError) as erro:
        Cabecalho.escrever(bloco, {"versaoo": 2})
    assert "versaoo" in str(erro.value)


def test_um_bloco_somente_leitura_recusa_escrita(E, Cabecalho):
    with pytest.raises(LayoutError) as erro:
        Cabecalho.escrever(b"\x00" * 8, {"versao": 1})
    assert "somente leitura" in str(erro.value)


def test_deslocamento_negativo(E, Cabecalho):
    with pytest.raises(erro_por_nome("BufferOverflowError")):
        Cabecalho.ler(E["bloco"](16), -1)


# ═══════════════════════════════════════════════════════════
#  A janela
# ═══════════════════════════════════════════════════════════

def test_a_janela_escreve_NO_BLOCO(E, Cabecalho):
    """Se copiasse, este teste passaria em silencio com o valor velho."""
    bloco = Cabecalho.empacotar({"magia": 1, "versao": 1, "itens": 1})
    j = E["janela"](bloco, Cabecalho)
    j.escrever("versao", 9)
    assert Cabecalho.ler(bloco)["versao"] == 9
    assert j.ler("versao") == 9


def test_a_janela_tambem_por_indice(E, Cabecalho):
    bloco = Cabecalho.empacotar({"magia": 1})
    j = E["janela"](bloco, Cabecalho)
    j["itens"] = 42
    assert j["itens"] == 42


def test_campo_inexistente_na_janela(E, Cabecalho):
    j = E["janela"](E["bloco"](8), Cabecalho)
    with pytest.raises(LayoutError) as erro:
        j.ler("verso")
    assert "versao" in str(erro.value)          # a sugestao, na mensagem
    assert "magia" in erro.value.nota           # e a lista, na nota


def test_janelas_percorre_um_arquivo_de_registros(E):
    molde = E["definir"]("Par", [["a", "u16"], ["b", "u16"]])
    bloco = E["de_bytes"](struct.pack(">HHHHHH", 1, 2, 3, 4, 5, 6))
    todas = E["janelas"](bloco, molde)
    assert len(todas) == 3
    assert [j.ler("a") for j in todas] == [1, 3, 5]
    assert [j.ler("b") for j in todas] == [2, 4, 6]


def test_janelas_recusa_pedir_mais_do_que_cabe(E):
    molde = E["definir"]("Par", [["a", "u16"], ["b", "u16"]])
    with pytest.raises(erro_por_nome("BufferOverflowError")) as erro:
        E["janelas"](E["bloco"](8), molde, quantos=5)
    assert "cabem 2" in str(erro.value)


def test_proxima_anda_um_registro(E):
    molde = E["definir"]("Par", [["a", "u16"], ["b", "u16"]])
    bloco = E["de_bytes"](struct.pack(">HHHH", 1, 2, 3, 4))
    j = E["janela"](bloco, molde)
    assert j.proxima().ler("a") == 3
    assert j.proxima().deslocamento() == 4


def test_vault_da_janela_e_uma_copia(E, Cabecalho):
    bloco = Cabecalho.empacotar({"versao": 1})
    j = E["janela"](bloco, Cabecalho)
    copia = j.vault()
    j.escrever("versao", 9)
    assert copia["versao"] == 1                 # a copia nao acompanha
    assert j.ler("versao") == 9


# ═══════════════════════════════════════════════════════════
#  O bloco
# ═══════════════════════════════════════════════════════════

def test_liberar_e_idempotente(E):
    b = E["bloco"](8)
    assert b.liberar() is True
    assert b.liberar() is False


def test_usar_um_bloco_liberado_levanta(E):
    b = E["bloco"](8)
    b.liberar()
    with pytest.raises(erro_por_nome("DanglingPointerError")):
        b.dados()


def test_tamanho_negativo(E):
    with pytest.raises(erro_por_nome("NegativeSizeError")):
        E["bloco"](-1)


# ═══════════════════════════════════════════════════════════
#  O ponteiro
# ═══════════════════════════════════════════════════════════

def test_o_ponteiro_anda_por_ELEMENTO_e_nao_por_byte(E):
    bloco = E["de_bytes"](struct.pack(">IIII", 10, 20, 30, 40))
    p = E["ponteiro"](bloco, "u32")
    assert p.ler() == 10
    assert p.mais(1).ler() == 20
    assert p.mais(1).endereco() == 4            # e nao 1
    assert p.mais(3).ler() == 40


def test_cluster_le_os_elementos_seguintes(E):
    bloco = E["de_bytes"](struct.pack(">IIII", 10, 20, 30, 40))
    assert E["ponteiro"](bloco, "u32").cluster(4) == [10, 20, 30, 40]


def test_o_ponteiro_escreve(E):
    bloco = E["bloco"](8)
    E["ponteiro"](bloco, "u32").mais(1).escrever(7)
    assert bloco.bytes() == b"\x00" * 4 + b"\x00\x00\x00\x07"


def test_distancia_e_em_elementos(E):
    bloco = E["bloco"](16)
    a = E["ponteiro"](bloco, "u32")
    assert a.mais(3).distancia(a) == 3


def test_distancia_entre_tipos_diferentes_e_recusada(E):
    bloco = E["bloco"](16)
    a = E["ponteiro"](bloco, "u32")
    b = E["ponteiro"](bloco, "u8")
    with pytest.raises(LayoutError) as erro:
        a.distancia(b)
    assert "distancia" in str(erro.value)


def test_como_reinterpreta_o_mesmo_endereco(E):
    bloco = E["de_bytes"](b"\x00\x00\x01\x02")
    assert E["ponteiro"](bloco, "u32").ler() == 0x0102
    assert E["ponteiro"](bloco, "u16").mais(1).ler() == 0x0102
    assert E["ponteiro"](bloco, "u32").como("u8").mais(3).ler() == 2


def test_o_ponteiro_fora_do_bloco_levanta(E):
    bloco = E["bloco"](8)
    with pytest.raises(erro_por_nome("BufferOverflowError")) as erro:
        E["ponteiro"](bloco, "u32").mais(2).ler()
    assert "byte 8" in str(erro.value)


def test_o_ponteiro_de_um_bloco_liberado_levanta(E):
    bloco = E["bloco"](8)
    p = E["ponteiro"](bloco, "u32")
    bloco.liberar()
    assert p.e_nulo() is True
    with pytest.raises(erro_por_nome("DanglingPointerError")):
        p.ler()


def test_o_ponteiro_de_um_bloco_temporario_continua_valido(E):
    """A primeira versao guardava referencia FRACA, e isto nascia morto.

    `Est.ponteiro(Est.bloco(8), "u32")` deixava o bloco sem nenhum dono
    forte: ele era coletado assim que a chamada voltava, e o ponteiro ja
    saia pendurado. Um ponteiro cuja validade depende de a expressao ter
    sido guardada numa variavel e uma armadilha — e ela aparece e some
    conforme a contagem de referencias.

    Num mundo com coletor, a memoria nunca esteve em risco; o que se
    protege e o protocolo, e ele tem um ponto so: `liberar()`.
    """
    import gc
    p = E["ponteiro"](E["bloco"](8), "u32")
    gc.collect()
    assert p.e_nulo() is False
    p.escrever(7)
    assert p.ler() == 7


def test_o_ponteiro_nulo_e_outra_coisa_que_void(E):
    p = E["nulo"]()
    assert p.e_nulo() is True
    with pytest.raises(erro_por_nome("NullPointerError")) as erro:
        p.ler()
    assert "nulo" in str(erro.value)
    with pytest.raises(erro_por_nome("NullPointerError")):
        p.escrever(1)


def test_tipo_desconhecido_no_ponteiro(E):
    with pytest.raises(LayoutError):
        E["ponteiro"](E["bloco"](8), "u128")


# ═══════════════════════════════════════════════════════════
#  Uniao e os tamanhos
# ═══════════════════════════════════════════════════════════

def test_a_uniao_poe_todos_no_mesmo_lugar(E):
    u = E["uniao"]("Valor", [["inteiro", "u32"], ["flutuante", "f32"]])
    assert u.deslocamento("inteiro") == 0
    assert u.deslocamento("flutuante") == 0
    assert u.tamanho == 4

    bloco = E["bloco"](4)
    u.escrever(bloco, {"flutuante": 1.0})
    assert u.ler(bloco)["inteiro"] == 0x3F800000     # o IEEE 754 de 1.0


def test_tamanho_e_alinhamento(E, Cabecalho):
    assert E["tamanho_de"]("u32") == 4
    assert E["tamanho_de"]("f64") == 8
    assert E["tamanho_de"](Cabecalho) == 8
    assert E["alinhamento_de"](Cabecalho) == 4


def test_a_lista_de_tipos_e_a_do_Arcane_Bytes(E):
    """Duas listas divergiriam, e o mesmo 'u32' teria dois tamanhos."""
    from dataforge.stdlib.arcane_bytes import TIPOS as DE_BYTES
    assert set(E["tipos"]()) == set(DE_BYTES)
    for nome in DE_BYTES:
        assert E["tamanho_de"](nome) == DE_BYTES[nome][1], nome


# ═══════════════════════════════════════════════════════════
#  A familia de erros
# ═══════════════════════════════════════════════════════════

def test_a_base_pega_todas():
    for nome in ["BufferOverflowError", "AlignmentError",
                 "NullPointerError", "DanglingPointerError"]:
        assert issubclass(erro_por_nome(nome), LayoutError), nome
