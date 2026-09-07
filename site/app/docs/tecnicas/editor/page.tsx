import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Editor e cores",
  description: "Realce de sintaxe no VS Code, instalado junto com a linguagem.",
};

const blocos: Bloco[] = [
  {"p": "O instalador já cuida disso. Quando você instala o DataForge, a extensão do editor vai junto e é aplicada em todos os editores encontrados — VS Code, Insiders, Cursor, VSCodium e Windsurf."},
  { code: `curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh
# …
# ✓ coloração de sintaxe instalada no editor` },
  {"p": "Reinicie o editor, abra um `.df`, e as palavras reservadas já estão coloridas."},
  {"h2": "Instalar ou reinstalar à mão"},
  { code: `dataforge editor           # instala em todos os editores achados
dataforge editor status    # mostra onde está instalada
dataforge editor remove    # desinstala` },
  {"p": "Use `dataforge editor` depois de atualizar a linguagem, ou depois de instalar um editor novo. Para pular a etapa na instalação, defina `DATAFORGE_SEM_EDITOR=1`."},
  {"h2": "O que você ganha"},
  {"table": {"head": ["", "O quê"], "rows": [
    ["cores", "as 98 palavras reservadas, em 14 grupos — condicional, laço, tipo, modificador, Kiln, operador"],
    ["snippets", "23 atalhos: `action`, `blueprint`, `match`, `server`, `route`, `crud`, `xlsx`…"],
    ["indentação", "4 espaços, `insertSpaces` forçado — tab é `SyncError` na linguagem"],
    ["dobra", "blocos de `action`, `blueprint`, `server`, `route` e afins"],
    ["ícone", "arquivos `.df` com o ícone do DataForge"],
    ["interpolação", "`$\"{expr}\"` colorido por dentro, como código"],
    ["`//` vs divisão", "a mesma regra do lexer: `x // 2` é divisão, `x // nota` é comentário"]
  ]}},
  {"h2": "Alguns snippets"},
  {"table": {"head": ["Digite", "Vira"], "rows": [
    ["`action`", "uma ação com corpo"],
    ["`blueprint`", "uma classe com método"],
    ["`match`", "`match` com um `point` e o `default`"],
    ["`pipe`", "um pipeline `sift`/`morph`"],
    ["`server`", "uma aplicação Kiln completa, com `ignite`"],
    ["`crud`", "as cinco rotas RESTful de um recurso"],
    ["`routeparam`", "rota com parâmetro e o 404"],
    ["`xlsx`", "gravar uma planilha"],
    ["`istr`", "uma string interpolada"]
  ]}},
  {"h2": "A gramática não pode ficar atrasada"},
  {"p": "A gramática TextMate é **gerada** a partir de `dataforge/tokens.py`, e há um teste que falha se o arquivo versionado não for exatamente o que o gerador produz. Se você acrescenta uma palavra à linguagem e esquece da gramática, a suíte avisa — em vez de a palavra simplesmente ficar cinza."},
  { code: `python3 tools/gerar_gramatica.py` },
  {"p": "A versão anterior da extensão foi escrita à mão, e por isso não conhecia `record` nem `enum`: exatamente o problema que o gerador resolve."},
  {"h2": "O que ainda não existe"},
  {"p": "Não há **LSP**: sem autocompletar sensível a contexto, sem \"ir para a definição\", sem erros sublinhados enquanto você digita. Para ver erros, rode `dataforge check` — ele dá a linha, a coluna, a explicação e a sugestão. Um servidor de linguagem está no [roadmap](/docs/roadmap)."},
  {"h2": "Outros editores"},
  {"p": "A gramática é TextMate padrão, em `editor/vscode/syntaxes/dataforge.tmLanguage.json`. Sublime Text e editores compatíveis leem o mesmo arquivo. Para Vim, Emacs ou Zed, ela serve de referência: a lista de palavras por grupo de cor está toda ali."},
];

const headings = [{ id: 'instalar-ou-reinstalar-a-mao', text: "Instalar ou reinstalar à mão", level: 2 as const }, { id: 'o-que-voce-ganha', text: "O que você ganha", level: 2 as const }, { id: 'alguns-snippets', text: "Alguns snippets", level: 2 as const }, { id: 'a-gramatica-nao-pode-ficar-atrasada', text: "A gramática não pode ficar atrasada", level: 2 as const }, { id: 'o-que-ainda-nao-existe', text: "O que ainda não existe", level: 2 as const }, { id: 'outros-editores', text: "Outros editores", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Editor e cores"}
      description={"Realce de sintaxe no VS Code, instalado junto com a linguagem."}
      href={"/docs/tecnicas/editor"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
