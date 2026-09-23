// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_extra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Paralelismo de dados",
  description: "Dividir a coleção, e o tamanho do bloco que decide se vale a pena.",
};

const blocos: Bloco[] = [
  {"p": "O caso mais comum de concorrência não é um servidor: é **uma coleção grande e a mesma conta para cada item**. Aqui o modelo importa mais que em qualquer outro lugar, porque a resposta muda conforme o trabalho é de E/S ou de CPU."},
  {"table": {"head": ["O trabalho é", "Use", "Porque"], "rows": [["rede, disco, banco", "`C.map` (threads)", "o GIL é solto na espera — a sobreposição é real"], ["conta pura", "`C.map_processos`", "o GIL serializa threads; processos usam núcleos"], ["mistura", "meça os dois", "a intuição erra aqui mais que em qualquer outra parte"], ["menos de ~10 ms por item", "nenhum dos dois", "a partida custa mais que o trabalho"]]}},
  { code: `adopt Arcane.Concurrent as C

action dobrar(x):
    yield x * 2

// 'map' roda a ação sobre a coleção em threads, e devolve NA ORDEM
// da entrada — o resultado não depende de quem terminou primeiro.
assert C.map(dobrar, [1, 2, 3, 4, 5]) is [2, 4, 6, 8, 10]

// E a ordem se mantém mesmo quando os itens terminam fora de ordem:
action devagar_se_par(x):
    given x % 2 is 0:
        sleep(20)
    yield x

assert C.map(devagar_se_par, [1, 2, 3, 4]) is [1, 2, 3, 4]
out "a ordem da saída é a da entrada, e isso não é acidente"`, lang: 'df' },
  {"h2": "O tamanho do bloco"},
  {"p": "Mandar um item por vez para outro processo faz o **transporte** dominar: cada item atravessa a fronteira, e a conta de um item é mais barata que a cópia dele. Blocos resolvem isso:"},
  { code: `adopt Arcane.Concurrent as C

action somar_bloco(bloco):
    // A ação recebe uma LISTA por vez, e não um item.
    yield bloco >> distill a, v: a + v 0

// 'lotes' faz as duas coisas: quebra em blocos do tamanho pedido e
// roda a ação sobre cada bloco. Um trabalho por BLOCO, e não por
// item — é o que impede o transporte de dominar a conta.
parciais := C.lotes(somar_bloco, [i cycle i in range(1, 11)], 4)
assert len(parciais) is 3
assert (parciais >> distill a, v: a + v 0) is 55
out $"{len(parciais)} blocos, soma {parciais >> distill a, v: a + v 0}"`, lang: 'df' },
  {"h2": "Quando não vale a pena"},
  { code: `adopt Arcane.Bench as B

action trivial(x):
    yield x + 1

// A regra prática: se o item custa menos que a partida, a série
// ganha. Medir é a única forma de saber de que lado você está.
action duzentos():
    yield [trivial(i) cycle i in range(0, 200)]

serie := B.medir(duzentos)
assert serie["ms"] >= 0
out $"200 itens triviais em série: {round(serie['ms'], 2)} ms"
out "com threads isso ficaria MAIS lento — a partida domina"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O erro de medida que mais engana", "texto": "Comparar paralelo com série medindo **tempo absoluto** mede a máquina, não o paralelismo — e um runner de três núcleos reprova um código correto. A trava deste repositório cobra um **fator**, e quando nem isso basta há o ponto de calibração: um algoritmo conhecidamente linear medido no mesmo instante."}},
  {"h2": "Espalhar e juntar, com falha"},
  { code: `adopt Arcane.Concurrent as C

action pode_falhar(x):
    given x is 3:
        trigger $"o item {x} falhou"
    yield x * 10

// 'esperar_todas' junta os resultados; a falha de um item vira erro
// do conjunto, e não um buraco silencioso no meio da lista.
monitor:
    C.map(pode_falhar, [1, 2, 3, 4])
    assert no
handle Error as e:
    out e.message`, lang: 'df' },
  {"p": "Um `map` que devolvesse `void` no lugar do item que falhou parece conveniente e é a origem do pior tipo de defeito: o resultado tem o tamanho certo, a soma está errada, e não há erro em lugar nenhum."},
];

const headings = [{ id: 'o-tamanho-do-bloco', text: "O tamanho do bloco", level: 2 as const }, { id: 'quando-nao-vale-a-pena', text: "Quando não vale a pena", level: 2 as const }, { id: 'espalhar-e-juntar-com-falha', text: "Espalhar e juntar, com falha", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Paralelismo de dados"}
      description={"Dividir a coleção, e o tamanho do bloco que decide se vale a pena."}
      href={"/docs/concorrencia/dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
