// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O estado de um módulo",
  description: "Um módulo carrega uma vez, e o que ele guarda é compartilhado por todos que o adotam.",
};

const blocos: Bloco[] = [
  {"p": "Um módulo é executado **uma vez**, no primeiro `adopt`. Os `adopt` seguintes do mesmo arquivo recebem o mesmo objeto — e com ele o mesmo estado. Um contador num módulo é um contador **do programa**, e não de quem o adotou."},
  { code: `// contador.df
//     out "carregando"
//     contagem := {"n": 0}
//     action mais():
//         contagem["n"] += 1
//         yield contagem["n"]
//
// main.df
//     adopt ./contador as A
//     adopt ./contador as B
//     A.mais()
//     out B.mais()          // 2 — e "carregando" saiu UMA vez

out "o modulo carrega uma vez, e o estado e um so"`, lang: 'df' },
  {"table": {"head": ["Isso é bom para", "Isso é perigoso para"], "rows": [["uma conexão aberta uma vez", "um valor que cada teste espera ver zerado"], ["um cache", "duas threads escrevendo no mesmo vault (ver `escrita-concorrente`)"], ["uma configuração lida no começo", "esconder dependência: a ação lê algo que ninguém passou"]]}},
  {"callout": {"tipo": "dica", "titulo": "Prefira passar a guardar", "texto": "Uma ação que recebe o que precisa como argumento se testa sozinha. Uma que lê um vault do módulo depende da ordem em que os testes rodaram — é a origem do teste que passa sozinho e falha na suíte."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"O estado de um módulo"}
      description={"Um módulo carrega uma vez, e o que ele guarda é compartilhado por todos que o adotam."}
      href={"/docs/modulos/estado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
