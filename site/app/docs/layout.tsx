import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Sidebar } from '@/components/Sidebar';

/** Chrome da documentação: cabeçalho com busca, sidebar de 122 rotas e rodapé. */
export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="page-glow">
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
    </div>
  );
}
