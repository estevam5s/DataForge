import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "06 · Blueprints",
  description: "14 exercícios: herança, `root`, traits, polimorfismo e padrões de projeto.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 06`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["063", "**Blueprint com construtor**", "modele um ponto no plano com campos e um metodo."], ["064", "**Construtor com setup**", "use o metodo setup como construtor tradicional."], ["065", "**Estado mutavel**", "uma conta bancaria que muda de saldo."], ["066", "**Heranca com extends**", "especialize um blueprint reutilizando o pai."], ["067", "**root (super)**", "chame a implementacao do pai a partir do filho."], ["068", "**Traits (interfaces)**", "declare um contrato e implemente em dois blueprints."], ["069", "**Polimorfismo**", "calcule a area de formas diferentes pela mesma interface."], ["070", "**Membros estaticos**", "conte quantas instancias foram criadas."], ["071", "**Sobrecarga de operadores**", "some e multiplique vetores com + e *."], ["072", "**Composicao**", "um pedido composto por varios itens."], ["073", "**Cadeia de heranca**", "tres niveis de heranca e resolucao de metodos."], ["074", "**Introspeccao**", "descubra campos, metodos e tipo de uma instancia."], ["075", "**Padrao Singleton**", "garanta uma unica instancia de configuracao usando membro estatico."], ["076", "**Padrao Observador**", "notifique varios assinantes quando o estado mudar."]]}},
  {"h2": "063 · Blueprint com construtor"},
  {"p": "Modele um ponto no plano com campos e um metodo."},
  { code: `// Exercicio 063 — Blueprint com construtor
// Enunciado: modele um ponto no plano com campos e um metodo.

blueprint Ponto(x, y):
    action distancia_origem():
        yield sqrt(self.x ** 2 + self.y ** 2)

    action toString():
        yield "(" + str(self.x) + ", " + str(self.y) + ")"

p := spawn Ponto(3, 4)
out p, p.distancia_origem()

assert p.x is 3, "campo x"
assert p.y is 4, "campo y"
assert p.distancia_origem() is 5.0, "distancia"
assert str(p) is "(3, 4)", "toString"
`, title: `063_blueprint_basico.df` },
  {"h2": "064 · Construtor com setup"},
  {"p": "Use o metodo setup como construtor tradicional."},
  { code: `// Exercicio 064 — Construtor com setup
// Enunciado: use o metodo setup como construtor tradicional.

blueprint Retangulo:
    action setup(largura, altura):
        self.largura := largura
        self.altura := altura

    action area():
        yield self.largura * self.altura

    action perimetro():
        yield 2 * (self.largura + self.altura)

r := spawn Retangulo(4, 6)
out "area:", r.area(), "perimetro:", r.perimetro()

assert r.area() is 24, "area"
assert r.perimetro() is 20, "perimetro"
`, title: `064_setup.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 12 exercícios deste módulo estão em `exercicios/06-blueprints/`. Rode-os com o comando acima."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '063--blueprint-com-construtor', text: "063 · Blueprint com construtor", level: 2 as const }, { id: '064--construtor-com-setup', text: "064 · Construtor com setup", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"06 · Blueprints"}
      description={"14 exercícios: herança, `root`, traits, polimorfismo e padrões de projeto."}
      href={"/docs/exercicios/06-blueprints"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
