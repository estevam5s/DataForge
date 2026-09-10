"""
Analise de complexidade — o Big-O do codigo, sem rodar o codigo.

    dataforge big-o programa.df

    action buscar(xs, alvo):        O(n)        tempo    O(1) espaco
    action ordenar_e_par(xs):       O(n log n)  tempo    O(n) espaco
    action fib(n):                  O(2^n)      tempo    O(n) espaco   ⚠

─── O que esta analise e, e o que ela nao e ────────────────

Ela le a arvore e conta estrutura: quantos lacos aninhados, se o
contador dobra ou soma, quantas vezes uma acao chama a si mesma, e
quanto custa cada funcao embutida que aparece. Com isso acerta a
esmagadora maioria do codigo que se escreve no dia a dia.

O que ela **nao** faz, e nao promete fazer:

  - decidir o indecidivel. Saber se um laco termina e o problema da
    parada; quando a analise nao consegue provar, ela diz 'O(?)' em vez
    de inventar um numero.
  - seguir valor. 'cycle i from 1 to k' e O(k); se 'k' vier de fora, a
    analise usa 'k' como simbolo em vez de fingir que e constante.
  - medir constante. O(n) com constante 1000 perde de O(n²) com
    constante 1 ate n=1000. Big-O e sobre crescimento, nao sobre
    velocidade — e um relatorio que sugere o contrario ensina errado.

E por isso que o relatorio traz o **porque** junto da classe: 'O(n²)
— dois lacos aninhados, linhas 4 e 5'. Uma letra sozinha nao ajuda
ninguem a melhorar nada.
"""

from . import ast_nodes as ast


# ═════════════════════════════════════════════════════════════
#  A algebra das classes
# ═════════════════════════════════════════════════════════════
#
# Uma complexidade e representada por um par (grau_polinomial,
# grau_logaritmico) mais uma marca para o que foge disso —
# exponencial, fatorial, desconhecido.
#
# Somar dois trechos e ficar com o maior; aninhar e multiplicar. Com o
# par isso vira aritmetica simples: n * n log n = n² log n vira
# (1,0) + (1,1) = (2,1).

CONSTANTE = "constante"
POLINOMIAL = "polinomial"
EXPONENCIAL = "exponencial"
FATORIAL = "fatorial"
DESCONHECIDO = "desconhecido"


class Ordem:
    """Uma classe de complexidade, com o motivo pelo qual ela e essa.

    O motivo importa tanto quanto a classe. 'O(n²)' nao diz o que
    fazer; 'O(n²) — dois lacos aninhados nas linhas 4 e 7' diz.
    """

    __slots__ = ("familia", "n", "log", "base", "motivos")

    def __init__(self, familia=CONSTANTE, n=0, log=0, base=2, motivos=None):
        self.familia = familia
        self.n = n              # grau polinomial: 1 = n, 2 = n², …
        self.log = log          # quantos fatores log n
        self.base = base        # base da exponencial, quando for o caso
        self.motivos = list(motivos or [])

    # ── construtores ────────────────────────────────────────

    @staticmethod
    def constante(motivo=""):
        return Ordem(CONSTANTE, 0, 0, motivos=[motivo] if motivo else [])

    @staticmethod
    def logaritmica(motivo=""):
        return Ordem(POLINOMIAL, 0, 1, motivos=[motivo] if motivo else [])

    @staticmethod
    def linear(motivo=""):
        return Ordem(POLINOMIAL, 1, 0, motivos=[motivo] if motivo else [])

    @staticmethod
    def linearitmica(motivo=""):
        return Ordem(POLINOMIAL, 1, 1, motivos=[motivo] if motivo else [])

    @staticmethod
    def quadratica(motivo=""):
        return Ordem(POLINOMIAL, 2, 0, motivos=[motivo] if motivo else [])

    @staticmethod
    def exponencial(base=2, motivo=""):
        return Ordem(EXPONENCIAL, 0, 0, base, [motivo] if motivo else [])

    @staticmethod
    def fatorial(motivo=""):
        return Ordem(FATORIAL, 0, 0, motivos=[motivo] if motivo else [])

    @staticmethod
    def desconhecida(motivo=""):
        return Ordem(DESCONHECIDO, 0, 0, motivos=[motivo] if motivo else [])

    # ── combinacao ──────────────────────────────────────────

    def maior(self, outra):
        """Dois trechos em sequencia: vale o maior dos dois.

        E o passo que descarta termos menores: O(n) seguido de O(n²) e
        O(n²), porque para n grande o primeiro some ao lado do segundo.
        """
        if self._peso() >= outra._peso():
            vencedora = Ordem(self.familia, self.n, self.log, self.base,
                              self.motivos)
            if outra._peso() == self._peso():
                vencedora.motivos = self.motivos + [
                    m for m in outra.motivos if m not in self.motivos]
            return vencedora
        return Ordem(outra.familia, outra.n, outra.log, outra.base,
                     outra.motivos)

    def vezes(self, outra):
        """Um trecho DENTRO de outro: os custos multiplicam.

        Um laco linear com corpo linear e quadratico. E a unica regra
        que produz O(n²), e por isso a mensagem sempre aponta os dois
        lacos, e nao so o de fora.
        """
        if DESCONHECIDO in (self.familia, outra.familia):
            return Ordem(DESCONHECIDO, motivos=self.motivos + outra.motivos)
        if FATORIAL in (self.familia, outra.familia):
            return Ordem(FATORIAL, motivos=self.motivos + outra.motivos)
        if EXPONENCIAL in (self.familia, outra.familia):
            base = max(self.base if self.familia == EXPONENCIAL else 0,
                       outra.base if outra.familia == EXPONENCIAL else 0)
            return Ordem(EXPONENCIAL, 0, 0, base or 2,
                         self.motivos + outra.motivos)

        combinados = self.motivos + [m for m in outra.motivos
                                     if m not in self.motivos]
        soma_n = self.n + outra.n
        soma_log = self.log + outra.log
        if soma_n == 0 and soma_log == 0:
            return Ordem(CONSTANTE, 0, 0, motivos=combinados)
        return Ordem(POLINOMIAL, soma_n, soma_log, motivos=combinados)

    def _peso(self):
        """Uma ordem total, para 'maior' saber quem vence."""
        if self.familia == DESCONHECIDO:
            return 10_000
        if self.familia == FATORIAL:
            return 9_000
        if self.familia == EXPONENCIAL:
            return 8_000 + self.base
        return self.n * 10 + self.log

    # ── apresentacao ────────────────────────────────────────

    def texto(self):
        if self.familia == DESCONHECIDO:
            return "O(?)"
        if self.familia == FATORIAL:
            return "O(n!)"
        if self.familia == EXPONENCIAL:
            return f"O({self.base}^n)"
        if self.n == 0 and self.log == 0:
            return "O(1)"

        partes = []
        if self.n == 1:
            partes.append("n")
        elif self.n > 1:
            partes.append(f"n^{self.n}")
        if self.log == 1:
            partes.append("log n")
        elif self.log > 1:
            partes.append(f"log^{self.log} n")
        return "O(" + " ".join(partes) + ")"

    def nome(self):
        """O nome que se usa ao falar, e nao a notacao."""
        return {
            "O(1)": "constante",
            "O(log n)": "logaritmica",
            "O(n)": "linear",
            "O(n log n)": "linearitmica",
            "O(n^2)": "quadratica",
            "O(n^3)": "cubica",
            "O(2^n)": "exponencial",
            "O(n!)": "fatorial",
            "O(?)": "indeterminada",
        }.get(self.texto(), "polinomial")

    def gravidade(self):
        """0 otimo, 1 aceitavel, 2 cuidado, 3 problema.

        E o que decide a cor no editor. A fronteira entre 1 e 2 e o
        quadratico: ate n log n, dobrar a entrada mais que dobra o
        tempo mas nao explode; a partir de n², dobrar a entrada
        quadruplica.
        """
        peso = self._peso()
        if peso <= 1:
            return 0
        if peso <= 11:
            return 1
        if peso < 8_000:
            return 2
        return 3

    def __repr__(self):
        return f"<{self.texto()}>"

    def para_vault(self):
        return {
            "notacao": self.texto(),
            "nome": self.nome(),
            "familia": self.familia,
            "grau": self.n,
            "logs": self.log,
            "gravidade": self.gravidade(),
            "motivos": list(self.motivos),
        }


# ═════════════════════════════════════════════════════════════
#  Custo das funcoes embutidas
# ═════════════════════════════════════════════════════════════
#
# Uma chamada nao e gratis so por ser uma linha. 'sorted(xs)' dentro de
# um laco e o jeito mais comum de escrever um O(n² log n) sem
# perceber — o laco esta a vista, o custo do sorted nao.

CUSTOS = {
    # constantes
    #
    # 'str' esta aqui, e nao entre as lineares, de proposito. Ele e
    # O(tamanho do valor) — mas 'tamanho do valor' nao e o 'n' do
    # algoritmo. Trata-lo como linear fazia TODO laco com 'str(x)'
    # dentro virar quadratico, inclusive o jeito certo de montar um
    # indice de vault:
    #
    #     cycle y in ys:
    #         indice[str(y)] := yes      <- isto e O(n), nao O(n^2)
    "len": (0, 0), "abs": (0, 0), "int": (0, 0), "float": (0, 0),
    "str": (0, 0), "repr": (0, 0),
    "bool": (0, 0), "type": (0, 0), "round": (0, 0), "chr": (0, 0),
    "ord": (0, 0), "hex": (0, 0), "bin": (0, 0), "pow": (0, 0),
    "sqrt": (0, 0), "floor": (0, 0), "ceil": (0, 0), "random": (0, 0),

    # lineares
    "sum": (1, 0), "min": (1, 0), "max": (1, 0), "reversed": (1, 0),
    "count": (1, 0), "index": (1, 0), "join": (1, 0), "split": (1, 0),
    "map": (1, 0), "filter": (1, 0), "reduce": (1, 0), "any": (1, 0),
    "all": (1, 0), "range": (1, 0), "list": (1, 0), "cluster": (1, 0),
    "flatten": (1, 0), "unique": (1, 0), "replace": (1, 0),
    "enumerate": (1, 0), "zip": (1, 0),

    # n log n
    "sorted": (1, 1), "sort": (1, 1), "sort_by": (1, 1),
    "sort_by_field": (1, 1), "ordenar": (1, 1),
}

#: Metodos, pelo nome, quando chamados sobre um valor.
CUSTOS_METODO = {
    "sort": (1, 1), "sorted": (1, 1),
    "reverse": (1, 0), "reversed": (1, 0), "copy": (1, 0),
    "unique": (1, 0), "flatten": (1, 0), "index_of": (1, 0),
    "contains": (1, 0), "includes": (1, 0), "count": (1, 0),
    "map": (1, 0), "filter": (1, 0), "reduce": (1, 0),
    "join": (1, 0), "sum": (1, 0), "min": (1, 0), "max": (1, 0),
    "mean": (1, 0), "tally": (1, 0), "group_by": (1, 0),
    "append": (0, 0), "push": (0, 0), "pop": (0, 0), "last": (0, 0),
    "first": (0, 0), "length": (0, 0), "get": (0, 0), "has": (0, 0),
    "keys": (1, 0), "values": (1, 0), "items": (1, 0),
    # os do vault sao O(1) — e a razao de trocar 'in cluster' por
    # 'in vault' derrubar um O(n²) para O(n)
}


# ═════════════════════════════════════════════════════════════
#  A analise
# ═════════════════════════════════════════════════════════════

class Analise:
    """O resultado para uma acao."""

    def __init__(self, nome, linha=0, tipo="action"):
        self.nome = nome
        self.linha = linha
        self.tipo = tipo
        self.tempo = Ordem.constante()
        self.espaco = Ordem.constante()
        self.recursiva = False
        self.chamadas_proprias = 0
        self.avisos = []
        self.lacos = []

    def para_vault(self):
        return {
            "nome": self.nome,
            "linha": self.linha,
            "tipo": self.tipo,
            "tempo": self.tempo.para_vault(),
            "espaco": self.espaco.para_vault(),
            "recursiva": self.recursiva,
            "avisos": list(self.avisos),
        }


class Analisador:
    """Percorre a arvore somando e multiplicando ordens."""

    def __init__(self, fonte=""):
        self.fonte = fonte
        self.acoes = {}          # nome -> ActionDeclaration
        self.resultados = []
        self.atual = None

    # ── entrada ─────────────────────────────────────────────

    def analisar(self, programa):
        """Devolve uma lista de Analise, uma por acao e metodo."""
        self._coletar(programa.body)

        for nome, no in self.acoes.items():
            self.resultados.append(self._analisar_acao(nome, no))

        # O corpo solto do arquivo tambem tem custo — e frequentemente
        # e onde mora o laco que trava tudo.
        soltas = [s for s in programa.body
                  if not isinstance(s, (ast.ActionDeclaration,
                                        ast.BlueprintDeclaration,
                                        ast.RecordDeclaration,
                                        ast.TraitDeclaration,
                                        ast.EnumDeclaration,
                                        ast.AdoptStatement))]
        if soltas:
            topo = Analise("<arquivo>", 1, "programa")
            self.atual = topo
            topo.tempo = self._bloco(soltas)
            topo.espaco = self._espaco_do_bloco(soltas)
            self.resultados.append(topo)

        return self.resultados

    def _coletar(self, corpo, prefixo=""):
        """Indexa as acoes, para a analise de recursao saber quem e quem."""
        for no in corpo:
            if isinstance(no, ast.ActionDeclaration):
                self.acoes[prefixo + no.name] = no
            elif isinstance(no, ast.BlueprintDeclaration):
                for metodo in self._metodos_de(no):
                    if isinstance(metodo, ast.ActionDeclaration):
                        self.acoes[f"{no.name}.{metodo.name}"] = metodo
            elif isinstance(no, ast.RecordDeclaration):
                for metodo in self._metodos_de(no):
                    if isinstance(metodo, ast.ActionDeclaration):
                        self.acoes[f"{no.name}.{metodo.name}"] = metodo

    @staticmethod
    def _metodos_de(no):
        """Os metodos de um blueprint ou record, venham de onde vierem."""
        for campo in ("methods", "body", "members"):
            valor = getattr(no, campo, None)
            if isinstance(valor, list):
                for item in valor:
                    if isinstance(item, ast.ActionDeclaration):
                        yield item
            elif isinstance(valor, dict):
                for item in valor.values():
                    if isinstance(item, ast.ActionDeclaration):
                        yield item

    # ── uma acao ────────────────────────────────────────────

    def _analisar_acao(self, nome, no):
        curto = nome.split(".")[-1]
        resultado = Analise(nome, getattr(no, "line", 0),
                            "stream action"
                            if getattr(no, "is_generator", False)
                            else "action")
        self.atual = resultado

        resultado.chamadas_proprias = self._contar_chamadas(no.body, curto)
        resultado.recursiva = resultado.chamadas_proprias > 0

        if resultado.tipo == "stream action":
            # Um generator nao tem custo total: ele tem custo POR ITEM
            # emitido. 'persist yes' com 'emit' dentro nao e um laco
            # infinito por engano — e a forma de escrever uma sequencia
            # preguicosa, e quem consome decide quantos itens quer.
            #
            # Analisar o corpo inteiro daria O(?) para todo generator
            # infinito da linguagem, que sao exatamente os corretos.
            resultado.tempo = self._custo_por_item(no.body)
            resultado.tempo.motivos.insert(
                0, "generator: o custo e por item emitido, nao pelo total")
            resultado.espaco = self._espaco_do_bloco(no.body)
            self._avisar(resultado)
            return resultado

        corpo = self._bloco(no.body)

        if resultado.recursiva:
            corpo = self._com_recursao(no, corpo, resultado, curto)

        resultado.tempo = corpo
        resultado.espaco = self._espaco_do_bloco(no.body)
        if resultado.recursiva and resultado.espaco.familia == CONSTANTE:
            # Cada chamada recursiva ocupa um quadro de pilha; mesmo sem
            # alocar nada, a profundidade e memoria.
            resultado.espaco = Ordem.linear(
                "a pilha cresce com a profundidade da recursao")

        self._avisar(resultado)
        return resultado

    def _custo_por_item(self, corpo):
        """O custo de produzir UM item de um generator.

        O laco que envolve os 'emit' nao entra na conta: ele e o que
        gera a sequencia, e a sequencia e preguicosa. O que conta e o
        trabalho entre um 'emit' e o proximo.
        """
        interno = []
        for no in corpo or []:
            if isinstance(no, (ast.PersistBlock, ast.PerformBlock,
                               ast.CycleFromTo, ast.CycleIn)):
                if any(isinstance(x, ast.EmitStatement)
                       for x in self._andar(no.body)):
                    interno.extend(no.body)
                    continue
            interno.append(no)
        return self._bloco(interno)

    def _com_recursao(self, no, corpo, resultado, curto):
        """A ordem de uma acao que chama a si mesma.

        Tres casos cobrem quase tudo o que se escreve:

            uma chamada, argumento diminui de 1     O(n)
            uma chamada, argumento pela metade      O(log n)
            duas ou mais chamadas                   O(2^n)

        E o caso que vale destacar: duas chamadas sobre METADE cada
        (divisao e conquista) nao e exponencial — e O(n log n) quando
        o trabalho fora da recursao e linear. E a diferenca entre o
        merge sort e o fibonacci ingenuo, que sao identicos em forma.
        """
        divide = self._divide_pela_metade(no.body, curto)

        if resultado.chamadas_proprias >= 2:
            if divide:
                # Divisao e conquista: o custo e o trabalho por nivel
                # vezes log n niveis.
                fora = corpo.maior(Ordem.constante())
                combinada = fora.vezes(Ordem.logaritmica(
                    f"'{curto}' se divide ao meio: log n niveis"))
                combinada.motivos.insert(
                    0, f"divisao e conquista: {resultado.chamadas_proprias} "
                       f"chamadas sobre metade cada")
                return combinada
            return Ordem.exponencial(
                resultado.chamadas_proprias,
                f"'{curto}' chama a si mesma {resultado.chamadas_proprias} "
                f"vezes por nivel, sem dividir a entrada")

        if divide:
            return corpo.maior(Ordem.constante()).vezes(Ordem.logaritmica(
                f"'{curto}' recorre sobre metade da entrada"))

        return corpo.maior(Ordem.constante()).vezes(Ordem.linear(
            f"'{curto}' recorre {resultado.chamadas_proprias}x, diminuindo a "
            f"entrada de um em um"))

    # ── blocos e instrucoes ─────────────────────────────────

    def _bloco(self, corpo):
        """A ordem de uma sequencia: o maior dos termos."""
        total = Ordem.constante()
        for no in corpo or []:
            total = total.maior(self._instrucao(no))
        return total

    def _instrucao(self, no):
        if no is None:
            return Ordem.constante()

        # ── lacos ──
        if isinstance(no, ast.CycleFromTo):
            return self._laco_contado(no)
        if isinstance(no, ast.CycleIn):
            return self._laco_sobre(no)
        if isinstance(no, (ast.PersistBlock, ast.PerformBlock)):
            return self._laco_condicional(no)

        # ── ramificacao: vale o pior ramo ──
        if isinstance(no, ast.GivenBlock):
            pior = self._expressao(no.condition).maior(self._bloco(no.body))
            for ramo in getattr(no, "orif_blocks", []) or []:
                cond = ramo[0] if isinstance(ramo, (list, tuple)) else \
                    getattr(ramo, "condition", None)
                corpo = ramo[1] if isinstance(ramo, (list, tuple)) else \
                    getattr(ramo, "body", [])
                pior = pior.maior(self._expressao(cond)).maior(self._bloco(corpo))
            if getattr(no, "otherwise_body", None):
                pior = pior.maior(self._bloco(no.otherwise_body))
            return pior

        if isinstance(no, ast.MatchBlock):
            pior = self._expressao(no.expression)
            for caso in getattr(no, "points", []) or []:
                pior = pior.maior(self._bloco(getattr(caso, "body", [])))
            return pior.maior(self._bloco(getattr(no, "default_body", [])))

        if isinstance(no, ast.MonitorBlock):
            pior = self._bloco(no.body)
            pior = pior.maior(self._bloco(getattr(no, "handle_body", [])))
            for clausula in getattr(no, "handles", []) or []:
                pior = pior.maior(self._bloco(clausula.body))
            return pior.maior(self._bloco(getattr(no, "ensure_body", [])))

        if isinstance(no, ast.RetryBlock):
            # Tentar n vezes multiplica o custo por uma constante, nao
            # muda a classe — a menos que o numero de tentativas venha
            # de uma variavel.
            return self._bloco(no.body)

        # ── declaracoes aninhadas ──
        if isinstance(no, (ast.BlueprintDeclaration, ast.RecordDeclaration,
                           ast.TraitDeclaration, ast.EnumDeclaration,
                           ast.ActionDeclaration)):
            return Ordem.constante()

        # ── as que carregam expressao ──
        for campo in ("value", "expression", "condition", "subject", "count"):
            valor = getattr(no, campo, None)
            if valor is not None and hasattr(valor, "line"):
                return self._expressao(valor)

        if isinstance(no, ast.OutStatement):
            total = Ordem.constante()
            for v in getattr(no, "expressions", []) or []:
                total = total.maior(self._expressao(v))
            return total

        if isinstance(no, ast.Assignment):
            alvo = self._expressao(getattr(no, "target", None))
            return alvo.maior(self._expressao(getattr(no, "value", None)))

        return Ordem.constante()

    # ── lacos ───────────────────────────────────────────────

    def _laco_contado(self, no):
        """'cycle i from a to b [step s]'.

        O passo decide: somar da laco linear, multiplicar da
        logaritmico. E a diferenca entre percorrer e buscar por
        bisseccao, e ela cabe num operador.
        """
        linha = getattr(no, "line", 0)
        limite = self._texto_de(no.end)
        constante = self._e_constante(no.start) and self._e_constante(no.end)

        if constante:
            ordem = Ordem.constante(
                f"laco de tamanho fixo na linha {linha}")
        else:
            ordem = Ordem.linear(
                f"'cycle … to {limite}' na linha {linha} anda uma vez por item")
            if self.atual:
                self.atual.lacos.append((linha, "linear"))

        corpo = self._bloco(no.body)
        return ordem.vezes(corpo) if corpo._peso() else ordem

    def _laco_sobre(self, no):
        """'cycle x in colecao' — uma volta por item."""
        linha = getattr(no, "line", 0)
        fonte = self._texto_de(no.collection)
        ordem = Ordem.linear(
            f"'cycle … in {fonte}' na linha {linha} anda uma vez por item")
        if self.atual:
            self.atual.lacos.append((linha, "linear"))

        custo_fonte = self._expressao(no.collection)
        corpo = self._bloco(no.body)
        return ordem.vezes(corpo).maior(custo_fonte)

    def _laco_condicional(self, no):
        """'persist cond' — o corpo decide se e linear ou logaritmico.

        Um contador que se divide ao meio ('n := n ~/ 2') termina em
        log n voltas; um que diminui de um em um leva n. Detectar isso
        e o que separa a busca binaria da linear no relatorio.
        """
        linha = getattr(no, "line", 0)
        corpo = self._bloco(no.body)

        if self._corpo_divide(no.body):
            ordem = Ordem.logaritmica(
                f"'persist' na linha {linha}: a variavel se divide a cada "
                f"volta, entao sao log n voltas")
        elif self._corpo_avanca(no.body):
            ordem = Ordem.linear(
                f"'persist' na linha {linha} avanca de um em um")
            if self.atual:
                self.atual.lacos.append((linha, "linear"))
        else:
            ordem = Ordem.desconhecida(
                f"'persist' na linha {linha}: nada no corpo mexe na "
                f"condicao de forma que a analise reconheca")

        return ordem.vezes(corpo) if corpo._peso() else ordem

    # ── expressoes ──────────────────────────────────────────

    def _expressao(self, no):
        if no is None:
            return Ordem.constante()

        if isinstance(no, ast.FunctionCall):
            return self._chamada(no)
        if isinstance(no, (ast.MethodCall, ast.SafeMethodCall)):
            return self._metodo(no)

        if isinstance(no, (ast.ListComprehension, ast.VaultComprehension)):
            return self._compreensao(no)

        if isinstance(no, ast.PipelineExpression):
            # Cada estagio percorre a colecao uma vez.
            base = Ordem.linear(
                f"pipeline na linha {getattr(no, 'line', 0)}: cada estagio "
                f"percorre a colecao")
            return base.maior(self._expressao(no.source))

        if isinstance(no, ast.MembershipOp):
            # 'x in cluster' e O(n); 'x in vault' e O(1). Sem saber o
            # tipo, o caso ruim e o que vale — e e ele que costuma
            # transformar um laco linear em quadratico.
            return Ordem.linear(
                f"'in' na linha {getattr(no, 'line', 0)} percorre a colecao "
                f"(use um vault para O(1))")

        if isinstance(no, ast.SliceAccess):
            return Ordem.linear(
                f"fatia na linha {getattr(no, 'line', 0)} copia os itens")

        if isinstance(no, ast.ListLiteral):
            total = Ordem.constante()
            for item in no.elements or []:
                if isinstance(item, ast.SpreadElement):
                    total = total.maior(Ordem.linear("'...' copia a colecao"))
                total = total.maior(self._expressao(item))
            return total

        # Percorre os filhos e fica com o maior.
        total = Ordem.constante()
        for campo in ("left", "right", "operand", "object", "index", "value",
                      "condition", "then_expr", "else_expr", "source",
                      "callee", "start", "end"):
            filho = getattr(no, campo, None)
            if filho is not None and hasattr(filho, "line"):
                total = total.maior(self._expressao(filho))
        for campo in ("args", "elements", "expressions", "operations",
                      "parts"):
            for filho in getattr(no, campo, []) or []:
                if hasattr(filho, "line"):
                    total = total.maior(self._expressao(filho))
        return total

    def _chamada(self, no):
        nome = getattr(no.callee, "name", "")
        base = Ordem.constante()
        for arg in no.args or []:
            base = base.maior(self._expressao(arg))

        if nome in CUSTOS:
            n, log = CUSTOS[nome]
            if n or log:
                custo = Ordem(POLINOMIAL, n, log, motivos=[
                    f"'{nome}()' na linha {getattr(no, 'line', 0)} custa "
                    f"{Ordem(POLINOMIAL, n, log).texto()}"])
                return base.maior(custo)
            return base

        # Chamada a outra acao do arquivo: usa a ordem dela.
        if nome in self.acoes and self.atual and nome != self.atual.nome:
            interna = self._ordem_conhecida(nome)
            if interna is not None:
                return base.maior(interna)
        return base

    def _metodo(self, no):
        base = self._expressao(getattr(no, "object", None))
        for arg in getattr(no, "args", []) or []:
            base = base.maior(self._expressao(arg))

        metodo = getattr(no, "method", "")
        if metodo in CUSTOS_METODO:
            n, log = CUSTOS_METODO[metodo]
            if n or log:
                custo = Ordem(POLINOMIAL, n, log, motivos=[
                    f"'.{metodo}()' na linha {getattr(no, 'line', 0)} custa "
                    f"{Ordem(POLINOMIAL, n, log).texto()}"])
                return base.maior(custo)
        return base

    def _compreensao(self, no):
        """'[x cycle x in xs]' e um laco escrito de outro jeito.

        Compreensao aninhada e o O(n²) mais facil de nao ver: ela cabe
        numa linha, e a linha nao parece um laco duplo.
        """
        linha = getattr(no, "line", 0)
        clausulas = getattr(no, "clauses", None) or []
        if not clausulas and hasattr(no, "clause"):
            clausulas = [no.clause]

        ordem = Ordem.constante()
        for i, clausula in enumerate(clausulas):
            fonte = self._texto_de(getattr(clausula, "source", None))
            uma = Ordem.linear(
                f"compreensao na linha {linha} percorre {fonte}"
                + (" (aninhada)" if i else ""))
            ordem = ordem.vezes(uma) if i else uma
            condicao = getattr(clausula, "condition", None)
            if condicao is not None:
                ordem = ordem.vezes(self._expressao(condicao).maior(
                    Ordem.constante()))

        corpo = self._expressao(getattr(no, "expression", None)
                                or getattr(no, "value", None))
        return ordem.vezes(corpo) if corpo._peso() else ordem

    # ── espaco ──────────────────────────────────────────────

    def _espaco_do_bloco(self, corpo, dentro_de_laco=False):
        """Quanta memoria a mais o codigo pede.

        A regra que importa: uma colecao que cresce dentro de um laco e
        O(n); uma variavel reatribuida nao e. Distinguir as duas e a
        diferenca entre um algoritmo no lugar e um que copia tudo.
        """
        total = Ordem.constante()
        for no in corpo or []:
            if isinstance(no, (ast.CycleFromTo, ast.CycleIn,
                               ast.PersistBlock, ast.PerformBlock)):
                interno = self._espaco_do_bloco(no.body, True)
                if self._acumula(no.body):
                    interno = interno.maior(Ordem.linear(
                        f"o laco da linha {getattr(no, 'line', 0)} acumula "
                        f"numa colecao"))
                total = total.maior(interno)
            elif isinstance(no, ast.GivenBlock):
                total = total.maior(self._espaco_do_bloco(
                    no.body, dentro_de_laco))
                if getattr(no, "otherwise_body", None):
                    total = total.maior(self._espaco_do_bloco(
                        no.otherwise_body, dentro_de_laco))
            elif isinstance(no, ast.Assignment):
                valor = getattr(no, "value", None)
                if isinstance(valor, (ast.ListComprehension,
                                      ast.VaultComprehension,
                                      ast.PipelineExpression)):
                    total = total.maior(Ordem.linear(
                        f"a colecao criada na linha {getattr(no, 'line', 0)} "
                        f"cresce com a entrada"))
                elif isinstance(valor, ast.SliceAccess):
                    total = total.maior(Ordem.linear(
                        f"a fatia da linha {getattr(no, 'line', 0)} e uma copia"))
                elif isinstance(valor, ast.FunctionCall):
                    nome = getattr(valor.callee, "name", "")
                    if nome in ("sorted", "list", "cluster", "reversed",
                                "map", "filter", "range"):
                        total = total.maior(Ordem.linear(
                            f"'{nome}()' na linha {getattr(no, 'line', 0)} "
                            f"cria uma colecao nova"))
        return total

    # ── deteccao estrutural ─────────────────────────────────

    @staticmethod
    def _e_constante(no):
        return isinstance(no, (ast.IntegerLiteral, ast.FloatLiteral))

    def _texto_de(self, no):
        """Um rotulo curto para a expressao, para a mensagem."""
        if no is None:
            return "a colecao"
        if isinstance(no, ast.Identifier):
            return f"'{no.name}'"
        if isinstance(no, ast.IntegerLiteral):
            return str(no.value)
        if isinstance(no, ast.FunctionCall):
            return f"'{getattr(no.callee, 'name', '?')}()'"
        if isinstance(no, ast.MemberAccess):
            return f"'{self._texto_de(no.object)}.{no.member}'".replace("''", "'")
        return "a colecao"

    def _contar_chamadas(self, corpo, nome):
        """Quantas vezes o corpo chama a acao pelo proprio nome."""
        contagem = 0
        for no in self._andar(corpo):
            if isinstance(no, ast.FunctionCall) and \
                    getattr(no.callee, "name", "") == nome:
                contagem += 1
            elif isinstance(no, ast.MethodCall) and no.method == nome:
                contagem += 1
        return contagem

    def _divide_pela_metade(self, corpo, nome):
        """A recursao passa metade da entrada adiante?

        E o que separa O(log n) de O(n), e O(n log n) de O(2^n). A
        marca e um '~/ 2', '/ 2' ou uma fatia no argumento da chamada.
        """
        for no in self._andar(corpo):
            chamada = None
            if isinstance(no, ast.FunctionCall) and \
                    getattr(no.callee, "name", "") == nome:
                chamada = no
            elif isinstance(no, ast.MethodCall) and no.method == nome:
                chamada = no
            if chamada is None:
                continue
            for arg in chamada.args or []:
                if self._e_metade(arg):
                    return True
        return False

    def _e_metade(self, no):
        if isinstance(no, ast.SliceAccess):
            return True
        if isinstance(no, ast.BinaryOp) and no.op in ("//", "~/", "/"):
            direita = no.right
            if isinstance(direita, ast.IntegerLiteral) and direita.value >= 2:
                return True
        # 'meio' e 'metade' como nome ja indicam bisseccao; a heuristica
        # e fraca de proposito — so confirma o que a forma sugere.
        for campo in ("left", "right", "value"):
            filho = getattr(no, campo, None)
            if filho is not None and hasattr(filho, "line") and \
                    self._e_metade(filho):
                return True
        return False

    def _corpo_divide(self, corpo):
        """O corpo divide alguma variavel ao meio a cada volta?"""
        for no in self._andar(corpo):
            if isinstance(no, ast.Assignment):
                valor = getattr(no, "value", None)
                operador = getattr(no, "compound_op", "") or ""
                if operador in ("/", "~/", "//"):
                    return True
                if isinstance(valor, ast.BinaryOp) and \
                        valor.op in ("/", "~/", "//") and \
                        isinstance(valor.right, ast.IntegerLiteral) and \
                        valor.right.value >= 2:
                    return True
        return False

    def _corpo_avanca(self, corpo):
        """O corpo mexe em alguma variavel de forma que a condicao veja?

        'a, b := b, a + b' conta: e desestruturacao, nao Assignment, e
        sem ela todo laco escrito assim caia em O(?). Um 'halt' tambem
        conta — e uma saida, ainda que a condicao nunca mude.
        """
        for no in self._andar(corpo):
            if isinstance(no, ast.Assignment):
                operador = getattr(no, "compound_op", "") or ""
                if operador in ("+", "-", "*") or not operador:
                    return True
            if isinstance(no, (ast.DestructuringAssignment, ast.HaltStatement,
                               ast.YieldStatement)):
                return True
        return False

    def _acumula(self, corpo):
        """O laco empurra itens numa colecao?

        Tres formas contam, e a terceira e a que mais aparece em
        DataForge: 'p := [...p, x]'. Sem ela, uma acao que monta uma
        lista inteira era relatada como O(1) de espaco — e o spread e
        justamente como se cresce uma colecao aqui, porque e o que os
        exercicios ensinam.

        O que NAO conta e reatribuir: 't := t + x' num laco continua
        sendo O(1). A distincao e o ponto do relatorio; contar tudo
        como O(n) o tornaria inutil.
        """
        for no in self._andar(corpo):
            if isinstance(no, ast.MethodCall) and \
                    no.method in ("append", "push", "extend", "insert", "add"):
                return True
            if isinstance(no, ast.Assignment):
                alvo = getattr(no, "target", None)
                if isinstance(alvo, ast.IndexAccess):
                    return True
                if self._cresce_por_spread(no):
                    return True
        return False

    def _cresce_por_spread(self, no):
        """'p := [...p, x]' — a colecao se reconstroi maior.

        A confirmacao e o NOME: o spread precisa ser da propria
        variavel que esta sendo atribuida. 'p := [...outra, x]' e uma
        copia de tamanho fixo, nao um acumulo.
        """
        alvo = getattr(no, "target", None)
        nome = getattr(alvo, "name", None)
        if not nome:
            return False
        valor = getattr(no, "value", None)
        elementos = getattr(valor, "elements", None)
        if elementos is None:
            elementos = getattr(valor, "pairs", None)
            if elementos is None:
                return False
            elementos = [v for par in elementos for v in par]
        for elemento in elementos:
            if isinstance(elemento, ast.SpreadElement) and \
                    getattr(elemento.value, "name", None) == nome:
                return True
        return False

    def _ordem_conhecida(self, nome):
        """A ordem de uma acao ja analisada, se houver.

        Nao recorre: uma acao que chama outra que chama a primeira
        entraria em laco. Sem o resultado, o custo dela e ignorado, e o
        relatorio subestima — o que e melhor que travar.
        """
        for resultado in self.resultados:
            if resultado.nome == nome or resultado.nome.endswith("." + nome):
                return resultado.tempo
        return None

    @staticmethod
    def _andar(no):
        """Todos os nos da subarvore, em profundidade."""
        pilha = list(no) if isinstance(no, list) else [no]
        while pilha:
            atual = pilha.pop()
            if atual is None:
                continue
            if isinstance(atual, list):
                pilha.extend(atual)
                continue
            if not hasattr(atual, "__dataclass_fields__"):
                continue
            yield atual
            for campo in atual.__dataclass_fields__:
                valor = getattr(atual, campo, None)
                if isinstance(valor, (list, tuple)):
                    pilha.extend(v for v in valor
                                 if hasattr(v, "__dataclass_fields__")
                                 or isinstance(v, list))
                elif hasattr(valor, "__dataclass_fields__"):
                    pilha.append(valor)

    # ── avisos ──────────────────────────────────────────────

    def _avisar(self, resultado):
        """O que o numero sozinho nao diz."""
        tempo = resultado.tempo

        if tempo.familia == EXPONENCIAL:
            resultado.avisos.append({
                "nivel": "grave",
                "texto": (f"{tempo.texto()} dobra de custo a cada item a "
                          f"mais. Com 40 itens ja sao 10^12 operacoes."),
                "sugestao": ("guarde os resultados ja calculados num vault "
                             "(memoizacao): quase sempre derruba para O(n)"),
            })
        elif tempo.n >= 3:
            resultado.avisos.append({
                "nivel": "grave",
                "texto": (f"{tempo.texto()}: triplicar a entrada multiplica o "
                          f"tempo por {3 ** tempo.n}."),
                "sugestao": "veja se algum dos lacos pode virar um vault indexado",
            })
        elif tempo.n == 2:
            resultado.avisos.append({
                "nivel": "atencao",
                "texto": (f"{tempo.texto()}: dobrar a entrada quadruplica o "
                          f"tempo."),
                "sugestao": ("se um dos lacos so procura um item, um vault "
                             "faz isso em O(1) e derruba para O(n)"),
            })

        if tempo.familia == DESCONHECIDO:
            resultado.avisos.append({
                "nivel": "informacao",
                "texto": "a analise nao conseguiu provar que o laco termina.",
                "sugestao": ("nao e necessariamente um bug — so nao da para "
                             "afirmar a ordem sem executar"),
            })

        if resultado.espaco.n >= 1 and tempo.n >= 2:
            resultado.avisos.append({
                "nivel": "informacao",
                "texto": (f"custa {tempo.texto()} de tempo e "
                          f"{resultado.espaco.texto()} de espaco."),
                "sugestao": "trocar tempo por espaco aqui costuma valer a pena",
            })


# ═════════════════════════════════════════════════════════════
#  Entrada publica
# ═════════════════════════════════════════════════════════════

def analisar_fonte(fonte, arquivo="<stdin>"):
    """Analisa um programa e devolve a lista de Analise."""
    from .lexer import tokenize
    from .parser import parse

    programa = parse(tokenize(fonte, arquivo), arquivo)
    return Analisador(fonte).analisar(programa)


def analisar_arquivo(caminho):
    with open(caminho, encoding="utf-8") as f:
        return analisar_fonte(f.read(), caminho)


def para_json(resultados):
    """O resultado como estrutura, para o editor e para o site."""
    return {
        "acoes": [r.para_vault() for r in resultados],
        "pior": max((r.tempo for r in resultados),
                    key=lambda o: o._peso()).para_vault() if resultados else None,
    }


#: A tabela de referencia — o que cada classe significa na pratica.
#:
#: Os numeros nao sao decorativos: e a diferenca entre "isso e lento" e
#: "isso nao termina antes do almoco". Um O(n²) com um milhao de itens
#: e 10^12 operacoes; a mesma entrada em O(n log n) sao 2*10^7.
ESCALA = [
    {"notacao": "O(1)", "nome": "constante",
     "exemplo": "ler um item pelo indice, ler uma chave de vault",
     "n10": "1", "n1k": "1", "n1m": "1",
     "descricao": "o tamanho da entrada nao muda o tempo"},
    {"notacao": "O(log n)", "nome": "logaritmica",
     "exemplo": "busca binaria, altura de arvore balanceada",
     "n10": "3", "n1k": "10", "n1m": "20",
     "descricao": "cada passo descarta metade do que sobrou"},
    {"notacao": "O(n)", "nome": "linear",
     "exemplo": "percorrer uma lista, somar, procurar sem indice",
     "n10": "10", "n1k": "1.000", "n1m": "1.000.000",
     "descricao": "dobrar a entrada dobra o tempo"},
    {"notacao": "O(n log n)", "nome": "linearitmica",
     "exemplo": "ordenacao por comparacao, merge sort",
     "n10": "33", "n1k": "10.000", "n1m": "20.000.000",
     "descricao": "o melhor possivel para ordenar comparando"},
    {"notacao": "O(n^2)", "nome": "quadratica",
     "exemplo": "dois lacos aninhados, comparar todos com todos",
     "n10": "100", "n1k": "1.000.000", "n1m": "10^12",
     "descricao": "dobrar a entrada quadruplica o tempo"},
    {"notacao": "O(n^3)", "nome": "cubica",
     "exemplo": "tres lacos aninhados, multiplicacao de matriz ingenua",
     "n10": "1.000", "n1k": "10^9", "n1m": "10^18",
     "descricao": "so serve para entrada pequena"},
    {"notacao": "O(2^n)", "nome": "exponencial",
     "exemplo": "fibonacci sem memoizacao, subconjuntos",
     "n10": "1.024", "n1k": "10^301", "n1m": "—",
     "descricao": "cada item a mais dobra o custo"},
    {"notacao": "O(n!)", "nome": "fatorial",
     "exemplo": "todas as permutacoes, caixeiro viajante por forca bruta",
     "n10": "3.628.800", "n1k": "—", "n1m": "—",
     "descricao": "inviavel acima de uma dezena de itens"},
]
