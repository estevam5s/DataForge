// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_extra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Prazo e cancelamento",
  description: "Esperar para sempre é o defeito mais comum de código concorrente — e cancelar é mais difícil do que parece.",
};

const blocos: Bloco[] = [
  {"p": "Uma espera sem prazo não dá erro: ela **trava**. E um travamento não tem linha, não tem mensagem e não aparece em log — só um processo que consome zero CPU e não responde."},
  { code: `adopt Arcane.Concurrent as C

// 'com_prazo' recebe SEGUNDOS, e LEVANTA quando o tempo acaba —
// um prazo que devolvesse void calado seria indistinguível de um
// trabalho que devolveu void.
action demorado():
    sleep(300)
    yield "pronto"

monitor:
    C.com_prazo(demorado, 0.05)
    assert no
handle Error as e:
    out e.message

action rapido():
    yield "pronto"

assert C.com_prazo(rapido, 2) is "pronto"
out "o prazo transforma um travamento numa decisão"`, lang: 'df' },
  {"h2": "O `receive` sem prazo NÃO espera"},
  {"p": "É contrato da linguagem, e o contrário do que quase todo mundo supõe: sem argumento, ele devolve `void` na hora se a fila está vazia. Trocar o padrão não daria erro em programa nenhum — daria **travamento**:"},
  { code: `adopt Arcane.Concurrent as C

canal := C.canal(4)

// vazio, e sem prazo: volta na hora
assert canal.tentar_receber() is void

canal.enviar("x")
assert canal.receber() is "x"
out "sem prazo, ele não espera — e é isso que evita o travamento calado"`, lang: 'df' },
  {"h2": "Cancelar é cooperativo"},
  {"p": "Não há como matar uma thread por fora sem deixar o estado pela metade — um `kill` no meio de uma escrita é como desligar a máquina no meio de um `write`. O que existe é **pedir**, e o trabalho conferir:"},
  { code: `adopt Arcane.Concurrent as C

blueprint Trabalho:
    action setup():
        self.cancelado := no
        self.feitos := 0

    action cancelar():
        self.cancelado := yes

    action rodar(quantos):
        cycle i from 1 to quantos:
            // A conferência é do TRABALHO, e ela acontece entre as
            // unidades — nunca no meio de uma.
            given self.cancelado:
                yield "cancelado"
            self.feitos := self.feitos + 1
        yield "terminou"

t := spawn Trabalho()
t.cancelar()
assert t.rodar(1000) is "cancelado"
assert t.feitos is 0
out "cancelar é pedir, e o trabalho confere entre as unidades"`, lang: 'df' },
  {"h2": "Os quatro pontos onde conferir o cancelamento"},
  {"list": ["**Entre itens de um laço** — o mais comum, e o mais barato.", "**Antes de começar** uma unidade cara: começar para cancelar depois é desperdício puro.", "**Depois de uma espera** — quem esperou dez segundos pode ter sido cancelado no meio deles.", "**Nunca no meio de uma escrita** — uma transação pela metade é pior que um trabalho a mais."]},
  {"h2": "O prazo de quem espera, e o prazo de quem faz"},
  {"p": "São dois prazos diferentes, e confundi-los custa caro: quem **espera** desiste e segue a vida; quem **faz** continua fazendo. Sem cancelamento, um prazo de cliente só troca um travamento por um vazamento — o trabalho continua, ninguém lê o resultado, e o recurso fica preso."},
  { code: `adopt Arcane.Concurrent as C

estado := {"terminou": no}

action trabalho():
    sleep(120)
    estado["terminou"] := yes
    yield "pronto"

// Quem espera desiste em 30 ms…
monitor:
    C.com_prazo(trabalho, 0.03)
handle Error:
    out "desisti de esperar"

// …e o trabalho CONTINUA rodando: o prazo é de quem espera.
sleep(250)
assert estado["terminou"] is yes
out "o prazo não cancela o trabalho — quem cancela é o cancelamento"`, lang: 'df' },
];

const headings = [{ id: 'o-receive-sem-prazo-nao-espera', text: "O `receive` sem prazo NÃO espera", level: 2 as const }, { id: 'cancelar-e-cooperativo', text: "Cancelar é cooperativo", level: 2 as const }, { id: 'os-quatro-pontos-onde-conferir-o-cancelamento', text: "Os quatro pontos onde conferir o cancelamento", level: 2 as const }, { id: 'o-prazo-de-quem-espera-e-o-prazo-de-quem-faz', text: "O prazo de quem espera, e o prazo de quem faz", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Prazo e cancelamento"}
      description={"Esperar para sempre é o defeito mais comum de código concorrente — e cancelar é mais difícil do que parece."}
      href={"/docs/concorrencia/prazo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
