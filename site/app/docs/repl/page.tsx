// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/plataforma_runtime.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O REPL",
  description: "O console interativo: avaliar, inspecionar a árvore, medir tempo e carregar um arquivo na sessão.",
};

const blocos: Bloco[] = [
  {"p": "O REPL é onde se responde \"o que essa linha faz?\" sem criar arquivo. Ele carrega o mesmo interpretador, a mesma biblioteca e o mesmo analisador — o que você vê ali é o que o programa vai fazer."},
  { code: `dataforge repl
`, lang: 'bash' },
  { code: `forge> x := 21
forge> x * 2
=> 42
forge> :type x
Integer  = 21
forge> exit
`, lang: 'text' },
  {"h2": "Os comandos"},
  {"table": {"head": ["Comando", "O que faz"], "rows": [["`:help`", "a lista (ou `help`)"], ["`:exit`", "sai (ou `exit`, `quit`, Ctrl+D)"], ["`:env`", "as variáveis definidas na sessão"], ["`:type <expr>`", "o tipo **e** o valor de uma expressão"], ["`:doc <nome>`", "o que é um nome definido na sessão"], ["`:check <código>`", "roda o analisador estático sobre o trecho"], ["`:tokens <código>`", "o fluxo de tokens — para entender o lexer"], ["`:ast <código>`", "a árvore sintática"], ["`:time <código>`", "executa e mede"], ["`:load <arquivo>`", "carrega e executa um `.df` **na sessão atual**"], ["`:save <arquivo>`", "grava o histórico da sessão num `.df`"], ["`:history [n]`", "os últimos comandos"], ["`:modules`", "os módulos `Arcane` disponíveis"], ["`:reset`", "zera o interpretador"], ["`:clear`", "limpa a tela"], ["`:version`", "a versão"]]}},
  {"h2": "Blocos de várias linhas"},
  {"p": "Uma linha terminada em `:` abre um bloco, que continua até uma **linha em branco**:"},
  { code: `forge> action dobro(n):
   ...     yield n * 2
   ...
forge> dobro(21)
=> 42
`, lang: 'text' },
  {"h2": "Carregar um arquivo e continuar de dentro dele"},
  {"p": "`:load` é o que transforma o REPL em ferramenta de depuração: o programa roda, e você fica com **as variáveis dele** ao alcance."},
  { code: `forge> :load src/main.df
forge> :env
forge> clientes[0]
forge> calcular_total(clientes)
`, lang: 'text' },
  {"h2": "Entender a linguagem por dentro"},
  {"p": "Três comandos existem para responder perguntas sobre a própria linguagem, e são os mesmos que se usa ao mexer no interpretador:"},
  { code: `forge> :tokens x := 7 ~/ 2
forge> :ast given a: out 1
forge> :check xs := [1, 2]
       out xs[10]
`, lang: 'text' },
  {"p": "O `:tokens` é a forma rápida de resolver a dúvida do `//`: seguido de dígito é divisão, seguido de nome é comentário."},
  {"h2": "Medir no lugar certo"},
  { code: `forge> :time [x * x cycle x in range(100000)]
`, lang: 'text' },
  {"p": "`:time` mede **aquela** expressão. Para comparar duas implementações com rigor, use [`Arcane.Bench`](/docs/tecnicas/bench); para achar onde o tempo vai num programa real, `dataforge profile`."},
  {"h2": "O que o REPL não é"},
  {"list": ["**Não é um editor.** Para algo com mais de dez linhas, `:save` e siga num arquivo.", "**Não guarda estado entre sessões.** `:save` grava o histórico; fechar o console perde as variáveis.", "**Não substitui teste.** O que funcionou no console precisa virar `trial` para continuar funcionando amanhã."]},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/cli/repl", "title": "Referência do comando", "desc": "as opções de linha de comando"}, {"href": "/docs/cli/explain", "title": "dataforge explain", "desc": "o que um código de erro significa"}, {"href": "/docs/primeiros-passos", "title": "Primeiros passos", "desc": "a linguagem em cinco minutos"}]},
];

const headings = [{ id: 'os-comandos', text: "Os comandos", level: 2 as const }, { id: 'blocos-de-varias-linhas', text: "Blocos de várias linhas", level: 2 as const }, { id: 'carregar-um-arquivo-e-continuar-de-dentro-dele', text: "Carregar um arquivo e continuar de dentro dele", level: 2 as const }, { id: 'entender-a-linguagem-por-dentro', text: "Entender a linguagem por dentro", level: 2 as const }, { id: 'medir-no-lugar-certo', text: "Medir no lugar certo", level: 2 as const }, { id: 'o-que-o-repl-nao-e', text: "O que o REPL não é", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O REPL"}
      description={"O console interativo: avaliar, inspecionar a árvore, medir tempo e carregar um arquivo na sessão."}
      href={"/docs/repl"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
