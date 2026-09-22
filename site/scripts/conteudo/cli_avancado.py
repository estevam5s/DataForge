# -*- coding: utf-8 -*-
"""A CLI — o índice, a referência completa e as páginas por tema.

O índice antigo era escrito à mão e dizia *"os treze comandos"* quando
havia sessenta e quatro. Aqui a lista **sai do catálogo** (`cli.GRUPOS`),
que é a mesma fonte do `dataforge help`, do autocompletar e da API
`/api/comandos.json`. Um comando novo aparece nesta página na próxima
geração; um removido some.

As páginas por tema descrevem os comandos que não tinham página — e
`tests/test_paginas_da_cli.py` confere que todo `dataforge <x>` citado
nelas é um comando que existe.
"""
import os
import sys

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from dataforge.cli import GRUPOS  # noqa: E402

#: Os comandos que têm página própria, e onde.
PAGINA_DE = {
    "run": "/docs/cli/run", "check": "/docs/cli/check", "test": "/docs/cli/test",
    "fmt": "/docs/cli/fmt", "lint": "/docs/cli/lint", "doc": "/docs/cli/doc",
    "init": "/docs/cli/init", "repl": "/docs/cli/repl", "watch": "/docs/cli/watch",
    "bench": "/docs/cli/bench", "explain": "/docs/cli/explain",
    "editor": "/docs/cli/editor", "workspace": "/docs/cli/workspace",
    "versions": "/docs/cli/versoes", "use": "/docs/cli/versoes",
    "upgrade": "/docs/cli/versoes", "clean": "/docs/cli/cache",
    "add": "/docs/cli/pacotes", "remove": "/docs/cli/pacotes",
    "install": "/docs/cli/pacotes", "update": "/docs/cli/pacotes",
    "list": "/docs/cli/pacotes", "tree": "/docs/cli/pacotes",
    "why": "/docs/cli/pacotes", "outdated": "/docs/cli/pacotes",
    "search": "/docs/cli/pacotes", "pack": "/docs/cli/pacotes",
    "publish": "/docs/cli/pacotes",
    "new": "/docs/cli/new", "info": "/docs/cli/new",
    "debug": "/docs/cli/debug", "dap": "/docs/cli/debug", "lsp": "/docs/cli/debug",
    "stats": "/docs/cli/analise", "oop": "/docs/cli/analise",
    "big-o": "/docs/cli/analise", "custo": "/docs/cli/analise",
    "deps": "/docs/cli/analise",
    "profile": "/docs/cli/profile", "fix": "/docs/cli/profile",
    "seguranca": "/docs/cli/seguranca",
    "crucible": "/docs/cli/crucible",
    "tokens": "/docs/cli/internos", "ast": "/docs/cli/internos",
    "ir": "/docs/cli/internos", "percurso": "/docs/cli/internos",
    "abi": "/docs/cli/abi", "alvo": "/docs/cli/abi",
    "completar": "/docs/cli/completar",
    "eval": "/docs/cli/scripts", "version": "/docs/cli/scripts",
    "help": "/docs/cli/scripts",
    "devops": "/docs/devops",
    "vitrine": "/docs/vitrine", "telegram": "/docs/telegram",
    "api": "/docs/tecnicas/api", "converter": "/docs/cli/scripts",
    "palavras": "/docs/referencia/palavras-reservadas",
    "erros": "/docs/referencia/erros",
    "login": "/docs/pacotes/publicar", "logout": "/docs/pacotes/publicar",
    "whoami": "/docs/pacotes/publicar",
    "ecossistema": "/docs/ecossistema/componentes",
    "principios": "/docs/ecossistema/principios",
}


def _comandos():
    return [(grupo, list(cmds)) for grupo, cmds in GRUPOS]


def _celula(texto):
    return str(texto).replace("|", "\\|").replace("\n", " ")


def _indice():
    total = sum(len(c) for _g, c in _comandos())
    blocos = [
        {"p": f"`dataforge` — ou `df`, o mesmo programa — tem **{total} comandos** "
              "em sete grupos. Esta tabela sai do catálogo que o próprio "
              "`dataforge help` lê: ela não tem como ficar para trás."},
        {"code": "dataforge help              # a visão geral\n"
                 "dataforge help check        # tudo sobre um comando\n"
                 "dataforge check --help      # o mesmo\n"
                 "dataforge completar zsh     # o Tab do terminal, gerado do mesmo catálogo",
         "lang": "bash"},
    ]
    for grupo, cmds in _comandos():
        blocos.append({"h2": grupo})
        linhas = []
        for c in cmds:
            nome = f"`{c.nome}`"
            if c.nome in PAGINA_DE:
                nome = f"[`{c.nome}`]({PAGINA_DE[c.nome]})"
            apelidos = ", ".join(f"`{a}`" for a in (c.apelidos or ()) if not a.startswith("-"))
            linhas.append([nome, _celula(c.resumo), apelidos])
        blocos.append({"table": {"head": ["Comando", "O que faz", "Também"], "rows": linhas}})
    blocos += [
        {"h2": "O ciclo de trabalho"},
        {"code": """dataforge new api loja        # comecar de um modelo que passa nos testes
cd loja

dataforge check src/          # nomes, tipos, aridade — antes de rodar
dataforge fmt src/            # formatar
dataforge test                # testes, com cobertura
dataforge run                 # executar a entrada do forge.toml""", "lang": "bash"},
        {"h2": "Em integração contínua"},
        {"code": "dataforge fmt . --check && dataforge check . --strict --formato=github && dataforge test --minimo=80",
         "lang": "bash"},
        {"p": "Todo comando sai com código **diferente de zero** quando falha, e o `&&` "
              "para na primeira etapa que quebrar. `--formato=github` põe o erro do "
              "`check` na linha do PR — ver [GitHub Actions](/docs/devops/github-actions)."},
        {"h2": "Por tema"},
        {"cards": [
            {"href": "/docs/cli/referencia", "title": "Referência completa", "desc": "todo comando, com opções, exemplos e apelidos"},
            {"href": "/docs/cli/new", "title": "new e info", "desc": "os modelos de projeto"},
            {"href": "/docs/cli/debug", "title": "debug, dap e lsp", "desc": "parar, vigiar, e o editor"},
            {"href": "/docs/cli/analise", "title": "Análise do código", "desc": "stats, oop, big-o, custo, deps"},
            {"href": "/docs/cli/profile", "title": "profile e fix", "desc": "onde o tempo vai; o que se conserta sozinho"},
            {"href": "/docs/cli/seguranca", "title": "seguranca", "desc": "segredos e padrões arriscados"},
            {"href": "/docs/cli/crucible", "title": "crucible", "desc": "filtro, tag, ordem aleatória, relatórios"},
            {"href": "/docs/cli/internos", "title": "tokens, ast, ir, percurso", "desc": "o que o compilador vê"},
            {"href": "/docs/cli/abi", "title": "abi e alvo", "desc": "o que quebra; onde roda"},
            {"href": "/docs/cli/completar", "title": "completar", "desc": "o Tab no bash, zsh e fish"},
            {"href": "/docs/cli/scripts", "title": "Em scripts", "desc": "códigos de saída, cor, ambiente, eval"}]},
    ]
    return {"href": "/docs/cli", "title": "CLI",
            "description": f"Os {total} comandos do dataforge, do catálogo que o próprio help lê.",
            "blocos": blocos}


def _referencia():
    blocos = [{"p": "Todo comando, na ordem do `dataforge help`. Esta página é **gerada** "
                    "do catálogo `cli.GRUPOS` — o mesmo que o `help`, o autocompletar e "
                    "`/api/comandos.json` leem."}]
    for grupo, cmds in _comandos():
        blocos.append({"h2": grupo})
        for c in cmds:
            blocos.append({"h3": c.nome})
            texto = c.resumo.rstrip(".") + "."
            if c.nome in PAGINA_DE:
                texto += f" Ver [a página]({PAGINA_DE[c.nome]})."
            blocos.append({"p": texto})
            blocos.append({"code": c.uso, "lang": "bash"})
            if c.detalhe:
                blocos.append({"code": c.detalhe, "lang": "text"})
            if c.opcoes:
                blocos.append({"table": {"head": ["Opção", "Efeito"], "rows": [
                    [f"`{_celula(f)}`", _celula(d)] for f, d in c.opcoes]}})
            if c.exemplos:
                blocos.append({"code": "\n".join(
                    (f"{e:<52} # {d}" if d else e) for e, d in c.exemplos), "lang": "bash"})
            extras = []
            ap = [a for a in (c.apelidos or ())]
            if ap:
                extras.append("Também: " + ", ".join(f"`{a}`" for a in ap) + ".")
            if c.veja:
                extras.append("Veja: " + ", ".join(f"`{v}`" for v in c.veja) + ".")
            if extras:
                blocos.append({"p": " ".join(extras)})
    return {"href": "/docs/cli/referencia", "title": "Referência da CLI",
            "description": "Todo comando, com uso, opções, exemplos e apelidos — gerada do catálogo.",
            "blocos": blocos}


PAGINAS = [
_indice(),
_referencia(),

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/cli/new",
"title": "dataforge new e info",
"description": "Os modelos de projeto — e por que todo projeto criado passa nos próprios testes.",
"blocos": [
 {"p": "`dataforge new` cria um projeto a partir de um modelo. A promessa de todos é a mesma: o projeto criado **roda e passa nos próprios testes** antes de você mexer em qualquer coisa. Um esqueleto com `TODO` é apagado na primeira hora; um projeto que funciona é o ponto de partida."},
 {"code": """dataforge new                    # escolhe na tela
dataforge new --list             # so os modelos
dataforge new api loja           # direto
cd loja && dataforge test tests/ # verde, antes de qualquer mudanca
dataforge info                   # o manifesto: nome, versao, entrada, dependencias""", "lang": "bash"},
 {"table": {"head": ["Modelo", "O que ele traz", "O tipo de projeto"], "rows": [
   ["`cli`", "argumentos, tabela colorida, `--help`", "[CLI de anotações](/docs/projetos/cli-notas)"],
   ["`api`", "rotas, JSON, 404/405 e testes sem socket", "[API REST](/docs/projetos/api-rest)"],
   ["`web`", "páginas HTML, estáticos, escape automático", "[Site estático](/docs/projetos/site-estatico)"],
   ["`data`", "banco, estatística, exportação para Excel", "[ETL](/docs/projetos/etl)"],
   ["`lib`", "`relay`, testes e pronto para publicar", "[Biblioteca](/docs/projetos/biblioteca)"],
   ["`oop`", "blueprints, traits, propriedades, operadores", "[Estoque](/docs/projetos/estoque)"],
   ["`script`", "arquivos, JSON, datas, processos", "[Agendador](/docs/projetos/agendador)"],
   ["`painel`", "métricas, gráficos, filtros e testes", "[Painel](/docs/projetos/painel)"],
   ["`bot`", "comandos, botões, conversa e testes sem rede", "[Bot](/docs/projetos/bot-atendimento)"],
   ["`test`", "como se testa: asserts, erros, cobertura", "[TDD](/docs/testes/tdd)"]]}},
 {"h2": "A estrutura é sempre a mesma"},
 {"code": """loja/
  forge.toml     nome, versao, entrada, dependencias, scripts
  README.md
  .gitignore     forge_modules/, .env, *.db
  src/           o codigo
  tests/         os testes — dataforge test tests/""", "lang": "text"},
 {"p": "Quem aprendeu um projeto sabe se achar em qualquer outro. E o `forge.toml` já fixa a versão da linguagem (`dataforge = \">=1.1\"`), que `dataforge run` **cobra** — ver [Versões](/docs/cli/versoes)."},
 {"p": "Continue em [Os vinte e dois tipos de projeto](/docs/projetos)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/cli/debug",
"title": "dataforge debug, dap e lsp",
"description": "Parar numa linha, vigiar um valor, e o editor com breakpoints na margem.",
"blocos": [
 {"p": "`dataforge debug` roda o programa parando onde você mandar. Ele funciona por ssh, num contêiner, em qualquer terminal — e é a mesma máquina que o editor usa pelo `dap`."},
 {"code": """dataforge debug conta.df                         # para na primeira instrucao
dataforge debug conta.df --parar=42,57           # paradas nas linhas 42 e 57
dataforge debug conta.df --vigiar=saldo          # para quando 'saldo' MUDAR
dataforge debug conta.df --vigiar-leitura=saldo  # para quando 'saldo' for LIDO""", "lang": "bash"},
 {"h2": "Dentro do depurador"},
 {"table": {"head": ["Comando", "Faz"], "rows": [
   ["`p`", "passo: entra na ação chamada"],
   ["`n`", "próximo: passa por cima da chamada"],
   ["`f`", "sai da ação atual"],
   ["`c`", "continua até a próxima parada"],
   ["`vars`", "o escopo onde você parou"],
   ["`pilha`", "quem chamou quem"],
   ["`w saldo` / `r saldo`", "vigia de escrita / de leitura, a partir daqui"],
   ["qualquer expressão", "avaliada no quadro onde você parou"]]}},
 {"h2": "Vigia de escrita e de leitura são perguntas diferentes"},
 {"table": {"head": ["", "`--vigiar`", "`--vigiar-leitura`"], "rows": [
   ["pergunta", "*quem mudou isto?*", "*quem está consultando isto?*"],
   ["como", "compara uma foto estrutural depois de cada instrução", "intercepta a leitura do nome e de `obj.campo`"],
   ["onde para", "na linha que **acabou** de mudar", "na linha que leu"]]}},
 {"callout": {"tipo": "dica", "titulo": "Custo zero quando desligado", "texto": "O depurador não é um `if` no caminho quente: ele **substitui** o método de execução enquanto roda, e sai com `del`. O programa sem depurador não paga nada por ele existir."}},
 {"h2": "No editor"},
 {"p": "`dataforge dap` fala o Debug Adapter Protocol — breakpoints na margem, pilha no painel, variáveis em árvore, data breakpoints de escrita **e** de leitura. Você não o roda à mão: a extensão o inicia no F5. `dataforge lsp` é o servidor de linguagem: hover, completar, ir para a definição, os diagnósticos do `check` enquanto você digita."},
 {"code": """dataforge editor          # instala a extensao (cores, snippets, LSP, DAP)
dataforge editor status   # onde ela esta instalada""", "lang": "bash"},
 {"p": "Continue em [O editor](/docs/editor) e [LSP](/docs/tecnicas/lsp)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/cli/analise",
"title": "Análise do código",
"description": "stats, oop, big-o, custo e deps — o que o código é, sem rodá-lo.",
"blocos": [
 {"p": "Cinco comandos que leem o código e respondem sobre a **forma** dele. Nenhum executa o programa, e todos aceitam arquivo, pasta ou padrão."},
 {"table": {"head": ["Comando", "Responde", "Quando"], "rows": [
   ["`dataforge stats`", "quantas ações e blueprints, o arquivo e a ação mais longos", "achar o que cresceu demais sem ninguém notar"],
   ["`dataforge oop`", "WMC, DIT, CBO, LCOM… e os cheiros com o princípio SOLID", "revisar um desenho de classes"],
   ["`dataforge big-o`", "a classe de complexidade de cada ação, **e o porquê**", "antes de otimizar"],
   ["`dataforge custo`", "o que cada `adopt` traz junto", "a partida está lenta"],
   ["`dataforge deps`", "o grafo de imports, e os ciclos", "entender um projeto novo"]]}},
 {"code": """dataforge stats src/
dataforge oop src/ --diagrama > classes.mmd   # Mermaid, para o README
dataforge oop src/ --strict                   # reprova o CI com cheiro
dataforge big-o src/ -v                       # a classe e o que fazer
dataforge big-o src/ --medir                  # confere a classe medindo
dataforge big-o --escala                      # a tabela do que cada classe custa
dataforge custo src/
dataforge deps""", "lang": "bash"},
 {"callout": {"tipo": "atencao", "titulo": "Errar a classe é pior que não ter a ferramenta", "texto": "O `big-o` erra com confiança, e o relatório é curto o bastante para ser lido como verdade. Quatro erros de classificação já foram medidos e corrigidos — o merge sort como `O(n log² n)`, a busca binária como `O(2ⁿ)` —, e hoje `--medir` confere a classe estimada contra o tempo real. Use o `-v`: a classe sem o porquê não ajuda a melhorar nada."}},
 {"p": "Continue em [Big-O](/docs/big-o) e [Métricas de OOP](/docs/oop)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/cli/profile",
"title": "dataforge profile e fix",
"description": "Onde o tempo foi gasto, ação por ação — e o que se conserta sozinho.",
"blocos": [
 {"p": "Um `bench` diz **que** está lento; um `profile` diz **onde**. Ele mede cada ação — chamadas, tempo **próprio** e por chamada — e ordena pelo que mais custa."},
 {"code": """dataforge profile src/main.df
dataforge bench src/main.df          # o tempo total, repetindo""", "lang": "bash"},
 {"callout": {"tipo": "atencao", "titulo": "Tempo próprio, e não acumulado", "texto": "O acumulado de `main` inclui tudo o que ela chama, e a soma de todos passaria de 100%. O tempo **próprio** é o que a ação gasta nela mesma — é o número que aponta o gargalo. A ação que você acha que é o gargalo quase nunca é."}},
 {"h2": "fix"},
 {"p": "`dataforge fix` roda o formatador e, em seguida, o linter: arruma o que dá para arrumar sozinho e **lista** o resto. O que exige julgamento não é consertado — uma ferramenta que muda código precisa ser previsível."},
 {"code": """dataforge fix              # formata e lista
dataforge fix --dry-run    # so o relatorio, sem escrever""", "lang": "bash"},
 {"p": "Continue em [Medir](/docs/cli/bench) e [Prometer desempenho](/docs/bibliotecas/desempenho)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/cli/seguranca",
"title": "dataforge seguranca",
"description": "Segredo escrito no código e padrão arriscado — em todo arquivo, não só nos .df.",
"blocos": [
 {"p": "Duas varreduras. A primeira acha **segredo pelo formato** — chave da AWS, token do GitHub, `sk_live` da Stripe, bloco de chave privada, token do PyPI —, e por isso acha o que você esqueceu, que é o único tipo que importa. A segunda aplica regras sintáticas: SQL concatenado, shell com interpolação, MD5 para assinatura, senha sem derivação, verificação de certificado desligada."},
 {"code": """dataforge seguranca .              # o projeto inteiro
dataforge seguranca src/ --strict  # sai com 1 se houver achado: reprova o CI
dataforge seguranca . --json       # para outra ferramenta
dataforge seguranca . --so=alto    # esconde os medios""", "lang": "bash"},
 {"h2": "O que ela cala, de propósito"},
 {"table": {"head": ["Cala sobre", "Porque"], "rows": [
   ["valor que se anuncia como exemplo", "`sua-senha-aqui`, `AKIA…EXAMPLE`"],
   ["JWT com papel `anon`", "a chave `anon` do Supabase vai no navegador de propósito — a `service_role` não"],
   ["credencial de `localhost`", "`postgres://app:app@localhost` num teste é um teste normal"],
   ["`// df: permitir segredo-no-codigo`", "o escape nomeado, em qualquer arquivo"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Um falso alarme desliga a ferramenta", "texto": "Sem esses silêncios a varredura apontava 19 vezes neste repositório, e as 19 eram falso alarme — inclusive os exercícios que ensinam a não escrever token no arquivo. Uma varredura assim é desligada no mesmo dia, e junto vão os achados de verdade."}},
 {"p": "No CI, antes do commit: [pre-commit](/docs/devops/ambiente-de-dev). O resto do assunto: [Segurança da informação](/docs/seguranca/mapa)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/cli/crucible",
"title": "dataforge crucible",
"description": "Filtro, tags, ordem aleatória, repetição, prazo e relatórios para o CI.",
"blocos": [
 {"p": "`dataforge test` descobre e roda os testes do projeto, com cobertura. `dataforge crucible` é o corredor do framework com **todas** as alavancas: escolher o que roda, mudar a ordem, repetir, e o formato do relatório."},
 {"code": """dataforge crucible                             # tudo, em tests/, testes/ e *_crucible.df
dataforge crucible --filtro=desconto           # so os trials com 'desconto' no nome
dataforge crucible --tag=rapido                # so os marcados
dataforge crucible --sem-tag=lento             # pula os marcados
dataforge crucible --aleatorio                 # embaralha: a dependencia de ordem aparece
dataforge crucible --aleatorio --semente=4217  # repete aquele embaralhamento
dataforge crucible --repetir=50                # o teste instavel se denuncia
dataforge crucible --prazo=200                 # falha o que passar de 200 ms
dataforge crucible --formato=junit --out=r.xml # para o CI
dataforge crucible --matchers                  # tudo o que se pode cobrar""", "lang": "bash"},
 {"table": {"head": ["Alavanca", "O defeito que ela expõe"], "rows": [
   ["`--aleatorio`", "o teste que só passa depois de outro — estado compartilhado"],
   ["`--semente`", "reproduzir a ordem que falhou, em vez de torcer para ela voltar"],
   ["`--repetir`", "o teste instável, que passa uma vez em vinte"],
   ["`--prazo`", "o teste que ficou lento sem ninguém notar"],
   ["`--formato=junit`", "o CI lista o teste que falhou, em vez de só *“job vermelho”*"]]}},
 {"p": "Continue em [Testes instáveis](/docs/testes/instaveis) e [Relatórios e CI](/docs/crucible/relatorios)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/cli/internos",
"title": "tokens, ast, ir e percurso",
"description": "O que o lexer, o parser e o compilador viram — quando o código é lido de outro jeito.",
"blocos": [
 {"p": "Quatro comandos que mostram o programa **como a linguagem o vê**. São os primeiros a usar quando o código não faz o que parece — e a suspeita é de que ele está sendo lido de outro jeito."},
 {"code": """dataforge tokens app.df              # o que o lexer viu
dataforge ast app.df                 # a arvore que o parser montou
dataforge ir app.df                  # HIR, MIR, analises, SSA, LIR
dataforge ir app.df --fase=mir --acao=total   # o grafo de fluxo de uma acao
dataforge percurso app.df            # todas as fases, em ordem, medidas
dataforge percurso app.df --desenho  # o caminho desenhado, com as ausencias""", "lang": "bash"},
 {"h2": "O caso clássico: `//`"},
 {"p": "`//` é comentário por padrão, e só vira divisão inteira seguido de dígito, `(`, ou chamada/índice/membro. `x // 2` é divisão; `x // nota` é comentário. `dataforge tokens` mostra na hora qual das duas o lexer escolheu — e `~/` é a divisão inteira sem ambiguidade."},
 {"table": {"head": ["Fase", "O que ela mostra"], "rows": [
   ["`hir`", "a árvore depois do açúcar — e quanto dele o arquivo usa"],
   ["`mir`", "o grafo de fluxo: bloco básico, aresta, laço, tratador"],
   ["`analises`", "alcance, constantes, escapatória, nome talvez não definido"],
   ["`ssa`", "uma definição por nome, com os nós φ das junções"],
   ["`lir`", "o que o compilador de fechamentos compilou — e o que recuou"]]}},
 {"callout": {"tipo": "nota", "titulo": "O percurso não executa", "texto": "`percurso` vai do lexer ao LIR e para. A décima fase — executar — é nomeada e marcada como não percorrida: um arquivo de verdade abre soquete e escreve em disco, e medir não pode ter efeito."}},
 {"p": "Continue em [Arquitetura](/docs/referencia/arquitetura) e [Gramática](/docs/referencia/gramatica)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/cli/abi",
"title": "dataforge abi e alvo",
"description": "A nova versão quebra a anterior? E este programa roda no navegador, no WASI, numa função?",
"blocos": [
 {"p": "Duas perguntas que se fazem antes de publicar, e que costumam ser respondidas a olho."},
 {"h2": "abi — o que muda para quem depende"},
 {"code": """dataforge abi v1/lib.df v2/lib.df         # o que mudou, e que bump exige
dataforge abi v1/lib.df v2/lib.df --json  # para o CI
dataforge abi v1/lib.df v2/lib.df --estrito""", "lang": "bash"},
 {"table": {"head": ["Veredito", "Significa", "Código de saída"], "rows": [
   ["`maior`", "alguma coisa quebrou", "1 — reprova o CI"],
   ["`menor`", "só acréscimos compatíveis", "0"],
   ["`correcao`", "a superfície não mudou", "0"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Renomear parâmetro é quebra", "texto": "A chamada com nome existe nesta linguagem (`somar(a := 1)`), então o nome do parâmetro é contrato, e não só a posição. Uma ferramenta feita para C não teria essa regra."}},
 {"h2": "alvo — onde o programa roda"},
 {"code": """dataforge alvo app.df                  # a tabela de todos
dataforge alvo app.df --alvo=navegador # um so; sai com 1 se nao roda""", "lang": "bash"},
 {"p": "Ela lê os `adopt` e cruza com o que cada ambiente suporta: servidor, CLI, navegador (CPython em WebAssembly), WASI, função serverless e embarcado. A leitura é **estática e de um arquivo** — um `roda` quer dizer *“não achei impedimento por esta via”*."},
 {"p": "Continue em [Compatibilidade](/docs/abi/compatibilidade) e [Portabilidade](/docs/alvos/portabilidade)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/cli/completar",
"title": "dataforge completar",
"description": "O Tab do terminal em bash, zsh e fish — gerado do mesmo catálogo do help.",
"blocos": [
 {"p": "`dataforge completar <shell>` imprime o script de autocompletar. Ele sai do **catálogo de comandos**: um comando novo aparece no Tab no dia em que entra na linguagem, e uma opção removida some."},
 {"code": """# bash
dataforge completar bash > ~/.local/share/bash-completion/completions/dataforge

# zsh
dataforge completar zsh > "${fpath[1]}/_dataforge"

# fish
dataforge completar fish > ~/.config/fish/completions/dataforge.fish""", "lang": "bash"},
 {"code": """$ dataforge ch<Tab>
check
$ dataforge check --<Tab>
--formato  --strict  --syntax-only  --help
$ dataforge run sr<Tab>
src/""", "lang": "text"},
 {"h2": "Três decisões"},
 {"table": {"head": ["Decisão", "Sem ela"], "rows": [
   ["as opções são **por comando**", "`check --<Tab>` ofereceria as sessenta opções de todos os comandos"],
   ["depois de `run`, `check`, `fmt`… completa **arquivo**", "o Tab oferece subcomando onde se digita `src/main.df`"],
   ["o script é texto puro, sem chamar o `dataforge`", "cada Tab custaria ~100 ms de interpretador — o bastante para desligar"]]}},
 {"callout": {"tipo": "dica", "titulo": "E o `df`", "texto": "O script registra o completar para `dataforge` **e** para `df` — os dois são o mesmo programa."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/cli/scripts",
"title": "A CLI em scripts",
"description": "Códigos de saída, cor, idioma, variáveis de ambiente, eval — e o que um script pode confiar.",
"blocos": [
 {"p": "A CLI é usada por gente e por programa. Para o programa, o que importa é o que não muda: o **código de saída**, a saída sem cor, e as variáveis de ambiente que mudam o comportamento."},
 {"h2": "Códigos de saída"},
 {"table": {"head": ["Código", "Significa"], "rows": [
   ["`0`", "deu certo — inclusive `check` com avisos (use `--strict` para reprovar)"],
   ["`1`", "falhou: erro no programa, teste reprovado, erro de análise, quebra de ABI"],
   ["`2`", "o seu programa pediu — `OS.exit(2)` sai com o código que você escolher"]]}},
 {"h2": "Variáveis de ambiente"},
 {"table": {"head": ["Variável", "Efeito"], "rows": [
   ["`NO_COLOR=1` ou `--no-color`", "sem códigos de cor — para log e CI"],
   ["`DF_IDIOMA=en`", "as mensagens em inglês (o padrão é português)"],
   ["`DATAFORGE_SEM_TROCA=1`", "ignora o pino de versão do `forge.toml`"],
   ["`DATAFORGE_REGISTRY`", "o registro de pacotes"],
   ["`DF_ATUALIZAR_SNAPSHOT=1`", "aceita as mudanças dos instantâneos"],
   ["`DATABASE_URL`", "a conexão que `Forge.de_ambiente()` lê"]]}},
 {"h2": "Uma linha, sem arquivo"},
 {"code": """dataforge eval 'out 2 ** 10'
dataforge eval 'out [1, 2, 3] >> morph n: n * 2'
dataforge --version            # o que o instalador e o CI conferem
dataforge converter script.py  # um ponto de partida, a partir de Python""", "lang": "bash"},
 {"h2": "Numa esteira"},
 {"code": """#!/bin/sh
set -e                                    # para no primeiro codigo diferente de zero
export NO_COLOR=1
dataforge fmt . --check
dataforge check . --strict --formato=github
dataforge seguranca . --strict
dataforge test --minimo=80
dataforge abi v1/lib.df src/lib.df        # 1 se a versao nova quebra""", "lang": "bash"},
 {"callout": {"tipo": "atencao", "titulo": "`--version`, e não a ajuda", "texto": "`dataforge --version` sai com a versão e o Python, e nada mais — é o que todo script chama para conferir a instalação. Ele caía no ramo sem argumentos e imprimia a ajuda inteira, que nenhum script sabe ler."}},
 {"p": "Continue em [Referência completa](/docs/cli/referencia)."},
]},
]
