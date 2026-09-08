"""Forge — banco de dados e ORM."""

PAGINAS = [
{
"href": "/docs/banco-de-dados",
"title": "Forge — banco de dados",
"description": "Cinco motores, uma interface, zero dependências.",
"blocos": [
 {"p": "**Forge** conecta a PostgreSQL, MySQL, MariaDB, MongoDB, Redis e SQLite. Trocar o motor troca a URL, e mais nada:"},
 {"code": """adopt Forge

db := Forge.conectar("postgres://usuario:senha@localhost:5432/app")
// ou "mysql://root@localhost/app"
// ou "mongodb://localhost/app"
// ou "redis://localhost"
// ou "dados.db"                    — SQLite

out Forge.versao(db)""", "lang": "df"},

 {"h2": "Sem dependência nenhuma"},
 {"p": "Cada driver fala o protocolo do seu banco, por socket. Não há `psycopg2`, `PyMySQL`, `redis-py` nem `pymongo` aqui — há um arquivo por protocolo, implementando a especificação publicada de cada servidor."},
 {"p": "O custo foi escrevê-los. O que se ganha é que `pip install dataforge` funciona numa máquina sem compilador, e a versão do driver nunca briga com a de outro pacote."},
 {"table": {"head": ["Motor", "Autenticação", "Testado contra"], "rows": [
   ["PostgreSQL", "SCRAM-SHA-256, MD5, trust", "16"],
   ["MySQL", "caching_sha2_password (com RSA), mysql_native_password", "8.4"],
   ["MariaDB", "mysql_native_password", "11"],
   ["Redis", "AUTH com usuário e senha", "7.4"],
   ["MongoDB", "SCRAM-SHA-256 e SHA-1", "7.0"],
   ["SQLite", "—", "o do Python"]]}},

 {"h2": "Primeiro programa"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")

Forge.executar(db, \"\"\"
    create table produtos (
        id integer primary key autoincrement,
        nome text not null,
        preco real
    )
\"\"\")

Forge.de(db, "produtos").inserir([
    {"nome": "Teclado", "preco": 250.0},
    {"nome": "Mouse", "preco": 90.0}
])

caros := Forge.de(db, "produtos").onde("preco", ">=", 100).buscar()
assert len(caros) is 1
assert caros[0]["nome"] is "Teclado\"""", "lang": "df"},

 {"h2": "Valores nunca entram no texto da consulta"},
 {"p": "Esta é a garantia central, e ela vale para o construtor e para o SQL escrito à mão:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table u (id integer primary key, nome text)")

malicioso := "'; drop table u; --"
Forge.de(db, "u").inserir({"nome": malicioso})

// a tabela continua lá: o valor foi tratado como dado, não como SQL
assert "u" in Forge.tabelas(db)
assert Forge.de(db, "u").contar() is 1""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Injeção é impossível por construção", "texto": "Não é disciplina de quem escreve: o construtor **não tem** como pôr um valor no texto. A lista de operadores também é fechada — um operador vindo de variável seria outro caminho de injeção."}},

 {"h2": "Erros que dizem o que houve"},
 {"p": "Cada erro do servidor vira uma classe da linguagem, capturável por família:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table u (id integer primary key, email text unique)")
Forge.de(db, "u").inserir({"email": "a@b.co"})

monitor:
    Forge.de(db, "u").inserir({"email": "a@b.co"})
handle ConstraintError as e:
    assert "UNIQUE" in e.message""", "lang": "df"},
 {"table": {"head": ["Classe", "Quando"], "rows": [
   ["`ConnectionError`", "o servidor não respondeu ou recusou"],
   ["`AuthenticationError`", "usuário ou senha inválidos"],
   ["`QueryError`", "SQL inválido, tabela ou coluna inexistente"],
   ["`ConstraintError`", "chave única, estrangeira, ou `not null`"],
   ["`TransactionError`", "deadlock, ou confirmar sem transação aberta"],
   ["`PoolExhaustedError`", "todas as conexões ocupadas"],
   ["`RecordNotFoundError`", "`buscar_ou_erro` não achou"],
   ["`ValidationError`", "o modelo recusou os dados"]]}},
 {"p": "Todas descendem de `DatabaseError`, então `handle DatabaseError` pega qualquer uma. Ver [catálogo de erros](/docs/erros)."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/banco-de-dados/consultas", "title": "Construtor de consultas", "desc": "onde, junções, agregados, paginação"},
   {"href": "/docs/banco-de-dados/transacoes", "title": "Transações e pool", "desc": "e por que 'transacao' com bloco é a única forma segura"},
   {"href": "/docs/banco-de-dados/motores", "title": "Cada motor", "desc": "o que só existe no PostgreSQL, no Redis, no Mongo"},
   {"href": "/docs/orm", "title": "ORM", "desc": "modelos, validação e relações sem N+1"},
   {"href": "/docs/orm/migracoes", "title": "Migrações", "desc": "com histórico no banco, não num arquivo"}]},
]},

{
"href": "/docs/banco-de-dados/consultas",
"title": "Construtor de consultas",
"description": "SQL montado por chamadas encadeadas — com o dialeto certo e sem injeção.",
"blocos": [
 {"p": "Escrever SQL à mão continua valendo — `Forge.consultar(db, sql, valores)` está aí para isso. O construtor resolve três coisas que o SQL à mão não resolve:"},
 {"list": [
   "**Dialeto.** `?` no SQLite e MySQL, `$1` no PostgreSQL. A mesma consulta roda nos dois.",
   "**Condição opcional.** Um filtro que só existe quando o usuário preencheu o campo.",
   "**Identificador citado.** Uma coluna chamada `order` quebraria a consulta."]},

 {"h2": "O básico"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, \"\"\"
    create table usuarios (
        id integer primary key autoincrement,
        nome text, cidade text, idade integer, ativo integer
    )
\"\"\")
Forge.de(db, "usuarios").inserir([
    {"nome": "Ana", "cidade": "Floripa", "idade": 30, "ativo": 1},
    {"nome": "Bia", "cidade": "Recife", "idade": 25, "ativo": 1},
    {"nome": "Cid", "cidade": "Floripa", "idade": 41, "ativo": 0}
])

adultos := Forge.de(db, "usuarios")
    .selecionar("nome", "cidade")
    .onde("idade", ">=", 18)
    .onde_em("cidade", ["Floripa", "Recife"])
    .ordenar("nome")
    .limite(10)
    .buscar()

assert len(adultos) is 3
assert adultos[0]["nome"] is "Ana\"""", "lang": "df"},

 {"h2": "Filtros"},
 {"table": {"head": ["Método", "SQL"], "rows": [
   ["`.onde(\"a\", 1)`", "`a = ?`"],
   ["`.onde(\"a\", \">=\", 1)`", "`a >= ?`"],
   ["`.ou_onde(\"a\", 2)`", "`OR a = ?`"],
   ["`.onde_em(\"a\", [1,2])`", "`a IN (?, ?)`"],
   ["`.onde_fora(\"a\", [1])`", "`a NOT IN (?)`"],
   ["`.onde_entre(\"a\", 1, 9)`", "`a BETWEEN ? AND ?`"],
   ["`.onde_nulo(\"a\")`", "`a IS NULL`"],
   ["`.onde_contem(\"a\", \"x\")`", "`a LIKE '%x%'`"],
   ["`.onde_comeca(\"a\", \"x\")`", "`a LIKE 'x%'`"],
   ["`.onde_cru(sql, valores)`", "o que você escrever, com os valores ainda parametrizados"]]}},
 {"callout": {"tipo": "nota", "titulo": "`onde(\"x\", void)` vira `IS NULL`", "texto": "Em SQL, `x = NULL` nunca é verdadeiro — nem quando x é nulo. O construtor traduz para `IS NULL`, que é o que quem escreveu queria."}},

 {"h2": "Condição opcional"},
 {"p": "`quando` aplica o trecho só se a condição valer. É o que evita o `if` em volta da consulta:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table p (id integer primary key, nome text, preco real)")
Forge.de(db, "p").inserir([
    {"nome": "Teclado", "preco": 250.0},
    {"nome": "Mouse", "preco": 90.0}
])

action procurar(db, busca, preco_max):
    yield Forge.de(db, "p")
        .quando(busca, lambda c => c.onde_contem("nome", busca))
        .quando(preco_max, lambda c => c.onde("preco", "<=", preco_max))
        .buscar()

assert len(procurar(db, "", void)) is 2
assert len(procurar(db, "Mouse", void)) is 1
assert len(procurar(db, "", 100)) is 1""", "lang": "df"},

 {"h2": "Agregados e paginação"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table v (id integer primary key, total real)")
Forge.de(db, "v").inserir([{"total": 10.0}, {"total": 20.0}, {"total": 30.0}])

q := Forge.de(db, "v")
assert q.contar() is 3
assert Forge.de(db, "v").somar("total") is 60.0
assert Forge.de(db, "v").media("total") is 20.0
assert Forge.de(db, "v").maximo("total") is 30.0
assert Forge.de(db, "v").existe() is yes

pagina := Forge.de(db, "v").paginar(1, 2)
assert pagina["total"] is 3
assert pagina["paginas"] is 2
assert pagina["tem_proxima"] is yes""", "lang": "df"},
 {"p": "`paginar` devolve as linhas **e** os números que a interface precisa: total, quantidade de páginas, se há próxima e anterior. A página 1 é a primeira — não a zero."},

 {"h2": "Escritas"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table c (id integer primary key autoincrement, n integer)")

Forge.de(db, "c").inserir({"n": 5})
Forge.de(db, "c").onde("id", 1).atualizar({"n": 10})
Forge.de(db, "c").onde("id", 1).incrementar("n", 3)

assert Forge.de(db, "c").onde("id", 1).primeiro()["n"] is 13""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "UPDATE e DELETE sem WHERE são recusados", "texto": "Um `UPDATE` sem condição mudaria todas as linhas. O construtor recusa e sugere `.onde(...)`. Quando a intenção é essa mesmo, `atualizar_tudo` e `remover_tudo` existem — e o nome deixa claro."}},
 {"p": "`incrementar` faz a soma **no banco**, sem ler antes. Ler-somar-gravar perde atualizações quando duas conexões fazem isso ao mesmo tempo."},

 {"h2": "Ver o SQL"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table u (id integer primary key, idade integer)")

consulta := Forge.de(db, "u").onde("idade", ">=", 18).limite(5)
out consulta.sql()""", "lang": "df"},
 {"p": "Útil para registrar, depurar, ou levar uma consulta complicada para o cliente do banco."},
]},

{
"href": "/docs/banco-de-dados/transacoes",
"title": "Transações e pool",
"description": "Tudo ou nada — e por que 'transacao' com bloco é a única forma segura.",
"blocos": [
 {"h2": "Transações"},
 {"p": "Uma transação garante que um conjunto de escritas aconteça inteiro, ou não aconteça:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table contas (id integer primary key, saldo real)")
Forge.de(db, "contas").inserir([{"id": 1, "saldo": 100.0}, {"id": 2, "saldo": 0.0}])

action transferir(db, de, para, valor):
    Forge.de(db, "contas").onde("id", de).incrementar("saldo", 0 - valor)
    Forge.de(db, "contas").onde("id", para).incrementar("saldo", valor)
    yield yes

Forge.transacao(db, lambda c => transferir(c, 1, 2, 30.0))

assert Forge.de(db, "contas").onde("id", 1).primeiro()["saldo"] is 70.0
assert Forge.de(db, "contas").onde("id", 2).primeiro()["saldo"] is 30.0""", "lang": "df"},
 {"p": "Se o corpo falhar, tudo é desfeito:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table t (id integer primary key, n integer)")

action falha(c):
    Forge.de(c, "t").inserir({"n": 1})
    trigger "deu errado no meio"

monitor:
    Forge.transacao(db, falha)
handle e:
    assert e.message is "deu errado no meio"

// a linha inserida antes da falha não ficou
assert Forge.de(db, "t").contar() is 0""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Use a forma com bloco", "texto": "`comecar()` com um `confirmar()` esquecido segura locks até a conexão cair — é o motivo mais comum de um banco travar em produção. `Forge.transacao` confirma no fim e desfaz na falha, sempre."}},

 {"h2": "A forma manual"},
 {"p": "Existe, para quando o fluxo não cabe num bloco:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table t (id integer primary key, n integer)")

db.comecar()
monitor:
    Forge.de(db, "t").inserir({"n": 1})
    db.confirmar()
handle e:
    db.desfazer()

assert Forge.de(db, "t").contar() is 1""", "lang": "df"},

 {"h2": "Pool de conexões"},
 {"p": "Abrir conexão custa: TCP, autenticação, negociação. Numa rota web isso acontece por requisição e passa a dominar o tempo de resposta."},
 {"code": """adopt Forge

pool := Forge.pool(":memory:", 5)

with Forge.conexao(pool) as db:
    out Forge.versao(db)

out pool.estado()""", "lang": "df"},
 {"p": "O pool não é só cache — é também **limite**. Sem teto, um pico de tráfego abre mil conexões e o servidor recusa **todas**, inclusive as do que já estava funcionando. Melhor a milésima requisição esperar do que as mil falharem."},
 {"callout": {"tipo": "dica", "titulo": "Sempre com `with`", "texto": "Uma conexão pegada e não devolvida some do pool para sempre. `Forge.conexao(pool)` devolve sozinha, inclusive se o corpo falhar — e desfaz uma transação aberta antes de devolver, para não contaminar quem pegar depois."}},

 {"h2": "Níveis de isolamento"},
 {"code": """db.comecar("SERIALIZABLE")""", "lang": "df"},
 {"table": {"head": ["Nível", "Impede", "Custo"], "rows": [
   ["`READ COMMITTED`", "leitura suja", "baixo — o padrão no PostgreSQL"],
   ["`REPEATABLE READ`", "leitura não repetível", "médio — o padrão no MySQL"],
   ["`SERIALIZABLE`", "leitura fantasma", "alto — pode abortar por conflito"]]}},
 {"p": "Com `SERIALIZABLE`, prepare-se para `TransactionError` por falha de serialização, e para tentar de novo. É o preço da garantia."},
]},

{
"href": "/docs/banco-de-dados/motores",
"title": "Cada motor",
"description": "O que a interface comum cobre, e o que só existe em cada um.",
"blocos": [
 {"p": "A interface comum cobre o que faz sentido em todos: conectar, consultar, fechar. O resto cada motor expõe pelo que ele é — **um ORM que finge que Redis é uma tabela produz código que parece portável e não é**."},

 {"h2": "SQLite"},
 {"p": "Roda dentro do processo. É o banco de teste que não deixa rastro:"},
 {"code": """adopt Forge

db := Forge.memoria()                 // ou Forge.conectar("dados.db")
Forge.executar(db, "create table t (id integer primary key, n integer)")
Forge.de(db, "t").inserir({"n": 1})
assert Forge.de(db, "t").contar() is 1""", "lang": "df"},
 {"p": "Duas coisas que o Forge liga e o SQLite deixa desligadas por padrão: **chave estrangeira** (senão a restrição existe só no papel) e **WAL** (senão um leitor bloqueia o escritor, e um servidor trava com carga leve)."},

 {"h2": "PostgreSQL"},
 {"p": "Os tipos voltam convertidos: `jsonb` vira vault, array vira cluster, `boolean` vira `yes`/`no`."},
 {"code": """// db := Forge.conectar("postgres://usuario:senha@localhost/app")
//
// Forge.executar(db, \"\"\"
//     create table pessoas (
//         id serial primary key,
//         nome text not null,
//         dados jsonb,
//         tags text[]
//     )
// \"\"\")
//
// Forge.executar(db,
//     "insert into pessoas (nome, dados, tags) values (?, ?, ?)",
//     ["Ana", {"cor": "azul"}, ["a", "b"]])
//
// linha := Forge.primeiro(db, "select * from pessoas")
// out linha["dados"]["cor"]        // "azul" — vault de verdade
// out linha["tags"][0]             // "a"    — cluster de verdade""", "lang": "df"},
 {"p": "`RETURNING` funciona e devolve as linhas:"},
 {"code": """// nova := Forge.executar(db,
//     "insert into pessoas (nome) values (?) returning id, nome",
//     ["Bia"])
// out nova[0]["id"]""", "lang": "df"},

 {"h2": "MySQL e MariaDB"},
 {"p": "O mesmo driver serve os dois — o MariaDB nasceu de um fork e manteve o protocolo. O que muda é a autenticação padrão."},
 {"callout": {"tipo": "nota", "titulo": "MySQL 8 e o caching_sha2_password", "texto": "Quando o cache do servidor não tem a senha e o canal não é TLS, o MySQL 8 exige que ela viaje cifrada com a chave pública dele. O Forge faz esse handshake — é onde a maioria dos drivers caseiros para."}},
 {"code": """// db := Forge.conectar("mysql://root:senha@localhost/app")
// out db.ultimo_id()        // o id gerado pelo último auto_increment""", "lang": "df"},

 {"h2": "Redis"},
 {"p": "Não tem SQL, e fingir que tem seria mentir. O que ele tem é chave-valor, e é isso que a interface expõe:"},
 {"code": """// db := Forge.conectar("redis://localhost")
//
// db.comando("SET", "usuario:1", "Ana")
// out db.comando("GET", "usuario:1")
// db.comando("EXPIRE", "usuario:1", 60)
//
// db.comando("RPUSH", "fila", 1, 2, 3)
// out db.comando("LRANGE", "fila", 0, -1)""", "lang": "df"},
 {"p": "**Pipeline** é a otimização mais eficaz com Redis. Cem comandos em cem idas custam cem vezes a latência da rede; numa ida só, custam uma:"},
 {"code": """// respostas := db.pipeline([
//     ["SET", "a", "1"],
//     ["SET", "b", "2"],
//     ["MGET", "a", "b"]
// ])
// out respostas[2]        // ["1", "2"]""", "lang": "df"},

 {"h2": "MongoDB"},
 {"p": "Documentos, não tabelas. O `_id` sai como texto e a busca por ele aceita texto — sem essa conversão, procurar por id nunca acharia nada, e não haveria erro, só um resultado vazio:"},
 {"code": """// db := Forge.conectar("mongodb://localhost/app")
//
// r := db.inserir("pessoas", [
//     {"nome": "Ana", "idade": 30},
//     {"nome": "Bia", "idade": 25}
// ])
//
// out db.achar("pessoas", {"idade": {"$gt": 26}})
// out db.achar_um("pessoas", {"_id": r["ids"][0]})
// db.atualizar("pessoas", {"nome": "Bia"}, {"idade": 26})
// out db.contar("pessoas")
//
// out db.agregar("pessoas", [
//     {"$group": {"_id": void, "media": {"$avg": "$idade"}}}
// ])
//
// db.criar_indice("pessoas", "nome", unico := yes)""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "`atualizar` embrulha em `$set`", "texto": "Sem um operador, o Mongo **substitui** o documento inteiro e apaga os campos que não vieram. Quase ninguém quer isso, então o Forge embrulha. Passe `{\"$inc\": {...}}` quando quiser outro operador."}},

 {"h2": "O que é comum a todos"},
 {"table": {"head": ["", "SQLite", "Postgres", "MySQL", "Redis", "Mongo"], "rows": [
   ["`conectar`", "✓", "✓", "✓", "✓", "✓"],
   ["`ping`, `versao`, `fechar`", "✓", "✓", "✓", "✓", "✓"],
   ["`consultar` / `executar`", "✓", "✓", "✓", "cru", "documento"],
   ["construtor de consultas", "✓", "✓", "✓", "—", "—"],
   ["ORM", "✓", "✓", "✓", "—", "—"],
   ["transações", "✓", "✓", "✓", "MULTI", "—"],
   ["`tabelas` / `colunas`", "✓", "✓", "✓", "—", "`colecoes`"]]}},
]},

{
"href": "/docs/orm",
"title": "ORM",
"description": "Modelos com validação, tipos convertidos e relações que não fazem N+1.",
"blocos": [
 {"p": "Um modelo descreve uma tabela e o que vale nela. O que ele acrescenta ao construtor de consultas:"},
 {"list": [
   "**validação** antes de ir ao banco, e com **todos** os erros de uma vez",
   "**tipos convertidos** — o que sai do banco volta como o modelo declara",
   "**relações** carregadas sem o problema de N+1",
   "**migrações** a partir da diferença entre o modelo e a tabela"]},

 {"h2": "Declarando"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")

Usuario := Forge.modelo("Usuario", {
    "id":    {"tipo": "Serial"},
    "email": {"tipo": "Texto", "obrigatorio": yes, "unico": yes,
              "validacoes": ["email"]},
    "nome":  {"tipo": "Texto", "obrigatorio": yes,
              "validacoes": [["minimo", 2]]},
    "idade": {"tipo": "Inteiro", "padrao": 0,
              "validacoes": [["minimo", 0], ["maximo", 130]]},
    "ativo": {"tipo": "Booleano", "padrao": yes},
    "perfil": {"tipo": "Json"}
}, {"conexao": db, "marcas_de_tempo": yes})

Forge.migrar_tudo(db)

ana := Usuario.criar({"email": "ana@exemplo.com", "nome": "Ana", "idade": 30})
assert ana["id"] is 1
assert ana["ativo"] is yes""", "lang": "df"},
 {"p": "O nome da tabela sai do plural do modelo: `Usuario` → `usuarios`, `Pedido` → `pedidos`, `Animal` → `animais`. Passe `{\"tabela\": \"...\"}` para um irregular."},

 {"h2": "Os tipos"},
 {"table": {"head": ["Forge", "PostgreSQL", "MySQL", "SQLite"], "rows": [
   ["`Serial`", "SERIAL PRIMARY KEY", "INT AUTO_INCREMENT PK", "INTEGER PK AUTOINCREMENT"],
   ["`Inteiro`", "INTEGER", "INT", "INTEGER"],
   ["`Grande`", "BIGINT", "BIGINT", "INTEGER"],
   ["`Decimal`", "NUMERIC(18,6)", "DECIMAL(18,6)", "NUMERIC"],
   ["`Real`", "DOUBLE PRECISION", "DOUBLE", "REAL"],
   ["`Texto`", "TEXT", "VARCHAR(255)", "TEXT"],
   ["`TextoLongo`", "TEXT", "LONGTEXT", "TEXT"],
   ["`Booleano`", "BOOLEAN", "TINYINT(1)", "INTEGER"],
   ["`Data` / `DataHora`", "DATE / TIMESTAMPTZ", "DATE / DATETIME", "TEXT"],
   ["`Json`", "JSONB", "JSON", "TEXT"],
   ["`Uuid`", "UUID", "CHAR(36)", "TEXT"],
   ["`Binario`", "BYTEA", "BLOB", "BLOB"]]}},
 {"callout": {"tipo": "dica", "titulo": "A conversão importa", "texto": "SQLite guarda booleano como 0 e 1. Sem a conversão de volta, `given usuario[\"ativo\"]:` seria sempre verdadeiro — 0 é um inteiro, e a comparação nunca falharia visivelmente. Erros assim vivem meses."}},

 {"h2": "Validação"},
 {"p": "Todos os problemas de uma vez. Um formulário que aponta um erro por vez faz o usuário submeter cinco vezes para descobrir cinco problemas:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Usuario := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "email": {"tipo": "Texto", "obrigatorio": yes, "validacoes": ["email"]},
    "nome": {"tipo": "Texto", "obrigatorio": yes, "validacoes": [["minimo", 2]]},
    "idade": {"tipo": "Inteiro", "validacoes": [["maximo", 130]]}
}, {"conexao": db})
Forge.migrar_tudo(db)

monitor:
    Usuario.criar({"email": "não-é-email", "nome": "X", "idade": 999})
handle ValidationError as e:
    // e.campos traz um item por problema
    assert len(e.campos) is 3""", "lang": "df"},
 {"table": {"head": ["Regra", "Cobra"], "rows": [
   ["`\"obrigatorio\"`", "não vazio"],
   ["`\"email\"`", "formato de e-mail"],
   ["`[\"minimo\", n]`", "número ≥ n, ou texto com n caracteres"],
   ["`[\"maximo\", n]`", "número ≤ n, ou texto até n caracteres"],
   ["`[\"formato\", padrao]`", "casa com a expressão regular"],
   ["`[\"um_de\", [a, b]]`", "está na lista"],
   ["`\"positivo\"`", "maior que zero"]]}},

 {"h2": "Buscar e escrever"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes},
    "idade": {"tipo": "Inteiro", "padrao": 0}
}, {"conexao": db})
Forge.migrar_tudo(db)

U.criar({"nome": "Ana", "idade": 30})
U.criar({"nome": "Bia", "idade": 25})

assert len(U.todos()) is 2
assert U.buscar(1)["nome"] is "Ana"
assert U.buscar(99) is void
assert U.primeiro(nome := "Bia")["idade"] is 25
assert U.contar() is 2
assert U.existe(nome := "Ana") is yes

U.atualizar(1, {"idade": 31})
assert U.buscar(1)["idade"] is 31

U.criar_ou_atualizar({"nome": "Ana"}, {"idade": 32})
assert U.contar() is 2          // não criou outra

U.remover(2)
assert U.contar() is 1""", "lang": "df"},
 {"p": "`buscar_ou_erro` levanta `RecordNotFoundError` quando não acha — útil numa rota onde a ausência é 404, e desnecessário onde ela é prevista."},

 {"h2": "Marcas de tempo e remoção suave"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes}
}, {"conexao": db, "marcas_de_tempo": yes, "remocao_suave": yes})
Forge.migrar_tudo(db)

u := U.criar({"nome": "Ana"})
assert u["criado_em"] isnt void

U.remover(u["id"])
assert U.contar() is 0                                  // some das buscas
assert len(Forge.consultar(db, "select * from usuarios")) is 1   // mas está lá""", "lang": "df"},

 {"h2": "Ganchos"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes}
}, {"conexao": db})
Forge.migrar_tudo(db)

U.antes_de_salvar(lambda dados => {"nome": dados["nome"].to_upper()})

assert U.criar({"nome": "ana"})["nome"] is "ANA\"""", "lang": "df"},
]},

{
"href": "/docs/orm/relacoes",
"title": "Relações",
"description": "Duas consultas para cem registros — e por que a relação não carrega sozinha.",
"blocos": [
 {"h2": "O problema do N+1"},
 {"p": "Buscar cem usuários e ler `usuario.pedidos` de cada um faz **cento e uma** consultas. Isso não aparece em desenvolvimento, com três linhas na tabela, e derruba a produção com dez mil."},
 {"p": "**É o bug de ORM mais comum que existe.** No Forge, a relação não carrega sozinha ao ser lida — ou você pede, ou ela não vem:"},
 {"code": """adopt Forge

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
Pedido.criar({"usuario_id": ana["id"], "total": 100.0})
Pedido.criar({"usuario_id": ana["id"], "total": 50.0})
Pedido.criar({"usuario_id": bia["id"], "total": 20.0})

// DUAS consultas, para qualquer quantidade de usuários
com_pedidos := Usuario.com(Usuario.todos(), "pedidos")
assert len(com_pedidos[0]["pedidos"]) is 2
assert len(com_pedidos[1]["pedidos"]) is 1""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Duas, e há teste contando", "texto": "A suíte do Forge tem um teste que instrumenta a conexão e conta as consultas. Se alguém trocar a implementação por uma que faz N+1, ele falha."}},

 {"h2": "Os quatro tipos"},
 {"code": """// um usuário tem muitos pedidos
Usuario.tem_muitos("pedidos", "Pedido")

// um pedido pertence a um usuário
Pedido.pertence_a("usuario", "Usuario")

// um usuário tem um perfil
Usuario.tem_um("perfil", "Perfil")

// um post tem muitas etiquetas, e uma etiqueta muitos posts
Post.muitos_para_muitos("etiquetas", "Etiqueta")""", "lang": "df"},
 {"table": {"head": ["Relação", "A chave fica em", "Padrão do nome"], "rows": [
   ["`tem_muitos`", "na tabela do outro", "`<modelo>_id`"],
   ["`tem_um`", "na tabela do outro", "`<modelo>_id`"],
   ["`pertence_a`", "nesta tabela", "`<nome>_id`"],
   ["`muitos_para_muitos`", "numa tabela ponte", "as duas chaves"]]}},

 {"h2": "Do outro lado"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"}, "nome": {"tipo": "Texto"}
}, {"conexao": db})
P := Forge.modelo("Pedido", {
    "id": {"tipo": "Serial"}, "usuario_id": {"tipo": "Inteiro"},
    "total": {"tipo": "Real", "padrao": 0}
}, {"conexao": db})
P.pertence_a("usuario", "Usuario")
Forge.migrar_tudo(db)

ana := U.criar({"nome": "Ana"})
P.criar({"usuario_id": ana["id"], "total": 10.0})

com_dono := P.com(P.todos(), "usuario")
assert com_dono[0]["usuario"]["nome"] is "Ana\"""", "lang": "df"},

 {"h2": "Relação desconhecida avisa"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {"id": {"tipo": "Serial"}}, {"conexao": db})
U.tem_muitos("pedidos", "Pedido")
Forge.migrar_tudo(db)

monitor:
    U.com(U.todos(), "inventada")
handle SchemaError as e:
    assert "inventada" in e.message""", "lang": "df"},
 {"p": "A mensagem lista as relações que existem — é mais útil que \"não encontrada\"."},
]},

{
"href": "/docs/orm/migracoes",
"title": "Migrações",
"description": "Com histórico no banco, não num arquivo — e nunca apagando dado sozinho.",
"blocos": [
 {"h2": "A forma simples: a diferença"},
 {"p": "O modelo descreve como a tabela deveria ser. `diferenca()` compara com como ela **é**:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes}
}, {"conexao": db})
Forge.migrar_tudo(db)

// agora o modelo cresce
U2 := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes},
    "telefone": {"tipo": "Texto"}
}, {"conexao": db})

d := U2.diferenca()
assert d["colunas_faltando"] is ["telefone"]

U2.aplicar_diferenca()
assert U2.diferenca()["colunas_faltando"] is []""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`aplicar_diferenca` nunca apaga", "texto": "Ele cria o que falta e **relata** o que sobra, sem remover. Perda de dado não se automatiza: uma coluna que sumiu do modelo pode ter sido um engano de digitação, e a diferença entre um `ALTER TABLE DROP` e uma restauração de backup é grande."}},
 {"p": "Comparar o modelo com a tabela de verdade é melhor que confiar num histórico de arquivos, que diverge assim que alguém mexe no banco à mão."},

 {"h2": "A forma completa: passos numerados"},
 {"p": "Para o que a diferença não cobre — renomear uma coluna, migrar dados, criar um índice composto:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
m := Forge.migracoes(db)

m.passo("001_cria_usuarios",
    lambda c => c.executar(
        "create table usuarios (id integer primary key, nome text)"),
    lambda c => c.executar("drop table usuarios"))

m.passo("002_acrescenta_email",
    lambda c => c.executar("alter table usuarios add column email text"),
    lambda c => c.executar("alter table usuarios drop column email"))

assert m.subir() is ["001_cria_usuarios", "002_acrescenta_email"]
assert m.pendentes() is []
assert m.subir() is []              // rodar de novo não repete""", "lang": "df"},

 {"h2": "O histórico mora no banco"},
 {"p": "Numa tabela `_forge_migracoes`. Guardá-lo ali, e não num arquivo, é o que faz duas máquinas concordarem sobre o estado: **um arquivo versionado diz o que deveria ter rodado; a tabela diz o que rodou.**"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
m := Forge.migracoes(db)
m.passo("001", lambda c => c.executar("create table a (id integer)"),
        lambda c => c.executar("drop table a"))
m.subir()

e := m.estado()
assert e["aplicadas"] is 1
assert e["pendentes"] is 0
assert e["passos"][0]["reversivel"] is yes""", "lang": "df"},

 {"h2": "Falha para tudo"},
 {"p": "Continuar depois de uma migração que falhou deixa o banco num estado que nenhuma migração previu:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
m := Forge.migracoes(db)
m.passo("001", lambda c => c.executar("create table a (id integer)"))
m.passo("002", lambda c => c.executar("isto não é sql"))
m.passo("003", lambda c => c.executar("create table c (id integer)"))

monitor:
    m.subir()
handle MigrationError as e:
    assert "002" in e.message

// a 003 não rodou
assert not ("c" in Forge.tabelas(db))""", "lang": "df"},

 {"h2": "Desfazer"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
m := Forge.migracoes(db)
m.passo("001", lambda c => c.executar("create table a (id integer)"),
        lambda c => c.executar("drop table a"))
m.subir()

assert m.descer(1) is ["001"]
assert not ("a" in Forge.tabelas(db))""", "lang": "df"},
 {"p": "Só desce o que declarou como desfazer. Uma migração sem caminho de volta avisa em vez de tentar adivinhar."},
 {"callout": {"tipo": "dica", "titulo": "Escreva o `descer` mesmo que não use", "texto": "O momento em que você precisa dele é o pior momento possível para escrevê-lo. Escrever no mesmo dia da subida custa dois minutos."}},
]},
]
