# -*- coding: utf-8 -*-
"""Uma placa de mentira que fala Firmata de verdade.

Ela **não** é um dublê que responde `yes` para tudo: é um transporte que
recebe os mesmos bytes que o cabo levaria, os interpreta com as mesmas
regras do `StandardFirmata`, guarda o estado dos pinos e devolve as
mesmas respostas — versão, firmware, capacidades, mapa analógico,
relatório periódico dos analógicos.

Isso é o que torna executável todo exemplo de `/docs/iot`, e o que deixa
os testes rodarem no CI. E é o que a documentação promete: um dublê mais
estreito que o original aprova o que quebra no hardware — foi o defeito
do `BotFalso.responder_inline`, registrado no CLAUDE.md.

O que ele **não** simula, e está dito: tempo de subida de um sinal,
ruído de um sensor, corrente, e o que acontece quando o cabo cai no meio
de um sysex. Para isso não há atalho: é placa de verdade, e é o que
`dataforge iot doctor` faz.
"""

import threading
import time

from .iot_firmata import (ANALOG_MAPPING_QUERY, ANALOG_MAPPING_RESPONSE,
                          ANALOG_MESSAGE, CAPABILITY_QUERY,
                          CAPABILITY_RESPONSE, DIGITAL_MESSAGE, END_SYSEX,
                          I2C_CONFIG, I2C_REPLY, I2C_REQUEST, MODOS,
                          NOME_DO_MODO, PROTOCOL_VERSION, REPORT_ANALOG,
                          REPORT_DIGITAL, REPORT_FIRMWARE, SAMPLING_INTERVAL,
                          SERVO_CONFIG, SET_DIGITAL_PIN, SET_PIN_MODE,
                          START_SYSEX, STRING_DATA, SYSTEM_RESET)

#: Os modelos que o simulador conhece, com o mapa de pinos de cada um.
#:
#: Os números vêm da documentação de cada placa: o UNO tem 14 digitais e
#: 6 analógicos, com PWM em 3, 5, 6, 9, 10 e 11; o Mega tem 54 e 16; o
#: Nano é um UNO com dois analógicos a mais.
#:
#: `tensao`, `bits` e `fqbn` estão aqui porque a conta do sensor depende
#: dos três: ligar um sensor de 5 V num ESP32 costuma matar o pino, e a
#: leitura dele vai a 4095 e não a 1023 — dois erros que aparecem como
#: número errado, e não como falha.
MODELOS = {
    "uno": {"digitais": 14, "analogicos": 6, "pwm": (3, 5, 6, 9, 10, 11),
            "tensao": 5.0, "bits": 10, "fqbn": "arduino:avr:uno",
            "firmware": "StandardFirmata.ino", "descricao": "Arduino UNO (ATmega328P)"},
    "nano": {"digitais": 14, "analogicos": 8, "pwm": (3, 5, 6, 9, 10, 11),
             "tensao": 5.0, "bits": 10, "fqbn": "arduino:avr:nano",
             "firmware": "StandardFirmata.ino", "descricao": "Arduino Nano"},
    "mega": {"digitais": 54, "analogicos": 16,
             "pwm": tuple(range(2, 14)) + (44, 45, 46),
             "tensao": 5.0, "bits": 10, "fqbn": "arduino:avr:mega",
             "firmware": "StandardFirmata.ino", "descricao": "Arduino Mega 2560"},
    "leonardo": {"digitais": 20, "analogicos": 12, "pwm": (3, 5, 6, 9, 10, 11, 13),
                 "tensao": 5.0, "bits": 10, "fqbn": "arduino:avr:leonardo",
                 "firmware": "StandardFirmata.ino", "descricao": "Arduino Leonardo"},
    "uno-r4": {"digitais": 14, "analogicos": 6, "pwm": (3, 5, 6, 9, 10, 11),
               "tensao": 5.0, "bits": 10,
               "fqbn": "arduino:renesas_uno:unor4wifi",
               "firmware": "StandardFirmata.ino", "descricao": "Arduino UNO R4 (Renesas)"},
    "esp32": {"digitais": 40, "analogicos": 16,
              "pwm": tuple(range(0, 34)),
              "tensao": 3.3, "bits": 12, "fqbn": "esp32:esp32:esp32",
              "firmware": "StandardFirmata.ino",
              "descricao": "ESP32 (o Firmata roda pela USB-serial)"},
}


class Simulador:
    """O transporte que finge ser o cabo — e a placa do outro lado."""

    def __init__(self, modelo="uno", versao=(2, 5)):
        chave = str(modelo).lower()
        if chave not in MODELOS:
            from ..errors import RuntimeError_
            raise RuntimeError_(
                f"nao conheco a placa '{modelo}'.", 0, 0,
                nota=f"conheco: {', '.join(sorted(MODELOS))}",
                dica="IoT.simulador(\"uno\") e o padrao", doc="iot/sem-placa")
        self.modelo = chave
        self.mapa = MODELOS[chave]
        self.versao = versao
        self._saida = bytearray()        # o que a placa mandou
        self._trava = threading.RLock()
        self._pinos = {}                 # pino -> valor escrito
        self._modos = {}
        self._analogicos = {}            # canal -> valor (quem testa define)
        self._relatando = set()
        self._relatando_portas = set()
        self._servos = {}
        self._i2c = {}                   # endereco -> {registro: [bytes]}
        self._amostragem = 19
        self._parcial = bytearray()
        self._sysex = None
        self._aberta = True
        self._ultimo_envio = 0.0
        self.recebidos = 0               # quantos comandos chegaram

    # ── o lado do transporte ─────────────────────────────────

    def escrever(self, dados):
        """O computador mandou bytes: a placa os interpreta agora."""
        if not self._aberta:
            return 0
        for byte in bytes(dados):
            self._consumir(byte)
        return len(bytes(dados))

    def ler(self, quantos=64, prazo=0.05):
        """O que a placa tem a dizer — inclusive o relatório periódico."""
        self._talvez_relatar()
        with self._trava:
            if not self._saida:
                return b""
            pedaco = bytes(self._saida[:quantos])
            del self._saida[:quantos]
            return pedaco

    def fechar(self):
        self._aberta = False
        return True

    def aberta(self):
        return self._aberta

    # ── a placa ──────────────────────────────────────────────

    def _responder(self, dados):
        with self._trava:
            self._saida.extend(bytes(dados))

    def _consumir(self, byte):
        if self._sysex is not None:
            if byte == END_SYSEX:
                self._tratar_sysex(bytes(self._sysex))
                self._sysex = None
            else:
                self._sysex.append(byte)
            return
        if byte == START_SYSEX:
            self._sysex = bytearray()
            return
        if byte & 0x80:
            self._parcial = bytearray([byte])
            if byte == PROTOCOL_VERSION:
                self.recebidos += 1
                self._responder([PROTOCOL_VERSION, self.versao[0], self.versao[1]])
                self._parcial = bytearray()
            elif byte == SYSTEM_RESET:
                self.recebidos += 1
                with self._trava:
                    self._modos.clear()
                    self._pinos.clear()
                    self._relatando.clear()
                self._parcial = bytearray()
            return
        self._parcial.append(byte)
        cabeca = self._parcial[0]
        comando = cabeca & 0xF0
        canal = cabeca & 0x0F
        if cabeca == SET_PIN_MODE and len(self._parcial) == 3:
            self.recebidos += 1
            self._modos[self._parcial[1]] = NOME_DO_MODO.get(self._parcial[2], "?")
            self._parcial = bytearray()
        elif cabeca == SET_DIGITAL_PIN and len(self._parcial) == 3:
            self.recebidos += 1
            self._pinos[self._parcial[1]] = self._parcial[2]
            self._parcial = bytearray()
        elif comando == ANALOG_MESSAGE and len(self._parcial) == 3:
            self.recebidos += 1
            valor = self._parcial[1] | (self._parcial[2] << 7)
            if self._modos.get(canal) == "servo":
                self._servos[canal] = valor
            self._pinos[canal] = valor
            self._parcial = bytearray()
        elif comando == REPORT_ANALOG and len(self._parcial) == 2:
            self.recebidos += 1
            (self._relatando.add if self._parcial[1] else self._relatando.discard)(canal)
            self._parcial = bytearray()
        elif comando == REPORT_DIGITAL and len(self._parcial) == 2:
            self.recebidos += 1
            (self._relatando_portas.add if self._parcial[1]
             else self._relatando_portas.discard)(canal)
            self._parcial = bytearray()

    def _tratar_sysex(self, corpo):
        if not corpo:
            return
        self.recebidos += 1
        tipo = corpo[0]
        if tipo == REPORT_FIRMWARE:
            nome = self.mapa["firmware"]
            partes = bytearray([START_SYSEX, REPORT_FIRMWARE,
                                self.versao[0], self.versao[1]])
            for c in nome.encode("ascii", "replace"):
                partes += bytes([c & 0x7F, (c >> 7) & 0x7F])
            partes.append(END_SYSEX)
            self._responder(partes)
        elif tipo == CAPABILITY_QUERY:
            self._responder(self._capacidades())
        elif tipo == ANALOG_MAPPING_QUERY:
            partes = bytearray([START_SYSEX, ANALOG_MAPPING_RESPONSE])
            for pino in range(self.mapa["digitais"] + self.mapa["analogicos"]):
                canal = pino - self.mapa["digitais"]
                partes.append(canal if canal >= 0 else 0x7F)
            partes.append(END_SYSEX)
            self._responder(partes)
        elif tipo == SAMPLING_INTERVAL and len(corpo) >= 3:
            self._amostragem = corpo[1] | (corpo[2] << 7)
        elif tipo == SERVO_CONFIG and len(corpo) >= 2:
            self._modos[corpo[1]] = "servo"
        elif tipo == I2C_CONFIG:
            pass
        elif tipo == I2C_REQUEST and len(corpo) >= 3:
            self._tratar_i2c(corpo)

    def _tratar_i2c(self, corpo):
        endereco, modo = corpo[1], corpo[2]
        if modo & 0x18:                       # leitura (uma vez ou contínua)
            registro = corpo[3] | (corpo[4] << 7) if len(corpo) > 4 else 0
            quantos = corpo[5] | (corpo[6] << 7) if len(corpo) > 6 else 1
            if endereco not in self._i2c:
                # Um endereço sem dispositivo não responde — ele não
                # responde ZERO, ele fica calado, e é essa a diferença
                # que o programa precisa enxergar. Devolver zeros aqui
                # faria o simulador ensinar o contrário do que acontece
                # com um fio solto: um sensor "presente" medindo nada.
                return
            dados = (self._i2c.get(endereco, {}).get(registro)
                     or [0] * int(quantos))
            partes = bytearray([START_SYSEX, I2C_REPLY,
                                endereco & 0x7F, (endereco >> 7) & 0x7F,
                                registro & 0x7F, (registro >> 7) & 0x7F])
            for byte in dados[:quantos]:
                partes += bytes([byte & 0x7F, (byte >> 7) & 0x7F])
            partes.append(END_SYSEX)
            self._responder(partes)
        else:                                 # escrita
            valores = [corpo[i] | (corpo[i + 1] << 7)
                       for i in range(3, len(corpo) - 1, 2)]
            if valores:
                self._i2c.setdefault(endereco, {})[valores[0]] = valores[1:]

    def _capacidades(self):
        partes = bytearray([START_SYSEX, CAPABILITY_RESPONSE])
        for pino in range(self.mapa["digitais"]):
            partes += bytes([MODOS["entrada"], 1, MODOS["saida"], 1,
                             MODOS["entrada_pullup"], 1])
            if pino in self.mapa["pwm"]:
                partes += bytes([MODOS["pwm"], 8])
                partes += bytes([MODOS["servo"], 14])
            partes.append(0x7F)
        for canal in range(self.mapa["analogicos"]):
            partes += bytes([MODOS["entrada"], 1, MODOS["saida"], 1,
                             MODOS["analogico"], 10, MODOS["i2c"], 1])
            partes.append(0x7F)
        partes.append(END_SYSEX)
        return partes

    def _talvez_relatar(self):
        """O envio periódico dos analógicos, como a placa faz."""
        agora = time.monotonic()
        if agora - self._ultimo_envio < self._amostragem / 1000.0:
            return
        self._ultimo_envio = agora
        for canal in sorted(self._relatando):
            valor = int(self._analogicos.get(canal, 0))
            self._responder([ANALOG_MESSAGE | (canal & 0x0F),
                             valor & 0x7F, (valor >> 7) & 0x7F])

    # ── o que quem testa controla ────────────────────────────

    def definir_analogico(self, canal, valor):
        """O que o sensor 'está medindo'.

        A faixa vem da PLACA: 0 a 1023 num UNO, 0 a 4095 num ESP32.
        Um teto fixo de 1023 recusaria a leitura normal de um ESP32 —
        e a diferença entre os dois é justamente o que mais engana
        quem troca de placa.
        """
        v = int(valor)
        bits = int(self.mapa.get("bits", 10))
        teto = (1 << bits) - 1
        if not 0 <= v <= teto:
            from ..errors import RuntimeError_
            raise RuntimeError_(
                f"um analogico de {bits} bits vai de 0 a {teto}, e veio {v}.",
                0, 0, nota=f"esta placa e um {self.mapa['descricao']}",
                doc="iot/sem-placa")
        self._analogicos[int(canal)] = v
        self._ultimo_envio = 0.0          # o próximo `ler` já relata
        return v

    def definir_digital(self, pino, valor):
        """Finge que alguém apertou o botão ligado neste pino."""
        alto = 1 if valor in (True, 1, "1") else 0
        self._pinos[int(pino)] = alto
        porta = int(pino) // 8
        mascara = 0
        for i in range(8):
            if self._pinos.get(porta * 8 + i):
                mascara |= 1 << i
        self._responder([DIGITAL_MESSAGE | (porta & 0x0F),
                         mascara & 0x7F, (mascara >> 7) & 0x7F])
        return alto == 1

    def definir_i2c(self, endereco, registro, dados):
        """O que um dispositivo I2C responderia naquele registrador."""
        self._i2c.setdefault(int(endereco), {})[int(registro)] = [int(d) for d in dados]
        return True

    def mandar_texto(self, texto):
        """O `Firmata.sendString` do sketch, visto de cá."""
        partes = bytearray([START_SYSEX, STRING_DATA])
        for c in str(texto).encode("utf-8"):
            partes += bytes([c & 0x7F, (c >> 7) & 0x7F])
        partes.append(END_SYSEX)
        self._responder(partes)
        return True

    # ── o que quem testa PERGUNTA ────────────────────────────

    def pino(self, numero):
        """O valor que a placa recebeu para aquele pino."""
        return self._pinos.get(int(numero), 0)

    def modo_do_pino(self, numero):
        return self._modos.get(int(numero))

    def servo(self, pino):
        return self._servos.get(int(pino))

    def estado(self):
        return {
            "modelo": self.modelo,
            "descricao": self.mapa["descricao"],
            "pinos": {str(p): v for p, v in sorted(self._pinos.items())},
            "modos": {str(p): m for p, m in sorted(self._modos.items())},
            "amostragem_ms": self._amostragem,
            "comandos_recebidos": self.recebidos,
        }

    def __repr__(self):
        return (f"<simulador {self.modelo}: {len(self._modos)} pino(s) "
                f"configurado(s), {self.recebidos} comando(s)>")
