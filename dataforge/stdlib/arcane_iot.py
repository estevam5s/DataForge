# -*- coding: utf-8 -*-
"""
Arcane.IoT — Arduino, ESP32 e o que estiver do outro lado do cabo.

    adopt Arcane.IoT as IoT

    placa := IoT.conectar(IoT.portas()[0]["porta"])
    placa.modo(13, "saida")
    placa.escrever(13, yes)                  // o LED acende

    placa.modo(14, "analogico")               // A0
    placa.relatar_analogico(0)
    out IoT.escala(placa.analogico(0), 0, 1023, 0, 100)
    placa.fechar()

São **dois** caminhos, e a diferença entre eles decide o projeto:

| Caminho | Quem decide | Serve para |
|---|---|---|
| **Firmata** (este módulo fala) | o computador, por cabo | prototipar, ler sensor, painel, automação de mesa |
| **sketch** (este módulo gera, compila e grava) | a placa, sozinha | o que precisa rodar sem computador, ou com microssegundos |

Nada aqui é dependência: a porta serial é `termios`/`ctypes` escrito à
mão (`iot_serial.py`), o protocolo é o Firmata 2.x (`iot_firmata.py`) e
o MQTT é o 3.1.1 falado à mão (`iot_mqtt.py`). O `arduino-cli` é a
**única** peça externa, e só para compilar e gravar — porque compilar
C++ para AVR não é coisa que se reimplemente, e dizer o contrário seria
mentira. Sem ele, tudo o que é Firmata continua funcionando.

O `Simulador` é uma placa de mentira que fala Firmata de verdade: é o
que torna executável cada exemplo de `/docs/iot` e o que deixa os testes
rodarem no CI. O que ele não simula está dito em `iot_simulador.py`.
"""

import json
import os
import shutil
import subprocess
import time

from ..errors import RuntimeError_
from . import iot_serial
from .iot_firmata import MODOS, Placa
from .iot_simulador import MODELOS, Simulador

_DOC = "iot"


def _erro(mensagem, nota="", dica=""):
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


# ═══════════════════════════════════════════════════════════
#  Conectar
# ═══════════════════════════════════════════════════════════

#: A velocidade do StandardFirmata. Ele fixa 57600 no `setup()`, e o
#: número mais comum em exemplo de Arduino — 9600 — não conversa com
#: ele: a porta abre, e nada do que chega faz sentido.
VELOCIDADE_FIRMATA = 57600


def conectar(porta=None, velocidade=VELOCIDADE_FIRMATA, prazo=5.0,
             reiniciar=True):
    """Abre a porta e apresenta a placa. Devolve a `Placa`.

    Com `porta` vazia, escolhe a única que existir — e **recusa** quando
    há duas: adivinhar qual placa receber um comando é o tipo de
    conveniência que liga o relé errado.
    """
    alvo = str(porta) if porta else _unica_porta()
    serial = iot_serial.abrir(alvo, velocidade, prazo=0.4)
    if reiniciar:
        # O autorreset acontece na abertura em quase toda placa, e o
        # bootloader leva ~1,5 s para sair do caminho. Falar antes disso
        # é falar com o bootloader, que não entende Firmata.
        serial.reiniciar_placa()
        time.sleep(1.6)
        serial.limpar()
    placa = Placa(serial, nome=os.path.basename(alvo), prazo=prazo)
    try:
        placa.apresentar()
    except Exception:
        placa.fechar()
        raise
    return placa


def _unica_porta():
    achadas = portas()
    if not achadas:
        raise _erro(
            "nao ha nenhuma placa conectada.",
            nota="procurei por portas USB-serial e nao achei nenhuma",
            dica="confira o cabo (muitos cabos sao SO de energia) e rode "
                 "'dataforge iot portas'")
    if len(achadas) > 1:
        nomes = ", ".join(p["porta"] for p in achadas)
        raise _erro(
            f"ha {len(achadas)} placas conectadas: {nomes}.",
            nota="adivinhar qual delas recebe o comando e o tipo de "
                 "conveniencia que liga o rele errado",
            dica='IoT.conectar("/dev/cu.usbmodem1101")')
    return achadas[0]["porta"]


def portas():
    """As portas seriais visíveis, sem abrir nenhuma."""
    return iot_serial.portas()


def simulador(modelo="uno"):
    """Uma placa de mentira que fala Firmata de verdade."""
    return Simulador(modelo)


def conectar_simulada(modelo="uno", prazo=2.0):
    """Um atalho: o simulador já apresentado, pronto para usar."""
    sim = Simulador(modelo)
    placa = Placa(sim, nome=f"simulada-{modelo}", prazo=prazo)
    placa.apresentar()
    # O simulador fica alcançável para quem testa: `placa.simulador`.
    placa.simulador = sim
    return placa


def modelos():
    """As placas que o simulador conhece, com o mapa de pinos."""
    return {nome: dict(dados) for nome, dados in sorted(MODELOS.items())}


def modos():
    """Os modos de pino que o Firmata define."""
    return sorted(MODOS)


# ═══════════════════════════════════════════════════════════
#  Converter o que o sensor devolve
# ═══════════════════════════════════════════════════════════

def escala(valor, de_min, de_max, para_min, para_max, limitar=True):
    """O `map()` do Arduino, com uma diferença: ele LIMITA por padrão.

    O `map` do C não limita, e um sensor que devolve 1024 por um
    instante vira 101% num painel — o tipo de número que ninguém
    percebe até alguém tomar uma decisão com ele.
    """
    de_min, de_max = float(de_min), float(de_max)
    if de_max == de_min:
        raise _erro("a faixa de origem tem largura zero.",
                    dica="escala(v, 0, 1023, 0, 100)")
    fracao = (float(valor) - de_min) / (de_max - de_min)
    if limitar:
        fracao = max(0.0, min(1.0, fracao))
    return float(para_min) + fracao * (float(para_max) - float(para_min))


def tensao(leitura, referencia=5.0, bits=10):
    """A leitura analógica em volts. Um ESP32 lê 12 bits e 3,3 V."""
    maximo = (1 << int(bits)) - 1
    return float(leitura) / maximo * float(referencia)


def tmp36(leitura, referencia=5.0, bits=10):
    """Graus Celsius de um TMP36: 10 mV por grau, com 500 mV de deslocamento."""
    return (tensao(leitura, referencia, bits) - 0.5) * 100.0


def ntc(leitura, resistor=10000.0, beta=3950.0, nominal=10000.0,
        temperatura_nominal=25.0, bits=10):
    """Graus Celsius de um termistor NTC pela equação B."""
    import math
    maximo = (1 << int(bits)) - 1
    valor = float(leitura)
    if valor <= 0 or valor >= maximo:
        raise _erro(
            f"a leitura {int(valor)} esta na ponta da escala.",
            nota="0 ou o maximo querem dizer curto ou circuito aberto — o "
                 "termistor ficaria com resistencia zero ou infinita",
            dica="confira o divisor de tensao e o resistor de 10k")
    resistencia = float(resistor) * valor / (maximo - valor)
    inverso = (1.0 / (float(temperatura_nominal) + 273.15)
               + math.log(resistencia / float(nominal)) / float(beta))
    return 1.0 / inverso - 273.15


def divisor(leitura, resistor=10000.0, bits=10):
    """A resistência do sensor num divisor de tensão — LDR, NTC, FSR."""
    maximo = (1 << int(bits)) - 1
    if float(leitura) <= 0:
        raise _erro("leitura zero: o divisor esta em curto, ou o pino errado.")
    return float(resistor) * (maximo / float(leitura) - 1.0)


def media_movel(tamanho=8):
    """Um suavizador: devolve a ação que recebe a leitura e dá a média.

    Leitura analógica treme — o último bit oscila sozinho. Mostrar o
    valor cru num painel faz o número dançar; a média das últimas N
    leituras é o que se vê em todo projeto que funciona.
    """
    tamanho = max(1, int(tamanho))
    janela = []

    def somar(valor):
        janela.append(float(valor))
        if len(janela) > tamanho:
            del janela[0]
        return sum(janela) / len(janela)

    return somar


def histerese(ligar, desligar):
    """Um gatilho com duas soleiras — a que liga e a que desliga.

    Com uma soleira só, um valor tremendo em volta dela liga e desliga o
    relé dezenas de vezes por segundo. Duas soleiras separadas é o que
    todo termostato faz.
    """
    if float(ligar) == float(desligar):
        raise _erro("as duas soleiras sao iguais: isso e uma soleira so.",
                    dica="histerese(30, 28) liga aos 30 e desliga aos 28")
    subindo = float(ligar) > float(desligar)
    estado = {"ligado": False}

    def decidir(valor):
        v = float(valor)
        if subindo:
            if v >= float(ligar):
                estado["ligado"] = True
            elif v <= float(desligar):
                estado["ligado"] = False
        else:
            if v <= float(ligar):
                estado["ligado"] = True
            elif v >= float(desligar):
                estado["ligado"] = False
        return estado["ligado"]

    return decidir


# ═══════════════════════════════════════════════════════════
#  Sketch: o que roda NA placa
# ═══════════════════════════════════════════════════════════

_CABECALHO = """// Gerado por DataForge — {descricao}
//
// Grave com:  dataforge iot carregar {arquivo} --fqbn {fqbn}
"""

MODELOS_DE_SKETCH = {
    "firmata": {
        "descricao": "StandardFirmata: a placa vira periferico do computador",
        "corpo": """#include <Firmata.h>

void analogWriteCallback(byte pin, int value) {
  if (IS_PIN_PWM(pin)) {
    pinMode(PIN_TO_DIGITAL(pin), OUTPUT);
    analogWrite(PIN_TO_PWM(pin), value);
  }
}

void setup() {
  Firmata.setFirmwareVersion(FIRMATA_FIRMWARE_MAJOR_VERSION,
                             FIRMATA_FIRMWARE_MINOR_VERSION);
  Firmata.attach(ANALOG_MESSAGE, analogWriteCallback);
  Firmata.begin(57600);
}

void loop() {
  while (Firmata.available()) Firmata.processInput();
}
""",
    },
    "pisca": {
        "descricao": "o LED da placa piscando — o 'ola mundo' do hardware",
        "corpo": """const int LED = {led};
const unsigned long INTERVALO = {intervalo};   // ms

void setup() {
  pinMode(LED, OUTPUT);
}

void loop() {
  digitalWrite(LED, HIGH);
  delay(INTERVALO);
  digitalWrite(LED, LOW);
  delay(INTERVALO);
}
""",
    },
    "sensor": {
        "descricao": "le um analogico e manda pela serial, uma linha por leitura",
        "corpo": """const int SENSOR = A{canal};
const unsigned long INTERVALO = {intervalo};   // ms

void setup() {
  Serial.begin({velocidade});
}

void loop() {
  Serial.println(analogRead(SENSOR));
  delay(INTERVALO);
}
""",
    },
    "ultrassom": {
        "descricao": "HC-SR04: distancia em cm pela serial (pulseIn nao cabe no Firmata)",
        "corpo": """const int GATILHO = {gatilho};
const int ECO = {eco};

void setup() {
  pinMode(GATILHO, OUTPUT);
  pinMode(ECO, INPUT);
  Serial.begin({velocidade});
}

void loop() {
  digitalWrite(GATILHO, LOW);
  delayMicroseconds(2);
  digitalWrite(GATILHO, HIGH);
  delayMicroseconds(10);
  digitalWrite(GATILHO, LOW);

  // 30 ms de teto: sem eco, 'pulseIn' devolve 0 em vez de travar
  unsigned long us = pulseIn(ECO, HIGH, 30000UL);
  Serial.println(us == 0 ? -1.0 : us / 58.0);
  delay({intervalo});
}
""",
    },
    "dht": {
        "descricao": "DHT11/DHT22: temperatura e umidade pela serial, em JSON",
        "corpo": """#include <DHT.h>
DHT dht({pino}, {tipo});

void setup() {
  Serial.begin({velocidade});
  dht.begin();
}

void loop() {
  float t = dht.readTemperature();
  float u = dht.readHumidity();
  if (isnan(t) || isnan(u)) {
    Serial.println("{\\"erro\\":\\"leitura falhou\\"}");
  } else {
    Serial.print("{\\"temperatura\\":");
    Serial.print(t, 1);
    Serial.print(",\\"umidade\\":");
    Serial.print(u, 1);
    Serial.println("}");
  }
  delay({intervalo});   // o DHT nao responde mais de uma vez por 2 s
}
""",
    },
    "wifi-mqtt": {
        "descricao": "ESP32/ESP8266: le um sensor e publica num topico MQTT",
        "corpo": """#include <WiFi.h>
#include <PubSubClient.h>

const char* WIFI = "{rede}";
const char* SENHA = "{senha}";
const char* BROKER = "{broker}";
const char* TOPICO = "{topico}";

WiFiClient rede;
PubSubClient mqtt(rede);

void conectar() {
  WiFi.begin(WIFI, SENHA);
  while (WiFi.status() != WL_CONNECTED) delay(400);
  mqtt.setServer(BROKER, 1883);
  while (!mqtt.connected()) { mqtt.connect("dataforge-{topico}"); delay(600); }
}

void setup() {
  Serial.begin({velocidade});
  conectar();
}

void loop() {
  if (!mqtt.connected()) conectar();
  mqtt.loop();
  char corpo[48];
  snprintf(corpo, sizeof(corpo), "{\\"valor\\":%d}", analogRead(A{canal}));
  mqtt.publish(TOPICO, corpo);
  delay({intervalo});
}
""",
    },
}

#: Os valores que cada modelo aceita, com o padrão.
_PADROES_DE_SKETCH = {
    "firmata": {},
    "pisca": {"led": 13, "intervalo": 500},
    "sensor": {"canal": 0, "intervalo": 200, "velocidade": 115200},
    "ultrassom": {"gatilho": 9, "eco": 10, "intervalo": 200, "velocidade": 115200},
    "dht": {"pino": 2, "tipo": "DHT22", "intervalo": 2000, "velocidade": 115200},
    "wifi-mqtt": {"rede": "minha-rede", "senha": "minha-senha",
                  "broker": "192.168.0.10", "topico": "casa/sala/luz",
                  "canal": 0, "intervalo": 5000, "velocidade": 115200},
}


def sketches():
    """Os modelos de sketch, com o que cada um faz e o que aceita."""
    return {nome: {"descricao": dados["descricao"],
                   "opcoes": dict(_PADROES_DE_SKETCH.get(nome, {}))}
            for nome, dados in sorted(MODELOS_DE_SKETCH.items())}


def sketch(modelo="pisca", opcoes=None, fqbn="arduino:avr:uno"):
    """O código C++ de um sketch, como texto — sem escrever arquivo nenhum."""
    chave = str(modelo)
    if chave not in MODELOS_DE_SKETCH:
        raise _erro(f"nao conheco o sketch '{modelo}'.",
                    nota=f"conheco: {', '.join(sorted(MODELOS_DE_SKETCH))}",
                    dica="IoT.sketches() mostra o que cada um faz")
    from .opcoes import ler as _ler_opcoes
    padrao = dict(_PADROES_DE_SKETCH.get(chave, {}))
    escolhas = {**padrao, **_ler_opcoes(opcoes, padrao, f"IoT.sketch({chave})")}
    corpo = MODELOS_DE_SKETCH[chave]["corpo"]
    for nome, valor in escolhas.items():
        corpo = corpo.replace("{" + nome + "}", str(valor))
    cabecalho = _CABECALHO.format(
        descricao=MODELOS_DE_SKETCH[chave]["descricao"],
        arquivo=f"{chave}/{chave}.ino", fqbn=fqbn)
    return cabecalho + "\n" + corpo


def gravar_sketch(pasta, modelo="pisca", opcoes=None, fqbn="arduino:avr:uno"):
    """Escreve `pasta/<nome>/<nome>.ino` — o layout que o Arduino exige.

    O arquivo **precisa** ter o nome da pasta que o contém; um `.ino`
    solto não compila, e o erro do `arduino-cli` fala de 'sketch not
    found' sem dizer por quê.
    """
    nome = str(modelo).replace("-", "_")
    destino = os.path.join(str(pasta), nome)
    os.makedirs(destino, exist_ok=True)
    caminho = os.path.join(destino, f"{nome}.ino")
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(sketch(modelo, opcoes, fqbn))
    return caminho


# ═══════════════════════════════════════════════════════════
#  arduino-cli: compilar e gravar
# ═══════════════════════════════════════════════════════════

def tem_arduino_cli():
    """O `arduino-cli` está no PATH?"""
    return shutil.which("arduino-cli") is not None


def _exigir_cli():
    caminho = shutil.which("arduino-cli")
    if caminho is None:
        raise _erro(
            "o 'arduino-cli' nao esta instalado.",
            nota="compilar C++ para AVR e gravar pelo bootloader e o que "
                 "ele faz; reimplementar isso aqui seria refazer um "
                 "compilador",
            dica="brew install arduino-cli  |  https://arduino.github.io/arduino-cli")
    return caminho


def _rodar(argumentos, prazo=300):
    saida = subprocess.run([_exigir_cli(), *argumentos], capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           timeout=prazo)
    return {"ok": saida.returncode == 0, "codigo": saida.returncode,
            "saida": saida.stdout, "erro": saida.stderr}


def placas():
    """As placas que o `arduino-cli` vê agora, com FQBN quando ele sabe."""
    resultado = _rodar(["board", "list", "--format", "json"], prazo=60)
    if not resultado["ok"]:
        raise _erro(f"'arduino-cli board list' falhou: {resultado['erro'].strip()}")
    try:
        dados = json.loads(resultado["saida"] or "{}")
    except json.JSONDecodeError:                          # pragma: no cover
        return []
    lista = dados.get("detected_ports", dados) if isinstance(dados, dict) else dados
    achadas = []
    for item in lista or []:
        porta = (item.get("port") or {})
        correspondencias = item.get("matching_boards") or []
        achadas.append({
            "porta": porta.get("address", ""),
            "protocolo": porta.get("protocol", ""),
            "placa": (correspondencias[0].get("name") if correspondencias
                      else porta.get("properties", {}).get("pid", "") and "desconhecida"
                      or "desconhecida"),
            "fqbn": correspondencias[0].get("fqbn", "") if correspondencias else "",
        })
    return achadas


def compilar(caminho, fqbn="arduino:avr:uno"):
    """Compila um sketch. Devolve `{ok, saida, erro}` — e não levanta.

    Um erro de compilação é **resultado**, e não falha do programa: quem
    chama quer mostrar a mensagem do compilador, que é onde está a
    linha errada.
    """
    return _rodar(["compile", "--fqbn", str(fqbn), str(caminho)])


def carregar(caminho, porta=None, fqbn="arduino:avr:uno"):
    """Compila e grava na placa. Devolve `{ok, saida, erro}`."""
    alvo = str(porta) if porta else _unica_porta()
    return _rodar(["compile", "--fqbn", str(fqbn), "--upload",
                   "-p", alvo, str(caminho)])


def nucleos():
    """Os cores instalados no `arduino-cli` — avr, esp32, renesas…"""
    resultado = _rodar(["core", "list", "--format", "json"], prazo=60)
    if not resultado["ok"]:
        raise _erro(f"'arduino-cli core list' falhou: {resultado['erro'].strip()}")
    try:
        dados = json.loads(resultado["saida"] or "[]")
    except json.JSONDecodeError:                          # pragma: no cover
        return []
    lista = dados.get("platforms", dados) if isinstance(dados, dict) else dados
    return [{"id": c.get("id", ""), "instalada": c.get("installed_version",
                                                       c.get("installed", "")),
             "nome": (c.get("releases", {}).get(c.get("installed_version", ""), {})
                      .get("name") or c.get("name", ""))}
            for c in lista or []]


# ═══════════════════════════════════════════════════════════
#  Monitor serial
# ═══════════════════════════════════════════════════════════

def monitorar(porta=None, velocidade=115200, linhas=10, prazo=10.0):
    """Lê N linhas da serial e devolve como cluster.

    É o monitor serial da IDE, do tamanho de uma chamada — e devolvendo
    **dado**, e não texto na tela: dá para afirmar coisas sobre ele num
    teste.
    """
    alvo = str(porta) if porta else _unica_porta()
    serial = iot_serial.abrir(alvo, velocidade, prazo=0.5)
    saida = []
    limite = time.monotonic() + float(prazo)
    try:
        while len(saida) < int(linhas) and time.monotonic() < limite:
            linha = serial.linha(prazo=0.5)
            if linha:
                saida.append(linha)
    finally:
        serial.fechar()
    return saida


def doctor(porta=None):
    """O diagnóstico: porta, placa, sketch e velocidade — nesta ordem.

    Cada linha responde uma pergunta que, sem ela, vira meia hora de
    tentativa: o cabo é de dados? a placa aparece? o Firmata está
    gravado? a velocidade é a dele?
    """
    achados = []
    lista = portas()
    achados.append({
        "o_que": "portas seriais",
        "ok": bool(lista),
        "detalhe": ", ".join(p["porta"] for p in lista) or
                   "nenhuma — cabo so de energia? driver do CH340?"})
    achados.append({
        "o_que": "arduino-cli",
        "ok": tem_arduino_cli(),
        "detalhe": "instalado" if tem_arduino_cli()
                   else "ausente — compilar e gravar exigem ele"})
    if tem_arduino_cli():
        try:
            vistas = placas()
            achados.append({
                "o_que": "placas reconhecidas",
                "ok": any(p["fqbn"] for p in vistas),
                "detalhe": ", ".join(f"{p['placa']} ({p['fqbn'] or 'sem FQBN'}) "
                                     f"em {p['porta']}" for p in vistas)
                           or "nenhuma"})
        except Exception as erro:                         # noqa: BLE001
            achados.append({"o_que": "placas reconhecidas", "ok": False,
                            "detalhe": str(erro)})
    alvo = str(porta) if porta else (lista[0]["porta"] if lista else None)
    if alvo:
        try:
            placa = conectar(alvo, prazo=4.0)
            info = placa.info()
            placa.fechar()
            achados.append({
                "o_que": "Firmata",
                "ok": True,
                "detalhe": f"{info['firmware'].get('nome', '?')} "
                           f"v{info['firmware'].get('versao', '?')}, "
                           f"{info['pinos']} pinos"})
        except Exception as erro:                         # noqa: BLE001
            achados.append({
                "o_que": "Firmata",
                "ok": False,
                "detalhe": f"{erro} — grave o StandardFirmata: "
                           f"dataforge iot sketch firmata"})
    return achados


class ArcaneIoT:
    """O dicionário que `adopt Arcane.IoT` entrega."""

    def __new__(cls):
        from .iot_mqtt import Mqtt, mqtt

        return {
            "__name__": "Arcane.IoT",

            # ── a placa ──
            "portas": portas,
            "conectar": conectar,
            "abrir_serial": iot_serial.abrir,
            "Placa": Placa,
            "modos": modos,

            # ── sem hardware ──
            "simulador": simulador,
            "conectar_simulada": conectar_simulada,
            "Simulador": Simulador,
            "modelos": modelos,

            # ── sensores ──
            "escala": escala,
            "tensao": tensao,
            "tmp36": tmp36,
            "ntc": ntc,
            "divisor": divisor,
            "media_movel": media_movel,
            "histerese": histerese,

            # ── sketch ──
            "sketch": sketch,
            "sketches": sketches,
            "gravar_sketch": gravar_sketch,
            "compilar": compilar,
            "carregar": carregar,
            "placas": placas,
            "nucleos": nucleos,
            "tem_arduino_cli": tem_arduino_cli,

            # ── diagnostico ──
            "monitorar": monitorar,
            "doctor": doctor,

            # ── MQTT ──
            "mqtt": mqtt,
            "Mqtt": Mqtt,
        }
