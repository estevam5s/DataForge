// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fundamentos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Verdade e ausência",
  description: "void, o que é verdadeiro, ?? e ?. — e por que 'não sei' não é zero.",
};

const blocos: Bloco[] = [
  {"p": "`void` é a ausência: *não há valor aqui*. Ele não é zero, não é texto vazio e não é `no` — confundir os três é a origem de metade dos bugs de dados: a média que conta o *“não respondeu”* como zero."},
  { code: `nada := void
assert nada is void
assert typeof(nada) is "Void"
assert void isnt 0 and void isnt "" and void isnt no`, lang: 'df' },
  {"h2": "O que conta como verdadeiro"},
  {"table": {"head": ["Falso (`no`)", "Verdadeiro (`yes`)"], "rows": [["`no`, `void`", "`yes`"], ["`0`, `0.0`", "qualquer outro número"], ["`\"\"`", "qualquer texto com algo"], ["`[]`, `{}`, `set()`", "qualquer coleção com algo"]]}},
  { code: `action tem_algo(x):
    given x:
        yield yes
    yield no

assert not tem_algo(0) and not tem_algo("") and not tem_algo([]) and not tem_algo(void)
assert tem_algo(-1) and tem_algo(" ") and tem_algo([0])`, lang: 'df' },
  {"h2": "Tratar a ausência: `??` e `?.`"},
  { code: `cliente := {"nome": "Ana"}

// ?? — o valor, ou um padrao quando e void (ou a chave nao existe).
assert cliente["telefone"] ?? "sem telefone" is "sem telefone"

// ?. — le o membro so se houver objeto; senao, void, sem erro.
endereco := void
assert endereco?.cidade is void

// 'and' e 'or' devolvem o VALOR que decidiu.
assert (void or "padrao") is "padrao"
assert (0 or "padrao") is "padrao"      // cuidado: 0 tambem e falso!
assert (0 ?? "padrao") is 0             // '??' so troca o void`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`or` troca o zero; `??` não", "texto": "`quantidade or 1` transforma uma quantidade **zero** em 1 — porque zero é falso. `quantidade ?? 1` só troca a ausência. Para padrão de valor, use `??`."}},
];

const headings = [{ id: 'o-que-conta-como-verdadeiro', text: "O que conta como verdadeiro", level: 2 as const }, { id: 'tratar-a-ausencia-e', text: "Tratar a ausência: `??` e `?.`", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Verdade e ausência"}
      description={"void, o que é verdadeiro, ?? e ?. — e por que 'não sei' não é zero."}
      href={"/docs/fundamentos/ausencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
