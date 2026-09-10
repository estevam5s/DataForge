# -*- coding: utf-8 -*-
"""
Arcane.Observar — métricas, tracing e linhagem de dados.

    adopt Arcane.Observar as O

    painel := O.painel("etl-vendas")

    O.contar(painel, "linhas_lidas", 40000)
    O.medir(painel, "duracao_extracao", 8.2)

    monitor:
        trecho := O.abrir(painel, "carregar")
        carregar()
    ensure:
        O.fechar(painel, trecho)

    out O.relatorio(painel)

─── As sete perguntas ──────────────────────────────────────

Observabilidade é conseguir responder, sem abrir o código:

    executou?  quanto demorou?  quantos registros?
    quantos falharam?  qual etapa?  quando?  qual versão?

Log sozinho responde a primeira e a sexta. As outras cinco exigem
NÚMERO — e é isso que separa observabilidade de logging.

─── Por que linhagem ───────────────────────────────────────

    vendas_bruto → limpeza → vendas_prata → agregação → painel_diario

Quando um número no painel está errado, a pergunta não é *onde está o
bug*: é **de onde veio esse número**. Sem linhagem registrada, a
resposta sai de ler o código de trás para a frente — e o código mudou
desde que aquele número foi calculado.

A linhagem também responde a pergunta inversa, que é a mais cara: *se
eu mexer aqui, o que quebra?*

─── Histograma, e não média ────────────────────────────────

A média esconde. Um pipeline com média de 2s e p99 de 40s tem um
problema que a média nunca mostra — e é o p99 que o usuário sente.
'medir' guarda a distribuição e devolve p50, p95 e p99.
"""

import json
import math
import os
import time

from ..errors import ValueError_

#: Quantas amostras guardar por métrica.
#:
#: O percentil exato exige a lista inteira, e uma lista sem teto vira
#: vazamento de memória num processo longo. Dez mil dá p99 com erro
#: menor que 1% e ocupa pouco — e o reservatório mantém a amostra
#: representativa mesmo depois de milhões de medidas.
AMOSTRAS = 10_000


class Painel:
    """Os números, os trechos e a linhagem de uma execução."""

    def __init__(self, nome, versao="", arquivo=None):
        self.nome = nome
        self.versao = versao
        self.arquivo = arquivo
        self.inicio = time.time()
        self.contadores = {}
        self.medidas = {}
        self.marcas = {}
        self.trechos = []
        self.abertos = {}
        self.linhagem = {}
        self.eventos = []
        self._proximo = 0


def _percentil(ordenados, p):
    if not ordenados:
        return 0.0
    k = (len(ordenados) - 1) * p
    baixo, alto = math.floor(k), math.ceil(k)
    if baixo == alto:
        return ordenados[int(k)]
    return ordenados[baixo] * (alto - k) + ordenados[alto] * (k - baixo)


class ArcaneObservar(dict):
    """Métricas, tracing e linhagem."""

    def __new__(cls):
        return {
            "painel": cls._painel,

            # métricas
            "contar": cls._contar,
            "medir": cls._medir,
            "marcar": cls._marcar,
            "valor": cls._valor,

            # tracing
            "abrir": cls._abrir,
            "fechar": cls._fechar,
            "cronometrar": cls._cronometrar,
            "trechos": cls._trechos,
            "arvore": cls._arvore,

            # linhagem
            "derivar": cls._derivar,
            "origem": cls._origem,
            "impacto": cls._impacto,
            "grafo": cls._grafo,

            # sair
            "relatorio": cls._relatorio,
            "resumo": cls._resumo,
            "prometheus": cls._prometheus,
            "salvar": cls._salvar,
            "alertar": cls._alertar,
        }

    @staticmethod
    def _painel(nome, versao="", arquivo=""):
        return Painel(nome, versao, arquivo or None)

    # ── métricas ────────────────────────────────────────────

    @staticmethod
    def _contar(painel, nome, quanto=1):
        """Um contador: só sobe. Linhas lidas, erros, tentativas."""
        painel.contadores[nome] = painel.contadores.get(nome, 0) + quanto
        return painel.contadores[nome]

    @staticmethod
    def _medir(painel, nome, valor):
        """Uma medida com distribuição — não só a média.

        A média esconde: um pipeline com média de 2s e p99 de 40s tem um
        problema que a média nunca mostra, e é o p99 que se sente.
        """
        registro = painel.medidas.setdefault(
            nome, {"quantas": 0, "soma": 0.0, "minimo": None,
                   "maximo": None, "amostras": []})
        v = float(valor)
        registro["quantas"] += 1
        registro["soma"] += v
        registro["minimo"] = v if registro["minimo"] is None \
            else min(registro["minimo"], v)
        registro["maximo"] = v if registro["maximo"] is None \
            else max(registro["maximo"], v)

        amostras = registro["amostras"]
        if len(amostras) < AMOSTRAS:
            amostras.append(v)
        else:
            # Amostragem por reservatório: cada valor tem a MESMA chance
            # de ficar, independente de quando chegou. Guardar só os
            # primeiros mil daria o percentil do começo da execução.
            import random
            i = random.randrange(registro["quantas"])
            if i < AMOSTRAS:
                amostras[i] = v
        return registro["quantas"]

    @staticmethod
    def _marcar(painel, nome, valor):
        """Um valor pontual — o último vale. Fila, memória, versão."""
        painel.marcas[nome] = valor
        return valor

    @staticmethod
    def _valor(painel, nome):
        if nome in painel.contadores:
            return painel.contadores[nome]
        if nome in painel.marcas:
            return painel.marcas[nome]
        if nome in painel.medidas:
            return ArcaneObservar._estatisticas(painel.medidas[nome])
        return None

    @staticmethod
    def _estatisticas(registro):
        ordenados = sorted(registro["amostras"])
        n = registro["quantas"] or 1
        return {
            "quantas": registro["quantas"],
            "soma": round(registro["soma"], 6),
            "media": round(registro["soma"] / n, 6),
            "minimo": registro["minimo"],
            "maximo": registro["maximo"],
            "p50": round(_percentil(ordenados, 0.50), 6),
            "p95": round(_percentil(ordenados, 0.95), 6),
            "p99": round(_percentil(ordenados, 0.99), 6),
        }

    # ── tracing ─────────────────────────────────────────────

    @staticmethod
    def _abrir(painel, nome, dentro_de=None):
        """Começa um trecho. Devolve o identificador para fechar.

        'dentro_de' aninha: um trecho dentro de outro forma a árvore que
        mostra ONDE o tempo foi — 'carregar levou 40s' não ajuda; 'dos
        40s, 38 foram no INSERT' resolve.
        """
        painel._proximo += 1
        ident = f"t{painel._proximo}"
        painel.abertos[ident] = {
            "id": ident, "nome": nome, "pai": dentro_de,
            "inicio": time.time(),
        }
        return ident

    @staticmethod
    def _fechar(painel, ident, estado="ok", detalhe=None):
        """Fecha o trecho e registra quanto durou.

        Um trecho aberto duas vezes, ou fechado sem abrir, não levanta:
        num 'ensure' isso acontece quando o corpo estourou antes de
        abrir, e derrubar ali esconderia o erro de verdade.
        """
        aberto = painel.abertos.pop(ident, None)
        if aberto is None:
            return None
        duracao = time.time() - aberto["inicio"]
        trecho = {**aberto, "duracao": round(duracao, 6), "estado": estado}
        trecho.pop("inicio", None)
        if detalhe:
            trecho["detalhe"] = detalhe
        painel.trechos.append(trecho)
        ArcaneObservar._medir(painel, f"duracao.{aberto['nome']}", duracao)
        return trecho

    @staticmethod
    def _cronometrar(painel, nome, acao):
        """Roda a ação medindo — e registra a falha se houver.

        É a forma que não deixa trecho aberto: mesmo quando a ação
        estoura, o 'finally' fecha.
        """
        ident = ArcaneObservar._abrir(painel, nome)
        try:
            valor = acao()
        except Exception as erro:                       # noqa: BLE001
            ArcaneObservar._fechar(painel, ident, "falhou",
                                   getattr(erro, "message", str(erro)))
            ArcaneObservar._contar(painel, "erros")
            raise
        ArcaneObservar._fechar(painel, ident, "ok")
        return valor

    @staticmethod
    def _trechos(painel):
        return list(painel.trechos)

    @staticmethod
    def _arvore(painel):
        """Os trechos aninhados, em texto — onde o tempo foi."""
        filhos = {}
        for t in painel.trechos:
            filhos.setdefault(t.get("pai"), []).append(t)

        total = sum(t["duracao"] for t in filhos.get(None, [])) or 1.0
        linhas = []

        def desenhar(pai, nivel):
            for t in sorted(filhos.get(pai, []), key=lambda x: -x["duracao"]):
                proporcao = t["duracao"] / total
                barra = "█" * max(1, int(proporcao * 24))
                marca = " " if t["estado"] == "ok" else "✗"
                linhas.append(
                    f"  {'  ' * nivel}{marca} {t['nome']:<24} "
                    f"{t['duracao']:>8.3f}s  {proporcao:>5.1%} {barra}")
                desenhar(t["id"], nivel + 1)

        desenhar(None, 0)
        return "\n".join(linhas)

    # ── linhagem ────────────────────────────────────────────

    @staticmethod
    def _derivar(painel, saida, entradas, como=""):
        """Registra que 'saida' veio de 'entradas'.

        É uma linha por transformação, e é o que responde 'de onde veio
        esse número' meses depois — quando o código já mudou.
        """
        entradas = [entradas] if isinstance(entradas, str) else list(entradas)
        painel.linhagem[saida] = {
            "de": entradas, "como": como,
            "quando": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        return painel.linhagem[saida]

    @staticmethod
    def _origem(painel, nome, profundidade=20):
        """Tudo de que este dado depende, direta ou indiretamente."""
        vistos, ordem, pilha = set(), [], [(nome, 0)]
        while pilha:
            atual, nivel = pilha.pop()
            if atual in vistos or nivel > profundidade:
                continue
            vistos.add(atual)
            no = painel.linhagem.get(atual)
            if no is None:
                continue
            for entrada in no["de"]:
                ordem.append({"de": entrada, "para": atual,
                              "como": no["como"], "nivel": nivel + 1})
                pilha.append((entrada, nivel + 1))
        return ordem

    @staticmethod
    def _impacto(painel, nome):
        """O que quebra se este dado mudar — a pergunta mais cara."""
        atingidos, pilha = [], [nome]
        while pilha:
            atual = pilha.pop()
            for saida, no in painel.linhagem.items():
                if atual in no["de"] and saida not in atingidos:
                    atingidos.append(saida)
                    pilha.append(saida)
        return atingidos

    @staticmethod
    def _grafo(painel):
        """A linhagem inteira, em texto."""
        if not painel.linhagem:
            return "  (nenhuma linhagem registrada)"
        linhas = []
        for saida in sorted(painel.linhagem):
            no = painel.linhagem[saida]
            como = f"  ({no['como']})" if no["como"] else ""
            linhas.append(f"  {' + '.join(no['de'])}  →  {saida}{como}")
        return "\n".join(linhas)

    # ── sair ────────────────────────────────────────────────

    @staticmethod
    def _resumo(painel):
        """As sete perguntas, respondidas."""
        falhas = sum(1 for t in painel.trechos if t["estado"] != "ok")
        return {
            "painel": painel.nome,
            "versao": painel.versao,
            "quando": time.strftime("%Y-%m-%dT%H:%M:%S",
                                    time.localtime(painel.inicio)),
            "duracao": round(time.time() - painel.inicio, 4),
            "executou": True,
            "trechos": len(painel.trechos),
            "falhas": falhas,
            "ok": falhas == 0 and not painel.abertos,
            "abertos": sorted(t["nome"] for t in painel.abertos.values()),
            "contadores": dict(painel.contadores),
            "marcas": dict(painel.marcas),
        }

    @staticmethod
    def _relatorio(painel):
        """Tudo em texto, para o log ou para o terminal."""
        r = ArcaneObservar._resumo(painel)
        marca = "✓" if r["ok"] else "✗"
        linhas = [f"{marca} {painel.nome}"
                  + (f" v{painel.versao}" if painel.versao else "")
                  + f"  —  {r['duracao']}s"]

        if r["abertos"]:
            # Trecho aberto no fim é quase sempre um 'ensure' que faltou.
            linhas.append(f"  ⚠ trechos ainda abertos: "
                          f"{', '.join(r['abertos'])}")

        if painel.contadores:
            linhas.append("")
            for nome in sorted(painel.contadores):
                linhas.append(f"  {nome:<28} {painel.contadores[nome]:>12,}")

        if painel.marcas:
            linhas.append("")
            for nome in sorted(painel.marcas):
                linhas.append(f"  {nome:<28} {painel.marcas[nome]!s:>12}")

        medidas = {k: v for k, v in painel.medidas.items()
                   if not k.startswith("duracao.")}
        if medidas:
            linhas.append("")
            linhas.append(f"  {'medida':<24}{'p50':>10}{'p95':>10}"
                          f"{'p99':>10}{'máx':>10}")
            for nome in sorted(medidas):
                e = ArcaneObservar._estatisticas(medidas[nome])
                linhas.append(f"  {nome:<24}{e['p50']:>10.3f}{e['p95']:>10.3f}"
                              f"{e['p99']:>10.3f}{e['maximo']:>10.3f}")

        if painel.trechos:
            linhas.append("")
            linhas.append(ArcaneObservar._arvore(painel))

        if painel.linhagem:
            linhas.append("")
            linhas.append("  linhagem:")
            linhas.append(ArcaneObservar._grafo(painel))

        return "\n".join(linhas)

    @staticmethod
    def _prometheus(painel):
        """As métricas no formato de exposição do Prometheus.

        É o formato que qualquer coletor entende, e sai em texto: quem
        quiser expor num endpoint do Kiln devolve isto como text/plain.
        """
        linhas = []
        prefixo = painel.nome.replace("-", "_").replace(".", "_")
        for nome, valor in sorted(painel.contadores.items()):
            metrica = f"{prefixo}_{nome}".replace("-", "_").replace(".", "_")
            linhas.append(f"# TYPE {metrica} counter")
            linhas.append(f"{metrica} {valor}")
        for nome, valor in sorted(painel.marcas.items()):
            if not isinstance(valor, (int, float)) or isinstance(valor, bool):
                continue
            metrica = f"{prefixo}_{nome}".replace("-", "_").replace(".", "_")
            linhas.append(f"# TYPE {metrica} gauge")
            linhas.append(f"{metrica} {valor}")
        for nome, registro in sorted(painel.medidas.items()):
            e = ArcaneObservar._estatisticas(registro)
            metrica = f"{prefixo}_{nome}".replace("-", "_").replace(".", "_")
            linhas.append(f"# TYPE {metrica} summary")
            for q in ("50", "95", "99"):
                linhas.append(f'{metrica}{{quantile="0.{q}"}} {e["p" + q]}')
            linhas.append(f"{metrica}_sum {e['soma']}")
            linhas.append(f"{metrica}_count {e['quantas']}")
        return "\n".join(linhas)

    @staticmethod
    def _alertar(painel, regras):
        """As regras que dispararam.

        Alerta é sobre o que EXIGE ação. Uma regra que dispara todo dia
        deixa de ser lida em uma semana — e aí a que importa passa
        despercebida junto.
        """
        disparados = []
        for nome, regra in (regras or {}).items():
            atual = ArcaneObservar._valor(painel, nome)
            if isinstance(atual, dict):
                atual = atual.get(regra.get("estatistica", "p95"))
            if not isinstance(atual, (int, float)):
                continue
            acima = regra.get("acima")
            abaixo = regra.get("abaixo")
            if acima is not None and atual > acima:
                disparados.append({"metrica": nome, "valor": atual,
                                   "limite": acima, "condicao": "acima",
                                   "texto": regra.get("texto", "")})
            elif abaixo is not None and atual < abaixo:
                disparados.append({"metrica": nome, "valor": atual,
                                   "limite": abaixo, "condicao": "abaixo",
                                   "texto": regra.get("texto", "")})
        return disparados

    @staticmethod
    def _salvar(painel, caminho=""):
        """Tudo em JSON, para comparar duas execuções depois."""
        alvo = caminho or painel.arquivo
        if not alvo:
            raise ValueError_(
                "não sei onde salvar: dê um caminho, ou crie o painel "
                "com um arquivo.", doc="tecnicas/observar")
        completo = ArcaneObservar._resumo(painel)
        completo["medidas"] = {
            k: ArcaneObservar._estatisticas(v)
            for k, v in painel.medidas.items()}
        completo["trechos"] = painel.trechos
        completo["linhagem"] = painel.linhagem

        pasta = os.path.dirname(alvo)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        temporario = alvo + ".parcial"
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(completo, f, ensure_ascii=False, indent=2, default=str)
        os.replace(temporario, alvo)
        return {"arquivo": alvo, "bytes": os.path.getsize(alvo)}
