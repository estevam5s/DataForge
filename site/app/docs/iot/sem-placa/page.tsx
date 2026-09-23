// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar IoT sem placa",
  description: "O simulador que fala o mesmo protocolo — e como um projeto de hardware passa no CI.",
};

const blocos: Bloco[] = [
  {"p": "Código de hardware costuma ser código sem teste, e a razão é sempre a mesma: o teste precisaria da placa, e o CI não tem placa. `IoT.conectar_simulada` resolve isso de um jeito específico — **não** é um dublê da API, é um dispositivo do outro lado do cabo."},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
assert placa.info()["firmware"]["nome"] is "StandardFirmata.ino"
assert placa.info()["protocolo"] is "2.5"
placa.fechar()`, lang: 'df' },
  {"p": "A diferença importa: o simulador recebe os **bytes** do Firmata e responde com os bytes que a placa responderia. O parser, a máquina de estados, a partição em sete bits, o sysex — tudo isso é exercitado. Um dublê que só implementasse `escrever(pino, valor)` não provaria nada sobre o protocolo, que é justamente onde estão os erros."},
  {"h2": "O simulador deixa PERGUNTAR e deixa MENTIR"},
  {"table": {"head": ["Para", "Método"], "rows": [["perguntar o estado de um pino", "`placa.simulador.pino(13)`"], ["perguntar o modo declarado", "`placa.simulador.modo_do_pino(9)`"], ["perguntar a posição de um servo", "`placa.simulador.servo(3)`"], ["fingir um sensor", "`placa.simulador.definir_analogico(0, 733)`"], ["fingir um botão", "`placa.simulador.definir_digital(2, 1)`"], ["fingir um dispositivo I²C", "`placa.simulador.definir_i2c(0x68, 0x3B, […])`"], ["fingir um `Firmata.sendString`", "`placa.simulador.mandar_texto(\"…\")`"]]}},
  {"h2": "Um teste de verdade, com `crucible`"},
  { code: `adopt Arcane.IoT as IoT
adopt Arcane.Crucible as Crucible

crucible "o termostato":

    trial "liga o aquecedor quando esfria":
        placa := IoT.conectar_simulada("uno")
        placa.modo(7, "saida")
        placa.modo(14, "analogico")
        placa.relatar_analogico(0)

        aquecedor := IoT.histerese(18, 21)
        placa.simulador.definir_analogico(0, 300)       // frio
        sleep(120)
        placa.escrever(7, aquecedor(IoT.tmp36(placa.analogico(0))))

        expect placa.simulador.pino(7) is 1
        placa.fechar()

    trial "e nao bate o rele na soleira":
        termostato := IoT.histerese(30, 28)
        expect termostato(31) is yes
        expect termostato(29) is yes
        expect termostato(27) is no

Crucible.run()`, lang: 'df' },
  {"h2": "O que o simulador NÃO prova"},
  {"list": ["**Tempo de subida** de um sinal, ruído de sensor, corrente, queda de tensão.", "**O cabo caindo no meio de um sysex** — o defeito mais chato do mundo real.", "**O bootloader**, o driver USB, o `avrdude`.", "Que o **seu** sensor está ligado nos pinos certos."]},
  {"p": "Por isso `tests/test_iot.py` tem duas provas que o simulador não dá: a camada serial é testada contra um **PTY de verdade** (um dispositivo tty do sistema), e os sketches gerados são compilados pelo **`arduino-cli` de verdade**. E há um teste de hardware que só roda quando alguém aponta uma placa:"},
  { code: `$ DATAFORGE_ARDUINO=/dev/cu.usbmodem1101 python3 -m pytest tests/test_iot.py -k verdade`, lang: 'bash' },
  {"callout": {"tipo": "nota", "titulo": "A honestidade é parte do teste", "texto": "Um teste que finge hardware e se anuncia como prova de hardware é pior que nenhum teste: ele dá confiança sem dar garantia. Cada camada daqui diz contra o que foi conferida — simulador, PTY, arduino-cli, ou placa física — e o que sobra fica escrito como o que sobra."}},
];

const headings = [{ id: 'o-simulador-deixa-perguntar-e-deixa-mentir', text: "O simulador deixa PERGUNTAR e deixa MENTIR", level: 2 as const }, { id: 'um-teste-de-verdade-com-crucible', text: "Um teste de verdade, com `crucible`", level: 2 as const }, { id: 'o-que-o-simulador-nao-prova', text: "O que o simulador NÃO prova", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar IoT sem placa"}
      description={"O simulador que fala o mesmo protocolo — e como um projeto de hardware passa no CI."}
      href={"/docs/iot/sem-placa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
