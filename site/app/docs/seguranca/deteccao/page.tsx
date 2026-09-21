// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Detecção e resposta",
  description: "Regras sobre eventos, correlação em janela deslizante, indicadores de comprometimento, alertas e trilha — e por que um SIEM de verdade é infraestrutura.",
};

const blocos: Bloco[] = [
  {"p": "Gravar log é fácil e quase inútil sozinho: ninguém lê dez milhões de linhas. O que transforma log em defesa é a **regra** — a afirmação de que uma sequência de eventos significa alguma coisa — e o **alerta**, que é a regra disparando com o contexto junto."},
  {"h2": "As três perguntas de uma detecção"},
  {"table": {"head": ["Pergunta", "A peça"], "rows": [["o que aconteceu?", "o evento, e a [trilha de auditoria](/docs/seguranca/ferramentas)"], ["isso significa alguma coisa?", "a regra: quantas vezes, em que janela, correlacionado por quê"], ["quem precisa saber?", "o alerta, e o canal — que é de quem chama"]]}},
  { code: `adopt Arcane.Deteccao as D

m := D.motor()
m.regra("forca-bruta", quando := "login.falhou", vezes := 5,
    janela := 60.0, gravidade := "alto", attack := "T1110",
    por := "ip")

cycle i from 1 to 4:
    assert len(m.evento("login.falhou", {"ip": "203.0.113.7"})) is 0

a := m.evento("login.falhou", {"ip": "203.0.113.7"})[0]

// O alerta traz os EVENTOS que o causaram: "forca bruta detectada"
// sem o que aconteceu nao e investigavel.
out $"{a['gravidade']} — {a['regra']} ({a['attack']}), {len(a['eventos'])} eventos"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O alerta errado custa mais que o alerta que falta", "texto": "Cinco falhas de cinco pessoas diferentes **não** são força bruta. Por isso a correlação é por **chave** (`por := \"ip\"`) e não global: sem ela, a regra dispara no primeiro dia movimentado, alguém marca como falso positivo, e na terceira vez ela é desligada — junto com a detecção de verdade."}},
  {"h2": "As armadilhas de contagem"},
  {"table": {"head": ["Armadilha", "O que acontece", "A resposta"], "rows": [["janela **fixa**", "5 falhas às 23h59 e 5 às 00h01 não disparam nada", "janela deslizante"], ["sem supressão", "a mesma regra grita mil vezes por minuto", "`suprimir := 300.0`"], ["janela não zerada", "o sexto evento dispara de novo, e o sétimo também", "a janela é limpa no alerta"], ["regra que levanta", "o motor para de detectar **tudo o resto**", "ela é contada em `erros()`, e as outras seguem"]]}},
  {"h2": "Indicadores de comprometimento"},
  {"p": "Um IOC — hash, IP, domínio, URL — responde *“isto já foi visto num incidente?”*. Ele é **datado e perecível**: um IP malicioso hoje é um IP de nuvem reciclado em três semanas, e um indicador sem prazo vira falso positivo permanente."},
  { code: `adopt Arcane.Deteccao as D

m := D.motor()
ind := m.indicadores()
ind.acrescentar("ip", "198.51.100.66", fonte := "feed-x",
    gravidade := "critico", prazo := 2592000.0)

m.regra("ioc", quando := "indicador.visto", vezes := 1,
    gravidade := "critico")

// 'observar' produz um EVENTO, e nao um veredito: um IOC nao prova
// nada sozinho — um dominio na lista pode ser um colega abrindo um
// artigo sobre o incidente.
m.observar("ip", "198.51.100.66", {"onde": "proxy"})
assert len(m.alertas(gravidade_minima := "critico")) is 1

out "o indicador virou sinal, e o sinal virou alerta"`, lang: 'df' },
  {"h2": "O que não existe, e o que usar"},
  {"table": {"head": ["Não há", "Porque", "O caminho"], "rows": [["**SIEM**", "é infraestrutura — coleta, índice, retenção, busca em escala", "Elastic, Loki, Splunk; este módulo alimenta o alerta"], ["**SOAR**", "orquestração entre dezenas de ferramentas externas", "`ao_alertar` é o gancho para a sua"], ["**YARA**", "`varrer` cobre as *strings* e a condição; não há módulo PE nem *offset*", "o `yara-python`, pela [ponte](/docs/tecnicas/ponte)"], ["**EDR / antivírus**", "exige agente no sistema operacional", "—"], ["leitor de log genérico", "formato de log é o que menos se parece entre sistemas", "`ler_linha` cobre o combinado; o resto é [Arcane.Regex](/docs/biblioteca/regex)"]]}},
  {"callout": {"tipo": "dica", "titulo": "Resposta a incidente começa antes do incidente", "texto": "As três coisas que decidem se uma investigação é possível são gravadas **antes**: a [trilha encadeada](/docs/biblioteca/seguranca) (com o resumo do registro anterior em cada registro), o `motivo` de cada decisão de [autorização](/docs/seguranca/autorizacao), e o `kid` em cada dado cifrado. Nenhuma das três se consegue depois do fato."}},
  {"p": "Referência: [Arcane.Deteccao](/docs/biblioteca/deteccao)."},
];

const headings = [{ id: 'as-tres-perguntas-de-uma-deteccao', text: "As três perguntas de uma detecção", level: 2 as const }, { id: 'as-armadilhas-de-contagem', text: "As armadilhas de contagem", level: 2 as const }, { id: 'indicadores-de-comprometimento', text: "Indicadores de comprometimento", level: 2 as const }, { id: 'o-que-nao-existe-e-o-que-usar', text: "O que não existe, e o que usar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Detecção e resposta"}
      description={"Regras sobre eventos, correlação em janela deslizante, indicadores de comprometimento, alertas e trilha — e por que um SIEM de verdade é infraestrutura."}
      href={"/docs/seguranca/deteccao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
