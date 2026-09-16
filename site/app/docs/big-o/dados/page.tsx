// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Complexidade em dados e I/O",
  description: "Onde a unidade de custo deixa de ser a operação e passa a ser o acesso — banco, disco e rede, com medição.",
};

const blocos: Bloco[] = [
  {"p": "Toda a análise das outras páginas conta **operações**, e supõe que todas custam igual. Quando o dado sai da memória, essa suposição quebra: um acesso a disco vale cem mil operações, e uma ida à rede vale dez milhões."},
  {"p": "A conta muda de unidade. O que se conta aqui não é instrução — é **ida e volta**."},
  {"table": {"head": ["Onde está o dado", "Ordem de grandeza do acesso", "Equivale a"], "rows": [["cache L1", "~1 ns", "1 operação"], ["memória principal", "~100 ns", "~100 operações"], ["SSD", "~100 µs", "~100 mil operações"], ["rede, no mesmo datacentro", "~500 µs", "~500 mil operações"], ["rede, entre continentes", "~150 ms", "~150 milhões"]]}},
  {"callout": {"tipo": "dica", "titulo": "A regra que decorre disso", "texto": "Um algoritmo `O(n^2)` que roda **na memória** costuma ganhar de um `O(n)` que vai ao banco a cada item. Antes de otimizar o laço, conte as idas."}},
  {"h2": "O N+1: o O(n) que ninguém vê"},
  {"p": "Buscar uma lista e depois, para cada item, buscar o relacionado. O código parece linear e **é** linear — em consultas, que é a unidade cara:"},
  { code: `// N+1: uma consulta pela lista, e mais uma por cliente
soma := 0.0
cycle c in DB.select(db, "clientes"):
    linhas := DB.query(db, "SELECT total FROM pedidos WHERE cliente_id = ?", [c["id"]])
    cycle l in linhas:
        soma += l["total"]
`, lang: 'df' },
  { code: `// uma consulta so: o banco agrupa, e volta uma vez
soma := 0.0
cycle l in DB.query(db, "SELECT cliente_id, SUM(total) AS t FROM pedidos GROUP BY cliente_id", []):
    soma += l["t"]
`, lang: 'df' },
  { code: `N+1 (501 consultas): 6.5 ms
uma consulta:        1.0 ms
razao: 6.4x
`, lang: 'text', title: `medido — 500 clientes, 5 mil pedidos, SQLite em memória` },
  {"p": "**6,4x** com o banco na mesma memória do processo, onde uma consulta é barata. Com o banco em outra máquina, cada uma das 501 paga uma ida à rede, e a mesma diferença vira **centenas de vezes**."},
  {"p": "É o problema de desempenho mais comum em sistema com banco, e ele não aparece em teste: com dez linhas de exemplo, as 11 consultas são instantâneas."},
  {"h2": "Índice: de O(n) para O(log n), medido"},
  {"p": "Sem índice, o banco lê a tabela inteira a cada consulta. Com índice, ele desce uma árvore. O `explain` mostra a diferença **antes** de você medir:"},
  { code: `adopt Arcane.Database as DB
adopt Arcane.Time as T

db := DB.memory()
DB.create_table(db, "pedidos", {"id": "INTEGER PRIMARY KEY", "cliente": "TEXT", "total": "REAL"})
DB.insert_many(db, "pedidos",
    [{"cliente": $"c{i % 500}", "total": i * 1.0} cycle i in range(0, 20000)])

inicio := T.monotonic()
cycle k from 1 to 200:
    DB.query(db, "SELECT * FROM pedidos WHERE cliente = ?", [$"c{k}"])
sem_indice := (T.monotonic() - inicio) * 1000

DB.create_index(db, "pedidos", ["cliente"])

inicio := T.monotonic()
cycle k from 1 to 200:
    DB.query(db, "SELECT * FROM pedidos WHERE cliente = ?", [$"c{k}"])
com_indice := (T.monotonic() - inicio) * 1000

out $"sem indice: {round(sem_indice, 1)} ms"
out $"com indice: {round(com_indice, 1)} ms"
out $"razao: {round(sem_indice / com_indice, 1)}x"
out DB.explain(db, "SELECT * FROM pedidos WHERE cliente = ?", ["c1"])
`, lang: 'df' },
  { code: `sem indice: 73.6 ms
com indice: 4.4 ms
razao: 16.6x
{passos: [SEARCH pedidos USING INDEX idx_pedidos_cliente (cliente=?)], varre_tabela: no, aviso: }
`, lang: 'text', title: `saída (20 mil linhas)` },
  {"p": "Antes do índice, o mesmo `explain` responde `varre_tabela: yes` e o aviso `le a tabela inteira: SCAN pedidos`. Esse campo é o que vale procurar num CI: uma consulta que varre a tabela inteira é aceitável com mil linhas e derruba o sistema com um milhão."},
  {"h2": "O que um índice custa"},
  {"p": "Ele não é grátis, e por isso não se indexa tudo:"},
  {"table": {"head": ["Operação", "Sem índice", "Com índice"], "rows": [["buscar por aquela coluna", "`O(n)`", "`O(log n)`"], ["inserir uma linha", "`O(1)`", "`O(log n)` — **por índice**"], ["atualizar aquela coluna", "`O(1)`", "`O(log n)`"], ["espaço em disco", "—", "mais uma estrutura por índice"]]}},
  {"p": "Indexe o que aparece em `WHERE`, `JOIN` e `ORDER BY` de consulta frequente. Uma tabela de escrita pesada com seis índices paga seis árvores a cada linha inserida."},
  {"h2": "Paginar por deslocamento é quadrático"},
  {"p": "`LIMIT 20 OFFSET 100000` parece constante e não é: o banco **produz e descarta** as cem mil primeiras linhas para chegar na página. Percorrer todas as páginas assim é `O(n^2)`."},
  { code: `// O(offset) por pagina — a ultima pagina e a mais cara
DB.query(db, "SELECT * FROM pedidos ORDER BY id LIMIT 20 OFFSET 100000", [])

// O(log n) por pagina: continua de onde parou
DB.query(db, "SELECT * FROM pedidos WHERE id > ? ORDER BY id LIMIT 20", [ultimo_id])
`, lang: 'sql' },
  {"p": "A segunda forma — paginação por cursor — exige um campo ordenado e único, e em troca cada página custa o mesmo. `DB.paginate` faz a primeira; para listas grandes e rolagem infinita, escreva a segunda."},
  {"h2": "Ler arquivo: o custo é o bloco"},
  {"p": "Disco não entrega byte, entrega **bloco**. Ler um arquivo de `n` bytes em blocos de `B` custa `O(n/B)` acessos — e é por isso que ler de mil em mil linhas ganha de ler de uma em uma, com a mesma classe assintótica."},
  { code: `// carrega o arquivo inteiro na memoria: O(n) de espaco
linhas := IO.read_lines("grande.csv")

// um item por vez: O(1) de espaco, e o mesmo O(n) de tempo
stream action registros(caminho):
    cycle linha in IO.read_lines(caminho):
        emit split(linha, ",")
`, lang: 'df' },
  {"p": "A segunda forma processa arquivo maior que a memória quando a fonte é preguiçosa. Ver [complexidade de espaço](/docs/big-o/espaco) e [generators](/docs/fundamentos/generators)."},
  {"h2": "A lista de conferência"},
  {"list": ["**Conte as idas ao banco**, não as linhas de código. Um laço com uma consulta dentro é um N+1 até prova em contrário.", "**Rode `DB.explain` nas consultas quentes** e procure `varre_tabela: yes`.", "**`DB.watch_slow` e `DB.slow_log`** registram o que passou do prazo, em produção.", "**Agregue no banco** (`SUM`, `GROUP BY`, `DB.aggregate`): trazer mil linhas para somar em memória paga transporte por nada.", "**Use transação para escrita em lote.** Sem ela, cada `insert` confirma sozinho, e o custo é por linha.", "**Pagine por cursor** quando a lista for grande."]},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/biblioteca/database", "title": "Arcane.Database", "desc": "transação, índice, explain, paginação e busca textual"}, {"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "por que contar operações não basta"}, {"href": "/docs/big-o/espaco", "title": "Complexidade de espaço", "desc": "processar mais dados do que cabem na memória"}]},
];

const headings = [{ id: 'o-n1-o-on-que-ninguem-ve', text: "O N+1: o O(n) que ninguém vê", level: 2 as const }, { id: 'indice-de-on-para-olog-n-medido', text: "Índice: de O(n) para O(log n), medido", level: 2 as const }, { id: 'o-que-um-indice-custa', text: "O que um índice custa", level: 2 as const }, { id: 'paginar-por-deslocamento-e-quadratico', text: "Paginar por deslocamento é quadrático", level: 2 as const }, { id: 'ler-arquivo-o-custo-e-o-bloco', text: "Ler arquivo: o custo é o bloco", level: 2 as const }, { id: 'a-lista-de-conferencia', text: "A lista de conferência", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Complexidade em dados e I/O"}
      description={"Onde a unidade de custo deixa de ser a operação e passa a ser o acesso — banco, disco e rede, com medição."}
      href={"/docs/big-o/dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
