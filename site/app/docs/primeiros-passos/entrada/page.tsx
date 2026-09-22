// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/primeiros_passos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "3. Perguntar ao usuário",
  description: "input(): ler o que a pessoa digita, converter em número, e o fim da entrada.",
};

const blocos: Bloco[] = [
  {"p": "Um programa fica interessante quando responde a quem o usa. `input(pergunta)` mostra a pergunta, espera a pessoa digitar e apertar Enter, e devolve **o texto** digitado."},
  { code: `nome := input("Qual e o seu nome? ")
out $"Ola, {nome}!"`, lang: 'df', title: `saudacao.df` },
  { code: `$ dataforge run saudacao.df
Qual e o seu nome? Ana
Ola, Ana!`, lang: 'text' },
  {"callout": {"tipo": "atencao", "titulo": "O que se digita é sempre TEXTO", "texto": "Mesmo que a pessoa digite `42`, `input` devolve o texto `\"42\"`. Para fazer conta, converta com `int(...)` ou `float(...)` — `\"42\" + 1` é um erro, e `int(\"42\") + 1` é `43`."}},
  { code: `// '?? "0"': se a entrada acabar, input devolve void, e int(void) seria erro.
idade := int(input("Sua idade: ") ?? "0")
out $"daqui a 10 anos voce tera {idade + 10}"`, lang: 'df', title: `idade.df` },
  {"h2": "Quando a pessoa digita algo que não é número"},
  { code: `action ler_inteiro(texto):
    monitor:
        yield int(texto)
    handle Error:
        yield void

assert ler_inteiro("42") is 42
assert ler_inteiro("quarenta") is void
out "o texto que nao e numero vira void, e o programa nao cai"`, lang: 'df' },
  {"h2": "Ler até acabar"},
  {"p": "Quando a entrada termina — Ctrl+D no terminal, ou o fim de um arquivo redirecionado —, `input` devolve `void`. É isso que deixa um laço de leitura terminar sozinho:"},
  { code: `total := 0
linha := input()
persist linha isnt void:
    total += int(linha)
    linha := input()
out $"soma: {total}"`, lang: 'df', title: `soma.df` },
  { code: `$ printf '10\\n20\\n12\\n' | dataforge run soma.df
soma: 42`, lang: 'text' },
  {"p": "Próximo: [4. Decidir](/docs/primeiros-passos/decisoes)."},
];

const headings = [{ id: 'quando-a-pessoa-digita-algo-que-nao-e-numero', text: "Quando a pessoa digita algo que não é número", level: 2 as const }, { id: 'ler-ate-acabar', text: "Ler até acabar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"3. Perguntar ao usuário"}
      description={"input(): ler o que a pessoa digita, converter em número, e o fim da entrada."}
      href={"/docs/primeiros-passos/entrada"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
