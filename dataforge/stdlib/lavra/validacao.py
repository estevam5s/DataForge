# -*- coding: utf-8 -*-
"""Conferir a consulta contra o esquema ANTES de resolver qualquer coisa.

Por que separado da execução
----------------------------
Executar e descobrir no meio que o campo não existe já custou tudo o
que veio antes — inclusive escritas, numa `mudanca`. A validação
percorre a mesma árvore sem chamar resolvedor nenhum, e devolve TODOS
os problemas de uma vez.

Devolver todos de uma vez é o ponto. Um validador que para no primeiro
erro faz quem escreve a consulta corrigir uma linha por tentativa; com
dez erros numa resposta, ele corrige as dez.
"""

from .esquema import ler_tipo, padrao_do_argumento, SEM_PADRAO, _tipo_do_argumento


class Problema:
    """O que a validacao achou — e se isso impede a consulta de rodar.

    `aviso` existe por causa de **obsoleto**. Um campo marcado como
    obsoleto era RECUSADO, e uma depreciacao que quebra no dia do
    aviso nao e aviso: e uma quebra com aviso previo de zero. O efeito
    pratico era `obsoleto` nao ter uso nenhum — ninguem marca um campo
    se marcar derruba o cliente, e o campo fica sem marca ate o dia em
    que some sem ninguem ter sido avisado.
    """

    __slots__ = ("mensagem", "linha", "caminho", "dica", "aviso")

    def __init__(self, mensagem, linha=0, caminho=None, dica="", aviso=False):
        self.mensagem = mensagem
        self.linha = linha
        self.caminho = list(caminho or [])
        self.dica = dica
        self.aviso = bool(aviso)

    def como_vault(self):
        return {"mensagem": self.mensagem, "linha": self.linha,
                "caminho": self.caminho, "dica": self.dica,
                "aviso": self.aviso}

    def __repr__(self):
        return f"<problema linha {self.linha}: {self.mensagem}>"


def validar(esquema, documento, operacao=None):
    """Todos os problemas da consulta, em ordem de linha."""
    problemas = []
    try:
        alvo = documento.operacao(operacao)
    except Exception as erro:                        # noqa: BLE001
        return [Problema(str(erro))]

    raiz = {"busca": esquema.busca, "mudanca": esquema.mudanca,
            "assinatura": esquema.assinatura}[alvo.especie]
    if not raiz.campos:
        problemas.append(Problema(
            f"o esquema não tem nenhuma {alvo.especie}", alvo.linha,
            dica=f"declare uma com Lavra.{alvo.especie}(esq, …)"))
        return problemas

    usadas = set()
    _validar_selecoes(esquema, documento, alvo.selecoes, raiz, [], problemas,
                      alvo, usadas, set())

    for nome, decl in alvo.variaveis.items():
        if nome not in usadas:
            problemas.append(Problema(
                f"a variável ${nome} é declarada e nunca usada", alvo.linha,
                dica="tire-a da declaração, ou use-a em algum argumento"))
        base = ler_tipo(decl["tipo"]).nome_base
        if esquema.obter(base) is None:
            problemas.append(Problema(
                f"a variável ${nome} é do tipo '{base}', que não existe",
                alvo.linha))

    for nome, trecho in documento.trechos.items():
        if esquema.obter(trecho.tipo) is None:
            problemas.append(Problema(
                f"o trecho '{nome}' é 'em {trecho.tipo}', e esse tipo não "
                f"existe no esquema", trecho.linha))

    problemas.sort(key=lambda p: (p.linha, p.mensagem))
    return problemas


def _validar_selecoes(esquema, documento, selecoes, tipo, caminho, problemas,
                      operacao, usadas, trechos_vistos):
    for selecao in selecoes:
        if selecao.trecho:
            trecho = documento.trechos.get(selecao.trecho)
            if trecho is None:
                problemas.append(Problema(
                    f"não há trecho chamado '{selecao.trecho}'", selecao.linha,
                    caminho, dica=f"há: {', '.join(sorted(documento.trechos)) or 'nenhum'}"))
                continue
            if selecao.trecho in trechos_vistos:
                problemas.append(Problema(
                    f"o trecho '{selecao.trecho}' usa a si mesmo",
                    selecao.linha, caminho,
                    dica="um ciclo de trechos trava antes de responder"))
                continue
            alvo = esquema.obter(trecho.tipo)
            if alvo is not None and not _pode_casar(esquema, trecho.tipo, tipo):
                problemas.append(Problema(
                    f"o trecho '{selecao.trecho}' é de '{trecho.tipo}' e está "
                    f"sendo usado em '{tipo.nome}'", selecao.linha, caminho,
                    dica="um trecho só se aplica ao tipo dele, ou a um tipo "
                         "que o cumpre"))
                continue
            _validar_selecoes(esquema, documento, trecho.selecoes,
                              alvo or tipo, caminho, problemas, operacao,
                              usadas, trechos_vistos | {selecao.trecho})
            continue

        if selecao.tipo_condicional:
            alvo = esquema.obter(selecao.tipo_condicional)
            if alvo is None:
                problemas.append(Problema(
                    f"'... em {selecao.tipo_condicional}' cita um tipo que "
                    f"não existe", selecao.linha, caminho))
                continue
            if not _pode_casar(esquema, selecao.tipo_condicional, tipo):
                problemas.append(Problema(
                    f"'{selecao.tipo_condicional}' não tem relação com "
                    f"'{tipo.nome}'", selecao.linha, caminho,
                    dica="o trecho condicional serve para união e contrato"))
                continue
            _validar_selecoes(esquema, documento, selecao.selecoes, alvo,
                              caminho, problemas, operacao, usadas,
                              trechos_vistos)
            continue

        for diretiva in selecao.diretivas:
            if diretiva["nome"] not in ("incluir", "include", "pular", "skip",
                                        *esquema.diretivas):
                problemas.append(Problema(
                    f"não existe a diretiva @{diretiva['nome']}",
                    selecao.linha, caminho,
                    dica="existem: incluir, pular" +
                         ("".join(", " + d for d in sorted(esquema.diretivas)))))
            for valor in diretiva["argumentos"].values():
                _marcar_variaveis(valor, usadas)

        campo = tipo.campos.get(selecao.nome)
        if campo is None:
            import difflib
            perto = difflib.get_close_matches(selecao.nome, list(tipo.campos),
                                              n=1, cutoff=0.6)
            problemas.append(Problema(
                f"'{tipo.nome}' não tem o campo '{selecao.nome}'",
                selecao.linha, caminho + [selecao.apelido],
                dica=(f"você quis dizer '{perto[0]}'?" if perto else
                      f"ele tem: {', '.join(list(tipo.campos)[:8])}")))
            continue

        if campo.obsoleto:
            # AVISO, e nao erro: o campo continua respondendo. Quem
            # marca um campo como obsoleto esta dando prazo, e tirar o
            # prazo transforma a marca numa remocao.
            problemas.append(Problema(
                f"{tipo.nome}.{campo.nome} está obsoleto: {campo.obsoleto}",
                selecao.linha, caminho + [selecao.apelido],
                dica="ele continua respondendo — troque antes que ele saia",
                aviso=True))

        _validar_argumentos(esquema, tipo, campo, selecao, caminho, problemas,
                            operacao, usadas)

        ref = ler_tipo(campo.tipo)
        alvo = esquema.obter(ref.nome_base)
        folha = alvo is None or alvo.especie in ("escalar", "enum")
        if folha and selecao.selecoes:
            problemas.append(Problema(
                f"'{campo.nome}' é {ref} e não tem campos dentro",
                selecao.linha, caminho + [selecao.apelido],
                dica="tire o ':' e o bloco"))
        if not folha and not selecao.selecoes:
            problemas.append(Problema(
                f"'{campo.nome}' é {ref} e a consulta não disse quais campos "
                f"quer", selecao.linha, caminho + [selecao.apelido],
                dica=f"termine em ':' e indente. Ele tem: "
                     f"{', '.join(list(alvo.campos)[:8])}"))
        if not folha and selecao.selecoes:
            _validar_selecoes(esquema, documento, selecao.selecoes, alvo,
                              caminho + [selecao.apelido], problemas,
                              operacao, usadas, trechos_vistos)


def _validar_argumentos(esquema, tipo, campo, selecao, caminho, problemas,
                        operacao, usadas):
    for nome, valor in selecao.argumentos.items():
        _marcar_variaveis(valor, usadas)
        if nome not in campo.argumentos:
            import difflib
            perto = difflib.get_close_matches(nome, list(campo.argumentos),
                                              n=1, cutoff=0.6)
            problemas.append(Problema(
                f"{tipo.nome}.{campo.nome} não aceita o argumento '{nome}'",
                selecao.linha, caminho + [selecao.apelido],
                dica=(f"você quis dizer '{perto[0]}'?" if perto else
                      f"ele aceita: {', '.join(campo.argumentos) or 'nenhum'}")))
            continue
        _conferir_variavel(esquema, valor, campo.argumentos[nome], nome,
                           tipo, campo, selecao, caminho, problemas, operacao)

    for nome, decl in campo.argumentos.items():
        if nome in selecao.argumentos:
            continue
        if (padrao_do_argumento(decl) is SEM_PADRAO
                and ler_tipo(_tipo_do_argumento(decl)).obrigatorio):
            problemas.append(Problema(
                f"{tipo.nome}.{campo.nome} exige o argumento '{nome}'",
                selecao.linha, caminho + [selecao.apelido],
                dica=f"ele é '{_tipo_do_argumento(decl)}'"))


def _conferir_variavel(esquema, valor, decl, nome, tipo, campo, selecao,
                       caminho, problemas, operacao):
    from .consulta import Variavel
    if not isinstance(valor, Variavel):
        return
    if valor.nome not in operacao.variaveis:
        problemas.append(Problema(
            f"a operação não declara ${valor.nome}", selecao.linha,
            caminho + [selecao.apelido],
            dica=f"declare-a: {operacao.especie} "
                 f"{operacao.nome or ''}(${valor.nome}: …)"))
        return
    esperado = ler_tipo(_tipo_do_argumento(decl))
    recebido = ler_tipo(operacao.variaveis[valor.nome]["tipo"])
    if recebido.nome_base != esperado.nome_base:
        problemas.append(Problema(
            f"${valor.nome} é '{recebido}' e o argumento '{nome}' é "
            f"'{esperado}'", selecao.linha, caminho + [selecao.apelido]))
    elif esperado.obrigatorio and not recebido.obrigatorio and \
            operacao.variaveis[valor.nome]["padrao"] is None:
        problemas.append(Problema(
            f"'{nome}' exige '{esperado}' e ${valor.nome} admite void",
            selecao.linha, caminho + [selecao.apelido],
            dica=f"declare ${valor.nome} como '{esperado}', ou dê um padrão"))


def _marcar_variaveis(valor, usadas):
    from .consulta import Variavel
    if isinstance(valor, Variavel):
        usadas.add(valor.nome)
    elif isinstance(valor, list):
        for item in valor:
            _marcar_variaveis(item, usadas)
    elif isinstance(valor, dict):
        for item in valor.values():
            _marcar_variaveis(item, usadas)


def _pode_casar(esquema, pedido, tipo):
    if pedido == tipo.nome:
        return True
    if pedido in tipo.contratos:
        return True
    alvo = esquema.obter(pedido)
    if alvo is None:
        return False
    if alvo.especie == "uniao":
        return tipo.nome in alvo.membros
    if alvo.especie == "contrato":
        return alvo.nome in tipo.contratos
    if tipo.especie == "uniao":
        return pedido in tipo.membros
    if tipo.especie == "contrato":
        return tipo.nome in alvo.contratos
    return False
