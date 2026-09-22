// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Resposta a incidentes",
  description: "As fases do NIST, o que preservar antes de consertar, e a comunicação que a LGPD exige.",
};

const blocos: Bloco[] = [
  {"p": "Um incidente é a pior hora para decidir como responder a um incidente. As fases abaixo seguem o guia do NIST (SP 800-61), e a regra que atravessa todas é a mesma: **preserve antes de consertar** — reiniciar a máquina apaga a memória, e reinstalar apaga o disco que provava o que aconteceu."},
  {"table": {"head": ["Fase", "O que se faz", "Com o quê, aqui"], "rows": [["**Preparação**", "quem é chamado, onde está o log, qual é a chave de emergência", "`auditoria` fora da máquina; manifesto assinado de cada deploy"], ["**Detecção e análise**", "o alerta, e a pergunta *“é real?”*", "`Arcane.Deteccao`: o alerta traz os eventos"], ["**Contenção**", "parar o dano sem destruir a evidência", "revogar tokens, girar chaves, tirar do balanceador"], ["**Erradicação**", "tirar o que o atacante deixou", "`conferir_manifesto`: o que foi acrescentado e alterado"], ["**Recuperação**", "voltar a um estado conhecido", "reimplantar do artefato assinado, e não da máquina"], ["**Lições**", "o que teria detectado antes", "uma regra nova no motor de detecção"]]}},
  {"h2": "A primeira hora"},
  { code: `adopt Arcane.Integridade as I
adopt Arcane.IO as IO
adopt Arcane.OS as OS

// 1. Fotografar antes de mexer: o manifesto do estado ATUAL e a evidencia.
servidor := $"{OS.temp_dir()}/df-inc-{randint(100000, 999999)}"
IO.mkdir(servidor)
IO.write($"{servidor}/app.df", "out 1")
IO.write($"{servidor}/.cache-x.df", "adopt Python.os")   // o que alguem deixou

esperado := {"app.df": I.manifesto(servidor)["app.df"]}   // o do deploy
agora := I.manifesto(servidor)
evidencia := to_json(agora)                                // guardado FORA daqui

r := I.conferir_manifesto(servidor, esperado)
out $"acrescentado desde o deploy: {r['acrescentados']}"
assert r["acrescentados"] is [".cache-x.df"]
IO.remove_tree(servidor)`, lang: 'df' },
  {"h2": "Comunicar"},
  {"p": "Um incidente com dado pessoal que possa gerar risco ou dano relevante ao titular precisa ser comunicado à **ANPD** e aos **titulares** (LGPD, art. 48). O regulamento da ANPD sobre comunicação de incidentes fixa o prazo em **três dias úteis** a partir do conhecimento — e pede o que foi afetado, quantos titulares, as medidas tomadas e o contato do encarregado."},
  {"table": {"head": ["A comunicação precisa dizer", "De onde vem"], "rows": [["quais dados, e de quantos titulares", "`Privacidade.titulares()` — onde cada dado mora"], ["quando começou e quando foi percebido", "a trilha de `auditoria`, e o alerta"], ["o que foi feito para conter", "o registro da contenção"], ["o que o titular deve fazer", "trocar a senha, desconfiar de contato"]]}},
  {"callout": {"tipo": "dica", "titulo": "O ensaio", "texto": "Uma resposta que só existe num documento falha no primeiro incidente. Ensaie uma vez por semestre: alguém apaga um arquivo de produção de mentira, e o time precisa descobrir o quê, quando e por quem — só com o que está registrado."}},
  {"p": "Volte ao [mapa de segurança](/docs/seguranca/mapa)."},
];

const headings = [{ id: 'a-primeira-hora', text: "A primeira hora", level: 2 as const }, { id: 'comunicar', text: "Comunicar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Resposta a incidentes"}
      description={"As fases do NIST, o que preservar antes de consertar, e a comunicação que a LGPD exige."}
      href={"/docs/seguranca/incidentes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
