import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Pipelines",
  description: "O operador >> com sift, morph e distill — transformação de dados como sintaxe.",
};

const blocos: Bloco[] = [
  {"h2": "O operador >>"},
  {"p": "Pipelines não são uma biblioteca: `>>`, `sift`, `morph` e `distill` fazem parte da gramática da linguagem."},
  { code: `nums := [1, 2, 3, 4, 5, 6]

out nums >> sift n: n % 2 is 0        # [2, 4, 6]      — filtra
out nums >> morph n: n * n            # [1, 4, ...]    — transforma
out nums >> distill acc, v: acc + v 0 # 21             — reduz` },
  {"h2": "sift — filtrar"},
  { code: `pessoas := [
    {"nome": "Ana", "idade": 30},
    {"nome": "Bruno", "idade": 17},
    {"nome": "Carla", "idade": 45}
]

adultos := pessoas >> sift p: p["idade"] bigger_eq 18
out adultos >> morph p: p["nome"]` },
  { code: `[Ana, Carla]`, lang: 'text', title: `saída` },
  {"h2": "morph — transformar"},
  { code: `precos := [100, 200, 300]
out precos >> morph p: round(p * 1.15, 2)

nomes := ["ana", "bruno"]
out nomes >> morph n: n.capitalize()` },
  {"h2": "distill — reduzir"},
  {"p": "A forma é `distill acumulador, valor: expressão valor_inicial`:"},
  { code: `nums := [1, 2, 3, 4, 5]

out nums >> distill acc, v: acc + v 0      # 15  — soma
out nums >> distill acc, v: acc * v 1      # 120 — produto

palavras := ["Data", "Forge"]
out palavras >> distill acc, v: acc + v ""  # DataForge` },
  {"p": "Sem valor inicial, `distill` usa o primeiro elemento como acumulador."},
  {"h2": "Encadeando"},
  { code: `vendas := [120, 45, 300, 80, 500, 15, 250]

total := vendas
    >> sift v: v bigger_eq 100
    >> morph v: v * 1.1
    >> distill acc, v: acc + v 0

out $"total das vendas grandes com 10%: {round(total, 2)}"` },
  {"p": "Uma linha que **começa** com `>>` continua a expressão anterior. Isso permite quebrar pipelines longos sem ruído."},
  {"h2": "Com ações nomeadas"},
  {"p": "Em vez da lambda inline, você pode passar o nome de uma ação:"},
  { code: `action eh_primo(n):
    given n smaller 2:
        yield no
    i := 2
    persist i * i smaller_eq n:
        given n % i is 0:
            yield no
        i += 1
    yield yes

action ao_quadrado(n):
    yield n * n

nums := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
out nums >> sift eh_primo                       # [2, 3, 5, 7, 11]
out nums >> sift eh_primo >> morph ao_quadrado  # [4, 9, 25, 49, 121]` },
  {"p": "A ação nomeada é preferível quando a lógica tem mais de uma linha, ou quando ela é reutilizada — e ainda pode ser testada isoladamente."},
  {"h2": "Pipeline, compreensão ou laço?"},
  {"p": "As três formas resolvem o mesmo problema. A escolha é de legibilidade:"},
  { code: `# pipeline — vários estágios encadeados
nums >> sift n: n % 2 is 1 >> morph n: n * 2

# compreensão — um filtro e uma transformação
[n * 2 cycle n in nums given n % 2 is 1]

# métodos — quando já se tem a lista na mão
nums.filter(lambda n: n % 2 is 1).map(lambda n: n * 2)` },
  {"table": {"head": ["Situação", "Prefira"], "rows": [["um filtro e uma transformação", "[compreensão](/docs/fundamentos/compreensoes)"], ["três ou mais estágios", "pipeline"], ["termina com uma redução", "pipeline (`distill`)"], ["duas fontes combinadas", "compreensão"], ["lógica com vários passos ou efeitos", "laço `cycle`"]]}},
  {"h2": "Um relatório completo"},
  { code: `vendas := [
    {"vendedor": "Ana", "valor": 1200},
    {"vendedor": "Bruno", "valor": 800},
    {"vendedor": "Ana", "valor": 300},
    {"vendedor": "Carla", "valor": 2000}
]

valores := vendas >> morph v: v["valor"]

out $"faturamento:  {sum(valores)}"
out $"ticket medio: {round(mean(valores), 2)}"
out $"acima de 1000: {vendas >> sift v: v["valor"] bigger 1000 >> morph v: v["vendedor"]}"` },
  { code: `faturamento:  4300
ticket medio: 1075.0
acima de 1000: [Ana, Carla]`, lang: 'text', title: `saída` },
  {"h2": "Com streams"},
  {"p": "Pipelines operam sobre listas em memória. Para fonte infinita ou arquivo grande, use [generators](/docs/fundamentos/generators) — que avaliam sob demanda e depois entregam a lista ao pipeline:"},
  { code: `stream action naturais():
    n := 1
    persist yes:
        emit n
        n += 1

primeiros := naturais().take(20)
out primeiros >> sift n: n % 3 is 0` },
];

const headings = [{ id: 'o-operador', text: "O operador >>", level: 2 as const }, { id: 'sift--filtrar', text: "sift — filtrar", level: 2 as const }, { id: 'morph--transformar', text: "morph — transformar", level: 2 as const }, { id: 'distill--reduzir', text: "distill — reduzir", level: 2 as const }, { id: 'encadeando', text: "Encadeando", level: 2 as const }, { id: 'com-acoes-nomeadas', text: "Com ações nomeadas", level: 2 as const }, { id: 'pipeline-compreensao-ou-laco', text: "Pipeline, compreensão ou laço?", level: 2 as const }, { id: 'um-relatorio-completo', text: "Um relatório completo", level: 2 as const }, { id: 'com-streams', text: "Com streams", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Pipelines"}
      description={"O operador >> com sift, morph e distill — transformação de dados como sintaxe."}
      href={"/docs/pipelines"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
