'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { Cabecalho, Vazio } from '@/components/painel/Casca';
import {
  apagarAnotacao, listarAnotacoes, salvarAnotacao, type Anotacao,
} from '@/lib/supabase/dados';
import { allRoutes } from '@/lib/nav';

export default function Anotacoes() {
  const [itens, setItens] = useState<Anotacao[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [formAberto, setFormAberto] = useState(false);
  const [rota, setRota] = useState('/docs');
  const [titulo, setTitulo] = useState('');
  const [conteudo, setConteudo] = useState('');

  const recarregar = () =>
    listarAnotacoes().then((r) => {
      setItens(r.dados);
      setErro(r.erro);
      setCarregando(false);
    });

  useEffect(() => { recarregar(); }, []);

  async function salvar(e: React.FormEvent) {
    e.preventDefault();
    if (!conteudo.trim()) return;
    const r = await salvarAnotacao(rota, titulo.trim(), conteudo.trim());
    if (r.erro) { setErro(r.erro); return; }
    setTitulo(''); setConteudo(''); setFormAberto(false);
    recarregar();
  }

  async function apagar(id: string) {
    if (!confirm('Apagar esta anotação?')) return;
    const e = await apagarAnotacao(id);
    if (e) setErro(e); else recarregar();
  }

  return (
    <>
      <Cabecalho
        titulo="Anotações"
        descricao="O que você anotou lendo a documentação, ligado à página."
        acao={
          <button onClick={() => setFormAberto((v) => !v)}
                  className="rounded-lg bg-accent px-4 py-2 text-[14px]
                             font-semibold text-white hover:opacity-90">
            {formAberto ? 'Cancelar' : 'Nova anotação'}
          </button>
        }
      />

      {formAberto && (
        <form onSubmit={salvar} className="surface-card mb-6 space-y-3 rounded-xl p-5">
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              value={titulo} onChange={(e) => setTitulo(e.target.value)}
              placeholder="Título (opcional)" autoFocus
              className="rounded-lg border border-line bg-raised px-3 py-2.5
                         text-[14px] text-strong outline-none focus:border-accent/50"
            />
            <select
              value={rota} onChange={(e) => setRota(e.target.value)}
              className="rounded-lg border border-line bg-raised px-3 py-2.5
                         text-[14px] text-strong outline-none focus:border-accent/50"
            >
              {allRoutes.map((r) => (
                <option key={r.href} value={r.href}>{r.title}</option>
              ))}
            </select>
          </div>
          <textarea
            value={conteudo} onChange={(e) => setConteudo(e.target.value)}
            placeholder="O que você quer lembrar" rows={4} required
            className="w-full resize-y rounded-lg border border-line bg-raised
                       px-3 py-2.5 text-[14px] text-strong outline-none
                       focus:border-accent/50"
          />
          <button type="submit"
                  className="rounded-lg bg-accent px-4 py-2 text-[14px]
                             font-semibold text-white hover:opacity-90">
            Salvar
          </button>
        </form>
      )}

      {erro && (
        <p role="alert" className="mb-5 rounded-lg border border-accent/30
                                   bg-accent/10 px-3 py-2 text-[13px] text-accent">
          {erro}
        </p>
      )}

      {carregando ? (
        <p className="text-[14px] text-muted">carregando…</p>
      ) : itens.length === 0 ? (
        <Vazio titulo="Nenhuma anotação"
               texto="Anote o que custou a entender — é o que você vai querer reler." />
      ) : (
        <div className="space-y-3">
          {itens.map((a) => (
            <article key={a.id} className="surface-card rounded-xl p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  {a.titulo && (
                    <h2 className="font-semibold text-strong">{a.titulo}</h2>
                  )}
                  <Link href={a.rota}
                        className="lp-mono text-[12px] text-muted hover:text-accent">
                    {a.rota}
                  </Link>
                </div>
                <button onClick={() => apagar(a.id)}
                        className="shrink-0 text-[12.5px] text-muted hover:text-accent">
                  apagar
                </button>
              </div>
              <p className="mt-3 whitespace-pre-wrap text-[14px] leading-[23px]
                            text-body">
                {a.conteudo}
              </p>
            </article>
          ))}
        </div>
      )}
    </>
  );
}
