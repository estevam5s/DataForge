'use client';

import { useEffect, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import { SoAdmin } from '@/components/painel/Admin';
import {
  listarFeedbackAdmin, responderFeedback, TIPOS, type Feedback,
} from '@/lib/supabase/comunidade';

const ESTADOS: Feedback['estado'][] = ['novo', 'lido', 'respondido', 'arquivado'];

const ROTULO: Record<Feedback['estado'], string> = {
  novo: 'Novo', lido: 'Lido', respondido: 'Respondido', arquivado: 'Arquivado',
};

export default function AdminFeedback() {
  return (
    <SoAdmin>
      <Caixa />
    </SoAdmin>
  );
}

function Caixa() {
  const [lista, setLista] = useState<Feedback[]>([]);
  const [filtro, setFiltro] = useState<Feedback['estado'] | 'todos'>('novo');
  const [erro, setErro] = useState<string | null>(null);
  const [aberto, setAberto] = useState<number | null>(null);
  const [rascunho, setRascunho] = useState('');

  const recarregar = () =>
    listarFeedbackAdmin().then((r) => {
      setLista(r.dados);
      setErro(r.erro);
    });

  useEffect(() => { recarregar(); }, []);

  const visiveis = filtro === 'todos'
    ? lista
    : lista.filter((f) => f.estado === filtro);

  const contar = (e: Feedback['estado']) =>
    lista.filter((f) => f.estado === e).length;

  async function mudar(f: Feedback, estado: Feedback['estado'], resposta?: string) {
    const falha = await responderFeedback(f.id, estado, resposta);
    if (falha) { setErro(falha); return; }
    setAberto(null);
    setRascunho('');
    recarregar();
  }

  return (
    <>
      <Cabecalho
        titulo="Feedback"
        descricao={`${contar('novo')} sem ler, ${lista.length} no total. Responder marca como respondido e a pessoa vê a resposta no painel dela.`}
      />

      {erro && (
        <p className="mb-4 rounded-lg border border-accent/40 bg-accent/8 px-4 py-2.5
                      text-[13.5px] text-body">
          {erro}
        </p>
      )}

      {/* ── filtro ── */}
      <div className="mb-6 flex flex-wrap gap-2">
        {(['todos', ...ESTADOS] as const).map((e) => (
          <button
            key={e}
            onClick={() => setFiltro(e)}
            aria-pressed={filtro === e}
            className={`rounded-lg border px-3 py-1.5 text-[13px] transition-colors ${
              filtro === e
                ? 'border-accent/60 bg-accent/10 font-medium text-accent'
                : 'border-line text-body hover:text-strong'
            }`}
          >
            {e === 'todos' ? 'Todos' : ROTULO[e]}
            <span className="ml-1.5 text-[11.5px] tabular-nums opacity-60">
              {e === 'todos' ? lista.length : contar(e)}
            </span>
          </button>
        ))}
      </div>

      {visiveis.length === 0 ? (
        <p className="rounded-xl border border-dashed border-line px-6 py-14
                      text-center text-[14px] text-muted">
          Nada aqui.
        </p>
      ) : (
        <ul className="space-y-3">
          {visiveis.map((f) => {
            const tipo = TIPOS.find((t) => t.valor === f.tipo);
            const expandido = aberto === f.id;
            return (
              <li key={f.id} className="rounded-xl border border-line px-5 py-4">
                <div className="flex flex-wrap items-baseline justify-between gap-3">
                  <div className="min-w-0">
                    <span className="text-[15px] font-semibold text-strong">
                      {f.assunto}
                    </span>
                    <span className="ml-2.5 rounded border border-line px-1.5 py-0.5
                                     text-[11px] text-muted">
                      {tipo?.rotulo ?? f.tipo}
                    </span>
                    {f.estado !== 'novo' && (
                      <span className="ml-1.5 text-[11.5px] text-muted">
                        {ROTULO[f.estado]}
                      </span>
                    )}
                  </div>
                  <time className="shrink-0 text-[12px] tabular-nums text-muted">
                    {new Date(f.criado_em).toLocaleDateString('pt-BR')}
                  </time>
                </div>

                <p className="mt-2 whitespace-pre-wrap text-[13.5px] leading-[1.65] text-body">
                  {f.mensagem}
                </p>

                {f.pagina && (
                  <p className="mt-2 text-[12.5px] text-muted">
                    sobre <code className="text-body">{f.pagina}</code>
                  </p>
                )}

                {f.resposta && (
                  <p className="mt-3 border-l-2 border-accent/50 pl-3 text-[13px] text-body">
                    {f.resposta}
                  </p>
                )}

                <div className="mt-3.5 flex flex-wrap items-center gap-2">
                  {f.estado === 'novo' && (
                    <Acao onClick={() => mudar(f, 'lido')}>Marcar como lido</Acao>
                  )}
                  <Acao onClick={() => {
                    setAberto(expandido ? null : f.id);
                    setRascunho(f.resposta ?? '');
                  }}>
                    {expandido ? 'Fechar' : f.resposta ? 'Editar resposta' : 'Responder'}
                  </Acao>
                  {f.estado !== 'arquivado' && (
                    <Acao onClick={() => mudar(f, 'arquivado')}>Arquivar</Acao>
                  )}
                </div>

                {expandido && (
                  <div className="mt-3">
                    <label htmlFor={`r-${f.id}`} className="sr-only">Resposta</label>
                    <textarea
                      id={`r-${f.id}`}
                      value={rascunho}
                      onChange={(e) => setRascunho(e.target.value)}
                      rows={4}
                      placeholder="O que foi feito, ou por que não será."
                      className="w-full resize-y rounded-lg border border-line bg-transparent
                                 px-3 py-2.5 text-[13.5px] text-strong outline-none
                                 placeholder:text-muted focus:border-accent/60"
                    />
                    <button
                      onClick={() => mudar(f, 'respondido', rascunho)}
                      disabled={!rascunho.trim()}
                      className="mt-2 rounded-lg bg-accent px-4 py-2 text-[13.5px]
                                 font-semibold text-white disabled:opacity-40"
                    >
                      Enviar resposta
                    </button>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}

function Acao({ onClick, children }: {
  onClick: () => void; children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className="rounded-lg border border-line px-3 py-1.5 text-[13px]
                 text-body transition-colors hover:border-accent/50 hover:text-strong"
    >
      {children}
    </button>
  );
}
