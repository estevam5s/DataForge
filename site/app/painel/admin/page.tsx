'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Cabecalho } from '@/components/painel/Casca';
import { Barras, Numero, SoAdmin } from '@/components/painel/Admin';
import {
  carregarResumo, listarExecucoes, listarMetricas,
  type Execucao, type MetricaDia, type Resumo,
} from '@/lib/supabase/admin';

export default function Admin() {
  return (
    <SoAdmin>
      <VisaoGeral />
    </SoAdmin>
  );
}

function VisaoGeral() {
  const [resumo, setResumo] = useState<Resumo | null>(null);
  const [metricas, setMetricas] = useState<MetricaDia[]>([]);
  const [execucoes, setExecucoes] = useState<Execucao[]>([]);

  useEffect(() => {
    carregarResumo().then((r) => setResumo(r.dados));
    listarMetricas(30).then((r) => setMetricas(r.dados));
    listarExecucoes(8).then((r) => setExecucoes(r.dados));
  }, []);

  const taxa = resumo && resumo.submissoes > 0
    ? Math.round((resumo.aceitas / resumo.submissoes) * 100)
    : 0;

  const dia = (iso: string) => iso.slice(8, 10) + '/' + iso.slice(5, 7);

  return (
    <>
      <Cabecalho
        titulo="Visão geral"
        descricao="Os números vêm da tabela de métricas, consolidada de madrugada pela tarefa agendada."
      />

      <div className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Numero rotulo="Usuários" valor={resumo?.usuarios ?? '—'} />
        <Numero rotulo="Submissões" valor={resumo?.submissoes ?? '—'}
                nota={`${resumo?.aceitas ?? 0} aceitas`} />
        <Numero rotulo="Taxa de acerto" valor={`${taxa}%`} destaque />
        <Numero rotulo="Problemas resolvidos" valor={resumo?.resolvidos ?? '—'} />
        <Numero rotulo="Problemas no catálogo" valor={resumo?.problemas ?? '—'} />
        <Numero rotulo="Tarefas agendadas" valor={resumo?.agendamentos ?? '—'} />
      </div>

      {metricas.length > 0 && (
        <div className="mb-6 grid gap-3 lg:grid-cols-2">
          <Barras
            rotulo="Submissões por dia"
            dados={metricas.map((m) => ({ chave: dia(m.dia), valor: m.submissoes }))}
          />
          <Barras
            rotulo="Usuários ativos por dia"
            dados={metricas.map((m) => ({ chave: dia(m.dia), valor: m.usuarios_ativos }))}
          />
        </div>
      )}

      {metricas.length === 0 && (
        <div className="mb-6 rounded-xl border border-dashed border-line px-6 py-10 text-center">
          <p className="font-semibold text-strong">Ainda não há métricas</p>
          <p className="mx-auto mt-1.5 max-w-[52ch] text-[14px] text-muted">
            A tarefa <code className="font-mono">metricas_diarias</code> roda às
            3h10 e consolida o dia anterior. A primeira linha aparece depois da
            primeira madrugada — ou quando você executá-la à mão em{' '}
            <Link href="/painel/admin/agendamentos" className="text-accent">
              Agendamentos
            </Link>
            .
          </p>
        </div>
      )}

      <h2 className="mb-3 text-[15px] font-bold text-strong">Últimas execuções</h2>
      {execucoes.length === 0 ? (
        <p className="text-[14px] text-muted">Nenhuma execução registrada ainda.</p>
      ) : (
        <ul className="space-y-1.5">
          {execucoes.map((e) => (
            <li
              key={e.id}
              className="flex flex-wrap items-center gap-3 rounded-lg border border-line bg-raised/25 px-4 py-2.5 text-[13px]"
            >
              <span className={e.sucesso ? 'text-emerald-400' : 'text-accent'}>
                {e.sucesso ? '✓' : '✗'}
              </span>
              <span className="font-mono text-muted">
                {new Date(e.comecou_em).toLocaleString('pt-BR')}
              </span>
              {e.linhas_afetadas !== null && (
                <span className="text-body">{e.linhas_afetadas} linha(s)</span>
              )}
              {e.detalhe && <span className="text-accent">{e.detalhe}</span>}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
