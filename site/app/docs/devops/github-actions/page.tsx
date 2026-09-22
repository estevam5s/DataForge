// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "GitHub Actions",
  description: "O pipeline na ordem que economiza tempo — e o erro de análise anotado na linha do PR.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge devops ci github` escreve `.github/workflows/ci.yml`: formato, análise estática, lint e testes, numa matriz de Python, com um push novo cancelando o anterior. A ordem é a do custo: o `check` acha nome errado e ciclo de import em menos de um segundo, e falhar ali poupa os minutos da suíte."},
  { code: `dataforge devops ci github
git add .github/workflows/ci.yml && git commit -m "CI"`, lang: 'bash' },
  {"h2": "O erro na linha do PR"},
  {"p": "`dataforge check --formato=github` troca o desenho do terminal por **anotações do Actions**. Com elas o erro aparece na aba *Files changed*, na linha exata — e não só no log do job, que ninguém abre enquanto o resto do PR está verde."},
  { code: `$ dataforge check src/ --formato=github
::error file=src/pedido.df,line=14,col=5,title=arity::Action 'total' takes 1 argument(s) but 2 were given%0Asugestão: Chame como total(itens)
::warning file=src/pedido.df,line=30,col=9,title=escrita-concorrente::…`, lang: 'text' },
  {"table": {"head": ["Decisão", "Porque"], "rows": [["o nível segue a gravidade", "erro vira `::error`, aviso vira `::warning` — o PR distingue os dois"], ["o `title` é o código do diagnóstico", "`arity`, `undefined-name`: é o que se procura e o que se silencia com `// df: permitir`"], ["a sugestão vai junto", "a correção aparece na mesma caixa que o erro"], ["a mensagem é escapada", "um `%` ou uma quebra de linha cortaria a anotação no meio"], ["o código de saída não muda", "o job continua reprovando com erro, com ou sem anotação"]]}},
  {"h2": "O que o workflow gerado já faz"},
  {"table": {"head": ["No workflow", "Sem ele"], "rows": [["`concurrency` com `cancel-in-progress`", "dois commits num minuto rodam a suíte duas vezes inteiras"], ["matriz `3.10` e `3.13`", "o que quebra na versão mínima só aparece com o primeiro usuário dela"], ["`fail-fast: false`", "a primeira versão que falha cancela a outra, e não se sabe se é geral"], ["o job da imagem confere `id -u`", "a imagem que roda como root chega ao registro"]]}},
  {"p": "Continue em [Actions na linguagem](/docs/devops/actions-na-linguagem)."},
];

const headings = [{ id: 'o-erro-na-linha-do-pr', text: "O erro na linha do PR", level: 2 as const }, { id: 'o-que-o-workflow-gerado-ja-faz', text: "O que o workflow gerado já faz", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"GitHub Actions"}
      description={"O pipeline na ordem que economiza tempo — e o erro de análise anotado na linha do PR."}
      href={"/docs/devops/github-actions"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
