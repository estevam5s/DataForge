import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Blueprints",
  description: "A classe do DataForge: setup, métodos, herança e traits.",
};

const blocos: Bloco[] = [
  {"h2": "O básico"},
  { code: `blueprint Pessoa:
    nome: String := ""
    idade: Integer := 0

    action setup(nome, idade):
        self.nome := nome
        self.idade := idade

    action apresentar():
        yield $"{self.nome}, {self.idade} anos"

p := spawn Pessoa("Ana", 30)
out p.apresentar()`, lang: 'df' },
  {"p": "`setup` é o construtor, e roda no `spawn`. `self` é a instância — sempre explícito, como em Python."},
  {"h2": "Parâmetros no cabeçalho"},
  {"p": "A forma curta, quando o construtor só atribui:"},
  { code: `blueprint Ponto(x, y):
    action mover(dx, dy):
        yield spawn Ponto(self.x + dx, self.y + dy)

p := spawn Ponto(1, 2)
out p.x`, lang: 'df' },
  {"callout": {"tipo": "nota", "texto": "Com parâmetros no cabeçalho, o corpo que não for `action` vira corpo do construtor. É prático para blueprints pequenos, mas com muitos campos a forma com `setup` lê melhor."}},
  {"h2": "Herança"},
  { code: `blueprint Documento:
    titulo: String := ""
    action setup(titulo):
        self.titulo := titulo

    action cabecalho():
        yield $"# {self.titulo}"

    action render():
        yield self.cabecalho()

blueprint Artigo extends Documento:
    autor: String := ""

    action setup(titulo, autor):
        self.titulo := titulo
        self.autor := autor

    // acrescenta ao do pai, em vez de refazer
    action cabecalho():
        yield root.cabecalho() + $"\\npor {self.autor}"`, lang: 'df' },
  {"p": "`root` chama a versão do pai. Um método do pai que chama `self.x()` resolve para a sobrescrita do filho — é o polimorfismo funcionando sem nenhuma marcação."},
  {"h2": "Traits"},
  { code: `trait Comparavel:
    action comparar(outro)          // exigência, sem corpo

    action maior_que(outro):        // implementação padrão
        yield self.comparar(outro) bigger 0

blueprint Peso with Comparavel:
    kg: Float := 0.0
    action setup(kg):
        self.kg := kg
    action comparar(o):
        yield self.kg - o.kg`, lang: 'df' },
  {"p": "Método sem corpo é exigência; com corpo, é herdado. O contrato é conferido **na declaração** do blueprint — veja [abstratos](/docs/oop/abstratos)."},
  {"h2": "Múltiplos traits"},
  { code: `blueprint X extends Base with Serializavel, Comparavel:
    …`, lang: 'df' },
  {"p": "`extends` é um só; `with` aceita vários. Trait não guarda estado, então não há o problema de herança múltipla de campos."},
];

const headings = [{ id: 'o-basico', text: "O básico", level: 2 as const }, { id: 'parametros-no-cabecalho', text: "Parâmetros no cabeçalho", level: 2 as const }, { id: 'heranca', text: "Herança", level: 2 as const }, { id: 'traits', text: "Traits", level: 2 as const }, { id: 'multiplos-traits', text: "Múltiplos traits", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Blueprints"}
      description={"A classe do DataForge: setup, métodos, herança e traits."}
      href={"/docs/oop/blueprints"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
