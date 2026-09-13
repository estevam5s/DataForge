# -*- coding: utf-8 -*-
"""O Lote — o que impede o N+1.

O problema, em uma frase
------------------------
Uma consulta que pede 50 pedidos e, de cada um, o cliente, faz 51
consultas ao banco: uma para os pedidos e uma por cliente. O servidor
parece rápido e o banco morre.

A solução, em uma frase
-----------------------
O resolvedor não busca — ele **pede**. Os pedidos feitos na mesma volta
são juntados num só, e cada um recebe a sua parte.

    clientes := Lavra.lote(ctx, "clientes", lambda ids => Banco.varios(ids))

    Lavra.campo(esq, "Pedido", "cliente", "Cliente!",
        resolve := lambda p, a, ctx => Lavra.pedir(ctx, "clientes", p.cliente_id))

Duas decisões
-------------
1. **O lote vive no CONTEXTO, e não no módulo.** Um lote de processo
   guardaria o cliente de um pedido depois que ele mudou, e serviria o
   valor velho para outra pessoa. O contexto morre com a consulta, que
   é exatamente a vida útil que um cache de leitura pode ter aqui.

2. **A ordem da resposta é a ordem do pedido.** A função de lote recebe
   as chaves e devolve os valores na MESMA ordem, ou um vault de
   chave → valor. Devolver uma lista fora de ordem é o bug clássico
   dessa técnica: cada pedido recebe o cliente de outro, e nada falha.
"""


class ErroDeLote(Exception):
    pass


class Lote:
    """Uma fila de chaves e a função que resolve todas de uma vez."""

    __slots__ = ("nome", "buscar", "fila", "cache", "chamadas", "chaves_vistas")

    def __init__(self, nome, buscar):
        self.nome = nome
        self.buscar = buscar
        self.fila = []
        self.cache = {}
        self.chamadas = 0
        self.chaves_vistas = 0

    def pedir(self, chave):
        """Enfileira a chave e devolve uma promessa a ser cobrada depois."""
        self.chaves_vistas += 1
        if chave in self.cache:
            return Promessa(self, chave, pronta=True)
        if chave not in self.fila:
            self.fila.append(chave)
        return Promessa(self, chave)

    def resolver(self):
        """Executa a busca pendente. Uma chamada para a fila inteira."""
        if not self.fila:
            return
        chaves = list(self.fila)
        self.fila = []
        self.chamadas += 1
        resposta = self.buscar(chaves)

        if isinstance(resposta, dict):
            for chave in chaves:
                self.cache[chave] = resposta.get(chave)
            return

        valores = list(resposta) if resposta is not None else []
        if len(valores) != len(chaves):
            raise ErroDeLote(
                f"o lote '{self.nome}' recebeu {len(chaves)} chave(s) e "
                f"devolveu {len(valores)} valor(es).\n"
                f"  Devolva um valor por chave, NA MESMA ORDEM — ou um vault "
                f"de chave para valor, que não depende de ordem nenhuma.\n"
                f"  Uma lista fora de ordem não falha: cada um recebe o dado "
                f"de outro, calado.")
        for chave, valor in zip(chaves, valores):
            self.cache[chave] = valor

    def valor(self, chave):
        if chave not in self.cache:
            self.resolver()
        return self.cache.get(chave)

    def preencher(self, chave, valor):
        """Põe um valor que já se tem — evita ir buscar o que já veio."""
        self.cache[chave] = valor
        if chave in self.fila:
            self.fila.remove(chave)
        return valor

    def esquecer(self, chave=None):
        if chave is None:
            self.cache.clear()
        else:
            self.cache.pop(chave, None)

    @property
    def economia(self):
        """Quantas idas ao banco o lote poupou."""
        return max(0, self.chaves_vistas - self.chamadas)


class Promessa:
    """O valor que ainda não chegou. Cobrada quando o campo é serializado."""

    __slots__ = ("lote", "chave", "pronta")

    def __init__(self, lote, chave, pronta=False):
        self.lote = lote
        self.chave = chave
        self.pronta = pronta

    def cobrar(self):
        return self.lote.valor(self.chave)

    def __repr__(self):
        return f"<promessa {self.lote.nome}[{self.chave}]>"


class Registro:
    """Os lotes de UMA consulta. Vive no contexto e morre com ele."""

    def __init__(self):
        self.lotes = {}

    def lote(self, nome, buscar):
        if nome not in self.lotes:
            self.lotes[nome] = Lote(nome, buscar)
        return self.lotes[nome]

    def pedir(self, nome, chave):
        if nome not in self.lotes:
            raise ErroDeLote(
                f"não há lote chamado '{nome}' nesta consulta.\n"
                f"  Declare-o antes: Lavra.lote(ctx, '{nome}', lambda ids => …)\n"
                f"  Há: {', '.join(sorted(self.lotes)) or 'nenhum'}")
        return self.lotes[nome].pedir(chave)

    def resolver_tudo(self):
        for lote in self.lotes.values():
            lote.resolver()

    def resumo(self):
        return {nome: {"chamadas": l.chamadas, "chaves": l.chaves_vistas,
                       "economia": l.economia}
                for nome, l in self.lotes.items()}
