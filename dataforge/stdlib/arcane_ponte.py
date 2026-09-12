"""Arcane.Ponte — o lado programático da ponte para o Python.

`adopt Python.numpy as np` resolve o caso comum: trazer um módulo. Este
módulo resolve os outros três.

**Perguntar antes de depender.** `Ponte.tem("numpy")` responde sem
levantar erro, e é o que permite um programa se adaptar em vez de
morrer:

    given Ponte.tem("numpy"):
        adopt Python.numpy as np
        resultado := np.array(dados).mean()
    otherwise:
        resultado := dados >> distill a, v: a + v 0 / len(dados)

**Explorar.** `Ponte.atributos`, `Ponte.doc` e `Ponte.assinatura` leem o
que o pacote oferece de dentro da linguagem. Sem elas, descobrir o que
existe do outro lado exige sair do DataForge e abrir a documentação do
pacote — e no REPL isso é a diferença entre experimentar e desistir.

**Converter quando quiser.** A ponte não converte sozinha (é o que
mantém o `ndarray` sendo um `ndarray`), então `Ponte.cluster` e
`Ponte.vault` existem para quando a resposta precisa entrar no
vocabulário da linguagem. Serem explícitas é o ponto: a linha diz onde
se paga a cópia.
"""

import inspect

from .. import ponte


class ArcanePonte:
    """A ponte para o Python, como valores."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Ponte",

            # ── Perguntar ──
            "tem": cls._tem,
            "versao": cls._versao,
            "onde": ponte.onde,
            "empacotado": ponte.empacotado,

            # ── Trazer ──
            "importar": cls._importar,

            # ── Explorar ──
            "atributos": ponte.atributos,
            "doc": cls._doc,
            "assinatura": cls._assinatura,
            "tipo": ponte.tipo_de,
            "chamavel": lambda x: callable(x),

            # ── Converter ──
            "cluster": ponte.para_cluster,
            "vault": ponte.para_vault,
        }

    @staticmethod
    def _tem(nome):
        return ponte.tem(nome)

    @staticmethod
    def _versao(nome):
        return ponte.versao(nome)

    @staticmethod
    def _importar(nome):
        """O módulo, como valor — para quando o nome só se sabe rodando.

        `adopt` precisa do nome escrito na linha, o que é quase sempre o
        certo: ler o arquivo basta para saber o que ele importa. Quando
        o nome vem de uma configuração, é aqui.
        """
        completo = nome if nome.startswith(ponte.PREFIXO + ".") \
            else f"{ponte.PREFIXO}.{nome}"
        return ponte.importar(completo)

    @staticmethod
    def _doc(valor):
        """A documentação que o próprio Python carrega no objeto."""
        alvo = valor.cru if isinstance(valor, ponte.ModuloPython) else valor
        texto = inspect.getdoc(alvo)
        return texto if texto else None

    @staticmethod
    def _assinatura(valor):
        """Como se chama — `(a, b, *, chave=None)` — ou `void`.

        Função escrita em C muitas vezes não declara a assinatura, e aí
        não há o que devolver. Devolver `void` é mais honesto que
        inventar `(…)`: quem pergunta fica sabendo que a resposta não
        existe, em vez de achar que a função não tem argumento.
        """
        alvo = valor.cru if isinstance(valor, ponte.ModuloPython) else valor
        try:
            return f"{getattr(alvo, '__name__', '')}{inspect.signature(alvo)}"
        except (TypeError, ValueError):
            return None
