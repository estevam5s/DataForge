// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "24 · Banco de dados",
  description: "8 exercícios: Forge: conexão, consultas, transações e ORM.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 24`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[203](#203-conectar-e-consultar)", "**Conectar e consultar**", "abra um banco, crie uma tabela e leia de volta."], ["[204](#204-construtor-de-consultas)", "**Construtor de consultas**", "monte consultas encadeando chamadas, sem escrever SQL."], ["[205](#205-injecao-de-sql-e-por-que-ela-nao-acontece-aqui)", "**Injecao de SQL, e por que ela nao acontece aqui**", "tente derrubar uma tabela por um campo de busca."], ["[206](#206-transacoes)", "**Transacoes**", "transfira saldo entre contas, e garanta que nao suma dinheiro."], ["[207](#207-modelos-e-validacao)", "**Modelos e validacao**", "declare um modelo, e deixe que ele recuse dado invalido."], ["[208](#208-relacoes-e-o-problema-do-n1)", "**Relacoes, e o problema do N+1**", "carregue os pedidos de cem usuarios em duas consultas."], ["[209](#209-migracoes)", "**Migracoes**", "evolua o esquema sem perder o que ja esta gravado."], ["[210](#210-pool-de-conexoes)", "**Pool de conexoes**", "reaproveite conexoes, e garanta que elas voltem."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "203 · Conectar e consultar"},
  {"p": "**Enunciado.** abra um banco, crie uma tabela e leia de volta."},
  { code: `// O Forge fala com cinco motores pela mesma interface. Trocar o motor
// troca a URL, e mais nada — e por isso o exercicio usa ':memory:',
// que nao precisa de servidor nenhum.

adopt Forge

db := Forge.conectar(":memory:")
out "dialeto:", db.dialeto
assert db.dialeto is "sqlite", "a URL decide o motor"

Forge.executar(db, """
    create table produtos (
        id integer primary key autoincrement,
        nome text not null,
        preco real
    )
""")
assert "produtos" in Forge.tabelas(db), "a tabela foi criada"

// 'executar' devolve quantas linhas mudaram
mudou := Forge.executar(db,
    "insert into produtos (nome, preco) values (?, ?)", ["Teclado", 250.0])
assert mudou is 1, "uma linha inserida"

// 'consultar' devolve uma lista de vaults, um por linha
linhas := Forge.consultar(db, "select * from produtos")
out linhas
assert len(linhas) is 1, "uma linha de volta"
assert linhas[0]["nome"] is "Teclado", "lida pelo nome da coluna, nao pelo indice"

// O tipo volta convertido: preco e Float, nao texto
assert type(linhas[0]["preco"]) is "Float", "o tipo sobrevive a ida e volta"
assert type(linhas[0]["id"]) is "Integer", "idem"

// 'primeiro' quando so interessa uma
p := Forge.primeiro(db, "select * from produtos where nome = ?", ["Teclado"])
assert p["preco"] is 250.0, "achou"

vazio := Forge.primeiro(db, "select * from produtos where nome = ?", ["nada"])
assert vazio is void, "sem resultado devolve void, nao erro"

Forge.fechar(db)
out "ok"`, lang: 'df', title: `exercicios/24-banco-de-dados/203_conectar.df` },
  {"h3": "Conceitos"},
  {"p": "O **Forge** fala com cinco motores pela mesma interface: PostgreSQL, MySQL, MariaDB, MongoDB, Redis e SQLite. Trocar o motor troca a URL, e mais nada."},
  { code: `db := Forge.conectar("postgres://usuario:senha@localhost/app")
db := Forge.conectar("mysql://root@localhost/app")
db := Forge.conectar("dados.db")          // SQLite
db := Forge.conectar(":memory:")          // SQLite, sem arquivo`, lang: 'df' },
  {"p": "O exercício usa `:memory:` porque ele não precisa de servidor nenhum — e é também o banco de teste ideal: cada execução começa limpa."},
  {"table": {"head": ["Função", "Devolve"], "rows": [["`Forge.consultar`", "uma lista de vaults, um por linha"], ["`Forge.executar`", "quantas linhas mudaram"], ["`Forge.primeiro`", "a primeira linha, ou `void`"]]}},
  {"h3": "O que observar"},
  {"p": "**As linhas voltam como vault, não como tupla.** `linha[\"nome\"]` continua funcionando quando alguém acrescenta uma coluna; `linha[0]` não."},
  {"p": "**Os tipos sobrevivem à ida e volta.** `preco` volta como `Float`, não como texto. Sem isso, `preco * 2` concatenaria em vez de multiplicar."},
  {"p": "**Sem resultado devolve `void`, não erro.** `Forge.primeiro` de uma busca que não achou nada é uma resposta legítima, não uma falha."},
  {"h3": "Armadilhas"},
  {"list": ["`Forge.executar` devolve **quantas linhas mudaram**, não as linhas. Para"]},
  {"p": "receber as linhas de volta num INSERT, use `RETURNING` (PostgreSQL) ou o ORM."},
  {"list": ["Uma conexão aberta e não fechada segura um recurso. Em programa curto isso"]},
  {"p": "não importa; num servidor, importa muito — ver o exercício 208."},
  {"h3": "Relacionados"},
  {"list": ["[202 — Construtor de consultas](202_construtor_de_consultas.md)", "[205 — Modelos e validação](205_modelos_e_validacao.md)", "[208 — Pool de conexões](208_pool_e_conexoes.md)"]},
  {"h2": "204 · Construtor de consultas"},
  {"p": "**Enunciado.** monte consultas encadeando chamadas, sem escrever SQL."},
  { code: `// O construtor resolve tres coisas que o SQL a mao nao resolve: o
// dialeto de cada banco, a condicao que so as vezes existe, e o
// identificador citado. E ele nunca poe um valor no texto.

adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, """
    create table usuarios (
        id integer primary key autoincrement,
        nome text, cidade text, idade integer
    )
""")

Forge.de(db, "usuarios").inserir([
        {"nome": "Ana", "cidade": "Floripa", "idade": 30},
        {"nome": "Bia", "cidade": "Recife", "idade": 25},
        {"nome": "Cid", "cidade": "Floripa", "idade": 41}
    ])
assert Forge.de(db, "usuarios").contar() is 3, "tres inseridos de uma vez"

// Filtros encadeados
maduros := Forge.de(db, "usuarios")
    .onde("idade", ">=", 30)
    .ordenar("idade", "desc")
    .buscar()
out [u["nome"] cycle u in maduros]
assert len(maduros) is 2, "dois com 30 ou mais"
assert maduros[0]["nome"] is "Cid", "o mais velho primeiro"

// 'onde_em' vira IN, com um parametro por item
floripa := Forge.de(db, "usuarios").onde_em("cidade", ["Floripa"]).buscar()
assert len(floripa) is 2, "dois em Floripa"

// Lista vazia nao gera 'in ()', que e erro de sintaxe em quase todo banco
nenhum := Forge.de(db, "usuarios").onde_em("cidade", []).buscar()
assert len(nenhum) is 0, "lista vazia devolve nada, sem quebrar"

// Agregados
assert Forge.de(db, "usuarios").somar("idade") is 96, "30+25+41"
assert Forge.de(db, "usuarios").media("idade") is 32.0, "a media"
assert Forge.de(db, "usuarios").maximo("idade") is 41, "o maior"
assert Forge.de(db, "usuarios").existe() is yes, "tem alguem"

// Paginacao: a pagina 1 e a primeira, nao a zero
pagina := Forge.de(db, "usuarios").paginar(1, 2)
assert pagina["total"] is 3, "o total nao muda com a pagina"
assert len(pagina["linhas"]) is 2, "dois por pagina"
assert pagina["paginas"] is 2, "duas paginas"
assert pagina["tem_proxima"] is yes, "ha uma segunda"

// 'quando' aplica o filtro so se a condicao valer
action procurar(db, cidade):
    yield Forge.de(db, "usuarios")
        .quando(cidade, lambda c => c.onde("cidade", cidade))
        .contar()

assert procurar(db, "") is 3, "sem filtro, todos"
assert procurar(db, "Recife") is 1, "com filtro, um"

out "ok"`, lang: 'df', title: `exercicios/24-banco-de-dados/204_construtor_de_consultas.df` },
  {"h3": "Conceitos"},
  {"p": "Escrever SQL à mão continua valendo. O construtor resolve três coisas que o SQL à mão não resolve:"},
  {"p": "1. **Dialeto.** `?` no SQLite e MySQL, `$1` no PostgreSQL. A mesma consulta roda nos dois. 2. **Condição opcional.** Um filtro que só existe quando o usuário preencheu o campo — o código mais chato e mais propenso a erro que existe. 3. **Identificador citado.** Uma coluna chamada `order` quebraria a consulta."},
  { code: `Forge.de(db, "usuarios")
    .onde("idade", ">=", 18)
    .onde_em("cidade", ["Floripa", "Recife"])
    .ordenar("nome")
    .limite(20)
    .buscar()`, lang: 'df' },
  {"h3": "O que observar"},
  {"p": "**A lista vazia não gera `in ()`.** Isso é erro de sintaxe em quase todo banco. `onde_em(\"x\", [])` vira uma condição sempre falsa, que é o que a lista vazia significa."},
  {"p": "**A página 1 é a primeira.** Off-by-one em paginação é clássico: quem chama pensa em \"página 1\", e o banco pensa em \"pule 0\"."},
  {"p": "**`quando` evita o `if` em volta da consulta.** Sem ele, um filtro opcional vira concatenação de texto com `and` na hora certa."},
  {"h3": "Armadilhas"},
  {"list": ["`paginar` faz **duas** consultas: uma para contar, outra para trazer. Se o"]},
  {"p": "total não importa, `.pagina(n, 20).buscar()` faz uma só."},
  {"list": ["`.buscar()` traz tudo. Numa tabela grande sem `.limite()`, isso carrega a"]},
  {"p": "tabela inteira na memória."},
  {"h3": "Relacionados"},
  {"list": ["[201 — Conectar e consultar](201_conectar.md)", "[203 — Injeção de SQL](203_injecao_de_sql.md)"]},
  {"h2": "205 · Injecao de SQL, e por que ela nao acontece aqui"},
  {"p": "**Enunciado.** tente derrubar uma tabela por um campo de busca."},
  { code: `// Injecao de SQL e o bug mais explorado da historia do software. O
// Forge o torna impossivel POR CONSTRUCAO: o construtor nao tem como
// por um valor no texto da consulta.

adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, """
    create table usuarios (
        id integer primary key autoincrement,
        nome text
    )
""")
Forge.de(db, "usuarios").inserir([{"nome":"Ana"}, {"nome":"Bia"}])

// O classico: um nome que fecha a string e emenda outro comando
malicioso := "'; drop table usuarios; --"

Forge.de(db, "usuarios").inserir({"nome": malicioso})
assert "usuarios" in Forge.tabelas(db), "a tabela continua la"
assert Forge.de(db, "usuarios").contar() is 3, "e o texto virou um nome comum"

// A busca tambem: o valor e comparado, nao executado
achados := Forge.de(db, "usuarios").onde("nome", malicioso).buscar()
assert len(achados) is 1, "encontrou o registro cujo nome e aquele texto"
out "guardado como texto:", achados[0]["nome"]

// SQL escrito a mao TAMBEM parametriza, desde que use '?'
Forge.executar(db, "insert into usuarios (nome) values (?)", [malicioso])
assert Forge.de(db, "usuarios").contar() is 4, "seguro do mesmo jeito"
assert "usuarios" in Forge.tabelas(db), "a tabela sobreviveu"

// A lista de operadores tambem e fechada: um operador vindo de
// variavel seria outro caminho de injecao
monitor:
    Forge.de(db, "usuarios").onde("nome", "; drop table usuarios; --", 1)
    assert no, "devia ter recusado"
handle QueryError as e:
    out "operador recusado:", e.message
    assert "operator" in e.message, "a mensagem explica"

assert "usuarios" in Forge.tabelas(db), "a tabela continua viva no fim"
out "ok"`, lang: 'df', title: `exercicios/24-banco-de-dados/205_injecao_de_sql.df` },
  {"h3": "Conceitos"},
  {"p": "Injeção de SQL é o bug mais explorado da história do software. Ele acontece quando um valor vindo do usuário entra no **texto** da consulta:"},
  { code: `-- o que o programa monta, concatenando:
select * from usuarios where nome = ''; drop table usuarios; --'`, lang: 'text' },
  {"p": "O Forge o torna impossível **por construção**: o construtor não tem como pôr um valor no texto. Valores viram parâmetros, sempre — e o banco os trata como dado, nunca como comando."},
  {"h3": "O que observar"},
  {"p": "**Não é disciplina de quem escreve.** Numa linguagem onde a concatenação é possível, todo programador precisa lembrar de não fazê-la, sempre, em todo lugar. Aqui não há o que lembrar."},
  {"p": "**A lista de operadores é fechada.** `.onde(\"x\", operador, v)` só aceita os operadores conhecidos. Um operador vindo de variável seria outro caminho de injeção, e ele está fechado pelo mesmo motivo."},
  {"p": "**O SQL à mão também é seguro**, desde que use `?` e passe os valores separados."},
  {"h3": "Armadilhas"},
  {"list": ["`onde_cru(sql, valores)` existe para o que o construtor não cobre. O SQL vai"]},
  {"p": "**como escrito**; os valores continuam parâmetros. Nunca concatene entrada do usuário no texto que você passa a ela."},
  {"list": ["Nome de **tabela** e de **coluna** não podem ser parâmetros — nenhum banco"]},
  {"p": "permite. Se eles vierem do usuário, valide contra uma lista fechada."},
  {"h3": "Relacionados"},
  {"list": ["[202 — Construtor de consultas](202_construtor_de_consultas.md)", "[Segurança](https://dataforge-lang.vercel.app/docs/seguranca)"]},
  {"h2": "206 · Transacoes"},
  {"p": "**Enunciado.** transfira saldo entre contas, e garanta que nao suma dinheiro."},
  { code: `// Uma transferencia sao duas escritas. Se a segunda falhar depois da
// primeira, o dinheiro desaparece. A transacao garante que as duas
// aconteçam, ou nenhuma.

adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, """
    create table contas (
        id integer primary key,
        dono text,
        saldo real
    )
""")
Forge.de(db, "contas").inserir([
        {"id": 1, "dono": "Ana", "saldo": 100.0},
        {"id": 2, "dono": "Bia", "saldo": 50.0}
    ])

action saldo_de(db, id):
    yield Forge.de(db, "contas").onde("id", id).primeiro()["saldo"]

action transferir(db, de, para, valor):
    given saldo_de(db, de) smaller valor:
        trigger "saldo insuficiente"
    Forge.de(db, "contas").onde("id", de).incrementar("saldo", 0 - valor)
    Forge.de(db, "contas").onde("id", para).incrementar("saldo", valor)
    yield yes

// A transferencia que da certo
Forge.transacao(db, lambda c => transferir(c, 1, 2, 30.0))
assert saldo_de(db, 1) is 70.0, "saiu de uma"
assert saldo_de(db, 2) is 80.0, "entrou na outra"

total_antes := saldo_de(db, 1) + saldo_de(db, 2)

// A que falha no meio: nada fica
monitor:
    Forge.transacao(db, lambda c => transferir(c, 1, 2, 1000.0))
    assert no, "devia ter falhado"
handle e:
    out "recusada:", e.message

assert saldo_de(db, 1) + saldo_de(db, 2) is total_antes,
"o total nao mudou — nenhuma das duas escritas ficou"
assert saldo_de(db, 1) is 70.0, "a conta de origem esta intacta"

// 'incrementar' soma NO BANCO, sem ler antes.
// Ler-somar-gravar perde atualizacoes quando duas conexoes fazem isso
// ao mesmo tempo; deixar a soma com o banco nao perde.
Forge.de(db, "contas").onde("id", 1).incrementar("saldo", 5.0)
assert saldo_de(db, 1) is 75.0, "somou no banco"

out "ok"`, lang: 'df', title: `exercicios/24-banco-de-dados/206_transacoes.df` },
  {"h3": "Conceitos"},
  {"p": "Uma transferência são duas escritas: tirar de uma conta, pôr na outra. Se a segunda falhar depois da primeira, o dinheiro desaparece."},
  {"p": "A transação garante que as duas aconteçam, ou nenhuma:"},
  { code: `Forge.transacao(db, lambda c => transferir(c, 1, 2, 30.0))`, lang: 'df' },
  {"p": "Se o corpo falhar, tudo é desfeito."},
  {"h3": "O que observar"},
  {"p": "**Use a forma com bloco.** `comecar()` com um `confirmar()` esquecido segura locks até a conexão cair — é o motivo mais comum de um banco travar em produção. `Forge.transacao` confirma no fim e desfaz na falha, sempre."},
  {"p": "**`incrementar` soma no banco.** Ler, somar e gravar perde atualizações quando duas conexões fazem isso ao mesmo tempo:"},
  { code: `conexão A lê 100    conexão B lê 100
A soma 10 → 110     B soma 20 → 120
A grava 110         B grava 120     ← os 10 de A sumiram`, lang: 'text' },
  {"p": "`incrementar` manda `saldo = saldo + ?` para o banco, e o banco resolve."},
  {"h3": "Armadilhas"},
  {"list": ["Uma transação aberta segura locks. Mantenha-as curtas: fazer uma chamada HTTP"]},
  {"p": "no meio de uma transação é o jeito mais fácil de travar um banco."},
  {"list": ["Com `SERIALIZABLE`, prepare-se para `TransactionError` por falha de"]},
  {"p": "serialização — e para tentar de novo. É o preço da garantia."},
  {"h3": "Relacionados"},
  {"list": ["[201 — Conectar e consultar](201_conectar.md)", "[208 — Pool de conexões](208_pool_e_conexoes.md)"]},
  {"h2": "207 · Modelos e validacao"},
  {"p": "**Enunciado.** declare um modelo, e deixe que ele recuse dado invalido."},
  { code: `// Um modelo descreve a tabela E o que vale nela. A validacao junta
// TODOS os problemas antes de reclamar: um formulario que aponta um
// erro por vez faz o usuario submeter cinco vezes.

adopt Forge

db := Forge.conectar(":memory:")

Usuario := Forge.modelo("Usuario", {
        "id": {"tipo": "Serial"},
        "email": {"tipo": "Texto", "obrigatorio": yes, "unico": yes,
            "validacoes": ["email"]},
        "nome": {"tipo": "Texto", "obrigatorio": yes,
            "validacoes": [["minimo", 2]]},
        "idade": {"tipo": "Inteiro", "padrao": 0,
            "validacoes": [["minimo", 0], ["maximo", 130]]},
        "ativo": {"tipo": "Booleano", "padrao": yes},
        "perfil": {"tipo": "Json"}
    }, {"conexao": db, "marcas_de_tempo": yes})

Forge.migrar_tudo(db)
assert "usuarios" in Forge.tabelas(db), "o nome da tabela sai do plural"

ana := Usuario.criar({
        "email": "ana@exemplo.com",
        "nome": "Ana",
        "idade": 30,
        "perfil": {"tema": "escuro"}
    })
out "criou:", ana["email"], "id", ana["id"]
assert ana["id"] is 1, "o Serial gerou o id"
assert ana["ativo"] is yes, "o padrao foi aplicado"

// Os tipos voltam CONVERTIDOS. Sem isso, o SQLite devolveria 0 e 1
// para booleano, e 'given usuario["ativo"]:' seria sempre verdadeiro.
assert type(ana["ativo"]) is "Boolean", "booleano volta booleano"
assert type(ana["perfil"]) is "Vault", "json volta vault"
assert ana["perfil"]["tema"] is "escuro", "e da para ler dentro"
assert ana["criado_em"] isnt void, "a marca de tempo foi posta"

// A validacao recusa, e diz TUDO o que esta errado
monitor:
    Usuario.criar({"email": "nao-e-email", "nome": "X", "idade": 999})
    assert no, "devia ter recusado"
handle ValidationError as e:
    out "problemas:", len(e.campos)
    cycle c in e.campos:
        out "  ", c["campo"], "-", c["motivo"]
    assert len(e.campos) is 3, "os tres de uma vez, nao so o primeiro"

// Campo que o modelo nao declara tambem e recusado
monitor:
    Usuario.criar({"email": "b@x.com", "nome": "Bia", "inventado": 1})
    assert no, "devia ter recusado"
handle ValidationError as e:
    assert len(e.campos) is 1, "so o campo inventado"

// Buscar e atualizar
assert Usuario.buscar(1)["nome"] is "Ana", "achou pelo id"
assert Usuario.buscar(99) is void, "sem resultado devolve void"
assert Usuario.primeiro(nome := "Ana")["idade"] is 30, "achou por campo"

Usuario.atualizar(1, {"idade": 31})
assert Usuario.buscar(1)["idade"] is 31, "atualizou"

// 'criar_ou_atualizar' nao duplica
Usuario.criar_ou_atualizar({"email": "ana@exemplo.com"}, {"nome": "Ana Maria"})
assert Usuario.contar() is 1, "continua uma"
assert Usuario.buscar(1)["nome"] is "Ana Maria", "mas foi atualizada"

out "ok"`, lang: 'df', title: `exercicios/24-banco-de-dados/207_modelos_e_validacao.df` },
  {"h3": "Conceitos"},
  {"p": "Um modelo descreve a tabela **e** o que vale nela:"},
  { code: `Usuario := Forge.modelo("Usuario", {
    "email": {"tipo": "Texto", "obrigatorio": yes, "unico": yes,
              "validacoes": ["email"]},
    "idade": {"tipo": "Inteiro", "validacoes": [["minimo", 0], ["maximo", 130]]}
}, {"conexao": db})`, lang: 'df' },
  {"p": "O nome da tabela sai do plural: `Usuario` → `usuarios`."},
  {"h3": "O que observar"},
  {"p": "**A validação junta TODOS os problemas.** Um formulário que aponta um erro por vez faz o usuário submeter cinco vezes para descobrir cinco problemas. `e.campos` traz um item por problema."},
  {"p": "**Os tipos voltam convertidos.** SQLite guarda booleano como 0 e 1. Sem a conversão de volta, `given usuario[\"ativo\"]:` seria **sempre verdadeiro** — 0 é um inteiro, e a comparação nunca falharia visivelmente. Erros assim vivem meses."},
  {"p": "**Campo desconhecido é recusado.** Um `nomee` digitado errado viraria uma coluna fantasma que nada lê."},
  {"h3": "Armadilhas"},
  {"list": ["`buscar` devolve `void` quando não acha; `buscar_ou_erro` levanta"]},
  {"p": "`RecordNotFoundError`. Use o primeiro quando a ausência é prevista."},
  {"list": ["`marcas_de_tempo` acrescenta `criado_em` e `atualizado_em` — mas só se você"]},
  {"p": "migrar depois de declará-las."},
  {"h3": "Relacionados"},
  {"list": ["[206 — Relações](206_relacoes_sem_n_mais_um.md)", "[207 — Migrações](207_migracoes.md)"]},
  {"h2": "208 · Relacoes, e o problema do N+1"},
  {"p": "**Enunciado.** carregue os pedidos de cem usuarios em duas consultas."},
  { code: `// Buscar cem usuarios e ler 'usuario.pedidos' de cada um faz cento e
// uma consultas. Isso nao aparece em desenvolvimento, com tres linhas
// na tabela, e derruba a producao com dez mil. E o bug de ORM mais
// comum que existe.

adopt Forge

db := Forge.conectar(":memory:")

Usuario := Forge.modelo("Usuario", {
        "id": {"tipo": "Serial"},
        "nome": {"tipo": "Texto", "obrigatorio": yes}
    }, {"conexao": db})

Pedido := Forge.modelo("Pedido", {
        "id": {"tipo": "Serial"},
        "usuario_id": {"tipo": "Inteiro", "indice": yes},
        "total": {"tipo": "Real", "padrao": 0}
    }, {"conexao": db})

Usuario.tem_muitos("pedidos", "Pedido")
Pedido.pertence_a("usuario", "Usuario")
Forge.migrar_tudo(db)

ana := Usuario.criar({"nome": "Ana"})
bia := Usuario.criar({"nome": "Bia"})
cid := Usuario.criar({"nome": "Cid"})

Pedido.criar({"usuario_id": ana["id"], "total": 100.0})
Pedido.criar({"usuario_id": ana["id"], "total": 50.0})
Pedido.criar({"usuario_id": bia["id"], "total": 20.0})

// A relacao NAO carrega sozinha ao ser lida — ou voce pede, ou ela
// nao vem. Ler uma relacao nao carregada devolveria void em vez de
// funcionar devagar.
com_pedidos := Usuario.com(Usuario.todos(), "pedidos")

cycle u in com_pedidos:
    out u["nome"], "tem", len(u["pedidos"]), "pedido(s)"

assert len(com_pedidos[0]["pedidos"]) is 2, "Ana tem dois"
assert len(com_pedidos[1]["pedidos"]) is 1, "Bia tem um"
assert len(com_pedidos[2]["pedidos"]) is 0, "Cid nao tem nenhum"

// Do outro lado: cada pedido conhece o dono
com_dono := Pedido.com(Pedido.todos(), "usuario")
assert com_dono[0]["usuario"]["nome"] is "Ana", "o pedido sabe de quem e"

// Somar por usuario, sem laco aninhado
total_da_ana := Forge.de(db, "pedidos").onde("usuario_id", ana["id"]).somar("total")
assert total_da_ana is 150.0, "100 + 50"

// Uma relacao que nao existe avisa, e lista as que existem
monitor:
    Usuario.com(Usuario.todos(), "inventada")
    assert no, "devia ter recusado"
handle SchemaError as e:
    out "recusado:", e.message
    assert "inventada" in e.message, "a mensagem nomeia o erro"

out "ok"`, lang: 'df', title: `exercicios/24-banco-de-dados/208_relacoes_sem_n_mais_um.df` },
  {"h3": "Conceitos"},
  {"p": "Buscar cem usuários e ler `usuario.pedidos` de cada um faz **cento e uma** consultas: uma para os usuários, e uma por usuário."},
  {"p": "Isso não aparece em desenvolvimento, com três linhas na tabela. Aparece em produção, com dez mil — e é o bug de ORM mais comum que existe."},
  { code: `// duas consultas, para qualquer quantidade
com_pedidos := Usuario.com(Usuario.todos(), "pedidos")`, lang: 'df' },
  {"h3": "O que observar"},
  {"p": "**A relação NÃO carrega sozinha.** Ou você pede com `com(...)`, ou ela não vem. Um ORM que carrega ao ser lida funciona — devagar, e só quando é tarde demais para perceber."},
  {"p": "**Duas consultas, e há teste contando.** A suíte do Forge instrumenta a conexão e conta as chamadas. Se alguém trocar a implementação por uma que faz N+1, o teste falha."},
  {"p": "**Uma relação que não existe avisa**, e lista as que existem."},
  {"h3": "Armadilhas"},
  {"list": ["`tem_muitos` procura a chave `<modelo>_id` na outra tabela. Se o nome for"]},
  {"p": "outro, passe-o: `tem_muitos(\"pedidos\", \"Pedido\", \"dono_id\")`."},
  {"list": ["Sem índice na chave estrangeira, a segunda consulta varre a tabela. Declare"]},
  {"p": "`\"indice\": yes` no campo."},
  {"h3": "Relacionados"},
  {"list": ["[205 — Modelos e validação](205_modelos_e_validacao.md)", "[213 — Medir o crescimento](../26-complexidade/213_medir_o_crescimento.md)"]},
  {"h2": "209 · Migracoes"},
  {"p": "**Enunciado.** evolua o esquema sem perder o que ja esta gravado."},
  { code: `// Duas formas. A simples compara o modelo com a tabela; a completa usa
// passos numerados, com historico NO BANCO — um arquivo versionado diz
// o que deveria ter rodado, a tabela diz o que rodou.

adopt Forge

db := Forge.conectar(":memory:")

// ── A forma simples: a diferenca ──

U := Forge.modelo("Usuario", {
        "id": {"tipo": "Serial"},
        "nome": {"tipo": "Texto", "obrigatorio": yes}
    }, {"conexao": db})
Forge.migrar_tudo(db)
U.criar({"nome": "Ana"})

// O modelo cresce: um campo novo
U2 := Forge.modelo("Usuario", {
        "id": {"tipo": "Serial"},
        "nome": {"tipo": "Texto", "obrigatorio": yes},
        "telefone": {"tipo": "Texto"}
    }, {"conexao": db})

d := U2.diferenca()
out "faltando:", d["colunas_faltando"]
assert d["colunas_faltando"] is ["telefone"], "a coluna nova"
assert d["tabela_falta"] is no, "a tabela ja existe"

U2.aplicar_diferenca()
assert U2.diferenca()["colunas_faltando"] is [], "agora esta em dia"
assert U2.contar() is 1, "e o dado de antes continua la"

// 'aplicar_diferenca' NUNCA apaga. Perda de dado nao se automatiza:
// uma coluna que sumiu do modelo pode ter sido erro de digitacao.
U3 := Forge.modelo("Usuario", {
        "id": {"tipo": "Serial"},
        "nome": {"tipo": "Texto", "obrigatorio": yes}
    }, {"conexao": db})
resultado := U3.aplicar_diferenca()
out "sobrando:", resultado["colunas_a_mais"]
assert "telefone" in resultado["colunas_a_mais"], "ele relata"
colunas := [c["nome"] cycle c in db.colunas("usuarios")]
assert "telefone" in colunas, "mas nao remove"

// ── A forma completa: passos numerados ──

m := Forge.migracoes(db)

m.passo("001_cria_pedidos",
    lambda c => c.executar("create table pedidos (id integer primary key)"),
    lambda c => c.executar("drop table pedidos"))

m.passo("002_acrescenta_total",
    lambda c => c.executar("alter table pedidos add column total real"))

feitas := m.subir()
out "aplicadas:", feitas
assert len(feitas) is 2, "as duas"
assert "pedidos" in Forge.tabelas(db), "a tabela existe"

// Rodar de novo nao repete
assert m.subir() is [], "o historico impede a repeticao"
assert m.estado()["aplicadas"] is 2, "duas no historico"
assert m.estado()["pendentes"] is 0, "nenhuma pendente"

// Desfazer so o que declarou como desfazer
m2 := Forge.migracoes(db)
m2.passo("003_sem_volta",
    lambda c => c.executar("create table temp (id integer)"))
m2.subir()
monitor:
    m2.descer(1)
    assert no, "devia ter recusado"
handle MigrationError as e:
    out "sem volta:", e.message
    assert "003" in e.message, "diz qual"

out "ok"`, lang: 'df', title: `exercicios/24-banco-de-dados/209_migracoes.df` },
  {"h3": "Conceitos"},
  {"p": "Duas formas."},
  {"p": "**A diferença** compara o modelo com a tabela real e cria o que falta:"},
  { code: `d := Usuario.diferenca()          // o que falta
Usuario.aplicar_diferenca()       // cria`, lang: 'df' },
  {"p": "**Os passos numerados** cobrem o que a diferença não cobre — renomear uma coluna, migrar dados, criar um índice composto:"},
  { code: `m := Forge.migracoes(db)
m.passo("001_cria_pedidos", subir, descer)
m.subir()`, lang: 'df' },
  {"h3": "O que observar"},
  {"p": "**`aplicar_diferenca` nunca apaga.** Ele cria o que falta e **relata** o que sobra. Perda de dado não se automatiza: uma coluna que sumiu do modelo pode ter sido erro de digitação, e a diferença entre um `DROP` e uma restauração de backup é grande."},
  {"p": "**O histórico mora no banco**, numa tabela `_forge_migracoes`. É o que faz duas máquinas concordarem sobre o estado: um arquivo versionado diz o que *deveria* ter rodado; a tabela diz o que rodou."},
  {"p": "**Uma migração que falha para tudo.** Continuar depois de uma falha deixa o banco num estado que nenhuma migração previu."},
  {"h3": "Armadilhas"},
  {"list": ["Escreva o `descer` mesmo que não vá usar. O momento em que você precisa dele é"]},
  {"p": "o pior momento possível para escrevê-lo."},
  {"list": ["Comparar o modelo com a tabela **real** é melhor que confiar num histórico de"]},
  {"p": "arquivos, que diverge assim que alguém mexe no banco à mão."},
  {"h3": "Relacionados"},
  {"list": ["[205 — Modelos e validação](205_modelos_e_validacao.md)"]},
  {"h2": "210 · Pool de conexoes"},
  {"p": "**Enunciado.** reaproveite conexoes, e garanta que elas voltem."},
  { code: `// Abrir conexao custa: TCP, autenticacao, negociacao. Numa rota web
// isso acontece por requisicao e passa a dominar o tempo de resposta.
// O pool nao e so cache — e tambem limite.

adopt Forge

pool := Forge.pool(":memory:", 2)
out "no comeco:", pool.estado()

// 'with' devolve a conexao sozinho, no fim do bloco
with Forge.conexao(pool) as db:
    Forge.executar(db, "create table t (id integer primary key)")
    assert "t" in Forge.tabelas(db), "usou a conexao"

assert pool.estado()["livres"] is 1, "voltou para o pool"

// E devolve mesmo quando o corpo falha — que e onde mais importa
monitor:
    with Forge.conexao(pool) as db:
        trigger "erro no meio"
handle e:
    out "capturado:", e.message

assert pool.estado()["livres"] is 1, "voltou mesmo com erro"

// A mesma conexao e reaproveitada
with Forge.conexao(pool) as a:
    primeira := a
with Forge.conexao(pool) as b:
    assert b is primeira, "e a mesma de antes, nao uma nova"

// Sem teto, um pico de trafego abriria mil conexoes e o servidor
// recusaria TODAS — inclusive as de quem ja estava funcionando.
// Melhor a milesima requisicao esperar do que as mil falharem.
pequeno := Forge.pool(":memory:", 1)
ocupada := pequeno.pegar()
monitor:
    pequeno.pegar()
    assert no, "devia ter esperado e desistido"
handle PoolExhaustedError as e:
    out "esgotado:", e.message
    assert "busy" in e.message, "a mensagem explica"

pequeno.devolver(ocupada)
assert pequeno.pegar() isnt void, "depois de devolver, funciona"

pool.fechar()
pequeno.fechar()
out "ok"`, lang: 'df', title: `exercicios/24-banco-de-dados/210_pool_e_conexoes.df` },
  {"h3": "Conceitos"},
  {"p": "Abrir conexão custa: TCP, autenticação, negociação. Numa rota web isso acontece por requisição e passa a dominar o tempo de resposta."},
  { code: `pool := Forge.pool("postgres://localhost/app", 5)

with Forge.conexao(pool) as db:
    Forge.de(db, "usuarios").contar()`, lang: 'df' },
  {"h3": "O que observar"},
  {"p": "**`with` devolve a conexão sozinho** — inclusive quando o corpo falha, que é onde mais importa. Uma conexão pegada e não devolvida some do pool para sempre."},
  {"p": "**O pool não é só cache — é limite.** Sem teto, um pico de tráfego abre mil conexões e o servidor recusa **todas**, inclusive as de quem já estava funcionando. Melhor a milésima requisição esperar do que as mil falharem."},
  {"p": "**O `with` roda no escopo de fora**, como o `monitor`: o que o corpo calcula continua visível depois. Só o nome do recurso é local — ele deixa de valer quando o recurso fecha."},
  {"h3": "Armadilhas"},
  {"list": ["Uma conexão devolvida no meio de uma transação contaminaria a próxima. O pool"]},
  {"p": "desfaz antes de devolver."},
  {"list": ["O tamanho do pool tem um teto natural: o `max_connections` do servidor. Cinco"]},
  {"p": "processos com pool de 20 pedem 100 conexões."},
  {"h3": "Relacionados"},
  {"list": ["[204 — Transações](204_transacoes.md)"]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/24-banco-de-dados/203_conectar.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '203-conectar-e-consultar', text: "203 · Conectar e consultar", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '204-construtor-de-consultas', text: "204 · Construtor de consultas", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '205-injecao-de-sql-e-por-que-ela-nao-acontece-aqui', text: "205 · Injecao de SQL, e por que ela nao acontece aqui", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '206-transacoes', text: "206 · Transacoes", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '207-modelos-e-validacao', text: "207 · Modelos e validacao", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '208-relacoes-e-o-problema-do-n1', text: "208 · Relacoes, e o problema do N+1", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '209-migracoes', text: "209 · Migracoes", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '210-pool-de-conexoes', text: "210 · Pool de conexoes", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"24 · Banco de dados"}
      description={"8 exercícios: Forge: conexão, consultas, transações e ORM."}
      href={"/docs/exercicios/24-banco-de-dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
