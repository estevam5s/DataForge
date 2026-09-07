'use client';

import { useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import { useAuth } from '@/lib/supabase/auth';
import { configurado, obterCliente } from '@/lib/supabase/cliente';

export default function Conta() {
  const { usuario, sair, demonstracao } = useAuth();
  const [nome, setNome] = useState(
    (usuario?.user_metadata?.nome as string) ?? '');
  const [aviso, setAviso] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  async function salvarPerfil(e: React.FormEvent) {
    e.preventDefault();
    setErro(null); setAviso(null); setSalvando(true);

    const cliente = obterCliente();
    if (!cliente) {
      setAviso('Em demonstração — a mudança não é gravada.');
      setSalvando(false);
      return;
    }

    const { error } = await cliente.auth.updateUser({ data: { nome } });
    if (!error && usuario) {
      await cliente.from('perfis').update({ nome }).eq('id', usuario.id);
    }
    setSalvando(false);
    if (error) setErro(error.message);
    else setAviso('Perfil salvo.');
  }

  return (
    <>
      <Cabecalho titulo="Conta" descricao="Seu perfil e a sessão atual." />

      <section className="surface-card rounded-xl p-6">
        <h2 className="font-semibold text-strong">Perfil</h2>
        <form onSubmit={salvarPerfil} className="mt-4 max-w-[380px] space-y-3.5">
          <div>
            <label htmlFor="nome"
                   className="mb-1.5 block text-[13px] font-medium text-body">
              Nome
            </label>
            <input
              id="nome" value={nome} onChange={(e) => setNome(e.target.value)}
              className="w-full rounded-lg border border-line bg-raised px-3
                         py-2.5 text-[14px] text-strong outline-none
                         focus:border-accent/50"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-[13px] font-medium text-body">
              E-mail
            </label>
            <p className="rounded-lg border border-line bg-raised px-3 py-2.5
                          text-[14px] text-muted">
              {usuario?.email}
            </p>
          </div>

          {erro && <p role="alert" className="text-[13px] text-accent">{erro}</p>}
          {aviso && <p role="status" className="text-[13px] text-muted">{aviso}</p>}

          <button type="submit" disabled={salvando}
                  className="rounded-lg bg-accent px-4 py-2 text-[14px]
                             font-semibold text-white hover:opacity-90
                             disabled:opacity-50">
            {salvando ? 'Salvando…' : 'Salvar'}
          </button>
        </form>
      </section>

      <section className="surface-card mt-5 rounded-xl p-6">
        <h2 className="font-semibold text-strong">Conexão</h2>
        <dl className="mt-4 space-y-2.5 text-[13.5px]">
          <div className="flex justify-between gap-4">
            <dt className="text-muted">Supabase</dt>
            <dd className={configurado ? 'text-strong' : 'text-accent'}>
              {configurado ? 'configurado' : 'não configurado'}
            </dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-muted">Modo</dt>
            <dd className="text-strong">
              {demonstracao ? 'demonstração' : 'produção'}
            </dd>
          </div>
          {usuario?.id && !demonstracao && (
            <div className="flex justify-between gap-4">
              <dt className="text-muted">Seu id</dt>
              <dd className="lp-mono truncate text-[12px] text-muted">
                {usuario.id}
              </dd>
            </div>
          )}
        </dl>
      </section>

      <section className="mt-5 rounded-xl border border-accent/25 p-6">
        <h2 className="font-semibold text-strong">Sair</h2>
        <p className="mt-1.5 text-[13.5px] text-muted">
          Encerra a sessão neste navegador.
        </p>
        <button onClick={() => sair()}
                className="mt-4 rounded-lg border border-accent/40 px-4 py-2
                           text-[14px] font-semibold text-accent
                           hover:bg-accent/10">
          Sair da conta
        </button>
      </section>
    </>
  );
}
