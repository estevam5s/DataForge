import type { MetadataRoute } from 'next';

/**
 * Tudo é público, e o sitemap fica anunciado aqui.
 *
 * Um `robots.txt` ausente não bloqueia nada — mas também não diz onde
 * está o sitemap, e é por ele que a maioria dos rastreadores o
 * descobre.
 */
export const dynamic = 'force-static';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [{ userAgent: '*', allow: '/' }],
    sitemap: 'https://dataforge-lang.vercel.app/sitemap.xml',
  };
}
