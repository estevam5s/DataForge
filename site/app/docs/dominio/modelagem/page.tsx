// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Modelar o domínio",
  description: "Linguagem ubíqua, event storming e onde traçar a fronteira de um agregado.",
};

const blocos: Bloco[] = [
  {"p": "O código de domínio é tão bom quanto as palavras que ele usa. Se o negócio diz \"o pedido foi **faturado**\" e o código diz `status = 3`, cada conversa entre as duas pontas precisa de tradução — e a tradução é onde os requisitos se perdem."},
  {"h2": "Event storming, em três passos"},
  {"list": ["**Os fatos, no passado.** Numa parede (ou num documento), todo mundo escreve o que acontece no negócio: `PedidoFeito`, `PagamentoConfirmado`, `PedidoEnviado`. Discutir o nome de um fato é discutir o negócio.", "**O que os causa.** Antes de cada fato, o comando que o provoca (`Pagar`) e quem o dá (o cliente, um sistema, o relógio).", "**O que precisa ser consistente junto.** Os fatos que não podem divergir entre si formam um agregado. O resto se comunica por evento."]},
  {"h2": "A fronteira do agregado"},
  {"table": {"head": ["Sinal", "O que ele diz"], "rows": [["dois comandos do mesmo agregado raramente disputam", "o tamanho está bom"], ["[`AggregateVersionError`](/docs/dominio/concorrencia-otimista) frequente", "o agregado junta coisas que mudam por motivos diferentes — divida"], ["uma invariante precisa de dois agregados", "ou eles são um só, ou a regra é eventual e vira [processo](/docs/dominio/processos)"], ["o agregado carrega mil itens para mudar um", "a coleção deveria ser outro agregado, ligado por id"]]}},
  { code: `adopt Arcane.Dominio as D

// a linguagem do negócio, e não a do banco
steady Dinheiro := D.valor("Dinheiro", ["centavos", "moeda"],
    regra := lambda v => v["centavos"] bigger_eq 0, motivo := "dinheiro não é negativo")

pedido := D.agregado("Pedido", D.novo_id(), situacao := "aberto", total := Dinheiro(0, "BRL"))
mark @pedido.comando("faturar")
action faturar(p):
    given p.ler("situacao") is not "aberto":
        trigger "só um pedido aberto é faturado"
    p.mudar(situacao := "faturado")
    p.aconteceu("PedidoFaturado")

pedido.faturar()
assert pedido.ler("situacao") is "faturado"
assert pedido.eventos()[0].nome is "PedidoFaturado"`, lang: 'df' },
];

const headings = [{ id: 'event-storming-em-tres-passos', text: "Event storming, em três passos", level: 2 as const }, { id: 'a-fronteira-do-agregado', text: "A fronteira do agregado", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Modelar o domínio"}
      description={"Linguagem ubíqua, event storming e onde traçar a fronteira de um agregado."}
      href={"/docs/dominio/modelagem"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
