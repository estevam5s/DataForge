"""
DataForge Doc Generator — `dataforge doc`

Extrai a documentação de um arquivo ou pasta `.df` e gera Markdown: ações,
blueprints, records, enums, traits e constantes, com seus comentários.

Convenção: o comentário imediatamente acima de uma declaração é a sua
documentação. Linhas começando com `//` ou `#` valem.
"""

import os

from . import ast_nodes as ast
from .lexer import tokenize
from .parser import parse


def _comentarios_por_linha(fonte):
    """Mapeia número de linha → texto do comentário daquela linha."""
    mapa = {}
    for numero, linha in enumerate(fonte.split("\n"), start=1):
        nua = linha.strip()
        if nua.startswith("//"):
            mapa[numero] = nua[2:].strip()
        elif nua.startswith("#"):
            mapa[numero] = nua[1:].strip()
    return mapa


def _doc_de(node, comentarios):
    """Junta o bloco de comentários logo acima da declaração."""
    linha = getattr(node, 'line', 0) - 1
    partes = []
    while linha in comentarios:
        partes.append(comentarios[linha])
        linha -= 1
    return "\n".join(reversed(partes)).strip()


def _assinatura_acao(node):
    partes = []
    for param in node.params:
        tipo = (getattr(node, 'param_types', {}) or {}).get(param)
        texto = f"{param}: {tipo}" if tipo else param
        if param in (node.defaults or {}):
            texto += " := …"
        partes.append(texto)
    prefixo = "stream action" if getattr(node, 'is_generator', False) else (
        "async action" if node.is_async else "action")
    retorno = getattr(node, 'return_type', '')
    sufixo = f" -> {retorno}" if retorno else ""
    return f"{prefixo} {node.name}({', '.join(partes)}){sufixo}"


class DocGenerator:
    """Gera Markdown a partir das declarações de um arquivo."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.fonte = open(caminho, encoding="utf-8").read()
        self.comentarios = _comentarios_por_linha(self.fonte)
        self.arvore = parse(tokenize(self.fonte, caminho), caminho)

    def gerar(self, nivel_titulo=1):
        h = "#" * nivel_titulo
        nome = os.path.basename(self.caminho)
        linhas = [f"{h} `{nome}`", ""]

        cabecalho = self._cabecalho_do_arquivo()
        if cabecalho:
            linhas += [cabecalho, ""]

        secoes = {
            "Constantes": self._constantes(),
            "Records": self._records(h),
            "Enums": self._enums(h),
            "Traits": self._traits(h),
            "Blueprints": self._blueprints(h),
            "Ações": self._acoes(h),
        }
        for titulo, conteudo in secoes.items():
            if conteudo:
                linhas += [f"{h}# {titulo}", ""] + conteudo + [""]
        return "\n".join(linhas).rstrip() + "\n"

    def _cabecalho_do_arquivo(self):
        """Comentários do topo do arquivo, antes de qualquer código."""
        partes = []
        for numero in range(1, 40):
            if numero in self.comentarios:
                partes.append(self.comentarios[numero])
            elif self.fonte.split("\n")[numero - 1:numero] == [""]:
                if partes:
                    break
            else:
                break
        return " ".join(partes).strip()

    def _constantes(self):
        linhas = []
        for stmt in self.arvore.body:
            if isinstance(stmt, ast.SteadyDeclaration):
                doc = _doc_de(stmt, self.comentarios)
                linhas.append(f"- **`{stmt.name}`**" + (f" — {doc}" if doc else ""))
        return linhas

    def _acoes(self, h, corpo=None, prefixo=""):
        linhas = []
        for stmt in (corpo if corpo is not None else self.arvore.body):
            if not isinstance(stmt, ast.ActionDeclaration):
                continue
            doc = _doc_de(stmt, self.comentarios)
            linhas.append(f"{h}## `{prefixo}{stmt.name}`")
            linhas.append("")
            linhas.append("```dataforge")
            linhas.append(_assinatura_acao(stmt))
            linhas.append("```")
            if doc:
                linhas += ["", doc]
            linhas.append("")
        return linhas

    def _records(self, h):
        linhas = []
        for stmt in self.arvore.body:
            if not isinstance(stmt, ast.RecordDeclaration):
                continue
            doc = _doc_de(stmt, self.comentarios)
            linhas.append(f"{h}## `{stmt.name}`")
            linhas.append("")
            if doc:
                linhas += [doc, ""]
            linhas.append("| Campo | Tipo | Padrão |")
            linhas.append("|-------|------|--------|")
            for campo, tipo, padrao in stmt.fields:
                linhas.append(f"| `{campo}` | `{tipo}` | "
                              f"{'sim' if padrao is not None else '—'} |")
            if stmt.methods:
                linhas += ["", "Métodos: " + ", ".join(
                    f"`{m}`" for m in stmt.methods)]
            linhas.append("")
        return linhas

    def _enums(self, h):
        linhas = []
        for stmt in self.arvore.body:
            if not isinstance(stmt, ast.EnumDeclaration):
                continue
            doc = _doc_de(stmt, self.comentarios)
            linhas.append(f"{h}## `{stmt.name}`")
            linhas.append("")
            if doc:
                linhas += [doc, ""]
            linhas.append("Membros: " + ", ".join(
                f"`{m}`" for m, _ in stmt.members))
            linhas.append("")
        return linhas

    def _traits(self, h):
        linhas = []
        for stmt in self.arvore.body:
            if not isinstance(stmt, ast.TraitDeclaration):
                continue
            doc = _doc_de(stmt, self.comentarios)
            linhas.append(f"{h}## `{stmt.name}` (trait)")
            linhas.append("")
            if doc:
                linhas += [doc, ""]
            for metodo in stmt.methods:
                if isinstance(metodo, ast.ActionDeclaration):
                    linhas.append(f"- `{_assinatura_acao(metodo)}`")
            linhas.append("")
        return linhas

    def _blueprints(self, h):
        linhas = []
        for stmt in self.arvore.body:
            if not isinstance(stmt, ast.BlueprintDeclaration):
                continue
            doc = _doc_de(stmt, self.comentarios)
            heranca = ""
            if stmt.parents:
                heranca += " extends " + ", ".join(stmt.parents)
            if getattr(stmt, 'traits', None):
                heranca += " with " + ", ".join(stmt.traits)
            params = f"({', '.join(stmt.constructor_params)})" if stmt.constructor_params else ""
            linhas.append(f"{h}## `{stmt.name}{params}{heranca}`")
            linhas.append("")
            if doc:
                linhas += [doc, ""]
            metodos = [s for s in stmt.body if isinstance(s, ast.ActionDeclaration)]
            if metodos:
                for metodo in metodos:
                    md = _doc_de(metodo, self.comentarios)
                    linhas.append(f"- `{_assinatura_acao(metodo)}`"
                                  + (f" — {md.splitlines()[0]}" if md else ""))
                linhas.append("")
        return linhas


def gerar_doc(caminho, nivel_titulo=1):
    """Gera o Markdown de um único arquivo."""
    return DocGenerator(caminho).gerar(nivel_titulo)


def gerar_doc_pasta(pasta, titulo="Documentação"):
    """Gera um Markdown único para todos os .df de uma pasta."""
    import glob
    arquivos = sorted(glob.glob(os.path.join(pasta, "**", "*.df"), recursive=True))
    partes = [f"# {titulo}", "",
              f"Gerado a partir de {len(arquivos)} arquivo(s) em `{pasta}`.", ""]
    for arquivo in arquivos:
        try:
            partes.append(gerar_doc(arquivo, nivel_titulo=2))
        except Exception as e:
            partes.append(f"## `{os.path.basename(arquivo)}`\n\n"
                          f"> Não consegui analisar: {e}\n")
    return "\n".join(partes)
