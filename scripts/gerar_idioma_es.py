# -*- coding: utf-8 -*-
"""Gera 'dataforge/idiomas/es.py' a partir dos PADROES do 'pt.py'.

Os padroes sao a metade que nao pode divergir entre dois catalogos: um
regex copiado a mao casaria 'quase', e 'quase' aqui quer dizer uma
mensagem que sai em ingles sem ninguem entender por que. As traducoes
sao escritas a mao, abaixo, e sao elas que valem.

Ao acrescentar uma entrada em 'pt.py', este gerador RECUSA rodar ate
haver a linha correspondente aqui — e a mensagem diz qual falta.
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import marca                                 # noqa: E402
from dataforge.idiomas import pt                            # noqa: E402

marca.preparar_saida()

INTEIRAS = [
    "'{n}' no está definido.",
    "'{n}' es una palabra reservada y no puede recibir un valor. Elija otro nombre.",
    "'{n}' es steady y no puede ser reasignado.",
    "'{n}' fue leído antes de recibir un valor.",
    'La clave "{k}" no está en este vault.',
    "El índice {i} está fuera del alcance de un cluster de {n} elemento(s).",
    "Un {t} no acepta índice.",
    "Un {t} no acepta índice.",
    "No se puede recorrer un {t}: se esperaba Cluster, Vault o String",
    "El {t} está vacío.",
    "División por cero.",
    "No se suma Void a un texto.",
    "'{op}' entre {a} y {b} no está definido.",
    "'{op}' entre {a} y {b} no tiene respuesta.",
    "'{op}' entre un Decimal y un Float se rechaza",
    "No se suma {a} con {b}",
    "No se multiplica {a} por {b}",
    "a la acción '{n}' le falta(n) el/los argumento(s): {q}",
    "la acción '{n}' recibe {e} argumento(s), y se pasaron {d}",
    "la acción '{n}' recibió un argumento que no conoce: '{a}'",
    "La pila de llamadas pasó de {n} marcos en '{f}'.",
    "El record '{r}' no tiene el campo ni el método '{m}'. Tiene: {tem}",
    "El record '{r}' no tiene el campo '{m}'",
    "El record '{r}' no tiene el/los campo(s): {q}",
    'El record \'{r}\' es inmutable: no se asigna a \'{m}\'. Haga una copia modificada con "{forma}".',
    "Al record '{r}' le falta(n) el/los campo(s): {q}",
    "'{b}' no tiene el miembro '{m}'",
    "El enum '{e}' no tiene el miembro '{m}'. Miembros: {tem}",
    "No se accede al miembro '{m}' en {t}.",
    "No se lee '{m}': el valor es void.",
    "el módulo '{mod}' no tiene '{m}'",
    "No se llama a '{n}': el valor es void.",
    "No se llama al método '{n}' en {t}.",
    "{t} no es invocable.",
    "Token inesperado: {t} ({v})",
    "Se esperaba {q} después de {onde}",
    "Se esperaba {q}",
    "La tabulación no se acepta en la sangría.",
    "Import circular: {cadeia}",
    "{w} tiene el tipo {d}, pero {onde} es {o}{resto}",
    "{w} tiene el tipo {d}, y recibió {o}",
    "{c} solo guarda {t}, y {op} recibió {o}.",
    "{c} no guarda {o}: {r} es {o2}",
    "'{b}<…>' no es una colección: solo Cluster<T>, Vault<K, V> y Set<T> "
    "declaran el tipo de lo que hay dentro. Anótelo como '{b2}'.",
    "{f} lleva un tipo — y '{t}' tiene {n}.",
    "{f} lleva dos tipos, la clave y el valor — y '{t}' tiene {n}.",
    "Declarado como {d}, y el valor es {o}",
    "El parámetro '{p}' de '{f}' espera {d}, y recibió {o}",
    "Código inalcanzable: el bloque ya terminó arriba",
    "La variable '{n}' recibe un valor y nunca se lee",
    "'{n}' fue declarado como {d}, y esta asignación es {o}",
    "El campo '{c}' de '{b}' fue declarado como {d}, y esta asignación es {o}",
    "Asigne un {d}",
    "'{p}' no puede salir de un bloque '{b}'.",
    "{n} thread(s) fallaron. El error está dibujado arriba.",
    "'{n}' recibe {e} argumento(s), y recibió {d}",
]

PEDACOS = [
    "Módulo '{m}' no encontrado.",
    "Busqué en la biblioteca estándar, junto a {a} y en forge_modules/.",
    "Ningún paquete instalado — pruebe 'dataforge add <paquete>'.",
    "Biblioteca estándar:",
    "¿Quiso decir '{n}'?",
    "Campos: ",
    "él ofrece: ",
    "declarada en {a}, línea {l}",
    "Tiene: ",
    "Miembros: ",
    "Elija otro nombre.",
    "la variable '{n}'",
    "el parámetro '{p}' de la acción '{f}'",
    "el valor devuelto por la acción '{f}'",
    "el campo '{c}' de '{b}'",
    " tiene el tipo {d}, y recibió {o}",
    "Asigne un {d}, o use un nombre nuevo — la anotación vale para toda "
    "asignación posterior, y no solo para la primera",
    "el valor en la clave {k}",
    "el valor de la clave {k}",
    "la clave {k}",
    "el elemento de {m}",
    "el valor asignado",
    "un elemento",
    "todo elemento tiene que ser {t} — corrija el valor, o amplíe la "
    "anotación (Any acepta todo)",
    "toda clave tiene que ser {t}",
    "inserte un {t}, o amplíe la anotación (Any acepta todo)",
    "{t} no tiene tamaño",
    "necesita un número real, y recibió {t}",
    "abs() no se aplica a {t}",
    "no se repite una secuencia por algo que no es {t}",
    "'{op}' no se aplica entre {a} y {b}",
    "'{op}' no se aplica entre {a} y {b}",
    "el primero: ",
    "un error capturado ({t})",
    "error capturado ({t})",
    "para atrapar el error con 'handle', use 'parallel', que espera las "
    "instrucciones",
    "cada instrucción de 'parallel' corre en su propio thread, y no hay "
    "bucle ni acción alrededor para terminar",
    "decida dentro de la instrucción, o saque el bucle de dentro del 'parallel'",
    "la clave se leyó aquí",
    "no hay nada que leer",
    "fuera del alcance",
    "usado aquí",
    "este nombre nunca recibió un valor en ningún ámbito alrededor",
    "el vault tiene {n} clave(s):",
    "los índices válidos van de {a} a {b}, o de {c} a {d} desde el final",
    "el lado derecho resultó en 0",
    "el lado {lado} resultó en 'void'",
    "algo antes de esto devolvió 'void'",
    "Solo Cluster, Vault, String y record aceptan [ ].",
    "'steady' declara un valor que nunca cambia",
    "use  valor ?? predeterminado  para un valor por defecto, o compruebe "
    "antes con  vault.has(clave)",
    "use  x[-1]  para el último elemento",
    "proteja el divisor antes:",
    "asigne antes de usar:",
    "recuerde que DataForge asigna con ':=', no con '='",
    "Pase {t}",
    "Constrúyalo como ",
    "Llámelo como ",
    "use  ?.  para parar con seguridad:",
    "o un valor por defecto:",
    "Quite esta línea, o muévala antes del 'yield'/'halt'/'skip'",
    "Quítela, o renómbrela a '{n}' para decir que es a propósito",
    "Compruebe el divisor antes de dividir",
    "(dentro de un 'monitor' o 'expect', por eso es solo un aviso)",
]

CABECALHO = '''# -*- coding: utf-8 -*-
"""El catálogo en español.

GERADO por 'scripts/gerar_idioma_es.py' a partir dos PADROES do
'pt.py' — eles sao a metade que nao pode divergir entre dois catalogos:
um regex copiado a mao casaria 'quase', e 'quase' aqui quer dizer uma
mensagem que sai em ingles sem ninguem entender por que.

As traducoes sao escritas a mao, no gerador. Nao edite este arquivo.
"""

'''


def gerar():
    faltam = []
    if len(INTEIRAS) != len(pt.INTEIRAS):
        faltam.append(f"INTEIRAS: pt tem {len(pt.INTEIRAS)}, es tem "
                      f"{len(INTEIRAS)}")
        for i in range(len(INTEIRAS), len(pt.INTEIRAS)):
            faltam.append(f"  sem tradução: {pt.INTEIRAS[i][1]}")
    if len(PEDACOS) != len(pt.PEDACOS):
        faltam.append(f"PEDACOS: pt tem {len(pt.PEDACOS)}, es tem "
                      f"{len(PEDACOS)}")
        for i in range(len(PEDACOS), len(pt.PEDACOS)):
            faltam.append(f"  sem tradução: {pt.PEDACOS[i][1]}")
    if faltam:
        raise SystemExit("o catálogo em espanhol ficou para trás:\n  "
                         + "\n  ".join(faltam))

    linhas = [CABECALHO.rstrip("\n"), "", "INTEIRAS = ("]
    for (padrao, _), texto in zip(pt.INTEIRAS, INTEIRAS):
        linhas.append(f"    ({padrao!r},\n     {texto!r}),")
    linhas += [")", "", "PEDACOS = ("]
    for (padrao, _), texto in zip(pt.PEDACOS, PEDACOS):
        linhas.append(f"    ({padrao!r},\n     {texto!r}),")
    linhas.append(")")
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    destino = os.path.join(RAIZ, "dataforge", "idiomas", "es.py")
    texto = gerar()
    if "--check" in sys.argv:
        atual = open(destino, encoding="utf-8").read()
        if atual != texto:
            raise SystemExit("es.py está fora de dia — rode o gerador")
        print("es.py em dia")
    else:
        open(destino, "w", encoding="utf-8").write(texto)
        print(f"  {len(INTEIRAS)} inteiras e {len(PEDACOS)} pedaços em es.py")
