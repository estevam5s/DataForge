"""
DataForge Environment (Scope Manager)
Manages variable scopes, constants, and name resolution.
"""

from .errors import NameError_, RuntimeError_


class Environment:
    """A scope environment for variable/function lookups."""

    def __init__(self, parent=None, name: str = "<global>"):
        self.parent = parent
        self.name = name
        self.variables: dict = {}
        self.constants: set = set()  # Names that are immutable (steady)

    def get(self, name: str):
        """Look up a variable, walking up the scope chain."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise self._erro_de_nome(name)

    # ── Diagnostico ──────────────────────────────────────────

    def nomes_visiveis(self):
        """Tudo o que este escopo enxerga, do mais proximo ao mais distante."""
        vistos, escopo = [], self
        while escopo is not None:
            for nome in escopo.variables:
                if not nome.startswith('__') and nome not in vistos:
                    vistos.append(nome)
            escopo = escopo.parent
        return vistos

    def _erro_de_nome(self, name):
        """'x nao existe' e pouco. Sugerir o parecido resolve a maioria."""
        import difflib

        visiveis = self.nomes_visiveis()
        perto = difflib.get_close_matches(name, visiveis, n=3, cutoff=0.7)

        nota = dica = ""
        if perto:
            if len(perto) == 1:
                dica = f"did you mean '{perto[0]}'?"
            else:
                opcoes = ", ".join(f"'{p}'" for p in perto)
                dica = f"did you mean one of: {opcoes}?"
        else:
            # Escrito depois de usado? Ou so nao existe mesmo?
            nota = "this name was never assigned in any enclosing scope"
            dica = ("assign it before using:  "
                    f"{name} := …\n"
                    "remember DataForge assigns with ':=', not '='")

        return NameError_(f"'{name}' is not defined.",
                          nota=nota, dica=dica, doc="variaveis",
                          rotulo="used here")

    def set(self, name: str, value):
        """Set a variable in the current scope."""
        if name in self.constants:
            raise RuntimeError_(
                f"'{name}' is steady and cannot be reassigned.",
                nota="'steady' declares a value that never changes",
                dica=(f"use a different name for the new value, or declare "
                      f"'{name}' with ':=' instead of 'steady' if it does "
                      f"need to change"),
                doc="variaveis")

        # Walk up to find existing variable to update
        env = self
        while env is not None:
            if name in env.variables:
                if name in env.constants:
                    raise RuntimeError_(
                        f"'{name}' is steady and cannot be reassigned.",
                        nota="'steady' declares a value that never changes",
                        dica=(f"pick another name, or declare '{name}' with "
                              f"':=' if it needs to change"),
                        doc="variaveis")
                env.variables[name] = value
                return
            env = env.parent

        # New variable in current scope
        self.variables[name] = value

    def set_local(self, name: str, value):
        """Define/set a variable strictly in the current scope."""
        if name in self.constants:
            raise RuntimeError_(f"Cannot reassign steady (constant) '{name}'")
        self.variables[name] = value

    def define_steady(self, name: str, value):
        """Define an immutable constant."""
        if name in self.constants:
            raise RuntimeError_(f"Cannot reassign steady (constant) '{name}'")
        self.variables[name] = value
        self.constants.add(name)

    def define_shadow(self, name: str, value):
        """Define a local shadow variable that overrides parent scope."""
        self.variables[name] = value

    def has(self, name: str) -> bool:
        """Check if a name exists in any scope."""
        if name in self.variables:
            return True
        if self.parent:
            return self.parent.has(name)
        return False

    def has_local(self, name: str) -> bool:
        """Check if a name exists in the current scope only."""
        return name in self.variables

    def delete(self, name: str):
        """Remove a variable from the current or parent scope."""
        if name in self.constants:
            raise RuntimeError_(f"Cannot delete steady (constant) '{name}'")
        if name in self.variables:
            del self.variables[name]
            return
        if self.parent:
            self.parent.delete(name)
            return
        raise NameError_(f"Cannot delete undefined name: '{name}'")

    def child(self, name: str = "<block>"):
        """Create a child scope."""
        return Environment(parent=self, name=name)

    def __repr__(self):
        keys = list(self.variables.keys())
        return f"Environment({self.name}, vars={keys})"
