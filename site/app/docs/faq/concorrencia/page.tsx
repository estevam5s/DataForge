// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/faq.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Concorrência: qual das quatro",
  description: "thread, parallel, async/await e processos — o que cada um resolve, o que nenhum resolve, e as medidas.",
};

const blocos: Bloco[] = [
  {"p": "A pergunta chega sempre na mesma forma: *\"quero que isto rode junto\"*. Há quatro respostas na linguagem, e escolher a errada não dá erro — dá um programa que fica **mais lento**, ou que perde dado em silêncio."},
  {"h2": "A tabela de decisão"},
  {"table": {"head": ["O trabalho é", "Use", "Medido"], "rows": [["rede, disco, banco, `sleep`", "`async` / `await`", "sobrepõe de verdade"], ["várias tarefas de I/O, esperando todas", "`parallel`", "espera todas e propaga o erro"], ["disparar e não esperar", "`thread:`", "não espera — e o erro sai na hora"], ["CPU, em vários núcleos", "`P.map_processos`", "**3,45×** em 10 núcleos"], ["CPU, com `thread`", "— **não faça**", "**0,97×**: perdeu da série"], ["milhares de conexões", "`Arcane.Laco`", "2000 conexões em **1 thread**, +0 MB"]]}},
  {"h2": "A linguagem não sincroniza sozinha"},
  {"p": "Duas threads escrevendo na mesma variável perdem atualizações. Medido: **40.425 de 80.000**. Sem erro, sem aviso do runtime."},
  { code: `adopt Arcane.Concurrent as C

trava := C.mutex()
total := 0

action somar(quanto):
    action juntar():
        total := total + quanto
    // 'com_trava' toma, roda e SOLTA — inclusive quando a acao falha.
    C.com_trava(trava, juntar)

parallel:
    somar(10)
    somar(20)
    somar(30)

assert total is 60

// E para o caso mais comum — um numero que so cresce — nem precisa de
// trava: o contador ja e indivisivel.
c := C.contador()
parallel:
    c.somar(1)
    c.somar(1)
    c.somar(1)
assert c.valor() is 3
out $"total {total}, contador {c.valor()}"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A rota do Kiln é o caso que mais engana", "texto": "O Kiln usa `ThreadingHTTPServer`: cada pedido roda numa thread, e ali a concorrência é **invisível** — quem escreve a rota não vê thread nenhuma. Medido: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**. O `check` avisa com `escrita-concorrente`."}},
  {"h2": "O que o `check` pega, e o que ele não pega"},
  {"p": "O aviso dispara quando um `thread`, um `parallel` **ou uma `route`** escreve num nome que vem de fora — inclusive na forma `v[\"n\"] := …`, que é a que mais engana. A lista de métodos que disparam foi **medida, não presumida**:"},
  {"table": {"head": ["Operação", "Medido", "Avisa?"], "rows": [["`append` de 4 threads, 5 mil vezes", "20.000 de 20.000", "**não** — o GIL protege a operação inteira"], ["`v[\"n\"] := v[\"n\"] + 1`", "33.740 de 40.000", "sim"], ["`remove`, `pop`, `insert`, `sort`", "lê para decidir o que escrever", "sim"]]}},
  {"p": "A análise **para na fronteira da ação**: seguir chamada exigiria um grafo, e um aviso que depende disso seria impreciso nos dois sentidos. E é aviso, não erro — um acumulador protegido por mutex passa por aqui igual, e recusá-lo proibiria o uso correto."},
  {"h2": "`parallel` espera; `thread` não"},
  { code: `// parallel: espera TODAS, e levanta na linha do bloco
monitor:
    parallel:
        out "a"
        out "b"
handle Error as e:
    out "alguma falhou:", e.message

out "aqui so chega depois das duas"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Isto já saiu com código 0 e metade do trabalho perdida", "texto": "Até a correção, os dois faziam `except Exception` e imprimiam uma linha: o programa seguia, saía com **0**, e nenhum `handle` via o erro. Um CI passava verde. O `parallel` também abandonava as threads depois de 30 s, calado."}},
  {"h2": "Processos: o único caminho para mais de um núcleo"},
  { code: `adopt Arcane.Concurrent as P

action pesado(n):
    total := 0
    cycle i from 1 to n:
        total := total + (i * i)
    yield total

resultados := P.map_processos(pesado, [200000, 200000, 200000, 200000])
assert len(resultados) is 4
out $"{len(resultados)} blocos, cada um num nucleo"`, lang: 'df' },
  {"p": "A ação atravessa por **declaração**, e não por fechamento: a árvore do corpo, os parâmetros e o que ela lê sem criar. Do outro lado, um interpretador novo remonta tudo. É o que faz um `record` devolvido de lá ser o **mesmo tipo** daqui — se fosse cópia, o `with` recusaria o próprio resultado."},
  {"callout": {"tipo": "nota", "titulo": "Um pool que sobrevive entre chamadas", "texto": "Iniciar um processo custa mais de cem milissegundos, e num servidor isso acontece *por pedido*. `P.pool_processos()` paga uma vez — medido: 180 ms na primeira chamada, **82 ms na segunda**. O `fechar()` é explícito porque o contrário deixa processos ociosos."}},
  {"h2": "O laço de eventos, e a fibra"},
  {"p": "`Arcane.Laco` é **uma** thread dormindo no `selectors` do sistema. Medido, servidor de linha:"},
  {"table": {"head": ["Conexões", "Laço", "Thread por conexão"], "rows": [["1000", "73 ms · **1 thread** · +1 MB", "83 ms · 1000 threads · +36 MB"], ["2000", "151 ms · **1 thread** · +0 MB", "161 ms · 2000 threads · +36 MB"]]}},
  {"p": "O tempo quase empata, e esse é o número honesto. O que muda é a forma da conta: plano contra linear. E a fibra é **sem pilha** — um `emit` dentro de uma ação *chamada* não suspende. É por isso que a documentação diz fibra, e não *green thread*."},
  {"cards": [{"href": "/docs/concorrencia", "title": "Concorrência", "desc": "o guia inteiro"}, {"href": "/docs/biblioteca/concurrent", "title": "Arcane.Concurrent", "desc": "mutex, semáforo, canal, processos"}, {"href": "/docs/biblioteca/laco", "title": "Arcane.Laco", "desc": "o reator e as fibras"}]},
];

const headings = [{ id: 'a-tabela-de-decisao', text: "A tabela de decisão", level: 2 as const }, { id: 'a-linguagem-nao-sincroniza-sozinha', text: "A linguagem não sincroniza sozinha", level: 2 as const }, { id: 'o-que-o-check-pega-e-o-que-ele-nao-pega', text: "O que o `check` pega, e o que ele não pega", level: 2 as const }, { id: 'parallel-espera-thread-nao', text: "`parallel` espera; `thread` não", level: 2 as const }, { id: 'processos-o-unico-caminho-para-mais-de-um-nucleo', text: "Processos: o único caminho para mais de um núcleo", level: 2 as const }, { id: 'o-laco-de-eventos-e-a-fibra', text: "O laço de eventos, e a fibra", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Concorrência: qual das quatro"}
      description={"thread, parallel, async/await e processos — o que cada um resolve, o que nenhum resolve, e as medidas."}
      href={"/docs/faq/concorrencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
