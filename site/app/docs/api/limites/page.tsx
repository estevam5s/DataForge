// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/api_rest_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Limite de taxa",
  description: "429, Retry-After e a janela deslizante — e por que o limite é por cliente, não global.",
};

const blocos: Bloco[] = [
  {"p": "Sem limite, um cliente com um laço errado derruba o serviço para todos os outros. `Kiln.rate_limit(maximo, janela)` conta pedidos por IP numa janela **deslizante** e responde 429 com `Retry-After`:"},
  { code: `adopt Arcane.Kiln as Kiln

app := Kiln.app()
Kiln.use(app, Kiln.rate_limit(3, 60))
Kiln.get(app, "/busca", lambda req: Kiln.json({"ok": yes}))

status := [Kiln.test(app, "GET", "/busca")["status"] cycle i in range(5)]
assert status is [200, 200, 200, 429, 429]

bloqueado := Kiln.test(app, "GET", "/busca")
assert int(bloqueado["headers"]["Retry-After"]) bigger 0`, lang: 'df' },
  {"h2": "Janela deslizante, e não fixa"},
  {"p": "Com janela **fixa** de um minuto, um cliente manda 60 pedidos às 12:00:59 e mais 60 às 12:01:00 — 120 em um segundo, os dois dentro do limite. A janela deslizante olha sempre os últimos 60 segundos, e esse pico não passa."},
  {"table": {"head": ["Cliente", "Faz", "Ao receber 429"], "rows": [["bem escrito", "respeita o `Retry-After`", "espera o que o servidor mandou"], ["com recuo exponencial", "dobra a espera a cada falha, com sorteio", "não sincroniza com os outros"], ["mal escrito", "repete na hora", "fica bloqueado — que é o ponto"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Atrás de um proxy, todo mundo tem o mesmo IP", "texto": "O limite é por `req[\"ip\"]`. Atrás de um nginx ou de um balanceador, esse IP é o do proxy, e um cliente abusivo bloqueia todos. Configure o proxy para passar o IP real, e limite por chave de API quando houver uma."}},
];

const headings = [{ id: 'janela-deslizante-e-nao-fixa', text: "Janela deslizante, e não fixa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Limite de taxa"}
      description={"429, Retry-After e a janela deslizante — e por que o limite é por cliente, não global."}
      href={"/docs/api/limites"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
