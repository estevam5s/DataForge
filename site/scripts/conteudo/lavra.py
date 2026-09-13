# -*- coding: utf-8 -*-
"""Arcane.Lavra — a consulta tipada do DataForge.

Nove páginas cobrindo o assunto inteiro: esquema, linguagem de
consulta, resolvedores, desempenho, segurança, servidor, federação e
prática.
"""


def cod(texto, lang="df"):
    return {"code": texto.strip("\n"), "lang": lang}


def consulta(texto):
    """Um bloco na linguagem de CONSULTA do Lavra, e não em DataForge.

    A distinção não é cosmética: `tools/verificar_docs.py` confere cada
    bloco, e ele confere um `lavra` com o leitor do próprio módulo. Um
    exemplo de consulta errado nesta documentação reprova a suíte, do
    mesmo jeito que um exemplo de DataForge errado.
    """
    return {"code": texto.strip("\n"), "lang": "lavra"}


PAGINAS = [

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra",
"title": "Lavra",
"description": "A consulta tipada do DataForge: o cliente diz exatamente quais campos quer, e recebe exatamente aqueles.",
"blocos": [
 {"p": "**Lavra** é a consulta tipada do DataForge. O cliente diz **exatamente** o que precisa, numa consulta, e recebe exatamente aquilo — nem um campo a mais, nem uma segunda chamada para buscar o que faltou."},
 consulta("""
busca:
    usuario(id: 7):
        nome
        pedidos(limite: 3):
            numero
            total
"""),
 {"p": "Uma rota REST devolve o que o **servidor** decidiu devolver. Quem precisa de menos carrega o resto; quem precisa de mais faz outra chamada. Numa tela de celular com rede ruim, as duas coisas custam."},
 {"componente": "diagrama-consulta"},

 {"h2": "O nome"},
 {"p": "**Lavra** é a extração de um veio de minério — e `lavrar` também é redigir um documento. As duas coisas que este módulo faz: um esquema é *lavrado*, e a consulta *lavra* dele exatamente o minério que quer. Segue a metáfora da forja, como [Kiln](/docs/kiln), [Crucible](/docs/crucible) e [Vitrine](/docs/vitrine)."},

 {"h2": "O esquema nasce dos seus records"},
 {"p": "Esta é a decisão que define o módulo. **Não há uma segunda linguagem de esquema ao lado da linguagem:**"},
 cod("""
record Usuario:
    id: Integer
    nome: String
    email: String

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Usuario)
"""),
 {"p": "O GraphQL precisa de um SDL próprio porque o servidor pode estar escrito em qualquer coisa, e o esquema tem de existir fora dela. Aqui o servidor é DataForge, e o `record` já diz nome, campo e tipo. Um arquivo de esquema ao lado seria uma **segunda fonte de verdade** para divergir da primeira."},
 {"callout": {"tipo": "nota", "titulo": "O que o record não diz",
              "texto": "O que é obrigatório, o que é lista de quê, qual campo é calculado e por quem — isso entra com `Lavra.campo`. O record dá a forma; o esquema dá o contrato."}},

 {"h2": "A consulta é indentada"},
 {"p": "Porque a linguagem é. Uma consulta escrita ao lado do código que a usa tem de parecer com ele — e o `:` no fim marca \"isto tem seleção dentro\", exatamente como em `given`, `cycle` e `action`."},
 {"table": {"head": ["GraphQL", "Lavra"], "rows": [
   ["`{ … }`", "indentação"],
   ["`query`", "`busca`"],
   ["`mutation`", "`mudanca`"],
   ["`subscription`", "`assinatura`"],
   ["`type`", "`tipo`"],
   ["`input`", "`entrada`"],
   ["`interface`", "`contrato`"],
   ["`union`", "`uniao`"],
   ["`scalar`", "`escalar`"],
   ["`fragment X on T`", "`trecho X em T`"],
   ["`...X`", "`...X`"],
   ["`... on T { }`", "`... em T:`"],
   ["`@include(if:)`", "`@incluir(se:)`"],
   ["`@skip(if:)`", "`@pular(se:)`"],
   ["`$v: T = padrão`", "`$v: T := padrão`"],
   ["`!` e `[ ]`", "iguais"],
 ]}},
 {"p": "`!` e `[ ]` são a **única** coisa emprestada da escrita do GraphQL, e de propósito: quem já conhece lê sem aprender nada, e quem não conhece aprende dois símbolos."},

 {"h2": "Um exemplo inteiro"},
 cod("""
adopt Arcane.Lavra as Lavra

record Usuario:
    id: Integer
    nome: String
    email: String

usuarios := [Usuario(1, "Ana", "ana@forja.co"), Usuario(2, "Bia", "bia@forja.co")]

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Usuario)
Lavra.campo(esq, "Usuario", "nome", "String!")

action achar(raiz, args, ctx):
    achados := [u cycle u in usuarios given u.id is args["id"]]
    yield achados[0] given len(achados) bigger 0 otherwise void

Lavra.busca(esq, "usuario", "Usuario", args := {"id": "Integer!"}, resolve := achar)
Lavra.conferir(esq)

r := Lavra.executar(esq, \"\"\"
busca:
    usuario(id: 1):
        nome
\"\"\")

out r["dados"]
"""),
 cod("""{usuario: {nome: Ana}}""", "text"),

 {"h2": "O que ele traz"},
 {"table": {"head": ["Assunto", "Página"], "rows": [
   ["Tipos, campos, argumentos, nulidade, listas", "[O esquema](/docs/lavra/esquema)"],
   ["Enums, entradas, escalares, contratos, uniões", "[O esquema](/docs/lavra/esquema)"],
   ["Busca, mudança, assinatura, apelidos", "[A consulta](/docs/lavra/consulta)"],
   ["Trechos, variáveis, diretivas, introspecção", "[A consulta](/docs/lavra/consulta)"],
   ["Resolvedores, contexto, erros, autorização", "[Resolvedores](/docs/lavra/resolvedores)"],
   ["Lote contra o N+1, paginação, cache", "[Desempenho](/docs/lavra/desempenho)"],
   ["Validação, limites, rate limit, observabilidade", "[Segurança](/docs/lavra/seguranca)"],
   ["HTTP, WebSocket, tempo real, cliente", "[O servidor](/docs/lavra/servidor)"],
   ["Vários serviços, portão, composição", "[Federação](/docs/lavra/federacao)"],
   ["CRUD, banco, DDD, testes, deploy, CI", "[Na prática](/docs/lavra/pratica)"],
 ]}},

 {"h2": "O que ele NÃO é"},
 {"p": "Lavra **não é GraphQL**. Não fala o protocolo do GraphQL, não lê arquivos de SDL, e uma ferramenta de GraphQL não conversa com ele. As ideias são as mesmas — e são boas —, a escrita é a do DataForge."},
 {"p": "Ele também não é um planejador de consulta distribuído: a [federação](/docs/lavra/federacao) compõe esquemas e resolve a fronteira com o lote, e não com um plano de execução entre serviços. Um subconjunto pela metade seria pior que a honestidade de não ter."},
 {"cards": [
   {"href": "/docs/lavra/esquema", "title": "O esquema", "desc": "Tipos, campos, contratos, uniões."},
   {"href": "/docs/lavra/consulta", "title": "A consulta", "desc": "A linguagem que o cliente escreve."},
   {"href": "/docs/lavra/servidor", "title": "O servidor", "desc": "HTTP e tempo real, sobre o Kiln."},
 ]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/esquema",
"title": "O esquema",
"description": "Tipos, campos, argumentos, nulidade, listas, enums, entradas, escalares próprios, contratos e uniões.",
"blocos": [
 {"p": "O esquema é **tudo o que a consulta pode pedir**, e quem responde por cada parte. Ele é montado uma vez, na subida, e conferido inteiro antes de a primeira consulta chegar."},

 {"h2": "Tipos, a partir de records"},
 cod("""
record Usuario:
    id: Integer
    nome: String
    email: String

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Usuario)
"""),
 {"p": "`Lavra.tipo` lê os campos declarados. Também aceita um **blueprint** e um **vault** de tipos, para quando o dado não vem de um record:"},
 cod("""
Lavra.tipo(esq, {"id": "Integer", "nome": "String"}, nome := "Cliente")
Lavra.tipo(esq, Usuario, esconder := ["senha_hash"])
"""),
 {"callout": {"tipo": "atencao", "titulo": "Esconder é parte do esquema",
              "texto": "Um campo que existe no record e não está no esquema **não pode ser pedido**. É a forma mais barata de garantir que `senha_hash` nunca saia: para quem consulta, ele não existe."}},

 {"h2": "A notação de tipo"},
 {"table": {"head": ["Escrita", "Significa"], "rows": [
   ["`String`", "pode ser `void`"],
   ["`String!`", "**nunca** é `void`"],
   ["`[String]`", "lista que pode ser void, de itens que podem ser void"],
   ["`[String!]!`", "lista que nunca é void, de itens que nunca são void"],
 ]}},
 {"p": "O `!` não é decoração: ele muda o que acontece quando o resolvedor falha. Um campo que admite `void` vira `void` e o resto da resposta segue; um `!` **sobe** o erro para o pai, e daí para cima, até achar alguém que admita `void`."},
 {"p": "É a única forma de a promessa do `!` valer alguma coisa. Se um `String!` pudesse voltar vazio, o cliente teria de conferir cada campo mesmo assim — e aí o `!` não diria nada."},

 {"h2": "Campos calculados"},
 cod("""
action pedidos_de(usuario, args, ctx):
    yield Banco.pedidos_do_usuario(usuario.id)

Lavra.campo(esq, "Usuario", "pedidos", "[Pedido!]!",
    args := {"limite": {"tipo": "Integer", "padrao": 10}},
    resolve := pedidos_de,
    descricao := "Os pedidos deste usuário, do mais recente ao mais antigo.")
"""),
 {"p": "Um campo **sem** `resolve` lê o valor do próprio objeto — do record, do vault, da instância. É o caso da maioria, e por isso é o padrão."},

 {"h2": "Argumentos"},
 cod("""
args := {
    "id": "Integer!",                              // obrigatório
    "limite": {"tipo": "Integer", "padrao": 10},   // com padrão
    "ordem": {"tipo": "Ordem", "padrao": "Recente"},
}
"""),
 {"callout": {"tipo": "nota", "titulo": "Sem padrão é diferente de padrão void",
              "texto": "Um argumento **sem** padrão é exigido quando o tipo é `!`. Um **com** padrão `void` já tem resposta. Os dois casos existem, e confundi-los faz um campo obrigatório passar despercebido."}},

 {"h2": "Enums"},
 cod("""
enum Estado:
    Rascunho
    Publicado := "pub"

Lavra.enum(esq, "Estado", Estado)
"""),
 {"p": "O `enum` da linguagem entra direto. A consulta escreve o **nome** (`Publicado`), e o resolvedor recebe o **valor** (`\"pub\"`). A tradução é do esquema, e é o que permite trocar o valor guardado no banco sem quebrar quem consulta."},

 {"h2": "Entradas: o que uma mudança recebe"},
 cod("""
record NovoUsuario:
    nome: String
    email: String

Lavra.entrada(esq, NovoUsuario)
Lavra.campo(esq, "NovoUsuario", "nome", "String!")
Lavra.campo(esq, "NovoUsuario", "email", "String!")

Lavra.mudanca(esq, "criarUsuario", "Usuario!",
    args := {"dados": "NovoUsuario!"}, resolve := criar)
"""),
 {"p": "Entrada e saída são tipos **diferentes**, de propósito. O `Usuario` que sai tem `id` e `criado_em`; o que entra não tem nem um nem outro. Usar o mesmo tipo nos dois lados obrigaria a marcar metade dos campos como opcionais — e aí nenhum deles seria conferido."},
 {"callout": {"tipo": "atencao", "titulo": "Campo desconhecido é recusado, não ignorado",
              "texto": "Uma entrada com `emial` falha, e diz quais campos existem. Ignorar o campo com o nome quase certo faria o dado **não chegar**, sem nada denunciando."}},

 {"h2": "Escalares próprios"},
 cod("""
adopt Arcane.Time as Time

Lavra.escalar(esq, "Data",
    serializa := lambda d => Time.format(d, "%Y-%m-%d"),
    desserializa := lambda t => Time.parse(t, "%Y-%m-%d"),
    descricao := "Uma data, sem hora, em ISO 8601.")
"""),
 {"p": "Um escalar próprio é onde entra o que a linguagem não tem como primitivo: `Data`, `Dinheiro`, `Email`, `CPF`. A validação vive no `desserializa` e vale para **todo** campo daquele tipo, em vez de espalhada por cada resolvedor."},

 {"h2": "Contratos"},
 {"p": "Um **contrato** são campos que vários tipos prometem ter. Quem consulta pede os campos do contrato e recebe de qualquer um dos que o cumprem."},
 cod("""
Lavra.tipo(esq, Artigo, cumpre := ["Conteudo"])
Lavra.tipo(esq, Video, cumpre := ["Conteudo"])

action que_tipo(valor, ctx):
    yield "Video" given "minutos" in valor.fields otherwise "Artigo"

Lavra.contrato(esq, "Conteudo", {"id": "Integer", "titulo": "String"},
    resolve_tipo := que_tipo)
"""),
 consulta("""
busca:
    acervo:
        titulo
        ... em Video:
            minutos
"""),
 {"p": "O `resolve_tipo` responde **qual tipo concreto é aquele valor**. Sem ele, o Lavra tenta descobrir pelo nome do record — e quando não consegue, diz isso com a lista dos candidatos, em vez de devolver um objeto pela metade."},
 {"callout": {"tipo": "dica", "titulo": "O contrato é conferido na montagem",
              "texto": "Um tipo que declara cumprir um contrato e não tem um dos campos dele **para o `Lavra.conferir`** — e não a primeira consulta que por acaso pedir aquele campo, meses depois, em produção."}},

 {"h2": "Uniões"},
 {"p": "Uma **união** é quando o campo devolve um de vários tipos que não têm nada em comum — o resultado de uma busca, por exemplo."},
 cod("""
Lavra.uniao(esq, "Achado", ["Usuario", "Produto", "Artigo"],
    resolve_tipo := classificar)
"""),
 consulta("""
busca:
    buscar(termo: "forja"):
        ... em Usuario:
            nome
        ... em Produto:
            titulo
            preco
"""),
 {"p": "A diferença para o contrato: uma união **não tem campos próprios**. Não dá para pedir `id` direto dela, porque não há promessa de que todos os membros tenham `id`."},

 {"h2": "Fechar o esquema"},
 cod("Lavra.conferir(esq)"),
 {"p": "Confere que todo tipo citado existe, que todo contrato é cumprido, que toda união aponta para tipos reais, e que há ao menos uma busca. Roda na **montagem**: um esquema que não fecha derruba a subida, e não a consulta de alguém."},
 {"h2": "O esquema em texto"},
 cod("out Lavra.texto_do_esquema(esq)"),
 {"p": "Serve para **versionar**. Um esquema em arquivo entra no diff, e uma mudança que quebra o cliente aparece na revisão em vez de na produção. É o mesmo texto que `GET /lavra` devolve."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/consulta",
"title": "A consulta",
"description": "A linguagem que o cliente escreve: busca, mudança, assinatura, apelidos, trechos, variáveis, diretivas e introspecção.",
"blocos": [
 {"p": "A consulta é um **texto** — ela atravessa a rede. A escrita é indentada, como a linguagem, e o `:` no fim marca que aquele campo tem seleção dentro."},

 {"h2": "As três operações"},
 {"table": {"head": ["Operação", "Para quê"], "rows": [
   ["`busca`", "ler — sem efeito colateral"],
   ["`mudanca`", "escrever — o efeito aparece no nome"],
   ["`assinatura`", "acompanhar — o servidor empurra cada novo valor"],
 ]}},
 {"p": "A separação não é burocracia. Quem lê a consulta sabe, **sem abrir o resolvedor**, se aquilo muda alguma coisa — e é o que permite a um intermediário guardar em cache uma `busca` e nunca uma `mudanca`."},
 consulta("""
busca:
    usuario(id: 1):
        nome

mudanca:
    criarUsuario(dados: {nome: "Ana", email: "ana@forja.co"}):
        id

assinatura:
    pedidoCriado:
        numero
        total
"""),

 {"h2": "Campos e argumentos"},
 consulta("""
busca:
    pedidos(limite: 10, ordem: Recente, ativo: yes):
        numero
        itens:
            quantidade
            produto:
                nome
"""),
 {"p": "Um campo **sem** seleção é uma folha (`numero`); um **com** seleção termina em `:`. É a mesma regra do bloco na linguagem, e o erro de esquecer os dois pontos diz isso."},
 {"p": "Os valores aceitos são os da linguagem: texto entre aspas, número, `yes`/`no`/`void`, `[lista]`, `{vault}`, `$variavel` e o nome de um membro de enum."},

 {"h2": "Apelidos"},
 consulta("""
busca:
    ana: usuario(id: 1):
        nome
    bia: usuario(id: 2):
        nome
"""),
 cod("""{ana: {nome: Ana}, bia: {nome: Bia}}""", "text"),
 {"p": "Sem apelido, os dois `usuario` colidiriam na resposta. É também como se pede o mesmo campo com argumentos diferentes na mesma consulta."},

 {"h2": "Trechos"},
 {"p": "Um **trecho** é um pedaço de seleção com nome. Ele existe para não repetir a mesma lista de campos em cinco lugares — e para que mudá-la seja uma edição só."},
 consulta("""
trecho Basico em Usuario:
    id
    nome
    email

busca:
    ana: usuario(id: 1):
        ...Basico
    bia: usuario(id: 2):
        ...Basico
        criado_em
"""),
 {"p": "O `em Usuario` diz a que tipo ele se aplica, e é o que permite **conferi-lo antes de rodar**: um trecho de `Usuario` usado num `Produto` é recusado pela validação."},
 {"callout": {"tipo": "nota", "titulo": "O mesmo campo duas vezes vira um",
              "texto": "`...Basico` mais `nome` escrito à mão pedem `nome` duas vezes. O Lavra junta os dois numa seleção só. Sem juntar, a segunda apagaria a primeira no vault — e aí a **ordem** da consulta mudaria o resultado."}},

 {"h2": "Trecho condicional"},
 {"p": "Para união e contrato: pedir o que só existe num dos tipos."},
 consulta("""
busca:
    acervo:
        titulo
        ... em Video:
            minutos
        ... em Podcast:
            episodio
"""),

 {"h2": "Variáveis"},
 {"p": "A consulta é uma só; o valor muda. É o que permite guardá-la como constante no cliente em vez de montá-la com concatenação — que é de onde vem injeção."},
 consulta("""
busca Painel($id: Integer!, $limite: Integer := 3):
    usuario(id: $id):
        nome
        pedidos(limite: $limite):
            numero
"""),
 cod("""
r := Lavra.executar(esq, consulta, variaveis := {"id": 7})
"""),
 {"table": {"head": ["Declaração", "O que acontece se não vier"], "rows": [
   ["`$id: Integer!`", "a consulta é recusada"],
   ["`$id: Integer`", "chega como `void`"],
   ["`$id: Integer := 3`", "chega como `3`"],
 ]}},
 {"callout": {"tipo": "atencao", "titulo": "A validação confere o tipo da variável",
              "texto": "Passar `$nome: String` para um argumento `Integer!` é recusado **antes** de executar, com as duas declarações na mensagem. E uma variável declarada e nunca usada também é apontada — ela costuma ser o resto de uma edição pela metade."}},

 {"h2": "Diretivas"},
 consulta("""
busca Talvez($detalhado: Boolean!):
    usuario(id: 1):
        nome
        email @incluir(se: $detalhado)
        telefone @pular(se: $detalhado)
"""),
 {"p": "`@incluir(se:)` põe o campo quando a condição é verdadeira; `@pular(se:)` tira. Servem para uma consulta só atender a duas telas — a compacta e a completa — sem duas versões dela para divergirem."},
 {"p": "Diretivas próprias entram no esquema:"},
 cod("""
action so_admin(args, ctx):
    yield ctx["papel"] is "admin"

Lavra.diretiva(esq, "admin", so_admin)
"""),
 consulta("""
busca:
    usuario(id: 1):
        nome
        cpf @admin
"""),
 {"p": "É o gancho para `@admin`, `@experimento(nome: …)` e afins — sem espalhar `given` por dentro de cada resolvedor."},

 {"h2": "Introspecção"},
 {"p": "O esquema se descreve, e é ele mesmo quem responde:"},
 consulta("""
busca:
    __tipo(nome: "Pedido")
"""),
 consulta("""
busca:
    __esquema
"""),
 {"p": "Sem introspecção, um cliente precisa de documentação ao lado para saber o que pedir — e essa documentação envelhece em silêncio. Com ela, o editor completa o campo e a página de referência é **gerada** do que está no ar."},
 {"p": "A resposta vem do **mesmo objeto** que executa. Não há um segundo lugar descrevendo o esquema para divergir do primeiro."},
 {"callout": {"tipo": "atencao", "titulo": "Desligue em produção",
              "texto": "`Lavra.introspeccao(esq, no)` tira `__esquema` e `__tipo`. Um esquema exposto é um mapa do que existe para quem for procurar, e quem precisa dele é o time — que pode lê-lo do repositório."}},

 {"h2": "Os erros de consulta dizem a linha"},
 cod("""
erro: 'Usuario' não tem o campo 'nomee'
  linha 3
  dica: você quis dizer 'nome'?
""", "text"),
 {"p": "E **todos de uma vez**: um validador que para no primeiro erro faz corrigir uma linha por tentativa. Com dez numa resposta, corrigem-se as dez."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/resolvedores",
"title": "Resolvedores",
"description": "Quem responde por cada campo: contexto, autorização, erros, middleware e a ordem das coisas.",
"blocos": [
 {"p": "Um **resolvedor** é a ação que responde por um campo. Ele recebe o objeto pai, os argumentos e o contexto — e devolve o valor."},
 cod("""
action pedidos_de(usuario, args, ctx):
    yield Banco.pedidos(usuario.id, limite := args["limite"])

Lavra.campo(esq, "Usuario", "pedidos", "[Pedido!]!",
    args := {"limite": {"tipo": "Integer", "padrao": 10}},
    resolve := pedidos_de)
"""),
 {"callout": {"tipo": "dica", "titulo": "Um resolvedor simples não precisa dos três",
              "texto": "`lambda p => p.total` funciona. O Lavra chama com quantos argumentos a ação aceitar — exigir os três faria toda linha carregar um `_, _` que não diz nada."}},

 {"h2": "A ordem em que as coisas acontecem"},
 cod("""
texto da consulta
    ↓  ler          — vira árvore; erro aqui traz linha e coluna
    ↓  validar      — TODOS os problemas de uma vez, sem resolver nada
    ↓  limites      — profundidade e custo, antes de qualquer resolvedor
    ↓  resolver     — campo a campo, do topo para as folhas
    ↓  lote         — a fila vira uma consulta só
    ↓  coagir       — o valor vira o tipo declarado
resposta: dados, erros, extensoes
""", "text"),
 {"componente": "diagrama-pipeline"},
 {"p": "A validação vem **antes** de executar de propósito. Executar e descobrir no meio que o campo não existe já custou tudo o que veio antes — inclusive escritas, numa `mudanca`."},

 {"h2": "O contexto"},
 {"p": "O contexto é o que atravessa a consulta inteira: quem pediu, a conexão do banco, o rastro. Ele é montado **por pedido** e morre com ele."},
 cod("""
action contexto_de(req):
    token := req["headers"]["authorization"] ?? ""
    yield {
        "usuario": autenticar(token),
        "banco": conexao,
        "ip": req["ip"],
    }

Lavra.montar(api, esq, "/lavra", contexto_de := contexto_de)
"""),
 cod("""
action meu_perfil(raiz, args, ctx):
    given ctx["usuario"] is void:
        Lavra.recusar("entre para ver o seu perfil")
    yield ctx["usuario"]
"""),
 {"callout": {"tipo": "atencao", "titulo": "Estado global não serve",
              "texto": "Guardar o usuário num vault do módulo funciona até o segundo pedido simultâneo — o Kiln atende **um pedido por thread**, e dois pedidos escrevendo no mesmo nome perdem um dos dois. O contexto existe para isso."}},

 {"h2": "Erros"},
 {"p": "Um erro num campo **não derruba a resposta inteira**. O campo vira `void`, o erro entra na lista com o **caminho** até ele, e o resto da consulta continua."},
 cod("""
action risco_de(cliente, args, ctx):
    resposta := Malha.de(ctx["malha"], "risco").obter($"/risco/{cliente.id}")
    given resposta["status"] isnt 200:
        Lavra.erro("o serviço de risco não respondeu", codigo := "dependencia")
    yield resposta["corpo"]["nota"]
"""),
 cod("""
{
  "dados": {"cliente": {"nome": "Ana", "risco": void}},
  "erros": [{"mensagem": "o serviço de risco não respondeu",
             "caminho": ["cliente", "risco"],
             "codigo": "dependencia"}]
}
""", "json"),
 {"p": "Quem pediu dez campos e teve um problema num recebe **nove** — não zero. É a diferença entre uma tela com um aviso e uma tela vazia."},
 {"p": "A exceção é o campo `!`: ele prometeu nunca ser `void`, então um erro ali sobe para o pai, e daí para cima, até achar alguém que admita `void`."},

 {"h2": "Autorização"},
 {"p": "Há três lugares, e eles resolvem coisas diferentes:"},
 {"table": {"head": ["Onde", "Para quê"], "rows": [
   ["o campo não está no esquema", "ninguém pode pedir, nunca"],
   ["`Lavra.recusar` no resolvedor", "**este** usuário não pode ver **este** dado"],
   ["uma diretiva `@admin`", "a regra vale para muitos campos, e aparece na consulta"],
 ]}},
 cod("""
action cpf_de(usuario, args, ctx):
    given ctx["usuario"]?.id isnt usuario.id and ctx["papel"] isnt "admin":
        Lavra.recusar("o CPF é do próprio dono")
    yield usuario.cpf
"""),
 {"callout": {"tipo": "perigo", "titulo": "Autorizar no campo, e não na busca",
              "texto": "Proteger só a busca de topo deixa a porta dos fundos aberta: `pedido.cliente.cpf` chega ao mesmo dado por outro caminho. Num grafo, todo caminho é uma porta."}},

 {"h2": "Middleware"},
 {"p": "Para o que vale para toda consulta — registro, rastro, tempo —, use o middleware do próprio [Kiln](/docs/kiln), que roda antes da rota:"},
 cod("""
action rastrear(req):
    Malha.propagar(req, "api")

server api on 8080:
    middleware rastrear
    middleware Kiln.rate_limit(60, 60)

Lavra.montar(api, esq, "/lavra")
"""),
 {"p": "Para o que vale por **campo**, o lugar é a diretiva própria — ela aparece na consulta, e é auditável lendo o texto."},

 {"h2": "Mudanças"},
 cod("""
action criar_pedido(raiz, args, ctx):
    dados := args["dados"]
    given len(dados["itens"]) is 0:
        Lavra.erro("um pedido precisa de ao menos um item", codigo := "validacao")
    yield Banco.transacao(ctx["banco"], lambda => gravar(dados))
"""),
 {"p": "Uma mudança que toca duas tabelas precisa de **transação** — e é `Arcane.Database` quem a dá. O Lavra não inventa uma: a venda gravada com o estoque não baixado é o mesmo problema em qualquer camada, e ele já está resolvido embaixo."},
 {"callout": {"tipo": "nota", "titulo": "As mudanças rodam em série",
              "texto": "Uma `mudanca` com três campos resolve os três **na ordem escrita**. Duas escritas no mesmo dado rodando juntas dariam resultado dependente de ordem — e a ordem da consulta é a única que quem escreveu controla."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/desempenho",
"title": "Desempenho",
"description": "O lote contra o N+1, paginação por cursor, cache e o custo de uma consulta.",
"blocos": [
 {"h2": "O N+1, em uma frase"},
 {"p": "Uma consulta que pede 50 pedidos e, de cada um, o cliente, faz **51** consultas ao banco: uma para os pedidos e uma por cliente. O servidor parece rápido e o banco morre."},
 consulta("""
busca:
    pedidos(limite: 50):
        numero
        cliente:
            nome
"""),

 {"h2": "O lote, em uma frase"},
 {"p": "O resolvedor não **busca** — ele **pede**. Os pedidos feitos na mesma volta são juntados num só, e cada um recebe a sua parte."},
 cod("""
action buscar_clientes(ids):
    yield Banco.varios(ctx["banco"], "clientes", ids)

action cliente_do_pedido(pedido, args, ctx):
    yield Lavra.pedir(ctx, "clientes", pedido.cliente_id)

Lavra.campo(esq, "Pedido", "cliente", "Cliente!", resolve := cliente_do_pedido)
"""),
 cod("""
ctx := Lavra.contexto({"banco": conexao})
_ := Lavra.lote(ctx, "clientes", buscar_clientes)

r := Lavra.executar(esq, consulta, contexto := ctx)
out r["extensoes"]["lotes"]
"""),
 cod("""{clientes: {chamadas: 1, chaves: 50, economia: 49}}""", "text"),
 {"componente": "diagrama-lote"},
 {"p": "Cinquenta pedidos, **uma** ida ao banco. O `economia` está ali para ser olhado: um lote que devolve o valor certo e mesmo assim consulta cinquenta vezes passaria em qualquer teste que só olhasse o resultado."},

 {"h3": "Duas decisões do lote"},
 {"list": [
   "**Ele vive no contexto, não no módulo.** Um lote de processo guardaria o cliente depois que ele mudou, e serviria o valor velho para outra pessoa. O contexto morre com a consulta, que é exatamente a vida útil que um cache de leitura pode ter aqui.",
   "**A ordem da resposta é a ordem do pedido.** A função recebe as chaves e devolve os valores na MESMA ordem — ou um vault de chave → valor, que não depende de ordem nenhuma.",
 ]},
 {"callout": {"tipo": "perigo", "titulo": "A lista fora de ordem é o bug clássico",
              "texto": "Cada pedido recebe o cliente de outro, e **nada falha**. Por isso o Lavra recusa uma resposta com tamanho diferente do pedido, e diz por quê — é o único sintoma que essa falha tem."}},

 {"h2": "Paginação por cursor"},
 {"p": "Paginar por posição (`pule 20, traga 20`) parece mais simples e quebra do jeito mais difícil de ver: se alguém insere uma linha entre a página 1 e a 2, **um item desaparece** — ele desceu para a posição que já foi lida."},
 cod("""
action pedidos_de(usuario, args, ctx):
    todos := Banco.pedidos(usuario.id)
    yield Lavra.pagina(todos, primeiros := args["primeiros"],
                       depois := args["depois"])

Lavra.tipo_pagina(esq, "Pedido")
Lavra.campo(esq, "Usuario", "pedidos", "PaginaPedido!",
    args := {"primeiros": {"tipo": "Integer", "padrao": 20},
             "depois": "String"},
    resolve := pedidos_de)
"""),
 consulta("""
busca:
    usuario(id: 1):
        pedidos(primeiros: 20, depois: "eyJ..."):
            itens:
                numero
            info:
                tem_proxima
                cursor_fim
            total
"""),
 {"p": "Com cursor, a página seguinte começa exatamente onde a anterior parou — independentemente do que aconteceu no meio."},

 {"h2": "Cache"},
 {"p": "Há três camadas, e elas não se substituem:"},
 {"table": {"head": ["Camada", "Vive", "Para quê"], "rows": [
   ["o lote", "uma consulta", "o mesmo dado pedido várias vezes na mesma resposta"],
   ["`V.cache` / memoize", "o processo", "o cálculo caro que muda devagar"],
   ["cabeçalho HTTP", "o cliente", "a resposta inteira, quando ela pode envelhecer"],
 ]}},
 {"callout": {"tipo": "atencao", "titulo": "Uma mudança nunca entra em cache",
              "texto": "É por isso que a operação diz o que é no nome. Um intermediário pode guardar uma `busca` sem abrir o corpo; uma `mudanca`, nunca."}},

 {"h2": "O custo de uma consulta"},
 {"p": "Nem toda consulta custa o mesmo, e o tamanho do texto não diz nada: três linhas pedindo uma lista de mil itens custam mais que trinta linhas de campos escalares."},
 cod("""
Lavra.campo(esq, "Usuario", "relatorio", "Relatorio!",
    resolve := gerar_relatorio, custo := 50)

Lavra.limites(esq, complexidade := 1000)
"""),
 {"p": "Um campo que devolve lista multiplica o custo do que vem dentro pelo argumento de limite — e, sem limite declarado, por dez. É o que faz `pedidos { itens { produto { … } } }` custar caro sem que ninguém precise contar à mão."},
 cod("""out r["extensoes"]""", "df"),
 cod("""{ms: 12.4, campos: 143, profundidade: 4, complexidade: 260,
 lotes: {clientes: {chamadas: 1, chaves: 50, economia: 49}}}""", "text"),
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/seguranca",
"title": "Segurança",
"description": "Validação antes de executar, limites de profundidade e custo, rate limit, introspecção e observabilidade.",
"blocos": [
 {"p": "Um servidor de consulta tem uma superfície de ataque que uma API REST não tem: **quem consulta escolhe a forma da consulta**. Isso é o valor do modelo, e é também o risco."},

 {"h2": "Validar antes de executar"},
 cod("""
problemas := Lavra.validar(esq, texto)
given len(problemas) bigger 0:
    respond 200 json {"dados": void, "erros": problemas}
"""),
 {"p": "A validação percorre a árvore **sem chamar resolvedor nenhum**: nada é lido, nada é escrito. `Lavra.executar` já faz isso por padrão — `validar_antes := no` só existe para quem já validou e guardou a consulta."},

 {"h2": "Os três limites"},
 cod("""
Lavra.limites(esq,
    profundidade := 8,      // quantos níveis a consulta pode descer
    complexidade := 1000,   // o custo somado
    itens := 500)           // o teto de uma lista devolvida
"""),
 {"table": {"head": ["Limite", "O que ele impede"], "rows": [
   ["`profundidade`", "`usuario.pedidos.cliente.pedidos…` num grafo com ciclo"],
   ["`complexidade`", "uma consulta curta que pede um milhão de itens"],
   ["`itens`", "um resolvedor que devolve a tabela inteira num dia de pico"],
 ]}},
 {"callout": {"tipo": "perigo", "titulo": "Nenhum deles é opcional num servidor público",
              "texto": "A consulta funda num grafo com ciclo é a forma mais barata de derrubar um servidor de consulta. Ela cabe num tuíte, não exige autenticação em muitos esquemas, e o servidor gasta tudo o que tem antes de responder."}},
 {"p": "Os três são conferidos **antes** de resolver qualquer coisa. Descobrir isso resolvendo já é tarde."},

 {"h2": "Rate limit"},
 {"p": "O limite por consulta não substitui o limite por cliente. Os dois são do [Kiln](/docs/kiln):"},
 cod("""
server api on 8080:
    middleware Kiln.rate_limit(60, 60)      // 60 pedidos por minuto, por IP

Lavra.montar(api, esq, "/lavra")
"""),
 {"p": "Sessenta consultas de custo 900 cada passam pelos dois limites e ainda derrubam o banco. Para isso, o limite tem de ser **de custo por janela**, e não de pedidos — o `extensoes.complexidade` de cada resposta é o número que se soma."},

 {"h2": "Introspecção em produção"},
 cod("""
Lavra.introspeccao(esq, no)
"""),
 {"p": "Um esquema exposto é um mapa do que existe para quem for procurar: nomes de campos internos, o tipo que só aparece no fluxo de pagamento, o argumento que ninguém deveria descobrir. Quem precisa do esquema é o time, e ele pode lê-lo do repositório."},
 {"callout": {"tipo": "nota", "titulo": "Desligar não é proteger",
              "texto": "Um campo que existe continua acessível para quem adivinhar o nome. A introspecção desligada só tira o índice; o que protege é o campo **não estar no esquema** ou o resolvedor recusar."}},

 {"h2": "Consultas guardadas"},
 {"p": "Num cliente próprio — um app, um site que você escreve —, a consulta não precisa vir da rede. Guarde as consultas no servidor e aceite só o **nome**:"},
 cod("""
consultas := {
    "painel": IO.read("consultas/painel.lavra"),
    "perfil": IO.read("consultas/perfil.lavra"),
}

route POST "/lavra":
    nome := body["nome"] ?? ""
    given nome not in consultas:
        respond 400 json {"erro": "consulta desconhecida"}
    respond json Lavra.executar(esq, consultas[nome],
        variaveis := body["variaveis"] ?? {})
"""),
 {"p": "Isso resolve os três problemas de uma vez: a superfície volta a ser fechada como a de uma API REST, o custo de cada consulta é conhecido, e o corpo do pedido fica pequeno."},

 {"h2": "O que nunca vai para a resposta"},
 {"list": [
   "**A mensagem de erro do banco.** `Lavra.erro` diz o que quem consulta precisa saber; o resto vai para o registro, com o rastro.",
   "**O campo que não está no esquema.** É a garantia mais barata que existe.",
   "**O caminho do arquivo.** Nenhuma mensagem do Lavra cita arquivo nem linha do servidor.",
 ]},

 {"h2": "Observabilidade"},
 {"p": "Toda resposta traz `extensoes` — tempo, campos resolvidos, profundidade, custo e o resumo dos lotes. É o que se registra:"},
 cod("""
action registrar(r, ctx):
    Log.info("consulta", {
        "ms": r["extensoes"]["ms"],
        "custo": r["extensoes"]["complexidade"],
        "campos": r["extensoes"]["campos"],
        "erros": len(r["erros"]),
        "rastro": Malha.rastro(),
    })
"""),
 {"p": "O **custo** é a métrica que importa, e não o tempo: uma consulta cara que ficou rápida porque o cache estava quente volta a ser cara quando ele esfria."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/servidor",
"title": "O servidor",
"description": "Servir o esquema por HTTP, assinaturas por WebSocket, e o cliente que consulta outro serviço.",
"blocos": [
 {"p": "O servidor do Lavra é o **Kiln**. HTTP, rotas, CORS, sessão, cabeçalhos de segurança e WebSocket já existem lá, testados — reimplementá-los aqui criaria duas implementações do mesmo protocolo para divergirem."},

 {"h2": "Montar num app que já existe"},
 cod("""
adopt Kiln
adopt Arcane.Lavra as Lavra

server api on 8080:
    route GET "/saude":
        respond json {"ok": yes}

Lavra.montar(api, esq, "/lavra")
ignite api
"""),
 {"table": {"head": ["Rota", "O que faz"], "rows": [
   ["`POST /lavra`", "executa a consulta"],
   ["`GET /lavra`", "devolve o esquema em texto"],
   ["`WS /lavra/assinar`", "as assinaturas"],
 ]}},
 {"p": "**Uma rota, um método.** Não há uma rota por busca: a consulta já diz o que quer, e uma rota por campo desfaria a razão de o Lavra existir."},

 {"h2": "O corpo do pedido"},
 cod("""
{
  "consulta": "busca:\n    usuario(id: $id):\n        nome",
  "variaveis": {"id": 7},
  "operacao": "Painel"
}
""", "json"),
 {"p": "`operacao` só é preciso quando o documento tem mais de uma. Com uma só, ela é a escolhida."},

 {"h2": "Erro de consulta responde 200"},
 {"p": "Parece errado e não é: o **HTTP falou**, e a resposta tem `dados` e `erros`. Um 400 obrigaria o cliente a ter dois caminhos de leitura para o mesmo corpo, e esconderia o caso normal — dados parciais com um erro num campo."},
 {"table": {"head": ["Status", "Quando"], "rows": [
   ["`200`", "a consulta foi lida — com ou sem erro nos campos"],
   ["`400`", "o corpo nem chegou a ser consulta (ilegível, sem `consulta`)"],
   ["`500`", "quebrou fora da consulta"],
 ]}},

 {"h2": "O contexto vem do pedido"},
 cod("""
action contexto_de(req):
    yield {
        "usuario": autenticar(req["headers"]["authorization"] ?? ""),
        "banco": conexao,
        "ip": req["ip"],
    }

Lavra.montar(api, esq, "/lavra", contexto_de := contexto_de)
"""),
 {"callout": {"tipo": "nota", "titulo": "Os cabeçalhos chegam em minúsculas",
              "texto": "`req[\"headers\"][\"authorization\"]`, e não `\"Authorization\"`. O Kiln normaliza, porque o HTTP não distingue maiúscula em nome de cabeçalho — e quem escreve a leitura com a maiúscula recebe `void` sem nada explicando."}},

 {"h2": "Um servidor só para o esquema"},
 cod("""
Lavra.servir(esq, porta := 8080, contexto_de := contexto_de)
"""),
 {"p": "Sobe e bloqueia. Para teste, `Lavra.em_segundo_plano` devolve `(app, porta)` e não bloqueia:"},
 cod("""
par := Lavra.em_segundo_plano(esq)
app := par[0]
porta := par[1]
defer:
    Lavra.parar(app)
"""),

 {"h2": "Assinaturas"},
 {"p": "Uma assinatura é o servidor **empurrando** cada novo valor. O transporte é WebSocket, e o formato de cada mensagem é o mesmo de uma resposta comum."},
 cod("""
novos := Lavra.fonte("pedidos")

action pedido_criado(raiz, args, ctx):
    yield novos

Lavra.assinatura(esq, "pedidoCriado", "Pedido!", resolve := pedido_criado)
Lavra.montar_assinaturas(api, esq, "/lavra/assinar")
"""),
 {"p": "Quando um pedido nasce, quem publica é o código que o criou:"},
 cod("""
action criar_pedido(raiz, args, ctx):
    novo := Banco.inserir(ctx["banco"], "pedidos", args["dados"])
    _ := novos.publicar(novo)
    yield novo
"""),
 consulta("""
assinatura:
    pedidoCriado:
        numero
        total
        cliente:
            nome
"""),
 {"p": "Repare que a assinatura **também é uma consulta**: cada evento passa pelo mesmo esquema, com os mesmos resolvedores e o mesmo lote. Quem acompanha escolhe os campos, como em qualquer outra operação."},
 {"h3": "Por que uma Fonte, e não um generator"},
 {"p": "Um generator serve **um** consumidor, e uma assinatura tem muitos. Publicar num generator obrigaria a manter um por conexão, o que multiplica o trabalho pelo número de pessoas com a aba aberta. A `Fonte` é uma fila com assinantes: publica-se uma vez, e ela entrega a todos."},
 {"callout": {"tipo": "atencao", "titulo": "Um assinante morto não derruba os outros",
              "texto": "Quem fechou a aba é removido da lista no momento em que a entrega falha — a mesma regra da `Sala` do Kiln. Sem isso, uma conexão zumbi levaria a mensagem de todo mundo junto."}},
 {"callout": {"tipo": "dica", "titulo": "Quando SSE é melhor",
              "texto": "Se o cliente só **ouve**, prefira `Kiln.sse`: é HTTP comum, reconecta sozinho e passa em qualquer proxy. O WebSocket ganha quando os dois lados falam."}},

 {"h2": "Consultar outro serviço"},
 cod("""
c := Lavra.cliente("http://contas.interno/lavra",
    cabecalhos := {"Authorization": $"Bearer {token}"})

r := c.consultar(\"\"\"
busca Um($id: Integer!):
    usuario(id: $id):
        nome
\"\"\", {"id": 7})

out r["dados"]["usuario"]["nome"]
"""),
 {"p": "O cliente é fino de propósito: monta o corpo, chama a [Malha](/docs/tecnicas/microservicos) e lê a resposta. Retentativa com recuo, disjuntor, propagação de rastro e idempotência já estão resolvidos lá."},
 {"callout": {"tipo": "atencao", "titulo": "status 0 é o caso honesto",
              "texto": "Uma chamada de rede tem três desfechos, e o terceiro é **não se sabe**. O cliente devolve um erro de código `rede` nesse caso, em vez de dizer que falhou — colapsar os dois faria quem chama repetir uma cobrança."}},

 {"h2": "Testar sem socket"},
 cod('''
c := Lavra.local(esq)

dados := c.dados("""
busca:
    usuario(id: 1):
        nome
""")

assert dados["usuario"]["nome"] is "Ana"
'''),
 {"p": "`Lavra.local` tem o **mesmo contrato** do cliente remoto, sem rede. É o que torna barato o teste de quem consome — e o que permite trocar um pelo outro sem mudar o código que usa."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/federacao",
"title": "Federação",
"description": "Vários serviços, um esquema só para quem consulta: o portão, a composição e o campo que atravessa a fronteira.",
"blocos": [
 {"p": "Cada time tem o seu serviço, e cada serviço tem o seu esquema. Quem consulta não quer saber disso: quer `usuario.pedidos.itens` numa consulta, sem descobrir que usuário mora num lugar e pedido em outro."},

 {"h2": "O portão"},
 cod("""
portao := Lavra.portao()

Lavra.juntar(portao, "contas", esquema_de_contas)
Lavra.juntar(portao, "vendas", esquema_de_vendas)
Lavra.juntar(portao, "catalogo", esquema_de_catalogo)

portao.conferir()
Lavra.montar(api, portao.esquema, "/lavra")
"""),
 {"p": "Os tipos de cada serviço entram num esquema só. As buscas de cada um viram buscas do portão. Quem consulta vê **um** esquema."},

 {"h2": "O campo que atravessa"},
 {"p": "`Usuario` é de contas; `Pedido` é de vendas. O campo `usuario.pedidos` não pertence a nenhum dos dois sozinho — ele é a fronteira, e é declarado como **extensão**:"},
 cod("""
action pedidos_do_usuario(usuario, args, ctx):
    yield Lavra.pedir(ctx, "pedidos_por_usuario", usuario["id"])

Lavra.estender(portao, "Usuario", "pedidos", "[Pedido!]!",
    resolve := pedidos_do_usuario)
"""),
 {"p": "Repare no `Lavra.pedir`: a fronteira é exatamente onde o [N+1](/docs/lavra/desempenho) dói mais, porque cada travessia é uma chamada de **rede**. Cinquenta usuários viram uma chamada ao serviço de vendas, e não cinquenta."},
 cod("""
action buscar_pedidos(ids_de_usuario):
    r := cliente_de_vendas.consultar(\"\"\"
busca Por($ids: [Integer!]!):
    pedidosPorUsuario(ids: $ids):
        usuario_id
        numero
        total
\"\"\", {"ids": ids_de_usuario})
    yield agrupar_por(r["dados"]["pedidosPorUsuario"], "usuario_id", ids_de_usuario)
"""),

 {"h2": "Conflito de nome é erro"},
 {"p": "Dois serviços que declaram `Usuario` **param a composição**:"},
 cod("""
erro: 'Usuario' é declarado por 'contas' e por 'perfis'.
  Dois tipos com o mesmo nome fariam a consulta devolver os campos de
  um ou de outro conforme a ordem do 'juntar'.
  Renomeie um dos dois, ou declare o tipo num serviço só e estenda-o
  do outro com Lavra.estender.
""", "text"),
 {"p": "Fundir os dois em silêncio faria a resposta depender da **ordem do `juntar`** — que é o pior jeito de falhar: funciona na máquina de quem escreveu e muda quando alguém reordena duas linhas."},

 {"h2": "De onde vem cada campo"},
 cod("""
out Lavra.mapa(portao)
"""),
 cod("""
{servicos: [catalogo, contas, vendas],
 tipos: {Usuario: contas, Pedido: vendas, Produto: catalogo},
 extensoes: [{tipo: Usuario, campo: pedidos}]}
""", "text"),
 {"p": "É a resposta para \"quem declara isto?\" — a pergunta que mais se faz num esquema federado, e a que mais custa responder lendo código de três repositórios."},

 {"h2": "O que este portão NÃO faz"},
 {"p": "Ele não é o Apollo Federation. Não há `@key`, `@external`, `_entities` nem **plano de consulta distribuído**: o portão resolve a extensão chamando o serviço dono, uma vez por fronteira, com o lote fazendo o agrupamento."},
 {"p": "Um planejador de consulta distribuído é um projeto próprio — ele decide quais subconsultas mandar, em que ordem, e como juntar os pedaços. Um subconjunto pela metade seria pior que a honestidade de não ter."},
 {"callout": {"tipo": "dica", "titulo": "Quando isto basta",
              "texto": "Na esmagadora maioria dos casos, sim. O plano distribuído ganha quando a fronteira é atravessada em várias direções na mesma consulta; com uma ou duas travessias — que é o normal —, uma chamada em lote por fronteira é o mesmo número de idas à rede."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/lavra/pratica",
"title": "Na prática",
"description": "CRUD, banco de dados, DDD, testes, documentação, Docker, CI e como organizar um projeto Lavra.",
"blocos": [
 {"h2": "A organização de um projeto"},
 cod("""
minha-api/
    forge.toml
    src/
        main.df              sobe o servidor
        esquema.df           monta o esquema e devolve
        tipos/
            usuario.df       record + tipo + campos + resolvedores
            pedido.df
        dominio/
            preco.df         a REGRA, sem saber que existe Lavra
            estoque.df
        infra/
            banco.df         as consultas SQL
    consultas/
        painel.lavra         as consultas guardadas
    tests/
        esquema_test.df
        usuario_test.df
""", "text"),
 {"p": "A regra que faz a diferença: **`dominio/` não importa `Arcane.Lavra`**. O cálculo de preço não muda porque a API mudou de forma, e um teste de domínio não precisa montar esquema nenhum."},
 cod("""
// dominio/preco.df — sem uma linha de Lavra
action preco_final(produto, cupom):
    base := produto.preco
    given cupom isnt void and cupom.valido:
        base := base * (1.0 - cupom.desconto)
    yield round(base, 2)

relay preco_final
"""),
 cod("""
// tipos/produto.df — a casca fina que liga os dois
adopt ../dominio/preco as Preco

action preco_de(produto, args, ctx):
    yield Preco.preco_final(produto, buscar_cupom(args["cupom"]))

Lavra.campo(esq, "Produto", "preco_final", "Float!",
    args := {"cupom": "String"}, resolve := preco_de)
"""),

 {"h2": "CRUD completo"},
 cod("""
// ── ler ──
Lavra.busca(esq, "produto", "Produto", args := {"id": "Integer!"},
    resolve := lambda r, a, ctx => Banco.achar(ctx["banco"], "produtos", a["id"]))

Lavra.busca(esq, "produtos", "PaginaProduto!",
    args := {"primeiros": {"tipo": "Integer", "padrao": 20},
             "depois": "String",
             "busca": "String"},
    resolve := listar_produtos)

// ── criar ──
Lavra.mudanca(esq, "criarProduto", "Produto!",
    args := {"dados": "NovoProduto!"}, resolve := criar_produto)

// ── alterar ──
Lavra.mudanca(esq, "alterarProduto", "Produto!",
    args := {"id": "Integer!", "dados": "AlteraProduto!"},
    resolve := alterar_produto)

// ── apagar ──
Lavra.mudanca(esq, "apagarProduto", "Boolean!",
    args := {"id": "Integer!"}, resolve := apagar_produto)
"""),
 {"callout": {"tipo": "nota", "titulo": "Três entradas, não uma",
              "texto": "`NovoProduto` exige nome e preço; `AlteraProduto` tem tudo opcional, porque alterar um campo não é reenviar o objeto. Usar a mesma entrada nos dois obrigaria a tornar tudo opcional — e aí a criação deixaria de ser conferida."}},

 {"h2": "Com banco de dados"},
 cod("""
adopt Arcane.Database as Banco

action listar_produtos(raiz, args, ctx):
    consulta := Banco.select(ctx["banco"], "produtos")
    given args["busca"] isnt void:
        consulta := Banco.search(consulta, args["busca"])
    yield Lavra.pagina(Banco.todos(consulta),
                       primeiros := args["primeiros"],
                       depois := args["depois"])

action criar_produto(raiz, args, ctx):
    yield Banco.transacao(ctx["banco"], lambda => gravar(ctx, args["dados"]))
"""),
 {"p": "A transação é do `Arcane.Database`, e não do Lavra: a venda gravada com o estoque não baixado é o mesmo problema em qualquer camada, e ele já está resolvido embaixo."},
 {"callout": {"tipo": "perigo", "titulo": "Ordenação que vem de fora vai crua para o SQL",
              "texto": "`ordem: \"nome\"` numa consulta chega ao `ORDER BY`. O `Arcane.Database` recusa o que não parece nome de coluna — mas o esquema resolve melhor: declare `ordem` como um **enum**, e o que não for um dos valores nem chega ao resolvedor."}},

 {"h2": "Testes"},
 cod("""
adopt Arcane.Crucible as Crucible
adopt ../src/esquema as E

crucible "o esquema":
    trial "fecha":
        Lavra.conferir(E.montar())

    trial "toda busca tem resolvedor":
        esq := E.montar()
        descricao := Lavra.descrever(esq)
        cycle campo in descricao["busca"]["campos"]:
            assert campo["tipo"] isnt "", $"{campo['nome']} sem tipo"

crucible "usuario":
    trial "traz só o que foi pedido":
        c := Lavra.local(E.montar())
        dados := c.dados("busca:\n    usuario(id: 1):\n        nome")
        assert dados["usuario"] is {"nome": "Ana"}

    trial "o campo que não existe é recusado":
        problemas := Lavra.validar(E.montar(), "busca:\n    usuario(id: 1):\n        nomee")
        assert len(problemas) is 1
        assert "nome" in problemas[0]["dica"]
"""),
 {"p": "Três coisas valem um teste próprio, e são as que mais quebram:"},
 {"list": [
   "**O esquema fecha.** Um `conferir` no teste é o que impede uma subida quebrada.",
   "**O N+1 não voltou.** Conte as idas ao banco, e não o resultado: um lote que devolve o valor certo e consulta cinquenta vezes passa em qualquer teste que só olhe os dados.",
   "**A consulta guardada ainda vale.** Valide cada arquivo de `consultas/` contra o esquema atual; é assim que uma mudança que quebra o cliente aparece na CI.",
 ]},
 cod("""
crucible "as consultas guardadas ainda valem":
    cycle arquivo in IO.list_dir("consultas"):
        trial arquivo:
            problemas := Lavra.validar(E.montar(), IO.read($"consultas/{arquivo}"))
            assert len(problemas) is 0, $"{arquivo}: {problemas}"
"""),

 {"h2": "Documentação"},
 {"p": "A do esquema sai do esquema — `descricao` em cada campo, e `Lavra.descrever` ou `Lavra.texto_do_esquema` para lê-la. Uma página escrita à mão ao lado envelheceria em silêncio, que é o defeito que este projeto persegue em todo lugar."},
 cod("""
Lavra.campo(esq, "Produto", "preco_final", "Float!",
    args := {"cupom": "String"},
    resolve := preco_de,
    descricao := "O preço com o cupom aplicado. Sem cupom, é o preço de tabela.")

Lavra.campo(esq, "Produto", "preco_antigo", "Float",
    obsoleto := "use 'preco_final'; este some na 2.0")
"""),
 {"p": "Um campo `obsoleto` continua funcionando e **aparece na validação** como aviso. É como se tira um campo sem quebrar quem ainda o usa: primeiro ele avisa, depois some."},

 {"h2": "Convivendo com REST"},
 {"p": "Os dois no mesmo app, sem escolher:"},
 cod("""
server api on 8080:
    route GET "/saude":
        respond json {"ok": yes}

    route POST "/webhooks/pagamento":
        respond 200 json processar(body)

Lavra.montar(api, esq, "/lavra")
"""),
 {"p": "Webhook, upload e download continuam REST — e devem. Um webhook é chamado por quem não conhece o seu esquema; um download é um arquivo, não um grafo."},

 {"h2": "Docker e CI"},
 cod("""
dataforge devops dockerfile
dataforge devops compose
dataforge devops ci
""", "bash"),
 {"p": "O que muda para uma API Lavra:"},
 {"list": [
   "**`--host=0.0.0.0`** no `ignite`. O padrão é `127.0.0.1`, que de dentro do container significa o próprio container — e o sintoma engana: o log diz \"no ar\" e o `curl` de fora não recebe nada.",
   "**O esquema em texto entra no repositório.** `Lavra.texto_do_esquema` num arquivo versionado faz cada mudança aparecer no diff.",
   "**A CI valida as consultas guardadas** contra o esquema do commit. É o que transforma \"quebrou o app\" em \"a revisão não passou\".",
 ]},
 cod("""
# .github/workflows/ci.yml
- name: o esquema nao mudou sem aviso
  run: |
    dataforge run scripts/exportar_esquema.df > /tmp/atual.lavra
    diff -u esquema.lavra /tmp/atual.lavra
""", "yaml"),

 {"h2": "Boas práticas"},
 {"table": {"head": ["Faça", "Porque"], "rows": [
   ["Declare os três limites", "a consulta funda é a forma mais barata de derrubar o servidor"],
   ["Use `!` onde a promessa é real", "um `!` que às vezes é void é pior que não ter `!`"],
   ["Autorize no **campo**, não na busca", "num grafo, todo caminho é uma porta"],
   ["Um lote por relacionamento", "o N+1 não aparece em teste que só olha o resultado"],
   ["Pagine por cursor", "paginar por posição faz itens sumirem"],
   ["Entrada separada da saída", "o mesmo tipo nos dois lados deixa de conferir os dois"],
   ["Desligue a introspecção em produção", "o esquema é um mapa para quem for procurar"],
   ["Versione o esquema em texto", "a quebra aparece na revisão, e não no app"],
 ]}},
 {"cards": [
   {"href": "/docs/exercicios/33-lavra", "title": "Os exercícios", "desc": "Três programas que rodam e provam o que esta página afirma."},
   {"href": "/docs/lavra/desempenho", "title": "Desempenho", "desc": "O N+1, medido."},
   {"href": "/docs/lavra/seguranca", "title": "Segurança", "desc": "O que um servidor de consulta tem de diferente."},
 ]},
]},
]
