import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "10 · Avançado",
  description: "10 exercícios: async, threads, canais, árvore binária e interpretador RPN.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 10`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["111", "**async / await**", "declare acoes assincronas e aguarde o resultado."], ["112", "**thread**", "dispare trabalho em segundo plano e espere terminar."], ["113", "**channel**", "passe valores entre partes do programa por um canal."], ["114", "**parallel**", "rode varias tarefas ao mesmo tempo."], ["115", "**defer com recursos reais**", "garanta que o arquivo seja apagado mesmo apos erro."], ["116", "**Lista ligada com blueprints**", "implemente uma lista ligada simples."], ["117", "**Arvore binaria de busca**", "insira valores e percorra em ordem."], ["118", "**Maquina de estados**", "modele o ciclo de vida de um pedido."], ["119", "**Sistema de inventario**", "junte blueprints, pipelines, erros e relatorio."], ["120", "**Avaliador de expressoes em notacao polonesa reversa**", "escreva um mini interpretador dentro do DataForge."]]}},
  {"h2": "111 · async / await"},
  {"p": "Declare acoes assincronas e aguarde o resultado."},
  { code: `// Exercicio 111 — async / await
// Enunciado: declare acoes assincronas e aguarde o resultado.

async action buscar_usuario(id):
    yield {"id": id, "nome": "Usuario " + str(id)}

async action buscar_pedidos(id):
    yield [{"id": 1, "usuario": id}, {"id": 2, "usuario": id}]

usuario := await buscar_usuario(7)
pedidos := await buscar_pedidos(7)

out usuario
out "pedidos:", len(pedidos)

assert usuario["id"] is 7, "id do usuario"
assert usuario["nome"] is "Usuario 7", "nome"
assert len(pedidos) is 2, "dois pedidos"
`, title: `111_async_await.df` },
  {"h2": "112 · thread"},
  {"p": "Dispare trabalho em segundo plano e espere terminar."},
  { code: `// Exercicio 112 — thread
// Enunciado: dispare trabalho em segundo plano e espere terminar.

resultados := []

thread:
    cycle i from 1 to 3:
        resultados.append("t1-" + str(i))

thread:
    cycle i from 1 to 3:
        resultados.append("t2-" + str(i))

wait 200
out "itens produzidos:", len(resultados)
assert len(resultados) is 6, "as duas threads produziram"
`, title: `112_threads.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 8 exercícios deste módulo estão em `exercicios/10-avancado/`. Rode-os com o comando acima."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '111--async--await', text: "111 · async / await", level: 2 as const }, { id: '112--thread', text: "112 · thread", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"10 · Avançado"}
      description={"10 exercícios: async, threads, canais, árvore binária e interpretador RPN."}
      href={"/exercicios/10-avancado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
