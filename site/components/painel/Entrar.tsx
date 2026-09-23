'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { Logo } from '@/components/Logo';
import { Turnstile, type ControleTurnstile } from '@/components/Turnstile';
import { TURNSTILE_LIGADO } from '@/lib/turnstile';
import { useAuth } from '@/lib/supabase/auth';

/* O Google só aparece quando o provedor está LIGADO no Supabase.
 *
 * Um botão "continuar com Google" que responde 'provider is not
 * enabled' é pior que não ter botão: quem clica conclui que o site
 * está quebrado, e não que falta configuração do outro lado. */
const GOOGLE_LIGADO = process.env.NEXT_PUBLIC_OAUTH_GOOGLE === '1';

type Modo = 'entrar' | 'registrar' | 'recuperar';

const TITULOS: Record<Modo, { titulo: string; botao: string }> = {
  entrar: { titulo: 'Entrar no painel', botao: 'Entrar' },
  registrar: { titulo: 'Criar conta', botao: 'Criar conta' },
  recuperar: { titulo: 'Recuperar senha', botao: 'Enviar link' },
};

export function Entrar() {
  const { entrar, registrar, recuperar, entrarComGoogle } = useAuth();
  // '/painel?criar=1' abre direto em "Criar conta". O cabeçalho
  // oferece as duas portas, e levar as duas para o mesmo formulário
  // em modo "entrar" faria a segunda mentir sobre o que faz.
  //
  // Lido de `window` e não de `useSearchParams`: o site é exportado
  // estático, e `useSearchParams` obriga a envolver a página num
  // `<Suspense>` — cerimônia para ler um parâmetro opcional.
  const [modo, setModo] = useState<Modo>(() => {
    if (typeof window === 'undefined') return 'entrar';
    return new URLSearchParams(window.location.search).has('criar')
      ? 'registrar'
      : 'entrar';
  });
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [nome, setNome] = useState('');
  const [erro, setErro] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [captcha, setCaptcha] = useState<string | null>(null);
  const [captchaFalhou, setCaptchaFalhou] = useState(false);
  const widget = useRef<ControleTurnstile>(null);

  // O widget pode RENDERIZAR e nunca terminar: domínio ainda não
  // liberado na chave, desafio interativo que não resolve, extensão
  // de navegador atrapalhando. Nesses casos o `error-callback` não
  // dispara — não há erro, há espera —, e sem um prazo o rótulo do
  // botão fica em "Conclua a verificação" para sempre.
  //
  // Doze segundos: o desafio invisível resolve em menos de dois, e o
  // interativo em poucos segundos depois do clique. Passar disso não
  // é lentidão, é uma espera que não vai terminar.
  useEffect(() => {
    if (!TURNSTILE_LIGADO || captcha || captchaFalhou) return;
    const prazo = setTimeout(() => {
      setCaptchaFalhou(true);
    }, 12000);
    return () => clearTimeout(prazo);
  }, [captcha, captchaFalhou, modo]);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setAviso(null);
    setEnviando(true);

    let resultado: string | null = null;
    if (modo === 'entrar') resultado = await entrar(email, senha, captcha);
    else if (modo === 'registrar') resultado = await registrar(email, senha, nome, captcha);
    else resultado = await recuperar(email, captcha);

    // O token é de USO ÚNICO: valeu a tentativa, deu certo ou não.
    // Sem reiniciar aqui, o segundo envio — com a senha certa, depois
    // de um erro de digitação — falharia por 'timeout-or-duplicate',
    // e a pessoa veria uma mensagem sobre captcha onde acabou de
    // corrigir a senha.
    widget.current?.reiniciar();
    setCaptcha(null);
    setCaptchaFalhou(false);

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
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-5 py-14">
      {/* O brilho de fundo, do mesmo vermelho da marca. Ele fica atrás
          de tudo e não intercepta clique — 'pointer-events: none'. */}
      <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute left-1/2 top-[-18%] h-[420px] w-[620px] -translate-x-1/2 rounded-full bg-accent/20 blur-[130px]" />
        <div className="absolute bottom-[-20%] right-[-10%] h-[360px] w-[460px] rounded-full bg-accent/10 blur-[120px]" />
      </div>

      <div className="w-full max-w-[400px]">
        <div className="rounded-[28px] border border-line/70 bg-gradient-to-b from-white/[0.07] to-transparent p-[1px] shadow-2xl">
          <div className="rounded-[27px] bg-surface/80 px-7 py-9 backdrop-blur-xl">
            <Link href="/" className="mx-auto mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-white/10 shadow-lg">
              <Logo size={26} />
            </Link>

            <h1 className="text-center text-[22px] font-semibold text-strong">{titulo}</h1>
            <p className="mx-auto mt-2 max-w-[30ch] text-center text-[13px] leading-[20px] text-muted">
              {modo === 'recuperar'
                ? 'Enviamos um link para você definir uma senha nova.'
                : 'Guarde projetos, trechos e seu progresso nos exercícios.'}
            </p>

            <form onSubmit={enviar} className="mt-7 space-y-3">
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
                   className="rounded-2xl border border-accent/30 bg-accent/10
                              px-4 py-2.5 text-[13px] text-accent">
                  {erro}
                </p>
              )}
              {aviso && (
                <p role="status"
                   className="rounded-2xl border border-line bg-raised px-4 py-2.5
                              text-[13px] text-body">
                  {aviso}
                </p>
              )}

              {/* A verificação fica ACIMA do botão: descobri-la depois de
                  clicar em "Entrar" e ver o botão desabilitado é a forma
                  mais rápida de alguém achar que o site quebrou. */}
              <Turnstile
                acao={modo}
                controle={widget}
                aoMudarToken={setCaptcha}
                aoFalhar={(motivo) => {
                  // FALHA ABERTA, aqui. Se o script não carrega — rede
                  // corporativa que bloqueia a Cloudflare, domínio ainda
                  // não liberado na chave, extensão de navegador — o
                  // botão NÃO pode morrer: quem recusa de verdade é o
                  // servidor do Supabase, e um painel que não abre por
                  // causa disso é uma porta trancada por acidente, sem
                  // ninguém do outro lado para explicar.
                  setCaptchaFalhou(true);
                  setAviso(`${motivo}. Você pode tentar entrar mesmo assim.`);
                }}
              />

              {/* O BOTÃO NÃO MORRE POR CAUSA DO CAPTCHA — só por já
                  estar enviando. Quem recusa de verdade é o servidor do
                  Supabase, e um envio recusado com motivo é sempre
                  melhor que um botão que não responde. */}
              <button
                type="submit"
                disabled={enviando}
                className="w-full rounded-full bg-accent px-5 py-3 text-[14.5px]
                           font-semibold text-white shadow-[0_10px_30px_-12px_rgb(var(--accent))]
                           transition-all hover:bg-accent-soft disabled:opacity-50"
              >
                {enviando
                  ? 'Aguarde…'
                  : TURNSTILE_LIGADO && !captcha && !captchaFalhou
                    ? `${botao} (verificando…)`
                    : botao}
              </button>
            </form>

            {GOOGLE_LIGADO && modo !== 'recuperar' && (
              <>
                <div className="my-5 flex items-center gap-3">
                  <span className="h-px flex-1 bg-line" />
                  <span className="text-[11px] uppercase tracking-wider text-muted">ou</span>
                  <span className="h-px flex-1 bg-line" />
                </div>
                <button
                  type="button"
                  onClick={async () => {
                    setErro(null);
                    const falha = await entrarComGoogle();
                    if (falha) setErro(falha);
                  }}
                  className="flex w-full items-center justify-center gap-2.5 rounded-full
                             border border-line bg-raised px-5 py-3 text-[14px] font-medium
                             text-strong transition-colors hover:border-line hover:bg-surface"
                >
                  <svg aria-hidden viewBox="0 0 24 24" className="h-[18px] w-[18px]">
                    <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5a5.6 5.6 0 0 1-2.4 3.7v3h3.9c2.3-2.1 3.5-5.2 3.5-8.9z" />
                    <path fill="#34A853" d="M12 24c3.2 0 5.9-1.1 7.9-2.9l-3.9-3c-1.1.7-2.4 1.1-4 1.1-3.1 0-5.7-2.1-6.6-4.9H1.4v3.1A12 12 0 0 0 12 24z" />
                    <path fill="#FBBC05" d="M5.4 14.3a7.2 7.2 0 0 1 0-4.6V6.6H1.4a12 12 0 0 0 0 10.8l4-3.1z" />
                    <path fill="#EA4335" d="M12 4.8c1.8 0 3.3.6 4.6 1.8l3.4-3.4A12 12 0 0 0 1.4 6.6l4 3.1C6.3 6.9 8.9 4.8 12 4.8z" />
                  </svg>
                  Continuar com Google
                </button>
              </>
            )}

            <div className="mt-6 space-y-1.5 text-center text-[13px]">
              {modo === 'entrar' && (
                <>
                  <p className="text-muted">
                    Não tem conta?{' '}
                    <button onClick={() => setModo('registrar')}
                            className="link-quiet underline">criar uma, é de graça</button>
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
        </div>

        {/* O que o painel guarda — o lugar onde um produto põe rostos de
            clientes. Aqui são as quatro coisas que a conta faz, porque
            inventar depoimento seria mentira. */}
        <ul className="mx-auto mt-8 grid max-w-[340px] grid-cols-2 gap-2 text-center text-[12px] text-muted">
          {['Progresso nos 399 exercícios', 'Trechos salvos', 'Projetos do laboratório', 'Tokens da API'].map((t) => (
            <li key={t} className="rounded-xl border border-line/70 bg-surface/50 px-3 py-2">{t}</li>
          ))}
        </ul>

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
      <label htmlFor={id} className="mb-1.5 block text-[12.5px] font-medium text-muted">
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
        className="w-full rounded-2xl border border-line bg-raised/70 px-4 py-3
                   text-[14px] text-strong outline-none transition-colors
                   placeholder:text-muted/60 focus:border-accent/50
                   focus:ring-2 focus:ring-accent/25"
      />
    </div>
  );
}
