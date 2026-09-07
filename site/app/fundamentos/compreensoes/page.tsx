import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Compreensões",
  description: "Construir listas e vaults numa expressão, transformando e filtrando.",
};

const blocos: Bloco[] = [
  {"h2": "A forma"},
  { code: `[ <expressão>  cycle <nome> in <fonte>  [given <condição>] ]
{ <chave>: <valor>  cycle <nome> in <fonte>  [given <condição>] }`, lang: 'text' },
  {"p": "Lê-se: *\"a expressão, para cada nome na fonte, dado que a condição vale\"*."},
  {"callout": {"tipo": "nota", "texto": "A sintaxe **reutiliza `cycle` e `given`** — as mesmas palavras dos laços e condicionais. Não há vocabulário novo para memorizar."}},
  {"h2": "Listas"},
  { code: `nums := [1, 2, 3, 4, 5, 6]

out [n * n cycle n in nums]                     # transforma
out [n cycle n in nums given n % 2 is 0]        # filtra
out [n * 2 cycle n in nums given n % 2 is 1]    # os dois` },
  { code: `[1, 4, 9, 16, 25, 36]
[2, 4, 6]
[2, 6, 10]`, lang: 'text', title: `saída` },
  {"h2": "Sobre outras fontes"},
  { code: `out [c.upper() cycle c in "dataforge" given c isnt "a"]     # sobre texto
out [k cycle k in {"a": 1, "b": 2}]                        # sobre as chaves
out [x * 10 cycle x in contar(4)]                          # sobre um stream` },
  {"h2": "Vaults"},
  { code: `out {n: n * n cycle n in [1, 2, 3]}       # {1: 1, 2: 4, 3: 9}` },
  {"h3": "Três usos que valem memorizar"},
  {"p": "**Indexar por um campo** — de busca linear para acesso direto, numa linha:"},
  { code: `pessoas := [{"id": 10, "nome": "Ana"}, {"id": 20, "nome": "Bruno"}]
por_id := {p["id"]: p["nome"] cycle p in pessoas}
out por_id[20]        # Bruno — sem varrer a lista` },
  {"p": "**Inverter um dicionário**:"},
  { code: `originais := {"a": 1, "b": 2}
out {originais[k]: k cycle k in originais.keys()}     # {1: a, 2: b}` },
  {"p": "**Normalizar chaves** vindas de fora:"},
  { code: `bruto := {"  Nome ": "Ana", "IDADE": 30}
out {k.trim().lower(): bruto[k] cycle k in bruto.keys()}` },
  {"callout": {"tipo": "atencao", "texto": "Se duas iterações produzem a mesma chave, **a última vence** — silenciosamente. Cuidado ao usar como chave algo que pode se repetir."}},
  {"h2": "Múltiplas fontes"},
  { code: `out [$"{a}x{b}={a * b}" cycle a in [2, 3] cycle b in [1, 2, 3]]` },
  {"p": "O `cycle` da direita gira mais rápido — é o laço interno. O resultado tem `2 × 3 = 6` itens."},
  {"h2": "Escopo"},
  {"p": "A variável do `cycle` **não vaza**:"},
  { code: `_ := [i cycle i in [1, 2]]
out i        # erro: Undefined name 'i'` },
  {"p": "Isso evita o bug clássico de reaproveitar sem querer o `i` de uma compreensão anterior."},
  {"h2": "Compreensão ou pipeline?"},
  { code: `[n * 2 cycle n in nums given n % 2 is 1]
nums >> sift n: n % 2 is 1 >> morph n: n * 2` },
  {"table": {"head": ["Situação", "Prefira"], "rows": [["um filtro e uma transformação", "compreensão"], ["três ou mais estágios", "[pipeline](/pipelines)"], ["duas fontes combinadas", "compreensão"], ["termina com uma redução", "pipeline (`distill`)"], ["lógica com vários passos", "laço `cycle`"]]}},
  {"p": "A compreensão diz **o que** você quer; o laço diz **como** obter. Para transformações simples, a primeira é mais direta — mas não force tudo numa linha."},
];

const headings = [{ id: 'a-forma', text: "A forma", level: 2 as const }, { id: 'listas', text: "Listas", level: 2 as const }, { id: 'sobre-outras-fontes', text: "Sobre outras fontes", level: 2 as const }, { id: 'vaults', text: "Vaults", level: 2 as const }, { id: 'multiplas-fontes', text: "Múltiplas fontes", level: 2 as const }, { id: 'escopo', text: "Escopo", level: 2 as const }, { id: 'compreensao-ou-pipeline', text: "Compreensão ou pipeline?", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Compreensões"}
      description={"Construir listas e vaults numa expressão, transformando e filtrando."}
      href={"/fundamentos/compreensoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
