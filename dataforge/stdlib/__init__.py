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
_COMPLEMENTOS = {
    "Arcane.Collections": (ArcaneColecoesEsp,),
    "Collections": (ArcaneColecoesEsp,),
}


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
    mod = _MODULES[name]
    if callable(mod) and not isinstance(mod, dict):
        mod = mod()
    for extra in _COMPLEMENTOS.get(name, ()):
        # Um modulo montado de duas partes. O complemento vence nos
        # nomes repetidos: ele e o mais completo.
        mod = {**mod, **extra()}
    if isinstance(mod, dict):
        mod.setdefault("__name__", name)
    return mod


def list_modules():
    """List all available standard library modules."""
    return list(_MODULES.keys())
