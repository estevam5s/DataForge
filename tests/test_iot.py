"""Arcane.IoT — porta serial, Firmata, sensores, sketch e MQTT.

O que esta suíte consegue provar sem hardware, e como:

| Camada | Contra o quê |
|---|---|
| porta serial | um **PTY de verdade** — um dispositivo tty do sistema |
| Firmata | o `Simulador`, que interpreta os mesmos bytes que o cabo levaria |
| sketch | o **arduino-cli**, compilando para uma placa real (quando há core) |
| MQTT | um broker mínimo escrito aqui, falando o protocolo |

E o que ela **não** prova, dito sem rodeio: tempo de subida de um sinal,
ruído de sensor, corrente, e o que acontece quando o cabo cai no meio de
um sysex. Para isso é placa de verdade — `test_com_placa_de_verdade`
roda quando `DATAFORGE_ARDUINO` aponta para uma porta.
"""
import os
import socket
import struct
import sys
import threading
import time

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402
from dataforge.stdlib.iot_firmata import Placa  # noqa: E402
from dataforge.stdlib.iot_simulador import Simulador  # noqa: E402
from tests._df import rodar  # noqa: E402

IoT = get_module("Arcane.IoT")


@pytest.fixture()
def placa():
    p = IoT["conectar_simulada"]("uno")
    yield p
    p.fechar()


# ═══════════════════════════════════════════════════════════
#  A porta serial, contra um tty de verdade
# ═══════════════════════════════════════════════════════════

@pytest.mark.skipif(sys.platform.startswith("win"),
                    reason="pty é POSIX; no Windows o caminho é o ctypes")
class TestSerial:
    def _par(self):
        import pty
        mestre, escravo = pty.openpty()
        return mestre, os.ttyname(escravo)

    def test_le_uma_linha_do_outro_lado(self):
        mestre, nome = self._par()
        s = IoT["abrir_serial"](nome, 115200, 0.5)
        os.write(mestre, b"21.5\r\n")
        assert s.linha() == "21.5"          # o \r some junto
        s.fechar()

    def test_escreve_e_o_outro_lado_recebe(self):
        mestre, nome = self._par()
        s = IoT["abrir_serial"](nome, 9600, 0.5)
        assert s.escrever(b"ping\n") == 5
        time.sleep(0.05)
        assert os.read(mestre, 32) == b"ping\n"
        s.fechar()

    def test_ler_sem_nada_devolve_vazio_e_nao_levanta(self):
        """Uma leitura que levanta obrigaria um `monitor` por volta do laço."""
        _mestre, nome = self._par()
        s = IoT["abrir_serial"](nome, 115200, 0.1)
        assert s.ler(8) == b""
        s.fechar()

    def test_fechar_e_idempotente_e_depois_disso_recusa(self):
        _mestre, nome = self._par()
        s = IoT["abrir_serial"](nome, 115200, 0.1)
        assert s.fechar() is True
        assert s.fechar() is False
        with pytest.raises(Exception, match="ja foi fechada"):
            s.ler(1)

    def test_velocidade_impossivel_e_recusada_com_a_lista(self):
        with pytest.raises(Exception, match="velocidade"):
            IoT["abrir_serial"]("/dev/null", 12345)

    def test_porta_que_nao_existe_diz_o_que_fazer(self):
        with pytest.raises(Exception) as info:
            IoT["abrir_serial"]("/dev/nao-existe-mesmo", 115200)
        assert "portas()" in info.value.dica


def test_portas_devolve_vault_com_porta_e_descricao():
    for p in IoT["portas"]():
        assert set(p) == {"porta", "descricao"} and p["porta"]


# ═══════════════════════════════════════════════════════════
#  Firmata
# ═══════════════════════════════════════════════════════════

class TestFirmata:
    def test_apresentar_traz_firmware_capacidades_e_mapa(self, placa):
        info = placa.info()
        assert info["firmware"]["nome"] == "DataForge"
        assert info["protocolo"] == "2.5"
        assert info["pinos"] == 20 and info["analogicos"] == 6

    def test_escrever_digital_chega_na_placa(self, placa):
        placa.modo(13, "saida")
        placa.escrever(13, True)
        assert placa.simulador.pino(13) == 1
        placa.escrever(13, False)
        assert placa.simulador.pino(13) == 0

    def test_o_pino_so_aceita_o_que_a_PLACA_diz_que_faz(self, placa):
        """A lista vem da placa, e não de uma tabela escrita aqui."""
        assert "pwm" in placa.capacidades(9)
        assert "pwm" not in placa.capacidades(13)
        with pytest.raises(Exception, match="nao faz 'pwm'"):
            placa.modo(13, "pwm")
        with pytest.raises(Exception, match="nao tem o pino"):
            placa.modo(99, "saida")

    def test_pwm_e_servo_exigem_o_modo_declarado(self, placa):
        with pytest.raises(Exception, match="precisa do modo declarado"):
            placa.pwm(9, 100)
        placa.modo(9, "pwm")
        assert placa.pwm(9, 200) == 200
        assert placa.simulador.pino(9) == 200
        with pytest.raises(Exception, match="0 a 255"):
            placa.pwm(9, 300)

    def test_servo_vai_de_0_a_180(self, placa):
        placa.modo(3, "servo")
        assert placa.servo(3, 90) == 90
        assert placa.simulador.servo(3) == 90
        with pytest.raises(Exception, match="0 a 180"):
            placa.servo(3, 200)

    def test_analogico_chega_pelo_relatorio_periodico(self, placa):
        placa.modo(14, "analogico")
        placa.relatar_analogico(0)
        placa.simulador.definir_analogico(0, 733)
        prazo = time.monotonic() + 2
        while placa.analogico(0) != 733 and time.monotonic() < prazo:
            time.sleep(0.01)
        assert placa.analogico(0) == 733

    def test_sem_relatar_nada_chega(self, placa):
        """É o defeito nº 1 de quem começa: o pino está certo e o valor é 0."""
        placa.modo(14, "analogico")
        placa.simulador.definir_analogico(0, 900)
        time.sleep(0.1)
        assert placa.analogico(0) == 0

    def test_botao_muda_o_digital_e_o_observador_ve(self, placa):
        vistos = []
        placa.observar(vistos.append)
        placa.modo(2, "entrada_pullup")
        placa.simulador.definir_digital(2, 1)
        prazo = time.monotonic() + 2
        while not placa.ler(2) and time.monotonic() < prazo:
            time.sleep(0.01)
        assert placa.ler(2) is True
        placa.simulador.definir_digital(2, 0)
        time.sleep(0.15)
        assert any(e["tipo"] == "digital" and e["pino"] == 2 for e in vistos)

    def test_texto_do_sketch_atravessa_com_acento(self, placa):
        """Ler só a metade baixa de cada par faz "olá" virar "olC!"."""
        placa.simulador.mandar_texto("olá, ção — 42")
        prazo = time.monotonic() + 2
        while not placa.textos() and time.monotonic() < prazo:
            time.sleep(0.01)
        assert placa.textos() == ["olá, ção — 42"]

    def test_i2c_le_o_que_o_dispositivo_responde(self, placa):
        placa.simulador.definir_i2c(0x68, 0x3B, [1, 2, 3, 4])
        placa.i2c_configurar()
        assert placa.i2c_ler(0x68, 0x3B, 4, prazo=2) == [1, 2, 3, 4]

    def test_endereco_sem_dispositivo_fica_CALADO(self, placa):
        """Fio solto, endereço errado e sensor sem energia dão o mesmo
        resultado no fio: nada. Devolver zeros faria o programa ver um
        sensor presente medindo zero — que é o pior desfecho."""
        placa.i2c_configurar()
        assert placa.i2c_ler(0x77, 0xD0, 1, prazo=0.3) is None

    def test_endereco_conhecido_e_registro_novo_responde_zeros(self, placa):
        """Um dispositivo presente responde, mesmo que o registro não
        signifique nada — é o que o barramento faz."""
        placa.simulador.definir_i2c(0x68, 0x3B, [1])
        placa.i2c_configurar()
        assert placa.i2c_ler(0x68, 0x40, 2, prazo=1) == [0, 0]

    def test_amostragem_tem_faixa(self, placa):
        assert placa.amostragem(50) == 50
        assert placa.simulador.estado()["amostragem_ms"] == 50
        with pytest.raises(Exception, match="10 a 10000"):
            placa.amostragem(1)

    def test_fechar_desliga_as_saidas(self, placa):
        """Terminar deixando um relé ligado é o defeito mais caro daqui."""
        placa.modo(13, "saida")
        placa.escrever(13, True)
        assert placa.simulador.pino(13) == 1
        placa.fechar()
        assert placa.simulador.pino(13) == 0
        assert placa.fechar() is False

    def test_modo_que_nao_existe_lista_os_que_existem(self, placa):
        with pytest.raises(Exception, match="nao e um modo de pino"):
            placa.modo(2, "telepatia")

    def test_reiniciar_limpa_os_modos(self, placa):
        placa.modo(13, "saida")
        placa.reiniciar()
        assert placa.capacidades(13)          # a placa continua conhecida
        with pytest.raises(Exception, match="precisa do modo declarado"):
            placa.pwm(9, 10)


def test_cada_modelo_tem_o_mapa_da_placa_de_verdade():
    modelos = IoT["modelos"]()
    assert modelos["uno"]["digitais"] == 14 and modelos["uno"]["analogicos"] == 6
    assert modelos["mega"]["digitais"] == 54
    assert 11 in modelos["uno"]["pwm"] and 4 not in modelos["uno"]["pwm"]
    with pytest.raises(Exception, match="nao conheco a placa"):
        IoT["simulador"]("commodore-64")


def test_a_escala_do_analogico_vem_da_PLACA():
    """1023 num UNO, 4095 num ESP32 — e é a troca de placa que engana."""
    uno = Simulador("uno")
    with pytest.raises(Exception, match="0 a 1023"):
        uno.definir_analogico(0, 5000)
    assert uno.definir_analogico(0, 1023) == 1023

    esp = Simulador("esp32")
    assert esp.definir_analogico(0, 4095) == 4095      # normal num ESP32
    with pytest.raises(Exception, match="0 a 4095"):
        esp.definir_analogico(0, 5000)


def test_cada_modelo_diz_a_tensao_os_bits_e_o_fqbn():
    """A conta do sensor depende dos três, e trocar de placa os muda."""
    modelos = IoT["modelos"]()
    assert modelos["uno"]["tensao"] == 5.0 and modelos["uno"]["bits"] == 10
    assert modelos["esp32"]["tensao"] == 3.3 and modelos["esp32"]["bits"] == 12
    assert modelos["uno-r4"]["fqbn"] == "arduino:renesas_uno:unor4wifi"
    for nome, dados in modelos.items():
        assert dados["fqbn"].count(":") == 2, nome


def test_mega_tem_mais_pinos_e_o_firmata_os_ve():
    p = IoT["conectar_simulada"]("mega")
    try:
        assert p.info()["pinos"] == 70
        p.modo(53, "saida")
        p.escrever(53, True)
        assert p.simulador.pino(53) == 1
    finally:
        p.fechar()


# ═══════════════════════════════════════════════════════════
#  Sensores
# ═══════════════════════════════════════════════════════════

class TestSensores:
    def test_escala_limita_por_padrao(self):
        """O `map` do C não limita — e 1024 vira 101% num painel."""
        assert IoT["escala"](512, 0, 1023, 0, 100) == pytest.approx(50.05, abs=0.1)
        assert IoT["escala"](2000, 0, 1023, 0, 100) == 100
        assert IoT["escala"](-5, 0, 1023, 0, 100) == 0
        assert IoT["escala"](2000, 0, 1023, 0, 100, limitar=False) > 100

    def test_faixa_de_largura_zero_e_recusada(self):
        with pytest.raises(Exception, match="largura zero"):
            IoT["escala"](1, 5, 5, 0, 10)

    def test_tensao_conhece_a_resolucao(self):
        assert IoT["tensao"](1023) == pytest.approx(5.0, abs=0.01)
        assert IoT["tensao"](4095, 3.3, 12) == pytest.approx(3.3, abs=0.01)

    def test_tmp36_em_graus(self):
        # 750 mV = 25 °C, pela folha de dados
        leitura = 0.75 / 5.0 * 1023
        assert IoT["tmp36"](leitura) == pytest.approx(25, abs=0.5)

    def test_ntc_a_25_graus_da_25(self):
        """Com o termistor na resistência nominal, o divisor lê a metade."""
        assert IoT["ntc"](1023 / 2) == pytest.approx(25, abs=0.3)

    def test_ntc_na_ponta_da_escala_explica_o_curto(self):
        with pytest.raises(Exception, match="ponta da escala"):
            IoT["ntc"](0)
        with pytest.raises(Exception, match="ponta da escala"):
            IoT["ntc"](1023)

    def test_divisor_devolve_a_resistencia(self):
        assert IoT["divisor"](1023 / 2) == pytest.approx(10000, rel=0.01)

    def test_media_movel_suaviza_e_esquece(self):
        media = IoT["media_movel"](3)
        assert media(10) == 10
        assert media(20) == 15
        assert media(30) == 20
        assert media(40) == 30          # o 10 saiu da janela

    def test_histerese_nao_bate_o_rele(self):
        termostato = IoT["histerese"](30, 28)
        assert termostato(29) is False   # subindo, ainda não
        assert termostato(31) is True
        assert termostato(29) is True    # no meio, segura o estado
        assert termostato(27) is False

    def test_histerese_invertida_para_resfriar(self):
        umidificador = IoT["histerese"](40, 50)   # liga abaixo de 40
        assert umidificador(45) is False
        assert umidificador(35) is True
        assert umidificador(45) is True
        assert umidificador(55) is False

    def test_duas_soleiras_iguais_sao_uma_so(self):
        with pytest.raises(Exception, match="soleira so"):
            IoT["histerese"](30, 30)


# ═══════════════════════════════════════════════════════════
#  Sketch
# ═══════════════════════════════════════════════════════════

class TestSketch:
    def test_o_arquivo_tem_o_nome_da_pasta(self, tmp_path):
        """Um .ino solto não compila, e o erro não diz por quê."""
        caminho = IoT["gravar_sketch"](str(tmp_path), "pisca")
        assert caminho.endswith(os.path.join("pisca", "pisca.ino"))
        assert os.path.isfile(caminho)

    def test_as_opcoes_entram_no_codigo(self):
        codigo = IoT["sketch"]("pisca", {"led": 7, "intervalo": 120})
        assert "const int LED = 7;" in codigo
        assert "INTERVALO = 120" in codigo

    def test_opcao_desconhecida_e_recusada(self):
        """`opcoes.ler` recusa o erro de digitação em vez de ignorá-lo."""
        with pytest.raises(Exception):
            IoT["sketch"]("pisca", {"lde": 7})

    def test_sketch_que_nao_existe_lista_os_que_existem(self):
        with pytest.raises(Exception, match="nao conheco o sketch"):
            IoT["sketch"]("teletransporte")

    def test_todos_os_modelos_geram_codigo_com_setup_e_loop(self):
        for nome in IoT["sketches"]():
            codigo = IoT["sketch"](nome)
            assert "void setup()" in codigo and "void loop()" in codigo
            assert "{" + "led" + "}" not in codigo     # nada por substituir

    def test_o_firmata_gerado_fala_a_velocidade_certa(self):
        """57600 é a que o cliente abre por padrão; 9600 não conversa."""
        assert "Serial.begin(57600)" in IoT["sketch"]("firmata")

    def test_o_firmata_NAO_depende_da_biblioteca_Firmata(self):
        """A biblioteca para nas placas de até 2018, e isso não é detalhe.

        `Firmata.h` traz um `Boards.h` com a tabela de pinos de cada
        placa, escrita à mão. Num **Arduino UNO R4 WiFi** ela responde
        `#error "Please edit Boards.h with a hardware abstraction for
        this board"`, e num **ESP32** também — as duas placas mais
        vendidas de hoje, e as duas que estavam na mesa quando isto foi
        escrito. Como `IoT.conectar` só fala Firmata, o módulo inteiro
        era inalcançável nelas: o sketch não compilava, e a mensagem
        falava de um arquivo de uma biblioteca de terceiro.

        Medido depois da correção: compila para `arduino:avr:uno`,
        `arduino:avr:mega`, `arduino:renesas_uno:unor4wifi` e
        `esp32:esp32:esp32`, e as duas placas de verdade responderam.
        """
        codigo = IoT["sketch"]("firmata")
        assert "#include <Firmata.h>" not in codigo, (
            "voltou a depender da biblioteca que não conhece R4 nem ESP32")
        assert "Firmata." not in codigo

    def test_o_firmata_gerado_responde_TUDO_que_o_cliente_pergunta(self):
        """O handshake tem quatro perguntas, e falhar uma trava a conexão.

        `Placa.apresentar` pede versão, firmware, capacidades e o mapa
        analógico, **e espera por cada uma**. O sketch antigo só tratava
        `ANALOG_MESSAGE`: ele compilava, gravava, a placa acendia — e
        `IoT.conectar` morria em "a placa nao respondeu quem e".

        A lista vem dos nomes do próprio cliente, e não de uma cópia:
        acrescentar uma pergunta lá sem responder aqui reprova este
        teste em vez de virar um travamento na bancada.
        """
        from dataforge.stdlib import iot_firmata as proto

        codigo = IoT["sketch"]("firmata")
        exigidas = {
            "REPORT_VERSION": proto.PROTOCOL_VERSION,
            "REPORT_FIRMWARE": proto.REPORT_FIRMWARE,
            "CAPABILITY_QUERY": proto.CAPABILITY_QUERY,
            "ANALOG_MAPPING_QUERY": proto.ANALOG_MAPPING_QUERY,
            "PIN_STATE_QUERY": proto.PIN_STATE_QUERY,
            "SET_PIN_MODE": proto.SET_PIN_MODE,
            "DIGITAL_MESSAGE": proto.DIGITAL_MESSAGE,
            "ANALOG_MESSAGE": proto.ANALOG_MESSAGE,
            "REPORT_ANALOG": proto.REPORT_ANALOG,
            "REPORT_DIGITAL": proto.REPORT_DIGITAL,
            "SAMPLING_INTERVAL": proto.SAMPLING_INTERVAL,
        }
        # O 'x' do '0x' e minusculo nos dois lados: um 'codigo.upper()'
        # aqui transformaria '0xF9' em '0XF9' e daria TUDO por faltando —
        # foi o primeiro jeito que escrevi, e ele reprovava um firmware
        # correto, que e a pior direcao para uma trava errar.
        faltando = [nome for nome, valor in exigidas.items()
                    if f"0x{valor:02X}" not in codigo
                    and f"0x{valor:02x}" not in codigo]
        assert not faltando, (
            "o firmware não conhece o que o cliente manda: "
            + ", ".join(faltando))

    def test_o_firmata_nao_escreve_tabela_de_pino_nenhuma(self):
        """O mapa sai do core, como o do cliente sai da placa.

        Uma tabela escrita aqui envelheceria na primeira placa nova — é
        a mesma decisão que faz `modo(13, "pwm")` ser recusado **pela
        placa** e não por uma lista. `NUM_DIGITAL_PINS`,
        `digitalPinHasPWM` e `analogInputToDigitalPin` são macros que
        todo core define, e cada uma tem recuo para quem não a define:
        o UNO R4 não traz `analogInputToDigitalPin`, e sem o recuo por
        `PIN_A0` ele relatava **zero** entradas analógicas tendo seis.
        """
        codigo = IoT["sketch"]("firmata")
        for macro in ("NUM_DIGITAL_PINS", "NUM_ANALOG_INPUTS",
                      "digitalPinHasPWM", "analogInputToDigitalPin",
                      "PIN_A0"):
            assert macro in codigo, f"o firmware deixou de perguntar {macro}"


@pytest.mark.skipif(not IoT["tem_arduino_cli"](),
                    reason="o arduino-cli não está instalado")
def test_o_arduino_cli_responde():
    nucleos = IoT["nucleos"]()
    assert isinstance(nucleos, list)


@pytest.mark.skipif(os.environ.get("DATAFORGE_ARDUINO_COMPILAR") != "1",
                    reason="compilar leva ~40 s: DATAFORGE_ARDUINO_COMPILAR=1 liga")
def test_o_sketch_gerado_compila_de_verdade(tmp_path):
    """A prova que o simulador não dá: o C++ gerado passa pelo compilador."""
    fqbn = os.environ.get("DATAFORGE_ARDUINO_FQBN", "arduino:avr:uno")
    pasta = os.path.dirname(IoT["gravar_sketch"](str(tmp_path), "pisca"))
    resultado = IoT["compilar"](pasta, fqbn)
    assert resultado["ok"], resultado["erro"]


@pytest.mark.skipif(os.environ.get("DATAFORGE_ARDUINO_COMPILAR") != "1",
                    reason="compilar leva ~40 s: DATAFORGE_ARDUINO_COMPILAR=1 liga")
def test_o_firmata_compila_em_TODO_core_instalado(tmp_path):
    """Um firmware que só compila numa arquitetura não é portátil.

    O alvo não é uma lista escrita aqui: são os cores que a máquina
    **tem**. Numa máquina com `avr`, `renesas_uno` e `esp32` ele cobre
    as três famílias que importam hoje; numa com um core só, cobre uma
    — e nunca reprova por um core que ninguém instalou.
    """
    familias = {"arduino:avr": "arduino:avr:uno",
                "arduino:renesas_uno": "arduino:renesas_uno:unor4wifi",
                "esp32:esp32": "esp32:esp32:esp32",
                "esp8266:esp8266": "esp8266:esp8266:nodemcuv2",
                "arduino:samd": "arduino:samd:nano_33_iot"}
    instalados = {c["id"] for c in IoT["nucleos"]()}
    alvos = [f for core, f in familias.items() if core in instalados]
    if not alvos:
        pytest.skip("nenhum core conhecido instalado")

    pasta = os.path.dirname(IoT["gravar_sketch"](str(tmp_path), "firmata"))
    falhas = []
    for fqbn in alvos:
        resultado = IoT["compilar"](pasta, fqbn)
        if not resultado["ok"]:
            falhas.append(f"{fqbn}: {resultado['erro'].strip().splitlines()[0][:120]}")
    assert not falhas, "o firmware não compila em:\n  " + "\n  ".join(falhas)


# ═══════════════════════════════════════════════════════════
#  MQTT, contra um broker mínimo
# ═══════════════════════════════════════════════════════════

class BrokerDeTeste:
    """O pedaço do MQTT que um teste precisa: CONNECT, SUBSCRIBE, PUBLISH.

    Ele existe porque testar um cliente só com dublê não prova nada
    sobre o que acontece no fio — é a mesma razão de `tests/test_malha.py`
    subir um servidor de verdade.
    """

    def __init__(self):
        self.soquete = socket.socket()
        self.soquete.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soquete.bind(("127.0.0.1", 0))
        self.soquete.listen(4)
        self.porta = self.soquete.getsockname()[1]
        self.publicados = []
        self.assinaturas = []
        self.clientes = []
        self.vivo = True
        threading.Thread(target=self._aceitar, daemon=True).start()

    def _aceitar(self):
        while self.vivo:
            try:
                cliente, _ = self.soquete.accept()
            except OSError:
                return
            self.clientes.append(cliente)
            threading.Thread(target=self._atender, args=(cliente,),
                             daemon=True).start()

    def _atender(self, cliente):
        buffer = bytearray()
        cliente.settimeout(0.2)
        while self.vivo:
            try:
                pedaco = cliente.recv(4096)
                if not pedaco:
                    return
                buffer.extend(pedaco)
            except socket.timeout:
                continue
            except OSError:
                return
            while len(buffer) >= 2:
                tamanho, desloc, mult = 0, 1, 1
                while True:
                    if desloc >= len(buffer):
                        tamanho = -1
                        break
                    byte = buffer[desloc]
                    tamanho += (byte & 0x7F) * mult
                    desloc += 1
                    if not byte & 0x80:
                        break
                    mult *= 128
                if tamanho < 0 or len(buffer) < desloc + tamanho:
                    break
                cabeca = buffer[0]
                corpo = bytes(buffer[desloc:desloc + tamanho])
                del buffer[:desloc + tamanho]
                self._tratar(cliente, cabeca >> 4, cabeca & 0x0F, corpo)

    def _tratar(self, cliente, tipo, bandeiras, corpo):
        if tipo == 1:                                   # CONNECT
            cliente.sendall(bytes([0x20, 2, 0, 0]))
        elif tipo == 8:                                 # SUBSCRIBE
            identificador = struct.unpack(">H", corpo[:2])[0]
            tam = struct.unpack(">H", corpo[2:4])[0]
            filtro = corpo[4:4 + tam].decode()
            self.assinaturas.append((cliente, filtro))
            cliente.sendall(bytes([0x90, 3]) + struct.pack(">H", identificador)
                            + bytes([0]))
        elif tipo == 3:                                 # PUBLISH
            tam = struct.unpack(">H", corpo[:2])[0]
            topico = corpo[2:2 + tam].decode()
            resto = corpo[2 + tam:]
            qos = (bandeiras >> 1) & 3
            if qos:
                identificador = struct.unpack(">H", resto[:2])[0]
                resto = resto[2:]
                cliente.sendall(bytes([0x40, 2]) + struct.pack(">H", identificador))
            self.publicados.append((topico, resto.decode()))
            self.entregar(topico, resto.decode())
        elif tipo == 12:                                # PINGREQ
            cliente.sendall(bytes([0xD0, 0]))

    def entregar(self, topico, mensagem):
        """Manda a mensagem a quem assinou um filtro que casa."""
        from dataforge.stdlib.iot_mqtt import _casa
        corpo = (struct.pack(">H", len(topico)) + topico.encode()
                 + mensagem.encode())
        for cliente, filtro in list(self.assinaturas):
            if _casa(filtro, topico):
                try:
                    cliente.sendall(bytes([0x30, len(corpo)]) + corpo)
                except OSError:                          # pragma: no cover
                    pass

    def fechar(self):
        self.vivo = False
        self.soquete.close()


@pytest.fixture()
def broker():
    b = BrokerDeTeste()
    yield b
    b.fechar()


class TestMqtt:
    def test_conecta_publica_e_o_broker_recebe(self, broker):
        c = IoT["mqtt"]("127.0.0.1", broker.porta, cliente="teste")
        c.publicar("casa/sala/temperatura", "21.5")
        prazo = time.monotonic() + 2
        while not broker.publicados and time.monotonic() < prazo:
            time.sleep(0.01)
        assert broker.publicados == [("casa/sala/temperatura", "21.5")]
        c.fechar()

    def test_assina_e_recebe_pela_acao(self, broker):
        c = IoT["mqtt"]("127.0.0.1", broker.porta)
        recebidas = []
        c.assinar("casa/+/temperatura", recebidas.append)
        time.sleep(0.15)
        broker.entregar("casa/quarto/temperatura", "19.2")
        prazo = time.monotonic() + 2
        while not recebidas and time.monotonic() < prazo:
            time.sleep(0.01)
        assert recebidas[0]["topico"] == "casa/quarto/temperatura"
        assert recebidas[0]["mensagem"] == "19.2"
        c.fechar()

    def test_qos_1_espera_o_puback(self, broker):
        c = IoT["mqtt"]("127.0.0.1", broker.porta)
        assert isinstance(c.publicar("t", "x", qos=1), int)
        c.fechar()

    def test_publicar_num_curinga_e_recusado(self, broker):
        c = IoT["mqtt"]("127.0.0.1", broker.porta)
        with pytest.raises(Exception, match="nao serve para publicar") as info:
            c.publicar("casa/+/luz", "on")
        assert "curingas de ASSINATURA" in info.value.nota
        c.fechar()

    def test_fechar_e_idempotente(self, broker):
        c = IoT["mqtt"]("127.0.0.1", broker.porta)
        assert c.fechar() is True
        assert c.fechar() is False

    def test_broker_que_nao_existe_diz_o_que_fazer(self):
        with pytest.raises(Exception) as info:
            IoT["mqtt"]("127.0.0.1", 1, prazo=1)
        assert "mosquitto" in info.value.dica

    @pytest.mark.parametrize("filtro,topico,casa", [
        ("casa/sala/luz", "casa/sala/luz", True),
        ("casa/+/luz", "casa/sala/luz", True),
        ("casa/+/luz", "casa/sala/piso/luz", False),
        ("casa/#", "casa/sala/piso/luz", True),
        ("casa/#", "jardim/luz", False),
        ("casa/sala", "casa/sala/luz", False),
    ])
    def test_os_curingas_seguem_a_norma(self, filtro, topico, casa):
        from dataforge.stdlib.iot_mqtt import _casa
        assert _casa(filtro, topico) is casa


# ═══════════════════════════════════════════════════════════
#  Pela linguagem
# ═══════════════════════════════════════════════════════════

def test_o_caminho_inteiro_pela_linguagem(tmp_path):
    r = rodar(tmp_path, '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")
placa.escrever(13, yes)
assert placa.simulador.pino(13) is 1

placa.modo(14, "analogico")
placa.relatar_analogico(0)
placa.simulador.definir_analogico(0, 1023)
sleep(80)
assert IoT.escala(placa.analogico(0), 0, 1023, 0, 100) is 100.0

placa.fechar()
out "ok"
''')
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "ok"


# ═══════════════════════════════════════════════════════════
#  Com placa de verdade
# ═══════════════════════════════════════════════════════════

@pytest.mark.skipif(not os.environ.get("DATAFORGE_ARDUINO"),
                    reason="DATAFORGE_ARDUINO=/dev/cu.usbmodem… liga o teste "
                           "com placa de verdade (o firmware gravado)")
def test_com_placa_de_verdade():
    """O que o simulador não prova: o cabo, o bootloader, o sketch.

    Ligue o LED do pino 13 e rode:

        DATAFORGE_ARDUINO=/dev/cu.usbmodem1101 python3 -m pytest tests/test_iot.py -k verdade
    """
    porta = os.environ["DATAFORGE_ARDUINO"]
    placa = IoT["conectar"](porta, prazo=8.0)
    try:
        info = placa.info()
        assert info["firmware"]["nome"], "a placa não disse quem é"
        assert info["pinos"] > 0
        # O firmware gravado por 'IoT.carregar("firmata")' diz o nome.
        if info["firmware"]["nome"] == "DataForge":
            assert info["placa"], "o firmware atual responde o nome da placa"
        # O pino e o canal saem da PLACA: o teste supunha o mapa do UNO
        # (A0 = pino 14) e reprovava num ESP32, onde o A0 é o GPIO 36.
        led = 13 if "saida" in placa.capacidades(13) else next(
            int(p) for p, modos in placa.capacidades().items() if "saida" in modos)
        placa.modo(led, "saida")
        for _ in range(3):
            placa.escrever(led, True)
            time.sleep(0.25)
            placa.escrever(led, False)
            time.sleep(0.25)
        assert 0 <= placa.ler_analogico(0) <= 1023
    finally:
        placa.fechar()


# ═══════════════════════════════════════════════════════════
#  A placa diz o próprio nome, e os pinos que não pode usar
# ═══════════════════════════════════════════════════════════

import dataforge.stdlib.arcane_iot as _iot_mod  # noqa: E402
from dataforge.stdlib import iot_firmata as _firmata  # noqa: E402

#: O que `arduino-cli board list --format json` respondeu NESTA mesa, com
#: um UNO R4 e um ESP32 atrás de uma ponte CH340. O teste usa a resposta
#: de verdade, e não um formato imaginado.
_BOARD_LIST_REAL = {"detected_ports": [
    {"port": {"address": "/dev/cu.Bluetooth-Incoming-Port",
              "protocol": "serial", "properties": {}}},
    {"port": {"address": "/dev/cu.usbserial-1110", "protocol": "serial",
              "properties": {"pid": "0x7523", "serialNumber": "", "vid": "0x1A86"}}},
    {"port": {"address": "/dev/cu.usbmodemC04E301234D42", "protocol": "serial",
              "properties": {"manufacturer": "Arduino", "pid": "0x1002",
                             "product": "UNO WiFi R4 CMSIS-DAP", "vid": "0x2341"}},
     "matching_boards": [{"name": "Arduino UNO R4 WiFi",
                          "fqbn": "arduino:renesas_uno:unor4wifi"}]},
    {"port": {"address": "/dev/cu.debug-console", "protocol": "serial",
              "properties": {}}},
]}


@pytest.fixture()
def duas_placas(monkeypatch):
    """Duas placas na mesa, sem placa nenhuma: o arduino-cli respondendo o
    que respondeu de verdade, e as portas que o sistema lista."""
    import json as _json
    chamadas = []

    def rodar_falso(argumentos, prazo=None):
        chamadas.append(list(argumentos))
        if argumentos[:2] == ["board", "list"]:
            return {"ok": True, "saida": _json.dumps(_BOARD_LIST_REAL), "erro": ""}
        return {"ok": True, "saida": "gravado", "erro": ""}

    monkeypatch.setattr(_iot_mod, "_rodar", rodar_falso)
    monkeypatch.setattr(_iot_mod, "tem_arduino_cli", lambda: True)
    monkeypatch.setattr(_iot_mod, "portas", lambda: [
        {"porta": "/dev/cu.usbmodemC04E301234D42", "descricao": "USB nativo"},
        {"porta": "/dev/cu.usbserial-1110", "descricao": "conversor USB-serial"}])
    return chamadas


@pytest.mark.parametrize("modelo,nome", [
    ("uno", "Arduino UNO"), ("mega", "Arduino Mega 2560"),
    ("uno-r4", "Arduino UNO R4 WiFi"), ("esp32", "ESP32")])
def test_a_placa_diz_o_proprio_nome(modelo, nome):
    """O mesmo nome que o firmware de verdade responde ('nomeDaPlaca')."""
    p = IoT["conectar_simulada"](modelo)
    try:
        assert p.info()["placa"] == nome
    finally:
        p.fechar()


def test_um_firmware_que_nao_sabe_o_nome_nao_trava_nem_quebra():
    """O StandardFirmata e um DataForge antigo não respondem à pergunta. O
    silêncio é "não sei" — e o handshake não espera por ele."""
    class Antigo(Simulador):
        def _tratar_sysex(self, corpo):
            if corpo and corpo[0] == _firmata.PLACA_QUERY:
                return
            super()._tratar_sysex(corpo)

    sim = Antigo("uno")
    p = Placa(sim, nome="antiga", prazo=2.0)
    inicio = time.monotonic()
    p.apresentar()
    assert time.monotonic() - inicio < 1.0
    assert p.info()["placa"] is None
    p.fechar()


def test_o_esp32_nao_oferece_os_pinos_da_flash():
    """GPIO 6 a 11 são a flash SPI do módulo: configurar um derruba a placa."""
    p = IoT["conectar_simulada"]("esp32")
    try:
        for pino in range(6, 12):
            assert p.capacidades(pino) == []
        with pytest.raises(Exception) as erro:
            p.modo(9, "pwm")
        assert "flash" in erro.value.dica
    finally:
        p.fechar()


def test_os_pinos_so_de_entrada_do_esp32_recusam_saida():
    p = IoT["conectar_simulada"]("esp32")
    try:
        for pino in range(34, 40):
            assert p.capacidades(pino) == ["entrada"]
        with pytest.raises(Exception, match="nao faz 'saida'"):
            p.modo(35, "saida")
        p.modo(35, "entrada")                 # ler continua podendo
    finally:
        p.fechar()


def test_a_dica_de_modo_sai_da_placa_e_nao_de_uma_tabela():
    """Ela dizia "num Arduino UNO, PWM só nos pinos 3, 5, 6, 9, 10 e 11"
    para qualquer placa — inclusive um ESP32."""
    p = IoT["conectar_simulada"]("uno")
    try:
        with pytest.raises(Exception) as erro:
            p.modo(4, "pwm")
        assert erro.value.dica == "nesta placa, 'pwm' funciona nos pinos: 3, 5-6, 9-11"
    finally:
        p.fechar()


def test_o_firmware_protege_o_esp32_e_responde_o_nome():
    codigo = IoT["sketch"]("firmata")
    assert "bool pinoReservado" in codigo and "pino >= 6 && pino <= 11" in codigo
    assert "GPIO_IS_VALID_OUTPUT_GPIO" in codigo
    assert f"0x{_firmata.PLACA_QUERY:02X}" in codigo
    assert "responderPlaca" in codigo


def test_placas_separa_usb_do_resto(duas_placas):
    vistas = {p["porta"]: p for p in IoT["placas"]()}
    assert vistas["/dev/cu.Bluetooth-Incoming-Port"]["usb"] == ""
    assert vistas["/dev/cu.debug-console"]["usb"] == ""
    assert "CH340" in vistas["/dev/cu.usbserial-1110"]["usb"]
    assert "1A86:7523" in vistas["/dev/cu.usbserial-1110"]["usb"]
    assert vistas["/dev/cu.usbmodemC04E301234D42"]["placa"] == "Arduino UNO R4 WiFi"


def test_a_porta_e_achada_pelo_nome_da_placa(duas_placas):
    assert _iot_mod._resolver_porta("uno r4") == "/dev/cu.usbmodemC04E301234D42"
    assert _iot_mod._resolver_porta("UNO-R4") == "/dev/cu.usbmodemC04E301234D42"
    # um caminho passa direto, sem consultar nada
    assert _iot_mod._resolver_porta("/dev/cu.x") == "/dev/cu.x"
    assert _iot_mod._resolver_porta("COM3") == "COM3"


def test_o_nome_que_a_ponte_nao_revela_e_recusado_sem_chute(duas_placas):
    """Uma ponte CH340 serve a um clone de UNO e a um ESP32: o USB não diz
    que chip está atrás dela, e a busca não finge que sabe."""
    with pytest.raises(Exception) as erro:
        _iot_mod._resolver_porta("esp32")
    assert "nenhuma porta se identifica" in erro.value.message
    assert 'IoT.conectar("/dev/cu.usbserial-1110")' in erro.value.dica


def test_duas_placas_a_dica_mostra_as_portas_que_existem(duas_placas):
    """A dica mostrava um caminho inventado ('/dev/cu.usbmodem1101')."""
    with pytest.raises(Exception) as erro:
        _iot_mod._unica_porta()
    dica = erro.value.dica
    assert 'IoT.conectar("/dev/cu.usbmodemC04E301234D42")   // Arduino UNO R4 WiFi' in dica
    assert "/dev/cu.usbserial-1110" in dica
    assert "usbmodem1101" not in dica
    assert "Bluetooth" not in dica


def test_carregar_descobre_o_fqbn_pela_porta(duas_placas):
    IoT["carregar"]("/tmp/sketch", "/dev/cu.usbmodemC04E301234D42")
    gravacao = [c for c in duas_placas if c[:1] == ["compile"]][-1]
    assert gravacao[gravacao.index("--fqbn") + 1] == "arduino:renesas_uno:unor4wifi"


def test_carregar_recusa_a_porta_que_nao_se_identifica(duas_placas):
    """O padrão era arduino:avr:uno: gravar num UNO R4 sem --fqbn mandava o
    binário do UNO clássico para a placa errada."""
    with pytest.raises(Exception) as erro:
        IoT["carregar"]("/tmp/sketch", "/dev/cu.usbserial-1110")
    assert "nao sei que placa" in erro.value.message
    assert "--fqbn=esp32:esp32:esp32" in erro.value.dica
    assert not [c for c in duas_placas if c[:1] == ["compile"]]


def test_carregar_aceita_o_nome_de_um_modelo(duas_placas, tmp_path, monkeypatch):
    monkeypatch.setattr("tempfile.mkdtemp", lambda prefix="": str(tmp_path))
    IoT["carregar"]("firmata", "uno r4")
    gravacao = [c for c in duas_placas if c[:1] == ["compile"]][-1]
    assert gravacao[-1].endswith("firmata")
    assert (tmp_path / "firmata" / "firmata.ino").is_file()


def test_o_doctor_nao_lista_bluetooth_como_placa(duas_placas, monkeypatch):
    monkeypatch.setattr(_iot_mod, "conectar", lambda alvo, prazo=4.0: (_ for _ in ()).throw(
        RuntimeError("sem firmware")))
    linhas = {a["o_que"]: a for a in IoT["doctor"]() if a["o_que"] != "Firmata"}
    detalhe = linhas["placas reconhecidas"]["detalhe"]
    assert "Bluetooth" not in detalhe and "debug-console" not in detalhe
    assert "Arduino UNO R4 WiFi" in detalhe and "CH340" in detalhe
    firmatas = [a for a in IoT["doctor"]() if a["o_que"] == "Firmata"]
    assert len(firmatas) == 2, "cada placa é conferida, e não só a primeira"


def test_pino_do_canal_vem_do_mapa_da_placa():
    uno = IoT["conectar_simulada"]("uno")
    try:
        assert uno.pino_do_canal(0) == 14
        with pytest.raises(Exception, match="canal analogico 9"):
            uno.pino_do_canal(9)
    finally:
        uno.fechar()


def test_ler_analogico_espera_a_primeira_amostra_de_verdade():
    """Sem 'relatar_analogico', 'analogico(0)' devolve zero, calado — a
    armadilha número 1 do Firmata. 'ler_analogico' liga tudo e só volta
    quando uma amostra chegou."""
    p = IoT["conectar_simulada"]("uno")
    try:
        p.simulador.definir_analogico(0, 512)
        assert p.analogico(0) == 0           # a armadilha: nada foi pedido
        assert p.ler_analogico(0) == 512
    finally:
        p.fechar()


def test_ler_analogico_sem_resposta_diz_quanto_esperou():
    p = IoT["conectar_simulada"]("uno")
    try:
        p.simulador.relatar = lambda *a, **k: None
        original = p._mandar
        p._mandar = lambda dados: None if dados and dados[0] & 0xF0 == 0xC0 else original(dados)
        with pytest.raises(Exception, match="em 0.2 s"):
            p.ler_analogico(0, prazo=0.2)
    finally:
        p.fechar()
