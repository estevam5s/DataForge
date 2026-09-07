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

        linhas_saida = []
        em_branco = 0
        no_topo = True

        for numero, bruta in enumerate(self.source.split("\n"), start=1):
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

    def _profundidade_por_linha(self):
        """Mapeia cada linha do arquivo ao seu nível de bloco.

        Levanta o erro do lexer quando o arquivo não tokeniza: um formatador
        não deve adivinhar a estrutura de um código com indentação ambígua.
        """
        tokens = Lexer(self.source).tokenize()

        profundidade = {}
        nivel = 0
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
                profundidade.setdefault(token.line, nivel)
                inicio_de_linha = False

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

        for token in tokens:
            if token.type in (TokenType.NEWLINE, TokenType.EOF,
                              TokenType.INDENT, TokenType.DEDENT):
                continue
            texto_token = self._render(token)
            if partes and self._precisa_espaco(anterior, token):
                partes.append(" ")
            partes.append(texto_token)
            anterior = token

        linha = "".join(partes)
        linha = re.sub(r"\s+([,;:])(?!=)", r"\1", linha)
        linha = re.sub(r"\(\s+", "(", linha)
        linha = re.sub(r"\s+\)", ")", linha)
        linha = re.sub(r"\[\s+", "[", linha)
        linha = re.sub(r"\s+\]", "]", linha)
        linha = re.sub(r"\{\s+", "{", linha)
        linha = re.sub(r"\s+\}", "}", linha)
        if comentario:
            linha = f"{linha}  {comentario}" if linha else comentario
        return linha.rstrip()

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
            corpo = corpo.replace("\n", "\\n").replace("\t", "\\t")
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
    def _precisa_espaco(anterior, atual):
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

        # Chamada: nome( sem espaço
        if b.type is TokenType.LPAREN and a.type in (
                TokenType.IDENTIFIER, TokenType.RPAREN, TokenType.RBRACKET):
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
            return True

        # Spread e unário grudam no operando
        if a.type is TokenType.SPREAD:
            return False
        if a.type is TokenType.AT:
            return False
        if b.type is TokenType.AT:
            return True

        if texto_a in BINARIOS or texto_b in BINARIOS:
            return True
        if texto_a in PALAVRAS_BINARIAS or texto_b in PALAVRAS_BINARIAS:
            return True
        if a.type is TokenType.COMMA:
            return True
        return True


def format_source(source: str, indent: str = INDENTACAO) -> str:
    """Formata um trecho de código DataForge."""
    return Formatter(source, indent).format()


def check_formatted(source: str) -> bool:
    """O código já está no formato canônico?"""
    return format_source(source) == (source.rstrip("\n") + "\n")
