# -*- coding: utf-8 -*-
"""Engenharia de dados: pipeline e qualidade."""

PAGINAS = [
{
"href": "/docs/tecnicas/pipeline",
"title": "Pipelines e orquestração",
"description": "DAG, dependências, retry e carga incremental — sem servidor, sem agendador, sem banco de metadados.",
"blocos": [
 {"p": "Airflow, Prefect e Dagster resolvem orquestração com um servidor, um banco de metadados e um agendador. `Arcane.Pipeline` resolve com **uma estrutura de dados e um laço** — o que cabe num processo só, que é onde a maioria dos pipelines de verdade vive."},
 {"code": """adopt Arcane.Pipeline as P

fluxo := P.fluxo("vendas")

P.etapa(fluxo, "extrair", extrair)
P.etapa(fluxo, "limpar",   limpar,   ["extrair"])
P.etapa(fluxo, "conferir", conferir, ["limpar"])
P.etapa(fluxo, "carregar", carregar, ["conferir"])

relatorio := P.rodar(fluxo)""", "lang": "df"},
 {"p": "A ordem sai das **dependências**, não da ordem em que você declarou — é a ordenação topológica que todo DAG faz. `P.grafico(fluxo)` mostra o resultado antes de rodar."},

 {"h2": "As três garantias"},
 {"h3": "1. Um ciclo é erro, não aviso"},
 {"code": """P.etapa(fluxo, "x", acao_x, ["y"])
P.etapa(fluxo, "y", acao_y, ["x"])

erro: as etapas x, y dependem umas das outras.
  nota: um ciclo não tem ordem possível
  dica: quebre o ciclo, ou junte as etapas numa só""", "lang": "text"},
 {"p": "Não há ordem que satisfaça as duas. Escolher uma arbitrariamente produziria um resultado que ninguém consegue explicar — e que muda entre execuções."},

 {"h3": "2. Falhou? quem depende é PULADO"},
 {"code": """ok      extrair
falhou  limpar     banco fora do ar
pulada  conferir   depende de limpar
pulada  carregar   depende de conferir
ok      notificar""", "lang": "text"},
 {"callout": {"tipo": "atencao", "titulo": "Rodar mesmo assim produz dado corrompido", "texto": "E dado corrompido é **pior** que dado ausente: o ausente alguém percebe. Uma etapa que não depende da que falhou continua rodando — `notificar`, acima, é justamente a que você quer que rode."}},

 {"h3": "3. Retry para a falha passageira"},
 {"code": """// 3 tentativas, esperando 2s, 4s entre elas
P.etapa(fluxo, "carregar", carregar, ["limpar"], 3, 2)""", "lang": "df"},
 {"p": "A espera **cresce** a cada tentativa. Se o banco está ocupado, insistir no mesmo ritmo mantém ele ocupado. E o relatório diz em qual tentativa passou — uma etapa que sempre precisa de três é um problema que a média esconde."},

 {"h2": "Carga incremental"},
 {"p": "Reprocessar tudo a cada execução é o que faz um pipeline de 10 minutos virar um de 6 horas em dois anos."},
 {"code": """fluxo := P.fluxo("vendas", "estado/vendas.json")

action extrair(ctx):
    desde := P.marca(fluxo, "ate") ?? "1970-01-01"
    novas := Banco.consultar(db,
        "SELECT * FROM vendas WHERE atualizado_em > ?", [desde])
    given len(novas) bigger 0:
        P.marcar(fluxo, "ate", maior(novas, "atualizado_em"))
    yield novas""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "A marca só avança quando a execução INTEIRA termina bem", "texto": "É a garantia que evita perda silenciosa. Avançar por etapa deixaria o checkpoint à frente do que foi realmente carregado — e o que ficou no meio some para sempre, sem ninguém notar. O arquivo é gravado num temporário e renomeado: um checkpoint pela metade é pior que nenhum."}},

 {"h2": "Rodar só um pedaço"},
 {"code": """P.rodar_ate(fluxo, "limpar")   // roda 'extrair' e 'limpar', e para""", "lang": "df"},
 {"p": "Ele resolve as dependências sozinho — roda o que `limpar` precisa, e nada além. É como se depura um pipeline longo sem esperar a carga."},

 {"h2": "O relatório"},
 {"code": """{
  "fluxo": "vendas",
  "ok": yes,
  "duracao": 12.4,
  "resumo": {"total": 4, "ok": 4, "falhou": 0, "pulada": 0, "saltada": 0},
  "etapas": [
    {"etapa": "extrair", "estado": "ok", "duracao": 8.1, "tentativas": 1},
    …
  ],
  "resultados": {"extrair": [ … ], "limpar": [ … ]}
}""", "lang": "json"},
 {"p": "O relatório é o produto. Sem ele, saber o que aconteceu exige ler log — e log de pipeline é o que ninguém lê até quebrar."},

 {"h2": "Condição: o mesmo fluxo em modos diferentes"},
 {"code": """P.etapa(fluxo, "carga_completa", completa, ["limpar"],
        1, 0, lambda ctx: MODO is "cheio")""", "lang": "df"},
 {"p": "A etapa é **saltada** quando a condição dá falso — e saltar não é falhar: o fluxo segue verde. É como se roda o mesmo pipeline em modo cheio e incremental sem duplicá-lo."},
]},

{
"href": "/docs/tecnicas/qualidade",
"title": "Qualidade de dados",
"description": "As seis dimensões, medidas e cobradas como parte do pipeline — não como um assert no fim.",
"blocos": [
 {"p": "Qualidade não é uma etapa no fim: é parte do pipeline. `Arcane.Qualidade` cobre as seis dimensões clássicas — **completude, validade, unicidade, consistência, precisão e atualidade**."},

 {"h2": "Por que isto não é um `assert`"},
 {"code": """assert todas(linhas, lambda l: l["id"] is not void)""", "lang": "df"},
 {"p": "Isso responde *passou?* e nada mais. Quando falha — e vai falhar, com dado de verdade — não diz **qual** linha, **quantas**, nem se é um caso isolado ou metade do arquivo. E é essa diferença que decide se o pipeline para ou segue."},
 {"code": """✗ 40000 linha(s), 3 violação(ões), 99.9% boas

  email  —  3 (0.0%)
      linha 1204: 'ana@' — fora do formato email
      linha 8891: 'sem-arroba' — fora do formato email
      linha 30112: '@dominio.co' — fora do formato email""", "lang": "text"},
 {"p": "*3 de 40.000 com e-mail inválido* leva a uma decisão. *falhou* leva a abrir o arquivo no editor."},

 {"h2": "Regras"},
 {"code": """REGRAS := {
    "id":       {"obrigatorio": yes, "tipo": "inteiro", "unico": yes},
    "produto":  {"obrigatorio": yes, "tipo": "texto", "minimo": 2, "maximo": 80},
    "valor":    {"tipo": "numero", "minimo": 0},
    "email":    {"formato": "email"},
    "situacao": {"em": ["ativo", "inativo"]},
    "score":    {"confere": lambda v: v % 2 is 0},
}

r := Q.conferir(linhas, REGRAS)""", "lang": "df"},
 {"table": {"head": ["Regra", "Cobra"], "rows": [
   ["`obrigatorio`", "veio preenchido — `void`, `\"\"` e `\"   \"` contam como vazio"],
   ["`tipo`", "`inteiro`, `numero`, `texto`, `booleano`, `lista`, `vault`"],
   ["`formato`", "`email`, `url`, `uuid`, `data`, `data_hora`, `cpf`, `cnpj`, `cep`, `telefone` — ou o seu regex"],
   ["`minimo` / `maximo`", "o valor, se for número; o tamanho, se for texto ou lista"],
   ["`em`", "está na lista permitida"],
   ["`unico`", "a chave não se repete"],
   ["`confere`", "a sua própria regra, como ação"]]}},
 {"callout": {"tipo": "nota", "titulo": "`\"   \"` conta como vazio", "texto": "Um campo com três espaços passou por *não é void* e mesmo assim não tem dado. Tratar os dois como o mesmo caso é o que evita descobrir isso três etapas adiante."}},

 {"h2": "Dentro do pipeline"},
 {"code": """action conferir(ctx):
    // levanta se a taxa boa ficar abaixo de 99%
    yield Q.esperar(ctx["limpar"], REGRAS, 0.99)""", "lang": "df"},
 {"p": "O mínimo existe porque nem todo dado precisa ser perfeito. Um arquivo com 0,1% de e-mails inválidos costuma poder seguir, e parar por isso seria pior que o problema. Quando ele levanta, a mensagem traz a taxa, quantas linhas e os cinco campos que mais falharam."},

 {"h2": "Perfil — quando o arquivo é desconhecido"},
 {"p": "Mede sem regra nenhuma. É por onde se começa, e é a partir daí que se escreve a regra:"},
 {"code": """p := Q.perfil(linhas)

// por campo:
//   preenchidos, vazios, completude
//   distintos, tipos, tipo_misto
//   minimo, maximo, media, mediana   (quando numérico)
//   menor_texto, maior_texto          (quando texto)
//   parece_chave                      (quando todos distintos)""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`tipo_misto` quase sempre é defeito de origem", "texto": "Dois tipos no mesmo campo vêm de CSV lido sem esquema, ou de JSON de fonte instável. É o achado mais útil do perfil, e o que mais causa erro três etapas adiante."}},

 {"h2": "Limpar"},
 {"code": """Q.sem_duplicadas(linhas, ["id"])     // mantém a PRIMEIRA de cada chave
Q.so_validas(linhas, REGRAS)         // só o que passa em tudo
Q.preencher(linhas, {"situacao": "ativo"})   // só o que está vazio""", "lang": "df"},
 {"p": "`sem_duplicadas` mantém a primeira, e não a última: em dado de origem a ordem costuma ser a de chegada, e a primeira é a original. É a mesma regra que faz `conferir` marcar o repetido na **segunda** ocorrência."},

 {"h2": "As dimensões, isoladas"},
 {"code": """Q.completude(linhas)                   // proporção preenchida por campo
Q.unicidade(linhas, "id")              // 1.0 = é chave
Q.duplicadas(linhas, ["id"])           // as repetidas, agrupadas
Q.fora_da_faixa(linhas, "valor", 0, 1000)
Q.atualidade(linhas, "atualizado_em", 7)   // quantas passaram de 7 dias""", "lang": "df"},
 {"p": "**Atualidade** é a dimensão que mais escapa da validação. Dado antigo não é dado errado — é dado que passou a mentir sem avisar."},
]},
]
