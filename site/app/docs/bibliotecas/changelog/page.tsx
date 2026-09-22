// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O CHANGELOG",
  description: "O que escrever, em que ordem, e a seção que quase todo mundo esquece.",
};

const blocos: Bloco[] = [
  {"p": "O CHANGELOG é para quem vai **atualizar**, e a pergunta dessa pessoa é uma só: *o que eu preciso mudar no meu código?*. Por isso ele é organizado pelo efeito, e não pela ordem dos commits."},
  { code: `## 2.0.0

### Quebra — o que voce precisa mudar
- \`total(itens)\` foi removida. Use \`calcular_total(itens)\` — avisava desde a 1.4.

### Adicionado
- \`calcular_frete(uf, peso)\`.

### Corrigido
- \`desconto\` arredondava para baixo; agora arredonda para o mais proximo.

### Obsoleto — vai sair na 3.0
- \`frete_fixo()\`: use \`calcular_frete\`.`, lang: 'text', title: `CHANGELOG.md` },
  {"table": {"head": ["Seção", "Porque ela existe"], "rows": [["**Quebra** (primeiro)", "é o que impede a atualização; escondê-la no meio é o que faz alguém atualizar e quebrar produção"], ["Adicionado", "o que se ganha"], ["Corrigido", "o comportamento que mudou — uma correção é uma mudança para quem dependia do defeito"], ["**Obsoleto**", "a seção esquecida: é ela que dá tempo de migrar"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Uma correção também quebra", "texto": "Se `desconto` arredondava errado há dois anos, alguém tem um relatório que depende do número errado. A correção entra no CHANGELOG dizendo **o que mudou no resultado** — e não só *“corrigido bug”*."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"O CHANGELOG"}
      description={"O que escrever, em que ordem, e a seção que quase todo mundo esquece."}
      href={"/docs/bibliotecas/changelog"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
