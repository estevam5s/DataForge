// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Um PWA passo a passo",
  description: "Do painel da Vitrine ao ícone na tela inicial do Android.",
};

const blocos: Bloco[] = [
  {"p": "O caminho inteiro tem quatro passos, e três deles são do Android — não da linguagem."},
  {"h2": "1. O painel"},
  { code: `adopt Arcane.Vitrine as V

action pagina():
    V.titulo("Chão de fábrica")
    colunas := V.colunas(2)
    colunas[0].metrica("Em produção", 12)
    colunas[1].metrica("Parados", 3)
    V.frame([
        {"maquina": "prensa 1", "estado": "ok"},
        {"maquina": "prensa 2", "estado": "parada"},
    ])
    V.atualizar_a_cada(5)

s := V.testar(pagina)
s.rodar()
assert "Chão de fábrica" in s.texto()
out "o painel responde — e é o mesmo no celular"`, lang: 'df' },
  {"h2": "2. Os arquivos do PWA"},
  { code: `$ dataforge mobile pwa --nome="Chão de fábrica" --em=publico`, lang: 'bash' },
  {"h2": "3. O HTML"},
  { code: `<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#0d1017">
<script>navigator.serviceWorker?.register('/sw.js')</script>`, lang: 'text' },
  {"h2": "4. O HTTPS"},
  {"p": "Sem ele o Android **não oferece instalar**, e não há aviso: o botão simplesmente não aparece. As três formas que funcionam:"},
  {"table": {"head": ["Forma", "Quando"], "rows": [["um proxy com certificado (nginx, Caddy)", "o painel roda na sua rede, e você controla o servidor"], ["um túnel (Cloudflare, ngrok)", "para mostrar a alguém hoje"], ["hospedagem estática + API", "quando a página é estática e o dado vem por HTTP"]]}},
  {"p": "O Kiln **não tem TLS** — ele roda sobre o `http.server` do Python. Em produção pública, o nginx ou o Caddy vai na frente, e isso está escrito na página dele também."},
  {"h2": "Conferir que ficou instalável"},
  {"list": ["Abra no Chrome do Android e veja se aparece \"Adicionar à tela inicial\" **com ícone próprio** (sem manifesto, ele oferece um atalho comum).", "Nas Ferramentas do Desenvolvedor: **Application → Manifest** e **Service Workers**.", "Desligue a rede e recarregue: com o service worker, a página abre; sem ele, dá erro de conexão.", "Instale, abra pelo ícone, e confira que **não há barra de endereço** — é o `display: standalone` funcionando."]},
  {"callout": {"tipo": "nota", "titulo": "Atualizar um PWA instalado", "texto": "O service worker gerado troca o cache pelo nome (`nome-vN`) e chama `skipWaiting`. Sem mudar a versão, o Android continua servindo o cache antigo — e o sintoma é \"publiquei e não mudou nada\", que faz perder uma tarde."}},
];

const headings = [{ id: '1-o-painel', text: "1. O painel", level: 2 as const }, { id: '2-os-arquivos-do-pwa', text: "2. Os arquivos do PWA", level: 2 as const }, { id: '3-o-html', text: "3. O HTML", level: 2 as const }, { id: '4-o-https', text: "4. O HTTPS", level: 2 as const }, { id: 'conferir-que-ficou-instalavel', text: "Conferir que ficou instalável", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Um PWA passo a passo"}
      description={"Do painel da Vitrine ao ícone na tela inicial do Android."}
      href={"/docs/mobile/pwa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
