"""
Arcane.Logging — registro estruturado de eventos.

Seis níveis (TRACE, DEBUG, INFO, WARN, ERROR, FATAL), saída em terminal com
cores e/ou em arquivo, campos estruturados e formato JSON opcional.
"""

import json
import os
import sys
import threading
from datetime import datetime

NIVEIS = {"TRACE": 10, "DEBUG": 20, "INFO": 30,
          "WARN": 40, "ERROR": 50, "FATAL": 60}

CORES = {"TRACE": "0;90", "DEBUG": "0;36", "INFO": "1;32",
         "WARN": "1;33", "ERROR": "1;31", "FATAL": "1;35"}


class _Logger:
    """Um logger nomeado, com nível, destinos e campos fixos."""

    def __init__(self, nome="app", nivel="INFO"):
        self.nome = nome
        self.nivel = nivel.upper()
        self.arquivo = None
        self.usar_cor = sys.stdout.isatty()
        self.formato_json = False
        self.mostrar_horario = True
        self.contexto = {}
        self.registros = []
        self.guardar = False
        self._lock = threading.Lock()
        self.contagem = {n: 0 for n in NIVEIS}

    # ── Configuração ──

    def set_level(self, nivel):
        nivel = str(nivel).upper()
        if nivel not in NIVEIS:
            raise ValueError(f"Nível inválido: {nivel}. Use {', '.join(NIVEIS)}")
        self.nivel = nivel
        return self

    def to_file(self, caminho, anexar=True):
        pasta = os.path.dirname(caminho)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        self.arquivo = open(caminho, "a" if anexar else "w", encoding="utf-8")
        return self

    def close(self):
        if self.arquivo:
            self.arquivo.close()
            self.arquivo = None
        return self

    def as_json(self, ativo=True):
        self.formato_json = bool(ativo)
        return self

    def colored(self, ativo=True):
        self.usar_cor = bool(ativo)
        return self

    def with_context(self, campos):
        self.contexto.update(campos or {})
        return self

    def keep(self, ativo=True):
        """Guarda os registros em memória (útil para testar)."""
        self.guardar = bool(ativo)
        return self

    # ── Emissão ──

    def log(self, nivel, mensagem, campos=None):
        nivel = nivel.upper()
        if NIVEIS.get(nivel, 0) < NIVEIS[self.nivel]:
            return None

        agora = datetime.now()
        registro = {
            "time": agora.isoformat(timespec="seconds"),
            "level": nivel,
            "logger": self.nome,
            "message": str(mensagem),
        }
        registro.update(self.contexto)
        if campos:
            registro.update(campos)

        with self._lock:
            self.contagem[nivel] += 1
            if self.guardar:
                self.registros.append(registro)
            linha = self._formatar(registro, agora, nivel, mensagem, campos)
            print(linha)
            if self.arquivo:
                self.arquivo.write(self._formatar(
                    registro, agora, nivel, mensagem, campos, cor=False) + "\n")
                self.arquivo.flush()
        return registro

    def _formatar(self, registro, agora, nivel, mensagem, campos, cor=None):
        if self.formato_json:
            return json.dumps(registro, ensure_ascii=False, default=str)
        usar_cor = self.usar_cor if cor is None else cor
        rotulo = nivel.ljust(5)
        if usar_cor:
            rotulo = f"\033[{CORES[nivel]}m{rotulo}\033[0m"
        partes = []
        if self.mostrar_horario:
            partes.append(agora.strftime("%H:%M:%S"))
        partes.append(rotulo)
        if self.nome and self.nome != "app":
            partes.append(f"[{self.nome}]")
        partes.append(str(mensagem))
        extras = {**self.contexto, **(campos or {})}
        if extras:
            partes.append(" ".join(f"{k}={v}" for k, v in extras.items()))
        return " ".join(partes)

    # ── Atalhos por nível ──

    def trace(self, m, campos=None): return self.log("TRACE", m, campos)
    def debug(self, m, campos=None): return self.log("DEBUG", m, campos)
    def info(self, m, campos=None): return self.log("INFO", m, campos)
    def warn(self, m, campos=None): return self.log("WARN", m, campos)
    def error(self, m, campos=None): return self.log("ERROR", m, campos)
    def fatal(self, m, campos=None): return self.log("FATAL", m, campos)

    # ── Consulta ──

    def stats(self):
        return {n: c for n, c in self.contagem.items() if c}

    def records(self):
        return list(self.registros)

    def clear(self):
        self.registros.clear()
        self.contagem = {n: 0 for n in NIVEIS}
        return self

    def __repr__(self):
        return f"<logger '{self.nome}' nivel={self.nivel}>"


_PADRAO = _Logger("app")


class ArcaneLogging:
    """Registro estruturado de eventos."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Logging",

            "logger": lambda nome="app", nivel="INFO": _Logger(nome, nivel),
            "default": lambda: _PADRAO,
            "set_level": lambda n: _PADRAO.set_level(n),
            "to_file": lambda c, anexar=True: _PADRAO.to_file(c, anexar),
            "as_json": lambda a=True: _PADRAO.as_json(a),

            "trace": lambda m, campos=None: _PADRAO.trace(m, campos),
            "debug": lambda m, campos=None: _PADRAO.debug(m, campos),
            "info": lambda m, campos=None: _PADRAO.info(m, campos),
            "warn": lambda m, campos=None: _PADRAO.warn(m, campos),
            "error": lambda m, campos=None: _PADRAO.error(m, campos),
            "fatal": lambda m, campos=None: _PADRAO.fatal(m, campos),
            "log": lambda n, m, campos=None: _PADRAO.log(n, m, campos),

            "stats": lambda: _PADRAO.stats(),
            "levels": lambda: list(NIVEIS.keys()),
        }
