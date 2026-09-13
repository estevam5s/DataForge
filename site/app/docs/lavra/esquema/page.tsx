// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O esquema",
  description: "Tipos, campos, argumentos, nulidade, listas, enums, entradas, escalares próprios, contratos e uniões.",
};

const blocos: Bloco[] = [
  {"p": "O esquema é **tudo o que a consulta pode pedir**, e quem responde por cada parte. Ele é montado uma vez, na subida, e conferido inteiro antes de a primeira consulta chegar."},
  {"h2": "Tipos, a partir de records"},
  { code: `record Usuario:
    id: Integer
    nome: String
    email: String

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Usuario)`, lang: 'df' },
  {"p": "`Lavra.tipo` lê os campos declarados. Também aceita um **blueprint** e um **vault** de tipos, para quando o dado não vem de um record:"},
  { code: `Lavra.tipo(esq, {"id": "Integer", "nome": "String"}, nome := "Cliente")
Lavra.tipo(esq, Usuario, esconder := ["senha_hash"])`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Esconder é parte do esquema", "texto": "Um campo que existe no record e não está no esquema **não pode ser pedido**. É a forma mais barata de garantir que `senha_hash` nunca saia: para quem consulta, ele não existe."}},
  {"h2": "A notação de tipo"},
  {"table": {"head": ["Escrita", "Significa"], "rows": [["`String`", "pode ser `void`"], ["`String!`", "**nunca** é `void`"], ["`[String]`", "lista que pode ser void, de itens que podem ser void"], ["`[String!]!`", "lista que nunca é void, de itens que nunca são void"]]}},
  {"p": "O `!` não é decoração: ele muda o que acontece quando o resolvedor falha. Um campo que admite `void` vira `void` e o resto da resposta segue; um `!` **sobe** o erro para o pai, e daí para cima, até achar alguém que admita `void`."},
  {"p": "É a única forma de a promessa do `!` valer alguma coisa. Se um `String!` pudesse voltar vazio, o cliente teria de conferir cada campo mesmo assim — e aí o `!` não diria nada."},
  {"h2": "Campos calculados"},
  { code: `action pedidos_de(usuario, args, ctx):
    yield Banco.pedidos_do_usuario(usuario.id)

Lavra.campo(esq, "Usuario", "pedidos", "[Pedido!]!",
    args := {"limite": {"tipo": "Integer", "padrao": 10}},
    resolve := pedidos_de,
    descricao := "Os pedidos deste usuário, do mais recente ao mais antigo.")`, lang: 'df' },
  {"p": "Um campo **sem** `resolve` lê o valor do próprio objeto — do record, do vault, da instância. É o caso da maioria, e por isso é o padrão."},
  {"h2": "Argumentos"},
  { code: `args := {
    "id": "Integer!",                              // obrigatório
    "limite": {"tipo": "Integer", "padrao": 10},   // com padrão
    "ordem": {"tipo": "Ordem", "padrao": "Recente"},
}`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Sem padrão é diferente de padrão void", "texto": "Um argumento **sem** padrão é exigido quando o tipo é `!`. Um **com** padrão `void` já tem resposta. Os dois casos existem, e confundi-los faz um campo obrigatório passar despercebido."}},
  {"h2": "Enums"},
  { code: `enum Estado:
    Rascunho
    Publicado := "pub"

Lavra.enum(esq, "Estado", Estado)`, lang: 'df' },
  {"p": "O `enum` da linguagem entra direto. A consulta escreve o **nome** (`Publicado`), e o resolvedor recebe o **valor** (`\"pub\"`). A tradução é do esquema, e é o que permite trocar o valor guardado no banco sem quebrar quem consulta."},
  {"h2": "Entradas: o que uma mudança recebe"},
  { code: `record NovoUsuario:
    nome: String
    email: String

Lavra.entrada(esq, NovoUsuario)
Lavra.campo(esq, "NovoUsuario", "nome", "String!")
Lavra.campo(esq, "NovoUsuario", "email", "String!")

Lavra.mudanca(esq, "criarUsuario", "Usuario!",
    args := {"dados": "NovoUsuario!"}, resolve := criar)`, lang: 'df' },
  {"p": "Entrada e saída são tipos **diferentes**, de propósito. O `Usuario` que sai tem `id` e `criado_em`; o que entra não tem nem um nem outro. Usar o mesmo tipo nos dois lados obrigaria a marcar metade dos campos como opcionais — e aí nenhum deles seria conferido."},
  {"callout": {"tipo": "atencao", "titulo": "Campo desconhecido é recusado, não ignorado", "texto": "Uma entrada com `emial` falha, e diz quais campos existem. Ignorar o campo com o nome quase certo faria o dado **não chegar**, sem nada denunciando."}},
  {"h2": "Escalares próprios"},
  { code: `adopt Arcane.Time as Time

Lavra.escalar(esq, "Data",
    serializa := lambda d => Time.format(d, "%Y-%m-%d"),
    desserializa := lambda t => Time.parse(t, "%Y-%m-%d"),
    descricao := "Uma data, sem hora, em ISO 8601.")`, lang: 'df' },
  {"p": "Um escalar próprio é onde entra o que a linguagem não tem como primitivo: `Data`, `Dinheiro`, `Email`, `CPF`. A validação vive no `desserializa` e vale para **todo** campo daquele tipo, em vez de espalhada por cada resolvedor."},
  {"h2": "Contratos"},
  {"p": "Um **contrato** são campos que vários tipos prometem ter. Quem consulta pede os campos do contrato e recebe de qualquer um dos que o cumprem."},
  { code: `Lavra.tipo(esq, Artigo, cumpre := ["Conteudo"])
Lavra.tipo(esq, Video, cumpre := ["Conteudo"])

action que_tipo(valor, ctx):
    yield "Video" given "minutos" in valor.fields otherwise "Artigo"

Lavra.contrato(esq, "Conteudo", {"id": "Integer", "titulo": "String"},
    resolve_tipo := que_tipo)`, lang: 'df' },
  { code: `busca:
    acervo:
        titulo
        ... em Video:
            minutos`, lang: 'lavra' },
  {"p": "O `resolve_tipo` responde **qual tipo concreto é aquele valor**. Sem ele, o Lavra tenta descobrir pelo nome do record — e quando não consegue, diz isso com a lista dos candidatos, em vez de devolver um objeto pela metade."},
  {"callout": {"tipo": "dica", "titulo": "O contrato é conferido na montagem", "texto": "Um tipo que declara cumprir um contrato e não tem um dos campos dele **para o `Lavra.conferir`** — e não a primeira consulta que por acaso pedir aquele campo, meses depois, em produção."}},
  {"h2": "Uniões"},
  {"p": "Uma **união** é quando o campo devolve um de vários tipos que não têm nada em comum — o resultado de uma busca, por exemplo."},
  { code: `Lavra.uniao(esq, "Achado", ["Usuario", "Produto", "Artigo"],
    resolve_tipo := classificar)`, lang: 'df' },
  { code: `busca:
    buscar(termo: "forja"):
        ... em Usuario:
            nome
        ... em Produto:
            titulo
            preco`, lang: 'lavra' },
  {"p": "A diferença para o contrato: uma união **não tem campos próprios**. Não dá para pedir `id` direto dela, porque não há promessa de que todos os membros tenham `id`."},
  {"h2": "Fechar o esquema"},
  { code: `Lavra.conferir(esq)`, lang: 'df' },
  {"p": "Confere que todo tipo citado existe, que todo contrato é cumprido, que toda união aponta para tipos reais, e que há ao menos uma busca. Roda na **montagem**: um esquema que não fecha derruba a subida, e não a consulta de alguém."},
  {"h2": "O esquema em texto"},
  { code: `out Lavra.texto_do_esquema(esq)`, lang: 'df' },
  {"p": "Serve para **versionar**. Um esquema em arquivo entra no diff, e uma mudança que quebra o cliente aparece na revisão em vez de na produção. É o mesmo texto que `GET /lavra` devolve."},
];

const headings = [{ id: 'tipos-a-partir-de-records', text: "Tipos, a partir de records", level: 2 as const }, { id: 'a-notacao-de-tipo', text: "A notação de tipo", level: 2 as const }, { id: 'campos-calculados', text: "Campos calculados", level: 2 as const }, { id: 'argumentos', text: "Argumentos", level: 2 as const }, { id: 'enums', text: "Enums", level: 2 as const }, { id: 'entradas-o-que-uma-mudanca-recebe', text: "Entradas: o que uma mudança recebe", level: 2 as const }, { id: 'escalares-proprios', text: "Escalares próprios", level: 2 as const }, { id: 'contratos', text: "Contratos", level: 2 as const }, { id: 'unioes', text: "Uniões", level: 2 as const }, { id: 'fechar-o-esquema', text: "Fechar o esquema", level: 2 as const }, { id: 'o-esquema-em-texto', text: "O esquema em texto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O esquema"}
      description={"Tipos, campos, argumentos, nulidade, listas, enums, entradas, escalares próprios, contratos e uniões."}
      href={"/docs/lavra/esquema"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
