// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Bot de atendimento",
  description: "Um bot de Telegram com menu, conversa em etapas e fallback — testado sem token e sem rede.",
};

const blocos: Bloco[] = [
  {"p": "Um bot que só se testa conversando com ele no celular não tem teste nenhum. `Tg.testar` injeta mensagens e lê o que o bot respondeu, e é isso que permite ter uma suíte para um bot de atendimento com a mesma disciplina de uma API."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`Tg.app` / `mark @app.comando`", "os comandos, como decoradores"], ["`mark @app.texto`", "casar por expressão regular"], ["`V.estado` por conversa (`ctx.estado`)", "a conversa em etapas"], ["`Tg.testar`", "a sonda que finge ser o Telegram"]]}},
  {"h2": "Estrutura"},
  { code: `bot-suporte/
  src/
    bot.df         montar(token) — sem subir nada
    fluxos.df      a conversa de abrir chamado
  main.df          le o token do ambiente e sobe
  tests/
    bot_test.df`, lang: 'text' },
  { code: `[project]
name = "bot-suporte"
version = "0.1.0"
description = "Bot de atendimento"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Arcane.Telegram as Tg

chamados := []

action montar(token):
    app := Tg.app(token)

    mark @app.comando("start")
    action comecar(ctx):
        ctx.responder("Oi! Mande /chamado para abrir um chamado, ou /status.")

    mark @app.comando("chamado")
    action abrir(ctx):
        ctx.estado["etapa"] := "assunto"
        ctx.responder("Qual e o assunto?")

    mark @app.comando("status")
    action status(ctx):
        ctx.responder($"{len(chamados)} chamado(s) aberto(s).")

    mark @app.qualquer()
    action conversa(ctx):
        match ctx.estado["etapa"] ?? "":
            point "assunto":
                ctx.estado["assunto"] := ctx.texto
                ctx.estado["etapa"] := "detalhe"
                ctx.responder("Descreva o problema em uma frase.")
            point "detalhe":
                chamados.append({"assunto": ctx.estado["assunto"], "detalhe": ctx.texto})
                ctx.estado["etapa"] := ""
                ctx.responder($"Chamado #{len(chamados)} aberto.")
            default:
                ctx.responder("Nao entendi. Mande /start.")

    yield app

t := Tg.testar(montar("123456:AAHexemplo"))
t.comando("start")
assert "/chamado" in t.ultima()

t.comando("chamado")
t.mandar("Impressora")
t.mandar("nao imprime frente e verso")
assert t.ultima() is "Chamado #1 aberto."
assert chamados[0]["assunto"] is "Impressora"

t.mandar("ola?")
assert "Nao entendi" in t.ultima()
t.comando("status")
assert t.ultima() is "1 chamado(s) aberto(s)."
out "bot verde"`, lang: 'df', title: `src/bot.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt Arcane.Telegram as Tg
adopt ../src/bot as B

crucible "bot":
    trial "a conversa volta ao comeco depois de abrir":
        t := Tg.testar(B.montar("123456:AAHexemplo"))
        t.comando("chamado")
        t.mandar("a")
        t.mandar("b")
        t.mandar("c")
        expect "Nao entendi" in t.ultima()`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["`montar(token)` devolve o app, não sobe", "o teste sobe um bot que nunca termina"], ["o token vem do ambiente em `main.df`", "o token vai parar no repositório"], ["a etapa mora no estado **da conversa**", "duas pessoas conversando misturam os chamados"], ["`qualquer()` por último", "o fallback engole os comandos"]]}},
  {"h2": "Para ir além"},
  {"list": ["Teclados e botões: [Telegram → teclados](/docs/telegram/teclados).", "Conversas longas: [Telegram → conversas](/docs/telegram/conversas).", "Publicar com webhook: [Telegram → publicar](/docs/telegram/publicar)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Bot de atendimento"}
      description={"Um bot de Telegram com menu, conversa em etapas e fallback — testado sem token e sem rede."}
      href={"/docs/projetos/bot-atendimento"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
