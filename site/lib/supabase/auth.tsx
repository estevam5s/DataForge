'use client';

import {
  createContext, useCallback, useContext, useEffect, useMemo, useState,
} from 'react';
import type { Session, User } from '@supabase/supabase-js';
import { configurado, obterCliente, traduzirErro } from './cliente';

/** O perfil de quem está logado — papel, pontos e ofensiva. */
export type Perfil = {
  id: string;
  nome: string | null;
  avatar_url: string | null;
  bio: string | null;
  papel: 'usuario' | 'moderador' | 'admin';
  xp: number;
  ofensiva: number;
  ultima_pratica: string | null;
};

type Estado = {
  usuario: User | null;
  sessao: Session | null;
  perfil: Perfil | null;
  /** O papel dá acesso ao painel do admin. Vem do banco, nunca do cliente. */
  admin: boolean;
  carregando: boolean;
  recarregarPerfil: () => Promise<void>;
  /** Sem credenciais do Supabase: o painel roda com dados de exemplo. */
  demonstracao: boolean;
  entrar: (email: string, senha: string) => Promise<string | null>;
  registrar: (email: string, senha: string, nome: string) => Promise<string | null>;
  sair: () => Promise<void>;
  recuperar: (email: string) => Promise<string | null>;
};

const Contexto = createContext<Estado | null>(null);

/** Usuário fictício do modo demonstração. */
const USUARIO_DEMO = {
  id: 'demo-0000-0000-0000-000000000000',
  email: 'voce@exemplo.com',
  user_metadata: { nome: 'Visitante' },
} as unknown as User;

const PERFIL_DEMO: Perfil = {
  id: USUARIO_DEMO.id,
  nome: 'Visitante',
  avatar_url: null,
  bio: null,
  papel: 'admin',   // na demonstração dá para ver os dois painéis
  xp: 180,
  ofensiva: 3,
  ultima_pratica: new Date().toISOString().slice(0, 10),
};

export function ProvedorAuth({ children }: { children: React.ReactNode }) {
  const [usuario, setUsuario] = useState<User | null>(null);
  const [sessao, setSessao] = useState<Session | null>(null);
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [carregando, setCarregando] = useState(true);

  /**
   * Busca o perfil do banco.
   *
   * O papel vem daqui, nunca do `user_metadata`: aquele o próprio
   * usuário edita, e um admin autodeclarado não seria admin nenhum —
   * mas a interface acreditaria nele.
   */
  const carregarPerfil = useCallback(async (id: string) => {
    const cliente = obterCliente();
    if (!cliente) return;
    const { data } = await cliente
      .from('perfis')
      .select('id, nome, avatar_url, bio, papel, xp, ofensiva, ultima_pratica')
      .eq('id', id)
      .maybeSingle();
    setPerfil((data as Perfil) ?? null);
  }, []);

  const recarregarPerfil = useCallback(async () => {
    if (usuario) await carregarPerfil(usuario.id);
  }, [usuario, carregarPerfil]);

  useEffect(() => {
    const cliente = obterCliente();
    if (!cliente) {
      // Modo demonstração: entra direto, sem pedir nada.
      setUsuario(USUARIO_DEMO);
      setPerfil(PERFIL_DEMO);
      setCarregando(false);
      return;
    }

    cliente.auth.getSession().then(async ({ data }) => {
      setSessao(data.session);
      setUsuario(data.session?.user ?? null);
      if (data.session?.user) await carregarPerfil(data.session.user.id);
      setCarregando(false);
    });

    const { data: assinatura } = cliente.auth.onAuthStateChange(
      (_evento, novaSessao) => {
        setSessao(novaSessao);
        setUsuario(novaSessao?.user ?? null);
        if (novaSessao?.user) carregarPerfil(novaSessao.user.id);
        else setPerfil(null);
      },
    );
    return () => assinatura.subscription.unsubscribe();
  }, [carregarPerfil]);

  /** Devolve a mensagem de erro, ou null quando deu certo. */
  const entrar = useCallback(async (email: string, senha: string) => {
    const cliente = obterCliente();
    if (!cliente) return null;
    const { error } = await cliente.auth.signInWithPassword({ email, password: senha });
    return error ? traduzirErro(error.message) : null;
  }, []);

  const registrar = useCallback(
    async (email: string, senha: string, nome: string) => {
      const cliente = obterCliente();
      if (!cliente) return null;
      const { error } = await cliente.auth.signUp({
        email,
        password: senha,
        options: { data: { nome } },
      });
      return error ? traduzirErro(error.message) : null;
    }, []);

  const sair = useCallback(async () => {
    const cliente = obterCliente();
    if (cliente) await cliente.auth.signOut();
    else setUsuario(null);
    setPerfil(null);
  }, []);

  const recuperar = useCallback(async (email: string) => {
    const cliente = obterCliente();
    if (!cliente) return null;
    const { error } = await cliente.auth.resetPasswordForEmail(email, {
      redirectTo: typeof window !== 'undefined'
        ? `${window.location.origin}/painel/`
        : undefined,
    });
    return error ? traduzirErro(error.message) : null;
  }, []);

  const valor = useMemo(
    () => ({
      usuario, sessao, perfil, carregando,
      admin: perfil?.papel === 'admin' || perfil?.papel === 'moderador',
      recarregarPerfil,
      demonstracao: !configurado,
      entrar, registrar, sair, recuperar,
    }),
    [usuario, sessao, perfil, carregando, recarregarPerfil,
     entrar, registrar, sair, recuperar],
  );

  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}

export function useAuth() {
  const contexto = useContext(Contexto);
  if (!contexto) {
    throw new Error('useAuth precisa estar dentro de <ProvedorAuth>');
  }
  return contexto;
}
