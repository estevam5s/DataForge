#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o llms.txt — a linguagem explicada para um modelo de linguagem.

Por que este arquivo existe
---------------------------
Quem escreve DataForge hoje quase sempre tem um modelo ao lado. E um
modelo que nunca viu esta linguagem faz o que qualquer um faria: chuta
a sintaxe de Python. O resultado e codigo que nao compila, e a culpa
parece da linguagem.

O 'llms.txt' e a convencao para isso — um arquivo na raiz do site com o
essencial em texto, para o modelo ler antes de responder.

Duas decisoes
-------------
1. **Ele e GERADO.** As 81 palavras reservadas, os 63 modulos e as 228
   embutidas saem do codigo que o interpretador executa. Um arquivo
   escrito a mao envelheceria na primeira palavra nova — e um resumo
   errado e pior que nenhum, porque o modelo confia nele.

2. **As ARMADILHAS vem antes da lista de simbolos.** O que faz um
   modelo errar aqui nao e nao saber que existe 'Arcane.Excel': e
   escrever '//' achando que e divisao, ou 'yield' achando que e
   'emit'. O arquivo comeca pelo que mais custa.

    python3 scripts/gerar_llms.py
    python3 scripts/gerar_llms.py --check
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import marca                                  # noqa: E402

marca.preparar_saida()

DESTINOS = (
    os.path.join(RAIZ, "llms.txt"),
    os.path.join(RAIZ, "site", "public", "llms.txt"),
)

SITE = "https://dataforge-lang.vercel.app"


def _linguagem():
    from dataforge import __version__
    from dataforge.builtins import get_builtins
    from dataforge.stdlib import get_module, list_modules
    from dataforge.stdlib.catalogo import DESCRICOES
    from dataforge.tokens import KEYWORDS

    modulos = sorted({get_module(n)["__name__"] for n in set(list_modules())})
    return {
        "versao": __version__,
        "palavras": sorted(KEYWORDS),
        "embutidas": sorted(get_builtins()),
        "modulos": [
            (m, DESCRICOES.get(m, ("", ""))[0].split(".")[0] + ".",
             len([k for k in get_module(m) if not k.startswith("__")]))
            for m in modulos
        ],
    }


TRADUCAO = [
    ("=", ":="), ("const", "steady"), ("print", "out"),
    ("f-string", '$"texto {expr}"'), ("if/elif/else", "given/orif/otherwise"),
    ("ternario", "a given cond otherwise b"),
    ("switch/match", "match / point / when / default"),
    ("for", "cycle x from a to b  ·  cycle x in colecao"),
    ("while", "persist"), ("do..while", "perform … persist"),
    ("break/continue", "halt/skip"), ("def/return", "action/yield"),
    ("generator", "stream action / emit"), ("class/new", "blueprint/spawn"),
    ("@dataclass(frozen)", "record"), ("enum", "enum"),
    ("self/super", "self/root"), ("interface", "trait"),
    ("import/export", "adopt/relay"),
    ("chamar Python", "adopt Python.numpy as np"),
    ("try/catch/finally", "monitor/handle/ensure"), ("throw", "trigger"),
    ("true/false/null", "yes/no/void"),
    ("list comprehension", "[expr cycle x in fonte given cond]"),
    ("filter/map/reduce", ">> sift  ·  >> morph  ·  >> distill"),
    ("lambda", "lambda x: expr  ·  lambda a, b => expr"),
    ("decorator", "mark @nome"),
    ("// (divisao inteira)", "~/   ← '//' e COMENTARIO"),
]

ARMADILHAS = [
    ("`//` e COMENTARIO, nao divisao inteira",
     "Use `~/` para dividir. `//` so vira divisao quando seguido de "
     "digito, `(` ou chamada — e depender disso torna o codigo fragil. "
     "Vale nos dois sentidos: um comentario de fim de linha que comeca "
     "com uma chamada vira divisao."),
    ("`yield` DEVOLVE e encerra; `emit` PRODUZ e continua",
     "Para uma sequencia, use `stream action` + `emit`. `yield` dentro "
     "de uma acao comum e o `return`."),
    ("So espacos na indentacao",
     "Tab e erro (`SyncError`). Quatro espacos por nivel."),
    ("`monitor` sem `handle` nao engole o erro",
     "Ele so garante o `ensure`."),
    ("Palavras reservadas nao podem ser nomes",
     "As que mais pegam em portugues: `no`, `in`, `is`, `to`, `from`, "
     "`as`, `step`, `point`, `default`, `frame`, `stream`, `emit`, "
     "`record`, `enum`, `when`. Ja `range`, `cluster` e `vault` sao "
     "FUNCOES, nao reservadas."),
    ("`self` dentro de metodos, sempre",
     "Escrever `x` em vez de `self.x` le a variavel do escopo externo."),
    ("Records sao imutaveis",
     "`p.x := 1` e erro; use `p with {\"x\": 1}`."),
    ("O valor inicial do `distill` vem DEPOIS do corpo",
     "`>> distill a, v: a + v 0 / len(x)` divide o ZERO. Use "
     "parenteses: `(xs >> distill a, v: a + v 0) / len(xs)`."),
    ("Um pipeline dentro de `lambda` precisa de parenteses",
     "O corpo do lambda liga mais forte que `>>`. O mesmo vale para o "
     "ternario: `lambda x => (a given c otherwise b)`."),
    ("`trigger` levanta `TriggerError`, nao `RuntimeError`",
     "Para pegar qualquer coisa, `handle Error`."),
    ("Dentro de `$\"{…}\"`, aspas normais",
     "`$\"item {v[\"id\"]}\"` funciona; escapar quebra a leitura."),
    ("`cycle from … to` e INCLUSIVO nos dois extremos",
     "`cycle i from 1 to 5` roda cinco vezes."),
    ("Um tipo de outro modulo se escreve qualificado",
     "`action criar() -> M.Pedido:` — vale em retorno, parametro, campo "
     "de record e anotacao de variavel."),
]


def montar():
    dados = _linguagem()
    L = []
    w = L.append

    w("# DataForge")
    w("")
    w(f"> Linguagem de programacao interpretada, de proposito geral, com "
      f"vocabulario em portugues. Versao {dados['versao']}. "
      f"Implementada em Python 3.10+ sem dependencia externa: lexer, "
      f"parser, AST, analisador estatico e interpretador proprios. "
      f"Arquivos `.df`. Licenca MIT.")
    w("")
    w(f"Site: {SITE}  ·  Documentacao: {SITE}/docs  ·  "
      f"API em JSON: {SITE}/api")
    w("")
    w("## Leia isto primeiro")
    w("")
    w("DataForge NAO e Python com outras palavras. Escrever Python aqui "
      "produz codigo que nao compila. As diferencas que mais custam "
      "estao logo abaixo, antes de qualquer lista de simbolos.")
    w("")

    w("## Armadilhas (o que faz um modelo errar)")
    w("")
    for titulo, texto in ARMADILHAS:
        w(f"- **{titulo}.** {texto}")
    w("")

    w("## Tabela de traducao")
    w("")
    w("| Em outra linguagem | Em DataForge |")
    w("|---|---|")
    for de, para in TRADUCAO:
        w(f"| `{de}` | `{para}` |")
    w("")

    w("## Um programa completo")
    w("")
    w("```dataforge")
    w(EXEMPLO.strip())
    w("```")
    w("")

    w(f"## As {len(dados['palavras'])} palavras reservadas")
    w("")
    w("Nenhuma delas pode ser nome de variavel.")
    w("")
    w("```")
    linha = []
    for palavra in dados["palavras"]:
        linha.append(f"{palavra:<12}")
        if len(linha) == 6:
            w("".join(linha).rstrip())
            linha = []
    if linha:
        w("".join(linha).rstrip())
    w("```")
    w("")

    w(f"## A biblioteca: {len(dados['modulos'])} modulos")
    w("")
    w("Todos por `adopt`. Nenhum precisa de instalacao.")
    w("")
    w("| Modulo | Simbolos | Para que serve |")
    w("|---|---|---|")
    for nome, descricao, quantos in dados["modulos"]:
        w(f"| `{nome}` | {quantos} | {descricao} |")
    w("")

    w(f"## As {len(dados['embutidas'])} funcoes embutidas")
    w("")
    w("Disponiveis sem `adopt`.")
    w("")
    w("```")
    linha = []
    for nome in dados["embutidas"]:
        linha.append(f"{nome:<20}")
        if len(linha) == 4:
            w("".join(linha).rstrip())
            linha = []
    if linha:
        w("".join(linha).rstrip())
    w("```")
    w("")

    w("## As ferramentas")
    w("")
    w("```")
    for linha_cmd in FERRAMENTAS.strip().split("\n"):
        w(linha_cmd)
    w("```")
    w("")

    w("## Onde ler mais")
    w("")
    for rota, sobre in PAGINAS:
        w(f"- [{sobre}]({SITE}{rota})")
    w("")
    w("A API em JSON (`/api/*.json`, CORS aberto) traz a sintaxe, os "
      "simbolos, os comandos e os codigos de erro como dado — util para "
      "quem quer a lista inteira sem raspar HTML.")
    w("")
    return "\n".join(L)


EXEMPLO = '''
adopt Arcane.Math as Math

record Pedido:
    id: Integer
    total: Float

    action com_desconto(p: Float) -> Float:
        yield self.total * (1.0 - p)

enum Estado:
    Aberto
    Pago := "pago"

blueprint Carrinho:
    self.itens := []

    action por(pedido):
        self.itens.append(pedido)
        yield len(self.itens)

action resumir(pedidos: Cluster) -> Vault:
    total := pedidos >> distill soma, p: soma + p.total 0
    yield {"quantos": len(pedidos), "total": total}

action classificar(valor) -> String:
    match valor:
        point Integer as n when n bigger 100:
            yield "grande"
        point [a, b]:
            yield "par"
        point {"tipo": t}:
            yield t
        default:
            yield "outro"

stream action naturais():
    n := 0
    persist yes:
        n += 1
        emit n

carrinho := spawn Carrinho()
_ := carrinho.por(Pedido(1, 99.9))
_ := carrinho.por(Pedido(2, 15.0))

monitor:
    out resumir(carrinho.itens)
handle Error as e:
    out e.type, e.message
ensure:
    out "sempre roda"

out naturais().map(lambda n: n * 2).take(5)
out [p.id cycle p in carrinho.itens given p.total bigger 50]
'''

FERRAMENTAS = """
dataforge run arquivo.df          roda
dataforge check src/              analisa antes de rodar (nomes, tipos, aridade)
dataforge test                    roda os *_test.df, com --cobertura
dataforge fmt .                   formata
dataforge lint src/               estilo e higiene
dataforge repl                    console interativo
dataforge debug arquivo.df        depurador de terminal
dataforge dap                     o depurador no painel do editor
dataforge new <modelo>            9 modelos de projeto
dataforge add <pacote>            gerenciador de pacotes (semver, lockfile)
dataforge devops dockerfile       Dockerfile, compose, CI, k8s, Helm, nginx
dataforge vitrine run app.df      sobe um painel de dados
dataforge profile arquivo.df      tempo proprio por acao
dataforge doc src/ --out=API.md   documentacao a partir dos comentarios
"""

PAGINAS = [
    ("/docs", "Introducao"),
    ("/docs/referencia", "Referencia da linguagem"),
    ("/docs/biblioteca", "A biblioteca Arcane, modulo a modulo"),
    ("/docs/kiln", "Kiln — o framework web"),
    ("/docs/vitrine", "Vitrine — dashboards e aplicacoes de dados"),
    ("/docs/lavra", "Lavra — a consulta tipada, no espirito do GraphQL"),
    ("/docs/crucible", "Crucible — testes"),
    ("/docs/exercicios", "Os exercicios, que verificam o proprio resultado"),
    ("/docs/erros", "Os codigos de erro, com exemplo e correcao"),
    ("/api", "A API publica em JSON"),
]


def main():
    texto = montar()
    if "--check" in sys.argv:
        for destino in DESTINOS:
            if not os.path.isfile(destino):
                print(f"  ✗ {os.path.relpath(destino, RAIZ)} nao existe")
                return 1
            if open(destino, encoding="utf-8").read() != texto:
                print(f"  ✗ {os.path.relpath(destino, RAIZ)} esta "
                      f"desatualizado — rode scripts/gerar_llms.py")
                return 1
        print("  o llms.txt esta em dia")
        return 0

    for destino in DESTINOS:
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"  {os.path.relpath(destino, RAIZ)}  "
              f"{len(texto) / 1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
