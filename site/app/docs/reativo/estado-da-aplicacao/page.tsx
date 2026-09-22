// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O estado de uma aplicação",
  description: "Sinais para o que se escreve, derivados para o que se calcula, comandos para o que muda — e nada mais.",
};

const blocos: Bloco[] = [
  {"p": "Uma aplicação reativa fica fácil de manter quando o estado segue três regras: **o que é informação de fato** é sinal; **o que se calcula a partir dela** é derivado; **o que muda** passa por uma ação nomeada, dentro de um lote. Um derivado guardado como sinal fica desatualizado; um sinal que qualquer um escreve vira depuração de \"quem mudou isto?\"."},
  { code: `adopt Arcane.Reativo as R

// ── o estado: só o que não se calcula ──
itens := R.sinal([])
cupom := R.sinal(void)

// ── o que se calcula ──
subtotal := R.derivado(lambda => (itens.ler() >> distill acc, i: acc + i["preco"] * i["qtd"] 0))
desconto := R.derivado(lambda => (subtotal.ler() * 0.1 given cupom.ler() is "DEZ" otherwise 0))
total := R.derivado(lambda => subtotal.ler() - desconto.ler())

// ── o que muda: comandos com nome ──
action adicionar(nome, preco, qtd):
    itens.escrever(itens.ler() + [{"nome": nome, "preco": preco, "qtd": qtd}])

action aplicar_cupom(codigo):
    cupom.escrever(codigo)

historico := R.historico(itens)
adicionar("café", 30, 2)
adicionar("filtro", 10, 1)
aplicar_cupom("DEZ")
assert total.ler() is 63.0
historico.desfazer()                  // tira o filtro
assert total.ler() is 54.0`, lang: 'df' },
  {"list": ["**Nunca guarde um calculado.** `total` como sinal precisaria ser atualizado em cada comando — e o primeiro comando novo esquece.", "**A lista é trocada, não mudada.** `itens.escrever(itens.ler() + [novo])` notifica; `itens.ler().append(novo)` muda a lista por dentro e **ninguém é avisado**.", "**O desfazer vem de graça** quando o estado é pequeno e os comandos só escrevem nele."]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"O estado de uma aplicação"}
      description={"Sinais para o que se escreve, derivados para o que se calcula, comandos para o que muda — e nada mais."}
      href={"/docs/reativo/estado-da-aplicacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
