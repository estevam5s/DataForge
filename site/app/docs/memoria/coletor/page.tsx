// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O coletor sob controle",
  description: "Desligar o coletor não vaza memória — a distinção que quase todo mundo erra. Mais congelar, limiares e a arena.",
};

const blocos: Bloco[] = [
  {"callout": {"tipo": "atencao", "titulo": "A distinção que quase todo mundo erra", "texto": "No CPython, quem libera é a **contagem de referência**, e ela roda na hora. O **coletor** existe só para o **ciclo** — `a` apontando para `b` que aponta para `a`. Desligar o coletor **não vaza memória em geral**: só deixa o ciclo para trás. É por isso que desligá-lo num trecho curto e sensível a latência é uma técnica segura, e não uma gambiarra."}},
  { code: `adopt Arcane.Memoria as Mem

action critico():
    total := 0
    cycle i from 1 to 100:
        total += i
    yield total

assert Mem.gc_ligado()

// sem coletor no trecho sensivel — e ele volta depois, SEMPRE
assert Mem.sem_gc(critico) is 5050
assert Mem.gc_ligado()`, lang: 'df' },
  {"p": "O `finally` do `sem_gc` não é detalhe: deixar o coletor desligado por causa de um erro é muito pior que a pausa que se queria evitar — e o programa seguiria assim até terminar, sem nada denunciando. Há teste cobrando isso com um corpo que falha."},
  {"h2": "A medida, e não a promessa"},
  {"p": "A frase \"desligar o coletor reduz pausa\" seria fé sem número. O teste mede a **mesma** carga dos dois jeitos, e o que ele mede é o tempo que o coletor passou parando o programa:"},
  { code: `com o coletor ligado    pausas: 3    total: 1,84 ms
com o coletor desligado pausas: 0    total: 0,00 ms`, lang: 'text', title: `6000 ciclos alocados` },
  {"h2": "Congelar, e os limiares"},
  {"table": {"head": ["Símbolo", "O que faz"], "rows": [["`Mem.gc_congelar()`", "tira o que **já vive** das varreduras, para sempre — o que um servidor faz depois da carga e antes do primeiro pedido"], ["`Mem.gc_limiares()`", "lê os três; com três argumentos, ajusta"], ["`Mem.gc_geracoes()`", "quantas coletas houve em cada geração, e quanto cada uma rendeu"], ["`Mem.coletar(geracao)`", "força uma coleta agora"]]}},
  { code: `adopt Arcane.Memoria as Mem

assert len(Mem.gc_limiares()) is 3
assert len(Mem.gc_geracoes()) is 3

antes := Mem.gc_congelados()
Mem.gc_congelar()
assert Mem.gc_congelados() bigger antes
Mem.gc_descongelar()`, lang: 'df' },
  {"h2": "Arena"},
  {"p": "**Não é um allocator**: quem aloca continua sendo o Python, e não há como trocá-lo por dentro. O que a arena troca é o **padrão de uso** — em vez de criar e descartar por volta, um lote é preparado, emprestado e devolvido."},
  { code: `adopt Arcane.Memoria as Mem

arena := Mem.arena(3, lambda => {"n": 0})
a := Mem.pegar(arena)
Mem.devolver(arena, a)
b := Mem.pegar(arena)         // o MESMO objeto volta

e := Mem.arena_estatisticas(arena)
assert e["criados"] is 3       // o lote, preparado de uma vez
assert e["reaproveitados"] is 1
assert e["em_uso"] is 1`, lang: 'df' },
  {"table": {"head": ["Decisão", "Por quê"], "rows": [["a arena **cresce** quando acaba, e **conta** que cresceu", "travar seria pior; crescer calado esconderia que ela foi dimensionada errada"], ["devolver o que não veio dela é **recusado**", "o lote cresceria com estranhos, e o próximo `pegar` entregaria um deles"], ["`limpar` solta o lote inteiro numa chamada", "é o tempo de vida de arena da literatura, e a operação que ela existe para ter"]]}},
  {"callout": {"tipo": "nota", "titulo": "O ganho aparece quando o objeto é caro de montar", "texto": "Não quando ele é um vault de três chaves. Uma arena de dicionários vazios troca alocação por indireção e não ganha nada — meça antes, com [`Arcane.Perfil`](/docs/observabilidade/comparar), e só mantenha se o `comparar` disser que a diferença é **significativa**."}},
];

const headings = [{ id: 'a-medida-e-nao-a-promessa', text: "A medida, e não a promessa", level: 2 as const }, { id: 'congelar-e-os-limiares', text: "Congelar, e os limiares", level: 2 as const }, { id: 'arena', text: "Arena", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O coletor sob controle"}
      description={"Desligar o coletor não vaza memória — a distinção que quase todo mundo erra. Mais congelar, limiares e a arena."}
      href={"/docs/memoria/coletor"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
