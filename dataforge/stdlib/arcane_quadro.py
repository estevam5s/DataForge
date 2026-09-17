# -*- coding: utf-8 -*-
"""Arcane.Quadro — a tabela de dados da linguagem.

Por que um terceiro quadro, se já havia dois
--------------------------------------------
Havia `Arcane.Analytics.DataFrame` e `Arcane.Data.Frame`: **duas classes
independentes**, com `group_by`, `describe`, `normalize`, `merge` e
`pivot` implementados duas vezes. E elas divergiam — `describe` devolvia
chaves diferentes conforme o módulo adotado:

    Analytics: {count, mean, std, min, 25%, 50%, 75%, max, sum, variance}
    Data:      {count, mean, median, min, max, std, variance, sum}

Duas respostas para "descreva estes dados" na mesma linguagem é o defeito
que este repositório já pagou três vezes (a resolução de módulo, a tabela
da stdlib, o grafo de imports). `Quadro` é a resposta única, e as duas
antigas continuam funcionando — quebrar código que existe seria pior.

As cinco decisões
-----------------
1. **A linha é um vault.** É a forma que o resto da linguagem já usa:
   `IO.read_csv(caminho, yes)` devolve vaults, `Database.query` devolve
   vaults, e o `>> sift`/`morph` já sabe percorrê-los. Um quadro que
   falasse outra língua obrigaria a converter em toda fronteira.

2. **Por dentro é COLUNAR.** Cada coluna é um cluster, e a linha é
   montada na saída. É o que torna `descrever`, `normalizar` e
   `correlacao` uma passada por coluna em vez de uma por célula — e é o
   que o documento pede em "columnar storage".

3. **Todo verbo devolve um quadro NOVO.** Como `record` e `with`: o
   original nunca muda. É o que permite comparar o antes e o depois, e o
   que torna um pipeline reexecutável.

4. **A ausência tem um nome só: `void`.** Texto vazio, `NaN` e `None` são
   três jeitos de dizer a mesma coisa, e tratá-los como coisas
   diferentes é de onde vem metade do bug de limpeza de dados.

5. **Coluna que não existe é ERRO, com sugestão.** `q.pegar("nme")`
   responde o que tem perto, como o analisador faz com nomes. Devolver
   uma coluna vazia calada é o jeito mais rápido de um relatório sair
   errado sem ninguém notar.
"""

import csv as _csv
import io as _io
import json as _json
import math as _math

from ..errors import RuntimeError_

DOC = "dados/quadro"


# ═════════════════════════════════════════════════════════════
#  Erros
# ═════════════════════════════════════════════════════════════

def _erro(mensagem, nota="", dica=""):
    return RuntimeError_(mensagem, 0, 0, nota=nota, dica=dica, doc=DOC)


def _parecido(nome, candidatos):
    """A coluna mais parecida, como o analisador faz com nomes."""
    import difflib
    perto = difflib.get_close_matches(str(nome), [str(c) for c in candidatos],
                                      n=1, cutoff=0.6)
    return perto[0] if perto else ""


# ═════════════════════════════════════════════════════════════
#  O que conta como ausente
# ═════════════════════════════════════════════════════════════

def _ausente(valor):
    """`void`, texto vazio e NaN são a MESMA ausência.

    Tratá-los como coisas diferentes é de onde vem metade do bug de
    limpeza: um CSV traz `""`, um JSON traz `null`, e uma conta que
    falhou traz `NaN` — e todos os três significam "não sei".
    """
    if valor is None:
        return True
    if isinstance(valor, str) and not valor.strip():
        return True
    if isinstance(valor, float) and _math.isnan(valor):
        return True
    return False


def _numerico(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _numeros(valores):
    """Só os números, descartando a ausência. Não converte texto."""
    return [v for v in valores if _numerico(v) and not _ausente(v)]


# ═════════════════════════════════════════════════════════════
#  As agregações, num lugar só
# ═════════════════════════════════════════════════════════════
#
# A tabela e' fechada de proposito: 'resumir' recebe o nome da agregacao
# como TEXTO, e um nome desconhecido tem de ser recusado com a lista do
# que existe. Aceitar qualquer callable abriria a porta para injecao de
# nome vindo de fora (um '?agregar=' de uma tela, por exemplo).

def _soma(vs):
    ns = _numeros(vs)
    return sum(ns) if ns else 0


def _media(vs):
    ns = _numeros(vs)
    return sum(ns) / len(ns) if ns else None


def _mediana(vs):
    ns = sorted(_numeros(vs))
    if not ns:
        return None
    meio = len(ns) // 2
    return ns[meio] if len(ns) % 2 else (ns[meio - 1] + ns[meio]) / 2


def _desvio(vs):
    ns = _numeros(vs)
    if len(ns) < 2:
        return 0.0
    m = sum(ns) / len(ns)
    return _math.sqrt(sum((x - m) ** 2 for x in ns) / (len(ns) - 1))


def _variancia(vs):
    d = _desvio(vs)
    return d * d


def _primeiro(vs):
    return vs[0] if vs else None


def _ultimo(vs):
    return vs[-1] if vs else None


AGREGACOES = {
    "soma": _soma,
    "media": _media,
    "mediana": _mediana,
    "minimo": lambda vs: min(_numeros(vs)) if _numeros(vs) else None,
    "maximo": lambda vs: max(_numeros(vs)) if _numeros(vs) else None,
    "contagem": len,
    "contagem_valida": lambda vs: len([v for v in vs if not _ausente(v)]),
    "distintos": lambda vs: len({_chave(v) for v in vs}),
    "desvio": _desvio,
    "variancia": _variancia,
    "primeiro": _primeiro,
    "ultimo": _ultimo,
    "juntar": lambda vs: ", ".join(str(v) for v in vs if not _ausente(v)),
    "lista": list,
}


def _chave(valor):
    """Um valor como chave de agrupamento — cluster e vault viram texto."""
    if isinstance(valor, (list, dict)):
        return _json.dumps(valor, sort_keys=True, default=str)
    return valor


# ═════════════════════════════════════════════════════════════
#  O Quadro
# ═════════════════════════════════════════════════════════════

class Quadro:
    """Uma tabela: colunas nomeadas, linhas como vault.

    Imutável — todo verbo devolve um quadro novo.
    """

    __slots__ = ("_colunas", "_dados", "__weakref__")

    def __init__(self, colunas=None, dados=None):
        #: A ORDEM das colunas é a que veio, e ela importa: um CSV
        #: gravado com as colunas embaralhadas não é o mesmo arquivo.
        self._colunas = list(colunas or [])
        self._dados = {c: list(dados.get(c, [])) for c in self._colunas} \
            if dados else {c: [] for c in self._colunas}

    # ── nascer ───────────────────────────────────────────────

    @staticmethod
    def de_vaults(linhas):
        """A partir de um cluster de vaults — a forma nativa da linguagem."""
        linhas = list(linhas or [])
        colunas = []
        for linha in linhas:
            if not isinstance(linha, dict):
                raise _erro(
                    "cada linha precisa ser um vault",
                    nota=f"recebi {type(linha).__name__.replace('dict', 'vault')}",
                    dica='Quadro.de_vaults([{"nome": "Ana"}, {"nome": "Bruno"}])')
            for c in linha:
                if c not in colunas:
                    colunas.append(c)
        dados = {c: [linha.get(c) for linha in linhas] for c in colunas}
        return Quadro(colunas, dados)

    @staticmethod
    def de_colunas(vault):
        """A partir de um vault de clusters — a forma colunar."""
        if not isinstance(vault, dict):
            raise _erro("'de_colunas' precisa de um vault de clusters",
                        dica='de_colunas({"nome": ["Ana"], "idade": [30]})')
        colunas = list(vault)
        tamanhos = {c: len(list(vault[c])) for c in colunas}
        if len(set(tamanhos.values())) > 1:
            maior = max(tamanhos, key=lambda c: tamanhos[c])
            menor = min(tamanhos, key=lambda c: tamanhos[c])
            raise _erro(
                "as colunas têm tamanhos diferentes",
                nota=f"'{maior}' tem {tamanhos[maior]} e "
                     f"'{menor}' tem {tamanhos[menor]}",
                dica="um quadro é retangular: complete a coluna curta com void")
        return Quadro(colunas, {c: list(vault[c]) for c in colunas})

    @staticmethod
    def de_csv(caminho, separador=",", tipos=True):
        """Lê um CSV. A primeira linha é o cabeçalho.

        Com `tipos := yes` (o padrão), texto que é número vira número —
        um CSV traz tudo como texto, e somar coluna de texto é o primeiro
        engano de quem chega.
        """
        with _io.open(caminho, encoding="utf-8", newline="") as f:
            linhas = list(_csv.DictReader(f, delimiter=separador))
        q = Quadro.de_vaults(linhas)
        return q.inferir_tipos() if tipos else q

    @staticmethod
    def de_json(caminho):
        with _io.open(caminho, encoding="utf-8") as f:
            dado = _json.load(f)
        if isinstance(dado, dict):
            return Quadro.de_colunas(dado)
        return Quadro.de_vaults(dado)

    @staticmethod
    def vazio(colunas=None):
        return Quadro(list(colunas or []), None)

    # ── olhar ────────────────────────────────────────────────

    def colunas(self):
        return list(self._colunas)

    def altura(self):
        return len(self._dados[self._colunas[0]]) if self._colunas else 0

    def largura(self):
        return len(self._colunas)

    def forma(self):
        return [self.altura(), self.largura()]

    def coluna(self, nome):
        self._exigir(nome)
        return list(self._dados[nome])

    def linha(self, i):
        n = self.altura()
        if not -n <= i < n:
            raise _erro(f"a linha {i} não existe",
                        nota=f"o quadro tem {n} linha(s)",
                        dica="confira com  len(q)  antes de indexar")
        return {c: self._dados[c][i] for c in self._colunas}

    def topo(self, n=5):
        return self._fatia(0, n)

    def fim(self, n=5):
        return self._fatia(max(0, self.altura() - n), self.altura())

    def fatiar(self, inicio, fim=None):
        return self._fatia(inicio, self.altura() if fim is None else fim)

    def amostra(self, n=5, semente=None):
        """Uma amostra aleatória. Com semente, sempre a mesma."""
        import random
        gerador = random.Random(semente)
        indices = sorted(gerador.sample(range(self.altura()),
                                        min(n, self.altura())))
        return self._por_indices(indices)

    def para_vaults(self):
        return [self.linha(i) for i in range(self.altura())]

    def para_colunas(self):
        return {c: list(self._dados[c]) for c in self._colunas}

    # ── escolher ─────────────────────────────────────────────

    def pegar(self, *nomes):
        """As colunas pedidas, nessa ordem."""
        nomes = _achatar(nomes)
        for n in nomes:
            self._exigir(n)
        return Quadro(nomes, {n: list(self._dados[n]) for n in nomes})

    def sem(self, *nomes):
        """Todas menos as pedidas."""
        nomes = set(_achatar(nomes))
        for n in nomes:
            self._exigir(n)
        ficam = [c for c in self._colunas if c not in nomes]
        return Quadro(ficam, {c: list(self._dados[c]) for c in ficam})

    def renomear(self, de_para):
        if not isinstance(de_para, dict):
            raise _erro("'renomear' precisa de um vault",
                        dica='renomear({"nome_antigo": "nome_novo"})')
        for antigo in de_para:
            self._exigir(antigo)
        novos = [de_para.get(c, c) for c in self._colunas]
        if len(set(novos)) != len(novos):
            raise _erro("renomear deixaria duas colunas com o mesmo nome",
                        dica="um quadro não pode ter nomes repetidos")
        return Quadro(novos, {de_para.get(c, c): list(self._dados[c])
                              for c in self._colunas})

    def onde(self, teste):
        """As linhas em que o teste dá `yes`.

        O teste recebe a LINHA como vault: `lambda l: l["idade"] bigger 18`.
        """
        indices = [i for i in range(self.altura())
                   if _verdade(teste(self.linha(i)))]
        return self._por_indices(indices)

    def ordenar(self, por, decrescente=False):
        """Ordena por uma ou mais colunas. A ausência vai para o fim."""
        chaves = _achatar([por])
        for c in chaves:
            self._exigir(c)

        def ordem(i):
            return tuple(_ordenavel(self._dados[c][i]) for c in chaves)

        indices = sorted(range(self.altura()), key=ordem,
                         reverse=bool(decrescente))
        return self._por_indices(indices)

    def distintas(self, por=None):
        """Sem linhas repetidas. Sem argumento, compara a linha inteira."""
        chaves = _achatar([por]) if por else list(self._colunas)
        for c in chaves:
            self._exigir(c)
        vistos, indices = set(), []
        for i in range(self.altura()):
            marca = tuple(_chave(self._dados[c][i]) for c in chaves)
            if marca not in vistos:
                vistos.add(marca)
                indices.append(i)
        return self._por_indices(indices)

    sem_duplicadas = distintas

    def duplicadas(self, por=None):
        """Só as linhas que repetem — o contrário de `distintas`."""
        chaves = _achatar([por]) if por else list(self._colunas)
        for c in chaves:
            self._exigir(c)
        contagem = {}
        for i in range(self.altura()):
            marca = tuple(_chave(self._dados[c][i]) for c in chaves)
            contagem[marca] = contagem.get(marca, 0) + 1
        indices = [i for i in range(self.altura())
                   if contagem[tuple(_chave(self._dados[c][i])
                                     for c in chaves)] > 1]
        return self._por_indices(indices)

    # ── mudar ────────────────────────────────────────────────

    def com(self, nome, valor_ou_acao):
        """Uma coluna nova — ou a substituição de uma que existe.

        O segundo argumento é um valor (a coluna inteira recebe ele), um
        cluster do tamanho certo, ou uma ação que recebe a linha.
        """
        n = self.altura()
        if callable(valor_ou_acao):
            coluna = [valor_ou_acao(self.linha(i)) for i in range(n)]
        elif isinstance(valor_ou_acao, list):
            if len(valor_ou_acao) != n:
                raise _erro(
                    f"a coluna '{nome}' tem {len(valor_ou_acao)} valores, "
                    f"e o quadro tem {n} linhas",
                    dica="um quadro é retangular")
            coluna = list(valor_ou_acao)
        else:
            coluna = [valor_ou_acao] * n

        colunas = list(self._colunas)
        if nome not in colunas:
            colunas.append(nome)
        dados = {c: list(self._dados[c]) for c in self._colunas}
        dados[nome] = coluna
        return Quadro(colunas, dados)

    def mapear(self, nome, acao):
        """Aplica uma ação a cada valor de uma coluna."""
        self._exigir(nome)
        return self.com(nome, [acao(v) for v in self._dados[nome]])

    def converter(self, tipos):
        """Converte colunas: `{"idade": "Integer", "preco": "Float"}`.

        Um valor que não converte vira `void` — e a contagem de quantos
        não converteram fica em `perfil()`. Levantar na primeira célula
        ruim de um CSV de um milhão de linhas não ajuda ninguém.
        """
        if not isinstance(tipos, dict):
            raise _erro("'converter' precisa de um vault",
                        dica='converter({"idade": "Integer"})')
        q = self
        for coluna, tipo in tipos.items():
            self._exigir(coluna)
            conversor = _CONVERSORES.get(str(tipo))
            if conversor is None:
                raise _erro(
                    f"não sei converter para '{tipo}'",
                    nota=f"os tipos são: {', '.join(sorted(_CONVERSORES))}",
                    dica='converter({"idade": "Integer"})')
            q = q.com(coluna, [conversor(v) for v in q._dados[coluna]])
        return q

    def inferir_tipos(self):
        """Texto que é número vira número, coluna por coluna.

        Só converte a coluna INTEIRA, e nunca pela metade: uma coluna com
        `["1", "2", "n/a"]` fica como está. Converter o que dá e deixar o
        resto como texto produziria uma coluna de dois tipos, que é pior
        que uma de um tipo errado.
        """
        q = self
        for coluna in self._colunas:
            valores = self._dados[coluna]
            uteis = [v for v in valores if not _ausente(v)]
            if not uteis or not all(isinstance(v, str) for v in uteis):
                continue
            if all(_e_inteiro(v) for v in uteis):
                q = q.com(coluna, [None if _ausente(v) else int(v)
                                   for v in valores])
            elif all(_e_decimal(v) for v in uteis):
                q = q.com(coluna, [None if _ausente(v) else float(v)
                                   for v in valores])
        return q

    # ── ausência ─────────────────────────────────────────────

    def nulos(self):
        """Quantos valores ausentes por coluna."""
        return {c: sum(1 for v in self._dados[c] if _ausente(v))
                for c in self._colunas}

    def sem_nulos(self, colunas=None):
        """As linhas sem ausência — em todas as colunas, ou só nas pedidas."""
        alvo = _achatar([colunas]) if colunas else list(self._colunas)
        for c in alvo:
            self._exigir(c)
        indices = [i for i in range(self.altura())
                   if not any(_ausente(self._dados[c][i]) for c in alvo)]
        return self._por_indices(indices)

    def preencher(self, valor):
        """Preenche a ausência. Aceita um valor, ou um vault por coluna.

        `"media"`, `"mediana"`, `"anterior"` e `"seguinte"` são
        reconhecidos como estratégia, e não como o texto a gravar.
        """
        por_coluna = valor if isinstance(valor, dict) else \
            {c: valor for c in self._colunas}
        q = self
        for coluna, como in por_coluna.items():
            self._exigir(coluna)
            q = q.com(coluna, _preencher(q._dados[coluna], como))
        return q

    # ── agrupar ──────────────────────────────────────────────

    def agrupar(self, por):
        """Agrupa por uma ou mais colunas. Devolve um `Grupo`."""
        chaves = _achatar([por])
        for c in chaves:
            self._exigir(c)
        return Grupo(self, chaves)

    def resumir(self, agregacoes):
        """Agrega o quadro inteiro, sem agrupar."""
        return Grupo(self, []).resumir(agregacoes)

    def contar_valores(self, coluna):
        """Quantas vezes cada valor aparece, do mais comum ao menos."""
        self._exigir(coluna)
        contagem = {}
        for v in self._dados[coluna]:
            k = _chave(v)
            contagem[k] = contagem.get(k, 0) + 1
        pares = sorted(contagem.items(), key=lambda p: (-p[1], str(p[0])))
        return Quadro([coluna, "contagem"],
                      {coluna: [p[0] for p in pares],
                       "contagem": [p[1] for p in pares]})

    def tabela_cruzada(self, linha, coluna):
        """Contagem cruzada de duas colunas."""
        self._exigir(linha)
        self._exigir(coluna)
        valores_col = []
        for v in self._dados[coluna]:
            k = _chave(v)
            if k not in valores_col:
                valores_col.append(k)
        valores_col.sort(key=str)

        linhas = {}
        for i in range(self.altura()):
            a = _chave(self._dados[linha][i])
            b = _chave(self._dados[coluna][i])
            linhas.setdefault(a, {c: 0 for c in valores_col})
            linhas[a][b] += 1

        ordenadas = sorted(linhas, key=str)
        dados = {linha: list(ordenadas)}
        for c in valores_col:
            dados[str(c)] = [linhas[a][c] for a in ordenadas]
        return Quadro([linha] + [str(c) for c in valores_col], dados)

    def pivotar(self, linha, coluna, valor, agregacao="soma"):
        """Linhas viram colunas — a tabela dinâmica."""
        for c in (linha, coluna, valor):
            self._exigir(c)
        agrega = _agregacao(agregacao)

        chaves_col = []
        for v in self._dados[coluna]:
            k = _chave(v)
            if k not in chaves_col:
                chaves_col.append(k)
        chaves_col.sort(key=str)

        baldes = {}
        for i in range(self.altura()):
            a = _chave(self._dados[linha][i])
            b = _chave(self._dados[coluna][i])
            baldes.setdefault(a, {}).setdefault(b, []).append(
                self._dados[valor][i])

        ordenadas = sorted(baldes, key=str)
        dados = {linha: list(ordenadas)}
        for c in chaves_col:
            dados[str(c)] = [agrega(baldes[a].get(c, [])) for a in ordenadas]
        return Quadro([linha] + [str(c) for c in chaves_col], dados)

    def despivotar(self, fixas, nome="variavel", valor="valor"):
        """O contrário do pivô: colunas viram linhas."""
        fixas = _achatar([fixas])
        for c in fixas:
            self._exizir(c) if False else self._exigir(c)
        moveis = [c for c in self._colunas if c not in fixas]
        linhas = []
        for i in range(self.altura()):
            base = {c: self._dados[c][i] for c in fixas}
            for c in moveis:
                linhas.append({**base, nome: c, valor: self._dados[c][i]})
        return Quadro.de_vaults(linhas)

    # ── juntar ───────────────────────────────────────────────

    def juntar(self, outro, em, tipo="dentro"):
        """Junta dois quadros por uma chave.

        `tipo`: "dentro" (só o que casa), "esquerda", "direita" ou
        "fora". São os quatro `JOIN` do SQL, com os nomes da linguagem.
        """
        if not isinstance(outro, Quadro):
            raise _erro("'juntar' precisa de outro quadro",
                        dica="q.juntar(outro, em := \"id\")")
        chaves = _achatar([em])
        for c in chaves:
            self._exigir(c)
            outro._exigir(c)
        if tipo not in ("dentro", "esquerda", "direita", "fora"):
            raise _erro(f"tipo de junção desconhecido: '{tipo}'",
                        nota="os tipos são: dentro, esquerda, direita, fora",
                        dica='q.juntar(outro, em := "id", tipo := "esquerda")')

        indice = {}
        for i in range(outro.altura()):
            marca = tuple(_chave(outro._dados[c][i]) for c in chaves)
            indice.setdefault(marca, []).append(i)

        so_do_outro = [c for c in outro._colunas if c not in chaves]
        linhas = []
        casados = set()
        for i in range(self.altura()):
            marca = tuple(_chave(self._dados[c][i]) for c in chaves)
            esquerda = self.linha(i)
            achados = indice.get(marca, [])
            if achados:
                casados.add(marca)
                for j in achados:
                    direita = {c: outro._dados[c][j] for c in so_do_outro}
                    linhas.append({**esquerda, **direita})
            elif tipo in ("esquerda", "fora"):
                linhas.append({**esquerda, **{c: None for c in so_do_outro}})

        if tipo in ("direita", "fora"):
            so_daqui = [c for c in self._colunas if c not in chaves]
            for j in range(outro.altura()):
                marca = tuple(_chave(outro._dados[c][j]) for c in chaves)
                if marca in casados:
                    continue
                linha = {c: outro._dados[c][j] for c in outro._colunas}
                linhas.append({**{c: None for c in so_daqui}, **linha})

        if not linhas:
            return Quadro(self._colunas + so_do_outro, None)
        return Quadro.de_vaults(linhas)

    def empilhar(self, outro):
        """Um quadro embaixo do outro. Coluna que falta de um lado vira void."""
        if not isinstance(outro, Quadro):
            raise _erro("'empilhar' precisa de outro quadro")
        return Quadro.de_vaults(self.para_vaults() + outro.para_vaults())

    # ── escala e feições ─────────────────────────────────────

    def normalizar(self, colunas=None):
        """Para a faixa 0..1. Coluna constante vira 0."""
        return self._escalar(colunas, _normalizar)

    def padronizar(self, colunas=None):
        """Média 0, desvio 1."""
        return self._escalar(colunas, _padronizar)

    def codificar(self, coluna, prefixo=None):
        """Uma coluna categórica vira uma coluna 0/1 por valor."""
        self._exigir(coluna)
        prefixo = coluna if prefixo is None else prefixo
        valores = []
        for v in self._dados[coluna]:
            k = _chave(v)
            if k not in valores:
                valores.append(k)
        valores.sort(key=str)
        q = self.sem(coluna)
        for v in valores:
            q = q.com(f"{prefixo}_{v}",
                      [1 if _chave(x) == v else 0 for x in self._dados[coluna]])
        return q

    def discretizar(self, coluna, faixas=5, nomes=None):
        """Números viram faixas — o `bin` da estatística."""
        self._exigir(coluna)
        ns = _numeros(self._dados[coluna])
        if not ns:
            raise _erro(f"a coluna '{coluna}' não tem número para discretizar")
        menor, maior = min(ns), max(ns)
        largura = (maior - menor) / faixas if maior > menor else 1.0

        def balde(v):
            if _ausente(v) or not _numerico(v):
                return None
            i = min(int((v - menor) / largura), faixas - 1)
            if nomes:
                return nomes[min(i, len(nomes) - 1)]
            inicio = menor + i * largura
            return f"[{_curto(inicio)}, {_curto(inicio + largura)})"

        return self.com(coluna, [balde(v) for v in self._dados[coluna]])

    # ── estatística ──────────────────────────────────────────

    def descrever(self):
        """Contagem, média, desvio, mínimo, quartis e máximo por coluna numérica.

        **Um contrato só.** `Arcane.Analytics.describe` e
        `Arcane.Data.describe` devolviam chaves diferentes para a mesma
        pergunta; este é o formato único, e ele traz os quartis porque é
        deles que se lê a assimetria.
        """
        linhas = []
        for c in self._colunas:
            ns = _numeros(self._dados[c])
            if not ns:
                continue
            ordenados = sorted(ns)
            linhas.append({
                "coluna": c,
                "contagem": len(ns),
                "ausentes": sum(1 for v in self._dados[c] if _ausente(v)),
                "media": sum(ns) / len(ns),
                "desvio": _desvio(ns),
                "minimo": ordenados[0],
                "q1": _percentil(ordenados, 25),
                "mediana": _percentil(ordenados, 50),
                "q3": _percentil(ordenados, 75),
                "maximo": ordenados[-1],
            })
        return Quadro.de_vaults(linhas)

    def correlacao(self, colunas=None):
        """Correlação de Pearson entre as colunas numéricas."""
        alvo = _achatar([colunas]) if colunas else [
            c for c in self._colunas if _numeros(self._dados[c])]
        for c in alvo:
            self._exigir(c)
        dados = {"coluna": list(alvo)}
        for a in alvo:
            dados[a] = [_pearson(self._dados[a], self._dados[b]) for b in alvo]
        return Quadro(["coluna"] + list(alvo), dados)

    def perfil(self):
        """O retrato de cada coluna: tipo, ausentes, distintos, exemplo.

        É o primeiro comando a rodar num conjunto que você não conhece —
        antes de calcular qualquer coisa.
        """
        linhas = []
        for c in self._colunas:
            valores = self._dados[c]
            uteis = [v for v in valores if not _ausente(v)]
            distintos = {_chave(v) for v in uteis}
            ns = _numeros(uteis)
            linhas.append({
                "coluna": c,
                "tipo": _tipo_da_coluna(uteis),
                "linhas": len(valores),
                "ausentes": len(valores) - len(uteis),
                "ausentes_pct": round(
                    100.0 * (len(valores) - len(uteis)) / len(valores), 1)
                    if valores else 0.0,
                "distintos": len(distintos),
                "minimo": min(ns) if ns else None,
                "maximo": max(ns) if ns else None,
                "exemplo": uteis[0] if uteis else None,
            })
        return Quadro.de_vaults(linhas)

    def fora_da_curva(self, coluna, fator=1.5):
        """As linhas fora de 1,5 × o intervalo interquartil."""
        self._exigir(coluna)
        ns = sorted(_numeros(self._dados[coluna]))
        if len(ns) < 4:
            return self._por_indices([])
        q1, q3 = _percentil(ns, 25), _percentil(ns, 75)
        folga = fator * (q3 - q1)
        indices = [i for i in range(self.altura())
                   if _numerico(self._dados[coluna][i])
                   and not (q1 - folga <= self._dados[coluna][i] <= q3 + folga)]
        return self._por_indices(indices)

    # ── sair ─────────────────────────────────────────────────

    def para_csv(self, caminho, separador=","):
        with _io.open(caminho, "w", encoding="utf-8", newline="") as f:
            escritor = _csv.writer(f, delimiter=separador)
            escritor.writerow(self._colunas)
            for i in range(self.altura()):
                escritor.writerow(
                    ["" if _ausente(self._dados[c][i]) else self._dados[c][i]
                     for c in self._colunas])
        return caminho

    def para_json(self, caminho=None):
        texto = _json.dumps(self.para_vaults(), ensure_ascii=False,
                            indent=2, default=str)
        if caminho is None:
            return texto
        with _io.open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        return caminho

    def texto(self, limite=10):
        """O quadro desenhado, para o terminal."""
        if not self._colunas:
            return "(quadro vazio)"
        mostrar = min(limite, self.altura())
        celulas = [[_celula(c) for c in self._colunas]]
        for i in range(mostrar):
            celulas.append([_celula(self._dados[c][i]) for c in self._colunas])
        larguras = [max(len(linha[j]) for linha in celulas)
                    for j in range(len(self._colunas))]
        fora = []
        for n, linha in enumerate(celulas):
            fora.append("  ".join(v.ljust(larguras[j])
                                  for j, v in enumerate(linha)).rstrip())
            if n == 0:
                fora.append("  ".join("-" * w for w in larguras))
        if self.altura() > mostrar:
            fora.append(f"… {self.altura() - mostrar} linha(s) a mais")
        fora.append(f"[{self.altura()} linha(s) × {self.largura()} coluna(s)]")
        return "\n".join(fora)

    # ── protocolo ────────────────────────────────────────────

    def __len__(self):
        return self.altura()

    def __iter__(self):
        """Iterar um quadro dá LINHAS, como vault.

        É o que faz `q >> sift l: l["v"] bigger 10` funcionar sem que o
        pipeline saiba o que é um quadro.
        """
        return iter(self.para_vaults())

    def __getitem__(self, chave):
        if isinstance(chave, str):
            return self.coluna(chave)
        if isinstance(chave, int):
            return self.linha(chave)
        if isinstance(chave, slice):
            inicio = 0 if chave.start is None else chave.start
            fim = self.altura() if chave.stop is None else chave.stop
            return self._fatia(inicio, fim)
        raise _erro("um quadro se indexa por nome de coluna ou por linha",
                    dica='q["nome"]  ou  q[0]  ou  q[0:10]')

    def __repr__(self):
        return self.texto()

    def __eq__(self, outro):
        return (isinstance(outro, Quadro)
                and self._colunas == outro._colunas
                and self.para_colunas() == outro.para_colunas())

    def __hash__(self):
        return id(self)

    # ── interno ──────────────────────────────────────────────

    def _exigir(self, nome):
        if nome in self._dados:
            return
        perto = _parecido(nome, self._colunas)
        raise _erro(
            f"a coluna '{nome}' não existe neste quadro",
            nota=f"as colunas são: {', '.join(str(c) for c in self._colunas)}"
                 if self._colunas else "o quadro não tem coluna nenhuma",
            dica=f"você quis dizer '{perto}'?" if perto else
                 "confira com  q.colunas()")

    def _fatia(self, inicio, fim):
        return self._por_indices(list(range(self.altura()))[inicio:fim])

    def _por_indices(self, indices):
        return Quadro(self._colunas,
                      {c: [self._dados[c][i] for i in indices]
                       for c in self._colunas})

    def _escalar(self, colunas, como):
        alvo = _achatar([colunas]) if colunas else [
            c for c in self._colunas if _numeros(self._dados[c])]
        q = self
        for c in alvo:
            self._exigir(c)
            q = q.com(c, como(q._dados[c]))
        return q


# ═════════════════════════════════════════════════════════════
#  Grupo — o resultado de 'agrupar'
# ═════════════════════════════════════════════════════════════

class Grupo:
    """Um quadro agrupado, esperando a agregação.

    Ele existe como tipo próprio porque `agrupar` sozinho não devolve
    tabela: um agrupamento sem agregação não tem forma retangular. Deixar
    `agrupar` devolver um quadro obrigaria a inventar uma coluna de
    listas, e a pergunta seguinte — "média de quê?" — ficaria sem lugar.
    """

    __slots__ = ("_quadro", "_chaves", "__weakref__")

    def __init__(self, quadro, chaves):
        self._quadro = quadro
        self._chaves = list(chaves)

    def chaves(self):
        return list(self._chaves)

    def grupos(self):
        """Os grupos como vault: a chave, e o quadro de cada um."""
        return {_texto_da_chave(k): q for k, q in self._baldes().items()}

    def contar(self):
        """Quantas linhas em cada grupo."""
        return self.resumir({"contagem": "contagem"})

    def resumir(self, agregacoes):
        """Agrega cada grupo.

            q.agrupar("cidade").resumir({"valor": "soma", "id": "contagem"})

        O nome da agregação é TEXTO e a tabela é fechada: um nome
        desconhecido é recusado com a lista do que existe. Aceitar
        qualquer ação abriria a porta para um nome vindo de fora — de um
        `?agregar=` de uma tela, por exemplo.
        """
        if not isinstance(agregacoes, dict):
            raise _erro("'resumir' precisa de um vault",
                        dica='resumir({"valor": "soma", "id": "contagem"})')

        pedidos = []
        for coluna, como in agregacoes.items():
            nomes = como if isinstance(como, list) else [como]
            for nome in nomes:
                if coluna != "contagem" or nome != "contagem":
                    self._quadro._exigir(coluna)
                pedidos.append((coluna, str(nome),
                                f"{coluna}_{nome}" if len(agregacoes) > 1
                                or len(nomes) > 1 else coluna))

        baldes = self._baldes()
        linhas = []
        for marca, quadro in baldes.items():
            linha = dict(zip(self._chaves, marca)) if self._chaves else {}
            for coluna, nome, saida in pedidos:
                agrega = _agregacao(nome)
                valores = quadro.coluna(coluna) if coluna in quadro._dados \
                    else list(range(quadro.altura()))
                linha[saida] = agrega(valores)
            linhas.append(linha)
        return Quadro.de_vaults(linhas)

    def _baldes(self):
        if not self._chaves:
            return {(): self._quadro}
        q = self._quadro
        ordem, baldes = [], {}
        for i in range(q.altura()):
            marca = tuple(_chave(q._dados[c][i]) for c in self._chaves)
            if marca not in baldes:
                baldes[marca] = []
                ordem.append(marca)
            baldes[marca].append(i)
        return {m: q._por_indices(baldes[m]) for m in ordem}

    def __repr__(self):
        return (f"<grupo por {', '.join(str(c) for c in self._chaves)}: "
                f"{len(self._baldes())} grupo(s)>")


# ═════════════════════════════════════════════════════════════
#  Auxiliares
# ═════════════════════════════════════════════════════════════

def _achatar(itens):
    """`("a", "b")`, `(["a","b"],)` e `"a"` viram todos `["a","b"]`."""
    fora = []
    for i in itens:
        if i is None:
            continue
        if isinstance(i, (list, tuple)):
            fora.extend(i)
        else:
            fora.append(i)
    return fora


def _verdade(v):
    return bool(v) and v is not None


def _ordenavel(v):
    """A ausência vai para o FIM, e tipos diferentes não se comparam."""
    if _ausente(v):
        return (2, 0, "")
    if _numerico(v):
        return (0, v, "")
    return (1, 0, str(v))


def _percentil(ordenados, p):
    if not ordenados:
        return None
    if len(ordenados) == 1:
        return ordenados[0]
    pos = (len(ordenados) - 1) * (p / 100.0)
    baixo = int(_math.floor(pos))
    alto = min(baixo + 1, len(ordenados) - 1)
    peso = pos - baixo
    return ordenados[baixo] * (1 - peso) + ordenados[alto] * peso


def _pearson(a, b):
    pares = [(x, y) for x, y in zip(a, b)
             if _numerico(x) and _numerico(y)
             and not _ausente(x) and not _ausente(y)]
    if len(pares) < 2:
        return None
    xs = [p[0] for p in pares]
    ys = [p[1] for p in pares]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    cima = sum((x - mx) * (y - my) for x, y in pares)
    bx = _math.sqrt(sum((x - mx) ** 2 for x in xs))
    by = _math.sqrt(sum((y - my) ** 2 for y in ys))
    return None if bx == 0 or by == 0 else round(cima / (bx * by), 6)


def _normalizar(valores):
    ns = _numeros(valores)
    if not ns:
        return list(valores)
    menor, maior = min(ns), max(ns)
    faixa = maior - menor
    return [None if _ausente(v) or not _numerico(v)
            else (0.0 if faixa == 0 else (v - menor) / faixa)
            for v in valores]


def _padronizar(valores):
    ns = _numeros(valores)
    if not ns:
        return list(valores)
    m = sum(ns) / len(ns)
    d = _desvio(ns)
    return [None if _ausente(v) or not _numerico(v)
            else (0.0 if d == 0 else (v - m) / d)
            for v in valores]


def _preencher(valores, como):
    if como == "media":
        alvo = _media(valores)
    elif como == "mediana":
        alvo = _mediana(valores)
    elif como in ("anterior", "seguinte"):
        return _preencher_vizinho(valores, como)
    else:
        alvo = como
    return [alvo if _ausente(v) else v for v in valores]


def _preencher_vizinho(valores, como):
    fora = list(valores)
    faixa = range(len(fora)) if como == "anterior" \
        else range(len(fora) - 1, -1, -1)
    passo = -1 if como == "anterior" else 1
    for i in faixa:
        if _ausente(fora[i]):
            vizinho = i + passo
            if 0 <= vizinho < len(fora) and not _ausente(fora[vizinho]):
                fora[i] = fora[vizinho]
    return fora


def _agregacao(nome):
    agrega = AGREGACOES.get(str(nome))
    if agrega is None:
        raise _erro(
            f"não conheço a agregação '{nome}'",
            nota=f"as agregações são: {', '.join(sorted(AGREGACOES))}",
            dica='resumir({"valor": "soma"})')
    return agrega


_CONVERSORES = {
    "Integer": lambda v: _talvez(int, v),
    "Float": lambda v: _talvez(float, v),
    "String": lambda v: None if _ausente(v) else str(v),
    "Boolean": lambda v: None if _ausente(v) else _booleano(v),
}


def _talvez(conversor, valor):
    """Converte, e devolve `void` quando não dá.

    Levantar na primeira célula ruim de um CSV de um milhão de linhas não
    ajuda ninguém: `perfil()` conta quantas não converteram, e é ali que
    a decisão é tomada.
    """
    if _ausente(valor):
        return None
    try:
        return conversor(str(valor).strip().replace(",", ".")
                         if conversor is float else str(valor).strip())
    except (TypeError, ValueError):
        return None


def _booleano(v):
    return str(v).strip().lower() in ("yes", "sim", "true", "1", "y", "s", "t")


def _e_inteiro(v):
    t = str(v).strip()
    return bool(t) and (t.lstrip("+-").isdigit())


def _e_decimal(v):
    try:
        float(str(v).strip().replace(",", "."))
        return True
    except (TypeError, ValueError):
        return False


def _tipo_da_coluna(uteis):
    if not uteis:
        return "Void"
    if all(isinstance(v, bool) for v in uteis):
        return "Boolean"
    if all(isinstance(v, int) and not isinstance(v, bool) for v in uteis):
        return "Integer"
    if all(_numerico(v) for v in uteis):
        return "Float"
    if all(isinstance(v, str) for v in uteis):
        return "String"
    return "Any"


def _curto(n):
    return f"{n:.2f}".rstrip("0").rstrip(".")


def _celula(v):
    if _ausente(v):
        return "void"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.4f}".rstrip("0").rstrip(".")
    return str(v)


def _texto_da_chave(marca):
    return " | ".join(str(k) for k in marca) if marca else "(tudo)"


# ═════════════════════════════════════════════════════════════
#  O módulo
# ═════════════════════════════════════════════════════════════

class ArcaneQuadro:
    """O dicionário que `adopt Arcane.Quadro` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Quadro",

            # ── nascer ──
            "Quadro": Quadro,
            "Grupo": Grupo,
            "de_vaults": Quadro.de_vaults,
            "de_colunas": Quadro.de_colunas,
            "de_csv": Quadro.de_csv,
            "de_json": Quadro.de_json,
            "vazio": Quadro.vazio,

            # ── as agregações que 'resumir' conhece ──
            "agregacoes": lambda: sorted(AGREGACOES),

            # ── perguntas sobre um valor ──
            "ausente": _ausente,
            "tipos": lambda: sorted(_CONVERSORES),
        }
