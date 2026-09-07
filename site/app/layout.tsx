import type { Metadata, Viewport } from 'next';
import './globals.css';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Sidebar } from '@/components/Sidebar';

export const metadata: Metadata = {
  metadataBase: new URL('https://dataforge-lang.dev'),
  title: {
    default: 'DataForge — documentação da linguagem',
    template: '%s | DataForge',
  },
  description:
    'Documentação oficial do DataForge: uma linguagem de programação com vocabulário próprio, tipos verificados, pattern matching estrutural e pipelines nativos.',
  keywords: [
    'DataForge', 'linguagem de programação', 'documentação', 'pipelines',
    'pattern matching', 'records', 'enums', 'português',
  ],
  authors: [{ name: 'DataForge' }],
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    siteName: 'DataForge',
    title: 'DataForge — documentação da linguagem',
    description:
      'Tipos verificados, pattern matching estrutural, pipelines nativos e 20 módulos de biblioteca padrão.',
  },
  robots: { index: true, follow: true },
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
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inconsolata:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="page-glow">
        <a
          href="#conteudo"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-lg focus:bg-accent focus:px-4 focus:py-2 focus:font-semibold focus:text-white"
        >
          Pular para o conteúdo
        </a>

        <Header />

        <div className="relative mx-auto flex max-w-[1600px] px-4 lg:px-6">
          <aside className="hidden w-[268px] shrink-0 lg:block">
            <div className="sticky top-[68px] max-h-[calc(100vh-68px)] overflow-y-auto py-8 pr-4">
              <Sidebar />
            </div>
          </aside>

          <main id="conteudo" className="min-w-0 flex-1 lg:pl-10">
            {children}
          </main>
        </div>

        <Footer />
      </body>
    </html>
  );
}
