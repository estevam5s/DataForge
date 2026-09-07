import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "CLI",
  description: "Os treze comandos do dataforge e suas opções.",
};

const blocos: Bloco[] = [
  {"h2": "Os comandos"},
  {"table": {"head": ["Comando", "O que faz"], "rows": [["[`run`](/docs/cli/run)", "executa um programa"], ["[`check`](/docs/cli/check)", "análise estática: nomes, aridade, tipos"], ["[`test`](/docs/cli/test)", "descobre e roda os testes"], ["[`fmt`](/docs/cli/fmt)", "formata o código"], ["[`lint`](/docs/cli/lint)", "aponta problemas de estilo"], ["[`doc`](/docs/cli/doc)", "gera documentação Markdown"], ["[`init`](/docs/cli/init)", "cria um projeto novo"], ["[`repl`](/docs/cli/repl)", "console interativo"], ["`info`", "mostra o manifesto do projeto"], ["`new`", "cria a partir de um template"], ["`tokens`", "mostra o fluxo de tokens (lexer)"], ["`ast`", "mostra a árvore sintática (parser)"], ["`version`", "mostra a versão"]]}},
  {"p": "`df` é um atalho para `dataforge` — os dois são o mesmo programa."},
  {"h2": "As flags"},
  {"table": {"head": ["Flag", "Efeito"], "rows": [["`--time`", "mostra o tempo de execução"], ["`--debug`", "imprime tokens, AST e o traceback completo"], ["`--no-color`", "desliga as cores (útil em CI e logs)"], ["`--check`", "`fmt`: só verifica, não reescreve"], ["`--strict`", "`check`/`lint`: trata avisos como erros"], ["`--verbose`, `-v`", "`test`: mostra cada caso"], ["`--filter=<texto>`", "`test`: só os casos cujo nome contém o texto"], ["`--fail-fast`", "`test`: para na primeira falha"], ["`--out=<arquivo>`", "`doc`: escreve num arquivo"], ["`--syntax-only`", "`check`: pula a análise semântica"]]}},
  {"h2": "O ciclo de trabalho"},
  { code: `dataforge init meu-app        # começar
cd meu-app

dataforge check src/          # nomes, tipos, aridade
dataforge lint src/           # estilo e higiene
dataforge fmt src/            # formatar
dataforge test tests/ -v      # testes
dataforge doc src/ --out=doc/API.md
dataforge run                 # executar`, lang: 'bash' },
  {"h2": "Em integração contínua"},
  { code: `dataforge fmt . --check && dataforge check . && dataforge test`, lang: 'bash' },
  {"p": "Cada comando sai com código diferente de zero em caso de falha, então o `&&` interrompe na primeira etapa que quebrar."},
  {"h2": "Depurar"},
  { code: `dataforge tokens arquivo.df    # o que o lexer viu
dataforge ast arquivo.df       # o que o parser montou
dataforge run arquivo.df --debug`, lang: 'bash' },
  {"p": "Úteis quando o programa não faz o que você espera e a suspeita é de que o código está sendo lido de outro jeito — a ambiguidade do `//` é o caso clássico."},
];

const headings = [{ id: 'os-comandos', text: "Os comandos", level: 2 as const }, { id: 'as-flags', text: "As flags", level: 2 as const }, { id: 'o-ciclo-de-trabalho', text: "O ciclo de trabalho", level: 2 as const }, { id: 'em-integracao-continua', text: "Em integração contínua", level: 2 as const }, { id: 'depurar', text: "Depurar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"CLI"}
      description={"Os treze comandos do dataforge e suas opções."}
      href={"/docs/cli"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
