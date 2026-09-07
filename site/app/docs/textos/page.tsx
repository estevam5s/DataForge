import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Textos",
  description: "Strings, seus métodos, interpolação e formatação.",
};

const blocos: Bloco[] = [
  {"h2": "Criar"},
  { code: `simples := "aspas duplas"
outro := 'aspas simples'
longo := """uma string
que atravessa
varias linhas"""

out simples.length(), longo.lines().length()` },
  {"callout": {"tipo": "atencao", "texto": "Uma string de aspas simples ou duplas **não cruza linhas**. Para SQL ou texto multilinha, use as triplas `\"\"\"…\"\"\"`."}},
  {"h2": "Acessar"},
  { code: `nome := "DataForge"
out nome.length()      # 9
out nome[0]            # D
out nome[-1]           # e
out nome[0:4]          # Data
out nome[::-1]         # egroFataD` },
  {"h2": "Métodos"},
  {"table": {"head": ["Grupo", "Métodos"], "rows": [["caixa", "`upper()` `lower()` `title()` `capitalize()` `swapcase()`"], ["limpeza", "`trim()` `strip()` `lstrip()` `rstrip()`"], ["busca", "`contains(s)` `find(s)` `startswith(s)` `endswith(s)` `count(s)`"], ["troca", "`replace(a, b)` `removeprefix(p)` `removesuffix(s)`"], ["divisão", "`split(sep)` `words()` `lines()` `partition(sep)`"], ["junção", "`join(itens)` `concat(...)` `repeat(n)`"], ["preenchimento", "`pad_start(n, c)` `pad_end(n, c)` `center(n)` `zfill(n)`"], ["teste", "`isalpha()` `isdigit()` `isalnum()` `isspace()` `isupper()`"], ["outros", "`reverse()` `slice(a, b)` `char_at(i)` `index_of(s)`"]]}},
  { code: `frase := "  DataForge e uma linguagem  "

out frase.trim()                        # sem espaços nas pontas
out frase.trim().upper()                # tudo maiúsculo
out frase.contains("linguagem")         # yes
out frase.trim().split(" ").length()    # 5
out "abc".pad_start(6, ".")             # ...abc
out "-".join(["a", "b", "c"])           # a-b-c` },
  {"h2": "Interpolação"},
  {"p": "Uma string prefixada por `$` interpreta `{…}` como expressão:"},
  { code: `nome := "Ana"
idade := 30

out $"Ola {nome}, voce tem {idade} anos"
out $"no ano que vem: {idade + 1}"
out $"{yes} e {void} seguem a grafia da linguagem"
out $"{{chaves literais}} sao dobradas"` },
  {"p": "Compare com a alternativa por concatenação:"},
  { code: `"Ola, " + nome + "! Voce tem " + str(idade) + " anos."
$"Ola, {nome}! Voce tem {idade} anos."` },
  {"p": "A segunda tem menos ruído, menos `+` e nenhum `str()` — a conversão é automática. Detalhes em [Interpolação](/docs/fundamentos/interpolacao)."},
  {"h2": "Concatenação"},
  {"p": "Com `+`. Números viram texto automaticamente quando um dos lados é texto:"},
  { code: `out "total: " + str(42)
out "x" + 1              # "x1" — conversão implícita` },
  {"h2": "Formatar uma tabela"},
  {"p": "`pad_end` alinha texto à esquerda; `pad_start`, números à direita:"},
  { code: `itens := [
    {"nome": "Mouse", "qtd": 15, "preco": 80.0},
    {"nome": "Teclado", "qtd": 3, "preco": 200.0}
]

out $"{"PRODUTO".pad_end(12)}{"QTD".pad_start(5)}{"PRECO".pad_start(10)}"
out "-".repeat(27)
cycle i in itens:
    out $"{i["nome"].pad_end(12)}{str(i["qtd"]).pad_start(5)}{str(i["preco"]).pad_start(10)}"` },
  { code: `PRODUTO       QTD     PRECO
---------------------------
Mouse          15      80.0
Teclado         3     200.0`, lang: 'text', title: `saída` },
  {"h2": "Além do básico"},
  {"p": "Para caixas, tabelas desenhadas, slug, remoção de acentos e distância entre textos, veja [Arcane.Text](/docs/biblioteca/text). Para validação e extração por padrão, [Arcane.Regex](/docs/biblioteca/regex)."},
];

const headings = [{ id: 'criar', text: "Criar", level: 2 as const }, { id: 'acessar', text: "Acessar", level: 2 as const }, { id: 'metodos', text: "Métodos", level: 2 as const }, { id: 'interpolacao', text: "Interpolação", level: 2 as const }, { id: 'concatenacao', text: "Concatenação", level: 2 as const }, { id: 'formatar-uma-tabela', text: "Formatar uma tabela", level: 2 as const }, { id: 'alem-do-basico', text: "Além do básico", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Textos"}
      description={"Strings, seus métodos, interpolação e formatação."}
      href={"/docs/textos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
