'use client';

import { useEffect, useRef, useState } from 'react';

/**
 * Um número que conta do zero até o valor, quando entra na tela.
 *
 * Três cuidados que a versão ingênua erra:
 *
 * 1. **A largura não pode pular.** Um número que cresce de 1 para 2377
 *    empurra o que está ao lado a cada quadro. O `ch` reservado é o do
 *    valor FINAL, e o texto é alinhado à direita.
 * 2. **`prefers-reduced-motion` manda.** Para quem pediu menos
 *    movimento, o número aparece pronto — animação não é informação.
 * 3. **Sem `setInterval`.** Ele acumula atraso e desenha quadros que o
 *    navegador vai descartar; `requestAnimationFrame` desenha quando
 *    há o que pintar.
 *
 * A curva é `1 - (1 - t)^3`: rápida no começo e freando no fim, que é
 * o que faz o número parecer chegar em vez de parar.
 */
export function Contagem({
  valor,
  duracao = 1100,
  className = '',
}: {
  valor: number | null;
  duracao?: number;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const [mostrado, setMostrado] = useState<number | null>(null);

  useEffect(() => {
    if (valor === null) return;

    const menos =
      typeof window !== 'undefined' &&
      window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    if (menos) {
      setMostrado(valor);
      return;
    }

    const el = ref.current;
    if (!el) {
      setMostrado(valor);
      return;
    }

    let quadro = 0;
    let comecou = 0;
    let rede: ReturnType<typeof setTimeout> | undefined;

    const observador = new IntersectionObserver(
      ([entrada]) => {
        if (!entrada.isIntersecting) return;
        observador.disconnect();

        const passo = (agora: number) => {
          if (!comecou) comecou = agora;
          const t = Math.min(1, (agora - comecou) / duracao);
          const suave = 1 - (1 - t) ** 3;
          setMostrado(Math.round(valor * suave));
          if (t < 1) quadro = requestAnimationFrame(passo);
        };
        quadro = requestAnimationFrame(passo);

        // A REDE DE SEGURANÇA, e ela não é luxo.
        //
        // 'requestAnimationFrame' NÃO RODA em aba de fundo: o navegador
        // não tem o que pintar e para de chamar. Uma aba aberta em
        // segundo plano — o caso de quase todo link que alguém abre com
        // o meio do mouse — congela a contagem no quadro em que estava.
        //
        // E um número congelado no meio não parece quebrado: ele parece
        // um número. Medido aqui: 'Downloads do release' ficou em '1'
        // com o valor real em 16, e o único jeito de perceber era ler o
        // 'aria-label'. Um contador que mostra 1 onde há 16 é pior que
        // um contador que não anima.
        //
        // 'setTimeout' também é limitado em aba de fundo, mas ele
        // DISPARA — só mais tarde. Então o valor final sempre chega.
        rede = setTimeout(() => setMostrado(valor), duracao + 400);
      },
      { rootMargin: '-8% 0px' },
    );
    observador.observe(el);

    return () => {
      observador.disconnect();
      if (quadro) cancelAnimationFrame(quadro);
      if (rede) clearTimeout(rede);
    };
  }, [valor, duracao]);

  // Antes de a animação começar, mostra o VALOR — e não zero. Um zero
  // enquanto o observador não disparou é indistinguível de um zero
  // verdadeiro, e esta página tem um número que é zero de verdade
  // (estrelas).
  const texto =
    valor === null ? '—' : (mostrado ?? valor).toLocaleString('pt-BR');
  const largura = valor === null ? 1 : valor.toLocaleString('pt-BR').length;

  return (
    <span
      ref={ref}
      className={`inline-block text-right tabular-nums ${className}`}
      style={{ minWidth: `${largura}ch` }}
      // O leitor de tela anuncia o valor final, e não a contagem: a
      // animação é decoração, e ler 300 números seguidos seria ruído.
      aria-label={valor === null ? undefined : valor.toLocaleString('pt-BR')}
    >
      <span aria-hidden={valor !== null}>{texto}</span>
    </span>
  );
}
