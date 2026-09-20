'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

type Lado = 'esquerda' | 'direita';

/**
 * Um painel lateral cuja largura quem lê decide.
 *
 * As duas barras da documentação tinham largura fixa — 248 px à
 * esquerda e 220 px à direita — e isso é uma aposta sobre o conteúdo
 * alheio. Um nome como `Arcane.Arquivo_Seguro.abrir_zip_seguro` não
 * cabe em 248 px e vira reticências; num monitor largo, sobra tela de
 * um lado e falta do outro. Quem lê sabe o que precisa ver.
 *
 * ─── Quatro decisões ────────────────────────────────────────────
 *
 * 1. **A largura é escrita no DOM durante o arrasto, e no estado só no
 *    fim.** Um `setState` por evento de ponteiro re-renderiza a árvore
 *    inteira da barra — com 190 rotas e as seções animadas, isso é
 *    trabalho suficiente para o arrasto engasgar. Durante o movimento o
 *    que muda é uma propriedade CSS; o React só fica sabendo quando o
 *    dedo sai.
 *
 * 2. **O valor guardado é lido DEPOIS da hidratação.** Ler
 *    `localStorage` no render daria um HTML diferente do que o servidor
 *    gerou, e o React descarta a árvore inteira quando isso acontece.
 *    O padrão aparece primeiro e o valor de quem lê entra no primeiro
 *    efeito — sem salto visível, porque a transição de largura é
 *    desligada até o primeiro arrasto.
 *
 * 3. **Teclado faz o mesmo que o mouse.** O puxador é um `separator`
 *    focável: setas movem de 16 em 16 px, com Shift de 64, Home e End
 *    vão aos limites, e Enter volta ao padrão. Uma barra que só
 *    responde ao arrasto é uma barra que não existe para quem navega
 *    por teclado — e a régua ARIA (`aria-valuenow`) é o que faz um
 *    leitor de tela anunciar a largura em vez de "separador".
 *
 * 4. **O clique duplo devolve o padrão.** É a saída de quem arrastou
 *    demais e não quer descobrir qual era o número.
 *
 * O armazenamento é por leitor e por navegador: ele pode vir vazio, ou
 * lançar (janela privada, dados bloqueados), e a página tem de
 * funcionar igual nos dois casos — daí o `try` em toda leitura e
 * escrita.
 */
export function Redimensionavel({
  id,
  lado,
  padrao,
  minimo,
  maximo,
  rotulo,
  className = '',
  children,
}: {
  id: string;
  lado: Lado;
  padrao: number;
  minimo: number;
  maximo: number;
  rotulo: string;
  className?: string;
  children: React.ReactNode;
}) {
  const [largura, setLargura] = useState(padrao);
  const [arrastando, setArrastando] = useState(false);
  const [restaurado, setRestaurado] = useState(false);
  const painel = useRef<HTMLElement>(null);
  const atual = useRef(padrao);

  const chave = `dataforge:largura:${id}`;

  const limitar = useCallback(
    (valor: number) => Math.min(maximo, Math.max(minimo, Math.round(valor))),
    [minimo, maximo]
  );

  useEffect(() => {
    try {
      const guardado = Number(window.localStorage.getItem(chave));
      if (Number.isFinite(guardado) && guardado > 0) {
        const valor = limitar(guardado);
        atual.current = valor;
        setLargura(valor);
      }
    } catch {
      /* armazenamento bloqueado: fica o padrão, e nada quebra */
    }
    setRestaurado(true);
  }, [chave, limitar]);

  const fixar = useCallback(
    (valor: number) => {
      const novo = limitar(valor);
      atual.current = novo;
      setLargura(novo);
      try {
        window.localStorage.setItem(chave, String(novo));
      } catch {
        /* idem */
      }
    },
    [chave, limitar]
  );

  const aoPegar = (evento: React.PointerEvent<HTMLDivElement>) => {
    // Só o botão principal: um arrasto com o botão do meio cola texto
    // em alguns sistemas, e com o direito abre o menu.
    if (evento.button !== 0) return;
    evento.preventDefault();

    const puxador = evento.currentTarget;
    puxador.setPointerCapture(evento.pointerId);
    setArrastando(true);

    const inicioX = evento.clientX;
    const inicioLargura = atual.current;

    const mover = (e: PointerEvent) => {
      const delta = lado === 'esquerda' ? e.clientX - inicioX : inicioX - e.clientX;
      const valor = limitar(inicioLargura + delta);
      atual.current = valor;
      // Direto no DOM: ver a decisão 1, no topo.
      if (painel.current) painel.current.style.width = `${valor}px`;
      puxador.setAttribute('aria-valuenow', String(valor));
    };

    const soltar = () => {
      puxador.removeEventListener('pointermove', mover);
      puxador.removeEventListener('pointerup', soltar);
      puxador.removeEventListener('pointercancel', soltar);
      setArrastando(false);
      fixar(atual.current);
    };

    puxador.addEventListener('pointermove', mover);
    puxador.addEventListener('pointerup', soltar);
    puxador.addEventListener('pointercancel', soltar);
  };

  const aoTeclar = (evento: React.KeyboardEvent<HTMLDivElement>) => {
    const passo = evento.shiftKey ? 64 : 16;
    const cresce = lado === 'esquerda' ? 'ArrowRight' : 'ArrowLeft';
    const encolhe = lado === 'esquerda' ? 'ArrowLeft' : 'ArrowRight';

    if (evento.key === cresce) fixar(atual.current + passo);
    else if (evento.key === encolhe) fixar(atual.current - passo);
    else if (evento.key === 'Home') fixar(lado === 'esquerda' ? minimo : maximo);
    else if (evento.key === 'End') fixar(lado === 'esquerda' ? maximo : minimo);
    else if (evento.key === 'Enter' || evento.key === ' ') fixar(padrao);
    else return;

    evento.preventDefault();
  };

  // Enquanto arrasta, o cursor e a ausência de seleção valem para a
  // PÁGINA inteira: sem isso, sair do puxador com o botão apertado
  // troca o cursor e começa a selecionar o texto da doc.
  useEffect(() => {
    if (!arrastando) return;
    const corpo = document.body;
    const cursor = corpo.style.cursor;
    const selecao = corpo.style.userSelect;
    corpo.style.cursor = 'col-resize';
    corpo.style.userSelect = 'none';
    return () => {
      corpo.style.cursor = cursor;
      corpo.style.userSelect = selecao;
    };
  }, [arrastando]);

  const naBorda =
    lado === 'esquerda' ? '-right-3 justify-start' : '-left-3 justify-end';

  return (
    <aside
      ref={painel}
      style={{ width: `${largura}px` }}
      data-redimensionavel={id}
      className={`relative shrink-0 self-stretch ${
        // A transição entra só depois de restaurar: com ela ligada, o
        // valor de quem lê chegaria animando a partir do padrão.
        restaurado && !arrastando ? 'transition-[width] duration-200' : ''
      } ${className}`}
    >
      {children}

      <div
        role="separator"
        aria-orientation="vertical"
        aria-label={rotulo}
        aria-valuenow={largura}
        aria-valuemin={minimo}
        aria-valuemax={maximo}
        aria-valuetext={`${largura} pixels`}
        tabIndex={0}
        onPointerDown={aoPegar}
        onKeyDown={aoTeclar}
        onDoubleClick={() => fixar(padrao)}
        data-arrastando={arrastando ? 'sim' : undefined}
        title="Arraste para redimensionar · duplo clique volta ao padrão"
        className={`group absolute top-[84px] z-20 hidden h-[calc(100vh-140px)] w-6 cursor-col-resize touch-none select-none items-center ${naBorda} lg:flex`}
      >
        {/* A linha fica discreta e acende no hover, no foco e durante o
            arrasto — um traço sempre aceso a mais na tela concorre com
            o texto, e a barra lateral já tem borda. */}
        <span
          aria-hidden="true"
          className="mx-auto h-full w-px rounded-full bg-line/0 transition-colors duration-150 group-hover:bg-accent/60 group-focus-visible:bg-accent data-[arrastando]:bg-accent"
        />
        <span
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-1/2 flex -translate-x-1/2 -translate-y-1/2 flex-col gap-[3px] rounded-full bg-raised/90 px-[3px] py-2 opacity-0 shadow-sm ring-1 ring-line transition-opacity duration-150 group-hover:opacity-100 group-focus-visible:opacity-100"
        >
          <i className="h-[3px] w-[3px] rounded-full bg-muted" />
          <i className="h-[3px] w-[3px] rounded-full bg-muted" />
          <i className="h-[3px] w-[3px] rounded-full bg-muted" />
        </span>
      </div>
    </aside>
  );
}
