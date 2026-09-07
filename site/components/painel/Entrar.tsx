'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Logo } from '@/components/Logo';
import { useAuth } from '@/lib/supabase/auth';

type Modo = 'entrar' | 'registrar' | 'recuperar';

const TITULOS: Record<Modo, { titulo: string; botao: string }> = {
  entrar: { titulo: 'Entrar no painel', botao: 'Entrar' },
  registrar: { titulo: 'Criar conta', botao: 'Criar conta' },
  recuperar: { titulo: 'Recuperar senha', botao: 'Enviar link' },
};

export function Entrar() {
  const { entrar, registrar, recuperar } = useAuth();
  const [modo, setModo] = useState<Modo>('entrar');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [nome, setNome] = useState('');
  const [erro, setErro] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setAviso(null);
    setEnviando(true);

    let resultado: string | null = null;
    if (modo === 'entrar') resultado = await entrar(email, senha);
    else if (modo === 'registrar') resultado = await registrar(email, senha, nome);
    else resultado = await recuperar(email);

    setEnviando(false);
    if (resultado) {
      setErro(resultado);
      return;
    }
    if (modo === 'registrar') {
      setAviso('Conta criada. Confirme o e-mail para entrar.');
    } else if (modo === 'recuperar') {
      setAviso('Se houver conta com esse e-mail, o link foi enviado.');
    }
  }

  const { titulo, botao } = TITULOS[modo];

  return (
    <div className="flex min-h-screen items-center justify-center px-5 py-12">
      <div className="w-full max-w-[380px]">
        <Link href="/" className="mb-8 flex items-center justify-center gap-2.5">
          <Logo size={30} />
          <span className="text-[19px] font-extrabold tracking-tight">
            DataForge
          </span>
        </Link>

        <div className="surface-card rounded-xl p-6">
          <h1 className="text-[21px] font-bold text-strong">{titulo}</h1>
          <p className="mt-1 text-[13.5px] text-muted">
            {modo === 'recuperar'
              ? 'Enviamos um link para você definir uma senha nova.'
              : 'Guarde projetos, trechos e seu progresso nos exercícios.'}
          </p>

          <form onSubmit={enviar} className="mt-6 space-y-3.5">
            {modo === 'registrar' && (
              <Campo rotulo="Nome" valor={nome} aoMudar={setNome}
                     tipo="text" auto="name" placeholder="Como te chamamos" />
            )}
            <Campo rotulo="E-mail" valor={email} aoMudar={setEmail}
                   tipo="email" auto="email" placeholder="voce@exemplo.com" />
            {modo !== 'recuperar' && (
              <Campo rotulo="Senha" valor={senha} aoMudar={setSenha}
                     tipo="password"
                     auto={modo === 'registrar' ? 'new-password' : 'current-password'}
                     placeholder="ao menos 6 caracteres" />
            )}

            {erro && (
              <p role="alert"
                 className="rounded-lg border border-accent/30 bg-accent/10
                            px-3 py-2 text-[13px] text-accent">
                {erro}
              </p>
            )}
            {aviso && (
              <p role="status"
                 className="rounded-lg border border-line bg-raised px-3 py-2
                            text-[13px] text-body">
                {aviso}
              </p>
            )}

            <button
              type="submit"
              disabled={enviando}
              className="w-full rounded-lg bg-accent px-4 py-2.5 text-[14.5px]
                         font-semibold text-white transition-opacity
                         hover:opacity-90 disabled:opacity-50"
            >
              {enviando ? 'Aguarde…' : botao}
            </button>
          </form>

          <div className="mt-5 space-y-1.5 text-center text-[13px]">
            {modo === 'entrar' && (
              <>
                <p className="text-muted">
                  Não tem conta?{' '}
                  <button onClick={() => setModo('registrar')}
                          className="link-quiet underline">criar uma</button>
                </p>
                <p className="text-muted">
                  <button onClick={() => setModo('recuperar')}
                          className="link-quiet underline">esqueci a senha</button>
                </p>
              </>
            )}
            {modo !== 'entrar' && (
              <p className="text-muted">
                <button onClick={() => setModo('entrar')}
                        className="link-quiet underline">voltar para entrar</button>
              </p>
            )}
          </div>
        </div>

        <p className="mt-6 text-center text-[12.5px] text-muted">
          <Link href="/docs" className="link-quiet">← voltar à documentação</Link>
        </p>
      </div>
    </div>
  );
}

function Campo({ rotulo, valor, aoMudar, tipo, auto, placeholder }: {
  rotulo: string; valor: string; aoMudar: (v: string) => void;
  tipo: string; auto: string; placeholder: string;
}) {
  const id = `campo-${rotulo.toLowerCase()}`;
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-[13px] font-medium text-body">
        {rotulo}
      </label>
      <input
        id={id}
        type={tipo}
        required
        autoComplete={auto}
        value={valor}
        onChange={(e) => aoMudar(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg border border-line bg-raised px-3 py-2.5
                   text-[14px] text-strong outline-none transition-colors
                   placeholder:text-muted/60 focus:border-accent/50"
      />
    </div>
  );
}
