'use client';

import {
  createContext, useCallback, useContext, useEffect, useMemo, useState,
} from 'react';
import type { Session, User } from '@supabase/supabase-js';
import { configurado, obterCliente, traduzirErro } from './cliente';

type Estado = {
  usuario: User | null;
  sessao: Session | null;
  carregando: boolean;
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

export function ProvedorAuth({ children }: { children: React.ReactNode }) {
  const [usuario, setUsuario] = useState<User | null>(null);
  const [sessao, setSessao] = useState<Session | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    const cliente = obterCliente();
    if (!cliente) {
      // Modo demonstração: entra direto, sem pedir nada.
      setUsuario(USUARIO_DEMO);
      setCarregando(false);
      return;
    }

    cliente.auth.getSession().then(({ data }) => {
      setSessao(data.session);
      setUsuario(data.session?.user ?? null);
      setCarregando(false);
    });

    const { data: assinatura } = cliente.auth.onAuthStateChange(
      (_evento, novaSessao) => {
        setSessao(novaSessao);
        setUsuario(novaSessao?.user ?? null);
      },
    );
    return () => assinatura.subscription.unsubscribe();
  }, []);

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
      usuario, sessao, carregando,
      demonstracao: !configurado,
      entrar, registrar, sair, recuperar,
    }),
    [usuario, sessao, carregando, entrar, registrar, sair, recuperar],
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
