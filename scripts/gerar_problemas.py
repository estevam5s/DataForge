#!/usr/bin/env python3
"""
Verifica as soluções de referência e publica os problemas no Supabase.

    python3 scripts/gerar_problemas.py --testar    # só verifica
    python3 scripts/gerar_problemas.py             # verifica e publica

**Toda solução roda contra todos os casos antes de publicar.** Um
problema cuja própria solução não passa é um problema quebrado, e
descobrir isso pelo usuário é tarde demais.

O mesmo corretor roda no painel: `codigo + chamada`, comparando a saída
com o esperado. Se a verificação passa aqui, o painel se comporta igual.
"""

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "problemas"))

from catalogo import PROBLEMAS                                  # noqa: E402
from dataforge.interpreter import Interpreter                   # noqa: E402
from dataforge.lexer import tokenize                            # noqa: E402
from dataforge.parser import parse                              # noqa: E402

VERDE, VERMELHO, CINZA, LIMPO = "\033[1;32m", "\033[1;31m", "\033[0;90m", "\033[0m"


def em_dataforge(valor):
    """Um valor Python escrito como literal DataForge."""
    if valor is True:
        return "yes"
    if valor is False:
        return "no"
    if valor is None:
        return "void"
    if isinstance(valor, str):
        return json.dumps(valor, ensure_ascii=False)
    if isinstance(valor, list):
        return "[" + ", ".join(em_dataforge(v) for v in valor) + "]"
    if isinstance(valor, dict):
        return "{" + ", ".join(f"{json.dumps(k)}: {em_dataforge(v)}"
                               for k, v in valor.items()) + "}"
    return repr(valor)


def rodar(codigo, entrada):
    """Executa `resolver(*entrada)` e devolve o valor, sem imprimir nada.

    O resultado sai por uma variável global do programa, não pelo stdout:
    comparar texto impresso confundiria 5 com "5".
    """
    argumentos = ", ".join(em_dataforge(v) for v in entrada)
    fonte = f"{codigo}\n\n__saida__ := resolver({argumentos})\n"
    interpretador = Interpreter()
    interpretador.run(parse(tokenize(fonte)))
    return interpretador.global_env.variables.get("__saida__")


def igual(obtido, esperado):
    """Comparação tolerante ao que não muda a resposta.

    Um Float que vale 2.0 e um Integer 2 são a mesma resposta para quem
    resolveu o problema; recusar seria implicância com o tipo.
    """
    if isinstance(esperado, float) or isinstance(obtido, float):
        try:
            return abs(float(obtido) - float(esperado)) < 1e-9
        except (TypeError, ValueError):
            return False
    if isinstance(esperado, list) and isinstance(obtido, (list, tuple)):
        return (len(esperado) == len(obtido)
                and all(igual(o, e) for o, e in zip(obtido, esperado)))
    return obtido == esperado


def verificar(problema):
    """Roda a solução de referência contra todos os casos."""
    falhas = []
    for caso in problema["casos"]:
        try:
            obtido = rodar(problema["solucao"], caso["entrada"])
        except Exception as erro:
            falhas.append((caso, f"{type(erro).__name__}: {erro}"))
            continue
        if not igual(obtido, caso["saida"]):
            falhas.append((caso, f"devolveu {obtido!r}, esperava {caso['saida']!r}"))
    return falhas


def publicar(problemas):
    """Manda o catálogo para o Supabase, um upsert por slug."""
    sys.path.insert(0, os.path.join(RAIZ, "scripts"))
    from supabase_aplicar import carregar_segredos, executar

    segredos = carregar_segredos()
    valores = []
    for ordem, p in enumerate(problemas):
        def texto(v):
            return "'" + str(v).replace("'", "''") + "'"

        def js(v):
            return texto(json.dumps(v, ensure_ascii=False)) + "::jsonb"

        conceitos = ("array[" + ", ".join(texto(c) for c in p["conceitos"])
                     + "]::text[]") if p["conceitos"] else "'{}'::text[]"
        valores.append(
            f"({texto(p['slug'])}, {texto(p['titulo'])}, "
            f"{texto(p['dificuldade'])}::public.dificuldade, "
            f"{texto(p['categoria'])}, {texto(p['enunciado'])}, "
            f"{texto(p['assinatura'])}, {js(p['exemplos'])}, "
            f"{js(p['dicas'])}, {js(p['casos'])}, {texto(p['solucao'])}, "
            f"{conceitos}, {ordem})")

    sql = (
        "insert into public.problemas (slug, titulo, dificuldade, categoria,"
        " enunciado, assinatura, exemplos, dicas, casos, solucao, conceitos,"
        " ordem) values\n" + ",\n".join(valores) +
        "\non conflict (slug) do update set"
        " titulo=excluded.titulo, dificuldade=excluded.dificuldade,"
        " categoria=excluded.categoria, enunciado=excluded.enunciado,"
        " assinatura=excluded.assinatura, exemplos=excluded.exemplos,"
        " dicas=excluded.dicas, casos=excluded.casos,"
        " solucao=excluded.solucao, conceitos=excluded.conceitos,"
        " ordem=excluded.ordem;")
    executar(sql, segredos)

    total = executar("select count(*) as n from public.problemas", segredos)
    return total[0]["n"]


def main():
    print(f"\n  {CINZA}verificando {len(PROBLEMAS)} problemas"
          f"{LIMPO}\n")
    quebrados = 0
    total_casos = 0
    for p in PROBLEMAS:
        falhas = verificar(p)
        total_casos += len(p["casos"])
        if falhas:
            quebrados += 1
            print(f"  {VERMELHO}✗{LIMPO} {p['slug']:<28} "
                  f"{len(falhas)}/{len(p['casos'])} casos falharam")
            for caso, motivo in falhas[:3]:
                print(f"      {CINZA}entrada {caso['entrada']!r}{LIMPO}")
                print(f"      {VERMELHO}{motivo}{LIMPO}")
        else:
            print(f"  {VERDE}✓{LIMPO} {p['slug']:<28} "
                  f"{CINZA}{len(p['casos'])} casos{LIMPO}")

    print(f"\n  {len(PROBLEMAS) - quebrados}/{len(PROBLEMAS)} problemas, "
          f"{total_casos} casos de teste")

    if quebrados:
        print(f"\n  {VERMELHO}{quebrados} problema(s) com a solução de "
              f"referência quebrada — nada foi publicado.{LIMPO}\n")
        raise SystemExit(1)

    if "--testar" in sys.argv:
        print()
        return

    print(f"\n  {CINZA}publicando…{LIMPO}")
    quantos = publicar(PROBLEMAS)
    print(f"  {VERDE}✓{LIMPO} {quantos} problemas no banco\n")


if __name__ == "__main__":
    main()
