// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/faq.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Hardware: a placa responde?",
  description: "O que funciona com Arduino e ESP32, o que foi medido com a placa na mesa, e o que a linguagem não faz.",
};

const blocos: Bloco[] = [
  {"p": "Responde — e esta página foi escrita com duas placas ligadas. A distinção que importa vem primeiro: **a linguagem fala *com* a placa, e não roda *dentro* dela.**"},
  {"h2": "O modelo"},
  {"p": "Você grava um firmware na placa uma vez. A partir daí ela deixa de ter um programa e passa a ter um **protocolo**: obedece. Quem decide é o computador, e o laço de trabalho passa a ser o dele — sem recompilar, sem regravar, sem esperar o upload."},
  { code: `$ dataforge iot portas
$ dataforge iot sketch firmata --em=/tmp/fw
$ dataforge iot carregar /tmp/fw/firmata --fqbn=arduino:renesas_uno:unor4wifi
$ dataforge iot piscar --pino=13 --vezes=5`, lang: 'bash' },
  {"h2": "O que foi medido, com a placa na mesa"},
  {"table": {"head": ["Placa", "Pinos", "Analógicos", "Provado"], "rows": [["Arduino UNO R4 WiFi", "20", "6", "LED no 13, PWM no 9, A0 lendo ruído"], ["ESP32-D0WD-V3", "40", "14", "LED no GPIO2, mapa de ADC completo"], ["`arduino:avr:uno`", "20", "6", "compilação"], ["`arduino:avr:mega`", "70", "16", "compilação"]]}},
  {"callout": {"tipo": "nota", "titulo": "O firmware não usa a biblioteca Firmata", "texto": "O `Firmata.h` traz um `Boards.h` com a tabela de pinos de cada placa, escrita à mão, e ela para em 2018: num UNO R4 e num ESP32 o compilador responde `#error \"Please edit Boards.h\"`. As duas placas mais vendidas de hoje. O firmware que a linguagem escreve fala o protocolo direto e **pergunta o mapa de pinos ao core** — `NUM_DIGITAL_PINS`, `digitalPinHasPWM`, `analogInputToDigitalPin` são macros que todo core define."}},
  {"h2": "Nada de tabela de pinos"},
  {"p": "`modo(13, \"pwm\")` é recusado porque a **placa** disse que aquele pino não faz PWM — ela responde a pergunta de capacidade no handshake. Uma tabela escrita na linguagem envelheceria na primeira placa nova, e UNO, Mega e ESP32 têm mapas diferentes."},
  {"h2": "As duas armadilhas que mais custam tempo"},
  {"list": ["**Sem `relatar_analogico(canal)` a leitura é zero, calada.** A placa envia sozinha, ela não responde perguntas — sem ligar o relatório, `analogico(0)` devolve o valor inicial para sempre.", "**`escala` limita por padrão.** O `map()` do C não limita, e um ADC que devolve 1024 por ruído vira 101% num painel."]},
  {"h2": "Sem placa, com o simulador"},
  {"p": "`IoT.conectar_simulada(\"uno\")` devolve uma placa que fala os **mesmos bytes**. Ela não é um dublê da API: é um dispositivo do outro lado do cabo, e por isso exercita o parser, a partição em sete bits e o sysex — que é onde estão os erros."},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")
placa.escrever(13, 1)
assert placa.ler(13) is 1
assert placa.info()["firmware"]["nome"] is "DataForge"
out $"{placa.info()["pinos"]} pinos, sem placa nenhuma"
`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O que o simulador NÃO prova", "texto": "O cabo, o driver USB-serial, o bootloader e o gravador. Um teste que finge hardware e se anuncia como prova de hardware dá confiança sem dar garantia — por isso o teste com placa real só roda com `DATAFORGE_ARDUINO=/dev/…` apontando uma porta de verdade."}},
  {"cards": [{"href": "/docs/iot", "title": "IoT", "desc": "o guia inteiro"}, {"href": "/docs/iot/firmata", "title": "O protocolo", "desc": "o Firmata, byte a byte"}, {"href": "/docs/iot/sem-placa", "title": "Sem placa", "desc": "o simulador"}]},
];

const headings = [{ id: 'o-modelo', text: "O modelo", level: 2 as const }, { id: 'o-que-foi-medido-com-a-placa-na-mesa', text: "O que foi medido, com a placa na mesa", level: 2 as const }, { id: 'nada-de-tabela-de-pinos', text: "Nada de tabela de pinos", level: 2 as const }, { id: 'as-duas-armadilhas-que-mais-custam-tempo', text: "As duas armadilhas que mais custam tempo", level: 2 as const }, { id: 'sem-placa-com-o-simulador', text: "Sem placa, com o simulador", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Hardware: a placa responde?"}
      description={"O que funciona com Arduino e ESP32, o que foi medido com a placa na mesa, e o que a linguagem não faz."}
      href={"/docs/faq/hardware"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
