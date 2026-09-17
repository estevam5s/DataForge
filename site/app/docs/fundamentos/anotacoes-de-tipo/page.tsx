import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Anotações de tipo",
  description: "Tipos opcionais em variáveis, parâmetros e retorno — verificados em execução e por análise estática.",
};

const blocos: Bloco[] = [
  {"p": "DataForge é dinâmica: nenhum tipo é obrigatório. Mas todo tipo que você **escreve** é cobrado — nas duas pontas, e é isso que diferencia uma anotação de um comentário."},
  {"table": {"head": ["Quem cobra", "Quando", "O que pega"], "rows": [["`dataforge check`", "antes de executar", "o que ele consegue **provar** olhando o arquivo, e o que atravessa um `adopt`"], ["o interpretador", "na chamada, na atribuição e no `yield`", "o que só se sabe com o valor na mão"]]}},
  {"p": "As duas metades são necessárias. A análise não vê o que vem de um arquivo JSON lido em execução; o interpretador não vê o caminho que aquele `given` nunca tomou nesta rodada."},

  {"h2": "A forma"},
  { code: `idade: Integer := 30                        // variável

action media(nums: Cluster) -> Float:        // parâmetro e retorno
    yield sum(nums) / len(nums)

lambda (n: Integer): n + 1                   // lambda (exige parênteses)

record Usuario:                              // campo de record: obrigatório
    nome: String
    idade: Integer` },
  {"p": "Anotar é **opcional** em variável, parâmetro e retorno; em campo de `record`, não. O código funciona sem, mas quando a anotação existe ela é verificada — pelo interpretador e pelo [`dataforge check`](/docs/cli/check)."},

  {"h2": "O que é verificado"},
  {"list": ["O valor atribuído a uma variável anotada", "Cada argumento passado a um parâmetro anotado, **na fronteira da ação**", "O valor devolvido pelo `yield`, contra o tipo declarado", "Se uma ação com retorno declarado pode terminar **sem** `yield` (aviso)", "O limite de um genérico (`<T extends Number>`), nas duas metades", "Os tipos declarados em **outro arquivo**, atravessando o `adopt`"]},

  {"h2": "Por que na fronteira"},
  {"p": "Compare as duas formas de errar:"},
  { code: `TypeError_: unsupported operand type(s) for *: 'str' and 'int'

parameter 'largura' of action 'area' declared as Number but got String`, lang: 'text' },
  {"p": "A segunda diz **onde** e **o quê**. É por isso que a checagem acontece na entrada da ação, e não lá dentro quando a conta explode — a conta pode estar três chamadas adiante, num arquivo que não é o culpado."},
  { code: `action area(largura: Number, altura: Number) -> Number:
    yield largura * altura

entrada := "3"          // veio de um formulário, de um CSV, de uma query
out area(entrada, 4)` },
  { code: `erro[DF0301]: parameter 'largura' of action 'area' declared as Number but got String
  ┌─ app.df:4:5
  │
4 │ out area(entrada, 4)
  │     ^`, lang: 'text', title: `saída` },

  {"h2": "Os nomes aceitos"},
  {"table": {"head": ["Canônico", "Sinônimos", "Aceita"], "rows": [["`Integer`", "`integer`, `int`", "inteiros"], ["`Float`", "`float`", "decimais **e** inteiros"], ["`Number`", "`number`", "inteiros ou decimais"], ["`String`", "`string`, `str`, `text`", "textos"], ["`Boolean`", "`boolean`, `bool`", "`yes` / `no`"], ["`Cluster`", "`cluster`, `list`, `array`", "listas"], ["`Vault`", "`vault`, `dict`, `map`", "dicionários"], ["`Void`", "`void`, `none`", "apenas `void`"], ["`Action`", "`action`, `function`", "ações e lambdas"], ["`Stream`", "`stream`", "o retorno de um `stream action`"], ["`Any`", "`any`", "tudo — desliga a checagem"]]}},
  {"p": "Qualquer outro nome é procurado entre os seus: record, enum, blueprint ou trait. A checagem percorre a cadeia de herança, então uma filha entra onde se pede a mãe."},

  {"h2": "A regra de alargamento"},
  { code: `media: Float := 8              // ok — todo inteiro é um decimal válido
quantidade: Integer := 3.5     // erro — 3.5 não é inteiro` },
  {"p": "Um `Integer` entra onde se espera `Float`. O contrário perderia informação, e por isso é recusado. Essa é a **única** flexibilização entre tipos embutidos — não há conversão automática de texto para número em lugar nenhum."},
  {"callout": {"tipo": "atencao", "titulo": "`Float` não é decimal exato", "texto": "`19.99` anotado como `Float` é binário, com o arredondamento de sempre. Para dinheiro, use [`Arcane.Decimal`](/docs/tecnicas/decimal) com a forma em aspas — `Dec.de(\"19.99\")` — que não passa por float nenhum."}},

  {"h2": "`Void`: a ação que não devolve"},
  {"p": "`-> Void` documenta que a ação existe pelo efeito, não pelo valor. É o que separa \"esqueci o `yield`\" de \"não há nada para devolver\":"},
  { code: `action registrar(msg: String) -> Void:
    out msg

registrar("gravado")` },
  {"p": "Sem o `-> Void`, uma ação que declara retorno e pode terminar sem `yield` recebe um aviso:"},
  { code: `action rotular(n: Integer) -> String:
    given n bigger 0:
        yield "positivo"
    // e quando n for 0 ou negativo?` },
  { code: `aviso: Action 'rotular' declares '-> String' but can end without a 'yield'
    sugestão: Add a 'yield' at the end, or drop the return type`, lang: 'text', title: `dataforge check` },

  {"h2": "`Any` desliga a conferência, de propósito"},
  { code: `x: Any := 1
x := "agora texto"      // passa: 'Any' aceita tudo` },
  {"p": "`Any` serve para o valor que realmente muda de forma — o que volta de um JSON, o que uma rota recebe no corpo. Usá-lo por comodidade em toda parte dá o mesmo resultado de não anotar nada, com mais ruído."},

  {"h2": "Coleções: o recipiente, e o conteúdo"},
  { code: `notas: Cluster := [7.5, 8.0]      // "é uma lista" — nada diz sobre os itens` },
  {"p": "`Cluster<T>`, `Vault<K, V>` e `Set<T>` declaram também o tipo do que está **dentro**, e aninham: `Vault<String, Cluster<Integer>>`. O conteúdo é conferido em três momentos:"},
  {"list": ["**na fronteira** — declaração, parâmetro, retorno e campo conferem cada item, e o erro diz **qual** (`item 2`, `o valor na chave \"b\"`);", "**na inserção** — a coleção que **nasce** na declaração (literal, compreensão, padrão de campo) recusa `append`, `insert`, `extend`, `xs[i] :=`, `+=`, `v[k] :=`, `set` e `update` fora do tipo;", "**antes de rodar** — o `check` prova o que um literal garante (`tipo-do-conteudo`)."]},
  { code: `notas: Cluster<Float> := [7.5, 8]      // um Integer serve onde se pede Float
notas.append(9.5)

estoque: Vault<String, Integer> := {"caneta": 10}
estoque["lapis"] := 4

monitor:
    notas.append("dez")
handle TypeError as e:
    out e.message      // Cluster<Float> só guarda Float, e append recebeu String.` },
  {"callout": {"tipo": "nota", "titulo": "Por que só a coleção que nasce ali é guardada", "texto": "Uma coleção que já existia é conferida na entrada e **continua sendo o mesmo objeto**. Copiá-la para poder guardar mudaria, em silêncio, toda ação que recebe uma lista para modificar: `acrescentar(xs: Cluster<Integer>, n)` passaria a acrescentar numa cópia que ninguém vê."}},

  {"h2": "Genéricos: `<T>` e `<T extends X>`"},
  {"p": "Um parâmetro de tipo liga a entrada à saída. Sem limite, ele **documenta** a relação e não é cobrado — a linguagem é dinâmica, e `action eco<T>(x: T) -> T` aceita qualquer valor. **Com** limite, ele é cobrado nas duas metades:"},
  { code: `action maior<T extends Number>(a: T, b: T) -> T:
    yield a given a bigger b otherwise b

out maior(3, 7)        // 7
out maior(2.5, 1.5)    // 2.5` },
  { code: `out maior("a", "b")`, title: `o que o check recusa` },
  { code: `erro: Parameter 'a' of 'maior' is a T, and T extends Number — but got String
    sugestão: Passe Number`, lang: 'text' },
  {"p": "Dentro do corpo, um `T extends Number` **é** um `Number` para o analisador — é o que permite escrever `a bigger b` sem alarme. O limite pode ser tipo embutido, blueprint, trait ou record, e atravessa o `adopt`. Mais em [Generics](/docs/fundamentos/generics)."},

  {"h2": "Os seus tipos também são tipos"},
  {"p": "Record, enum, blueprint e trait valem como anotação, e a hierarquia conta. Um `trait` como tipo de parâmetro é o jeito de pedir **capacidade** em vez de linhagem:"},
  { code: `trait Desenhavel:
    action desenhar()

blueprint Forma:
    action area():
        yield 0

blueprint Circulo(raio) extends Forma with Desenhavel:
    action area():
        yield 3.14159 * self.raio ** 2
    action desenhar():
        yield $"círculo de raio {self.raio}"

action mostrar(d: Desenhavel) -> String:    // qualquer um que desenhe
    yield d.desenhar()

action medir(f: Forma) -> Float:            // qualquer forma
    yield f.area()

c := spawn Circulo(2)
out mostrar(c)
out round(medir(c), 2)` },
  { code: `círculo de raio 2
12.57`, lang: 'text', title: `saída` },
  {"p": "O `Circulo` passa nos dois: pela mãe em `medir`, pelo trait em `mostrar`. Nenhum dos dois precisou citar `Circulo`."},

  {"h2": "O tipo atravessa o `adopt`"},
  {"p": "Num sistema de muitos arquivos, a maioria das chamadas cruza módulo — e era exatamente ali que a conferência calava. Hoje o tipo declarado num arquivo é cobrado no outro:"},
  { code: `record Pedido:
    id: Integer
    total: Float

action criar(id: Integer, total: Float) -> Pedido:
    yield Pedido(id, total)

relay Pedido, criar`, title: `dados.df` },
  { code: `adopt ./dados as D

p := D.criar(1, 99.9)
out p.total

out D.criar(1, "muito")`, title: `main.df` },
  { code: `main.df:5:16: erro: O parâmetro 'total' de 'D.criar' espera Float, e recebeu String
    sugestão: declarada em dados.df, linha 5`, lang: 'text', title: `dataforge check` },
  {"p": "O tipo **de retorno** também atravessa: `D.criar(...)` vale como `Pedido`, então `.totall` — o campo errado com o nome quase certo — é acusado do outro lado da fronteira, com sugestão."},

  {"h2": "Quando o analisador cala"},
  {"p": "O que faz o `check` ficar em silêncio é tão importante quanto o que o faz falar: um falso alarme ensina a ignorar mensagens. Ele cala nestes casos, todos de propósito:"},
  {"table": {"head": ["Cala quando", "Porque"], "rows": [["o tipo é um parâmetro genérico **sem** limite", "`T` não é um tipo concreto, e `primeiro([1,2,3]) is 1` é verdadeiro"], ["a ação é **decorada**", "um decorador pode substituir o alvo e mudar o retorno — e um que devolve `void` não substitui nada"], ["o valor veio de um módulo que não compila, ou de um ciclo de import", "a superfície é conservadora: prefere calar a chutar"], ["o outro módulo **não exporta** aquele tipo pelo `relay`", "um módulo que declara o que exporta está dizendo que o resto é interno"], ["o tipo é `Any`", "foi o que você pediu"], ["está dentro de `monitor` ou `expect`", "provocar falha ali é legítimo — vira aviso, não erro"]]}},
  {"p": "E, quando um alarme legítimo atrapalha uma linha específica, ele se silencia **por nome**: `// df: permitir type-mismatch` na linha, ou na de cima."},

  {"h2": "Em execução: perguntar pelo tipo"},
  {"p": "O que a linguagem sabe sobre um valor, com ele na mão:"},
  { code: `record P:
    x: Integer
    y: Integer
    action norma():
        yield self.x + self.y

p := P(1, 2)

out typeof(p), typeof(3), typeof(3.0), typeof("a"), typeof(yes), typeof(void)
out e_um(p, "P")
out has_field(p, "x"), has_method(p, "norma")
out get_fields(p), get_methods(p)` },
  { code: `P Integer Float String Boolean Void
yes
yes yes
[x, y] [norma]`, lang: 'text', title: `saída` },
  {"p": "`typeof` devolve **texto**, então compara com aspas (`typeof(v) is \"Integer\"`). `e_um` percorre a herança e os traits — é a pergunta certa para hierarquia, porque `typeof` de um `Circulo` responde `Circulo`, e não `Forma`."},

  {"h2": "A checagem estática"},
  {"p": "O `dataforge check` encontra os mesmos problemas **antes** de executar, com sugestão de correção:"},
  { code: `app.df:14:1: erro: Declared as String but the value is Integer
    sugestão: Change the annotation to Integer or fix the value
app.df:13:1: erro: Unknown type 'Intger'
    sugestão: Did you mean 'Integer'?`, lang: 'text' },
  {"p": "Detalhes em [Análise estática](/docs/tecnicas/analise-estatica)."},

  {"h2": "Os enganos mais comuns"},
  {"table": {"head": ["O que se escreve", "O que acontece", "A forma certa"], "rows": [["`alias: Cluster<Integer> := outra_lista` e depois `alias.append(\"x\")`", "conferida na entrada, e não guardada: é a mesma lista de antes", "declare a coleção onde ela nasce: `xs: Cluster<Integer> := []`"], ["`n: Integer := \"3\"`", "erro: texto não vira número sozinho", "`n: Integer := int(\"3\")`"], ["`preco: Float := 19.99` para dinheiro", "arredondamento binário, calado", "`Dec.de(\"19.99\")`"], ["`lambda n: Integer: n + 1`", "sem parênteses, o `:` começa o corpo", "`lambda (n: Integer): n + 1`"], ["`-> String` com um `given` sem `otherwise`", "aviso: pode terminar sem `yield`", "feche com um `yield` final, ou `-> Void`"], ["`typeof(v) is Integer`", "compara com um nome, não com texto", "`typeof(v) is \"Integer\"`"]]}},

  {"h2": "Para onde ir agora"},
  {"cards": [{"href": "/docs/fundamentos/generics", "title": "Generics", "desc": "`<T>`, `<T extends X>` e o que é cobrado em cada um."}, {"href": "/docs/fundamentos/records", "title": "Records", "desc": "Campos sempre tipados, imutabilidade e `with`."}, {"href": "/docs/tecnicas/analise-estatica", "title": "Análise estática", "desc": "O que o `check` prova, e por que ele cala quando cala."}, {"href": "/docs/cli/check", "title": "dataforge check", "desc": "O comando, as opções e os códigos de diagnóstico."}]},
];

const headings = [{ id: 'a-forma', text: "A forma", level: 2 as const }, { id: 'o-que-e-verificado', text: "O que é verificado", level: 2 as const }, { id: 'por-que-na-fronteira', text: "Por que na fronteira", level: 2 as const }, { id: 'os-nomes-aceitos', text: "Os nomes aceitos", level: 2 as const }, { id: 'a-regra-de-alargamento', text: "A regra de alargamento", level: 2 as const }, { id: 'void-a-acao-que-nao-devolve', text: "`Void`: a ação que não devolve", level: 2 as const }, { id: 'any-desliga-a-conferencia-de-proposito', text: "`Any` desliga a conferência, de propósito", level: 2 as const }, { id: 'colecoes-o-recipiente-e-o-conteudo', text: "Coleções: o recipiente, e o conteúdo", level: 2 as const }, { id: 'genericos-t-e-t-extends-x', text: "Genéricos: `<T>` e `<T extends X>`", level: 2 as const }, { id: 'os-seus-tipos-tambem-sao-tipos', text: "Os seus tipos também são tipos", level: 2 as const }, { id: 'o-tipo-atravessa-o-adopt', text: "O tipo atravessa o `adopt`", level: 2 as const }, { id: 'quando-o-analisador-cala', text: "Quando o analisador cala", level: 2 as const }, { id: 'em-execucao-perguntar-pelo-tipo', text: "Em execução: perguntar pelo tipo", level: 2 as const }, { id: 'a-checagem-estatica', text: "A checagem estática", level: 2 as const }, { id: 'os-enganos-mais-comuns', text: "Os enganos mais comuns", level: 2 as const }, { id: 'para-onde-ir-agora', text: "Para onde ir agora", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Anotações de tipo"}
      description={"Tipos opcionais em variáveis, parâmetros e retorno — verificados em execução e por análise estática."}
      href={"/docs/fundamentos/anotacoes-de-tipo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
