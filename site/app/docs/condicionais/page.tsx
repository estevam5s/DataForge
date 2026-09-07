import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Condicionais",
  description: "given, orif, otherwise, o ternário e a seleção múltipla com match.",
};

const blocos: Bloco[] = [
  {"h2": "given / orif / otherwise"},
  {"p": "A estrutura condicional do DataForge. `given` lê-se \"dado que\":"},
  { code: `action classificar(n):
    given n bigger 0:
        yield "positivo"
    orif n smaller 0:
        yield "negativo"
    otherwise:
        yield "zero"

cycle n in [5, -3, 0]:
    out $"{n} -> {classificar(n)}"` },
  { code: `5 -> positivo
-3 -> negativo
0 -> zero`, lang: 'text', title: `saída` },
  {"p": "Pode haver quantos `orif` você precisar, e o `otherwise` é opcional."},
  {"h3": "A ordem importa"},
  {"p": "Os ramos são testados de cima para baixo, e o primeiro verdadeiro vence. Coloque sempre o mais específico primeiro:"},
  { code: `action conceito(nota):
    given nota bigger_eq 9:
        yield "A"
    orif nota bigger_eq 7:      # só chega aqui se não for >= 9
        yield "B"
    orif nota bigger_eq 5:
        yield "C"
    otherwise:
        yield "D"` },
  {"h2": "O ternário"},
  {"p": "Para escolher entre dois valores, sem abrir um bloco:"},
  { code: `n := 4
rotulo := "par" given n % 2 is 0 otherwise "impar"
out rotulo` },
  {"p": "Lê-se: *\"este valor, dado que a condição vale, senão o outro\"*. Associa à direita, então encadeia:"},
  { code: `n := 0
x := "positivo" given n bigger 0 otherwise "zero" given n is 0 otherwise "negativo"
out x` },
  {"callout": {"tipo": "dica", "texto": "O ternário rende em dois ou três casos. Com quatro ou mais, um bloco `given`/`orif` lê melhor."}},
  {"h2": "match — seleção múltipla"},
  {"p": "Quando a decisão depende do **formato** do valor, e não de uma condição booleana, o `match` é a ferramenta:"},
  { code: `action dia(n):
    match n:
        point 1:
            yield "segunda"
        point 2:
            yield "terca"
        point 3:
            yield "quarta"
        default:
            yield "desconhecido"

out dia(1), dia(3), dia(9)` },
  {"p": "Diferente de um `switch` de C, **não há fall-through**: o ramo que casa executa e o `match` termina."},
  {"h3": "Alternativas com or"},
  { code: `action tipo(n):
    match n:
        point 1 or 2 or 3:
            yield "pequeno"
        point 100 or 200:
            yield "redondo"
        default:
            yield "outro"` },
  {"p": "O `match` do DataForge vai muito além de comparar valores — ele desmonta estruturas, testa tipos e aceita guardas. Isso está em [Pattern matching](/docs/fundamentos/pattern-matching)."},
  {"h2": "Verdadeiro e falso"},
  {"p": "Em contexto booleano, estes valores são **falsos**:"},
  {"list": ["`void`", "`no`", "`0` e `0.0`", "`\"\"` (texto vazio)", "`[]` (lista vazia)", "`{}` (vault vazio)"]},
  {"p": "Todo o resto é verdadeiro. Ainda assim, comparar explicitamente costuma ler melhor:"},
  { code: `given len(itens) is 0:        # claro
given not itens:              # funciona, mas menos explícito` },
];

const headings = [{ id: 'given--orif--otherwise', text: "given / orif / otherwise", level: 2 as const }, { id: 'o-ternario', text: "O ternário", level: 2 as const }, { id: 'match--selecao-multipla', text: "match — seleção múltipla", level: 2 as const }, { id: 'verdadeiro-e-falso', text: "Verdadeiro e falso", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Condicionais"}
      description={"given, orif, otherwise, o ternário e a seleção múltipla com match."}
      href={"/docs/condicionais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
