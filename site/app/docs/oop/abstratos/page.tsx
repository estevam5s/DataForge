import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Abstratos e contratos",
  description: "Declarar exigências, e a linguagem cobrar na declaração.",
};

const blocos: Bloco[] = [
  { code: `abstract blueprint Forma:
    abstract action area()

    // metodo concreto: os herdeiros ganham de graca
    action descrever():
        yield $"{self.nome()} com area {round(self.area(), 2)}"

    abstract action nome()

blueprint Quadrado extends Forma:
    lado: Float := 0.0

    action setup(lado):
        self.lado := lado

    action area():
        yield self.lado ** 2

    action nome():
        yield "quadrado"

blueprint Circulo extends Forma:
    raio: Float := 0.0

    action setup(raio):
        self.raio := raio

    action area():
        yield PI * self.raio ** 2

    action nome():
        yield "circulo"`, lang: 'df' },
  {"h2": "O erro sai cedo"},
  {"p": "Um blueprint concreto que não implementa tudo o que prometeu falha **ao ser declarado**:"},
  { code: `erro[DF0301]: Blueprint 'Ruim' does not implement 1 abstract method:
    comparar()  — declarado em 'Comparavel'
    Implement it, or mark 'Ruim' as 'abstract blueprint' if it is not meant
    to be spawned directly.`, lang: 'text' },
  {"p": "Isso é diferente de descobrir o problema quando alguém chama o método ausente, em produção. Foi a mudança mais valiosa do 4.1 para quem monta hierarquias."},
  {"h2": "Abstrato não se instancia"},
  { code: `erro[DF0301]: 'Forma' is an abstract blueprint and cannot be spawned directly.
    It still misses: area()
    Spawn a blueprint that extends it instead.`, lang: 'text' },
  {"h2": "Método molde"},
  {"p": "Um abstrato pode ter métodos concretos que chamam os abstratos — o pai define o roteiro, o filho preenche os passos:"},
  { code: `abstract blueprint Relatorio:
    abstract action cabecalho()
    abstract action linhas()

    action gerar():                 // o roteiro, uma vez só
        partes := [self.cabecalho()]
        cycle l in self.linhas():
            partes.append(l)
        yield partes.join("\\n")`, lang: 'df' },
  {"h2": "Regras"},
  {"list": ["Um herdeiro que não implementa tudo também precisa ser `abstract`", "Trait com método sem corpo é exigência; com corpo, é implementação padrão", "Trait não guarda estado — para compartilhar campos, use herança ou composição"]},
];

const headings = [{ id: 'o-erro-sai-cedo', text: "O erro sai cedo", level: 2 as const }, { id: 'abstrato-nao-se-instancia', text: "Abstrato não se instancia", level: 2 as const }, { id: 'metodo-molde', text: "Método molde", level: 2 as const }, { id: 'regras', text: "Regras", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Abstratos e contratos"}
      description={"Declarar exigências, e a linguagem cobrar na declaração."}
      href={"/docs/oop/abstratos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
