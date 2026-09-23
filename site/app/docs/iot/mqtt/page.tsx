// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "MQTT: a placa e o resto do mundo",
  description: "Publicar, assinar, curingas e o testamento — como o painel descobre que o sensor caiu.",
};

const blocos: Bloco[] = [
  {"p": "Um sensor ligado por cabo fala com um computador. Vinte sensores espalhados numa casa falam com um **broker**, e quem quiser ouve. MQTT é esse protocolo: `Arcane.IoT` traz um cliente 3.1.1 falado à mão sobre TCP, sem dependência."},
  { code: `adopt Arcane.IoT as IoT

// precisa de um broker: docker run -p 1883:1883 eclipse-mosquitto
c := IoT.mqtt("localhost", 1883, "sala")
c.publicar("casa/sala/temperatura", "21.5")
c.assinar("casa/+/temperatura", lambda m: out $"{m["topico"]}: {m["mensagem"]}")
sleep(500)
c.fechar()`, lang: 'df', title: `precisa de broker` },
  {"h2": "Os curingas, e onde cada um vale"},
  {"table": {"head": ["Filtro", "Casa", "Não casa"], "rows": [["`casa/sala/luz`", "`casa/sala/luz`", "qualquer outro"], ["`casa/+/luz`", "`casa/sala/luz`, `casa/quarto/luz`", "`casa/sala/piso/luz`"], ["`casa/#`", "`casa/sala/piso/luz`", "`jardim/luz`"]]}},
  {"p": "`+` casa **um** nível; `#` casa o resto, e só no fim do filtro. Publicar num curinga é recusado — eles são de assinatura, e `publicar(\"casa/+/luz\")` criaria um tópico literalmente chamado `+`."},
  {"h2": "O testamento: como se descobre que o sensor caiu"},
  {"p": "Um sensor sem energia não avisa ninguém: ele simplesmente para de publicar, e o painel fica com o último valor congelado na tela — parecendo atual. O *last will* é uma mensagem que **o broker** publica quando a conexão cai:"},
  { code: `adopt Arcane.IoT as IoT

c := IoT.mqtt("localhost", 1883, "estufa", "", "", 60, {
    "topico": "casa/estufa/estado",
    "mensagem": "offline",
    "reter": yes})
c.publicar("casa/estufa/estado", "online", 0, yes)
c.fechar()`, lang: 'df', title: `precisa de broker` },
  {"p": "Com `reter := yes`, quem assinar depois recebe o último valor na hora — é o que faz um painel recém-aberto já mostrar o estado em vez de esperar a próxima leitura."},
  {"h2": "QoS: 0 e 1"},
  {"table": {"head": ["QoS", "Promessa", "Quando"], "rows": [["0", "manda e esquece", "leitura periódica — a próxima chega em 5 s de qualquer forma"], ["1", "chega **pelo menos** uma vez (espera o PUBACK)", "um comando: \"desligar a bomba\""]]}},
  {"p": "Não há QoS 2 aqui, e a razão está escrita: ele exige guardar o estado de quatro mensagens por publicação, e quase nenhum projeto de sensor usa. Com QoS 1, o receptor precisa aguentar **repetição** — um comando \"alternar\" é perigoso, e um \"ligar\" não é."},
  {"h2": "O keepalive não é detalhe"},
  {"p": "Sem PINGREQ, o broker fecha a conexão no silêncio — e o sintoma é um painel que para de atualizar de madrugada, quando nada acontece por muito tempo. O cliente daqui tem uma thread própria para isso, e ela nasce junto com a conexão."},
  {"h2": "Quando o broker recusa"},
  { code: `adopt Arcane.IoT as IoT

monitor:
    IoT.mqtt("127.0.0.1", 1, "x", "", "", 60, void, 1)
handle Error as e:
    out e.message
    out e.dica              // docker run -p 1883:1883 eclipse-mosquitto`, lang: 'df' },
  {"p": "E quando ele responde mas nega, o código volta traduzido: `5` é \"não autorizado\" — o mais comum de todos, e o que mais confunde, porque a conexão TCP funcionou."},
];

const headings = [{ id: 'os-curingas-e-onde-cada-um-vale', text: "Os curingas, e onde cada um vale", level: 2 as const }, { id: 'o-testamento-como-se-descobre-que-o-sensor-caiu', text: "O testamento: como se descobre que o sensor caiu", level: 2 as const }, { id: 'qos-0-e-1', text: "QoS: 0 e 1", level: 2 as const }, { id: 'o-keepalive-nao-e-detalhe', text: "O keepalive não é detalhe", level: 2 as const }, { id: 'quando-o-broker-recusa', text: "Quando o broker recusa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"MQTT: a placa e o resto do mundo"}
      description={"Publicar, assinar, curingas e o testamento — como o painel descobre que o sensor caiu."}
      href={"/docs/iot/mqtt"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
