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
  /dev/cu.usbmodemC04E301234D42      placa com USB nativo (UNO R4, Leonardo, Micro, ESP32-S3)
  /dev/cu.usbserial-1110             conversor USB-serial (FTDI, CH340, CP2102)`, lang: 'bash' },
  {"p": "Listar **não abre porta nenhuma**: abrir reinicia a placa, e um comando que só lista não pode reiniciar todos os Arduinos da mesa. As portas do sistema que não são placa (o Bluetooth e o console de depuração do macOS) ficam de fora."},
  {"p": "Nenhuma porta é o sintoma mais comum de todos, e quase nunca é a placa:"},
  {"list": ["**O cabo é só de energia.** Muitos cabos de celular não têm os fios de dados. É a causa nº 1.", "**Falta o driver.** Clones de UNO usam o CH340; ESP32 costuma usar CP2102 ou CH9102.", "**Num contêiner**, a porta precisa ser passada: `docker run --device=/dev/ttyACM0`."]},
  {"h2": "2. Gravar o firmware"},
  {"p": "O Firmata é um sketch como outro qualquer: ele fica na placa esperando ordens. Sem ele, a porta abre e o silêncio é total. A linguagem escreve o sketch e chama o `arduino-cli` para gravar:"},
  { code: `$ dataforge iot carregar firmata --porta=/dev/cu.usbmodemC04E301234D42
[==============================] 100% (16/16 pages)
gravado.`, lang: 'bash' },
  {"p": "`carregar` aceita o **nome** de um sketch (`firmata`, `pisca`, `sensor`…) e o gera numa pasta temporária, ou a pasta de um sketch seu. Sem `--fqbn`, a placa é **descoberta pela porta**: o `arduino-cli` reconhece um UNO R4 pelo USB, e o sketch é compilado para ele."},
  {"p": "Quando a placa **não** se identifica, a gravação é recusada em vez de chutar. É o caso de uma ponte USB-serial genérica: a CH340 está num clone de UNO e num ESP32 igualmente, e o USB não diz qual chip está atrás dela."},
  { code: `$ dataforge iot carregar firmata --porta=/dev/cu.usbserial-1110
erro: nao sei que placa esta em /dev/cu.usbserial-1110 (ponte CH340 — clone de UNO/Nano, ESP32 ou ESP8266 (1A86:7523)).
  nota: compilar para a placa errada grava um binario que ela nao roda — e o erro, quando aparece, fala do bootloader
  dica: diga o FQBN: --fqbn=esp32:esp32:esp32, --fqbn=arduino:avr:uno, --fqbn=arduino:renesas_uno:unor4wifi

$ dataforge iot carregar firmata --porta=/dev/cu.usbserial-1110 --fqbn=esp32:esp32:esp32:UploadSpeed=115200
gravado.`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "Por que não havia um padrão", "texto": "O padrão era `arduino:avr:uno`. Gravar num UNO R4 sem dizer o FQBN compilava para o UNO clássico e mandava o binário para a placa errada. Uma velocidade que a placa não aguenta vai no próprio FQBN: alguns ESP32 não sobem a 921600 baud, e `UploadSpeed=115200` resolve."}},
  {"callout": {"tipo": "atencao", "titulo": "O arquivo tem o nome da pasta", "texto": "Um `.ino` solto não compila, e o erro do `arduino-cli` não diz por quê. `IoT.gravar_sketch(\"/tmp/fw\", \"firmata\")` cria `/tmp/fw/firmata/firmata.ino` — a pasta e o arquivo com o mesmo nome, que é o que o Arduino exige."}},
  {"callout": {"tipo": "nota", "titulo": "Este firmware NÃO usa a biblioteca Firmata", "texto": "E a razão é concreta. O `Firmata.h` traz um `Boards.h` com a tabela de pinos de cada placa, escrita à mão, e ela para nas placas de até 2018: num **Arduino UNO R4 WiFi** o compilador responde `#error \"Please edit Boards.h with a hardware abstraction for this board\"`, e num **ESP32** também — as duas placas mais vendidas de hoje. Como `IoT.conectar` só fala Firmata, o módulo inteiro era inalcançável nelas."}},
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
  {"p": "Com duas placas na mesa — um UNO R4 e um ESP32 —, a saída de verdade:"},
  { code: `$ dataforge iot doctor
  ✓ portas seriais           /dev/cu.usbmodemC04E301234D42, /dev/cu.usbserial-1110
  ✓ arduino-cli              instalado
  ✓ placas reconhecidas      Arduino UNO R4 WiFi (arduino:renesas_uno:unor4wifi) em /dev/cu.usbmodemC04E301234D42,
                             ponte CH340 — clone de UNO/Nano, ESP32 ou ESP8266 (1A86:7523) em /dev/cu.usbserial-1110
  ✓ Firmata                  /dev/cu.usbmodemC04E301234D42: Arduino UNO R4 WiFi, DataForge v2.5, 20 pinos
  ✓ Firmata                  /dev/cu.usbserial-1110: ESP32, DataForge v2.5, 40 pinos`, lang: 'bash' },
  {"p": "As duas últimas linhas mostram o que o USB não mostra: a ponte CH340 não diz que chip está atrás dela, mas o **firmware** diz — `ESP32`. O `doctor` confere **cada** placa, e não só a primeira."},
  {"p": "Quando uma linha falha, as causas são sempre as mesmas:"},
  {"list": ["**nenhuma porta:** o cabo é só de energia, ou falta o driver (CH340, CP2102) do clone;", "**Firmata não responde:** o firmware não está gravado — `dataforge iot carregar firmata --porta=…`;", "**a porta abre e fica muda:** o monitor serial da IDE está com ela aberta. Duas coisas não abrem a mesma porta, e nada na tela explica isso."]},
  {"h2": "4. Duas placas: diga qual"},
  {"p": "Com mais de uma placa, `IoT.conectar()` sem argumento **recusa** — adivinhar qual placa recebe o comando é o tipo de conveniência que liga o relé errado. A mensagem lista as portas que existem, com o que se sabe de cada uma:"},
  { code: `erro[DF0201]: ha 2 placas conectadas: /dev/cu.usbmodemC04E301234D42, /dev/cu.usbserial-1110.
  = dica: diga qual — pelo caminho, ou pelo nome da placa (IoT.conectar("uno r4")):
          IoT.conectar("/dev/cu.usbserial-1110")   // ponte CH340 — clone de UNO/Nano, ESP32 ou ESP8266 (1A86:7523)
          IoT.conectar("/dev/cu.usbmodemC04E301234D42")   // Arduino UNO R4 WiFi`, lang: 'text' },
  {"p": "O **nome** funciona quando o `arduino-cli` reconhece a placa pelo USB — `IoT.conectar(\"uno r4\")` acha o R4 sem que se saiba o caminho. Uma ponte genérica não revela o chip, e aí a busca pelo nome é recusada com a lista acima, em vez de chutar."},
  {"h2": "5. Ler um analógico sem cair na armadilha"},
  {"p": "A placa só envia uma leitura analógica depois que alguém pede (`relatar_analogico`). Sem o pedido, `analogico(0)` devolve **zero** — um zero com cara de leitura. `ler_analogico` declara o modo, liga o envio e só volta quando uma amostra de verdade chegou:"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.simulador.definir_analogico(0, 512)

assert placa.analogico(0) is 0          // ninguém pediu: zero, calado
assert placa.ler_analogico(0) is 512    // pede, espera e devolve
assert placa.pino_do_canal(0) is 14     // o A0 de um UNO — num ESP32, o GPIO 36
placa.fechar()`, lang: 'df' },
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

const headings = [{ id: '1-ver-se-o-computador-enxerga-a-placa', text: "1. Ver se o computador enxerga a placa", level: 2 as const }, { id: '2-gravar-o-firmware', text: "2. Gravar o firmware", level: 2 as const }, { id: '3-piscar', text: "3. Piscar", level: 2 as const }, { id: 'quando-nao-funciona-o-doctor', text: "Quando não funciona: o doctor", level: 2 as const }, { id: '4-duas-placas-diga-qual', text: "4. Duas placas: diga qual", level: 2 as const }, { id: '5-ler-um-analogico-sem-cair-na-armadilha', text: "5. Ler um analógico sem cair na armadilha", level: 2 as const }, { id: 'a-velocidade-tem-de-ser-a-do-sketch', text: "A velocidade tem de ser a do sketch", level: 2 as const }];

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
