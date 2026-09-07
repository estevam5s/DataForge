"""
Arcane.OS — sistema operacional, ambiente e informações do processo.

Somente leitura por padrão: nada aqui altera o sistema, salvo as funções
explicitamente marcadas (set_env, chdir).
"""

import json
import os


def _argv_do_programa():
    """Os argumentos passados ao programa apos '--'.

    A CLI os grava em DATAFORGE_ARGV como JSON. Sem a variavel — quando
    alguem importa o modulo fora do 'dataforge run' — devolve vazio.
    """
    bruto = os.environ.get("DATAFORGE_ARGV")
    if not bruto:
        return []
    try:
        return list(json.loads(bruto))
    except (ValueError, TypeError):
        return []

import platform
import shutil
import socket
import sys
import tempfile


class ArcaneOS:
    """Informações e utilidades do sistema operacional."""

    def __new__(cls):
        return {
            "__name__": "Arcane.OS",

            # ── Identificação ──
            "name": lambda: platform.system(),
            "platform": lambda: sys.platform,
            "release": lambda: platform.release(),
            "version": lambda: platform.version(),
            "machine": lambda: platform.machine(),
            "processor": lambda: platform.processor() or platform.machine(),
            "hostname": lambda: socket.gethostname(),
            "arch": lambda: platform.architecture()[0],
            "is_windows": lambda: os.name == "nt",
            "is_mac": lambda: sys.platform == "darwin",
            "is_linux": lambda: sys.platform.startswith("linux"),
            "is_posix": lambda: os.name == "posix",
            "info": cls._info,

            # ── Recursos ──
            "cpu_count": lambda: os.cpu_count() or 1,
            "disk_usage": cls._disk_usage,
            "memory_info": cls._memory_info,

            # ── Ambiente ──
            "env": cls._env,
            "get_env": lambda nome, padrao=None: os.environ.get(nome, padrao),
            "set_env": cls._set_env,
            "has_env": lambda nome: nome in os.environ,
            "env_names": lambda: sorted(os.environ.keys()),
            "path_separator": lambda: os.pathsep,
            "separator": lambda: os.sep,
            "line_separator": lambda: os.linesep,

            # ── Diretórios ──
            "cwd": lambda: os.getcwd(),
            "chdir": cls._chdir,
            "home": lambda: os.path.expanduser("~"),
            "temp_dir": lambda: tempfile.gettempdir(),
            "which": lambda prog: shutil.which(prog),

            # ── Usuário e processo ──
            "user": cls._user,
            "pid": lambda: os.getpid(),
            "parent_pid": lambda: os.getppid() if hasattr(os, "getppid") else 0,
            # Os argumentos do PROGRAMA, nao do interpretador: o que
            # vier depois de '--' na linha do dataforge. Devolver
            # sys.argv inteiro faria todo programa ter de descartar
            # 'dataforge', 'run' e o caminho do arquivo.
            "argv": _argv_do_programa,
            "argv_completo": lambda: list(sys.argv),
            "executable": lambda: sys.executable,
            "python_version": lambda: platform.python_version(),
            "exit": cls._exit,

            # ── Terminal ──
            "terminal_size": cls._terminal_size,
            "is_tty": lambda: sys.stdout.isatty(),
        }

    @staticmethod
    def _info():
        return {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "hostname": socket.gethostname(),
            "cpus": os.cpu_count() or 1,
            "python": platform.python_version(),
            "cwd": os.getcwd(),
            "user": ArcaneOS._user(),
        }

    @staticmethod
    def _env():
        return dict(os.environ)

    @staticmethod
    def _set_env(nome, valor):
        os.environ[nome] = str(valor)
        return valor

    @staticmethod
    def _chdir(caminho):
        os.chdir(caminho)
        return os.getcwd()

    @staticmethod
    def _user():
        for chave in ("USER", "USERNAME", "LOGNAME"):
            if chave in os.environ:
                return os.environ[chave]
        try:
            import getpass
            return getpass.getuser()
        except Exception:
            return "desconhecido"

    @staticmethod
    def _disk_usage(caminho="."):
        uso = shutil.disk_usage(caminho)
        return {
            "total": uso.total,
            "used": uso.used,
            "free": uso.free,
            "total_gb": round(uso.total / 1024 ** 3, 2),
            "used_gb": round(uso.used / 1024 ** 3, 2),
            "free_gb": round(uso.free / 1024 ** 3, 2),
            "percent_used": round(uso.used / uso.total * 100, 1) if uso.total else 0,
        }

    @staticmethod
    def _memory_info():
        """Memória do sistema, quando o SO expõe isso sem dependências."""
        try:
            if sys.platform.startswith("linux"):
                dados = {}
                with open("/proc/meminfo") as f:
                    for linha in f:
                        chave, _, resto = linha.partition(":")
                        dados[chave] = int(resto.strip().split()[0]) * 1024
                total = dados.get("MemTotal", 0)
                livre = dados.get("MemAvailable", dados.get("MemFree", 0))
                return {"total": total, "available": livre,
                        "used": total - livre,
                        "total_gb": round(total / 1024 ** 3, 2),
                        "available_gb": round(livre / 1024 ** 3, 2)}
            paginas = os.sysconf("SC_PHYS_PAGES")
            tamanho = os.sysconf("SC_PAGE_SIZE")
            total = paginas * tamanho
            return {"total": total, "total_gb": round(total / 1024 ** 3, 2),
                    "available": 0, "available_gb": 0}
        except (OSError, ValueError, AttributeError):
            return {"total": 0, "available": 0, "total_gb": 0, "available_gb": 0}

    @staticmethod
    def _terminal_size():
        try:
            tamanho = shutil.get_terminal_size()
            return {"columns": tamanho.columns, "lines": tamanho.lines}
        except Exception:
            return {"columns": 80, "lines": 24}

    @staticmethod
    def _exit(codigo=0):
        sys.exit(int(codigo))
