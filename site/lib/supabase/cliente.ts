import { createClient, type SupabaseClient } from '@supabase/supabase-js';

/**
 * Cliente do Supabase.
 *
 * As credenciais vêm de variáveis de ambiente. Enquanto não estiverem
 * configuradas, `supabase` é null e o painel entra em modo demonstração
 * — mostra a interface com dados de exemplo em vez de quebrar.
 *
 * Para ligar de verdade, crie `site/.env.local`:
 *
 *     NEXT_PUBLIC_SUPABASE_URL=https://seu-projeto.supabase.co
 *     NEXT_PUBLIC_SUPABASE_ANON_KEY=sua-chave-anon
 *
 * A chave `anon` é pública por natureza — vai no bundle e o navegador a
 * enxerga. É a RLS (Row Level Security) que protege os dados, não o
 * segredo da chave. A `service_role` NUNCA entra aqui: ela ignora RLS.
 */

export const URL_SUPABASE = process.env.NEXT_PUBLIC_SUPABASE_URL ?? '';
export const CHAVE_ANON = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? '';

/** Há credenciais configuradas? */
export const configurado = Boolean(URL_SUPABASE && CHAVE_ANON);

let instancia: SupabaseClient | null = null;

/**
 * O cliente, ou null quando falta credencial.
 *
 * Criado sob demanda e uma vez só: o Supabase mantém a sessão em
 * memória, e duas instâncias brigariam pelo refresh do token.
 */
export function obterCliente(): SupabaseClient | null {
  if (!configurado) return null;
  if (instancia) return instancia;

  instancia = createClient(URL_SUPABASE, CHAVE_ANON, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  });
  return instancia;
}

/** Mensagem de erro do Supabase traduzida para o que fazer. */
export function traduzirErro(mensagem: string): string {
  const mapa: Record<string, string> = {
    'Invalid login credentials':
      'E-mail ou senha incorretos.',
    'Email not confirmed':
      'Confirme seu e-mail antes de entrar — veja a caixa de entrada.',
    'User already registered':
      'Já existe uma conta com este e-mail. Tente entrar.',
    'Password should be at least 6 characters':
      'A senha precisa de ao menos 6 caracteres.',
    'Unable to validate email address: invalid format':
      'Esse e-mail não parece válido.',
    'For security purposes, you can only request this after 60 seconds':
      'Aguarde um minuto antes de tentar de novo.',
  };
  for (const [ingles, portugues] of Object.entries(mapa)) {
    if (mensagem.includes(ingles)) return portugues;
  }
  return mensagem;
}
