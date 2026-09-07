'use client';

import { useEffect, useState } from 'react';

export type Heading = { id: string; text: string; level: 2 | 3 };

/**
 * Índice "Nesta página". Acompanha a rolagem destacando a seção visível,
 * como no layout de referência.
 */
export function Toc({ headings }: { headings: Heading[] }) {
  const [ativo, setAtivo] = useState<string>('');

  useEffect(() => {
    if (headings.length === 0) return;

    const observador = new IntersectionObserver(
      (entradas) => {
        const visiveis = entradas
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visiveis[0]) setAtivo(visiveis[0].target.id);
      },
      // A faixa estreita no topo evita que o último título "ganhe" a disputa
      { rootMargin: '-88px 0px -70% 0px', threshold: 0 }
    );

    const alvos = headings
      .map((h) => document.getElementById(h.id))
      .filter((e): e is HTMLElement => e !== null);
    alvos.forEach((e) => observador.observe(e));
    return () => observador.disconnect();
  }, [headings]);

  if (headings.length === 0) return null;

  return (
    <nav aria-label="Nesta página" className="text-[13.5px]">
      <p className="nav-label mb-3 text-muted">Nesta página</p>
      <ul className="space-y-px border-l border-line">
        {headings.map((h) => {
          const ativoAqui = ativo === h.id;
          return (
            <li key={h.id}>
              <a
                href={`#${h.id}`}
                className={`-ml-px block border-l-2 py-1.5 transition-colors ${
                  h.level === 3 ? 'pl-7' : 'pl-4'
                } ${
                  ativoAqui
                    ? 'border-accent font-medium text-accent'
                    : 'border-transparent text-muted hover:text-strong'
                }`}
              >
                {h.text}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
