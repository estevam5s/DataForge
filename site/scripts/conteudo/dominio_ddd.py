# -*- coding: utf-8 -*-
"""Arcane.Dominio — DDD com as distinções cobradas, e não nomeadas."""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio",
"title": "Domínio e DDD",
"description": "Valor, entidade, agregado, evento, regra, repositório e unidade de trabalho — cobrados, e não só nomeados.",
"blocos": [
 {"p": "**`Arcane.Dominio`** traz as peças do *Domain-Driven Design*. Ele não é um framework que obriga a modelar de um jeito, e não é uma camada sobre banco: DDD é um conjunto de **distinções**, e o valor delas está em serem cobradas."},
 {"p": "Um `blueprint` chamado `Pedido` com um comentário `// agregado` em cima não impede ninguém de mexer nos itens por fora — e é justamente isso que faz a modelagem se desfazer em seis meses. O que este módulo acrescenta é a recusa."},
 {"code": """adopt Arcane.Dominio as D

pedido := D.agregado("Pedido", "PED-7", total := 0)
pedido.invariante("o total nunca e negativo",
    lambda p => p.ler("total", 0) bigger_eq 0)

mark @pedido.comando("acrescentar")
action acrescentar(p, nome, preco):
    p.mudar(total := p.ler("total", 0) + preco)
    p.aconteceu("ItemAcrescentado", {"item": nome, "preco": preco})

pedido.acrescentar("cafe", 32)
out pedido.ler("total")        // 32

pedido.mudar(total := 999999)  // recusado: so muda dentro de um comando""", "lang": "df"},

 {"h2": "As sete peças"},
 {"table": {"head": ["", "O que é", "O que ela recusa"], "rows": [
   ["`valor`", "igualdade por **conteúdo**, imutável", "criar um valor que a regra não permite"],
   ["`entidade`", "igualdade por **identidade**, estado muda", "confundir duas pessoas de mesmo nome"],
   ["`agregado`", "a única porta de escrita", "escrever por fora, e sair de um comando inválido"],
   ["`evento`", "um fato no passado, imutável", "reescrever o que já aconteceu"],
   ["`regra`", "condição de negócio combinável", "um `given` que não dá para reaproveitar"],
   ["`repositorio`", "guarda agregados **inteiros**", "guardar algo sem identidade"],
   ["`unidade`", "confirma tudo, ou nada", "publicar um fato que a transação vai desfazer"]]}},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/dominio/valores", "title": "Valores e entidades", "desc": "A distinção que decide metade da modelagem."},
   {"href": "/docs/dominio/agregados", "title": "Agregados e invariantes", "desc": "A porta única, e o comando que desfaz."},
   {"href": "/docs/dominio/eventos", "title": "Eventos e unidade de trabalho", "desc": "Por que o fato espera a confirmação."},
   {"href": "/docs/dominio/contextos", "title": "Regras e contextos", "desc": "A regra como objeto, e a fronteira entre modelos."}]},
 {"h2": "Fonte de eventos e além"},
 {"p": "Guardar os fatos em vez do estado, a versão esperada que recusa a decisão velha, projeções, CQRS, processos, serviços e a camada anticorrupção."},
 {"cards": [{"href": "/docs/dominio/fonte-de-eventos", "title": "Fonte de eventos", "desc": "O estado não é guardado: é derivado dos fatos. O armazém, as duas funções puras e o que isso compra."}, {"href": "/docs/dominio/concorrencia-otimista", "title": "Concorrência otimista", "desc": "Dois comandos decididos sobre a mesma versão: um grava, o outro recebe VersionConflictError — e tenta de novo."}, {"href": "/docs/dominio/projecoes", "title": "Projeções", "desc": "Modelos de leitura montados dos eventos: idempotentes, reconstruíveis, e cada um do tamanho da sua pergunta."}, {"href": "/docs/dominio/cqrs", "title": "CQRS", "desc": "O lado que decide e o lado que responde, separados: quando isso simplifica, e quando é peso morto."}, {"href": "/docs/dominio/processos", "title": "Processos e sagas", "desc": "Quando um fato de um agregado precisa virar comando em outro: o gerente de processo, e a compensação."}, {"href": "/docs/dominio/servicos", "title": "Serviços de domínio", "desc": "A regra que não pertence a nenhuma entidade — e por que ela não é um 'Manager' com tudo dentro."}, {"href": "/docs/dominio/anticorrupcao", "title": "Camada anticorrupção", "desc": "O modelo de um sistema externo não entra inteiro: é traduzido na fronteira, num lugar só."}, {"href": "/docs/dominio/testes", "title": "Testar o domínio", "desc": "Dado estes fatos, quando este comando, então estes fatos — ou esta recusa."}, {"href": "/docs/dominio/modelagem", "title": "Modelar o domínio", "desc": "Linguagem ubíqua, event storming e onde traçar a fronteira de um agregado."}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/valores",
"title": "Valores e entidades",
"description": "A distinção que decide metade da modelagem — e como cada lado é cobrado.",
"blocos": [
 {"p": "Duas pessoas com o mesmo nome são **duas pessoas**. E a mesma pessoa com outro nome continua sendo ela. O que separa uma entidade de um objeto de valor não é a mutabilidade — é a **continuidade**."},

 {"h2": "Objeto de valor"},
 {"code": """steady Dinheiro := D.valor("Dinheiro", ["quantia", "moeda"],
    regra := lambda v => v["quantia"] bigger_eq 0,
    motivo := "dinheiro nao e negativo")

dez := Dinheiro(10, "BRL")
outro := Dinheiro(10, "BRL")
assert dez is outro                  // o MESMO valor

vinte := dez.com(quantia := 20)      // outro valor; o original nao muda
assert dez.quantia is 10""", "lang": "df"},
 {"p": "O `record` da linguagem já dá a imutabilidade e a igualdade estrutural, e essas duas metades são a maior parte. O que ele não dá é a **regra**: um `Dinheiro(-5, \"BRL\")` é um record perfeitamente válido, e o negócio descobre isso três camadas adiante, num extrato negativo."},
 {"callout": {"tipo": "nota", "titulo": "A regra é cobrada na criação — e no `com`",
              "texto": "A criação é o único ponto em que ela pode impedir o valor errado de existir. E um refinamento que só valesse ali seria uma sugestão, não um tipo: `dez.com(quantia := -1)` é recusado pela mesma regra."}},
 {"p": "Uma regra que **estoura** não vira \"valor inválido\": ela vira um erro dizendo que a regra quebrou. Dizer \"inválido\" ali esconderia o defeito real, que é da regra e não do valor."},

 {"h2": "Entidade"},
 {"code": """ana := D.entidade("Pessoa", "1", nome := "Ana")
ana_maria := D.entidade("Pessoa", "1", nome := "Ana Maria")
homonima := D.entidade("Pessoa", "2", nome := "Ana")

assert ana is ana_maria       // mesma id, outro nome  -> a mesma pessoa
assert ana isnt homonima      // mesmo nome, outra id  -> duas pessoas""", "lang": "df"},
 {"p": "O identificador é **texto**, e nasce com o objeto (`D.novo_id()` dá um UUID4). Um id que o banco gera obriga a salvar antes de ter identidade — e no intervalo entre criar e confirmar o objeto existe sem ser ele mesmo."},

 {"h2": "E um valor não entra num repositório"},
 {"code": """D.repositorio("Dinheiro").guardar(Dinheiro(10, "BRL"))
// erro: o que vai para um repositorio precisa de identidade""", "lang": "df"},
 {"p": "Não é uma limitação: é a distinção sendo cobrada. Se a sua peça precisa distinguir duas instâncias iguais, ela é uma **entidade** — e o módulo diz isso em vez de deixar passar."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/agregados",
"title": "Agregados e invariantes",
"description": "A única porta de escrita, a invariante cobrada na saída, e o comando que desfaz.",
"blocos": [
 {"p": "Um agregado é a única porta de escrita de um grupo de objetos. Três cobranças sustentam isso, e cada uma evita um defeito diferente."},

 {"h2": "1. O estado só muda por comando"},
 {"code": """pedido := D.agregado("Pedido", "PED-7", total := 0, itens := 0)
pedido.invariante("o total nunca e negativo",
    lambda p => p.ler("total", 0) bigger_eq 0)
pedido.invariante("um pedido tem no maximo 3 itens",
    lambda p => p.ler("itens", 0) smaller_eq 3)

pedido.mudar(total := -1)
// erro: 'Pedido' so muda dentro de um comando.""", "lang": "df"},
 {"p": "Se qualquer um escreve, a invariante não vale nada — porque não há onde cobrá-la. O comando é o lugar."},

 {"h2": "2. A invariante é cobrada na SAÍDA"},
 {"p": "Cobrar na entrada deixa o objeto quebrado quando o comando falha no meio. Cobrar na saída garante que ninguém observa um estado inválido — e é isso que faz o agregado ser a única porta."},
 {"code": """mark @pedido.comando("descontar")
action descontar(p, quanto):
    p.mudar(total := p.ler("total", 0) - quanto)

monitor:
    pedido.descontar(999)
handle Error as e:
    out e.message      // 'Pedido' violou: o total nunca e negativo""", "lang": "df"},

 {"h2": "3. O comando que falha no meio é desfeito por inteiro"},
 {"p": "Estado e eventos voltam ao que eram, e a versão **não** avança. Sem isso, metade da mudança fica aplicada e a próxima leitura vê um agregado que nunca deveria existir — inclusive um evento de um comando que não aconteceu, que é a pior classe de fato."},
 {"code": """assert pedido.ler("total") is 50      // como antes da tentativa
assert pedido.versao() is 2           // a versao tambem voltou
assert len(pedido.eventos()) is 2     // nada novo foi anotado""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "`versao()` serve a travas otimistas",
              "texto": "Ela conta quantos comandos já rodaram. Gravar comparando a versão lida é como dois usuários editando o mesmo pedido deixam de sobrescrever um ao outro em silêncio."}},

 {"h2": "A invariante que estoura é um bug dela"},
 {"p": "Como na regra de um valor: um erro dentro da condição vira uma mensagem dizendo que a **invariante** quebrou, e não que o estado é inválido. As duas coisas exigem correções em lugares diferentes."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/eventos",
"title": "Eventos e unidade de trabalho",
"description": "Por que o fato espera a confirmação, e o que acontece quando ela não vem.",
"blocos": [
 {"p": "Um evento é um fato que **aconteceu**. O nome no passado não é estilo: um evento chamado `CriarPedido` é um comando disfarçado, e quem o recebe acha que pode recusá-lo. Um `PedidoCriado` já aconteceu — quem escuta reage, e não decide."},
 {"code": """e := D.evento("PedidoPago", {"valor": 120})
e.valor := 0
// erro: o evento 'PedidoPago' ja aconteceu: ele nao muda.""", "lang": "df"},

 {"h2": "O evento fica guardado até a confirmação"},
 {"code": """publicados := []

action anotar(fato):
    publicados.append(fato.nome)

u := D.unidade(publicar := anotar)
u.registrar(pedido, pedidos)     // o agregado e o repositorio dele
assert len(publicados) is 0      // o mundo ainda nao sabe

u.confirmar()
assert len(publicados) is 2      // agora sim""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Publicar na hora é o defeito clássico",
              "texto": "O mundo reage a um fato que a transação ainda pode desfazer: o e-mail sai, e o pedido não existe. `desfazer()` descarta os eventos junto — eles nunca aconteceram."}},

 {"h2": "Todas as invariantes antes de qualquer gravação"},
 {"p": "A unidade confere **todos** os agregados registrados e só então grava **qualquer** um deles. Se a segunda gravação falhasse por invariante, a primeira já estaria no banco — e a transação de domínio teria vazado pela metade."},

 {"h2": "E não dá para desfazer o confirmado"},
 {"code": """u.confirmar()
u.desfazer()
// erro: nao da para desfazer o que ja foi confirmado.
//   dica: publique um evento de compensacao""", "lang": "df"},
 {"p": "Os eventos já saíram, e quem reagiu a eles não tem como voltar atrás. A saída é a compensação — a mesma que a `Saga` do `Arcane.Malha` implementa quando a transação atravessa a rede."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/dominio/contextos",
"title": "Regras e contextos delimitados",
"description": "A regra como objeto, e a tradução que atravessa a fronteira entre dois modelos.",
"blocos": [
 {"h2": "A regra é um objeto, e não um `given`"},
 {"p": "Um `given` dentro do serviço não pode ser combinado, nem reaproveitado na consulta que lista \"quem pode\", nem explicado ao usuário. Os três usos são a **mesma** regra, e escrevê-la três vezes é como as três divergem."},
 {"code": """steady grande := D.regra("o pedido passa de R$ 100",
    lambda p => p.ler("total", 0) bigger 100)
steady cheio := D.regra("o pedido tem ao menos 3 itens",
    lambda p => p.ler("itens", 0) bigger_eq 3)

steady vale_frete := grande.e(cheio)

given not vale_frete.vale(pedido):
    out vale_frete.por_que_nao(pedido)   // "o pedido passa de R$ 100"

com_frete := pedidos.que(vale_frete)     // a MESMA regra, como consulta""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "`por_que_nao` aponta a parte que falhou",
              "texto": "E não a frase inteira. \"maior de idade E mora no Brasil\" não diz qual das duas a pessoa precisa resolver — e essa frase é o que vai para a tela."}},
 {"p": "As combinações são `e`, `ou` e `nao`. Uma regra que **estoura** levanta, em vez de responder \"não vale\": devolver falso esconderia o defeito, e o usuário seria recusado por um bug."},

 {"h2": "Contexto delimitado"},
 {"p": "O \"Cliente\" de Vendas tem limite de crédito; o de Suporte tem plano e chamados abertos. São o mesmo nome e **não** são o mesmo conceito. Passar o objeto inteiro de um lado ao outro é o que faz dois modelos virarem um só — e o único não serve a ninguém."},
 {"code": """suporte := D.contexto("Suporte")

suporte.receber("Vendas", "Cliente", {"nome": "Ana", "credito": 5000})
// erro: 'Suporte' nao sabe traduzir 'Cliente' de 'Vendas'.

suporte.traduzir_de("Vendas", "Cliente",
    lambda c => {"nome": c["nome"], "plano": "basico", "chamados": 0})

aqui := suporte.receber("Vendas", "Cliente", {"nome": "Ana", "credito": 5000})
assert "credito" not in aqui""", "lang": "df"},
 {"p": "É a *camada anticorrupção*: sem ela, o modelo de fora entra inteiro, e o de dentro passa a ter campos que só existem porque o outro time os tem."},

 {"h2": "Um ouvinte que estoura não impede os outros"},
 {"code": """mark @vendas.ao_acontecer("PedidoPago")
action faturar(fato):
    ...

falhas := vendas.publicar(D.evento("PedidoPago", {"pedido": "PED-7"}))
out len(falhas)      // quantos ouvintes quebraram — os demais rodaram""", "lang": "df"},
 {"p": "Eles reagem a um fato que **já aconteceu**: derrubar os demais por causa de um deixaria o mundo parcialmente atualizado sem ninguém saber. As falhas voltam como dado, para quem quiser agir sobre elas."},

 {"h2": "O exemplo completo"},
 {"p": "`examples/dominio_ddd.df` percorre as sete peças com `assert` em cada afirmação — inclusive as recusas."},
]},
]
