import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Sobrecarga de operadores",
  description: "Fazer +, == e < funcionarem no seu próprio tipo.",
};

const blocos: Bloco[] = [
  { code: `blueprint Vetor:
    x: Float := 0.0
    y: Float := 0.0

    action setup(x, y):
        self.x := x
        self.y := y

    operator + (o):
        yield spawn Vetor(self.x + o.x, self.y + o.y)

    operator - (o):
        yield spawn Vetor(self.x - o.x, self.y - o.y)

    operator * (k):
        yield spawn Vetor(self.x * k, self.y * k)

    operator == (o):
        yield self.x is o.x and self.y is o.y

    get comprimento():
        yield sqrt(self.x ** 2 + self.y ** 2)

    action toString():
        yield $"({self.x}, {self.y})"`, lang: 'df' },
  {"h2": "Quando vale"},
  {"p": "Só quando a operação é **óbvia**: somar dois vetores, comparar dois valores monetários, concatenar duas listas. Se alguém precisa ler a documentação para saber o que `+` faz no seu tipo, um método com nome é melhor."},
  {"h2": "O que dá para sobrecarregar"},
  {"table": {"head": ["Grupo", "Operadores"], "rows": [["Aritméticos", "`+` `-` `*` `/` `%` `**`"], ["Igualdade", "`==` (e `is`)"], ["Ordem", "`<` `>` `<=` `>=` — e os equivalentes `smaller`, `bigger`…"]]}},
  {"p": "Tentar outro símbolo dá erro listando os aceitos:"},
  { code: `erro[DF0103]: '@' cannot be overloaded. You can overload: !=, %, *, **, +, -, /, <, <=, ==, >, >=`, lang: 'text' },
  {"h2": "`isnt` vem de graça"},
  {"p": "Declarar `operator ==` já faz `isnt` funcionar — não é preciso declarar os dois. O mesmo não vale para `<` e `>`: eles são operações diferentes."},
  {"h2": "Regras"},
  {"list": ["`+` deve **devolver um valor novo**, não alterar `self` — `a + b` que muda `a` surpreende quem lê", "Operadores são herdados: um filho ganha os do pai sem redeclarar", "Operador não comutativo (`-`, `/`, `<`) só é tentado no lado esquerdo: `2 * vetor` não funciona se só `Vetor` define `*`"]},
];

const headings = [{ id: 'quando-vale', text: "Quando vale", level: 2 as const }, { id: 'o-que-da-para-sobrecarregar', text: "O que dá para sobrecarregar", level: 2 as const }, { id: 'isnt-vem-de-graca', text: "`isnt` vem de graça", level: 2 as const }, { id: 'regras', text: "Regras", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Sobrecarga de operadores"}
      description={"Fazer +, == e < funcionarem no seu próprio tipo."}
      href={"/docs/oop/operadores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
