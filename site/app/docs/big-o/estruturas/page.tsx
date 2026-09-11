// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Custo das estruturas",
  description: "O que cada operação de cluster, vault e string realmente custa.",
};

const blocos: Bloco[] = [
  {"p": "Escolher a estrutura certa costuma render mais que otimizar o algoritmo. Esta é a tabela que decide."},
  {"h2": "Cluster"},
  {"table": {"head": ["Operação", "Custo", "Por quê"], "rows": [["`xs[i]`", "O(1)", "acesso direto pelo índice"], ["`xs.append(x)`", "O(1)*", "amortizado — ver [casos](/docs/big-o/casos)"], ["`xs.pop()`", "O(1)", "remove do fim"], ["`xs.pop(0)`", "O(n)", "desloca todos os outros"], ["`xs.insert(0, x)`", "O(n)", "idem"], ["`x in xs`", "O(n)", "percorre até achar"], ["`xs.index_of(x)`", "O(n)", "idem"], ["`xs.remove(x)`", "O(n)", "procura e desloca"], ["`len(xs)`", "O(1)", "o tamanho é guardado"], ["`xs[a:b]`", "O(b−a)", "copia a fatia"], ["`xs.sort()`", "O(n log n)", "ordenação por comparação"], ["`xs.reverse()`", "O(n)", "troca aos pares"], ["`sum(xs)`, `max(xs)`", "O(n)", "percorre uma vez"], ["`[...a, ...b]`", "O(n+m)", "copia os dois"]]}},
  {"callout": {"tipo": "atencao", "titulo": "`pop(0)` num laço é O(n²)", "texto": "Remover do início desloca todos os outros. Para uma fila, percorra com índice ou inverta a lista e use `pop()`."}},
  {"h2": "Vault"},
  {"table": {"head": ["Operação", "Custo", "Por quê"], "rows": [["`v[chave]`", "O(1)", "tabela de espalhamento"], ["`v[chave] := x`", "O(1)", "idem"], ["`v.has(chave)`", "O(1)", "idem"], ["`chave in v`", "O(1)", "idem"], ["`v.get(chave, padrao)`", "O(1)", "idem"], ["`delete v[chave]`", "O(1)", "idem"], ["`v.keys()`", "O(n)", "monta o cluster"], ["`v.values()`", "O(n)", "idem"], ["`v.items()`", "O(n)", "idem"], ["`len(v)`", "O(1)", "guardado"]]}},
  {"p": "**O vault é a estrutura mais subutilizada da linguagem.** Quase todo O(n²) acidental some ao trocar uma busca linear por uma consulta de vault."},
  {"h2": "String"},
  {"table": {"head": ["Operação", "Custo", "Por quê"], "rows": [["`s[i]`", "O(1)", "acesso direto"], ["`len(s)`", "O(1)", "guardado"], ["`a + b`", "O(n+m)", "cria uma string nova"], ["`s.contains(t)`", "O(n·m)", "compara em cada posição"], ["`s.split(sep)`", "O(n)", "uma passada"], ["`sep.join(xs)`", "O(n)", "aloca uma vez"], ["`s.replace(a, b)`", "O(n)", "uma passada"], ["`s.upper()`", "O(n)", "cria uma nova"], ["`s[a:b]`", "O(b−a)", "copia"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Strings são imutáveis", "texto": "Toda operação que \"muda\" uma string cria outra. `s := s + x` num laço é O(n²). Acumule num cluster e use `join` no fim."}},
  {"h2": "Record e blueprint"},
  {"table": {"head": ["Operação", "Custo"], "rows": [["`p.campo`", "O(1)"], ["`p with {...}`", "O(k) — k campos"], ["`spawn X(...)`", "O(k) — k campos"], ["`p1 is p2` (record)", "O(k) — compara campo a campo"], ["chamar um método", "O(1) + o corpo"], ["`root.metodo()`", "O(d) — d = profundidade da herança"]]}},
  {"h2": "Escolhendo"},
  {"table": {"head": ["Você precisa de…", "Use", "Por quê"], "rows": [["ordem e índice", "`Cluster`", "acesso O(1) por posição"], ["procurar por chave", "`Vault`", "O(1) contra O(n)"], ["itens únicos", "`Vault` com valor `yes`", "a chave já garante unicidade"], ["contar ocorrências", "`xs.tally()`", "uma passada, O(n)"], ["agrupar", "`xs.group_by(f)`", "uma passada, O(n)"], ["valor imutável", "`record`", "igualdade estrutural, serve de chave"], ["entidade com estado", "`blueprint`", "identidade própria"]]}},
];

const headings = [{ id: 'cluster', text: "Cluster", level: 2 as const }, { id: 'vault', text: "Vault", level: 2 as const }, { id: 'string', text: "String", level: 2 as const }, { id: 'record-e-blueprint', text: "Record e blueprint", level: 2 as const }, { id: 'escolhendo', text: "Escolhendo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Custo das estruturas"}
      description={"O que cada operação de cluster, vault e string realmente custa."}
      href={"/docs/big-o/estruturas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
