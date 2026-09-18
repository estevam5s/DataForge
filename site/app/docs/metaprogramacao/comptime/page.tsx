// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/metaprogramacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "comptime",
  description: "A conta feita uma vez, na carga, e congelada: tabela gerada, constante calculada e validação que falha antes da primeira linha rodar.",
};

const blocos: Bloco[] = [
  {"p": "`comptime` marca o que é calculado **antes** de o programa começar. O resultado vira constante, e a validação que falhar ali derruba a carga — não a primeira requisição em produção."},
  { code: `comptime QUADRADOS := [i * i cycle i in range(0, 6)]
comptime steady MAXIMO := 2 ** 10

assert QUADRADOS is [0, 1, 4, 9, 16, 25]
assert MAXIMO is 1024`, lang: 'df' },
  {"h2": "Bloco, com ação própria"},
  {"p": "A tabela de consulta é o caso clássico: a conta é cara, a resposta é sempre a mesma, e ninguém quer pagá-la a cada chamada."},
  { code: `comptime:
    action fatorial(n):
        yield 1 given n smaller_eq 1 otherwise n * fatorial(n - 1)

    TABELA := [fatorial(i) cycle i in range(0, 6)]
    LIMITE := TABELA[5]

assert TABELA is [1, 1, 2, 6, 24, 120]
assert LIMITE is 120`, lang: 'df' },
  {"h2": "Validação estática"},
  {"p": "Um `assert` dentro de `comptime` é uma trava de **build**: o `dataforge check` a executa e acusa com o código `comptime-falhou`, antes de rodar."},
  { code: `comptime TABELA := [1, 2, 3]
comptime:
    assert len(TABELA) is 3              // se mudar, o check acusa

assert len(TABELA) is 3`, lang: 'df' },
  {"h2": "A caixa: o que não entra"},
  {"p": "Se `comptime` pudesse fazer E/S, \"tempo de compilação\" seria só \"mais cedo\". O corpo é varrido antes de rodar, e o que não é conta é recusado com o motivo."},
  {"table": {"head": ["Recusado", "Por quê"], "rows": [["`out`", "escrever na saída durante a carga confunde o que é programa com o que é build"], ["`adopt`", "módulo traz E/S; a conta de build não depende de disco, rede nem relógio"], ["`thread` e `parallel`", "deixaria trabalho correndo por baixo de um programa que ainda não começou"], ["`in` (ler da entrada), `wait`, `server`, `ignite`", "o mesmo motivo: pertencem ao programa"]]}},
  { code: `monitor:
    // este bloco é recusado na carga
    assert yes
handle Error as e:
    assert no

comptime SEGURO := 2 + 2
assert SEGURO is 4`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "'comptime' continua sendo um nome", "texto": "Como `type`, `opaque` e `where`, ele é **contextual**: `comptime := 3` e `action comptime(x)` continuam valendo. A declaração só começa quando o que vem depois confirma — `comptime:` abrindo bloco, ou `comptime NOME :=`."}},
  {"h2": "O que isto não é"},
  {"table": {"head": ["Não existe", "Por quê"], "rows": [["geração de código de máquina em build", "não há compilação para binário: o DataForge interpreta a árvore"], ["especialização de código por tipo", "o caminho aqui é `overload`, que decide na chamada, e a macro, que reescreve o corpo"], ["geração de tipos em compile-time", "o que existe é `type Par<T> := …` (alias genérico) e `Vetor<3>` (argumento numérico)"], ["`comptime` dentro de uma ação", "ele é declaração de topo: uma conta de build presa a uma chamada seria uma conta de execução com outro nome"]]}},
];

const headings = [{ id: 'bloco-com-acao-propria', text: "Bloco, com ação própria", level: 2 as const }, { id: 'validacao-estatica', text: "Validação estática", level: 2 as const }, { id: 'a-caixa-o-que-nao-entra', text: "A caixa: o que não entra", level: 2 as const }, { id: 'o-que-isto-nao-e', text: "O que isto não é", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"comptime"}
      description={"A conta feita uma vez, na carga, e congelada: tabela gerada, constante calculada e validação que falha antes da primeira linha rodar."}
      href={"/docs/metaprogramacao/comptime"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
