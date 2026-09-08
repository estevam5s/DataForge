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
}


def get_module(name: str):
    """Get a standard library module by name."""
    if name in _MODULES:
        mod = _MODULES[name]
        if callable(mod) and not isinstance(mod, dict):
            return mod()
        return mod
    return None


def list_modules():
    """List all available standard library modules."""
    return list(_MODULES.keys())
