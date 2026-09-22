// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Carga antecipada e o N+1",
  description: "Duas consultas em vez de cento e uma — e a relação que atravessa um terceiro modelo.",
};

const blocos: Bloco[] = [
  {"p": "O N+1 é o defeito de desempenho mais comum de qualquer ORM, e o mais fácil de não notar: ele **funciona**. A página abre, os dados estão certos, e a lentidão cresce com o tamanho da lista — o que em desenvolvimento, com dez linhas, não aparece."},
  {"h2": "O problema"},
  { code: `// ERRADO — uma consulta para os clientes, e uma POR CLIENTE.
// Com cem clientes, sao cento e uma consultas.
//
//   clientes := Cliente.todos()
//   cycle c in clientes:
//       pedidos := Pedido.onde("cliente_id", c["id"]).buscar()
//
// CERTO — duas consultas, para qualquer quantidade:
//
//   clientes := Cliente.com(Cliente.todos(), "pedidos")

out "o numero de consultas nao pode crescer com o numero de linhas"`, lang: 'df' },
  { code: `adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Cliente := Forge.modelo("Cliente", {"id": "Serial", "nome": "Texto"})
Pedido := Forge.modelo("Pedido", {"id": "Serial", "cliente_id": "Inteiro", "total": "Decimal"})
cycle m in [Cliente, Pedido]:
    Forge.ligar(m, db)
    m.migrar()

Cliente.tem_muitos("pedidos", "Pedido", chave_externa := "cliente_id")
Pedido.pertence_a("cliente", "Cliente", chave_local := "cliente_id")

ana := Cliente.criar({"nome": "Ana"})
bob := Cliente.criar({"nome": "Bob"})
Pedido.criar({"cliente_id": ana["id"], "total": 99.9})
Pedido.criar({"cliente_id": ana["id"], "total": 45.0})
Pedido.criar({"cliente_id": bob["id"], "total": 12.0})

// DUAS consultas: uma para os clientes, outra para todos os
// pedidos deles.
cycle c in Cliente.com(Cliente.todos(), "pedidos"):
    out $"{c['nome']}: {len(c['pedidos'])} pedido(s)"

// E o outro lado, tambem em duas.
cycle p in Pedido.com(Pedido.todos(), "cliente"):
    out $"pedido {p['id']} e de {p['cliente']['nome']}"

Forge.fechar(db)`, lang: 'df' },
  {"h2": "A relação que atravessa um terceiro"},
  {"p": "O autor **não tem** comentários: ele tem posts, e os posts têm comentários. É a relação que não tem nome no dia a dia e aparece em todo sistema — e sem uma peça para ela, o caminho natural é carregar os posts, tirar os ids e consultar de novo. Quem escreve isso tende a fazer uma consulta por post: o N+1 com um passo a mais."},
  { code: `adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Autor := Forge.modelo("Autor", {"id": "Serial", "nome": "Texto"})
Post := Forge.modelo("Post", {"id": "Serial", "autor_id": "Inteiro", "titulo": "Texto"})
Comentario := Forge.modelo("Comentario", {"id": "Serial", "post_id": "Inteiro", "texto": "Texto"})
cycle m in [Autor, Post, Comentario]:
    Forge.ligar(m, db)
    m.migrar()

// Autor -> (Post) -> Comentario
Autor.tem_muitos_atraves("comentarios", "Comentario", "Post")

ana := Autor.criar({"nome": "Ana"})
bob := Autor.criar({"nome": "Bob"})
p1 := Post.criar({"autor_id": ana["id"], "titulo": "Um"})
p2 := Post.criar({"autor_id": ana["id"], "titulo": "Dois"})
p3 := Post.criar({"autor_id": bob["id"], "titulo": "Tres"})

cycle t in ["otimo", "concordo", "hmm"]:
    Comentario.criar({"post_id": p1["id"], "texto": t})
Comentario.criar({"post_id": p2["id"], "texto": "no outro"})
Comentario.criar({"post_id": p3["id"], "texto": "do bob"})

// TRES consultas: autores, posts deles, comentarios desses posts.
cycle a in Autor.com(Autor.todos(), "comentarios"):
    out $"{a['nome']}: {len(a['comentarios'])} comentario(s)"

assert len(Autor.com(Autor.todos(), "comentarios")[0]["comentarios"]) is 4

Forge.fechar(db)`, lang: 'df' },
  {"h2": "As cinco relações"},
  {"table": {"head": ["Relação", "Consultas", "Quando"], "rows": [["`tem_um`", "2", "um perfil por usuário"], ["`tem_muitos`", "2", "os pedidos de um cliente"], ["`pertence_a`", "2", "o cliente de um pedido"], ["`muitos_para_muitos`", "2 (com tabela-ponte)", "as etiquetas de um post"], ["`tem_muitos_atraves`", "3", "os comentários de um autor, pelos posts"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Indexe a chave estrangeira", "texto": "A carga antecipada troca N+1 por duas consultas — e a segunda é um `where chave_externa in (…)`. Sem índice nessa coluna, ela é uma **varredura da tabela inteira**, e o ganho some. É o item mais esquecido da lista de índices, porque a relação funciona sem ele."}},
  {"p": "Continue em [Escopos e paginação](/docs/orm/escopos) e [Em produção](/docs/banco-de-dados/producao)."},
];

const headings = [{ id: 'o-problema', text: "O problema", level: 2 as const }, { id: 'a-relacao-que-atravessa-um-terceiro', text: "A relação que atravessa um terceiro", level: 2 as const }, { id: 'as-cinco-relacoes', text: "As cinco relações", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Carga antecipada e o N+1"}
      description={"Duas consultas em vez de cento e uma — e a relação que atravessa um terceiro modelo."}
      href={"/docs/orm/atraves"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
