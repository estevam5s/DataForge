// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Dentro de um contêiner",
  description: "O programa como PID 1, o prazo do docker stop, o host 0.0.0.0 e a sonda de saúde.",
};

const blocos: Bloco[] = [
  {"p": "Dentro de um contêiner, o seu programa costuma ser o **PID 1** — o primeiro processo. Isso muda três coisas que fora dele não importam."},
  {"table": {"head": ["O quê", "Fora", "Dentro do contêiner"], "rows": [["SIGTERM sem tratador", "o processo morre", "o PID 1 **ignora** — e o `docker stop` espera 10 s e mata com SIGKILL"], ["o endereço `127.0.0.1`", "a máquina", "**o próprio contêiner**: nada de fora chega"], ["processos filhos que terminam", "o sistema limpa", "viram zumbis, se o PID 1 não os recolhe"]]}},
  { code: `adopt Arcane.Inicio as Inicio

// o tratador de SIGTERM é o que faz o 'docker stop' levar 50 ms, e não 10 s
Inicio.ao_encerrar(lambda => out "fila devolvida, banco fechado")
out "servindo"`, lang: 'df' },
  {"list": ["**`--host=0.0.0.0` no Kiln e na Vitrine.** Com o padrão `127.0.0.1`, o log diz \"no ar\" e o `curl` de fora não recebe nada — o defeito mais enganoso de um contêiner.", "**`dataforge devops init`** gera o Dockerfile com `USER` sem privilégio, `HEALTHCHECK` e a ordem de camadas que não reinstala tudo a cada commit.", "**A sonda de saúde responde do próprio processo**: uma rota `/saude` que confere o banco. Um contêiner vivo com o banco caído não deveria receber tráfego."]},
  {"p": "O guia completo, com compose, Kubernetes e o que cada artefato carrega: [DevOps](/docs/devops)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Dentro de um contêiner"}
      description={"O programa como PID 1, o prazo do docker stop, o host 0.0.0.0 e a sonda de saúde."}
      href={"/docs/partida/conteineres"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
