# -*- coding: utf-8 -*-
"""
Parquet em Python puro — o formato colunar, escrito e lido aqui.

Sem pyarrow, sem fastparquet: um arquivo gerado por este módulo é lido
pelo pandas, pelo DuckDB e pelo Spark, e um arquivo gerado por eles é
lido aqui.

─── Por que colunar ────────────────────────────────────────

Um CSV guarda linha a linha. Para somar uma coluna de 40 milhões de
linhas, o disco entrega as outras trinta colunas junto — e elas são
jogadas fora. O Parquet guarda coluna a coluna: ler uma coluna lê só
ela.

E valores do mesmo tipo, lado a lado, comprimem muito melhor. Uma
coluna de datas repetidas ou de categorias encolhe uma ordem de
grandeza; a mesma informação espalhada por linhas, não.

─── O formato, por dentro ──────────────────────────────────

    PAR1                       ← marca de abertura
    [dados da coluna 1]        ← páginas, uma por bloco de valores
    [dados da coluna 2]
    …
    [metadados em Thrift]      ← esquema, onde cada coluna começa
    <4 bytes: tamanho deles>
    PAR1                       ← marca de fechamento

Os metadados ficam no FIM, e não no começo. É o que permite escrever um
arquivo sem saber de antemão quantas linhas ele terá — e é por isso que
o leitor busca o fim primeiro.

─── Thrift compact, escrito à mão ──────────────────────────

Os metadados são serializados em Thrift compact protocol. Não há
biblioteca aqui, então ele está implementado abaixo: inteiros em zigzag
varint, campos por delta de id, estruturas aninhadas.

É a parte que mais parece arbitrária e a que menos pode errar por um
byte — um deslocamento de um único byte no rodapé faz o pyarrow
recusar o arquivo inteiro sem dizer onde. Por isso os testes leem de
volta com o pyarrow quando ele existe.
"""

import gzip
import struct

from ..errors import ValueError_

MARCA = b"PAR1"

# ── Thrift: os tipos do protocolo compact ──
T_PARADA = 0x0
T_VERDADE = 0x1
T_FALSO = 0x2
T_I32 = 0x5
T_I64 = 0x6
T_DOUBLE = 0x7
T_BINARIO = 0x8
T_LISTA = 0x9
T_ESTRUTURA = 0xC

# ── Parquet: os tipos físicos ──
P_BOOLEAN, P_INT32, P_INT64 = 0, 1, 2
P_FLOAT, P_DOUBLE, P_BYTE_ARRAY = 4, 5, 6

#: tipo físico -> (nome no DataForge, como converter para escrever)
TIPOS = {
    P_BOOLEAN: "booleano",
    P_INT32: "inteiro",
    P_INT64: "inteiro",
    P_FLOAT: "numero",
    P_DOUBLE: "numero",
    P_BYTE_ARRAY: "texto",
}

#: Quantas linhas por grupo.
#:
#: O grupo é a unidade que um leitor consegue PULAR inteira: uma
#: consulta com filtro lê o mínimo e o máximo de cada coluna no grupo e
#: descarta o grupo todo se ele não puder conter o que se procura.
#: Grupos grandes demais tornam esse descarte grosseiro; pequenos demais
#: enchem o rodapé de metadado.
LINHAS_POR_GRUPO = 100_000


# ═════════════════════════════════════════════════════════════
#  Thrift compact — escrever
# ═════════════════════════════════════════════════════════════

class _Escritor:
    """Serializa em Thrift compact.

    O 'ultimo_id' existe porque o protocolo grava a DIFERENÇA entre o id
    do campo atual e o anterior, num nibble. Campos em ordem crescente e
    próximos cabem num byte só — que é o ponto do 'compact'.
    """

    def __init__(self):
        self.saida = bytearray()
        self.ultimo_id = 0
        self.pilha = []

    def varint(self, n):
        while True:
            byte = n & 0x7F
            n >>= 7
            if n:
                self.saida.append(byte | 0x80)
            else:
                self.saida.append(byte)
                return

    def zigzag(self, n):
        """Inteiro com sinal: o bit menos significativo carrega o sinal.

        Sem isso, -1 seria dez bytes de 0xFF — o varint só é curto para
        números pequenos e POSITIVOS.
        """
        self.varint((n << 1) ^ (n >> 63) if n < 0 else (n << 1))

    def campo(self, ident, tipo):
        delta = ident - self.ultimo_id
        if 0 < delta <= 15:
            self.saida.append((delta << 4) | tipo)
        else:
            self.saida.append(tipo)
            self.zigzag(ident)
        self.ultimo_id = ident

    def i32(self, ident, valor):
        self.campo(ident, T_I32)
        self.zigzag(valor)

    def i64(self, ident, valor):
        self.campo(ident, T_I64)
        self.zigzag(valor)

    def booleano(self, ident, valor):
        self.campo(ident, T_VERDADE if valor else T_FALSO)

    def binario(self, ident, valor):
        self.campo(ident, T_BINARIO)
        bruto = valor.encode("utf-8") if isinstance(valor, str) else valor
        self.varint(len(bruto))
        self.saida += bruto

    def lista(self, ident, tipo, quantos):
        self.campo(ident, T_LISTA)
        if quantos < 15:
            self.saida.append((quantos << 4) | tipo)
        else:
            self.saida.append(0xF0 | tipo)
            self.varint(quantos)

    def abrir(self, ident):
        self.campo(ident, T_ESTRUTURA)
        self.pilha.append(self.ultimo_id)
        self.ultimo_id = 0

    def abrir_em_lista(self):
        """Um struct dentro de lista não tem cabeçalho de campo."""
        self.pilha.append(self.ultimo_id)
        self.ultimo_id = 0

    def fechar(self):
        """Encerra a estrutura atual.

        A estrutura RAIZ nunca foi aberta com 'abrir' — ela e o
        documento inteiro —, mas tambem precisa do byte de parada. Por
        isso a pilha vazia nao e erro: e o fim do documento.
        """
        self.saida.append(T_PARADA)
        self.ultimo_id = self.pilha.pop() if self.pilha else 0

    def bytes(self):
        return bytes(self.saida)


class _Leitor:
    """Lê Thrift compact."""

    def __init__(self, dados, posicao=0):
        self.dados = dados
        self.i = posicao
        self.ultimo_id = 0
        self.pilha = []

    def varint(self):
        resultado = deslocamento = 0
        while True:
            byte = self.dados[self.i]
            self.i += 1
            resultado |= (byte & 0x7F) << deslocamento
            if not byte & 0x80:
                return resultado
            deslocamento += 7

    def zigzag(self):
        n = self.varint()
        return (n >> 1) ^ -(n & 1)

    def campo(self):
        """(id, tipo). Tipo T_PARADA marca o fim da estrutura."""
        cabecalho = self.dados[self.i]
        self.i += 1
        if cabecalho == T_PARADA:
            self.ultimo_id = self.pilha.pop() if self.pilha else 0
            return 0, T_PARADA
        tipo = cabecalho & 0x0F
        delta = (cabecalho & 0xF0) >> 4
        ident = self.ultimo_id + delta if delta else self.zigzag()
        self.ultimo_id = ident
        return ident, tipo

    def binario(self):
        tamanho = self.varint()
        bruto = self.dados[self.i:self.i + tamanho]
        self.i += tamanho
        return bruto

    def cabecalho_de_lista(self):
        cabecalho = self.dados[self.i]
        self.i += 1
        tipo = cabecalho & 0x0F
        quantos = (cabecalho & 0xF0) >> 4
        if quantos == 15:
            quantos = self.varint()
        return tipo, quantos

    def entrar(self):
        self.pilha.append(self.ultimo_id)
        self.ultimo_id = 0

    def pular(self, tipo):
        """Pula um valor cujo campo não interessa.

        Sem isto, um arquivo escrito por outra ferramenta — que traz
        campos que não lemos — deslocaria tudo daí para a frente.
        """
        if tipo in (T_VERDADE, T_FALSO):
            return
        if tipo in (T_I32, T_I64):
            self.zigzag()
        elif tipo == T_DOUBLE:
            self.i += 8
        elif tipo == T_BINARIO:
            self.binario()
        elif tipo == T_LISTA:
            interno, quantos = self.cabecalho_de_lista()
            for _ in range(quantos):
                if interno == T_ESTRUTURA:
                    self.entrar()
                    self.pular_estrutura()
                else:
                    self.pular(interno)
        elif tipo == T_ESTRUTURA:
            self.entrar()
            self.pular_estrutura()

    def pular_estrutura(self):
        while True:
            _, tipo = self.campo()
            if tipo == T_PARADA:
                return
            self.pular(tipo)


# ═════════════════════════════════════════════════════════════
#  Valores: PLAIN encoding
# ═════════════════════════════════════════════════════════════

def _tipo_da_coluna(valores):
    """O tipo físico que cabe em todos os valores.

    Um inteiro que não cabe em 64 bits, ou um número com casas, sobe
    para DOUBLE. Misturar tipos numa coluna é o que mais quebra na
    leitura — o Parquet é tipado, e o CSV que o originou não era.
    """
    presentes = [v for v in valores if v is not None]
    if not presentes:
        return P_BYTE_ARRAY
    if all(isinstance(v, bool) for v in presentes):
        return P_BOOLEAN
    if all(isinstance(v, int) and not isinstance(v, bool) for v in presentes):
        if all(-(2 ** 63) <= v < 2 ** 63 for v in presentes):
            return P_INT64
        return P_DOUBLE
    if all(isinstance(v, (int, float)) and not isinstance(v, bool)
           for v in presentes):
        return P_DOUBLE
    return P_BYTE_ARRAY


def _plain(valores, tipo):
    """Os valores, um atrás do outro, sem cabeçalho."""
    saida = bytearray()
    if tipo == P_INT64:
        for v in valores:
            saida += struct.pack("<q", int(v))
    elif tipo == P_DOUBLE:
        for v in valores:
            saida += struct.pack("<d", float(v))
    elif tipo == P_BOOLEAN:
        # Um bit por valor, do menos significativo para o mais.
        atual = quantos = 0
        for v in valores:
            if v:
                atual |= 1 << quantos
            quantos += 1
            if quantos == 8:
                saida.append(atual)
                atual = quantos = 0
        if quantos:
            saida.append(atual)
    else:
        for v in valores:
            bruto = v.encode("utf-8") if isinstance(v, str) else \
                bytes(v) if isinstance(v, (bytes, bytearray)) else \
                str(v).encode("utf-8")
            saida += struct.pack("<I", len(bruto)) + bruto
    return bytes(saida)


def _ler_plain(dados, tipo, quantos):
    valores, i = [], 0
    if tipo == P_INT64:
        for _ in range(quantos):
            valores.append(struct.unpack_from("<q", dados, i)[0])
            i += 8
    elif tipo == P_INT32:
        for _ in range(quantos):
            valores.append(struct.unpack_from("<i", dados, i)[0])
            i += 4
    elif tipo == P_DOUBLE:
        for _ in range(quantos):
            valores.append(struct.unpack_from("<d", dados, i)[0])
            i += 8
    elif tipo == P_FLOAT:
        for _ in range(quantos):
            valores.append(struct.unpack_from("<f", dados, i)[0])
            i += 4
    elif tipo == P_BOOLEAN:
        for n in range(quantos):
            valores.append(bool(dados[n // 8] & (1 << (n % 8))))
    else:
        for _ in range(quantos):
            tamanho = struct.unpack_from("<I", dados, i)[0]
            i += 4
            bruto = dados[i:i + tamanho]
            i += tamanho
            try:
                valores.append(bruto.decode("utf-8"))
            except UnicodeDecodeError:
                valores.append(bruto)
    return valores


def _rle_niveis(niveis, bits=1):
    """Os níveis de definição, em RLE/bit-packed híbrido.

    O nível diz se o valor está presente (1) ou é nulo (0). Uma coluna
    sem nulo nenhum vira uma corrida só — três bytes para um milhão de
    linhas, que é o ponto.
    """
    saida = bytearray()
    i = 0
    while i < len(niveis):
        corrida = 1
        while i + corrida < len(niveis) and niveis[i + corrida] == niveis[i]:
            corrida += 1
        # cabeçalho par = RLE; o valor ocupa ceil(bits/8) bytes
        cabecalho = corrida << 1
        while cabecalho >= 0x80:
            saida.append((cabecalho & 0x7F) | 0x80)
            cabecalho >>= 7
        saida.append(cabecalho)
        saida += bytes([niveis[i]]) * max(1, (bits + 7) // 8)
        i += corrida
    return bytes(saida)


def _ler_rle(dados, quantos, bits=1):
    """Desfaz o RLE/bit-packed hibrido dos niveis.

    Sao dois formatos no mesmo fluxo, e o bit menos significativo do
    cabecalho diz qual: par e uma CORRIDA (o valor repetido n vezes),
    impar e um bloco BIT-PACKED (8 valores por grupo, empacotados).

    Nos escrevemos so corridas — uma coluna sem nulo vira tres bytes
    para um milhao de linhas. Mas o pyarrow escreve bit-packed, e ler
    arquivo dos outros e metade do ponto de falar Parquet.
    """
    niveis, i = [], 0
    largura_rle = max(1, (bits + 7) // 8)
    mascara = (1 << bits) - 1

    while len(niveis) < quantos and i < len(dados):
        cabecalho = deslocamento = 0
        while i < len(dados):
            byte = dados[i]
            i += 1
            cabecalho |= (byte & 0x7F) << deslocamento
            if not byte & 0x80:
                break
            deslocamento += 7

        if cabecalho & 1:
            # Bit-packed: 'grupos' blocos de 8 valores, cada valor com
            # 'bits' bits, do menos significativo para o mais.
            grupos = cabecalho >> 1
            bytes_do_bloco = grupos * bits
            bloco = dados[i:i + bytes_do_bloco]
            i += bytes_do_bloco
            for n in range(grupos * 8):
                if len(niveis) >= quantos:
                    break
                inicio_bit = n * bits
                byte = inicio_bit // 8
                if byte >= len(bloco):
                    break
                # O valor pode cruzar TRES bytes: um indice de 16 bits
                # comecando no bit 1 ocupa do byte 0 ao 2. Uma janela de
                # dois bytes truncava o topo — e o erro so aparecia um
                # valor em mil, com o resto certo, que e o pior jeito de
                # um bug de formato se manifestar.
                fim = min(len(bloco), byte + (bits + 15) // 8)
                janela = int.from_bytes(bloco[byte:fim], "little")
                niveis.append((janela >> (inicio_bit % 8)) & mascara)
        else:
            corrida = cabecalho >> 1
            valor = int.from_bytes(dados[i:i + largura_rle], "little")
            i += largura_rle
            if corrida == 0:
                break                       # cabecalho vazio: fim
            niveis.extend([valor] * min(corrida, quantos - len(niveis)))

    return niveis[:quantos]


# ═════════════════════════════════════════════════════════════
#  Escrever o arquivo
# ═════════════════════════════════════════════════════════════

def _pagina(valores, tipo, tem_nulo, compressao):
    """Uma página: cabeçalho Thrift + níveis + valores.

    O cabeçalho declara os tamanhos COMPRIMIDO e cru. Errar um deles faz
    o leitor pedir a quantidade errada de bytes e falhar no meio do
    arquivo, longe da causa.
    """
    presentes = [v for v in valores if v is not None]
    corpo = bytearray()
    if tem_nulo:
        niveis = [0 if v is None else 1 for v in valores]
        bruto = _rle_niveis(niveis)
        corpo += struct.pack("<I", len(bruto)) + bruto
    corpo += _plain(presentes, tipo)
    corpo = bytes(corpo)

    cru = len(corpo)
    if compressao == "gzip":
        # mtime=0: sem isso o mesmo dado geraria bytes diferentes a cada
        # gravação, e comparar dois arquivos deixaria de significar algo.
        comprimido = gzip.compress(corpo, mtime=0)
    else:
        comprimido = corpo

    cabecalho = _Escritor()
    cabecalho.i32(1, 0)                       # type = DATA_PAGE
    cabecalho.i32(2, cru)                     # uncompressed_page_size
    cabecalho.i32(3, len(comprimido))         # compressed_page_size
    cabecalho.abrir(5)                        # data_page_header
    cabecalho.i32(1, len(valores))            # num_values (com os nulos)
    cabecalho.i32(2, 0)                       # encoding = PLAIN
    cabecalho.i32(3, 3)                       # definition_level = RLE
    cabecalho.i32(4, 3)                       # repetition_level = RLE
    cabecalho.fechar()
    cabecalho.fechar()
    return cabecalho.bytes() + comprimido, cru, len(comprimido)


def escrever(caminho, linhas, compressao="gzip", por_grupo=LINHAS_POR_GRUPO):
    """Grava as linhas em Parquet. Devolve o que foi escrito."""
    linhas = list(linhas or [])
    if not linhas:
        raise ValueError_(
            "não há o que gravar: a lista está vazia.",
            dica="um Parquet sem coluna nenhuma não tem esquema, e nenhum "
                 "leitor sabe o que fazer com ele",
            doc="tecnicas/parquet")

    colunas = []
    for linha in linhas:
        if not isinstance(linha, dict):
            raise ValueError_(
                f"cada linha precisa ser um vault; veio "
                f"{type(linha).__name__}.", doc="tecnicas/parquet")
        for chave in linha:
            if chave not in colunas:
                colunas.append(chave)

    dados = {c: [l.get(c) for l in linhas] for c in colunas}
    tipos = {c: _tipo_da_coluna(dados[c]) for c in colunas}
    tem_nulo = {c: any(v is None for v in dados[c]) for c in colunas}

    corpo = bytearray(MARCA)
    grupos = []
    for inicio in range(0, len(linhas), por_grupo):
        fim = min(inicio + por_grupo, len(linhas))
        pedaco = {c: dados[c][inicio:fim] for c in colunas}
        chunks = []
        for coluna in colunas:
            comeco = len(corpo)
            pagina, cru, comprimido = _pagina(
                pedaco[coluna], tipos[coluna], tem_nulo[coluna], compressao)
            corpo += pagina
            chunks.append({
                "coluna": coluna, "tipo": tipos[coluna],
                "inicio": comeco, "cru": len(pagina) - comprimido + cru,
                "comprimido": len(pagina), "valores": fim - inicio,
            })
        grupos.append({"chunks": chunks, "linhas": fim - inicio})

    rodape = _metadados(colunas, tipos, tem_nulo, grupos, len(linhas))
    corpo += rodape + struct.pack("<I", len(rodape)) + MARCA

    with open(caminho, "wb") as f:
        f.write(corpo)

    return {
        "arquivo": caminho, "linhas": len(linhas),
        "colunas": len(colunas), "grupos": len(grupos),
        "bytes": len(corpo), "compressao": compressao,
        "esquema": {c: TIPOS[tipos[c]] for c in colunas},
    }


def _metadados(colunas, tipos, tem_nulo, grupos, total):
    """O rodapé: esquema, grupos e onde cada coluna começa."""
    m = _Escritor()
    m.i32(1, 1)                                     # version

    # ── schema: a raiz, depois uma folha por coluna ──
    m.lista(2, T_ESTRUTURA, len(colunas) + 1)
    m.abrir_em_lista()
    m.binario(4, "forja")                           # name
    m.i32(5, len(colunas))                          # num_children
    m.fechar()
    for coluna in colunas:
        m.abrir_em_lista()
        m.i32(1, tipos[coluna])                     # type
        # 0 = REQUIRED, 1 = OPTIONAL. Declarar OPTIONAL numa coluna sem
        # nulo custaria os níveis de definição à toa.
        m.i32(3, 1 if tem_nulo[coluna] else 0)      # repetition_type
        m.binario(4, coluna)                        # name
        if tipos[coluna] == P_BYTE_ARRAY:
            m.i32(6, 0)                             # converted_type = UTF8
        m.fechar()

    m.i64(3, total)                                 # num_rows

    m.lista(4, T_ESTRUTURA, len(grupos))            # row_groups
    for grupo in grupos:
        m.abrir_em_lista()
        m.lista(1, T_ESTRUTURA, len(grupo["chunks"]))
        for chunk in grupo["chunks"]:
            m.abrir_em_lista()
            m.i64(2, chunk["inicio"])               # file_offset
            m.abrir(3)                              # meta_data
            m.i32(1, chunk["tipo"])                 # type
            m.lista(2, T_I32, 1)                    # encodings
            m.zigzag(0)                             # PLAIN
            m.lista(3, T_BINARIO, 1)                # path_in_schema
            bruto = chunk["coluna"].encode("utf-8")
            m.varint(len(bruto))
            m.saida += bruto
            m.i32(4, 2 if grupo is not None and
                  chunk["comprimido"] != chunk["cru"] else 0)   # codec
            m.i64(5, chunk["valores"])              # num_values
            m.i64(6, chunk["cru"])                  # total_uncompressed_size
            m.i64(7, chunk["comprimido"])           # total_compressed_size
            m.i64(9, chunk["inicio"])               # data_page_offset
            m.fechar()
            m.fechar()
        m.i64(2, sum(c["comprimido"] for c in grupo["chunks"]))
        m.i64(3, grupo["linhas"])
        m.fechar()

    m.binario(6, "DataForge")                       # created_by
    m.fechar()
    return m.bytes()


# ═════════════════════════════════════════════════════════════
#  Ler o arquivo
# ═════════════════════════════════════════════════════════════

def _ler_metadados(dados):
    """O rodapé, desmontado no que precisamos dele."""
    if len(dados) < 12 or dados[:4] != MARCA or dados[-4:] != MARCA:
        raise ValueError_(
            "isto não é um arquivo Parquet.",
            nota="ele precisa começar e terminar com 'PAR1'",
            doc="tecnicas/parquet")
    tamanho = struct.unpack("<I", dados[-8:-4])[0]
    inicio = len(dados) - 8 - tamanho
    if inicio < 4:
        raise ValueError_("o rodapé do Parquet está corrompido.",
                          doc="tecnicas/parquet")

    leitor = _Leitor(dados, inicio)
    esquema, grupos, linhas = [], [], 0

    while True:
        ident, tipo = leitor.campo()
        if tipo == T_PARADA:
            break
        if ident == 2 and tipo == T_LISTA:              # schema
            _, quantos = leitor.cabecalho_de_lista()
            for _ in range(quantos):
                leitor.entrar()
                esquema.append(_ler_elemento(leitor))
        elif ident == 3 and tipo in (T_I32, T_I64):     # num_rows
            linhas = leitor.zigzag()
        elif ident == 4 and tipo == T_LISTA:            # row_groups
            _, quantos = leitor.cabecalho_de_lista()
            for _ in range(quantos):
                leitor.entrar()
                grupos.append(_ler_grupo(leitor))
        else:
            leitor.pular(tipo)

    return {"esquema": [e for e in esquema if e.get("tipo") is not None],
            "grupos": grupos, "linhas": linhas}


def _ler_elemento(leitor):
    elemento = {}
    while True:
        ident, tipo = leitor.campo()
        if tipo == T_PARADA:
            return elemento
        if ident == 1:
            elemento["tipo"] = leitor.zigzag()
        elif ident == 3:
            elemento["repeticao"] = leitor.zigzag()
        elif ident == 4:
            elemento["nome"] = leitor.binario().decode("utf-8")
        else:
            leitor.pular(tipo)


def _ler_grupo(leitor):
    grupo = {"chunks": [], "linhas": 0}
    while True:
        ident, tipo = leitor.campo()
        if tipo == T_PARADA:
            return grupo
        if ident == 1 and tipo == T_LISTA:
            _, quantos = leitor.cabecalho_de_lista()
            for _ in range(quantos):
                leitor.entrar()
                grupo["chunks"].append(_ler_chunk(leitor))
        elif ident == 3:
            grupo["linhas"] = leitor.zigzag()
        else:
            leitor.pular(tipo)


def _ler_chunk(leitor):
    chunk = {}
    while True:
        ident, tipo = leitor.campo()
        if tipo == T_PARADA:
            return chunk
        if ident == 3 and tipo == T_ESTRUTURA:
            leitor.entrar()
            chunk.update(_ler_meta_da_coluna(leitor))
        else:
            leitor.pular(tipo)


def _ler_meta_da_coluna(leitor):
    meta = {}
    while True:
        ident, tipo = leitor.campo()
        if tipo == T_PARADA:
            return meta
        if ident == 1:
            meta["tipo"] = leitor.zigzag()
        elif ident == 3 and tipo == T_LISTA:
            _, quantos = leitor.cabecalho_de_lista()
            partes = [leitor.binario().decode("utf-8") for _ in range(quantos)]
            meta["coluna"] = ".".join(partes)
        elif ident == 4:
            meta["codec"] = leitor.zigzag()
        elif ident == 5:
            meta["valores"] = leitor.zigzag()
        elif ident == 9:
            meta["inicio"] = leitor.zigzag()
        elif ident == 11:
            meta["dicionario"] = leitor.zigzag()
        else:
            leitor.pular(tipo)


def _cabecalho_da_pagina(dados, posicao):
    """(tipo da pagina, valores, cru, comprimido, encoding, inicio do corpo)."""
    leitor = _Leitor(dados, posicao)
    especie = cru = comprimido = quantos = encoding = 0
    while True:
        ident, tipo = leitor.campo()
        if tipo == T_PARADA:
            break
        if ident == 1:
            especie = leitor.zigzag()
        elif ident == 2:
            cru = leitor.zigzag()
        elif ident == 3:
            comprimido = leitor.zigzag()
        elif ident in (5, 7) and tipo == T_ESTRUTURA:
            # 5 = data_page_header, 7 = dictionary_page_header
            leitor.entrar()
            while True:
                sub, subtipo = leitor.campo()
                if subtipo == T_PARADA:
                    break
                if sub == 1:
                    quantos = leitor.zigzag()
                elif sub == 2:
                    encoding = leitor.zigzag()
                else:
                    leitor.pular(subtipo)
        else:
            leitor.pular(tipo)
    return especie, quantos, cru, comprimido, encoding, leitor.i


def _descomprimir(corpo, codec):
    if codec == 2:
        return gzip.decompress(corpo)
    if codec in (0, None):
        return corpo
    nomes = {1: "snappy", 3: "lzo", 4: "brotli", 5: "lz4", 6: "zstd"}
    raise ValueError_(
        f"este Parquet usa a compressão "
        f"{nomes.get(codec, codec)}, que ainda não lemos.",
        nota="lemos 'sem compressão' e 'gzip'",
        dica="regrave com compression='gzip' ou 'none' na ferramenta de origem",
        doc="tecnicas/parquet")


def _ler_dicionario(dados, posicao, tipo_da_coluna, codec):
    """A página de dicionário: os valores distintos, em PLAIN."""
    _, quantos, _, comprimido, _, inicio = _cabecalho_da_pagina(dados, posicao)
    corpo = _descomprimir(dados[inicio:inicio + comprimido], codec)
    return _ler_plain(corpo, tipo_da_coluna, quantos)


def _indices_rle(corpo, quantos):
    """Os índices do dicionário.

    O primeiro byte é a LARGURA em bits — ela depende de quantos valores
    distintos há, e é por isso que uma coluna de categorias fica tão
    pequena: cinco valores distintos cabem em 3 bits cada.
    """
    if not corpo:
        return []
    bits = corpo[0]
    if bits == 0:
        return [0] * quantos
    return _ler_rle(corpo[1:], quantos, bits)


def _ler_pagina(dados, posicao, tipo_da_coluna, opcional, codec,
                dicionario=None):
    """Uma página. Devolve (valores, próxima posição)."""
    _, quantos, cru, comprimido, encoding, corpo_em = _cabecalho_da_pagina(
        dados, posicao)
    leitor = _Leitor(dados, corpo_em)

    corpo = _descomprimir(dados[corpo_em:corpo_em + comprimido], codec)

    i = 0
    niveis = None
    if opcional:
        tamanho = struct.unpack_from("<I", corpo, 0)[0]
        i = 4
        niveis = _ler_rle(corpo[i:i + tamanho], quantos)
        i += tamanho

    presentes = niveis.count(1) if niveis is not None else quantos
    if encoding in (2, 8) and dicionario is not None:
        # PLAIN_DICTIONARY / RLE_DICTIONARY: a página guarda ÍNDICES, e
        # os valores estão na página de dicionário. É como a maioria dos
        # Parquet do mundo é escrita — ler só PLAIN leria quase nada.
        indices = _indices_rle(corpo[i:], presentes)
        valores = [dicionario[k] if k < len(dicionario) else None
                   for k in indices]
    else:
        valores = _ler_plain(corpo[i:], tipo_da_coluna, presentes)

    if niveis is not None:
        completos, k = [], 0
        for nivel in niveis:
            if nivel:
                completos.append(valores[k])
                k += 1
            else:
                completos.append(None)
        valores = completos

    return valores, corpo_em + comprimido


def ler(caminho, colunas=None):
    """As linhas do arquivo, como vaults.

    'colunas' lê SÓ o que se pediu — que é o ponto do formato colunar:
    ler uma coluna de trinta não toca nas outras vinte e nove.
    """
    with open(caminho, "rb") as f:
        dados = f.read()

    meta = _ler_metadados(dados)
    nomes = [e["nome"] for e in meta["esquema"]]
    opcional = {e["nome"]: e.get("repeticao") == 1 for e in meta["esquema"]}
    pedidas = list(colunas) if colunas else nomes

    faltando = [c for c in pedidas if c not in nomes]
    if faltando:
        raise ValueError_(
            f"o arquivo não tem a coluna {', '.join(faltando)}.",
            nota=f"ele tem: {', '.join(nomes)}",
            doc="tecnicas/parquet")

    por_coluna = {c: [] for c in pedidas}
    for grupo in meta["grupos"]:
        for chunk in grupo["chunks"]:
            nome = chunk.get("coluna")
            if nome not in por_coluna:
                continue
            codec = chunk.get("codec", 0)
            dicionario = None
            if chunk.get("dicionario"):
                dicionario = _ler_dicionario(
                    dados, chunk["dicionario"], chunk["tipo"], codec)

            # Um chunk pode ter VÁRIAS páginas: o leitor anda de página
            # em página até completar o que o grupo declarou.
            posicao = chunk["inicio"]
            lidos = 0
            alvo = chunk.get("valores", grupo["linhas"])
            while lidos < alvo:
                especie, _, _, _, _, _ = _cabecalho_da_pagina(dados, posicao)
                if especie == 2:                    # dicionário: pula
                    _, _, _, comprimido, _, corpo_em = \
                        _cabecalho_da_pagina(dados, posicao)
                    posicao = corpo_em + comprimido
                    continue
                valores, posicao = _ler_pagina(
                    dados, posicao, chunk["tipo"],
                    opcional.get(nome, False), codec, dicionario)
                if not valores:
                    break
                por_coluna[nome].extend(valores)
                lidos += len(valores)

    total = max((len(v) for v in por_coluna.values()), default=0)
    return [{c: por_coluna[c][i] if i < len(por_coluna[c]) else None
             for c in pedidas} for i in range(total)]


def esquema(caminho):
    """O que há dentro, sem ler os dados."""
    with open(caminho, "rb") as f:
        f.seek(-8, 2)
        tamanho = struct.unpack("<I", f.read(4))[0]
        f.seek(0, 2)
        fim = f.tell()
        f.seek(0)
        dados = f.read()
    meta = _ler_metadados(dados)
    return {
        "linhas": meta["linhas"],
        "grupos": len(meta["grupos"]),
        "bytes": fim,
        "colunas": [{"nome": e["nome"],
                     "tipo": TIPOS.get(e.get("tipo"), "?"),
                     "aceita_vazio": e.get("repeticao") == 1}
                    for e in meta["esquema"]],
    }
