'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Logo } from '@/components/Logo';

const REPO = 'https://github.com/estevam5s/DataForge';

const links = [
  { t: 'Documentação', h: '/docs' },
  { t: 'Primeiros passos', h: '/docs/primeiros-passos' },
  { t: 'Biblioteca', h: '/docs/biblioteca' },
  { t: 'Exercícios', h: '/docs/exercicios' },
  { t: 'Referência', h: '/docs/referencia/gramatica' },
];

export function NavSite() {
  const [aberto, setAberto] = useState(false);

  return (
    <div className="absolute inset-x-0 top-0 z-40 px-4 pt-4 sm:px-10 sm:pt-10">
      <nav className="mx-auto flex max-w-[1280px] items-center gap-4 rounded-[28px] border border-white/10 bg-black/35 px-5 py-3 backdrop-blur-xl sm:rounded-full sm:px-6">
        <Link href="/" className="flex shrink-0 items-center gap-2.5" aria-label="DataForge, início">
          <Logo size={28} />
          <span className="text-[17px] font-extrabold tracking-tight">DataForge</span>
        </Link>

        <div className="hidden flex-1 justify-center gap-8 lg:flex">
          {links.map((l) => (
            <Link
              key={l.h}
              href={l.h}
              className="text-[15px] font-medium text-white/85 transition-colors hover:text-white"
            >
              {l.t}
            </Link>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-3 lg:ml-0">
          <span className="lp-mono hidden text-[12px] text-white/45 sm:inline">v4.0.0</span>
          <a
            href={REPO}
            target="_blank"
            rel="noreferrer noopener"
            aria-label="Repositório no GitHub"
            className="text-white/70 transition-colors hover:text-white"
          >
            <svg viewBox="0 0 16 16" className="h-5 w-5" fill="currentColor" aria-hidden>
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.4 7.4 0 0 1 2-.27c.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
            </svg>
          </a>
          <button
            onClick={() => setAberto((v) => !v)}
            className="rounded-lg p-1.5 text-white/70 transition-colors hover:text-white lg:hidden"
            aria-label={aberto ? 'Fechar menu' : 'Abrir menu'}
            aria-expanded={aberto}
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
              {aberto ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M3 6h18M3 12h18M3 18h18" />}
            </svg>
          </button>
        </div>
      </nav>

      {aberto && (
        <div className="mx-auto mt-2 max-w-[1280px] rounded-2xl border border-white/10 bg-black/85 p-3 backdrop-blur-xl lg:hidden">
          {links.map((l) => (
            <Link
              key={l.h}
              href={l.h}
              onClick={() => setAberto(false)}
              className="block rounded-lg px-3 py-2.5 text-[15px] font-medium text-white/85 hover:bg-white/5 hover:text-white"
            >
              {l.t}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
