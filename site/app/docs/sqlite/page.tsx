// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_etl.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "SQLite",
  description: "O banco que vem junto: tabelas, transações, índices, busca textual e migrações — sem instalar nada.",
};

const blocos: Bloco[] = [
  {"p": "SQLite é um banco **dentro do processo**: um arquivo, sem servidor, sem porta, sem senha. Ele vem com o Python e portanto com a DataForge — `adopt Arcane.Database` e já existe banco."},
  {"p": "É a escolha certa para muito mais coisa do que costuma parecer: ferramenta de linha de comando, aplicação de uma máquina, cache local, teste automatizado, e sites de leitura pesada com escrita moderada."},
  {"h2": "Abrir, criar, inserir, consultar"},
  { code: `adopt Arcane.Database as DB

db := DB.memory()                   // some ao fim do programa
// db := DB.connect("dados.db")     // um arquivo

DB.create_table(db, "pedidos", {
    "id": "INTEGER PRIMARY KEY",
    "cliente": "TEXT",
    "total": "REAL"
})

DB.insert(db, "pedidos", {"cliente": "Ana", "total": 99.9})
DB.insert_many(db, "pedidos", [
    {"cliente": "Bruno", "total": 45.0},
    {"cliente": "Carla", "total": 12.5}
])

out DB.count(db, "pedidos")
out DB.query(db, "SELECT cliente, total FROM pedidos ORDER BY total DESC", [])
DB.close(db)
`, lang: 'df' },
  {"p": "A consulta devolve um **cluster de vaults** — a mesma forma que o resto da linguagem usa, e a mesma que a [análise de dados](/docs/dados) espera."},
  {"h2": "Parâmetro, sempre"},
  { code: `// NÃO: um nome com aspas quebra a consulta, e um nome malicioso a reescreve
DB.query(db, $"SELECT * FROM pedidos WHERE cliente = '{nome}'", [])

// SIM: o valor vai por fora do SQL
DB.query(db, "SELECT * FROM pedidos WHERE cliente = ?", [nome])
`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "O nome da coluna é a exceção", "texto": "O SQLite não aceita **nome de coluna** por parâmetro, então ele vai cru para o SQL. É por isso que `order_by` e amigos passam por uma validação que recusa o que não parece um identificador — e isso importa porque um `?ordenar=` de uma listagem chega de fora."}},
  {"h2": "Transação: tudo ou nada"},
  { code: `DB.transacao(db, lambda:
    [DB.insert(db, "itens", i) cycle i in itens])
`, lang: 'df' },
  {"p": "Sem transação, cada escrita confirma sozinha — e uma falha no meio deixa metade dentro. Com ela, as duas únicas saídas são \"tudo\" e \"nada\"."},
  {"p": "**E a transação também é desempenho.** Mil `insert` soltos são mil confirmações em disco; dentro de uma transação, é uma — a diferença costuma ser de duas ordens de grandeza."},
  {"h2": "Índice: de varrer para buscar"},
  { code: `DB.create_index(db, "pedidos", ["cliente"])
out DB.explain(db, "SELECT * FROM pedidos WHERE cliente = ?", ["Ana"])
`, lang: 'df' },
  { code: `{passos: [SEARCH pedidos USING INDEX idx_pedidos_cliente (cliente=?)],
 varre_tabela: no, aviso: }
`, lang: 'text' },
  {"p": "Antes do índice, o mesmo `explain` responde `varre_tabela: yes`. Medido com 20 mil linhas e 200 consultas: **73,6 ms → 4,4 ms**, 16,6×. Ver [complexidade em dados](/docs/big-o/dados)."},
  {"h2": "Busca textual"},
  { code: `DB.create_search(db, "pedidos", ["cliente"])
out DB.search(db, "pedidos", "ana")
`, lang: 'df' },
  {"p": "Duas armadilhas que a implementação já pagou, as duas silenciosas: o `*` de prefixo vai **fora** das aspas (`\"livr\"*`, e não `\"livr*\"`), e o nome da tabela junto de um apelido devolvia vazio — as duas devolviam lista vazia sem erro."},
  {"h2": "Migrações"},
  { code: `DB.migrate(db, [
    {"nome": "001_pedidos",
     "up": "CREATE TABLE pedidos (id INTEGER PRIMARY KEY, cliente TEXT)",
     "down": "DROP TABLE pedidos"},
    {"nome": "002_total",
     "up": "ALTER TABLE pedidos ADD COLUMN total REAL DEFAULT 0",
     "down": "ALTER TABLE pedidos DROP COLUMN total"}
])

out DB.migrations_applied(db)
`, lang: 'df' },
  {"p": "O `down` não é opcional por preguiça: sem ele, desfazer exige editar o banco à mão — e a hora de precisar disso é sempre a pior possível."},
  {"h2": "Concorrência: o que o SQLite faz e o que não faz"},
  {"table": {"head": ["", "SQLite"], "rows": [["muitos leitores ao mesmo tempo", "sim"], ["um escritor por vez", "sim — o banco inteiro trava na escrita"], ["muitos escritores ao mesmo tempo", "**não**"], ["acesso pela rede", "**não** — é um arquivo local"]]}},
  {"p": "O `Arcane.Database` serializa o acesso à conexão: sem isso, a primeira consulta de qualquer servidor estoura, porque a conexão do SQLite não atravessa thread. Num Kiln com carga de escrita alta, essa serialização vira o gargalo — e é o momento de trocar por um banco cliente-servidor."},
  {"h2": "Quando trocar de banco"},
  {"list": ["**Vários processos escrevendo** — não é o caso de uso do SQLite.", "**Acesso pela rede** — ele não tem; um arquivo em disco compartilhado corrompe.", "**Escrita concorrente alta** — o travamento no nível do banco passa a doer.", "**Dados maiores que o disco de uma máquina** — a resposta aí não é banco, é [lago](/docs/tecnicas/lago)."]},
  {"p": "Fora esses quatro casos, trocar SQLite por um servidor costuma acrescentar operação sem acrescentar capacidade."},
  {"h2": "Testar com banco"},
  { code: `adopt Arcane.Crucible as C
adopt Arcane.Database as DB

crucible "pedidos":
    trial "insere e conta":
        db := DB.memory()
        DB.create_table(db, "p", {"id": "INTEGER PRIMARY KEY", "v": "REAL"})
        DB.insert(db, "p", {"v": 1.0})
        expect DB.count(db, "p") is 1
        DB.close(db)

C.run()
`, lang: 'df' },
  {"p": "`DB.memory()` é o que torna teste com banco barato: nada em disco, nada para limpar, e cada `trial` começa do zero. Para testar sobre um banco **real** sem sujá-lo, `Crucible.banco(db)` abre transação e a desfaz no fim."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/biblioteca/database", "title": "Arcane.Database", "desc": "os 64 símbolos, um por um"}, {"href": "/docs/tecnicas/banco-de-dados/crud", "title": "CRUD completo", "desc": "um exemplo ponta a ponta"}, {"href": "/docs/orm", "title": "ORM", "desc": "quando o SQL à mão deixa de compensar"}, {"href": "/docs/big-o/dados", "title": "Custo em dados", "desc": "N+1, índice e paginação por cursor"}]},
];

const headings = [{ id: 'abrir-criar-inserir-consultar', text: "Abrir, criar, inserir, consultar", level: 2 as const }, { id: 'parametro-sempre', text: "Parâmetro, sempre", level: 2 as const }, { id: 'transacao-tudo-ou-nada', text: "Transação: tudo ou nada", level: 2 as const }, { id: 'indice-de-varrer-para-buscar', text: "Índice: de varrer para buscar", level: 2 as const }, { id: 'busca-textual', text: "Busca textual", level: 2 as const }, { id: 'migracoes', text: "Migrações", level: 2 as const }, { id: 'concorrencia-o-que-o-sqlite-faz-e-o-que-nao-faz', text: "Concorrência: o que o SQLite faz e o que não faz", level: 2 as const }, { id: 'quando-trocar-de-banco', text: "Quando trocar de banco", level: 2 as const }, { id: 'testar-com-banco', text: "Testar com banco", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"SQLite"}
      description={"O banco que vem junto: tabelas, transações, índices, busca textual e migrações — sem instalar nada."}
      href={"/docs/sqlite"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
