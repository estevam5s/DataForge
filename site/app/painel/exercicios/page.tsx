'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import {
  listarProgresso, marcarExercicio, type Progresso,
} from '@/lib/supabase/dados';
import dados from '@/lib/dados-gerados.json';

type Exercicio = { num: string; titulo: string; arquivo: string };
const MODULOS = Object.entries(
  dados.exercicios as Record<string, Exercicio[]>,
);

export default function Exercicios() {
  const [feitos, setFeitos] = useState<Record<string, boolean>>({});
  const [carregando, setCarregando] = useState(true);
  const [aberto, setAberto] = useState<string | null>(MODULOS[0]?.[0] ?? null);

  useEffect(() => {
    listarProgresso().then((r) => {
      const mapa: Record<string, boolean> = {};
      for (const p of r.dados as Progresso[]) {
        mapa[p.exercicio] = p.concluido;
      }
      setFeitos(mapa);
      setCarregando(false);
    });
  }, []);

  async function alternar(exercicio: string, modulo: string) {
    const novo = !feitos[exercicio];
    setFeitos((atual) => ({ ...atual, [exercicio]: novo }));   // otimista
    const erro = await marcarExercicio(exercicio, modulo, novo);
    if (erro) {
      // desfaz se o servidor recusou
      setFeitos((atual) => ({ ...atual, [exercicio]: !novo }));
    }
  }

  const total = useMemo(
    () => MODULOS.reduce((n, [, lista]) => n + lista.length, 0), []);
  const concluidos = Object.values(feitos).filter(Boolean).length;
  const pct = total ? Math.round((concluidos / total) * 100) : 0;

  return (
    <>
      <Cabecalho
        titulo="Exercícios"
        descricao="Marque o que já resolveu. O progresso fica salvo na sua conta."
      />

      <div className="surface-card mb-6 rounded-xl p-5">
        <div className="flex items-baseline justify-between">
          <span className="text-[14px] font-semibold text-strong">
            {concluidos} de {total}
          </span>
          <span className="text-[13px] text-muted">{pct}%</span>
        </div>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-raised">
          <div className="h-full rounded-full bg-accent transition-all"
               style={{ width: `${pct}%` }} />
        </div>
      </div>

      {carregando ? (
        <p className="text-[14px] text-muted">carregando…</p>
      ) : (
        <div className="space-y-2">
          {MODULOS.map(([modulo, lista]) => {
            const feitosNoModulo = lista.filter(
              (e) => feitos[e.arquivo.replace('.df', '')]).length;
            const estaAberto = aberto === modulo;

            return (
              <div key={modulo} className="surface-card overflow-hidden rounded-xl">
                <button
                  onClick={() => setAberto(estaAberto ? null : modulo)}
                  className="flex w-full items-center gap-3 px-5 py-3.5 text-left
                             transition-colors hover:bg-raised/60"
                  aria-expanded={estaAberto}
                >
                  <span className="flex-1 font-semibold text-strong">
                    {modulo.replace(/^\d+-/, '').replace(/-/g, ' ')}
                  </span>
                  <span className="text-[13px] text-muted">
                    {feitosNoModulo}/{lista.length}
                  </span>
                  <svg viewBox="0 0 24 24" className={`h-4 w-4 text-muted
                       transition-transform ${estaAberto ? 'rotate-90' : ''}`}
                       fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
                    <path d="m9 6 6 6-6 6" />
                  </svg>
                </button>

                {estaAberto && (
                  <ul className="border-t border-line">
                    {lista.map((e) => {
                      const chave = e.arquivo.replace('.df', '');
                      const feito = Boolean(feitos[chave]);
                      return (
                        <li key={chave}
                            className="flex items-center gap-3 border-b border-line
                                       px-5 py-2.5 last:border-0">
                          <input
                            type="checkbox"
                            checked={feito}
                            onChange={() => alternar(chave, modulo)}
                            id={chave}
                            className="accent-[rgb(var(--accent))]"
                          />
                          <label htmlFor={chave}
                                 className={`flex-1 cursor-pointer text-[13.5px] ${
                                   feito ? 'text-muted line-through' : 'text-body'}`}>
                            <span className="lp-mono text-muted">{e.num}</span>
                            {' · '}{e.titulo}
                          </label>
                          <Link href={`/docs/exercicios/${modulo}`}
                                className="text-[12.5px] text-muted hover:text-accent">
                            ver
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}
