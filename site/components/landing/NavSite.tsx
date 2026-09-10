'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { Logo } from '@/components/Logo';

const REPO = 'https://github.com/estevam5s/DataForge';

// Sem selo 'novo': um selo que fica anos no lugar deixa de informar.
const links = [
  { t: 'Documentação', h: '/docs' },
  { t: 'Primeiros passos', h: '/docs/primeiros-passos' },
  { t: 'Biblioteca', h: '/docs/biblioteca' },
  { t: 'Exercícios', h: '/docs/exercicios' },
  { t: 'Kiln', h: '/docs/kiln' },
  { t: 'Painel', h: '/painel' },
];

/**
 * Barra da landing.
 *
 * `sticky`, não `absolute`: assim ela acompanha a rolagem em vez de
 * ficar presa ao topo do documento e sumir na primeira rolada.
 *
 * A classe `lp-barra` não é decoração: ela isenta esta barra do
 * `overflow-x: clip` que as seções da landing têm. Qualquer `overflow`
 * diferente de `visible` num ANCESTRAL desliga o sticky do filho — sem
 * erro e sem aviso, ele simplesmente vira `relative` e some depois da
 * primeira dobra. Era o que acontecia quando o clip estava em `.lp`.
 *
 * Só a marca, sem o nome ao lado — uma marca reconhecível não precisa
 * se apresentar. Ao rolar, o fundo fecha e ganha sombra; o tamanho não
 * muda, porque uma barra que encolhe faz o conteúdo pular.
 */
export function NavSite() {
  const [aberto, setAberto] = useState(false);
  const [rolou, setRolou] = useState(false);

  useEffect(() => {
    const aoRolar = () => setRolou(window.scrollY > 12);
    aoRolar();
    window.addEventListener('scroll', aoRolar, { passive: true });
    return () => window.removeEventListener('scroll', aoRolar);
  }, []);

  // Com o menu aberto, a página atrás não deve rolar.
  useEffect(() => {
    document.body.style.overflow = aberto ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [aberto]);

  return (
    <>
      <div className="lp-barra sticky inset-x-0 top-0 z-50 px-4 pb-2 pt-4 sm:px-10 sm:pb-3 sm:pt-5">
        <nav
          className={`mx-auto flex h-[76px] max-w-[1280px] items-center gap-4 rounded-[30px] border px-5 transition-all duration-300 sm:rounded-full sm:px-7 ${
            rolou
              ? 'border-white/12 bg-black/70 shadow-[0_10px_40px_-14px_rgb(0_0_0/0.7)] backdrop-blur-2xl'
              : 'border-white/10 bg-black/35 backdrop-blur-xl'
          }`}
        >
          <Link
            href="/"
            className="flex shrink-0 items-center transition-transform duration-300 hover:scale-105"
            aria-label="DataForge, início"
          >
            <Logo size={48} />
          </Link>

          <div className="hidden flex-1 justify-center gap-1 lg:flex">
            {links.map((l) => (
              <Link key={l.h} href={l.h} className="lp-link">
                {l.t}
              </Link>
            ))}
          </div>

          <div className="ml-auto flex items-center gap-3 lg:ml-0">
            <span className="lp-mono hidden text-[12px] text-white/45 sm:inline">
              v1.0.0
            </span>
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
              <svg
                viewBox="0 0 24 24"
                className="h-6 w-6"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                aria-hidden
              >
                {aberto ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M3 6h18M3 12h18M3 18h18" />}
              </svg>
            </button>
          </div>
        </nav>
      </div>

      {/* No celular, o menu ocupa a tela inteira: uma caixinha com seis
          links numa tela de 390px força a mira e desperdiça o espaço. */}
      {aberto && (
        <div className="fixed inset-0 z-[60] flex flex-col bg-[#0b0507] animate-[fade_.18s_ease] lg:hidden">
          <div className="flex h-[76px] shrink-0 items-center justify-between px-6">
            <Link href="/" onClick={() => setAberto(false)} aria-label="Início">
              <Logo size={44} />
            </Link>
            <button
              onClick={() => setAberto(false)}
              className="rounded-lg p-2 text-white/70 transition-colors hover:text-white"
              aria-label="Fechar menu"
            >
              <svg
                viewBox="0 0 24 24"
                className="h-6 w-6"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                aria-hidden
              >
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>

          <nav className="flex min-h-0 flex-1 flex-col justify-center gap-1 px-6 pb-16">
            {links.map((l, i) => (
              <Link
                key={l.h}
                href={l.h}
                onClick={() => setAberto(false)}
                style={{ animationDelay: `${i * 40}ms` }}
                className="flex animate-[subir_.36s_cubic-bezier(.22,1,.36,1)_both] items-center gap-2.5 rounded-2xl px-4 py-4 text-[26px] font-bold tracking-tight text-white/90 transition-colors hover:bg-white/5 hover:text-white"
              >
                {l.t}
              </Link>
            ))}
          </nav>

          <div className="shrink-0 border-t border-white/10 px-6 py-5">
            <a
              href={REPO}
              target="_blank"
              rel="noreferrer noopener"
              className="flex items-center gap-2.5 text-[15px] text-white/60 transition-colors hover:text-white"
            >
              <svg viewBox="0 0 16 16" className="h-5 w-5" fill="currentColor" aria-hidden>
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.4 7.4 0 0 1 2-.27c.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
              </svg>
              github.com/estevam5s/DataForge
              <span className="lp-mono ml-auto text-[12px] text-white/35">v1.0.0</span>
            </a>
          </div>
        </div>
      )}
    </>
  );
}
