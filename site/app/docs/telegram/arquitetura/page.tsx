// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Um bot que cresce",
  description: "O bot como casca: a regra num módulo, o estado fora da memória, e o teste que não precisa do Telegram.",
};

const blocos: Bloco[] = [
  {"p": "O primeiro bot é um arquivo só, e está certo assim. O segundo mês traz um banco, três tipos de usuário e um relatório — e aí o arquivo único mistura **o que o bot faz** com **como o Telegram recebe**, e nenhum dos dois se testa sozinho."},
  {"table": {"head": ["Camada", "Sabe de", "Não sabe de"], "rows": [["o **núcleo** (`pedidos.df`)", "a regra: o que é um pedido válido, o total, o estado", "Telegram, `ctx`, teclado"], ["o **bot** (`bot.df`)", "comandos, teclados, a conversa", "como se calcula o total"], ["o **estado**", "onde a conversa mora entre mensagens", "o que ela significa"]]}},
  { code: `adopt Arcane.Telegram as Tg

app := Tg.app("123456:TESTE-exemplo")

// o núcleo: nada aqui sabe que existe um Telegram
action total(itens):
    yield itens >> distill acc, i: acc + i["preco"] * i["qtd"] 0

// a casca: traduz mensagem em chamada, e resultado em texto
mark @app.comando("total")
action comando_total(ctx):
    carrinho := ctx.lembrar("carrinho", [])
    ctx.responder($"Total: R$ {total(carrinho)}")

mark @app.comando("pegar")
action pegar(ctx):
    carrinho := ctx.lembrar("carrinho", [])
    carrinho.append({"preco": 10, "qtd": 2})
    ctx.guardar("carrinho", carrinho)
    ctx.responder("Adicionado.")

assert total([{"preco": 10, "qtd": 3}]) is 30   // o núcleo, sem bot

t := Tg.testar(app)
t.comando("pegar")
t.comando("total")
assert t.ultima() is "Total: R$ 20"`, lang: 'df' },
  {"h2": "O estado fora da memória"},
  {"p": "`Tg.estado_em_memoria()` some quando o processo reinicia — e o bot reinicia a cada deploy. Para produção, `Tg.estado_em_arquivo(caminho)`, e o carrinho de quem estava no meio de uma compra sobrevive à atualização."},
  {"p": "O projeto completo nesse formato está em [Bot de atendimento](/docs/projetos/bot-atendimento)."},
];

const headings = [{ id: 'o-estado-fora-da-memoria', text: "O estado fora da memória", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Um bot que cresce"}
      description={"O bot como casca: a regra num módulo, o estado fora da memória, e o teste que não precisa do Telegram."}
      href={"/docs/telegram/arquitetura"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
