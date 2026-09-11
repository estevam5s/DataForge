# -*- coding: utf-8 -*-
"""
O catalogo dos modulos da stdlib: nome, nome curto e para que serve.

Ele existe pelo mesmo motivo de 'catalogo_erros.py'. A descricao de
cada modulo era escrita em TRES lugares — a doc em Markdown, os dados
do site e a pagina de visao geral — e as tres divergiram: a pagina
ainda anunciava "vinte modulos e 675 simbolos" quando ja eram 33 e
1143, e o Arcane.Crypto aparecia com 38 simbolos tendo 48.

Divergencia assim nao se resolve com atencao; resolve-se tirando as
copias. A contagem de simbolos NAO esta aqui de proposito: ela sai do
codigo, sempre. O que se escreve a mao e so o que o codigo nao sabe
dizer — para que o modulo serve.

A ordem e a da doc: os quatro grandes primeiro, depois o resto por
assunto.
"""

#: nome oficial -> (para que serve, nome curto que 'adopt' tambem aceita)
DESCRICOES = {
    "Arcane.Math": ("Matemática, álgebra linear e estatística básica.", "Math"),
    "Arcane.Text": ("Manipulação de texto, formatação, tabelas e conversão de caixa.", "Text"),
    "Arcane.Analytics": ("Análise de dados: estatística, regressão, clustering e gráficos ASCII.", "Analytics"),
    "Arcane.Functional": ("Utilitários funcionais: composição, lentes, Maybe/Either, transdutores.", "Functional"),
    "Arcane.Database": ("Banco de dados SQLite: tabelas, consultas, migrações e importação.", "Database / DB"),
    "Arcane.Excel": ("Planilhas .xlsx: ler, gravar, fórmulas e conversão para CSV e frame.", "Excel / Xlsx"),
    "Arcane.Meta": ("Metadados de decorador: ler @Nome em tempo de execução.", "Meta"),
    "Kiln": ("Framework web: rotas, middleware, templates, sessão e arquivos estáticos.", "Kiln"),
    "Arcane.Test": ("Asserções e organização de suítes de teste.", "Test"),
    "Arcane.Regex": ("Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone).", "Regex"),
    "Arcane.IO": ("Arquivos, diretórios, JSON, CSV e shell.", "IO"),
    "Arcane.Http": ("Servidor HTTP: rotas, middleware, JSON, arquivos estáticos.", "Http / Server"),
    "Arcane.Async": ("Promessas, filas, agendamento e execução concorrente.", "Async"),
    "Arcane.Data": ("DataFrames, séries e transformações tabulares.", "Data"),
    "Arcane.Web": ("Cliente HTTP, URL encoding e JSON.", "Web / Network"),
    "Arcane.Cortex": ("Aprendizado de máquina: regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA.", "Cortex"),

    # ── DataForge 4.0 ──
    "Arcane.Time": ("Datas, horas, durações e cronometragem.", "Time"),
    "Arcane.OS": ("Sistema operacional, ambiente, disco e processo atual.", "OS"),
    "Arcane.Process": ("Execução de processos externos, com stdout, stderr e código de saída.", "Process"),
    "Arcane.Logging": ("Registro estruturado de eventos, com níveis e destinos.", "Logging / Log"),
    "Arcane.Crypto": ("Hashes, HMAC, senhas, codificações, aleatoriedade segura e cifragem de arquivo (ChaCha20-Poly1305).", "Crypto"),
    "Arcane.Collections": ("Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca.", "Collections"),
    "Arcane.Serialization": ("JSON, CSV, INI, TOML, XML e conversões entre eles.", "Serialization / Serde"),

    # ── Depois do 4.0 ──
    "Arcane.Forge": ("Banco de dados: SQLite, Postgres, MySQL, Redis e MongoDB pela mesma interface.", "Forge / Banco"),
    "Arcane.Crucible": ("Framework de testes: suítes, matchers, fixtures, dublês e benchmark.", "Crucible"),
    "Arcane.Iter": ("Iteradores preguiçosos e composição de ações: janelas, combinatória, memoize.", "Iter"),
    "Arcane.Color": ("Cor de 24 bits no terminal, tabela, moldura, barra de progresso e árvore.", "Color / Cor"),
    "Arcane.Concurrent": ("Threads, processos, canal bloqueante, grupo de tarefas e prazo.", "Concurrent / Paralelo"),
    "Arcane.Archive": ("Zip e tar: compactar, listar, conferir e extrair recusando Zip Slip e zip bomb.", "Archive / Zip"),
    "Arcane.Pipeline": ("Orquestração de ETL/ELT: DAG, dependências, retry, incremental e relatório.", "Pipeline / Fluxo"),
    "Arcane.Stream": ("Streaming: tópicos, partições, offsets, grupos de consumo e janelas de tempo.", "Stream / Corrente"),
    "Arcane.Observar": ("Observabilidade: métricas com percentil, tracing aninhado e linhagem de dados.", "Observar / Observe"),
    "Arcane.Lago": ("Data Lake: Parquet nativo, partições Hive, camadas bronze/prata/ouro e compactação.", "Lago / Parquet"),
    "Arcane.Qualidade": ("Qualidade de dados: as seis dimensões, perfil, validação e limpeza.", "Qualidade / Quality"),
}


def descricao(nome):
    """Para que serve o modulo, ou "" se ele nao esta no catalogo."""
    return DESCRICOES.get(nome, ("", ""))[0]


def nome_curto(nome):
    """O apelido que 'adopt' tambem aceita."""
    return DESCRICOES.get(nome, ("", ""))[1]


#: A assinatura das funcoes que a stdlib expoe direto do C do Python.
#:
#: `math.factorial` chama o parametro de `x` ate o Python 3.12 e de `n`
#: a partir do 3.13. Como `Arcane.Math` publica `math.factorial` sem
#: envolve-la, `inspect.signature` vazava o nome interno do CPython para
#: dentro da documentacao da linguagem — e `doc/BIBLIOTECA_PADRAO.md`
#: passava a depender da versao de Python de quem rodou o gerador. Duas
#: maquinas certas produziam arquivos diferentes, e o CI cobrava a
#: diferenca sem que ninguem tivesse errado.
#:
#: A tabela existe para o DataForge nomear a propria interface. O nome
#: aqui e o que a documentacao mostra, independente de build.
#:
#: Ha teste garantindo que toda funcao C exposta tenha entrada: uma que
#: faltasse voltaria a herdar o nome do CPython em silencio.
ASSINATURAS = {
    # ── Arcane.Math ──
    "abs": "(x)",
    "acos": "(x)",
    "asin": "(x)",
    "atan": "(x)",
    "atan2": "(y, x)",
    "ceil": "(x)",
    "comb": "(n, k)",
    "cos": "(x)",
    "degrees": "(x)",
    "exp": "(x)",
    "factorial": "(n)",
    "floor": "(x)",
    "gcd": "(*inteiros)",
    "hypot": "(*coordenadas)",
    "log": "(x, base=e)",
    "log10": "(x)",
    "log2": "(x)",
    "perm": "(n, k=void)",
    "pow": "(x, y)",
    "radians": "(x)",
    "round": "(numero, casas=void)",
    "sin": "(x)",
    "sqrt": "(x)",
    "tan": "(x)",
    # ── Globais ──
    "max": "(*valores)",
    "min": "(*valores)",
}


def assinatura_fixa(simbolo):
    """A assinatura declarada, ou None se o simbolo nao esta na tabela."""
    return ASSINATURAS.get(simbolo)
