// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_stm.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Atômicos e estruturas sem trava",
  description: "CAS, fetch-add, fila e pilha sem trava, ring buffer, executor e promessa — e o que o GIL garante de verdade.",
};

const blocos: Bloco[] = [
  {"p": "O `Contador` resolve contar. O que faltava era a peça geral: um valor que troca **só se ainda for o que você leu** — o *compare-and-swap*. É com ele que se escreve um contador sem trava, uma pilha sem trava e metade de uma STM."},
  {"h2": "CAS: a troca condicional"},
  { code: `adopt Arcane.Concurrent as C

a := C.atomico(10)

assert a.pegar() is 10
assert a.comparar_e_trocar(10, 20)       // ainda era 10: trocou
assert a.pegar() is 20
assert not a.comparar_e_trocar(10, 30)   // já não é 10: não trocou
assert a.trocar(99) is 20                // devolve o ANTERIOR
assert a.pegar() is 99`, lang: 'df' },
  {"p": "O laço clássico — leia, calcule, troque se ninguém mexeu — é a forma de escrever qualquer atualização sem trava:"},
  { code: `adopt Arcane.Concurrent as C

a := C.atomico(0)

action incrementar_sem_trava():
    persist yes:
        atual := a.pegar()
        given a.comparar_e_trocar(atual, atual + 1):
            halt

action trabalhar(i):
    cycle _ in range(0, 200):
        incrementar_sem_trava()

C.para_cada(trabalhar, [i cycle i in range(1, 11)])
assert a.pegar() is 2000`, lang: 'df' },
  {"table": {"head": ["Símbolo", "O que faz"], "rows": [["`a.pegar()` · `a.definir(x)`", "leitura e escrita indivisíveis"], ["`a.trocar(x)`", "escreve e devolve o **anterior**"], ["`a.comparar_e_trocar(esperado, novo)`", "troca só se o valor ainda for o esperado; devolve se trocou"], ["`a.somar(n)`", "soma e devolve o **novo** (fetch-add com a ordem certa)"], ["`a.pegar_e_somar(n)`", "soma e devolve o **anterior**"], ["`a.atualizar(f)`", "aplica `f`, repetindo enquanto alguém trocar"]]}},
  {"h2": "Fila, pilha e anel"},
  { code: `adopt Arcane.Concurrent as C

fila := C.fila_sem_trava()
fila.por(1)
fila.por(2)
assert fila.tirar() is 1 and fila.tamanho() is 1

pilha := C.pilha_sem_trava()
pilha.por(1)
pilha.por(2)
assert pilha.tirar() is 2            // do topo
assert pilha.tirar() is 1
assert pilha.tirar() is void         // vazia: void, e não erro

anel := C.anel(3)
cycle i from 1 to 5:
    anel.por(i)
assert anel.tudo() is [3, 4, 5]      // o mais velho sai quando enche
assert anel.cheio()`, lang: 'df' },
  {"p": "O **anel** é a estrutura de uma janela de métricas, de um log em memória e de um produtor rápido com consumidor lento — onde perder o mais velho é melhor que parar o produtor."},
  {"h2": "O que o GIL garante — e o que não"},
  {"callout": {"tipo": "atencao", "titulo": "\"Sem trava\" aqui quer dizer uma coisa específica", "texto": "`append` e `popleft` de um `deque` acontecem **inteiros** em C, sem janela entre ler e escrever: é indivisível de verdade, e está medido no repositório — quatro threads com 5 mil `append` cada entregaram 20.000 de 20.000. O que **não** é indivisível é qualquer sequência escrita em DataForge: `v[\"n\"] := v[\"n\"] + 1` perde atualização, e ali a resposta é `atomico`, `mutex` ou transação."}},
  {"table": {"head": ["Item da literatura", "Aqui"], "rows": [["compare-and-swap", "`atomico.comparar_e_trocar` — existe, e é a base do resto"], ["fetch-add, atomic load/store", "`somar`, `pegar_e_somar`, `pegar`, `definir`"], ["acquire, release, relaxed, seq-cst, fences", "**não se aplicam**: não há reordenação observável a ordenar — o GIL já dá consistência sequencial entre operações Python"], ["wait-free", "**não existe** como garantia: o laço de CAS é *lock-free*, não *wait-free* — uma thread azarada pode repetir"], ["ABA problem", "acontece, e a saída é a mesma: guarde um selo junto do valor (`(valor, versão)`) em vez do valor cru"], ["hazard pointers, epoch reclamation", "**não se aplicam**: o coletor cuida da liberação, que é o problema que essas técnicas resolvem"]]}},
  {"h2": "Executor e promessa"},
  {"p": "`C.rodar` abre uma thread por chamada; num servidor isso acontece por pedido. O **executor** paga a partida uma vez. A **promessa** é o resultado que ainda não existe e que alguém — um evento, uma resposta de rede — vai cumprir."},
  { code: `adopt Arcane.Concurrent as C

executor := C.executor(4)

action dobro(x):
    yield x * 2

tarefas := [executor.submeter(dobro, i) cycle i in range(1, 4)]
assert [C.esperar(t) cycle t in tarefas] is [2, 4, 6]
assert executor.mapear(dobro, [10, 20]) is [20, 40]
executor.fechar()
assert not executor.aberto()

p := C.promessa()

action cumprir(i):
    p.cumprir("pronto")

C.rodar(cumprir, 1)
assert p.esperar(3000) is "pronto" `, lang: 'df' },
  {"p": "Uma promessa que falha leva a falha a quem espera — e não um valor vazio:"},
  { code: `adopt Arcane.Concurrent as C

p := C.promessa()
p.falhar("deu ruim")

monitor:
    p.esperar(1000)
    assert no
handle Error as e:
    assert "deu ruim" in e.message`, lang: 'df' },
];

const headings = [{ id: 'cas-a-troca-condicional', text: "CAS: a troca condicional", level: 2 as const }, { id: 'fila-pilha-e-anel', text: "Fila, pilha e anel", level: 2 as const }, { id: 'o-que-o-gil-garante-e-o-que-nao', text: "O que o GIL garante — e o que não", level: 2 as const }, { id: 'executor-e-promessa', text: "Executor e promessa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Atômicos e estruturas sem trava"}
      description={"CAS, fetch-add, fila e pilha sem trava, ring buffer, executor e promessa — e o que o GIL garante de verdade."}
      href={"/docs/concorrencia/sem-trava"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
