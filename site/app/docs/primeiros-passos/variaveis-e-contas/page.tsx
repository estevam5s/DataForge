// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/primeiros_passos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Variáveis e contas",
  description: "Dar nome a um valor com :=, e as contas que a linguagem sabe fazer.",
};

const blocos: Bloco[] = [
  {"p": "Uma **variável** é um nome para um valor. Você guarda o valor uma vez e usa o nome quantas vezes quiser. Em DataForge, guardar se escreve `:=` — lê-se *“recebe”*."},
  { code: `preco := 12.50
quantidade := 3
total := preco * quantidade
out "total:", total

// O nome pode receber outro valor depois.
quantidade := 4
total := preco * quantidade
out "agora:", total
assert total is 50.0`, lang: 'df' },
  {"h2": "As contas"},
  {"table": {"head": ["Escreva", "Faz", "Exemplo", "Dá"], "rows": [["`+` `-` `*`", "soma, subtração, multiplicação", "`7 * 3`", "`21`"], ["`/`", "divisão — sempre com vírgula", "`7 / 2`", "`3.5`"], ["`~/`", "divisão **inteira**", "`7 ~/ 2`", "`3`"], ["`%`", "o resto da divisão", "`7 % 2`", "`1`"], ["`**`", "potência", "`2 ** 10`", "`1024`"]]}},
  { code: `assert 7 / 2 is 3.5
assert 7 ~/ 2 is 3
assert 7 % 2 is 1
assert 2 ** 10 is 1024
assert (2 + 3) * 4 is 20     // os parenteses mandam
assert 2 + 3 * 4 is 14       // sem eles, a multiplicacao vem antes
out "todas as contas conferem"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`//` não é divisão", "texto": "Em muitas linguagens `//` divide; aqui, `//` começa um **comentário**. A divisão inteira é `~/`. Se você escrever `x // 2` e o resultado parecer estranho, é isso."}},
  {"h2": "Constantes"},
  { code: `steady PI := 3.14159
raio := 2
out "area:", PI * raio ** 2
// PI := 3 daria erro: 'steady' e um valor que nao muda.`, lang: 'df' },
  {"p": "Próximo: [Perguntar ao usuário](/docs/primeiros-passos/entrada)."},
];

const headings = [{ id: 'as-contas', text: "As contas", level: 2 as const }, { id: 'constantes', text: "Constantes", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Variáveis e contas"}
      description={"Dar nome a um valor com :=, e as contas que a linguagem sabe fazer."}
      href={"/docs/primeiros-passos/variaveis-e-contas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
