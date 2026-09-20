'use client';

import { useCallback, useEffect, useImperativeHandle, useRef } from 'react';
import { CHAVE_DE_SITE, SCRIPT_TURNSTILE, TURNSTILE_LIGADO } from '@/lib/turnstile';

type Janela = Window & {
  turnstile?: {
    render: (alvo: HTMLElement, opcoes: Record<string, unknown>) => string;
    reset: (id?: string) => void;
    remove: (id?: string) => void;
  };
};

/** O que o formulário pode pedir ao widget. */
export type ControleTurnstile = {
  /** Descarta o token usado e pede outro. */
  reiniciar: () => void;
};

/**
 * O script entra na página UMA vez, mesmo com dois widgets.
 *
 * Em desenvolvimento o React monta cada efeito duas vezes de
 * propósito; sem esta promessa compartilhada, a segunda montagem
 * acrescentaria um segundo `<script>` e o `turnstile.render` correria
 * contra si mesmo.
 */
let carregando: Promise<void> | null = null;

function carregarScript(): Promise<void> {
  if (typeof window === 'undefined') return Promise.resolve();
  const janela = window as Janela;
  if (janela.turnstile) return Promise.resolve();
  if (carregando) return carregando;

  carregando = new Promise<void>((resolver, recusar) => {
    const existente = document.querySelector<HTMLScriptElement>(
      `script[src="${SCRIPT_TURNSTILE}"]`
    );
    const script = existente ?? document.createElement('script');
    script.src = SCRIPT_TURNSTILE;
    script.async = true;
    script.defer = true;
    script.addEventListener('load', () => resolver());
    script.addEventListener('error', () =>
      recusar(new Error('o script do Turnstile não carregou'))
    );
    if (!existente) document.head.appendChild(script);
  });
  return carregando;
}

/**
 * O desafio "não sou um robô" da Cloudflare, na entrada do painel.
 *
 * ─── Quatro coisas que este componente precisa acertar ──────────
 *
 * 1. **O token é de uso único.** Depois de enviado — deu certo ou não
 *    — ele não vale mais, e o próximo envio com o mesmo token volta
 *    como `timeout-or-duplicate`. Quem chama tem de chamar
 *    `reiniciar()` a cada tentativa; é por isso que o componente expõe
 *    um controle em vez de só devolver o token. Esquecer isso produz o
 *    defeito clássico: o primeiro login falha por senha errada, e o
 *    segundo — com a senha certa — falha por captcha, sem explicação.
 *
 * 2. **O token EXPIRA** (cerca de cinco minutos). O
 *    `expired-callback` zera o token, e o formulário volta a pedir a
 *    verificação em vez de mandar um token morto.
 *
 * 3. **A rede pode não deixar.** Em rede corporativa que bloqueia a
 *    Cloudflare o script não carrega; `aoFalhar` avisa quem chama, que
 *    decide entre bloquear o envio e seguir sem o token. Aqui a
 *    escolha é seguir: quem recusa de verdade é o Supabase, e um
 *    painel que não abre por causa de um bloqueio de rede seria pior
 *    que um envio recusado com mensagem clara.
 *
 * 4. **O widget morre com o componente.** `turnstile.remove` no
 *    desmonte: sem ele, trocar de modo (entrar → criar conta) deixaria
 *    widgets órfãos, e a Cloudflare conta cada um.
 */
export function Turnstile({
  aoMudarToken,
  aoFalhar,
  controle,
  acao,
}: {
  aoMudarToken: (token: string | null) => void;
  aoFalhar?: (motivo: string) => void;
  controle?: React.Ref<ControleTurnstile>;
  /** Aparece no painel da Cloudflare, separando login de cadastro. */
  acao?: string;
}) {
  const caixa = useRef<HTMLDivElement>(null);
  const identificador = useRef<string | null>(null);

  const reiniciar = useCallback(() => {
    const janela = window as Janela;
    if (janela.turnstile && identificador.current !== null) {
      janela.turnstile.reset(identificador.current);
      aoMudarToken(null);
    }
  }, [aoMudarToken]);

  useImperativeHandle(controle, () => ({ reiniciar }), [reiniciar]);

  useEffect(() => {
    if (!TURNSTILE_LIGADO) return;
    let vivo = true;

    carregarScript()
      .then(() => {
        const janela = window as Janela;
        if (!vivo || !janela.turnstile || !caixa.current) return;
        if (identificador.current !== null) return;

        identificador.current = janela.turnstile.render(caixa.current, {
          sitekey: CHAVE_DE_SITE,
          action: acao,
          theme: 'auto',
          language: 'pt-br',
          callback: (token: string) => aoMudarToken(token),
          'expired-callback': () => aoMudarToken(null),
          'timeout-callback': () => aoMudarToken(null),
          'error-callback': () => {
            aoMudarToken(null);
            aoFalhar?.('a verificação anti-robô não pôde ser carregada');
          },
        });
      })
      .catch(() => {
        if (!vivo) return;
        aoMudarToken(null);
        aoFalhar?.('a verificação anti-robô não pôde ser carregada');
      });

    return () => {
      vivo = false;
      const janela = window as Janela;
      if (janela.turnstile && identificador.current !== null) {
        janela.turnstile.remove(identificador.current);
        identificador.current = null;
      }
    };
    // `acao` muda ao trocar de modo, e aí o widget é remontado de
    // propósito: o desafio de "entrar" não vale para "criar conta".
  }, [acao, aoMudarToken, aoFalhar]);

  if (!TURNSTILE_LIGADO) return null;

  return (
    <div className="pt-0.5">
      <div ref={caixa} className="flex min-h-[65px] justify-center" />
    </div>
  );
}
