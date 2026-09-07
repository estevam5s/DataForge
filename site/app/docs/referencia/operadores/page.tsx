import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Operadores",
  description: "Tabela completa dos operadores da linguagem.",
};

const blocos: Bloco[] = [
  {"h2": "Todos os operadores"},
  {"table": {"head": ["Operador", "Categoria", "Significado"], "rows": [["`:=`", "atribuição", "atribui ou declara"], ["`+=` `-=` `*=` `/=` `%=`", "atribuição", "composta"], ["`+` `-` `*` `/` `%`", "aritmética", "soma, subtração, produto, divisão, resto"], ["`**`", "aritmética", "potência — associa à **direita**"], ["`~/`", "aritmética", "divisão inteira (**preferido**)"], ["`//`", "aritmética", "divisão inteira (ambíguo — ver abaixo)"], ["`is` / `==`", "comparação", "igual"], ["`isnt` / `!=`", "comparação", "diferente"], ["`bigger` / `>`", "comparação", "maior"], ["`smaller` / `<`", "comparação", "menor"], ["`bigger_eq` / `>=`", "comparação", "maior ou igual"], ["`smaller_eq` / `<=`", "comparação", "menor ou igual"], ["`and` `or` `not`", "lógica", "conjunção, disjunção, negação"], ["`??`", "coalescência", "alternativa quando o esquerdo é `void`"], ["`?.`", "acesso seguro", "membro/método, ou `void` se o objeto for `void`"], ["`in` / `not in`", "pertinência", "o elemento está na coleção?"], ["`...`", "spread / rest", "expande ou coleta"], ["`>>`", "pipeline", "encadeia `sift` / `morph` / `distill`"], ["`.`", "acesso", "membro"], ["`[]`", "acesso", "índice ou fatia"], ["`()`", "chamada", "invocação"], ["`->`", "tipo", "tipo de retorno de uma ação"], ["`=>`", "lambda", "corpo de lambda (alternativa a `:`)"], ["`@`", "metadado", "nome do decorador após `mark`"], ["`$\"…\"`", "interpolação", "string com expressões embutidas"]]}},
  {"h2": "A ambiguidade do //"},
  {"p": "`//` abre comentário **e** é divisão inteira. A regra do lexer é conservadora — **`//` é comentário**, salvo quando **todas** estas condições valem:"},
  {"list": ["o token anterior pode terminar uma expressão (valor, `)`, `]`, `}`);", "o que vem depois começa como operando: dígito, `(`, `-` seguido de número, ou identificador;", "esse identificador abre uma chamada, índice ou membro — `len(`, `xs[`, `obj.`."]},
  { code: `x := 7 // 2              # divisão inteira
x := total // len(xs)    # divisão inteira (chamada depois)
x := (a + b) // 2        # divisão inteira
x := 3  // marcar item   # COMENTÁRIO
x := a // b              # COMENTÁRIO (identificador solto)` },
  {"callout": {"tipo": "dica", "texto": "**Use `~/`.** É inequívoco e não depende de heurística. O formatador reimprime a divisão inteira sempre nessa grafia."}},
  {"h2": "Comparações encadeadas"},
  { code: `0 <= nota <= 10        # equivale a (0 <= nota) and (nota <= 10)
1 smaller 5 smaller 10` },
  {"p": "O termo do meio é avaliado uma única vez."},
  {"h2": "Coalescência: só void dispara"},
  { code: `void ?? "padrao"     # "padrao"
no   ?? "padrao"     # no   — falso é um valor
0    ?? 99           # 0    — zero é um valor
""   ?? "vazio"      # ""   — texto vazio é um valor` },
];

const headings = [{ id: 'todos-os-operadores', text: "Todos os operadores", level: 2 as const }, { id: 'a-ambiguidade-do', text: "A ambiguidade do //", level: 2 as const }, { id: 'comparacoes-encadeadas', text: "Comparações encadeadas", level: 2 as const }, { id: 'coalescencia-so-void-dispara', text: "Coalescência: só void dispara", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Operadores"}
      description={"Tabela completa dos operadores da linguagem."}
      href={"/docs/referencia/operadores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
