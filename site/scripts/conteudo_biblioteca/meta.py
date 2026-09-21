# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de meta.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{"p": "`Arcane.Meta` lê os metadados que os [decoradores](/docs/fundamentos/decoradores-avancados) deixaram. É a metade que torna um decorador útil: `@Rota(\"/itens\")` grava o caminho, e `Meta.ler` o devolve."}''',
    r'''{ code: `adopt Arcane.Meta as Meta

@Rota("GET", "/itens")
action listar():
    yield itens

Meta.tem(listar, "Rota")        // yes
Meta.arg(listar, "Rota", 0)     // GET` }''',
    r'''{"h2": "Leitura"}''',
    r'''{"table": {"head": ["Função", "Devolve"], "rows": [["`Meta.tem(alvo, nome)`", "o alvo foi decorado com `@nome`?"], ["`Meta.nomes(alvo)`", "os nomes dos decoradores, na ordem em que aparecem"], ["`Meta.todos(alvo)`", "todos os metadados: `[{nome, args, kwargs}]`"], ["`Meta.ler(alvo, nome)`", "o primeiro `@nome`, ou `void`"], ["`Meta.todos_de(alvo, nome)`", "todas as ocorrências de `@nome` (decorador repetível)"], ["`Meta.arg(alvo, nome, i, padrao)`", "um argumento posicional, com padrão"], ["`Meta.opcao(alvo, nome, chave, padrao)`", "um argumento nomeado, com padrão"]]}}''',
    r'''{"p": "Todas devolvem o padrão (ou `void`) quando o decorador não existe — nunca levantam. Perguntar por um decorador ausente é o caso normal, não erro."}''',
    r'''{"h2": "Varredura"}''',
    r'''{ code: `// os métodos de um controlador anotados com @Rota
cycle r in Meta.metodos_com(UsuariosController, "Rota"):
    out r["nome"], r["meta"]["args"]

// de uma lista de blueprints, os @Injetavel
servicos := Meta.filtrar([Repo, Cache, Config], "Injetavel")` }''',
    r'''{"table": {"head": ["Função", "Devolve"], "rows": [["`Meta.metodos_com(blueprint, nome)`", "`[{nome, metodo, meta}]` — os métodos anotados"], ["`Meta.filtrar(valores, nome)`", "de uma lista ou vault, os que têm `@nome`"], ["`Meta.descrever(alvo)`", "tipo, nome, decoradores, métodos e campos"]]}}''',
    r'''{"p": "`metodos_com` é o que um roteador usa para descobrir rotas a partir de uma classe; `filtrar` é o que um contêiner usa para achar o que registrar."}''',
    r'''{"h2": "Escrita"}''',
    r'''{ code: `// anotar algo que já existe, sem a sintaxe de decorador
Meta.marcar(minha_acao, "Cache", 60)
out Meta.arg(minha_acao, "Cache", 0)    // 60

Meta.limpar(minha_acao)                 // remove tudo — útil em teste` }''',
    r'''{"p": "`marcar` serve para anotar um valor vindo de outro módulo, e para escrever decoradores que anotam além do que receberam."}''',
    r'''{"h2": "O que sobrevive ao embrulho"}''',
    r'''{ code: `@logar          // embrulha
@Rota("/x")     // só anota
action f(n):
    yield n

Meta.tem(f, "Rota")     // yes — o embrulho herdou a anotação` }''',
    r'''{"p": "Quando um decorador embrulha o alvo, o embrulho **herda** os metadados de quem embrulhou. Sem isso, `@logar @Rota(...)` perderia a anotação assim que o primeiro decorador devolvesse um embrulho — e a ordem dos decoradores viraria uma armadilha."}''',
    r'''{"h2": "Onde ver funcionando"}''',
    r'''{"table": {"head": ["Onde", "O quê"], "rows": [["[Decoradores](/docs/fundamentos/decoradores-avancados)", "um roteador e um contêiner de injeção completos"], ["[Playground](/painel/playground)", "o exemplo \"Decoradores\", rodando no navegador"], ["`tests/test_decoradores.py`", "20 testes"]]}}''',
]
