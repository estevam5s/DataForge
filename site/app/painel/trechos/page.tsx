'use client';

import { useEffect, useState } from 'react';
import { Cabecalho, Vazio } from '@/components/painel/Casca';
import { CodeBlock } from '@/components/CodeBlock';
import {
  apagarTrecho, listarProjetos, listarTrechos, salvarTrecho,
  type Projeto, type Trecho,
} from '@/lib/supabase/dados';

export default function Trechos() {
  const [itens, setItens] = useState<Trecho[]>([]);
  const [projetos, setProjetos] = useState<Projeto[]>([]);
  const [filtro, setFiltro] = useState('');
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [formAberto, setFormAberto] = useState(false);
  const [titulo, setTitulo] = useState('');
  const [codigo, setCodigo] = useState('');
  const [projetoId, setProjetoId] = useState('');

  const recarregar = () =>
    Promise.all([listarTrechos(), listarProjetos()]).then(([t, p]) => {
      setItens(t.dados);
      setProjetos(p.dados);
      setErro(t.erro ?? p.erro);
      if (!projetoId && p.dados[0]) setProjetoId(p.dados[0].id);
      setCarregando(false);
    });

  useEffect(() => { recarregar(); }, []);

  async function salvar(e: React.FormEvent) {
    e.preventDefault();
    if (!titulo.trim() || !projetoId) return;
    const r = await salvarTrecho(projetoId, titulo.trim(), codigo);
    if (r.erro) { setErro(r.erro); return; }
    setTitulo(''); setCodigo(''); setFormAberto(false);
    recarregar();
  }

  async function apagar(id: string) {
    if (!confirm('Apagar este trecho?')) return;
    const e = await apagarTrecho(id);
    if (e) setErro(e); else recarregar();
  }

  const visiveis = filtro
    ? itens.filter((t) =>
        (t.titulo + t.codigo).toLowerCase().includes(filtro.toLowerCase()))
    : itens;

  const nomeDoProjeto = (id: string) =>
    projetos.find((p) => p.id === id)?.nome ?? 'sem projeto';

  return (
    <>
      <Cabecalho
        titulo="Trechos"
        descricao="Código que você quer ter à mão."
        acao={
          <button
            onClick={() => setFormAberto((v) => !v)}
            disabled={projetos.length === 0}
            className="rounded-lg bg-accent px-4 py-2 text-[14px] font-semibold
                       text-white hover:opacity-90 disabled:opacity-40"
          >
            {formAberto ? 'Cancelar' : 'Novo trecho'}
          </button>
        }
      />

      {projetos.length === 0 && !carregando && (
        <p className="mb-5 rounded-lg border border-line bg-raised px-3 py-2
                      text-[13px] text-muted">
          Crie um projeto antes — todo trecho pertence a um.
        </p>
      )}

      {formAberto && (
        <form onSubmit={salvar} className="surface-card mb-6 space-y-3 rounded-xl p-5">
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              value={titulo} onChange={(e) => setTitulo(e.target.value)}
              placeholder="Título do trecho" required autoFocus
              className="rounded-lg border border-line bg-raised px-3 py-2.5
                         text-[14px] text-strong outline-none focus:border-accent/50"
            />
            <select
              value={projetoId} onChange={(e) => setProjetoId(e.target.value)}
              className="rounded-lg border border-line bg-raised px-3 py-2.5
                         text-[14px] text-strong outline-none focus:border-accent/50"
            >
              {projetos.map((p) => (
                <option key={p.id} value={p.id}>{p.nome}</option>
              ))}
            </select>
          </div>
          <textarea
            value={codigo} onChange={(e) => setCodigo(e.target.value)}
            placeholder={'action somar(a, b):\n    yield a + b'}
            rows={8} spellCheck={false}
            className="w-full resize-y rounded-lg border border-line bg-raised
                       px-3 py-2.5 font-mono text-[13px] text-strong outline-none
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

      {itens.length > 0 && (
        <input
          value={filtro} onChange={(e) => setFiltro(e.target.value)}
          placeholder="filtrar por título ou conteúdo"
          className="mb-5 w-full rounded-lg border border-line bg-raised px-3
                     py-2 text-[14px] text-strong outline-none
                     placeholder:text-muted/60 focus:border-accent/50"
        />
      )}

      {carregando ? (
        <p className="text-[14px] text-muted">carregando…</p>
      ) : visiveis.length === 0 ? (
        <Vazio
          titulo={filtro ? 'Nada encontrado' : 'Nenhum trecho ainda'}
          texto={filtro
            ? 'Nenhum trecho casa com esse filtro.'
            : 'Guarde aqui o código que você reescreve toda hora.'}
        />
      ) : (
        <div className="space-y-4">
          {visiveis.map((t) => (
            <article key={t.id} className="surface-card overflow-hidden rounded-xl">
              <div className="flex items-center justify-between gap-3 border-b
                              border-line px-4 py-3">
                <div className="min-w-0">
                  <h2 className="truncate font-semibold text-strong">{t.titulo}</h2>
                  <p className="text-[12px] text-muted">
                    {nomeDoProjeto(t.projeto_id)}
                  </p>
                </div>
                <button onClick={() => apagar(t.id)}
                        className="shrink-0 text-[12.5px] text-muted hover:text-accent">
                  apagar
                </button>
              </div>
              <CodeBlock code={t.codigo} lang="df" />
            </article>
          ))}
        </div>
      )}
    </>
  );
}
