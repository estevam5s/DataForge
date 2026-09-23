# -*- coding: utf-8 -*-
"""A superfície pública — o que sai de `adopt Arcane.Lavra as Lavra`."""

import time

from . import introspeccao as I
from . import validacao as V
from .consulta import ErroDeConsulta, ler as ler_consulta
from .esquema import (Campo, Esquema, ErroDeEsquema, Tipo, ler_tipo,
                      ESCALARES, SEM_PADRAO)
from .execucao import (Contexto, ErroDeExecucao, Execucao, Recusado,
                       valor_do_campo)
from .lote import ErroDeLote, Promessa


# ══════════════════════════════════════════════════════════════
#  Montar o esquema
# ══════════════════════════════════════════════════════════════

def esquema(nome="lavra"):
    return Esquema(nome)


def _campos_do_record(alvo):
    """Os campos declarados de um record, blueprint ou vault de tipos.

    É o que torna o esquema barato: o `record` já diz nome, campo e
    tipo. Repetir isso num arquivo de esquema seria uma segunda fonte
    de verdade para divergir da primeira.
    """
    # record: DFRecord tem 'field_names' e 'field_types'
    nomes = getattr(alvo, "field_names", None)
    if nomes:
        tipos = getattr(alvo, "field_types", None) or {}
        return {n: tipos.get(n) or "String" for n in nomes}
    # blueprint: campos declarados
    decl = getattr(alvo, "fields_decl", None)
    if decl:
        saida = {}
        for item in decl:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                saida[item[0]] = item[1] or "String"
            elif isinstance(item, str):
                saida[item] = "String"
        return saida
    if isinstance(alvo, dict):
        return dict(alvo)
    return {}


def _nome_do_alvo(alvo, nome):
    if nome:
        return nome
    for atributo in ("name", "nome", "__name__"):
        achado = getattr(alvo, atributo, None)
        if isinstance(achado, str) and achado:
            return achado
    raise ErroDeEsquema(
        "não descobri o nome deste tipo — passe 'nome := \"Usuario\"'")


def _traduzir(tipo_declarado):
    """O tipo da linguagem vira o tipo do esquema.

    `Cluster` e `Vault` não têm forma no esquema — um campo que é
    "uma lista de qualquer coisa" não pode ser consultado por partes.
    Eles viram `[String]` e `Vault` (escalar), e quem quiser a forma
    de verdade declara o campo com `Lavra.campo`.
    """
    if not tipo_declarado:
        return "String"
    texto = str(tipo_declarado)
    if texto in ESCALARES:
        return texto
    return {"Cluster": "[String]", "Vault": "Vault", "Any": "String",
            "Number": "Float", "Void": "String"}.get(texto, texto)


def tipo(esq, alvo, nome=None, descricao="", cumpre=None, campos=None,
         esconder=None):
    """Declara um tipo de SAÍDA a partir de um record, blueprint ou vault."""
    nome = _nome_do_alvo(alvo, nome)
    t = Tipo(nome, "objeto", descricao)
    t.origem = alvo
    t.contratos = list(cumpre or [])
    esconder = set(esconder or [])
    for campo_nome, campo_tipo in (campos or _campos_do_record(alvo)).items():
        if campo_nome in esconder:
            continue
        t.campos[campo_nome] = Campo(campo_nome, _traduzir(campo_tipo))
    return esq.registrar(t)


def entrada(esq, alvo, nome=None, descricao="", campos=None):
    """Declara um tipo de ENTRADA — o que uma mudança recebe.

    Entrada e saída são tipos DIFERENTES de propósito. O `Usuario` que
    sai tem `id` e `criado_em`; o que entra não tem nem um nem outro, e
    usar o mesmo tipo nos dois lados obrigaria a marcar metade dos
    campos como opcionais — e aí nenhum deles seria conferido.
    """
    nome = _nome_do_alvo(alvo, nome)
    t = Tipo(nome, "entrada", descricao)
    t.origem = alvo
    for campo_nome, campo_tipo in (campos or _campos_do_record(alvo)).items():
        t.campos[campo_nome] = Campo(campo_nome, _traduzir(campo_tipo))
    return esq.registrar(t)


def escalar(esq, nome, serializa=None, desserializa=None, descricao=""):
    """Um escalar próprio: Data, Dinheiro, Email — o que a linguagem não tem."""
    t = Tipo(nome, "escalar", descricao)
    t.serializar = serializa
    t.desserializar = desserializa
    return esq.registrar(t)


def contrato(esq, nome, campos, descricao="", resolve_tipo=None):
    """Um contrato: campos que vários tipos prometem ter.

    Quem consulta pede os campos do contrato e recebe de qualquer um
    dos que o cumprem — e usa `... em Tipo:` para pedir o que só existe
    num deles.
    """
    t = Tipo(nome, "contrato", descricao)
    t.resolver_tipo = resolve_tipo
    for campo_nome, campo_tipo in campos.items():
        t.campos[campo_nome] = Campo(campo_nome, _traduzir(campo_tipo))
    return esq.registrar(t)


def uniao(esq, nome, membros, descricao="", resolve_tipo=None):
    """Uma união: o campo devolve UM de vários tipos sem nada em comum."""
    t = Tipo(nome, "uniao", descricao)
    t.membros = list(membros)
    t.resolver_tipo = resolve_tipo
    return esq.registrar(t)


def enum(esq, nome, valores, descricao=""):
    """Um enum. Aceita o `enum` da linguagem, um cluster ou um vault."""
    t = Tipo(nome, "enum", descricao)
    membros = getattr(valores, "members", None)
    if isinstance(membros, dict):
        for chave, membro in membros.items():
            t.valores[chave] = getattr(membro, "value", chave)
    elif isinstance(valores, dict):
        t.valores = dict(valores)
    else:
        t.valores = {str(v): v for v in valores}
    return esq.registrar(t)


def campo(esq, tipo_nome, nome, tipo_do_campo, resolve=None, args=None,
          descricao="", obsoleto="", custo=1):
    """Acrescenta (ou substitui) um campo de um tipo já declarado."""
    alvo = esq.obter(tipo_nome)
    if alvo is None:
        raise ErroDeEsquema(
            f"não há tipo '{tipo_nome}' neste esquema.\n"
            f"  Declare-o antes: Lavra.tipo(esq, {tipo_nome})\n"
            f"  Há: {', '.join(sorted(esq.tipos)) or 'nenhum'}")
    alvo.campos[nome] = Campo(nome, tipo_do_campo, args or {}, resolve,
                              descricao, obsoleto, custo)
    return alvo.campos[nome]


def _raiz(esq, qual, nome, tipo_do_campo, resolve, args, descricao, custo):
    alvo = {"busca": esq.busca, "mudanca": esq.mudanca,
            "assinatura": esq.assinatura}[qual]
    alvo.campos[nome] = Campo(nome, tipo_do_campo, args or {}, resolve,
                              descricao, "", custo)
    return alvo.campos[nome]


def busca(esq, nome, tipo_do_campo, resolve=None, args=None, descricao="",
          custo=1):
    """Uma leitura. O ponto de entrada de tudo o que se pode ler."""
    return _raiz(esq, "busca", nome, tipo_do_campo, resolve, args, descricao,
                 custo)


def mudanca(esq, nome, tipo_do_campo, resolve=None, args=None, descricao="",
            custo=1):
    """Uma escrita. Separada da busca porque o efeito colateral tem de
    aparecer no nome da operação: quem lê a consulta sabe, sem abrir o
    resolvedor, se aquilo muda alguma coisa."""
    return _raiz(esq, "mudanca", nome, tipo_do_campo, resolve, args, descricao,
                 custo)


def assinatura(esq, nome, tipo_do_campo, resolve=None, args=None,
               descricao="", custo=1):
    """Um acompanhamento: o servidor empurra cada novo valor."""
    return _raiz(esq, "assinatura", nome, tipo_do_campo, resolve, args,
                 descricao, custo)


def diretiva(esq, nome, decidir):
    """Uma diretiva própria: `@nome(args)` decide se o campo entra.

    `decidir(args, ctx)` devolvendo `no` tira o campo da resposta. É o
    gancho para `@admin`, `@experimento(nome: …)` e afins — sem
    espalhar `given` por dentro de cada resolvedor.
    """
    esq.diretivas[nome] = decidir
    return nome


def limites(esq, profundidade=None, complexidade=None, itens=None):
    """Os três tetos. Nenhum deles é opcional num servidor público."""
    if profundidade is not None:
        esq.limites["profundidade"] = profundidade
    if complexidade is not None:
        esq.limites["complexidade"] = complexidade
    if itens is not None:
        esq.limites["itens"] = itens
    return dict(esq.limites)


def conferir(esq):
    """Fecha o esquema: todo tipo citado existe, todo contrato é cumprido."""
    return esq.conferir()


def introspeccao(esq, ligada=True):
    if ligada:
        I.instalar(esq)
    else:
        I.remover(esq)
    return esq


# ══════════════════════════════════════════════════════════════
#  Consultar
# ══════════════════════════════════════════════════════════════

def ler(texto):
    """O texto da consulta vira documento. Erro aqui traz linha e coluna."""
    return ler_consulta(texto)


def validar(esq, texto, operacao=None):
    """Todos os problemas da consulta, sem resolver nada."""
    try:
        documento = ler_consulta(texto) if isinstance(texto, str) else texto
    except ErroDeConsulta as erro:
        return [{"mensagem": erro.mensagem, "linha": erro.linha,
                 "caminho": [], "dica": erro.dica}]
    return [p.como_vault() for p in V.validar(esq, documento, operacao)]


def executar(esq, texto, variaveis=None, contexto=None, raiz=None,
             operacao=None, validar_antes=True):
    """Roda a consulta e devolve `{dados, erros, extensoes}`.

    Nunca levanta por causa da consulta: um erro de sintaxe, de
    validação ou de resolvedor vira item em `erros`, com o caminho até
    o campo. Quem chama decide o que fazer — e no HTTP isso é o que
    permite responder 200 com dados parciais, que é o contrato que
    clientes de consulta esperam.
    """
    inicio = time.perf_counter()
    try:
        documento = ler_consulta(texto) if isinstance(texto, str) else texto
    except ErroDeConsulta as erro:
        return {"dados": None,
                "erros": [{"mensagem": erro.mensagem, "caminho": [],
                           "codigo": "sintaxe",
                           "extra": {"linha": erro.linha,
                                     "coluna": erro.coluna,
                                     "dica": erro.dica}}],
                "extensoes": {"ms": _ms(inicio)}}

    avisos = []
    if validar_antes:
        problemas = V.validar(esq, documento, operacao)
        # Um AVISO nao impede a consulta: ele viaja em 'extensoes.avisos',
        # que e onde um cliente procura o que vai quebrar depois.
        avisos = [p for p in problemas if p.aviso]
        graves = [p for p in problemas if not p.aviso]
        if graves:
            return {"dados": None,
                    "erros": [{"mensagem": p.mensagem, "caminho": p.caminho,
                               "codigo": "validacao",
                               "extra": {"linha": p.linha, "dica": p.dica}}
                              for p in graves],
                    "extensoes": {"ms": _ms(inicio),
                                  "avisos": [p.como_vault() for p in avisos]}}

    try:
        execucao = Execucao(esq, documento, variaveis, contexto, raiz, operacao)
        resposta = execucao.rodar()
        if avisos:
            resposta.setdefault("extensoes", {})["avisos"] = [
                p.como_vault() for p in avisos]
        return resposta
    except ErroDeExecucao as erro:
        return {"dados": None, "erros": [erro.como_vault()],
                "extensoes": {"ms": _ms(inicio)}}


def _ms(inicio):
    return round((time.perf_counter() - inicio) * 1000, 3)


# ══════════════════════════════════════════════════════════════
#  Contexto e lote
# ══════════════════════════════════════════════════════════════

def contexto(dados=None):
    return Contexto(dados)


def lote(ctx, nome, buscar):
    """Declara um lote nesta consulta. Ver `Lavra.pedir`."""
    return _registro(ctx).lote(nome, buscar)


def pedir(ctx, nome, chave):
    """Pede uma chave ao lote. Só vira consulta quando a volta termina."""
    return _registro(ctx).pedir(nome, chave)


def entao(promessa, acao):
    """Calcula a partir do que o lote vai trazer, sem desfazer o lote.

    Cobrar a promessa dentro do resolvedor resolveria a fila com uma
    chave só — e vinte pedidos voltariam a ser vinte idas ao banco. O
    `entao` guarda a conta para depois:

        action total(pedido, _args, ctx):
            itens := Lavra.pedir(ctx, "itens", pedido.id)
            yield Lavra.entao(itens, lambda lista => somar(lista))

    Um valor que não é promessa passa direto pela ação, para que o
    mesmo resolvedor sirva com e sem lote.
    """
    if isinstance(promessa, Promessa):
        return promessa.entao(acao)
    from .execucao import _chamar
    return _chamar(acao, promessa)


def preencher(ctx, nome, chave, valor):
    """Põe no lote um valor que já se tem, para ele não ser buscado."""
    return _registro(ctx).lote(nome, lambda _: []).preencher(chave, valor)


def lotes(ctx):
    return _registro(ctx).resumo()


def _registro(ctx):
    if isinstance(ctx, Contexto):
        return ctx.lotes
    raise ErroDeLote(
        "o lote vive no CONTEXTO da consulta, e este não é um contexto.\n"
        "  Passe o 'ctx' que o resolvedor recebe como terceiro argumento.")


def recusar(mensagem="sem permissão", extra=None):
    """Levanta a recusa de autorização, com o caminho preenchido depois."""
    raise Recusado(mensagem, None, extra)


def erro(mensagem, codigo="erro", extra=None):
    """Levanta um erro de campo: ele vira item em `erros`, com o caminho."""
    raise ErroDeExecucao(mensagem, None, codigo, extra)


# ══════════════════════════════════════════════════════════════
#  Paginação
# ══════════════════════════════════════════════════════════════

def pagina(itens, primeiros=None, depois=None, total=None):
    """A página no formato de cursor, que é o único que não pula item.

    Paginar por `offset` parece mais simples e quebra do jeito mais
    difícil de ver: se alguém insere uma linha entre a página 1 e a 2,
    um item **desaparece** da listagem — ele desceu para a posição que
    já foi lida. Com cursor, a página seguinte começa exatamente onde a
    anterior parou.
    """
    itens = list(itens)
    total = len(itens) if total is None else total
    inicio = 0
    if depois is not None:
        for i, item in enumerate(itens):
            if str(_cursor_de(item, i)) == str(depois):
                inicio = i + 1
                break
        else:
            raise ErroDeExecucao(
                f"o cursor '{depois}' não está nesta listagem", [], "cursor",
                {"dica": "um cursor só vale para a mesma ordenação e filtro"})
    fim = len(itens) if primeiros is None else inicio + max(0, primeiros)
    recorte = itens[inicio:fim]
    return {
        "itens": recorte,
        "bordas": [{"cursor": str(_cursor_de(item, inicio + i)), "item": item}
                   for i, item in enumerate(recorte)],
        "info": {
            "tem_proxima": fim < len(itens),
            "tem_anterior": inicio > 0,
            "cursor_inicio": (str(_cursor_de(recorte[0], inicio))
                              if recorte else None),
            "cursor_fim": (str(_cursor_de(recorte[-1], fim - 1))
                           if recorte else None),
        },
        "total": total,
    }


def _cursor_de(item, posicao):
    achado = valor_do_campo(item, "id")
    return achado if achado is not None else posicao


def tipo_pagina(esq, nome_do_item, nome=None):
    """Declara `PaginaDeX` — `itens`, `bordas`, `info` e `total`."""
    nome = nome or f"Pagina{nome_do_item}"
    if esq.obter("InfoDePagina") is None:
        info = Tipo("InfoDePagina", "objeto", "Onde a página começa e termina.")
        for campo_nome, campo_tipo in (("tem_proxima", "Boolean!"),
                                       ("tem_anterior", "Boolean!"),
                                       ("cursor_inicio", "String"),
                                       ("cursor_fim", "String")):
            info.campos[campo_nome] = Campo(campo_nome, campo_tipo)
        esq.registrar(info)
    if esq.obter(f"Borda{nome_do_item}") is None:
        borda = Tipo(f"Borda{nome_do_item}", "objeto",
                     f"Um {nome_do_item} e o cursor dele.")
        borda.campos["cursor"] = Campo("cursor", "String!")
        borda.campos["item"] = Campo("item", f"{nome_do_item}!")
        esq.registrar(borda)
    t = Tipo(nome, "objeto", f"Uma página de {nome_do_item}.")
    t.campos["itens"] = Campo("itens", f"[{nome_do_item}!]!")
    t.campos["bordas"] = Campo("bordas", f"[Borda{nome_do_item}!]!")
    t.campos["info"] = Campo("info", "InfoDePagina!")
    t.campos["total"] = Campo("total", "Integer!")
    return esq.registrar(t)


# ══════════════════════════════════════════════════════════════
#  Descrever
# ══════════════════════════════════════════════════════════════

def descrever(esq):
    return I.descrever(esq)


def texto_do_esquema(esq):
    return I.texto(esq)
