// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Transações e pool",
  description: "Tudo ou nada — e por que 'transacao' com bloco é a única forma segura.",
};

const blocos: Bloco[] = [
  {"h2": "Transações"},
  {"p": "Uma transação garante que um conjunto de escritas aconteça inteiro, ou não aconteça:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table contas (id integer primary key, saldo real)")
Forge.de(db, "contas").inserir([{"id": 1, "saldo": 100.0}, {"id": 2, "saldo": 0.0}])

action transferir(db, de, para, valor):
    Forge.de(db, "contas").onde("id", de).incrementar("saldo", 0 - valor)
    Forge.de(db, "contas").onde("id", para).incrementar("saldo", valor)
    yield yes

Forge.transacao(db, lambda c => transferir(c, 1, 2, 30.0))

assert Forge.de(db, "contas").onde("id", 1).primeiro()["saldo"] is 70.0
assert Forge.de(db, "contas").onde("id", 2).primeiro()["saldo"] is 30.0`, lang: 'df' },
  {"p": "Se o corpo falhar, tudo é desfeito:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table t (id integer primary key, n integer)")

action falha(c):
    Forge.de(c, "t").inserir({"n": 1})
    trigger "deu errado no meio"

monitor:
    Forge.transacao(db, falha)
handle e:
    assert e.message is "deu errado no meio"

// a linha inserida antes da falha não ficou
assert Forge.de(db, "t").contar() is 0`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Use a forma com bloco", "texto": "`comecar()` com um `confirmar()` esquecido segura locks até a conexão cair — é o motivo mais comum de um banco travar em produção. `Forge.transacao` confirma no fim e desfaz na falha, sempre."}},
  {"h2": "A forma manual"},
  {"p": "Existe, para quando o fluxo não cabe num bloco:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table t (id integer primary key, n integer)")

db.comecar()
monitor:
    Forge.de(db, "t").inserir({"n": 1})
    db.confirmar()
handle e:
    db.desfazer()

assert Forge.de(db, "t").contar() is 1`, lang: 'df' },
  {"h2": "Pool de conexões"},
  {"p": "Abrir conexão custa: TCP, autenticação, negociação. Numa rota web isso acontece por requisição e passa a dominar o tempo de resposta."},
  { code: `adopt Forge

pool := Forge.pool(":memory:", 5)

with Forge.conexao(pool) as db:
    out Forge.versao(db)

out pool.estado()`, lang: 'df' },
  {"p": "O pool não é só cache — é também **limite**. Sem teto, um pico de tráfego abre mil conexões e o servidor recusa **todas**, inclusive as do que já estava funcionando. Melhor a milésima requisição esperar do que as mil falharem."},
  {"callout": {"tipo": "dica", "titulo": "Sempre com `with`", "texto": "Uma conexão pegada e não devolvida some do pool para sempre. `Forge.conexao(pool)` devolve sozinha, inclusive se o corpo falhar — e desfaz uma transação aberta antes de devolver, para não contaminar quem pegar depois."}},
  {"h2": "Níveis de isolamento"},
  { code: `db.comecar("SERIALIZABLE")`, lang: 'df' },
  {"table": {"head": ["Nível", "Impede", "Custo"], "rows": [["`READ COMMITTED`", "leitura suja", "baixo — o padrão no PostgreSQL"], ["`REPEATABLE READ`", "leitura não repetível", "médio — o padrão no MySQL"], ["`SERIALIZABLE`", "leitura fantasma", "alto — pode abortar por conflito"]]}},
  {"p": "Com `SERIALIZABLE`, prepare-se para `TransactionError` por falha de serialização, e para tentar de novo. É o preço da garantia."},
];

const headings = [{ id: 'transacoes', text: "Transações", level: 2 as const }, { id: 'a-forma-manual', text: "A forma manual", level: 2 as const }, { id: 'pool-de-conexoes', text: "Pool de conexões", level: 2 as const }, { id: 'niveis-de-isolamento', text: "Níveis de isolamento", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Transações e pool"}
      description={"Tudo ou nada — e por que 'transacao' com bloco é a única forma segura."}
      href={"/docs/banco-de-dados/transacoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
