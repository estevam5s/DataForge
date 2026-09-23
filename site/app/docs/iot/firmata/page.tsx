// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Firmata: a placa como periférico",
  description: "O protocolo, os doze modos de pino, o relatório periódico — e o erro nº 1 de quem começa.",
};

const blocos: Bloco[] = [
  {"p": "Com o firmware gravado, a placa deixa de ter um programa e passa a ter um **protocolo**: ela obedece. Quem decide é o computador, e isso muda o ciclo de trabalho por inteiro."},
  {"table": {"head": ["Sem Firmata", "Com Firmata"], "rows": [["escrever C++, compilar, gravar, testar", "chamar `placa.escrever(13, yes)` e ver o LED"], ["~20 s a cada tentativa", "milissegundos"], ["depurar por `Serial.println`", "depurar com `dataforge debug`"]]}},
  {"h2": "Todo pino tem um modo, e ele é declarado"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")

placa.modo(13, "saida")          // LED, relé
placa.modo(2, "entrada_pullup")  // botão, sem resistor externo
placa.modo(9, "pwm")             // brilho, velocidade
placa.modo(3, "servo")           // posição
placa.modo(14, "analogico")      // A0 — sensor

assert "pwm" in IoT.modos()      // a lista dos doze
placa.fechar()`, lang: 'df', title: `os modos mais usados` },
  { code: `adopt Arcane.IoT as IoT

out IoT.modos()
assert len(IoT.modos()) is 12`, lang: 'df' },
  {"p": "Declarar o modo por conta própria seria conveniente e **errado**: um pino em `saida` recebendo PWM acende no talo, e quem lê o programa não veria onde o modo mudou. Por isso `pwm` e `servo` exigem o modo já declarado:"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
monitor:
    placa.pwm(9, 128)                 // sem o modo
handle Error as e:
    out e.message                     // …precisa do modo declarado
placa.modo(9, "pwm")
assert placa.pwm(9, 128) is 128
placa.fechar()`, lang: 'df' },
  {"h2": "O erro nº 1: ler analógico sem pedir o relatório"},
  {"p": "A placa **não responde perguntas** sobre o analógico: ela envia sozinha, de tempos em tempos, os canais que você mandou relatar. Sem `relatar_analogico`, o pino está certo, o sensor está certo, e a leitura é zero — sem nenhum erro."},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.simulador.definir_analogico(0, 900)   // o sensor "vale" 900
sleep(100)
assert placa.analogico(0) is 0              // e chega ZERO

placa.relatar_analogico(0)                  // é esta linha que falta
sleep(120)
assert placa.analogico(0) is 900
placa.fechar()`, lang: 'df' },
  {"h2": "A amostragem é uma troca"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
assert placa.amostragem(50) is 50       // de 10 a 10000 ms; o padrão é 19
placa.fechar()`, lang: 'df' },
  {"list": ["**Baixa demais** enche a serial de mensagens e **atrasa as ordens que você manda** — o LED demora a responder ao clique.", "**Alta demais** faz o gráfico perder detalhe, e um botão lido por relatório parecer que \"não pegou\".", "Para um sensor de temperatura, 500 ms é generoso. Para um potenciômetro que move um servo, 20 ms."]},
  {"h2": "Reagir, em vez de perguntar"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
vistos := []
placa.observar(lambda e: vistos.append(e["tipo"]))

placa.modo(2, "entrada_pullup")
placa.simulador.definir_digital(2, 1)
sleep(120)
placa.simulador.definir_digital(2, 0)
sleep(120)

assert "digital" in vistos
placa.fechar()`, lang: 'df' },
  {"h2": "O sketch também fala"},
  {"p": "`Firmata.sendString(\"…\")` no C++ chega aqui como texto — é o `println` de quem usa Firmata:"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.simulador.mandar_texto("calibração concluída — ção, á, ê")
sleep(120)
assert "calibração" in placa.textos()[0]
placa.fechar()`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Por que o acento importa aqui", "texto": "No Firmata todo byte de dado viaja partido em dois de **sete bits** — o oitavo marca comando. Ler só o primeiro de cada par funciona em ASCII, porque ali o bit 7 é zero; num acento, \"olá\" vira \"olC!\". O defeito fica escondido até a primeira mensagem em português, e foi exatamente assim que ele apareceu aqui."}},
  {"h2": "Fechar desliga as saídas"},
  { code: `adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")
placa.escrever(13, yes)
placa.fechar()
assert placa.simulador.pino(13) is 0        // apagou ao sair`, lang: 'df' },
  {"p": "Um programa que termina deixando um relé ligado é o defeito mais caro desta área: o resto do sistema continua, sem ninguém olhando. `fechar` é idempotente — chamá-lo num `defer` e de novo no fim não é erro."},
];

const headings = [{ id: 'todo-pino-tem-um-modo-e-ele-e-declarado', text: "Todo pino tem um modo, e ele é declarado", level: 2 as const }, { id: 'o-erro-n-1-ler-analogico-sem-pedir-o-relatorio', text: "O erro nº 1: ler analógico sem pedir o relatório", level: 2 as const }, { id: 'a-amostragem-e-uma-troca', text: "A amostragem é uma troca", level: 2 as const }, { id: 'reagir-em-vez-de-perguntar', text: "Reagir, em vez de perguntar", level: 2 as const }, { id: 'o-sketch-tambem-fala', text: "O sketch também fala", level: 2 as const }, { id: 'fechar-desliga-as-saidas', text: "Fechar desliga as saídas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Firmata: a placa como periférico"}
      description={"O protocolo, os doze modos de pino, o relatório periódico — e o erro nº 1 de quem começa."}
      href={"/docs/iot/firmata"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
