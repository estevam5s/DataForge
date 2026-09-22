import type { Metadata, Viewport } from 'next';
import './globals.css';

/**
 * O que aparece quando alguém compartilha o link.
 *
 * Três coisas decidem se o card funciona, e as três estavam erradas:
 *
 * 1. **A imagem era um SVG.** Nenhuma rede que mostra prévia aceita
 *    SVG — nem Facebook, nem LinkedIn, nem WhatsApp, Discord ou
 *    Telegram. O link aparecia sem imagem nenhuma, que é pior do que
 *    não ter metadado: o card fica cinza e vazio.
 *
 * 2. **A descrição não dizia para que a linguagem serve.** "Tipos
 *    verificados, pattern matching estrutural e pipelines nativos" é
 *    uma lista de recursos para quem já conhece. Quem vê o card no
 *    feed do LinkedIn não conhece — e é ela que decide o clique.
 *
 * 3. **Não havia `canonical` nem `url`.** Sem eles, o mesmo conteúdo
 *    compartilhado de `/` e de `/docs/` vira duas páginas para o
 *    buscador, e o LinkedIn às vezes guarda a prévia da errada.
 */
const DESCRICAO_CURTA =
  'Uma linguagem de programação completa, em português: interpretador, ' +
  'analisador estático, 85 módulos de biblioteca, dois frameworks web e ' +
  'uma consulta tipada própria.';

const DESCRICAO_LONGA =
  'DataForge é uma linguagem de programação de propósito geral criada para ' +
  'que o vocabulário do código seja o mesmo de quem o escreve — as palavras ' +
  'são em português e cada uma diz o que faz. ' +
  'Ela é interpretada, tipada opcionalmente e implementada em Python 3.10+ ' +
  'sem dependência externa: lexer, parser, AST, analisador estático e ' +
  'interpretador próprios. ' +
  'Traz 85 módulos de biblioteca padrão (Arcane), o framework web Kiln, ' +
  'a Vitrine para dashboards, o Crucible para testes, o Lavra — uma ' +
  'consulta tipada no espírito do GraphQL — e a Malha para microsserviços. ' +
  'Vem com CLI, gerenciador de pacotes, formatador, linter, depurador, ' +
  'LSP e extensão do VS Code. ' +
  'Tudo o que a documentação afirma é código que roda: 387 exercícios que ' +
  'verificam o próprio resultado e mais de 2.400 testes.';

export const metadata: Metadata = {
  // O dominio onde o site REALMENTE vive.
  //
  // Apontava para um '.dev' que nao responde, e era o unico lugar do
  // repositorio que o citava — nao havia nem a intencao de usa-lo.
  // Todo canonico e todo Open Graph iam para um endereco inexistente:
  // um link compartilhado nao mostra previa, e um buscador indexa o
  // lugar errado.
  metadataBase: new URL('https://dataforge-lang.vercel.app'),
  title: {
    default: 'DataForge — documentação da linguagem',
    template: '%s | DataForge',
  },
  description: DESCRICAO_CURTA,
  keywords: [
    'DataForge', 'linguagem de programação', 'linguagem em português',
    'interpretador', 'compilador', 'pipelines', 'pattern matching',
    'records', 'enums', 'Kiln', 'Vitrine', 'Lavra', 'Arcane',
    'framework web', 'dashboards', 'GraphQL', 'Python', 'open source',
  ],
  authors: [{ name: 'Estevam Souza', url: 'https://github.com/estevam5s' }],
  creator: 'Estevam Souza',
  publisher: 'DataForge',
  category: 'technology',
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    url: 'https://dataforge-lang.vercel.app',
    siteName: 'DataForge',
    title: 'DataForge — a linguagem de programação em português',
    // O LinkedIn e o Facebook mostram a descrição INTEIRA no card, e é
    // ela que decide se alguém clica. Uma frase de efeito não diz para
    // que a linguagem serve; esta diz o propósito, o que ela traz e o
    // que a sustenta.
    description: DESCRICAO_LONGA,
    images: [
      {
        url: '/og.png',
        width: 1200,
        height: 630,
        type: 'image/png',
        alt: 'DataForge — uma linguagem de programação completa, em português',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DataForge — a linguagem de programação em português',
    description: DESCRICAO_CURTA,
    images: ['/og.png'],
    creator: '@estevam5s',
  },
  alternates: { canonical: 'https://dataforge-lang.vercel.app' },
  icons: {
    icon: [
      { url: '/icon.svg', type: 'image/svg+xml' },
      { url: '/favicon.ico', sizes: '16x16 32x32 48x48' },
    ],
    apple: '/apple-icon.png',
  },
  robots: { index: true, follow: true },
};

/**
 * O dado estruturado que as redes e o buscador leem.
 *
 * O Open Graph diz o que MOSTRAR; isto diz o que a coisa É. O Google
 * usa para o painel de conhecimento, e o LinkedIn para completar o
 * card quando o autor da publicação não escreveu nada — que é o caso
 * mais comum de todos, alguém colando o link e apertando publicar.
 */
const DADO_ESTRUTURADO = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'SoftwareApplication',
      '@id': 'https://dataforge-lang.vercel.app/#linguagem',
      name: 'DataForge',
      alternateName: 'DataForge Language',
      applicationCategory: 'DeveloperApplication',
      applicationSubCategory: 'Programming Language',
      operatingSystem: 'macOS, Linux, Windows',
      softwareVersion: '1.0.0',
      description: DESCRICAO_LONGA,
      url: 'https://dataforge-lang.vercel.app',
      downloadUrl: 'https://dataforge-lang.vercel.app/download',
      image: 'https://dataforge-lang.vercel.app/og.png',
      license: 'https://opensource.org/licenses/MIT',
      inLanguage: 'pt-BR',
      programmingLanguage: 'Python',
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'BRL' },
      author: {
        '@type': 'Person',
        name: 'Estevam Souza',
        url: 'https://github.com/estevam5s',
      },
      featureList: [
        'Interpretador de árvore com compilação para fechamentos',
        'Analisador estático que atravessa arquivos',
        'Tipos opcionais verificados em execução',
        'Pattern matching estrutural',
        'Pipelines nativos (sift, morph, distill)',
        'Records imutáveis, enums com valor e traits',
        'Generators preguiçosos, inclusive infinitos',
        '85 módulos de biblioteca padrão (Arcane)',
        'Kiln — framework web com WebSocket e SSE',
        'Vitrine — dashboards e aplicações de dados',
        'Lavra — consulta tipada, no espírito do GraphQL',
        'Crucible — testes com cobertura de linha',
        'Arcane.Malha — retry, disjuntor, rastro e saga',
        'Gerenciador de pacotes com semver e lockfile',
        'Formatador, linter, depurador, LSP e extensão do VS Code',
        'Ponte para o Python: adopt Python.numpy',
      ],
    },
    {
      '@type': 'WebSite',
      '@id': 'https://dataforge-lang.vercel.app/#site',
      url: 'https://dataforge-lang.vercel.app',
      name: 'DataForge',
      description: DESCRICAO_CURTA,
      inLanguage: 'pt-BR',
      publisher: { '@id': 'https://dataforge-lang.vercel.app/#linguagem' },
    },
    {
      '@type': 'TechArticle',
      '@id': 'https://dataforge-lang.vercel.app/docs#doc',
      headline: 'Documentação do DataForge',
      description:
        'Mais de 460 páginas, 387 exercícios que verificam o próprio ' +
        'resultado, e cada trecho de código compilado a cada mudança.',
      url: 'https://dataforge-lang.vercel.app/docs',
      image: 'https://dataforge-lang.vercel.app/og-docs.png',
      inLanguage: 'pt-BR',
      isPartOf: { '@id': 'https://dataforge-lang.vercel.app/#site' },
      about: { '@id': 'https://dataforge-lang.vercel.app/#linguagem' },
    },
  ],
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: dark)', color: 'rgb(8, 6, 6)' },
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
  ],
  width: 'device-width',
  initialScale: 1,
};

/**
 * Aplica o tema antes da primeira pintura, evitando o flash de tema errado.
 * Precisa rodar síncrono no <head>, por isso não é um componente React.
 */
const scriptDeTema = `
(function () {
  try {
    var t = localStorage.getItem('df-theme');
    document.documentElement.dataset.theme = t === 'light' ? 'light' : 'dark';
  } catch (e) {
    document.documentElement.dataset.theme = 'dark';
  }
})();
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" data-theme="dark" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: scriptDeTema }} />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(DADO_ESTRUTURADO) }}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Inconsolata:wght@400;500;600&family=Geist+Mono:wght@300;400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <a
          href="#conteudo"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-lg focus:bg-accent focus:px-4 focus:py-2 focus:font-semibold focus:text-white"
        >
          Pular para o conteúdo
        </a>

        {children}
      </body>
    </html>
  );
}
