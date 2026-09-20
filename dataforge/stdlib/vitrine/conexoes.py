"""Conexões e segredos — o que um painel precisa antes do primeiro dado.

Um painel começa lendo de algum lugar, e esse lugar precisa de uma
credencial. Duas coisas costumam dar errado aí, e as duas são caras:

1. **A conexão é reaberta a cada execução.** O programa roda inteiro a
   cada clique; abrir um banco por clique é o gargalo mais fácil de
   criar e o mais difícil de notar, porque cada abertura é rápida.
   `V.conexao` guarda a conexão **por processo** — é o `cache_resource`
   do Streamlit, com o nome do que ele faz.

2. **A credencial vai parar no código.** `V.segredos` lê um arquivo
   fora do repositório e as variáveis de ambiente, nessa ordem, e
   **nunca** aparece num `V.json(V.segredos())` sem que se peça: as
   chaves saem mascaradas.

O que este módulo NÃO é
-----------------------
Não é um ORM nem um pool. A conexão é a do `sqlite3`, e para os outros
bancos o caminho é `adopt Python.psycopg` ou `Arcane.Database` — o que
`V.conexao` acrescenta é o lugar onde ela mora e o cache das consultas.
"""

import os
import re
import threading

from . import componentes as C

_str = C._str

_TRAVA = threading.RLock()
#: nome -> conexão viva. Do processo, e não da sessão: uma conexão por
#: visitante é o jeito mais rápido de esgotar o banco.
_VIVAS = {}


# ═══════════════════════════════════════════════════════════
#  Conexões
# ═══════════════════════════════════════════════════════════

class Conexao:
    """Uma conexão viva, com consulta em cache.

        banco := V.conexao("vendas", arquivo := "dados/vendas.db")
        linhas := banco.consultar("SELECT * FROM pedidos WHERE mes = ?",
                                  [mes], validade := 300)

    `validade` é em segundos. Sem ela, a consulta roda **toda vez** —
    que é o certo para um painel que mostra o estado de agora, e errado
    para um relatório mensal que custa dois segundos.
    """

    def __init__(self, nome, conexao, tipo="sqlite"):
        self.nome = _str(nome)
        self.bruta = conexao
        self.tipo = _str(tipo)
        self._trava = threading.RLock()

    def consultar(self, sql, parametros=None, validade=None):
        """Roda a consulta e devolve um cluster de vaults."""
        if validade:
            from .api import _CACHE
            deposito = _CACHE.deposito(f"conexao:{self.nome}", teto=64,
                                       validade=float(validade),
                                       rotulo=f"conexao {self.nome}")
            chave = f"{sql}|{parametros!r}"
            valor, achou = deposito.obter(chave)
            if achou:
                return valor
            return deposito.guardar(chave, self._rodar(sql, parametros))
        return self._rodar(sql, parametros)

    def _rodar(self, sql, parametros):
        # A trava é do objeto, e não da consulta: uma conexão do
        # `sqlite3` não atravessa thread com segurança, e o Kiln atende
        # um pedido por thread. Sem ela, duas abas do mesmo painel dão
        # "recursive use of cursors" numa hora impossível de reproduzir.
        with self._trava:
            cursor = self.bruta.cursor()
            try:
                cursor.execute(str(sql), tuple(parametros or ()))
                if cursor.description is None:
                    self.bruta.commit()
                    return []
                nomes = [d[0] for d in cursor.description]
                return [dict(zip(nomes, linha)) for linha in cursor.fetchall()]
            finally:
                cursor.close()

    def executar(self, sql, parametros=None):
        """Escreve. Devolve quantas linhas mudaram."""
        with self._trava:
            cursor = self.bruta.cursor()
            try:
                cursor.execute(str(sql), tuple(parametros or ()))
                self.bruta.commit()
                return cursor.rowcount
            finally:
                cursor.close()

    def tabelas(self):
        """Os nomes das tabelas — para montar um explorador sem saber o schema."""
        if self.tipo != "sqlite":
            return []
        linhas = self._rodar(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name", None)
        return [l["name"] for l in linhas]

    def colunas(self, tabela):
        """As colunas de uma tabela, com tipo e obrigatoriedade."""
        if not _NOME_SEGURO.match(str(tabela)):
            from ...errors import RuntimeError_
            raise RuntimeError_(
                f"'{tabela}' nao parece um nome de tabela.", 0, 0,
                nota="o SQLite nao aceita nome de tabela por parametro, entao "
                     "ele vai cru para o SQL e precisa ser conferido antes",
                doc="vitrine/referencia")
        return [{"nome": l["name"], "tipo": l["type"],
                 "obrigatoria": bool(l["notnull"]), "chave": bool(l["pk"])}
                for l in self._rodar(f'PRAGMA table_info("{tabela}")', None)]

    def fechar(self):
        with _TRAVA:
            _VIVAS.pop(self.nome, None)
        try:
            self.bruta.close()
        except Exception:                                    # noqa: BLE001
            # Fechar duas vezes não pode virar erro de página: o
            # segundo `fechar` é o caso comum de um `defer` somado a
            # uma limpeza explícita.
            pass

    def __repr__(self):
        return f"<conexao {self.nome} ({self.tipo})>"


#: Nome de tabela ou coluna que pode ir cru para o SQL. A mesma regra
#: do `Arcane.Database`, e pelo mesmo motivo: o SQLite não aceita nome
#: por parâmetro, e o nome costuma chegar de uma escolha na tela.
_NOME_SEGURO = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")


def conexao(nome, arquivo="", tipo="sqlite", **opcoes):
    """Abre (ou devolve) uma conexão do processo.

        banco := V.conexao("app", arquivo := "dados/app.db")

    Chamar de novo com o mesmo nome devolve **a mesma** conexão. É por
    isso que ela recebe um nome: sem ele, cada execução da página
    abriria outra, e o programa que roda de cima para baixo não teria
    onde guardar a anterior.
    """
    chave = _str(nome)
    with _TRAVA:
        viva = _VIVAS.get(chave)
        if viva is not None:
            return viva
    aberta = _abrir(chave, _str(arquivo), _str(tipo), opcoes)
    with _TRAVA:
        # Duas threads podem ter aberto ao mesmo tempo; a segunda fecha
        # a sua e fica com a primeira, senão haveria duas conexões vivas
        # com o mesmo nome e uma delas nunca seria fechada.
        ja = _VIVAS.get(chave)
        if ja is not None:
            aberta.bruta.close()
            return ja
        _VIVAS[chave] = aberta
        return aberta


def _abrir(nome, arquivo, tipo, opcoes):
    if tipo != "sqlite":
        from ...errors import RuntimeError_
        raise RuntimeError_(
            f"V.conexao nao sabe abrir '{tipo}'.", 0, 0,
            nota="ela abre 'sqlite' por conta propria",
            dica="para outro banco, abra com 'adopt Python.<driver>' e passe a "
                 "conexao pronta em V.conexao_de(nome, conexao)",
            doc="vitrine/referencia")
    import sqlite3
    caminho = arquivo or ":memory:"
    if caminho != ":memory:":
        pasta = os.path.dirname(os.path.abspath(caminho))
        if pasta:
            os.makedirs(pasta, exist_ok=True)
    bruta = sqlite3.connect(
        caminho, check_same_thread=False,
        timeout=float(opcoes.get("espera", 20.0)))
    bruta.execute("PRAGMA foreign_keys = ON")
    return Conexao(nome, bruta, "sqlite")


def conexao_de(nome, bruta, tipo="externa"):
    """Registra uma conexão que **você** abriu.

    É a porta para Postgres, MySQL e o que mais existir: a Vitrine não
    reimplementa driver nenhum, e o que ela oferece — o lugar onde a
    conexão mora e o cache das consultas — vale igual para todos.
    """
    pronta = Conexao(nome, bruta, tipo)
    with _TRAVA:
        _VIVAS[_str(nome)] = pronta
    return pronta


def conexoes():
    """Os nomes das conexões vivas neste processo."""
    with _TRAVA:
        return sorted(_VIVAS)


def fechar_conexoes():
    with _TRAVA:
        vivas = list(_VIVAS.values())
    for c in vivas:
        c.fechar()
    return len(vivas)


# ═══════════════════════════════════════════════════════════
#  Segredos
# ═══════════════════════════════════════════════════════════

#: Onde procurar, em ordem. O primeiro que existir vence — e nenhum
#: deles deveria estar no repositório.
CAMINHOS = (".vitrine/segredos.toml", ".vitrine/segredos.json",
            "segredos.toml", ".env")

_SEGREDOS = {"carregado": False, "dados": {}, "de": ""}


def segredos(recarregar=False):
    """Todos os segredos, como vault. Leia uma chave com `V.segredo(...)`."""
    with _TRAVA:
        if _SEGREDOS["carregado"] and not recarregar:
            return dict(_SEGREDOS["dados"])
        dados, de = _ler_segredos()
        _SEGREDOS.update({"carregado": True, "dados": dados, "de": de})
        return dict(dados)


def segredo(chave, padrao=""):
    """Um segredo, do arquivo ou do ambiente.

    O **ambiente vence o arquivo**: é assim que um deploy troca a senha
    sem reescrever nada, e é o que a Vercel, o Docker e o systemd
    esperam. A ordem contrária faria um arquivo esquecido no servidor
    silenciar a configuração de produção.
    """
    nome = _str(chave)
    do_ambiente = os.environ.get(nome)
    if do_ambiente is not None:
        return do_ambiente
    atual = segredos()
    if "." in nome:
        secao, resto = nome.split(".", 1)
        dentro = atual.get(secao)
        if isinstance(dentro, dict):
            return dentro.get(resto, padrao)
    return atual.get(nome, padrao)


def origem_dos_segredos():
    """De qual arquivo eles vieram, ou vazio. Para um `V.saude()` honesto."""
    segredos()
    return _SEGREDOS["de"]


def segredos_mascarados():
    """As chaves, com o valor escondido. É o que pode aparecer na tela.

    Mostrar os quatro últimos caracteres é o suficiente para conferir
    *qual* chave está configurada — que é a pergunta real de quem está
    depurando — sem entregar a chave a quem está olhando a tela junto.
    """
    def mascarar(valor):
        if isinstance(valor, dict):
            return {k: mascarar(v) for k, v in valor.items()}
        texto = _str(valor)
        if len(texto) <= 4:
            return "••••"
        return "••••" + texto[-4:]

    return {k: mascarar(v) for k, v in segredos().items()}


def _ler_segredos():
    for caminho in CAMINHOS:
        if not os.path.isfile(caminho):
            continue
        try:
            texto = open(caminho, encoding="utf-8").read()
        except OSError:
            continue
        if caminho.endswith(".json"):
            import json
            try:
                return json.loads(texto), caminho
            except ValueError:
                continue
        return _toml_simples(texto), caminho
    return {}, ""


def _toml_simples(texto):
    """TOML de uma seção de profundidade, e `.env`, no mesmo laço.

    Não é um TOML completo: `tomllib` só existe a partir do Python 3.11
    e este projeto vale do 3.10 em diante, e trazer um analisador
    inteiro para ler `chave = "valor"` seria caro. O que ele não
    entende — vetor, tabela aninhada, multilinha — é **ignorado**, e
    não adivinhado.
    """
    dados, secao = {}, None
    for linha in texto.splitlines():
        limpa = linha.strip()
        if not limpa or limpa.startswith(("#", ";")):
            continue
        if limpa.startswith("[") and limpa.endswith("]"):
            secao = limpa[1:-1].strip()
            dados.setdefault(secao, {})
            continue
        if "=" not in limpa:
            continue
        chave, valor = limpa.split("=", 1)
        chave = chave.strip().strip('"').strip("'")
        valor = valor.strip()
        if valor[:1] in ('"', "'") and valor[-1:] == valor[:1]:
            valor = valor[1:-1]
        elif valor.lower() in ("true", "false"):
            valor = valor.lower() == "true"
        elif _e_numero(valor):
            valor = float(valor) if "." in valor else int(valor)
        if secao:
            dados[secao][chave] = valor
        else:
            dados[chave] = valor
    return dados


def _e_numero(texto):
    try:
        float(texto)
        return True
    except (TypeError, ValueError):
        return False
