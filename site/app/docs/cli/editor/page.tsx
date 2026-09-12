import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge editor",
  description: "Instala a coloração de sintaxe no VS Code e derivados.",
};

const blocos: Bloco[] = [
  { code: `dataforge editor           # instala em todos os editores achados
dataforge editor status    # mostra onde está instalada
dataforge editor remove    # desinstala de todos`, lang: 'bash' },
  {"p": "O instalador já roda `dataforge editor` no fim. Use o comando à mão depois de atualizar a linguagem, ou depois de instalar um editor novo."},
  {"h2": "Onde ele procura"},
  {"table": {"head": ["Editor", "Pasta"], "rows": [
    ["VS Code", "`~/.vscode/extensions`"],
    ["VS Code Insiders", "`~/.vscode-insiders/extensions`"],
    ["VSCodium", "`~/.vscode-oss/extensions`"],
    ["Cursor", "`~/.cursor/extensions`"],
    ["Windsurf", "`~/.windsurf/extensions`"],
    ["VS Code (WSL)", "`~/.vscode-server/extensions`"]
  ]}},
  {"p": "A extensão é copiada para cada pasta que existir. Isso é o que o `code --install-extension` faz por baixo — e funciona mesmo quando o comando `code` não está no `PATH`, que é o caso da maioria das instalações no macOS."},
  {"h2": "A saída"},
  { code: `  Instalando a coloracao do DataForge

  ✓ VS Code              /Users/você/.vscode/extensions/dataforge…
  ✓ VS Code Insiders     /Users/você/.vscode-insiders/extensions/…

  Pronto. Reinicie o editor e abra um arquivo .df.`, lang: 'bash' },
  {"p": "Sem nenhum editor instalado, o comando lista onde procurou e sai — sem erro, porque não ter VS Code não é um problema a resolver."},
  {"h2": "Versões antigas"},
  {"p": "Uma versão anterior da extensão é removida antes de a nova ser copiada. Se as duas ficassem, o editor escolheria uma delas sem avisar qual."},
  {"h2": "Pular na instalação"},
  { code: `DATAFORGE_SEM_EDITOR=1 curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh`, lang: 'bash' },
  {"h2": "Veja também"},
  {"p": "[Editor e cores](/docs/editor) — o que a extensão traz e como a gramática é gerada."},
];

const headings = [{ id: 'onde-ele-procura', text: "Onde ele procura", level: 2 as const }, { id: 'a-saida', text: "A saída", level: 2 as const }, { id: 'versoes-antigas', text: "Versões antigas", level: 2 as const }, { id: 'pular-na-instalacao', text: "Pular na instalação", level: 2 as const }, { id: 'veja-tambem', text: "Veja também", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"dataforge editor"}
      description={"Instala a coloração de sintaxe no VS Code e derivados."}
      href={"/docs/cli/editor"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
