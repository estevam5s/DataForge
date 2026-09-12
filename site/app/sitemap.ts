import type { MetadataRoute } from 'next';
import { nav } from '@/lib/nav';

/**
 * O mapa do site, gerado da navegação.
 *
 * Não havia sitemap — `/sitemap.xml` dava 404 — e o site tem 96 páginas
 * de documentação. Um buscador as acha seguindo links, mas as mais
 * fundas (o módulo 32 dos exercícios, a referência da Vitrine) levam
 * três ou quatro saltos, e o rastreador desiste antes.
 *
 * A lista sai de `nav.ts`, que é a mesma fonte da barra lateral: uma
 * segunda lista aqui divergiria, e um sitemap que aponta para uma
 * página removida é pior que nenhum.
 */
const BASE = 'https://dataforge-lang.vercel.app';

/** As rotas que não estão na navegação da documentação. */
const AVULSAS = ['/', '/download', '/instalar', '/api'];

export const dynamic = 'force-static';

export default function sitemap(): MetadataRoute.Sitemap {
  const daNav = nav.flatMap((secao) => secao.items.map((item) => item.href));

  // `Set` porque `/api` está na nav E em AVULSAS: uma rota repetida no
  // sitemap é ignorada por uns rastreadores e reclamada por outros.
  const rotas = Array.from(new Set([...AVULSAS, ...daNav]));

  return rotas.map((rota) => ({
    url: `${BASE}${rota === '/' ? '' : rota}`,
    lastModified: new Date(),
    // A home e o download primeiro; a documentação depois. Sem isso
    // tudo tem o mesmo peso, e o peso deixa de dizer algo.
    priority: rota === '/' ? 1 : rota === '/download' ? 0.9 : 0.7,
    changeFrequency: rota.startsWith('/docs') ? 'weekly' : 'monthly',
  }));
}
