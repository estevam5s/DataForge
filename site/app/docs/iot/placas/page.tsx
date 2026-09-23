// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "As placas",
  description: "UNO, Nano, Mega, Leonardo, UNO R4 e ESP32 — o mapa de cada uma, e por que ele vem da PLACA e não de uma tabela.",
};

const blocos: Bloco[] = [
  {"p": "Cada placa tem um mapa diferente: quantos pinos digitais, quais fazem PWM, quantos canais analógicos, qual a resolução da conversão. Escrever esse mapa no código da linguagem seria errar na primeira placa nova — então, com a placa ligada, **quem responde é ela**."},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
assert "pwm" in placa.capacidades(9)        // a PLACA disse isto
assert not ("pwm" in placa.capacidades(13))

monitor:
    placa.modo(13, "pwm")                   // e por isso isto é recusado
    assert no                               // não chega aqui
handle Error as e:
    out e.message                           // o pino 13 nao faz 'pwm'.
placa.fechar()`, lang: 'df' },
  {"h2": "Os modelos que o simulador conhece"},
  { code: `adopt Arcane.IoT as IoT

m := IoT.modelos()
assert m["uno"]["digitais"] is 14 and m["uno"]["analogicos"] is 6
assert m["mega"]["digitais"] is 54
assert 11 in m["uno"]["pwm"] and not (4 in m["uno"]["pwm"])
out sorted(keys(m))`, lang: 'df' },
  {"table": {"head": ["Modelo", "Digitais", "Analógicos", "PWM", "Tensão", "FQBN"], "rows": [["`uno`", "14", "6", "3, 5, 6, 9, 10, 11", "5 V", "`arduino:avr:uno`"], ["`nano`", "14", "8", "3, 5, 6, 9, 10, 11", "5 V", "`arduino:avr:nano`"], ["`mega`", "54", "16", "2–13, 44–46", "5 V", "`arduino:avr:mega`"], ["`leonardo`", "20", "12", "3, 5, 6, 9, 10, 11, 13", "5 V", "`arduino:avr:leonardo`"], ["`uno-r4`", "14", "6", "3, 5, 6, 9, 10, 11", "5 V", "`arduino:renesas_uno:unor4wifi`"], ["`esp32`", "34", "16", "quase todos", "**3,3 V**", "`esp32:esp32:esp32`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "3,3 V não é 5 V, e isso queima placa", "texto": "Ligar um sensor de 5 V direto num ESP32 costuma matar o pino. E a conta do sensor muda junto: a leitura analógica do ESP32 tem **12 bits** (0 a 4095), não 10. Toda função de sensor daqui recebe `referencia` e `bits` por isso — ver *Sensores*."}},
  { code: `adopt Arcane.IoT as IoT

assert IoT.tensao(1023) is 5.0                      // UNO: 10 bits, 5 V
assert round(IoT.tensao(4095, 3.3, 12), 2) is 3.3   // ESP32: 12 bits, 3,3 V`, lang: 'df' },
  {"h2": "Uma Mega tem mais pinos, e o Firmata os vê"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("mega")
assert placa.info()["pinos"] is 70
placa.modo(53, "saida")                 // um pino que não existe numa UNO
placa.escrever(53, yes)
assert placa.simulador.pino(53) is 1
placa.fechar()`, lang: 'df' },
  {"h2": "Qual é o FQBN da minha placa?"},
  {"p": "O `arduino-cli` responde, com a placa ligada:"},
  { code: `$ dataforge iot placas
  /dev/cu.usbmodem1101           Arduino UNO R4 WiFi        arduino:renesas_uno:unor4wifi`, lang: 'bash' },
  {"p": "Um FQBN em branco quer dizer que a placa foi reconhecida mas o *core* dela não está instalado — `arduino-cli core install arduino:renesas_uno` resolve."},
];

const headings = [{ id: 'os-modelos-que-o-simulador-conhece', text: "Os modelos que o simulador conhece", level: 2 as const }, { id: 'uma-mega-tem-mais-pinos-e-o-firmata-os-ve', text: "Uma Mega tem mais pinos, e o Firmata os vê", level: 2 as const }, { id: 'qual-e-o-fqbn-da-minha-placa', text: "Qual é o FQBN da minha placa?", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"As placas"}
      description={"UNO, Nano, Mega, Leonardo, UNO R4 e ESP32 — o mapa de cada uma, e por que ele vem da PLACA e não de uma tabela."}
      href={"/docs/iot/placas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
