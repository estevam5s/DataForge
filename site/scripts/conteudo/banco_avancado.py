# -*- coding: utf-8 -*-
"""Banco de dados — o contêiner, cada motor, e o ORM a fundo.

Nove páginas. As três primeiras respondem "como eu rodo isto de
verdade" (contêiner, produção, cada motor), e as outras cobrem o que
o ORM ganhou: escopos, paginação, has-many-through, validação.

Todo bloco `df` aqui RODA — inclusive os que falam com Postgres, que
são escritos contra SQLite quando a diferença não importa e marcados
como shell quando importa.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/banco-de-dados/docker",
"title": "O banco em contêiner",
"description": "Subir Postgres, MySQL, Redis ou Mongo com Docker e conectar — incluindo a espera que todo compose precisa e ninguém escreve.",
"blocos": [
 {"p": "O caminho normal de desenvolvimento hoje é o banco num contêiner. Esta página cobre as três coisas que quebram nesse caminho — e as três têm resposta na biblioteca."},

 {"callout": {"tipo": "dica", "titulo": "Não há driver a instalar", "texto": "`postgres.py`, `mysql.py`, `redis.py` e `mongo.py` falam o protocolo **por socket**, em Python puro. Não há `psycopg2`, `PyMySQL`, `redis-py` nem `pymongo` aqui — é o que faz `pip install dataforge-lang` bastar numa máquina sem compilador, e o que impede a versão do driver de envelhecer separada da linguagem."}},

 {"h2": "1. Subir o banco"},

 {"code": """# O jeito curto, para experimentar:
docker run -d --name loja-db \\
  -e POSTGRES_USER=forge -e POSTGRES_PASSWORD=segredo \\
  -e POSTGRES_DB=loja \\
  -p 5432:5432 postgres:16-alpine""", "lang": "bash"},

 {"p": "E o `docker-compose.yml` sai da **mesma URL** que a aplicação usa. Escrever os dois à mão é como eles divergem: o compose sobe `POSTGRES_DB=loja` e a aplicação procura `loja_dev`, e o erro só aparece na primeira consulta."},

 {"code": """adopt Arcane.Forge as Forge
adopt Arcane.Serialization as S

steady URL := "postgres://forge:segredo@localhost:5432/loja"

c := Forge.compose(URL, servico := "banco")

out $"servico:     {c['servico']}"
out $"url interna: {c['url_interna']}"
out ""
out S.to_json(c["definicao"], yes)""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "A URL de dentro não é a de fora", "texto": "Por dentro da rede do compose o host é o **nome do serviço** e a porta é a **interna do motor** — `postgres://…@banco:5432/loja`. Trocar só o host é o erro clássico de quem publica numa porta diferente: `localhost:55432` vira `banco:55432`, e nada escuta ali dentro. `url_interna` devolve as duas trocas."}},

 {"h2": "2. Esperar — “Up” não quer dizer “pronto”"},

 {"p": "O `docker compose up` volta, o contêiner aparece como *Up*, e a aplicação morre no primeiro `conectar` com **connection refused**. O contêiner do Postgres sobe, cria o cluster, **reinicia o servidor uma vez** durante a inicialização, e só então passa a escutar — são segundos. O do MySQL demora mais."},

 {"table": {"head": ["A saída comum", "Por que falha"], "rows": [
   ["`sleep 5` no script de partida", "falha na máquina lenta, e desperdiça quatro segundos na rápida"],
   ["laço de retentativa escrito à mão", "quase sempre insiste também em credencial errada, e esconde a causa atrás do prazo"],
   ["`depends_on` sem `condition`", "espera o contêiner **começar**, não ficar pronto"]]}},

 {"code": """adopt Arcane.Forge as Forge

// A espera e por RESPOSTA, e nao por relogio.
db := Forge.esperar("postgres://forge:segredo@localhost:5432/loja",
    prazo := 30.0)

out Forge.versao(db)
Forge.fechar(db)""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "Senha errada não melhora com o tempo", "texto": "`esperar` insiste só no que é **transitório** — conexão recusada, conexão redefinida, servidor iniciando. Uma credencial inválida ou um banco que não existe sobem **na hora**: insistir trinta segundos nisso é esconder a causa atrás de um prazo, e quem lê o log vê um “tempo esgotado” e vai procurar no lugar errado. Medido: 4 ms contra os 30 s do prazo."}},

 {"h2": "3. A URL vem do ambiente"},

 {"p": "Uma URL de banco no código é um segredo no repositório: ela carrega usuário e senha. Num contêiner ela nunca está no código — está no ambiente, e é isso que permite a **mesma imagem** rodar em desenvolvimento, em teste e em produção."},

 {"code": """adopt Arcane.Forge as Forge

// Procura DATABASE_URL, DB_URL e FORGE_DATABASE_URL, nesta ordem.
// Sem nenhuma delas e SEM padrao, isto e ERRO — e nao um SQLite
// calado, que e o defeito que faz alguem rodar uma semana contra o
// banco errado.
db := Forge.de_ambiente(padrao := ":memory:")

Forge.executar(db, "create table t (id integer primary key, v text)")
Forge.executar(db, "insert into t (v) values (?)", ["ok"])
assert Forge.consultar(db, "select v from t")[0]["v"] is "ok"

out "conectado pelo ambiente"
Forge.fechar(db)""", "lang": "df"},

 {"h2": "O compose completo"},

 {"code": """services:
  banco:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: forge
      POSTGRES_PASSWORD: segredo
      POSTGRES_DB: loja
    ports: ["5432:5432"]
    volumes: ["banco-dados:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U forge"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 20s

  app:
    build: .
    environment:
      # O host e o NOME DO SERVICO, e a porta e a interna.
      DATABASE_URL: postgres://forge:segredo@banco:5432/loja
    depends_on:
      banco:
        condition: service_healthy

volumes:
  banco-dados:""", "lang": "yaml"},

 {"table": {"head": ["No arquivo", "Sem ele"], "rows": [
   ["`healthcheck` com `start_period`", "as falhas normais da inicialização contam como *não saudável* e derrubam o serviço"],
   ["`depends_on: service_healthy`", "a app sobe antes do banco e falha na primeira consulta, de forma intermitente"],
   ["`volumes`", "o banco começa vazio a cada `down`"],
   ["`DATABASE_URL` no ambiente", "a senha vai para a imagem, e `docker history` a mostra"]]}},

 {"callout": {"tipo": "dica", "titulo": "A sonda e o `esperar` atacam o mesmo problema de lados diferentes", "texto": "A sonda é o **plano**: com ela, o compose só inicia a aplicação quando o banco responde. O `esperar` é a **rede de segurança**: ele cobre o `docker run` solto, o banco que reinicia em produção, e o caso em que alguém subiu os dois à mão. Ter os dois não é redundância — é que um deles não está presente em metade das situações reais."}},

 {"h2": "Os quatro motores em contêiner"},

 {"table": {"head": ["Motor", "Imagem", "URL"], "rows": [
   ["PostgreSQL", "`postgres:16-alpine`", "`postgres://forge:segredo@localhost:5432/loja`"],
   ["MySQL", "`mysql:8`", "`mysql://forge:segredo@localhost:3306/loja`"],
   ["MariaDB", "`mariadb:11`", "`mariadb://forge:segredo@localhost:3306/loja`"],
   ["Redis", "`redis:7-alpine`", "`redis://localhost:6379`"],
   ["MongoDB", "`mongo:7`", "`mongo://forge:segredo@localhost:27017/loja`"]]}},

 {"p": "Continue em [Cada motor](/docs/banco-de-dados/motores) e [Produção](/docs/banco-de-dados/producao)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/banco-de-dados/producao",
"title": "Em produção",
"description": "Pool, índices, o que medir, o que nunca fazer — e as decisões que só aparecem quando há carga.",
"blocos": [
 {"p": "O que funciona numa máquina com um usuário falha com cinquenta. Esta página é a lista do que muda."},

 {"h2": "Uma conexão por pedido não escala"},

 {"p": "Abrir conexão com Postgres custa um aperto de mão TCP, autenticação e alocação de um processo do lado do servidor — dezenas de milissegundos. Por pedido, isso domina o tempo de resposta; e o servidor tem um teto de conexões que se atinge antes do teto de CPU."},

 {"code": """adopt Arcane.Forge as Forge

// O pool abre N conexoes e as empresta. 'conexao' devolve ao fim.
pool := Forge.pool(":memory:", 4)

// Sempre com 'with': uma conexao pegada e nao devolvida some do
// pool para sempre, e o 'with' devolve inclusive se o corpo falhar.
cycle i from 1 to 8:
    with Forge.conexao(pool) as db:
        Forge.consultar(db, "select 1 as um")

out $"oito pedidos, {pool.estado()['tamanho']} conexoes"
""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "O tamanho do pool não é “quanto maior melhor”", "texto": "Cada conexão do Postgres é um **processo** do lado do servidor, com memória própria. Um pool de 100 por instância, com quatro instâncias, são 400 processos — e o servidor passa mais tempo trocando de contexto que respondendo. A conta que funciona na prática é próxima de `núcleos × 2 + fusos de disco`, por **todo o conjunto**, e não por instância. Quando o número precisa ser maior, o que falta é um *pooler* (PgBouncer), e não um pool maior."}},

 {"h2": "O índice que falta"},

 {"p": "A consulta que responde em 3 ms com mil linhas responde em 3 s com um milhão — e nada no código mudou. `explain` mostra o plano, e é ele que diz se o banco está varrendo a tabela."},

 {"code": """adopt Arcane.Database as Db

db := Db.connect(":memory:")
Db.execute(db, "create table pedido (id integer primary key, cliente_id integer, total real)")

cycle i from 1 to 500:
    Db.execute(db, "insert into pedido (cliente_id, total) values (?, ?)",
        [i % 50, i * 1.5])

// Sem indice: varredura.
antes := Db.explain(db, "select * from pedido where cliente_id = 7")
out $"antes:  {antes}"

Db.execute(db, "create index idx_pedido_cliente on pedido (cliente_id)")

depois := Db.explain(db, "select * from pedido where cliente_id = 7")
out $"depois: {depois}"

Db.close(db)""", "lang": "df"},

 {"table": {"head": ["Indexe", "Porque"], "rows": [
   ["toda chave estrangeira", "é por onde as relações do ORM buscam — e sem índice cada `com()` vira varredura"],
   ["a coluna de todo `onde` frequente", "é o caso óbvio, e o mais esquecido"],
   ["a coluna de `ordenar` quando há `limite`", "sem ele o banco ordena a tabela inteira para devolver dez linhas"],
   ["**não** indexe tudo", "todo índice é escrito em cada `insert`; uma tabela com oito índices escreve nove vezes"]]}},

 {"h2": "O que nunca fazer"},

 {"table": {"head": ["Nunca", "O que acontece"], "rows": [
   ["`select *` numa listagem", "traz colunas grandes que a tela não usa, e o custo é de rede"],
   ["listagem sem `limite`", "a forma mais comum de derrubar uma aplicação — e a `paginar` do ORM já vem com teto"],
   ["consulta dentro de laço", "o N+1: use [`com()`](/docs/orm/atraves)"],
   ["`order by` por coluna vinda da URL, sem lista", "injeção por identificador; o `order_by` do `Arcane.Database` recusa o que não parece nome"],
   ["migração sem `down`", "desfazer exige editar o banco à mão"],
   ["transação aberta esperando rede", "ela segura locks enquanto o HTTP de terceiro demora"]]}},

 {"callout": {"tipo": "atencao", "titulo": "A rota do Kiln é concorrente, e é invisível", "texto": "O Kiln usa `ThreadingHTTPServer`: cada pedido roda numa thread. O `Arcane.Database` serializa o acesso à conexão — sem isso, a primeira consulta de qualquer servidor estoura —, mas **estado em memória compartilhado entre rotas não é protegido**. Medido: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**. O `check` avisa (`escrita-concorrente`)."}},

 {"h2": "O que medir"},

 {"table": {"head": ["Medida", "Como", "O que ela denuncia"], "rows": [
   ["consultas por pedido", "contar no log", "N+1 — o número cresce com o tamanho da página"],
   ["p95 da consulta", "`Arcane.Perfil`", "a média esconde a cauda, e é a cauda que o usuário sente"],
   ["conexões em uso", "`pool.estado()`", "pool no teto = pedidos esperando"],
   ["plano da consulta lenta", "`Db.explain`", "índice faltando"],
   ["tamanho das tabelas", "`Db.stats`", "a tabela que cresce sem retenção"]]}},

 {"p": "Continue em [Transações e pool](/docs/banco-de-dados/transacoes) e [O banco em contêiner](/docs/banco-de-dados/docker)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/banco-de-dados/postgres",
"title": "PostgreSQL",
"description": "O driver, os tipos, os parâmetros posicionais e o que o Postgres não perdoa — com o contêiner pronto.",
"blocos": [
 {"p": "O driver fala o **protocolo v3** por socket: aperto de mão, autenticação (`md5` e `scram-sha-256`), consulta simples e consulta estendida com parâmetros. Não há `psycopg` no caminho."},

 {"h2": "Conectar"},

 {"code": """adopt Arcane.Forge as Forge

// O motor sai da URL; a porta padrao e 5432.
db := Forge.esperar("postgres://forge:segredo@localhost:5432/loja",
    prazo := 30.0)

out Forge.versao(db)
out $"tabelas: {len(Forge.tabelas(db))}"
Forge.fechar(db)""", "lang": "df"},

 {"h2": "Os parâmetros são `$1`, e não `?`"},

 {"p": "Cada banco tem a sua marca de parâmetro, e trocá-la é o primeiro erro de quem vem do SQLite. O construtor de consultas cuida disso sozinho — o cuidado é para o SQL escrito à mão."},

 {"table": {"head": ["Motor", "Marca", "Exemplo"], "rows": [
   ["SQLite", "`?`", "`where id = ?`"],
   ["PostgreSQL", "`$1`, `$2`", "`where id = $1`"],
   ["MySQL / MariaDB", "`?`", "`where id = ?`"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Parâmetro, sempre — e não por estilo", "texto": "`$\"select * from u where id = {id}\"` é injeção de SQL, e o `dataforge seguranca` acusa (`sql-concatenado`). O valor vai por parâmetro **inclusive** quando ele “é só um número”: o dia em que ele deixa de ser um número é o dia do incidente."}},

 {"h2": "Os tipos que só o Postgres tem"},

 {"table": {"head": ["Tipo", "Chega como", "Observação"], "rows": [
   ["`serial` / `bigserial`", "Integer", "a sequência é do servidor; o `id` volta no `criar`"],
   ["`numeric` / `decimal`", "texto exato, convertido", "**não** vira Float: o arredondamento binário é o que `Arcane.Decimal` existe para evitar"],
   ["`timestamp` / `timestamptz`", "DataHora", "guarde em UTC; o fuso é de quem apresenta"],
   ["`jsonb`", "texto", "use `Arcane.Serialization` para ler"],
   ["`text[]`", "texto", "arrays não têm tipo próprio na linguagem"],
   ["`uuid`", "texto", "`Crypto.uuid4()` gera"]]}},

 {"h2": "O que o Postgres não perdoa e o SQLite perdoa"},

 {"table": {"head": ["No SQLite passa", "No Postgres", "Porque"], "rows": [
   ["`\"texto\"` como literal", "erro", "aspas duplas são **identificador**; literal é aspas simples"],
   ["inserir texto numa coluna `integer`", "erro", "o SQLite tem afinidade de tipo, e não tipo"],
   ["`select a, b … group by a`", "erro", "toda coluna do `select` tem de estar no `group by` ou numa agregação"],
   ["comparar `integer` com `text`", "erro", "não há conversão implícita"],
   ["tabela sem chave primária", "passa, e dói depois", "replicação e `ON CONFLICT` precisam dela"]]}},

 {"callout": {"tipo": "dica", "titulo": "Teste contra o banco de verdade", "texto": "O SQLite é ótimo para o teste rápido e **mente sobre tipos**. A suíte deste repositório roda o ORM contra um Postgres em contêiner justamente por isso: o que quebra em produção é o que o SQLite deixou passar. Veja `tests/test_forge_docker.py`."}},

 {"p": "Continue em [O banco em contêiner](/docs/banco-de-dados/docker)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/banco-de-dados/mysql",
"title": "MySQL e MariaDB",
"description": "Um driver para os dois, a autenticação que quase todo driver caseiro não faz, e as diferenças que importam.",
"blocos": [
 {"p": "O mesmo driver serve os dois: o protocolo é o mesmo, e o que muda é o método de autenticação padrão e alguns nomes de variável."},

 {"code": """adopt Arcane.Forge as Forge

db := Forge.esperar("mysql://forge:segredo@localhost:3306/loja",
    prazo := 40.0)

out Forge.versao(db)
Forge.fechar(db)""", "lang": "df"},

 {"callout": {"tipo": "dica", "titulo": "O `caching_sha2_password` é onde os drivers caseiros param", "texto": "O MySQL 8 mudou o padrão de `mysql_native_password` para `caching_sha2_password`. Ele tem dois caminhos: o **rápido**, que usa o cache do servidor, e o **completo**, que exige trocar uma chave RSA. Quase todo driver escrito à mão implementa só o rápido — e falha na primeira conexão de uma senha que o servidor ainda não cacheou, que é justamente a primeira conexão depois de subir o contêiner. Este faz os dois."}},

 {"h2": "As diferenças que importam"},

 {"table": {"head": ["", "MySQL / MariaDB", "PostgreSQL"], "rows": [
   ["parâmetro", "`?`", "`$1`"],
   ["auto incremento", "`auto_increment`", "`serial`"],
   ["texto sem limite", "`text`", "`text`"],
   ["texto com limite", "`varchar(n)` — e `n` é **obrigatório** num índice", "`text` indexa direto"],
   ["booleano", "`tinyint(1)`", "`boolean`"],
   ["`insert … on duplicate`", "existe", "é `on conflict`"],
   ["comparação de texto", "**insensível** a maiúsculas por padrão", "sensível"]]}},

 {"callout": {"tipo": "atencao", "titulo": "A comparação insensível é uma armadilha silenciosa", "texto": "No MySQL, `where email = 'Ana@x.com'` encontra `ana@x.com` — e o mesmo código no Postgres não encontra. Um sistema migrado de um para o outro passa a rejeitar logins que funcionavam, sem nenhum erro no meio. Normalize na **aplicação** (`lower()` antes de gravar e antes de buscar) e o comportamento deixa de depender do motor."}},

 {"h2": "Codificação"},

 {"p": "Use `utf8mb4`, sempre. O `utf8` do MySQL guarda **três** bytes por caractere e não cabe emoji nem vários ideogramas — e o sintoma é um texto truncado na gravação, sem erro."},

 {"code": """docker run -d --name loja-my \\
  -e MYSQL_ROOT_PASSWORD=segredo \\
  -e MYSQL_DATABASE=loja \\
  -e MYSQL_USER=forge -e MYSQL_PASSWORD=segredo \\
  -p 3306:3306 mysql:8 \\
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci""", "lang": "bash"},

 {"p": "Continue em [Cada motor](/docs/banco-de-dados/motores)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/banco-de-dados/chave-valor",
"title": "Redis e MongoDB",
"description": "Os dois que não são SQL: o que cada um resolve, o que não resolve, e por que o driver cabe em poucas linhas.",
"blocos": [
 {"p": "Os dois entram pela mesma porta (`Forge.conectar`) e respondem a perguntas diferentes das do SQL. Usá-los como banco principal é o erro mais caro dos dois."},

 {"h2": "Redis"},

 {"p": "Memória, com persistência opcional. O que ele faz melhor que qualquer banco: **expirar sozinho**. Cache, sessão, limite de taxa, fila simples — tudo isso é um valor com prazo."},

 {"code": """adopt Arcane.Forge as Forge

// Comentado porque exige o conteiner:
//
//   r := Forge.conectar("redis://localhost:6379")
//   Forge.executar(r, "SET sessao:abc {\\"id\\": 7}")
//   Forge.executar(r, "EXPIRE sessao:abc 3600")
//   out Forge.consultar(r, "GET sessao:abc")
//
// O protocolo (RESP) e texto, e e por isso que o driver cabe em
// poucas linhas: cada comando e uma lista de strings, e cada
// resposta tem um prefixo de um caractere dizendo o que ela e.

out "veja o exemplo acima; ele precisa de um Redis no ar\"""", "lang": "df"},

 {"table": {"head": ["Use Redis para", "Não use para"], "rows": [
   ["cache com prazo", "o dado que não pode ser perdido"],
   ["sessão", "relação entre entidades"],
   ["limite de taxa compartilhado entre processos", "relatório"],
   ["fila simples", "fila com garantia forte — isso é um broker"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Sem prazo, o Redis vira um vazamento com nome bonito", "texto": "Uma chave sem `EXPIRE` fica para sempre, e a memória é o recurso finito dali. O padrão que funciona é: **toda** chave nasce com prazo, e a exceção é escrita e justificada. O contrário — pôr prazo depois — é o que enche a instância às três da manhã."}},

 {"h2": "MongoDB"},

 {"p": "Documentos, sem esquema declarado. O driver fala o *wire protocol* com BSON — e `bson.py` existe aqui pelo mesmo motivo dos outros: sem `pymongo`."},

 {"table": {"head": ["Use Mongo para", "Pense duas vezes"], "rows": [
   ["documento cuja forma varia de verdade", "dado com relações — `join` não é o forte dele"],
   ["esquema que muda toda semana no começo", "quando a forma estabilizar, o SQL volta a ser melhor"],
   ["agregação sobre eventos", "transação entre coleções"]]}},

 {"callout": {"tipo": "dica", "titulo": "“Sem esquema” não quer dizer “sem forma”", "texto": "O esquema continua existindo — ele só deixou de estar no banco e passou a estar espalhado pelo código, em cada lugar que lê o documento. Quando isso incomoda, a resposta aqui é validar na fronteira: [`Objetos.de_vault`](/docs/biblioteca/objetos) com a lista de tipos, ou um [`record`](/docs/oop) com os campos declarados."}},

 {"p": "Continue em [Cada motor](/docs/banco-de-dados/motores) e [O banco em contêiner](/docs/banco-de-dados/docker)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/orm/escopos",
"title": "Escopos e paginação",
"description": "O filtro com nome, reaproveitável e encadeável — e a página que traz o total que a tela precisa.",
"blocos": [
 {"p": "Duas peças pequenas que decidem se uma listagem de verdade é escrita uma vez ou dez."},

 {"h2": "Escopo: o filtro com nome"},

 {"p": "`ativos`, `do_mes`, `sem_pagamento` — o filtro que aparece em dez lugares e, escrito dez vezes, **diverge em um deles**. Quando a regra muda (*“ativo agora exclui suspenso”*), há um lugar só para mudar; e o nome documenta a intenção, que um `onde` solto não faz."},

 {"code": """adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Pedido := Forge.modelo("Pedido", {
    "id": "Serial", "cliente_id": "Inteiro",
    "status": "Texto", "total": "Decimal"
})
Forge.ligar(Pedido, db)
Pedido.migrar()

Pedido.escopo("abertos", lambda q => q.onde("status", "aberto"))
Pedido.escopo("grandes", lambda q => q.onde("total", ">", 100.0))

Pedido.criar({"cliente_id": 1, "status": "aberto", "total": 250.0})
Pedido.criar({"cliente_id": 1, "status": "aberto", "total": 30.0})
Pedido.criar({"cliente_id": 2, "status": "pago", "total": 900.0})

out $"abertos:  {len(Pedido.usar('abertos').buscar())}"
out $"grandes:  {len(Pedido.usar('grandes').buscar())}"

// Encadear e o que separa um escopo de um atalho.
ambos := Pedido.usar("grandes", Pedido.usar("abertos")).buscar()
out $"abertos E grandes: {len(ambos)}"
assert len(ambos) is 1

Forge.fechar(db)""", "lang": "df"},

 {"callout": {"tipo": "dica", "titulo": "Um escopo desconhecido diz quais existem", "texto": "`Pedido.usar(\"abertoss\")` não devolve lista vazia — ele levanta, e a mensagem lista os escopos que o modelo tem. Devolver vazio silenciosamente é como um erro de digitação vira um relatório com zero linhas, e ninguém desconfia do relatório."}},

 {"h2": "Paginação"},

 {"p": "Uma listagem sem teto é a forma mais comum de uma aplicação travar. E uma paginação sem **total** não desenha: a tela não sabe quantos botões pôr, e a saída comum é buscar tudo para contar — exatamente o que a paginação existe para evitar."},

 {"code": """adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()
Post := Forge.modelo("Post", {"id": "Serial", "titulo": "Texto"})
Forge.ligar(Post, db)
Post.migrar()

cycle i from 1 to 25:
    Post.criar({"titulo": $"Post {i}"})

p := Post.paginar(pagina := 2, tamanho := 10)

out $"pagina {p['pagina']} de {p['paginas']}"
out $"{len(p['linhas'])} linhas, de {p['total']} no total"
out $"anterior: {p['tem_anterior']}  proxima: {p['tem_proxima']}"

assert p["total"] is 25
assert p["paginas"] is 3

// Pagina fora da faixa e VAZIA, e nao erro: '?pagina=999' e um
// favorito de seis meses atras, e nao um ataque.
fora := Post.paginar(pagina := 999)
assert len(fora["linhas"]) is 0
assert fora["total"] is 25

Forge.fechar(db)""", "lang": "df"},

 {"table": {"head": ["Decisão", "Sem ela"], "rows": [
   ["devolve `total` e `paginas`", "a tela busca tudo para contar"],
   ["página fora da faixa é **vazia**", "um link antigo quebra a listagem"],
   ["`tamanho` tem teto de 500", "`?tamanho=999999` derruba a página"],
   ["aceita uma consulta pronta", "paginar um escopo exigiria repetir o filtro"]]}},

 {"code": """adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()
Post := Forge.modelo("Post", {"id": "Serial", "titulo": "Texto", "status": "Texto"})
Forge.ligar(Post, db)
Post.migrar()
Post.escopo("publicados", lambda q => q.onde("status", "publicado"))

cycle i from 1 to 12:
    Post.criar({"titulo": $"P{i}",
        "status": "publicado" given i % 2 is 0 otherwise "rascunho"})

// Paginar SOBRE um escopo: o total ja e o do escopo.
p := Post.paginar(pagina := 1, tamanho := 4,
    consulta := Post.usar("publicados"))

out $"publicados: {p['total']} em {p['paginas']} pagina(s)"
assert p["total"] is 6

Forge.fechar(db)""", "lang": "df"},

 {"p": "Continue em [Relações](/docs/orm/relacoes) e [Carga antecipada](/docs/orm/atraves)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/orm/atraves",
"title": "Carga antecipada e o N+1",
"description": "Duas consultas em vez de cento e uma — e a relação que atravessa um terceiro modelo.",
"blocos": [
 {"p": "O N+1 é o defeito de desempenho mais comum de qualquer ORM, e o mais fácil de não notar: ele **funciona**. A página abre, os dados estão certos, e a lentidão cresce com o tamanho da lista — o que em desenvolvimento, com dez linhas, não aparece."},

 {"h2": "O problema"},

 {"code": """// ERRADO — uma consulta para os clientes, e uma POR CLIENTE.
// Com cem clientes, sao cento e uma consultas.
//
//   clientes := Cliente.todos()
//   cycle c in clientes:
//       pedidos := Pedido.onde("cliente_id", c["id"]).buscar()
//
// CERTO — duas consultas, para qualquer quantidade:
//
//   clientes := Cliente.com(Cliente.todos(), "pedidos")

out "o numero de consultas nao pode crescer com o numero de linhas\"""", "lang": "df"},

 {"code": """adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Cliente := Forge.modelo("Cliente", {"id": "Serial", "nome": "Texto"})
Pedido := Forge.modelo("Pedido", {"id": "Serial", "cliente_id": "Inteiro", "total": "Decimal"})
cycle m in [Cliente, Pedido]:
    Forge.ligar(m, db)
    m.migrar()

Cliente.tem_muitos("pedidos", "Pedido", chave_externa := "cliente_id")
Pedido.pertence_a("cliente", "Cliente", chave_local := "cliente_id")

ana := Cliente.criar({"nome": "Ana"})
bob := Cliente.criar({"nome": "Bob"})
Pedido.criar({"cliente_id": ana["id"], "total": 99.9})
Pedido.criar({"cliente_id": ana["id"], "total": 45.0})
Pedido.criar({"cliente_id": bob["id"], "total": 12.0})

// DUAS consultas: uma para os clientes, outra para todos os
// pedidos deles.
cycle c in Cliente.com(Cliente.todos(), "pedidos"):
    out $"{c['nome']}: {len(c['pedidos'])} pedido(s)"

// E o outro lado, tambem em duas.
cycle p in Pedido.com(Pedido.todos(), "cliente"):
    out $"pedido {p['id']} e de {p['cliente']['nome']}"

Forge.fechar(db)""", "lang": "df"},

 {"h2": "A relação que atravessa um terceiro"},

 {"p": "O autor **não tem** comentários: ele tem posts, e os posts têm comentários. É a relação que não tem nome no dia a dia e aparece em todo sistema — e sem uma peça para ela, o caminho natural é carregar os posts, tirar os ids e consultar de novo. Quem escreve isso tende a fazer uma consulta por post: o N+1 com um passo a mais."},

 {"code": """adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Autor := Forge.modelo("Autor", {"id": "Serial", "nome": "Texto"})
Post := Forge.modelo("Post", {"id": "Serial", "autor_id": "Inteiro", "titulo": "Texto"})
Comentario := Forge.modelo("Comentario", {"id": "Serial", "post_id": "Inteiro", "texto": "Texto"})
cycle m in [Autor, Post, Comentario]:
    Forge.ligar(m, db)
    m.migrar()

// Autor -> (Post) -> Comentario
Autor.tem_muitos_atraves("comentarios", "Comentario", "Post")

ana := Autor.criar({"nome": "Ana"})
bob := Autor.criar({"nome": "Bob"})
p1 := Post.criar({"autor_id": ana["id"], "titulo": "Um"})
p2 := Post.criar({"autor_id": ana["id"], "titulo": "Dois"})
p3 := Post.criar({"autor_id": bob["id"], "titulo": "Tres"})

cycle t in ["otimo", "concordo", "hmm"]:
    Comentario.criar({"post_id": p1["id"], "texto": t})
Comentario.criar({"post_id": p2["id"], "texto": "no outro"})
Comentario.criar({"post_id": p3["id"], "texto": "do bob"})

// TRES consultas: autores, posts deles, comentarios desses posts.
cycle a in Autor.com(Autor.todos(), "comentarios"):
    out $"{a['nome']}: {len(a['comentarios'])} comentario(s)"

assert len(Autor.com(Autor.todos(), "comentarios")[0]["comentarios"]) is 4

Forge.fechar(db)""", "lang": "df"},

 {"h2": "As cinco relações"},

 {"table": {"head": ["Relação", "Consultas", "Quando"], "rows": [
   ["`tem_um`", "2", "um perfil por usuário"],
   ["`tem_muitos`", "2", "os pedidos de um cliente"],
   ["`pertence_a`", "2", "o cliente de um pedido"],
   ["`muitos_para_muitos`", "2 (com tabela-ponte)", "as etiquetas de um post"],
   ["`tem_muitos_atraves`", "3", "os comentários de um autor, pelos posts"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Indexe a chave estrangeira", "texto": "A carga antecipada troca N+1 por duas consultas — e a segunda é um `where chave_externa in (…)`. Sem índice nessa coluna, ela é uma **varredura da tabela inteira**, e o ganho some. É o item mais esquecido da lista de índices, porque a relação funciona sem ele."}},

 {"p": "Continue em [Escopos e paginação](/docs/orm/escopos) e [Em produção](/docs/banco-de-dados/producao)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/orm/validacao",
"title": "Validação, ganchos e marcas",
"description": "O que o modelo recusa antes de gravar, o que ele preenche sozinho, e a remoção que não apaga.",
"blocos": [
 {"p": "Três coisas que todo sistema escreve à mão em cada lugar — e que, escritas em cada lugar, são esquecidas em um deles."},

 {"h2": "Validar devolve TODOS os problemas"},

 {"p": "Parar no primeiro erro faz o formulário ser corrigido campo a campo, num vaivém: a pessoa conserta o nome, envia, e descobre que o e-mail também estava errado. A lista inteira é o que a tela precisa."},

 {"code": """adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Usuario := Forge.modelo("Usuario", {"id": "Serial"})
Usuario.campo("nome", "Texto", obrigatorio := yes)
Usuario.campo("email", "Texto", obrigatorio := yes, unico := yes)
Usuario.campo("idade", "Inteiro", padrao := 0)
Forge.ligar(Usuario, db)
Usuario.migrar()

// Faltam os DOIS obrigatorios, e a lista traz os dois.
problemas := Usuario.validar({"idade": 30})
out $"{len(problemas)} problema(s) — e nao so o primeiro:"
cycle p in problemas:
    out $"   {p['campo']}: {p['motivo']}"
assert len(problemas) is 2

assert len(Usuario.validar({"nome": "Ana", "email": "ana@x.com", "idade": 30})) is 0
out "o valido passa"

Forge.fechar(db)""", "lang": "df"},

 {"h2": "Ganchos"},

 {"code": """adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Conta := Forge.modelo("Conta", {"id": "Serial", "email": "Texto"})
Forge.ligar(Conta, db)
Conta.migrar()

// O e-mail entra sempre em minusculas. Normalizar na aplicacao e o
// que faz o comportamento deixar de depender do motor: o MySQL
// compara sem diferenciar maiusculas, e o Postgres diferencia.
action normalizar(dados):
    dados["email"] := (dados["email"] ?? "").lower()
    yield dados

Conta.antes_de_salvar(normalizar)

c := Conta.criar({"email": "Ana@LOJA.com"})
out $"gravado como: {c['email']}"
assert c["email"] is "ana@loja.com"

Forge.fechar(db)""", "lang": "df"},

 {"h2": "Marcas de tempo e remoção suave"},

 {"table": {"head": ["", "O que faz", "Por que"], "rows": [
   ["`com_marcas_de_tempo()`", "`criado_em` e `atualizado_em`, mantidos sozinhos", "a pergunta *“quando isto mudou?”* aparece em toda investigação, e não dá para responder depois"],
   ["`com_remocao_suave()`", "`remover` **marca**; as buscas ignoram o marcado", "apagar de verdade é irreversível, e o pedido mais comum depois de um apagar é desfazer"]]}},

 {"code": """adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Nota := Forge.modelo("Nota", {"id": "Serial", "texto": "Texto"})
Nota.com_marcas_de_tempo()
Nota.com_remocao_suave()
Forge.ligar(Nota, db)
Nota.migrar()

n := Nota.criar({"texto": "primeira"})
out $"criado_em preenchido: {n['criado_em'] isnt void}"

Nota.criar({"texto": "segunda"})
assert Nota.contar() is 2

Nota.remover(n["id"])

// As buscas ignoram o removido — mas ele continua no banco.
assert Nota.contar() is 1
out "removida da vista, e nao do disco"

Forge.fechar(db)""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "Remoção suave e LGPD se contradizem", "texto": "O direito à eliminação pede que o dado **saia**, e a remoção suave o mantém. As duas convivem com uma regra escrita: soft delete para o desfazer de curto prazo (dias), e um processo de expurgo que apaga de verdade no fim do prazo — **inclusive nas cópias de segurança**, que é onde quase todo mundo falha. Veja [Operação e conformidade](/docs/seguranca/operacao)."}},

 {"p": "Continue em [Migrações](/docs/orm/migracoes) e [Escopos](/docs/orm/escopos)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/banco-de-dados/receitas",
"title": "Receitas",
"description": "Os seis problemas que todo sistema com banco resolve — com o código que funciona e o que dá errado na versão ingênua.",
"blocos": [
 {"p": "Cada uma destas tem uma versão ingênua que funciona no teste e falha com concorrência, com volume, ou com um link antigo."},

 {"h2": "1. Inserir sem duplicar"},

 {"code": """adopt Arcane.Database as Db

db := Db.connect(":memory:")
Db.execute(db, "create table produto (sku text primary key, nome text, preco real)")

// 'upsert': insere, ou atualiza se a chave ja existe. A versao
// ingenua — buscar, e inserir se nao achou — tem uma janela entre a
// busca e a insercao, e duas importacoes ao mesmo tempo duplicam.
Db.upsert(db, "produto", {"sku": "A1", "nome": "Cafe", "preco": 32.0}, ["sku"])
Db.upsert(db, "produto", {"sku": "A1", "nome": "Cafe", "preco": 35.0}, ["sku"])

linhas := Db.query(db, "select * from produto")
assert len(linhas) is 1
out $"uma linha, preco atualizado: {linhas[0]['preco']}"

Db.close(db)""", "lang": "df"},

 {"h2": "2. Contador que não perde"},

 {"code": """adopt Arcane.Database as Db

db := Db.connect(":memory:")
Db.execute(db, "create table estoque (id integer primary key, qtd integer)")
Db.execute(db, "insert into estoque (id, qtd) values (1, 100)")

// 'increment' faz a conta NO BANCO. A versao ingenua — ler, somar,
// gravar — perde atualizacoes: duas vendas ao mesmo tempo leem 100,
// as duas gravam 99, e uma some.
Db.increment(db, "estoque", "qtd", -1, {"id": 1})
Db.increment(db, "estoque", "qtd", -1, {"id": 1})

assert Db.query(db, "select qtd from estoque")[0]["qtd"] is 98
out "duas baixas, duas contadas"

Db.close(db)""", "lang": "df"},

 {"h2": "3. Listagem paginada"},

 {"code": """adopt Arcane.Database as Db

db := Db.connect(":memory:")
Db.execute(db, "create table item (id integer primary key, nome text)")
cycle i from 1 to 40:
    Db.execute(db, "insert into item (nome) values (?)", [$"Item {i}"])

// 'paginate' devolve o total junto — sem ele a tela nao sabe
// quantos botoes desenhar.
p := Db.paginate(db, "item", 2, 15)
out $"pagina {p['pagina']} de {p['paginas']}: {len(p['itens'])} de {p['total']}"
assert p["total"] is 40
assert p["tem_anterior"]

Db.close(db)""", "lang": "df"},

 {"h2": "4. Busca textual"},

 {"code": """adopt Arcane.Database as Db

db := Db.connect(":memory:")
Db.execute(db, "create table artigo (id integer primary key, titulo text, corpo text)")
Db.execute(db, "insert into artigo (titulo, corpo) values (?, ?)",
    ["Cafe especial", "sobre torra e moagem"])
Db.execute(db, "insert into artigo (titulo, corpo) values (?, ?)",
    ["Cha verde", "sobre temperatura da agua"])

// FTS5: um indice de verdade. 'like %termo%' varre a tabela
// inteira, e o custo cresce com o tamanho.
Db.create_search(db, "artigo", ["titulo", "corpo"])

r := Db.search(db, "artigo", "torra")
out $"achou: {len(r)}"
assert len(r) is 1

Db.close(db)""", "lang": "df"},

 {"h2": "5. Exportar sem carregar tudo"},

 {"code": """adopt Arcane.Forge as Forge
adopt Arcane.OS as OS
adopt Arcane.IO as IO

db := Forge.memoria()
Forge.executar(db, "create table venda (id integer primary key, valor real)")
cycle i from 1 to 100:
    Forge.executar(db, "insert into venda (valor) values (?)", [i * 1.5])

caminho := $"{OS.temp_dir()}/df-vendas-{randint(100000, 999999)}.csv"

// 'para_csv' recebe as LINHAS, e nao a tabela: assim ele exporta o
// resultado de qualquer consulta, e nao so uma tabela inteira.
Forge.para_csv(Forge.consultar(db, "select id, valor from venda"), caminho)

conteudo := IO.read(caminho)
// O CSV exportado tem cabecalho mais uma linha por venda.
assert len(conteudo) bigger 100
assert "valor" in conteudo
out $"{len(conteudo)} bytes exportados, com cabecalho"

IO.delete(caminho)
Forge.fechar(db)""", "lang": "df"},

 {"h2": "6. Migração que desfaz"},

 {"code": """adopt Arcane.Forge as Forge

db := Forge.memoria()
m := Forge.migracoes(db)

// O passo recebe ACOES, e nao texto de SQL. A diferenca importa:
// uma migracao de verdade quase nunca e um comando so — ela cria a
// tabela, preenche a coluna nova a partir da antiga, e so entao
// derruba a antiga. Com texto, isso viraria uma lista de strings e
// uma regra sobre a ordem delas.
action criar(c):
    Forge.executar(c, "create table cliente (id integer primary key, nome text)")

action derrubar(c):
    Forge.executar(c, "drop table cliente")

m.passo("001_cria_cliente", criar, derrubar)

m.subir()
assert "cliente" in Forge.tabelas(db)
out "aplicada"

// O 'down' e o que torna o erro reversivel. Uma migracao sem ele
// exige editar o banco a mao — as tres da manha, com pressa.
m.descer()
assert "cliente" not in Forge.tabelas(db)
out "desfeita"

Forge.fechar(db)""", "lang": "df"},

 {"p": "Continue em [Em produção](/docs/banco-de-dados/producao) e [O banco em contêiner](/docs/banco-de-dados/docker)."},
]},
]
