'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * O comando de instalação, grande, com um holofote que segue o mouse.
 *
 * O texto fica apagado e só o que está sob o cursor acende. É feito com
 * `background-clip: text` e um gradiente radial posicionado por duas
 * variáveis CSS — nada de JavaScript pintando caractere por caractere.
 *
 * Quatro cuidados:
 *
 * 1. **A posição vai por variável CSS, não por estado do React.** Mover
 *    o mouse dispara dezenas de eventos por segundo; re-renderizar a
 *    árvore em cada um deixa o efeito travado. Aqui o React não
 *    re-renderiza: o handler escreve `--x`/`--y` no nó.
 * 2. **Sem mouse, o texto fica LEGÍVEL.** Num celular não há cursor, e
 *    um texto que só acende sob o ponteiro seria invisível. O estado
 *    inicial é o holofote no centro, e `@media (hover: none)` acende
 *    tudo.
 * 3. **`prefers-reduced-motion` acende tudo também.**
 * 4. **Clicar copia.** É o que a linha embaixo promete, e uma promessa
 *    dessas precisa funcionar no primeiro clique.
 */

const COMANDOS = [
  'curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh',
  'dataforge new minha-api --modelo=api',
];

export function Instalar() {
  const caixa = useRef<HTMLDivElement>(null);
  const [copiado, setCopiado] = useState<number | null>(null);

  const aoMover = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const el = caixa.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    el.style.setProperty('--x', `${((e.clientX - r.left) / r.width) * 100}%`);
    el.style.setProperty('--y', `${((e.clientY - r.top) / r.height) * 100}%`);
  }, []);

  const aoSair = useCallback(() => {
    const el = caixa.current;
    if (!el) return;
    el.style.setProperty('--x', '50%');
    el.style.setProperty('--y', '50%');
  }, []);

  useEffect(() => {
    if (copiado === null) return;
    const t = setTimeout(() => setCopiado(null), 1600);
    return () => clearTimeout(t);
  }, [copiado]);

  async function copiar(texto: string, i: number) {
    try {
      await navigator.clipboard.writeText(texto);
      setCopiado(i);
    } catch {
      // Área de transferência negada (http, permissão): selecionar o
      // texto é o melhor que dá para fazer, e é melhor que nada
      // acontecer.
      const alvo = document.getElementById(`cmd-${i}`);
      if (alvo) {
        const faixa = document.createRange();
        faixa.selectNodeContents(alvo);
        const sel = window.getSelection();
        sel?.removeAllRanges();
        sel?.addRange(faixa);
      }
    }
  }

  return (
    <section className="relative border-t border-[var(--lp-line)] px-4 py-24 sm:px-10 sm:py-32">
      <div
        ref={caixa}
        onMouseMove={aoMover}
        onMouseLeave={aoSair}
        className="lp-holofote mx-auto max-w-[1280px] py-6 sm:py-10"
        style={{ ['--x' as string]: '50%', ['--y' as string]: '50%' }}
      >
        {COMANDOS.map((cmd, i) => (
          <button
            key={cmd}
            type="button"
            onClick={() => copiar(cmd, i)}
            className="block w-full cursor-pointer text-left"
            aria-label={`Copiar: ${cmd}`}
          >
            <span
              id={`cmd-${i}`}
              className="lp-holofote-linha block truncate py-2 text-[clamp(1.05rem,3.4vw,2.9rem)] font-medium leading-[1.3] tracking-tight"
            >
              <span aria-hidden className="text-[0.85em] opacity-70">$ </span>
              {cmd}
            </span>
          </button>
        ))}

        <p className="lp-mono mt-10 text-center text-[11px] tracking-[2px] text-white/30">
          {copiado === null
            ? '{ CLIQUE. COPIE. CONSTRUA. }'
            : '{ COPIADO }'}
        </p>
      </div>
    </section>
  );
}
