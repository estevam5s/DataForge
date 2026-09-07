'use client';

import { useMemo } from 'react';
import { TextoRevelado, Sobe } from './Primitivos';

/** Campo de estrelas do fundo — posições estáveis, geradas sem aleatoriedade de render. */
function Estrelas() {
  const pontos = useMemo(
    () =>
      Array.from({ length: 90 }, (_, i) => {
        // sequência determinística: mesmo resultado no servidor e no cliente
        const a = (i * 9301 + 49297) % 233280;
        const b = (i * 4801 + 9973) % 233280;
        const c = (i * 7717 + 1543) % 233280;
        return {
          x: (a / 233280) * 100,
          y: (b / 233280) * 100,
          t: 0.6 + (c / 233280) * 1.5,
          o: 0.18 + (c / 233280) * 0.55,
        };
      }),
    [],
  );

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      {pontos.map((p, i) => (
        <span
          key={i}
          className="absolute rounded-full bg-white"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.t,
            height: p.t,
            opacity: p.o,
          }}
        />
      ))}
    </div>
  );
}

export function Manifesto() {
  return (
    <section className="relative overflow-hidden bg-black px-4 py-32 sm:px-10 sm:py-48">
      <Estrelas />

      <div className="relative mx-auto max-w-[1280px]">
        <TextoRevelado
          texto="Nenhuma linguagem dizia o que a gente queria dizer — então escrevemos a nossa."
          className="lp-h1 max-w-[16ch] font-medium"
        />

        <Sobe className="mt-14 max-w-[58ch]">
          <p className="lp-mono text-[14px] leading-[26px] text-white/60">
            Onde outras linguagens dizem if, for, class e try, o DataForge diz
            given, cycle, blueprint e monitor. Não é troca de nome: é a decisão de
            nomear a intenção. O resto — analisador, formatador, linter, runner de
            testes, gerador de documentação — veio junto, porque uma linguagem sem
            ferramenta é só uma gramática.
          </p>
        </Sobe>
      </div>
    </section>
  );
}
