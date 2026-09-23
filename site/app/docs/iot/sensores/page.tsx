// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Sensores: do número cru ao valor",
  description: "escala, tensão, TMP36, NTC, divisor, média móvel e histerese — a matemática que todo projeto reescreve errado.",
};

const blocos: Bloco[] = [
  {"p": "Um pino analógico devolve um número de 0 a 1023. Ele não é temperatura, nem luz, nem umidade: é o quanto da tensão de referência chegou ali. Transformar isso em grandeza é a parte que todo projeto refaz — e onde os mesmos quatro erros acontecem."},
  {"h2": "escala — o `map` que limita"},
  { code: `adopt Arcane.IoT as IoT

assert IoT.escala(512, 0, 1023, 0, 100) > 50.0 and IoT.escala(512, 0, 1023, 0, 100) < 50.1
assert IoT.escala(2000, 0, 1023, 0, 100) is 100     // limita, por padrão
assert IoT.escala(-5, 0, 1023, 0, 100) is 0
assert IoT.escala(2000, 0, 1023, 0, 100, no) > 100  // sem limitar, extrapola`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O `map()` do Arduino não limita", "texto": "Ruído faz um ADC de 10 bits devolver 1024 de vez em quando. Com o `map` do C, isso vira 101% num painel — e num controle de motor vira um valor fora da faixa do PWM. Aqui o padrão é limitar, e `limitar := no` é escolha explícita de quem quer extrapolar."}},
  {"h2": "tensão — a conta que depende da placa"},
  { code: `adopt Arcane.IoT as IoT

assert IoT.tensao(1023) is 5.0                       // UNO
assert round(IoT.tensao(2048, 3.3, 12), 2) is 1.65   // ESP32: 12 bits`, lang: 'df' },
  {"h2": "TMP36 — o sensor de três pernas"},
  {"p": "A folha de dados diz: 750 mV a 25 °C, 10 mV por grau. É uma reta, e a conta é uma linha — mas o deslocamento de 500 mV é o que quase todo mundo esquece:"},
  { code: `adopt Arcane.IoT as IoT

leitura := 0.75 / 5.0 * 1023            // 750 mV num ADC de 10 bits
temperatura := IoT.tmp36(leitura)
assert temperatura > 24.5 and temperatura < 25.5
out $"{round(temperatura, 1)} °C"`, lang: 'df' },
  {"h2": "NTC — o termistor, e a equação B"},
  { code: `adopt Arcane.IoT as IoT

// com o termistor na resistência nominal, o divisor lê a metade da escala
t := IoT.ntc(1023 / 2)
assert t > 24.7 and t < 25.3

// e a ponta da escala não é temperatura: é fio solto ou curto
monitor:
    IoT.ntc(0)
handle Error as e:
    out e.message                       // …ponta da escala…`, lang: 'df' },
  {"p": "Recusar as pontas é o ponto: com a leitura em 0 ou 1023 a equação divide por zero ou tira log de zero, e o que sai é um número absurdo com cara de temperatura. Um termostato que vê −273 °C liga o aquecedor e não desliga mais."},
  {"h2": "divisor — quando o sensor é uma resistência"},
  { code: `adopt Arcane.IoT as IoT

// LDR, sensor de umidade de solo, potenciômetro: tudo vira resistência
r := IoT.divisor(1023 / 2)
assert r > 9900 and r < 10100
out $"{round(r)} Ω"`, lang: 'df' },
  {"h2": "média móvel — o ruído do ADC"},
  {"p": "Uma leitura pura treme: 512, 509, 514, 511. Num gráfico isso é grama; num controle, é o relé batendo. A média móvel é a resposta mais barata, e ela **esquece**:"},
  { code: `adopt Arcane.IoT as IoT

media := IoT.media_movel(3)
assert media(10) is 10
assert media(20) is 15
assert media(30) is 20
assert media(40) is 30          // o 10 saiu da janela`, lang: 'df' },
  {"h2": "histerese — o relé que não bate"},
  {"p": "Ligar acima de 30 e desligar abaixo de 30 faz o relé chavear dezenas de vezes por minuto quando a temperatura fica **em** 30 — e é assim que um contato se queima. A saída é ter **duas** soleiras:"},
  { code: `adopt Arcane.IoT as IoT

ventoinha := IoT.histerese(30, 28)      // liga em 30, só desliga em 28
assert ventoinha(29) is no              // subindo, ainda não
assert ventoinha(31) is yes
assert ventoinha(29) is yes             // no meio, segura o estado
assert ventoinha(27) is no`, lang: 'df' },
  {"p": "Invertendo as duas, ela liga **abaixo** — é o umidificador, o aquecedor, a bomba:"},
  { code: `adopt Arcane.IoT as IoT

umidificador := IoT.histerese(40, 50)   // liga abaixo de 40
assert umidificador(45) is no
assert umidificador(35) is yes
assert umidificador(45) is yes
assert umidificador(55) is no`, lang: 'df' },
  { code: `adopt Arcane.IoT as IoT

monitor:
    IoT.histerese(30, 30)               // duas soleiras iguais são uma só
handle Error as e:
    out e.message`, lang: 'df' },
  {"h2": "Os quatro juntos, num sensor de verdade"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.relatar_analogico(0)
placa.amostragem(20)

suavizar := IoT.media_movel(5)
aquecedor := IoT.histerese(18, 21)      // liga abaixo de 18, desliga em 21
placa.modo(7, "saida")

placa.simulador.definir_analogico(0, 123)       // ~10 °C
sleep(120)
graus := IoT.tmp36(suavizar(placa.analogico(0)))
ligado := aquecedor(graus)
placa.escrever(7, ligado)

out $"{round(graus, 1)} °C — aquecedor {"ligado" given ligado otherwise "desligado"}"
assert ligado is yes
placa.fechar()`, lang: 'df' },
];

const headings = [{ id: 'escala-o-map-que-limita', text: "escala — o `map` que limita", level: 2 as const }, { id: 'tensao-a-conta-que-depende-da-placa', text: "tensão — a conta que depende da placa", level: 2 as const }, { id: 'tmp36-o-sensor-de-tres-pernas', text: "TMP36 — o sensor de três pernas", level: 2 as const }, { id: 'ntc-o-termistor-e-a-equacao-b', text: "NTC — o termistor, e a equação B", level: 2 as const }, { id: 'divisor-quando-o-sensor-e-uma-resistencia', text: "divisor — quando o sensor é uma resistência", level: 2 as const }, { id: 'media-movel-o-ruido-do-adc', text: "média móvel — o ruído do ADC", level: 2 as const }, { id: 'histerese-o-rele-que-nao-bate', text: "histerese — o relé que não bate", level: 2 as const }, { id: 'os-quatro-juntos-num-sensor-de-verdade', text: "Os quatro juntos, num sensor de verdade", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Sensores: do número cru ao valor"}
      description={"escala, tensão, TMP36, NTC, divisor, média móvel e histerese — a matemática que todo projeto reescreve errado."}
      href={"/docs/iot/sensores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
