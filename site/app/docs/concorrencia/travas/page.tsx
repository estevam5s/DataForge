// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Travas",
  description: "Mutex para um de cada vez, semáforo para N de cada vez, e com_trava para não esquecer de soltar.",
};

const blocos: Bloco[] = [
  {"p": "Uma trava transforma um trecho em **seção crítica**: só uma thread por vez passa. É a ferramenta mais direta — e a que mais depende de disciplina: toda escrita no estado protegido precisa estar dentro dela, em todo lugar do programa."},
  { code: `adopt Arcane.Concurrent as P

trava := P.mutex()
total := {"n": 0}

action somar_muito():
    cycle i from 1 to 1000:
        P.com_trava(trava, lambda => incrementar())

action incrementar():
    total["n"] := total["n"] + 1

parallel:
    somar_muito()
    somar_muito()
assert total["n"] is 2000`, lang: 'df' },
  {"table": {"head": ["Trava", "Deixa passar", "Uso"], "rows": [["`P.mutex()`", "uma thread por vez (reentrante)", "proteger um estado compartilhado"], ["`P.semaforo(n)`", "até N ao mesmo tempo", "limitar conexões a um serviço externo"], ["`P.trava_leitura_escrita()`", "muitos leitores, **ou** um escritor", "cache lido o tempo todo e escrito raramente"], ["`P.com_trava(trava, acao)`", "—", "toma, roda, e **solta mesmo com erro**"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Tomar e soltar à mão", "texto": "Funciona até o corpo levantar: a trava fica tomada, e a próxima thread espera para sempre. `com_trava` solta no `finally`. Se você se pegar tomando uma trava à mão, é o momento de usar `com_trava` — ou um [ator](/docs/concorrencia/atores), que não tem trava para esquecer."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Travas"}
      description={"Mutex para um de cada vez, semáforo para N de cada vez, e com_trava para não esquecer de soltar."}
      href={"/docs/concorrencia/travas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
