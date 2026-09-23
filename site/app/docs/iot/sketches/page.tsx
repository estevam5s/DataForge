// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Sketches: C++ gerado e gravado",
  description: "Seis modelos prontos, o arduino-cli por baixo, e o que a linguagem NÃO faz.",
};

const blocos: Bloco[] = [
  {"p": "Firmata cobre o protótipo. O que precisa rodar **sem computador** — um sensor a bateria, um controle com resposta em microssegundos — é sketch: C++ na placa. A linguagem escreve o sketch e chama o `arduino-cli` para compilar e gravar."},
  { code: `adopt Arcane.IoT as IoT

cycle nome in keys(IoT.sketches()):
    out $"{nome}: {IoT.sketches()[nome]["descricao"]}"
assert len(IoT.sketches()) >= 6`, lang: 'df' },
  {"table": {"head": ["Modelo", "Para quê"], "rows": [["`firmata`", "o firmware do Firmata — é o que torna a placa controlável daqui"], ["`pisca`", "o \"olá mundo\": prova que gravar funcionou"], ["`sensor`", "lê um analógico e escreve na serial, pronto para `iot monitorar`"], ["`ultrassom`", "HC-SR04 — distância em centímetros"], ["`dht`", "DHT11/DHT22 — temperatura e umidade"], ["`wifi-mqtt`", "ESP32 que publica leituras num broker MQTT"]]}},
  {"h2": "As opções entram no código"},
  { code: `adopt Arcane.IoT as IoT

codigo := IoT.sketch("pisca", {"led": 7, "intervalo": 120})
assert "const int LED = 7;" in codigo
assert "void setup()" in codigo and "void loop()" in codigo`, lang: 'df' },
  {"p": "Uma opção que não existe é **recusada**, e não ignorada — `opcoes.ler` de novo. Um `--lde=7` que passa calado grava o sketch com o LED errado, e a pessoa vai procurar o defeito no fio:"},
  { code: `adopt Arcane.IoT as IoT

monitor:
    IoT.sketch("pisca", {"lde": 7})
handle Error as e:
    out e.message`, lang: 'df' },
  {"h2": "Gravar em disco, e depois na placa"},
  { code: `adopt Arcane.IoT as IoT
adopt Arcane.OS as OS
adopt Arcane.IO as IO

pasta := $"{OS.temp_dir()}/df-doc-iot-{randint(100000, 999999)}"
caminho := IoT.gravar_sketch(pasta, "sensor", {"canal": 0, "velocidade": 9600})
assert "sensor.ino" in caminho
assert "Serial.begin(9600)" in IO.read(caminho)
IO.remove_tree(pasta)`, lang: 'df' },
  { code: `$ dataforge iot carregar /tmp/fw/sensor --fqbn=arduino:avr:uno
gravado.

$ dataforge iot compilar /tmp/fw/sensor --fqbn=esp32:esp32:esp32
Sketch uses 265417 bytes (20%) of program storage space.
compilou.`, lang: 'bash' },
  {"h2": "O que a linguagem não faz — e por quê"},
  {"p": "`IoT.compilar` e `IoT.carregar` chamam o `arduino-cli`. Compilar C++ para AVR, resolver bibliotecas e falar com o bootloader é o que ele faz, e bem; reimplementar isso seria refazer o GCC e o avrdude. O projeto prefere **dizer que depende dele** a fingir que não:"},
  { code: `adopt Arcane.IoT as IoT

given IoT.tem_arduino_cli():
    out "dá para compilar e gravar daqui"
otherwise:
    out "instale: brew install arduino-cli"`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Estes sketches compilam de verdade", "texto": "`pisca`, `sensor` e `ultrassom` foram compilados pelo `arduino-cli` para `arduino:renesas_uno:unor4wifi`, e `wifi-mqtt` para `esp32:esp32:esp32`. O teste que faz isso está em `tests/test_iot.py` e só roda com `DATAFORGE_ARDUINO_COMPILAR=1`, porque leva ~40 s — mas ele existe: um gerador de C++ que nunca passou por um compilador é um gerador de texto."}},
];

const headings = [{ id: 'as-opcoes-entram-no-codigo', text: "As opções entram no código", level: 2 as const }, { id: 'gravar-em-disco-e-depois-na-placa', text: "Gravar em disco, e depois na placa", level: 2 as const }, { id: 'o-que-a-linguagem-nao-faz-e-por-que', text: "O que a linguagem não faz — e por quê", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Sketches: C++ gerado e gravado"}
      description={"Seis modelos prontos, o arduino-cli por baixo, e o que a linguagem NÃO faz."}
      href={"/docs/iot/sketches"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
