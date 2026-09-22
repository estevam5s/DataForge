// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "PostgreSQL",
  description: "O driver, os tipos, os parâmetros posicionais e o que o Postgres não perdoa — com o contêiner pronto.",
};

const blocos: Bloco[] = [
  {"p": "O driver fala o **protocolo v3** por socket: aperto de mão, autenticação (`md5` e `scram-sha-256`), consulta simples e consulta estendida com parâmetros. Não há `psycopg` no caminho."},
  {"h2": "Conectar"},
  { code: `adopt Arcane.Forge as Forge

// O motor sai da URL; a porta padrao e 5432.
db := Forge.esperar("postgres://forge:segredo@localhost:5432/loja",
    prazo := 30.0)

out Forge.versao(db)
out $"tabelas: {len(Forge.tabelas(db))}"
Forge.fechar(db)`, lang: 'df' },
  {"h2": "Os parâmetros são `$1`, e não `?`"},
  {"p": "Cada banco tem a sua marca de parâmetro, e trocá-la é o primeiro erro de quem vem do SQLite. O construtor de consultas cuida disso sozinho — o cuidado é para o SQL escrito à mão."},
  {"table": {"head": ["Motor", "Marca", "Exemplo"], "rows": [["SQLite", "`?`", "`where id = ?`"], ["PostgreSQL", "`$1`, `$2`", "`where id = $1`"], ["MySQL / MariaDB", "`?`", "`where id = ?`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Parâmetro, sempre — e não por estilo", "texto": "`$\"select * from u where id = {id}\"` é injeção de SQL, e o `dataforge seguranca` acusa (`sql-concatenado`). O valor vai por parâmetro **inclusive** quando ele “é só um número”: o dia em que ele deixa de ser um número é o dia do incidente."}},
  {"h2": "Os tipos que só o Postgres tem"},
  {"table": {"head": ["Tipo", "Chega como", "Observação"], "rows": [["`serial` / `bigserial`", "Integer", "a sequência é do servidor; o `id` volta no `criar`"], ["`numeric` / `decimal`", "texto exato, convertido", "**não** vira Float: o arredondamento binário é o que `Arcane.Decimal` existe para evitar"], ["`timestamp` / `timestamptz`", "DataHora", "guarde em UTC; o fuso é de quem apresenta"], ["`jsonb`", "texto", "use `Arcane.Serialization` para ler"], ["`text[]`", "texto", "arrays não têm tipo próprio na linguagem"], ["`uuid`", "texto", "`Crypto.uuid4()` gera"]]}},
  {"h2": "O que o Postgres não perdoa e o SQLite perdoa"},
  {"table": {"head": ["No SQLite passa", "No Postgres", "Porque"], "rows": [["`\"texto\"` como literal", "erro", "aspas duplas são **identificador**; literal é aspas simples"], ["inserir texto numa coluna `integer`", "erro", "o SQLite tem afinidade de tipo, e não tipo"], ["`select a, b … group by a`", "erro", "toda coluna do `select` tem de estar no `group by` ou numa agregação"], ["comparar `integer` com `text`", "erro", "não há conversão implícita"], ["tabela sem chave primária", "passa, e dói depois", "replicação e `ON CONFLICT` precisam dela"]]}},
  {"callout": {"tipo": "dica", "titulo": "Teste contra o banco de verdade", "texto": "O SQLite é ótimo para o teste rápido e **mente sobre tipos**. A suíte deste repositório roda o ORM contra um Postgres em contêiner justamente por isso: o que quebra em produção é o que o SQLite deixou passar. Veja `tests/test_forge_docker.py`."}},
  {"p": "Continue em [O banco em contêiner](/docs/banco-de-dados/docker)."},
];

const headings = [{ id: 'conectar', text: "Conectar", level: 2 as const }, { id: 'os-parametros-sao-1-e-nao', text: "Os parâmetros são `$1`, e não `?`", level: 2 as const }, { id: 'os-tipos-que-so-o-postgres-tem', text: "Os tipos que só o Postgres tem", level: 2 as const }, { id: 'o-que-o-postgres-nao-perdoa-e-o-sqlite-perdoa', text: "O que o Postgres não perdoa e o SQLite perdoa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"PostgreSQL"}
      description={"O driver, os tipos, os parâmetros posicionais e o que o Postgres não perdoa — com o contêiner pronto."}
      href={"/docs/banco-de-dados/postgres"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
