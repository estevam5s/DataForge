import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Fila de trabalho",
  description: "Tarefas com prioridade, retentativa por tarefa e relatório.",
};

const blocos: Bloco[] = [
  {"p": "Este é o código completo do exercício `174_projeto_worker.df`, que roda e verifica a si mesmo."},
  { code: `adopt Arcane.Collections as Col
adopt Arcane.Time as Time
adopt Arcane.Logging as Log
adopt Arcane.Text as Text

// ═══ MODELO ═══

enum Estado:
    Pendente
    Executando
    Concluida
    Falhou

record Tarefa:
    id: Integer
    nome: String
    prioridade: Integer
    duracao_ms: Integer

// ═══ FILA COM PRIORIDADE ═══

fila := Col.priority_queue()

tarefas := [
    Tarefa(1, "enviar email", 5, 10),
    Tarefa(2, "processar pagamento", 1, 20),
    Tarefa(3, "gerar relatorio", 8, 15),
    Tarefa(4, "backup", 9, 25),
    Tarefa(5, "alerta de seguranca", 1, 5),
    Tarefa(6, "limpar cache", 7, 10)
]

cycle t in tarefas:
    fila.push(t, t.prioridade)

out Text.box("Fila de Trabalho")
out $"tarefas na fila: {fila.size()}"
assert fila.size() is 6, "seis tarefas"

// ═══ EXECUCAO ═══

registro := Log.logger("worker", "INFO")
registro.colored(no)

historico := []
falhas := {"n": 0}

action executar(t):
    // Simula o trabalho levando o tempo declarado
    wait t.duracao_ms
    given t.nome.contains("pagamento"):
        trigger "gateway indisponivel"
    yield $"{t.nome} concluida"

out ""
out "── processando por prioridade ──"

crono := Time.stopwatch()
crono.start()

persist yes:
    t := fila.pop()
    given t is void:
        halt

    resultado := {"tarefa": t, "estado": Estado.Executando, "detalhe": ""}

    retry 2:
        saida := executar(t)
        resultado["estado"] := Estado.Concluida
        resultado["detalhe"] := saida
    handle e:
        resultado["estado"] := Estado.Falhou
        resultado["detalhe"] := e
        falhas["n"] := falhas["n"] + 1

    historico.append(resultado)
    marca := "ok " given resultado["estado"] is Estado.Concluida otherwise "ERR"
    out $"  [p{t.prioridade}] {marca} {t.nome.pad_end(22)} {resultado["detalhe"]}"

decorrido := crono.stop()

// ═══ RELATORIO ═══

out ""
out Text.box("Relatorio")

concluidas := historico >> sift h: h["estado"] is Estado.Concluida
falhadas := historico >> sift h: h["estado"] is Estado.Falhou

out $"total:      {len(historico)}"
out $"concluidas: {len(concluidas)}"
out $"falhadas:   {len(falhadas)}"
out $"tempo:      {round(decorrido * 1000, 1)} ms"

assert len(historico) is 6, "todas processadas"
assert len(falhadas) is 1, "so o pagamento falhou"
assert falhas["n"] is 1, "uma falha contabilizada"

// A ordem seguiu a prioridade, nao a de insercao
ordem := historico >> morph h: h["tarefa"].prioridade
out ""
out $"ordem de execucao (prioridade): {ordem}"
assert ordem is sorted(ordem), "menor prioridade primeiro"
assert ordem[0] is 1, "as urgentes vieram antes"

// Agrupar por estado
out ""
out "── por estado ──"
cycle nome_estado in Estado.names():
    quantos := len(historico >> sift h: h["estado"].name is nome_estado)
    given quantos bigger 0:
        out $"  {nome_estado.pad_end(12)} {"#".repeat(quantos)} ({quantos})"

// As que falharam voltam para a fila
out ""
given len(falhadas) bigger 0:
    out "── reenfileirando falhas ──"
    cycle h in falhadas:
        t := h["tarefa"]
        fila.push(t, 0)
        out $"  {t.nome} volta com prioridade maxima"
    assert fila.size() is 1, "uma tarefa reenfileirada"`, title: `174_projeto_worker.df` },
  {"h2": "Fila de prioridade"},
  {"p": "Menor número = mais urgente. A convenção pode parecer invertida, mas é a tradicional: \"prioridade 1\" é o topo da lista."},
  {"h2": "Retentativa por tarefa"},
  {"p": "O `retry` fica em volta de **uma** tarefa. Uma falha não interrompe a fila — é registrada e o laço segue. Um `monitor` em volta do laço inteiro abortaria tudo na primeira falha."},
  {"h2": "Registrar o resultado, não só o sucesso"},
  {"p": "Guardar o histórico completo é o que torna o relatório possível. Sem ele, você saberia que \"algo falhou\", mas não o quê nem por quê."},
  {"h2": "Reenfileirar"},
  {"p": "Tarefas que falharam voltam com prioridade 0. Numa fila real, isso precisaria de um contador de tentativas para não gerar laço infinito com tarefas que sempre falham."},
];

const headings = [{ id: 'fila-de-prioridade', text: "Fila de prioridade", level: 2 as const }, { id: 'retentativa-por-tarefa', text: "Retentativa por tarefa", level: 2 as const }, { id: 'registrar-o-resultado-nao-so-o-sucesso', text: "Registrar o resultado, não só o sucesso", level: 2 as const }, { id: 'reenfileirar', text: "Reenfileirar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Fila de trabalho"}
      description={"Tarefas com prioridade, retentativa por tarefa e relatório."}
      href={"/receitas/fila-de-trabalho"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
