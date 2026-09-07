"""
Arcane.Excel — planilhas .xlsx sem dependencia externa

Um .xlsx e um ZIP de arquivos XML. Ler e escrever isso e trabalho
chato, mas nao e trabalho dificil — e evita arrastar openpyxl para uma
linguagem que se orgulha de nao ter dependencia de runtime.

    adopt Arcane.Excel as Xls

    livro := Xls.new()
    Xls.sheet(livro, "Vendas", [
        ["Produto", "Qtd", "Preco"],
        ["Martelo", 3, 89.9]
    ])
    Xls.save(livro, "vendas.xlsx")

    lido := Xls.read("vendas.xlsx")
    out Xls.rows(lido, "Vendas")

Suporta: varias abas, cabecalho, tipos (texto/numero/booleano/data),
formulas, largura de coluna, negrito no cabecalho, congelar painel,
e leitura de arquivos gerados pelo Excel, LibreOffice e Google Sheets.
"""

import datetime
import os
import re
import xml.etree.ElementTree as ET
import zipfile

#: 1900-01-00 — a epoca do Excel. O bug do ano bissexto de 1900 esta
#: embutido no formato desde o Lotus 1-2-3; nao da para "consertar".
EPOCA = datetime.datetime(1899, 12, 30)

_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


# ─────────────────────────────────────────────────────────────
#  Enderecos de celula
# ─────────────────────────────────────────────────────────────

def coluna_para_letra(indice):
    """0 → A, 25 → Z, 26 → AA."""
    letras = ""
    indice += 1
    while indice > 0:
        indice, resto = divmod(indice - 1, 26)
        letras = chr(65 + resto) + letras
    return letras


def letra_para_coluna(letras):
    """A → 0, AA → 26."""
    total = 0
    for caractere in letras.upper():
        total = total * 26 + (ord(caractere) - 64)
    return total - 1


def endereco(linha, coluna):
    """(0, 0) → 'A1'."""
    return f"{coluna_para_letra(coluna)}{linha + 1}"


def ler_endereco(texto):
    """'B7' → (6, 1)."""
    achado = re.match(r"([A-Za-z]+)(\d+)", texto.strip())
    if achado is None:
        raise ValueError(f"endereço de célula inválido: {texto!r}")
    return int(achado.group(2)) - 1, letra_para_coluna(achado.group(1))


# ─────────────────────────────────────────────────────────────
#  Modelo
# ─────────────────────────────────────────────────────────────

class Aba:
    """Uma planilha. As celulas ficam num dict esparso: uma planilha de
    10 mil linhas com 3 preenchidas ocupa 3 celulas, nao 10 mil listas."""

    def __init__(self, nome):
        self.nome = nome
        self.celulas = {}            # (linha, coluna) -> valor
        self.formulas = {}           # (linha, coluna) -> "SUM(A1:A9)"
        self.larguras = {}           # coluna -> largura
        self.negrito = set()         # linhas em negrito
        self.congelar = None         # "A2" congela a primeira linha

    @property
    def altura(self):
        # As formulas contam: uma celula com '=SUM(...)' e sem valor
        # ficava fora da area e simplesmente nao era gravada.
        return max((l for l, _ in self._ocupadas()), default=-1) + 1

    @property
    def largura(self):
        return max((c for _, c in self._ocupadas()), default=-1) + 1

    def _ocupadas(self):
        return set(self.celulas) | set(self.formulas)

    def por(self, linha, coluna, valor):
        if valor is None:
            self.celulas.pop((linha, coluna), None)
        else:
            self.celulas[(linha, coluna)] = valor

    def pega(self, linha, coluna, padrao=None):
        return self.celulas.get((linha, coluna), padrao)

    def linhas(self):
        """Tudo como lista de listas, com void nos buracos."""
        return [[self.celulas.get((l, c)) for c in range(self.largura)]
                for l in range(self.altura)]


class Livro:
    def __init__(self):
        self.abas = []

    def aba(self, nome):
        for a in self.abas:
            if a.nome == nome:
                return a
        return None

    def nova_aba(self, nome):
        existente = self.aba(nome)
        if existente is not None:
            return existente
        aba = Aba(nome)
        self.abas.append(aba)
        return aba


# ─────────────────────────────────────────────────────────────
#  Escrita
# ─────────────────────────────────────────────────────────────

def _xml_seguro(texto):
    texto = str(texto)
    for bruto, escapado in (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"),
                            ('"', "&quot;")):
        texto = texto.replace(bruto, escapado)
    # O XML 1.0 nao aceita controles; um \x00 vindo de um CSV sujo
    # geraria um arquivo que o Excel recusa abrir sem dizer por que.
    return "".join(c for c in texto
                   if c in "\t\n\r" or 0x20 <= ord(c) <= 0xD7FF
                   or 0xE000 <= ord(c) <= 0xFFFD
                   or 0x10000 <= ord(c) <= 0x10FFFF)


def _serie_do_tempo(valor):
    if isinstance(valor, datetime.datetime):
        return (valor - EPOCA).total_seconds() / 86400.0
    delta = datetime.datetime(valor.year, valor.month, valor.day) - EPOCA
    return float(delta.days)


def _celula_xml(ref, valor, formula, estilo):
    atributos = f'r="{ref}"'
    if estilo:
        atributos += f' s="{estilo}"'

    if formula:
        return f'<c {atributos}><f>{_xml_seguro(formula)}</f></c>'
    if isinstance(valor, bool):
        return f'<c {atributos} t="b"><v>{1 if valor else 0}</v></c>'
    if isinstance(valor, (int, float)):
        return f'<c {atributos}><v>{valor}</v></c>'
    if isinstance(valor, (datetime.date, datetime.datetime)):
        return f'<c {atributos} s="2"><v>{_serie_do_tempo(valor)}</v></c>'
    # Texto inline evita a tabela de strings compartilhadas: o arquivo
    # fica maior, o codigo fica muito menor, e o Excel le igual.
    return (f'<c {atributos} t="inlineStr"><is><t xml:space="preserve">'
            f'{_xml_seguro(valor)}</t></is></c>')


def _aba_xml(aba):
    partes = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
              f'<worksheet xmlns="{_NS["main"]}">']

    if aba.larguras:
        partes.append("<cols>")
        for coluna, largura in sorted(aba.larguras.items()):
            partes.append(f'<col min="{coluna + 1}" max="{coluna + 1}" '
                          f'width="{largura}" customWidth="1"/>')
        partes.append("</cols>")

    partes.append("<sheetData>")
    for linha in range(aba.altura):
        celulas = []
        for coluna in range(aba.largura):
            valor = aba.celulas.get((linha, coluna))
            formula = aba.formulas.get((linha, coluna))
            if valor is None and formula is None:
                continue
            estilo = "1" if linha in aba.negrito else ""
            celulas.append(_celula_xml(endereco(linha, coluna), valor,
                                       formula, estilo))
        if celulas:
            partes.append(f'<row r="{linha + 1}">' + "".join(celulas) + "</row>")
    partes.append("</sheetData>")

    if aba.congelar:
        partes.append(
            f'<sheetViews><sheetView workbookViewId="0"><pane '
            f'ySplit="1" topLeftCell="{aba.congelar}" activePane="bottomLeft" '
            f'state="frozen"/></sheetView></sheetViews>')
    partes.append("</worksheet>")
    return "".join(partes)


_ESTILOS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="{ns}">
<numFmts count="1"><numFmt numFmtId="164" formatCode="yyyy\\-mm\\-dd"/></numFmts>
<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>
<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="2"><fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="3">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''.replace("{ns}", _NS["main"])


def escrever(livro, caminho):
    if not livro.abas:
        livro.nova_aba("Planilha1")

    rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    doc_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    ml = "application/vnd.openxmlformats-officedocument.spreadsheetml"

    tipos = [f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
             f'<Types xmlns="{ct_ns}">',
             '<Default Extension="rels" ContentType="application/'
             'vnd.openxmlformats-package.relationships+xml"/>',
             '<Default Extension="xml" ContentType="application/xml"/>',
             f'<Override PartName="/xl/workbook.xml" '
             f'ContentType="{ml}.sheet.main+xml"/>',
             f'<Override PartName="/xl/styles.xml" '
             f'ContentType="{ml}.styles+xml"/>']
    for i in range(len(livro.abas)):
        tipos.append(f'<Override PartName="/xl/worksheets/sheet{i + 1}.xml" '
                     f'ContentType="{ml}.worksheet+xml"/>')
    tipos.append("</Types>")

    abas_xml = "".join(
        f'<sheet name="{_xml_seguro(a.nome)}" sheetId="{i + 1}" '
        f'r:id="rId{i + 1}"/>' for i, a in enumerate(livro.abas))
    workbook = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<workbook xmlns="{_NS["main"]}" xmlns:r="{doc_ns}">'
                f'<sheets>{abas_xml}</sheets></workbook>')

    rels_abas = "".join(
        f'<Relationship Id="rId{i + 1}" Type="{doc_ns}/worksheet" '
        f'Target="worksheets/sheet{i + 1}.xml"/>'
        for i in range(len(livro.abas)))
    estilo_id = len(livro.abas) + 1

    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(tipos))
        z.writestr("_rels/.rels",
                   f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   f'<Relationships xmlns="{rel_ns}">'
                   f'<Relationship Id="rId1" Type="{doc_ns}/officeDocument" '
                   f'Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels",
                   f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   f'<Relationships xmlns="{rel_ns}">{rels_abas}'
                   f'<Relationship Id="rId{estilo_id}" Type="{doc_ns}/styles" '
                   f'Target="styles.xml"/></Relationships>')
        z.writestr("xl/styles.xml", _ESTILOS)
        for i, aba in enumerate(livro.abas):
            z.writestr(f"xl/worksheets/sheet{i + 1}.xml", _aba_xml(aba))
    return caminho


# ─────────────────────────────────────────────────────────────
#  Leitura
# ─────────────────────────────────────────────────────────────

def _tag(elemento):
    """'{ns}row' → 'row'."""
    return elemento.tag.rsplit("}", 1)[-1]


def _strings_compartilhadas(z):
    """A tabela que o Excel de verdade usa (e nos evitamos ao escrever)."""
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    raiz = ET.fromstring(z.read("xl/sharedStrings.xml"))
    textos = []
    for si in raiz:
        pedacos = [no.text or "" for no in si.iter()
                   if _tag(no) == "t"]
        textos.append("".join(pedacos))
    return textos


def _formatos_de_data(z):
    """Quais estilos sao data — sem isso, toda data vira um numero."""
    if "xl/styles.xml" not in z.namelist():
        return set()
    raiz = ET.fromstring(z.read("xl/styles.xml"))
    embutidos = set(range(14, 23)) | {27, 30, 36, 45, 46, 47, 50, 57}
    personalizados = set()
    for no in raiz.iter():
        if _tag(no) == "numFmt":
            codigo = (no.get("formatCode") or "").lower()
            if any(m in codigo for m in ("yy", "mmm", "dd", "hh")) \
                    and "[" not in codigo:
                personalizados.add(int(no.get("numFmtId")))
    datas = set()
    for xfs in raiz.iter():
        if _tag(xfs) != "cellXfs":
            continue
        for indice, xf in enumerate(xfs):
            fmt = int(xf.get("numFmtId") or 0)
            if fmt in embutidos or fmt in personalizados:
                datas.add(indice)
    return datas


def _valor_da_celula(celula, strings, estilos_data):
    tipo = celula.get("t")
    estilo = celula.get("s")

    if tipo == "inlineStr":
        return "".join(no.text or "" for no in celula.iter()
                       if _tag(no) == "t")

    bruto = None
    for filho in celula:
        if _tag(filho) == "v":
            bruto = filho.text
            break
    if bruto is None:
        return None

    if tipo == "s":
        indice = int(bruto)
        return strings[indice] if indice < len(strings) else ""
    if tipo == "b":
        return bruto == "1"
    if tipo == "str":
        return bruto
    if tipo == "e":
        return bruto                     # #DIV/0!, #N/A — devolve o texto

    try:
        numero = float(bruto)
    except ValueError:
        return bruto

    if estilo is not None and int(estilo) in estilos_data:
        return EPOCA + datetime.timedelta(days=numero)
    return int(numero) if numero.is_integer() else numero


def ler(caminho):
    if not os.path.isfile(caminho):
        raise FileNotFoundError(f"planilha não encontrada: {caminho}")

    livro = Livro()
    with zipfile.ZipFile(caminho) as z:
        strings = _strings_compartilhadas(z)
        estilos_data = _formatos_de_data(z)

        # O nome da aba esta no workbook.xml; o conteudo, num sheetN.xml
        # cuja ligacao passa pelo arquivo de relacionamentos.
        raiz = ET.fromstring(z.read("xl/workbook.xml"))
        nomes = []
        for no in raiz.iter():
            if _tag(no) == "sheet":
                rid = next((v for k, v in no.attrib.items()
                            if k.endswith("}id")), None)
                nomes.append((no.get("name"), rid))

        alvos = {}
        if "xl/_rels/workbook.xml.rels" in z.namelist():
            rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            for rel in rels:
                alvos[rel.get("Id")] = rel.get("Target")

        for posicao, (nome, rid) in enumerate(nomes, start=1):
            alvo = alvos.get(rid) or f"worksheets/sheet{posicao}.xml"
            caminho_interno = ("xl/" + alvo.lstrip("/")).replace("xl/xl/", "xl/")
            if caminho_interno not in z.namelist():
                continue

            aba = livro.nova_aba(nome)
            folha = ET.fromstring(z.read(caminho_interno))
            for elemento in folha.iter():
                if _tag(elemento) != "c":
                    continue
                ref = elemento.get("r")
                if not ref:
                    continue
                linha, coluna = ler_endereco(ref)
                for filho in elemento:
                    if _tag(filho) == "f" and filho.text:
                        aba.formulas[(linha, coluna)] = filho.text
                valor = _valor_da_celula(elemento, strings, estilos_data)
                if valor is not None:
                    aba.por(linha, coluna, valor)
    return livro


# ─────────────────────────────────────────────────────────────
#  Modulo Arcane.Excel
# ─────────────────────────────────────────────────────────────

def _linhas_de(dados):
    """Aceita lista de listas ou lista de vaults (com cabecalho deduzido)."""
    if not dados:
        return [], None
    primeiro = dados[0]
    if isinstance(primeiro, dict):
        colunas = list(primeiro.keys())
        for item in dados[1:]:
            for chave in item:
                if chave not in colunas:
                    colunas.append(chave)
        return [[item.get(c) for c in colunas] for item in dados], colunas
    if hasattr(primeiro, "campos"):
        colunas = list(primeiro.campos.keys())
        return [[i.campos.get(c) for c in colunas] for i in dados], colunas
    return [list(linha) for linha in dados], None


class ArcaneExcel:
    """Planilhas .xlsx — ler, escrever e converter."""

    # ── livro ──

    @staticmethod
    def _new():
        return Livro()

    @staticmethod
    def _read(caminho):
        return ler(caminho)

    @staticmethod
    def _save(livro, caminho):
        return escrever(livro, caminho)

    @staticmethod
    def _sheets(livro):
        return [a.nome for a in livro.abas]

    @staticmethod
    def _sheet(livro, nome, dados=None, cabecalho=None):
        """Cria (ou pega) uma aba e, se vierem dados, preenche.

        'dados' pode ser lista de listas ou lista de vaults — no segundo
        caso o cabecalho sai das chaves.
        """
        aba = livro.nova_aba(nome)
        if dados is None:
            return aba

        linhas, colunas = _linhas_de(dados)
        topo = cabecalho if cabecalho is not None else colunas
        deslocamento = 0
        if topo:
            for coluna, titulo in enumerate(topo):
                aba.por(0, coluna, titulo)
            aba.negrito.add(0)
            aba.congelar = "A2"
            deslocamento = 1
        for l, linha in enumerate(linhas):
            for c, valor in enumerate(linha):
                aba.por(l + deslocamento, c, valor)
        ArcaneExcel._autofit(aba)
        return aba

    @staticmethod
    def _drop_sheet(livro, nome):
        livro.abas = [a for a in livro.abas if a.nome != nome]
        return livro

    # ── celulas ──

    @staticmethod
    def _get(aba, ref):
        linha, coluna = ler_endereco(ref) if isinstance(ref, str) else ref
        return aba.pega(linha, coluna)

    @staticmethod
    def _set(aba, ref, valor):
        linha, coluna = ler_endereco(ref) if isinstance(ref, str) else ref
        aba.por(linha, coluna, valor)
        return aba

    @staticmethod
    def _cell(aba, linha, coluna, valor=None):
        if valor is None:
            return aba.pega(int(linha), int(coluna))
        aba.por(int(linha), int(coluna), valor)
        return aba

    @staticmethod
    def _formula(aba, ref, expressao):
        """Grava uma formula. O Excel calcula ao abrir; nos so guardamos."""
        linha, coluna = ler_endereco(ref) if isinstance(ref, str) else ref
        aba.formulas[(linha, coluna)] = str(expressao).lstrip("=")
        return aba

    @staticmethod
    def _get_formula(aba, ref):
        """A formula gravada numa celula, ou void.

        As formulas ficam num dict com chave (linha, coluna) — uma tupla,
        que o DataForge nao consegue indexar. Sem esta funcao, o unico
        jeito de ler uma formula de volta seria abrir o arquivo no Excel.
        """
        linha, coluna = ler_endereco(ref) if isinstance(ref, str) else ref
        return aba.formulas.get((linha, coluna))

    @staticmethod
    def _formulas(aba):
        """Todas as formulas da aba, por endereco: {"D5": "SUM(D2:D4)"}."""
        return {endereco(l, c): texto
                for (l, c), texto in sorted(aba.formulas.items())}

    @staticmethod
    def _append(aba, linha_valores):
        destino = aba.altura
        for coluna, valor in enumerate(list(linha_valores)):
            aba.por(destino, coluna, valor)
        return aba

    # ── leitura em bloco ──

    @staticmethod
    def _rows(livro, nome=None):
        aba = livro.abas[0] if nome is None else livro.aba(nome)
        if aba is None:
            raise ValueError(f"aba não encontrada: {nome}")
        return aba.linhas()

    @staticmethod
    def _records(livro, nome=None):
        """Cada linha vira um vault, usando a primeira linha de cabecalho."""
        linhas = ArcaneExcel._rows(livro, nome)
        if not linhas:
            return []
        cabecalho = [str(c) if c is not None else f"col{i}"
                     for i, c in enumerate(linhas[0])]
        saida = []
        for linha in linhas[1:]:
            item = {}
            for i, chave in enumerate(cabecalho):
                item[chave] = linha[i] if i < len(linha) else None
            saida.append(item)
        return saida

    @staticmethod
    def _column(livro, nome_aba, coluna):
        """Uma coluna inteira, pelo titulo ou pela letra."""
        aba = livro.aba(nome_aba) if nome_aba else livro.abas[0]
        linhas = aba.linhas()
        if not linhas:
            return []
        if isinstance(coluna, str):
            # O titulo vence a letra: numa planilha com a coluna 'A' de
            # nome, pedir "A" deve trazer essa coluna, nao a primeira.
            cabecalho = [str(c) for c in linhas[0]]
            if coluna in cabecalho:
                indice = cabecalho.index(coluna)
                return [l[indice] if indice < len(l) else None
                        for l in linhas[1:]]
            if re.fullmatch(r"[A-Za-z]+", coluna):
                indice = letra_para_coluna(coluna)
                return [l[indice] if indice < len(l) else None for l in linhas]
            raise ValueError(f"coluna não encontrada: {coluna}")
        indice = int(coluna)
        return [l[indice] if indice < len(l) else None for l in linhas]

    @staticmethod
    def _dims(livro, nome=None):
        aba = livro.abas[0] if nome is None else livro.aba(nome)
        return {"linhas": aba.altura, "colunas": aba.largura,
                "celulas": len(aba.celulas)}

    # ── formatacao ──

    @staticmethod
    def _width(aba, coluna, largura):
        indice = letra_para_coluna(coluna) if isinstance(coluna, str) \
            else int(coluna)
        aba.larguras[indice] = float(largura)
        return aba

    @staticmethod
    def _bold_row(aba, linha):
        aba.negrito.add(int(linha))
        return aba

    @staticmethod
    def _freeze(aba, ref="A2"):
        aba.congelar = ref
        return aba

    @staticmethod
    def _autofit(aba):
        """Largura pelo conteudo. Nao e exato — o Excel mede em pixels de
        fonte — mas evita a coluna de '####' que todo mundo odeia."""
        for coluna in range(aba.largura):
            maior = 0
            for linha in range(aba.altura):
                valor = aba.pega(linha, coluna)
                if valor is not None:
                    maior = max(maior, len(str(valor)))
            if maior:
                aba.larguras[coluna] = min(max(maior + 2, 8), 60)
        return aba

    # ── conversao ──

    @staticmethod
    def _from_csv(caminho, separador=",", nome="Planilha1"):
        import csv
        livro = Livro()
        with open(caminho, newline="", encoding="utf-8-sig") as f:
            linhas = list(csv.reader(f, delimiter=separador))
        convertidas = []
        for linha in linhas:
            atual = []
            for campo in linha:
                # Numero que veio como texto vira numero: senao a planilha
                # abre com tudo alinhado a esquerda e nada soma.
                try:
                    atual.append(int(campo))
                except ValueError:
                    try:
                        atual.append(float(campo))
                    except ValueError:
                        atual.append(campo)
            convertidas.append(atual)
        ArcaneExcel._sheet(livro, nome, convertidas[1:],
                           cabecalho=convertidas[0] if convertidas else None)
        return livro

    @staticmethod
    def _to_csv(livro, caminho, nome=None, separador=","):
        import csv
        linhas = ArcaneExcel._rows(livro, nome)
        with open(caminho, "w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f, delimiter=separador)
            for linha in linhas:
                escritor.writerow(["" if v is None else v for v in linha])
        return caminho

    @staticmethod
    def _to_frame(livro, nome=None):
        """Vira um frame do Arcane.Analytics, para analisar de verdade."""
        from .arcane_analytics import ArcaneAnalytics
        registros = ArcaneExcel._records(livro, nome)
        return ArcaneAnalytics._from_records(registros)

    @staticmethod
    def _from_frame(frame, nome="Dados", livro=None):
        livro = livro if livro is not None else Livro()
        dados = frame.get("rows", frame) if isinstance(frame, dict) else frame
        ArcaneExcel._sheet(livro, nome, dados)
        return livro

    @staticmethod
    def _quick(caminho, dados, nome="Planilha1", cabecalho=None):
        """O caminho curto: dados → arquivo, numa chamada."""
        livro = Livro()
        ArcaneExcel._sheet(livro, nome, dados, cabecalho)
        return escrever(livro, caminho)

    # ── enderecos ──

    @staticmethod
    def _addr(linha, coluna):
        return endereco(int(linha), int(coluna))

    @staticmethod
    def _parse_addr(ref):
        linha, coluna = ler_endereco(ref)
        return {"linha": linha, "coluna": coluna}

    @staticmethod
    def _col_letter(indice):
        return coluna_para_letra(int(indice))

    def __new__(cls):
        return {
            "__name__": "Arcane.Excel",

            # livro
            "new": cls._new,
            "read": cls._read,
            "save": cls._save,
            "sheets": cls._sheets,
            "sheet": cls._sheet,
            "drop_sheet": cls._drop_sheet,

            # celulas
            "get": cls._get,
            "set": cls._set,
            "cell": cls._cell,
            "formula": cls._formula,
            "get_formula": cls._get_formula,
            "formulas": cls._formulas,
            "append": cls._append,

            # leitura
            "rows": cls._rows,
            "records": cls._records,
            "column": cls._column,
            "dims": cls._dims,

            # formatacao
            "width": cls._width,
            "bold_row": cls._bold_row,
            "freeze": cls._freeze,
            "autofit": cls._autofit,

            # conversao
            "from_csv": cls._from_csv,
            "to_csv": cls._to_csv,
            "to_frame": cls._to_frame,
            "from_frame": cls._from_frame,
            "quick": cls._quick,

            # enderecos
            "addr": cls._addr,
            "parse_addr": cls._parse_addr,
            "col_letter": cls._col_letter,
        }
