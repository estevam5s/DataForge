'use client';

import { useState } from 'react';
import { TextoRevelado, Sobe } from './Primitivos';

/**
 * Ícones desenhados aqui, em SVG, com um degrade metálico.
 * Nenhum asset da captura é usado — só a linguagem visual.
 */
function Glifo({ tipo }: { tipo: number }) {
  const formas = [
    // módulos: cubos empilhados
    <g key="0">
      <rect x="14" y="26" width="20" height="20" rx="3" />
      <rect x="30" y="14" width="20" height="20" rx="3" />
      <rect x="30" y="38" width="20" height="20" rx="3" />
    </g>,
    // tipos: escudo com marca
    <g key="1">
      <path d="M36 10 58 20v16c0 13-9 22-22 26-13-4-22-13-22-26V20L36 10Z" />
      <path d="M26 35l7 8 15-16" strokeWidth="4" />
    </g>,
    // pattern matching: caminhos que se ramificam
    <g key="2">
      <circle cx="17" cy="36" r="7" />
      <circle cx="55" cy="18" r="6" />
      <circle cx="55" cy="36" r="6" />
      <circle cx="55" cy="54" r="6" />
      <path d="M24 36h10l15-18M34 36h15M34 36h10l11 18" strokeWidth="2.5" />
    </g>,
    // records: bloco selado
    <g key="3">
      <rect x="13" y="16" width="46" height="40" rx="6" />
      <path d="M13 30h46M27 30v26" strokeWidth="2.5" />
    </g>,
    // pipelines: fluxo afunilando
    <g key="4">
      <path d="M11 18h50l-17 18v20l-16-8V36L11 18Z" />
    </g>,
    // generators: espiral
    <g key="5">
      <path d="M36 12a24 24 0 1 1-17 41 17 17 0 1 1 24-24 10 10 0 1 1-14 14" strokeWidth="3.5" />
    </g>,
    // zero dependências: círculo cortado
    <g key="6">
      <circle cx="36" cy="36" r="23" />
      <path d="M19 19l34 34" strokeWidth="4" />
    </g>,
  ];

  return (
    <svg viewBox="0 0 72 72" className="h-14 w-14" fill="none" aria-hidden>
      <defs>
        <linearGradient id={`met${tipo}`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#fff" stopOpacity="0.95" />
          <stop offset="42%" stopColor="#a8a8a8" stopOpacity="0.8" />
          <stop offset="70%" stopColor="#f2f2f2" stopOpacity="0.95" />
          <stop offset="100%" stopColor="#6b6b6b" stopOpacity="0.75" />
        </linearGradient>
      </defs>
      <g stroke={`url(#met${tipo})`} strokeWidth="3" strokeLinejoin="round" strokeLinecap="round">
        {formas[tipo]}
      </g>
    </svg>
  );
}

const pilares = [
  {
    titulo: 'Vocabulário próprio',
    texto: 'given, cycle, action, blueprint. As palavras descrevem a intenção de quem escreve, não a mecânica da máquina.',
  },
  {
    titulo: 'Tipos verificados',
    texto: 'Um analisador estático confere nomes, aridade e tipos antes de rodar — e fica calado quando não consegue provar o erro.',
  },
  {
    titulo: 'Pattern matching',
    texto: 'match estrutural sobre tipo, sequência, mapa, record e enum, com guardas em when.',
  },
  {
    titulo: 'Records e enums',
    texto: 'Dados imutáveis com igualdade estrutural e cópia por with. Enums com valores associados.',
  },
  {
    titulo: 'Pipelines nativos',
    texto: 'sift, morph e distill encadeados com >>, lidos de cima para baixo como o dado flui.',
  },
  {
    titulo: 'Generators preguiçosos',
    texto: 'stream action com emit produz valores sob demanda — inclusive em sequências infinitas.',
  },
  {
    titulo: 'Zero dependências',
    texto: 'O runtime inteiro usa apenas a biblioteca padrão do Python. Instala e roda.',
  },
];

export function Pilares() {
  const [ativo, setAtivo] = useState<number | null>(null);

  return (
    <section className="relative overflow-hidden px-4 py-24 sm:px-10 sm:py-32">
      <div className="mx-auto max-w-[1280px]">
        <TextoRevelado
          texto="DataForge é uma linguagem completa: analisada, verificada e interpretada por código próprio."
          className="lp-h2 mx-auto max-w-[22ch] text-center"
        />
      </div>

      {/* O leque: as cartas se abrem no hover, como na captura */}
      <div className="mt-20 flex overflow-x-auto pb-10 pt-6 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        <div className="mx-auto flex shrink-0 px-6">
          {pilares.map((p, i) => {
            const meio = (pilares.length - 1) / 2;
            const desvio = i - meio;
            const acesa = ativo === i;
            return (
              <button
                key={p.titulo}
                onMouseEnter={() => setAtivo(i)}
                onMouseLeave={() => setAtivo(null)}
                onFocus={() => setAtivo(i)}
                onBlur={() => setAtivo(null)}
                aria-label={p.titulo}
                className="lp-card group relative -mx-4 flex h-[250px] w-[200px] shrink-0 flex-col items-center justify-center rounded-[22px] px-4 text-center sm:-mx-7 sm:h-[272px] sm:w-[224px]"
                style={{
                  transform: acesa
                    ? 'rotate(0deg) translateY(-22px) scale(1.045)'
                    : `rotate(${desvio * 2.6}deg) translateY(${Math.abs(desvio) * 9}px)`,
                  zIndex: acesa ? 30 : 10 + i,
                  transition: 'transform .45s cubic-bezier(.16,1,.3,1), border-color .3s ease',
                  borderColor: acesa ? 'rgba(234,40,69,.5)' : undefined,
                  boxShadow: acesa ? '0 34px 70px -22px rgba(0,0,0,.9)' : '0 18px 44px -26px rgba(0,0,0,.8)',
                }}
              >
                <Glifo tipo={i} />
                <h3 className="mt-5 text-[17px] font-semibold leading-tight text-white">
                  {p.titulo}
                </h3>
                <p
                  className="lp-mono mt-3 text-[12px] leading-[19px] text-white/60"
                  style={{
                    opacity: acesa ? 1 : 0,
                    transform: acesa ? 'none' : 'translateY(6px)',
                    transition: 'opacity .32s ease, transform .32s ease',
                  }}
                >
                  {p.texto}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      <Sobe className="mx-auto mt-6 max-w-[1280px]">
        <p className="lp-mono text-center text-[12px] text-white/35">
          passe o cursor sobre uma carta
        </p>
      </Sobe>
    </section>
  );
}
