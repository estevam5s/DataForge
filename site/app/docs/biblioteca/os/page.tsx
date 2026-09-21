// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/os.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.OS",
  description: "Sistema operacional, ambiente, disco e processo atual.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.OS as OS

out $"{OS.name()} {OS.arch()} com {OS.cpu_count()} CPUs"
out $"disco livre: {OS.disk_usage().free_gb} GB"
out $"usuario: {OS.user()}"
out OS.get_env("PATH_INEXISTENTE", "(padrao)")`, title: `exemplo` },
  {"h2": "Funções (43)"},
  {"table": {"head": ["Assinatura"], "rows": [["`arch()`"], ["`argv()`"], ["`argv_completo()`"], ["`beside(*partes)`"], ["`chdir(caminho)`"], ["`cpu_count()`"], ["`cwd()`"], ["`disk_usage(caminho='.')`"], ["`env()`"], ["`env_names()`"], ["`executable()`"], ["`exit(codigo=0)`"], ["`get_env(nome, padrao=None)`"], ["`has_env(nome)`"], ["`home()`"], ["`hostname()`"], ["`info()`"], ["`is_linux()`"], ["`is_mac()`"], ["`is_posix()`"], ["`is_tty()`"], ["`is_windows()`"], ["`line_separator()`"], ["`machine()`"], ["`memory_info()`"], ["`name()`"], ["`parent_pid()`"], ["`path_separator()`"], ["`pid()`"], ["`platform()`"], ["`processor()`"], ["`python_version()`"], ["`release()`"], ["`script()`"], ["`script_dir()`"], ["`separator()`"], ["`set_env(nome, valor)`"], ["`temp_dir()`"], ["`terminal_size()`"], ["`unset_env(nome)`"], ["`user()`"], ["`version()`"], ["`which(prog)`"]]}},
];

const headings = [{ id: 'funcoes-43', text: "Funções (43)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.OS"}
      description={"Sistema operacional, ambiente, disco e processo atual."}
      href={"/docs/biblioteca/os"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
