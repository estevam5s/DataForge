// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Resolvedores",
  description: "Quem responde por cada campo: contexto, autorização, erros, middleware e a ordem das coisas.",
};

const blocos: Bloco[] = [
  {"p": "Um **resolvedor** é a ação que responde por um campo. Ele recebe o objeto pai, os argumentos e o contexto — e devolve o valor."},
  { code: `action pedidos_de(usuario, args, ctx):
    yield Banco.pedidos(usuario.id, limite := args["limite"])

Lavra.campo(esq, "Usuario", "pedidos", "[Pedido!]!",
    args := {"limite": {"tipo": "Integer", "padrao": 10}},
    resolve := pedidos_de)`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Um resolvedor simples não precisa dos três", "texto": "`lambda p => p.total` funciona. O Lavra chama com quantos argumentos a ação aceitar — exigir os três faria toda linha carregar um `_, _` que não diz nada."}},
  {"h2": "A ordem em que as coisas acontecem"},
  { code: `texto da consulta
    ↓  ler          — vira árvore; erro aqui traz linha e coluna
    ↓  validar      — TODOS os problemas de uma vez, sem resolver nada
    ↓  limites      — profundidade e custo, antes de qualquer resolvedor
    ↓  resolver     — campo a campo, do topo para as folhas
    ↓  lote         — a fila vira uma consulta só
    ↓  coagir       — o valor vira o tipo declarado
resposta: dados, erros, extensoes`, lang: 'text' },
  {"p": "A validação vem **antes** de executar de propósito. Executar e descobrir no meio que o campo não existe já custou tudo o que veio antes — inclusive escritas, numa `mudanca`."},
  {"h2": "O contexto"},
  {"p": "O contexto é o que atravessa a consulta inteira: quem pediu, a conexão do banco, o rastro. Ele é montado **por pedido** e morre com ele."},
  { code: `action contexto_de(req):
    token := req["headers"]["authorization"] ?? ""
    yield {
        "usuario": autenticar(token),
        "banco": conexao,
        "ip": req["ip"],
    }

Lavra.montar(api, esq, "/lavra", contexto_de := contexto_de)`, lang: 'df' },
  { code: `action meu_perfil(raiz, args, ctx):
    given ctx["usuario"] is void:
        Lavra.recusar("entre para ver o seu perfil")
    yield ctx["usuario"]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Estado global não serve", "texto": "Guardar o usuário num vault do módulo funciona até o segundo pedido simultâneo — o Kiln atende **um pedido por thread**, e dois pedidos escrevendo no mesmo nome perdem um dos dois. O contexto existe para isso."}},
  {"h2": "Erros"},
  {"p": "Um erro num campo **não derruba a resposta inteira**. O campo vira `void`, o erro entra na lista com o **caminho** até ele, e o resto da consulta continua."},
  { code: `action risco_de(cliente, args, ctx):
    resposta := Malha.de(ctx["malha"], "risco").obter($"/risco/{cliente.id}")
    given resposta["status"] isnt 200:
        Lavra.erro("o serviço de risco não respondeu", codigo := "dependencia")
    yield resposta["corpo"]["nota"]`, lang: 'df' },
  { code: `{
  "dados": {"cliente": {"nome": "Ana", "risco": void}},
  "erros": [{"mensagem": "o serviço de risco não respondeu",
             "caminho": ["cliente", "risco"],
             "codigo": "dependencia"}]
}`, lang: 'json' },
  {"p": "Quem pediu dez campos e teve um problema num recebe **nove** — não zero. É a diferença entre uma tela com um aviso e uma tela vazia."},
  {"p": "A exceção é o campo `!`: ele prometeu nunca ser `void`, então um erro ali sobe para o pai, e daí para cima, até achar alguém que admita `void`."},
  {"h2": "Autorização"},
  {"p": "Há três lugares, e eles resolvem coisas diferentes:"},
  {"table": {"head": ["Onde", "Para quê"], "rows": [["o campo não está no esquema", "ninguém pode pedir, nunca"], ["`Lavra.recusar` no resolvedor", "**este** usuário não pode ver **este** dado"], ["uma diretiva `@admin`", "a regra vale para muitos campos, e aparece na consulta"]]}},
  { code: `action cpf_de(usuario, args, ctx):
    given ctx["usuario"]?.id isnt usuario.id and ctx["papel"] isnt "admin":
        Lavra.recusar("o CPF é do próprio dono")
    yield usuario.cpf`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "Autorizar no campo, e não na busca", "texto": "Proteger só a busca de topo deixa a porta dos fundos aberta: `pedido.cliente.cpf` chega ao mesmo dado por outro caminho. Num grafo, todo caminho é uma porta."}},
  {"h2": "Middleware"},
  {"p": "Para o que vale para toda consulta — registro, rastro, tempo —, use o middleware do próprio [Kiln](/docs/kiln), que roda antes da rota:"},
  { code: `action rastrear(req):
    Malha.propagar(req, "api")

server api on 8080:
    middleware rastrear
    middleware Kiln.rate_limit(60, 60)

Lavra.montar(api, esq, "/lavra")`, lang: 'df' },
  {"p": "Para o que vale por **campo**, o lugar é a diretiva própria — ela aparece na consulta, e é auditável lendo o texto."},
  {"h2": "Mudanças"},
  { code: `action criar_pedido(raiz, args, ctx):
    dados := args["dados"]
    given len(dados["itens"]) is 0:
        Lavra.erro("um pedido precisa de ao menos um item", codigo := "validacao")
    yield Banco.transacao(ctx["banco"], lambda => gravar(dados))`, lang: 'df' },
  {"p": "Uma mudança que toca duas tabelas precisa de **transação** — e é `Arcane.Database` quem a dá. O Lavra não inventa uma: a venda gravada com o estoque não baixado é o mesmo problema em qualquer camada, e ele já está resolvido embaixo."},
  {"callout": {"tipo": "nota", "titulo": "As mudanças rodam em série", "texto": "Uma `mudanca` com três campos resolve os três **na ordem escrita**. Duas escritas no mesmo dado rodando juntas dariam resultado dependente de ordem — e a ordem da consulta é a única que quem escreveu controla."}},
];

const headings = [{ id: 'a-ordem-em-que-as-coisas-acontecem', text: "A ordem em que as coisas acontecem", level: 2 as const }, { id: 'o-contexto', text: "O contexto", level: 2 as const }, { id: 'erros', text: "Erros", level: 2 as const }, { id: 'autorizacao', text: "Autorização", level: 2 as const }, { id: 'middleware', text: "Middleware", level: 2 as const }, { id: 'mudancas', text: "Mudanças", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Resolvedores"}
      description={"Quem responde por cada campo: contexto, autorização, erros, middleware e a ordem das coisas."}
      href={"/docs/lavra/resolvedores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
