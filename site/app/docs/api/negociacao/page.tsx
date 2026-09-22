// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/api_rest_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Negociação de conteúdo",
  description: "JSON ou CSV no mesmo endereço: o cabeçalho Accept, o q, o curinga — e quando responder 406.",
};

const blocos: Bloco[] = [
  {"p": "O mesmo recurso pode ter mais de uma representação: a lista de pedidos em JSON para um programa, em CSV para uma planilha. O cliente diz o que aceita no `Accept`, com um peso `q` de 0 a 1, e o servidor escolhe. `Kiln.negociar` faz a escolha como a RFC 9110 manda."},
  { code: `adopt Arcane.Kiln as Kiln

pedidos := [{"id": 1, "total": 50}, {"id": 2, "total": 70}]
app := Kiln.app()

action listar(req):
    tipo := Kiln.negociar(req, ["application/json", "text/csv"])
    given tipo is void:
        yield Kiln.problema(406, "Formato não disponível",
            "esta rota responde application/json ou text/csv")
    given tipo is "text/csv":
        linhas := ["id,total"] + [$"{p["id"]},{p["total"]}" cycle p in pedidos]
        yield Kiln.text(linhas.join("\\n"), 200, {"Content-Type": "text/csv; charset=utf-8", "Vary": "Accept"})
    yield Kiln.json(pedidos, 200, {"Vary": "Accept"})

Kiln.get(app, "/pedidos", listar)

assert Kiln.test(app, "GET", "/pedidos")["body"][0]["id"] is 1
csv := Kiln.test(app, "GET", "/pedidos", void, {"Accept": "text/csv"})
assert csv["body"].starts_with("id,total")
assert Kiln.test(app, "GET", "/pedidos", void, {"Accept": "image/png"})["status"] is 406`, lang: 'df' },
  {"h2": "As regras, na ordem em que decidem"},
  {"table": {"head": ["Accept", "Escolhe", "Por quê"], "rows": [["(nenhum)", "o primeiro oferecido", "o cliente não pediu nada"], ["`text/csv;q=0.5, application/json`", "JSON", "q maior vence"], ["`text/*`", "o primeiro `text/…` oferecido", "curinga de subtipo"], ["`*/*, text/csv;q=0`", "nunca CSV", "`q=0` é recusa explícita, e a faixa mais específica decide"], ["`image/png`", "`void` → 406", "nada que você oferece serve"]]}},
  {"callout": {"tipo": "atencao", "titulo": "`Vary: Accept`", "texto": "Quando a mesma URL responde formatos diferentes, um cache no caminho (CDN, proxy, navegador) precisa saber que a resposta **depende** do `Accept`. Sem o `Vary`, o primeiro CSV guardado é entregue a quem pediu JSON."}},
  {"callout": {"tipo": "dica", "titulo": "No empate, vale a sua ordem", "texto": "Com `Accept: */*`, qualquer oferecido serve com q=1. A escolha cai no **primeiro da sua lista** — então ponha nela primeiro o formato que você prefere servir."}},
];

const headings = [{ id: 'as-regras-na-ordem-em-que-decidem', text: "As regras, na ordem em que decidem", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Negociação de conteúdo"}
      description={"JSON ou CSV no mesmo endereço: o cabeçalho Accept, o q, o curinga — e quando responder 406."}
      href={"/docs/api/negociacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
