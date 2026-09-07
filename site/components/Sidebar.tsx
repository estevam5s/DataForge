'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { nav } from '@/lib/nav';

function Chevron({ aberto }: { aberto: boolean }) {
  return (
    <svg
      width="14" height="14" viewBox="0 0 16 16" fill="none"
      className={`shrink-0 transition-transform duration-200 ${aberto ? '' : '-rotate-90'}`}
      aria-hidden="true"
    >
      <path d="M4 6l4 4 4-4" stroke="currentColor" strokeWidth="1.7"
        strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname() ?? '/';
  const atual = pathname.replace(/\/$/, '') || '/';

  // A seção que contém a página atual começa aberta; as demais seguem o padrão.
  const [abertas, setAbertas] = useState<Set<string>>(() => new Set());

  useEffect(() => {
    setAbertas((anteriores) => {
      const proximas = new Set(anteriores);
      for (const secao of nav) {
        const contemAtual = secao.items.some((i) => i.href === atual);
        if (contemAtual || secao.defaultOpen) proximas.add(secao.title);
      }
      return proximas;
    });
  }, [atual]);

  const alternar = (titulo: string) =>
    setAbertas((anteriores) => {
      const proximas = new Set(anteriores);
      proximas.has(titulo) ? proximas.delete(titulo) : proximas.add(titulo);
      return proximas;
    });

  return (
    <nav aria-label="Navegação da documentação" className="pb-16">
      {nav.map((secao) => {
        const unico = secao.standalone && secao.items.length === 1;

        if (unico) {
          const item = secao.items[0];
          const ativo = item.href === atual;
          return (
            <Link
              key={secao.title}
              href={item.href}
              onClick={onNavigate}
              className={`nav-label mt-1 block rounded-lg px-3 py-2 transition-colors ${
                ativo ? 'text-accent' : 'text-body hover:text-strong'
              }`}
            >
              {secao.title}
            </Link>
          );
        }

        const aberta = abertas.has(secao.title);
        const idPainel = `secao-${secao.title.replace(/\s+/g, '-').toLowerCase()}`;

        return (
          <div key={secao.title} className="mt-1">
            <button
              onClick={() => alternar(secao.title)}
              aria-expanded={aberta}
              aria-controls={idPainel}
              className="nav-label flex w-full items-center justify-between rounded-lg px-3 py-2 text-body transition-colors hover:text-strong"
            >
              <span className="flex items-center gap-2">
                {secao.title}
                {secao.badge && (
                  <span className="rounded-full bg-accent/15 px-1.5 py-px text-[10px] font-bold tracking-normal text-accent">
                    {secao.badge}
                  </span>
                )}
              </span>
              <Chevron aberto={aberta} />
            </button>

            {aberta && (
              <ul id={idPainel} className="mb-2 space-y-px">
                {secao.items.map((item) => {
                  const ativo = item.href === atual;
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        onClick={onNavigate}
                        aria-current={ativo ? 'page' : undefined}
                        className={`block rounded-lg py-[7px] pl-6 pr-3 text-[14px] transition-colors ${
                          ativo
                            ? 'bg-accent/10 font-medium text-accent'
                            : 'text-muted hover:bg-raised/60 hover:text-strong'
                        }`}
                      >
                        {item.title}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        );
      })}
    </nav>
  );
}
