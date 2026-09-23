// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Quando não funciona",
  description: "Os quinze sintomas de hardware, cada um com a causa que quase sempre é.",
};

const blocos: Bloco[] = [
  {"p": "Depurar hardware é diferente de depurar software: a maioria dos sintomas **não dá erro**. Esta é a lista, na ordem em que os problemas aparecem."},
  {"h2": "A placa não aparece"},
  {"table": {"head": ["Sintoma", "Quase sempre é"], "rows": [["`iot portas` não mostra nada", "o cabo é só de energia — é a causa nº 1, e não parece"], ["some e volta sozinha", "cabo ruim ou hub USB sem alimentação"], ["aparece no Windows como \"dispositivo desconhecido\"", "falta o driver CH340/CP2102 do clone"], ["não aparece dentro do contêiner", "falta `--device=/dev/ttyACM0` no `docker run`"]]}},
  {"h2": "A porta abre e nada chega"},
  {"table": {"head": ["Sintoma", "Quase sempre é"], "rows": [["`conectar` dá prazo esgotado", "o StandardFirmata não está gravado"], ["texto ilegível no monitor", "a velocidade não é a do `Serial.begin()` do sketch"], ["\"permissão negada\" ou \"porta ocupada\"", "o monitor serial da IDE está aberto — duas coisas não abrem a mesma porta"], ["no Linux, permissão negada sempre", "o usuário não está no grupo `dialout`: `sudo usermod -aG dialout $USER`"], ["as primeiras linhas são lixo", "abrir a porta reinicia a placa; espere ~2 s e `limpar()`"]]}},
  {"h2": "Responde, mas errado"},
  {"table": {"head": ["Sintoma", "Quase sempre é"], "rows": [["analógico sempre 0", "faltou `relatar_analogico(canal)` — é o erro nº 1 do Firmata"], ["analógico sempre 1023", "o pino está solto: uma entrada sem nada ligada flutua"], ["o botão \"não pega\"", "amostragem alta demais, ou falta o pull-up"], ["temperatura absurda (−273, 500)", "termistor no fim da escala: fio solto ou curto"], ["o valor treme muito", "ruído do ADC — média móvel resolve"]]}},
  {"h2": "Age, mas errado"},
  {"table": {"head": ["Sintoma", "Quase sempre é"], "rows": [["o relé liga quando devia desligar", "módulo de relé com lógica invertida (ativo em `LOW`)"], ["o LED acende no talo com PWM baixo", "o pino está em `saida`, não em `pwm`"], ["o servo treme numa ponta", "os microssegundos de fim de curso — `configurar_servo`"], ["a placa reinicia quando o motor para", "falta o diodo de roda-livre; o pico indutivo derruba a alimentação"], ["o pino parou de funcionar", "corrente: um pino entrega ~20 mA, e motor/fita de LED precisam de driver"]]}},
  {"h2": "O diagnóstico, em ordem"},
  { code: `$ dataforge iot doctor --porta=/dev/cu.usbmodem1101`, lang: 'bash' },
  {"p": "Ele confere, nesta ordem: a porta existe → a porta abre → alguém responde Firmata → o `arduino-cli` está instalado. A ordem é a das causas, e a primeira falha é a que interessa — as de baixo são consequência."},
  {"h2": "Quando o problema não é o seu código"},
  { code: `adopt Arcane.IoT as IoT

// a prova mais barata: o caminho inteiro, contra um simulador
placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")
placa.escrever(13, yes)
assert placa.simulador.pino(13) is 1
placa.fechar()
out "o programa está certo — o que falta é do lado do fio"`, lang: 'df' },
  {"p": "Rodar a mesma lógica contra o simulador separa as duas metades em segundos. Se ela funciona ali e não na placa, o problema é elétrico, é o sketch ou é a porta — e nenhuma releitura do código vai achá-lo."},
];

const headings = [{ id: 'a-placa-nao-aparece', text: "A placa não aparece", level: 2 as const }, { id: 'a-porta-abre-e-nada-chega', text: "A porta abre e nada chega", level: 2 as const }, { id: 'responde-mas-errado', text: "Responde, mas errado", level: 2 as const }, { id: 'age-mas-errado', text: "Age, mas errado", level: 2 as const }, { id: 'o-diagnostico-em-ordem', text: "O diagnóstico, em ordem", level: 2 as const }, { id: 'quando-o-problema-nao-e-o-seu-codigo', text: "Quando o problema não é o seu código", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Quando não funciona"}
      description={"Os quinze sintomas de hardware, cada um com a causa que quase sempre é."}
      href={"/docs/iot/solucao-de-problemas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
