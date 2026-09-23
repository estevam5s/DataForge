// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "IoT e Arduino",
  description: "A linguagem falando com placa de verdade: Firmata para prototipar, sketch em C++ para o que precisa de tempo, MQTT para o resto do mundo.",
};

const blocos: Bloco[] = [
  {"p": "`Arcane.IoT` liga a linguagem a uma placa física. São três caminhos, e a escolha entre eles é a primeira decisão de qualquer projeto: **Firmata** (o computador manda, a placa obedece), **sketch** (o programa roda na placa, e a linguagem só o escreve e grava) e **MQTT** (a placa e o painel conversam por uma rede)."},
  {"table": {"head": ["Caminho", "Onde o programa roda", "Serve para", "O preço"], "rows": [["Firmata", "no computador", "prototipar, sensor de mesa, painel", "cada ordem atravessa o cabo — milissegundos"], ["Sketch", "na placa", "tempo real, autonomia, bateria", "compilar e gravar a cada mudança"], ["MQTT", "os dois, ligados por rede", "vários sensores, telemetria, automação", "depende de um broker de pé"]]}},
  {"h2": "O menor programa que fala com hardware"},
  {"p": "Com a placa ligada e o `StandardFirmata` gravado nela, isto acende o LED da placa:"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar()          // acha a porta sozinha, se houver uma só
placa.modo(13, "saida")
placa.escrever(13, yes)
sleep(500)
placa.escrever(13, no)
placa.fechar()`, lang: 'df', title: `precisa de placa` },
  {"callout": {"tipo": "nota", "titulo": "Sem placa, tudo aqui roda", "texto": "Troque `IoT.conectar()` por `IoT.conectar_simulada(\"uno\")` e o programa inteiro funciona: do outro lado do cabo fica um simulador que fala o mesmo protocolo, com o mapa de pinos da placa de verdade. É assim que os exemplos desta seção são conferidos a cada execução da suíte."}},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")
placa.escrever(13, yes)
assert placa.simulador.pino(13) is 1     // o simulador deixa PERGUNTAR
placa.fechar()
out "o LED acendeu — num Arduino de mentira"`, lang: 'df' },
  {"h2": "O que existe"},
  {"list": ["**Porta serial** escrita aqui — `termios` no macOS e no Linux, `ctypes` sobre a API do Windows. Sem `pyserial`, e sem dependência nenhuma.", "**Firmata 2.x** completo: modos, digital, analógico, PWM, servo, I²C, `sendString`, amostragem, reset.", "**Um simulador** com o mapa de seis placas (UNO, Nano, Mega, Leonardo, UNO R4, ESP32).", "**Seis sketches** gerados em C++, prontos para o `arduino-cli` compilar e gravar.", "**MQTT 3.1.1** falado à mão sobre TCP, com QoS 0 e 1, curingas e testamento.", "**`dataforge iot`** no terminal: `portas`, `doctor`, `monitorar`, `sketch`, `carregar`, `piscar`."]},
  {"h2": "O que não existe — e não vale fingir"},
  {"table": {"head": ["Não há", "Porque"], "rows": [["compilador de C++ próprio", "o `arduino-cli` faz isso, e bem; reimplementá-lo seria refazer o GCC e o avrdude"], ["gravador de bootloader próprio", "idem — `IoT.carregar` chama o `arduino-cli`"], ["TLS no MQTT", "o `ssl` da biblioteca padrão resolveria; a decisão espera um teste com certificado de verdade"], ["QoS 2", "exige guardar o estado de quatro mensagens por publicação, e quase nenhum projeto de sensor usa"], ["tempo real por Firmata", "cada ordem atravessa o cabo. O que precisa de microssegundos é sketch — ver *Quando usar cada um*"]]}},
  {"h2": "Por onde começar"},
  {"cards": [{"title": "Primeiros passos", "desc": "Ligar a placa, descobrir a porta, gravar o Firmata e ver o LED piscar.", "href": "/docs/iot/primeiros-passos"}, {"title": "Sem placa nenhuma", "desc": "O simulador, e como testar um projeto de hardware no CI.", "href": "/docs/iot/sem-placa"}, {"title": "Quando usar cada um", "desc": "Firmata ou sketch: a conta de latência, medida.", "href": "/docs/iot/quando-usar"}, {"title": "Um projeto inteiro", "desc": "A estufa: sensor, relé, histerese, painel e telemetria.", "href": "/docs/iot/projeto-estufa"}]},
];

const headings = [{ id: 'o-menor-programa-que-fala-com-hardware', text: "O menor programa que fala com hardware", level: 2 as const }, { id: 'o-que-existe', text: "O que existe", level: 2 as const }, { id: 'o-que-nao-existe-e-nao-vale-fingir', text: "O que não existe — e não vale fingir", level: 2 as const }, { id: 'por-onde-comecar', text: "Por onde começar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"IoT e Arduino"}
      description={"A linguagem falando com placa de verdade: Firmata para prototipar, sketch em C++ para o que precisa de tempo, MQTT para o resto do mundo."}
      href={"/docs/iot"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
