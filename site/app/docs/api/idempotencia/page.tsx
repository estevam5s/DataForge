// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/api_rest_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Idempotência",
  description: "A resposta se perde na rede e o cliente reenvia. Sem chave de idempotência, a cobrança acontece duas vezes.",
};

const blocos: Bloco[] = [
  {"p": "`GET`, `PUT` e `DELETE` são idempotentes por definição: repetir dá o mesmo estado final. `POST` não é — cada um cria algo. E o problema real é de rede: o servidor cobrou, a resposta se perdeu, o cliente **não sabe** se deu certo, e reenvia."},
  {"p": "O cliente sozinho não resolve: ele não tem como saber. Quem resolve é o servidor, reconhecendo o reenvio por uma chave que o cliente gera **uma vez por intenção** e manda em `Idempotency-Key`:"},
  { code: `adopt Arcane.Kiln as Kiln

cobrancas := []
app := Kiln.app()
Kiln.use(app, Kiln.idempotente())

action cobrar(req):
    cobrancas.append(req["body"]["valor"])
    yield Kiln.json({"cobranca": len(cobrancas)}, 201)

Kiln.post(app, "/cobrancas", cobrar)

chave := {"Idempotency-Key": "pedido-77-tentativa"}
primeira := Kiln.test(app, "POST", "/cobrancas", {"valor": 50}, chave)
reenvio := Kiln.test(app, "POST", "/cobrancas", {"valor": 50}, chave)

assert len(cobrancas) is 1                        // cobrou uma vez só
assert reenvio["body"] is primeira["body"]
assert reenvio["headers"]["Idempotent-Replay"] is "true"`, lang: 'df' },
  {"list": ["**A chave é por intenção, não por tentativa.** Gerar uma nova a cada reenvio desliga a proteção.", "**Só resposta de sucesso fica guardada.** Um 500 guardado faria o reenvio devolver o erro para sempre, quando o reenvio existe justamente para tentar de novo.", "**Fica em memória.** Um processo reiniciado esquece as chaves, e várias réplicas não se enxergam. Para valer em produção, a chave vai para o banco — com restrição de unicidade."]},
  {"p": "Do lado de quem chama, `Arcane.Malha` já não repete `POST` sem chave: ver [Chamadas entre serviços](/docs/tecnicas/microservicos)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Idempotência"}
      description={"A resposta se perde na rede e o cliente reenvia. Sem chave de idempotência, a cobrança acontece duas vezes."}
      href={"/docs/api/idempotencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
