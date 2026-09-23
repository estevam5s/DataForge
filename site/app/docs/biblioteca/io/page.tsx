// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/io.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.IO",
  description: "Arquivos, diretórios, JSON, CSV e shell.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.IO as IO

IO.write("_temp.txt", "linha 1\\nlinha 2")
out IO.read("_temp.txt").lines().length()
out IO.size("_temp.txt"), IO.ext("_temp.txt")
IO.delete("_temp.txt")`, title: `exemplo` },
  {"p": "Guia com contexto e boas práticas: [IO](/docs/tecnicas/arquivos)."},
  {"h2": "Funções (35)"},
  {"table": {"head": ["Assinatura"], "rows": [["`abs(path)`"], ["`append(path, content)`"], ["`append_bytes(path, content)`"], ["`basename(path)`"], ["`copy(src, dst)`"], ["`copy_tree(origem, destino)`"], ["`cwd()`"], ["`delete(path)`"], ["`dirname(path)`"], ["`exists(path)`"], ["`ext(path)`"], ["`file_exists(path)`"], ["`is_dir(path)`"], ["`is_file(path)`"], ["`join(*parts)`"], ["`list_dir(path='.')`"], ["`listdir(path='.')`"], ["`mkdir(path)`"], ["`open(path, mode='r')`"], ["`path(path)`"], ["`read(path)`"], ["`read_bytes(path)`"], ["`read_csv(path, cabecalho=False)`"], ["`read_file(path)`"], ["`read_json(path)`"], ["`remove_tree(path)`"], ["`rename(old, new)`"], ["`rmdir(path)`"], ["`shell(command)`"], ["`size(path)`"], ["`write(path, content)`"], ["`write_bytes(path, content)`"], ["`write_csv(path, data)`"], ["`write_file(path, content)`"], ["`write_json(path, data, indent=2)`"]]}},
];

const headings = [{ id: 'funcoes-35', text: "Funções (35)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.IO"}
      description={"Arquivos, diretórios, JSON, CSV e shell."}
      href={"/docs/biblioteca/io"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
