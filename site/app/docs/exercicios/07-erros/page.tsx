import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "07 · Tratamento de erros",
  description: "10 exercícios: `monitor`, `handle` tipado, `guard`, `retry` e `propagate`.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 07`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["077", "**monitor / handle**", "capture uma divisao por zero sem derrubar o programa."], ["078", "**ensure (finally)**", "garanta que a limpeza rode com ou sem erro."], ["079", "**trigger (lancar erro)**", "valide a entrada de uma acao lancando erros descritivos."], ["080", "**handle tipado**", "capture apenas um tipo de erro e deixe os outros passarem."], ["081", "**monitor sem handle propaga**", "comprove que um monitor com apenas ensure nao engole o erro."], ["082", "**guard e validate**", "compare as duas formas de pre-condicao."], ["083", "**retry**", "repita uma operacao instavel ate ter sucesso."], ["084", "**propagate**", "registre o erro e repasse para o chamador."], ["085", "**assert**", "use assert como verificacao interna e capture a falha."], ["086", "**Pilha de erros e recuperacao**", "converta valores com fallback em varias camadas."]]}},
  {"h2": "077 · monitor / handle"},
  {"p": "Capture uma divisao por zero sem derrubar o programa."},
  { code: `// Exercicio 077 — monitor / handle
// Enunciado: capture uma divisao por zero sem derrubar o programa.

resultado := void
monitor:
    resultado := 10 / 0
handle e:
    out "capturado:", e
    resultado := -1

out "continuou, resultado =", resultado
assert resultado is -1, "o handle rodou"
`, title: `077_monitor_handle.df` },
  {"h2": "078 · ensure (finally)"},
  {"p": "Garanta que a limpeza rode com ou sem erro."},
  { code: `// Exercicio 078 — ensure (finally)
// Enunciado: garanta que a limpeza rode com ou sem erro.

log := []

action com_falha():
    monitor:
        log.append("inicio")
        trigger "falhou"
    handle e:
        log.append("tratou")
    ensure:
        log.append("limpou")

action sem_falha():
    monitor:
        log.append("ok")
    handle e:
        log.append("nao deveria")
    ensure:
        log.append("limpou2")

com_falha()
sem_falha()
out log

assert log is ["inicio", "tratou", "limpou", "ok", "limpou2"], "ensure sempre roda"
`, title: `078_ensure.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 8 exercícios deste módulo estão em `exercicios/07-erros/`. Rode-os com o comando acima."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '077--monitor--handle', text: "077 · monitor / handle", level: 2 as const }, { id: '078--ensure-finally', text: "078 · ensure (finally)", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"07 · Tratamento de erros"}
      description={"10 exercícios: `monitor`, `handle` tipado, `guard`, `retry` e `propagate`."}
      href={"/docs/exercicios/07-erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
