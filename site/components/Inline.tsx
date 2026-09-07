import Link from 'next/link';
import type { ReactNode } from 'react';

/**
 * Renderiza a marcação leve usada no conteúdo: `código`, **negrito**,
 * *itálico* e [texto](/rota).
 *
 * É deliberadamente pequeno — um parser de Markdown completo seria peso morto
 * para o subconjunto que a documentação usa.
 */
export function Inline({ texto }: { texto: string }) {
  const partes: ReactNode[] = [];
  // A ordem dos grupos define a precedência: link, código, negrito, itálico.
  const padrao = /\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*/g;

  let ultimo = 0;
  let m: RegExpExecArray | null;
  let chave = 0;

  while ((m = padrao.exec(texto)) !== null) {
    if (m.index > ultimo) partes.push(texto.slice(ultimo, m.index));

    if (m[1] !== undefined) {
      const href = m[2];
      const externo = /^https?:/.test(href);
      partes.push(
        externo ? (
          <a key={chave++} href={href} target="_blank" rel="noreferrer noopener">
            {m[1]}
          </a>
        ) : (
          <Link key={chave++} href={href}>
            {m[1]}
          </Link>
        )
      );
    } else if (m[3] !== undefined) {
      partes.push(<code key={chave++}>{m[3]}</code>);
    } else if (m[4] !== undefined) {
      partes.push(<strong key={chave++}>{m[4]}</strong>);
    } else if (m[5] !== undefined) {
      partes.push(<em key={chave++}>{m[5]}</em>);
    }
    ultimo = m.index + m[0].length;
  }
  if (ultimo < texto.length) partes.push(texto.slice(ultimo));

  return <>{partes}</>;
}
