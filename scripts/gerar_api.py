#!/usr/bin/env python3
"""
Gera a API pública da linguagem, em JSON estático.

    python3 scripts/gerar_api.py

Escreve site/public/api/*.json. O site é exportado estático, então não
há rota de servidor — mas um JSON servido por URL fixa é uma API tão
consumível quanto qualquer outra, e nunca sai do ar.

Tudo aqui é lido do próprio código: palavras reservadas de tokens.py,
funções de builtins.py, módulos da stdlib, comandos do cli.py. Escrever
à mão garantiria que um dia a API descreveria uma linguagem que não
existe mais.
"""

import inspect
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import __version__                                # noqa: E402
from dataforge.builtins import get_builtins                      # noqa: E402
from dataforge.cli import GRUPOS                                 # noqa: E402
from dataforge.diagnosticos import CATALOGO                      # noqa: E402
from dataforge.stdlib import get_module, list_modules            # noqa: E402
from dataforge.tokens import (                                   # noqa: E402
    CONTEXTUAIS_BLUEPRINT, CONTEXTUAIS_KILN, KEYWORDS, VERBOS_KILN,
)

SAIDA = os.path.join(RAIZ, "site", "public", "api")

#: O que cada palavra reservada faz, e o equivalente em outra linguagem.
#: É a única parte escrita à mão — o significado de uma palavra não está
#: no código, está na cabeça de quem a escolheu.
SIGNIFICADOS = {
    "steady": ("declara um valor que nunca muda", "const"),
    "out": ("imprime", "print"),
    "in": ("pertence a", "in"),
    "typeof": ("o tipo de um valor", "typeof"),
    "shadow": ("declara sobrepondo o escopo de fora", "let (com shadowing)"),
    "given": ("condicional", "if"),
    "orif": ("condição seguinte", "elif / else if"),
    "otherwise": ("caso contrário", "else"),
    "match": ("casamento de padrão", "match / switch"),
    "point": ("um caso do match", "case"),
    "default": ("o caso que sobra", "default"),
    "when": ("guarda de um padrão", "if (em case)"),
    "is": ("igual a", "=="),
    "isnt": ("diferente de", "!="),
    "bigger": ("maior que", ">"),
    "smaller": ("menor que", "<"),
    "bigger_eq": ("maior ou igual", ">="),
    "smaller_eq": ("menor ou igual", "<="),
    "and": ("e lógico", "and / &&"),
    "or": ("ou lógico", "or / ||"),
    "not": ("negação", "not / !"),
    "cycle": ("laço sobre faixa ou coleção", "for"),
    "persist": ("laço enquanto", "while"),
    "perform": ("laço que roda ao menos uma vez", "do…while"),
    "halt": ("interrompe o laço", "break"),
    "skip": ("pula para a próxima volta", "continue"),
    "from": ("início da faixa", "range(start, …)"),
    "to": ("fim da faixa, inclusivo", "range(…, stop)"),
    "step": ("passo da faixa", "range(…, step)"),
    "action": ("declara uma função", "def / function"),
    "yield": ("devolve e encerra a ação", "return"),
    "blueprint": ("declara uma classe", "class"),
    "spawn": ("instancia", "new"),
    "self": ("a própria instância", "self / this"),
    "root": ("a implementação da classe pai", "super"),
    "adopt": ("importa", "import"),
    "relay": ("exporta", "export"),
    "trait": ("declara uma interface", "interface / protocol"),
    "static": ("membro da classe, não da instância", "static"),
    "monitor": ("bloco que pode falhar", "try"),
    "handle": ("trata a falha", "catch / except"),
    "ensure": ("roda sempre, falhando ou não", "finally"),
    "trigger": ("lança um erro", "throw / raise"),
    "retry": ("bloco que tenta de novo", "—"),
    "recover": ("recuperação de um retry", "—"),
    "guard": ("pré-condição que encerra cedo", "guard"),
    "propagate": ("relança o erro atual", "raise"),
    "validate": ("verifica e falha com mensagem", "assert"),
    "async": ("ação assíncrona", "async"),
    "await": ("espera o resultado", "await"),
    "thread": ("bloco em outra thread", "Thread"),
    "channel": ("fila entre threads", "Queue / channel"),
    "pulse": ("emite um evento", "emit"),
    "observe": ("assina um fluxo", "subscribe"),
    "stream": ("gerador preguiçoso (com action)", "function*"),
    "defer": ("adia até o fim do escopo", "defer"),
    "parallel": ("roda instruções em paralelo", "—"),
    "mark": ("decorador", "@decorator"),
    "frame": ("marcador de DataFrame", "—"),
    "sift": ("filtra, num pipeline", "filter"),
    "morph": ("transforma, num pipeline", "map"),
    "distill": ("reduz, num pipeline", "reduce"),
    "train": ("marcador de treino de modelo", "—"),
    "predict": ("marcador de inferência", "—"),
    "using": ("contexto gerenciado", "with"),
    "with": ("cópia com alterações; traits", "dataclasses.replace"),
    "extends": ("herda de", "extends"),
    "as": ("apelida no import ou no padrão", "as"),
    "wait": ("dorme", "sleep"),
    "emit": ("produz um valor no gerador", "yield"),
    "forge": ("cria/constrói", "—"),
    "cast": ("converte de tipo", "as / cast"),
    "lambda": ("função anônima", "lambda / =>"),
    "record": ("dado imutável com igualdade estrutural", "@dataclass(frozen)"),
    "enum": ("enumeração", "enum"),
    "inspect": ("depura mostrando valor e tipo", "console.debug"),
    "assert": ("afirma uma condição", "assert"),
    "delete": ("remove uma chave ou item", "del"),
    "void": ("ausência de valor", "null / None"),
    "yes": ("verdadeiro", "true"),
    "no": ("falso", "false"),
}

SIGNIFICADOS_CONTEXTUAIS = {
    "get": ("abre uma propriedade de leitura", "@property"),
    "set": ("abre uma propriedade de escrita", "@x.setter"),
    "private": ("visível só dentro do blueprint", "private"),
    "protected": ("visível no blueprint e nos herdeiros", "protected"),
    "operator": ("sobrecarrega um operador", "__add__ / operator+"),
    "final": ("não pode ser sobrescrito", "final"),
    "slots": ("os únicos campos que a instância pode ter; economiza memória",
              "slots"),
    "abstract": ("sem implementação; obriga o herdeiro", "abstract"),
    "server": ("declara uma aplicação web", "Flask() / express()"),
    "route": ("declara uma rota", "@app.route"),
    "respond": ("responde e encerra a rota", "return jsonify(…)"),
    "render": ("renderiza um template", "render_template"),
    "redirect": ("redireciona", "redirect"),
    "middleware": ("roda antes de toda rota", "app.use"),
    "after": ("roda depois, com a resposta na mão", "app.apos"),
    "mount": ("monta outra aplicação sob um prefixo", "app.mount"),
    "assets": ("serve arquivos estáticos", "static_folder"),
    "views": ("pasta dos templates", "template_folder"),
    "ignite": ("sobe o servidor", "app.run() / listen()"),
}

OPERADORES = [
    (":=", "atribuição", "="),
    ("steady x :=", "constante", "const x ="),
    ("+ - * /", "aritmética", "iguais"),
    ("~/", "divisão inteira", "//"),
    ("**", "potência", "**"),
    ("%", "resto", "%"),
    ("+= -= *= /= %=", "atribuição composta", "iguais"),
    ("is / isnt", "igualdade", "== / !="),
    ("bigger / smaller", "comparação", "> / <"),
    ("and / or / not", "lógica", "and / or / not"),
    ("??", "valor padrão quando void", "?? / or"),
    ("?.", "acesso seguro", "?."),
    ("...", "spread e rest", "..."),
    (">> sift / morph / distill", "pipeline", "filter / map / reduce"),
    ("$\"{expr}\"", "interpolação", "f\"\" / `${}`"),
    ("->", "tipo de retorno", "-> / :"),
    ("=>", "corpo de lambda", "=>"),
    ("//", "comentário (divisão só antes de dígito)", "// ou #"),
    ("[a:b:c]", "fatiamento", "[a:b:c]"),
]


def sintaxe():
    reservadas = []
    for palavra in sorted(KEYWORDS):
        descricao, equivalente = SIGNIFICADOS.get(palavra, ("", ""))
        reservadas.append({
            "palavra": palavra,
            "descricao": descricao,
            "equivalente": equivalente,
        })

    contextuais = []
    for palavra in sorted(set(CONTEXTUAIS_BLUEPRINT) | set(CONTEXTUAIS_KILN)):
        descricao, equivalente = SIGNIFICADOS_CONTEXTUAIS.get(palavra, ("", ""))
        contextuais.append({
            "palavra": palavra,
            "descricao": descricao,
            "equivalente": equivalente,
            "onde": ("bloco server" if palavra in CONTEXTUAIS_KILN
                     else "corpo de blueprint"),
        })

    return {
        "versao": __version__,
        "extensao": ".df",
        "reservadas": reservadas,
        "contextuais": contextuais,
        "operadores": [{"simbolo": s, "descricao": d, "equivalente": e}
                       for s, d, e in OPERADORES],
        "verbos_http": list(VERBOS_KILN),
        "regras": [
            "A indentação é de 4 espaços. Tab é erro de sintaxe.",
            "'//' é comentário; vira divisão inteira só antes de dígito, "
            "'(' ou chamada. Para dividir sempre, use '~/'.",
            "'yield' encerra a ação; 'emit' produz num 'stream action'.",
            "'cycle x from a to b' é inclusivo nos dois extremos.",
            "Records são imutáveis: use 'p with {\"campo\": valor}'.",
            "Dentro de $\"{…}\", as aspas são normais, não escapadas.",
        ],
    }


def embutidas():
    nomes = sorted(get_builtins())
    return {
        "versao": __version__,
        "total": len(nomes),
        "funcoes": nomes,
    }


def modulos():
    saida = []
    vistos = {}
    for nome in sorted(set(list_modules())):
        modulo = get_module(nome)
        canonico = modulo.get("__name__", nome)
        if canonico in vistos:
            vistos[canonico]["apelidos"].append(nome)
            continue

        simbolos = []
        for chave, valor in sorted(modulo.items()):
            if chave == "__name__":
                continue
            try:
                assinatura = str(inspect.signature(valor))
            except (TypeError, ValueError):
                assinatura = ""
            resumo = (inspect.getdoc(valor) or "").split("\n")[0]
            simbolos.append({"nome": chave, "assinatura": assinatura,
                             "resumo": resumo})

        entrada = {
            "nome": canonico,
            "apelidos": [nome] if nome != canonico else [],
            "total": len(simbolos),
            "simbolos": simbolos,
        }
        vistos[canonico] = entrada
        saida.append(entrada)

    return {
        "versao": __version__,
        "total_modulos": len(saida),
        "total_simbolos": sum(m["total"] for m in saida),
        "modulos": sorted(saida, key=lambda m: -m["total"]),
    }


def comandos():
    grupos = []
    for titulo, cmds in GRUPOS:
        grupos.append({
            "grupo": titulo,
            "comandos": [{
                "nome": c.nome,
                "uso": c.uso,
                "resumo": c.resumo,
                "detalhe": c.detalhe,
                "opcoes": [{"flag": f, "descricao": d} for f, d in c.opcoes],
                "exemplos": [{"comando": cmd, "nota": nota}
                             for cmd, nota in c.exemplos],
                "apelidos": list(c.apelidos),
                "veja": list(c.veja),
            } for c in cmds],
        })
    return {
        "versao": __version__,
        "total": sum(len(g["comandos"]) for g in grupos),
        "grupos": grupos,
    }


def erros():
    return {
        "versao": __version__,
        "total": len(CATALOGO),
        "codigos": [{
            "codigo": codigo,
            "titulo": info["titulo"],
            "explicacao": info["explicacao"],
            "exemplo": info.get("exemplo", ""),
            "solucao": info.get("solucao", ""),
            "doc": info.get("doc", ""),
        } for codigo, info in sorted(CATALOGO.items())],
    }


def conteudos():
    """Índice do que existe para aprender, com contagens reais."""
    import glob

    exercicios = {}
    base = os.path.join(RAIZ, "exercicios")
    for pasta in sorted(os.listdir(base)):
        caminho = os.path.join(base, pasta)
        if not os.path.isdir(caminho):
            continue
        arquivos = [a for a in os.listdir(caminho) if a.endswith(".df")]
        if arquivos:
            exercicios[pasta] = len(arquivos)

    return {
        "versao": __version__,
        "exercicios": {
            "modulos": exercicios,
            "total": sum(exercicios.values()),
        },
        "exemplos": len(glob.glob(os.path.join(RAIZ, "examples", "*.df"))),
        "pacotes": len(glob.glob(os.path.join(RAIZ, "packages", "*", "forge.toml"))),
        "projetos": len(glob.glob(os.path.join(RAIZ, "projetos", "*", "forge.toml"))),
    }


def main():
    os.makedirs(SAIDA, exist_ok=True)

    partes = {
        "sintaxe": sintaxe(),
        "embutidas": embutidas(),
        "modulos": modulos(),
        "comandos": comandos(),
        "erros": erros(),
        "conteudos": conteudos(),
    }

    indice = {
        "nome": "DataForge",
        "versao": __version__,
        "descricao": "API pública da linguagem: sintaxe, biblioteca, "
                     "comandos e conteúdos. Tudo gerado do código-fonte.",
        "documentacao": "https://dataforge-lang.vercel.app/docs",
        "rotas": {},
    }

    for nome, dados in partes.items():
        caminho = os.path.join(SAIDA, f"{nome}.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, separators=(",", ":"))
        tamanho = os.path.getsize(caminho)
        indice["rotas"][nome] = f"/api/{nome}.json"
        print(f"  /api/{nome}.json  {tamanho / 1024:>7.1f} KB")

    with open(os.path.join(SAIDA, "index.json"), "w", encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, indent=2)
    print(f"  /api/index.json")


if __name__ == "__main__":
    main()
