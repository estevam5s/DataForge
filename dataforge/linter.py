"""
DataForge Linter — `dataforge lint`

Encontra o que compila mas provavelmente não é o que você quis dizer.
Não altera semântica e não repete o que o Type Checker já reporta: aqui moram
questões de higiene e estilo.

Regras
------
  unused-variable    variável atribuída e nunca lida
  unused-import      módulo importado com 'adopt' e nunca usado
  unused-parameter   parâmetro de ação nunca lido no corpo
  shadowed-name      nome local que esconde um de fora sem 'shadow'
  empty-block        bloco cujo corpo não faz nada
  magic-number       número solto repetido — provável constante
  long-action        ação com corpo muito longo
  deep-nesting       aninhamento profundo demais
  naming-convention  blueprint/record/enum fora de PascalCase, ação fora de snake_case
  redundant-else     'otherwise' depois de um ramo que sempre retorna
  double-negation    'not not x'
  comparison-to-bool x is yes / x is no
  todo-comment       comentário TODO/FIXME (informativo)
"""

import re

from . import ast_nodes as ast
from .typechecker import Diagnostic

LIMITE_LINHAS_ACAO = 60
LIMITE_ANINHAMENTO = 5
MIN_REPETICOES_MAGICAS = 5
NUMEROS_TOLERADOS = {0, 1, 2, 3, -1, -2, 10, 12, 24, 60, 100, 360, 1000}

# Métodos que o runtime chama pelo nome: a grafia é parte do contrato.
METODOS_ESPECIAIS = {
    "toString", "setup", "initiate",
    "add", "sub", "mul", "div", "mod", "pow", "floordiv",
}


class Linter:
    """Analisa estilo e higiene do código."""

    def __init__(self, filename="<stdin>", source="", ignorar=()):
        self.filename = filename
        self.source = source
        self.diagnostics = []
        self._profundidade = 0
        self._numeros = {}
        # Regras desligadas — vem de [lint] ignore no forge.toml.
        # Uma regra que nao serve ao projeto e pior que nenhuma: ensina
        # a ignorar a saida inteira.
        self.ignorar = set(ignorar or ())

    def warn(self, mensagem, node, hint="", code=""):
        if code and code in self.ignorar:
            return
        self.diagnostics.append(Diagnostic(
            'warning', mensagem, getattr(node, 'line', 0),
            getattr(node, 'column', 0), hint, code))

    # ── Entrada ────────────────────────────────────────────

    def lint(self, program):
        self._analisar_uso(program.body)
        self._checar_bloco(program.body, topo=True)
        for stmt in program.body:
            self._checar_expressoes(stmt)
        self._checar_numeros_magicos()
        self._checar_comentarios()
        return sorted(self.diagnostics, key=lambda d: (d.line, d.column))

    # ── Percurso ───────────────────────────────────────────

    def _checar_bloco(self, statements, topo=False, escopo_externo=None):
        """Percorre um bloco. A análise de uso acontece por ESCOPO, não por
        bloco: uma variável atribuída dentro de um 'given' pode muito bem ser
        lida depois, fora dele."""
        for stmt in statements:
            self._checar_statement(stmt, escopo_externo or set())

    def _analisar_uso(self, statements, rotulo=""):
        """Reporta atribuições e imports sem leitura dentro de um escopo.

        Um escopo é o topo do arquivo ou o corpo de uma ação: blocos aninhados
        (given, cycle, monitor) compartilham o escopo de quem os contém.
        """
        atribuidos = {}
        importados = {}
        lidos = set()

        def descer(nos):
            for node in nos:
                if node is None:
                    continue
                if isinstance(node, ast.Assignment) and isinstance(
                        node.target, ast.Identifier):
                    atribuidos.setdefault(node.target.name, node)
                elif isinstance(node, ast.AdoptStatement):
                    alias = node.alias or node.module.split('.')[-1]
                    importados[alias] = node
                elif isinstance(node, ast.DestructuringAssignment):
                    for nome, _ in node.targets:
                        atribuidos.setdefault(nome, node)

                # Uma ação aninhada abre seu próprio escopo, mas o que ela lê
                # conta como leitura aqui (closures).
                if isinstance(node, ast.ActionDeclaration):
                    self._coletar_leituras(node, lidos)
                    continue
                if isinstance(node, (ast.BlueprintDeclaration, ast.RecordDeclaration,
                                     ast.EnumDeclaration, ast.TraitDeclaration)):
                    self._coletar_leituras(node, lidos)
                    continue

                self._coletar_leituras(node, lidos)
                for corpo in self._blocos_de(node):
                    descer(corpo)

        descer(statements)

        for nome, node in atribuidos.items():
            if nome.startswith('_') or nome in lidos:
                continue
            self.warn(f"Variable '{nome}' is assigned but never read", node,
                      f"Remove it, or rename it to '_{nome}' to say it is on purpose",
                      "unused-variable")

        for alias, node in importados.items():
            if alias not in lidos:
                self.warn(f"Module '{node.module}' is imported but never used", node,
                          "Remove the 'adopt' line", "unused-import")

    @staticmethod
    def _blocos_de(node):
        """Os corpos de bloco que um nó carrega (sem entrar em ações)."""
        saida = []
        for atributo in ('body', 'else_body', 'handle_body', 'ensure_body',
                         'otherwise_body', 'default_body', 'blocks'):
            # 'handle_body' continua na lista pelo 'retry', que tem uma
            # clausula so; o 'monitor' guarda as suas em 'handles'.
            corpo = getattr(node, atributo, None)
            if isinstance(corpo, list) and corpo and isinstance(corpo[0], ast.ASTNode):
                saida.append(corpo)
        for clausula in getattr(node, 'handles', []) or []:
            saida.append(clausula.body)
        for _, corpo in getattr(node, 'orif_blocks', []) or []:
            saida.append(corpo)
        for caso in getattr(node, 'points', []) or []:
            saida.append(caso[1] if isinstance(caso, tuple) else caso.body)
        return saida

    def _checar_statement(self, node, nomes_externos):
        if node is None:
            return

        if isinstance(node, ast.ActionDeclaration):
            self._checar_acao(node, nomes_externos)
            return

        if isinstance(node, (ast.BlueprintDeclaration, ast.RecordDeclaration,
                             ast.EnumDeclaration, ast.TraitDeclaration)):
            self._checar_nome_de_tipo(node)
            # TraitDeclaration guarda os métodos numa lista; record e enum,
            # num vault; blueprint usa 'body'.
            corpo = getattr(node, 'body', None)
            if corpo is None:
                corpo = getattr(node, 'methods', [])
            if isinstance(corpo, dict):
                corpo = list(corpo.values())
            if not isinstance(corpo, list):
                corpo = []
            self._descer(corpo or [], nomes_externos)
            return

        if isinstance(node, ast.GivenBlock):
            self._checar_vazio(node.body, node, "given")
            sempre_retorna = self._sempre_encerra(node.body)
            self._descer(node.body, nomes_externos)
            for _, corpo in node.orif_blocks:
                self._checar_vazio(corpo, node, "orif")
                self._descer(corpo, nomes_externos)
            if node.otherwise_body:
                if sempre_retorna and not node.orif_blocks:
                    self.warn(
                        "The 'otherwise' is redundant: the 'given' branch always ends",
                        node,
                        "Unindent the 'otherwise' body — it runs anyway",
                        "redundant-else")
                self._descer(node.otherwise_body, nomes_externos)
            return

        for atributo in ('body', 'else_body', 'handle_body', 'ensure_body',
                         'otherwise_body', 'default_body', 'blocks'):
            # 'handle_body' continua na lista pelo 'retry', que tem uma
            # clausula so; o 'monitor' guarda as suas em 'handles'.
            corpo = getattr(node, atributo, None)
            if isinstance(corpo, list) and corpo and isinstance(corpo[0], ast.ASTNode):
                self._descer(corpo, nomes_externos)

        if isinstance(node, ast.MatchBlock):
            for caso in node.points:
                corpo = caso[1] if isinstance(caso, tuple) else caso.body
                self._checar_vazio(corpo, node, "point")
                self._descer(corpo, nomes_externos)

        if isinstance(node, (ast.CycleFromTo, ast.CycleIn, ast.PersistBlock,
                             ast.PerformBlock)):
            self._checar_vazio(node.body, node, "loop")

    def _descer(self, corpo, nomes_externos):
        self._profundidade += 1
        if self._profundidade == LIMITE_ANINHAMENTO and corpo:
            self.warn(
                f"Nesting is {LIMITE_ANINHAMENTO} levels deep here", corpo[0],
                "Pull the inner part into its own action", "deep-nesting")
        try:
            self._checar_bloco(corpo, escopo_externo=nomes_externos)
        finally:
            self._profundidade -= 1

    def _checar_acao(self, node, nomes_externos):
        # Uma ação sem corpo é uma assinatura (trait ou método abstrato):
        # nada aqui se aplica a ela.
        e_assinatura = not node.body

        if (node.name not in METODOS_ESPECIAIS
                and not re.fullmatch(r"[a-z_][a-z0-9_]*|<lambda>|<async>", node.name)):
            self.warn(
                f"Action '{node.name}' does not follow snake_case", node,
                f"Rename it to '{self._para_snake(node.name)}'", "naming-convention")

        if e_assinatura:
            return

        lidos = set()
        for stmt in node.body:
            self._coletar_leituras(stmt, lidos)

        for param in node.params:
            if param.startswith('_') or param in ('self', 'this'):
                continue
            if param not in lidos:
                self.warn(
                    f"Parameter '{param}' of action '{node.name}' is never used",
                    node,
                    f"Remove it, or rename it to '_{param}'", "unused-parameter")

        for param in node.params:
            if param in nomes_externos:
                self.warn(
                    f"Parameter '{param}' hides an outer name", node,
                    "Rename the parameter to avoid confusion", "shadowed-name")

        linhas = self._extensao(node)
        if linhas > LIMITE_LINHAS_ACAO:
            self.warn(
                f"Action '{node.name}' has {linhas} lines", node,
                f"Split it: actions above {LIMITE_LINHAS_ACAO} lines are hard to follow",
                "long-action")

        self._checar_vazio(node.body, node, f"action '{node.name}'")
        self._analisar_uso(node.body, node.name)
        internos = set(nomes_externos) | set(node.params)
        self._descer(node.body, internos)

    def _checar_nome_de_tipo(self, node):
        rotulo = type(node).__name__.replace('Declaration', '').lower()
        if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", node.name):
            self.warn(
                f"{rotulo.capitalize()} '{node.name}' does not follow PascalCase",
                node, f"Rename it to '{self._para_pascal(node.name)}'",
                "naming-convention")

    def _checar_vazio(self, corpo, node, rotulo):
        if corpo is not None and len(corpo) == 0:
            self.warn(f"Empty block in {rotulo}", node,
                      "Remove it, or add a comment saying why it is empty",
                      "empty-block")

    def _checar_expressoes(self, node, dentro_de_assert=False):
        """Varre a subárvore inteira procurando expressões suspeitas.

        Dentro de 'assert' as regras afrouxam: 'assert f(x) is yes' e valores
        literais são a forma normal de escrever uma expectativa.
        """
        if isinstance(node, ast.AssertStatement):
            dentro_de_assert = True
        for filho in self._filhos(node):
            if isinstance(filho, ast.NotOp) and isinstance(filho.operand, ast.NotOp):
                self.warn("Double negation: 'not not x'", filho,
                          "Drop both 'not' — the value is already boolean",
                          "double-negation")
            if (not dentro_de_assert and isinstance(filho, ast.ComparisonOp)
                    and filho.op in ('is', 'isnt')):
                for lado in (filho.left, filho.right):
                    if isinstance(lado, ast.BooleanLiteral):
                        forma = "yes" if lado.value else "no"
                        self.warn(
                            f"Comparing to '{forma}' is redundant", filho,
                            "Use the value directly (or 'not valor')",
                            "comparison-to-bool")
            if (not dentro_de_assert and isinstance(filho, ast.IntegerLiteral)
                    and filho.value not in NUMEROS_TOLERADOS):
                self._numeros.setdefault(filho.value, []).append(filho)
            self._checar_expressoes(filho, dentro_de_assert)

    def _checar_numeros_magicos(self):
        for valor, ocorrencias in self._numeros.items():
            if len(ocorrencias) >= MIN_REPETICOES_MAGICAS:
                self.warn(
                    f"The number {valor} appears {len(ocorrencias)} times", ocorrencias[0],
                    f"Name it: 'steady NOME := {valor}'", "magic-number")

    def _checar_comentarios(self):
        """Marcadores TODO/FIXME. Nao confundir com a palavra 'todo'.

        Em portugues, 'todo' e 'toda' abrem frases o tempo todo — "todo
        cache e uma aposta". Um marcador de verdade e escrito em
        MAIUSCULA, ou vem seguido de ':'. Exigir uma das duas coisas
        elimina o falso positivo sem deixar passar marcador real.
        """
        for numero, linha in enumerate(self.source.split("\n"), start=1):
            achado = re.search(
                r"(?://|#)\s*(TODO|FIXME|XXX|HACK)\b(:)?[ ]*(.*)", linha)
            if achado is None:
                # tolera minuscula so quando ha ':' logo depois
                achado = re.search(
                    r"(?://|#)\s*(todo|fixme|xxx|hack)(:)[ ]*(.*)",
                    linha, re.IGNORECASE)
            if achado:
                marca = achado.group(1).upper()
                resto = achado.group(3).strip()
                node = type('_N', (), {'line': numero, 'column': achado.start() + 1})()
                self.warn(f"{marca}: {resto}" if resto else f"{marca} comment", node,
                          "Track it in an issue, or resolve it", "todo-comment")

    # ── Utilidades ─────────────────────────────────────────

    @staticmethod
    def _filhos(node):
        if not isinstance(node, ast.ASTNode):
            return
        for campo, valor in vars(node).items():
            if campo in ('line', 'column'):
                continue
            if isinstance(valor, ast.ASTNode):
                yield valor
            elif isinstance(valor, list):
                for item in valor:
                    if isinstance(item, ast.ASTNode):
                        yield item
                    elif isinstance(item, tuple):
                        for sub in item:
                            if isinstance(sub, ast.ASTNode):
                                yield sub
            elif isinstance(valor, dict):
                for item in valor.values():
                    if isinstance(item, ast.ASTNode):
                        yield item

    def _coletar_leituras(self, node, destino):
        """Nomes lidos em qualquer lugar da subárvore."""
        if not isinstance(node, ast.ASTNode):
            return
        if isinstance(node, ast.Identifier):
            destino.add(node.name)
        if isinstance(node, ast.InterpolatedString):
            for tipo, conteudo in node.parts:
                if tipo == 'expr':
                    self._coletar_leituras(conteudo, destino)
                elif tipo == 'fmt':
                    # A parte com formato tambem le nomes. Sem isto, um
                    # 'adopt' usado so em '{M.pi():.2f}' seria acusado de
                    # nao usado — e falso alarme ensina a ignorar o lint
                    # inteiro.
                    self._coletar_leituras(conteudo[0], destino)
        if isinstance(node, (ast.SiftOperation, ast.MorphOperation,
                             ast.DistillOperation)):
            if getattr(node, 'func_ref', None):
                destino.add(node.func_ref)
        if isinstance(node, ast.MemberAccess) and isinstance(node.object, ast.Identifier):
            destino.add(node.object.name)
        # O alvo de uma atribuição simples não conta como leitura
        pular = None
        if isinstance(node, ast.Assignment) and isinstance(node.target, ast.Identifier):
            pular = node.target
        for filho in self._filhos(node):
            if filho is pular:
                continue
            self._coletar_leituras(filho, destino)

    @staticmethod
    def _sempre_encerra(corpo):
        return bool(corpo) and isinstance(
            corpo[-1], (ast.YieldStatement, ast.HaltStatement, ast.SkipStatement,
                        ast.TriggerStatement, ast.PropagateStatement))

    def _extensao(self, node):
        """Quantas linhas o corpo de uma acao ocupa.

        Nem todo no do AST tem linha preenchida — alguns nascem com 0.
        Um unico zero na conta puxava o minimo para o comeco do arquivo e
        transformava uma acao de duas linhas em 'has 197 lines'.
        """
        linhas = []

        def descer(n):
            linha = getattr(n, 'line', 0)
            if linha:
                linhas.append(linha)
            for filho in self._filhos(n):
                descer(filho)

        inicio = getattr(node, 'line', 0)
        if inicio:
            linhas.append(inicio)
        for stmt in node.body:
            descer(stmt)

        if not linhas:
            return 0
        return max(linhas) - min(linhas) + 1

    @staticmethod
    def _para_snake(nome):
        s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', nome)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()

    @staticmethod
    def _para_pascal(nome):
        return ''.join(p.capitalize() for p in re.split(r'[_\-\s]+', nome) if p)


#: Todas as regras, para validar o que se pede em [lint] ignore.
REGRAS = {
    "unused-variable", "unused-import", "unused-parameter", "shadowed-name",
    "empty-block", "magic-number", "long-action", "deep-nesting",
    "naming-convention", "redundant-else", "double-negation",
    "comparison-to-bool", "todo-comment",
}


def lint_program(program, filename="<stdin>", source="", ignorar=()):
    """Analisa estilo e higiene, devolvendo os avisos encontrados.

    'ignorar' desliga regras pelo nome — o que o forge.toml declara em
    [lint] ignore.
    """
    return Linter(filename, source, ignorar).lint(program)
