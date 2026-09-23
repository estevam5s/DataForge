// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Firmata ou sketch: a conta",
  description: "Onde a latência do cabo mata o projeto, e onde ela não importa — com números.",
};

const blocos: Bloco[] = [
  {"p": "A pergunta não é qual é melhor: é **onde o programa precisa rodar**. E a resposta sai de uma conta, não de gosto."},
  {"h2": "A latência do cabo"},
  {"p": "Cada ordem do Firmata é uma mensagem de 2 a 4 bytes atravessando a serial, e cada leitura é outra voltando. A 57600 baud, isso é sub-milissegundo no fio — mas o caminho inteiro (escrever, o USB agendar, a placa processar, responder, o driver entregar) fica na casa de **1 a 5 ms** por ida e volta."},
  {"table": {"head": ["O projeto precisa de", "Firmata", "Sketch"], "rows": [["ler um sensor a cada segundo", "✓ perfeito", "exagero"], ["acender LED ao clicar num painel", "✓", "precisaria de protocolo próprio"], ["ler um encoder de motor", "✗ perde pulso", "✓ interrupção"], ["PWM de áudio, LED endereçável (WS2812)", "✗ não dá", "✓"], ["responder a um botão em < 1 ms", "✗", "✓"], ["funcionar sem o computador ligado", "✗ por definição", "✓"], ["rodar a bateria por meses", "✗", "✓ com *deep sleep*"], ["prototipar, calibrar, explorar um sensor novo", "✓ sem comparação", "20 s por tentativa"]]}},
  {"h2": "O meio-termo que quase sempre é a resposta"},
  {"p": "Prototipar com Firmata, e **depois** virar sketch. A calibração de um sensor leva dezenas de tentativas; fazer isso com ciclo de 20 s custa uma tarde, e com Firmata custa minutos. Quando as constantes estiverem certas, elas entram no `.ino`:"},
  { code: `adopt Arcane.IoT as IoT

// 1. descobrir a constante com Firmata, na bancada
placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.relatar_analogico(0)
placa.simulador.definir_analogico(0, 512)
sleep(120)
limiar := placa.analogico(0)
placa.fechar()

// 2. gerar o sketch com ela dentro
codigo := IoT.sketch("sensor", {"canal": 0, "velocidade": 9600})
assert "A0" in codigo
out $"limiar calibrado: {limiar}"`, lang: 'df' },
  {"h2": "E o terceiro caminho"},
  {"p": "Um sketch que publica em MQTT não precisa do computador **nem** de um programa esperando na ponta: ele fala com o broker, e quem quiser escuta. É o desenho de quase toda automação doméstica que funciona, e o modelo `wifi-mqtt` já sai assim."},
  {"callout": {"tipo": "atencao", "titulo": "O erro de arquitetura mais comum", "texto": "Escrever a lógica de controle no computador, por Firmata, e deixá-la controlando algo que não pode parar — uma bomba, um aquecedor, uma trava. Quando o cabo cai ou o computador reinicia, o atuador fica no último estado, para sempre. Controle que **não pode parar** mora na placa; o computador olha e manda ajustes."}},
];

const headings = [{ id: 'a-latencia-do-cabo', text: "A latência do cabo", level: 2 as const }, { id: 'o-meio-termo-que-quase-sempre-e-a-resposta', text: "O meio-termo que quase sempre é a resposta", level: 2 as const }, { id: 'e-o-terceiro-caminho', text: "E o terceiro caminho", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Firmata ou sketch: a conta"}
      description={"Onde a latência do cabo mata o projeto, e onde ela não importa — com números."}
      href={"/docs/iot/quando-usar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
