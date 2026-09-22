'use client';

import { useEffect, useRef, useState } from 'react';

export type Heading = { id: string; text: string; level: 2 | 3 };

/**
 * Índice "Nesta página". Acompanha a rolagem destacando a seção visível.
 *
 * ─── Duas coisas que ele precisa fazer, e não fazia ─────────────
 *
 * 1. **Acompanhar sozinho.** Numa página com trinta títulos o índice
 *    é mais alto que a tela, e o item destacado saía de vista: a
 *    pessoa rolava o texto, o marcador vermelho descia para fora do
 *    índice, e para vê-lo era preciso rolar o índice **à mão**. Um
 *    índice que exige ser rolado para mostrar onde você está deixou
 *    de responder à única pergunta dele.
 *
 * 2. **Mostrar `código` como código.** O texto vem dos títulos, e
 *    título de referência costuma ser um nome de arquivo ou de rota
 *    (`` `/api/sintaxe.json` ``). Sem tratamento, as crases apareciam
 *    literais na tela — o índice de `/api` era uma coluna de acentos
 *    graves.
 */
export function Toc({ headings }: { headings: Heading[] }) {
  const [ativo, setAtivo] = useState<string>('');
  const lista = useRef<HTMLUListElement>(null);

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
      { rootMargin: '-88px 0px -70% 0px', threshold: 0 },
    );

    const alvos = headings
      .map((h) => document.getElementById(h.id))
      .filter((e): e is HTMLElement => e !== null);
    alvos.forEach((e) => observador.observe(e));
    return () => observador.disconnect();
  }, [headings]);

  /* ── O índice acompanha o item ativo ──────────────────────────
   *
   * `scrollIntoView` está DE FORA de propósito: ele rola todos os
   * ancestrais roláveis, e o de cima é a janela. O índice puxaria a
   * página junto — a pessoa rolaria o texto e o texto pularia sozinho,
   * que é pior que o problema original.
   *
   * Aqui a conta é feita à mão e escrita num contêiner só: o do
   * próprio índice. E só quando o item está FORA da faixa visível —
   * rolar um item que já está à vista faria a coluna tremer a cada
   * título que passa.
   */
  useEffect(() => {
    if (!ativo || !lista.current) return;

    const caixa = lista.current.closest<HTMLElement>('[data-toc-rolagem]');
    if (!caixa) return;

    const item = lista.current.querySelector<HTMLElement>(
      `[data-id="${CSS.escape(ativo)}"]`,
    );
    if (!item) return;

    const margem = 24;
    const topoDoItem = item.offsetTop - caixa.offsetTop;
    const fimDoItem = topoDoItem + item.offsetHeight;
    const topoVisivel = caixa.scrollTop;
    const fimVisivel = topoVisivel + caixa.clientHeight;

    if (topoDoItem < topoVisivel + margem) {
      caixa.scrollTo({ top: Math.max(0, topoDoItem - margem), behavior: 'smooth' });
    } else if (fimDoItem > fimVisivel - margem) {
      caixa.scrollTo({
        top: fimDoItem - caixa.clientHeight + margem,
        behavior: 'smooth',
      });
    }
  }, [ativo]);

  if (headings.length === 0) return null;

  return (
    <nav aria-label="Nesta página" className="text-[13.5px]">
      <p className="nav-label mb-3 text-muted">Nesta página</p>
      <ul ref={lista} className="space-y-px border-l border-line">
        {headings.map((h) => {
          const ativoAqui = ativo === h.id;
          return (
            <li key={h.id} data-id={h.id}>
              <a
                href={`#${h.id}`}
                aria-current={ativoAqui ? 'location' : undefined}
                className={`-ml-px block border-l-2 py-1.5 transition-colors ${
                  h.level === 3 ? 'pl-7' : 'pl-4'
                } ${
                  ativoAqui
                    ? 'border-accent font-medium text-accent'
                    : 'border-transparent text-muted hover:text-strong'
                }`}
              >
                <ComCodigo texto={h.text} />
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

/** `crase` vira <code>, como no resto do site. */
function ComCodigo({ texto }: { texto: string }) {
  if (!texto.includes('`')) return <>{texto}</>;
  return (
    <>
      {texto.split(/(`[^`]+`)/g).map((parte, i) =>
        parte.startsWith('`') && parte.endsWith('`') && parte.length > 2 ? (
          <code
            key={i}
            className="rounded bg-raised/70 px-1 py-px text-[0.92em] tracking-tight"
          >
            {parte.slice(1, -1)}
          </code>
        ) : (
          <span key={i}>{parte}</span>
        ),
      )}
    </>
  );
}
