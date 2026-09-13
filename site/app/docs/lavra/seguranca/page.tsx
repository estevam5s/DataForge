// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Segurança",
  description: "Validação antes de executar, limites de profundidade e custo, rate limit, introspecção e observabilidade.",
};

const blocos: Bloco[] = [
  {"p": "Um servidor de consulta tem uma superfície de ataque que uma API REST não tem: **quem consulta escolhe a forma da consulta**. Isso é o valor do modelo, e é também o risco."},
  {"h2": "Validar antes de executar"},
  { code: `problemas := Lavra.validar(esq, texto)
given len(problemas) bigger 0:
    respond 200 json {"dados": void, "erros": problemas}`, lang: 'df' },
  {"p": "A validação percorre a árvore **sem chamar resolvedor nenhum**: nada é lido, nada é escrito. `Lavra.executar` já faz isso por padrão — `validar_antes := no` só existe para quem já validou e guardou a consulta."},
  {"h2": "Os três limites"},
  { code: `Lavra.limites(esq,
    profundidade := 8,      // quantos níveis a consulta pode descer
    complexidade := 1000,   // o custo somado
    itens := 500)           // o teto de uma lista devolvida`, lang: 'df' },
  {"table": {"head": ["Limite", "O que ele impede"], "rows": [["`profundidade`", "`usuario.pedidos.cliente.pedidos…` num grafo com ciclo"], ["`complexidade`", "uma consulta curta que pede um milhão de itens"], ["`itens`", "um resolvedor que devolve a tabela inteira num dia de pico"]]}},
  {"callout": {"tipo": "perigo", "titulo": "Nenhum deles é opcional num servidor público", "texto": "A consulta funda num grafo com ciclo é a forma mais barata de derrubar um servidor de consulta. Ela cabe num tuíte, não exige autenticação em muitos esquemas, e o servidor gasta tudo o que tem antes de responder."}},
  {"p": "Os três são conferidos **antes** de resolver qualquer coisa. Descobrir isso resolvendo já é tarde."},
  {"h2": "Rate limit"},
  {"p": "O limite por consulta não substitui o limite por cliente. Os dois são do [Kiln](/docs/kiln):"},
  { code: `server api on 8080:
    middleware Kiln.rate_limit(60, 60)      // 60 pedidos por minuto, por IP

Lavra.montar(api, esq, "/lavra")`, lang: 'df' },
  {"p": "Sessenta consultas de custo 900 cada passam pelos dois limites e ainda derrubam o banco. Para isso, o limite tem de ser **de custo por janela**, e não de pedidos — o `extensoes.complexidade` de cada resposta é o número que se soma."},
  {"h2": "Introspecção em produção"},
  { code: `Lavra.introspeccao(esq, no)`, lang: 'df' },
  {"p": "Um esquema exposto é um mapa do que existe para quem for procurar: nomes de campos internos, o tipo que só aparece no fluxo de pagamento, o argumento que ninguém deveria descobrir. Quem precisa do esquema é o time, e ele pode lê-lo do repositório."},
  {"callout": {"tipo": "nota", "titulo": "Desligar não é proteger", "texto": "Um campo que existe continua acessível para quem adivinhar o nome. A introspecção desligada só tira o índice; o que protege é o campo **não estar no esquema** ou o resolvedor recusar."}},
  {"h2": "Consultas guardadas"},
  {"p": "Num cliente próprio — um app, um site que você escreve —, a consulta não precisa vir da rede. Guarde as consultas no servidor e aceite só o **nome**:"},
  { code: `consultas := {
    "painel": IO.read("consultas/painel.lavra"),
    "perfil": IO.read("consultas/perfil.lavra"),
}

route POST "/lavra":
    nome := body["nome"] ?? ""
    given nome not in consultas:
        respond 400 json {"erro": "consulta desconhecida"}
    respond json Lavra.executar(esq, consultas[nome],
        variaveis := body["variaveis"] ?? {})`, lang: 'df' },
  {"p": "Isso resolve os três problemas de uma vez: a superfície volta a ser fechada como a de uma API REST, o custo de cada consulta é conhecido, e o corpo do pedido fica pequeno."},
  {"h2": "O que nunca vai para a resposta"},
  {"list": ["**A mensagem de erro do banco.** `Lavra.erro` diz o que quem consulta precisa saber; o resto vai para o registro, com o rastro.", "**O campo que não está no esquema.** É a garantia mais barata que existe.", "**O caminho do arquivo.** Nenhuma mensagem do Lavra cita arquivo nem linha do servidor."]},
  {"h2": "Observabilidade"},
  {"p": "Toda resposta traz `extensoes` — tempo, campos resolvidos, profundidade, custo e o resumo dos lotes. É o que se registra:"},
  { code: `action registrar(r, ctx):
    Log.info("consulta", {
        "ms": r["extensoes"]["ms"],
        "custo": r["extensoes"]["complexidade"],
        "campos": r["extensoes"]["campos"],
        "erros": len(r["erros"]),
        "rastro": Malha.rastro(),
    })`, lang: 'df' },
  {"p": "O **custo** é a métrica que importa, e não o tempo: uma consulta cara que ficou rápida porque o cache estava quente volta a ser cara quando ele esfria."},
];

const headings = [{ id: 'validar-antes-de-executar', text: "Validar antes de executar", level: 2 as const }, { id: 'os-tres-limites', text: "Os três limites", level: 2 as const }, { id: 'rate-limit', text: "Rate limit", level: 2 as const }, { id: 'introspeccao-em-producao', text: "Introspecção em produção", level: 2 as const }, { id: 'consultas-guardadas', text: "Consultas guardadas", level: 2 as const }, { id: 'o-que-nunca-vai-para-a-resposta', text: "O que nunca vai para a resposta", level: 2 as const }, { id: 'observabilidade', text: "Observabilidade", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Segurança"}
      description={"Validação antes de executar, limites de profundidade e custo, rate limit, introspecção e observabilidade."}
      href={"/docs/lavra/seguranca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
