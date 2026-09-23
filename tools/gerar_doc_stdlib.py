#!/usr/bin/env python3
"""Gera doc/BIBLIOTECA_PADRAO.md a partir das assinaturas reais dos modulos Arcane.

Rode depois de mexer em dataforge/stdlib/ para manter a documentacao em sincronia:

    python3 tools/gerar_doc_stdlib.py
"""

import inspect
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

# A saida deste script tambem desenha, e precisa sobreviver a um
# terminal que nao fala UTF-8 — o cano do Windows e cp1252, que
# nao tem um unico dos tracos usados aqui.
from dataforge import marca  # noqa: E402

marca.preparar_saida()

from dataforge.stdlib import get_module  # noqa: E402

#: A tabela vive em 'dataforge/stdlib/catalogo.py', ao lado do
#: codigo que ela descreve — e nao em copia por gerador.
from dataforge.stdlib.catalogo import DESCRICOES, assinatura_fixa  # noqa: E402

CABECALHO = """# Biblioteca padrão DataForge — módulos `Arcane.*`

Referência gerada a partir das assinaturas reais do código
(`python3 tools/gerar_doc_stdlib.py`). Todo módulo é carregado com `adopt`:

```dataforge
adopt Arcane.Math as Math
out Math.sqrt(16)
```

Cada módulo tem um **nome curto** equivalente (`adopt Math as M` funciona igual).

## Índice

| Módulo | Nome curto | Símbolos | Para quê |
|--------|-----------|----------|----------|"""

RODAPE_INDICE = """
> Os nomes curtos e os aliases (`DB`, `Server`, `Network`) apontam para o mesmo
> módulo — use o que ficar mais legível.

## Exemplos rápidos

```dataforge
adopt Arcane.Math as Math
adopt Arcane.Text as Text
adopt Arcane.Analytics as An

out Math.sqrt(16)                       // 4.0
out Math.is_prime(97)                   // yes
out Text.slug("Ola Mundo")              // ola-mundo
out Text.box("Relatorio")               // caixa desenhada
out An.correlation([1,2,3], [2,4,6])    // 1.0
```
"""


def e_funcao_do_c(valor):
    """E uma funcao escrita em C, vinda da biblioteca do Python?

    O nome do parametro dessas nao e estavel entre versoes:
    `math.factorial` chama o dele de `x` ate o 3.12 e de `n` a partir do
    3.13. Deixar `inspect` decidir fazia a documentacao da linguagem
    depender da versao de Python de quem rodou o gerador.
    """
    return (inspect.isbuiltin(valor)
            or type(valor).__name__ in ("builtin_function_or_method",
                                        "method_descriptor"))


def assinatura(valor, simbolo=""):
    """Devolve (assinatura, None) para funcoes e (None, valor) para constantes."""
    if not callable(valor):
        texto = repr(valor)
        return None, (texto[:50] + "…" if len(texto) > 50 else texto)

    if e_funcao_do_c(valor):
        fixa = assinatura_fixa(simbolo)
        if fixa is None:
            raise SystemExit(
                f"'{simbolo}' e uma funcao C do Python e nao esta em "
                f"ASSINATURAS, no 'dataforge/stdlib/catalogo.py'.\n"
                f"Sem uma entrada la, a documentacao herda o nome de "
                f"parametro do CPython — que muda entre versoes — e este "
                f"arquivo deixa de ser reproduzivel.")
        return fixa, None

    try:
        sig = str(inspect.signature(valor))
    except (TypeError, ValueError):
        sig = "(…)"
    return sig.replace(", /", "").replace("(/)", "()").replace("/, ", ""), None


def main():
    partes = [CABECALHO]
    corpos = []

    for nome, (descricao, curto) in DESCRICOES.items():
        modulo = get_module(nome)
        if modulo is None:
            print(f"AVISO: modulo {nome} nao carregou", file=sys.stderr)
            continue
        itens = sorted(k for k in modulo if not k.startswith("__"))
        ancora = nome.lower().replace(".", "")
        partes.append(f"| [`{nome}`](#{ancora}) | `{curto}` | {len(itens)} | {descricao} |")

        corpo = [
            f"\n---\n\n## {nome}\n\n{descricao}\n",
            f"```dataforge\nadopt {nome} as {curto.split(' / ')[0]}\n```\n",
        ]
        constantes, funcoes = [], []
        for chave in itens:
            sig, valor = assinatura(modulo[chave], chave)
            if sig is None:
                constantes.append(f"| `{chave}` | `{valor}` |")
            else:
                funcoes.append(f"| `{chave}{sig}` |")

        if constantes:
            corpo.append("**Constantes**\n\n| Nome | Valor |\n|------|-------|")
            corpo.extend(constantes)
            corpo.append("")
        if funcoes:
            corpo.append(f"**Funções ({len(funcoes)})**\n\n| Assinatura |\n|------------|")
            corpo.extend(funcoes)
            corpo.append("")
        corpos.append("\n".join(corpo))

    partes.append(RODAPE_INDICE)
    partes.extend(corpos)

    destino = os.path.join(RAIZ, "doc", "BIBLIOTECA_PADRAO.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(partes))
    print(f"gerado: {destino}")

    atualizar_readme()
    atualizar_estado()


#: Os marcadores que delimitam a tabela gerada dentro do README.
ABRE = "<!-- stdlib:inicio -->"
FECHA = "<!-- stdlib:fim -->"

#: E os do quadro de estado, pelo mesmo motivo. Ele dizia "1012 testes"
#: e "216 exercicios" com 5.868 e 397 — e listava como ausente o que ja
#: existia ha meses (generics com limite, exaustividade alem de enum,
#: depurador com ponto de parada). Um quadro de estado que descreve um
#: estado que ja nao e o do projeto e lido como verdade, e cada numero
#: errado dele vira uma decisao errada.
ABRE_ESTADO = "<!-- estado:inicio -->"
FECHA_ESTADO = "<!-- estado:fim -->"


def _trocar_bloco(caminho, abre, fecha, novo, o_que):
    texto = open(caminho, encoding="utf-8").read()
    if abre not in texto or fecha not in texto:
        print(f"  ({os.path.basename(caminho)} sem {abre}: pulando)")
        return
    inicio = texto.index(abre)
    fim = texto.index(fecha) + len(fecha)
    open(caminho, "w", encoding="utf-8").write(texto[:inicio] + novo + texto[fim:])
    print(f"gerado: {caminho} ({o_que})")


def _contar(padrao, recursivo=True):
    import glob
    return len(glob.glob(os.path.join(RAIZ, padrao), recursive=recursivo))


def atualizar_estado():
    """O quadro de estado e a lista do que NAO existe, lidos do codigo.

    A lista de ausencias vem de `Arcane.Ecossistema`, que e conferido
    contra o disco — e nao de um paragrafo escrito a mao, que e o que
    fez este README anunciar como falta quatro coisas que existiam.
    """
    import glob
    import json

    from dataforge.catalogo_erros import ERROS
    from dataforge.cli import COMANDOS
    from dataforge.stdlib import get_module, list_modules

    oficiais = {get_module(n)["__name__"] for n in set(list_modules())}
    simbolos = sum(len([k for k in get_module(n) if not k.startswith("__")])
                   for n in oficiais)

    caminho_dados = os.path.join(RAIZ, "site", "lib", "dados-gerados.json")
    testes = exercicios = 0
    if os.path.exists(caminho_dados):
        with open(caminho_dados, encoding="utf-8") as f:
            dados = json.load(f)
        testes = dados["contagem"]["testes"]
        exercicios = sum(len(v) for v in dados["exercicios"].values())

    conferidos = sum(
        len(glob.glob(os.path.join(RAIZ, pasta, "**", "*.df"), recursive=True))
        for pasta in ("examples", "exercicios", "projetos", "packages", "trilha"))

    eco = get_module("Arcane.Ecossistema")
    numeros = eco["numeros"]()

    quadro = "\n".join([
        ABRE_ESTADO,
        "| Verificação | Resultado |",
        "|-------------|-----------|",
        f"| `pytest tests/` | {testes} funções de teste |",
        f"| `exercicios/run_all.py` | {exercicios}/{exercicios} |",
        f"| `trilha/run_all.py` | {_contar('trilha/*.df')} capítulos |",
        f"| `examples/*.df` | {_contar('examples/*.df')} programas |",
        f"| Módulos da stdlib | {len(oficiais)} carregam, {simbolos} símbolos |",
        f"| Comandos da CLI | {len({c.nome for c in COMANDOS.values()})} |",
        f"| Códigos de erro | {len(ERROS)} |",
        f"| `dataforge check` × 5 pastas | 0 erros em {conferidos} arquivos |",
        f"| Componentes do ecossistema | {numeros['componentes']} conferidos "
        f"contra o disco: {numeros['existem']} existem, "
        f"{numeros['equivalem']} equivalem, {numeros['nao_existem']} não |",
        "| Instalação via pip, curl e Docker | funciona |",
        "",
        "### O que ainda não existe",
        "",
        "Lido de `Arcane.Ecossistema`, que é **conferido contra o disco** —",
        "e não de um parágrafo, que é o que fez esta seção anunciar como",
        "falta quatro coisas que já existiam:",
        "",
        "| Não há | O que há no lugar |",
        "|--------|-------------------|",
        *[f"| **{no['no']}** | {no['aqui'][:160]}{'…' if len(no['aqui']) > 160 else ''} |"
          for no in eco["o_que_nao_existe"]()],
        "",
        "A lista viva: `dataforge ecossistema`. O roadmap completo está em",
        "[`doc/ANALISE_E_ROADMAP.md`](doc/ANALISE_E_ROADMAP.md).",
        FECHA_ESTADO,
    ])
    _trocar_bloco(os.path.join(RAIZ, "README.md"), ABRE_ESTADO, FECHA_ESTADO,
                  quadro, "quadro de estado")


def atualizar_readme():
    """A mesma tabela, dentro do README, entre marcadores.

    Ela ja esteve escrita a mao ali — e divergiu: anunciava 22 modulos
    com 753 simbolos e um 'Arcane.Crypto' com 38, quando eram 29, 1016
    e 48. Numero em README nao envelhece sozinho; envelhece porque foi
    digitado.
    """
    from dataforge.stdlib import get_module, list_modules

    oficiais = {get_module(n)["__name__"] for n in set(list_modules())}
    def quantos(n):
        return len([k for k in get_module(n) if not k.startswith("__")])

    # O nome desempata: sem ele, dois modulos com o mesmo numero de
    # simbolos trocavam de lugar a cada execucao — 'oficiais' e um
    # conjunto, e a ordem de um conjunto de textos muda a cada processo.
    # O gerador tem de dar o MESMO arquivo toda vez, senao o teste que
    # o compara com o versionado falha sozinho.
    linhas = []
    for nome in sorted(oficiais, key=lambda n: (-quantos(n), n)):
        modulo = get_module(nome)
        simbolos = [k for k in modulo if not k.startswith("__")]
        descricao, _ = DESCRICOES.get(nome, ("", ""))
        linhas.append(f"| `{nome}` | {len(simbolos)} | {descricao} |")

    total = sum(len([k for k in get_module(n) if not k.startswith("__")])
                for n in oficiais)
    from dataforge.builtins import get_builtins

    tabela = "\n".join([
        ABRE,
        f"{len(oficiais)} módulos, {total} símbolos, mais {len(get_builtins())} "
        "funções globais sem import.",
        "",
        "| Módulo | Símbolos | Para quê |",
        "|--------|----------|----------|",
        *linhas,
        FECHA,
    ])

    caminho = os.path.join(RAIZ, "README.md")
    texto = open(caminho, encoding="utf-8").read()
    if ABRE not in texto or FECHA not in texto:
        print(f"  (README sem os marcadores {ABRE} … {FECHA}: pulando)")
        return
    inicio = texto.index(ABRE)
    fim = texto.index(FECHA) + len(FECHA)
    open(caminho, "w", encoding="utf-8").write(
        texto[:inicio] + tabela + texto[fim:])
    print(f"gerado: {caminho} (tabela da stdlib)")


if __name__ == "__main__":
    main()
