// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/tipos_genericos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Generics",
  description: "<T> e <T extends X> em ação, blueprint, record, enum e trait: o que o parâmetro documenta, o que o limite cobra, e onde o argumento chega ao conteúdo.",
};

const blocos: Bloco[] = [
  {"p": "Um parâmetro de tipo diz **qual é a relação** entre a entrada e a saída. `action primeiro<T>(xs: Cluster<T>) -> T` promete que o que sai é do mesmo tipo do que estava dentro — e é isso que uma assinatura sem `T` não consegue dizer."},
  {"table": {"head": ["Declaração", "Forma", "O que é cobrado"], "rows": [["ação", "`action eco<T>(x: T) -> T`", "nada: `<T>` documenta"], ["ação com limite", "`action maior<T extends Number>(a: T, b: T)`", "`check` na chamada, e execução no valor"], ["blueprint", "`blueprint Pilha<T>`", "o conteúdo dos campos anotados com `T`"], ["record", "`record Caixa<T>`", "o campo, quando a anotação diz `Caixa<Integer>`"], ["enum", "`enum Talvez<T>`", "documenta a relação do valor que ele carrega"], ["trait", "`trait Comparavel<T>`", "documenta o que quem implementa recebe"], ["alias", "`type Par<T> := Cluster<T>`", "a substituição: `Par<Integer>` é `Cluster<Integer>`"]]}},
  {"h2": "Ação genérica"},
  {"p": "O `<T>` solto **não** é verificado, e isso é de propósito: ele existe para descrever a relação, e a linguagem é de tipagem dinâmica. O `<T extends X>` é verificável, e por isso é verificado nas duas metades — o `check` confere o argumento na chamada, e a execução confere o valor."},
  { code: `action primeiro<T>(xs: Cluster<T>) -> T:
    yield xs[0]

action maior<T extends Number>(a: T, b: T) -> T:
    yield a given a bigger b otherwise b

assert primeiro([1, 2, 3]) is 1
assert primeiro(["a", "b"]) is "a"      // o mesmo T, outro tipo
assert maior(2, 7) is 7
assert maior(1.5, 0.5) is 1.5

monitor:
    maior("dois", "sete")               // String não é Number
    assert no
handle TypeError as e:
    assert "Number" in e.message`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Dentro do corpo, um T com limite É o limite", "texto": "`T extends Number` permite escrever `a bigger b` no corpo sem o analisador reclamar: para ele, ali dentro, `T` é um `Number`. É o que torna o limite útil, e não só decorativo."}},
  {"h2": "Record genérico"},
  {"p": "O parâmetro chega ao **campo**. Sem isso, `Caixa<Integer>` prometeria uma coisa e aceitaria outra — o parâmetro viraria comentário."},
  { code: `record Caixa<T>:
    valor: T

record Par<A, B>:
    esquerda: A
    direita: B

action girar(p: Par<Integer, String>) -> Par<String, Integer>:
    yield Par(p.direita, p.esquerda)

c := Caixa(7)
assert c.valor is 7
assert typeof(c) is "Caixa"

g := girar(Par(1, "um"))
assert g.esquerda is "um" and g.direita is 1

monitor:
    errada: Caixa<Integer> := Caixa("texto")
    assert no
handle TypeError as e:
    assert "Caixa<Integer>" in e.message
    assert "valor" in e.message`, lang: 'df' },
  {"p": "Com limite, o record cobra na construção — e o `check` acusa antes, com o código `generic-bound`:"},
  { code: `record Medida<T extends Number>:
    quanto: T
    action dobro():
        yield self.quanto * 2

assert Medida(2.5).dobro() is 5.0

monitor:
    Medida("dois")
    assert no
handle TypeError as e:
    assert "Number" in e.message`, lang: 'df' },
  {"h2": "Enum genérico"},
  {"p": "Um enum genérico descreve o tipo que os membros carregam. É como se escreve um resultado sem inventar dois records:"},
  { code: `enum Talvez<T>:
    Nada
    Algo

action achar<T>(xs: Cluster<T>, alvo: T) -> Talvez<T>:
    cycle x in xs:
        given x is alvo:
            yield Talvez.Algo
    yield Talvez.Nada

assert achar([1, 2, 3], 2).name is "Algo"
assert achar([1], 9).name is "Nada" `, lang: 'df' },
  {"h2": "Blueprint genérico"},
  { code: `blueprint Pilha<T>:
    itens: Cluster<T> := []

    action por(x):
        self.itens.append(x)
        yield self

    action tirar():
        yield self.itens.pop(len(self.itens) - 1)

p := spawn Pilha()
p.por(1)
p.por(2)
assert p.tirar() is 2
assert len(p.itens) is 1`, lang: 'df' },
  {"h3": "A anotação `Caixa<Integer>`, e o que ela cobra"},
  {"p": "Anotar a variável **vincula** o parâmetro de tipo, e daí em diante a conferência tem contra o que comparar."},
  { code: `blueprint Caixa<T>(valor: T):
    action guardar(v: T):
        self.valor := v
    action ler() -> T:
        yield self.valor

// A anotacao vincula T, e a fronteira confere o conteudo
inteira: Caixa<Integer> := spawn Caixa(7)
assert inteira.ler() is 7

monitor:
    errada: Caixa<Integer> := spawn Caixa("texto")
    assert no
handle TypeError as e:
    assert "field 'valor' of Caixa<Integer>" in e.message
    assert "declared as Integer but got String" in e.message

out "o vinculo e cobrado na fronteira" `, lang: 'df' },
  {"p": "A conferência olha os campos do cabeçalho **e** do corpo, **e os herdados** — um campo que vem da mãe é tão declarado quanto um próprio, e a mãe é quem costuma declarar o genérico."},
  {"table": {"head": ["Onde", "O que é cobrado"], "rows": [["a fronteira (a atribuição anotada)", "todo campo cujo tipo declarado é um parâmetro, inclusive o herdado"], ["o `check`, na chamada de método", "`c.guardar(\"texto\")` com `c: Caixa<Integer>` — acusado **na linha que causa**, com o código `generic-argument`"], ["a execução, com limite", "`<T extends Number>` é cobrado no valor, com ou sem anotação"], ["a aridade dos argumentos", "`Caixa<Integer, String>` num `<T>` é recusado na leitura"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Por que o `check` importa aqui: o erro aparecia no lugar errado", "texto": "Um parâmetro de `T` **sem limite** não é conferido em execução. O campo recebia o texto calado, e a queixa saía na leitura seguinte — *\"a variável 'n' declared as Integer but got String\"*, uma linha depois e sobre **outro nome**. Quem lê a mensagem vai depurar o `n`, que está certo."}},
  {"callout": {"tipo": "perigo", "titulo": "Três defeitos moravam atrás desta anotação", "texto": "Ela era **erro de sintaxe**: `parse_blueprint` lia os parâmetros de tipo e não os registrava — `record`, `enum`, `trait` e `type` registravam, só o blueprint não, e a mensagem sugeria escrever `type Caixa<T> := …`, que é o caminho errado. O ramo de blueprint da conferência era **código morto**, lendo um atributo que nunca existiu. E escrever o argumento de tipo **desligava** a conferência de membro: `p: Par<Integer, String>` e depois `p.naoExiste` passava limpo — escrever **mais** informação de tipo comprava **menos** verificação."}},
  {"h3": "O objeto carrega o vínculo"},
  {"p": "O vínculo não vive só na anotação: ele é **carimbado no objeto** na primeira atribuição anotada. Daí em diante, toda escrita de campo é conferida — e não apenas a fronteira."},
  { code: `blueprint Caixa<T>:
    guardado: T

action de_fora():
    yield "texto"

c: Caixa<Integer> := spawn Caixa()
c.guardado := 7

// A escrita POSTERIOR tambem e conferida, com valor que o
// analisador nao pode ver
monitor:
    c.guardado := de_fora()
    assert no
handle TypeError as e:
    assert "field 'guardado' of Caixa<Integer>" in e.message

out "o vinculo viaja com o objeto" `, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "E ele custa zero para quem não o usa", "texto": "`DFInstance._tipos` nasce em `None`, como os três sentinelas de OOP — e o caminho rápido de escrita de campo tem `_tipos is None` na condição. Um objeto que nunca passou por uma anotação genérica não paga uma única conferência a mais. O slot **nasce** com `None` em vez de ficar ausente porque `getattr` num slot nunca atribuído custa 7× mais: ele levanta e captura um `AttributeError` por dentro."}},
  {"h3": "O primeiro carimbo vence"},
  {"p": "Alargar é legítimo — `Caixa<Integer>` numa anotação `Caixa<Number>` passa. Mas o alargamento **não afrouxa** o objeto:"},
  { code: `blueprint Caixa<T>:
    guardado: T

inteira: Caixa<Integer> := spawn Caixa()
inteira.guardado := 7

larga: Caixa<Number> := inteira        // legitimo: alargar a vista

monitor:
    larga.guardado := 3.5              // ...mas o objeto continua Integer
    assert no
handle TypeError as e:
    assert "declared as Integer" in e.message

out "o primeiro carimbo vence" `, lang: 'df' },
  {"p": "Se o segundo carimbo vencesse, escrever um `Float` por `larga` quebraria a vista `inteira`, que continua apontando para o mesmo objeto. **É a insegurança clássica da covariância com objeto mutável** — e a regra do primeiro carimbo a fecha sem proibir o alargamento."},
  {"h2": "Tipos indexados: quando o parâmetro é um número"},
  {"p": "`Vetor<3>` é um tipo cujo **argumento é um valor**. O parâmetro entra na regra do tipo, e o tamanho passa a fazer parte dele: é a forma prática dos tipos dependentes, e resolve o problema real de \"esta ação só aceita coordenada de duas casas\"."},
  { code: `type Vetor<N> := Cluster<Float> where len(valor) is N

action somar(a: Vetor<2>, b: Vetor<2>) -> Vetor<2>:
    yield [a[0] + b[0], a[1] + b[1]]

assert somar([1.0, 2.0], [3.0, 4.0]) is [4.0, 6.0]

v: Vetor<3> := [1.0, 2.0, 3.0]
assert len(v) is 3

monitor:
    curto: Vetor<3> := [1.0, 2.0]
    assert no
handle TypeError as e:
    assert "len(valor) is N" in e.message`, lang: 'df' },
  {"p": "O `check` prova o tamanho de um **literal** antes de rodar: `v: Vetor<3> := [1.0, 2.0]` é acusado com `tipo-refinado`. O valor que vem de uma chamada não é — e essa é a linha entre verificar e adivinhar."},
  {"h2": "O que não existe"},
  {"table": {"head": ["Não existe", "Por quê"], "rows": [["monomorfização", "não há compilação para código de máquina: o DataForge interpreta a árvore, e o genérico é uma conferência na fronteira"], ["especialização por tipo (`impl<Integer>`)", "exigiria despacho por tipo em tempo de compilação; o caminho aqui é sobrecarga (`overload`), que decide na chamada"], ["variância declarada (`covariant`/`contravariant`)", "**não se aplica** — e isso foi medido. A conferência é estrutural sobre os valores reais em cada fronteira, então ela já dá a resposta certa: `Caixa<Integer>` passa numa anotação `Caixa<Number>` e é recusada numa `Caixa<String>`. Uma palavra de variância não teria o que decidir, e seria a oitava reservada removida por ser cara sem entregar nada"], ["`<T>` cobrado sem limite", "de propósito — o parâmetro solto documenta, e cobrar o que não foi declarado seria inventar uma regra que o código não escreveu"]]}},
];

const headings = [{ id: 'acao-generica', text: "Ação genérica", level: 2 as const }, { id: 'record-generico', text: "Record genérico", level: 2 as const }, { id: 'enum-generico', text: "Enum genérico", level: 2 as const }, { id: 'blueprint-generico', text: "Blueprint genérico", level: 2 as const }, { id: 'a-anotacao-caixainteger-e-o-que-ela-cobra', text: "A anotação `Caixa<Integer>`, e o que ela cobra", level: 3 as const }, { id: 'o-objeto-carrega-o-vinculo', text: "O objeto carrega o vínculo", level: 3 as const }, { id: 'o-primeiro-carimbo-vence', text: "O primeiro carimbo vence", level: 3 as const }, { id: 'tipos-indexados-quando-o-parametro-e-um-numero', text: "Tipos indexados: quando o parâmetro é um número", level: 2 as const }, { id: 'o-que-nao-existe', text: "O que não existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Generics"}
      description={"<T> e <T extends X> em ação, blueprint, record, enum e trait: o que o parâmetro documenta, o que o limite cobra, e onde o argumento chega ao conteúdo."}
      href={"/docs/tipos/genericos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
