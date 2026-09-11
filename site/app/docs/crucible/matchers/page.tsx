// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/crucible_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Os matchers",
  description: "59 formas de cobrar um valor — e a mensagem que cada uma produz.",
};

const blocos: Bloco[] = [
  {"h2": "Duas formas"},
  {"p": "A curta, para os comuns; a encadeada, para o resto. As duas viram a mesma cobrança:"},
  { code: `crucible "Formas":
    trial "curta":
        expect 2 + 2 is 4

    trial "encadeada":
        expect(2 + 2).to_be(4).to_be_even().to_be_positive()`, lang: 'df' },
  {"p": "A curta existe porque quatro de cada cinco cobranças são igualdade, e `.to_be(...)` em volta delas só acrescenta ruído."},
  {"table": {"head": ["Forma curta", "Equivale a"], "rows": [["`expect x is 4`", "`expect(x).to_be(4)`"], ["`expect x isnt 4`", "`expect(x).nao().to_be(4)`"], ["`expect n bigger 5`", "`expect(n).to_be_greater_than(5)`"], ["`expect n smaller 5`", "`expect(n).to_be_less_than(5)`"], ["`expect s matches \"^a\"`", "`expect(s).to_match(\"^a\")`"], ["`expect xs has 3`", "`expect(xs).to_contain(3)`"], ["`expect x`", "cobra que valha como verdadeiro"]]}},
  {"h2": "Igualdade"},
  { code: `crucible "Igualdade":
    trial "valor":
        expect(4).to_be(4)

    trial "identidade":
        xs := [1, 2]
        expect(xs).to_be_exactly(xs)

    trial "ponto flutuante":
        // 0.1 + 0.2 não dá 0.3 em nenhuma linguagem com IEEE 754
        expect(0.1 + 0.2).to_be_close_to(0.3)

    trial "faixa":
        expect(7).to_be_between(1, 10)`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Nunca `to_be` com float", "texto": "Cobrar igualdade exata de ponto flutuante é escrever um teste que falha por motivo errado. `to_be_close_to` existe para isso."}},
  {"h2": "Verdade e vazio"},
  {"table": {"head": ["Matcher", "Passa quando"], "rows": [["`to_be_true`", "é exatamente `yes`"], ["`to_be_false`", "é exatamente `no`"], ["`to_be_truthy`", "vale como verdadeiro num `given`"], ["`to_be_falsy`", "vale como falso"], ["`to_be_void`", "é `void`"], ["`to_exist`", "não é `void`"], ["`to_be_empty`", "não tem nenhum item"]]}},
  {"h2": "Tipos"},
  { code: `crucible "Tipos":
    trial "pelo nome":
        expect(42).to_be_a("Integer")

    trial "pelos específicos":
        expect(42).to_be_integer().to_be_number()
        expect("a").to_be_text()
        expect([1]).to_be_cluster()
        expect({}).to_be_vault()
        expect(lambda x: x).to_be_action()`, lang: 'df' },
  {"p": "`to_be_instance_of` aceita a linhagem inteira — um herdeiro passa:"},
  { code: `blueprint Animal:
    action f():
        yield 1

blueprint Cachorro extends Animal:
    action g():
        yield 2

crucible "Linhagem":
    trial "o herdeiro é da mãe também":
        expect(spawn Cachorro()).to_be_instance_of("Animal")`, lang: 'df' },
  {"h2": "Números"},
  {"table": {"head": ["Matcher", "", "Matcher", ""], "rows": [["`to_be_greater_than`", "maior", "`to_be_positive`", "> 0"], ["`to_be_less_than`", "menor", "`to_be_negative`", "< 0"], ["`to_be_at_least`", "≥", "`to_be_zero`", "= 0"], ["`to_be_at_most`", "≤", "`to_be_even`", "par"], ["`to_be_divisible_by`", "sem resto", "`to_be_odd`", "ímpar"], ["`to_be_finite`", "nem ∞ nem NaN", "`to_be_nan`", "é NaN"]]}},
  {"h2": "Texto"},
  { code: `crucible "Texto":
    trial "bordas":
        expect("abacate").to_start_with("aba").to_end_with("ate")

    trial "regex":
        expect("ana@x.com").to_match("^[^@]+@[^@]+$")

    trial "conteúdo":
        expect("abacate").to_contain_text("baca")

    trial "forma":
        expect("ABC").to_be_uppercase()
        expect("   ").to_be_blank()`, lang: 'df' },
  {"h2": "Coleções"},
  { code: `crucible "Coleções":
    trial "conteúdo":
        expect([1, 2, 3]).to_contain(2).to_have_length(3)
        expect([1, 2, 3]).to_contain_all([1, 3])
        expect([1, 2, 3]).to_contain_any([9, 2])

    trial "vault":
        expect({"a": 1}).to_have_key("a")
        expect({"a": 1, "b": 2}).to_have_keys(["a", "b"])

    trial "ordem e unicidade":
        expect([1, 2, 3]).to_be_sorted()
        expect([1, 2, 3]).to_be_unique()
        expect([3, 1, 2]).to_have_same_items([1, 2, 3])

    trial "todos e algum":
        expect([2, 4]).to_all_satisfy(lambda n: n % 2 is 0)
        expect([1, 2]).to_any_satisfy(lambda n: n % 2 is 0)`, lang: 'df' },
  {"p": "`to_have_field` serve para vault, record e instância — o teste não deveria precisar saber qual dos três o valor é:"},
  { code: `record Ponto:
    x: Integer
    y: Integer

crucible "Campo":
    trial "vault":
        expect({"nome": "Ana"}).to_have_field("nome", "Ana")

    trial "record":
        expect(Ponto(1, 2)).to_have_field("x", 1)`, lang: 'df' },
  {"h2": "Erros"},
  { code: `action sacar_demais():
    trigger "saldo insuficiente"

crucible "Erros":
    trial "levanta o tipo esperado":
        expect(lambda => 1 / 0).to_raise(DivisionByZeroError)

    trial "a família também serve":
        expect(lambda => 1 / 0).to_raise(RuntimeError)

    trial "e a mensagem":
        // o corpo de um lambda é uma EXPRESSÃO; para uma instrução,
        // declare uma ação
        expect(sacar_demais).to_raise(mensagem := "saldo")

    trial "não levanta nada":
        expect(lambda => 1 + 1).to_not_raise()`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`to_raise` precisa de uma ação", "texto": "`expect(1 / 0)` já estourou antes de chegar ao matcher. É `expect(lambda => 1 / 0)` — sem os parênteses da chamada, senão o erro acontece antes de o Crucible poder observá-lo. O matcher recusa um valor já avaliado, dizendo isso."}},
  {"h2": "Desempenho e saída"},
  { code: `action cumprimentar():
    out "olá"

crucible "Outros":
    trial "prazo":
        expect(lambda => 1 + 1).to_finish_within(100)

    trial "imprime":
        expect(cumprimentar).to_print("olá")`, lang: 'df' },
  {"h2": "Invertendo"},
  {"p": "`nao()` inverte **o próximo** matcher — e só ele, para não deixar um estado invertido pendurado:"},
  { code: `crucible "Negação":
    trial "inverte só o próximo":
        expect([1, 2, 3]).nao().to_contain(9).to_contain(2)`, lang: 'df' },
  {"h2": "Falhando de propósito"},
  { code: `crucible "Manual":
    trial "condição própria":
        Crucible.check(2 + 2 is 4, "a soma quebrou")

    trial "caminho impossível":
        given no:
            Crucible.fail("não deveria chegar aqui")
        expect yes`, lang: 'df' },
  {"p": "A lista completa: `dataforge crucible --matchers`."},
];

const headings = [{ id: 'duas-formas', text: "Duas formas", level: 2 as const }, { id: 'igualdade', text: "Igualdade", level: 2 as const }, { id: 'verdade-e-vazio', text: "Verdade e vazio", level: 2 as const }, { id: 'tipos', text: "Tipos", level: 2 as const }, { id: 'numeros', text: "Números", level: 2 as const }, { id: 'texto', text: "Texto", level: 2 as const }, { id: 'colecoes', text: "Coleções", level: 2 as const }, { id: 'erros', text: "Erros", level: 2 as const }, { id: 'desempenho-e-saida', text: "Desempenho e saída", level: 2 as const }, { id: 'invertendo', text: "Invertendo", level: 2 as const }, { id: 'falhando-de-proposito', text: "Falhando de propósito", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Os matchers"}
      description={"59 formas de cobrar um valor — e a mensagem que cada uma produz."}
      href={"/docs/crucible/matchers"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
