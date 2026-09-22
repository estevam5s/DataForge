#!/usr/bin/env python3
"""Extrai do repositorio DataForge os dados que o site usa.

Roda a partir de site/:  python3 scripts/gerar_dados.py

Escreve lib/dados-gerados.json com as assinaturas reais dos modulos
Arcane, os exercicios com codigo-fonte, as palavras reservadas e as
funcoes embutidas. E a fonte unica desses numeros no site — as paginas
nunca devem repetir um total escrito a mao.
"""

import inspect
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(AQUI)
REPO = os.path.dirname(SITE)
sys.path.insert(0, REPO)

from dataforge.stdlib import get_module, list_modules          # noqa: E402
from dataforge import __version__
from dataforge.tokens import KEYWORDS                          # noqa: E402


#: A tabela vive em 'dataforge/stdlib/catalogo.py'. Ela ja esteve
#: escrita aqui tambem, e as duas copias divergiram.
from dataforge.stdlib.catalogo import (DESCRICOES, assinatura_fixa,  # noqa: E402
                                       nome_curto)



def assinatura(valor):
    """Devolve '(a, b)' para funcao, ou o rotulo do que nao e chamavel."""
    if isinstance(valor, dict):
        return "{ … }"          # sub-namespace, como Math.random
    if not callable(valor):
        return ""               # constante, como Math.PI
    if inspect.isbuiltin(valor):
        # Funcao escrita em C. Duas razoes para NAO perguntar ao
        # CPython aqui, e a tabela de 'catalogo.py' existe para as duas:
        #
        # 1. a resposta muda com a versao. 'math.hypot' nao tinha
        #    assinatura no 3.13 e ganhou uma no 3.14 — o arquivo gerado
        #    passava a depender de QUEM rodou o gerador, e o job do CI
        #    que compara o versionado com o gerado reprovava sozinho.
        # 2. o nome vem em ingles e do CPython ('coordinates'), e a
        #    documentacao em Markdown ja mostra o declarado
        #    ('coordenadas'). Duas respostas para a mesma pergunta.
        fixa = assinatura_fixa(getattr(valor, "__name__", ""))
        if fixa:
            return fixa
    try:
        params = list(inspect.signature(valor).parameters)
    except (TypeError, ValueError):
        return "(…)"
    return "(" + ", ".join(params) + ")"


def coletar_modulos():
    modulos, vistos = {}, set()
    for nome in sorted(set(list_modules())):
        mod = get_module(nome)
        if not isinstance(mod, dict):
            continue
        oficial = mod.get("__name__", nome)
        if oficial in vistos:
            continue
        vistos.add(oficial)

        simbolos = []
        for chave in sorted(k for k in mod if not k.startswith("__")):
            valor = mod[chave]
            simbolos.append({
                "nome": chave,
                "sig": assinatura(valor),
                # 'const' e 'grupo' aparecem na doc com marcacao propria
                "tipo": ("grupo" if isinstance(valor, dict)
                         else "funcao" if callable(valor) else "const"),
            })

        chave_curta = oficial.split(".")[-1].lower()
        modulos[chave_curta] = {
            "nome": oficial,
            "desc": DESCRICOES.get(oficial, ("", ""))[0],
            "curto": nome_curto(oficial),
            "funcoes": simbolos,
        }
    return modulos


def coletar_exercicios():
    base = os.path.join(REPO, "exercicios")
    saida = {}
    for modulo in sorted(os.listdir(base)):
        pasta = os.path.join(base, modulo)
        if not os.path.isdir(pasta):
            continue
        itens = []
        for arq in sorted(f for f in os.listdir(pasta)
                          if f.endswith(".df") and re.match(r"^\d{3}_", f)):
            caminho = os.path.join(pasta, arq)
            codigo = open(caminho, encoding="utf-8").read()
            num = arq.split("_")[0]
            titulo = enunciado = ""
            for linha in codigo.splitlines()[:4]:
                if linha.startswith("// Exercicio") and "—" in linha:
                    titulo = linha.split("—", 1)[1].strip()
                elif linha.startswith("// Enunciado:"):
                    enunciado = linha.split(":", 1)[1].strip()
            itens.append({
                "num": num,
                "titulo": titulo,
                "enunciado": enunciado,
                "arquivo": arq,
                "temDoc": os.path.exists(caminho[:-3] + ".md"),
                "codigo": codigo,
            })
        if itens:
            saida[modulo] = itens
    return saida


def coletar_builtins():
    """Lista as embutidas, agrupadas pelos marcadores internos do registro.

    A lista de nomes vem de get_builtins() — essa e a verdade. O arquivo
    e lido apenas para saber em que grupo cada nome foi declarado, pelas
    linhas '# \u2500\u2500 Nome \u2500\u2500'. Assim as constantes (PI, TAU, MAX_INT)
    entram junto com as funcoes, em vez de ficarem de fora.
    """
    from dataforge.builtins import get_builtins
    oficiais = set(get_builtins())

    fonte = open(os.path.join(REPO, "dataforge", "builtins.py"),
                 encoding="utf-8").read()
    linhas = fonte.splitlines()
    inicio = next(i for i, l in enumerate(linhas)
                  if l.startswith("def get_builtins"))

    grupos, atual = {}, "Gerais"
    for linha in linhas[inicio:]:
        marca = re.match(r"\s*#\s*\u2500+\s*(.+?)\s*\u2500+\s*$", linha)
        if marca:
            atual = marca.group(1).strip()
            grupos.setdefault(atual, [])
            continue
        m = re.match(r'\s*["\'](\w+)["\']\s*:', linha)
        if m and m.group(1) in oficiais:
            grupos.setdefault(atual, []).append(m.group(1))

    resultado = {g: sorted(set(f)) for g, f in grupos.items() if f}
    capturadas = {n for f in resultado.values() for n in f}
    faltando = oficiais - capturadas
    if faltando:
        resultado.setdefault("Gerais", []).extend(sorted(faltando))
        resultado["Gerais"] = sorted(set(resultado["Gerais"]))
    return resultado


def contar_o_repositorio():
    """Os números que a landing anuncia, contados aqui.

    Estavam escritos à mão em `Aprender.tsx` — `378 testes`,
    `190 exercícios`, `286 arquivos .df` — sob a legenda "números
    conferidos na última execução da suíte". Nenhum dos quatro era
    verdade: a suíte tinha 2368 testes e os exercícios eram 231.

    Uma legenda que afirma verificação sobre um número escrito à mão é
    pior que não ter número: quem lê confia.

    Os testes são contados pelos `def test_`, e não pela execução do
    pytest — contá-los de verdade exigiria rodar a suíte dentro de um
    gerador de dados do site. É um limite e está dito no rótulo:
    "funções de teste".
    """
    import re

    def contar(padrao, dentro):
        total = 0
        for raiz, pastas, nomes in os.walk(os.path.join(REPO, dentro)):
            pastas[:] = [d for d in pastas
                         if d not in {"node_modules", "__pycache__",
                                      "forge_modules", ".git"}]
            for nome in nomes:
                if re.fullmatch(padrao, nome):
                    total += 1
        return total

    funcoes_de_teste = 0
    for raiz, _, nomes in os.walk(os.path.join(REPO, "tests")):
        for nome in nomes:
            if nome.endswith(".py"):
                with open(os.path.join(raiz, nome), encoding="utf-8") as f:
                    funcoes_de_teste += len(
                        re.findall(r"^def test_", f.read(), re.M))

    arquivos_df = 0
    for dentro in ("exercicios", "examples", "projetos", "packages",
                   "dataforge", "doc"):
        arquivos_df += contar(r".*\.df", dentro)

    return {
        "testes": funcoes_de_teste,
        "exemplos": contar(r".*\.df", "examples"),
        "arquivosDf": arquivos_df,
    }


def numeros_do_mundo():
    """Estrelas, release e downloads — o instantâneo de build.

    O site é um **export estático**: não há servidor para consultar
    nada. Estes números existem para a página abrir já com um valor no
    lugar, e o navegador atualiza depois (`site/lib/numeros.ts`), que é
    o único jeito de eles não envelhecerem entre um deploy e outro.

    Sem rede, devolve o que der — um número ausente vira `None`, e o
    componente mostra o traço. Falhar aqui deixaria o site sem build
    por causa de uma estatística.
    """
    import json as _json
    import urllib.error
    import urllib.request

    def pegar(url, dados=None, cabecalhos=None):
        pedido = urllib.request.Request(
            url, data=dados,
            headers={"User-Agent": "dataforge-site", **(cabecalhos or {})})
        try:
            with urllib.request.urlopen(pedido, timeout=8) as r:
                return _json.load(r)
        except (urllib.error.URLError, TimeoutError, ValueError,
                urllib.error.HTTPError):
            return None

    # O que o arquivo ja tem. A API da loja e INTERMITENTE: a mesma
    # consulta responde ora com 'statistics', ora sem — medido, tres
    # chamadas seguidas, duas vazias. Um build que caisse na vazia
    # apagaria um numero que o site ja mostrava.
    #
    # Entao o padrao nao e None: e o ultimo valor conhecido. So um
    # valor NOVO substitui um valor antigo.
    anterior = {}
    try:
        with open(os.path.join(SITE, "lib", "dados-gerados.json"),
                  encoding="utf-8") as f:
            anterior = _json.load(f).get("mundo") or {}
    except (OSError, ValueError):
        pass

    saida = {chave: anterior.get(chave) for chave in
             ("estrelas", "versao", "publicado", "baixados", "instalacoes")}

    repo = pegar("https://api.github.com/repos/estevam5s/DataForge")
    if repo:
        if repo.get("stargazers_count") is not None:
            saida["estrelas"] = repo["stargazers_count"]

    release = pegar(
        "https://api.github.com/repos/estevam5s/DataForge/releases/latest")
    if release:
        saida["versao"] = release.get("tag_name") or saida["versao"]
        saida["publicado"] = ((release.get("published_at") or "")[:10]
                              or saida["publicado"])
        saida["baixados"] = sum(a.get("download_count", 0)
                                for a in release.get("assets", []))

    corpo = _json.dumps({
        "filters": [{"criteria": [
            {"filterType": 7, "value": "EstevamSouza.dataforge-language"}],
            "pageSize": 1}],
        "flags": 914}).encode()
    loja = pegar(
        "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery",
        corpo,
        {"Content-Type": "application/json",
         "Accept": "application/json;api-version=7.2-preview.1"})
    if loja:
        try:
            estatisticas = loja["results"][0]["extensions"][0]["statistics"]
            por_nome = {e["statisticName"]: e["value"] for e in estatisticas}
            # 'install' e o numero que a loja mostra na pagina, e ela so
            # o publica depois de algum tempo; ate la existe so o
            # 'downloadCount'. Preferir o primeiro e cair no segundo faz
            # o site mostrar um numero verdadeiro desde o primeiro dia.
            bruto = por_nome.get("install", por_nome.get("downloadCount"))
            if bruto is not None:
                saida["instalacoes"] = int(bruto)
        except (KeyError, IndexError, TypeError, ValueError):
            pass

    return saida


def main():
    modulos = coletar_modulos()
    builtins = coletar_builtins()
    dados = {
        "modulos": modulos,
        "exercicios": coletar_exercicios(),
        "palavras": sorted(KEYWORDS),
        "builtins": builtins,
        "totalBuiltins": sum(len(v) for v in builtins.values()),
        "contagem": contar_o_repositorio(),
        "mundo": numeros_do_mundo(),
        # A versao da LINGUAGEM, que nao e a mesma coisa que a tag do
        # ultimo release ('mundo.versao'): a tag so muda quando alguem
        # cria a tag, e entre um release e o proximo as duas divergem.
        #
        # O rodape e a barra lateral escreviam "1.0.0" a mao, e ficaram
        # dizendo 1.0.0 depois de a linguagem virar 1.1.0. O numero
        # aparece em toda pagina do site — e uma das coisas mais
        # visiveis que havia para envelhecer calado.
        "versaoDaLinguagem": __version__,
    }

    destino = os.path.join(SITE, "lib", "dados-gerados.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)

    total_simbolos = sum(len(m["funcoes"]) for m in modulos.values())
    total_exerc = sum(len(v) for v in dados["exercicios"].values())
    print(f"lib/dados-gerados.json escrito")
    print(f"  {len(modulos)} módulos, {total_simbolos} símbolos")
    print(f"  {len(dados['exercicios'])} módulos de exercício, {total_exerc} exercícios")
    print(f"  {len(dados['palavras'])} palavras reservadas")
    print(f"  {dados['totalBuiltins']} embutidas em {len(builtins)} grupos")
    c = dados["contagem"]
    print(f"  {c['testes']} funcoes de teste, {c['exemplos']} exemplos, "
          f"{c['arquivosDf']} arquivos .df")
    m = dados["mundo"]
    print(f"  {m['estrelas']} estrelas, release {m['versao']}, "
          f"{m['baixados']} baixados, {m['instalacoes']} instalacoes")


if __name__ == "__main__":
    main()
