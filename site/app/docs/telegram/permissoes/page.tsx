// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Quem pode usar o quê",
  description: "Lista de permitidos, administradores de grupo e o gancho que barra antes do tratador.",
};

const blocos: Bloco[] = [
  {"p": "Um bot é público: **qualquer pessoa** que achar o nome dele pode mandar `/apagar_tudo`. A pergunta \"quem pode?\" precisa de resposta em todo comando que muda algo — e a forma de não esquecê-la em nenhum é respondê-la **num lugar só**."},
  { code: `adopt Arcane.Telegram as Tg

app := Tg.app("123456:TESTE-exemplo")

steady ADMINS := [42]

mark @app.antes_de_cada()
action barrar(ctx):
    publicos := ["/start", "/ajuda"]
    given (ctx.texto ?? "") in publicos or ctx.id_do_usuario() in ADMINS:
        yield yes
    ctx.responder("Este bot é de uso interno.")
    yield no                               // 'no' interrompe o update

mark @app.comando("apagar_tudo")
action apagar_tudo(ctx):
    ctx.responder("Apagado.")

admin := Tg.testar(app)
admin.comando("apagar_tudo")
assert admin.ultima() is "Apagado."

estranho := Tg.testar(app, 2002, {"id": 7, "first_name": "Zé"})
estranho.comando("apagar_tudo")
assert estranho.ultima() is "Este bot é de uso interno."`, lang: 'df' },
  {"h2": "Em grupo: quem administra"},
  {"p": "Num grupo, a pergunta costuma ser \"quem fala é administrador deste grupo?\". `ctx.e_admin()` pergunta ao Telegram — e em conversa privada é sempre `yes`, porque ali a pessoa administra a própria conversa:"},
  { code: `adopt Arcane.Telegram as Tg

app := Tg.app("123456:TESTE-exemplo")

mark @app.comando("fixar")
action fixar(ctx):
    given not ctx.e_admin():
        ctx.responder("Só administradores fixam mensagens.")
        yield void
    ctx.responder("Fixada.")

t := Tg.testar(app, -100123)            // id negativo: um grupo
t.comando("fixar")
assert t.ultima() is "Só administradores fixam mensagens."`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "Nunca confie no nome", "texto": "`username` e `first_name` são escolhidos pela pessoa e mudam quando ela quiser. A lista de permitidos é de **ids** numéricos — `ctx.id_do_usuario()` —, que o Telegram garante."}},
];

const headings = [{ id: 'em-grupo-quem-administra', text: "Em grupo: quem administra", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Quem pode usar o quê"}
      description={"Lista de permitidos, administradores de grupo e o gancho que barra antes do tratador."}
      href={"/docs/telegram/permissoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
