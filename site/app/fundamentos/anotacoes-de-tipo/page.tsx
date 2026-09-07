import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Anotações de tipo",
  description: "Tipos opcionais em variáveis, parâmetros e retorno — verificados em execução e por análise estática.",
};

const blocos: Bloco[] = [
  {"h2": "A forma"},
  { code: `idade: Integer := 30                        # variável

action media(nums: Cluster) -> Float:        # parâmetro e retorno
    yield sum(nums) / len(nums)

lambda (n: Integer): n + 1                   # lambda (exige parênteses)` },
  {"p": "Anotar é **opcional**. O código funciona sem, mas quando presente a anotação é verificada — pelo interpretador e pelo [`dataforge check`](/cli/check)."},
  {"h2": "O que é verificado"},
  {"list": ["O valor atribuído a uma variável anotada", "Cada argumento passado a um parâmetro anotado, **na fronteira da ação**", "O valor devolvido pelo `yield`, contra o tipo declarado", "Se uma ação com retorno declarado pode terminar **sem** `yield` (aviso)"]},
  {"h2": "Por que na fronteira"},
  {"p": "Compare as duas formas de errar:"},
  { code: `TypeError_: unsupported operand type(s) for *: 'str' and 'int'

parameter 'largura' of action 'area' declared as Number but got String`, lang: 'text' },
  {"p": "A segunda diz **onde** e **o quê**. É por isso que a checagem acontece na entrada da ação, e não lá dentro quando a conta explode."},
  {"h2": "Os nomes aceitos"},
  {"table": {"head": ["Canônico", "Sinônimos", "Aceita"], "rows": [["`Integer`", "`integer`, `int`", "inteiros"], ["`Float`", "`float`", "decimais **e** inteiros"], ["`Number`", "`number`", "inteiros ou decimais"], ["`String`", "`string`, `str`, `text`", "textos"], ["`Boolean`", "`boolean`, `bool`", "`yes` / `no`"], ["`Cluster`", "`cluster`, `list`, `array`", "listas"], ["`Vault`", "`vault`, `dict`, `map`", "dicionários"], ["`Void`", "`void`, `none`", "apenas `void`"], ["`Action`", "`action`, `function`", "ações e lambdas"], ["`Stream`", "`stream`", "o retorno de um `stream action`"], ["`Any`", "`any`", "tudo — desliga a checagem"]]}},
  {"p": "Qualquer outro nome é tratado como record, enum ou blueprint, e a checagem percorre a cadeia de herança."},
  {"h2": "A regra de alargamento"},
  { code: `media: Float := 8              # ok — todo inteiro é um decimal válido
quantidade: Integer := 3.5     # erro — 3.5 não é inteiro` },
  {"p": "Um `Integer` entra onde se espera `Float`. O contrário perderia informação, e por isso é recusado. Essa é a **única** flexibilização do sistema."},
  {"h2": "Coleções: o recipiente, não o conteúdo"},
  { code: `notas: Cluster := [7.5, 8.0]      # "é uma lista" — nada diz sobre os itens` },
  {"p": "DataForge 4.0 ainda não tem `Cluster<Float>` — [generics](/roadmap) estão no roadmap. Enquanto isso, o conteúdo se valida com código:"},
  { code: `action todos_numeros(valores: Cluster) -> Boolean:
    cycle v in valores:
        given typeof(v) isnt "Integer" and typeof(v) isnt "Float":
            yield no
    yield yes` },
  {"h2": "Records: campos sempre tipados"},
  {"p": "Diferente de variáveis e parâmetros, o tipo de um campo de `record` é **obrigatório**:"},
  { code: `record Usuario:
    nome: String
    idade: Integer
    email: String := "sem@email"    # com valor padrão` },
  {"h2": "A checagem estática"},
  {"p": "O `dataforge check` encontra os mesmos problemas **antes** de executar, com sugestão de correção:"},
  { code: `app.df:14:1: erro: Declared as String but the value is Integer
    sugestão: Change the annotation to Integer or fix the value
app.df:13:1: erro: Unknown type 'Intger'
    sugestão: Did you mean 'Integer'?`, lang: 'text' },
  {"p": "Detalhes em [Análise estática](/tecnicas/analise-estatica)."},
];

const headings = [{ id: 'a-forma', text: "A forma", level: 2 as const }, { id: 'o-que-e-verificado', text: "O que é verificado", level: 2 as const }, { id: 'por-que-na-fronteira', text: "Por que na fronteira", level: 2 as const }, { id: 'os-nomes-aceitos', text: "Os nomes aceitos", level: 2 as const }, { id: 'a-regra-de-alargamento', text: "A regra de alargamento", level: 2 as const }, { id: 'colecoes-o-recipiente-nao-o-conteudo', text: "Coleções: o recipiente, não o conteúdo", level: 2 as const }, { id: 'records-campos-sempre-tipados', text: "Records: campos sempre tipados", level: 2 as const }, { id: 'a-checagem-estatica', text: "A checagem estática", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Anotações de tipo"}
      description={"Tipos opcionais em variáveis, parâmetros e retorno — verificados em execução e por análise estática."}
      href={"/fundamentos/anotacoes-de-tipo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
