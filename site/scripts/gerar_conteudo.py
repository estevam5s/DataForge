"""Gera as páginas .tsx a partir das definições em scripts/conteudo/.

As páginas do site são dados: uma lista de blocos por página. Este
script transforma esses dados nos componentes React que o Next compila.

Escrever .tsx à mão para 200 páginas produziria 200 variações do mesmo
markup. Aqui a moldura é uma só, e o que muda é o conteúdo.
"""
import importlib
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gerar_paginas import escrever  # noqa: E402

#: Os módulos de conteúdo, na ordem em que aparecem na navegação.
MODULOS = [
    "faq",
    "iot",
    "receitas_cli",
    "lavra_mais",
    "posse_mais",
    "concorrencia_extra",
    "dados_engenharia",
    "desktop",
    "api_rest_mais",
    "telegram_mais",
    "dominio_mais",
    "estruturas_mais",
    "reativo_mais",
    "ffi_mais",
    "compilador_mais",
    "runtime_mais",
    "observabilidade_mais",
    "partida_mais",
    "abi_mais",
    "ecossistema_mais",
    "concorrencia_mais",
    "primeiros_passos_avancado",
    "fundamentos_avancado",
    "big_o_avancado",
    "modulos_mais",
    "bibliotecas_mais",
    "dados_mais",
    "big_o",
    "modulos",
    "modulos_avancado",
    "bibliotecas",
    "bibliotecas_avancado",
    "projetos_tipos",
    "testes_avancado",
    "devops_avancado",
    "cli_avancado",
    "gramatica_doc",
    "seguranca_avancado",
    "plataforma_runtime",
    "dados_etl",
    "dados_quadro",
    "testes_api",
    "oop_avancado",
    "oop_magicos",
    "oop_meta",
    "exercicios",
    "lsp",
    "editor",
    "dados",
    "lago",
    "ml",
    "fluxo",
    "banco",
    "banco_sqlite",
    "banco_avancado",
    "telegram",
    "dominio_ddd",
    "reativo",
    "estruturas",
    "kiln_extra",
    "microservicos",
    "devops",
    "api_publica",
    "crucible_doc",
    "lavra",
    "tipos_nomeados",
    "tipos_genericos",
    "tipos_tuplas",
    "tipos_resultado",
    "tipos_mapa",
    "memoria_posse",
    "concorrencia_stm",
    "metaprogramacao",
    "ffi_c",
    "compilador_interno",
    "compilador_backend",
    "runtime_laco",
    "observabilidade",
    "partida_e_seguranca",
    "seguranca_informacao",
    "abi_e_alvos",
    "ecossistema",
    "fechamento",
    "plataforma",
    "vitrine",
    "versoes",
]


def main():
    total = 0
    for nome in MODULOS:
        try:
            modulo = importlib.import_module(f"conteudo.{nome}")
        except ModuleNotFoundError:
            print(f"  (pulando {nome}: ainda não existe)")
            continue
        for pagina in modulo.PAGINAS:
            # De onde veio, para o aviso no topo da pagina gerada poder
            # apontar o arquivo que a pessoa precisa abrir.
            pagina.setdefault("fonte", f"site/scripts/conteudo/{nome}.py")
            escrever(pagina)
            total += 1
            print(f"  {pagina['href']}")
    print(f"\n  {total} página(s) geradas")


if __name__ == "__main__":
    main()
