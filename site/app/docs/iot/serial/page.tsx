// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A porta serial, crua",
  description: "Quando não há Firmata do outro lado: abrir, ler linha, escrever, e o pulso de DTR que reinicia a placa.",
};

const blocos: Bloco[] = [
  {"p": "Nem todo dispositivo fala Firmata. Um sketch seu que escreve com `Serial.println`, um módulo GPS, um leitor RFID, uma balança — todos falam **texto numa serial**. `IoT.abrir_serial` é a camada de baixo, e ela é escrita aqui: `termios` no macOS e no Linux, `ctypes` sobre a API do Windows. Sem `pyserial`."},
  { code: `adopt Arcane.IoT as IoT

// com um sketch que faz Serial.begin(9600) e Serial.println(temperatura)
porta := IoT.abrir_serial("/dev/cu.usbmodem1101", 9600, 2.0)
cycle i from 1 to 5:
    linha := porta.linha()
    given linha is not void:
        out linha
porta.fechar()`, lang: 'df', title: `precisa de placa` },
  {"h2": "As quatro operações"},
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`porta.linha()`", "lê até o `\\n`; devolve `void` quando o prazo acaba"], ["`porta.ler(n, prazo)`", "até n bytes; devolve vazio em vez de levantar"], ["`porta.escrever(bytes)`", "devolve quantos foram"], ["`porta.esperando()`", "quantos bytes já chegaram, sem bloquear"], ["`porta.limpar()`", "descarta o que está no buffer — antes de um comando"], ["`porta.reiniciar_placa()`", "o pulso de DTR que a IDE dá ao gravar"]]}},
  {"h2": "Ler não levanta"},
  {"p": "Uma leitura vazia é o estado normal de uma serial: o dispositivo fala quando tem o que dizer. Se isso levantasse, todo laço de leitura precisaria de um `monitor` em volta — e o programa ficaria ilegível para tratar o caso mais comum de todos."},
  {"h2": "O pulso de DTR"},
  {"p": "Abrir a porta de um Arduino UNO **reinicia a placa**: o sinal DTR está ligado ao reset, e é assim que a IDE grava sem apertar botão. Consequência prática: as primeiras linhas depois de abrir costumam ser lixo do boot, e o sketch começa do zero."},
  { code: `adopt Arcane.IoT as IoT

porta := IoT.abrir_serial("/dev/cu.usbmodem1101", 9600, 2.0)
porta.reiniciar_placa()      // começa do zero, de propósito
sleep(2000)                  // o bootloader leva ~1,5 s
porta.limpar()               // e o lixo dele vai embora
out porta.linha()
porta.fechar()`, lang: 'df', title: `precisa de placa` },
  {"h2": "A velocidade é conferida"},
  { code: `adopt Arcane.IoT as IoT

monitor:
    IoT.abrir_serial("/dev/null", 12345)     // não é uma velocidade padrão
handle Error as e:
    out e.message`, lang: 'df' },
  {"p": "Uma velocidade fora da lista é aceita pelo driver em alguns sistemas e produz bytes corrompidos em vez de erro — que é o pior resultado possível, porque parece um problema de fio."},
  {"h2": "Fechar é idempotente, e depois disso a porta recusa"},
  { code: `adopt Arcane.IoT as IoT

monitor:
    porta := IoT.abrir_serial("/dev/nao-existe-mesmo", 115200)
handle Error as e:
    out e.dica              // portas() mostra as que existem agora`, lang: 'df' },
];

const headings = [{ id: 'as-quatro-operacoes', text: "As quatro operações", level: 2 as const }, { id: 'ler-nao-levanta', text: "Ler não levanta", level: 2 as const }, { id: 'o-pulso-de-dtr', text: "O pulso de DTR", level: 2 as const }, { id: 'a-velocidade-e-conferida', text: "A velocidade é conferida", level: 2 as const }, { id: 'fechar-e-idempotente-e-depois-disso-a-porta-recusa', text: "Fechar é idempotente, e depois disso a porta recusa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A porta serial, crua"}
      description={"Quando não há Firmata do outro lado: abrir, ler linha, escrever, e o pulso de DTR que reinicia a placa."}
      href={"/docs/iot/serial"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
