# -*- coding: utf-8 -*-
"""Arcane.C — chamar biblioteca nativa, com o layout na mão.

O que faltava
-------------
A ponte (`adopt Python.numpy`) resolve "preciso de algo que alguém já
escreveu **em Python**". O degrau de baixo não existia: chamar uma
função de uma biblioteca **C** — a `libm`, a `libz`, o `.so` que a
empresa mantém há quinze anos — sem escrever módulo de extensão e sem
trazer dependência.

    libm := C.matematica()
    raiz := libm.funcao("sqrt", ["f64"], "f64")
    raiz(16.0)                                  # 4.0

Isto roda sobre o `ctypes`, que é da biblioteca padrão do Python: a
promessa de zero dependência continua de pé.

Cinco decisões
--------------
1. **Os tipos são declarados, e não adivinhados.** `funcao(nome,
   [tipos], retorno)` obriga a dizer a assinatura. Sem isso, um `int`
   onde o C espera `long` passa em 90% dos casos e corrompe memória nos
   outros 10% — em silêncio, e longe da linha que causou.

2. **O erro de FFI é traduzido.** Biblioteca que não abre e símbolo que
   não existe são os dois erros mais comuns, e os dois chegam do sistema
   ilegíveis. Aqui eles dizem o nome, onde foi procurado e o que fazer.

3. **O layout é exposto.** `tamanho`, `alinhamento` e `deslocamentos`
   vêm do próprio `ctypes`, que segue a ABI da plataforma. É a parte que
   ninguém acerta de cabeça — e a que quebra quando a struct do C muda.

4. **O callback é um objeto com tempo de vida.** Ele precisa continuar
   vivo enquanto o C puder chamá-lo: um callback coletado no meio de um
   `qsort` derruba o processo, e a pilha não fala do DataForge. Por isso
   `retorno_de_chamada` devolve algo que se segura — e que diz se ainda
   está vivo.

5. **Nada disto é seguro, e o módulo não finge.** Ponteiro cru, aritmética
   de endereço e `liberar` são as ferramentas de quem sabe o que está
   fazendo. O que dá para conferir sem custo — nulo, tipo desconhecido,
   símbolo ausente — é conferido; o resto é responsabilidade de quem
   chama, e a documentação diz isso em vez de prometer o contrário.
"""

import ctypes
import ctypes.util
import sys

from ..errors import RuntimeError_

#: Os tipos que atravessam a fronteira, e o que cada um é no C.
#: A lista é FECHADA: um tipo inventado vira erro com a lista junto, e
#: não um valor lido do lugar errado.
_TIPOS = {
    "void": None,
    "bool": ctypes.c_bool,
    "i8": ctypes.c_int8, "u8": ctypes.c_uint8,
    "i16": ctypes.c_int16, "u16": ctypes.c_uint16,
    "i32": ctypes.c_int32, "u32": ctypes.c_uint32,
    "i64": ctypes.c_int64, "u64": ctypes.c_uint64,
    "f32": ctypes.c_float, "f64": ctypes.c_double,
    "texto": ctypes.c_char_p,
    "bytes": ctypes.c_char_p,
    "ponteiro": ctypes.c_void_p,
    "tamanho": ctypes.c_size_t,
    "char": ctypes.c_char,
}


def _tipo(nome, onde="este tipo"):
    chave = str(nome)
    if chave not in _TIPOS:
        raise RuntimeError_(
            f"'{chave}' não é um tipo do C que eu saiba passar.", 0, 0,
            nota=f"tipos: {', '.join(sorted(t for t in _TIPOS if t != 'void'))}",
            dica=f"use um da lista em {onde}",
            doc="ffi/c")
    return _TIPOS[chave]


def _para_c(valor, tipo):
    """O ajuste que o ctypes não faz sozinho: texto vira bytes."""
    if tipo in ("texto", "bytes") and isinstance(valor, str):
        return valor.encode("utf-8")
    if isinstance(valor, Ponteiro):
        return valor.endereco()
    if isinstance(valor, Bloco):
        # Um bloco passado onde o C espera ponteiro é o endereço dele:
        # obrigar '.endereco()' em toda chamada seria cerimônia sem ganho.
        return valor.endereco()
    if isinstance(valor, RetornoDeChamada):
        return valor._funcao
    if isinstance(valor, Estruturado):
        return ctypes.byref(valor._dado)
    return valor


def _do_c(valor, tipo):
    if valor is None:
        return None
    if tipo == "texto" and isinstance(valor, bytes):
        return valor.decode("utf-8", errors="replace")
    return valor


# ═════════════════════════════════════════════════════════════
#  A biblioteca
# ═════════════════════════════════════════════════════════════

class Biblioteca:
    """Uma biblioteca aberta — o `dlopen`, com nome e símbolos."""

    __slots__ = ("_lib", "_nome", "_caminho", "_funcoes")

    def __init__(self, lib, nome, caminho):
        self._lib = lib
        self._nome = nome
        self._caminho = caminho
        self._funcoes = {}

    def nome(self):
        return self._nome

    def caminho(self):
        return self._caminho or self._nome

    def tem(self, simbolo):
        """O símbolo existe? É o `dlsym` sem levantar."""
        try:
            getattr(self._lib, str(simbolo))
            return True
        except AttributeError:
            return False

    def funcao(self, simbolo, argumentos=None, retorno="void"):
        """Uma função com a assinatura DECLARADA.

        Declarar é obrigatório porque adivinhar erra fora do caso comum:
        um `i32` onde o C espera `i64` passa quase sempre e corrompe
        memória no resto — longe da linha que causou.
        """
        nome = str(simbolo)
        try:
            bruta = getattr(self._lib, nome)
        except AttributeError:
            raise RuntimeError_(
                f"a biblioteca '{self._nome}' não tem o símbolo '{nome}'.",
                0, 0,
                nota="em C++ o nome é decorado (name mangling) — procure o "
                     "símbolo exportado com 'extern \"C\"'",
                dica=f"confira com {self._nome}.tem(\"{nome}\"), ou veja os "
                     f"símbolos com 'nm -gU' / 'objdump -T'",
                doc="ffi/c") from None
        tipos = [str(a) for a in (argumentos or [])]
        bruta.argtypes = [_tipo(a, f"os argumentos de '{nome}'") for a in tipos]
        bruta.restype = _tipo(retorno, f"o retorno de '{nome}'")
        chamavel = _Funcao(bruta, nome, tipos, str(retorno))
        self._funcoes[nome] = chamavel
        return chamavel

    def __repr__(self):                                    # pragma: no cover
        return f"<biblioteca {self._nome}>"


class _Funcao:
    """Uma função nativa pronta para ser chamada da linguagem."""

    __slots__ = ("_bruta", "_nome", "_argumentos", "_retorno")

    def __init__(self, bruta, nome, argumentos, retorno):
        self._bruta = bruta
        self._nome = nome
        self._argumentos = argumentos
        self._retorno = retorno

    @property
    def name(self):                    # o interpretador usa isto no erro
        return self._nome

    def assinatura(self):
        return {"nome": self._nome, "argumentos": list(self._argumentos),
                "retorno": self._retorno}

    def __call__(self, *valores):
        if len(valores) != len(self._argumentos):
            raise RuntimeError_(
                f"'{self._nome}' recebe {len(self._argumentos)} argumento(s), "
                f"e foram passados {len(valores)}.", 0, 0,
                nota=f"assinatura: ({', '.join(self._argumentos)}) -> "
                     f"{self._retorno}",
                doc="ffi/c")
        prontos = [_para_c(v, t) for v, t in zip(valores, self._argumentos)]
        return _do_c(self._bruta(*prontos), self._retorno)

    def __repr__(self):                                    # pragma: no cover
        return f"<funcao C {self._nome}>"


def carregar(alvo, procurar=True):
    """Abre a biblioteca: por nome ('m', 'z') ou por caminho."""
    nome = str(alvo)
    tentativas = [nome]
    if procurar:
        achado = ctypes.util.find_library(nome.replace("lib", "", 1)
                                          if nome.startswith("lib") else nome)
        if achado:
            tentativas.insert(0, achado)
    for caminho in tentativas:
        try:
            return Biblioteca(ctypes.CDLL(caminho), nome, caminho)
        except OSError:
            continue
    raise RuntimeError_(
        f"não consegui abrir a biblioteca '{nome}'.", 0, 0,
        nota=f"procurei por: {', '.join(tentativas)}",
        dica=_dica_do_sistema(nome),
        doc="ffi/c")


def _dica_do_sistema(nome):
    if sys.platform.startswith("win"):
        return (f"no Windows, passe o caminho do .dll ou ponha a pasta dele "
                f"no PATH")
    if sys.platform == "darwin":
        return (f"no macOS, o arquivo é '.dylib'; tente o caminho completo, "
                f"ou instale a biblioteca (brew install {nome})")
    return (f"no Linux, o arquivo é 'lib{nome}.so'; instale o pacote -dev "
            f"ou ajuste LD_LIBRARY_PATH")


def padrao():
    """A biblioteca C do sistema — `libc`, ou o equivalente."""
    if sys.platform.startswith("win"):
        return Biblioteca(ctypes.CDLL("msvcrt"), "msvcrt", "msvcrt")
    return carregar("c")


def matematica():
    """A `libm`. No macOS ela mora dentro da libSystem, e isso é tratado."""
    if sys.platform == "darwin":
        return carregar("System")
    if sys.platform.startswith("win"):
        return Biblioteca(ctypes.CDLL("msvcrt"), "msvcrt", "msvcrt")
    return carregar("m")


def do_processo():
    """Os símbolos do próprio processo — o `dlopen(NULL)`."""
    return Biblioteca(ctypes.CDLL(None), "<processo>", "")


# ═════════════════════════════════════════════════════════════
#  Estruturas e uniões
# ═════════════════════════════════════════════════════════════

class Molde:
    """Uma `struct` (ou `union`) do C, com o layout da plataforma."""

    __slots__ = ("_classe", "_campos", "_uniao")

    def __init__(self, campos, uniao=False):
        pares = []
        for campo in campos:
            nome, tipo = (campo[0], campo[1]) if not isinstance(campo, dict) \
                else (campo.get("nome"), campo.get("tipo"))
            pares.append((str(nome), _tipo(tipo, f"o campo '{nome}'")))
        base = ctypes.Union if uniao else ctypes.Structure
        self._classe = type("Molde", (base,), {"_fields_": pares})
        self._campos = [(n, t) for n, t in
                        zip([p[0] for p in pares],
                            [c[1] if not isinstance(c, dict) else c.get("tipo")
                             for c in campos])]
        self._uniao = uniao

    def tamanho(self):
        """Em bytes, **com padding** — o tamanho de verdade."""
        return ctypes.sizeof(self._classe)

    def alinhamento(self):
        return ctypes.alignment(self._classe)

    def deslocamentos(self):
        """Onde cada campo começa. É aqui que o padding aparece."""
        return {nome: getattr(self._classe, nome).offset
                for nome, _ in self._campos}

    def campos(self):
        return {nome: tipo for nome, tipo in self._campos}

    def criar(self, valores=None):
        dado = self._classe()
        estruturado = Estruturado(dado, self)
        for nome, valor in (valores or {}).items():
            estruturado.escrever(nome, valor)
        return estruturado

    def de_ponteiro(self, ponteiro):
        """Lê a struct que já está na memória, sem copiar."""
        endereco = ponteiro.endereco() if isinstance(ponteiro, Ponteiro) \
            else int(ponteiro)
        if not endereco:
            raise _erro_de_nulo()
        return Estruturado(self._classe.from_address(endereco), self)

    def __repr__(self):                                    # pragma: no cover
        forma = "uniao" if self._uniao else "estrutura"
        return f"<{forma} {self.tamanho()} bytes>"


class Estruturado:
    """Um valor de struct: lê, escreve e aponta."""

    __slots__ = ("_dado", "_molde")

    def __init__(self, dado, molde):
        self._dado = dado
        self._molde = molde

    def ler(self, campo):
        nome = str(campo)
        self._exigir_campo(nome)
        tipo = self._molde.campos()[nome]
        return _do_c(getattr(self._dado, nome), tipo)

    def escrever(self, campo, valor):
        nome = str(campo)
        self._exigir_campo(nome)
        tipo = self._molde.campos()[nome]
        setattr(self._dado, nome, _para_c(valor, tipo))
        return valor

    def tudo(self):
        return {nome: self.ler(nome) for nome in self._molde.campos()}

    def endereco(self):
        return ctypes.addressof(self._dado)

    def ponteiro(self):
        return Ponteiro(ctypes.addressof(self._dado), "ponteiro")

    def bytes(self):
        return bytes(memoryview(self._dado).cast("B"))

    def _exigir_campo(self, nome):
        if nome not in self._molde.campos():
            raise RuntimeError_(
                f"esta estrutura não tem o campo '{nome}'.", 0, 0,
                nota=f"campos: {', '.join(self._molde.campos())}",
                doc="ffi/c")

    def __repr__(self):                                    # pragma: no cover
        return f"<estruturado {self.tudo()}>"


def estrutura(campos):
    return Molde(list(campos), uniao=False)


def uniao(campos):
    return Molde(list(campos), uniao=True)


def enumeracao(pares):
    """Um `enum` do C é inteiro com nome — e aqui ele é um vault.

    Não há tipo novo a criar: o que atravessa a fronteira é o número, e
    inventar um embrulho só esconderia isso.
    """
    return {str(nome): int(valor) for nome, valor in dict(pares).items()}


# ═════════════════════════════════════════════════════════════
#  Ponteiros crus e memória
# ═════════════════════════════════════════════════════════════

def _erro_de_nulo():
    return RuntimeError_(
        "este ponteiro é nulo: não há o que ler nem onde escrever.", 0, 0,
        nota="ler um endereço nulo derruba o processo, e a pilha não fala "
             "do DataForge — por isso a conferência acontece aqui",
        dica="confira com 'p.e_nulo()' antes de usar",
        doc="ffi/c")


class Ponteiro:
    """Um endereço, com o tipo do que ele aponta.

    O tipo não é decoração: é ele que diz quanto `deslocar(1)` anda e
    como `ler()` interpreta os bytes.
    """

    __slots__ = ("_endereco", "_tipo")

    def __init__(self, endereco=0, tipo="u8"):
        self._endereco = int(endereco or 0)
        self._tipo = str(tipo)
        _tipo_c = _tipo_do(self._tipo)

    def endereco(self):
        return self._endereco

    def tipo(self):
        return self._tipo

    def e_nulo(self):
        return self._endereco == 0

    def deslocar(self, quantos):
        """Anda `quantos` ITENS — não bytes. É a aritmética de ponteiro."""
        passo = tamanho_de(self._tipo)
        return Ponteiro(self._endereco + int(quantos) * passo, self._tipo)

    def deslocar_bytes(self, quantos):
        return Ponteiro(self._endereco + int(quantos), self._tipo)

    def ler(self):
        if self.e_nulo():
            raise _erro_de_nulo()
        alvo = _tipo_do(self._tipo)
        return _do_c(ctypes.cast(self._endereco,
                                 ctypes.POINTER(alvo)).contents.value,
                     self._tipo)

    def escrever(self, valor):
        if self.e_nulo():
            raise _erro_de_nulo()
        alvo = _tipo_do(self._tipo)
        ctypes.cast(self._endereco,
                    ctypes.POINTER(alvo)).contents.value = _para_c(valor, self._tipo)
        return valor

    def como(self, tipo):
        """O mesmo endereço, lido como outro tipo — o cast."""
        return Ponteiro(self._endereco, tipo)

    def bytes(self, quantos):
        if self.e_nulo():
            raise _erro_de_nulo()
        return ctypes.string_at(self._endereco, int(quantos))

    def texto(self):
        if self.e_nulo():
            raise _erro_de_nulo()
        return ctypes.string_at(self._endereco).decode("utf-8", errors="replace")

    def __repr__(self):                                    # pragma: no cover
        return f"<ponteiro {self._tipo} 0x{self._endereco:x}>"


def _tipo_do(nome):
    alvo = _tipo(nome, "o tipo do ponteiro")
    return ctypes.c_ubyte if alvo is None else alvo


def ponteiro(alvo, tipo="u8"):
    """Um ponteiro a partir de um endereço, um bloco ou uma estrutura."""
    if isinstance(alvo, Ponteiro):
        return Ponteiro(alvo.endereco(), tipo)
    if isinstance(alvo, Estruturado):
        return Ponteiro(alvo.endereco(), tipo)
    if isinstance(alvo, Bloco):
        return Ponteiro(alvo.endereco(), tipo)
    return Ponteiro(int(alvo or 0), tipo)


def nulo(tipo="u8"):
    return Ponteiro(0, tipo)


class Bloco:
    """Memória alocada à mão — e que só sai com `liberar`."""

    __slots__ = ("_buffer", "_bytes", "_vivo")

    def __init__(self, quantos):
        self._bytes = int(quantos)
        self._buffer = ctypes.create_string_buffer(self._bytes)
        self._vivo = True

    def endereco(self):
        self._exigir_vivo()
        return ctypes.addressof(self._buffer)

    def tamanho(self):
        return self._bytes

    def vivo(self):
        return self._vivo

    def bytes(self):
        self._exigir_vivo()
        return bytes(self._buffer.raw)

    def liberar(self):
        """Solta o bloco. Idempotente, como todo `soltar` daqui."""
        if not self._vivo:
            return False
        self._vivo = False
        self._buffer = None
        return True

    def _exigir_vivo(self):
        if not self._vivo:
            raise RuntimeError_(
                "este bloco já foi liberado.", 0, 0,
                nota="usar memória liberada é o defeito que mais derruba "
                     "processo em C",
                dica="aloque outro com C.alocar(bytes)", doc="ffi/c")

    def __repr__(self):                                    # pragma: no cover
        return f"<bloco {self._bytes} bytes{'' if self._vivo else ', livre'}>"


def alocar(bytes_quantos):
    """Memória crua, zerada. Quem aloca, libera."""
    return Bloco(bytes_quantos)


def liberar(bloco):
    if isinstance(bloco, Bloco):
        return bloco.liberar()
    return False


def de_bytes(dados):
    """Um bloco com esses bytes dentro — para passar ao C."""
    brutos = dados.encode("utf-8") if isinstance(dados, str) else bytes(dados)
    bloco = Bloco(len(brutos) + 1)
    ctypes.memmove(bloco.endereco(), brutos, len(brutos))
    return bloco


def para_bytes(alvo, quantos):
    """Lê `quantos` bytes de um bloco, ponteiro ou endereço."""
    endereco = (alvo.endereco() if isinstance(alvo, (Bloco, Ponteiro, Estruturado))
                else int(alvo))
    if not endereco:
        raise _erro_de_nulo()
    return ctypes.string_at(endereco, int(quantos))


def copiar(destino, origem, quantos):
    """`memcpy`, com os dois lados podendo ser bloco, ponteiro ou endereço."""
    def endereco_de(x):
        return (x.endereco() if isinstance(x, (Bloco, Ponteiro, Estruturado))
                else int(x))
    ctypes.memmove(endereco_de(destino), endereco_de(origem), int(quantos))
    return quantos


def tamanho_de(tipo):
    alvo = _tipo(tipo, "tamanho_de")
    return 0 if alvo is None else ctypes.sizeof(alvo)


def alinhamento_de(tipo):
    alvo = _tipo(tipo, "alinhamento_de")
    return 0 if alvo is None else ctypes.alignment(alvo)


def endianness():
    """'little' ou 'big' — o que importa ao ler formato binário."""
    return sys.byteorder


def tipos():
    return sorted(t for t in _TIPOS if t != "void")


# ═════════════════════════════════════════════════════════════
#  Callbacks
# ═════════════════════════════════════════════════════════════

class RetornoDeChamada:
    """Uma ação da linguagem, vista pelo C como ponteiro de função.

    Ele precisa continuar **vivo** enquanto o C puder chamá-lo: um
    callback coletado no meio de um `qsort` derruba o processo, e a pilha
    não fala do DataForge. Por isso ele é um objeto que se segura, e que
    responde se ainda vale.
    """

    __slots__ = ("_funcao", "_acao", "_tipo", "_vivo", "_argumentos", "_retorno")

    def __init__(self, acao, argumentos, retorno):
        self._acao = acao
        self._argumentos = [str(a) for a in (argumentos or [])]
        self._retorno = str(retorno)
        assinatura = [_tipo(self._retorno, "o retorno do callback")] + \
                     [_tipo(a, "os argumentos do callback") for a in self._argumentos]
        self._tipo = ctypes.CFUNCTYPE(*assinatura)
        self._funcao = self._tipo(self._chamar)
        self._vivo = True

    def _chamar(self, *valores):
        if not self._vivo:
            return 0
        saida = self._acao(*[_do_c(v, t) for v, t
                             in zip(valores, self._argumentos)])
        return _para_c(saida, self._retorno) if saida is not None else 0

    def chamar(self, *valores):
        """Chama pela ponte do C — o mesmo caminho que a biblioteca usa."""
        if not self._vivo:
            raise RuntimeError_(
                "este retorno de chamada já foi solto.", 0, 0,
                dica="crie outro, ou não solte enquanto o C puder chamar",
                doc="ffi/c")
        return _do_c(self._funcao(*[_para_c(v, t) for v, t
                                    in zip(valores, self._argumentos)]),
                     self._retorno)

    def endereco(self):
        return ctypes.cast(self._funcao, ctypes.c_void_p).value or 0

    def vivo(self):
        return self._vivo

    def soltar(self):
        if not self._vivo:
            return False
        self._vivo = False
        return True

    def assinatura(self):
        return {"argumentos": list(self._argumentos), "retorno": self._retorno}

    def __repr__(self):                                    # pragma: no cover
        return f"<callback {'vivo' if self._vivo else 'solto'}>"


def retorno_de_chamada(acao, argumentos=None, retorno="void"):
    return RetornoDeChamada(acao, argumentos, retorno)


class ArcaneC:
    """O dicionário que `adopt Arcane.C` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.C",

            # ── bibliotecas ──
            "carregar": carregar,
            "padrao": padrao,
            "matematica": matematica,
            "do_processo": do_processo,
            "Biblioteca": Biblioteca,

            # ── layout ──
            "estrutura": estrutura,
            "uniao": uniao,
            "enumeracao": enumeracao,
            "tamanho_de": tamanho_de,
            "alinhamento_de": alinhamento_de,
            "endianness": endianness,
            "tipos": tipos,

            # ── memória e ponteiros ──
            "ponteiro": ponteiro,
            "nulo": nulo,
            "alocar": alocar,
            "liberar": liberar,
            "de_bytes": de_bytes,
            "para_bytes": para_bytes,
            "copiar": copiar,
            "Ponteiro": Ponteiro,
            "Bloco": Bloco,

            # ── callbacks ──
            "retorno_de_chamada": retorno_de_chamada,
            "RetornoDeChamada": RetornoDeChamada,
        }
