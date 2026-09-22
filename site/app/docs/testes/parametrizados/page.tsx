// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testes parametrizados",
  description: "Uma tabela de casos, um corpo só — e o caso que falhou aparece pelo nome.",
};

const blocos: Bloco[] = [
  {"p": "Quando dez testes têm o mesmo corpo e mudam só os dados, eles são uma tabela. `Crucible.table` roda um trial por linha: o corpo é escrito uma vez, e a falha diz **qual linha** quebrou."},
  { code: `adopt Arcane.Crucible

action categoria(idade):
    given idade smaller 0:
        trigger "idade negativa"
    given idade smaller 12:
        yield "crianca"
    given idade smaller 18:
        yield "adolescente"
    given idade smaller 60:
        yield "adulto"
    yield "idoso"

crucible "categoria por idade":
    Crucible.table("limites", [
        {"idade": 0, "esperado": "crianca"},
        {"idade": 11, "esperado": "crianca"},
        {"idade": 12, "esperado": "adolescente"},
        {"idade": 17, "esperado": "adolescente"},
        {"idade": 18, "esperado": "adulto"},
        {"idade": 59, "esperado": "adulto"},
        {"idade": 60, "esperado": "idoso"}
    ], lambda caso: Crucible.expect(categoria(caso["idade"])).to_be(caso["esperado"]))

    trial "idade negativa e recusada":
        expect(lambda => categoria(-1)).to_raise()

r := Crucible.run()
assert r["falhou"] is 0
assert r["passou"] is 8`, lang: 'df' },
  {"h2": "Quando usar tabela, e quando não"},
  {"table": {"head": ["Tabela", "Trials separados"], "rows": [["o corpo é **o mesmo** e só os dados mudam", "cada caso confere uma coisa diferente"], ["os limites de uma regra", "caminhos diferentes (sucesso, erro, vazio)"], ["a tabela da lei, linha por linha", "o caso precisa de preparo próprio"]]}},
  {"callout": {"tipo": "dica", "titulo": "A tabela como especificação", "texto": "Uma tabela de limites é o que o analista de negócio consegue ler e conferir. Mantenha as colunas com nome (`idade`, `esperado`) e não com posição — `[0, \"crianca\"]` exige saber a ordem para ler."}},
  {"p": "Para **milhares** de entradas geradas, e não uma tabela escrita: [Teste por propriedade](/docs/crucible/propriedades)."},
];

const headings = [{ id: 'quando-usar-tabela-e-quando-nao', text: "Quando usar tabela, e quando não", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testes parametrizados"}
      description={"Uma tabela de casos, um corpo só — e o caso que falhou aparece pelo nome."}
      href={"/docs/testes/parametrizados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
