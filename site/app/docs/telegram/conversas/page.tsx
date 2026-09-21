// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Conversas e estado",
  description: "A máquina de estados por chat, a validação passo a passo, e onde o estado mora.",
};

const blocos: Bloco[] = [
  {"p": "Guardar \"em que passo este chat está\" num vault solto é o que todo bot faz errado: funciona até o segundo usuário, os dois se misturam, e um bot reiniciado esquece todo mundo."},
  {"h2": "Uma conversa"},
  { code: `action e_email(texto):
    yield "@" in texto and "." in texto

cadastro := app.conversa("cadastro", [
    {"pergunta": "Qual e o seu nome?", "guarda": "nome"},
    {"pergunta": "E o seu e-mail?", "guarda": "email",
     "valida": e_email, "erro": "Isso nao parece um e-mail."}
])

mark @cadastro.ao_terminar()
action terminou(ctx, respostas):
    salvar(respostas["nome"], respostas["email"])
    ctx.responder($"Pronto, {respostas['nome']}!")

mark @app.comando("cadastro")
action abrir(ctx):
    cadastro.comecar(ctx)`, lang: 'df' },
  {"p": "Cada passo pergunta, espera, valida e guarda. O estado fica **no chat**, então duas pessoas conversando ao mesmo tempo não se atrapalham."},
  {"callout": {"tipo": "dica", "titulo": "Um comando sempre escapa da conversa", "texto": "Qualquer mensagem que comece com `/` encerra a conversa aberta e cai no tratador do comando. Sem isso, quem se perde no meio de um cadastro não consegue nem mandar `/cancelar` — e a única saída vira bloquear o bot."}},
  {"h2": "O estado deste chat"},
  { code: `mark @app.comando("lembrar")
action lembrar(ctx):
    ctx.guardar("ultima_busca", ctx.args[0] ?? "")
    ctx.responder($"Anotei: {ctx.lembrar('ultima_busca', 'nada')}")`, lang: 'df' },
  {"table": {"head": ["Onde", "Sobrevive a", "Quando usar"], "rows": [["`Tg.estado_em_memoria()`", "nada — some ao reiniciar", "desenvolvimento, e bots sem memória"], ["`Tg.estado_em_arquivo(pasta)`", "o reinício do processo", "um bot só, num servidor só"]]}},
  {"p": "O nome do arquivo sai do id do chat, e ele é **conferido**: um id que chegasse com `../` escreveria fora da pasta. O id vem do Telegram e é sempre numérico — mas \"sempre\" é uma suposição sobre um sistema de terceiros, e é barato não depender dela."},
  { code: `app := Tg.app(Tg.segredo_do_ambiente(),
              estado := Tg.estado_em_arquivo(".telegram/estado"))`, lang: 'df' },
];

const headings = [{ id: 'uma-conversa', text: "Uma conversa", level: 2 as const }, { id: 'o-estado-deste-chat', text: "O estado deste chat", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Conversas e estado"}
      description={"A máquina de estados por chat, a validação passo a passo, e onde o estado mora."}
      href={"/docs/telegram/conversas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
