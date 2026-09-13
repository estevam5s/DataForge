// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "33 · Lavra",
  description: "3 exercícios: esquema, consulta, lote contra o N+1, servidor e federação.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 33`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[232](#232-lavra-o-esquema-e-a-consulta)", "**Lavra: o esquema e a consulta**", "declare um esquema a partir de records e peca exatamente os campos que quer."], ["[233](#233-lavra-o-n1-os-limites-e-a-paginacao)", "**Lavra: o N+1, os limites e a paginacao**", "conte as idas ao banco e prove que o lote as junta numa so."], ["[234](#234-lavra-contratos-mudancas-servidor-e-federacao)", "**Lavra: contratos, mudancas, servidor e federacao**", "sirva o esquema por HTTP e componha dois servicos num so."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "232 · Lavra: o esquema e a consulta"},
  {"p": "**Enunciado.** declare um esquema a partir de records e peca exatamente os campos que quer."},
  { code: `adopt Arcane.Lavra as Lavra

// ── 1. Os records que o programa JA tem ──
//
// O esquema nasce deles. Nao ha um arquivo de esquema ao lado para
// divergir do codigo: o record ja diz nome, campo e tipo.
record Usuario:
    id: Integer
    nome: String
    email: String

record Pedido:
    id: Integer
    numero: String
    total: Float
    usuario_id: Integer

usuarios := [Usuario(1, "Ana", "ana@forja.co"), Usuario(2, "Bia", "bia@forja.co")]
pedidos := [Pedido(10, "P-1", 99.9, 1), Pedido(11, "P-2", 15.0, 1),
    Pedido(12, "P-3", 42.0, 2)]

// ── 2. O esquema ──
esq := Lavra.esquema("loja")

Lavra.tipo(esq, Usuario)
Lavra.tipo(esq, Pedido)

// '!' promete que o campo nunca e void. '[Pedido!]!' e uma lista que
// nunca e void, de itens que nunca sao void.
Lavra.campo(esq, "Usuario", "id", "Integer!")
Lavra.campo(esq, "Usuario", "nome", "String!")
Lavra.campo(esq, "Pedido", "total", "Float!")

action pedidos_de(u):
    yield [p cycle p in pedidos given p.usuario_id is u.id]

// Um campo CALCULADO: ele nao existe no record, e quem responde por
// ele e o resolvedor.
Lavra.campo(esq, "Usuario", "pedidos", "[Pedido!]!", resolve := pedidos_de)

action achar_usuario(_raiz, args):
    achados := [u cycle u in usuarios given u.id is args["id"]]
    yield achados[0] given len(achados) bigger 0 otherwise void

Lavra.busca(esq, "usuario", "Usuario", args := {"id": "Integer!"},
    resolve := achar_usuario)
Lavra.busca(esq, "usuarios", "[Usuario!]!", resolve := lambda r, a, c => usuarios)

// 'conferir' fecha o esquema: todo tipo citado existe. Ele falha AQUI,
// e nao na primeira consulta que por acaso pedir aquele campo.
Lavra.conferir(esq)

// ── 3. A consulta ──
//
// Indentada, como a linguagem. O ':' no fim marca "isto tem selecao
// dentro", igual a 'given', 'cycle' e 'action'.
r := Lavra.executar(esq, """
busca:
    usuario(id: 1):
        nome
        pedidos:
            numero
            total
""")

out r["dados"]
assert len(r["erros"]) is 0, "sem erros"
assert r["dados"]["usuario"]["nome"] is "Ana", "o nome veio"
assert len(r["dados"]["usuario"]["pedidos"]) is 2, "os dois pedidos da Ana"

// O que NAO foi pedido nao vem. E a razao de o Lavra existir: uma rota
// REST devolve o que o servidor decidiu devolver.
assert "email" not in r["dados"]["usuario"], "nao pedi email"
assert "id" not in r["dados"]["usuario"]["pedidos"][0], "nao pedi id"

// ── 4. Apelido: o mesmo campo, duas vezes ──
dois := Lavra.executar(esq, """
busca:
    ana: usuario(id: 1):
        nome
    bia: usuario(id: 2):
        nome
""")
out dois["dados"]
assert dois["dados"]["ana"]["nome"] is "Ana"
assert dois["dados"]["bia"]["nome"] is "Bia"

// ── 5. Variaveis: a consulta e uma so, o valor muda ──
com_variavel := Lavra.executar(esq, """
busca Um($id: Integer!):
    usuario(id: $id):
        nome
    """, variaveis := {"id": 2})
assert com_variavel["dados"]["usuario"]["nome"] is "Bia"

// ── 6. O erro diz QUAL campo ──
errado := Lavra.executar(esq, """
busca:
    usuario(id: 1):
        nomee
""")
out errado["erros"][0]["mensagem"], "|", errado["erros"][0]["extra"]["dica"]
assert "nomee" in errado["erros"][0]["mensagem"]
assert "nome" in errado["erros"][0]["extra"]["dica"], "sugere o parecido"

out "229 ok"`, lang: 'df', title: `exercicios/33-lavra/232_lavra_basico.df` },
  {"h3": "O problema que o Lavra resolve"},
  {"p": "Uma rota REST devolve o que o **servidor** decidiu devolver:"},
  { code: `GET /usuarios/1
{"id": 1, "nome": "Ana", "email": "…", "criado_em": "…", "endereco": {…},
 "preferencias": {…}, "ultimo_acesso": "…"}`, lang: 'json' },
  {"p": "Quem só queria o nome carregou tudo. Quem queria o nome **e os pedidos** faz uma segunda chamada. Numa tela de celular com rede ruim, as duas coisas custam — e as duas aparecem como \"o app está lento\"."},
  {"p": "Com o Lavra, quem pergunta diz o que precisa:"},
  { code: `busca:
    usuario(id: 1):
        nome
        pedidos:
            numero`, lang: 'lavra' },
  {"h3": "O esquema nasce dos seus records"},
  {"p": "Esta é a decisão que define o módulo:"},
  { code: `record Usuario:
    id: Integer
    nome: String
    email: String

Lavra.tipo(esq, Usuario)`, lang: 'df' },
  {"p": "O `record` já diz nome, campo e tipo. Um arquivo de esquema ao lado seria uma **segunda fonte de verdade** para divergir da primeira — e esse é exatamente o defeito que este projeto persegue em todo lugar."},
  {"p": "O que o record não diz — o que é obrigatório, o que é lista de quê, qual campo é calculado e por quem — entra com `Lavra.campo`."},
  {"h3": "A notação de tipo"},
  {"table": {"head": ["Escrita", "Significa"], "rows": [["`String`", "pode ser `void`"], ["`String!`", "**nunca** é `void`"], ["`[Pedido]`", "lista que pode ser void, de itens que podem ser void"], ["`[Pedido!]!`", "lista que nunca é void, de itens que nunca são void"]]}},
  {"p": "O `!` não é decoração. Um campo que admite `void` vira `void` quando o resolvedor falha, e o resto da resposta segue. Um `!` **sobe** o erro para o pai, até achar alguém que admita `void`."},
  {"p": "É a única forma de a promessa valer alguma coisa: se um `String!` pudesse voltar vazio, quem consome teria de conferir cada campo mesmo assim."},
  {"h3": "Campo calculado"},
  {"p": "`pedidos` não existe no record `Usuario` — ele é uma relação, e quem responde por ele é o resolvedor:"},
  { code: `action pedidos_de(u):
    yield [p cycle p in pedidos given p.usuario_id is u.id]

Lavra.campo(esq, "Usuario", "pedidos", "[Pedido!]!", resolve := pedidos_de)`, lang: 'df' },
  {"p": "Repare que `pedidos_de` recebe **um** argumento. A assinatura completa é `(pai, args, ctx)`, e o Lavra chama com quantos a ação aceitar — exigir os três faria toda linha carregar um `_, _` que não diz nada."},
  {"h3": "`conferir` fecha o esquema"},
  { code: `Lavra.conferir(esq)`, lang: 'df' },
  {"p": "Confere que todo tipo citado existe, que todo contrato é cumprido e que há ao menos uma busca. Ele falha **aqui** — na montagem —, e não na primeira consulta que por acaso pedir aquele campo, que pode ser meses depois, em produção."},
  {"h3": "Apelidos"},
  { code: `busca:
    ana: usuario(id: 1):
        nome
    bia: usuario(id: 2):
        nome`, lang: 'lavra' },
  {"p": "Sem apelido, os dois `usuario` colidiriam na resposta. É também como se pede o mesmo campo com argumentos diferentes na mesma consulta."},
  {"h3": "Variáveis"},
  { code: `busca Um($id: Integer!):
    usuario(id: $id):
        nome`, lang: 'lavra' },
  {"p": "A consulta é uma só; o valor muda. É o que permite guardá-la como constante no cliente, em vez de montá-la com concatenação — que é de onde vem injeção."},
  {"h3": "Saída esperada"},
  { code: `{usuario: {nome: Ana, pedidos: [{numero: P-1, total: 99.9}, {numero: P-2, total: 15.0}]}}
{ana: {nome: Ana}, bia: {nome: Bia}}
'Usuario' não tem o campo 'nomee' | você quis dizer 'nome'?
229 ok`, lang: 'text' },
  {"h3": "Para experimentar"},
  {"list": ["Peça `email` e veja-o aparecer; tire-o e veja-o sumir. É a diferença inteira.", "Troque `Integer!` por `Integer` no argumento `id` e chame sem passá-lo.", "Declare `Lavra.tipo(esq, Usuario, esconder := [\"email\"])` e tente pedir"]},
  {"p": "`email`. O campo deixa de existir para quem consulta — é a garantia mais barata que existe."},
  {"h2": "233 · Lavra: o N+1, os limites e a paginacao"},
  {"p": "**Enunciado.** conte as idas ao banco e prove que o lote as junta numa so."},
  { code: `adopt Arcane.Lavra as Lavra

record Cliente:
    id: Integer
    nome: String

record Pedido:
    id: Integer
    cliente_id: Integer

clientes := {1: Cliente(1, "Ana"), 2: Cliente(2, "Bia")}
pedidos := [Pedido(n, 1 given n % 2 is 1 otherwise 2) cycle n in range(1, 21)]

// ── 1. O problema do N+1 ──
//
// Uma consulta que pede 20 pedidos e, de cada um, o cliente, faz 21
// idas ao banco: uma para os pedidos e uma por cliente. O servidor
// parece rapido e o banco morre.
//
// Aqui a lista 'idas' CONTA — sem contar, um lote que devolve o valor
// certo e mesmo assim consulta vinte vezes passaria despercebido.
idas := []

action buscar_clientes(ids):
    idas.append(len(ids))
    yield [clientes[i] cycle i in ids]

esq := Lavra.esquema("n1")
Lavra.tipo(esq, Cliente)
Lavra.tipo(esq, Pedido)
Lavra.campo(esq, "Cliente", "nome", "String!")
Lavra.campo(esq, "Pedido", "id", "Integer!")

// O resolvedor nao BUSCA — ele PEDE. Os pedidos da mesma volta sao
// juntados num so.
// Este precisa do 'ctx' — e o ctx e o TERCEIRO. Nao da para pular o do
// meio, entao o '_args' diz que ele esta ali de proposito.
action cliente_do_pedido(p, _args, ctx):
    yield Lavra.pedir(ctx, "clientes", p.cliente_id)

Lavra.campo(esq, "Pedido", "cliente", "Cliente!", resolve := cliente_do_pedido)
Lavra.busca(esq, "pedidos", "[Pedido!]!",
    args := {"limite": {"tipo": "Integer", "padrao": 20}},
    resolve := lambda r, a, c => pedidos[0:a["limite"]])
Lavra.conferir(esq)

// O lote vive no CONTEXTO, e morre com a consulta. Um lote de processo
// guardaria o cliente depois que ele mudou, e serviria o valor velho
// para outra pessoa.
ctx := Lavra.contexto({})
_ := Lavra.lote(ctx, "clientes", buscar_clientes)

r := Lavra.executar(esq, """
busca:
    pedidos:
        id
        cliente:
            nome
    """, contexto := ctx)

out $"20 pedidos, {len(idas)} ida(s) ao banco"
assert len(r["dados"]["pedidos"]) is 20, "os vinte vieram"
assert len(idas) is 1, "UMA ida — sem o lote seriam 20"
assert idas[0] is 2, "e ela levou as duas chaves distintas"
out r["extensoes"]["lotes"]

// ── 2. Os limites ──
//
// Um grafo com ciclo deixa pedir 'pedido.cliente.pedidos.cliente…'
// para sempre. E a forma mais barata de derrubar um servidor de
// consulta, e descobrir isso RESOLVENDO ja e tarde.
_ := Lavra.limites(esq, profundidade := 2)

fundo := Lavra.executar(esq, """
busca:
    pedidos:
        cliente:
            nome
""")
out fundo["erros"][0]["mensagem"]
assert fundo["dados"] is void, "recusada antes de resolver"
assert "profundidade" in fundo["erros"][0]["mensagem"]

_ := Lavra.limites(esq, profundidade := 12)

// ── 3. Paginacao por cursor ──
//
// Paginar por posicao ('pule 3, traga 3') quebra do jeito mais dificil
// de ver: se alguem insere uma linha entre a pagina 1 e a 2, um item
// DESAPARECE — ele desceu para a posicao que ja foi lida.
p1 := Lavra.pagina(pedidos, primeiros := 3)
assert len(p1["itens"]) is 3
assert p1["info"]["tem_proxima"], "ha mais"

p2 := Lavra.pagina(pedidos, primeiros := 3, depois := p1["info"]["cursor_fim"])
out [i.id cycle i in p2["itens"]]
assert p2["itens"][0].id is 4, "continua exatamente onde parou"
assert p2["total"] is 20, "o total nao depende da pagina"

// ── 4. O erro parcial ──
//
// Quem pediu dois campos e teve problema em um recebe UM — e nao zero.
Lavra.campo(esq, "Cliente", "risco", "String",
    resolve := lambda c, a, ctx => Lavra.erro("o servico de risco caiu"))

ctx2 := Lavra.contexto({})
_ := Lavra.lote(ctx2, "clientes", buscar_clientes)

parcial := Lavra.executar(esq, """
busca:
    pedidos(limite: 1):
        cliente:
            nome
            risco
    """, contexto := ctx2)

out parcial["erros"][0]["caminho"], "|", parcial["erros"][0]["mensagem"]
assert parcial["dados"]["pedidos"][0]["cliente"]["nome"] is "Ana", "o resto veio"
assert parcial["dados"]["pedidos"][0]["cliente"]["risco"] is void
assert len(parcial["erros"]) is 1

out "230 ok"`, lang: 'df', title: `exercicios/33-lavra/233_lavra_n1_e_limites.df` },
  {"h3": "O N+1, em uma frase"},
  {"p": "Uma consulta que pede 20 pedidos e, de cada um, o cliente, faz **21** consultas ao banco: uma para os pedidos e uma por cliente."},
  { code: `busca:
    pedidos:
        numero
        cliente:
            nome`, lang: 'lavra' },
  {"p": "O servidor parece rápido — cada consulta é de milissegundos — e o banco morre. É o problema mais conhecido de qualquer camada de consulta, e o mais fácil de introduzir sem perceber: a consulta acima tem cinco linhas."},
  {"h3": "O lote, em uma frase"},
  {"p": "O resolvedor não **busca** — ele **pede**. Os pedidos feitos na mesma volta são juntados num só:"},
  { code: `action cliente_do_pedido(p, _args, ctx):
    yield Lavra.pedir(ctx, "clientes", p.cliente_id)`, lang: 'df' },
  {"p": "E o lote é declarado no contexto da consulta:"},
  { code: `ctx := Lavra.contexto({})
_ := Lavra.lote(ctx, "clientes", buscar_clientes)`, lang: 'df' },
  {"h3": "Por que o teste conta a IDA, e não o resultado"},
  {"p": "Este é o ponto do exercício. Um lote que devolve o valor certo e mesmo assim consulta vinte vezes **passa em qualquer teste que só olhe os dados**:"},
  { code: `idas := []

action buscar_clientes(ids):
    idas.append(len(ids))
    yield [clientes[i] cycle i in ids]

...
assert len(idas) is 1, "UMA ida — sem o lote seriam 20"`, lang: 'df' },
  {"p": "O `r[\"extensoes\"][\"lotes\"]` traz o mesmo número para se olhar em produção:"},
  { code: `{clientes: {chamadas: 1, chaves: 20, economia: 19}}`, lang: 'text' },
  {"h3": "Duas decisões do lote"},
  {"p": "**O lote vive no contexto, e não no módulo.** Um lote de processo guardaria o cliente depois que ele mudou, e serviria o valor velho para outra pessoa. O contexto morre com a consulta, que é exatamente a vida útil que um cache de leitura pode ter aqui."},
  {"p": "**A ordem da resposta é a ordem do pedido.** A função recebe as chaves e devolve os valores na MESMA ordem — ou um vault de chave para valor, que não depende de ordem nenhuma. Uma lista fora de ordem é o bug clássico da técnica: cada pedido recebe o cliente de outro, e **nada falha**."},
  {"h3": "Os limites"},
  {"p": "Um grafo com ciclo deixa pedir `pedido.cliente.pedidos.cliente…` para sempre:"},
  { code: `Lavra.limites(esq, profundidade := 8, complexidade := 1000, itens := 500)`, lang: 'df' },
  {"table": {"head": ["Limite", "O que impede"], "rows": [["`profundidade`", "a consulta funda num grafo com ciclo"], ["`complexidade`", "uma consulta curta que pede um milhão de itens"], ["`itens`", "um resolvedor que devolve a tabela inteira num dia de pico"]]}},
  {"p": "Os três são conferidos **antes** de resolver qualquer coisa. A consulta funda é a forma mais barata de derrubar um servidor de consulta: cabe num tuíte, e o servidor gasta tudo o que tem antes de responder."},
  {"h3": "Paginação por cursor"},
  {"p": "Paginar por posição (`pule 3, traga 3`) quebra do jeito mais difícil de ver: se alguém insere uma linha entre a página 1 e a 2, um item **desaparece** — ele desceu para a posição que já foi lida."},
  { code: `p1 := Lavra.pagina(pedidos, primeiros := 3)
p2 := Lavra.pagina(pedidos, primeiros := 3, depois := p1["info"]["cursor_fim"])`, lang: 'df' },
  {"p": "Com cursor, a página seguinte começa exatamente onde a anterior parou."},
  {"h3": "O erro parcial"},
  { code: `[pedidos, 0, cliente, risco] | o servico de risco caiu`, lang: 'text' },
  {"p": "Quem pediu dois campos e teve problema em um recebe **um** — não zero. É a diferença entre uma tela com um aviso e uma tela vazia. O `caminho` diz exatamente qual campo quebrou."},
  {"h3": "Saída esperada"},
  { code: `20 pedidos, 1 ida(s) ao banco
{clientes: {chamadas: 1, chaves: 20, economia: 19}}
a consulta tem profundidade 3, e o limite é 2
[4, 5, 6]
[pedidos, 0, cliente, risco] | o servico de risco caiu
230 ok`, lang: 'text' },
  {"h3": "Para experimentar"},
  {"list": ["Tire o `Lavra.pedir` e busque direto no resolvedor. Veja `idas` ir para 20.", "Devolva `[clientes[i] cycle i in reversed(ids)]` no lote. O Lavra recusa, e"]},
  {"p": "diz por quê — porque esse é o único sintoma que a falha tem."},
  {"list": ["Baixe `itens` para 5 e peça os 20 pedidos."]},
  {"h2": "234 · Lavra: contratos, mudancas, servidor e federacao"},
  {"p": "**Enunciado.** sirva o esquema por HTTP e componha dois servicos num so."},
  { code: `adopt Arcane.Lavra as Lavra
adopt Arcane.Web as Web
adopt Arcane.Serialization as Serde

// ── 1. Contrato: campos que varios tipos prometem ter ──
record Artigo:
    id: Integer
    titulo: String

record Video:
    id: Integer
    titulo: String
    minutos: Integer

esq := Lavra.esquema("cms")

Lavra.tipo(esq, Artigo, cumpre := ["Conteudo"])
Lavra.tipo(esq, Video, cumpre := ["Conteudo"])
Lavra.campo(esq, "Artigo", "titulo", "String!")
Lavra.campo(esq, "Video", "titulo", "String!")
Lavra.campo(esq, "Video", "minutos", "Integer!")

// O contrato precisa saber, na hora, QUAL tipo concreto e aquele valor.
action que_tipo(valor):
    yield "Video" given "minutos" in valor.fields otherwise "Artigo"

Lavra.contrato(esq, "Conteudo", {"id": "Integer", "titulo": "String"},
    resolve_tipo := que_tipo)

acervo := [Artigo(1, "Sobre a forja"), Video(2, "Como fundir", 12)]
Lavra.busca(esq, "acervo", "[Conteudo!]!", resolve := lambda r, a, c => acervo)

// ── 2. Mudanca: a escrita aparece no NOME da operacao ──
//
// Quem le a consulta sabe, sem abrir o resolvedor, se aquilo muda
// alguma coisa. Uma entrada e um tipo DIFERENTE do de saida: o Artigo
// que sai tem 'id', o que entra nao.
Lavra.entrada(esq, {"titulo": "String"}, nome := "NovoArtigo")
Lavra.campo(esq, "NovoArtigo", "titulo", "String!")

action criar_artigo(_raiz, args):
    novo := Artigo(len(acervo) + 1, args["dados"]["titulo"])
    acervo.append(novo)
    yield novo

Lavra.mudanca(esq, "criarArtigo", "Artigo!", args := {"dados": "NovoArtigo!"},
    resolve := criar_artigo)

Lavra.conferir(esq)

r := Lavra.executar(esq, """
busca:
    acervo:
        titulo
        ... em Video:
            minutos
""")
out r["dados"]
assert r["dados"]["acervo"][1]["minutos"] is 12, "o trecho condicional casou"
assert "minutos" not in r["dados"]["acervo"][0], "o artigo nao tem minutos"

m := Lavra.executar(esq, """
mudanca:
    criarArtigo(dados: {titulo: "Recem-forjado"}):
        id
        titulo
""")
assert m["dados"]["criarArtigo"]["titulo"] is "Recem-forjado"
assert len(acervo) is 3, "a mudanca mudou mesmo"

// ── 3. Servir por HTTP ──
//
// Uma rota, um metodo: POST executa, GET devolve o esquema em texto.
// Nao ha uma rota por busca — a consulta ja diz o que quer, e uma
// rota por campo desfaria a razao de o Lavra existir.
par := Lavra.em_segundo_plano(esq)
app := par[0]
porta := par[1]
defer:
    Lavra.parar(app)

base := $"http://127.0.0.1:{porta}/lavra"

resposta := Web.post(base, {"consulta": "busca:\\n    acervo:\\n        titulo"})
corpo := Serde.from_json(resposta["body"])
out resposta["status"], len(corpo["dados"]["acervo"])
assert resposta["status"] is 200
assert len(corpo["dados"]["acervo"]) is 3

// Um erro de consulta responde 200 — o HTTP falou, e a resposta tem
// 'dados' e 'erros'. E o que permite dados parciais.
ruim := Web.post(base, {"consulta": "busca:\\n    naoExiste"})
assert ruim["status"] is 200
assert Serde.from_json(ruim["body"])["dados"] is void

esquema_em_texto := Web.get(base)
assert "tipo Video cumpre Conteudo:" in esquema_em_texto["body"], "o GET versiona o esquema"

// ── 4. Federacao: dois servicos, um esquema ──
contas := Lavra.esquema("contas")
Lavra.tipo(contas, {"id": "Integer", "nome": "String"}, nome := "Conta")
Lavra.campo(contas, "Conta", "nome", "String!")
Lavra.busca(contas, "conta", "Conta", args := {"id": "Integer!"},
    resolve := lambda r, a, c => {"id": a["id"], "nome": "Ana"})

vendas := Lavra.esquema("vendas")
Lavra.tipo(vendas, {"id": "Integer", "total": "Float"}, nome := "Venda")
Lavra.campo(vendas, "Venda", "total", "Float!")
Lavra.busca(vendas, "venda", "Venda", args := {"id": "Integer!"},
    resolve := lambda r, a, c => {"id": a["id"], "total": 9.9})

portao := Lavra.portao()
Lavra.juntar(portao, "contas", contas)
Lavra.juntar(portao, "vendas", vendas)

// O campo que atravessa a fronteira e declarado como extensao.
Lavra.estender(portao, "Conta", "vendas", "[Venda!]!",
    resolve := lambda conta, a, ctx => [{"id":1, "total":9.9}])

f := Lavra.executar(portao.esquema, """
busca:
    conta(id: 1):
        nome
        vendas:
            total
""")
out f["dados"]
assert f["dados"]["conta"]["vendas"][0]["total"] is 9.9

// De onde vem cada tipo — a resposta para "quem declara isto?"
mapa := Lavra.mapa(portao)
out mapa["tipos"]["Conta"], mapa["tipos"]["Venda"]
assert mapa["tipos"]["Conta"] is "contas"
assert mapa["tipos"]["Venda"] is "vendas"

out "231 ok"`, lang: 'df', title: `exercicios/33-lavra/234_lavra_servidor_e_federacao.df` },
  {"h3": "Contratos"},
  {"p": "Um **contrato** são campos que vários tipos prometem ter:"},
  { code: `Lavra.tipo(esq, Artigo, cumpre := ["Conteudo"])
Lavra.tipo(esq, Video, cumpre := ["Conteudo"])

Lavra.contrato(esq, "Conteudo", {"id": "Integer", "titulo": "String"},
    resolve_tipo := que_tipo)`, lang: 'df' },
  {"p": "Quem consulta pede os campos do contrato, e usa `... em Tipo:` para pedir o que só existe num deles:"},
  { code: `busca:
    acervo:
        titulo
        ... em Video:
            minutos`, lang: 'lavra' },
  {"p": "O `resolve_tipo` responde **qual tipo concreto é aquele valor**. Sem ele, o Lavra tenta descobrir pelo nome do record — e quando não consegue, diz isso com a lista dos candidatos, em vez de devolver um objeto pela metade."},
  {"p": "O contrato é conferido na montagem: um tipo que declara cumpri-lo e não tem um dos campos **para o `Lavra.conferir`**."},
  {"h3": "Mudanças"},
  {"p": "A escrita aparece no **nome da operação**:"},
  { code: `mudanca:
    criarArtigo(dados: {titulo: "Recem-forjado"}):
        id
        titulo`, lang: 'lavra' },
  {"p": "Quem lê a consulta sabe, sem abrir o resolvedor, se aquilo muda alguma coisa — e é o que permite a um intermediário guardar uma `busca` em cache e nunca uma `mudanca`."},
  {"p": "**Entrada e saída são tipos diferentes**"},
  { code: `Lavra.entrada(esq, {"titulo": "String"}, nome := "NovoArtigo")`, lang: 'df' },
  {"p": "O `Artigo` que sai tem `id`; o `NovoArtigo` que entra não tem. Usar o mesmo tipo nos dois lados obrigaria a marcar metade dos campos como opcionais — e aí nenhum deles seria conferido."},
  {"h3": "Servir por HTTP"},
  { code: `par := Lavra.em_segundo_plano(esq)
app := par[0]
porta := par[1]`, lang: 'df' },
  {"p": "Uma rota, um método:"},
  {"table": {"head": ["Rota", "O que faz"], "rows": [["`POST /lavra`", "executa a consulta"], ["`GET /lavra`", "devolve o esquema em texto"], ["`WS /lavra/assinar`", "as assinaturas"]]}},
  {"p": "Não há uma rota por busca: a consulta já diz o que quer, e uma rota por campo desfaria a razão de o Lavra existir."},
  {"p": "**Erro de consulta responde 200**"},
  {"p": "Parece errado e não é: o **HTTP falou**, e a resposta tem `dados` e `erros`. Um 400 obrigaria o cliente a ter dois caminhos de leitura para o mesmo corpo, e esconderia o caso normal — dados parciais com um erro num campo."},
  {"p": "O 400 fica para o que nem chegou a ser consulta (corpo ilegível, sem `consulta`), e o 500 para o que quebrou fora dela."},
  {"h3": "Federação"},
  {"p": "Cada time tem o seu serviço. Quem consulta não quer saber disso:"},
  { code: `portao := Lavra.portao()
Lavra.juntar(portao, "contas", contas)
Lavra.juntar(portao, "vendas", vendas)

Lavra.estender(portao, "Conta", "vendas", "[Venda!]!", resolve := vendas_da_conta)`, lang: 'df' },
  {"p": "O campo que atravessa a fronteira é declarado como **extensão** — ele não pertence a nenhum dos dois serviços sozinho."},
  {"p": "**Conflito de nome é erro**"},
  {"p": "Dois serviços que declaram `Usuario` param a composição. Fundir os dois em silêncio faria a resposta depender da **ordem do `juntar`** — que funciona na máquina de quem escreveu e muda quando alguém reordena duas linhas."},
  {"p": "**O mapa**"},
  { code: `out Lavra.mapa(portao)`, lang: 'df' },
  {"p": "É a resposta para \"quem declara isto?\" — a pergunta que mais se faz num esquema federado, e a que mais custa responder lendo código de três repositórios."},
  {"h3": "Saída esperada"},
  { code: `{acervo: [{titulo: Sobre a forja}, {titulo: Como fundir, minutos: 12}]}
200 3
{conta: {nome: Ana, vendas: [{total: 9.9}]}}
contas vendas
231 ok`, lang: 'text' },
  {"h3": "Para experimentar"},
  {"list": ["Peça `minutos` sem o `... em Video:` e veja a validação recusar — `Conteudo`"]},
  {"p": "não promete `minutos`."},
  {"list": ["Junte dois esquemas com um tipo de mesmo nome e leia a mensagem.", "Chame `GET /lavra` no navegador: o esquema em texto é o que se versiona."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/33-lavra/232_lavra_basico.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '232-lavra-o-esquema-e-a-consulta', text: "232 · Lavra: o esquema e a consulta", level: 2 as const }, { id: 'o-problema-que-o-lavra-resolve', text: "O problema que o Lavra resolve", level: 3 as const }, { id: 'o-esquema-nasce-dos-seus-records', text: "O esquema nasce dos seus records", level: 3 as const }, { id: 'a-notacao-de-tipo', text: "A notação de tipo", level: 3 as const }, { id: 'campo-calculado', text: "Campo calculado", level: 3 as const }, { id: 'conferir-fecha-o-esquema', text: "`conferir` fecha o esquema", level: 3 as const }, { id: 'apelidos', text: "Apelidos", level: 3 as const }, { id: 'variaveis', text: "Variáveis", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'para-experimentar', text: "Para experimentar", level: 3 as const }, { id: '233-lavra-o-n1-os-limites-e-a-paginacao', text: "233 · Lavra: o N+1, os limites e a paginacao", level: 2 as const }, { id: 'o-n1-em-uma-frase', text: "O N+1, em uma frase", level: 3 as const }, { id: 'o-lote-em-uma-frase', text: "O lote, em uma frase", level: 3 as const }, { id: 'por-que-o-teste-conta-a-ida-e-nao-o-resultado', text: "Por que o teste conta a IDA, e não o resultado", level: 3 as const }, { id: 'duas-decisoes-do-lote', text: "Duas decisões do lote", level: 3 as const }, { id: 'os-limites', text: "Os limites", level: 3 as const }, { id: 'paginacao-por-cursor', text: "Paginação por cursor", level: 3 as const }, { id: 'o-erro-parcial', text: "O erro parcial", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'para-experimentar', text: "Para experimentar", level: 3 as const }, { id: '234-lavra-contratos-mudancas-servidor-e-federacao', text: "234 · Lavra: contratos, mudancas, servidor e federacao", level: 2 as const }, { id: 'contratos', text: "Contratos", level: 3 as const }, { id: 'mudancas', text: "Mudanças", level: 3 as const }, { id: 'servir-por-http', text: "Servir por HTTP", level: 3 as const }, { id: 'federacao', text: "Federação", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'para-experimentar', text: "Para experimentar", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"33 · Lavra"}
      description={"3 exercícios: esquema, consulta, lote contra o N+1, servidor e federação."}
      href={"/docs/exercicios/33-lavra"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
