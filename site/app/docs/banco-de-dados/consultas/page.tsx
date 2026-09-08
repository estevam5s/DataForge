import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Construtor de consultas",
  description: "SQL montado por chamadas encadeadas — com o dialeto certo e sem injeção.",
};

const blocos: Bloco[] = [
  {"p": "Escrever SQL à mão continua valendo — `Forge.consultar(db, sql, valores)` está aí para isso. O construtor resolve três coisas que o SQL à mão não resolve:"},
  {"list": ["**Dialeto.** `?` no SQLite e MySQL, `$1` no PostgreSQL. A mesma consulta roda nos dois.", "**Condição opcional.** Um filtro que só existe quando o usuário preencheu o campo.", "**Identificador citado.** Uma coluna chamada `order` quebraria a consulta."]},
  {"h2": "O básico"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, """
    create table usuarios (
        id integer primary key autoincrement,
        nome text, cidade text, idade integer, ativo integer
    )
""")
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
assert adultos[0]["nome"] is "Ana"`, lang: 'df' },
  {"h2": "Filtros"},
  {"table": {"head": ["Método", "SQL"], "rows": [["`.onde(\"a\", 1)`", "`a = ?`"], ["`.onde(\"a\", \">=\", 1)`", "`a >= ?`"], ["`.ou_onde(\"a\", 2)`", "`OR a = ?`"], ["`.onde_em(\"a\", [1,2])`", "`a IN (?, ?)`"], ["`.onde_fora(\"a\", [1])`", "`a NOT IN (?)`"], ["`.onde_entre(\"a\", 1, 9)`", "`a BETWEEN ? AND ?`"], ["`.onde_nulo(\"a\")`", "`a IS NULL`"], ["`.onde_contem(\"a\", \"x\")`", "`a LIKE '%x%'`"], ["`.onde_comeca(\"a\", \"x\")`", "`a LIKE 'x%'`"], ["`.onde_cru(sql, valores)`", "o que você escrever, com os valores ainda parametrizados"]]}},
  {"callout": {"tipo": "nota", "titulo": "`onde(\"x\", void)` vira `IS NULL`", "texto": "Em SQL, `x = NULL` nunca é verdadeiro — nem quando x é nulo. O construtor traduz para `IS NULL`, que é o que quem escreveu queria."}},
  {"h2": "Condição opcional"},
  {"p": "`quando` aplica o trecho só se a condição valer. É o que evita o `if` em volta da consulta:"},
  { code: `adopt Forge

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
assert len(procurar(db, "", 100)) is 1`, lang: 'df' },
  {"h2": "Agregados e paginação"},
  { code: `adopt Forge

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
assert pagina["tem_proxima"] is yes`, lang: 'df' },
  {"p": "`paginar` devolve as linhas **e** os números que a interface precisa: total, quantidade de páginas, se há próxima e anterior. A página 1 é a primeira — não a zero."},
  {"h2": "Escritas"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table c (id integer primary key autoincrement, n integer)")

Forge.de(db, "c").inserir({"n": 5})
Forge.de(db, "c").onde("id", 1).atualizar({"n": 10})
Forge.de(db, "c").onde("id", 1).incrementar("n", 3)

assert Forge.de(db, "c").onde("id", 1).primeiro()["n"] is 13`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "UPDATE e DELETE sem WHERE são recusados", "texto": "Um `UPDATE` sem condição mudaria todas as linhas. O construtor recusa e sugere `.onde(...)`. Quando a intenção é essa mesmo, `atualizar_tudo` e `remover_tudo` existem — e o nome deixa claro."}},
  {"p": "`incrementar` faz a soma **no banco**, sem ler antes. Ler-somar-gravar perde atualizações quando duas conexões fazem isso ao mesmo tempo."},
  {"h2": "Ver o SQL"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table u (id integer primary key, idade integer)")

consulta := Forge.de(db, "u").onde("idade", ">=", 18).limite(5)
out consulta.sql()`, lang: 'df' },
  {"p": "Útil para registrar, depurar, ou levar uma consulta complicada para o cliente do banco."},
];

const headings = [{ id: 'o-basico', text: "O básico", level: 2 as const }, { id: 'filtros', text: "Filtros", level: 2 as const }, { id: 'condicao-opcional', text: "Condição opcional", level: 2 as const }, { id: 'agregados-e-paginacao', text: "Agregados e paginação", level: 2 as const }, { id: 'escritas', text: "Escritas", level: 2 as const }, { id: 'ver-o-sql', text: "Ver o SQL", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Construtor de consultas"}
      description={"SQL montado por chamadas encadeadas — com o dialeto certo e sem injeção."}
      href={"/docs/banco-de-dados/consultas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
