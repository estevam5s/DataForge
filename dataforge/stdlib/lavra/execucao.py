# -*- coding: utf-8 -*-
"""Executar uma consulta: percorrer a seleção e chamar quem resolve.

Três decisões que valem lembrar
-------------------------------
1. **Um erro não derruba a resposta inteira.** O campo que falhou vira
   `void`, o erro entra na lista com o CAMINHO até ele
   (`usuario.pedidos.2.total`), e o resto da consulta continua. Quem
   pediu dez campos e teve um problema num recebe nove — não zero.

   A exceção é o campo `!`: ele prometeu nunca ser `void`, então um erro
   ali sobe para o pai, e daí para cima, até achar alguém que admita
   `void`. É a única forma de a promessa do `!` valer alguma coisa.

2. **A resposta preserva a ordem em que os campos foram pedidos.** Não é
   detalhe estético: quem consome uma resposta costuma exibi-la na
   ordem, e um vault que embaralha faz a tela mudar de consulta para
   consulta sem ninguém ter mexido nela.

3. **O limite é conferido ANTES de resolver qualquer coisa.** Uma
   consulta de profundidade 40 num grafo cíclico é a forma mais barata
   de derrubar um servidor de consulta, e descobrir isso resolvendo já
   é tarde.
"""

import re
import time

from .consulta import ErroDeConsulta, Selecao, Variavel, SEM
from .esquema import (ErroDeEsquema, ler_tipo, padrao_do_argumento,
                      SEM_PADRAO, _tipo_do_argumento)
from .lote import Promessa, Registro


class ErroDeExecucao(BaseException):
    """Uma falha com caminho: quem consome sabe QUAL campo quebrou.

    Deriva de `BaseException`, como `halt` e `skip` da linguagem e como
    o `_Parar` da Vitrine — e pelo mesmo motivo. O interpretador
    embrulha toda `Exception` que sai de uma função Python num
    `RuntimeError_`, e `Lavra.erro("faltou saldo")` dentro de um
    resolvedor saía assim:

        RuntimeError_ [line 52, col 36]: erro: faltou saldo

    O nome da classe interna e a posição no arquivo do módulo, dentro
    de uma mensagem que vai para quem CONSULTA — que nunca viu nem uma
    coisa nem outra. Este erro não é uma falha do programa: é o valor
    que o campo tem a dizer, e ele viaja até a lista `erros` inteiro.
    """

    def __init__(self, mensagem, caminho=None, codigo="erro", extras=None):
        self.mensagem = mensagem
        self.caminho = list(caminho or [])
        self.codigo = codigo
        self.extras = extras or {}
        super().__init__(mensagem)

    def como_vault(self):
        saida = {"mensagem": self.mensagem, "caminho": self.caminho,
                 "codigo": self.codigo}
        if self.extras:
            saida["extra"] = self.extras
        return saida


class Recusado(ErroDeExecucao):
    """Autorização: quem pediu não pode ver isto."""

    def __init__(self, mensagem="sem permissão", caminho=None, extras=None):
        super().__init__(mensagem, caminho, "recusado", extras)


class Contexto:
    """O que atravessa a consulta inteira: quem pediu, e o que ela acumulou.

    Ele é um vault de verdade para quem escreve o resolvedor — `ctx["usuario"]`
    funciona — e carrega por dentro o registro de lotes e a lista de erros.
    """

    def __init__(self, dados=None, esquema=None):
        self.dados = dict(dados or {})
        self.esquema = esquema
        self.lotes = Registro()
        self.erros = []
        self.inicio = time.perf_counter()
        self.campos_resolvidos = 0
        self.extensoes = {}

    # Um Contexto se comporta como vault dentro da linguagem.
    def __getitem__(self, chave):
        return self.dados[chave]

    def __setitem__(self, chave, valor):
        self.dados[chave] = valor

    def __contains__(self, chave):
        return chave in self.dados

    def __iter__(self):
        return iter(self.dados)

    def __len__(self):
        return len(self.dados)

    def get(self, chave, padrao=None):
        return self.dados.get(chave, padrao)

    def keys(self):
        return self.dados.keys()

    def items(self):
        return self.dados.items()

    def values(self):
        return self.dados.values()

    @property
    def ms(self):
        return round((time.perf_counter() - self.inicio) * 1000, 3)


# ── Ler um campo de um valor qualquer ──────────────────────────

def valor_do_campo(objeto, nome):
    """O campo `nome` de um record, de um vault, de uma instância ou de um objeto.

    A ordem importa: o vault vem primeiro porque um resolvedor que
    devolve `{"nome": …}` é o caso mais comum, e ir perguntar atributo
    antes acharia métodos do próprio dicionário.
    """
    if objeto is None:
        return None
    if isinstance(objeto, dict):
        return objeto.get(nome)
    for atributo in ("values", "fields"):
        campos = getattr(objeto, atributo, None)
        if isinstance(campos, dict) and nome in campos:
            return campos[nome]
    if hasattr(objeto, "get") and not isinstance(objeto, (str, bytes)):
        try:
            achado = objeto.get(nome)
            if achado is not None:
                return achado
        except Exception:               # noqa: BLE001
            pass
    return getattr(objeto, nome, None)


def _quantos_aceita(funcao, teto):
    """Quantos dos `teto` argumentos esta ação aceita.

    Perguntado ANTES, e não descoberto tentando. A primeira versão
    chamava com três, pegava o `TypeError` e tentava com dois — e nunca
    funcionou: o erro de aridade de uma ação da linguagem não é um
    `TypeError` do Python, é um `TypeError_` do interpretador, e o
    `except` não o via.

    Tentar-e-errar também engoliria um `TypeError` de VERDADE vindo de
    dentro do resolvedor, que é o pior tipo de silêncio: o campo
    voltaria com o valor de uma chamada com menos argumentos.
    """
    params = getattr(funcao, "params", None)
    if isinstance(params, (list, tuple)):
        return min(len(params), teto)
    import inspect
    try:
        assinatura = inspect.signature(funcao)
    except (ValueError, TypeError):
        return teto
    quantos = 0
    for p in assinatura.parameters.values():
        if p.kind is p.VAR_POSITIONAL:
            return teto
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD):
            quantos += 1
    return min(quantos, teto)


def _chamar(funcao, *args):
    """Chama o resolvedor com quantos argumentos ele aceitar.

    Um resolvedor de campo simples não quer receber três coisas:

        lambda p => p.total            um argumento
        lambda p, a => …               dois
        lambda p, a, ctx => …          três

    Exigir os três faria toda linha ter um `_, _` que não diz nada — e
    o `lint` reclamaria de cada um deles, com razão.
    """
    return funcao(*args[:_quantos_aceita(funcao, len(args))])


# ── Coerção de entrada ─────────────────────────────────────────

def coagir_entrada(esquema, valor, ref, caminho, onde):
    """Confere e converte um argumento contra o tipo declarado."""
    ref = ler_tipo(ref)

    if valor is None:
        if ref.obrigatorio:
            raise ErroDeExecucao(
                f"{onde} é '{ref}' e recebeu void", caminho, "argumento")
        return None

    if ref.lista:
        if isinstance(valor, (str, bytes)) or not hasattr(valor, "__iter__"):
            # Um item onde se espera lista vira lista de um. É o que o
            # GraphQL faz, e poupa o cliente de escrever [x] no caso
            # esmagadoramente mais comum.
            valor = [valor]
        return [coagir_entrada(esquema, item, ref.de, caminho + [str(i)], onde)
                for i, item in enumerate(valor)]

    tipo = esquema.obter(ref.nome)
    if tipo is None:
        raise ErroDeExecucao(f"o tipo '{ref.nome}' não existe no esquema",
                             caminho, "esquema")

    if tipo.especie == "escalar":
        return _coagir_escalar(tipo, valor, caminho, onde)

    if tipo.especie == "enum":
        if valor in tipo.valores:
            return tipo.valores[valor]
        if valor in tipo.valores.values():
            return valor
        nomes = ", ".join(tipo.valores) or "nenhum"
        raise ErroDeExecucao(
            f"{onde}: '{valor}' não é um valor de {tipo.nome}", caminho,
            "argumento", {"aceita": list(tipo.valores)})

    if tipo.especie == "entrada":
        if not isinstance(valor, dict):
            raise ErroDeExecucao(
                f"{onde} é a entrada '{tipo.nome}' e recebeu um valor solto",
                caminho, "argumento")
        saida = {}
        for nome, campo in tipo.campos.items():
            if nome in valor:
                saida[nome] = coagir_entrada(esquema, valor[nome], campo.tipo,
                                             caminho + [nome],
                                             f"{tipo.nome}.{nome}")
            else:
                padrao = padrao_do_argumento(campo.argumentos or {})
                if padrao is not SEM_PADRAO:
                    saida[nome] = padrao
                elif ler_tipo(campo.tipo).obrigatorio:
                    raise ErroDeExecucao(
                        f"a entrada '{tipo.nome}' exige o campo '{nome}'",
                        caminho, "argumento")
        sobrando = [k for k in valor if k not in tipo.campos]
        if sobrando:
            # RECUSAR, e não ignorar: um campo com o nome quase certo
            # ('emial') seria descartado em silêncio e o dado não
            # chegaria, sem nada denunciando.
            raise ErroDeExecucao(
                f"a entrada '{tipo.nome}' não tem o campo "
                f"'{sobrando[0]}'", caminho, "argumento",
                {"aceita": list(tipo.campos)})
        return saida

    raise ErroDeExecucao(
        f"{onde} é '{tipo.nome}', que é um {tipo.especie} — tipos de saída "
        f"não podem ser argumento", caminho, "esquema")


def _coagir_escalar(tipo, valor, caminho, onde):
    if tipo.desserializar is not None:
        return tipo.desserializar(valor)
    nome = tipo.nome
    if nome == "Boolean":
        if isinstance(valor, bool):
            return valor
        raise ErroDeExecucao(f"{onde} é Boolean e recebeu '{valor}'",
                             caminho, "argumento")
    if nome == "Integer":
        if isinstance(valor, bool):
            raise ErroDeExecucao(f"{onde} é Integer e recebeu um Boolean",
                                 caminho, "argumento")
        if isinstance(valor, int):
            return valor
        if isinstance(valor, float) and valor.is_integer():
            return int(valor)
        raise ErroDeExecucao(f"{onde} é Integer e recebeu '{valor}'",
                             caminho, "argumento")
    if nome == "Float":
        if isinstance(valor, bool):
            raise ErroDeExecucao(f"{onde} é Float e recebeu um Boolean",
                                 caminho, "argumento")
        if isinstance(valor, (int, float)):
            return float(valor)
        raise ErroDeExecucao(f"{onde} é Float e recebeu '{valor}'",
                             caminho, "argumento")
    if nome == "String":
        if isinstance(valor, str):
            return valor
        raise ErroDeExecucao(f"{onde} é String e recebeu '{valor}'",
                             caminho, "argumento")
    if nome == "ID":
        if isinstance(valor, (str, int)) and not isinstance(valor, bool):
            return valor
        raise ErroDeExecucao(f"{onde} é ID e recebeu '{valor}'",
                             caminho, "argumento")
    return valor


# ── Coerção de saída ───────────────────────────────────────────

def _serializar_escalar(tipo, valor):
    if tipo.serializar is not None:
        return tipo.serializar(valor)
    nome = tipo.nome
    if nome == "String":
        return valor if isinstance(valor, str) else str(valor)
    if nome == "Integer":
        return int(valor)
    if nome == "Float":
        return float(valor)
    if nome == "Boolean":
        return bool(valor)
    return valor


# ── O executor ─────────────────────────────────────────────────

class Execucao:
    def __init__(self, esquema, documento, variaveis=None, contexto=None,
                 raiz=None, operacao=None):
        self.esquema = esquema
        self.documento = documento
        self.operacao = documento.operacao(operacao)
        self.contexto = (contexto if isinstance(contexto, Contexto)
                         else Contexto(contexto, esquema))
        self.contexto.esquema = esquema
        self.raiz = raiz
        self.variaveis = self._coagir_variaveis(variaveis or {})
        self.erros = self.contexto.erros

    # ── variáveis ──────────────────────────────────────────

    def _coagir_variaveis(self, dados):
        saida = {}
        for nome, decl in self.operacao.variaveis.items():
            ref = ler_tipo(decl["tipo"])
            if nome in dados and dados[nome] is not None:
                saida[nome] = coagir_entrada(self.esquema, dados[nome], ref,
                                             [nome], f"a variável ${nome}")
            elif decl["padrao"] is not SEM:
                saida[nome] = decl["padrao"]
            elif ref.obrigatorio:
                raise ErroDeExecucao(
                    f"a variável ${nome} é '{ref}' e não foi passada",
                    [nome], "variavel")
            else:
                saida[nome] = None
        sobrando = [k for k in dados if k not in self.operacao.variaveis]
        if sobrando:
            raise ErroDeExecucao(
                f"a operação não declara a variável '{sobrando[0]}'",
                [], "variavel",
                {"declaradas": list(self.operacao.variaveis)})
        return saida

    def _resolver_valor(self, valor):
        """Troca `$x` pelo valor da variável, em qualquer profundidade."""
        if isinstance(valor, Variavel):
            if valor.nome not in self.variaveis:
                raise ErroDeExecucao(
                    f"a variável ${valor.nome} não foi declarada pela operação",
                    [], "variavel",
                    {"declaradas": list(self.operacao.variaveis)})
            return self.variaveis[valor.nome]
        if isinstance(valor, list):
            return [self._resolver_valor(v) for v in valor]
        if isinstance(valor, dict):
            return {k: self._resolver_valor(v) for k, v in valor.items()}
        return valor

    # ── diretivas ──────────────────────────────────────────

    def _passa_nas_diretivas(self, selecao):
        for diretiva in selecao.diretivas:
            nome = diretiva["nome"]
            args = {k: self._resolver_valor(v)
                    for k, v in diretiva["argumentos"].items()}
            if nome in ("incluir", "include"):
                if not args.get("se", args.get("if", True)):
                    return False
            elif nome in ("pular", "skip"):
                if args.get("se", args.get("if", False)):
                    return False
            elif nome in self.esquema.diretivas:
                if self.esquema.diretivas[nome](args, self.contexto) is False:
                    return False
            else:
                raise ErroDeExecucao(
                    f"não existe a diretiva @{nome}", [], "diretiva",
                    {"existem": ["incluir", "pular",
                                 *sorted(self.esquema.diretivas)]})
        return True

    # ── expandir trechos ───────────────────────────────────

    def _expandir(self, selecoes, nome_do_tipo, vistos=None):
        """Resolve `...Trecho` e `... em Tipo:` numa lista plana de campos."""
        vistos = vistos or set()
        saida = []
        for selecao in selecoes:
            if not self._passa_nas_diretivas(selecao):
                continue
            if selecao.trecho:
                if selecao.trecho in vistos:
                    raise ErroDeExecucao(
                        f"o trecho '{selecao.trecho}' usa a si mesmo",
                        [], "consulta",
                        {"dica": "um trecho que se expande sem fim trava o "
                                 "servidor antes de responder"})
                trecho = self.documento.trechos.get(selecao.trecho)
                if trecho is None:
                    raise ErroDeExecucao(
                        f"não há trecho chamado '{selecao.trecho}'", [],
                        "consulta",
                        {"existem": sorted(self.documento.trechos)})
                if not self._tipo_casa(trecho.tipo, nome_do_tipo):
                    continue
                saida.extend(self._expandir(trecho.selecoes, nome_do_tipo,
                                            vistos | {selecao.trecho}))
                continue
            if selecao.tipo_condicional:
                if not self._tipo_casa(selecao.tipo_condicional, nome_do_tipo):
                    continue
                saida.extend(self._expandir(selecao.selecoes, nome_do_tipo,
                                            vistos))
                continue
            saida.append(selecao)
        return _juntar_iguais(saida)

    def _tipo_casa(self, pedido, concreto):
        if pedido == concreto:
            return True
        tipo = self.esquema.obter(concreto)
        if tipo is None:
            return False
        if pedido in tipo.contratos:
            return True
        alvo = self.esquema.obter(pedido)
        if alvo is not None and alvo.especie == "uniao":
            return concreto in alvo.membros
        return False

    # ── limites ────────────────────────────────────────────

    def conferir_limites(self):
        profundidade = _profundidade(self.operacao.selecoes, self.documento)
        maximo = self.esquema.limites.get("profundidade", 12)
        if profundidade > maximo:
            raise ErroDeExecucao(
                f"a consulta tem profundidade {profundidade}, e o limite é "
                f"{maximo}", [], "limite",
                {"dica": "um grafo com ciclo deixa pedir 'usuario.pedidos."
                         "cliente.pedidos…' para sempre; o limite é o que "
                         "impede uma consulta de derrubar o servidor"})
        custo = self._custo(self.operacao.selecoes, self._raiz_do_tipo())
        teto = self.esquema.limites.get("complexidade", 1000)
        if custo > teto:
            raise ErroDeExecucao(
                f"a consulta custa {custo}, e o teto é {teto}", [], "limite",
                {"dica": "campos que devolvem lista multiplicam o custo pelo "
                         "argumento de limite"})
        return {"profundidade": profundidade, "complexidade": custo}

    def _custo(self, selecoes, nome_do_tipo, multiplicador=1):
        total = 0
        tipo = self.esquema.obter(nome_do_tipo)
        for selecao in selecoes:
            if selecao.trecho or selecao.tipo_condicional:
                trecho = (self.documento.trechos.get(selecao.trecho)
                          if selecao.trecho else selecao)
                if trecho is not None:
                    total += self._custo(trecho.selecoes, nome_do_tipo,
                                         multiplicador)
                continue
            campo = tipo.campos.get(selecao.nome) if tipo else None
            peso = campo.complexidade if campo else 1
            total += peso * multiplicador
            if selecao.selecoes and campo is not None:
                ref = ler_tipo(campo.tipo)
                fator = multiplicador
                if ref.lista:
                    bruto = selecao.argumentos.get("limite",
                                                   selecao.argumentos.get("primeiros"))
                    valor = self._resolver_valor(bruto) if bruto is not None else None
                    fator = multiplicador * (valor if isinstance(valor, int)
                                             else 10)
                total += self._custo(selecao.selecoes, ref.nome_base, fator)
        return total

    def _raiz_do_tipo(self):
        return {"busca": "Busca", "mudanca": "Mudanca",
                "assinatura": "Assinatura"}[self.operacao.especie]

    # ── rodar ──────────────────────────────────────────────

    def rodar(self):
        metricas = self.conferir_limites()
        raiz_tipo = self.esquema.obter(self._raiz_do_tipo())
        if not raiz_tipo.campos:
            raise ErroDeExecucao(
                f"o esquema não tem nenhuma {self.operacao.especie}",
                [], "esquema")

        selecoes = self._expandir(self.operacao.selecoes, raiz_tipo.nome)
        # A MUDANÇA é serial, e a busca também: um resolvedor que escreve
        # e outro que lê o mesmo dado, rodando juntos, daria resultado
        # dependente de ordem — e este executor é de uma thread só, então
        # a garantia é de graça e vale declará-la.
        try:
            dados = self._resolver_objeto(self.raiz, raiz_tipo, selecoes, [])
        except _NuloProibido:
            # Um campo da RAIZ era '!' e falhou. Não há a quem subir: a
            # resposta inteira é void, e o erro já está na lista.
            # Deixar o sinal escapar daqui faria o programa de quem
            # chamou receber '_NuloProibido' — o nome de uma classe
            # interna, no lugar de uma resposta.
            dados = None
        dados = self._forcar_ate_o_fim(dados)
        return {
            "dados": dados,
            "erros": [e.como_vault() for e in self.erros],
            "extensoes": {
                "ms": self.contexto.ms,
                "campos": self.contexto.campos_resolvidos,
                "lotes": self.contexto.lotes.resumo(),
                **metricas,
                **self.contexto.extensoes,
            },
        }

    def _forcar_ate_o_fim(self, arvore):
        """Resolve a fila e força os adiados, nível a nível.

        Cada rodada pode criar a fila do nível seguinte — `pedido.cliente`
        adia, e forçar isso pede `cliente.empresa`. O laço termina
        quando uma rodada não força nada; o teto existe porque um
        resolvedor que adia a si mesmo giraria para sempre, e travar
        calado é pior que dizer o que houve.
        """
        for _ in range(self.esquema.limites.get("profundidade", 12) + 4):
            self.contexto.lotes.resolver_tudo()
            arvore, forcados = self._forcar(arvore)
            if not forcados:
                return _cobrar_promessas(arvore)
        raise ErroDeExecucao(
            "a resolução não terminou: algum campo adia sem parar", [],
            "lote", {"dica": "um resolvedor que pede ao lote o próprio "
                             "valor que ele produz nunca fecha"})

    def _forcar(self, no, caminho=None):
        caminho = caminho or []
        if isinstance(no, Adiado):
            try:
                valor = no.forcar()
            except _NuloProibido:
                if no.obrigatorio:
                    raise
                return None, 1
            except ErroDeExecucao as erro:
                erro.caminho = erro.caminho or no.caminho
                self.erros.append(erro)
                if no.obrigatorio:
                    raise _NuloProibido() from None
                return None, 1
            filho, _ = self._forcar(valor, no.caminho)
            return filho, 1
        if isinstance(no, dict):
            saida, total = {}, 0
            for chave, valor in no.items():
                try:
                    saida[chave], quantos = self._forcar(valor,
                                                         caminho + [chave])
                except _NuloProibido:
                    return None, 1
                total += quantos
            return saida, total
        if isinstance(no, list):
            saida, total = [], 0
            for i, valor in enumerate(no):
                try:
                    filho, quantos = self._forcar(valor, caminho + [str(i)])
                except _NuloProibido:
                    return None, 1
                saida.append(filho)
                total += quantos
            return saida, total
        return no, 0

    def _resolver_objeto(self, pai, tipo, selecoes, caminho):
        saida = {}
        for selecao in selecoes:
            campo = tipo.campos.get(selecao.nome)
            if campo is None:
                self.erros.append(ErroDeExecucao(
                    f"'{tipo.nome}' não tem o campo '{selecao.nome}'",
                    caminho + [selecao.apelido], "consulta",
                    {"tem": _parecidos(selecao.nome, tipo.campos)}))
                saida[selecao.apelido] = None
                continue
            try:
                saida[selecao.apelido] = self._resolver_campo(
                    pai, tipo, campo, selecao, caminho + [selecao.apelido])
            except _NuloProibido:
                # Um `!` falhou aqui dentro: este objeto inteiro é void.
                raise
            except ErroDeExecucao as erro:
                self.erros.append(erro)
                if ler_tipo(campo.tipo).obrigatorio:
                    raise _NuloProibido() from None
                saida[selecao.apelido] = None
        return saida

    def _resolver_campo(self, pai, tipo, campo, selecao, caminho):
        argumentos = self._argumentos(tipo, campo, selecao, caminho)
        self.contexto.campos_resolvidos += 1

        try:
            if campo.resolver is not None:
                bruto = _chamar(campo.resolver, pai, argumentos, self.contexto)
            else:
                bruto = valor_do_campo(pai, campo.nome)
        except Recusado as erro:
            erro.caminho = erro.caminho or caminho
            raise
        except ErroDeExecucao as erro:
            erro.caminho = erro.caminho or caminho
            raise
        except Exception as erro:                    # noqa: BLE001
            # Um erro de verdade do resolvedor. A mensagem é limpa do
            # que o interpretador acrescenta ao embrulhar — quem lê a
            # resposta não tem como saber o que é 'RuntimeError_' nem a
            # que arquivo se refere aquela linha.
            raise ErroDeExecucao(_limpar(erro), caminho,
                                 "resolvedor") from None

        return self._coagir_saida(bruto, ler_tipo(campo.tipo), selecao, caminho)

    def _argumentos(self, tipo, campo, selecao, caminho):
        argumentos = {}
        for nome, valor in selecao.argumentos.items():
            if nome not in campo.argumentos:
                raise ErroDeExecucao(
                    f"{tipo.nome}.{campo.nome} não aceita o argumento "
                    f"'{nome}'", caminho, "argumento",
                    {"aceita": list(campo.argumentos)})
            declarado = _tipo_do_argumento(campo.argumentos[nome])
            argumentos[nome] = coagir_entrada(
                self.esquema, self._resolver_valor(valor), declarado, caminho,
                f"o argumento '{nome}' de {tipo.nome}.{campo.nome}")
        for nome, decl in campo.argumentos.items():
            if nome in argumentos:
                continue
            padrao = padrao_do_argumento(decl)
            if padrao is not SEM_PADRAO:
                argumentos[nome] = padrao
            elif ler_tipo(_tipo_do_argumento(decl)).obrigatorio:
                raise ErroDeExecucao(
                    f"{tipo.nome}.{campo.nome} exige o argumento '{nome}'",
                    caminho, "argumento")
        return argumentos

    def _coagir_saida(self, valor, ref, selecao, caminho):
        if isinstance(valor, Promessa):
            # NÃO cobrar aqui. Cobrar é o que desfaz o lote: o primeiro
            # item da lista resolveria a fila com uma chave só, o
            # segundo com outra, e vinte pedidos dariam vinte idas ao
            # banco — exatamente o N+1 que o lote existe para evitar.
            #
            # Em vez disso, o valor fica ADIADO. Quando a volta inteira
            # termina, a fila é resolvida de uma vez e só então os
            # adiados são forçados — e forçar pode criar a fila do
            # nível seguinte, que é resolvida do mesmo jeito.
            return Adiado(valor,
                          lambda v: self._coagir_saida(v, ref, selecao,
                                                       caminho),
                          ref.obrigatorio, caminho)

        if valor is None:
            if ref.obrigatorio:
                raise ErroDeExecucao(
                    f"o campo é '{ref}' e o resolvedor devolveu void",
                    caminho, "nulo",
                    {"dica": "ou o resolvedor devolve um valor, ou o campo "
                             "deixa de ser '!' no esquema"})
            return None

        if ref.lista:
            if isinstance(valor, (str, bytes)) or not hasattr(valor, "__iter__"):
                raise ErroDeExecucao(
                    f"o campo é '{ref}' e o resolvedor devolveu um valor solto",
                    caminho, "nulo")
            itens = list(valor)
            teto = self.esquema.limites.get("itens", 1000)
            if len(itens) > teto:
                raise ErroDeExecucao(
                    f"o campo devolveu {len(itens)} itens, e o teto é {teto}",
                    caminho, "limite",
                    {"dica": "pagine: a lista sem teto é como uma consulta "
                             "boa derruba o servidor num dia de pico"})
            saida = []
            for i, item in enumerate(itens):
                try:
                    saida.append(self._coagir_saida(item, ref.de, selecao,
                                                    caminho + [str(i)]))
                except _NuloProibido:
                    if ref.de.obrigatorio:
                        raise
                    saida.append(None)
                except ErroDeExecucao as erro:
                    self.erros.append(erro)
                    if ref.de.obrigatorio:
                        raise _NuloProibido() from None
                    saida.append(None)
            return saida

        tipo = self.esquema.obter(ref.nome)
        if tipo is None:
            raise ErroDeExecucao(f"o tipo '{ref.nome}' sumiu do esquema",
                                 caminho, "esquema")

        if tipo.especie == "escalar":
            try:
                return _serializar_escalar(tipo, valor)
            except Exception as erro:                # noqa: BLE001
                raise ErroDeExecucao(
                    f"não consegui serializar '{valor}' como {tipo.nome}: "
                    f"{erro}", caminho, "serializacao") from None

        if tipo.especie == "enum":
            for nome, bruto in tipo.valores.items():
                if bruto == valor or nome == valor:
                    return nome
            raise ErroDeExecucao(
                f"'{valor}' não é um valor de {tipo.nome}", caminho, "enum",
                {"aceita": list(tipo.valores)})

        if tipo.especie in ("contrato", "uniao"):
            concreto = self._concretizar(tipo, valor, caminho)
            selecoes = self._expandir(selecao.selecoes, concreto.nome)
            try:
                return self._resolver_objeto(valor, concreto, selecoes, caminho)
            except _NuloProibido:
                if ref.obrigatorio:
                    raise
                return None

        if not selecao.selecoes:
            raise ErroDeExecucao(
                f"'{tipo.nome}' é um objeto e a consulta não disse quais "
                f"campos quer", caminho, "consulta",
                {"dica": f"termine o campo com ':' e indente o que precisa. "
                         f"Ele tem: {', '.join(list(tipo.campos)[:8])}"})

        selecoes = self._expandir(selecao.selecoes, tipo.nome)
        try:
            return self._resolver_objeto(valor, tipo, selecoes, caminho)
        except _NuloProibido:
            if ref.obrigatorio:
                raise
            return None

    def _concretizar(self, tipo, valor, caminho):
        nome = None
        if tipo.resolver_tipo is not None:
            nome = _chamar(tipo.resolver_tipo, valor, self.contexto)
        if nome is None:
            nome = valor_do_campo(valor, "__tipo") or _nome_do_valor(valor)
        concreto = self.esquema.obter(nome) if nome else None
        if concreto is None or concreto.especie != "objeto":
            candidatos = (tipo.membros if tipo.especie == "uniao"
                          else [t.nome for t in self.esquema.tipos.values()
                                if tipo.nome in t.contratos])
            raise ErroDeExecucao(
                f"não descobri qual tipo concreto é este valor de "
                f"'{tipo.nome}'", caminho, "tipo",
                {"dica": "declare 'resolve_tipo' no contrato/união, ou "
                         "devolva um record cujo nome seja um dos membros",
                 "candidatos": candidatos})
        if tipo.especie == "uniao" and concreto.nome not in tipo.membros:
            raise ErroDeExecucao(
                f"'{concreto.nome}' não é membro da união '{tipo.nome}'",
                caminho, "tipo", {"membros": tipo.membros})
        return concreto


#: O que o interpretador acrescenta ao embrulhar um erro. Quem lê a
#: resposta de uma consulta nunca viu 'RuntimeError_' nem sabe a que
#: arquivo se refere aquela linha.
_RUIDO = re.compile(r"^\w*Error_?\s*(\[line \d+, col \d+\])?:\s*")


def _limpar(erro):
    """A mensagem do resolvedor, sem os bastidores do interpretador."""
    texto = str(erro) or type(erro).__name__
    texto = _RUIDO.sub("", texto).strip()
    return texto or "o resolvedor falhou"


class Adiado:
    """Um valor que ainda não pode ser calculado: falta o lote resolver."""

    __slots__ = ("promessa", "continuar", "obrigatorio", "caminho")

    def __init__(self, promessa, continuar, obrigatorio, caminho):
        self.promessa = promessa
        self.continuar = continuar
        self.obrigatorio = obrigatorio
        self.caminho = list(caminho)

    def forcar(self):
        return self.continuar(self.promessa.cobrar())

    def __repr__(self):
        return f"<adiado {'.'.join(self.caminho)}>"


class _NuloProibido(Exception):
    """Um `!` falhou: o objeto que o contém não pode existir pela metade."""


def _nome_do_valor(valor):
    for atributo in ("record", "blueprint"):
        dono = getattr(valor, atributo, None)
        if dono is not None and getattr(dono, "name", None):
            return dono.name
    if isinstance(valor, dict):
        return valor.get("__tipo") or valor.get("tipo")
    return type(valor).__name__


def _juntar_iguais(selecoes):
    """Dois pedidos do mesmo campo viram um, com as seleções somadas.

    `...Basico` mais `nome` escrito à mão pedem `nome` duas vezes. Sem
    juntar, a resposta traria a chave repetida — e num vault a segunda
    apaga a primeira, o que faz a ordem da consulta mudar o resultado.
    """
    saida, indice = [], {}
    for selecao in selecoes:
        chave = (selecao.apelido, selecao.nome)
        if chave in indice:
            anterior = saida[indice[chave]]
            if selecao.selecoes:
                anterior.selecoes = _juntar_iguais(
                    list(anterior.selecoes) + list(selecao.selecoes))
            continue
        indice[chave] = len(saida)
        saida.append(Selecao(selecao.nome, selecao.apelido, selecao.argumentos,
                             list(selecao.selecoes), selecao.diretivas,
                             selecao.linha, selecao.coluna,
                             selecao.tipo_condicional, selecao.trecho))
    return saida


def _profundidade(selecoes, documento, vistos=None, nivel=1):
    vistos = vistos or set()
    maxima = nivel
    for selecao in selecoes:
        filhas = selecao.selecoes
        if selecao.trecho:
            if selecao.trecho in vistos:
                continue
            trecho = documento.trechos.get(selecao.trecho)
            if trecho is None:
                continue
            maxima = max(maxima, _profundidade(trecho.selecoes, documento,
                                               vistos | {selecao.trecho}, nivel))
            continue
        if filhas:
            maxima = max(maxima, _profundidade(filhas, documento, vistos,
                                               nivel + 1))
    return maxima


def _cobrar_promessas(valor):
    if isinstance(valor, Promessa):
        return _cobrar_promessas(valor.cobrar())
    if isinstance(valor, dict):
        return {k: _cobrar_promessas(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [_cobrar_promessas(v) for v in valor]
    return valor


def _parecidos(nome, campos):
    import difflib
    perto = difflib.get_close_matches(nome, list(campos), n=3, cutoff=0.6)
    return perto or list(campos)[:6]
