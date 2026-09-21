// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_ddd.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Regras e contextos delimitados",
  description: "A regra como objeto, e a tradução que atravessa a fronteira entre dois modelos.",
};

const blocos: Bloco[] = [
  {"h2": "A regra é um objeto, e não um `given`"},
  {"p": "Um `given` dentro do serviço não pode ser combinado, nem reaproveitado na consulta que lista \"quem pode\", nem explicado ao usuário. Os três usos são a **mesma** regra, e escrevê-la três vezes é como as três divergem."},
  { code: `steady grande := D.regra("o pedido passa de R$ 100",
    lambda p => p.ler("total", 0) bigger 100)
steady cheio := D.regra("o pedido tem ao menos 3 itens",
    lambda p => p.ler("itens", 0) bigger_eq 3)

steady vale_frete := grande.e(cheio)

given not vale_frete.vale(pedido):
    out vale_frete.por_que_nao(pedido)   // "o pedido passa de R$ 100"

com_frete := pedidos.que(vale_frete)     // a MESMA regra, como consulta`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "`por_que_nao` aponta a parte que falhou", "texto": "E não a frase inteira. \"maior de idade E mora no Brasil\" não diz qual das duas a pessoa precisa resolver — e essa frase é o que vai para a tela."}},
  {"p": "As combinações são `e`, `ou` e `nao`. Uma regra que **estoura** levanta, em vez de responder \"não vale\": devolver falso esconderia o defeito, e o usuário seria recusado por um bug."},
  {"h2": "Contexto delimitado"},
  {"p": "O \"Cliente\" de Vendas tem limite de crédito; o de Suporte tem plano e chamados abertos. São o mesmo nome e **não** são o mesmo conceito. Passar o objeto inteiro de um lado ao outro é o que faz dois modelos virarem um só — e o único não serve a ninguém."},
  { code: `suporte := D.contexto("Suporte")

suporte.receber("Vendas", "Cliente", {"nome": "Ana", "credito": 5000})
// erro: 'Suporte' nao sabe traduzir 'Cliente' de 'Vendas'.

suporte.traduzir_de("Vendas", "Cliente",
    lambda c => {"nome": c["nome"], "plano": "basico", "chamados": 0})

aqui := suporte.receber("Vendas", "Cliente", {"nome": "Ana", "credito": 5000})
assert "credito" not in aqui`, lang: 'df' },
  {"p": "É a *camada anticorrupção*: sem ela, o modelo de fora entra inteiro, e o de dentro passa a ter campos que só existem porque o outro time os tem."},
  {"h2": "Um ouvinte que estoura não impede os outros"},
  { code: `mark @vendas.ao_acontecer("PedidoPago")
action faturar(fato):
    ...

falhas := vendas.publicar(D.evento("PedidoPago", {"pedido": "PED-7"}))
out len(falhas)      // quantos ouvintes quebraram — os demais rodaram`, lang: 'df' },
  {"p": "Eles reagem a um fato que **já aconteceu**: derrubar os demais por causa de um deixaria o mundo parcialmente atualizado sem ninguém saber. As falhas voltam como dado, para quem quiser agir sobre elas."},
  {"h2": "O exemplo completo"},
  {"p": "`examples/dominio_ddd.df` percorre as sete peças com `assert` em cada afirmação — inclusive as recusas."},
];

const headings = [{ id: 'a-regra-e-um-objeto-e-nao-um-given', text: "A regra é um objeto, e não um `given`", level: 2 as const }, { id: 'contexto-delimitado', text: "Contexto delimitado", level: 2 as const }, { id: 'um-ouvinte-que-estoura-nao-impede-os-outros', text: "Um ouvinte que estoura não impede os outros", level: 2 as const }, { id: 'o-exemplo-completo', text: "O exemplo completo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Regras e contextos delimitados"}
      description={"A regra como objeto, e a tradução que atravessa a fronteira entre dois modelos."}
      href={"/docs/dominio/contextos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
