"""
Arcane.Crypto (cifragem de arquivo) e Arcane.Archive (zip e tar).

    adopt Arcane.Crypto as V

    V.cifrar_arquivo("contrato.pdf", "contrato.pdf.df", "minha senha")
    V.decifrar_arquivo("contrato.pdf.df", "de-volta.pdf", "minha senha")

    adopt Arcane.Archive as A

    A.extrair("pacote.zip", "destino/")
    A.compactar("relatorios/", "backup.zip")

─── O formato ──────────────────────────────────────────────

Um arquivo cifrado comeca com um cabecalho legivel:

    DFVAULT1 | iteracoes | sal (16) | nonce (12) | etiqueta (16) | dados

O cabecalho NAO e segredo — ele diz como decifrar, e precisa ser lido
antes de haver chave. Mas ele e AUTENTICADO junto com os dados: mudar
o numero de iteracoes para 1, na esperanca de enfraquecer a
derivacao, invalida a etiqueta e o arquivo e recusado.

─── Sobre o zip ────────────────────────────────────────────

Extrair um zip de origem desconhecida e perigoso: uma entrada com
'../..' escreve fora da pasta de destino, e um arquivo de 1 KB pode
descompactar para 10 GB. Os dois casos sao verificados aqui e
recusados com mensagem — nao por prudencia excessiva, mas porque os
dois tem nome proprio (Zip Slip e zip bomb) justamente por terem sido
explorados muitas vezes.

─── O que ele nao faz ──────────────────────────────────────

'cifrar_arquivo' le o arquivo INTEIRO na memoria antes de cifrar.
Para contrato, backup de configuracao e planilha — o que se cifra na
pratica — isso e o mais simples e o mais seguro: o texto cifrado e a
etiqueta saem juntos, e nao ha estado parcial gravado. Cifrar um
arquivo maior que a RAM pede um formato em pedacos, com uma etiqueta
por pedaco, e isso o DFVAULT1 nao tem.
"""

import os
import struct
import tarfile
import zipfile

from . import cifra
from ..errors import FileNotFoundError_, UnsafeArchiveError, ValueError_


#: A marca do formato. A versao esta nela para um formato futuro poder
#: conviver com este.
MARCA = b"DFVAULT1"

#: Quanto escrever por vez ao sobrescrever um arquivo em 'apagar_seguro'.
PEDACO = 1024 * 1024

#: Tetos de extracao.
#:
#: A razao de compressao SOZINHA nao serve de alarme: um CSV de linhas
#: repetidas comprime 400x sem ser ataque nenhum, e recusa-lo ensina o
#: usuario a desligar a protecao. O que faz uma bomba ser bomba e o
#: tamanho ABSOLUTO — encher o disco. Por isso a razao so pesa quando
#: o resultado ja e grande o bastante para doer.
EXPANSAO_MAXIMA = 200
TAMANHO_SUSPEITO = 512 * 1024 ** 2   # 512 MB
TAMANHO_MAXIMO = 8 * 1024 ** 3       # 8 GB


class ArcaneCofre(dict):
    """Cifragem de verdade — junta-se ao Arcane.Crypto.

    O 'xor_cipher' que ja existe la e brinquedo educativo: XOR com uma
    chave repetida se quebra com analise de frequencia, e nao detecta
    adulteracao. Isto aqui e ChaCha20-Poly1305, que cifra E autentica.
    Os dois convivem no mesmo modulo porque o nome ja diz qual e qual.
    """

    def __new__(cls):
        return {
            "cifrar": cls._cifrar,
            "decifrar": cls._decifrar,
            "cifrar_arquivo": cls._cifrar_arquivo,
            "decifrar_arquivo": cls._decifrar_arquivo,
            "cifrar_pasta": cls._cifrar_pasta,
            "e_cifrado": cls._e_cifrado,
            "informacao_do_cofre": cls._informacao,
            "chave_nova": cls._chave_nova,
            "derivar_chave": cls._derivar,
            "apagar_seguro": cls._apagar_seguro,
        }

    # ── cifrar em memoria ───────────────────────────────────

    @staticmethod
    def _cifrar(dados, senha, iteracoes=None):
        """Cifra bytes ou texto; devolve bytes prontos para gravar."""
        if isinstance(dados, str):
            dados = dados.encode("utf-8")
        if not senha:
            raise ValueError_(
                "encrypting without a password protects nothing.",
                dica="pass a password, or generate a key with chave_nova()",
                doc="tecnicas/criptografia")

        n = int(iteracoes or cifra.ITERACOES)
        sal = cifra.sal_novo()
        nonce = cifra.nonce_novo()
        chave = cifra.derivar(senha, sal, n)

        # O cabecalho entra como dado EXTRA do selo: ele nao e segredo,
        # mas mexer nele invalida a etiqueta.
        cabecalho = MARCA + struct.pack("<I", n) + sal + nonce
        cifrado, etiqueta = cifra.selar(chave, nonce, dados, cabecalho)
        return cabecalho + etiqueta + cifrado

    @staticmethod
    def _decifrar(pacote, senha):
        """Devolve os bytes originais, ou levanta se a senha ou o
        conteudo estiverem errados."""
        if isinstance(pacote, str):
            pacote = pacote.encode("latin-1")

        if len(pacote) < len(MARCA) + 4 + 16 + 12 + 16:
            raise ValueError_(
                "this is not a DataForge vault file: it is too short.",
                doc="tecnicas/criptografia")
        if not pacote.startswith(MARCA):
            raise ValueError_(
                "this is not a DataForge vault file.",
                nota=f"it should start with {MARCA.decode()}",
                doc="tecnicas/criptografia")

        i = len(MARCA)
        n = struct.unpack("<I", pacote[i:i + 4])[0]
        i += 4
        sal, i = pacote[i:i + 16], i + 16
        nonce, i = pacote[i:i + 12], i + 12
        etiqueta, i = pacote[i:i + 16], i + 16
        cifrado = pacote[i:]

        cabecalho = pacote[:len(MARCA) + 4 + 16 + 12]
        chave = cifra.derivar(senha, sal, n)
        aberto = cifra.abrir(chave, nonce, cifrado, etiqueta, cabecalho)

        if aberto is None:
            raise ValueError_(
                "wrong password, or the file was tampered with.",
                nota="the authentication tag did not match",
                dica=("there is no way to tell the two apart — and that is "
                      "the point: an error that distinguished them would "
                      "let someone test passwords faster"),
                doc="tecnicas/criptografia")
        return aberto

    # ── cifrar arquivo ──────────────────────────────────────

    @staticmethod
    def _cifrar_arquivo(origem, destino="", senha="", iteracoes=None):
        """Cifra um arquivo. Sem destino, acrescenta '.dfv'."""
        if not os.path.isfile(origem):
            raise FileNotFoundError_(
                f"'{origem}' does not exist.", doc="tecnicas/criptografia")
        alvo = destino or (origem + ".dfv")

        with open(origem, "rb") as f:
            dados = f.read()
        pacote = ArcaneCofre._cifrar(dados, senha, iteracoes)

        # Grava num temporario e RENOMEIA. Gravar direto no destino
        # deixa um arquivo pela metade se a maquina cair no meio — e
        # aqui pela metade significa perdido.
        temporario = alvo + ".parcial"
        with open(temporario, "wb") as f:
            f.write(pacote)
        os.replace(temporario, alvo)

        return {"arquivo": alvo,
                "original": len(dados),
                "cifrado": len(pacote),
                "iteracoes": int(iteracoes or cifra.ITERACOES)}

    @staticmethod
    def _decifrar_arquivo(origem, destino="", senha=""):
        if not os.path.isfile(origem):
            raise FileNotFoundError_(
                f"'{origem}' does not exist.", doc="tecnicas/criptografia")

        with open(origem, "rb") as f:
            pacote = f.read()
        dados = ArcaneCofre._decifrar(pacote, senha)

        alvo = destino or (origem[:-4] if origem.endswith(".dfv")
                           else origem + ".aberto")
        temporario = alvo + ".parcial"
        with open(temporario, "wb") as f:
            f.write(dados)
        os.replace(temporario, alvo)

        return {"arquivo": alvo, "bytes": len(dados)}

    @staticmethod
    def _cifrar_pasta(pasta, destino="", senha=""):
        """Compacta a pasta e cifra o resultado, num passo."""
        if not os.path.isdir(pasta):
            raise FileNotFoundError_(
                f"'{pasta}' is not a folder.", doc="tecnicas/criptografia")
        alvo = destino or (pasta.rstrip("/\\") + ".zip.dfv")

        temporario = alvo + ".zip.tmp"
        try:
            ArcaneArchive._compactar(pasta, temporario)
            r = ArcaneCofre._cifrar_arquivo(temporario, alvo, senha)
        finally:
            if os.path.exists(temporario):
                os.remove(temporario)
        return r

    @staticmethod
    def _e_cifrado(caminho):
        """O arquivo e um cofre do DataForge?"""
        try:
            with open(caminho, "rb") as f:
                return f.read(len(MARCA)) == MARCA
        except OSError:
            return False

    @staticmethod
    def _informacao(caminho):
        """O cabecalho, sem precisar da senha.

        Ele nao e segredo — e o que diz COMO decifrar. Poder le-lo sem
        a senha e util para saber se vale a pena procurar a senha
        certa.
        """
        with open(caminho, "rb") as f:
            cabecalho = f.read(len(MARCA) + 4 + 16 + 12)
        if not cabecalho.startswith(MARCA):
            return {"cofre": False}
        n = struct.unpack("<I", cabecalho[len(MARCA):len(MARCA) + 4])[0]
        return {"cofre": True, "formato": MARCA.decode(),
                "iteracoes": n,
                "tamanho": os.path.getsize(caminho),
                "algoritmo": "ChaCha20-Poly1305 + PBKDF2-SHA256"}

    # ── chaves ──────────────────────────────────────────────

    @staticmethod
    def _chave_nova(tamanho=32):
        """Bytes aleatorios do sistema — mais fortes que qualquer senha."""
        return os.urandom(tamanho).hex()

    @staticmethod
    def _derivar(senha, sal="", iteracoes=None):
        """A chave que uma senha produz. Mesmo sal, mesma chave."""
        s = sal.encode("utf-8") if isinstance(sal, str) and sal else \
            (sal if isinstance(sal, bytes) else cifra.sal_novo())
        return {"chave": cifra.derivar(senha, s,
                                       int(iteracoes or cifra.ITERACOES)).hex(),
                "sal": s.hex()}

    # ── apagar ──────────────────────────────────────────────

    @staticmethod
    def _apagar_seguro(caminho, passadas=1):
        """Sobrescreve antes de apagar.

        Em disco magnetico, isso dificulta a recuperacao. Em SSD, NAO
        garante nada: o controlador escreve em outro bloco e o antigo
        continua la, fora do alcance do sistema. A funcao existe
        porque em disco magnetico ela ajuda — mas prometer apagamento
        seguro em SSD seria mentira.
        """
        if not os.path.isfile(caminho):
            return False
        tamanho = os.path.getsize(caminho)
        with open(caminho, "r+b") as f:
            for _ in range(max(1, passadas)):
                f.seek(0)
                restante = tamanho
                while restante > 0:
                    bloco = min(PEDACO, restante)
                    f.write(os.urandom(bloco))
                    restante -= bloco
                f.flush()
                os.fsync(f.fileno())
        os.remove(caminho)
        return True


class ArcaneArchive(dict):
    """Zip e tar — criar, listar, conferir e extrair com seguranca."""

    def __new__(cls):
        return {
            "compactar": cls._compactar,
            "extrair": cls._extrair,
            "listar": cls._listar,
            "conferir": cls._conferir,
            "acrescentar": cls._acrescentar,
            "ler_de": cls._ler_de,
            "compactar_tar": cls._compactar_tar,
            "extrair_tar": cls._extrair_tar,
        }

    # ── zip ─────────────────────────────────────────────────

    @staticmethod
    def _compactar(origem, destino, nivel=6):
        """Compacta um arquivo ou pasta inteira."""
        origem = str(origem).rstrip("/\\")
        if not os.path.exists(origem):
            raise FileNotFoundError_(f"'{origem}' does not exist.", doc="tecnicas/arquivos")

        n = 0
        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED,
                             compresslevel=nivel) as z:
            if os.path.isfile(origem):
                z.write(origem, os.path.basename(origem))
                n = 1
            else:
                base = os.path.dirname(origem) or "."
                for raiz, _, arquivos in os.walk(origem):
                    for a in arquivos:
                        completo = os.path.join(raiz, a)
                        z.write(completo, os.path.relpath(completo, base))
                        n += 1

        return {"arquivo": destino, "itens": n,
                "bytes": os.path.getsize(destino)}

    @staticmethod
    def _extrair(arquivo, destino=".", senha=""):
        """Extrai um zip, recusando entrada perigosa.

        Dois ataques com nome proprio, os dois verificados aqui:

        **Zip Slip** — uma entrada chamada '../../.ssh/authorized_keys'
        escreve FORA da pasta de destino. Foi explorado em dezenas de
        bibliotecas, e a defesa e conferir o caminho final resolvido.

        **Zip bomb** — 1 KB que descompacta para 10 GB, enchendo o
        disco. A defesa e olhar o tamanho declarado antes de extrair.
        """
        if not os.path.isfile(arquivo):
            raise FileNotFoundError_(f"'{arquivo}' does not exist.", doc="tecnicas/arquivos")

        destino_real = os.path.realpath(destino)
        os.makedirs(destino_real, exist_ok=True)

        extraidos = []
        with zipfile.ZipFile(arquivo) as z:
            if senha:
                z.setpassword(senha.encode("utf-8"))

            comprimido = sum(i.compress_size for i in z.infolist()) or 1
            total = sum(i.file_size for i in z.infolist())

            if total > TAMANHO_MAXIMO:
                raise UnsafeArchiveError(
                    f"this archive expands to {total / 1024**3:.1f} GB.",
                    nota=f"the ceiling is {TAMANHO_MAXIMO / 1024**3:.0f} GB",
                    dica="extract entry by entry with 'ler_de' if this is expected",
                    doc="tecnicas/arquivos")
            if (total > TAMANHO_SUSPEITO and
                    total / comprimido > EXPANSAO_MAXIMA):
                raise UnsafeArchiveError(
                    f"this archive expands {total // comprimido}x — "
                    f"it looks like a zip bomb.",
                    nota=(f"{total // 1024**2} MB from "
                          f"{comprimido // 1024} KB"),
                    doc="tecnicas/arquivos")

            for item in z.infolist():
                alvo = os.path.realpath(os.path.join(destino_real, item.filename))
                # A comparacao e sobre o caminho RESOLVIDO: '..' e link
                # simbolico ja foram desfeitos aqui.
                if not alvo.startswith(destino_real + os.sep) and \
                        alvo != destino_real:
                    raise UnsafeArchiveError(
                        f"the entry '{item.filename}' writes outside "
                        f"the destination.",
                        nota=("this is the Zip Slip attack — the entry "
                              "escapes with '..' or an absolute path"),
                        dica="do not extract archives from unknown sources",
                        doc="tecnicas/arquivos")
                z.extract(item, destino_real)
                extraidos.append(item.filename)

        return {"destino": destino_real, "itens": len(extraidos),
                "arquivos": extraidos[:200]}

    @staticmethod
    def _listar(arquivo):
        """O que ha dentro, sem extrair."""
        with zipfile.ZipFile(arquivo) as z:
            return [{"nome": i.filename,
                     "bytes": i.file_size,
                     "comprimido": i.compress_size,
                     "pasta": i.is_dir(),
                     "razao": (round(i.file_size / i.compress_size, 1)
                               if i.compress_size else 0)}
                    for i in z.infolist()]

    @staticmethod
    def _conferir(arquivo):
        """O arquivo esta integro? Devolve o nome do primeiro corrompido."""
        try:
            with zipfile.ZipFile(arquivo) as z:
                ruim = z.testzip()
                return {"integro": ruim is None, "corrompido": ruim or ""}
        except zipfile.BadZipFile as e:
            return {"integro": False, "corrompido": str(e)}

    @staticmethod
    def _acrescentar(arquivo, caminho, nome=""):
        """Acrescenta um arquivo a um zip existente."""
        with zipfile.ZipFile(arquivo, "a", zipfile.ZIP_DEFLATED) as z:
            z.write(caminho, nome or os.path.basename(caminho))
        return True

    @staticmethod
    def _ler_de(arquivo, nome, senha=""):
        """Le UM arquivo de dentro, sem extrair o resto."""
        with zipfile.ZipFile(arquivo) as z:
            if senha:
                z.setpassword(senha.encode("utf-8"))
            with z.open(nome) as f:
                bruto = f.read()
        try:
            return bruto.decode("utf-8")
        except UnicodeDecodeError:
            return bruto

    # ── tar ─────────────────────────────────────────────────

    @staticmethod
    def _compactar_tar(origem, destino, compressao="gz"):
        modo = {"gz": "w:gz", "bz2": "w:bz2", "xz": "w:xz",
                "": "w"}.get(compressao, "w:gz")
        with tarfile.open(destino, modo) as t:
            t.add(origem, arcname=os.path.basename(str(origem).rstrip("/\\")))
        return {"arquivo": destino, "bytes": os.path.getsize(destino)}

    @staticmethod
    def _extrair_tar(arquivo, destino="."):
        """Extrai um tar, com a mesma checagem de caminho do zip."""
        destino_real = os.path.realpath(destino)
        os.makedirs(destino_real, exist_ok=True)

        with tarfile.open(arquivo) as t:
            for membro in t.getmembers():
                alvo = os.path.realpath(
                    os.path.join(destino_real, membro.name))
                if not alvo.startswith(destino_real + os.sep) and \
                        alvo != destino_real:
                    raise UnsafeArchiveError(
                        f"the entry '{membro.name}' writes outside "
                        f"the destination.",
                        nota="this is the Zip Slip attack, in tar form",
                        doc="tecnicas/arquivos")
                if membro.issym() or membro.islnk():
                    raise UnsafeArchiveError(
                        f"'{membro.name}' is a link.",
                        nota="a link inside an archive can point anywhere",
                        doc="tecnicas/arquivos")
            # 'filter=data' e a defesa do proprio Python, e ela recusa
            # permissao estranha e dono de outro usuario.
            try:
                t.extractall(destino_real, filter="data")
            except TypeError:
                t.extractall(destino_real)       # Python < 3.12

        return {"destino": destino_real}

