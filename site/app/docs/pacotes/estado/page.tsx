import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "estado",
  description: "Máquina de estados: transições declaradas, guardas e histórico.",
};

const blocos: Bloco[] = [
  { code: `dataforge add estado`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "3 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "A transição só acontece se foi declarada. É isso que distingue uma máquina de estados de um punhado de `given` espalhados: o que não pode acontecer fica impossível, não apenas improvável."},
  {"h2": "Uso"},
  { code: `adopt estado as S

m := S.maquina("rascunho")
m.permitir("rascunho", "publicar", "publicado")
m.permitir("publicado", "arquivar", "arquivado")

out m.pode("publicar")      // yes
m.disparar("publicar")
out m.atual                 // publicado`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 3 símbolos:"},
  { code: `blueprint Maquina
maquina(inicial)
de_tabela(inicial, tabela)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add estado
dataforge add estado@1.0.0
dataforge add estado@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"estado"}
      description={"Máquina de estados: transições declaradas, guardas e histórico."}
      href={"/docs/pacotes/estado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
