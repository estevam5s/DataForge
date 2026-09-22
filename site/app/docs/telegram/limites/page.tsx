// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Os limites da Bot API",
  description: "Tamanhos, arquivos, teclados e o que o módulo confere antes de o Telegram recusar.",
};

const blocos: Bloco[] = [
  {"p": "Quase toda recusa do Telegram é um limite que se sabe de antemão. Conferir antes troca um `400 Bad Request` genérico, que não diz qual campo estourou, por uma mensagem com o nome do campo."},
  {"table": {"head": ["O quê", "Limite", "Quem confere"], "rows": [["texto de mensagem", "4096 unidades UTF-16", "`Tg.dividir`"], ["legenda de mídia", "1024 unidades UTF-16", "`Tg.dividir(texto, 1024)`"], ["`dados` de um botão", "64 **bytes**", "`Tg.botao` — recusa na hora"], ["`dados` e `url` no mesmo botão", "não pode", "`Tg.botao` — recusa na hora"], ["arquivo enviado pelo bot", "50 MB", "o Telegram"], ["arquivo baixado pelo bot", "20 MB", "o Telegram"], ["comandos no menu", "100, de até 32 caracteres", "`app.publicar_comandos`"]]}},
  { code: `adopt Arcane.Telegram as Tg

monitor:
    Tg.botao("Ver", dados := "detalhe:" + "ç" * 40)
handle Error as e:
    assert e.message.contains("64 bytes")        // quarenta 'ç' são 80 bytes`, lang: 'df' },
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Os limites da Bot API"}
      description={"Tamanhos, arquivos, teclados e o que o módulo confere antes de o Telegram recusar."}
      href={"/docs/telegram/limites"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
