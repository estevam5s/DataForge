'use client';

import { ProvedorAuth, useAuth } from '@/lib/supabase/auth';
import { Casca } from '@/components/painel/Casca';
import { Entrar } from '@/components/painel/Entrar';

function Portao({ children }: { children: React.ReactNode }) {
  const { usuario, carregando } = useAuth();

  if (carregando) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-[14px] text-muted">carregando…</p>
      </div>
    );
  }
  if (!usuario) return <Entrar />;
  return <Casca>{children}</Casca>;
}

export default function LayoutPainel({ children }: { children: React.ReactNode }) {
  return (
    <ProvedorAuth>
      <Portao>{children}</Portao>
    </ProvedorAuth>
  );
}
