"""Estado e cache.

Três lugares onde um valor pode morar, e a diferença entre eles é quem
enxerga:

| Onde        | Quem vê                | Some quando                 |
|-------------|------------------------|-----------------------------|
| `V.estado`  | uma sessão             | a sessão expira             |
| `V.geral`   | **todas** as sessões   | o processo termina          |
| `V.cache`   | todas, por argumento   | o TTL vence ou é invalidado |

O `V.geral` é compartilhado de verdade, com todos os perigos disso: se
duas sessões escrevem na mesma chave, uma perde. Ele tem trava, mas a
trava protege o dicionário, não a lógica de quem lê-e-depois-escreve.
Para contar, `V.geral.somar(chave, 1)`, que é atômico.
"""

import hashlib
import json
import os
import threading
import time

from .nucleo import Contexto


def _sessao():
    ctx = Contexto.atual()
    if ctx is None:
        from ...errors import RuntimeError_
        raise RuntimeError_(
            "V.estado so existe durante uma execucao da pagina.", 0, 0,
            dica="para um valor que atravessa sessoes, use V.geral",
            doc="tecnicas/vitrine")
    return ctx.sessao


class Estado:
    """O estado da sessão — o mesmo entre execuções do programa.

    É o que torna o modelo utilizável: sem ele, um contador voltaria a
    zero a cada clique, porque o programa roda do começo toda vez.
    """

    def obter(self, chave, padrao=None):
        return _sessao().obter(str(chave), padrao)

    def definir(self, chave, valor):
        return _sessao().definir(str(chave), valor)

    def existe(self, chave):
        return _sessao().existe(str(chave))

    def remover(self, chave):
        _sessao().remover(str(chave))

    def limpar(self):
        _sessao().limpar()

    def tudo(self):
        #: Sem as chaves internas: campo, formulário e arquivo enviado
        #: moram aqui, e mostrá-los num `V.json(V.estado.tudo())` seria
        #: um despejo ilegível.
        return {k: v for k, v in _sessao().tudo().items()
                if not k.startswith("__")}

    def padrao(self, chave, valor):
        """Define só se ainda não existe. Devolve o que vale agora.

        Substitui as três linhas que todo app escreve no começo:

            given no V.estado.existe("contador"):
                V.estado.definir("contador", 0)
        """
        sessao = _sessao()
        chave = str(chave)
        with sessao._trava:
            if chave not in sessao.dados:
                sessao.dados[chave] = valor
            return sessao.dados[chave]

    def somar(self, chave, quanto=1):
        """Incremento sem a corrida do ler-somar-escrever."""
        sessao = _sessao()
        chave = str(chave)
        with sessao._trava:
            atual = sessao.dados.get(chave, 0) or 0
            sessao.dados[chave] = atual + quanto
            return sessao.dados[chave]

    def id(self):
        return _sessao().id

    def idade(self):
        """Segundos desde que a sessão começou."""
        return round(time.time() - _sessao().criada_em, 3)


class Geral:
    """Estado do processo inteiro — todas as sessões veem o mesmo.

    Use com parcimônia: configuração, um contador de visitas, um modelo
    de ML carregado uma vez. **Não** use para o que pertence a um
    usuário, ou dois visitantes verão os dados um do outro — é o tipo de
    vazamento que não dá erro nenhum.
    """

    def __init__(self):
        self._dados = {}
        self._trava = threading.RLock()

    def obter(self, chave, padrao=None):
        with self._trava:
            return self._dados.get(str(chave), padrao)

    def definir(self, chave, valor):
        with self._trava:
            self._dados[str(chave)] = valor
        return valor

    def existe(self, chave):
        with self._trava:
            return str(chave) in self._dados

    def remover(self, chave):
        with self._trava:
            self._dados.pop(str(chave), None)

    def limpar(self):
        with self._trava:
            self._dados.clear()

    def tudo(self):
        with self._trava:
            return dict(self._dados)

    def padrao(self, chave, valor):
        with self._trava:
            return self._dados.setdefault(str(chave), valor)

    def somar(self, chave, quanto=1):
        with self._trava:
            atual = self._dados.get(str(chave), 0) or 0
            self._dados[str(chave)] = atual + quanto
            return self._dados[str(chave)]


# ═══════════════════════════════════════════════════════════
#  Cache
# ═══════════════════════════════════════════════════════════

class _Deposito:
    """Um cache com validade e teto — em memória, e opcionalmente em disco.

    O teto existe porque um cache sem limite é um vazamento com outro
    nome: uma função chamada com mil argumentos diferentes guarda mil
    resultados e nunca solta nenhum. Ao encher, sai o **menos usado
    recentemente**.
    """

    def __init__(self, teto=128, validade=None, pasta=None):
        self.teto = max(1, int(teto))
        self.validade = validade
        self.pasta = pasta
        self.rotulo = ""          # o nome da ação, para o relatório
        self._dados = {}          # chave -> (valor, gravado_em)
        self._ordem = []          # da menos usada para a mais usada
        self._trava = threading.RLock()
        self.acertos = 0
        self.erros = 0

    def obter(self, chave):
        with self._trava:
            item = self._dados.get(chave)
            if item is None and self.pasta:
                item = self._ler_do_disco(chave)
            if item is None:
                self.erros += 1
                return None, False
            valor, gravado = item
            if self.validade is not None and (time.time() - gravado) > self.validade:
                self._descartar(chave)
                self.erros += 1
                return None, False
            self.acertos += 1
            if chave in self._ordem:
                self._ordem.remove(chave)
            self._ordem.append(chave)
            return valor, True

    def guardar(self, chave, valor):
        with self._trava:
            self._dados[chave] = (valor, time.time())
            if chave in self._ordem:
                self._ordem.remove(chave)
            self._ordem.append(chave)
            while len(self._ordem) > self.teto:
                self._descartar(self._ordem[0])
            if self.pasta:
                self._gravar_no_disco(chave, valor)
        return valor

    def _descartar(self, chave):
        self._dados.pop(chave, None)
        if chave in self._ordem:
            self._ordem.remove(chave)
        if self.pasta:
            try:
                os.remove(self._arquivo(chave))
            except OSError:
                pass

    def limpar(self):
        with self._trava:
            self._dados.clear()
            self._ordem.clear()
            if self.pasta and os.path.isdir(self.pasta):
                for nome in os.listdir(self.pasta):
                    if nome.endswith(".json"):
                        try:
                            os.remove(os.path.join(self.pasta, nome))
                        except OSError:
                            pass

    def estatisticas(self):
        with self._trava:
            total = self.acertos + self.erros
            return {"itens": len(self._dados), "teto": self.teto,
                    "acertos": self.acertos, "erros": self.erros,
                    "taxa": round(self.acertos / total, 4) if total else 0.0}

    # ── Disco ────────────────────────────────────────────────
    #
    # Só o que o JSON aguenta. Guardar objeto arbitrário exigiria
    # pickle, e ler pickle de um arquivo que outro processo escreveu é
    # execução de código — num framework web, isso é a porta aberta.

    def _arquivo(self, chave):
        seguro = hashlib.sha256(chave.encode()).hexdigest()[:32]
        return os.path.join(self.pasta, f"{seguro}.json")

    def _ler_do_disco(self, chave):
        try:
            with open(self._arquivo(chave), encoding="utf-8") as f:
                pacote = json.load(f)
            return pacote["valor"], pacote["gravado_em"]
        except (OSError, ValueError, KeyError):
            return None

    def _gravar_no_disco(self, chave, valor):
        try:
            os.makedirs(self.pasta, exist_ok=True)
            with open(self._arquivo(chave), "w", encoding="utf-8") as f:
                json.dump({"valor": valor, "gravado_em": time.time()}, f)
        except (OSError, TypeError, ValueError):
            # Valor que não vira JSON continua valendo em memória. Falhar
            # aqui derrubaria a página por causa de uma otimização.
            pass


class Cache:
    """`mark @V.cache` sobre uma ação, e ela para de recalcular.

    Vale por argumento: `carregar("2026-01")` e `carregar("2026-02")`
    ocupam entradas diferentes.

        mark @V.cache
        action vendas(mes):
            yield Banco.consultar("SELECT …", [mes])

    Com ajustes:

        mark @V.cache(validade := 300, teto := 32)
        action cotacao(moeda):
            yield Http.get($"…/{moeda}").json()

    Em disco, para o que é caro e sobrevive a reiniciar:

        mark @V.cache(pasta := ".cache/ibge")
        action municipios():
            yield Http.get("…").json()
    """

    def __init__(self):
        self._depositos = {}
        self._trava = threading.RLock()

    def __call__(self, *args, **kwargs):
        """Decorador com e sem parênteses.

        `mark @V.cache` passa a ação; `mark @V.cache(validade := 60)`
        passa as opções e devolve o decorador de verdade.
        """
        if len(args) == 1 and not kwargs and callable(args[0]):
            return self._envolver(args[0], {})
        opcoes = dict(kwargs)
        if args and isinstance(args[0], dict):
            opcoes.update(args[0])
        return lambda alvo: self._envolver(alvo, opcoes)

    def _envolver(self, alvo, opcoes):
        nome = getattr(alvo, "name", None) or getattr(alvo, "__name__", "acao")
        # A identidade da ação entra na chave do depósito, e não só o
        # nome. Duas ações chamadas 'carregar' em arquivos diferentes
        # dividiriam o mesmo cache: uma receberia o resultado da outra,
        # e o 'teto' da primeira venceria calado sobre o da segunda.
        deposito = self.deposito(
            f"{nome}#{id(alvo):x}",
            teto=opcoes.get("teto", 128),
            validade=opcoes.get("validade", opcoes.get("ttl")),
            pasta=opcoes.get("pasta"),
            rotulo=nome)

        def embrulho(*a, **kw):
            chave = _chave_de(nome, a, kw)
            valor, achou = deposito.obter(chave)
            if achou:
                return valor
            return deposito.guardar(chave, alvo(*a, **kw))

        embrulho.__name__ = nome
        embrulho.__doc__ = getattr(alvo, "__doc__", None)
        #: O alvo e o depósito ficam alcançáveis: é o que permite
        #: `V.cache.invalidar(vendas)` e testar a ação sem o cache.
        embrulho.sem_cache = alvo
        embrulho.deposito = deposito
        embrulho.limpar = deposito.limpar
        return embrulho

    def deposito(self, nome, teto=128, validade=None, pasta=None, rotulo=""):
        with self._trava:
            if nome not in self._depositos:
                deposito = _Deposito(teto, validade, pasta)
                deposito.rotulo = rotulo or nome
                self._depositos[nome] = deposito
            return self._depositos[nome]

    def invalidar(self, quem=None):
        """Esquece tudo, ou só o de uma ação."""
        with self._trava:
            if quem is None:
                for d in self._depositos.values():
                    d.limpar()
                return
            deposito = getattr(quem, "deposito", None)
            if deposito is None:
                # Pelo nome, quando veio um texto. Esvazia todos os que
                # o usam: quem passa um nome quer dizer "esse cálculo",
                # e não uma das cópias dele.
                rotulo = (getattr(quem, "name", None)
                          or getattr(quem, "__name__", None) or str(quem))
                for d in self._depositos.values():
                    if getattr(d, "rotulo", "") == rotulo:
                        d.limpar()
                return
            deposito.limpar()

    def estatisticas(self):
        """Por ação, com o nome que quem escreveu reconhece."""
        with self._trava:
            return {getattr(d, "rotulo", nome): d.estatisticas()
                    for nome, d in self._depositos.items()}


def _chave_de(nome, args, kwargs):
    """A identidade de uma chamada.

    `repr` e não `str`: `"1"` e `1` são chamadas diferentes e
    precisam de entradas diferentes — com `str`, a segunda receberia o
    resultado da primeira, e seria um bug silencioso.
    """
    crua = f"{nome}|{args!r}|{sorted(kwargs.items())!r}"
    return hashlib.sha256(crua.encode()).hexdigest()[:24]
