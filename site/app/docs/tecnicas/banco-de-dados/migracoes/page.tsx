// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_sqlite.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Migrações",
  description: "Mudar o schema de um banco que tem dado dentro — com ida, volta e histórico.",
};

const blocos: Bloco[] = [
  {"p": "Num sistema em produção o banco tem dado dentro. Trocar o `create_table` no código não muda a tabela que já existe, e apagar e recriar perde tudo."},
  {"h2": "A lista, com ida e volta"},
  { code: `steady MIGRACOES := [
    {
        "version": 1,
        "description": "clientes",
        "up": """
            CREATE TABLE clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL
            );
        """,
        "down": "DROP TABLE clientes;"
    },
    {
        "version": 2,
        "description": "e-mail do cliente",
        "up":   "ALTER TABLE clientes ADD COLUMN email TEXT;",
        "down": "ALTER TABLE clientes DROP COLUMN email;"
    }
]

Banco.migrate(db, MIGRACOES)      // aplica o que falta; devolve quantas`, lang: 'df' },
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`Banco.migrate(db, lista)`", "aplica as que faltam, em ordem de versão"], ["`Banco.migrations_applied(db)`", "versão, descrição e quando"], ["`Banco.rollback_migration(db, lista)`", "desfaz **uma**"], ["`Banco.rollback_migration(db, lista, ate := 3)`", "desfaz até a 3, que **fica**"], ["`Banco.schema_sql(db)`", "o schema como o SQLite o guarda"]]}},
  {"h2": "É idempotente, e isso é o ponto"},
  {"p": "`migrate` grava numa tabela `_migrations` o que já aplicou, e pula essas. Rodar de novo devolve `0`. É o que permite chamá-lo no começo de **todo** processo:"},
  { code: `db := Banco.connect("dados.db")
Banco.migrate(db, MIGRACOES)
V.subir(porta := 8501)`, lang: 'df' },
  {"p": "Sem isso, subir o servidor duas vezes quebraria na segunda — e alguém acabaria escrevendo um script de migração que se roda à mão, que é o mesmo problema com mais passos."},
  {"h2": "Toda migração deveria ter `down`"},
  {"p": "Desfazer acontece no meio de um incidente — que é quando ninguém tem paciência para editar o banco à mão. Duas escolhas deliberadas:"},
  {"callout": {"tipo": "atencao", "titulo": "Por padrão desfaz uma", "texto": "Desfazer em cascata por acidente é perda de dado, e é a diferença entre \"corrigi a última\" e \"apaguei o banco\". Para ir mais fundo, diga explicitamente até onde: `ate := 3`."}},
  {"callout": {"tipo": "atencao", "titulo": "Sem `down`, o rollback para com erro", "texto": "Pular em silêncio deixaria o banco num estado que **nenhuma versão descreve** — nem a anterior, nem a nova. Descobrir isso depois é pior que o erro agora."}},
  {"h2": "O dado sobrevive"},
  { code: `Banco.insert(db, "clientes", {"nome": "Ana", "email": "ana@exemplo.br"})

steady MAIS := [...MIGRACOES, {
    "version": 3, "description": "telefone",
    "up":   "ALTER TABLE clientes ADD COLUMN telefone TEXT DEFAULT '';",
    "down": "ALTER TABLE clientes DROP COLUMN telefone;"
}]

Banco.migrate(db, MAIS)                  // uma aplicada
Banco.count(db, "clientes")              // o dado continua lá`, lang: 'df' },
  {"h2": "As migrações que exigem cuidado"},
  {"table": {"head": ["Mudança", "Como fazer"], "rows": [["acrescentar coluna", "`ALTER TABLE … ADD COLUMN` — barato, e com `DEFAULT` não trava"], ["renomear coluna", "`ALTER TABLE … RENAME COLUMN` (SQLite 3.25+)"], ["mudar tipo de coluna", "tabela nova, `INSERT … SELECT`, `DROP`, `RENAME` — o SQLite não altera tipo"], ["acrescentar `NOT NULL` sem `DEFAULT`", "impossível com dado existente: preencha antes, em duas migrações"], ["acrescentar índice numa tabela grande", "trava a escrita enquanto constrói; faça na janela de manutenção"], ["apagar coluna", "`DROP COLUMN` (3.35+), e é **irreversível** — o `down` não recupera o dado"]]}},
  {"callout": {"tipo": "dica", "titulo": "Duas migrações, não uma", "texto": "Para tornar uma coluna obrigatória: primeiro acrescente nula e preencha o que falta; depois, numa segunda migração, imponha o `NOT NULL`. Uma migração que precisa que o dado já esteja certo falha na primeira máquina onde ele não está."}},
  {"h2": "Antes de migrar em produção"},
  { code: `Banco.backup(db, $"antes-da-v{proxima}.db")
Banco.migrate(db, MIGRACOES)
Banco.integrity(db)`, lang: 'df' },
  {"p": "`backup` faz uma cópia consistente **com o banco em uso** — é a API de backup do SQLite, não um `cp`. Um `cp` de um banco sendo escrito copia um arquivo pela metade."},
  {"p": "E o SQLite não desfaz DDL dentro de transação de forma confiável em todas as versões: o backup é a rede de segurança real, não o `rollback`."},
  {"h2": "Comparar dois ambientes"},
  { code: `// em produção
IO.write("schema-prod.sql", Banco.schema_sql(prod))
// no seu
IO.write("schema-dev.sql", Banco.schema_sql(dev))`, lang: 'df' },
  {"p": "Um `diff` entre os dois mostra o que falta migrar. É o jeito mais direto de descobrir que alguém alterou o banco à mão."},
];

const headings = [{ id: 'a-lista-com-ida-e-volta', text: "A lista, com ida e volta", level: 2 as const }, { id: 'e-idempotente-e-isso-e-o-ponto', text: "É idempotente, e isso é o ponto", level: 2 as const }, { id: 'toda-migracao-deveria-ter-down', text: "Toda migração deveria ter `down`", level: 2 as const }, { id: 'o-dado-sobrevive', text: "O dado sobrevive", level: 2 as const }, { id: 'as-migracoes-que-exigem-cuidado', text: "As migrações que exigem cuidado", level: 2 as const }, { id: 'antes-de-migrar-em-producao', text: "Antes de migrar em produção", level: 2 as const }, { id: 'comparar-dois-ambientes', text: "Comparar dois ambientes", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Migrações"}
      description={"Mudar o schema de um banco que tem dado dentro — com ida, volta e histórico."}
      href={"/docs/tecnicas/banco-de-dados/migracoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
