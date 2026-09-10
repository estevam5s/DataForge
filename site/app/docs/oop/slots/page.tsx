import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "slots",
  description: "Restringir os campos de uma instância — e gastar 64% menos memória por objeto.",
};

const blocos: Bloco[] = [
  {"p": "`slots` declara **todos** os campos que uma instância pode ter. Quem tenta criar outro é recusado:"},
  { code: `blueprint Ponto:
    slots x, y

    action setup(x, y):
        self.x := x
        self.y := y

p := spawn Ponto(1, 2)
out p.x                  // imprime 1
p.z := 3                 // erro: 'Ponto' has no field 'z'`, lang: 'df' },
  { code: `erro[DF0402]: 'Ponto' has no field 'z'.
  = nota: it declares slots: x, y
  = dica: slots list every field the object may have; add it there,
          or remove the 'slots' declaration`, lang: 'text', title: `saída` },
  {"h2": "Por que isso economiza memória"},
  {"p": "Sem `slots`, cada instância carrega um **vault** com os seus campos — e um vault guarda as chaves, a tabela de espalhamento e o espaço vago que ela precisa para não colidir. Com `slots`, a linguagem sabe de antemão quais campos existem e em que ordem, e guarda só os **valores**, numa lista."},
  {"p": "São **64% menos memória por objeto**, medido. Num programa com um milhão de instâncias, é a diferença entre caber e não caber."},
  {"callout": {"tipo": "dica", "titulo": "Quando usar", "texto": "Quando existirem **muitos** objetos do mesmo blueprint — pontos, linhas de um arquivo, nós de um grafo. Para um punhado de objetos de configuração, a economia não paga a rigidez."}},
  {"h2": "Herança"},
  {"p": "Herdar de um blueprint com `slots` e acrescentar os próprios é o caso normal: os campos se somam."},
  { code: `blueprint Ponto:
    slots x, y

blueprint Ponto3D extends Ponto:
    slots z
    // a instância aceita x, y e z`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Um ancestral sem slots derruba a restrição", "texto": "Se **qualquer** blueprint da linhagem não declara `slots`, ele aceita campo livre — e a instância precisa de um vault de qualquer jeito. A restrição cai por terra, e a economia junto. Não é um defeito: é a única resposta correta."}},
  {"h2": "`slots` é contextual, não reservada"},
  {"p": "O parser só a reconhece dentro de um blueprint e quando o que vem depois confirma. `slots := 3` em qualquer lugar continua sendo uma variável chamada `slots` — pelo mesmo motivo de `get`, `set`, `final` e as dez palavras do [Kiln](/docs/kiln): são nomes bons demais para tirar de quem escreve."},
];

const headings = [{ id: 'por-que-isso-economiza-memoria', text: "Por que isso economiza memória", level: 2 as const }, { id: 'heranca', text: "Herança", level: 2 as const }, { id: 'slots-e-contextual-nao-reservada', text: "`slots` é contextual, não reservada", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"slots"}
      description={"Restringir os campos de uma instância — e gastar 64% menos memória por objeto."}
      href={"/docs/oop/slots"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
