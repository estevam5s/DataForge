"""
O construtor de consultas do Forge.

Monta SQL a partir de chamadas encadeadas, e nunca coloca um valor
dentro do texto: valores viram parametros, sempre. Nao e conveniencia —
e o que torna injecao de SQL impossivel por construcao em vez de por
disciplina.

    Forge.de(db, "usuarios")
        .onde("idade", ">=", 18)
        .onde_em("cidade", ["Floripa", "Sao Paulo"])
        .ordenar("nome")
        .limite(20)
        .buscar()

─── Por que um construtor, se ja da para escrever SQL ──────

Escrever SQL a mao continua valendo, e 'db.consultar(...)' esta ali
para isso. O construtor resolve tres coisas que o SQL a mao nao
resolve:

  1. **Dialeto.** '?' no SQLite e MySQL, '$1' no PostgreSQL; LIMIT no
     MySQL, OFFSET/FETCH no SQL Server. A mesma consulta roda nos
     tres sem reescrita.

  2. **Condicao opcional.** Um filtro que so existe quando o usuario
     preencheu o campo vira concatenacao de texto com 'and' na hora
     certa — o codigo mais chato e mais propenso a erro que existe.

  3. **Identificador citado.** Uma coluna chamada 'order' quebra a
     consulta; aqui ela e citada com o simbolo do dialeto.
"""

from ...errors import QueryError


#: Como cada dialeto cita um identificador e marca um parametro.
DIALETOS = {
    "postgres": {"citar": '"{}"', "marca": "${}", "numerado": True},
    "mysql":    {"citar": "`{}`", "marca": "?", "numerado": False},
    "mariadb":  {"citar": "`{}`", "marca": "?", "numerado": False},
    "sqlite":   {"citar": '"{}"', "marca": "?", "numerado": False},
}

#: Os operadores que 'onde' aceita. A lista e fechada de proposito: um
#: operador vindo de variavel e um caminho de injecao, e o unico jeito
#: de fechar esse caminho e nao aceitar texto arbitrario aqui.
OPERADORES = {
    "=", "==", "!=", "<>", "<", "<=", ">", ">=",
    "like", "not like", "ilike", "in", "not in",
    "is", "is not", "between",
}


class Consulta:
    """Uma consulta em construcao.

    Cada metodo devolve a propria consulta, entao encadear e natural. A
    consulta so vai ao banco quando alguem pede o resultado —
    'buscar()', 'primeiro()', 'contar()'. Ate la e so estrutura, o que
    permite monta-la em pedacos, por condicoes espalhadas pelo codigo.
    """

    def __init__(self, conexao, tabela, dialeto=None):
        self.conexao = conexao
        self.tabela = tabela
        self.dialeto = dialeto or getattr(conexao, "dialeto", "sqlite")
        self._perfil = DIALETOS.get(self.dialeto, DIALETOS["sqlite"])

        self._colunas = ["*"]
        self._condicoes = []            # [(juncao, texto, valores)]
        self._juncoes = []
        self._ordem = []
        self._agrupar = []
        self._tendo = []
        self._limite = None
        self._pular = None
        self._distinto = False
        self._valores = []

    # ── o que trazer ────────────────────────────────────────

    def selecionar(self, *colunas):
        """As colunas a trazer. Sem chamar, traz todas."""
        achatadas = []
        for c in colunas:
            achatadas.extend(c if isinstance(c, (list, tuple)) else [c])
        self._colunas = achatadas or ["*"]
        return self

    def distinto(self):
        self._distinto = True
        return self

    # ── filtros ─────────────────────────────────────────────

    def onde(self, coluna, operador=None, valor=None):
        """Uma condicao. 'onde("idade", ">=", 18)' ou 'onde("ativo", yes)'.

        Com dois argumentos, o operador e '='. E a forma mais comum, e
        obrigar a escrever '=' em todas nao acrescenta clareza.
        """
        if operador is not None and valor is None and not isinstance(operador, str):
            operador, valor = "=", operador
        elif valor is None and operador is not None and \
                str(operador).lower() not in OPERADORES:
            operador, valor = "=", operador

        return self._condicao("AND", coluna, operador or "=", valor)

    def ou_onde(self, coluna, operador=None, valor=None):
        if valor is None and operador is not None and \
                str(operador).lower() not in OPERADORES:
            operador, valor = "=", operador
        return self._condicao("OR", coluna, operador or "=", valor)

    def _condicao(self, juncao, coluna, operador, valor):
        op = str(operador).lower().strip()
        if op not in OPERADORES:
            aceitos = ", ".join(sorted(OPERADORES))
            raise QueryError(
                f"'{operador}' is not an operator the builder accepts.",
                nota=f"it takes: {aceitos}",
                dica=("the list is closed on purpose: an operator coming "
                      "from a variable would be an injection path"),
                doc="banco-de-dados")

        if op == "==":
            op = "="
        if op == "<>":
            op = "!="

        # 'onde("x", "=", void)' quase sempre quer dizer 'is null': em
        # SQL, 'x = NULL' nunca e verdadeiro, nem quando x e nulo.
        if valor is None and op in ("=", "!="):
            texto = f"{self.citar(coluna)} IS {'NOT ' if op == '!=' else ''}NULL"
            self._condicoes.append((juncao, texto, []))
            return self

        self._condicoes.append(
            (juncao, f"{self.citar(coluna)} {op.upper()} {{}}", [valor]))
        return self

    def onde_em(self, coluna, valores):
        """'onde_em("id", [1, 2, 3])' — um parametro por item."""
        itens = list(valores)
        if not itens:
            # 'in ()' e erro de sintaxe em quase todo banco. Uma
            # condicao sempre falsa e o que a lista vazia significa.
            self._condicoes.append(("AND", "1 = 0", []))
            return self
        marcas = ", ".join("{}" for _ in itens)
        self._condicoes.append(
            ("AND", f"{self.citar(coluna)} IN ({marcas})", itens))
        return self

    def onde_fora(self, coluna, valores):
        itens = list(valores)
        if not itens:
            return self
        marcas = ", ".join("{}" for _ in itens)
        self._condicoes.append(
            ("AND", f"{self.citar(coluna)} NOT IN ({marcas})", itens))
        return self

    def onde_entre(self, coluna, minimo, maximo):
        self._condicoes.append(
            ("AND", f"{self.citar(coluna)} BETWEEN {{}} AND {{}}",
             [minimo, maximo]))
        return self

    def onde_nulo(self, coluna, nulo=True):
        self._condicoes.append(
            ("AND", f"{self.citar(coluna)} IS {'' if nulo else 'NOT '}NULL", []))
        return self

    def onde_contem(self, coluna, trecho):
        """LIKE '%trecho%', com o trecho como parametro."""
        self._condicoes.append(
            ("AND", f"{self.citar(coluna)} LIKE {{}}", [f"%{trecho}%"]))
        return self

    def onde_comeca(self, coluna, prefixo):
        self._condicoes.append(
            ("AND", f"{self.citar(coluna)} LIKE {{}}", [f"{prefixo}%"]))
        return self

    def onde_cru(self, sql, valores=None):
        """Uma condicao escrita a mao, com os valores ainda parametrizados.

        A saida de emergencia para o que o construtor nao cobre —
        funcoes do banco, operadores geograficos. O SQL vai como
        escrito; os valores continuam parametros.
        """
        self._condicoes.append(("AND", sql.replace("?", "{}"),
                                list(valores or [])))
        return self

    def quando(self, condicao, funcao):
        """Aplica o trecho so se a condicao valer.

        E o que evita o 'if' em volta da consulta:

            q.quando(busca, lambda c => c.onde_contem("nome", busca))
        """
        if condicao:
            resultado = funcao(self)
            return resultado if isinstance(resultado, Consulta) else self
        return self

    # ── juncoes ─────────────────────────────────────────────

    def juntar(self, tabela, coluna_esquerda, coluna_direita, tipo="INNER"):
        self._juncoes.append(
            f"{tipo} JOIN {self.citar(tabela)} ON "
            f"{self._citar_caminho(coluna_esquerda)} = "
            f"{self._citar_caminho(coluna_direita)}")
        return self

    def juntar_esquerda(self, tabela, esquerda, direita):
        return self.juntar(tabela, esquerda, direita, "LEFT")

    # ── ordem e recorte ─────────────────────────────────────

    def ordenar(self, coluna, direcao="asc"):
        d = str(direcao).lower()
        if d not in ("asc", "desc"):
            raise QueryError(
                f"'{direcao}' is not a sort direction; use 'asc' or 'desc'.",
                doc="banco-de-dados")
        self._ordem.append(f"{self._citar_caminho(coluna)} {d.upper()}")
        return self

    def agrupar(self, *colunas):
        self._agrupar.extend(self._citar_caminho(c) for c in colunas)
        return self

    def tendo(self, sql, valores=None):
        self._tendo.append((sql.replace("?", "{}"), list(valores or [])))
        return self

    def limite(self, n):
        self._limite = int(n)
        return self

    def pular(self, n):
        self._pular = int(n)
        return self

    def pagina(self, numero, por_pagina=20):
        """Pagina 1 e a primeira — nao a zero.

        Off-by-one em paginacao e classico: quem chama pensa em
        'pagina 1', e o banco pensa em 'pule 0'.
        """
        numero = max(1, int(numero))
        return self.limite(por_pagina).pular((numero - 1) * por_pagina)

    # ── montagem ────────────────────────────────────────────

    def citar(self, identificador):
        """Cita um nome, para uma coluna chamada 'order' nao quebrar."""
        nome = str(identificador)
        if nome == "*" or "(" in nome:
            return nome                              # funcao ou estrela
        return self._perfil["citar"].format(nome.replace('"', "").replace("`", ""))

    def _citar_caminho(self, caminho):
        """'usuarios.id' -> "usuarios"."id"."""
        texto = str(caminho)
        if "(" in texto:
            return texto
        return ".".join(self.citar(p) for p in texto.split("."))

    def montar(self):
        """Devolve (sql, valores). Nao vai ao banco."""
        valores = []
        partes = ["SELECT"]
        if self._distinto:
            partes.append("DISTINCT")
        partes.append(", ".join(self._citar_caminho(c) for c in self._colunas))
        partes.append(f"FROM {self.citar(self.tabela)}")
        partes.extend(self._juncoes)

        if self._condicoes:
            pedacos = []
            for i, (juncao, texto, vals) in enumerate(self._condicoes):
                if i:
                    pedacos.append(juncao)
                pedacos.append(texto)
                valores.extend(vals)
            partes.append("WHERE " + " ".join(pedacos))

        if self._agrupar:
            partes.append("GROUP BY " + ", ".join(self._agrupar))
        if self._tendo:
            pedacos = []
            for texto, vals in self._tendo:
                pedacos.append(texto)
                valores.extend(vals)
            partes.append("HAVING " + " AND ".join(pedacos))
        if self._ordem:
            partes.append("ORDER BY " + ", ".join(self._ordem))
        if self._limite is not None:
            partes.append(f"LIMIT {self._limite}")
        if self._pular is not None:
            partes.append(f"OFFSET {self._pular}")

        return self._numerar(" ".join(partes)), valores

    def _numerar(self, sql):
        """Troca '{}' pela marca do dialeto."""
        if not self._perfil["numerado"]:
            return sql.replace("{}", "?")
        saida, n = [], 0
        i = 0
        while i < len(sql):
            if sql[i:i + 2] == "{}":
                n += 1
                saida.append(f"${n}")
                i += 2
            else:
                saida.append(sql[i])
                i += 1
        return "".join(saida)

    # ── execucao ────────────────────────────────────────────

    def buscar(self):
        """Roda e devolve todas as linhas."""
        sql, valores = self.montar()
        return self.conexao.consultar(sql, valores)

    def primeiro(self):
        """A primeira linha, ou void."""
        linhas = self.limite(1).buscar()
        return linhas[0] if linhas else None

    def primeiro_ou_erro(self):
        """A primeira linha; erro se nao houver."""
        from ...errors import RecordNotFoundError
        linha = self.primeiro()
        if linha is None:
            raise RecordNotFoundError(
                f"no row in '{self.tabela}' matches this query.",
                dica="use  primeiro()  when the absence is expected",
                doc="orm")
        return linha

    def contar(self, coluna="*"):
        copia = self._copiar()
        copia._colunas = [f"COUNT({coluna if coluna == '*' else self.citar(coluna)}) AS n"]
        copia._ordem = []
        copia._limite = copia._pular = None
        linhas = copia.buscar()
        return linhas[0]["n"] if linhas else 0

    def existe(self):
        return self.contar() > 0

    def somar(self, coluna):
        return self._agregar("SUM", coluna)

    def media(self, coluna):
        return self._agregar("AVG", coluna)

    def minimo(self, coluna):
        return self._agregar("MIN", coluna)

    def maximo(self, coluna):
        return self._agregar("MAX", coluna)

    def _agregar(self, funcao, coluna):
        copia = self._copiar()
        copia._colunas = [f"{funcao}({self.citar(coluna)}) AS valor"]
        copia._ordem = []
        copia._limite = copia._pular = None
        linhas = copia.buscar()
        return linhas[0]["valor"] if linhas else None

    def valores(self, coluna):
        """Uma coluna, como cluster simples."""
        return [l[coluna] for l in self.selecionar(coluna).buscar()]

    def paginar(self, numero=1, por_pagina=20):
        """Traz a pagina E os numeros que a interface precisa."""
        total = self.contar()
        linhas = self.pagina(numero, por_pagina).buscar()
        paginas = max(1, -(-total // por_pagina))
        return {
            "linhas": linhas,
            "total": total,
            "pagina": numero,
            "por_pagina": por_pagina,
            "paginas": paginas,
            "tem_proxima": numero < paginas,
            "tem_anterior": numero > 1,
        }

    # ── escritas ────────────────────────────────────────────

    def inserir(self, dados):
        """Insere um vault, ou varios de uma vez."""
        if isinstance(dados, dict):
            dados = [dados]
        if not dados:
            return 0

        colunas = list(dados[0])
        valores = []
        grupos = []
        for linha in dados:
            faltando = [c for c in colunas if c not in linha]
            if faltando:
                raise QueryError(
                    f"row is missing column(s): {', '.join(faltando)}.",
                    nota="every row of a batch insert needs the same columns",
                    doc="banco-de-dados")
            grupos.append("(" + ", ".join("{}" for _ in colunas) + ")")
            valores.extend(linha[c] for c in colunas)

        sql = (f"INSERT INTO {self.citar(self.tabela)} "
               f"({', '.join(self.citar(c) for c in colunas)}) "
               f"VALUES {', '.join(grupos)}")
        return self.conexao.executar(self._numerar(sql), valores)

    def inserir_e_devolver(self, dados, chave="id"):
        """Insere e devolve a linha criada, com o id gerado.

        Cada banco responde a isso de um jeito: o PostgreSQL tem
        RETURNING, o MySQL tem last_insert_id, o SQLite tem lastrowid.
        Aqui a diferenca fica escondida.
        """
        if self.dialeto == "postgres":
            colunas = list(dados)
            sql = (f"INSERT INTO {self.citar(self.tabela)} "
                   f"({', '.join(self.citar(c) for c in colunas)}) "
                   f"VALUES ({', '.join('{}' for _ in colunas)}) RETURNING *")
            linhas = self.conexao.executar(
                self._numerar(sql), [dados[c] for c in colunas])
            return linhas[0] if isinstance(linhas, list) and linhas else None

        self.inserir(dados)
        novo = getattr(self.conexao, "ultimo_id", lambda: None)()
        if novo:
            return Consulta(self.conexao, self.tabela, self.dialeto) \
                .onde(chave, novo).primeiro()
        return dict(dados)

    def atualizar(self, mudancas):
        if not mudancas:
            return 0
        valores = list(mudancas.values())
        atribuicoes = ", ".join(f"{self.citar(c)} = {{}}" for c in mudancas)
        sql = f"UPDATE {self.citar(self.tabela)} SET {atribuicoes}"

        if self._condicoes:
            pedacos = []
            for i, (juncao, texto, vals) in enumerate(self._condicoes):
                if i:
                    pedacos.append(juncao)
                pedacos.append(texto)
                valores.extend(vals)
            sql += " WHERE " + " ".join(pedacos)
        else:
            raise QueryError(
                "an UPDATE with no condition would change every row.",
                dica=("add  .onde(...)  first, or call "
                      "atualizar_tudo() if that is really what you want"),
                doc="banco-de-dados")

        return self.conexao.executar(self._numerar(sql), valores)

    def atualizar_tudo(self, mudancas):
        """Atualiza a tabela inteira — de proposito, e por escrito."""
        valores = list(mudancas.values())
        atribuicoes = ", ".join(f"{self.citar(c)} = {{}}" for c in mudancas)
        sql = f"UPDATE {self.citar(self.tabela)} SET {atribuicoes}"
        return self.conexao.executar(self._numerar(sql), valores)

    def incrementar(self, coluna, quanto=1):
        """'x = x + n' no banco, sem ler antes.

        Ler, somar e gravar perde atualizacoes quando duas conexoes
        fazem isso ao mesmo tempo. Deixar a soma com o banco nao perde.
        """
        valores = [quanto]
        sql = (f"UPDATE {self.citar(self.tabela)} SET "
               f"{self.citar(coluna)} = {self.citar(coluna)} + {{}}")
        if self._condicoes:
            pedacos = []
            for i, (juncao, texto, vals) in enumerate(self._condicoes):
                if i:
                    pedacos.append(juncao)
                pedacos.append(texto)
                valores.extend(vals)
            sql += " WHERE " + " ".join(pedacos)
        return self.conexao.executar(self._numerar(sql), valores)

    def remover(self):
        if not self._condicoes:
            raise QueryError(
                "a DELETE with no condition would empty the table.",
                dica=("add  .onde(...)  first, or call  remover_tudo()  "
                      "if that is really what you want"),
                doc="banco-de-dados")
        valores, pedacos = [], []
        for i, (juncao, texto, vals) in enumerate(self._condicoes):
            if i:
                pedacos.append(juncao)
            pedacos.append(texto)
            valores.extend(vals)
        sql = (f"DELETE FROM {self.citar(self.tabela)} "
               f"WHERE {' '.join(pedacos)}")
        return self.conexao.executar(self._numerar(sql), valores)

    def remover_tudo(self):
        """Esvazia a tabela — de proposito, e por escrito."""
        return self.conexao.executar(
            f"DELETE FROM {self.citar(self.tabela)}")

    # ── auxiliares ──────────────────────────────────────────

    def _copiar(self):
        nova = Consulta(self.conexao, self.tabela, self.dialeto)
        nova._colunas = list(self._colunas)
        nova._condicoes = list(self._condicoes)
        nova._juncoes = list(self._juncoes)
        nova._ordem = list(self._ordem)
        nova._agrupar = list(self._agrupar)
        nova._tendo = list(self._tendo)
        nova._limite = self._limite
        nova._pular = self._pular
        nova._distinto = self._distinto
        return nova

    def sql(self):
        """O SQL que seria enviado, para conferir ou registrar."""
        texto, valores = self.montar()
        return {"sql": texto, "valores": valores}

    def __repr__(self):
        return f"<Consulta {self.montar()[0]}>"
