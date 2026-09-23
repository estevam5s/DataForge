# 397 — lê, decide, age

Uma estufa é o projeto de IoT completo mais simples que existe: ela
**lê** (temperatura e umidade de solo), **decide** (com histerese) e
**age** (aquecedor e bomba). Todo problema da área aparece nela.

## As cinco decisões que o programa carrega

| Decisão | O que ela evita |
|---|---|
| `defer` no topo | terminar — inclusive por erro — com a bomba ligada |
| média móvel antes da histerese | o ruído do ADC decidir por conta própria |
| duas soleiras, não uma | o relé batendo dezenas de vezes por minuto |
| a leitura vira `record` | `estado["aquecndo"]` num vault é `void`, e `void` é falso |
| a decisão numa ação, longe do hardware | não dá para testar controle que só existe dentro do laço da placa |

## O teto duro que a histerese não dá

Histerese não protege de um sensor que soltou do vaso: a leitura fica em
"seco" para sempre, e a bomba não desliga nunca. O limite por tempo
(`no máximo 30 s por hora`) é a proteção que importa, e ela é de outra
natureza — não olha o sensor, olha o atuador.

## O que falta para isto virar produção

Sair do Firmata (uma estufa não pode depender do computador ligado),
telemetria (sem histórico não há como saber por que a planta morreu) e
alerta (o testamento do MQTT avisa quando a placa cai).
