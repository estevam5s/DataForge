// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Carga, ordem e ciclos",
  description: "Quando o corpo de um módulo executa, o que ele deixa para trás, e por que um ciclo é erro aqui.",
};

const blocos: Bloco[] = [
  {"p": "Um `adopt` **executa** o arquivo, de cima a baixo, uma vez. Tudo o que estiver no topo dele roda — inclusive o que imprime, o que abre arquivo e o que conecta em banco."},
  {"h2": "O que roda, e quando"},
  { code: `// config.df — tudo isto roda no primeiro 'adopt'
out "lendo a configuração"
steady PORTA := 8000
conexao := abrir_banco()          // acontece AQUI, não no primeiro uso

action porta():
    yield PORTA

relay porta
`, lang: 'df' },
  {"p": "Efeito colateral no topo de um módulo é a causa mais comum de \"por que meu teste abre conexão?\". A regra prática é a mesma de qualquer linguagem com carga única: **no topo, só declaração e constante**; o que custa fica dentro de uma ação."},
  {"h2": "Ciclo é erro, e não meia resposta"},
  {"p": "As outras linguagens escolheram conviver com o ciclo: CommonJS devolve o módulo **pela metade**, e ESM deixa o nome numa zona morta onde lê-lo é erro de execução. As duas transformam um problema de arquitetura num bug intermitente."},
  { code: `adopt ./y as Y
action daqui():
    yield "x"
relay daqui
`, lang: 'df', title: `x.df` },
  { code: `adopt ./x as X
action dali():
    yield "y"
relay dali
`, lang: 'df', title: `y.df` },
  { code: `erro[DF0501]: Circular import: x.df → y.df → x.df.
Break the cycle by moving the shared part into a third module.
`, lang: 'text' },
  {"p": "**A cadeia inteira aparece.** Um ciclo de quatro arquivos é impossível de quebrar sem saber por onde ele passa, e a busca é em **largura** para achar o ciclo mais curto — que é o mais fácil de romper."},
  {"h2": "O `check` acha o ciclo antes de rodar"},
  {"p": "O ciclo estourava só em execução, no primeiro `adopt`, e o `check` passava limpo num projeto que não sobe:"},
  { code: `$ dataforge check x.df
x.df:1:1: erro: circular import: x.df → y.df → x.df
    sugestão: move the shared part into a third module
`, lang: 'bash' },
  {"callout": {"tipo": "dica", "titulo": "Rode o check na PASTA", "texto": "Conferir só o arquivo de entrada não acha o ciclo: ele não está no ciclo, apenas importa quem está. `dataforge check .` percorre todos, e é a forma que o CI deve usar."}},
  {"h2": "Como quebrar um ciclo"},
  {"list": ["**Mova o compartilhado para um terceiro módulo.** Se `x` e `y` se pedem, quase sempre é porque ambos precisam de um tipo ou de uma constante que não é de nenhum dos dois.", "**Inverta a dependência.** Quem sabe *como* fazer não deveria conhecer quem *manda* fazer: passe a ação como argumento em vez de importar o chamador.", "**Junte os dois.** Dois arquivos que se pedem em círculo frequentemente são um só arquivo que alguém dividiu cedo demais."], "ordered": true},
  {"h2": "Ordem de execução, num programa com módulos"},
  { code: `1. o interpretador lê o arquivo de entrada
2. cada 'adopt' do topo executa o módulo pedido, na ordem em que aparece
3. o módulo, por sua vez, executa os 'adopt' dele — em profundidade
4. um módulo já carregado NÃO executa de novo: devolve o mesmo objeto
5. o corpo do arquivo de entrada roda
6. os 'defer' escritos no topo rodam no fim, inclusive se houve erro
`, lang: 'text' },
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/modulos/superficie", "title": "A superfície", "desc": "o que o analisador consegue provar sobre outro arquivo"}, {"href": "/docs/tecnicas/concorrencia", "title": "Concorrência", "desc": "por que estado no topo de um módulo é perigoso num servidor"}]},
];

const headings = [{ id: 'o-que-roda-e-quando', text: "O que roda, e quando", level: 2 as const }, { id: 'ciclo-e-erro-e-nao-meia-resposta', text: "Ciclo é erro, e não meia resposta", level: 2 as const }, { id: 'o-check-acha-o-ciclo-antes-de-rodar', text: "O `check` acha o ciclo antes de rodar", level: 2 as const }, { id: 'como-quebrar-um-ciclo', text: "Como quebrar um ciclo", level: 2 as const }, { id: 'ordem-de-execucao-num-programa-com-modulos', text: "Ordem de execução, num programa com módulos", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Carga, ordem e ciclos"}
      description={"Quando o corpo de um módulo executa, o que ele deixa para trás, e por que um ciclo é erro aqui."}
      href={"/docs/modulos/carga"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
