# -*- coding: utf-8 -*-
"""Uma pagina por modulo da Arcane, gerada do PROPRIO modulo.

O problema que ele resolve
--------------------------
As paginas de `/docs/biblioteca/<modulo>` traziam a lista de simbolos
**copiada a mao**, e nenhum gerador as mantinha. Elas envelheceram em
silencio: a de `Arcane.Regex` anunciava *"Funcoes (28)"* onde havia 44,
e a contagem estava no TITULO da secao — quem abre a pagina le o numero
antes de ler a lista.

E havia o outro lado: **32 dos 75 modulos nao tinham pagina nenhuma**.
`Arcane.Quadro`, `Arcane.Malha`, `Arcane.Posse` e `Arcane.Reflexo`
existem, tem centenas de simbolos somados, e a unica forma de ver a
assinatura de um deles era abrir o codigo.

Os dois problemas tem a mesma causa e a mesma correcao: a lista sai do
modulo, sempre.

O que e escrito, e o que e derivado
-----------------------------------
    escrito     o prologo: exemplo, aviso, link para o guia
                mora em 'site/scripts/conteudo_biblioteca/<curto>.py'
    derivado    a tabela de constantes e a de funcoes, com a assinatura
                lida por 'inspect' do objeto que o 'adopt' entrega

O prologo mora **fora** do `.tsx` de proposito. Deixa-lo dentro de um
arquivo marcado `GERADO` e o convite para edita-lo ali — e a correcao
some na proxima geracao, sem nada explicando. Foi exatamente assim que
uma contagem de simbolos ja voltou a ficar errada depois de corrigida.

    python3 tools/gerar_paginas_biblioteca.py
    python3 tools/gerar_paginas_biblioteca.py --check   # so confere
"""

import importlib.util
import inspect
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import marca  # noqa: E402

# No Windows a saida do console nao e UTF-8, e um gerador que desenha
# '✓' morre ao imprimir — depois de ja ter escrito os arquivos.
marca.preparar_saida()

from dataforge.stdlib import get_module, list_modules       # noqa: E402
from dataforge.stdlib.catalogo import DESCRICOES            # noqa: E402

PROLOGOS = os.path.join(RAIZ, "site", "scripts", "conteudo_biblioteca")
DESTINO = os.path.join(RAIZ, "site", "app", "docs", "biblioteca")

#: Modulos que NAO ganham pagina propria. Cada um tem um motivo, e a
#: lista e fechada: sem ela, um modulo novo nasceria fora da doc e
#: ninguem veria — que e o estado de onde este gerador veio.
SEM_PAGINA = {
    # Os frameworks tem secao inteira, com varias paginas.
    "Kiln": "o framework web tem a propria secao",
    "Arcane.Vitrine": "o framework de dashboards tem a propria secao",
}


def _de_outro_gerador():
    """Os '/docs/biblioteca/<x>' que 'gerar_conteudo.py' ja escreve.

    Sete modulos (`Url`, `Bytes`, `Rede`, `Eventos`, `Cli`, `Email`,
    `Html`) tem guia inteiro escrito em 'site/scripts/conteudo/', e nao
    a forma fina de exemplo-mais-tabela. Este gerador cede a eles.

    A lista e LIDA, e nao escrita: duas ferramentas escrevendo o mesmo
    arquivo fazem o resultado depender da ordem em que rodam — e foi
    exatamente assim que as duas 'slugify' deste repositorio se
    sobrescreveram por um tempo.
    """
    import glob
    import re as _re

    pasta = os.path.join(RAIZ, "site", "scripts", "conteudo")
    donos = {}
    for caminho in sorted(glob.glob(os.path.join(pasta, "*.py"))):
        texto = open(caminho, encoding="utf-8").read()
        for href in _re.findall(r'"href":\s*"(/docs/biblioteca/[^"]+)"',
                                texto):
            donos[href.rsplit("/", 1)[-1]] = os.path.basename(caminho)
    return donos


def _prologo(curto):
    """O que foi escrito a mao para este modulo, se houver."""
    caminho = os.path.join(PROLOGOS, f"{curto}.py")
    if not os.path.isfile(caminho):
        return []
    spec = importlib.util.spec_from_file_location(
        f"_prologo_{curto}", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return list(getattr(modulo, "PROLOGO_TSX", []))


def _assinatura(nome, valor):
    """`somar(a, b=0)` — lida do objeto, e nao escrita a mao.

    Quando `inspect` nao consegue (um embutido do C, um objeto com
    `__call__`), sai so o nome. Inventar `(...)` ali seria pior: uma
    assinatura errada e consultada como se fosse certa.
    """
    try:
        return f"{nome}{inspect.signature(valor)}"
    except (TypeError, ValueError):
        return nome


def _valor_curto(valor):
    """O valor de uma constante, cortado para caber numa celula."""
    try:
        texto = json.dumps(valor, ensure_ascii=False)
    except (TypeError, ValueError):
        texto = repr(valor)
    return texto if len(texto) <= 60 else texto[:57] + "…"


def _partes(modulo):
    """As constantes e as funcoes, separadas e em ordem."""
    constantes, funcoes = [], []
    for nome in sorted(k for k in modulo if not k.startswith("__")):
        valor = modulo[nome]
        if callable(valor):
            funcoes.append((nome, valor))
        else:
            constantes.append((nome, valor))
    return constantes, funcoes


def _tabela(cabecalho, linhas):
    return json.dumps({"table": {"head": cabecalho, "rows": linhas}},
                      ensure_ascii=False)


def _blocos(curto, oficial, modulo):
    blocos = list(_prologo(curto))
    constantes, funcoes = _partes(modulo)

    if constantes:
        blocos.append(json.dumps({"h2": "Constantes"}, ensure_ascii=False))
        blocos.append(_tabela(
            ["Nome", "Valor"],
            [[f"`{n}`", f"`{_valor_curto(v)}`"] for n, v in constantes]))

    if funcoes:
        # A contagem entra no titulo porque e o que se le primeiro — e
        # era justamente ela que estava errada.
        blocos.append(json.dumps({"h2": f"Funções ({len(funcoes)})"},
                                 ensure_ascii=False))
        blocos.append(_tabela(
            ["Assinatura"],
            [[f"`{_assinatura(n, v)}`"] for n, v in funcoes]))

    if not constantes and not funcoes:
        blocos.append(json.dumps(
            {"p": f"`{oficial}` não expõe nenhum símbolo público."},
            ensure_ascii=False))
    return blocos


def _pagina(curto, oficial, descricao, blocos):
    titulo = json.dumps(oficial, ensure_ascii=False)
    desc = json.dumps(descricao, ensure_ascii=False)
    href = json.dumps(f"/docs/biblioteca/{curto}", ensure_ascii=False)

    from importlib import import_module
    sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))
    slugify = import_module("gerar_indices").slugify

    cabecas = []
    for bloco in blocos:
        if bloco.startswith('{"h2"'):
            texto = json.loads(bloco)["h2"]
            cabecas.append(
                "{ id: '%s', text: %s, level: 2 as const }"
                % (slugify(texto), json.dumps(texto, ensure_ascii=False)))

    corpo = ",\n  ".join(blocos)
    return f"""// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/{curto}.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type {{ Metadata }} from 'next';
import type {{ Bloco }} from '@/lib/content';
import {{ DocPage }} from '@/components/Doc';
import {{ Renderer }} from '@/components/Renderer';

export const metadata: Metadata = {{
  title: {titulo},
  description: {desc},
}};

const blocos: Bloco[] = [
  {corpo},
];

const headings = [{', '.join(cabecas)}];

export default function Pagina() {{
  return (
    <DocPage
      title={{{titulo}}}
      description={{{desc}}}
      href={{{href}}}
      headings={{headings}}
    >
      <Renderer blocos={{blocos}} />
    </DocPage>
  );
}}
"""


def modulos():
    """(curto, oficial, descricao, modulo) de cada modulo com pagina.

    Inclui os que outro gerador escreve: a barra lateral precisa deles,
    e um modulo cuja pagina existe e nao aparece no menu e um modulo
    que ninguem encontra.
    """
    vistos = {}
    for nome in list_modules():
        modulo = get_module(nome)
        oficial = modulo["__name__"]
        if oficial in vistos or oficial in SEM_PAGINA:
            continue
        descricao = DESCRICOES.get(oficial, ("", ""))[0]
        if not descricao:
            raise SystemExit(
                f"'{oficial}' nao esta em DESCRICOES de "
                f"'dataforge/stdlib/catalogo.py'. Um modulo sem descricao "
                f"nao tem o que a pagina dele anuncia.")
        vistos[oficial] = (oficial.split(".")[-1].lower(), oficial,
                           descricao, modulo)
    return [vistos[k] for k in sorted(vistos)]


def gerar(conferir=False):
    mudadas, iguais, cedidas = [], 0, 0
    donos = _de_outro_gerador()
    for curto, oficial, descricao, modulo in modulos():
        if curto in donos:
            cedidas += 1
            continue
        texto = _pagina(curto, oficial, descricao,
                        _blocos(curto, oficial, modulo))
        pasta = os.path.join(DESTINO, curto)
        caminho = os.path.join(pasta, "page.tsx")
        atual = (open(caminho, encoding="utf-8").read()
                 if os.path.isfile(caminho) else None)
        if atual == texto:
            iguais += 1
            continue
        mudadas.append(f"/docs/biblioteca/{curto}")
        if not conferir:
            os.makedirs(pasta, exist_ok=True)
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto)
    return mudadas, iguais, cedidas


def main():
    conferir = "--check" in sys.argv
    mudadas, iguais, cedidas = gerar(conferir)
    if conferir:
        if mudadas:
            print("  ✗ paginas da biblioteca fora de dia:")
            for href in mudadas:
                print(f"      {href}")
            print("    rode tools/gerar_paginas_biblioteca.py")
            return 1
        print(f"  ✓ as {iguais} paginas da biblioteca estao em dia "
              f"({cedidas} escritas por gerar_conteudo.py)")
        return 0
    total = len(mudadas) + iguais
    print(f"  {total} pagina(s) de modulo, {len(mudadas)} reescrita(s), "
          f"{cedidas} de outro gerador")
    for href in mudadas:
        print(f"      {href}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
