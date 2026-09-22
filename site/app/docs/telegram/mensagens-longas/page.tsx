// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Mensagens longas",
  description: "O limite de 4096 é em UTF-16, e não em caracteres: Tg.dividir corta onde o Telegram aceita.",
};

const blocos: Bloco[] = [
  {"p": "Uma mensagem do Telegram tem no máximo **4096** unidades; uma legenda de foto, **1024**. Passar disso não corta a mensagem: o Telegram a **recusa inteira** com `message is too long`, e o relatório que o bot ia mandar simplesmente não chega."},
  {"p": "E a conta é em unidades **UTF-16**, não em caracteres. Um emoji — quase todos estão fora do plano básico — vale **dois**. Uma mensagem de 4000 caracteres com 200 emojis passa de 4096 e é recusada, embora `len` diga 4000."},
  { code: `adopt Arcane.Telegram as Tg

app := Tg.app("123456:TESTE-exemplo")

relatorio := ("linha do relatório com 📦\\n" * 300)

mark @app.comando("relatorio")
action enviar_relatorio(ctx):
    cycle parte in Tg.dividir(relatorio):
        ctx.responder(parte)

t := Tg.testar(app)
t.comando("relatorio")
assert t.quantas("sendMessage") bigger 1
assert "".join(t.respostas()).replace("\\n", "") is relatorio.replace("\\n", "")`, lang: 'df' },
  {"h2": "Onde ele corta"},
  {"table": {"head": ["Preferência", "Por quê"], "rows": [["1. parágrafo (`\\n\\n`)", "o leitor não percebe a quebra"], ["2. linha", "uma linha de tabela não fica pela metade"], ["3. espaço", "uma palavra não se parte"], ["4. no meio", "só quando uma \"palavra\" passa do limite sozinha"]]}},
  {"p": "E um escape do MarkdownV2 nunca é separado da barra: um pedaço terminando em `\\\\` e o seguinte começando em `.` são **duas** mensagens recusadas por marcação inválida."},
  { code: `adopt Arcane.Telegram as Tg

legenda := Tg.dividir("Legenda muito longa " * 80, 1024)
assert len(legenda) bigger 1
cycle p in legenda:
    assert len(p) smaller_eq 1024`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Mais de 20 mensagens?", "texto": "Um relatório que vira vinte mensagens já não é uma mensagem. Mande um **arquivo**: `ctx.responder_documento(\"relatorio.csv\")` — ele chega inteiro, e a pessoa abre na planilha."}},
];

const headings = [{ id: 'onde-ele-corta', text: "Onde ele corta", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Mensagens longas"}
      description={"O limite de 4096 é em UTF-16, e não em caracteres: Tg.dividir corta onde o Telegram aceita."}
      href={"/docs/telegram/mensagens-longas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
