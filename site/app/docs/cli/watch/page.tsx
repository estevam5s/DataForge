import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge watch",
  description: "Reexecuta a cada vez que você salva.",
};

const blocos: Bloco[] = [
  { code: `dataforge watch src/main.df    # roda o arquivo
dataforge watch --test         # roda a suíte
dataforge watch --check        # roda a análise estática`, lang: 'bash' },
  {"p": "Observa os `.df` da pasta e reexecuta quando algo muda. Ctrl+C para sair."},
  {"h2": "Para TDD"},
  { code: `dataforge watch --test`, lang: 'bash' },
  {"p": "A suíte roda a cada save. Escreva o teste que falha, veja o vermelho, implemente, veja o verde — sem trocar de janela."},
  {"h2": "Como funciona"},
  {"p": "Compara o `mtime` dos arquivos a cada meio segundo. Sem biblioteca de watch: para um punhado de arquivos isso é mais simples e mais portátil que inotify, e a diferença não se percebe."},
  {"p": "A varredura pula `forge_modules/`, `.git/` e `__pycache__` — mudança em dependência baixada não deveria disparar sua suíte."},
];

const headings = [{ id: 'para-tdd', text: "Para TDD", level: 2 as const }, { id: 'como-funciona', text: "Como funciona", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge watch"}
      description={"Reexecuta a cada vez que você salva."}
      href={"/docs/cli/watch"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
