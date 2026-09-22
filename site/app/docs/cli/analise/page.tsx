// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Análise do código",
  description: "stats, oop, big-o, custo e deps — o que o código é, sem rodá-lo.",
};

const blocos: Bloco[] = [
  {"p": "Cinco comandos que leem o código e respondem sobre a **forma** dele. Nenhum executa o programa, e todos aceitam arquivo, pasta ou padrão."},
  {"table": {"head": ["Comando", "Responde", "Quando"], "rows": [["`dataforge stats`", "quantas ações e blueprints, o arquivo e a ação mais longos", "achar o que cresceu demais sem ninguém notar"], ["`dataforge oop`", "WMC, DIT, CBO, LCOM… e os cheiros com o princípio SOLID", "revisar um desenho de classes"], ["`dataforge big-o`", "a classe de complexidade de cada ação, **e o porquê**", "antes de otimizar"], ["`dataforge custo`", "o que cada `adopt` traz junto", "a partida está lenta"], ["`dataforge deps`", "o grafo de imports, e os ciclos", "entender um projeto novo"]]}},
  { code: `dataforge stats src/
dataforge oop src/ --diagrama > classes.mmd   # Mermaid, para o README
dataforge oop src/ --strict                   # reprova o CI com cheiro
dataforge big-o src/ -v                       # a classe e o que fazer
dataforge big-o src/ --medir                  # confere a classe medindo
dataforge big-o --escala                      # a tabela do que cada classe custa
dataforge custo src/
dataforge deps`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "Errar a classe é pior que não ter a ferramenta", "texto": "O `big-o` erra com confiança, e o relatório é curto o bastante para ser lido como verdade. Quatro erros de classificação já foram medidos e corrigidos — o merge sort como `O(n log² n)`, a busca binária como `O(2ⁿ)` —, e hoje `--medir` confere a classe estimada contra o tempo real. Use o `-v`: a classe sem o porquê não ajuda a melhorar nada."}},
  {"p": "Continue em [Big-O](/docs/big-o) e [Métricas de OOP](/docs/oop)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Análise do código"}
      description={"stats, oop, big-o, custo e deps — o que o código é, sem rodá-lo."}
      href={"/docs/cli/analise"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
