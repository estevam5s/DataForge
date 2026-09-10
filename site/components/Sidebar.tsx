'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { nav } from '@/lib/nav';

function Chevron({ aberto }: { aberto: boolean }) {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 16 16"
      fill="none"
      className={`shrink-0 opacity-60 transition-transform duration-300 ${
        aberto ? '' : '-rotate-90'
      }`}
      aria-hidden="true"
    >
      <path
        d="M4 6l4 4 4-4"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function Selo({ texto }: { texto: string }) {
  return (
    <span className="rounded-full border border-accent/30 bg-accent/10 px-1.5 py-px text-[9.5px] font-bold uppercase leading-[15px] tracking-wide text-accent">
      {texto}
    </span>
  );
}

/**
 * Uma seção que abre e fecha com altura animada.
 *
 * `height: auto` não anima. Medimos o conteúdo e animamos até a altura
 * exata; ao terminar, soltamos para `auto` — senão uma seção que muda de
 * tamanho depois (por quebra de linha, por zoom) fica cortada.
 */
function Painel({ aberto, children, id }: { aberto: boolean; children: React.ReactNode; id: string }) {
  const conteudo = useRef<HTMLDivElement>(null);
  const [altura, setAltura] = useState<number | undefined>(aberto ? undefined : 0);

  useEffect(() => {
    const elemento = conteudo.current;
    if (!elemento) return;

    if (aberto) {
      setAltura(elemento.scrollHeight);
      const t = setTimeout(() => setAltura(undefined), 300);
      return () => clearTimeout(t);
    }
    // Fixa a altura atual antes de ir a zero: de `auto` não há transição.
    setAltura(elemento.scrollHeight);
    const t = requestAnimationFrame(() => setAltura(0));
    return () => cancelAnimationFrame(t);
  }, [aberto]);

  return (
    <div
      id={id}
      style={{ height: altura }}
      className="overflow-hidden transition-[height] duration-300 ease-[cubic-bezier(.22,1,.36,1)]"
      aria-hidden={!aberto}
    >
      <div ref={conteudo}>{children}</div>
    </div>
  );
}

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname() ?? '/';
  const atual = pathname.replace(/\/$/, '') || '/';

  // Aberta fica UMA seção: a que contém a página atual.
  //
  // Antes este efeito só acrescentava — nunca tirava. Cada navegação
  // deixava a seção anterior aberta, e depois de alguns cliques a barra
  // estava com tudo escancarado: era preciso rolar por 190 rotas para
  // achar a de baixo. Duas seções ainda abriam sozinhas na primeira
  // visita, então até `/docs`, que não pertence a seção nenhuma, já
  // começava expandido.
  //
  // Trocar o conjunto inteiro a cada rota dá o comportamento de
  // sanfona. Abrir outras à mão continua valendo: o clique manda até a
  // próxima navegação.
  const secaoDaRota = (caminho: string) =>
    nav.find((s) => s.items.some((i) => i.href === caminho))?.title;

  const [abertas, setAbertas] = useState<Set<string>>(() => {
    const dona = secaoDaRota(atual);
    return new Set(dona ? [dona] : []);
  });

  useEffect(() => {
    const dona = secaoDaRota(atual);
    setAbertas(new Set(dona ? [dona] : []));
  }, [atual]);

  const alternar = (titulo: string) =>
    setAbertas((anteriores) => {
      const proximas = new Set(anteriores);
      proximas.has(titulo) ? proximas.delete(titulo) : proximas.add(titulo);
      return proximas;
    });

  return (
    <nav aria-label="Navegação da documentação" className="pb-2">
      {nav.map((secao) => {
        const unico = secao.standalone && secao.items.length === 1;

        if (unico) {
          const item = secao.items[0];
          const ativo = item.href === atual;
          return (
            <Link
              key={secao.title}
              href={item.href}
              onClick={onNavigate}
              className={`nav-label block rounded-lg px-2.5 py-[6px] transition-colors ${
                ativo ? 'text-accent' : 'text-body hover:text-strong'
              }`}
            >
              {secao.title}
            </Link>
          );
        }

        const aberta = abertas.has(secao.title);
        const contemAtual = secao.items.some((i) => i.href === atual);
        const idPainel = `secao-${secao.title.replace(/\s+/g, '-').toLowerCase()}`;

        return (
          <div key={secao.title}>
            <button
              onClick={() => alternar(secao.title)}
              aria-expanded={aberta}
              aria-controls={idPainel}
              className={`nav-label flex w-full items-center justify-between rounded-lg px-2.5 py-[6px] transition-colors ${
                contemAtual ? 'text-strong' : 'text-body hover:text-strong'
              }`}
            >
              <span className="flex items-center gap-2 text-left">
                {secao.badge && <Selo texto={secao.badge} />}
                {secao.title}
              </span>
              <span className="flex shrink-0 items-center gap-1.5">
                {/* Quantas páginas há ali dentro. Com 20 seções e 190
                    rotas, saber o tamanho antes de abrir evita expandir
                    a seção errada — e some quando ela está aberta, que
                    é quando a contagem deixa de importar. */}
                <span
                  className={`text-[10px] tabular-nums transition-opacity duration-200 ${
                    aberta ? 'opacity-0' : 'opacity-40'
                  }`}
                  aria-hidden="true"
                >
                  {secao.items.length}
                </span>
                <Chevron aberto={aberta} />
              </span>
            </button>

            <Painel aberto={aberta} id={idPainel}>
              <ul className="mb-0.5 ml-[15px] space-y-0 border-l border-line/60 pl-2">
                {secao.items.map((item) => {
                  const ativo = item.href === atual;
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        onClick={onNavigate}
                        aria-current={ativo ? 'page' : undefined}
                        tabIndex={aberta ? undefined : -1}
                        className={`group relative block rounded-md py-[4.5px] pl-2.5 pr-2 text-[12.5px] leading-[18px] transition-all duration-200 ${
                          ativo
                            ? 'bg-accent/10 font-medium text-accent'
                            : 'text-muted hover:translate-x-0.5 hover:text-strong'
                        }`}
                      >
                        {/* A barra do item ativo cresce a partir do centro */}
                        <span
                          className={`absolute -left-[9px] top-1/2 w-[2px] -translate-y-1/2 rounded-full bg-accent transition-all duration-300 ${
                            ativo ? 'h-[14px] opacity-100' : 'h-0 opacity-0'
                          }`}
                          aria-hidden="true"
                        />
                        <span className="flex items-center gap-1.5">
                          {item.badge && <Selo texto={item.badge} />}
                          {item.title}
                        </span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </Painel>
          </div>
        );
      })}
    </nav>
  );
}
