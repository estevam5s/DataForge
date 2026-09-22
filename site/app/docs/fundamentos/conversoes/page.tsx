// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fundamentos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Conversões",
  description: "int, float, str, cast e typeof — e o que acontece quando o valor não converte.",
};

const blocos: Bloco[] = [
  {"p": "O que vem de fora — do teclado, de um CSV, de um JSON — chega quase sempre como texto. Converter é explícito nesta linguagem: `\"42\" + 1` é erro, e não `\"421\"` nem `43`."},
  { code: `assert int("42") + 1 is 43
assert float("3.5") * 2 is 7.0
assert str(42) + "!" is "42!"
assert int(3.9) is 3                 // corta, nao arredonda
assert cast "7" as Integer is 7
assert bool(0) is no and bool("x") is yes
assert typeof(int("5")) is "Integer"`, lang: 'df' },
  {"h2": "Quando não converte"},
  { code: `action como_inteiro(texto, padrao := void):
    monitor:
        yield int(texto)
    handle Error:
        yield padrao

assert como_inteiro("12") is 12
assert como_inteiro("12,5") is void          // virgula nao e ponto
assert como_inteiro("", 0) is 0
out "o que nao converte vira void — e voce decide o que fazer"`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Num CSV grande, converta a coluna", "texto": "Converter linha a linha com `monitor` num arquivo de um milhão de linhas é lento e esconde quantas falharam. `Quadro.converter({\"idade\": \"Integer\"})` converte a coluna inteira, põe `void` no que não converte, e conta as falhas em `perfil()`."}},
  {"h2": "Texto de um valor"},
  { code: `assert str([1, 2]) is "[1, 2]"
assert str({"a": 1}) is "{a: 1}"
assert str(void) is "void" and str(yes) is "yes"
assert $"total: {10 * 3}" is "total: 30"`, lang: 'df' },
];

const headings = [{ id: 'quando-nao-converte', text: "Quando não converte", level: 2 as const }, { id: 'texto-de-um-valor', text: "Texto de um valor", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Conversões"}
      description={"int, float, str, cast e typeof — e o que acontece quando o valor não converte."}
      href={"/docs/fundamentos/conversoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
