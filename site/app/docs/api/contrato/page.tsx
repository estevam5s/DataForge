// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/api_rest_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O contrato: OpenAPI",
  description: "O documento que Swagger, Postman e gerador de cliente leem — gerado das rotas, e conferido num teste.",
};

const blocos: Bloco[] = [
  {"p": "`API.openapi` lê as rotas registradas e escreve o documento OpenAPI 3.1 — o formato que o Swagger UI desenha, que o Postman importa e que gera cliente em vinte linguagens. Ele sai **das rotas**, e não de um arquivo escrito à mão: um documento escrito à mão descreve a API que alguém lembrou de descrever."},
  { code: `adopt Arcane.Kiln as Kiln
adopt Arcane.API as API

app := Kiln.app()
Kiln.get(app, "/pedidos/:id", lambda req: Kiln.json({"id": 1}))
Kiln.post(app, "/pedidos", lambda req: Kiln.json({"id": 2}, 201))

out API.rotas(app)
doc := from_json(API.openapi(app, {"titulo": "Loja", "versao": "1.0.0"}))
assert doc["info"]["title"] is "Loja"
assert "/pedidos/{id}" in doc["paths"]            // ':id' vira '{id}'
assert "post" in doc["paths"]["/pedidos"]`, lang: 'df' },
  {"h2": "O teste de contrato"},
  {"p": "O documento é um contrato, e contrato se confere. Um teste que compara as rotas de hoje com a lista publicada falha no dia em que alguém remove uma rota sem avisar — antes do cliente descobrir em produção:"},
  { code: `adopt Arcane.Kiln as Kiln
adopt Arcane.API as API

app := Kiln.app()
Kiln.get(app, "/pedidos", lambda req: Kiln.json([]))
Kiln.get(app, "/pedidos/:id", lambda req: Kiln.json({}))

steady PUBLICADAS := ["GET /pedidos", "GET /pedidos/:id"]
hoje := [$"{r["method"]} {r["path"]}" cycle r in API.rotas(app)]
sumiram := [r cycle r in PUBLICADAS given r not in hoje]
assert sumiram is []`, lang: 'df' },
  {"p": "Para exportar para as ferramentas: `API.postman(app)`, `API.insomnia(app)`, `API.curl(app)` e `API.markdown(app)`. A referência completa está em [a API do site](/api), que é gerada do mesmo jeito."},
];

const headings = [{ id: 'o-teste-de-contrato', text: "O teste de contrato", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O contrato: OpenAPI"}
      description={"O documento que Swagger, Postman e gerador de cliente leem — gerado das rotas, e conferido num teste."}
      href={"/docs/api/contrato"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
