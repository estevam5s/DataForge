# -*- coding: utf-8 -*-
"""
Arcane.Stream — eventos contínuos: tópicos, partições e offsets.

    adopt Arcane.Stream as S

    corrente := S.corrente("eventos/")
    S.topico(corrente, "pedidos", 4)

    S.publicar(corrente, "pedidos", {"id": 1, "valor": 90}, "cliente-7")

    cycle e in S.consumir(corrente, "pedidos", "faturamento"):
        processar(e["valor"])
        S.confirmar(corrente, "pedidos", "faturamento", e)

─── Um broker em disco, não um Kafka ───────────────────────

Kafka é um cluster: réplicas, eleição de líder, coordenação entre
máquinas. Isto é um **log em arquivo** com a mesma semântica de
tópico, partição e offset — o que cabe num processo, e que é onde a
maioria dos fluxos de verdade começa.

Um evento publicado aqui não some quando o consumidor cai. É essa a
diferença entre uma fila e um log: a fila entrega e esquece; o log
guarda, e cada consumidor lembra onde parou. Dois consumidores
diferentes leem o mesmo evento sem disputar.

─── Por que partição ───────────────────────────────────────

Uma partição é a unidade de ORDEM. Eventos com a mesma chave caem
sempre na mesma partição, e ali a ordem é garantida — os três eventos
do cliente 7 chegam na ordem em que aconteceram.

Entre partições não há ordem, e é justamente isso que permite processar
quatro em paralelo. Quem quer ordem total usa uma partição só, e paga
com a serialização.

─── O que ele não faz ──────────────────────────────────────

Não há réplica, não há transação entre tópicos, não há coordenação
automática entre consumidores de um mesmo grupo — cada processo lê as
partições que você mandar. E o offset é confirmado DEPOIS de processar,
o que dá 'ao menos uma vez': um processo que cai entre processar e
confirmar reprocessa o evento. É a garantia honesta; 'exatamente uma
vez' exige transação de ponta a ponta, e ninguém a tem de graça.
"""

import hashlib
import json
import os
import time

from ..errors import FileNotFoundError_, ValueError_

#: Quantos eventos por arquivo de segmento.
#:
#: O segmento é a unidade que se apaga inteira na retenção. Grandes
#: demais seguram lixo por muito tempo; pequenos demais enchem a pasta
#: de arquivos e o custo passa a ser abrir.
POR_SEGMENTO = 1000


def _particao_de(chave, quantas):
    """A partição de uma chave. Estável entre execuções.

    hash() do Python é aleatorizado por processo desde a 3.3: usá-lo
    mandaria a mesma chave para partições diferentes a cada execução, e
    a ordem por chave — que é a única coisa que a partição garante —
    deixaria de existir.
    """
    if chave is None:
        return 0
    digest = hashlib.sha256(str(chave).encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % max(1, quantas)


class Corrente:
    """A raiz em disco, e os tópicos que existem nela."""

    def __init__(self, raiz):
        self.raiz = os.path.abspath(raiz)
        os.makedirs(self.raiz, exist_ok=True)
        self.registro = os.path.join(self.raiz, "_topicos.json")
        self.topicos = self._ler()

    def _ler(self):
        if not os.path.isfile(self.registro):
            return {}
        try:
            with open(self.registro, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def gravar(self):
        temporario = self.registro + ".parcial"
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(self.topicos, f, ensure_ascii=False, indent=2)
        os.replace(temporario, self.registro)

    def pasta(self, topico, particao=None):
        alvo = os.path.join(self.raiz, topico)
        if particao is not None:
            alvo = os.path.join(alvo, f"p{particao}")
        return alvo

    def exigir(self, topico):
        if topico not in self.topicos:
            raise FileNotFoundError_(
                f"não há o tópico '{topico}'.",
                nota=f"há: {', '.join(sorted(self.topicos)) or 'nenhum'}",
                dica="crie com 'Stream.topico(corrente, nome, particoes)'",
                doc="tecnicas/streaming")
        return self.topicos[topico]


def _segmento(pasta, indice):
    return os.path.join(pasta, f"seg-{indice:08d}.jsonl")


def _segmentos(pasta):
    if not os.path.isdir(pasta):
        return []
    return sorted(n for n in os.listdir(pasta)
                  if n.startswith("seg-") and n.endswith(".jsonl"))


class ArcaneStream(dict):
    """Streaming: tópicos, partições, offsets e grupos."""

    def __new__(cls):
        return {
            # montar
            "corrente": cls._corrente,
            "topico": cls._topico,
            "topicos": cls._topicos,
            "remover_topico": cls._remover_topico,

            # publicar
            "publicar": cls._publicar,
            "publicar_lote": cls._publicar_lote,

            # consumir
            "consumir": cls._consumir,
            "ler_de": cls._ler_de,
            "confirmar": cls._confirmar,
            "confirmar_ate": cls._confirmar_ate,

            # posição
            "offset": cls._offset,
            "voltar": cls._voltar,
            "atraso": cls._atraso,
            "grupos": cls._grupos,

            # manter
            "informacao": cls._informacao,
            "reter": cls._reter,
            "janela": cls._janela,
        }

    # ── montar ──────────────────────────────────────────────

    @staticmethod
    def _corrente(raiz):
        return Corrente(raiz)

    @staticmethod
    def _topico(corrente, nome, particoes=1):
        """Cria o tópico. Chamar de novo não apaga o que existe."""
        if nome in corrente.topicos:
            return corrente.topicos[nome]
        quantas = max(1, int(particoes))
        for p in range(quantas):
            os.makedirs(corrente.pasta(nome, p), exist_ok=True)
        corrente.topicos[nome] = {
            "particoes": quantas,
            "criado_em": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "grupos": {},
        }
        corrente.gravar()
        return corrente.topicos[nome]

    @staticmethod
    def _topicos(corrente):
        return sorted(corrente.topicos)

    @staticmethod
    def _remover_topico(corrente, nome):
        import shutil
        corrente.exigir(nome)
        shutil.rmtree(corrente.pasta(nome), ignore_errors=True)
        corrente.topicos.pop(nome, None)
        corrente.gravar()
        return True

    # ── publicar ────────────────────────────────────────────

    @staticmethod
    def _publicar(corrente, topico, valor, chave=None):
        """Um evento. A chave decide a partição — e a ordem.

        Sem chave, ele vai para a partição 0. Distribuir sem chave
        pareceria melhor, mas quebraria a única garantia que a partição
        dá: quem não escolheu chave provavelmente quer ordem.
        """
        return ArcaneStream._publicar_lote(
            corrente, topico, [{"valor": valor, "chave": chave}])[0]

    @staticmethod
    def _publicar_lote(corrente, topico, eventos):
        """Vários de uma vez — um 'open' por partição, não por evento."""
        info = corrente.exigir(topico)
        quantas = info["particoes"]

        por_particao = {}
        for e in eventos or []:
            if isinstance(e, dict) and "valor" in e:
                valor, chave = e["valor"], e.get("chave")
            else:
                valor, chave = e, None
            por_particao.setdefault(_particao_de(chave, quantas), []).append(
                (valor, chave))

        escritos = []
        for particao, lote in sorted(por_particao.items()):
            pasta = corrente.pasta(topico, particao)
            os.makedirs(pasta, exist_ok=True)
            proximo = ArcaneStream._proximo_offset(pasta)
            indice = proximo // POR_SEGMENTO
            caminho = _segmento(pasta, indice)

            with open(caminho, "a", encoding="utf-8") as f:
                for valor, chave in lote:
                    registro = {
                        "offset": proximo,
                        "particao": particao,
                        "chave": chave,
                        "valor": valor,
                        "quando": time.time(),
                    }
                    f.write(json.dumps(registro, ensure_ascii=False,
                                       default=str) + "\n")
                    escritos.append(registro)
                    proximo += 1
                    # Um segmento novo a cada POR_SEGMENTO: é a unidade
                    # que a retenção apaga inteira.
                    if proximo % POR_SEGMENTO == 0:
                        f.close()
                        indice = proximo // POR_SEGMENTO
                        caminho = _segmento(pasta, indice)
                        f = open(caminho, "a", encoding="utf-8")
        return escritos

    @staticmethod
    def _proximo_offset(pasta):
        """O offset que o próximo evento vai receber."""
        nomes = _segmentos(pasta)
        if not nomes:
            return 0
        ultimo = os.path.join(pasta, nomes[-1])
        base = int(nomes[-1][4:12]) * POR_SEGMENTO
        with open(ultimo, encoding="utf-8") as f:
            return base + sum(1 for linha in f if linha.strip())

    # ── consumir ────────────────────────────────────────────

    @staticmethod
    def _ler_de(corrente, topico, desde=0, quantos=0, particao=None):
        """Lê a partir de um offset, sem grupo e sem confirmar.

        É a leitura para inspecionar: ela não mexe em posição nenhuma.
        """
        info = corrente.exigir(topico)
        alvos = [int(particao)] if particao is not None \
            else range(info["particoes"])
        saida = []
        for p in alvos:
            pasta = corrente.pasta(topico, p)
            for nome in _segmentos(pasta):
                base = int(nome[4:12]) * POR_SEGMENTO
                if quantos and len(saida) >= quantos:
                    break
                with open(os.path.join(pasta, nome), encoding="utf-8") as f:
                    for linha in f:
                        if not linha.strip():
                            continue
                        evento = json.loads(linha)
                        if evento["offset"] < desde:
                            continue
                        saida.append(evento)
                        if quantos and len(saida) >= quantos:
                            break
        saida.sort(key=lambda e: (e["particao"], e["offset"]))
        return saida

    @staticmethod
    def _consumir(corrente, topico, grupo, quantos=0, particao=None):
        """Os eventos que este grupo ainda não confirmou.

        Ele NÃO avança a posição: quem avança é 'confirmar', depois de
        processar. Avançar na leitura daria 'no máximo uma vez' — um
        processo que cai no meio perderia o evento em silêncio, que é o
        pior resultado possível num fluxo de dados.
        """
        info = corrente.exigir(topico)
        posicoes = info.setdefault("grupos", {}).setdefault(grupo, {})
        alvos = [int(particao)] if particao is not None \
            else range(info["particoes"])

        saida = []
        for p in alvos:
            desde = posicoes.get(str(p), 0)
            pasta = corrente.pasta(topico, p)
            for nome in _segmentos(pasta):
                if quantos and len(saida) >= quantos:
                    break
                with open(os.path.join(pasta, nome), encoding="utf-8") as f:
                    for linha in f:
                        if not linha.strip():
                            continue
                        evento = json.loads(linha)
                        if evento["offset"] < desde:
                            continue
                        evento["grupo"] = grupo
                        saida.append(evento)
                        if quantos and len(saida) >= quantos:
                            break
        saida.sort(key=lambda e: (e["particao"], e["offset"]))
        return saida

    @staticmethod
    def _confirmar(corrente, topico, grupo, evento):
        """Marca este evento como processado.

        A posição vira offset+1: ela aponta para o PRÓXIMO a ler, e não
        para o último lido. Guardar o último faria toda retomada
        reprocessar um evento — sempre o mesmo.
        """
        info = corrente.exigir(topico)
        posicoes = info.setdefault("grupos", {}).setdefault(grupo, {})
        chave = str(evento["particao"])
        posicoes[chave] = max(posicoes.get(chave, 0), evento["offset"] + 1)
        corrente.gravar()
        return posicoes[chave]

    @staticmethod
    def _confirmar_ate(corrente, topico, grupo, eventos):
        """Confirma um lote de uma vez — uma gravação, não n."""
        info = corrente.exigir(topico)
        posicoes = info.setdefault("grupos", {}).setdefault(grupo, {})
        for evento in eventos or []:
            chave = str(evento["particao"])
            posicoes[chave] = max(posicoes.get(chave, 0), evento["offset"] + 1)
        corrente.gravar()
        return dict(posicoes)

    # ── posição ─────────────────────────────────────────────

    @staticmethod
    def _offset(corrente, topico, grupo):
        info = corrente.exigir(topico)
        return dict(info.get("grupos", {}).get(grupo, {}))

    @staticmethod
    def _voltar(corrente, topico, grupo, para=0):
        """Reprocessar do começo — o que uma fila não permite.

        É o motivo de o log guardar o evento depois de entregue: quando
        a regra estava errada, dá para rodar tudo de novo.
        """
        info = corrente.exigir(topico)
        info.setdefault("grupos", {})[grupo] = {
            str(p): int(para) for p in range(info["particoes"])}
        corrente.gravar()
        return True

    @staticmethod
    def _atraso(corrente, topico, grupo):
        """Quantos eventos faltam. É a métrica que se vigia.

        Um atraso que só cresce significa que a produção passou o
        consumo — e o momento de agir é antes de o disco encher.
        """
        info = corrente.exigir(topico)
        posicoes = info.get("grupos", {}).get(grupo, {})
        total = por_particao = 0
        detalhe = {}
        for p in range(info["particoes"]):
            fim = ArcaneStream._proximo_offset(corrente.pasta(topico, p))
            atras = max(0, fim - posicoes.get(str(p), 0))
            detalhe[f"p{p}"] = atras
            total += atras
        return {"total": total, "por_particao": detalhe}

    @staticmethod
    def _grupos(corrente, topico):
        return sorted(corrente.exigir(topico).get("grupos", {}))

    # ── manter ──────────────────────────────────────────────

    @staticmethod
    def _informacao(corrente, topico):
        info = corrente.exigir(topico)
        particoes = []
        for p in range(info["particoes"]):
            pasta = corrente.pasta(topico, p)
            bytes_ = sum(os.path.getsize(os.path.join(pasta, n))
                         for n in _segmentos(pasta))
            particoes.append({
                "particao": p,
                "eventos": ArcaneStream._proximo_offset(pasta),
                "segmentos": len(_segmentos(pasta)),
                "bytes": bytes_,
            })
        return {"topico": topico, "particoes": particoes,
                "grupos": sorted(info.get("grupos", {})),
                "eventos": sum(p["eventos"] for p in particoes),
                "bytes": sum(p["bytes"] for p in particoes)}

    @staticmethod
    def _reter(corrente, topico, segmentos=10):
        """Apaga os segmentos mais antigos, guardando os últimos n.

        Um log que só cresce enche o disco. A retenção apaga por
        SEGMENTO, e não por evento: apagar o meio de um arquivo exigiria
        reescrevê-lo inteiro, e o offset dos que sobram mudaria.
        """
        info = corrente.exigir(topico)
        apagados = 0
        for p in range(info["particoes"]):
            pasta = corrente.pasta(topico, p)
            nomes = _segmentos(pasta)
            for nome in nomes[:max(0, len(nomes) - int(segmentos))]:
                os.remove(os.path.join(pasta, nome))
                apagados += 1
        return {"segmentos_apagados": apagados}

    @staticmethod
    def _janela(eventos, segundos=60, campo="quando"):
        """Agrupa os eventos em janelas de tempo.

        É a operação que dá sentido a um fluxo: 'quantos por minuto' é
        a pergunta que se faz, e ela não existe sem janela.
        """
        janelas = {}
        for evento in eventos or []:
            instante = evento.get(campo) if isinstance(evento, dict) else None
            if not isinstance(instante, (int, float)):
                continue
            inicio = int(instante // segundos) * segundos
            janelas.setdefault(inicio, []).append(evento)
        return [{"inicio": k, "fim": k + segundos,
                 "quantos": len(v), "eventos": v}
                for k, v in sorted(janelas.items())]
