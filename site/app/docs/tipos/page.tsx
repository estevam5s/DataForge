import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Tipos",
  description: "Os tipos primitivos, typeof, cast e as anotações opcionais verificadas.",
};

const blocos: Bloco[] = [
  {"h2": "Os tipos primitivos"},
  {"table": {"head": ["Tipo", "Exemplos", "`typeof` devolve"], "rows": [["Inteiro", "`42`, `0xFF`, `0b1010`, `1_000_000`", "`\"Integer\"`"], ["Decimal", "`3.14`, `1.5e3`", "`\"Float\"`"], ["Texto", "`\"a\"`, `'b'`, `\"\"\"várias linhas\"\"\"`", "`\"String\"`"], ["Booleano", "`yes`, `no`", "`\"Boolean\"`"], ["Nulo", "`void`", "`\"Void\"`"], ["Lista", "`[1, 2, 3]`", "`\"Cluster\"`"], ["Dicionário", "`{\"k\": 1}`", "`\"Vault\"`"]]}},
  {"p": "Os nomes **Cluster** e **Vault** valem uma explicação: são lista e dicionário, com nomes que descrevem o uso — um agrupamento de itens e um cofre de pares chave-valor."},
  {"h2": "typeof"},
  {"p": "`typeof x` devolve **o mesmo nome que você usaria numa anotação**. Isso não é detalhe: significa que as duas formas falam a mesma língua."},
  { code: `idade: Integer := 30
out typeof(idade)          # Integer

record Ponto:
    x: Integer
    y: Integer

enum Cor:
    Vermelho

out typeof(42), typeof(3.14), typeof("a"), typeof(yes), typeof(void)
out typeof([1]), typeof({"k": 1})
out typeof(Ponto(1, 2))    # Ponto — o próprio nome do record
out typeof(Cor.Vermelho)   # Cor — o nome do enum` },
  {"h2": "Conversão"},
  {"p": "`cast valor as Tipo` converte explicitamente:"},
  { code: `out cast "42" as Integer      # 42
out cast 3.9 as Integer       # 3   — trunca, não arredonda
out cast 42 as String         # "42"
out cast "3.5" as Float       # 3.5

out str(42), int("7"), float("2.5"), bool(1)` },
  {"callout": {"tipo": "atencao", "texto": "`cast 3.9 as Integer` dá `3`, não `4`. Truncar é a regra; para arredondar use `round(3.9)`."}},
  {"p": "Uma conversão impossível dispara erro em vez de devolver lixo:"},
  { code: `monitor:
    cast "abc" as Integer
handle e:
    out e.message` },
  {"h2": "Anotações de tipo"},
  {"p": "Opcionais, mas **verificadas** — tanto em tempo de execução quanto pelo [analisador estático](/docs/tecnicas/analise-estatica):"},
  { code: `idade: Integer := 30
nome: String := "Ana"
notas: Cluster := [8, 9, 10]
config: Vault := {"tema": "escuro"}

# recusado:
# quantidade: Integer := 3.5` },
  {"p": "Os nomes aceitos, com seus sinônimos:"},
  {"table": {"head": ["Canônico", "Também aceita"], "rows": [["`Integer`", "`integer`, `int`"], ["`Float`", "`float`"], ["`Number`", "`number` — aceita `Integer` **ou** `Float`"], ["`String`", "`string`, `str`, `text`"], ["`Boolean`", "`boolean`, `bool`"], ["`Cluster`", "`cluster`, `list`, `array`"], ["`Vault`", "`vault`, `dict`, `map`"], ["`Void`", "`void`, `none`"], ["`Action`", "`action`, `function`"], ["`Any`", "`any` — desliga a checagem"]]}},
  {"p": "Qualquer outro nome é tratado como nome de record, enum ou blueprint, e a checagem percorre a cadeia de herança."},
  {"h3": "A regra de alargamento"},
  {"p": "Há uma única flexibilização, e ela existe porque é matematicamente segura:"},
  { code: `media: Float := 8          # ok: todo inteiro é um decimal válido
# quantidade: Integer := 3.5   # erro: 3.5 não é inteiro` },
  {"p": "Um `Integer` entra onde se espera `Float`. O contrário perderia informação, e por isso é recusado."},
  {"h2": "Tipagem gradual com Any"},
  {"p": "`Any` diz explicitamente \"qualquer tipo serve\". É diferente de **não anotar**:"},
  {"table": {"head": ["Forma", "Significa"], "rows": [["`action f(x):`", "não pensei sobre o tipo"], ["`action f(x: Any):`", "pensei, e qualquer tipo serve"]]}},
  {"p": "A segunda comunica intenção. Aceitar `Any` não significa tratar tudo igual — o padrão é estreitar logo na entrada com [pattern matching](/docs/fundamentos/pattern-matching):"},
  { code: `action descrever(v: Any) -> String:
    match v:
        point Integer as n:
            yield $"inteiro {n}"
        point String as s:
            yield $"texto de {len(s)} letras"
        point Cluster as c:
            yield $"lista com {len(c)} itens"
        default:
            yield "outro"` },
];

const headings = [{ id: 'os-tipos-primitivos', text: "Os tipos primitivos", level: 2 as const }, { id: 'typeof', text: "typeof", level: 2 as const }, { id: 'conversao', text: "Conversão", level: 2 as const }, { id: 'anotacoes-de-tipo', text: "Anotações de tipo", level: 2 as const }, { id: 'a-regra-de-alargamento', text: "A regra de alargamento", level: 3 as const }, { id: 'tipagem-gradual-com-any', text: "Tipagem gradual com Any", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Tipos"}
      description={"Os tipos primitivos, typeof, cast e as anotações opcionais verificadas."}
      href={"/docs/tipos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
