import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Propriedades",
  description: "get e set: lido como campo, mas roda código.",
};

const blocos: Bloco[] = [
  { code: `blueprint Retangulo:
    private _largura: Float := 1.0
    private _altura: Float := 1.0

    action setup(largura, altura):
        self.largura := largura
        self.altura := altura

    get largura():
        yield self._largura

    set largura(v):
        given v smaller_eq 0:
            trigger "largura precisa ser positiva"
        self._largura := v

    get altura():
        yield self._altura

    set altura(v):
        given v smaller_eq 0:
            trigger "altura precisa ser positiva"
        self._altura := v

    // so leitura: nao ha 'set area'
    get area():
        yield self._largura * self._altura

    get e_quadrado():
        yield self._largura is self._altura`, lang: 'df' },
  {"h2": "Por que importa"},
  {"p": "Quem usa escreve `r.area` e `r.largura := 4` — não `r.obter_area()`. A diferença aparece depois: você pode **transformar um campo em propriedade** sem quebrar quem já usava."},
  {"p": "E o setter é o lugar da validação. Um campo público aceita qualquer coisa; uma propriedade decide o que é válido no momento da escrita, não depois."},
  {"h2": "Só leitura, só escrita"},
  {"p": "Uma propriedade com `get` e sem `set` recusa a atribuição, dizendo o que falta:"},
  { code: `erro[DF0301]: 'Retangulo.area' is read-only: it has a 'get' but no 'set'.
    Add one:  set area(valor): …`, lang: 'text' },
  {"p": "O contrário também vale: `set` sem `get` é escrita apenas, e ler dá erro."},
  {"h2": "Herança"},
  { code: `blueprint Base:
    action setup():
        self.n := 3
    get dobro():
        yield self.n * 2

blueprint Filho extends Base:
    action setup():
        self.n := 5

out (spawn Filho()).dobro      // 10 — o get do pai lê o campo do filho`, lang: 'df' },
  {"h2": "Armadilhas"},
  {"callout": {"tipo": "atencao", "titulo": "O campo de apoio precisa de outro nome", "texto": "`set largura(v): self.largura := v` chama o próprio setter — recursão infinita. Use `self._largura`."}},
  {"p": "E cuidado com o custo: quem lê `obj.x` espera um custo de leitura. Se a conta é cara — bate no banco, percorre uma lista grande —, um método com nome é mais honesto."},
];

const headings = [{ id: 'por-que-importa', text: "Por que importa", level: 2 as const }, { id: 'so-leitura-so-escrita', text: "Só leitura, só escrita", level: 2 as const }, { id: 'heranca', text: "Herança", level: 2 as const }, { id: 'armadilhas', text: "Armadilhas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Propriedades"}
      description={"get e set: lido como campo, mas roda código."}
      href={"/docs/oop/propriedades"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
