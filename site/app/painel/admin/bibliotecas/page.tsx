'use client';

import { useEffect, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import { SoAdmin } from '@/components/painel/Admin';
import { CodeBlock } from '@/components/CodeBlock';
import {
  listarBibliotecasAdmin, revisarBiblioteca, type Biblioteca,
} from '@/lib/supabase/comunidade';

const ESTADOS: Biblioteca['estado'][] = ['pendente', 'aprovada', 'recusada'];
const ROTULO: Record<Biblioteca['estado'], string> = {
  pendente: 'Em revisão', aprovada: 'No registro', recusada: 'Recusada',
};

export default function AdminBibliotecas() {
  return (
    <SoAdmin>
      <Fila />
    </SoAdmin>
  );
}

function Fila() {
  const [lista, setLista] = useState<Biblioteca[]>([]);
  const [filtro, setFiltro] = useState<Biblioteca['estado'] | 'todos'>('pendente');
  const [erro, setErro] = useState<string | null>(null);
  const [recusando, setRecusando] = useState<number | null>(null);
  const [motivo, setMotivo] = useState('');

  const recarregar = () =>
    listarBibliotecasAdmin().then((r) => {
      setLista(r.dados);
      setErro(r.erro);
    });

  useEffect(() => { recarregar(); }, []);

  const visiveis = filtro === 'todos'
    ? lista
    : lista.filter((b) => b.estado === filtro);
  const contar = (e: Biblioteca['estado']) =>
    lista.filter((b) => b.estado === e).length;

  async function revisar(b: Biblioteca, estado: Biblioteca['estado'], porque?: string) {
    const falha = await revisarBiblioteca(b.id, estado, porque);
    if (falha) { setErro(falha); return; }
    setRecusando(null);
    setMotivo('');
    recarregar();
  }

  return (
    <>
      <Cabecalho
        titulo="Bibliotecas da comunidade"
        descricao={`${contar('pendente')} esperando revisão. Aprovar põe o pacote no registro, e o dataforge add passa a baixá-lo e executá-lo.`}
      />

      {erro && (
        <p className="mb-4 rounded-lg border border-accent/40 bg-accent/8 px-4 py-2.5
                      text-[13.5px] text-body">
          {erro}
        </p>
      )}

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
            {e === 'todos' ? 'Todas' : ROTULO[e]}
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
          {visiveis.map((b) => (
            <li key={b.id} className="rounded-xl border border-line px-5 py-4">
              <div className="flex flex-wrap items-baseline justify-between gap-3">
                <div>
                  <code className="text-[15px] font-semibold text-strong">{b.nome}</code>
                  <span className="ml-2 text-[13px] text-muted">{b.versao}</span>
                  <span className="ml-2.5 rounded border border-line px-1.5 py-0.5
                                   text-[11px] text-muted">
                    {ROTULO[b.estado]}
                  </span>
                </div>
                <time className="text-[12px] tabular-nums text-muted">
                  {new Date(b.criado_em).toLocaleDateString('pt-BR')}
                </time>
              </div>

              <p className="mt-1.5 text-[13.5px] text-body">{b.descricao}</p>

              <dl className="mt-3 grid gap-x-6 gap-y-1 text-[12.5px] sm:grid-cols-2">
                <Linha rotulo="Licença" valor={b.licenca} />
                <Linha rotulo="Downloads" valor={String(b.downloads)} />
                <Linha rotulo="Tarball" valor={b.tarball} link />
                {b.repositorio && <Linha rotulo="Repositório" valor={b.repositorio} link />}
                {b.documentacao && <Linha rotulo="Documentação" valor={b.documentacao} link />}
                {b.palavras.length > 0 && (
                  <Linha rotulo="Palavras" valor={b.palavras.join(', ')} />
                )}
              </dl>

              {/* O que conferir antes de aprovar. Um checklist escrito é o
                  que separa uma revisão de um clique. */}
              {b.estado === 'pendente' && (
                <div className="mt-3.5 rounded-lg border border-line bg-raised/25 px-4 py-3">
                  <p className="text-[12.5px] font-semibold text-strong">
                    Antes de aprovar, confira o tarball:
                  </p>
                  <div className="mt-2">
                    <CodeBlock
                      lang="bash"
                      code={`curl -fsSLO ${b.tarball}
shasum -a 256 ${b.tarball.split('/').pop()}
#  esperado: ${b.sha256}
tar -tzf ${b.tarball.split('/').pop()} | head -20`}
                    />
                  </div>
                  <p className="mt-2 text-[12px] text-muted">
                    O hash tem de bater, e o conteúdo tem de ser <code>.df</code> e{' '}
                    <code>forge.toml</code> — nada fora da pasta do pacote.
                  </p>
                </div>
              )}

              {b.motivo && (
                <p className="mt-3 border-l-2 border-line pl-3 text-[13px] text-body">
                  {b.motivo}
                </p>
              )}

              <div className="mt-3.5 flex flex-wrap items-center gap-2">
                {b.estado !== 'aprovada' && (
                  <button
                    onClick={() => revisar(b, 'aprovada')}
                    className="rounded-lg bg-accent px-4 py-1.5 text-[13px]
                               font-semibold text-white"
                  >
                    Aprovar
                  </button>
                )}
                {b.estado !== 'recusada' && (
                  <button
                    onClick={() => {
                      setRecusando(recusando === b.id ? null : b.id);
                      setMotivo(b.motivo ?? '');
                    }}
                    className="rounded-lg border border-line px-3 py-1.5 text-[13px]
                               text-body hover:border-accent/50 hover:text-strong"
                  >
                    Recusar
                  </button>
                )}
                {b.estado === 'aprovada' && (
                  <button
                    onClick={() => revisar(b, 'pendente')}
                    className="rounded-lg border border-line px-3 py-1.5 text-[13px]
                               text-body hover:border-accent/50 hover:text-strong"
                  >
                    Tirar do registro
                  </button>
                )}
              </div>

              {recusando === b.id && (
                <div className="mt-3">
                  <label htmlFor={`m-${b.id}`} className="mb-1.5 block text-[13px] text-body">
                    Por quê? Sem motivo, a pessoa reenvia a mesma coisa.
                  </label>
                  <textarea
                    id={`m-${b.id}`}
                    value={motivo}
                    onChange={(e) => setMotivo(e.target.value)}
                    rows={3}
                    className="w-full resize-y rounded-lg border border-line bg-transparent
                               px-3 py-2.5 text-[13.5px] text-strong outline-none
                               focus:border-accent/60"
                  />
                  <button
                    onClick={() => revisar(b, 'recusada', motivo)}
                    disabled={!motivo.trim()}
                    className="mt-2 rounded-lg border border-line px-4 py-2 text-[13.5px]
                               text-body disabled:opacity-40"
                  >
                    Confirmar recusa
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

function Linha({ rotulo, valor, link }: {
  rotulo: string; valor: string; link?: boolean;
}) {
  return (
    <div className="flex gap-2">
      <dt className="shrink-0 text-muted">{rotulo}</dt>
      <dd className="min-w-0 truncate text-body">
        {link ? (
          <a href={valor} target="_blank" rel="noopener noreferrer"
             className="text-accent hover:underline">
            {valor}
          </a>
        ) : valor}
      </dd>
    </div>
  );
}
