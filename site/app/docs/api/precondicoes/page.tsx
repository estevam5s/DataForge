// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/api_rest_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Edição concorrente: ETag e If-Match",
  description: "Duas pessoas editam o mesmo recurso. Sem pré-condição, a segunda apaga a mudança da primeira — calada. Com ela, recebe 412.",
};

const blocos: Bloco[] = [
  {"p": "Ana abre o pedido 7 e começa a editar. Bia abre o mesmo pedido, muda o endereço e salva. Ana salva em seguida — e o endereço da Bia some. Nenhum erro, nenhum aviso: é a **atualização perdida**, e ela acontece em toda API que aceita `PUT` sem pré-condição."},
  {"p": "A saída é o controle de concorrência **otimista**: cada leitura devolve uma etiqueta (`ETag`) da versão lida; a escrita manda a etiqueta de volta em `If-Match`; se o recurso mudou nesse meio-tempo, o servidor responde **412** em vez de sobrescrever."},
  { code: `adopt Arcane.Kiln as Kiln

pedidos := {"7": {"endereco": "Rua A", "versao": 1}}
app := Kiln.app()

action ler(req):
    p := pedidos[req["params"]["id"]]
    yield Kiln.json(p, 200, {"ETag": Kiln.etiqueta(p["versao"])})

action salvar(req):
    p := pedidos[req["params"]["id"]] ?? void
    atual := void given p is void otherwise Kiln.etiqueta(p["versao"])
    falha := Kiln.precondicao(req, atual, yes)
    given falha is not void:
        yield falha
    p["endereco"] := req["body"]["endereco"]
    p["versao"] += 1
    yield Kiln.json(p, 200, {"ETag": Kiln.etiqueta(p["versao"])})

Kiln.get(app, "/pedidos/:id", ler)
Kiln.put(app, "/pedidos/:id", salvar)

etiqueta_da_ana := Kiln.test(app, "GET", "/pedidos/7")["headers"]["ETag"]
etiqueta_da_bia := Kiln.test(app, "GET", "/pedidos/7")["headers"]["ETag"]

bia := Kiln.test(app, "PUT", "/pedidos/7", {"endereco": "Rua B"}, {"If-Match": etiqueta_da_bia})
assert bia["status"] is 200

ana := Kiln.test(app, "PUT", "/pedidos/7", {"endereco": "Rua C"}, {"If-Match": etiqueta_da_ana})
assert ana["status"] is 412                      // a mudança da Bia não some
assert pedidos["7"]["endereco"] is "Rua B"

sem := Kiln.test(app, "PUT", "/pedidos/7", {"endereco": "Rua D"})
assert sem["status"] is 428                      // exigir := yes`, lang: 'df' },
  {"h2": "Os quatro casos"},
  {"table": {"head": ["Pedido", "Resposta", "Uso"], "rows": [["`If-Match` com a etiqueta atual", "segue", "a edição normal"], ["`If-Match` com outra etiqueta", "**412**", "alguém mudou no meio: leia de novo"], ["`If-None-Match: *`", "412 se já existe", "criar com `PUT` sem sobrescrever"], ["sem cabeçalho, com `exigir := yes`", "**428**", "a API não aceita escrita às cegas"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Etiqueta fraca nunca casa em `If-Match`", "texto": "Pela RFC 9110, `If-Match` usa comparação **forte**, e uma etiqueta `W/\"…\"` não casa nunca. O `Kiln.cache` gera etiquetas fracas, que servem para o 304 de uma leitura. Para escrita, use `Kiln.etiqueta(versao)`, que é forte."}},
  {"p": "É a mesma ideia do `versao_esperada` de um [armazém de eventos](/docs/dominio/concorrencia-otimista), só que atravessando HTTP."},
];

const headings = [{ id: 'os-quatro-casos', text: "Os quatro casos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Edição concorrente: ETag e If-Match"}
      description={"Duas pessoas editam o mesmo recurso. Sem pré-condição, a segunda apaga a mudança da primeira — calada. Com ela, recebe 412."}
      href={"/docs/api/precondicoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
