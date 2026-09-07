import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Records",
  description: "Dados imutáveis com igualdade estrutural, valores padrão, métodos e o operador with.",
};

const blocos: Bloco[] = [
  {"h2": "Declarar"},
  { code: `record Usuario:
    nome: String
    idade: Integer
    email: String := "sem@email"` },
  {"p": "Cada campo **exige** um tipo. Um `:=` depois do tipo dá um valor padrão, tornando o campo opcional na construção."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`@dataclass(frozen=True)`"], ["TypeScript", "`interface` / `type`"], ["Java", "`record`"], ["Go", "`struct`"], ["Rust", "`struct`"]]}},
  {"h2": "Construir"},
  { code: `u := Usuario("Ana", 30)                                # posicional
b := Usuario(nome := "Bruno", idade := 25, email := "b@x.com")  # nomeada` },
  {"p": "A forma nomeada é preferível com mais de três campos: `Usuario(\"Ana\", 30, \"a@x.com\", yes, 2)` é ilegível."},
  {"p": "Campo obrigatório ausente ou tipo errado dispara erro na construção — e o `check` acha antes:"},
  { code: `Record 'Usuario' is missing field 'idade'
field 'nome' of record 'Usuario' declared as String but got Integer`, lang: 'text' },
  {"h2": "Igualdade estrutural"},
  {"p": "Esta é a diferença central em relação a um `blueprint`:"},
  { code: `out Usuario("Ana", 30) is Usuario("Ana", 30)     # yes
out Usuario("Ana", 30) is Usuario("Ana", 31)     # no` },
  {"p": "Duas instâncias com os mesmos valores **são iguais**, mesmo sendo objetos distintos. Blueprints comparam por identidade; records, por conteúdo. É isso que torna records úteis como chaves e em comparações de teste."},
  {"h2": "Imutabilidade"},
  { code: `u := Usuario("Ana", 30)
u.idade := 31` },
  { code: `Record 'Usuario' is immutable: cannot assign to 'idade'.
Build a changed copy with "registro with {'idade': valor}".`, lang: 'text' },
  {"p": "Não é uma restrição arbitrária: é o que permite a igualdade estrutural funcionar de forma confiável, e elimina a classe de bugs em que o valor guardado muda debaixo dos seus pés."},
  {"h2": "with — a cópia alterada"},
  { code: `original := Conta("Ana", 1000)
depositado := original with {"saldo": original.saldo + 500}

out original.saldo, depositado.saldo     # 1000 1500` },
  {"p": "Leia como *\"o mesmo que `original`, mas com `saldo` valendo outra coisa\"*."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`dataclasses.replace(obj, saldo=…)`"], ["JavaScript", "`{...obj, saldo: …}`"], ["Rust", "`Conta { saldo: …, ..original }`"], ["Elixir", "`%{original | saldo: …}`"]]}},
  {"p": "O `with` também **valida os nomes**: pedir um campo que não existe é erro. Compare com o spread de JavaScript, onde `{...obj, sldo: 1}` cria alegremente um campo com o nome digitado errado."},
  {"h2": "Transformações encadeadas"},
  { code: `action depositar(conta, valor):
    yield conta with {"saldo": conta.saldo + valor}

action sacar(conta, valor):
    guard valor smaller_eq conta.saldo, "saldo insuficiente"
    yield conta with {"saldo": conta.saldo - valor}

final := sacar(depositar(original, 500), 100)
out original.saldo, final.saldo     # 1000 1400` },
  {"p": "Nenhuma das chamadas tocou em `original`. Se algo der errado no meio, você ainda tem o estado anterior intacto — que é exatamente o que se quer numa transação."},
  {"h2": "Métodos"},
  {"p": "Um record pode ter métodos. A regra não tem exceção: **podem ler `self`, nunca escrever**."},
  { code: `record Retangulo:
    largura: Number
    altura: Number

    action area():
        yield self.largura * self.altura

    action escalar(fator):
        yield Retangulo(self.largura * fator, self.altura * fator)

    action toString():
        yield $"{self.largura}x{self.altura}"

r := Retangulo(3, 4)
out r, r.area(), r.escalar(2)` },
  { code: `3x4 12 6x8`, lang: 'text', title: `saída` },
  {"p": "Quando um método precisaria mudar o estado, ele devolve um record novo — o mesmo padrão de `\"abc\".upper()`."},
  {"h2": "Em pattern matching"},
  {"p": "Records se desmontam em padrões, e é aí que o desenho todo se paga:"},
  { code: `match fig:
    point Retangulo(l, a) when l is a:
        yield "quadrado"
    point Retangulo(largura := 0):
        yield "degenerado"
    point Retangulo:
        yield "retangulo"` },
  {"p": "`point Retangulo(l, a)` faz três coisas de uma vez: verifica o tipo, extrai os campos e liga cada um a um nome. Veja [Pattern matching](/docs/fundamentos/pattern-matching)."},
  {"h2": "Desestruturar"},
  { code: `{nome, idade} := u
out nome, idade` },
];

const headings = [{ id: 'declarar', text: "Declarar", level: 2 as const }, { id: 'construir', text: "Construir", level: 2 as const }, { id: 'igualdade-estrutural', text: "Igualdade estrutural", level: 2 as const }, { id: 'imutabilidade', text: "Imutabilidade", level: 2 as const }, { id: 'with--a-copia-alterada', text: "with — a cópia alterada", level: 2 as const }, { id: 'transformacoes-encadeadas', text: "Transformações encadeadas", level: 2 as const }, { id: 'metodos', text: "Métodos", level: 2 as const }, { id: 'em-pattern-matching', text: "Em pattern matching", level: 2 as const }, { id: 'desestruturar', text: "Desestruturar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Records"}
      description={"Dados imutáveis com igualdade estrutural, valores padrão, métodos e o operador with."}
      href={"/docs/fundamentos/records"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
