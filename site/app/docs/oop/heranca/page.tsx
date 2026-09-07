import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Herança e traits",
  description: "Estender sem reimplementar, e o que final impede.",
};

const blocos: Bloco[] = [
  {"h2": "`root` chama o pai"},
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
  {"p": "É o que distingue **estender** de **reimplementar**: o filho acrescenta, e continua acompanhando as mudanças do pai."},
  {"h2": "Polimorfismo sem marcação"},
  {"p": "Um método herdado que chama `self.x()` resolve para a versão do filho. No exemplo acima, `render` foi herdado sem mudança e usa o `cabecalho` sobrescrito."},
  {"h2": "`final`"},
  { code: `blueprint Base:
    final action identidade():
        yield self._id`, lang: 'df' },
  {"p": "Impede a sobrescrita, e a tentativa falha na declaração do herdeiro:"},
  { code: `erro[DF0301]: 'Filho.identidade' cannot override 'Base.identidade', which is declared final`, lang: 'text' },
  {"p": "Use no que o resto da hierarquia depende para funcionar — um método que outros métodos do pai chamam esperando um comportamento específico."},
  {"h2": "Traits"},
  { code: `trait Serializavel:
    action serializar()              // exigência

    action salvar_em(caminho):       // padrão, herdado
        adopt Arcane.IO as IO
        IO.write(caminho, self.serializar())

blueprint Config with Serializavel:
    action serializar():
        yield "…"`, lang: 'df' },
  {"p": "Trait não guarda estado — por isso `with` aceita vários sem o problema clássico de herança múltipla."},
  {"h2": "Quando não herdar"},
  {"p": "Herança amarra o filho ao pai para sempre. Antes de estender, pergunte se não é composição:"},
  {"list": ["**Herança** quando A *é* um B — um Artigo é um Documento", "**Composição** quando A *tem* um B — um Carro tem um Motor"]},
  {"p": "Uma cadeia com mais de dois ou três níveis costuma ser sinal de que a modelagem foi longe demais. Veja [modelagem](/docs/oop/modelagem)."},
];

const headings = [{ id: 'root-chama-o-pai', text: "`root` chama o pai", level: 2 as const }, { id: 'polimorfismo-sem-marcacao', text: "Polimorfismo sem marcação", level: 2 as const }, { id: 'final', text: "`final`", level: 2 as const }, { id: 'traits', text: "Traits", level: 2 as const }, { id: 'quando-nao-herdar', text: "Quando não herdar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Herança e traits"}
      description={"Estender sem reimplementar, e o que final impede."}
      href={"/docs/oop/heranca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
