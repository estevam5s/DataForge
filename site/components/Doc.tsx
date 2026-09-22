import Link from 'next/link';
import type { ReactNode } from 'react';
import { neighbours, sectionOf } from '@/lib/nav';
import { Toc, type Heading } from './Toc';
import { Redimensionavel } from './Redimensionavel';
import { Inline } from './Inline';
import { Footer } from './Footer';

/** Transforma um texto de título no id usado pela âncora. */
export function slugify(texto: string) {
  return texto
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-');
}

/** Título de seção com âncora clicável. */
export function H2({ children }: { children: string }) {
  const id = slugify(children);
  return (
    <h2 id={id} className="group">
      <a href={`#${id}`} className="!no-underline !text-strong">
        {children}
        <span className="ml-2 text-accent opacity-0 transition-opacity group-hover:opacity-100">#</span>
      </a>
    </h2>
  );
}

export function H3({ children }: { children: string }) {
  const id = slugify(children);
  return (
    <h3 id={id} className="group">
      <a href={`#${id}`} className="!no-underline !text-strong">
        {children}
        <span className="ml-2 text-accent opacity-0 transition-opacity group-hover:opacity-100">#</span>
      </a>
    </h3>
  );
}

/** Caixa de destaque: dica, atenção ou perigo. */
export function Callout({
  tipo = 'dica',
  titulo,
  children,
}: {
  tipo?: 'dica' | 'atencao' | 'perigo' | 'nota';
  titulo?: string;
  children: ReactNode;
}) {
  const estilos = {
    dica: { borda: 'border-l-emerald-400/70', rotulo: 'text-emerald-400', padrao: 'Dica' },
    nota: { borda: 'border-l-sky-400/70', rotulo: 'text-sky-400', padrao: 'Nota' },
    atencao: { borda: 'border-l-amber-400/70', rotulo: 'text-amber-400', padrao: 'Atenção' },
    perigo: { borda: 'border-l-accent', rotulo: 'text-accent', padrao: 'Cuidado' },
  }[tipo];

  return (
    <aside className={`my-6 rounded-r-lg border-l-2 bg-raised/45 px-5 py-4 ${estilos.borda}`}>
      <p className={`nav-label mb-1.5 ${estilos.rotulo}`}>{titulo ?? estilos.padrao}</p>
      <div className="[&>p:first-child]:mt-0 [&>p:last-child]:mb-0 text-[14.5px]">{children}</div>
    </aside>
  );
}

/** Grade de cartões para páginas-índice. */
export function CardGrid({ children }: { children: ReactNode }) {
  return <div className="my-8 grid gap-3 sm:grid-cols-2">{children}</div>;
}

export function Card({
  href,
  title,
  children,
  meta,
}: {
  href: string;
  title: string;
  children?: ReactNode;
  meta?: string;
}) {
  return (
    <Link
      href={href}
      className="group surface-card block p-5 transition-colors hover:border-accent/45 hover:bg-raised/70"
    >
      <div className="flex items-start justify-between gap-3">
        <p className="font-semibold text-strong transition-colors group-hover:text-accent">
          {title}
        </p>
        {meta && (
          <span className="shrink-0 rounded-md border border-line px-1.5 py-px font-mono text-[11px] text-muted">
            {meta}
          </span>
        )}
      </div>
      {children && <p className="mt-1.5 text-[13.5px] leading-[21px] text-muted">{children}</p>}
    </Link>
  );
}

/** Tabela simples a partir de dados — evita repetir markup. */
export function Table({
  head,
  rows,
}: {
  head: string[];
  rows: (ReactNode)[][];
}) {
  return (
    <div className="my-6 overflow-x-auto">
      <table>
        <thead>
          <tr>{head.map((h, i) => <th key={i}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((linha, i) => (
            <tr key={i}>{linha.map((c, k) => <td key={k}>{c}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * Moldura de uma página de documentação: título, conteúdo, índice lateral
 * e a navegação anterior/próxima no rodapé.
 */
export function DocPage({
  title,
  description,
  href,
  headings = [],
  children,
}: {
  title: string;
  description?: string;
  href: string;
  headings?: Heading[];
  children: ReactNode;
}) {
  const { prev, next } = neighbours(href);
  const secao = sectionOf(href);

  return (
    /* O RODAPÉ FICA DENTRO DESTA LINHA, na coluna do texto.
     *
     * `position: sticky` só gruda enquanto o elemento está dentro do
     * container dele. Com o rodapé fora deste flex, o container
     * terminava onde o artigo terminava — e o "Nesta página"
     * desgrudava na última tela, que é justamente onde quem leu tudo
     * ainda quer pular para outra seção.
     *
     * É a mesma correção que a barra ESQUERDA já tinha recebido (ver o
     * comentário em `app/docs/layout.tsx`); a da direita ficou de fora.
     */
    <div className="flex w-full min-w-0 items-stretch gap-10">
      <div className="min-w-0 flex-1">
      <article className="entra-conteudo min-w-0 px-1 py-8 sm:px-2 lg:py-10">
        <div className="max-w-content">
          {secao && !secao.standalone && (
            <p className="nav-label mb-3 text-accent">{secao.title}</p>
          )}
          <div className="prose-df animate-fade-up">
            <h1>{title}</h1>
            {description && (
              <p className="!mt-0 !mb-8 text-[17px] leading-[28px] text-muted">
                <Inline texto={description} />
              </p>
            )}
            {children}
          </div>

          <nav className="mt-16 grid gap-3 border-t border-line pt-8 sm:grid-cols-2">
            {prev ? (
              <Link
                href={prev.href}
                className="surface-card group p-4 transition-colors hover:border-accent/45"
              >
                <p className="mb-1 text-[12px] text-muted">Anterior</p>
                <p className="font-semibold text-strong transition-colors group-hover:text-accent">
                  ← {prev.title}
                </p>
              </Link>
            ) : (
              <span />
            )}
            {next && (
              <Link
                href={next.href}
                className="surface-card group p-4 text-right transition-colors hover:border-accent/45 sm:col-start-2"
              >
                <p className="mb-1 text-[12px] text-muted">Próximo</p>
                <p className="font-semibold text-strong transition-colors group-hover:text-accent">
                  {next.title} →
                </p>
              </Link>
            )}
          </nav>
        </div>
      </article>
        <Footer />
      </div>

      {/* O índice também é redimensionável, e pelo lado de dentro: um
          título longo cabia em 220 px na base e não cabe em toda
          página. */}
      <Redimensionavel
        id="docs-indice"
        lado="direita"
        padrao={220}
        minimo={170}
        maximo={420}
        rotulo="Largura do índice desta página"
        className="hidden xl:block"
      >
        {/* `data-toc-rolagem`: é este contêiner que o índice rola
            para acompanhar o título ativo, e só ele. Sem a marca, o
            `Toc` teria de adivinhar qual ancestral rola — e erraria
            para a janela, puxando a página junto. */}
        <div
          data-toc-rolagem
          className="sticky top-[100px] max-h-[calc(100vh-130px)] overflow-y-auto py-10"
        >
          <Toc headings={headings} />
        </div>
      </Redimensionavel>
    </div>
  );
}
