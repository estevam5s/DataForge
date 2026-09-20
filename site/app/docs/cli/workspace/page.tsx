// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fechamento.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A árvore inteira, e os conflitos dela",
  description: "Vários pacotes num repositório: quem depende de quê, e duas faixas incompatíveis do mesmo terceiro — achadas antes de instalar.",
};

const blocos: Bloco[] = [
  {"p": "Cada pacote tem o seu `forge.toml`. A única forma de saber se dois deles pedem faixas **incompatíveis** do mesmo terceiro era instalar os dois e esperar o erro — que aparece no dia da instalação, na máquina de quem consome."},
  { code: `dataforge workspace              # a arvore daqui para baixo
dataforge workspace packages     # so uma pasta
dataforge workspace --json       # para o CI ler
dataforge ws                     # o mesmo comando`, lang: 'bash' },
  { code: `── 25 pacote(s) em packages ──
  aleatorio            0.1.0      0 dep(s)  aleatorio/forge.toml
  validador            0.1.0      1 dep(s)  validador/forge.toml
  …

  nenhum conflito de faixa entre os pacotes`, lang: 'text', title: `dataforge workspace — a saída` },
  {"h2": "Conflito é erro, e não aviso"},
  {"p": "O comando **sai com 2** quando duas faixas não se cruzam. É a mesma decisão que o resolvedor de dependências já tomava: instalar duas cópias do mesmo pacote em versões diferentes gera bug irreproduzível."},
  { code: `  CONFLITOS:
   terceiro
      um pede 1.0.0
      dois pede 2.0.0`, lang: 'text' },
  {"callout": {"tipo": "nota", "titulo": "A interseção sai da MESMA classe que o `add` usa", "texto": "`Requisito`, de `packages.py`. Uma segunda noção de *\"estas faixas se cruzam?\"* divergiria da instalação — e aí o relatório aprovaria o que o `add` recusa, que é o pior resultado possível para duas respostas da mesma pergunta."}},
  {"h2": "Ele não inventa conflito"},
  {"p": "Sem uma lista das versões publicadas não há como decidir por enumeração. Então a pergunta é feita sobre os **pinos exatos**: se um lado exige `==X` e o outro recusa o `X`, o conflito está **provado**. Fora disso, cala."},
  {"table": {"head": ["Um pede", "O outro pede", "Veredito"], "rows": [["`1.0.0`", "`2.0.0`", "**conflito** — o pino de um é recusado pelo outro"], ["`^1.0.0`", "`>=1.0.0`", "cala — as faixas podem se cruzar"], ["`^1.0.0`", "`1.5.0`", "cala — `1.5.0` satisfaz `^1.0.0`"]]}},
  {"p": "É a mesma prudência do [analisador estático](/docs/tecnicas/analise-estatica): um falso conflito faria o comando ser ignorado, e aí ele não serviria para o caso verdadeiro."},
  {"h2": "E ele não instala"},
  {"p": "Ler e relatar. Instalar a árvore inteira a partir de um comando que a pessoa rodou para *\"ver o que tem\"* seria mexer em disco sem ser pedido — quem quer instalar chama `dataforge install`, em cada pacote."},
  {"p": "As pastas que não são pacote do projeto ficam fora da varredura: `forge_modules`, `node_modules`, `dist`, `out`, `.venv` e as que começam com ponto."},
];

const headings = [{ id: 'conflito-e-erro-e-nao-aviso', text: "Conflito é erro, e não aviso", level: 2 as const }, { id: 'ele-nao-inventa-conflito', text: "Ele não inventa conflito", level: 2 as const }, { id: 'e-ele-nao-instala', text: "E ele não instala", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A árvore inteira, e os conflitos dela"}
      description={"Vários pacotes num repositório: quem depende de quê, e duas faixas incompatíveis do mesmo terceiro — achadas antes de instalar."}
      href={"/docs/cli/workspace"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
