// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/mobile.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Limites",
  description: "O que a Brasa não faz, por que, e quando esta linguagem não é a ferramenta.",
};

const blocos: Bloco[] = [
  {"h2": "O que NÃO existe"},
  {"list": ["**APK** e publicação na Play Store ou na App Store.", "**Widget nativo** (Material, Compose, SwiftUI) — os componentes são HTML com o CSS ajustado ao dedo.", "**Notificação push** — exigiria um servidor de push e chaves VAPID, e no iPhone só funciona com o aplicativo instalado.", "**Bluetooth, NFC e sensores** — as APIs da web para eles são parciais, e só no Chrome.", "**Funcionar sem servidor**: o programa roda no servidor. Sem rede, o aplicativo mostra as telas já visitadas, do cache — não executa nada novo."]},
  {"h2": "O iPhone tem limites próprios"},
  {"p": "O Safari instala o PWA na tela inicial, mas descarta o service worker com mais frequência, e a notificação só existe com o aplicativo instalado. O que a Brasa gera funciona nos dois — o que muda é quanto do cache sobrevive."},
  {"h2": "A decisão, escrita"},
  {"p": "Um APK que empacota o CPython é possível, e custa a promessa central do projeto: **zero dependência**. O PWA entrega o caso de uso real — uma ferramenta no celular de quem trabalha: o estoque, a entrega, o chamado, o painel — sem quebrar nada. Quando o caso for um aplicativo de loja, com widget nativo e notificação, a resposta honesta é que esta linguagem não é a ferramenta."},
  { code: `$ dataforge mobile doctor`, lang: 'bash' },
  {"p": "O `doctor` repete, no terminal, o que existe e o que não existe — para ninguém precisar abrir esta página para descobrir."},
];

const headings = [{ id: 'o-que-nao-existe', text: "O que NÃO existe", level: 2 as const }, { id: 'o-iphone-tem-limites-proprios', text: "O iPhone tem limites próprios", level: 2 as const }, { id: 'a-decisao-escrita', text: "A decisão, escrita", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Limites"}
      description={"O que a Brasa não faz, por que, e quando esta linguagem não é a ferramenta."}
      href={"/docs/mobile/limites"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
