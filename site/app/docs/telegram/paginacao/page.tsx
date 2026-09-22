// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Listas com páginas",
  description: "Um teclado ◀ 2/5 ▶ que edita a mesma mensagem, e o callback velho que não quebra.",
};

const blocos: Bloco[] = [
  {"p": "Uma lista de cem produtos não cabe numa mensagem, e mandar vinte mensagens enterra a conversa. O padrão é **uma** mensagem com um teclado de navegação que a **edita** a cada clique."},
  { code: `adopt Arcane.Telegram as Tg

app := Tg.app("123456:TESTE-exemplo")

produtos := [$"Produto {i}" cycle i in range(1, 13)]

action mostrar(numero):
    yield Tg.paginado(produtos, numero, 5, "prod")

mark @app.comando("catalogo")
action catalogo(ctx):
    p := mostrar(1)
    ctx.responder(p["itens"].join("\\n"), teclado := p["teclado"])

mark @app.botao("^prod:")
action virar(ctx):
    p := mostrar(Tg.ler_pagina(ctx.dados, "prod"))
    ctx.editar(p["itens"].join("\\n"), teclado := p["teclado"])

t := Tg.testar(app)
t.comando("catalogo")
assert t.ultima().starts_with("Produto 1")
assert t.ultimo_teclado()["inline_keyboard"][0][-1]["callback_data"] is "prod:2"

t.clicar("prod:3")
editada := t.chamadas("editMessageText")[-1]
assert editada["texto"].starts_with("Produto 11")`, lang: 'df' },
  {"h2": "Três detalhes"},
  {"list": ["**Editar, e não mandar de novo.** `ctx.editar` troca a mensagem que tinha o teclado; mandar outra deixaria cinco teclados vivos na conversa, cada um mostrando outra página.", "**O callback velho não quebra.** A lista pode encolher entre o envio do teclado e o clique: `paginado` limita a página ao que existe, e o clique em `prod:9` mostra a última.", "**O prefixo separa os teclados.** O mesmo bot tem vários; `Tg.ler_pagina(\"menu:2\", \"prod\")` é `void`, e não a página 2 de outra lista."]},
  {"callout": {"tipo": "atencao", "titulo": "64 bytes por botão", "texto": "O `dados` de um botão tem no máximo 64 **bytes**. Por isso ele leva só a página (`prod:3`), e nunca o filtro, a busca ou o item inteiro: guarde isso em `ctx.estado` e mande só a chave."}},
];

const headings = [{ id: 'tres-detalhes', text: "Três detalhes", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Listas com páginas"}
      description={"Um teclado ◀ 2/5 ▶ que edita a mesma mensagem, e o callback velho que não quebra."}
      href={"/docs/telegram/paginacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
