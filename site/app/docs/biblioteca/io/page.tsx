import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.IO",
  description: "Arquivos, diretórios, JSON e CSV.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.IO as IO

IO.write("_temp.txt", "linha 1\\nlinha 2")
out IO.read("_temp.txt").lines().length()
out IO.size("_temp.txt"), IO.ext("_temp.txt")
IO.delete("_temp.txt")`, title: `exemplo` },
  {"p": "Guia com contexto e boas práticas: [IO](/docs/tecnicas/arquivos)."},
  {"h2": "Funções (27)"},
  {"table": {"head": ["Assinatura"], "rows": [["`abs(path)`"], ["`append(path, content)`"], ["`basename(path)`"], ["`copy(src, dst)`"], ["`cwd()`"], ["`delete(path)`"], ["`dirname(path)`"], ["`exists(path)`"], ["`ext(path)`"], ["`file_exists(path)`"], ["`join(*parts)`"], ["`list_dir(path='.')`"], ["`listdir(path='.')`"], ["`mkdir(path)`"], ["`open(path, mode='r')`"], ["`path(path)`"], ["`read(path)`"], ["`read_csv(path)`"], ["`read_file(path)`"], ["`read_json(path)`"], ["`rename(old, new)`"], ["`shell(command)`"], ["`size(path)`"], ["`write(path, content)`"], ["`write_csv(path, data)`"], ["`write_file(path, content)`"], ["`write_json(path, data, indent=2)`"]]}},
];

const headings = [{ id: 'funcoes-27', text: "Funções (27)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.IO"}
      description={"Arquivos, diretórios, JSON e CSV."}
      href={"/docs/biblioteca/io"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
