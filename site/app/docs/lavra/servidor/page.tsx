// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O servidor",
  description: "Servir o esquema por HTTP, assinaturas por WebSocket, e o cliente que consulta outro serviço.",
};

const blocos: Bloco[] = [
  {"p": "O servidor do Lavra é o **Kiln**. HTTP, rotas, CORS, sessão, cabeçalhos de segurança e WebSocket já existem lá, testados — reimplementá-los aqui criaria duas implementações do mesmo protocolo para divergirem."},
  {"h2": "Montar num app que já existe"},
  { code: `adopt Kiln
adopt Arcane.Lavra as Lavra

server api on 8080:
    route GET "/saude":
        respond json {"ok": yes}

Lavra.montar(api, esq, "/lavra")
ignite api`, lang: 'df' },
  {"table": {"head": ["Rota", "O que faz"], "rows": [["`POST /lavra`", "executa a consulta"], ["`GET /lavra`", "devolve o esquema em texto"], ["`WS /lavra/assinar`", "as assinaturas"]]}},
  {"p": "**Uma rota, um método.** Não há uma rota por busca: a consulta já diz o que quer, e uma rota por campo desfaria a razão de o Lavra existir."},
  {"h2": "O corpo do pedido"},
  { code: `{
  "consulta": "busca:
    usuario(id: $id):
        nome",
  "variaveis": {"id": 7},
  "operacao": "Painel"
}`, lang: 'json' },
  {"p": "`operacao` só é preciso quando o documento tem mais de uma. Com uma só, ela é a escolhida."},
  {"h2": "Erro de consulta responde 200"},
  {"p": "Parece errado e não é: o **HTTP falou**, e a resposta tem `dados` e `erros`. Um 400 obrigaria o cliente a ter dois caminhos de leitura para o mesmo corpo, e esconderia o caso normal — dados parciais com um erro num campo."},
  {"table": {"head": ["Status", "Quando"], "rows": [["`200`", "a consulta foi lida — com ou sem erro nos campos"], ["`400`", "o corpo nem chegou a ser consulta (ilegível, sem `consulta`)"], ["`500`", "quebrou fora da consulta"]]}},
  {"h2": "O contexto vem do pedido"},
  { code: `action contexto_de(req):
    yield {
        "usuario": autenticar(req["headers"]["authorization"] ?? ""),
        "banco": conexao,
        "ip": req["ip"],
    }

Lavra.montar(api, esq, "/lavra", contexto_de := contexto_de)`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Os cabeçalhos chegam em minúsculas", "texto": "`req[\"headers\"][\"authorization\"]`, e não `\"Authorization\"`. O Kiln normaliza, porque o HTTP não distingue maiúscula em nome de cabeçalho — e quem escreve a leitura com a maiúscula recebe `void` sem nada explicando."}},
  {"h2": "Um servidor só para o esquema"},
  { code: `Lavra.servir(esq, porta := 8080, contexto_de := contexto_de)`, lang: 'df' },
  {"p": "Sobe e bloqueia. Para teste, `Lavra.em_segundo_plano` devolve `(app, porta)` e não bloqueia:"},
  { code: `par := Lavra.em_segundo_plano(esq)
app := par[0]
porta := par[1]
defer:
    Lavra.parar(app)`, lang: 'df' },
  {"h2": "Assinaturas"},
  {"p": "Uma assinatura é o servidor **empurrando** cada novo valor. O transporte é WebSocket, e o formato de cada mensagem é o mesmo de uma resposta comum."},
  { code: `novos := Lavra.fonte("pedidos")

action pedido_criado(raiz, args, ctx):
    yield novos

Lavra.assinatura(esq, "pedidoCriado", "Pedido!", resolve := pedido_criado)
Lavra.montar_assinaturas(api, esq, "/lavra/assinar")`, lang: 'df' },
  {"p": "Quando um pedido nasce, quem publica é o código que o criou:"},
  { code: `action criar_pedido(raiz, args, ctx):
    novo := Banco.inserir(ctx["banco"], "pedidos", args["dados"])
    _ := novos.publicar(novo)
    yield novo`, lang: 'df' },
  { code: `assinatura:
    pedidoCriado:
        numero
        total
        cliente:
            nome`, lang: 'lavra' },
  {"p": "Repare que a assinatura **também é uma consulta**: cada evento passa pelo mesmo esquema, com os mesmos resolvedores e o mesmo lote. Quem acompanha escolhe os campos, como em qualquer outra operação."},
  {"h3": "Por que uma Fonte, e não um generator"},
  {"p": "Um generator serve **um** consumidor, e uma assinatura tem muitos. Publicar num generator obrigaria a manter um por conexão, o que multiplica o trabalho pelo número de pessoas com a aba aberta. A `Fonte` é uma fila com assinantes: publica-se uma vez, e ela entrega a todos."},
  {"callout": {"tipo": "atencao", "titulo": "Um assinante morto não derruba os outros", "texto": "Quem fechou a aba é removido da lista no momento em que a entrega falha — a mesma regra da `Sala` do Kiln. Sem isso, uma conexão zumbi levaria a mensagem de todo mundo junto."}},
  {"callout": {"tipo": "dica", "titulo": "Quando SSE é melhor", "texto": "Se o cliente só **ouve**, prefira `Kiln.sse`: é HTTP comum, reconecta sozinho e passa em qualquer proxy. O WebSocket ganha quando os dois lados falam."}},
  {"h2": "Consultar outro serviço"},
  { code: `c := Lavra.cliente("http://contas.interno/lavra",
    cabecalhos := {"Authorization": $"Bearer {token}"})

r := c.consultar("""
busca Um($id: Integer!):
    usuario(id: $id):
        nome
""", {"id": 7})

out r["dados"]["usuario"]["nome"]`, lang: 'df' },
  {"p": "O cliente é fino de propósito: monta o corpo, chama a [Malha](/docs/tecnicas/microservicos) e lê a resposta. Retentativa com recuo, disjuntor, propagação de rastro e idempotência já estão resolvidos lá."},
  {"callout": {"tipo": "atencao", "titulo": "status 0 é o caso honesto", "texto": "Uma chamada de rede tem três desfechos, e o terceiro é **não se sabe**. O cliente devolve um erro de código `rede` nesse caso, em vez de dizer que falhou — colapsar os dois faria quem chama repetir uma cobrança."}},
  {"h2": "Testar sem socket"},
  { code: `c := Lavra.local(esq)

dados := c.dados("""
busca:
    usuario(id: 1):
        nome
""")

assert dados["usuario"]["nome"] is "Ana"`, lang: 'df' },
  {"p": "`Lavra.local` tem o **mesmo contrato** do cliente remoto, sem rede. É o que torna barato o teste de quem consome — e o que permite trocar um pelo outro sem mudar o código que usa."},
];

const headings = [{ id: 'montar-num-app-que-ja-existe', text: "Montar num app que já existe", level: 2 as const }, { id: 'o-corpo-do-pedido', text: "O corpo do pedido", level: 2 as const }, { id: 'erro-de-consulta-responde-200', text: "Erro de consulta responde 200", level: 2 as const }, { id: 'o-contexto-vem-do-pedido', text: "O contexto vem do pedido", level: 2 as const }, { id: 'um-servidor-so-para-o-esquema', text: "Um servidor só para o esquema", level: 2 as const }, { id: 'assinaturas', text: "Assinaturas", level: 2 as const }, { id: 'por-que-uma-fonte-e-nao-um-generator', text: "Por que uma Fonte, e não um generator", level: 3 as const }, { id: 'consultar-outro-servico', text: "Consultar outro serviço", level: 2 as const }, { id: 'testar-sem-socket', text: "Testar sem socket", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O servidor"}
      description={"Servir o esquema por HTTP, assinaturas por WebSocket, e o cliente que consulta outro serviço."}
      href={"/docs/lavra/servidor"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
