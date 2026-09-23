# -*- coding: utf-8 -*-
"""IoT — quatorze páginas: da porta serial ao painel, com Arduino de verdade.

Todo bloco roda **sem placa**: `IoT.conectar_simulada` põe do outro lado
do cabo um `Simulador` que fala o mesmo Firmata. É o que torna esta
seção executável no CI — e o que deixa quem lê testar antes de comprar
a placa.

Onde o texto fala de hardware que este repositório não tem, ele diz.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot",
"title": "IoT e Arduino",
"description": "A linguagem falando com placa de verdade: Firmata para prototipar, sketch em C++ para o que precisa de tempo, MQTT para o resto do mundo.",
"blocos": [
 {"p": "`Arcane.IoT` liga a linguagem a uma placa física. São três caminhos, e a escolha entre eles é a primeira decisão de qualquer projeto: **Firmata** (o computador manda, a placa obedece), **sketch** (o programa roda na placa, e a linguagem só o escreve e grava) e **MQTT** (a placa e o painel conversam por uma rede)."},
 {"table": {
   "head": ["Caminho", "Onde o programa roda", "Serve para", "O preço"],
   "rows": [
     ["Firmata", "no computador", "prototipar, sensor de mesa, painel", "cada ordem atravessa o cabo — milissegundos"],
     ["Sketch", "na placa", "tempo real, autonomia, bateria", "compilar e gravar a cada mudança"],
     ["MQTT", "os dois, ligados por rede", "vários sensores, telemetria, automação", "depende de um broker de pé"]]}},
 {"h2": "O menor programa que fala com hardware"},
 {"p": "Com a placa ligada e o `StandardFirmata` gravado nela, isto acende o LED da placa:"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar()          // acha a porta sozinha, se houver uma só
placa.modo(13, "saida")
placa.escrever(13, yes)
sleep(500)
placa.escrever(13, no)
placa.fechar()''', "lang": "df", "title": "precisa de placa"},
 {"callout": {"tipo": "nota", "titulo": "Sem placa, tudo aqui roda", "texto": "Troque `IoT.conectar()` por `IoT.conectar_simulada(\"uno\")` e o programa inteiro funciona: do outro lado do cabo fica um simulador que fala o mesmo protocolo, com o mapa de pinos da placa de verdade. É assim que os exemplos desta seção são conferidos a cada execução da suíte."}},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")
placa.escrever(13, yes)
assert placa.simulador.pino(13) is 1     // o simulador deixa PERGUNTAR
placa.fechar()
out "o LED acendeu — num Arduino de mentira"''', "lang": "df"},
 {"h2": "O que existe"},
 {"list": [
   "**Porta serial** escrita aqui — `termios` no macOS e no Linux, `ctypes` sobre a API do Windows. Sem `pyserial`, e sem dependência nenhuma.",
   "**Firmata 2.x** completo: modos, digital, analógico, PWM, servo, I²C, `sendString`, amostragem, reset.",
   "**Um simulador** com o mapa de seis placas (UNO, Nano, Mega, Leonardo, UNO R4, ESP32).",
   "**Seis sketches** gerados em C++, prontos para o `arduino-cli` compilar e gravar.",
   "**MQTT 3.1.1** falado à mão sobre TCP, com QoS 0 e 1, curingas e testamento.",
   "**`dataforge iot`** no terminal: `portas`, `doctor`, `monitorar`, `sketch`, `carregar`, `piscar`."]},
 {"h2": "O que não existe — e não vale fingir"},
 {"table": {
   "head": ["Não há", "Porque"],
   "rows": [
     ["compilador de C++ próprio", "o `arduino-cli` faz isso, e bem; reimplementá-lo seria refazer o GCC e o avrdude"],
     ["gravador de bootloader próprio", "idem — `IoT.carregar` chama o `arduino-cli`"],
     ["TLS no MQTT", "o `ssl` da biblioteca padrão resolveria; a decisão espera um teste com certificado de verdade"],
     ["QoS 2", "exige guardar o estado de quatro mensagens por publicação, e quase nenhum projeto de sensor usa"],
     ["tempo real por Firmata", "cada ordem atravessa o cabo. O que precisa de microssegundos é sketch — ver *Quando usar cada um*"]]}},
 {"h2": "Por onde começar"},
 {"cards": [
   {"title": "Primeiros passos", "desc": "Ligar a placa, descobrir a porta, gravar o Firmata e ver o LED piscar.", "href": "/docs/iot/primeiros-passos"},
   {"title": "Sem placa nenhuma", "desc": "O simulador, e como testar um projeto de hardware no CI.", "href": "/docs/iot/sem-placa"},
   {"title": "Quando usar cada um", "desc": "Firmata ou sketch: a conta de latência, medida.", "href": "/docs/iot/quando-usar"},
   {"title": "Um projeto inteiro", "desc": "A estufa: sensor, relé, histerese, painel e telemetria.", "href": "/docs/iot/projeto-estufa"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/primeiros-passos",
"title": "Primeiros passos com a placa",
"description": "Do cabo ao LED piscando: achar a porta, gravar o StandardFirmata, e o doctor que diz por que nada responde.",
"blocos": [
 {"p": "Uma placa que não responde **também não dá erro**: a porta abre, e nada chega. As causas são poucas e sempre as mesmas, e o `doctor` confere cada uma na ordem em que elas acontecem."},
 {"h2": "1. Ver se o computador enxerga a placa"},
 {"code": '''$ dataforge iot portas
2 porta(s):
  /dev/cu.usbmodem1101               Arduino UNO R4 WiFi
  /dev/cu.Bluetooth-Incoming-Port    Bluetooth''', "lang": "bash"},
 {"p": "Nenhuma porta é o sintoma mais comum de todos, e quase nunca é a placa:"},
 {"list": [
   "**O cabo é só de energia.** Muitos cabos de celular não têm os fios de dados. É a causa nº 1.",
   "**Falta o driver.** Clones de UNO usam o CH340; ESP32 costuma usar CP2102 ou CH9102.",
   "**Num contêiner**, a porta precisa ser passada: `docker run --device=/dev/ttyACM0`."]},
 {"h2": "2. Gravar o StandardFirmata"},
 {"p": "O Firmata é um sketch como outro qualquer: ele fica na placa esperando ordens. Sem ele, a porta abre e o silêncio é total. A linguagem escreve o sketch e chama o `arduino-cli` para gravar:"},
 {"code": '''$ dataforge iot sketch firmata --em=/tmp/fw
escrito: /tmp/fw/firmata/firmata.ino
  grave com: dataforge iot carregar /tmp/fw/firmata --fqbn=arduino:avr:uno

$ dataforge iot carregar /tmp/fw/firmata --fqbn=arduino:avr:uno
gravado.''', "lang": "bash"},
 {"callout": {"tipo": "atencao", "titulo": "O arquivo tem o nome da pasta", "texto": "Um `.ino` solto não compila, e o erro do `arduino-cli` não diz por quê. `IoT.gravar_sketch(\"/tmp/fw\", \"firmata\")` cria `/tmp/fw/firmata/firmata.ino` — a pasta e o arquivo com o mesmo nome, que é o que o Arduino exige."}},
 {"h2": "3. Piscar"},
 {"code": '''$ dataforge iot piscar --pino=13 --vezes=5
  1/5 ●
  2/5 ●
  3/5 ●
  4/5 ●
  5/5 ●
se o LED piscou, o caminho inteiro funciona.''', "lang": "bash"},
 {"h2": "Quando não funciona: o doctor"},
 {"code": '''$ dataforge iot doctor
  ✓ porta serial            /dev/cu.usbmodem1101 — Arduino UNO R4 WiFi
  ✓ a porta abre            57600 baud, 8N1
  ✗ responde Firmata        nada chegou em 5 s
  ✓ arduino-cli             0.35.3

O que costuma ser:
  1. o cabo é só de energia — troque por um de dados
  2. falta o driver USB-serial (CH340, CP2102) do clone
  3. o StandardFirmata não está gravado:
       dataforge iot sketch firmata --em=/tmp/fw
       dataforge iot carregar /tmp/fw/firmata --fqbn=arduino:avr:uno
  4. o monitor serial da IDE está com a porta aberta''', "lang": "bash"},
 {"p": "A última linha pega o erro que mais custa tempo a quem vem da IDE: **duas coisas não abrem a mesma porta**. Com o monitor serial aberto na IDE, a conexão daqui falha ou fica muda, e nada na tela explica isso."},
 {"h2": "A velocidade tem de ser a do sketch"},
 {"code": '''adopt Arcane.IoT as IoT

// o StandardFirmata fala 57600 — e é o padrão de IoT.conectar
assert "pwm" in IoT.modos()
out "os modos:", len(IoT.modos())''', "lang": "df"},
 {"p": "Para um sketch seu, que escreve com `Serial.println`, a velocidade é a do `Serial.begin()` dele — e o monitor do terminal pergunta:"},
 {"code": '''$ dataforge iot monitorar --velocidade=9600 --linhas=5 --prazo=10
  temperatura: 21.4
  temperatura: 21.5
  temperatura: 21.4''', "lang": "bash"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/placas",
"title": "As placas",
"description": "UNO, Nano, Mega, Leonardo, UNO R4 e ESP32 — o mapa de cada uma, e por que ele vem da PLACA e não de uma tabela.",
"blocos": [
 {"p": "Cada placa tem um mapa diferente: quantos pinos digitais, quais fazem PWM, quantos canais analógicos, qual a resolução da conversão. Escrever esse mapa no código da linguagem seria errar na primeira placa nova — então, com a placa ligada, **quem responde é ela**."},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
assert "pwm" in placa.capacidades(9)        // a PLACA disse isto
assert not ("pwm" in placa.capacidades(13))

monitor:
    placa.modo(13, "pwm")                   // e por isso isto é recusado
    assert no                               // não chega aqui
handle Error as e:
    out e.message                           // o pino 13 nao faz 'pwm'.
placa.fechar()''', "lang": "df"},
 {"h2": "Os modelos que o simulador conhece"},
 {"code": '''adopt Arcane.IoT as IoT

m := IoT.modelos()
assert m["uno"]["digitais"] is 14 and m["uno"]["analogicos"] is 6
assert m["mega"]["digitais"] is 54
assert 11 in m["uno"]["pwm"] and not (4 in m["uno"]["pwm"])
out sorted(keys(m))''', "lang": "df"},
 {"table": {
   "head": ["Modelo", "Digitais", "Analógicos", "PWM", "Tensão", "FQBN"],
   "rows": [
     ["`uno`", "14", "6", "3, 5, 6, 9, 10, 11", "5 V", "`arduino:avr:uno`"],
     ["`nano`", "14", "8", "3, 5, 6, 9, 10, 11", "5 V", "`arduino:avr:nano`"],
     ["`mega`", "54", "16", "2–13, 44–46", "5 V", "`arduino:avr:mega`"],
     ["`leonardo`", "20", "12", "3, 5, 6, 9, 10, 11, 13", "5 V", "`arduino:avr:leonardo`"],
     ["`uno-r4`", "14", "6", "3, 5, 6, 9, 10, 11", "5 V", "`arduino:renesas_uno:unor4wifi`"],
     ["`esp32`", "34", "16", "quase todos", "**3,3 V**", "`esp32:esp32:esp32`"]]}},
 {"callout": {"tipo": "atencao", "titulo": "3,3 V não é 5 V, e isso queima placa", "texto": "Ligar um sensor de 5 V direto num ESP32 costuma matar o pino. E a conta do sensor muda junto: a leitura analógica do ESP32 tem **12 bits** (0 a 4095), não 10. Toda função de sensor daqui recebe `referencia` e `bits` por isso — ver *Sensores*."}},
 {"code": '''adopt Arcane.IoT as IoT

assert IoT.tensao(1023) is 5.0                      // UNO: 10 bits, 5 V
assert round(IoT.tensao(4095, 3.3, 12), 2) is 3.3   // ESP32: 12 bits, 3,3 V''', "lang": "df"},
 {"h2": "Uma Mega tem mais pinos, e o Firmata os vê"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("mega")
assert placa.info()["pinos"] is 70
placa.modo(53, "saida")                 // um pino que não existe numa UNO
placa.escrever(53, yes)
assert placa.simulador.pino(53) is 1
placa.fechar()''', "lang": "df"},
 {"h2": "Qual é o FQBN da minha placa?"},
 {"p": "O `arduino-cli` responde, com a placa ligada:"},
 {"code": '''$ dataforge iot placas
  /dev/cu.usbmodem1101           Arduino UNO R4 WiFi        arduino:renesas_uno:unor4wifi''', "lang": "bash"},
 {"p": "Um FQBN em branco quer dizer que a placa foi reconhecida mas o *core* dela não está instalado — `arduino-cli core install arduino:renesas_uno` resolve."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/firmata",
"title": "Firmata: a placa como periférico",
"description": "O protocolo, os doze modos de pino, o relatório periódico — e o erro nº 1 de quem começa.",
"blocos": [
 {"p": "Com o `StandardFirmata` gravado, a placa deixa de ter um programa e passa a ter um **protocolo**: ela obedece. Quem decide é o computador, e isso muda o ciclo de trabalho por inteiro."},
 {"table": {
   "head": ["Sem Firmata", "Com Firmata"],
   "rows": [
     ["escrever C++, compilar, gravar, testar", "chamar `placa.escrever(13, yes)` e ver o LED"],
     ["~20 s a cada tentativa", "milissegundos"],
     ["depurar por `Serial.println`", "depurar com `dataforge debug`"]]}},
 {"h2": "Todo pino tem um modo, e ele é declarado"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")

placa.modo(13, "saida")          // LED, relé
placa.modo(2, "entrada_pullup")  // botão, sem resistor externo
placa.modo(9, "pwm")             // brilho, velocidade
placa.modo(3, "servo")           // posição
placa.modo(14, "analogico")      // A0 — sensor

assert "pwm" in IoT.modos()      // a lista dos doze
placa.fechar()''', "lang": "df", "title": "os modos mais usados"},
 {"code": '''adopt Arcane.IoT as IoT

out IoT.modos()
assert len(IoT.modos()) is 12''', "lang": "df"},
 {"p": "Declarar o modo por conta própria seria conveniente e **errado**: um pino em `saida` recebendo PWM acende no talo, e quem lê o programa não veria onde o modo mudou. Por isso `pwm` e `servo` exigem o modo já declarado:"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
monitor:
    placa.pwm(9, 128)                 // sem o modo
handle Error as e:
    out e.message                     // …precisa do modo declarado
placa.modo(9, "pwm")
assert placa.pwm(9, 128) is 128
placa.fechar()''', "lang": "df"},
 {"h2": "O erro nº 1: ler analógico sem pedir o relatório"},
 {"p": "A placa **não responde perguntas** sobre o analógico: ela envia sozinha, de tempos em tempos, os canais que você mandou relatar. Sem `relatar_analogico`, o pino está certo, o sensor está certo, e a leitura é zero — sem nenhum erro."},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.simulador.definir_analogico(0, 900)   // o sensor "vale" 900
sleep(100)
assert placa.analogico(0) is 0              // e chega ZERO

placa.relatar_analogico(0)                  // é esta linha que falta
sleep(120)
assert placa.analogico(0) is 900
placa.fechar()''', "lang": "df"},
 {"h2": "A amostragem é uma troca"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
assert placa.amostragem(50) is 50       // de 10 a 10000 ms; o padrão é 19
placa.fechar()''', "lang": "df"},
 {"list": [
   "**Baixa demais** enche a serial de mensagens e **atrasa as ordens que você manda** — o LED demora a responder ao clique.",
   "**Alta demais** faz o gráfico perder detalhe, e um botão lido por relatório parecer que \"não pegou\".",
   "Para um sensor de temperatura, 500 ms é generoso. Para um potenciômetro que move um servo, 20 ms."]},
 {"h2": "Reagir, em vez de perguntar"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
vistos := []
placa.observar(lambda e: vistos.append(e["tipo"]))

placa.modo(2, "entrada_pullup")
placa.simulador.definir_digital(2, 1)
sleep(120)
placa.simulador.definir_digital(2, 0)
sleep(120)

assert "digital" in vistos
placa.fechar()''', "lang": "df"},
 {"h2": "O sketch também fala"},
 {"p": "`Firmata.sendString(\"…\")` no C++ chega aqui como texto — é o `println` de quem usa Firmata:"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.simulador.mandar_texto("calibração concluída — ção, á, ê")
sleep(120)
assert "calibração" in placa.textos()[0]
placa.fechar()''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Por que o acento importa aqui", "texto": "No Firmata todo byte de dado viaja partido em dois de **sete bits** — o oitavo marca comando. Ler só o primeiro de cada par funciona em ASCII, porque ali o bit 7 é zero; num acento, \"olá\" vira \"olC!\". O defeito fica escondido até a primeira mensagem em português, e foi exatamente assim que ele apareceu aqui."}},
 {"h2": "Fechar desliga as saídas"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")
placa.escrever(13, yes)
placa.fechar()
assert placa.simulador.pino(13) is 0        // apagou ao sair''', "lang": "df"},
 {"p": "Um programa que termina deixando um relé ligado é o defeito mais caro desta área: o resto do sistema continua, sem ninguém olhando. `fechar` é idempotente — chamá-lo num `defer` e de novo no fim não é erro."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/sensores",
"title": "Sensores: do número cru ao valor",
"description": "escala, tensão, TMP36, NTC, divisor, média móvel e histerese — a matemática que todo projeto reescreve errado.",
"blocos": [
 {"p": "Um pino analógico devolve um número de 0 a 1023. Ele não é temperatura, nem luz, nem umidade: é o quanto da tensão de referência chegou ali. Transformar isso em grandeza é a parte que todo projeto refaz — e onde os mesmos quatro erros acontecem."},
 {"h2": "escala — o `map` que limita"},
 {"code": '''adopt Arcane.IoT as IoT

assert IoT.escala(512, 0, 1023, 0, 100) > 50.0 and IoT.escala(512, 0, 1023, 0, 100) < 50.1
assert IoT.escala(2000, 0, 1023, 0, 100) is 100     // limita, por padrão
assert IoT.escala(-5, 0, 1023, 0, 100) is 0
assert IoT.escala(2000, 0, 1023, 0, 100, no) > 100  // sem limitar, extrapola''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O `map()` do Arduino não limita", "texto": "Ruído faz um ADC de 10 bits devolver 1024 de vez em quando. Com o `map` do C, isso vira 101% num painel — e num controle de motor vira um valor fora da faixa do PWM. Aqui o padrão é limitar, e `limitar := no` é escolha explícita de quem quer extrapolar."}},
 {"h2": "tensão — a conta que depende da placa"},
 {"code": '''adopt Arcane.IoT as IoT

assert IoT.tensao(1023) is 5.0                       // UNO
assert round(IoT.tensao(2048, 3.3, 12), 2) is 1.65   // ESP32: 12 bits''', "lang": "df"},
 {"h2": "TMP36 — o sensor de três pernas"},
 {"p": "A folha de dados diz: 750 mV a 25 °C, 10 mV por grau. É uma reta, e a conta é uma linha — mas o deslocamento de 500 mV é o que quase todo mundo esquece:"},
 {"code": '''adopt Arcane.IoT as IoT

leitura := 0.75 / 5.0 * 1023            // 750 mV num ADC de 10 bits
temperatura := IoT.tmp36(leitura)
assert temperatura > 24.5 and temperatura < 25.5
out $"{round(temperatura, 1)} °C"''', "lang": "df"},
 {"h2": "NTC — o termistor, e a equação B"},
 {"code": '''adopt Arcane.IoT as IoT

// com o termistor na resistência nominal, o divisor lê a metade da escala
t := IoT.ntc(1023 / 2)
assert t > 24.7 and t < 25.3

// e a ponta da escala não é temperatura: é fio solto ou curto
monitor:
    IoT.ntc(0)
handle Error as e:
    out e.message                       // …ponta da escala…''', "lang": "df"},
 {"p": "Recusar as pontas é o ponto: com a leitura em 0 ou 1023 a equação divide por zero ou tira log de zero, e o que sai é um número absurdo com cara de temperatura. Um termostato que vê −273 °C liga o aquecedor e não desliga mais."},
 {"h2": "divisor — quando o sensor é uma resistência"},
 {"code": '''adopt Arcane.IoT as IoT

// LDR, sensor de umidade de solo, potenciômetro: tudo vira resistência
r := IoT.divisor(1023 / 2)
assert r > 9900 and r < 10100
out $"{round(r)} Ω"''', "lang": "df"},
 {"h2": "média móvel — o ruído do ADC"},
 {"p": "Uma leitura pura treme: 512, 509, 514, 511. Num gráfico isso é grama; num controle, é o relé batendo. A média móvel é a resposta mais barata, e ela **esquece**:"},
 {"code": '''adopt Arcane.IoT as IoT

media := IoT.media_movel(3)
assert media(10) is 10
assert media(20) is 15
assert media(30) is 20
assert media(40) is 30          // o 10 saiu da janela''', "lang": "df"},
 {"h2": "histerese — o relé que não bate"},
 {"p": "Ligar acima de 30 e desligar abaixo de 30 faz o relé chavear dezenas de vezes por minuto quando a temperatura fica **em** 30 — e é assim que um contato se queima. A saída é ter **duas** soleiras:"},
 {"code": '''adopt Arcane.IoT as IoT

ventoinha := IoT.histerese(30, 28)      // liga em 30, só desliga em 28
assert ventoinha(29) is no              // subindo, ainda não
assert ventoinha(31) is yes
assert ventoinha(29) is yes             // no meio, segura o estado
assert ventoinha(27) is no''', "lang": "df"},
 {"p": "Invertendo as duas, ela liga **abaixo** — é o umidificador, o aquecedor, a bomba:"},
 {"code": '''adopt Arcane.IoT as IoT

umidificador := IoT.histerese(40, 50)   // liga abaixo de 40
assert umidificador(45) is no
assert umidificador(35) is yes
assert umidificador(45) is yes
assert umidificador(55) is no''', "lang": "df"},
 {"code": '''adopt Arcane.IoT as IoT

monitor:
    IoT.histerese(30, 30)               // duas soleiras iguais são uma só
handle Error as e:
    out e.message''', "lang": "df"},
 {"h2": "Os quatro juntos, num sensor de verdade"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.relatar_analogico(0)
placa.amostragem(20)

suavizar := IoT.media_movel(5)
aquecedor := IoT.histerese(18, 21)      // liga abaixo de 18, desliga em 21
placa.modo(7, "saida")

placa.simulador.definir_analogico(0, 123)       // ~10 °C
sleep(120)
graus := IoT.tmp36(suavizar(placa.analogico(0)))
ligado := aquecedor(graus)
placa.escrever(7, ligado)

out $"{round(graus, 1)} °C — aquecedor {"ligado" given ligado otherwise "desligado"}"
assert ligado is yes
placa.fechar()''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/atuadores",
"title": "Atuadores: LED, PWM, servo e relé",
"description": "Do LED ao motor — e as três armadilhas elétricas que nenhum código evita.",
"blocos": [
 {"p": "Ler é metade; a outra é **agir**. São quatro formas, e a escolha entre elas é elétrica antes de ser de software."},
 {"h2": "Digital: ligado ou desligado"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")

cycle i from 1 to 3:
    placa.escrever(13, yes)
    sleep(50)
    placa.escrever(13, no)
    sleep(50)

assert placa.simulador.pino(13) is 0
placa.fechar()''', "lang": "df"},
 {"h2": "PWM: o meio-termo que não existe"},
 {"p": "Um pino digital só tem dois valores. \"Meio brilho\" é o pino ligando e desligando rápido o bastante para o olho — ou o motor — não notar. É o PWM, de 0 a 255:"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(9, "pwm")

cycle brilho in [0, 64, 128, 192, 255]:
    placa.pwm(9, brilho)
    sleep(20)

assert placa.simulador.pino(9) is 255

monitor:
    placa.pwm(9, 300)                   // a faixa é 0..255
handle Error as e:
    out e.message
placa.fechar()''', "lang": "df"},
 {"p": "Num UNO, só os pinos **3, 5, 6, 9, 10 e 11** fazem PWM — e é a placa quem diz isso, não uma tabela escrita aqui. Um `modo(13, \"pwm\")` é recusado na hora, com a lista do que aquele pino aceita."},
 {"h2": "Servo: posição, não velocidade"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(3, "servo")

cycle graus in [0, 90, 180, 90]:
    placa.servo(3, graus)
    sleep(30)

assert placa.simulador.servo(3) is 90
placa.fechar()''', "lang": "df"},
 {"p": "Cada servo tem os seus microssegundos de fim de curso. Quando o braço treme numa ponta, é isso — e `configurar_servo` ajusta:"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
assert placa.configurar_servo(3, 600, 2300) is "servo"
placa.servo(3, 0)
placa.fechar()''', "lang": "df"},
 {"h2": "Relé: ligar o que não é de 5 V"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(7, "saida")

action bomba(ligada):
    placa.escrever(7, ligada)
    yield ligada

assert bomba(yes) is yes
sleep(50)
assert bomba(no) is no
placa.fechar()                          // o relé desliga ao sair''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Três armadilhas que o código não evita", "texto": "**Corrente**: um pino de Arduino entrega ~20 mA. Motor, tira de LED e bomba precisam de transistor ou driver — ligados direto, o pino morre. **Lógica invertida**: quase todo módulo de relé chinês liga em `LOW`; o programa fica certo e o comportamento, ao contrário. **Indutivo**: motor e solenoide devolvem um pico ao desligar, e sem o diodo de roda-livre isso reinicia a placa — o sintoma é um travamento \"aleatório\" que só acontece quando o motor para."}},
 {"h2": "Desligar é parte do programa"},
 {"code": '''adopt Arcane.IoT as IoT

action regar(placa, segundos):
    placa.modo(7, "saida")
    defer:
        placa.escrever(7, no)           // roda mesmo se o corpo falhar
    placa.escrever(7, yes)
    sleep(segundos * 10)
    yield "regado"

placa := IoT.conectar_simulada("uno")
assert regar(placa, 2) is "regado"
assert placa.simulador.pino(7) is 0
placa.fechar()''', "lang": "df"},
 {"p": "O `defer` roda na saída da ação — inclusive quando ela falha no meio. Numa bomba de água, a diferença entre isso e um `escrever(7, no)` no fim do corpo é uma casa alagada."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/i2c",
"title": "I²C: dois fios, muitos sensores",
"description": "O barramento que liga BMP280, MPU6050 e display no mesmo par de fios — e por que a leitura pode devolver void.",
"blocos": [
 {"p": "I²C liga vários dispositivos em **dois fios** (SDA e SCL), cada um com um endereço. É como quase todo sensor moderno conversa: acelerômetro, barômetro, RTC, display OLED, expansor de portas."},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.i2c_configurar()

// o MPU6050 no endereço 0x68, registro 0x3B: seis bytes de aceleração
placa.simulador.definir_i2c(0x68, 0x3B, [0, 100, 255, 200, 1, 44])
dados := placa.i2c_ler(0x68, 0x3B, 6, 2)
assert len(dados) is 6

x := dados[0] * 256 + dados[1]
out $"aceleração X (cru): {x}"
placa.fechar()''', "lang": "df"},
 {"h2": "A leitura devolve `void` quando ninguém responde"},
 {"p": "Um endereço errado, um fio solto ou um sensor sem alimentação dão o **mesmo** resultado: silêncio. Levantar aqui obrigaria um `monitor` em volta de cada leitura de um laço que roda mil vezes; devolver `void` deixa o programa decidir:"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.i2c_configurar()

resposta := placa.i2c_ler(0x77, 0xD0, 1, 0.3)   // ninguém nesse endereço
given resposta is void:
    out "nenhum dispositivo respondeu em 0x77 — confira SDA, SCL e o 3,3 V"
otherwise:
    out resposta
placa.fechar()''', "lang": "df"},
 {"h2": "Escrever num registro"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.i2c_configurar()
// acordar o MPU6050: registro 0x6B := 0
assert placa.i2c_escrever(0x68, [0x6B, 0x00]) is 2
placa.fechar()''', "lang": "df"},
 {"h2": "Os três erros de I²C, em ordem de frequência"},
 {"table": {
   "head": ["Sintoma", "Quase sempre é"],
   "rows": [
     ["nada responde, em nenhum endereço", "faltam os resistores de *pull-up* (4,7 kΩ) — muitos módulos já os têm, e dois módulos juntos podem ter demais"],
     ["responde, mas os valores não fazem sentido", "o sensor não foi acordado: quase todos nascem em modo de repouso"],
     ["funciona perto e falha com fio longo", "I²C é de placa, não de instalação — acima de ~1 m, use um barramento diferencial"]]}},
 {"p": "E o endereço na folha de dados às vezes vem **deslocado**: 0xD0 é 0x68 escrito com o bit de leitura/escrita junto. Se o sensor não responde em nenhum endereço, tente a metade."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/sketches",
"title": "Sketches: C++ gerado e gravado",
"description": "Seis modelos prontos, o arduino-cli por baixo, e o que a linguagem NÃO faz.",
"blocos": [
 {"p": "Firmata cobre o protótipo. O que precisa rodar **sem computador** — um sensor a bateria, um controle com resposta em microssegundos — é sketch: C++ na placa. A linguagem escreve o sketch e chama o `arduino-cli` para compilar e gravar."},
 {"code": '''adopt Arcane.IoT as IoT

cycle nome in keys(IoT.sketches()):
    out $"{nome}: {IoT.sketches()[nome]["descricao"]}"
assert len(IoT.sketches()) >= 6''', "lang": "df"},
 {"table": {
   "head": ["Modelo", "Para quê"],
   "rows": [
     ["`firmata`", "o StandardFirmata — é o que torna a placa controlável daqui"],
     ["`pisca`", "o \"olá mundo\": prova que gravar funcionou"],
     ["`sensor`", "lê um analógico e escreve na serial, pronto para `iot monitorar`"],
     ["`ultrassom`", "HC-SR04 — distância em centímetros"],
     ["`dht`", "DHT11/DHT22 — temperatura e umidade"],
     ["`wifi-mqtt`", "ESP32 que publica leituras num broker MQTT"]]}},
 {"h2": "As opções entram no código"},
 {"code": '''adopt Arcane.IoT as IoT

codigo := IoT.sketch("pisca", {"led": 7, "intervalo": 120})
assert "const int LED = 7;" in codigo
assert "void setup()" in codigo and "void loop()" in codigo''', "lang": "df"},
 {"p": "Uma opção que não existe é **recusada**, e não ignorada — `opcoes.ler` de novo. Um `--lde=7` que passa calado grava o sketch com o LED errado, e a pessoa vai procurar o defeito no fio:"},
 {"code": '''adopt Arcane.IoT as IoT

monitor:
    IoT.sketch("pisca", {"lde": 7})
handle Error as e:
    out e.message''', "lang": "df"},
 {"h2": "Gravar em disco, e depois na placa"},
 {"code": '''adopt Arcane.IoT as IoT
adopt Arcane.OS as OS
adopt Arcane.IO as IO

pasta := $"{OS.temp_dir()}/df-doc-iot-{randint(100000, 999999)}"
caminho := IoT.gravar_sketch(pasta, "sensor", {"canal": 0, "velocidade": 9600})
assert "sensor.ino" in caminho
assert "Serial.begin(9600)" in IO.read(caminho)
IO.remove_tree(pasta)''', "lang": "df"},
 {"code": '''$ dataforge iot carregar /tmp/fw/sensor --fqbn=arduino:avr:uno
gravado.

$ dataforge iot compilar /tmp/fw/sensor --fqbn=esp32:esp32:esp32
Sketch uses 265417 bytes (20%) of program storage space.
compilou.''', "lang": "bash"},
 {"h2": "O que a linguagem não faz — e por quê"},
 {"p": "`IoT.compilar` e `IoT.carregar` chamam o `arduino-cli`. Compilar C++ para AVR, resolver bibliotecas e falar com o bootloader é o que ele faz, e bem; reimplementar isso seria refazer o GCC e o avrdude. O projeto prefere **dizer que depende dele** a fingir que não:"},
 {"code": '''adopt Arcane.IoT as IoT

given IoT.tem_arduino_cli():
    out "dá para compilar e gravar daqui"
otherwise:
    out "instale: brew install arduino-cli"''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Estes sketches compilam de verdade", "texto": "`pisca`, `sensor` e `ultrassom` foram compilados pelo `arduino-cli` para `arduino:renesas_uno:unor4wifi`, e `wifi-mqtt` para `esp32:esp32:esp32`. O teste que faz isso está em `tests/test_iot.py` e só roda com `DATAFORGE_ARDUINO_COMPILAR=1`, porque leva ~40 s — mas ele existe: um gerador de C++ que nunca passou por um compilador é um gerador de texto."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/mqtt",
"title": "MQTT: a placa e o resto do mundo",
"description": "Publicar, assinar, curingas e o testamento — como o painel descobre que o sensor caiu.",
"blocos": [
 {"p": "Um sensor ligado por cabo fala com um computador. Vinte sensores espalhados numa casa falam com um **broker**, e quem quiser ouve. MQTT é esse protocolo: `Arcane.IoT` traz um cliente 3.1.1 falado à mão sobre TCP, sem dependência."},
 {"code": '''adopt Arcane.IoT as IoT

// precisa de um broker: docker run -p 1883:1883 eclipse-mosquitto
c := IoT.mqtt("localhost", 1883, "sala")
c.publicar("casa/sala/temperatura", "21.5")
c.assinar("casa/+/temperatura", lambda m: out $"{m["topico"]}: {m["mensagem"]}")
sleep(500)
c.fechar()''', "lang": "df", "title": "precisa de broker"},
 {"h2": "Os curingas, e onde cada um vale"},
 {"table": {
   "head": ["Filtro", "Casa", "Não casa"],
   "rows": [
     ["`casa/sala/luz`", "`casa/sala/luz`", "qualquer outro"],
     ["`casa/+/luz`", "`casa/sala/luz`, `casa/quarto/luz`", "`casa/sala/piso/luz`"],
     ["`casa/#`", "`casa/sala/piso/luz`", "`jardim/luz`"]]}},
 {"p": "`+` casa **um** nível; `#` casa o resto, e só no fim do filtro. Publicar num curinga é recusado — eles são de assinatura, e `publicar(\"casa/+/luz\")` criaria um tópico literalmente chamado `+`."},
 {"h2": "O testamento: como se descobre que o sensor caiu"},
 {"p": "Um sensor sem energia não avisa ninguém: ele simplesmente para de publicar, e o painel fica com o último valor congelado na tela — parecendo atual. O *last will* é uma mensagem que **o broker** publica quando a conexão cai:"},
 {"code": '''adopt Arcane.IoT as IoT

c := IoT.mqtt("localhost", 1883, "estufa", "", "", 60, {
    "topico": "casa/estufa/estado",
    "mensagem": "offline",
    "reter": yes})
c.publicar("casa/estufa/estado", "online", 0, yes)
c.fechar()''', "lang": "df", "title": "precisa de broker"},
 {"p": "Com `reter := yes`, quem assinar depois recebe o último valor na hora — é o que faz um painel recém-aberto já mostrar o estado em vez de esperar a próxima leitura."},
 {"h2": "QoS: 0 e 1"},
 {"table": {
   "head": ["QoS", "Promessa", "Quando"],
   "rows": [
     ["0", "manda e esquece", "leitura periódica — a próxima chega em 5 s de qualquer forma"],
     ["1", "chega **pelo menos** uma vez (espera o PUBACK)", "um comando: \"desligar a bomba\""]]}},
 {"p": "Não há QoS 2 aqui, e a razão está escrita: ele exige guardar o estado de quatro mensagens por publicação, e quase nenhum projeto de sensor usa. Com QoS 1, o receptor precisa aguentar **repetição** — um comando \"alternar\" é perigoso, e um \"ligar\" não é."},
 {"h2": "O keepalive não é detalhe"},
 {"p": "Sem PINGREQ, o broker fecha a conexão no silêncio — e o sintoma é um painel que para de atualizar de madrugada, quando nada acontece por muito tempo. O cliente daqui tem uma thread própria para isso, e ela nasce junto com a conexão."},
 {"h2": "Quando o broker recusa"},
 {"code": '''adopt Arcane.IoT as IoT

monitor:
    IoT.mqtt("127.0.0.1", 1, "x", "", "", 60, void, 1)
handle Error as e:
    out e.message
    out e.dica              // docker run -p 1883:1883 eclipse-mosquitto''', "lang": "df"},
 {"p": "E quando ele responde mas nega, o código volta traduzido: `5` é \"não autorizado\" — o mais comum de todos, e o que mais confunde, porque a conexão TCP funcionou."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/sem-placa",
"title": "Testar IoT sem placa",
"description": "O simulador que fala o mesmo protocolo — e como um projeto de hardware passa no CI.",
"blocos": [
 {"p": "Código de hardware costuma ser código sem teste, e a razão é sempre a mesma: o teste precisaria da placa, e o CI não tem placa. `IoT.conectar_simulada` resolve isso de um jeito específico — **não** é um dublê da API, é um dispositivo do outro lado do cabo."},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
assert placa.info()["firmware"]["nome"] is "StandardFirmata.ino"
assert placa.info()["protocolo"] is "2.5"
placa.fechar()''', "lang": "df"},
 {"p": "A diferença importa: o simulador recebe os **bytes** do Firmata e responde com os bytes que a placa responderia. O parser, a máquina de estados, a partição em sete bits, o sysex — tudo isso é exercitado. Um dublê que só implementasse `escrever(pino, valor)` não provaria nada sobre o protocolo, que é justamente onde estão os erros."},
 {"h2": "O simulador deixa PERGUNTAR e deixa MENTIR"},
 {"table": {
   "head": ["Para", "Método"],
   "rows": [
     ["perguntar o estado de um pino", "`placa.simulador.pino(13)`"],
     ["perguntar o modo declarado", "`placa.simulador.modo_do_pino(9)`"],
     ["perguntar a posição de um servo", "`placa.simulador.servo(3)`"],
     ["fingir um sensor", "`placa.simulador.definir_analogico(0, 733)`"],
     ["fingir um botão", "`placa.simulador.definir_digital(2, 1)`"],
     ["fingir um dispositivo I²C", "`placa.simulador.definir_i2c(0x68, 0x3B, […])`"],
     ["fingir um `Firmata.sendString`", "`placa.simulador.mandar_texto(\"…\")`"]]}},
 {"h2": "Um teste de verdade, com `crucible`"},
 {"code": '''adopt Arcane.IoT as IoT
adopt Arcane.Crucible as Crucible

crucible "o termostato":

    trial "liga o aquecedor quando esfria":
        placa := IoT.conectar_simulada("uno")
        placa.modo(7, "saida")
        placa.modo(14, "analogico")
        placa.relatar_analogico(0)

        aquecedor := IoT.histerese(18, 21)
        placa.simulador.definir_analogico(0, 300)       // frio
        sleep(120)
        placa.escrever(7, aquecedor(IoT.tmp36(placa.analogico(0))))

        expect placa.simulador.pino(7) is 1
        placa.fechar()

    trial "e nao bate o rele na soleira":
        termostato := IoT.histerese(30, 28)
        expect termostato(31) is yes
        expect termostato(29) is yes
        expect termostato(27) is no

Crucible.run()''', "lang": "df"},
 {"h2": "O que o simulador NÃO prova"},
 {"list": [
   "**Tempo de subida** de um sinal, ruído de sensor, corrente, queda de tensão.",
   "**O cabo caindo no meio de um sysex** — o defeito mais chato do mundo real.",
   "**O bootloader**, o driver USB, o `avrdude`.",
   "Que o **seu** sensor está ligado nos pinos certos."]},
 {"p": "Por isso `tests/test_iot.py` tem duas provas que o simulador não dá: a camada serial é testada contra um **PTY de verdade** (um dispositivo tty do sistema), e os sketches gerados são compilados pelo **`arduino-cli` de verdade**. E há um teste de hardware que só roda quando alguém aponta uma placa:"},
 {"code": '''$ DATAFORGE_ARDUINO=/dev/cu.usbmodem1101 python3 -m pytest tests/test_iot.py -k verdade''', "lang": "bash"},
 {"callout": {"tipo": "nota", "titulo": "A honestidade é parte do teste", "texto": "Um teste que finge hardware e se anuncia como prova de hardware é pior que nenhum teste: ele dá confiança sem dar garantia. Cada camada daqui diz contra o que foi conferida — simulador, PTY, arduino-cli, ou placa física — e o que sobra fica escrito como o que sobra."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/quando-usar",
"title": "Firmata ou sketch: a conta",
"description": "Onde a latência do cabo mata o projeto, e onde ela não importa — com números.",
"blocos": [
 {"p": "A pergunta não é qual é melhor: é **onde o programa precisa rodar**. E a resposta sai de uma conta, não de gosto."},
 {"h2": "A latência do cabo"},
 {"p": "Cada ordem do Firmata é uma mensagem de 2 a 4 bytes atravessando a serial, e cada leitura é outra voltando. A 57600 baud, isso é sub-milissegundo no fio — mas o caminho inteiro (escrever, o USB agendar, a placa processar, responder, o driver entregar) fica na casa de **1 a 5 ms** por ida e volta."},
 {"table": {
   "head": ["O projeto precisa de", "Firmata", "Sketch"],
   "rows": [
     ["ler um sensor a cada segundo", "✓ perfeito", "exagero"],
     ["acender LED ao clicar num painel", "✓", "precisaria de protocolo próprio"],
     ["ler um encoder de motor", "✗ perde pulso", "✓ interrupção"],
     ["PWM de áudio, LED endereçável (WS2812)", "✗ não dá", "✓"],
     ["responder a um botão em < 1 ms", "✗", "✓"],
     ["funcionar sem o computador ligado", "✗ por definição", "✓"],
     ["rodar a bateria por meses", "✗", "✓ com *deep sleep*"],
     ["prototipar, calibrar, explorar um sensor novo", "✓ sem comparação", "20 s por tentativa"]]}},
 {"h2": "O meio-termo que quase sempre é a resposta"},
 {"p": "Prototipar com Firmata, e **depois** virar sketch. A calibração de um sensor leva dezenas de tentativas; fazer isso com ciclo de 20 s custa uma tarde, e com Firmata custa minutos. Quando as constantes estiverem certas, elas entram no `.ino`:"},
 {"code": '''adopt Arcane.IoT as IoT

// 1. descobrir a constante com Firmata, na bancada
placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.relatar_analogico(0)
placa.simulador.definir_analogico(0, 512)
sleep(120)
limiar := placa.analogico(0)
placa.fechar()

// 2. gerar o sketch com ela dentro
codigo := IoT.sketch("sensor", {"canal": 0, "velocidade": 9600})
assert "A0" in codigo
out $"limiar calibrado: {limiar}"''', "lang": "df"},
 {"h2": "E o terceiro caminho"},
 {"p": "Um sketch que publica em MQTT não precisa do computador **nem** de um programa esperando na ponta: ele fala com o broker, e quem quiser escuta. É o desenho de quase toda automação doméstica que funciona, e o modelo `wifi-mqtt` já sai assim."},
 {"callout": {"tipo": "atencao", "titulo": "O erro de arquitetura mais comum", "texto": "Escrever a lógica de controle no computador, por Firmata, e deixá-la controlando algo que não pode parar — uma bomba, um aquecedor, uma trava. Quando o cabo cai ou o computador reinicia, o atuador fica no último estado, para sempre. Controle que **não pode parar** mora na placa; o computador olha e manda ajustes."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/serial",
"title": "A porta serial, crua",
"description": "Quando não há Firmata do outro lado: abrir, ler linha, escrever, e o pulso de DTR que reinicia a placa.",
"blocos": [
 {"p": "Nem todo dispositivo fala Firmata. Um sketch seu que escreve com `Serial.println`, um módulo GPS, um leitor RFID, uma balança — todos falam **texto numa serial**. `IoT.abrir_serial` é a camada de baixo, e ela é escrita aqui: `termios` no macOS e no Linux, `ctypes` sobre a API do Windows. Sem `pyserial`."},
 {"code": '''adopt Arcane.IoT as IoT

// com um sketch que faz Serial.begin(9600) e Serial.println(temperatura)
porta := IoT.abrir_serial("/dev/cu.usbmodem1101", 9600, 2.0)
cycle i from 1 to 5:
    linha := porta.linha()
    given linha is not void:
        out linha
porta.fechar()''', "lang": "df", "title": "precisa de placa"},
 {"h2": "As quatro operações"},
 {"table": {
   "head": ["Chamada", "Faz"],
   "rows": [
     ["`porta.linha()`", "lê até o `\\n`; devolve `void` quando o prazo acaba"],
     ["`porta.ler(n, prazo)`", "até n bytes; devolve vazio em vez de levantar"],
     ["`porta.escrever(bytes)`", "devolve quantos foram"],
     ["`porta.esperando()`", "quantos bytes já chegaram, sem bloquear"],
     ["`porta.limpar()`", "descarta o que está no buffer — antes de um comando"],
     ["`porta.reiniciar_placa()`", "o pulso de DTR que a IDE dá ao gravar"]]}},
 {"h2": "Ler não levanta"},
 {"p": "Uma leitura vazia é o estado normal de uma serial: o dispositivo fala quando tem o que dizer. Se isso levantasse, todo laço de leitura precisaria de um `monitor` em volta — e o programa ficaria ilegível para tratar o caso mais comum de todos."},
 {"h2": "O pulso de DTR"},
 {"p": "Abrir a porta de um Arduino UNO **reinicia a placa**: o sinal DTR está ligado ao reset, e é assim que a IDE grava sem apertar botão. Consequência prática: as primeiras linhas depois de abrir costumam ser lixo do boot, e o sketch começa do zero."},
 {"code": '''adopt Arcane.IoT as IoT

porta := IoT.abrir_serial("/dev/cu.usbmodem1101", 9600, 2.0)
porta.reiniciar_placa()      // começa do zero, de propósito
sleep(2000)                  // o bootloader leva ~1,5 s
porta.limpar()               // e o lixo dele vai embora
out porta.linha()
porta.fechar()''', "lang": "df", "title": "precisa de placa"},
 {"h2": "A velocidade é conferida"},
 {"code": '''adopt Arcane.IoT as IoT

monitor:
    IoT.abrir_serial("/dev/null", 12345)     // não é uma velocidade padrão
handle Error as e:
    out e.message''', "lang": "df"},
 {"p": "Uma velocidade fora da lista é aceita pelo driver em alguns sistemas e produz bytes corrompidos em vez de erro — que é o pior resultado possível, porque parece um problema de fio."},
 {"h2": "Fechar é idempotente, e depois disso a porta recusa"},
 {"code": '''adopt Arcane.IoT as IoT

monitor:
    porta := IoT.abrir_serial("/dev/nao-existe-mesmo", 115200)
handle Error as e:
    out e.dica              // portas() mostra as que existem agora''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/painel",
"title": "Um painel para a placa",
"description": "Vitrine e Arduino no mesmo programa: gráfico ao vivo, botão que liga o relé, e o cuidado com a thread.",
"blocos": [
 {"p": "A Vitrine desenha painéis, e a placa produz números: juntar os dois é o caso que fecha o ciclo — ver o sensor num gráfico e agir com um botão. Mas há um detalhe que decide se funciona: **a página inteira roda de novo a cada interação**, e uma conexão serial não pode ser aberta a cada volta."},
 {"code": '''adopt Arcane.Vitrine as V
adopt Arcane.IoT as IoT

// V.recurso guarda o objeto POR PROCESSO: a porta abre uma vez
mark @V.recurso
action placa():
    p := IoT.conectar_simulada("uno")
    p.modo(13, "saida")
    p.modo(14, "analogico")
    p.relatar_analogico(0)
    yield p

assert placa().info()["pinos"] is 20
assert placa() is placa()            // a MESMA porta, na segunda chamada
placa().fechar()''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Sem `V.recurso`, a porta abre a cada clique", "texto": "E a segunda abertura falha, porque a porta já está tomada pela primeira — o sintoma é um painel que funciona no primeiro carregamento e morre no primeiro clique, com um erro que fala de permissão. `V.recurso` guarda o objeto por processo, que é exatamente a vida de uma porta serial."}},
 {"h2": "O painel inteiro"},
 {"code": '''adopt Arcane.Vitrine as V
adopt Arcane.IoT as IoT

mark @V.recurso
action abrir():
    p := IoT.conectar_simulada("uno")
    p.modo(13, "saida")
    p.modo(14, "analogico")
    p.relatar_analogico(0)
    p.amostragem(200)
    yield p

action pagina():
    p := abrir()
    V.titulo("Estufa")

    leitura := p.analogico(0)
    colunas := V.colunas(3)
    colunas[0].metrica("Leitura", leitura)
    colunas[1].metrica("Temperatura", $"{round(IoT.tmp36(leitura), 1)} °C")
    colunas[2].metrica("Aquecedor", "ligado" given p.ler(13) otherwise "desligado")

    given V.botao("Alternar aquecedor"):
        p.escrever(13, not p.ler(13))

    V.atualizar_a_cada(2)

// Sonda: o painel testado sem navegador
s := V.testar(pagina)
s.rodar()
assert "Estufa" in s.texto()
s.clicar("Alternar aquecedor")
assert "Aquecedor" in s.texto()''', "lang": "df"},
 {"h2": "O tempo real da Vitrine é por pergunta"},
 {"p": "`V.atualizar_a_cada(2)` reexecuta a página de dois em dois segundos — é *polling*, e está escrito assim de propósito. A Vitrine não empurra dado (não usa WebSocket nem SSE), e para um painel de sensor isso é suficiente: o que muda a cada 200 ms não precisa ser visto a cada 200 ms."},
 {"h2": "Uma rota do Kiln, para a placa"},
 {"p": "Quando o que se quer é uma API — outro sistema lendo o sensor —, o Kiln serve. E aqui vale o aviso que o `check` dá sozinho:"},
 {"code": '''adopt Arcane.IoT as IoT

// o Kiln atende UM PEDIDO POR THREAD, e a placa é uma só:
// duas rotas escrevendo no mesmo pino ao mesmo tempo perdem ordens.
// A resposta é um mutex em volta da placa.
adopt Arcane.Concurrent as C

trava := C.mutex()
placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")

action ligar(valor):
    placa.escrever(13, valor)
    yield placa.ler(13)

// com_trava toma a trava, roda, e a SOLTA mesmo se o corpo estourar —
// soltar na mão funciona até o dia em que o corpo levanta, e aí a
// próxima thread espera para sempre.
assert C.com_trava(trava, lambda => ligar(yes)) is yes
assert C.com_trava(trava, lambda => ligar(no)) is no
placa.fechar()''', "lang": "df"},
 {"p": "O `dataforge check` **avisa** quando uma `route` escreve num nome que vem de fora (`escrita-concorrente`), e uma placa compartilhada é o caso exato: a concorrência é invisível para quem escreve a rota."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/telemetria",
"title": "Telemetria: guardar o que o sensor leu",
"description": "Do pino ao banco, ao quadro e ao gráfico — e a decisão de quanto guardar.",
"blocos": [
 {"p": "Um sensor que não guarda nada responde \"quanto é agora?\". Guardar transforma isso em \"o que aconteceu de madrugada?\", que costuma ser a pergunta que importa."},
 {"h2": "Do pino para o banco"},
 {"code": '''adopt Arcane.IoT as IoT
adopt Arcane.Database as DB
adopt Arcane.OS as OS
adopt Arcane.IO as IO

pasta := $"{OS.temp_dir()}/df-doc-tel-{randint(100000, 999999)}"
IO.mkdir(pasta)
db := DB.connect($"{pasta}/estufa.db")
DB.execute(db, "CREATE TABLE leituras (quando TEXT, canal INTEGER, valor INTEGER)")

placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.relatar_analogico(0)

cycle i from 1 to 5:
    placa.simulador.definir_analogico(0, 400 + i * 30)
    sleep(60)
    DB.insert(db, "leituras", {"quando": $"t{i}", "canal": 0,
                               "valor": placa.analogico(0)})

linhas := DB.query(db, "SELECT * FROM leituras ORDER BY quando")
assert len(linhas) is 5
placa.fechar()
DB.close(db)
IO.remove_tree(pasta)''', "lang": "df"},
 {"h2": "O quadro, e a pergunta"},
 {"code": '''adopt Arcane.Quadro as Q

leituras := Q.de_vaults([
    {"hora": 0, "canal": 0, "valor": 430},
    {"hora": 1, "canal": 0, "valor": 460},
    {"hora": 2, "canal": 0, "valor": 512},
    {"hora": 0, "canal": 1, "valor": 210},
    {"hora": 1, "canal": 1, "valor": 205},
])

por_canal := leituras >> agrupar "canal" >> resumir {"valor": "media"}
assert len(por_canal) is 2
out por_canal.para_vaults()''', "lang": "df"},
 {"h2": "Quanto guardar"},
 {"p": "Um sensor a cada segundo dá 86.400 linhas por dia, e 31 milhões por ano. Quase sempre o que se quer é **agregado**: a média por minuto para a semana passada, o valor cru só para as últimas horas."},
 {"table": {
   "head": ["Idade do dado", "Resolução que costuma bastar"],
   "rows": [
     ["últimas 6 h", "cru — é onde se investiga um incidente"],
     ["últimos 7 dias", "1 minuto"],
     ["últimos 6 meses", "1 hora, com mínimo e máximo"],
     ["mais que isso", "1 dia, ou nada"]]}},
 {"p": "A agregação e a limpeza são trabalho de `supabase-cron`/`pg_cron` ou de um laço próprio — o ponto é decidir isso no começo. Um banco de sensor que cresce sem política sempre termina cheio, e a descoberta vem quando a escrita falha."},
 {"h2": "E se o painel some"},
 {"p": "Um sensor que publica em MQTT com testamento avisa que caiu; um que grava direto no banco, não. Para saber que o dado **parou de chegar**, a pergunta é sobre a última linha:"},
 {"code": '''adopt Arcane.IoT as IoT

ultima := 0
agora := 120

action saudavel(ultima_leitura, momento, prazo):
    yield momento - ultima_leitura smaller prazo

assert saudavel(115, agora, 30) is yes
assert saudavel(40, agora, 30) is no       // 80 s sem notícia: alerta''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/projeto-estufa",
"title": "Projeto: a estufa",
"description": "Sensor, relé, histerese, painel e telemetria num programa só — e as decisões que ele carrega.",
"blocos": [
 {"p": "Uma estufa é o projeto de IoT completo mais simples que existe: ela **lê** (temperatura e umidade de solo), **decide** (com histerese) e **age** (aquecedor e bomba). Todo problema desta seção aparece nela."},
 {"h2": "O programa"},
 {"code": '''adopt Arcane.IoT as IoT

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
assert estado.regando is no''', "lang": "df"},
 {"h2": "As cinco decisões que ele carrega"},
 {"table": {
   "head": ["Decisão", "O que ela evita"],
   "rows": [
     ["`defer placa.fechar()` no topo", "terminar — inclusive por erro — com a bomba ligada"],
     ["média móvel antes da histerese", "o ruído do ADC decidir por conta própria"],
     ["duas soleiras, não uma", "o relé batendo dezenas de vezes por minuto na soleira"],
     ["a leitura vira `record`", "um vault solto onde `estado[\"aquecendo\"]` com erro de digitação é `void` — e `void` é falso"],
     ["a decisão em uma ação, longe do hardware", "não dá para testar controle que só existe dentro do laço da placa"]]}},
 {"h2": "E o que falta para isto virar produção"},
 {"list": [
   "**Sair do Firmata.** Uma estufa não pode depender do computador ligado — a lógica vira sketch, e o computador passa a olhar. Ver *Firmata ou sketch*.",
   "**Um teto de tempo na bomba.** Histerese não protege de um sensor que soltou do vaso: a leitura fica em \"seco\" para sempre e a bomba não desliga nunca. Um limite duro (`no máximo 30 s por hora`) é a proteção que importa.",
   "**Telemetria.** Sem histórico, não há como saber por que a planta morreu.",
   "**Alerta.** `Arcane.Telegram` manda mensagem; o testamento do MQTT avisa quando a placa cai."]},
 {"code": '''adopt Arcane.IoT as IoT

// o teto duro, que a histerese sozinha nao da
action limitador(maximo_ms):
    gasto := [0]
    acao := lambda ligar, decorrido: (
        gasto[0] + decorrido smaller_eq maximo_ms) and ligar
    yield acao

pode := limitador(30000)
assert pode(yes, 1000) is yes
assert pode(yes, 40000) is no          // passou do teto: nao liga''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "O que este repositório conseguiu provar", "texto": "Este programa roda a cada execução da suíte, contra o simulador. Os sketches que a estufa usaria foram compilados pelo `arduino-cli` de verdade. O que **não** foi conferido aqui é a estufa física: não há placa ligada nesta máquina. `dataforge iot doctor` e `dataforge iot piscar` são o caminho para conferir isso na sua."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/receitas",
"title": "Receitas de IoT",
"description": "Botão, LDR, ultrassom, potenciômetro, fita de LED, RFID — os pedaços que todo projeto repete.",
"blocos": [
 {"p": "Os blocos que aparecem em quase todo projeto, prontos para colar. Todos rodam contra o simulador."},
 {"h2": "Botão sem resistor externo"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(2, "entrada_pullup")      // o resistor é interno

// com pull-up, o botão LIGA em 0 — ele puxa para o terra
placa.simulador.definir_digital(2, 0)
sleep(100)
apertado := not placa.ler(2)
out $"apertado: {apertado}"
placa.fechar()''', "lang": "df"},
 {"h2": "Debounce: um toque não é um toque"},
 {"p": "O contato de um botão treme por alguns milissegundos e a placa lê dez transições. A correção é temporal, e não elétrica:"},
 {"code": '''aceitos := []
ultimo := 0 - 200
cycle instante in [0, 5, 12, 300, 305, 700]:
    given instante - ultimo bigger_eq 200:
        aceitos.append(instante)
        ultimo := instante

assert aceitos is [0, 300, 700]      // os tremores sumiram''', "lang": "df"},
 {"h2": "LDR: claro ou escuro"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.relatar_analogico(0)

placa.simulador.definir_analogico(0, 800)
sleep(120)
luz := IoT.escala(placa.analogico(0), 0, 1023, 0, 100)
acender := IoT.histerese(20, 35)          // acende abaixo de 20% de luz

placa.modo(13, "saida")
placa.escrever(13, acender(luz))
assert placa.simulador.pino(13) is 0      // está claro
out $"luz: {round(luz)}%"
placa.fechar()''', "lang": "df"},
 {"h2": "Ultrassom (HC-SR04)"},
 {"p": "O HC-SR04 mede tempo de eco em microssegundos — abaixo do que o Firmata alcança. Esta é a receita que **precisa** de sketch, e ele já existe:"},
 {"code": '''adopt Arcane.IoT as IoT

codigo := IoT.sketch("ultrassom", {"gatilho": 9, "eco": 10})
assert "pulseIn" in codigo
assert "void loop()" in codigo
out "grave e leia com: dataforge iot monitorar --velocidade=9600"''', "lang": "df"},
 {"h2": "Potenciômetro que move um servo"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.relatar_analogico(0)
placa.modo(3, "servo")
placa.amostragem(20)

placa.simulador.definir_analogico(0, 1023)
sleep(80)
graus := round(IoT.escala(placa.analogico(0), 0, 1023, 0, 180))
placa.servo(3, graus)
assert placa.simulador.servo(3) is 180
placa.fechar()''', "lang": "df"},
 {"h2": "Ler vários canais de uma vez"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
cycle canal from 0 to 3:
    placa.modo(14 + canal, "analogico")
    placa.relatar_analogico(canal)
    placa.simulador.definir_analogico(canal, 100 * (canal + 1))

sleep(150)
leituras := [placa.analogico(c) cycle c in range(0, 4)]
assert leituras is [100, 200, 300, 400]
placa.fechar()''', "lang": "df"},
 {"h2": "Um laço de controle que dá para interromper"},
 {"code": '''adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
defer:
    placa.fechar()
placa.modo(13, "saida")

voltas := 0
persist yes:
    voltas += 1
    placa.escrever(13, voltas % 2 is 1)
    sleep(20)
    given voltas bigger_eq 6:
        halt

assert voltas is 6''', "lang": "df"},
 {"p": "Num programa de verdade a condição de parada vem de fora — um arquivo, um sinal, um `Arcane.Inicio.ao_encerrar`. O que **não** pode acontecer é um `persist yes` sem saída controlando um relé: `Ctrl-C` num laço assim deixa o atuador ligado."},
 {"code": '''adopt Arcane.Inicio as Inicio

desligado := []
Inicio.ao_encerrar(lambda => desligado.append("relés desligados"))
out "o encerramento está registrado"''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/iot/solucao-de-problemas",
"title": "Quando não funciona",
"description": "Os quinze sintomas de hardware, cada um com a causa que quase sempre é.",
"blocos": [
 {"p": "Depurar hardware é diferente de depurar software: a maioria dos sintomas **não dá erro**. Esta é a lista, na ordem em que os problemas aparecem."},
 {"h2": "A placa não aparece"},
 {"table": {
   "head": ["Sintoma", "Quase sempre é"],
   "rows": [
     ["`iot portas` não mostra nada", "o cabo é só de energia — é a causa nº 1, e não parece"],
     ["some e volta sozinha", "cabo ruim ou hub USB sem alimentação"],
     ["aparece no Windows como \"dispositivo desconhecido\"", "falta o driver CH340/CP2102 do clone"],
     ["não aparece dentro do contêiner", "falta `--device=/dev/ttyACM0` no `docker run`"]]}},
 {"h2": "A porta abre e nada chega"},
 {"table": {
   "head": ["Sintoma", "Quase sempre é"],
   "rows": [
     ["`conectar` dá prazo esgotado", "o StandardFirmata não está gravado"],
     ["texto ilegível no monitor", "a velocidade não é a do `Serial.begin()` do sketch"],
     ["\"permissão negada\" ou \"porta ocupada\"", "o monitor serial da IDE está aberto — duas coisas não abrem a mesma porta"],
     ["no Linux, permissão negada sempre", "o usuário não está no grupo `dialout`: `sudo usermod -aG dialout $USER`"],
     ["as primeiras linhas são lixo", "abrir a porta reinicia a placa; espere ~2 s e `limpar()`"]]}},
 {"h2": "Responde, mas errado"},
 {"table": {
   "head": ["Sintoma", "Quase sempre é"],
   "rows": [
     ["analógico sempre 0", "faltou `relatar_analogico(canal)` — é o erro nº 1 do Firmata"],
     ["analógico sempre 1023", "o pino está solto: uma entrada sem nada ligada flutua"],
     ["o botão \"não pega\"", "amostragem alta demais, ou falta o pull-up"],
     ["temperatura absurda (−273, 500)", "termistor no fim da escala: fio solto ou curto"],
     ["o valor treme muito", "ruído do ADC — média móvel resolve"]]}},
 {"h2": "Age, mas errado"},
 {"table": {
   "head": ["Sintoma", "Quase sempre é"],
   "rows": [
     ["o relé liga quando devia desligar", "módulo de relé com lógica invertida (ativo em `LOW`)"],
     ["o LED acende no talo com PWM baixo", "o pino está em `saida`, não em `pwm`"],
     ["o servo treme numa ponta", "os microssegundos de fim de curso — `configurar_servo`"],
     ["a placa reinicia quando o motor para", "falta o diodo de roda-livre; o pico indutivo derruba a alimentação"],
     ["o pino parou de funcionar", "corrente: um pino entrega ~20 mA, e motor/fita de LED precisam de driver"]]}},
 {"h2": "O diagnóstico, em ordem"},
 {"code": '''$ dataforge iot doctor --porta=/dev/cu.usbmodem1101''', "lang": "bash"},
 {"p": "Ele confere, nesta ordem: a porta existe → a porta abre → alguém responde Firmata → o `arduino-cli` está instalado. A ordem é a das causas, e a primeira falha é a que interessa — as de baixo são consequência."},
 {"h2": "Quando o problema não é o seu código"},
 {"code": '''adopt Arcane.IoT as IoT

// a prova mais barata: o caminho inteiro, contra um simulador
placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")
placa.escrever(13, yes)
assert placa.simulador.pino(13) is 1
placa.fechar()
out "o programa está certo — o que falta é do lado do fio"''', "lang": "df"},
 {"p": "Rodar a mesma lógica contra o simulador separa as duas metades em segundos. Se ela funciona ali e não na placa, o problema é elétrico, é o sketch ou é a porta — e nenhuma releitura do código vai achá-lo."},
]},
]
