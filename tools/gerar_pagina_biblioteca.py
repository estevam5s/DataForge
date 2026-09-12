#!/usr/bin/env python3
"""
Gera a pagina /docs/biblioteca a partir do catalogo e dos modulos.

    python3 tools/gerar_pagina_biblioteca.py

A tabela era escrita a mao e envelheceu duas vezes: anunciava "trinta e
sete modulos" tendo trinta e oito, e SEIS modulos nao apareciam nela —
Arcane.API, Decimal, Observar, Ponte, Stream e Vitrine. Um modulo que
existe e nao aparece e trabalho que ninguem encontra.

A contagem de simbolos e as descricoes saem do codigo. O que sobra de
escrito a mao aqui e so o texto ao redor da tabela.
"""

import json
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import marca  # noqa: E402

marca.preparar_saida()

from dataforge.stdlib import get_module, list_modules       # noqa: E402
from dataforge.stdlib.catalogo import DESCRICOES            # noqa: E402

DESTINO = os.path.join(RAIZ, "site", "app", "docs", "biblioteca",
                       "page.tsx")

#: 'trinta e oito' em vez de '38' no titulo da secao — a pagina e texto,
#: e numero por extenso le melhor. Ate cinquenta basta.
EXTENSO = {
    20: "vinte", 21: "vinte e um", 22: "vinte e dois", 23: "vinte e três",
    24: "vinte e quatro", 25: "vinte e cinco", 26: "vinte e seis",
    27: "vinte e sete", 28: "vinte e oito", 29: "vinte e nove",
    30: "trinta", 31: "trinta e um", 32: "trinta e dois",
    33: "trinta e três", 34: "trinta e quatro", 35: "trinta e cinco",
    36: "trinta e seis", 37: "trinta e sete", 38: "trinta e oito",
    39: "trinta e nove", 40: "quarenta", 41: "quarenta e um",
    42: "quarenta e dois", 43: "quarenta e três",
    44: "quarenta e quatro", 45: "quarenta e cinco",
    46: "quarenta e seis", 47: "quarenta e sete",
    48: "quarenta e oito", 49: "quarenta e nove", 50: "cinquenta",
}


def por_extenso(n):
    return EXTENSO.get(n, str(n))


def paginas_existentes():
    """Os modulos que tem pagina propria, para virarem link."""
    pasta = os.path.join(RAIZ, "site", "app", "docs", "biblioteca")
    if not os.path.isdir(pasta):
        return set()
    return {nome for nome in os.listdir(pasta)
            if os.path.isfile(os.path.join(pasta, nome, "page.tsx"))}


#: Um modulo grande o bastante para merecer destaque tem pagina propria
#: fora de /docs/biblioteca. Aqui ficam esses desvios.
FORA = {
    "Kiln": "/docs/kiln",
    "Arcane.Vitrine": "/docs/vitrine",
    "Arcane.Crucible": "/docs/tecnicas/testes",
    "Arcane.Lago": "/docs/tecnicas/lago",
    "Arcane.Pipeline": "/docs/tecnicas/pipeline",
    "Arcane.Qualidade": "/docs/tecnicas/qualidade",
    "Arcane.Stream": "/docs/tecnicas/streaming",
    "Arcane.Observar": "/docs/tecnicas/observar",
    "Arcane.Archive": "/docs/tecnicas/arquivos",
    "Arcane.Concurrent": "/docs/tecnicas/concorrencia",
    "Arcane.Forge": "/docs/tecnicas/banco-de-dados",
    "Arcane.Ponte": "/docs/tecnicas/ponte",
    "Arcane.Decimal": "/docs/tecnicas/decimal",
    "Arcane.API": "/docs/tecnicas/api",
}


def destino_de(oficial, com_pagina):
    """O link do modulo, ou vazio quando ele nao tem pagina."""
    curto = oficial.split(".")[-1].lower()
    if curto in com_pagina:
        return f"/docs/biblioteca/{curto}"
    fora = FORA.get(oficial)
    if fora and os.path.isfile(
            os.path.join(RAIZ, "site", "app", fora.strip("/"), "page.tsx")):
        return fora
    return ""


def levantar():
    """(oficial, simbolos, descricao, link) de cada modulo, do maior."""
    com_pagina = paginas_existentes()
    vistos = {}
    for nome in list_modules():
        modulo = get_module(nome)
        oficial = modulo["__name__"]
        if oficial in vistos:
            continue
        simbolos = len([k for k in modulo if not k.startswith("__")])
        descricao = DESCRICOES.get(oficial, ("", ""))[0]
        if not descricao:
            raise SystemExit(
                f"'{oficial}' nao esta em DESCRICOES de "
                f"dataforge/stdlib/catalogo.py.\n"
                f"Todo modulo precisa de uma linha la — e dela sai a doc "
                f"em Markdown, os dados do site e esta pagina.")
        vistos[oficial] = (oficial, simbolos, descricao,
                           destino_de(oficial, com_pagina))
    return sorted(vistos.values(), key=lambda m: (-m[1], m[0]))


def construir():
    modulos = levantar()
    total = sum(m[1] for m in modulos)
    quantos = len(modulos)

    linhas = []
    for oficial, simbolos, descricao, link in modulos:
        rotulo = f"[`{oficial}`]({link})" if link else f"`{oficial}`"
        linhas.append([rotulo, str(simbolos), descricao])

    sem_pagina = [m[0] for m in modulos if not m[3]]

    blocos = [
        {"h2": "Importar"},
        {"code": """adopt Arcane.Math as Math                # o módulo inteiro
adopt Arcane.Math.{sqrt, factorial}       # só o que você usa
adopt {sqrt as raiz} from Arcane.Math     # com apelido

out Math.sqrt(16), sqrt(16), raiz(16)""", "lang": "df"},
        {"p": "Cada módulo tem um **nome curto** equivalente: "
              "`adopt Math as M` funciona igual a `adopt Arcane.Math as M`."},

        {"h2": f"Os {por_extenso(quantos)} módulos"},
        {"p": f"São **{total} símbolos** ao todo. Esta tabela é gerada "
              "do próprio código: a contagem sai dos módulos e a "
              "descrição, do catálogo."},
        {"table": {"head": ["Módulo", "Símbolos", "Para quê"],
                   "rows": linhas}},

        {"h2": "Sem dependências"},
        {"p": "Toda a biblioteca usa apenas a biblioteca padrão do "
              "Python. Isso significa que um programa DataForge roda em "
              "qualquer máquina com Python 3.10+, sem `pip install` de "
              "nada."},
        {"p": "A contrapartida é o escopo: não há cliente de PostgreSQL "
              "nem parser de YAML na biblioteca. O que existe é o que "
              "dá para fazer bem sem arrastar o ecossistema inteiro "
              "junto — e, quando falta, "
              "[`adopt Python.<pacote>`](/docs/tecnicas/ponte) "
              "alcança qualquer biblioteca do Python."},

        {"h2": "Os dois frameworks web"},
        {"table": {"head": ["", "Kiln", "Vitrine"], "rows": [
            ["Para", "sites e APIs",
             "painéis e aplicações de dados"],
            ["Você escreve", "rotas que devolvem o que quiser",
             "um programa de cima para baixo"],
            ["Sintaxe", "onze palavras contextuais",
             "nenhuma palavra nova"],
            ["Documentação", "[/docs/kiln](/docs/kiln)",
             "[/docs/vitrine](/docs/vitrine)"]]}},
        {"p": "A Vitrine roda **sobre** o Kiln: HTTP, rotas, sessão e "
              "cabeçalhos de segurança vêm dele."},

        {"h2": "Além dos módulos"},
        {"p": "Existem ainda **228 funções globais** disponíveis sem "
              "nenhum `adopt` — `len`, `sum`, `sorted`, `map`, `round`, "
              "`str`, e o resto. A lista completa está em "
              "[Funções embutidas](/docs/referencia/embutidas)."},
    ]

    if sem_pagina:
        blocos.insert(-2, {"callout": {
            "tipo": "nota",
            "titulo": "Onde ver a assinatura de cada símbolo",
            "texto": "Os módulos sem link acima ainda não têm página "
                     "própria. Para eles, `doc/BIBLIOTECA_PADRAO.md` "
                     "no repositório traz todos os símbolos com "
                     "assinatura, e `dataforge repl` responde "
                     "`:doc Arcane.<Nome>`."}})

    corpo = json.dumps(blocos, ensure_ascii=False, indent=2)

    def slug(texto):
        texto = unicodedata.normalize("NFD", texto)
        texto = "".join(c for c in texto
                        if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9\s-]", "",
                      texto.lower()).strip().replace(" ", "-")

    titulos = [b["h2"] for b in blocos if "h2" in b]
    cabecalhos = ", ".join(
        "{ id: '%s', text: %s, level: 2 as const }"
        % (slug(t), json.dumps(t, ensure_ascii=False)) for t in titulos)

    descricao = (f"{por_extenso(quantos).capitalize()} módulos e "
                 f"{total} símbolos, sem uma única dependência externa.")

    return f'''import type {{ Metadata }} from 'next';
import type {{ Bloco }} from '@/lib/content';
import {{ DocPage }} from '@/components/Doc';
import {{ Renderer }} from '@/components/Renderer';

// Gerado por tools/gerar_pagina_biblioteca.py — não edite à mão.

export const metadata: Metadata = {{
  title: "Biblioteca Arcane",
  description: {json.dumps(descricao, ensure_ascii=False)},
}};

const blocos: Bloco[] = {corpo};

const headings = [{cabecalhos}];

export default function Pagina() {{
  return (
    <DocPage
      title={{"Biblioteca Arcane"}}
      description={{{json.dumps(descricao, ensure_ascii=False)}}}
      href={{"/docs/biblioteca"}}
      headings={{headings}}
    >
      <Renderer blocos={{blocos}} />
    </DocPage>
  );
}}
'''


def main():
    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(construir())
    modulos = levantar()
    print(f"pagina gerada: {os.path.relpath(DESTINO, RAIZ)}")
    print(f"  {len(modulos)} modulos, "
          f"{sum(m[1] for m in modulos)} simbolos")
    sem = [m[0] for m in modulos if not m[3]]
    if sem:
        print(f"  {len(sem)} sem pagina propria: {', '.join(sem)}")


if __name__ == "__main__":
    main()
