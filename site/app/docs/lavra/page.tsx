// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Lavra",
  description: "A consulta tipada do DataForge: o cliente diz exatamente quais campos quer, e recebe exatamente aqueles.",
};

const blocos: Bloco[] = [
  {"p": "**Lavra** é a consulta tipada do DataForge. O cliente diz **exatamente** o que precisa, numa consulta, e recebe exatamente aquilo — nem um campo a mais, nem uma segunda chamada para buscar o que faltou."},
  { code: `busca:
    usuario(id: 7):
        nome
        pedidos(limite: 3):
            numero
            total`, lang: 'lavra' },
  {"p": "Uma rota REST devolve o que o **servidor** decidiu devolver. Quem precisa de menos carrega o resto; quem precisa de mais faz outra chamada. Numa tela de celular com rede ruim, as duas coisas custam."},
  {"h2": "O nome"},
  {"p": "**Lavra** é a extração de um veio de minério — e `lavrar` também é redigir um documento. As duas coisas que este módulo faz: um esquema é *lavrado*, e a consulta *lavra* dele exatamente o minério que quer. Segue a metáfora da forja, como [Kiln](/docs/kiln), [Crucible](/docs/crucible) e [Vitrine](/docs/vitrine)."},
  {"h2": "O esquema nasce dos seus records"},
  {"p": "Esta é a decisão que define o módulo. **Não há uma segunda linguagem de esquema ao lado da linguagem:**"},
  { code: `record Usuario:
    id: Integer
    nome: String
    email: String

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Usuario)`, lang: 'df' },
  {"p": "O GraphQL precisa de um SDL próprio porque o servidor pode estar escrito em qualquer coisa, e o esquema tem de existir fora dela. Aqui o servidor é DataForge, e o `record` já diz nome, campo e tipo. Um arquivo de esquema ao lado seria uma **segunda fonte de verdade** para divergir da primeira."},
  {"callout": {"tipo": "nota", "titulo": "O que o record não diz", "texto": "O que é obrigatório, o que é lista de quê, qual campo é calculado e por quem — isso entra com `Lavra.campo`. O record dá a forma; o esquema dá o contrato."}},
  {"h2": "A consulta é indentada"},
  {"p": "Porque a linguagem é. Uma consulta escrita ao lado do código que a usa tem de parecer com ele — e o `:` no fim marca \"isto tem seleção dentro\", exatamente como em `given`, `cycle` e `action`."},
  {"table": {"head": ["GraphQL", "Lavra"], "rows": [["`{ … }`", "indentação"], ["`query`", "`busca`"], ["`mutation`", "`mudanca`"], ["`subscription`", "`assinatura`"], ["`type`", "`tipo`"], ["`input`", "`entrada`"], ["`interface`", "`contrato`"], ["`union`", "`uniao`"], ["`scalar`", "`escalar`"], ["`fragment X on T`", "`trecho X em T`"], ["`...X`", "`...X`"], ["`... on T { }`", "`... em T:`"], ["`@include(if:)`", "`@incluir(se:)`"], ["`@skip(if:)`", "`@pular(se:)`"], ["`$v: T = padrão`", "`$v: T := padrão`"], ["`!` e `[ ]`", "iguais"]]}},
  {"p": "`!` e `[ ]` são a **única** coisa emprestada da escrita do GraphQL, e de propósito: quem já conhece lê sem aprender nada, e quem não conhece aprende dois símbolos."},
  {"h2": "Um exemplo inteiro"},
  { code: `adopt Arcane.Lavra as Lavra

record Usuario:
    id: Integer
    nome: String
    email: String

usuarios := [Usuario(1, "Ana", "ana@forja.co"), Usuario(2, "Bia", "bia@forja.co")]

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Usuario)
Lavra.campo(esq, "Usuario", "nome", "String!")

action achar(raiz, args, ctx):
    achados := [u cycle u in usuarios given u.id is args["id"]]
    yield achados[0] given len(achados) bigger 0 otherwise void

Lavra.busca(esq, "usuario", "Usuario", args := {"id": "Integer!"}, resolve := achar)
Lavra.conferir(esq)

r := Lavra.executar(esq, """
busca:
    usuario(id: 1):
        nome
""")

out r["dados"]`, lang: 'df' },
  { code: `{usuario: {nome: Ana}}`, lang: 'text' },
  {"h2": "O que ele traz"},
  {"table": {"head": ["Assunto", "Página"], "rows": [["Tipos, campos, argumentos, nulidade, listas", "[O esquema](/docs/lavra/esquema)"], ["Enums, entradas, escalares, contratos, uniões", "[O esquema](/docs/lavra/esquema)"], ["Busca, mudança, assinatura, apelidos", "[A consulta](/docs/lavra/consulta)"], ["Trechos, variáveis, diretivas, introspecção", "[A consulta](/docs/lavra/consulta)"], ["Resolvedores, contexto, erros, autorização", "[Resolvedores](/docs/lavra/resolvedores)"], ["Lote contra o N+1, paginação, cache", "[Desempenho](/docs/lavra/desempenho)"], ["Validação, limites, rate limit, observabilidade", "[Segurança](/docs/lavra/seguranca)"], ["HTTP, WebSocket, tempo real, cliente", "[O servidor](/docs/lavra/servidor)"], ["Vários serviços, portão, composição", "[Federação](/docs/lavra/federacao)"], ["CRUD, banco, DDD, testes, deploy, CI", "[Na prática](/docs/lavra/pratica)"]]}},
  {"h2": "O que ele NÃO é"},
  {"p": "Lavra **não é GraphQL**. Não fala o protocolo do GraphQL, não lê arquivos de SDL, e uma ferramenta de GraphQL não conversa com ele. As ideias são as mesmas — e são boas —, a escrita é a do DataForge."},
  {"p": "Ele também não é um planejador de consulta distribuído: a [federação](/docs/lavra/federacao) compõe esquemas e resolve a fronteira com o lote, e não com um plano de execução entre serviços. Um subconjunto pela metade seria pior que a honestidade de não ter."},
  {"cards": [{"href": "/docs/lavra/esquema", "title": "O esquema", "desc": "Tipos, campos, contratos, uniões."}, {"href": "/docs/lavra/consulta", "title": "A consulta", "desc": "A linguagem que o cliente escreve."}, {"href": "/docs/lavra/servidor", "title": "O servidor", "desc": "HTTP e tempo real, sobre o Kiln."}]},
];

const headings = [{ id: 'o-nome', text: "O nome", level: 2 as const }, { id: 'o-esquema-nasce-dos-seus-records', text: "O esquema nasce dos seus records", level: 2 as const }, { id: 'a-consulta-e-indentada', text: "A consulta é indentada", level: 2 as const }, { id: 'um-exemplo-inteiro', text: "Um exemplo inteiro", level: 2 as const }, { id: 'o-que-ele-traz', text: "O que ele traz", level: 2 as const }, { id: 'o-que-ele-nao-e', text: "O que ele NÃO é", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Lavra"}
      description={"A consulta tipada do DataForge: o cliente diz exatamente quais campos quer, e recebe exatamente aqueles."}
      href={"/docs/lavra"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
