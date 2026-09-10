# -*- coding: utf-8 -*-
"""
Arcane.Lago — Data Lake em disco: Parquet, partições e camadas.

    adopt Arcane.Lago as L

    lago := L.lago("dados/")

    L.gravar(lago, "vendas", linhas, ["ano", "mes"])
    L.ler(lago, "vendas", {"ano": 2026})

─── Por que particionar ────────────────────────────────────

    dados/vendas/ano=2026/mes=03/parte-0001.parquet

O caminho carrega o filtro. Uma consulta por 'ano=2026' não abre um
arquivo sequer de 2025 — ela nem os lista. Com dois anos de dados isso
é conveniência; com dez, é a diferença entre segundos e minutos.

O formato 'chave=valor' na pasta não é invenção: é o layout do Hive, e
é o que o Spark, o DuckDB e o pandas já sabem ler. Um lago escrito aqui
é lido por eles sem conversão.

─── As três camadas ────────────────────────────────────────

    bronze    o dado como chegou, sem tocar
    prata     limpo, tipado, sem duplicata
    ouro      agregado, pronto para consumo

Bronze existe para poder REPROCESSAR. Quando a regra de limpeza estava
errada — e vai estar — sem o bruto guardado a única saída é pedir os
dados de novo à origem, que nem sempre os tem.

─── O que este módulo NÃO é ────────────────────────────────

Não é Delta Lake nem Iceberg. Não há transação ACID entre escritores
concorrentes, nem viagem no tempo por versão, nem evolução de esquema
automática. Ele grava, particiona, compacta e lê — e o manifesto
registra o que aconteceu, para você saber o que tem.

Dois processos gravando na MESMA partição ao mesmo tempo é o caso que
ele não protege. Cada gravação cria um arquivo com nome próprio, então
eles não se sobrescrevem — mas nada garante que os dois apareçam juntos
para quem lê no meio.
"""

import json
import os
import re
import time

from ..errors import FileNotFoundError_, ValueError_
from . import parquet

#: O nome de arquivo aceito numa partição.
#:
#: Ele carrega o instante e um contador. O instante ordena; o contador
#: separa duas gravações no mesmo segundo — sem ele, a segunda
#: sobrescreveria a primeira em silêncio.
PADRAO_PARTE = re.compile(r"^parte-\d{8}-\d{6}-\d{4}\.parquet$")

#: As camadas, e o que se espera de cada uma.
CAMADAS = ("bronze", "prata", "ouro")


def _seguro(texto):
    """Um pedaço de caminho que não escapa da pasta.

    O valor da partição vem do DADO, e dado vem de fora: um campo com
    '../..' escreveria fora do lago. É o mesmo Zip Slip, por outra
    porta.
    """
    limpo = re.sub(r"[^\w\-.@ ]", "_", str(texto), flags=re.UNICODE)
    limpo = limpo.strip(". ")
    return limpo or "vazio"


class Lago:
    """A raiz, e o manifesto do que há dentro."""

    def __init__(self, raiz):
        self.raiz = os.path.abspath(raiz)
        os.makedirs(self.raiz, exist_ok=True)
        self.manifesto = os.path.join(self.raiz, "_manifesto.json")
        self.registro = self._ler_manifesto()

    def _ler_manifesto(self):
        if not os.path.isfile(self.manifesto):
            return {"tabelas": {}, "eventos": []}
        try:
            with open(self.manifesto, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            # Manifesto corrompido não pode esconder os dados: eles
            # estão no disco, e o manifesto é derivável deles.
            return {"tabelas": {}, "eventos": []}

    def gravar_manifesto(self):
        temporario = self.manifesto + ".parcial"
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(self.registro, f, ensure_ascii=False, indent=2,
                      default=str)
        os.replace(temporario, self.manifesto)

    def anotar(self, evento):
        self.registro.setdefault("eventos", []).append(evento)
        self.registro["eventos"] = self.registro["eventos"][-200:]


class ArcaneLago(dict):
    """Data Lake: Parquet, partições Hive e camadas."""

    def __new__(cls):
        return {
            "lago": cls._lago,
            "gravar": cls._gravar,
            "ler": cls._ler,
            "acrescentar": cls._gravar,

            # inspecionar
            "tabelas": cls._tabelas,
            "particoes": cls._particoes,
            "arquivos": cls._arquivos,
            "esquema": cls._esquema,
            "tamanho": cls._tamanho,
            "eventos": cls._eventos,

            # manter
            "compactar": cls._compactar,
            "remover_particao": cls._remover_particao,
            "vacuo": cls._vacuo,

            # camadas
            "camada": cls._camada,
            "promover": cls._promover,

            # Parquet solto, sem lago
            "gravar_parquet": cls._gravar_parquet,
            "ler_parquet": cls._ler_parquet,
            "esquema_parquet": cls._esquema_parquet,
        }

    # ── montar ──────────────────────────────────────────────

    @staticmethod
    def _lago(raiz):
        return Lago(raiz)

    @staticmethod
    def _camada(lago, nome):
        """Um lago apontado para uma camada: bronze, prata ou ouro."""
        if nome not in CAMADAS:
            raise ValueError_(
                f"'{nome}' não é uma camada.",
                nota=f"as camadas são: {', '.join(CAMADAS)}",
                dica="bronze guarda o bruto, prata o limpo, ouro o agregado",
                doc="tecnicas/lago")
        return Lago(os.path.join(lago.raiz, nome))

    # ── gravar ──────────────────────────────────────────────

    @staticmethod
    def _gravar(lago, tabela, linhas, particoes=None, compressao="gzip"):
        """Grava as linhas, particionando pelos campos que você indicar.

        Sempre ACRESCENTA: cada gravação cria um arquivo novo. Sobrescrever
        exigiria saber que a gravação anterior terminou, e num lago
        ninguém garante isso — quem quer trocar remove a partição antes.
        """
        linhas = list(linhas or [])
        if not linhas:
            return {"tabela": tabela, "linhas": 0, "arquivos": []}

        campos = list(particoes or [])
        for campo in campos:
            faltando = [i for i, l in enumerate(linhas)
                        if not isinstance(l, dict) or campo not in l]
            if faltando:
                raise ValueError_(
                    f"a linha {faltando[0]} não tem o campo de partição "
                    f"'{campo}'.",
                    nota=f"{len(faltando)} linha(s) sem ele",
                    dica="toda linha precisa do campo por onde se particiona",
                    doc="tecnicas/lago")

        grupos = {}
        for linha in linhas:
            chave = tuple((c, _seguro(linha[c])) for c in campos)
            grupos.setdefault(chave, []).append(linha)

        marca = time.strftime("%Y%m%d-%H%M%S")
        escritos = []
        for i, (chave, pedaco) in enumerate(sorted(grupos.items())):
            pasta = os.path.join(lago.raiz, _seguro(tabela),
                                 *[f"{c}={v}" for c, v in chave])
            os.makedirs(pasta, exist_ok=True)
            nome = f"parte-{marca}-{i:04d}.parquet"
            caminho = os.path.join(pasta, nome)

            # Os campos de partição saem das linhas: eles já estão no
            # caminho, e guardá-los duas vezes é desperdício — é assim
            # que o Hive faz, e o que os leitores esperam.
            sem_particao = [{k: v for k, v in l.items() if k not in campos}
                            for l in pedaco] if campos else pedaco
            if not sem_particao or not sem_particao[0]:
                sem_particao = pedaco

            r = parquet.escrever(caminho, sem_particao, compressao)
            escritos.append({
                "arquivo": os.path.relpath(caminho, lago.raiz),
                "particao": {c: v for c, v in chave},
                "linhas": r["linhas"], "bytes": r["bytes"],
            })

        registro = lago.registro.setdefault("tabelas", {}).setdefault(
            tabela, {"particionada_por": campos, "linhas": 0, "arquivos": 0})
        registro["particionada_por"] = campos
        registro["linhas"] += len(linhas)
        registro["arquivos"] += len(escritos)
        registro["atualizada_em"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        lago.anotar({"quando": registro["atualizada_em"], "o_que": "gravar",
                     "tabela": tabela, "linhas": len(linhas),
                     "arquivos": len(escritos)})
        lago.gravar_manifesto()

        return {"tabela": tabela, "linhas": len(linhas),
                "arquivos": escritos,
                "bytes": sum(e["bytes"] for e in escritos)}

    # ── ler ─────────────────────────────────────────────────

    @staticmethod
    def _ler(lago, tabela, filtro=None, colunas=None, limite=0):
        """Lê a tabela. O filtro por partição nem abre os outros arquivos.

        É o ponto do particionamento: 'ano=2026' descarta 2025 pelo
        NOME DA PASTA, sem ler um byte de dado.
        """
        raiz = os.path.join(lago.raiz, _seguro(tabela))
        if not os.path.isdir(raiz):
            raise FileNotFoundError_(
                f"não há a tabela '{tabela}' neste lago.",
                nota=f"há: {', '.join(ArcaneLago._tabelas(lago)) or 'nenhuma'}",
                doc="tecnicas/lago")

        filtro = {k: _seguro(v) for k, v in (filtro or {}).items()}
        saida = []
        for caminho, particao in _percorrer(raiz):
            if any(particao.get(k) != v for k, v in filtro.items()):
                continue
            pedidas = None
            if colunas:
                # Um campo de partição não está DENTRO do arquivo: ele
                # vem do caminho. Pedi-lo ao Parquet daria erro.
                pedidas = [c for c in colunas if c not in particao]
                if not pedidas:
                    pedidas = None
            linhas = parquet.ler(caminho, pedidas)
            for linha in linhas:
                completa = dict(particao)
                completa.update(linha)
                if colunas:
                    completa = {c: completa.get(c) for c in colunas}
                saida.append(completa)
                if limite and len(saida) >= limite:
                    return saida
        return saida

    # ── inspecionar ─────────────────────────────────────────

    @staticmethod
    def _tabelas(lago):
        if not os.path.isdir(lago.raiz):
            return []
        return sorted(n for n in os.listdir(lago.raiz)
                      if os.path.isdir(os.path.join(lago.raiz, n))
                      and not n.startswith("_") and n not in CAMADAS)

    @staticmethod
    def _particoes(lago, tabela):
        raiz = os.path.join(lago.raiz, _seguro(tabela))
        vistas = []
        for _, particao in _percorrer(raiz):
            if particao and particao not in vistas:
                vistas.append(particao)
        return vistas

    @staticmethod
    def _arquivos(lago, tabela, filtro=None):
        raiz = os.path.join(lago.raiz, _seguro(tabela))
        filtro = {k: _seguro(v) for k, v in (filtro or {}).items()}
        saida = []
        for caminho, particao in _percorrer(raiz):
            if any(particao.get(k) != v for k, v in filtro.items()):
                continue
            saida.append({"arquivo": os.path.relpath(caminho, lago.raiz),
                          "particao": particao,
                          "bytes": os.path.getsize(caminho)})
        return saida

    @staticmethod
    def _esquema(lago, tabela):
        """O esquema do primeiro arquivo, mais os campos de partição."""
        raiz = os.path.join(lago.raiz, _seguro(tabela))
        for caminho, particao in _percorrer(raiz):
            e = parquet.esquema(caminho)
            for campo in particao:
                e["colunas"].append({"nome": campo, "tipo": "texto",
                                     "aceita_vazio": False,
                                     "de_particao": True})
            return e
        return {"linhas": 0, "colunas": []}

    @staticmethod
    def _tamanho(lago, tabela=""):
        alvo = os.path.join(lago.raiz, _seguro(tabela)) if tabela else lago.raiz
        total = arquivos = 0
        for pasta, _, nomes in os.walk(alvo):
            for nome in nomes:
                if nome.endswith(".parquet"):
                    total += os.path.getsize(os.path.join(pasta, nome))
                    arquivos += 1
        return {"bytes": total, "arquivos": arquivos,
                "legivel": _humano(total)}

    @staticmethod
    def _eventos(lago, quantos=20):
        return lago.registro.get("eventos", [])[-int(quantos):]

    # ── manter ──────────────────────────────────────────────

    @staticmethod
    def _compactar(lago, tabela, minimo=2):
        """Junta os arquivinhos de cada partição num só.

        Um lago que recebe carga de hora em hora acumula 24 arquivos por
        dia por partição. Ler mil arquivos de 4 KB é muito mais lento
        que ler um de 4 MB — o custo está em ABRIR, não em ler.
        """
        raiz = os.path.join(lago.raiz, _seguro(tabela))
        por_pasta = {}
        for caminho, particao in _percorrer(raiz):
            por_pasta.setdefault(os.path.dirname(caminho), []).append(caminho)

        juntados = removidos = 0
        for pasta, arquivos in sorted(por_pasta.items()):
            if len(arquivos) < int(minimo):
                continue
            linhas = []
            for caminho in sorted(arquivos):
                linhas.extend(parquet.ler(caminho))
            if not linhas:
                continue
            marca = time.strftime("%Y%m%d-%H%M%S")
            novo = os.path.join(pasta, f"parte-{marca}-0000.parquet")
            temporario = novo + ".parcial"
            parquet.escrever(temporario, linhas)
            # Só apaga os antigos depois de o novo estar INTEIRO no
            # disco. Apagar antes e falhar no meio perde os dados.
            os.replace(temporario, novo)
            for caminho in arquivos:
                if os.path.abspath(caminho) != os.path.abspath(novo):
                    os.remove(caminho)
                    removidos += 1
            juntados += 1

        if juntados:
            lago.anotar({"quando": time.strftime("%Y-%m-%dT%H:%M:%S"),
                         "o_que": "compactar", "tabela": tabela,
                         "particoes": juntados, "removidos": removidos})
            lago.gravar_manifesto()
        return {"particoes_compactadas": juntados, "arquivos_removidos": removidos}

    @staticmethod
    def _remover_particao(lago, tabela, filtro):
        """Apaga uma partição inteira — é como se sobrescreve um período."""
        if not filtro:
            raise ValueError_(
                "remover_particao sem filtro apagaria a tabela inteira.",
                dica="passe o filtro, ou apague a pasta à mão se for isso mesmo",
                doc="tecnicas/lago")
        alvos = ArcaneLago._arquivos(lago, tabela, filtro)
        for a in alvos:
            os.remove(os.path.join(lago.raiz, a["arquivo"]))
        lago.anotar({"quando": time.strftime("%Y-%m-%dT%H:%M:%S"),
                     "o_que": "remover", "tabela": tabela,
                     "filtro": filtro, "arquivos": len(alvos)})
        lago.gravar_manifesto()
        return {"removidos": len(alvos)}

    @staticmethod
    def _vacuo(lago):
        """Tira pasta vazia e arquivo pela metade.

        Um '.parcial' é gravação interrompida: ele não tem rodapé, e
        nenhum leitor consegue abri-lo. Deixá-lo ali só confunde.
        """
        tirados = []
        for pasta, _, nomes in os.walk(lago.raiz, topdown=False):
            for nome in nomes:
                if nome.endswith(".parcial"):
                    os.remove(os.path.join(pasta, nome))
                    tirados.append(nome)
            if pasta != lago.raiz and not os.listdir(pasta):
                os.rmdir(pasta)
                tirados.append(os.path.relpath(pasta, lago.raiz) + "/")
        return {"tirados": tirados}

    # ── camadas ─────────────────────────────────────────────

    @staticmethod
    def _promover(lago, tabela, de, para, transformar=None, particoes=None):
        """Lê de uma camada, transforma, grava na seguinte.

        É o movimento que a arquitetura medalhão descreve, e o único que
        se repete: bronze → prata → ouro. O bruto NUNCA é alterado — é
        ele que permite reprocessar quando a regra estava errada.
        """
        origem = ArcaneLago._camada(lago, de)
        destino = ArcaneLago._camada(lago, para)
        linhas = ArcaneLago._ler(origem, tabela)
        if transformar is not None:
            linhas = transformar(linhas)
        r = ArcaneLago._gravar(destino, tabela, linhas, particoes)
        lago.anotar({"quando": time.strftime("%Y-%m-%dT%H:%M:%S"),
                     "o_que": "promover", "tabela": tabela,
                     "de": de, "para": para, "linhas": r["linhas"]})
        lago.gravar_manifesto()
        return r

    # ── Parquet solto ───────────────────────────────────────

    @staticmethod
    def _gravar_parquet(caminho, linhas, compressao="gzip"):
        return parquet.escrever(caminho, linhas, compressao)

    @staticmethod
    def _ler_parquet(caminho, colunas=None):
        return parquet.ler(caminho, colunas)

    @staticmethod
    def _esquema_parquet(caminho):
        return parquet.esquema(caminho)


def _percorrer(raiz):
    """(caminho, partição) de cada .parquet, em ordem estável."""
    if not os.path.isdir(raiz):
        return
    for pasta, subpastas, nomes in os.walk(raiz):
        subpastas.sort()
        particao = {}
        relativo = os.path.relpath(pasta, raiz)
        if relativo != ".":
            for parte in relativo.split(os.sep):
                if "=" in parte:
                    chave, _, valor = parte.partition("=")
                    particao[chave] = valor
        for nome in sorted(nomes):
            if nome.endswith(".parquet"):
                yield os.path.join(pasta, nome), particao


def _humano(n):
    for unidade in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unidade == "TB":
            return f"{n:.1f} {unidade}" if unidade != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} TB"
