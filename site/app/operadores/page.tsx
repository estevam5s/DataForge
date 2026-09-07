import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Operadores",
  description: "Aritméticos, comparação, lógicos, coalescência, pertinência e a precedência completa.",
};

const blocos: Bloco[] = [
  {"h2": "Aritméticos"},
  { code: `out 7 + 2      # 9
out 7 - 2      # 5
out 7 * 2      # 14
out 7 / 2      # 3.5    — sempre Float
out 7 % 2      # 1
out 7 ** 2     # 49
out 7 ~/ 2     # 3      — divisão inteira` },
  {"callout": {"tipo": "atencao", "titulo": "Divisão inteira: use ~/", "texto": "`//` também funciona, mas é ambíguo: ele abre comentários. A regra é conservadora — **`//` é comentário**, salvo quando seguido de dígito, `(`, ou identificador que abre chamada, índice ou membro. Com `~/` você nunca precisa pensar nisso."}},
  { code: `x := 7 // 2              # divisão inteira (dígito depois)
y := total // len(xs)    # divisão inteira (chamada depois)
z := 3  // marcar item   # COMENTÁRIO
w := a // b              # COMENTÁRIO` },
  {"h2": "Comparação"},
  {"p": "Cada operador tem duas grafias, equivalentes. A forma por palavra lê melhor em condições longas; a simbólica é mais compacta."},
  {"table": {"head": ["Palavra", "Símbolo", "Significado"], "rows": [["`is`", "`==`", "igual"], ["`isnt`", "`!=`", "diferente"], ["`bigger`", "`>`", "maior"], ["`smaller`", "`<`", "menor"], ["`bigger_eq`", "`>=`", "maior ou igual"], ["`smaller_eq`", "`<=`", "menor ou igual"]]}},
  {"h3": "Comparações encadeadas"},
  {"p": "Funcionam como em matemática — e o termo do meio é avaliado **uma única vez**:"},
  { code: `nota := 7.5
out 0 <= nota <= 10           # yes
out 1 smaller 5 smaller 10    # yes
out 10 < 5 < 20               # no` },
  {"h2": "Lógicos"},
  { code: `out yes and no      # no
out yes or no       # yes
out not yes         # no` },
  {"p": "`and` e `or` têm avaliação curta-circuito: o lado direito só é avaliado se necessário."},
  {"h2": "Coalescência e acesso seguro"},
  { code: `config := void
out config ?? "padrao"          # "padrao"
out config?.porta ?? 8080       # 8080, sem estourar` },
  {"p": "`??` só entra em ação quando o valor é **`void`**. `no`, `0` e `\"\"` são valores legítimos, e passam direto:"},
  { code: `out no ?? "padrao"     # no  — falso é um valor
out 0 ?? 99            # 0   — zero é um valor
out "" ?? "vazio"      # ""  — texto vazio é um valor` },
  {"p": "Essa distinção é o que separa `??` de um `or`: com `or`, todos os três cairiam no padrão."},
  {"h2": "Pertinência"},
  { code: `out 2 in [1, 2, 3]              # yes  — elemento na lista
out "a" in "casa"               # yes  — subtexto
out "chave" in {"chave": 1}     # yes  — chave do vault
out 9 not in [1, 2, 3]          # yes` },
  {"p": "Em um `Vault`, `in` testa **chaves**, não valores — a mesma convenção de `cycle k in vault`."},
  {"h2": "Atribuição composta"},
  { code: `x := 10
x += 5      # 15
x -= 3      # 12
x *= 2      # 24
x /= 4      # 6.0
x %= 4      # 2.0` },
  {"h2": "Precedência"},
  {"p": "Da mais alta para a mais baixa:"},
  {"table": {"head": ["Nível", "Operadores", "Associatividade"], "rows": [["1", "`()` `[]` `.` `?.`", "esquerda"], ["2", "`**`", "**direita**"], ["3", "`-` `+` `not` (unários)", "direita"], ["4", "`*` `/` `%` `~/`", "esquerda"], ["5", "`+` `-`", "esquerda"], ["6", "comparações", "encadeável"], ["7", "`not`", "direita"], ["8", "`and`", "esquerda"], ["9", "`or`", "esquerda"], ["10", "`??`", "esquerda"], ["11", "`given … otherwise` (ternário)", "direita"], ["12", "`>>`", "esquerda"]]}},
  {"p": "As consequências que mais surpreendem:"},
  { code: `out 2 ** 3 ** 2    # 512, e não 64 — potência associa à direita
out -2 ** 2        # -4, e não 4 — o sinal aplica depois
out 2 + 3 * 4      # 14` },
  {"p": "A tabela completa está na [Referência de precedência](/referencia/precedencia)."},
];

const headings = [{ id: 'aritmeticos', text: "Aritméticos", level: 2 as const }, { id: 'comparacao', text: "Comparação", level: 2 as const }, { id: 'logicos', text: "Lógicos", level: 2 as const }, { id: 'coalescencia-e-acesso-seguro', text: "Coalescência e acesso seguro", level: 2 as const }, { id: 'pertinencia', text: "Pertinência", level: 2 as const }, { id: 'atribuicao-composta', text: "Atribuição composta", level: 2 as const }, { id: 'precedencia', text: "Precedência", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Operadores"}
      description={"Aritméticos, comparação, lógicos, coalescência, pertinência e a precedência completa."}
      href={"/operadores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
