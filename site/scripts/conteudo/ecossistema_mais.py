# -*- coding: utf-8 -*-
"""Ecossistema — a página-raiz (que respondia 404) e cinco páginas:
glossário, comparação com outras linguagens, a arquitetura em arquivos,
as decisões de desenho e os números.

`Ecossistema.glossario` e `definir` entraram nesta leva; cada termo
aponta para uma página, e um teste confere que ela existe.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema",
"title": "O ecossistema",
"description": "O que a linguagem tem, o que ela não tem, e por quê — conferido contra o disco, e não escrito de memória.",
"blocos": [
 {"p": "Esta seção responde perguntas sobre a linguagem como um todo: quais peças existem, quais não, que princípios decidiram o desenho, e onde o tempo de um programa vai. As respostas saem do **próprio código** — `Arcane.Ecossistema` confere o inventário contra os arquivos, e um módulo novo fora do mapa reprova a suíte."},
 {"code": '''adopt Arcane.Ecossistema as E

n := E.numeros()
assert n["modulos"] bigger 80
assert n["existem"] + n["equivalem"] + n["nao_existem"] is n["componentes"]
assert E.conferir()["ok"]''', "lang": "df"},
 {"cards": [
   {"href": "/docs/ecossistema/componentes", "title": "O ecossistema, conferido", "desc": "cada peça, com o arquivo que a implementa"},
   {"href": "/docs/ecossistema/ausencias", "title": "O que não existe", "desc": "e o que há no lugar"},
   {"href": "/docs/ecossistema/glossario", "title": "Glossário", "desc": "os termos, com a página que os explica"},
   {"href": "/docs/ecossistema/comparacao", "title": "Comparada com outras", "desc": "Python, JavaScript, Go e Rust, lado a lado"},
   {"href": "/docs/ecossistema/arquitetura", "title": "A arquitetura em arquivos", "desc": "onde mora cada fase"},
   {"href": "/docs/ecossistema/decisoes", "title": "Decisões de desenho", "desc": "o que foi escolhido, e o que custou"},
   {"href": "/docs/ecossistema/numeros", "title": "Os números", "desc": "contados do código, e não escritos à mão"},
   {"href": "/docs/ecossistema/principios", "title": "Os dez princípios", "desc": "com prova que roda"},
   {"href": "/docs/ecossistema/tensoes", "title": "As tensões", "desc": "onde dois princípios brigam"},
   {"href": "/docs/ecossistema/percurso", "title": "Onde o tempo vai", "desc": "as fases de um arquivo, medidas"},
   {"href": "/docs/ecossistema/referencia", "title": "Referência rápida", "desc": "a linguagem numa página"},
   {"href": "/docs/ecossistema/mapa", "title": "Ecossistema: o mapa", "desc": "tudo, com o veredito"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/glossario",
"title": "Glossário",
"description": "Os termos da documentação, com a definição curta e a página que explica cada um — conferidos contra o site.",
"blocos": [
 {"p": "A documentação usa termos de compiladores, de concorrência, de domínio e de protocolos. O glossário é também um **dado**: `Ecossistema.glossario()` devolve a lista, e `definir(termo)` busca um — com sugestão quando o nome vem quase certo."},
 {"code": '''adopt Arcane.Ecossistema as E

d := E.definir("SSA")
assert d["pagina"] is "/docs/compilador/ssa"
out d["definicao"]

sugestao := void
monitor:
    E.definir("dominacia")
handle Error as e:
    sugestao := e.dica
assert sugestao.contains("dominancia")

assert len(E.glossario()) bigger_eq 38''', "lang": "df"},
 {"table": {"head": ["Termo", "Em uma linha"], "rows": [
   ["**ABI**", "a superfície do que o `relay` exporta, comparada entre versões — [ver](/docs/abi)"],
   ["**agregado**", "a única porta de escrita de um grupo de objetos do domínio — [ver](/docs/dominio/agregados)"],
   ["**ator**", "estado com dono, alcançado só por mensagem — [ver](/docs/concorrencia/atores)"],
   ["**canal**", "o cano entre fibras que suspende quem envia quando cheio — [ver](/docs/runtime/canais)"],
   ["**chamada de cauda**", "`yield f(…)` que vira salto — [ver](/docs/compilador/cauda)"],
   ["**contrapressão**", "o consumidor lento freando o produtor — [ver](/docs/runtime/contrapressao)"],
   ["**CQRS**", "o modelo que decide separado do que responde — [ver](/docs/dominio/cqrs)"],
   ["**cursor**", "\"onde parou\" numa listagem, opaco — [ver](/docs/api/paginacao)"],
   ["**dominância**", "todo caminho até B passa por A — [ver](/docs/compilador/dominancia)"],
   ["**ETag**", "a etiqueta de uma versão de recurso HTTP — [ver](/docs/api/precondicoes)"],
   ["**fibra**", "`stream action` conduzido pelo laço — [ver](/docs/runtime/fibras)"],
   ["**fonte de eventos**", "guardar fatos, e derivar o estado — [ver](/docs/dominio/fonte-de-eventos)"],
   ["**idempotência**", "repetir o pedido sem repetir o efeito — [ver](/docs/api/idempotencia)"],
   ["**orçamento de erro**", "as falhas que o SLO permite — [ver](/docs/observabilidade/slo)"],
   ["**projeção**", "modelo de leitura montado dos eventos — [ver](/docs/dominio/projecoes)"],
   ["**sinal**", "um valor que sabe quem depende dele — [ver](/docs/reativo/sinais)"],
   ["**SSA**", "cada nome recebe valor uma vez só — [ver](/docs/compilador/ssa)"],
   ["**STM**", "escritas que acontecem juntas, ou não acontecem — [ver](/docs/concorrencia/stm)"],
   ["**taxa de queima**", "a velocidade com que o orçamento é gasto — [ver](/docs/observabilidade/slo)"],
   ["**varint**", "o inteiro de tamanho variável do protobuf — [ver](/docs/estruturas/varint)"]]}},
 {"p": "A lista completa, com 38 termos, sai de `E.glossario()`. Ela é conferida: um termo que aponta para uma página que não existe reprova a suíte de testes."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/comparacao",
"title": "Comparada com outras linguagens",
"description": "Python, JavaScript, Go e Rust lado a lado: sintaxe, tipos, concorrência, erros — e onde DataForge escolheu diferente.",
"blocos": [
 {"p": "DataForge roda sobre o CPython, e em execução se parece mais com Python do que com qualquer outra. Na **escrita**, as escolhas vieram de lugares diferentes — e esta tabela diz de onde, e o que ficou de fora."},
 {"table": {"head": ["", "DataForge", "Python", "JavaScript", "Go", "Rust"], "rows": [
   ["atribuição", "`x := 1`", "`x = 1`", "`let x = 1`", "`x := 1`", "`let x = 1`"],
   ["tipos", "opcionais, conferidos pelo `check` e em execução", "opcionais, só por ferramenta", "TypeScript à parte", "estáticos", "estáticos, com dono"],
   ["nulo", "`void`, com `??` e `?.`", "`None`", "`null`/`undefined`", "`nil`", "`Option`"],
   ["erro", "`monitor`/`handle`, e `Resultado` como valor", "`try`/`except`", "`try`/`catch`", "valor de retorno", "`Result`"],
   ["concorrência", "threads, laço, fibras, atores, STM, processos", "threads + GIL, asyncio", "laço único", "goroutines + canais", "threads + async"],
   ["divisão inteira", "`~/`", "`//`", "`Math.floor(a/b)`", "`/` em inteiros", "`/` em inteiros"],
   ["pipeline", "`>> sift`, `>> morph`", "—", "—", "—", "iteradores"],
   ["pacotes", "`dataforge add`, com lock e sha256", "pip", "npm", "go mod", "cargo"]]}},
 {"code": '''// o canal do Go, o ator do Erlang e o Resultado do Rust — na mesma linguagem
adopt Arcane.Laco as L
adopt Arcane.Concurrent as P
adopt Arcane.Resultado as Res

c := L.canal(1)
a := P.ator(lambda soma, v: soma + v, 0)
a.enviar(5)
assert a.parar() is 5
assert Res.ok(3).deu_certo()''', "lang": "df"},
 {"h2": "O que ficou de fora, de propósito"},
 {"list": [
   "**Compilação para código nativo.** O interpretador compila a árvore para fechamentos do Python (1,5× a 1,8×); o teto dessa técnica é ~6,5×. Ir além exigiria sair do Python — e da dependência zero.",
   "**Operadores de bits.** `>>`, `|` e `&` já têm dono (pipeline, união e interseção de tipos); as [operações de bits](/docs/estruturas/operacoes-de-bits) são funções.",
   "**Macro que reescreve sintaxe.** Há [macro sobre a árvore](/docs/metaprogramacao/macros), mas não uma que invente palavra nova."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/arquitetura",
"title": "A arquitetura em arquivos",
"description": "Onde mora cada fase: do lexer ao interpretador, e as ferramentas que leem as mesmas estruturas.",
"blocos": [
 {"p": "A linguagem inteira mora em `dataforge/`, em Python, sem dependência externa em tempo de execução. Cada fase é um arquivo, e as ferramentas leem as **mesmas** estruturas que o interpretador — uma segunda leitura divergiria da primeira, e aí duas respostas para a mesma pergunta passariam a discordar."},
 {"table": {"head": ["Fase", "Arquivo", "Entrega"], "rows": [
   ["lexer", "`lexer.py`, `tokens.py`", "tokens com linha e coluna"],
   ["parser", "`parser.py`, `ast_nodes.py`", "a árvore"],
   ["analisador", "`typechecker.py`", "erros e avisos antes de rodar"],
   ["onde mora um `adopt`", "`resolucao.py`", "o caminho — a **única** cópia da regra"],
   ["o que um arquivo oferece", "`superficie.py`", "a superfície, sem executar — usada pelo `check` e pela ABI"],
   ["execução", "`interpreter.py`", "a semântica"],
   ["compilação", "`compilador.py`", "a árvore vira fechamentos, uma vez"],
   ["representações do meio", "`hir.py`, `mir.py`, `ssa.py`, `lir.py`", "o que o compilador vê"],
   ["biblioteca", "`stdlib/`", "86 módulos"],
   ["ferramentas", "`formatter.py`, `linter.py`, `testrunner.py`, `lsp.py`, `dap.py`", "fmt, lint, test, editor, depurador"]]}},
 {"code": '''adopt Arcane.Ecossistema as E

conferido := E.conferir()
assert conferido["ok"]                       // nenhum caminho citado sumiu
assert len(conferido["orfaos"]) is 0         // nenhum arquivo ficou fora do mapa''', "lang": "df"},
 {"p": "O fluxo de um arquivo: `texto → tokenize → parse → [check] → Interpreter.run`. O interpretador despacha por nome de classe — um nó `GivenBlock` procura `exec_GivenBlock` —, e por isso acrescentar um recurso à linguagem é mexer em cinco lugares: tokens, lexer, nós e parser, interpretador, analisador. O guia está em [Contribuir](/docs/contribuir)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/decisoes",
"title": "Decisões de desenho",
"description": "Doze escolhas que definem a linguagem, com o que cada uma evita e o que cada uma custa.",
"blocos": [
 {"p": "Toda linguagem é um conjunto de escolhas, e cada escolha tem um preço. Esta página as lista com o preço junto — uma lista de decisões sem custo seria propaganda."},
 {"table": {"head": ["Decisão", "Evita", "Custa"], "rows": [
   ["dependência zero em execução", "instalação que quebra, rede fechada sem pacote", "reescrever o que o ecossistema Python já tem"],
   ["`//` é comentário; divisão é `~/`", "confusão com o comentário de C/JS", "`// 3 parcelas` divide — e o parser agora recusa"],
   ["uma instrução por linha", "a instrução solta que some calada", "nenhum — nada no repositório usava duas"],
   ["o analisador cala quando não prova", "o falso alarme que ensina a ignorar", "deixa passar o que não consegue provar"],
   ["o campo vence o método", "o método que nunca roda", "`v.nome()` inalcançável se houver campo `nome`"],
   ["`record` imutável", "o objeto que muda por baixo de quem o guardou", "`with` para cada mudança"],
   ["mensagens em português, com `DF_IDIOMA=en`", "o erro de execução numa língua e o do `check` em outra", "a tradução é no desenho, e cobre parte"],
   ["`given` compartilha escopo; `cycle` não", "o nome decidido em dois ramos que não existe depois", "—"],
   ["erro de sistema é da família certa", "`handle RuntimeError` pegando tudo", "saber o nome da família"],
   ["concorrência sem sincronização automática", "o custo de trava em todo acesso", "o `check` avisa, mas a trava é sua"],
   ["`@f()` é fábrica, `@f` é aplicação", "`@app.texto()` recebendo a ação como padrão", "—"],
   ["o corpo de `lambda` absorve ternário e `??`", "`lambda x: v[x] ?? 0` que nunca usa o padrão", "o pipeline continua precisando de parênteses"]]}},
 {"callout": {"tipo": "nota", "titulo": "As três últimas são desta versão", "texto": "Foram achadas escrevendo a documentação: um bloco que devia rodar e não rodava, e a causa era da linguagem. É o motivo de todo bloco desta documentação ser **executado** pela suíte de testes."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/numeros",
"title": "Os números",
"description": "Módulos, símbolos, comandos, componentes — contados do código a cada vez, e nunca escritos à mão.",
"blocos": [
 {"p": "Um número escrito à mão numa documentação envelhece no primeiro módulo novo, e ninguém lê a mesma página duas vezes para notar. Os números desta página saem de `Ecossistema.numeros()`, que os **conta** do código."},
 {"code": '''adopt Arcane.Ecossistema as E

n := E.numeros()
out n
assert n["modulos"] bigger 80
assert n["simbolos"] bigger 2000
assert n["comandos"] bigger 50''', "lang": "df"},
 {"table": {"head": ["Campo", "Conta"], "rows": [
   ["`modulos`", "módulos da biblioteca padrão, sem os apelidos"],
   ["`simbolos`", "funções, classes e constantes exportadas por eles"],
   ["`comandos`", "comandos da CLI, lidos do catálogo que despacha"],
   ["`componentes`", "as peças do mapa, e quantas existem, equivalem ou não existem"],
   ["`alvos`", "os perfis de onde um programa roda"]]}},
 {"p": "Os números do site — na página inicial, na API pública, no README — têm uma trava: um teste compara cada um com a contagem real, e reprova quando divergem. Foi ela que achou o `.deb` dizendo 38 módulos quando eram 39."},
]},
]
