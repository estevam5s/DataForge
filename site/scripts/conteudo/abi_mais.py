# -*- coding: utf-8 -*-
"""Superfície e alvos — as páginas-raiz de /docs/abi e /docs/alvos (que
respondiam 404) e cinco páginas: a próxima versão calculada, o changelog,
aposentar sem quebrar, o contrato no CI e o 0.x.

`Abi.proxima_versao` e `Abi.changelog` entraram nesta leva.
"""

_VERSOES = '''adopt Arcane.Abi as Abi
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-abi-{randint(100000, 999999)}"
IO.mkdir(pasta)
antes := $"{pasta}/v1.df"
IO.write(antes, "action somar(a, b):\\n    yield a + b\\naction dobro(x):\\n    yield x * 2\\nrelay somar, dobro\\n")
'''

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/abi",
"title": "Superfície e contrato",
"description": "O que um módulo oferece é um contrato com quem o usa — e a ferramenta que diz, antes do release, se ele foi quebrado.",
"blocos": [
 {"p": "A **superfície** de um módulo é o que ele exporta com `relay`: nomes, parâmetros, campos. Quem adota o módulo depende exatamente disso. Mudar a superfície é mudar o contrato — e `Arcane.Abi` compara duas versões e diz se a mudança **quebra** quem usava a anterior."},
 {"code": _VERSOES + '''
depois := $"{pasta}/v2.df"
IO.write(depois, "action somar(a, b, c := 0):\\n    yield a + b + c\\naction dobro(x):\\n    yield x * 2\\nrelay somar, dobro\\n")

assert Abi.veredito(antes, depois) is "menor"          // acrescentou, não quebrou
assert Abi.compativel(antes, depois)
IO.remove_tree(pasta)''', "lang": "df"},
 {"cards": [
   {"href": "/docs/abi/superficie", "title": "A superfície é o contrato", "desc": "o que entra, e o que o relay esconde"},
   {"href": "/docs/abi/compatibilidade", "title": "O que quebra", "desc": "as onze regras, uma a uma"},
   {"href": "/docs/abi/versao", "title": "A próxima versão", "desc": "calculada da superfície, e não escolhida a olho"},
   {"href": "/docs/abi/changelog", "title": "O changelog", "desc": "o esqueleto que a superfície consegue escrever"},
   {"href": "/docs/abi/aposentar", "title": "Aposentar sem quebrar", "desc": "renomear com relay … as, e avisar antes de remover"},
   {"href": "/docs/abi/ci", "title": "O contrato no CI", "desc": "o release que quebra sem subir a versão maior é reprovado"},
   {"href": "/docs/abi/zero-x", "title": "Antes do 1.0", "desc": "o que o 0.x promete, e o que não"},
   {"href": "/docs/abi/simbolos", "title": "O mapa de símbolos", "desc": "quem exporta o quê"},
   {"href": "/docs/alvos", "title": "Alvos", "desc": "onde um programa roda"},
   {"href": "/docs/abi/mapa", "title": "ABI e alvos: o mapa", "desc": "o que existe, e o que não"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/abi/versao",
"title": "A próxima versão, calculada",
"description": "Abi.proxima_versao compara as duas superfícies e diz 2.0.0, 1.5.0 ou 1.4.3 — com o porquê.",
"blocos": [
 {"p": "O versionamento semântico é uma promessa: a **maior** sobe quando algo quebra, a **menor** quando algo entra sem quebrar, a **correção** quando a superfície não muda. A promessa só vale se o número for **calculado**; escolhido a olho, ele sobe menor numa quebra — e o `^1.4` de todo mundo que depende do pacote puxa a versão que quebra."},
 {"code": _VERSOES + '''
quebra := $"{pasta}/quebra.df"
IO.write(quebra, "action somar(a, b):\\n    yield a + b\\nrelay somar\\n")
acrescimo := $"{pasta}/acrescimo.df"
IO.write(acrescimo, "action somar(a, b):\\n    yield a + b\\naction dobro(x):\\n    yield x * 2\\naction triplo(x):\\n    yield x * 3\\nrelay somar, dobro, triplo\\n")

p := Abi.proxima_versao("1.4.2", antes, quebra)
assert p["proxima"] is "2.0.0"
out p["porque"]

assert Abi.proxima_versao("1.4.2", antes, acrescimo)["proxima"] is "1.5.0"
assert Abi.proxima_versao("1.4.2", antes, antes)["proxima"] is "1.4.3"
IO.remove_tree(pasta)''', "lang": "df"},
 {"table": {"head": ["Veredito", "Quando", "1.4.2 vira"], "rows": [
   ["`maior`", "um nome sumiu, um parâmetro obrigatório entrou, um parâmetro mudou de nome", "2.0.0"],
   ["`menor`", "um nome novo, um parâmetro opcional novo", "1.5.0"],
   ["`correcao`", "a superfície é a mesma", "1.4.3"],
   ["`desconhecido`", "uma das versões não compila", "não calcula — `proxima` é `void`"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Renomear parâmetro é quebra", "texto": "A chamada com nome existe aqui — `somar(a := 1, b := 2)` —, então o **nome** do parâmetro é contrato, e não só a posição. Uma ferramenta feita para C não teria esta regra."}},
 {"p": "A superfície vê o que é **visível**. Uma mudança de comportamento com a mesma assinatura — a ação passa a arredondar diferente — é quebra, e só um teste pega. O cálculo é o piso, não o teto."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/abi/changelog",
"title": "O changelog que a superfície escreve",
"description": "Abi.changelog separa quebra de acréscimo, com a dica de migração de cada uma — o esqueleto, e não a nota inteira.",
"blocos": [
 {"p": "Todo release precisa de uma seção no CHANGELOG, e a parte que mais se esquece é justamente a que mais importa: **o que quebrou**. `Abi.changelog` escreve o esqueleto a partir da comparação — cada quebra com a dica do que fazer, cada acréscimo — e deixa para você o porquê."},
 {"code": _VERSOES + '''
depois := $"{pasta}/v2.df"
IO.write(depois, "action somar(a, b, c := 0):\\n    yield a + b + c\\naction triplo(x):\\n    yield x * 3\\nrelay somar, triplo\\n")

texto := Abi.changelog(antes, depois, "2.0.0")
out texto
assert texto.starts_with("## 2.0.0")
assert texto.contains("### Quebra compatibilidade")
assert texto.contains("`dobro`")                 // o que sumiu
assert texto.contains("### Adicionado")
IO.remove_tree(pasta)''', "lang": "df"},
 {"list": [
   "**Quebra primeiro.** É o que quem atualiza precisa ler antes de qualquer outra coisa.",
   "**Com a dica.** \"`dobro` foi removida\" não diz o que fazer; a dica diz (\"mantenha o nome como casca que chama o novo, ou suba a versão maior\").",
   "**O porquê é seu.** A ferramenta sabe **o que** mudou na superfície; **por que** mudou — e o que isso resolve — só quem escreveu sabe."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/abi/aposentar",
"title": "Aposentar sem quebrar",
"description": "Renomear com relay … as, avisar com Evolucao.obsoleta, e só então remover — em duas versões, e não em uma.",
"blocos": [
 {"p": "Um nome ruim numa biblioteca publicada não se troca de uma vez: quem o usa quebra no dia da atualização. O caminho tem três passos, e cada um é uma versão."},
 {"table": {"head": ["Versão", "Faz", "Quem usa o nome velho"], "rows": [
   ["1.5 (menor)", "exporta o novo, e o velho como apelido: `relay somar, somar as soma`", "continua funcionando"],
   ["1.6 (menor)", "marca o velho com `Evolucao.obsoleta`", "funciona, com aviso na saída de erro"],
   ["2.0 (maior)", "remove o velho", "quebra — mas foi avisado por duas versões"]]}},
 {"code": _VERSOES + '''
// o renomeio com apelido: o nome velho continua exportado
com_apelido := $"{pasta}/v15.df"
IO.write(com_apelido, "action somar(a, b):\\n    yield a + b\\naction duplicar(x):\\n    yield x * 2\\nrelay somar, duplicar, duplicar as dobro\\n")
assert Abi.veredito(antes, com_apelido) is "menor"        // nada quebrou

sem_apelido := $"{pasta}/v2.df"
IO.write(sem_apelido, "action somar(a, b):\\n    yield a + b\\naction duplicar(x):\\n    yield x * 2\\nrelay somar, duplicar\\n")
assert Abi.veredito(antes, sem_apelido) is "maior"        // o 'dobro' sumiu
IO.remove_tree(pasta)''', "lang": "df"},
 {"p": "O aviso da versão intermediária vem de [`Arcane.Evolucao`](/docs/bibliotecas/obsolescencia): `obsoleta(motivo, desde, use)` avisa **uma vez** por ação, na saída de erro, e `DF_OBSOLETOS=erro` transforma o aviso em falha — para o CI de quem depende descobrir antes do 2.0."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/abi/ci",
"title": "O contrato no CI",
"description": "dataforge abi sai com erro quando a versão declarada é menor que a quebra exige — antes do release, e não depois.",
"blocos": [
 {"p": "Conferir a superfície à mão é o tipo de passo que se pula na sexta-feira. No CI ele não é pulado: o job compara o módulo publicado com o de agora, e **reprova** o release que quebra o contrato sem subir a versão maior."},
 {"code": '''# no CI, com a última versão publicada baixada em ultima/
dataforge abi ultima/src/main.df src/main.df
# sai com 0 (compatível), 2 (quebra) — e o relatório diz qual regra''', "lang": "bash"},
 {"code": _VERSOES + '''
depois := $"{pasta}/v2.df"
IO.write(depois, "action somar(a):\\n    yield a\\nrelay somar\\n")

versao_declarada := "1.5.0"                         // o que está no forge.toml
calculada := Abi.proxima_versao("1.4.2", antes, depois)["proxima"]
subiu_certo := versao_declarada.split(".")[0] is calculada.split(".")[0]
assert not subiu_certo                             // 1.5.0 numa quebra: reprovar
out $"declarada {versao_declarada}, exigida {calculada}"
IO.remove_tree(pasta)''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "O que não compila não é julgado", "texto": "Se uma das duas versões não compila, o veredito é `desconhecido` e o job não reprova por contrato — reprova pelo erro de compilação, que é o problema real. Um falso alarme de quebra reprovaria um release correto, e na segunda vez a conferência inteira seria desligada."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/abi/zero-x",
"title": "Antes do 1.0",
"description": "O 0.x anuncia que a API ainda não assentou: quebra sobe o menor, acréscimo sobe a correção.",
"blocos": [
 {"p": "Pelo versionamento semântico, qualquer coisa pode mudar antes do 1.0. Na prática, os gerenciadores de pacote (Cargo, npm) tratam o 0.x com uma regra própria: o **menor** faz o papel do maior. `^0.4.2` aceita 0.4.9, mas não 0.5.0. `Abi.proxima_versao` segue a mesma convenção:"},
 {"code": _VERSOES + '''
quebra := $"{pasta}/quebra.df"
IO.write(quebra, "action somar(a, b):\\n    yield a + b\\nrelay somar\\n")
assert Abi.proxima_versao("0.4.2", antes, quebra)["proxima"] is "0.5.0"    // não 1.0.0
assert Abi.proxima_versao("0.4.2", antes, antes)["proxima"] is "0.4.3"
IO.remove_tree(pasta)''', "lang": "df"},
 {"table": {"head": ["Mudança", "0.x", "1.x em diante"], "rows": [
   ["quebra", "0.4 → **0.5**", "1.4 → **2.0**"],
   ["acréscimo", "0.4.2 → 0.4.3", "1.4 → 1.5"],
   ["correção", "0.4.2 → 0.4.3", "1.4.2 → 1.4.3"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Por que não pular para o 1.0", "texto": "Uma quebra no 0.x não deveria ir para 1.0 sozinha: o 1.0 é uma **promessa** de estabilidade, e fazê-la por causa de uma quebra — e não porque a API assentou — é prometer sem querer. Subir para 1.0 é decisão de quem mantém, e nenhuma ferramenta a toma."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/alvos",
"title": "Alvos",
"description": "Onde um programa roda — lido dos adopt, antes de rodar — e o que WebAssembly quer dizer aqui.",
"blocos": [
 {"p": "Um programa que adota `Arcane.C` não roda no navegador; um que adota `Arcane.OS.fork` não roda no Windows. `Arcane.Alvo` lê os `adopt` do arquivo e responde, antes de rodar, em quais alvos ele funciona — e o motivo de cada recusa."},
 {"code": '''adopt Arcane.Alvo as Alvo

assert len(Alvo.alvos()) bigger 0
out Alvo.alvos()''', "lang": "df"},
 {"cards": [
   {"href": "/docs/alvos/portabilidade", "title": "Onde este programa roda", "desc": "os perfis de alvo, e o que cada um recusa"},
   {"href": "/docs/alvos/wasm", "title": "WebAssembly, com precisão", "desc": "rodar em WASM existe; compilar para WASM, não"},
   {"href": "/docs/abi/mapa", "title": "ABI e alvos: o mapa", "desc": "o que existe, e o que não"}]},
 {"callout": {"tipo": "nota", "titulo": "A leitura é de um arquivo", "texto": "Um módulo alcançado **indiretamente** — pelo `adopt` de um `adopt` — não aparece. `roda` quer dizer \"não achei impedimento por esta via\", e `Alvo.limites()` diz isso em execução."}},
]},
]
