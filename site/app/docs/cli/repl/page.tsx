import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge repl",
  description: "Console interativo",
};

const blocos: Bloco[] = [
  {"h2": "Uso"},
  { code: `dataforge repl`, lang: 'bash' },
  {"h2": "Os comandos"},
  {"table": {"head": ["Comando", "Faz"], "rows": [["`:help`", "lista os comandos"], ["`:exit`", "sai (ou Ctrl+D)"], ["`:type <expr>`", "o tipo de uma expressão"], ["`:tokens <código>`", "o fluxo de tokens"], ["`:ast <código>`", "a árvore sintática"], ["`:check <código>`", "roda o analisador estático"], ["`:load <arquivo>`", "carrega e executa um `.df` na sessão"], ["`:save <arquivo>`", "grava o histórico da sessão"], ["`:doc <nome>`", "o que é um nome definido na sessão"], ["`:env`", "as variáveis definidas"], ["`:modules`", "os módulos Arcane"], ["`:history [n]`", "os últimos comandos"], ["`:time <código>`", "executa e mede"], ["`:reset`", "zera o interpretador"], ["`:clear`", "limpa a tela"]]}},
  {"h2": "Blocos"},
  {"p": "Uma linha terminada em `:` abre um bloco — o REPL continua lendo até você enviar uma linha em branco:"},
  { code: `forge> action dobro(n):
...        yield n * 2
...
forge> dobro(21)
42`, lang: 'text' },
  {"h2": "Histórico e autocomplete"},
  {"p": "O histórico persiste em `~/.dataforge_history` entre sessões. Tab completa nomes definidos, palavras-chave e os próprios comandos `:`."},
];

const headings = [{ id: 'uso', text: "Uso", level: 2 as const }, { id: 'os-comandos', text: "Os comandos", level: 2 as const }, { id: 'blocos', text: "Blocos", level: 2 as const }, { id: 'historico-e-autocomplete', text: "Histórico e autocomplete", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge repl"}
      description={"Console interativo"}
      href={"/docs/cli/repl"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
