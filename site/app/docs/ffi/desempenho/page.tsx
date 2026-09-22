// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O custo de uma chamada",
  description: "Atravessar a fronteira custa microssegundos: um milhão de chamadas pequenas perde para um laço daqui.",
};

const blocos: Bloco[] = [
  {"p": "Chamar C não é de graça: cada chamada converte os argumentos, atravessa o `ctypes` e converte o retorno — alguns **microssegundos**. Para uma função que trabalha milissegundos (comprimir, decodificar, resolver um sistema), isso some. Para `abs(x)` num laço de um milhão, isso **é** o tempo."},
  { code: `adopt Arcane.C as C

libc := C.padrao()
abs_c := libc.funcao("abs", ["i32"], "i32")

// correto, mas cada chamada atravessa a fronteira
soma := 0
cycle i in range(-500, 500):
    soma += abs_c(i)
assert soma is 250000

// o mesmo, sem atravessar nada
assert ([abs(i) cycle i in range(-500, 500)] >> distill a, v: a + v 0) is 250000`, lang: 'df' },
  {"table": {"head": ["Vale atravessar", "Não vale"], "rows": [["uma chamada que faz muito trabalho", "muitas chamadas que fazem pouco"], ["passar um bloco inteiro de uma vez", "passar item a item"], ["a função só existe em C", "a mesma conta existe na linguagem"]]}},
  {"p": "A regra de ouro: **atravesse com lotes**. Uma função C que recebe um ponteiro e um tamanho processa um milhão de itens numa chamada só — o `qsort` no exemplo de [Callbacks](/docs/ffi/callbacks) é o modelo. E meça antes de concluir: [`dataforge profile`](/docs/cli/analise) mostra onde o tempo vai."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"O custo de uma chamada"}
      description={"Atravessar a fronteira custa microssegundos: um milhão de chamadas pequenas perde para um laço daqui."}
      href={"/docs/ffi/desempenho"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
