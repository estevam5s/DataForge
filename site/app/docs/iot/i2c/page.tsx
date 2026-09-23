// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "I²C: dois fios, muitos sensores",
  description: "O barramento que liga BMP280, MPU6050 e display no mesmo par de fios — e por que a leitura pode devolver void.",
};

const blocos: Bloco[] = [
  {"p": "I²C liga vários dispositivos em **dois fios** (SDA e SCL), cada um com um endereço. É como quase todo sensor moderno conversa: acelerômetro, barômetro, RTC, display OLED, expansor de portas."},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.i2c_configurar()

// o MPU6050 no endereço 0x68, registro 0x3B: seis bytes de aceleração
placa.simulador.definir_i2c(0x68, 0x3B, [0, 100, 255, 200, 1, 44])
dados := placa.i2c_ler(0x68, 0x3B, 6, 2)
assert len(dados) is 6

x := dados[0] * 256 + dados[1]
out $"aceleração X (cru): {x}"
placa.fechar()`, lang: 'df' },
  {"h2": "A leitura devolve `void` quando ninguém responde"},
  {"p": "Um endereço errado, um fio solto ou um sensor sem alimentação dão o **mesmo** resultado: silêncio. Levantar aqui obrigaria um `monitor` em volta de cada leitura de um laço que roda mil vezes; devolver `void` deixa o programa decidir:"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.i2c_configurar()

resposta := placa.i2c_ler(0x77, 0xD0, 1, 0.3)   // ninguém nesse endereço
given resposta is void:
    out "nenhum dispositivo respondeu em 0x77 — confira SDA, SCL e o 3,3 V"
otherwise:
    out resposta
placa.fechar()`, lang: 'df' },
  {"h2": "Escrever num registro"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.i2c_configurar()
// acordar o MPU6050: registro 0x6B := 0
assert placa.i2c_escrever(0x68, [0x6B, 0x00]) is 2
placa.fechar()`, lang: 'df' },
  {"h2": "Os três erros de I²C, em ordem de frequência"},
  {"table": {"head": ["Sintoma", "Quase sempre é"], "rows": [["nada responde, em nenhum endereço", "faltam os resistores de *pull-up* (4,7 kΩ) — muitos módulos já os têm, e dois módulos juntos podem ter demais"], ["responde, mas os valores não fazem sentido", "o sensor não foi acordado: quase todos nascem em modo de repouso"], ["funciona perto e falha com fio longo", "I²C é de placa, não de instalação — acima de ~1 m, use um barramento diferencial"]]}},
  {"p": "E o endereço na folha de dados às vezes vem **deslocado**: 0xD0 é 0x68 escrito com o bit de leitura/escrita junto. Se o sensor não responde em nenhum endereço, tente a metade."},
];

const headings = [{ id: 'a-leitura-devolve-void-quando-ninguem-responde', text: "A leitura devolve `void` quando ninguém responde", level: 2 as const }, { id: 'escrever-num-registro', text: "Escrever num registro", level: 2 as const }, { id: 'os-tres-erros-de-ic-em-ordem-de-frequencia', text: "Os três erros de I²C, em ordem de frequência", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"I²C: dois fios, muitos sensores"}
      description={"O barramento que liga BMP280, MPU6050 e display no mesmo par de fios — e por que a leitura pode devolver void."}
      href={"/docs/iot/i2c"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
