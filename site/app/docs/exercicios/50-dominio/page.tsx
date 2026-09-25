// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "50 · Domínio e DDD",
  description: "15 exercícios: valor, entidade, agregado, evento, regra e unidade de trabalho.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Sistemas e arquitetura** · valor, entidade, agregado, evento, regra e unidade de trabalho · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 50`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[268](#268-o-que-separa-um-valor-de-uma-entidade)", "**o que separa um valor de uma entidade**", "a distincao que decide metade da modelagem. Duas pessoas"], ["[269](#269-a-regra-cobrada-na-criacao)", "**a regra cobrada na criacao**", "um 'record' da a imutabilidade e a igualdade estrutural."], ["[270](#270-o-agregado-e-a-unica-porta-de-escrita)", "**o agregado e a unica porta de escrita**", "se qualquer um escreve, a invariante nao vale nada —"], ["[271](#271-o-fato-espera-a-confirmacao)", "**o fato espera a confirmacao**", "publicar um evento na hora faz o mundo reagir a um fato"], ["[272](#272-a-regra-de-negocio-que-se-combina-e-se-explica)", "**a regra de negocio que se combina e se explica**", "um 'given' dentro do servico nao pode ser combinado, nem"], ["[273](#273-o-repositorio-guarda-agregados-inteiros)", "**o repositorio guarda AGREGADOS INTEIROS**", "um repositorio que devolve meio agregado devolve um"], ["[274](#274-a-fronteira-entre-dois-modelos)", "**a fronteira entre dois modelos**", "o \"Cliente\" de Vendas tem limite de credito; o de Suporte"], ["[275](#275-a-invariante-quebrada-e-um-bug-dela)", "**a invariante quebrada e um bug DELA**", "uma invariante que estoura ao ser avaliada nao quer dizer"], ["[276](#276-o-comando-que-falha-no-meio-nao-deixa-metade)", "**o comando que falha no meio nao deixa metade**", "um comando que muda tres campos e falha no terceiro"], ["[277](#277-a-unidade-confere-todos-antes-de-gravar-qualquer)", "**a unidade confere TODOS antes de gravar QUALQUER**", "se a segunda gravacao falhasse por invariante, a primeira"], ["[278](#278-a-identidade-nasce-com-o-objeto)", "**a identidade nasce com o objeto**", "um id que o banco gera obriga a salvar antes de ter"], ["[279](#279-regras-que-se-combinam-em-arvore)", "**regras que se combinam em arvore**", "'e', 'ou' e 'nao' devolvem regras, e uma regra composta"], ["[280](#280-o-mesmo-contrato-sobre-outro-armazem)", "**o mesmo contrato sobre outro armazem**", "'D.repositorio' guarda em memoria; 'D.repositorio_de'"], ["[281](#281-um-caso-de-uso-inteiro)", "**um caso de uso inteiro**", "juntar as sete pecas num fluxo so — reservar estoque e"], ["[282](#282-a-familia-de-erros-do-dominio)", "**a familia de erros do dominio**", "levantar 'RuntimeError' em tudo faria a distincao morrer"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "268 · o que separa um valor de uma entidade"},
  {"p": "**Enunciado.** a distincao que decide metade da modelagem. Duas pessoas"},
  { code: `// com o mesmo nome sao DUAS pessoas; a mesma pessoa com outro nome
// continua sendo ela. O que separa as duas nao e a mutabilidade — e a
// continuidade.

adopt Arcane.Dominio as D

out "== 1. o valor e igual por CONTEUDO =="

steady Dinheiro := D.valor("Dinheiro", ["quantia", "moeda"])

dez := Dinheiro(10, "BRL")
outro := Dinheiro(10, "BRL")

assert dez is outro
assert dez isnt Dinheiro(10, "USD")
assert dez isnt Dinheiro(11, "BRL")
out $"   {dez} e {outro} sao o mesmo valor"

// Ele serve de chave, porque tem hash coerente com a igualdade.
cotacoes := {}
cotacoes[dez] := "dez reais"
assert cotacoes[Dinheiro(10, "BRL")] is "dez reais"

out ""
out "== 2. a entidade e igual por IDENTIDADE =="

ana := D.entidade("Pessoa", "1", nome := "Ana")
ana_maria := D.entidade("Pessoa", "1", nome := "Ana Maria")
homonima := D.entidade("Pessoa", "2", nome := "Ana")

assert ana is ana_maria
assert ana isnt homonima
out "   mesma id, outro nome -> a mesma pessoa"

// O tipo faz parte da identidade: um Pedido '1' nao e uma Pessoa '1'.
assert D.entidade("Pedido", "1") isnt D.entidade("Pessoa", "1")

// E ela MUDA, sem deixar de ser ela.
ana.mudar(nome := "Ana Souza")
assert ana.ler("nome") is "Ana Souza"
assert ana is ana_maria

out ""
out "== 3. trocar um campo de um valor e criar OUTRO valor =="

vinte := dez.com(quantia := 20)
assert vinte.quantia is 20
assert dez.quantia is 10  // o original nao mudou
assert dez isnt vinte

out "exercicio 268 ok"`, lang: 'df', title: `exercicios/50-dominio/268_valor_e_entidade.df` },
  {"p": "A distinção que decide metade da modelagem, e que não é sobre mutabilidade. Duas pessoas com o mesmo nome são **duas pessoas**; a mesma pessoa com outro nome continua sendo ela. O que separa as duas é a **continuidade**."},
  {"h3": "O valor é igual por conteúdo"},
  {"p": "`Dinheiro(10, \"BRL\")` e outro `Dinheiro(10, \"BRL\")` são o **mesmo valor** — não dois valores parecidos. E é por isso que ele serve de chave num vault: a igualdade e o hash andam juntos."},
  {"p": "Trocar um campo não muda o valor: cria **outro**. `dez.com(quantia := 20)` devolve um novo, e o original continua valendo 10."},
  {"h3": "A entidade é igual por identidade"},
  {"p": "`D.entidade(\"Pessoa\", \"1\", nome := \"Ana\")` e a mesma id com outro nome são a mesma pessoa. Dois nomes iguais com ids diferentes são duas."},
  {"p": "E o **tipo** faz parte da identidade: um `Pedido` de id `\"1\"` não é uma `Pessoa` de id `\"1\"`. Sem isso, dois repositórios distintos colidiriam na mesma chave."},
  {"h3": "E ela muda sem deixar de ser ela"},
  {"p": "`ana.mudar(nome := \"Ana Souza\")` continua igual a `ana_maria`. É o ponto: a entidade é o que sobrevive à mudança de estado."},
  {"p": "---"},
  {"p": "Se a sua peça precisa distinguir duas instâncias iguais, ela é uma **entidade**. Se duas iguais são a mesma coisa, é um **valor** — e aí ela não tem lugar num repositório."},
  {"h2": "269 · a regra cobrada na criacao"},
  {"p": "**Enunciado.** um 'record' da a imutabilidade e a igualdade estrutural."},
  { code: `// O que ele nao da e a REGRA: 'Dinheiro(-5, "BRL")' e um record
// perfeitamente valido, e o negocio descobre isso tres camadas
// adiante, num extrato negativo.

adopt Arcane.Dominio as D

steady Dinheiro := D.valor("Dinheiro", ["quantia", "moeda"],
    regra := lambda v => v["quantia"] bigger_eq 0,
    motivo := "dinheiro nao e negativo")

out "== 1. a criacao e o unico ponto que impede =="

assert Dinheiro(0, "BRL").quantia is 0

recusou := no
monitor:
    Dinheiro(-5, "BRL")
handle ValueObjectError as e:
    recusou := yes
    assert "negativo" in e.message
    out $"   {e.message}"
assert recusou

out ""
out "== 2. a regra vale em TODA fronteira, inclusive no 'com' =="

// Um refinamento que so valesse na criacao seria uma sugestao, e nao
// um tipo.
no_com := no
monitor:
    Dinheiro(10, "BRL").com(quantia := -1)
handle ValueObjectError:
    no_com := yes
assert no_com

out ""
out "== 3. um valor nao muda =="

dez := Dinheiro(10, "BRL")
nao_muda := no
monitor:
    dez.quantia := 99
handle ValueObjectError as e:
    nao_muda := yes
    assert "valor" in e.message
assert nao_muda
assert dez.quantia is 10

out ""
out "== 4. e ele nasce COMPLETO =="

// Um campo vazio faria dois valores 'iguais' diferirem no que ninguem
// preencheu.
incompleto := no
monitor:
    Dinheiro(10)
handle ValueObjectError as e:
    incompleto := yes
    assert "moeda" in e.message
assert incompleto

out ""
out "== 5. a regra que ESTOURA e um bug dela =="

// Dizer 'valor invalido' aqui esconderia o defeito real.
steady Ruim := D.valor("Ruim", ["n"], regra := lambda v => v["naoexiste"])
bug := no
monitor:
    Ruim(1)
handle ValueObjectError as e:
    bug := yes
    assert "estourou" in e.message
assert bug

out "exercicio 269 ok"`, lang: 'df', title: `exercicios/50-dominio/269_o_valor_recusa.df` },
  {"p": "Um `record` já dá imutabilidade e igualdade estrutural, e essas duas metades são a maior parte. O que ele **não** dá é a regra: `Dinheiro(-5, \"BRL\")` é um record perfeitamente válido, e o negócio descobre isso três camadas adiante, num extrato negativo."},
  {"h3": "A criação é o único ponto que impede"},
  {"p": "Depois de existir, o valor circula. A regra vale ali, ou não vale em lugar nenhum."},
  {"h3": "E ela vale em toda fronteira"},
  {"p": "Inclusive no `com`. Um refinamento que só valesse na criação seria uma sugestão, e não um tipo."},
  {"h3": "Um valor não muda"},
  {"p": "Dois valores iguais são o **mesmo** valor; mudar um deles mudaria o outro para quem os comparou. A saída é criar outro."},
  {"h3": "E ele nasce completo"},
  {"p": "Um campo vazio faria dois valores \"iguais\" diferirem no que ninguém preencheu."},
  {"h3": "A regra que estoura é um bug DELA"},
  {"p": "Dizer \"valor inválido\" quando a condição quebrou esconderia o defeito real — e mandaria a pessoa procurar no lugar errado. As duas coisas exigem correções em arquivos diferentes."},
  {"p": "---"},
  {"p": "Tudo isso levanta `ValueObjectError`, que desce de `DomainError`: `handle DomainError` pega a família, e quem precisa distinguir nomeia o específico."},
  {"h2": "270 · o agregado e a unica porta de escrita"},
  {"p": "**Enunciado.** se qualquer um escreve, a invariante nao vale nada —"},
  { code: `// nao ha onde cobra-la. E ela e conferida na SAIDA de cada comando:
// cobrar na entrada deixaria o objeto quebrado quando o comando falha
// no meio.

adopt Arcane.Dominio as D

pedido := D.agregado("Pedido", "PED-1", total := 0, itens := 0)

pedido.invariante("o total nunca e negativo",
    lambda p => p.ler("total", 0) bigger_eq 0)
pedido.invariante("no maximo 3 itens",
    lambda p => p.ler("itens", 0) smaller_eq 3)

mark @pedido.comando("acrescentar")
action acrescentar(p, preco):
    p.mudar(total := p.ler("total", 0) + preco,
        itens := p.ler("itens", 0) + 1)

mark @pedido.comando("descontar")
action descontar(p, quanto):
    p.mudar(total := p.ler("total", 0) - quanto)

out "== 1. escrever por fora e recusado =="

por_fora := no
monitor:
    pedido.mudar(total := 999999)
handle AggregateError as e:
    por_fora := yes
    assert "comando" in e.message
assert por_fora
assert pedido.ler("total") is 0

out ""
out "== 2. o comando muda, e a versao avanca =="

assert pedido.versao() is 0
pedido.acrescentar(30)
pedido.acrescentar(20)
assert pedido.ler("total") is 50
assert pedido.versao() is 2
out $"   dois comandos -> total {pedido.ler('total')}, versao {pedido.versao()}"

out ""
out "== 3. a invariante e cobrada na SAIDA =="

violou := no
monitor:
    pedido.descontar(999)
handle AggregateError as e:
    violou := yes
    assert "negativo" in e.message
assert violou

out ""
out "== 4. e o comando recusado e DESFEITO por inteiro =="

// Sem isso, metade da mudanca fica aplicada, e a proxima leitura ve um
// agregado que nunca deveria existir.
assert pedido.ler("total") is 50
assert pedido.versao() is 2
out "   o estado voltou, e a versao nao avancou"

out ""
out "== 5. a outra invariante tambem vale =="

pedido.acrescentar(1)
estourou := no
monitor:
    pedido.acrescentar(1)  // seria o quarto item
handle AggregateError as e:
    estourou := yes
    assert "3 itens" in e.message
assert estourou
assert pedido.ler("itens") is 3

out "exercicio 270 ok"`, lang: 'df', title: `exercicios/50-dominio/270_agregado_porta_unica.df` },
  {"p": "Se qualquer um escreve, a invariante não vale nada — não há onde cobrá-la. O agregado existe para que exista esse lugar."},
  {"h3": "Escrever por fora é recusado"},
  {"p": "`pedido.mudar(total := 999999)` levanta. Não é burocracia: é a condição para as duas linhas seguintes significarem algo."},
  {"h3": "A invariante é cobrada na SAÍDA"},
  {"p": "Cobrar na entrada deixa o objeto quebrado quando o comando falha no meio. Cobrar na saída garante que ninguém observa um estado inválido."},
  {"h3": "E o comando recusado é desfeito"},
  {"p": "Estado, eventos e versão voltam ao que eram. Sem isso, metade da mudança fica aplicada e a próxima leitura vê um agregado que nunca deveria existir."},
  {"h3": "A versão conta os comandos"},
  {"p": "Ela não avança num comando desfeito — e é ela que serve a uma trava otimista: quem grava comparando a versão que leu descobre que outro passou na frente."},
  {"p": "---"},
  {"p": "A distinção que vale lembrar: a invariante de um `blueprint` **acusa** e não desfaz; o agregado **acusa e desfaz**."},
  {"h2": "271 · o fato espera a confirmacao"},
  {"p": "**Enunciado.** publicar um evento na hora faz o mundo reagir a um fato"},
  { code: `// que a transacao ainda pode desfazer — o e-mail sai, e o pedido nao
// existe. E um evento e imutavel: mudar um fato passado e reescrever a
// historia para quem ja reagiu a ele.

adopt Arcane.Dominio as D

out "== 1. o evento nao muda =="

fato := D.evento("PedidoPago", {"valor": 120})
assert fato.nome is "PedidoPago"
assert fato.dados["valor"] is 120

imutavel := no
monitor:
    fato.dados := {}
handle EventError as e:
    imutavel := yes
    assert "aconteceu" in e.message
assert imutavel

// E ele precisa de nome.
sem_nome := no
monitor:
    D.evento("")
handle EventError:
    sem_nome := yes
assert sem_nome

out ""
out "== 2. o evento fica guardado ate a confirmacao =="

publicados := []

action anotar(e):
    publicados.append(e.nome)

pedido := D.agregado("Pedido", "PED-1", total := 0)

mark @pedido.comando("pagar")
action pagar(p, valor):
    p.mudar(total := valor)
    p.aconteceu("PedidoPago", {"valor": valor})

pedido.pagar(120)
assert len(pedido.eventos()) is 1
assert len(publicados) is 0

u := D.unidade(publicar := anotar)
u.registrar(pedido)
assert len(publicados) is 0
out "   registrado, e o mundo ainda nao sabe"

saindo := u.confirmar()
assert len(saindo) is 1
assert publicados is ["PedidoPago"]
out $"   confirmado -> {publicados}"

out ""
out "== 3. a unidade desfeita nao publica nada =="

outro := D.agregado("Pedido", "PED-2", total := 0)
outro.comando("marcar", lambda p => p.aconteceu("PedidoCriado"))
outro.marcar()

descartada := D.unidade(publicar := anotar)
descartada.registrar(outro)
descartada.desfazer()

assert publicados is ["PedidoPago"]
assert len(outro.eventos()) is 0
out "   os eventos foram descartados junto"

out ""
out "== 4. nao da para desfazer o confirmado =="

// Os eventos ja sairam, e quem reagiu nao tem como voltar atras.
tarde := no
monitor:
    u.desfazer()
handle UnitOfWorkError as e:
    tarde := yes
    assert "compensacao" in e.dica
assert tarde

out "exercicio 271 ok"`, lang: 'df', title: `exercicios/50-dominio/271_evento_e_unidade.df` },
  {"p": "Publicar um evento na hora faz o mundo reagir a um fato que a transação ainda pode desfazer: o e-mail sai, e o pedido não existe."},
  {"h3": "O evento não muda"},
  {"p": "Ele já aconteceu. Mudá-lo é reescrever a história — quem já reagiu a ele reagiu ao que estava escrito antes. E o nome no passado não é estilo: um evento chamado `CriarPedido` é um comando disfarçado, e quem o recebe acha que pode recusá-lo."},
  {"h3": "Ele fica guardado até a confirmação"},
  {"p": "O agregado anota; a unidade publica. Entre os dois há a janela em que a transação pode ser desfeita."},
  {"h3": "A unidade desfeita não publica nada"},
  {"p": "E descarta os eventos junto: eles nunca aconteceram."},
  {"h3": "E não dá para desfazer o confirmado"},
  {"p": "Os eventos já saíram, e quem reagiu não tem como voltar atrás. A saída é a **compensação** — a mesma que a `Saga` do `Arcane.Malha` implementa quando a transação atravessa a rede."},
  {"h2": "272 · a regra de negocio que se combina e se explica"},
  {"p": "**Enunciado.** um 'given' dentro do servico nao pode ser combinado, nem"},
  { code: `// reaproveitado na consulta que lista "quem pode", nem explicado ao
// usuario. Os tres usos sao a MESMA regra, e escreve-la tres vezes e
// como as tres divergem.

adopt Arcane.Dominio as D

record Cliente:
    nome: String
    idade: Integer
    pais: String

steady maior := D.regra("maior de idade", lambda c => c.idade bigger_eq 18)
steady brasil := D.regra("mora no Brasil", lambda c => c.pais is "BR")
steady pode := maior.e(brasil)

steady TODOS := [
    Cliente("Ana", 30, "BR"),
    Cliente("Bia", 15, "BR"),
    Cliente("Caio", 40, "US"),
    Cliente("Dora", 22, "BR")
]

out "== 1. a decisao =="

assert pode.vale(TODOS[0])
assert not pode.vale(TODOS[1])
assert not pode.vale(TODOS[2])

out ""
out "== 2. a explicacao aponta a PARTE que falhou =="

// A frase inteira nao diz o que a pessoa precisa resolver.
assert pode.por_que_nao(TODOS[1]) is "maior de idade"
assert pode.por_que_nao(TODOS[2]) is "mora no Brasil"
assert pode.por_que_nao(TODOS[0]) is ""
out $"   Bia: {pode.por_que_nao(TODOS[1])}"
out $"   Caio: {pode.por_que_nao(TODOS[2])}"

out ""
out "== 3. a MESMA regra, como consulta =="

habilitados := pode.filtrar(TODOS)
assert len(habilitados) is 2
assert [c.nome cycle c in habilitados] is ["Ana", "Dora"]

out ""
out "== 4. ou, e nao =="

steady qualquer := maior.ou(brasil)
assert qualquer.vale(TODOS[1])  // brasileira, menor
assert qualquer.vale(TODOS[2])  // maior, americano

steady menor := maior.nao()
assert menor.vale(TODOS[1])
assert not menor.vale(TODOS[0])
assert "NAO" in menor.descricao

out ""
out "== 5. uma regra quebrada LEVANTA =="

// Devolver 'nao vale' recusaria o usuario por um bug, calado.
steady ruim := D.regra("ruim", lambda c => c.idadee)
bug := no
monitor:
    ruim.vale(TODOS[0])
handle SpecificationError as e:
    bug := yes
    assert "estourou" in e.message
assert bug

out "exercicio 272 ok"`, lang: 'df', title: `exercicios/50-dominio/272_regra_como_objeto.df` },
  {"p": "Um `given` dentro do serviço não pode ser combinado, nem reaproveitado na consulta que lista \"quem pode\", nem explicado ao usuário. Os três usos são a **mesma** regra, e escrevê-la três vezes é como as três divergem."},
  {"h3": "A decisão"},
  {"p": "`pode.vale(cliente)` responde sim ou não. É o uso óbvio, e o único que um `given` cobre."},
  {"h3": "A explicação aponta a PARTE que falhou"},
  {"p": "*\"maior de idade E mora no Brasil\"* não diz qual das duas a pessoa precisa resolver — e essa frase é o que vai para a tela."},
  {"h3": "E a mesma regra filtra uma lista"},
  {"p": "`pode.filtrar(todos)` é a consulta. Sem o objeto, ela seria um segundo `given` numa compreensão — e os dois divergiriam na primeira mudança."},
  {"h3": "Uma regra quebrada LEVANTA"},
  {"p": "Devolver \"não vale\" recusaria o usuário por um bug, calado."},
  {"h2": "273 · o repositorio guarda AGREGADOS INTEIROS"},
  {"p": "**Enunciado.** um repositorio que devolve meio agregado devolve um"},
  { code: `// objeto cujas invariantes ninguem pode garantir. E o que vai para
// dentro dele precisa de IDENTIDADE — um objeto de valor nao tem, e
// nao tem porque dois iguais sao o mesmo.

adopt Arcane.Dominio as D

steady pedidos := D.repositorio("Pedido")

action um_pedido(id, total, itens):
    yield D.agregado("Pedido", id, total := total, itens := itens)

pedidos.guardar(um_pedido("PED-1", 40, 1))
pedidos.guardar(um_pedido("PED-2", 250, 4))
pedidos.guardar(um_pedido("PED-3", 900, 5))

out "== 1. guardar e recuperar =="

assert pedidos.quantos() is 3
achado := pedidos.por_id("PED-2")
assert achado.ler("total") is 250

out ""
out "== 2. as duas perguntas existem =="

// 'por_id' devolve void; 'exigir' levanta. Uma so obrigaria metade das
// chamadas a tratar um void que nunca acontece.
assert pedidos.por_id("PED-404") is void

levantou := no
monitor:
    pedidos.exigir("PED-404")
handle RepositoryError as e:
    levantou := yes
    assert "PED-404" in e.message
assert levantou

out ""
out "== 3. consultar com a MESMA regra da decisao =="

steady grande := D.regra("passa de 200", lambda p => p.ler("total", 0) bigger 200)
grandes := pedidos.que(grande)
assert len(grandes) is 2

out ""
out "== 4. apagar e idempotente na resposta =="

assert pedidos.apagar("PED-1") is yes
assert pedidos.apagar("PED-1") is no
assert pedidos.quantos() is 2

out ""
out "== 5. um objeto de VALOR nao entra =="

steady Dinheiro := D.valor("Dinheiro", ["quantia"])
sem_id := no
monitor:
    D.repositorio("Dinheiro").guardar(Dinheiro(10))
handle IdentityError as e:
    sem_id := yes
    assert "identidade" in e.message
assert sem_id
out "   se voce precisa distinguir duas instancias iguais, e uma entidade"

out "exercicio 273 ok"`, lang: 'df', title: `exercicios/50-dominio/273_repositorio.df` },
  {"p": "Um repositório que devolve meio agregado devolve um objeto cujas invariantes ninguém pode garantir. Por isso ele não tem `atualizar_campo` nem consulta por coluna."},
  {"h3": "As duas perguntas existem"},
  {"p": "`por_id` devolve `void`; `exigir` levanta. Uma só obrigaria metade das chamadas a tratar um `void` que nunca acontece."},
  {"h3": "A consulta usa a MESMA regra da decisão"},
  {"p": "`pedidos.que(grande)` — e não um segundo filtro escrito à mão."},
  {"h3": "E um objeto de VALOR não entra"},
  {"p": "Ele não tem identidade, e não tem porque dois iguais são o mesmo. Se a sua peça precisa distinguir duas instâncias iguais, ela é uma **entidade** — e o módulo diz isso em vez de deixar passar."},
  {"h2": "274 · a fronteira entre dois modelos"},
  {"p": "**Enunciado.** o \"Cliente\" de Vendas tem limite de credito; o de Suporte"},
  { code: `// tem plano e chamados abertos. Sao o mesmo NOME e nao sao o mesmo
// conceito. Passar o objeto inteiro de um lado ao outro e o que faz
// dois modelos virarem um so — e o unico nao serve a ninguem.

adopt Arcane.Dominio as D

steady vendas := D.contexto("Vendas")
steady suporte := D.contexto("Suporte")

out "== 1. sem traducao, nao atravessa =="

steady DE_VENDAS := {"nome": "Ana", "credito": 5000, "ultima_compra": "2026-09"}

recusou := no
monitor:
    suporte.receber("Vendas", "Cliente", DE_VENDAS)
handle BoundedContextError as e:
    recusou := yes
    assert "traduzir" in e.message
assert recusou

out ""
out "== 2. a traducao deixa so o que ESTE lado usa =="

suporte.traduzir_de("Vendas", "Cliente",
    lambda c => {"nome": c["nome"], "plano": "basico", "chamados": 0})

aqui := suporte.receber("Vendas", "Cliente", DE_VENDAS)
assert aqui["nome"] is "Ana"
assert aqui["plano"] is "basico"
assert "credito" not in aqui
assert "ultima_compra" not in aqui
out $"   {aqui}"

out ""
out "== 3. quem escuta REAGE, e nao decide =="

atendidos := []

mark @suporte.ao_acontecer("PedidoPago")
action abrir_acompanhamento(e):
    atendidos.append(e.dados["pedido"])

suporte.publicar(D.evento("PedidoPago", {"pedido": "PED-7"}))
assert atendidos is ["PED-7"]

// Um evento que ninguem escuta nao e erro.
falhas := suporte.publicar(D.evento("PedidoCancelado", {"pedido": "PED-8"}))
assert len(falhas) is 0
assert atendidos is ["PED-7"]

out ""
out "== 4. um ouvinte que estoura nao impede os outros =="

vistos := []

mark @vendas.ao_acontecer("PedidoPago")
action quebrado(_e):
    trigger "este ouvinte esta com defeito"

mark @vendas.ao_acontecer("PedidoPago")
action tambem(e):
    vistos.append(e.dados["pedido"])

falhas := vendas.publicar(D.evento("PedidoPago", {"pedido": "PED-9"}))
assert len(falhas) is 1
assert vistos is ["PED-9"]
out $"   um falhou, o outro rodou: {vistos}"

out ""
out "== 5. o repositorio do contexto e o mesmo entre chamadas =="

assert vendas.repositorio("Pedido") is vendas.repositorio("Pedido")
assert vendas.repositorios() is ["Pedido"]

out "exercicio 274 ok"`, lang: 'df', title: `exercicios/50-dominio/274_contexto_delimitado.df` },
  {"p": "O \"Cliente\" de Vendas tem limite de crédito; o de Suporte tem plano e chamados abertos. São o mesmo **nome** e não são o mesmo conceito."},
  {"h3": "Sem tradução, não atravessa"},
  {"p": "É a *camada anticorrupção*: sem ela, o modelo de fora entra inteiro, e o de dentro passa a ter campos que só existem porque o outro time os tem."},
  {"h3": "Quem escuta REAGE, e não decide"},
  {"p": "O evento já aconteceu. Um ouvinte que pudesse recusá-lo seria um comando com outro nome."},
  {"h3": "E um ouvinte que estoura não impede os outros"},
  {"p": "Derrubar os demais por causa de um deixaria o mundo parcialmente atualizado sem ninguém saber. As falhas voltam como **dado**, para quem quiser agir sobre elas."},
  {"h2": "275 · a invariante quebrada e um bug DELA"},
  {"p": "**Enunciado.** uma invariante que estoura ao ser avaliada nao quer dizer"},
  { code: `// que o estado e invalido. Dizer "violou" ali mandaria a pessoa
// procurar no agregado, e o defeito esta na condicao. As duas coisas
// exigem correcoes em lugares diferentes.

adopt Arcane.Dominio as D

out "== 1. a invariante com erro de digitacao =="

conta := D.agregado("Conta", "C-1", saldo := 100)
conta.invariante("o saldo nao fica negativo",
    lambda c => c.lerr("saldo", 0) bigger_eq 0)  // 'lerr' nao existe

conta.comando("sacar", lambda c, v => c.mudar(saldo := c.ler("saldo", 0) - v))

bug := no
monitor:
    conta.sacar(10)
handle AggregateError as e:
    bug := yes
    assert "estourou" in e.message
    assert "o saldo nao fica negativo" in e.message
    out $"   {e.message}"
assert bug

// E o estado voltou: o comando foi desfeito.
assert conta.ler("saldo") is 100

out ""
out "== 2. com a invariante certa, a mesma conta funciona =="

boa := D.agregado("Conta", "C-2", saldo := 100)
boa.invariante("o saldo nao fica negativo",
    lambda c => c.ler("saldo", 0) bigger_eq 0)
boa.comando("sacar", lambda c, v => c.mudar(saldo := c.ler("saldo", 0) - v))

boa.sacar(30)
assert boa.ler("saldo") is 70

estourou := no
monitor:
    boa.sacar(999)
handle AggregateError as e:
    estourou := yes
    assert "violou" in e.message
    assert "estourou" not in e.message
assert estourou
assert boa.ler("saldo") is 70

out ""
out "== 3. a diferenca esta na MENSAGEM, e e ela que orienta =="

// 'estourou' manda olhar a condicao; 'violou' manda olhar o comando.
out "   estourou -> o bug esta na condicao"
out "   violou   -> o bug esta no comando"

out ""
out "== 4. conferir() cobra na hora =="

assert boa.conferir()

// Uma invariante sem condicao e recusada na declaracao.
sem := no
monitor:
    boa.invariante("sem condicao", void)
handle AggregateError:
    sem := yes
assert sem

out "exercicio 275 ok"`, lang: 'df', title: `exercicios/50-dominio/275_invariante_que_estoura.df` },
  {"p": "Uma condição que estoura ao ser avaliada não quer dizer que o estado é inválido. Dizer \"violou\" ali mandaria a pessoa procurar no agregado, e o defeito está na condição."},
  {"h3": "As duas mensagens orientam lugares diferentes"},
  {"p": "`estourou` manda olhar a condição; `violou` manda olhar o comando. São correções em arquivos diferentes, e uma mensagem que junta as duas custa a tarde de quem lê."},
  {"h3": "E o estado volta nos dois casos"},
  {"p": "O comando é desfeito por inteiro, tenha ele falhado pela condição ou por um erro dentro dela."},
  {"h2": "276 · o comando que falha no meio nao deixa metade"},
  {"p": "**Enunciado.** um comando que muda tres campos e falha no terceiro"},
  { code: `// deixaria os dois primeiros aplicados. A proxima leitura veria um
// agregado que nunca deveria existir — e nada denunciaria.

adopt Arcane.Dominio as D

estoque := D.agregado("Estoque", "E-1",
    disponivel := 10, reservado := 0, vendido := 0)

estoque.invariante("nada fica negativo",
    lambda e => e.ler("disponivel", 0) bigger_eq 0)

mark @estoque.comando("reservar")
action reservar(e, quantos):
    e.mudar(disponivel := e.ler("disponivel", 0) - quantos)
    e.mudar(reservado := e.ler("reservado", 0) + quantos)
    e.aconteceu("Reservado", {"quantos": quantos})

mark @estoque.comando("quebrar_no_meio")
action quebrar_no_meio(e):
    e.mudar(disponivel := 0)
    e.mudar(reservado := 999)
    e.aconteceu("NuncaAconteceu")
    trigger "falhei depois de mexer em tudo"

out "== 1. o caminho feliz =="

estoque.reservar(3)
assert estoque.ler("disponivel") is 7
assert estoque.ler("reservado") is 3
assert len(estoque.eventos()) is 1
assert estoque.versao() is 1

out ""
out "== 2. o comando que estoura no fim desfaz TUDO =="

quebrou := no
monitor:
    estoque.quebrar_no_meio()
handle Error as e:
    quebrou := yes
    assert "falhei" in e.message
assert quebrou

assert estoque.ler("disponivel") is 7
assert estoque.ler("reservado") is 3
assert estoque.versao() is 1
out "   estado, versao e eventos voltaram ao que eram"

out ""
out "== 3. o EVENTO do comando desfeito tambem some =="

// Um fato de um comando que nao aconteceu e a pior classe de evento:
// alguem reage a ele, e nao ha nada para reagir.
assert len(estoque.eventos()) is 1
assert estoque.eventos()[0].nome is "Reservado"

out ""
out "== 4. e a invariante violada tem o mesmo efeito =="

violou := no
monitor:
    estoque.reservar(999)
handle AggregateError:
    violou := yes
assert violou
assert estoque.ler("disponivel") is 7
assert estoque.ler("reservado") is 3
assert len(estoque.eventos()) is 1

out "exercicio 276 ok"`, lang: 'df', title: `exercicios/50-dominio/276_comando_desfaz.df` },
  {"p": "Um comando que muda três campos e falha no terceiro deixaria os dois primeiros aplicados. A próxima leitura veria um agregado que nunca deveria existir — e nada denunciaria."},
  {"h3": "Estado, versão e eventos voltam"},
  {"p": "Os três juntos. Deixar a versão avançar faria uma trava otimista recusar uma gravação legítima."},
  {"h3": "O evento do comando desfeito também some"},
  {"p": "Um fato de um comando que não aconteceu é a pior classe de evento: alguém reage a ele, e não há nada para reagir."},
  {"h3": "E a invariante violada tem o mesmo efeito"},
  {"p": "Não há dois caminhos de desfazer — há um."},
  {"h2": "277 · a unidade confere TODOS antes de gravar QUALQUER"},
  {"p": "**Enunciado.** se a segunda gravacao falhasse por invariante, a primeira"},
  { code: `// ja estaria no banco — e a transacao de dominio teria vazado pela
// metade. A ordem das duas fases e o recurso.

adopt Arcane.Dominio as D

steady repo := D.repositorio("Conta")

action conta(id, saldo, minimo):
    c := D.agregado("Conta", id, saldo := saldo)
    c.invariante($"o saldo nao cai abaixo de {minimo}",
        lambda a => a.ler("saldo", 0) bigger_eq minimo)
    c.comando("mover", lambda a, v => a.mudar(saldo := a.ler("saldo", 0) + v))
    yield c

out "== 1. as duas pontas de uma transferencia =="

origem := conta("A", 100, 0)
destino := conta("B", 50, 0)

origem.mover(-30)
destino.mover(30)

u := D.unidade()
u.registrar(origem, repo)
u.registrar(destino, repo)
assert repo.quantos() is 0
u.confirmar()
assert repo.quantos() is 2
assert repo.exigir("A").ler("saldo") is 70
assert repo.exigir("B").ler("saldo") is 50 + 30

out ""
out "== 2. se um viola, NENHUM e gravado =="

steady repo2 := D.repositorio("Conta")
boa := conta("C", 100, 0)
ruim := conta("D", 10, 100)  // ja nasce violando o minimo

u2 := D.unidade()
u2.registrar(boa, repo2)
u2.registrar(ruim, repo2)

falhou := no
monitor:
    u2.confirmar()
handle AggregateError as e:
    falhou := yes
    assert "100" in e.message
assert falhou
assert repo2.quantos() is 0
out "   a primeira NAO foi gravada"

out ""
out "== 3. a unidade que terminou nao recebe mais =="

fechada := no
monitor:
    u.registrar(conta("E", 1, 0))
handle UnitOfWorkError as e:
    fechada := yes
    assert "D.unidade()" in e.dica
assert fechada

duas_vezes := no
monitor:
    u.confirmar()
handle UnitOfWorkError:
    duas_vezes := yes
assert duas_vezes

out ""
out "== 4. eventos_pendentes mostra sem publicar =="

pend := conta("F", 100, 0)
pend.comando("marcar", lambda a => a.aconteceu("Marcado"))
pend.marcar()

u3 := D.unidade()
u3.registrar(pend)
assert [e.nome cycle e in u3.eventos_pendentes()] is ["Marcado"]
assert len(pend.eventos()) is 1  // continuam com o agregado

out "exercicio 277 ok"`, lang: 'df', title: `exercicios/50-dominio/277_unidade_tudo_ou_nada.df` },
  {"p": "Se a segunda gravação falhasse por invariante, a primeira já estaria no banco — e a transação de domínio teria vazado pela metade. A ordem das duas fases é o recurso."},
  {"h3": "As duas pontas de uma transferência"},
  {"p": "Origem e destino confirmam juntas, ou nenhuma das duas."},
  {"h3": "A unidade que terminou não recebe mais"},
  {"p": "Nem registra, nem confirma de novo. Um objeto que aceita operações depois de terminado é um objeto sem estado."},
  {"h3": "E `eventos_pendentes` mostra sem publicar"},
  {"p": "Para quem quer conferir antes de confirmar — e sem tirar os eventos do agregado."},
  {"h2": "278 · a identidade nasce com o objeto"},
  {"p": "**Enunciado.** um id que o banco gera obriga a salvar antes de ter"},
  { code: `// identidade, e no intervalo entre criar e confirmar o objeto existe
// sem ser ele mesmo. Aqui ele nasce com um.

adopt Arcane.Dominio as D

out "== 1. um id novo nao repete =="

vistos := {}
cycle i from 1 to 500:
    vistos[D.novo_id()] := yes
assert len(vistos) is 500

out ""
out "== 2. o agregado nasce com identidade, mesmo sem dizer qual =="

anonimo := D.agregado("Pedido")
assert len(anonimo.id()) bigger 30  // um UUID em texto
assert anonimo.tipo() is "Pedido"

nomeado := D.agregado("Pedido", "PED-1")
assert nomeado.id() is "PED-1"

out ""
out "== 3. dois agregados do mesmo tipo e id sao o mesmo =="

assert D.agregado("Pedido", "X") is D.agregado("Pedido", "X")
assert D.agregado("Pedido", "X") isnt D.agregado("Pedido", "Y")
assert D.agregado("Pedido", "X") isnt D.agregado("Conta", "X")

out ""
out "== 4. a versao conta os comandos, e serve a trava otimista =="

conta := D.agregado("Conta", "C-1", saldo := 0)
conta.comando("somar", lambda c, v => c.mudar(saldo := c.ler("saldo", 0) + v))

assert conta.versao() is 0
cycle i from 1 to 5:
    conta.somar(10)
assert conta.versao() is 5
assert conta.ler("saldo") is 50

// Dois usuarios editando o mesmo agregado: quem gravar com a versao
// que leu descobre que o outro passou na frente.
lida := conta.versao()
conta.somar(1)
assert conta.versao() isnt lida
out $"   li a versao {lida}, e agora ela e {conta.versao()}"

out ""
out "== 5. o estado e uma COPIA =="

foto := conta.estado()
conta.somar(100)
assert foto["saldo"] is 51
assert conta.ler("saldo") is 151
out "   a foto nao acompanha o agregado"

out "exercicio 278 ok"`, lang: 'df', title: `exercicios/50-dominio/278_agregado_e_id.df` },
  {"p": "Um id que o banco gera obriga a salvar antes de ter identidade, e no intervalo entre criar e confirmar o objeto existe sem ser ele mesmo."},
  {"h3": "O id é texto, e nasce com o agregado"},
  {"p": "`D.novo_id()` é um UUID4. Quem quiser o seu passa na criação."},
  {"h3": "A versão conta os comandos"},
  {"p": "E é ela que serve a uma trava otimista: quem grava comparando a versão que leu descobre que outro passou na frente."},
  {"h3": "E `estado()` é uma cópia"},
  {"p": "A foto não acompanha o agregado. Devolver o dicionário vivo abriria uma porta de escrita ao lado do comando — que é exatamente o que o agregado existe para fechar."},
  {"h2": "279 · regras que se combinam em arvore"},
  {"p": "**Enunciado.** 'e', 'ou' e 'nao' devolvem regras, e uma regra composta"},
  { code: `// se combina de novo. E o que permite montar a politica em pedacos
// nomeados, em vez de um 'given' de cinco linhas.

adopt Arcane.Dominio as D

record Pedido:
    total: Float
    itens: Integer
    pais: String
    primeiro: Boolean

steady grande := D.regra("passa de R$ 200", lambda p => p.total bigger 200.0)
steady cheio := D.regra("tem 3 itens ou mais", lambda p => p.itens bigger_eq 3)
steady nacional := D.regra("e do Brasil", lambda p => p.pais is "BR")
steady estreante := D.regra("e a primeira compra", lambda p => p.primeiro)

// Frete gratis: (grande E cheio) OU estreante — e sempre nacional.
steady frete_gratis := grande.e(cheio).ou(estreante).e(nacional)

out "== 1. a arvore inteira =="

out $"   {frete_gratis.descricao}"
assert "OU" in frete_gratis.descricao
assert "E" in frete_gratis.descricao

out ""
out "== 2. os casos =="

assert frete_gratis.vale(Pedido(300.0, 4, "BR", no))  // grande e cheio
assert frete_gratis.vale(Pedido(10.0, 1, "BR", yes))  // estreante
assert not frete_gratis.vale(Pedido(300.0, 4, "US", no))  // fora do pais
assert not frete_gratis.vale(Pedido(300.0, 1, "BR", no))  // grande, so 1 item
assert not frete_gratis.vale(Pedido(10.0, 1, "BR", no))  // nada

out ""
out "== 3. o motivo, pelo caminho que falhou =="

// Num 'ou', nenhum dos dois basta: a explicacao diz isso.
so_pais := frete_gratis.por_que_nao(Pedido(300.0, 4, "US", no))
assert so_pais is "e do Brasil"

nem_um_nem_outro := frete_gratis.por_que_nao(Pedido(10.0, 1, "BR", no))
assert "nem" in nem_um_nem_outro
out $"   {nem_um_nem_outro}"

out ""
out "== 4. a mesma arvore filtra uma lista =="

steady CARRINHOS := [
    Pedido(300.0, 4, "BR", no),
    Pedido(10.0, 1, "BR", yes),
    Pedido(300.0, 4, "US", no),
    Pedido(50.0, 2, "BR", no)
]

com_frete := frete_gratis.filtrar(CARRINHOS)
assert len(com_frete) is 2

out ""
out "== 5. negar uma composta =="

steady paga_frete := frete_gratis.nao()
assert len(paga_frete.filtrar(CARRINHOS)) is 2
assert len(com_frete) + len(paga_frete.filtrar(CARRINHOS)) is len(CARRINHOS)

out "exercicio 279 ok"`, lang: 'df', title: `exercicios/50-dominio/279_regra_composta.df` },
  {"p": "`e`, `ou` e `nao` devolvem regras, e uma regra composta se combina de novo. É o que permite montar a política em pedaços **nomeados**, em vez de um `given` de cinco linhas."},
  {"h3": "A árvore inteira tem descrição"},
  {"p": "`(grande E cheio) OU estreante E nacional` — e a descrição sai da composição, e não de uma segunda string escrita à mão."},
  {"h3": "O motivo segue o caminho que falhou"},
  {"p": "Num `ou`, nenhum dos dois basta, e a explicação diz isso. Num `e`, ela aponta a parte."},
  {"h3": "E a mesma árvore filtra a lista"},
  {"p": "Os que passam e os que não passam somam o total: é a prova de que a negação é a complementar."},
  {"h2": "280 · o mesmo contrato sobre outro armazem"},
  {"p": "**Enunciado.** 'D.repositorio' guarda em memoria; 'D.repositorio_de'"},
  { code: `// recebe as acoes de ler e gravar. O contrato e o mesmo, e e ele que
// importa — quem chama nao sabe onde o dado mora.

adopt Arcane.Dominio as D

// O "banco": um vault, e as quatro acoes em cima dele.
banco := {}
gravacoes := {"n": 0}

action ler_do_banco(id):
    yield banco[id] ?? void

action gravar_no_banco(id, valor):
    gravacoes["n"] := gravacoes["n"] + 1
    banco[id] := valor

action apagar_do_banco(id):
    given id in banco:
        remove(banco, id)
        yield yes
    yield no

action listar_do_banco():
    yield [banco[k] cycle k in keys(banco)]

steady repo := D.repositorio_de("Pedido",
    ler := ler_do_banco,
    gravar := gravar_no_banco,
    apagar := apagar_do_banco,
    listar := listar_do_banco)

out "== 1. o mesmo contrato =="

repo.guardar(D.agregado("Pedido", "P-1", total := 10))
repo.guardar(D.agregado("Pedido", "P-2", total := 300))

assert repo.quantos() is 2
assert "P-1" in banco
assert gravacoes["n"] is 2
assert repo.exigir("P-2").ler("total") is 300

out ""
out "== 2. a ausencia responde igual =="

assert repo.por_id("P-404") is void

levantou := no
monitor:
    repo.exigir("P-404")
handle RepositoryError:
    levantou := yes
assert levantou

out ""
out "== 3. a consulta por regra tambem =="

steady grande := D.regra("grande", lambda p => p.ler("total", 0) bigger 100)
assert len(repo.que(grande)) is 1

out ""
out "== 4. apagar =="

assert repo.apagar("P-1") is yes
assert repo.apagar("P-1") is no
assert repo.quantos() is 1
assert len(keys(banco)) is 1

out ""
out "== 5. quem chama nao sabe onde o dado mora =="

action quantos_grandes(qualquer_repo, regra):
    yield len(qualquer_repo.que(regra))

steady memoria := D.repositorio("Pedido")
memoria.guardar(D.agregado("Pedido", "M-1", total := 500))

// A mesma acao, sobre os dois.
assert quantos_grandes(repo, grande) is 1
assert quantos_grandes(memoria, grande) is 1

out "exercicio 280 ok"`, lang: 'df', title: `exercicios/50-dominio/280_repositorio_de_fora.df` },
  {"p": "`D.repositorio` guarda em memória; `D.repositorio_de` recebe as ações de ler e gravar. O contrato é o mesmo, e é ele que importa."},
  {"h3": "Quem chama não sabe onde o dado mora"},
  {"p": "A mesma ação recebe os dois e responde igual. É o teste de que a abstração vale alguma coisa."},
  {"h3": "E a ausência responde igual"},
  {"p": "`por_id` devolve `void` e `exigir` levanta nos dois — senão trocar o armazém mudaria o comportamento do código que o usa."},
  {"h2": "281 · um caso de uso inteiro"},
  {"p": "**Enunciado.** juntar as sete pecas num fluxo so — reservar estoque e"},
  { code: `// cobrar, com as duas pontas numa unidade de trabalho, e o faturamento
// reagindo ao evento depois da confirmacao.

adopt Arcane.Dominio as D

steady Dinheiro := D.valor("Dinheiro", ["centavos", "moeda"],
    regra := lambda v => v["centavos"] bigger_eq 0,
    motivo := "dinheiro nao e negativo")

steady estoques := D.repositorio("Estoque")
steady pedidos := D.repositorio("Pedido")
steady vendas := D.contexto("Vendas")

// ── o estoque ──
action novo_estoque(sku, quantos):
    e := D.agregado("Estoque", sku, disponivel := quantos, reservado := 0)
    e.invariante("o disponivel nao fica negativo",
        lambda a => a.ler("disponivel", 0) bigger_eq 0)
    e.comando("reservar", lambda a, n => a.mudar(
            disponivel := a.ler("disponivel", 0) - n,
            reservado := a.ler("reservado", 0) + n))
    yield e

// ── o pedido ──
action novo_pedido(id):
    p := D.agregado("Pedido", id, centavos := 0, itens := 0, pago := no)
    p.invariante("o total nunca e negativo",
        lambda a => a.ler("centavos", 0) bigger_eq 0)
    p.comando("acrescentar", lambda a, preco => a.mudar(
            centavos := a.ler("centavos", 0) + preco.centavos,
            itens := a.ler("itens", 0) + 1))
    p.comando("pagar", pagar_pedido)
    yield p

action pagar_pedido(p):
    given p.ler("pago", no):
        trigger "este pedido ja foi pago"
    p.mudar(pago := yes)
    p.aconteceu("PedidoPago", {"pedido": p.id(),
            "centavos": p.ler("centavos", 0)})

// ── quem reage ──
faturas := []

mark @vendas.ao_acontecer("PedidoPago")
action faturar(fato):
    faturas.append({"pedido": fato.dados["pedido"],
            "centavos": fato.dados["centavos"]})

out "== 1. montar o pedido =="

estoque := novo_estoque("CAFE-500", 10)
pedido := novo_pedido("PED-1")

pedido.acrescentar(Dinheiro(3250, "BRL"))
pedido.acrescentar(Dinheiro(900, "BRL"))
estoque.reservar(2)

assert pedido.ler("centavos") is 4150
assert pedido.ler("itens") is 2
assert estoque.ler("disponivel") is 8

out ""
out "== 2. pagar, e confirmar as duas pontas juntas =="

pedido.pagar()
assert len(faturas) is 0  // o evento ainda esta guardado

u := D.unidade(publicar := vendas.publicar)
u.registrar(pedido, pedidos)
u.registrar(estoque, estoques)
u.confirmar()

assert len(faturas) is 1
assert faturas[0]["centavos"] is 4150
assert pedidos.quantos() is 1
assert estoques.quantos() is 1
out $"   faturado: {faturas[0]}"

out ""
out "== 3. pagar duas vezes e recusado =="

de_novo := no
monitor:
    pedido.pagar()
handle Error as e:
    de_novo := yes
    assert "ja foi pago" in e.message
assert de_novo
assert len(faturas) is 1

out ""
out "== 4. o estoque nao fica negativo =="

sem := no
monitor:
    estoque.reservar(999)
handle AggregateError:
    sem := yes
assert sem
assert estoque.ler("disponivel") is 8

out ""
out "== 5. a consulta usa a regra da decisao =="

steady pagos := D.regra("esta pago", lambda p => p.ler("pago", no))
assert len(pedidos.que(pagos)) is 1

out "exercicio 281 ok"`, lang: 'df', title: `exercicios/50-dominio/281_ddd_ponta_a_ponta.df` },
  {"p": "As sete peças num fluxo só: reservar estoque e cobrar, com as duas pontas numa unidade de trabalho, e o faturamento reagindo ao evento **depois** da confirmação."},
  {"h3": "O evento espera"},
  {"p": "Entre `pedido.pagar()` e `u.confirmar()` o faturamento não rodou. É a janela em que a transação ainda podia ser desfeita."},
  {"h3": "Pagar duas vezes é recusado"},
  {"p": "E a recusa mora no comando, que é onde a regra pode ser cobrada."},
  {"h3": "E a consulta usa a regra da decisão"},
  {"p": "`pedidos.que(pagos)` — a mesma regra que decide é a que lista."},
  {"h2": "282 · a familia de erros do dominio"},
  {"p": "**Enunciado.** levantar 'RuntimeError' em tudo faria a distincao morrer"},
  { code: `// na fronteira — para quem escreve o 'handle', violar uma invariante e
// dividir por zero viram a mesma coisa. Cada peca levanta a sua, e a
// base pega todas.

adopt Arcane.Dominio as D

steady Dinheiro := D.valor("Dinheiro", ["q"], regra := lambda v => v["q"] bigger 0)

action classe_do_erro(acao):
    monitor:
        acao()
    handle Error as e:
        yield e.type
    yield "nenhum"

out "== 1. cada peca levanta a SUA =="

assert classe_do_erro(lambda => Dinheiro(-1)) is "ValueObjectError"
assert classe_do_erro(lambda => D.repositorio("X").exigir("nao-existe")) is "RepositoryError"
assert classe_do_erro(lambda => D.evento("")) is "EventError"
assert classe_do_erro(lambda => D.contexto("A").receber("B", "C", {})) is "BoundedContextError"
assert classe_do_erro(lambda => D.repositorio("X").guardar(Dinheiro(1))) is "IdentityError"

p := D.agregado("Pedido", "P", total := 0)
assert classe_do_erro(lambda => p.mudar(total := 1)) is "AggregateError"

u := D.unidade()
u.confirmar()
assert classe_do_erro(lambda => u.confirmar()) is "UnitOfWorkError"

out "   sete pecas, sete classes"

out ""
out "== 2. a base pega todas =="

action pela_base(acao):
    monitor:
        acao()
    handle DomainError:
        yield yes
    yield no

assert pela_base(lambda => Dinheiro(-1))
assert pela_base(lambda => D.evento(""))
assert pela_base(lambda => p.mudar(total := 1))
assert pela_base(lambda => u.confirmar())

out ""
out "== 3. e ela NAO pega um erro de fora =="

// Senao 'handle DomainError' viraria um 'handle' sem tipo.
nao_pegou := no
monitor:
    monitor:
        _x := 1 / 0  // df: permitir division-by-zero
    handle DomainError:
        assert no
handle DivisionByZeroError:
    nao_pegou := yes
assert nao_pegou

out ""
out "== 4. o especifico continua distinguivel =="

so_valor := no
monitor:
    Dinheiro(-1)
handle RepositoryError:
    assert no
handle ValueObjectError:
    so_valor := yes
assert so_valor

out "exercicio 282 ok"`, lang: 'df', title: `exercicios/50-dominio/282_dominio_erros.df` },
  {"p": "Levantar `RuntimeError` em tudo faria a distinção morrer na fronteira: para quem escreve o `handle`, violar uma invariante e dividir por zero viram a mesma coisa."},
  {"h3": "Sete peças, sete classes"},
  {"p": "E cada uma diz de quem é a culpa: `ValueObjectError` é do valor, `AggregateError` é da regra de negócio, `RepositoryError` é da consulta."},
  {"h3": "A base pega todas"},
  {"p": "`handle DomainError` sem listar as nove."},
  {"h3": "E ela NÃO pega um erro de fora"},
  {"p": "Senão `handle DomainError` viraria um `handle` sem tipo — e o tratamento de domínio engoliria um bug de divisão por zero."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/50-dominio/268_valor_e_entidade.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '268-o-que-separa-um-valor-de-uma-entidade', text: "268 · o que separa um valor de uma entidade", level: 2 as const }, { id: 'o-valor-e-igual-por-conteudo', text: "O valor é igual por conteúdo", level: 3 as const }, { id: 'a-entidade-e-igual-por-identidade', text: "A entidade é igual por identidade", level: 3 as const }, { id: 'e-ela-muda-sem-deixar-de-ser-ela', text: "E ela muda sem deixar de ser ela", level: 3 as const }, { id: '269-a-regra-cobrada-na-criacao', text: "269 · a regra cobrada na criacao", level: 2 as const }, { id: 'a-criacao-e-o-unico-ponto-que-impede', text: "A criação é o único ponto que impede", level: 3 as const }, { id: 'e-ela-vale-em-toda-fronteira', text: "E ela vale em toda fronteira", level: 3 as const }, { id: 'um-valor-nao-muda', text: "Um valor não muda", level: 3 as const }, { id: 'e-ele-nasce-completo', text: "E ele nasce completo", level: 3 as const }, { id: 'a-regra-que-estoura-e-um-bug-dela', text: "A regra que estoura é um bug DELA", level: 3 as const }, { id: '270-o-agregado-e-a-unica-porta-de-escrita', text: "270 · o agregado e a unica porta de escrita", level: 2 as const }, { id: 'escrever-por-fora-e-recusado', text: "Escrever por fora é recusado", level: 3 as const }, { id: 'a-invariante-e-cobrada-na-saida', text: "A invariante é cobrada na SAÍDA", level: 3 as const }, { id: 'e-o-comando-recusado-e-desfeito', text: "E o comando recusado é desfeito", level: 3 as const }, { id: 'a-versao-conta-os-comandos', text: "A versão conta os comandos", level: 3 as const }, { id: '271-o-fato-espera-a-confirmacao', text: "271 · o fato espera a confirmacao", level: 2 as const }, { id: 'o-evento-nao-muda', text: "O evento não muda", level: 3 as const }, { id: 'ele-fica-guardado-ate-a-confirmacao', text: "Ele fica guardado até a confirmação", level: 3 as const }, { id: 'a-unidade-desfeita-nao-publica-nada', text: "A unidade desfeita não publica nada", level: 3 as const }, { id: 'e-nao-da-para-desfazer-o-confirmado', text: "E não dá para desfazer o confirmado", level: 3 as const }, { id: '272-a-regra-de-negocio-que-se-combina-e-se-explica', text: "272 · a regra de negocio que se combina e se explica", level: 2 as const }, { id: 'a-decisao', text: "A decisão", level: 3 as const }, { id: 'a-explicacao-aponta-a-parte-que-falhou', text: "A explicação aponta a PARTE que falhou", level: 3 as const }, { id: 'e-a-mesma-regra-filtra-uma-lista', text: "E a mesma regra filtra uma lista", level: 3 as const }, { id: 'uma-regra-quebrada-levanta', text: "Uma regra quebrada LEVANTA", level: 3 as const }, { id: '273-o-repositorio-guarda-agregados-inteiros', text: "273 · o repositorio guarda AGREGADOS INTEIROS", level: 2 as const }, { id: 'as-duas-perguntas-existem', text: "As duas perguntas existem", level: 3 as const }, { id: 'a-consulta-usa-a-mesma-regra-da-decisao', text: "A consulta usa a MESMA regra da decisão", level: 3 as const }, { id: 'e-um-objeto-de-valor-nao-entra', text: "E um objeto de VALOR não entra", level: 3 as const }, { id: '274-a-fronteira-entre-dois-modelos', text: "274 · a fronteira entre dois modelos", level: 2 as const }, { id: 'sem-traducao-nao-atravessa', text: "Sem tradução, não atravessa", level: 3 as const }, { id: 'quem-escuta-reage-e-nao-decide', text: "Quem escuta REAGE, e não decide", level: 3 as const }, { id: 'e-um-ouvinte-que-estoura-nao-impede-os-outros', text: "E um ouvinte que estoura não impede os outros", level: 3 as const }, { id: '275-a-invariante-quebrada-e-um-bug-dela', text: "275 · a invariante quebrada e um bug DELA", level: 2 as const }, { id: 'as-duas-mensagens-orientam-lugares-diferentes', text: "As duas mensagens orientam lugares diferentes", level: 3 as const }, { id: 'e-o-estado-volta-nos-dois-casos', text: "E o estado volta nos dois casos", level: 3 as const }, { id: '276-o-comando-que-falha-no-meio-nao-deixa-metade', text: "276 · o comando que falha no meio nao deixa metade", level: 2 as const }, { id: 'estado-versao-e-eventos-voltam', text: "Estado, versão e eventos voltam", level: 3 as const }, { id: 'o-evento-do-comando-desfeito-tambem-some', text: "O evento do comando desfeito também some", level: 3 as const }, { id: 'e-a-invariante-violada-tem-o-mesmo-efeito', text: "E a invariante violada tem o mesmo efeito", level: 3 as const }, { id: '277-a-unidade-confere-todos-antes-de-gravar-qualquer', text: "277 · a unidade confere TODOS antes de gravar QUALQUER", level: 2 as const }, { id: 'as-duas-pontas-de-uma-transferencia', text: "As duas pontas de uma transferência", level: 3 as const }, { id: 'a-unidade-que-terminou-nao-recebe-mais', text: "A unidade que terminou não recebe mais", level: 3 as const }, { id: 'e-eventospendentes-mostra-sem-publicar', text: "E `eventos_pendentes` mostra sem publicar", level: 3 as const }, { id: '278-a-identidade-nasce-com-o-objeto', text: "278 · a identidade nasce com o objeto", level: 2 as const }, { id: 'o-id-e-texto-e-nasce-com-o-agregado', text: "O id é texto, e nasce com o agregado", level: 3 as const }, { id: 'a-versao-conta-os-comandos', text: "A versão conta os comandos", level: 3 as const }, { id: 'e-estado-e-uma-copia', text: "E `estado()` é uma cópia", level: 3 as const }, { id: '279-regras-que-se-combinam-em-arvore', text: "279 · regras que se combinam em arvore", level: 2 as const }, { id: 'a-arvore-inteira-tem-descricao', text: "A árvore inteira tem descrição", level: 3 as const }, { id: 'o-motivo-segue-o-caminho-que-falhou', text: "O motivo segue o caminho que falhou", level: 3 as const }, { id: 'e-a-mesma-arvore-filtra-a-lista', text: "E a mesma árvore filtra a lista", level: 3 as const }, { id: '280-o-mesmo-contrato-sobre-outro-armazem', text: "280 · o mesmo contrato sobre outro armazem", level: 2 as const }, { id: 'quem-chama-nao-sabe-onde-o-dado-mora', text: "Quem chama não sabe onde o dado mora", level: 3 as const }, { id: 'e-a-ausencia-responde-igual', text: "E a ausência responde igual", level: 3 as const }, { id: '281-um-caso-de-uso-inteiro', text: "281 · um caso de uso inteiro", level: 2 as const }, { id: 'o-evento-espera', text: "O evento espera", level: 3 as const }, { id: 'pagar-duas-vezes-e-recusado', text: "Pagar duas vezes é recusado", level: 3 as const }, { id: 'e-a-consulta-usa-a-regra-da-decisao', text: "E a consulta usa a regra da decisão", level: 3 as const }, { id: '282-a-familia-de-erros-do-dominio', text: "282 · a familia de erros do dominio", level: 2 as const }, { id: 'sete-pecas-sete-classes', text: "Sete peças, sete classes", level: 3 as const }, { id: 'a-base-pega-todas', text: "A base pega todas", level: 3 as const }, { id: 'e-ela-nao-pega-um-erro-de-fora', text: "E ela NÃO pega um erro de fora", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"50 · Domínio e DDD"}
      description={"15 exercícios: valor, entidade, agregado, evento, regra e unidade de trabalho."}
      href={"/docs/exercicios/50-dominio"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
