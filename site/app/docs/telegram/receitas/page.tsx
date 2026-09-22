// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Receitas de bot",
  description: "Lembrete, enquete de um toque, menu de confirmação e resposta a documento — cada uma testada.",
};

const blocos: Bloco[] = [
  {"h2": "Confirmar antes de agir"},
  { code: `adopt Arcane.Telegram as Tg

app := Tg.app("123456:TESTE-exemplo")

mark @app.comando("cancelar_pedido")
action pedir_confirmacao(ctx):
    ctx.responder("Cancelar o pedido 77?", teclado := Tg.botoes([[
        Tg.botao("Sim, cancelar", dados := "cancelar:77:sim"),
        Tg.botao("Não", dados := "cancelar:77:nao")]]))

mark @app.botao("^cancelar:")
action decidir(ctx):
    partes := ctx.dados.split(":")
    ctx.editar("Pedido cancelado." given partes[2] is "sim" otherwise "Nada foi feito.")

t := Tg.testar(app)
t.comando("cancelar_pedido")
t.clicar("cancelar:77:nao")
assert t.chamadas("editMessageText")[-1]["texto"] is "Nada foi feito."`, lang: 'df' },
  {"h2": "Enquete de um toque"},
  { code: `adopt Arcane.Telegram as Tg

app := Tg.app("123456:TESTE-exemplo")

votos := {"sim": 0, "nao": 0}

mark @app.comando("enquete")
action enquete(ctx):
    ctx.responder("Almoço às 12h?", teclado := Tg.botoes([[
        Tg.botao("👍", dados := "voto:sim"), Tg.botao("👎", dados := "voto:nao")]]))

mark @app.botao("^voto:")
action votar(ctx):
    escolha := ctx.dados.split(":")[1]
    votos[escolha] += 1
    ctx.editar($"Almoço às 12h?  👍 {votos["sim"]}  👎 {votos["nao"]}")

t := Tg.testar(app)
t.comando("enquete")
t.clicar("voto:sim")
t.clicar("voto:sim")
assert votos["sim"] is 2`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Um voto por pessoa", "texto": "A enquete acima conta dois cliques da mesma pessoa. Para um voto por pessoa, guarde `ctx.id_do_usuario()` num conjunto — `{…}` — e confira antes de somar. E duas pessoas clicando ao mesmo tempo escrevem no mesmo vault: com o bot atendendo em threads, use um [ator](/docs/concorrencia/atores)."}},
];

const headings = [{ id: 'confirmar-antes-de-agir', text: "Confirmar antes de agir", level: 2 as const }, { id: 'enquete-de-um-toque', text: "Enquete de um toque", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Receitas de bot"}
      description={"Lembrete, enquete de um toque, menu de confirmação e resposta a documento — cada uma testada."}
      href={"/docs/telegram/receitas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
