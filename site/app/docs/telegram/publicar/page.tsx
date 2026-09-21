// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Publicar o bot",
  description: "Long polling contra webhook, o segredo do cabeçalho, e por que `deploy` não existe.",
};

const blocos: Bloco[] = [
  {"h2": "Os dois modos"},
  {"table": {"head": ["", "Long polling", "Webhook"], "rows": [["como", "o bot pergunta ao Telegram", "o Telegram chama o bot"], ["exige", "só saída para a internet", "HTTPS com certificado **válido**"], ["custo", "uma conexão aberta o tempo todo", "nada enquanto ninguém fala"], ["quando", "desenvolvimento, e bots pequenos", "produção"]]}},
  {"p": "Os dois passam pelo **mesmo caminho** por dentro: `atender` recebe um update e não sabe de onde ele veio. Sem isso, um bot testado em polling quebra ao virar webhook — que é justamente quando ele vai para produção."},
  {"h2": "Webhook"},
  { code: `app.publicar("https://bot.seudominio.dev",
             porta := 8443,
             segredo := Tg.segredo_do_ambiente("WEBHOOK_SEGREDO"))`, lang: 'df' },
  {"p": "Ou em dois passos, quando o servidor já existe: `dataforge telegram webhook https://bot.seudominio.dev` registra, e `app.montar(\"/telegram\", segredo)` devolve um app Kiln para você montar onde quiser."},
  {"callout": {"tipo": "atencao", "titulo": "Use o segredo", "texto": "Sem ele, qualquer um que descubra a URL manda updates falsos para o seu bot — e a URL vaza em log de proxy, em print de tela, em qualquer lugar. O módulo confere o cabeçalho `X-Telegram-Bot-Api-Secret-Token` e responde 403 quando não bate."}},
  {"p": "O webhook responde **200 sempre**, mesmo quando o tratador falha: o Telegram reenvia o update quando a resposta demora ou dá erro, e isso faria o mesmo comando rodar três vezes."},
  {"h2": "Quando o bot fica calado"},
  { code: `dataforge telegram doctor`, lang: 'bash' },
  {"p": "Um bot que não responde não dá erro — ele simplesmente fica calado, e as causas são sempre as mesmas:"},
  {"table": {"head": ["O que o doctor pergunta", "O que costuma ser"], "rows": [["o Telegram aceita o token?", "token revogado, ou com espaço em volta"], ["há webhook registrado?", "ele e o polling **não convivem** — o `getUpdates` responde 409 para sempre"], ["o bot lê tudo em grupo?", "a privacidade vem ligada: ele só vê `/comandos` e menções"], ["o bot entra em grupos?", "`/setjoingroups` no @BotFather"], ["quantos updates estão na fila?", "o servidor do webhook não está respondendo 200"]]}},
  {"h2": "Ritmo"},
  { code: `app := Tg.app(Tg.segredo_do_ambiente(),
              limitador := Tg.limitar(por_segundo := 25,
                                      por_chat_por_minuto := 18))`, lang: 'df' },
  {"p": "O Telegram corta acima de ~30 mensagens por segundo, e num grupo o limite é de cerca de 20 por minuto. Segurar aqui custa milissegundos; ser bloqueado custa minutos — e o `retry_after` que ele devolve é obedecido ao pé da letra, porque repetir antes dele só gasta a cota."},
  {"h2": "`deploy` não existe — de propósito"},
  {"p": "Registrar o webhook é do bot, e isso existe. **Onde** essa URL vai morar — Docker, systemd, uma PaaS, um túnel — é uma opinião sobre infraestrutura que o projeto não tem, pelo mesmo motivo que `dataforge vitrine deploy` não existe."},
  { code: `dataforge devops docker --porta=8443     # o Dockerfile
dataforge telegram doctor                # o que falta
GET <caminho>/saude                      # métricas e erros`, lang: 'bash' },
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/telegram", "title": "Visão geral", "desc": "O bot inteiro em oito linhas."}, {"href": "/docs/telegram/testes", "title": "Testar sem rede", "desc": "A sonda injeta updates e lê as respostas."}, {"href": "/docs/devops", "title": "DevOps", "desc": "Dockerfile, compose, CI e manifestos."}, {"href": "/docs/kiln", "title": "Kiln", "desc": "O servidor HTTP que atende o webhook."}]},
];

const headings = [{ id: 'os-dois-modos', text: "Os dois modos", level: 2 as const }, { id: 'webhook', text: "Webhook", level: 2 as const }, { id: 'quando-o-bot-fica-calado', text: "Quando o bot fica calado", level: 2 as const }, { id: 'ritmo', text: "Ritmo", level: 2 as const }, { id: 'deploy-nao-existe-de-proposito', text: "`deploy` não existe — de propósito", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Publicar o bot"}
      description={"Long polling contra webhook, o segredo do cabeçalho, e por que `deploy` não existe."}
      href={"/docs/telegram/publicar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
