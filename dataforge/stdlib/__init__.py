"""
DataForge Standard Library
Module registry and loader.
"""

from .arcane_io import ArcaneIO
from .arcane_math import ArcaneMath
from .arcane_web import ArcaneWeb
from .arcane_cortex import ArcaneCortex
from .arcane_data import ArcaneData
from .arcane_regex import ArcaneRegex
from .arcane_test import ArcaneTest
from .arcane_functional import ArcaneFunctional
from .arcane_async import ArcaneAsync
from .arcane_text import ArcaneText
from .arcane_analytics import ArcaneAnalytics
from .arcane_database import ArcaneDatabase
from .arcane_http import ArcaneHttp
from .arcane_time import ArcaneTime
from .arcane_os import ArcaneOS
from .arcane_process import ArcaneProcess
from .arcane_logging import ArcaneLogging
from .arcane_crypto import ArcaneCrypto
from .arcane_collections import ArcaneCollections
from .arcane_serialization import ArcaneSerialization
from .kiln import ArcaneKiln
from .arcane_excel import ArcaneExcel
from .arcane_meta import ArcaneMeta
from .crucible import ArcaneCrucible
from .forge import ArcaneForge
from .arcane_colecoes_esp import ArcaneCollections as ArcaneColecoesEsp
from .arcane_iter import ArcaneIter
from .arcane_cor import ArcaneColor
from .arcane_paralelo import ArcaneConcurrent
from .arcane_arquivo_seguro import ArcaneArchive, ArcaneCofre
from .arcane_pipeline import ArcanePipeline
from .arcane_qualidade import ArcaneQualidade
from .arcane_lago import ArcaneLago
from .arcane_fluxo import ArcaneStream
from .arcane_observar import ArcaneObservar
from .arcane_ponte import ArcanePonte
from .arcane_decimal import ArcaneDecimal
from .arcane_api import ArcaneAPI
from .vitrine import ArcaneVitrine
from .arcane_malha import ArcaneMalha

_MODULES = {
    "Arcane.IO": ArcaneIO,
    "Arcane.Math": ArcaneMath,
    "Arcane.Web": ArcaneWeb,
    "Arcane.Cortex": ArcaneCortex,
    "Arcane.Data": ArcaneData,
    "Arcane.Regex": ArcaneRegex,
    "Arcane.Test": ArcaneTest,
    "Arcane.Functional": ArcaneFunctional,
    "Arcane.Async": ArcaneAsync,
    "Arcane.Text": ArcaneText,
    "IO": ArcaneIO,
    "Math": ArcaneMath,
    "Web": ArcaneWeb,
    "Cortex": ArcaneCortex,
    "Data": ArcaneData,
    "Regex": ArcaneRegex,
    "Test": ArcaneTest,
    "Functional": ArcaneFunctional,
    "Async": ArcaneAsync,
    "Text": ArcaneText,
    "Arcane.Analytics": ArcaneAnalytics,
    "Arcane.Database": ArcaneDatabase,
    "Analytics": ArcaneAnalytics,
    "Database": ArcaneDatabase,
    "DB": ArcaneDatabase,
    "Arcane.Http": ArcaneHttp,
    "Http": ArcaneHttp,
    "Server": ArcaneHttp,
    "Network": ArcaneWeb,

    # ── DataForge 4.0 ──
    "Arcane.Time": ArcaneTime,
    "Time": ArcaneTime,
    "Arcane.OS": ArcaneOS,
    "OS": ArcaneOS,
    "Arcane.Process": ArcaneProcess,
    "Process": ArcaneProcess,
    "Arcane.Logging": ArcaneLogging,
    "Logging": ArcaneLogging,
    "Log": ArcaneLogging,
    "Arcane.Crypto": ArcaneCrypto,
    "Crypto": ArcaneCrypto,
    "Arcane.Collections": ArcaneCollections,
    "Collections": ArcaneCollections,
    "Arcane.Serialization": ArcaneSerialization,
    "Serialization": ArcaneSerialization,
    "Serde": ArcaneSerialization,

    # ── Kiln 4.2 — framework web ──
    "Kiln": ArcaneKiln,
    "Arcane.Kiln": ArcaneKiln,
    "Arcane.Excel": ArcaneExcel,
    "Excel": ArcaneExcel,
    "Xlsx": ArcaneExcel,

    # ── Metadados de decorador ──
    "Arcane.Meta": ArcaneMeta,
    "Meta": ArcaneMeta,

    # ── Crucible — o framework de testes ──
    "Crucible": ArcaneCrucible,
    "Arcane.Crucible": ArcaneCrucible,

    # ── Iteradores e cor ──
    "Arcane.Iter": ArcaneIter,
    "Iter": ArcaneIter,
    "Arcane.Concurrent": ArcaneConcurrent,
    "Concurrent": ArcaneConcurrent,
    "Paralelo": ArcaneConcurrent,

    # ── Engenharia de dados ──
    "Arcane.Pipeline": ArcanePipeline,
    "Pipeline": ArcanePipeline,
    "Fluxo": ArcanePipeline,
    "Arcane.Stream": ArcaneStream,
    "Stream": ArcaneStream,
    "Corrente": ArcaneStream,
    "Arcane.Observar": ArcaneObservar,
    "Observar": ArcaneObservar,
    "Observe": ArcaneObservar,
    "Arcane.Lago": ArcaneLago,
    "Lago": ArcaneLago,
    "Lake": ArcaneLago,
    "Parquet": ArcaneLago,
    "Arcane.API": ArcaneAPI,
    "API": ArcaneAPI,

    # ── Vitrine — dashboards e aplicacoes de dados ──
    "Arcane.Vitrine": ArcaneVitrine,
    "Vitrine": ArcaneVitrine,
    "Painel": ArcaneVitrine,

    # ── Malha — chamada entre servicos ──
    "Arcane.Malha": ArcaneMalha,
    "Malha": ArcaneMalha,
    "Mesh": ArcaneMalha,

    "Arcane.Decimal": ArcaneDecimal,
    "Decimal": ArcaneDecimal,
    "Exato": ArcaneDecimal,

    "Arcane.Ponte": ArcanePonte,
    "Ponte": ArcanePonte,
    "Bridge": ArcanePonte,

    "Arcane.Qualidade": ArcaneQualidade,
    "Qualidade": ArcaneQualidade,
    "Quality": ArcaneQualidade,

    "Arcane.Archive": ArcaneArchive,
    "Archive": ArcaneArchive,
    "Zip": ArcaneArchive,
    "Arcane.Color": ArcaneColor,
    "Color": ArcaneColor,
    "Cor": ArcaneColor,

    # ── Forge — bancos de dados e ORM ──
    "Forge": ArcaneForge,
    "Arcane.Forge": ArcaneForge,
    "Banco": ArcaneForge,
}


#: Modulos servidos sob o mesmo nome, juntos.
#:
#: 'Arcane.Collections' e o caso: uma parte trazia 'group_by' e
#: 'sort_by_field', a outra traz fila, heap e conjunto. Sao o mesmo
#: assunto, e obrigar quem escreve a lembrar em qual metade esta cada
#: funcao seria arbitrario.
#: A chave e o nome OFICIAL — o apelido chega ate aqui ja traduzido
#: por '_CANONICO'. Listar apelido por apelido daria o mesmo modulo
#: completo por um nome e pela metade por outro.
_COMPLEMENTOS = {
    "Arcane.Collections": (ArcaneColecoesEsp,),
    "Arcane.Crypto": (ArcaneCofre,),
}


def _canonicos():
    """Para cada apelido, o nome oficial do modulo que ele aponta.

    'Zip', 'Archive' e 'Arcane.Archive' sao o MESMO modulo, e ele
    precisa se chamar 'Arcane.Archive' venha por onde vier. Carimbar o
    apelido pedido fazia o mesmo modulo aparecer como varios: o site
    contava 33 modulos onde ha 29, e a descricao do catalogo — indexada
    pelo nome oficial — nao era encontrada para nenhum apelido.

    O oficial e a forma 'Arcane.X' quando existe; senao, o primeiro
    nome registrado.
    """
    por_objeto = {}
    for chave, valor in _MODULES.items():
        por_objeto.setdefault(id(valor), []).append(chave)

    mapa = {}
    for chaves in por_objeto.values():
        oficial = next((c for c in chaves if c.startswith("Arcane.")), chaves[0])
        for c in chaves:
            mapa[c] = oficial
    return mapa


_CANONICO = _canonicos()


def get_module(name: str):
    """Um modulo da biblioteca padrao, pelo nome.

    Carimba '__name__' em quem nao declarou. Nao e enfeite: o
    interpretador usa esse campo para saber que o dicionario e um
    MODULO, e nao um vault comum — e so entao os simbolos dele
    ganham prioridade sobre os metodos de vault.

    Sem o carimbo, um modulo com um simbolo chamado 'set', 'get',
    'keys' ou 'merge' via esse nome ser engolido pelo metodo de vault
    de mesmo nome. Foi o que aconteceu com 'Collections.set': ele
    resolvia para o 'set' do vault, e a mensagem falava de argumento
    faltando — sem nenhuma pista da causa.
    """
    if name not in _MODULES:
        return None
    oficial = _CANONICO.get(name, name)
    mod = _MODULES[name]
    if callable(mod) and not isinstance(mod, dict):
        mod = mod()
    for extra in _COMPLEMENTOS.get(oficial, ()):
        # Um modulo montado de duas partes. O complemento vence nos
        # nomes repetidos: ele e o mais completo.
        mod = {**mod, **extra()}
    if isinstance(mod, dict):
        mod.setdefault("__name__", oficial)
    return mod


def reiniciar_por_execucao():
    """Zera o estado que pertence a UMA execucao de programa.

    Quase todo modulo da biblioteca e sem memoria: 'Arcane.Math.sqrt'
    nao lembra da chamada anterior. O Crucible e a excecao — ele
    ACUMULA, porque 'crucible'/'trial' registram e 'Crucible.run()'
    executa o que foi registrado.

    Esse registro era um objeto de modulo, um por PROCESSO. Dois
    programas no mesmo processo compartilhavam a lista de testes: o
    'dataforge test' cria um interpretador por arquivo, e o segundo
    arquivo via os trials do primeiro — contagem errada, e a falha de um
    reaparecendo no relatorio do outro. Num framework de teste, um
    relatorio errado e a pior falha possivel.

    Chamado uma vez por interpretador, na primeira execucao. Nao a cada
    'adopt': um programa com dois 'adopt Crucible' apagaria o que o
    primeiro registrou. Nem a cada 'run': o REPL chama 'run' por linha,
    e a suite montada na linha 3 precisa existir na linha 4.
    """
    from .crucible import REGISTRO
    REGISTRO.reiniciar()


def list_modules():
    """List all available standard library modules."""
    return list(_MODULES.keys())
