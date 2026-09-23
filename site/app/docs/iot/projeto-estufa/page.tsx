// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Projeto: a estufa",
  description: "Sensor, relé, histerese, painel e telemetria num programa só — e as decisões que ele carrega.",
};

const blocos: Bloco[] = [
  {"p": "Uma estufa é o projeto de IoT completo mais simples que existe: ela **lê** (temperatura e umidade de solo), **decide** (com histerese) e **age** (aquecedor e bomba). Todo problema desta seção aparece nela."},
  {"h2": "O programa"},
  { code: `adopt Arcane.IoT as IoT

// ── os pinos ────────────────────────────────────────────
TEMPERATURA := 0        // A0 — TMP36
SOLO := 1               // A1 — sensor resistivo
AQUECEDOR := 7          // relé
BOMBA := 8              // relé

action abrir(modelo):
    p := IoT.conectar_simulada(modelo)
    p.modo(AQUECEDOR, "saida")
    p.modo(BOMBA, "saida")
    p.modo(14 + TEMPERATURA, "analogico")
    p.modo(14 + SOLO, "analogico")
    p.relatar_analogico(TEMPERATURA)
    p.relatar_analogico(SOLO)
    p.amostragem(100)
    yield p

record Estado:
    graus: Float
    umidade: Float
    aquecendo: Boolean
    regando: Boolean

action ciclo(placa, suavizar, aquecedor, bomba):
    graus := IoT.tmp36(suavizar(placa.analogico(TEMPERATURA)))
    umidade := IoT.escala(placa.analogico(SOLO), 0, 1023, 0, 100)

    aquecendo := aquecedor(graus)
    regando := bomba(umidade)

    placa.escrever(AQUECEDOR, aquecendo)
    placa.escrever(BOMBA, regando)
    yield Estado(round(graus, 1), round(umidade, 1), aquecendo, regando)

// ── rodar ───────────────────────────────────────────────
placa := abrir("uno")
defer:
    placa.fechar()                       // os dois relés desligam ao sair

suavizar := IoT.media_movel(5)
aquecedor := IoT.histerese(18, 21)       // liga abaixo de 18
bomba := IoT.histerese(30, 45)           // liga abaixo de 30% de umidade

placa.simulador.definir_analogico(TEMPERATURA, 123)   // ~10 °C: frio
placa.simulador.definir_analogico(SOLO, 200)          // seco
sleep(150)

estado := ciclo(placa, suavizar, aquecedor, bomba)
assert estado.aquecendo is yes and estado.regando is yes
out $"{estado.graus} °C · solo {estado.umidade}% · aquecedor {estado.aquecendo} · bomba {estado.regando}"

// aqueceu e molhou
placa.simulador.definir_analogico(TEMPERATURA, 500)
placa.simulador.definir_analogico(SOLO, 700)
sleep(150)
cycle i from 1 to 5:
    estado := ciclo(placa, suavizar, aquecedor, bomba)
    sleep(30)
assert estado.regando is no`, lang: 'df' },
  {"h2": "As cinco decisões que ele carrega"},
  {"table": {"head": ["Decisão", "O que ela evita"], "rows": [["`defer placa.fechar()` no topo", "terminar — inclusive por erro — com a bomba ligada"], ["média móvel antes da histerese", "o ruído do ADC decidir por conta própria"], ["duas soleiras, não uma", "o relé batendo dezenas de vezes por minuto na soleira"], ["a leitura vira `record`", "um vault solto onde `estado[\"aquecendo\"]` com erro de digitação é `void` — e `void` é falso"], ["a decisão em uma ação, longe do hardware", "não dá para testar controle que só existe dentro do laço da placa"]]}},
  {"h2": "E o que falta para isto virar produção"},
  {"list": ["**Sair do Firmata.** Uma estufa não pode depender do computador ligado — a lógica vira sketch, e o computador passa a olhar. Ver *Firmata ou sketch*.", "**Um teto de tempo na bomba.** Histerese não protege de um sensor que soltou do vaso: a leitura fica em \"seco\" para sempre e a bomba não desliga nunca. Um limite duro (`no máximo 30 s por hora`) é a proteção que importa.", "**Telemetria.** Sem histórico, não há como saber por que a planta morreu.", "**Alerta.** `Arcane.Telegram` manda mensagem; o testamento do MQTT avisa quando a placa cai."]},
  { code: `adopt Arcane.IoT as IoT

// o teto duro, que a histerese sozinha nao da
action limitador(maximo_ms):
    gasto := [0]
    acao := lambda ligar, decorrido: (
        gasto[0] + decorrido smaller_eq maximo_ms) and ligar
    yield acao

pode := limitador(30000)
assert pode(yes, 1000) is yes
assert pode(yes, 40000) is no          // passou do teto: nao liga`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que este repositório conseguiu provar", "texto": "Este programa roda a cada execução da suíte, contra o simulador. Os sketches que a estufa usaria foram compilados pelo `arduino-cli` de verdade. O que **não** foi conferido aqui é a estufa física: não há placa ligada nesta máquina. `dataforge iot doctor` e `dataforge iot piscar` são o caminho para conferir isso na sua."}},
];

const headings = [{ id: 'o-programa', text: "O programa", level: 2 as const }, { id: 'as-cinco-decisoes-que-ele-carrega', text: "As cinco decisões que ele carrega", level: 2 as const }, { id: 'e-o-que-falta-para-isto-virar-producao', text: "E o que falta para isto virar produção", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Projeto: a estufa"}
      description={"Sensor, relé, histerese, painel e telemetria num programa só — e as decisões que ele carrega."}
      href={"/docs/iot/projeto-estufa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
