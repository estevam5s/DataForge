'use client';

import Link from 'next/link';
import { useState } from 'react';
import { tokenize, classePorTipo } from '@/lib/highlight';
import trechos from '@/lib/trechos-landing.json';
import { Rotulo, Sobe } from './Primitivos';

/** Realce pelo mesmo tokenizador da documentação — inclusive a regra do '//'. */
function Codigo({ fonte }: { fonte: string }) {
  return (
    <code>
      {tokenize(fonte).map((t, i) => (
        <span key={i} className={classePorTipo[t.kind]}>
          {t.text}
        </span>
      ))}
    </code>
  );
}

export function Sintaxe() {
  const [i, setI] = useState(0);
  const atual = trechos[i];

  return (
    <section className="relative overflow-hidden px-4 py-24 sm:px-10 sm:py-32">
      {/* brilho vermelho vazando por baixo do painel, como na captura */}
      <div className="lp-bleed left-[-6%] top-1/3 h-[380px] w-[520px]" aria-hidden />

      <div className="relative mx-auto grid max-w-[1280px] items-center gap-14 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <div>
          <Rotulo texto="SINTAXE" />
          <h2 className="lp-h2 mt-5 max-w-[16ch]">
            Escreva com o vocabulário da intenção.
          </h2>
          <p className="lp-mono mt-7 max-w-[46ch] text-[13px] leading-[24px] text-white/60">
            Todo trecho aqui é um arquivo <span className="text-white/85">.df</span> que
            roda: o código e a saída foram capturados da execução, não escritos à mão.
          </p>
          <Link href="/docs/referencia/gramatica" className="lp-btn mt-9 !bg-[var(--lp-raised)] !text-white">
            Referência da linguagem
          </Link>
        </div>

        <Sobe>
          <div className="lp-card overflow-hidden rounded-[20px]">
            <div className="flex gap-1 overflow-x-auto border-b border-[var(--lp-line)] px-3 py-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
              {trechos.map((t, n) => (
                <button
                  key={t.titulo}
                  onClick={() => setI(n)}
                  className="shrink-0 rounded-full px-4 py-2 text-[13.5px] font-semibold transition-colors"
                  style={{
                    color: n === i ? '#fff' : 'rgba(255,255,255,.4)',
                    background: n === i ? 'rgba(255,255,255,.09)' : 'transparent',
                  }}
                  aria-current={n === i}
                >
                  {t.titulo}
                </button>
              ))}
            </div>

            <div className="overflow-x-auto px-4 py-5 sm:px-6">
              <pre className="lp-mono text-[12.5px] leading-[22px] sm:text-[13px] sm:leading-[23px]">
                <Codigo fonte={atual.codigo} />
              </pre>
            </div>

            <div className="border-t border-[var(--lp-line)] bg-black/35 px-4 py-4 sm:px-6">
              <p className="lp-label mb-2">SAÍDA</p>
              <pre className="lp-mono overflow-x-auto text-[12.5px] leading-[22px] text-[#4ec9a4]">
                {atual.saida}
              </pre>
            </div>
          </div>

          <p className="lp-mono mt-4 text-[12px] text-white/35">{atual.desc}</p>
        </Sobe>
      </div>
    </section>
  );
}
