import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Cada motor",
  description: "O que a interface comum cobre, e o que só existe em cada um.",
};

const blocos: Bloco[] = [
  {"p": "A interface comum cobre o que faz sentido em todos: conectar, consultar, fechar. O resto cada motor expõe pelo que ele é — **um ORM que finge que Redis é uma tabela produz código que parece portável e não é**."},
  {"h2": "SQLite"},
  {"p": "Roda dentro do processo. É o banco de teste que não deixa rastro:"},
  { code: `adopt Forge

db := Forge.memoria()                 // ou Forge.conectar("dados.db")
Forge.executar(db, "create table t (id integer primary key, n integer)")
Forge.de(db, "t").inserir({"n": 1})
assert Forge.de(db, "t").contar() is 1`, lang: 'df' },
  {"p": "Duas coisas que o Forge liga e o SQLite deixa desligadas por padrão: **chave estrangeira** (senão a restrição existe só no papel) e **WAL** (senão um leitor bloqueia o escritor, e um servidor trava com carga leve)."},
  {"h2": "PostgreSQL"},
  {"p": "Os tipos voltam convertidos: `jsonb` vira vault, array vira cluster, `boolean` vira `yes`/`no`."},
  { code: `// db := Forge.conectar("postgres://usuario:senha@localhost/app")
//
// Forge.executar(db, """
//     create table pessoas (
//         id serial primary key,
//         nome text not null,
//         dados jsonb,
//         tags text[]
//     )
// """)
//
// Forge.executar(db,
//     "insert into pessoas (nome, dados, tags) values (?, ?, ?)",
//     ["Ana", {"cor": "azul"}, ["a", "b"]])
//
// linha := Forge.primeiro(db, "select * from pessoas")
// out linha["dados"]["cor"]        // "azul" — vault de verdade
// out linha["tags"][0]             // "a"    — cluster de verdade`, lang: 'df' },
  {"p": "`RETURNING` funciona e devolve as linhas:"},
  { code: `// nova := Forge.executar(db,
//     "insert into pessoas (nome) values (?) returning id, nome",
//     ["Bia"])
// out nova[0]["id"]`, lang: 'df' },
  {"h2": "MySQL e MariaDB"},
  {"p": "O mesmo driver serve os dois — o MariaDB nasceu de um fork e manteve o protocolo. O que muda é a autenticação padrão."},
  {"callout": {"tipo": "nota", "titulo": "MySQL 8 e o caching_sha2_password", "texto": "Quando o cache do servidor não tem a senha e o canal não é TLS, o MySQL 8 exige que ela viaje cifrada com a chave pública dele. O Forge faz esse handshake — é onde a maioria dos drivers caseiros para."}},
  { code: `// db := Forge.conectar("mysql://root:senha@localhost/app")
// out db.ultimo_id()        // o id gerado pelo último auto_increment`, lang: 'df' },
  {"h2": "Redis"},
  {"p": "Não tem SQL, e fingir que tem seria mentir. O que ele tem é chave-valor, e é isso que a interface expõe:"},
  { code: `// db := Forge.conectar("redis://localhost")
//
// db.comando("SET", "usuario:1", "Ana")
// out db.comando("GET", "usuario:1")
// db.comando("EXPIRE", "usuario:1", 60)
//
// db.comando("RPUSH", "fila", 1, 2, 3)
// out db.comando("LRANGE", "fila", 0, -1)`, lang: 'df' },
  {"p": "**Pipeline** é a otimização mais eficaz com Redis. Cem comandos em cem idas custam cem vezes a latência da rede; numa ida só, custam uma:"},
  { code: `// respostas := db.pipeline([
//     ["SET", "a", "1"],
//     ["SET", "b", "2"],
//     ["MGET", "a", "b"]
// ])
// out respostas[2]        // ["1", "2"]`, lang: 'df' },
  {"h2": "MongoDB"},
  {"p": "Documentos, não tabelas. O `_id` sai como texto e a busca por ele aceita texto — sem essa conversão, procurar por id nunca acharia nada, e não haveria erro, só um resultado vazio:"},
  { code: `// db := Forge.conectar("mongodb://localhost/app")
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
// db.criar_indice("pessoas", "nome", unico := yes)`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "`atualizar` embrulha em `$set`", "texto": "Sem um operador, o Mongo **substitui** o documento inteiro e apaga os campos que não vieram. Quase ninguém quer isso, então o Forge embrulha. Passe `{\"$inc\": {...}}` quando quiser outro operador."}},
  {"h2": "O que é comum a todos"},
  {"table": {"head": ["", "SQLite", "Postgres", "MySQL", "Redis", "Mongo"], "rows": [["`conectar`", "✓", "✓", "✓", "✓", "✓"], ["`ping`, `versao`, `fechar`", "✓", "✓", "✓", "✓", "✓"], ["`consultar` / `executar`", "✓", "✓", "✓", "cru", "documento"], ["construtor de consultas", "✓", "✓", "✓", "—", "—"], ["ORM", "✓", "✓", "✓", "—", "—"], ["transações", "✓", "✓", "✓", "MULTI", "—"], ["`tabelas` / `colunas`", "✓", "✓", "✓", "—", "`colecoes`"]]}},
];

const headings = [{ id: 'sqlite', text: "SQLite", level: 2 as const }, { id: 'postgresql', text: "PostgreSQL", level: 2 as const }, { id: 'mysql-e-mariadb', text: "MySQL e MariaDB", level: 2 as const }, { id: 'redis', text: "Redis", level: 2 as const }, { id: 'mongodb', text: "MongoDB", level: 2 as const }, { id: 'o-que-e-comum-a-todos', text: "O que é comum a todos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Cada motor"}
      description={"O que a interface comum cobre, e o que só existe em cada um."}
      href={"/docs/banco-de-dados/motores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
