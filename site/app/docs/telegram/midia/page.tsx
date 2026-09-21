// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Mídia, arquivos e grupos",
  description: "Enviar foto e documento, baixar o que chega, e administrar um grupo.",
};

const blocos: Bloco[] = [
  {"h2": "Enviar"},
  { code: `ctx.responder_foto("relatorio.png", "O gráfico de setembro")
ctx.responder_documento("fechamento.pdf", "Fechamento do mês")

// ou pelo bot, para outro chat:
app.bot.video(outro_chat, "clipe.mp4")
app.bot.enquete(ctx.chat, "Qual prefere?", ["A", "B"], anonima := no)`, lang: 'df' },
  {"p": "Um **`file_id`** ou uma **URL** vão como texto; só o que está em disco (ou em memória) sobe por multipart. Mandar tudo por multipart funcionaria — e reenviaria um arquivo que o Telegram já tem."},
  {"callout": {"tipo": "dica", "titulo": "Guarde o `file_id`", "texto": "Quando um arquivo só vai voltar ao Telegram, guardar o `file_id` que ele devolveu evita as duas chamadas do download e o upload de volta."}},
  {"h2": "\"Digitando…\""},
  { code: `mark @app.comando("relatorio")
action relatorio(ctx):
    ctx.digitando()          // some em 5s, ou quando a mensagem chega
    dados := consulta_demorada()
    ctx.responder(resumo(dados))`, lang: 'df' },
  {"p": "Chamar antes de um trabalho demorado é a diferença entre um bot que parece travado e um que parece pensando."},
  {"h2": "Baixar"},
  { code: `mark @app.midia("documento")
action recebeu(ctx):
    arquivo := ctx.mensagem["document"]
    caminho := app.bot.baixar(arquivo["file_id"], $"/tmp/{arquivo['file_name']}")
    ctx.responder($"Salvei em {caminho}")`, lang: 'df' },
  {"p": "São **duas** chamadas por baixo: `getFile` devolve um caminho temporário, e o download é num endereço diferente. Arquivos acima de 20 MB não podem ser baixados pela Bot API, e a mensagem diz isso."},
  {"h2": "Grupos"},
  {"table": {"head": ["", ""], "rows": [["`bot.e_admin(chat, usuario)`", "a pergunta mais comum, já pronta"], ["`bot.banir` · `bot.desbanir` · `bot.silenciar`", "moderação"], ["`bot.fixar` · `bot.desafixar`", "mensagem fixada"], ["`bot.chat(id)` · `bot.membro(chat, id)`", "o que o Telegram sabe"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Em grupo, o bot só vê comandos — por padrão", "texto": "A privacidade vem **ligada** no @BotFather: o bot recebe apenas mensagens que começam com `/` ou que o citam. Em privado tudo funciona, e no grupo ele parece mudo. `dataforge telegram doctor` pergunta isso ao Telegram e diz como desligar."}},
  {"h2": "O que o módulo não embrulha"},
  { code: `Tg.chamar(token, "setChatTitle",
          {"chat_id": -100123, "title": "Novo nome"})

// ou, com o bot aberto:
app.bot.chamar("setChatPhoto", {"chat_id": ctx.chat}, arquivos := {"photo": "logo.png"})`, lang: 'df' },
  {"p": "A Bot API cresce, e um módulo que só oferece o que ele conhece envelhece no dia seguinte. `chamar` é a porta para qualquer método, com o mesmo tratamento de erro e de limite de taxa."},
];

const headings = [{ id: 'enviar', text: "Enviar", level: 2 as const }, { id: 'digitando', text: "\"Digitando…\"", level: 2 as const }, { id: 'baixar', text: "Baixar", level: 2 as const }, { id: 'grupos', text: "Grupos", level: 2 as const }, { id: 'o-que-o-modulo-nao-embrulha', text: "O que o módulo não embrulha", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Mídia, arquivos e grupos"}
      description={"Enviar foto e documento, baixar o que chega, e administrar um grupo."}
      href={"/docs/telegram/midia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
