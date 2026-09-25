# -*- coding: utf-8 -*-
"""As páginas dos exercícios — geradas dos próprios arquivos .df.

Escritas à mão, elas pararam no módulo 23: os módulos 24 (banco de
dados), 25 (Crucible) e 26 (complexidade) existiam no repositório e não
apareciam no site. E o índice ainda anunciava "os vinte módulos" e
"todos os 180" quando já eram 26 e 216.

Nada aqui é digitado duas vezes: o título e o enunciado saem das duas
primeiras linhas de comentário de cada exercício, que é onde eles já
estavam.
"""

import glob
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
EXERCICIOS = os.path.join(RAIZ, "exercicios")

#: O assunto de cada módulo, para a página de índice. O que o nome da
#: pasta não diz — 'controle-fluxo' não explica o que se aprende ali.
ASSUNTOS = {
    "01-fundamentos": "tipos, operadores, precedência, conversão e anotações",
    "02-controle-fluxo": "given/orif/otherwise, ternário, match e guardas",
    "03-colecoes": "cluster e vault, fatias, spread e compreensões",
    "04-strings": "interpolação, métodos de texto, formatação e regex",
    "05-acoes": "parâmetros, padrões, retorno, closures e recursão",
    "06-blueprints": "campos, métodos, herança, traits e records",
    "07-erros": "monitor/handle/ensure, trigger, retry e defer",
    "08-pipelines": "sift, morph, distill e composição",
    "09-modulos": "adopt, relay, seleção e apelidos",
    "10-avancado": "decoradores, generators, threads e canais",
    "11-tipos-e-checagem": "anotações, o analisador estático e generics",
    "12-records-e-enums": "imutabilidade, 'with' e enums com valor",
    "13-desestruturacao": "cluster, vault, rest e troca de variáveis",
    "14-pattern-matching": "point, when, tipos, sequências e vaults",
    "15-streams-e-generators": "stream action, emit, take e sequências infinitas",
    "16-modulos-e-projetos": "forge.toml, pacotes e organização",
    "17-tempo-e-sistema": "datas, durações, ambiente e processos",
    "18-dados-e-persistencia": "JSON, CSV, SQLite e serialização",
    "19-concorrencia": "threads, canais, tarefas e paralelismo",
    "20-projetos-finais": "programas completos, de ponta a ponta",
    "21-oop-avancado": "propriedades, estáticos, operadores, SOLID",
    "22-web-kiln": "rotas, respostas, templates e estáticos",
    "23-dados-e-planilhas": "frames, agregação e .xlsx",
    "24-banco-de-dados": "Forge: conexão, consultas, transações e ORM",
    "25-testes-crucible": "suítes, matchers, fixtures e dublês",
    "26-complexidade": "Big-O, memoização e custo de estrutura",
    "27-ponte-python": "adopt Python.*: numpy, pandas e o que vem junto",
    "28-vitrine": "painéis e aplicações de dados sem escrever HTML",
    "29-banco-e-crud": "transações, upsert, busca textual e paginação",
    "30-tempo-real": "upload, SSE e WebSocket no Kiln",
    "31-qualidade": "check, lint, cobertura e o que o CI cobra",
    "32-microservicos": "Arcane.Malha: retry, disjuntor, rastro e saga",
    "33-lavra": "esquema, consulta, lote contra o N+1, servidor e federação",
    "34-binario-e-rede": "dados binários, TCP/UDP/DNS, eventos, CLI, e-mail e HTML",
    # Do 35 em diante a coluna ficava VAZIA no índice, e a descrição de
    # cada página saía "3 exercícios: ." — é o texto do resultado de busca
    # e do cartão de compartilhamento. Há teste cobrando um por módulo.
    "35-paralelismo": "vários núcleos de verdade, o que atravessa para outro processo",
    "36-quadro-e-dados": "o quadro de dados e os seis verbos do pipeline",
    "37-oop-sistema": "contratos, modificadores, sobrecarga, metaclasse, DI e padrões",
    "38-tipos": "alias, união, refinamento, opaco, generics, tuplas e posse",
    "39-concorrencia-avancada": "memória transacional, CAS e estruturas sem trava",
    "40-metaprogramacao": "comptime, macros, DSL e plugin do check",
    "41-ffi-nativo": "chamar C: bibliotecas, ponteiros e callbacks",
    "42-compilador": "HIR, MIR e o que a análise de fluxo prova",
    "43-backend": "SSA, o nó phi e a otimização que foi medida",
    "44-runtime": "laço de eventos, escalonador e fibras",
    "45-observabilidade": "percentis, significância e o coletor sob controle",
    "46-partida": "as fases da partida, a pilha e a fronteira de capacidade",
    "47-abi-e-alvos": "a superfície como contrato e o alvo como restrição",
    "48-ecossistema": "o mapa conferido e os princípios que se medem",
    "49-decimal-e-padroes": "dinheiro exato com Decimal e o padrão acusado antes de rodar",
    "50-dominio": "valor, entidade, agregado, evento, regra e unidade de trabalho",
    "51-reativo": "sinal, derivado, efeito, observável e o losango",
    "52-estruturas": "layout binário com nome, janela sem cópia e ponteiro",
    "53-regex-avancado": "grupos nomeados, âncoras, troca que calcula e risco",
    "54-erros": "as famílias de erro, a falha como valor e o que o monitor não pega",
    "55-oop-magicos": "métodos mágicos: texto, conta, coleção, ordem e iteração",
    "56-telegram": "bots testados sem rede: comandos, botões, estado e webhook",
    "57-vitrine-painel": "painéis com layout, gráficos, grade, cache e sessão",
    "58-iot": "Arduino pelo Firmata: sensores, relé, escala e sketch",
    "59-tipos-literais": "tipos literais e o método que não existe, acusado antes",
}


def _n_exercicios(n):
    """'1 exercício', '12 exercícios' — a página dizia '1 exercícios'."""
    return f"{n} exercício" if n == 1 else f"{n} exercícios"


#: Os níveis e as trilhas. O MESMO arquivo que o README dos exercícios lê
#: ('tools/gerar_indice_exercicios.py'): duas listas divergiriam no
#: primeiro módulo novo.
def _trilhas():
    import json
    with open(os.path.join(EXERCICIOS, "trilhas.json"), encoding="utf-8") as f:
        return json.load(f)


def _cabecalho(caminho):
    """(numero, titulo, enunciado) das duas primeiras linhas de comentário."""
    numero = titulo = enunciado = ""
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha.startswith("//"):
                if linha:
                    break
                continue
            texto = linha.lstrip("/").strip()
            m = re.match(r"Exercicio\s+(\d+)\s+[—-]\s+(.+)", texto)
            if m:
                numero, titulo = m.group(1), m.group(2)
            elif texto.lower().startswith("enunciado:"):
                enunciado = texto.split(":", 1)[1].strip()
            if numero and enunciado:
                break
    return numero, titulo, enunciado


def _corpo(caminho):
    """O .df sem as duas linhas de cabeçalho, que a página já mostra."""
    linhas = open(caminho, encoding="utf-8").read().split("\n")
    i = 0
    while i < len(linhas) and (
            linhas[i].strip().startswith("//") or not linhas[i].strip()):
        texto = linhas[i].strip().lstrip("/").strip()
        if texto and not (re.match(r"Exercicio\s+\d+\s+[—-]", texto)
                          or texto.lower().startswith("enunciado:")):
            break
        i += 1
    return "\n".join(linhas[i:]).strip()


#: Um bloco de código no .md, com a linguagem que a cerca declara.
_CERCA = re.compile(r"^```(\w*)\s*$")
_TABELA = re.compile(r"^\|(.+)\|\s*$")
_SEPARADOR = re.compile(r"^\|[\s:|-]+\|\s*$")


def _markdown_para_blocos(texto, nivel_base=3):
    """Converte o .md explicativo para os blocos que o site renderiza.

    Não é um parser de Markdown: é o subconjunto que estes arquivos
    usam — título, parágrafo, cerca de código, tabela e lista. O que
    não casar com nada vira parágrafo, que é o pior caso aceitável:
    o texto aparece, só sem a formatação.

    A alternativa era linkar para o arquivo no GitHub, e aí a
    explicação de 13 módulos de exercício simplesmente não estaria no
    site — que é o que acontecia.
    """
    blocos = []
    linhas = texto.split("\n")
    i = 0
    paragrafo = []

    def fechar():
        if paragrafo:
            blocos.append({"p": " ".join(paragrafo).strip()})
            paragrafo.clear()

    while i < len(linhas):
        linha = linhas[i]
        nua = linha.strip()

        cerca = _CERCA.match(nua)
        if cerca:
            fechar()
            lang = cerca.group(1) or "text"
            corpo = []
            i += 1
            while i < len(linhas) and not linhas[i].strip().startswith("```"):
                corpo.append(linhas[i])
                i += 1
            i += 1
            mapa = {"dataforge": "df", "df": "df", "bash": "bash", "sh": "bash",
                    "json": "json", "toml": "toml", "sql": "sql", "text": "text",
                    "yaml": "yaml", "javascript": "javascript",
                    # A linguagem de consulta do Lavra NAO e DataForge.
                    # Marcá-la como tal faria o verificador tentar
                    # compilá-la, e reprovar um exemplo correto.
                    "lavra": "lavra"}
            blocos.append({"code": "\n".join(corpo).rstrip(),
                           "lang": mapa.get(lang, "text")})
            continue

        if nua.startswith("#"):
            fechar()
            nivel = len(nua) - len(nua.lstrip("#"))
            titulo = nua.lstrip("#").strip()
            # '##' do arquivo vira o nível abaixo do título do exercício.
            chave = "h3" if nivel_base + nivel - 2 <= 3 else "h4"
            if chave == "h4":
                blocos.append({"p": f"**{titulo}**"})
            else:
                blocos.append({"h3": titulo})
            i += 1
            continue

        if _TABELA.match(nua) and i + 1 < len(linhas) and _SEPARADOR.match(
                linhas[i + 1].strip()):
            fechar()
            cabeca = [c.strip() for c in nua.strip("|").split("|")]
            i += 2
            corpo = []
            while i < len(linhas) and _TABELA.match(linhas[i].strip()):
                corpo.append([c.strip()
                              for c in linhas[i].strip().strip("|").split("|")])
                i += 1
            blocos.append({"table": {"head": cabeca, "rows": corpo}})
            continue

        if nua.startswith(("- ", "* ")):
            fechar()
            itens = []
            while i < len(linhas) and linhas[i].strip().startswith(("- ", "* ")):
                itens.append(linhas[i].strip()[2:].strip())
                i += 1
            blocos.append({"list": itens})
            continue

        if not nua:
            fechar()
            i += 1
            continue

        paragrafo.append(nua)
        i += 1

    fechar()
    return blocos


def _explicacao(caminho_df):
    """Os blocos do .md ao lado, sem o título e sem o 'Enunciado'."""
    caminho = caminho_df[:-3] + ".md"
    if not os.path.isfile(caminho):
        return []
    texto = open(caminho, encoding="utf-8").read()
    # Fora o '# Exercicio N — ...' e a secao '## Enunciado', que a
    # pagina ja mostrou logo acima.
    texto = re.sub(r"^#\s+[^\n]*\n", "", texto)
    texto = re.sub(r"##\s+Enunciado\s*\n.*?(?=\n##\s|\Z)", "", texto,
                   flags=re.S)
    return _markdown_para_blocos(texto.strip())


def _modulos():
    saida = []
    for pasta in sorted(glob.glob(os.path.join(EXERCICIOS, "*"))):
        nome = os.path.basename(pasta)
        if not os.path.isdir(pasta) or not nome[:2].isdigit():
            continue
        arquivos = sorted(
            a for a in glob.glob(os.path.join(pasta, "*.df"))
            if os.path.basename(a)[0].isdigit())
        if arquivos:
            saida.append((nome, [_cabecalho(a) for a in arquivos], arquivos))
    return saida


#: O nome que a pessoa lê — COPIADO de 'site/lib/nav.ts', e há um teste
#: comparando os dois: dois rótulos para a mesma página fazem a barra
#: lateral e o título da aba discordarem.
#:
#: O da PASTA não serve. Ele não tem acento e perde as maiúsculas dos
#: nomes próprios: saíam "03 · Colecoes", "05 · Acoes", "10 · Avancado"
#: e "22 · Web kiln" no título da aba, na busca e na navegação.
TITULOS = {
    "01-fundamentos": "Fundamentos",
    "02-controle-fluxo": "Controle de fluxo",
    "03-colecoes": "Coleções",
    "04-strings": "Textos",
    "05-acoes": "Ações",
    "06-blueprints": "Blueprints",
    "07-erros": "Erros",
    "08-pipelines": "Pipelines",
    "09-modulos": "Módulos",
    "10-avancado": "Avançado",
    "11-tipos-e-checagem": "Tipos e checagem",
    "12-records-e-enums": "Records e enums",
    "13-desestruturacao": "Desestruturação",
    "14-pattern-matching": "Pattern matching",
    "15-streams-e-generators": "Streams",
    "16-modulos-e-projetos": "Módulos e projetos",
    "17-tempo-e-sistema": "Tempo e sistema",
    "18-dados-e-persistencia": "Persistência",
    "19-concorrencia": "Concorrência",
    "20-projetos-finais": "Projetos finais",
    "21-oop-avancado": "OOP avançado",
    "22-web-kiln": "Web com Kiln",
    "23-dados-e-planilhas": "Dados e planilhas",
    "24-banco-de-dados": "Banco de dados",
    "25-testes-crucible": "Testes com Crucible",
    "26-complexidade": "Complexidade",
    "27-ponte-python": "Ponte para o Python",
    "28-vitrine": "Vitrine",
    "29-banco-e-crud": "Banco e CRUD",
    "30-tempo-real": "Tempo real",
    "31-qualidade": "Qualidade",
    "32-microservicos": "Microserviços",
    "33-lavra": "Lavra",
    "34-binario-e-rede": "Binário e rede",
    "35-paralelismo": "Paralelismo",
    "36-quadro-e-dados": "Quadro e dados",
    "37-oop-sistema": "OOP como sistema",
    "38-tipos": "Sistema de tipos",
    "39-concorrencia-avancada": "Concorrência avançada",
    "40-metaprogramacao": "Metaprogramação",
    "41-ffi-nativo": "FFI e nativo",
    "42-compilador": "Dentro do compilador",
    "43-backend": "Backend e otimização",
    "44-runtime": "Runtime e laço de eventos",
    "45-observabilidade": "Observabilidade e memória",
    "46-partida": "Partida, pilha e capacidade",
    "47-abi-e-alvos": "Superfície e alvos",
    "48-ecossistema": "Ecossistema e design",
    "49-decimal-e-padroes": "Decimal exato e padrões",
    "50-dominio": "Domínio e DDD",
    "51-reativo": "Programação reativa",
    "52-estruturas": "Estruturas e ponteiros",
    "53-regex-avancado": "Regex avançado",
    "54-erros": "Erros e famílias",
    "55-oop-magicos": "Métodos mágicos",
    "56-telegram": "Bots de Telegram",
    "57-vitrine-painel": "Vitrine — o painel",
    "58-iot": "IoT e Arduino",
    "59-tipos-literais": "Tipos literais",
}


def _rotulo(nome):
    """'01-fundamentos' -> '01 · Fundamentos'."""
    num, resto = nome.split("-", 1)
    return f"{num} · {TITULOS.get(nome, resto.replace('-', ' ').capitalize())}"


MODULOS = _modulos()
TOTAL = sum(len(itens) for _, itens, _ in MODULOS)

#: Os módulos que trazem um .md explicativo ao lado de cada .df.
COM_EXPLICACAO = sorted(
    nome for nome, _, arquivos in MODULOS
    if all(os.path.isfile(a[:-3] + ".md") for a in arquivos))


def _nivel_de(nome):
    """O nível do módulo, pelo número ('35-paralelismo' -> 'Aplicações')."""
    for nivel in _trilhas()["niveis"]:
        if nome[:2] in nivel["modulos"]:
            return nivel["titulo"]
    return ""


def _link_do_modulo(numero):
    """'35' -> '[35](/docs/exercicios/35-paralelismo)'."""
    nome = next(n for n, _, _ in MODULOS if n[:2] == numero)
    return f"[{numero}](/docs/exercicios/{nome})"


def _pagina_indice():
    por_numero = {nome[:2]: (nome, itens) for nome, itens, _ in MODULOS}
    dados = _trilhas()

    faixa = ""
    if COM_EXPLICACAO:
        nums = [n[:2] for n in COM_EXPLICACAO]
        faixa = (f"Os módulos **{nums[0]} a {nums[-1]}** trazem um arquivo `.md` "
                 "ao lado de cada `.df`, com enunciado, conceitos, saída esperada "
                 "e sugestões para experimentar.")

    # As trilhas: por objetivo, e não por número. Cinquenta e nove módulos
    # numa lista só não dizem por onde começar.
    trilhas = [[t["quero"][:1].upper() + t["quero"][1:],
                " → ".join(_link_do_modulo(m) for m in t["modulos"])]
               for t in dados["trilhas"]]

    # Os módulos, agrupados por nível. Era uma tabela de 59 linhas, e a
    # coluna de assunto ficava vazia do 35 em diante.
    por_nivel = []
    for nivel in dados["niveis"]:
        numeros = [m for m in nivel["modulos"] if m in por_numero]
        exercicios = sum(len(por_numero[m][1]) for m in numeros)
        por_nivel.append({"h3": f"{nivel['titulo']} · {len(numeros)} módulos, "
                                f"{_n_exercicios(exercicios)}"})
        por_nivel.append({"p": nivel["texto"]})
        por_nivel.append({"table": {
            "head": ["Módulo", "Exercícios", "Assunto"],
            "rows": [[f"[**{_rotulo(por_numero[m][0])}**]"
                      f"(/docs/exercicios/{por_numero[m][0]})",
                      str(len(por_numero[m][1])),
                      ASSUNTOS.get(por_numero[m][0], "")]
                     for m in numeros]}})

    return {
        "href": "/docs/exercicios",
        "title": "Exercícios",
        "description": f"{TOTAL} exercícios em {len(MODULOS)} módulos, "
                       "cada um verificando o próprio resultado.",
        "blocos": [
            {"h2": "Como funcionam"},
            {"p": "Cada exercício **verifica o próprio resultado com `assert`** — se ele roda sem erro, está correto. Não há gabarito separado: o código é a resposta e o teste ao mesmo tempo."},
            {"code": f"""python3 exercicios/run_all.py          # todos os {TOTAL}
python3 exercicios/run_all.py 14       # só o módulo 14
python3 exercicios/run_all.py 03 07    # módulos 03 e 07

dataforge run exercicios/01-fundamentos/001_ola_mundo.df""", "lang": "bash"},
            *([{"p": faixa}] if faixa else []),
            {"callout": {"tipo": "nota", "titulo": "Eles rodam a cada mudança",
                         "texto": f"Os {TOTAL} são executados na suíte do repositório. Um exercício que quebrasse com uma mudança na linguagem apareceria no mesmo instante — é por isso que os exemplos desta documentação podem ser citados sem medo."}},
            {"h2": "Como praticar"},
            {"list": [
                "**Leia o enunciado e tente antes.** As duas primeiras linhas de cada `.df` dizem o que fazer. Escreva a sua versão num arquivo à parte e só depois compare com a resposta.",
                "**Rode o original.** `dataforge run exercicios/<módulo>/<arquivo>.df` termina sem erro quando está certo — não há saída \"passou\" para procurar.",
                "**Quebre de propósito.** Troque o valor esperado num `assert` e rode de novo: o erro aponta a linha e mostra os dois valores. É o jeito mais rápido de ler o que cada linha garante.",
                "**Passe o `check`.** `dataforge check` no arquivo mostra o que o analisador acusa antes de rodar. Vários exercícios provocam um erro dentro de `monitor` de propósito, e ali ele aparece como aviso.",
                "**Faça o \"Experimente\".** Do módulo 11 em diante, a explicação de cada exercício termina com sugestões de mudança — é onde está a parte que não se aprende só lendo.",
            ], "ordered": True},
            {"h2": "Por onde começar"},
            {"p": "Uma trilha por objetivo. Os números levam ao módulo; dentro dele, os exercícios estão em ordem de dificuldade."},
            {"table": {"head": ["Se você quer…", "Módulos, nesta ordem"],
                       "rows": trilhas}},
            {"h2": f"Os {len(MODULOS)} módulos, por nível"},
            *por_nivel,
        ],
    }


def _ancora(numero, titulo):
    """O mesmo id que 'gerar_paginas' vai gerar para o h2 do exercício."""
    from gerar_indices import slugify
    return slugify(f"{numero} · {titulo}")


def _pagina_modulo(nome, itens, caminhos):
    tem_md = os.path.isfile(caminhos[0][:-3] + ".md")

    # O índice continua: com 14 exercícios numa página, pular para o que
    # interessa importa mais que ler do começo. Agora cada linha LEVA ao
    # exercício, em vez de só nomeá-lo.
    linhas = [
        [f"[{n}](#{_ancora(n, t)})", f"**{t}**", e]
        for n, t, e in itens if n
    ]

    nivel = _nivel_de(nome)
    blocos = [
        *([{"p": f"Nível: **{nivel}** · {ASSUNTOS.get(nome, '')} · "
                 f"[todos os módulos](/docs/exercicios)"}] if nivel else []),
        {"code": f"python3 exercicios/run_all.py {nome[:2]}", "lang": "bash"},
        {"h2": "Os exercícios"},
        {"table": {"head": ["#", "Título", "Enunciado"], "rows": linhas}},
    ]
    if tem_md:
        blocos.append({"callout": {
            "tipo": "dica", "titulo": "Cada um traz a explicação junto",
            "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}})

    # ── O corpo: cada exercício, por inteiro ──────────────────────
    #
    # Antes a página parava na tabela acima: título e enunciado, e nada
    # do código. Quem chegava por busca via a PROMESSA de 399 exercícios
    # e nenhum deles — para ler um, era preciso clonar o repositório.
    # O código é a resposta e o teste ao mesmo tempo; escondê-lo
    # esvazia a seção inteira.
    for (numero, titulo, enunciado), caminho in zip(itens, caminhos):
        if not numero:
            continue
        arquivo = os.path.basename(caminho)
        blocos.append({"h2": f"{numero} · {titulo}"})
        if enunciado:
            blocos.append({"p": f"**Enunciado.** {enunciado}"})
        blocos.append({"code": _corpo(caminho), "lang": "df",
                       "title": f"exercicios/{nome}/{arquivo}"})
        blocos.extend(_explicacao(caminho))

    blocos.append({"hr": True})
    blocos.append({"p": f"Rode um isolado com `dataforge run exercicios/{nome}/{os.path.basename(caminhos[0])}`."})

    return {
        "href": f"/docs/exercicios/{nome}",
        "title": _rotulo(nome),
        "description": f"{_n_exercicios(len(linhas))}: {ASSUNTOS.get(nome, '')}.",
        "blocos": blocos,
    }


PAGINAS = [_pagina_indice()] + [
    _pagina_modulo(nome, itens, caminhos) for nome, itens, caminhos in MODULOS
]
