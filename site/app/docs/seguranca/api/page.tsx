// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Segurança de API",
  description: "O OWASP API Top 10, e o BOLA — a falha mais comum de uma API — escrita e corrigida.",
};

const blocos: Bloco[] = [
  {"p": "A falha número um de API não é injeção nem criptografia: é **autorização por objeto** (BOLA). A rota confere que o usuário está logado, e não que o pedido `/pedidos/43` é **dele**. Trocar o número na URL mostra o pedido de outra pessoa."},
  { code: `adopt Kiln

pedidos := {
    "42": {"id": "42", "dono": "ana", "total": 120},
    "43": {"id": "43", "dono": "bia", "total": 900}
}

// Quem e o usuario sai do TOKEN, e nunca do corpo ou da query.
// O Kiln entrega os cabecalhos em minusculas, como o HTTP/2 os escreve.
action usuario_de(cabecalhos):
    yield {"t-ana": "ana", "t-bia": "bia"}[cabecalhos["authorization"] ?? ""] ?? void

server api on 0:
    route GET "/pedidos/:id":
        quem := usuario_de(headers)
        given quem is void:
            respond 401 json {"erro": "entre primeiro"}
        p := pedidos[params["id"]] ?? void
        // 404 tambem para o pedido de OUTRA pessoa: 403 confirmaria que existe.
        given p is void or p["dono"] isnt quem:
            respond 404 json {"erro": "pedido nao encontrado"}
        respond json p

assert Kiln.test(api, "GET", "/pedidos/42", void, {"Authorization": "t-ana"})["status"] is 200
assert Kiln.test(api, "GET", "/pedidos/43", void, {"Authorization": "t-ana"})["status"] is 404
assert Kiln.test(api, "GET", "/pedidos/42")["status"] is 401
out "BOLA fechado: o dono e conferido por objeto"`, lang: 'df' },
  {"h2": "O OWASP API Top 10 (2023)"},
  {"table": {"head": ["Categoria", "A pergunta em cada rota"], "rows": [["API1 — autorização por objeto (BOLA)", "este objeto é **deste** usuário?"], ["API2 — autenticação quebrada", "o token é conferido, tem prazo, e o erro não diz qual parte errou?"], ["API3 — autorização por propriedade", "o corpo pode mudar `papel` ou `saldo`? — aceite uma lista de campos"], ["API4 — consumo sem limite", "há `rate_limit`, `body_limit` e paginação com teto?"], ["API5 — autorização por função", "a rota de administração confere o papel, e não só o login?"], ["API6 — fluxos de negócio sensíveis", "comprar 500 ingressos por script é possível?"], ["API7 — SSRF", "a URL que o cliente manda passa por `url_segura`?"], ["API8 — configuração insegura", "`secure_headers`, CORS com origem nomeada, erro sem traceback"], ["API9 — inventário", "há uma rota esquecida de uma versão antiga? `dataforge api` lista todas"], ["API10 — consumo inseguro de APIs", "a resposta do terceiro é validada como entrada de fora?"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Mass assignment (API3)", "texto": "`atualizar(usuario, body)` com o corpo inteiro deixa o cliente mandar `{\"papel\": \"admin\"}`. A correção é a mesma da minimização de dados: uma lista de **permitidos** — `Privacidade.minimizar(body, [\"nome\", \"email\"])` — e não de proibidos."}},
  {"p": "Continue em [Web](/docs/seguranca/web) e [Autorização](/docs/seguranca/autorizacao)."},
];

const headings = [{ id: 'o-owasp-api-top-10-2023', text: "O OWASP API Top 10 (2023)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Segurança de API"}
      description={"O OWASP API Top 10, e o BOLA — a falha mais comum de uma API — escrita e corrigida."}
      href={"/docs/seguranca/api"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
