// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "58 · IoT e Arduino",
  description: "10 exercícios: Arduino pelo Firmata: sensores, relé, escala e sketch.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Aplicações** · Arduino pelo Firmata: sensores, relé, escala e sketch · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 58`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[388](#388-a-primeira-placa)", "**a primeira placa**", "acenda um LED. Sem placa nenhuma: 'conectar_simulada'"], ["[389](#389-o-erro-numero-1-do-firmata)", "**o erro numero 1 do Firmata**", "leia um sensor. A placa NAO responde perguntas sobre o"], ["[390](#390-do-numero-cru-ao-valor)", "**do numero cru ao valor**", "um pino analogico devolve 0 a 1023. Ele nao e"], ["[391](#391-o-rele-que-nao-bate)", "**o rele que nao bate**", "uma leitura pura treme (512, 509, 514, 511). Num"], ["[392](#392-o-meio-termo-que-nao-existe)", "**o meio-termo que nao existe**", "um pino digital so tem dois valores. \"Meio brilho\" e o"], ["[393](#393-quem-conhece-a-placa-e-a-placa)", "**quem conhece a placa e a placa**", "cada placa tem um mapa diferente — quantos pinos"], ["[394](#394-dois-fios-muitos-sensores)", "**dois fios, muitos sensores**", "I2C liga varios dispositivos em dois fios (SDA e SCL),"], ["[395](#395-o-acento-que-quebra-o-protocolo)", "**o acento que quebra o protocolo**", "no Firmata todo byte de dado viaja PARTIDO em dois de"], ["[396](#396-quando-o-programa-precisa-rodar-na-placa)", "**quando o programa precisa rodar NA placa**", "Firmata cobre o prototipo. O que precisa rodar sem"], ["[397](#397-le-decide-age)", "**le, decide, age**", "uma estufa e o projeto de IoT completo mais simples"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "388 · a primeira placa"},
  {"p": "**Enunciado.** acenda um LED. Sem placa nenhuma: 'conectar_simulada'"},
  { code: `// poe do outro lado do cabo um simulador que fala o MESMO Firmata,
// com o mapa de pinos de uma placa de verdade.

adopt Arcane.IoT as IoT

out "== 1. conectar =="

placa := IoT.conectar_simulada("uno")
info := placa.info()
assert info["firmware"]["nome"] is "DataForge"
assert info["protocolo"] is "2.5"
assert info["pinos"] is 20
assert info["analogicos"] is 6
out $"   {info['pinos']} pinos, {info['analogicos']} canais analogicos"

out ""
out "== 2. todo pino tem um modo, e ele e declarado =="

// Sem o modo, a placa nao sabe se o pino le ou escreve.
placa.modo(13, "saida")
placa.escrever(13, yes)
assert placa.simulador.pino(13) is 1
placa.escrever(13, no)
assert placa.simulador.pino(13) is 0
out "   o LED acendeu e apagou"

out ""
out "== 3. piscar =="

cycle i from 1 to 3:
    placa.escrever(13, yes)
    sleep(20)
    placa.escrever(13, no)
    sleep(20)
out "   tres piscadas"

out ""
out "== 4. fechar DESLIGA as saidas =="

placa.escrever(13, yes)
assert placa.simulador.pino(13) is 1
placa.fechar()
assert placa.simulador.pino(13) is 0

// Terminar deixando um rele ligado e o defeito mais caro desta area:
// o resto do sistema continua, sem ninguem olhando.
out "   e fechar de novo nao e erro:"
assert placa.fechar() is no

out ""
out "== 5. depois de fechada, ela recusa =="

monitor:
    placa.escrever(13, yes)
    assert no
handle Error as e:
    out $"   {e.message}"

out "exercicio 388 ok"`, lang: 'df', title: `exercicios/58-iot/388_a_primeira_placa.df` },
  {"p": "Acender um LED é o \"olá mundo\" do hardware. Aqui ele roda **sem placa**: `IoT.conectar_simulada` põe do outro lado do cabo um simulador que fala o mesmo Firmata, com o mapa de pinos de uma placa de verdade."},
  {"h3": "Não é um dublê da API"},
  {"p": "O simulador recebe os **bytes** do protocolo e responde com os bytes que a placa responderia. O parser, a máquina de estados e a partição em sete bits são exercitados — que é onde os erros moram. Um dublê de `escrever(pino, valor)` não provaria nada disso."},
  {"h3": "`fechar` desliga as saídas"},
  {"p": "Um programa que termina deixando um relé ligado é o defeito mais caro desta área: o resto do sistema continua, sem ninguém olhando. E `fechar` é idempotente — chamá-lo num `defer` e de novo no fim não é erro."},
  {"h3": "Para experimentar"},
  {"p": "Troque `\"uno\"` por `\"mega\"` e confira `info()[\"pinos\"]`: são 70."},
  {"h2": "389 · o erro numero 1 do Firmata"},
  {"p": "**Enunciado.** leia um sensor. A placa NAO responde perguntas sobre o"},
  { code: `// analogico — ela envia sozinha, de tempos em tempos, os canais que
// voce mandou relatar. Sem isso, o pino esta certo, o sensor esta
// certo, e a leitura e zero. Sem nenhum erro.

adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")

out "== 1. o modo nao basta =="

placa.modo(14, "analogico")                 // o A0 e o pino 14
placa.simulador.definir_analogico(0, 900)   // o sensor "vale" 900
sleep(120)
assert placa.analogico(0) is 0
out "   modo declarado, sensor em 900, leitura 0 — e nada acusa"

out ""
out "== 2. e esta a linha que falta =="

placa.relatar_analogico(0)
sleep(150)
assert placa.analogico(0) is 900
out $"   agora chega: {placa.analogico(0)}"

out ""
out "== 3. a amostragem e uma troca =="

// Baixa demais enche a serial e ATRASA as ordens que voce manda;
// alta demais faz o grafico perder detalhe.
assert placa.amostragem(20) is 20
placa.simulador.definir_analogico(0, 512)
sleep(120)
assert placa.analogico(0) is 512

monitor:
    placa.amostragem(1)
    assert no
handle Error as e:
    out $"   {e.message}"

out ""
out "== 4. varios canais ao mesmo tempo =="

cycle canal from 1 to 3:
    placa.modo(14 + canal, "analogico")
    placa.relatar_analogico(canal)
    placa.simulador.definir_analogico(canal, 100 * canal)

sleep(200)
leituras := [placa.analogico(c) cycle c in range(1, 4)]
assert leituras is [100, 200, 300]
out $"   {leituras}"

out ""
out "== 5. o digital e por MUDANCA =="

// Ele nao vem periodicamente: a placa avisa quando o pino muda.
vistos := []
placa.observar(lambda e: vistos.append(e["tipo"]))
placa.modo(2, "entrada_pullup")
placa.simulador.definir_digital(2, 1)
sleep(120)
assert placa.ler(2) is yes
placa.simulador.definir_digital(2, 0)
sleep(120)
assert "digital" in vistos
out "   o observador viu a mudanca"

placa.fechar()
out "exercicio 389 ok"`, lang: 'df', title: `exercicios/58-iot/389_o_relatorio_analogico.df` },
  {"p": "A placa **não responde perguntas** sobre o analógico: ela envia sozinha, de tempos em tempos, os canais que você mandou relatar. Sem `relatar_analogico(canal)`, o pino está certo, o sensor está certo, e a leitura é **zero** — sem nenhum erro."},
  {"p": "É o defeito que mais custa tempo a quem começa, porque não há nada para depurar: o programa está correto do ponto de vista de qualquer leitura."},
  {"h3": "A amostragem é uma troca"},
  {"table": {"head": ["Muito baixa", "Muito alta"], "rows": [["enche a serial e **atrasa as ordens que você manda**", "o gráfico perde detalhe"], ["o LED demora a responder ao clique", "um botão lido por relatório parece que \"não pegou\""]]}},
  {"p": "Para temperatura, 500 ms é generoso. Para um potenciômetro que move um servo, 20 ms."},
  {"h3": "O digital é por mudança"},
  {"p": "Ele não vem periodicamente: a placa avisa quando o pino muda de estado. `placa.observar(acao)` recebe esses eventos; `placa.ler(pino)` devolve o **último** valor relatado, e não uma pergunta ao vivo."},
  {"h2": "390 · do numero cru ao valor"},
  {"p": "**Enunciado.** um pino analogico devolve 0 a 1023. Ele nao e"},
  { code: `// temperatura, nem luz: e o quanto da tensao de referencia chegou
// ali. Transformar isso em grandeza e a parte que todo projeto
// refaz — e onde os mesmos erros acontecem.

adopt Arcane.IoT as IoT

out "== 1. escala LIMITA por padrao =="

meio := IoT.escala(512, 0, 1023, 0, 100)
assert meio > 50.0 and meio < 50.1

// O 'map()' do Arduino NAO limita, e ruido faz um ADC de 10 bits
// devolver 1024 de vez em quando: no painel isso vira 101%.
assert IoT.escala(2000, 0, 1023, 0, 100) is 100
assert IoT.escala(0 - 5, 0, 1023, 0, 100) is 0
out "   fora da faixa, ela para nas pontas"

// E quem QUER extrapolar pede.
assert IoT.escala(2000, 0, 1023, 0, 100, no) > 100
out "   com limitar := no, ela extrapola"

out ""
out "== 2. uma faixa de largura zero e recusada =="

monitor:
    IoT.escala(1, 5, 5, 0, 10)
    assert no
handle Error as e:
    out $"   {e.message}"

out ""
out "== 3. a tensao depende da PLACA =="

assert IoT.tensao(1023) is 5.0                      // UNO: 10 bits, 5 V
assert round(IoT.tensao(4095, 3.3, 12), 2) is 3.3   // ESP32: 12 bits
assert round(IoT.tensao(2048, 3.3, 12), 2) is 1.65
out "   a mesma leitura em duas placas e duas tensoes"

out ""
out "== 4. TMP36: uma reta, com um deslocamento =="

// A folha de dados: 750 mV a 25 graus, 10 mV por grau. O
// deslocamento de 500 mV e o que quase todo mundo esquece.
leitura := 0.75 / 5.0 * 1023
t := IoT.tmp36(leitura)
assert t > 24.5 and t < 25.5
out $"   {round(t, 1)} graus"

out ""
out "== 5. NTC: e a ponta da escala nao e temperatura =="

// Com o termistor na resistencia nominal, o divisor le a metade.
assert IoT.ntc(1023 / 2) > 24.7 and IoT.ntc(1023 / 2) < 25.3

// Em 0 ou 1023 a equacao divide por zero ou tira log de zero, e o
// que sai e um numero absurdo com cara de temperatura. Um
// termostato que ve -273 liga o aquecedor e nao desliga mais.
cycle ponta in [0, 1023]:
    monitor:
        IoT.ntc(ponta)
        assert no
    handle Error as e:
        out $"   {ponta}: {e.message}"

out ""
out "== 6. divisor: quando o sensor e uma resistencia =="

// LDR, umidade de solo, potenciometro: tudo vira resistencia.
r := IoT.divisor(1023 / 2)
assert r > 9900 and r < 10100
out $"   {round(r)} ohms"

out "exercicio 390 ok"`, lang: 'df', title: `exercicios/58-iot/390_escala_e_tensao.df` },
  {"p": "Um pino analógico devolve 0 a 1023. Ele não é temperatura, nem luz: é o quanto da tensão de referência chegou ali. Transformar isso em grandeza é a parte que todo projeto refaz — e onde os mesmos erros acontecem."},
  {"h3": "`escala` limita por padrão"},
  {"p": "O `map()` do Arduino **não** limita, e ruído faz um ADC de 10 bits devolver 1024 de vez em quando: no painel isso vira 101%, e num controle de motor vira um valor fora da faixa do PWM. Aqui o padrão é limitar, e `limitar := no` é escolha explícita de quem quer extrapolar."},
  {"h3": "A tensão depende da placa"},
  {"table": {"head": ["Placa", "Bits", "Referência"], "rows": [["UNO, Nano, Mega", "10 (0–1023)", "5 V"], ["ESP32", "12 (0–4095)", "3,3 V"]]}},
  {"p": "A mesma leitura nas duas é uma tensão diferente — e ligar um sensor de 5 V direto num ESP32 costuma matar o pino."},
  {"h3": "A ponta da escala não é temperatura"},
  {"p": "Com a leitura em 0 ou 1023, a equação do termistor divide por zero ou tira log de zero, e o que sai é um número absurdo **com cara de temperatura**. Um termostato que vê −273 °C liga o aquecedor e não desliga mais. Por isso `ntc` recusa as pontas: ali não é frio nem calor, é fio solto ou curto."},
  {"h2": "391 · o rele que nao bate"},
  {"p": "**Enunciado.** uma leitura pura treme (512, 509, 514, 511). Num"},
  { code: `// grafico isso e grama; num controle, e o rele chaveando dezenas de
// vezes por minuto — e e assim que um contato se queima.

adopt Arcane.IoT as IoT

out "== 1. a media movel ESQUECE =="

media := IoT.media_movel(3)
assert media(10) is 10
assert media(20) is 15
assert media(30) is 20
assert media(40) is 30              // o 10 saiu da janela
out "   janela de 3: a quarta leitura empurra a primeira para fora"

out ""
out "== 2. uma soleira so faz o rele bater =="

// Ligar acima de 30 e desligar abaixo de 30: com a temperatura EM
// 30, cada tremor de leitura e um chaveamento.
simples := lambda v: v bigger 30
batidas := 0
anterior := no
cycle v in [29.9, 30.1, 29.8, 30.2, 29.9, 30.1]:
    atual := simples(v)
    given atual is not anterior:
        batidas += 1
    anterior := atual
assert batidas is 5
out $"   seis leituras em volta de 30, {batidas} chaveamentos"

out ""
out "== 3. com DUAS soleiras, nenhum =="

ventoinha := IoT.histerese(30, 28)
batidas := 0
anterior := no
cycle v in [29.9, 30.1, 29.8, 30.2, 29.9, 30.1]:
    atual := ventoinha(v)
    given atual is not anterior:
        batidas += 1
    anterior := atual
assert batidas is 1
out $"   as mesmas leituras, {batidas} chaveamento"

out ""
out "== 4. ela SEGURA o estado no meio =="

termostato := IoT.histerese(30, 28)
assert termostato(29) is no         // subindo, ainda nao
assert termostato(31) is yes
assert termostato(29) is yes        // no meio, segura
assert termostato(27) is no
out "   liga em 30, so desliga em 28"

out ""
out "== 5. invertendo, ela liga ABAIXO =="

// E o umidificador, o aquecedor, a bomba.
umidificador := IoT.histerese(40, 50)
assert umidificador(45) is no
assert umidificador(35) is yes
assert umidificador(45) is yes
assert umidificador(55) is no
out "   liga abaixo de 40, so desliga em 50"

out ""
out "== 6. duas soleiras iguais sao UMA =="

monitor:
    IoT.histerese(30, 30)
    assert no
handle Error as e:
    out $"   {e.message}"

out "exercicio 391 ok"`, lang: 'df', title: `exercicios/58-iot/391_media_e_histerese.df` },
  {"p": "Uma leitura pura treme: 512, 509, 514, 511. Num gráfico isso é grama; num controle, é o relé chaveando dezenas de vezes por minuto — e é assim que um contato se queima."},
  {"h3": "Média móvel: a resposta mais barata"},
  {"p": "Ela **esquece**: numa janela de 3, a quarta leitura empurra a primeira para fora. Janela grande suaviza mais e responde mais devagar; é uma troca, e não uma melhoria."},
  {"h3": "Histerese: duas soleiras, não uma"},
  {"p": "Ligar acima de 30 e desligar abaixo de 30 faz o relé chavear a cada tremor quando a temperatura fica **em** 30. Medido no exercício: as mesmas seis leituras dão **5 chaveamentos** com uma soleira e **1** com duas."},
  {"p": "No meio da faixa ela **segura o estado** — e é isso que a torna um controle, e não um comparador."},
  {"h3": "Invertendo, ela liga abaixo"},
  {"p": "`IoT.histerese(40, 50)` liga abaixo de 40 e só desliga em 50: é o umidificador, o aquecedor, a bomba. Duas soleiras iguais são recusadas, porque isso é uma soleira só com outro nome."},
  {"h2": "392 · o meio-termo que nao existe"},
  {"p": "**Enunciado.** um pino digital so tem dois valores. \"Meio brilho\" e o"},
  { code: `// pino ligando e desligando rapido o bastante para o olho — ou o
// motor — nao notar. E o PWM.

adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")

out "== 1. o modo e DECLARADO, nunca adivinhado =="

// Declarar por conta propria seria conveniente e errado: um pino em
// 'saida' recebendo PWM acende no talo, e quem le o programa nao
// veria onde o modo mudou.
monitor:
    placa.pwm(9, 128)
    assert no
handle Error as e:
    out $"   {e.message}"

placa.modo(9, "pwm")
assert placa.pwm(9, 128) is 128
out "   com o modo declarado, passa"

out ""
out "== 2. a faixa e 0 a 255 =="

cycle brilho in [0, 64, 128, 192, 255]:
    placa.pwm(9, brilho)
assert placa.simulador.pino(9) is 255

monitor:
    placa.pwm(9, 300)
    assert no
handle Error as e:
    out $"   {e.message}"

out ""
out "== 3. e so alguns pinos fazem PWM =="

// Num UNO: 3, 5, 6, 9, 10 e 11. E quem diz isso e a PLACA.
assert "pwm" in placa.capacidades(9)
assert not ("pwm" in placa.capacidades(13))

monitor:
    placa.modo(13, "pwm")
    assert no
handle Error as e:
    out $"   {e.message}"
    out $"   {e.nota}"

out ""
out "== 4. servo: posicao, nao velocidade =="

placa.modo(3, "servo")
cycle graus in [0, 90, 180, 90]:
    placa.servo(3, graus)
assert placa.simulador.servo(3) is 90

monitor:
    placa.servo(3, 200)
    assert no
handle Error as e:
    out $"   {e.message}"

out ""
out "== 5. cada servo tem o seu fim de curso =="

// Quando o braco treme numa ponta, e isto.
assert placa.configurar_servo(3, 600, 2300) is "servo"
placa.servo(3, 0)
assert placa.simulador.servo(3) is 0
out "   os microssegundos das duas pontas, ajustados"

placa.fechar()
out "exercicio 392 ok"`, lang: 'df', title: `exercicios/58-iot/392_pwm_e_servo.df` },
  {"p": "Um pino digital só tem dois valores. \"Meio brilho\" é o pino ligando e desligando rápido o bastante para o olho — ou o motor — não notar. É o PWM, de 0 a 255."},
  {"h3": "O modo é declarado, nunca adivinhado"},
  {"p": "Declarar por conta própria seria conveniente e **errado**: um pino em `saida` recebendo PWM acende no talo, e quem lê o programa não veria onde o modo mudou. Por isso `pwm` e `servo` exigem o modo já declarado."},
  {"h3": "Quem diz o que o pino faz é a placa"},
  {"p": "Num UNO, só 3, 5, 6, 9, 10 e 11 fazem PWM — e essa lista vem da **resposta de capacidade** da placa, não de uma tabela escrita na linguagem. Uma tabela envelheceria na primeira placa nova, e UNO, Mega e ESP32 têm mapas diferentes."},
  {"h3": "Servo é posição"},
  {"p": "`servo(3, 90)` não é \"gire até 90\"; é \"fique em 90\". E cada servo tem os seus microssegundos de fim de curso: quando o braço treme numa ponta, é `configurar_servo` que resolve."},
  {"h2": "393 · quem conhece a placa e a placa"},
  {"p": "**Enunciado.** cada placa tem um mapa diferente — quantos pinos"},
  { code: `// digitais, quais fazem PWM, quantos canais analogicos. Escrever
// esse mapa na linguagem seria errar na primeira placa nova.

adopt Arcane.IoT as IoT

out "== 1. os modelos que o simulador conhece =="

m := IoT.modelos()
assert m["uno"]["digitais"] is 14 and m["uno"]["analogicos"] is 6
assert m["mega"]["digitais"] is 54
assert m["esp32"]["tensao"] is 3.3
out $"   {len(m)} modelos: {sorted(keys(m))}"

out ""
out "== 2. o PWM nao esta em todo pino =="

assert 11 in m["uno"]["pwm"]
assert not (4 in m["uno"]["pwm"])
out $"   numa UNO: {m['uno']['pwm']}"

out ""
out "== 3. e a PLACA confirma, pelo protocolo =="

uno := IoT.conectar_simulada("uno")
assert "pwm" in uno.capacidades(9)
assert "servo" in uno.capacidades(9)
assert not ("pwm" in uno.capacidades(13))
assert "saida" in uno.capacidades(13)

// Um pino que nao existe e outro erro, com outra mensagem.
monitor:
    uno.modo(99, "saida")
    assert no
handle Error as e:
    out $"   {e.message}"
    out $"   {e.nota}"

out ""
out "== 4. uma Mega tem mais, e o Firmata os ve =="

mega := IoT.conectar_simulada("mega")
assert mega.info()["pinos"] is 70
mega.modo(53, "saida")                  // um pino que a UNO nao tem
mega.escrever(53, yes)
assert mega.simulador.pino(53) is 1
out "   o pino 53 respondeu"

monitor:
    uno.modo(53, "saida")               // e na UNO, nao
    assert no
handle Error as e:
    out $"   na UNO: {e.message}"

out ""
out "== 5. um modelo que nao existe e recusado com a lista =="

monitor:
    IoT.simulador("commodore-64")
    assert no
handle Error as e:
    out $"   {e.message}"

uno.fechar()
mega.fechar()
out "exercicio 393 ok"`, lang: 'df', title: `exercicios/58-iot/393_as_capacidades.df` },
  {"p": "Cada placa tem um mapa diferente: quantos pinos digitais, quais fazem PWM, quantos canais analógicos, qual a tensão e quantos bits o conversor tem. Escrever esse mapa na linguagem seria errar na primeira placa nova."},
  {"p": "Com a placa ligada, quem responde é ela — pela **resposta de capacidade** do Firmata, que o cliente pede logo depois de conectar."},
  {"h3": "Três números que mudam com a placa"},
  {"table": {"head": ["", "UNO, Nano, Mega", "ESP32"], "rows": [["tensão", "5 V", "**3,3 V**"], ["conversor", "10 bits (0–1023)", "**12 bits (0–4095)**"], ["FQBN", "`arduino:avr:uno`", "`esp32:esp32:esp32`"]]}},
  {"p": "Ligar um sensor de 5 V direto num ESP32 costuma matar o pino — e a leitura dele vai a 4095, não a 1023. Os dois erros aparecem como número errado, não como falha."},
  {"h3": "Duas mensagens diferentes"},
  {"p": "Um pino que **não existe** e um pino que **não faz aquilo** são erros distintos, e a mensagem de cada um diz o que fazer: a primeira mostra a faixa da placa, a segunda lista o que aquele pino aceita."},
  {"h2": "394 · dois fios, muitos sensores"},
  {"p": "**Enunciado.** I2C liga varios dispositivos em dois fios (SDA e SCL),"},
  { code: `// cada um com um endereco. E como quase todo sensor moderno
// conversa: acelerometro, barometro, RTC, display.

adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")
placa.i2c_configurar()

out "== 1. ler um registro =="

// O MPU6050 em 0x68, registro 0x3B: seis bytes de aceleracao.
placa.simulador.definir_i2c(0x68, 0x3B, [0, 100, 255, 200, 1, 44])
dados := placa.i2c_ler(0x68, 0x3B, 6, 2)
assert len(dados) is 6
assert dados is [0, 100, 255, 200, 1, 44]

// Os valores vem em dois bytes: alto primeiro.
x := dados[0] * 256 + dados[1]
assert x is 100
out $"   aceleracao X (cru): {x}"

out ""
out "== 2. silencio devolve void, e NAO levanta =="

// Endereco errado, fio solto ou sensor sem alimentacao dao o mesmo
// resultado: nada. Levantar aqui obrigaria um 'monitor' em volta de
// cada leitura de um laco que roda mil vezes.
resposta := placa.i2c_ler(0x77, 0xD0, 1, 0.3)
assert resposta is void
out "   ninguem em 0x77 — e o programa decide o que fazer"

given resposta is void:
    out "   confira SDA, SCL, o 3,3 V e os resistores de pull-up"

out ""
out "== 3. escrever num registro =="

// Quase todo sensor nasce em modo de repouso: acordar e a primeira
// escrita de qualquer driver.
assert placa.i2c_escrever(0x68, [0x6B, 0x00]) is 2
out "   dois bytes: o registro e o valor"

out ""
out "== 4. dois dispositivos no MESMO par de fios =="

placa.simulador.definir_i2c(0x76, 0xF7, [80, 0, 0])     // BMP280
placa.simulador.definir_i2c(0x68, 0x75, [104])          // WHO_AM_I

assert placa.i2c_ler(0x76, 0xF7, 3, 2) is [80, 0, 0]
assert placa.i2c_ler(0x68, 0x75, 1, 2) is [104]
out "   o endereco e o que os separa"

out ""
out "== 5. o endereco da folha de dados as vezes vem DESLOCADO =="

// 0xD0 e 0x68 escrito com o bit de leitura/escrita junto. Se o
// sensor nao responde em nenhum endereco, tente a metade.
assert 0xD0 ~/ 2 is 0x68
out "   0xD0 / 2 = 0x68"

placa.fechar()
out "exercicio 394 ok"`, lang: 'df', title: `exercicios/58-iot/394_i2c.df` },
  {"p": "I²C liga vários dispositivos em **dois fios** (SDA e SCL), cada um com um endereço. É como quase todo sensor moderno conversa: acelerômetro, barômetro, RTC, display OLED, expansor de portas."},
  {"h3": "O silêncio é uma resposta"},
  {"p": "Endereço errado, fio solto ou sensor sem alimentação dão o **mesmo** resultado no barramento: nada. `i2c_ler` devolve `void` em vez de levantar — levantar obrigaria um `monitor` em volta de cada leitura de um laço que roda mil vezes."},
  {"p": "E o simulador fica calado de verdade num endereço sem dispositivo. Devolver zeros ali faria ele ensinar o contrário do que acontece com um fio solto: um sensor \"presente\" medindo nada."},
  {"h3": "Os três erros de I²C, em ordem de frequência"},
  {"table": {"head": ["Sintoma", "Quase sempre é"], "rows": [["nada responde, em nenhum endereço", "faltam os *pull-ups* de 4,7 kΩ (ou há dois módulos com eles)"], ["responde, mas os valores não fazem sentido", "o sensor não foi acordado — quase todos nascem em repouso"], ["funciona perto e falha com fio longo", "I²C é de placa, não de instalação"]]}},
  {"h3": "O endereço deslocado"},
  {"p": "`0xD0` é `0x68` escrito com o bit de leitura/escrita junto. Se o sensor não responde em nenhum endereço, tente a metade."},
  {"h2": "395 · o acento que quebra o protocolo"},
  {"p": "**Enunciado.** no Firmata todo byte de dado viaja PARTIDO em dois de"},
  { code: `// sete bits — o oitavo marca comando. Ler so o primeiro de cada par
// devolve a metade baixa: em ASCII ninguem nota, porque ali o bit 7
// e zero. Num acento, "ola" vira "olC!".

adopt Arcane.IoT as IoT

placa := IoT.conectar_simulada("uno")

out "== 1. o sketch fala com Firmata.sendString =="

placa.simulador.mandar_texto("calibracao concluida")
sleep(120)
assert placa.textos()[0] is "calibracao concluida"
out $"   {placa.textos()[0]}"

out ""
out "== 2. e com acento tambem =="

placa.simulador.mandar_texto("temperatura: 21,5 graus — leitura ok")
sleep(120)
assert "—" in placa.textos()[1]
assert "graus" in placa.textos()[1]
out $"   {placa.textos()[1]}"

texto := "ola, ceu de acucar: ção, ã, ê, ü"
placa.simulador.mandar_texto(texto)
sleep(120)
assert placa.textos()[2] is texto
out $"   {placa.textos()[2]}"

out ""
out "== 3. por que isso quebra =="

// 'ç' em UTF-8 sao dois bytes, e cada um deles tem o bit 7 LIGADO.
// Partir em sete bits e obrigatorio; esquecer de juntar de volta
// devolve a metade baixa, e o defeito fica escondido ate a primeira
// mensagem em portugues.
bytes_de_c := len("ç")
assert bytes_de_c is 1               // um caractere...
out "   um caractere, dois bytes no fio, quatro no Firmata"

out ""
out "== 4. o observador tambem ve o texto =="

vistos := []
placa.observar(lambda e: vistos.append(e))
placa.simulador.mandar_texto("pronto")
sleep(120)
tipos := [e["tipo"] cycle e in vistos]
assert "texto" in tipos
out "   chega como evento, e nao so na lista"

out ""
out "== 5. e por que isso e o 'println' de quem usa Firmata =="

// Depurar um sketch e escrever na serial. Com o Firmata ocupando a
// porta, 'Serial.println' estragaria o protocolo — a mensagem tem
// de vir DENTRO dele.
assert len(placa.textos()) is 4
out $"   {len(placa.textos())} mensagens, e o protocolo intacto"

placa.fechar()
out "exercicio 395 ok"`, lang: 'df', title: `exercicios/58-iot/395_texto_e_sete_bits.df` },
  {"p": "No Firmata todo byte de dado viaja **partido** em dois de sete bits: o oitavo é reservado para marcar comando. Ler só o primeiro de cada par devolve a metade baixa de cada byte."},
  {"p": "Em ASCII ninguém nota, porque ali o bit 7 é zero. Num acento, `\"olá\"` vira `\"olC!\"` — e o defeito fica escondido até a primeira mensagem em português. Foi exatamente assim que ele apareceu neste repositório."},
  {"h3": "Por que `ç` é o caso"},
  {"p": "Em UTF-8, `ç` são **dois** bytes, e cada um deles tem o bit 7 ligado. No fio do Firmata viram quatro. Partir é obrigatório; esquecer de juntar de volta é o bug."},
  {"h3": "`sendString` é o `println` de quem usa Firmata"},
  {"p": "Com o Firmata ocupando a porta, um `Serial.println` do sketch estragaria o protocolo: a mensagem tem de vir **dentro** dele. `placa.textos()` devolve o que chegou, e `placa.observar` entrega como evento."},
  {"h2": "396 · quando o programa precisa rodar NA placa"},
  {"p": "**Enunciado.** Firmata cobre o prototipo. O que precisa rodar sem"},
  { code: `// computador — um sensor a bateria, um controle com resposta em
// microssegundos — e sketch: C++ na placa. A linguagem escreve o
// sketch, e o arduino-cli compila e grava.

adopt Arcane.IoT as IoT
adopt Arcane.OS as OS
adopt Arcane.IO as IO

out "== 1. os modelos que existem =="

modelos := IoT.sketches()
assert len(modelos) >= 6
cycle nome in sorted(keys(modelos)):
    out $"   {nome}: {modelos[nome]['descricao']}"

out ""
out "== 2. todo modelo gera C++ valido =="

cycle nome in keys(modelos):
    codigo := IoT.sketch(nome)
    assert "void setup()" in codigo
    assert "void loop()" in codigo
    assert not ("{led}" in codigo)      // nada por substituir
out "   setup, loop, e nenhum marcador esquecido"

out ""
out "== 3. as opcoes entram no codigo =="

codigo := IoT.sketch("pisca", {"led": 7, "intervalo": 120})
assert "const int LED = 7;" in codigo
assert "INTERVALO = 120" in codigo
out "   o LED e o intervalo foram para dentro do .ino"

out ""
out "== 4. uma opcao que nao existe e RECUSADA =="

// Um '--lde=7' que passa calado grava o sketch com o LED errado, e
// a pessoa vai procurar o defeito no fio.
monitor:
    IoT.sketch("pisca", {"lde": 7})
    assert no
handle Error as e:
    out $"   {e.message}"

out ""
out "== 5. o arquivo tem o NOME DA PASTA =="

// Um .ino solto nao compila, e o erro do arduino-cli nao diz por que.
pasta := $"{OS.temp_dir()}/df-396-{randint(100000, 999999)}"
caminho := IoT.gravar_sketch(pasta, "sensor", {"canal": 0, "velocidade": 9600})
assert "sensor/sensor.ino" in caminho
assert "Serial.begin(9600)" in IO.read(caminho)
out "   pasta 'sensor', arquivo 'sensor.ino'"
IO.remove_tree(pasta)

out ""
out "== 6. o firmata gerado fala a velocidade certa =="

// 57600 e a do firmware; 9600 nao conversa com ele.
assert "Serial.begin(57600)" in IoT.sketch("firmata")
out "   57600, que e a que IoT.conectar usa"

// E ele NAO usa a biblioteca Firmata. O 'Boards.h' dela traz a tabela
// de pinos de cada placa escrita a mao, e para nas placas de ate 2018:
// num UNO R4 e num ESP32 ela responde '#error "Please edit Boards.h"'.
// Aqui o mapa e perguntado ao core, e as duas placas funcionam.
assert "#include <Firmata.h>" not in IoT.sketch("firmata")
assert "NUM_DIGITAL_PINS" in IoT.sketch("firmata")
out "   sem a biblioteca: o mapa de pinos vem do core"

out ""
out "== 7. compilar e gravar chamam o arduino-cli =="

// Reimplementar isso seria refazer o GCC e o avrdude. O projeto
// prefere dizer que depende dele a fingir que nao.
given IoT.tem_arduino_cli():
    out "   ele esta instalado: da para compilar e gravar daqui"
otherwise:
    out "   nao esta instalado — 'brew install arduino-cli'"

out "exercicio 396 ok"`, lang: 'df', title: `exercicios/58-iot/396_sketch_gerado.df` },
  {"p": "Firmata cobre o protótipo. O que precisa rodar **sem computador** — um sensor a bateria, um controle com resposta em microssegundos — é sketch: C++ na placa. A linguagem escreve o sketch, e o `arduino-cli` compila e grava."},
  {"h3": "O arquivo tem o nome da pasta"},
  {"p": "Um `.ino` solto não compila, e o erro do `arduino-cli` não diz por quê. `gravar_sketch(\"/tmp/fw\", \"sensor\")` cria `/tmp/fw/sensor/sensor.ino` — a pasta e o arquivo com o mesmo nome, que é o que o Arduino exige."},
  {"h3": "Uma opção que não existe é recusada"},
  {"p": "`opcoes.ler` de novo: um `--lde=7` que passasse calado gravaria o sketch com o LED errado, e a pessoa iria procurar o defeito no fio."},
  {"h3": "57600, e não 9600"},
  {"p": "É a velocidade do firmware. Um sketch de Firmata com `Serial.begin(9600)` compila, grava, e **não conversa** com ninguém."},
  {"h3": "O que a linguagem não faz"},
  {"p": "`IoT.compilar` e `IoT.carregar` chamam o `arduino-cli`. Compilar C++ para AVR, resolver bibliotecas e falar com o bootloader é o que ele faz, e bem; reimplementar isso seria refazer o GCC e o avrdude. O projeto prefere dizer que depende dele a fingir que não."},
  {"h2": "397 · le, decide, age"},
  {"p": "**Enunciado.** uma estufa e o projeto de IoT completo mais simples"},
  { code: `// que existe. Ela LE (temperatura e umidade de solo), DECIDE (com
// histerese) e AGE (aquecedor e bomba). Todo problema da area
// aparece nela.

adopt Arcane.IoT as IoT

steady TEMPERATURA := 0        // A0 — TMP36
steady SOLO := 1               // A1 — sensor resistivo
steady AQUECEDOR := 7          // rele
steady BOMBA := 8              // rele

record Estado:
    graus: Float
    umidade: Float
    aquecendo: Boolean
    regando: Boolean

action abrir(modelo):
    p := IoT.conectar_simulada(modelo)
    p.modo(AQUECEDOR, "saida")
    p.modo(BOMBA, "saida")
    p.modo(14 + TEMPERATURA, "analogico")
    p.modo(14 + SOLO, "analogico")
    p.relatar_analogico(TEMPERATURA)
    p.relatar_analogico(SOLO)
    p.amostragem(50)
    yield p

// A decisao mora FORA do laco da placa: sem isso nao da para testar
// um controle sem hardware.
action ciclo(placa, suavizar, aquecedor, bomba):
    graus := IoT.tmp36(suavizar(placa.analogico(TEMPERATURA)))
    umidade := IoT.escala(placa.analogico(SOLO), 0, 1023, 0, 100)
    aquecendo := aquecedor(graus)
    regando := bomba(umidade)
    placa.escrever(AQUECEDOR, aquecendo)
    placa.escrever(BOMBA, regando)
    yield Estado(round(graus, 1), round(umidade, 1), aquecendo, regando)

out "== 1. frio e seco: os dois ligam =="

placa := abrir("uno")
defer:
    placa.fechar()              // os dois reles desligam ao sair

suavizar := IoT.media_movel(5)
aquecedor := IoT.histerese(18, 21)      // liga abaixo de 18
bomba := IoT.histerese(30, 45)          // liga abaixo de 30% de umidade

placa.simulador.definir_analogico(TEMPERATURA, 123)   // ~10 graus
placa.simulador.definir_analogico(SOLO, 200)          // ~20%
sleep(150)

estado := ciclo(placa, suavizar, aquecedor, bomba)
assert estado.aquecendo is yes and estado.regando is yes
assert placa.simulador.pino(AQUECEDOR) is 1
out $"   {estado.graus} graus, solo {estado.umidade}% — aquecedor e bomba ligados"

out ""
out "== 2. aqueceu e molhou: os dois desligam =="

placa.simulador.definir_analogico(TEMPERATURA, 400)   // ~72 graus
placa.simulador.definir_analogico(SOLO, 700)          // ~68%
sleep(150)
cycle i from 1 to 5:                                   // a janela da media
    estado := ciclo(placa, suavizar, aquecedor, bomba)
    sleep(20)
assert estado.aquecendo is no and estado.regando is no
assert placa.simulador.pino(BOMBA) is 0
out $"   {estado.graus} graus, solo {estado.umidade}% — os dois desligados"

out ""
out "== 3. no MEIO da faixa, a histerese segura =="

placa.simulador.definir_analogico(SOLO, 400)          // ~39%: entre 30 e 45
sleep(120)
cycle i from 1 to 3:
    estado := ciclo(placa, suavizar, aquecedor, bomba)
assert estado.regando is no                            // estava desligada
out "   entre as duas soleiras, ela mantem o estado"

out ""
out "== 4. o record evita a chave com erro de digitacao =="

// Num vault solto, estado["aquecndo"] seria void — e void e falso.
monitor:
    out estado.aquecndo
    assert no
handle Error as e:
    out $"   {e.message}"

out ""
out "== 5. o teto duro que a histerese NAO da =="

// Histerese nao protege de um sensor que soltou do vaso: a leitura
// fica em "seco" para sempre, e a bomba nao desliga nunca.
action limitador(maximo_ms):
    gasto := [0]
    action pode(ligar, decorrido):
        given not ligar:
            yield no
        given gasto[0] + decorrido bigger maximo_ms:
            yield no
        gasto[0] := gasto[0] + decorrido
        yield yes
    yield pode

pode := limitador(30000)
assert pode(yes, 10000) is yes
assert pode(yes, 10000) is yes
assert pode(yes, 20000) is no           // passou do teto da hora
out "   30 s por hora, e nem o sensor quebrado alaga a casa"

out ""
out "== 6. e o defer desliga tudo, inclusive no erro =="

monitor:
    placa.escrever(AQUECEDOR, yes)
    trigger "um erro no meio do ciclo"
handle Error:
    out "   falhou no meio — e o programa ainda fecha a placa"

out "exercicio 397 ok"`, lang: 'df', title: `exercicios/58-iot/397_a_estufa.df` },
  {"p": "Uma estufa é o projeto de IoT completo mais simples que existe: ela **lê** (temperatura e umidade de solo), **decide** (com histerese) e **age** (aquecedor e bomba). Todo problema da área aparece nela."},
  {"h3": "As cinco decisões que o programa carrega"},
  {"table": {"head": ["Decisão", "O que ela evita"], "rows": [["`defer` no topo", "terminar — inclusive por erro — com a bomba ligada"], ["média móvel antes da histerese", "o ruído do ADC decidir por conta própria"], ["duas soleiras, não uma", "o relé batendo dezenas de vezes por minuto"], ["a leitura vira `record`", "`estado[\"aquecndo\"]` num vault é `void`, e `void` é falso"], ["a decisão numa ação, longe do hardware", "não dá para testar controle que só existe dentro do laço da placa"]]}},
  {"h3": "O teto duro que a histerese não dá"},
  {"p": "Histerese não protege de um sensor que soltou do vaso: a leitura fica em \"seco\" para sempre, e a bomba não desliga nunca. O limite por tempo (`no máximo 30 s por hora`) é a proteção que importa, e ela é de outra natureza — não olha o sensor, olha o atuador."},
  {"h3": "O que falta para isto virar produção"},
  {"p": "Sair do Firmata (uma estufa não pode depender do computador ligado), telemetria (sem histórico não há como saber por que a planta morreu) e alerta (o testamento do MQTT avisa quando a placa cai)."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/58-iot/388_a_primeira_placa.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '388-a-primeira-placa', text: "388 · a primeira placa", level: 2 as const }, { id: 'nao-e-um-duble-da-api', text: "Não é um dublê da API", level: 3 as const }, { id: 'fechar-desliga-as-saidas', text: "`fechar` desliga as saídas", level: 3 as const }, { id: 'para-experimentar', text: "Para experimentar", level: 3 as const }, { id: '389-o-erro-numero-1-do-firmata', text: "389 · o erro numero 1 do Firmata", level: 2 as const }, { id: 'a-amostragem-e-uma-troca', text: "A amostragem é uma troca", level: 3 as const }, { id: 'o-digital-e-por-mudanca', text: "O digital é por mudança", level: 3 as const }, { id: '390-do-numero-cru-ao-valor', text: "390 · do numero cru ao valor", level: 2 as const }, { id: 'escala-limita-por-padrao', text: "`escala` limita por padrão", level: 3 as const }, { id: 'a-tensao-depende-da-placa', text: "A tensão depende da placa", level: 3 as const }, { id: 'a-ponta-da-escala-nao-e-temperatura', text: "A ponta da escala não é temperatura", level: 3 as const }, { id: '391-o-rele-que-nao-bate', text: "391 · o rele que nao bate", level: 2 as const }, { id: 'media-movel-a-resposta-mais-barata', text: "Média móvel: a resposta mais barata", level: 3 as const }, { id: 'histerese-duas-soleiras-nao-uma', text: "Histerese: duas soleiras, não uma", level: 3 as const }, { id: 'invertendo-ela-liga-abaixo', text: "Invertendo, ela liga abaixo", level: 3 as const }, { id: '392-o-meio-termo-que-nao-existe', text: "392 · o meio-termo que nao existe", level: 2 as const }, { id: 'o-modo-e-declarado-nunca-adivinhado', text: "O modo é declarado, nunca adivinhado", level: 3 as const }, { id: 'quem-diz-o-que-o-pino-faz-e-a-placa', text: "Quem diz o que o pino faz é a placa", level: 3 as const }, { id: 'servo-e-posicao', text: "Servo é posição", level: 3 as const }, { id: '393-quem-conhece-a-placa-e-a-placa', text: "393 · quem conhece a placa e a placa", level: 2 as const }, { id: 'tres-numeros-que-mudam-com-a-placa', text: "Três números que mudam com a placa", level: 3 as const }, { id: 'duas-mensagens-diferentes', text: "Duas mensagens diferentes", level: 3 as const }, { id: '394-dois-fios-muitos-sensores', text: "394 · dois fios, muitos sensores", level: 2 as const }, { id: 'o-silencio-e-uma-resposta', text: "O silêncio é uma resposta", level: 3 as const }, { id: 'os-tres-erros-de-ic-em-ordem-de-frequencia', text: "Os três erros de I²C, em ordem de frequência", level: 3 as const }, { id: 'o-endereco-deslocado', text: "O endereço deslocado", level: 3 as const }, { id: '395-o-acento-que-quebra-o-protocolo', text: "395 · o acento que quebra o protocolo", level: 2 as const }, { id: 'por-que-c-e-o-caso', text: "Por que `ç` é o caso", level: 3 as const }, { id: 'sendstring-e-o-println-de-quem-usa-firmata', text: "`sendString` é o `println` de quem usa Firmata", level: 3 as const }, { id: '396-quando-o-programa-precisa-rodar-na-placa', text: "396 · quando o programa precisa rodar NA placa", level: 2 as const }, { id: 'o-arquivo-tem-o-nome-da-pasta', text: "O arquivo tem o nome da pasta", level: 3 as const }, { id: 'uma-opcao-que-nao-existe-e-recusada', text: "Uma opção que não existe é recusada", level: 3 as const }, { id: '57600-e-nao-9600', text: "57600, e não 9600", level: 3 as const }, { id: 'o-que-a-linguagem-nao-faz', text: "O que a linguagem não faz", level: 3 as const }, { id: '397-le-decide-age', text: "397 · le, decide, age", level: 2 as const }, { id: 'as-cinco-decisoes-que-o-programa-carrega', text: "As cinco decisões que o programa carrega", level: 3 as const }, { id: 'o-teto-duro-que-a-histerese-nao-da', text: "O teto duro que a histerese não dá", level: 3 as const }, { id: 'o-que-falta-para-isto-virar-producao', text: "O que falta para isto virar produção", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"58 · IoT e Arduino"}
      description={"10 exercícios: Arduino pelo Firmata: sensores, relé, escala e sketch."}
      href={"/docs/exercicios/58-iot"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
