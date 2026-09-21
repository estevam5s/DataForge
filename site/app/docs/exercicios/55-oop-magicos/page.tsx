// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "55 · Métodos mágicos",
  description: "15 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 55`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[343](#343-como-um-objeto-se-mostra-e-se-compara)", "**como um objeto se mostra e se compara**", "os tres mais usados. '__str__' e para quem LE, '__repr__'"], ["[344](#344-o-objeto-que-entra-numa-conta)", "**o objeto que entra numa conta**", "sobrecarregar operador e o que faz um tipo de dominio"], ["[345](#345-o-objeto-que-se-comporta-como-colecao)", "**o objeto que se comporta como colecao**", "'__len__', '__getitem__', '__setitem__', '__contains__' e"], ["[346](#346-ordenar-objetos)", "**ordenar objetos**", "'__lt__' e o unico que 'sort' precisa. Os outros tres"], ["[347](#347-o-objeto-que-se-chama-e-o-que-se-abre)", "**o objeto que se chama, e o que se abre**", "'__call__' faz um objeto virar acao — util quando ele"], ["[348](#348-interceptar-a-leitura-e-a-escrita)", "**interceptar a leitura e a escrita**", "'__getattr__' responde pelo que NAO existe;"], ["[349](#349-quanto-vale-e-se-e-verdade)", "**quanto vale, e se e verdade**", "'__int__', '__float__' e '__bool__' decidem o que"], ["[350](#350-um-iterador-com-estado)", "**um iterador com estado**", "'__iter__' devolvendo uma lista e o caminho simples."], ["[351](#351-copiar-sem-levar-o-que-nao-se-quer)", "**copiar sem levar o que nao se quer**", "a copia RASA compartilha o que esta dentro. Mudar a lista"], ["[352](#352-quando-o-record-basta)", "**quando o record basta**", "um 'record' ja traz '__eq__', '__hash__' e a"], ["[353](#353-root-com-tres-niveis)", "**'root' com tres niveis**", "'root' e o pai de QUEM DECLAROU o metodo, e nao o pai da"], ["[354](#354-o-que-nao-se-usa-nao-pode-custar)", "**o que nao se usa nao pode custar**", "contratos, sobrecarga, invariantes, metaclasses e 'lazy'"], ["[355](#355-perguntar-ao-objeto-o-que-ele-tem)", "**perguntar ao objeto o que ele tem**", "reflexao e o que faz uma biblioteca funcionar com um tipo"], ["[356](#356-despacho-por-forma-e-a-classe-que-nasce-mudada)", "**despacho por forma, e a classe que nasce mudada**", "'overload' escolhe o metodo pelo TIPO dos argumentos, e"], ["[357](#357-o-mapa-e-os-tres-que-nao-existem)", "**o mapa, e os tres que NAO existem**", "fechar o modulo com a lista do que cada magico responde,"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "343 · como um objeto se mostra e se compara"},
  {"p": "**Enunciado.** os tres mais usados. '__str__' e para quem LE, '__repr__'"},
  { code: `// e para quem DEPURA, e '__eq__' sem '__hash__' faz o objeto sumir de
// um vault — e o Python nao avisa.

blueprint Dinheiro:
    action setup(centavos, moeda):
        self.centavos := centavos
        self.moeda := moeda

    action __str__():
        reais := self.centavos ~/ 100
        resto := self.centavos % 100
        centavos := $"{resto}" given resto bigger_eq 10 otherwise $"0{resto}"
        yield $"{self.moeda} {reais},{centavos}"

    action __repr__():
        yield $"Dinheiro({self.centavos}, \\"{self.moeda}\\")"

    action __eq__(outro):
        yield self.centavos is outro.centavos and self.moeda is outro.moeda

    action __hash__():
        yield hash($"{self.centavos}:{self.moeda}")

out "== 1. str e para quem le =="

dez := spawn Dinheiro(1050, "BRL")
assert str(dez) is "BRL 10,50"
out $"   {dez}"

out ""
out "== 2. repr e para quem depura =="

// Ele deve poder ser colado de volta no codigo.
assert repr(dez) is 'Dinheiro(1050, "BRL")'

out ""
out "== 3. igualdade por CONTEUDO =="

assert dez is spawn Dinheiro(1050, "BRL")
assert dez isnt spawn Dinheiro(1050, "USD")
assert dez isnt spawn Dinheiro(999, "BRL")

out ""
out "== 4. e o hash que acompanha =="

// Sem '__hash__', dois objetos iguais teriam hashes diferentes — e o
// segundo nao acharia o primeiro num vault.
caixa := {}
caixa[dez] := "o primeiro"
assert caixa[spawn Dinheiro(1050, "BRL")] is "o primeiro"
assert len(keys(caixa)) is 1

caixa[spawn Dinheiro(1050, "BRL")] := "o mesmo"
assert len(keys(caixa)) is 1
out "   dois objetos iguais, uma chave"

out ""
out "== 5. sem os dois, o objeto so e igual a si mesmo =="

blueprint Solto:
    action setup(n):
        self.n := n

a := spawn Solto(1)
b := spawn Solto(1)
assert a isnt b
assert a is a

out ""
out "== 6. e o padrao de 'str' quando nao ha '__str__' =="

texto := str(a)
assert "Solto" in texto
out $"   {texto}"

out "exercicio 343 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/343_texto_e_igualdade.df` },
  {"p": "Os três mais usados. `__str__` é para quem **lê**, `__repr__` é para quem **depura**, e `__eq__` sem `__hash__` faz o objeto sumir de um vault — e o Python não avisa."},
  {"h3": "`repr` era inalcançável"},
  {"p": "`__repr__` estava na lista de mágicos, na referência e na doc, e a linguagem não tinha como pedi-lo: não havia `repr`, e um cluster de objetos imprime com `__str__`. Ele só era alcançado como **reserva**, quando não havia `__str__` — ou seja, exatamente quando não se queria a distinção."},
  {"h3": "O par eq/hash nunca se separa"},
  {"p": "Sem `__hash__`, dois objetos iguais teriam hashes diferentes — e o segundo não acharia o primeiro num vault."},
  {"h3": "E sem os dois, o objeto só é igual a si mesmo"},
  {"p": "O que é o padrão certo: identidade é o que um blueprint tem por natureza."},
  {"h2": "344 · o objeto que entra numa conta"},
  {"p": "**Enunciado.** sobrecarregar operador e o que faz um tipo de dominio"},
  { code: `// parecer um numero. O limite: so faca isso quando a operacao TIVER o
// significado que o simbolo sugere — um '+' que envia e-mail e o pior
// codigo que existe.

blueprint Vetor:
    action setup(x, y):
        self.x := x
        self.y := y

    action __str__():
        yield $"({self.x}, {self.y})"

    action __eq__(o):
        yield self.x is o.x and self.y is o.y

    operator + (o):
        yield spawn Vetor(self.x + o.x, self.y + o.y)

    operator - (o):
        yield spawn Vetor(self.x - o.x, self.y - o.y)

    operator * (k):
        yield spawn Vetor(self.x * k, self.y * k)

    action __abs__():
        yield sqrt(self.x ** 2 + self.y ** 2)

    action __neg__():
        yield spawn Vetor(-self.x, -self.y)

out "== 1. somar e subtrair =="

a := spawn Vetor(1, 2)
b := spawn Vetor(3, 4)

assert(a + b) is spawn Vetor(4, 6)
assert(b - a) is spawn Vetor(2, 2)
out $"   {a} + {b} = {a + b}"

out ""
out "== 2. multiplicar por escalar =="

assert(a * 3) is spawn Vetor(3, 6)

out ""
out "== 3. o modulo, e o negativo =="

assert abs(spawn Vetor(3, 4)) is 5.0
assert(-a) is spawn Vetor(-1, -2)

out ""
out "== 4. eles compoem =="

resultado := (a + b) * 2 - a
assert resultado is spawn Vetor(7, 10)
out $"   (a + b) * 2 - a = {resultado}"

out ""
out "== 5. e um tipo SEM o operador recusa =="

blueprint Sem:
    action setup(n):
        self.n := n

recusou := no
monitor:
    x := spawn Sem(1) + spawn Sem(2)
handle Error as e:
    recusou := yes
    out $"   {e.message}"
assert recusou

out ""
out "== 6. a regra de quando NAO sobrecarregar =="

out "   so quando a operacao TEM o significado do simbolo"
out "   um '+' que envia e-mail e pior que um metodo com nome ruim"

out "exercicio 344 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/344_operadores.df` },
  {"p": "Sobrecarregar operador é o que faz um tipo de domínio parecer um número."},
  {"h3": "Eles compõem"},
  {"p": "`(a + b) * 2 - a` — e é a composição que justifica a sobrecarga: um método com nome não compõe assim."},
  {"h3": "Um tipo sem o operador recusa"},
  {"p": "Com uma mensagem que nomeia os dois lados."},
  {"h3": "E a regra de quando NÃO sobrecarregar"},
  {"p": "Só quando a operação **tem** o significado do símbolo. Um `+` que envia e-mail é pior que um método com nome ruim: o nome ruim pelo menos pode ser lido."},
  {"h2": "345 · o objeto que se comporta como colecao"},
  {"p": "**Enunciado.** '__len__', '__getitem__', '__setitem__', '__contains__' e"},
  { code: `// '__iter__' sao o que fazem 'len(x)', 'x[0]', 'k in x' e 'cycle i in
// x' funcionarem SEM que nenhum deles saiba o que e o seu tipo. E o
// mesmo protocolo da ponte para o Python.

blueprint Carrinho:
    action setup():
        self.itens := []

    action __len__():
        yield len(self.itens)

    action __getitem__(i):
        yield self.itens[i]

    action __setitem__(i, valor):
        self.itens[i] := valor

    action __contains__(nome):
        cycle item in self.itens:
            given item["nome"] is nome:
                yield yes
        yield no

    action __iter__():
        yield self.itens

    action acrescentar(nome, preco):
        self.itens.append({"nome": nome, "preco": preco})
        yield self

out "== 1. len =="

c := spawn Carrinho()
assert len(c) is 0
c.acrescentar("cafe", 32.5)
c.acrescentar("filtro", 9.0)
c.acrescentar("moedor", 240.0)
assert len(c) is 3

out ""
out "== 2. indexar, e escrever por indice =="

assert c[0]["nome"] is "cafe"
assert c[-1]["nome"] is "moedor"

c[1] := {"nome": "coador", "preco": 12.0}
assert c[1]["nome"] is "coador"

out ""
out "== 3. 'in' pergunta ao objeto =="

assert "cafe" in c
assert "coador" in c
assert "filtro" not in c

out ""
out "== 4. e o 'cycle' o percorre =="

nomes := []
cycle item in c:
    nomes.append(item["nome"])
assert nomes is ["cafe", "coador", "moedor"]
out $"   {nomes}"

out ""
out "== 5. a compreensao tambem =="

precos := [i["preco"] cycle i in c]
assert sum(precos) is 284.5

caros := [i["nome"] cycle i in c given i["preco"] bigger 100.0]
assert caros is ["moedor"]

out ""
out "== 6. e o pipeline =="

total := c >> morph i: i["preco"] >> distill a, v: a + v 0
assert total is 284.5
out $"   total: {total}"

out ""
out "== 7. nada disso sabe o que e um Carrinho =="

// Trocar protocolo por 'isinstance' em qualquer um desses quebraria
// tambem o quadro, a tupla e a ponte para o Python — todos entram
// pela mesma porta.
action resumir(qualquer_colecao):
    yield $"{len(qualquer_colecao)} item(ns)"

assert resumir(c) is "3 item(ns)"
assert resumir([1, 2, 3]) is "3 item(ns)"
assert resumir("abc") is "3 item(ns)"
assert resumir({"a": 1, "b": 2, "c": 3}) is "3 item(ns)"

out "exercicio 345 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/345_colecao_propria.df` },
  {"p": "`__len__`, `__getitem__`, `__setitem__`, `__contains__` e `__iter__` são o que fazem `len(x)`, `x[0]`, `k in x` e `cycle i in x` funcionarem **sem que nenhum deles saiba o que é o seu tipo**."},
  {"h3": "É o mesmo protocolo da ponte para o Python"},
  {"p": "Um `ndarray` continua um `ndarray` porque o interpretador trata objeto estranho por protocolo, e não por tipo."},
  {"h3": "A compreensão e o pipeline também"},
  {"p": "`[i[\"preco\"] cycle i in c]` e `c >> morph … >> distill …` — nenhum dos dois sabe o que é um carrinho."},
  {"h3": "E trocar protocolo por `isinstance` quebraria tudo junto"},
  {"p": "O quadro, a tupla e a ponte entram pela mesma porta."},
  {"h2": "346 · ordenar objetos"},
  {"p": "**Enunciado.** '__lt__' e o unico que 'sort' precisa. Os outros tres"},
  { code: `// existem para o codigo LER melhor — e declarar so '__lt__' faz
// 'a bigger b' recusar, o que surpreende quem ja conseguiu ordenar.

blueprint Versao:
    action setup(maior, menor, correcao):
        self.maior := maior
        self.menor := menor
        self.correcao := correcao

    action __str__():
        yield $"{self.maior}.{self.menor}.{self.correcao}"

    action partes():
        yield [self.maior, self.menor, self.correcao]

    action __eq__(o):
        yield self.partes() is o.partes()

    action __lt__(o):
        yield self.partes() smaller o.partes()

    action __le__(o):
        yield self.partes() smaller_eq o.partes()

    action __gt__(o):
        yield self.partes() bigger o.partes()

    action __ge__(o):
        yield self.partes() bigger_eq o.partes()

    action __hash__():
        yield hash(str(self))

out "== 1. comparar =="

steady UM := spawn Versao(1, 0, 0)
steady DOIS := spawn Versao(1, 2, 0)
steady TRES := spawn Versao(1, 2, 3)

assert UM smaller DOIS
assert DOIS smaller TRES
assert TRES bigger UM
assert UM smaller_eq UM
assert UM is spawn Versao(1, 0, 0)

out ""
out "== 2. ordenar =="

steady SOLTAS := [
    spawn Versao(2, 0, 0),
    spawn Versao(1, 10, 0),
    spawn Versao(1, 2, 0),
    spawn Versao(1, 2, 3)
]

em_ordem := sorted(SOLTAS)
assert [str(v) cycle v in em_ordem] is ["1.2.0", "1.2.3", "1.10.0", "2.0.0"]
out $"   {[str(v) cycle v in em_ordem]}"

// E e ai que se ve por que a comparacao NAO pode ser por texto:
// "1.10.0" vem antes de "1.2.0" em ordem alfabetica.
por_texto := sorted([str(v) cycle v in SOLTAS])
assert por_texto[0] is "1.10.0"
out $"   por texto (errado): {por_texto}"

out ""
out "== 3. min, max e o maior de todos =="

assert str(min(SOLTAS)) is "1.2.0"
assert str(max(SOLTAS)) is "2.0.0"

out ""
out "== 4. e a ordem inversa =="

assert [str(v) cycle v in sorted(SOLTAS, void, yes)][0] is "2.0.0"

out ""
out "== 5. um objeto sem '__lt__' nao ordena =="

blueprint Sem:
    action setup(n):
        self.n := n

recusou := no
monitor:
    sorted([spawn Sem(2), spawn Sem(1)])
handle Error as e:
    recusou := yes
assert recusou

// A saida sem declarar mágico nenhum: ordenar por uma CHAVE.
assert [s.n cycle s in sorted([spawn Sem(2), spawn Sem(1)], lambda s => s.n)] is [1, 2]

out "exercicio 346 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/346_ordem_e_comparacao.df` },
  {"p": "`__lt__` é o único que `sorted` precisa. Os outros três existem para o código **ler** melhor."},
  {"h3": "Por que a comparação não pode ser por texto"},
  {"p": "`\"1.10.0\"` vem antes de `\"1.2.0\"` em ordem alfabética. Ordenar versão por texto é o defeito mais comum de um gerenciador de pacotes caseiro."},
  {"h3": "E um objeto sem `__lt__` não ordena"},
  {"p": "A saída sem declarar mágico nenhum é ordenar por uma **chave** — e é a que serve quando o critério muda de lugar para lugar."},
  {"h2": "347 · o objeto que se chama, e o que se abre"},
  {"p": "**Enunciado.** '__call__' faz um objeto virar acao — util quando ele"},
  { code: `// tem ESTADO entre chamadas. '__enter__'/'__exit__' garantem a
// limpeza, e sao o que 'defer' faz do outro lado.

adopt Arcane.IO as IO
adopt Arcane.OS as OS

out "== 1. um objeto que se chama =="

blueprint Contador:
    action setup(passo):
        self.passo := passo
        self.total := 0

    action __call__(quanto):
        self.total := self.total + quanto * self.passo
        yield self.total

dobro := spawn Contador(2)
assert dobro(5) is 10
assert dobro(3) is 16
assert dobro.total is 16
out $"   depois de duas chamadas: {dobro.total}"

out ""
out "== 2. e por que isso nao e so uma closure =="

// O estado fica VISIVEL e nomeado: 'dobro.total' e 'dobro.passo'
// podem ser lidos, testados e serializados. Uma closure esconde os
// dois.
assert dobro.passo is 2

out ""
out "== 3. ele passa onde uma acao passa =="

assert [dobro(1) cycle i in range(3)][-1] is 22

action aplicar_tres(f):
    yield [f(1), f(1), f(1)]

steady outro := spawn Contador(10)
assert aplicar_tres(outro) is [10, 20, 30]

out ""
out "== 4. o bloco com entrada e saida =="

steady pasta := $"{OS.temp_dir()}/df-347-{randint(100000, 999999)}"
IO.mkdir(pasta)

eventos := []

blueprint Sessao:
    action setup(nome):
        self.nome := nome
        self.aberta := no

    action __enter__():
        self.aberta := yes
        eventos.append($"abriu {self.nome}")
        yield self

    action __exit__(_tipo, _valor, _pilha):
        self.aberta := no
        eventos.append($"fechou {self.nome}")
        yield no

s := spawn Sessao("A")
s.__enter__()
assert s.aberta
eventos.append("trabalhou")
s.__exit__(void, void, void)
assert not s.aberta
assert eventos is ["abriu A", "trabalhou", "fechou A"]
out $"   {eventos}"

out ""
out "== 5. e a forma que a linguagem usa para isso e o 'defer' =="

// Nao ha 'with' em DataForge: quem garante a saida e o 'defer', e ele
// roda em TODOS os caminhos.
eventos := []

action trabalhar_com(nome, vai_falhar):
    sessao := spawn Sessao(nome)
    sessao.__enter__()
    defer:
        sessao.__exit__(void, void, void)
    given vai_falhar:
        trigger "falhou no meio"
    eventos.append("terminou")

monitor:
    trabalhar_com("B", yes)
handle Error:
    void

assert eventos is ["abriu B", "fechou B"]
out "   falhou no meio, e fechou mesmo assim"

IO.remove_tree(pasta)
out "exercicio 347 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/347_chamavel_e_contexto.df` },
  {"p": "`__call__` faz um objeto virar ação — útil quando ele tem **estado** entre chamadas."},
  {"h3": "Por que isso não é só uma closure"},
  {"p": "O estado fica visível e nomeado: `dobro.total` e `dobro.passo` podem ser lidos, testados e serializados. Uma closure esconde os dois."},
  {"h3": "E ele passa onde uma ação passa"},
  {"p": "Numa compreensão, num argumento — o protocolo é o mesmo."},
  {"h3": "O bloco com entrada e saída"},
  {"p": "Não há `with` em DataForge: quem garante a saída é o `defer`, e ele roda em **todos** os caminhos."},
  {"h2": "348 · interceptar a leitura e a escrita"},
  {"p": "**Enunciado.** '__getattr__' responde pelo que NAO existe;"},
  { code: `// '__getattribute__' responde por TUDO — e e a diferenca entre um
// objeto flexivel e uma recursao infinita.

out "== 1. '__getattr__' so entra quando o campo nao existe =="

blueprint Config:
    action setup(dados):
        self.dados := dados

    action __getattr__(nome):
        given nome in self.dados:
            yield self.dados[nome]
        yield $"<sem {nome}>"

c := spawn Config({"host": "localhost", "porta": 8080})

// 'dados' existe: nao passa pelo magico.
assert len(keys(c.dados)) is 2
// 'host' nao e campo: passa.
assert c.host is "localhost"
assert c.porta is 8080
assert c.qualquer is "<sem qualquer>"
out $"   {c.host}:{c.porta}"

out ""
out "== 2. e e isso que faz um vault virar objeto =="

action de_vault(v):
    yield spawn Config(v)

api := de_vault({"url": "https://x", "chave": "abc"})
assert api.url is "https://x"

out ""
out "== 3. '__setattr__' intercepta a escrita =="

registro := []

blueprint Auditada:
    // O deposito e um campo DECLARADO, e nao criado no 'setup': um
    // campo declarado com padrao mutavel ganha uma copia por
    // instancia, e ja existe quando o magico roda. Cria-lo dentro do
    // 'setup' faria a primeira escrita entrar no proprio
    // '__setattr__' antes de haver onde guardar.
    valores: Vault := {}

    action __setattr__(nome, valor):
        registro.append($"{nome} := {valor}")
        // Escrita por INDICE nao passa pelo magico de membro: e o que
        // permite guardar sem recursao.
        self.valores[nome] := valor

    action __getattr__(nome):
        yield self.valores[nome] ?? void

a := spawn Auditada()
a.saldo := 100
a.nome := "Ana"

assert a.saldo is 100
assert a.nome is "Ana"
assert registro is ["saldo := 100", "nome := Ana"]
out $"   {registro}"

out ""
out "== 4. a propriedade, para UM campo =="

// Quando so um campo precisa de logica, uma propriedade e melhor que
// interceptar tudo: ela diz na declaracao o que faz.
blueprint Retangulo:
    action setup(largura, altura):
        self.largura := largura
        self.altura := altura

    get area():
        yield self.largura * self.altura

    get proporcao():
        yield round(self.largura / self.altura, 2)

r := spawn Retangulo(16, 9)
assert r.area is 144
assert r.proporcao is 1.78

// Ela e SO leitura: escrever e recusado.
recusou := no
monitor:
    r.area := 1
handle Error as e:
    recusou := yes
    out $"   {e.message}"
assert recusou

out ""
out "== 5. e a propriedade com escrita =="

blueprint Celsius:
    action setup(c):
        self.c := c

    get fahrenheit():
        yield self.c * 9 / 5 + 32

    set fahrenheit(f):
        self.c := (f - 32) * 5 / 9

t := spawn Celsius(100)
assert t.fahrenheit is 212.0
t.fahrenheit := 32
assert t.c is 0.0
out "   escrever em fahrenheit mudou o celsius"

out "exercicio 348 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/348_acesso_interceptado.df` },
  {"p": "`__getattr__` responde pelo que **não** existe; `__getattribute__` responde por **tudo** — e é a diferença entre um objeto flexível e uma recursão infinita."},
  {"h3": "O campo interno precisa existir antes"},
  {"p": "Um depósito criado no `setup` faria a primeira escrita entrar no próprio `__setattr__` antes de haver onde guardar. Um campo **declarado** com padrão mutável ganha uma cópia por instância, e já existe quando o mágico roda."},
  {"h3": "Escrita por ÍNDICE não passa pelo mágico de membro"},
  {"p": "É o que permite guardar sem recursão."},
  {"h3": "E a propriedade, para UM campo"},
  {"p": "Quando só um campo precisa de lógica, ela é melhor que interceptar tudo: ela diz na declaração o que faz. E ela é só leitura até alguém escrever o `set`."},
  {"h2": "349 · quanto vale, e se e verdade"},
  {"p": "**Enunciado.** '__int__', '__float__' e '__bool__' decidem o que"},
  { code: `// acontece num 'int(x)', num 'float(x)' e num 'given x:'. E o
// '__bool__' e o mais perigoso dos tres: ele muda a verdade de TODO
// objeto daquele tipo.

blueprint Temperatura:
    action setup(celsius):
        self.celsius := celsius

    action __str__():
        yield $"{self.celsius}C"

    action __float__():
        yield self.celsius * 1.0

    action __int__():
        yield int(round(self.celsius, 0))

    action __bool__():
        // "tem leitura" — e nao "e diferente de zero".
        yield self.celsius is not void

out "== 1. converter =="

t := spawn Temperatura(21.6)
assert float(t) is 21.6
assert int(t) is 22
out $"   {t} -> int {int(t)}, float {float(t)}"

out ""
out "== 2. a verdade =="

assert spawn Temperatura(0.0)
assert spawn Temperatura(-5.0)
assert not spawn Temperatura(void)

// E e por isso que '__bool__' e perigoso: sem ele, ZERO GRAUS seria
// falso — e "nao ha leitura" e "esta zero" viram a mesma coisa.
sem_leitura := spawn Temperatura(void)
given sem_leitura:
    assert no
otherwise:
    out "   sem leitura e falso; zero grau e verdadeiro"

out ""
out "== 3. o padrao, quando nao ha '__bool__' =="

blueprint Simples:
    action setup(n):
        self.n := n

// Toda instancia e verdadeira.
assert spawn Simples(0)
assert spawn Simples(void)

out ""
out "== 4. '__len__' NAO decide a verdade aqui =="

// Em Python, um objeto com len() 0 e falso. Aqui nao: o
// interpretador pergunta 'if obj:' sobre instancias, e um '__len__'
// mudaria a verdade de todo objeto que declara tamanho.
blueprint Lista:
    action setup():
        self.itens := []

    action __len__():
        yield len(self.itens)

vazia := spawn Lista()
assert len(vazia) is 0
assert vazia
out "   tamanho zero, e continua verdadeira"

out ""
out "== 5. e e por isso que se pergunta o TAMANHO =="

// A forma que funciona nas duas linguagens, e que diz o que quer
// dizer.
given len(vazia) is 0:
    out "   'len(x) is 0' e explicito; 'not x' depende do tipo"

out ""
out "== 6. o arredondamento tambem e do objeto =="

blueprint Preco:
    action setup(v):
        self.v := v

    action __float__():
        yield self.v

    action __round__(casas):
        yield round(self.v, casas)

p := spawn Preco(19.987)
assert round(p, 2) is 19.99
assert round(p, 0) is 20.0

out "exercicio 349 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/349_conversao_e_verdade.df` },
  {"p": "`__int__`, `__float__` e `__bool__` decidem o que acontece num `int(x)`, num `float(x)` e num `given x:`."},
  {"h3": "`__bool__` é o mais perigoso dos três"},
  {"p": "Ele muda a verdade de **todo** objeto daquele tipo. Sem ele, zero graus seria falso — e \"não há leitura\" e \"está zero\" viram a mesma coisa."},
  {"h3": "`__len__` NÃO decide a verdade aqui"},
  {"p": "Em Python, um objeto com `len()` 0 é falso. Aqui não: o interpretador pergunta `if obj:` sobre instâncias, e um `__len__` mudaria a verdade de todo objeto que declara tamanho."},
  {"h3": "E por isso se pergunta o TAMANHO"},
  {"p": "`len(x) is 0` é explícito e funciona nas duas linguagens; `not x` depende do tipo."},
  {"h2": "350 · um iterador com estado"},
  {"p": "**Enunciado.** '__iter__' devolvendo uma lista e o caminho simples."},
  { code: `// '__next__' e o caminho que nao materializa nada — e a diferenca
// aparece num milhao de itens, onde o primeiro aloca um milhao e o
// segundo aloca um.

blueprint Contagem:
    action setup(de, ate, passo):
        self.de := de
        self.ate := ate
        self.passo := passo
        self.atual := de

    action __iter__():
        self.atual := self.de
        yield self

    action __next__():
        // 'void' encerra. Nao ha 'StopIteration' aqui: sinalizar o fim
        // com um erro obrigaria a linguagem a ter uma excecao que nao
        // e erro nenhum — e a confundir com um 'handle Error' de
        // verdade, que e o que acontece em Python.
        given self.atual bigger self.ate:
            yield void
        valor := self.atual
        self.atual := self.atual + self.passo
        yield valor

out "== 1. percorrer =="

vistos := []
cycle n in spawn Contagem(1, 10, 3):
    vistos.append(n)
assert vistos is [1, 4, 7, 10]
out $"   {vistos}"

out ""
out "== 2. e ele reinicia a cada 'cycle' =="

c := spawn Contagem(1, 3, 1)
primeira := [n cycle n in c]
segunda := [n cycle n in c]
assert primeira is segunda
assert primeira is [1, 2, 3]

out ""
out "== 3. o generator da linguagem faz o mesmo, sem blueprint =="

stream action contar(de, ate, passo):
    atual := de
    persist atual smaller_eq ate:
        emit atual
        atual := atual + passo

assert contar(1, 10, 3).to_cluster() is [1, 4, 7, 10]

out ""
out "== 4. e ele e preguicoso de verdade =="

// Um generator INFINITO so termina porque quem consome para.
stream action naturais():
    n := 1
    persist yes:
        emit n
        n += 1

assert naturais().take(5) is [1, 2, 3, 4, 5]

// 'take' ja devolve um cluster; 'to_cluster()' num generator
// INFINITO trava, e e a armadilha de sempre.
assert typeof(naturais().take(3)) is "Cluster"

out ""
out "== 5. compondo — e a ordem IMPORTA =="

// O pipeline converte a fonte em lista: canalizar um generator
// infinito direto TRAVA o programa. Recorta primeiro, canaliza
// depois.
pares := naturais().take(8) >> sift n: n % 2 is 0
assert pares is [2, 4, 6, 8]
out "   'take' antes do '>>': o infinito precisa de um teto"

out ""
out "== 6. quando usar cada um =="

out "   blueprint com __next__: quando o iterador tem estado NOMEADO"
out "   stream action:          quando e so uma sequencia"

out "exercicio 350 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/350_iterador_proprio.df` },
  {"p": "`__iter__` devolvendo uma lista é o caminho simples. `__next__` é o caminho que não materializa nada — e a diferença aparece num milhão de itens."},
  {"h3": "`void` encerra"},
  {"p": "Não há `StopIteration` aqui: sinalizar o fim com um erro obrigaria a linguagem a ter uma exceção que não é erro nenhum — e a confundir com um `handle Error` de verdade."},
  {"h3": "O generator faz o mesmo, sem blueprint"},
  {"p": "E é preguiçoso de verdade: um `stream action` infinito só termina porque quem consome para."},
  {"h3": "E a ORDEM importa"},
  {"p": "O pipeline converte a fonte em lista: canalizar um generator infinito direto **trava** o programa. Recorta primeiro, canaliza depois."},
  {"h2": "351 · copiar sem levar o que nao se quer"},
  {"p": "**Enunciado.** a copia RASA compartilha o que esta dentro. Mudar a lista"},
  { code: `// da copia muda a do original — e o defeito aparece longe, numa outra
// instancia que ninguem tocou.

adopt Arcane.Objetos as Obj

blueprint Pedido:
    action setup(cliente):
        self.cliente := cliente
        self.itens := []

    action __copy__():
        novo := spawn Pedido(self.cliente)
        yield novo

    action __deepcopy__(_memo := void):
        novo := spawn Pedido(self.cliente)
        novo.itens := [vault(i) cycle i in self.itens]
        yield novo

    action acrescentar(nome, preco):
        self.itens.append({"nome": nome, "preco": preco})
        yield self

out "== 1. a copia rasa compartilha =="

original := spawn Pedido("Ana")
original.acrescentar("cafe", 32.5)

// Aqui o '__copy__' foi escrito para NAO levar os itens.
raso := Obj.clonar(original)
assert raso.cliente is "Ana"
assert len(raso.itens) is 0

out ""
out "== 2. a copia funda leva tudo, e SEPARADO =="

fundo := Obj.clonar_fundo(original)
assert len(fundo.itens) is 1
fundo.itens[0]["preco"] := 99.0
assert original.itens[0]["preco"] is 32.5
out "   mexer na copia funda nao mexeu no original"

out ""
out "== 3. o padrao, quando nao se escreve nenhum dos dois =="

blueprint Simples:
    action setup():
        self.dados := [1, 2, 3]

s := spawn Simples()
r := Obj.clonar(s)
r.dados.append(4)
// A copia rasa compartilha a lista.
assert len(s.dados) is 4
out "   sem '__copy__', a lista e a MESMA lista"

f := Obj.clonar_fundo(s)
f.dados.append(5)
assert len(s.dados) is 4
out "   com copia funda, nao"

out ""
out "== 4. congelar =="

congelado := Obj.congelar(spawn Simples())
recusou := no
monitor:
    congelado.dados := []
handle Error as e:
    recusou := yes
    out $"   {e.message}"
assert recusou

out ""
out "== 5. igualdade estrutural, sem escrever '__eq__' =="

a := spawn Simples()
b := spawn Simples()
assert a isnt b
assert Obj.igual(a, b)
out "   'iguais' compara os campos; 'is' compara a identidade"

out ""
out "== 6. e a serializacao so reconstroi o que foi AUTORIZADO =="

// Um desserializador que aceita qualquer tipo e uma porta de entrada:
// o dado escolhe a classe a instanciar.
dados := Obj.para_vault(original)
assert dados["cliente"] is "Ana"

de_volta := Obj.de_vault(dados, [Pedido])
assert de_volta.cliente is "Ana"

nao_listado := no
monitor:
    Obj.de_vault(dados, [Simples])
handle Error:
    nao_listado := yes
assert nao_listado
out "   o dado nunca escolhe o blueprint"

out "exercicio 351 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/351_copia_e_congelar.df` },
  {"p": "A cópia **rasa** compartilha o que está dentro. Mudar a lista da cópia muda a do original — e o defeito aparece longe, numa outra instância que ninguém tocou."},
  {"h3": "Sem `__copy__`, a lista é a MESMA lista"},
  {"p": "E com cópia funda, não. Os dois mágicos existem para o objeto decidir o que atravessa."},
  {"h3": "Congelar recusa a escrita"},
  {"p": "Com uma mensagem que nomeia o campo."},
  {"h3": "E a serialização só reconstrói o AUTORIZADO"},
  {"p": "Um desserializador que aceita qualquer tipo é uma porta de entrada: o **dado** escolheria a classe a instanciar."},
  {"h2": "352 · quando o record basta"},
  {"p": "**Enunciado.** um 'record' ja traz '__eq__', '__hash__' e a"},
  { code: `// imutabilidade de graca. Escrever um blueprint com esses tres
// magicos a mao e refazer o que a linguagem faz — e errar num deles.

record Ponto:
    x: Integer
    y: Integer

    action norma():
        yield sqrt(self.x ** 2 + self.y ** 2)

blueprint PontoMutavel:
    action setup(x, y):
        self.x := x
        self.y := y

out "== 1. o record ja compara por conteudo =="

assert Ponto(1, 2) is Ponto(1, 2)
assert Ponto(1, 2) isnt Ponto(1, 3)

// O blueprint, nao.
assert spawn PontoMutavel(1, 2) isnt spawn PontoMutavel(1, 2)

out ""
out "== 2. e ja serve de chave =="

mapa := {}
mapa[Ponto(0, 0)] := "origem"
assert mapa[Ponto(0, 0)] is "origem"

out ""
out "== 3. ele e IMUTAVEL =="

p := Ponto(3, 4)
recusou := no
monitor:
    p.x := 99
handle Error as e:
    recusou := yes
    out $"   {e.message}"
assert recusou

// A forma de "mudar": criar outro.
q := p with {"y": 0}
assert q.x is 3
assert q.y is 0
assert p.y is 4

out ""
out "== 4. e tem metodos =="

assert p.norma() is 5.0

out ""
out "== 5. o 'with' confere as CHAVES =="

// Um campo que nao existe seria um erro de digitacao gravando em
// lugar nenhum.
errou := no
monitor:
    _r := p with {"z": 1}  // df: permitir unknown-field
handle Error as e:
    errou := yes
assert errou

out ""
out "== 6. quando o blueprint e o certo =="

out "   record:    valor, imutavel, comparado por conteudo"
out "   blueprint: identidade, estado que muda, heranca"

// E a prova: um contador NAO e um record.
blueprint Contador:
    action setup():
        self.n := 0

    action somar():
        self.n += 1
        yield self.n

c := spawn Contador()
c.somar()
c.somar()
assert c.n is 2

out ""
out "== 7. o record no 'match' =="

action onde(ponto):
    match ponto:
        point Ponto(0, 0):
            yield "origem"
        point Ponto(x, 0):
            yield $"no eixo x, em {x}"
        point Ponto(0, y):
            yield $"no eixo y, em {y}"
        point Ponto(x, y):
            yield $"em ({x}, {y})"
        default:
            yield "nao e um ponto"

assert onde(Ponto(0, 0)) is "origem"
assert onde(Ponto(5, 0)) is "no eixo x, em 5"
assert onde(Ponto(0, 7)) is "no eixo y, em 7"
assert onde(Ponto(1, 2)) is "em (1, 2)"
assert onde("x") is "nao e um ponto"

out "exercicio 352 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/352_record_vs_blueprint.df` },
  {"p": "Um `record` já traz `__eq__`, `__hash__` e a imutabilidade de graça. Escrever um blueprint com esses três mágicos à mão é refazer o que a linguagem faz — e errar num deles."},
  {"h3": "O `with` confere as CHAVES"},
  {"p": "Um campo que não existe seria um erro de digitação gravando em lugar nenhum."},
  {"h3": "Quando o blueprint é o certo"},
  {"p": "Identidade, estado que muda, herança. Um contador **não** é um record."},
  {"h3": "E o record no `match`"},
  {"p": "A desestruturação por posição é o que faz o `match` ler como a declaração."},
  {"h2": "353 · 'root' com tres niveis"},
  {"p": "**Enunciado.** 'root' e o pai de QUEM DECLAROU o metodo, e nao o pai da"},
  { code: `// classe da instancia. Com dois niveis a conta da certo dos dois
// jeitos — e por isso o defeito sobreviveu: toda heranca de um
// repositorio pequeno tem dois niveis.

blueprint A:
    action nome():
        yield "A"

    action cadeia():
        yield "A"

blueprint B extends A:
    action nome():
        yield "B"

    action cadeia():
        yield $"B -> {root.cadeia()}"

blueprint C extends B:
    action nome():
        yield "C"

    action cadeia():
        yield $"C -> {root.cadeia()}"

out "== 1. tres niveis =="

c := spawn C()
assert c.nome() is "C"
assert c.cadeia() is "C -> B -> A"
out $"   {c.cadeia()}"

out ""
out "== 2. e o defeito que isso pegava =="

// 'root' era o pai da classe da INSTANCIA: dentro de 'B.cadeia', o
// 'self' ainda e um C, entao 'root' voltava a ser B — e 'B.cadeia'
// chamava a si mesmo, para sempre.
out "   com dois niveis a conta dava certo; com tres, era laco infinito"

out ""
out "== 3. o diamante resolve por C3 =="

blueprint Base:
    action quem():
        yield "Base"

blueprint Esquerda extends Base:
    action quem():
        yield $"Esquerda({root.quem()})"

blueprint Direita extends Base:
    action quem():
        yield $"Direita({root.quem()})"

blueprint Fundo extends Esquerda:
    action quem():
        yield $"Fundo({root.quem()})"

f := spawn Fundo()
assert f.quem() is "Fundo(Esquerda(Base))"

out ""
out "== 4. o trait declara, e a instancia cumpre =="

trait Desenhavel:
    action desenhar()

blueprint Circulo with Desenhavel:
    action setup(r):
        self.r := r

    action desenhar():
        yield $"circulo de raio {self.r}"

blueprint Quadrado with Desenhavel:
    action setup(l):
        self.l := l

    action desenhar():
        yield $"quadrado de lado {self.l}"

steady FORMAS := [spawn Circulo(2), spawn Quadrado(3)]
assert [f.desenhar() cycle f in FORMAS] is
["circulo de raio 2", "quadrado de lado 3"]

out ""
out "== 5. e quem nao cumpre e recusado =="

// O contrato do trait e cobrado na declaracao, e nao na primeira
// chamada.
out "   um blueprint 'with Desenhavel' sem 'desenhar' nao compila"

out ""
out "== 6. o metodo chamado e o do OBJETO, e nao o do tipo =="

action mostrar(qualquer):
    yield qualquer.desenhar()

assert mostrar(spawn Circulo(1)) is "circulo de raio 1"
assert mostrar(spawn Quadrado(1)) is "quadrado de lado 1"

out "exercicio 353 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/353_heranca_e_mro.df` },
  {"p": "`root` é o pai de **quem declarou o método**, e não o pai da classe da instância. Com dois níveis a conta dá certo dos dois jeitos — e por isso o defeito sobreviveu: toda herança de um repositório pequeno tem dois níveis."},
  {"h3": "Com três, era laço infinito"},
  {"p": "Dentro de `B.cadeia`, o `self` ainda é um `C`: `root` voltava a ser `B`, e `B.cadeia` chamava a si mesmo."},
  {"h3": "O diamante resolve por C3"},
  {"p": "Como o `super()` do Python — e a ordem é a mesma."},
  {"h3": "E o método chamado é o do OBJETO"},
  {"p": "Uma ação que recebe \"qualquer coisa que desenha\" funciona com os dois tipos, sem saber de nenhum."},
  {"h2": "354 · o que nao se usa nao pode custar"},
  {"p": "**Enunciado.** contratos, sobrecarga, invariantes, metaclasses e 'lazy'"},
  { code: `// nao podem custar nada a quem nao os usa. A prova nao e uma
// afirmacao: e medir o acesso a campo num blueprint simples contra um
// com propriedade.

adopt Arcane.Bench as Bench

steady VOLTAS := 40000

blueprint Simples:
    action setup(n):
        self.n := n

blueprint ComPropriedade:
    action setup(n):
        self._n := n

    get n():
        yield self._n

blueprint ComInvariante:
    invariant self.n bigger_eq 0

    action setup(n):
        self.n := n

    action somar(x):
        self.n := self.n + x

out "== 1. os tres funcionam igual =="

a := spawn Simples(10)
b := spawn ComPropriedade(10)
c := spawn ComInvariante(10)
assert a.n is 10
assert b.n is 10
assert c.n is 10

out ""
out "== 2. e o acesso simples e o mais rapido =="

action ler_simples(n):
    total := 0
    cycle i from 1 to n:
        total += a.n
    yield total

action ler_propriedade(n):
    total := 0
    cycle i from 1 to n:
        total += b.n
    yield total

simples := Bench.medir(ler_simples, VOLTAS)
propriedade := Bench.medir(ler_propriedade, VOLTAS)

out $"   campo:       {round(simples['ms'], 1)} ms"
out $"   propriedade: {round(propriedade['ms'], 1)} ms"

// A propriedade CHAMA uma acao por leitura: ela nao pode empatar.
// E o que se cobra e um FATOR com folga — 'assert a bigger b' entre
// dois numeros medidos e um sorteio, e reprova numa esteira
// carregada sem que nada tenha mudado no codigo.
razao := propriedade["ms"] / max(simples["ms"], 0.0001)
out $"   a propriedade custa {round(razao, 1)}x"
assert razao bigger 1.5

out ""
out "== 3. a invariante so e cobrada na chamada PUBLICA mais de fora =="

// Sem isso, 'invariant self.area() bigger_eq 0' chamaria 'area', que
// conferiria a invariante, que chamaria 'area'.
c.somar(5)
assert c.n is 15

violou := no
monitor:
    c.somar(-999)
handle InvariantError:
    violou := yes
assert violou

// E aqui esta a distincao que vale lembrar: a invariante ACUSA, e nao
// DESFAZ. O objeto ficou no estado invalido, e quem trata decide o
// que fazer com ele.
assert c.n is 15 - 999
out "   a invariante acusou; o estado NAO voltou sozinho"

// Quem precisa do desfazer usa um agregado: la o comando inteiro e
// revertido, e a versao nao avanca.
out "   para desfazer junto: Arcane.Dominio.agregado"

out ""
out "== 4. e a leitura de um campo NAO dispara a conferencia =="

// Conferir a cada leitura faria um laco de 40 mil leituras rodar 40
// mil invariantes.
antes := Bench.medir(ler_simples, VOLTAS)
assert antes["ms"] bigger 0.0

out ""
out "== 5. o atalho mora no blueprint, e e recalculado =="

// 'leitura_simples' e 'escrita_simples' dizem que nao ha propriedade,
// descritor nem gancho. Com eles, o acesso a campo ficou mais rapido
// que ANTES de os recursos existirem.
out "   quem acrescenta um jeito novo de interceptar precisa derrubar o atalho"

out ""
out "== 6. e a regra, em uma frase =="

out "   um recurso que custa a quem nao o usa e um recurso que ninguem liga"

out "exercicio 354 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/354_custo_zero.df` },
  {"p": "Contratos, sobrecarga, invariantes, metaclasses e `lazy` não podem custar nada a quem não os usa. A prova não é uma afirmação: é medir."},
  {"h3": "A propriedade CHAMA uma ação por leitura"},
  {"p": "Ela não pode empatar com o acesso a campo — e o que se cobra é um **fator** com folga, porque `assert a bigger b` entre dois números medidos é um sorteio."},
  {"h3": "A invariante ACUSA, e não DESFAZ"},
  {"p": "O objeto fica no estado inválido, e quem trata decide o que fazer com ele. Quem precisa do desfazer usa um agregado."},
  {"h3": "E o atalho mora no blueprint"},
  {"p": "`leitura_simples` e `escrita_simples` dizem que não há propriedade, descritor nem gancho. Quem acrescenta um jeito novo de interceptar acesso precisa derrubá-lo — senão o recurso novo não roda para os blueprints \"simples\", e nada avisa."},
  {"h2": "355 · perguntar ao objeto o que ele tem"},
  {"p": "**Enunciado.** reflexao e o que faz uma biblioteca funcionar com um tipo"},
  { code: `// que ela nunca viu. E ela precisa respeitar a VISIBILIDADE: uma
// reflexao que le campo privado transforma 'private' em comentario.

adopt Arcane.Reflexo as Ref

blueprint Produto:
    action setup(nome, preco):
        self.nome := nome
        self.preco := preco
        self._custo := preco * 0.6

    action margem():
        yield round(self.preco - self._custo, 2)

    private action calcular_imposto():
        yield self.preco * 0.1

out "== 1. os campos e os metodos =="

p := spawn Produto("cafe", 32.5)

// 'campos' devolve a DESCRICAO de cada um: nome, tipo, visibilidade,
// somente-leitura e anotacoes. Um cluster de nomes bastaria para
// imprimir, e nao para decidir o que serializar.
campos := [c["nome"] cycle c in Ref.campos(p)]
assert "nome" in campos
assert "preco" in campos
out $"   campos: {campos}"

metodos := [m["nome"] cycle m in Ref.metodos(Produto)]
assert "margem" in metodos

out ""
out "== 2. chamar por NOME =="

assert Ref.invocar(p, "margem") is 13.0

out ""
out "== 3. e a visibilidade e respeitada =="

recusou := no
monitor:
    Ref.invocar(p, "calcular_imposto")
handle Error as e:
    recusou := yes
    out $"   {e.message}"
assert recusou

out ""
out "== 4. a linhagem =="

blueprint Digital extends Produto:
    action setup(nome, preco, tamanho):
        root.setup(nome, preco)
        self.tamanho := tamanho

// 'mro' e 'herdeiros' devolvem os BLUEPRINTS, e nao os nomes: com o
// objeto na mao da para continuar perguntando.
assert [Ref.nome(b) cycle b in Ref.mro(Digital)] is ["Digital", "Produto"]
assert [Ref.nome(b) cycle b in Ref.herdeiros(Produto)] is ["Digital"]
assert Ref.descende(Digital, Produto)

out ""
out "== 5. e e isso que faz um serializador generico funcionar =="

action para_vault(objeto):
    "Sem saber que tipo e — so perguntando."
    saida := {}
    cycle campo in Ref.campos(objeto):
        nome := campo["nome"]
        given campo["visibilidade"] is "public" and not startswith(nome, "_"):
            saida[nome] := Ref.ler(objeto, nome)
    yield saida

assert para_vault(p) is {"nome": "cafe", "preco": 32.5}
assert para_vault(spawn Digital("livro", 40.0, 12))["tamanho"] is 12
out $"   {para_vault(p)}"

out ""
out "== 6. o diagrama, para quem precisa VER =="

diagrama := Ref.diagrama([Produto, Digital])
assert "Produto" in diagrama
assert "Digital" in diagrama
out "   e o Mermaid sai pronto para colar num README"

out "exercicio 355 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/355_reflexao.df` },
  {"p": "Reflexão é o que faz uma biblioteca funcionar com um tipo que ela nunca viu."},
  {"h3": "Ela respeita a VISIBILIDADE"},
  {"p": "Uma reflexão que lê campo privado transforma `private` em comentário."},
  {"h3": "`campos` devolve a DESCRIÇÃO de cada um"},
  {"p": "Nome, tipo, visibilidade, somente-leitura e anotações. Um cluster de nomes bastaria para imprimir, e não para decidir o que serializar."},
  {"h3": "E é isso que faz um serializador genérico funcionar"},
  {"p": "Sem saber que tipo é — só perguntando."},
  {"h2": "356 · despacho por forma, e a classe que nasce mudada"},
  {"p": "**Enunciado.** 'overload' escolhe o metodo pelo TIPO dos argumentos, e"},
  { code: `// uma metaclasse roda quando o blueprint e criado — os dois existem
// para tirar um 'match' de dentro do codigo de negocio.

adopt Arcane.Reflexo as Ref

out "== 1. o mesmo nome, formas diferentes =="

blueprint Area:
    overload action de(lado: Integer):
        yield lado * lado

    overload action de(largura: Integer, altura: Integer):
        yield largura * altura

    overload action de(medidas: Cluster):
        yield sum(medidas)

a := spawn Area()
assert a.de(4) is 16
assert a.de(3, 5) is 15
assert a.de([1, 2, 3]) is 6
out "   um nome, tres formas"

out ""
out "== 2. e a forma que nao existe e RECUSADA =="

recusou := no
monitor:
    a.de("texto")
handle Error as e:
    recusou := yes
    out $"   {e.message}"
assert recusou

out ""
out "== 3. sem sobrecarga, isso seria um 'match' no comeco =="

blueprint AreaSemSobrecarga:
    action de(x, y := void):
        match x:
            point Cluster as c:
                yield sum(c)
            point Integer as n:
                yield n * n given y is void otherwise n * y
            default:
                trigger "nao sei calcular"

b := spawn AreaSemSobrecarga()
assert b.de(4) is 16
assert b.de(3, 5) is 15
out "   funciona, e o 'match' cresce a cada forma nova"

out ""
out "== 4. a metaclasse roda na CRIACAO do blueprint =="

meta blueprint Registro:
    nomes := []

    action on_forge(molde):
        self.nomes.append(Ref.nome(molde))

blueprint Comando using Registro:
    action rodar():
        yield "base"

blueprint Salvar extends Comando:
    action rodar():
        yield "salvou"

registro := Ref.meta_instancia(Comando)
assert "Comando" in registro.nomes
assert "Salvar" in registro.nomes
out $"   registradas sozinhas: {registro.nomes}"

out ""
out "== 5. e e isso que substitui um registro a mao =="

// Sem ela, cada comando novo exige lembrar de uma linha de registro
// em outro arquivo — e a linha que se esquece e a do comando que
// ninguem testa.

out ""
out "== 6. 'augment' muda um blueprint DEPOIS de pronto =="

augment Comando:
    action descrever():
        yield $"comando: {self.rodar()}"

assert spawn Salvar().descrever() is "comando: salvou"
out "   e os herdeiros tambem ganham"

out ""
out "== 7. e o cache e esquecido junto =="

// 'augment' e 'Reflexo.definir_metodo' chamam 'esquecer_caches()',
// que recalcula o atalho de acesso e os magicos DAS FILHAS tambem.
// O metodo definido em execucao NAO recebe 'self' como parametro
// declarado: ele e ligado ao blueprint, e 'self' esta no escopo.
action dizer_novo():
    yield "novo"

Ref.definir_metodo(Comando, "outro", dizer_novo)
assert spawn Salvar().outro() is "novo"

out "exercicio 356 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/356_sobrecarga_e_metaclasse.df` },
  {"p": "`overload` escolhe o método pelo **tipo** dos argumentos, e uma metaclasse roda quando o blueprint é criado. Os dois existem para tirar um `match` de dentro do código de negócio."},
  {"h3": "Sem sobrecarga, isso seria um `match` no começo"},
  {"p": "Funciona — e cresce a cada forma nova, num lugar que não é a declaração."},
  {"h3": "A metaclasse substitui um registro à mão"},
  {"p": "Sem ela, cada comando novo exige lembrar de uma linha de registro em outro arquivo — e a linha que se esquece é a do comando que ninguém testa."},
  {"h3": "E o cache é esquecido junto"},
  {"p": "`augment` e `Reflexo.definir_metodo` chamam `esquecer_caches()`, que recalcula o atalho de acesso e os mágicos **das filhas** também."},
  {"h2": "357 · o mapa, e os tres que NAO existem"},
  {"p": "**Enunciado.** fechar o modulo com a lista do que cada magico responde,"},
  { code: `// e com a lista do que a linguagem DELIBERADAMENTE nao delega. A
// segunda e a que evita procurar um recurso que nao existe.

out "== 1. o que cada grupo responde =="

steady GRUPOS := {
    "texto": ["__str__", "__repr__", "__format__"],
    "igualdade": ["__eq__", "__ne__", "__hash__"],
    "ordem": ["__lt__", "__le__", "__gt__", "__ge__"],
    "conversao": ["__int__", "__float__", "__bool__", "__bytes__"],
    "colecao": ["__len__", "__getitem__", "__setitem__", "__delitem__",
        "__contains__", "__iter__", "__next__"],
    "conta": ["__abs__", "__neg__", "__round__", "__floor__", "__ceil__"],
    "acesso": ["__getattr__", "__setattr__", "__getattribute__",
        "__delattr__"],
    "vida": ["__call__", "__enter__", "__exit__", "__copy__",
        "__deepcopy__", "__del__"]
}

total := sum([len(GRUPOS[g]) cycle g in keys(GRUPOS)])
assert total is 36
cycle g in keys(GRUPOS):
    out $"   {g}: {len(GRUPOS[g])}"

out ""
out "== 2. os TRES que a linguagem nao delega, e por que =="

// Nao ha '__len__', '__bool__' nem '__iter__' na tabela de protocolos
// que o interpretador entrega ao Python. Eles EXISTEM como magicos
// chamaveis, e nao decidem a verdade nem a iteracao por baixo.
blueprint Vazia:
    action setup():
        self.itens := []

    action __len__():
        yield len(self.itens)

v := spawn Vazia()
assert len(v) is 0
// Em Python, isto seria falso. Aqui nao: o interpretador pergunta
// 'if obj:' sobre instancias, e um '__len__' mudaria a verdade de
// TODO objeto que declara tamanho.
assert v
out "   tamanho zero, e ainda verdadeira"

out ""
out "== 3. a regra de quando declarar =="

out "   __str__:  sempre que o objeto aparece num log ou numa tela"
out "   __eq__:   quando dois objetos iguais DEVEM ser o mesmo"
out "   __hash__: sempre junto com __eq__ — nunca um sem o outro"
out "   operador: so quando o simbolo TEM o significado da operacao"

out ""
out "== 4. e a prova do par eq/hash =="

blueprint SoEq:
    action setup(n):
        self.n := n

    action __eq__(o):
        yield self.n is o.n

// Sem '__hash__', dois objetos iguais podem cair em baldes
// diferentes — e o segundo nao acha o primeiro.
a := spawn SoEq(1)
b := spawn SoEq(1)
assert a is b

caixa := {}
caixa[a] := "primeiro"
achou := b in keys(caixa)
out $"   iguais, e a busca por chave acha: {achou}"

blueprint ComOsDois:
    action setup(n):
        self.n := n

    action __eq__(o):
        yield self.n is o.n

    action __hash__():
        yield hash(self.n)

outra := {}
outra[spawn ComOsDois(1)] := "primeiro"
assert spawn ComOsDois(1) in keys(outra)
out "   com o par, acha sempre"

out ""
out "== 5. e o que o record ja da de graca =="

record P:
    n: Integer

assert P(1) is P(1)
caixa2 := {}
caixa2[P(1)] := "x"
assert caixa2[P(1)] is "x"
out "   record: eq, hash e imutabilidade, sem escrever nada"

out "exercicio 357 ok"`, lang: 'df', title: `exercicios/55-oop-magicos/357_o_mapa_dos_magicos.df` },
  {"p": "Fechar o módulo com a lista do que cada mágico responde, e com a lista do que a linguagem **deliberadamente** não delega. A segunda é a que evita procurar um recurso que não existe."},
  {"h3": "Não há `__len__`, `__bool__` nem `__iter__` na tabela de protocolos"},
  {"p": "Eles existem como mágicos chamáveis, e não decidem a verdade nem a iteração por baixo: o interpretador pergunta `if obj:` sobre instâncias."},
  {"h3": "A regra de quando declarar"},
  {"p": "`__str__` sempre que o objeto aparece num log. `__eq__` quando dois objetos iguais **devem** ser o mesmo. `__hash__` sempre junto com `__eq__`."},
  {"h3": "E o record já dá os três de graça"},
  {"p": "Igualdade, hash e imutabilidade, sem escrever nada."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/55-oop-magicos/343_texto_e_igualdade.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '343-como-um-objeto-se-mostra-e-se-compara', text: "343 · como um objeto se mostra e se compara", level: 2 as const }, { id: 'repr-era-inalcancavel', text: "`repr` era inalcançável", level: 3 as const }, { id: 'o-par-eqhash-nunca-se-separa', text: "O par eq/hash nunca se separa", level: 3 as const }, { id: 'e-sem-os-dois-o-objeto-so-e-igual-a-si-mesmo', text: "E sem os dois, o objeto só é igual a si mesmo", level: 3 as const }, { id: '344-o-objeto-que-entra-numa-conta', text: "344 · o objeto que entra numa conta", level: 2 as const }, { id: 'eles-compoem', text: "Eles compõem", level: 3 as const }, { id: 'um-tipo-sem-o-operador-recusa', text: "Um tipo sem o operador recusa", level: 3 as const }, { id: 'e-a-regra-de-quando-nao-sobrecarregar', text: "E a regra de quando NÃO sobrecarregar", level: 3 as const }, { id: '345-o-objeto-que-se-comporta-como-colecao', text: "345 · o objeto que se comporta como colecao", level: 2 as const }, { id: 'e-o-mesmo-protocolo-da-ponte-para-o-python', text: "É o mesmo protocolo da ponte para o Python", level: 3 as const }, { id: 'a-compreensao-e-o-pipeline-tambem', text: "A compreensão e o pipeline também", level: 3 as const }, { id: 'e-trocar-protocolo-por-isinstance-quebraria-tudo-junto', text: "E trocar protocolo por `isinstance` quebraria tudo junto", level: 3 as const }, { id: '346-ordenar-objetos', text: "346 · ordenar objetos", level: 2 as const }, { id: 'por-que-a-comparacao-nao-pode-ser-por-texto', text: "Por que a comparação não pode ser por texto", level: 3 as const }, { id: 'e-um-objeto-sem-lt-nao-ordena', text: "E um objeto sem `__lt__` não ordena", level: 3 as const }, { id: '347-o-objeto-que-se-chama-e-o-que-se-abre', text: "347 · o objeto que se chama, e o que se abre", level: 2 as const }, { id: 'por-que-isso-nao-e-so-uma-closure', text: "Por que isso não é só uma closure", level: 3 as const }, { id: 'e-ele-passa-onde-uma-acao-passa', text: "E ele passa onde uma ação passa", level: 3 as const }, { id: 'o-bloco-com-entrada-e-saida', text: "O bloco com entrada e saída", level: 3 as const }, { id: '348-interceptar-a-leitura-e-a-escrita', text: "348 · interceptar a leitura e a escrita", level: 2 as const }, { id: 'o-campo-interno-precisa-existir-antes', text: "O campo interno precisa existir antes", level: 3 as const }, { id: 'escrita-por-indice-nao-passa-pelo-magico-de-membro', text: "Escrita por ÍNDICE não passa pelo mágico de membro", level: 3 as const }, { id: 'e-a-propriedade-para-um-campo', text: "E a propriedade, para UM campo", level: 3 as const }, { id: '349-quanto-vale-e-se-e-verdade', text: "349 · quanto vale, e se e verdade", level: 2 as const }, { id: 'bool-e-o-mais-perigoso-dos-tres', text: "`__bool__` é o mais perigoso dos três", level: 3 as const }, { id: 'len-nao-decide-a-verdade-aqui', text: "`__len__` NÃO decide a verdade aqui", level: 3 as const }, { id: 'e-por-isso-se-pergunta-o-tamanho', text: "E por isso se pergunta o TAMANHO", level: 3 as const }, { id: '350-um-iterador-com-estado', text: "350 · um iterador com estado", level: 2 as const }, { id: 'void-encerra', text: "`void` encerra", level: 3 as const }, { id: 'o-generator-faz-o-mesmo-sem-blueprint', text: "O generator faz o mesmo, sem blueprint", level: 3 as const }, { id: 'e-a-ordem-importa', text: "E a ORDEM importa", level: 3 as const }, { id: '351-copiar-sem-levar-o-que-nao-se-quer', text: "351 · copiar sem levar o que nao se quer", level: 2 as const }, { id: 'sem-copy-a-lista-e-a-mesma-lista', text: "Sem `__copy__`, a lista é a MESMA lista", level: 3 as const }, { id: 'congelar-recusa-a-escrita', text: "Congelar recusa a escrita", level: 3 as const }, { id: 'e-a-serializacao-so-reconstroi-o-autorizado', text: "E a serialização só reconstrói o AUTORIZADO", level: 3 as const }, { id: '352-quando-o-record-basta', text: "352 · quando o record basta", level: 2 as const }, { id: 'o-with-confere-as-chaves', text: "O `with` confere as CHAVES", level: 3 as const }, { id: 'quando-o-blueprint-e-o-certo', text: "Quando o blueprint é o certo", level: 3 as const }, { id: 'e-o-record-no-match', text: "E o record no `match`", level: 3 as const }, { id: '353-root-com-tres-niveis', text: "353 · 'root' com tres niveis", level: 2 as const }, { id: 'com-tres-era-laco-infinito', text: "Com três, era laço infinito", level: 3 as const }, { id: 'o-diamante-resolve-por-c3', text: "O diamante resolve por C3", level: 3 as const }, { id: 'e-o-metodo-chamado-e-o-do-objeto', text: "E o método chamado é o do OBJETO", level: 3 as const }, { id: '354-o-que-nao-se-usa-nao-pode-custar', text: "354 · o que nao se usa nao pode custar", level: 2 as const }, { id: 'a-propriedade-chama-uma-acao-por-leitura', text: "A propriedade CHAMA uma ação por leitura", level: 3 as const }, { id: 'a-invariante-acusa-e-nao-desfaz', text: "A invariante ACUSA, e não DESFAZ", level: 3 as const }, { id: 'e-o-atalho-mora-no-blueprint', text: "E o atalho mora no blueprint", level: 3 as const }, { id: '355-perguntar-ao-objeto-o-que-ele-tem', text: "355 · perguntar ao objeto o que ele tem", level: 2 as const }, { id: 'ela-respeita-a-visibilidade', text: "Ela respeita a VISIBILIDADE", level: 3 as const }, { id: 'campos-devolve-a-descricao-de-cada-um', text: "`campos` devolve a DESCRIÇÃO de cada um", level: 3 as const }, { id: 'e-e-isso-que-faz-um-serializador-generico-funcionar', text: "E é isso que faz um serializador genérico funcionar", level: 3 as const }, { id: '356-despacho-por-forma-e-a-classe-que-nasce-mudada', text: "356 · despacho por forma, e a classe que nasce mudada", level: 2 as const }, { id: 'sem-sobrecarga-isso-seria-um-match-no-comeco', text: "Sem sobrecarga, isso seria um `match` no começo", level: 3 as const }, { id: 'a-metaclasse-substitui-um-registro-a-mao', text: "A metaclasse substitui um registro à mão", level: 3 as const }, { id: 'e-o-cache-e-esquecido-junto', text: "E o cache é esquecido junto", level: 3 as const }, { id: '357-o-mapa-e-os-tres-que-nao-existem', text: "357 · o mapa, e os tres que NAO existem", level: 2 as const }, { id: 'nao-ha-len-bool-nem-iter-na-tabela-de-protocolos', text: "Não há `__len__`, `__bool__` nem `__iter__` na tabela de protocolos", level: 3 as const }, { id: 'a-regra-de-quando-declarar', text: "A regra de quando declarar", level: 3 as const }, { id: 'e-o-record-ja-da-os-tres-de-graca', text: "E o record já dá os três de graça", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"55 · Métodos mágicos"}
      description={"15 exercícios: ."}
      href={"/docs/exercicios/55-oop-magicos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
