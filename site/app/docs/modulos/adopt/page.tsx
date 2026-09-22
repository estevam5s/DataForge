// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "As formas de adopt",
  description: "Seis formas, e o que cada uma muda — inclusive a que traz qualquer biblioteca do Python.",
};

const blocos: Bloco[] = [
  {"p": "`adopt` é uma palavra e seis formas. A escolha entre elas não é estilo: ela decide o que o leitor do arquivo consegue saber sem sair dele."},
  { code: `// 1. O modulo inteiro, com o nome dele.
adopt Arcane.Math

// 2. Com apelido — o mais comum, e o que encurta sem esconder.
adopt Arcane.Math as M

// 3. So o que se usa.
adopt Arcane.Math.{sqrt, floor}

// 4. So o que se usa, renomeando.
adopt {sqrt as raiz} from Arcane.Math

out M.PI
out sqrt(16.0)
out raiz(25.0)
assert floor(3.7) is 3`, lang: 'df' },
  {"table": {"head": ["Forma", "Quando", "O que ela custa"], "rows": [["`adopt X`", "uso raro, nome curto", "o nome inteiro em cada chamada"], ["`adopt X as M`", "**o padrão**", "nada; o apelido diz de onde veio"], ["`adopt X.{a, b}`", "duas ou três funções muito usadas", "quem lê `sqrt(x)` não sabe de onde ele vem"], ["`adopt {a as b} from X`", "quando o nome colide", "idem, mais o nome trocado"], ["`adopt ./vizinho`", "arquivo do próprio projeto", "o caminho é relativo a **este** arquivo"], ["`adopt Python.numpy`", "biblioteca do Python", "a dependência deixa de ser zero"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O import seletivo apaga a origem", "texto": "`adopt Arcane.Math.{sqrt}` faz `sqrt(x)` ficar igual a uma função do próprio arquivo — e num arquivo de trezentas linhas, quem lê no meio não tem como saber de onde ela veio sem subir até o topo. Vale para duas ou três funções de uso muito frequente; a partir daí, o apelido custa três caracteres e devolve a informação."}},
  {"h2": "Caminhos relativos"},
  { code: `// 'adopt ./x' procura ao lado DESTE arquivo — e nao da pasta em
// que o programa foi executado. A diferenca aparece quando o mesmo
// modulo e importado de duas profundidades.
//
//   projeto/
//     src/
//       main.df          adopt ./modelos
//       modelos.df
//       admin/
//         painel.df      adopt ../modelos
//
// E o hifen funciona: 'adopt ./minha-lib as L'. O lexer entrega o
// hifen como MINUS, e o caminho so o cola ao nome quando as colunas
// sao ADJACENTES — sem essa guarda, 'a - b' viraria um arquivo
// chamado 'a-b'.

out "o caminho e relativo ao arquivo, e nao ao diretorio de trabalho"`, lang: 'df' },
  {"h2": "A ponte para o Python"},
  {"p": "`Python` é espaço de nomes **reservado**, resolvido antes da biblioteca e dos arquivos vizinhos — um `Python.df` no disco não sequestra o import."},
  { code: `// adopt Python.numpy as np
//
// A ponte NAO CONVERTE: um 'ndarray' continua um 'ndarray', e
// 'a * 2' e a conta vetorizada do numpy, e nao um laco sobre um
// milhao de posicoes. Isso so funciona porque o interpretador trata
// objeto estranho por PROTOCOLO — membro, metodo, indice, 'len',
// iteracao, aritmetica, texto e verdade.

out "a ponte existe, e a dependencia passa a ser sua"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Um `adopt Python.x` muda a promessa do seu projeto", "texto": "`dataforge/` não tem dependência externa, e é isso que faz `pip install dataforge-lang` bastar numa máquina sem compilador. No momento em que o **seu** código adota um módulo do Python, quem instalar o seu projeto precisa daquele pacote também — e o `forge.toml` não sabe disso. Declare no README, e prefira o que a biblioteca já resolve."}},
  {"p": "Continue em [Resolução](/docs/modulos/resolucao) e [A ponte](/docs/tecnicas/ponte)."},
];

const headings = [{ id: 'caminhos-relativos', text: "Caminhos relativos", level: 2 as const }, { id: 'a-ponte-para-o-python', text: "A ponte para o Python", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"As formas de adopt"}
      description={"Seis formas, e o que cada uma muda — inclusive a que traz qualquer biblioteca do Python."}
      href={"/docs/modulos/adopt"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
