import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Blueprints",
  description: "Classes: construtores, herança, traits, polimorfismo, estáticos e sobrecarga de operadores.",
};

const blocos: Bloco[] = [
  {"h2": "Declarar"},
  {"p": "Um `blueprint` é a classe do DataForge. Os parâmetros do cabeçalho viram campos automaticamente:"},
  { code: `blueprint Ponto(x, y):
    action distancia():
        yield sqrt(self.x ** 2 + self.y ** 2)

    action toString():
        yield $"({self.x}, {self.y})"

p := spawn Ponto(3, 4)
out p, p.x, p.distancia()` },
  { code: `(3, 4) 3 5.0`, lang: 'text', title: `saída` },
  {"p": "`spawn` instancia. `forge` é sinônimo, e chamar o blueprint diretamente (`Ponto(3, 4)`) também funciona."},
  {"h3": "Construtor com setup"},
  {"p": "Para inicializar campos derivados, use o método `setup`:"},
  { code: `blueprint Pedido:
    action setup(cliente):
        self.cliente := cliente
        self.itens := []

    action adicionar(item):
        self.itens.append(item)
        yield len(self.itens)

p := spawn Pedido("Ana")
p.adicionar("mouse")` },
  {"p": "As duas formas convivem: se um blueprint tem parâmetros **e** um `setup`, os parâmetros são atribuídos primeiro e depois o `setup` roda."},
  {"h2": "Herança"},
  { code: `blueprint Animal(nome):
    action falar():
        yield "..."
    action apresentar():
        yield $"{self.nome} diz {self.falar()}"

blueprint Cachorro(nome) extends Animal:
    action falar():
        yield "Au au"

blueprint Gato(nome) extends Animal:
    action falar():
        yield "Miau"

cycle bicho in [spawn Cachorro("Rex"), spawn Gato("Mia")]:
    out bicho.apresentar()` },
  { code: `Rex diz Au au
Mia diz Miau`, lang: 'text', title: `saída` },
  {"p": "`apresentar` está definido só no pai, mas chama `self.falar()` — que resolve para a versão do filho. Isso é polimorfismo."},
  {"h3": "root — chamar o pai"},
  { code: `blueprint Base(nome):
    action descrever():
        yield $"Base:{self.nome}"

blueprint Derivada(nome) extends Base:
    action descrever():
        yield $"Derivada[{root.descrever()}]"

out (spawn Derivada("teste")).descrever()` },
  {"h2": "Traits"},
  {"p": "Um `trait` declara um contrato. Um blueprint o compõe com `with`:"},
  { code: `trait Serializavel:
    action serializar()

trait Comparavel:
    action comparar(outro)

blueprint Produto(nome, preco) with Serializavel, Comparavel:
    action serializar():
        yield {"nome": self.nome, "preco": self.preco}

    action comparar(outro):
        yield self.preco - outro.preco` },
  {"callout": {"tipo": "atencao", "texto": "O contrato **ainda não é verificado**: um blueprint pode declarar `with Serializavel` sem implementar `serializar`, e nada reclama até alguém chamar. Use `has_method(x, \"nome\")` quando isso importar. Está no [roadmap](/docs/roadmap)."}},
  {"h2": "Membros estáticos"},
  { code: `blueprint Contador:
    static total := 0

    action inc():
        Contador.total := Contador.total + 1

c := spawn Contador()
c.inc()
out Contador.total     # 1 — compartilhado por todas as instâncias` },
  {"h2": "Sobrecarga de operadores"},
  {"p": "Defina os métodos com estes nomes e os operadores passam a funcionar:"},
  {"table": {"head": ["Método", "Operador"], "rows": [["`add`", "`+`"], ["`sub`", "`-`"], ["`mul`", "`*`"], ["`div`", "`/`"], ["`mod`", "`%`"], ["`pow`", "`**`"], ["`floordiv`", "`~/`"], ["`toString`", "`out` e `str()`"], ["`setup` / `initiate`", "o construtor, chamado por `spawn`"]]}},
  { code: `blueprint Vetor(x, y):
    action add(o):
        yield spawn Vetor(self.x + o.x, self.y + o.y)
    action mul(k):
        yield spawn Vetor(self.x * k, self.y * k)
    action toString():
        yield $"<{self.x}, {self.y}>"

out spawn Vetor(1, 2) + spawn Vetor(3, 4)     # <4, 6>
out spawn Vetor(1, 2) * 3                     # <3, 6>` },
  {"h2": "Introspecção"},
  { code: `p := spawn Ponto(3, 4)

out typeof(p)              # Ponto
out class_name(p)          # Ponto
out get_fields(p)          # os campos da instância
out get_methods(p)         # os métodos disponíveis
out has_method(p, "distancia")
out has_field(p, "x")
out get_mro(p)             # ordem de resolução de métodos` },
  {"h2": "Blueprint ou record?"},
  {"table": {"head": ["Use `record`", "Use `blueprint`"], "rows": [["dados sem comportamento próprio", "objetos com estado que muda"], ["igualdade por valor", "identidade importa"], ["imutável", "precisa mutar campos"], ["sem herança", "herança, traits, polimorfismo"]]}},
  {"p": "Detalhes em [Records](/docs/fundamentos/records)."},
];

const headings = [{ id: 'declarar', text: "Declarar", level: 2 as const }, { id: 'construtor-com-setup', text: "Construtor com setup", level: 3 as const }, { id: 'heranca', text: "Herança", level: 2 as const }, { id: 'root-chamar-o-pai', text: "root — chamar o pai", level: 3 as const }, { id: 'traits', text: "Traits", level: 2 as const }, { id: 'membros-estaticos', text: "Membros estáticos", level: 2 as const }, { id: 'sobrecarga-de-operadores', text: "Sobrecarga de operadores", level: 2 as const }, { id: 'introspeccao', text: "Introspecção", level: 2 as const }, { id: 'blueprint-ou-record', text: "Blueprint ou record?", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Blueprints"}
      description={"Classes: construtores, herança, traits, polimorfismo, estáticos e sobrecarga de operadores."}
      href={"/docs/blueprints"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
