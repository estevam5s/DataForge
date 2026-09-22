// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Em produção",
  description: "Pool, índices, o que medir, o que nunca fazer — e as decisões que só aparecem quando há carga.",
};

const blocos: Bloco[] = [
  {"p": "O que funciona numa máquina com um usuário falha com cinquenta. Esta página é a lista do que muda."},
  {"h2": "Uma conexão por pedido não escala"},
  {"p": "Abrir conexão com Postgres custa um aperto de mão TCP, autenticação e alocação de um processo do lado do servidor — dezenas de milissegundos. Por pedido, isso domina o tempo de resposta; e o servidor tem um teto de conexões que se atinge antes do teto de CPU."},
  { code: `adopt Arcane.Forge as Forge

// O pool abre N conexoes e as empresta. 'conexao' devolve ao fim.
pool := Forge.pool(":memory:", 4)

// Sempre com 'with': uma conexao pegada e nao devolvida some do
// pool para sempre, e o 'with' devolve inclusive se o corpo falhar.
cycle i from 1 to 8:
    with Forge.conexao(pool) as db:
        Forge.consultar(db, "select 1 as um")

out $"oito pedidos, {pool.estado()['tamanho']} conexoes"
`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O tamanho do pool não é “quanto maior melhor”", "texto": "Cada conexão do Postgres é um **processo** do lado do servidor, com memória própria. Um pool de 100 por instância, com quatro instâncias, são 400 processos — e o servidor passa mais tempo trocando de contexto que respondendo. A conta que funciona na prática é próxima de `núcleos × 2 + fusos de disco`, por **todo o conjunto**, e não por instância. Quando o número precisa ser maior, o que falta é um *pooler* (PgBouncer), e não um pool maior."}},
  {"h2": "O índice que falta"},
  {"p": "A consulta que responde em 3 ms com mil linhas responde em 3 s com um milhão — e nada no código mudou. `explain` mostra o plano, e é ele que diz se o banco está varrendo a tabela."},
  { code: `adopt Arcane.Database as Db

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

Db.close(db)`, lang: 'df' },
  {"table": {"head": ["Indexe", "Porque"], "rows": [["toda chave estrangeira", "é por onde as relações do ORM buscam — e sem índice cada `com()` vira varredura"], ["a coluna de todo `onde` frequente", "é o caso óbvio, e o mais esquecido"], ["a coluna de `ordenar` quando há `limite`", "sem ele o banco ordena a tabela inteira para devolver dez linhas"], ["**não** indexe tudo", "todo índice é escrito em cada `insert`; uma tabela com oito índices escreve nove vezes"]]}},
  {"h2": "O que nunca fazer"},
  {"table": {"head": ["Nunca", "O que acontece"], "rows": [["`select *` numa listagem", "traz colunas grandes que a tela não usa, e o custo é de rede"], ["listagem sem `limite`", "a forma mais comum de derrubar uma aplicação — e a `paginar` do ORM já vem com teto"], ["consulta dentro de laço", "o N+1: use [`com()`](/docs/orm/atraves)"], ["`order by` por coluna vinda da URL, sem lista", "injeção por identificador; o `order_by` do `Arcane.Database` recusa o que não parece nome"], ["migração sem `down`", "desfazer exige editar o banco à mão"], ["transação aberta esperando rede", "ela segura locks enquanto o HTTP de terceiro demora"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A rota do Kiln é concorrente, e é invisível", "texto": "O Kiln usa `ThreadingHTTPServer`: cada pedido roda numa thread. O `Arcane.Database` serializa o acesso à conexão — sem isso, a primeira consulta de qualquer servidor estoura —, mas **estado em memória compartilhado entre rotas não é protegido**. Medido: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**. O `check` avisa (`escrita-concorrente`)."}},
  {"h2": "O que medir"},
  {"table": {"head": ["Medida", "Como", "O que ela denuncia"], "rows": [["consultas por pedido", "contar no log", "N+1 — o número cresce com o tamanho da página"], ["p95 da consulta", "`Arcane.Perfil`", "a média esconde a cauda, e é a cauda que o usuário sente"], ["conexões em uso", "`pool.estado()`", "pool no teto = pedidos esperando"], ["plano da consulta lenta", "`Db.explain`", "índice faltando"], ["tamanho das tabelas", "`Db.stats`", "a tabela que cresce sem retenção"]]}},
  {"p": "Continue em [Transações e pool](/docs/banco-de-dados/transacoes) e [O banco em contêiner](/docs/banco-de-dados/docker)."},
];

const headings = [{ id: 'uma-conexao-por-pedido-nao-escala', text: "Uma conexão por pedido não escala", level: 2 as const }, { id: 'o-indice-que-falta', text: "O índice que falta", level: 2 as const }, { id: 'o-que-nunca-fazer', text: "O que nunca fazer", level: 2 as const }, { id: 'o-que-medir', text: "O que medir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Em produção"}
      description={"Pool, índices, o que medir, o que nunca fazer — e as decisões que só aparecem quando há carga."}
      href={"/docs/banco-de-dados/producao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
