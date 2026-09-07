import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Process",
  description: "Execução de processos externos.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Process as Proc

r := Proc.run("echo ola do processo")
out r.stdout.trim(), r.exit_code, r.ok

out Proc.capture("echo direto")
out Proc.exists("echo")`, title: `exemplo` },
  {"callout": {"tipo": "perigo", "texto": "Por padrão os comandos **não passam pelo shell** — isso previne injeção. Só use `shell := yes` quando precisar de pipes, e nunca com texto vindo do usuário."}},
  {"p": "Guia com contexto e boas práticas: [Process](/tecnicas/processos)."},
  {"h2": "Funções (15)"},
  {"table": {"head": ["Assinatura"], "rows": [["`capture(comando, shell=False, timeout=None)`"], ["`check(comando, shell=False, timeout=None)`"], ["`exists(prog)`"], ["`exit_code(comando, shell=False, timeout=None)`"], ["`is_running(processo)`"], ["`kill(processo)`"], ["`pid()`"], ["`pipeline(comandos, timeout=None)`"], ["`python()`"], ["`run(comando, shell=False, timeout=None, cwd=None, env=None, input_text=None)`"], ["`run_shell(cmd, timeout=None)`"], ["`spawn(comando, shell=False, cwd=None)`"], ["`terminate(processo)`"], ["`wait(processo, timeout=None)`"], ["`which(programa)`"]]}},
];

const headings = [{ id: 'funcoes-15', text: "Funções (15)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Process"}
      description={"Execução de processos externos."}
      href={"/biblioteca/process"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
