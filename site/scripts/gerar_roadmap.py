#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera `site/lib/roadmap-gerado.json` — o que a pagina /roadmap desenha.

A pagina precisa de quatro coisas, e **nenhuma delas pode ser escrita a
mao**:

1. **As dez fases** de um arquivo, do lexer a execucao. Elas saem de
   `Arcane.Percurso.fases()`, que e a mesma lista que `dataforge
   percurso` mede — nao uma copia.

2. **Os 41 componentes** do ecossistema, com o veredito de cada um
   (`existe`, `equivale`, `nao-existe`), o que ele e, o que ele e
   AQUI, e onde mora no disco. Saem de
   `Arcane.Ecossistema.componentes()`, que `conferir()` cobra contra o
   disco nas duas direcoes.

3. **O que nao existe**, de `o_que_nao_existe()`. Uma pagina de roadmap
   que so mostra o que ja foi feito e propaganda; o valor dela esta na
   metade que falta, e essa metade tem de vir do codigo — senao ela
   envelhece exatamente quando alguem implementa o item.

4. **Os 76 modulos**, agrupados, de `dados-gerados.json`.

─── Por que um arquivo proprio ────────────────────────────

`dados-gerados.json` ja existe e ja e lido pela home. Acrescentar o
ecossistema la dentro faria toda pagina que importa aquele arquivo
carregar 41 componentes que nao usa — e ele ja e o maior JSON do site.

─── A trava ───────────────────────────────────────────────

`tests/test_roadmap.py` roda este gerador e compara com o arquivo
versionado, como as outras onze travas de geracao. E ele confere que
todo `href` das trilhas existe em `nav.ts`: uma trilha que aponta para
uma pagina removida e pior que nenhuma trilha.

    python3 site/scripts/gerar_roadmap.py
    python3 site/scripts/gerar_roadmap.py --check
"""

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)

DESTINO = os.path.join(RAIZ, "site", "lib", "roadmap-gerado.json")
DADOS = os.path.join(RAIZ, "site", "lib", "dados-gerados.json")

from dataforge.stdlib import get_module  # noqa: E402


#: Os grupos da galaxia 3D, e a ordem em que ela os desenha.
#:
#: A mesma divisao da landing (`site/components/landing/Arcane.tsx`).
#: Duas divisoes do mesmo conjunto divergiriam no primeiro modulo novo
#: — e um modulo que cai em "Outros" nas duas telas e um modulo que
#: ninguem colocou em lugar nenhum.
GRUPOS_DE_MODULO = [
    ("Núcleo", ["math", "text", "io", "regex", "collections", "functional",
                "iter", "decimal", "bytes", "algoritmos"]),
    ("Frameworks", ["kiln", "vitrine", "telegram", "lavra", "crucible",
                    "forge", "api"]),
    ("Dados", ["quadro", "data", "analytics", "cortex", "lago", "pipeline",
               "qualidade", "stream"]),
    ("Formatos", ["serialization", "excel", "archive", "database", "html"]),
    ("Sistema e rede", ["os", "process", "time", "http", "web", "async",
                        "concurrent", "ponte", "malha", "rede", "email", "url",
                        "github"]),
    ("Qualidade", ["test", "bench", "logging", "crypto", "seguranca",
                   "politica", "chaves", "deteccao", "privacidade", "integridade",
                   "observar", "color", "meta", "cli", "eventos"]),
    ("Objetos", ["reflexo", "objetos", "injecao", "padroes"]),
    ("Domínio", ["dominio", "reativo", "estrutura"]),
    ("Tipos", ["tipos", "resultado"]),
    ("Memória", ["posse", "memoria"]),
    ("Concorrência", ["laco", "stm", "perfil"]),
    ("Metaprogramação", ["macro", "dsl"]),
    ("Baixo nível", ["c", "compilador"]),
    ("IoT", ["iot"]),
    ("Partida", ["inicio", "capacidade"]),
    ("Distribuição", ["abi", "alvo", "evolucao"]),
    ("A própria implementação", ["ecossistema", "principios", "percurso",
                                 "gramatica"]),
]


def _modulos():
    """Os modulos agrupados, com nome oficial, descricao e tamanho."""
    with open(DADOS, encoding="utf-8") as f:
        todos = json.load(f)["modulos"]

    reivindicados = set()
    grupos = []
    for rotulo, chaves in GRUPOS_DE_MODULO:
        itens = []
        for chave in chaves:
            if chave not in todos:
                continue
            reivindicados.add(chave)
            m = todos[chave]
            itens.append({
                "chave": chave,
                "nome": m.get("nome", chave),
                "desc": (m.get("desc") or "").split(".")[0][:150],
                "simbolos": m.get("simbolos") or len(m.get("funcoes") or []),
            })
        if itens:
            grupos.append({"rotulo": rotulo, "modulos": itens})

    # Quem nenhum grupo reivindicou. Vazio e o estado esperado, e a
    # trava do teste cobra isso: um modulo em "Outros" e um modulo que
    # ninguem colocou em lugar nenhum.
    sobrando = sorted(set(todos) - reivindicados)
    if sobrando:
        grupos.append({"rotulo": "Outros", "modulos": [
            {"chave": c, "nome": todos[c].get("nome", c),
             "desc": (todos[c].get("desc") or "").split(".")[0][:150],
             "simbolos": todos[c].get("simbolos")
             or len(todos[c].get("funcoes") or [])}
            for c in sobrando]})
    return grupos, sobrando


def construir():
    percurso = get_module("Arcane.Percurso")
    eco = get_module("Arcane.Ecossistema")

    fases = [dict(f) for f in percurso["fases"]()]
    componentes = [dict(c) for c in eco["componentes"]()]
    for c in componentes:
        # 'no_disco' e o que 'conferir()' achou; a pagina mostra 'onde',
        # e a divergencia entre os dois e justamente o que o comando
        # 'dataforge ecossistema' existe para acusar. Aqui ela nao
        # entra: um JSON do site nao e o lugar de reportar isso.
        c.pop("no_disco", None)

    grupos_de_modulo, sobrando = _modulos()

    return {
        "fases": fases,
        "componentes": componentes,
        "gruposDeComponente": [dict(g) for g in eco["grupos"]()],
        "naoExiste": [dict(x) if isinstance(x, dict) else {"item": str(x)}
                      for x in eco["o_que_nao_existe"]()],
        "numeros": dict(eco["numeros"]()),
        "modulos": grupos_de_modulo,
        "semGrupo": sobrando,
    }


def main():
    dados = construir()
    texto = json.dumps(dados, ensure_ascii=False, indent=2,
                       sort_keys=True) + "\n"

    if "--check" in sys.argv:
        if not os.path.isfile(DESTINO):
            print("roadmap-gerado.json nao existe; rode o gerador")
            return 1
        with open(DESTINO, encoding="utf-8") as f:
            if f.read() != texto:
                print("roadmap-gerado.json esta defasado; rode o gerador")
                return 1
        print("roadmap-gerado.json em dia")
        return 0

    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(texto)
    n = dados["numeros"]
    print(f"gerado: {DESTINO}")
    print(f"  {len(dados['fases'])} fases, {n['componentes']} componentes "
          f"({n['existem']} existem, {n['equivalem']} equivalem, "
          f"{n['nao_existem']} nao), {n['modulos']} modulos")
    if dados["semGrupo"]:
        print(f"  AVISO: sem grupo: {dados['semGrupo']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
