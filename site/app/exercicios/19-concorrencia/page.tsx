import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "19 · Concorrência",
  description: "6 exercícios: `async`/`await`, threads, canais, `defer` e `retry`.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 19`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["169", "**Acoes assincronas**", "declare acoes async e aguarde o resultado com await."], ["170", "**Threads e paralelismo**", "execute trabalho em segundo plano."], ["171", "**Canais entre threads**", "passe valores entre threads com seguranca."], ["172", "**Liberacao garantida**", "garanta limpeza mesmo quando algo falha."], ["173", "**Erros e retentativas**", "trate falhas temporarias com retry e propagacao controlada."], ["174", "**Projeto: fila de trabalho**", "monte um sistema de tarefas com fila, trabalhadores e relatorio."]]}},
  {"h2": "169 · Acoes assincronas"},
  {"p": "Declare acoes async e aguarde o resultado com await."},
  { code: `// Exercicio 169 — Acoes assincronas
// Enunciado: declare acoes async e aguarde o resultado com await.

// Uma acao async representa trabalho que pode demorar
async action buscar_usuario(id):
    yield {"id": id, "nome": $"Usuario {id}", "ativo": yes}

async action buscar_pedidos(id_usuario):
    yield [
        {"id": 100, "usuario": id_usuario, "total": 250.0},
        {"id": 101, "usuario": id_usuario, "total": 80.0}
    ]

// await resolve o resultado
usuario := await buscar_usuario(7)
pedidos := await buscar_pedidos(7)

out $"usuario: {usuario["nome"]}"
out $"pedidos: {len(pedidos)}"

assert usuario["id"] is 7, "id do usuario"
assert len(pedidos) is 2, "dois pedidos"

// Compor chamadas assincronas
async action perfil_completo(id):
    u := await buscar_usuario(id)
    p := await buscar_pedidos(id)
    total := p >> morph x: x["total"] >> distill acc, v: acc + v 0
    yield {
        "nome": u["nome"],
        "pedidos": len(p),
        "total_gasto": total
    }

perfil := await perfil_completo(7)
out ""
out perfil
assert perfil["total_gasto"] is 330.0, "250 + 80"

// Erros atravessam o await normalmente
async action pode_falhar(deve):
    given deve:
        trigger "a busca falhou"
    yield "ok"

out ""
monitor:
    await pode_falhar(yes)
handle e:
    out $"erro capturado: {e.message}"

assert await pode_falhar(no) is "ok", "caminho feliz"

// Varias chamadas em sequencia
ids := [1, 2, 3]
nomes := []
cycle id in ids:
    u := await buscar_usuario(id)
    nomes.append(u["nome"])

out ""
out nomes
assert len(nomes) is 3, "tres usuarios"
`, title: `169_async_await.df` },
  {"h2": "170 · Threads e paralelismo"},
  {"p": "Execute trabalho em segundo plano."},
  { code: `// Exercicio 170 — Threads e paralelismo
// Enunciado: execute trabalho em segundo plano.

adopt Arcane.Time as Time

// Um bloco thread roda em segundo plano
resultados := []

thread:
    cycle i from 1 to 3:
        resultados.append($"A{i}")

thread:
    cycle i from 1 to 3:
        resultados.append($"B{i}")

// Espera as threads terminarem
wait 200

out $"itens produzidos: {len(resultados)}"
assert len(resultados) is 6, "as duas threads produziram"

// parallel roda cada instrucao em uma thread
adopt Arcane.Math as Math

saidas := []
parallel:
    saidas.append($"fatorial: {Math.factorial(12)}")
    saidas.append($"fibonacci: {Math.fibonacci(25)}")
    saidas.append($"primo: {Math.is_prime(9973)}")

wait 300
out ""
cycle s in sorted(saidas):
    out $"  {s}"
assert len(saidas) is 3, "tres tarefas"

// Medindo: trabalho concorrente
action trabalho(n):
    total := 0
    cycle i from 1 to n:
        total += i * i
    yield total

crono := Time.stopwatch()
crono.start()

sequencial := []
cycle n in [50000, 50000, 50000]:
    sequencial.append(trabalho(n))

tempo_seq := crono.stop()
out ""
out $"sequencial: {round(tempo_seq * 1000, 1)} ms"
assert len(sequencial) is 3, "tres resultados"

// Aviso importante: sem sincronizacao, atualizacoes se perdem
contador := {"valor": 0}

thread:
    cycle _ in range(0, 1000):
        contador["valor"] := contador["valor"] + 1

thread:
    cycle _ in range(0, 1000):
        contador["valor"] := contador["valor"] + 1

wait 400
out ""
out $"contador (esperado 2000): {contador["valor"]}"
out "se o numero veio menor, voce acabou de ver uma condicao de corrida"
`, title: `170_threads.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 4 exercícios deste módulo estão em `exercicios/19-concorrencia/`. Cada um tem um `.md` ao lado com a explicação completa."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '169--acoes-assincronas', text: "169 · Acoes assincronas", level: 2 as const }, { id: '170--threads-e-paralelismo', text: "170 · Threads e paralelismo", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"19 · Concorrência"}
      description={"6 exercícios: `async`/`await`, threads, canais, `defer` e `retry`."}
      href={"/exercicios/19-concorrencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
