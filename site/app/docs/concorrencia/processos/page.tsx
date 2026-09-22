// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Processos",
  description: "O único caminho para mais de um núcleo no CPython — o que atravessa, o que custa, e o pool que paga a partida uma vez.",
};

const blocos: Bloco[] = [
  {"p": "Duas threads do CPython nunca executam código Python ao mesmo tempo — o **GIL** alterna entre elas. Para conta pesada, threads não ajudam: 8 blocos de CPU em 10 núcleos levaram 1607 ms em série e 1654 ms em threads. Em **processos**, 466 ms: 3,45× mais rápido."},
  { code: `adopt Arcane.Concurrent as P

action pesado(n):
    total := 0
    cycle i from 1 to n:
        total += i * i
    yield total

resultados := P.map_processos(pesado, [1000, 2000, 3000])
assert resultados[0] is 333833500                  // na ordem da entrada`, lang: 'df' },
  {"h2": "O que atravessa"},
  {"p": "Um processo não vê a memória do outro. O que vai é a **declaração** da ação — a árvore, os parâmetros, os records e blueprints que ela usa — e os dados, copiados. Uma conexão de banco ou um arquivo aberto não atravessam: abra do lado de lá."},
  {"table": {"head": ["Use", "Quando"], "rows": [["`P.map`", "trabalho que **espera** (rede, disco): threads bastam"], ["`P.map_processos`", "conta pesada, uma vez"], ["`P.pool_processos()`", "conta pesada **repetida**: a partida (~100 ms) é paga uma vez"], ["nada disso", "trabalho pequeno: a partida de um processo custa mais que a conta"]]}},
  {"p": "O detalhe completo — o que é copiado, a nota de erro que diz que ele aconteceu no outro processo, o `forkserver` — está em [Paralelismo](/docs/tecnicas/processos)."},
];

const headings = [{ id: 'o-que-atravessa', text: "O que atravessa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Processos"}
      description={"O único caminho para mais de um núcleo no CPython — o que atravessa, o que custa, e o pool que paga a partida uma vez."}
      href={"/docs/concorrencia/processos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
