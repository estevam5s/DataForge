"""
ChaCha20-Poly1305, Arcane.Crypto e Arcane.Archive.

A primeira classe e a que mais importa: os **vetores oficiais** do
RFC 8439. Uma cifra ou reproduz o vetor byte a byte ou esta errada —
nao ha "quase". Enquanto estes quatro testes passarem, a
implementacao esta correta; se um deles falhar depois de uma
"otimizacao", a otimizacao e que esta errada.
"""

import os
import zipfile

import pytest

from dataforge.errors import UnsafeArchiveError, ValueError_
from dataforge.stdlib import get_module
from dataforge.stdlib.cifra import (abrir, bloco, chacha20, derivar, poly1305,
                                    selar)

CRYPTO = get_module("Arcane.Crypto")
ARCHIVE = get_module("Arcane.Archive")


# ═════════════════════════════════════════════════════════════
#  Os vetores oficiais do RFC 8439
# ═════════════════════════════════════════════════════════════

class TestVetoresOficiais:
    """https://datatracker.ietf.org/doc/html/rfc8439"""

    def test_bloco_secao_2_3_2(self):
        b = bloco(bytes(range(32)), 1,
                  bytes.fromhex("000000090000004a00000000"))
        assert b.hex() == (
            "10f1e7e4d13b5915500fdd1fa32071c4"
            "c7d1f4c733c068030422aa9ac3d46c4e"
            "d2826446079faa0914c2d705d98b02a2"
            "b5129cd1de164eb9cbd083e8a2503c4e")

    def test_chacha20_secao_2_4_2(self):
        texto = (b"Ladies and Gentlemen of the class of '99: If I could "
                 b"offer you only one tip for the future, sunscreen would "
                 b"be it.")
        r = chacha20(bytes(range(32)),
                     bytes.fromhex("000000000000004a00000000"), texto, 1)
        assert r.hex() == (
            "6e2e359a2568f98041ba0728dd0d6981"
            "e97e7aec1d4360c20a27afccfd9fae0b"
            "f91b65c5524733ab8f593dabcd62b357"
            "1639d624e65152ab8f530c359f0861d8"
            "07ca0dbf500d6a6156a38e088a22b65e"
            "52bc514d16ccf806818ce91ab7793736"
            "5af90bbf74a35be6b40b8eedf2785e42"
            "874d")

    def test_poly1305_secao_2_5_2(self):
        chave = bytes.fromhex(
            "85d6be7857556d337f4452fe42d506a8"
            "0103808afb0db2fd4abff6af4149f51b")
        assert poly1305(chave, b"Cryptographic Forum Research Group").hex() \
            == "a8061dc1305136c6c22b8baf0c0127a9"

    def test_aead_secao_2_8_2(self):
        """O vetor completo: cifra + autenticador + dado extra.

        As tres pecas acima podem estar certas e a MONTAGEM errada —
        chave do autenticador tirada do bloco errado, preenchimento
        faltando, comprimentos na ordem trocada. Este vetor cobre isso.
        """
        texto = (b"Ladies and Gentlemen of the class of '99: If I could "
                 b"offer you only one tip for the future, sunscreen would "
                 b"be it.")
        cifrado, etiqueta = selar(
            bytes(range(0x80, 0xA0)),
            bytes.fromhex("070000004041424344454647"),
            texto,
            bytes.fromhex("50515253c0c1c2c3c4c5c6c7"))

        assert cifrado.hex().startswith(
            "d31a8d34648e60db7b86afbc53ef7ec2a4aded51296e08fea9e2b5a736ee62d6")
        assert etiqueta.hex() == "1ae10b594f09e26a7e902ecbd0600691"


class TestPropriedadesDaCifra:

    def test_cifrar_duas_vezes_devolve_o_original(self):
        chave, nonce = os.urandom(32), os.urandom(12)
        dados = os.urandom(1000)
        assert chacha20(chave, nonce, chacha20(chave, nonce, dados)) == dados

    def test_um_bit_diferente_na_chave_muda_tudo(self):
        """Efeito avalanche: sem ele, a cifra vaza estrutura."""
        chave = bytes(32)
        outra = bytes([1]) + bytes(31)
        nonce = bytes(12)
        a = chacha20(chave, nonce, bytes(64))
        b = chacha20(outra, nonce, bytes(64))
        diferentes = sum(bin(x ^ y).count("1") for x, y in zip(a, b))
        # Metade dos 512 bits deve mudar. Aceito uma folga generosa;
        # o que este teste pega e o caso degenerado, nao o desvio.
        assert 200 < diferentes < 312

    def test_etiqueta_recusa_texto_adulterado(self):
        chave, nonce = os.urandom(32), os.urandom(12)
        cifrado, etiqueta = selar(chave, nonce, b"transferir 100 reais")
        for i in range(len(cifrado)):
            mexido = bytearray(cifrado)
            mexido[i] ^= 0x01
            assert abrir(chave, nonce, bytes(mexido), etiqueta) is None

    def test_etiqueta_recusa_extra_adulterado(self):
        """O 'extra' nao e cifrado, mas e autenticado."""
        chave, nonce = os.urandom(32), os.urandom(12)
        cifrado, etiqueta = selar(chave, nonce, b"x", b"para: alice")
        assert abrir(chave, nonce, cifrado, etiqueta, b"para: mallory") is None
        assert abrir(chave, nonce, cifrado, etiqueta, b"para: alice") == b"x"

    def test_derivar_e_deterministico_e_depende_do_sal(self):
        a = derivar("senha", b"sal fixo", 1000)
        b = derivar("senha", b"sal fixo", 1000)
        c = derivar("senha", b"outro sal", 1000)
        assert a == b and a != c and len(a) == 32

    def test_chave_de_tamanho_errado_e_recusada(self):
        with pytest.raises(ValueError):
            chacha20(bytes(16), bytes(12), b"x")


# ═════════════════════════════════════════════════════════════
#  Arcane.Crypto — arquivos
# ═════════════════════════════════════════════════════════════

class TestArquivoCifrado:

    def test_ida_e_volta(self, tmp_path):
        origem = tmp_path / "nota.txt"
        origem.write_text("senha do wifi: abacaxi", encoding="utf-8")

        CRYPTO["cifrar_arquivo"](str(origem), str(tmp_path / "c.dfv"),
                                 "chave forte", 1000)
        CRYPTO["decifrar_arquivo"](str(tmp_path / "c.dfv"),
                                   str(tmp_path / "volta.txt"),
                                   "chave forte")
        assert (tmp_path / "volta.txt").read_text(encoding="utf-8") \
            == "senha do wifi: abacaxi"

    def test_o_arquivo_cifrado_nao_contem_o_texto(self, tmp_path):
        origem = tmp_path / "n.txt"
        origem.write_text("SEGREDO", encoding="utf-8")
        r = CRYPTO["cifrar_arquivo"](str(origem), "", "senha", 1000)
        assert b"SEGREDO" not in open(r["arquivo"], "rb").read()

    def test_senha_errada_e_recusada(self, tmp_path):
        origem = tmp_path / "n.txt"
        origem.write_text("x", encoding="utf-8")
        r = CRYPTO["cifrar_arquivo"](str(origem), "", "certa", 1000)
        with pytest.raises(ValueError_):
            CRYPTO["decifrar_arquivo"](r["arquivo"], str(tmp_path / "o"),
                                       "errada")

    def test_cabecalho_adulterado_e_recusado(self, tmp_path):
        """Baixar as iteracoes para 1 nao ajuda quem ataca.

        O cabecalho e legivel de proposito — precisa ser, para saber
        como decifrar. Mas ele entra como dado autenticado, entao
        mexer nele invalida a etiqueta.
        """
        origem = tmp_path / "n.txt"
        origem.write_text("x", encoding="utf-8")
        r = CRYPTO["cifrar_arquivo"](str(origem), "", "senha", 5000)

        bruto = bytearray(open(r["arquivo"], "rb").read())
        bruto[8:12] = (1).to_bytes(4, "little")     # iteracoes := 1
        open(r["arquivo"], "wb").write(bytes(bruto))

        with pytest.raises(ValueError_):
            CRYPTO["decifrar_arquivo"](r["arquivo"], str(tmp_path / "o"),
                                       "senha")

    def test_informacao_dispensa_a_senha(self, tmp_path):
        origem = tmp_path / "n.txt"
        origem.write_text("x", encoding="utf-8")
        r = CRYPTO["cifrar_arquivo"](str(origem), "", "senha", 7777)
        info = CRYPTO["informacao_do_cofre"](r["arquivo"])
        assert info["cofre"] and info["iteracoes"] == 7777

    def test_arquivo_comum_nao_e_cofre(self, tmp_path):
        comum = tmp_path / "a.txt"
        comum.write_text("nada demais", encoding="utf-8")
        assert CRYPTO["e_cifrado"](str(comum)) is False
        with pytest.raises(ValueError_):
            CRYPTO["decifrar"](comum.read_bytes(), "senha")

    def test_pasta_inteira(self, tmp_path):
        pasta = tmp_path / "docs"
        pasta.mkdir()
        (pasta / "a.txt").write_text("um", encoding="utf-8")
        (pasta / "b.txt").write_text("dois", encoding="utf-8")
        r = CRYPTO["cifrar_pasta"](str(pasta), str(tmp_path / "d.dfv"),
                                   "senha")
        assert os.path.exists(r["arquivo"])
        assert not os.path.exists(str(tmp_path / "d.dfv.zip.tmp"))

    def test_senha_vazia_e_recusada(self):
        with pytest.raises(ValueError_):
            CRYPTO["cifrar"]("x", "")

    def test_apagar_seguro_remove(self, tmp_path):
        alvo = tmp_path / "x.bin"
        alvo.write_bytes(b"A" * 5000)
        assert CRYPTO["apagar_seguro"](str(alvo)) is True
        assert not alvo.exists()


# ═════════════════════════════════════════════════════════════
#  Arcane.Archive
# ═════════════════════════════════════════════════════════════

class TestArquivosCompactados:

    def test_compactar_e_extrair_pasta(self, tmp_path):
        pasta = tmp_path / "projeto"
        (pasta / "sub").mkdir(parents=True)
        (pasta / "a.txt").write_text("um", encoding="utf-8")
        (pasta / "sub" / "b.txt").write_text("dois", encoding="utf-8")

        r = ARCHIVE["compactar"](str(pasta), str(tmp_path / "p.zip"))
        assert r["itens"] == 2

        ARCHIVE["extrair"](str(tmp_path / "p.zip"), str(tmp_path / "fora"))
        assert (tmp_path / "fora" / "projeto" / "sub" / "b.txt").read_text(
            encoding="utf-8") == "dois"

    def test_ler_um_arquivo_sem_extrair(self, tmp_path):
        z = tmp_path / "p.zip"
        with zipfile.ZipFile(z, "w") as f:
            f.writestr("leia.txt", "conteudo")
        assert ARCHIVE["ler_de"](str(z), "leia.txt") == "conteudo"

    def test_zip_slip_e_recusado(self, tmp_path):
        """A entrada '../..' escreve fora do destino.

        O ataque tem nome — Zip Slip — porque foi explorado em dezenas
        de bibliotecas. Este teste garante que nao passa aqui.
        """
        z = tmp_path / "mau.zip"
        with zipfile.ZipFile(z, "w") as f:
            f.writestr("../../invadido.txt", "fui parar fora")

        destino = tmp_path / "destino"
        with pytest.raises(UnsafeArchiveError):
            ARCHIVE["extrair"](str(z), str(destino))
        assert not (tmp_path.parent / "invadido.txt").exists()

    def test_caminho_absoluto_tambem_e_recusado(self, tmp_path):
        """Uma entrada absoluta e recusada, nao relocada em silencio.

        O 'extractall' do proprio Python apenas tira a barra inicial e
        extrai assim mesmo — o arquivo vai parar em outro lugar sem
        ninguem ser avisado. Aqui a extracao para: um zip que pede
        '/tmp/x' nao esta pedindo 'destino/tmp/x'.
        """
        z = tmp_path / "mau2.zip"
        with zipfile.ZipFile(z, "w") as f:
            f.writestr("/tmp/df-invadido.txt", "x")

        with pytest.raises(UnsafeArchiveError):
            ARCHIVE["extrair"](str(z), str(tmp_path / "d"))
        assert not os.path.exists("/tmp/df-invadido.txt")

    def test_zip_bomb_e_recusada(self, tmp_path):
        z = tmp_path / "bomba.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
            f.writestr("grande.bin", b"\0" * (600 * 1024 * 1024))

        with pytest.raises(UnsafeArchiveError) as e:
            ARCHIVE["extrair"](str(z), str(tmp_path / "d"))
        assert "bomb" in str(e.value)

    def test_zip_honesto_passa(self, tmp_path):
        """A defesa nao pode atrapalhar o uso normal.

        Este CSV comprime **421x** — mais que o teto de razao — e
        ainda assim e um arquivo honesto de 60 KB. Foi ele que mostrou
        que a razao sozinha nao serve de criterio.
        """
        z = tmp_path / "bom.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
            f.writestr("relatorio.csv", "nome,valor\n" + "linha,1\n" * 5000)
        r = ARCHIVE["extrair"](str(z), str(tmp_path / "d"))
        assert r["itens"] == 1

    def test_conferir_acha_corrompido(self, tmp_path):
        z = tmp_path / "p.zip"
        with zipfile.ZipFile(z, "w") as f:
            f.writestr("a.txt", "conteudo")
        assert ARCHIVE["conferir"](str(z))["integro"] is True

        z.write_bytes(b"isto nao e um zip")
        assert ARCHIVE["conferir"](str(z))["integro"] is False

    def test_tar_recusa_link_simbolico(self, tmp_path):
        """Um link dentro do tar pode apontar para qualquer lugar."""
        import tarfile
        t = tmp_path / "mau.tar"
        with tarfile.open(t, "w") as f:
            info = tarfile.TarInfo("atalho")
            info.type = tarfile.SYMTYPE
            info.linkname = "/etc/passwd"
            f.addfile(info)

        with pytest.raises(UnsafeArchiveError):
            ARCHIVE["extrair_tar"](str(t), str(tmp_path / "d"))

    def test_tar_ida_e_volta(self, tmp_path):
        pasta = tmp_path / "p"
        pasta.mkdir()
        (pasta / "a.txt").write_text("conteudo", encoding="utf-8")

        ARCHIVE["compactar_tar"](str(pasta), str(tmp_path / "p.tar.gz"))
        ARCHIVE["extrair_tar"](str(tmp_path / "p.tar.gz"),
                               str(tmp_path / "fora"))
        assert (tmp_path / "fora" / "p" / "a.txt").read_text(
            encoding="utf-8") == "conteudo"
