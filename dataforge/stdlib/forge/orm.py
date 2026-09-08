"""
O ORM do Forge — modelos, relacoes e migracoes.

Um modelo descreve uma tabela e o que vale nela:

    modelo Usuario:
        campo id: Serial
        campo email: Texto unico obrigatorio
        campo idade: Inteiro padrao 0
        campo criado_em: DataHora automatico

        tem_muitos Pedido

E o que se ganha sobre o construtor de consultas:

    validacao       antes de ir ao banco, e com TODOS os erros de uma
                    vez — nao o primeiro que aparecer
    relacoes        carregadas sem o problema de N+1
    migracoes       a diferenca entre o modelo e a tabela, como SQL
    conversao       o que sai do banco volta com o tipo declarado

─── A decisao que mais importa: N+1 ────────────────────────

Buscar cem usuarios e ler 'usuario.pedidos' de cada um faz cento e uma
consultas. Isso nao aparece em desenvolvimento, com tres linhas na
tabela, e derruba a producao com dez mil. E o bug de ORM mais comum que
existe.

Aqui a relacao NAO carrega sozinha ao ser lida. Ou se pede
('com("pedidos")', que faz duas consultas para qualquer quantidade), ou
se chama explicitamente. Ler uma relacao nao carregada devolve void e
diz o que fazer — em vez de funcionar devagar.
"""

import datetime
import json
import re

from .consulta import Consulta
from ...errors import (ConstraintError, DatabaseError, MigrationError,
                       QueryError, RecordNotFoundError, SchemaError,
                       ValidationError)


# ═════════════════════════════════════════════════════════════
#  Tipos
# ═════════════════════════════════════════════════════════════

#: Tipo do Forge -> tipo SQL de cada dialeto.
#:
#: 'Serial' e o unico que difere tanto que precisa de linha propria em
#: cada um: o PostgreSQL tem SERIAL, o MySQL tem AUTO_INCREMENT e o
#: SQLite exige exatamente 'INTEGER PRIMARY KEY AUTOINCREMENT'.
TIPOS_SQL = {
    "Serial": {
        "postgres": "SERIAL PRIMARY KEY",
        "mysql": "INT AUTO_INCREMENT PRIMARY KEY",
        "mariadb": "INT AUTO_INCREMENT PRIMARY KEY",
        "sqlite": "INTEGER PRIMARY KEY AUTOINCREMENT",
    },
    "Inteiro": {"postgres": "INTEGER", "mysql": "INT", "mariadb": "INT",
                "sqlite": "INTEGER"},
    "Grande": {"postgres": "BIGINT", "mysql": "BIGINT", "mariadb": "BIGINT",
               "sqlite": "INTEGER"},
    "Decimal": {"postgres": "NUMERIC(18,6)", "mysql": "DECIMAL(18,6)",
                "mariadb": "DECIMAL(18,6)", "sqlite": "NUMERIC"},
    "Real": {"postgres": "DOUBLE PRECISION", "mysql": "DOUBLE",
             "mariadb": "DOUBLE", "sqlite": "REAL"},
    "Texto": {"postgres": "TEXT", "mysql": "VARCHAR(255)",
              "mariadb": "VARCHAR(255)", "sqlite": "TEXT"},
    "TextoLongo": {"postgres": "TEXT", "mysql": "LONGTEXT",
                   "mariadb": "LONGTEXT", "sqlite": "TEXT"},
    "Booleano": {"postgres": "BOOLEAN", "mysql": "TINYINT(1)",
                 "mariadb": "TINYINT(1)", "sqlite": "INTEGER"},
    "Data": {"postgres": "DATE", "mysql": "DATE", "mariadb": "DATE",
             "sqlite": "TEXT"},
    "DataHora": {"postgres": "TIMESTAMPTZ", "mysql": "DATETIME",
                 "mariadb": "DATETIME", "sqlite": "TEXT"},
    "Json": {"postgres": "JSONB", "mysql": "JSON", "mariadb": "JSON",
             "sqlite": "TEXT"},
    "Uuid": {"postgres": "UUID", "mysql": "CHAR(36)", "mariadb": "CHAR(36)",
             "sqlite": "TEXT"},
    "Binario": {"postgres": "BYTEA", "mysql": "BLOB", "mariadb": "BLOB",
                "sqlite": "BLOB"},
}


def sql_do_tipo(tipo, dialeto):
    mapa = TIPOS_SQL.get(tipo)
    if mapa is None:
        conhecidos = ", ".join(sorted(TIPOS_SQL))
        raise SchemaError(
            f"'{tipo}' is not a Forge column type.",
            nota=f"the types are: {conhecidos}",
            doc="orm")
    return mapa.get(dialeto, mapa["sqlite"])


class Campo:
    """A declaracao de uma coluna."""

    __slots__ = ("nome", "tipo", "obrigatorio", "unico", "padrao", "indice",
                 "chave", "referencia", "automatico", "validacoes", "tamanho",
                 "comentario")

    def __init__(self, nome, tipo="Texto", obrigatorio=False, unico=False,
                 padrao=None, indice=False, chave=False, referencia="",
                 automatico=False, validacoes=None, tamanho=0, comentario=""):
        self.nome = nome
        self.tipo = tipo
        self.obrigatorio = obrigatorio
        self.unico = unico
        self.padrao = padrao
        self.indice = indice
        self.chave = chave or tipo == "Serial"
        self.referencia = referencia
        self.automatico = automatico
        self.validacoes = list(validacoes or [])
        self.tamanho = tamanho
        self.comentario = comentario

    def sql(self, dialeto):
        partes = [f'"{self.nome}"' if dialeto in ("postgres", "sqlite")
                  else f"`{self.nome}`"]
        tipo = sql_do_tipo(self.tipo, dialeto)
        if self.tamanho and self.tipo == "Texto":
            tipo = (f"VARCHAR({self.tamanho})" if dialeto != "sqlite"
                    else "TEXT")
        partes.append(tipo)

        if self.tipo != "Serial":
            if self.obrigatorio:
                partes.append("NOT NULL")
            if self.unico:
                partes.append("UNIQUE")
            if self.padrao is not None:
                partes.append(f"DEFAULT {self._padrao_sql(dialeto)}")
        return " ".join(partes)

    def _padrao_sql(self, dialeto):
        if isinstance(self.padrao, bool):
            if dialeto in ("mysql", "mariadb", "sqlite"):
                return "1" if self.padrao else "0"
            return "TRUE" if self.padrao else "FALSE"
        if isinstance(self.padrao, (int, float)):
            return repr(self.padrao)
        if self.padrao == "agora":
            return "CURRENT_TIMESTAMP"
        return "'" + str(self.padrao).replace("'", "''") + "'"

    def converter(self, valor):
        """O valor do banco, no tipo que o modelo declara.

        SQLite guarda booleano como 0 e 1, e data como texto. Sem esta
        conversao, 'given usuario["ativo"]:' e sempre verdadeiro — 0 e
        um inteiro, e um inteiro nao vazio vale como verdadeiro em
        muitos lugares.
        """
        if valor is None:
            return None
        try:
            if self.tipo == "Booleano":
                if isinstance(valor, bool):
                    return valor
                if isinstance(valor, (int, float)):
                    return bool(valor)
                return str(valor).lower() in ("1", "true", "t", "yes", "sim")
            if self.tipo in ("Inteiro", "Grande", "Serial"):
                return int(valor)
            if self.tipo in ("Real", "Decimal"):
                return float(valor)
            if self.tipo == "Json" and isinstance(valor, str):
                return json.loads(valor)
        except (TypeError, ValueError, json.JSONDecodeError):
            return valor
        return valor

    def para_banco(self, valor, dialeto="sqlite"):
        """O valor no formato que ESTE banco aceita.

        Data e hora e onde os motores mais divergem. O PostgreSQL
        entende ISO-8601 com fuso e o guarda em TIMESTAMPTZ; o
        DATETIME do MySQL nao tem fuso, e o do MariaDB recusa o 'T' e
        o '+00:00' de vez — com um erro que fala de 'incorrect
        datetime value' e nao diz o que ele queria.

        Um formato so para os tres significaria descartar o fuso
        sempre, inclusive onde o banco sabe guarda-lo.
        """
        if valor is None:
            return None
        if self.tipo == "Json" and isinstance(valor, (dict, list)):
            return json.dumps(valor, ensure_ascii=False)
        if self.tipo == "Booleano":
            return bool(valor)
        if self.tipo in ("DataHora", "Data"):
            return self._data_para_banco(valor, dialeto)
        return valor

    @staticmethod
    def _data_para_banco(valor, dialeto):
        if isinstance(valor, str):
            if dialeto in ("mysql", "mariadb"):
                # Normaliza o que veio pronto: corta o fuso e troca o
                # 'T' pelo espaco que o DATETIME exige.
                texto = valor.replace("T", " ")
                for corte in ("+", "Z"):
                    i = texto.find(corte, 10)
                    if i > 0:
                        texto = texto[:i]
                return texto.split(".")[0]
            return valor
        if isinstance(valor, datetime.datetime):
            if dialeto in ("mysql", "mariadb"):
                return valor.strftime("%Y-%m-%d %H:%M:%S")
            return valor.isoformat()
        if isinstance(valor, datetime.date):
            return valor.isoformat()
        return valor


# ═════════════════════════════════════════════════════════════
#  Validacao
# ═════════════════════════════════════════════════════════════

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


class Validador:
    """As regras que um campo pode cobrar.

    A validacao junta TODOS os erros antes de reclamar. Um formulario
    que aponta um erro por vez faz o usuario submeter cinco vezes para
    descobrir cinco problemas.
    """

    @staticmethod
    def obrigatorio(valor, _=None):
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            return "e obrigatorio"
        return ""

    @staticmethod
    def email(valor, _=None):
        if valor and not EMAIL.match(str(valor)):
            return "nao parece um e-mail"
        return ""

    @staticmethod
    def minimo(valor, limite):
        if valor is None:
            return ""
        try:
            if isinstance(valor, str):
                return (f"precisa de ao menos {limite} caracteres"
                        if len(valor) < limite else "")
            return f"precisa ser ao menos {limite}" if valor < limite else ""
        except TypeError:
            return ""

    @staticmethod
    def maximo(valor, limite):
        if valor is None:
            return ""
        try:
            if isinstance(valor, str):
                return (f"passa de {limite} caracteres"
                        if len(valor) > limite else "")
            return f"nao pode passar de {limite}" if valor > limite else ""
        except TypeError:
            return ""

    @staticmethod
    def formato(valor, padrao):
        if valor and not re.match(padrao, str(valor)):
            return f"nao casa com o formato esperado"
        return ""

    @staticmethod
    def um_de(valor, opcoes):
        if valor is not None and valor not in opcoes:
            return f"precisa ser um de: {', '.join(str(o) for o in opcoes)}"
        return ""

    @staticmethod
    def positivo(valor, _=None):
        if valor is not None and valor <= 0:
            return "precisa ser positivo"
        return ""


REGRAS = {nome: getattr(Validador, nome) for nome in
          ("obrigatorio", "email", "minimo", "maximo", "formato", "um_de",
           "positivo")}


# ═════════════════════════════════════════════════════════════
#  Relacoes
# ═════════════════════════════════════════════════════════════

class Relacao:
    """Uma ligacao entre dois modelos."""

    __slots__ = ("tipo", "nome", "modelo", "chave_local", "chave_externa",
                 "tabela_ponte")

    def __init__(self, tipo, nome, modelo, chave_local="", chave_externa="",
                 tabela_ponte=""):
        self.tipo = tipo               # "tem_um" | "tem_muitos" | "pertence_a" | "muitos_para_muitos"
        self.nome = nome
        self.modelo = modelo
        self.chave_local = chave_local
        self.chave_externa = chave_externa
        self.tabela_ponte = tabela_ponte


# ═════════════════════════════════════════════════════════════
#  Modelo
# ═════════════════════════════════════════════════════════════

class Modelo:
    """A descricao de uma tabela, e o que se pode fazer com ela."""

    def __init__(self, nome, tabela="", conexao=None):
        self.nome = nome
        self.tabela = tabela or self._pluralizar(nome)
        self.conexao = conexao
        self.campos = {}
        self.relacoes = {}
        self.ganchos = {"antes_de_salvar": [], "depois_de_salvar": [],
                        "antes_de_remover": [], "depois_de_remover": []}
        self.chave = "id"
        self.marcas_de_tempo = False
        self.remocao_suave = False

    @staticmethod
    def _pluralizar(nome):
        """O plural em portugues, para o nome da tabela.

        Nao cobre tudo — nenhuma regra cobre — mas acerta os casos que
        aparecem. Quem tiver um irregular passa o nome da tabela.
        """
        n = nome.lower()
        if n.endswith(("s", "x", "z")):
            return n
        if n.endswith("ao"):
            return n[:-2] + "oes"
        if n.endswith(("r", "n")):
            return n + "es"
        if n.endswith("l"):
            return n[:-1] + "is"
        if n.endswith("m"):
            return n[:-1] + "ns"
        return n + "s"

    # ── declaracao ──────────────────────────────────────────

    def campo(self, nome, tipo="Texto", **opcoes):
        self.campos[nome] = Campo(nome, tipo, **opcoes)
        if opcoes.get("chave") or tipo == "Serial":
            self.chave = nome
        return self

    def tem_muitos(self, nome, modelo, chave_externa=""):
        self.relacoes[nome] = Relacao(
            "tem_muitos", nome, modelo,
            chave_local=self.chave,
            chave_externa=chave_externa or f"{self.nome.lower()}_id")
        return self

    def tem_um(self, nome, modelo, chave_externa=""):
        self.relacoes[nome] = Relacao(
            "tem_um", nome, modelo,
            chave_local=self.chave,
            chave_externa=chave_externa or f"{self.nome.lower()}_id")
        return self

    def pertence_a(self, nome, modelo, chave_local=""):
        self.relacoes[nome] = Relacao(
            "pertence_a", nome, modelo,
            chave_local=chave_local or f"{nome.lower()}_id",
            chave_externa="id")
        return self

    def muitos_para_muitos(self, nome, modelo, ponte="", local="", externa=""):
        self.relacoes[nome] = Relacao(
            "muitos_para_muitos", nome, modelo,
            chave_local=local or f"{self.nome.lower()}_id",
            chave_externa=externa or f"{modelo.lower()}_id",
            tabela_ponte=ponte or "_".join(
                sorted([self.tabela, self._pluralizar(modelo)])))
        return self

    def com_marcas_de_tempo(self):
        """Acrescenta 'criado_em' e 'atualizado_em', mantidos sozinhos."""
        self.marcas_de_tempo = True
        self.campo("criado_em", "DataHora")
        self.campo("atualizado_em", "DataHora")
        return self

    def com_remocao_suave(self):
        """'remover' marca em vez de apagar; as buscas ignoram os marcados."""
        self.remocao_suave = True
        self.campo("removido_em", "DataHora")
        return self

    def antes_de_salvar(self, funcao):
        self.ganchos["antes_de_salvar"].append(funcao)
        return self

    def depois_de_salvar(self, funcao):
        self.ganchos["depois_de_salvar"].append(funcao)
        return self

    # ── validacao ───────────────────────────────────────────

    def validar(self, dados, parcial=False):
        """Devolve a lista de problemas — TODOS eles, nao o primeiro."""
        problemas = []

        for nome, campo in self.campos.items():
            if campo.tipo == "Serial" or campo.automatico:
                continue
            presente = nome in dados
            valor = dados.get(nome)

            if campo.obrigatorio and not parcial and not presente:
                problemas.append({"campo": nome, "motivo": "e obrigatorio"})
                continue
            if not presente:
                continue
            if campo.obrigatorio:
                erro = Validador.obrigatorio(valor)
                if erro:
                    problemas.append({"campo": nome, "motivo": erro})
                    continue

            for regra in campo.validacoes:
                if isinstance(regra, (list, tuple)):
                    nome_regra, argumento = regra[0], regra[1]
                else:
                    nome_regra, argumento = regra, None
                funcao = REGRAS.get(nome_regra)
                if funcao is None:
                    continue
                erro = funcao(valor, argumento)
                if erro:
                    problemas.append({"campo": nome, "motivo": erro})

        desconhecidos = [k for k in dados if k not in self.campos]
        for k in desconhecidos:
            problemas.append({
                "campo": k,
                "motivo": f"nao e um campo de {self.nome}"})

        return problemas

    def _cobrar_validacao(self, dados, parcial=False):
        problemas = self.validar(dados, parcial)
        if problemas:
            resumo = "; ".join(f"{p['campo']}: {p['motivo']}" for p in problemas)
            erro = ValidationError(
                f"{self.nome} did not validate: {resumo}",
                nota=f"{len(problemas)} field(s) with problems",
                dica="the full list is in e.campos",
                doc="orm")
            erro.campos = problemas
            raise erro

    # ── consultas ───────────────────────────────────────────

    def consulta(self):
        """Uma consulta nova sobre a tabela deste modelo."""
        self._exigir_conexao()
        q = Consulta(self.conexao, self.tabela)
        if self.remocao_suave:
            q.onde_nulo("removido_em")
        return q

    def todos(self, limite=0):
        q = self.consulta()
        if limite:
            q.limite(limite)
        return [self._converter(l) for l in q.buscar()]

    def buscar(self, valor, chave=""):
        """A linha com aquela chave, ou void."""
        linha = self.consulta().onde(chave or self.chave, valor).primeiro()
        return self._converter(linha) if linha else None

    def buscar_ou_erro(self, valor, chave=""):
        linha = self.buscar(valor, chave)
        if linha is None:
            raise RecordNotFoundError(
                f"no {self.nome} with {chave or self.chave} = {valor!r}.",
                dica=f"use  {self.nome}.buscar(...)  when the absence is expected",
                doc="orm")
        return linha

    def onde(self, coluna, operador=None, valor=None):
        return self.consulta().onde(coluna, operador, valor)

    def primeiro(self, **filtros):
        q = self.consulta()
        for coluna, valor in filtros.items():
            q.onde(coluna, valor)
        linha = q.primeiro()
        return self._converter(linha) if linha else None

    def contar(self, **filtros):
        q = self.consulta()
        for coluna, valor in filtros.items():
            q.onde(coluna, valor)
        return q.contar()

    def existe(self, **filtros):
        return self.contar(**filtros) > 0

    # ── escritas ────────────────────────────────────────────

    def criar(self, dados):
        """Valida, aplica os ganchos, insere, devolve a linha criada."""
        self._exigir_conexao()
        dados = dict(dados)

        for gancho in self.ganchos["antes_de_salvar"]:
            resultado = gancho(dados)
            if isinstance(resultado, dict):
                dados = resultado

        if self.marcas_de_tempo:
            # Um datetime, e nao texto: cada campo o formata para o
            # banco em que vai cair.
            agora = datetime.datetime.now(datetime.timezone.utc)
            dados.setdefault("criado_em", agora)
            dados.setdefault("atualizado_em", agora)

        self._cobrar_validacao(dados)

        dialeto = getattr(self.conexao, "dialeto", "sqlite")
        preparados = {k: self.campos[k].para_banco(v, dialeto)
                      for k, v in dados.items() if k in self.campos}
        linha = Consulta(self.conexao, self.tabela).inserir_e_devolver(
            preparados, self.chave)
        criada = self._converter(linha) if linha else preparados

        for gancho in self.ganchos["depois_de_salvar"]:
            gancho(criada)
        return criada

    def criar_varios(self, linhas):
        self._exigir_conexao()
        for linha in linhas:
            self._cobrar_validacao(dict(linha))
        dialeto = getattr(self.conexao, "dialeto", "sqlite")
        preparadas = [{k: self.campos[k].para_banco(v, dialeto)
                       for k, v in linha.items() if k in self.campos}
                      for linha in linhas]
        return Consulta(self.conexao, self.tabela).inserir(preparadas)

    def atualizar(self, valor_chave, mudancas):
        self._exigir_conexao()
        mudancas = dict(mudancas)
        self._cobrar_validacao(mudancas, parcial=True)

        if self.marcas_de_tempo:
            mudancas["atualizado_em"] = datetime.datetime.now(
                datetime.timezone.utc)

        dialeto = getattr(self.conexao, "dialeto", "sqlite")
        preparadas = {k: self.campos[k].para_banco(v, dialeto)
                      for k, v in mudancas.items() if k in self.campos}
        Consulta(self.conexao, self.tabela) \
            .onde(self.chave, valor_chave).atualizar(preparadas)
        return self.buscar(valor_chave)

    def remover(self, valor_chave):
        self._exigir_conexao()
        for gancho in self.ganchos["antes_de_remover"]:
            gancho(valor_chave)

        if self.remocao_suave:
            dialeto = getattr(self.conexao, "dialeto", "sqlite")
            agora = self.campos["removido_em"].para_banco(
                datetime.datetime.now(datetime.timezone.utc), dialeto)
            n = Consulta(self.conexao, self.tabela) \
                .onde(self.chave, valor_chave) \
                .atualizar({"removido_em": agora})
        else:
            n = Consulta(self.conexao, self.tabela) \
                .onde(self.chave, valor_chave).remover()

        for gancho in self.ganchos["depois_de_remover"]:
            gancho(valor_chave)
        return n

    def criar_ou_atualizar(self, procura, dados):
        """Acha pela procura; cria se nao existir, atualiza se existir."""
        existente = self.primeiro(**procura)
        if existente:
            return self.atualizar(existente[self.chave], dados)
        return self.criar({**procura, **dados})

    # ── relacoes ────────────────────────────────────────────

    def com(self, linhas, *nomes):
        """Carrega as relacoes de uma vez — duas consultas, nao N+1.

        Buscar cem usuarios e ler 'pedidos' de cada um faz cento e uma
        consultas. Aqui sao duas, para qualquer quantidade: uma para os
        usuarios, outra para todos os pedidos deles.
        """
        self._exigir_conexao()
        if isinstance(linhas, dict):
            linhas = [linhas]
        linhas = list(linhas)
        if not linhas:
            return linhas

        for nome in nomes:
            relacao = self.relacoes.get(nome)
            if relacao is None:
                conhecidas = ", ".join(self.relacoes) or "none"
                raise SchemaError(
                    f"'{nome}' is not a relation of {self.nome}.",
                    nota=f"it has: {conhecidas}",
                    doc="orm")
            self._carregar(linhas, relacao)
        return linhas

    def _carregar(self, linhas, relacao):
        alvo = REGISTRO.modelo(relacao.modelo)
        if alvo is None:
            raise SchemaError(
                f"model '{relacao.modelo}' is not registered.",
                dica="declare it before the model that points to it",
                doc="orm")

        if relacao.tipo in ("tem_muitos", "tem_um"):
            chaves = [l.get(relacao.chave_local) for l in linhas]
            chaves = [c for c in chaves if c is not None]
            if not chaves:
                for l in linhas:
                    l[relacao.nome] = [] if relacao.tipo == "tem_muitos" else None
                return

            filhos = Consulta(self.conexao, alvo.tabela) \
                .onde_em(relacao.chave_externa, sorted(set(chaves))).buscar()

            por_chave = {}
            for filho in filhos:
                por_chave.setdefault(
                    filho.get(relacao.chave_externa), []).append(
                        alvo._converter(filho))

            for linha in linhas:
                grupo = por_chave.get(linha.get(relacao.chave_local), [])
                linha[relacao.nome] = (grupo if relacao.tipo == "tem_muitos"
                                       else (grupo[0] if grupo else None))

        elif relacao.tipo == "pertence_a":
            chaves = [l.get(relacao.chave_local) for l in linhas]
            chaves = [c for c in chaves if c is not None]
            if not chaves:
                for l in linhas:
                    l[relacao.nome] = None
                return

            pais = Consulta(self.conexao, alvo.tabela) \
                .onde_em(relacao.chave_externa, sorted(set(chaves))).buscar()
            por_chave = {p.get(relacao.chave_externa): alvo._converter(p)
                         for p in pais}
            for linha in linhas:
                linha[relacao.nome] = por_chave.get(
                    linha.get(relacao.chave_local))

        elif relacao.tipo == "muitos_para_muitos":
            chaves = [l.get(self.chave) for l in linhas if l.get(self.chave)]
            if not chaves:
                for l in linhas:
                    l[relacao.nome] = []
                return

            pontes = Consulta(self.conexao, relacao.tabela_ponte) \
                .onde_em(relacao.chave_local, sorted(set(chaves))).buscar()
            ids_alvo = sorted({p[relacao.chave_externa] for p in pontes})
            if not ids_alvo:
                for l in linhas:
                    l[relacao.nome] = []
                return

            alvos = Consulta(self.conexao, alvo.tabela) \
                .onde_em(alvo.chave, ids_alvo).buscar()
            por_id = {a[alvo.chave]: alvo._converter(a) for a in alvos}

            agrupado = {}
            for ponte in pontes:
                agrupado.setdefault(ponte[relacao.chave_local], []).append(
                    por_id.get(ponte[relacao.chave_externa]))
            for linha in linhas:
                linha[relacao.nome] = [
                    x for x in agrupado.get(linha.get(self.chave), []) if x]

    # ── esquema ─────────────────────────────────────────────

    def sql_criar(self, dialeto=None):
        """O CREATE TABLE deste modelo."""
        d = dialeto or getattr(self.conexao, "dialeto", "sqlite")
        colunas = [c.sql(d) for c in self.campos.values()]

        estrangeiras = []
        for campo in self.campos.values():
            if campo.referencia:
                tabela, coluna = (campo.referencia.split(".") + ["id"])[:2]
                estrangeiras.append(
                    f'FOREIGN KEY ("{campo.nome}") '
                    f'REFERENCES "{tabela}" ("{coluna}")'
                    if d in ("postgres", "sqlite") else
                    f"FOREIGN KEY (`{campo.nome}`) "
                    f"REFERENCES `{tabela}` (`{coluna}`)")

        corpo = ",\n  ".join(colunas + estrangeiras)
        nome = (f'"{self.tabela}"' if d in ("postgres", "sqlite")
                else f"`{self.tabela}`")
        return f"CREATE TABLE IF NOT EXISTS {nome} (\n  {corpo}\n)"

    def sql_indices(self, dialeto=None):
        d = dialeto or getattr(self.conexao, "dialeto", "sqlite")
        saida = []
        for campo in self.campos.values():
            if campo.indice and not campo.unico and not campo.chave:
                nome = f"idx_{self.tabela}_{campo.nome}"
                citada = (f'"{self.tabela}"' if d != "mysql"
                          else f"`{self.tabela}`")
                coluna = (f'"{campo.nome}"' if d != "mysql"
                          else f"`{campo.nome}`")
                saida.append(
                    f"CREATE INDEX IF NOT EXISTS {nome} ON {citada} ({coluna})")
        return saida

    def migrar(self):
        """Cria a tabela e os indices, se ainda nao existirem."""
        self._exigir_conexao()
        self.conexao.executar(self.sql_criar())
        for sql in self.sql_indices():
            try:
                self.conexao.executar(sql)
            except (QueryError, DatabaseError):
                pass                                 # ja existia
        return self.tabela

    def diferenca(self):
        """O que a tabela tem a menos que o modelo.

        E o que uma migracao precisa saber. Comparar o modelo com a
        tabela de verdade e melhor que confiar num historico de
        arquivos, que diverge assim que alguem mexe no banco a mao.
        """
        self._exigir_conexao()
        try:
            existentes = {c["nome"] for c in self.conexao.colunas(self.tabela)}
        except (QueryError, DatabaseError):
            return {"tabela_falta": True, "colunas_faltando": list(self.campos)}

        if not existentes:
            return {"tabela_falta": True, "colunas_faltando": list(self.campos)}

        faltando = [n for n in self.campos if n not in existentes]
        sobrando = [n for n in existentes if n not in self.campos]
        return {"tabela_falta": False, "colunas_faltando": faltando,
                "colunas_a_mais": sobrando}

    def aplicar_diferenca(self):
        """Cria o que falta. Nunca apaga: perda de dado nao se automatiza."""
        d = self.diferenca()
        if d["tabela_falta"]:
            self.migrar()
            return {"criou_tabela": True, "colunas_criadas": []}

        criadas = []
        dialeto = getattr(self.conexao, "dialeto", "sqlite")
        for nome in d["colunas_faltando"]:
            campo = self.campos[nome]
            if campo.tipo == "Serial":
                continue
            tabela = (f'"{self.tabela}"' if dialeto != "mysql"
                      else f"`{self.tabela}`")
            self.conexao.executar(
                f"ALTER TABLE {tabela} ADD COLUMN {campo.sql(dialeto)}")
            criadas.append(nome)
        return {"criou_tabela": False, "colunas_criadas": criadas,
                "colunas_a_mais": d["colunas_a_mais"]}

    # ── auxiliares ──────────────────────────────────────────

    def _converter(self, linha):
        if not isinstance(linha, dict):
            return linha
        return {k: (self.campos[k].converter(v) if k in self.campos else v)
                for k, v in linha.items()}

    def _exigir_conexao(self):
        if self.conexao is None:
            raise SchemaError(
                f"model '{self.nome}' has no connection.",
                dica=("attach one:  Forge.ligar(modelo, db)  — or pass it "
                      "when declaring the model"),
                doc="orm")

    def __repr__(self):
        return f"<Modelo {self.nome} -> {self.tabela} ({len(self.campos)} campos)>"


# ═════════════════════════════════════════════════════════════
#  Registro de modelos
# ═════════════════════════════════════════════════════════════

class RegistroDeModelos:
    """Onde os modelos declarados ficam, para as relacoes se acharem."""

    def __init__(self):
        self.modelos = {}

    def registrar(self, modelo):
        self.modelos[modelo.nome] = modelo
        return modelo

    def modelo(self, nome):
        return self.modelos.get(nome)

    def todos(self):
        return list(self.modelos.values())

    def limpar(self):
        self.modelos.clear()

    def migrar_tudo(self, conexao=None):
        """Cria todas as tabelas, na ordem em que foram declaradas.

        A ordem importa quando ha chave estrangeira: a tabela apontada
        precisa existir antes da que aponta.
        """
        feitas = []
        for modelo in self.modelos.values():
            if conexao is not None:
                modelo.conexao = conexao
            modelo.migrar()
            feitas.append(modelo.tabela)
        return feitas


REGISTRO = RegistroDeModelos()


# ═════════════════════════════════════════════════════════════
#  Migracoes com historico
# ═════════════════════════════════════════════════════════════

class Migracoes:
    """Migracoes numeradas, com registro do que ja rodou.

    Guardar o historico NO BANCO, e nao num arquivo, e o que faz duas
    maquinas concordarem sobre o estado. Um arquivo de historico
    versionado diz o que deveria ter rodado; a tabela diz o que rodou.
    """

    TABELA = "_forge_migracoes"

    def __init__(self, conexao):
        self.conexao = conexao
        self.passos = []
        self._garantir_tabela()

    def _garantir_tabela(self):
        d = getattr(self.conexao, "dialeto", "sqlite")
        serial = sql_do_tipo("Serial", d)
        texto = sql_do_tipo("Texto", d)
        quando = sql_do_tipo("DataHora", d)
        self.conexao.executar(
            f"CREATE TABLE IF NOT EXISTS {self.TABELA} ("
            f"  id {serial},"
            f"  nome {texto} NOT NULL,"
            f"  aplicada_em {quando}"
            f")")

    def passo(self, nome, subir, descer=None):
        """Registra uma migracao. 'descer' e opcional, mas recomendado."""
        self.passos.append({"nome": nome, "subir": subir, "descer": descer})
        return self

    def aplicadas(self):
        linhas = self.conexao.consultar(
            f"SELECT nome FROM {self.TABELA} ORDER BY id")
        return [l["nome"] for l in linhas]

    def pendentes(self):
        feitas = set(self.aplicadas())
        return [p for p in self.passos if p["nome"] not in feitas]

    def subir(self, ate=""):
        """Roda as pendentes, em ordem, parando na primeira que falhar.

        Parar e o certo: continuar depois de uma falha deixa o banco
        num estado que nenhuma migracao previu.
        """
        feitas = []
        for passo in self.pendentes():
            try:
                passo["subir"](self.conexao)
            except Exception as e:                   # noqa: BLE001
                raise MigrationError(
                    f"migration '{passo['nome']}' failed: "
                    f"{getattr(e, 'message', e)}",
                    nota=(f"{len(feitas)} migration(s) applied before it"
                          if feitas else "it was the first one"),
                    dica="fix the migration and run again; the rest is untouched",
                    doc="orm") from None

            agora = datetime.datetime.now(datetime.timezone.utc)
            dialeto = getattr(self.conexao, "dialeto", "sqlite")
            Consulta(self.conexao, self.TABELA).inserir(
                {"nome": passo["nome"],
                 "aplicada_em": Campo("aplicada_em", "DataHora").para_banco(
                     agora, dialeto)})
            feitas.append(passo["nome"])
            if ate and passo["nome"] == ate:
                break
        return feitas

    def descer(self, quantas=1):
        """Desfaz as ultimas. So as que declararam como desfazer."""
        aplicadas = self.aplicadas()
        desfeitas = []
        for nome in reversed(aplicadas[-quantas:]):
            passo = next((p for p in self.passos if p["nome"] == nome), None)
            if passo is None or passo["descer"] is None:
                raise MigrationError(
                    f"migration '{nome}' has no way down.",
                    dica="declare it with  passo(nome, subir, descer)",
                    doc="orm")
            passo["descer"](self.conexao)
            Consulta(self.conexao, self.TABELA).onde("nome", nome).remover()
            desfeitas.append(nome)
        return desfeitas

    def estado(self):
        feitas = set(self.aplicadas())
        return {
            "aplicadas": len(feitas),
            "pendentes": len(self.pendentes()),
            "passos": [{"nome": p["nome"],
                        "aplicada": p["nome"] in feitas,
                        "reversivel": p["descer"] is not None}
                       for p in self.passos],
        }
