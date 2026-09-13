// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Federação",
  description: "Vários serviços, um esquema só para quem consulta: o portão, a composição e o campo que atravessa a fronteira.",
};

const blocos: Bloco[] = [
  {"p": "Cada time tem o seu serviço, e cada serviço tem o seu esquema. Quem consulta não quer saber disso: quer `usuario.pedidos.itens` numa consulta, sem descobrir que usuário mora num lugar e pedido em outro."},
  {"h2": "O portão"},
  { code: `portao := Lavra.portao()

Lavra.juntar(portao, "contas", esquema_de_contas)
Lavra.juntar(portao, "vendas", esquema_de_vendas)
Lavra.juntar(portao, "catalogo", esquema_de_catalogo)

portao.conferir()
Lavra.montar(api, portao.esquema, "/lavra")`, lang: 'df' },
  {"p": "Os tipos de cada serviço entram num esquema só. As buscas de cada um viram buscas do portão. Quem consulta vê **um** esquema."},
  {"h2": "O campo que atravessa"},
  {"p": "`Usuario` é de contas; `Pedido` é de vendas. O campo `usuario.pedidos` não pertence a nenhum dos dois sozinho — ele é a fronteira, e é declarado como **extensão**:"},
  { code: `action pedidos_do_usuario(usuario, args, ctx):
    yield Lavra.pedir(ctx, "pedidos_por_usuario", usuario["id"])

Lavra.estender(portao, "Usuario", "pedidos", "[Pedido!]!",
    resolve := pedidos_do_usuario)`, lang: 'df' },
  {"p": "Repare no `Lavra.pedir`: a fronteira é exatamente onde o [N+1](/docs/lavra/desempenho) dói mais, porque cada travessia é uma chamada de **rede**. Cinquenta usuários viram uma chamada ao serviço de vendas, e não cinquenta."},
  { code: `action buscar_pedidos(ids_de_usuario):
    r := cliente_de_vendas.consultar("""
busca Por($ids: [Integer!]!):
    pedidosPorUsuario(ids: $ids):
        usuario_id
        numero
        total
""", {"ids": ids_de_usuario})
    yield agrupar_por(r["dados"]["pedidosPorUsuario"], "usuario_id", ids_de_usuario)`, lang: 'df' },
  {"h2": "Conflito de nome é erro"},
  {"p": "Dois serviços que declaram `Usuario` **param a composição**:"},
  { code: `erro: 'Usuario' é declarado por 'contas' e por 'perfis'.
  Dois tipos com o mesmo nome fariam a consulta devolver os campos de
  um ou de outro conforme a ordem do 'juntar'.
  Renomeie um dos dois, ou declare o tipo num serviço só e estenda-o
  do outro com Lavra.estender.`, lang: 'text' },
  {"p": "Fundir os dois em silêncio faria a resposta depender da **ordem do `juntar`** — que é o pior jeito de falhar: funciona na máquina de quem escreveu e muda quando alguém reordena duas linhas."},
  {"h2": "De onde vem cada campo"},
  { code: `out Lavra.mapa(portao)`, lang: 'df' },
  { code: `{servicos: [catalogo, contas, vendas],
 tipos: {Usuario: contas, Pedido: vendas, Produto: catalogo},
 extensoes: [{tipo: Usuario, campo: pedidos}]}`, lang: 'text' },
  {"p": "É a resposta para \"quem declara isto?\" — a pergunta que mais se faz num esquema federado, e a que mais custa responder lendo código de três repositórios."},
  {"h2": "O que este portão NÃO faz"},
  {"p": "Ele não é o Apollo Federation. Não há `@key`, `@external`, `_entities` nem **plano de consulta distribuído**: o portão resolve a extensão chamando o serviço dono, uma vez por fronteira, com o lote fazendo o agrupamento."},
  {"p": "Um planejador de consulta distribuído é um projeto próprio — ele decide quais subconsultas mandar, em que ordem, e como juntar os pedaços. Um subconjunto pela metade seria pior que a honestidade de não ter."},
  {"callout": {"tipo": "dica", "titulo": "Quando isto basta", "texto": "Na esmagadora maioria dos casos, sim. O plano distribuído ganha quando a fronteira é atravessada em várias direções na mesma consulta; com uma ou duas travessias — que é o normal —, uma chamada em lote por fronteira é o mesmo número de idas à rede."}},
];

const headings = [{ id: 'o-portao', text: "O portão", level: 2 as const }, { id: 'o-campo-que-atravessa', text: "O campo que atravessa", level: 2 as const }, { id: 'conflito-de-nome-e-erro', text: "Conflito de nome é erro", level: 2 as const }, { id: 'de-onde-vem-cada-campo', text: "De onde vem cada campo", level: 2 as const }, { id: 'o-que-este-portao-nao-faz', text: "O que este portão NÃO faz", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Federação"}
      description={"Vários serviços, um esquema só para quem consulta: o portão, a composição e o campo que atravessa a fronteira."}
      href={"/docs/lavra/federacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
