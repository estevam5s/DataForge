'use client';

import Link from 'next/link';

/**
 * A faixa que passa embaixo do herói — o lugar onde um site de produto
 * põe os logos de quem usa.
 *
 * Aqui não há logos de clientes para mostrar, e inventá-los seria
 * mentira. O que existe de verdade é **com o que a linguagem fala**:
 * cada item abaixo é um módulo da biblioteca padrão ou uma ponte que
 * roda, com a página que a explica. Um item que não existisse seria
 * um link quebrado, e o teste de links internos reprovaria.
 *
 * A faixa é duplicada no DOM e deslocada em -50%: é o que faz o laço
 * fechar sem salto. `prefers-reduced-motion` para a animação — quem
 * pediu menos movimento não deve receber um carrossel infinito.
 */
const TECNOLOGIAS: { nome: string; href: string }[] = [
  { nome: 'Python', href: '/docs/tecnicas/ponte' },
  { nome: 'SQLite', href: '/docs/sqlite' },
  { nome: 'HTTP', href: '/docs/kiln' },
  { nome: 'WebSocket', href: '/docs/kiln/tempo-real' },
  { nome: 'Telegram', href: '/docs/telegram' },
  { nome: 'Arduino', href: '/docs/iot' },
  { nome: 'Docker', href: '/docs/devops' },
  { nome: 'Prometheus', href: '/docs/observabilidade/metricas' },
  { nome: 'Parquet', href: '/docs/tecnicas/parquet' },
  { nome: 'Excel', href: '/docs/tecnicas/planilhas' },
  { nome: 'C / FFI', href: '/docs/ffi' },
  { nome: 'OpenAPI', href: '/docs/api/contrato' },
];

export function Tecnologias() {
  const fila = [...TECNOLOGIAS, ...TECNOLOGIAS];

  return (
    <section aria-labelledby="tec-titulo" className="relative px-4 sm:px-10">
      <div className="mx-auto max-w-[1280px] border-y border-white/10 py-6">
        <h2 id="tec-titulo" className="lp-mono mb-5 text-center text-[11px] uppercase tracking-[0.22em] text-white/40">
          Fala com
        </h2>

        {/* As bordas desbotadas escondem o corte nas duas pontas. */}
        <div className="lp-marquee-mask relative overflow-hidden">
          <ul className="lp-marquee flex w-max items-center gap-3">
            {fila.map((t, i) => (
              <li key={`${t.nome}-${i}`}>
                <Link
                  href={t.href}
                  aria-hidden={i >= TECNOLOGIAS.length}
                  tabIndex={i >= TECNOLOGIAS.length ? -1 : 0}
                  className="lp-mono flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-[13px] text-white/60 transition-colors hover:border-white/25 hover:text-white"
                >
                  <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-[var(--lp-accent)]" />
                  {t.nome}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
