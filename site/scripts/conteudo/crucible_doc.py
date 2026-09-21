"""Crucible — o framework de testes."""

PAGINAS = [
{
"href": "/docs/crucible",
"title": "Crucible — testes",
"description": "No cadinho o metal é provado no fogo. DataForge molda, Kiln assa, Crucible prova.",
"blocos": [
 {"p": "**Crucible** é o framework de testes da linguagem. Tem sintaxe própria — dez palavras contextuais — e 59 matchers."},
 {"code": """crucible "Calculadora":

    setup:
        base := 10

    trial "soma dois números":
        expect 2 + 2 is 4

    trial "recusa divisão por zero":
        expect(lambda => 1 / 0).to_raise(DivisionByZeroError)

    trial "vê o setup":
        expect base is 10""", "lang": "df"},
 {"code": """$ dataforge crucible

  ✓ Calculadora  3 trial(s), 84µs

  ────────────────────────────────────────
  3 passou   em 100µs""", "lang": "bash"},

 {"h2": "Por que um framework próprio"},
 {"p": "O `dataforge test` que já existia roda arquivos `*_test.df` e conta `assert`. Isso responde \"passou?\" e nada mais. Quando falha, a mensagem diz que uma expressão deu falso — não o que se esperava, o que veio, nem qual dos quarenta casos daquele arquivo era."},
 {"p": "O Crucible responde as outras perguntas:"},
 {"code": """$ dataforge crucible

  ✗ Carrinho  4 trial(s), 1.2ms
      ✗ soma o frete

  ────────────────────────────────────────

  1) Carrinho > soma o frete
     testes/carrinho.df:18

     devia ser {"total": 130, "frete": 30}, e veio
     {"total": 100, "frete": 30}

     ~ "total": esperava 130, veio 100""", "lang": "bash"},
 {"p": "Comparar dois vaults de dez chaves lendo os dois inteiros não se faz — o Crucible aponta a chave que difere."},

 {"h2": "As garantias"},
 {"list": [
   "**Um trial não vaza para o próximo.** Cada um roda no próprio quadro de escopo, com as fixtures reconstruídas. Um teste que passa sozinho e falha na suíte seria bug do framework.",
   "**A limpeza roda mesmo com falha.** `teardown` e a parte da fixture depois do `provide` rodam em qualquer saída.",
   "**A ordem não importa.** Com `--aleatorio` a suíte embaralha; um teste que depende de ordem falha ali, e não seis meses depois.",
   "**A diferença é mostrada, não descrita.**"]},

 {"h2": "Isolamento, na prática"},
 {"code": """crucible "Isolamento":
    setup:
        contador := 0

    trial "o primeiro soma":
        contador := contador + 1
        expect contador is 1

    trial "o segundo vê o valor original":
        expect contador is 0""", "lang": "df"},
 {"p": "Os dois passam. O `setup` roda antes de cada trial, num quadro novo — o que o primeiro escreveu não existe para o segundo."},

 {"h2": "As dez palavras"},
 {"table": {"head": ["Palavra", "O que abre"], "rows": [
   ["`crucible`", "uma suíte; suítes aninham"],
   ["`trial`", "um caso de teste"],
   ["`expect`", "uma cobrança"],
   ["`setup`", "roda antes de cada trial (`setup all` uma vez)"],
   ["`teardown`", "roda depois de cada trial"],
   ["`fixture`", "preparo e limpeza no mesmo lugar"],
   ["`provide`", "entrega o valor preparado, e divide a fixture"],
   ["`tagged`", "marca, para filtrar depois"],
   ["`pending`", "não roda, e o relatório diz por quê"],
   ["`bench`", "mede em vez de cobrar"]]}},
 {"callout": {"tipo": "nota", "titulo": "Nenhuma delas é reservada", "texto": "`setup` é o nome do construtor de blueprint, e `expect` e `trial` são nomes bons demais para tirar de quem escreve. Elas só valem dentro de um bloco `crucible`; fora dele seguem sendo identificadores livres."}},

 {"h2": "Rodando"},
 {"code": """dataforge crucible                      # tudo
dataforge crucible -v                   # mostra também o que passou
dataforge crucible --filtro=carrinho    # só os que casam
dataforge crucible --tag=rapido         # só os marcados
dataforge crucible --sem-tag=rede       # pula os marcados
dataforge crucible --aleatorio          # embaralha a ordem
dataforge crucible --semente=42         # repete um embaralhamento
dataforge crucible --repetir=10         # cada trial 10 vezes
dataforge crucible --prazo=500          # falha o que passar de 500ms
dataforge crucible --fail-fast          # para na primeira falha
dataforge crucible --formato=junit --out=r.xml
dataforge crucible --matchers           # lista os 59""", "lang": "bash"},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/crucible/matchers", "title": "Os 79 matchers", "desc": "igualdade, tipos, coleções, erros, desempenho"},
   {"href": "/docs/crucible/fixtures", "title": "Fixtures e ganchos", "desc": "preparo, limpeza e por que elas ficam juntas"},
   {"href": "/docs/crucible/dubles", "title": "Dublês", "desc": "mock, spy e stub — e a diferença entre eles"},
   {"href": "/docs/crucible/propriedades", "title": "Teste por propriedade", "desc": "a regra em vez dos casos, com contraexemplo encolhido"},
   {"href": "/docs/crucible/relatorios", "title": "Relatórios e CI", "desc": "texto, JUnit, JSON, TAP — e benchmark com p95"},
   {"href": "/docs/crucible/cenarios", "title": "Cenários", "desc": "concorrência, relógio que anda, e um HTTP que você controla"},
   {"href": "/docs/crucible/mutacao", "title": "Contratos e mutação", "desc": "o mesmo teste em duas implementações, e se o teste testa mesmo"}]},
]},

{
"href": "/docs/crucible/matchers",
"title": "Os matchers",
"description": "59 formas de cobrar um valor — e a mensagem que cada uma produz.",
"blocos": [
 {"h2": "Duas formas"},
 {"p": "A curta, para os comuns; a encadeada, para o resto. As duas viram a mesma cobrança:"},
 {"code": """crucible "Formas":
    trial "curta":
        expect 2 + 2 is 4

    trial "encadeada":
        expect(2 + 2).to_be(4).to_be_even().to_be_positive()""", "lang": "df"},
 {"p": "A curta existe porque quatro de cada cinco cobranças são igualdade, e `.to_be(...)` em volta delas só acrescenta ruído."},
 {"table": {"head": ["Forma curta", "Equivale a"], "rows": [
   ["`expect x is 4`", "`expect(x).to_be(4)`"],
   ["`expect x isnt 4`", "`expect(x).nao().to_be(4)`"],
   ["`expect n bigger 5`", "`expect(n).to_be_greater_than(5)`"],
   ["`expect n smaller 5`", "`expect(n).to_be_less_than(5)`"],
   ["`expect s matches \"^a\"`", "`expect(s).to_match(\"^a\")`"],
   ["`expect xs has 3`", "`expect(xs).to_contain(3)`"],
   ["`expect x`", "cobra que valha como verdadeiro"]]}},

 {"h2": "Igualdade"},
 {"code": """crucible "Igualdade":
    trial "valor":
        expect(4).to_be(4)

    trial "identidade":
        xs := [1, 2]
        expect(xs).to_be_exactly(xs)

    trial "ponto flutuante":
        // 0.1 + 0.2 não dá 0.3 em nenhuma linguagem com IEEE 754
        expect(0.1 + 0.2).to_be_close_to(0.3)

    trial "faixa":
        expect(7).to_be_between(1, 10)""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Nunca `to_be` com float", "texto": "Cobrar igualdade exata de ponto flutuante é escrever um teste que falha por motivo errado. `to_be_close_to` existe para isso."}},

 {"h2": "Verdade e vazio"},
 {"table": {"head": ["Matcher", "Passa quando"], "rows": [
   ["`to_be_true`", "é exatamente `yes`"],
   ["`to_be_false`", "é exatamente `no`"],
   ["`to_be_truthy`", "vale como verdadeiro num `given`"],
   ["`to_be_falsy`", "vale como falso"],
   ["`to_be_void`", "é `void`"],
   ["`to_exist`", "não é `void`"],
   ["`to_be_empty`", "não tem nenhum item"]]}},

 {"h2": "Tipos"},
 {"code": """crucible "Tipos":
    trial "pelo nome":
        expect(42).to_be_a("Integer")

    trial "pelos específicos":
        expect(42).to_be_integer().to_be_number()
        expect("a").to_be_text()
        expect([1]).to_be_cluster()
        expect({}).to_be_vault()
        expect(lambda x: x).to_be_action()""", "lang": "df"},
 {"p": "`to_be_instance_of` aceita a linhagem inteira — um herdeiro passa:"},
 {"code": """blueprint Animal:
    action f():
        yield 1

blueprint Cachorro extends Animal:
    action g():
        yield 2

crucible "Linhagem":
    trial "o herdeiro é da mãe também":
        expect(spawn Cachorro()).to_be_instance_of("Animal")""", "lang": "df"},

 {"h2": "Números"},
 {"table": {"head": ["Matcher", "", "Matcher", ""], "rows": [
   ["`to_be_greater_than`", "maior", "`to_be_positive`", "> 0"],
   ["`to_be_less_than`", "menor", "`to_be_negative`", "< 0"],
   ["`to_be_at_least`", "≥", "`to_be_zero`", "= 0"],
   ["`to_be_at_most`", "≤", "`to_be_even`", "par"],
   ["`to_be_divisible_by`", "sem resto", "`to_be_odd`", "ímpar"],
   ["`to_be_finite`", "nem ∞ nem NaN", "`to_be_nan`", "é NaN"]]}},

 {"h2": "Texto"},
 {"code": """crucible "Texto":
    trial "bordas":
        expect("abacate").to_start_with("aba").to_end_with("ate")

    trial "regex":
        expect("ana@x.com").to_match("^[^@]+@[^@]+$")

    trial "conteúdo":
        expect("abacate").to_contain_text("baca")

    trial "forma":
        expect("ABC").to_be_uppercase()
        expect("   ").to_be_blank()""", "lang": "df"},

 {"h2": "Coleções"},
 {"code": """crucible "Coleções":
    trial "conteúdo":
        expect([1, 2, 3]).to_contain(2).to_have_length(3)
        expect([1, 2, 3]).to_contain_all([1, 3])
        expect([1, 2, 3]).to_contain_any([9, 2])

    trial "vault":
        expect({"a": 1}).to_have_key("a")
        expect({"a": 1, "b": 2}).to_have_keys(["a", "b"])

    trial "ordem e unicidade":
        expect([1, 2, 3]).to_be_sorted()
        expect([1, 2, 3]).to_be_unique()
        expect([3, 1, 2]).to_have_same_items([1, 2, 3])

    trial "todos e algum":
        expect([2, 4]).to_all_satisfy(lambda n: n % 2 is 0)
        expect([1, 2]).to_any_satisfy(lambda n: n % 2 is 0)""", "lang": "df"},
 {"p": "`to_have_field` serve para vault, record e instância — o teste não deveria precisar saber qual dos três o valor é:"},
 {"code": """record Ponto:
    x: Integer
    y: Integer

crucible "Campo":
    trial "vault":
        expect({"nome": "Ana"}).to_have_field("nome", "Ana")

    trial "record":
        expect(Ponto(1, 2)).to_have_field("x", 1)""", "lang": "df"},

 {"h2": "Erros"},
 {"code": """action sacar_demais():
    trigger "saldo insuficiente"

crucible "Erros":
    trial "levanta o tipo esperado":
        expect(lambda => 1 / 0).to_raise(DivisionByZeroError)

    trial "a família também serve":
        expect(lambda => 1 / 0).to_raise(RuntimeError)

    trial "e a mensagem":
        // o corpo de um lambda é uma EXPRESSÃO; para uma instrução,
        // declare uma ação
        expect(sacar_demais).to_raise(mensagem := "saldo")

    trial "não levanta nada":
        expect(lambda => 1 + 1).to_not_raise()""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`to_raise` precisa de uma ação", "texto": "`expect(1 / 0)` já estourou antes de chegar ao matcher. É `expect(lambda => 1 / 0)` — sem os parênteses da chamada, senão o erro acontece antes de o Crucible poder observá-lo. O matcher recusa um valor já avaliado, dizendo isso."}},

 {"h2": "Desempenho e saída"},
 {"code": """action cumprimentar():
    out "olá"

crucible "Outros":
    trial "prazo":
        expect(lambda => 1 + 1).to_finish_within(100)

    trial "imprime":
        expect(cumprimentar).to_print("olá")""", "lang": "df"},

 {"h2": "Invertendo"},
 {"p": "`nao()` inverte **o próximo** matcher — e só ele, para não deixar um estado invertido pendurado:"},
 {"code": """crucible "Negação":
    trial "inverte só o próximo":
        expect([1, 2, 3]).nao().to_contain(9).to_contain(2)""", "lang": "df"},

 {"h2": "Falhando de propósito"},
 {"code": """crucible "Manual":
    trial "condição própria":
        Crucible.check(2 + 2 is 4, "a soma quebrou")

    trial "caminho impossível":
        given no:
            Crucible.fail("não deveria chegar aqui")
        expect yes""", "lang": "df"},
 {"h2": "O que mudou — `to_change`"},
 {"p": "É o matcher que mais falta num framework de teste, porque ele cobre o caso que um `assert` simples cobre mal: o **efeito colateral**. Sem ele se escreve `antes := saldo()`, a ação, `depois := saldo()` e um assert — quatro linhas em que a do meio pode falhar em silêncio."},
 {"code": """expect(lambda => conta.depositar(10)).to_change(
    lambda => conta.saldo()).por(10)

expect(lambda => conta.sacar(500)).to_change(
    lambda => conta.saldo()).de_para(100, -400)

expect(lambda => olhar(conta)).to_not_change(lambda => conta.saldo())""", "lang": "df"},
 {"p": "`to_not_change` é um matcher **próprio**, e não `nao().to_change(...)`: encadear `.por(...)` depois de \"não mudou\" não quer dizer nada."},

 {"h2": "Quem foi chamado — os dublês"},
 {"code": """banco := Crucible.spy(banco_real)
servico.processar(pedido)

expect(banco).to_have_been_called("salvar")
expect(banco).to_have_been_called_once("cobrar")
expect(banco).to_have_been_called_with(pedido.id)
expect(banco).to_have_been_called_in_order("abrir", "salvar", "fechar")
expect(banco).to_have_never_been_called("apagar")""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "`once` não é `called`",
              "texto": "\"Foi chamado\" passa com três chamadas — e três chamadas de `cobrar()` é uma cobrança duplicada, o tipo de bug que ninguém perdoa."}},
 {"p": "A **ordem** admite outras chamadas no meio, de propósito: cobrar a sequência exata quebraria a cada chamada nova que o código passasse a fazer, e um teste que quebra sem o comportamento mudar é um teste que será apagado."},

 {"h2": "Forma, e não valor"},
 {"table": {"head": ["Matcher", "Para quê"], "rows": [
   ["`to_match_vault(parcial)`", "as chaves dadas batem; as outras são ignoradas"],
   ["`to_have_shape(forma)`", "cada chave tem o **tipo** dito, sem olhar o valor"],
   ["`to_satisfy(regra, texto)`", "a saída de emergência: qualquer regra que você escreva"],
   ["`to_be_one_of(lista)`", "o valor está entre estes"],
   ["`to_contain_exactly(itens)`", "os mesmos itens, em qualquer ordem"],
   ["`to_be_subset_of(maior)`", "tudo o que há aqui está lá"],
   ["`to_be_ordered_by(campo)`", "ordenado por um campo de vault, record ou instância"],
   ["`to_round_trip(ida, volta)`", "serializar e desserializar devolve o mesmo"],
   ["`to_be_within_percent(v, p)`", "perto em **proporção**, e não em valor absoluto"],
   ["`to_raise_matching(padrao)`", "o erro tem uma mensagem que casa"],
   ["`to_emit(lista)` · `to_emit_first(lista)`", "um gerador finito, e um infinito"]]}},
 {"p": "`to_match_vault` existe porque cobrar o vault inteiro obriga a escrever no teste campos que ele não testa — e no dia em que um campo novo aparece, dez testes quebram sem nenhum comportamento ter mudado."},
 {"p": "`to_be_within_percent` existe porque uma tolerância absoluta serve mal a grandezas de escalas diferentes: `0,01` é muito para um percentual e nada para um saldo."},
 {"p": "E `to_emit` é separado de `to_emit_first` porque fundir as duas faria `to_emit([0,1,2])` passar sobre uma série que **nunca acaba** — e a afirmação \"produz [0,1,2]\" seria falsa. Um `stream action` infinito é comum na linguagem."},

 {"p": "A lista completa: `dataforge crucible --matchers`."},
]},

{
"href": "/docs/crucible/fixtures",
"title": "Fixtures e ganchos",
"description": "Preparo e limpeza no mesmo lugar — e por que isso não é detalhe.",
"blocos": [
 {"h2": "Os ganchos"},
 {"code": """crucible "Ganchos":
    setup all:
        // uma vez, antes de tudo
        origem := "arquivo.csv"

    setup:
        // antes de CADA trial, num quadro novo
        base := 10

    teardown:
        // depois de cada trial, mesmo se ele falhar
        expect yes

    trial "usa o setup":
        expect base is 10""", "lang": "df"},
 {"p": "Os ganchos rodam da raiz para dentro: o `setup` mais geral prepara o terreno, o mais específico ajusta. A ordem inversa faria o ajuste ser sobrescrito pelo preparo."},

 {"h2": "Fixture: preparo e limpeza juntos"},
 {"p": "`provide` divide a fixture em duas metades. O que vem antes prepara; o que vem depois limpa:"},
 {"code": """crucible "Banco":
    fixture banco():
        adopt Forge
        db := Forge.conectar(":memory:")
        Forge.executar(db, "create table t (id integer primary key)")
        provide db
        Forge.fechar(db)

    trial "usa o banco":
        expect banco() exists""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Por que juntos", "texto": "Escrever preparo e limpeza no mesmo lugar é o que impede a limpeza de ser esquecida — que é o modo mais comum de uma suíte passar a depender de ordem. Um recurso aberto e não fechado derruba o próximo teste por um motivo que não é dele."}},

 {"h2": "Suítes aninhadas"},
 {"p": "Uma suíte dentro de outra herda os ganchos e as fixtures da de fora:"},
 {"code": """crucible "Loja":
    setup:
        estoque := 100

    crucible "Venda":
        trial "vê o estoque do pai":
            expect estoque is 100

    crucible "Devolução":
        setup:
            devolvidos := 5

        trial "vê os dois":
            expect estoque + devolvidos is 105""", "lang": "df"},
 {"p": "No relatório, o caminho aparece inteiro: `Loja > Devolução > vê os dois`."},

 {"h2": "Modificadores do trial"},
 {"code": """crucible "Modificadores":
    trial "marcado" tagged "rápido", "unitário":
        expect 1 is 1

    trial "adiado" pending "esperando a API do fornecedor":
        expect 1 is 2

    trial "com prazo" within 100:
        expect 1 is 1

    trial "repetido" repeat 5:
        expect 1 is 1

    trial "é par" over [2, 4, 6]:
        expect caso % 2 is 0""", "lang": "df"},
 {"table": {"head": ["Modificador", "Faz"], "rows": [
   ["`tagged \"a\", \"b\"`", "marca, para `--tag` e `--sem-tag`"],
   ["`pending \"motivo\"`", "não roda; o relatório mostra o motivo"],
   ["`only`", "com um `only` na suíte, **só** os focados rodam"],
   ["`repeat n`", "roda n vezes — instabilidade aparece"],
   ["`within ms`", "falha se passar do prazo"],
   ["`over [a, b, c]`", "um trial por linha, com `caso` ligado"]]}},

 {"h2": "Trial parametrizado"},
 {"p": "`over` gera um resultado por linha, e o nome do trial mostra qual falhou:"},
 {"code": """crucible "Tabela":
    trial "dobra certo" over [[1, 2], [2, 4], [3, 6]]:
        expect caso[0] * 2 is caso[1]""", "lang": "df"},
 {"p": "Se o segundo caso falhar, o relatório diz `dobra certo [[2, 4]]` — não \"um dos três\"."},

 {"h2": "Foco"},
 {"p": "Com um `only` em qualquer trial da suíte, só os focados rodam. É para depurar, não para versionar:"},
 {"code": """crucible "Depurando":
    trial "este" only:
        expect 1 is 1

    trial "aquele não roda":
        expect 1 is 2""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`only` esquecido é perigoso", "texto": "Um `only` commitado faz o CI rodar um teste e reportar verde. Vale uma regra de revisão — ou um `grep only` antes do push."}},
]},

{
"href": "/docs/crucible/dubles",
"title": "Dublês",
"description": "Mock, spy e stub — e por que aqui são um objeto só.",
"blocos": [
 {"p": "Um dublê finge ser outro objeto e anota o que lhe pediram. Serve para três coisas que costumam se confundir:"},
 {"table": {"head": ["", "O que faz"], "rows": [
   ["**stub**", "devolve o que você mandou devolver"],
   ["**spy**", "deixa passar para o real e anota as chamadas"],
   ["**mock**", "as duas, mais expectativas sobre as chamadas"]]}},
 {"p": "Aqui é **um objeto só**, porque a diferença entre eles é como se usa, não o que são — e obrigar a escolher o nome certo antes de escrever o teste atrapalha mais que ajuda."},

 {"h2": "Programando respostas"},
 {"code": """crucible "Dublês":
    trial "devolve o programado":
        m := Crucible.mock("servico")
        m.quando("buscar").devolve([1, 2, 3])
        expect m.buscar() is [1, 2, 3]

    trial "em sequência":
        m := Crucible.mock()
        m.quando("proximo").devolve_em_sequencia([1, 2, 3])
        expect [m.proximo(), m.proximo(), m.proximo()] is [1, 2, 3]

    trial "levanta o programado":
        m := Crucible.mock()
        m.quando("falhar").levanta("indisponível")
        expect(lambda => m.falhar()).to_raise()""", "lang": "df"},

 {"h2": "Verificando as chamadas"},
 {"code": """crucible "Chamadas":
    trial "anota tudo":
        m := Crucible.mock("api")
        m.buscar(1)
        m.buscar(2)
        m.salvar("x")

        expect m.vezes("buscar") is 2
        expect m.foi_chamado("salvar") is yes
        expect m.foi_chamado("apagar") is no
        expect m.chamado_com("salvar", "x") is yes
        expect m.argumentos_de("buscar") is [[1], [2]]""", "lang": "df"},

 {"h2": "Spy: deixa passar e anota"},
 {"code": """blueprint Calculadora:
    action dobro(x):
        yield x * 2

crucible "Spy":
    trial "o real roda, e a chamada fica registrada":
        espiao := Crucible.spy(spawn Calculadora())
        expect espiao.dobro(4) is 8
        expect espiao.chamado_com("dobro", 4) is yes""", "lang": "df"},

 {"h2": "Stub: só as respostas"},
 {"code": """crucible "Stub":
    trial "programado de uma vez":
        s := Crucible.stub({"buscar": [1, 2], "contar": 2})
        expect s.buscar() is [1, 2]
        expect s.contar() is 2""", "lang": "df"},

 {"h2": "Onde isso encaixa no projeto"},
 {"p": "Dublê é o que torna [inversão de dependência](/docs/oop/solid) prática. Um serviço que recebe o repositório por parâmetro se testa sem banco nenhum:"},
 {"code": """trait Repositorio:
    action salvar(nome)

blueprint Servico:
    action setup(repositorio):
        self.repositorio := repositorio

    action cadastrar(nome):
        given len(nome) smaller 2:
            trigger "nome curto demais"
        yield self.repositorio.salvar(nome)

crucible "Cadastro":
    trial "salva o que passa na validação":
        repo := Crucible.mock("repositorio")
        repo.quando("salvar").devolve("Ana")

        s := spawn Servico(repo)
        expect s.cadastrar("Ana") is "Ana"
        expect repo.chamado_com("salvar", "Ana") is yes

    trial "não salva o que não passa":
        repo := Crucible.mock("repositorio")
        s := spawn Servico(repo)

        expect(lambda => s.cadastrar("A")).to_raise()
        expect repo.foi_chamado("salvar") is no""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Cobre o que NÃO aconteceu", "texto": "O segundo trial cobra que o repositório **não** foi chamado. Sem o dublê, verificar isso exigiria olhar o banco — e um teste que precisa de banco para verificar uma regra de nome está testando a coisa errada."}},

 {"h2": "Congelando o relógio"},
 {"p": "Todo teste que toca data e hora falha uma vez por ano, na virada, se não congelar:"},
 {"code": """crucible "Tempo":
    trial "instante fixo":
        relogio := Crucible.freeze_time(1700000000)
        expect yes
        relogio.liberar()""", "lang": "df"},
]},

{
"href": "/docs/crucible/propriedades",
"title": "Teste por propriedade",
"description": "A regra em vez dos casos — e o contraexemplo encolhido até caber numa linha.",
"blocos": [
 {"p": "Em vez de escrever trinta casos à mão, descreve-se a **regra que vale para todos** e deixa-se a máquina procurar o contraexemplo."},
 {"code": """crucible "Propriedades":
    trial "inverter duas vezes volta ao original":
        Crucible.forall(
            Crucible.clusters(Crucible.integers(0, 100)),
            lambda xs: xs.reversed().reversed() is xs)

    trial "ordenar não muda o tamanho":
        Crucible.forall(
            Crucible.clusters(),
            lambda xs: len(sorted(xs)) is len(xs))""", "lang": "df"},

 {"h2": "Os geradores"},
 {"table": {"head": ["Gerador", "Produz"], "rows": [
   ["`Crucible.integers(min, max)`", "inteiros na faixa"],
   ["`Crucible.floats(min, max)`", "reais na faixa"],
   ["`Crucible.texts(tamanho)`", "textos até o tamanho"],
   ["`Crucible.booleans()`", "`yes` e `no`"],
   ["`Crucible.clusters(item, max)`", "clusters do gerador dado"],
   ["`Crucible.vaults(valor, max)`", "vaults"],
   ["`Crucible.one_of([a, b])`", "um dos valores"]]}},
 {"p": "Geradores se combinam:"},
 {"code": """crucible "Combinando":
    trial "só pares":
        pares := Crucible.integers(0, 1000).mapear(lambda n: n * 2)
        Crucible.forall(pares, lambda n: n % 2 is 0)

    trial "com filtro":
        positivos := Crucible.integers(-100, 100)
            .filtrar(lambda n: n bigger 0)
        Crucible.forall(positivos, lambda n: n bigger 0)""", "lang": "df"},

 {"h2": "O contraexemplo é encolhido"},
 {"p": "Um contraexemplo de novecentos dígitos prova que há bug e não ajuda a achar. Quando a propriedade falha, o Crucible **encolhe** até o menor valor que ainda falha:"},
 {"code": """$ dataforge crucible

  1) Listas > nunca passa de dois itens

     a propriedade falhou depois de 7 caso(s).
         menor contraexemplo: [0, 0, 0]""", "lang": "bash"},
 {"p": "Sem o encolhimento, o contraexemplo seria a lista aleatória de 27 itens que falhou primeiro."},

 {"h2": "Quando vale"},
 {"list": [
   "**Ida e volta.** Serializar e desserializar deve devolver o original. Codificar e decodificar. Comprimir e descomprimir.",
   "**Invariantes.** Ordenar não muda o tamanho. Somar zero não muda o valor. Uma soma é comutativa.",
   "**Comparação com uma implementação óbvia.** A versão rápida deve concordar com a versão lenta e evidente."]},
 {"code": """action soma_rapida(xs):
    yield sum(xs)

action soma_obvia(xs):
    total := 0
    cycle x in xs:
        total += x
    yield total

crucible "Equivalência":
    trial "as duas somas concordam":
        Crucible.forall(
            Crucible.clusters(Crucible.integers(-100, 100)),
            lambda xs: soma_rapida(xs) is soma_obvia(xs))""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Não substitui os casos", "texto": "Teste por propriedade acha o que você não pensou. Casos escritos à mão documentam o que você pensou. Os dois servem, e o segundo lê melhor."}},
]},

{
"href": "/docs/crucible/relatorios",
"title": "Relatórios, benchmark e CI",
"description": "Quatro formatos, e a medição que mostra o p95 em vez de só a média.",
"blocos": [
 {"h2": "Os formatos"},
 {"code": """dataforge crucible                        # texto, colorido
dataforge crucible --formato=junit --out=r.xml
dataforge crucible --formato=json --out=r.json
dataforge crucible --formato=tap""", "lang": "bash"},
 {"table": {"head": ["Formato", "Para"], "rows": [
   ["texto", "ler no terminal"],
   ["JUnit XML", "GitHub Actions, GitLab, Jenkins — todos leem"],
   ["JSON", "processar por programa"],
   ["TAP 13", "o formato mais simples e portável que existe"]]}},
 {"p": "O JUnit existe porque integrar com cada CI exigiria que cada um aprendesse o formato do Crucible — e nenhum vai aprender."},

 {"h2": "A ordem do relatório"},
 {"p": "Primeiro o mapa, uma linha por suíte. Depois cada falha com espaço para respirar. Quem roda a suíte quer saber se está verde; quando não está, quer o detalhe de cada uma — e não rolar a tela procurando o vermelho no meio do verde."},

 {"h2": "Benchmark"},
 {"code": """crucible "Desempenho":
    bench "soma de mil" times 100:
        total := 0
        cycle i from 1 to 1000:
            total += i""", "lang": "df"},
 {"code": """    ⏱  soma de mil: 0.0821ms media, 0.0798ms mediana,
       p95 0.0954ms, 12180 ops/s""", "lang": "text"},
 {"callout": {"tipo": "dica", "titulo": "Média sozinha engana", "texto": "Uma pausa do coletor de lixo no meio de mil voltas move a média e não aparece nela. A mediana e o p95 contam a história inteira — e o p95 é o que o usuário de um serviço web sente."}},
 {"p": "Pela biblioteca, com mais controle:"},
 {"code": """adopt Crucible

m := Crucible.benchmark("soma", lambda => sum(range(1000)), 500)
out m["media_ms"], m["mediana_ms"], m["p95_ms"], m["ops_por_s"]""", "lang": "df"},

 {"h2": "Ordem aleatória"},
 {"p": "Um teste que só passa porque outro rodou antes é uma bomba-relógio. `--aleatorio` a detona cedo:"},
 {"code": """dataforge crucible --aleatorio
# ordem aleatoria, semente 1738 (--semente=1738 repete)

dataforge crucible --aleatorio --semente=1738   # reproduz exatamente""", "lang": "bash"},
 {"p": "A semente aparece no relatório justamente para a falha ser reproduzível — uma ordem aleatória que não se repete é impossível de depurar."},

 {"h2": "Instabilidade"},
 {"code": """dataforge crucible --repetir=20""", "lang": "bash"},
 {"p": "Roda cada trial vinte vezes. Um teste que passa às vezes depende de tempo, de ordem, ou de estado que sobrou — e é melhor descobrir isso agora que numa madrugada de plantão."},

 {"h3": "O estado que sobra: três fontes"},
 {"p": "\"Estado que sobrou\" soa abstrato até virar uma suíte que passa sozinha e falha em conjunto. As três fontes, e o que desfaz cada uma:"},
 {"table": {"head": ["O que sobra", "Como desfazer"], "rows": [
   ["uma linha no banco", "`Crucible.banco(db)` — abre transação e a desfaz no fim do trial"],
   ["uma variável de ambiente", "`OS.unset_env(nome)` — devolve `yes` se ela existia"],
   ["um arquivo temporário", "uma **subpasta própria** e `IO.remove_tree` nela"]]}},
 {"code": """adopt Crucible
adopt Arcane.OS as OS
adopt Arcane.IO as IO

crucible "com estado externo":
    setup:
        pasta := $"{OS.temp_dir()}/meu-teste-{randint(100000, 999999)}"
        IO.mkdir(pasta)
        OS.set_env("MODO", "teste")

    teardown:
        OS.unset_env("MODO")
        IO.remove_tree(pasta)

    trial "usa o ambiente e a pasta":
        expect OS.get_env("MODO") is "teste"
""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`OS.temp_dir()` é a pasta do SISTEMA", "texto": "Ela é compartilhada com todo processo da máquina. Escrever direto nela deixa lixo, e `IO.remove_tree(OS.temp_dir())` destrói o temporário dos outros programas — o exercício 157 fazia isso na primeira versão. Sempre uma subpasta com nome único."}},
 {"p": "O ambiente é do **processo**, e um processo roda mais de um programa: o `dataforge test` cria um interpretador por arquivo. Uma variável definida e não removida muda o que o arquivo seguinte vê — foi assim que o exercício 160 imprimia 77 variáveis na primeira execução e 78 na segunda."},

 {"h2": "No CI"},
 {"code": """name: testes
on: [push, pull_request]

jobs:
  crucible:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh
      - run: dataforge check src/ --strict
      - run: dataforge big-o src/ --strict
      - run: dataforge crucible --formato=junit --out=resultados.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: resultados
          path: resultados.xml""", "lang": "text"},
 {"p": "`dataforge crucible` sai com código 1 quando algo falha, então o passo reprova sozinho."},

 {"h2": "Lendo o resultado por programa"},
 {"code": """adopt Crucible

Crucible.suite("Exemplo", lambda => [
    Crucible.trial("passa", lambda => Crucible.expect(1).to_be(1))
])

resumo := Crucible.run()
out resumo["passou"], resumo["falhou"], resumo["verde"]

cycle r in Crucible.results():
    out r["nome"], r["estado"], r["duracao"]""", "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/crucible/cenarios",
"title": "Cenários: concorrência, tempo e rede",
"description": "Provar que o mutex segura, que o cache vence amanhã, e o que o cliente faz com um 503.",
"blocos": [
 {"p": "Os matchers respondem *\"o valor é o esperado?\"*. Estas quatro ferramentas respondem uma pergunta anterior: **em que mundo o código está rodando?** Elas montam o cenário — e não comparam nada."},

 {"h2": "Concorrência: a corrida que o `check` só avisa"},
 {"p": "A linguagem **não sincroniza sozinha**, e isso está documentado: duas threads escrevendo no mesmo nome perdem atualizações, em silêncio. O `check` avisa sobre o padrão (`escrita-concorrente`) — mas avisar não é provar, e um teste que roda a ação uma vez por thread não detecta nada, porque a janela é estreita."},
 {"code": """action test_o_contador_perde_sem_mutex():
    contador := spawn Contador()
    r := Crucible.corrida(lambda => contador.somar(),
                          threads := 4, voltas := 5000,
                          leitor := lambda => contador.valor())
    expect(r.perdeu()).to_be_true()
    out $"perdeu {r.perdidas()} de {r.esperado}"

action test_com_mutex_nao_perde():
    contador := spawn ContadorProtegido()
    r := Crucible.corrida(lambda => contador.somar(),
                          threads := 4, voltas := 5000,
                          leitor := lambda => contador.valor())
    expect(r.perdeu()).to_be_false()""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "A barreira é o ponto",
              "texto": "As threads largam **juntas**. Sem isso, a primeira costuma terminar antes de a última começar — e o teste passa justamente no código que tem a corrida."}},
 {"table": {"head": ["", "O que diz"], "rows": [
   ["`r.perdeu()`", "`yes` quando o total não bate"],
   ["`r.perdidas()`", "quantas atualizações sumiram"],
   ["`r.erros`", "o que estourou **dentro** da thread — sem isto, morreria calado"],
   ["`r.para_vault()`", "tudo, para um relatório"]]}},

 {"h2": "Determinismo: o mesmo dado dá o mesmo resultado?"},
 {"code": """r := Crucible.determinismo(lambda => montar_relatorio(vendas), vezes := 5)
expect(r["estavel"]).to_be_true()""", "lang": "df"},
 {"p": "É a propriedade que um relatório precisa ter e que quase nada tem: um `id()` na chave de um cache, uma ordem de vault, um `random` sem semente — os três passam no teste que roda **uma** vez."},
 {"p": "A comparação é por **foto estrutural**, e não por referência: duas listas iguais são objetos diferentes, e comparar referência diria \"instável\" para código perfeitamente determinístico."},

 {"h2": "O relógio que anda"},
 {"p": "`freeze_time` congela; o relógio **anda**. A diferença importa para testar o que depende de *intervalo* — um cache com validade, um recuo, um prazo — porque congelado eles nunca vencem, e com o relógio de verdade o teste precisa dormir."},
 {"code": """action test_o_cache_vence_em_trinta_minutos():
    Crucible.com_relogio(lambda r => conferir_validade(r),
                         "2026-09-20 10:00:00")

action conferir_validade(r):
    cache.guardar("cotacao", 5.42)
    r.avancar(minutos := 29)
    expect(cache.obter("cotacao")).to_be(5.42)
    r.avancar(minutos := 2)
    expect(cache.obter("cotacao")).to_be_void()""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Use `com_relogio`, e não `ligar` à mão",
              "texto": "Ele desliga o relógio **mesmo quando o trial estoura**. Um relógio ligado que escapa faz todos os trials seguintes verem o tempo parado — e a suíte passa a falhar em lugares que não têm nada a ver."}},

 {"h2": "Um HTTP que você controla"},
 {"p": "Um dublê substitui o cliente e prova que o código chamou um método. O **servidor falso** sobe um socket de verdade e prova que o código fala HTTP direito — cabeçalho, corpo, status — e o que ele faz com um 503. São perguntas diferentes, e a segunda é a que quebra em produção."},
 {"code": """action test_o_cliente_repete_duas_vezes_e_desiste():
    s := Crucible.servidor_falso()
    s.falhar("/precos", 503, vezes := 2)
    s.responder("/precos", {"dolar": 5.42})

    resposta := meu_cliente.buscar(s.url("/precos"))

    expect(resposta["dolar"]).to_be(5.42)
    expect(s.quantos("/precos")).to_be(3)
    s.parar()""", "lang": "df"},
 {"p": "O `vezes` é o que torna testável o *\"falha duas vezes e na terceira funciona\"* — o comportamento que um cliente com recuo promete e quase nunca tem teste."},
 {"table": {"head": ["Programar", "Perguntar"], "rows": [
   ["`s.responder(rota, corpo, status)`", "`s.pedidos(rota)` — tudo o que chegou"],
   ["`s.falhar(rota, status, vezes)`", "`s.ultimo(rota)` — o último, com corpo e cabeçalhos"],
   ["`s.demorar(segundos)`", "`s.quantos(rota)`"],
   ["`s.url(caminho)`", "`s.limpar()` · `s.parar()`"]]}},
 {"p": "Uma rota que ninguém programou responde **404**, e não um corpo vazio: um 200 sem conteúdo faria o teste falhar num ponto distante, dizendo que o dado veio errado."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/crucible/mutacao",
"title": "Contratos e mutação",
"description": "O mesmo teste valendo para duas implementações, e a pergunta que a cobertura não responde.",
"blocos": [
 {"h2": "Contrato: um trait, muitas implementações"},
 {"p": "Duas implementações do mesmo trait costumam ter **dois** conjuntos de testes, escritos em épocas diferentes, cobrindo coisas diferentes. A segunda passa nos testes dela e quebra no uso — porque o que ela não cumpre é justamente o que só o teste da primeira cobria."},
 {"code": """action guarda_e_le(a):
    a.guardar("x", 1)
    expect(a.ler("x")).to_be(1)

action apaga(a):
    a.guardar("x", 1)
    a.apagar("x")
    expect(a.ler("x")).to_be_void()

provas := Crucible.contrato("Armazem", [
    {"nome": "guarda e le", "prova": guarda_e_le},
    {"nome": "apaga", "prova": apaga}
])

provas.para("em memoria", lambda => spawn EmMemoria())
provas.para("em disco", lambda => spawn EmDisco("/tmp/x"))
provas.cobrar()""", "lang": "df"},
 {"p": "`cobrar()` levanta nomeando **qual implementação** falhou em **qual caso**. A alternativa — um resumo dizendo \"2 falhas\" — manda procurar em dois lugares."},

 {"h2": "Mutação: o teste testa mesmo?"},
 {"p": "Cobertura responde *\"esta linha rodou?\"*. Ela não responde *\"se esta linha estivesse errada, alguém reclamaria?\"* — e as duas divergem justamente onde importa: um teste que chama a função e **não confere o resultado** dá 100% de cobertura e zero de proteção."},
 {"p": "A mutação responde a segunda pergunta: troca um operador no código, roda a suíte, e vê se ela falha. Se a suíte **passar**, aquele teste não testava aquilo. O mutante é chamado de *sobrevivente*, e cada sobrevivente é um buraco com endereço."},
 {"code": """r := Crucible.mutar("src/calculo.df",
                    lambda => Crucible.run()["falhas"] bigger 0)

out Crucible.relatorio_de_mutacao(r)
expect(r["sobreviventes"]).to_be_empty()""", "lang": "df"},
 {"code": """  src/calculo.df
  7/9 mutantes pegos (78%)

  sobreviveram — ninguém reclamou destas trocas:
    linha 12: bigger_eq → bigger  (afrouxa um limite: '>=' vira '>')
      yield idade bigger_eq 18
    linha 27: * → /  (troca a operação)
      yield valor * desconto""", "lang": "text"},
 {"p": "A primeira sobrevivente diz que nenhum teste passa exatamente 18 — o caso de borda. A segunda, que ninguém confere o valor com desconto."},
 {"table": {"head": ["Decisão", "Por quê"], "rows": [
   ["**uma** troca por mutante", "com duas, um teste que pega a primeira esconde a segunda"],
   ["fronteira de palavra", "`bigger` é pedaço de `bigger_eq`; sem ela o relatório descreveria uma troca e faria outra"],
   ["comentário e texto não mutam", "mudar um literal ali não muda comportamento, e o mutante sobreviveria sempre"],
   ["suíte que **estoura** conta como pego", "o código quebrado não passou despercebido, que é a única pergunta"],
   ["o arquivo volta num `finally`", "um código-fonte silenciosamente alterado é o pior desfecho de uma ferramenta de teste"]]}},
 {"callout": {"tipo": "atencao", "titulo": "O custo, dito de frente",
              "texto": "Cada mutante roda a suíte inteira. Com quarenta mutantes e uma suíte de dois segundos, são oitenta segundos — por isso o `limite` existe e por isso isto **não** roda no CI de cada commit. É uma ferramenta de auditoria, e não um portão."}},

 {"h2": "As onze trocas"},
 {"p": "Cada uma é uma mudança que um humano faria por engano, e que um teste de verdade pegaria. Trocas que quase sempre produzem erro de sintaxe ou laço infinito ficam de fora: elas gastam uma rodada da suíte para não dizer nada."},
 {"table": {"head": ["Troca", "O que ela simula"], "rows": [
   ["`bigger_eq` → `bigger`", "afrouxa um limite — o caso de borda"],
   ["`smaller_eq` → `smaller`", "o mesmo, do outro lado"],
   ["`bigger` ↔ `smaller`", "inverte a comparação"],
   ["`is not` → `is`", "inverte a igualdade"],
   ["`and` ↔ `or`", "troca o conectivo"],
   ["`+` ↔ `-` · `*` → `/`", "troca a operação"],
   ["`yes` → `no`", "inverte um literal lógico"]]}},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/crucible/cenarios", "title": "Cenários", "desc": "Concorrência, relógio e um HTTP que você controla."},
   {"href": "/docs/crucible/matchers", "title": "Os matchers", "desc": "As 79 cobranças, por família."},
   {"href": "/docs/tecnicas/cobertura", "title": "Cobertura", "desc": "O que a cobertura mede — e o que ela não mede."},
   {"href": "/docs/crucible/relatorios", "title": "Relatórios e CI", "desc": "JUnit, JSON, TAP e benchmark."}]},
]},
]
