"""
Arcane.IO - File & System Operations
"""

import os
import json
import csv


class ArcaneIO:
    """File I/O and system operations module."""

    def __new__(cls):
        return {
            "__name__": "Arcane.IO",
            "open": cls._open,
            "read": cls._read,
            "write": cls._write,
            "append": cls._append,
            "exists": cls._exists,
            "delete": cls._delete,
            "mkdir": cls._mkdir,
            "rmdir": cls._rmdir,
            "remove_tree": cls._remove_tree,
            "copy_tree": cls._copy_tree,
            "listdir": cls._listdir,
            "path": cls._path,
            "join": cls._join,
            "basename": cls._basename,
            "dirname": cls._dirname,
            "ext": cls._ext,
            "abs": cls._abs,
            "cwd": cls._cwd,
            "shell": cls._shell,
            "read_json": cls._read_json,
            "write_json": cls._write_json,
            "read_csv": cls._read_csv,
            "write_csv": cls._write_csv,
            "size": cls._size,
            "rename": cls._rename,
            "copy": cls._copy,
            # Aliases
            "read_file": cls._read,
            "write_file": cls._write,
            "file_exists": cls._exists,
            "list_dir": cls._listdir,
        }

    @staticmethod
    def _open(path, mode="r"):
        return open(path, mode, encoding="utf-8")

    @staticmethod
    def _read(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _write(path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(content))

    @staticmethod
    def _append(path, content):
        with open(path, "a", encoding="utf-8") as f:
            f.write(str(content))

    @staticmethod
    def _exists(path):
        return os.path.exists(path)

    @staticmethod
    def _delete(path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            os.rmdir(path)

    @staticmethod
    def _mkdir(path):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def _rmdir(path):
        """Remove uma pasta VAZIA. Devolve 'no' se ela nao estava vazia.

        Separado de 'remove_tree' de proposito: apagar uma pasta que se
        acredita vazia e uma operacao segura, e a mesma chamada apagando
        uma arvore inteira por engano nao e. Quem quer a arvore pede a
        arvore.
        """
        try:
            os.rmdir(path)
            return True
        except OSError:
            return False

    @staticmethod
    def _remove_tree(path):
        """Remove uma pasta e tudo dentro dela.

        Recusa um LINK SIMBOLICO para pasta: seguir o link apagaria o
        alvo, que pode estar em qualquer lugar do disco. A remocao anda
        so dentro do que ela recebeu.
        """
        import shutil

        if not os.path.exists(path):
            return False
        if os.path.islink(path):
            from ..errors import RuntimeError_
            raise RuntimeError_(
                f"'{path}' e um link simbolico, nao uma pasta.", 0, 0,
                nota="apagar seguindo o link removeria o alvo, que pode "
                     "estar em qualquer lugar",
                dica="use IO.delete para remover o link em si",
                doc="tecnicas/arquivos")
        if not os.path.isdir(path):
            from ..errors import RuntimeError_
            raise RuntimeError_(
                f"'{path}' nao e uma pasta.", 0, 0,
                dica="use IO.delete para um arquivo",
                doc="tecnicas/arquivos")
        shutil.rmtree(path)
        return True

    @staticmethod
    def _copy_tree(origem, destino):
        """Copia uma pasta inteira. Junta com o que ja existe no destino."""
        import shutil

        shutil.copytree(origem, destino, dirs_exist_ok=True,
                        symlinks=True)
        return destino

    @staticmethod
    def _listdir(path="."):
        return os.listdir(path)

    @staticmethod
    def _path(path):
        return os.path.normpath(path)

    @staticmethod
    def _join(*parts):
        return os.path.join(*parts)

    @staticmethod
    def _basename(path):
        return os.path.basename(path)

    @staticmethod
    def _dirname(path):
        return os.path.dirname(path)

    @staticmethod
    def _ext(path):
        return os.path.splitext(path)[1]

    @staticmethod
    def _abs(path):
        return os.path.abspath(path)

    @staticmethod
    def _cwd():
        return os.getcwd()

    @staticmethod
    def _shell(command):
        return os.popen(command).read().strip()

    @staticmethod
    def _read_json(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _write_json(path, data, indent=2):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

    @staticmethod
    def _read_csv(path):
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            return [row for row in reader]

    @staticmethod
    def _write_csv(path, data):
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(data)

    @staticmethod
    def _size(path):
        return os.path.getsize(path)

    @staticmethod
    def _rename(old, new):
        os.rename(old, new)

    @staticmethod
    def _copy(src, dst):
        import shutil
        shutil.copy2(src, dst)
