import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Forge — banco de dados",
  description: "Cinco motores, uma interface, zero dependências.",
};

const blocos: Bloco[] = [
  {"p": "**Forge** conecta a PostgreSQL, MySQL, MariaDB, MongoDB, Redis e SQLite. Trocar o motor troca a URL, e mais nada:"},
  { code: `adopt Forge

db := Forge.conectar("postgres://usuario:senha@localhost:5432/app")
// ou "mysql://root@localhost/app"
// ou "mongodb://localhost/app"
// ou "redis://localhost"
// ou "dados.db"                    — SQLite

out Forge.versao(db)`, lang: 'df' },
  {"h2": "Sem dependência nenhuma"},
  {"p": "Cada driver fala o protocolo do seu banco, por socket. Não há `psycopg2`, `PyMySQL`, `redis-py` nem `pymongo` aqui — há um arquivo por protocolo, implementando a especificação publicada de cada servidor."},
  {"p": "O custo foi escrevê-los. O que se ganha é que `pip install dataforge` funciona numa máquina sem compilador, e a versão do driver nunca briga com a de outro pacote."},
  {"table": {"head": ["Motor", "Autenticação", "Testado contra"], "rows": [["PostgreSQL", "SCRAM-SHA-256, MD5, trust", "16"], ["MySQL", "caching_sha2_password (com RSA), mysql_native_password", "8.4"], ["MariaDB", "mysql_native_password", "11"], ["Redis", "AUTH com usuário e senha", "7.4"], ["MongoDB", "SCRAM-SHA-256 e SHA-1", "7.0"], ["SQLite", "—", "o do Python"]]}},
  {"h2": "Primeiro programa"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")

Forge.executar(db, """
    create table produtos (
        id integer primary key autoincrement,
        nome text not null,
        preco real
    )
""")

Forge.de(db, "produtos").inserir([
    {"nome": "Teclado", "preco": 250.0},
    {"nome": "Mouse", "preco": 90.0}
])

caros := Forge.de(db, "produtos").onde("preco", ">=", 100).buscar()
assert len(caros) is 1
assert caros[0]["nome"] is "Teclado"`, lang: 'df' },
  {"h2": "Valores nunca entram no texto da consulta"},
  {"p": "Esta é a garantia central, e ela vale para o construtor e para o SQL escrito à mão:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table u (id integer primary key, nome text)")

malicioso := "'; drop table u; --"
Forge.de(db, "u").inserir({"nome": malicioso})

// a tabela continua lá: o valor foi tratado como dado, não como SQL
assert "u" in Forge.tabelas(db)
assert Forge.de(db, "u").contar() is 1`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Injeção é impossível por construção", "texto": "Não é disciplina de quem escreve: o construtor **não tem** como pôr um valor no texto. A lista de operadores também é fechada — um operador vindo de variável seria outro caminho de injeção."}},
  {"h2": "Erros que dizem o que houve"},
  {"p": "Cada erro do servidor vira uma classe da linguagem, capturável por família:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table u (id integer primary key, email text unique)")
Forge.de(db, "u").inserir({"email": "a@b.co"})

monitor:
    Forge.de(db, "u").inserir({"email": "a@b.co"})
handle ConstraintError as e:
    assert "UNIQUE" in e.message`, lang: 'df' },
  {"table": {"head": ["Classe", "Quando"], "rows": [["`ConnectionError`", "o servidor não respondeu ou recusou"], ["`AuthenticationError`", "usuário ou senha inválidos"], ["`QueryError`", "SQL inválido, tabela ou coluna inexistente"], ["`ConstraintError`", "chave única, estrangeira, ou `not null`"], ["`TransactionError`", "deadlock, ou confirmar sem transação aberta"], ["`PoolExhaustedError`", "todas as conexões ocupadas"], ["`RecordNotFoundError`", "`buscar_ou_erro` não achou"], ["`ValidationError`", "o modelo recusou os dados"]]}},
  {"p": "Todas descendem de `DatabaseError`, então `handle DatabaseError` pega qualquer uma. Ver [catálogo de erros](/docs/erros)."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/banco-de-dados/consultas", "title": "Construtor de consultas", "desc": "onde, junções, agregados, paginação"}, {"href": "/docs/banco-de-dados/transacoes", "title": "Transações e pool", "desc": "e por que 'transacao' com bloco é a única forma segura"}, {"href": "/docs/banco-de-dados/motores", "title": "Cada motor", "desc": "o que só existe no PostgreSQL, no Redis, no Mongo"}, {"href": "/docs/orm", "title": "ORM", "desc": "modelos, validação e relações sem N+1"}, {"href": "/docs/orm/migracoes", "title": "Migrações", "desc": "com histórico no banco, não num arquivo"}]},
];

const headings = [{ id: 'sem-dependencia-nenhuma', text: "Sem dependência nenhuma", level: 2 as const }, { id: 'primeiro-programa', text: "Primeiro programa", level: 2 as const }, { id: 'valores-nunca-entram-no-texto-da-consulta', text: "Valores nunca entram no texto da consulta", level: 2 as const }, { id: 'erros-que-dizem-o-que-houve', text: "Erros que dizem o que houve", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Forge — banco de dados"}
      description={"Cinco motores, uma interface, zero dependências."}
      href={"/docs/banco-de-dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
