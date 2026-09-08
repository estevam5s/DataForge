import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Relações",
  description: "Duas consultas para cem registros — e por que a relação não carrega sozinha.",
};

const blocos: Bloco[] = [
  {"h2": "O problema do N+1"},
  {"p": "Buscar cem usuários e ler `usuario.pedidos` de cada um faz **cento e uma** consultas. Isso não aparece em desenvolvimento, com três linhas na tabela, e derruba a produção com dez mil."},
  {"p": "**É o bug de ORM mais comum que existe.** No Forge, a relação não carrega sozinha ao ser lida — ou você pede, ou ela não vem:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")

Usuario := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes}
}, {"conexao": db})

Pedido := Forge.modelo("Pedido", {
    "id": {"tipo": "Serial"},
    "usuario_id": {"tipo": "Inteiro", "indice": yes},
    "total": {"tipo": "Real", "padrao": 0}
}, {"conexao": db})

Usuario.tem_muitos("pedidos", "Pedido")
Pedido.pertence_a("usuario", "Usuario")
Forge.migrar_tudo(db)

ana := Usuario.criar({"nome": "Ana"})
bia := Usuario.criar({"nome": "Bia"})
Pedido.criar({"usuario_id": ana["id"], "total": 100.0})
Pedido.criar({"usuario_id": ana["id"], "total": 50.0})
Pedido.criar({"usuario_id": bia["id"], "total": 20.0})

// DUAS consultas, para qualquer quantidade de usuários
com_pedidos := Usuario.com(Usuario.todos(), "pedidos")
assert len(com_pedidos[0]["pedidos"]) is 2
assert len(com_pedidos[1]["pedidos"]) is 1`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Duas, e há teste contando", "texto": "A suíte do Forge tem um teste que instrumenta a conexão e conta as consultas. Se alguém trocar a implementação por uma que faz N+1, ele falha."}},
  {"h2": "Os quatro tipos"},
  { code: `// um usuário tem muitos pedidos
Usuario.tem_muitos("pedidos", "Pedido")

// um pedido pertence a um usuário
Pedido.pertence_a("usuario", "Usuario")

// um usuário tem um perfil
Usuario.tem_um("perfil", "Perfil")

// um post tem muitas etiquetas, e uma etiqueta muitos posts
Post.muitos_para_muitos("etiquetas", "Etiqueta")`, lang: 'df' },
  {"table": {"head": ["Relação", "A chave fica em", "Padrão do nome"], "rows": [["`tem_muitos`", "na tabela do outro", "`<modelo>_id`"], ["`tem_um`", "na tabela do outro", "`<modelo>_id`"], ["`pertence_a`", "nesta tabela", "`<nome>_id`"], ["`muitos_para_muitos`", "numa tabela ponte", "as duas chaves"]]}},
  {"h2": "Do outro lado"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"}, "nome": {"tipo": "Texto"}
}, {"conexao": db})
P := Forge.modelo("Pedido", {
    "id": {"tipo": "Serial"}, "usuario_id": {"tipo": "Inteiro"},
    "total": {"tipo": "Real", "padrao": 0}
}, {"conexao": db})
P.pertence_a("usuario", "Usuario")
Forge.migrar_tudo(db)

ana := U.criar({"nome": "Ana"})
P.criar({"usuario_id": ana["id"], "total": 10.0})

com_dono := P.com(P.todos(), "usuario")
assert com_dono[0]["usuario"]["nome"] is "Ana"`, lang: 'df' },
  {"h2": "Relação desconhecida avisa"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {"id": {"tipo": "Serial"}}, {"conexao": db})
U.tem_muitos("pedidos", "Pedido")
Forge.migrar_tudo(db)

monitor:
    U.com(U.todos(), "inventada")
handle SchemaError as e:
    assert "inventada" in e.message`, lang: 'df' },
  {"p": "A mensagem lista as relações que existem — é mais útil que \"não encontrada\"."},
];

const headings = [{ id: 'o-problema-do-n1', text: "O problema do N+1", level: 2 as const }, { id: 'os-quatro-tipos', text: "Os quatro tipos", level: 2 as const }, { id: 'do-outro-lado', text: "Do outro lado", level: 2 as const }, { id: 'relacao-desconhecida-avisa', text: "Relação desconhecida avisa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Relações"}
      description={"Duas consultas para cem registros — e por que a relação não carrega sozinha."}
      href={"/docs/orm/relacoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
