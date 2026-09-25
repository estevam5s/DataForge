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

#: A velocidade do firmware. Ele fixa 57600 no `setup()`, e o
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
    alvo = _resolver_porta(porta)
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


def _parece_caminho(texto):
    """'/dev/cu.usbmodem1101', 'COM3' — e não 'esp32' ou 'uno r4'."""
    return ("/" in texto or "\\" in texto
            or texto.upper().startswith("COM") and texto[3:].isdigit())


def _resolver_porta(porta):
    """A porta a abrir: o caminho dado, a placa pelo NOME, ou a única."""
    if not porta:
        return _unica_porta()
    texto = str(porta)
    if _parece_caminho(texto):
        return texto
    return _porta_pela_placa(texto)


def _identificadas():
    """As portas USB com o que se sabe delas, SEM abrir nenhuma.

    Abrir uma porta reinicia a placa (o DTR). O que se sabe sem abrir vem
    do `arduino-cli` — o nome, quando é uma placa que ele conhece, e o
    VID:PID do USB. Sem ele, só o nome do arquivo da porta.
    """
    vistas = []
    if tem_arduino_cli():
        try:
            vistas = [p for p in placas() if p.get("usb")]
        except Exception:                                 # noqa: BLE001
            vistas = []
    if vistas:
        return vistas
    return [{"porta": p["porta"], "placa": "desconhecida", "fqbn": "",
             "usb": p["descricao"], "vid": "", "pid": ""} for p in portas()]


def _rotulo(item):
    """'Arduino UNO R4 WiFi' ou 'ponte CH340 (1A86:7523) — …'."""
    if item.get("placa") and item["placa"] != "desconhecida":
        return item["placa"]
    return item.get("usb") or "desconhecida"


def _como_conectar(achadas):
    return "\n".join(f'IoT.conectar("{p["porta"]}")   // {_rotulo(p)}'
                     for p in achadas)


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
        # A dica mostra as portas QUE EXISTEM, com o que se sabe de cada
        # uma. Ela mostrava um exemplo inventado ('/dev/cu.usbmodem1101'),
        # e quem tinha duas placas precisava rodar outro comando para
        # descobrir qual caminho era qual.
        raise _erro(
            f"ha {len(achadas)} placas conectadas: {nomes}.",
            nota="adivinhar qual delas recebe o comando e o tipo de "
                 "conveniencia que liga o rele errado",
            dica="diga qual — pelo caminho, ou pelo nome da placa "
                 '(IoT.conectar("uno r4")):\n'
                 + _como_conectar(_identificadas()))
    return achadas[0]["porta"]


def _normalizar(texto):
    return "".join(c for c in str(texto).lower() if c.isalnum())


def _porta_pela_placa(nome):
    """`IoT.conectar("uno r4")`: a porta cuja placa se chama assim.

    O nome é conferido contra o que o `arduino-cli` diz de cada porta —
    sem abrir nenhuma. Uma ponte USB-serial genérica (CH340, CP210x) não
    diz que chip está atrás dela: um ESP32 e um clone de UNO usam a mesma.
    Nesse caso a busca não acha, e a mensagem diz isso em vez de chutar.
    """
    procurado = _normalizar(nome)
    achadas = _identificadas()
    casam = [p for p in achadas
             if procurado and (procurado in _normalizar(p.get("placa", ""))
                               or procurado in _normalizar(p.get("fqbn", "")))]
    if len(casam) == 1:
        return casam[0]["porta"]
    if len(casam) > 1:
        raise _erro(
            f"ha {len(casam)} placas que casam com '{nome}'.",
            nota=", ".join(f"{p['porta']} ({_rotulo(p)})" for p in casam),
            dica=_como_conectar(casam))
    raise _erro(
        f"nenhuma porta se identifica como '{nome}'.",
        nota=("o nome vem do arduino-cli, e uma ponte USB-serial generica "
              "(CH340, CP210x) nao diz que placa esta atras dela"
              if tem_arduino_cli() else
              "sem o arduino-cli, a placa so e reconhecida pelo caminho"),
        dica=("use o caminho:\n" + _como_conectar(achadas)) if achadas
        else "nao ha placa conectada; rode 'dataforge iot portas'")


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
        "descricao": "o firmware que faz a placa virar periferico do computador",
        "corpo": """#include <Wire.h>
#if __has_include(<Servo.h>)
  #include <Servo.h>
  #define DF_TEM_SERVO 1
#endif

// ── o protocolo ────────────────────────────────────────────
#define DF_DIGITAL_MESSAGE 0x90
#define DF_ANALOG_MESSAGE  0xE0
#define DF_REPORT_ANALOG   0xC0
#define DF_REPORT_DIGITAL  0xD0
#define DF_SET_PIN_MODE    0xF4
#define DF_SET_DIGITAL_PIN 0xF5
#define DF_REPORT_VERSION  0xF9
#define DF_SYSTEM_RESET    0xFF
#define DF_START_SYSEX     0xF0
#define DF_END_SYSEX       0xF7

#define DF_REPORT_FIRMWARE      0x79
#define DF_CAPABILITY_QUERY     0x6B
#define DF_CAPABILITY_RESPONSE  0x6C
#define DF_ANALOG_MAPPING_QUERY 0x69
#define DF_ANALOG_MAPPING_REPLY 0x6A
#define DF_PIN_STATE_QUERY      0x6D
#define DF_PIN_STATE_RESPONSE   0x6E
#define DF_SERVO_CONFIG         0x70
#define DF_I2C_REQUEST          0x76
#define DF_I2C_REPLY            0x77
#define DF_I2C_CONFIG           0x78
#define DF_SAMPLING_INTERVAL    0x7A
// Proprio do DataForge, na faixa que o Firmata reserva para uso livre
// (0x01-0x0F): "que placa e voce?". Um firmware antigo nao responde, e o
// lado de la trata o silencio como "nao sei" — nunca como erro.
#define DF_PLACA_QUERY          0x0E

// Os modos, com os numeros que o 'Arcane.IoT' usa.
#define DF_ENTRADA   0x00
#define DF_SAIDA     0x01
#define DF_ANALOGICO 0x02
#define DF_PWM       0x03
#define DF_SERVO     0x04
#define DF_I2C_MODO  0x06
#define DF_PULLUP    0x0B

#ifndef NUM_DIGITAL_PINS
  #define NUM_DIGITAL_PINS 20
#endif
#ifndef NUM_ANALOG_INPUTS
  #define NUM_ANALOG_INPUTS 6
#endif

// Um ESP32 declara mais de 40 pinos, e a resposta de capacidade cresce
// com eles. O teto e para ela caber na serial sem partir.
#if NUM_DIGITAL_PINS > 64
  #define DF_PINOS 64
#else
  #define DF_PINOS NUM_DIGITAL_PINS
#endif
#define DF_PORTAS ((DF_PINOS + 7) / 8)
#define DF_SYSEX_MAX 64

byte modoDoPino[DF_PINOS];
byte relatarPorta[DF_PORTAS];
byte fotoDaPorta[DF_PORTAS];
unsigned int relatarAnalogico = 0;
unsigned long intervalo = 19;
unsigned long ultimaAmostra = 0;

byte sysex[DF_SYSEX_MAX];
byte nSysex = 0;
bool emSysex = false;
byte comando = 0;
byte args[2];
byte nArgs = 0;
byte precisaArgs = 0;

#ifdef DF_TEM_SERVO
Servo servos[DF_PINOS];
#endif

// ── o que o core diz sobre cada pino ───────────────────────

// O nome da placa, para 'info()["placa"]'. O core define ARDUINO_BOARD
// no ESP32 ("ESP32_DEV"); o Renesas e o AVR definem uma macro por placa.
const char *nomeDaPlaca() {
#if defined(ARDUINO_UNOR4_WIFI)
  return "Arduino UNO R4 WiFi";
#elif defined(ARDUINO_UNOR4_MINIMA)
  return "Arduino UNO R4 Minima";
#elif defined(ARDUINO_AVR_UNO)
  return "Arduino UNO";
#elif defined(ARDUINO_AVR_NANO)
  return "Arduino Nano";
#elif defined(ARDUINO_AVR_MEGA2560)
  return "Arduino Mega 2560";
#elif defined(ARDUINO_AVR_LEONARDO)
  return "Arduino Leonardo";
#elif defined(CONFIG_IDF_TARGET_ESP32S3)
  return "ESP32-S3";
#elif defined(CONFIG_IDF_TARGET_ESP32C3)
  return "ESP32-C3";
#elif defined(CONFIG_IDF_TARGET_ESP32)
  return "ESP32";
#elif defined(ARDUINO_BOARD)
  return ARDUINO_BOARD;
#else
  return "desconhecida";
#endif
}

// Os pinos que EXISTEM e nao podem ser tocados.
//
// E a unica excecao a regra de perguntar ao core: no ESP32 classico os
// GPIO 6 a 11 sao a flash SPI do modulo, e 'digitalPinIsValid' diz que
// eles existem — porque existem. Configurar um deles derruba a placa no
// meio do programa, e o firmware anunciava os seis como entrada, saida
// e PWM.
bool pinoReservado(byte pino) {
#if defined(CONFIG_IDF_TARGET_ESP32)
  return pino >= 6 && pino <= 11;
#else
  (void)pino;
  return false;
#endif
}

bool pinoExiste(byte pino) {
  if (pinoReservado(pino)) return false;
#if defined(digitalPinIsValid)
  return digitalPinIsValid(pino);
#else
  return pino < DF_PINOS;
#endif
}

// Saida, pull-up e PWM exigem um pino que possa ser saida. No ESP32, os
// GPIO 34 a 39 so leem — e nao tem pull-up. O core do ESP-IDF sabe
// disso ('GPIO_IS_VALID_OUTPUT_GPIO'); as outras placas nao tem pino so
// de entrada.
bool podeSair(byte pino) {
#if defined(GPIO_IS_VALID_OUTPUT_GPIO)
  return GPIO_IS_VALID_OUTPUT_GPIO(pino);
#else
  (void)pino;
  return true;
#endif
}

// Qual pino digital atende o canal analogico 'c'.
//
// Tres respostas, e a ordem importa: vence a primeira que o core sabe
// dar. O AVR e o ESP32 definem 'analogInputToDigitalPin'; o UNO R4
// **nao define nenhum dos dois** — so 'PIN_A0' —, e foi por isso que a
// primeira versao deste firmware respondeu 'analogicos: 0' numa placa
// com seis entradas analogicas. Zero honesto continua sendo zero.
int pinoDoCanal(byte canal) {
  if (canal >= NUM_ANALOG_INPUTS) return -1;
#if defined(analogInputToDigitalPin)
  return analogInputToDigitalPin(canal);
#elif defined(PIN_A0)
  return (int)PIN_A0 + (int)canal;
#else
  return -1;
#endif
}

// E o inverso sai do direto, de proposito: se as duas respostas fossem
// escritas separadas, elas divergiriam — e um mapa analogico que nao
// bate com a capacidade faz 'analogico(0)' ler outro pino, calado.
int canalDoPino(byte pino) {
  for (byte c = 0; c < NUM_ANALOG_INPUTS && c < 16; c++) {
    int d = pinoDoCanal(c);
    if (d >= 0 && (byte)d == pino) return c;
  }
  return -1;
}

bool temPwm(byte pino) {
#if defined(digitalPinHasPWM)
  return digitalPinHasPWM(pino);
#else
  return false;
#endif
}

bool ehI2c(byte pino) {
#if defined(SDA) && defined(SCL)
  return pino == (byte)SDA || pino == (byte)SCL;
#else
  return false;
#endif
}

// ── mandar ─────────────────────────────────────────────────

void mandarVersao() {
  Serial.write(DF_REPORT_VERSION);
  Serial.write((byte)2);
  Serial.write((byte)5);
}

void mandarTexto(const char *texto) {
  Serial.write(DF_START_SYSEX);
  Serial.write((byte)0x71);
  for (const char *p = texto; *p; p++) {
    Serial.write((byte)(*p & 0x7F));
    Serial.write((byte)((*p >> 7) & 0x7F));
  }
  Serial.write(DF_END_SYSEX);
}

void responderFirmware() {
  const char *nome = "DataForge";
  Serial.write(DF_START_SYSEX);
  Serial.write(DF_REPORT_FIRMWARE);
  Serial.write((byte)2);
  Serial.write((byte)5);
  for (const char *p = nome; *p; p++) {
    Serial.write((byte)(*p & 0x7F));
    Serial.write((byte)((*p >> 7) & 0x7F));
  }
  Serial.write(DF_END_SYSEX);
}

void responderPlaca() {
  Serial.write(DF_START_SYSEX);
  Serial.write((byte)DF_PLACA_QUERY);
  for (const char *p = nomeDaPlaca(); *p; p++) {
    Serial.write((byte)(*p & 0x7F));
    Serial.write((byte)((*p >> 7) & 0x7F));
  }
  Serial.write(DF_END_SYSEX);
}

void responderCapacidades() {
  Serial.write(DF_START_SYSEX);
  Serial.write(DF_CAPABILITY_RESPONSE);
  for (byte p = 0; p < DF_PINOS; p++) {
    if (pinoExiste(p)) {
      bool sai = podeSair(p);
      Serial.write((byte)DF_ENTRADA); Serial.write((byte)1);
      if (sai) { Serial.write((byte)DF_SAIDA);  Serial.write((byte)1); }
      if (sai) { Serial.write((byte)DF_PULLUP); Serial.write((byte)1); }
      if (canalDoPino(p) >= 0) { Serial.write((byte)DF_ANALOGICO); Serial.write((byte)10); }
      if (sai && temPwm(p))    { Serial.write((byte)DF_PWM);       Serial.write((byte)8); }
#ifdef DF_TEM_SERVO
      if (sai && temPwm(p))    { Serial.write((byte)DF_SERVO);     Serial.write((byte)14); }
#endif
      if (ehI2c(p))            { Serial.write((byte)DF_I2C_MODO);  Serial.write((byte)1); }
    }
    Serial.write((byte)0x7F);
  }
  Serial.write(DF_END_SYSEX);
}

void responderMapaAnalogico() {
  Serial.write(DF_START_SYSEX);
  Serial.write(DF_ANALOG_MAPPING_REPLY);
  for (byte p = 0; p < DF_PINOS; p++) {
    int c = canalDoPino(p);
    Serial.write((byte)(c >= 0 ? c : 0x7F));
  }
  Serial.write(DF_END_SYSEX);
}

void responderEstado(byte pino) {
  if (pino >= DF_PINOS) return;
  int valor = 0;
  if (modoDoPino[pino] == DF_ANALOGICO) {
    int c = canalDoPino(pino);
    valor = (c >= 0) ? analogRead(pino) : 0;
  } else {
    valor = digitalRead(pino);
  }
  Serial.write(DF_START_SYSEX);
  Serial.write(DF_PIN_STATE_RESPONSE);
  Serial.write(pino);
  Serial.write(modoDoPino[pino]);
  Serial.write((byte)(valor & 0x7F));
  if (valor > 0x7F) Serial.write((byte)((valor >> 7) & 0x7F));
  Serial.write(DF_END_SYSEX);
}

// ── receber ────────────────────────────────────────────────

void definirModo(byte pino, byte modo) {
  if (pino >= DF_PINOS || !pinoExiste(pino)) return;
  // Um pino so de entrada recusa os modos que escrevem, aqui tambem: o
  // lado de la ja confere pela capacidade, mas quem fala Firmata cru
  // (outro cliente, um script) nao pode derrubar o pino.
  if (!podeSair(pino) && modo != DF_ENTRADA && modo != DF_ANALOGICO) return;
#ifdef DF_TEM_SERVO
  if (modoDoPino[pino] == DF_SERVO && modo != DF_SERVO) servos[pino].detach();
#endif
  switch (modo) {
    case DF_ENTRADA:   pinMode(pino, INPUT);        break;
    case DF_PULLUP:    pinMode(pino, INPUT_PULLUP); break;
    case DF_SAIDA:     pinMode(pino, OUTPUT);       break;
    case DF_PWM:       pinMode(pino, OUTPUT);       break;
    case DF_ANALOGICO: break;
#ifdef DF_TEM_SERVO
    case DF_SERVO:     servos[pino].attach(pino);   break;
#endif
    case DF_I2C_MODO:  Wire.begin();                break;
    default: return;
  }
  modoDoPino[pino] = modo;
}

void escreverPorta(byte porta, unsigned int valor) {
  for (byte i = 0; i < 8; i++) {
    byte pino = porta * 8 + i;
    if (pino >= DF_PINOS) return;
    if (modoDoPino[pino] == DF_SAIDA)
      digitalWrite(pino, (valor & (1 << i)) ? HIGH : LOW);
  }
}

void escreverAnalogico(byte pino, unsigned int valor) {
  if (pino >= DF_PINOS) return;
#ifdef DF_TEM_SERVO
  if (modoDoPino[pino] == DF_SERVO) { servos[pino].write(valor); return; }
#endif
  if (modoDoPino[pino] == DF_PWM) analogWrite(pino, valor);
}

void tratarSysex() {
  if (nSysex == 0) return;
  switch (sysex[0]) {
    case DF_REPORT_FIRMWARE:      responderFirmware();      break;
    case DF_PLACA_QUERY:          responderPlaca();         break;
    case DF_CAPABILITY_QUERY:     responderCapacidades();   break;
    case DF_ANALOG_MAPPING_QUERY: responderMapaAnalogico(); break;
    case DF_PIN_STATE_QUERY:
      if (nSysex >= 2) responderEstado(sysex[1]);
      break;
    case DF_SAMPLING_INTERVAL:
      if (nSysex >= 3) {
        intervalo = sysex[1] | (sysex[2] << 7);
        if (intervalo < 10) intervalo = 10;
      }
      break;
    case DF_I2C_CONFIG: Wire.begin(); break;
#ifdef DF_TEM_SERVO
    case DF_SERVO_CONFIG:
      if (nSysex >= 6) {
        byte pino = sysex[1];
        if (pino < DF_PINOS) {
          servos[pino].attach(pino, sysex[2] | (sysex[3] << 7),
                                    sysex[4] | (sysex[5] << 7));
          modoDoPino[pino] = DF_SERVO;
        }
      }
      break;
#endif
    case DF_I2C_REQUEST:
      if (nSysex >= 4) {
        byte endereco = sysex[1];
        byte modo = (sysex[2] >> 3) & 0x03;
        if (modo == 0) {                       // escrever
          Wire.beginTransmission(endereco);
          for (byte i = 3; i + 1 < nSysex; i += 2)
            Wire.write((byte)(sysex[i] | (sysex[i + 1] << 7)));
          Wire.endTransmission();
        } else {                               // ler uma vez
          byte registro = (nSysex >= 6) ? (sysex[3] | (sysex[4] << 7)) : 0;
          byte quantos  = (nSysex >= 6) ? (sysex[5] | (sysex[6] << 7)) : 1;
          if (nSysex >= 6) {
            Wire.beginTransmission(endereco);
            Wire.write(registro);
            Wire.endTransmission();
          }
          Wire.requestFrom((int)endereco, (int)quantos);
          Serial.write(DF_START_SYSEX);
          Serial.write(DF_I2C_REPLY);
          Serial.write((byte)(endereco & 0x7F));
          Serial.write((byte)((endereco >> 7) & 0x7F));
          Serial.write((byte)(registro & 0x7F));
          Serial.write((byte)((registro >> 7) & 0x7F));
          while (Wire.available()) {
            byte b = Wire.read();
            Serial.write((byte)(b & 0x7F));
            Serial.write((byte)((b >> 7) & 0x7F));
          }
          Serial.write(DF_END_SYSEX);
        }
      }
      break;
    default: break;
  }
}

void tratarComando() {
  byte tipo = comando & 0xF0;
  byte canal = comando & 0x0F;
  if (tipo == DF_DIGITAL_MESSAGE) {
    escreverPorta(canal, args[0] | (args[1] << 7));
  } else if (tipo == DF_ANALOG_MESSAGE) {
    escreverAnalogico(canal, args[0] | (args[1] << 7));
  } else if (tipo == DF_REPORT_ANALOG) {
    if (args[0]) relatarAnalogico |= (1 << canal);
    else         relatarAnalogico &= ~(1 << canal);
  } else if (tipo == DF_REPORT_DIGITAL) {
    if (canal < DF_PORTAS) relatarPorta[canal] = args[0] ? 1 : 0;
  } else if (comando == DF_SET_PIN_MODE) {
    definirModo(args[0], args[1]);
  } else if (comando == DF_SET_DIGITAL_PIN) {
    byte pino = args[0];
    if (pino < DF_PINOS && modoDoPino[pino] == DF_SAIDA)
      digitalWrite(pino, args[1] ? HIGH : LOW);
  }
}

void consumir(byte b) {
  if (emSysex) {
    if (b == DF_END_SYSEX) { emSysex = false; tratarSysex(); nSysex = 0; }
    else if (nSysex < DF_SYSEX_MAX) sysex[nSysex++] = b;
    return;
  }
  if (b & 0x80) {                              // e um comando
    if (b == DF_START_SYSEX) { emSysex = true; nSysex = 0; return; }
    if (b == DF_REPORT_VERSION) { mandarVersao(); return; }
    if (b == DF_SYSTEM_RESET)   { reiniciarEstado(); return; }
    byte tipo = b & 0xF0;
    if (tipo == DF_DIGITAL_MESSAGE || tipo == DF_ANALOG_MESSAGE) precisaArgs = 2;
    else if (tipo == DF_REPORT_ANALOG || tipo == DF_REPORT_DIGITAL) precisaArgs = 1;
    else if (b == DF_SET_PIN_MODE || b == DF_SET_DIGITAL_PIN) precisaArgs = 2;
    else { precisaArgs = 0; return; }
    comando = b;
    nArgs = 0;
    return;
  }
  if (precisaArgs == 0) return;                // dado sem comando: ignora
  args[nArgs++] = b;
  if (nArgs >= precisaArgs) { tratarComando(); nArgs = 0; }
}

void reiniciarEstado() {
  for (byte p = 0; p < DF_PINOS; p++) {
#ifdef DF_TEM_SERVO
    if (modoDoPino[p] == DF_SERVO) servos[p].detach();
#endif
    modoDoPino[p] = DF_ENTRADA;
  }
  for (byte porta = 0; porta < DF_PORTAS; porta++) {
    relatarPorta[porta] = 0;
    fotoDaPorta[porta] = 0;
  }
  relatarAnalogico = 0;
  intervalo = 19;
}

// ── relatar ────────────────────────────────────────────────

void relatarEntradas() {
  for (byte porta = 0; porta < DF_PORTAS; porta++) {
    if (!relatarPorta[porta]) continue;
    byte valor = 0;
    for (byte i = 0; i < 8; i++) {
      byte pino = porta * 8 + i;
      if (pino >= DF_PINOS) break;
      if (modoDoPino[pino] == DF_ENTRADA || modoDoPino[pino] == DF_PULLUP)
        if (digitalRead(pino)) valor |= (1 << i);
    }
    if (valor != fotoDaPorta[porta]) {
      fotoDaPorta[porta] = valor;
      Serial.write((byte)(DF_DIGITAL_MESSAGE | porta));
      Serial.write((byte)(valor & 0x7F));
      Serial.write((byte)((valor >> 7) & 0x7F));
    }
  }
  for (byte c = 0; c < NUM_ANALOG_INPUTS && c < 16; c++) {
    if (!(relatarAnalogico & (1 << c))) continue;
    int pino = pinoDoCanal(c);
    if (pino < 0) continue;
    int valor = analogRead(pino);
    Serial.write((byte)(DF_ANALOG_MESSAGE | c));
    Serial.write((byte)(valor & 0x7F));
    Serial.write((byte)((valor >> 7) & 0x7F));
  }
}

void setup() {
  Serial.begin(57600);
  // Toda placa relata 10 bits. O R4 le com 14 e o ESP32 com 12, e sem
  // esta linha o MESMO sensor daria 1023 numa placa e 4095 na outra —
  // quem escreve 'analogico(0)' teria de saber em que placa esta.
#if defined(ARDUINO_ARCH_RENESAS) || defined(ESP32) || defined(ARDUINO_ARCH_SAMD) || defined(ARDUINO_ARCH_MBED)
  analogReadResolution(10);
#endif
  reiniciarEstado();
  mandarVersao();
}

void loop() {
  while (Serial.available()) consumir((byte)Serial.read());
  unsigned long agora = millis();
  if (agora - ultimaAmostra >= intervalo) {
    ultimaAmostra = agora;
    relatarEntradas();
  }
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
        propriedades = porta.get("properties") or {}
        vid = _hex4(propriedades.get("vid", ""))
        pid = _hex4(propriedades.get("pid", ""))
        achadas.append({
            "porta": porta.get("address", ""),
            "protocolo": porta.get("protocol", ""),
            "placa": (correspondencias[0].get("name") if correspondencias
                      else "desconhecida"),
            "fqbn": correspondencias[0].get("fqbn", "") if correspondencias else "",
            "vid": vid,
            "pid": pid,
            # Vazio para o que não é USB (Bluetooth, console de depuração):
            # é o que separa uma placa de uma porta do sistema.
            "usb": _chip_usb(vid, pid) if vid else "",
        })
    return achadas


#: O que o VID do USB diz sobre o que está do outro lado do cabo. É sobre
#: o CHIP USB, e não sobre a placa: uma ponte CH340 está num clone de UNO
#: e num ESP32 igualmente, e dizer mais que isso seria chutar.
_CHIPS_USB = {
    "2341": "Arduino, USB oficial",
    "2A03": "Arduino, USB oficial",
    "1A86": "ponte CH340 — clone de UNO/Nano, ESP32 ou ESP8266",
    "10C4": "ponte CP210x — comum em ESP32 DevKit e NodeMCU",
    "0403": "ponte FTDI",
    "303A": "Espressif com USB nativo (ESP32-S2, S3 ou C3)",
    "239A": "Adafruit",
    "2E8A": "Raspberry Pi (RP2040)",
}


def _hex4(valor):
    texto = str(valor or "").lower().replace("0x", "")
    return texto.upper().zfill(4) if texto else ""


def _chip_usb(vid, pid):
    base = _CHIPS_USB.get(vid, "USB-serial")
    return f"{base} ({vid}:{pid})"


def compilar(caminho, fqbn="arduino:avr:uno"):
    """Compila um sketch. Devolve `{ok, saida, erro}` — e não levanta.

    Um erro de compilação é **resultado**, e não falha do programa: quem
    chama quer mostrar a mensagem do compilador, que é onde está a
    linha errada.
    """
    return _rodar(["compile", "--fqbn", str(fqbn), str(caminho)])


def carregar(caminho, porta=None, fqbn=None):
    """Compila e grava na placa. Devolve `{ok, saida, erro}`.

    `caminho` é a pasta de um sketch, ou o NOME de um modelo
    (`"firmata"`, `"pisca"`…): aí o sketch é gerado numa pasta temporária
    para aquela placa e gravado.

    Sem `fqbn`, a placa é descoberta pela porta. O padrão era
    `arduino:avr:uno`: gravar num UNO R4 sem dizer o FQBN compilava para
    o UNO clássico e mandava o binário para a placa errada. Uma porta que
    não se identifica (uma ponte CH340 serve a um clone de UNO e a um
    ESP32) é RECUSADA, em vez de receber um chute.
    """
    alvo = _resolver_porta(porta)
    if not fqbn:
        fqbn = _fqbn_da_porta(alvo)
    fonte = str(caminho)
    if not os.path.exists(fonte) and fonte in MODELOS_DE_SKETCH:
        import tempfile
        pasta = tempfile.mkdtemp(prefix="dataforge-sketch-")
        fonte = os.path.dirname(gravar_sketch(pasta, fonte, None, fqbn))
    return _rodar(["compile", "--fqbn", str(fqbn), "--upload",
                   "-p", alvo, fonte])


def _fqbn_da_porta(porta):
    """O FQBN da placa nesta porta, pelo arduino-cli — ou uma recusa."""
    conhecidas = [p for p in _identificadas() if p["porta"] == porta]
    if conhecidas and conhecidas[0].get("fqbn"):
        return conhecidas[0]["fqbn"]
    quem = _rotulo(conhecidas[0]) if conhecidas else "desconhecida"
    raise _erro(
        f"nao sei que placa esta em {porta} ({quem}).",
        nota="compilar para a placa errada grava um binario que ela nao "
             "roda — e o erro, quando aparece, fala do bootloader",
        dica="diga o FQBN: --fqbn=esp32:esp32:esp32, "
             "--fqbn=arduino:avr:uno, --fqbn=arduino:renesas_uno:unor4wifi "
             "('arduino-cli board listall' mostra todos)")


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
            # Só o que é USB. O Bluetooth e o console de depuração do macOS
            # também são portas seriais, e apareciam aqui como "placas
            # desconhecidas" — ruído na linha que devia responder "a placa
            # aparece?".
            vistas = [p for p in placas() if p.get("usb")]
            achados.append({
                "o_que": "placas reconhecidas",
                "ok": bool(vistas),
                "detalhe": ", ".join(
                    f"{_rotulo(p)}{' (' + p['fqbn'] + ')' if p['fqbn'] else ''}"
                    f" em {p['porta']}" for p in vistas) or "nenhuma"})
        except Exception as erro:                         # noqa: BLE001
            achados.append({"o_que": "placas reconhecidas", "ok": False,
                            "detalhe": str(erro)})
    # O Firmata de CADA placa, e não só da primeira: com duas na mesa, a
    # segunda nunca era conferida. Abrir reinicia a placa — é um
    # diagnóstico, e é o único jeito de perguntar o que está gravado.
    alvos = [str(porta)] if porta else [p["porta"] for p in lista]
    for alvo in alvos:
        onde = "" if porta or len(alvos) == 1 else f"{alvo}: "
        try:
            placa = conectar(alvo, prazo=4.0)
            info = placa.info()
            placa.fechar()
            quem = f"{info['placa']}, " if info.get("placa") else ""
            achados.append({
                "o_que": "Firmata",
                "ok": True,
                "detalhe": f"{onde}{quem}{info['firmware'].get('nome', '?')} "
                           f"v{info['firmware'].get('versao', '?')}, "
                           f"{info['pinos']} pinos"})
        except Exception as erro:                         # noqa: BLE001
            achados.append({
                "o_que": "Firmata",
                "ok": False,
                "detalhe": f"{onde}{erro} — grave o firmware: "
                           f"dataforge iot carregar firmata --porta={alvo}"})
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
