import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Métodos mágicos",
  description: "Os 95 ganchos que a linguagem procura no seu blueprint.",
};

const blocos: Bloco[] = [
  {"p": "Um **método mágico** é um gancho: a linguagem o procura no blueprint quando uma operação acontece sobre uma instância. Declarar `__add__` faz o `+` funcionar; declarar `__getitem__` faz o `[]` funcionar. São **95**, em 16 grupos."},
  { code: `blueprint Vetor:
    action setup(x, y):
        self.x := x
        self.y := y

    action __add__(outro):
        yield spawn Vetor(self.x + outro.x, self.y + outro.y)

    action __str__():
        yield $"({self.x}, {self.y})"

    action __eq__(outro):
        yield self.x is outro.x and self.y is outro.y

    action __len__():
        yield 2

out spawn Vetor(1, 2) + spawn Vetor(3, 4)      // imprime (4, 6)
assert len(spawn Vetor(1, 2)) is 2`, lang: 'df' },
  {"h2": "Por que o nome com dois sublinhados"},
  {"p": "Porque é o que quem chega do Python já conhece, e porque o sublinhado duplo sinaliza *isto não é para você chamar*: ele é chamado **pela linguagem**, no momento da operação. `v.__add__(outro)` funciona, mas escrever isso é o mesmo que escrever `v + outro` de um jeito pior."},
  {"callout": {"tipo": "nota", "titulo": "`operator +` continua valendo — e vence", "texto": "DataForge já tinha [`operator`](/docs/oop/operadores), que é mais direto de ler para quem nunca viu Python. Quando o blueprint declara os dois para a mesma operação, o `operator` tem prioridade. Eles convivem porque cobrem públicos diferentes."}},
  {"h2": "Um decorador que devolve void não substitui o alvo"},
  {"p": "Vale lembrar aqui porque é a regra que permite `@Rota(\"/x\")` apenas anotar: se um decorador devolvesse `void` e isso virasse o novo valor, a ação decorada sumiria."},
  {"h2": "Construção (6)"},
  {"p": "Nascer, morrer e copiar."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__init__`", "0", "roda no spawn; sinonimo de 'setup'"], ["`__new__`", "0", "cria a instancia antes de '__init__'"], ["`__del__`", "0", "roda quando o objeto e descartado"], ["`__copy__`", "0", "copia rasa"], ["`__deepcopy__`", "0", "copia profunda"], ["`__clone__`", "0", "copia, no vocabulario do DataForge"]]}},
  {"h2": "Texto (5)"},
  {"p": "O que `out`, `str()` e a interpolação chamam."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__str__`", "0", "o texto que 'out' imprime"], ["`__repr__`", "0", "o texto para quem depura"], ["`__format__`", "1", "formatacao com especificador"], ["`__bytes__`", "0", "a representacao em bytes"], ["`__doc__`", "0", "a documentacao do objeto"]]}},
  {"h2": "Comparação (7)"},
  {"p": "`is`, `isnt`, `<`, `<=`, `>`, `>=` e a ordenação."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__eq__`", "1", "a == b  (e 'a is b')"], ["`__ne__`", "1", "a != b  (e 'a isnt b')"], ["`__lt__`", "1", "a < b   (e 'a smaller b')"], ["`__le__`", "1", "a <= b"], ["`__gt__`", "1", "a > b   (e 'a bigger b')"], ["`__ge__`", "1", "a >= b"], ["`__cmp__`", "1", "-1, 0 ou 1; cobre os seis de uma vez"]]}},
  {"h2": "Aritmética (9)"},
  {"p": "`+` `-` `*` `/` `~/` `%` `**`."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__add__`", "1", "a + b"], ["`__sub__`", "1", "a - b"], ["`__mul__`", "1", "a * b"], ["`__truediv__`", "1", "a / b"], ["`__floordiv__`", "1", "a ~/ b"], ["`__mod__`", "1", "a % b"], ["`__pow__`", "1", "a ** b"], ["`__divmod__`", "1", "quociente e resto de uma vez"], ["`__matmul__`", "1", "a @ b — multiplicacao de matriz"]]}},
  {"h2": "Aritmética refletida (8)"},
  {"p": "Quando o objeto está à **direita** do operador."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__radd__`", "1", "b + a, quando 'b' nao sabe somar"], ["`__rsub__`", "1", "b - a"], ["`__rmul__`", "1", "b * a"], ["`__rtruediv__`", "1", "b / a"], ["`__rfloordiv__`", "1", "b ~/ a"], ["`__rmod__`", "1", "b % a"], ["`__rpow__`", "1", "b ** a"], ["`__rmatmul__`", "1", "b @ a"]]}},
  {"h2": "Aritmética no lugar (7)"},
  {"p": "`+=`, `-=` e as outras compostas."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__iadd__`", "1", "a += b, alterando 'a'"], ["`__isub__`", "1", "a -= b"], ["`__imul__`", "1", "a *= b"], ["`__itruediv__`", "1", "a /= b"], ["`__ifloordiv__`", "1", "a ~/= b"], ["`__imod__`", "1", "a %= b"], ["`__ipow__`", "1", "a **= b"]]}},
  {"h2": "Unários (8)"},
  {"p": "`-x`, `+x`, `abs(x)`, `round(x)`."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__neg__`", "0", "-a"], ["`__pos__`", "0", "+a"], ["`__abs__`", "0", "abs(a)"], ["`__invert__`", "0", "~a"], ["`__round__`", "1", "round(a, casas)"], ["`__floor__`", "0", "floor(a)"], ["`__ceil__`", "0", "ceil(a)"], ["`__trunc__`", "0", "trunc(a)"]]}},
  {"h2": "Bits (8)"},
  {"p": "`&` `|` `^` `~` `<<` `>>`."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__and__`", "1", "a & b"], ["`__or__`", "1", "a | b"], ["`__xor__`", "1", "a ^ b"], ["`__lshift__`", "1", "a << b"], ["`__rshift__`", "1", "a >> b"], ["`__rand__`", "1", "b & a"], ["`__ror__`", "1", "b | a"], ["`__rxor__`", "1", "b ^ a"]]}},
  {"h2": "Conversão (6)"},
  {"p": "`int()`, `float()`, `bool()`, `len()`, `hash()`."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__bool__`", "0", "o que 'given obj:' decide"], ["`__int__`", "0", "int(obj)"], ["`__float__`", "0", "float(obj)"], ["`__complex__`", "0", "complex(obj)"], ["`__index__`", "0", "o objeto como indice de colecao"], ["`__hash__`", "0", "a chave de vault que este objeto vira"]]}},
  {"h2": "Coleção (10)"},
  {"p": "`[]`, `in`, percurso e tamanho."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__len__`", "0", "len(obj)"], ["`__getitem__`", "1", "obj[chave]"], ["`__setitem__`", "2", "obj[chave] := valor"], ["`__delitem__`", "1", "delete obj[chave]"], ["`__contains__`", "1", "item in obj"], ["`__iter__`", "0", "'cycle x in obj'"], ["`__next__`", "0", "o proximo item do percurso"], ["`__reversed__`", "0", "percurso de tras para frente"], ["`__missing__`", "1", "chave ausente, antes de dar erro"], ["`__length_hint__`", "0", "tamanho aproximado, para alocar antes"]]}},
  {"h2": "Chamada (1)"},
  {"p": "Fazer a instância ser chamável."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__call__`", "-1", "obj(argumentos)"]]}},
  {"h2": "Atributo (5)"},
  {"p": "Ler, escrever e remover campo."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__getattr__`", "1", "obj.campo, quando o campo nao existe"], ["`__getattribute__`", "1", "obj.campo, SEMPRE"], ["`__setattr__`", "2", "obj.campo := valor"], ["`__delattr__`", "1", "delete obj.campo"], ["`__dir__`", "0", "a lista de nomes do objeto"]]}},
  {"h2": "Descritor (4)"},
  {"p": "Um campo cujo acesso é controlado por outro objeto."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__get__`", "2", "leitura do campo que este objeto guarda"], ["`__set__`", "2", "escrita nele"], ["`__delete__`", "1", "remocao"], ["`__set_name__`", "2", "o nome que ele recebeu na classe"]]}},
  {"h2": "Contexto (2)"},
  {"p": "Entrar e sair de um bloco com limpeza garantida."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__enter__`", "0", "'with obj as x:' — o que 'x' recebe"], ["`__exit__`", "0", "o fim do bloco, mesmo com erro"]]}},
  {"h2": "Assíncrono (5)"},
  {"p": "`await` e percurso assíncrono."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__await__`", "0", "'await obj'"], ["`__aiter__`", "0", "percurso assincrono"], ["`__anext__`", "0", "o proximo item dele"], ["`__aenter__`", "0", "'with' assincrono"], ["`__aexit__`", "0", "o fim dele"]]}},
  {"h2": "Tipo (4)"},
  {"p": "Como o objeto responde a perguntas sobre si mesmo."},
  {"table": {"head": ["Método", "Parâmetros", "Chamado por"], "rows": [["`__instancecheck__`", "1", "'e_um(x, Isto)'"], ["`__subclasscheck__`", "1", "se um blueprint descende deste"], ["`__class_getitem__`", "1", "Blueprint[Tipo] — generics"], ["`__init_subclass__`", "1", "roda quando alguem herda deste"]]}},
  {"h2": "O que não existe"},
  {"list": ["**Não há verificação de contrato.** Declarar `__iter__` sem `__next__` só falha quando alguém tenta percorrer o objeto.", "**`__slots__` não é um método mágico** — é uma declaração; veja [slots](/docs/oop/slots).", "**Um mágico que devolve o tipo errado não é corrigido.** `__len__` devolvendo texto quebra no `len()`, não na declaração."]},
];

const headings = [{ id: 'por-que-o-nome-com-dois-sublinhados', text: "Por que o nome com dois sublinhados", level: 2 as const }, { id: 'um-decorador-que-devolve-void-nao-substitui-o-alvo', text: "Um decorador que devolve void não substitui o alvo", level: 2 as const }, { id: 'construcao-6', text: "Construção (6)", level: 2 as const }, { id: 'texto-5', text: "Texto (5)", level: 2 as const }, { id: 'comparacao-7', text: "Comparação (7)", level: 2 as const }, { id: 'aritmetica-9', text: "Aritmética (9)", level: 2 as const }, { id: 'aritmetica-refletida-8', text: "Aritmética refletida (8)", level: 2 as const }, { id: 'aritmetica-no-lugar-7', text: "Aritmética no lugar (7)", level: 2 as const }, { id: 'unarios-8', text: "Unários (8)", level: 2 as const }, { id: 'bits-8', text: "Bits (8)", level: 2 as const }, { id: 'conversao-6', text: "Conversão (6)", level: 2 as const }, { id: 'colecao-10', text: "Coleção (10)", level: 2 as const }, { id: 'chamada-1', text: "Chamada (1)", level: 2 as const }, { id: 'atributo-5', text: "Atributo (5)", level: 2 as const }, { id: 'descritor-4', text: "Descritor (4)", level: 2 as const }, { id: 'contexto-2', text: "Contexto (2)", level: 2 as const }, { id: 'assincrono-5', text: "Assíncrono (5)", level: 2 as const }, { id: 'tipo-4', text: "Tipo (4)", level: 2 as const }, { id: 'o-que-nao-existe', text: "O que não existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Métodos mágicos"}
      description={"Os 95 ganchos que a linguagem procura no seu blueprint."}
      href={"/docs/oop/magicos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
