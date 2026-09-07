import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge test",
  description: "Descobrir e executar os testes",
};

const blocos: Bloco[] = [
  {"h2": "Uso"},
  { code: `dataforge test                    # tudo
dataforge test tests/ -v          # mostra cada caso
dataforge test --filter=primo     # só os que casam
dataforge test --fail-fast        # para na primeira falha`, lang: 'bash' },
  {"h2": "Descoberta"},
  {"p": "Arquivos `*_test.df`, `test_*.df` ou qualquer `.df` dentro de `tests/`. Dentro deles, **toda ação `test_*` é um caso**."},
  {"h2": "A saída"},
  { code: `✓ tests/matematica_test.df (3/3)
✗ tests/texto_test.df (1/2)
    FALHOU test_juncao
      join
      em tests/texto_test.df:12

4 passaram, 1 falharam em 2 arquivo(s) — 0.02s`, lang: 'text' },
  {"h2": "Ganchos"},
  {"p": "`setup_all`, `setup`, `teardown` e `teardown_all` são chamados quando existem. Guia completo em [Testes](/docs/tecnicas/testes)."},
];

const headings = [{ id: 'uso', text: "Uso", level: 2 as const }, { id: 'descoberta', text: "Descoberta", level: 2 as const }, { id: 'a-saida', text: "A saída", level: 2 as const }, { id: 'ganchos', text: "Ganchos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge test"}
      description={"Descobrir e executar os testes"}
      href={"/docs/cli/test"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
