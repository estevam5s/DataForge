// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_extra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Contrapressão",
  description: "Quando o produtor é mais rápido que o consumidor — e por que uma fila sem teto é uma falha adiada.",
};

const blocos: Bloco[] = [
  {"p": "Todo sistema com produtor e consumidor tem uma pergunta que precisa de resposta: **o que acontece quando o produtor é mais rápido?** Há três respostas possíveis, e escolher por omissão significa escolher a pior."},
  {"table": {"head": ["Resposta", "O que custa", "Quando serve"], "rows": [["a fila cresce sem teto", "**morte por memória**, horas depois", "nunca — é a escolha por omissão"], ["o produtor **espera**", "a lentidão sobe para quem produz", "quase sempre: é a contrapressão"], ["descarta o mais velho", "perde dado, de propósito e visivelmente", "telemetria, métrica, quadro de vídeo"]]}},
  { code: `adopt Arcane.Concurrent as C

// Um canal com TETO: o 'enviar' espera quando ele está cheio, e é
// isso que faz a lentidão do consumidor chegar ao produtor.
canal := C.canal(3)

produzidos := []
action produtor():
    cycle i from 1 to 5:
        canal.enviar(i)
        produzidos.append(i)
    canal.fechar()

action consumidor():
    recebidos := []
    cycle item in canal:
        recebidos.append(item)
        sleep(10)
    yield recebidos

resultado := void
parallel:
    produtor()
    thread:
        resultado := consumidor()

assert resultado is [1, 2, 3, 4, 5]
out $"produziu {len(produzidos)}, consumiu {len(resultado)} — sem perder nada"`, lang: 'df' },
  {"h2": "A fila sem teto é uma falha adiada"},
  {"p": "Ela não dá erro: ela funciona em todos os testes, porque num teste o consumidor acompanha. Em produção, a fila cresce nas horas de pico, a memória acaba de madrugada, e o processo é morto pelo sistema — sem mensagem, e longe da causa."},
  { code: `adopt Arcane.Concurrent as C

// Um teto pequeno, de propósito, para a espera aparecer:
canal := C.canal(1)
canal.enviar("a")
assert canal.cheio() is yes

// 'tentar_enviar' NÃO espera: ele devolve no quando não cabe. É o que
// permite ao produtor decidir — esperar, descartar ou contar.
assert canal.tentar_enviar("b") is no

descartados := 0
given not canal.tentar_enviar("c"):
    descartados += 1
assert descartados is 1
out "cheio: o produtor decide o que fazer, em vez de a memória decidir"`, lang: 'df' },
  {"h2": "Descartar, quando descartar é a resposta certa"},
  {"p": "Para telemetria, a leitura de trinta segundos atrás **não tem valor**: mandar a mais nova e perder a velha é melhor que atrasar as duas. O importante é que isso seja uma decisão escrita, e **contada**:"},
  { code: `adopt Arcane.Concurrent as C

blueprint Telemetria:
    action setup(teto):
        self.canal := C.canal(teto)
        self.descartados := 0

    action medir(valor):
        given not self.canal.tentar_enviar(valor):
            // Contar o descarte é o que separa "escolha" de "defeito":
            // sem o número, ninguém sabe que está perdendo dado.
            self.descartados := self.descartados + 1
            yield no
        yield yes

t := spawn Telemetria(2)
assert t.medir(1) is yes
assert t.medir(2) is yes
assert t.medir(3) is no
assert t.descartados is 1
out $"descartados: {t.descartados} — e o número aparece no painel"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O canal do laço de eventos tem o mesmo teto", "texto": "`Arcane.Laco` aceita um teto na fila de prontas pelo mesmo motivo: sem ele, uma fonte mais rápida que o consumo troca uma falha visível por morte por memória. A escolha é sempre entre falhar cedo e falhar tarde."}},
];

const headings = [{ id: 'a-fila-sem-teto-e-uma-falha-adiada', text: "A fila sem teto é uma falha adiada", level: 2 as const }, { id: 'descartar-quando-descartar-e-a-resposta-certa', text: "Descartar, quando descartar é a resposta certa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Contrapressão"}
      description={"Quando o produtor é mais rápido que o consumidor — e por que uma fila sem teto é uma falha adiada."}
      href={"/docs/concorrencia/contrapressao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
