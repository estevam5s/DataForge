import Link from 'next/link';
import { CodeBlock } from '@/components/CodeBlock';

export const metadata = { title: 'Página não encontrada' };

const trecho = `monitor:
    adopt Doc.Rota as r
    out r.buscar("${'/'}...")
handle erro:
    out "essa rota nao existe — tente a busca (⌘K)"`;

export default function NaoEncontrada() {
  return (
    <div className="mx-auto max-w-content py-24">
      <p className="nav-label mb-3 text-accent">Erro 404</p>
      <h1 className="mb-4 text-[40px] font-extrabold leading-[1.1] tracking-[-0.02em] text-strong">
        Página não encontrada
      </h1>
      <p className="mb-8 text-[17px] leading-[28px] text-muted">
        A rota que você pediu não existe nesta documentação. Use a busca no topo
        (<kbd className="rounded border border-line bg-raised px-1.5 py-0.5 text-[12px]">⌘K</kbd>)
        ou comece por um destes pontos:
      </p>

      <CodeBlock code={trecho} lang="df" />

      <div className="mt-8 grid gap-3 sm:grid-cols-3">
        {[
          { href: '/', title: 'Introdução', texto: 'O que é a linguagem' },
          { href: '/primeiros-passos', title: 'Primeiros passos', texto: 'Do zero ao primeiro .df' },
          { href: '/biblioteca', title: 'Biblioteca', texto: '20 módulos, 674 símbolos' },
        ].map((c) => (
          <Link key={c.href} href={c.href} className="surface-card group p-4 transition-colors hover:border-accent/45">
            <p className="font-semibold text-strong transition-colors group-hover:text-accent">
              {c.title}
            </p>
            <p className="mt-1 text-[13px] text-muted">{c.texto}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
