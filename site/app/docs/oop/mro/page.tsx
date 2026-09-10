import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "MRO — ordem de resolução",
  description: "Com herança múltipla, qual método ganha. Linearização C3.",
};

const blocos: Bloco[] = [
  {"p": "Quando um blueprint herda de **um** pai, a busca de método é óbvia: ele, depois o pai, depois o avô. Com herança múltipla não é — e a **MRO** (*method resolution order*) é a lista que responde, calculada por **linearização C3**, a mesma do Python."},
  { code: `blueprint A:
    action quem():
        yield "A"

blueprint B extends A:
    action quem():
        yield "B"

blueprint C extends A:
    action quem():
        yield "C"

blueprint D extends B, C:
    action de_quem_herdo():
        yield "de B e de C"

// D não declara 'quem': a MRO decide qual das duas responde
out (spawn D()).quem()      // "B" — a MRO é D, B, C, A`, lang: 'df' },
  {"h2": "As três garantias do C3"},
  {"list": ["**A classe vem antes das mães.** `D` antes de `B` e `C`.", "**A ordem em que as mães foram escritas é respeitada.** `extends B, C` põe `B` antes de `C`.", "**Uma mãe só aparece depois de todas as filhas dela.** `A` vem por último, mesmo sendo mãe de `B`."]},
  {"p": "Quando não existe ordem que satisfaça as três, a hierarquia é **ambígua** — e aí o C3 recusa, em vez de escolher em silêncio:"},
  { code: `blueprint X extends A, B:
    // se B já herda de A, esta ordem se contradiz

erro: cannot linearize the hierarchy of 'X'`, lang: 'text' },
  {"p": "Recusar é o certo: uma escolha arbitrária aqui vira um bug que só aparece quando alguém acrescenta um método meses depois."},
  {"h2": "`root` segue a MRO"},
  {"p": "`root.metodo()` não vai ao \"primeiro pai\": vai ao **próximo na MRO**, a partir de onde a chamada está. É o que faz uma cadeia de `root` percorrer cada blueprint exatamente uma vez, mesmo em diamante."},
  { code: `blueprint B extends A:
    action quem():
        yield "B->" + root.quem()

assert (spawn B()).quem() is "B->A"`, lang: 'df' },
  {"h2": "Quando ela é calculada"},
  {"p": "Uma vez, na primeira consulta, e guardada. O C3 não é caro, mas a linhagem é percorrida em **toda** busca de método mágico — e aí a conta apareceria."},
];

const headings = [{ id: 'as-tres-garantias-do-c3', text: "As três garantias do C3", level: 2 as const }, { id: 'root-segue-a-mro', text: "`root` segue a MRO", level: 2 as const }, { id: 'quando-ela-e-calculada', text: "Quando ela é calculada", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"MRO — ordem de resolução"}
      description={"Com herança múltipla, qual método ganha. Linearização C3."}
      href={"/docs/oop/mro"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
