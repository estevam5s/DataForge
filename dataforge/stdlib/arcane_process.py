"""
Arcane.Process — execução de processos externos.

Roda comandos, captura stdout/stderr e o código de saída. Por padrão os
comandos NÃO passam pelo shell: a lista de argumentos é entregue direto ao
sistema, o que evita injeção. Use shell := yes conscientemente.
"""

import os
import shlex
import signal
import subprocess
import sys


def _resultado(proc, saida, erro, comando):
    return {
        "__type__": "ProcessResult",
        "command": comando,
        "stdout": saida or "",
        "stderr": erro or "",
        "exit_code": proc.returncode,
        "ok": proc.returncode == 0,
        "failed": proc.returncode != 0,
        "lines": (saida or "").splitlines(),
    }


def _normalizar(comando, shell):
    if isinstance(comando, str):
        return comando if shell else shlex.split(comando)
    return list(comando)


class ArcaneProcess:
    """Execução e controle de processos externos."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Process",

            # ── Execução ──
            "run": cls._run,
            "run_shell": lambda cmd, timeout=None: cls._run(cmd, shell=True, timeout=timeout),
            "capture": cls._capture,
            "check": cls._check,
            "exit_code": cls._exit_code,
            "spawn": cls._spawn,
            "pipeline": cls._pipeline,

            # ── Controle ──
            "wait": cls._wait,
            "kill": cls._kill,
            "terminate": cls._terminate,
            "is_running": cls._is_running,

            # ── Consulta ──
            "which": cls._which,
            "exists": lambda prog: cls._which(prog) is not None,
            "pid": lambda: os.getpid(),
            "python": lambda: sys.executable,
        }

    @staticmethod
    def _run(comando, shell=False, timeout=None, cwd=None, env=None, input_text=None):
        """Executa e espera. Devolve um ProcessResult com stdout, stderr e código."""
        alvo = _normalizar(comando, shell)
        ambiente = None
        if env:
            ambiente = dict(os.environ)
            ambiente.update({str(k): str(v) for k, v in env.items()})
        try:
            proc = subprocess.run(
                alvo, shell=bool(shell), capture_output=True, text=True,
                timeout=timeout, cwd=cwd, env=ambiente, input=input_text)
            return _resultado(proc, proc.stdout, proc.stderr, comando)
        except subprocess.TimeoutExpired:
            return {"__type__": "ProcessResult", "command": comando,
                    "stdout": "", "stderr": f"tempo esgotado após {timeout}s",
                    "exit_code": -1, "ok": False, "failed": True,
                    "timed_out": True, "lines": []}
        except FileNotFoundError:
            programa = alvo[0] if isinstance(alvo, list) else alvo
            return {"__type__": "ProcessResult", "command": comando,
                    "stdout": "", "stderr": f"comando não encontrado: {programa}",
                    "exit_code": 127, "ok": False, "failed": True, "lines": []}

    @staticmethod
    def _capture(comando, shell=False, timeout=None):
        """Só o stdout, já sem a quebra final."""
        return ArcaneProcess._run(comando, shell, timeout)["stdout"].rstrip("\n")

    @staticmethod
    def _check(comando, shell=False, timeout=None):
        """Roda e devolve yes/no conforme o código de saída."""
        return ArcaneProcess._run(comando, shell, timeout)["ok"]

    @staticmethod
    def _exit_code(comando, shell=False, timeout=None):
        return ArcaneProcess._run(comando, shell, timeout)["exit_code"]

    @staticmethod
    def _spawn(comando, shell=False, cwd=None):
        """Inicia sem esperar. Devolve um identificador para wait/kill."""
        alvo = _normalizar(comando, shell)
        proc = subprocess.Popen(
            alvo, shell=bool(shell), stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, cwd=cwd)
        return {"__type__": "Process", "pid": proc.pid,
                "command": comando, "_handle": proc}

    @staticmethod
    def _wait(processo, timeout=None):
        proc = processo.get("_handle") if isinstance(processo, dict) else processo
        if proc is None:
            raise ValueError("processo inválido")
        try:
            saida, erro = proc.communicate(timeout=timeout)
            return _resultado(proc, saida, erro, processo.get("command", ""))
        except subprocess.TimeoutExpired:
            proc.kill()
            return {"__type__": "ProcessResult", "stdout": "", "stderr": "timeout",
                    "exit_code": -1, "ok": False, "failed": True, "lines": []}

    @staticmethod
    def _kill(processo):
        proc = processo.get("_handle") if isinstance(processo, dict) else processo
        if proc and proc.poll() is None:
            proc.kill()
            return True
        return False

    @staticmethod
    def _terminate(processo):
        proc = processo.get("_handle") if isinstance(processo, dict) else processo
        if proc and proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            return True
        return False

    @staticmethod
    def _is_running(processo):
        proc = processo.get("_handle") if isinstance(processo, dict) else processo
        return bool(proc) and proc.poll() is None

    @staticmethod
    def _pipeline(comandos, timeout=None):
        """Encadeia comandos: a saída de um vira a entrada do próximo."""
        entrada = None
        resultado = None
        for comando in comandos:
            resultado = ArcaneProcess._run(comando, timeout=timeout, input_text=entrada)
            if resultado["failed"]:
                return resultado
            entrada = resultado["stdout"]
        return resultado

    @staticmethod
    def _which(programa):
        import shutil
        return shutil.which(programa)
