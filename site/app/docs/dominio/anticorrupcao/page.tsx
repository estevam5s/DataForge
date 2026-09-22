// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Camada anticorrupção",
  description: "O modelo de um sistema externo não entra inteiro: é traduzido na fronteira, num lugar só.",
};

const blocos: Bloco[] = [
  {"p": "O ERP da empresa chama cliente de `PARCEIRO_NEGOCIO`, com o CPF em `CD_DOC` sem pontuação e o nome em maiúsculas. Se esse formato entra no seu domínio, cada regra passa a saber do ERP — e no dia em que o ERP muda, muda o seu sistema inteiro. A camada anticorrupção é o tradutor na fronteira, e o **único** lugar que conhece o modelo de fora."},
  { code: `adopt Arcane.Dominio as D

steady Cliente := D.valor("Cliente", ["nome", "cpf"],
    regra := lambda c => len(c["cpf"]) is 11, motivo := "CPF com 11 dígitos")

// a tradução: o único lugar que sabe como o ERP escreve
action do_erp(registro):
    yield Cliente(registro["NM_PARCEIRO"].title(),
                  registro["CD_DOC"].replace(".", "").replace("-", ""))

externo := {"NM_PARCEIRO": "ANA SOUZA", "CD_DOC": "123.456.789-01", "FL_ATIVO": "S"}
ana := do_erp(externo)
assert ana.nome is "Ana Souza" and ana.cpf is "12345678901"`, lang: 'df' },
  {"p": "Entre dois **contextos** do próprio sistema vale o mesmo, e `D.contexto` cobra: um contexto recusa receber um modelo de outro sem uma tradução registrada. Ver [Regras e contextos](/docs/dominio/contextos)."},
  {"list": ["**O campo que você não usa não entra** — `FL_ATIVO` fica do lado de fora até alguém precisar dele.", "**A validação é do seu modelo**, na tradução: um CPF malformado do ERP é recusado na fronteira, e não três camadas adiante.", "**A tradução tem teste próprio**, com registros reais do sistema de fora. É o teste que quebra quando o outro lado muda — e é bom que quebre ali."]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Camada anticorrupção"}
      description={"O modelo de um sistema externo não entra inteiro: é traduzido na fronteira, num lugar só."}
      href={"/docs/dominio/anticorrupcao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
