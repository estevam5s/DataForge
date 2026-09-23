// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/iot.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.IoT",
  description: "Arduino e ESP32: Firmata pelo cabo, sketch gerado e gravado, sensores, MQTT — e um simulador de placa para testar sem hardware.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (28)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Mqtt(host='localhost', porta=1883, cliente='', usuario='', senha='', keepalive=60, testamento=None, prazo=10.0)`"], ["`Placa(transporte, nome='placa', prazo=5.0)`"], ["`Simulador(modelo='uno', versao=(2, 5))`"], ["`abrir_serial(porta, velocidade=115200, prazo=1.0)`"], ["`carregar(caminho, porta=None, fqbn='arduino:avr:uno')`"], ["`compilar(caminho, fqbn='arduino:avr:uno')`"], ["`conectar(porta=None, velocidade=57600, prazo=5.0, reiniciar=True)`"], ["`conectar_simulada(modelo='uno', prazo=2.0)`"], ["`divisor(leitura, resistor=10000.0, bits=10)`"], ["`doctor(porta=None)`"], ["`escala(valor, de_min, de_max, para_min, para_max, limitar=True)`"], ["`gravar_sketch(pasta, modelo='pisca', opcoes=None, fqbn='arduino:avr:uno')`"], ["`histerese(ligar, desligar)`"], ["`media_movel(tamanho=8)`"], ["`modelos()`"], ["`modos()`"], ["`monitorar(porta=None, velocidade=115200, linhas=10, prazo=10.0)`"], ["`mqtt(host='localhost', porta=1883, cliente='', usuario='', senha='', keepalive=60, testamento=None, prazo=10.0)`"], ["`ntc(leitura, resistor=10000.0, beta=3950.0, nominal=10000.0, temperatura_nominal=25.0, bits=10)`"], ["`nucleos()`"], ["`placas()`"], ["`portas()`"], ["`simulador(modelo='uno')`"], ["`sketch(modelo='pisca', opcoes=None, fqbn='arduino:avr:uno')`"], ["`sketches()`"], ["`tem_arduino_cli()`"], ["`tensao(leitura, referencia=5.0, bits=10)`"], ["`tmp36(leitura, referencia=5.0, bits=10)`"]]}},
];

const headings = [{ id: 'funcoes-28', text: "Funções (28)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.IoT"}
      description={"Arduino e ESP32: Firmata pelo cabo, sketch gerado e gravado, sensores, MQTT — e um simulador de placa para testar sem hardware."}
      href={"/docs/biblioteca/iot"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
