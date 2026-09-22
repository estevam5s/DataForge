// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/api_rest_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Autenticação numa API",
  description: "Bearer token, 401 contra 403, o middleware que falha fechado, e o token assinado do próprio Kiln.",
};

const blocos: Bloco[] = [
  {"p": "Autenticar é saber **quem** pede; autorizar é saber se ele **pode**. São dois códigos diferentes, e confundi-los esconde um incidente:"},
  {"table": {"head": ["Status", "Quer dizer", "O cliente deve"], "rows": [["401", "não sei quem você é (sem credencial, ou inválida)", "autenticar de novo"], ["403", "sei quem você é, e você não pode", "não tentar de novo — pedir permissão"]]}},
  { code: `adopt Arcane.Kiln as Kiln

steady SEGREDO := "troque-isto"
app := Kiln.app()

action quem_e(token):
    dados := Kiln.unsign(token, SEGREDO)
    yield void given dados is void otherwise dados["usuario"]

Kiln.use(app, Kiln.auth(quem_e))
Kiln.get(app, "/eu", lambda req: Kiln.json({"usuario": req["state"]["user"]}))
action apagar(req):
    given req["state"]["user"] is not "admin":
        yield Kiln.problema(403, "Sem permissão", "só o administrador apaga pedidos")
    yield Kiln.status(204)

Kiln.delete(app, "/pedidos/:id", apagar)

token := Kiln.sign({"usuario": "ana"}, SEGREDO)
cab := {"Authorization": $"Bearer {token}"}

assert Kiln.test(app, "GET", "/eu")["status"] is 401
assert Kiln.test(app, "GET", "/eu", void, {"Authorization": "Bearer forjado"})["status"] is 401
assert Kiln.test(app, "GET", "/eu", void, cab)["body"]["usuario"] is "ana"
assert Kiln.test(app, "DELETE", "/pedidos/1", void, cab)["status"] is 403`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O middleware falha fechado", "texto": "Se o verificador levanta ou devolve `void`, a rota **não roda**. Um middleware de autenticação que, ao falhar, deixa passar é pior que nenhum: ele dá a sensação de proteção."}},
  {"callout": {"tipo": "atencao", "titulo": "`x ?? void is void` não compara nada", "texto": "O `??` tem a precedência mais baixa da linguagem: `saldos[quem] ?? void is void` é lido como `saldos[quem] ?? (void is void)`, e o `given` nunca vê o `void`. Escreva `(saldos[quem] ?? void) is void` — o `dataforge check` avisa (`coalescencia-engole-comparacao`)."}},
  {"p": "Para autorização além de um `given` na rota — papéis, dono do recurso, negação explícita —, use [`Arcane.Politica`](/docs/seguranca/autorizacao). Para JWT de outro emissor, `Crypto.jwt_verificar`."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Autenticação numa API"}
      description={"Bearer token, 401 contra 403, o middleware que falha fechado, e o token assinado do próprio Kiln."}
      href={"/docs/api/autenticacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
