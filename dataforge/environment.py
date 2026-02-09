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
        raise NameError_(f"Undefined name: '{name}'")

    def set(self, name: str, value):
        """Set a variable in the current scope."""
        if name in self.constants:
            raise RuntimeError_(f"Cannot reassign steady (constant) '{name}'")

        # Walk up to find existing variable to update
        env = self
        while env is not None:
            if name in env.variables:
                if name in env.constants:
                    raise RuntimeError_(f"Cannot reassign steady (constant) '{name}'")
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
