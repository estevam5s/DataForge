// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/tipos_genericos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Sistema de traits",
  description: "Traits com implementação padrão, herança entre traits, tipos e constantes associados, interseção, despacho dinâmico e o que a linguagem cobra de quem implementa.",
};

const blocos: Bloco[] = [
  {"p": "Um `trait` descreve **o que um objeto sabe fazer**. Um método sem corpo é exigência; um método com corpo é implementação padrão, que quem adota recebe de graça."},
  { code: `trait Legivel:
    action ler()                       // exigência
    action descrever():                // padrão: vem junto
        yield $"leio: {self.ler()}"

blueprint Documento extends Legivel:
    conteudo := "vazio"
    action ler():
        yield self.conteudo

d := spawn Documento()
assert d.ler() is "vazio"
assert d.descrever() is "leio: vazio" `, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Trait ou contract?", "texto": "`trait` pode trazer implementação; `contract` só declara, confere a aridade de quem implementa e pode estender outros contratos. Quando você quer só a forma, use `contract`; quando quer forma **e** comportamento padrão, use `trait`."}},
  {"h2": "Um trait herda de outro"},
  {"p": "`trait Editavel extends Legivel` soma as exigências e as implementações padrão. A mensagem de quem não implementa aponta **onde a exigência nasceu**, e não quem a repassou — numa cadeia de traits, o nome errado manda procurar no arquivo errado."},
  { code: `trait Legivel:
    action ler()
    action descrever():
        yield $"leio: {self.ler()}"

trait Editavel extends Legivel:
    action escrever(x)

blueprint Nota extends Editavel:
    texto := ""
    action ler():
        yield self.texto
    action escrever(x):
        self.texto := x

n := spawn Nota()
n.escrever("oi")
assert n.ler() is "oi"
assert n.descrever() is "leio: oi" `, lang: 'df' },
  {"p": "Quem implementa só metade é recusado **na declaração**, e a mensagem diz de onde vem a exigência:"},
  { code: `trait Legivel:
    action ler()

trait Editavel extends Legivel:
    action escrever(x)

monitor:
    blueprint Meio extends Editavel:
        action escrever(x):
            yield x
    assert no
handle TraitContractError as e:
    assert "ler" in e.message
    assert "Legivel" in e.message        // quem exigiu, não quem repassou`, lang: 'df' },
  {"h2": "Tipo associado e constante associada"},
  {"p": "Um trait pode declarar um **tipo** que quem implementa preenche, e uma **constante** que todos compartilham. O tipo associado é usado nas anotações dos métodos, e é conferido em execução como qualquer anotação."},
  { code: `trait Coletor:
    type Item := Any                   // tipo associado
    steady LIMITE := 3                 // constante associada
    action pegar() -> Item

blueprint Fila extends Coletor:
    type Item := Integer               // preenchido aqui
    itens := [1, 2]
    action pegar() -> Item:
        yield self.itens[0]

f := spawn Fila()
assert f.pegar() is 1
assert Fila.LIMITE is 3
assert Fila.Item is "Integer" `, lang: 'df' },
  { code: `trait Coletor:
    type Item := Any
    action pegar() -> Item

blueprint Errada extends Coletor:
    type Item := Integer
    action pegar() -> Item:
        yield "nao e numero"

monitor:
    (spawn Errada()).pegar()
    assert no
handle TypeError as e:
    assert "Integer" in e.message and "String" in e.message`, lang: 'df' },
  {"h2": "Trait genérico"},
  { code: `trait Comparavel<T>:
    action comparar(outro: T) -> Integer

blueprint Dinheiro extends Comparavel:
    valor := 0
    action comparar(outro: Dinheiro) -> Integer:
        yield self.valor - outro.valor

a := spawn Dinheiro()
b := spawn Dinheiro()
b.valor := 5
assert a.comparar(b) is -5`, lang: 'df' },
  {"h2": "Exigir dois traits ao mesmo tempo"},
  {"p": "A interseção de tipos (`&`) é o que diz \"precisa saber as duas coisas\" sem inventar um trait novo só para juntá-las. Ver [tipos nomeados](/docs/tipos-nomeados)."},
  { code: `trait Serial:
    action serializar()

trait Ordenavel:
    action comparar(outro)

type Auditavel := Serial & Ordenavel

blueprint Lancamento extends Serial, Ordenavel:
    valor := 7
    action serializar():
        yield $"L{self.valor}"
    action comparar(outro):
        yield self.valor - outro.valor

action registrar(x: Auditavel) -> String:
    yield x.serializar()

assert registrar(spawn Lancamento()) is "L7" `, lang: 'df' },
  {"h2": "Despacho: dinâmico por padrão"},
  {"p": "A chamada de método resolve pelo objeto, em execução, subindo a linhagem (C3, como o `super()` do Python). Não há vtable a declarar nem `virtual` a escrever: **todo** método é despachado assim."},
  {"table": {"head": ["Pergunta", "Resposta no DataForge"], "rows": [["despacho dinâmico", "sim, sempre: o método vem do objeto"], ["despacho estático", "não existe como escolha — o analisador resolve o **nome** antes de rodar, mas a chamada é dinâmica"], ["vtable", "não há tabela declarável: a busca usa a linhagem e um cache de método por blueprint"], ["trait object", "um parâmetro anotado com o trait já é isso: qualquer objeto que o implemente serve"], ["`root`", "chama a implementação de quem **declarou** o método em execução, resolvendo o diamante por C3"]]}},
  { code: `trait Forma:
    action area()

blueprint Quadrado extends Forma:
    lado := 2
    action area():
        yield self.lado ** 2

blueprint Circulo extends Forma:
    raio := 1
    action area():
        yield 3.14 * self.raio ** 2

action somar_areas(formas: Cluster<Forma>) -> Float:
    total := 0.0
    cycle f in formas:
        total += f.area()          // despacho dinâmico
    yield total

assert round(somar_areas([spawn Quadrado(), spawn Circulo()]), 2) is 7.14`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O que o trait NÃO faz", "texto": "Ele não declara campo obrigatório nem construtor. O que ele cobra é método e propriedade — e quem implementa decide como guardar o estado. Um trait que exigisse campo obrigaria um layout, e aí seria herança com outro nome."}},
];

const headings = [{ id: 'um-trait-herda-de-outro', text: "Um trait herda de outro", level: 2 as const }, { id: 'tipo-associado-e-constante-associada', text: "Tipo associado e constante associada", level: 2 as const }, { id: 'trait-generico', text: "Trait genérico", level: 2 as const }, { id: 'exigir-dois-traits-ao-mesmo-tempo', text: "Exigir dois traits ao mesmo tempo", level: 2 as const }, { id: 'despacho-dinamico-por-padrao', text: "Despacho: dinâmico por padrão", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Sistema de traits"}
      description={"Traits com implementação padrão, herança entre traits, tipos e constantes associados, interseção, despacho dinâmico e o que a linguagem cobra de quem implementa."}
      href={"/docs/tipos/traits"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
