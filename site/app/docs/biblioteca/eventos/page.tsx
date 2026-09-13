// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/plataforma.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Eventos",
  description: "Publicar e assinar sem as duas partes se conhecerem, contexto por thread e fila de trabalho.",
};

const blocos: Bloco[] = [
  {"p": "Duas partes de um programa que precisam conversar sem se conhecer. O Kiln tem `Sala` para WebSocket e o [Lavra](/docs/lavra) tem `Fonte` para assinatura — os dois resolvem o mesmo problema para um transporte específico, e faltava a peça geral."},
  {"h2": "Emissor"},
  { code: `adopt Arcane.Eventos as Eventos

loja := Eventos.emissor("loja")

loja.ao("venda", lambda pedido: gravar_nota(pedido))
loja.ao("venda", lambda pedido: avisar_estoque(pedido))

quantos := loja.emitir("venda", pedido)`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "`emitir` devolve quantos ouviram", "texto": "Zero é **informação**: o evento com o nome errado não falha, ele simplesmente não chega — e essa é a falha mais difícil de achar num sistema de eventos."}},
  {"h2": "O ouvinte que quebra sai"},
  {"p": "Um ouvinte quebrado que continua inscrito quebra **a cada evento**, para sempre, e some no meio do log. Ele é removido, e o erro vai para a lista:"},
  { code: `out loja.erros            // [{evento: venda, erro: …, quando: …}]
out loja.resumo()         // {emitidos: 12, entregues: 20, ouvintes: {…}, erros: 1}`, lang: 'df' },
  {"h2": "Curinga e uma vez"},
  { code: `loja.ao("*", lambda nome: registrar(nome))        // ouve tudo
loja.uma_vez("pronto", lambda: comecar())         // ouve o próximo, e sai

cancelar := loja.ao("venda", tratar)
cancelar()                                        // desinscreve`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Inscrever dentro de um laço é recusado", "texto": "Mil ouvintes no mesmo evento quase sempre significa um `ao(...)` dentro de um laço ou de um handler — cada volta inscreve mais um, e nenhum sai. O erro diz isso, em vez de deixar a memória crescer."}},
  {"h2": "O contexto atravessa as camadas"},
  {"p": "O id do pedido, quem pediu, o rastro — sem passar por parâmetro em cada camada:"},
  { code: `action atender(req):
    yield Eventos.com_contexto({"pedido": req["id"], "quem": req["usuario"]},
        lambda => processar())

// dez camadas abaixo, sem ter recebido nada
action gravar_log(texto):
    Log.info(texto, {"pedido": Eventos.por("pedido")})`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "É por thread, e tem de ser", "texto": "Um vault global serviria até o segundo pedido simultâneo — e aí o id de um apareceria no log do outro. O Kiln atende **um pedido por thread**, então o contexto é por thread."}},
  {"h2": "Fila de trabalho"},
  {"p": "A diferença para o emissor: o emissor entrega **agora**, na thread de quem emitiu. A fila aceita e devolve o controle — quem publicou não espera o trabalho terminar."},
  { code: `envios := Eventos.fila(lambda mensagem: Email.enviar(mensagem, servidor),
    operarios := 4)

route POST "/cadastro":
    criar(body)
    envios.publicar(boas_vindas(body["email"]))    // não espera
    respond 201 json {"ok": yes}`, lang: 'df' },
  { code: `envios.esperar(prazo := 5.0)     // num teste: espera esvaziar
out envios.resumo()              // {feitos: 40, falhos: 0, pendentes: 0, operarios: 4}`, lang: 'df' },
];

const headings = [{ id: 'emissor', text: "Emissor", level: 2 as const }, { id: 'o-ouvinte-que-quebra-sai', text: "O ouvinte que quebra sai", level: 2 as const }, { id: 'curinga-e-uma-vez', text: "Curinga e uma vez", level: 2 as const }, { id: 'o-contexto-atravessa-as-camadas', text: "O contexto atravessa as camadas", level: 2 as const }, { id: 'fila-de-trabalho', text: "Fila de trabalho", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Eventos"}
      description={"Publicar e assinar sem as duas partes se conhecerem, contexto por thread e fila de trabalho."}
      href={"/docs/biblioteca/eventos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
