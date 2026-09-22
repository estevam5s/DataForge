# -*- coding: utf-8 -*-
"""Arcane.Estrutura — layout binario com nome, e o ponteiro que o percorre.

O que ja existia, e o que faltava
---------------------------------
`Arcane.Bytes` empacota e desempacota por FORMATO: `'>i32 u16'`. Ele
resolve a conversao, e cobra a ordem dos bytes — o que ja evita o pior
defeito da area. O que ele nao tem e **nome**: o resultado e uma lista
posicional, e quem le `dados[3]` tres meses depois nao sabe o que e.

`Arcane.C` tem `estrutura` e `ponteiro`, mas eles sao da **FFI**: exigem
uma biblioteca nativa carregada, e existem para falar com o C. Ler o
cabecalho de um PNG nao deveria exigir `ctypes`.

Este modulo e o meio: uma estrutura com campos nomeados, alinhamento
declarado, uma janela que le sem copiar, e um ponteiro que anda por
ela — tudo em cima de `bytearray`, sem FFI e sem dependencia.

    Cabecalho := Est.definir("Cabecalho", [
        ["magia", "u32"],
        ["versao", "u16"],
        ["itens", "u16"],
    ], ordem := "rede")

    c := Cabecalho.ler(dados)
    out c["versao"]

Cinco decisoes que valem lembrar
--------------------------------
1. **A ordem dos bytes e obrigatoria.** Sem ela, o mesmo arquivo lido
   em duas maquinas da dois valores — e nenhuma das duas falha. E a
   mesma cobranca do `Arcane.Bytes`, e pelo mesmo motivo.

2. **O alinhamento e declarado, e conferido.** `empacotado := no` (o
   padrao) insere enchimento como o C faz; `yes` recusa o enchimento e
   cobra os deslocamentos. Adivinhar aqui e como o mesmo `.struct` sai
   com 12 bytes de um lado e 16 do outro.

3. **A janela nao copia.** `Est.janela(bloco, molde, deslocamento)` le
   e escreve **no bloco original**. Copiar um registro de 4 KB para ler
   um campo de 2 bytes e o que faz um parser de arquivo grande levar
   minutos.

4. **O ponteiro sabe se o bloco morreu.** Ele guarda uma referencia
   fraca: soltar o bloco e usar o ponteiro depois levanta em vez de ler
   o que ocupou o espaco. Num mundo com coletor a memoria nunca esteve
   em risco — o que se protege e o PROTOCOLO, como em `Arcane.Posse`.

5. **Ler fora do bloco e erro, e nao lixo.** Um registro de 16 bytes
   lido a partir do byte 10 de um bloco de 20 leria 6 bytes que nao sao
   dele. Sem a conferencia, o resultado e um numero plausivel — e o
   defeito aparece tres camadas adiante.
"""

import difflib
import mmap
import os
import struct
import threading
import zlib

_DOC = "estruturas"

#: nome -> (letra do struct, tamanho, alinhamento natural)
TIPOS = {
    "i8": ("b", 1), "u8": ("B", 1),
    "i16": ("h", 2), "u16": ("H", 2),
    "i32": ("i", 4), "u32": ("I", 4),
    "i64": ("q", 8), "u64": ("Q", 8),
    "f32": ("f", 4), "f64": ("d", 8),
    "bool": ("?", 1),
}

#: Os tipos cujo `quantos` e o TAMANHO, e nao uma repeticao: `["nome",
#: "char", 16]` e um texto de ate 16 bytes (o `char nome[16]` do C), e
#: `["magica", "bytes", 8]` sao oito bytes crus. Ficam fora de TIPOS de
#: proposito: um ponteiro para "char" nao teria o que ler.
TEXTUAIS = ("char", "bytes")


def _largura(tipo):
    return 1 if tipo in TEXTUAIS else TIPOS[tipo][1]


#: Como a ordem dos bytes e escrita. 'rede' e big-endian, que e o que
#: todo formato de arquivo e todo protocolo usam.
ORDENS = {"rede": ">", "big": ">", ">": ">",
          "intel": "<", "little": "<", "<": "<"}


def _faixa(tipo):
    """O que cabe num tipo, em palavras de quem declarou o campo.

    A mensagem do `struct` diz `'B' format requires 0 <= number <= 255`:
    a letra e do formato interno do Python, e quem escreveu `u8` nao
    tem como ligar uma coisa a outra. A faixa sai do PROPRIO tipo.
    """
    if tipo == "bool":
        return "aceita apenas yes ou no"
    if tipo.startswith("f"):
        return "espera um numero com ponto"
    bits = int(tipo[1:])
    if tipo[0] == "u":
        return f"vai de 0 a {2 ** bits - 1}"
    return f"vai de {-(2 ** (bits - 1))} a {2 ** (bits - 1) - 1}"


def _erro(mensagem, nota="", dica="", classe="LayoutError"):
    from .. import errors
    alvo = errors.erro_por_nome(classe) or errors.RuntimeError_
    return alvo(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


def _parecido(nome, candidatos):
    """'você quis dizer X?' — a mesma resposta que o `check` dá.

    Sem ela, `j.ler("verso")` responde apenas que o campo não existe, e
    quem lê vai conferir o arquivo binário antes de notar o `a` que
    falta. O nome certo está a um caractere de distância, e o
    analisador da linguagem já usa `difflib` justamente aqui.
    """
    achados = difflib.get_close_matches(str(nome), list(candidatos), 1, 0.6)
    return f" Você quis dizer '{achados[0]}'?" if achados else ""


def _bytes_de(alvo):
    """O bytearray por tras de um bloco, janela ou valor cru."""
    if isinstance(alvo, Bloco):
        return alvo.dados()
    if isinstance(alvo, Janela):
        return alvo._bloco.dados()
    if isinstance(alvo, (bytes, bytearray, memoryview)):
        return alvo
    raise _erro(
        "isto nao e um bloco de bytes.",
        nota="aceita um Bloco, uma Janela, bytes ou bytearray",
        dica="Est.bloco(n) cria um; IO.read_bytes(caminho) le um")


# ═══════════════════════════════════════════════════════════
#  O molde
# ═══════════════════════════════════════════════════════════

class Molde:
    """A descricao de um registro: campos, tamanho e deslocamentos.

    Ele nao guarda dado nenhum — e o mapa. Ler devolve um vault; uma
    janela le e escreve no bloco original.
    """

    __slots__ = ("nome", "campos", "ordem", "empacotado", "tamanho",
                 "_desloc", "_formato")

    def __init__(self, nome, campos, ordem="rede", empacotado=False):
        self.nome = str(nome)
        self.ordem = ORDENS.get(str(ordem), None)
        if self.ordem is None:
            raise _erro(
                f"'{ordem}' nao e uma ordem de bytes.",
                nota="sem a ordem, o mesmo arquivo lido em duas maquinas "
                     "da dois valores, e nenhuma das duas falha",
                dica='use "rede" (big-endian, o de todo formato de '
                     'arquivo) ou "intel" (little-endian)')
        self.empacotado = bool(empacotado)

        lista = []
        for campo in (campos or []):
            if isinstance(campo, dict):
                nome_campo = campo.get("nome")
                tipo = campo.get("tipo")
                quantos = int(campo.get("quantos", 1) or 1)
            else:
                partes = list(campo)
                nome_campo = partes[0]
                tipo = partes[1]
                quantos = int(partes[2]) if len(partes) > 2 else 1
            lista.append((str(nome_campo), str(tipo), quantos))

        if not lista:
            raise _erro(f"'{self.nome}' precisa de ao menos um campo.",
                        dica='Est.definir("P", [["x", "i32"], ["y", "i32"]])')

        repetidos = [n for n, _, _ in lista
                     if [m for m, _, _ in lista].count(n) > 1]
        if repetidos:
            raise _erro(
                f"'{self.nome}' declara '{sorted(set(repetidos))[0]}' "
                f"duas vezes.",
                nota="o segundo campo seria inalcancavel: a leitura "
                     "devolve um vault, e a chave repetida some")

        conhecidos = list(TIPOS) + list(TEXTUAIS)
        desconhecidos = [t for _, t, _ in lista if t not in conhecidos]
        if desconhecidos:
            alvo = desconhecidos[0]
            raise _erro(
                f"tipo desconhecido: '{alvo}'."
                f"{_parecido(alvo, conhecidos)}",
                nota=f"os tipos sao: {', '.join(sorted(conhecidos))}")

        self.campos = lista
        self._desloc = {}
        self._formato = {}
        posicao = 0
        maior = 1
        for nome_campo, tipo, quantos in lista:
            if tipo in TEXTUAIS:
                # Um texto de N bytes nao tem alinhamento: e um cluster
                # de bytes, e o C o poe em qualquer posicao.
                self._desloc[nome_campo] = posicao
                self._formato[nome_campo] = (f"{quantos}s", quantos, 1)
                posicao += quantos
                continue
            letra, largura = TIPOS[tipo]
            maior = max(maior, largura)
            if not self.empacotado and posicao % largura:
                # O enchimento que o C insere: um u32 comeca num
                # multiplo de 4. Ignorar isto e o que faz o mesmo
                # registro ter 12 bytes de um lado e 16 do outro.
                posicao += largura - (posicao % largura)
            self._desloc[nome_campo] = posicao
            self._formato[nome_campo] = (self.ordem + letra * quantos,
                                         largura * quantos, quantos)
            posicao += largura * quantos

        if not self.empacotado and posicao % maior:
            # O registro inteiro tambem e alinhado ao maior campo: e o
            # que faz um cluster deles ficar certo.
            posicao += maior - (posicao % maior)
        self.tamanho = posicao

    # ── ler e escrever ───────────────────────────────────────

    def deslocamento(self, campo):
        """Onde o campo comeca, em bytes."""
        if str(campo) not in self._desloc:
            raise _erro(f"'{self.nome}' nao tem o campo '{campo}'."
                        f"{_parecido(campo, self._desloc)}",
                        nota=f"tem: {', '.join(self._desloc)}")
        return self._desloc[str(campo)]

    def ler(self, fonte, deslocamento=0):
        """Os campos como vault. Uma copia — nao acompanha o bloco."""
        crus = _bytes_de(fonte)
        base = int(deslocamento)
        self._conferir(len(crus), base, "ler")
        saida = {}
        for nome_campo, _tipo, _quantos in self.campos:
            saida[nome_campo] = self._ler_campo(crus, base, nome_campo)
        return saida

    def escrever(self, alvo, valores, deslocamento=0):
        """Grava os campos no bloco. Devolve o proprio alvo."""
        crus = _bytes_de(alvo)
        if isinstance(crus, bytes):
            raise _erro(
                "este bloco e somente leitura.",
                nota="'bytes' nao muda; 'bytearray' e um Bloco mudam",
                dica="Est.bloco(n), ou bytearray(dados)")
        base = int(deslocamento)
        self._conferir(len(crus), base, "escrever")
        desconhecidos = set(valores or {}) - set(self._desloc)
        if desconhecidos:
            raise _erro(
                f"'{self.nome}' nao tem {sorted(desconhecidos)}."
                f"{_parecido(sorted(desconhecidos)[0], self._desloc)}",
                nota=f"os campos sao: {', '.join(self._desloc)}",
                dica="um campo a mais aqui seria um erro de digitacao "
                     "gravando em lugar nenhum")
        if isinstance(crus, mmap.mmap) and _so_leitura(crus):
            raise _erro(
                "este arquivo foi mapeado so para leitura.",
                dica="Est.mapear(caminho, escrita := yes)")
        for nome_campo, valor in (valores or {}).items():
            self._escrever_campo(crus, base, nome_campo, valor)
        return alvo

    def empacotar(self, valores):
        """Um bloco novo com estes campos. O que faltar vai zerado."""
        bloco = Bloco(self.tamanho)
        self.escrever(bloco, valores)
        return bloco

    def _conferir(self, disponivel, base, o_que):
        if base < 0:
            raise _erro(f"deslocamento negativo: {base}.",
                        classe="BufferOverflowError")
        if disponivel - base < self.tamanho:
            raise _erro(
                f"nao da para {o_que} '{self.nome}' aqui: ele precisa de "
                f"{self.tamanho} byte(s), e ha {max(0, disponivel - base)} "
                f"a partir do byte {base}.",
                nota="ler alem do fim devolveria bytes que nao sao deste "
                     "registro — um numero plausivel, e o defeito "
                     "aparecendo tres camadas adiante",
                classe="BufferOverflowError")

    def _tipo(self, campo):
        for nome_campo, tipo, _q in self.campos:
            if nome_campo == campo:
                return tipo
        return None

    def _ler_campo(self, crus, base, campo):
        formato, largura, quantos = self._formato[campo]
        inicio = base + self._desloc[campo]
        valores = struct.unpack_from(formato, crus, inicio)
        tipo = self._tipo(campo)
        if tipo == "char":
            # Ate o primeiro zero, como o C le um char[N].
            return valores[0].split(b"\x00", 1)[0].decode("utf-8", "replace")
        if tipo == "bytes":
            return bytes(valores[0])
        return list(valores) if quantos > 1 else valores[0]

    def _escrever_campo(self, crus, base, campo, valor):
        formato, largura, quantos = self._formato[campo]
        inicio = base + self._desloc[campo]
        tipo = self._tipo(campo)
        if tipo in TEXTUAIS:
            if tipo == "char":
                bruto = str(valor).encode("utf-8")
                unidade = "byte(s) em UTF-8"
            else:
                bruto = bytes(valor)
                unidade = "byte(s)"
            if len(bruto) > largura:
                raise _erro(
                    f"'{campo}' guarda ate {largura} byte(s), e o valor tem "
                    f"{len(bruto)} {unidade}.",
                    nota="cortar em silencio gravaria outro texto — e, no "
                         "meio de um caractere acentuado, um texto invalido",
                    dica=f"aumente o campo, ou corte antes de gravar",
                    classe="BufferOverflowError")
            # O 's' do struct completa com zeros: o terminador do C.
            struct.pack_into(formato, crus, inicio, bruto)
            return
        if quantos > 1:
            itens = list(valor)
            if len(itens) != quantos:
                raise _erro(
                    f"'{campo}' tem {quantos} posicao(oes), e vieram "
                    f"{len(itens)}.")
            struct.pack_into(formato, crus, inicio, *itens)
            return
        try:
            struct.pack_into(formato, crus, inicio, valor)
        except struct.error:
            tipo = dict((n, t) for n, t, _ in self.campos)[campo]
            raise _erro(
                f"{valor!r} nao cabe em '{campo}': um {tipo} "
                f"{_faixa(tipo)}.",
                nota="o tipo declara a faixa; sem esta conferencia o valor "
                     "seria truncado em silencio, e o arquivo sairia com "
                     "outro numero",
                classe="BufferOverflowError")

    # ── o que o molde sabe dizer ─────────────────────────────

    def mapa(self):
        """Campo, tipo, deslocamento e tamanho — a tabela do layout."""
        saida = []
        for nome_campo, tipo, quantos in self.campos:
            _f, largura, _q = self._formato[nome_campo]
            if tipo in TEXTUAIS:
                quantos = largura
            saida.append({"campo": nome_campo, "tipo": tipo,
                          "quantos": quantos,
                          "deslocamento": self._desloc[nome_campo],
                          "bytes": largura})
        return saida

    def enchimento(self):
        """Quantos bytes sao SO alinhamento. Zero se empacotado."""
        util = sum(l for _f, l, _q in self._formato.values())
        return self.tamanho - util

    def __call__(self, valores=None, **nomeados):
        """`Molde({"x": 1})` ou `Molde(x := 1)` — um bloco novo.

        O vault e a forma natural na linguagem, e o molde so aceitava os
        argumentos nomeados: `P({"x": 1})` dava um erro de aridade que
        nem dizia o nome da funcao.
        """
        juntos = dict(valores or {})
        juntos.update(nomeados)
        return self.empacotar(juntos)

    def __len__(self):
        return self.tamanho

    def __repr__(self):
        modo = "empacotado" if self.empacotado else "alinhado"
        return (f"<molde {self.nome}, {len(self.campos)} campo(s), "
                f"{self.tamanho} bytes, {modo}>")


def definir(nome, campos, ordem="rede", empacotado=False):
    return Molde(nome, campos, ordem, empacotado)


# ═══════════════════════════════════════════════════════════
#  O bloco
# ═══════════════════════════════════════════════════════════

class Bloco:
    """Bytes mutaveis, com um dono que pode declarar o fim.

    `liberar()` nao devolve memoria ao sistema — quem faz isso e o
    CPython. O que ele faz e **marcar**: a partir dali, todo ponteiro e
    toda janela sobre este bloco levantam em vez de ler. E a mesma
    escolha de `Arcane.Posse`: num mundo com coletor, o que se protege
    e o protocolo.
    """

    __slots__ = ("_dados", "_vivo", "_trava")

    def __init__(self, tamanho_ou_dados=0):
        if isinstance(tamanho_ou_dados, int):
            if tamanho_ou_dados < 0:
                raise _erro(f"tamanho negativo: {tamanho_ou_dados}.",
                            classe="NegativeSizeError")
            self._dados = bytearray(tamanho_ou_dados)
        else:
            self._dados = bytearray(_bytes_de(tamanho_ou_dados))
        self._vivo = True
        self._trava = threading.RLock()

    def dados(self):
        if not self._vivo:
            raise _erro(
                "este bloco ja foi liberado.",
                nota="o endereco continua na mao de alguem, e o que "
                     "ocupou o espaco depois nao e o dado que se espera",
                dica="use Arcane.Posse quando o dono precisa ser um so",
                classe="DanglingPointerError")
        return self._dados

    def vivo(self):
        return self._vivo

    def liberar(self):
        """Marca o fim. Idempotente, como o `soltar` da posse."""
        with self._trava:
            if not self._vivo:
                return False
            self._vivo = False
            if isinstance(self._dados, mmap.mmap):
                self._dados.close()
            self._dados = bytearray()
        return True

    def bytes(self):
        return bytes(self.dados())

    def sincronizar(self):
        """Num bloco mapeado, garante que o escrito chegou ao arquivo."""
        dados = self.dados()
        if isinstance(dados, mmap.mmap):
            dados.flush()
        return self

    def mapeado(self):
        return self._vivo and isinstance(self._dados, mmap.mmap)

    def fatiar(self, inicio, fim=None):
        crus = self.dados()
        return Bloco(crus[inicio:len(crus) if fim is None else fim])

    def preencher(self, valor=0):
        crus = self.dados()
        for i in range(len(crus)):
            crus[i] = int(valor) & 0xFF
        return self

    def __len__(self):
        return len(self._dados) if self._vivo else 0

    def __getitem__(self, chave):
        return self.dados()[chave]

    def __setitem__(self, chave, valor):
        self.dados()[chave] = valor

    def __repr__(self):
        if not self._vivo:
            return "<bloco liberado>"
        amostra = bytes(self._dados[:8]).hex()
        reticencia = "…" if len(self._dados) > 8 else ""
        return f"<bloco {len(self._dados)} bytes: {amostra}{reticencia}>"


def bloco(tamanho_ou_dados=0):
    return Bloco(tamanho_ou_dados)


def de_bytes(dados):
    return Bloco(dados)


# ═══════════════════════════════════════════════════════════
#  A janela
# ═══════════════════════════════════════════════════════════

class Janela:
    """Um registro visto NO LUGAR: ler e escrever mexem no bloco.

    Copiar um registro de 4 KB para ler um campo de 2 bytes e o que faz
    um parser de arquivo grande levar minutos. A janela nao copia.
    """

    __slots__ = ("_bloco", "_molde", "_desloc")

    def __init__(self, bloco_alvo, molde, deslocamento=0):
        if not isinstance(bloco_alvo, Bloco):
            bloco_alvo = Bloco(bloco_alvo)
        self._bloco = bloco_alvo
        self._molde = molde
        self._desloc = int(deslocamento)
        molde._conferir(len(bloco_alvo.dados()), self._desloc, "abrir")

    def molde(self):
        return self._molde

    def deslocamento(self):
        return self._desloc

    def ler(self, campo):
        return self._molde._ler_campo(self._bloco.dados(), self._desloc,
                                      self._conferir(campo))

    def escrever(self, campo, valor):
        self._molde._escrever_campo(self._bloco.dados(), self._desloc,
                                    self._conferir(campo), valor)
        return self

    def vault(self):
        """Uma copia dos campos. A partir daqui, nao acompanha mais."""
        return self._molde.ler(self._bloco, self._desloc)

    def proxima(self):
        """A janela do registro seguinte — como percorrer um cluster."""
        return Janela(self._bloco, self._molde,
                      self._desloc + self._molde.tamanho)

    def _conferir(self, campo):
        nome = str(campo)
        if nome not in self._molde._desloc:
            raise _erro(
                f"'{self._molde.nome}' nao tem o campo '{nome}'."
                f"{_parecido(nome, self._molde._desloc)}",
                nota=f"tem: {', '.join(self._molde._desloc)}")
        return nome

    def __getitem__(self, campo):
        return self.ler(campo)

    def __setitem__(self, campo, valor):
        self.escrever(campo, valor)

    def __len__(self):
        return self._molde.tamanho

    def __repr__(self):
        return (f"<janela {self._molde.nome} em +{self._desloc}>")


def janela(alvo, molde, deslocamento=0):
    return Janela(alvo, molde, deslocamento)


def janelas(alvo, molde, quantos=None, deslocamento=0):
    """Um cluster de janelas — a leitura de um arquivo de registros."""
    destino = alvo if isinstance(alvo, Bloco) else Bloco(alvo)
    disponivel = len(destino.dados()) - int(deslocamento)
    cabem = disponivel // molde.tamanho if molde.tamanho else 0
    if quantos is None:
        quantos = cabem
    quantos = int(quantos)
    if quantos > cabem:
        raise _erro(
            f"cabem {cabem} registro(s) de '{molde.nome}' aqui, e foram "
            f"pedidos {quantos}.",
            nota=f"cada um ocupa {molde.tamanho} byte(s), e ha "
                 f"{max(0, disponivel)} a partir do byte {deslocamento}",
            classe="BufferOverflowError")
    return [Janela(destino, molde, int(deslocamento) + i * molde.tamanho)
            for i in range(quantos)]


# ═══════════════════════════════════════════════════════════
#  O ponteiro
# ═══════════════════════════════════════════════════════════

class Ponteiro:
    """Um deslocamento num bloco, com aritmetica e com dono fraco.

        p := Est.ponteiro(b, "u32")
        out p.ler()
        p2 := p.mais(1)        // anda UM u32, e nao um byte

    Andar por TIPO e nao por byte e o que separa um ponteiro de um
    indice: `p + 1` num `u32*` do C anda quatro bytes, e quem escreve
    aritmetica de ponteiro conta elementos.

    O ponteiro **segura** o bloco, e isso e uma decisao, nao um
    descuido. A primeira versao guardava uma referencia fraca, para
    imitar o C: `Est.ponteiro(Est.bloco(8), "u32")` nascia pendurado,
    porque o bloco temporario morria assim que a chamada voltava. Um
    ponteiro cuja validade depende de a expressao ter sido guardada
    numa variavel e uma armadilha, e ela aparece e some conforme a
    contagem de referencias.

    Num mundo com coletor a memoria nunca esteve em risco. O que se
    protege e o **protocolo**, e ele tem um so ponto: `liberar()`.
    Depois dele, ler daqui levanta — e e a mesma escolha do
    `Arcane.Posse`.
    """

    __slots__ = ("_bloco", "_tipo", "_desloc", "_ordem")

    def __init__(self, bloco_alvo, tipo="u8", deslocamento=0, ordem="rede"):
        if not isinstance(bloco_alvo, Bloco):
            bloco_alvo = Bloco(bloco_alvo)
        if str(tipo) not in TIPOS:
            raise _erro(f"tipo desconhecido: '{tipo}'."
                        f"{_parecido(tipo, TIPOS)}",
                        nota=f"os tipos sao: {', '.join(sorted(TIPOS))}")
        self._bloco = bloco_alvo
        self._tipo = str(tipo)
        self._desloc = int(deslocamento)
        self._ordem = ORDENS.get(str(ordem), ">")

    # ── o bloco, se ainda houver ─────────────────────────────

    def _alvo(self):
        destino = self._bloco
        if not destino.vivo():
            raise _erro(
                "o bloco deste ponteiro foi liberado.",
                dica="use Arcane.Posse quando o dono precisa ser um so",
                classe="DanglingPointerError")
        return destino

    def e_nulo(self):
        return not self._bloco.vivo()

    def endereco(self):
        """O deslocamento em BYTES — o que um `%p` mostraria."""
        return self._desloc

    def tipo(self):
        return self._tipo

    def passo(self):
        return TIPOS[self._tipo][1]

    # ── ler e escrever ───────────────────────────────────────

    def ler(self):
        crus = self._alvo().dados()
        letra, largura = TIPOS[self._tipo]
        self._conferir(len(crus), largura)
        return struct.unpack_from(self._ordem + letra, crus, self._desloc)[0]

    def escrever(self, valor):
        crus = self._alvo().dados()
        letra, largura = TIPOS[self._tipo]
        self._conferir(len(crus), largura)
        try:
            struct.pack_into(self._ordem + letra, crus, self._desloc, valor)
        except struct.error:
            raise _erro(f"{valor!r} nao cabe num {self._tipo}: ele "
                        f"{_faixa(self._tipo)}.",
                        classe="BufferOverflowError")
        return self

    def _conferir(self, disponivel, largura):
        if self._desloc < 0 or disponivel - self._desloc < largura:
            raise _erro(
                f"o ponteiro aponta para o byte {self._desloc}, e o bloco "
                f"tem {disponivel}.",
                nota=f"um {self._tipo} ocupa {largura} byte(s)",
                classe="BufferOverflowError")

    # ── aritmetica ───────────────────────────────────────────

    def mais(self, quantos=1):
        """Anda `quantos` ELEMENTOS — nao bytes."""
        return self._outro(self._desloc + int(quantos) * self.passo())

    def menos(self, quantos=1):
        return self.mais(-int(quantos))

    def como(self, tipo):
        """O mesmo endereco, lido como outro tipo — o cast do C."""
        return Ponteiro(self._alvo(), tipo, self._desloc,
                        ">" if self._ordem == ">" else "<")

    def distancia(self, outro):
        """Quantos elementos separam os dois. O `p - q` do C."""
        if outro.tipo() != self._tipo:
            raise _erro(
                f"nao da para medir distancia entre um {self._tipo}* e um "
                f"{outro.tipo()}*.",
                nota="a conta e em ELEMENTOS, e os dois tipos tem tamanhos "
                     "diferentes")
        return (self._desloc - outro.endereco()) // self.passo()

    def cluster(self, quantos):
        """Os `quantos` elementos a partir daqui."""
        atual = self
        saida = []
        for _ in range(int(quantos)):
            saida.append(atual.ler())
            atual = atual.mais(1)
        return saida

    def _outro(self, desloc):
        novo = Ponteiro.__new__(Ponteiro)
        novo._bloco = self._bloco
        novo._tipo = self._tipo
        novo._desloc = desloc
        novo._ordem = self._ordem
        return novo

    def __repr__(self):
        estado = "nulo" if self.e_nulo() else f"+{self._desloc}"
        return f"<ponteiro {self._tipo}* {estado}>"


def ponteiro(alvo, tipo="u8", deslocamento=0, ordem="rede"):
    return Ponteiro(alvo, tipo, deslocamento, ordem)


class _Nulo(Ponteiro):
    """O ponteiro que nao aponta para lugar nenhum.

    Diferente do `void` da linguagem: aqui o endereco existe e vale
    zero. Ler dele e a falha de segmentacao classica — e aqui ela vira
    uma mensagem em vez de derrubar o processo.
    """

    __slots__ = ()

    def __init__(self):
        vazio = Bloco(0)
        vazio.liberar()
        Ponteiro.__init__(self, vazio, "u8", 0)

    def e_nulo(self):
        return True

    def ler(self):
        raise _erro("este ponteiro e nulo.",
                    nota="o endereco existe e vale zero; le-lo seria a "
                         "falha de segmentacao classica",
                    dica="confira 'p.e_nulo()' antes de ler",
                    classe="NullPointerError")

    def escrever(self, _valor):
        raise _erro("este ponteiro e nulo.",
                    dica="confira 'p.e_nulo()' antes de escrever",
                    classe="NullPointerError")

    def __repr__(self):
        return "<ponteiro nulo>"


def nulo():
    return _Nulo()


# ═══════════════════════════════════════════════════════════
#  Uniao e enumeracao — sem FFI
# ═══════════════════════════════════════════════════════════

def uniao(nome, campos, ordem="rede"):
    """Todos os campos no MESMO deslocamento zero.

    O tamanho e o do maior. Escrever um e ler outro devolve a
    reinterpretacao dos bytes — que e o ponto de uma uniao, e tambem o
    que a torna perigosa quando o tipo escrito nao e registrado em
    algum lugar.
    """
    molde = Molde(nome, campos, ordem, empacotado=True)
    for nome_campo in molde._desloc:
        molde._desloc[nome_campo] = 0
    molde.tamanho = max(l for _f, l, _q in molde._formato.values())
    return molde


def tamanho_de(tipo_ou_molde):
    if isinstance(tipo_ou_molde, Molde):
        return tipo_ou_molde.tamanho
    nome = str(tipo_ou_molde)
    if nome not in TIPOS:
        raise _erro(f"tipo desconhecido: '{nome}'."
                    f"{_parecido(nome, TIPOS)}",
                    nota=f"os tipos sao: {', '.join(sorted(TIPOS))}")
    return TIPOS[nome][1]


def alinhamento_de(tipo_ou_molde):
    if isinstance(tipo_ou_molde, Molde):
        return max(_largura(t) for _n, t, _q in tipo_ou_molde.campos)
    return tamanho_de(tipo_ou_molde)


def tipos():
    """Os tipos ESCALARES — os que um ponteiro, `tamanho_de` e o
    `Arcane.Bytes` aceitam. `char` e `bytes` so existem como campo de
    molde (o tamanho e o `quantos`), e ficam fora daqui de proposito."""
    return sorted(TIPOS)


# ═══════════════════════════════════════════════════════════
#  Operacoes de bits
# ═══════════════════════════════════════════════════════════
#
# Por que funcoes, e nao operadores: os tres simbolos de toda linguagem
# ja tem dono aqui. `>>` e o PIPELINE, `|` e a uniao de tipos e `&` a
# intersecao. Um `a >> 2` que deslocasse bits mudaria o sentido de todo
# pipeline escrito; e `a & b` seria lido como tipo onde uma anotacao e
# possivel. Os nomes abaixo nao disputam nada.

def _inteiro(valor, nome):
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise _erro(f"{nome} opera sobre inteiros, e veio {valor!r}.",
                    dica="int(x) antes, se for texto")
    return valor


def bits_e(a, b):
    """E bit a bit: fica 1 so onde os dois tem 1 — a MASCARA."""
    return _inteiro(a, "bits_e") & _inteiro(b, "bits_e")


def bits_ou(a, b):
    """OU bit a bit: liga o que estiver ligado em qualquer um."""
    return _inteiro(a, "bits_ou") | _inteiro(b, "bits_ou")


def bits_xou(a, b):
    """OU exclusivo: 1 onde os dois diferem. Aplicado duas vezes, desfaz."""
    return _inteiro(a, "bits_xou") ^ _inteiro(b, "bits_xou")


def bits_nao(a, largura):
    """Inverte os bits DENTRO da largura.

    A largura e obrigatoria: o inteiro da linguagem nao tem tamanho, e o
    NAO de um numero sem tamanho e negativo — `~5` no Python da -6, que
    nao e o que quem inverte um byte quer.
    """
    n, bits = _inteiro(a, "bits_nao"), int(largura)
    if bits < 1:
        raise _erro("a largura precisa ser de ao menos 1 bit.")
    if n < 0 or n >= (1 << bits):
        raise _erro(f"{n} nao cabe em {bits} bits.",
                    classe="BufferOverflowError")
    return ((1 << bits) - 1) ^ n


def deslocar(a, casas):
    """Desloca para a ESQUERDA com casas positivas, direita com negativas.

    Um sentido so, com sinal, em vez de dois nomes: `deslocar(x, -4)` le
    como "quatro casas para a direita", e evita a duvida de qual dos
    dois e o `>>`.
    """
    n, k = _inteiro(a, "deslocar"), int(casas)
    return n << k if k >= 0 else n >> (-k)


def contar_uns(a):
    """Quantos bits estao ligados (o popcount)."""
    n = _inteiro(a, "contar_uns")
    if n < 0:
        raise _erro("contar_uns e para inteiros nao negativos.")
    return bin(n).count("1")


def bit_ligado(a, posicao):
    """O bit na posicao (0 e o de BAIXO) esta ligado?"""
    return bool((_inteiro(a, "bit_ligado") >> int(posicao)) & 1)


def ligar_bit(a, posicao):
    return _inteiro(a, "ligar_bit") | (1 << int(posicao))


def desligar_bit(a, posicao):
    return _inteiro(a, "desligar_bit") & ~(1 << int(posicao))


# ═══════════════════════════════════════════════════════════
#  Campos de bits
# ═══════════════════════════════════════════════════════════

class MoldeDeBits:
    """Campos menores que um byte, dentro de um inteiro.

    O primeiro campo e o de CIMA (os bits mais significativos), que e
    como toda RFC desenha um cabecalho: em IPv4, `versao` (4 bits) vem
    antes de `ihl` (4 bits) no mesmo byte. O C deixa essa ordem para o
    compilador — e e por isso que protocolo nao se escreve com bitfield
    do C, e sim com mascara e deslocamento, que e o que isto faz.
    """

    __slots__ = ("nome", "campos", "largura", "_posicoes")

    def __init__(self, nome, campos, largura=8):
        self.nome = str(nome)
        self.largura = int(largura)
        lista = [(str(c[0]), int(c[1])) for c in (campos or [])]
        if not lista:
            raise _erro(f"'{self.nome}' precisa de ao menos um campo.",
                        dica='Est.campos_de_bits("B", [["versao", 4], '
                             '["ihl", 4]])')
        nomes = [n for n, _ in lista]
        repetidos = sorted({n for n in nomes if nomes.count(n) > 1})
        if repetidos:
            raise _erro(f"'{self.nome}' declara '{repetidos[0]}' duas vezes.")
        ruins = [n for n, b in lista if b < 1]
        if ruins:
            raise _erro(f"o campo '{ruins[0]}' precisa de ao menos 1 bit.")
        total = sum(b for _, b in lista)
        if total > self.largura:
            raise _erro(
                f"os campos de '{self.nome}' somam {total} bits, e a "
                f"largura e {self.largura}.",
                nota="o que passasse da largura seria cortado ao gravar, "
                     "e lido como zero",
                dica=f"use largura := {-(-total // 8) * 8}")
        self.campos = lista
        self._posicoes = {}
        topo = self.largura
        for nome_campo, bits in lista:
            topo -= bits
            self._posicoes[nome_campo] = (topo, bits)

    def ler(self, valor):
        """O inteiro aberto em campos, como vault."""
        numero = int(valor)
        if numero < 0 or numero >= (1 << self.largura):
            raise _erro(f"{numero} nao cabe em {self.largura} bits.")
        return {n: (numero >> pos) & ((1 << bits) - 1)
                for n, (pos, bits) in self._posicoes.items()}

    def juntar(self, valores):
        """Os campos de volta num inteiro. O que faltar vale zero."""
        desconhecidos = set(valores or {}) - set(self._posicoes)
        if desconhecidos:
            alvo = sorted(desconhecidos)[0]
            raise _erro(f"'{self.nome}' nao tem o campo '{alvo}'."
                        f"{_parecido(alvo, self._posicoes)}")
        numero = 0
        for nome_campo, valor in (valores or {}).items():
            pos, bits = self._posicoes[nome_campo]
            v = int(valor)
            if v < 0 or v >= (1 << bits):
                raise _erro(
                    f"{v} nao cabe em '{nome_campo}': sao {bits} bit(s), "
                    f"de 0 a {(1 << bits) - 1}.",
                    nota="sem esta conferencia o valor invadiria o campo "
                         "vizinho — o defeito aparece no OUTRO campo",
                    classe="BufferOverflowError")
            numero |= v << pos
        return numero

    def mapa(self):
        return [{"campo": n, "bits": b, "deslocamento": self._posicoes[n][0],
                 "mascara": ((1 << b) - 1) << self._posicoes[n][0]}
                for n, b in self.campos]

    def __repr__(self):
        return f"<bits {self.nome}, {len(self.campos)} campo(s) em {self.largura}>"


def campos_de_bits(nome, campos, largura=8):
    return MoldeDeBits(nome, campos, largura)


# ═══════════════════════════════════════════════════════════
#  Varint (LEB128) e zigzag
# ═══════════════════════════════════════════════════════════

def varint(numero):
    """O inteiro em LEB128 sem sinal: 7 bits por byte, o alto diz "tem mais".

    E o formato do Protocol Buffers, do WebAssembly e do DWARF: numero
    pequeno ocupa um byte, e nao ha teto. Negativo e recusado — em
    LEB128 sem sinal, -1 viraria dez bytes. Para negativos, `zigzag`.
    """
    n = int(numero)
    if n < 0:
        raise _erro(
            f"varint nao guarda negativo ({n}).",
            nota="sem sinal, -1 viraria o maior numero de 64 bits: dez bytes",
            dica="Est.varint(Est.zigzag(n)) — e o que o protobuf faz com sint64")
    saida = bytearray()
    while True:
        parte = n & 0x7F
        n >>= 7
        if n:
            saida.append(parte | 0x80)
        else:
            saida.append(parte)
            return bytes(saida)


def ler_varint(dados, deslocamento=0):
    """`{valor, tamanho}` — o numero e quantos bytes ele ocupou."""
    crus = _bytes_de(dados)
    pos = int(deslocamento)
    valor, desloc, lidos = 0, 0, 0
    while True:
        if pos + lidos >= len(crus):
            raise _erro(
                f"o varint que comeca no byte {pos} nao termina: os dados "
                f"acabaram depois de {lidos} byte(s).",
                nota="todo byte lido tinha o bit alto ligado, que quer dizer "
                     "'ainda tem mais'",
                classe="BufferOverflowError")
        byte = crus[pos + lidos]
        valor |= (byte & 0x7F) << desloc
        lidos += 1
        desloc += 7
        if not byte & 0x80:
            return {"valor": valor, "tamanho": lidos}
        if lidos >= 10:
            raise _erro(f"varint com mais de 10 bytes no byte {pos}.",
                        nota="nenhum inteiro de 64 bits precisa de tanto; "
                             "isto e dado corrompido, ou nao e um varint",
                        classe="BufferOverflowError")


def zigzag(numero):
    """Intercala negativos e positivos: 0, -1, 1, -2 viram 0, 1, 2, 3.

    Assim um -1 cabe em um byte de varint, em vez de dez.
    """
    n = int(numero)
    return (n << 1) if n >= 0 else ((-n << 1) - 1)


def desfazer_zigzag(numero):
    n = int(numero)
    return (n >> 1) if not n & 1 else -((n + 1) >> 1)


# ═══════════════════════════════════════════════════════════
#  Conferencia e ordem
# ═══════════════════════════════════════════════════════════

def crc32(dados, inicial=0):
    """O CRC-32 do PNG, do ZIP e do gzip — o mesmo polinomio dos tres.

    `inicial` continua uma conta: o CRC de um chunk PNG e o do TIPO mais
    os DADOS, e da para calcular em duas partes.
    """
    return zlib.crc32(bytes(_bytes_de(dados)), int(inicial)) & 0xFFFFFFFF


def trocar_ordem(valor, tipo="u32"):
    """O mesmo numero com os bytes invertidos (o `bswap`)."""
    tipo = str(tipo)
    if tipo not in TIPOS or tipo in ("f32", "f64", "bool"):
        raise _erro(f"trocar_ordem e para inteiros, e '{tipo}' nao e.",
                    dica="use u16, u32, u64 ou os com sinal")
    letra, _ = TIPOS[tipo]
    return struct.unpack("<" + letra, struct.pack(">" + letra, int(valor)))[0]


# ═══════════════════════════════════════════════════════════
#  Arquivo mapeado
# ═══════════════════════════════════════════════════════════

def _so_leitura(mapa):
    """Um mmap de leitura recusa ate a escrita de zero bytes."""
    try:
        antes = mapa.tell()
        mapa.write(b"")
        mapa.seek(antes)
        return False
    except TypeError:
        return True


def mapear(caminho, escrita=False):
    """O arquivo como um Bloco, sem le-lo inteiro.

    O sistema operacional traz para a memoria so as paginas tocadas: um
    arquivo de 4 GB com um cabecalho de 64 bytes custa 4 KB de leitura.
    Com `escrita := yes`, escrever numa janela escreve **no arquivo**; e
    `sincronizar()` garante que chegou ao disco.

    O arquivo nao pode ser vazio — o mmap de zero bytes nao existe.
    """
    caminho = str(caminho)
    if not os.path.exists(caminho):
        raise _erro(f"o arquivo '{caminho}' nao existe.",
                    dica="crie-o com o tamanho certo antes: IO.write_bytes")
    if os.path.getsize(caminho) == 0:
        raise _erro(f"'{caminho}' esta vazio, e nao ha o que mapear.",
                    dica="escreva o tamanho que o formato exige antes")
    modo = "r+b" if escrita else "rb"
    with open(caminho, modo) as arquivo:
        acesso = mmap.ACCESS_WRITE if escrita else mmap.ACCESS_READ
        mapa = mmap.mmap(arquivo.fileno(), 0, access=acesso)
    alvo = Bloco(0)
    alvo._dados = mapa
    return alvo


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

class ArcaneEstrutura:
    """Arcane.Estrutura — layout binario com nome, janela e ponteiro."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Estrutura",

            # ── o molde ──
            "definir": definir,
            "Molde": Molde,
            "uniao": uniao,

            # ── o bloco ──
            "bloco": bloco,
            "de_bytes": de_bytes,
            "Bloco": Bloco,

            # ── sem copiar ──
            "janela": janela,
            "janelas": janelas,
            "Janela": Janela,

            # ── ponteiro ──
            "ponteiro": ponteiro,
            "nulo": nulo,
            "Ponteiro": Ponteiro,

            # ── o que os tipos dizem ──
            "tipos": tipos,
            "tamanho_de": tamanho_de,
            "alinhamento_de": alinhamento_de,
            "trocar_ordem": trocar_ordem,

            # ── operacoes de bits ──
            "bits_e": bits_e,
            "bits_ou": bits_ou,
            "bits_xou": bits_xou,
            "bits_nao": bits_nao,
            "deslocar": deslocar,
            "contar_uns": contar_uns,
            "bit_ligado": bit_ligado,
            "ligar_bit": ligar_bit,
            "desligar_bit": desligar_bit,

            # ── bits, varint e conferencia ──
            "campos_de_bits": campos_de_bits,
            "MoldeDeBits": MoldeDeBits,
            "varint": varint,
            "ler_varint": ler_varint,
            "zigzag": zigzag,
            "desfazer_zigzag": desfazer_zigzag,
            "crc32": crc32,

            # ── arquivo mapeado ──
            "mapear": mapear,
        }
