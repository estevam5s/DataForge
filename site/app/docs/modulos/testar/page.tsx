// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar código modular",
  description: "Testar um módulo pelo caminho que um usuário usaria — e as duas armadilhas que fazem a suíte mentir.",
};

const blocos: Bloco[] = [
  {"p": "Um teste que importa o módulo por um caminho que ninguém mais usa não prova que o módulo é utilizável."},
  { code: `// packages/validador/tests/cpf_test.df
//
// CERTO: pelo NOME do pacote, como um usuario faria.
//   adopt validador as V
//
// ERRADO: por caminho relativo ate a fonte.
//   adopt ../src/main as V
//
// A segunda forma passa e nao prova nada sobre a instalacao. Foi
// ela que escondeu que um pacote nao sabia se importar pelo proprio
// nome: as suites dos VINTE pacotes deste repositorio falhavam, e o
// CI nao apanhava — ele nao rodava 'dataforge test' dentro de
// 'packages/'.

out "teste pelo caminho que o usuario usa"`, lang: 'df' },
  {"h2": "As duas armadilhas"},
  {"callout": {"tipo": "atencao", "titulo": "1. “Tudo verde” com um teste reprovado", "texto": "Um arquivo com `crucible`/`trial` **registra** as suítes e não as roda — quem roda é `Crucible.run()`. O corredor caía no caso *“sem ações `test_`, o próprio arquivo é o caso”* e contava o arquivo como **um teste que passou**. Um arquivo com dez `trial`, um deles quebrado, saía com **código 0** — e `dataforge crucible`, sobre a mesma suíte, saía com 1. Os dois discordavam, e o nome mais óbvio era o que mentia."}},
  {"callout": {"tipo": "atencao", "titulo": "2. A cobertura otimista", "texto": "O denominador vem do parser (quais linhas são **executáveis**), e a definição de “instrução” é a existência de `exec_<Nó>` no interpretador — e não uma lista. A primeira versão era uma lista e apodreceu antes de ser commitada: ela tinha `CycleLoop`, e o nó se chama `CycleFromTo`. O laço inteiro ficava fora do denominador, e a cobertura saía **otimista** — o pior defeito possível numa métrica."}},
  {"h2": "O teste de um módulo"},
  { code: `adopt Arcane.Crucible

crucible "normalizacao":
    trial "tira espaco e caixa":
        expect(normalizar("  Café  ")) to_be("café")

    trial "texto vazio nao quebra":
        expect(normalizar("")) to_be("")

    trial "ainda nao decidido" pending:
        expect(normalizar(void)) to_be("")

action normalizar(t):
    yield (t ?? "").strip().lower()

r := Crucible.run()
out $"{r['passou']} passaram, {r['pendente']} pendente(s)"`, lang: 'df' },
  {"table": {"head": ["Comando", "Cobre"], "rows": [["`dataforge test .`", "descobre `*_test.df` e `tests/`"], ["`dataforge test --cobertura --minimo=80`", "reprova o CI abaixo do piso"], ["`dataforge test --fail-fast`", "para na primeira falha"], ["`dataforge check . --strict`", "o que nem chega a rodar"]]}},
  {"p": "Continue em [Testes de biblioteca](/docs/bibliotecas/testes) e [Crucible](/docs/testes)."},
];

const headings = [{ id: 'as-duas-armadilhas', text: "As duas armadilhas", level: 2 as const }, { id: 'o-teste-de-um-modulo', text: "O teste de um módulo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar código modular"}
      description={"Testar um módulo pelo caminho que um usuário usaria — e as duas armadilhas que fazem a suíte mentir."}
      href={"/docs/modulos/testar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
