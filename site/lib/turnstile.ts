/**
 * Cloudflare Turnstile — a proteção contra robô na entrada do painel.
 *
 * ─── Onde cada chave mora, e por quê ────────────────────────────
 *
 * | Chave      | Onde                                   | Pode ser vista? |
 * |------------|----------------------------------------|-----------------|
 * | **site**   | aqui, no pacote do navegador           | **sim**, por desenho |
 * | **secret** | painel do Supabase (Auth → Attack Protection) | **nunca** |
 *
 * A chave de site é pública: ela vai no HTML de toda página que mostra
 * o widget, e qualquer pessoa a lê com "ver código-fonte". Esconder-la
 * não protegeria nada — quem valida o desafio é o servidor, com a
 * outra chave.
 *
 * A chave secreta **não está neste repositório e não deve estar**. Há
 * teste procurando por ela (`test_a_chave_SECRETA_do_turnstile_nao_esta_no_repositorio`).
 *
 * ─── Quem verifica o token ──────────────────────────────────────
 *
 * Não somos nós. O site é exportado como arquivos estáticos — não há
 * servidor nosso no caminho do login —, e o navegador fala direto com
 * o Supabase. Um widget cujo token o *nosso* JavaScript conferisse
 * seria **decoração**: o robô não abriria esta página, chamaria o
 * endpoint de autenticação do Supabase direto.
 *
 * Quem tem de recusar é quem recebe a senha. O Supabase tem suporte
 * nativo a Turnstile: com a proteção ligada no projeto, `signIn`,
 * `signUp` e `resetPasswordForEmail` **exigem** o token, e o servidor
 * dele confere com a Cloudflare (`/siteverify`) antes de olhar a
 * senha. É por isso que o token vai em `options.captchaToken` e não
 * num `fetch` nosso.
 *
 * Enquanto a proteção não estiver ligada lá, o widget aparece e o
 * token é ignorado pelo servidor — a página não quebra, e a segurança
 * também não existe. Os dois lados são necessários, e a documentação
 * em `/docs/painel/seguranca` diz isso com todas as letras.
 */

/** A chave de SITE. Pública, e substituível por ambiente. */
export const CHAVE_DE_SITE =
  process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY ?? '0x4AAAAAAE90dNHbqVbe4OI8';

/** Há widget a mostrar? Sem chave, o formulário segue sem ele. */
export const TURNSTILE_LIGADO = Boolean(CHAVE_DE_SITE);

/** O endereço do script, com renderização explícita. */
export const SCRIPT_TURNSTILE =
  'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';

/**
 * As falhas do Turnstile, ditas em português e com o que fazer.
 *
 * O Supabase devolve o recado da Cloudflare quase cru
 * (`captcha protection: request disallowed (invalid-input-response)`),
 * e ele fala de um serviço que quem está entrando não sabe que existe.
 */
export function traduzirFalhaDeCaptcha(mensagem: string): string | null {
  const texto = mensagem.toLowerCase();
  if (!texto.includes('captcha')) return null;

  if (texto.includes('timeout-or-duplicate') || texto.includes('already-seen')) {
    return 'A verificação expirou. Ela foi refeita — tente enviar de novo.';
  }
  if (texto.includes('missing-input-response')) {
    return 'Conclua a verificação "não sou um robô" antes de enviar.';
  }
  if (texto.includes('invalid-input-secret') || texto.includes('invalid-input-response')) {
    return 'A verificação anti-robô não foi aceita. Recarregue a página e tente de novo.';
  }
  return 'Não foi possível concluir a verificação anti-robô. Tente de novo.';
}
