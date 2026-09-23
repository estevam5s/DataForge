// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Receitas de IoT",
  description: "Botão, LDR, ultrassom, potenciômetro, fita de LED, RFID — os pedaços que todo projeto repete.",
};

const blocos: Bloco[] = [
  {"p": "Os blocos que aparecem em quase todo projeto, prontos para colar. Todos rodam contra o simulador."},
  {"h2": "Botão sem resistor externo"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(2, "entrada_pullup")      // o resistor é interno

// com pull-up, o botão LIGA em 0 — ele puxa para o terra
placa.simulador.definir_digital(2, 0)
sleep(100)
apertado := not placa.ler(2)
out $"apertado: {apertado}"
placa.fechar()`, lang: 'df' },
  {"h2": "Debounce: um toque não é um toque"},
  {"p": "O contato de um botão treme por alguns milissegundos e a placa lê dez transições. A correção é temporal, e não elétrica:"},
  { code: `aceitos := []
ultimo := 0 - 200
cycle instante in [0, 5, 12, 300, 305, 700]:
    given instante - ultimo bigger_eq 200:
        aceitos.append(instante)
        ultimo := instante

assert aceitos is [0, 300, 700]      // os tremores sumiram`, lang: 'df' },
  {"h2": "LDR: claro ou escuro"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.relatar_analogico(0)

placa.simulador.definir_analogico(0, 800)
sleep(120)
luz := IoT.escala(placa.analogico(0), 0, 1023, 0, 100)
acender := IoT.histerese(20, 35)          // acende abaixo de 20% de luz

placa.modo(13, "saida")
placa.escrever(13, acender(luz))
assert placa.simulador.pino(13) is 0      // está claro
out $"luz: {round(luz)}%"
placa.fechar()`, lang: 'df' },
  {"h2": "Ultrassom (HC-SR04)"},
  {"p": "O HC-SR04 mede tempo de eco em microssegundos — abaixo do que o Firmata alcança. Esta é a receita que **precisa** de sketch, e ele já existe:"},
  { code: `adopt Arcane.IoT as IoT

codigo := IoT.sketch("ultrassom", {"gatilho": 9, "eco": 10})
assert "pulseIn" in codigo
assert "void loop()" in codigo
out "grave e leia com: dataforge iot monitorar --velocidade=9600"`, lang: 'df' },
  {"h2": "Potenciômetro que move um servo"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.relatar_analogico(0)
placa.modo(3, "servo")
placa.amostragem(20)

placa.simulador.definir_analogico(0, 1023)
sleep(80)
graus := round(IoT.escala(placa.analogico(0), 0, 1023, 0, 180))
placa.servo(3, graus)
assert placa.simulador.servo(3) is 180
placa.fechar()`, lang: 'df' },
  {"h2": "Ler vários canais de uma vez"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
cycle canal from 0 to 3:
    placa.modo(14 + canal, "analogico")
    placa.relatar_analogico(canal)
    placa.simulador.definir_analogico(canal, 100 * (canal + 1))

sleep(150)
leituras := [placa.analogico(c) cycle c in range(0, 4)]
assert leituras is [100, 200, 300, 400]
placa.fechar()`, lang: 'df' },
  {"h2": "Um laço de controle que dá para interromper"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
defer:
    placa.fechar()
placa.modo(13, "saida")

voltas := 0
persist yes:
    voltas += 1
    placa.escrever(13, voltas % 2 is 1)
    sleep(20)
    given voltas bigger_eq 6:
        halt

assert voltas is 6`, lang: 'df' },
  {"p": "Num programa de verdade a condição de parada vem de fora — um arquivo, um sinal, um `Arcane.Inicio.ao_encerrar`. O que **não** pode acontecer é um `persist yes` sem saída controlando um relé: `Ctrl-C` num laço assim deixa o atuador ligado."},
  { code: `adopt Arcane.Inicio as Inicio

desligado := []
Inicio.ao_encerrar(lambda => desligado.append("relés desligados"))
out "o encerramento está registrado"`, lang: 'df' },
];

const headings = [{ id: 'botao-sem-resistor-externo', text: "Botão sem resistor externo", level: 2 as const }, { id: 'debounce-um-toque-nao-e-um-toque', text: "Debounce: um toque não é um toque", level: 2 as const }, { id: 'ldr-claro-ou-escuro', text: "LDR: claro ou escuro", level: 2 as const }, { id: 'ultrassom-hc-sr04', text: "Ultrassom (HC-SR04)", level: 2 as const }, { id: 'potenciometro-que-move-um-servo', text: "Potenciômetro que move um servo", level: 2 as const }, { id: 'ler-varios-canais-de-uma-vez', text: "Ler vários canais de uma vez", level: 2 as const }, { id: 'um-laco-de-controle-que-da-para-interromper', text: "Um laço de controle que dá para interromper", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Receitas de IoT"}
      description={"Botão, LDR, ultrassom, potenciômetro, fita de LED, RFID — os pedaços que todo projeto repete."}
      href={"/docs/iot/receitas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
