// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/api_rest_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Paginação: página, cursor e Link",
  description: "Por que ?pagina=3 pula e repete itens numa lista que muda, como um cursor opaco resolve, e o cabeçalho Link.",
};

const blocos: Bloco[] = [
  {"p": "`Kiln.paginar` corta por número de página, e isso é certo para uma lista que **não muda** enquanto alguém a percorre. Numa lista viva — um feed, uma fila de pedidos —, um item novo no topo empurra todos uma posição: quem pede a página 2 vê de novo o último item da página 1, e um item some entre as duas."},
  {"p": "O **cursor** diz *onde parou*, e não *em que posição*: \"depois do pedido 1042\" não se move quando chega o 1043. `Kiln.cursor` o empacota opaco, e com um segredo, assinado — o cliente não monta um à mão, e não consegue forjar."},
  { code: `adopt Arcane.Kiln as Kiln

steady SEGREDO := "troque-isto"
pedidos := [{"id": i} cycle i in range(1, 26)]
app := Kiln.app()

action listar(req):
    c := req["query"]["cursor"] ?? void
    depois_de := 0
    given c is not void:
        lido := Kiln.ler_cursor(c, SEGREDO)
        given lido is void:
            yield Kiln.problema(400, "Cursor inválido")
        depois_de := lido["depois_de"]
    pagina := [p cycle p in pedidos given p["id"] bigger depois_de][0:10]
    proximo := void
    given len(pagina) is 10:
        proximo := Kiln.cursor({"depois_de": pagina[-1]["id"]}, SEGREDO)
    yield Kiln.json({"itens": pagina, "proximo": proximo})

Kiln.get(app, "/pedidos", listar)

p1 := Kiln.test(app, "GET", "/pedidos")["body"]
pedidos.insert(0, {"id": 0})                   // chegou um novo no topo
p2 := Kiln.test(app, "GET", $"/pedidos?cursor={p1["proximo"]}")["body"]
assert p1["itens"][-1]["id"] is 10
assert p2["itens"][0]["id"] is 11                // nem repetiu, nem pulou
assert Kiln.test(app, "GET", "/pedidos?cursor=forjado")["status"] is 400`, lang: 'df' },
  {"h2": "O cabeçalho Link"},
  {"p": "O cliente não deveria montar URL de página: se a API trocar de página para cursor, todo cliente que monta URL quebra. O `Link` (RFC 8288) entrega os endereços prontos:"},
  { code: `adopt Arcane.Kiln as Kiln

link := Kiln.links("/pedidos?ordem=data", 2, 5)
out link
assert link.contains('</pedidos?ordem=data&pagina=3>; rel="next"')
assert link.contains('rel="prev"')`, lang: 'df' },
  {"table": {"head": ["Use", "Quando"], "rows": [["`Kiln.paginar`", "lista estável, e o cliente precisa pular para a página 7"], ["cursor", "lista que muda, feed, rolagem infinita, exportação"], ["`Kiln.links`", "sempre que houver próxima página — com qualquer dos dois"]]}},
];

const headings = [{ id: 'o-cabecalho-link', text: "O cabeçalho Link", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Paginação: página, cursor e Link"}
      description={"Por que ?pagina=3 pula e repete itens numa lista que muda, como um cursor opaco resolve, e o cabeçalho Link."}
      href={"/docs/api/paginacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
