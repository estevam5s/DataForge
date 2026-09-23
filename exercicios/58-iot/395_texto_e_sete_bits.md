# 395 — o acento que quebra o protocolo

No Firmata todo byte de dado viaja **partido** em dois de sete bits: o
oitavo é reservado para marcar comando. Ler só o primeiro de cada par
devolve a metade baixa de cada byte.

Em ASCII ninguém nota, porque ali o bit 7 é zero. Num acento, `"olá"`
vira `"olC!"` — e o defeito fica escondido até a primeira mensagem em
português. Foi exatamente assim que ele apareceu neste repositório.

## Por que `ç` é o caso

Em UTF-8, `ç` são **dois** bytes, e cada um deles tem o bit 7 ligado.
No fio do Firmata viram quatro. Partir é obrigatório; esquecer de juntar
de volta é o bug.

## `sendString` é o `println` de quem usa Firmata

Com o Firmata ocupando a porta, um `Serial.println` do sketch estragaria
o protocolo: a mensagem tem de vir **dentro** dele. `placa.textos()`
devolve o que chegou, e `placa.observar` entrega como evento.
