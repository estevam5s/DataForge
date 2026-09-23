# -*- coding: utf-8 -*-
"""'dataforge iot' — a placa, do terminal.

    dataforge iot portas               as portas seriais que existem agora
    dataforge iot doctor               por que a placa nao responde
    dataforge iot monitorar            o monitor serial, com prazo
    dataforge iot sketch pisca         escreve o .ino (e mostra o codigo)
    dataforge iot carregar pasta/      compila e grava (usa o arduino-cli)
    dataforge iot placas               o que o arduino-cli reconhece
    dataforge iot piscar               o 'ola mundo': acende o LED 13 por Firmata

Por que 'doctor' e o comando mais util daqui
---------------------------------------------
Uma placa que nao responde tambem nao da erro: a porta abre e nada
chega. As causas sao poucas e sempre as mesmas — cabo so de energia,
driver do CH340 ausente, o sketch StandardFirmata nao gravado, a
velocidade errada, o monitor serial da IDE segurando a porta. O
`doctor` confere cada uma, na ordem em que elas acontecem.

Por que 'carregar' chama o arduino-cli
---------------------------------------
Compilar C++ para AVR e gravar pelo bootloader e o que ele faz, e bem.
Reimplementar isso seria refazer um compilador e um gravador — e o
projeto prefere dizer que depende dele a fingir que nao.
"""

import os
import sys


def color(texto, codigo):
    from .cli import color as _color
    return _color(texto, codigo)


def _iot():
    from .stdlib import get_module
    return get_module("Arcane.IoT")


def _tudo(argumentos, flags):
    """Os argumentos e as flags juntos.

    O despachante da CLI separa `--x=y` dos argumentos e entrega as
    duas listas. Ler so uma delas faz `--em=/tmp` sumir sem erro — e o
    sketch e impresso na tela em vez de ser gravado.
    """
    return list(argumentos or []) + list(flags or [])


def _porta_de(flags, argumentos):
    for a in _tudo(argumentos, flags):
        if a.startswith("--porta="):
            return a.split("=", 1)[1]
    return None


def _valor(argumentos, nome, padrao=None, flags=()):
    for a in _tudo(argumentos, flags):
        if a.startswith(f"--{nome}="):
            return a.split("=", 1)[1]
    return padrao


# ═══════════════════════════════════════════════════════════
#  Os subcomandos
# ═══════════════════════════════════════════════════════════

def portas(_argumentos, _flags):
    lista = _iot()["portas"]()
    if not lista:
        print(color("nenhuma porta serial encontrada.", "1;33"))
        print("  · o cabo pode ser SÓ de energia — muitos cabos de celular são")
        print("  · clones de UNO e ESP32 precisam do driver CH340/CP2102")
        print("  · num contêiner, a porta precisa ser passada com --device")
        return 1
    print(color(f"{len(lista)} porta(s):", "1;36"))
    for p in lista:
        print(f"  {p['porta']:<34} {color(p['descricao'], '0;90')}")
    return 0


def placas(_argumentos, _flags):
    iot = _iot()
    if not iot["tem_arduino_cli"]():
        print(color("o arduino-cli não está instalado.", "1;31"))
        print("  brew install arduino-cli   |   https://arduino.github.io/arduino-cli")
        return 1
    lista = iot["placas"]()
    if not lista:
        print("nenhuma placa reconhecida.")
        return 1
    for p in lista:
        fqbn = p["fqbn"] or color("sem FQBN — instale o core dela", "0;90")
        print(f"  {p['porta']:<30} {p['placa']:<26} {fqbn}")
    return 0


def doctor(argumentos, flags):
    achados = _iot()["doctor"](_porta_de(flags, argumentos))
    ruim = 0
    for a in achados:
        marca = color("✓", "1;32") if a["ok"] else color("✗", "1;31")
        ruim += 0 if a["ok"] else 1
        print(f"  {marca} {a['o_que']:<24} {a['detalhe']}")
    if ruim:
        print()
        print(color("O que costuma ser:", "1;33"))
        print("  1. o cabo é só de energia — troque por um de dados")
        print("  2. falta o driver USB-serial (CH340, CP2102) do clone")
        print("  3. o StandardFirmata não está gravado:")
        print("       dataforge iot sketch firmata --em=/tmp/fw")
        print("       dataforge iot carregar /tmp/fw/firmata --fqbn=arduino:avr:uno")
        print("  4. o monitor serial da IDE está com a porta aberta")
    return 1 if ruim else 0


def monitorar(argumentos, flags):
    iot = _iot()
    velocidade = int(_valor(argumentos, "velocidade", "115200", flags))
    linhas = int(_valor(argumentos, "linhas", "20", flags))
    prazo = float(_valor(argumentos, "prazo", "15", flags))
    try:
        lidas = iot["monitorar"](_porta_de(flags, argumentos), velocidade,
                                 linhas, prazo)
    except Exception as erro:                            # noqa: BLE001
        print(color(f"erro: {erro}", "1;31"))
        return 1
    for linha in lidas:
        print(f"  {linha}")
    if not lidas:
        print(color("nada chegou.", "1;33"))
        print("  · a velocidade tem de ser a do Serial.begin() do sketch")
        print(f"  · você pediu {velocidade}; os sketches usam 9600 ou 115200")
        return 1
    return 0


def sketch(argumentos, flags):
    iot = _iot()
    juntos = _tudo(argumentos, flags)
    primeiro = juntos[0] if juntos else ""
    if "--lista" in juntos or "-l" in juntos or primeiro == "lista":
        modelo = "--lista"
    else:
        modelo = primeiro if primeiro and not primeiro.startswith("-") else "pisca"
    if modelo == "--lista":
        for nome, dados in iot["sketches"]().items():
            print(f"  {color(nome, '1;36'):<24} {dados['descricao']}")
            if dados["opcoes"]:
                print(f"    {color('opções: ' + ', '.join(f'{k}={v}' for k, v in dados['opcoes'].items()), '0;90')}")
        return 0
    opcoes = {}
    for a in juntos[1:] if juntos and juntos[0] == modelo else juntos:
        if a.startswith("--") and "=" in a:
            chave, valor = a[2:].split("=", 1)
            if chave in ("em", "fqbn"):
                continue
            opcoes[chave] = int(valor) if valor.isdigit() else valor
    fqbn = _valor(argumentos, "fqbn", "arduino:avr:uno", flags)
    try:
        codigo = iot["sketch"](modelo, opcoes, fqbn)
    except Exception as erro:                            # noqa: BLE001
        print(color(f"erro: {erro}", "1;31"))
        return 1
    pasta = _valor(argumentos, "em", None, flags)
    if pasta:
        caminho = iot["gravar_sketch"](pasta, modelo, opcoes, fqbn)
        print(color(f"escrito: {caminho}", "1;32"))
        print(f"  grave com: dataforge iot carregar {os.path.dirname(caminho)} "
              f"--fqbn={fqbn}")
        return 0
    print(codigo)
    return 0


def carregar(argumentos, flags):
    iot = _iot()
    if not argumentos:
        print(color("falta o caminho do sketch.", "1;31"))
        print("  dataforge iot carregar /tmp/fw/firmata --fqbn=arduino:avr:uno")
        return 2
    fqbn = _valor(argumentos, "fqbn", "arduino:avr:uno", flags)
    try:
        r = iot["carregar"](argumentos[0], _porta_de(flags, argumentos), fqbn)
    except Exception as erro:                            # noqa: BLE001
        print(color(f"erro: {erro}", "1;31"))
        return 1
    print(r["saida"].strip() or "")
    if not r["ok"]:
        print(color(r["erro"].strip(), "1;31"))
        return 1
    print(color("gravado.", "1;32"))
    return 0


def compilar(argumentos, flags):
    iot = _iot()
    if not argumentos:
        print(color("falta o caminho do sketch.", "1;31"))
        return 2
    r = iot["compilar"](argumentos[0],
                        _valor(argumentos, "fqbn", "arduino:avr:uno", flags))
    print(r["saida"].strip() or "")
    if not r["ok"]:
        print(color(r["erro"].strip(), "1;31"))
        return 1
    print(color("compilou.", "1;32"))
    return 0


def piscar(argumentos, flags):
    """O 'olá mundo' do hardware: acende e apaga o LED da placa."""
    import time
    iot = _iot()
    pino = int(_valor(argumentos, "pino", "13", flags))
    vezes = int(_valor(argumentos, "vezes", "5", flags))
    try:
        placa = iot["conectar"](_porta_de(flags, argumentos))
    except Exception as erro:                            # noqa: BLE001
        print(color(f"erro: {erro}", "1;31"))
        print("  dataforge iot doctor")
        return 1
    try:
        placa.modo(pino, "saida")
        for i in range(vezes):
            placa.escrever(pino, True)
            print(f"  {i + 1}/{vezes} {color('●', '1;32')}")
            time.sleep(0.4)
            placa.escrever(pino, False)
            time.sleep(0.4)
    finally:
        placa.fechar()
    print(color("se o LED piscou, o caminho inteiro funciona.", "1;32"))
    return 0


SUBCOMANDOS = {
    "portas": portas,
    "placas": placas,
    "doctor": doctor,
    "monitorar": monitorar,
    "monitor": monitorar,
    "sketch": sketch,
    "carregar": carregar,
    "compilar": compilar,
    "piscar": piscar,
    "blink": piscar,
}


def executar(argumentos, flags=None):
    flags = flags or {}
    if not argumentos or argumentos[0] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return 0
    nome = argumentos[0]
    acao = SUBCOMANDOS.get(nome)
    if acao is None:
        import difflib
        parecido = difflib.get_close_matches(nome, SUBCOMANDOS, 1, 0.6)
        print(color(f"'{nome}' não é um subcomando de 'iot'.", "1;31"))
        if parecido:
            print(f"  você quis dizer '{parecido[0]}'?")
        print(f"  os que existem: {', '.join(sorted(SUBCOMANDOS))}")
        return 2
    try:
        return acao(argumentos[1:], flags)
    except KeyboardInterrupt:                            # pragma: no cover
        print()
        return 130
