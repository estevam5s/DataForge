'use client';

import { useEffect, useRef, useState } from 'react';

/** Dispara uma vez quando o elemento entra na viewport. */
export function useVisivel<T extends HTMLElement>(margem = '-12% 0px') {
  const ref = useRef<T>(null);
  const [visivel, setVisivel] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => e.isIntersecting && setVisivel(true),
      { rootMargin: margem },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [margem]);

  return { ref, visivel };
}

/**
 * Rótulo `{ TEXTO _` datilografado, com cursor piscando.
 * Na captura os rótulos aparecem meio digitados — a animação
 * começa quando a seção entra na tela.
 */
export function Rotulo({
  texto,
  className = '',
  fecha = false,
}: {
  texto: string;
  className?: string;
  /** Rótulo numérico fecha a chave — `{ 2 }_` — como na contagem de grupos. */
  fecha?: boolean;
}) {
  const { ref, visivel } = useVisivel<HTMLDivElement>();
  const [n, setN] = useState(0);

  useEffect(() => {
    if (!visivel) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setN(texto.length);
      return;
    }
    const id = setInterval(() => {
      setN((v) => {
        if (v >= texto.length) { clearInterval(id); return v; }
        return v + 1;
      });
    }, 42);
    return () => clearInterval(id);
  }, [visivel, texto]);

  return (
    <div
      ref={ref}
      className={`lp-label flex items-center whitespace-pre ${className}`}
      aria-label={texto}
    >
      <span aria-hidden>{'{ '}</span>
      <span aria-hidden>{texto.slice(0, n)}</span>
      {fecha && n >= texto.length && <span aria-hidden>{' }'}</span>}
      <span aria-hidden className="lp-caret ml-1">_</span>
    </div>
  );
}

/**
 * Revelação palavra a palavra conforme a seção atravessa a tela.
 * É o efeito de assinatura da página: o texto sai do cinza-escuro
 * para o branco na medida do scroll, e não de uma vez só.
 */
export function TextoRevelado({
  texto,
  className = '',
  as: Tag = 'h2',
}: {
  texto: string;
  className?: string;
  as?: 'h2' | 'p';
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [progresso, setProgresso] = useState(0);
  const palavras = texto.split(' ');

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setProgresso(1);
      return;
    }

    let frame = 0;
    const medir = () => {
      frame = 0;
      const r = el.getBoundingClientRect();
      const alt = window.innerHeight;
      // 0 quando o topo entra por baixo; 1 quando o bloco chega a 35% da tela
      const p = (alt - r.top) / (alt * 0.62 + r.height * 0.5);
      setProgresso(Math.min(1, Math.max(0, p)));
    };
    const aoRolar = () => {
      if (!frame) frame = requestAnimationFrame(medir);
    };

    medir();
    window.addEventListener('scroll', aoRolar, { passive: true });
    window.addEventListener('resize', aoRolar);
    return () => {
      window.removeEventListener('scroll', aoRolar);
      window.removeEventListener('resize', aoRolar);
      if (frame) cancelAnimationFrame(frame);
    };
  }, []);

  return (
    <div ref={ref}>
      <Tag className={className}>
        {palavras.map((p, i) => {
          // cada palavra acende um pouco depois da anterior
          const inicio = i / palavras.length;
          const t = Math.min(1, Math.max(0, (progresso - inicio) / (1.15 / palavras.length)));
          return (
            <span
              key={i}
              style={{
                color: `rgba(255,255,255,${0.14 + t * 0.86})`,
                filter: t < 1 ? `blur(${(1 - t) * 5}px)` : 'none',
                transition: 'color 90ms linear, filter 90ms linear',
              }}
            >
              {p}
              {i < palavras.length - 1 ? ' ' : ''}
            </span>
          );
        })}
      </Tag>
    </div>
  );
}

/** Sobe e revela quando entra na tela — usado nos blocos menores. */
export function Sobe({
  children,
  atraso = 0,
  className = '',
}: {
  children: React.ReactNode;
  atraso?: number;
  className?: string;
}) {
  const { ref, visivel } = useVisivel<HTMLDivElement>();
  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: visivel ? 1 : 0,
        transform: visivel ? 'none' : 'translateY(18px)',
        transition: `opacity .7s cubic-bezier(.16,1,.3,1) ${atraso}ms, transform .7s cubic-bezier(.16,1,.3,1) ${atraso}ms`,
      }}
    >
      {children}
    </div>
  );
}
