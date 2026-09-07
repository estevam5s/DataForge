'use client';

import { useEffect, useMemo, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import { CodeBlock } from '@/components/CodeBlock';

type Versao = { sha256: string; dependencias: Record<string, string> };
type Pacote = {
  descricao: string; licenca: string; tags: string[];
  versoes: Record<string, Versao>;
};

export default function Pacotes() {
  const [pacotes, setPacotes] = useState<Record<string, Pacote>>({});
  const [filtro, setFiltro] = useState('');
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    fetch('/registry/index.json')
      .then((r) => {
        if (!r.ok) throw new Error(`o registro respondeu ${r.status}`);
        return r.json();
      })
      .then((d) => { setPacotes(d.pacotes ?? {}); setCarregando(false); })
      .catch((e) => { setErro(String(e.message ?? e)); setCarregando(false); });
  }, []);

  const visiveis = useMemo(() => {
    const lista = Object.entries(pacotes);
    if (!filtro) return lista;
    const t = filtro.toLowerCase();
    return lista.filter(([nome, p]) =>
      (nome + p.descricao + (p.tags ?? []).join(' ')).toLowerCase().includes(t));
  }, [pacotes, filtro]);

  const ultimaVersao = (p: Pacote) =>
    Object.keys(p.versoes ?? {}).sort().pop() ?? '?';

  return (
    <>
      <Cabecalho
        titulo="Pacotes"
        descricao={`${Object.keys(pacotes).length} bibliotecas no registro oficial.`}
      />

      <input
        value={filtro} onChange={(e) => setFiltro(e.target.value)}
        placeholder="filtrar por nome, descrição ou tag"
        className="mb-5 w-full rounded-lg border border-line bg-raised px-3 py-2.5
                   text-[14px] text-strong outline-none placeholder:text-muted/60
                   focus:border-accent/50"
      />

      {erro && (
        <p role="alert" className="mb-5 rounded-lg border border-accent/30
                                   bg-accent/10 px-3 py-2 text-[13px] text-accent">
          Não consegui ler o registro: {erro}
        </p>
      )}

      {carregando ? (
        <p className="text-[14px] text-muted">carregando…</p>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {visiveis.map(([nome, p]) => (
            <article key={nome} className="surface-card rounded-xl p-5">
              <div className="flex items-baseline justify-between gap-3">
                <h2 className="lp-mono font-semibold text-strong">{nome}</h2>
                <span className="lp-mono shrink-0 text-[12px] text-muted">
                  {ultimaVersao(p)}
                </span>
              </div>
              <p className="mt-2 text-[13.5px] leading-[21px] text-muted">
                {p.descricao}
              </p>
              {(p.tags ?? []).length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {p.tags.map((t) => (
                    <span key={t} className="rounded-full bg-raised px-2 py-0.5
                                             text-[11px] text-muted">
                      #{t}
                    </span>
                  ))}
                </div>
              )}
              <div className="mt-4">
                <CodeBlock code={`dataforge add ${nome}`} lang="bash" />
              </div>
            </article>
          ))}
        </div>
      )}
    </>
  );
}
