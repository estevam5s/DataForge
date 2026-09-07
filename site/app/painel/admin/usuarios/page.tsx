'use client';

import { useEffect, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import { SoAdmin, Tabela } from '@/components/painel/Admin';
import { listarUsuarios, mudarPapel, type UsuarioAdmin } from '@/lib/supabase/admin';
import { useAuth } from '@/lib/supabase/auth';

export default function Usuarios() {
  return (
    <SoAdmin>
      <ListaUsuarios />
    </SoAdmin>
  );
}

function ListaUsuarios() {
  const { usuario } = useAuth();
  const [lista, setLista] = useState<UsuarioAdmin[]>([]);
  const [busca, setBusca] = useState('');
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState<string | null>(null);

  const recarregar = () =>
    listarUsuarios().then((r) => {
      setLista(r.dados);
      setErro(r.erro);
    });

  useEffect(() => {
    recarregar();
  }, []);

  const trocar = async (id: string, papel: UsuarioAdmin['papel']) => {
    setSalvando(id);
    const falha = await mudarPapel(id, papel);
    if (falha) setErro(falha);
    else await recarregar();
    setSalvando(null);
  };

  const visiveis = lista.filter(
    (u) => busca === '' || (u.nome ?? '').toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <>
      <Cabecalho
        titulo="Usuários"
        descricao={`${lista.length} conta(s). O papel decide o acesso ao painel administrativo.`}
      />

      <input
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        placeholder="Buscar por nome…"
        className="mb-4 w-full max-w-[280px] rounded-xl border border-line bg-raised/40 px-3 py-2 text-[13.5px] outline-none placeholder:text-muted focus:border-accent/50"
      />

      {erro && (
        <p className="mb-4 rounded-lg border border-accent/40 bg-accent/8 px-4 py-2.5 text-[13.5px] text-body">
          {erro}
        </p>
      )}

      <Tabela cabecalho={['Nome', 'Papel', 'XP', 'Ofensiva', 'Última prática', 'Desde']}>
        {visiveis.map((u) => (
          <tr key={u.id} className="hover:bg-raised/30">
            <td className="px-4 py-2.5">
              <span className="font-medium text-strong">{u.nome ?? '—'}</span>
              {u.id === usuario?.id && (
                <span className="ml-2 text-[11.5px] text-muted">(você)</span>
              )}
            </td>
            <td className="px-4 py-2.5">
              <select
                value={u.papel}
                disabled={salvando === u.id || u.id === usuario?.id}
                onChange={(e) => trocar(u.id, e.target.value as UsuarioAdmin['papel'])}
                className="rounded-lg border border-line bg-raised/50 px-2 py-1 text-[12.5px] outline-none disabled:opacity-50"
                title={u.id === usuario?.id
                  ? 'Você não pode mudar o próprio papel — a política do banco também recusa'
                  : undefined}
              >
                <option value="usuario">usuário</option>
                <option value="moderador">moderador</option>
                <option value="admin">admin</option>
              </select>
            </td>
            <td className="px-4 py-2.5 tabular-nums text-body">{u.xp}</td>
            <td className="px-4 py-2.5 tabular-nums text-body">{u.ofensiva}</td>
            <td className="px-4 py-2.5 text-muted">{u.ultima_pratica ?? '—'}</td>
            <td className="px-4 py-2.5 text-muted">
              {new Date(u.criado_em).toLocaleDateString('pt-BR')}
            </td>
          </tr>
        ))}
      </Tabela>

      <p className="mt-3 text-[12.5px] text-muted">
        Você não pode mudar o próprio papel. A política do banco recusa isso mesmo
        que a interface deixasse — senão bastaria um UPDATE para qualquer um virar
        admin.
      </p>
    </>
  );
}
