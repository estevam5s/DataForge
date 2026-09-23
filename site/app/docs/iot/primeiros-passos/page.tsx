// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Primeiros passos com a placa",
  description: "Do cabo ao LED piscando: achar a porta, gravar o firmware, e o doctor que diz por que nada responde.",
};

const blocos: Bloco[] = [
  {"p": "Uma placa que não responde **também não dá erro**: a porta abre, e nada chega. As causas são poucas e sempre as mesmas, e o `doctor` confere cada uma na ordem em que elas acontecem."},
  {"h2": "1. Ver se o computador enxerga a placa"},
  { code: `$ dataforge iot portas
2 porta(s):
  /dev/cu.usbmodem1101               Arduino UNO R4 WiFi
  /dev/cu.Bluetooth-Incoming-Port    Bluetooth`, lang: 'bash' },
  {"p": "Nenhuma porta é o sintoma mais comum de todos, e quase nunca é a placa:"},
  {"list": ["**O cabo é só de energia.** Muitos cabos de celular não têm os fios de dados. É a causa nº 1.", "**Falta o driver.** Clones de UNO usam o CH340; ESP32 costuma usar CP2102 ou CH9102.", "**Num contêiner**, a porta precisa ser passada: `docker run --device=/dev/ttyACM0`."]},
  {"h2": "2. Gravar o firmware"},
  {"p": "O Firmata é um sketch como outro qualquer: ele fica na placa esperando ordens. Sem ele, a porta abre e o silêncio é total. A linguagem escreve o sketch e chama o `arduino-cli` para gravar:"},
  { code: `$ dataforge iot sketch firmata --em=/tmp/fw
escrito: /tmp/fw/firmata/firmata.ino
  grave com: dataforge iot carregar /tmp/fw/firmata --fqbn=arduino:avr:uno

$ dataforge iot carregar /tmp/fw/firmata --fqbn=arduino:avr:uno
gravado.`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "O arquivo tem o nome da pasta", "texto": "Um `.ino` solto não compila, e o erro do `arduino-cli` não diz por quê. `IoT.gravar_sketch(\"/tmp/fw\", \"firmata\")` cria `/tmp/fw/firmata/firmata.ino` — a pasta e o arquivo com o mesmo nome, que é o que o Arduino exige."}},
  {"callout": {"tipo": "info", "titulo": "Este firmware NÃO usa a biblioteca Firmata", "texto": "E a razão é concreta. O `Firmata.h` traz um `Boards.h` com a tabela de pinos de cada placa, escrita à mão, e ela para nas placas de até 2018: num **Arduino UNO R4 WiFi** o compilador responde `#error \"Please edit Boards.h with a hardware abstraction for this board\"`, e num **ESP32** também — as duas placas mais vendidas de hoje. Como `IoT.conectar` só fala Firmata, o módulo inteiro era inalcançável nelas."}},
  {"p": "O firmware que a linguagem escreve fala o protocolo direto, e **pergunta o mapa de pinos ao core** em vez de trazer tabela: `NUM_DIGITAL_PINS`, `NUM_ANALOG_INPUTS`, `digitalPinHasPWM` e `analogInputToDigitalPin` são macros que todo core do Arduino define. É a mesma regra do outro lado do cabo — quem decide se um pino faz PWM é a placa, não uma lista."},
  {"table": {"head": ["Placa", "Compila", "Pinos", "Analógicos"], "rows": [["`arduino:avr:uno`", "sim", "20", "6"], ["`arduino:avr:mega`", "sim", "70", "16"], ["`arduino:renesas_uno:unor4wifi`", "sim — a biblioteca **não**", "20", "6"], ["`esp32:esp32:esp32`", "sim — a biblioteca **não**", "40", "14"]]}},
  {"p": "As duas últimas linhas foram medidas com a placa na mesa, e não deduzidas: o LED piscou pelos dois caminhos, e `analogico(0)` devolveu ruído de um pino solto."},
  {"callout": {"tipo": "atencao", "titulo": "O R4 não define `analogInputToDigitalPin`", "texto": "Ele define só `PIN_A0`. A primeira versão deste firmware respondeu **`analogicos: 0`** numa placa com seis entradas analógicas — um zero honesto, e inútil. O recuo por `PIN_A0` resolve, e o mapa inverso é derivado do direto de propósito: escritas separadas divergiriam, e um mapa que não bate com a capacidade faz `analogico(0)` ler outro pino, calado."}},
  {"h2": "3. Piscar"},
  { code: `$ dataforge iot piscar --pino=13 --vezes=5
  1/5 ●
  2/5 ●
  3/5 ●
  4/5 ●
  5/5 ●
se o LED piscou, o caminho inteiro funciona.`, lang: 'bash' },
  {"h2": "Quando não funciona: o doctor"},
  { code: `$ dataforge iot doctor
  ✓ porta serial            /dev/cu.usbmodem1101 — Arduino UNO R4 WiFi
  ✓ a porta abre            57600 baud, 8N1
  ✗ responde Firmata        nada chegou em 5 s
  ✓ arduino-cli             0.35.3

O que costuma ser:
  1. o cabo é só de energia — troque por um de dados
  2. falta o driver USB-serial (CH340, CP2102) do clone
  3. o firmware não está gravado:
       dataforge iot sketch firmata --em=/tmp/fw
       dataforge iot carregar /tmp/fw/firmata --fqbn=arduino:avr:uno
  4. o monitor serial da IDE está com a porta aberta`, lang: 'bash' },
  {"p": "A última linha pega o erro que mais custa tempo a quem vem da IDE: **duas coisas não abrem a mesma porta**. Com o monitor serial aberto na IDE, a conexão daqui falha ou fica muda, e nada na tela explica isso."},
  {"h2": "A velocidade tem de ser a do sketch"},
  { code: `adopt Arcane.IoT as IoT

// o firmware fala 57600 — e é o padrão de IoT.conectar
assert "pwm" in IoT.modos()
out "os modos:", len(IoT.modos())`, lang: 'df' },
  {"p": "Para um sketch seu, que escreve com `Serial.println`, a velocidade é a do `Serial.begin()` dele — e o monitor do terminal pergunta:"},
  { code: `$ dataforge iot monitorar --velocidade=9600 --linhas=5 --prazo=10
  temperatura: 21.4
  temperatura: 21.5
  temperatura: 21.4`, lang: 'bash' },
];

const headings = [{ id: '1-ver-se-o-computador-enxerga-a-placa', text: "1. Ver se o computador enxerga a placa", level: 2 as const }, { id: '2-gravar-o-firmware', text: "2. Gravar o firmware", level: 2 as const }, { id: '3-piscar', text: "3. Piscar", level: 2 as const }, { id: 'quando-nao-funciona-o-doctor', text: "Quando não funciona: o doctor", level: 2 as const }, { id: 'a-velocidade-tem-de-ser-a-do-sketch', text: "A velocidade tem de ser a do sketch", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Primeiros passos com a placa"}
      description={"Do cabo ao LED piscando: achar a porta, gravar o firmware, e o doctor que diz por que nada responde."}
      href={"/docs/iot/primeiros-passos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
