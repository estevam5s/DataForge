/**
 * Conteúdo das páginas como dados.
 *
 * Cada página é uma lista de blocos. Isso mantém o conteúdo separado do
 * markup, deixa as 120+ páginas consistentes entre si e torna trivial gerar
 * as páginas que derivam do código real (biblioteca padrão, exercícios).
 */

export type Bloco =
  | { h2: string }
  | { h3: string }
  | { p: string }
  | { code: string; lang?: 'df' | 'bash' | 'toml' | 'json' | 'text'; title?: string }
  | { list: string[]; ordered?: boolean }
  | { table: { head: string[]; rows: string[][] } }
  | { callout: { tipo?: 'dica' | 'nota' | 'atencao' | 'perigo'; titulo?: string; texto: string } }
  | { cards: { href: string; title: string; desc?: string; meta?: string }[] }
  | { hr: true };

export type Pagina = {
  /** Rota, sempre começando com '/'. */
  href: string;
  title: string;
  description?: string;
  blocos: Bloco[];
};

/**
 * Marcação leve aceita dentro de `p`, itens de lista e células de tabela:
 *
 *   `código`        → <code>
 *   **negrito**     → <strong>
 *   *itálico*       → <em>
 *   [texto](/rota)  → <Link>
 */
export type Inline = string;
