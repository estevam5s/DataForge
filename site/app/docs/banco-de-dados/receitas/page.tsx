// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Receitas",
  description: "Os seis problemas que todo sistema com banco resolve — com o código que funciona e o que dá errado na versão ingênua.",
};

const blocos: Bloco[] = [
  {"p": "Cada uma destas tem uma versão ingênua que funciona no teste e falha com concorrência, com volume, ou com um link antigo."},
  {"h2": "1. Inserir sem duplicar"},
  { code: `adopt Arcane.Database as Db

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

Db.close(db)`, lang: 'df' },
  {"h2": "2. Contador que não perde"},
  { code: `adopt Arcane.Database as Db

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

Db.close(db)`, lang: 'df' },
  {"h2": "3. Listagem paginada"},
  { code: `adopt Arcane.Database as Db

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

Db.close(db)`, lang: 'df' },
  {"h2": "4. Busca textual"},
  { code: `adopt Arcane.Database as Db

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

Db.close(db)`, lang: 'df' },
  {"h2": "5. Exportar sem carregar tudo"},
  { code: `adopt Arcane.Forge as Forge
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
Forge.fechar(db)`, lang: 'df' },
  {"h2": "6. Migração que desfaz"},
  { code: `adopt Arcane.Forge as Forge

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

Forge.fechar(db)`, lang: 'df' },
  {"p": "Continue em [Em produção](/docs/banco-de-dados/producao) e [O banco em contêiner](/docs/banco-de-dados/docker)."},
];

const headings = [{ id: '1-inserir-sem-duplicar', text: "1. Inserir sem duplicar", level: 2 as const }, { id: '2-contador-que-nao-perde', text: "2. Contador que não perde", level: 2 as const }, { id: '3-listagem-paginada', text: "3. Listagem paginada", level: 2 as const }, { id: '4-busca-textual', text: "4. Busca textual", level: 2 as const }, { id: '5-exportar-sem-carregar-tudo', text: "5. Exportar sem carregar tudo", level: 2 as const }, { id: '6-migracao-que-desfaz', text: "6. Migração que desfaz", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Receitas"}
      description={"Os seis problemas que todo sistema com banco resolve — com o código que funciona e o que dá errado na versão ingênua."}
      href={"/docs/banco-de-dados/receitas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
