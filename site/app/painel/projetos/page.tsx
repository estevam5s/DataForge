'use client';

import { useEffect, useState } from 'react';
import { Cabecalho, Vazio } from '@/components/painel/Casca';
import {
  apagarProjeto, criarProjeto, listarProjetos, type Projeto,
} from '@/lib/supabase/dados';

export default function Projetos() {
  const [itens, setItens] = useState<Projeto[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [formAberto, setFormAberto] = useState(false);
  const [nome, setNome] = useState('');
  const [descricao, setDescricao] = useState('');
  const [publico, setPublico] = useState(false);

  const recarregar = () =>
    listarProjetos().then((r) => {
      setItens(r.dados);
      setErro(r.erro);
      setCarregando(false);
    });

  useEffect(() => { recarregar(); }, []);

  async function criar(e: React.FormEvent) {
    e.preventDefault();
    if (!nome.trim()) return;
    const r = await criarProjeto(nome.trim(), descricao.trim(), publico);
    if (r.erro) { setErro(r.erro); return; }
    setNome(''); setDescricao(''); setPublico(false); setFormAberto(false);
    recarregar();
  }

  async function apagar(id: string, nomeProjeto: string) {
    if (!confirm(`Apagar "${nomeProjeto}"? Os trechos dele vão junto.`)) return;
    const e = await apagarProjeto(id);
    if (e) setErro(e); else recarregar();
  }

  return (
    <>
      <Cabecalho
        titulo="Projetos"
        descricao="Cada projeto agrupa trechos de código que andam juntos."
        acao={
          <button onClick={() => setFormAberto((v) => !v)}
                  className="rounded-lg bg-accent px-4 py-2 text-[14px]
                             font-semibold text-white hover:opacity-90">
            {formAberto ? 'Cancelar' : 'Novo projeto'}
          </button>
        }
      />

      {formAberto && (
        <form onSubmit={criar} className="surface-card mb-6 space-y-3 rounded-xl p-5">
          <input
            value={nome} onChange={(e) => setNome(e.target.value)}
            placeholder="Nome do projeto" required autoFocus
            className="w-full rounded-lg border border-line bg-raised px-3 py-2.5
                       text-[14px] text-strong outline-none focus:border-accent/50"
          />
          <textarea
            value={descricao} onChange={(e) => setDescricao(e.target.value)}
            placeholder="O que ele faz (opcional)" rows={2}
            className="w-full resize-y rounded-lg border border-line bg-raised
                       px-3 py-2.5 text-[14px] text-strong outline-none
                       focus:border-accent/50"
          />
          <label className="flex items-center gap-2 text-[13.5px] text-body">
            <input type="checkbox" checked={publico}
                   onChange={(e) => setPublico(e.target.checked)}
                   className="accent-[rgb(var(--accent))]" />
            Público — qualquer pessoa com o link pode ver
          </label>
          <button type="submit"
                  className="rounded-lg bg-accent px-4 py-2 text-[14px]
                             font-semibold text-white hover:opacity-90">
            Criar
          </button>
        </form>
      )}

      {erro && <Erro texto={erro} />}

      {carregando ? (
        <p className="text-[14px] text-muted">carregando…</p>
      ) : itens.length === 0 ? (
        <Vazio titulo="Nenhum projeto ainda"
               texto="Crie um para começar a guardar trechos de código." />
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {itens.map((p) => (
            <article key={p.id} className="surface-card rounded-xl p-5">
              <div className="flex items-start justify-between gap-3">
                <h2 className="font-semibold text-strong">{p.nome}</h2>
                {p.publico && (
                  <span className="shrink-0 rounded-full bg-accent/12 px-2 py-0.5
                                   text-[11px] font-medium text-accent">
                    público
                  </span>
                )}
              </div>
              {p.descricao && (
                <p className="mt-1.5 text-[13.5px] leading-[21px] text-muted">
                  {p.descricao}
                </p>
              )}
              <div className="mt-4 flex items-center gap-3 text-[12.5px]">
                <span className="text-muted">
                  {new Date(p.criado_em).toLocaleDateString('pt-BR')}
                </span>
                <button onClick={() => apagar(p.id, p.nome)}
                        className="ml-auto text-muted hover:text-accent">
                  apagar
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </>
  );
}

function Erro({ texto }: { texto: string }) {
  return (
    <p role="alert" className="mb-5 rounded-lg border border-accent/30
                               bg-accent/10 px-3 py-2 text-[13px] text-accent">
      {texto}
    </p>
  );
}
