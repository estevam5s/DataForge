'use client';

import { useEffect, useRef, useState } from 'react';
import { Terminal, type Linha } from './Terminal';
import { useVisivel } from './Primitivos';

export type Aba = { titulo: string; texto: string; terminal: string; linhas: Linha[] };

const DURACAO = 7000;

export function Vitrine({
  titulo,
  subtitulo,
  abas,
}: {
  titulo: string;
  subtitulo: string;
  abas: Aba[];
}) {
  const { ref, visivel } = useVisivel<HTMLElement>('-25% 0px');
  const [i, setI] = useState(0);
  const [progresso, setProgresso] = useState(0);
  const manual = useRef(false);

  // Avança sozinho enquanto a seção está na tela, como no original.
  useEffect(() => {
    if (!visivel || manual.current) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const passo = 60;
    const id = setInterval(() => {
      setProgresso((p) => {
        if (p + passo >= DURACAO) {
          setI((v) => (v + 1) % abas.length);
          return 0;
        }
        return p + passo;
      });
    }, passo);
    return () => clearInterval(id);
  }, [visivel, abas.length]);

  const escolher = (n: number) => {
    manual.current = true;
    setI(n);
    setProgresso(0);
  };

  return (
    <section ref={ref} className="relative px-4 py-20 sm:px-10 sm:py-28">
      <div className="mx-auto max-w-[1280px]">
        <div className="relative">
          {/* halo branco atrás do título, como na captura */}
          <div
            aria-hidden
            className="pointer-events-none absolute left-1/2 top-0 h-[280px] w-[min(760px,92vw)] -translate-x-1/2 -translate-y-1/3"
            style={{
              background:
                'radial-gradient(50% 50% at 50% 50%, rgba(255,255,255,.15) 0%, rgba(255,255,255,0) 70%)',
            }}
          />
          <h2 className="lp-h2 relative text-center text-[clamp(2.25rem,5vw,4rem)]">{titulo}</h2>
          <p className="lp-mono relative mx-auto mt-5 max-w-[64ch] text-center text-[13px] leading-[24px] text-white/65 sm:text-[14px]">
            {subtitulo}
          </p>
        </div>

        <div className="mt-12 sm:mt-16">
          <Terminal titulo={abas[i].terminal} linhas={abas[i].linhas} />
        </div>

        <div className="mt-10 grid gap-8 sm:mt-12 md:grid-cols-3">
          {abas.map((a, n) => {
            const ativa = n === i;
            return (
              <button
                key={a.titulo}
                onClick={() => escolher(n)}
                className="group text-left"
                aria-current={ativa}
              >
                <h3
                  className="text-[19px] font-semibold transition-colors sm:text-[20px]"
                  style={{ color: ativa ? '#fff' : 'rgba(255,255,255,.34)' }}
                >
                  {a.titulo}
                </h3>
                <p
                  className="lp-mono mt-3 text-[13px] leading-[23px] transition-colors"
                  style={{ color: ativa ? 'rgba(255,255,255,.72)' : 'rgba(255,255,255,.26)' }}
                >
                  {a.texto}
                </p>
                <div className="mt-5 h-px w-full bg-white/12">
                  <div
                    className="h-px bg-white"
                    style={{
                      width: ativa ? `${(progresso / DURACAO) * 100}%` : '0%',
                      transition: 'width 60ms linear',
                    }}
                  />
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
