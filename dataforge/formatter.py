"""
DataForge Formatter — `dataforge fmt`

Reescreve o código com regras determinísticas: mesmo arquivo, mesma saída.
Trabalha sobre o fluxo de tokens (não sobre a AST), para preservar comentários
e a intenção do autor.

Regras
------
* 4 espaços por nível de indentação; tabs viram espaços.
* Um espaço em volta de operadores binários e de ':=' — nenhum depois de '(',
  antes de ')' ou antes de ',' / ':' de bloco.
* Sem espaço entre um nome e o '(' da chamada.
* Nenhum espaço em branco no fim da linha.
* No máximo uma linha em branco dentro de um bloco, duas no topo do arquivo.
* O arquivo termina com exatamente uma quebra de linha.
"""

import re

from .lexer import Lexer
from .tokens import TokenType

INDENTACAO = "    "

# Operadores que recebem um espaço de cada lado
BINARIOS = {
    '+', '-', '*', '/', '%', '**', '//', '~/', ':=', '==', '!=', '<', '>',
    '<=', '>=', '>>', '=>', '->', '??', '+=', '-=', '*=', '/=', '%=',
}

PALAVRAS_BINARIAS = {
    'is', 'isnt', 'bigger', 'smaller', 'bigger_eq', 'smaller_eq',
    'and', 'or', 'in', 'as', 'to', 'from', 'step', 'extends', 'with',
    'using', 'when', 'given', 'otherwise',
}

# Palavras que abrem um bloco e por isso terminam a linha com ':'
ABRE_BLOCO = {
    'action', 'blueprint', 'trait', 'record', 'enum', 'given', 'orif',
    'otherwise', 'match', 'point', 'default', 'cycle', 'persist', 'perform',
    'monitor', 'handle', 'ensure', 'retry', 'thread', 'parallel', 'defer',
    'observe', 'async', 'stream',
}


class Formatter:
    """Formata código DataForge a partir do texto original."""

    def __init__(self, source: str, indent: str = INDENTACAO):
        self.source = source
        self.indent = indent

    def format(self) -> str:
        # A profundidade de cada linha vem da estrutura real do arquivo
        # (INDENT/DEDENT do lexer), nunca da contagem de espaços do original.
        profundidade = self._profundidade_por_linha()

        # As linhas que estao DENTRO de uma string de tres aspas.
        #
        # O formatador trabalha linha a linha sobre o texto cru — e uma
        # string multilinha ocupa varias. Sem esta marcacao, o conteudo
        # dela era reformatado como codigo: '<h1>' virava '< h1 >', dois
        # espacos viravam um, e um template HTML dentro do programa
        # chegava corrompido ao navegador. Formatar passava a MUDAR o
        # que o programa faz — a unica coisa que um formatador nao pode
        # fazer. O exercicio 194 quebrou exatamente assim.
        dentro_de_texto = self._linhas_de_texto_longo()

        linhas_saida = []
        em_branco = 0
        no_topo = True

        for numero, bruta in enumerate(self.source.split("\n"), start=1):
            if numero in dentro_de_texto:
                linhas_saida.append(bruta)      # verbatim, sem tocar
                em_branco = 0
                no_topo = False
                continue

            nua = bruta.strip()

            if not nua:
                em_branco += 1
                limite = 2 if no_topo else 1
                if em_branco <= limite and linhas_saida:
                    linhas_saida.append("")
                continue
            em_branco = 0
            no_topo = False

            nivel = profundidade.get(numero, 0)

            # Comentário sozinho na linha: preserva o texto, ajusta o recuo
            if nua.startswith("//") or nua.startswith("#"):
                linhas_saida.append(self.indent * nivel + nua)
                continue

            corpo = self._formatar_linha(nua)
            linhas_saida.append((self.indent * nivel + corpo).rstrip())

        texto = "\n".join(linhas_saida)
        return texto.rstrip("\n") + "\n"

    def _linhas_de_texto_longo(self):
        """As linhas de continuacao de toda string de tres aspas.

        A PRIMEIRA linha nao entra: ela tem codigo antes das aspas
        (x := ...) e precisa do recuo. A do FECHA tambem nao, pelo
        mesmo motivo — pode haver codigo depois dela.
        """
        TRIPLO_D = chr(34) * 3
        TRIPLO_S = chr(39) * 3
        marcadas = set()
        fonte = self.source
        i = 0
        linha = 1
        aspas_curtas = ""
        while i < len(fonte):
            c = fonte[i]
            if c == chr(10):
                linha += 1
                i += 1
                continue
            if aspas_curtas:
                if c == chr(92):
                    i += 2
                    continue
                if c == aspas_curtas:
                    aspas_curtas = ""
                i += 1
                continue
            if fonte.startswith(TRIPLO_D, i) or fonte.startswith(TRIPLO_S, i):
                marca = fonte[i:i + 3]
                fim = fonte.find(marca, i + 3)
                if fim < 0:
                    break                  # nao fechou: o lexer reclama
                miolo = fonte[i + 3:fim]
                # A linha do FECHA tambem entra quando ha conteudo
                # antes dele: em 'WHERE a = 1"""' o texto e da string,
                # e reformata-lo mudaria o SQL. So fica de fora a linha
                # que comeca com o fecha — ali o que vem depois e
                # codigo de verdade.
                for _ in range(miolo.count(chr(10))):
                    linha += 1
                    marcadas.add(linha)
                if miolo and not miolo.endswith(chr(10)):
                    pass                   # o fecha esta na mesma linha do texto
                else:
                    marcadas.discard(linha)
                i = fim + 3
                continue
            if c in (chr(34), chr(39)):
                aspas_curtas = c
            elif c == "/" and fonte.startswith("//", i):
                fim = fonte.find(chr(10), i)
                i = len(fonte) if fim < 0 else fim
                continue
            i += 1
        return marcadas

    def _profundidade_por_linha(self):
        """Mapeia cada linha do arquivo ao seu nível de bloco.

        Levanta o erro do lexer quando o arquivo não tokeniza: um formatador
        não deve adivinhar a estrutura de um código com indentação ambígua.
        """
        tokens = Lexer(self.source).tokenize()

        profundidade = {}
        nivel = 0
        abertos = 0
        inicio_de_linha = True
        for token in tokens:
            if token.type is TokenType.INDENT:
                nivel += 1
                continue
            if token.type is TokenType.DEDENT:
                nivel = max(0, nivel - 1)
                continue
            if token.type is TokenType.NEWLINE:
                inicio_de_linha = True
                continue
            if token.type is TokenType.EOF:
                break
            if inicio_de_linha or token.line not in profundidade:
                profundidade.setdefault(token.line, nivel + abertos)
                inicio_de_linha = False

            # O lexer NAO emite INDENT dentro de colchete, chave ou
            # parentese aberto — e a profundidade do formatador vem
            # dali. Sem contar aqui, uma lista multilinha voltava
            # encostada na margem: ainda compila, e fica ilegivel.
            #
            # O nivel do FECHA e o de fora, nao o de dentro: ']' alinha
            # com o '[' que o abriu, e nao com os itens.
            if token.type in (TokenType.LBRACKET, TokenType.LBRACE,
                              TokenType.LPAREN):
                abertos += 1
            elif token.type in (TokenType.RBRACKET, TokenType.RBRACE,
                                TokenType.RPAREN):
                abertos = max(0, abertos - 1)
                if inicio_de_linha or profundidade.get(token.line) is not None:
                    profundidade[token.line] = min(
                        profundidade.get(token.line, nivel + abertos),
                        nivel + abertos)

        # Linhas de comentário herdam o nível da próxima linha com código
        linhas = self.source.split("\n")
        proximo = 0
        for numero in range(len(linhas), 0, -1):
            if numero in profundidade:
                proximo = profundidade[numero]
            else:
                nua = linhas[numero - 1].strip()
                if nua.startswith(("//", "#")):
                    profundidade[numero] = proximo
        return profundidade

    def _formatar_linha(self, texto: str) -> str:
        """Normaliza espaços dentro de uma linha, preservando strings."""
        try:
            tokens = Lexer(texto + "\n").tokenize()
        except Exception:
            # Linha que o lexer recusa isolada (continuação, por exemplo):
            # preserva como está para não corromper o arquivo.
            return texto

        comentario = self._extrair_comentario(texto)
        partes = []
        anterior = None
        antes_do_anterior = None
        colchetes = 0

        for token in tokens:
            if token.type in (TokenType.NEWLINE, TokenType.EOF,
                              TokenType.INDENT, TokenType.DEDENT):
                continue
            # A profundidade de colchete distingue a fatia do vault: o
            # ':' de 'xs[1:4]' esta dentro de '[', o de '{"a": 1}' nao.
            if token.type is TokenType.LBRACKET:
                colchetes += 1
            elif token.type is TokenType.RBRACKET:
                colchetes = max(0, colchetes - 1)
            texto_token = self._render(token)
            if partes and self._precisa_espaco(
                    anterior, token, antes_do_anterior, colchetes > 0):
                partes.append(" ")
            partes.append(texto_token)
            antes_do_anterior = anterior
            anterior = token

        linha = self._encostar_pontuacao("".join(partes))
        if comentario:
            linha = f"{linha}  {comentario}" if linha else comentario
        return linha.rstrip()

    #: A limpeza de espaço em volta da pontuação.
    #:
    #: Ela roda sobre a linha MONTADA, e por isso precisa saber o que é
    #: código e o que é conteúdo de string. Sem essa distinção,
    #: `out "com :id"` virava `out "com:id"` e `"{{ id }}"` virava
    #: `"{{id}}"` — o formatador **alterando dados**, numa ferramenta
    #: que promete não mudar semântica.
    #:
    #: O bug apareceu num exercício sobre exportar API: o `{{ id }}` do
    #: Insomnia é significativo, e o `fmt` o destruía em silêncio.
    _LIMPEZAS = (
        (r"\s+([,;:])(?!=)", r"\1"),
        (r"\(\s+", "("),
        (r"\s+\)", ")"),
        (r"\[\s+", "["),
        (r"\s+\]", "]"),
        (r"\{\s+", "{"),
        (r"\s+\}", "}"),
    )

    @classmethod
    def _encostar_pontuacao(cls, linha):
        """Tira o espaço antes da pontuação — **fora** das strings."""
        partes = cls._partir_por_strings(linha)
        saida = []
        for texto, e_string in partes:
            if e_string:
                saida.append(texto)          # verbatim: é dado, não código
                continue
            for padrao, troca in cls._LIMPEZAS:
                texto = re.sub(padrao, troca, texto)
            saida.append(texto)
        return "".join(saida)

    @staticmethod
    def _partir_por_strings(linha):
        """A linha em pedaços (texto, é_string).

        Varre caractere a caractere porque é a única forma de acertar:
        uma expressão regular sobre aspas erra em `"ele disse \"oi\""`, e
        o lexer já foi usado — o que se tem aqui é a linha montada.
        """
        pedacos = []
        atual = []
        aspas = ""
        i = 0
        while i < len(linha):
            c = linha[i]
            if aspas:
                atual.append(c)
                if c == chr(92) and i + 1 < len(linha):
                    atual.append(linha[i + 1])
                    i += 2
                    continue
                if c == aspas:
                    pedacos.append(("".join(atual), True))
                    atual = []
                    aspas = ""
                i += 1
                continue

            if c in ('"', "'"):
                if atual:
                    pedacos.append(("".join(atual), False))
                atual = [c]
                aspas = c
                i += 1
                continue

            atual.append(c)
            i += 1

        if atual:
            # Aspas não fechada: trata como string, para não estragar o
            # que o lexer vai recusar de qualquer jeito.
            pedacos.append(("".join(atual), bool(aspas)))
        return pedacos

    @staticmethod
    def _extrair_comentario(texto):
        """Devolve o comentário no fim da linha, se houver.

        Percorre o token stream em vez de varrer caracteres: só assim strings
        comuns, strings interpoladas (que podem conter '#' e '//' no texto) e o
        operador '//' são distinguidos corretamente de um comentário.
        """
        try:
            tokens = Lexer(texto + "\n").tokenize()
        except Exception:
            return ""

        # O lexer descarta comentários; o que sobra é o código. Encontramos onde
        # o último token termina e olhamos o que vem depois na linha original.
        ultimo = None
        for token in tokens:
            if token.type in (TokenType.NEWLINE, TokenType.EOF,
                              TokenType.INDENT, TokenType.DEDENT):
                continue
            ultimo = token

        if ultimo is None:
            nua = texto.strip()
            return nua if nua.startswith(("//", "#")) else ""

        # Procura o início do comentário a partir do fim do último token.
        # A coluna do token é 1-based e aponta para o seu primeiro caractere.
        inicio_busca = max(0, ultimo.column - 1)
        resto = texto[inicio_busca:]
        for marcador in ("//", "#"):
            pos = resto.find(marcador)
            while pos != -1:
                absoluto = inicio_busca + pos
                # Confirma que o trecho antes ainda tokeniza sozinho — se sim,
                # o que vem depois é comentário.
                try:
                    Lexer(texto[:absoluto] + "\n").tokenize()
                    return texto[absoluto:].rstrip()
                except Exception:
                    pos = resto.find(marcador, pos + 1)
        return ""

    @staticmethod
    def _render(token):
        if token.type is TokenType.FLOOR_DIV:
            # Sempre a grafia inequívoca: reimprimir '//' faria a linha virar
            # comentário na próxima passagem do formatador.
            return '~/'
        if token.type is TokenType.STRING:
            valor = token.value
            aspas = "'" if '"' in valor and "'" not in valor else '"'
            corpo = valor.replace("\\", "\\\\")
            if aspas == '"':
                corpo = corpo.replace('"', '\\"')
            # O '\\r' precisa estar aqui junto do '\\n' e do '\\t'.
            # Sem ele, o escape virava um retorno de carro DE VERDADE
            # dentro da string, e o arquivo deixava de ter uma string
            # terminada — o pacote 'progresso', que usa '\\r' para
            # reescrever a linha do terminal, parava de compilar depois
            # de formatado.
            corpo = (corpo.replace("\n", "\\n")
                          .replace("\t", "\\t")
                          .replace("\r", "\\r"))
            return f"{aspas}{corpo}{aspas}"
        if token.type is TokenType.INTERP_STRING:
            partes = []
            for tipo, conteudo in token.value:
                if tipo == 'text':
                    # Reescapa o que o lexer já converteu, senão a próxima
                    # passagem não reconhece a string.
                    escapado = conteudo
                    for antes, depois in ((chr(92), chr(92) * 2),
                                          (chr(34), chr(92) + chr(34)),
                                          (chr(10), chr(92) + "n"),
                                          (chr(9), chr(92) + "t"),
                                          (chr(13), chr(92) + "r"),
                                          ("{", "{{"), ("}", "}}")):
                        escapado = escapado.replace(antes, depois)
                    partes.append(escapado)
                elif tipo == "fmt":
                    # A parte com formato traz (expressao, formato), e nao
                    # um texto. Sem este ramo, o formatador estourava com
                    # 'can only concatenate str (not tuple)' ao tocar em
                    # qualquer arquivo com '{x:.2f}'.
                    expressao, formato = conteudo
                    partes.append("{" + expressao + ":" + formato + "}")
                else:
                    partes.append("{" + conteudo + "}")
            return '$"' + "".join(partes) + '"'
        if token.type is TokenType.BOOLEAN:
            return token.text or ("yes" if token.value else "no")
        if token.type is TokenType.VOID:
            return "void"
        if token.type is TokenType.FLOAT:
            return repr(token.value)
        if token.type is TokenType.INTEGER:
            return str(token.value)
        return str(token.text if token.text is not None else token.value)

    @staticmethod
    def _precisa_espaco(anterior, atual, anterior_do_anterior=None,
                        dentro_de_colchete=False):
        if anterior is None:
            return False
        a, b = anterior, atual
        texto_a = str(a.text if a.text is not None else a.value)
        texto_b = str(b.text if b.text is not None else b.value)

        # Sem espaço depois de abre-delimitador ou antes de fecha
        if a.type in (TokenType.LPAREN, TokenType.LBRACKET):
            return False
        if b.type in (TokenType.RPAREN, TokenType.RBRACKET, TokenType.COMMA):
            return False
        if a.type is TokenType.LBRACE or b.type is TokenType.RBRACE:
            return False

        # Ponto de acesso não leva espaço
        if a.type in (TokenType.DOT, TokenType.SAFE_DOT):
            return False
        if b.type in (TokenType.DOT, TokenType.SAFE_DOT):
            return False

        # Chamada: nome( sem espaco.
        #
        # 'typeof', 'delete', 'len' sao PALAVRAS RESERVADAS que chamam
        # como funcao — olhar so IDENTIFIER escrevia 'typeof (1)', que
        # parece outra coisa. A regra e: se o token anterior e um nome
        # ou um fecha-delimitador, o parentese e de chamada.
        if b.type is TokenType.LPAREN and (
                a.type in (TokenType.IDENTIFIER, TokenType.RPAREN,
                           TokenType.RBRACKET)
                or _e_nome_chamavel(a)):
            return False
        # Indexação: nome[ sem espaço
        if b.type is TokenType.LBRACKET and a.type in (
                TokenType.IDENTIFIER, TokenType.RPAREN, TokenType.RBRACKET,
                TokenType.STRING):
            return False

        # ':' de bloco / de vault / de tipo
        if b.type is TokenType.COLON:
            return False
        if a.type is TokenType.COLON:
            # O ':' de FATIA nao respira: 'xs[1:4]' e um intervalo, e
            # 'xs[1: 4]' parece um par chave-valor. O de vault continua
            # espacado, porque ali ele separa chave de valor.
            if dentro_de_colchete:
                return False
            return True

        # Spread e unário grudam no operando
        if a.type is TokenType.SPREAD:
            return False
        if a.type is TokenType.AT:
            return False
        if b.type is TokenType.AT:
            return True

        # O '-' unário gruda; o binário respira.
        #
        # '-2' é um número negativo; '- 2' parece uma subtração a que
        # falta o termo da esquerda. A diferença entre os dois é o que
        # vem ANTES: depois de um valor ou de um fecha-delimitador, o
        # '-' subtrai; em qualquer outro lugar, ele nega.
        #
        # Sem esta regra, o formatador espacava todo '-' e 93 dos 216
        # exercicios ficavam permanentemente 'fora do formato' — rodar
        # 'fmt' os pioraria, entao ninguem rodava, e o '--check' era
        # inutil no CI.
        if a.type in (TokenType.MINUS, TokenType.PLUS) and \
                _e_unario(anterior_do_anterior):
            return False

        if texto_a in BINARIOS or texto_b in BINARIOS:
            return True
        if texto_a in PALAVRAS_BINARIAS or texto_b in PALAVRAS_BINARIAS:
            return True
        if a.type is TokenType.COMMA:
            return True
        return True


#: O que pode vir ANTES de um '-' binario: um valor, ou o fim de algo
#: que produz valor. Depois de qualquer outra coisa — inicio de linha,
#: operador, virgula, abre-parentese — o '-' e unario.
_ANTES_DE_BINARIO = (
    TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.FLOAT,
    TokenType.STRING, TokenType.RPAREN, TokenType.RBRACKET,
    TokenType.RBRACE,
)


def _e_nome_chamavel(token):
    """Uma palavra reservada que chama como funcao.

    'typeof(1)' e 'v.delete("k")' sao chamadas; o texto do token e um
    nome, ainda que o TIPO dele seja de palavra reservada.
    """
    texto = token.text if token.text is not None else str(token.value)
    return bool(texto) and (texto[0].isalpha() or texto[0] == "_") \
        and texto.replace("_", "").isalnum()


def _e_unario(antes):
    """O token anterior ao '-' diz se ele nega ou subtrai."""
    if antes is None:
        return True                     # comeco da linha: '-x'
    return antes.type not in _ANTES_DE_BINARIO


def format_source(source: str, indent: str = INDENTACAO) -> str:
    """Formata um trecho de código DataForge."""
    return Formatter(source, indent).format()


def check_formatted(source: str) -> bool:
    """O código já está no formato canônico?"""
    return format_source(source) == (source.rstrip("\n") + "\n")
