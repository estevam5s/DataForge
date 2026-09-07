'use client';

import { useEffect, useMemo, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import { SoAdmin } from '@/components/painel/Admin';
import { listarEventos, type Evento } from '@/lib/supabase/admin';

export default function Eventos() {
  return (
    <SoAdmin>
      <Trilha />
    </SoAdmin>
  );
}

function Trilha() {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [tipo, setTipo] = useState('todos');

  useEffect(() => {
    listarEventos(150).then((r) => setEventos(r.dados));
  }, []);

  const tipos = useMemo(
    () => ['todos', ...Array.from(new Set(eventos.map((e) => e.tipo)))],
    [eventos]
  );

  const visiveis = eventos.filter((e) => tipo === 'todos' || e.tipo === tipo);

  return (
    <>
      <Cabecalho
        titulo="Auditoria"
        descricao="Trilha de eventos. A rotina de limpeza apaga o que tem mais de 90 dias."
      />

      <div className="mb-4 flex flex-wrap gap-1.5">
        {tipos.map((t) => (
          <button
            key={t}
            onClick={() => setTipo(t)}
            className={`rounded-lg px-3 py-1.5 text-[12.5px] font-semibold transition-colors ${
              tipo === t ? 'bg-accent text-white' : 'bg-raised/40 text-muted hover:text-strong'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {visiveis.length === 0 ? (
        <div className="rounded-xl border border-dashed border-line px-6 py-12 text-center">
          <p className="font-semibold text-strong">Nenhum evento ainda</p>
          <p className="mx-auto mt-1.5 max-w-[48ch] text-[14px] text-muted">
            A tarefa <code className="font-mono">pulso_horario</code> grava um a cada
            hora. Os primeiros aparecem depois da primeira hora no ar.
          </p>
        </div>
      ) : (
        <ul className="space-y-1.5">
          {visiveis.map((e) => (
            <li
              key={e.id}
              className="rounded-lg border border-line bg-raised/25 px-4 py-2.5"
            >
              <div className="flex flex-wrap items-baseline gap-3">
                <span className="rounded bg-accent/12 px-1.5 py-px font-mono text-[11.5px] font-semibold text-accent">
                  {e.tipo}
                </span>
                <span className="font-mono text-[12px] text-muted">
                  {new Date(e.criado_em).toLocaleString('pt-BR')}
                </span>
              </div>
              {Object.keys(e.dados).length > 0 && (
                <pre className="mt-1.5 overflow-x-auto font-mono text-[12px] text-body">
                  {JSON.stringify(e.dados, null, 0)}
                </pre>
              )}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
