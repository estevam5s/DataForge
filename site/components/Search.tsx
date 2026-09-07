'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { nav, allRoutes, sectionOf } from '@/lib/nav';

/**
 * Busca por título de página, aberta com ⌘K / Ctrl+K.
 *
 * O índice são as próprias rotas — suficiente para um site de documentação
 * com pouco mais de cem páginas, e sem depender de serviço externo.
 */
export function Search() {
  const [aberto, setAberto] = useState(false);
  const [termo, setTermo] = useState('');
  const [selecionado, setSelecionado] = useState(0);
  const campo = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const resultados = useMemo(() => {
    const t = termo.trim().toLowerCase();
    if (!t) return allRoutes.slice(0, 8);
    const normalizar = (s: string) =>
      s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    const alvo = normalizar(t);
    return allRoutes
      .map((r) => {
        const titulo = normalizar(r.title);
        const secao = normalizar(sectionOf(r.href)?.title ?? '');
        // Prefixo do título pesa mais que ocorrência no meio ou na seção
        let peso = -1;
        if (titulo.startsWith(alvo)) peso = 0;
        else if (titulo.includes(alvo)) peso = 1;
        else if (r.href.includes(alvo)) peso = 2;
        else if (secao.includes(alvo)) peso = 3;
        return { rota: r, peso };
      })
      .filter((x) => x.peso >= 0)
      .sort((a, b) => a.peso - b.peso)
      .slice(0, 12)
      .map((x) => x.rota);
  }, [termo]);

  const fechar = useCallback(() => {
    setAberto(false);
    setTermo('');
    setSelecionado(0);
  }, []);

  useEffect(() => {
    const aoTeclar = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setAberto((v) => !v);
      }
      if (e.key === 'Escape') fechar();
    };
    window.addEventListener('keydown', aoTeclar);
    return () => window.removeEventListener('keydown', aoTeclar);
  }, [fechar]);

  useEffect(() => {
    if (aberto) setTimeout(() => campo.current?.focus(), 30);
  }, [aberto]);

  useEffect(() => setSelecionado(0), [termo]);

  const navegarComTeclado = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelecionado((i) => Math.min(i + 1, resultados.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelecionado((i) => Math.max(i - 1, 0));
    } else if (e.key === 'Enter' && resultados[selecionado]) {
      e.preventDefault();
      router.push(resultados[selecionado].href);
      fechar();
    }
  };

  return (
    <>
      <button
        onClick={() => setAberto(true)}
        className="flex w-full max-w-[300px] items-center gap-2.5 rounded-xl border border-line bg-raised/60 px-3.5 py-2 text-left text-[13.5px] text-muted transition-colors hover:border-line hover:bg-raised"
        aria-label="Buscar na documentação"
      >
        <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="7" cy="7" r="4.6" stroke="currentColor" strokeWidth="1.6" />
          <path d="M10.6 10.6 14 14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
        <span className="flex-1">Buscar</span>
        <kbd className="hidden rounded border border-line bg-base px-1.5 py-px font-sans text-[11px] text-muted sm:block">
          ⌘K
        </kbd>
      </button>

      {aberto && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center bg-black/65 px-4 pt-[12vh] backdrop-blur-sm"
          onClick={fechar}
          role="dialog"
          aria-modal="true"
          aria-label="Busca"
        >
          <div
            className="w-full max-w-[560px] overflow-hidden rounded-2xl border border-line bg-surface shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 border-b border-line px-4">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="text-muted" aria-hidden="true">
                <circle cx="7" cy="7" r="4.6" stroke="currentColor" strokeWidth="1.6" />
                <path d="M10.6 10.6 14 14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
              </svg>
              <input
                ref={campo}
                value={termo}
                onChange={(e) => setTermo(e.target.value)}
                onKeyDown={navegarComTeclado}
                placeholder="Buscar páginas, módulos, exercícios…"
                className="flex-1 bg-transparent py-3.5 text-[15px] text-strong outline-none placeholder:text-muted"
                aria-label="Termo de busca"
              />
              <kbd className="rounded border border-line px-1.5 py-px text-[11px] text-muted">esc</kbd>
            </div>

            <ul className="max-h-[52vh] overflow-y-auto p-2">
              {resultados.length === 0 && (
                <li className="px-3 py-8 text-center text-[14px] text-muted">
                  Nada encontrado para <span className="text-strong">{termo}</span>.
                </li>
              )}
              {resultados.map((r, i) => (
                <li key={r.href}>
                  <Link
                    href={r.href}
                    onClick={fechar}
                    onMouseEnter={() => setSelecionado(i)}
                    className={`flex items-center justify-between rounded-lg px-3 py-2.5 text-[14px] transition-colors ${
                      i === selecionado ? 'bg-accent/12 text-strong' : 'text-body hover:bg-raised'
                    }`}
                  >
                    <span>{r.title}</span>
                    <span className="ml-3 shrink-0 text-[12px] text-muted">
                      {sectionOf(r.href)?.title}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>

            <div className="flex items-center gap-4 border-t border-line px-4 py-2 text-[11.5px] text-muted">
              <span><kbd className="font-sans">↑↓</kbd> navegar</span>
              <span><kbd className="font-sans">↵</kbd> abrir</span>
              <span><kbd className="font-sans">esc</kbd> fechar</span>
              <span className="ml-auto">{allRoutes.length} páginas</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
