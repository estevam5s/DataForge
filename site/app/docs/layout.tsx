import Link from 'next/link';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Sidebar } from '@/components/Sidebar';

/**
 * Chrome da documentação.
 *
 * Cabeçalho e sidebar são cartões flutuantes sobre o fundo, não painéis
 * colados nas bordas: o respiro em volta é o que separa a navegação do
 * texto sem precisar de uma linha divisória forte.
 *
 * A sidebar rola sozinha e mantém o rodapé (versão e CTA) sempre à
 * mão — com 190 rotas, um rodapé no fim da lista nunca seria visto.
 */
export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="page-glow min-h-screen">
      <Header />

      <div className="relative mx-auto flex max-w-[1620px] gap-6 px-2 pt-3 sm:px-4">
        <aside className="hidden w-[280px] shrink-0 lg:block">
          <div className="sticky top-[84px] flex max-h-[calc(100vh-100px)] flex-col rounded-2xl border border-line/70 bg-surface/50 backdrop-blur-sm">
            <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-2.5 py-4 [scrollbar-width:thin]">
              <Sidebar />
            </div>

            <div className="shrink-0 space-y-2 border-t border-line/70 p-3">
              <Link
                href="/painel"
                className="block rounded-xl bg-accent px-4 py-2.5 text-center text-[13px] font-bold uppercase tracking-wide text-white shadow-[0_6px_20px_-8px_rgb(var(--accent))] transition-all hover:bg-accent-soft hover:shadow-[0_8px_24px_-8px_rgb(var(--accent))]"
              >
                Praticar no painel
              </Link>
              <Link
                href="/docs/roadmap"
                className="block rounded-xl border border-line px-4 py-2 text-center text-[12.5px] font-semibold text-muted transition-colors hover:border-line hover:bg-raised hover:text-strong"
              >
                Versão 1.0.0
              </Link>
            </div>
          </div>
        </aside>

        <main id="conteudo" className="min-w-0 flex-1">
          {children}
        </main>
      </div>

      <Footer />
    </div>
  );
}
