'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { Cabecalho, Icone, ROTAS_PAINEL } from '@/components/painel/Casca';
import { useAuth } from '@/lib/supabase/auth';
import {
  listarAnotacoes, listarProgresso, listarProjetos, listarTrechos,
} from '@/lib/supabase/dados';
import dados from '@/lib/dados-gerados.json';

const TOTAL_EXERCICIOS = Object.values(
  dados.exercicios as Record<string, unknown[]>,
).reduce((n, l) => n + l.length, 0);

export default function Inicio() {
  const { usuario } = useAuth();
  const [n, setN] = useState({ projetos: 0, trechos: 0, anotacoes: 0, feitos: 0 });
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    Promise.all([
      listarProjetos(), listarTrechos(), listarAnotacoes(), listarProgresso(),
    ]).then(([p, t, a, g]) => {
      setN({
        projetos: p.dados.length,
        trechos: t.dados.length,
        anotacoes: a.dados.length,
        feitos: g.dados.filter((x) => x.concluido).length,
      });
      setCarregando(false);
    });
  }, []);

  const nome = (usuario?.user_metadata?.nome as string)
    ?? usuario?.email?.split('@')[0] ?? 'você';
  const pct = Math.round((n.feitos / TOTAL_EXERCICIOS) * 100);

  return (
    <>
      <Cabecalho
        titulo={`Olá, ${nome}`}
        descricao="O que você guardou e onde parou."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Numero rotulo="Projetos" valor={n.projetos} href="/painel/projetos"
                carregando={carregando} />
        <Numero rotulo="Trechos" valor={n.trechos} href="/painel/trechos"
                carregando={carregando} />
        <Numero rotulo="Anotações" valor={n.anotacoes} href="/painel/anotacoes"
                carregando={carregando} />
        <Numero rotulo="Exercícios" valor={n.feitos}
                sufixo={`/ ${TOTAL_EXERCICIOS}`} href="/painel/exercicios"
                carregando={carregando} />
      </div>

      <section className="surface-card mt-6 rounded-xl p-6">
        <div className="flex items-baseline justify-between">
          <h2 className="font-semibold text-strong">Progresso nos exercícios</h2>
          <span className="text-[13px] text-muted">{pct}%</span>
        </div>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-raised">
          <div className="h-full rounded-full bg-accent transition-all"
               style={{ width: `${pct}%` }} />
        </div>
        <p className="mt-3 text-[13.5px] text-muted">
          {n.feitos === 0
            ? 'Comece pelo módulo 01 — doze exercícios de fundamentos.'
            : `${n.feitos} de ${TOTAL_EXERCICIOS} concluídos. Continue de onde parou.`}
        </p>
      </section>

      <section className="mt-8">
        <h2 className="mb-3 font-semibold text-strong">Ir para</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {ROTAS_PAINEL.filter((r) => r.href !== '/painel').map((r) => (
            <Link key={r.href} href={r.href}
                  className="surface-card group flex items-start gap-3 rounded-xl
                             p-4 transition-colors hover:border-accent/40">
              <span className="mt-0.5 text-accent"><Icone nome={r.icone} /></span>
              <span>
                <span className="block font-semibold text-strong
                                 transition-colors group-hover:text-accent">
                  {r.titulo}
                </span>
                <span className="block text-[13px] text-muted">{r.desc}</span>
              </span>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}

function Numero({ rotulo, valor, sufixo, href, carregando }: {
  rotulo: string; valor: number; sufixo?: string;
  href: string; carregando: boolean;
}) {
  return (
    <Link href={href} className="surface-card rounded-xl p-5 transition-colors
                                 hover:border-accent/40">
      <p className="text-[12px] uppercase tracking-wider text-muted">{rotulo}</p>
      <p className="mt-1.5 text-[28px] font-bold leading-none text-strong">
        {carregando ? '—' : valor}
        {sufixo && <span className="text-[15px] font-normal text-muted">
          {' '}{sufixo}</span>}
      </p>
    </Link>
  );
}
