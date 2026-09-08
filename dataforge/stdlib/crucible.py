"""
Crucible — o framework de testes do DataForge

No cadinho o metal e provado no fogo: o que nao resiste, aparece. E o
terceiro nome da forja — DataForge molda, Kiln assa, Crucible prova.

    crucible "Calculadora":

        fixture calc():
            provide spawn Calculadora()

        trial "soma dois numeros":
            expect(2 + 2).to_be(4)

        trial "recusa divisao por zero":
            expect(lambda => 1 / 0).to_raise(DivisionByZeroError)

Ha tambem a forma de biblioteca, para quem prefere chamadas:

    adopt Crucible

    Crucible.suite("Calculadora")
    Crucible.trial("soma", lambda => Crucible.expect(2 + 2).to_be(4))
    Crucible.run()

─── Por que um framework proprio ───────────────────────────

O 'dataforge test' que ja existia roda arquivos '*_test.df' e conta
'assert'. Isso responde "passou?" e nada mais. Quando falha, a mensagem
diz que uma expressao deu falso — nao o que se esperava, o que veio, nem
qual dos 40 casos daquele arquivo era.

O Crucible responde as outras perguntas: qual caso, o que se esperava, o
que veio, a diferenca entre os dois, quanto tempo levou, e o que mais
falhou junto. E o que separa um teste que aponta o bug de um que so
avisa que ele existe.

─── As garantias ───────────────────────────────────────────

1. **Um trial nao vaza para o proximo.** Cada um roda no proprio escopo,
   com as fixtures reconstruidas. Um teste que passa sozinho e falha na
   suite e um bug do framework, nao do teste.

2. **A limpeza roda mesmo com falha.** 'after' e a parte da fixture
   depois do 'provide' rodam em qualquer saida — inclusive quando o
   trial estoura. Sem isso, uma falha deixa lixo e derruba os seguintes.

3. **A ordem nao importa.** Com '--aleatorio' a suite embaralha; um
   teste que depende de ordem falha ali, e nao seis meses depois.

4. **A diferenca e mostrada, nao descrita.** Comparar dois vaults de
   dez chaves lendo 'esperava X, veio Y' inteiros nao se faz; o
   Crucible aponta a chave que difere.
"""

import difflib
import io
import json
import os
import random
import re
import sys
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr

from ..errors import ExpectationError, erro_por_nome


# ═════════════════════════════════════════════════════════════
#  Resultado
# ═════════════════════════════════════════════════════════════

#: Os desfechos possiveis de um trial.
PASSOU = "passou"
FALHOU = "falhou"
ERRO = "erro"
PENDENTE = "pendente"
IGNORADO = "ignorado"

#: Simbolo e cor de cada desfecho no relatorio.
MARCA = {
    PASSOU:   ("✓", "1;32"),
    FALHOU:   ("✗", "1;31"),
    ERRO:     ("⚡", "1;35"),
    PENDENTE: ("○", "1;33"),
    IGNORADO: ("–", "0;90"),
}


class Resultado:
    """O que aconteceu com um trial.

    Guarda o suficiente para o relatorio ser escrito depois, e nao
    durante: com '--paralelo' a ordem de execucao nao e a de leitura,
    e imprimir na hora embaralharia a saida.
    """

    __slots__ = ("suite", "nome", "estado", "duracao", "erro", "motivo",
                 "tags", "esperado", "obtido", "diferenca", "saida",
                 "arquivo", "linha", "tentativas")

    def __init__(self, suite, nome, estado=PASSOU, duracao=0.0):
        self.suite = suite
        self.nome = nome
        self.estado = estado
        self.duracao = duracao
        self.erro = None
        self.motivo = ""
        self.tags = []
        self.esperado = None
        self.obtido = None
        self.diferenca = ""
        self.saida = ""
        self.arquivo = ""
        self.linha = 0
        self.tentativas = 1

    @property
    def caminho(self):
        return f"{self.suite} > {self.nome}" if self.suite else self.nome

    def para_vault(self):
        """O resultado como vault, para o DataForge ler."""
        return {
            "suite": self.suite,
            "nome": self.nome,
            "estado": self.estado,
            "duracao": round(self.duracao, 6),
            "motivo": self.motivo,
            "tags": list(self.tags),
            "diferenca": self.diferenca,
            "arquivo": self.arquivo,
            "linha": self.linha,
            "tentativas": self.tentativas,
        }

    def __repr__(self):
        return f"<{self.estado} {self.caminho}>"


class FalhaDeExpectativa(ExpectationError):
    """Uma expectativa nao se cumpriu.

    E o DF1402 do catalogo, e nao uma excecao a parte. Isso importa por
    dois motivos:

        - ela atravessa o interpretador intacta. Como excecao comum do
          Python, o tradutor a reescrevia como RuntimeError e a
          mensagem cuidadosamente montada aqui virava 'to_be: devia
          ser 5, e veio 4' — com o nome do metodo colado na frente.

        - 'handle ExpectationError' funciona dentro do proprio teste,
          para quem precisa cobrar que uma expectativa falhe.
    """

    def __init__(self, mensagem, esperado=None, obtido=None, diferenca=""):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.esperado = esperado
        self.obtido = obtido
        self.diferenca = diferenca


# ═════════════════════════════════════════════════════════════
#  Formatacao de valores e diferencas
# ═════════════════════════════════════════════════════════════

def _texto(valor, profundidade=0):
    """Um valor no vocabulario do DataForge, nao no do Python.

    'True' vira 'yes', 'None' vira 'void', dict vira vault. Quem le a
    falha escreve DataForge; ver 'True' na mensagem obriga a traduzir
    de cabeca antes de entender o que houve.
    """
    if valor is True:
        return "yes"
    if valor is False:
        return "no"
    if valor is None:
        return "void"
    if isinstance(valor, str):
        return f'"{valor}"' if profundidade else valor
    if isinstance(valor, float):
        return repr(round(valor, 10)).rstrip("0").rstrip(".") or "0"
    if isinstance(valor, (list, tuple)):
        if profundidade > 3:
            return "[...]"
        return "[" + ", ".join(_texto(v, profundidade + 1) for v in valor) + "]"
    if isinstance(valor, dict):
        if profundidade > 3:
            return "{...}"
        return "{" + ", ".join(
            f'{_texto(k, profundidade + 1)}: {_texto(v, profundidade + 1)}'
            for k, v in valor.items()) + "}"
    if isinstance(valor, set):
        return "{" + ", ".join(_texto(v, profundidade + 1) for v in sorted(
            valor, key=str)) + "}"
    nome = getattr(valor, "name", None)
    if nome and hasattr(valor, "fields"):
        return f"{nome}({', '.join(f'{k}: {_texto(v, profundidade+1)}' for k, v in valor.fields.items())})"
    return str(valor)


def _tipo(valor):
    """O nome do tipo como o DataForge o chama."""
    if valor is None:
        return "Void"
    if isinstance(valor, bool):
        return "Boolean"
    if isinstance(valor, int):
        return "Integer"
    if isinstance(valor, float):
        return "Float"
    if isinstance(valor, str):
        return "String"
    if isinstance(valor, (list, tuple)):
        return "Cluster"
    if isinstance(valor, dict):
        return "Vault"
    if callable(valor):
        return "Action"
    return getattr(getattr(valor, "blueprint", None), "name", None) \
        or type(valor).__name__


def diferenca(esperado, obtido):
    """Onde os dois valores divergem — a parte, nao o todo.

    Imprimir dois vaults de trinta chaves lado a lado nao ajuda: quem
    le tem de conferir chave por chave, que e exatamente o trabalho que
    o teste deveria poupar. Aqui sai so o que difere.
    """
    if isinstance(esperado, dict) and isinstance(obtido, dict):
        linhas = []
        for chave in sorted(set(esperado) | set(obtido), key=str):
            if chave not in obtido:
                linhas.append(f'  - {_texto(chave, 1)}: {_texto(esperado[chave], 1)}   (faltou)')
            elif chave not in esperado:
                linhas.append(f'  + {_texto(chave, 1)}: {_texto(obtido[chave], 1)}   (sobrou)')
            elif esperado[chave] != obtido[chave]:
                linhas.append(f'  ~ {_texto(chave, 1)}: '
                              f'esperava {_texto(esperado[chave], 1)}, '
                              f'veio {_texto(obtido[chave], 1)}')
        return "\n".join(linhas)

    if isinstance(esperado, (list, tuple)) and isinstance(obtido, (list, tuple)):
        linhas = []
        if len(esperado) != len(obtido):
            linhas.append(f"  tamanho: esperava {len(esperado)}, veio {len(obtido)}")
        for i in range(min(len(esperado), len(obtido))):
            if esperado[i] != obtido[i]:
                linhas.append(f"  [{i}]: esperava {_texto(esperado[i], 1)}, "
                              f"veio {_texto(obtido[i], 1)}")
        for i in range(len(obtido), len(esperado)):
            linhas.append(f"  [{i}]: faltou {_texto(esperado[i], 1)}")
        for i in range(len(esperado), len(obtido)):
            linhas.append(f"  [{i}]: sobrou {_texto(obtido[i], 1)}")
        return "\n".join(linhas[:20])

    if isinstance(esperado, str) and isinstance(obtido, str):
        if "\n" in esperado or "\n" in obtido:
            saida = difflib.unified_diff(
                esperado.splitlines(), obtido.splitlines(),
                "esperado", "obtido", lineterm="", n=1)
            return "\n".join("  " + l for l in list(saida)[:24])
        # Uma linha: aponta a coluna onde divergem.
        for i, (a, b) in enumerate(zip(esperado, obtido)):
            if a != b:
                return (f'  esperava "{esperado}"\n'
                        f'  veio     "{obtido}"\n'
                        f'  {" " * (i + 11)}^ diverge na coluna {i + 1}')
        return (f"  um e prefixo do outro: esperava {len(esperado)} "
                f"caracteres, veio {len(obtido)}")

    return ""


# ═════════════════════════════════════════════════════════════
#  Expectativa — a cadeia de matchers
# ═════════════════════════════════════════════════════════════

#: Marca "nao passaram este argumento", para distinguir de 'void' —
#: que e um valor legitimo a se cobrar.
NADA = object()


class Expectativa:
    """O valor sob teste, com os matchers que se pode cobrar dele.

    Cada matcher devolve a propria expectativa, entao encadear e
    natural:

        expect(nome).to_be_text().to_start_with("Ana").to_have_length(3)

    'nao' inverte o proximo — e so o proximo, para nao deixar um estado
    invertido pendurado:

        expect(xs).nao().to_contain(9)
    """

    __slots__ = ("valor", "_negado", "_rotulo")

    def __init__(self, valor, rotulo=""):
        self.valor = valor
        self._negado = False
        self._rotulo = rotulo

    # ── controle da cadeia ──────────────────────────────────

    def nao(self):
        """Inverte a proxima cobranca."""
        self._negado = not self._negado
        return self

    def como(self, rotulo):
        """Da um nome ao valor, para a mensagem de falha."""
        self._rotulo = rotulo
        return self

    def _falhar(self, descricao, esperado=None, obtido=NADA):
        alvo = self.valor if obtido is NADA else obtido
        sujeito = f"{self._rotulo} " if self._rotulo else ""
        if self._negado:
            msg = f"{sujeito}nao devia {descricao}, mas {_texto(alvo)} e assim"
            raise FalhaDeExpectativa(msg, esperado, alvo)
        msg = f"{sujeito}devia {descricao}"
        dif = diferenca(esperado, alvo) if esperado is not None else ""
        raise FalhaDeExpectativa(msg, esperado, alvo, dif)

    def _cobrar(self, condicao, descricao, esperado=None):
        """O nucleo: uma condicao, e o que dizer quando ela nao vale."""
        if bool(condicao) == self._negado:
            self._falhar(descricao, esperado)
        self._negado = False
        return self

    # ── igualdade ───────────────────────────────────────────

    def to_be(self, esperado):
        """Igual por valor. E o matcher que se usa em 9 de 10 casos."""
        return self._cobrar(self.valor == esperado,
                            f"ser {_texto(esperado)}, e veio {_texto(self.valor)}",
                            esperado)

    def to_equal(self, esperado):
        """Sinonimo de to_be, para quem vem de outra linguagem."""
        return self.to_be(esperado)

    def to_be_exactly(self, esperado):
        """A mesma identidade, nao so o mesmo valor."""
        return self._cobrar(self.valor is esperado,
                            f"ser exatamente o mesmo objeto que {_texto(esperado)}")

    def to_be_close_to(self, esperado, casas=7):
        """Igualdade de ponto flutuante, que nunca e exata.

        '0.1 + 0.2' nao da '0.3' em nenhuma linguagem com IEEE 754.
        Cobrar igualdade exata de float e escrever um teste que falha
        por motivo errado.
        """
        margem = 10 ** -casas
        perto = abs(float(self.valor) - float(esperado)) < margem
        return self._cobrar(
            perto, f"estar a menos de {margem} de {_texto(esperado)}, "
                   f"e veio {_texto(self.valor)}")

    def to_be_between(self, minimo, maximo):
        """Dentro da faixa, extremos incluidos."""
        return self._cobrar(minimo <= self.valor <= maximo,
                            f"estar entre {_texto(minimo)} e {_texto(maximo)}, "
                            f"e veio {_texto(self.valor)}")

    # ── verdade e vazio ─────────────────────────────────────

    def to_be_true(self):
        """E exatamente yes — nao apenas algo que vale como verdadeiro."""
        return self._cobrar(self.valor is True, "ser yes")

    def to_be_false(self):
        """E exatamente no."""
        return self._cobrar(self.valor is False, "ser no")

    def to_be_truthy(self):
        """Vale como verdadeiro num given: nao e 0, vazio nem void."""
        return self._cobrar(bool(self.valor), "valer como verdadeiro")

    def to_be_falsy(self):
        """Vale como falso: 0, texto vazio, colecao vazia ou void."""
        return self._cobrar(not bool(self.valor), "valer como falso")

    def to_be_void(self):
        """E void — o resultado de uma acao sem yield."""
        return self._cobrar(self.valor is None, "ser void")

    def to_exist(self):
        """Nao e void."""
        return self._cobrar(self.valor is not None, "existir (nao ser void)")

    def to_be_empty(self):
        """Nao tem nenhum item; vale para texto, cluster e vault."""
        return self._cobrar(len(self.valor) == 0,
                            f"estar vazio, e tem {len(self.valor)} item(ns)")

    # ── tipos ───────────────────────────────────────────────

    def to_be_a(self, tipo):
        """O tipo, pelo nome que o DataForge usa."""
        nome = tipo if isinstance(tipo, str) else getattr(tipo, "name", str(tipo))
        return self._cobrar(_tipo(self.valor) == nome,
                            f"ser {nome}, e e {_tipo(self.valor)}")

    def to_be_number(self):
        """E Integer ou Float; Boolean nao conta, ainda que o Python ache."""
        return self._cobrar(isinstance(self.valor, (int, float))
                            and not isinstance(self.valor, bool),
                            f"ser numero, e e {_tipo(self.valor)}")

    def to_be_text(self):
        """E String."""
        return self._cobrar(isinstance(self.valor, str),
                            f"ser String, e e {_tipo(self.valor)}")

    def to_be_cluster(self):
        """E Cluster (lista)."""
        return self._cobrar(isinstance(self.valor, list),
                            f"ser Cluster, e e {_tipo(self.valor)}")

    def to_be_vault(self):
        """E Vault (dicionario)."""
        return self._cobrar(isinstance(self.valor, dict),
                            f"ser Vault, e e {_tipo(self.valor)}")

    def to_be_action(self):
        """Pode ser chamado com parenteses."""
        return self._cobrar(callable(self.valor),
                            f"ser chamavel, e e {_tipo(self.valor)}")

    def to_be_integer(self):
        """E Integer, e nao Float nem Boolean."""
        return self._cobrar(isinstance(self.valor, int)
                            and not isinstance(self.valor, bool),
                            f"ser Integer, e e {_tipo(self.valor)}")

    def to_be_float(self):
        """E Float."""
        return self._cobrar(isinstance(self.valor, float),
                            f"ser Float, e e {_tipo(self.valor)}")

    def to_be_boolean(self):
        """E yes ou no."""
        return self._cobrar(isinstance(self.valor, bool),
                            f"ser Boolean, e e {_tipo(self.valor)}")

    def to_be_instance_of(self, blueprint):
        """Instancia daquele blueprint, ou de um herdeiro dele."""
        nome = blueprint if isinstance(blueprint, str) else getattr(
            blueprint, "name", str(blueprint))
        bp = getattr(self.valor, "blueprint", None)
        linhagem = [b.name for b in bp.linhagem()] if bp and hasattr(bp, "linhagem") else []
        return self._cobrar(nome in linhagem,
                            f"ser instancia de {nome}; a linhagem e "
                            f"{' < '.join(linhagem) or _tipo(self.valor)}")

    # ── numeros ─────────────────────────────────────────────

    def to_be_greater_than(self, outro):
        """Estritamente maior."""
        return self._cobrar(self.valor > outro,
                            f"ser maior que {_texto(outro)}, e vale {_texto(self.valor)}")

    def to_be_less_than(self, outro):
        """Estritamente menor."""
        return self._cobrar(self.valor < outro,
                            f"ser menor que {_texto(outro)}, e vale {_texto(self.valor)}")

    def to_be_at_least(self, outro):
        """Maior ou igual."""
        return self._cobrar(self.valor >= outro,
                            f"ser pelo menos {_texto(outro)}, e vale {_texto(self.valor)}")

    def to_be_at_most(self, outro):
        """Menor ou igual."""
        return self._cobrar(self.valor <= outro,
                            f"ser no maximo {_texto(outro)}, e vale {_texto(self.valor)}")

    def to_be_positive(self):
        """Maior que zero; zero nao passa."""
        return self._cobrar(self.valor > 0,
                            f"ser positivo, e vale {_texto(self.valor)}")

    def to_be_negative(self):
        """Menor que zero."""
        return self._cobrar(self.valor < 0,
                            f"ser negativo, e vale {_texto(self.valor)}")

    def to_be_zero(self):
        """E zero."""
        return self._cobrar(self.valor == 0,
                            f"ser zero, e vale {_texto(self.valor)}")

    def to_be_even(self):
        """E par."""
        return self._cobrar(self.valor % 2 == 0,
                            f"ser par, e vale {_texto(self.valor)}")

    def to_be_odd(self):
        """E impar."""
        return self._cobrar(self.valor % 2 != 0,
                            f"ser impar, e vale {_texto(self.valor)}")

    def to_be_divisible_by(self, divisor):
        """Divide sem deixar resto."""
        return self._cobrar(self.valor % divisor == 0,
                            f"ser divisivel por {_texto(divisor)}, "
                            f"e {_texto(self.valor)} deixa resto "
                            f"{self.valor % divisor}")

    def to_be_finite(self):
        """Nao e infinito nem NaN."""
        import math
        return self._cobrar(math.isfinite(self.valor), "ser finito")

    def to_be_nan(self):
        """E NaN — o valor que nao e igual nem a si mesmo."""
        import math
        return self._cobrar(isinstance(self.valor, float)
                            and math.isnan(self.valor), "ser NaN")

    # ── texto ───────────────────────────────────────────────

    def to_start_with(self, prefixo):
        """Comeca com o prefixo."""
        return self._cobrar(str(self.valor).startswith(prefixo),
                            f'comecar com "{prefixo}", e veio {_texto(self.valor, 1)}')

    def to_end_with(self, sufixo):
        """Termina com o sufixo."""
        return self._cobrar(str(self.valor).endswith(sufixo),
                            f'terminar com "{sufixo}", e veio {_texto(self.valor, 1)}')

    def to_match(self, padrao):
        """Casa com a expressao regular."""
        return self._cobrar(re.search(padrao, str(self.valor)) is not None,
                            f'casar com /{padrao}/, e veio {_texto(self.valor, 1)}')

    def to_be_blank(self):
        """So espaco em branco, ou nada."""
        return self._cobrar(not str(self.valor).strip(),
                            "estar em branco")

    def to_be_uppercase(self):
        """Todas as letras em maiuscula."""
        return self._cobrar(str(self.valor).isupper(), "estar em maiusculas")

    def to_be_lowercase(self):
        """Todas as letras em minuscula."""
        return self._cobrar(str(self.valor).islower(), "estar em minusculas")

    def to_contain_text(self, trecho):
        """O trecho aparece em algum lugar do texto."""
        return self._cobrar(trecho in str(self.valor),
                            f'conter "{trecho}", e veio {_texto(self.valor, 1)}')

    def to_have_lines(self, n):
        """Tem exatamente n linhas."""
        reais = len(str(self.valor).splitlines())
        return self._cobrar(reais == n, f"ter {n} linha(s), e tem {reais}")

    # ── colecoes ────────────────────────────────────────────

    def to_be_in(self, colecao):
        """O contrario de to_contain — o valor esta dentro da colecao."""
        return self._cobrar(self.valor in colecao,
                            f"estar em {_texto(colecao)}")

    def to_contain(self, item):
        """A colecao tem o item."""
        return self._cobrar(item in self.valor,
                            f"conter {_texto(item)}, e tem {_texto(self.valor)}")

    def to_contain_all(self, itens):
        """Tem todos os itens; a mensagem diz quais faltaram."""
        faltando = [i for i in itens if i not in self.valor]
        return self._cobrar(not faltando,
                            f"conter todos; faltou {_texto(faltando)}")

    def to_contain_any(self, itens):
        """Tem pelo menos um dos itens."""
        return self._cobrar(any(i in self.valor for i in itens),
                            f"conter pelo menos um de {_texto(itens)}")

    def to_have_length(self, n):
        """Tem exatamente n itens."""
        real = len(self.valor)
        return self._cobrar(real == n,
                            f"ter {n} item(ns), e tem {real}")

    def to_have_key(self, chave):
        """O vault tem a chave; a mensagem lista as que tem."""
        return self._cobrar(chave in self.valor,
                            f'ter a chave {_texto(chave, 1)}; tem '
                            f'{_texto(list(self.valor))}')

    def to_have_keys(self, chaves):
        """Tem todas as chaves listadas."""
        faltando = [c for c in chaves if c not in self.valor]
        return self._cobrar(not faltando,
                            f"ter as chaves; faltou {_texto(faltando)}")

    def to_have_field(self, campo, valor=NADA):
        """O campo existe — e, se dado, vale aquilo.

        Serve para vault, record e instancia: os tres respondem a
        pergunta "voce tem este campo?" de jeitos diferentes, e quem
        escreve o teste nao deveria precisar saber qual e qual.
        """
        alvo = self.valor
        if isinstance(alvo, dict):
            tem, atual = campo in alvo, alvo.get(campo)
        elif hasattr(alvo, "fields") and campo in getattr(alvo, "fields", {}):
            tem, atual = True, alvo.fields[campo]
        else:
            tem, atual = hasattr(alvo, campo), getattr(alvo, campo, None)
        if valor is NADA:
            return self._cobrar(tem, f"ter o campo '{campo}'")
        return self._cobrar(tem and atual == valor,
                            f"ter '{campo}' igual a {_texto(valor)}, "
                            f"e vale {_texto(atual)}")

    def to_be_sorted(self, decrescente=False):
        esperada = sorted(self.valor, reverse=decrescente)
        return self._cobrar(list(self.valor) == esperada,
                            f"estar ordenado{'  (decrescente)' if decrescente else ''}",
                            esperada)

    def to_be_unique(self):
        """Nenhum item se repete."""
        vistos, repetidos = set(), []
        for item in self.valor:
            chave = json.dumps(item, sort_keys=True, default=str)
            if chave in vistos:
                repetidos.append(item)
            vistos.add(chave)
        return self._cobrar(not repetidos,
                            f"nao ter repetidos; repetiu {_texto(repetidos)}")

    def to_all_satisfy(self, condicao):
        """Todo item passa na condicao; a mensagem mostra os que nao."""
        maus = [x for x in self.valor if not condicao(x)]
        return self._cobrar(not maus,
                            f"ter todos os itens satisfazendo; falharam "
                            f"{_texto(maus[:5])}")

    def to_any_satisfy(self, condicao):
        """Ao menos um item passa na condicao."""
        return self._cobrar(any(condicao(x) for x in self.valor),
                            "ter ao menos um item satisfazendo")

    def to_have_same_items(self, outra):
        """Os mesmos itens, em qualquer ordem."""
        a = sorted(self.valor, key=str)
        b = sorted(outra, key=str)
        return self._cobrar(a == b, "ter os mesmos itens", outra)

    # ── erros ───────────────────────────────────────────────

    def to_raise(self, tipo=None, mensagem=None):
        """A acao levanta um erro — do tipo dado, se dado.

        O valor sob teste tem de ser uma acao, nao o resultado dela:
        'expect(1 / 0)' ja estourou antes de chegar aqui. E
        'expect(lambda => 1 / 0)'.
        """
        if not callable(self.valor):
            raise FalhaDeExpectativa(
                "to_raise precisa de uma acao, nao de um valor.\n"
                "    Use  expect(lambda => arriscado())  — sem os parenteses "
                "da chamada,\n    senao o erro acontece antes de o Crucible "
                "poder observa-lo.")

        nome_esperado = None
        if tipo is not None:
            nome_esperado = tipo if isinstance(tipo, str) else getattr(
                tipo, "__name__", str(tipo))
            nome_esperado = nome_esperado.rstrip("_")

        try:
            self.valor()
        except FalhaDeExpectativa:
            raise
        except BaseException as e:          # noqa: BLE001 — e o objetivo
            nome = type(e).__name__.rstrip("_")
            texto = str(getattr(e, "message", None) or e)
            if nome_esperado and nome != nome_esperado:
                # A familia tambem serve: 'to_raise(RuntimeError)' aceita
                # DivisionByZeroError, como o 'handle' da linguagem.
                alvo = erro_por_nome(nome_esperado)
                if not (alvo and isinstance(e, alvo)):
                    if self._negado:
                        self._negado = False
                        return self
                    raise FalhaDeExpectativa(
                        f"devia levantar {nome_esperado}, e levantou {nome}: {texto}")
            if mensagem and mensagem not in texto:
                raise FalhaDeExpectativa(
                    f'a mensagem devia conter "{mensagem}", e foi "{texto}"')
            if self._negado:
                self._negado = False
                raise FalhaDeExpectativa(
                    f"nao devia levantar nada, e levantou {nome}: {texto}")
            self._negado = False
            return self

        if self._negado:
            self._negado = False
            return self
        alvo = f" {nome_esperado}" if nome_esperado else ""
        raise FalhaDeExpectativa(f"devia levantar{alvo}, e nao levantou nada")

    def to_not_raise(self):
        """A acao roda sem erro. O oposto util de to_raise."""
        if not callable(self.valor):
            raise FalhaDeExpectativa("to_not_raise precisa de uma acao")
        try:
            self.valor()
        except FalhaDeExpectativa:
            raise
        except BaseException as e:          # noqa: BLE001
            raise FalhaDeExpectativa(
                f"nao devia levantar nada, e levantou "
                f"{type(e).__name__.rstrip('_')}: {e}")
        return self

    # ── desempenho ──────────────────────────────────────────

    def to_finish_within(self, milissegundos):
        """A acao termina dentro do prazo."""
        if not callable(self.valor):
            raise FalhaDeExpectativa("to_finish_within precisa de uma acao")
        inicio = time.perf_counter()
        self.valor()
        gasto = (time.perf_counter() - inicio) * 1000
        return self._cobrar(gasto <= milissegundos,
                            f"terminar em ate {milissegundos}ms, "
                            f"e levou {gasto:.2f}ms")

    # ── saida ───────────────────────────────────────────────

    def to_print(self, esperado):
        """A acao imprime aquilo."""
        if not callable(self.valor):
            raise FalhaDeExpectativa("to_print precisa de uma acao")
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.valor()
        saida = buffer.getvalue().strip()
        return self._cobrar(esperado in saida,
                            f'imprimir "{esperado}", e imprimiu "{saida}"',
                            esperado)


# ═════════════════════════════════════════════════════════════
#  Dublês: mock, spy, stub
# ═════════════════════════════════════════════════════════════

class Dublê:
    """Um objeto que finge ser outro e anota o que lhe pediram.

    Serve para tres coisas que costumam se confundir:

        stub    devolve o que voce mandou devolver
        spy     deixa passar e anota as chamadas
        mock    as duas, mais expectativas sobre as chamadas

    Aqui e um objeto so, porque a diferenca entre eles e como se usa,
    nao o que sao — e obrigar a escolher o nome certo antes de escrever
    o teste atrapalha mais do que ajuda.
    """

    def __init__(self, nome="dublê", alvo=None):
        self.nome = nome
        self.alvo = alvo
        self.chamadas = []          # [(metodo, args, kwargs)]
        self.respostas = {}         # metodo -> valor ou lista de valores
        self.erros = {}             # metodo -> excecao a levantar
        self.passar_adiante = alvo is not None

    # ── programacao ──
    def quando(self, metodo):
        """Comeca a programar uma resposta: .quando("x").devolve(1)"""
        return _Programacao(self, metodo)

    def devolve(self, metodo, valor):
        self.respostas[metodo] = valor
        self.passar_adiante = False
        return self

    def levanta(self, metodo, erro):
        self.erros[metodo] = erro
        self.passar_adiante = False
        return self

    # ── uso ──
    def chamar(self, metodo, *args, **kwargs):
        self.chamadas.append((metodo, list(args), dict(kwargs)))
        if metodo in self.erros:
            erro = self.erros[metodo]
            raise erro if isinstance(erro, BaseException) else RuntimeError(str(erro))
        if metodo in self.respostas:
            resposta = self.respostas[metodo]
            if isinstance(resposta, _Sequencia):
                return resposta.proximo()
            return resposta
        if self.passar_adiante and self.alvo is not None:
            real = getattr(self.alvo, metodo, None)
            if callable(real):
                return real(*args, **kwargs)
        return None

    def __getattr__(self, nome):
        if nome.startswith("_"):
            raise AttributeError(nome)
        return lambda *a, **kw: self.chamar(nome, *a, **kw)

    # ── verificacao ──
    def vezes(self, metodo=None):
        if metodo is None:
            return len(self.chamadas)
        return sum(1 for c in self.chamadas if c[0] == metodo)

    def foi_chamado(self, metodo=None):
        return self.vezes(metodo) > 0

    def chamado_com(self, metodo, *args):
        return any(c[0] == metodo and c[1] == list(args) for c in self.chamadas)

    def argumentos_de(self, metodo):
        return [c[1] for c in self.chamadas if c[0] == metodo]

    def ultima_chamada(self):
        return list(self.chamadas[-1]) if self.chamadas else None

    def limpar(self):
        self.chamadas.clear()
        return self


class _Sequencia:
    """Respostas em fila: a 1a chamada devolve a 1a, e assim por diante."""

    def __init__(self, valores):
        self.valores = list(valores)
        self.i = 0

    def proximo(self):
        if not self.valores:
            return None
        valor = self.valores[min(self.i, len(self.valores) - 1)]
        self.i += 1
        return valor


class _Programacao:
    """O elo intermediario de dublê.quando("x").devolve(1)."""

    def __init__(self, duble, metodo):
        self.duble = duble
        self.metodo = metodo

    def devolve(self, valor):
        return self.duble.devolve(self.metodo, valor)

    def devolve_em_sequencia(self, valores):
        return self.duble.devolve(self.metodo, _Sequencia(valores))

    def levanta(self, erro):
        return self.duble.levanta(self.metodo, erro)


# ═════════════════════════════════════════════════════════════
#  A suite e o executor
# ═════════════════════════════════════════════════════════════

class Trial:
    """Um caso de teste."""

    __slots__ = ("nome", "corpo", "tags", "pendente", "focado", "repetir",
                 "prazo", "arquivo", "linha", "dados")

    def __init__(self, nome, corpo, tags=(), pendente="", focado=False,
                 repetir=1, prazo=0, arquivo="", linha=0, dados=None):
        self.nome = nome
        self.corpo = corpo
        self.tags = list(tags)
        self.pendente = pendente
        self.focado = focado
        self.repetir = repetir
        self.prazo = prazo
        self.arquivo = arquivo
        self.linha = linha
        self.dados = dados          # tabela de casos, para trials parametrizados


class Suite:
    """Um grupo de trials, com os ganchos e fixtures que eles veem.

    Suites aninham: a de dentro herda os ganchos da de fora, e roda os
    proprios depois. E a ordem que quem escreve espera — o 'before' mais
    geral prepara o terreno, o mais especifico ajusta.
    """

    def __init__(self, nome, pai=None):
        self.nome = nome
        self.pai = pai
        #: O quadro do trial em curso — um escopo novo por trial, que o
        #: 'setup' preenche e o corpo do trial le. E onde mora a
        #: garantia de isolamento: refazer o quadro apaga tudo o que o
        #: trial anterior escreveu, sem ninguem precisar limpar a mao.
        #:
        #: O interpretador o le pelas closures que registra aqui; o
        #: executor o troca antes de cada trial.
        self.quadro = None
        self.abrir_quadro = None    # o interpretador instala
        self.trials = []
        self.filhas = []
        self.antes_de_cada = []
        self.depois_de_cada = []
        self.antes_de_tudo = []
        self.depois_de_tudo = []
        self.fixtures = {}
        self.tags = []
        self.pendente = ""

    @property
    def caminho(self):
        if self.pai and self.pai.nome:
            return f"{self.pai.caminho} > {self.nome}"
        return self.nome

    def linhagem(self):
        """Da raiz ate aqui — a ordem em que os ganchos rodam."""
        cadeia = []
        atual = self
        while atual is not None:
            cadeia.append(atual)
            atual = atual.pai
        return list(reversed(cadeia))

    def fixture_de(self, nome):
        """Procura a fixture subindo pelas suites."""
        atual = self
        while atual is not None:
            if nome in atual.fixtures:
                return atual.fixtures[nome]
            atual = atual.pai
        return None

    def total(self):
        return len(self.trials) + sum(f.total() for f in self.filhas)


class Executor:
    """Roda as suites e junta os resultados.

    Fica separado da Suite de proposito: a suite descreve o que testar,
    o executor decide como. E o que permite '--aleatorio', '--repetir',
    '--so-falhas' e o filtro por tag sem tocar em nada que o usuario
    escreveu.
    """

    def __init__(self, semente=None, aleatorio=False, prazo_padrao=0,
                 filtro="", tags=(), sem_tags=(), parar_na_primeira=False,
                 capturar_saida=True, repetir=1):
        self.semente = semente if semente is not None else int(time.time())
        self.aleatorio = aleatorio
        self.prazo_padrao = prazo_padrao
        self.filtro = filtro.lower()
        self.tags = set(tags)
        self.sem_tags = set(sem_tags)
        self.parar_na_primeira = parar_na_primeira
        self.capturar_saida = capturar_saida
        self.repetir = repetir
        self.resultados = []
        self.inicio = 0.0
        self.fim = 0.0
        self._parar = False

    # ── selecao ─────────────────────────────────────────────

    def _selecionado(self, suite, trial):
        if self.filtro:
            alvo = f"{suite.caminho} {trial.nome}".lower()
            if self.filtro not in alvo:
                return False
        marcas = set(trial.tags) | set(suite.tags)
        if self.tags and not (marcas & self.tags):
            return False
        if self.sem_tags and (marcas & self.sem_tags):
            return False
        return True

    def _ha_focado(self, suite):
        """Algum trial pediu foco? Entao so os focados rodam."""
        if any(t.focado for t in suite.trials):
            return True
        return any(self._ha_focado(f) for f in suite.filhas)

    # ── execucao ────────────────────────────────────────────

    def rodar(self, raiz):
        self.inicio = time.perf_counter()
        so_focados = self._ha_focado(raiz)
        try:
            self._rodar_suite(raiz, so_focados)
        finally:
            self.fim = time.perf_counter()
        return self.resultados

    def _rodar_suite(self, suite, so_focados):
        if self._parar:
            return

        for gancho in suite.antes_de_tudo:
            self._chamar_gancho(gancho, suite, "before all")

        try:
            trials = list(suite.trials)
            if self.aleatorio:
                random.Random(self.semente).shuffle(trials)

            for trial in trials:
                if self._parar:
                    break
                if so_focados and not trial.focado:
                    continue
                if not self._selecionado(suite, trial):
                    continue
                self._rodar_trial(suite, trial)

            filhas = list(suite.filhas)
            if self.aleatorio:
                random.Random(self.semente + 1).shuffle(filhas)
            for filha in filhas:
                self._rodar_suite(filha, so_focados)
        finally:
            for gancho in suite.depois_de_tudo:
                self._chamar_gancho(gancho, suite, "after all")

    def _rodar_trial(self, suite, trial):
        vezes = max(trial.repetir, self.repetir)

        # Trial parametrizado: um resultado por linha da tabela.
        casos = trial.dados if trial.dados else [None]

        for caso in casos:
            nome = trial.nome
            if caso is not None:
                nome = f"{trial.nome} [{_texto(caso)}]"

            resultado = Resultado(suite.caminho, nome)
            resultado.tags = list(trial.tags) + list(suite.tags)
            resultado.arquivo = trial.arquivo
            resultado.linha = trial.linha
            resultado.tentativas = vezes

            if trial.pendente or suite.pendente:
                resultado.estado = PENDENTE
                resultado.motivo = trial.pendente or suite.pendente
                self.resultados.append(resultado)
                continue

            inicio = time.perf_counter()
            buffer = io.StringIO()
            limpezas = []

            try:
                for _ in range(vezes):
                    limpezas = []
                    contexto = {}
                    try:
                        self._preparar(suite, contexto, limpezas)
                        alvo = trial.corpo
                        if self.capturar_saida:
                            with redirect_stdout(buffer):
                                self._executar_corpo(alvo, contexto, caso)
                        else:
                            self._executar_corpo(alvo, contexto, caso)
                    finally:
                        # A limpeza roda na ordem inversa da preparacao,
                        # e roda mesmo com falha: senao um teste que
                        # estoura deixa a fixture aberta e derruba os
                        # proximos por um motivo que nao e deles.
                        self._limpar(suite, contexto, limpezas)

                resultado.estado = PASSOU

            except FalhaDeExpectativa as f:
                resultado.estado = FALHOU
                resultado.motivo = f.mensagem
                resultado.esperado = f.esperado
                resultado.obtido = f.obtido
                resultado.diferenca = f.diferenca
            except BaseException as e:      # noqa: BLE001
                resultado.estado = ERRO
                resultado.motivo = f"{type(e).__name__.rstrip('_')}: " \
                                   f"{getattr(e, 'message', None) or e}"
                resultado.erro = e
            finally:
                resultado.duracao = time.perf_counter() - inicio
                resultado.saida = buffer.getvalue()

            prazo = trial.prazo or self.prazo_padrao
            if prazo and resultado.estado == PASSOU:
                if resultado.duracao * 1000 > prazo:
                    resultado.estado = FALHOU
                    resultado.motivo = (
                        f"passou do prazo: {resultado.duracao*1000:.1f}ms "
                        f"para um limite de {prazo}ms")

            self.resultados.append(resultado)
            if self.parar_na_primeira and resultado.estado in (FALHOU, ERRO):
                self._parar = True
                return

    def _executar_corpo(self, corpo, contexto, caso):
        if caso is not None:
            try:
                corpo(caso)
                return
            except TypeError as e:
                if "argument" not in str(e):
                    raise
        corpo()

    def _preparar(self, suite, contexto, limpezas):
        # Um quadro limpo antes de tudo: e o que faz um trial nao ver o
        # que o anterior escreveu.
        if suite.abrir_quadro is not None:
            suite.abrir_quadro()

        # Os ganchos rodam da raiz para dentro: o 'setup' mais geral
        # prepara o terreno, o mais especifico ajusta. A ordem inversa
        # faria o ajuste ser sobrescrito pelo preparo.
        for nivel in suite.linhagem():
            for gancho in nivel.antes_de_cada:
                resultado = gancho(suite)
                if isinstance(resultado, dict):
                    contexto.update(resultado)

    def _limpar(self, suite, contexto, limpezas):
        erros = []
        for limpeza in reversed(limpezas):
            try:
                limpeza()
            except BaseException as e:      # noqa: BLE001
                erros.append(e)
        for nivel in reversed(suite.linhagem()):
            for gancho in nivel.depois_de_cada:
                try:
                    gancho(suite)
                except BaseException as e:  # noqa: BLE001
                    erros.append(e)
        if erros:
            raise erros[0]

    def _chamar_gancho(self, gancho, suite, qual):
        try:
            gancho(suite)
        except BaseException as e:          # noqa: BLE001
            resultado = Resultado(suite.caminho, f"<{qual}>", ERRO)
            resultado.motivo = f"{type(e).__name__.rstrip('_')}: {e}"
            resultado.erro = e
            self.resultados.append(resultado)

    # ── numeros ─────────────────────────────────────────────

    def resumo(self):
        contagem = {e: 0 for e in (PASSOU, FALHOU, ERRO, PENDENTE, IGNORADO)}
        for r in self.resultados:
            contagem[r.estado] = contagem.get(r.estado, 0) + 1
        return {
            "total": len(self.resultados),
            "passou": contagem[PASSOU],
            "falhou": contagem[FALHOU],
            "erro": contagem[ERRO],
            "pendente": contagem[PENDENTE],
            "ignorado": contagem[IGNORADO],
            "duracao": round(self.fim - self.inicio, 4),
            "semente": self.semente,
            "verde": contagem[FALHOU] == 0 and contagem[ERRO] == 0,
        }


# ═════════════════════════════════════════════════════════════
#  O relatorio
# ═════════════════════════════════════════════════════════════

def _cor(texto, codigo, colorir=True):
    return f"\033[{codigo}m{texto}\033[0m" if colorir and codigo else str(texto)


def _duracao(segundos):
    """Tempo em unidade legivel — ms para o rapido, s para o resto."""
    ms = segundos * 1000
    if ms < 1:
        return f"{ms*1000:.0f}µs"
    if ms < 1000:
        return f"{ms:.1f}ms"
    return f"{segundos:.2f}s"


def relatorio(executor, colorir=True, verboso=False, largura=78):
    """O relatorio completo, como texto.

    A ordem e deliberada: primeiro o que passou, resumido em uma linha
    por suite; depois cada falha com espaco para respirar. Quem roda a
    suite quer saber se esta verde; quando nao esta, quer o detalhe de
    cada uma — e nao rolar a tela procurando o vermelho no meio do
    verde.
    """
    linhas = []
    por_suite = {}
    for r in executor.resultados:
        por_suite.setdefault(r.suite, []).append(r)

    # ── passagem 1: o mapa ──
    for suite, resultados in por_suite.items():
        ruins = [r for r in resultados if r.estado in (FALHOU, ERRO)]
        simbolo = "✓" if not ruins else "✗"
        cor = "1;32" if not ruins else "1;31"
        tempo = sum(r.duracao for r in resultados)
        cabecalho = (f"  {_cor(simbolo, cor, colorir)} "
                     f"{_cor(suite or '(raiz)', '1;37', colorir)}  "
                     f"{_cor(f'{len(resultados)} trial(s), {_duracao(tempo)}', '0;90', colorir)}")
        linhas.append(cabecalho)

        for r in resultados:
            if r.estado == PASSOU and not verboso:
                continue
            marca, cor_marca = MARCA[r.estado]
            detalhe = ""
            if r.estado == PENDENTE and r.motivo:
                detalhe = _cor(f"  — {r.motivo}", "0;90", colorir)
            elif verboso:
                detalhe = _cor(f"  {_duracao(r.duracao)}", "0;90", colorir)
            linhas.append(f"      {_cor(marca, cor_marca, colorir)} "
                          f"{r.nome}{detalhe}")

    # ── passagem 2: as falhas, em detalhe ──
    ruins = [r for r in executor.resultados if r.estado in (FALHOU, ERRO)]
    if ruins:
        linhas.append("")
        linhas.append(_cor("─" * largura, "0;90", colorir))
        for i, r in enumerate(ruins, 1):
            marca, cor_marca = MARCA[r.estado]
            linhas.append("")
            linhas.append(f"  {_cor(f'{i})', cor_marca, colorir)} "
                          f"{_cor(r.caminho, '1;37', colorir)}")
            if r.arquivo:
                local = f"{os.path.relpath(r.arquivo)}:{r.linha}" if r.linha \
                    else os.path.relpath(r.arquivo)
                linhas.append(f"     {_cor(local, '0;90', colorir)}")
            linhas.append("")
            for linha in str(r.motivo).split("\n"):
                linhas.append(f"     {_cor(linha, cor_marca, colorir)}")
            if r.diferenca:
                linhas.append("")
                for linha in r.diferenca.split("\n"):
                    linhas.append(f"     {linha}")
            if r.saida.strip():
                linhas.append("")
                linhas.append(f"     {_cor('saida do trial:', '0;90', colorir)}")
                for linha in r.saida.strip().split("\n")[:10]:
                    linhas.append(f"       {_cor(linha, '0;90', colorir)}")

    # ── o placar ──
    n = executor.resumo()
    linhas.append("")
    linhas.append(_cor("─" * largura, "0;90", colorir))
    partes = []
    if n["passou"]:
        partes.append(_cor(f"{n['passou']} passou", "1;32", colorir))
    if n["falhou"]:
        partes.append(_cor(f"{n['falhou']} falhou", "1;31", colorir))
    if n["erro"]:
        partes.append(_cor(f"{n['erro']} com erro", "1;35", colorir))
    if n["pendente"]:
        partes.append(_cor(f"{n['pendente']} pendente", "1;33", colorir))
    linhas.append("  " + "  ".join(partes) +
                  _cor(f"   em {_duracao(n['duracao'])}", "0;90", colorir))
    if executor.aleatorio:
        linhas.append(_cor(f"  ordem aleatoria, semente {n['semente']} "
                           f"(--semente={n['semente']} repete)", "0;90", colorir))
    linhas.append("")
    return "\n".join(linhas)


def relatorio_junit(executor):
    """O mesmo resultado em JUnit XML, que todo CI sabe ler.

    Sem isto, integrar com GitHub Actions, GitLab ou Jenkins exigiria
    que cada um deles aprendesse o formato do Crucible — e nenhum vai
    aprender.
    """
    from xml.sax.saxutils import escape, quoteattr

    n = executor.resumo()
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              f'<testsuites tests="{n["total"]}" failures="{n["falhou"]}" '
              f'errors="{n["erro"]}" time="{n["duracao"]}">']

    por_suite = {}
    for r in executor.resultados:
        por_suite.setdefault(r.suite, []).append(r)

    for suite, resultados in por_suite.items():
        falhas = sum(1 for r in resultados if r.estado == FALHOU)
        erros = sum(1 for r in resultados if r.estado == ERRO)
        tempo = sum(r.duracao for r in resultados)
        linhas.append(f'  <testsuite name={quoteattr(suite or "raiz")} '
                      f'tests="{len(resultados)}" failures="{falhas}" '
                      f'errors="{erros}" time="{tempo:.4f}">')
        for r in resultados:
            linhas.append(f'    <testcase name={quoteattr(r.nome)} '
                          f'classname={quoteattr(r.suite or "raiz")} '
                          f'time="{r.duracao:.4f}">')
            if r.estado == FALHOU:
                linhas.append(f'      <failure message={quoteattr(str(r.motivo))}>'
                              f'{escape(r.diferenca)}</failure>')
            elif r.estado == ERRO:
                linhas.append(f'      <error message={quoteattr(str(r.motivo))}/>')
            elif r.estado == PENDENTE:
                linhas.append(f'      <skipped message={quoteattr(r.motivo)}/>')
            linhas.append('    </testcase>')
        linhas.append('  </testsuite>')

    linhas.append('</testsuites>')
    return "\n".join(linhas)


def relatorio_json(executor):
    """O resultado como JSON, para quem quer processar."""
    return json.dumps({
        "resumo": executor.resumo(),
        "resultados": [r.para_vault() for r in executor.resultados],
    }, ensure_ascii=False, indent=2)


def relatorio_tap(executor):
    """TAP 13 — o formato mais simples que existe, e o mais portavel."""
    linhas = [f"TAP version 13", f"1..{len(executor.resultados)}"]
    for i, r in enumerate(executor.resultados, 1):
        if r.estado == PASSOU:
            linhas.append(f"ok {i} - {r.caminho}")
        elif r.estado == PENDENTE:
            linhas.append(f"ok {i} - {r.caminho} # SKIP {r.motivo}")
        else:
            linhas.append(f"not ok {i} - {r.caminho}")
            linhas.append("  ---")
            linhas.append(f"  message: {r.motivo}")
            linhas.append("  ...")
    return "\n".join(linhas)


# ═════════════════════════════════════════════════════════════
#  Estado global — o que a sintaxe da linguagem alimenta
# ═════════════════════════════════════════════════════════════

class Registro:
    """A suite em construcao.

    A sintaxe ('crucible', 'trial', 'before') e as chamadas de
    biblioteca escrevem aqui. Ter um so registro e o que permite as
    duas formas conviverem no mesmo arquivo.
    """

    def __init__(self):
        self.raiz = Suite("")
        self.atual = self.raiz
        self.snapshots = {}
        self.arquivo_snapshots = ""

    def reiniciar(self):
        self.raiz = Suite("")
        self.atual = self.raiz

    def abrir_suite(self, nome):
        nova = Suite(nome, self.atual)
        self.atual.filhas.append(nova)
        self.atual = nova
        return nova

    def fechar_suite(self):
        if self.atual.pai is not None:
            self.atual = self.atual.pai


REGISTRO = Registro()


# ═════════════════════════════════════════════════════════════
#  Snapshots
# ═════════════════════════════════════════════════════════════

def _caminho_snapshot(arquivo):
    """Onde ficam os snapshots de um arquivo de teste."""
    pasta = os.path.join(os.path.dirname(arquivo) or ".", "__snapshots__")
    nome = os.path.basename(arquivo).replace(".df", "") + ".snap.json"
    return os.path.join(pasta, nome)


def carregar_snapshots(arquivo):
    caminho = _caminho_snapshot(arquivo)
    if not os.path.isfile(caminho):
        return {}
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def gravar_snapshots(arquivo, dados):
    caminho = _caminho_snapshot(arquivo)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, sort_keys=True,
                  default=str)


# ═════════════════════════════════════════════════════════════
#  Geradores de dados — para teste baseado em propriedade
# ═════════════════════════════════════════════════════════════

class Gerador:
    """Produz valores aleatorios de uma forma.

    E a base do teste por propriedade: em vez de escrever trinta casos
    a mao, descreve-se a regra que vale para todos e deixa-se a maquina
    procurar o contraexemplo.
    """

    def __init__(self, funcao, nome="valor"):
        self.funcao = funcao
        self.nome = nome

    def gerar(self, rng):
        return self.funcao(rng)

    def amostra(self, n=10, semente=None):
        rng = random.Random(semente)
        return [self.gerar(rng) for _ in range(n)]

    def mapear(self, f):
        return Gerador(lambda rng: f(self.funcao(rng)), f"{self.nome}*")

    def filtrar(self, cond, tentativas=100):
        def gerar(rng):
            for _ in range(tentativas):
                valor = self.funcao(rng)
                if cond(valor):
                    return valor
            raise RuntimeError(
                f"o gerador '{self.nome}' nao achou valor que passe no "
                f"filtro em {tentativas} tentativas")
        return Gerador(gerar, f"{self.nome}?")


def _encolher(valor):
    """Candidatos menores que o contraexemplo, do menor para o maior.

    Um contraexemplo de 900 digitos prova que ha bug e nao ajuda a
    achar; encolher devolve o menor valor que ainda falha, que
    costuma caber numa linha.
    """
    if isinstance(valor, bool):
        return []
    if isinstance(valor, int):
        candidatos = [0, 1, -1, valor // 2, valor - 1, valor + 1]
        return [c for c in candidatos if abs(c) < abs(valor)]
    if isinstance(valor, float):
        return [0.0, round(valor / 2, 6)]
    if isinstance(valor, str):
        if not valor:
            return []
        return ["", valor[:1], valor[:len(valor)//2]]
    if isinstance(valor, list):
        if not valor:
            return []
        return [[], valor[:1], valor[:len(valor)//2], valor[1:]]
    if isinstance(valor, dict):
        if not valor:
            return []
        chaves = list(valor)
        return [{}, {chaves[0]: valor[chaves[0]]}]
    return []


def verificar_propriedade(gerador, propriedade, casos=100, semente=None):
    """Procura um contraexemplo, e o encolhe ate o menor que ainda falha.

    Devolve (ok, contraexemplo, casos_rodados).
    """
    rng = random.Random(semente)
    for i in range(casos):
        valor = gerador.gerar(rng)
        try:
            if propriedade(valor) is False:
                return (False, _menor_que_falha(valor, propriedade), i + 1)
        except FalhaDeExpectativa:
            return (False, _menor_que_falha(valor, propriedade), i + 1)
        except BaseException:               # noqa: BLE001
            return (False, _menor_que_falha(valor, propriedade), i + 1)
    return (True, None, casos)


def _falha(valor, propriedade):
    try:
        return propriedade(valor) is False
    except BaseException:                   # noqa: BLE001
        return True


def _menor_que_falha(valor, propriedade, voltas=12):
    atual = valor
    for _ in range(voltas):
        menores = [c for c in _encolher(atual) if _falha(c, propriedade)]
        if not menores:
            break
        atual = min(menores, key=lambda v: len(str(v)))
    return atual


# ═════════════════════════════════════════════════════════════
#  A fachada — o que o DataForge ve como 'Crucible.*'
# ═════════════════════════════════════════════════════════════

class ArcaneCrucible(dict):
    """Crucible — o framework de testes.

    Duas formas de usar, e as duas escrevem no mesmo registro:

        crucible "nome":  ...        a sintaxe da linguagem
        Crucible.suite("nome")       a chamada de biblioteca
    """

    def __new__(cls):
        return {
            # ── montar a suite ──
            "suite": cls._suite,
            "describe": cls._suite,
            "trial": cls._trial,
            "test": cls._trial,
            "pending": cls._pending,
            "only": cls._only,
            "before": cls._before,
            "after": cls._after,
            "before_all": cls._before_all,
            "after_all": cls._after_all,
            "fixture": cls._fixture,
            "tag": cls._tag,
            "table": cls._table,

            # ── cobrar ──
            "expect": cls._expect,
            "fail": cls._fail,
            "check": cls._check,
            "approx": cls._approx,

            # ── dublês ──
            "mock": cls._mock,
            "spy": cls._spy,
            "stub": cls._stub,

            # ── propriedade ──
            "integers": cls._g_integers,
            "floats": cls._g_floats,
            "texts": cls._g_texts,
            "booleans": cls._g_booleans,
            "clusters": cls._g_clusters,
            "vaults": cls._g_vaults,
            "one_of": cls._g_one_of,
            "forall": cls._forall,

            # ── rodar ──
            "run": cls._run,
            "report": cls._report,
            "junit": cls._junit,
            "json": cls._json,
            "tap": cls._tap,
            "reset": cls._reset,
            "results": cls._results,
            "summary": cls._summary,

            # ── utilidades ──
            "capture": cls._capture,
            "timed": cls._timed,
            "benchmark": cls._benchmark,
            "diff": cls._diff,
            "freeze_time": cls._freeze_time,
            "temp_file": cls._temp_file,
        }

    # ── montar ──────────────────────────────────────────────

    @staticmethod
    def _suite(nome, corpo=None):
        """Abre uma suite. Com 'corpo', fecha ao terminar."""
        REGISTRO.abrir_suite(nome)
        if corpo is not None:
            try:
                corpo()
            finally:
                REGISTRO.fechar_suite()
        return nome

    @staticmethod
    def _trial(nome, corpo, tags=None, prazo=0, repetir=1, dados=None):
        REGISTRO.atual.trials.append(
            Trial(nome, corpo, tags or [], repetir=repetir, prazo=prazo,
                  dados=dados))
        return nome

    @staticmethod
    def _pending(nome, motivo="", corpo=None):
        REGISTRO.atual.trials.append(
            Trial(nome, corpo or (lambda: None), pendente=motivo or "pendente"))
        return nome

    @staticmethod
    def _only(nome, corpo, tags=None):
        REGISTRO.atual.trials.append(
            Trial(nome, corpo, tags or [], focado=True))
        return nome

    @staticmethod
    def _before(corpo):
        REGISTRO.atual.antes_de_cada.append(corpo)
        return corpo

    @staticmethod
    def _after(corpo):
        REGISTRO.atual.depois_de_cada.append(corpo)
        return corpo

    @staticmethod
    def _before_all(corpo):
        REGISTRO.atual.antes_de_tudo.append(corpo)
        return corpo

    @staticmethod
    def _after_all(corpo):
        REGISTRO.atual.depois_de_tudo.append(corpo)
        return corpo

    @staticmethod
    def _fixture(nome, corpo):
        REGISTRO.atual.fixtures[nome] = corpo
        return nome

    @staticmethod
    def _tag(*nomes):
        REGISTRO.atual.tags.extend(nomes)
        return list(nomes)

    @staticmethod
    def _table(nome, casos, corpo, tags=None):
        """Um trial por linha da tabela — o mesmo corpo, dados diferentes."""
        REGISTRO.atual.trials.append(
            Trial(nome, corpo, tags or [], dados=list(casos)))
        return nome

    # ── cobrar ──────────────────────────────────────────────

    @staticmethod
    def _expect(valor, rotulo=""):
        return Expectativa(valor, rotulo)

    @staticmethod
    def _fail(mensagem="falhou por decisao do teste"):
        raise FalhaDeExpectativa(str(mensagem))

    @staticmethod
    def _check(condicao, mensagem="a condicao nao se cumpriu"):
        if not condicao:
            raise FalhaDeExpectativa(str(mensagem))
        return True

    @staticmethod
    def _approx(valor, casas=7):
        """Um valor que se compara por aproximacao."""
        return _Aproximado(valor, casas)

    # ── dublês ──────────────────────────────────────────────

    @staticmethod
    def _mock(nome="mock", alvo=None):
        return Dublê(nome, alvo)

    @staticmethod
    def _spy(alvo, nome="spy"):
        return Dublê(nome, alvo)

    @staticmethod
    def _stub(respostas=None, nome="stub"):
        d = Dublê(nome)
        for metodo, valor in (respostas or {}).items():
            d.devolve(metodo, valor)
        return d

    # ── geradores ───────────────────────────────────────────

    @staticmethod
    def _g_integers(minimo=-1000, maximo=1000):
        return Gerador(lambda r: r.randint(minimo, maximo), "Integer")

    @staticmethod
    def _g_floats(minimo=-1000.0, maximo=1000.0):
        return Gerador(lambda r: r.uniform(minimo, maximo), "Float")

    @staticmethod
    def _g_texts(tamanho_max=20, alfabeto=None):
        letras = alfabeto or "abcdefghijklmnopqrstuvwxyz ÁÉÍÓÚçãõ"
        return Gerador(
            lambda r: "".join(r.choice(letras)
                              for _ in range(r.randint(0, tamanho_max))),
            "String")

    @staticmethod
    def _g_booleans():
        return Gerador(lambda r: r.choice([True, False]), "Boolean")

    @staticmethod
    def _g_clusters(item=None, tamanho_max=10):
        gerador = item or ArcaneCrucible._g_integers()
        return Gerador(
            lambda r: [gerador.gerar(r) for _ in range(r.randint(0, tamanho_max))],
            "Cluster")

    @staticmethod
    def _g_vaults(valor=None, tamanho_max=6):
        gv = valor or ArcaneCrucible._g_integers()
        gk = ArcaneCrucible._g_texts(6, "abcdefgh")
        return Gerador(
            lambda r: {gk.gerar(r): gv.gerar(r)
                       for _ in range(r.randint(0, tamanho_max))},
            "Vault")

    @staticmethod
    def _g_one_of(valores):
        return Gerador(lambda r: r.choice(list(valores)), "escolha")

    @staticmethod
    def _forall(gerador, propriedade, casos=100, semente=None):
        """Cobra que a propriedade valha para todo valor gerado."""
        ok, contra, rodados = verificar_propriedade(
            gerador, propriedade, casos, semente)
        if not ok:
            raise FalhaDeExpectativa(
                f"a propriedade falhou depois de {rodados} caso(s).\n"
                f"    menor contraexemplo: {_texto(contra)}",
                obtido=contra)
        return True

    # ── rodar ───────────────────────────────────────────────

    @staticmethod
    def _run(opcoes=None):
        o = opcoes or {}
        executor = Executor(
            semente=o.get("semente"),
            aleatorio=bool(o.get("aleatorio")),
            prazo_padrao=o.get("prazo", 0),
            filtro=o.get("filtro", ""),
            tags=o.get("tags", ()),
            sem_tags=o.get("sem_tags", ()),
            parar_na_primeira=bool(o.get("parar")),
            capturar_saida=o.get("capturar", True) is not False,
            repetir=o.get("repetir", 1),
        )
        executor.rodar(REGISTRO.raiz)
        ArcaneCrucible._ultimo = executor
        return executor.resumo()

    _ultimo = None

    @staticmethod
    def _report(colorir=True, verboso=False):
        if ArcaneCrucible._ultimo is None:
            return "nenhuma suite foi rodada ainda"
        return relatorio(ArcaneCrucible._ultimo, colorir, verboso)

    @staticmethod
    def _junit():
        return relatorio_junit(ArcaneCrucible._ultimo) if ArcaneCrucible._ultimo else ""

    @staticmethod
    def _json():
        return relatorio_json(ArcaneCrucible._ultimo) if ArcaneCrucible._ultimo else "{}"

    @staticmethod
    def _tap():
        return relatorio_tap(ArcaneCrucible._ultimo) if ArcaneCrucible._ultimo else ""

    @staticmethod
    def _reset():
        REGISTRO.reiniciar()
        ArcaneCrucible._ultimo = None
        return True

    @staticmethod
    def _results():
        if ArcaneCrucible._ultimo is None:
            return []
        return [r.para_vault() for r in ArcaneCrucible._ultimo.resultados]

    @staticmethod
    def _summary():
        return ArcaneCrucible._ultimo.resumo() if ArcaneCrucible._ultimo else {}

    # ── utilidades ──────────────────────────────────────────

    @staticmethod
    def _capture(acao):
        """Roda a acao e devolve {saida, erro, valor}."""
        saida, erro = io.StringIO(), io.StringIO()
        valor = None
        with redirect_stdout(saida), redirect_stderr(erro):
            valor = acao()
        return {"saida": saida.getvalue(), "erro": erro.getvalue(),
                "valor": valor}

    @staticmethod
    def _timed(acao, vezes=1):
        """Quanto tempo a acao leva, em milissegundos."""
        inicio = time.perf_counter()
        for _ in range(max(1, vezes)):
            acao()
        total = (time.perf_counter() - inicio) * 1000
        return {"total_ms": round(total, 4),
                "media_ms": round(total / max(1, vezes), 4),
                "vezes": vezes}

    @staticmethod
    def _benchmark(nome, acao, vezes=1000, aquecimento=10):
        """Mede com aquecimento e devolve as estatisticas que importam.

        Media sozinha engana: uma pausa do coletor de lixo no meio de
        mil voltas move a media e nao aparece. A mediana e o percentil
        95 contam a historia inteira.
        """
        for _ in range(aquecimento):
            acao()
        tempos = []
        for _ in range(vezes):
            inicio = time.perf_counter()
            acao()
            tempos.append((time.perf_counter() - inicio) * 1000)
        tempos.sort()
        n = len(tempos)
        return {
            "nome": nome,
            "vezes": vezes,
            "media_ms": round(sum(tempos) / n, 6),
            "mediana_ms": round(tempos[n // 2], 6),
            "min_ms": round(tempos[0], 6),
            "max_ms": round(tempos[-1], 6),
            "p95_ms": round(tempos[int(n * 0.95)], 6),
            "p99_ms": round(tempos[min(int(n * 0.99), n - 1)], 6),
            "ops_por_s": round(1000 / (sum(tempos) / n), 2) if sum(tempos) else 0,
        }

    @staticmethod
    def _diff(esperado, obtido):
        return diferenca(esperado, obtido)

    @staticmethod
    def _freeze_time(instante):
        """Congela o relogio num instante, para testes de data.

        Devolve um objeto com 'liberar()'. Sem isto, todo teste que
        toca data e hora falha uma vez por ano, na virada.
        """
        return _RelogioCongelado(instante)

    @staticmethod
    def _temp_file(conteudo="", sufixo=".txt"):
        """Um arquivo temporario que se apaga sozinho."""
        import tempfile
        fd, caminho = tempfile.mkstemp(suffix=sufixo)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(conteudo)
        return {"caminho": caminho,
                "apagar": lambda: os.path.exists(caminho) and os.remove(caminho)}


class _Aproximado:
    """Um numero que se compara com margem — para usar dentro de to_be."""

    def __init__(self, valor, casas=7):
        self.valor = float(valor)
        self.margem = 10 ** -casas

    def __eq__(self, outro):
        try:
            return abs(float(outro) - self.valor) < self.margem
        except (TypeError, ValueError):
            return False

    def __hash__(self):
        return hash(round(self.valor, 6))

    def __repr__(self):
        return f"~{self.valor}"


class _RelogioCongelado:
    """Troca time.time() por um instante fixo enquanto vale."""

    def __init__(self, instante):
        self.instante = float(instante)
        self._original = time.time
        time.time = lambda: self.instante

    def liberar(self):
        time.time = self._original
        return True
