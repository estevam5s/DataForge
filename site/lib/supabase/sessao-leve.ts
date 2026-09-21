'use client';

/**
 * "Há alguém com sessão aberta?" — a pergunta mínima, para o cabeçalho.
 *
 * ─── Por que não usar o `ProvedorAuth` ──────────────────────────
 *
 * O cabeçalho aparece em **todas** as páginas do site, inclusive nas
 * 500 de documentação, que são estáticas e não têm nada a ver com
 * conta. Envolver a raiz no `ProvedorAuth` faria cada uma delas
 * carregar o perfil do banco, abrir a assinatura de mudança de estado
 * e manter um cliente Supabase vivo — para desenhar **um botão**.
 *
 * Este hook responde só o que o botão precisa: existe sessão, ou não.
 * Nada de perfil, nada de papel, nada de consulta ao banco.
 *
 * ─── E por que não ler o `localStorage` direto ──────────────────
 *
 * Seria mais barato e estaria errado de duas formas: a chave de
 * armazenamento é um detalhe interno do SDK (muda entre versões), e um
 * token **expirado** continua lá. `getSession()` responde pelo estado
 * de verdade, e `onAuthStateChange` mantém a resposta viva quando a
 * pessoa entra ou sai numa outra aba.
 *
 * ─── O terceiro estado importa ──────────────────────────────────
 *
 * `null` é "ainda não sei", e é diferente de `false`. Sem ele, o
 * cabeçalho desenharia "Entrar / Criar conta" no primeiro quadro e
 * trocaria por "Painel" um instante depois — o pulo que faz a página
 * parecer quebrada para quem já está autenticado. Enquanto for `null`
 * o cabeçalho não desenha nenhum dos dois.
 */

import { useEffect, useState } from 'react';
import { configurado, obterCliente } from './cliente';

export function useTemSessao(): boolean | null {
  // `configurado` é falso quando o site roda sem as variáveis do
  // Supabase (uma prévia, um fork). Ali não há login possível, e
  // responder `false` de cara evita um estado de carregamento que
  // nunca termina.
  const [tem, setTem] = useState<boolean | null>(configurado ? null : false);

  useEffect(() => {
    if (!configurado) return;
    const cliente = obterCliente();
    if (!cliente) {
      setTem(false);
      return;
    }

    let vivo = true;

    cliente.auth
      .getSession()
      .then(({ data }) => {
        if (vivo) setTem(Boolean(data.session));
      })
      .catch(() => {
        // Sem rede, ou o Supabase fora do ar: o cabeçalho não pode
        // ficar num carregamento eterno por causa disso. "Não há
        // sessão" é a resposta segura — ela mostra "Entrar", e quem
        // já estava autenticado entra de novo com um clique.
        if (vivo) setTem(false);
      });

    const { data: assinatura } = cliente.auth.onAuthStateChange(
      (_evento, sessao) => {
        if (vivo) setTem(Boolean(sessao));
      },
    );

    return () => {
      vivo = false;
      assinatura.subscription.unsubscribe();
    };
  }, []);

  return tem;
}
