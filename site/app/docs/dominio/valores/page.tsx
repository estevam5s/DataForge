// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_ddd.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Valores e entidades",
  description: "A distinção que decide metade da modelagem — e como cada lado é cobrado.",
};

const blocos: Bloco[] = [
  {"p": "Duas pessoas com o mesmo nome são **duas pessoas**. E a mesma pessoa com outro nome continua sendo ela. O que separa uma entidade de um objeto de valor não é a mutabilidade — é a **continuidade**."},
  {"h2": "Objeto de valor"},
  { code: `steady Dinheiro := D.valor("Dinheiro", ["quantia", "moeda"],
    regra := lambda v => v["quantia"] bigger_eq 0,
    motivo := "dinheiro nao e negativo")

dez := Dinheiro(10, "BRL")
outro := Dinheiro(10, "BRL")
assert dez is outro                  // o MESMO valor

vinte := dez.com(quantia := 20)      // outro valor; o original nao muda
assert dez.quantia is 10`, lang: 'df' },
  {"p": "O `record` da linguagem já dá a imutabilidade e a igualdade estrutural, e essas duas metades são a maior parte. O que ele não dá é a **regra**: um `Dinheiro(-5, \"BRL\")` é um record perfeitamente válido, e o negócio descobre isso três camadas adiante, num extrato negativo."},
  {"callout": {"tipo": "nota", "titulo": "A regra é cobrada na criação — e no `com`", "texto": "A criação é o único ponto em que ela pode impedir o valor errado de existir. E um refinamento que só valesse ali seria uma sugestão, não um tipo: `dez.com(quantia := -1)` é recusado pela mesma regra."}},
  {"p": "Uma regra que **estoura** não vira \"valor inválido\": ela vira um erro dizendo que a regra quebrou. Dizer \"inválido\" ali esconderia o defeito real, que é da regra e não do valor."},
  {"h2": "Entidade"},
  { code: `ana := D.entidade("Pessoa", "1", nome := "Ana")
ana_maria := D.entidade("Pessoa", "1", nome := "Ana Maria")
homonima := D.entidade("Pessoa", "2", nome := "Ana")

assert ana is ana_maria       // mesma id, outro nome  -> a mesma pessoa
assert ana isnt homonima      // mesmo nome, outra id  -> duas pessoas`, lang: 'df' },
  {"p": "O identificador é **texto**, e nasce com o objeto (`D.novo_id()` dá um UUID4). Um id que o banco gera obriga a salvar antes de ter identidade — e no intervalo entre criar e confirmar o objeto existe sem ser ele mesmo."},
  {"h2": "E um valor não entra num repositório"},
  { code: `D.repositorio("Dinheiro").guardar(Dinheiro(10, "BRL"))
// erro: o que vai para um repositorio precisa de identidade`, lang: 'df' },
  {"p": "Não é uma limitação: é a distinção sendo cobrada. Se a sua peça precisa distinguir duas instâncias iguais, ela é uma **entidade** — e o módulo diz isso em vez de deixar passar."},
];

const headings = [{ id: 'objeto-de-valor', text: "Objeto de valor", level: 2 as const }, { id: 'entidade', text: "Entidade", level: 2 as const }, { id: 'e-um-valor-nao-entra-num-repositorio', text: "E um valor não entra num repositório", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Valores e entidades"}
      description={"A distinção que decide metade da modelagem — e como cada lado é cobrado."}
      href={"/docs/dominio/valores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
