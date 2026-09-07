'use client';

import { useEffect, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import { SoAdmin, Tabela } from '@/components/painel/Admin';
import {
  alternarAgendamento, listarAgendamentos, listarExecucoes, mudarCron,
  type Agendamento, type Execucao,
} from '@/lib/supabase/admin';

/** Cadências prontas, para não obrigar ninguém a decorar cron. */
const CADENCIAS: { rotulo: string; cron: string }[] = [
  { rotulo: 'A cada 30 minutos', cron: '*/30 * * * *' },
  { rotulo: 'De hora em hora', cron: '0 * * * *' },
  { rotulo: 'A cada 6 horas', cron: '0 */6 * * *' },
  { rotulo: 'Todo dia às 3h', cron: '0 3 * * *' },
  { rotulo: 'Fim do dia (23h50)', cron: '50 23 * * *' },
  { rotulo: 'Segunda de manhã', cron: '0 12 * * 1' },
  { rotulo: 'Todo dia 1º', cron: '0 6 1 * *' },
];

export default function Agendamentos() {
  return (
    <SoAdmin>
      <Lista />
    </SoAdmin>
  );
}

function Lista() {
  const [tarefas, setTarefas] = useState<Agendamento[]>([]);
  const [execucoes, setExecucoes] = useState<Execucao[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [editando, setEditando] = useState<string | null>(null);
  const [rascunho, setRascunho] = useState('');

  const recarregar = async () => {
    const [t, e] = await Promise.all([listarAgendamentos(), listarExecucoes(30)]);
    setTarefas(t.dados);
    setExecucoes(e.dados);
    setErro(t.erro);
  };

  useEffect(() => {
    recarregar();
  }, []);

  const alternar = async (t: Agendamento) => {
    const falha = await alternarAgendamento(t.id, !t.ativo);
    if (falha) setErro(falha);
    else await recarregar();
  };

  const salvarCron = async (id: string) => {
    const falha = await mudarCron(id, rascunho);
    if (falha) {
      setErro(falha);
      return;
    }
    setEditando(null);
    setErro(null);
    await recarregar();
  };

  const ultimasDe = (id: string) =>
    execucoes.filter((e) => e.agendamento_id === id).slice(0, 5);

  return (
    <>
      <Cabecalho
        titulo="Agendamentos"
        descricao="O que roda sozinho. Mudar a expressão aqui reagenda o pg_cron na hora — um gatilho no banco cuida disso."
      />

      {erro && (
        <p className="mb-4 rounded-lg border border-accent/40 bg-accent/8 px-4 py-2.5 text-[13.5px] text-body">
          {erro}
        </p>
      )}

      <div className="space-y-3">
        {tarefas.map((t) => {
          const historico = ultimasDe(t.id);
          return (
            <div
              key={t.id}
              className={`rounded-xl border p-4 transition-colors ${
                t.ativo ? 'border-line bg-raised/25' : 'border-line/50 bg-raised/10'
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-[14px] font-semibold text-strong">
                      {t.nome}
                    </span>
                    <span
                      className={`rounded px-1.5 py-px text-[10px] font-bold uppercase ${
                        t.ativo
                          ? 'bg-emerald-400/12 text-emerald-400'
                          : 'bg-muted/12 text-muted'
                      }`}
                    >
                      {t.ativo ? 'ativa' : 'parada'}
                    </span>
                    {t.ultimo_estado && t.ultimo_estado !== 'ok' && (
                      <span className="rounded bg-accent/12 px-1.5 py-px text-[10px] font-bold uppercase text-accent">
                        erro
                      </span>
                    )}
                  </div>
                  {t.descricao && (
                    <p className="mt-1 text-[13.5px] text-muted">{t.descricao}</p>
                  )}
                </div>

                <button
                  onClick={() => alternar(t)}
                  className={`shrink-0 rounded-lg px-3 py-1.5 text-[12.5px] font-semibold transition-colors ${
                    t.ativo
                      ? 'border border-line text-muted hover:text-strong'
                      : 'bg-accent text-white hover:bg-accent-soft'
                  }`}
                >
                  {t.ativo ? 'Parar' : 'Ativar'}
                </button>
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-2">
                {editando === t.id ? (
                  <>
                    <input
                      value={rascunho}
                      onChange={(e) => setRascunho(e.target.value)}
                      className="rounded-lg border border-accent/50 bg-black/30 px-2.5 py-1 font-mono text-[12.5px] outline-none"
                      autoFocus
                    />
                    <select
                      onChange={(e) => setRascunho(e.target.value)}
                      value=""
                      className="rounded-lg border border-line bg-raised/50 px-2 py-1 text-[12px] outline-none"
                    >
                      <option value="">usar uma pronta…</option>
                      {CADENCIAS.map((c) => (
                        <option key={c.cron} value={c.cron}>
                          {c.rotulo}
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={() => salvarCron(t.id)}
                      className="rounded-lg bg-accent px-3 py-1 text-[12.5px] font-semibold text-white"
                    >
                      Salvar
                    </button>
                    <button
                      onClick={() => setEditando(null)}
                      className="text-[12.5px] text-muted hover:text-strong"
                    >
                      cancelar
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => {
                      setEditando(t.id);
                      setRascunho(t.expressao_cron);
                    }}
                    className="rounded-lg border border-line bg-black/25 px-2.5 py-1 font-mono text-[12.5px] text-body transition-colors hover:border-accent/40"
                    title="clique para editar"
                  >
                    {t.expressao_cron}
                  </button>
                )}

                <span className="font-mono text-[11.5px] text-muted">{t.funcao}()</span>

                {t.ultima_execucao && (
                  <span className="ml-auto text-[12px] text-muted">
                    última: {new Date(t.ultima_execucao).toLocaleString('pt-BR')}
                  </span>
                )}
              </div>

              {historico.length > 0 && (
                <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                  {historico.map((e) => (
                    <span
                      key={e.id}
                      title={`${new Date(e.comecou_em).toLocaleString('pt-BR')}${
                        e.detalhe ? ' — ' + e.detalhe : ''
                      }`}
                      className={`h-1.5 w-8 rounded-full ${
                        e.sucesso ? 'bg-emerald-400/60' : 'bg-accent/70'
                      }`}
                    />
                  ))}
                  <span className="ml-1 text-[11.5px] text-muted">
                    últimas {historico.length} execuções
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 rounded-xl border border-line bg-raised/20 p-4">
        <p className="mb-2 text-[13px] font-semibold text-strong">
          Como ler a expressão
        </p>
        <p className="font-mono text-[12.5px] text-muted">
          minuto hora dia-do-mês mês dia-da-semana
        </p>
        <p className="mt-2 text-[13px] leading-[21px] text-muted">
          Os horários são <strong className="text-body">UTC</strong>, que é como o
          Supabase roda. Converter para o fuso de quem lê só criaria confusão no
          horário de verão — <code className="font-mono">0 3 * * *</code> é meia-noite
          em Brasília.
        </p>
      </div>
    </>
  );
}
