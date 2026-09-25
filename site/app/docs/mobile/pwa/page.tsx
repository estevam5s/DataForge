// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/mobile.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "PWA e publicação",
  description: "Do programa ao ícone na tela inicial: o que a Brasa gera, por que instalar exige HTTPS, e as formas de publicar.",
};

const blocos: Bloco[] = [
  {"h2": "O que a Brasa gera sozinha"},
  {"table": {"head": ["Arquivo", "O que é"], "rows": [["`/manifest.webmanifest`", "nome, cor, ícones e `display: standalone`"], ["`/sw.js`", "o service worker, na raiz — **rede primeiro, cache de reserva**"], ["`/__brasa__/icone-192.png` e `-512.png`", "o ícone: a cor da marca e as iniciais do nome, em PNG"], ["`/__brasa__/icone-maskable-512.png`", "o mesmo, de borda a borda, para o recorte do Android"]]}},
  { code: `adopt Arcane.Brasa as Br

app := Br.app("Estoque da Loja", cor := "#E8453C", versao := "3")
m := Br.manifesto(app)
assert m["display"] is "standalone"
assert m["short_name"] is "Estoque da L"
out [i["sizes"] cycle i in m["icons"]]`, lang: 'df' },
  {"p": "Os ícones são PNG escritos em Python puro — cabeçalho, pixels comprimidos com `zlib`, CRC —, porque a biblioteca padrão não desenha imagem e trazer o Pillow quebraria a promessa de zero dependência por um quadrado com duas letras."},
  {"h2": "Rede primeiro, cache de reserva"},
  {"p": "O service worker busca da rede e **só** cai no cache quando ela falha. Cache primeiro seria mais rápido — e faria o aplicativo mostrar dado velho sem avisar. Só `GET` entra no cache: uma ação repetida do cache seria um pedido duplicado. Uma tela nunca aberta com internet mostra \"Sem conexão\" em vez de uma página em branco."},
  {"callout": {"tipo": "nota", "titulo": "Suba a `versao` a cada publicação", "texto": "Ela entra no nome do cache (`brasa-3`). Sem mudar a versão, o aparelho continua servindo o cache antigo — e o sintoma é \"publiquei e não mudou nada\", que faz perder uma tarde."}},
  {"h2": "Instalar exige HTTPS"},
  {"p": "Pela rede local, em `http://192.168…`, o aplicativo **abre e funciona**, mas o celular não oferece \"instalar\" e o service worker não roda — e não há aviso: o botão simplesmente não aparece. É regra do navegador, não da linguagem. `localhost` é a exceção, para desenvolver no computador."},
  {"table": {"head": ["Forma", "Quando"], "rows": [["um proxy com certificado (Caddy, nginx) na frente do `Br.rodar`", "o aplicativo roda num servidor seu"], ["um túnel (Cloudflare Tunnel, ngrok)", "para mostrar a alguém hoje, do seu computador"], ["um contêiner numa plataforma com HTTPS", "`dataforge devops` gera o Dockerfile; lembre de `--host=0.0.0.0`"]]}},
  {"p": "O Kiln, que serve a Vitrine e a Brasa, **não tem TLS** — ele roda sobre o `http.server` do Python. Em produção, o proxy vai na frente."},
  {"h2": "Conferir no aparelho"},
  {"list": ["No Chrome do Android: o menu mostra **Instalar aplicativo** (sem manifesto, ele oferece só um atalho comum).", "No iPhone: Safari → Compartilhar → **Adicionar à Tela de Início**.", "Abra pelo ícone: **não há barra de endereço** — é o `standalone`.", "Desligue a rede e reabra uma tela já visitada: ela abre, do cache."]},
];

const headings = [{ id: 'o-que-a-brasa-gera-sozinha', text: "O que a Brasa gera sozinha", level: 2 as const }, { id: 'rede-primeiro-cache-de-reserva', text: "Rede primeiro, cache de reserva", level: 2 as const }, { id: 'instalar-exige-https', text: "Instalar exige HTTPS", level: 2 as const }, { id: 'conferir-no-aparelho', text: "Conferir no aparelho", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"PWA e publicação"}
      description={"Do programa ao ícone na tela inicial: o que a Brasa gera, por que instalar exige HTTPS, e as formas de publicar."}
      href={"/docs/mobile/pwa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
