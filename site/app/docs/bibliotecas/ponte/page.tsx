// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Embrulhar uma biblioteca do Python",
  description: "Quando vale, o que a ponte não converte — e a promessa que o seu pacote passa a quebrar.",
};

const blocos: Bloco[] = [
  {"p": "`adopt Python.numpy as np` traz qualquer biblioteca do Python. Numa **aplicação**, é conveniência. Numa **biblioteca publicada**, é uma decisão que passa para quem instala."},
  {"callout": {"tipo": "atencao", "titulo": "A dependência deixa de ser zero — e o `forge.toml` não sabe disso", "texto": "`dataforge/` não tem dependência externa, e é isso que faz `pip install dataforge-lang` bastar numa máquina sem compilador. No momento em que o **seu** pacote adota `Python.lxml`, quem o instalar precisa daquele pacote também — e o gerenciador não vai instalá-lo. Declare no README, e falhe com uma mensagem que diga o comando."}},
  {"h2": "A ponte não converte"},
  { code: `// Um 'ndarray' continua um 'ndarray'. E o que faz 'a * 2' ser a
// conta vetorizada do numpy, e nao um laco sobre um milhao de
// posicoes.
//
// Isso so funciona porque o interpretador trata objeto estranho por
// PROTOCOLO — membro, metodo, indice, 'len', iteracao, aritmetica,
// texto e verdade ja passavam assim. Trocar protocolo por
// 'isinstance' em qualquer um deles quebraria a ponte inteira.

// E 'typeof' tem uma excecao de proposito: 'np.int64' nao e
// subclasse de 'int', mas faz conta de inteiro — entao ele responde
// 'Integer'. Nao ha nada de numpy no interpretador: 'Fraction' e
// 'Decimal' entram pela mesma porta.

out "a ponte e por protocolo, e nao por tipo"`, lang: 'df' },
  {"h2": "Quando vale, e quando não"},
  {"table": {"head": ["Vale", "Não vale"], "rows": [["o trabalho é numérico pesado (numpy, scipy)", "a biblioteca já existe em `Arcane.*`"], ["um formato binário complexo com implementação madura", "dá para escrever em 200 linhas sem dependência"], ["um driver que fala um protocolo proprietário", "só para economizar uma tarde"], ["a conta é o gargalo **medido**", "*“pode vir a ser mais rápido”*"]]}},
  {"h2": "A falha tem de nomear o Python exato"},
  {"p": "O instalador cria uma venv em `~/.dataforge`, e um `pip install` no terminal instala em **outro** Python. Uma mensagem que só diz *“módulo não encontrado”* manda a pessoa rodar o comando que já não funcionou."},
  {"table": {"head": ["Ambiente", "O que a mensagem deve dizer"], "rows": [["venv do instalador", "o caminho do Python que está rodando"], ["executável único", "`pip install dataforge-lang` — ali não há `pip` nenhum"], ["`pip install -e .`", "o `pip` do próprio ambiente"]]}},
  {"p": "Continue em [A ponte](/docs/tecnicas/ponte) e [As formas de adopt](/docs/modulos/adopt)."},
];

const headings = [{ id: 'a-ponte-nao-converte', text: "A ponte não converte", level: 2 as const }, { id: 'quando-vale-e-quando-nao', text: "Quando vale, e quando não", level: 2 as const }, { id: 'a-falha-tem-de-nomear-o-python-exato', text: "A falha tem de nomear o Python exato", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Embrulhar uma biblioteca do Python"}
      description={"Quando vale, o que a ponte não converte — e a promessa que o seu pacote passa a quebrar."}
      href={"/docs/bibliotecas/ponte"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
