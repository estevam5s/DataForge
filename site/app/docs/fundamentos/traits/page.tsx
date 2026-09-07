import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Traits",
  description: "Contratos de interface compostos com with.",
};

const blocos: Bloco[] = [
  {"h2": "Declarar"},
  { code: `trait Serializavel:
    action serializar()

trait Comparavel:
    action comparar(outro)` },
  {"p": "Um `trait` lista assinaturas — ações sem corpo. Ele descreve o que um tipo deve saber fazer."},
  {"h2": "Compor"},
  { code: `blueprint Produto(nome, preco) with Serializavel, Comparavel:
    action serializar():
        yield {"nome": self.nome, "preco": self.preco}

    action comparar(outro):
        yield self.preco - outro.preco

a := spawn Produto("Mouse", 80)
b := spawn Produto("Teclado", 200)

out a.serializar()
out a.comparar(b)          # -120` },
  {"p": "Um blueprint pode compor vários traits: `with A, B, C`."},
  {"h2": "Métodos com corpo"},
  {"p": "Um trait pode trazer implementação padrão. Ela só é usada se o blueprint **não** definir a própria:"},
  { code: `trait Descritivel:
    action descrever():
        yield $"<{typeof(self)}>"      # padrão

blueprint Simples with Descritivel:
    # herda descrever()
    action nada():
        yield void

blueprint Detalhado(nome) with Descritivel:
    action descrever():                # sobrescreve
        yield $"Detalhado: {self.nome}"` },
  {"h2": "A limitação atual"},
  {"callout": {"tipo": "atencao", "titulo": "O contrato não é verificado", "texto": "Um blueprint pode declarar `with Serializavel` sem implementar `serializar`, e nada reclama — até alguém chamar. Verificar isso na declaração está no [roadmap](/docs/roadmap)."}},
  {"p": "Enquanto isso, quando a garantia importa, verifique em tempo de execução:"},
  { code: `action processar(item):
    guard has_method(item, "serializar"), $"{typeof(item)} nao implementa Serializavel"
    yield item.serializar()` },
  {"h2": "Trait ou herança?"},
  {"table": {"head": ["Use `trait`", "Use `extends`"], "rows": [["definir uma capacidade", "especializar um tipo"], ["vários tipos não relacionados", "relação \"é um tipo de\""], ["compor várias capacidades", "uma cadeia de especialização"], ["sem estado compartilhado", "reaproveitar campos e lógica"]]}},
  {"p": "Na dúvida: se você diria \"*um Produto **é um** Serializável*\", talvez seja herança. Se diria \"*um Produto **sabe** serializar*\", é trait."},
  {"h2": "Introspecção"},
  { code: `out has_method(a, "serializar")     # yes
out get_methods(a)                  # todos os métodos disponíveis
out get_mro(a)                      # ordem de resolução` },
];

const headings = [{ id: 'declarar', text: "Declarar", level: 2 as const }, { id: 'compor', text: "Compor", level: 2 as const }, { id: 'metodos-com-corpo', text: "Métodos com corpo", level: 2 as const }, { id: 'a-limitacao-atual', text: "A limitação atual", level: 2 as const }, { id: 'trait-ou-heranca', text: "Trait ou herança?", level: 2 as const }, { id: 'introspeccao', text: "Introspecção", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Traits"}
      description={"Contratos de interface compostos com with."}
      href={"/docs/fundamentos/traits"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
