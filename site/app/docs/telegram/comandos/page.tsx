// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Comandos e roteamento",
  description: "As sete formas de casar um update, o middleware e o tratador de erro.",
};

const blocos: Bloco[] = [
  {"h2": "Comando"},
  { code: `mark @app.comando("start", ajuda := "Comeca a conversa")
action comecar(ctx):
    ctx.responder("Ola!")

mark @app.comando(["ajuda", "help"])
action ajudar(ctx):
    ctx.responder("Mande /cadastro.")`, lang: 'df' },
  {"p": "Ele casa com `/nome`, com `/nome argumento` e com **`/nome@meubot`** — a última forma é a que o Telegram usa em grupo, e um bot que não a trata parece mudo lá dentro, funcionando em privado."},
  {"p": "O `ajuda` alimenta `app.publicar_comandos()`, que manda o menu ao Telegram. Sem o menu, a lista que aparece ao digitar `/` vem vazia, e um bot sem menu parece quebrado."},
  {"h2": "Texto, botão e mídia"},
  { code: `mark @app.texto("^preco de (.+)$")
action preco(ctx):
    ctx.responder("Consultando…")

mark @app.botao("^comprar:(\\\\d+)$")
action comprar(ctx):
    ctx.avisar("Adicionado!")
    ctx.editar("Pedido atualizado.")

mark @app.midia("foto")
action recebeu_foto(ctx):
    ctx.responder("Foto recebida.")`, lang: 'df' },
  {"p": "O `texto` recebe uma expressão regular, ou nada para casar qualquer texto — e ele **nunca** casa uma mensagem que começa com `/`: um tratador de texto que engolisse comandos faria todo comando novo parar de funcionar."},
  {"callout": {"tipo": "atencao", "titulo": "`ctx.avisar()` é obrigatório num botão", "texto": "Sem ele, o Telegram deixa o botão com o relógio girando por até um minuto, e quem clicou conclui que o bot travou. Chame sempre, mesmo sem texto."}},
  {"p": "As espécies de mídia: `foto`, `documento`, `voz`, `video`, `audio`, `adesivo`, `local`, `contato`, `animacao` e `enquete`. Uma espécie que não existe é recusada na hora, listando as que existem."},
  {"h2": "Entrou, saiu, consulta inline"},
  { code: `mark @app.entrou()
action boas_vindas(ctx):
    ctx.responder("Bem-vindo ao grupo!")

mark @app.inline()
action buscar(ctx):
    ctx.bot.responder_inline(ctx.consulta["id"], resultados_de(ctx.texto))`, lang: 'df' },
  {"h2": "Middleware"},
  { code: `mark @app.antes_de_cada()
action so_assinantes(ctx):
    given not assinante(ctx.id_do_usuario()):
        ctx.responder("Isto e so para assinantes.")
        yield no        // 'no' interrompe: nenhum tratador roda

mark @app.depois_de_cada()
action registrar(ctx):
    Log.info($"{ctx.tipo} de {ctx.chat}")`, lang: 'df' },
  {"p": "Devolver `no` no `antes_de_cada` interrompe o update — é como se faz uma barreira sem espalhar um `given` por todos os tratadores."},
  {"h2": "Quando algo quebra"},
  { code: `mark @app.ao_falhar()
action deu_errado(ctx, erro):
    out $"[bot] {erro}"
    ctx.responder("Alguma coisa quebrou aqui. Ja anotei.")`, lang: 'df' },
  {"p": "Um erro num tratador **não derruba o bot**: ele é anotado, o tratador de erro roda, e o próximo update é atendido. Um bot que morre porque alguém mandou um emoji inesperado é um bot que fica fora do ar de madrugada."},
  {"p": "Um tratador de erro que também falha não entra em laço: a linha para ali, e o bot segue vivo."},
];

const headings = [{ id: 'comando', text: "Comando", level: 2 as const }, { id: 'texto-botao-e-midia', text: "Texto, botão e mídia", level: 2 as const }, { id: 'entrou-saiu-consulta-inline', text: "Entrou, saiu, consulta inline", level: 2 as const }, { id: 'middleware', text: "Middleware", level: 2 as const }, { id: 'quando-algo-quebra', text: "Quando algo quebra", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Comandos e roteamento"}
      description={"As sete formas de casar um update, o middleware e o tratador de erro."}
      href={"/docs/telegram/comandos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
