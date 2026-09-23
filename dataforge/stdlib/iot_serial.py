# -*- coding: utf-8 -*-
"""A porta serial, escrita à mão — sem pyserial.

A linguagem não tem dependência externa em tempo de execução, e isso
vale para falar com uma placa. São três sistemas e dois caminhos:

| Sistema | Como |
|---|---|
| macOS, Linux | `os.open` + `termios` (raw, sem eco, sem canônico) e `select` |
| Windows | `ctypes` sobre a `kernel32`: `CreateFileW`, `DCB`, `COMMTIMEOUTS` |

O que **não** está aqui, e é de propósito: controle de fluxo por
hardware (RTS/CTS), paridade diferente de "nenhuma" e 7 bits de dados.
Toda placa Arduino conversa em 8N1 sem controle de fluxo, e cada opção
a mais seria um caminho sem teste.
"""

import glob
import os
import sys
import threading
import time

from ..errors import RuntimeError_

_DOC = "iot/serial"

#: As velocidades que uma placa usa. 115200 é o do Firmata; 9600 é o
#: padrão histórico dos exemplos do Arduino IDE.
VELOCIDADES = (300, 1200, 2400, 4800, 9600, 19200, 38400, 57600,
               74880, 115200, 230400, 250000, 500000, 1000000, 2000000)


def _erro(mensagem, nota="", dica=""):
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


# ═══════════════════════════════════════════════════════════
#  Achar as portas
# ═══════════════════════════════════════════════════════════

#: Os padrões de nome de uma porta USB-serial em cada sistema.
#:
#: No macOS existem DOIS arquivos para a mesma porta: `/dev/tty.*`
#: (entrada, espera o DCD) e `/dev/cu.*` (saída, não espera). Abrir o
#: `tty.` de um Arduino bloqueia até a placa levantar o sinal — e com
#: alguns clones isso nunca acontece. O `cu.` é o certo, e é por isso
#: que ele vem primeiro na lista.
_PADROES = {
    "darwin": ("/dev/cu.usbmodem*", "/dev/cu.usbserial*", "/dev/cu.wchusbserial*",
               "/dev/cu.SLAB_USBtoUART*"),
    "linux": ("/dev/ttyACM*", "/dev/ttyUSB*", "/dev/serial/by-id/*"),
}


def portas():
    """As portas seriais visíveis, como vault com nome e descrição.

    Não abre nenhuma: listar não pode ter efeito. Abrir uma porta
    reinicia a placa (o DTR), e um `IoT.portas()` que reiniciasse todos
    os Arduinos da mesa seria uma surpresa cara.
    """
    achadas = []
    if sys.platform.startswith("win"):
        achadas = [{"porta": f"COM{n}", "descricao": "porta serial do Windows"}
                   for n in _portas_do_windows()]
    else:
        chave = "darwin" if sys.platform == "darwin" else "linux"
        vistos = set()
        for padrao in _PADROES[chave]:
            for caminho in sorted(glob.glob(padrao)):
                real = os.path.realpath(caminho)
                if real in vistos:
                    continue
                vistos.add(real)
                achadas.append({"porta": caminho,
                                "descricao": _descricao_posix(caminho)})
    return achadas


def _descricao_posix(caminho):
    nome = os.path.basename(caminho)
    if "usbmodem" in nome or "ttyACM" in nome:
        return "placa com USB nativo (UNO R4, Leonardo, Micro, ESP32-S3)"
    if "wchusbserial" in nome or "SLAB" in nome:
        return "conversor USB-serial (clone de UNO, ESP32, ESP8266)"
    if "usbserial" in nome or "ttyUSB" in nome:
        return "conversor USB-serial (FTDI, CH340, CP2102)"
    return "porta serial"


def _portas_do_windows():
    """Os números de COM que o registro conhece.

    Sondar de COM1 a COM64 abrindo cada uma seria o outro caminho — e
    abrir reinicia a placa. O registro responde sem tocar em nada.
    """
    try:
        import winreg                                   # noqa: WPS433
    except ImportError:                                  # pragma: no cover
        return []
    numeros = []
    try:
        chave = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"HARDWARE\DEVICEMAP\SERIALCOMM")
    except OSError:                                      # pragma: no cover
        return []
    with chave:
        i = 0
        while True:
            try:
                _nome, valor, _tipo = winreg.EnumValue(chave, i)
            except OSError:
                break
            if str(valor).upper().startswith("COM"):
                try:
                    numeros.append(int(str(valor)[3:]))
                except ValueError:                       # pragma: no cover
                    pass
            i += 1
    return sorted(numeros)


# ═══════════════════════════════════════════════════════════
#  A porta
# ═══════════════════════════════════════════════════════════

class Serial:
    """Uma porta serial aberta. 8 bits, sem paridade, 1 stop — 8N1."""

    def __init__(self, porta, velocidade=115200, prazo=1.0):
        self.porta = str(porta)
        self.velocidade = int(velocidade)
        self.prazo = float(prazo)
        self._trava = threading.RLock()
        self._aberta = False
        self._fd = None
        self._win = None
        if self.velocidade not in VELOCIDADES:
            raise _erro(
                f"{self.velocidade} nao e uma velocidade de porta serial.",
                nota=f"as usuais: {', '.join(str(v) for v in VELOCIDADES[:10])}",
                dica="o Firmata fala a 57600; os exemplos do Arduino, a 9600")
        if sys.platform.startswith("win"):
            self._abrir_windows()
        else:
            self._abrir_posix()
        self._aberta = True

    # ── POSIX ────────────────────────────────────────────────

    def _abrir_posix(self):
        import termios
        try:
            fd = os.open(self.porta, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        except FileNotFoundError:
            raise _erro(
                f"a porta '{self.porta}' nao existe.",
                nota="uma placa desconectada some do /dev na hora",
                dica="IoT.portas() lista as que existem agora") from None
        except PermissionError:
            raise _erro(
                f"sem permissao para abrir '{self.porta}'.",
                nota="no Linux a porta pertence ao grupo 'dialout'",
                dica="sudo usermod -aG dialout $USER — e entre de novo") from None
        except OSError as erro:
            raise _erro(f"nao consegui abrir '{self.porta}': {erro}") from None

        try:
            atual = termios.tcgetattr(fd)
        except termios.error as erro:                    # pragma: no cover
            os.close(fd)
            raise _erro(f"'{self.porta}' nao e uma porta serial: {erro}") from None

        iflag, oflag, cflag, lflag, ispeed, ospeed, cc = atual
        velocidade = getattr(termios, f"B{self.velocidade}", None)
        if velocidade is None:                           # pragma: no cover
            os.close(fd)
            raise _erro(f"este sistema nao tem a velocidade {self.velocidade}.")

        # RAW: sem tradução de \r\n, sem eco, sem modo canônico. O modo
        # canônico entrega por LINHA, e um protocolo binário como o
        # Firmata não tem linhas — ele travaria esperando um '\n' que
        # nunca vem.
        iflag &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                   | termios.ISTRIP | termios.INLCR | termios.IGNCR
                   | termios.ICRNL | termios.IXON)
        oflag &= ~termios.OPOST
        lflag &= ~(termios.ECHO | termios.ECHONL | termios.ICANON
                   | termios.ISIG | termios.IEXTEN)
        cflag &= ~(termios.CSIZE | termios.PARENB | termios.CSTOPB)
        cflag |= termios.CS8 | termios.CREAD | termios.CLOCAL
        cc = list(cc)
        cc[termios.VMIN] = 0
        cc[termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW,
                          [iflag, oflag, cflag, lflag, velocidade, velocidade, cc])
        termios.tcflush(fd, termios.TCIOFLUSH)
        self._fd = fd

    # ── Windows ──────────────────────────────────────────────

    def _abrir_windows(self):                            # pragma: no cover
        import ctypes
        from ctypes import wintypes

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        nome = self.porta if self.porta.startswith("\\\\") else f"\\\\.\\{self.porta}"
        GENERIC = 0x80000000 | 0x40000000
        handle = k32.CreateFileW(nome, GENERIC, 0, None, 3, 0, None)
        if handle == ctypes.c_void_p(-1).value:
            raise _erro(f"nao consegui abrir '{self.porta}' "
                        f"(erro {ctypes.get_last_error()}).",
                        dica="feche o monitor serial do Arduino IDE: "
                             "a porta e exclusiva no Windows")

        class DCB(ctypes.Structure):
            _fields_ = [("DCBlength", wintypes.DWORD), ("BaudRate", wintypes.DWORD),
                        ("fBits", wintypes.DWORD), ("wReserved", wintypes.WORD),
                        ("XonLim", wintypes.WORD), ("XoffLim", wintypes.WORD),
                        ("ByteSize", ctypes.c_byte), ("Parity", ctypes.c_byte),
                        ("StopBits", ctypes.c_byte), ("XonChar", ctypes.c_char),
                        ("XoffChar", ctypes.c_char), ("ErrorChar", ctypes.c_char),
                        ("EofChar", ctypes.c_char), ("EvtChar", ctypes.c_char),
                        ("wReserved1", wintypes.WORD)]

        class TIMEOUTS(ctypes.Structure):
            _fields_ = [("ReadIntervalTimeout", wintypes.DWORD),
                        ("ReadTotalTimeoutMultiplier", wintypes.DWORD),
                        ("ReadTotalTimeoutConstant", wintypes.DWORD),
                        ("WriteTotalTimeoutMultiplier", wintypes.DWORD),
                        ("WriteTotalTimeoutConstant", wintypes.DWORD)]

        dcb = DCB()
        dcb.DCBlength = ctypes.sizeof(DCB)
        if not k32.GetCommState(handle, ctypes.byref(dcb)):
            k32.CloseHandle(handle)
            raise _erro(f"'{self.porta}' nao e uma porta serial.")
        dcb.BaudRate = self.velocidade
        dcb.ByteSize = 8
        dcb.Parity = 0
        dcb.StopBits = 0
        dcb.fBits = 1            # fBinary, sem paridade e sem controle de fluxo
        k32.SetCommState(handle, ctypes.byref(dcb))

        # Leitura que NAO bloqueia: devolve o que houver. Quem espera é
        # `ler`, com o prazo desta classe — assim POSIX e Windows têm o
        # mesmo comportamento, e não dois.
        t = TIMEOUTS(ReadIntervalTimeout=0xFFFFFFFF,
                     ReadTotalTimeoutMultiplier=0, ReadTotalTimeoutConstant=0,
                     WriteTotalTimeoutMultiplier=0, WriteTotalTimeoutConstant=2000)
        k32.SetCommTimeouts(handle, ctypes.byref(t))
        self._win = (k32, handle, ctypes)

    # ── ler e escrever ───────────────────────────────────────

    def _exigir_aberta(self):
        if not self._aberta:
            raise _erro("esta porta ja foi fechada.",
                        dica="IoT.abrir(porta) devolve outra")

    def escrever(self, dados):
        """Manda bytes. Devolve quantos foram."""
        self._exigir_aberta()
        crus = dados if isinstance(dados, (bytes, bytearray)) else str(dados).encode()
        with self._trava:
            if self._win:                                # pragma: no cover
                k32, handle, ctypes = self._win
                escritos = ctypes.wintypes.DWORD(0)
                k32.WriteFile(handle, crus, len(crus), ctypes.byref(escritos), None)
                return escritos.value
            total = 0
            while total < len(crus):
                try:
                    total += os.write(self._fd, crus[total:])
                except BlockingIOError:                  # pragma: no cover
                    time.sleep(0.001)
                except OSError as erro:
                    raise _erro(f"a porta '{self.porta}' sumiu no meio da "
                                f"escrita: {erro}",
                                nota="a placa foi desconectada, ou o cabo "
                                     "e so de energia") from None
            return total

    def ler(self, quantos=1, prazo=None):
        """Até `quantos` bytes, esperando no máximo `prazo` segundos.

        Devolve o que chegou — inclusive vazio. Uma leitura serial que
        levanta ao não receber nada obrigaria um `monitor` em volta de
        cada volta do laço; quem espera dado que pode não vir precisa
        decidir isso, e não ser interrompido.
        """
        self._exigir_aberta()
        limite = time.monotonic() + (self.prazo if prazo is None else float(prazo))
        saida = bytearray()
        while len(saida) < quantos:
            pedaco = self._ler_agora(quantos - len(saida))
            if pedaco:
                saida.extend(pedaco)
                continue
            if time.monotonic() >= limite:
                break
            time.sleep(0.001)
        return bytes(saida)

    def _ler_agora(self, quantos):
        if self._win:                                    # pragma: no cover
            k32, handle, ctypes = self._win
            buf = ctypes.create_string_buffer(quantos)
            lidos = ctypes.wintypes.DWORD(0)
            k32.ReadFile(handle, buf, quantos, ctypes.byref(lidos), None)
            return buf.raw[:lidos.value]
        import select
        pronto, _, _ = select.select([self._fd], [], [], 0)
        if not pronto:
            return b""
        try:
            return os.read(self._fd, quantos)
        except BlockingIOError:                          # pragma: no cover
            return b""
        except OSError as erro:
            raise _erro(f"a porta '{self.porta}' sumiu: {erro}",
                        nota="a placa foi desconectada") from None

    def linha(self, prazo=None, fim=b"\n"):
        """Lê até o fim de linha. Texto, já sem o `\\r\\n`."""
        limite = time.monotonic() + (self.prazo if prazo is None else float(prazo))
        saida = bytearray()
        while time.monotonic() < limite:
            byte = self.ler(1, prazo=0.02)
            if not byte:
                continue
            if byte == fim:
                break
            saida.extend(byte)
        return saida.decode("utf-8", "replace").rstrip("\r")

    def esperando(self):
        """Quantos bytes já chegaram e ainda não foram lidos."""
        self._exigir_aberta()
        if self._win:                                    # pragma: no cover
            return 0
        import fcntl
        import termios
        import array
        buf = array.array("i", [0])
        fcntl.ioctl(self._fd, termios.FIONREAD, buf, True)
        return buf[0]

    def limpar(self):
        """Joga fora o que chegou e ainda não foi lido."""
        self._exigir_aberta()
        if self._win:                                    # pragma: no cover
            return True
        import termios
        termios.tcflush(self._fd, termios.TCIOFLUSH)
        return True

    def reiniciar_placa(self):
        """Pulsa o DTR: é o que faz o Arduino reiniciar e rodar o setup().

        Abrir a porta já costuma reiniciar a placa (o autorreset está no
        hardware), mas nem toda placa o faz — e depois de um upload é
        preciso reiniciar à mão.
        """
        self._exigir_aberta()
        if self._win:                                    # pragma: no cover
            return False
        import fcntl
        import termios
        import struct
        DTR = struct.pack("I", termios.TIOCM_DTR)
        fcntl.ioctl(self._fd, termios.TIOCMBIC, DTR)     # baixa
        time.sleep(0.06)
        fcntl.ioctl(self._fd, termios.TIOCMBIS, DTR)     # levanta
        time.sleep(0.05)
        return True

    def fechar(self):
        """Idempotente, como todo `fechar` desta linguagem."""
        with self._trava:
            if not self._aberta:
                return False
            self._aberta = False
            if self._win:                                # pragma: no cover
                k32, handle, _ctypes = self._win
                k32.CloseHandle(handle)
            else:
                os.close(self._fd)
            return True

    def aberta(self):
        return self._aberta

    def __repr__(self):
        estado = "aberta" if self._aberta else "fechada"
        return f"<serial {self.porta} {self.velocidade} 8N1 {estado}>"


def abrir(porta, velocidade=115200, prazo=1.0):
    return Serial(porta, velocidade, prazo)
