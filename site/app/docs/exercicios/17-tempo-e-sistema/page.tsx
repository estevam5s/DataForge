// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "17 · Tempo e sistema",
  description: "6 exercícios: datas, durações, ambiente e processos.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 17`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["157", "**Datas e horas**", "crie, formate e compare datas com Arcane.Time."], ["158", "**Aritmetica com datas**", "some e subtraia periodos, e calcule diferencas."], ["159", "**Cronometragem e desempenho**", "meca quanto tempo o codigo leva."], ["160", "**Sistema e ambiente**", "consulte o sistema operacional e as variaveis de ambiente."], ["161", "**Executando processos**", "rode comandos externos e trate a saida."], ["162", "**Registro de eventos**", "registre o que acontece com niveis, campos e destino em arquivo."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/17-tempo-e-sistema/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/17-tempo-e-sistema/157_datas_basico.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"17 · Tempo e sistema"}
      description={"6 exercícios: datas, durações, ambiente e processos."}
      href={"/docs/exercicios/17-tempo-e-sistema"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
