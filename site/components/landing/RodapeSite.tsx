'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Logo } from '@/components/Logo';
import { Rotulo } from './Primitivos';

const REPO = 'https://github.com/estevam5s/DataForge';

const colunas = [
  {
    t: 'Documentação',
    l: [
      { t: 'Introdução', h: '/docs' },
      { t: 'Primeiros passos', h: '/docs/primeiros-passos' },
      { t: 'Instalação', h: '/docs/instalacao' },
      { t: 'Tutorial completo', h: '/docs/fundamentos/anotacoes-de-tipo' },
    ],
  },
  {
    t: 'Referência',
    l: [
      { t: 'Gramática', h: '/docs/referencia/gramatica' },
      { t: 'Palavras reservadas', h: '/docs/referencia/palavras-reservadas' },
      { t: 'Funções embutidas', h: '/docs/referencia/embutidas' },
      { t: 'Biblioteca Arcane', h: '/docs/biblioteca' },
    ],
  },
  {
    t: 'Ferramentas',
    l: [
      { t: 'CLI', h: '/docs/cli' },
      { t: 'Análise estática', h: '/docs/tecnicas/analise-estatica' },
      { t: 'Testes', h: '/docs/tecnicas/testes' },
      { t: 'forge.toml', h: '/docs/cli/forge-toml' },
    ],
  },
  {
    t: 'Projeto',
    l: [
      { t: 'Roadmap', h: '/docs/roadmap' },
      { t: 'Contribuir', h: '/docs/contribuir' },
      { t: 'FAQ', h: '/docs/faq' },
      { t: 'Exercícios', h: '/docs/exercicios' },
    ],
  },
];

/** Linhas onduladas do painel — desenhadas, não uma imagem da captura. */
function Ondas() {
  return (
    <svg
      viewBox="0 0 420 520"
      className="pointer-events-none absolute bottom-0 right-0 h-full w-auto opacity-[.22]"
      fill="none"
      aria-hidden
    >
      {Array.from({ length: 26 }, (_, i) => (
        <path
          key={i}
          d={`M${-40 + i * 9} 520 C ${60 + i * 11} ${400 - i * 6}, ${150 + i * 5} ${300 - i * 4}, ${420} ${150 - i * 5}`}
          stroke="#fff"
          strokeWidth="0.7"
          strokeOpacity={0.16 + (i % 5) * 0.1}
        />
      ))}
    </svg>
  );
}

export function RodapeSite() {
  const [email, setEmail] = useState('');
  const [enviado, setEnviado] = useState(false);

  return (
    <footer className="relative overflow-hidden p-4 sm:p-10">
      {/* o brilho vermelho sangra por trás do painel, como no original */}
      <div className="lp-bleed left-[-10%] top-[30%] h-[420px] w-[460px]" aria-hidden />
      <div className="lp-bleed right-[-10%] top-[30%] h-[420px] w-[460px]" aria-hidden />

      <div className="relative overflow-hidden rounded-[28px] border border-[var(--lp-line)] bg-[var(--lp-surface)] sm:rounded-[40px]">
        <div className="grid lg:grid-cols-[minmax(0,380px)_minmax(0,1fr)]">
          {/* Painel do boletim */}
          <div className="relative overflow-hidden border-b border-[var(--lp-line)] px-8 py-12 sm:px-12 sm:py-16 lg:border-b-0 lg:border-r">
            <Ondas />
            <div className="relative">
              <h2 className="text-[24px] font-semibold sm:text-[26px]">Quer acompanhar?</h2>
              <p className="lp-mono mt-4 max-w-[34ch] text-[13px] leading-[24px] text-white/60">
                A linguagem é aberta e o desenvolvimento acontece no GitHub.
                Acompanhe os lançamentos por lá.
              </p>

              <form
                className="mt-8 flex max-w-[340px] items-center rounded-full border border-white/12 bg-white/[.04] p-1.5"
                onSubmit={(e) => {
                  e.preventDefault();
                  setEnviado(true);
                }}
              >
                <label htmlFor="lp-email" className="sr-only">
                  Seu e-mail
                </label>
                <input
                  id="lp-email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="SEU E-MAIL"
                  className="lp-mono min-w-0 flex-1 bg-transparent px-4 text-[12px] tracking-[1px] text-white placeholder:text-white/35 focus:outline-none"
                />
                <button
                  type="submit"
                  className="shrink-0 rounded-full bg-white/10 px-5 py-2.5 text-[13.5px] font-semibold transition-colors hover:bg-white/20"
                >
                  Inscrever
                </button>
              </form>

              <p className="lp-mono mt-3 text-[11.5px] text-white/40" role="status">
                {enviado
                  ? 'Ainda não há lista de e-mails — acompanhe pelo GitHub.'
                  : 'Sem lista ainda: os avisos saem nos releases do repositório.'}
              </p>
            </div>
          </div>

          {/* Colunas de links */}
          <div className="px-8 py-12 sm:px-12 sm:py-16">
            <div className="grid grid-cols-2 gap-x-6 gap-y-10 md:grid-cols-4">
              {colunas.map((c) => (
                <div key={c.t}>
                  <p className="lp-label mb-6">{c.t.toUpperCase()}</p>
                  <ul className="space-y-4">
                    {c.l.map((l) => (
                      <li key={l.h}>
                        <Link
                          href={l.h}
                          className="text-[14.5px] text-white/85 transition-colors hover:text-[var(--lp-warm)]"
                        >
                          {l.t}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            <div className="mt-16 flex flex-col gap-6 border-t border-[var(--lp-line)] pt-8 sm:flex-row sm:items-center sm:justify-between">
              <Link href="/" className="flex items-center gap-2.5">
                <Logo size={24} />
                <span className="font-extrabold tracking-tight">DataForge</span>
                <span className="lp-mono text-[11px] text-white/40">v4.0.0</span>
              </Link>

              <p className="lp-mono text-[11px] leading-[20px] tracking-[.6px] text-white/40">
                SOB LICENÇA MIT{'  /  '}
                <a href={REPO} target="_blank" rel="noreferrer noopener" className="underline hover:text-white">
                  GITHUB
                </a>
                {'  /  '}DOCUMENTAÇÃO EM{' '}
                <Link href="/docs" className="underline hover:text-white">
                  PORTUGUÊS
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="relative mt-8 flex justify-center">
        <Rotulo texto="ESCREVA. VERIFIQUE. RODE." />
      </div>
    </footer>
  );
}
