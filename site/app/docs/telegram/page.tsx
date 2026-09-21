// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Bots de Telegram",
  description: "Comandos, botões, conversa com estado e webhook — e testes que rodam sem token e sem rede.",
};

const blocos: Bloco[] = [
  {"p": "**`Arcane.Telegram`** é o módulo de bots. A Bot API do Telegram é HTTP com JSON: falar com ela do zero é possível e chato — noventa métodos, um formato de erro próprio, um limite de taxa que responde no **corpo** e não no status, upload multipart, e uma sintaxe de formatação que quebra a mensagem inteira se um caractere escapar."},
  { code: `adopt Arcane.Telegram as Tg

app := Tg.app(Tg.segredo_do_ambiente())

mark @app.comando("start")
action comecar(ctx):
    ctx.responder($"Ola, {ctx.nome()}!")

app.rodar()`, lang: 'df' },
  {"p": "Isso é o bot inteiro. `ctx` traz quem falou, o que disse e como responder; o `rodar` faz long polling até alguém parar."},
  {"h2": "Do zero ao bot no ar"},
  { code: `dataforge telegram new meubot     # cria o projeto
cd meubot
export TELEGRAM_TOKEN="123456:AAH..."   # o token vem do @BotFather
dataforge telegram doctor         # confere o que falta
dataforge telegram run            # sobe em long polling`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "O token nunca vai no código", "texto": "Ele vai para o Git, e do Git para qualquer um — e o @BotFather não avisa quando alguém o usa: o bot só começa a mandar spam. `Tg.segredo_do_ambiente()` lê de `$TELEGRAM_TOKEN` e falha dizendo o que fazer quando a variável está vazia."}},
  {"p": "O módulo também nunca deixa o token aparecer numa mensagem de erro. Ele está na URL de toda chamada, e a URL entra em todo traceback — um token num log de CI é um bot sequestrado."},
  {"h2": "O que chega em `ctx`"},
  {"table": {"head": ["", "O que é"], "rows": [["`ctx.texto`", "o texto da mensagem, ou a legenda da mídia"], ["`ctx.args`", "o que veio depois do comando, já separado"], ["`ctx.dados`", "o `dados` do botão que foi clicado"], ["`ctx.chat`", "o id do chat"], ["`ctx.nome()` · `ctx.apelido()`", "quem falou"], ["`ctx.e_privado()` · `ctx.e_grupo()` · `ctx.e_admin()`", "onde, e com que poder"], ["`ctx.estado`", "o vault **deste chat**, que sobrevive entre mensagens"], ["`ctx.update`", "o update cru, para o campo que nenhuma conveniência cobre"]]}},
  {"p": "E para responder: `ctx.responder`, `ctx.citar` (que responde **citando**, o que dá contexto em grupo), `ctx.responder_foto`, `ctx.responder_documento`, `ctx.editar`, `ctx.apagar`, `ctx.digitando` e `ctx.avisar`."},
  {"h2": "O despacho para no primeiro que casa"},
  {"p": "O update é casado **uma vez**, na ordem do registro. A alternativa — entregar a todos — parece mais flexível e produz o bug mais confuso que um bot tem: duas respostas para uma mensagem, e ninguém sabe de onde veio a segunda."},
  { code: `mark @app.comando("start")
action comecar(ctx):
    ctx.responder("Ola!")

mark @app.texto("\\\\b(oi|ola)\\\\b")
action cumprimento(ctx):
    ctx.responder("Oi!")

mark @app.qualquer()
action resto(ctx):
    ctx.responder("Nao entendi.")`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "`qualquer` vai por último — e isso é cobrado", "texto": "Ela casa com tudo. Uma rota registrada **depois** dela nunca seria alcançada, e o sintoma é o bot responder \"não entendi\" a um comando que existe. Registrar nessa ordem é **recusado**, na partida: é a mesma classe do `point` inalcançável que o `check` acusa na linguagem."}},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/telegram/comandos", "title": "Comandos e roteamento", "desc": "Comando, texto, botão, mídia, consulta inline e middleware."}, {"href": "/docs/telegram/teclados", "title": "Teclados e formatação", "desc": "Botões, o teclado do celular, e o escape que salva a mensagem."}, {"href": "/docs/telegram/conversas", "title": "Conversas e estado", "desc": "A máquina de estados por chat, e onde ela mora."}, {"href": "/docs/telegram/testes", "title": "Testar sem rede", "desc": "A sonda injeta updates e lê o que o bot mandou."}, {"href": "/docs/telegram/publicar", "title": "Publicar", "desc": "Webhook, HTTPS, e por que `deploy` não existe."}]},
];

const headings = [{ id: 'do-zero-ao-bot-no-ar', text: "Do zero ao bot no ar", level: 2 as const }, { id: 'o-que-chega-em-ctx', text: "O que chega em `ctx`", level: 2 as const }, { id: 'o-despacho-para-no-primeiro-que-casa', text: "O despacho para no primeiro que casa", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Bots de Telegram"}
      description={"Comandos, botões, conversa com estado e webhook — e testes que rodam sem token e sem rede."}
      href={"/docs/telegram"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
