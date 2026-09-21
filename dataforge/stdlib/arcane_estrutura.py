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
import struct
import threading

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

        desconhecidos = [t for _, t, _ in lista if t not in TIPOS]
        if desconhecidos:
            alvo = desconhecidos[0]
            raise _erro(
                f"tipo desconhecido: '{alvo}'."
                f"{_parecido(alvo, TIPOS)}",
                nota=f"os tipos sao: {', '.join(sorted(TIPOS))}")

        self.campos = lista
        self._desloc = {}
        self._formato = {}
        posicao = 0
        maior = 1
        for nome_campo, tipo, quantos in lista:
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

    def _ler_campo(self, crus, base, campo):
        formato, largura, quantos = self._formato[campo]
        inicio = base + self._desloc[campo]
        valores = struct.unpack_from(formato, crus, inicio)
        return list(valores) if quantos > 1 else valores[0]

    def _escrever_campo(self, crus, base, campo, valor):
        formato, largura, quantos = self._formato[campo]
        inicio = base + self._desloc[campo]
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
            saida.append({"campo": nome_campo, "tipo": tipo,
                          "quantos": quantos,
                          "deslocamento": self._desloc[nome_campo],
                          "bytes": largura})
        return saida

    def enchimento(self):
        """Quantos bytes sao SO alinhamento. Zero se empacotado."""
        util = sum(l for _f, l, _q in self._formato.values())
        return self.tamanho - util

    def __call__(self, **valores):
        return self.empacotar(valores)

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
            self._dados = bytearray()
        return True

    def bytes(self):
        return bytes(self.dados())

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
        return max(TIPOS[t][1] for _n, t, _q in tipo_ou_molde.campos)
    return tamanho_de(tipo_ou_molde)


def tipos():
    return sorted(TIPOS)


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
        }
