// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Android",
  description: "O que funciona hoje, o que não existe, e por que a distinção importa.",
};

const blocos: Bloco[] = [
  {"callout": {"tipo": "atencao", "titulo": "Não há APK", "texto": "Empacotar o interpretador num aplicativo Android exigiria python-for-android ou Chaquopy, e as duas trazem uma cadeia de dependências que a linguagem não tem. Dizer \"dá para fazer app Android\" sem essa distinção seria a documentação mentindo sobre a linguagem."}},
  {"h2": "O que funciona hoje"},
  {"table": {"head": ["Caminho", "O que é", "O que custa"], "rows": [["**PWA**", "uma aplicação Vitrine ou Kiln que o Android instala na tela inicial", "precisa de HTTPS, e não é app nativo"], ["**servidor na rede**", "o programa roda no computador, e o celular abre no navegador", "os dois na mesma rede"], ["**Termux**", "o interpretador roda **dentro** do Android", "quem usa precisa instalar o Termux"]]}},
  { code: `$ dataforge mobile doctor
$ dataforge mobile pwa --nome="Meu Painel" --em=publico
gerado em publico/
  manifest.json   o que o Android lê para oferecer 'instalar'
  sw.js           o service worker — rede primeiro, cache de reserva
  icone.svg       o ícone`, lang: 'bash' },
  {"h2": "O que o Android exige, sem exceção"},
  {"list": ["**HTTPS** — em `http://` ele não oferece instalar (`localhost` é a exceção, para desenvolver).", "**O manifesto** com `name`, `icons` e `display: standalone`.", "**Um service worker** registrado — é ele que faz o botão \"instalar\" aparecer.", "Um ícone de **512×512** com `purpose: maskable`, senão o Android recorta o seu de qualquer jeito."]},
  {"h2": "Rede primeiro, cache de reserva"},
  {"p": "O service worker gerado busca da rede e **só** cai no cache quando ela falha. A estratégia inversa (cache primeiro) é mais rápida e faz um painel mostrar dado velho sem avisar — o que é pior que dizer \"sem conexão\"."},
  { code: `adopt Arcane.Vitrine as V

// Um painel da Vitrine é o que vira PWA: ele já é uma página, já
// responde no celular, e o manifesto só acrescenta o "instalar".
action pagina():
    V.titulo("Estoque")
    V.metrica("Produtos", 42)
    V.frame([{"nome": "café", "qtd": 12}])

s := V.testar(pagina)
s.rodar()
assert "Estoque" in s.texto()
out "o mesmo painel vira app instalável"`, lang: 'df' },
  {"h2": "O que NÃO existe"},
  {"list": ["**APK**, e publicação na Play Store.", "**Widget nativo** (Material, Compose).", "**Câmera, GPS e notificação nativas** pelo DataForge — o PWA alcança parte disso pelo navegador, com a permissão do usuário.", "**iOS**: o Safari instala PWA na tela inicial, com limites maiores (sem notificação push confiável, e o service worker é descartado com mais frequência)."]},
  {"h2": "A decisão, escrita"},
  {"p": "Um APK que empacota o CPython é possível e custa a promessa central do projeto: **zero dependência**. O PWA entrega o caso de uso real — uma ferramenta interna no celular de quem trabalha — sem quebrar nada. Quando o caso for um app de loja, com widget nativo e notificação, a resposta honesta é que esta linguagem não é a ferramenta."},
];

const headings = [{ id: 'o-que-funciona-hoje', text: "O que funciona hoje", level: 2 as const }, { id: 'o-que-o-android-exige-sem-excecao', text: "O que o Android exige, sem exceção", level: 2 as const }, { id: 'rede-primeiro-cache-de-reserva', text: "Rede primeiro, cache de reserva", level: 2 as const }, { id: 'o-que-nao-existe', text: "O que NÃO existe", level: 2 as const }, { id: 'a-decisao-escrita', text: "A decisão, escrita", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Android"}
      description={"O que funciona hoje, o que não existe, e por que a distinção importa."}
      href={"/docs/mobile"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
