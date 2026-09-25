"""Onde mora a documentação de cada coisa.

O hover do editor dizia o que a palavra faz e mostrava um exemplo. O que
faltava era o passo seguinte: **ir ler**. Uma pessoa que para o mouse em
`distill` e quer entender pipelines tinha de sair do editor, abrir o site
e procurar — e quem faz isso três vezes para de fazer.

Aqui ficam os destinos, num lugar só, porque três coisas os usam: o cartão
do hover, o comando *Abrir a documentação do símbolo* e o autocompletar.

**Todo destino é conferido contra as páginas que existem.**
`tests/test_docs_links.py` compara esta tabela com `site/app/docs/`, e é a
única forma de o link não virar 404: a doc vive fora deste módulo e muda
sem avisar. Um link quebrado num hover é pior que nenhum link — ele gasta
a confiança de quem clicou.
"""

URL_BASE = "https://dataforge-lang.vercel.app/docs"


#: Palavra reservada → a página que a explica.
#:
#: Agrupada por assunto, e não uma página por palavra: `given`, `orif` e
#: `otherwise` são o mesmo assunto, e mandar cada uma para um lugar
#: diferente faria a pessoa ler um terço do que precisa.
PAGINA_DE_PALAVRA = {
    # ── Fundamentos e variáveis ──
    "out": "primeiros-passos",
    "steady": "variaveis",
    "shadow": "fundamentos/escopo",
    "static": "variaveis",
    "typeof": "tipos",
    "cast": "tipos",
    "as": "tipos",
    "yes": "tipos",
    "no": "tipos",
    "void": "tipos",
    "inspect": "primeiros-passos",
    "assert": "primeiros-passos",

    # ── Condicionais ──
    "given": "condicionais",
    "orif": "condicionais",
    "otherwise": "condicionais",
    "match": "fundamentos/pattern-matching",
    "point": "fundamentos/pattern-matching",
    "when": "fundamentos/pattern-matching",
    "default": "fundamentos/pattern-matching",

    # ── Laços ──
    "cycle": "lacos",
    "persist": "lacos",
    "perform": "lacos",
    "halt": "lacos",
    "skip": "lacos",
    "from": "lacos",
    "to": "lacos",
    "step": "lacos",
    "in": "lacos",

    # ── Ações ──
    "action": "acoes",
    "yield": "acoes",
    "lambda": "acoes",
    "mark": "fundamentos/decoradores",
    "defer": "acoes",
    "stream": "fundamentos/generators",
    "emit": "fundamentos/generators",
    "async": "tecnicas/concorrencia",
    "await": "tecnicas/concorrencia",

    # ── Objetos ──
    "blueprint": "blueprints",
    "spawn": "blueprints",
    "forge": "blueprints",
    "extends": "oop",
    "trait": "fundamentos/traits",
    "self": "blueprints",
    "root": "oop",
    "record": "fundamentos/records",
    "enum": "fundamentos/enums",
    "with": "fundamentos/records",
    "operator": "oop",
    "slots": "oop",
    "abstract": "oop",
    "final": "oop",
    "private": "oop",
    "protected": "oop",
    "get": "oop",
    "set": "oop",
    "internal": "oop/modificadores",
    "readonly": "oop/modificadores",
    "override": "oop/modificadores",
    "exclusive": "oop/modificadores",
    "lazy": "oop/modificadores",
    "sealed": "oop/modificadores",
    "overload": "oop/sobrecarga",
    "contract": "oop/contratos",
    "invariant": "oop/contratos",
    "expects": "oop/contratos",
    "promises": "oop/contratos",
    "meta": "oop/metaclasses",
    "augment": "oop/augment",

    # ── Erros ──
    "monitor": "erros",
    "handle": "erros",
    "ensure": "erros",
    "trigger": "erros",
    "retry": "erros",
    "guard": "erros",
    "validate": "erros",
    "propagate": "erros",
    "recover": "erros",

    # ── Coleções, pipelines e operadores ──
    "sift": "pipelines",
    "morph": "pipelines",
    "distill": "pipelines",
    "and": "operadores",
    "or": "operadores",
    "not": "operadores",
    "is": "operadores",
    "isnt": "operadores",
    "bigger": "operadores",
    "bigger_eq": "operadores",
    "smaller": "operadores",
    "smaller_eq": "operadores",
    "delete": "colecoes",

    # ── Módulos ──
    "adopt": "pacotes",
    "relay": "pacotes",

    # ── Concorrência ──
    "thread": "tecnicas/concorrencia",
    "parallel": "tecnicas/concorrencia",
    "channel": "tecnicas/concorrencia",
    "wait": "tecnicas/concorrencia",
    "pulse": "tecnicas/concorrencia",
    "observe": "tecnicas/concorrencia",

    # ── Dados ──
    "frame": "lavra",
    "train": "biblioteca/cortex",
    "predict": "biblioteca/cortex",
    "using": "biblioteca/cortex",

    # ── Kiln: as onze do framework web ──
    "server": "kiln",
    "route": "kiln",
    "respond": "kiln",
    "render": "kiln",
    "redirect": "kiln",
    "middleware": "kiln",
    "after": "kiln",
    "mount": "kiln",
    "assets": "kiln",
    "views": "kiln",
    "ignite": "kiln",
}


#: Módulo da stdlib que tem página PRÓPRIA, fora de `biblioteca/`.
#:
#: Kiln e Vitrine são frameworks e têm árvore inteira; Lavra e Crucible
#: também ganharam página de topo. Mandá-los para `biblioteca/kiln` daria
#: 404, e é o tipo de erro que ninguém vê até um usuário clicar.
PAGINA_PROPRIA = {
    "Kiln": "kiln",
    "Arcane.Kiln": "kiln",
    "Arcane.Vitrine": "vitrine",
    "Arcane.Lavra": "lavra",
    "Arcane.Crucible": "crucible",
    "Arcane.Database": "banco-de-dados",
    "Arcane.Forge": "orm",
}


def pagina_de_palavra(palavra):
    """A página de uma palavra reservada, ou `None`."""
    return PAGINA_DE_PALAVRA.get(palavra)


def pagina_de_modulo(oficial):
    """A página de um módulo da stdlib.

    Cai no índice da biblioteca quando o módulo não tem página própria —
    19 dos 47 não têm, e um índice é um destino honesto. Inventar
    `biblioteca/malha` porque o padrão *parece* certo daria 404.
    """
    if oficial in PAGINA_PROPRIA:
        return PAGINA_PROPRIA[oficial]
    curto = oficial.split(".")[-1].lower()
    return f"biblioteca/{curto}" if curto in MODULOS_COM_PAGINA else "biblioteca"


#: Os módulos que têm `site/app/docs/biblioteca/<x>/page.tsx`.
#:
#: Escrita à mão de propósito: o LSP roda a partir do wheel instalado, e
#: ali não há pasta `site/`. O teste é que garante que ela não envelhece.
MODULOS_COM_PAGINA = frozenset({
    "abi", "algoritmos", "alvo", "analytics", "api", "archive", "async", "bench",
    "bigorna", "brasa", "bytes", "c", "capacidade", "chaves", "cli", "collections", "color",
    "compilador", "concurrent", "cortex", "crucible", "crypto", "data",
    "database", "deteccao", "decimal", "dominio", "dsl", "ecossistema", "email",
    "estrutura", "eventos", "evolucao", "excel", "forge", "functional", "html", "http",
    "inicio", "injecao", "io", "iot", "iter", "janela", "laco", "lago", "lavra", "logging",
    "macro", "malha", "math", "memoria", "meta", "objetos", "observar",
    "os", "padroes", "percurso", "perfil", "pipeline", "politica", "ponte", "posse",
    "principios", "process", "quadro", "qualidade", "reativo", "seguranca", "rede",
    "github", "gramatica", "integridade", "privacidade",
    "reflexo", "regex", "resultado", "serialization", "stm", "stream",
    "telegram", "test", "text", "time", "tipos", "url", "web",
})


def pagina_de_comando(comando):
    """A página de um comando da CLI (`check`, `fmt`, `test`…).

    Vários comandos dividem uma página (`dap` e `lsp` moram em `debug`;
    `stats`, `oop` e `big-o` em `analise`). Sem o mapa, o hover do editor
    sobre `dataforge dap` mandava para o índice da CLI.
    """
    comando = _COMANDO_NA_PAGINA.get(comando, comando)
    return f"cli/{comando}" if comando in COMANDOS_COM_PAGINA else "cli"


#: Comando -> a página onde ele é explicado, quando não é a dele.
_COMANDO_NA_PAGINA = {
    "dap": "debug", "lsp": "debug", "info": "new",
    "stats": "analise", "oop": "analise", "big-o": "analise",
    "custo": "analise", "deps": "analise", "fix": "profile",
    "tokens": "internos", "ast": "internos", "ir": "internos",
    "percurso": "internos", "alvo": "abi", "eval": "scripts",
    "version": "scripts", "converter": "scripts",
    "versions": "versoes", "use": "versoes", "upgrade": "versoes",
    "clean": "cache",
}


#: Os comandos que têm `site/app/docs/cli/<x>/page.tsx`.
COMANDOS_COM_PAGINA = frozenset({
    "abi", "analise", "bench", "cache", "check", "completar", "crucible",
    "debug", "doc", "editor", "explain", "fmt", "forge-toml", "init",
    "internos", "lint", "new", "pacotes", "profile", "referencia", "repl",
    "run", "scripts", "seguranca", "test", "versoes", "watch", "workspace",
})


def url(pagina):
    """O endereço completo de uma página."""
    return f"{URL_BASE}/{pagina.lstrip('/')}" if pagina else URL_BASE


def link_markdown(pagina, rotulo="ler a documentação"):
    """O link do cartão de hover. Vazio quando não há destino."""
    if not pagina:
        return ""
    return f"[{rotulo}]({url(pagina)})"
