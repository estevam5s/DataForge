'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Logo } from './Logo';
import { Search } from './Search';
import { ThemeToggle } from './ThemeToggle';
import { Sidebar } from './Sidebar';

const REPO = 'https://github.com/estevam5s/DataForge';

export function Header() {
  const [menuAberto, setMenuAberto] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-line bg-base/85 backdrop-blur-xl">
        <div className="mx-auto flex h-[68px] max-w-[1600px] items-center gap-4 px-4 lg:px-6">
          {/* Menu do celular */}
          <button
            onClick={() => setMenuAberto(true)}
            className="rounded-lg p-2 text-muted transition-colors hover:bg-raised hover:text-strong lg:hidden"
            aria-label="Abrir navegação"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path d="M3 5.5h14M3 10h14M3 14.5h14" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
            </svg>
          </button>

          <Link href="/docs" className="flex shrink-0 items-center gap-2.5">
            <Logo />
            <span className="text-[17px] font-extrabold tracking-[-0.4px] text-strong">
              DataForge
            </span>
            <span className="hidden rounded-md border border-line px-1.5 py-px font-mono text-[10.5px] text-muted sm:block">
              v4.2
            </span>
          </Link>

          <div className="ml-auto hidden flex-1 justify-center px-6 md:flex">
            <Search />
          </div>

          <nav className="ml-auto flex items-center gap-1 md:ml-0">
            <Link
              href="/docs/primeiros-passos"
              className="hidden rounded-lg px-3 py-2 text-[13.5px] font-semibold text-body transition-colors hover:text-strong lg:block"
            >
              Começar
            </Link>
            <Link
              href="/docs/exercicios"
              className="hidden rounded-lg px-3 py-2 text-[13.5px] font-semibold text-body transition-colors hover:text-strong lg:block"
            >
              Exercícios
            </Link>
            <Link
              href="/docs/biblioteca"
              className="hidden rounded-lg px-3 py-2 text-[13.5px] font-semibold text-body transition-colors hover:text-strong xl:block"
            >
              Biblioteca
            </Link>
            <Link
              href="/painel"
              className="text-[14.5px] font-medium text-body transition-colors hover:text-strong"
            >
              Painel
            </Link>

            <span className="mx-1 hidden h-5 w-px bg-line lg:block" />

            <a
              href={REPO}
              target="_blank"
              rel="noreferrer noopener"
              className="rounded-lg p-2 text-muted transition-colors hover:bg-raised hover:text-strong"
              aria-label="Repositório no GitHub"
            >
              <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.4 7.4 0 0 1 2-.27c.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
              </svg>
            </a>
            <ThemeToggle />
          </nav>
        </div>

        {/* Busca no celular */}
        <div className="border-t border-line px-4 py-2.5 md:hidden">
          <Search />
        </div>
      </header>

      {/* Gaveta de navegação no celular */}
      {menuAberto && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setMenuAberto(false)}
        >
          <aside
            className="h-full w-[300px] max-w-[85vw] overflow-y-auto border-r border-line bg-surface p-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Logo size={26} />
                <span className="font-extrabold text-strong">DataForge</span>
              </span>
              <button
                onClick={() => setMenuAberto(false)}
                className="rounded-lg p-2 text-muted hover:text-strong"
                aria-label="Fechar navegação"
              >
                <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                  <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              </button>
            </div>
            <Sidebar onNavigate={() => setMenuAberto(false)} />
          </aside>
        </div>
      )}
    </>
  );
}
