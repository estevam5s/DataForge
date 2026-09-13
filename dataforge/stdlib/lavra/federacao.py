# -*- coding: utf-8 -*-
"""Federação: vários serviços, um esquema só para quem consulta.

O problema
----------
Cada time tem o seu serviço, e cada serviço tem o seu esquema. Quem
consulta não quer saber disso: ele quer `usuario.pedidos.itens` numa
consulta, sem descobrir que usuário mora num lugar e pedido em outro.

Como é feito aqui
-----------------
O portão **compõe** os esquemas: os tipos de cada serviço entram num
esquema só, e um campo que atravessa a fronteira é declarado como
extensão.

    portao := Lavra.portao()
    Lavra.juntar(portao, "contas", esquema_de_contas)
    Lavra.juntar(portao, "vendas", esquema_de_vendas)

    // vendas acrescenta 'pedidos' ao Usuario, que é de contas
    Lavra.estender(portao, "Usuario", "pedidos", "[Pedido!]!",
        resolve := lambda u, a, ctx => pedidos_do(u["id"]))

O que ele NÃO é
---------------
Não é o Apollo Federation. Não há `@key`, `@external`, `_entities` nem
plano de consulta distribuído: o portão aqui resolve a extensão
chamando o serviço dono, uma vez por fronteira, com o **lote** fazendo
o agrupamento. Um planejador de consulta distribuído é um projeto
próprio, e um subconjunto pela metade seria pior que a honestidade de
não ter.

Um conflito de nome é ERRO
--------------------------
Dois serviços que declaram `Usuario` param a composição. Fundir os dois
em silêncio faria a consulta devolver campos de um ou de outro conforme
a ordem do `juntar` — que é o pior jeito de falhar.
"""

from .esquema import Campo, ErroDeEsquema, Esquema


class Portao:
    """Os esquemas de vários serviços, compostos em um."""

    def __init__(self, nome="portao"):
        self.nome = nome
        self.esquema = Esquema(nome)
        self.donos = {}         # nome do tipo -> serviço
        self.servicos = {}
        self.extensoes = []

    def juntar(self, servico, esquema):
        if servico in self.servicos:
            raise ErroDeEsquema(f"o serviço '{servico}' já foi juntado")
        self.servicos[servico] = esquema

        for nome, tipo in esquema.tipos.items():
            if tipo.especie == "escalar" and nome in self.esquema.tipos:
                continue                       # escalar embutido: é o mesmo
            if nome in self.esquema.tipos:
                dono = self.donos.get(nome, "?")
                raise ErroDeEsquema(
                    f"'{nome}' é declarado por '{dono}' e por '{servico}'.\n"
                    f"  Dois tipos com o mesmo nome fariam a consulta devolver "
                    f"os campos de um ou de outro conforme a ordem do "
                    f"'juntar'.\n"
                    f"  Renomeie um dos dois, ou declare o tipo num serviço só "
                    f"e estenda-o do outro com Lavra.estender.")
            self.esquema.tipos[nome] = tipo
            self.donos[nome] = servico

        for qual, alvo in (("busca", self.esquema.busca),
                           ("mudanca", self.esquema.mudanca),
                           ("assinatura", self.esquema.assinatura)):
            origem = getattr(esquema, qual)
            for nome, campo in origem.campos.items():
                if nome in alvo.campos:
                    dono = self.donos.get(f"{qual}.{nome}", "?")
                    raise ErroDeEsquema(
                        f"a {qual} '{nome}' é declarada por '{dono}' e por "
                        f"'{servico}'")
                alvo.campos[nome] = campo
                self.donos[f"{qual}.{nome}"] = servico
        return self

    def estender(self, tipo_nome, campo_nome, tipo_do_campo, resolve=None,
                 args=None, descricao="", custo=1):
        """Acrescenta a um tipo de OUTRO serviço o campo que atravessa."""
        alvo = self.esquema.obter(tipo_nome)
        if alvo is None:
            raise ErroDeEsquema(
                f"nenhum serviço juntado declara '{tipo_nome}'.\n"
                f"  Há: {', '.join(sorted(self.esquema.tipos)) or 'nenhum'}")
        if campo_nome in alvo.campos:
            raise ErroDeEsquema(
                f"'{tipo_nome}.{campo_nome}' já existe — quem o declarou foi "
                f"'{self.donos.get(tipo_nome, '?')}'")
        alvo.campos[campo_nome] = Campo(campo_nome, tipo_do_campo, args or {},
                                        resolve, descricao, "", custo)
        self.extensoes.append((tipo_nome, campo_nome))
        return alvo.campos[campo_nome]

    def conferir(self):
        return self.esquema.conferir()

    def mapa(self):
        """Quem declara o quê. É a resposta para 'de onde vem este campo?'."""
        return {
            "servicos": sorted(self.servicos),
            "tipos": {nome: self.donos.get(nome, "?")
                      for nome in sorted(self.esquema.tipos)
                      if self.esquema.tipos[nome].especie != "escalar"
                      or nome in self.donos},
            "extensoes": [{"tipo": t, "campo": c} for t, c in self.extensoes],
        }


def portao(nome="portao"):
    return Portao(nome)


def juntar(p, servico, esquema):
    return p.juntar(servico, esquema)


def estender(p, tipo_nome, campo_nome, tipo_do_campo, resolve=None, args=None,
             descricao="", custo=1):
    return p.estender(tipo_nome, campo_nome, tipo_do_campo, resolve, args,
                      descricao, custo)


def mapa(p):
    return p.mapa()
