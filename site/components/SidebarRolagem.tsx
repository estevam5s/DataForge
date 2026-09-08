'use client';

import { usePathname } from 'next/navigation';
import { useEffect, useRef } from 'react';

const CHAVE = 'dataforge:sidebar-scroll';

/**
 * Mantém a rolagem da barra lateral ao trocar de página.
 *
 * O problema: com 190 rotas, a barra rola muito. Ao navegar, o React
 * remonta o container e a posição volta a zero — quem estava em
 * "Pacotes", lá embaixo, era jogado de volta ao topo e precisava rolar
 * tudo de novo a cada clique.
 *
 * A posição é guardada em `sessionStorage`, não em estado: ela precisa
 * sobreviver à remontagem **e** ao recarregar a página, mas não deve
 * durar entre sessões — voltar amanhã no meio da lista seria estranho.
 *
 * Depois de restaurar, se o item ativo ficou fora de vista (porque a
 * seção dele abriu e empurrou a lista), ele é trazido para o centro.
 */
export function SidebarRolagem({ children }: { children: React.ReactNode }) {
  const caixa = useRef<HTMLDivElement>(null);
  const rota = usePathname();

  useEffect(() => {
    const elemento = caixa.current;
    if (!elemento) return;

    // Restaura antes da primeira pintura para não haver salto visível.
    try {
      const guardado = sessionStorage.getItem(CHAVE);
      if (guardado) elemento.scrollTop = Number(guardado);
    } catch {
      /* armazenamento bloqueado: a barra simplesmente começa no topo */
    }

    // O item ativo só existe depois que a seção dele abre, o que leva
    // um quadro. Sem o rAF, a busca não acha nada.
    const quadro = requestAnimationFrame(() => {
      const ativo = elemento.querySelector('[aria-current="page"]');
      if (!ativo) return;

      const caixaRect = elemento.getBoundingClientRect();
      const itemRect = ativo.getBoundingClientRect();
      const forade = itemRect.top < caixaRect.top + 8
        || itemRect.bottom > caixaRect.bottom - 8;

      if (forade) {
        ativo.scrollIntoView({ block: 'center', behavior: 'auto' });
      }
    });

    const aoRolar = () => {
      try {
        sessionStorage.setItem(CHAVE, String(elemento.scrollTop));
      } catch {
        /* idem */
      }
    };
    elemento.addEventListener('scroll', aoRolar, { passive: true });

    return () => {
      cancelAnimationFrame(quadro);
      elemento.removeEventListener('scroll', aoRolar);
    };
  }, [rota]);

  return (
    <div
      ref={caixa}
      className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-2.5 py-4 [scrollbar-width:thin]"
    >
      {children}
    </div>
  );
}
