// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Quando o tratador falha",
  description: "ao_falhar, a mensagem que a pessoa vê, e o erro que vai para o log — nunca o contrário.",
};

const blocos: Bloco[] = [
  {"p": "Um tratador que levanta, sem nada por cima, deixa a pessoa esperando uma resposta que não vem. `app.ao_falhar` é o tratador do erro: ele recebe o contexto **e** o erro, responde algo útil a quem estava falando, e anota o resto."},
  { code: `adopt Arcane.Telegram as Tg

app := Tg.app("123456:TESTE-exemplo")

anotados := []

mark @app.comando("dividir")
action dividir(ctx):
    partes := ctx.texto.split(" ")
    ctx.responder($"{int(partes[1]) / int(partes[2])}")

mark @app.ao_falhar()
action falhou(ctx, erro):
    anotados.append(erro)
    ctx.responder("Não consegui fazer essa conta. Tente: /dividir 10 2")

t := Tg.testar(app)
t.comando("dividir", "10", "0")
assert t.ultima().starts_with("Não consegui")
assert len(anotados) is 1 and t.falhou()

t.comando("dividir", "10", "2")
assert t.ultima() is "5.0"`, lang: 'df' },
  {"table": {"head": ["Vai para a pessoa", "Vai para o log"], "rows": [["o que ela pode fazer (\"tente /dividir 10 2\")", "o erro inteiro, com a linha"], ["que algo falhou, sem culpá-la", "o id do chat e o texto que chegou"], ["nunca: mensagem do banco, caminho de arquivo, token", "o token **mascarado**, se aparecer"]]}},
  {"callout": {"tipo": "dica", "titulo": "Nos testes, `t.falhou()`", "texto": "O `ao_falhar` faz o bot parecer bem-comportado — e esconde a falha do teste. Confira `t.falhou()` e `t.falhas()`: um teste que só olha a resposta gentil passa com o tratador quebrado."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Quando o tratador falha"}
      description={"ao_falhar, a mensagem que a pessoa vê, e o erro que vai para o log — nunca o contrário."}
      href={"/docs/telegram/erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
