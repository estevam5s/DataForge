// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ritmo e limites do Telegram",
  description: "30 mensagens por segundo, 20 por minuto num grupo, e o 429 que bloqueia por minutos.",
};

const blocos: Bloco[] = [
  {"p": "O Telegram corta o bot que envia rápido demais, e o corte não é uma mensagem perdida: é um **429** com `retry_after` que pode passar de um minuto, e nesse intervalo o bot não responde **ninguém**."},
  {"table": {"head": ["Limite", "Aproximado", "O que estoura"], "rows": [["mensagens no total", "~30 por segundo", "um aviso para todos os assinantes num laço"], ["num mesmo grupo", "~20 por minuto", "um bot que responde toda mensagem de um grupo ativo"], ["num mesmo chat privado", "~1 por segundo", "uma resposta dividida em vinte partes"]]}},
  {"p": "`Tg.limitar` segura o ritmo **antes** de enviar — esperar alguns milissegundos custa menos que ser bloqueado por minutos:"},
  { code: `adopt Arcane.Telegram as Tg

lim := Tg.limitar(50, 18)             // até 50 por segundo, e 18 por minuto por chat
inicio := time()
cycle i in range(10):
    lim.esperar(1001)
decorrido := time() - inicio
assert decorrido bigger_eq 0.15       // dez envios a 50/s: ao menos 180 ms`, lang: 'df' },
  {"h2": "Aviso para todos os assinantes"},
  {"p": "O caso que mais estoura é o *broadcast*: mil assinantes num laço sem pausa. Com o limitador, o laço leva o tempo que o Telegram aceita — e numa [fila](/docs/biblioteca/eventos), ele não segura o tratador que disparou o aviso."},
  { code: `adopt Arcane.Telegram as Tg

app := Tg.app("123456:TESTE-exemplo")

assinantes := [1001, 1002, 1003]
lim := Tg.limitar(25, 18)

action avisar_todos(texto):
    cycle chat in assinantes:
        lim.esperar(chat)
        app.bot.enviar(chat, texto)

t := Tg.testar(app)
avisar_todos("Manutenção às 22h.")
assert t.quantas("sendMessage") is 3`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O bloqueio pelo usuário", "texto": "Quem bloqueia o bot faz todo envio a ele falhar com **403**. No broadcast, isso não é erro do bot: anote e tire o chat da lista, senão cada aviso futuro gasta uma chamada — e o ritmo — num chat que nunca vai receber."}},
];

const headings = [{ id: 'aviso-para-todos-os-assinantes', text: "Aviso para todos os assinantes", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ritmo e limites do Telegram"}
      description={"30 mensagens por segundo, 20 por minuto num grupo, e o 429 que bloqueia por minutos."}
      href={"/docs/telegram/ritmo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
