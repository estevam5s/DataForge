// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O banco em contêiner",
  description: "Subir Postgres, MySQL, Redis ou Mongo com Docker e conectar — incluindo a espera que todo compose precisa e ninguém escreve.",
};

const blocos: Bloco[] = [
  {"p": "O caminho normal de desenvolvimento hoje é o banco num contêiner. Esta página cobre as três coisas que quebram nesse caminho — e as três têm resposta na biblioteca."},
  {"callout": {"tipo": "dica", "titulo": "Não há driver a instalar", "texto": "`postgres.py`, `mysql.py`, `redis.py` e `mongo.py` falam o protocolo **por socket**, em Python puro. Não há `psycopg2`, `PyMySQL`, `redis-py` nem `pymongo` aqui — é o que faz `pip install dataforge-lang` bastar numa máquina sem compilador, e o que impede a versão do driver de envelhecer separada da linguagem."}},
  {"h2": "1. Subir o banco"},
  { code: `# O jeito curto, para experimentar:
docker run -d --name loja-db \\
  -e POSTGRES_USER=forge -e POSTGRES_PASSWORD=segredo \\
  -e POSTGRES_DB=loja \\
  -p 5432:5432 postgres:16-alpine`, lang: 'bash' },
  {"p": "E o `docker-compose.yml` sai da **mesma URL** que a aplicação usa. Escrever os dois à mão é como eles divergem: o compose sobe `POSTGRES_DB=loja` e a aplicação procura `loja_dev`, e o erro só aparece na primeira consulta."},
  { code: `adopt Arcane.Forge as Forge
adopt Arcane.Serialization as S

steady URL := "postgres://forge:segredo@localhost:5432/loja"

c := Forge.compose(URL, servico := "banco")

out $"servico:     {c['servico']}"
out $"url interna: {c['url_interna']}"
out ""
out S.to_json(c["definicao"], yes)`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A URL de dentro não é a de fora", "texto": "Por dentro da rede do compose o host é o **nome do serviço** e a porta é a **interna do motor** — `postgres://…@banco:5432/loja`. Trocar só o host é o erro clássico de quem publica numa porta diferente: `localhost:55432` vira `banco:55432`, e nada escuta ali dentro. `url_interna` devolve as duas trocas."}},
  {"h2": "2. Esperar — “Up” não quer dizer “pronto”"},
  {"p": "O `docker compose up` volta, o contêiner aparece como *Up*, e a aplicação morre no primeiro `conectar` com **connection refused**. O contêiner do Postgres sobe, cria o cluster, **reinicia o servidor uma vez** durante a inicialização, e só então passa a escutar — são segundos. O do MySQL demora mais."},
  {"table": {"head": ["A saída comum", "Por que falha"], "rows": [["`sleep 5` no script de partida", "falha na máquina lenta, e desperdiça quatro segundos na rápida"], ["laço de retentativa escrito à mão", "quase sempre insiste também em credencial errada, e esconde a causa atrás do prazo"], ["`depends_on` sem `condition`", "espera o contêiner **começar**, não ficar pronto"]]}},
  { code: `adopt Arcane.Forge as Forge

// A espera e por RESPOSTA, e nao por relogio.
db := Forge.esperar("postgres://forge:segredo@localhost:5432/loja",
    prazo := 30.0)

out Forge.versao(db)
Forge.fechar(db)`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Senha errada não melhora com o tempo", "texto": "`esperar` insiste só no que é **transitório** — conexão recusada, conexão redefinida, servidor iniciando. Uma credencial inválida ou um banco que não existe sobem **na hora**: insistir trinta segundos nisso é esconder a causa atrás de um prazo, e quem lê o log vê um “tempo esgotado” e vai procurar no lugar errado. Medido: 4 ms contra os 30 s do prazo."}},
  {"h2": "3. A URL vem do ambiente"},
  {"p": "Uma URL de banco no código é um segredo no repositório: ela carrega usuário e senha. Num contêiner ela nunca está no código — está no ambiente, e é isso que permite a **mesma imagem** rodar em desenvolvimento, em teste e em produção."},
  { code: `adopt Arcane.Forge as Forge

// Procura DATABASE_URL, DB_URL e FORGE_DATABASE_URL, nesta ordem.
// Sem nenhuma delas e SEM padrao, isto e ERRO — e nao um SQLite
// calado, que e o defeito que faz alguem rodar uma semana contra o
// banco errado.
db := Forge.de_ambiente(padrao := ":memory:")

Forge.executar(db, "create table t (id integer primary key, v text)")
Forge.executar(db, "insert into t (v) values (?)", ["ok"])
assert Forge.consultar(db, "select v from t")[0]["v"] is "ok"

out "conectado pelo ambiente"
Forge.fechar(db)`, lang: 'df' },
  {"h2": "O compose completo"},
  { code: `services:
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
  banco-dados:`, lang: 'yaml' },
  {"table": {"head": ["No arquivo", "Sem ele"], "rows": [["`healthcheck` com `start_period`", "as falhas normais da inicialização contam como *não saudável* e derrubam o serviço"], ["`depends_on: service_healthy`", "a app sobe antes do banco e falha na primeira consulta, de forma intermitente"], ["`volumes`", "o banco começa vazio a cada `down`"], ["`DATABASE_URL` no ambiente", "a senha vai para a imagem, e `docker history` a mostra"]]}},
  {"callout": {"tipo": "dica", "titulo": "A sonda e o `esperar` atacam o mesmo problema de lados diferentes", "texto": "A sonda é o **plano**: com ela, o compose só inicia a aplicação quando o banco responde. O `esperar` é a **rede de segurança**: ele cobre o `docker run` solto, o banco que reinicia em produção, e o caso em que alguém subiu os dois à mão. Ter os dois não é redundância — é que um deles não está presente em metade das situações reais."}},
  {"h2": "Os quatro motores em contêiner"},
  {"table": {"head": ["Motor", "Imagem", "URL"], "rows": [["PostgreSQL", "`postgres:16-alpine`", "`postgres://forge:segredo@localhost:5432/loja`"], ["MySQL", "`mysql:8`", "`mysql://forge:segredo@localhost:3306/loja`"], ["MariaDB", "`mariadb:11`", "`mariadb://forge:segredo@localhost:3306/loja`"], ["Redis", "`redis:7-alpine`", "`redis://localhost:6379`"], ["MongoDB", "`mongo:7`", "`mongo://forge:segredo@localhost:27017/loja`"]]}},
  {"p": "Continue em [Cada motor](/docs/banco-de-dados/motores) e [Produção](/docs/banco-de-dados/producao)."},
];

const headings = [{ id: '1-subir-o-banco', text: "1. Subir o banco", level: 2 as const }, { id: '2-esperar-up-nao-quer-dizer-pronto', text: "2. Esperar — “Up” não quer dizer “pronto”", level: 2 as const }, { id: '3-a-url-vem-do-ambiente', text: "3. A URL vem do ambiente", level: 2 as const }, { id: 'o-compose-completo', text: "O compose completo", level: 2 as const }, { id: 'os-quatro-motores-em-conteiner', text: "Os quatro motores em contêiner", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O banco em contêiner"}
      description={"Subir Postgres, MySQL, Redis ou Mongo com Docker e conectar — incluindo a espera que todo compose precisa e ninguém escreve."}
      href={"/docs/banco-de-dados/docker"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
