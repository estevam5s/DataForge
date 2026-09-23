// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Atuadores: LED, PWM, servo e relé",
  description: "Do LED ao motor — e as três armadilhas elétricas que nenhum código evita.",
};

const blocos: Bloco[] = [
  {"p": "Ler é metade; a outra é **agir**. São quatro formas, e a escolha entre elas é elétrica antes de ser de software."},
  {"h2": "Digital: ligado ou desligado"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")

cycle i from 1 to 3:
    placa.escrever(13, yes)
    sleep(50)
    placa.escrever(13, no)
    sleep(50)

assert placa.simulador.pino(13) is 0
placa.fechar()`, lang: 'df' },
  {"h2": "PWM: o meio-termo que não existe"},
  {"p": "Um pino digital só tem dois valores. \"Meio brilho\" é o pino ligando e desligando rápido o bastante para o olho — ou o motor — não notar. É o PWM, de 0 a 255:"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(9, "pwm")

cycle brilho in [0, 64, 128, 192, 255]:
    placa.pwm(9, brilho)
    sleep(20)

assert placa.simulador.pino(9) is 255

monitor:
    placa.pwm(9, 300)                   // a faixa é 0..255
handle Error as e:
    out e.message
placa.fechar()`, lang: 'df' },
  {"p": "Num UNO, só os pinos **3, 5, 6, 9, 10 e 11** fazem PWM — e é a placa quem diz isso, não uma tabela escrita aqui. Um `modo(13, \"pwm\")` é recusado na hora, com a lista do que aquele pino aceita."},
  {"h2": "Servo: posição, não velocidade"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(3, "servo")

cycle graus in [0, 90, 180, 90]:
    placa.servo(3, graus)
    sleep(30)

assert placa.simulador.servo(3) is 90
placa.fechar()`, lang: 'df' },
  {"p": "Cada servo tem os seus microssegundos de fim de curso. Quando o braço treme numa ponta, é isso — e `configurar_servo` ajusta:"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
assert placa.configurar_servo(3, 600, 2300) is "servo"
placa.servo(3, 0)
placa.fechar()`, lang: 'df' },
  {"h2": "Relé: ligar o que não é de 5 V"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(7, "saida")

action bomba(ligada):
    placa.escrever(7, ligada)
    yield ligada

assert bomba(yes) is yes
sleep(50)
assert bomba(no) is no
placa.fechar()                          // o relé desliga ao sair`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Três armadilhas que o código não evita", "texto": "**Corrente**: um pino de Arduino entrega ~20 mA. Motor, tira de LED e bomba precisam de transistor ou driver — ligados direto, o pino morre. **Lógica invertida**: quase todo módulo de relé chinês liga em `LOW`; o programa fica certo e o comportamento, ao contrário. **Indutivo**: motor e solenoide devolvem um pico ao desligar, e sem o diodo de roda-livre isso reinicia a placa — o sintoma é um travamento \"aleatório\" que só acontece quando o motor para."}},
  {"h2": "Desligar é parte do programa"},
  { code: `adopt Arcane.IoT as IoT

action regar(placa, segundos):
    placa.modo(7, "saida")
    defer:
        placa.escrever(7, no)           // roda mesmo se o corpo falhar
    placa.escrever(7, yes)
    sleep(segundos * 10)
    yield "regado"

placa := IoT.conectar_simulada("uno")
assert regar(placa, 2) is "regado"
assert placa.simulador.pino(7) is 0
placa.fechar()`, lang: 'df' },
  {"p": "O `defer` roda na saída da ação — inclusive quando ela falha no meio. Numa bomba de água, a diferença entre isso e um `escrever(7, no)` no fim do corpo é uma casa alagada."},
];

const headings = [{ id: 'digital-ligado-ou-desligado', text: "Digital: ligado ou desligado", level: 2 as const }, { id: 'pwm-o-meio-termo-que-nao-existe', text: "PWM: o meio-termo que não existe", level: 2 as const }, { id: 'servo-posicao-nao-velocidade', text: "Servo: posição, não velocidade", level: 2 as const }, { id: 'rele-ligar-o-que-nao-e-de-5-v', text: "Relé: ligar o que não é de 5 V", level: 2 as const }, { id: 'desligar-e-parte-do-programa', text: "Desligar é parte do programa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Atuadores: LED, PWM, servo e relé"}
      description={"Do LED ao motor — e as três armadilhas elétricas que nenhum código evita."}
      href={"/docs/iot/atuadores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
