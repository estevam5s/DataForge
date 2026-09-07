import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Processos",
  description: "Executar comandos externos com segurança.",
};

const blocos: Bloco[] = [
  {"h2": "Segurança primeiro"},
  { code: `adopt Arcane.Process as Proc

Proc.run("echo ola")                    # sem shell
Proc.run(["echo", "texto com espacos"]) # lista: mais seguro ainda
Proc.run("...", shell := yes)           # shell, conscientemente` },
  {"callout": {"tipo": "perigo", "texto": "Sem shell, não há injeção: `rm -rf /` dentro de uma variável vira um argumento literal, não um comando. Só ligue `shell := yes` quando precisar de pipes ou expansão de `*` — e **nunca** com texto vindo do usuário."}},
  {"h2": "O resultado"},
  {"p": "`run` sempre devolve um `ProcessResult`, mesmo quando falha:"},
  {"table": {"head": ["Campo", "Contém"], "rows": [["`stdout`", "a saída padrão"], ["`stderr`", "a saída de erro"], ["`exit_code`", "0 = sucesso"], ["`ok`", "`yes` se o código foi 0"], ["`failed`", "o oposto de `ok`"], ["`lines`", "`stdout` já separado em linhas"]]}},
  { code: `r := Proc.run("comando_inexistente")
given r.failed:
    out $"nao rolou: {r.stderr}"     # código 127` },
  {"p": "Um comando inexistente devolve 127 em vez de derrubar o programa. Falha de processo externo é um resultado esperado, não uma exceção."},
  {"h2": "Atalhos"},
  { code: `Proc.capture("echo x")     # só o stdout, sem a quebra final
Proc.check("test -f x")    # só yes/no
Proc.exit_code("cmd")      # só o número
Proc.exists("git")         # o programa está instalado?` },
  {"h2": "Entrada e encadeamento"},
  { code: `Proc.run("cat", input_text := "vindo da entrada")

Proc.pipeline(["printf 'c\\na\\nb'", "sort"])` },
  {"p": "A cadeia **para no primeiro que falhar** — devolvendo o resultado daquele, não um sucesso enganoso."},
  {"h2": "Tempo limite"},
  { code: `Proc.run("sleep 5", timeout := 1)     # ok = no, timed_out = yes` },
  {"p": "Sempre ponha timeout em comando que fala com a rede. Sem ele, um servidor que não responde trava seu programa indefinidamente."},
  {"h2": "Segundo plano"},
  { code: `p := Proc.spawn("servidor --porta 8080")
Proc.is_running(p)
Proc.terminate(p)      # pede para encerrar (SIGTERM)
Proc.kill(p)           # força (SIGKILL)
r := Proc.wait(p)      # espera e colhe o resultado` },
];

const headings = [{ id: 'seguranca-primeiro', text: "Segurança primeiro", level: 2 as const }, { id: 'o-resultado', text: "O resultado", level: 2 as const }, { id: 'atalhos', text: "Atalhos", level: 2 as const }, { id: 'entrada-e-encadeamento', text: "Entrada e encadeamento", level: 2 as const }, { id: 'tempo-limite', text: "Tempo limite", level: 2 as const }, { id: 'segundo-plano', text: "Segundo plano", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Processos"}
      description={"Executar comandos externos com segurança."}
      href={"/docs/tecnicas/processos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
