// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Concorrência",
  description: "Threads, atores, canais, travas, STM e processos — e a regra que decide qual: quem pode escrever neste estado?",
};

const blocos: Bloco[] = [
  {"p": "A linguagem **não sincroniza sozinha**. Duas threads escrevendo na mesma variável perdem atualizações — medido: 40.425 de 80.000, calado. Toda ferramenta desta seção responde de um jeito à mesma pergunta: **quem pode escrever neste estado, e quando?**"},
  { code: `adopt Arcane.Concurrent as P

// um ator: o estado mora numa thread, e as outras só enviam
contador := P.ator(lambda n, m: n + m, 0)
action somar_muito():
    cycle i from 1 to 500:
        contador.enviar(1)
parallel:
    somar_muito()
    somar_muito()
assert contador.parar() is 1000          // nenhuma atualização perdida`, lang: 'df' },
  {"table": {"head": ["Resposta", "Ferramenta", "Página"], "rows": [["ninguém: cada um tem o seu", "variável por thread", "[Uma por thread](/docs/partida/por-thread)"], ["só um dono, por mensagem", "**ator**", "[Atores](/docs/concorrencia/atores)"], ["passa de mão em mão", "canal", "[Canais](/docs/concorrencia/canais)"], ["qualquer um, um de cada vez", "mutex, semáforo", "[Travas](/docs/concorrencia/travas)"], ["qualquer um, junto ou nada", "STM", "[Memória transacional](/docs/concorrencia/stm)"], ["ninguém compartilha memória", "processos", "[Processos](/docs/concorrencia/processos)"]]}},
  {"cards": [{"href": "/docs/concorrencia/atores", "title": "Atores", "desc": "estado com dono, alcançado por mensagem"}, {"href": "/docs/concorrencia/canais", "title": "Canais entre threads", "desc": "o produtor que espera, e o fechar"}, {"href": "/docs/concorrencia/travas", "title": "Travas", "desc": "mutex, semáforo, leitura e escrita"}, {"href": "/docs/concorrencia/corridas", "title": "Condição de corrida", "desc": "o ler-somar-escrever, medido"}, {"href": "/docs/concorrencia/impasse", "title": "Impasse", "desc": "duas travas em ordens diferentes"}, {"href": "/docs/concorrencia/processos", "title": "Processos", "desc": "o único caminho para mais de um núcleo"}, {"href": "/docs/concorrencia/padroes", "title": "Padrões", "desc": "produtor-consumidor, pool, espalhar e juntar"}, {"href": "/docs/concorrencia/stm", "title": "Memória transacional", "desc": "escritas que acontecem juntas"}, {"href": "/docs/concorrencia/sem-trava", "title": "Atômicos e sem trava", "desc": "contador, anel e pilha"}, {"href": "/docs/runtime/escolher", "title": "Laço, thread, async ou processo", "desc": "qual modelo para qual trabalho"}, {"href": "/docs/concorrencia/mapa", "title": "Concorrência: o mapa", "desc": "o que existe, e o que não"}]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Concorrência"}
      description={"Threads, atores, canais, travas, STM e processos — e a regra que decide qual: quem pode escrever neste estado?"}
      href={"/docs/concorrencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
