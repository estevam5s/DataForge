"""Onde a sessão mora — na memória, num SQLite ou em arquivos.

A sessão nasceu num dicionário do processo, e isso prende a aplicação a
um processo só: atrás de um balanceador, o segundo pedido da mesma
pessoa cai numa memória que nunca a viu. O contador volta a 1, o login
"cai" — sem erro, só às vezes, conforme o sorteio do balanceador.

O armazém separa a sessão do lugar onde ela é guardada:

| Armazém                 | Quem vê                              |
|-------------------------|--------------------------------------|
| `EmMemoria` (o padrão)  | este processo                        |
| `EmBanco`               | todo processo que abre o mesmo SQLite |
| `EmArquivos`            | todo processo que vê a mesma pasta    |
| um blueprint            | o que ele decidir (Redis, Postgres…)  |

─── O ciclo de um pedido ───────────────────────────────────────

    abrir(id)  →  a página roda sobre um dicionário comum  →  confirmar

A página nunca fala com o banco: `obter` e `definir` continuam sendo um
acesso a dicionário. Tudo é gravado UMA vez, no fim, e só o que mudou.

─── Por que comparar no fim, e não gravar em cada 'definir' ────

Porque `itens.append(x)` muda a sessão sem chamar `definir`. Na memória
isso sempre funcionou — o objeto é o mesmo —, e um armazém que gravasse
só no `definir` perderia a mudança calado. No fim do pedido cada valor é
codificado e comparado com a foto tirada ao abrir; o que difere é
gravado, o que sumiu é apagado.

─── Duas pessoas, o mesmo instante ─────────────────────────────

A gravação é POR CHAVE. Duas abas que mexem em chaves diferentes — uma no
carrinho, outra no tema — não apagam o trabalho uma da outra, porque cada
uma grava só a chave que mudou. Na MESMA chave, vence a última: é a
semântica que a memória já tinha, e `V.estado.somar` entre processos não
é atômico.

─── O que atravessa ────────────────────────────────────────────

Número, texto, lógico, void, Cluster, Vault (com chave de qualquer um
desses), Set, bytes e Decimal. Um record ou uma instância não: o tipo
vive no interpretador de um processo, e o outro não o conhece. A recusa
aparece NA PÁGINA, com a chave e o tipo, e o resto da sessão é gravado —
perder o login porque alguém guardou um objeto seria pior que o aviso.

─── O identificador ────────────────────────────────────────────

Um id que o armazém não conhece não vira sessão: vira uma NOVA, com id
sorteado. Aceitar o que o cliente inventou é fixação de sessão, e com a
sessão sobrevivendo ao processo o estrago dura mais. E só um id com a
forma de um sorteio (32 hexadecimais) chega ao armazém — em arquivos,
ele é nome de arquivo, e '../x' não pode ser.
"""

import base64
import json
import os
import re
import sqlite3
import threading
import time
import uuid
from decimal import Decimal

from .nucleo import Sessao

_ID = re.compile(r"[0-9a-f]{32}")


def id_valido(identificador):
    return isinstance(identificador, str) and _ID.fullmatch(identificador) is not None


def _novo_id():
    return uuid.uuid4().hex


# ═════════════════════════════════════════════════════════════
#  O que atravessa processo
# ═════════════════════════════════════════════════════════════

class NaoAtravessa(Exception):
    """Um valor da sessão que não tem forma fora deste processo."""

    def __init__(self, tipo):
        super().__init__(tipo)
        self.tipo = tipo


def _nome_do_tipo(valor):
    from ...interpreter import DFAction
    interp = DFAction._interpreter
    if interp is not None:
        try:
            return interp._type_of(valor)
        except Exception:                                   # noqa: BLE001
            pass
    return type(valor).__name__


def _para_json(valor, profundidade=0):
    if profundidade > 64:
        raise NaoAtravessa("uma estrutura funda demais (ou que contém a si mesma)")
    if valor is None or isinstance(valor, (bool, int, float, str)):
        return valor
    abaixo = profundidade + 1
    if isinstance(valor, list):
        return [_para_json(v, abaixo) for v in valor]
    if isinstance(valor, dict):
        if all(isinstance(k, str) and not k.startswith("$") for k in valor):
            return {k: _para_json(v, abaixo) for k, v in valor.items()}
        return {"$vault": [[_para_json(k, abaixo), _para_json(v, abaixo)]
                           for k, v in valor.items()]}
    if isinstance(valor, tuple):
        return {"$tupla": [_para_json(v, abaixo) for v in valor]}
    if isinstance(valor, (set, frozenset)):
        itens = [_para_json(v, abaixo) for v in valor]
        # ordem fixa: a foto de um conjunto que nao mudou nao pode mudar
        return {"$set": sorted(itens, key=lambda i: json.dumps(i, sort_keys=True))}
    if isinstance(valor, (bytes, bytearray)):
        return {"$bytes": base64.b64encode(bytes(valor)).decode("ascii")}
    if isinstance(valor, Decimal):
        return {"$decimal": str(valor)}
    raise NaoAtravessa(_nome_do_tipo(valor))


def _de_json(dado):
    if isinstance(dado, list):
        return [_de_json(v) for v in dado]
    if isinstance(dado, dict):
        if len(dado) == 1:
            (marca, conteudo), = dado.items()
            if marca == "$vault":
                return {_de_json(k): _de_json(v) for k, v in conteudo}
            if marca == "$tupla":
                return tuple(_de_json(v) for v in conteudo)
            if marca == "$set":
                return {_de_json(v) for v in conteudo}
            if marca == "$bytes":
                return base64.b64decode(conteudo)
            if marca == "$decimal":
                return Decimal(conteudo)
        return {k: _de_json(v) for k, v in dado.items()}
    return dado


def codificar(valor):
    """O texto que representa o valor fora do processo. Levanta NaoAtravessa."""
    return json.dumps(_para_json(valor), ensure_ascii=False, separators=(",", ":"))


def decodificar(texto):
    return _de_json(json.loads(texto))


# ═════════════════════════════════════════════════════════════
#  O contrato
# ═════════════════════════════════════════════════════════════

class Armazem:
    """O que a aplicação pede a quem guarda as sessões.

    `abrir` devolve a sessão, ou `None` se o id não existe; `nova` cria
    uma com id sorteado; `confirmar` grava o que mudou no pedido e devolve
    as recusas `[(chave, tipo)]`; `encerrar`, `vencer` e `contar` são a
    operação.
    """

    #: Se dois processos veem as mesmas sessões. A memória não.
    compartilhado = True

    def abrir(self, identificador):
        raise NotImplementedError

    def nova(self):
        raise NotImplementedError

    def confirmar(self, sessao):
        return []

    def encerrar(self, identificador):
        raise NotImplementedError

    def vencer(self, validade, agora=None):
        return 0

    def contar(self):
        return 0


class EmMemoria(Armazem):
    """O padrão: um dicionário deste processo. Não codifica nada."""

    compartilhado = False

    def __init__(self):
        self.sessoes = {}

    def abrir(self, identificador):
        sessao = self.sessoes.get(identificador)
        if sessao is not None:
            sessao.tocada_em = time.time()
        return sessao

    def nova(self):
        sessao = Sessao(_novo_id())
        self.sessoes[sessao.id] = sessao
        return sessao

    def encerrar(self, identificador):
        self.sessoes.pop(identificador, None)

    def vencer(self, validade, agora=None):
        agora = time.time() if agora is None else agora
        vencidas = [i for i, s in self.sessoes.items()
                    if agora - s.tocada_em > validade]
        for i in vencidas:
            del self.sessoes[i]
        return len(vencidas)

    def contar(self):
        return len(self.sessoes)


class _PorChave(Armazem):
    """A parte comum aos armazéns que guardam cada chave codificada.

    As subclasses sabem ler e escrever registros; esta sabe o que mudou.
    """

    def _ler(self, identificador):
        """(criada_em, {chave: texto}) ou None."""
        raise NotImplementedError

    def _escrever(self, identificador, criada_em, mudadas, removidas):
        raise NotImplementedError

    def abrir(self, identificador):
        registro = self._ler(identificador)
        if registro is None:
            return None
        criada_em, textos = registro
        sessao = Sessao(identificador)
        sessao.criada_em = criada_em
        dados = {}
        for chave, texto in textos.items():
            try:
                dados[chave] = decodificar(texto)
            except (ValueError, TypeError):
                # um registro corrompido perde a chave, e nao a sessao
                textos[chave] = None
        sessao.dados = dados
        sessao._fotos = dict(textos)
        return sessao

    def nova(self):
        sessao = Sessao(_novo_id())
        sessao._fotos = {}
        return sessao

    def confirmar(self, sessao):
        if getattr(sessao, "encerrada", False):
            return []
        fotos = getattr(sessao, "_fotos", None)
        if fotos is None:
            fotos = sessao._fotos = {}
        recusas, mudadas = [], {}
        with sessao._trava:
            pares = list(sessao.dados.items())
        presentes = set()
        for chave, valor in pares:
            presentes.add(chave)
            try:
                texto = codificar(valor)
            except NaoAtravessa as erro:
                recusas.append((chave, erro.tipo))
                continue
            if fotos.get(chave) != texto:
                mudadas[chave] = texto
        removidas = [c for c in fotos if c not in presentes]
        self._escrever(sessao.id, sessao.criada_em, mudadas, removidas)
        fotos.update(mudadas)
        for chave in removidas:
            fotos.pop(chave, None)
        return recusas


# ═════════════════════════════════════════════════════════════
#  SQLite
# ═════════════════════════════════════════════════════════════

class EmBanco(_PorChave):
    """Um arquivo SQLite que vários processos abrem.

    WAL deixa ler enquanto outro grava; `BEGIN IMMEDIATE` pega a trava de
    escrita no começo, e não no meio, que é onde duas gravações se
    atropelariam com 'database is locked'. Uma conexão por thread: o
    Kiln atende um pedido por thread, e uma conexão sqlite3 não se
    divide entre elas.
    """

    def __init__(self, caminho):
        caminho = _caminho_do_banco(caminho)
        self.caminho = caminho
        self._local = threading.local()
        _insistir(lambda: self._criar_tabelas())

    def _criar_tabelas(self):
        with self._conexao() as conexao:
            conexao.executescript("""
                CREATE TABLE IF NOT EXISTS df_vitrine_sessoes (
                    id TEXT PRIMARY KEY,
                    criada_em REAL NOT NULL,
                    tocada_em REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS df_vitrine_valores (
                    sessao TEXT NOT NULL,
                    chave TEXT NOT NULL,
                    valor TEXT NOT NULL,
                    PRIMARY KEY (sessao, chave));
                CREATE INDEX IF NOT EXISTS df_vitrine_tocada
                    ON df_vitrine_sessoes (tocada_em);
            """)

    def _conexao(self):
        conexao = getattr(self._local, "conexao", None)
        if conexao is None:
            conexao = sqlite3.connect(self.caminho, timeout=30,
                                      isolation_level=None,
                                      check_same_thread=False)
            # Trocar para WAL pede a trava exclusiva e NAO respeita o
            # timeout: dois processos subindo juntos — que e o caso de
            # uso — recebiam 'database is locked' na hora.
            _insistir(lambda: conexao.execute("PRAGMA journal_mode=WAL"))
            conexao.execute("PRAGMA synchronous=NORMAL")
            self._local.conexao = conexao
        return _Transacao(conexao)

    def _ler(self, identificador):
        with self._conexao() as conexao:
            linha = conexao.execute(
                "SELECT criada_em FROM df_vitrine_sessoes WHERE id = ?",
                (identificador,)).fetchone()
            if linha is None:
                return None
            textos = dict(conexao.execute(
                "SELECT chave, valor FROM df_vitrine_valores WHERE sessao = ?",
                (identificador,)).fetchall())
        return linha[0], textos

    def _escrever(self, identificador, criada_em, mudadas, removidas):
        with self._conexao().escrita() as conexao:
            conexao.execute(
                "INSERT INTO df_vitrine_sessoes (id, criada_em, tocada_em) "
                "VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                "tocada_em = excluded.tocada_em",
                (identificador, criada_em, time.time()))
            conexao.executemany(
                "INSERT INTO df_vitrine_valores (sessao, chave, valor) "
                "VALUES (?, ?, ?) ON CONFLICT(sessao, chave) DO UPDATE SET "
                "valor = excluded.valor",
                [(identificador, c, t) for c, t in mudadas.items()])
            conexao.executemany(
                "DELETE FROM df_vitrine_valores WHERE sessao = ? AND chave = ?",
                [(identificador, c) for c in removidas])

    def encerrar(self, identificador):
        with self._conexao().escrita() as conexao:
            conexao.execute("DELETE FROM df_vitrine_valores WHERE sessao = ?",
                            (identificador,))
            conexao.execute("DELETE FROM df_vitrine_sessoes WHERE id = ?",
                            (identificador,))

    def vencer(self, validade, agora=None):
        limite = (time.time() if agora is None else agora) - validade
        with self._conexao().escrita() as conexao:
            conexao.execute(
                "DELETE FROM df_vitrine_valores WHERE sessao IN "
                "(SELECT id FROM df_vitrine_sessoes WHERE tocada_em < ?)", (limite,))
            return conexao.execute(
                "DELETE FROM df_vitrine_sessoes WHERE tocada_em < ?",
                (limite,)).rowcount

    def contar(self):
        with self._conexao() as conexao:
            return conexao.execute(
                "SELECT COUNT(*) FROM df_vitrine_sessoes").fetchone()[0]


def _insistir(operacao, prazo=30.0):
    """Repete enquanto o SQLite disser que outro processo tem a trava."""
    fim = time.monotonic() + prazo
    espera = 0.01
    while True:
        try:
            return operacao()
        except sqlite3.OperationalError as erro:
            texto = str(erro).lower()
            if ("locked" not in texto and "busy" not in texto) \
                    or time.monotonic() > fim:
                raise
            time.sleep(espera)
            espera = min(espera * 2, 0.25)


class _Transacao:
    """`with` que lê sem transação, ou escreve dentro de BEGIN IMMEDIATE."""

    def __init__(self, conexao, escrever=False):
        self.conexao = conexao
        self.escrever = escrever

    def escrita(self):
        return _Transacao(self.conexao, True)

    def __enter__(self):
        if self.escrever:
            self.conexao.execute("BEGIN IMMEDIATE")
        return self.conexao

    def __exit__(self, tipo, erro, rastro):
        if self.escrever:
            self.conexao.execute("ROLLBACK" if tipo else "COMMIT")
        return False


def _caminho_do_banco(alvo):
    """Um caminho, ou a conexão do Arcane.Database — de onde se tira o arquivo."""
    if isinstance(alvo, dict) and alvo.get("__type__") == "DBConnection":
        linhas = alvo["_conn"].execute("PRAGMA database_list").fetchall()
        alvo = next((l[2] for l in linhas if l[1] == "main"), "")
    caminho = str(alvo or "")
    if not caminho or caminho == ":memory:" or caminho.startswith("file::memory:"):
        from ...errors import RuntimeError_
        raise RuntimeError_(
            "a sessao compartilhada precisa de um banco em ARQUIVO: um banco "
            "em memoria existe so dentro deste processo.", 0, 0,
            dica='V.sessoes_em_banco("sessoes.db") — o mesmo caminho em todo processo',
            doc="vitrine/producao")
    return caminho


# ═════════════════════════════════════════════════════════════
#  Arquivos
# ═════════════════════════════════════════════════════════════

class EmArquivos(_PorChave):
    """Um JSON por sessão, numa pasta que os processos dividem.

    A escrita toma a trava do arquivo da sessão, relê o que está lá, junta
    só as chaves que mudaram e troca o arquivo por inteiro com
    `os.replace` — atômico: quem lê vê o arquivo velho ou o novo, nunca
    a metade. A trava é do sistema (flock / msvcrt), e por isso vale
    entre processos e não só entre threads.
    """

    def __init__(self, pasta):
        self.pasta = os.path.abspath(str(pasta))
        os.makedirs(self.pasta, exist_ok=True)

    def _arquivo(self, identificador):
        if not id_valido(identificador):
            raise ValueError("identificador de sessao invalido")
        return os.path.join(self.pasta, identificador + ".json")

    def _ler(self, identificador):
        try:
            with open(self._arquivo(identificador), encoding="utf-8") as f:
                registro = json.load(f)
        except (OSError, ValueError):
            return None
        return registro.get("criada_em", time.time()), dict(registro.get("valores") or {})

    def _escrever(self, identificador, criada_em, mudadas, removidas):
        destino = self._arquivo(identificador)
        with _TravaDeArquivo(destino + ".trava"):
            atual = self._ler(identificador)
            valores = atual[1] if atual else {}
            valores.update(mudadas)
            for chave in removidas:
                valores.pop(chave, None)
            registro = {"criada_em": atual[0] if atual else criada_em,
                        "tocada_em": time.time(), "valores": valores}
            temporario = f"{destino}.{os.getpid()}.{threading.get_ident()}.tmp"
            with open(temporario, "w", encoding="utf-8") as f:
                json.dump(registro, f, ensure_ascii=False)
            os.replace(temporario, destino)

    def encerrar(self, identificador):
        if not id_valido(identificador):
            return
        destino = self._arquivo(identificador)
        with _TravaDeArquivo(destino + ".trava"):
            _remover(destino)
        _remover(destino + ".trava")

    def _sessoes(self):
        try:
            nomes = os.listdir(self.pasta)
        except OSError:
            return []
        return [n[:-5] for n in nomes if n.endswith(".json") and id_valido(n[:-5])]

    def vencer(self, validade, agora=None):
        limite = (time.time() if agora is None else agora) - validade
        vencidas = 0
        for identificador in self._sessoes():
            destino = self._arquivo(identificador)
            try:
                # o mtime e o do ultimo 'os.replace': toda confirmacao grava
                if os.path.getmtime(destino) < limite:
                    self.encerrar(identificador)
                    vencidas += 1
            except OSError:
                continue
        return vencidas

    def contar(self):
        return len(self._sessoes())


def _remover(caminho):
    try:
        os.remove(caminho)
    except OSError:
        pass


class _TravaDeArquivo:
    def __init__(self, caminho):
        self.caminho = caminho
        self._arquivo = None

    def __enter__(self):
        self._arquivo = open(self.caminho, "a+b")
        if os.name == "nt":
            import msvcrt
            while True:
                try:
                    self._arquivo.seek(0)
                    msvcrt.locking(self._arquivo.fileno(), msvcrt.LK_LOCK, 1)
                    break
                except OSError:
                    time.sleep(0.01)
        else:
            import fcntl
            fcntl.flock(self._arquivo.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *_):
        try:
            if os.name == "nt":
                import msvcrt
                self._arquivo.seek(0)
                msvcrt.locking(self._arquivo.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._arquivo.fileno(), fcntl.LOCK_UN)
        finally:
            self._arquivo.close()
        return False


# ═════════════════════════════════════════════════════════════
#  O armazém escrito em DataForge
# ═════════════════════════════════════════════════════════════

class DoUsuario(Armazem):
    """Um objeto com `carregar(id)`, `gravar(id, dados)` e `apagar(id)`.

    `vencer(segundos)` e `contar()` são opcionais. O contrato é de sessão
    inteira — `gravar` recebe o vault todo, a cada pedido —, porque é o
    que se escreve em cinco linhas sobre Redis ou uma tabela. Os valores
    chegam como estão: serializar é escolha de quem guarda.
    """

    def __init__(self, objeto):
        faltam = [m for m in ("carregar", "gravar", "apagar")
                  if not _tem_metodo(objeto, m)]
        if faltam:
            from ...errors import TypeError_
            raise TypeError_(
                f"sessoes_em precisa de um armazem com carregar(id), "
                f"gravar(id, dados) e apagar(id); falta {', '.join(faltam)}.",
                dica="V.sessoes_em_banco(caminho), V.sessoes_em_arquivos(pasta), "
                     "ou um blueprint com os tres metodos",
                doc="vitrine/producao")
        self.objeto = objeto

    def abrir(self, identificador):
        dados = _chamar(self.objeto, "carregar", identificador)
        if dados is None:
            return None
        sessao = Sessao(identificador)
        sessao.dados = dict(dados)
        return sessao

    def nova(self):
        return Sessao(_novo_id())

    def confirmar(self, sessao):
        if not getattr(sessao, "encerrada", False):
            with sessao._trava:
                dados = dict(sessao.dados)
            _chamar(self.objeto, "gravar", sessao.id, dados)
        return []

    def encerrar(self, identificador):
        _chamar(self.objeto, "apagar", identificador)

    def vencer(self, validade, agora=None):
        if _tem_metodo(self.objeto, "vencer"):
            return _chamar(self.objeto, "vencer", validade) or 0
        return 0

    def contar(self):
        if _tem_metodo(self.objeto, "contar"):
            return _chamar(self.objeto, "contar") or 0
        return 0


def _tem_metodo(objeto, nome):
    from ... import interpreter as i
    if isinstance(objeto, i.DFInstance):
        pendentes = [objeto.blueprint]
        while pendentes:
            molde = pendentes.pop()
            if nome in (molde.methods or {}):
                return True
            pendentes.extend(molde.parents or [])
        return False
    return callable(getattr(objeto, nome, None))


def _chamar(objeto, nome, *args):
    from ... import ast_nodes as ast
    from ... import interpreter as i
    if isinstance(objeto, i.DFInstance):
        interp = i.DFAction._interpreter
        no = ast.MethodCall(object=None, method=nome, args=[], kwargs={})
        return interp._chamar_metodo(objeto, list(args), {}, no, interp.global_env)
    return getattr(objeto, nome)(*args)


def resolver(alvo):
    """O armazém que 'sessoes_em' pede: None é a memória."""
    if alvo is None or isinstance(alvo, Armazem):
        return alvo
    return DoUsuario(alvo)
