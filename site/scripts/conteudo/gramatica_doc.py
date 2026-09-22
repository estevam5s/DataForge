# -*- coding: utf-8 -*-
"""As páginas da gramática — geradas de `dataforge/gramatica.py`.

Nenhuma produção é escrita aqui: esta página as LÊ. É o que impede a
documentação de descrever uma sintaxe que o parser já não aceita —
cada exemplo abaixo é conferido por `tests/test_gramatica.py` e
executado por `tests/test_paginas_novas_rodam.py`.
"""
import os
import sys

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from dataforge import gramatica as G  # noqa: E402

_INTRO = {
    "lexico": "Antes do parser, o lexer corta o texto em tokens. É aqui que moram as "
              "decisões que mais enganam: o `//` que é comentário, o `d` que faz um "
              "decimal, a indentação que vira `INDENT`/`DEDENT`.",
    "expressoes": "Uma expressão produz um valor. A ordem em que os operadores ligam está "
                  "na [tabela de precedência](/docs/referencia/gramatica/precedencia), e "
                  "cada nível ali é conferido pela forma da árvore.",
    "instrucoes": "Uma instrução faz algo e não produz valor. As que abrem bloco terminam "
                  "em `:` e o corpo vem indentado.",
    "declaracoes": "Declarações dão nome a algo que dura: uma ação, um tipo, um molde de "
                   "objeto. Duas de topo com o mesmo nome no mesmo arquivo viram aviso — "
                   "a primeira não tem como ser alcançada.",
    "padroes": "O `match` compara a forma de um valor com uma lista de padrões, do mais "
               "específico ao mais geral.",
    "modulos": "Três palavras ligam arquivos: `adopt` traz, `relay` declara o que sai, "
               "e `mark` aplica um decorador.",
    "erros": "O caminho de erro tem sintaxe própria, e a regra que mais importa é que "
             "`halt`, `skip` e `yield` **não são erros**: eles atravessam o `monitor`.",
    "concorrencia": "A linguagem não sincroniza sozinha. Estas formas criam concorrência; "
                    "proteger o estado compartilhado é escolha de quem escreve.",
    "dominios": "Palavras que só valem dentro do bloco que as abre — por isso não roubam "
                "nomes de quem escreve.",
}


def _pagina_do_grupo(gid, nome, resumo):
    ps = G.do_grupo(gid)
    blocos = [{"p": _INTRO.get(gid, resumo)},
              {"table": {"head": ["Produção", "Nós que ela produz"], "rows": [
                  [f"`{p['nome']}`", ", ".join(f"`{c}`" for c in p["contem"])] for p in ps]}}]
    for p in ps:
        blocos.append({"h2": p["nome"]})
        blocos.append({"code": p["ebnf"], "lang": "text"})
        blocos.append({"code": p["exemplo"], "lang": "df"})
        if p["nota"]:
            blocos.append({"callout": {"tipo": "nota", "titulo": "O que engana",
                                       "texto": p["nota"]}})
    blocos.append({"p": "Estas produções saem de `dataforge/gramatica.py`. "
                        f"No terminal: `dataforge gramatica {gid}`. Volte para "
                        "[a gramática](/docs/referencia/gramatica)."})
    return {"href": f"/docs/referencia/gramatica/{gid}", "title": f"Gramática — {nome}",
            "description": f"{len(ps)} produções: {resumo}. Cada exemplo é aceito pelo parser.",
            "blocos": blocos}


def _precedencia():
    linhas = [[str(n["nivel"]), f"`{n['nome']}`", " ".join(f"`{o}`" for o in n["operadores"]),
               n["associa"]] for n in G.PRECEDENCIA]
    provas = [[f"`{e}`", f"`{r[0]}`" + (f" `{r[1]}`" if r[1] else "")]
              for e, r in G.CONFERENCIAS_DE_PRECEDENCIA]
    assoc = [[f"`{e}`", f"`{lado}` é `{c}`"] for e, lado, c in G.CONFERENCIAS_DE_ASSOCIACAO]
    return {
        "href": "/docs/referencia/gramatica/precedencia",
        "title": "Precedência, provada",
        "description": "Da mais fraca para a mais forte — e cada nível conferido pela forma da árvore.",
        "blocos": [
            {"p": "Uma tabela de precedência que ninguém confere é uma opinião. Esta sai de "
                  "`dataforge/gramatica.py`, e cada afirmação embaixo dela é uma expressão em "
                  "que a ordem **decide o resultado** — o teste parseia e confere qual nó fica "
                  "na raiz."},
            {"table": {"head": ["Nível", "Nome", "Operadores", "Associa"], "rows": linhas}},
            {"h2": "O que fica na raiz"},
            {"table": {"head": ["Expressão", "Raiz"], "rows": provas}},
            {"h2": "Para que lado associa"},
            {"table": {"head": ["Expressão", "O lado que guarda o resto"], "rows": assoc}},
            {"callout": {"tipo": "atencao", "titulo": "A comparação encadeia",
                         "texto": "`1 smaller 5 smaller 3` é `1 smaller 5 and 5 smaller 3` — "
                                  "e dá `no`. Não é `(1 smaller 5) smaller 3`, que compararia "
                                  "um booleano com um número."}},
            {"code": 'assert (1 smaller 2 smaller 3) is yes\nassert (1 smaller 5 smaller 3) is no\n'
                     'assert -2 ** 2 is -4\nassert 2 ** 3 ** 2 is 512\nassert 7 - 3 - 1 is 3\n'
                     'out "a precedencia confere executando, e nao so na arvore"', "lang": "df"},
            {"p": "No terminal: `dataforge gramatica --precedencia`. Veja também "
                  "[Precedência](/docs/referencia/precedencia)."},
        ]}


def _ambiguidades():
    return {
        "href": "/docs/referencia/gramatica/ambiguidades",
        "title": "Onde a leitura engana",
        "description": "As seis construções que o parser lê de um jeito e quem escreve lê de outro.",
        "blocos": [
            {"p": "Uma gramática sem ambiguidade para o parser ainda pode ser ambígua para quem "
                  "lê. Estas são as seis que mais custam tempo — cada uma com a forma certa, "
                  "que roda."},
            {"table": {"head": ["Parece", "O parser lê", "Escreva"], "rows": [
                ["`x // nota`", "comentário", "`x ~/ 2` para dividir"],
                ["`lambda => xs >> morph x: x * 2`", "o pipeline aplicado ao **lambda**", "`lambda => (xs >> morph x: x * 2)`"],
                ["`morph n: n given c otherwise 0`", "o `given` abre uma instrução", "`morph n: (n given c otherwise 0)`"],
                ["`distill a, v: a + v 0 / len(x)`", "o inicial é `0 / len(x)`", "divida **depois**: `(xs >> distill a, v: a + v 0) / len(x)`"],
                ["`spawn B().f()`", "`(spawn B()).f()`", "é o que se quer — e era o contrário antes"],
                ["`$\"{v[\\\"id\\\"]}\"`", "interpolação que não termina", "`$\"{v[\"id\"]}\"` — aspas normais dentro de `{}`"]]}},
            {"code": 'xs := [1, 2, 3]\n'
                     'dobro := lambda => (xs >> morph x: x * 2)\n'
                     'assert dobro() is [2, 4, 6]\n\n'
                     'sinais := xs >> morph n: (n given n bigger 1 otherwise 0)\n'
                     'assert sinais is [0, 2, 3]\n\n'
                     'media := (xs >> distill a, v: a + v 0) / len(xs)\n'
                     'assert media is 2.0\n\n'
                     'v := {"id": 7}\n'
                     'assert $"item {v["id"]}" is "item 7"\n'
                     'assert 7 ~/ 2 is 3\n'
                     'out "as seis formas certas rodam"', "lang": "df"},
            {"p": "Quando a dúvida é *como isto foi lido*, `dataforge tokens` e `dataforge ast` "
                  "respondem na hora — ver [tokens, ast, ir](/docs/cli/internos)."},
        ]}


def _na_linguagem():
    return {
        "href": "/docs/referencia/gramatica/na-linguagem",
        "title": "A gramática, de dentro de um programa",
        "description": "Arcane.Gramatica e dataforge gramatica — perguntar à linguagem como ela é.",
        "blocos": [
            {"p": "Um editor, um formatador ou um gerador de documentação escrito em DataForge "
                  "não precisa manter uma cópia da gramática: ele pergunta **à linguagem**. "
                  "`Arcane.Gramatica` expõe as produções, a precedência, os tokens e a "
                  "validação — com o lexer e o parser de verdade, e sem executar nada."},
            {"code": 'adopt Arcane.Gramatica as G\n\n'
                     'out len(G.producoes()), "producoes em", len(G.grupos()), "grupos"\n'
                     'out G.producao("guard")["ebnf"]\n\n'
                     '// Quem liga mais forte? A resposta sai da arvore.\n'
                     'assert G.raiz("1 + 2 * 3") is ["BinaryOp", "+"]\n\n'
                     '// O que o parser entendeu, instrucao por instrucao.\n'
                     'assert G.instrucoes("x := 1\\nout x") is ["Assignment", "OutStatement"]\n\n'
                     '// Validar o texto que um usuario digitou — sem executa-lo.\n'
                     'r := G.validar("x := (1 +")\n'
                     'assert not r["ok"]\n'
                     'out $"linha {r[\'erros\'][0][\'linha\']}: {r[\'erros\'][0][\'mensagem\']}"\n\n'
                     'assert "cycle" in G.palavras()["reservadas"]\n'
                     'assert "route" in G.palavras()["contextuais"]', "lang": "df"},
            {"table": {"head": ["Função", "Devolve"], "rows": [
                ["`producoes(grupo)`", "as produções — nome, EBNF, exemplo, nós, nota"],
                ["`producao(nome)`", "uma; o nome errado é recusado com sugestão"],
                ["`grupos()` / `ebnf(grupo)`", "os grupos; o texto EBNF"],
                ["`precedencia()`", "a escada, da mais fraca para a mais forte"],
                ["`raiz(expressao)`", "a classe e o operador na raiz da árvore"],
                ["`tokens(texto)`", "o que o lexer viu, com linha e coluna"],
                ["`instrucoes(texto)`", "a classe de cada instrução de topo"],
                ["`validar(texto)`", "`{ok, instrucoes, erros}` — sem executar"],
                ["`palavras()`", "as reservadas e as contextuais"]]}},
            {"h2": "No terminal"},
            {"code": "dataforge gramatica                      # os grupos\n"
                     "dataforge gramatica pipeline             # uma producao: EBNF, exemplo, nota\n"
                     "dataforge gramatica expressoes --ebnf    # o EBNF de um grupo\n"
                     "dataforge gramatica --ebnf               # a gramatica inteira\n"
                     "dataforge gramatica --precedencia        # quem liga mais forte\n"
                     "dataforge gramatica --json               # como dado", "lang": "bash"},
            {"callout": {"tipo": "dica", "titulo": "A garantia",
                         "texto": f"São {len(G.PRODUCOES)} produções, e cobrem as "
                                  "81 palavras reservadas — há teste exigindo que "
                                  "toda palavra reservada apareça em alguma. Uma palavra "
                                  "fora da gramática seria uma parte da linguagem que a "
                                  "documentação não descreve."}},
        ]}


PAGINAS = ([_pagina_do_grupo(*g) for g in G.GRUPOS]
           + [_precedencia(), _ambiguidades(), _na_linguagem()])
