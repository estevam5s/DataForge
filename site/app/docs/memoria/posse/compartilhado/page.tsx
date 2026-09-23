// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/posse_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Compartilhado, contagem e referência fraca",
  description: "Quando há mais de um dono legítimo — e o ciclo que a contagem não resolve.",
};

const blocos: Bloco[] = [
  {"p": "Um dono só nem sempre é possível: um cache, um pool e um barramento de eventos têm **vários** interessados no mesmo objeto, e nenhum deles sabe quem é o último a sair. A contagem responde isso — e ela é **determinística**, diferente do coletor."},
  { code: `adopt Arcane.Posse as Posse

soltos := []
c := Posse.compartilhado({"conexao": 1}, lambda v => soltos.append("fechou"))
assert c.contar() is 1

// Cada 'clonar' é mais um dono.
b := c.clonar()
d := c.clonar()
assert c.contar() is 3

// E o recurso só fecha quando o ÚLTIMO sai.
c.soltar()
b.soltar()
assert soltos is []
d.soltar()
assert soltos is ["fechou"]`, lang: 'df' },
  {"p": "\"Determinística\" é a palavra que importa: o fechamento acontece **na linha do último `soltar`**, e não quando o coletor decidir passar. Para um arquivo, isso é a diferença entre um descritor liberado agora e um liberado daqui a um minuto."},
  {"h2": "A referência fraca não conta"},
  { code: `adopt Arcane.Posse as Posse

c := Posse.compartilhado({"x": 1})
f := Posse.fraco(c)

// A fraca NÃO segura o recurso vivo.
assert c.contar() is 1
assert f.vivo() is yes

// 'promover' devolve um dono de verdade — ou void, se já foi.
forte := f.promover()
assert forte is not void
assert c.contar() is 2
forte.soltar()

c.soltar()
assert f.vivo() is no
assert f.promover() is void`, lang: 'df' },
  {"h2": "Para que serve a fraca"},
  {"table": {"head": ["Caso", "Por que fraca"], "rows": [["um **cache** de objetos", "o cache não pode ser a razão de nada continuar vivo"], ["o **filho que aponta para o pai**", "forte nos dois sentidos é um ciclo, e o ciclo nunca zera"], ["um **observador**", "quem observa não deveria impedir o observado de sumir"], ["um **índice** por id", "ele é uma conveniência, não um dono"]]}},
  {"h2": "O ciclo, que é o que a contagem não resolve"},
  { code: `adopt Arcane.Posse as Posse

// Pai e filho apontando um para o outro com FORTE: a contagem de
// nenhum dos dois chega a zero, e o recurso nunca fecha.
pai := Posse.compartilhado({"nome": "pai"})
filho := Posse.compartilhado({"nome": "filho"})

// A saída: um dos lados é fraco. Aqui, o filho→pai.
fraca_para_o_pai := Posse.fraco(pai)
assert pai.contar() is 1              // a fraca não somou

pai.soltar()
assert fraca_para_o_pai.vivo() is no  // e o pai pôde sair
filho.soltar()
out "sem ciclo: o lado de volta é fraco"`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O coletor do Python continua lá", "texto": "Ele é quem resolve o ciclo que escapa — e `Arcane.Memoria` deixa medi-lo e controlá-lo. A contagem daqui não substitui o coletor: ela dá **momento** ao fechamento de um recurso, que é outra promessa. Confundir as duas é o erro mais comum ao ler esta parte."}},
];

const headings = [{ id: 'a-referencia-fraca-nao-conta', text: "A referência fraca não conta", level: 2 as const }, { id: 'para-que-serve-a-fraca', text: "Para que serve a fraca", level: 2 as const }, { id: 'o-ciclo-que-e-o-que-a-contagem-nao-resolve', text: "O ciclo, que é o que a contagem não resolve", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Compartilhado, contagem e referência fraca"}
      description={"Quando há mais de um dono legítimo — e o ciclo que a contagem não resolve."}
      href={"/docs/memoria/posse/compartilhado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
