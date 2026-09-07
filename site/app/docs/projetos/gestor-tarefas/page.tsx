import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gestor de tarefas",
  description: "CLI de tarefas com prazos, prioridade e persistência em JSON.",
};

const blocos: Bloco[] = [
  { code: `dataforge install
dataforge run src/main.df -- adicionar "Comprar pão" --prioridade 3 --prazo 2026-09-15
dataforge run src/main.df -- listar --pendentes
dataforge run src/main.df -- concluir 1
dataforge run src/main.df -- resumo`, lang: 'bash' },
  { code: `┌───┬───┬─────────────────────────┬────────┬───────────────────────┐
│   │ # │ Tarefa                  │ Prior. │ Prazo                 │
├───┼───┼─────────────────────────┼────────┼───────────────────────┤
│   │ 1 │ Escrever a documentação │ alta   │ 2026-09-15            │
│ ✓ │ 2 │ Revisar os testes       │ media  │ —                     │
│   │ 3 │ Comprar café            │ baixa  │ 2026-09-01 (atrasada) │
└───┴───┴─────────────────────────┴────────┴───────────────────────┘`, lang: 'bash' },
  {"h2": "Estrutura"},
  {"table": {"head": ["Arquivo", "Responsabilidade"], "rows": [["`src/tarefa.df`", "o modelo — um `record`"], ["`src/repositorio.df`", "persistência, isolada atrás de uma interface"], ["`src/main.df`", "CLI e apresentação"]]}},
  {"h2": "O modelo"},
  { code: `record Tarefa:
    id: Integer
    titulo: String
    prioridade: Integer
    prazo: String
    feita: Boolean

    action esta_atrasada():
        given self.feita or self.prazo is "":
            yield no
        yield D.dias_entre(D.hoje(), D.de_iso(self.prazo)) smaller 0

    action dias_restantes():
        given self.prazo is "":
            yield void
        yield D.dias_entre(D.hoje(), D.de_iso(self.prazo))

    action rotulo_prioridade():
        given self.prioridade bigger_eq 3:
            yield "alta"
        given self.prioridade is 2:
            yield "media"
        yield "baixa"`, lang: 'df' },
  {"p": "Tarefa é `record` porque o que muda é a lista que as contém. Concluir uma cria uma cópia com `with`, e o original fica intacto — impossível alterar por engano em outro ponto do código."},
  {"h2": "Configuração em camadas"},
  { code: `action carregar_config():
    cfg := C.novo()
    cfg := C.padroes(cfg, {
        "arquivo": "tarefas.json",
        "estilo": "simples",
        "cor": yes
    })
    cfg := C.do_arquivo(cfg, "tarefas.config.json")
    cfg := C.do_ambiente(cfg, "TAREFAS_")
    yield cfg`, lang: 'df' },
  {"p": "Padrão, arquivo, ambiente, argumentos — nessa ordem de precedência. `cofre` guarda de onde veio cada valor, o que responde à pergunta que se faz às três da manhã."},
  {"h2": "Arquivo corrompido não derruba"},
  {"p": "Um JSON quebrado avisa e começa vazio, sem apagar o original. Derrubar o programa por causa de um arquivo que alguém editou à mão seria pior que seguir — e há teste para isso."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-modelo', text: "O modelo", level: 2 as const }, { id: 'configuracao-em-camadas', text: "Configuração em camadas", level: 2 as const }, { id: 'arquivo-corrompido-nao-derruba', text: "Arquivo corrompido não derruba", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gestor de tarefas"}
      description={"CLI de tarefas com prazos, prioridade e persistência em JSON."}
      href={"/docs/projetos/gestor-tarefas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
